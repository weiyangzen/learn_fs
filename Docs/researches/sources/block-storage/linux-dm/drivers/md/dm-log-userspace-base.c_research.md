# File Research: sources/block-storage/linux-dm/drivers/md/dm-log-userspace-base.c

## Purpose
Implements the DM dirty-log type `userspace`, allowing mirror/replication dirty-log decisions to be delegated to a userspace log server through the userspace-log transfer layer.

## Main Interfaces
- Dirty-log lifecycle: `userspace_ctr()`, `userspace_dtr()`, `userspace_presuspend()`, `userspace_postsuspend()`, `userspace_resume()`.
- Region queries: `userspace_is_clean()`, `userspace_in_sync()`, `userspace_is_remote_recovering()`.
- Region mutation: `userspace_mark_region()`, `userspace_clear_region()`, `userspace_set_region_sync()`.
- Resync/status: `userspace_get_resync_work()`, `userspace_get_sync_count()`, `userspace_status()`.
- Flush handling: `userspace_flush()`, `flush_by_group()`, `flush_one_by_one()`, `do_flush()`.
- Module setup: `userspace_dirty_log_init()`, `userspace_dirty_log_exit()`.

## Control Flow
Construction expects a UUID, optional `integrated_flush`, and userspace-implementation-specific arguments. It builds a constructor string beginning with target length, sends `DM_ULOG_CTR` to userspace, retrieves region size, optionally opens a returned log device, initializes flush-entry mempool state, and creates a delayed flush workqueue when integrated flush is enabled.

Mark and clear operations enqueue flush entries under `flush_lock`. `userspace_flush()` detaches local mark/clear lists, sends clear requests first, then mark requests and a final flush. Requests are grouped up to `MAX_FLUSH_GROUP_COUNT`; failed grouped sends fall back to one-by-one sends. Integrated flush sends mark groups as `DM_ULOG_FLUSH` payloads and delays clear-only flushes.

Most dirty-log operations call `userspace_do_request()`, which retries server communication after `-ESRCH` by periodically attempting a new constructor request and then resume.

## State And Synchronization
`struct log_c` stores the DM target, optional log device, constructor string, region geometry, local unique ID, UUID, mark/clear lists, in-sync hint, optional delayed flush workqueue, integrated-flush flag, and flush-entry mempool. `flush_lock` protects pending mark/clear lists. `sched_flush` tracks whether delayed flush work is pending.

## Integration Points
Registers as a `dm_dirty_log_type`, uses `dm_consult_userspace()` from the transfer layer, opens devices returned by userspace through DM table device management, emits table events on log failures, and participates in target status output.

## Notable Behaviors
- The local unique ID is derived from the `log_c` pointer value.
- `in_sync_hint` is reset on resume and used to reduce remote-recovery traffic once earlier regions are known in sync.
- `userspace_in_sync()` returns `-EWOULDBLOCK` when asked not to block.
- Failed `is_clean`, `in_sync`, and sync-count requests choose conservative results.
- `clear_region` is allowed to fail allocation and skip clearing, causing extra future resync rather than unsafe cleanliness.
- Status info falls back to `COM_FAILURE` on userspace communication failure.

## Risks And Review Focus
- Kernel/userspace protocol failures are treated differently by operation; conservative defaults must match mirror correctness expectations.
- Integrated flush changes ordering and batching semantics, especially delayed clear-only flushes.
- The reconnect loop can block while repeatedly trying to contact userspace.
- Grouped request payload size is bounded by transfer-layer preallocation, so batching constants must stay compatible.
