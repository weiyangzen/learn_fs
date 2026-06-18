<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/openvswitch.h -->
# sources/distributed-fs/ceph-client/include/linux/openvswitch.h

## Purpose
This header is the kernel-private Open vSwitch wrapper that includes the UAPI OVS definitions and adds an internal clone-action attribute constant.

## Important APIs, types, and functions
It includes `<uapi/linux/openvswitch.h>` and defines `OVS_CLONE_ATTR_EXEC` as clone action attribute index 0, representing a u32 flag controlling whether clone actions mutate flow keys.

## Control flow
OVS action parsing/execution code can inspect this attribute while handling clone actions. There are no functions or state transitions in the header.

## State and persistence
No state is stored. The attribute value affects per-packet action execution state in Open vSwitch datapath code.

## Dependencies and integration points
It integrates kernel datapath internals with the OVS netlink UAPI definitions.

## Risks and test signals
Risks include attribute numbering conflicts with UAPI action parsing, inconsistent clone flow-key mutation semantics, and userspace/kernel version assumptions. Test OVS clone actions with and without execute semantics, netlink policy parsing, and datapath compatibility with userspace ovs-vswitchd.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/openvswitch.h -->
