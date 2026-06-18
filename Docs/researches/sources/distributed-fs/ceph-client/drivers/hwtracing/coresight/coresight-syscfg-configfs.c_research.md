# sources/distributed-fs/ceph-client/drivers/hwtracing/coresight/coresight-syscfg-configfs.c

## Purpose
This file projects the CoreSight system configuration manager into configfs. It creates a `cs-syscfg` subsystem with `configurations` and `features` groups, exposes loaded configuration descriptors, presets, feature metadata, and mutable feature parameters, and forwards activation/parameter changes to the syscfg core.

## Important APIs, Types, And Functions
Configuration attributes include read-only `description`, read-only `feature_refs`, read/write `enable`, and read/write `preset`. Preset groups expose `values`. Feature attributes include `description`, `matches`, and `nr_params`. Per-parameter groups expose a `value` attribute. Public entry points are `cscfg_configfs_init()`, `cscfg_configfs_release()`, `cscfg_configfs_add_config()`, `cscfg_configfs_add_feature()`, `cscfg_configfs_del_config()`, and `cscfg_configfs_del_feature()`.

## Control Flow And State
Initialization allocates a config item type from `cscfg_device()`, names the subsystem `cs-syscfg`, initializes default `configurations` and `features` groups, and registers the subsystem. Adding a config allocates a `cscfg_fs_config`, initializes its config group, creates default `presetN` groups, registers it under `configurations`, and stores the group pointer in the descriptor. Enabling a config parses a boolean, calls `cscfg_config_sysfs_activate()`, records local active state, and updates the sysfs preset if enabling. Parameter writes parse `u64` and call `cscfg_update_feat_param_val()`.

## Dependencies And Integration Points
This file depends on configfs, descriptor types from `coresight-config.h`, wrappers from `coresight-syscfg-configfs.h`, and syscfg core APIs for activation, preset, feature lookup, and parameter update. Its allocations are devm-managed against the syscfg manager device.

## Risks And Test Signals
Configfs locking is intentionally separated from syscfg list locking by the core; changes here can reintroduce lock inversion. `cscfg_cfg_values_show()` assumes `cscfg_get_named_feat_desc()` succeeds for all feature refs, which relies on core validation and load ordering. Preset numbers are 1-based and must remain consistent with descriptor arrays. Test signals include mounting configfs, loading/unloading config sets, enabling one config and rejecting a second active sysfs config, invalid preset writes, parameter writes while active returning `-EBUSY`, and configfs removal on unload.
