# sources/distributed-fs/ceph-client/drivers/hwtracing/coresight/coresight-syscfg.c

## Purpose
This file implements the global CoreSight system configuration manager. It loads feature and configuration descriptors, attaches matching features/configs to registered CoreSight devices, exposes descriptors through perf and configfs, handles dynamic load/unload ordering, and manages activation counts for perf and sysfs-controlled trace sessions.

## Important APIs, Types, And Functions
Public APIs include `cscfg_load_config_sets()`, `cscfg_unload_config_sets()`, `cscfg_register_csdev()`, `cscfg_unregister_csdev()`, `cscfg_activate_config()`, `cscfg_deactivate_config()`, `cscfg_csdev_enable_active_config()`, `cscfg_csdev_disable_active_config()`, `cscfg_update_feat_param_val()`, `cscfg_config_sysfs_activate()`, and `cscfg_config_sysfs_get_active_cfg()`. Internally, `cscfg_load_feat_csdev()` creates per-device feature instances, `cscfg_add_csdev_cfg()` creates per-device config instances when features match, and `cscfg_owner_get/put()` pins module owners while active or while later loads depend on earlier ones.

## Control Flow And State
`cscfg_mgr` is a singleton protected by `cscfg_mutex`. It owns lists of registered devices, feature descriptors, config descriptors, load owners, global active count, configfs subsystem, sysfs active config hash/preset, and a load state. Loading is serialized by `load_state`: features load first, configs validate feature references, per-device instances are attached, perf symlinks are created, owner dependency is recorded, configfs entries are registered outside the mutex, and configs become available only at the end. Unload is allowed only when nothing is active and the owner is the last loaded. Activation increments descriptor and global counts and pins owners; per-device enable finds a matching active config, programs feature values with `cscfg_csdev_enable_config()`, and records `active_cscfg_ctxt`.

## Dependencies And Integration Points
This file depends on descriptor operations in `coresight-config.h`, perf integration in `coresight-etm-perf.h`, configfs helpers, module refcounting, CoreSight device feature/config lists, and device-managed allocation on each CoreSight component.

## Risks And Test Signals
The manager mixes mutex-protected global lists with per-device raw spinlocks. Ordering is critical around configfs operations, load/unload serialization, and active config enable racing with disable. Error unwinds must remove partially loaded descriptors, perf symlinks, configfs entries, and owner-list pins. Test signals include duplicate feature/config names, missing feature references, dynamic module load/unload in reverse order, unload rejection while active, parameter writes while active, sysfs single-active enforcement, perf multiple active configs, and device registration after descriptors are already loaded.
