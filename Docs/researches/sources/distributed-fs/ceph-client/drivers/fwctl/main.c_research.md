# sources/distributed-fs/ceph-client/drivers/fwctl/main.c

## Purpose
`fwctl/main.c` implements the fwctl character-device core. It provides `/dev/fwctl/fwctlN` devices, per-file user contexts owned by provider drivers, ioctl dispatch for info and firmware RPC commands, lifetime disassociation on unregister, and global tainting for write-capable debug access.

## Important APIs, Types, and Functions
Important internal types are `struct fwctl_ucmd` and `struct fwctl_ioctl_op`. Public provider APIs are `_fwctl_alloc_device()`, `fwctl_register()`, and `fwctl_unregister()`. File operations are `fwctl_fops_open()`, `fwctl_fops_release()`, and `fwctl_fops_ioctl()`. Command handlers are `fwctl_cmd_info()` and `fwctl_cmd_rpc()`. Helpers include `ucmd_respond()` and `copy_to_user_zero_pad()`.

## Control Flow
Subsystem init allocates up to 4096 character minors and registers class `fwctl` with devnodes under `fwctl/`. Providers allocate devices through the wrapper around `_fwctl_alloc_device()`, which allocates a class device, cdev, locks, and a list of open contexts. `fwctl_register()` publishes the cdev.

Open takes `registration_lock` for reading, rejects unregistered devices, allocates the provider-defined `uctx_size`, calls `ops->open_uctx()`, adds the context to the device list, takes a device reference, and stores it in `filp->private_data`. Ioctl dispatch validates the ioctl number, user-provided struct size, and minimum trailing field through `copy_struct_from_user()`, then executes under the registration read lock. Info optionally calls provider `info()`, copies provider data to the user buffer with zero padding, and returns device type plus actual length. RPC enforces a 2 MiB input and output cap, maps fwctl scopes, requires `CAP_SYS_RAWIO` for `FWCTL_RPC_DEBUG_WRITE_FULL`, taints the kernel for debug write scopes, copies input, calls provider `fw_rpc()`, copies output, and returns actual output length.

Unregister deletes the cdev, takes the write lock, destroys all open user contexts by calling provider `close_uctx()`, then sets `ops = NULL` so remaining file descriptors return `-ENODEV`. Release only calls provider close if unregister has not already done so.

## State and Persistence
State is volatile: IDA minor allocation, class device lifetime, open-context list, locks, and a global `fwctl_tainted` bit used to emit one warning and add `TAINT_FWCTL`. No firmware messages are persisted by the core.

## Dependencies and Integration Points
The core depends on fwctl uapi structs, cdev/class infrastructure, `copy_struct_from_user()`, `cleanup.h` scoped guards, kernel capabilities, and module namespace exports. Provider drivers supply `struct fwctl_ops`.

## Risks and Test Signals
The core is the lifetime and policy boundary. Provider `fw_rpc()` may return the input buffer as output, and the core must avoid double-freeing by nulling `inbuf`; this path is present and should be tested. Pointer arithmetic on `void __user *` in zero padding relies on compiler extension accepted by the kernel. Tests should cover ioctl struct size compatibility, zero padding for short provider info, all scope permission paths, `MAX_RPC_LEN` rejection, provider output shorter and longer than requested, unregister with open fds, and release after unregister.
