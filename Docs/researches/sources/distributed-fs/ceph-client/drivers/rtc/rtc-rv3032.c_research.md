<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/rtc/rtc-rv3032.c -->
# sources/distributed-fs/ceph-client/drivers/rtc/rtc-rv3032.c

Purpose: implements the Micro Crystal RV3032 I2C RTC with minute-resolution alarms, offset calibration, EEPROM and NVRAM access, backup switching, trickle charger configuration, optional clock output, and hwmon temperature input.

Important APIs/types/functions: `struct rv3032_data` stores regmap, RTC, trickle state, and optional clkout hardware. `rv3032_enter_eerd()`, `rv3032_exit_eerd()`, and `rv3032_update_cfg()` manage EEPROM update mode. RTC ops include time, alarm, alarm IRQ enable, offset, voltage ioctl, and backup-switch params. Nvmem callbacks expose 16 RAM bytes and 32 user EEPROM bytes.

Control flow: probe creates the regmap, reads status, allocates the RTC, optionally requests IRQ, configures trickle charging from properties, sets backup switch and minute-alarm feature bits, registers the RTC/nvmem devices, optionally registers clkout, and registers hwmon. Time reads reject PORF or VLF, bulk-read BCD time, and decode to 2000-2099. Alarm operations program minute/hour/day, clear AF/UF, and combine AIE/UIE based on RTC core timers. IRQ handling reports PF/AF/UF, clears corresponding status flags, and disables matching interrupt enables.

State and persistence: persistent hardware state includes time, alarms, flags, PMU backup/trickle bits, offset, EEPROM user area, RAM, and clock-output configuration. Driver state prevents backup-switch mode changes after trickle charger setup because those PMU fields overlap.

Dependencies and integration points: depends on I2C regmap, RTC nvmem helpers, optional Common Clock Framework, hwmon, device properties `trickle-resistor-ohms` and `trickle-voltage-millivolt`, ACPI/OF IDs, and RTC backup-switch params.

Risks and test signals: EEPROM entry/exit must be restored across all error paths. `devm_rtc_nvmem_register()`, clkout registration, and hwmon registration errors are mostly ignored. `hwmon_info` advertises max/hyst fields that are not readable in the read callback. Test PORF/VLF rejection and clear, alarm IRQ paths with/without IRQ, offset clamping, backup-switch rejection when trickle is active, trickle property matrix, EEPROM busy timeouts, clkout low/high-frequency rates, and stable two-sample temperature reads.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/rtc/rtc-rv3032.c -->
