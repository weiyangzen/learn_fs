# sources/distributed-fs/ceph-client/drivers/rtc/rtc-tps6586x.c

Purpose: RTC driver for TI TPS6586x PMICs. It exposes a 1 kHz tick counter as seconds, one alarm with a 14-bit seconds-ahead range, wake IRQ support, and PMIC register configuration through the parent MFD API.

Important APIs/types/functions: `struct tps6586x_rtc` stores device, RTC, IRQ, and software IRQ enable state. Time ops read a dummy-prefixed multi-byte counter and shift ticks by 10 to seconds; set-time disables RTC, writes shifted ticks, and re-enables it. Alarm ops enable/disable the IRQ line manually, read current counter, clamp alarms beyond `ALM1_VALID_RANGE_IN_SEC` by programming a past time, and write three alarm bytes. Probe starts the counter in 1 kHz mode, configures start time metadata, requests a no-auto-enable threaded IRQ, and registers.

Control flow/state/persistence: probe enables the PMIC counter and wakeup, then RTC core state maps hardware seconds to a configured start date of 2009-01-01. Remove disables RTC control bits. Suspend/resume toggles IRQ wake if enabled.

Dependencies/integration: TPS6586x MFD functions (`tps6586x_reads/writes/update/set_bits/clr_bits`), platform driver `tps6586x-rtc`, RTC core, IRQ core, PM wake.

Risks/test signals: `platform_get_irq()` result is not checked before `irq_set_status_flags()`. Out-of-range future alarms are silently converted to a past alarm rather than returning an error. Failed time write can leave RTC disabled. Test IRQ absence, counter read byte order, alarm range clamping, manual IRQ enable state, start-time mapping, and remove/error cleanup disabling the counter.
