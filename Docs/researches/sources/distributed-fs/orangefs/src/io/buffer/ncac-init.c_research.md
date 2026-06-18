# sources/distributed-fs/orangefs/src/io/buffer/ncac-init.c

## Purpose
Initializes global NCAC cache resources: request pool, extent pool, cache memory metadata, free lists, request-progress lists, inode table, radix callbacks, and locks.

## Important APIs, Types, And Functions
Defines global `NCAC_dev` and `inode_arr`. Public entry is `cache_init`; helper functions are `radix_get_value`, `init_free_extent_list`, `init_free_req_list`, `init_cache_stack_list`, and placeholder `extlog2`.

## Control Flow
`cache_init` chooses the request count, allocates/zeros request objects, initializes free request list and lock, sets extent size/cache size/cache memory, computes extent count, allocates/zeros extents, initializes extent free list and cache stack lists, initializes prepare/buffer-complete/complete lists, clears inode buckets, and records radix tree callbacks.

## State And Persistence
All state is process-local global NCAC state. Extent `addr` fields point into caller-provided `info->cachespace`; request and extent metadata are heap-allocated and not freed here. `extlog2` currently returns 15 regardless of the configured extent size, effectively assuming 32 KiB extents for index shifts.

## Dependencies And Integration Points
Depends on `internal.h`, `ncac-list.h`, and `radix.h`. It must run before any `cache_*_post` operation.

## Risks And Test Signals
Risks include checking `free_extent_src` for NULL after `memset`, no cleanup function, `extlog2` hardcoding, no validation that extent size divides cache size or is a power of two, and allowing NULL cache memory after warning. Tests should initialize varied cache sizes, verify free-list counts and extent addresses, reject invalid configs, and exercise non-32KiB extents to expose index errors.
