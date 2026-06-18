# sources/distributed-fs/ceph-client/include/linux/ts-nbus.h

## Purpose
Declares a tiny interface for Technologic Systems NBUS register access.

## Important APIs, Types, And Functions
Forward-declares `struct ts_nbus` and exports `ts_nbus_read()` and `ts_nbus_write()`, using 8-bit register addresses and 16-bit values.

## Control Flow
No implementation is present. Callers pass an NBUS handle, address, and either receive or write a 16-bit value; error handling is via integer return codes.

## State, Persistence, And Dependencies
State is opaque in `struct ts_nbus`. The header itself assumes fixed-width integer types are visible from including context.

## Integration Points
Used by platform or MFD child drivers sharing a TS NBUS controller.

## Risks And Test Signals
Risks include endianness/addressing assumptions and lack of visible locking contract. Test signals are controller read/write tests, invalid address handling, and concurrent child-driver access coverage.
