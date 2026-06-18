# sources/distributed-fs/ceph/src/rgw/rgw_xxh_digest.h

## Purpose
`rgw_xxh_digest.h` wraps xxHash XXH3 64-bit streaming digest behind RGW's digest interface style.

## Important APIs, Types, and Functions
`rgw::digest::XXH3` stores `XXH3_state_t`, exposes `digest_size = 8`, initializes and restarts state, updates with bytes, and writes the final digest in big-endian order using RGW byte-swap helpers when native endian is not big.

## Control Flow
Constructors initialize/reset state. Callers call `Update()` zero or more times, then `Final()` to digest the current stream.

## State and Persistence Behavior
State is in-memory hash state only. The final digest byte order is stable for wire/storage uses.

## Dependencies and Integration Points
Depends on `rgw_crc_digest.h`, `xxhash.h` with `XXH_INLINE_ALL`, `<bit>` endian support, and C memory APIs. Used by RGW checksum/digest code when XXH3 is selected.

## Risks
`XXH_INLINE_ALL` in a header can increase compile time and risks ODR surprises if xxhash configuration differs elsewhere. `Final()` does not restart state after digesting. Callers must provide at least 8 bytes of output buffer.

## Test Signals
Compare against known XXH3-64 vectors, incremental vs one-shot updates, empty input, endian-stable byte output, restart reuse, and buffer-size assumptions.
