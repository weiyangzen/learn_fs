# sources/distributed-fs/ceph-client/drivers/thermal/imx91_thermal.c

## Purpose
NXP i.MX91 TMU driver. It initializes trim, clock divider, power-up delay, resolution, periodic measurement mode, runtime PM, a thermal zone with hardware trip programming, and a threaded threshold IRQ.

## Important APIs, Types, and Functions
- `struct imx91_tmu` stores MMIO base, clock, device, and thermal zone.
- `imx91_tmu_start()` and `imx91_tmu_enable()` control measurement start/stop and module enable through set/clear aliases.
- `imx91_tmu_to_mcelsius()` and `_from_mcelsius()` convert fixed-point 1/64C register units.
- `imx91_tmu_get_temp()` reads signed 16-bit `DATA0`.
- `imx91_tmu_set_trips()` programs comparator threshold 1 for the high trip and enables its interrupt.
- `imx91_init_from_nvmem_cells()` reads `trim1` and `trim2`; probe falls back to defaults if absent/invalid.
- IRQ top half checks `THR1_IF`, clears/disables it, and wakes the thread; thread updates the thermal zone.
- Runtime PM callbacks disable/enable the TMU and clock.

## Control Flow
Probe maps registers, gets/enables clock, disables and stops the TMU, loads trim or default trim, computes a divider for a 4 MHz conversion clock, programs power-up delay, resolution, periodic measurement mode, and 25 Hz period, enables the TMU, installs a cleanup action, enables runtime PM, registers the thermal zone and hwmon, requests the IRQ, and runtime-suspends the device. Thermal mode changes acquire/release runtime PM, configure threshold mode as greater-or-equal, and start/stop measurements. `set_trips()` disables threshold IRQ, writes the high threshold, clears stale flag, and re-enables the IRQ.

## State and Persistence
State is MMIO/clock/device/zone pointers and runtime PM usage count. Hardware trim, divider, period, resolution, threshold, and interrupt bits persist while powered.

## Dependencies and Integration Points
Depends on nvmem, clocks, runtime PM, platform IRQ, thermal OF zone callbacks (`get_temp`, `change_mode`, `set_trips`), and hwmon sysfs.

## Risks and Edge Cases
- `set_trips()` rejects `high >= 125000`; callers passing `INT_MAX` to disable high trips will get `-EINVAL`.
- Clock divider computation assumes rate at least 4 MHz; lower rates can underflow unsigned `div`.
- Fallback trim values permit operation but may reduce accuracy.
- IRQ remains disabled after firing until thermal core calls `set_trips()` again.
- Runtime PM get/put balance depends on thermal mode transitions.

## Test Signals
Tests should verify trim nvmem and fallback paths, divider boundary values, temperature conversion for negative and positive 16-bit values, `set_trips()` programming and high-limit rejection, IRQ top/thread behavior, runtime suspend/resume, and mode enable/disable PM balance.
