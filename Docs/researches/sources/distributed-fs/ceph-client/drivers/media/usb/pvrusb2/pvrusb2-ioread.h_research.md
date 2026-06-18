# sources/distributed-fs/ceph-client/drivers/media/usb/pvrusb2/pvrusb2-ioread.h

Purpose: public header for the pvrusb2 read adapter layered over `pvr2_stream`. It exposes a compact API for setup, synchronization, enablement, availability, and userspace reads.

Important APIs, types, and functions: declares opaque `struct pvr2_ioread`; lifecycle functions `pvr2_ioread_create()` and `pvr2_ioread_destroy()`; `pvr2_ioread_setup()` to bind a stream; `pvr2_ioread_get_stream()` to retrieve it; `pvr2_ioread_set_sync_key()` for MPEG or stream alignment; `pvr2_ioread_set_enabled()` to start/stop queueing; `pvr2_ioread_read()` for `copy_to_user()` reads; and `pvr2_ioread_avail()` for readiness checks.

Control flow: clients create a reader, bind it to a stream from hardware, optionally set a sync key, enable it when capture starts, call avail/read from file operations, and disable/destroy it during close or teardown.

State and persistence: the header hides all state. Runtime storage and current buffer offsets are owned by `pvrusb2-ioread.c`.

Dependencies and integration points: includes `pvrusb2-io.h` so callers can work with the underlying stream handle. It is intended for V4L2 read interfaces or similar code paths that need byte-stream access.

Risks: callers must coordinate hardware streaming state with reader enablement. Reads return kernel error codes (`-EIO`, `-EAGAIN`, `-EFAULT`) that user-facing file operations must propagate correctly. The `void __user *` contract requires use only from user-copy contexts.

Test signals: compile users; bind/unbind against a live `pvr2_stream`; check read readiness behavior in blocking and nonblocking modes; validate cleanup when stream setup fails.
