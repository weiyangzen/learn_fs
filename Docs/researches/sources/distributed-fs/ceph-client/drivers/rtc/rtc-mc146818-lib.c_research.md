# sources/distributed-fs/ceph-client/drivers/rtc/rtc-mc146818-lib.c

Purpose: provides shared MC146818/CMOS RTC helper routines for safe UIP-aware time reads, RTC presence checks, and CMOS time writes across architecture-specific RTC drivers.

Important APIs and functions: exported functions are `mc146818_avoid_UIP()`, `mc146818_does_rtc_work()`, `mc146818_get_time()`, and `mc146818_set_time()`. `mc146818_get_time_callback()` performs locked CMOS reads. `apply_amd_register_a_behavior()` handles AMD/Hygon register-A bank-select behavior.

Control flow: `mc146818_avoid_UIP()` repeatedly locks `rtc_lock`, reads seconds before checking UIP, waits if UIP is active, optionally invokes a callback, then rechecks UIP and seconds for NMI/virtualization races. `mc146818_get_time()` uses that helper, converts BCD when required, applies DECstation and ACPI century handling, then normalizes month/year. `mc146818_set_time()` validates year range, optionally splits ACPI century, converts to BCD if needed, sets RTC_SET, adjusts frequency-select/divider behavior, writes fields, and restores control/frequency registers.

State and persistence: hardware CMOS RTC registers are persistent. No software state is kept beyond stack callback parameters. Global `rtc_lock` serializes CMOS access.

Dependencies and integration: CMOS_READ/WRITE macros, `rtc_lock`, ACPI FADT century field, architecture config such as DECstation, x86 vendor data for AMD/Hygon behavior, BCD helpers, and exported symbols for other RTC code.

Risks: callbacks may run more than once, so callers must be idempotent. Timeout is in milliseconds but polling granularity is 100 usec. Incorrect century or binary/BCD mode handling changes dates by 100 years. Register-A behavior differs on AMD/Hygon and must preserve bank select semantics.

Test signals: UIP stuck timeout, UIP race during read, long read warning path, binary versus BCD mode, ACPI century presence/absence, DECstation special year handling, AMD/Hygon register-A path, year > 2069 rejection, and exported caller integration.
