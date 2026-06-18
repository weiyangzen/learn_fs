# sources/distributed-fs/ceph/src/osd/OSDMap.cc

## Purpose

`OSDMap.cc` implements Ceph's in-memory and wire-format description of the OSD cluster. It is the authoritative code for applying OSD map epochs, encoding and decoding full and incremental maps, deriving object-to-PG and PG-to-OSD placement, maintaining temporary and explicit remaps, reporting OSD/pool topology, computing balancing suggestions, and generating map-derived health checks.

The file backs the declarations in `OSDMap.h` and is central to monitor, OSD, client, and tooling behavior. Monitors create and persist new maps and incrementals; OSDs and clients decode maps to route IO; balancer and admin commands use its upmap/read-balance helpers; health monitoring uses its topology and flag inspection.

## Important APIs, Types, And Functions

- `osd_info_t`: persisted per-OSD epoch history: `up_from`, `up_thru`, `down_at`, `lost_at`, and last clean interval. It supports formatter dumps, versioned encode/decode, test instance generation, and stream printing.
- `osd_xinfo_t`: persisted per-OSD extended metadata: down timestamp, laggy probability/interval, feature mask, prior auto-out weight, scrub timestamp for purged snaps, and `dead_epoch`. Encoding is feature-gated for older releases.
- `OSDMap::Incremental`: a diff from `epoch - 1` to `epoch`. Its fields carry new pools, removed pools, CRUSH map blobs, OSD state XORs, address updates, weights, temp mappings, upmaps, blocklists, compatibility requirements, stretch mode changes, and Crimson enablement mutation. Helpers include `get_net_marked_out`, `get_net_marked_down`, `identify_osd`, `propagate_base_properties_to_tiers`, `encode*`, `decode*`, and `dump`.
- `OSDMap`: full map state and behavior. Major methods include `apply_incremental`, `encode*`, `decode*`, `post_decode`, `map_to_pg`, `object_locator_to_pg`, `pg_to_raw_osds`, `pg_to_raw_up`, `pg_to_raw_upmap`, `_pg_to_up_acting_osds`, `check_pg_upmaps`, `clean_pg_upmaps`, `calc_pg_upmaps`, `balance_primaries`, `calc_read_balance_score`, `dump`, `print`, `print_tree`, `check_health`, and `build_simple*`.
- `range_bits`: internal helper used by range blocklist matching for IPv4/IPv6 prefix-style addresses encoded through `entity_addr_t::nonce`.
- Local dumper classes: `OSDTreePlainDumper`, `OSDTreeFormattingDumper`, `OSDUtilizationDumper`, `OSDUtilizationPlainDumper`, and `OSDUtilizationFormatDumper` adapt CRUSH tree traversal and `PGMap` stats into CLI/formatter output.

## Control Flow

### Incremental Application

`apply_incremental` is the core epoch transition path. It validates FSID, asserts the next epoch, increments `epoch`, updates `modified`, and either decodes a full replacement map from `inc.fullmap` or applies field-level changes. The field-level path updates global flags, max OSD count, pool definitions/names/removals, removed/purged snap queues, last up/in timestamps, weights, primary affinity, erasure-code profiles, OSD state, addresses, `osd_info`, `osd_xinfo`, UUIDs, `pg_temp`, `primary_temp`, `pg_upmap`, `pg_upmap_items`, `pg_upmap_primaries`, blocklists, CRUSH node/device-class flags, cluster snapshot text, fullness ratios, compatibility release requirements, CRUSH map, stretch mode, and `allow_crimson`.

OSD state updates are XOR-style for `Incremental::new_state`. A zero delta is treated as `CEPH_OSD_UP`, matching legacy semantics. Destroying an existing OSD clears UUID, info, xinfo, primary affinity, and all address channels. Bringing an OSD up sets `EXISTS|UP`, clears `STOP`, writes client/heartbeat addresses, and records `up_from`.

The function recalculates `num_osd`, `num_up_osd`, `num_in_osd`, and cached common up-OSD feature bits at the end.

### Placement Mapping

Object placement starts at `map_to_pg` or `object_locator_to_pg`, which hashes object name/key/namespace through the target `pg_pool_t` to produce `pg_t`.

PG placement then follows this chain:

1. `_pg_to_raw_osds` maps the pool's placement seed through the pool CRUSH rule via `CrushWrapper::do_rule`, using `osd_weight`.
2. `_remove_nonexistent_osds` either shifts missing OSDs out for pools that can shift or replaces them with `CRUSH_ITEM_NONE`.
3. `_apply_upmap` applies explicit `pg_upmap`, pair-wise `pg_upmap_items`, and `pg_upmap_primaries`, with guards against out/invalid targets.
4. `_raw_to_up_osds` removes or masks down/nonexistent OSDs to derive the `up` set.
5. `_apply_primary_affinity` may select a non-first primary according to per-OSD primary affinity and the PG seed.
6. `_get_temp_osds` overlays `pg_temp` and `primary_temp` for acting-set overrides.
7. `_pg_to_up_acting_osds` combines raw/up calculation with temp mappings to return `up`, `up_primary`, `acting`, and `acting_primary`.

Optimized erasure-coded pools have special `pgtemp_primaryfirst` and `pgtemp_undo_primaryfirst` transformations so temporary acting vectors can keep a legal primary shard first without changing client-visible OSDMap primary selection semantics.

### Upmap Cleaning And Balancing

`get_upmap_pgs`, `check_pg_upmaps`, and `clean_pg_upmaps` validate explicit remaps after pool, CRUSH, or OSD changes. Invalid PGs, merge-source PGs, mappings outside the current CRUSH rule, out targets, redundant mappings, wrong-size mappings, and invalid/redundant primary remaps are canceled or simplified in a pending incremental.

`calc_pg_upmaps` builds PG-by-OSD and OSD-weight data, computes deviations from target PG counts, searches for remaps from overfull to underfull OSDs, tests each candidate for lower deviation, and packs accepted changes into `pending_inc->new_pg_upmap_items` or `old_pg_upmap_items`. Aggressive mode randomizes candidate order and retries local fallbacks.

`balance_primaries`, `calc_desired_primary_distribution*`, `calc_read_balance_score`, and related helpers optimize/read-score primary placement using `pg_upmap_primaries`. They support a simple fair policy and a size-aware policy based on pool read ratio. These paths operate only on replicated pools and reject or warn on invalid primary-affinity/read-ratio conditions.

## State And Persistence Behavior

Persistent full-map state includes FSID, epoch timestamps, pools and names, flags, max OSD, OSD state and weight vectors, all address channels, `pg_temp`, `primary_temp`, primary affinity, CRUSH map, erasure-code profiles, upmap structures, CRUSH version, removed/purged snap queues, OSD info/xinfo/UUID vectors, blocklists and range blocklists, cluster snapshot, fullness ratios, compatibility release gates, CRUSH node/device-class flags, stretch-mode fields, and `allow_crimson`.

Encoding is heavily compatibility-gated:

- `encode_client_old` and `encode_classic` support pre-`CEPH_FEATURE_OSDMAP_ENC` consumers and older PGID/address formats.
- Modern `encode` uses a wrapper with separate client-usable and OSD-only sections, selected per feature/release. It asserts `CEPH_FEATURE_RESERVED` to prevent arbitrary callers from creating canonical map encodings.
- Incremental encoding follows the same split and records both `inc_crc` and `full_crc`.
- Decode paths detect old wrapper versions and rewind to classic decoders. Modern decoders set defaults for fields absent in older versions.
- Full maps and incrementals include CRC validation for newer wrapper versions. Bad CRC throws `ceph::buffer::malformed_input`.
- `get_encoding_features` limits significant feature bits according to `require_osd_release`, and comments require new encoding dependencies to update `SIGNIFICANT_FEATURES`.

`post_decode` rebuilds reverse pool-name lookup, recomputes OSD counts, and refreshes cached common up-OSD features. `dedup` reuses shared address, CRUSH, temp-map, and UUID storage between adjacent map instances when equal, reducing memory churn in map history.

## Dependencies And Integration Points

- `CrushWrapper` and `CrushTreeDumper`: CRUSH rule execution, topology inspection, rule validation, tree output, weight maps, device classes, and simple CRUSH map construction.
- `pg_pool_t`, `pg_t`, `object_locator_t`, `object_t`, `osd_stat_t`, and pool options from Ceph OSD type headers.
- `entity_addr_t` and `entity_addrvec_t`: public, cluster, and heartbeat address persistence plus blocklist/range-blocklist matching.
- `ceph::buffer::list` and Ceph encode/decode macros: canonical wire/persistence format and CRC coverage.
- `CephContext` and config: logging, default pool/CRUSH construction, balancer toggles, fullness failsafe ratios, public network checks, health warning policy, read-ratio defaults.
- `Formatter` and `TextTable`: JSON/plain output for admin commands.
- `PGMap`: OSD utilization output and `print_osd_utilization`.
- `health_check_map_t`: monitor health checks from `check_health`.
- Monitor integrations are visible through `OSDMonitor` friendship and mon command references for `pg_upmap`/`pg_upmap_items`; MDS monitor health can request OSDMap writes for blocklisting.

## Risks And Edge Cases

- Encoding compatibility is fragile. Adding fields without correct section versioning, feature masking, defaults, and `SIGNIFICANT_FEATURES` updates can make monitors, OSDs, or clients diverge.
- `Incremental::new_state` is XOR-based and has legacy zero-as-UP handling. Incorrect pending state composition can accidentally toggle flags instead of setting/clearing them.
- `apply_incremental` assumes valid indexes after `new_max_osd`; malformed incrementals can hit assertions or vector bounds assumptions.
- Upmap and primary-upmap behavior depends on CRUSH topology, OSD weights, and pool size. Stale entries can route to invalid/out OSDs unless `clean_pg_upmaps` runs after topology changes.
- `_apply_upmap` intentionally cannot express bidirectional swaps through `pg_upmap_items`; callers must not assume pair order supports all permutations.
- Primary-affinity and read-balance calculations have known warning/error cases: all-zero affinity, PGs mapped only to zero-affinity OSDs, non-replicated pools, invalid read ratios, incomplete PG legs, and non-power-of-two PG counts for size-aware assumptions.
- Range blocklist prefix matching relies on the address nonce field as a prefix length; mistakes in address normalization or release-dependent address type handling can over-block or under-block clients/OSDs.
- Health checks perform recursive CRUSH subtree analysis and cache down/up subtrees. Incorrect CRUSH parent/type metadata could produce misleading subtree-down health checks.
- Fullness ratio health handling mirrors OSD-side failsafe adjustment. Changing ratio semantics in OSD services should be reflected here to avoid inconsistent health results.
- `dedup` shares immutable-equivalent structures between maps. Future mutations to shared objects outside copy-on-write expectations would corrupt historical map views.

## Test Signals

The local checkout does not include the broad `src/test` or `qa` trees, but this file exposes several built-in and nearby test signals:

- `osd_info_t::generate_test_instances`, `osd_xinfo_t::generate_test_instances`, `OSDMap::Incremental::generate_test_instances`, and `OSDMap::generate_test_instances` support Ceph encode/decode corpus tests.
- Serialization tests should round-trip classic and modern full maps/incrementals across feature masks, verify CRC failure handling, and verify defaulting for absent older-version fields.
- Incremental tests should apply pool creation/removal, OSD up/down/destroy, address updates, weight changes, blocklist/range-blocklist additions/removals, CRUSH changes, stretch-mode mutations, and Crimson mutation.
- Placement tests should compare raw/up/acting outputs for replicated and erasure pools, down/nonexistent OSDs, primary affinity, `pg_temp`, `primary_temp`, `pg_upmap`, `pg_upmap_items`, and `pg_upmap_primaries`.
- Upmap cleaning tests should cover missing pools, pending merges, CRUSH topology movement, out targets, redundant explicit maps, wrong-size maps, simplified pair lists, and primary-only cancellations.
- Balancer tests should validate deterministic seeded behavior in `calc_pg_upmaps`, monotonic deviation reduction, pending incremental packing, aggressive retry behavior, and preservation of admin-specified `pg_upmap`.
- Read-balance tests should cover fair and size-aware policies, warning/error text, all-zero primary affinity, invalid read ratios, non-replicated pools, and pool-size changes that remove primary remaps.
- Health tests should assert `OSD_DOWN`, subtree-down checks, `OSD_ORPHAN`, fullness ordering and OSD/pool fullness checks, map and OSD flag checks, legacy CRUSH tunable warnings, missing cache hit sets, sortbitwise warning, upgrade-finished warning, stretch-mode warnings, and public-network reachability checks.
