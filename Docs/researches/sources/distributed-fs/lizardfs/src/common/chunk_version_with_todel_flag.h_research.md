<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/common/chunk_version_with_todel_flag.h -->
# sources/distributed-fs/lizardfs/src/common/chunk_version_with_todel_flag.h

## Purpose

This header defines helpers for packing a chunk version and deletion flag into one 32-bit field.

## Important APIs, Types, and Functions

In namespace `common`, `chunk_version_t` is `uint32_t`, `TODEL_MASK` is the high bit, `VERSION_MASK` is the low 31 bits, and constexpr helpers are `combineVersionWithTodelFlag()`, `getChunkVersion()`, and `getTodelFlag()`.

## Control Flow

All behavior is constexpr bit masking/or-ing.

## State and Persistence Behavior

The packed value is used in chunk info sent in `cstoma::chunkNew` and `cstoma::registerChunks` packets, making the bit layout a protocol contract.

## Dependencies and Integration Points

It integrates chunkserver/master registration messages and any code that interprets deletion state alongside versions.

## Risks and Edge Cases

Versions larger than 31 bits collide with the deletion flag; callers must ensure raw chunk versions fit `VERSION_MASK`. `getTodelFlag()` returns bool from a masked integer.

## Test Signals

Tests should cover packing/unpacking with flag false/true, max 31-bit version, and accidental high-bit input.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/common/chunk_version_with_todel_flag.h -->
