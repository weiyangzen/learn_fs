# sources/distributed-fs/ceph-client/drivers/md/dm-vdo/dedupe.h

## Purpose
Declares the public interface and core shared structures for dm-vdo dedupe hash zones. It exposes just enough of `dedupe.c` for the VDO data path, target lifecycle, statistics, dump, and message handlers to create hash zones, route writes to the right zone, acquire/release hash locks, manage the UDS index, and tune index timeouts.

## Important APIs, Types, And Data
`struct dedupe_context` contains a `struct uds_request`, zone pointer, list/funnel entries, submission time, requestor `data_vio`, and atomic state. It is embedded in each `hash_zone` as a fixed-size pool of `MAXIMUM_VDO_USER_VIOS` contexts so timed-out UDS requests can remain owned by UDS until their callbacks complete.

`struct hash_zone` is intentionally visible because other VDO code needs fields such as `zone_number`, `thread_id`, and admin/completion state. It contains an `admin_state`, per-zone thread id, `int_map` from record name keys to hash locks, free lock pool, `hash_lock_statistics`, the lock array, available/pending dedupe-context lists, timeout funnel queue, timer, completion, active context count, atomic timer state, and the context pool.

`struct hash_zones` and `struct hash_lock` are opaque outside the interface except where direct zone selection is required. The main data-path functions are `vdo_select_hash_zone()`, `vdo_acquire_hash_lock()`, `vdo_continue_hash_lock()`, `vdo_release_hash_lock()`, `vdo_clean_failed_hash_lock()`, `vdo_share_compressed_write_lock()`, and `vdo_get_duplicate_lock()`.

Lifecycle and admin APIs are `vdo_make_hash_zones()`, `vdo_free_hash_zones()`, `vdo_drain_hash_zones()`, `vdo_resume_hash_zones()`, `vdo_finish_dedupe_index()`, `vdo_start_dedupe_index()`, `vdo_set_dedupe_state_normal()`, `vdo_message_dedupe_index()`, `vdo_get_dedupe_index_state_name()`, and `vdo_dump_hash_zones()`. Statistics and tuning APIs include `vdo_get_dedupe_statistics()`, `vdo_get_dedupe_index_timeout_count()`, `vdo_dedupe_index_timeout_interval`, `vdo_dedupe_index_min_timer_interval`, and their setter functions.

## Control Flow
The header divides integration into three lanes. Construction and destruction happen during VDO load/unload through `vdo_make_hash_zones()`, `vdo_finish_dedupe_index()`, and `vdo_free_hash_zones()`. Administrative state changes happen during target load/resume/suspend and dmsetup messages through the index-state APIs. Write-path operations select a zone from a UDS record name, enter the hash-zone thread, acquire or share a hash lock, and later continue or release it as the `data_vio` completes asynchronous write or dedupe work.

The exported timeout variables are module-wide settings, in milliseconds, used by `dedupe.c` to derive jiffies for timer scheduling. The setters clamp and convert these values before they are consumed by zone timers.

## State And Persistence
The header exposes volatile runtime structures only. The UDS index itself is persistent, but no on-disk format is defined here. `hash_zone` state is per-VDO runtime state and must be drained before suspend or shutdown. The `dedupe_context` pool and timer fields are transient and are meaningful only while the containing VDO is active.

## Dependencies And Integration Points
It includes Linux list/timer APIs, the UDS `indexer.h` request types, and VDO admin-state, constants, statistics, types, and wait-queue definitions. `data-vio` users depend on the lock APIs; `dm-vdo-target.c` depends on lifecycle and dmsetup message entry points; `dump.c` depends on `vdo_dump_hash_zones()`; statistics code depends on `vdo_get_dedupe_statistics()`.

## Risks
Because `struct hash_zone` is not opaque, external code can theoretically depend on internal fields and make future refactoring harder. Callers must obey the threading contract implied by the implementation: lock acquisition, continuation, and release must occur on the appropriate hash-zone thread unless the implementation explicitly launches a callback to another zone. The declared `vdo_get_dedupe_index_timeout_count()` has no matching implementation in the searched dm-vdo sources, which is a stale-API risk if future code calls it.

## Test Signals
Header-level test signals are compile coverage of all users, sparse/lockdep checks for timer/list/admin-state usage where available, and ensuring no unresolved symbol appears for declared APIs. Runtime tests should exercise lifecycle calls in the target load/resume/suspend paths and data-path lock calls under concurrent writes.
