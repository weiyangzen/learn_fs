# sources/distributed-fs/ceph-client/include/linux/mfd/samsung/s2mpg11.h

## Purpose

This 434-line header defines S2MPG11 common, PMIC, meter, external-control, and regulator identifiers for another Samsung PMIC generation.

## Important APIs, Types, and Functions

It defines common registers and interrupt source masks, PMIC registers for interrupts/status, buck/buckboost/LDO controls, ultrasonic modes, DVS, sequencing, GPIO, OCP, PIF, and fault output, PCTRLSEL values for PWREN/MIF/AP/G3D/AOC/UFS controls, meter registers with power and NTC warning/filter data, and regulator IDs for buckboost, 10 bucks, BUCKD, BUCKA, and 15 LDOs.

## Control Flow

The header has no executable flow. Variant-specific Samsung MFD and regulator code use its register maps to configure rail state, sequencing, interrupts, and monitoring.

## State and Persistence Behavior

State persists in PMIC registers for rail configuration, external controls, IRQs, sequencing, OCP, NTC and power-meter samples, and fault output.

## Dependencies and Integration Points

It integrates with Samsung core and IRQ headers, regulator drivers, meter/thermal warning consumers, and GPIO/external power-control logic.

## Risks and Edge Cases

The register enum deliberately skips holes; assuming contiguous hardware at commented gaps is unsafe. S2MPG11 regulator and IRQ names differ from S2MPG10 despite similar structure.

## Test Signals

Variant probe tests, regulator ID count validation, meter/NTC warning register tests, IRQ mask mapping tests, and external-control selector validation on supported boards.
