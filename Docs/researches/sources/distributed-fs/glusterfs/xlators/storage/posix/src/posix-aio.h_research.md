# Research: sources/distributed-fs/glusterfs/xlators/storage/posix/src/posix-aio.h

Purpose:
This header declares the POSIX storage translator's AIO toggle API, queue sizing constants, and synchronous read/write prototypes needed by the AIO implementation.

Important APIs, types, and functions:
- `POSIX_AIO_MAX_NR_EVENTS` is 256 and bounds concurrently submitted AIO events.
- `POSIX_AIO_MAX_NR_GETEVENTS` is 16 and bounds completions reaped per `io_getevents()` call.
- `posix_aio_on()` enables async read/write/fsync replacement when available.
- `posix_aio_off()` restores synchronous behavior.
- `posix_readv()` and `posix_writev()` are declared for fallback restoration.

Control flow and integration:
`posix-aio.c` uses the constants for `io_setup()` capacity and completion batching. POSIX translator configuration calls `posix_aio_on()` or `posix_aio_off()` to mutate `this->fops`.

State and persistence behavior:
No state is stored here. The constants shape runtime queue depth and completion batching.

Dependencies:
The declarations require Gluster types such as `xlator_t`, `call_frame_t`, `fd_t`, `dict_t`, and `struct iobref` from surrounding POSIX/Gluster headers. `posix_fsync()` is restored by the implementation but declared elsewhere.

Risks and edge cases:
The queue depth is fixed at compile time. High concurrency can exceed 256 submissions. Prototype drift for synchronous FOPs can break fallback restoration.

Test signals:
Compile with libaio and without libaio. Runtime tests should confirm FOP pointer swapping and queue-depth behavior under concurrency.
