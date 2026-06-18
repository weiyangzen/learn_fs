# sources/distributed-fs/ceph-client/include/linux/mfd/samsung/s2mps15.h

## Purpose

This 149-line header maps S2MPS15 registers and regulator IDs and provides common selector and enable field definitions.

## Important APIs, Types, and Functions

It exports `enum s2mps15_reg`, `enum s2mps15_regulators` for 27 LDOs and 11 bucks, LDO/buck vsel masks, enable shift/mask, and selector counts for LDO and buck rails.

## Control Flow

No flow executes. The S2MPS15 regulator driver uses these IDs and masks to configure rail voltage and enable state through regmap.

## State and Persistence Behavior

PMIC hardware stores interrupt, status, buck/LDO control, buckboost, ramp, LDO DVS, and discharge state. The header is compile-time layout state.

## Dependencies and Integration Points

It integrates Samsung MFD core, regulator framework, and shared IRQ/RTC definitions for S2MPS15 devices.

## Risks and Edge Cases

Buckboost registers are present in the register enum but not a separately named regulator ID here. Selector ranges are generic and still need per-rail descriptor constraints.

## Test Signals

Regulator ID count checks, selector range tests, probe/build coverage, and board voltage enable/disable smoke tests.
