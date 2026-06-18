# sources/distributed-fs/glusterfs/xlators/storage/posix/src/posix-io-uring.h

## Purpose

This header declares the public switch points for enabling and disabling the POSIX io_uring backend and, when liburing is available, exposes the normal `posix_readv` and `posix_writev` symbols needed to restore synchronous fops.

## Important APIs, Types, and Functions

`POSIX_URING_MAX_ENTRIES` sets the queue depth to 512. `posix_io_uring_on(xlator_t *this)` attempts initialization and fop-table replacement. `posix_io_uring_off(xlator_t *this)` restores synchronous fops and tears down io_uring state when active. Under `HAVE_LIBURING`, the header also declares the synchronous `posix_readv` and `posix_writev` prototypes used by `posix_io_uring_off`.

## Control Flow

The header is consumed by translator initialization/reconfiguration logic. Runtime code calls `posix_io_uring_on` when the option is enabled and `posix_io_uring_off` when disabled or during cleanup.

## State and Persistence Behavior

The header persists nothing. Its constants and declarations gate runtime in-memory queue state created in `posix-io-uring.c`.

## Dependencies and Integration Points

It depends on Gluster types such as `xlator_t`, `call_frame_t`, `fd_t`, `dict_t`, `iobref`, and `struct iovec` through included translation-unit context. It integrates with `posix.c` fop registration and `posix_private` io_uring fields.

## Risks

The conditional prototypes mean compile coverage must include both liburing and non-liburing builds. Queue depth is fixed here, so workloads with high concurrency can hit SQE exhaustion unless the implementation grows retry/backpressure behavior.

## Test Signals

Compile with and without `HAVE_LIBURING`, verify fop restore uses synchronous symbols, and validate queue-depth behavior around 512 submitted operations.
