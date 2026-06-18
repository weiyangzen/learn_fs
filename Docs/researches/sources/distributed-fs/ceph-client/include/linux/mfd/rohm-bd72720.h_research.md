# sources/distributed-fs/ceph-client/include/linux/mfd/rohm-bd72720.h

## Purpose

This 634-line header is the complete public register and IRQ map for the ROHM BD72720 PMIC. It spans regulator rails, GPIOs, RTC, power-state logic, charger, voltage monitor, coulomb counter, alarm, and interrupt status/source/mask registers across two I2C slave addresses.

## Important APIs, Types, and Functions

The file defines regulator IDs for 11 bucks and 11 LDOs, a large IRQ enum beginning with GPIO parent IRQs for device-tree xlate convenience, interrupt bit masks, common-register addresses behind I2C address `0x4b`, charger/monitor/counter registers behind address `0x4c` using `BD72720_I2C4C_ADDR_OFFSET`, GPIO IRQ type and drive masks, DVS state enable masks, voltage selector masks, RTC range markers, and detection bits such as `BD72720_MASK_DCIN_DET`.

## Control Flow

There is no local code flow. The MFD core and child drivers use the register enum as a logical address space and let regmap translate accesses. Interrupt handling follows the documented `_STAT` versus `_SRC` split: `_STAT` reports and acknowledges line events, while `_SRC` reflects current functional state.

## State and Persistence Behavior

All state is hardware-backed: DVS rail selections, GPIO modes, RTC time/alarm values, charger state, sampled voltage/current/coulomb data, interrupt enable/status/source fields, and alarm thresholds. The artificial `0x100` offset prevents address collisions between the two physical I2C register banks in one logical map.

## Dependencies and Integration Points

It includes `regmap.h` and integrates with ROHM MFD core probing, regulator DVS tables, GPIO/IRQ-controller child devices, RTC support, power-supply/charger code, fuel-gauge-like monitoring, and device-tree interrupt consumers attached to PMIC GPIO inputs.

## Risks and Edge Cases

The first two IRQ numbers are intentionally GPIO inputs, not register-order IRQs; changing this order would break device-tree consumers. Confusing `_STAT` and `_SRC` can either fail to ack IRQs or report stale functional state. Register offset handling must be consistent or charger-bank operations will hit common-bank registers.

## Test Signals

Compile coverage for all BD72720 children, IRQ domain xlate tests for GPIO1/GPIO2, regmap range tests for the `0x4c` offset, RTC alarm smoke tests, charger/power-supply property checks, and hardware tests for DVS and GPIO interrupt polarity programming.
