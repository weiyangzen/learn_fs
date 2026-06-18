# sources/distributed-fs/ceph-client/include/linux/mfd/rohm-bd718x7.h

## Purpose

This 313-line header is the shared register, regulator, voltage, reset, and interrupt contract for ROHM BD71837/BD71847 PMIC family support. Regulator, RTC, power-key, IRQ, and poweroff drivers include it so numeric register addresses and bit masks stay aligned with the chip datasheet.

## Important APIs, Types, and Functions

It defines `BD718XX_BUCK1` through `BD718XX_LDO7`, `BD718XX_REGULATOR_AMOUNT`, BD71837-only register aliases, common `BD718XX_REG_*` addresses, voltage selector counts, regulator enable/vsel/ramp masks, voltage-monitor masks, IRQ IDs, software reset settings, poweroff transition values, and power-button timing enums. There are no functions.

## Control Flow

No executable flow lives here. Runtime flow is table-driven: child drivers choose a regulator or IRQ enum, then use regmap writes/updates against these addresses and masks. Poweroff and reset code writes transition and reset fields using the protected mask values.

## State and Persistence Behavior

The file owns no storage. The represented state persists in PMIC registers, including OTP revision, reset source, power state, voltage selectors, monitor enables, interrupt latches, and lock bits. `REGLOCK_*` definitions are safety-critical because they gate writes to power sequence and regulator fields.

## Dependencies and Integration Points

It includes `rohm-generic.h` and `regmap.h`. Integration points are the ROHM MFD core, regulator framework, power/reset paths, regmap IRQ setup, and device-tree-configured DVS levels.

## Risks and Edge Cases

Variant-specific BD71837 and BD71847 definitions are interleaved; using a BD71837-only register on BD71847, or vice versa, would silently program the wrong address. Reset writes are especially risky because the comment explains bit 0 triggers reset and must not be copied from a read-modify-write source value.

## Test Signals

Build coverage for BD718xx MFD/regulator/RTC/poweroff drivers, regmap field tests for enable/vsel/ramp masks, IRQ mask-to-enum validation, and board boot/suspend/power-key tests that verify no unintended reset or regulator lock behavior.
