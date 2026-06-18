<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/include/uapi/linux/pkt_sched.h -->
# sources/distributed-fs/ceph-client/tools/include/uapi/linux/pkt_sched.h

Purpose: this header defines the traffic-control queueing discipline UAPI: qdisc handles, generic stats, rate/size specifications, and parameter/stat structures for many schedulers.

Important APIs/types: generic APIs are `struct tc_stats`, `struct tc_estimator`, handle macros (`TC_H_MAJ`, `TC_H_MIN`, `TC_H_MAKE`, root/ingress constants), `struct tc_ratespec`, and `struct tc_sizespec`. Scheduler-specific sections define FIFO, skbprio, prio, multiq, plug, TBF, SFQ/SFQRED, RED/GRED/CHOKe, HTB, HFSC, netem and loss models, DRR, MQPRIO, SFB, QFQ, CoDel, FQ-CoDel, FQ, HHF, PIE, CBS, ETF, CAKE, and TAPRIO attributes/stats.

Control flow: userspace sends `RTM_NEWQDISC`, `RTM_NEWTCLASS`, and related rtnetlink messages with `tcmsg` plus nested `TCA_*` attributes. Kernel qdisc implementations parse these structs, maintain queue state, and return xstats/stats to dump requests.

State and persistence: qdisc state persists in kernel attached to network devices/classes. This header exposes configuration knobs, statistics snapshots, and queue handles but stores no local state. Many structs are ABI-frozen and contain fixed units such as bytes, packets, microseconds, nanoseconds, rates, or fixed-point probabilities.

Dependencies/integration: depends on `linux/types.h`; integrated with `pkt_cls.h`, `rtnetlink.h`, `iproute2 tc`, NIC hardware offload paths, and time-aware scheduling features.

Risks and test signals: risks include unit confusion, 32-bit rate overflow mitigated by later 64-bit attributes, attribute nesting errors, and scheduler-specific kernel availability. Test by adding/dumping each supported qdisc, checking handle/class linkage, stats growth under traffic, and offload flags for mqprio, cbs, etf, taprio, and cake.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/include/uapi/linux/pkt_sched.h -->
