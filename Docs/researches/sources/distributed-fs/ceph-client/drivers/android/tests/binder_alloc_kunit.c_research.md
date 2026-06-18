# sources/distributed-fs/ceph-client/drivers/android/tests/binder_alloc_kunit.c

## Purpose
`binder_alloc_kunit.c` is a KUnit suite for Binder allocator page allocation, LRU, free, and reclaim behavior. It exhaustively generates buffer alignment and free-order cases to verify that pages shared across adjacent buffers are placed on or removed from the LRU correctly.

## Important APIs, Types, And Functions
Important definitions include `BINDER_MMAP_SIZE`, `BUFFER_NUM`, `BUFFER_MIN_SIZE`, `TOTAL_EXHAUSTIVE_CASES`, `enum buf_end_align_type`, `struct binder_alloc_test_case_info`, and `struct binder_alloc_test`. Helpers include stringification functions, `check_buffer_pages_allocated`, allocation/free/reclaim helpers, `binder_alloc_test_alloc_free`, `permute_frees`, `gen_buf_sizes`, and `gen_buf_offsets`. Test cases are `binder_alloc_test_init_freelist`, `binder_alloc_test_mmap`, and slow `binder_alloc_exhaustive_test`. Fixture functions are `binder_alloc_test_init` and `binder_alloc_test_exit`.

## Control Flow
The fixture creates a private `binder_alloc`, initializes a test `list_lru`, attaches an mm, opens an anonymous inode with an mmap handler, and maps 128 KiB of Binder transaction memory. The exhaustive test generates five-buffer end alignments, tests front-page and back-page sharing arrangements, permutes all free orders, allocates buffers, frees them, verifies expected LRU pages, reallocates from LRU, verifies the LRU drains, frees again, then walks the LRU through `binder_alloc_free_page` until all pages are reclaimed.

## State And Persistence
Per-test state holds allocator state, test LRU, backing file, and mmap address. The allocator's page array, rb trees, and LRU are mutated heavily during each generated case and cleaned up in the fixture exit. The test attaches an mm so allocator mmap and shrinker paths can operate like normal Binder usage.

## Dependencies
The test depends on KUnit, anon inodes, file/mm helpers, seq_buf, `binder_alloc.h`, `binder_internal.h`, and KUnit-exported Binder symbols such as `__binder_alloc_init`, `binder_alloc_buffer_size`, `binder_alloc_new_buf`, `binder_alloc_free_buf`, `binder_alloc_free_page`, and `binder_vm_fault`.

## Integration Points
The Makefile includes this object under `CONFIG_ANDROID_BINDER_ALLOC_KUNIT_TEST`. It directly exercises `binder_alloc.c` internals and is the strongest regression signal for the allocator's page sharing and shrinker logic.

## Risks
The exhaustive suite is intentionally slow: 3125 alignment combinations times two placement modes times 120 free orders. The test focuses on page/LRU behavior and does not cover all allocator security properties, async spam accounting, or user copy bounds. It also depends on KUnit-exported internal symbols, so namespace/export drift can break the suite even when allocator runtime code still builds.

## Test Signals
Run the `binder_alloc` KUnit suite, confirm `TOTAL_EXHAUSTIVE_CASES` runs, zero failures, no leaked LRU items at exit, no installed pages after reclaim, successful mmap initialization, and clean build with `MODULE_IMPORT_NS("EXPORTED_FOR_KUNIT_TESTING")`.
