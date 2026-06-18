# sources/distributed-fs/ceph-client/include/linux/mfd/samsung/s2mpu02.h

## Purpose

This 189-line header defines S2MPU02 registers, regulator IDs, voltage constraints, selector masks, suspend enable encodings, and buck ramp fields.

## Important APIs, Types, and Functions

It exports `enum S2MPU02_reg`, `enum S2MPU02_regulators` for 28 LDOs and 7 bucks, per-buck minimum voltage/step/start selector constants, LDO group voltage constants, LDO/buck vsel masks and counts, enable mask/shift, suspend enable/disable encodings, and ramp shift/mask definitions for BUCK1-4.

## Control Flow

There is no executable flow. Regulator descriptors use these constants to compute selector ranges and program voltage, enable, suspend, and ramp fields.

## State and Persistence Behavior

PMIC registers persist regulator control, DVS, warm reset, interrupt, status, and ramp state. Driver-owned state is elsewhere.

## Dependencies and Integration Points

It integrates with Samsung MFD core, regulator framework, and shared IRQ/RTC support for S2MPU02.

## Risks and Edge Cases

Voltage ranges vary significantly by buck and LDO group. `S2MPU02_DISABLE_SUSPEND` encodes `0x11 << 6`, which exceeds an 8-bit field if treated naively; consumers need to match existing driver semantics.

## Test Signals

Regulator conversion tests per buck/LDO group, suspend enable tests, ramp field tests, and build coverage for S2MPU02 boards.
