# sources/distributed-fs/ceph-client/drivers/thermal/imx8mm_thermal.c

## Purpose
NXP i.MX8MM/i.MX8MP TMU driver. It registers one or two thermal zones, loads OCOTP calibration from nvmem when available, programs TMU calibration registers, enables probes, and reports temperature readings.

## Important APIs, Types, and Functions
- `struct thermal_soc_data` provides sensor count, TMU version, and get-temp callback.
- `struct tmu_sensor` binds a hardware id and zone to the parent TMU.
- `struct imx8mm_tmu` stores MMIO base, clock, SoC data, and flexible sensor array.
- `imx8mm_tmu_get_temp()` reads V1 `TRITSR` temperature0, ignores invalid V bit due to erratum, and checks range.
- `imx8mp_tmu_get_temp()` checks per-probe ready bits, reads signed V2 fields for sensor0/1, and checks range.
- `imx8mm_tmu_probe_set_calib_v1()` and `_v2()` parse nvmem calibration data and program TASR/TCALIV/TRIM registers.
- `imx8mm_tmu_probe()` maps resources, enables clock, disables monitor, registers zones, loads calibration, enables V2 probes, and enables monitor.

## Control Flow
Probe loads match data, allocates a parent struct sized for `num_sensors`, maps registers, enables the clock, disables the TMU, registers each sensor as an OF thermal zone and hwmon, then applies calibration. V1 expects a 32-bit `calib` cell. V2 reads a 16-byte cell and either applies trim fields or default 25C binary codes for blank sample hardware. V2 selects all probes before enabling the monitor. Remove disables the TMU and clock.

## State and Persistence
Driver state is MMIO base, clock, SoC descriptor, and sensor array. Calibration register values persist in hardware while powered. Thermal zone private data points to each `tmu_sensor`.

## Dependencies and Integration Points
Depends on platform MMIO, clocks, OF matching, nvmem cells, thermal OF zones, and `thermal_hwmon`. DTs without `nvmem-cells` are allowed for compatibility but produce less accurate readings.

## Risks and Edge Cases
- V1 ignores validity bit intentionally due to erratum; range checks are the only stale/invalid-sample guard.
- V2 negative handling computes magnitude for signed values but does not negate it, which should be scrutinized against hardware encoding.
- Missing calibration is nonfatal, risking inaccurate readings on old DTs.
- V2 calibration requires exactly 16 bytes; any other length fails probe.

## Test Signals
Tests should cover V1/V2 get-temp paths, ready-bit `-EAGAIN`, range rejection, no-nvmem compatibility warning, blank V2 calibration defaults, exact-length V2 calibration parsing, multi-zone registration, and clock cleanup on failures.
