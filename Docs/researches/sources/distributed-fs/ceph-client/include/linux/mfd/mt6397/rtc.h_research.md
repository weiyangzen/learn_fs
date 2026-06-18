# sources/distributed-fs/ceph-client/include/linux/mfd/mt6397/rtc.h

## Purpose

This header defines the common RTC register offsets, bit masks, timing constants, chip data, and runtime state structure for MediaTek PMIC RTC drivers in the MT6397 family.

## Important APIs, Types, and Functions

Important register and bit macros include `RTC_BBPU`, `RTC_BBPU_CBUSY`, `RTC_BBPU_KEY`, chip-specific write-trigger registers `RTC_WRTGR_MT6358`, `RTC_WRTGR_MT6397`, and `RTC_WRTGR_MT6323`, IRQ bits `RTC_IRQ_STA_AL`, `RTC_IRQ_STA_LP`, `RTC_IRQ_EN_AL`, `RTC_IRQ_EN_ONESHOT`, `RTC_IRQ_EN_LP`, alarm masks, time counter offsets from `RTC_TC_SEC`, alarm field masks, `RTC_PDN2_PWRON_ALARM`, and poll timing constants. `struct mtk_rtc_data` carries the write-trigger offset. `struct mt6397_rtc` stores the registered RTC device, lock, regmap, IRQ, address base, and chip data.

## Control Flow

The RTC driver uses `addr_base` plus these offsets to read time registers, set alarm registers, enable or clear IRQs, and trigger writes through the chip-specific `wrtgr` register. Busy polling uses `RTC_BBPU_CBUSY` with `MTK_RTC_POLL_DELAY_US` and `MTK_RTC_POLL_TIMEOUT`. The driver lock serializes register sequences because time/alarm updates require multiple register writes plus a final trigger.

## State and Persistence Behavior

`struct mt6397_rtc` is runtime kernel state. The RTC hardware maintains persistent time, alarm, PDN, and power-on-alarm bits in the PMIC RTC domain. `RTC_PDN2_PWRON_ALARM` can influence boot/power behavior. The write-trigger register is a commit mechanism: values staged into time/alarm registers are not fully applied until the trigger sequence completes.

## Dependencies and Integration Points

The header includes jiffies, mutex, regmap, and RTC core headers. It is included by `drivers/rtc/rtc-mt6397.c` and by `drivers/power/reset/mt6323-poweroff.c` for RTC poweroff/power-on behavior. The parent MFD provides the regmap, IRQ resource, and chip-specific RTC base.

## Risks and Edge Cases

Month/year masks are hardware-specific and narrow, so date conversion must handle century offsets correctly in the C driver. Multi-register time reads can race rollover unless the driver uses stable read patterns. Failure to poll `CBUSY` or to trigger writes leaves stale hardware state. Incorrect `wrtgr` selection breaks only some chips, making cross-chip tests important.

## Test Signals

Use RTC class tests for read/set, alarm set/enable/interrupt, and wake from suspend; test boundary dates and month rollover; check busy-poll timeout behavior with fault injection if possible; verify MT6358/MT6397/MT6323 write-trigger variants; and confirm power-on-alarm behavior through reboot or power-cycle tests.
