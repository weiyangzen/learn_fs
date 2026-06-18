<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/aspeed-p2a-ctrl.h -->
# sources/distributed-fs/ceph-client/include/uapi/linux/aspeed-p2a-ctrl.h

## Purpose
Defines ioctls for ASPEED P2A host access windows into BMC physical memory, including read-only/read-write policy and memory config readback.

## Important APIs, Types, And Functions
`ASPEED_P2A_CTRL_READ_ONLY` and `ASPEED_P2A_CTRL_READWRITE` are window flags. `struct aspeed_p2a_ctrl_mapping` carries physical address, length, and flags. Ioctls are `ASPEED_P2A_CTRL_IOCTL_SET_WINDOW` and `ASPEED_P2A_CTRL_IOCTL_GET_MEMORY_CONFIG`.

## Control Flow
Userspace sets a host-readable or host-writable BMC memory window, or queries the configured memory region used for mmap. Once a region is mapped, hardware semantics can unlock broader read access.

## State And Persistence
State is live P2A hardware window configuration. It controls host access to BMC memory until changed or reset.

## Dependencies And Integration Points
Depends on ioctl/types. Integrates with ASPEED P2A hardware, BMC security configuration, host debug/management flows, and mmap-capable driver paths.

## Risks And Edge Cases
The documented caveat that any mapped region unlocks all regions for reading is a major security risk. Address/length validation, write enable, and permission checks are critical.

## Test Signals
SET_WINDOW/GET_MEMORY_CONFIG ioctl tests, read-only vs read-write host access tests, invalid range rejection, and security policy checks around memory exposure.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/aspeed-p2a-ctrl.h -->
