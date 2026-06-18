# sources/distributed-fs/ceph-client/drivers/net/wan/hdlc_cisco.c

## Purpose
`hdlc_cisco.c` implements Cisco HDLC protocol support for the generic HDLC core. It adds Cisco HDLC framing, keepalive negotiation, link dormancy management, and ioctl-based protocol selection using `IF_PROTO_CISCO`.

## Important APIs, Types, And Functions
The key wire structures are `struct hdlc_header` and `struct cisco_packet`. `struct cisco_state` holds user settings, a timer, peer sequence tracking, link-up state, and a spinlock. The protocol callbacks are `cisco_start()`, `cisco_stop()`, `cisco_type_trans()`, `cisco_rx()`, and `cisco_ioctl()` in a `struct hdlc_proto`. `cisco_hard_header()` is exposed through `cisco_header_ops`, and `cisco_keepalive_send()` creates control packets for address replies and keepalive requests.

## Control Flow
When user space selects Cisco HDLC, `cisco_ioctl()` validates privileges, device-down state, interval and timeout, asks the hardware driver to attach NRZ/CRC16, allocates `struct cisco_state`, stores settings, installs header ops, changes `dev->type` to `ARPHRD_CISCO`, and marks the interface dormant. On carrier start, `cisco_start()` initializes sequence state and starts a one-second timer. The timer checks timeout, marks the link dormant if keepalives age out, sends a `CISCO_KEEPALIVE_REQ`, and re-arms itself using the configured interval. Receive dispatch validates the Cisco header, drops system-info packets, replies to address requests with the configured IPv4 address if present, and uses keepalive ACKs to mark the link up.

## State And Persistence
All state is volatile per HDLC device. `txseq`, `rxseq`, `last_poll`, and `up` are guarded by `cisco_state.lock`. The timer is deleted synchronously on stop. The module registers and unregisters only the protocol callback object.

## Dependencies And Integration Points
This module depends on the generic HDLC protocol registry, netdevice header ops, `dev_queue_xmit()`, IPv4 address access via `__in_dev_get_rcu()`, traffic-control priority for control packets, and `netif_dormant_on/off()` to expose protocol-level link health separately from physical carrier.

## Risks
Timer send runs while `st->lock` is held and calls into transmit queueing, so changes around locking or allocator context need care. Keepalive packet validation allows only two exact Cisco control lengths; unexpected peer variants are treated as errors. The address-request path assumes `init_net` behavior inherited from the HDLC core. User-provided keepalive intervals are minimally bounded, so very low values could create excessive control traffic.

## Test Signals
Test by attaching Cisco HDLC with invalid and valid settings, confirming netdevice type and dormant state, observing periodic keepalive frames, simulating keepalive ACKs to transition dormant off, checking timeout transition back to dormant, and confirming unsupported protocols are dropped without corrupting stats except intended error counters.
