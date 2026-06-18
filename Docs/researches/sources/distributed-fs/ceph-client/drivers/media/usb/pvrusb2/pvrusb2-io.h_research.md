# sources/distributed-fs/ceph-client/drivers/media/usb/pvrusb2/pvrusb2-io.h

Purpose: public interface for pvrusb2 USB stream and buffer management. It hides stream internals while exposing buffer states, statistics, callbacks, lifecycle, queueing, and ready/idle buffer access.

Important APIs, types, and functions: declares `pvr2_stream_callback`, `enum pvr2_buffer_state`, opaque `struct pvr2_stream` and `struct pvr2_buffer`, and `struct pvr2_stream_stats`. Stream APIs create/destroy/setup streams, set callbacks, get/reset stats, configure buffer counts, get idle/ready/specific buffers, count ready buffers, and kill queued/ready data. Buffer APIs set external storage, read ready byte count/status/ID, and queue a buffer for USB filling.

Control flow: users create a stream, bind it to a USB endpoint, allocate a chosen number of buffers, attach storage to idle buffers, queue buffers, consume ready buffers, then requeue or kill them during stop/teardown. The callback signals transitions to ready data but does not itself transfer data.

State and persistence: the header exposes only counters and state enum values. Stream and buffer internals remain private to `pvrusb2-io.c`.

Dependencies and integration points: includes Linux USB and list declarations. Used by `pvrusb2-hdw.h` for stream handles and by `pvrusb2-ioread.h/.c` to build a user-readable streaming path.

Risks: callers must not manipulate buffers outside expected idle/queued/ready transitions. Storage passed to `pvr2_buffer_set_buffer()` must outlive queued URBs. `pvr2_stream_get_ready_buffer()` and `pvr2_stream_get_idle_buffer()` return raw pointers whose state can change in completion context if caller locking is not aligned with the implementation.

Test signals: compile all stream users; validate queue/read/requeue loops; inspect stats through hardware reports; disconnect and destroy without leaked URBs or buffers.
