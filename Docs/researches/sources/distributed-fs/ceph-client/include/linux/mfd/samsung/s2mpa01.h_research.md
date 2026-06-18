# sources/distributed-fs/ceph-client/include/linux/mfd/samsung/s2mpa01.h

## Purpose

This 175-line header maps S2MPA01 PMIC registers, regulator IDs, voltage selector masks, enable fields, and buck ramp controls.

## Important APIs, Types, and Functions

It defines `enum s2mpa01_reg`, `enum s2mpa01_regulators` for 26 LDOs and 10 bucks, LDO/buck vsel masks and voltage counts, enable mask/shift, default ramp delay, per-buck ramp shift values, ramp enable shifts, and PMIC enable shift.

## Control Flow

No flow executes here. The S2MPA01 regulator driver indexes register enums and regulator IDs, then programs enable, voltage, and ramp fields through regmap.

## State and Persistence Behavior

Regulator voltage, enable, ramp, DVS pointer/data, OTP, status, and interrupt mask state persists in the PMIC. The header itself is compile-time ABI.

## Dependencies and Integration Points

It integrates with Samsung core, IRQ, RTC, and regulator code for S2MPA01 devices.

## Risks and Edge Cases

The large register enum includes reserved slots; drivers must not assume every entry is a usable regulator register. Ramp shift values differ by buck grouping.

## Test Signals

Regulator descriptor tests for all 36 rails, selector bounds tests, ramp-delay programming tests, and build coverage with Samsung MFD IRQ/RTC support.
