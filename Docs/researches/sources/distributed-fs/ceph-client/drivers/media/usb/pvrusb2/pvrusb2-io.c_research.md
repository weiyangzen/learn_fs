# sources/distributed-fs/ceph-client/drivers/media/usb/pvrusb2/pvrusb2-io.c

Purpose: reusable USB bulk-stream buffer manager for pvrusb2. It owns buffer allocation, idle/queued/ready list transitions, URB submission/completion, error tolerance accounting, callbacks, and stream statistics.

Important APIs, types, and functions: private `struct pvr2_stream` tracks queued, ready, and idle lists plus counts/bytes, buffer array sizing, callback, USB device/endpoint, locks, tolerance counters, and processed byte/error totals. Private `struct pvr2_buffer` wraps an ID, state, client storage pointer, used/max counts, status, stream pointer, list node, and URB. Public functions include `pvr2_stream_create()`, `pvr2_stream_destroy()`, `pvr2_stream_setup()`, `pvr2_stream_set_callback()`, `pvr2_stream_get_stats()`, buffer-count getters/setters, idle/ready/buffer lookup, `pvr2_stream_kill()`, `pvr2_buffer_set_buffer()`, `pvr2_buffer_queue()`, and buffer accessors.

Control flow: stream setup flushes queued work and binds a USB device/endpoint/tolerance. Buffer-count changes allocate or free `struct pvr2_buffer` objects and URBs, keeping newly available buffers on the idle list. `pvr2_buffer_queue()` kills any pending URB for that buffer, moves it to queued, fills a bulk receive URB with caller-owned storage, and submits it. `buffer_complete()` records status and bytes, tolerates a configurable number of nonfatal failures, moves the buffer to ready, and invokes the callback when data arrives. `pvr2_stream_kill()` cancels queued URBs, moves ready buffers back idle, and resizes toward target.

State and persistence: all state is volatile in `struct pvr2_stream` and buffers. Statistics persist until reset through `pvr2_stream_get_stats(..., zero_counts=1)`. Client data storage is supplied by higher layers and only referenced here.

Dependencies and integration points: uses Linux USB bulk URBs, spinlocks for list state in completion context, a mutex for structural changes, and pvrusb2 debug tracing. `pvrusb2-hdw.c` creates and configures the video stream, while `pvrusb2-ioread.c` provides storage and user-read semantics on top.

Risks: `pvr2_buffer_queue()` does not propagate `usb_submit_urb()` failure into `ret`, so failed submissions may only surface later through status/list behavior. List getters are mostly unlocked and rely on caller discipline. Error tolerance can hide intermittent transfer failures. Buffer storage must remain valid while queued. Shrinking the buffer pool only frees trailing idle buffers, so target count may not be reached until active buffers return.

Test signals: repeated set-buffer-count and start/stop streaming; USB disconnect while URBs are queued; forced transfer errors with tolerance set to 0 and nonzero values; stats consistency; lockdep/KASAN on queue/kill/race paths; verify callback wakes readers only when ready data appears.
