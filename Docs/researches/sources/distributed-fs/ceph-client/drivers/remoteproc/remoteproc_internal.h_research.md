# sources/distributed-fs/ceph-client/drivers/remoteproc/remoteproc_internal.h

## Purpose
Declares private cross-file remoteproc interfaces and inline dispatch helpers shared by core, sysfs/debugfs, coredump, ELF loader, virtio transport, and platform drivers.

## Important APIs, Types, And Functions
Defines `struct rproc_debug_trace` for trace debugfs state and `struct rproc_vdev_data` for passing vdev resource data to the `rproc-virtio` platform driver. Declares core, virtio, debugfs, sysfs, cdev, vring, ELF, carveout, and rvdev helpers. Inline wrappers dispatch optional `rproc_ops` hooks: prepare, unprepare, attach, sanity_check, get_boot_addr, load, parse_fw, handle_rsc, find_loaded_rsc_table, and get_loaded_rsc_table. It also provides feature-bit helpers and `rproc_u64_fit_in_size_t()`.

## Control Flow
Most wrappers return success or neutral values when a platform callback is absent; `rproc_load_segments()` returns `-EINVAL` when no loader exists. Core code uses these wrappers so lifecycle logic can stay independent of optional platform hooks.

## State And Persistence Behavior
The header keeps no global state. It reads or mutates `rproc->features` and calls function pointers stored in the copied `rproc->ops` table.

## Dependencies And Integration Points
It is the local contract among implementation files under `drivers/remoteproc`. It hides optional `CONFIG_REMOTEPROC_CDEV` behind no-op stubs when disabled and ties together resource parsing, debugfs trace files, sysfs class registration, virtio vring handling, and ELF defaults.

## Risks
Silent no-op wrappers make it important that platform drivers know which callbacks are truly optional for their mode. Attach validation is enforced elsewhere by `rproc_validate()`. The declaration of `rproc_release(struct kref *)` appears stale relative to the current device-model release path, so new code should follow actual lifetime APIs.

## Test Signals
Build configurations with and without `CONFIG_REMOTEPROC_CDEV`, default ELF platforms, custom loader platforms, attach-only platforms, vendor resource handlers, and feature-bit bounds checking through `rproc_set_feature()`.
