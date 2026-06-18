<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/atm_tcp.h -->
# sources/distributed-fs/ceph-client/include/uapi/linux/atm_tcp.h

## Purpose
Defines the ATMTCP pseudo-ATM driver protocol and ioctls for tunneling ATM cells/control over a TCP-like daemon interface.

## Important APIs, Types, And Functions
`struct atmtcp_hdr` carries network-order VPI, VCI, and length. `ATMTCP_HDR_MAGIC` marks control messages. `struct atmtcp_control` carries open/close control, kernel VCC pointer, suggested PVC address, QoS, and result. Ioctls include `SIOCSIFATMTCP`, `ATMTCP_CREATE`, and `ATMTCP_REMOVE`.

## Control Flow
Kernel and daemon exchange data cells or control messages. Open/close messages carry VCC, address, QoS, and result fields according to direction; create/remove ioctls manage persistent ATMTCP interfaces.

## State And Persistence
State includes persistent ATMTCP interface instances and active VCC mappings between kernel and daemon. `atm_kptr_t` carries opaque kernel pointers.

## Dependencies And Integration Points
Depends on ATM API, ATM addresses/QoS, ioctl ranges, and Linux types. Integrates with ATM daemon/userland emulation.

## Risks And Edge Cases
Header fields are network byte order while control fields are host order. Opaque pointer handling, open/close field direction, and persistent interface cleanup are fragile.

## Test Signals
Create/remove interface tests, open/close control exchange, endian validation for VPI/VCI/length, invalid result handling, and VCC cleanup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/atm_tcp.h -->
