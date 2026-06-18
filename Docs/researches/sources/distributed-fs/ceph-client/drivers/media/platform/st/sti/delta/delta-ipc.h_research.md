# sources/distributed-fs/ceph-client/drivers/media/platform/st/sti/delta/delta-ipc.h

Purpose: declares the Delta IPC API and documents the shared-buffer contract between codec code and the rpmsg transport.

Important APIs and functions: exposes initialization/exit functions plus `delta_ipc_open`, `delta_ipc_set_stream`, `delta_ipc_decode`, and `delta_ipc_close`. The comments define `struct delta_ipc_param` expectations: command parameter and status pointers must be virtual addresses inside the allocated IPC shared buffer for set-stream and decode.

Control flow: a decoder calls open with initial parameters and desired shared buffer size, receives a buffer and handle, writes later command structures into that buffer, uses set-stream/decode synchronously, then calls close during teardown.

State and persistence: no header-owned state. The API mutates `delta_ctx->ipc_ctx`, firmware instance state, and DMA buffer ownership in the implementation.

Dependencies and integration points: requires `struct delta_dev`, `struct delta_ctx`, `struct delta_buf`, and `struct delta_ipc_param` definitions from `delta.h`. It is consumed by MJPEG decoder code and initialized by `delta-v4l2.c`.

Risks: the API is synchronous and only supports one pending command per context. Passing stack or unrelated heap data to set-stream/decode violates the documented address-range requirement and will be rejected. The close function returns void, so close errors are only logged/counted.

Test signals: compile coverage, open/decode/close sequencing with a live firmware endpoint, and range-validation tests that deliberately pass command data outside the IPC buffer.
