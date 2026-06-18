# File Research: sources/block-storage/parted/libparted/labels/efi_crc32.c

This file provides the CRC32 implementation used by EFI/GPT code.

Key API:
- `__efi_crc32(const void *buf, unsigned long len, uint32_t seed)`: computes a table-driven CRC32 over `len` bytes using the caller-supplied seed.

Behavior:
- Uses a static 256-entry CRC32 table for polynomial `0xedb88320`.
- Iterates byte-by-byte, updating `crc32val` as `crc32_tab[(crc32val ^ s[i]) & 0xff] ^ (crc32val >> 8)`.
- GPT wraps this helper with seed `~0L` and final xor `~0L`.

Integration:
- Included through libparted’s CRC32 declaration path and used by `gpt.c` as `__efi_crc32()`.
- Source comments trace this implementation to Gary S. Brown’s public-domain CRC code with later EFI-oriented modifications.

Risk notes:
- No NULL guard exists; callers must pass a valid buffer for nonzero length.
- The function is pure with respect to input memory and has no allocation or I/O.
