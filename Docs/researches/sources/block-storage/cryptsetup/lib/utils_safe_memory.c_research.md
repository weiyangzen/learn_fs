# File Research: sources/block-storage/cryptsetup/lib/utils_safe_memory.c

## Purpose
Implements safe allocation, wipe, copy, free, realloc, and size lookup for sensitive memory.

## Key Responsibilities
- Provides explicit non-optimized memory zeroing through backend primitives.
- Provides backend copy helper to avoid sensitive register spill patterns.
- Allocates zeroed memory with a hidden metadata header.
- Attempts to `mlock()` safe allocations.
- Wipes and unlocks memory before free.
- Reallocates by allocating new safe memory, copying bounded old content, and freeing old memory.
- Returns stored safe allocation size.

## Important Details
- Allocation header records size and lock status before aligned data.
- `mlock()` failure is tolerated.
- `crypt_safe_free()` overwrites the stored size with a marker before freeing.
- Zero-size or overflow-prone allocations return `NULL`.

## Dependencies
Uses backend memory primitives from `internal.h` and POSIX `mlock`/`munlock`.
