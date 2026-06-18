# sources/distributed-fs/ceph-client/drivers/hwtracing/coresight/coresight-etm4x-cfg.c

## Purpose

This file connects ETMv4 devices to the generic CoreSight system configuration framework. It validates configuration feature register offsets and maps each allowed hardware register offset to the corresponding field inside `struct etmv4_config`.

## Important APIs, Types, and Functions

- `CHECKREG()` and `CHECKREGIDX()` assign `cscfg_regval_csdev::driver_regval` to scalar or indexed fields in `struct etmv4_config`.
- `etm4_cfg_map_reg_offset()` is the whitelist and mapper for trace-capture configuration registers.
- `etm4_cfg_load_feature()` sets the feature's `drv_spinlock` to the ETM driver lock and maps every register descriptor in the feature to a driver config field.
- `etm4_cscfg_register()` registers the ETM4 CoreSight device with ETM4 source match flags.

## Control Flow

During ETM4 device registration, `coresight-etm4x-core.c` calls `etm4_cscfg_register()`. The CoreSight syscfg framework later calls `etm4_cfg_load_feature()` for matching features. For each feature register descriptor, the loader extracts the offset and resolves it to driver config storage. Invalid offsets return `-EINVAL` and fail feature loading.

## State and Persistence

This file does not allocate persistent state itself. It mutates `struct cscfg_feature_csdev` records by setting their lock pointer and per-register `driver_regval` pointers. The pointed-to values live in `drvdata->config` and are later programmed by normal ETM4 enable paths.

## Dependencies, Risks, and Test Signals

It depends on ETM4 register macros and config definitions, CoreSight syscfg APIs, and generic config descriptors. Offset matching uses masks and index arithmetic, so mistakes can map to wrong array elements. Tests should register syscfg features covering scalar registers, indexed counters, address comparators, context/VMID comparators, and invalid offsets.
