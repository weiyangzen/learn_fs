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
