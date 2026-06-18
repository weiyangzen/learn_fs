<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/net/netfilter/nf_conntrack_timeout.h -->
# sources/distributed-fs/ceph-client/include/net/netfilter/nf_conntrack_timeout.h

## Purpose
`nf_conntrack_timeout.h` defines named/custom timeout objects and conntrack timeout extension APIs.

## Important APIs, types, and functions
It defines `CTNL_TIMEOUT_NAME_MAX`, `struct nf_ct_timeout`, `struct nf_conn_timeout`, data/find/add/lookup helpers, `nf_ct_untimeout`, `nf_ct_set_timeout`, `nf_ct_destroy_timeout`, and RCU timeout hook callbacks.

## Control flow
Userspace can define named timeout policies. Conntracks allocate a timeout extension pointing via RCU to a timeout object, and protocol code looks up the per-protocol timeout array through `nf_ct_timeout_lookup`. Destroy paths detach references.

## State and persistence
State is per-conntrack timeout extension pointer, named timeout objects with L3/protocol and variable data, and global RCU hook table. No on-disk persistence is defined here.

## Dependencies and integration points
It depends on conntrack, extensions, L4 protocol definitions, net namespace, refcounts, and CONFIG_NF_CONNTRACK_TIMEOUT. It integrates ctnetlink timeout policies with conntrack protocol state.

## Risks and test signals
Risks include RCU pointer lifetime, protocol/object size mismatch, timeout name lookup failure, disabled stub returning `-EOPNOTSUPP`, and stale timeouts during namespace teardown. Tests should cover set/destroy, policy delete while flows reference it, protocol-specific timeout data, disabled builds, and namespace cleanup.

## Source read
Read `sources/distributed-fs/ceph-client/include/net/netfilter/nf_conntrack_timeout.h` completely for this pass (112 lines, 2679 bytes).
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/net/netfilter/nf_conntrack_timeout.h -->
