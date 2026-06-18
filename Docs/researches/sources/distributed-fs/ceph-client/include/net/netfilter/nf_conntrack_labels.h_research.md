<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/net/netfilter/nf_conntrack_labels.h -->
# sources/distributed-fs/ceph-client/include/net/netfilter/nf_conntrack_labels.h

## Purpose
`nf_conntrack_labels.h` defines the conntrack labels extension used by xt_connlabel/nftables to attach bit labels to connections.

## Important APIs, types, and functions
It defines `NF_CT_LABELS_MAX_SIZE`, `struct nf_conn_labels`, `nf_ct_labels_find`, `nf_ct_labels_ext_add`, `nf_connlabels_replace`, and per-net label usage get/put helpers.

## Control flow
When labels are in use in a namespace, new conntracks may allocate the labels extension. Rules find the extension directly, replace bits according to data/mask, and manage `labels_used` through get/put.

## State and persistence
State is a bitmap stored per conntrack and a per-net labels-used counter. No disk persistence exists.

## Dependencies and integration points
It depends on conntrack, extension internals, net namespace, and xt_connlabel UAPI limits. It integrates rule matching/setting labels with conntrack entries.

## Risks and test signals
Risks include direct extension lookup bypassing exported symbols, labels not allocated when usage count is zero, word/mask length mismatch, disabled CONFIG stubs, and flow dissector constraints. Tests should cover label get/put, extension allocation, replace masks, max bit, disabled builds, and existing flows before label enable.

## Source read
Read `sources/distributed-fs/ceph-client/include/net/netfilter/nf_conntrack_labels.h` completely for this pass (62 lines, 1709 bytes).
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/net/netfilter/nf_conntrack_labels.h -->
