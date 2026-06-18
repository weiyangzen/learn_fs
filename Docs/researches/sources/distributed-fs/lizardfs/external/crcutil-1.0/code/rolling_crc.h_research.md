# sources/distributed-fs/lizardfs/external/crcutil-1.0/code/rolling_crc.h

## Purpose

`rolling_crc.h` implements a generic rolling CRC adapter for fixed-size windows, suitable for Rabin-fingerprint-like sliding-window use. It lets callers compute the first window with the underlying CRC implementation and then update the CRC when one byte leaves and one byte enters.

## Important APIs and types

`RollingCrc<CrcImplementation>` requires the implementation to provide `Crc`, `TableEntry`, `Word`, `CrcDefault()`, and `Base()`. It exports `Start(const void *data)`, `Roll(const Crc &old_crc, size_t byte_out, size_t byte_in)`, `Init(const CrcImplementation&, size_t roll_window_bytes, const Crc &start_value)`, `StartValue()`, and `WindowBytes()`.

## Control flow, state, and persistence

`Init()` stores a borrowed pointer to the CRC implementation, the window size, and the start value. It precomputes `out_[256]` for outgoing byte corrections using `GfUtil` powers and `MultiplyUnnormalized`, and `in_[256]` from the implementation's last word table. `Start()` computes the CRC of the first window by delegating to the implementation. `Roll()` shifts the old CRC by one byte, applies the incoming-byte table entry, and xors the outgoing-byte correction.

## Dependencies and integration points

It includes `base_types.h` and `crc_casts.h`. It relies on access to `crc.crc_word_`, which is possible because `GenericCrc` declares the corresponding `RollingCrc` specialization as a friend. This tight coupling means alternative implementations must expose compatible internals or provide their own rolling class, as `Crc32cSSE4` does.

## Risks and test signals

The class stores a raw pointer to the CRC implementation, so lifetime is the caller's responsibility. `byte_out` and `byte_in` are `size_t`, but table indexing assumes byte values 0..255. Test signals include comparing `Roll()` output against recomputing `Start()` for every window over random buffers, window sizes 1 and large sizes, nonzero start values, canonical and noncanonical CRCs, and invalid-byte defensive tests if callers can pass wider values.
