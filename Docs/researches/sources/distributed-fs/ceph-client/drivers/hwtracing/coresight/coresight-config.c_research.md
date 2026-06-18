# sources/distributed-fs/ceph-client/drivers/hwtracing/coresight/coresight-config.c

## Purpose
`coresight-config.c` implements generic per-device programming helpers for CoreSight system configurations and features. It translates descriptor values and user/preset parameters into driver-owned register storage when a configuration is enabled, and saves selected register values when disabled.

## Important APIs, Types, And Functions
`cscfg_set_reg()` writes a configured register value to a driver storage location, supporting 64-bit values and 32-bit masked updates. `cscfg_save_reg()` copies driver storage back into a descriptor instance for registers marked `CS_CFG_REG_TYPE_VAL_SAVE`. `cscfg_init_reg_param()` binds a feature parameter to the register instance it controls and initializes the register from the parameter value.

`cscfg_reset_feat()` restores feature parameter and register instances from static descriptors. `cscfg_update_presets()` maps a selected preset row across the ordered feature parameter list. `cscfg_update_curr_params()` updates parameter-backed registers from current per-device parameter values. The public APIs are `cscfg_csdev_enable_config()` and `cscfg_csdev_disable_config()`.

## Control Flow
Feature load code elsewhere creates `cscfg_feature_csdev` and `cscfg_config_csdev` objects with pointers into driver register storage. On enable, `cscfg_csdev_enable_config()` either applies a preset or current parameter values, then calls `cscfg_prog_config(..., true)`. That iterates all features in the config and calls `cscfg_set_on_enable()`, which takes the device driver spinlock and copies all register values into driver storage. On disable, `cscfg_csdev_disable_config()` calls `cscfg_save_on_disable()` for each feature to preserve marked values.

## State And Persistence
The file does not allocate global state. It mutates runtime feature/config instances and the target driver register storage they reference. Parameter current values persist in `cscfg_parameter_csdev`; saved register values persist in each `cscfg_regval_csdev.reg_desc` for later inspection or re-enable.

## Dependencies And Integration Points
This file depends on `coresight-config.h` for data structures and `coresight-priv.h` for device context. It is generic infrastructure used by device-specific feature loaders, especially ETMv4 configuration support. Locking is delegated to each feature instance through `feat_csdev->drv_spinlock`.

## Risks
The generic code trusts earlier load-time validation for parameter indexes and driver register pointers. Bad descriptors can write through invalid pointers or apply 32-bit values to 64-bit storage. Preset ordering is positional across feature parameters, so changing feature order or parameter count without updating `nr_total_params` and preset arrays will silently misconfigure hardware. Lock coverage protects driver storage but not broader config activation policy.

## Test Signals
Unit-style tests should cover masked writes, 64-bit writes, saved registers, parameter binding, preset bounds, no-preset current parameters, and multi-feature parameter ordering. Integration tests should activate AFDO/panicstop configurations and verify resulting ETMv4 programmed state.
