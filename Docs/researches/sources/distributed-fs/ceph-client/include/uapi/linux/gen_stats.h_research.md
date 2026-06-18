<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/gen_stats.h -->
# sources/distributed-fs/ceph-client/include/uapi/linux/gen_stats.h

## Purpose
`gen_stats.h` defines the generic traffic-control statistics ABI used in netlink attributes for qdiscs, classes, actions, and estimators. It is a layout contract between kernel networking code and user tools such as `tc`.

## Important APIs, types, and functions
The exported attribute IDs are `TCA_STATS_UNSPEC`, `TCA_STATS_BASIC`, `TCA_STATS_RATE_EST`, `TCA_STATS_QUEUE`, `TCA_STATS_APP`, `TCA_STATS_RATE_EST64`, `TCA_STATS_PAD`, and `TCA_STATS_BASIC_HW`, bounded by `TCA_STATS_MAX`. Data layouts are `struct gnet_stats_basic`, `struct gnet_stats_rate_est`, `struct gnet_stats_rate_est64`, `struct gnet_stats_queue`, and `struct gnet_estimator`.

## Control flow
This header has no executable flow. The kernel fills nested `TCA_STATS_*` netlink attributes; user space selects known attributes and decodes the matching fixed-size structures.

## State and persistence behavior
State is sampled counter state, not persistent configuration. 64-bit byte and packet counters are used for basic stats, while queue counters and estimator settings reflect current qdisc/action state.

## Dependencies and integration points
It depends on `<linux/types.h>` and is included by traffic-control UAPI consumers. It integrates with rtnetlink dumps and rate estimator setup.

## Risks and test signals
Risks are ABI size changes, 32-bit rate estimator overflow, confusing software and hardware basic counters, and attribute alignment mistakes. Test signals include `tc -s` dumps, netlink policy validation, 32/64-bit userspace decoding, and qdisc/action tests that compare byte, packet, drop, requeue, and rate fields.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/gen_stats.h -->
