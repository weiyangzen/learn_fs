<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/bcd.c -->
# sources/distributed-fs/ceph-client/lib/bcd.c

## Purpose
Provides binary-coded decimal conversion helpers used by RTCs, firmware tables, and legacy hardware interfaces.

## APIs, Types, and Functions
Exports `_bcd2bin(unsigned char val)` and `_bin2bcd(unsigned val)`. Public wrappers/macros are declared in `linux/bcd.h`.

## Control Flow, State, and Persistence
`_bcd2bin()` converts the low nibble plus ten times the high nibble. `_bin2bcd()` computes decimal tens with `(val * 103) >> 10`, then packs tens into the high nibble and remainder into the low nibble. There is no state.

## Dependencies and Integration
Depends on `linux/bcd.h` and export support. The helpers are always built by `lib/Makefile` as `bcd.o`.

## Risks and Test Signals
Risks include callers passing values outside valid BCD or binary 0-99 ranges; the helpers do not validate and will produce mechanically packed results. Test signals include conversions for 0, 9, 10, 42, 99, invalid BCD nibbles, and RTC driver round trips.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/bcd.c -->
