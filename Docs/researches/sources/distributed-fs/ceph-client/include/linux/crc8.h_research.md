<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/crc8.h -->
# sources/distributed-fs/ceph-client/include/linux/crc8.h

## Purpose

`crc8.h` declares table population and calculation helpers for configurable CRC-8 polynomials. The source was read as a complete 101-line file.

## Important APIs, Types, and Functions

Constants include `CRC8_INIT_VALUE`, `CRC8_GOOD_VALUE(table)`, `CRC8_TABLE_SIZE`, and `DECLARE_CRC8_TABLE(table)`. APIs include `crc8_populate_lsb()`, `crc8_populate_msb()`, and `crc8()`.

## Control Flow

Callers allocate a 256-entry table, populate it with the polynomial and bit direction, then call `crc8()` with a data pointer, byte count, and seed or previous CRC. Validation protocols may compare the final value against `CRC8_GOOD_VALUE()`.

## State and Persistence Behavior

CRC tables are caller-owned mutable arrays, often static after population. The header owns no global mutable state.

## Dependencies and Integration Points

It depends on `linux/types.h` and integrates with device protocols that use custom CRC-8 polynomials.

## Risks and Edge Cases

The caller must choose LSB or MSB table population to match the protocol's bit order. The helper does not complement the generated CRC; callers are responsible for final inversion/insertion. Table size must be exactly 256 entries.

## Test Signals

Signals include table population known-vector tests for LSB and MSB polynomials, one-shot and chunked `crc8()` equivalence, validation of `CRC8_GOOD_VALUE()`, and driver protocol checksum tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/crc8.h -->
