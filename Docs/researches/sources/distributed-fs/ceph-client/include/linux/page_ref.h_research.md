<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/page_ref.h -->
# sources/distributed-fs/ceph-client/include/linux/page_ref.h

## Purpose
This header provides atomic page/folio reference-count operations with optional debug tracepoint instrumentation and freeze/unfreeze support for migration/splitting.

## Important APIs, types, and functions
It declares page-ref tracepoints and, under `CONFIG_DEBUG_PAGE_REF`, instrumentation hooks. Public helpers include `page_ref_count()`, `folio_ref_count()`, `page_count()`, `set_page_count()`, `folio_set_count()`, `init_page_count()`, add/sub/inc/dec variants, return/test variants, `page_ref_add_unless_zero()`, folio equivalents, `folio_try_get()`, `folio_ref_try_add()`, `page_ref_freeze()`, `folio_ref_freeze()`, `page_ref_unfreeze()`, and `folio_ref_unfreeze()`.

## Control flow
All ref changes update `page->_refcount` atomically and optionally emit debug tracepoint callbacks when enabled. Try-get adds only when refcount is not zero. Freeze atomically changes an expected count to zero, blocking new speculative gets; unfreeze asserts count is zero, validates a nonzero target count, and publishes it with release ordering.

## State and persistence
Persistent state is the atomic `_refcount` in `struct page`/folio. Debug tracepoint enablement and trace records are external instrumentation state.

## Dependencies and integration points
It depends on atomics, mm types, page flags, tracepoint definitions, VM debug assertions, folio/page lifecycle, page cache, GUP, migration, split, allocator, and memory-management tracing.

## Risks and test signals
Risks include refcount underflow/overflow, freezing with wrong expected count, unfreezing to zero, missing trace events in debug mode, speculative get races after free, and incorrect folio-vs-page usage. Test page allocation/free refcounts, GUP/pagecache pins, migration/split freeze paths, debug tracepoints, VM_BUG_ON assertions, concurrent put/get stress, and `CONFIG_DEBUG_PAGE_REF` builds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/page_ref.h -->
