# Group Research: group_905_linux_sources_os_linux_linux_mm_shmem_c_sources_os_linux_linux_mm_sh_def4e9ea9dab

Scope checked against `Docs/research_subset_a.md`: all files are under `sources/os/linux/linux`, which is included in subset A. Every listed source file was read completely.

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/mm/shmem.c -->
# File Research: sources/os/linux/linux/mm/shmem.c

Implements Linux shmem/tmpfs, the swap-backed in-memory filesystem used for tmpfs mounts, SysV/shared anonymous memory, `/dev/zero` shared mappings, memfd-style internal files, and many kernel users that need page-cache-backed volatile storage. The full implementation is enabled under `CONFIG_SHMEM`; without it, this file supplies a tiny ramfs-based tmpfs fallback plus the common shmem file setup helpers.

Key responsibilities:
- Maintains tmpfs superblock state, inode state, block/inode accounting, inode number allocation, quota integration, xattrs, ACLs, file attributes, casefolding, export handles, and mount/remount option parsing.
- Provides the core shmem page-cache API: `shmem_get_folio()`, `shmem_add_to_page_cache()`, swap entry replacement, swapin, swapout, truncate/hole-punch, fallocate, and read/write/splice paths.
- Implements tmpfs resource limits with per-superblock `used_blocks`, inode-space accounting, `SHMEM_F_NORESERVE` overcommit accounting, and optional in-memory dquot accounting.
- Supports tmpfs huge folios and transparent huge pages, including mount options, global/sysfs policy, mTHP order masks, huge-folio allocation fallback, end-of-file shrink handling, and a shrinker for unused large folio tails.
- Handles shmem swap lifecycle: page-cache entries can be real folios or encoded swap entries; `shmem_writeout()` replaces folios with swap entries, `shmem_swapin_folio()` moves data back, and `shmem_unuse()` scans all swapped shmem inodes during swapoff.
- Supplies VMA operations for ordinary tmpfs mappings and anonymous shmem mappings, including fault handling, NUMA shared mempolicy hooks, userfaultfd missing/minor support, and hugepage-friendly unmapped-area alignment.
- Implements tmpfs VFS operations: create, tmpfile, mkdir, link, unlink, rmdir, rename with whiteout/exchange support, symlink storage, statfs, getattr/setattr, fileattr get/set, xattr handlers, and export file handles.
- Registers and initializes the tmpfs filesystem, the internal kernel mount `shm_mnt`, tmpfs sysfs feature files, transparent hugepage sysfs controls, and boot parameters for shmem/tmpfs THP policy.
- Exports common helpers such as `shmem_file_setup()`, `shmem_kernel_file_setup()`, `shmem_file_setup_with_mnt()`, `shmem_zero_setup()`, `shmem_read_folio_gfp()`, and `shmem_read_mapping_page_gfp()`.

Important behavior:
- tmpfs file data is sparse and page-cache based. Holes read as zeroes, while allocated folios are charged incrementally unless the caller pre-accounted object size through shmem file setup.
- `info->alloced`, `info->swapped`, and `mapping->nrpages` are intentionally reconciled by `shmem_recalc_inode()` because the VM can drop clean hole pages or move folios between cache and swap behind VFS operations.
- Swap entries are stored in the mapping xarray as exceptional entries. Large folios and large swap entries require aligned index/order handling and can be split when swapin falls back to smaller folios.
- Swapoff uses a global `shmem_swaplist`; inode eviction coordinates with `stop_eviction` so the inode is not removed/freed while `shmem_unuse()` is scanning it.
- `shmem_writeout()` refuses swapout for locked shmem, noswap mounts, lack of swap, or fallocate races; otherwise it allocates swap, replaces the page-cache entry, submits swap I/O, and repairs state if writeout requests reactivation.
- `shmem_get_folio_gfp()` is the central lookup path. It handles cache hit, swapin, hole read, no-allocation lookup, userfaultfd interception, huge folio allocation, accounting failure cleanup, and truncate races.
- Hole punching uses `inode->i_private` as a temporary `struct shmem_falloc` rendezvous so page faults into the punched range wait instead of continuously refilling the hole.
- Fallocate can allocate not-yet-uptodate folios and roll them back if later allocation fails. `info->fallocend` protects fallocated large folio portions beyond `i_size` from being freed by truncation/splitting logic.
- Reads and splice reads treat absent folios as zeroes and fall back to base-page copying/splicing if a large folio has a hardware-poisoned subpage.
- `shmem_get_unmapped_area()` may inflate and adjust the chosen address so file offsets align with PMD-sized or mTHP-sized mappings when huge shmem is enabled.
- tmpfs remount can relax/tighten existing block and inode limits only if current usage fits; it cannot retroactively impose limits on unlimited mounts, cannot disable swap on remount, and cannot enable/change quotas after mount.
- Inode numbers can be 32-bit-compatible or full-width. Kernel-only mounts use per-CPU batched inode number allocation because those objects are created from contexts where the normal superblock stat lock is undesirable.
- Casefold support depends on Unicode support and only applies to directories; enabling/disabling it is rejected when the directory is non-empty.
- Security xattrs can be initialized during inode creation. tmpfs charges xattr storage against inode-space limits when inode limits are active.
- The tiny-shmem fallback registers tmpfs using ramfs operations and implements only no-op or ramfs-backed versions of the common shmem hooks.

Dependencies:
- Relies on the Linux VFS, page cache/xarray, swap subsystem, memcg charging, folios, LRU/writeback, rmap/MMU notifier side behavior through swap/page-cache helpers, inode/dentry helpers, quota core, xattr/simple_xattr, POSIX ACLs, fs_context parsing, mempolicy, userfaultfd, THP/mTHP helpers, sysfs/debug boot parameter infrastructure, security hooks, and ramfs fallback code.

Notable risks:
- The file has many cross-subsystem invariants: xarray entries, swapcache folios, `mapping->nrpages`, inode accounting, quota accounting, memcg charging, and folio lock state must be updated in the right order on every success and rollback path.
- Large folios increase boundary complexity: truncate, hole-punch, swapout, swapin, fallocate, EOF shrink, hardware poison, and hugepage policy all need consistent base-index/order calculations.
- Swapin/out races are expected. Correctness depends on repeated confirmation that the mapping still contains the expected swap entry and on converting `-EEXIST` races into retries.
- `inode->i_private` is reused for fallocate coordination rather than a permanent inode field; it is protected by inode locks/rwsem assumptions that must remain valid for all users.
- tmpfs quotas are volatile and in-memory; mount/remount restrictions protect against losing limits or enabling incomplete accounting after objects already exist.
<!-- END FILE RESEARCH: sources/os/linux/linux/mm/shmem.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/mm/shmem_quota.c -->
# File Research: sources/os/linux/linux/mm/shmem_quota.c

Implements the in-memory quota format used by tmpfs when `CONFIG_TMPFS_QUOTA` is enabled. Since tmpfs has no persistent quota file, this format stores quota limits and tracked ids in kernel memory while delegating active dquot accounting to the generic quota layer.

Key responsibilities:
- Defines quota grace periods and a per-id `struct quota_id` containing user/group id plus block and inode hard/soft limits.
- Provides `quota_format_ops` for the fake shmem quota format: quota-file checking, quota info setup, quota info write no-op, and full teardown.
- Allocates one red-black tree root per quota type in `mem_dqinfo->dqi_priv`.
- Implements `get_next_id` by walking the sorted id tree under the quota I/O semaphore.
- Implements dquot acquire by finding or creating a `quota_id` entry, applying tmpfs global default hard limits for new ids, loading limits into the dquot, and marking it active.
- Implements dquot release by either removing empty/fake ids from the tree or saving current dquot limits back into the tree.
- Exports `shmem_quota_format` and `shmem_quota_operations` for `shmem.c` to register and attach to tmpfs superblocks.

Important behavior:
- There is deliberately no on-disk quota file; check/write operations are successful no-ops.
- `dqi_max_spc_limit`, `dqi_max_ino_limit`, block grace, and inode grace are initialized when quota tracking is enabled.
- New user/group ids inherit default hard limits from `struct shmem_sb_info::qlimits`; soft limits default to zero until explicitly changed.
- Dquots with no useful state are marked fake and can be removed from the in-memory tree on release.
- The tree is protected by `dqio_sem`; individual dquot state is protected by `dq_lock` and `dq_dqb_lock`.

Dependencies:
- Uses generic Linux quota/dquot infrastructure, `mem_dqinfo`, rbtrees, tmpfs `struct shmem_sb_info`, and id conversion through `init_user_ns`.

Notable risks:
- All quota state is volatile. If a dquot were shrinkable like persistent quota formats, limits would be lost, so this code intentionally keeps state in the red-black tree until quota teardown or an empty release.
- `shmem_is_empty_dquot()` assumes only supported quota types reach it; additional quota types would need explicit handling.
- Correct limit persistence depends on release paths storing modified limits before clearing `DQ_ACTIVE_B`.
<!-- END FILE RESEARCH: sources/os/linux/linux/mm/shmem_quota.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/mm/show_mem.c -->
# File Research: sources/os/linux/linux/mm/show_mem.c

Provides generic Linux memory summary and diagnostic reporting. It backs sysinfo-style memory totals, estimates available memory, and prints detailed free-area state for OOM/debug paths.

Key responsibilities:
- Defines/export global RAM counters `_totalram_pages`, `totalreserve_pages`, and `totalcma_pages`.
- Implements `si_mem_available()` by estimating free pages plus reclaimable page cache and reclaimable kernel memory, while preserving low-watermark reserves.
- Fills global `sysinfo` memory fields through `si_meminfo()`.
- Fills per-NUMA-node `sysinfo` memory fields through `si_meminfo_node()` when NUMA is enabled.
- Implements node filtering for `show_free_areas()` based on cpuset/nodemask flags.
- Prints global VM counters, per-node counters, per-zone watermarks and state, buddy free lists by order and migratetype, hugetlb node info, pagecache totals, and swap cache info.
- Implements `__show_mem()` to print the standard `Mem-Info` dump plus total RAM, highmem/movable-only pages, reserved pages, CMA pages, hardware-poisoned pages, and optional allocation profiling top users.

Important behavior:
- Available memory is an estimate, not an exact reclaim promise. It subtracts total reserves and keeps at least half of page cache/reclaimable memory or the low watermark.
- `SHOW_MEM_FILTER_NODES` suppresses nodes outside an explicit nodemask or the current cpuset memory allowance.
- Buddy free-list reporting samples protected zone state under each zone lock, then prints counts outside the lock.
- Output includes many conditional counters only when corresponding kernel features are enabled, such as THP, shadow call stack, zsmalloc, CMA, memory failure, and allocation profiling.

Dependencies:
- Uses VM statistics, zones/nodes, cpusets, highmem, block-device page accounting, hugetlb, swap cache reporting, CMA, allocation profiling codetags, and page allocator watermarks/free lists.

Notable risks:
- This is diagnostic code and intentionally tolerates races in global/per-node counters; exact consistency is less important than avoiding heavy locking during failures.
- Output format is consumed by humans and tooling, so field changes have operational visibility even though this is not a strict stable ABI.
- Allocation profiling output is guarded by a trylock to avoid recursive or contended diagnostic paths.
<!-- END FILE RESEARCH: sources/os/linux/linux/mm/show_mem.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/mm/shrinker.c -->
# File Research: sources/os/linux/linux/mm/shrinker.c

Implements the core shrinker registry and execution engine used by reclaim to ask subsystem caches how many objects are reclaimable and to scan them. It supports global shrinkers, NUMA-aware shrinkers, memcg-aware shrinkers, deferred scan accounting, debugfs naming, and RCU-safe registration/removal.

Key responsibilities:
- Maintains the global `shrinker_list` protected by `shrinker_mutex` for mutation and RCU for reclaim-time iteration.
- Allocates/frees `struct shrinker` objects through `shrinker_alloc()` and `shrinker_free()`.
- Registers shrinkers with `shrinker_register()` and exposes names through shrinker debugfs support.
- Computes scan targets in `do_shrink_slab()` from freeable object counts, reclaim priority, previous deferred work, shrinker seek cost, and batch size.
- Tracks deferred scan counts per shrinker, per NUMA node, and when applicable per memcg shrinker id.
- Implements global slab shrinking via RCU list traversal and shrinker refcounts.
- Implements memcg slab shrinking by using per-memcg bitmaps to call only shrinkers that have objects charged in that memcg/node.
- Allocates, expands, frees, and reparents per-memcg `shrinker_info` structures.
- Allocates memcg-aware shrinker ids with an IDR and expands every online memcg's shrinker bitmap/deferred arrays as ids grow.

Important behavior:
- `do_shrink_slab()` first calls `count_objects()`. `SHRINK_EMPTY` and zero mean no scan work; otherwise it computes `delta` from priority and `seeks`, adds deferred work, caps scan work to twice freeable objects, and calls `scan_objects()` in batches.
- Shrinkers with `seeks == 0` are scanned aggressively because their objects are assumed cheap to recreate.
- Unused scan work is returned to deferred accounting so later reclaim can pick it up without over-scanning concurrent shrinkers.
- Global shrinking uses `shrinker_try_get()` under RCU, drops RCU while running potentially sleeping callbacks, reacquires RCU before `shrinker_put()`, and then continues iteration safely.
- Memcg shrinking walks bitmap units. If a shrinker reports `SHRINK_EMPTY`, the bit is cleared, a memory barrier pairs with `set_shrinker_bit()`, and the shrinker is sampled one more time to avoid losing a concurrent object addition.
- `set_shrinker_bit()` is the producer-side hook for memcg-aware shrinkers; it sets the per-memcg/node bit after a barrier so reclaim sees newly queued objects.
- `shrinker_free()` drops the registration reference, waits for in-flight lookups to finish through a completion, removes list/debugfs/id state under `shrinker_mutex`, and frees memory after an RCU grace period.

Dependencies:
- Uses memcg internals, RCU, IDR, mutexes, completions/refcounts, atomic deferred counters, vmscan tracepoints, debugfs helper functions from `shrinker_debug.c`, NUMA node ids, and shrinker callback contracts from `linux/shrinker.h`.

Notable risks:
- Lifetime rules are delicate: reclaim may run shrinker callbacks while unregister is waiting, so refcount/completion/RCU ordering must remain exact.
- Per-memcg shrinker-info expansion copies old unit pointers and publishes new arrays under RCU; readers must reacquire RCU after sleeping callbacks because the array may have been replaced.
- Deferred scan accounting is approximate and concurrent by design; incorrect capping or missed updates can cause either reclaim latency or cache growth.
- Memcg-aware shrinkers depend on producers setting bits when objects appear. If a subsystem forgets to call `set_shrinker_bit()`, memcg reclaim may skip reclaimable objects.
<!-- END FILE RESEARCH: sources/os/linux/linux/mm/shrinker.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/mm/shrinker_debug.c -->
# File Research: sources/os/linux/linux/mm/shrinker_debug.c

Provides debugfs visibility and manual scan control for registered shrinkers. It creates `/sys/kernel/debug/shrinker/<name-id>/count` and `scan` files for each shrinker once debugfs is available.

Key responsibilities:
- Maintains a shrinker debugfs root and an IDA for unique per-shrinker debugfs ids.
- Counts shrinker objects per node and per memcg through the shrinker's `count_objects()` callback.
- Implements a `count` seq_file that prints one line per memcg with nonzero objects: memcg id followed by per-node counts.
- Implements a write-only `scan` file accepting `memcg_id nid nr_to_scan` to invoke `scan_objects()` manually.
- Adds debugfs directories/files when shrinkers register and creates entries for already-registered boot shrinkers at late init.
- Supports runtime debugfs renaming and detach/remove during shrinker free.

Important behavior:
- Non-NUMA-aware shrinkers are counted only on node 0; other nodes report zero.
- Non-memcg-aware shrinkers only accept memcg id 0 in the manual scan interface.
- Manual scans validate node id, memcg existence, and memcg online state before calling the shrinker.
- `shrinker_debugfs_add()` expects `shrinker_mutex` to be held and gracefully does nothing before the debugfs root exists.
- Removal is split into detach under `shrinker_mutex` and recursive debugfs removal outside the mutex.

Dependencies:
- Uses debugfs, seq_file, IDA allocation, user copy, memcg iteration/id lookup, shrinker callbacks, and the global shrinker list/mutex exported from the shrinker core.

Notable risks:
- Debugfs callbacks call shrinker methods directly with `GFP_KERNEL`; these files are diagnostic/control surfaces and can induce reclaim behavior if written by privileged users.
- Count output can be expensive on systems with many memcgs and NUMA nodes because it iterates memcgs and calls every shrinker's count callback.
- Lifetime safety depends on the core shrinker registration/free path detaching debugfs before final RCU free.
<!-- END FILE RESEARCH: sources/os/linux/linux/mm/shrinker_debug.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/mm/shuffle.c -->
# File Research: sources/os/linux/linux/mm/shuffle.c

Implements optional page allocator freelist shuffling for `CONFIG_SHUFFLE_PAGE_ALLOCATOR`. It randomizes high-order buddy free-list order during memory initialization/hotplug and provides a random head/tail choice helper for allocator insertion.

Key responsibilities:
- Defines the `page_alloc_shuffle_key` static branch and the `shuffle=` module parameter/boot parameter hook.
- Enables shuffling when the boolean parameter is set.
- Validates candidate pages for shuffling: online, same zone, currently buddy-free, and matching buddy order.
- Implements `__shuffle_zone()` as a Fisher-Yates-style random swap pass over order-`SHUFFLE_ORDER` PFN-aligned blocks in a zone.
- Swaps two free-list entries only when they share the same order and pageblock migratetype.
- Implements `__shuffle_free_memory()` to shuffle every zone in a pgdat.
- Implements `shuffle_pick_tail()` to return pseudo-random booleans used by allocator code to vary freelist insertion side.

Important behavior:
- Shuffling operates under the zone lock because it directly swaps `page->lru` entries on buddy free lists.
- Random targets are retried up to `SHUFFLE_RETRY` times to skip holes or unsuitable pages.
- The algorithm explicitly accepts distribution bias; its goal is to reduce allocator predictability rather than provide a mathematically perfect shuffle.
- The zone lock is periodically dropped every 100 order-sized blocks to reduce long lock hold times during large zone initialization.
- `shuffle_pick_tail()` intentionally has unsynchronized static random state; racing updates are considered harmless and add variation.

Dependencies:
- Uses page allocator zone/free-area state, buddy page metadata, pageblock migratetypes, random number helpers, static keys, and kernel parameter infrastructure.

Notable risks:
- The code manipulates allocator free lists directly, so page validation must reject any page not currently on the expected buddy list.
- It assumes same migratetype before `list_swap()`; mixing migration lists would corrupt allocator policy.
- The lock-dropping/rescheduling in `__shuffle_zone()` is necessary for latency but means zone free-list state can change between chunks.
<!-- END FILE RESEARCH: sources/os/linux/linux/mm/shuffle.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/mm/shuffle.h -->
# File Research: sources/os/linux/linux/mm/shuffle.h

Internal header for page allocator freelist shuffling. It exposes the static-key-gated entry points used by page allocator initialization and free paths.

Key responsibilities:
- Defines `SHUFFLE_ORDER` as `MAX_PAGE_ORDER`.
- Declares `page_alloc_shuffle_key`, `__shuffle_free_memory()`, `__shuffle_zone()`, and `shuffle_pick_tail()` when shuffling is configured.
- Provides inline wrappers `shuffle_free_memory()` and `shuffle_zone()` that return immediately unless the static branch is enabled.
- Provides `is_shuffle_order()` so allocator code can cheaply test whether an order participates in shuffle-related behavior.
- Provides no-op fallbacks when `CONFIG_SHUFFLE_PAGE_ALLOCATOR` is disabled.

Important behavior:
- The static branch keeps the disabled fast path cheap even in builds that include shuffling support.
- Disabled or unconfigured builds always return `false` for `shuffle_pick_tail()` and `is_shuffle_order()`.

Dependencies:
- Depends on jump labels/static keys and page allocator types such as `pg_data_t` and `struct zone` supplied by including contexts.

Notable risks:
- The wrappers intentionally hide all implementation details behind the static branch; callers must use the header helpers rather than call underscored functions directly if they need the disabled fast path.
<!-- END FILE RESEARCH: sources/os/linux/linux/mm/shuffle.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/mm/slab.h -->
# File Research: sources/os/linux/linux/mm/slab.h

Internal slab allocator header shared by SLUB/slab support code. It defines the in-memory layout of `struct slab`, core `struct kmem_cache` fields, kmalloc cache lookup helpers, debug/metadata helpers, and internal allocator entry points.

Key responsibilities:
- Defines freelist/counter packing for lockless slab freelist updates, including optional wide compare-exchange support to avoid ABA problems.
- Defines `struct slab`, which overlays selected `struct page` fields, with static assertions to keep the layout compatible.
- Provides conversion helpers between slab, folio, page, virtual address, node id, pgdat, order, size, and object index.
- Defines `struct kmem_cache` internal fields for flags, object sizes, free-pointer offset, sheaf capacity, order/object packing, constructor, alignment, redzone padding, sysfs/debug/randomization/KASAN/usercopy/stat fields, and per-node pointers.
- Provides `cache_has_sheaves()` and sysfs support stubs/entry points for configurations that support slab sysfs.
- Provides nearest-object and object-index helpers used by debugging, reporting, and object validation.
- Declares allocator lifecycle state (`enum slab_state`), global slab mutex/list/cache variables, kmalloc cache metadata, and boot/cache creation functions.
- Implements `kmalloc_slab()` to map requested allocation size, kmalloc bucket set, GFP flags, and caller into the appropriate kmem cache.
- Declares cache creation, merging, flag normalization, shutdown, shrink, release, and slabinfo functions.
- Defines slab debug flag helpers, KUnit hook stubs, KASAN/KMSAN metadata access suppression helpers, and SLUB debug/stat prototypes.
- Defines slab object extension helpers under `CONFIG_SLAB_OBJ_EXT`, including object-extension pointer decoding, stride handling, and indexed extension access.
- Declares memcg slab post-alloc/free hooks, RCU free helpers, large-kmalloc size/order helpers, unreclaimable slab dump hooks, heap object checking, deferred free barriers, and object info diagnostics.

Important behavior:
- `struct slab` deliberately reuses `struct page` storage. Compile-time assertions enforce field offsets and total size, so allocator code can safely reinterpret the first page of a slab folio as `struct slab`.
- ABA-resistant freelist updates are only enabled when the architecture provides the required wide cmpxchg and aligned `struct page` support.
- `page_slab()` checks the page type marker on the compound head and returns NULL for non-slab pages, including large kmalloc pages that are not ordinary slab objects.
- `slab_folio()` is the preferred abstraction for converting a slab to its backing folio, keeping callers away from direct casts.
- `kmalloc_slab()` uses the small-size index table for allocations up to 192 bytes and `fls(size - 1)` for larger kmalloc cache indexes.
- Metadata access helpers disable KASAN/KMSAN while allocator internals touch memory outside the logical allocated object.
- Object extensions are not refcounted; `get_slab_obj_exts()`/`put_slab_obj_exts()` instead bracket sanitizer suppression while callers inspect extension arrays.
- Init-on-alloc/free decisions avoid constructors and avoid unconditional clearing for `SLAB_TYPESAFE_BY_RCU` or poisoned caches unless the caller explicitly requested zeroing.

Dependencies:
- Depends on slab public APIs, folios/pages, memcontrol, list_lru, local locks, randomization, sysfs/kobjects, KFENCE, KASAN/KMSAN, hardened usercopy, debugfs, SLUB debug, KUnit, kmalloc bucket definitions, and architecture cmpxchg capabilities.

Notable risks:
- Layout coupling to `struct page` is intentionally strict; any page/slab field change must preserve asserted offsets or update the overlay design.
- Freelist hardening, randomization, object extensions, memcg metadata, and sanitizer suppression all interact with allocator hot paths, so helper misuse can become either a correctness bug or a performance regression.
- `kmalloc_slab()` assumes callers already validated nonzero size and maximum size.
- Object-extension pointer flags and memcg data bits share storage; the validation in `slab_obj_exts()` is important for catching invalid mixed states.
<!-- END FILE RESEARCH: sources/os/linux/linux/mm/slab.h -->