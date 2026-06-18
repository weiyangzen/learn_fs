# subset-b-006911 Research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/mds/MDBalancer.cc -->
# sources/distributed-fs/ceph/src/mds/MDBalancer.cc

## Purpose
`MDBalancer.cc` implements the CephFS MDS metadata balancer. It samples local metadata load, exchanges `MHeartbeat` messages with peer MDS ranks, computes inter-rank directory export targets, drives actual subtree exports through `Migrator`, and manages hot/cold directory fragmentation. It also handles export-pin policy, popularity accounting, directory replication for read-heavy directories, Mantle-scripted balancing, and admin load dumping.

## Important APIs, Functions, and Types
The file defines `MDBalancer::proc_message`, the constructor, `handle_conf_change`, `tick`, `handle_export_pins`, `send_heartbeat`, `handle_heartbeat`, `prep_rebalance`, `mantle_prep_rebalance`, `try_rebalance`, `find_exports`, `queue_split`, `queue_merge`, `maybe_fragment`, `hit_inode`, `hit_dir`, `subtract_export`, `add_import`, `adjust_pop_for_rename`, `handle_mds_failure`, and `dump_loads`. It also defines `mds_load_t::mds_load`, which converts `mds_load_t` metrics into the configured scalar load mode. `C_Bal_SendHeartbeat` is a small delayed callback used when the cache is not open yet.

The implementation depends heavily on `MDSRank`, `MDSMap`, `MDCache`, `CDir`, `CInode`, `Migrator`, `Messenger`, `Objecter`, `Mantle`, `MHeartbeat`, and Ceph config/logging utilities. The load model uses `dirfrag_load_vec_t` counters for `auth`, `all`, `pop_me`, `pop_nested`, `pop_auth_subtree`, and `pop_auth_subtree_nested`, plus request rate, dispatch queue length, CPU ticks, and cache hit rate.

## Control Flow
`tick()` is the periodic entry point. If `mds_bal_export_pin` is enabled it first drains export-pin work. It updates `last_sample` when `mds_bal_sample_interval` elapses, and rank 0 periodically starts a balancing heartbeat when automated balancing is allowed, the MDS is active, `mds_bal_interval` has elapsed, and the configured balancing count/window allows another run.

`send_heartbeat()` refuses to run while the cluster is degraded. If the cache is not open it registers `C_Bal_SendHeartbeat` and retries later. Rank 0 increments `beat_epoch` and clears prior load samples. Every rank computes local load with `get_load()`, records logger counters, builds an import map from auth subtrees whose inode authority is a different rank, stores local data, and sends an `MHeartbeat` containing the load and import map to every other up rank.

`handle_heartbeat()` is the scatter/gather side. It ignores messages while inactive, delayed until the cache is open, or while the cluster is degraded. Nonzero ranks advance to a new epoch when they receive a future beat; receiving rank-0 heartbeats triggers an immediate response heartbeat. Rank 0 accepts only current-epoch peer heartbeats. Once all in-MDS ranks have reported and the rank mask contains at least one participating MDS, the balancer first tries Mantle if the MDS map names a balancer object; otherwise, or if Mantle fails, it uses the built-in heuristic.

The built-in `prep_rebalance()` rescales each rank's configured scalar load back into metadata-load units using this rank's auth metadata load as a conversion factor. It computes `target_load` across only rank-mask participants, marks underloaded or barely overloaded ranks in `mds_last_epoch_under_map`, waits for `mds_bal_overload_epochs` before treating the local rank as a real exporter, classifies importers/exporters, then fills `balance_state_t::targets` through `try_match()`. It first favors returning load to ranks that were import sources, then alternates by beat between larger-exporter/larger-importer and smaller-exporter/larger-importer matching.

The Mantle path, `mantle_prep_rebalance()`, lazily refreshes the configured balancer object from RADOS with `localize_balancer()`, builds a vector of per-rank metrics (`auth.meta_load`, `all.meta_load`, `req_rate`, `queue_len`, and `cpu_load_avg`), calls `Mantle::balance`, validates that the returned target map covers the cluster, and then reuses `try_rebalance()`.

`try_rebalance()` is the export execution phase. It clears the migrator export queue before planning, builds maps of this rank's full-auth subtrees and imported subtrees, exports idle imports back to their original authority when below `mds_bal_idle_threshold`, then walks each target amount. It first reexports imports that came from the target, then other suitable imports, then calls `find_exports()` to search nested auth subtrees for chunks that match the target amount. Selected directories are exported with `export_dir_nicely`.

`find_exports()` recursively walks `pop_lru_subdirs` within an auth directory, skips already selected or frozen/freezing candidates, and uses configurable need/min/max/mid/minchunk factors to choose a subtree whose `pop_auth_subtree.meta_load()` fills enough of the export target. It stops if a run exceeds roughly 0.1 seconds, setting `have = amount` to abort further searching.

Fragmentation runs on delayed contexts. `queue_split()` inserts a dirfrag into `split_pending` and either schedules a timer or, for fast splits, queues an end-of-dispatch waiter. Its callback erases the pending mark, skips stopping/non-auth/missing dirfrags, adjusts split bits to satisfy ephemeral-distributed minimum fragment bits, and calls `MDCache::split_dir`. `queue_merge()` similarly tracks `merge_pending`, waits `mds_bal_fragment_interval`, requires the dirfrag to remain auth, checks sibling completeness and `should_merge()` status up the fragment tree, and calls `MDCache::merge_dir` when it can coalesce.

Popularity updates enter through `hit_inode()` and `hit_dir()`. `hit_inode()` hits the inode counter and propagates to the parent directory. `hit_dir()` skips stray directories, updates local popularity, evaluates hot split thresholds, calls `maybe_fragment()`, optionally toggles directory replication based on read popularity and replicate/unreplicate thresholds, and then propagates nested/auth-subtree counters up ancestors. Export/import/rename helper methods adjust the same nested counters when subtrees move between authorities or parents.

## State and Persistence
The balancer's own persistent process state is in memory: cached config values, `beat_epoch`, `bal_code`, `bal_version`, timestamps (`last_heartbeat`, `last_sample`, `rebalance_time`, `last_get_load`), previous request/CPU/traverse counters, pending split/merge dirfrag sets, per-epoch maps (`mds_load`, `mds_meta_load`, `mds_import_map`, `mds_last_epoch_under_map`), and computed `my_load`/`target_load`.

Cross-daemon persistence is mostly indirect. Mantle code is read from a RADOS object named by `MDSMap::get_balancer()` in the metadata pool and cached by object name as `bal_version`. Load and import maps are exchanged in transient `MHeartbeat` messages. Directory popularity and replication metadata live on `CDir`/`CInode`; some of those fields are encoded by `CDir`, not by `MDBalancer` itself. Actual export state and subtree authority changes are delegated to `MDCache`/`Migrator`.

The constructor and `handle_conf_change()` cache many runtime options (`mds_bal_*`), so live config changes depend on callers passing the correct changed-key set. `handle_mds_failure()` clears `mds_last_epoch_under_map` only when rank 0 fails, preventing stale overload history from carrying across coordinator failure.

## Dependencies and Integration Points
This file integrates with the MDS heartbeat message path (`proc_message`, `MHeartbeat`), rank membership and balancing policy from `MDSMap`, active/open/degraded state from `MDSRank`, subtree and dirfrag operations in `MDCache`, export execution in `Migrator`, request and traversal counters from MDS logging, dispatch queue length from `Messenger`, CPU accounting via `read_process_cpu_ticks`, and optional external balancing logic through `Mantle` and RADOS reads via `Objecter`.

It is called from high-traffic server and cache paths: metadata operations call `hit_inode`, `hit_dir`, and `maybe_fragment`; `MDCache` invokes split/merge/export-pin handling and rename adjustment; `MDSRank` constructs the balancer, calls queue methods, and exposes `dump_loads` through an admin command. Export-pin handling is tightly coupled to inode export-pin policies, ephemeral random/distributed pin modes, aux subtree state, hash-to-rank bucket selection, and subtree authority updates.

## Risks
Balancing is sensitive to timing and stale state. `get_load()` reuses previous rates for sub-second samples and depends on monotonic request/CPU/traverse counters. The built-in rebalance assumes `mds_load.at(i)` exists for ranks `0..cluster_size-1`; heartbeat gather completeness and rank numbering must stay consistent. `target_load` is divided by the number of ranks in the rank mask, so an empty or stale mask would be dangerous, although callers check for a positive mask count.

The export planner uses several heuristics and hard-coded thresholds (`MIN_OFFLOAD`, `MIN_REEXPORT`, short `find_exports()` runtime cap). It can undershoot, skip frozen directories, avoid export-pinned directories, and leave load imbalanced when no suitably sized subtree is found. Mantle introduces script/object risks: RADOS read timeout is tied to half of `bal_interval`, returned target maps must match cluster size, and failed Mantle execution falls back to the old balancer after warning.

Fragmentation callbacks are asynchronous and deliberately tolerate races with cache eviction, authority loss, stopping MDS state, and duplicate fast-split callbacks. Incorrect pending-set handling could suppress future fragmentation or duplicate freezes. Export-pin handling can repeatedly delay work for invalid pins, freezing dirfrags, empty exports, or ephemeral-distributed directories that still need splitting.

Popularity propagation is complex because counters must remain consistent across hits, replication adjustments, exports, imports, and renames. Replication toggling updates only selected read counters and has an in-code note that whole-hierarchy adjustment is incomplete. Directory moves across subtrees must maintain `pop_lru_subdirs` and nested/auth counters in the correct ancestor range.

## Test Signals
Useful direct signals include unit or integration coverage for `mds_load_t::mds_load()` modes, config-change refresh, heartbeat epoch transitions, complete heartbeat gathering, Mantle success/fallback behavior, and rank-mask load targeting. CephFS integration tests should observe that overloaded ranks enqueue expected exports, idle imports return to origin, export-pinned directories move or create aux subtrees correctly, and degraded/opening/stopping states suppress unsafe work.

Fragmentation tests should verify delayed and fast split scheduling, duplicate pending behavior, ephemeral-distributed minimum bits, merge sibling completeness, and no split/merge after authority loss. Popularity tests should exercise read/write/readdir/fetch/store hits, rename/export/import counter adjustment, replication and unreplication threshold transitions, and `dump_loads()` formatter output at bounded depths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/mds/MDBalancer.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/mds/MDBalancer.h -->
# sources/distributed-fs/ceph/src/mds/MDBalancer.h

## Purpose
`MDBalancer.h` declares the CephFS MDS metadata-balancing class. The header defines the public surface used by `MDSRank`, `MDCache`, metadata operation paths, and admin dump handlers to track metadata popularity, schedule dirfrag split/merge work, process balancer heartbeats, handle export pins, and expose balancing configuration. It also declares the private state used to coordinate heartbeat epochs and per-rank load-transfer planning.

## Important APIs, Types, and Members
`MDBalancer` uses `ceph::coarse_mono_clock` and `ceph::coarse_mono_time` aliases for low-cost timing. The constructor accepts owning/integration pointers to `MDSRank`, `Messenger`, and `MonClient`. Public APIs are `handle_conf_change`, `proc_message`, `tick`, `handle_export_pins`, `subtract_export`, `add_import`, `adjust_pop_for_rename`, `hit_inode`, `hit_dir`, `queue_split`, `queue_merge`, `is_fragment_pending`, `maybe_fragment`, `handle_mds_failure`, `dump_loads`, and small getters for selected config values.

The private `balance_state_t` groups target, imported, and exported load maps keyed by `mds_rank_t`; this is the intermediate structure shared by the built-in and Mantle balancers before export execution. `AUTH_TREES_THRESHOLD` is a logging guard for auth-subtree dumps. Private helper declarations include rebalance preparation/execution (`prep_rebalance`, `mantle_prep_rebalance`, `try_rebalance`, `find_exports`, `try_match`), local metric handling (`get_load`, `send_heartbeat`, `handle_heartbeat`), Mantle code localization (`localize_balancer`), and rank-mask checks.

Config cache members mirror MDS options: fragmentation enable/interval, balancing interval/mode/max limits, export-pin behavior, sample interval, split read/write thresholds, replication thresholds, fast fragment factor, split bits/size, merge size, and remaining max balance count. Runtime members include integration pointers, `beat_epoch`, Mantle code/version strings, heartbeat/sample/rebalance/load timestamps, last metric counters, pending split/merge sets, per-epoch load/import maps, overload history, and current local/target load scalars.

## Control Flow Contract
Callers normally use `tick()` as regular upkeep; it may process export pins and initiate heartbeat-based balancing. Message dispatch should call `proc_message()`, which currently accepts balancer heartbeat messages. Metadata operation paths call `hit_inode()` and `hit_dir()` to feed popularity data; cache and server paths can call `maybe_fragment()` directly when they need size-based fragmentation checks before a later popularity hit. Split/merge requests are queued through `queue_split()` and `queue_merge()`, and callers can check `is_fragment_pending()` to avoid conflicting fragment work.

Subtree movement callers use `subtract_export()` before encoding exported directories, `add_import()` after importing directories, and `adjust_pop_for_rename()` when a subtree changes parent. Failure handling is deliberately small: `handle_mds_failure()` lets the implementation clear rank-0-coordinated overload history. Admin code calls `dump_loads()` to serialize current dirfrag and per-rank load state.

## State and Persistence
The header declares no on-disk persistence owned by `MDBalancer`; it is a runtime coordinator. Its state is epoch-scoped and process-local except for data delegated to other subsystems. `mds_load`, `mds_meta_load`, and `mds_import_map` are rebuilt from heartbeat exchanges. `split_pending` and `merge_pending` are in-memory guards around delayed contexts. `bal_code` and `bal_version` cache an external Mantle balancer object loaded by the implementation. Popularity vectors and replication flags are stored on `CDir`/`CInode` objects that the balancer mutates through public helper calls.

The config fields are cached copies of dynamic options, not authoritative storage. `handle_conf_change()` is therefore part of the class contract: without it, live config changes would not affect the balancer until reconstruction.

## Dependencies and Integration Points
The header forward-declares `MDSMap`, `MDSRank`, `MHeartbeat`, `CInode`, `CDir`, `Messenger`, `MonClient`, and `Message`, while including `mdstypes.h`, `include/types.h`, `common/ceph_time.h`, CephFS rank types, `common/Clock.h`, and reference-counted pointer support. It exposes APIs in terms of core MDS cache objects (`CInode`, `CDir`, `dirfrag_t`) and Ceph formatting (`Formatter`), so the class sits directly between metadata-operation accounting, directory cache fragmentation, heartbeat messaging, monitor/RADOS-backed balancing policy, and migration.

Friendship with `C_Bal_SendHeartbeat` allows the delayed callback in the implementation to call the private `send_heartbeat()`. The private accessors `get_maxim()` and `get_maxex()` encode the planner's invariant that pending imported/exported amounts must be subtracted from target capacity or excess capacity before assigning more transfers.

## Risks
The public API is pointer-heavy and assumes callers pass live `CDir`/`CInode` objects with correct authority and cache state. Many methods are valid only on the MDS event path where locking and object lifetime are controlled by `MDSRank`/`MDCache`; using them from a different context would risk stale pointers or inconsistent popularity counters.

The header exposes only partial config getters, so tests or callers that need other cached options must inspect behavior rather than state. `is_fragment_pending()` only checks pending sets, not actual `MDCache` split/merge state, so it is a scheduling guard rather than a full fragmentation-state query. `balance_state_t` stores load as `double`, so small threshold comparisons and accumulated floating-point amounts matter to planner decisions.

Because `beat_epoch`, per-rank maps, and overload history are mutable shared balancer state, correctness depends on heartbeat ordering and rank-mask updates in the implementation. The class has no explicit copy/move deletion in the header; practical ownership through `MDSRank` should prevent copying, but accidental copying would be unsafe because it would duplicate raw subsystem pointers and pending state.

## Test Signals
Header-level contract tests should focus on integration behavior: construction with mocked `MDSRank`/`Messenger`/`MonClient`, live config refresh through `handle_conf_change()`, public getters reflecting updated values, pending-fragment checks after queue calls, and admin dump availability. Broader MDS tests should assert that metadata operation call sites feed `hit_inode`/`hit_dir`, cache migration call sites invoke export/import/rename adjustments in the expected order, and failure handling resets coordinator-derived overload state when rank 0 fails.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/mds/MDBalancer.h -->
