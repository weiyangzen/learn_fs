# sources/distributed-fs/ceph/src/mon/OSDMonitor.cc lines 1-8317

## Chunk Scope

This chunk covers the first half of Ceph's OSD monitor implementation: includes and local helpers, OSD map cache management, initial OSDMap creation, Paxos load/encode paths, full-map pruning, message preprocessing and prepare handlers for OSD lifecycle and PG messages, map serving, subscription fanout, periodic timeout/quota/prune work, read-only command handling, purged snap indexes, and the start of pool and CRUSH-rule creation validation. The source file continues past line 8317; pool creation is in progress at the chunk boundary and command mutation handling continues in later chunks.

## Purpose

`OSDMonitor.cc` implements the monitor-side authority for OSDMap state. In this chunk it receives OSD/client/command messages, decides whether each message can be answered from the current committed map or must become a Paxos proposal, stages changes in `pending_inc`, persists committed OSDMap epochs and auxiliary indexes, and keeps runtime monitor state such as OSD failure reports, creating-PG notifications, last-clean trim bounds, and map caches synchronized with committed Paxos state.

The dominant design is a two-phase monitor-service flow:

- `preprocess_*` methods validate capabilities, source identity, stale epochs, and idempotence. They return `true` when the request was answered or ignored without a proposal.
- `prepare_*` methods mutate only pending state, mainly `pending_inc`, `pending_metadata`, `pending_created_pgs`, and failure/timeout side state. Those mutations become durable only when `encode_pending()` writes them into the monitor store transaction.

## Local Helpers and Types

- `OSD_PG_CREATING_PREFIX`, `OSD_METADATA_PREFIX`, and `OSD_SNAP_PREFIX` define monitor-store namespaces for creating-PG state, per-OSD metadata, and snap purge/remove metadata.
- `OSDMemCache`, `IncCache`, and `FullCache` adapt `inc_osd_cache` and `full_osd_cache` to `PriorityCache::PriCache`, allowing the monitor priority cache manager to account for incremental and full OSDMap memory separately.
- `is_osd_writable()` and `is_unmanaged_snap_op_permitted()` translate monitor and OSD caps into a permission decision for unmanaged snapshot operations. The latter falls back from mon caps to decoded OSD caps stored in the auth monitor's key server.
- `LastEpochClean` collects `min_last_epoch_clean` reports per pool/PG and computes a lower bound used for safe OSDMap trimming.
- `C_UpdateCreatingPGs` is an async mapping completion callback. When an OSDMap mapping job completes it refreshes `creating_pgs_by_osd_epoch` and notifies subscribers.
- `C_AckMarkedDown` and other callback classes used in this chunk bridge Paxos proposal completion to protocol replies or retry dispatch.
- `osd_pool_get_choices` and the helper `subtract_second_from_first()` drive the large `osd pool get` read command branch.

## Initialization and Cache Tuning

`OSDMonitor::OSDMonitor()` initializes the Paxos service, OSDMap caches, prune manifest state, and mapping worker, then registers itself as a config observer. It tries `_set_cache_sizes()` so the OSDMap LRU caches can participate in monitor memory autotuning.

`get_tracked_keys()` and `handle_conf_change()` react to `mon_memory_target`, `mon_memory_autotune`, and `rocksdb_cache_size`. The cache-control path is:

- `_set_cache_sizes()` seeds local cache sizes and memory baseline values when autotuning is enabled.
- `_set_cache_autotuning()` creates or drops the `PriorityCache::Manager`.
- `register_cache_with_pcm()` obtains the RocksDB binned KV cache from `MonitorDBStore`, computes min/max/target memory, inserts `kv`, `inc`, and `full` cache participants, and sets ratios.
- `_update_mon_cache_settings()`, `_set_cache_ratios()`, `_set_new_cache_sizes()`, and the cache section of `tick()` keep the cache manager and LRU caches aligned with current config and tcmalloc measurements.

Important risk: `_set_cache_ratios()` assumes `rocksdb_binned_kv_cache` has already been populated; callers generally establish that through `register_cache_with_pcm()` or store access checks. Changes in this area should preserve the null checks in `_update_mon_cache_settings()` and `register_cache_with_pcm()`.

## OSDMap Creation, Loading, and Encoding

`create_initial()` builds epoch 1. It loads a mkfs-provided OSDMap from `mkfs/osdmap` if present, otherwise builds an empty simple map, sets cluster fsid, full/backfill/nearfull ratios, default OSDMap flags, required OSD release and minimum client release, then encodes the full map into `pending_inc.fullmap` with CRC.

`update_from_paxos()` is the main committed-state refresh path. It reloads the osdmap prune manifest, compares `get_last_committed()` with `osdmap.epoch`, optionally recovers the `full_latest` pointer, reloads a newer full map if available, loads the persisted `OSD_PG_CREATING_PREFIX/creating` object, and then walks each incremental epoch forward. For each incremental it:

- Loads the encoded incremental through `get_version()`.
- Lazily registers cache manager participation if needed.
- Applies the incremental to in-memory `osdmap`.
- Writes a canonical full map for the epoch unless the primary already supplied one.
- Maintains `full_latest`, removes old mkfs map material after epoch 1, batches store writes by `mon_sync_max_payload_size`, and clears per-OSD report caches when an OSD is newly up.

After applying all epochs it refreshes `down_pending_out`, map subscriptions, PG-create subscriptions, logger counters, failure report waiters, messenger feature requirements, mapping jobs, and stretch-mode monitor state.

`create_pending()` resets `pending_inc` to `osdmap.epoch + 1`, sets fsid, clears pending metadata changes, and repairs invalid full/backfill/nearfull ratios by staging defaults.

`encode_pending()` is the critical persistence boundary. It may first call `do_prune()`, stamps `pending_inc.modified`, propagates tier base properties, optionally primes `pg_temp`, normalizes pending OSD state, updates last-up/last-in timestamps, applies the pending increment to a temporary map, cleans temps and upmaps, updates and persists creating-PG state, maintains per-pool full/backfillfull/nearfull flags, performs release-transition migrations, encodes the full map and incremental, writes Paxos version keys, writes per-OSD metadata changes, writes purged snap indexes, and stores the next health map.

Release-transition side effects inside `encode_pending()` are important:

- First Nautilus epoch adds CREATING flags for still-creating pools and normalizes blocklist address types.
- First Octopus epoch rewrites obsolete cache modes, clears legacy `removed_snaps`, creates a combined pre-Octopus purged-snap epoch object, and erases legacy removed-snap keys.
- First Umbrella epoch fills EC shard counts where possible, enables split-read flags on eligible pools, and auto-enables OMAP on replicated pools.

## Map Storage, Pruning, and Retrieval

The chunk uses both PaxosService's standard map keys and OSDMonitor-specific full-map pruning state.

Store namespaces and keys visible here:

- Service namespace `service_name`: Paxos incrementals, full maps, `full_latest`, and `osdmap_manifest`.
- `OSD_PG_CREATING_PREFIX`: key `creating`.
- `OSD_METADATA_PREFIX`: key per OSD id.
- `OSD_SNAP_PREFIX`: keys `purged_epoch_%08lx`, `purged_snap_<pool>_<last_snap>`, plus legacy `removed_*` keys erased during Octopus transition.

`get_trim_to()` will not trim when quorum is absent, PGs are still creating, or debug trim blocking is enabled. It derives a floor from `LastEpochClean` and `osd_epochs`, honors `mon_osd_force_trim_to`, and preserves at least `mon_min_osdmap_epochs`.

`encode_trim_extra()` writes the oldest retained full map into the trim transaction and, if pruning is active, updates `osdmap_manifest` so pinned full maps remain reconstructable.

Full OSDMap pruning is managed by:

- `load_osdmap_manifest()`
- `should_prune()`
- `_prune_update_trimmed()`
- `prune_init()`
- `_prune_sanitize_options()`
- `is_prune_enabled()`
- `is_prune_supported()`
- `do_prune()`

The pruning model pins sparse full maps at `mon_osdmap_full_prune_interval` boundaries, erases intermediate full maps up to `mon_osdmap_full_prune_txsize`, and leaves incrementals available for reconstruction. `get_full_from_pinned_map()` reconstructs a missing full map by finding the closest lower pinned map, optionally starting from a cached full map, applying each incremental through the requested version, and encoding the result. `get_version_full()` falls back to this reconstruction on `-ENOENT`.

`get_version()`, `get_version_full()`, `reencode_incremental_map()`, and `reencode_full_map()` enforce peer-feature-compatible encodings and cache results by epoch plus significant feature bits.

Risks in this area:

- Prune correctness relies on pinned maps and incrementals forming a contiguous reconstructable chain.
- `get_full_from_pinned_map()` contains optional CRC paranoia under `mon_debug_extra_checks`; tests that alter incremental encoding should exercise this path.
- `encode_pending()` asserts encoded full-map features are a subset of quorum connection features, so feature-gating changes must account for mixed-version monitor quorum behavior.

## Message Dispatch Flow

`preprocess_query()` switches on message type for reads and damp updates. It handles monitor commands, map fetches, OSD self-state messages, failure reports, boot/alive/full/beacon messages, PG create/temp/merge messages, pool ops, remove-snaps, and purged-snap requests.

`prepare_update()` mirrors the mutating messages and dispatches to `prepare_*` handlers. Command and pool-op paths are delegated to functions later in this file; this chunk includes only the beginning of command mutation and pool creation logic.

`should_propose()` forces immediate proposal when `pending_inc.fullmap` exists, and can stage OSD weight adjustments from the `osd_weight` vector before deferring to `PaxosService::should_propose()`.

## OSD Failure, Down, Dead, Boot, Full, Alive, and Beacon Handling

`check_source()` validates monitor session caps and fsid for failure-style OSD messages.

Failure report flow:

- `preprocess_failure()` rejects unauthorized, stale, wrong-source, wrong-address, down, duplicate, or disallowed reports. Valid new reports proceed to prepare.
- `prepare_failure()` stores or cancels a reporter in `failure_info`. Immediate reports call `force_failure()`. Normal reports call `check_failure()`.
- `check_failure()` requires reports from enough distinct CRUSH subtrees, waits out adjusted heartbeat grace from `get_grace_time()`, and stages `pending_inc.new_state[target_osd] = CEPH_OSD_UP`, which is the incremental bit used to mark the OSD down.
- `check_failures()`, `is_failure_stale()`, `process_failures()`, and `take_all_failures()` maintain pending report state and notify original reporters once the map has moved.

Self-marking flow:

- `preprocess_mark_me_down()` validates an up OSD requesting to mark itself down and optionally schedules an ACK.
- `prepare_mark_me_down()` stages the down bit and, if requested, waits for proposal completion before replying with `MOSDMarkMeDown`.
- `preprocess_mark_me_dead()` only accepts an existing down OSD.
- `prepare_mark_me_dead()` writes `dead_epoch` into pending xinfo and then no-replies on commit.

Boot flow:

- `preprocess_boot()` verifies session caps, fsid, nonblank address, OSD feature lower bound, release-span restrictions, crimson eligibility, stretch-mode capability, duplicate boot idempotence, OSD fsid consistency, old up_from races, and `noup`.
- `prepare_boot()` stages new public/cluster/heartbeat addresses, UUID, optional weight, fresh OSD `lost_at`, metadata, last-clean interval, laggy xinfo decay/update, features, and optional auto-in weight. If the OSD is already up at a different address, it first stages a down transition and retries after proposal.
- `_booted()` logs and sends maps starting after the OSD's current epoch.

Other OSD status handlers:

- `preprocess_full()` and `prepare_full()` manage nearfull/backfillfull/full state bits.
- `preprocess_alive()`, `prepare_alive()`, and `update_up_thru()` update `up_thru` when an OSD has consumed map epochs.
- `preprocess_beacon()` always forwards valid beacons to the leader. `prepare_beacon()` records beacon report time, OSD epoch, per-PG `min_last_epoch_clean`, and newer `last_purged_snaps_scrub` into xinfo if needed.
- `handle_osd_timeouts()` marks up OSDs down when no beacon arrives after `max(mon_osd_report_timeout, 2 * osd_beacon_report_interval)`, but only after the monitor has been leader long enough.

Safety gates are centralized in `can_mark_down()`, `can_mark_up()`, `can_mark_out()`, and `can_mark_in()`, which honor OSDMap flags such as `nodown`, `noup`, `noout`, `noin` and ratio constraints such as `mon_osd_min_up_ratio` and `mon_osd_min_in_ratio`.

## PG Creation, PG Temp, and PG Merge Control

Creating-PG state is maintained separately from the OSDMap so OSDs can be told which PGs to instantiate.

- `scan_for_creating_pgs()` queues pools whose PGs need creation unless already created, removed, or invalid by CRUSH rule.
- `update_pending_pgs()` clones current creating state, scans old/new pools, removes deleted/created PGs, filters nonexistent PGs, drains queued ranges into `creating_pgs.pgs`, and for Octopus+ computes PG history/past intervals by comparing old and next acting sets.
- `start_mapping()` launches an async OSDMap mapping job, and `update_creating_pgs()` maps each creating PG to an acting primary and epoch for `MOSDPGCreate2`.
- `send_pg_creates()` sends pending creates to subscribed, up OSDs and advances the subscription cursor.

`maybe_prime_pg_temp()` and `prime_pg_temp()` pre-populate `pending_inc.new_pg_temp` when an upcoming map change could make acting sets worse. It can map all PGs after major changes, or target PGs touching interesting OSDs when the estimate stays under `mon_osd_prime_pg_temp_max_estimate`. It avoids creating PGs and only preserves old acting sets when they are safer than the next acting set.

`preprocess_pgtemp()` validates caps and active source, discards entries from non-primary senders or removed pools, handles forced updates, and only proposes when there is an actual change or removal. `prepare_pgtemp()` writes `new_pg_temp`, clears primary-temp entries, reorders for EC optimization primary behavior through `pgtemp_primaryfirst()`, updates `up_thru`, and replies after proposal.

PG merge handling:

- `preprocess_pg_ready_to_merge()` validates caps, pool existence, and that the reported PG is exactly the last PG expected by the pending shrink.
- `prepare_pg_ready_to_merge()` either decrements `pg_num` with source/target version metadata, backs off by resetting `pg_num_pending`, or blocks crimson merges unless `crimson_allow_pg_merge` is set. It always forces pre-Nautilus clients to resend ops.
- `preprocess_pg_stop_merge()` validates caps and pool existence.
- `prepare_pg_stop_merge()` handles crimson OSDs reporting unsupported merge conditions, cancels shrink targets, clears `FLAG_CRIMSON_ALLOW_PG_MERGE`, clears merge metadata, and replies after proposal.

## Snapshot Removal and Purged Snap Tracking

`preprocess_remove_snaps()` checks `osd pool rmsnap` capability, validates snaps are already removed or not above snap sequence, and for Octopus-capable clients sends an echo reply. `prepare_remove_snaps()` updates pending pool removed snap state, sets self-managed snaps, bumps snap sequence and snap epoch, and stages `pending_inc.new_removed_snaps`.

Purged snap read/write support includes:

- `make_purged_snap_epoch_key()`
- `make_purged_snap_key()`
- `make_purged_snap_key_value()`
- `lookup_purged_snap()`
- `insert_purged_snap_update()`
- `try_prune_purged_snaps()`
- `preprocess_get_purged_snaps()`

The per-pool `purged_snap_*` key stores intervals by the last snap in the key so forward iteration can find a candidate interval. `insert_purged_snap_update()` coalesces adjacent intervals by looking up the snap before and the first snap after the new interval. For Octopus+ `encode_pending()` also writes epoch-grouped `purged_epoch_*` keys to support `MMonGetPurgedSnaps` range queries.

`try_prune_purged_snaps()` depends on `MgrStatMonitor` being readable. It compares manager-reported purged snaps with the OSDMap removed-snap queue, stages actual prunes in `pending_inc.new_purged_snaps`, and bounds per-epoch work by `mon_max_snap_prune_per_epoch`.

## Map Serving and Subscriptions

`preprocess_get_osdmap()` replies to explicit map fetches with bounded full and incremental ranges, honoring `osd_map_message_max` and `osd_map_message_max_bytes`, and includes `cluster_osdmap_trim_lower_bound` plus newest epoch.

`send_latest()`, `build_latest_full()`, `build_incremental()`, `send_full()`, and both `send_incremental()` overloads implement protocol map delivery. Important behavior:

- If a requester asks before `get_first_committed()`, the monitor sends a base full map at `first_committed` before incrementals.
- Map messages are segmented by `osd_map_message_max`.
- Proxy sessions can route the send request through another monitor using `MRoute`.
- Session `osd_epoch` is advanced as maps are sent.

`check_osdmap_subs()` and `check_osdmap_sub()` serve ordinary OSDMap subscriptions. `check_pg_creates_subs()` and `check_pg_creates_sub()` serve stateful `osd_pg_creates` subscriptions only to up OSDs.

## Periodic Tick Behavior

`tick()` runs on active monitors. All active monitors reload the osdmap manifest and, when enabled, tune priority caches. Only the leader proceeds to mutating checks:

- Detect OSD beacon timeouts through `handle_osd_timeouts()`.
- Convert accumulated failure reports to down marks through `check_failures()`.
- Force a proposal when full-map pruning should run.
- Mark long-down OSDs out, with optional laggy adjustment and subtree-down suppression.
- Expire blocklist and range-blocklist entries.
- Stage purged-snap pruning.
- Update quota-driven pool full flags through `update_pools_status()`.
- Propose when any change or primed `pg_temp` exists.

`update_pools_status()` uses `MgrStatMonitor` pool stats to set or clear `FLAG_FULL_QUOTA` and `FLAG_FULL`, and clears nearfull/backfillfull when quota full takes precedence.

## Read Command Handling in This Chunk

`preprocess_command()` parses JSON commands, checks session existence, chooses a formatter, and handles many read-only commands directly:

- OSD map summaries and dumps: `osd stat`, `osd dump`, `osd tree`, `osd tree-from`, `osd ls`, `osd getmap`, `osd getcrushmap`, `osd ls-tree`, `osd info`, `osd getmaxosd`, `osd utilization`, `osd find`, `osd metadata`, `osd versions`, `osd count-metadata`, `osd numa-status`, `osd map`, `pg map`, `osd lspools`.
- Blocklist listing: `osd blocklist ls` and legacy `osd blacklist ls`.
- Pool reads: `osd pool ls`, `osd pool stretch show`, `osd pool get`, `osd pool get-quota`, `osd pool application get`, `osd get-require-min-compat-client`.
- CRUSH reads: tunable get, rule list/dump/list-by-class, crush dump/tree/tunables/ls, class list/list-osd/get-device-class, weight-set list/dump.
- EC profile reads: erasure-code profile list/get.

If a command is not handled as a read or idempotent application operation, `preprocess_command()` returns `false` to enter the prepare path in later command mutation logic.

Metadata helpers supporting these commands include `load_metadata()`, `count_metadata()`, `get_versions()`, `get_osd_objectstore_type()`, `is_pool_currently_all_bluestore()`, `dump_osd_metadata()`, and `print_nodes()`.

## Pool and CRUSH Creation Validation at Chunk Boundary

The chunk includes helper APIs used by pool and CRUSH mutations:

- `_have_pending_crush()`, `_get_stable_crush()`, and `_get_pending_crush()` load the current effective CRUSH map, using `pending_inc.crush` when already staged.
- `crush_rename_bucket()` validates rename on stable CRUSH when possible, then stages encoded pending CRUSH.
- `check_legacy_ec_plugin()`, `normalize_profile()`, `get_erasure_code()`, `parse_erasure_code_profile()`, and `erasure_code_profile_in_use()` validate EC profile/plugin details.
- `crush_rule_create_erasure()`, `prepare_pool_crush_rule()`, `get_crush_rule()`, `validate_crush_against_features()`, and `check_cluster_features()` stage or validate CRUSH rule changes while respecting monitor, OSD, and client feature compatibility.
- `prepare_pool_size()`, `prepare_pool_stripe_width()`, `get_replicated_stretch_crush_rule()`, `get_osd_num_by_crush()`, and `check_pg_num()` derive pool sizing and reject projected PG counts above `mon_max_pg_per_osd`.
- `prepare_new_pool(MonOpRequestRef)` is a simple pool-op wrapper for replicated pools.
- The overloaded `prepare_new_pool(string& ...)` begins full pool construction before the chunk boundary. Within this chunk it validates name, PG/PGP limits, crimson constraints, fast-read applicability, CRUSH rule, size/min_size, optional CRUSH smoke test, projected PG count, rule type, stripe width, duplicate pending names, allocates a new pool id, initializes flags and pool fields, handles stretch mode, PG autoscaler settings, EC shard metadata, target size options, cache defaults, EC optimizations, split ops, and stages `pending_inc.new_pool_names`.

The overloaded pool creation function continues after line 8317, so later chunks must complete the description of its tail and the surrounding command prepare path.

## Dependencies and Integration Points

Key dependencies in this chunk:

- Monitor core: `Monitor`, `Paxos`, `PaxosService`, `MonitorDBStore`, `MonSession`, `MonSessionMap`, `Subscription`, command reply helpers, cluster logger, and operation tracker.
- OSD map model: `OSDMap`, `OSDMap::Incremental`, `pg_pool_t`, `osd_info_t`, `osd_xinfo_t`, `PastIntervals`, `OSDMapMapping`, and map encoding feature logic.
- CRUSH and placement: `CrushWrapper`, `CrushTester`, `CrushTreeDumper`, CRUSH class/rule APIs, and mapping jobs.
- Messaging: `MOSDBeacon`, `MOSDFailure`, `MOSDMarkMeDown`, `MOSDMarkMeDead`, `MOSDFull`, `MOSDMap`, `MMonGetOSDMap`, `MOSDBoot`, `MOSDAlive`, `MPoolOp`, `MOSDPGCreate2`, `MOSDPGCreated`, `MOSDPGTemp`, `MOSDPGReadyToMerge`, `MOSDPGStopMerge`, `MRemoveSnaps`, `MRoute`, `MMonGetPurgedSnaps`, and replies.
- Other monitor services: `MgrStatMonitor` for pool stats and purged snap digest, auth/key server for unmanaged snapshot authorization, MDS/KV/Auth includes used elsewhere in the file, and stretch-mode coordination on `Monitor`.
- Common utilities: `Formatter`, `TextTable`, config observer APIs, strict numeric parsing, priority cache, CPU/NUMA parsing, checksum names, and erasure-code plugin registry.

## State and Persistence Behavior

Persistent state is staged in memory and encoded only through monitor transactions. Major state carriers:

- `osdmap`: current committed map.
- `pending_inc`: next OSDMap incremental and primary write surface for map mutations.
- `pending_metadata` and `pending_metadata_rm`: per-OSD metadata writes/deletes under `OSD_METADATA_PREFIX`.
- `creating_pgs`, `creating_pgs_by_osd_epoch`, `creating_pgs_epoch`, `pending_created_pgs`: creating-PG queue and notification state.
- `last_epoch_clean` and `osd_epochs`: trim safety state derived from beacons.
- `failure_info`, `last_osd_report`, and `down_pending_out`: runtime leader-side failure and down/out state. These are not persisted directly; they drive future OSDMap proposals.
- `osdmap_manifest`: persisted sparse full-map prune state.
- `inc_osd_cache` and `full_osd_cache`: feature-sensitive encoded map caches.

Durability boundaries to preserve:

- `prepare_*` methods must not directly write monitor store state; they should stage pending mutations and arrange callbacks.
- `encode_pending()` must write all durable auxiliary state that must atomically match the new OSDMap epoch.
- Trimming and pruning must keep at least one full map in any retained/reconstructable range.

## Risks and Edge Cases

- OSD state bit semantics are inverted in several pending paths: staging `CEPH_OSD_UP` in `new_state` can mean toggling an up OSD down. Callers must compare against current `osdmap` and any existing pending bitmask.
- Mixed-version encoding is sensitive. Full-map CRC mismatch handling in `update_from_paxos()` intentionally reloads canonical full maps supplied by a primary monitor; reencoding code must maintain compatible feature masks.
- Full-map pruning can make `get_version_full()` reconstruction mandatory. Bugs in manifest pinning, incremental retention, or trim-extra writes can make old maps unrecoverable.
- Creating-PG state is protected by `creating_pgs_lock` in some but not all visible access paths. Changes should respect existing lock boundaries and async mapping job cancellation.
- Failure detection combines reporter topology, laggy history, stale cancellation, ratio guards, and monitor leadership age. Tests should cover noout/nodown/noup/noin flags and ratio thresholds, not just the normal failure path.
- PG temp and PG merge paths defend against stale primaries and concurrent pool changes. Removing these checks can resurrect stale acting-set hints or shrink the wrong PG.
- Snap purge indexes use interval coalescing and forward iteration keyed by interval end. Off-by-one errors in `make_purged_snap_key_value()` or lookup start/end semantics would affect purge idempotence.
- `preprocess_command()` is a very broad read/dispatch function. Adding new commands requires carefully deciding whether the command is safe to answer before Paxos or must return `false` for prepare.
- `prepare_new_pool()` behavior at the cutoff includes release-specific defaults, crimson restrictions, stretch-mode restrictions, EC plugin loading, and PG-count admission control. Later code must be read before making whole-function conclusions.

## Test Signals

Useful tests and validation signals for this chunk include:

- Monitor startup and sync tests that verify initial OSDMap creation, mkfs map removal, `full_latest` recovery, canonical full-map CRC behavior, and cache-compatible map delivery.
- OSDMap trim/prune tests for `mon_min_osdmap_epochs`, `mon_osdmap_full_prune_*`, manifest persistence, pinned-map reconstruction, and `get_first_committed()` lower-bound behavior.
- OSD lifecycle tests for boot duplicate detection, fsid mismatch, release feature gating, crimson allow flag, stretch-mode OSD feature requirement, auto-in behavior, metadata persistence, full/nearfull/backfillfull state changes, alive/up_thru, and beacon timeout.
- Failure-report tests covering immediate failure, reporter subtree minimums, stale report cleanup, cancellation, laggy grace adjustment, nodown/noout/noup/noin flags, min up/in ratio gates, and down-out subtree suppression.
- PG tests for creating-PG queue persistence, PG-created removal, PG temp primary validation, EC optimized pg_temp ordering, PG merge ready/not-ready flow, crimson merge blocking, and PG stop-merge cancellation.
- Snap tests for self-managed removed snaps, Octopus purged epoch keys, purged interval coalescing, manager digest pruning, and purged snap query size limits.
- Command tests for read-only output parity between plain and formatted modes, epoch-specific OSDMap reads, `osd pool get all` filtering by pool type, CRUSH read branches, metadata corruption handling, quota status updates, and application get/read idempotence.
- Pool creation tests for CRUSH rule existence/type, erasure profile normalization, stripe-unit validation, EC plugin failure, PG count admission, stretch-mode replicated pool defaults, crimson pool constraints, and boundary conditions where helper functions return `-EAGAIN` for pending CRUSH/profile state.
