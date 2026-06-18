# sources/distributed-fs/ceph-client/drivers/rtc/rtc-stmp3xxx.c

Purpose: Freescale/Sigmatel STMP37xx/STMP378x/i.MX28 RTC driver. It provides seconds counter, alarm, persistent oscillator configuration, optional child watchdog registration, and suspend/resume reset handling.

Important APIs/types/functions: `struct stmp3xxx_rtc_data` stores RTC device, MMIO, and alarm IRQ. `stmp3xxx_wait_time()` polls stale bits before reading/writing seconds. `stmp3xxx_rtc_gettime()` and `_settime()` access `STMP3XXX_RTC_SECONDS`. Alarm ops use `STMP3XXX_RTC_ALARM` plus persistent alarm wake/enable bits. Optional `stmp3xxx_wdt_set_timeout()` exposes watchdog control through child platform data.

Control flow/state/persistence: probe maps MMIO, verifies RTC presence, avoids block reset if watchdog is running, detects or reads DT override for 32 kHz crystal frequency, configures persistent oscillator and alarm bits, disables IRQs, allocates/registers RTC, requests alarm IRQ, then registers the watchdog child if enabled. Persistent registers survive low-power states and control wake and clock source.

Dependencies/integration: compatible `fsl,stmp3xxx-rtc`, STMP register set/clear offsets, optional `CONFIG_STMP3XXX_RTC_WATCHDOG`, DT `stmp,crystal-freq`, RTC core, platform IRQ.

Risks/test signals: resetting the block can stop a running watchdog, so the skip path is critical. Crystal fuse values can be unreliable, hence DT override. Test stale-bit timeout, 32000/32768/no-crystal modes, alarm wake bits, watchdog-enabled probe, resume reset clearing alarm wake, and invalid crystal warning path.
