<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/net/netfilter/nf_conntrack_act_ct.h -->
# sources/distributed-fs/ceph-client/include/net/netfilter/nf_conntrack_act_ct.h

## Purpose
`nf_conntrack_act_ct.h` defines the conntrack extension used by the traffic-control `act_ct` action to remember ingress/egress interface indexes.

## Important APIs, types, and functions
It defines `struct nf_conn_act_ct_ext` and helpers to find, fill, and add the extension.

## Control flow
When `CONFIG_NET_ACT_CT` is enabled, TC action paths allocate the ACT_CT extension and fill the direction-specific ifindex from the skb device for init_net traffic.

## State and persistence
State is a two-entry ifindex array stored as a conntrack extension. The helper stores nothing when NET_ACT_CT is disabled or when not in `init_net`.

## Dependencies and integration points
It depends on conntrack, conntrack extensions, skb device state, and TC act_ct configuration. It integrates TC connection tracking with later flow/offload consumers.

## Risks and test signals
Risks include `nf_conn_act_ct_ext_add` not checking allocation before fill, init_net-only behavior surprises, skb without dev, and stale ifindexes after device removal. Tests should cover extension allocation, both directions, non-init netns behavior, and disabled builds.

## Source read
Read `sources/distributed-fs/ceph-client/include/net/netfilter/nf_conntrack_act_ct.h` completely for this pass (54 lines, 1350 bytes).
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/net/netfilter/nf_conntrack_act_ct.h -->
