# sources/distributed-fs/glusterfs/libglusterfs/src/gf-io-legacy.c

## Purpose
`gf-io-legacy.c` provides the legacy implementation of the `gf_io_engine_t` interface. It bridges the newer I/O framework to existing GlusterFS event and timer infrastructure when `io_uring` is unavailable or not selected.

## Important APIs, Types, and Functions
- `gf_io_engine_legacy`: exported engine descriptor with name `legacy` and mode `GF_IO_MODE_LEGACY`.
- `gf_io_legacy_setup()`, `gf_io_legacy_cleanup()`: initialize/reset legacy sequence state and no-op cleanup.
- `gf_io_legacy_wait()`: delegates to `gf_event_dispatch(global_ctx->event_pool)`.
- `gf_io_legacy_cancel()`: cancels timer-backed operations or reports missing/already completed timers.
- `gf_io_legacy_callback()`: immediately completes a callback operation.

## Control Flow
Setup resets a static sequence counter. Wait dispatches the global event loop. Legacy callbacks increment `gf_io_legacy_seq` atomically and call `gf_io_cbk(NULL, seq, id, res)`. Cancel interprets `op->cancel.id` as a `gf_timer_t *`; absent timers complete cancel with `-ENOENT`, failed timer cancellation completes cancel with `-EALREADY`, and successful cancellation completes the original operation with `-ECANCELED` and the cancel request with `0`.

## State and Persistence
The only local state is static `gf_io_legacy_seq`, used to provide callback sequence values. Event and timer state lives in `global_ctx`.

## Dependencies and Integration Points
Depends on `gf-io-legacy.h`, global context, `gf-event.h`, and `timer.h`. It integrates new `gf_io` callback/cancel abstractions with the older event loop.

## Risks and Edge Cases
- Cancellation assumes timer IDs are stored as pointer-sized integers.
- `worker_*` hooks are NULL because this engine has no worker threads; callers must handle legacy mode correctly.
- Global event dispatch remains the blocking wait path until event code migrates to the I/O framework.

## Test Signals
Exercise callback immediate completion, timer cancel success and failure, null timer IDs, sequence monotonicity under concurrent callbacks, and full `gf_io_run("legacy", ...)` behavior with setup/cleanup handlers.
