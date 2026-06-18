## sources/distributed-fs/ceph-client/drivers/media/platform/mediatek/vcodec/decoder/vdec_msg_queue.c

Purpose: implements the LAT-to-core message queue used by MediaTek split decoder architectures. It allocates reusable LAT buffers, tracks UBE transfer-buffer read/write pointers, schedules core decode work, and coordinates flush completion.

Important APIs/types/functions: public functions are `vdec_msg_queue_init_ctx`, `vdec_msg_queue_qbuf`, `vdec_msg_queue_dqbuf`, `vdec_msg_queue_update_ube_rptr`, `vdec_msg_queue_update_ube_wptr`, `vdec_msg_queue_wait_lat_buf_full`, `vdec_msg_queue_deinit`, and `vdec_msg_queue_init`. Static helpers choose list heads, update atomic list counts, wait for LAT buffers, and run `vdec_msg_queue_core_work`.

Control flow: initialization sets up LAT and core queue contexts, allocates a WDMA/UBE buffer sized by resolution, creates three `vdec_lat_buf` objects with error/slice buffers and optional AV1 buffers, allocates codec-private per-buffer data, and enqueues all buffers to LAT availability. LAT backends dequeue from `lat_ctx`, fill a buffer, then queue to `core_ctx`. Core queueing schedules `core_work`; the worker dequeues one core buffer, runs its codec `core_decode` callback under core hardware power/current context, then returns it to LAT availability. Flush inserts an `empty_lat_buf` sentinel and waits for `flush_done`.

State and persistence behavior: queue state lives in `struct vdec_msg_queue` embedded in the decoder context. It persists allocated DMA memory, ready lists, atomic LAT/core counts, WDMA read/write DMA addresses, status flags, and a waitqueue for flush completion. Deinit frees all buffers and cancels pending work if initialized.

Dependencies and integration points: depends on kthread/freezer headers, workqueues, spinlocks, waitqueues, MediaTek decoder power helpers, and codec-specific core callbacks. VP9/AV1 LAT backends use the transfer pointers and private payloads to bridge LAT and core phases.

Risks: queue counters and lists must stay consistent across error paths or LAT buffers can leak from the pool. Core work only processes one buffer per invocation and reschedules based on `core_list_cnt`, so races around `CONTEXT_LIST_QUEUED` matter. Flush waits unbounded after queuing the sentinel. WDMA size is chosen from current `picinfo`, so stale dimensions can undersize large streams. Deinit must not race with active core work or freed private data.

Test signals: run split decode with multiple queued frames, backpressure, flush while core work is active, AV1 allocation path, allocation failures at each buffer, and repeated init/deinit. Trace `lat_list_cnt`, `core_list_cnt`, `ready_num`, `status`, and UBE pointers for stuck or duplicated buffers.
