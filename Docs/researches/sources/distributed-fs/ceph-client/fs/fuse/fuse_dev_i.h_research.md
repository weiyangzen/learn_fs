# sources/distributed-fs/ceph-client/fs/fuse/fuse_dev_i.h

## Purpose
`fuse_dev_i.h` is the internal interface between FUSE core code and the device/request-copy implementation. It defines request ID bit conventions, copy-state bookkeeping for moving request payloads between kernel buffers, userspace iovecs, pipes, and io_uring, and inline accessors for safely recovering the `fuse_dev` and `fuse_conn` behind a `/dev/fuse` file.

## Important APIs, Types, And Functions
`FUSE_INT_REQ_BIT` marks interrupt-request IDs as odd while ordinary requests use even IDs stepped by `FUSE_REQ_ID_STEP`. `struct fuse_copy_state` tracks the request being copied, the active `iov_iter`, pipe buffers, current page, length, offset, direction (`write`), folio moving, io_uring mode, and ring copied size. `FUSE_DEV_FC_DISCONNECTED` is a sentinel stored in `fud->fc` after `/dev/fuse` is closed.

The inline helpers are `fuse_dev_fc_get()`, `fuse_file_to_fud()`, and `__fuse_get_dev()`. Function declarations expose the request and copy operations implemented elsewhere: `fuse_get_dev()`, `fuse_req_hash()`, `fuse_request_find()`, `fuse_dev_end_requests()`, `fuse_copy_init()`, `fuse_copy_finish()`, `fuse_copy_args()`, `fuse_copy_out_args()`, `fuse_dev_queue_forget()`, `fuse_dev_queue_interrupt()`, `fuse_remove_pending_req()`, and `fuse_request_expired()`.

## Control Flow
Callers that operate on a FUSE device file fetch `struct fuse_dev *` from `file->private_data`, then use `fuse_dev_fc_get()` to acquire-load the connection pointer. `__fuse_get_dev()` returns `NULL` if the device has not been installed on a connection, otherwise returns the device. The explicit comment identifies exceptions where the disconnected sentinel matters: `fuse_dev_put()` and `fuse_fill_super_common()` must distinguish an installed live connection from a released device.

Copy operations are declared around `struct fuse_copy_state`: initialize the copy direction and iterator, copy input/output args, finish pipe/vmap/user state, and queue protocol side requests such as forgets or interrupts into the input queue.

## State And Persistence Behavior
The header itself owns no storage except external `fuse_dev_waitq`. Its key persistent contract is the lifetime and memory-ordering model for `fud->fc`: assigned once during mount, valid until file release, then exchanged to `FUSE_DEV_FC_DISCONNECTED`. The acquire load pairs with installation/release stores so request-device users do not dereference a partially installed connection.

## Dependencies And Integration Points
This header depends on `linux/types.h` and forward declarations from `fuse_i.h`. It is included by device code and `inode.c`; `inode.c` uses the sentinel and helpers while installing or putting a `fuse_dev`. Request-copy functions integrate with the FUSE request queues, `/dev/fuse` read/write paths, pipe splice support, and io_uring support.

## Risks And Edge Cases
The most important risk is treating `FUSE_DEV_FC_DISCONNECTED` as a valid connection or assuming lockless access is safe in the documented exceptions. Incorrect request ID parity would break interrupt matching. Copy state is security-sensitive because it moves protocol payloads across kernel/userspace boundaries; wrong length, offset, page pin, or pipe handling can corrupt replies or leak data.

## Test Signals
Useful tests include mount/device install races, `/dev/fuse` close while requests are pending, interrupt request ID matching, forget and interrupt queueing, splice read/write copy paths, io_uring copy accounting, and ensuring callers reject uninstalled or disconnected devices without dereferencing the sentinel.
