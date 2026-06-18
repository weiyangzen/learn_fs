# sources/distributed-fs/lizardfs/external/crcutil-1.0/code/crc_casts.h

## Purpose

`crc_casts.h` centralizes conversions between crcutil CRC value types and smaller integer representations. It exists so scalar CRC types and compound CRC types such as `uint128_sse2` can share generic table and byte-processing code while still providing specialized downcasts.

## Important APIs and macros

`Downcast<Crc, Result>(const Crc &x)` defaults to `static_cast<Result>(x)` and can be specialized by complex CRC classes. `TO_BYTE(x)` extracts the least significant byte by downcasting to `uint8`. `CrcFromUint64<Crc>(uint64 lo, uint64 hi = 0)` constructs a CRC value from one or two 64-bit words, using `SHIFT_LEFT_SAFE` when the target is wider than 64 bits. `Uint64FromCrc<Crc>(const Crc&, uint64 *lo, uint64 *hi = NULL)` extracts low and optional high 64-bit words.

## Control flow, state, and persistence

The file has no runtime state. The functions are inline templates used inside CRC table lookup loops, GF arithmetic, and tests/examples that need to serialize or inspect CRC values.

## Dependencies and integration points

It includes `base_types.h` and `platform.h`. `generic_crc.h`, `gf_util.h`, `rolling_crc.h`, and `uint128_sse2.h` depend on it. `uint128_sse2.h` supplies specializations for downcasting and two-word conversion.

## Risks and test signals

For wider CRC types, callers are responsible for ensuring `hi` is meaningful and that shifting/composition matches the CRC type's byte ordering. `Uint64FromCrc` writes `*hi` in the wide case without checking for null, so callers must pass `hi` when `sizeof(crc) > sizeof(*lo)`. Test signals include round-tripping scalar and `uint128_sse2` values through `CrcFromUint64`/`Uint64FromCrc`, and verifying `TO_BYTE` in table-driven CRC loops.
