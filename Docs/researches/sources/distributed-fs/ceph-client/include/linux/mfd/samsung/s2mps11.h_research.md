# sources/distributed-fs/ceph-client/include/linux/mfd/samsung/s2mps11.h

## Purpose

This 198-line header maps S2MPS11 PMIC registers and regulator IDs, plus selector, enable, voltage-count, ramp, and power-hold controls.

## Important APIs, Types, and Functions

It defines `enum s2mps11_reg`, `enum s2mps11_regulators` for 38 LDOs and 10 bucks, LDO/buck/buck9 vsel masks, voltage counts for buck groups, ramp delay, `S2MPS11_CTRL1_PWRHOLD_MASK`, per-buck ramp shift and ramp-enable shifts, and PMIC enable shift.

## Control Flow

No code flow exists. Regulator code indexes the register map by rail ID, then programs enable, voltage selector, ramp, and suspend/PWREN behavior through regmap.

## State and Persistence Behavior

Voltage, enable, ramp, PWRHOLD, interrupt, status, OTP, and DVS register state persists in the PMIC.

## Dependencies and Integration Points

It integrates with Samsung MFD core, regulator framework, shared IRQ/RTC definitions, and shutdown logic through PWRHOLD.

## Risks and Edge Cases

Buck voltage counts vary by buck group; using one selector range for all bucks is wrong. The comment notes suspend enable bits are shared with S2MPS14 definitions.

## Test Signals

Regulator descriptor bounds tests, PWRHOLD shutdown tests, ramp programming checks, and compile tests for S2MPS11 regulator/IRQ/RTC code.
