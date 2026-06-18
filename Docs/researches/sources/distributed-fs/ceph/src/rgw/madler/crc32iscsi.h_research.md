# sources/distributed-fs/ceph/src/rgw/madler/crc32iscsi.h

## Purpose
This header declares the public CRC-32C/iSCSI routines implemented in `crc32iscsi.c`.

## Important APIs, types, and functions
It includes `<stddef.h>` and `<stdint.h>` and declares `crc32iscsi_bit()`, `crc32iscsi_rem()`, `crc32iscsi_byte()`, `crc32iscsi_word()`, and `crc32iscsi_comb()`.

## Control flow
There is no executable control flow in the header. The comments define the contract: the update routines apply bytes at `mem` to a prior CRC, `NULL` returns the initial CRC of zero bytes, `_rem` handles a non-byte-aligned suffix, and `_comb` combines CRCs for concatenated data.

## State and persistence behavior
No state or persistence is declared.

## Dependencies and integration points
Consumers include this header when they need CRC-32C/iSCSI checksums. The API uses C integer types and is independent of Ceph C++ classes.

## Risks and edge cases
The header documents that `bits` must be `0..8` but does not enforce it. It also does not document the little-endian assumption of the `_word` implementation, so callers may need platform gating.

## Test signals
Compile C and C++ users against the header, validate ABI-visible function names, and run the implementation's golden-vector tests for every declared routine.
