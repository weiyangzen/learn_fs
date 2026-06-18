
<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/can.h -->
# sources/distributed-fs/ceph-client/include/uapi/linux/can.h

## Purpose
Defines the core SocketCAN UAPI shared by raw CAN, CAN FD, CAN XL, BCM, ISO-TP, J1939, gateways, and netlink configuration. It standardizes CAN identifiers, frame layouts, protocol numbers, socket addresses, and filter structures.

## APIs, Control Flow, and State
Important exports include `canid_t`, `can_err_mask_t`, identifier flags/masks (`CAN_EFF_FLAG`, `CAN_RTR_FLAG`, `CAN_ERR_FLAG`, `CAN_SFF_MASK`, `CAN_EFF_MASK`), payload sizes for classic CAN, CAN FD, and CAN XL, `struct can_frame`, `struct canfd_frame`, `struct canxl_frame`, MTU constants, protocol numbers (`CAN_RAW`, `CAN_BCM`, `CAN_ISOTP`, `CAN_J1939`), `SOL_CAN_BASE`, `struct sockaddr_can`, and `struct can_filter`. The frame structs encode the per-packet state passed through sockets; `sockaddr_can` selects interface and protocol-specific addressing data. There is no implementation control flow in the header; kernel socket families validate MTU, flags, and filters and route frames to netdevices and protocol modules.

## Dependencies, Integration, Risks, and Tests
Depends on Linux integer, socket, and `offsetof` definitions. Integration spans PF_CAN sockets, CAN netdevices, vcan/vxcan, CAN FD/XL drivers, filters, error frames, and protocol modules. Risks include ABI layout constraints for the dual-use classic/FD structs, misinterpreting CAN ID flag bits as identifier bits, accepting invalid CAN XL length or mandatory XLF flags, filter inversion errors, and userspace not enabling FD/XL support before sending larger MTUs. Test signals include SocketCAN selftests, vcan/vxcan frame send/receive, CAN FD/XL MTU validation, filter-match tests including inverted filters, and compat layout checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/can.h -->
