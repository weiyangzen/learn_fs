# sources/distributed-fs/ceph-client/drivers/thermal/intel/intel_pch_thermal.c

## Purpose

`intel_pch_thermal.c` registers PCI PCH thermal sensors as Linux thermal zones, reads PCH temperature/trips from MMIO, and adds suspend-time cooling delay logic for S0ix reliability.

## Important APIs, Types, and Functions

`struct pch_thermal_device` stores BAR mapping, PCI device, thermal zone, and whether BIOS already enabled the sensor. `pch_thermal_get_temp()` reads WPT temperature. `intel_pch_thermal_probe()` enables PCI, maps BAR0, enables the thermal sensor if not locked, reads critical/hot trips, optionally reads ACPI passive `_PSV`, registers a board-named thermal zone, and enables it. PM callbacks disable/reenable non-BIOS sensors and delay suspend if PCH is hotter than threshold.

## Control Flow

Probe follows PCI enable/request/map, sensor enable, trip read, zone register. During noirq suspend, non-BIOS-enabled sensors are shut down; BIOS-enabled sensors during s2idle compare current temperature against the TSPM threshold and loop with sleeps until cooled, wakeup pending, or timeout. Resume reenables sensors that the driver enabled.

## State and Persistence Behavior

Driver state is per PCI device. Hardware sensor enable and trip registers persist in PCH MMIO. Module parameters `delay_timeout` and `delay_cnt` tune suspend cooling behavior.

## Dependencies and Integration Points

It depends on PCI, ACPI passive trip helpers, thermal core, PM suspend state, and many Intel PCH PCI IDs. Board IDs determine thermal-zone names.

## Risks and Test Signals

Risks include suspend delays in noirq context, unit conversion differences between raw and displayed temps, inability to enable locked sensors, no interrupts, and reliance on BIOS TSPM threshold. Test signals include probe on supported IDs, BIOS-enabled versus driver-enabled sensor paths, critical/hot/passive trips, s2idle cooling loop with wake abort, and resume re-enable.
