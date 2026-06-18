# sources/distributed-fs/moosefs/mfsmaster/matoclserv.h

## Purpose
`matoclserv.h` is the public interface for the MooseFS master client-service module implemented in `matoclserv.c`. It exposes lifecycle, statistics, client-version, chunk-completion, lock-wakeup, cache-invalidation, pending-work, and disconnect controls to the rest of the master process while hiding the private connection and packet queue structures.

## APIs
`matoclserv_stats(uint64_t stats[12])` copies and resets the service's per-interval counters: packets and bytes received/sent, mount-reported read/write byte counts, read/write/fsync operation counts, mount-reported network bytes, and lock operation count. Callers must provide a 12-element array.

`matoclserv_get_min_cl_version(void)` scans registered live clients and returns the smallest negotiated client version, or zero when no registered client is present. Other modules can use this to decide whether all clients support a feature.

`matoclserv_chunk_unlocked(uint64_t chunkid, void *cptr)` and `matoclserv_chunk_status(uint64_t chunkid, uint8_t status)` are callbacks used by chunk management code. They retry or complete client read/write/truncate/create operations that were waiting on chunk lock/busy state or asynchronous chunk status.

`matoclserv_fuse_flock_wake_up(void *veptr, uint32_t msgid, uint8_t status)` and `matoclserv_fuse_posix_lock_wake_up(void *veptr, uint32_t msgid, uint8_t status)` let lock managers send deferred lock results back to the client connection represented by `veptr`.

`matoclserv_fuse_invalidate_chunk_cache(void)` broadcasts chunk-cache invalidation to connected clients that support the packet.

`matoclserv_no_more_pending_jobs(void)` reports whether the service has no pending output packets and no status-wait chunk operations. It is useful during controlled shutdown or master role transitions.

`matoclserv_disconnect_all(void)` marks and disconnects all active client connections.

`matoclserv_close_lsock(void)` closes the listening socket after a fork path without running full service teardown.

`matoclserv_init(void)` initializes configuration, creates the listen socket, and registers the module's poll, reload, keepalive, timeout, and destructor hooks with the master main loop. It returns `0` on success and `-1` on socket/listen setup failure.

## Control Flow And State
The header itself owns no state; it declares entry points into the stateful implementation. The implementation maintains the listen socket, active connection list, packet queues, deferred chunk-operation hash tables, authentication/session data, and counters. Callers interact only through coarse module-level hooks and callback functions.

The callback APIs assume the passed connection pointer (`veptr`) is one originally supplied by `matoclserv.c` to lock subsystems, and the chunk callbacks assume the chunk hash tables still contain matching pending operations. Disconnect cleanup removes pending entries before freeing connections, so external users should not retain these opaque pointers beyond the callback contracts established by the implementation.

## Dependencies And Integration
The header includes only `<inttypes.h>` for fixed-width integer types. It intentionally avoids exposing `matoclserventry` or subsystem-specific structures, reducing compile-time coupling. Consumers are expected to include it from master modules that coordinate chunks, locks, lifecycle, monitoring, and shutdown.

Primary integration points are the chunk subsystem, flock/POSIX lock managers, master main loop, status/statistics reporting code, and shutdown/reload orchestration. The protocol constants and packet formats are not exposed here; they remain internal to the `.c` implementation and `MFSCommunication.h`.

## Risks
The interface exposes raw `void *` connection pointers for lock wakeups and chunk callbacks. This keeps subsystem coupling low but relies on strict lifetime discipline: callbacks must not arrive after `matoclserv_beforedisconnect()` has detached pending lock/chunk state. Any future asynchronous or threaded execution model would need stronger ownership or reference counting.

The 12-slot stats array is positional rather than named, so caller and callee must stay synchronized. Adding counters without a new API or documented enum would be error-prone.

`matoclserv_close_lsock()` is narrower than `matoclserv_term()`; callers must use it only for the intended after-fork listener-close case, not as service shutdown.

## Test Signals
Compile-time tests should verify all consumers include this header without needing private implementation types. Runtime signals include successful master startup through `matoclserv_init()`, clean all-client disconnect through `matoclserv_disconnect_all()`, correct no-pending result after output queues and async chunk waits drain, lock wait wakeups producing client responses, chunk callbacks completing delayed operations, and stats snapshots resetting counters after read.
