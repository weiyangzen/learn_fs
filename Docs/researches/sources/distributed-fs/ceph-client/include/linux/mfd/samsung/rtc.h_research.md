# sources/distributed-fs/ceph-client/include/linux/mfd/samsung/rtc.h

## Purpose

This 170-line header defines Samsung S5M/S2MPS/S2MPG RTC register layouts and common bitfields for time, alarm, update, 12/24-hour, WTSR, and SMPL control.

## Important APIs, Types, and Functions

It defines `enum s5m_rtc_reg`, `enum s2mps_rtc_reg`, `enum s2mpg10_rtc_reg`, RTC I2C address, hour/alarm status bits, BCD/24-hour mode masks, per-variant update request bits, S5M update delay values, alarm enable mask, SMPL/WTSR enable masks, and S2MPG10 cold reset/timer fields.

## Control Flow

No local flow exists. RTC drivers use these enums to select register offsets, write time/alarm values, request update latching with the correct UDR/AUDR/WUDR bits, and enable wakeup/reset features.

## State and Persistence Behavior

RTC time, alarms, update latches, mode flags, WTSR, and SMPL settings persist in PMIC RTC registers, often on an RTC-specific I2C address.

## Dependencies and Integration Points

It integrates Samsung MFD regmap access with Linux RTC class drivers and PMIC wakeup/reset behavior.

## Risks and Edge Cases

Update bits differ between S2MPS13, S2MPS15, and older variants. Hour mode and PM bits need careful conversion. WTSR/SMPL can reset or power-cycle systems if configured incorrectly.

## Test Signals

RTC set/read/alarm tests for each layout, BCD and 12/24-hour conversion tests, update-bit timing tests, and suspend wake alarm validation.
