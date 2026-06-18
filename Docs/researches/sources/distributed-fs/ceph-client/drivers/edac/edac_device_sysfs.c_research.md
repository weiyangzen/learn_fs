# sources/distributed-fs/ceph-client/drivers/edac/edac_device_sysfs.c

## Purpose
This file implements sysfs exposure for EDAC generic devices. It creates the controller kobject, common controller attributes, symlink to the physical device, instance directories, block directories, and optional driver-supplied attributes.

## Important APIs, Types, And Functions
Controller attributes include `log_ue`, `log_ce`, `panic_on_ue`, and `poll_msec`. Instance and block attributes expose `ce_count` and `ue_count`. Key exported lifecycle functions are `edac_device_register_sysfs_main_kobj()`, `edac_device_unregister_sysfs_main_kobj()`, `edac_device_create_sysfs()`, and `edac_device_remove_sysfs()`.

Internal helpers include `edac_device_create_instance()`, `edac_device_delete_instance()`, `edac_device_create_block()`, `edac_device_delete_block()`, `edac_device_add_main_sysfs_attributes()`, and their removal counterparts. Kobject types provide release callbacks that drop references on the main controller object.

## Control Flow
Allocation calls `edac_device_register_sysfs_main_kobj()` to create the top-level `.../edac/<name>` kobject and hold a module reference. Registration then calls `edac_device_create_sysfs()`, which creates driver-supplied main attributes, creates the `device` symlink to the parent device, and recursively creates instance and block kobjects. Removal deletes main attributes, removes the symlink, and walks the instance/block tree releasing kobjects. Final controller release calls `__edac_device_free_ctl_info()`.

## State And Persistence
Sysfs state mirrors `struct edac_device_ctl_info`, its instance array, and block array. Store operations mutate live flags such as `log_ue`, `log_ce`, `panic_on_ue`, and polling delay. Kobject reference counts tie child instance/block lifetime to the controller's main kobject and module reference.

## Dependencies And Integration Points
The file depends on `edac_device.h`, `edac_module.h`, sysfs/kobject APIs, and the EDAC bus returned by `edac_get_sysfs_subsys()`. It is invoked by `edac_device.c`; low-level drivers indirectly use it through EDAC device registration APIs.

## Risks
The `poll_msec` store path uses `simple_strtoul()` and does not enforce the comment's nonzero minimum. Partial sysfs creation paths must unwind child kobjects and attributes in order; the code does this but is sensitive to future changes. Driver-supplied block attributes are manually created and removed, so invalid attr arrays can break registration.

## Test Signals
Signals include correct top-level kobject creation, module reference release, common attribute read/write behavior, `device` symlink existence, instance/block count files, optional driver attributes, recursive cleanup on mid-creation failures, and poll delay changes reaching `edac_device_reset_delay_period()`.
