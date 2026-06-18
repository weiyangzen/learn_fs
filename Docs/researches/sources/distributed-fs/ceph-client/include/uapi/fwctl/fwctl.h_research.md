<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/fwctl/fwctl.h -->
# sources/distributed-fs/ceph-client/include/uapi/fwctl/fwctl.h

## Purpose
Provides the generic fwctl userspace ABI for controlled firmware RPC access. It defines the ioctl numbering, common extensible struct convention, device type discovery, security scopes, and generic RPC envelope.

## Important APIs, Types, And Functions
`FWCTL_INFO` uses `struct fwctl_info` to return `out_device_type` and optional device-specific data. `FWCTL_RPC` uses `struct fwctl_rpc` with scope, input length/pointer, and output length/pointer. `enum fwctl_device_type` identifies MLX5, CXL, BNXT, and PDS payload formats. `enum fwctl_rpc_scope` distinguishes configuration, read-only debug, debug write, and full debug write access.

## Control Flow
Userspace opens a fwctl device, calls `FWCTL_INFO` to determine the vendor payload ABI, allocates any returned device-data buffer, then sends device-specific RPC buffers through `FWCTL_RPC`. The kernel checks struct sizes, rejects nonzero unknown extension bytes, validates scope/permissions, delivers the RPC to firmware, and returns kernel delivery errors separately from device-encoded response status.

## State And Persistence
The ABI is fd-oriented. Per-fd kernel state can include security scope, firmware user context, hot-unplug orphaning, and vendor binding. Firmware configuration RPCs may persist in device firmware depending on command semantics; debug-write scopes may taint the kernel.

## Dependencies And Integration Points
Depends on `<linux/types.h>` and `<linux/ioctl.h>`. Vendor-specific headers provide the device-data and RPC payload formats. Integration points include CAP_SYS_RAW_IO, lockdown policy, driver hotplug, firmware command queues, and user management tools.

## Risks And Edge Cases
ABI growth depends on zeroing unknown struct tails. Errno meanings are part of the contract: `ENOTTY`, `E2BIG`, `EOPNOTSUPP`, `EINVAL`, `ENOMEM`, and `ENODEV` carry distinct diagnostics. Security risk is high because firmware RPCs can expose configuration and debug control.

## Test Signals
Test old/new struct sizes, nonzero unknown-tail rejection, all scope permission paths, hot-unplug `ENODEV`, invalid pointer/length handling, vendor device-type discovery, and separation between ioctl errno and device response status.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/fwctl/fwctl.h -->
