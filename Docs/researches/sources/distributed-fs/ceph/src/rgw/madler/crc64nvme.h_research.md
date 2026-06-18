# sources/distributed-fs/ceph/src/rgw/madler/crc64nvme.h

## Purpose
This header declares the public CRC-64/NVME routines implemented in `crc64nvme.c`.

## Important APIs, types, and functions
It includes `<stddef.h>` and `<stdint.h>` and declares `crc64nvme_bit()`, `crc64nvme_rem()`, `crc64nvme_byte()`, `crc64nvme_word()`, and `crc64nvme_comb()`.

## Control flow
There is no executable control flow. Comments specify byte update behavior, `NULL` behavior, partial-bit handling, and CRC combination semantics.

## State and persistence behavior
No state or persistence is declared.

## Dependencies and integration points
This is a small C ABI header for code that needs CRC-64/NVME. It does not expose Ceph-specific types.

## Risks and edge cases
The header does not enforce the documented `bits` range or advertise the implementation's little-endian fast-path assumption. Users should select `_byte` or platform-gate `_word` on non-little-endian targets.

## Test signals
Compile users against the declarations and run implementation tests for known NVME CRC-64 vectors, parity among update variants, partial-bit behavior, and combine behavior.
