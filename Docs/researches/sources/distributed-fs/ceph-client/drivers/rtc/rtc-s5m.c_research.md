<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/rtc/rtc-s5m.c -->
# sources/distributed-fs/ceph-client/drivers/rtc/rtc-s5m.c

Purpose: implements Samsung S5M8767, S2MPG10, S2MPS13, S2MPS14, and S2MPS15 PMIC RTC subdrivers, including time, alarm, alarm IRQ wake, UDR synchronization, and an S2MPG10 restart handler.

Important APIs/types/functions: `struct s5m_rtc_reg_config` abstracts per-chip register layout and UDR masks. `struct s5m_rtc_info` stores parent PMIC, regmap, RTC, IRQ, device type, 24-hour mode, and selected config. Conversion helpers `s5m8767_data_to_tm()` and `s5m8767_tm_to_data()` handle binary-format RTC data. Update helpers `s5m8767_wait_for_udr_update()`, `s5m8767_rtc_set_time_reg()`, and `s5m8767_rtc_set_alarm_reg()` synchronize hardware transfers. RTC ops cover time, alarm, and alarm IRQ enable.

Control flow: probe gets the PMIC RTC regmap or creates a dummy I2C client/regmap for older PMICs, selects the register config, obtains optional alarm IRQ, initializes PMIC RTC control to binary 24-hour mode, allocates the RTC, requests threaded alarm IRQ and wakeup if present, optionally registers an S2MPG10 sys-off restart handler, and registers the RTC. Reads optionally trigger RUDR, bulk-read time, and convert fields. Writes raw time/alarm data, set WUDR/AUDR/RUDR masks as required per chip, and wait for auto-clear. Alarm enable sets or clears `ALARM_ENABLE_MASK` bits across active alarm fields.

State and persistence: PMIC RTC registers persist time, alarm fields, enable bits, UDR transfer state, status bits, and watchdog/restart controls. Driver state records chip-specific UDR behavior, because some bits auto-clear and S2MPS13 AUDR must be manually cleared.

Dependencies and integration points: depends on Samsung MFD core/regmap, platform device IDs, parent PMIC status regmap for pending alarms, optional named IRQ `alarm`, RTC core, PM sleep wake IRQs, and sys-off restart registration for S2MPG10 power-controller systems.

Risks and test signals: UDR masks differ subtly across devices; a wrong config can make time/alarm writes silently not transfer. `s5m8767_wait_for_udr_update()` returns the last regmap status even when retries expire, only logging an error. Weekday uses `ffs()` without subtracting one. Test every device type, dummy RTC I2C creation, regmap-from-parent path, WUDR/RUDR/AUDR sequencing, S2MPS13 manual AUDR clear, pending-alarm status source, IRQ absent feature clearing, suspend/resume wake, and S2MPG10 restart watchdog arming.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/rtc/rtc-s5m.c -->
