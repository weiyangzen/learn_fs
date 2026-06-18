# sources/distributed-fs/ceph-client/drivers/hwmon/sht21.c

Purpose: I2C hwmon driver for Sensirion SHT20/SHT21/SHT25 humidity and temperature sensors. It exposes temperature, humidity, and electronic identification code.

Important APIs/types/functions: `struct sht21` stores client, lock, cached readings, validity, and EIC text. `sht21_update_measurements()` triggers hold-master temperature and humidity SMBus word reads, converts raw ticks, and caches results. `eic_read()` performs two raw I2C command/read transfers to assemble the serial/electronic code.

Control flow: probe checks SMBus word support, allocates state, initializes mutex, and registers hwmon with legacy attribute group. Reading temp or humidity refreshes both values at most twice per second. EIC is read once lazily and cached as text.

State and persistence: temperature/humidity cache for half a second to satisfy sensor duty-cycle guidance. EIC string persists after first successful read.

Dependencies/integration: I2C SMBus word reads plus raw I2C transfers for EIC, hwmon group API, I2C/OF matching.

Risks: no CRC validation is performed on measurement words. `i2c_transfer()` return values are only checked for negative errors, not partial message counts. EIC cache remains empty after failures and will retry.

Test signals: SMBus functionality gating, conversion formulas, half-second cache behavior, EIC read formatting, and support for all three IDs/compatibles.
