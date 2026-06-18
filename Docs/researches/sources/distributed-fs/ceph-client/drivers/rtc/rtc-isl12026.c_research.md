# sources/distributed-fs/ceph-client/drivers/rtc/rtc-isl12026.c

Purpose: supports the Intersil ISL12026 I2C RTC and its separate EEPROM array exposed through nvmem at companion I2C address `0x57`.

Important APIs/types/functions: `struct isl12026` stores RTC and dummy EEPROM client. `isl12026_arm_write()`/`isl12026_disarm_write()` implement the WEL/RWEL write-enable sequence. `isl12026_rtc_read_time()` and `isl12026_rtc_set_time()` access CCR registers with BCD conversion and century field. `isl12026_nvm_read()`/`isl12026_nvm_write()` expose 512 bytes of EEPROM with page-sized writes. `isl12026_force_power_modes()` applies optional `isil,pwr-bsw` and `isil,pwr-sbib` properties.

Control flow: probe checks I2C functionality, allocates state, optionally updates power mode bits, creates the dummy EEPROM client, allocates RTC, registers nvmem, and registers RTC. Time writes arm register writes, write the clock block, then disarm. Nvmem writes split data at 16-byte page boundaries and sleep for EEPROM write time after each page.

State and persistence: time registers, power mode bits, and EEPROM contents persist in hardware. Runtime state includes the dummy nvmem client and RTC pointer.

Dependencies and integration: depends on I2C transfers with two-byte register addresses, RTC core, nvmem provider, OF properties, and dummy I2C client lifecycle.

Risks and test signals: if RTC registration fails after the dummy client is created, devm cleanup will not automatically unregister it because only `remove()` does that for a bound device. Error paths after dummy creation deserve review. Test write-enable sequencing, oscillator/RTC failure warnings, 12/24-hour read conversion, page boundary nvmem writes, power property updates, and dummy-client cleanup on failures.
