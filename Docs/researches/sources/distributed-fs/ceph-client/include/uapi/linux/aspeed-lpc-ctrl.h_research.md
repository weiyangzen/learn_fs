<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/aspeed-lpc-ctrl.h -->
# sources/distributed-fs/ceph-client/include/uapi/linux/aspeed-lpc-ctrl.h

## Purpose
Defines ioctls for configuring ASPEED BMC LPC host windows into BMC flash or memory resources.

## Important APIs, Types, And Functions
`ASPEED_LPC_CTRL_WINDOW_FLASH` and `ASPEED_LPC_CTRL_WINDOW_MEMORY` identify window types. `struct aspeed_lpc_ctrl_mapping` carries window type/id, reserved flags, host LPC address, BMC offset, and size. Ioctls are `ASPEED_LPC_CTRL_IOCTL_GET_SIZE` and `ASPEED_LPC_CTRL_IOCTL_MAP`.

## Control Flow
Userspace queries a window's size or requests a mapping. The driver validates type/id, alignment, offset/size, then programs LPC bridge registers so the host can access the selected BMC resource.

## State And Persistence
Mapping state is live BMC/host LPC window configuration. It can persist until reprogrammed or reset, depending on hardware/driver lifecycle.

## Dependencies And Integration Points
Depends on Linux ioctl/types. Integrates with ASPEED BMC LPC hardware, host firmware access paths, flash/RAM exposure policy, and BMC management tools.

## Risks And Edge Cases
Address/size must be power-of-two aligned, minimum size is 64 KiB, flags must be zero, and exposing BMC flash/RAM to the host is security-sensitive.

## Test Signals
GET_SIZE/MAP ioctl tests, alignment rejection, window type/id validation, host-visible access tests, and permission/security policy checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/aspeed-lpc-ctrl.h -->
