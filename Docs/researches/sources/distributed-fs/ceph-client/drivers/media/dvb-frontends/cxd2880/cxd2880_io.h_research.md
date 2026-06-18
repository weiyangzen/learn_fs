# sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/cxd2880/cxd2880_io.h

## Purpose
Defines the CXD2880 register I/O abstraction used to decouple tuner-demod logic from bus transport.

## Important APIs, Types, and Functions
`enum cxd2880_io_tgt` selects SYS or DMD register target. `struct cxd2880_reg_value` stores address/value pairs. `struct cxd2880_io` contains `read_regs`, `write_regs`, `write_reg`, transport object, legacy I2C address fields, slave select, and user pointer. Declares generic helper functions.

## Control Flow
No executable flow. Implementations populate callbacks; driver logic invokes them uniformly.

## State and Persistence
`struct cxd2880_io` persists per frontend instance and stores transport binding. Hardware register state persists only while the device is powered.

## Dependencies and Integration Points
SPI device code fills this interface; tuner-demod, standard-specific, and monitor code consume it for all register access.

## Risks and Edge Cases
Callback lifetime and serialization are external concerns. The I2C fields are unused for CXD2880 SPI but inherited from a generic design, which can confuse new code.

## Test Signals
Attach/init should verify callbacks are populated. Fault-injection transport tests should prove all callers propagate I/O errors cleanly.
