# sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/tests/xe_guc_buf_kunit.c

## Purpose

`xe_guc_buf_kunit.c` tests the GuC buffer cache allocator: reservation sizing, uniqueness, non-overlap, reuse, bounds failure, CPU-to-BO flush, pointer-to-GPU-address lookup, data initialization, and cleanup-class behavior.

## Important APIs, Types, and Functions

- Static replacement: `replacement_xe_managed_bo_create_pin_map()` creates a fake BO and optional GGTT node.
- Setup: `guc_buf_test_init()` initializes fake device, GGTT, static stub, and `xe_guc_buf_cache_init`.
- Tests: `test_smallest`, `test_largest`, `test_granular`, `test_unique`, `test_overlap`, `test_reusable`, `test_too_big`, `test_flush`, `test_lookup`, `test_data`, and `test_class`.
- Suite: `guc_buf_suite`.

## Control Flow

Initialization builds a fake PF device, initializes a bounded fake GGTT range, replaces managed BO allocation, and creates the GuC buffer cache. Tests reserve buffers of different sizes, inspect CPU pointers and GGTT addresses, release buffers, validate address ranges and non-overlap, copy data into reserved buffers and flush to the backing BO map, and use the cleanup-class wrapper for automatic release.

## State and Persistence Behavior

The cache owns a fake BO/suballocator, GGTT node state, and reservation/free state. Released ranges are expected to be reusable. Flushed data persists in the backing BO vmap.

## Dependencies and Integration Points

It depends on KUnit static stubs, fake Xe device setup, GGTT KUnit initialization, GuC CT/buffer APIs, managed BO creation, `iosys_map`, and cleanup-class support.

## Risks and Edge Cases

- The fake BO path bypasses real memory-management behavior; this is allocator/API coverage, not full hardware coverage.
- Pointer arithmetic tests assume reserved CPU ranges can be compared directly.
- The too-big case ensures invalid buffers are safe to release, guarding cleanup paths.

## Test Signals

Passing tests indicate correct allocation granularity, no overlapping CPU/GPU ranges, stable reuse, flush propagation, lookup bounds, copied data initialization, and cleanup-class release behavior.
