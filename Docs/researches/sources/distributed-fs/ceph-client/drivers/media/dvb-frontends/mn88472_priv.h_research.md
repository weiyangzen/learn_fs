# sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/mn88472_priv.h

## Purpose
`mn88472_priv.h` contains private includes, firmware name, and the internal runtime state for the MN88472 driver.

## Important APIs, Types, And Functions
`MN88472_FIRMWARE` names `dvb-demod-mn88472-02.fw`. `struct mn88472_dev` stores three I2C clients, three regmaps, the embedded `dvb_frontend`, maximum I2C write size, crystal clock, active flag, TS mode, and TS clock.

## Control Flow
There is no control flow. `mn88472.c` uses the structure for probe/init/tune/status/sleep/remove and the firmware macro in `request_firmware()` and `MODULE_FIRMWARE()`.

## State And Persistence
The structure is in-memory per-device state. Firmware is loaded from the kernel firmware filesystem and then resident on the demodulator until reset/power loss.

## Dependencies And Integration Points
It includes DVB frontend, integer log, public config, firmware loader, and regmap headers. It is private to `mn88472.c`.

## Risks
The bitfield active/TS fields are compact but rely on values from the public header staying within one bit. Client/regmap arrays require consistent bank indexing throughout the driver.

## Test Signals
Compile, probe/remove leak checks, firmware request path, and all three-bank tuning/status paths cover this private contract.
