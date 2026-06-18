## sources/distributed-fs/ceph-client/arch/arm/mm/copypage-fa.c

### Purpose
Provides Faraday FA526-optimized implementations of `copy_user_highpage` and `clear_user_highpage` for page fault and COW paths.

### Important APIs, Types, And Functions
Exports `fa_user_fns` with `fa_copy_user_highpage` and `fa_clear_user_highpage`. The private `fa_copy_user_page` inline assembly copies 32-byte chunks using ARM load/store multiple and CP15 clean+invalidate operations.

### Control Flow
Both public functions temporarily map highmem pages with `kmap_atomic`, run a PAGE_SIZE loop in inline assembly, perform write-buffer drain, and unmap. Clear fills registers with zero and stores them across the page.

### State, Dependencies, And Integration
No persistent state. Depends on highmem atomic mappings, CP15 cache operations, and the CPU user function selection path. Integrates with generic page copy/clear hooks used by memory management.

### Risks And Test Signals
Risks are incorrect clobbers, cacheline maintenance ordering, and assumptions about page size or FA cache behavior. Validate with FA build coverage, highmem page copy tests, COW faults, fork/exec stress, and cache aliasing data-integrity checks.
