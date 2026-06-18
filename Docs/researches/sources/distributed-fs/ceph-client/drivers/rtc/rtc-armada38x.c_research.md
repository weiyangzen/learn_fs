# sources/distributed-fs/ceph-client/drivers/rtc/rtc-armada38x.c

## Purpose

`rtc-armada38x.c` drives Marvell Armada 38x and Armada 7K/8K RTC blocks. It supports seconds-counter timekeeping, one alarm, calibration offset, SoC bridge timing setup, and multiple hardware workarounds for unreliable access.

## Important APIs, types, and functions

`struct armada38x_rtc_data` abstracts SoC-specific bridge timing, register read workaround, interrupt clear/unmask, and alarm selection. `struct armada38x_rtc` stores mapped RTC and SoC registers, spinlock, IRQ, initialization state, and sampling buffer. RTC callbacks include `armada38x_rtc_read_time()`, `armada38x_rtc_set_time()`, `armada38x_rtc_read_alarm()`, `armada38x_rtc_set_alarm()`, `armada38x_rtc_alarm_irq_enable()`, `armada38x_rtc_read_offset()`, and `armada38x_rtc_set_offset()`. `rtc_delayed_write()` implements the erratum workaround.

## Control flow

Probe maps `"rtc"` and `"rtc-soc"` resources, gets the IRQ, allocates the RTC, requests the IRQ if available, configures wakeup or clears alarm support, updates MBUS bridge timing, assigns ops and `range_max = U32_MAX`, and registers. For Armada 38x, reads sample a register up to 100 times and return the most frequent value. Set time lazily resets uninitialized RTC state before writing. Alarm set writes the compare register and, if enabled, enables the corresponding IRQ and unmasks SoC interrupt routing. IRQ handling clears SoC ISR, disables the alarm IRQ, acknowledges RTC status, derives update/periodic flags if frequency bits were set, and reports to the RTC core.

## State and persistence behavior

Hardware persists time, alarm, IRQ config, correction register, status, and bridge timing registers. The driver keeps volatile `initialized` state to avoid repeated reset and a sampling buffer for read workarounds. Calibration persists in `RTC_CCR`.

## Dependencies and integration points

It depends on platform resources, OF compatibles `"marvell,armada-380-rtc"` and `"marvell,armada-8k-rtc"`, MMIO, spinlocks, RTC class APIs, and PM wake IRQ handling. The RTC offset API exposes hardware calibration in parts per billion.

## Risks and edge cases

The write path requires two dummy writes and a 5 us delay; missing that pattern can lose writes. The 38x read workaround assumes the most frequent sample is correct. Offset conversion is non-linear and clamps inputs to avoid division issues. `armada38x_rtc_set_offset()` writes without taking the driver's spinlock, unlike other register mutations. If IRQ request fails, alarm features are cleared but alarm registers still exist.

## Test signals

Test both compatibles, read consistency under ticking counter, reset path when `RTC_CONF_TEST` low bits are non-zero, alarm IRQ acknowledge and disable, wake from suspend, offset read/set over clamp limits and fine/coarse mode crossover, and bridge timing reprogramming on resume.
