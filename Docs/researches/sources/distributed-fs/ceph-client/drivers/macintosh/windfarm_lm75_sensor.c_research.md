# sources/distributed-fs/ceph-client/drivers/macintosh/windfarm_lm75_sensor.c

## Purpose
Registers LM75 and DS1775 I2C temperature sensors as Windfarm sensors on PowerMac systems, translating Apple device-tree `hwsensor-location` strings into canonical thermal-loop sensor names.

## Important APIs, Types, And Functions
`struct wf_lm75_sensor` stores DS1775 type, lazy initialization state, the I2C client, and embedded `wf_sensor`. `wf_lm75_get()` clears the shutdown bit on first use, waits 200 ms after wake, reads register 0 with SMBus word access, and converts the raw little-endian value into Windfarm 16.16 fixed point. `wf_lm75_probe()` maps locations to names such as `hd-temp`, `incoming-air-temp`, `optical-drive-temp`, `slots-temp`, and CPU inlet temperatures.

## Control Flow
The I2C driver matches `"MAC,lm75"`, `"MAC,ds1775"`, or OF compatibles `"lm75"`/`"ds1775"`. Probe rejects unsupported or unnamed locations, allocates the wrapper, stores client data, and registers the sensor. Remove nulls `lm->i2c` before unregistering so racing reads fail with `-ENODEV`.

## State, Dependencies, And Integration
State is per I2C client and persists until remove/release. It depends on I2C SMBus helpers, OF properties, and Windfarm sensor registration. Platform drivers consume the resulting names for hard-drive, optical-drive, incoming-air, slot, and CPU inlet loops.

## Risks And Test Signals
The DS1775 flag is recorded but not otherwise used. Sensor discovery is only as complete as the hardcoded location string table. The raw conversion assumes the Apple firmware/device endian format expected by this driver. Test signals include first-read initialization, missing location rejection, supported location mapping, remove/read races returning `-ENODEV`, and sysfs fixed-point temperature output.
