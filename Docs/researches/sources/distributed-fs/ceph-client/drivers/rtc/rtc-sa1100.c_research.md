# sources/distributed-fs/ceph-client/drivers/rtc/rtc-sa1100.c

Purpose: RTC subsystem platform driver for StrongARM SA1100 and related PXA/MMP RTC blocks. It exposes a seconds counter, alarm compare register, 1 Hz/update interrupt, proc diagnostics, clock enable, wakeup, and two register layouts selected by architecture or DT compatible.

Important APIs/types/functions: `struct sa1100_rtc` comes from `rtc-sa1100.h`. `sa1100_rtc_interrupt()` handles both 1 Hz and alarm IRQs, clears RTSR status carefully, and reports `RTC_AF`/`RTC_UF`. `sa1100_rtc_read_time()` and `sa1100_rtc_set_time()` map the 32-bit `RCNR` seconds counter to `struct rtc_time`. `sa1100_rtc_read_alarm()`, `sa1100_rtc_set_alarm()`, and `sa1100_rtc_alarm_irq_enable()` operate on `RTAR` and `RTSR_ALE`. `sa1100_rtc_init()` is exported for reuse and performs clock setup, divider initialization, RTC registration, and initial interrupt-status clearing.

Control flow/state/persistence: probe obtains named IRQs, allocates the RTC, requests both IRQs, maps MMIO, assigns register offsets for SA1100 vs MMP/PXA layout, enables wakeup, then calls the shared init. The persistent hardware state is the counter, alarm, trim/divider, and status/enable bits. If `RTTR` is zero, the driver installs a default 32768 Hz divider and resets the counter to zero, explicitly treating old state as invalid.

Dependencies/integration: platform driver name `sa1100-rtc`, OF compatibles `mrvl,sa1100-rtc` and `mrvl,mmp-rtc`, clock framework, devm RTC registration, MMIO, named platform IRQs, and PM wake IRQ enable on alarm.

Risks/test signals: most risk is register-status semantics. The interrupt path has special handling for spurious `RTSR_HZ`/`RTSR_AL` states seen on SA11xx and clears disabled pending sources to avoid interrupt storms. Test with alarm firing, 1 Hz updates, suspend wake, both register layouts, zeroed trim register initialization, and removal disabling `RTSR`.
