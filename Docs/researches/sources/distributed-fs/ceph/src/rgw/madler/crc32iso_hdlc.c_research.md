# sources/distributed-fs/ceph/src/rgw/madler/crc32iso_hdlc.c

## Purpose
This C file implements reflected CRC-32/ISO-HDLC using generated lookup tables. It mirrors the iSCSI implementation shape but uses polynomial `0xedb88320` and exports `crc32iso_hdlc_*` symbols.

## Important APIs, types, and functions
- `crc32iso_hdlc_bit()` provides the reference bitwise algorithm.
- `crc32iso_hdlc_rem()` processes a partial final byte.
- `crc32iso_hdlc_byte()` performs table-driven byte updates.
- `crc32iso_hdlc_word()` performs slicing-by-8 updates over aligned little-endian 64-bit words.
- `crc32iso_hdlc_comb()` combines two CRCs over concatenated messages.

## Control flow
The implementation complements the prior CRC in the bit/rem paths, shifts reflected bits right, and xors with `0xedb88320` on set low bits. The byte path advances through `table_word[0]`; the word path aligns the pointer, folds 64-bit words through eight table rows, and handles the remaining tail. `multmodp()` and `x8nmodp()` implement polynomial multiplication for combining.

## State and persistence behavior
There is no mutable state or persistence. Lookup and combination tables are static constants.

## Dependencies and integration points
The file includes `crc32iso_hdlc.h` only. It is an RGW-local checksum utility and can be linked into code needing the ISO-HDLC/standard ZIP/Ethernet CRC-32 flavor.

## Risks and edge cases
- `_word` assumes little-endian storage and uses raw 64-bit loads.
- `_rem` depends on valid `bits` input.
- `NULL` input returning zero is documented but may mask misuse.
- Because CRC variants are easy to confuse, tests must distinguish ISO-HDLC from iSCSI/CRC-32C with known check values.

## Test signals
Verify `"123456789"` against the CRC-32/ISO-HDLC check value, compare bit/byte/word equality across sizes and alignments, test combine versus concatenation, test zero-length and NULL behavior, and include partial-bit tests for `_rem`.
