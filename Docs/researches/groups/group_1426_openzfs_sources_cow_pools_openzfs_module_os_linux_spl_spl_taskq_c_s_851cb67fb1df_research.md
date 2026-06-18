# Group Research: group_1426_openzfs_sources_cow_pools_openzfs_module_os_linux_spl_spl_taskq_c_s_851cb67fb1df

Scope: `Docs/research_subset_a.md`  
Repository: `/home/sansha/Github/learn_fs`  
All listed source files were read completely.

<!-- BEGIN FILE RESEARCH: sources/cow-pools/openzfs/module/os/linux/spl/spl-taskq.c -->
# File Research: sources/cow-pools/openzfs/module/os/linux/spl/spl-taskq.c

## Purpose

Implements the Linux SPL task queue subsystem, providing Solaris-style `taskq_*` APIs on top of Linux kthreads, wait queues, timers, spinlocks, CPU hotplug callbacks, and kstats. It exports global task queues used across OpenZFS and supports fixed, dynamic, delayed, priority, preallocated, and CPU-percentage-sized task queues.

## Major State

- `system_taskq`: global dynamic task queue for normal short work.
- `system_delay_taskq`: global dynamic queue for delayed work.
- `dynamic_taskq`: private queue used to create additional dynamic taskq worker threads without recursing into `system_taskq`.
- `tq_list` plus `tq_list_sem`: global registry of all task queues for kstats and kick handling.
- `taskq_tsd`: TSD key storing the current thread’s taskq membership.
- `spl_taskq_cpuhp_state`: CPU hotplug multi-state used for `TASKQ_THREADS_CPU_PCT`.

Module parameters:
- `spl_taskq_thread_bind`: optionally binds taskq threads to CPUs.
- `spl_taskq_thread_timeout_ms`: idle timeout pacing for dynamic thread exit.
- `spl_taskq_thread_dynamic`: enables dynamic taskq thread behavior.
- `spl_taskq_thread_priority`: enables setting worker nice levels from taskq priority.
- `spl_taskq_thread_sequential`: threshold of sequential tasks before trying to spawn more workers.
- `spl_taskq_kick`: write-only style trigger that scans taskqs for old pending work and tries to spawn more threads.

## Core Data Flow

Task dispatch allocates or reuses a `taskq_ent_t`, assigns a monotonically increasing `tqent_id`, links it to one of the task lists, wakes workers, and may request a dynamic worker spawn. The queue maintains separate ordered lists for:

- `tq_pend_list`: normal pending tasks.
- `tq_prio_list`: front/priority tasks and expired delayed tasks.
- `tq_delay_list`: timer-backed delayed tasks.
- `tq_active_list`: tasks currently executing on worker threads.
- `tq_free_list`: reusable task entries.

`taskq_lowest_id()` computes the lowest incomplete task ID across pending, priority, delay, and active state. `taskq_wait_id()`, `taskq_wait_outstanding()`, and `taskq_wait()` all build on that monotonic ID accounting.

## Important Functions

- `task_alloc()` / `task_free()` / `task_done()`: manage task entry reuse, allocation throttling, and free-list retention.
- `task_expire()` / `task_expire_impl()`: timer callback path for delayed tasks; moves them from delay list to priority list.
- `taskq_find()` and `taskq_find_list()`: locate dispatched tasks in queued or active state.
- `taskq_cancel_id()`: cancels pending or delayed tasks, optionally waits for active tasks, and uses `timer_delete_sync()` unconditionally to close a delayed-task expiry race.
- `taskq_dispatch()`: normal dispatch, honoring `TQ_NOQUEUE`, `TQ_FRONT`, allocation flags, and dynamic spawning.
- `taskq_dispatch_delay()`: delayed dispatch using Linux timers.
- `taskq_dispatch_ent()`: dispatches caller-provided preallocated entries.
- `taskq_thread()`: worker main loop; blocks signals, records TSD taskq membership, pulls priority before pending work, updates active lists, executes functions, updates lowest task ID, and exits if dynamic idle-stop rules allow.
- `taskq_thread_create()` / `taskq_thread_spawn()`: create workers directly or through `dynamic_taskq`.
- `taskq_create()` / `taskq_destroy()` / `taskq_create_synced()`: lifecycle and optional synchronized worker capture.
- `spl_taskq_expand()` / `spl_taskq_prepare_down()`: CPU hotplug callbacks for queues sized by CPU percentage.
- `spl_taskq_init()` / `spl_taskq_fini()`: module-level setup and teardown.

## Kstats

Per-taskq kstats expose static values, gauges, and counters including thread counts, pending/priority/delayed task counts, dispatch/execution counts, cancellation counts, wakeups, sleeps, and free entries. A raw `taskq/summary` kstat prints a compact all-taskq table.

## Concurrency And Correctness Notes

- `tq_lock` protects taskq lists, counts, and active state.
- `tq_lock_class` distinguishes general queues from `dynamic_taskq` to avoid lockdep false positives during nested dispatch.
- Task lists are kept in task-ID order where needed so wait semantics can be implemented cheaply.
- Preallocated entries are duplicated on worker execution because their original storage may be reused or freed by the task function.
- Delayed cancellation deliberately avoids relying on `timer_pending()` because an expired timer can be dequeued before its callback runs.
- `taskq_destroy()` first clears `TASKQ_ACTIVE`, waits for outstanding dynamic-spawn work, drains tasks, stops workers, frees cached entries, and asserts all lists/counts are empty.
<!-- END FILE RESEARCH: sources/cow-pools/openzfs/module/os/linux/spl/spl-taskq.c -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/openzfs/module/os/linux/spl/spl-thread.c -->
# File Research: sources/cow-pools/openzfs/module/os/linux/spl/spl-thread.c

## Purpose

Implements SPL thread compatibility APIs over Linux kthreads. It supplies Solaris-style `thread_create()` behavior, an OpenZFS-specific resilient kthread creation wrapper, signal handling compatibility, and a reclaim-thread predicate.

## Key Components

- `thread_priv_t`: temporary launch structure carrying function, argument, name, start state, priority, and magic validation.
- `thread_generic_wrapper()`: unwraps `thread_priv_t`, applies task state and priority, frees launch metadata, then calls the requested function.
- `__thread_create()`: allocates launch metadata, strips a trailing `_thread` substring from the generated name, creates a Linux kthread with `spl_kthread_create()`, wakes it, and returns the task pointer.
- `spl_kthread_create()`: repeatedly calls `kthread_create()` and retries on pending signals or `-ENOMEM`, approximating older non-killable creation semantics.
- `issig()`: Solaris-like pending-signal check that handles Linux `dequeue_signal()` API variants, stop signals, and pending status.
- `current_is_reclaim_thread()`: returns whether the current task is `kswapd`.

## Exports

- `__thread_create`
- `spl_kthread_create`
- `issig`
- `current_is_reclaim_thread`

## Notes

`__thread_create()` ignores the Solaris `proc_t *pp` argument and does not support caller-provided stacks. The file intentionally favors blocking/retry behavior because many Solaris-style callers do not expect thread creation failure.
<!-- END FILE RESEARCH: sources/cow-pools/openzfs/module/os/linux/spl/spl-thread.c -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/openzfs/module/os/linux/spl/spl-trace.c -->
# File Research: sources/cow-pools/openzfs/module/os/linux/spl/spl-trace.c

## Purpose

Defines SPL tracepoints exactly once for Linux builds.

## Contents

The file includes `sys/taskq.h`, defines `CREATE_TRACE_POINTS`, then includes:

- `sys/trace.h`
- `sys/trace_taskq.h`

## Notes

There is no runtime logic. Its role is build/link ownership for DTrace-style tracepoint definitions used by SPL taskq instrumentation.
<!-- END FILE RESEARCH: sources/cow-pools/openzfs/module/os/linux/spl/spl-trace.c -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/openzfs/module/os/linux/spl/spl-tsd.c -->
# File Research: sources/cow-pools/openzfs/module/os/linux/spl/spl-tsd.c

## Purpose

Implements Solaris-style thread-specific data for Linux without modifying `task_struct`. It uses a global hash table keyed by `(tsd key, pid)` and supports per-key destructors, per-thread cleanup, and lookup by current or specified thread.

## Main Structures

- `tsd_hash_table_t`: global table with table lock, key allocator, hash size, and bins.
- `tsd_hash_bin_t`: per-bin spinlock plus hlist.
- `tsd_hash_entry_t`: one hash object, used for actual TSD values and for anchor entries.
- Key anchor: entry with `he_pid == DTOR_PID`, holding destructor and list of values for that key.
- PID anchor: entry with `he_key == PID_KEY`, holding list of values for that thread.

## Important Functions

- `tsd_hash_search()`: lookup by key and pid, locking only the computed bin.
- `tsd_hash_add_key()`: allocates a new nonzero TSD key and creates its destructor anchor.
- `tsd_hash_add_pid()`: creates a PID anchor on first use by a thread.
- `tsd_hash_add()`: creates a real TSD entry, linking it into the hash bin, key-anchor list, and pid-anchor list.
- `tsd_remove_entry()`: removes one value entry and prunes the PID anchor when empty.
- `tsd_hash_table_init()` / `tsd_hash_table_fini()`: allocate/free the fixed-size table and run destructors on remaining entries.
- `tsd_set()`: update, add, or remove current-thread value for a key.
- `tsd_get()`: get current-thread value.
- `tsd_get_by_thread()`: get value for a specific `kthread_t`.
- `tsd_create()`: create a key with optional destructor.
- `tsd_destroy()`: remove a key and all values using it.
- `tsd_exit()`: remove all TSD for the current thread.
- `spl_tsd_init()` / `spl_tsd_fini()`: module lifecycle.

## Concurrency Notes

Fast lookup locks only one hash bin. Operations that need to connect or tear down key/pid anchor relationships take the table lock and then bin locks. Destructors run after entries are removed from shared structures by moving removed entries to a local work list.
<!-- END FILE RESEARCH: sources/cow-pools/openzfs/module/os/linux/spl/spl-tsd.c -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/openzfs/module/os/linux/spl/spl-vmem.c -->
# File Research: sources/cow-pools/openzfs/module/os/linux/spl/spl-vmem.c

## Purpose

Provides public SPL `vmem_*` allocation wrappers backed by the SPL kmem implementation.

## Functions

- `spl_vmem_alloc(size, flags, func, line)`: validates public kmem flags, adds `KM_VMEM`, then dispatches to normal, debug, or tracking allocation implementation depending on build configuration.
- `spl_vmem_zalloc(size, flags, func, line)`: same as allocation, adding `KM_ZERO`.
- `spl_vmem_free(buf, size)`: frees through normal, debug, or tracking implementation.
- `spl_vmem_init()` / `spl_vmem_fini()`: no-op lifecycle hooks.

## Exports

- `spl_vmem_alloc`
- `spl_vmem_zalloc`
- `spl_vmem_free`

## Notes

This file is a thin compatibility layer. The real allocation behavior lives in the SPL kmem allocator selected by build flags such as `DEBUG_KMEM` and `DEBUG_KMEM_TRACKING`.
<!-- END FILE RESEARCH: sources/cow-pools/openzfs/module/os/linux/spl/spl-vmem.c -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/openzfs/module/os/linux/spl/spl-xdr.c -->
# File Research: sources/cow-pools/openzfs/module/os/linux/spl/spl-xdr.c

## Purpose

Implements an in-memory XDR encoder/decoder used by libnvpair and ZFS metadata serialization. It serializes primitive values, opaque bytes, strings, and arrays into a portable big-endian representation.

## Main Entry Point

- `xdrmem_create(XDR *xdrs, caddr_t addr, uint_t size, enum xdr_op op)`: initializes an XDR stream over a caller-provided memory buffer for encode or decode and rejects invalid operations or pointer wraparound.

## Encoding/Decoding Behavior

- Uses 4-byte XDR alignment.
- Encodes integers in big-endian order.
- Pads opaque data with zero bytes.
- Rejects nonzero padding on decode.
- Rejects decoded strings containing embedded NUL bytes.
- Validates decoded char and ushort range.
- Bounds-checks buffer availability before advancing.
- Can allocate arrays or strings during decode when caller passes a null pointer.

## Important Functions

- `xdrmem_control()`: implements `XDR_GET_BYTES_AVAIL`.
- `xdrmem_enc_bytes()` / `xdrmem_dec_bytes()`: opaque byte operations with padding handling.
- `xdrmem_enc_uint32()` / `xdrmem_dec_uint32()`: endian primitive operations.
- `xdrmem_enc_char()` / `xdrmem_dec_char()`
- `xdrmem_enc_ushort()` / `xdrmem_dec_ushort()`
- `xdrmem_enc_uint()` / `xdrmem_dec_uint()`
- `xdrmem_enc_ulonglong()` / `xdrmem_dec_ulonglong()`
- `xdr_enc_array()` / `xdr_dec_array()`
- `xdr_enc_string()` / `xdr_dec_string()`

## Ops Tables

- `xdrmem_encode_ops`
- `xdrmem_decode_ops`

## Notes

The implementation documents strict ABI assumptions: 8-bit chars, 32-bit unsigned ints, 64-bit unsigned long longs, two’s-complement negative integers, suitable alignment, and kernel memory buffers only.
<!-- END FILE RESEARCH: sources/cow-pools/openzfs/module/os/linux/spl/spl-xdr.c -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/openzfs/module/os/linux/spl/spl-zlib.c -->
# File Research: sources/cow-pools/openzfs/module/os/linux/spl/spl-zlib.c

## Purpose

Provides SPL zlib compression and decompression wrappers using the Linux kernel zlib API and a reusable workspace kmem cache.

## Main State

- `zlib_workspace_cache`: cache for deflate/inflate workspaces, avoiding repeated vmalloc/vfree behavior.

## Functions

- `zlib_workspace_alloc()` / `zlib_workspace_free()`: allocate/free cached workspaces, clearing `__GFP_FS` from allocation flags.
- `z_compress_level(dest, destLen, source, sourceLen, level)`: compresses a buffer using `zlib_deflateInit`, `zlib_deflate(..., Z_FINISH)`, and `zlib_deflateEnd`.
- `z_uncompress(dest, destLen, source, sourceLen)`: decompresses a buffer using inflate APIs and maps some stream failures to `Z_DATA_ERROR`.
- `spl_zlib_init()`: creates `spl_zlib_workspace_cache` sized to the max deflate/inflate workspace requirement.
- `spl_zlib_fini()`: destroys the workspace cache.

## Exports

- `z_compress_level`
- `z_uncompress`

## Notes

The functions are adapted from zlib’s `compress2()` / `uncompress()` semantics but wired to kernel zlib and SPL allocation. Destination sizes are checked for truncation to zlib’s `uInt`.
<!-- END FILE RESEARCH: sources/cow-pools/openzfs/module/os/linux/spl/spl-zlib.c -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/openzfs/module/os/linux/spl/spl-zone.c -->
# File Research: sources/cow-pools/openzfs/module/os/linux/spl/spl-zone.c

## Purpose

Implements Linux user-namespace-backed equivalents of Solaris zone dataset visibility and delegation. It supports namespace-specific dataset delegation and UID-owned dataset delegation for rootless container use.

## Main State

- `zone_datasets_lock`: protects all delegation lists.
- `zone_datasets`: list of user-namespace-specific delegations.
- `zone_uid_datasets`: list of UID-owned delegations.
- `zone_get_zoned_uid_fn`: callback registered by ZFS to resolve the `zoned_uid` property and delegation root.

## Data Structures

- `zone_datasets_t`: namespace reference plus datasets delegated to that namespace.
- `zone_dataset_t`: variable-length dataset name node.
- `zone_uid_datasets_t`: owner UID plus datasets delegated to that UID.

## Namespace Handling

When `CONFIG_USER_NS` is enabled, `user_ns_get()` validates a file descriptor as an nsfs user namespace file, extracts its `struct user_namespace`, and returns errors that let higher layers distinguish invalid namespace references. Namespace zone IDs are derived from `user_ns->ns.inum`.

Without user namespace support, attach/detach APIs return `ENXIO`, and global-zone checks treat all callers as global.

## Delegation APIs

- `zone_dataset_attach()`: root-only attach of dataset to a user namespace.
- `zone_dataset_attach_uid()`: root-only attach of dataset to an owning UID.
- `zone_dataset_detach()`: remove namespace delegation and release namespace ref when empty.
- `zone_dataset_detach_uid()`: remove UID delegation and prune empty UID entry.
- `zone_register_zoned_uid_callback()` / `zone_unregister_zoned_uid_callback()`: ZFS property callback lifecycle.

## Authorization And Visibility

- `zone_dataset_admin_check()`: authorizes operations under `zoned_uid` delegation. It checks non-global zone status, callback availability, delegation root, namespace owner UID, operation-specific capability, and extra constraints for destroy, rename, and clone.
- `zone_dataset_visible()`: checks if a dataset should be visible/writable to the current zone. Global zone gets full write visibility. Non-global callers are checked first against namespace delegation and then UID delegation.
- `zone_dataset_check_list()`: implements parent/root/child matching. Parents are visible read-only; delegated roots and descendants are writable.

## Utility APIs

- `global_zoneid()`
- `crgetzoneid()`
- `inglobalzone()`
- `spl_zone_init()`
- `spl_zone_fini()`

## Notes

Dataset names are rejected if empty or beginning with `/`; a trailing slash is ignored. Namespace delegation holds a namespace reference to avoid namespace ID reuse while delegation is active.
<!-- END FILE RESEARCH: sources/cow-pools/openzfs/module/os/linux/spl/spl-zone.c -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/openzfs/module/os/linux/zfs/abd_os.c -->
# File Research: sources/cow-pools/openzfs/module/os/linux/zfs/abd_os.c

## Purpose

Linux-specific ABD implementation. It backs ARC buffered data with either linear kernel buffers or scatterlists of Linux pages, supporting highmem, compound pages, direct-I/O user pages, BIO mapping, zero scatter buffers, and ABD kstats.

## Main Concepts

- Linear ABDs behave like normal contiguous virtual buffers.
- Scatter ABDs use physical pages in a Linux scatterlist and map chunks only during access.
- On non-highmem systems, a one-entry scatter ABD can be represented as a linear page-backed ABD for faster cached reads.
- ABDs created from user pages are marked with `ABD_FLAG_FROM_PAGES` and are handled carefully because user memory cannot be write-protected by ABD code.

## Main State

- `abd_stats`: named kstats template.
- `abd_sums`: writable sums backing stats.
- `zfs_abd_scatter_min_size`: minimum size for scatter allocation.
- `zfs_abd_scatter_max_order`: maximum compound-page order for scatter ABD allocation.
- `abd_zero_scatter`: SPA_MAXBLOCKSIZE scatter ABD backed by one zero page.
- `abd_zero_page`: shared zero page or allocated substitute.
- `abd_cache`: cache for `abd_t`.
- `abd_ksp`: abdstats kstat.

## Allocation

- `abd_alloc_struct_impl()` / `abd_free_struct_impl()`: allocate/free `abd_t` from cache and update struct-size stats.
- `abd_alloc_chunks()`: allocates pages for scatter ABDs.
  - Non-highmem path prefers high-order compound pages, tries to stay within a NUMA zone, and degrades allocation order on failure.
  - Highmem path allocates individual pages for maximum compatibility.
- `abd_free_chunks()`: unmarks and frees pages unless ABD is from caller-provided pages, then frees the scatter table.
- `abd_alloc_zero_scatter()` / `abd_free_zero_scatter()`: create and destroy shared zero-filled scatter ABD.
- `abd_size_alloc_linear()`: chooses linear allocation for small sizes or when scatter is disabled.
- `abd_alloc_from_pages()`: constructs an ABD over caller-provided pinned pages, representing single-page mappings as linear when possible.
- `abd_alloc_for_io()`: currently delegates to `abd_alloc()`.

## Stats And Initialization

- Tracks struct memory, linear count/bytes, scatter count/bytes, scatter chunk waste, allocation order distribution, multi-chunk/multi-zone ABDs, page allocation retries, and sg table retries.
- `abd_init()` creates the ABD cache, initializes sums, installs `zfs/abdstats`, and creates zero scatter.
- `abd_fini()` tears down zero scatter, kstats, sums, and cache.

## Iteration And Mapping

- `abd_iter_init()`: initializes an iterator for linear or scatter ABDs.
- `abd_iter_at_end()`: checks completion.
- `abd_iter_advance()`: advances through linear offset or scatterlist entries.
- `abd_iter_map()` / `abd_iter_unmap()`: maps the current chunk into kernel address space, using local kmap for scatter pages.
- `abd_iter_page()`: yields page pointer, data offset, and data length without mapping. It handles compound tail pages by moving to the compound head and expanding the yielded segment when possible.

## Buffer Borrowing

- `abd_borrow_buf()`: returns direct linear storage when safe, otherwise allocates a temporary zio buffer.
- `abd_borrow_buf_copy()`: borrows and copies ABD contents when needed.
- `abd_return_buf()`: validates or frees borrowed buffers, with special handling for gang ABDs and user-page ABDs.
- `abd_return_buf_copy()`: copies modified data back before returning the temporary buffer.

## BIO Mapping

- `abd_nr_pages_off()`: counts pages needed for a range, including gang ABD recursion.
- `bio_map()`: maps a linear virtual range into a BIO.
- `abd_gang_bio_map_off()`: maps gang ABD ranges across children.
- `abd_bio_map_off()`: maps linear, gang, or scatter ABD ranges into a Linux BIO.

## Tunables And Export

- Exports `abd_alloc_from_pages`.
- Module parameters:
  - `zfs_abd_scatter_enabled`
  - `zfs_abd_scatter_min_size`
  - `zfs_abd_scatter_max_order`

## Correctness Notes

Pages may be marked private on 64-bit builds so ZFS data pages can be excluded from crash dumps. Scatter allocation loops intentionally retry with sleeps when page or sg table allocation fails. Direct-I/O user page ABDs are not trusted to remain stable, so temporary buffers and checksum verification are used to catch concurrent user modifications.
<!-- END FILE RESEARCH: sources/cow-pools/openzfs/module/os/linux/zfs/abd_os.c -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/openzfs/module/os/linux/zfs/arc_os.c -->
# File Research: sources/cow-pools/openzfs/module/os/linux/zfs/arc_os.c

## Purpose

Linux-specific ARC memory integration. It computes ARC memory limits, plugs ARC eviction into the Linux shrinker, handles memory pressure throttling, updates tuning when module parameters change, and reacts to memory hotplug.

## Memory Sizing

- `arc_default_max(min, allmem)`: default ARC max is based on total memory, keeping at least 1 GiB outside ARC on larger systems while enforcing a 5/8 total-memory style cap.
- `arc_all_memory()`: total usable memory, excluding highmem when configured.
- `arc_free_memory()`: free memory estimate, using free plus inactive file pages on normal builds.
- `arc_available_memory()`: free memory minus `arc_sys_free`.
- `arc_set_sys_free()`: computes system reserve from Linux watermark logic, boosts it, and adds a fraction of total memory.

## Shrinker Integration

- `arc_evictable_memory()`: estimates ARC bytes that can be evicted, accounting for clean/dirty ARC and page-cache proportional minimums.
- `arc_shrinker_count()`: reports reclaimable pages and honors `zfs_arc_shrinker_limit` for kswapd.
- `arc_shrinker_scan()`: marks ARC warm, pauses growth, reduces ARC target, waits for eviction when safe under `__GFP_FS`, updates reclaim accounting, and bumps direct/indirect memory-pressure stats.
- `arc_lowmem_init()` / `arc_lowmem_fini()`: register/unregister `zfs-arc-shrinker`.

## Throttling

- `arc_memory_throttle(spa, reserve, txg)`: throttles transaction work under low memory. It distinguishes kswapd/pageout context from normal context, using `spa_lowmem_page_load`, `arc_reclaim_needed()`, and returns `ERESTART` or `EAGAIN` when pressure is high.

## Parameter Hooks

- `param_set_arc_u64()`
- `param_set_arc_min()`
- `param_set_arc_max()`
- `param_set_arc_int()`
- `param_set_arc_no_grow_shift()`
- `param_set_l2arc_dwpd_limit()`

These parse module parameter changes and call ARC retuning or L2ARC DWPD reset behavior where needed.

## Memory Hotplug

With `CONFIG_MEMORY_HOTPLUG`:
- `arc_hotplug_callback()` responds to `MEM_ONLINE`, recomputes ARC limits, dirty-data maximum, and `arc_sys_free`.
- `arc_register_hotplug()` / `arc_unregister_hotplug()` manage the notifier.

## Module Parameters

- `zfs_arc_shrinker_limit`: pages reclaimable at once through shrinker.
- `zfs_arc_shrinker_seeks`: relative ARC eviction cost for shrinker policy.
<!-- END FILE RESEARCH: sources/cow-pools/openzfs/module/os/linux/zfs/arc_os.c -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/openzfs/module/os/linux/zfs/kasan_compat.c -->
# File Research: sources/cow-pools/openzfs/module/os/linux/zfs/kasan_compat.c

## Purpose

Provides a compatibility workaround for kernels where `kasan_enabled()` depends on a GPL-only symbol.

## Behavior

When `HAVE_KASAN_ENABLED_GPL_ONLY` is defined, the file defines:

- `struct static_key_false kasan_flag_enabled = STATIC_KEY_FALSE_INIT;`

This satisfies references from header-based kernel code without linking against the GPL-only kernel symbol.

## Notes

The workaround effectively makes OpenZFS code see KASAN as disabled for the affected symbol path, avoiding build/link failures caused by inaccessible kernel internals.
<!-- END FILE RESEARCH: sources/cow-pools/openzfs/module/os/linux/zfs/kasan_compat.c -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/openzfs/module/os/linux/zfs/mmp_os.c -->
# File Research: sources/cow-pools/openzfs/module/os/linux/zfs/mmp_os.c

## Purpose

Linux-specific MMP parameter hook.

## Function

- `param_set_multihost_interval(val, kp)`: parses a `uint64_t` module parameter via `spl_param_set_u64()`. If pools have been initialized (`spa_mode_global != SPA_MODE_UNINIT`), it calls `mmp_signal_all_threads()` so MMP worker threads react promptly to interval changes.

## Notes

This file contains only the OS-specific parameter callback; core MMP logic is elsewhere.
<!-- END FILE RESEARCH: sources/cow-pools/openzfs/module/os/linux/zfs/mmp_os.c -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/openzfs/module/os/linux/zfs/policy.c -->
# File Research: sources/cow-pools/openzfs/module/os/linux/zfs/policy.c

## Purpose

Maps illumos/ZFS security policy checks to Linux credentials, capabilities, user namespaces, UID/GID mappings, and VFS behavior. Many checks are no-ops because Linux VFS already enforces the corresponding rule.

## Core Helpers

- `priv_policy_ns(cr, capability, err, ns)`: checks a Linux capability, temporarily overriding current credentials when the supplied credentials differ from current and `kcred`.
- `priv_policy(cr, capability, err)`: capability check in `cr->user_ns`.
- `priv_policy_user(cr, capability, err)`: user-namespace-aware capability check intended after UID/GID mapping validation.

## Implemented Policy Checks

- `secpolicy_nfs()`: `CAP_SYS_ADMIN`.
- `secpolicy_sys_config()`: `CAP_SYS_ADMIN`.
- `secpolicy_vnode_any_access()`: owner, inode-owner/capable, UID mapping, `CAP_DAC_OVERRIDE`, or `CAP_DAC_READ_SEARCH`.
- `secpolicy_vnode_chown()`: owner or `CAP_FOWNER`, with UID mapping check.
- `secpolicy_vnode_create_gid()`: `CAP_SETGID`.
- `secpolicy_vnode_remove()`: `CAP_FOWNER`.
- `secpolicy_vnode_setdac()`: owner or `CAP_FOWNER`, with UID mapping check.
- `secpolicy_vnode_setid_retain()`: `CAP_FSETID`.
- `secpolicy_vnode_setids_setgids()`: translated GID ownership/group membership or `CAP_FSETID`.
- `secpolicy_zinject()`: `CAP_SYS_ADMIN`, returning `EACCES` on denial.
- `secpolicy_zfs()`: `CAP_SYS_ADMIN`, returning `EACCES` on denial.
- `secpolicy_setid_clear()`: clears setuid/setgid bits when caller lacks retain privilege.
- `secpolicy_setid_setsticky_clear()`: validates setuid and setgid changes and clears sticky/setgid bits as needed.
- `secpolicy_xvattr()`: delegates to chown policy.

## Linux-VFS-Enforced No-Ops

These return success because Linux VFS handles them elsewhere:

- `secpolicy_vnode_access2()`
- `secpolicy_vnode_setattr()`
- `secpolicy_basic_link()`
- Sticky-bit modification helper returns success.

## Notes

The file is heavily user-namespace aware. It avoids namespace capability checks when UID/GID mapping cannot be established.
<!-- END FILE RESEARCH: sources/cow-pools/openzfs/module/os/linux/zfs/policy.c -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/openzfs/module/os/linux/zfs/qat.c -->
# File Research: sources/cow-pools/openzfs/module/os/linux/zfs/qat.c

## Purpose

Top-level Intel QAT integration for OpenZFS when built with `_KERNEL` and `HAVE_QAT`.

## Main State

- `qat_stats`: kstat-named counters for compression, decompression, encryption, decryption, checksum requests, byte totals, and failure counts.
- `qat_ksp`: installed `zfs/qat` kstat.

## Functions

- `qat_mem_alloc_contig(pp, size)`: QAT-compatible contiguous allocation wrapper using `kmalloc`.
- `qat_mem_free_contig(pp)`: frees and nulls contiguous allocation.
- `qat_init()`: creates QAT kstat, initializes compression and crypto/checksum QAT subsystems, and sets disable flags when initialization fails.
- `qat_fini()`: deletes kstat and finalizes crypto/checksum and compression subsystems.

## Notes

Initialization does not fail module loading. If QAT setup fails, it sets runtime disable parameters so QAT can potentially be re-enabled later through sysfs/module parameters.
<!-- END FILE RESEARCH: sources/cow-pools/openzfs/module/os/linux/zfs/qat.c -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/openzfs/module/os/linux/zfs/qat_compress.c -->
# File Research: sources/cow-pools/openzfs/module/os/linux/zfs/qat_compress.c

## Purpose

Implements Intel QAT accelerated compression and decompression for ZFS buffers.

## Main State

- `dc_inst_handles`: QAT data-compression instance handles.
- `session_handles`: one compression session per instance.
- `buffer_array`: intermediate buffers required by QAT.
- `num_inst`: active instance count.
- `inst_num`: round-robin counter.
- `qat_dc_init_done`: initialization flag.
- `zfs_qat_compress_disable`: module parameter controlling use.

## Eligibility

- `qat_dc_use_accel(s_len)`: true only when compression is enabled, initialized, and buffer size is within QAT min/max bounds.

## Initialization And Cleanup

- `qat_dc_init()`: discovers QAT compression instances, caps them to `QAT_DC_MAX_INSTANCES`, sets address translation, allocates metadata/intermediate buffers, starts instances, creates DEFLATE/Adler32 stateless sessions, and marks initialization complete.
- `qat_dc_clean()`: stops instances, frees sessions and intermediate buffers, resets state.
- `qat_dc_fini()`: calls cleanup if initialized.
- `qat_dc_callback()`: completion callback for async QAT requests.

## Compression Path

- `qat_compress_impl()`: common implementation for compression and decompression.
  - Builds QAT source and destination `CpaBufferList` objects over page-mapped source, destination, and optional scratch buffers.
  - For compression:
    - Generates zlib header.
    - Submits `cpaDcCompressData`.
    - Waits for completion.
    - Checks output fits destination.
    - Writes Adler32 footer.
    - Returns compressed length.
  - For decompression:
    - Skips zlib header in source.
    - Submits `cpaDcDecompressData`.
    - Waits for completion.
    - Verifies Adler32 checksum.
    - Returns decompressed length.
  - Cleans up page mappings, metadata, and buffer lists on all paths.

- `qat_compress()`: public entry point. Allocates an additional destination-sized scratch buffer during compression so incompressible data does not cause QAT buffer-overflow warnings.

## Parameter Hook

- `param_set_qat_compress()`: changing disable flag to `0` attempts QAT DC initialization; on failure it restores disabled state.

## Notes

The implementation tracks kstats for request counts, byte totals, and failures. `CPA_STATUS_INCOMPRESSIBLE` is treated separately from hard failures.
<!-- END FILE RESEARCH: sources/cow-pools/openzfs/module/os/linux/zfs/qat_compress.c -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/openzfs/module/os/linux/zfs/qat_crypt.c -->
# File Research: sources/cow-pools/openzfs/module/os/linux/zfs/qat_crypt.c

## Purpose

Implements Intel QAT acceleration for ZFS encryption/decryption and checksumming. QAT cryptographic instances serve both operations, so they share initialization and instance selection.

## Main State

- `cy_inst_handles`: QAT crypto instance handles.
- `num_inst`: active crypto instance count.
- `inst_num`: round-robin instance counter.
- `qat_cy_init_done`: initialization flag.
- `zfs_qat_encrypt_disable`: encryption/decryption disable parameter.
- `zfs_qat_checksum_disable`: checksum disable parameter.

## Eligibility

- `qat_crypt_use_accel(s_len)`: encryption enabled, initialized, and size within QAT bounds.
- `qat_checksum_use_accel(s_len)`: checksum enabled, initialized, and size within QAT bounds.

## Initialization And Cleanup

- `qat_cy_init()`: discovers crypto instances, caps to `QAT_CRYPT_MAX_INSTANCES`, sets address translation, starts instances, and marks initialized.
- `qat_cy_clean()`: stops instances and resets state.
- `qat_cy_fini()`: cleans if initialized.
- `symcallback()`: records QAT verification result and completes the waiting thread.

## Session Setup

- `qat_init_crypt_session_ctx()`: creates AES-GCM session context for encrypt/decrypt. CCM is explicitly unsupported and returns failure without counting as a GCM failure.
- `qat_init_checksum_session_ctx()`: creates a SHA256 hash session context. ZFS SHA512/256 is not supported by QAT and is rejected.
- `qat_init_cy_buffer_lists()`: allocates QAT private metadata for source and destination buffer lists.

## Encryption/Decryption

- `qat_crypt()`: maps source and destination buffers page-by-page, allocates session and operation metadata, copies IV/AAD/digest as needed, submits `cpaCySymPerformOp`, waits for completion, validates callback result, copies produced digest on encryption, updates kstats, unmaps pages, removes session, and frees allocations.

## Checksumming

- `qat_checksum()`: maps input pages, creates checksum session, allocates digest buffer, submits QAT hash operation, waits for completion, copies digest into `zio_cksum_t`, updates kstats, and cleans resources.

## Parameter Hooks

- `param_set_qat_encrypt()`: enabling attempts crypto initialization.
- `param_set_qat_checksum()`: enabling attempts crypto initialization.
- Module parameters expose encryption and checksum disable flags.

## Notes

The file uses fixed arrays sized for up to 48 QAT crypto instances and `MAX_PAGE_NUM` stack arrays for mapped pages. Unsupported algorithms are returned as failures to the caller but not always counted as QAT operational failures.
<!-- END FILE RESEARCH: sources/cow-pools/openzfs/module/os/linux/zfs/qat_crypt.c -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/openzfs/module/os/linux/zfs/spa_misc_os.c -->
# File Research: sources/cow-pools/openzfs/module/os/linux/zfs/spa_misc_os.c

## Purpose

Linux-specific SPA miscellaneous hooks: module parameter parsing, history zone label, and restoration/cleanup of UID-based dataset zoning on pool import/export.

## Parameter Hooks

- `param_set_deadman_failmode()`: validates via common deadman failmode parser, then stores char pointer.
- `param_set_deadman_ziotime()`: parses milliseconds and updates deadman ZIO time in nanoseconds.
- `param_set_deadman_synctime()`: parses milliseconds and updates deadman sync time in nanoseconds.
- `param_set_slop_shift()`: parses integer, accepts only values 1 through 31, then stores parameter.
- `param_set_active_allocator()`: validates allocator name through common parser, then stores char pointer.

## OS Hooks

- `spa_history_zone()`: returns `"linux"` for history records.
- `spa_import_os(spa)`: walks datasets in imported pool and restores nonzero `zoned_uid` properties by calling `zone_dataset_attach_uid(kcred, ...)`.
- `spa_export_os(spa)`: walks datasets and detaches nonzero `zoned_uid` delegations with `zone_dataset_detach_uid(kcred, ...)`.
- `spa_activate_os()` / `spa_deactivate_os()`: no-op Linux hooks.

## Notes

Restore and cleanup callbacks log warnings if UID delegation attach/detach fails with errors other than expected duplicate/missing cases.
<!-- END FILE RESEARCH: sources/cow-pools/openzfs/module/os/linux/zfs/spa_misc_os.c -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/openzfs/module/os/linux/zfs/trace.c -->
# File Research: sources/cow-pools/openzfs/module/os/linux/zfs/trace.c

## Purpose

Defines ZFS tracepoints exactly once for kernel builds.

## Contents

The file includes core ZFS headers needed by tracepoint definitions, then under `_KERNEL` defines `CREATE_TRACE_POINTS` and includes trace headers for:

- ACL
- ARC
- debug messages
- dbuf
- DMU
- dnode
- multilist
- rrwlock
- txg
- vdev
- ZIL
- ZIO
- zrlock

## Notes

There is no runtime control flow. This is a compilation unit whose purpose is tracepoint ownership and link-time definition.
<!-- END FILE RESEARCH: sources/cow-pools/openzfs/module/os/linux/zfs/trace.c -->