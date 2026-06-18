# sources/distributed-fs/ceph/src/rgw/madler/crc32iso_hdlc.h

## Purpose
This header declares the public reflected CRC-32/ISO-HDLC routines implemented in `crc32iso_hdlc.c`.

## Important APIs, types, and functions
It includes `<stddef.h>` and `<stdint.h>` and declares `crc32iso_hdlc_bit()`, `crc32iso_hdlc_rem()`, `crc32iso_hdlc_byte()`, `crc32iso_hdlc_word()`, and `crc32iso_hdlc_comb()`.

## Control flow
The header has no executable control flow. Its comments define the same contract as the other madler CRC headers: update a prior CRC, return the zero-byte initial CRC for `NULL`, process partial low bits with `_rem`, and combine two CRCs with `_comb`.

## State and persistence behavior
No state or persistence is declared.

## Dependencies and integration points
This is a C API for RGW or utility callers needing standard CRC-32/ISO-HDLC. The interface is independent of Ceph object types.

## Risks and edge cases
`bits` bounds and `_word` platform suitability are not enforced in the header. The function names are the main guard against accidentally using the wrong CRC-32 variant.

## Test signals
Header-level checks should verify C/C++ compilation and symbol availability; implementation tests should validate known ISO-HDLC vectors and parity across bit, byte, word, remainder, and combine APIs.
