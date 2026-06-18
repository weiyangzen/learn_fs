# sources/distributed-fs/ceph-client/net/sched/sch_mqprio.c

Purpose: implements the root `mqprio` qdisc, mapping socket priorities to traffic classes and traffic classes to hardware TX queue ranges. It can configure software queue mapping or delegate ownership to hardware through `TC_SETUP_QDISC_MQPRIO`.

Important APIs, types, and functions: `struct mqprio_sched` stores child qdisc pointers, mode, shaper, hardware offload state, netlink flags, min/max rates, and frame preemption (`fp`) settings. Key routines are `mqprio_parse_opt`, `mqprio_parse_nlattr`, `mqprio_parse_tc_entries`, `mqprio_enable_offload`, `mqprio_disable_offload`, `mqprio_init`, `mqprio_attach`, `mqprio_graft`, `mqprio_dump`, `mqprio_dump_class_stats`, and `mqprio_walk`.

Control flow: init validates root placement, multiqueue support, classid capacity, option length, queue mapping via `mqprio_validate_qopt`, and offload capabilities. Extended netlink attributes are allowed only in hardware mode. Child qdiscs are precreated for every TX queue. If `qopt->hw` is set, the qdisc builds an offload request with optional mode/shaper/rate/preemption fields and calls `ndo_setup_tc`; otherwise it programs `netdev_set_num_tc` and each `netdev_set_tc_queue`. Priority-to-TC mappings are always applied to the netdev.

State and persistence behavior: child qdiscs move from the preattach array to netdev queues at attach. The netdev stores TC queue mappings and priority maps; `mqprio_qopt_reconstruct` reconstructs dumps from device state. Private state preserves offload mode, flags, rate arrays, and frame preemption values for dump/offload teardown. Destroy either disables hardware offload or clears `num_tc`.

Dependencies and integration points: uses the shared mqprio library, ethtool MAC merge/preemption support (`ethtool_dev_mm_supported`), netdev TC mapping APIs, child qdisc grafting, and `ndo_setup_tc(TC_SETUP_QDISC_MQPRIO)`. It shares `mq_change_real_num_tx` with mq-style roots.

Risks: extended attrs are tightly coupled to `qopt->hw`; accepting them in software mode would create state userspace cannot enforce. Hardware drivers may override or validate queue counts differently, so offload capability queries matter. Frame preemption must reject unsupported devices. Stats for virtual traffic classes unlock and relock around child qdisc locks, which is sensitive to locking order. Class IDs have two regions: per-queue classes and virtual traffic-class classes.

Test signals: validate queue count overlaps/ranges, hardware and software modes, DCB versus channel mode/shaper combinations, min/max rate dumping, frame preemption with and without MAC merge support, class walking order, virtual TC stats aggregation, child grafting while up, and destroy behavior for offload and non-offload paths.
