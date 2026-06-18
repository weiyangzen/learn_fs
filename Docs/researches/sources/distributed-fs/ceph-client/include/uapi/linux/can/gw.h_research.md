
<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/can/gw.h -->
# sources/distributed-fs/ceph-client/include/uapi/linux/can/gw.h

## Purpose
Defines the SocketCAN gateway netlink ABI for routing, filtering, modifying, and checksum-updating CAN and CAN FD frames between CAN interfaces.

## APIs, Control Flow, and State
The header exports gateway routing flag bits, netlink attribute IDs, `struct rtcanmsg`, CAN/CAN FD frame modification structures, checksum descriptors (`cgw_csum_xor`, `cgw_csum_crc8`), CRC8 profile constants, and length macros for each attribute payload. A gateway rule combines source/destination interfaces, filter/mask, optional frame modifications, checksum operations, and deletion/echo/control flags. Control flow is in the gateway netlink handler and packet forwarding path: rules are created, matched against incoming frames, transformations are applied, and packets are emitted to destination interfaces. Persistent state is the configured gateway rule table in the kernel.

## Dependencies, Integration, Risks, and Tests
Depends on core CAN frame layouts and netlink route-message conventions. Integration points are can-gw userspace tools, CAN network namespaces, vcan/vxcan setups, and in-kernel CAN receive/transmit paths. Risks include malformed netlink attributes, out-of-bounds modification/checksum offsets, rule loops between interfaces, FD/classic frame-size confusion, and CRC profile drift. Test signals include can-gw rule add/delete/list tests, frame modification and checksum verification, loop-prevention tests, netns/vxcan forwarding, and fuzzed netlink attribute lengths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/can/gw.h -->
