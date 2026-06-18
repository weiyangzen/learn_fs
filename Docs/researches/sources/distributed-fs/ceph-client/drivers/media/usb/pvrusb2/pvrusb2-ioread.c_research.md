# sources/distributed-fs/ceph-client/drivers/media/usb/pvrusb2/pvrusb2-ioread.c

Purpose: read-side adapter that turns a `pvr2_stream` of USB buffers into a user-copy pull interface with fixed buffer storage, optional stream synchronization-key filtering, availability checks, and start/stop control.

Important APIs, types, and functions: `struct pvr2_ioread` stores the stream, 32 page-aligned 16 KiB buffers, optional sync key, sync state/offset/skip count, enabled/spigot/running flags, current buffer and offsets, and a mutex. Public functions include `pvr2_ioread_create()`, `pvr2_ioread_destroy()`, `pvr2_ioread_setup()`, `pvr2_ioread_get_stream()`, `pvr2_ioread_set_sync_key()`, `pvr2_ioread_set_enabled()`, `pvr2_ioread_avail()`, and `pvr2_ioread_read()`. Internal helpers include `pvr2_ioread_start()`, `pvr2_ioread_stop()`, `pvr2_ioread_get_buffer()`, and `pvr2_ioread_filter()`.

Control flow: creation allocates fixed buffer storage. Setup tears down any previous stream, kills it, sets the stream buffer count to 32, assigns each stream buffer one storage block, and records the stream. Enabling queues every idle buffer and optionally enters sync-search state. Availability rejects disabled streams, searches for the sync key if required, then requires either any ready buffer once running or at least half the buffers ready before first read. Reading calls availability, marks the stream running, copies from the current ready buffer or repeated sync key to userspace, advances offsets, and requeues exhausted buffers.

State and persistence: all state is volatile per reader. Sync state transitions from searching (`1`) to replaying matched key (`2`) to normal (`0`). Stream buffers are recycled continuously until stop. No persistent storage is used.

Dependencies and integration points: depends on `pvrusb2-io` for buffer queueing/status, kernel `copy_to_user()`, page-aligned allocation, and pvrusb2 debug tracing. V4L2/read-style interfaces can use this layer to expose streaming data without knowing URB details.

Risks: sync filtering has subtle boundary accounting; `cp->c_data_offs += idx` adds an absolute index rather than consumed delta, which is worth scrutinizing for nonzero offsets. A bad userspace pointer returns `-EFAULT` after data may already be consumed. `pvr2_ioread_get_buffer()` stops streaming on queue or buffer status errors and reports no buffer, causing read-side `-EIO` or `-EAGAIN`. Availability threshold delays initial delivery until half the buffers fill, trading latency for smoothness.

Test signals: read streaming with and without sync keys; sync key split across buffers; nonblocking/poll paths expecting `-EAGAIN`; user fault injection; repeated enable/disable/setup; disconnect during read; verify every consumed buffer is requeued and no ready-buffer starvation occurs.
