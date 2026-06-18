<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/net/netfilter/nf_conntrack_timestamp.h -->
# sources/distributed-fs/ceph-client/include/net/netfilter/nf_conntrack_timestamp.h

## Purpose
`nf_conntrack_timestamp.h` defines optional start/stop timestamp extension support for conntrack entries.

## Important APIs, types, and functions
It defines `struct nf_conn_tstamp`, find/add helpers, and `nf_conntrack_tstamp_pernet_init` or a stub.

## Control flow
When per-net timestamping is enabled, conntracks allocate a timestamp extension and implementation records start/stop times for reporting.

## State and persistence
State is per-conntrack start/stop 64-bit timestamps plus `net->ct.sysctl_tstamp` per-net enable flag.

## Dependencies and integration points
It depends on conntrack, tuple constants, extensions, and CONFIG_NF_CONNTRACK_TIMESTAMP. It integrates with ctnetlink/proc reporting of flow lifetimes.

## Risks and test signals
Risks include missing extension after sysctl toggles, timestamp source consistency, zero stop time interpretation, and disabled-build stubs. Tests should cover timestamp enable/disable, flow creation/destruction, reporting, and namespace isolation.

## Source read
Read `sources/distributed-fs/ceph-client/include/net/netfilter/nf_conntrack_timestamp.h` completely for this pass (47 lines, 1124 bytes).
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/net/netfilter/nf_conntrack_timestamp.h -->
