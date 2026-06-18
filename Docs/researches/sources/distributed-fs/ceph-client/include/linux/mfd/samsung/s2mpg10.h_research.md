# sources/distributed-fs/ceph-client/include/linux/mfd/samsung/s2mpg10.h

## Purpose

This 478-line header defines S2MPG10 common, PMIC, power-meter, external-control, and regulator identifier maps for a modern Samsung PMIC.

## Important APIs, Types, and Functions

It exports common-register and interrupt-source definitions, a large PMIC register enum covering interrupts, status, buck/LDO controls, ultrasonic mode, discharge, ramp, DVS sync, sequencing, GPIO, OCP, PIF, fault output, and LDO sense registers; PCTRLSEL external-control encodings; meter registers for accumulation/filter/power warning data; and regulator IDs for 10 bucks and 31 LDOs.

## Control Flow

No executable flow exists. The MFD core addresses typed register windows, regulator code consumes control/output registers and external-control selectors, and monitoring code reads meter/accumulator registers.

## State and Persistence Behavior

Hardware state includes interrupt masks/status, rail voltages, external control source selection, DVS sequencing, GPIO configuration, power meter accumulators, OCP warning thresholds, and fault output settings.

## Dependencies and Integration Points

It integrates Samsung MFD, regulator, interrupt, power-meter/hwmon-like monitoring, GPIO, and sequencing support. It also pairs with `samsung/irq.h` for S2MPG10 IRQ names.

## Risks and Edge Cases

The PMIC has multiple logical register types; mixing common, PMIC, and meter spaces will target the wrong hardware area. External-control selector values are rail-specific, especially LDO20M.

## Test Signals

Compile coverage, regulator table size checks against `S2MPG10_REGULATOR_MAX`, meter register read tests, IRQ source routing tests, and external-control mode tests for PCTRLSEL/DCTRLSEL rails.
