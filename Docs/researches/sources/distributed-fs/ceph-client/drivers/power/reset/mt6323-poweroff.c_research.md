# sources/distributed-fs/ceph-client/drivers/power/reset/mt6323-poweroff.c

## Purpose
MediaTek MT6323 PMIC RTC/BBPU poweroff driver.

## Important APIs, Types, and Functions
PMIC register definitions, `mt6323_do_pwroff()`, and probe obtaining parent regmap.

## Control Flow
probe checks for PMIC/RTC parent data and sets global poweroff; callback writes BBPU key/enable bits and waits for external shutdown.

## State and Persistence Behavior
global regmap pointer and poweroff hook persist; PMIC RTC BBPU bits persist in hardware.

## Dependencies and Integration Points
MFD_MT6397/MT6323, regmap, platform driver, legacy poweroff.

## Risks and Edge Cases
global singleton; key-protected register writes must be exact; callback may spin/delay if PMIC fails to cut power.

## Test Signals
MT6323 board shutdown, regmap failure, probe with missing parent, and poweroff register trace.
