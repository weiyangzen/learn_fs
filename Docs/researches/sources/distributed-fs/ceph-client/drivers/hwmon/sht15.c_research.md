# sources/distributed-fs/ceph-client/drivers/hwmon/sht15.c

Purpose: bit-banged GPIO platform driver for Sensirion SHT1x temperature/humidity sensors. It implements the sensor’s custom two-wire protocol, optional CRC checking, regulator-aware temperature compensation, interrupt-driven conversion completion, and legacy hwmon sysfs attributes.

Important APIs/types/functions: `struct sht15_data` stores GPIOs, workqueue, waitqueue, cached raw values/status, CRC flags, regulator state, and read lock. Low-level protocol functions implement transmission start, bit/byte send/read, ACK/NAK, status read/write, soft reset, and connection reset. `sht15_measurement()` starts conversions and waits for IRQ/work completion.

Control flow: probe enables optional regulator and notifier, requests clock/data GPIOs and falling-edge IRQ, resets the sensor, creates sysfs group, and registers hwmon. Reads refresh status or humidity+temperature if stale, then calculate compensated values. IRQ disables itself and schedules bottom-half work to read conversion data and wake waiters.

State and persistence: measurements/status are cached for one second. `val_status` mirrors device status and persists heater/low-resolution bits. Supply voltage is cached and updated asynchronously after regulator notifications.

Dependencies/integration: GPIO descriptors, platform IRQs, regulators, workqueues, waitqueues, hwmon legacy API.

Risks: protocol timing is software bit-banged. Checksum mode exists but is never enabled in this file. Regulator notifier scheduling can leave `supply_uv_valid` unused. Remove performs soft reset and regulator cleanup but outstanding work ordering needs hardware testing.

Test signals: GPIO waveform/IRQ completion, timeout/reset path, heater sysfs writes, low battery fault, regulator voltage compensation, cache timing, and probe/remove cleanup.
