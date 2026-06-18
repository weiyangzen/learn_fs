# Group Research: group_552_illumos_gate_sources_os_illumos_illumos_gate_usr_src_uts_common_os_l_8cdfd25cbd17

Scope: `Docs/research_subset_a.md` includes `sources/os/illumos/illumos-gate`. All listed files were read completely.

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/os/lwp.c -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/os/lwp.c

## Purpose

Implements illumos kernel support for lightweight processes: LWP creation, exit, fork duplication, process-wide LWP hold/continue/exit coordination, LWP directory/hash-table maintenance, and per-LWP accounting updates.

This file is central to process/thread lifecycle correctness. It ties together scheduler classes, `/proc` synchronization, zones/tasks/projects resource controls, brand hooks, contract templates, microstate accounting, lgroup placement, and LWP id lookup.

## Main Responsibilities

- Create kernel and user LWPs through `lwp_kernel_create()` and `lwp_create()`.
- Manage LWP stacks, including segkp stack allocation and death-row reuse.
- Enforce task/project/zone `max-lwps` resource controls.
- Grow and maintain `p_lwpdir` and `p_tidhash`.
- Stop, continue, and hold LWPs for fork, fork1, vfork, watchpoints, `/proc`, core dump, exec, and process exit.
- Tear down an exiting LWP and maintain process counts.
- Duplicate LWP state for fork through `forklwp()`.
- Provide fast LWP id lookup and locked lookup for unparking paths.
- Update selected per-LWP resource counters.

## Key Entry Points

- `lwp_kernel_create(proc_t *p, void (*proc)(), void *arg, int state, pri_t pri)`
  Creates a kernel LWP in a system process and returns the backing `kthread_t`.

- `lwp_create(...)`
  Allocates/initializes `klwp_t` and `kthread_t`, assigns tid, links into process thread list, inserts directory/hash entries, performs class/brand/lgroup setup, and optionally starts the LWP.

- `lwp_create_done(kthread_t *t)`
  Completes creation by setting `TS_CREATE | TS_CSTART`, updating `p_lwprcnt`, and making the thread runnable.

- `lwp_exit(void)`
  Main per-LWP exit path. Handles tsd, CPC, poll, doors, schedctl, upimutex, brand exit, `/proc`, zombie/detached LWP handling, counts, scheduler exit, context exit, address-space/HAT transition, and zombie switch.

- `lwp_cleanup(void)`
  Shared cleanup for exiting LWP or process exit, including timers, `/proc` agent cleanup, lgroup removal, and contract template clearing.

- `lwp_suspend(kthread_t *t)` / `lwp_continue(kthread_t *t)`
  Implements targeted LWP suspension and resumption through `TP_HOLDLWP`, `p_holdlwps`, and scheduler state.

- `holdlwp()`, `holdlwps(int holdflag)`, `holdwatch()`
  Process-wide LWP quiescing mechanisms for fork/fork1/watchpoint activity.

- `pokelwps(proc_t *p)`, `runlwps(proc_t *p, ushort_t schedbits)`, `continuelwps(proc_t *p)`
  Force LWPs into kernel, run stopped LWPs, or continue suspended LWPs.

- `exitlwps(int coredump)`
  Coordinates termination or core-dump quiescence of all other LWPs in the process.

- `forklwp(klwp_t *lwp, proc_t *cp, id_t lwpid)`
  Duplicates an LWP into a child process, copying register/FPU/door/contract/brand/scheduler state.

- `lwp_hash_in()`, `lwp_hash_out()`, `lwp_hash_lookup()`, `lwp_hash_lookup_and_lock()`
  Maintain and query process-local LWP id directory/hash structures.

- `lwp_stat_update(lwp_stat_id_t id, long inc)`
  Updates selected `lwp_ru` resource counters.

## Important Data Structures

- `proc_t`
  Uses `p_lock`, `p_tlist`, `p_lwpcnt`, `p_lwprcnt`, `p_lwpdaemon`, `p_lwpwait`, `p_lwpdwait`, `p_lwpdir`, `p_lwpfree`, `p_tidhash`, `p_ret_tidhash`, flags such as `SEXITLWPS`, `SHOLDFORK`, `SHOLDFORK1`, `SHOLDWATCH`, `SWATCHOK`, `SLWPWRAP`.

- `klwp_t`
  Per-LWP kernel state: thread pointer, process pointer, signal alt stack, child stack size, contracts, signal info, brand data, registers/FPU pointers, resource usage.

- `kthread_t`
  Scheduler/thread state: `t_lwp`, `t_tid`, `t_proc_flag`, `t_schedflag`, class fields, binding/lgroup fields, context ops, stack pointer.

- `lwpent_t`, `lwpdir_t`, `tidhash_t`, `ret_tidhash_t`
  LWP directory and LWP id hash table elements. Retired hash tables are retained for safe lockless-ish lookup races.

## Locking and Synchronization

- `p->p_lock` protects process LWP/thread list state, counts, flags, and directory mutations.
- `p->p_zone->zone_nlwps_lock` protects zone/task/project LWP accounting updates.
- Per-bucket `tidhash_t.th_lock` protects LWP id hash buckets.
- `lwp_hash_lookup_and_lock()` intentionally searches without `p_lock`; table growth uses memory barriers and acquires all old/new bucket locks before publishing a new hash table.
- `/proc` synchronization uses `prbarrier(p)` before manipulating states visible to `/proc`.
- `pidlock` protects global thread linkage and join wakeups during final exit.
- `p_holdlwps` condition variable coordinates process-wide holds, exits, and suspension waits.
- `pool_barrier_enter/exit` interaction is handled around stop points in `lwp_create()`.

## Lifecycle Notes

- `lwp_create()` increments task/project/zone LWP counts before allocation; every allocation/class/brand/tid failure path must unwind these counts.
- Default-size LWP stacks can be reused from `lwp_deathrow`; reused context ops are freed before reuse.
- New LWPs are created stopped with `TP_HOLDLWP` and without `TS_CREATE`, so callers can finish initialization before scheduling.
- `lwp_exit()` can trigger whole-process `proc_exit()` when the last non-daemon LWP exits.
- Non-detached exiting LWPs can remain as zombie directory entries until waited for or detached.
- `exitlwps()` has two modes: coredump quiescence without destruction, and full termination for exec/exit/shutdown paths.

## Error and Edge Handling

- System LWP creation failures panic, because system processes should not exhaust LWP ids.
- LWP id wrap uses `SLWPWRAP` and hash lookup to avoid duplicate live tids.
- If process is exiting while creating a current-process LWP, creation fails.
- `holdlwps()` and `holdwatch()` include precedence logic for exit, fork, fork1, watchpoint activity, job control, and `/proc` stops.
- `exitlwps()` handles stopped dangling LWPs from aborted hold operations and cleans zombie LWP directory entries.

## External Dependencies

Scheduler class operations (`CL_ALLOC`, `CL_ENTERCLASS`, `CL_FORK`, `CL_EXIT`), `/proc`, doors, schedctl, upimutex, contract templates, brands, CPC, lgroup, zones/tasks/projects resource controls, HAT, segkp stack allocation, and DTrace probes.

## Research Notes

This file is a high-risk concurrency core. The most important invariants are balanced LWP accounting, safe publication/reclamation of tid hash tables, correct `p_lwprcnt` transitions around stopped/runnable LWPs, and respecting `/proc` barriers before exposing process state changes.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/os/lwp.c -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/os/main.c -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/os/main.c

## Purpose

Machine-independent kernel startup path. It initializes core kernel subsystems, mounts root, prepares process 0, creates init/pageout/fsflush/cluster processes, starts selected system threads, and enters the scheduler.

It also builds the initial user stack and exec state for `/sbin/init` or zone init.

## Main Responsibilities

- Maintain well-known process globals: `proc_sched`, `proc_init`, `proc_pageout`, `proc_fsflush`.
- Define global memory counters `maxmem`, `freemem`, and startup state `interrupts_unleashed`.
- Provide process-zero static LWP directory/hash storage.
- Construct init argument stack and invoke `exec_common()`.
- Initialize init process address-space model and protections.
- Drive the ordered kernel bootstrap sequence in `main()`.
- Create init, pageout, fsflush, optional cluster process, and p0 system threads.
- Initialize process 0’s LWP directory and tid hash.

## Key Entry Points

- `cluster_wrapper()`
  Invokes `cluster()` and panics if it returns.

- `exec_init(const char *initpath, const char *args)`
  Builds the initial user stack layout for init, including argv strings and pointers, handles ILP32 argv packing, sets syscall argument state for `execve`, clears inherited signal mask, and retries selected transient `exec_common()` failures.

- `start_init_common()`
  Common global-zone and non-global-zone init setup. Establishes init pid in zone, resets accounting, creates address space, sets 32-bit model/user limits/protections, initializes core state, and calls `exec_init()`.

- `start_init()`
  Sets `proc_init`, starts global init, and enters `lwp_rtt()` after successful exec setup.

- `main(void)`
  Top-level MI kernel startup routine.

## Startup Ordering Highlights

`main()` performs a strict sequence:

1. Takes `ualock` to prevent administrative shutdown during boot.
2. Initializes lgroup stage 2.
3. Runs `startup()`, `segkmem_gc()`, callback/cyclic/callout/clock setup.
4. Reinitializes microstate counters after final time source selection.
5. Initializes lgroup stage 3 and calls `init_tbl`.
6. Loads iSCSI boot properties, initializes VM and physio buffers.
7. Drops to `spl0()` and sets `interrupts_unleashed`.
8. Creates `process_cache`.
9. Mounts root via `vfs_mountroot()`.
10. Initializes error queues, CPU kstats, timestamps, post-startup, swap state, audit.
11. Starts vmem periodic rescale and optionally plumbs networking.
12. Configures console, releases bootstrap memory, force-attaches drivers.
13. Calls `setupclock()`.
14. Initializes p0 LWP directory/hash and inserts current thread.
15. Initializes extended accounting and sysevent channel threads.
16. Completes lgroup and MP initialization.
17. Starts platform post-startup hooks and SMT late init on x86.
18. Creates init, pageout, fsflush, and optional cluster processes.
19. Starts module uninstall and seg_pasync p0 threads.
20. Releases `ualock`, labels p0 as `sched`, and enters `sched()`.

## Important Data

- `initname`, `initargs`
  Default init path and boot args.

- `p0_lwpdir[2]`, `p0_tidhash[2]`, `p0_lep`
  Static initial LWP directory/hash resources for process 0.

- `process_cache`
  Kmem cache for `proc_t`.

## Locking and Synchronization

- `ualock` blocks disruptive administrative actions during startup.
- p0 LWP directory initialization occurs after `setupclock()` and before accounting/sysevent and process creation.
- Interrupts are only unleashed after clock/callout/cyclic setup and before root mount and driver activity requiring interrupts.

## Init Stack Construction

`exec_init()` treats boot args as space-delimited tokens with no quoting support. It copies the combined init path and args string to the top of the user stack, builds argv pointers beneath it, converts argv to 32-bit pointers for ILP32 processes, and sets current LWP syscall state so `exec_common()` sees an `execve`-style call.

## External Dependencies

Boot properties, VFS root mount, VM, HAT, lgroup, callouts/cyclics, DDI, audit, STREAMS plumbing, module subsystem, scheduler, pageout, fsflush, sysevent, fastboot, SMT, and process creation.

## Research Notes

This file is mostly sequencing glue. Bugs here are usually ordering bugs: using a subsystem before its clock/callout/root/VM/driver prerequisite, or allowing shutdown/admin interference during boot. The p0 LWP directory setup is also a direct dependency of LWP lookup semantics used elsewhere.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/os/main.c -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/os/mem_cage.c -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/os/mem_cage.c

## Purpose

Implements the kernel memory cage. The cage reserves and manages relocatable/non-relocatable physical page ranges so kernel memory can remain available while supporting dynamic memory operations and page relocation policies.

It maintains cage ranges, thresholds, free-page accounting, cage expansion, cageout reclaim, allocator throttling, kstats, and memory DR callbacks.

## Main Responsibilities

- Track cage growth ranges with `kcage_glist`.
- Initialize the cage from physical memory lists.
- Mark pages as non-relocatable (`P_NORELOC`) as they enter the cage.
- Reclaim or relocate cage pages under pressure.
- Expand the cage when cage free memory falls below thresholds.
- Throttle page creation when cage memory is scarce.
- Register callbacks for physical memory add/delete threshold recalculation.
- Publish cage ranges through kstat.
- Coordinate cageout thread behavior around CPR suspend/resume.

## Key Data Structures

- `struct kcage_glist`
  Range node with `base`, `lim`, `curr`, and growth direction `decr`. The allocated cage is the consumed part of these monotonic ranges.

- `kcage_glist`
  Head of all cage-eligible ranges.

- `kcage_current_glist`
  Current range being consumed for cage expansion.

- `kcage_range_rwlock`
  Protects range list structure and major range updates.

- Cage thresholds:
  `kcage_freemem`, `kcage_needfree`, `kcage_lotsfree`, `kcage_desfree`, `kcage_minfree`, `kcage_throttlefree`, `kcage_reserve`.

- Cageout synchronization:
  `kcage_cageout_mutex`, `kcage_cageout_cv`, `kcage_cageout_ready`, `kcage_cageout_thread`.

- Throttle synchronization:
  `kcage_throttle_mutex`, `kcage_throttle_cv`.

- Optional `KCAGE_STATS`
  Debug-only scan and event counters for cageout, expansion, throttling, and invalidation.

## Key Entry Points

- `kcage_current_pfn(pfn_t *pfncur)`
  Returns approximate current cage PFN and direction for contiguous page allocation exclusion.

- `kcage_next_range(int incage, pfn_t lo, pfn_t hi, pfn_t *nlo, pfn_t *nhi)`
  Finds the lowest overlapping cage or non-cage range in a PFN interval.

- `kcage_range_init(struct memlist *ml, kcage_dir_t d, pgcnt_t preferred_size)`
  Creates cage arena, builds initial glist from memlist, and calls `kcage_init()`.

- `kcage_range_add()`, `kcage_range_delete()`, `kcage_range_delete_post_mem_del()`
  Dynamic range management APIs.

- `kcage_recalc_thresholds()`
  Recomputes thresholds from `total_pages` and configured initial values, wakes cageout/throttled waiters when needed.

- `kcage_cageout_init()`
  Starts cageout LWP under `proc_pageout` if cage is enabled.

- `kcage_create_throttle(pgcnt_t npages, int flags)`
  Blocks or classifies page creation requests depending on cage free memory, real-time priority, panic/cageout context, VM criticality, and wait flags.

- `kcage_freemem_add()` / `kcage_freemem_sub()`
  Atomic cage free-memory accounting and wakeup trigger points.

- `kcage_cageout_wakeup()`
  Signals cageout thread or performs early expansion before cageout is ready.

- `kcage_tick()`
  Periodic safety wakeup for throttled threads.

## Internal Algorithms

### Range Management

`kcage_range_add_internal()` creates a new glist node and deletes overlaps from the new range before appending it. `kcage_glist_delete()` supports whole-range removal, front/back trimming, and middle splits. Deletion refuses ranges overlapping already-used cage portions unless called from post-memory-delete cleanup.

### PFN Allocation

`kcage_get_pfn()` consumes PFNs from `kcage_current_glist`, growing either upward or downward. It advances to the next range when the current range is exhausted.

`kcage_walk_cage()` walks the static allocated portion of the cage in ascending PFN order for cageout scans.

### Initialization

`kcage_init()` recalculates preferred size, registers kphysm callbacks, chooses startup cage size bounded by `kcage_minfree` and `availrmem`, marks startup cage pages `P_NORELOC`, captures existing kernel allocated pages from `kvp.v_pages`, enables `kcage_on`, registers CPR callback, optionally coalesces free pages for large pages, and installs raw kstat reporting.

### Assimilation and Reclaim

`kcage_assimilate_page()` tries to lock a page, mark it non-relocatable, and either move a free page to the correct NORELOC list or invalidate/relocate an allocated page.

`kcage_invalidate_page()` unloads mappings, checks lock/COW/modified state, relocates if required, demotes large pages when possible, and disposes clean unshared pages.

`kcage_expand()` consumes new PFNs from the glist until enough free caged pages exist or expansion cannot progress.

`kcage_cageout()` scans caged pages, assimilates holes, skips pages it cannot safely lock or pages with excessive sharing, invalidates/relocates pages, expands if still under throttle threshold, and broadcasts to throttled allocators.

## Locking and Synchronization

- Range list edits require `kcage_range_rwlock` writer lock.
- Read-side range queries tolerate some `curr` movement races by design.
- Cageout waits on `kcage_cageout_cv` under `kcage_cageout_mutex`.
- Throttled allocators wait on `kcage_throttle_cv` under `kcage_throttle_mutex`.
- `kcage_freemem` and `kcage_needfree` use atomics in some startup paths.
- Page-level operations depend on page locks, group page locks, HAT unload synchronization, and free-list manipulation rules.

## External Dependencies

VM page allocator, page relocation, HAT, page free/cache lists, kphysm setup callbacks, CPR callbacks, kstats, lgrp, segkmem large page settings, pageout scanner, and memory deletion state via `pfn_is_being_deleted()`.

## Research Notes

The cage is a pressure-control subsystem with subtle accounting. Key invariants are: `P_NORELOC` pages must be on appropriate accounting lists, cage expansion must not enter memory being deleted, cageout must not block itself, and throttled allocators must eventually be woken even if reclaim makes no forward progress.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/os/mem_cage.c -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/os/mem_config.c -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/os/mem_config.c

## Purpose

Implements dynamic physical memory configuration: adding memory, preparing/deleting memory spans, tracking delete handles, coordinating page relocation/collection, updating memsegs and memory lists, and notifying registered subsystems.

This is the core kernel memory DR implementation for adding/removing physical pages from the running system.

## Main Responsibilities

- Dynamically add physical memory and its `page_t` metadata.
- Reserve add/delete spans to prevent overlapping operations.
- Allocate and manage memory delete handles.
- Validate delete spans against installed memory, memsegs, cage/nonrelocatable pages, and architecture constraints.
- Start asynchronous memory delete threads.
- Relocate, page out, destroy, or collect pages from delete spans.
- Clean up deleted memsegs and remap deleted page metadata to dummy pages.
- Maintain `phys_install`, `phys_avail`, `physmax`, `physinstalled`, `total_pages`, `maxmem`, `physmem`, `availrmem`, and dump sizing.
- Register callback vectors for subsystems affected by physical memory add/delete.
- Split memsegs for partial delete operations.
- Manage reusable dynamic memseg virtual-address space.

## Major Entry Points

- `kphysm_add_memory_dynamic(pfn_t base, pgcnt_t npgs)`
  Adds a dynamic memory span. Handles span reservation, installed-memory insertion, page metadata allocation/mapping, memnode setup, page counter resize, memseg allocation/reuse, page initialization/freeing, global memory accounting, page coalescing, callbacks, DDI notification, and rollback on failures.

- `kphysm_del_gethandle(memhandle_t *xmhp)`
  Allocates a delete handle and enters `MHND_INIT`.

- `kphysm_del_span(memhandle_t handle, pfn_t base, pgcnt_t npgs)`
  Intersects requested span with `phys_install`, reserves non-overlapping delete spans, checks memseg coverage and relocatability, splits memsegs when needed, rejects `P_NORELOC` pages, and records page counts.

- `kphysm_del_span_query(pfn_t base, pgcnt_t npgs, memquery_t *mqp)`
  Reports installed, managed, and non-relocatable page counts and first/last non-relocatable PFNs.

- `kphysm_del_start(memhandle_t handle, void (*complete)(void *, int), void *complete_arg)`
  Starts asynchronous memory deletion in `delete_memory_thread()`.

- `kphysm_del_cancel(memhandle_t handle)`
  Requests cancellation and wakes the delete thread.

- `kphysm_del_status(memhandle_t handle, memdelstat_t *mdstp)`
  Reports delete progress from handle counters.

- `kphysm_del_release(memhandle_t handle)`
  Releases handles in init/done states and removes reserved spans.

- `pfn_is_being_deleted(pfn_t pfnum)`
  Allows other subsystems, notably the cage, to detect active deletion spans.

- `kphysm_setup_func_register()` / `kphysm_setup_func_unregister()`
  Register post-add, pre-delete, and post-delete callback vectors.

- `mem_config_init()`, `memseg_alloc()`
  Initialize and allocate `struct memseg` objects.

## Add-Memory Flow

`kphysm_add_memory_dynamic()`:

1. Reserves the target span in the transit list.
2. Adds the full incoming span to `phys_install`.
3. Allocates `page_t` metadata either externally through weak `memseg_alloc_meta()` or from the incoming memory itself.
4. Handles KPM granularity and metadata sizing.
5. Maps metadata pages into kernel VA and probes accessibility.
6. Adds memnode range and adjusts page counters.
7. Adds usable pages to `phys_avail`.
8. Reuses or allocates a `memseg`, initializes page structures, remaps metadata if needed.
9. Inserts memseg into `memsegs`, updates KPM state, rebuilds PFN hash, updates `total_pages`.
10. Frees new pages to the VM system.
11. Updates global memory counters, dump size, page coalescing, callbacks, lgroup generation, and DDI.
12. Unreserves the span.

Rollback is handled by `kphysm_addmem_error_undospan()` plus local cleanup for metadata mappings, memnodes, page counters, and allocated metadata.

## Delete-Memory Flow

Delete is handle based:

1. `kphysm_del_gethandle()` creates a handle.
2. `kphysm_del_span()` adds one or more non-overlapping installed spans to the handle transit list, validates all relevant memsegs, and may split memsegs to isolate the delete range.
3. `kphysm_del_start()` records completion callback and starts `delete_memory_thread()`.
4. `delete_memory_thread()` reserves `availrmem`, runs registered pre-delete callbacks, allocates span bitmaps, starts AIO cleanup helper, and repeatedly scans target PFNs.
5. Pages are collected by:
   - removing free pages from free/cache lists,
   - accounting retired pages,
   - relocating locked/modified pages,
   - destroying clean pages,
   - forcing `VOP_PUTPAGE()` for dirty file-backed pages,
   - retrying after delays when no progress is made.
6. On cancellation, collected pages are freed back and `availrmem` is restored.
7. On success, `kphysm_del_cleanup()` removes memsegs, remaps metadata, updates memory lists/counters, dump size, and lgroup generation.
8. Post-delete callbacks run, state becomes `MHND_DONE`, and completion callback is invoked.

## Key Data Structures

- `struct mem_handle`
  Delete operation handle with mutex, external id, state, transit spans, counters, callback, cancel flags, worker thread id, and collected deleted-page list.

- `struct memdelspan`
  PFN span plus bitmaps for collected and retired pages.

- `struct transit_list` / `transit_list_head`
  Global list of active reserved/delete spans. Prevents overlap between add/delete operations and exposes active collection state.

- `struct memseg`
  Kernel memory segment descriptors. Dynamic memsegs may include metadata in the memory being managed or use external metadata.

- `memseg_va_avail`, `memseg_delete_junk`, `memseg_edit_junk`
  Lists for reusable dynamic memseg VA, deleted boot metadata, and obsolete split memsegs retained for concurrent readers.

## State Machine

`mhnd_state_t`:

- `MHND_FREE`
- `MHND_INIT`
- `MHND_STARTING`
- `MHND_RUNNING`
- `MHND_DONE`
- `MHND_RELEASE`

APIs enforce sequence. Release is refused while delete is starting/running; start is refused without spans or after completion.

## Locking and Synchronization

- `mem_handle_list_mutex` protects global handle list and handle id generation.
- Each `mem_handle` has `mh_mutex` for state, counters, cancellation, and worker coordination.
- `transit_list_head.trh_lock` protects span reservation and active collection visibility.
- `memsegs_lock()` protects global memseg list updates.
- `memseg_lists_lock` protects reusable/junk memseg side lists.
- `memlist_write_lock/read_lock` protects `phys_install` and `phys_avail`.
- `freemem_lock` protects `maxmem`, `physmem`, `availrmem`, and related counters.
- `mem_callback_rwlock` protects callback registry; pre-delete holds the reader lock until post-delete.
- Page deletion uses page locks, reclaim locks, group page locks, iolocks, vnode holds, HAT unload, and condition-variable wakeups for page waiters.
- CPU VM memseg caches are invalidated under `cpu_lock` with paused CPUs.

## Special Mechanisms

- Weak metadata provider hooks:
  `memseg_alloc_meta`, `memseg_free_meta`, `memseg_get_metapfn`, `memseg_remap_meta`.

- Dummy page metadata remapping:
  `memseg_remap_init()`, `remap_to_dummy()`, `memseg_remap_to_dummy()` create read-only dummy `page_t` backing for deleted metadata ranges so stale references do not point into removed memory.

- AIO cleanup helper:
  `dr_aio_cleanup_thread()` repeatedly invokes kaio cleanup for processes to break delete/kaio page-lock dependency cycles.

- Memseg split:
  `kphysm_split_memseg()` creates low/mid/high memseg replacements for partial deletes and leaves old memseg in edit junk for concurrent readers.

## External Dependencies

Memlists, memnodes, HAT/KPM, page relocation, page counters, kernel cage (`P_NORELOC`, `pfn_is_being_deleted()` interaction), DDI memory updates, dump subsystem, lgroup, pageout scanner, vnode putpage, kaio module, CPU pause/resume, and architecture-specific delete-span validation.

## Research Notes

This file is the dynamic memory hotplug/delete coordinator. Highest-risk areas are rollback after partial add failure, delete cancellation after collecting pages, stale memseg readers during split/delete, callback lock lifetime from pre-delete to post-delete, and ensuring no cage/nonrelocatable page enters a delete span after validation.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/os/mem_config.c -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/os/mem_config_stubs.c -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/os/mem_config_stubs.c

## Purpose

Provides stub definitions for memory cage and memory configuration interfaces on builds/platforms where the real implementation is absent or disabled.

The file comments note these should be in a platform stubs file.

## Main Responsibilities

- Define cage globals so references link without full cage support.
- Provide no-op or success-returning implementations for cage and kphysm setup APIs.
- Keep callers able to compile while making cage behavior effectively disabled.

## Data Provided

- `int kcage_on`
- `kthread_id_t kcage_cageout_thread`
- `pgcnt_t kcage_freemem`
- `pgcnt_t kcage_throttlefree`
- `pgcnt_t kcage_minfree`
- `pgcnt_t kcage_desfree`
- `pgcnt_t kcage_needfree`
- `pgcnt_t kcage_lotsfree = 1`

## Stubbed Functions

- `kphysm_setup_func_register(...)`
  Returns success on non-x86 or xPV builds covered by the preprocessor guard.

- `kphysm_setup_func_unregister(...)`
  No-op under the same guard.

- `kcage_create_throttle(pgcnt_t npages, int flags)`
  Returns `0`, meaning no cage throttling behavior is applied.

- `kcage_cageout_init(void)`
  No-op.

- `kcage_cageout_wakeup()`
  No-op.

- `kcage_tick()`
  No-op.

- `kcage_current_pfn(pfn_t *pfn)`
  Returns `0` without setting an active cage PFN.

## Locking and Side Effects

There is no locking and no meaningful state transition. These functions are compatibility shims only.

## External Dependencies

Includes page, memory configuration, and memory cage headers to match real interface types.

## Research Notes

Any code running with these stubs must not rely on actual cage reclaim, throttling, or kphysm callback behavior. The stubs are deliberately permissive and should be treated as platform/build compatibility, not functional memory DR support.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/os/mem_config_stubs.c -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/os/memlist_new.c -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/os/memlist_new.c

## Purpose

Implements allocation/free-list support and sorted span manipulation for `struct memlist` lists. These lists describe physical memory address ranges such as installed or available memory.

This file is a small foundational utility used by memory configuration code and boot/runtime memory-list management.

## Main Responsibilities

- Maintain a global freelist of reusable `struct memlist` nodes.
- Insert preallocated blocks of `struct memlist` nodes into the freelist.
- Insert existing nodes into sorted non-overlapping memory lists.
- Find the memlist element containing an address.
- Add spans with adjacency coalescing and overlap rejection.
- Delete spans with trimming, whole-node removal, or node splitting.

## Key Data

- `memlist_freelist`
  Singly linked list of free `struct memlist` nodes.

- `memlist_freelist_count`
  Count of free nodes.

- `memlist_freelist_mutex`
  Protects freelist and count.

## Key Functions

- `memlist_get_one(void)`
  Pops one node from the freelist. Caller must handle `NULL`.

- `memlist_free_one(struct memlist *mlp)`
  Pushes one node onto the freelist.

- `memlist_free_list(struct memlist *mlp)`
  Pushes an entire linked list of nodes onto the freelist and counts them.

- `memlist_free_block(caddr_t base, size_t bytes)`
  Treats a raw memory block as an array of `struct memlist` nodes and adds them all to the freelist.

- `memlist_insert(struct memlist *new, struct memlist **curmemlistp)`
  Inserts a caller-provided node into sorted order. Panics if the list is overlapping or malformed.

- `memlist_del(struct memlist *memlistp, struct memlist **curmemlistp)`
  Unlinks a specific node from a doubly linked memlist. Debug builds assert that the node is present.

- `memlist_find(struct memlist *mlp, uint64_t address)`
  Returns the node containing `address`, or `NULL`.

- `memlist_add_span(uint64_t address, uint64_t bytes, struct memlist **curmemlistp)`
  Allocates a node and adds a span. It coalesces with adjacent nodes, can concatenate two adjacent ranges, rejects overlaps with `MEML_SPANOP_ESPAN`, and returns `MEML_SPANOP_EALLOC` on node allocation failure.

- `memlist_delete_span(uint64_t address, uint64_t bytes, struct memlist **curmemlistp)`
  Deletes an existing span. It rejects missing/partially missing spans, trims from front/back, removes whole nodes, or splits a node when deleting from the middle.

## Return Codes

- `MEML_SPANOP_OK`
  Operation succeeded.

- `MEML_SPANOP_ESPAN`
  Add overlaps an existing span, or delete targets a span not fully present.

- `MEML_SPANOP_EALLOC`
  A new memlist node was needed but unavailable.

## Locking and Synchronization

Only the node freelist is internally locked. The actual memory lists passed by `curmemlistp` are not globally locked here; callers must hold the appropriate memlist lock, such as `memlist_write_lock()`, when manipulating shared lists.

## Invariants

- Managed memory lists are sorted by `ml_address`.
- Managed memory lists are non-overlapping.
- Adjacent spans are coalesced by `memlist_add_span()`.
- Doubly linked `ml_prev`/`ml_next` pointers are maintained for active lists.
- Free-list linkage uses `ml_next`; other fields may retain old values until reused.

## External Dependencies

Used by physical memory configuration code for `phys_install`, `phys_avail`, and related span bookkeeping.

## Research Notes

The subtle point is allocation ownership: `memlist_add_span()` allocates its own node from the freelist, while `memlist_insert()` inserts a supplied node. Callers must distinguish these APIs and must provide external locking for shared active lists.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/os/memlist_new.c -->