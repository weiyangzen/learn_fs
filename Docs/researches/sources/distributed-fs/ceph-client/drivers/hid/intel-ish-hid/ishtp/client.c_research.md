# sources/distributed-fs/ceph-client/drivers/hid/intel-ish-hid/ishtp/client.c

## Purpose
`client.c` implements the ISHTP client-session layer. It allocates and links host clients, connects/disconnects them to firmware clients through HBM, manages RX/TX queues and flow-control credits, sends client payloads over IPC or DMA, receives fragmented or DMA-backed responses, and exposes small client accessors for upper ISHTP client drivers.

## Important APIs, types, and functions
Exported lifecycle APIs are `ishtp_cl_allocate()`, `ishtp_cl_free()`, `ishtp_cl_link()`, `ishtp_cl_unlink()`, `ishtp_cl_connect()`, `ishtp_cl_disconnect()`, `ishtp_cl_establish_connection()`, `ishtp_cl_destroy_connection()`, and `ishtp_cl_flush_queues()`. Data path APIs are `ishtp_cl_send()`, `ishtp_cl_read_start()`, `ishtp_cl_send_msg()`, `recv_ishtp_cl_msg()`, and `recv_ishtp_cl_msg_dma()`. Helpers maintain client state, ring sizes, firmware IDs, private data, and the parent `ishtp_device`.

## Control flow and integration points
Connection starts by linking the client into `dev->cl_list`, reserving a host client ID from `host_clients_map`, locating a firmware client by UUID, then sending `CLIENT_CONNECT_REQ_CMD` and waiting on `wait_ctrl_res` until HBM changes the state to connected or disconnected. Non-reset connection allocates RX/TX rings before starting flow control; reset reconnection reuses existing rings and clears counters/ack state.

Transmit flow enqueues copied payloads into `tx_list`, then sends only when the client is connected, the device is enabled, the payload fits the firmware client's `max_msg_length`, a TX ring entry is free, and `ishtp_flow_ctrl_creds` allows progress. `ishtp_cl_send_msg()` selects DMA only when `dev->transfer_path == CL_TX_PATH_DMA`; otherwise IPC fragments the payload by `dev->mtu`. IPC and DMA are ack-gated against each other via `last_ipc_acked`, `last_dma_acked`, `last_tx_path`, and `last_dma_addr` to avoid mixing outstanding paths.

Receive flow is driven by the HBM/IPC bottom half. `recv_ishtp_cl_msg()` validates the ISHTP header, finds the matching read buffer on `dev->read_list`, copies IPC fragments via `dev->ops->ishtp_read()`, and completes the buffer when `msg_complete` is set. `recv_ishtp_cl_msg_dma()` validates the DMA HBM address/length at the HBM layer, copies the DMA payload into the client's read buffer, and treats it as a complete message. Complete buffers move to `in_process_list` and wake the bus client callback with `ishtp_cl_bus_rx_event()`.

## State and persistence behavior
Persistent runtime state is held in `struct ishtp_cl`: host/firmware IDs, connection state, flow-control credits, RX free buffers, in-process RX list, TX queued/free rings, transmit offsets, ack state, send/receive counters, error counters, and FC timing. `client.c` does not persist data across reboot; it preserves allocated rings across firmware reset when `ishtp_cl_establish_connection(..., reset=true)` is used. Shared device state includes `dev->cl_list`, `dev->read_list`, host-client bitmaps, open-handle count, DMA buffers, and hardware operation callbacks.

## Dependencies
This file depends on `hbm.c` for connect/disconnect/flow-control messages, `dma-if.c` for DMA slot allocation/release, client-buffer helpers for ring objects, `bus.c` for firmware client lookup and RX event dispatch, and low-level `ishtp_hw_ops` for reading/writing hardware IPC. It also uses Linux lists, spinlocks, wait queues, DMA/cache helpers, and exported ISHTP client interfaces consumed by HID and firmware-loader client drivers.

## Risks and edge cases
The largest risks are reset races while a caller waits on `wait_ctrl_res`, stale read buffers left on `dev->read_list`, flow-control credit imbalance, lost DMA/IPC ack sequencing, and queue lock ordering across `read_list_spinlock`, `free_list_spinlock`, `tx_list_spinlock`, and `cl_list_lock`. `ishtp_cl_establish_connection()` returns `-ENOENT` if the UUID is missing but does not unlink the just-linked client in that path, so callers must be robust to failed setup cleanup. RX overflow drops the buffer and withholds new FC, potentially wedging a client. DMA sends rely on coherent buffer allocation plus explicit cache flushing when firmware lacks snooping.

## Test signals
Useful tests are connect/disconnect with valid and missing UUIDs, repeated firmware reset/reconnect, concurrent clients targeting the same firmware client, TX ring exhaustion, payloads at and above max message length, IPC fragmentation across `dev->mtu`, DMA fallback when no DMA slot exists, DMA ACK release validation, RX fragmentation, RX overflow, flow-control timing/counter checks, suspend/resume reset paths, module removal queue flushes, and lockdep/KASAN stress during open/close and interrupt-driven RX.
