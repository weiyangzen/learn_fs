# sources/distributed-fs/ceph-client/drivers/hwtracing/coresight/coresight-tpdm.c

## Purpose

`coresight-tpdm.c` implements Qualcomm Trace, Profiling and Diagnostic Monitor devices as CoreSight sources. It discovers DSB, CMB, and MCMB datasets, exposes a large sysfs configuration surface, programs dataset registers on enable, and supports dynamic AMBA TPDM plus static platform TPDM nodes.

## Important APIs, Types, and Functions

Dataset helpers include `tpdm_has_*_dataset`, `tpdm_datasets_setup`, `static_tpdm_datasets_setup`, and `tpdm_reset_datasets`. Register programming is handled by `tpdm_enable_dsb`, `tpdm_enable_cmb`, `tpdm_disable_dsb`, and `tpdm_disable_cmb`. CoreSight source ops are `tpdm_enable` and `tpdm_disable`. Sysfs handlers manage DSB mode, edge control index/value/mask, pattern and trigger arrays, MSRs, timestamp booleans, CMB/MCMB modes, trace ID, dataset reset, and integration test writes. Probe paths are `dynamic_tpdm_probe` for AMBA and `tpdm_platform_probe` for static DT nodes.

## Control Flow

Dynamic probe maps registers, reads `CORESIGHT_PERIPHIDR0` to identify datasets, allocates `dsb_dataset` and/or `cmb_dataset`, reads optional MSR counts from DT, and registers a CoreSight TPDM source with full sysfs groups. Static probe has no MMIO resource and only registers traceid visibility, allocating dataset structs from firmware properties. Enable takes a CoreSight mode, programs DSB/CMB registers under lock unless static, records `path->trace_id`, and marks enabled. Disable clears dataset enable bits and returns the CoreSight device to disabled mode.

## State and Persistence Behavior

`tpdm_drvdata` persists dataset presence bits, allocated DSB/CMB config structs, MSR counts, enable flag, and last trace ID. Sysfs writes modify shadow dataset structures; hardware is programmed from those shadows on enable. Reset clears dataset state and restores DSB default trigger timestamp true and trigger type false. Static TPDM has no register programming but still participates as a CoreSight source for topology purposes.

## Dependencies and Integration Points

The driver depends on CoreSight source APIs, CoreSight PMU path trace IDs, AMBA/platform driver helpers, DT properties, bitfield helpers, and register constants from `coresight-tpdm.h`. TPDA consumes TPDM drvdata and firmware element-size properties to configure aggregation ports.

## Risks and Edge Cases

The sysfs surface is large and mostly writes shadow state even while enabled; changes during active tracing may not affect hardware until re-enable. Many show/store paths assume the relevant dataset pointer exists and rely on attribute visibility to prevent invalid access. MSR visibility depends on DT-provided counts. Static TPDM cannot run `integration_test` and does not expose configuration groups. Traceid reads fail until a path has enabled the source.

## Test Signals

Exercise dynamic and static probe, dataset detection for DSB/CMB/MCMB combinations, attribute visibility, MSR count limits, invalid sysfs values, reset defaults, integration test requiring enabled state, traceid after path enable, and register writes for DSB/CMB programming. Lockdep and race tests should cover sysfs writes versus enable/disable.
