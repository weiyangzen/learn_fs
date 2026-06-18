# sources/distributed-fs/ceph-client/drivers/rtc/rtc-tegra.c

Purpose: NVIDIA Tegra internal RTC driver for Tegra 200 series and ACPI-exposed variants. It supports seconds time, alarm0, interrupt masking/status, proc info, clock setup for DT systems, wakeup, and PM alarm wake.

Important APIs/types/functions: `struct tegra_rtc_info` holds platform device, RTC, MMIO, optional clock, IRQ, and lock. `tegra_rtc_wait_while_busy()` waits for the hardware copy/update window so writes have a safe period. `tegra_rtc_read_time()` reads milliseconds first to latch shadow seconds. Alarm ops use `SECONDS_ALARM0` and mask bit `SEC_ALARM0`. IRQ handler clears all masks/status on any IRQ and reports alarm or periodic events.

Control flow/state/persistence: probe maps MMIO, gets IRQ, allocates RTC, enables optional DT clock, clears alarm/status/mask registers, enables wakeup, requests high-trigger IRQ, registers RTC, and logs. Suspend clears status, enables only alarm0 mask for wake, and calls `enable_irq_wake()` when appropriate; shutdown disables alarm IRQ.

Dependencies/integration: OF compatible `nvidia,tegra20-rtc`, ACPI ID `NVDA0280`, platform MMIO/IRQ, optional clock, RTC core, seq proc callback, PM wake.

Risks/test signals: `tegra_rtc_wait_while_busy()` comments say wait for busy then not busy, but implementation only waits while currently busy; timing assumptions need hardware validation. Set-alarm ignores wait return values. Test shadow read correctness, write windows, alarm disable-on-IRQ, suspend wake mask, ACPI and OF probe paths, and U32 time range.
