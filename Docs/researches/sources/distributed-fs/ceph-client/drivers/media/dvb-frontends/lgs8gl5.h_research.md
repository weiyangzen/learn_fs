# sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/lgs8gl5.h

## Purpose
`lgs8gl5.h` defines the board-facing attach interface for the standalone LGS-8GL5 DTMB demodulator driver.

## Important APIs, Types, and Functions
`struct lgs8gl5_config` contains only the demodulator I2C address. `lgs8gl5_attach()` is declared under `CONFIG_DVB_LGS8GL5` and otherwise replaced with a warning stub.

## Control Flow
Callers provide the config and I2C adapter to attach. The C file reads a reset register at that address before returning a configured `dvb_frontend`.

## State and Persistence
The header defines no mutable state. The address is retained by runtime state and used for every demodulator transaction.

## Dependencies and Integration Points
It depends on `<linux/dvb/frontend.h>` and integrates with board drivers using attach-style DVB frontend setup.

## Risks and Edge Cases
There are no fields for TS mode, IF, or alternate-device address, so those are hard-coded in the C file. Misdescribed board wiring cannot be corrected through this config.

## Test Signals
Build-test both Kconfig paths and verify a board can attach, tune, and read status using only the supplied demod address.
