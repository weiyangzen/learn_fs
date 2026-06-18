# File Research: sources/cow-pools/bcachefs-tools/raid/memory.h

## Purpose
Public declarations and constants for RAID memory helpers.

## Constants
- `RAID_MALLOC_ALIGN`: 256-byte alignment.
- `RAID_MALLOC_DISPLACEMENT`: `7 * 256`, used to reduce cache address aliasing across contiguous block buffers.

## APIs
- `raid_malloc()`
- `raid_malloc_align()`
- `raid_malloc_vector()`
- `raid_malloc_vector_align()`
- `raid_mrand_vector()`
- `raid_mtest_vector()`

## Notes
The displacement comment records empirical throughput gains from avoiding cache/prefetch aliasing for multi-buffer RAID operations.
