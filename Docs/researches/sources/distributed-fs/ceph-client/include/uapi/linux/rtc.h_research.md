<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/rtc.h -->
# sources/distributed-fs/ceph-client/include/uapi/linux/rtc.h

Purpose: defines the generic `/dev/rtc` userspace ABI for reading and setting RTC time, alarms, periodic interrupts, PLL correction, voltage-low status, feature flags, and device parameters.

Important APIs, types, and functions: `struct rtc_time` mirrors broken-down calendar time. `struct rtc_wkalrm` carries alarm enable/pending state and time. `struct rtc_pll_info` describes clock correction capabilities. `struct rtc_param` is a generic indexed parameter container. Ioctls include alarm/update/periodic/watchdog interrupt toggles, `RTC_ALM_SET/READ`, `RTC_RD_TIME`, `RTC_SET_TIME`, `RTC_IRQP_READ/SET`, epoch, wake alarm, PLL, parameter, and voltage-low operations. Constants define IRQ flags, feature IDs, parameter IDs, backup-switch modes, voltage flags, and `RTC_MAX_FREQ`.

Control flow: userspace opens an RTC character device, issues ioctl reads/writes for time and alarm state, optionally enables interrupts and reads interrupt flags from the device, queries feature bitmaps through parameters, and clears voltage-low flags after inspection.

State and persistence behavior: time, alarm, correction, and voltage status live in RTC hardware and driver state, often backed by battery power. Parameter and feature values may be static capabilities or runtime settings. The header itself owns no state.

Dependencies and integration points: depends on const, ioctl, and fixed-width type UAPI headers. It integrates with RTC class drivers, wakeup alarm infrastructure, poll/read interrupt delivery, and time-setting tools.

Risks and edge cases: calendar fields follow `struct tm` conventions and need range validation. Some ioctl command numbers overlap historically (`RTC_WIE_*` with wake alarm, parameter with voltage-low), so driver dispatch must disambiguate by command encoding. Not all RTCs support every feature or high interrupt rates.

Test signals: read/set time round trips, alarm wakeup behavior, periodic/update/alarm interrupts, unsupported ioctl returns, voltage-low flag read/clear, feature bitmap queries, backup-switch modes, and boundary calendar values.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/rtc.h -->
