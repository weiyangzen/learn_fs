# sources/distributed-fs/ceph-client/kernel/time/ntp_internal.h

Purpose: private internal interface between timekeeping code and the NTP discipline implementation.

Important APIs: declares initialization and reset (`ntp_init()`, `ntp_clear()`), scaled tick query (`ntp_tick_length()`), leap query (`ntp_get_next_leap()`), per-second update (`second_overflow()`), `adjtimex` processing (`ntp_adjtimex()`), PPS discipline (`__hardpps()`), and conditional CMOS/RTC notification (`ntp_notify_cmos_timer()`).

State and persistence: no direct storage. It defines compile-time behavior for callers when hardware clock synchronization is unavailable by providing an inline no-op `ntp_notify_cmos_timer()`.

Dependencies and integration: included by NTP/timekeeping internals; relies on `ktime_t`, `time64_t`, `__kernel_timex`, `timespec64`, and audit NTP data types supplied by including context. It keeps these APIs out of public kernel headers.

Risks and test signals: risks are ABI drift between declarations and `ntp.c`, and configuration drift around CMOS/RTC sync. Build-test with and without `CONFIG_GENERIC_CMOS_UPDATE`/`CONFIG_RTC_SYSTOHC`, and verify timekeeping callers can link all declared functions.
