<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/crc32.h -->
# sources/distributed-fs/ceph-client/include/linux/crc32.h

## Purpose

`crc32.h` declares IEEE CRC-32, CRC-32C, optimization reporting, and Ethernet CRC helpers. The source was read as a complete 110-line file.

## Important APIs, Types, and Functions

APIs include `crc32_le()`, alias `crc32()`, `crc32_be()`, `crc32c()`, and optional `crc32_optimizations()`. Optimization flags are `CRC32_LE_OPTIMIZATION`, `CRC32_BE_OPTIMIZATION`, and `CRC32C_OPTIMIZATION`. Ethernet helpers are `ether_crc(length, data)` and `ether_crc_le(length, data)`.

## Control Flow

Callers seed a CRC, process a buffer, and optionally invert before/after according to protocol. LE and BE helpers implement different bit orders for the same IEEE polynomial, while `crc32c()` implements Castagnoli. Ethernet helpers seed with `~0` and bit-reverse where needed.

## State and Persistence Behavior

The header owns no mutable state. Architecture-specific optimized implementations may be selected by the implementation and reported by `crc32_optimizations()`.

## Dependencies and Integration Points

It depends on `linux/types.h` and `linux/bitrev.h`. It integrates with networking, filesystems, storage, crypto/hash code, and architecture CRC acceleration.

## Risks and Edge Cases

The helpers do not perform automatic initial/final inversion except Ethernet macros. CRC-32 and CRC-32C are distinct and not interchangeable. Runtime optimization flags depend on both config and CPU features.

## Test Signals

Signals include IEEE and CRC-32C known vectors, LE/BE distinction tests, Ethernet hash table generation checks, architecture optimized versus generic comparisons, and zero-length/incremental tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/crc32.h -->
