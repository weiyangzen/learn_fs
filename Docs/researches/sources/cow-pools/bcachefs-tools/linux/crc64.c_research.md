# File Research: sources/cow-pools/bcachefs-tools/linux/crc64.c

Implements table-driven big-endian ECMA-182 CRC64 as `crc64_be()`. It iterates bytes, indexes `crc64table`, and shifts the CRC. The lookup table is in `crc64table.h`.
