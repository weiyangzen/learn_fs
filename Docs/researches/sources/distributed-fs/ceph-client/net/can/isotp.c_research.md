# sources/distributed-fs/ceph-client/net/can/isotp.c

## Purpose
This file implements the PF_CAN ISO 15765-2 transport protocol (`CAN_ISOTP`). It exposes datagram sockets that segment larger protocol data units over Classic CAN or CAN FD, handle flow control, enforce padding and STmin options, support broadcast modes, and reassemble incoming ISO-TP PDUs for user space.

## Important APIs, Types, And Functions
`struct isotp_sock` is the socket state. It stores bind state, ifindex, TX/RX CAN IDs, timers, ISO-TP options, flow-control options, link-layer options, forced STmin settings, echo tracking, RX/TX `struct tpcon` state machines, notifier list node, wait queue, and RX state lock.

`struct tpcon` tracks one RX or TX PDU: buffer pointer, buffer length, PDU length, current index, state, block size counter, sequence number, link-layer data length, and default static buffer.

Important functions include `isotp_bind()`, `isotp_sendmsg()`, `isotp_recvmsg()`, `isotp_rcv()`, `isotp_rcv_sf()`, `isotp_rcv_ff()`, `isotp_rcv_cf()`, `isotp_rcv_fc()`, `isotp_send_fc()`, `isotp_send_cframe()`, `isotp_rcv_echo()`, `isotp_setsockopt_locked()`, and netdevice notifier helpers.

## Control Flow
Socket initialization fills default ISO-TP options, initializes RX/TX state to idle, points RX/TX buffers at static 8300-byte arrays, sets up three high-resolution timers, adds the socket to the global notifier list, and installs `isotp_sock_destruct()`.

Before binding, user space may set options. `isotp_bind()` validates AF_CAN, ifindex, sanitized CAN IDs, CAN/CAN FD MTU compatibility, and distinct TX/RX IDs for normal unicast mode. It registers the RX ID for data/flow-control frames unless a broadcast mode is active, always registers the TX ID for local echo tracking, then marks the socket bound.

`isotp_sendmsg()` serializes one PDU at a time using `cmpxchg()` on `tx.state`. It may grow the static TX buffer up to the module `max_pdu_size`, validates broadcast constraints, copies user payload, builds a single frame when possible, otherwise builds a first frame and either waits for flow control or enters CF-broadcast mode. Consecutive frames are paced by local echo (`isotp_rcv_echo()`), flow-control block size, and `tx_gap`/`txfrtimer`.

The receive callback `isotp_rcv()` enforces the configured MTU, optional extended address, and half-duplex constraints under `rx_lock`. It dispatches N_PCI types to flow-control, single-frame, first-frame, or consecutive-frame handlers. Multi-frame RX sends FC CTS/OVFLW frames unless listen mode is active, tracks sequence numbers, enforces block size and padding options, and queues a completed PDU as a datagram skb.

Release waits for TX idle where possible, moves TX to shutdown, unregisters CAN filters, cancels timers, removes notifier state, and frees any dynamically grown RX/TX buffers in the socket destructor.

## State And Persistence
State is per socket and in memory only. Options must be set before bind because `isotp_setsockopt_locked()` rejects changes after binding. RX/TX state machines persist across callbacks and timers until completion, timeout, error, release, or netdevice unregister.

The default static buffers avoid allocation for common PDUs. Larger buffers are lazily allocated up to `max_pdu_size` and freed on socket destruction. Wait queues coordinate blocking writers and release behavior.

## Dependencies And Integration Points
ISO-TP depends on PF_CAN protocol registration, `can_send()`, CAN receive filters, CAN skb extensions, CAN ISO-TP UAPI options from `linux/can/isotp.h`, high-resolution timers, datagram socket queues, and netdevice notifiers.

It relies on local echo delivery through PF_CAN to know when a single/consecutive frame has left the local stack and when to schedule the next consecutive frame.

## Risks And Edge Cases
Only one TX PDU can be active per socket. Blocking sends wait for idle; nonblocking sends return `-EAGAIN`.

Padding and length validation are subtle across Classic CAN and CAN FD because optimized lengths, mandatory CAN FD padding, extended addressing, and SF_DL/FF_DL escape encodings interact.

Half-duplex mode suppresses conflicting RX/TX progress but depends on correct N_PCI classification under `rx_lock`.

The bind path calls `can_rx_register()` but does not check the return value in the visible code; registration failures could leave partial state if allocation fails in the CAN core.

Some error paths call `netdev_put(dev, NULL)` after `dev_get_by_index()` while most paths call `dev_put()`. That warrants review against the kernel version's netdevice reference API expectations.

Timeouts surface as socket errors: RX data timeout `ETIMEDOUT`, TX flow-control/echo timeout `ECOMM`, malformed padding/layout `EBADMSG`, sequence mismatch `EILSEQ`, and receiver overflow `EMSGSIZE`.

## Test Signals
Test with vcan pairs and ISO-TP user-space tools should cover single-frame and multi-frame send/receive, Classic CAN versus CAN FD MTUs, 12-bit and 32-bit FF_DL lengths, STmin and forced STmin, dynamic flow-control parameters, padding length/data checks, listen mode, half-duplex, SF/CF broadcast modes, local echo timeouts, netdevice down/unregister, and max PDU size boundaries.
