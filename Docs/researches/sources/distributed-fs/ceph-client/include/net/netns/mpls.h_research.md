# sources/distributed-fs/ceph-client/include/net/netns/mpls.h

Purpose: Defines per-network-namespace MPLS routing and platform-label state.

Important APIs/types/functions: `struct netns_mpls` stores `ip_ttl_propagate`, `default_ttl`, `platform_labels`, an RCU pointer array of RCU `mpls_route` pointers, `platform_mutex`, `platform_label_seq`, and sysctl header `ctl`.

Control flow: MPLS route lookup uses the per-net platform-label table indexed by label under RCU/sequence protection. Configuration changes take `platform_mutex`, update the table and sequence counter, and sysctls adjust TTL propagation/default TTL.

State and persistence: Runtime per-net MPLS route tables and sysctl state.

Dependencies/integration: Depends on MPLS routing, sysctl, net namespace lifecycle, and route table allocation.

Risks/test signals: Test platform label resize with concurrent lookup, sequence counter retry behavior, route table cleanup, TTL sysctl changes, namespace isolation, and disabled MPLS builds.
