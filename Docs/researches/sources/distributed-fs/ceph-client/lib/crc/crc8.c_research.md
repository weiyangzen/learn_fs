# sources/distributed-fs/ceph-client/lib/crc/crc8.c

## Purpose

`sources/distributed-fs/ceph-client/lib/crc/crc8.c` provides generic CRC8 table population and update helpers, supporting both MSB-first and LSB-first polynomial table construction.

## Important APIs, Types, and Functions

Exported functions are `crc8_populate_msb`, `crc8_populate_lsb`, and `crc8`. Tables are caller-owned arrays of `CRC8_TABLE_SIZE` bytes.

## Control Flow

The populate helpers construct a 256-entry table by repeated doubling/xor of the current polynomial term, one in reverse bit order from `0x80`, the other in regular bit order from `1`. `crc8()` then iterates over input bytes and updates `crc = table[(crc ^ *pdata++) & 0xff]`.

## State and Persistence Behavior

No global table is stored; callers allocate and persist the table they need. The CRC accumulator is passed by value.

## Dependencies and Integration Points

Dependencies include `linux/crc8.h`, printk/module metadata, and exports. Drivers with custom CRC8 polynomials call a populate helper once and reuse the table for data updates.

## Risks and Edge Cases

Callers must choose the correct bit order and polynomial. Using an uninitialized or transient table produces wrong CRCs. The helper does not protect concurrent table population and use.

## Test Signals

Signals include table generation for known MSB/LSB polynomials, CRC8 known vectors, zero-length behavior, incremental equivalence, and callers caching tables safely.

## Read Coverage

Source read size: 87 lines, 2504 bytes.
