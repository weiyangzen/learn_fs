# sources/distributed-fs/ceph-client/drivers/macintosh/windfarm_max6690_sensor.c

## Purpose
Registers MAX6690 I2C external-temperature readings as Windfarm sensors for backside, north-bridge, and GPU ambient temperatures used by PowerMac thermal loops.

## Important APIs, Types, And Functions
`struct wf_6690_sensor` stores the I2C client and embedded `wf_sensor`. `wf_max6690_get()` reads `MAX6690_EXTERNAL_TEMP` via SMBus byte access and returns it as 16.16 fixed point. `wf_max6690_probe()` maps `hwsensor-location` values `"BACKSIDE"`/`"SYS CTRLR AMBIENT"` to `backside-temp`, `"NB Ambient"` to `north-bridge-temp`, and `"GPU Ambient"` to `gpu-temp`.

## Control Flow
The module is a standard I2C driver matching `"MAC,max6690"` or OF compatible `"max6690"`. Probe rejects missing or unrecognized location strings, allocates a sensor wrapper, attaches it to client data, and registers it with Windfarm. Remove sets `max->i2c` to NULL and unregisters.

## State, Dependencies, And Integration
State is per I2C client. It depends on SMBus reads, OF properties, and Windfarm sensor registration. PM72, PM81, PM112, PM121, and related model drivers consume the canonical names in backside, north-bridge, and GPU control loops.

## Risks And Test Signals
The chip is assumed firmware-initialized and only its external temperature register is surfaced. Location-string drift causes silent `-ENXIO` probe failure for otherwise working chips. Test signals include supported/unsupported location probes, SMBus read failures, sysfs fixed-point values, and model-loop behavior when `backside-temp`, `north-bridge-temp`, or `gpu-temp` is missing.
