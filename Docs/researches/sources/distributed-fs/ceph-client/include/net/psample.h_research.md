# sources/distributed-fs/ceph-client/include/net/psample.h

Purpose: declares packet sampling group state, metadata, reference helpers, and the optional psample packet emission API.

Important APIs and types: `struct psample_group` stores group list node, netns, group number, refcount, sequence, and RCU head. `struct psample_metadata` carries truncation size, ingress/egress ifindexes, output traffic class/occupancy, latency, validity bits, probability-rate flag, and user cookie. APIs get/take/put groups and, when enabled, sample packets to userspace.

Control flow: callers obtain a group, fill metadata, call `psample_sample_packet()`, and release the group. Disabled builds compile sampling to a no-op while group lifecycle functions remain declared.

State and persistence: per-netns group list/refcounts/sequence are runtime only.

Dependencies and integration points: depends on psample UAPI, RCU, net namespaces, skbuffs, and TC/switchdev sampling users.

Risks and test signals: risks include group refcount leaks, sequence wrap assumptions, metadata validity bit mismatch, and disabled-config no-op surprises. Test sampling netlink output, truncation, metadata combinations, user cookie, group get/put, namespace teardown, and CONFIG_PSAMPLE disabled builds.
