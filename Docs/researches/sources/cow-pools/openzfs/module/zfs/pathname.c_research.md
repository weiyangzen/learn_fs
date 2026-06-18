# File Research: sources/cow-pools/openzfs/module/zfs/pathname.c

## Scope

Minimal pathname buffer allocation utility used by the OpenZFS portability layer. This file allocates and frees the storage inside a `struct pathname`.

## Main Interfaces

- `pn_alloc()` allocates a pathname buffer of `MAXPATHLEN`.
- `pn_alloc_sz()` allocates a pathname buffer of a caller-specified size and records `pn_bufsize`.
- `pn_free()` frees `pn_buf` using the recorded size and clears the pointer and size.

## State And Control Flow

Callers typically allocate `struct pathname` itself on the stack and call `pn_alloc()` or `pn_alloc_sz()` to allocate the internal buffer with `KM_SLEEP`. `pn_free()` releases that buffer and resets the structure fields to prevent stale reuse.

## Dependencies

Uses `struct pathname` definitions, `MAXPATHLEN`, and kernel memory allocation helpers from `sys/kmem.h`.

## Correctness Notes

`pn_free()` relies on `pn_bufsize` matching the original allocation size, which is why `pn_alloc_sz()` records it immediately. Allocation can sleep and must not be used from interrupt context.
