# Research: sources/distributed-fs/glusterfs/xlators/storage/posix/src/posix-aio.c

Purpose:
This file implements the POSIX storage translator's Linux native AIO backend when `HAVE_LIBAIO` is available, and fallback stubs when it is not. When enabled, `posix_aio_on()` replaces `readv`, `writev`, and `fsync` FOPs with asynchronous implementations backed by `io_submit()` and a completion thread using `io_getevents()`.

Important APIs, types, and functions:
- `__posix_fd_set_odirect()` toggles `O_DIRECT` on the underlying fd based on open flags and alignment hints.
- `struct posix_aio_cb` wraps one async request, including kernel `iocb`, call frame, iobuf/iobref, prebuf, raw fd, Gluster fd ref, op type, and offset.
- `posix_aio_readv()`, `posix_aio_writev()`, and `posix_aio_fsync()` validate inputs, prepare iocbs, submit work, and unwind synchronously on setup failure.
- Completion functions stat post-operation state, update counters, unwind the original stack, and free the callback.
- `posix_aio_thread()` reaps events and dispatches completions.
- `posix_aio_init()` creates the AIO context and completion thread.
- `posix_aio_on()` lazily initializes and swaps FOP pointers; `posix_aio_off()` restores synchronous functions.

Control flow:
After `posix_aio_on()`, read/write/fsync calls allocate a `posix_aio_cb`, prepare one kernel request, optionally update direct-IO fd flags under `fd->lock`, and submit with `io_submit()`. The completion thread blocks in `io_getevents()`, dispatches by operation type, and each completion unwinds the saved frame.

State and persistence behavior:
Long-lived AIO state lives in `struct posix_private` (`ctxp`, thread, capability flags, counters, alignment data). Per-request state lives in `posix_aio_cb`. The implementation mutates kernel fd `O_DIRECT` state and tracks that in `pfd->odirect`. It performs requested file IO but defines no separate persistent format.

Dependencies and integration points:
Enabled builds depend on `<libaio.h>`, POSIX fd helpers, iobuf/iobref APIs, Gluster unwind macros, disk-space checks, `posix_fdstat()`, `posix_fd_ctx_get()`, `struct posix_private`, atomic counters, and synchronous fallback functions. The makefile links `$(LIBAIO)` when configured.

Risks and edge cases:
Linux AIO error conventions vary between `-errno` returns and `-1` plus `errno`; mappings need care. `O_DIRECT` toggling on a shared fd relies on `fd->lock`. The completion thread exits on hard `io_getevents()` failure and has no restart path here. Disabling AIO restores FOP pointers but does not cancel in-flight operations or destroy the AIO context. EOF is signaled by setting `op_errno = ENOENT` on reads, which is a protocol convention upper layers must preserve.

Test signals:
Cover libaio/no-libaio builds, runtime ENOSYS fallback, success and failure for read/write/fsync, direct-IO aligned/unaligned paths, concurrent operations on one fd, write disk-space failures, counter increments, EOF signaling, and completion thread EINTR/hard-error behavior.
