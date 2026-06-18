<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/pkt_sched.h -->
# sources/distributed-fs/ceph-client/include/uapi/linux/pkt_sched.h

Purpose: defines the userspace ABI for Linux traffic-control queue disciplines, qdisc/class handles, generic stats, rate and size specs, and many scheduler-specific option/stat structures.

Important APIs and types: common pieces include `TC_PRIO_*`, `struct tc_stats`, `struct tc_estimator`, `TC_H_*` handle macros, `enum tc_link_layer`, `struct tc_ratespec`, `struct tc_sizespec`, and stab attributes. Scheduler sections define option and stats ABIs for FIFO, skbprio, prio, multiq, plug, TBF, SFQ/SFQRED, RED/GRED/CHOKe, HTB, HFSC, netem, DRR, mqprio, SFB, QFQ, CoDel/FQ-CoDel, FQ, HHF, PIE/FQ-PIE, CBS, ETF, CAKE, TAPRIO, ETS, and DUALPI2.

Control flow: `tc` encodes qdisc/class creation and changes as rtnetlink attributes using these `TCA_*` IDs and structs. The kernel parses the payload into scheduler instances, enqueues/dequeues packets according to qdisc-specific algorithms, and dumps generic and private xstats back to userspace.

State and persistence: qdisc state is in-memory per netdevice/queue/class: token buckets, deficits, RED averages, flow queues, timers, gate schedules, offload flags, statistics, and hardware state. The ABI structures persist only as configuration and dump serialization; no on-disk state is defined.

Dependencies and integration points: depends on Linux const/type headers and integrates with rtnetlink, `tc`, qdisc modules, netdevice TX queues, hardware offload for mqprio/taprio/ETF/CBS/HTB, PTP/clockids for time-aware scheduling, and AQM algorithms such as CoDel, PIE, CAKE, and DUALPI2.

Risks and test signals: risks include field unit confusion (bytes, packets, usec, nsec, sectors-like cells), 32-bit vs 64-bit rate/latency attributes, reserved flag compatibility, flexible nested TAPRIO/MQPRIO entries, and offload/software behavior mismatch. Test qdisc add/change/dump for each scheduler, strict flag validation for v1/v2 ioctls where present, rate64 fallbacks, netem distributions, TAPRIO schedules, mqprio frame preemption, and malformed netlink attributes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/pkt_sched.h -->
