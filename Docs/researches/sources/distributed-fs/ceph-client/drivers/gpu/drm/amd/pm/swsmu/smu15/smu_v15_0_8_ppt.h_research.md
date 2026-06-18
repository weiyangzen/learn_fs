# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/swsmu/smu15/smu_v15_0_8_ppt.h

## Purpose

`smu_v15_0_8_ppt.h` declares the SMU 15.0.8 power-play table surface and metrics schemas. It exposes topology limits for XGMI links, GFX clocks, XCCs, VCN/JPEG engines, AIDs/MIDs, and HBM stacks; the `PPTable_t` structure; and `smu_v15_0_8_set_ppt_funcs()` for installing ASIC-specific SMU callbacks. Under `SWSMU_CODE_LAYER_L2` it uses the common SMU metrics metaprogramming macros to declare packed GPU, GPU-board temperature, and baseboard temperature metric classes.

## Important APIs, Types, And Functions

The public type is `PPTable_t`, which caches socket power limits, graphics/fabric/GL2/UCLK/SOC/LCLK/VCN clocks, thermal/CTF limits for MID/AID/XCD/HBM, public serial numbers, PPT1 limits, and an `init` flag. The main macro APIs are `SMU_15_0_8_METRICS_FIELDS`, `SMU_15_0_8_GPUBOARD_TEMP_METRICS_FIELDS`, and `SMU_15_0_8_BASEBOARD_TEMP_METRICS_FIELDS`, each consumed by `DECLARE_SMU_METRICS_CLASS`. The metrics include temperatures, power, PCIe/XGMI counters, activity accumulators, firmware timestamps, clock arrays, JPEG/VCN busy percentages, and board/baseboard sensor fields.

## Control Flow, State, And Persistence

This header has no runtime control flow. Its generated inline class initializers zero-fill with `0xff`, encode metric attribute/unit/type metadata, set the metrics table header, and count fields. State persists only in consumers: `PPTable_t` is a driver cache, while metrics snapshots mirror firmware-owned tables and platform sensors.

## Dependencies And Integration Points

The file depends on `smu_cmn.h` and the AMDGPU metrics attribute/type/unit definitions when layer L2 is enabled. It integrates with the SMU 15.0.8 PPT implementation, sysfs/metrics export paths, power/thermal limit handling, topology-aware monitoring, and firmware table copy paths in `smu_cmn.c`.

## Risks And Test Signals

Risks are schema drift against firmware metrics layout, wrong array bounds for multi-die products, and stale `PPTable_t` defaults being treated as initialized. Tests should cover SMU 15.0.8 build coverage, metrics table size/revision checks, sensor export on multi-AID/XCC/HBM hardware, and firmware table compatibility during probe/resume.
