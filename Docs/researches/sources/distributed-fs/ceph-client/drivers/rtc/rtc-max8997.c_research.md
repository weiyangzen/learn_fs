# sources/distributed-fs/ceph-client/drivers/rtc/rtc-max8997.c

Purpose: supports the MAX8997 PMIC RTC with binary-mode timekeeping, alarm1, IRQ-domain alarm delivery, and WTSR/SMPL reset features controlled by module parameters.

Important APIs and functions: `struct max8997_rtc_info` tracks parent PMIC, RTC I2C client, RTC device, mutex, virtual IRQ, and 24-hour mode. Conversion helpers are `max8997_rtc_data_to_tm()` and `max8997_rtc_tm_to_data()`. Alarm helpers include `max8997_rtc_stop_alarm()` and `max8997_rtc_start_alarm()`. Reset-feature helpers are `max8997_rtc_enable_wtsr()` and `max8997_rtc_enable_smpl()`.

Control flow: probe initializes binary/24-hour control, enables WTSR/SMPL if module parameters allow, marks wakeup, registers the RTC, maps the RTCA1 IRQ from the parent IRQ domain, and requests a threaded IRQ. Writes require `max8997_rtc_set_update_reg()` followed by a 20 ms delay. Alarm enabling sets enable bits on second/minute/hour and valid date/month/year fields while clearing weekday enable.

State and persistence: RTC registers hold time, alarm, update, WTSR, and SMPL settings. Software mutex serializes updates. WTSR/SMPL are disabled in shutdown.

Dependencies and integration: MAX8997 MFD private helpers, IRQ domain mapping, module parameters `wtsr_en` and `smpl_en`, RTC class, mutexes, and parent PMIC status registers.

Risks: reset features can affect system behavior beyond RTC timekeeping and are enabled by default. Driver uses info-level logging in set_alarm and IRQ paths, which can be noisy. No PM sleep hooks are present despite wakeup initialization. The driver only supports years >= 2000.

Test signals: WTSR/SMPL enable/disable and shutdown cleanup, update-register delay, alarm bit selection and IRQ handling, parent status pending read, year rejection, IRQ-domain mapping failure, and module parameter-disabled reset features.
