# sources/distributed-fs/ceph-client/include/trace/events/qdisc.h

Purpose: Provides traffic-control qdisc tracepoints for enqueue, dequeue, drop, reset, destroy, and create operations. It makes qdisc queueing behavior observable in the network stack.

Important APIs/types/functions: Events include `qdisc_dequeue`, `qdisc_enqueue`, `qdisc_drop`, `qdisc_reset`, `qdisc_destroy`, and `qdisc_create`. Fields capture qdisc pointer, parent handle, ifindex, device name, skb pointer, length, packet count, backlog, return codes, and drop reason symbols.

Control flow: TC/qdisc code emits events when packets enter or leave queues, are dropped, qdiscs are reset/destroyed/created, or enqueue/dequeue actions return. Trace data allows reconstruction of queue depth and drop behavior.

State and persistence: No state is stored. It observes in-memory qdisc and skb state; qdisc configuration persists only via TC/netlink setup outside tracing.

Dependencies and integration points: Depends on skb, netdevice, ftrace, packet scheduler headers, `net/sch_generic.h`, and tracepoints. It integrates with TC, netdev TX scheduling, and drop monitoring.

Risks and test signals: Risks include hot-path overhead, skb lifetime after drop, inconsistent drop-reason coverage, and qdisc pointer reuse. Test pfifo/fq_codel/netem/ingress qdiscs, enqueue/dequeue stress, drops, reset/destroy during traffic, and TC netlink reconfiguration.

Source-read signal: read `sources/distributed-fs/ceph-client/include/trace/events/qdisc.h` completely for this pass (204 lines, 5158 bytes). Final split target: `Docs/researches/sources/distributed-fs/ceph-client/include/trace/events/qdisc.h_research.md`.
