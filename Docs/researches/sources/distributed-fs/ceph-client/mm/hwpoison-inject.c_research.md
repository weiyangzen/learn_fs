## sources/distributed-fs/ceph-client/mm/hwpoison-inject.c

Purpose: provides a debugfs-backed software injector for memory failure handling. It lets privileged tests poison or unpoison a PFN and optionally filter candidate pages by backing device, stable page flags, or memory cgroup.

Important APIs and functions: module init creates `debugfs/hwpoison` files `corrupt-pfn`, `unpoison-pfn`, and filter controls. Core functions are `hwpoison_inject()`, `hwpoison_unpoison()`, `hwpoison_filter()`, `hwpoison_filter_dev()`, `hwpoison_filter_flags()`, and, under `CONFIG_MEMCG`, `hwpoison_filter_task()`. It registers the filter with `hwpoison_filter_register()` from memory-failure internals.

Control flow: a write to `corrupt-pfn` requires `CAP_SYS_ADMIN`, validates the PFN, derives its folio, optionally shakes it toward LRU/free state, rejects unsupported non-LRU/non-HugeTLB/non-free pages when filtering is enabled, then invokes `memory_failure(pfn, MF_SW_SIMULATED)`. `-EOPNOTSUPP` is translated to success for unsupported test targets. A write to `unpoison-pfn` calls `unpoison_memory()`.

State and persistence: state is held in static filter variables exposed through debugfs. It persists only while the module is loaded. Exit disables filters, unregisters from memory-failure code, and removes the debugfs subtree.

Dependencies and integration: integrates with debugfs, page cache mappings, inode superblock devices, memcg inode IDs, `stable_page_flags()`, HugeTLB/LRU/free-page tests, and memory-failure recovery.

Risks and test signals: filter checks are intentionally racy and only narrow test scope; final ownership validation happens in `memory_failure()`. Risk areas include poisoning shared dirty pages outside the intended memcg, device filters on anonymous pages, and unsupported page types. Tests should exercise each debugfs knob, capability enforcement, valid/invalid PFNs, memcg filtering, and module unload cleanup.
