# sources/distributed-fs/ceph-client/lib/lz4/lz4defs.h

## Purpose
`lz4defs.h` is the private shared implementation header for the kernel LZ4 compressor, HC compressor, and decompressor. It supplies architecture-specific constants, unaligned memory access wrappers, wild-copy primitives, byte matching helpers, and the internal directive enums used to specialize generic compression/decompression loops.

## Important APIs, types, and functions
The header defines byte-sized aliases (`BYTE`, `U16`, `U32`, `U64`, `uptrval`), block constants (`MINMATCH`, `WILDCOPYLENGTH`, `LASTLITERALS`, `MFLIMIT`, `MATCH_SAFEGUARD_DISTANCE`, masks for token literal/match lengths), and table/dictionary directives. Key helpers are `LZ4_read16()`, `LZ4_read32()`, `LZ4_read_ARCH()`, `LZ4_writeLE16()`, `LZ4_copy8()`, `LZ4_wildCopy()`, `LZ4_NbCommonBytes()`, and `LZ4_count()`. It also defines `limitedOutput_directive`, `tableType_t`, `dict_directive`, `dictIssue_directive`, `endCondition_directive`, and `earlyEnd_directive`.

## Control flow
The header itself has no standalone runtime flow, but its helpers sit directly in hot compression and decompression paths. `LZ4_count()` compares machine words while possible, uses bit-scan operations to locate the first differing byte, then finishes with 32-bit, 16-bit, and byte comparisons near the input limit. `LZ4_wildCopy()` repeatedly copies 8 bytes and intentionally permits bounded over-copy where callers have guaranteed slack.

## State and persistence
The header carries no mutable state. Its compile-time state comes from kernel architecture configuration, including `CONFIG_64BIT`, endian definitions, `BITS_PER_LONG`, and optional `LZ4_DISTANCE_MAX`. These choices affect hash width, common-byte counting, and copy width in all LZ4 objects built from the directory.

## Dependencies and integration points
Dependencies include `linux/unaligned.h`, `linux/bitops.h`, `linux/string.h`, `linux/types.h`, and `linux/lz4.h`. This header is included by all three local LZ4 implementation files and forms the private ABI between generic algorithm code and the public structures declared in `include/linux/lz4.h`.

## Risks and test signals
Because this file defines low-level memory primitives, mistakes affect every LZ4 mode. Risk areas are bounded wild-copy assumptions, unaligned read/write behavior on strict-alignment architectures, endian-specific bit scans, and token/distance constants matching the public LZ4 format. Test signals are architecture-diverse build coverage, KASAN/UBSAN or equivalent bounds testing around block ends, round trips on little- and big-endian targets, and focused tests where matches end exactly at `LASTLITERALS`, `MFLIMIT`, and `MATCH_SAFEGUARD_DISTANCE` boundaries.
