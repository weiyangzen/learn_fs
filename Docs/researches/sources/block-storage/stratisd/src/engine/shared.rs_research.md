# File Research: sources/block-storage/stratisd/src/engine/shared.rs

This file contains shared engine helper functions used by both real and simulated implementations.

Pool/cache idempotence:
- `create_pool_idempotent_or_err()`:
  - compares requested data blockdev paths with existing data-tier devices.
  - returns identity if identical, otherwise a detailed conflict error.
- `init_cache_idempotent_or_err()`:
  - compares requested cache paths with existing cache devices.
  - returns empty set-create action if identical, otherwise conflict error.

Key reading:
- `read_key_shared()`:
  - reads key material from a raw file descriptor into a provided buffer.
  - enforces `MAX_STRATIS_PASS_SIZE`.
  - checks for extra data with `poll()` when the buffer fills exactly.
  - avoids closing the passed fd by converting it back with `into_raw_fd()`.

Validation:
- `validate_name()` rejects:
  - empty names;
  - NUL/control characters;
  - `.` and `..`;
  - names over 255 bytes;
  - leading/trailing whitespace;
  - characters not allowed in udev symlinks;
  - absolute paths or multi-component paths.
- `validate_paths()` requires absolute paths.
- `validate_filesystem_size()`:
  - validates max representable size;
  - requires sector alignment;
  - enforces minimum thin device size.
- `validate_filesystem_size_specs()` validates and normalizes filesystem specs, defaulting unspecified size to 1 TiB.

Metadata aggregation:
- `gather_encryption_info()` ensures all devices in a pool are consistently encrypted or unencrypted and builds `PoolEncryptionInfo`.
- `gather_pool_name()` gathers optional names and marks inconsistent names.

Diff helpers:
- `total_used()` combines thin-pool used bytes and metadata size diffs.
- `total_allocated()` combines allocated size and metadata size diffs.

Time helpers:
- `unsigned_to_timestamp()` converts seconds/nanoseconds into `DateTime<Utc>`.
- `now_to_timestamp()` returns current UTC truncated to seconds.

Tests:
- Focus on name validation edge cases, including path-like values, whitespace, control characters, special punctuation, and unicode.

Role in architecture:
- This file holds cross-engine policy: validation, idempotence comparison, size normalization, key length enforcement, and diff arithmetic.
