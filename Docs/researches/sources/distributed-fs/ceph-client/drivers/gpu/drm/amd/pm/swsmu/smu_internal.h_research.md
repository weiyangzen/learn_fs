# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/swsmu/smu_internal.h

## Purpose

`smu_internal.h` defines layer-L1 convenience wrappers around `smu->ppt_funcs`. It lets higher-level SMU code call ASIC-specific hooks through consistent macro names while providing default returns when a hook or function table is absent.

## Important APIs, Types, And Functions

The core macro is `smu_ppt_funcs(intf, ret, smu, args...)`, which returns `-EINVAL` if `ppt_funcs` is missing, calls the hook if present, or returns the supplied default. Wrappers cover microcode/table/power initialization, PPT setup/write, feature masks, GFXOFF, SMC sensors, display config, BTC, watermarks, thermal alerts, performance levels, PCIe parameters, power source, I2C, IDs, thermal throttling logs, fan/config table hooks, WBRF hooks, UCLK shadowing, and RAS SMU-driver extraction.

## Control Flow, State, And Persistence

The macros are call-through dispatch only. They do not store state, but they gate access to persistent SMU/firmware and driver state owned by the invoked PPT implementation. Default return values are part of the behavior: some missing hooks are benign `0`, while unsupported data paths return `-EINVAL`, `-EOPNOTSUPP`, or `false`.

## Dependencies And Integration Points

It includes `amdgpu_smu.h` and is compiled only for `SWSMU_CODE_LAYER_L1`. It integrates with all ASIC PPT implementations through `struct pptable_funcs`, and with SMU initialization, display, power, thermal, feature, metrics, and RAS plumbing.

## Risks And Test Signals

Risks are silent success defaults masking absent required hooks, wrong default error codes changing caller fallback, and macro type errors being harder to inspect than functions. Test signals include build coverage across ASIC PPTs, probe paths on ASICs with partial hook tables, feature/sysfs operations for missing hooks, and runtime checks that required hooks are installed before use.
