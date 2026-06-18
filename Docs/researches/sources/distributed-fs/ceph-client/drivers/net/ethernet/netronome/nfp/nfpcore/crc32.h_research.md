# sources/distributed-fs/ceph-client/drivers/net/ethernet/netronome/nfp/nfpcore/crc32.h

## Purpose

`nfpcore/crc32.h` provides small inline helpers for POSIX CRC32 calculation used by NFP core code, especially resource keys whose comments elsewhere describe CRC32-POSIX over identification strings.

## Important APIs, Types, and Functions

It declares `crc32_posix_end()` and `crc32_posix()`. `crc32_posix_end()` appends the little-byte sequence of the total length to an in-progress big-endian CRC32 state and returns the complemented final value. `crc32_posix()` performs `crc32_be(0, buff, len)` and finalizes it with the buffer length.

## Control Flow

The helpers are straight-line inlines. Finalization loops while `total_len` is nonzero, extracts the low byte, updates the big-endian CRC, shifts the length, and returns bitwise-not of the final CRC.

## State and Persistence Behavior

There is no persistent state. Results are deterministic for a given buffer and length and are suitable for matching firmware/resource table keys.

## Dependencies and Integration Points

The header depends on Linux `crc32_be()` from `<linux/crc32.h>`. It integrates with nfpcore resource lookup/key generation code.

## Risks and Edge Cases

Length finalization is part of POSIX CRC32 semantics; callers that use plain CRC32 will not match NFP resource keys. Empty buffers skip the length loop and return complement of the initial CRC state. The function consumes `size_t`, so results are platform-width aware for very large lengths.

## Test Signals

Compare known POSIX CRC32 vectors, empty input, short identification strings, and resource key values against firmware/resource table expectations.
