# sources/distributed-fs/ceph/src/rgw/madler/crc32iscsi.c

## Purpose
This C file implements CRC-32C/iSCSI using Mark Adler style generated tables. It provides bit-at-a-time, byte-table, word-slicing, remainder-bit, and CRC-combine routines for the reflected polynomial `0x82f63b78`.

## Important APIs, types, and functions
- `crc32iscsi_bit()` computes the CRC one bit at a time and complements before/after processing.
- `crc32iscsi_rem()` extends a CRC with a partial trailing byte of `bits` low-order bits.
- `crc32iscsi_byte()` uses `table_word[0]` as a byte lookup table.
- `crc32iscsi_word()` uses slicing-by-8 lookup tables and 64-bit loads for throughput.
- `crc32iscsi_comb()` combines two CRCs with `len2` bytes in the second message using `multmodp()` and `x8nmodp()`.

## Control flow
The bit and remainder paths update the reflected CRC by shifting right and conditionally xoring the iSCSI polynomial. The byte path folds each byte through `table_byte[(crc ^ data[i]) & 0xff]`. The word path first processes bytes until the input pointer is 8-byte aligned, processes `len >> 3` little-endian 64-bit words using eight table rows, then processes the tail bytes. Combine computes the polynomial multiplier for `x^(8*len2)` and applies it to `crc1`, then xors `crc2`.

## State and persistence behavior
All tables are static constants and all CRC state is passed by value. There is no persistence, allocation, or global mutable state.

## Dependencies and integration points
The file includes `crc32iscsi.h`, which supplies `<stddef.h>` and `<stdint.h>`. It is suitable for RGW checksum code that needs CRC-32C semantics and can choose slower or faster routines depending on platform assumptions.

## Risks and edge cases
- `crc32iscsi_word()` explicitly assumes little-endian integer storage and performs casted 64-bit loads after alignment; portability depends on architecture and strict-aliasing/compiler behavior.
- `crc32iscsi_rem()` masks with `(1U << bits) - 1`; callers must keep `bits` in `0..8` as documented.
- Passing `NULL` returns zero, ignoring the supplied prior CRC. That encodes "CRC of zero bytes" but can hide caller mistakes.
- Table corruption or mismatch would silently produce incompatible checksums, so golden-vector tests are important.

## Test signals
Compare bit, byte, and word outputs for the same data; verify standard CRC-32C check values such as `"123456789"`; test incremental update and `crc32iscsi_comb()` against concatenated buffers; test NULL and zero-length behavior; test all `bits` values in `crc32iscsi_rem()`; and run on little-endian CI with sanitizers if possible.
