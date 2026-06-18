# sources/distributed-fs/ceph-client/drivers/hid/intel-ish-hid/ishtp/hbm.c

## Purpose
`hbm.c` implements ISHTP Host Bus Message protocol handling. It starts protocol negotiation, enumerates firmware clients, fetches client properties, handles client connect/disconnect/flow-control messages, enables ISHTP-over-DMA, dispatches DMA transfers and ACKs, handles fixed system/loader clients, and sends suspend/resume system-state notifications.

## Important APIs, types, and functions
Startup APIs include `ishtp_hbm_start_req()`, `ishtp_hbm_start_wait()`, and `ishtp_hbm_enum_clients_req()`. Client-control APIs include `ishtp_hbm_cl_connect_req()`, `ishtp_hbm_cl_disconnect_req()`, and `ishtp_hbm_cl_flow_control_req()`. Dispatch entry points are `recv_hbm()`, `bh_hbm_work_fn()`, `ishtp_hbm_dispatch()`, and `recv_fixed_cl_msg()`. Power/system helpers are `ishtp_query_subscribers()`, `ishtp_send_suspend()`, and `ishtp_send_resume()`.

## Control flow and integration points
The normal HBM boot sequence sends `HOST_START_REQ_CMD`, waits for `HOST_START_RES_CMD`, sends `HOST_ENUM_REQ_CMD`, copies the valid firmware-client bitmap from `HOST_ENUM_RES_CMD`, allocates `dev->fw_clients`, requests properties for each set bit, and finally moves `hbm_state` to `ISHTP_HBM_WORKING` and `dev_state` to `ISHTP_DEV_ENABLED` before creating bus devices with `ishtp_bus_new_client()`.

`recv_hbm()` reads a bus message from hardware. Flow-control is handled immediately so waiting TX queues can resume. Connect/disconnect responses, firmware disconnect requests, and inbound DMA transfers are also dispatched in-order. Other HBM messages are copied into a fixed-size FIFO and processed by `bh_hbm_work_fn()` on the unbound workqueue.

DMA setup happens after all client properties have been fetched and `ishtp_use_dma_transfer()` allows it. The driver allocates RX/TX DMA buffers, notifies firmware of the RX buffer with `DMA_BUFFER_ALLOC_NOTIFY`, marks DMA enabled on `DMA_BUFFER_ALLOC_RESPONSE`, copies inbound DMA data through `recv_ishtp_cl_msg_dma()`, and returns `DMA_XFER_ACK`. Outbound ACKs release TX slots and may trigger the next queued client message.

## State and persistence behavior
The file drives `dev->hbm_state`, `dev->dev_state`, firmware client arrays/bitmaps/indexes, DMA-enabled state, read-message FIFO cursors, loader response flags, and static system-state bitfields. State is volatile and reset-oriented; failures often set `ISHTP_DEV_RESETTING` and call `ish_hw_reset()`.

## Dependencies
It depends on `ishtp_write_message()`, hardware read callbacks, bus client creation, ISHTP client queues, DMA buffer helpers, loader work, and Linux workqueues/waitqueues/spinlocks. It also consumes protocol definitions from `hbm.h` and loader constants from `loader.h`.

## Risks and edge cases
HBM state-machine ordering is strict; unexpected responses trigger hardware reset. The bottom-half FIFO can overflow and drop HBMs. Several routines call `ishtp_write_message()` while holding list locks or flow-control locks, so hardware write latency and lock ordering are important. DMA ACK handling walks `dev->cl_list` without taking `cl_list_lock`, which is a concurrency-sensitive area. Flow-control uses a single outstanding outbound FC credit and can wedge traffic if a receive buffer cannot be replenished. Static system-state variables are global rather than per device.

## Test signals
Probe boot through start/enum/property states, unsupported HBM version handling, malformed property response address/status, FIFO overflow injection, connect/disconnect response wakeups, firmware-initiated disconnect, FC duplicate detection, DMA notify/response, DMA XFER and ACK range validation, loader-client responses, system-state subscribe/suspend/resume messages, reset on unexpected HBM, and lockdep during client removal while DMA ACKs arrive.
