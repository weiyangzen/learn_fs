# sources/distributed-fs/ceph-client/drivers/rtc/rtc-sc27xx.c

Purpose: RTC driver for Spreadtrum/Unisoc SC27xx PMIC RTC blocks. It supports current time, normal alarm, auxiliary alarm, power-down validity detection, and power-off alarm persistence through PMIC regmap registers.

Important APIs/types/functions: `struct sprd_rtc` stores the RTC device, parent regmap, register base, IRQ, and validity flag. `sprd_rtc_get_secs()` and `sprd_rtc_set_secs()` convert split sec/min/hour/day registers to seconds for time, normal alarm, and auxiliary alarm register groups. `sprd_rtc_lock_alarm()` updates SPG alarm lock bits and power-off alarm flag. `sprd_rtc_set_alarm()` chooses normal alarm for the RTC core AIE timer and auxiliary alarm for wake-only alarms. `sprd_rtc_check_power_down()` sets `valid`, and `sprd_rtc_check_alarm_int()` restores alarm enable when SPG indicates a previous power-off alarm.

Control flow/state/persistence: probe gets the parent regmap, DT `reg` base, IRQ, allocates RTC, restores alarm interrupt state, checks power-status validity, requests a threaded IRQ, enables wakeup, sets range 0..5662310399 seconds, and registers. Hardware stores time and normal/SPG registers in always-on VDDRTC regions, while `INT_EN` does not persist across full power down; the driver uses SPG flags to bridge that.

Dependencies/integration: platform driver `sprd-rtc`, compatible `sprd,sc2731-rtc`, parent MFD regmap, RTC core, threaded IRQ with `IRQF_ONESHOT | IRQF_EARLY_RESUME`, DT base offset, and wakeup integration.

Risks/test signals: register writes require polling up to 200 ms because always-on register updates are slow. Alarm mode selection depends on comparing requested alarm with `rtc->aie_timer.node.expires`; regressions can break power-on alarm vs deep-sleep wake behavior. Test invalid power status, set-time validity transition, normal and auxiliary alarms, alarm lock/unlock, power-cycle persistence, and timeout/error propagation from regmap.
