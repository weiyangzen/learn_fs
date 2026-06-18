# sources/distributed-fs/ceph-client/drivers/rtc/rtc-ds3232.c

Purpose: supports Maxim/Dallas DS3232 I2C and DS3234 SPI RTCs using a shared regmap-based core. It provides calendar, one-shot alarm, SRAM nvmem, optional temperature hwmon, IRQ wake support, and both I2C/SPI module registration.

Important APIs/types/functions: `struct ds3232` stores device, regmap, IRQ, RTC, and suspend state. `ds3232_probe()` is the shared core. `ds3232_read_time()`/`ds3232_set_time()` access the first seven registers, handling 12/24-hour and century bits. `ds3232_read_alarm()`/`ds3232_set_alarm()` use alarm1. `ds3232_irq()` disables alarm1, clears A1F, and reports `RTC_AF`. `ds3232_nvmem_read()`/`write()` expose SRAM; `ds3232_hwmon_read_temp()` exposes temperature.

Control flow: bus-specific probes create an I2C or SPI regmap, perform any SPI control setup, and call the shared probe. The shared probe clears oscillator/alarm status, configures interrupt mode, enables wake capability when IRQ exists, registers hwmon, registers the RTC, registers SRAM nvmem, and requests a threaded IRQ if available. Suspend/resume toggles IRQ wake for I2C devices.

State and persistence: time, alarm registers, SRAM, oscillator flags, control bits, and temperature conversion state are hardware-backed. Runtime state tracks regmap and IRQ availability.

Dependencies and integration: integrates with I2C, SPI, regmap, RTC, nvmem, hwmon, OF/I2C/SPI IDs, and PM sleep hooks.

Risks and test signals: the alarm path only supports alarm1 and disables it after interrupt, so repeated alarms require reprogramming. SPI probe overwrites parts of control/status during setup. Test I2C and SPI registration combinations, oscillator-stop warnings, alarm IRQ clear/disable, SRAM nvmem range, hwmon conversion including negative temperatures, wake suspend/resume, and no-IRQ alarm behavior.
