<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/proc/page.c -->
## sources/distributed-fs/ceph-client/fs/proc/page.c

Purpose: implements global page-monitor files `/proc/kpagecount`, `/proc/kpageflags`, and optionally `/proc/kpagecgroup`, exposing physical page mapcounts, stable page flags, and owning memory-cgroup inode IDs as arrays of 64-bit records indexed by PFN.

Important APIs and functions: `kpage_read` is the common aligned array reader. `get_max_dump_pfn`, `get_kpage_count`, `stable_page_flags`, `kpagecount_read`, `kpageflags_read`, `kpagecgroup_read`, and `proc_page_init` implement each file. `stable_page_flags` is exported GPL for other kernel users.

Control flow: reads require offset and size alignment to `sizeof(u64)`, clamp to the maximum dumpable PFN, loop PFN-by-PFN through `pfn_to_online_page`, compute the requested value or zero for holes, copy it to userspace, and periodically reschedule. `stable_page_flags` snapshots page/folio state and maps internal flags into documented `KPF_*` bits including pseudo flags for NOPAGE, THP, huge, zero page, mmap, anon, KSM, buddy, offline, pgtable, slab, idle, swapcache, hwpoison, and architecture/private bits.

State and persistence behavior: no file-local state persists. Values are live snapshots of struct page, folio, memcg, and mapcount state. Sparsemem extends readable PFNs to populated early sections even beyond `max_pfn` alignment.

Dependencies and integration points: depends on memory hotplug/online pages, page snapshots, folio flags, mapcount helpers from `internal.h`, KSM, THP, hugetlb, memcg, page idle, memory failure, and procfs permanent file registration.

Risks: these interfaces expose low-level memory layout signals; permissions are root-read-only but still security-sensitive. Page state can change while reading, so output is not atomic. Mapcount precision depends on config. Device-zone TODO notes that not all memmap initialization can be identified.

Test signals: aligned and misaligned reads; reads across holes and sparsemem section edges; THP/hugetlb/KSM/zero/offline/hwpoison page flag bits; memcg enabled/disabled builds; compare kpagecount with mapped pages under `CONFIG_PAGE_MAPCOUNT` and fallback configs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/proc/page.c -->
