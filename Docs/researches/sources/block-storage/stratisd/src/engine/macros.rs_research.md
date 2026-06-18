# File Research: sources/block-storage/stratisd/src/engine/macros.rs

This file defines shared macros used across engine implementations and tests.

Lock/table convenience:
- `get_pool!` and `get_mut_pool!` wrap async pool table read/write access.
- Rename precheck macros implement common idempotent rename logic for pools and filesystems:
  - source missing;
  - same name identity;
  - target name conflict.

User info:
- `set_blockdev_user_info!` updates user info only when changed.

Error message construction:
- `device_list_check_num!` formats singular/plural device-list messages.
- `create_pool_generate_error_string!` builds detailed idempotent create-pool conflict errors.
- `init_cache_generate_error_string!` builds detailed cache-initialization mismatch errors.

Conversion helpers:
- `convert_int!` returns `StratisError` on fallible integer conversion.
- `convert_const!` is for compile-time-known safe conversions.
- `uuid_to_string!` formats UUIDs for names/signatures.

Encryption helper:
- `pool_enc_to_enc!` converts legacy pool encryption info into modern `EncryptionInfo`.

Test-only helpers:
- `strs_to_paths!`
- `convert_test!`
- `retry_operation!`
- `generate_events!`, which scans initialized udev devices for Stratis/crypto signatures.

Role in architecture:
- These macros consolidate repeated idempotence, validation, conversion, and test patterns used by both simulator and real engine code.
