# sources/distributed-fs/ceph-client/net/sched/sch_mqprio_lib.c

Purpose: provides shared mqprio helpers used by `mqprio` and related qdiscs such as taprio. The helpers validate traffic-class queue mappings, reconstruct a `tc_mqprio_qopt` from netdev state, and convert per-TC frame-preemption settings into an offload bitmask.

Important APIs, types, and functions: `mqprio_validate_qopt` is exported and validates `num_tc`, priority-to-TC map bounds, and optionally queue counts. `mqprio_validate_queue_counts` checks nonzero queue counts, range within `real_num_tx_queues`, and overlap unless explicitly allowed. `mqprio_qopt_reconstruct` fills `num_tc`, priority map, counts, and offsets from `struct net_device`. `mqprio_fp_to_offload` builds `preemptible_tcs` from `TC_FP_PREEMPTIBLE` entries.

Control flow: validation first rejects `num_tc > TC_MAX_QUEUE`, then verifies every `prio_tc_map` entry is less than `num_tc`. If requested, each TC queue interval `[offset, offset + count)` is checked for nonzero size, device bounds, and pairwise overlap. Reconstruction reads device TC state linearly. Frame-preemption conversion scans all queue slots and sets one bit per preemptible TC.

State and persistence behavior: this file owns no long-lived state. It reads caller-provided qopts and netdev fields, writes caller-provided output structs, and reports validation failures through extack messages.

Dependencies and integration points: depends on netdevice TC fields, netlink extack formatting, `TC_QOPT_MAX_QUEUE`, `TC_BITMASK`, and `TC_FP_*` constants. Exports symbols with GPL visibility for other scheduler modules.

Risks: callers choose whether queue counts are validated and whether overlap is allowed, so misuse can accept configurations a device cannot execute. Reconstruction trusts netdev state to be coherent. Error messages include queue count/offset data and should remain aligned with iproute2 expectations.

Test signals: unit-style tests should cover invalid `num_tc`, priority map entries outside range, zero queue counts, queue ranges exceeding `real_num_tx_queues`, overlapping intervals with overlap allowed and disallowed, reconstruction from programmed netdev TC state, and preemptible bitmask generation.
