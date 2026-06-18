# File Research: sources/block-storage/util-linux/sys-utils/hwclock-rtc.c

Purpose: Provides the `/dev/rtc` hardware-clock backend for `hwclock`, including Linux RTC ioctls, GNU/Hurd RTC support, Linux RTC parameters, and voltage-low status operations.

Core behavior:
- Opens an explicitly requested `--rtc` path or probes common RTC paths (`/dev/rtc`, `/dev/rtc0`, `/dev/misc/rtc`, plus ia64 EFI variants).
- Reads and sets RTC time using `RTC_RD_TIME` and `RTC_SET_TIME`, copying between kernel `struct rtc_time` and userspace `struct tm`.
- Synchronizes to the next RTC tick by enabling `RTC_UIE_ON` and waiting with `select()`; falls back to busy-waiting on repeated reads when update interrupts are unsupported.
- Exposes `probe_for_rtc_clock()` as a `clock_ops` backend when an RTC device can be opened.
- On Alpha builds, supports reading and setting the RTC epoch using `RTC_EPOCH_READ` and `RTC_EPOCH_SET`.
- On Linux non-GNU builds, supports `RTC_PARAM_GET/SET` for named or numeric RTC parameters and voltage-low read/clear via `RTC_VL_READ` and `RTC_VL_CLR`.

Important implementation details:
- Device fd is cached globally and closed with `atexit()`.
- Linux opens RTC devices read-only except on GNU/Hurd, where read-write is used.
- `set_param_rtc()` reads the current parameter and skips the set ioctl if the value is unchanged.
- Voltage-low reporting decodes known bits and prints any remaining unknown bitmask.

Dependencies and integration:
- Implements declarations from `hwclock.h`: RTC probe, optional epoch helpers, parameter helpers, and voltage-low helpers.
- Used by `hwclock.c` as the preferred access method on Linux/GNU when direct ISA is not selected.

Risks and edge cases:
- Some diagnostic strings mention `RTC_RD_NAME`/`RTC_VL_CLEAR` while calling `RTC_RD_TIME`/`RTC_VL_CLR`; this is cosmetic but can confuse troubleshooting.
- Busy-wait tick synchronization has a 1.5 second timeout and depends on RTC reads changing seconds promptly.
