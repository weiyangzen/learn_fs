# sources/distributed-fs/ceph-client/drivers/media/platform/st/sti/delta/delta-ipc.c

Purpose: implements Delta host-to-firmware IPC over rpmsg. It opens/closes firmware decoder instances and sends synchronous set-stream/decode commands using a DMA shared command buffer.

Important APIs and functions: exported APIs are `delta_ipc_init`, `delta_ipc_exit`, `delta_ipc_open`, `delta_ipc_set_stream`, `delta_ipc_decode`, and `delta_ipc_close`. Internal pieces define rpmsg message structures, command IDs, sanity tag validation, DMA virtual-to-physical translation, data range validation, callback completion, and rpmsg probe/remove binding.

Control flow: `delta_ipc_init` registers an rpmsg driver for `"rpmsg-delta"`. Probe stores the rpmsg device in `delta_dev`. `delta_ipc_open` validates parameters, allocates a write-combined DMA buffer through `hw_alloc`, copies open parameters into it, sends `DELTA_IPC_OPEN`, waits up to 100 ms for completion, stores the firmware handle, and returns the shared buffer and host handle. Set-stream and decode require parameter/status data to live inside that shared buffer, translate those pointers to physical addresses, send rpmsg commands, wait for the callback, and map firmware errors to `-EIO`. Close frees the IPC buffer, sends `DELTA_IPC_CLOSE`, and waits for acknowledgement.

State and persistence: each `delta_ctx` embeds a `delta_ipc_ctx` with callback error, firmware handle, completion, and shared buffer metadata. `delta_dev` stores the currently bound rpmsg device. No persistent storage exists; firmware-side state is represented by `copro_hdl`.

Dependencies and integration points: depends on rpmsg, DMA allocation from `delta-mem.c`, `delta_ctx` counters, and MJPEG decoder code that fills firmware-specific command structures.

Risks: command completion is single-flight per context and assumes firmware always echoes the host handle and sanity tag correctly. `delta_ipc_open` references `ctx->ipc_buf->size` in an error message before `ctx->ipc_buf` is assigned, which could fault if `param->size > ipc_buf_size`. The callback length error message swaps received length/source values. All timeouts are fixed at 100 ms, which may be tight under firmware stalls. Closing frees the shared buffer before sending the close command, so firmware close must not need command data beyond the header.

Test signals: rpmsg endpoint bind/unbind, timeout injection, malformed callback tag/host handle tests, MJPEG decode under load, and error-path checks for DMA buffer leaks and `sys_errors` counters.
