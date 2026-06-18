<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/fwctl.h -->
# sources/distributed-fs/ceph-client/include/linux/fwctl.h

Purpose: Defines the kernel driver API for `fwctl`, a character-device framework that exposes controlled firmware RPC/info interfaces to userspace.

Important APIs/types/functions: `fwctl_ops` carries the UAPI `device_type`, user context allocation size, context open/close callbacks, `info()` implementation, and `fw_rpc()` implementation. `fwctl_device` embeds a sysfs `device`, `cdev`, user-context list, registration lock, and ops pointer. `fwctl_uctx` is the per-file-descriptor context. Allocation/lifetime helpers are `_fwctl_alloc_device()`, `fwctl_alloc_device()`, `fwctl_get()`, `fwctl_put()`, `DEFINE_FREE(fwctl, ...)`, `fwctl_register()`, and `fwctl_unregister()`.

Control flow: Drivers allocate an embedding struct with `fwctl_alloc_device()`, register it, and provide ops. Opening a char device allocates a `fwctl_uctx`, calls `open_uctx()`, then ioctl paths call `info()` or `fw_rpc()`. Unregister clears ops under a write lock and waits for in-flight read-locked operations.

State and persistence behavior: State is runtime-only: device references, cdev registration, user contexts linked under `uctx_list_lock`, and driver-private bytes trailing the base structs.

Dependencies and integration points: Depends on device core, cdev, cleanup helpers, rw semaphores, mutex/list infrastructure, and `uapi/fwctl/fwctl.h`. Integrates with hot unplug and module unload through `fwctl_unregister()`.

Risks: Driver ops must not run indefinitely because unregister waits for them. `fw_rpc()` memory ownership is subtle: returned response may alias input or be freed with `kvfree()`. The allocation macro requires the `fwctl_device` member at offset zero.

Test signals: Open/close lifecycle tests, concurrent ioctl versus unregister, hot unplug while RPCs run, info buffer sizing/copy tests, invalid device type/scope handling, and KASAN/lockdep around context list management.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/fwctl.h -->
