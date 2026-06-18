<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/net/netfilter/nf_conntrack_expect.h -->
# sources/distributed-fs/ceph-client/include/net/netfilter/nf_conntrack_expect.h

## Purpose
`nf_conntrack_expect.h` defines conntrack expectations used by helpers/NAT to preauthorize related connections.

## Important APIs, types, and functions
It defines global expectation hash sizing symbols, `struct nf_conntrack_expect`, `struct nf_conntrack_expect_policy`, class/flag constants, pernet/global init/fini, find/get/unlink/remove/iterate functions, allocation/init/put, and related-registration APIs.

## Control flow
Helpers allocate expectations from a master conntrack, initialize tuple/mask/protocol/class/NAT data, insert with `nf_ct_expect_related`, and later incoming packets find and optionally unlink matching expectations to create related conntracks and call `expectfn`.

## State and persistence
State includes expectation hash/list nodes, netns pointer, tuple/mask, optional zone, refcount, flags/class, helper pointers, master conntrack, timeout timer, optional NAT saved address/proto/dir, and global hash table/max counts.

## Dependencies and integration points
It depends on conntrack, zones, timers, RCU, helpers, NAT optional support, and expectation locks from core. It integrates helpers such as FTP/SIP with related-flow tracking.

## Risks and test signals
Risks include timer vs unlink races, master/helper lifetime, expectation hash exhaustion, zone matching semantics, NAT saved tuple mistakes, `NF_CT_EXP_F_SKIP_MASTER` reuse surprises, and ref leaks. Tests should cover helper-created expectations, timeout expiry, related flow creation, NAT expectations, zones, class limits, and iterate-destroy.

## Source read
Read `sources/distributed-fs/ceph-client/include/net/netfilter/nf_conntrack_expect.h` completely for this pass (157 lines, 4528 bytes).
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/net/netfilter/nf_conntrack_expect.h -->
