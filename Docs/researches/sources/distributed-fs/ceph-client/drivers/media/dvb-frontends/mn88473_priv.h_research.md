# sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/mn88473_priv.h

## Purpose
`mn88473_priv.h` provides the private firmware name and runtime device structure for `mn88473.c`.

## Important APIs, Types, And Functions
`MN88473_FIRMWARE` is `dvb-demod-mn88473-01.fw`. `struct mn88473_dev` stores the three I2C clients, three regmaps, embedded frontend, I2C write limit, active flag, and demodulator clock.

## Control Flow
There is no executable flow. The C file uses these definitions for firmware loading, frontend callbacks, and register-bank access.

## State And Persistence
The structure is per-device in-memory state. The firmware file is an external runtime dependency and is not embedded in the driver.

## Dependencies And Integration Points
It includes DVB frontend, integer log, math64, firmware, regmap, and the public MN88473 config header.

## Risks
Bank index misuse is the main risk because the same numeric register can mean different things on each regmap. Firmware filename changes must be coordinated with packaging and `MODULE_FIRMWARE()`.

## Test Signals
Compile, firmware request, three-bank probe/remove, active gating, and tune/status tests cover this private header.
