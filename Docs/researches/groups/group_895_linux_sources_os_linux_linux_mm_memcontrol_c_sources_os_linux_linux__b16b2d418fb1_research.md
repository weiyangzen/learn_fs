# Group Research: group_895_linux_sources_os_linux_linux_mm_memcontrol_c_sources_os_linux_linux__b16b2d418fb1

Scope: `Docs/research_subset_a.md` / Linux `mm` memory cgroup, memfd, and memfd LUO preservation files. All listed source files were read completely.

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/mm/memcontrol.c -->
# File Research: sources/os/linux/linux/mm/memcontrol.c

## Role

Main Linux memory controller implementation for the cgroup memory subsystem. It defines the `memory_cgrp_subsys`, root memory cgroup, per-memcg/per-node accounting, folio and kernel-object charging, memory/swap/zswap limits, reclaim throttling, memcg OOM handling, lifecycle hooks, rstat flushing, cgroupfs files, socket memory accounting, and integration with writeback, LRU generations, shrinkers, hugetlb, swap, and cgroup v1 compatibility.

## Key Behavior

- Initializes global memcg state, per-CPU charge stocks, object charge stocks, workqueues, slab caches, stats indexes, VM event indexes, CPU hotplug drain handling, and boot options from `cgroup.memory=` and `swapaccount=`.
- Allocates and onlines memcgs through cgroup CSS hooks, including page counters, per-node `lruvec` state, vmstats, private 16-bit memcg IDs, vmpressure, memory peaks, writeback domains, shrinker state, objcg roots, and LRU generation state.
- Offlines and frees memcgs by clearing protection limits, cleaning zswap state, reparenting list_lru/deferred split/object cgroups, invalidating reclaim iterators, waiting for foreign writeback completions, draining per-CPU stocks, releasing private IDs, and freeing per-node/per-CPU storage.
- Maintains per-memcg and per-lruvec statistics through per-CPU deltas, cgroup rstat propagation, periodic flush work, synchronous flush-on-read thresholds, NMI-safe atomic fallbacks, and v1 local-stat reparenting.
- Implements page/folio charging through `try_charge_memcg()`: consumes per-CPU stock, attempts memory and memsw page-counter charges, handles `memory.max` events, reclaim, stock draining, retry policy, memcg OOM, forced charges for nofail/high-priority allocations, and `memory.high`/`swap.high` overage notification.
- Enforces `memory.high` with reclaim and exponential task throttling on user-return paths via `__mem_cgroup_handle_over_high()`, plus async high-limit work for interrupt-context charges.
- Tracks folio ownership through `folio->memcg_data` carrying an objcg, with helpers for normal charge, hugetlb charge, swapin charge, batched uncharge, replacement, migration, folio split reference propagation, and procfs inode lookup.
- Accounts kernel memory and slab objects with `obj_cgroup` references, per-task lazy objcg caching, per-CPU byte stock, slab object extension storage, list_lru preallocation, per-node slab vmstat batching, NMI-safe accounting paths, and object-cgroup reparenting on memcg removal.
- Provides socket memory accounting on cgroup v2 and v1, including socket memcg association, inheritance, charge/uncharge, and static-key enablement.
- Supports cgroup writeback by exposing memcg writeback domains, per-writeback dirty/writeback/headroom stats, foreign dirty tracking, and remote foreign writeback flushing for inode/page ownership mismatches.
- Maintains private memcg IDs for swap and shadow entries so IDs can be recycled after cgroup offlining while referenced pages can still resolve to live ancestors.
- Exposes cgroup v2 memory files: `memory.current`, `memory.peak`, `memory.min`, `memory.low`, `memory.high`, `memory.max`, `memory.events`, `memory.events.local`, `memory.stat`, optional `memory.numa_stat`, `memory.oom.group`, and `memory.reclaim`.
- Under `CONFIG_SWAP`, exposes `memory.swap.current`, `memory.swap.high`, `memory.swap.max`, `memory.swap.peak`, and `memory.swap.events`; records swap cgroup IDs, charges/un-charges swap, computes per-memcg swap availability, and detects swap-full conditions.
- Under `CONFIG_ZSWAP`, enforces hierarchical zswap limits, charges/un-charges compressed backend memory, tracks zswap stats, controls zswap writeback, and exposes `memory.zswap.current`, `memory.zswap.max`, and `memory.zswap.writeback`.
- Preserves cgroup v1 behavior through `memcontrol-v1.h` helpers for legacy files, soft limits, kmem/tcp accounting, non-hierarchical local stats, OOM preparation/finish, and legacy stat formatting.

## Dependencies

Uses cgroup core, `page_counter`, folio/page cache helpers, reclaim/vmscan, swap cgroup, shmem/hugetlb, slab object extensions, list_lru, shrinkers, LRU generations, rstat, vmpressure, PSI, OOM, cpuset, socket memory hooks, writeback domains, zswap, tracepoints from `trace/events/memcg.h` and `trace/events/vmscan.h`, and legacy memcg-v1 support.

## Research Notes

This file is the central policy and accounting layer for memory isolation. The implementation is intentionally split between fast-path approximate per-CPU accounting and slower synchronized reconciliation: charges use stocks and deferred rstat propagation for performance, while limit changes, OOM paths, swap/zswap decisions, and user-visible stats force draining or flushing when accuracy is required. The highest-risk invariants are ownership lifetime (`obj_cgroup` and private memcg IDs), charge/uncharge pairing across folio migration/replacement/swap, lock ordering during objcg reparenting, and limit enforcement behavior under reclaim, OOM, and dying-task conditions.
<!-- END FILE RESEARCH: sources/os/linux/linux/mm/memcontrol.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/mm/memfd.c -->
# File Research: sources/os/linux/linux/mm/memfd.c

## Role

Implementation of the `memfd_create()` syscall and shared memfd sealing support for tmpfs/shmem and hugetlbfs-backed anonymous files. It creates anonymous in-memory files, validates memfd flags and noexec policy, manages seal addition/querying through `fcntl()`, checks mmap writability against write seals, and provides a folio allocation helper for GUP-based memfd pinning.

## Key Behavior

- Reuses `PAGECACHE_TAG_TOWRITE` as `MEMFD_TAG_PINNED` for tmpfs/hugetlbfs pin scanning because these memory-only filesystems do not use that tag for writeback.
- Detects potentially pinned folios by comparing actual folio references with the expected page-cache reference count after draining local LRU additions.
- `memfd_wait_for_pins()` tags folios with extra refs, drains all LRU additions once, then performs bounded retry scans with killable sleeps; it clears tags as pins disappear and returns `-EBUSY` if folios remain pinned on the final scan.
- `memfd_alloc_folio()` allocates missing folios for memfd pinning: shmem uses `shmem_read_folio()`, while hugetlbfs reserves one hugepage, allocates from non-highmem/non-movable zones, zeroes it, marks it uptodate, serializes insertion with the hugetlb fault mutex, adds it to the page cache, sets subpool metadata, and unwinds reservations on failure.
- `memfd_add_seals()` validates write mode and seal bits, rejects additions after `F_SEAL_SEAL`, expands `F_SEAL_EXEC` on executable files into shrink/grow/write/future-write seals, denies writable mappings before adding `F_SEAL_WRITE`, waits for outstanding pins, and then ORs new seals into the inode seal word.
- `memfd_get_seals()` and `memfd_fcntl()` implement `F_GET_SEALS` and `F_ADD_SEALS` for supported shmem or hugetlbfs files.
- `check_sysctl_memfd_noexec()` applies per-pid-namespace `vm.memfd_noexec` policy by defaulting unspecified exec flags to `MFD_NOEXEC_SEAL` or `MFD_EXEC`, and can reject executable memfds when noexec is enforced.
- `memfd_check_seals_mmap()` blocks new writable shared mappings under write/future-write seals and strips `VM_MAYWRITE` from read-only shared mappings so later `mprotect(PROT_WRITE)` cannot bypass sealing.
- `sanitize_flags()` validates memfd creation flags, permits hugepage size encodings only with `MFD_HUGETLB`, rejects simultaneous `MFD_EXEC` and `MFD_NOEXEC_SEAL`, then applies sysctl noexec policy.
- `alloc_name()` constructs the internal `memfd:<user-name>` name with `NAME_MAX` bounds and user-copy error handling.
- `memfd_alloc_file()` creates either a shmem or hugetlb anonymous file, initializes anonymous inode security, sets seek/read/write file modes and `O_LARGEFILE`, clears default `F_SEAL_SEAL` when sealing is allowed, and applies noexec mode plus `F_SEAL_EXEC` for `MFD_NOEXEC_SEAL`.
- `SYSCALL_DEFINE2(memfd_create)` validates flags, copies the name, maps `MFD_CLOEXEC` to `O_CLOEXEC`, and returns a new fd for the allocated file.

## Dependencies

Uses VFS/file allocation, shmem, hugetlbfs, page cache XArray scanning, folios, GUP pinning support, LRU drain helpers, `fcntl` seal constants, pid namespace sysctl policy, anonymous inode LSM initialization, syscall fd installation, and `uapi/linux/memfd.h`.

## Research Notes

The key safety path is adding `F_SEAL_WRITE`: the caller must prevent new writable references, then this file denies writable mappings and waits for elevated folio refs that may represent DMA or GUP pins. The noexec policy is enforced at creation time, while mmap checks enforce write seals after creation. Hugetlb folio allocation is careful about reservations, zeroing, uptodate state, and page-cache serialization because it supports long-term pinned use cases outside the usual fault path.
<!-- END FILE RESEARCH: sources/os/linux/linux/mm/memfd.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/mm/memfd_luo.c -->
# File Research: sources/os/linux/linux/mm/memfd_luo.c

## Role

Live Update Orchestrator file-preservation handler for memfd files across kexec. It serializes selected memfd state into KHO-preserved memory, preserves the backing folios, freezes mutable shmem state during preparation, restores a new memfd in the next kernel, and cleans up preserved or restored resources depending on the live-update outcome.

## Key Behavior

- Documents the unstable LUO memfd preservation contract: file contents, size, file position, status flags, and known seals are preserved; properties such as `FD_CLOEXEC` are reset; hugetlb-backed memfds are rejected.
- `memfd_luo_preserve_folios()` handles empty files without folio metadata; otherwise it estimates a page-sized upper bound, allocates a folio pointer array, pins all file indices with `memfd_pin_folios()` so pages are resident and immovable, allocates serialized folio records, KHO-preserves each folio, forces every folio dirty, zeroes and marks non-uptodate folios, records PFN/index/flags, and preserves the serialized folio array via KHO vmalloc preservation.
- The preserve path intentionally fills sparse holes by pinning all file offsets; the comments call out possible future performance work to avoid allocating every missing page.
- `memfd_luo_unpreserve_folios()` reverses a prepared-but-not-committed preservation by unpreserving the vmalloc metadata, unpreserving each folio, unpinning it, and freeing the serialized array.
- `memfd_luo_preserve()` locks the inode, freezes shmem, allocates the main serialized structure in preserved memory, validates current seals against `MEMFD_LUO_ALL_SEALS`, records file position, size, and seals, rejects files whose page count exceeds `UINT_MAX`, preserves folios, stores the serialized physical address, and leaves shmem frozen until later unpreserve/finish handling.
- `memfd_luo_freeze()` updates only the saved file position at freeze time because file offset can change after prepare while size/folios/seals are frozen.
- `memfd_luo_unpreserve()` thaws shmem and frees all preserved state if the original-kernel preservation is cancelled.
- `memfd_luo_finish()` runs in the source/old context when retrieval did not happen; it restores preserved metadata enough to drop folio references, discards preserved folios, frees vmalloc metadata, and frees the serialized structure.
- `memfd_luo_retrieve_folios()` restores preserved folios by physical address, locks and marks them swap-backed, charges them to memcg, inserts them into the new shmem page cache, restores uptodate/dirty flags, accounts shmem inode blocks, adds them to LRU, recalculates inode state, and unwinds uninserted folios on error.
- `memfd_luo_retrieve()` validates serialized data and seals, creates a new seal-capable memfd, reapplies seals, restores file position and size, restores folio metadata from KHO vmalloc memory, inserts all folios, returns the new file through `args->file`, and frees the serialized KHO state.
- `memfd_luo_can_preserve()` accepts only anonymous shmem memfds (`shmem_file(file)` with no inode links), which excludes hugetlbfs and linked shmem files.
- Registers a `liveupdate_file_handler` at `late_initcall()` with preserve, freeze, unpreserve, finish, retrieve, can-preserve, and ID callbacks; registration errors other than `-EOPNOTSUPP` are logged and returned.

## Dependencies

Uses the liveupdate file-handler API, KHO preserved allocation/vmalloc/folio helpers, shmem freeze and page-cache insertion helpers, memfd allocation and sealing helpers from `memfd.c`, folio pinning/unpinning, memcg charging, file position helpers, vmalloc, PFN/physical address conversion, and serialized ABI definitions from `linux/kho/abi/memfd.h`.

## Research Notes

The preservation model favors correctness over sparseness and reclaimability: all holes are materialized, all folios are marked dirty, and non-uptodate folios are zeroed before preservation so restored user data cannot be lost under reclaim. The restore path depends on careful resource ownership transfer from KHO-preserved physical folios into a new shmem mapping; failures deliberately leave already inserted folios owned by the new file while dropping only not-yet-inserted restored folios. The handler is intentionally narrow because only anonymous shmem memfds have the expected sealing and page-cache semantics.
<!-- END FILE RESEARCH: sources/os/linux/linux/mm/memfd_luo.c -->