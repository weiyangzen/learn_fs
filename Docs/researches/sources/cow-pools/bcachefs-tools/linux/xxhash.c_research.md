# File Research: sources/cow-pools/bcachefs-tools/linux/xxhash.c

## Purpose
Linux-compatible xxHash implementation, dual BSD/GPL licensed.

## Key APIs
- `xxh32()`, `xxh64()`
- `xxh32_reset()`, `xxh64_reset()`
- `xxh64_update()`, `xxh64_digest()`
- `xxh32_copy_state()`, `xxh64_copy_state()`

## Behavior
- Implements one-shot 32-bit and 64-bit xxHash.
- Implements streaming 64-bit update/digest.
- Uses unaligned little-endian loads.
- Validates streaming update input, returning `-EINVAL` for `NULL`.

## Dependencies
Uses Linux unaligned access, errno, compiler, kernel, module, string, and `xxhash.h`.
