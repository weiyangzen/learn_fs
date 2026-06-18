# sources/distributed-fs/ceph-client/include/uapi/linux/map_to_14segment.h

Purpose: provides UAPI-visible helpers and default ASCII lookup tables for mapping characters to 14-segment display bitmasks.

Important APIs and types: bit indices `BIT_SEG14_*` name all segment positions plus reserved bits. `struct seg14_conversion_map` stores 128 big-endian 16-bit entries. `map_to_seg14()` validates an ASCII index and returns a CPU-endian segment mask or `-EINVAL`. `SEG14_CONVERSION_MAP`, `SEG14_DEFAULT_MAP`, `MAP_TO_SEG14_SYSFS_FILE`, `_SEG14`, and `MAP_ASCII14SEG_ALPHANUM` provide static map construction and sysfs naming.

Control flow: a display driver instantiates a conversion map, optionally exposes it through a sysfs binary-like attribute, then converts each character to a segment bitmask before driving hardware. Userspace can replace the table if the driver exposes `map_seg14`.

State and persistence: map state is a driver-owned `struct seg14_conversion_map`; updates via sysfs are runtime driver state and not persisted unless userspace reloads them.

Dependencies and integration points: depends on `linux/errno.h`, `linux/types.h`, and `asm/byteorder.h`. Integrates LED/LCD/front-panel drivers and userspace custom character map tooling.

Risks and test signals: risks include endian conversion mistakes, accepting non-ASCII indexes, table size mismatch in sysfs writes, reserved-bit leakage, and visually ambiguous glyph mappings. Test `map_to_seg14()` bounds, known digits/letters, big/little-endian builds, sysfs map replacement size checks, and rendered display output.
