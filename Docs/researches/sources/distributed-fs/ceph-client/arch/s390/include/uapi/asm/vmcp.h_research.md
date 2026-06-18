# sources/distributed-fs/ceph-client/arch/s390/include/uapi/asm/vmcp.h

## Purpose
Defines the userspace ioctl ABI for the s390 z/VM CP command character device. The device lets userspace submit CP commands via diagnose code 8 and retrieve CP responses.

## Important APIs, Types, And Functions
The header exposes `VMCP_GETCODE`, `VMCP_SETBUF`, and `VMCP_GETSIZE`. These use ioctl type `0x10` and an `int` payload to get the CP response code, configure the response buffer size, and query the current response buffer size.

## Control Flow
This header has no executable logic. Userspace writes CP commands to the vmcp device, then uses these ioctls to control or inspect command response handling in the vmcp driver.

## State And Persistence
The header persists only ioctl numbers. Runtime state such as the last CP response code and buffer size belongs to the vmcp device instance.

## Dependencies And Integration Points
Depends on `<linux/ioctl.h>`. It integrates z/VM management tools with the kernel vmcp driver and the lower-level `cpcmd` diagnose 8 implementation.

## Risks And Edge Cases
The ABI is old and compact, so ioctl number reuse is the main risk. `int` payload sizing must remain compat-safe. Driver tests need to cover invalid buffer sizes and CP commands that return large or no responses.

## Test Signals
Signals include UAPI header compile checks, vmcp ioctl smoke tests under z/VM, response-code propagation, buffer resize behavior, and compat 32-bit userspace ioctl tests where applicable.
