# sources/distributed-fs/glusterfs/xlators/features/leases/src/leases.c

## Purpose
Implements the public fop surface and lifecycle for the leases translator. It intercepts lease requests and selected file/data/metadata operations, checks them against active leases, blocks or fails conflicting operations, and forwards allowed operations to the child translator.

## Important APIs, Types, and Functions
- `leases_lease()` is the fop for explicit lease get/set/unlock requests and delegates to `process_lease_req()`.
- `leases_open()`, `leases_readv()`, `leases_writev()`, `leases_lk()`, `leases_truncate()`, `leases_setattr()`, `leases_rename()`, `leases_unlink()`, `leases_link()`, `leases_create()`, `leases_fsync()`, `leases_ftruncate()`, `leases_fsetattr()`, `leases_fallocate()`, `leases_discard()`, `leases_zerofill()`, and `leases_flush()` wrap normal fops with lease conflict checks.
- `leases_init_priv()`, `init()`, `reconfigure()`, and `fini()` manage options, timer wheel, recall thread, and private state.
- `leases_release()` frees fd ctx; `leases_clnt_disconnect_cbk()` triggers client cleanup.

## Control Flow
Most fop wrappers follow the same pattern: skip checks when leases are disabled or the operation is internal, extract `"lease-id"` from xdata, compute data-modifying and blocking flags, call `check_lease_conflict()`, then either unwind error, queue a stub with `LEASE_BLOCK_FOP`, or wind the fop to the child. `leases_open()` also creates fd ctx containing client UID and lease ID so later conflict checks can distinguish same-lease opens. `leases_flush()` clears fd ctx as a workaround for release not always arriving after close.

`init()` reads `leases` and `lease-lock-recall-timeout`, initializes lists and mutexes, and starts timer support only when enabled. `reconfigure()` currently only updates recall timeout; enabling/disabling leases dynamically is explicitly not supported. `fini()` stops the recall cleanup thread and releases the timer wheel reference.

## State and Persistence
The file owns translator-private runtime setup and fd ctx lifetime. Lease state itself remains in memory through helpers in `leases-internal.c`; no persistent disk data is written.

## Dependencies and Integration Points
Depends on `leases.h` macros for flag calculation, internal fop bypass, and blocking-stub creation. Integrates with GlusterFS xlator fops/cbks, timer wheel context, client disconnect callbacks, and volume options introduced in op-version 3.8.0.

## Risks and Edge Cases
The wrappers are repetitive, so drift in one fop’s flag calculation can change semantics. `leases_create()` checks `fd->inode`, which may be sensitive during create setup. `leases_flush()` unwinds with the `create` signature on error, likely a bug. Dynamic disable is not supported, so operators changing options must understand existing leases are not recalled. `pthread_cond_broadcast()` is used in `fini()` without an explicit cond init in this file.

## Test Signals
Run lease-enabled and lease-disabled fop tests, conflict tests for all wrapped data-modifying fops, blocking vs nonblocking behavior, lease request get/set/unlock responses, fd ctx setup/release/flush cleanup, client disconnect cleanup, and reconfigure of recall timeout.
