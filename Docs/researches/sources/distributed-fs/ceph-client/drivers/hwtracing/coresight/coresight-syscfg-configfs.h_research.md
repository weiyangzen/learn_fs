# sources/distributed-fs/ceph-client/drivers/hwtracing/coresight/coresight-syscfg-configfs.h

## Purpose
This header defines the configfs-facing wrapper objects and public configfs lifecycle functions for the CoreSight system configuration manager.

## Important APIs, Types, And Functions
`CSCFG_FS_SUBSYS_NAME` names the configfs subsystem `cs-syscfg`. `struct cscfg_fs_config` wraps a configuration descriptor, configfs group, active flag, and selected preset. `struct cscfg_fs_feature` wraps a feature descriptor and group. `struct cscfg_fs_param` identifies a parameter index within a feature descriptor. `struct cscfg_fs_preset` identifies a preset index within a configuration descriptor. Declared functions initialize/release configfs and add/delete config and feature groups.

## Control Flow And State
The wrapper state mirrors descriptor state into configfs item lifetimes. Config `active` and `preset` fields track the sysfs-control view exposed through configfs, while descriptor pointers remain owned by the syscfg core or the module that loaded them. Add/delete functions are called during syscfg load/unload sequences after descriptor list validation.

## Dependencies And Integration Points
The header depends on `linux/configfs.h` and `coresight-syscfg.h`. It is included by both the syscfg core and configfs implementation, forming the narrow interface between descriptor management and user-visible configfs objects.

## Risks And Test Signals
The structs embed `config_group`, so object lifetime must remain valid while configfs references exist. Descriptor ownership is external, making unload ordering important. Test signals include add/delete of configs and features with and without presets/parameters, active config toggles, and module unload while configfs entries are visible.
