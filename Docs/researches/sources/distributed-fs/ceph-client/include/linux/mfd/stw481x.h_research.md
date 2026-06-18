# sources/distributed-fs/ceph-client/include/linux/mfd/stw481x.h

## Purpose

This 51-line header exposes shared STw481x PMIC register bits and parent state for ST-Ericsson/Linaro MFD children.

## Important APIs, Types, and Functions

It defines shared `STW_CONF1`, `STW_CONF2`, and `STW_VCORE_SLEEP` register addresses and masks for VMMC power/voltage, monitoring, wakeup, GPOs, and warning behavior, plus `struct stw481x` with I2C client and regmap.

## Control Flow

No code flow exists. Child drivers use the shared regmap to update shared configuration registers for regulators, MMC voltage, warning masks, and GPIO-like outputs.

## State and Persistence Behavior

Hardware persists VMMC/VAUX power-down and voltage selection, warning masks, GPO bits, and sleep voltage state. Runtime parent state holds the I2C/regmap handles.

## Dependencies and Integration Points

It integrates STw481x MFD support with I2C, regmap, regulator machine constraints, and bit operations.

## Risks and Edge Cases

Several registers are shared by more than one driver, so read-modify-write operations must preserve unrelated bits. VMMC voltage field values directly affect external card power.

## Test Signals

Regmap update-bit tests, MMC voltage selection tests, regulator child probe tests, and shared-register concurrency tests.
