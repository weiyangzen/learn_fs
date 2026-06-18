# sources/distributed-fs/ceph-client/drivers/hwtracing/coresight/coresight-syscfg.h

## Purpose
This header defines the internal and external API contract for the CoreSight system configuration manager. It declares the singleton manager state, registered-device entries, load-owner records, load-state enum, and functions used by CoreSight devices, configfs, perf, preload code, and dynamically loaded configuration modules.

## Important APIs, Types, And Functions
`enum cscfg_load_ops` distinguishes no operation, load, and unload. `struct cscfg_manager` stores the manager device, registered CoreSight devices, feature/config descriptor lists, load order, active count, configfs subsystem, sysfs active config/preset, and load state. `struct cscfg_registered_csdev` records a CoreSight device, match flags, feature-load ops, and list node. `struct cscfg_load_owner_info` records owner type and handle for dependency-aware unload. Function declarations cover initialization, preload, descriptor lookup/update, sysfs config activation, config-set load/unload, CoreSight device registration, active config enable/disable, and active sysfs config query.

## Control Flow And State
The header itself does not execute code, but the declared structures define syscfg persistence. Descriptor lists represent all loaded configuration material; `sys_active_cnt` prevents mutation while tracing uses any config; `load_order_list` enforces dependency-preserving reverse unload; and `sysfs_active_config/sysfs_active_preset` hold the single config selected for sysfs-controlled trace.

## Dependencies And Integration Points
It depends on configfs, CoreSight public device definitions, Linux device model, and `coresight-config.h` descriptor types. It is included by syscfg core, configfs support, and CoreSight source drivers that register feature support or enable active configs.

## Risks And Test Signals
Because this is an internal ABI among CoreSight modules, structure semantics must stay synchronized with `coresight-syscfg.c` and `coresight-syscfg-configfs.c`. Owner type handling must match module/preload lifecycle. Test signals are compile coverage for syscfg-enabled builds, module load/unload of config providers, and source-driver registration paths that call `cscfg_register_csdev()`.
