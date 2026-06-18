# sources/distributed-fs/ceph-client/include/linux/mfd/samsung/s2mps13.h

## Purpose

This 177-line header defines S2MPS13 PMIC register and regulator IDs, default ramp behavior, and warm-reset control mask.

## Important APIs, Types, and Functions

It exports `enum s2mps13_reg`, `enum s2mps13_regulators` for 40 LDOs, 10 bucks, and a buckboost rail, plus `S2MPS13_BUCK_RAMP_DELAY` and `S2MPS13_REG_WRSTBI_MASK`.

## Control Flow

No local flow exists. Regulator code uses rail IDs and register offsets to configure buck/LDO outputs, while core code can control WRSTBI behavior using the mask.

## State and Persistence Behavior

Regulator output, ramp, LDO DVS/discharge, WRSTBI, interrupt, status, and control state persist in PMIC registers.

## Dependencies and Integration Points

It integrates with Samsung MFD core, regulator descriptors, shared IRQ definitions, and reset/warm-reset policy.

## Risks and Edge Cases

The file documents that datasheet ramp-control register details are unclear, so drivers rely on a default ramp delay. Changing that assumption should be validated on hardware.

## Test Signals

Regulator table size tests, default-ramp behavior checks, WRSTBI mask tests, and hardware voltage-transition measurements where available.
