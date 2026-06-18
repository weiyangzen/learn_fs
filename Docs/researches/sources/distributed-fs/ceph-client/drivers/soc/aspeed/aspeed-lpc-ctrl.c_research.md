# sources/distributed-fs/ceph-client/drivers/soc/aspeed/aspeed-lpc-ctrl.c

## Purpose
This miscdevice driver controls ASPEED LPC firmware/memory windows from host LPC space to BMC memory or flash and exposes an mmap interface for the reserved BMC memory buffer.

## Important APIs, Types, And Functions
`struct aspeed_lpc_ctrl` stores the miscdevice, LPC regmap, clock, reserved memory, PNOR flash info, AST2600 FWH2AHB state, and SCU regmap. File operations are `aspeed_lpc_ctrl_mmap()` and `aspeed_lpc_ctrl_ioctl()`. IOCTLs include `ASPEED_LPC_CTRL_IOCTL_GET_SIZE` and `ASPEED_LPC_CTRL_IOCTL_MAP`.

## Control Flow
Probe records optional flash resource and reserved-memory resource, validates reserved memory is power-of-two and naturally aligned, gets the parent LPC syscon regmap, handles AST2600 SCU setup, enables the clock, and registers `/dev/aspeed-lpc-ctrl`. GET_SIZE returns reserved memory size. MAP validates flags, window type, size/offset alignment, offset within flash or memory, programs HICR7/HICR8 mapping registers, optionally enables AST2600 FWH2AHB, and enables LPC firmware cycles.

## State, Persistence, And Dependencies
State lives in hardware registers and the miscdevice struct. Dependencies include parent LPC syscon, optional flash phandle, optional reserved memory, clocks, miscdevice, mmap, usercopy, and ASPEED LPC ioctl UAPI.

## Integration Points
Userspace controls host-visible LPC windows and maps BMC reserved memory. This binds as a child of the ASPEED LPC syscon node.

## Risks
The IOCTL copies the mapping struct before checking command, so unknown commands still require a readable user pointer. There is no explicit serialization around HICR register updates. Host exposure of BMC memory/flash is security-sensitive and relies on userspace permissions and DT region constraints. FWH2AHB programming is AST2600-specific.

## Test Signals
Probe with/without flash and reserved memory, reject invalid memory geometry, test GET_SIZE, MAP for flash and memory, mmap range checks, AST2600 FWH2AHB path, and host LPC read/write validation.
