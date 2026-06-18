# sources/distributed-fs/ceph-client/drivers/iio/chemical/atlas-ezo-sensor.c

## Purpose
`atlas-ezo-sensor.c` supports Atlas Scientific EZO CO2, O2, and humidity sensors over I2C, exposing one raw channel per device with appropriate scale.

## Important APIs, Types, And Functions
`struct atlas_ezo_device` describes the channel table and conversion delay. `struct atlas_ezo_data` stores the client, device descriptor, lock, and receive buffer. `atlas_ezo_sanitize()` removes a decimal point for fixed integer representation. `atlas_ezo_read_raw()` sends the ASCII `R` read command, waits the device-specific delay, receives up to eight bytes, checks response code `1`, parses the ASCII result, and returns raw or scale. Probe selects chip data through I2C/OF match data.

## Control Flow
Probe builds a direct-mode IIO device for the matched sensor type. Runtime raw reads lock the I2C command/response transaction, issue `R`, wait 950 ms for gas or 350 ms for humidity, receive the response, sanitize decimal formatting, and parse.

## State And Persistence
State is volatile. The driver keeps no calibration or persistent configuration. The mutex serializes command/response traffic.

## Dependencies And Integration Points
It uses I2C SMBus write byte, I2C master receive, firmware match data, and IIO concentration/humidity channel ABIs.

## Risks
`atlas_ezo_read_raw()` rejects any channel whose type is not `IIO_CONCENTRATION` before the switch, which prevents humidity raw and scale reads despite defining a humidity channel. Receive data may not be NUL-terminated before string operations. Short positive receive lengths are not explicitly validated. Decimal removal is simplistic for negative or longer values.

## Test Signals
Test CO2/O2 parsing and scale, humidity channel access, busy response code handling, short/unterminated I2C responses, and concurrent reads.
