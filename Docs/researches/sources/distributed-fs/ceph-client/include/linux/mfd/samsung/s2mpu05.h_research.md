# sources/distributed-fs/ceph-client/include/linux/mfd/samsung/s2mpu05.h

## Purpose

This 183-line header defines S2MPU05 PMIC register and regulator IDs plus enable timing, voltage range, ramp, selector, and enable masks.

## Important APIs, Types, and Functions

It declares `enum S2MPU05_reg`, `enum S2MPU05_regulators` for 35 LDOs and 5 bucks, software enable mask, per-buck enable times, LDO/buck minimums and steps, ramp delay, enable shift/mask, vsel masks/counts, and PMIC enable shift.

## Control Flow

No code executes. Regulator drivers use the constants to describe enable delays, voltage maps, and regmap update masks for each rail.

## State and Persistence Behavior

State persists in PMIC registers for interrupts, status, control, OTP, timing, buck/LDO output, ramp, discharge, TCXO control, and MIF selection.

## Dependencies and Integration Points

It integrates with Samsung MFD core, regulator framework, and S2MPU05 IRQ definitions in `samsung/irq.h`.

## Risks and Edge Cases

Enable timing differs by buck and must be honored to avoid early consumer access. Mixed LDO/buck voltage step groups require careful regulator descriptor selection.

## Test Signals

Enable-time tests, regulator voltage conversion tests, probe/build coverage, and suspend/resume tests for TCXO or MIF-related rails.
