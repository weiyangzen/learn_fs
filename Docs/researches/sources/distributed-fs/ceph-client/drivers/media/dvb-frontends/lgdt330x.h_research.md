# sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/lgdt330x.h

## Purpose
`lgdt330x.h` defines the public configuration and attach API for LGDT3302/LGDT3303 demodulators.

## Important APIs, Types, and Functions
`lg_chip_type` enumerates `UNDEFINED`, `LGDT3302`, and `LGDT3303`. `struct lgdt330x_config` selects the demod chip, serial MPEG output bit, optional RF-input callback, optional TS-parameter callback, LGDT3303 clock polarity flip, and a driver-filled `get_dvb_frontend()` callback. `lgdt330x_attach()` creates or returns a frontend when the driver is enabled; otherwise the inline stub warns and returns `NULL`.

## Control Flow
Board code supplies the config to `lgdt330x_attach()`, which wraps I2C-client creation. Probe copies the config, fills `get_dvb_frontend`, selects chip-specific ops, and returns the frontend through that callback.

## State and Persistence
This header defines configuration only. Runtime state is allocated in the C file and the demodulator register state is rebuilt during init and tuning.

## Dependencies and Integration Points
It depends on Linux DVB frontend types and I2C client types. Integration is with older board drivers that still use attach-style frontend construction.

## Risks and Edge Cases
The `serial_mpeg` field is a raw register bit value rather than an enum, and differs between LGDT3302 and LGDT3303 according to implementation comments. `clock_polarity_flip` applies only to LGDT3303 and accepts multiple magic variants.

## Test Signals
Build-test enabled and disabled Kconfig paths, attach with both chip enum values, and verify caller callbacks are preserved after probe copies the config.
