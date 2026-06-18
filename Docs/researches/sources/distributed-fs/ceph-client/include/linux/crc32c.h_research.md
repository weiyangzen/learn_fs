<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/crc32c.h -->
# sources/distributed-fs/ceph-client/include/linux/crc32c.h

## Purpose

`crc32c.h` is a compatibility wrapper that includes `linux/crc32.h` for CRC-32C access. The source was read as a complete 7-line file.

## Important APIs, Types, and Functions

It introduces no new API. Consumers get `crc32c()` and related CRC32 declarations from `crc32.h`.

## Control Flow

There is no runtime flow; preprocessing forwards to `crc32.h`.

## State and Persistence Behavior

No state is owned by this header.

## Dependencies and Integration Points

It depends only on `linux/crc32.h` and preserves include compatibility for code that historically included `crc32c.h`.

## Risks and Edge Cases

Semantic risks are those of `crc32.h`; this file's main concern is avoiding duplicate or divergent CRC-32C declarations.

## Test Signals

Signals include compile coverage for direct `crc32c.h` inclusion and known-vector tests for `crc32c()` through that include path.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/crc32c.h -->
