# sources/distributed-fs/ceph-client/drivers/media/common/b2c2/Makefile

## Purpose
This Makefile builds the common B2C2 FlexCop DVB support object.

## Important APIs, Types, and Functions
It composes `b2c2-flexcop.o` from `flexcop.o`, `flexcop-fe-tuner.o`, `flexcop-i2c.o`, `flexcop-sram.o`, `flexcop-eeprom.o`, `flexcop-misc.o`, and `flexcop-hw-filter.o`. It maps that composite object to `CONFIG_DVB_B2C2_FLEXCOP`.

## Control Flow
Kbuild links all common FlexCop components together, with include paths added for DVB frontend and tuner headers.

## State and Persistence
No runtime state is present.

## Dependencies and Integration Points
Bus-specific PCI/USB FlexCop drivers depend on this common object for shared device initialization, frontend discovery, I2C, SRAM, EEPROM, and filtering support.

## Risks and Test Signals
Build tests should confirm include paths cover all optional frontend/tuner headers and that all referenced common helpers are linked into the composite object.
