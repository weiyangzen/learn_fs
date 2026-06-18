# Research: sources/distributed-fs/ceph/src/mon/OSDMonitor.cc

This per-file research report is synthesized from ordered chunk research reports.

## Chunk Map

- `subset-b-006928`: lines 1-8317, `Docs/researches/chunks/subset-b-006928_research.md`
- `subset-b-006929`: lines 8318-16118, `Docs/researches/chunks/subset-b-006929_research.md`
- `subset-b-006930`: lines 16119-16125, `Docs/researches/chunks/subset-b-006930_research.md`

## Chunk Research

### subset-b-006928: lines 1-8317

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

### subset-b-006929: lines 8318-16118

# sources/distributed-fs/ceph/src/mon/OSDMonitor.cc lines 8318-16118

## Scope

This chunk covers the back half of Ceph's monitor-side OSD map command and pool-operation implementation. It starts in the tail of pool creation validation and includes pool flag setters, erasure-code optimization helpers, `ceph osd pool set`, pool application metadata, per-pool stretch settings, OSD create/new/destroy/purge flows, the main `MMonCommand` prepare dispatcher, legacy `MPoolOp` snapshot/pool operations, pool deletion/rename helpers, priority conversion, and stretch-mode degradation/recovery transitions.

The source is centered on `OSDMonitor` mutating `pending_inc`, the monitor's pending `OSDMap::Incremental`, and coordinating Paxos callbacks through `wait_for_commit()` or `wait_for_finished_proposal()`. It depends on earlier helpers in the same file for CRUSH validation, pool creation, erasure-code profile normalization, removed-snap lookup, command preprocessing, and monitor service lifecycle.

## Purpose

This section is the authoritative write path for many administrative changes to the OSDMap. It validates user and daemon requests, translates them into pending OSDMap increments, schedules Paxos proposals, and replies only when the relevant epoch is committed or the command is proved to be a no-op.

The covered code owns mutation of pool geometry and options, CRUSH maps, CRUSH classes/rules/weight sets, OSD existence and identity, OSD weights and state flags, blocklists, PG remap overrides, snapshots, cache tiers, pool availability status, force-created PGs, Crimson enablement, and stretch-mode state. It also provides compatibility behavior for older monitor/client schemas and idempotent retries.

## Important APIs, Types, and Functions

`prepare_set_flag()` and `prepare_unset_flag()` modify `pending_inc.new_flags` using existing OSDMap flags as a base and enqueue a command reply after the next committed epoch. They back `osd pause/unpause`, `osd set`, and `osd unset`.

`enable_pool_ec_optimizations()` validates and toggles `pg_pool_t::FLAG_EC_OPTIMIZATIONS` for erasure-coded pools. It requires all OSDs to be at least `tentacle`, obtains an `ErasureCodeInterface`, checks plugin support and 4 KiB stripe-unit alignment, and computes `nonprimary_shards` so optimized EC pools restrict primaries to safe shards. Disabling after enablement is refused. `maybe_enable_pool_split_ops()` then records shard mappings for direct-read-capable EC plugins and, on `umbrella` or later, enables `FLAG_CLIENT_SPLIT_READS` for non-Crimson pools.

`prepare_command_pool_set()` is the large `ceph osd pool set` implementation. It copies current or pending `pg_pool_t` state, parses typed values with SI/IEC/int/float helpers, rejects tier-only settings on non-tiers, and handles size/min_size, `pg_num` and `pgp_num` actual/target fields, autoscaling mode, CRUSH rule changes, pool flags, hit-set/cache-tier settings, EC overwrites/optimizations, OMAP support, quotas and targets, compression/checksum/fingerprint/dedup pool opts, recovery priority, read ratio, and fast-read. It updates `p.last_change` and stores the result in `pending_inc.new_pools`.

`prepare_command_pool_application()`, `preprocess_command_pool_application()`, and `_command_pool_application()` share validation for application metadata enable/disable/set/rm commands. They enforce base-tier-only metadata, maximum application/key/value counts and lengths, idempotent disables/removals, and force confirmation when adding a second application or disabling an application.

`prepare_command_pool_stretch_set()` and `prepare_command_pool_stretch_unset()` mutate per-pool stretch fields: peering bucket count/target/barrier, CRUSH rule, size, and min_size. They validate the pool, bucket type, subtree counts, CRUSH rule type, and user confirmation when requested bucket counts exceed available subtrees.

`_prepare_command_osd_crush_remove()`, `do_osd_crush_remove()`, and `prepare_command_osd_crush_remove()` remove or unlink CRUSH items and encode the changed `CrushWrapper` into `pending_inc.crush`.

`prepare_command_osd_remove()`, `_allocate_osd_id()`, `do_osd_create()`, `validate_osd_create()`, `prepare_command_osd_create()`, and `prepare_command_osd_new()` implement OSD identity lifecycle. They allocate or reuse IDs, validate UUID/id collisions, handle destroyed-OSD recreation, update device classes in CRUSH, set `CEPH_OSD_NEW`, record UUIDs, and coordinate cephx and dm-crypt lockbox secrets through `AuthMonitor` and `KVMonitor`.

`prepare_command()` parses `MMonCommand` JSON, requires a monitor session, and delegates to `prepare_command_impl()`. `parse_reweights()` parses JSON maps for bulk OSD reweighting. `parse_pgid()` validates PG identifiers and existence.

`prepare_command_impl()` is the central command dispatcher. It maps command prefixes to pending OSDMap changes, replies immediately for no-ops/errors, waits for existing proposals when a multi-epoch command must settle, or commits the new increment. Its branches cover CRUSH map replacement, CRUSH classes, buckets, rules, tunables, rule creation/removal/rename, erasure-code profile set/rm, max OSD count, full ratios, min compatible client, OSD flags, require-osd-release, OSD in/out/down/rm/stop, targeted no* flags by OSD/CRUSH node/device class, `pg_temp`, `primary_temp`, `pg_upmap`, `pg_upmap_items`, `pg_upmap_primary`, primary affinity, OSD reweight/lost/destroy/purge/new/create, blocklist operations, pool snapshots, force snapshot removal, pool create/delete/rename/set, tiers, quotas, pool application metadata, pool stretch settings, pool availability output, force-create-pg, stretch-mode forcing, and `set-allow-crimson`.

`enforce_pool_op_caps()`, `preprocess_pool_op()`, `_is_removed_snap()`, `_is_pending_removed_snap()`, `preprocess_pool_op_create()`, `prepare_pool_op()`, `prepare_pool_op_create()`, `prepare_pool_op_delete()`, and `_pool_op_reply()` are the older `MPoolOp` path. They enforce monitor caps or unmanaged-snapshot permissions, reject wrong FSIDs, short-circuit idempotent pool/snapshot operations, create/remove managed and unmanaged snapshots, record removed snapshots, and reply with `MPoolOpReply`.

`_check_remove_pool()`, `_check_become_tier()`, `_check_remove_tier()`, `_prepare_remove_pool()`, and `_prepare_rename_pool()` centralize deletion, tiering, and rename invariants. They protect CephFS pools, tier relationships, config and per-pool delete locks, fake pool deletion, cleanup of PG remaps/primary temps/upmaps/choose args, and removal of unused EC CRUSH rules.

`convert_pool_priorities()` rescales pool recovery priorities into the newer allowed range when existing values exceed `OSD_POOL_PRIORITY_MIN/MAX`.

`try_disable_stretch_mode()`, `try_enable_stretch_mode_pools()`, `try_enable_stretch_mode()`, `check_for_dead_crush_zones()`, `trigger_degraded_stretch_mode()`, `trigger_recovery_stretch_mode()`, `set_degraded_stretch_mode()`, `set_recovery_stretch_mode()`, `set_healthy_stretch_mode()`, `notify_new_pg_digest()`, `try_end_recovery_stretch_mode()`, and `trigger_healthy_stretch_mode()` implement stretch-mode validation and state transitions between healthy, degraded, and recovery modes.

## Control Flow

Most command handling follows a two-phase monitor pattern. The command is first validated against committed `osdmap` state and, when needed, projected pending state. If it needs no persistent change, the monitor replies directly through `reply_no_propose`. If it must mutate the OSDMap, the code writes fields in `pending_inc`, uses `wait_for_commit()` or `wait_for_finished_proposal()` with a command callback, and returns `true` so Paxos proposes the increment. If an earlier pending change must commit before validation can be meaningful, the `wait` label schedules a retry after the current proposal.

Pool setting control flow starts by resolving the pool and copying any pending pool update. Each `var` branch validates the requested value, applies release gates such as Nautilus for PG target fields, Quincy for `pg_num_max`, Tentacle for EC optimizations, and Umbrella for OMAP/client split reads, then writes the projected pool back to `pending_inc.new_pools`. PG changes distinguish actual values from targets: pre-Nautilus maps mutate actual `pg_num`/`pgp_num` directly, while newer maps set targets for manager-driven adjustment. Decreasing PG counts is gated more strictly than increasing, and Crimson pools require explicit merge/split allowances.

OSD create/new flow validates ID/UUID semantics before touching durable state. `osd new` requires a UUID, optionally parses JSON secrets, validates auth and lockbox idempotency, waits for `AuthMonitor` and `KVMonitor` writability, and then updates those services plus `pending_inc`. Existing UUIDs with matching secrets return success without a new OSDMap proposal. Destroy and purge paths validate that the OSD is down, remove cephx/config-key material, mark `CEPH_OSD_DESTROYED`, optionally remove CRUSH items, then remove the OSD entry.

The CRUSH command branches typically obtain `_get_pending_crush()`, mutate a `CrushWrapper`, validate feature compatibility or rule type where needed, encode into `pending_inc.crush`, and wait for commit. Some commands are explicitly idempotent on replays, such as class/rule rename when the destination already exists, missing rule/class removals, or CRUSH updates that match current state with a prior version.

Pool creation handles replicated and erasure-coded forms, default pool type, implicit EC profile/rule creation, expected object counts, target size options, fast-read, autoscale mode, bulk flag, and Crimson flag. It delegates pool object initialization to `prepare_new_pool()` and may split the operation across epochs if the default EC profile or rule must first be created.

Pool deletion checks both committed and pending pool state. It can fake deletion by renaming when configured, otherwise records `pending_inc.old_pools`, clears per-PG temporary mappings and upmap state for that pool, removes pool choose args, and removes an unused EC CRUSH rule. It refuses deletion for CephFS-attached pools, tier pools, pools with tiers, pools protected by `mon_allow_pool_delete == false`, or `FLAG_NODELETE`.

Legacy `MPoolOp` control flow mirrors command handling but replies with `MPoolOpReply`. Preprocess rejects unauthorized operations and short-circuits idempotent requests. Prepare projects `pg_pool_t`, enforces mutual exclusion between pool snapshots and unmanaged snapshots, updates snap metadata or removed-snap queues, and waits for the finished proposal with a `C_PoolOp` callback.

Stretch mode enablement first validates all pools and CRUSH topology without committing: pools must be replicated and start from default size/min_size unless already on the requested rule, the dividing bucket type must exist, there must be exactly two subtrees, bucket count must be two, and site weights must be within `mon_stretch_max_bucket_weight_delta`. Commit mode then rewrites every pool's CRUSH rule, peering bucket fields, size, and min_size, and records global stretch fields in `pending_inc`. Degradation and recovery triggers are asynchronous monitor-side state transitions driven by dead CRUSH zones and manager PG digests.

## State and Persistence Behavior

The principal persistent output is `pending_inc`, an `OSDMap::Incremental`. This chunk writes `new_flags`, `crush`, `new_pools`, `new_pool_names`, `old_pools`, `new_max_osd`, `new_state`, `new_uuid`, `new_weight`, `new_xinfo`, `new_crush_node_flags`, `new_device_class_flags`, `new_pg_temp`, `new_primary_temp`, `new_pg_upmap`, `old_pg_upmap`, `new_pg_upmap_items`, `old_pg_upmap_items`, `new_pg_upmap_primary`, `old_pg_upmap_primary`, `new_primary_affinity`, `new_lost`, blocklist additions/removals, erasure-code profile additions/removals, removed snaps, release requirements, full ratios, stretch-mode fields, and `allow_crimson`.

Pool state persists through `pg_pool_t` copies in `pending_inc.new_pools`. Mutated fields include size/min_size, PG actual/pending/target counts, autoscale mode, CRUSH rule, flags, hit-set and cache settings, EC profile metadata, stripe width, shard mappings, target sizes, compression/checksum/dedup options, quota fields, tiers/read/write tier, snap state, application metadata, recovery priority, Crimson flags, OMAP support, split-read flags, and stretch peering fields. `last_change` and snap epochs are set to the pending epoch when client-visible behavior changes.

CRUSH changes are persisted by encoding a complete modified `CrushWrapper` into `pending_inc.crush`, not by logging small CRUSH deltas. This includes map replacement, class changes, item insert/move/link/remove, bucket swaps, tunables, rules, choose args, weight changes, and choose-arg cleanup during pool deletion.

OSD identity state spans OSDMap, AuthMonitor, KVMonitor, and monitor metadata. `do_osd_create()` records OSD weights, NEW state, UUIDs, and optional CRUSH device class. Destroy/purge paths remove auth/config-key material before marking destroyed or removing the OSD. `prepare_command_osd_remove()` also queues metadata removal via `pending_metadata_rm`.

Snapshot state persists in pool snap maps and monitor removed-snap queues. Managed snapshots use `add_snap()` and `remove_pool_snap()`. Unmanaged snapshots use `add_unmanaged_snap()` and `remove_unmanaged_snap()`, with pre-Octopus compatibility behavior. Forced removal adds ranges to `pending_inc.new_removed_snaps` so OSDs can retrim leaked snapshots.

Stretch mode persists at two levels: global `pending_inc.change_stretch_mode`, `stretch_mode_enabled`, bucket counts, degraded/recovery flags, and bucket type; and per-pool peering bucket fields, mandatory member, CRUSH rule, size/min_size, and forced op resend epochs. `stretch_recovery_triggered` is local monitor timing state used to decide when PG digest health permits leaving recovery.

## Dependencies and Integration Points

`OSDMap`, `pg_pool_t`, `pool_opts_t`, `CrushWrapper`, `CrushTester`, `ErasureCodeInterface`, `HitSet` implementations, `Compressor`, `Checksummer`, `FeatureMap`, `PGMapDigest`, and `PoolAvailability` provide the domain model.

Monitor integration is broad. `mon.reply_command()` and `mon.send_reply()` return results. `wait_for_commit()`, `wait_for_finished_proposal()`, `force_immediate_propose()`, `propose_pending()`, and Paxos plug/unplug control proposal timing. `mon.authmon()` and `mon.kvmon()` validate and persist OSD secrets and lockbox keys. `mon.mdsmon()` blocks unsafe CephFS pool/tier/snapshot operations. `mon.mgrstatmon()` supplies pool stats, availability data, and PG recovery digests. `mon.monmap` and combined feature maps gate release transitions.

Command parsing relies on `cmdmap_t`, `cmd_getval()`, `cmd_getval_or()`, `cmd_getval_compat_cephbool()`, strict numeric parsing helpers, JSON parsing helpers, and `Formatter` output. Several branches preserve compatibility with older command schemas, legacy `blacklist` naming, and pre-Nautilus/pre-Octopus OSDMap formats.

Cluster-feature integration uses `check_cluster_features()`, `validate_crush_against_features()`, `HAVE_FEATURE()`, required monitor features, `require_min_compat_client`, and `require_osd_release`. These checks prevent map features from being introduced while clients, OSDs, monitors, MDSs, or managers may not understand them.

Operational side effects include cluster log messages for marking OSDs out, manager availability clearing, blocklist/range-blocklist updates, `creating_pgs` tracking for force-created PGs, and immediate proposal forcing for OSD new/destroy/purge operations that touch multiple monitor services.

## Risks and Edge Cases

The dispatcher is extremely broad and uses shared `err`, `ss`, `rs`, and `goto` labels. Bugs in branch ordering or missing `goto reply_no_propose/update/wait` paths can accidentally propose partial state, reply before a needed proposal, or lose an error message.

Many operations are intentionally idempotent under retries, but idempotency is uneven. OSD create/new depends on UUID and secret matching; CRUSH class/rule renames infer success from destination existence; pool delete may become a fake rename; missing pool/snap delete often returns success. Callers that need strict "did this change happen" semantics must account for this.

Pending-versus-committed state is subtle. The comment at the start of `prepare_command_impl()` states that no-op checks usually use committed state even if pending conflicting changes exist. Some branches inspect pending state and wait, while others intentionally squash pending pool updates. Concurrent administrative clients can therefore observe operations as ordered by committed epochs, not by arrival at the monitor.

PG geometry changes are high risk. Size increases call `check_pg_num()`, PG decreases require newer OSDMap formats and single-step pending decreases, cache pool splits require force confirmation, Crimson pools disallow or gate split/merge, and pool flags such as `NOPGCHANGE` and `CREATING` block changes. Incorrect validation can strand PGs, break client mapping, or cause large data movement.

EC optimization and overwrite flags are effectively irreversible and version-sensitive. They depend on plugin-reported capabilities, shard mappings, stripe-unit alignment, BlueStore-only placement for overwrites, and conversion of existing `pg_temp` order when optimizations are first enabled.

CRUSH mutations can cause large remaps or invalid placement. The code uses feature validation, optional smoke tests, rule type checks, force flags for dangerous bucket/class/hash changes, and refuses removal of rules/classes still in use or referenced by EC profiles. Still, many branches modify a full CRUSH map in memory and encode it wholesale, so accidental stale pending state can be costly.

OSD destroy/purge/new flows span OSDMap, auth, config-key, CRUSH, and metadata. Partial failure is mitigated by validation ordering, Paxos plug/unplug, and idempotency checks, but the code comments explicitly require later steps in purge to be guaranteed after auth/config-key side effects are applied.

Pool deletion and tier changes are blocked for CephFS and tier invariants, but cache tier transitions depend on manager pool statistics for dirty object counts. Missing or stale stats can affect whether a dangerous transition is refused.

Snapshot operations must avoid mixing pool-managed and unmanaged modes, must block CephFS-attached pools, and must handle already purged or pending-removed snap IDs. Force-remove-snap can deliberately cause OSD retrimming and must not exceed the pool's snap sequence.

Stretch mode is explicitly limited to two sites. It asserts or errors on other topologies, halves pool min_size in degraded mode, forces mandatory bucket membership, and uses manager digest health plus a wait timer to exit recovery. Incorrect dead-zone detection or stale PG digest data could prematurely change pool peering rules.

## Test Signals

Command-dispatch tests should cover every `prepare_command_impl()` prefix family with success, validation failure, idempotent retry, pending-change wait, and formatter/plain output variants. Assertions should verify `pending_inc` fields and returned proposal behavior, not only command text.

Pool setting tests should exercise `size`, `min_size`, `pg_num` and `pgp_num` actual/target changes, autoscale bounds, `pg_num_min/max`, Crimson split/merge gates, EC overwrite and optimization gates, OMAP support restrictions, pool option parsing with SI/IEC units, dedup tier lookup, and irreversible flag disable attempts.

CRUSH tests should cover full map replacement with `prior_version`, smoke-test failure, class create/rm/rename, device class set/rm, bucket add/move/link/unlink/swap, weight-set create/reweight/remove, tunables, replicated and erasure rule creation, rule removal while in use, and cleanup of choose args/rules on pool deletion.

OSD lifecycle tests should cover legacy `osd create`, `osd new` with and without secrets, idempotent UUID reuse, mismatched secrets, destroyed-ID recreation, OSD remove while up, destroy/purge with auth or KVMonitor not writeable, purge-new restrictions, device-class creation, and metadata removal queuing.

Pool lifecycle and snapshot tests should cover pool create with replicated and EC defaults, implicit EC profile/rule creation across two epochs, dot-prefixed internal names, fake and real pool delete, rename idempotency, managed snapshots, unmanaged snapshots, removed-snap idempotency, force-remove dry runs, and CephFS pool rejection.

Tier/cache tests should cover adding/removing tiers, overlays, cache modes and invalid transitions with dirty objects, `add-cache` default hit-set configuration, tier pool non-empty rejection, CephFS restrictions, Crimson tier rejection, and force-nonempty snapshot hazards.

Placement override tests should cover `pg_temp`, `primary_temp`, `pg repeer`, pg-upmap, pg-upmap-items, pg-upmap-primary, release/feature gates, pending update waits, duplicate entries, invalid OSD IDs, illegal acting sets, and pool-pending-removal behavior.

Stretch tests should cover enable validation for non-replicated pools, non-default size/min_size, invalid bucket type, more or fewer than two zones, weight imbalance, per-pool stretch set/unset, dead-zone detection, degraded mode pool rewrites, recovery mode triggering, PG digest based exit, and forced healthy/recovery commands.

Security and capability tests should cover `MMonCommand` without session, `MPoolOp` write caps, unmanaged-snapshot special permissions, blocklist/range-blocklist feature gates, `set-allow-crimson` requiring both experimental feature and confirmation, and release-gate commands with connected old clients or missing monitor/OSD features.

### subset-b-006930: lines 16119-16125

# sources/distributed-fs/ceph/src/mon/OSDMonitor.cc lines 16119-16125

## Scope

This chunk is the tail of `OSDMonitor::trigger_healthy_stretch_mode()`. The function is called after stretch-mode recovery has completed, either because `try_end_recovery_stretch_mode()` observed no degraded, inactive, or unknown PG recovery state in `PGMapDigest`, or because the caller forced the transition. The covered lines update every stretch-aware pool in the pending OSDMap increment, then submit the increment with `propose_pending()`.

The exact covered operations are:

- Clear the pool's required CRUSH member with `peering_crush_mandatory_member = CRUSH_ITEM_NONE`.
- Restore the pool's `min_size` from monitor configuration `mon_stretch_pool_min_size`.
- Mark the pending epoch as `last_force_op_resend`.
- Close the loop and call `propose_pending()`.

The immediately preceding lines in the same function set `newp.peering_crush_bucket_count = osdmap.stretch_bucket_count` and reset the global stretch-mode fields in `pending_inc` so `degraded_stretch_mode` and `recovering_stretch_mode` become zero.

## Purpose

The purpose of this chunk is to finish returning a stretch-mode pool from a degraded single-site peering posture to the normal healthy stretch-mode posture. While degraded, `trigger_degraded_stretch_mode()` lowers each affected pool's `peering_crush_bucket_count` to the remaining site count, sets `peering_crush_mandatory_member` to the surviving site, halves `min_size`, and forces operation resend. This chunk reverses the pool-specific parts of that degraded-mode relaxation.

Clearing `peering_crush_mandatory_member` removes the requirement that PG acting sets include a replica under one specific CRUSH bucket. Restoring `min_size` to `mon_stretch_pool_min_size` reinstates the normal write/recovery availability threshold for stretch pools. Updating `last_force_op_resend` forces clients and OSD-side PG handling to discard or resend operations that were mapped against the older degraded/recovering pool parameters. `propose_pending()` then persists and publishes the OSDMap increment through the monitor proposal path.

## Important APIs, Types, and Fields

- `OSDMonitor::trigger_healthy_stretch_mode()` is a monitor-side transition helper. It asserts writeability before building a pending OSDMap increment and proposing it.
- `osdmap.pools` is the current pool map. The loop copies each pool entry by value as `pgi`; only pools with non-zero `peering_crush_bucket_count` are treated as stretch-aware pools.
- `pending_inc.get_new_pool(pgi.first, &pgi.second)` returns a mutable `pg_pool_t` entry in `OSDMap::Incremental::new_pools`, initialized from the current pool if needed.
- `pg_pool_t::peering_crush_mandatory_member` is an optional CRUSH item that stretch peering must include. `CRUSH_ITEM_NONE` disables the mandatory-member constraint.
- `pg_pool_t::min_size` is the minimum number of acting replicas needed for normal IO and recoverability decisions.
- `g_conf().get_val<uint64_t>("mon_stretch_pool_min_size")` supplies the configured healthy stretch pool minimum size used here and when enabling stretch mode.
- `pg_pool_t::set_last_force_op_resend(pending_inc.epoch)` sets `last_force_op_resend`, `last_force_op_resend_prenautilus`, and `last_force_op_resend_preluminous` to the pending OSDMap epoch for compatibility with older clients.
- `propose_pending()` submits the constructed `pending_inc` through monitor consensus, making the transition durable only after the proposal commits.

## Control Flow

`try_end_recovery_stretch_mode()` first ensures the monitor is leader, degraded stretch mode is active, recovering stretch mode is active, and the OSDMonitor plus MgrStatMonitor data are readable. It waits asynchronously with `CMonExitRecovery` if either monitor component is not readable. Once the configured `mon_stretch_recovery_min_wait` has elapsed, or the request is forced, it reads `PGMapDigest` recovery counters and calls `mon.trigger_healthy_stretch_mode()` if no degraded, inactive, or unknown PGs remain.

Inside `trigger_healthy_stretch_mode()`, the monitor resets the in-memory `stretch_recovery_triggered` timestamp, marks `pending_inc.change_stretch_mode`, copies the current stretch enablement, bucket count, and bucket type into the increment, and sets both `new_degraded_stretch_mode` and `new_recovering_stretch_mode` to zero. The loop in this chunk then applies the matching pool-level state restoration for pools that are already stretch-aware. Non-stretch pools are skipped because their `peering_crush_bucket_count` is zero.

The function ends with `propose_pending()`. There is no local return-value handling in this helper; success or retry is governed by the monitor proposal machinery.

## State and Persistence Behavior

The state changes are staged in `OSDMap::Incremental`, not written directly into the current committed `osdmap`. The global stretch-mode fields staged before the covered lines are applied by `OSDMap::apply_incremental()` when `inc.change_stretch_mode` is true: `stretch_mode_enabled`, `stretch_bucket_count`, `degraded_stretch_mode`, `recovering_stretch_mode`, and `stretch_mode_bucket` are copied from the increment.

The pool changes staged in `pending_inc.new_pools` are encoded as part of the same OSDMap epoch. After commit, each restored pool has no mandatory CRUSH member, has its stretch bucket count restored to the full stretch bucket count, and has `min_size` reset to the configured healthy stretch value. `last_force_op_resend` is persistent pool metadata; clients and OSD PG code use it as an epoch fence. For example, PG message handling rejects messages from epochs older than the pool's `last_force_op_resend`, and Objecter tracking observes this field to resend operations when the map epoch reaches the force-resend epoch.

`stretch_recovery_triggered` itself is local monitor state used to debounce recovery exit checks. It is cleared before the proposed map transition, but the durable cluster-visible change is the OSDMap increment.

## Dependencies and Integration Points

This chunk depends on the stretch-mode state prepared by nearby helpers:

- `trigger_degraded_stretch_mode()` enters degraded mode, constrains pools to the surviving CRUSH site, reduces `min_size`, and forces operation resend.
- `trigger_recovery_stretch_mode()` marks recovery mode and forces resend without changing pool placement constraints.
- `try_end_recovery_stretch_mode()` decides when this healthy transition is allowed using monitor leadership/readability, Mgr PG digest recovery stats, `mon_stretch_recovery_min_wait`, and optional force.
- `try_enable_stretch_mode()` initializes the same pool fields when stretch mode is first enabled.
- `try_disable_stretch_mode()` clears stretch-mode pool fields entirely when stretch mode is disabled, but refuses to run while recovering.

Downstream consumers include OSD peering code, client/Objecter map handling, and any monitor command/reporting path that dumps pool fields. `PeeringState` uses `peering_crush_mandatory_member` to ensure a selected acting set includes a required CRUSH ancestor when one is configured, and uses `min_size` to decide whether recovery and IO can proceed. OSDMap encoding/decoding persists these fields across monitor epochs and distributes them to OSDs and clients.

## Risks

- The function assumes it is called only while the monitor is writeable; the `ceph_assert(is_writeable())` catches violations but would crash in assert-enabled builds.
- Resetting `min_size` from `mon_stretch_pool_min_size` rather than the pool's previous value means operator changes made while degraded could be overwritten for stretch-aware pools during recovery exit.
- The loop selects pools by non-zero `peering_crush_bucket_count`. A pool with partially inconsistent stretch fields but zero bucket count would not be repaired by this transition.
- `pgi` is copied by value, so the function relies on `pending_inc.get_new_pool()` to update the real pending pool entry. This is correct here, but future edits must avoid mutating `pgi.second` directly.
- If `propose_pending()` fails, is delayed, or loses leadership before commit, the durable OSDMap transition has not happened even though local `stretch_recovery_triggered` was cleared.
- `set_last_force_op_resend()` intentionally perturbs client/OSD operation flow. Missing this call could leave operations mapped under degraded constraints in flight; setting it unnecessarily can cause extra client resend work.

## Test and Validation Signals

Useful coverage should exercise a two-site stretch cluster through degraded, recovery, and healthy transitions:

- Unit or integration tests should verify that exiting recovery sets `degraded_stretch_mode == 0`, `recovering_stretch_mode == 0`, preserves `stretch_mode_enabled`, and keeps `stretch_bucket_count` and `stretch_mode_bucket` aligned with the pre-existing stretch configuration.
- Pool assertions should check that each stretch-aware pool has `peering_crush_bucket_count == osdmap.stretch_bucket_count`, `peering_crush_mandatory_member == CRUSH_ITEM_NONE`, `min_size == mon_stretch_pool_min_size`, and `last_force_op_resend == pending epoch`.
- Recovery-gating tests should cover both natural exit after `mon_stretch_recovery_min_wait` with clean PG digest counters and forced exit with non-clean counters.
- Peering tests should confirm that acting-set selection no longer requires the formerly surviving CRUSH site after healthy transition and that the restored `min_size` is enforced.
- Client/Objecter or OSD PG tests should observe operation resend or rejection behavior around the `last_force_op_resend` epoch.
- Negative tests should verify `try_disable_stretch_mode()` remains blocked while recovering, and that non-stretch pools are not modified by `trigger_healthy_stretch_mode()`.
