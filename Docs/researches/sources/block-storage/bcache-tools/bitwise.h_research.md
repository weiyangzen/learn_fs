# File Research: sources/block-storage/bcache-tools/bitwise.h

This GPL-2.0 header is copied from Linux swab/endian helpers and supplies byte-swap macros plus `cpu_to_le*` and `le*_to_cpu` conversions for userspace. It detects local endianness with `__BYTE_ORDER == __LITTLE_ENDIAN`.

The bcache tools rely on this file for portable conversion between disk little-endian superblocks and native in-memory values.
