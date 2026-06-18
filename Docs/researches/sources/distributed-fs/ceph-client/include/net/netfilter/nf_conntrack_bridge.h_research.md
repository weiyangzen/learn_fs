<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/net/netfilter/nf_conntrack_bridge.h -->
# sources/distributed-fs/ceph-client/include/net/netfilter/nf_conntrack_bridge.h

## Purpose
`nf_conntrack_bridge.h` declares a small registration ABI for bridge conntrack hook providers.

## Important APIs, types, and functions
It defines `struct nf_ct_bridge_info` with hook ops pointer/count and owning module, plus `nf_ct_bridge_register` and `nf_ct_bridge_unregister`.

## Control flow
Bridge conntrack code registers its hook operations and module owner with conntrack; unregister removes them during teardown.

## State and persistence
Registered bridge hook info is held by implementation. The header stores no state.

## Dependencies and integration points
It depends on module, netfilter hook ops, and Ethernet UAPI. It integrates bridge traffic with conntrack hooks.

## Risks and test signals
Risks include ops array lifetime, module owner mismatches, and unregister while hooks are active. Tests should cover bridge conntrack module load/unload and bridged IPv4/IPv6 flows.

## Source read
Read `sources/distributed-fs/ceph-client/include/net/netfilter/nf_conntrack_bridge.h` completely for this pass (19 lines, 398 bytes).
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/net/netfilter/nf_conntrack_bridge.h -->
