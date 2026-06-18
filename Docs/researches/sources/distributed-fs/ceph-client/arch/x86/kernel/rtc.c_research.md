# sources/distributed-fs/ceph-client/arch/x86/kernel/rtc.c

## Purpose
Implements x86 CMOS RTC access, persistent clock read/write hooks, and fallback `rtc_cmos` platform-device registration.

## APIs, Types, And Functions
Exports `rtc_lock`, and on 32-bit exports `cmos_lock`. Public functions include `mach_set_cmos_time()`, `mach_get_cmos_time()`, `rtc_cmos_read()`, `rtc_cmos_write()`, `update_persistent_clock64()`, and `read_persistent_clock64()`. `add_rtc_cmos()` is a device initcall.

## Control Flow
`mach_set_cmos_time()` converts a timespec to `rtc_time`, validates it, then writes the MC146818 clock. `mach_get_cmos_time()` rejects RTC values used by pm_trace, reads the RTC with a timeout, and converts to timespec. CMOS byte access uses `lock_cmos_prefix/suffix` around port index/data I/O. Persistent clock hooks delegate to `x86_platform.set_wallclock` and `x86_platform.get_wallclock`. `add_rtc_cmos()` registers a fallback platform device unless another CMOS device exists or the platform marked legacy RTC absent.

## State And Persistence
CMOS RTC contents are persistent hardware state. Kernel state includes exported locks and the platform device. The file does not cache wall time.

## Dependencies And Integration
Depends on MC146818 RTC helpers, I/O ports, ACPI/pm_trace validation, `x86_platform` wallclock hooks, platform device core, and legacy platform quirks.

## Risks And Test Signals
Risks include invalid RTC writes, NMI/CMOS locking mistakes, pm_trace misinterpreted as real time, and duplicate RTC platform devices. Test signals include read/write persistent clock tests, suspend/resume timekeeping, `/dev/rtc` binding, 32-bit NMI-safe CMOS access, and boot logs for fallback registration.
