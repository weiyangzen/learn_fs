# sources/distributed-fs/ceph-client/drivers/hwmon/sg2042-mcu.c

Purpose: I2C hwmon/debugfs/sysfs driver for Sophgo SG2042 power-control MCU. It exposes SoC/board temperatures, critical/repower thresholds, reset/uptime/policy attributes, and debug MCU metadata.

Important APIs/types/functions: `struct sg2042_mcu_data` stores client and mutex. `sg2042_mcu_read()` reads temperature registers in millidegrees. `sg2042_mcu_write()` updates critical or repower hysteresis with ordering validation under `guard(mutex)`. Device attributes expose reset count, uptime, reset reason, and repower policy. `DEFINE_MCU_DEBUG_ATTR` generates debugfs readers.

Control flow: probe checks SMBus byte/block support, allocates state, registers hwmon with extra device groups, then creates debugfs files. Runtime threshold writes read the paired threshold, enforce `crit >= hyst`, clamp to one byte, and write the target register.

State and persistence: MCU register settings persist in hardware. Driver state only serializes threshold updates.

Dependencies/integration: I2C SMBus, hwmon, debugfs, sysfs groups, mutex cleanup guard macros, OF/I2C matching.

Risks: `devm_kmalloc()` leaves padding/unset fields but current struct fields are initialized. Uptime reads two bytes and only checks negative return, not short block length. Temperature threshold units are truncated to whole degrees.

Test signals: threshold write ordering, repower policy strings, debugfs metadata reads, uptime endianness, SMBus functionality gating, and hwmon visibility for writable channel 0 thresholds only.
