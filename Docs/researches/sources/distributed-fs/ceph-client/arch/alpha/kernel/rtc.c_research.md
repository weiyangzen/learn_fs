# sources/distributed-fs/ceph-client/arch/alpha/kernel/rtc.c

## Purpose
`rtc.c` provides an Alpha-specific RTC class device around the MC146818-compatible CMOS clock. It avoids the generic `rtc-cmos` alarm-capable driver because alarm interrupts are indistinguishable from timer interrupts on these systems, and it handles non-1900 RTC epochs used by Alpha firmware and operating systems.

## Important APIs, Types, And Functions
- `rtc_epoch` stores the active RTC epoch and can be set with the boot parameter `epoch=`.
- `specifiy_epoch()` parses the boot parameter, accepting epochs at or after 1900.
- `init_rtc_epoch()` detects PC, NT, Digital UNIX, or 2000-style epoch based on CMOS year.
- `alpha_rtc_read_time()` reads via `mc146818_get_time()` and adjusts `tm_year` for non-1900 epochs.
- `alpha_rtc_set_time()` reverses the epoch adjustment before `mc146818_set_time()`.
- `alpha_rtc_ioctl()` implements `RTC_EPOCH_READ` and `RTC_EPOCH_SET`.
- `alpha_rtc_ops` is the normal RTC ops table.
- Under selected SMP generic/Marvel configs, `remote_rtc_ops` marshals reads/writes to `boot_cpuid` through `smp_call_function_single()` when `alpha_mv.rtc_boot_cpu_only` is true.
- `alpha_rtc_init()` registers platform device `rtc-alpha`, allocates an RTC device, assigns ops, and registers it at `device_initcall`.

## Control Flow
Initialization detects or accepts an epoch, registers a simple platform device, allocates an RTC class device, selects normal or remote ops, and registers with the RTC core. Read calls fetch CMOS time using generic MC146818 logic, then undo/reapply century adjustment if the epoch is not 1900. Set calls subtract the epoch delta before programming CMOS. Remote ops execute the same read/set functions on the boot CPU for hardware that only permits CMOS access there.

## State And Persistence
`rtc_epoch` is runtime kernel state and can be changed through ioctl. The CMOS RTC hardware persists date/time across reboots. The code intentionally does not support alarms. Platform and RTC device registration persists for the lifetime of the kernel.

## Dependencies And Integration Points
The file depends on Linux RTC class, platform device APIs, MC146818 CMOS helpers, BCD conversion, Alpha `alpha_mv.rtc_boot_cpu_only`, `boot_cpuid`, and SMP call-function support. Time initialization elsewhere uses `common_init_rtc()` declared in `proto.h`.

## Risks
- The boot parameter function name is misspelled `specifiy_epoch`, but the `__setup("epoch=", ...)` binding is correct.
- Epoch inference from two-digit CMOS year is heuristic; unusual firmware settings can produce wrong years.
- Remote RTC access must not deadlock if invoked in contexts unsuitable for synchronous cross-CPU calls.
- `platform_device_register_simple()` failure is not checked before using `pdev->dev`, which is a potential robustness issue.

## Test Signals
- Boot logs show chosen epoch and RTC year.
- `hwclock`/RTC class reads produce expected full year across PC, NT, Digital UNIX, and 2000 epochs.
- `RTC_EPOCH_READ/SET` ioctl tests reject epochs before 1900 and affect subsequent read/set conversion.
- SMP boot-CPU-only platforms can read/set RTC from non-boot CPUs.
