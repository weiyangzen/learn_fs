# sources/distributed-fs/ceph-client/lib/zstd/common/mem.h

## Purpose
`mem.h` provides the kernel-adapted primitive memory I/O layer for this Zstd copy. It defines fixed-width aliases and inline unaligned native, little-endian, big-endian, and byte-swap helpers used throughout bitstream, entropy, frame, and match-finding code.

## Important APIs and Types
The file defines `BYTE`, `U8/S8`, `U16/S16`, `U32/S32`, and `U64/S64`. It exposes `MEM_32bits()`, `MEM_64bits()`, `MEM_isLittleEndian()`, native `MEM_read16/32/64/ST()` and `MEM_write16/32/64()`, endian-specific `MEM_readLE16/24/32/64/ST()`, `MEM_writeLE16/24/32/64/ST()`, `MEM_readBE32/64/ST()`, `MEM_writeBE32/64/ST()`, and `MEM_swap32/64/ST()`.

## Control Flow and State
All helpers are `static inline` and stateless. Native reads/writes use `get_unaligned()` and `put_unaligned()`. Endian helpers use Linux `get_unaligned_le*` and `get_unaligned_be*` routines. Size-t variants branch on `sizeof(size_t)` to select 32-bit or 64-bit behavior, making bitstream serialization portable across kernel architectures.

## Dependencies and Integration Points
Dependencies are Linux headers: `linux/unaligned.h`, `linux/compiler.h`, `linux/swab.h`, and `linux/types.h`, plus `debug.h` for static assertion support. Entropy code uses these helpers for table headers, jump tables, packed bit containers, and 64-bit spread writes; changing them affects almost every Zstd source file.

## Risks and Test Signals
The main risks are architecture portability and assumptions about `__LITTLE_ENDIAN`. Incorrect endian detection or unaligned behavior would corrupt frame headers and entropy streams. `MEM_writeLE24()` has a mixed 16-bit helper plus byte store, so 24-bit frame/block fields deserve coverage. Tests should run known Zstd vectors on little- and big-endian builds where available, exercise unaligned addresses, verify 32-bit versus 64-bit `size_t` paths, and compare packed table/jump-table byte output against upstream vectors.
