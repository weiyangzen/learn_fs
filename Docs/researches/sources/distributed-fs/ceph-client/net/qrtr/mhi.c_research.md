# sources/distributed-fs/ceph-client/net/qrtr/mhi.c

## Purpose
`mhi.c` implements a QRTR endpoint transport over the MHI bus, typically for Qualcomm external modem communication. It converts MHI download buffers into QRTR packets and QRTR outgoing skbs into MHI upload transfers.

## Important APIs, Types, And Functions
The device wrapper is `struct qrtr_mhi_dev`, containing a `qrtr_endpoint`, `mhi_device`, and device pointer. Main callbacks are `qcom_mhi_qrtr_dl_callback()`, `qcom_mhi_qrtr_ul_callback()`, `qcom_mhi_qrtr_send()`, `qcom_mhi_qrtr_queue_dl_buffers()`, `qcom_mhi_qrtr_probe()`, `qcom_mhi_qrtr_remove()`, and suspend/resume helpers.

## Control Flow
Probe allocates driver state, sets endpoint `xmit`, stores drvdata, prepares MHI channels, registers a QRTR endpoint with auto node id, then queues all available downlink buffers. Downlink callback ignores absent state and most failed transactions; `-ENOTCONN` frees reset buffers. Successful transfers call `qrtr_endpoint_post()`, report invalid packets, and recycle the same buffer back to MHI. QRTR transmit linearizes the skb, holds `skb->sk` while queued to MHI, and submits via `mhi_queue_skb()`. Upload completion drops the socket ref and consumes the skb.

Suspend late unprepares transfers unless the controller is already in M3. Resume early prepares channels and refills downlink buffers unless still in M3.

## State And Persistence
State is per-MHI-device and devm-managed. Download buffers are devm allocations recycled through MHI. QRTR endpoint registration owns a `qrtr_node` until remove. Socket refs are temporarily held across asynchronous upload completion.

## Dependencies And Integration Points
The file depends on MHI client driver APIs, QRTR endpoint APIs, skb linearization, DMA direction constants, and PM callbacks. It matches MHI channel `"IPCR"`.

## Risks
Buffer recycling must avoid leaks on queue failures and channel reset. Holding socket refs across MHI upload is necessary for skb ownership accounting; missing release would leak sockets. `skb_linearize()` may fail under memory pressure. Resume must requeue enough buffers to avoid receive starvation.

## Test Signals
Tests should cover probe failure unwind, invalid QRTR packet logging, MHI reset `-ENOTCONN`, upload queue failure, upload completion socket ref release, suspend/resume in M3 and non-M3 states, and remove after partial initialization.
