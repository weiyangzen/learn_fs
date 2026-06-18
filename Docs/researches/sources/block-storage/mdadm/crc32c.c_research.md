# File Research: sources/block-storage/mdadm/crc32c.c

## Purpose
`crc32c.c` implements bitwise CRC32, CRC32C, and big-endian CRC32 helpers.

## Behavior
`crc32_le_generic()` computes little-endian CRC with a supplied polynomial. `crc32_le()` uses the Ethernet AUTODIN II polynomial, and `crc32c_le()` uses the Castagnoli CRC32C polynomial. `crc32_be_generic()` and `crc32_be()` implement big-endian Ethernet CRC32.

## Integration Notes
The file is kernel-derived GPLv2 code adapted for mdadm. It uses Linux integer types and takes caller-supplied seed values without imposing final XOR semantics.

## Risks
The implementation is simple and portable but bitwise, so it is slower than table-driven CRC. Callers must choose the correct polynomial and seed/finalization convention.
