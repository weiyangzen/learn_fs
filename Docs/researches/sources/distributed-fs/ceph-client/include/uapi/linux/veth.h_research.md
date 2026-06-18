# sources/distributed-fs/ceph-client/include/uapi/linux/veth.h

## Purpose
Defines netlink attribute IDs for virtual Ethernet pair information.

## Important APIs, Types, And Constants
The anonymous enum exposes `VETH_INFO_UNSPEC`, `VETH_INFO_PEER`, and `__VETH_INFO_MAX`; `VETH_INFO_MAX` is `__VETH_INFO_MAX - 1`. `VETH_INFO_PEER` identifies nested peer link information in rtnetlink messages.

## Control Flow, State, And Persistence
No code runs here. During veth creation or inspection, rtnetlink messages use these attributes to describe the peer endpoint. Persistent state is the kernel network-device pair and its namespace placement, not the header.

## Dependencies And Integration Points
The header is standalone and integrates with rtnetlink, `ip link add type veth`, container/network namespace setup tools, and kernel veth driver attributes.

## Risks And Test Signals
Risks include netlink attribute policy drift and incorrect nested peer parsing by userspace. Tests should create veth pairs with peer attributes, move peers across namespaces, dump link info, and verify `VETH_INFO_MAX` bounds in netlink policy and userspace decoders.
