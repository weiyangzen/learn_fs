<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/net/netfilter/nf_conntrack_acct.h -->
# sources/distributed-fs/ceph-client/include/net/netfilter/nf_conntrack_acct.h

## Purpose
`nf_conntrack_acct.h` defines optional packet/byte accounting extensions for conntrack entries and per-netns accounting controls.

## Important APIs, types, and functions
It defines `struct nf_conn_counter`, `struct nf_conn_acct`, find/add helpers, enabled/set helpers, `nf_ct_acct_add`, `nf_ct_acct_update`, and pernet init.

## Control flow
When per-netns accounting is enabled, new conntracks can allocate the ACCT extension. Packet paths update per-direction atomic counters through `nf_ct_acct_update`.

## State and persistence
State is per-conntrack ACCT extension counters and `net->ct.sysctl_acct` per-net setting. No disk persistence exists.

## Dependencies and integration points
It depends on conntrack, tuple common constants, extensions, and net namespace state. It integrates with conntrack timeout/refresh paths and sysctl configuration.

## Risks and test signals
Risks include extension missing when sysctl toggles after connection creation, atomic counter overhead, disabled CONFIG stubs, and direction indexing. Tests should cover accounting on/off, existing flows after toggles, both directions, and namespace isolation.

## Source read
Read `sources/distributed-fs/ceph-client/include/net/netfilter/nf_conntrack_acct.h` completely for this pass (81 lines, 1819 bytes).
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/net/netfilter/nf_conntrack_acct.h -->
