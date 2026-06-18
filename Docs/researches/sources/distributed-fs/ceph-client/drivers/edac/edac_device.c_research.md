# sources/distributed-fs/ceph-client/drivers/edac/edac_device.c

## Purpose
This file implements the EDAC generic device core for non-memory-controller error domains such as caches, CPU interfaces, fabrics, DMA engines, and other ECC-capable blocks. It manages allocation, global registration, polling work, sysfs lifecycle, CE/UE counter propagation, and newer EDAC RAS feature device registration.

## Important APIs, Types, And Functions
Global state is `device_ctls_mutex` plus `edac_device_list`. Allocation and lifecycle APIs are `edac_device_alloc_ctl_info()`, `edac_device_free_ctl_info()`, `edac_device_add_device()`, `edac_device_del_device()`, and `edac_device_alloc_index()`. Error reporting APIs are `edac_device_handle_ce_count()` and `edac_device_handle_ue_count()`, with inline single-error wrappers declared in the header.

Polling is handled by `edac_device_workq_function()`, `edac_device_workq_setup()`, `edac_device_workq_teardown()`, and `edac_device_reset_delay_period()`. `edac_dev_register()` registers modern EDAC RAS feature devices with scrub, ECS, and memory-repair attribute groups.

## Control Flow
`edac_device_alloc_ctl_info()` allocates the controller, instances, blocks, optional private data, initializes names/counters/default logging, marks `OP_ALLOC`, and creates the main sysfs kobject. `edac_device_add_device()` locks the global list, inserts by unique `dev_idx`, records start time, creates sysfs instance/block hierarchy, and either starts delayed polling work or marks interrupt mode. `edac_device_del_device()` finds by parent device, marks offline, removes it from the RCU-protected list, tears down work, removes sysfs, and returns the control structure to the caller for freeing.

Error handlers validate instance/block indexes, update block, instance, and controller counters, log CE/UE messages according to per-device flags, and panic on UE if configured. `edac_dev_register()` builds an independent sysfs device under the EDAC bus for RAS feature controls by gathering attribute groups from scrub/ECS/mem-repair descriptor helpers.

## State And Persistence
The global list is protected by a mutex and RCU deletion synchronization. Each EDAC device keeps counters at block, instance, and controller levels. Poll scheduling state lives in `delayed_work`, `poll_msec`, and `delay`. Sysfs object lifetime is reference-counted through kobjects and module references. Feature devices store private provider context in `struct edac_dev_feat_ctx` and free it through a device release callback.

## Dependencies And Integration Points
The file depends on `edac_device.h`, `edac_module.h`, workqueue helpers, sysfs functions implemented in `edac_device_sysfs.c`, and RAS feature descriptor helpers such as `edac_scrub_get_desc()`, `edac_ecs_get_desc()`, and `edac_mem_repair_get_desc()`. Hardware drivers call its APIs to expose non-MC error domains.

## Risks
Index uniqueness is delegated to callers unless they use `edac_device_alloc_index()`. `edac_device_reset_delay_period()` does not reject zero even though the sysfs comment says nonzero, so invalid poll periods should be considered. Error reporting drops invalid instance/block events after logging an internal error. RAS feature registration has multi-stage allocation paths that must unwind correctly on descriptor failure.

## Test Signals
Tests should validate allocation/free under failures, duplicate `dev_idx` and duplicate device rejection, poll work start/stop, sysfs hierarchy creation/removal, CE/UE counter propagation, panic-on-UE configuration, RAS feature attr-group accounting, and RCU-safe removal while readers might traverse the list.
