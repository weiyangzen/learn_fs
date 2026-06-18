# sources/distributed-fs/ceph-client/include/uapi/linux/ipmi_bmc.h

## Purpose
`ipmi_bmc.h` defines a small BMC-side IPMI ioctl ABI for manipulating SMS attention and abort state.

## Important APIs, Types, and Functions
The ioctl magic is `0xB1`. Exposed commands are `IPMI_BMC_IOCTL_SET_SMS_ATN`, `IPMI_BMC_IOCTL_CLEAR_SMS_ATN`, and `IPMI_BMC_IOCTL_FORCE_ABORT`. They carry no payload and are encoded with `_IO`.

## Control Flow
BMC emulation or management userspace opens the relevant device and issues one of the control ioctls. The kernel-side BMC driver asserts or clears attention signaling or forces abort handling.

## State and Persistence
State is entirely driver/hardware owned. SMS attention persists until cleared or reset by device state; abort behavior is an immediate control action.

## Dependencies and Integration Points
It includes `<linux/ioctl.h>` and integrates with IPMI BMC character devices and host-management signaling paths.

## Risks and Test Signals
Tests should confirm ioctl numbers, permission checks, idempotent set/clear behavior, abort effects on in-flight messages, and error handling when no BMC backend is present.
