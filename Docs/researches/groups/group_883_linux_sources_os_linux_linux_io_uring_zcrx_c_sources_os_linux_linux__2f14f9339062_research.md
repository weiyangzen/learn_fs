# Group Research: Linux io_uring zero-copy RX and memory-management support files

This group covers io_uring zero-copy receive registration and TCP receive plumbing, memory-management Kconfig/build wiring, backing-device writeback lifecycle, balloon pages, bootmem metadata, BPF memcg kfuncs, and CMA allocation/debug/sysfs support.

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/io_uring/zcrx.c -->
# File Research: sources/os/linux/linux/io_uring/zcrx.c

## Purpose
Implements io_uring zero-copy receive support for network RX buffers. It registers user memory or dma-buf backed receive areas, exposes a userspace return-buffer ring, plugs the area into netdev page-pool memory-provider hooks, and emits 32-byte CQEs describing received zero-copy buffers.

## Main Interfaces
- Registration/lifecycle: `io_register_zcrx()`, `io_terminate_zcrx()`, `io_unregister_zcrx()`, `io_zcrx_get_region()`.
- Control operations: `io_zcrx_ctrl()`, `zcrx_flush_rq()`, `zcrx_export()`, `import_zcrx()`.
- Receive path: `io_zcrx_recv()`, `io_zcrx_tcp_recvmsg()`, `io_zcrx_recv_skb()`, `io_zcrx_recv_frag()`.
- Page-pool provider hooks: `io_pp_zc_alloc_netmems()`, `io_pp_zc_release_netmem()`, `io_pp_zc_init()`, `io_pp_zc_destroy()`, `io_pp_uninstall()`.

## Control Flow
Registration validates privileged `CAP_NET_ADMIN`, io_uring setup flags, reserved fields, queue size, region descriptors, and area descriptors. It then allocates an `io_zcrx_ifq`, creates an mmap-able return queue region, imports memory from pinned user pages or dma-buf, optionally opens the selected netdev RX queue as a page-pool memory provider, publishes the context in `ctx->zcrx_ctxs`, and copies updated IDs/tokens back to userspace.

The page-pool allocation path first consumes userspace-returned RQEs, validates area/index encoding, drops user references, tests page-pool references, and returns eligible netmems to the driver. If the ring has no usable entries, it falls back to the area freelist. TCP receive walks SKB head data, frags, and nested frags; net_iov-backed frags are passed by CQE offset, while linear/head or nonmatching frags are copied into kernel-readable fallback niovs.

## State And Synchronization
The file uses `ctx->mmap_lock` for xarray/region publication, `ctx->uring_lock` for termination/unregister paths, `ifq->pp_lock` for netdev/page-pool state, `rq.lock` for return-ring parsing, and `area->freelist_lock` for free niov management. Buffer ownership is tracked with per-niov user atomic counters plus page-pool netmem references.

## Integration Points
Integrates io_uring memory-region mapping, `io_account_mem()` accounting, netdev queue memory-provider APIs, page-pool netmem/net_iov APIs, TCP `tcp_read_sock()`, RPS flow recording, dma-buf attachment/mapping, DMA sync/unmap helpers, and io_uring CQE allocation.

## Notable Behaviors
- Supports one area per interface queue and area ID `0` for now.
- Requires `IORING_SETUP_DEFER_TASKRUN` and either `IORING_SETUP_CQE32` or `IORING_SETUP_CQE_MIXED`.
- Can export a registered ZCRX queue through an anonymous fd and import it into another ring.
- `ZCRX_REG_NODEV` permits area creation without binding a netdev, but non-page-sized buffers require a DMA device.
- Flush/control paths let userspace return outstanding RQEs without receiving more packets.

## Risks And Review Focus
- Refcount ordering between user refs, page-pool refs, anon-fd refs, and io_uring xarray lifetime is correctness-critical.
- DMA-buf and pinned-user-page paths have different readability, accounting, and unmap rules.
- RQE offset parsing must stay aligned with UAPI area-token encoding and buffer-size shifts.
- Copy fallback must not expose dma-buf-only memory to kernel copy paths.
<!-- END FILE RESEARCH: sources/os/linux/linux/io_uring/zcrx.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/io_uring/zcrx.h -->
# File Research: sources/os/linux/linux/io_uring/zcrx.h

## Purpose
Defines the internal io_uring zero-copy receive data structures, feature/flag masks, and public internal entry points used by io_uring receive and registration code.

## Main Contents
- `io_zcrx_mem` stores imported memory state: size, pinned pages, sg table, memory-accounting pages, dma-buf attachment, and dma-buf handle.
- `io_zcrx_area` groups a `net_iov_area`, per-niov user references, freelist state, mapping state, area ID, and backing memory.
- `zcrx_rq` describes the userspace return queue ring and cached head.
- `io_zcrx_ifq` ties one io_uring ZCRX context to an area, return queue, user/mm accounting, optional netdev/RX queue/DMA device, refcounts, page-pool lock, and mmap region.
- Compile-time stubs return `-EOPNOTSUPP` when `CONFIG_IO_URING_ZCRX` is disabled.

## Integration Points
Included by io_uring receive and registration implementation. Depends on io_uring types, dma-buf declarations, socket declarations, page-pool types, and netdev tracker state.

## Notable Behaviors
- `ZCRX_SUPPORTED_REG_FLAGS` admits import and no-device registration modes.
- `ZCRX_FEATURES` currently advertises receive page-size support.
- `user_refs` counts userspace-facing references separately from the internal object lifetime refcount.

## Risks And Review Focus
- Layout changes must remain consistent with `zcrx.c` lifetime rules and UAPI registration behavior.
- Stub behavior must match callers that expect unsupported ZCRX to fail cleanly.
<!-- END FILE RESEARCH: sources/os/linux/linux/io_uring/zcrx.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/mm/Kconfig -->
# File Research: sources/os/linux/linux/mm/Kconfig

## Purpose
Defines the kernel memory-management configuration menu and feature dependencies for swap, allocators, memory models, migration, compaction, huge pages, CMA, memory hotplug, device memory, userfaultfd, MGLRU, and architecture MM feature hooks.

## Main Contents
- Swap and compression: `SWAP`, `ZSWAP`, default zswap compressor choices, zswap shrinker defaults, and `ZSMALLOC` options.
- Slab/page hardening and observability: SLUB, freelist randomization/hardening, kmalloc bucket separation, SLUB stats, random kmalloc caches, page allocator shuffle, and heap-randomization compatibility.
- Memory model/hotplug: FLATMEM/SPARSEMEM/VMEMMAP selection, memory-hotplug online defaults, hot-remove, memmap-on-memory, and bootmem info hooks.
- Reclaim/migration/compaction: balloon migration, compaction, page reporting, NUMA migration, generic migration, contig allocation, and PCP batch scaling.
- User-visible MM features: KSM, memory failure recovery, THP policy defaults, read-only file THP, soft-dirty tracking, secretmem, anonymous VMA names, GUP tests, userfaultfd, MGLRU, per-VMA locks, NUMA emulation, and lazy MMU mode tests.
- CMA and device memory: CMA core/debugfs/sysfs, maximum CMA areas, pageblock order bounds, ZONE_DMA/DMA32/DEVICE, HMM mirror, DEVICE_PRIVATE, and PFNMAP support.

## Integration Points
Feeds conditional compilation across `mm/Makefile`, architecture Kconfig selections, documentation-described sysfs/proc/kernel-command-line controls, and dependent subsystems such as zram/zswap, hugetlb, DAX/HMM, memcg, DAMON, and userfaultfd.

## Notable Behaviors
- Many symbols are architecture-selected capability hooks rather than direct user choices.
- Several defaults are intentionally conservative, especially for debug/statistics, THP submodes, hotplug online policy, and experimental mapcount/THP options.
- CMA depends on MMU and selects migration plus memory isolation.
- The file sources `mm/damon/Kconfig` before ending the Memory Management menu.

## Risks And Review Focus
- Dependency changes can silently alter build coverage across architectures.
- Defaults affect boot-time policy and runtime ABI expectations under `/sys`, `/proc`, and command-line parameters.
- Experimental options such as read-only THP for filesystems and no per-page mapcount need careful compatibility review.
<!-- END FILE RESEARCH: sources/os/linux/linux/mm/Kconfig -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/mm/Makefile -->
# File Research: sources/os/linux/linux/mm/Makefile

## Purpose
Defines object composition, instrumentation exclusions, and configuration-gated build rules for the Linux memory-management subsystem.

## Main Contents
- Disables KASAN/KCSAN/KCOV instrumentation for selected allocator, page allocator, kmemleak, memcg, vmstat, and related objects where instrumentation is noisy or unsafe.
- Builds the core MM object set: filemap, writeback, reclaim, swap core, shmem, slab, page allocation, memblock, backing-dev, percpu, compaction, GUP, VMAs, and MMU/NOMMU-specific files.
- Selects optional objects for swap/zswap, DMA pools, hugetlb, NUMA, sparsemem, MMU notifier, KSM, sanitizers, migration, memcg, CMA, ballooning, page extension, secretmem, userfaultfd, DAMON, hardened usercopy, zone device, HMM, page reporting, bootmem info, and tests.

## Integration Points
Directly consumes symbols from `mm/Kconfig` and architecture Kconfig. It also assigns module-parameter namespaces through aggregate targets such as `page-alloc-y` and `memory-hotplug-y`.

## Notable Behaviors
- `mmu-y` is `nommu.o` by default and replaced with the normal MMU object list when `CONFIG_MMU=y`.
- `bpf_memcontrol.o` is only built when both memcg and BPF syscall support are enabled.
- CMA support is split into core, debugfs, and sysfs objects by config.
- KCSAN barrier instrumentation is explicitly enabled while KCSAN is disabled for noisy allocator files.

## Risks And Review Focus
- Build-rule ordering and config guards determine which subsystem code is linked into every kernel.
- Instrumentation exclusions should be reviewed before adding sanitizer-sensitive MM code.
- Optional object additions must match Kconfig dependencies to avoid unresolved symbols.
<!-- END FILE RESEARCH: sources/os/linux/linux/mm/Makefile -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/mm/backing-dev.c -->
# File Research: sources/os/linux/linux/mm/backing-dev.c

## Purpose
Implements backing-device information lifecycle, sysfs/debugfs exposure, writeback object initialization/shutdown, global BDI registration/lookup, and cgroup writeback object management.

## Main Interfaces
- BDI lifecycle: `bdi_init()`, `bdi_alloc()`, `bdi_register_va()`, `bdi_register()`, `bdi_unregister()`, `bdi_put()`.
- Lookup/metadata: `bdi_get_by_id()`, `inode_to_bdi()`, `bdi_dev_name()`, `bdi_set_owner()`.
- Writeback setup/teardown: `wb_init()`, `wb_shutdown()`, `wb_exit()`.
- Cgroup writeback: `wb_get_lookup()`, `wb_get_create()`, `wb_memcg_offline()`, `wb_blkcg_offline()`.

## Control Flow
Initialization registers the `bdi` class, debugfs root, and global writeback workqueue. BDI registration creates a sysfs device, registers the root writeback, installs debugfs files, marks the writeback registered, assigns a monotonically increasing ID, inserts the BDI into an RB tree and RCU list, and emits a tracepoint. Unregistration removes global visibility, shuts down writeback work, unregisters cgroup writebacks, resets min-ratio accounting, removes debugfs/sysfs objects, and drops owner references.

When cgroup writeback is enabled, per-memcg writeback objects are looked up by memcg CSS ID and validated against the current blkcg association. Missing or stale entries are created with their own refs, lists, work items, memcg/blkcg pins, and BDI references. Offline cleanup kills radix-tree entries, moves writebacks to an offline list, and later switches attached inodes to live ancestors once dirty IO drains.

## State And Synchronization
Uses `bdi_lock` for the global RB tree and BDI list, RCU for list readers, `wb->work_lock` for writeback work registration state, `wb->list_lock` for inode IO lists, and `cgwb_lock` for cgroup writeback trees/lists/offline state. Cgroup writeback release is serialized with `cgwb_release_mutex` and deferred through workqueues plus RCU freeing.

## Integration Points
Connects the writeback subsystem, sysfs class devices, debugfs stats, block cgroup and memory cgroup writeback, inode writeback switching, global dirty throttling, tracepoints, and block-device superblock BDI selection.

## Notable Behaviors
- Exposes BDI tunables for read-ahead, min/max dirty ratios and bytes, strict limit, and a compatibility `stable_pages_required` attribute.
- Debugfs reports per-BDI and per-cgroup writeback dirty/writeback counters and thresholds.
- Root writeback is embedded in each BDI; cgroup writebacks are dynamic and RCU-managed.
- `noop_backing_dev_info` is exported for inodes without a real backing device.

## Risks And Review Focus
- Cgroup writeback teardown is lock/refcount/order sensitive, especially around offline dirty IO.
- Global BDI visibility must be removed before writeback shutdown to avoid new users.
- Sysfs setters must preserve dirty-limit invariants maintained outside this file.
<!-- END FILE RESEARCH: sources/os/linux/linux/mm/backing-dev.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/mm/balloon.c -->
# File Research: sources/os/linux/linux/mm/balloon.c

## Purpose
Provides common helper code for memory balloon drivers, including balloon page allocation, enqueue/dequeue accounting, and optional migration support for inflated balloon pages.

## Main Interfaces
- Allocation and list operations: `balloon_page_alloc()`, `balloon_page_enqueue()`, `balloon_page_dequeue()`.
- Batched operations: `balloon_page_list_enqueue()`, `balloon_page_list_dequeue()`.
- Migration hooks under `CONFIG_BALLOON_MIGRATION`: isolate, putback, and migrate operations registered for offline movable pages.

## Control Flow
Drivers allocate pages with balloon-appropriate GFP flags, enqueue them into the balloon device list, and later dequeue them before returning pages to the guest allocator. Enqueue marks pages offline, optionally installs movable ops and `page_private` backpointer, adjusts managed page counts, and updates balloon VM/node counters. Dequeue reverses accounting and finalizes pages for release.

With migration enabled, compaction can isolate balloon pages, call the driver-specific `migratepage()` callback, insert the replacement page into the balloon list on success, or account deflation when migration reports `-ENOENT`.

## State And Synchronization
A global `balloon_pages_lock` protects balloon page lists, `page_private` balloon ownership, and isolated-page counters. Page offline state remains sticky until returned to the buddy allocator.

## Integration Points
Used by virtualization balloon drivers through `struct balloon_dev_info`. Hooks into MM migration through `movable_operations`, VM event counters, node page state, and optional managed page count adjustment.

## Risks And Review Focus
- Drivers must not use `page->lru` while a page is enqueued.
- Dequeue can return `NULL` while pages are temporarily isolated by compaction.
- Migration callback results affect whether old and new pages are counted as inflated or deflated.
<!-- END FILE RESEARCH: sources/os/linux/linux/mm/balloon.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/mm/bootmem_info.c -->
# File Research: sources/os/linux/linux/mm/bootmem_info.c

## Purpose
Tracks boot-time memory-management metadata pages so memory hotplug can later identify and release reserved metadata such as node info and sparsemem section usage.

## Main Interfaces
- `get_page_bootmem()` tags a metadata page with bootmem type and info encoded in `page_private`, marks it private, and increments its reference count.
- `put_page_bootmem()` drops a tagged bootmem page reference and frees the reserved page when the last metadata reference is gone.
- `register_page_bootmem_info_node()` registers pgdat pages and sparsemem section metadata pages for a node.

## Control Flow
Node registration tags the physical pages backing `struct pglist_data`, then walks section-sized PFN ranges for the node. Valid PFNs owned by the node are aligned to section boundaries and registered through `register_page_bootmem_info_section()`, which also registers vmemmap memmap pages unless preinitialized and tags `mem_section_usage` pages.

## State And Synchronization
The file relies on early boot/hotplug context rather than local locking. Encoded `page_private` stores the bootmem type in low bits and node/section info above it.

## Integration Points
Uses memblock/sparsemem section metadata, memory hotplug bootmem type definitions, kmemleak physical-part freeing, reserved-page freeing, and node PFN ownership helpers.

## Risks And Review Focus
- Type/info encoding must stay within the low-nibble layout expected by bootmem helpers.
- Duplicate registration across nodes is avoided with `early_pfn_to_nid()` and is important on platforms with overlapping node PFN assignments.
<!-- END FILE RESEARCH: sources/os/linux/linux/mm/bootmem_info.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/mm/bpf_memcontrol.c -->
# File Research: sources/os/linux/linux/mm/bpf_memcontrol.c

## Purpose
Registers BPF kfuncs that let BPF programs acquire memory cgroup references and read memory-controller statistics, events, usage, and page-state counters.

## Main Interfaces
- Reference helpers: `bpf_get_root_mem_cgroup()`, `bpf_get_mem_cgroup()`, `bpf_put_mem_cgroup()`.
- Read helpers: `bpf_mem_cgroup_vm_events()`, `bpf_mem_cgroup_usage()`, `bpf_mem_cgroup_memory_events()`, `bpf_mem_cgroup_page_state()`.
- Maintenance helper: `bpf_mem_cgroup_flush_stats()`.
- Registration: `bpf_memcontrol_init()` registers the BTF kfunc ID set for `BPF_PROG_TYPE_UNSPEC`.

## Control Flow
The getter for arbitrary CSS accepts a CSS from any controller, resolves the corresponding memcg CSS through the cgroup’s subsystem array when necessary, and uses `css_tryget()` to provide acquire semantics. Counter helpers validate event/stat indexes before reading memcg counters. The kfunc set annotates acquire, release, nullable return, RCU, and sleepable semantics for verifier use.

## State And Synchronization
Uses CSS reference counting for acquired memcgs and RCU while translating non-memcg CSS values to the memcg subsystem CSS. Stats flushing may sleep and is marked `KF_SLEEPABLE`.

## Integration Points
Connects memcg internals, BPF kfunc registration, BTF ID metadata, VM event/stat validation helpers, page counters, and memcg rstat flushing.

## Risks And Review Focus
- Verifier annotations must match actual lifetime and sleepability behavior.
- Root memcg is returned with acquire semantics despite not needing a ref, so `bpf_put_mem_cgroup()` remains valid.
- Invalid event/stat indexes intentionally return `(unsigned long)-1`.
<!-- END FILE RESEARCH: sources/os/linux/linux/mm/bpf_memcontrol.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/mm/cma.c -->
# File Research: sources/os/linux/linux/mm/cma.c

## Purpose
Implements the Contiguous Memory Allocator core: early reservation of CMA regions, activation into pageblock-managed areas, bitmap-based allocation, contiguous-page migration/freezing, release, multi-range CMA support, and early sub-reservation.

## Main Interfaces
- Metadata access: `cma_get_base()`, `cma_get_size()`, `cma_get_name()`, `cma_for_each_area()`, `cma_intersects()`.
- Reservation/setup: `cma_init_reserved_mem()`, `cma_declare_contiguous_nid()`, `cma_declare_contiguous_multi()`, `cma_reserve_pages_on_error()`.
- Allocation/release: `cma_alloc()`, `cma_alloc_frozen()`, `cma_alloc_frozen_compound()`, `cma_release()`, `cma_release_frozen()`.
- Early reservation: `cma_reserve_early()`.

## Control Flow
Early declaration reserves fixed or dynamically chosen memblock ranges, validates alignment and size against pageblock and `order_per_bit`, creates a CMA descriptor, and records one or more ranges. Activation later allocates per-range bitmaps, validates that each range stays within a single zone, marks already early-reserved portions as used, initializes reserved pageblocks as CMA, initializes locks/debug lists, and marks the area activated.

Allocation searches each range bitmap for an aligned free span, marks it allocated under `cma->lock`, then calls `alloc_contig_frozen_range()` under `alloc_mutex` to isolate/migrate pages. On busy failure it clears the bitmap and retries; on success it resets KASAN tags and updates VM events/sysfs counters. Normal `cma_alloc()` also makes pages refcounted. Release validates the page range belongs to a CMA range, drops page refs for normal release, frees the frozen contiguous range, clears bitmap bits, and updates counters/tracepoints.

## State And Synchronization
Global state is `cma_areas[]` plus `cma_area_count`. Each CMA area has a spinlock for bitmap and `available_count`, a mutex serializing contiguous allocation, per-range bitmaps, flags recording activation/zone validation/error behavior, and optional debugfs/sysfs accounting state.

## Integration Points
Uses memblock for boot reservations, pageblock migration-type initialization, contiguous allocation/freeing, memory isolation/migration, KASAN tag reset, kmemleak physical ignores, VM event counters, tracepoints, and optional CMA debugfs/sysfs accounting.

## Notable Behaviors
- Multi-range declaration first tries a single region, then selects the largest suitable above-4G free ranges and reserves them bottom-up.
- Dynamic allocation avoids the first 4GB when possible on 64-bit systems to preserve constrained DMA/DMA32 zones.
- CMA ranges crossing zones are rejected because `alloc_contig_range()` requires a single-zone PFN range.
- `cma_reserve_early()` can reserve aligned chunks before activation without locking or later unreserve support.

## Risks And Review Focus
- Bitmap accounting and contiguous allocation rollback must remain paired on every failure path.
- Zone validation and highmem/lowmem boundary checks protect allocator assumptions.
- Multi-range failure cleanup must free only successfully reserved memblock ranges.
- Early reservations are caller-managed if CMA activation later fails.
<!-- END FILE RESEARCH: sources/os/linux/linux/mm/cma.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/mm/cma.h -->
# File Research: sources/os/linux/linux/mm/cma.h

## Purpose
Defines internal CMA data structures, flags, global declarations, bitmap helpers, and sysfs accounting hooks shared by CMA core, debugfs, and sysfs files.

## Main Contents
- `cma_memrange` describes each CMA physical range with base PFN, page count, early-reservation PFN before activation or bitmap after activation, and optional debugfs bitmap wrapper.
- `cma` describes an allocator area: total/available pages, bitmap granularity, locks, optional debugfs allocation tracking, name, range array, optional sysfs counters/kobject, flags, and NUMA node.
- `cma_kobject` binds a sysfs kobject back to a `struct cma`.
- `CMA_MAX_RANGES` limits multi-range CMA to 8 ranges.
- `cma_bitmap_maxno()` computes the bitmap size in allocation units.

## Integration Points
Included by `cma.c`, `cma_debug.c`, and `cma_sysfs.c`. Exposes `cma_areas` and `cma_area_count` to debug/visibility code and hides sysfs counter calls behind config stubs.

## Risks And Review Focus
- The `early_pfn`/`bitmap` union changes meaning after activation.
- `available_count`, bitmap bits, and sysfs counters must remain consistent with allocation/release code.
- Flag additions must preserve the one-bit state checks used by activation and validation.
<!-- END FILE RESEARCH: sources/os/linux/linux/mm/cma.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/mm/cma_debug.c -->
# File Research: sources/os/linux/linux/mm/cma_debug.c

## Purpose
Provides a debugfs interface for inspecting and manually exercising CMA areas.

## Main Interfaces
- Debugfs read attributes: `count`, `order_per_bit`, `used`, `maxchunk`, per-range `base_pfn`, and per-range `bitmap`.
- Debugfs write attributes: `alloc` allocates pages from a CMA area; `free` releases pages previously allocated through this debug interface.
- Init: `cma_debugfs_init()` creates `/sys/kernel/debug/cma` entries for activated CMA areas.

## Control Flow
Manual allocation creates a `cma_mem` tracking entry, allocates pages with `cma_alloc()`, and stores the allocation on a per-CMA debug list. Manual free pops tracked entries and releases full allocations, or partial allocations only when `order_per_bit == 0`; otherwise it keeps the remainder tracked and logs that partial block release is unsupported.

## State And Synchronization
Uses `cma->lock` to read allocation bitmap-derived state and `cma->mem_head_lock` to protect the debug allocation tracking list.

## Integration Points
Calls CMA core allocation/release functions and exposes raw CMA bitmap data through debugfs. Creates backward-compatible `base_pfn` and `bitmap` symlinks to range `0`.

## Risks And Review Focus
- This is a privileged debug interface that can perturb allocator state.
- Partial free behavior differs when bitmap granularity represents more than one page.
- Debugfs bitmap exposure depends on `unsigned long` bitmap storage cast into a `u32` array view.
<!-- END FILE RESEARCH: sources/os/linux/linux/mm/cma_debug.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/mm/cma_sysfs.c -->
# File Research: sources/os/linux/linux/mm/cma_sysfs.c

## Purpose
Exposes per-CMA-area allocation/release counters and capacity information under the MM sysfs hierarchy.

## Main Interfaces
- Accounting hooks: `cma_sysfs_account_success_pages()`, `cma_sysfs_account_fail_pages()`, `cma_sysfs_account_release_pages()`.
- Read-only attributes: `alloc_pages_success`, `alloc_pages_fail`, `release_pages_success`, `total_pages`, `available_pages`.
- Init: `cma_sysfs_init()` creates the `cma` kobject under `mm_kobj` and one child kobject per activated CMA area.

## Control Flow
CMA core updates atomic64 counters on allocation success, allocation failure, and release. Sysfs show methods retrieve the owning `struct cma` from the enclosing `cma_kobject` and emit counter or capacity values. Initialization skips inactive CMA areas and unwinds already-created kobjects on failure.

## State And Synchronization
Counters are atomic64 values in `struct cma`. The kobject release method frees the dynamic `cma_kobject` and clears `cma->cma_kobj`.

## Integration Points
Hooks into CMA core accounting, `mm_kobj`, kobject sysfs operations, and activated CMA area enumeration.

## Risks And Review Focus
- `available_pages` reads `cma->available_count` without taking `cma->lock`, so it is informational rather than a synchronized allocation guarantee.
- Init failure unwinding must match kobject ownership and release semantics.
<!-- END FILE RESEARCH: sources/os/linux/linux/mm/cma_sysfs.c -->