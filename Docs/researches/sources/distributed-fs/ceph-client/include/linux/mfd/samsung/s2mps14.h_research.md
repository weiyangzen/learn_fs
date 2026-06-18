# sources/distributed-fs/ceph-client/include/linux/mfd/samsung/s2mps14.h

## Purpose

This 134-line header defines S2MPS14 PMIC registers, regulator IDs, selector masks, enable semantics, default ramp delay, and external/suspend control encodings.

## Important APIs, Types, and Functions

It declares `enum s2mps14_reg`, `enum s2mps14_regulators` for 25 LDOs and 5 bucks, buck start selector values, ramp delay, LDO/buck vsel masks/counts, enable mask/shift, `S2MPS14_ENABLE_SUSPEND`, and `S2MPS14_ENABLE_EXT_CONTROL`.

## Control Flow

No executable flow exists. The regulator driver maps rail IDs to register controls and uses the enable mode encodings to support normal, suspend/PWREN, or external-control operation.

## State and Persistence Behavior

Regulator voltage, enable mode, discharge, WRSTBI, RTC control, interrupt, and status values persist in PMIC registers.

## Dependencies and Integration Points

It integrates with Samsung MFD core, regulator framework, shared IRQ/RTC handling, and external control pins such as LDO10EN/EMMCEN.

## Risks and Edge Cases

External-control enable value is encoded as zero in the enable field; code must not treat zero as necessarily disabled. Buck start selectors differ between BUCK4 and other bucks.

## Test Signals

Regulator mode tests for normal/suspend/external enable, selector bounds tests, and suspend-resume tests where PWREN controls rails.
