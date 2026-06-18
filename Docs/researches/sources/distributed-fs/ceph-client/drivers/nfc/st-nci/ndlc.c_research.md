# sources/distributed-fs/ceph-client/drivers/nfc/st-nci/ndlc.c

## Purpose
`ndlc.c` implements the ST low-level NDLC transport state machine used beneath the ST_NCI NCI core. It adds/removes packet control bytes, queues outgoing and incoming frames, handles supervisor ACK/NACK/WAIT frames, retransmits on timeout, and detects hard link faults.

## Important APIs, types, and functions
- `ndlc_probe()` allocates `struct llt_ndlc`, initializes timers/queues/work, then calls `st_nci_probe()`.
- `ndlc_open()` enables the physical link and marks it powered.
- `ndlc_close()` toggles reset, sends proprietary NFC mode off, marks unpowered, and disables the physical link.
- `ndlc_send()` prepends a data-frame PCB and queues an skb for worker processing.
- `ndlc_recv()` queues inbound skbs and schedules the state-machine work; NULL receive marks hard fault and closes the link.
- Internal helpers process send queue, receive queue, retransmission, and T1/T2 timer expiry.

## Control flow
Outgoing NCI frames are wrapped with a data PCB and appended to `send_q`. The worker writes each frame through physical ops, records send jiffies in `skb->cb`, moves it to `ack_pending_q`, and arms T1 for supervisor acknowledgement plus T2 for chip availability. Incoming supervisor ACK frees one pending skb and stops timers; NACK requeues pending frames with retransmit bits; WAIT extends T1. Incoming data frames strip the PCB and enter `nci_recv_frame()`. T1 expiry requeues pending data; T2 expiry closes NDLC and sets `hard_fault = -EREMOTEIO`.

## State and persistence
State is in-memory queues (`rcv_q`, `send_q`, `ack_pending_q`), timers, active flags, work item, powered flag, and `hard_fault`. There is no persistence. `skb->cb` temporarily records send time.

## Dependencies and integration points
NDLC depends on transport `struct nfc_phy_ops` for write/enable/disable, NCI core for receive, timers, sk_buff queues, and ST_NCI proprietary mode commands. I2C/SPI transports call `ndlc_recv()` from IRQ contexts.

## Risks
No explicit locking protects queues/timer flags beyond skb queue internals and serialized work assumptions; races between IRQ receive, send, close, and remove need care. ACK handling dequeues one pending skb without checking NULL. `ndlc_remove()` purges `rcv_q` and `send_q` but not `ack_pending_q`, which may leak pending skbs. T2 timeout calls `ndlc_close()` from worker context and sends an NCI proprietary command during fault handling.

## Test signals
Unit-style tests should cover ACK/NACK/WAIT PCBs, T1 retransmit, T2 hard fault, write failure hard fault, data-frame receive, NULL receive, close while pending frames exist, and remove with nonempty `ack_pending_q`.
