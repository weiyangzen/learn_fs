# File Research: sources/cow-pools/nilfs-utils/lib/crc32.c

Implements table-driven little-endian CRC32 using polynomial `0xedb88320`. The only exported function, `crc32_le()`, iterates over input bytes and updates the seed through a 256-entry lookup table.
