# Group Research: group_539_illumos_gate_sources_os_illumos_illumos_gate_usr_src_uts_common_os_b_22ce79164ba0

Scope checked against `Docs/research_subset_a.md`: `sources/os/illumos/illumos-gate` is included in subset A. All eight listed source files were read completely.

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/os/bio.c -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/os/bio.c

## Purpose

`bio.c` implements illumos kernel buffer cache and page-I/O buffer support. It provides classic block-buffer operations used by UFS and block devices, delayed-write handling, buffer invalidation/flush paths, buffer header/memory recycling, and `buf(9S)` helper interfaces.

## Main Interfaces

Core block-buffer APIs include `bread`, `breada`, `bwrite`, `bwrite2`, `bdwrite`, `bawrite`, `brelse`, `getblk`, `getblk_common`, `trygetblk`, `bflush`, `blkflush`, `bfinval`, `binval`, `bio_busy`, `bcheck`, `iowait`, `iodone`, `biowait`, `biodone`, `geterror`, and `clrbuf`.

Page-I/O and driver helper APIs include `pageio_setup`, `pageio_done`, `bioerror`, `bioreset`, `biosize`, `biomodified`, `bioinit`, `biofini`, and `bioclone`.

Private machinery includes `bio_getfreeblk`, `bio_mem_get`, `bio_bhdr_alloc`, `bio_bhdr_free`, `bio_recycle`, `bio_flushlist`, `bio_incore`, `bio_pageio_done`, and `hash2ints`.

## Behavior And Data Flow

The buffer cache is organized by hash buckets in `hbuf`, delayed-write lists in `dwbuf`, and a free header list in `bhdrlist`. Each `buf` is protected primarily by `b_sem`, while hash/free-list structure is protected by bucket locks plus `blist_lock`, `bfree_lock`, and `bhdr_lock`.

`bread_common()` gets or allocates a buffer through `getblk_common()`, issues `bdev_strategy()` or UFS logging/snapshot strategy hooks if the buffer is not already `B_DONE`, waits with `biowait()`, and returns the locked buffer.

`bwrite_common()` sends the buffer through the block strategy or UFS logging/snapshot path, optionally waits, and optionally releases. `bdwrite()` marks a buffer as delayed write and complete, while `bawrite()` opportunistically sets `B_ASYNC`.

`brelse()` returns buffers to the correct free or delayed-write list. It handles failed retry writes, stale/error buffers, `B_NOCACHE` private buffers, and wakes memory waiters.

## Cache Management

`getblk_common()` searches the hash chain for a matching non-stale buffer, waits safely if the buffer is busy, handles identity changes after dropping locks, and allocates a new buffer if no match exists. If a duplicate appears while allocating, it frees the newly allocated memory/header and returns the existing buffer.

`bio_getfreeblk()` accounts against the buffer high-water memory budget, allocates a header, then allocates buffer memory. If memory allocation fails, it scans free lists for reusable buffers of the right size before falling back to sleeping allocation.

`bio_recycle()` reclaims aged free buffers, writes delayed-write buffers, frees memory and headers, and waits on `bio_mem_cv` if no reclaim path can satisfy the request.

`binit()` sizes the cache from `bufhwm`, `bufhwm_pct`, physical memory, and heap virtual memory, then initializes hash buckets, delayed-write buckets, and free-list accounting.

## Flush And Invalidate Semantics

`bflush()` serializes against invalidations, gathers delayed-write candidates without blocking under hash locks, then writes them asynchronously.

`blkflush()` targets one device/block delayed-write buffer and writes it synchronously in intent, though the file notes `B_ASYNC` can undermine that guarantee.

`bfinval()` invalidates all buffers for a device. With `force`, it can clear delayed writes and retry flags, move buffers from delayed-write to normal free lists, and mark them stale. Without `force`, delayed writes cause `EIO`.

## Page I/O

`pageio_setup()` allocates a `B_PAGEIO | B_NOCACHE` buffer over a page list, updates VM/page-in statistics, initializes semaphores, and holds the vnode.

`biodone()` routes async page I/O and remapped I/O to `bio_pageio_done()`. That path maps page completion to `pvn_read_done()` or `pvn_write_done()` and then destroys the pageio buffer through `pageio_done()`.

`biomodified()` tests whether pages in a pageio buffer have hardware modified state using `hat_pagesync()`.

## Notable Invariants

- `b_sem` is the exclusive buffer lock; `B_WANTED/B_BUSY` are not primary synchronization.
- Hash locks protect list membership and bucket lengths.
- `brelse()` expects a held `b_sem`.
- Buffers on delayed-write lists have `B_DELWRI`; non-delayed free-list scanning asserts otherwise.
- `B_NOCACHE` buffers are destroyed on release, not returned to the global cache.
- Pageio buffers hold vnode references until `pageio_done()`.

## Dependencies

This file depends on block device strategy dispatch, UFS logging/snapshot hooks, VM page/pvn APIs, HAT page attributes, kernel semaphores/condition variables, kstats, CPU stats, DTrace probes, and tunables in `var`.

## Research Notes

High-risk areas are lock ordering around hash lists versus `b_sem`, delayed-write flush/invalidation races, retry-write preservation, panic-time behavior in `getblk_common()`, buffer recycling under memory pressure, and pageio/remapped buffer cleanup.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/os/bio.c -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/os/bitmap.c -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/os/bitmap.c

## Purpose

`bitmap.c` provides low-level operations on arbitrary-size bitmaps represented as arrays of `ulong_t`. Callers own range validation and bitmap sizing.

## Main Interfaces

Functions are `bt_availbit`, `bt_gethighbit`, `bt_range`, `odd_parity`, `bt_getlowbit`, and `bt_copy`.

## Behavior

`bt_availbit()` scans for the first zero bit up to `nbits`, first by word and then by bit. It returns the bit index or `-1`.

`bt_gethighbit()` walks downward from a word index until it finds a nonzero word, then returns the global index of the highest set bit.

`bt_range()` finds a consecutive run of set bits between `*pos1` and `end_pos`, returning the first set bit and one-past-last bit through `pos1` and `pos2`.

`odd_parity()` folds a `ulong_t` with shifts/xors until one parity bit remains.

`bt_getlowbit()` finds the lowest set bit in an inclusive `[start, stop]` range. It masks partial start and stop words and uses `lowbit()` on the first nonzero word.

`bt_copy()` copies a bitmap word array.

## Notable Invariants

- Bitmap size and range validity are caller responsibilities.
- `bt_availbit()` assumes `nbits > 0` because it subtracts one before computing the last word.
- Word-boundary masking in `bt_getlowbit()` is central to correctness for unaligned ranges.

## Dependencies

The file depends on bitmap macros from `sys/bitmap.h`, `highbit()`, `lowbit()`, and `ASSERT`.

## Research Notes

This is shared primitive code. Audit focus should be boundary handling for zero-sized inputs, inclusive stop ranges, and shift expressions around `partial_stop + 1`.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/os/bitmap.c -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/os/bitset.c -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/os/bitset.c

## Purpose

`bitset.c` implements dynamic kernel `bitset_t` storage and operations. It wraps bitmap macros with allocation, fanout support, atomic set/clear helpers, randomized selection, boolean set operations, matching, zeroing, and copying.

## Main Interfaces

Lifecycle and sizing: `bitset_init`, `bitset_init_fanout`, `bitset_fini`, `bitset_resize`, `bitset_capacity`.

Mutation and tests: `bitset_add`, `bitset_atomic_add`, `bitset_atomic_test_and_add`, `bitset_del`, `bitset_atomic_del`, `bitset_atomic_test_and_del`, `bitset_in_set`, `bitset_is_null`.

Search and algebra: `bitset_find`, `bitset_and`, `bitset_or`, `bitset_xor`, `bitset_match`, `bitset_zero`, `bitset_copy`.

## Behavior

`bitset_resize()` computes required words from `els << bs_fanout`, allocates zeroed storage, copies the overlapping old words, swaps storage, then frees the old array. Shrinking drops out-of-range elements.

Element positions are shifted by `bs_fanout`, allowing one logical element to map to spaced bitmap bits.

Atomic variants use bitmap atomic macros and return exclusive-test results for test-and-add/delete.

`bitset_find()` uses `CPU_PSEUDO_RANDOM()` to choose a starting word and rotate within words via `bitset_find_in_word()`, reducing bias toward low-order bits.

Boolean operations assume equal fanout and write into `res`, returning whether the result contains any set bits.

## Notable Invariants

- Callers must size the bitset before adding/removing elements.
- Add/delete assert the computed bit position is inside capacity.
- `bitset_find()` asserts `bs_words > 0`.
- Boolean operations assume compatible word counts; the code asserts only fanout equality.

## Dependencies

Uses `kmem_zalloc/free`, `bcopy`, `bzero`, bitmap macros, atomic bitmap macros, `lowbit()`, `CPU_PSEUDO_RANDOM()`, and kernel assertions.

## Research Notes

The main risks are caller-side capacity discipline, fanout overflow in `els << bs_fanout` or `elt << bs_fanout`, and ensuring result bitsets passed to boolean operations are at least as large as the operands.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/os/bitset.c -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/os/bp_map.c -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/os/bp_map.c

## Purpose

`bp_map.c` maps `struct buf` data into kernel virtual address space for page I/O or physical I/O buffers, and provides copy helpers for buffers that may not already be kernel-addressable.

## Main Interfaces

Public APIs are `bp_init`, `bp_mapin_common`, `bp_mapin`, `bp_mapout`, `bp_copyout`, and `bp_copyin`.

Private helpers are `bp_vmem_alloc` and `bp_copy_common`.

## Behavior

`bp_init()` records required mapping alignment and HAT flags, and may create a dedicated `bp_map` vmem arena for cached aligned mappings.

`bp_mapin_common()` returns immediately for already remapped buffers, non-page/phys buffers, or physical I/O already in kernel address space. Otherwise it computes page offset, size, page count, and color alignment.

For single-page shadow/pageio buffers, it can use the kernel physical mapping fast path (`hat_kpm_mapin`). Otherwise it allocates aligned kernel virtual space, records `B_REMAPPED`, and maps each source page or PFN with `hat_devload()`.

`bp_mapout()` reverses the mapping, handling the KPM fast path separately. For ordinary mappings it flushes instruction memory on SPARC, unloads locked mappings, frees vmem space, and clears `B_REMAPPED`.

`bp_copy_common()` copies between driver memory and buffers. It uses direct `bcopy()` for ordinary KVA buffers, mapin/mapout when KPM is unavailable or forced off, and otherwise maps one page at a time with KPM for pageio, shadow, or user physical buffers.

## Notable Invariants

- A buffer cannot be both `B_PAGEIO` and `B_PHYS`.
- `B_REMAPPED` marks ownership of a temporary kernel mapping.
- Color alignment from `bp_color()` is preserved.
- Physical user VAs are translated through the process address space or `kas`.
- `bp_copy_common()` asserts requested copy range is within `b_bcount`.

## Dependencies

The file depends on `buf`, VM pages, KPM, HAT APIs, `vmem`, page coloring/alignment macros, address spaces, and platform instruction-cache flush support on SPARC.

## Research Notes

Important audit areas are PFN lookup failures for user VAs, page-list traversal with offsets, KPM mapout address correctness, and ensuring all `B_REMAPPED` paths are paired with `bp_mapout()`.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/os/bp_map.c -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/os/brand.c -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/os/brand.c

## Purpose

`brand.c` implements common illumos branded-zone process support. It manages registered kernel brands, zone references to brands, process brand transitions, SPARC syscall interposition hooks, and helper logic for Solaris-derived brands during `exec`, fork, LWP lifecycle, and process exit.

## Main Interfaces

Brand registry and zone lifecycle: `brand_init`, `brand_register`, `brand_unregister`, `brand_register_zone`, `brand_zone_count`, `brand_unregister_zone`.

Process lifecycle: `brand_setbrand`, `brand_clearbrand`, `brand_solaris_copy_procdata`, `brand_solaris_exec`, `brand_solaris_fini`, `brand_solaris_forklwp`, `brand_solaris_freelwp`, `brand_solaris_initlwp`, `brand_solaris_lwpexit`, `brand_solaris_proc_exit`, `brand_solaris_setbrand`.

Brand syscall/exec helpers: `brand_solaris_cmd`, `brand_solaris_elfexec`.

SPARC-only helpers: `brand_plat_interposition_enable`, `brand_plat_interposition_disable`.

## Behavior

The global `brand_list` tracks loaded brands and per-brand zone reference counts under `brand_list_lock`. Registration rejects malformed brands, unsupported versions, and duplicate names. Zone registration may dynamically load `brand/<module>` with `ddi_modopen()` and then increments the matching brand refcount.

`brand_setbrand()` is called from exec for a single-threaded process, changes `p_brand`, and calls the brand’s `b_setbrand` operation. `brand_clearbrand()` calls `b_proc_exit` and restores the native brand.

On SPARC, the first non-native brand enables global syscall interposition by hot-patching trap-table patch points to branch to syscall wrappers. The last unregister restores original instructions.

`brand_solaris_cmd()` handles common branded syscall commands: executing native binaries, registering the user-space syscall handler, returning saved ELF data, and providing a truss visibility point.

`brand_solaris_elfexec()` is the largest path. It first execs the brand emulation library, saves its aux-vector data, maps the target executable and optional branded linker, rewrites process exec environment and aux vectors so debuggers see target program data, emits brand-specific aux vectors for the emulation library, sets `AF_SUN_NOPLM`, and clears `spd_handler` until user-space brand initialization completes.

## Notable Invariants

- Brand operations generally assume single-threaded exec context.
- `p_brand_data` exists for branded processes and is freed on process exit.
- Registered brand modules cannot unload while zones reference them.
- Labeled systems reject branded zones.
- SPARC interposition changes are protected by `brand_list_lock` and only enabled while brands are loaded.

## Dependencies

This file depends on zone state, process/LWP structures, brand machine operations, module loading, ELF exec helpers, aux-vector layout, vnode lookup/release, copyin/copyout, and platform hot-patching.

## Research Notes

Audit hotspots are `brand_solaris_elfexec()` error unwinding after partial exec-environment changes, aux-vector rewriting for 32-bit versus native models, dynamic module/brand-name mismatch handling, and SPARC syscall patch restoration.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/os/brand.c -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/os/callb.c -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/os/callb.c

## Purpose

`callb.c` implements the generic kernel callback table used for checkpoint/resume, debugger, and daemon coordination events. Callbacks are grouped by class and executed serially per class.

## Main Interfaces

Registration and deletion: `callb_init`, `callb_add`, `callb_add_thread`, `callb_delete`.

Execution/control: `callb_execute_class`, `callb_lock_table`, `callb_unlock_table`.

CPR helpers: `callb_generic_cpr`, `callb_generic_cpr_safe`, `callb_is_stopped`.

## Behavior

Callbacks are stored in `callb_table_t`, with class heads in `ct_first_cb[]`, a freelist, a table lock, and a busy gate preventing additions while callers lock the table.

`callb_add_common()` waits while the table is busy, allocates or reuses a callback record, records the target thread, function, argument, class, and name, then inserts at the class-list head.

`callb_delete()` locates the entry in its class, waits if the callback is executing, unlinks it, marks it free, and returns it to the freelist.

`callb_execute_class()` walks a class list under the table lock, marks each callback executing, drops the lock while calling it, and stops on the first callback failure, returning that callback name.

`callb_generic_cpr()` implements standard CPR daemon behavior by setting `CALLB_CPR_START`, optionally waiting until safe, and signaling resume. `callb_is_stopped()` checks whether a kernel thread is registered and safe/stopped for CPR, falling back to a symbol name for unknown threads.

## Notable Invariants

- `ct_lock` protects callback state and list membership.
- Deletion waits for `CALLB_EXECUTING` to clear.
- Execution drops the table lock around callback invocation.
- Callback names are bounded by `CB_MAXNAME`.
- The table busy flag prevents concurrent additions in special phases.

## Dependencies

Depends on kernel threads, condition variables, CPR protocol structures, task/thread state, `kobj_getsymname()`, and delay/retry constants.

## Research Notes

Key risks are callback deletion while class execution is walking the list, callbacks that block or recursively manipulate callback state, and CPR stop checks that depend on thread sleep/stop timing.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/os/callb.c -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/os/callout.c -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/os/callout.c

## Purpose

`callout.c` implements illumos timeout/callout scheduling. It supports legacy `timeout(9F)` IDs and full callout IDs, per-CPU normal and realtime callout tables, cyclic-based expiration, taskq execution for normal callouts, high-resolution grouping, cancellation, CPU online/offline migration, CPR suspend/resume, debugger time adjustment, and hrestime changes.

## Main Interfaces

Creation/cancellation: `timeout_generic`, `timeout`, `timeout_default`, `realtime_timeout`, `realtime_timeout_default`, `untimeout_generic`, `untimeout`, `untimeout_default`.

Expiration paths: `callout_realtime`, `callout_queue_realtime`, `callout_normal`, `callout_queue_normal`, `callout_execute`, `callout_hrestime`.

Lifecycle: `callout_init`, `callout_mp_init`, `callout_cpu_online`, `callout_cpu_offline`.

Private machinery covers callout/list allocation, list lookup, heap insert/delete/process, queue insert/delete/process, cyclic setup, kstats, CPR/debug callbacks, and expired-list execution.

## Behavior

Each CPU has realtime and normal callout tables. Realtime callouts execute from low-level cyclic context. Normal callouts are noticed by a cyclic handler at lock PIL and executed by a per-table taskq at thread context.

Callouts are grouped by exact expiration into `callout_list_t` objects. Lists are indexed by expiration hash, tracked in a min-heap when possible, and placed in a sorted queue if heap expansion fails. A separate ID hash table supports cancellation.

`timeout_generic()` computes expiration, applies resolution/rounding, chooses an ID format, finds or creates a matching callout list, inserts the list into the heap or queue, appends the callout to the list and ID hash, and updates pending counters.

`untimeout_generic()` locates an ID, removes unexpired callouts, waits for currently executing callouts unless `nowait` or self-cancel applies, and returns remaining time or `-1`.

Expiration proceeds in two phases: expired lists are moved to `ct_expired`, then `callout_expire()` invokes each callback, frees callout records to the table freelist, and wakes waiters.

## Time And CPU Handling

Heap processing cleans empty lists, adjusts relative callouts after debugger pauses, and expires absolute hrestime callouts after system time changes. CPR suspend reprograms cyclics to infinity; resume processes time changes and reprograms earliest expirations.

CPU online creates lgroup-local kmem caches, initializes table heaps/hashes/kstats/cyclics, creates taskqs for normal tables, and binds cyclics to the CPU. CPU offline unbinds cyclics so the cyclic subsystem can move them.

## Notable Invariants

- `ct_mutex` protects all table-local callout/list/heap/hash state.
- Callout structures and lists are persistent and recycled, not normally destroyed.
- `CALLOUT_EXECUTING` in `c_xid` coordinates `untimeout()` with active callbacks.
- Empty heaped lists are lazily reaped through `ct_nreap`.
- Normal callouts may need multiple taskq executor threads to avoid dependency deadlocks.
- Realtime handlers must avoid paths such as `cpu_lock` that can deadlock CPU offline.

## Dependencies

Depends on cyclic subsystem, taskq, CPU online/offline, kmem caches, lgroup handles, kstats, CPR callbacks, debugger callbacks, DTrace probes, and callout ID macros from `sys/callo.h`.

## Research Notes

Audit hotspots include ID generation/wrap semantics, cancellation while executing, heap cleanup and queue fallback correctness, cyclic reprogramming under suspend/offline, normal-callout taskq dispatch guarantees, and absolute hrestime expiration on clock changes.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/os/callout.c -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/os/cap_util.c -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/os/cap_util.c

## Purpose

`cap_util.c` implements capacity/utilization measurement for processor hardware components using CPU performance counters. It programs per-CPU CPC contexts, samples counters, attributes utilization to CPUs and processor groups, exports per-CPU hardware-sharing kstats, and coordinates with DTrace CPC use and CPU online/offline events.

## Main Interfaces

Global control: `cu_init`, `cu_disable`, `cu_enable`.

Counter control: `cu_cpc_program`, `cu_cpc_unprogram`.

Updates: `cu_cpu_update`, `cu_pg_update`.

CPU lifecycle and helpers are mostly private: `cu_cpu_callback`, `cu_cpu_init`, `cu_cpu_fini`, `cu_cpu_disable`, `cu_cpu_enable`, `cu_cpu_run`, `cu_cpc_trigger`, `cu_cpu_update_stats`, `cu_cpu_kstat_create`, and `cu_cpu_kstat_update`.

## Behavior

`cu_init()` verifies the framework is enabled, initializes CPC support, allocates request storage, initializes per-active-CPU state, sets the module online, programs counters on active CPUs, and registers a CPU setup callback.

`cu_cpc_init()` determines which CPC events are needed. It first asks platform code through `cu_plat_cpc_init()`. If unsupported, common code walks the CPU’s CMT processor-group lineage and requests events such as `PAPI_tot_ins` for instruction pipeline groups and `PAPI_fp_ins` for FPU groups. It creates per-CPU/per-PG counter info and kstats.

`cu_cpu_init()` allocates `cpu_cu_info`, counter stats, and CPU-bound CPC contexts. `cu_cpu_fini()` deletes kstats, frees stats and CPC contexts, detaches `cpu_cu_info` via cross-call if needed, and frees the CPU state.

`cu_cpc_program()` runs on the target CPU at high PIL with preemption disabled. It refuses to program if CU is off, DTrace CPC is active, counters are already on, counters are disabled, or a live CPU CPC context exists. It rotates through prepared contexts, programs CPC counters, marks counters on, and samples initial state.

`cu_cpc_unprogram()` updates stats, validates that the current CPU CPC context is the CU context, unprograms counters, clears `cpu_cpc_ctx`, and marks counters off.

## Sampling And Kstats

`cu_cpu_update()` throttles sampling using `cu_update_threshold`. When sampling is needed, it reads CPC counters on the owning CPU either by cross-call or directly.

`cu_cpu_update_stats()` updates per-counter start values, deltas, running/stopped time, total utilization, current rate, and max rate. It handles off-to-on transitions by treating the current counter value as the new start.

`cu_cpu_kstat_update()` exports CPU id, PG id, generation, total utilization, running/stopped time, rate, max rate, and relationship string. Without `priv_cpc_cpu`, utilization values are zeroed.

`cu_pg_update()` aggregates all CPUs in a hardware processor group, updates each CPU first, sums utilization/time fields, accounts for stopped counters, and computes group rate/max rate.

## CPU And DTrace Coordination

`cu_disable()` and `cu_enable()` iterate active CPUs under `cpu_lock` and use CPU calls to toggle collection. `cu_cpc_trigger()` maintains a per-CPU disable count, unprogramming on first disable and reprogramming when the count returns to zero.

The CPU setup callback initializes state on `CPU_ON`, programs counters on `CPU_INTR_ON`, and disables/frees state on `CPU_OFF`.

DTrace CPC interaction is explicit: CU counters are not programmed while `dtrace_cpc_in_use` is true, and newly initialized CPUs start disabled when DTrace owns CPC.

## Notable Invariants

- CPC programming/unprogramming must run on the target CPU at high PIL with preemption disabled.
- `cpu_lock` protects CPU lifecycle initialization/finalization.
- `cpu_cu_info` must not be freed until target-CPU access is quiesced.
- Sampling is intentionally throttled to avoid excessive cross-calls.
- Kstat consumers need `priv_cpc_cpu` to see utilization data.
- CPU generation is exported so consumers can reject snapshots across topology changes.

## Dependencies

Depends on CPC/kcpc, CPU cross-calls, processor groups/CMT, platform CU hooks, DTrace CPC state, kstats, privilege checks, CPU lifecycle callbacks, high-resolution time, and hardware sharing relationship metadata.

## Research Notes

High-risk areas are target-CPU execution assumptions, interaction with thread-bound CPC contexts during CPU online, DTrace CPC disable/re-enable sequencing, cleanup of partially initialized CPU state, and rate calculations when CPUs go offline or counters stop mid-sample.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/os/cap_util.c -->