<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/rtc/rtc-rv3029c2.c -->
# sources/distributed-fs/ceph-client/drivers/rtc/rtc-rv3029c2.c

Purpose: implements Micro Crystal RV3029 and RV3049 RTC support over I2C and SPI, including time, alarm, battery-backed RAM, EEPROM-controlled trickle charging, and optional hwmon temperature reporting.

Important APIs/types/functions: `struct rv3029_data` stores device, RTC, regmap, and IRQ. EEPROM helpers `rv3029_eeprom_enter()`, `rv3029_eeprom_exit()`, `rv3029_eeprom_busywait()`, `rv3029_eeprom_read/write()`, and `rv3029_eeprom_update_bits()` guard nonvolatile access. `rv3029_probe()` is bus-neutral, while `rv3029_i2c_probe()` and `rv3049_probe()` provide regmaps. RTC ops cover time, alarm, alarm IRQ enable, and voltage ioctl.

Control flow: bus probe initializes the regmap with inaccessible holes, then common probe applies trickle charger configuration, registers hwmon when configured, allocates the RTC, requests an optional alarm IRQ, sets the 2000-2079 range, registers the RTC, and exposes 8 bytes of battery-backed RAM. Time reads reject VLOW2 or PON, then decode the watch section, including 12-hour mode. Set-time writes the watch section and clears PON/VLOW2. Alarm IRQ handling reads IRQ control/flags under `rtc_lock`, reports AF, disables AIE, and writes updated flags/control.

State and persistence: time, alarm, IRQ flags, trickle charger bits, temperature configuration, and RAM live in hardware. EEPROM refresh is disabled during direct EEPROM access and re-enabled afterward; low-voltage bits gate safe EEPROM access.

Dependencies and integration points: depends on I2C or SPI regmap, RTC core, optional `CONFIG_RTC_DRV_RV3029_HWMON`, OF trickle-resistor property, nvmem, BCD helpers, and both I2C and SPI module registration.

Risks and test signals: trickle configuration selects the first table resistance greater than or equal to the requested value and can dereference past the table if a too-large value is provided. EEPROM reads/writes must not proceed under VLOW2 or persistent VLOW1. Test both bus frontends, inaccessible regmap ranges, low-voltage paths, 12/24-hour decoding, full-date alarm programming, IRQ disable-after-alarm, nvmem, hwmon temperature/update interval, and SPI registration rollback if I2C/SPI init partially fails.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/rtc/rtc-rv3029c2.c -->
