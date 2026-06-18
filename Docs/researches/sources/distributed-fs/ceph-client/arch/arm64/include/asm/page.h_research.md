# sources/distributed-fs/ceph-client/arch/arm64/include/asm/page.h

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/include/asm/page.h -->
## sources/distributed-fs/ceph-client/arch/arm64/include/asm/page.h

### Purpose
`page.h` declares ARM64 page operations and page-level MM helpers, including copy/clear page, highpage handling, MTE tag clearing, pfn validation, and default VMA data flags.

### Important APIs, Types, And Functions
Exports include `copy_page()`, `clear_page()`, `copy_user_highpage()`, `copy_highpage()`, `vma_alloc_zeroed_movable_folio()`, `tag_clear_highpages()`, `copy_user_page()`, `pgtable_t`, `pfn_is_map_memory()`, and `VMA_DATA_DEFAULT_FLAGS`.

### Control Flow
MM and filesystem paths call page copy/clear helpers during allocation, COW, page cache operations, and highpage handling. MTE-aware paths clear tags for user pages when needed.

### State, Persistence, And Dependencies
State is page contents, page tags, and VMA flags. It depends on page definitions, pgtable types, memory layout, personality flags, and generic getorder.

### Integration Points
Used by generic MM, page cache, file I/O, networking buffers, and memory-mapped files.

### Risks
Copy/clear routines must preserve alignment and tagging semantics. Wrong executable default flags affect W^X/security and legacy behavior.

### Test Signals
Run MM selftests, page cache stress, MTE tag-clearing tests, COW/fork workloads, and page-size config builds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/include/asm/page.h -->
