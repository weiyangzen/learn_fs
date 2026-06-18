<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/proc/meminfo.c -->
## sources/distributed-fs/ceph-client/fs/proc/meminfo.c

Purpose: implements `/proc/meminfo`, the central text summary of system memory, swap, slab, vmalloc, hugepage, zswap, GPU, CMA, poisoned, unaccepted, and architecture-specific memory counters.

Important APIs and functions: `meminfo_proc_show` gathers counters via `si_meminfo`, `si_swapinfo`, `vm_memory_committed`, `si_mem_available`, `global_node_page_state`, `global_zone_page_state`, `pcpu_nr_pages`, `hugetlb_report_meminfo`, `memtest_report_meminfo`, and weak `arch_report_meminfo`. `show_val_kb` formats page counts as kB; `proc_meminfo_init` registers the permanent proc file.

Control flow: each read builds a live snapshot: base RAM/swap totals, file cache adjusted for swapcache and buffers, LRU lists, slab reclaimability, writeback/dirty state, page table usage, commit limit, vmalloc, per-config optional sections, hugepage data, and architecture extensions. Init creates a single seq file and marks its PDE permanent.

State and persistence behavior: no local state is stored. All reported values come from VM, swap, memcg-independent global page state, atomic counters, and architecture hooks. Some fields intentionally report zero for compatibility (`NFS_Unstable`, `Bounce`, `WritebackTmp`, `VmallocChunk`).

Dependencies and integration points: integrates with the VM page allocator, swap, slab, hugetlb, transparent hugepages, zswap, CMA, memory failure, unaccepted memory, percpu allocator, GPU reclaim counters, and procfs/seq_file. Userspace treats field names as ABI.

Risks: the file is a non-atomic multi-counter snapshot, so values may not add up exactly under memory pressure. Field removal or reordering can break userspace parsers. New counters must use correct units and config guards. Cached memory calculation must avoid underflow.

Test signals: parse field presence across configs; compare totals under memory allocation, swap, zswap, THP, hugetlb, CMA, memory hotplug, and NUMA workloads; ABI tests for field names and kB formatting.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/proc/meminfo.c -->
