<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/rtc/rtc-rv3028.c -->
# sources/distributed-fs/ceph-client/drivers/rtc/rtc-rv3028.c

Purpose: implements the Micro Crystal RV3028 I2C RTC with alarms, update interrupts, timestamp capture, EEPROM-backed configuration, NVRAM/EEPROM nvmem cells, backup switch control, trickle charger setup, offset calibration, and optional clock output.

Important APIs/types/functions: `struct rv3028_data` carries the regmap, RTC device, chip type, and optional `clk_hw`. EEPROM helpers `rv3028_enter_eerd()`, `rv3028_exit_eerd()`, `rv3028_update_eeprom()`, and `rv3028_update_cfg()` serialize nonvolatile configuration changes. RTC ops cover time, alarm, alarm IRQ enable, offset, backup-switch `param_get/set`, and voltage ioctl. Nvmem callbacks expose two RAM bytes and 43 EEPROM bytes.

Control flow: probe creates an I2C regmap, warns on missed alarm status, allocates the RTC, optionally requests a threaded IRQ, selects day-of-month alarms with `WADA`, enables timestamp events, applies trickle charger properties, adds timestamp sysfs attributes, registers the RTC, registers nvmem providers, and optionally registers clkout. IRQ handling reads status, reports PF/AF/UF events, clears handled flags and disables matching interrupt enables, and notifies timestamp sysfs on external events.

State and persistence: time, alarms, event flags, clock output, backup mode, trickle charger, and offset are persisted in hardware registers, with selected settings committed through EEPROM update commands. Timestamp count/data and RAM survive backup power. Driver state is mostly the regmap and RTC feature bits.

Dependencies and integration points: depends on I2C regmap, RTC core, nvmem registration through RTC, sysfs attribute groups, optional Common Clock Framework provider, device properties `trickle-resistor-ohms` and `aux-voltage-chargeable`, and ACPI/OF IDs.

Risks and test signals: EEPROM paths must always restore EERD state after errors. Alarm enable depends on RTC core `uie_rtctimer` and `aie_timer` state. `devm_rtc_nvmem_register()` return values are ignored. Test PORF rejection/clear, alarm rounding to minute, IRQ flag clearing, timestamp count/reset, backup switch modes, offset clamp, EEPROM busy timeouts, trickle property validation, clkout rate/prepare/unprepare, and operation without IRQ.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/rtc/rtc-rv3028.c -->
