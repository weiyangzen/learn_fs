<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/page-isolation.h -->
# sources/distributed-fs/ceph-client/include/linux/page-isolation.h

## Purpose
This header declares pageblock isolation helpers used by memory hotplug/offline, CMA, compaction, and other page-range isolation workflows.

## Important APIs, types, and functions
With `CONFIG_MEMORY_ISOLATION`, inline helpers test/set/clear the `PB_migrate_isolate` pageblock bit and compare migratetypes. Disabled stubs return false/no-op. `enum pb_isolate_mode` distinguishes memory offlining, CMA allocation, and other isolation. External APIs include `init_pageblock_migratetype()`, `pageblock_isolate_and_move_free_pages()`, `pageblock_unisolate_and_move_free_pages()`, `start_isolate_page_range()`, `undo_isolate_page_range()`, `test_pages_isolated()`, and `page_is_unmovable()`.

## Control flow
Callers mark pageblocks isolate, move free pages out of normal free lists, scan for unmovable pages according to isolation mode, and either complete isolation or undo it. Memory-offline mode treats poison/offline pages specially; CMA mode has different reporting expectations.

## State and persistence
State persists in pageblock migratetype and isolation bits. Isolated ranges remain unavailable to normal allocation until unisolated.

## Dependencies and integration points
It depends on pageblock flags, migratetypes, zones, PFN/page conversion, memory isolation config, memory hotplug, CMA, compaction, and page allocator free lists.

## Risks and test signals
Risks include leaving pageblocks isolated after failure, misclassifying unmovable pages, races with allocator/compaction, CMA starvation, and disabled isolation stubs hiding unsupported workflows. Test memory hotplug offline/online, CMA allocation isolation, compaction with isolate bits, poisoned/offline pages, rollback paths, and `!CONFIG_MEMORY_ISOLATION` builds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/page-isolation.h -->
