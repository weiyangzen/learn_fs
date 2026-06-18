# sources/distributed-fs/ceph-client/drivers/hwtracing/coresight/coresight-cfg-preload.c

## Purpose
`coresight-cfg-preload.c` is the initialization bridge that registers built-in CoreSight feature and configuration descriptors with the system configuration manager.

## Important APIs, Types, And Functions
The file defines `preload_feats[]` and `preload_cfgs[]`, conditionally including ETMv4 descriptors such as `strobe_etm4x`, `gen_etrig_etm4x`, `afdo_etm4x`, and `pstop_etm4x`. `preload_owner` identifies the load owner as `CSCFG_OWNER_PRELOAD`. The single exported function, `cscfg_preload(void *owner_handle)`, records the owner handle and calls `cscfg_load_config_sets()`.

## Control Flow
CoreSight syscfg initialization calls `cscfg_preload()`. The function updates the owner context, then passes the null-terminated feature/config arrays into the loader. Conditional compilation keeps the arrays empty except for NULL sentinels when ETMv4 support is absent.

## State And Persistence
The persistent state is the static owner record and the static descriptor pointer arrays. Loaded runtime objects and configfs/syscfg state are owned by the syscfg subsystem after `cscfg_load_config_sets()` succeeds.

## Dependencies And Integration Points
This file depends on `coresight-cfg-preload.h` for descriptor declarations, `coresight-config.h` for descriptor types, and `coresight-syscfg.h` for the loader API and owner metadata. It integrates built-in descriptor files with the dynamic configuration-management layer.

## Risks
Any descriptor referenced here must be defined under matching Kconfig conditions; otherwise builds can fail or the preload arrays can reference unavailable symbols. Load-order issues would affect whether built-in configurations appear at CoreSight initialization.

## Test Signals
Boot-time syscfg initialization should show the preloaded configurations and features when ETMv4 is enabled, and no invalid references when ETMv4 is disabled. Failure injection around `cscfg_load_config_sets()` should propagate errors to the caller.
