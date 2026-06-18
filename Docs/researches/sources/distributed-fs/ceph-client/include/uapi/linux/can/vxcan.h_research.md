
<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/can/vxcan.h -->
# sources/distributed-fs/ceph-client/include/uapi/linux/can/vxcan.h

## Purpose
Defines the netlink information attributes for virtual CAN tunnel pairs (`vxcan`). It is the minimal UAPI used to create and inspect peer links.

## APIs, Control Flow, and State
The header exports an enum with `VXCAN_INFO_UNSPEC`, `VXCAN_INFO_PEER`, and `__VXCAN_INFO_MAX`, plus `VXCAN_INFO_MAX`. There are no structures or functions; rtnetlink creation paths interpret the peer attribute to instantiate linked virtual CAN devices. Persistent state is the netdevice pair and namespace placement, not the header.

## Dependencies, Integration, Risks, and Tests
Integration points are `ip link add type vxcan`, network namespaces, CAN protocol tests that need linked virtual devices, and rtnetlink parsers. Risks are malformed nested peer attributes, namespace cleanup issues, and tooling assuming veth-like attributes beyond the single peer definition. Test signals include vxcan create/delete tests, namespace move tests, frame forwarding between peers, and netlink attribute validation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/can/vxcan.h -->
