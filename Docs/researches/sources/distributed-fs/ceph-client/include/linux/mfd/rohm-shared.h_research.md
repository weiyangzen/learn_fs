# sources/distributed-fs/ceph-client/include/linux/mfd/rohm-shared.h

## Purpose

This 21-line header contains shared RTC bit masks for ROHM BD70528 and BD71828 devices. It centralizes BCD field widths and alarm-enable masks used by ROHM RTC code.

## Important APIs, Types, and Functions

It defines masks for seconds, minutes, 24-hour mode, PM flag, hour, day, week, month, year, and alarm enable fields: `BD70528_MASK_RTC_SEC` through `BD70528_MASK_ALM_EN`. There are no types or functions.

## Control Flow

There is no flow. RTC drivers use these masks while reading or writing time/alarm registers through regmap.

## State and Persistence Behavior

The represented state persists in PMIC RTC registers and alarm control bits. The header itself has no storage.

## Dependencies and Integration Points

It is a leaf include for ROHM RTC implementations shared across related chips.

## Risks and Edge Cases

Misapplying the 24-hour and PM masks can corrupt hour conversion. Alarm enable mask width must match the chip's alarm register layout.

## Test Signals

RTC set/get tests across 12/24-hour values, alarm enable/disable tests, and BCD boundary tests for day/month/year field masks.
