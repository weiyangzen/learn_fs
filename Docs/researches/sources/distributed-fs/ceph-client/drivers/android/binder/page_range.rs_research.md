# sources/distributed-fs/ceph-client/drivers/android/binder/page_range.rs

Purpose: manages a Binder mmap page range whose unused pages can be reclaimed by a kernel shrinker. It backs transaction buffers with lazily allocated pages, maps them into the owning process, and moves freed pages to an LRU for memory pressure reclamation.

Important APIs/types/functions: `Shrinker` wraps a C shrinker pointer and `list_lru`; `register` initializes callbacks. `ShrinkablePageRange` owns the process `Mm`, mmap synchronization mutex, spinlocked `Inner`, and pinned page metadata. `register_with_vma`, `use_range`, `use_page_slow`, `stop_using_range`, `copy_from_user_slice`, `read`, `write`, and `fill_zero` are the main Rust APIs. C callbacks are `rust_shrink_count`, `rust_shrink_scan`, and `rust_shrink_free_page`.

Control flow: `register_with_vma` validates the mm, allocates `PageInfo` entries, records VMA address, and tags the VMA with Binder-specific `vm_ops` and private data. `use_range` removes existing pages from LRU or allocates through `use_page_slow`, which takes `mm_lock`, inserts a zeroed highmem page into the VMA, then stores it under the spinlock. `stop_using_range` puts fully unused pages on the LRU. The shrinker walks the LRU, trylocks locks in shrinker-safe order, isolates a page, removes it from the array, drops the LRU lock, zaps the user mapping, and drops the page.

State and persistence: page state is an array of `PageInfo` values with three states: free, available-on-LRU, and used. The array is installed once per mmap and destroyed with the process. Pages persist while allocated but may be reclaimed whenever marked available.

Dependencies and integration points: used by `Process::create_mapping`, `buffer_alloc`, and `buffer_raw_free`. Depends on kernel Rust MM/VMA wrappers, `Page`, list LRU C APIs, Binder module-global `BINDER_SHRINKER`, and `AssertSync` for static `vm_operations_struct`.

Risks: lock ordering is explicit and fragile: mmap lock, spinlock, then LRU spinlock, while shrinker paths use trylocks to avoid inversion. `iterate` uses raw page pointers after dropping the spinlock and is safe only when callers guarantee pages are in use. VMA identity checks are essential to avoid mapping or zapping the wrong address range.

Test signals: mmap size validation, concurrent transactions allocating the same page, buffer free followed by shrinker reclaim, mm teardown races, and copy/read/write across page boundaries. Failures should not produce "Page is null" warnings or stale user mappings after shrinker eviction.
