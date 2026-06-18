# File Research: sources/cow-pools/bcachefs-tools/fs/data/extents_types.h

## Purpose
Shared type definitions for decoded extent CRCs, decoded pointers, accumulated IO failures, and read flags.

## Main Interfaces and Behavior
- `struct bch_extent_crc_unpacked` normalizes encoded extent metadata: compressed size, uncompressed size, live size, checksum/compression types, offset, nonce, and checksum.
- `struct extent_ptr_decoded` combines a physical pointer, currently active CRC, optional EC stripe pointer, EC reconstruction flags, and retry count.
- `struct bch_io_failures` tracks per-device read/checksum/EC failures plus a print buffer for EC diagnostics. It has one more slot than `BCH_REPLICAS_MAX`.
- `BCH_READ_FLAGS()` defines read-path flags: retry on stale pointer, allow promotion, user-mapped destination, soft/hard read-device requirement, last fragment, forced bounce/clone, retry mode, and poison-check bypass.

## Dependencies
Includes `bcachefs_format.h` for checksum and replica constants.

## Risks and Invariants
- `bch_io_failures` is part of retry/self-heal selection; callers must initialize/exit its print buffer through helpers in `extents.h`.
