# sources/distributed-fs/ceph-client/net/sched/sch_blackhole.c

## Purpose
`sch_blackhole.c` implements the minimal `blackhole` qdisc. Every packet accepted by enqueue is dropped immediately, and dequeue/peek always return no packet. It is useful as an explicit traffic sink while keeping qdisc attachment semantics.

## Important APIs, Types, and Functions
The only behavior functions are `blackhole_enqueue()` and `blackhole_dequeue()`. `blackhole_qdisc_ops` advertises id `blackhole`, no private state, enqueue/dequeue/peek callbacks, and module ownership. `blackhole_init()` registers the qdisc through `register_qdisc()` at device initcall time.

## Control Flow
On enqueue, the qdisc calls `qdisc_drop()` for the skb, then returns `NET_XMIT_SUCCESS | __NET_XMIT_BYPASS`, signaling that the packet did not remain queued and callers should not treat it as a congestion backoff event. Dequeue and peek return `NULL`, so the qdisc is always empty from the device transmit scheduler's perspective.

## State and Persistence
There is no qdisc-private state, no queue, no timers, no child qdiscs, and no persistence. Statistics are updated only through the common qdisc drop path.

## Dependencies and Integration Points
The file depends only on core qdisc/skbuff headers and `register_qdisc()` from `sch_api.c`. It integrates with traffic control by registering `Qdisc_ops` with id `blackhole`; there are no netlink options, class operations, hardware offload hooks, or module exit unregister path in this source.

## Risks
The main behavioral risk is operator surprise: enqueue reports success with bypass while discarding all packets. Because there is no `module_exit()` unregister in this file, it behaves like built-in/device-init registered scheduler code rather than a normal unloadable qdisc module.

## Test Signals
Attach `blackhole` to a test interface or class and verify packets are dropped, qdisc backlog and qlen stay at zero, dequeue never emits skbs, and `tc qdisc show` exposes the qdisc id. Drop counters should move through the standard qdisc drop accounting.
