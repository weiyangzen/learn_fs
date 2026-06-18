# sources/distributed-fs/ceph-client/drivers/thunderbolt/ctl.c

## Purpose

`ctl.c` implements the Thunderbolt control channel and the common configuration read/write/reset command helpers. It owns ring allocation, DMA-backed control-frame buffers, CRC conversion, outstanding request matching, synchronous and asynchronous request completion, hotplug/event dispatch, and error translation from Thunderbolt configuration errors to Linux errnos.

## Important APIs, Types, and Functions

The central private type is `struct tb_ctl`, which holds the NHI pointer, TX/RX rings, a DMA pool for frames, preposted RX packets, the outstanding request queue, default timeout, domain index, and the event callback installed by the domain. The public lifecycle APIs are `tb_ctl_alloc()`, `tb_ctl_start()`, `tb_ctl_stop()`, and `tb_ctl_free()`.

`tb_cfg_request_alloc/get/put()`, `tb_cfg_request()`, `tb_cfg_request_cancel()`, and `tb_cfg_request_sync()` manage refcounted `struct tb_cfg_request` objects. Standard command helpers include `tb_cfg_ack_notification()`, `tb_cfg_ack_plug()`, `tb_cfg_reset()`, `tb_cfg_read_raw()`, `tb_cfg_write_raw()`, `tb_cfg_read()`, `tb_cfg_write()`, and `tb_cfg_get_upstream_port()`.

Internal helpers such as `check_header()`, `check_config_address()`, `decode_error()`, `parse_header()`, `tb_cfg_print_error()`, `tb_ctl_tx()`, `tb_ctl_rx_callback()`, `tb_cfg_match()`, and `tb_cfg_copy()` provide packet validation, CRC handling, route/sequence matching, and result decoding.

## Control Flow

Allocation creates a coherent frame pool, a TX ring on control HopID 0, an RX ring with a small pool of preallocated receive packets, and initializes the request list. Starting the channel starts TX first, then RX, submits all RX packets, and marks the control channel running. Stopping clears `running`, stops RX/TX rings, warns if requests are still queued, and reinitializes the queue.

Transmit flow allocates a `ctl_pkg`, copies host-endian dwords to big endian, appends a CRC32C-derived checksum, assigns SOF/EOF to the package type, and queues the frame. The TX completion callback frees the package and DMA buffer.

Receive flow validates frame size, strips and verifies the checksum for normal packet classes, converts data to CPU endian, dispatches async errors and event/XDomain/ICM notifications to the domain callback, then tries to match the packet against active requests. A matching request copies the response, schedules completion work, and is later dequeued and refcount-released from `tb_cfg_request_work()`.

Synchronous requests queue an async request and wait on a completion. Timeout calls `tb_cfg_request_cancel()`, schedules the work item, waits until the request is inactive, stores the timeout error, then flushes the work before returning.

## State and Persistence Behavior

The file maintains volatile in-kernel state only. `struct tb_ctl` persists for the domain lifetime and owns rings, DMA pool, RX packet buffers, and outstanding request list. `struct tb_cfg_request` persists until its kref reaches zero; while queued it stores a back pointer to the control channel, request/response buffers, matching callbacks, and completion result.

No filesystem state is persisted. Hardware-visible side effects are real Thunderbolt control-channel operations: configuration reads and writes, reset packets, and event acknowledgments. Retried reads/writes use sequence values `0..3` and short sleeps between timeouts to avoid stale replies colliding with a new attempt.

## Dependencies and Integration Points

The file depends on NHI ring APIs (`tb_ring_alloc_*`, `tb_ring_start/stop/free`, `tb_ring_tx/rx`), DMA pools, workqueues, wait queues, mutexes, CRC32C, endian conversion helpers, Thunderbolt message structures from `tb_msgs.h`, and tracepoints from `trace.h`.

It is the transport used by higher-level switch, port, ICM, DMA-port, and domain code. Domain callbacks receive events through the `event_cb` function pointer. Config helpers are consumed throughout the Thunderbolt driver through `tb_sw_read/write()`, `tb_port_read/write()`, and lower-level safe-mode access paths.

## Risks and Edge Cases

The request cancellation path deliberately schedules the request work even if RX completion races with timeout. Correctness depends on the active flag, cancel flag, and kref serialization around request lookup. `tb_ctl_stop()` only warns about dangling requests and reinitializes the queue; callers must stop after outstanding work is drained or canceled.

`tb_cfg_match()` treats any error packet as a match. This ensures errors complete requests, but an unrelated asynchronous error must be filtered earlier by `tb_async_error()`. Unknown error packets may still terminate the first active request.

Raw read/write response sizes are derived from `length`; callers must respect maximum control packet payload size. `tb_ctl_tx()` rejects frames larger than `TB_FRAME_SIZE - 4`, but raw helper stack objects assume the message structs are large enough for the requested data.

`tb_ctl_start()` sets `running = true` after submitting RX frames without holding `request_queue_lock`. Enqueue checks are locked, but lifecycle callers rely on domain-level locking to serialize start/stop with request issuance.

## Test Signals

Useful tests include config read/write success, Thunderbolt error response mapping, timeout and retry behavior, stale reply after timeout, async event delivery, checksum mismatch drops, invalid frame size drops, stop during in-flight request, and request cancel races. Fault injection should cover DMA pool allocation failure, ring allocation failure, `tb_ring_tx()` failure, callback-initiated traffic, and suspended/runtime-resumed domain transitions.
