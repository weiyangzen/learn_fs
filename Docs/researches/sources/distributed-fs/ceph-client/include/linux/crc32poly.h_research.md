<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/crc32poly.h -->
# sources/distributed-fs/ceph-client/include/linux/crc32poly.h

## Purpose

`crc32poly.h` names the integer polynomial constants used by the kernel CRC-32 helpers. The source was read as a complete 14-line file.

## Important APIs, Types, and Functions

It defines `CRC32_POLY_LE` as `0xedb88320`, `CRC32_POLY_BE` as `0x04c11db7`, and `CRC32C_POLY_LE` as `0x82f63b78`.

## Control Flow

There is no runtime flow. The constants are used at compile time by table generation, tests, or implementations.

## State and Persistence Behavior

No state is owned.

## Dependencies and Integration Points

It has no includes and integrates with CRC32 implementations and table builders.

## Risks and Edge Cases

Polynomial constants encode bit order. Using the LE reflected polynomial in a BE algorithm, or vice versa, produces incompatible CRCs.

## Test Signals

Signals include table-generation tests, cross-checking constants against `crc32.h` documentation, and known-vector CRC validation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/crc32poly.h -->
