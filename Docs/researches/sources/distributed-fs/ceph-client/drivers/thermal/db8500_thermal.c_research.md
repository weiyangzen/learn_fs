# sources/distributed-fs/ceph-client/drivers/thermal/db8500_thermal.c

## Purpose
ST-Ericsson DB8500 thermal driver using PRCMU hotmon interrupts. Because no direct PRCMU temperature read API exists, it reports an interpolated pseudo-temperature between programmed low/high thresholds.

## Important APIs, Types, and Functions
- `db8500_thermal_points[]` defines stepped threshold bands from 15C to 100C.
- `struct db8500_thermal_zone` stores the zone, device, current interpolated temperature, and current threshold index.
- `db8500_thermal_update_config()` stops sensing, updates index/interpolated value, programs PRCMU low/high celsius thresholds, and restarts sensing.
- `prcmu_low_irq_handler()` and `prcmu_high_irq_handler()` move the threshold window down or up and update the thermal zone.
- Suspend/resume stop and restart sensing.

## Control Flow
Probe allocates state, requests low and high threaded IRQs by name, registers thermal OF zone id 0, and starts sensing at the lowest threshold band. Low IRQ lowers the band unless already at index 0. High IRQ raises the band until the highest point, then reports one degree above max. Each threshold movement reprograms PRCMU hotmon and notifies the thermal core.

## State and Persistence
`cur_index` and `interpolated_temp` represent the current PRCMU threshold band. PRCMU hotmon register state is external to this driver and is reset on probe/resume.

## Dependencies and Integration Points
Depends on PRCMU functions (`prcmu_config_hotmon()`, start/stop), named platform IRQs, OF thermal zone registration, and system suspend/resume callbacks.

## Risks and Edge Cases
- Temperature is approximate midpoint of threshold bands, not direct sensor data.
- IRQ handlers are threaded but do not use explicit locking around `cur_index`; PRCMU IRQ serialization is assumed.
- The highest band reports only max+1 mC, not actual high temperature.
- Critical behavior relies on DT thermal-zone trips being consistent with the fixed threshold table.

## Test Signals
Tests should drive low/high IRQs across band boundaries, verify PRCMU programming values in Celsius, suspend/resume reset behavior, OF registration failure, and no-op low IRQ at index 0.
