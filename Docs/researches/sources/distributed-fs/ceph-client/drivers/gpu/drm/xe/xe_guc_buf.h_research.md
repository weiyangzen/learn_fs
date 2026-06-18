# sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_guc_buf.h

## Purpose

`xe_guc_buf.h` declares the GuC buffer-cache API and defines cleanup-class helpers for automatic suballocation release.

## Important APIs, Types, and Functions

It exposes cache init, reserve/from-data, release, CPU/GPU pointer, flush/sync, capacity, pointer-to-address lookup, and the inline `xe_guc_buf_is_valid()`. `DEFINE_CLASS(xe_guc_buf, ...)` and `DEFINE_CLASS(xe_guc_buf_from_data, ...)` provide kernel cleanup-scope wrappers.

## Control Flow

Callers initialize a cache, reserve a `struct xe_guc_buf`, check validity, write/read data via CPU pointer, flush before passing GPU address to GuC, and release explicitly or through the cleanup class.

## State and Persistence Behavior

The header itself has no state. It operates on `struct xe_guc_buf_cache` and `struct xe_guc_buf` from `xe_guc_buf_types.h`.

## Dependencies and Integration Points

It depends on Linux cleanup/err helpers and GuC buffer types. It is used by GuC feature opt-ins, ADS policy updates, and any GuC command path needing temporary firmware-visible memory.

## Risks and Edge Cases

The documentation typo says `ref`/`sub-allication`, but the semantic contract is clear. Callers must not dereference CPU/GPU helpers on invalid buffers. Cleanup-class users must ensure the cache outlives the scoped buffer.

## Test Signals

Compile tests should cover cleanup-class use. Runtime/KUnit tests should validate invalid handles, automatic release, and flush-before-GPU-address patterns.
