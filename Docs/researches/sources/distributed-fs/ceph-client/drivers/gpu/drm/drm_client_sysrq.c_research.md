# sources/distributed-fs/ceph-client/drivers/gpu/drm/drm_client_sysrq.c

## Purpose
`drm_client_sysrq.c` connects Magic SysRq key `v` to forced DRM client restore, intended to recover framebuffer console output.

## Important APIs, Types, And Functions
Under `CONFIG_MAGIC_SYSRQ`, global state includes `drm_client_sysrq_dev_list`, `drm_client_sysrq_dev_lock`, and `drm_client_sysrq_restore_work`. Public functions are `drm_client_sysrq_register()` and `drm_client_sysrq_unregister()`. The handler schedules work; the work function calls `drm_client_dev_restore(dev, true)`.

## Control Flow
Registration adds the device and registers SysRq `v` when the list transitions from empty. The SysRq handler schedules a work item. The work item locks the device list, skips powered-off devices, and performs forced restore. Unregister removes the device and unregisters the key when the list becomes empty.

## State And Persistence
State is a runtime global list of DRM devices and the registered sysrq key operation. There is no persistence beyond device lifetime.

## Dependencies And Integration Points
It integrates with Linux sysrq, workqueues, DRM device `client_sysrq_list`, switch power state, and `drm_client_dev_restore()`.

## Risks And Edge Cases
Register/unregister balance is critical; double unregister warns. Restore runs under the sysrq device mutex, so restore paths must not acquire it. Restore errors are intentionally ignored. Powered-off devices are skipped.

## Test Signals
Test first/last device key registration, handler scheduling, restore invocation, powered-off skip, and warning behavior for invalid unregister.
