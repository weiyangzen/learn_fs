# sources/distributed-fs/ceph-client/drivers/hwmon/htu31.c

## Purpose
`htu31.c` drives Measurement Specialties HTU31 temperature and humidity sensors. It exposes temperature/humidity via hwmon, a writable heater control sysfs attribute, and the sensor serial number through debugfs.

## Important APIs, Types, and Functions
`struct htu31_data` stores client, mutex, conversion wait time, latest readings, serial number, and heater state. `htu31_data_fetch_command()` triggers conversion, waits, reads six bytes, verifies CRC8 for temperature and humidity words, and converts values. `htu31_read_serial_number()` reads and CRC-checks the serial number. `heater_enable_show()`/`heater_enable_store()` expose heater control. `htu31_read()` implements hwmon reads, with visibility from `htu31_is_visible()`.

## Control Flow
Probe allocates state, initializes a devm mutex, populates the CRC8 table, reads the serial number, creates debugfs under the I2C client's debugfs directory, and registers hwmon with standard temp/humidity channels plus the heater attribute group. Each hwmon read locks, sends the conversion command, sleeps for combined maximum temperature and humidity conversion time, performs a write-then-read I2C transfer, validates both CRC bytes, updates cached readings, and returns the requested value. Heater writes parse a boolean, lock, send one byte, and update cached heater state.

## State and Persistence
Measurements and heater state are in RAM. Heater state is also programmed into the device and persists according to sensor power state. The serial number is read once at probe and retained for debugfs.

## Dependencies and Integration Points
The driver uses I2C transfers, CRC8 table helpers, cleanup guard mutex syntax, debugfs, hwmon callback registration, and OF/I2C matching (`meas,htu31`, `htu31`).

## Risks
`htu31_read_serial_number()` treats any nonnegative `i2c_transfer()` result as success instead of requiring both messages. Debugfs file lifetime relies on the I2C client's debugfs parent. There is no measurement cache, so frequent reads always trigger conversions. Heater state can diverge if hardware changes externally or a positive short send is returned.

## Test Signals
Test CRC mismatch handling, serial read failure, heater boolean parsing and command selection, temperature/humidity conversion vectors, short I2C transfer behavior, concurrent reads and heater writes under the mutex, and debugfs serial formatting.
