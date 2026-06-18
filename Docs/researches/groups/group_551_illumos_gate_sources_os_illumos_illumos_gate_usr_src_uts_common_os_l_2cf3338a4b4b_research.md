# Group Research: group_551_illumos_gate_sources_os_illumos_illumos_gate_usr_src_uts_common_os_l_2cf3338a4b4b

Scope verified against `Docs/research_subset_a.md`: `sources/os/illumos/illumos-gate` is included in subset A. All six listed source files were read completely.

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/os/labelsys.c -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/os/labelsys.c

## Purpose

`labelsys.c` implements the kernel side of several Trusted Solaris / Trusted Extensions labeling system calls and backing caches. It manages trusted network remote-host templates, remote-host cache entries, multilevel port lists, and the `labelsys()` syscall dispatcher.

This file is security-sensitive because it maps network peers and ports to label policy, enforces privilege checks for Trusted Network Database updates, and exposes label lookup operations used by the labeled networking stack.

## Main Interfaces

System call entry point:

- `labelsys()`

Trusted network remote host cache/template operations:

- `tcache_init()`
- `tnrh_load()`
- `find_rhc()`
- `find_tpc()`
- internal syscall handlers `tnrh()` and `tnrhtp()`

Multilevel port operations:

- `tsol_mlp_anon()`
- `tsol_next_port()`
- `tsol_mlp_port_type()`
- `tsol_mlp_findzone()`
- internal syscall handler `tnmlp()`

Debug helper:

- `tsol_print_label()`

## Trusted Host Database

The file keeps trusted network host templates in `tpc_name_hash`, keyed by template name and protected by `tpc_lock`. Template records are reference-counted through `TPC_HOLD` / `TPC_RELE` and invalidated rather than mutated in place. `tnrhtp_create()` replaces an existing template by marking the old one invalid, removing it from the hash, and inserting a newly allocated copy.

Remote host entries are stored in prefix-length-indexed hash tables:

- `tnrhc_table` for IPv4 prefixes `0..32`
- `tnrhc_table_v6` for IPv6 prefixes `0..128`

Lookup uses longest-prefix match in `find_rhc()`, walking from most-specific to least-specific prefix. IPv4-mapped IPv6 addresses are normalized to IPv4. Entries are reference-counted and protected by per-bucket locks. Hash tables are allocated lazily by prefix length with `tnrhc_init_table()`.

If a remote-host entry points to an invalidated template, `find_rhc()` may refresh the host entry by finding the replacement template and reloading the hash entry. If stale entries are not allowed and no replacement exists, the lookup fails.

## Initialization

`tcache_init()` initializes template and remote-host structures, asserts label initialization has already run, creates prefix-zero tables for IPv4 and IPv6, creates an internal `_unlab` template, and installs default `0.0.0.0/0` and `::/0` remote-host entries pointing to `_unlab`.

The internal `_unlab` template represents unlabeled hosts with default/admin-low label, admin-low minimum, admin-high maximum, and the default DOI.

## Remote Host Syscall Behavior

`tnrh()` handles:

- `TNDB_LOAD`: copy in a `tsol_rhent_t`, validate template name termination, find the named template, allocate a new remote-host cache entry, and install it.
- `TNDB_DELETE`: remove the matching host entry from its prefix table.
- `TNDB_GET`: perform lookup and copy the resolved template name back.
- `TNDB_FLUSH`: invalidate and release all remote-host entries.

Non-GET operations require `secpolicy_net_config(CRED(), B_FALSE)`.

## Template Syscall Behavior

`tnrhtp()` handles:

- `TNDB_LOAD`: validate host type and create/replace a template.
- `TNDB_GET`: look up a held template and copy its contents to userland.
- `TNDB_DELETE`: invalidate and remove the named template.
- `TNDB_FLUSH`: invalidate and clear all templates.

Template names are explicitly checked for NUL termination within `TNTNAMSIZ`.

## Multilevel Ports

Multilevel ports are tracked in ordered doubly linked lists of `tsol_mlp_entry_t` protected by reader/writer locks. There is one global shared-address list, `shared_mlps`, and each zone has a private `zone_mlps` list.

`mlp_add_del()` maintains sorted order by port and protocol and rejects overlapping ranges for the same protocol. Deletion requires an exact port-range match.

`tnmlp()` supports loading, getting the next matching entry, deleting, and flushing MLP entries. It selects either the shared list or a zone-local list based on `TSOL_MEF_SHARED`.

Runtime helpers classify ports:

- `tsol_mlp_port_type()` determines whether a port is private, shared, both, or single-level.
- `tsol_mlp_findzone()` maps a shared MLP packet port to the owning zone.
- `tsol_next_port()` skips over configured MLP ranges when choosing a single-level port.

## Concurrency And Lifetime

Important locks and invariants:

- `tpc_lock` protects the template hash.
- `tnrhc_g_lock` protects lazy allocation of prefix hash tables.
- Per-prefix-bucket `tnrh_lock` protects remote-host linked lists.
- Per-entry `rhc_lock` and `tpc_lock` fields coordinate refcount destruction.
- MLP lists use `mlpl_rwlock`.
- Templates and remote-host entries are invalidated before release so new lookups do not attach to deleting objects.

## Dependencies

Depends on Trusted Extensions label/network headers, IP address helpers, zones, policy checks, `mod_hash`, kernel memory allocation, copyin/copyout, DTrace probes, and label functions such as `getlabel()` and `fgetlabel()`.

## Research Notes

Key audit areas are longest-prefix match correctness, stale-template refresh behavior, deletion while lookups hold references, MLP range overlap logic, zone/shared MLP interactions, and privilege enforcement on all mutating Trusted Network Database operations.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/os/labelsys.c -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/os/lgrp.c -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/os/lgrp.c

## Purpose

`lgrp.c` implements illumos kernel locality-group support. Lgroups describe NUMA locality between CPUs and memory, drive scheduler homing, guide memory placement, maintain per-lgroup load averages and kstats, and handle CPU/memory dynamic reconfiguration.

The file also maintains per-CPU-partition lgroup load structures, known as `lpl_t`, which mirror usable portions of the lgroup topology for dispatcher decisions.

## Global State

Core topology state:

- `lgrp_gen`: generation counter for topology/resource changes.
- `lgrp_table[]`: indexed table of initialized or recyclable `lgrp_t` objects.
- `nlgrps`, `nlgrpsmax`, `lgrp_alloc_hint`, `lgrp_alloc_max`.
- `lgrp_root`: root locality group.
- `lgrp_initialized` and `lgrp_topo_initialized`.

Bootstrap scheduler state:

- `lpl_bootstrap_list`, `lpl_bootstrap`, and associated bootstrap resource arrays allow CPU0 and early slave CPUs to use minimal lpl state before `cp_default` is fully initialized.

Memory placement tunables include private/shared random thresholds, default/root policies, processor-set awareness, and segmap policy.

## Initialization

`lgrp_init()` is staged and delegates platform initialization through `lgrp_plat_init()`:

- stage 1 sets `nlgrpsmax`
- stage 2 runs `lgrp_setup()`
- stage 4 runs `lgrp_main_init()`
- stage 5 runs `lgrp_main_mp_init()`

`lgrp_root_init()` creates the root lgroup, initializes bootstrap lpl state, and sets `t0.t_lpl`.

`lgrp_setup()` creates the root, adds CPU0, and marks CPU0 online through `lgrp_config()`.

`lgrp_main_init()` validates memory policy defaults, handles platform cases that collapse topology to UMA, initializes kstats, creates CPU0 kstats, and marks lgroup initialization complete.

`lgrp_main_mp_init()` initializes SMT support, finishes topology updates after all CPUs are online, and marks topology initialization complete.

## Reconfiguration

`lgrp_config()` handles common lgroup events:

- CPU add/delete/online/offline
- CPU partition add/delete
- memory add/delete/rename
- generation bump
- topology flatten
- latency changes

CPU online initializes the CPU’s lgroup, adds it to its CPU partition’s lpl topology, verifies the lpl topology, informs platform code, and increments `lgrp_gen`. CPU offline removes partition and lgroup membership, verifies topology, informs platform code, and increments `lgrp_gen`.

Memory add/remove uses `lgrp_mem_init()` and `lgrp_mem_fini()`. Memory rename is modeled as remove-from-source followed by add-to-destination, with special handling for DR copy-rename cases where temporarily removing the last memory node from root could make allocations fail.

## Lgroup Object Lifecycle

`lgrp_create()` allocates or recycles an `lgrp_t`, assigns an ID, clears topology/resource state, resets kstats if needed, and stores it in `lgrp_table`.

`lgrp_destroy()` marks an lgroup reusable by setting `lgrp_id` to `LGRP_NONE`, clearing parent/child/resource/memory/CPU state, updating allocation hints, and decrementing `nlgrps`. Lgroup structures are recycled rather than always freed.

## CPU And Memory Resource Management

`lgrp_cpu_init()` maps a CPU to a platform lgroup handle, creates or updates the leaf lgroup as needed, adds CPU resources to the topology, updates memory nodes for changed intermediate groups, assigns `cpu_lpl`, and links the CPU into the lgroup CPU circular list.

`lgrp_cpu_fini()` removes a CPU from the lgroup CPU list. If the last CPU leaves a leaf lgroup, CPU resources are removed; if no resources remain, the leaf is removed from the topology.

`lgrp_mnode_update()` recomputes memory-node sets for target lgroups based on their memory resource sets.

`lgrp_mem_init()` adds a memory node to an existing or newly created lgroup, updates topology under `cpu_lock`, pauses CPUs when needed, and updates changed ancestor memory-node sets.

`lgrp_mem_fini()` removes a memory node, clears memory resources if an lgroup no longer has memory, and deletes empty leaf lgroups when needed.

## Queries And Kstats

Query helpers include:

- `lgrp_home_lgrp()`
- `lgrp_home_id()`
- `lgrp_pfn_to_lgrp()`
- `lgrp_phys_to_lgrp()`
- `lgrp_hand_to_lgrp()`
- `lgrp_query_cpu()`
- `lgrp_query_load()`
- `lgrp_mem_size()`

Kstat support initializes named stats, creates per-lgroup kstats, resets counters, extracts counter and snapshot values, and reports CPU count, installed/available/free pages, and load average.

## LPL Topology

The lpl layer stores CPU-partition-specific load and resource hierarchy data. It uses `lpl_t` records indexed by lgroup ID inside each `cpupart_t`.

Main lpl operations:

- `lpl_init()` and `lpl_clear()`
- `lpl_rset_add()` and `lpl_rset_del()`
- `lpl_leaf_insert()` and `lpl_leaf_remove()`
- `lgrp_part_add_cpu()` and `lgrp_part_del_cpu()`
- `lpl_topo_verify()`
- `lpl_topo_flatten()`
- `lpl_topo_bootstrap()`

`lpl_topo_verify()` is extensive. It checks lpl/lgroup ID correspondence, parent consistency, leaf CPU lists and counts, non-leaf resource counts, resource-set membership, partition membership, orphaned lpls, and CPU-to-lpl pointers.

## Load And Thread Homing

`lgrp_loadavg()` updates a leaf lpl and its ancestors using a fixed-point exponential decay. It supports both normal aging updates and anticipatory remote-thread load increments.

`lgrp_choose()` selects a home lgroup for a thread within a CPU partition. It considers explicit lgroup affinity, partition membership, leaf-only placement, free-memory thresholds, process spread, load thresholds, expansion thresholds, and policy mode:

- random
- round-robin
- longest time since last homed

`lpl_pick()` compares two candidate lpls using load and tolerance.

`lgrp_move_thread()` is the sole routine that updates a thread’s `t_lpl`. It updates process lgroup membership, migration counters, text-replication migration tracking, and anticipatory load on the new lgroup and its ancestors. It can also remove recently added anticipatory load if the old placement was too short-lived.

## Memory Policy

Memory placement policies handled here include:

- default / next-touch
- next CPU
- random across machine
- random across process lgroups
- random across processor-set lgroups
- round-robin
- next segment

`lgrp_mem_policy_default()` decides default policy based on mapping type, size, thresholds, and processor-set awareness.

`lgrp_mem_choose()` selects the lgroup for allocation based on segment policy, current thread home, root override behavior, random/round-robin logic, and DR tolerance.

Shared memory policy support stores per-range policy in AVL trees attached to `anon_map` or vnode locality structures. Functions include initialization/finalization, AVL comparison, split/concat, lookup, and `lgrp_shm_policy_set()`.

`lgrp_memnode_choose()` chooses actual memnodes from an lgroup, optionally traversing ancestors when local nodes are exhausted.

## Concurrency

Important rules:

- `cpu_lock` protects most topology mutations after initialization.
- Some paths run with CPUs paused and must not block or acquire new locks.
- `kpreempt_disable()` protects reads of current CPU/thread lpl state where needed.
- Shared memory policy trees use `loc_lock`.
- Kstat extraction uses `lgrp_kstat_mutex`.
- Load averages are updated atomically.

## Dependencies

Depends on platform lgroup callbacks, CPU and CPU partition code, scheduler structures, memnode support, VM segment policies, AVL trees, kstats, processor groups, SMT initialization, DTrace probes, and page/memory sizing hooks.

## Research Notes

The highest-risk areas are DR memory remove/add edge cases, lgrp/lpl topology consistency, anticipatory load accounting, CPU partition transitions, shared-memory policy range splitting/concatenation, and calls made while CPUs are paused where blocking would be unsafe.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/os/lgrp.c -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/os/lgrp_topo.c -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/os/lgrp_topo.c

## Purpose

`lgrp_topo.c` implements topology construction and mutation helpers for locality groups. It builds and updates the lgroup hierarchy based on leaf-to-leaf latency, resource sets, parent/child relations, and configurable topology height limits.

This file complements `lgrp.c`: `lgrp.c` handles lifecycle, CPU/memory events, scheduler load structures, and memory policy, while `lgrp_topo.c` handles the structural algorithms for adding/removing leaves, splitting parents, propagating resource sets, collapsing duplicates, and flattening topology.

## Configuration

Top-level tunables:

- `lgrp_topo_levels`: current topology height limit, default 4.
- `lgrp_collapse_equidist`: collapse only lgroups with same latency and same resources.
- `lgrp_collapse_off`: disables duplicate collapse by default.
- `lgrp_split_off`: disables splitting by default.

Debug builds expose `lgrp_topo_debug` and print helpers for lgroup sets, resource sets, and topology.

## Resource Set Helpers

Resource sets are arrays indexed by `LGRP_RSRC_*`. Helpers include:

- `lgrp_rsets_add()`: OR all resources from one set into another.
- `lgrp_rsets_copy()`: copy resource arrays.
- `lgrp_rsets_delete()`: remove a lgroup ID from one lgroup and optionally its ancestors.
- `lgrp_rsets_empty()`: test whether all resource sets are empty.
- `lgrp_rsets_equal()`: compare all resource sets.
- `lgrp_rsets_member()` and `lgrp_rsets_member_all()`: membership tests.
- `lgrp_rsets_replace()`: replace an lgroup’s resources/latency and optionally shift old contents upward.
- `lgrp_rsets_set()`: initialize all resource classes to a single lgroup ID.

## Topology Mutation

`lgrp_ancestor_delete()` removes a child from its ancestors, decrements child counts, and destroys ancestors that become childless.

`lgrp_consolidate()` merges one non-leaf lgroup into another. It preserves the larger latency, removes empty ancestors of the source, reparents source children to the destination, propagates leaves toward root, and destroys the source lgroup.

`lgrp_collapse_dups()` searches target lgroups for duplicate non-leaf lgroups with identical resource sets, optionally requiring identical latency, and consolidates duplicates.

`lgrp_new_parent()` creates an intermediate parent with a given latency/resource set and inserts it between a child and the child’s old parent.

`lgrp_proprogate()` propagates a new leaf’s resources into a child’s parent if not already present. The misspelling is in the source symbol name.

`lgrp_split()` can split a child away from its parent when sibling leaves have different latency to a newly added leaf. It is gated by `lgrp_split_off`.

## Leaf Addition

`lgrp_lineage_add()` is the core algorithm for placing a new leaf into an existing leaf’s ancestry. It:

1. Gets platform latency between old and new leaves.
2. Walks from the old leaf up toward root.
3. Optionally splits parents when sibling latency differs.
4. Inserts a new intermediate parent if the new latency is less than the current parent latency.
5. Propagates resources upward once placement is found.
6. Enforces the topology height limit by replacing/shift-propagating parent contents when needed.
7. Collapses duplicates among changed lgroups if duplicate collapse is enabled.

`lgrp_leaf_add()` initializes a leaf’s parent as root if needed, sets leaf/root latencies, and adds the new leaf to every other leaf’s lineage and vice versa. It assumes callers hold `cpu_lock`, have preemption disabled, or are running before lgroup initialization.

## Leaf Deletion

`lgrp_leaf_delete()` removes a leaf’s resources from every lgroup that contains it, removes childless ancestors, destroys the leaf, and optionally collapses duplicate lgroups among changed nodes.

## Flattening And Height Limits

`lgrp_topo_flatten()` currently supports flattening to a two-level topology. It destroys non-root non-leaf lgroups and reparents leaves to root, updating root children/leaves and leaf latencies.

Height helper APIs:

- `lgrp_topo_height()`
- `lgrp_topo_ht_limit()`
- `lgrp_topo_ht_limit_default()`
- `lgrp_topo_ht_limit_set()`

`lgrp_topo_ht_limit_set()` caps requested height at `LGRP_TOPO_LEVELS_MAX`.

## Deferred Topology Update

`lgrp_topo_update()` completes topology for leaves whose latency was unavailable when initially added. It handles UMA root setup specially, pauses CPUs while updating delayed leaves, calls `lgrp_mnode_update()` for changed lgroups, and optionally flattens both lgroup and lpl topology when the height limit is 2.

## Concurrency

Topology updates assume strong external synchronization: `cpu_lock`, disabled preemption, or pre-initialization state. Some update paths pause CPUs and must avoid unsafe blocking.

## Dependencies

Depends on `lgrp_table`, `lgrp_root`, `lgrp_create()`, `lgrp_destroy()`, `lgrp_mnode_update()`, `lpl_topo_flatten()`, platform latency callbacks, CPU pause/start infrastructure, and klgrpset bitset helpers.

## Research Notes

Important review points are parent/child count consistency, leaf propagation to root, duplicate collapse safety, height-limit replacement behavior, disabled-by-default split/collapse code paths, and off-by-one iteration over `lgrp_alloc_max` versus passed `lgrp_count`.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/os/lgrp_topo.c -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/os/lockstat_subr.c -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/os/lockstat_subr.c

## Purpose

`lockstat_subr.c` provides resident kernel support for the lockstat driver and DTrace lockstat probes.

It is intentionally small: it defines shared lockstat probe state and one helper that counts threads currently marked for lockstat tracing.

## Main Interfaces

Global state:

- `lockstat_probemap[LS_NPROBES]`
- `lockstat_probe`

Function:

- `lockstat_active_threads()`

## Behavior

`lockstat_probemap` maps lockstat probe indexes to DTrace probe IDs. `lockstat_probe` is a function pointer used by lock instrumentation paths to fire probes when lockstat is active.

`lockstat_active_threads()` counts active threads that have `t_lockstat` set. It enters `pidlock`, starts with `curthread`, walks the circular global thread list using `t_next`, increments a counter for each marked thread, and releases `pidlock`.

## Concurrency

`pidlock` protects traversal of the global thread list. The function assumes the thread list is circular and reaches `curthread` again to terminate.

## Dependencies

Depends on thread structures, CPU/kernel headers, cyclic/time headers, SPL definitions, and `sys/lockstat.h`.

## Research Notes

The main invariant is safe global thread-list traversal under `pidlock`. This file has no allocation, no user copy, and no complex lifecycle; most lockstat behavior lives in the lockstat driver and instrumentation users of `lockstat_probe`.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/os/lockstat_subr.c -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/os/log_sysevent.c -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/os/log_sysevent.c

## Purpose

`log_sysevent.c` implements kernel system event publication to `syseventd`. It allocates and packs sysevent buffers, queues events, performs door upcalls to the user daemon, tracks sent-but-not-freed event buffers, supports daemon restart replay, manages sysevent channel registration state, and exposes DDI/user event posting interfaces.

It also maintains a small lofi device-link cache used to communicate devfsadm device-link updates to the lofi driver.

## Event Delivery State

Pending events are held on `log_eventq_head` / `log_eventq_tail`, with count `log_eventq_cnt`. Successfully delivered but not yet freed events are moved to `log_eventq_sent`.

Delivery is controlled by:

- `log_event_delivery`
- `sysevent_upcall_status`
- `sysevent_daemon_init`
- `log_event_cv`
- `async_thread`

The queue has tunable maximum size `logevent_max_q_sz`, default 5000. Threads may block on `event_qfull_cv` if the queue is full and sleeping semantics are allowed.

## Door Upcalls

`log_event_upcall()` performs a kernel door upcall to `syseventd` using `door_ki_upcall_limited()`. It handles:

- `EBADF`: daemon door died; release and clear door handle.
- `EINTR`: short pause and retry.
- `EAGAIN`: exponential backoff, usually while the server process is forking.
- other errors: log and return.

`log_event_pause()` implements the retry delay using `timeout()` and a condition variable.

`log_sysevent_filename()` is called by `syseventd` to set or refresh the door filename. It opens the door, replaces the old handle, and moves all sent-but-uncommitted events back to the pending queue in order so daemon restart can replay them.

`log_sysevent_flushq()` starts the async delivery thread if needed, marks delivery active, runs post-startup setup, and wakes the delivery loop.

## Delivery Thread

`log_event_deliver()` is the async event delivery thread. It runs under CPR callbacks, waits on `log_event_cv`, and delivers pending events in order. For each event, it releases the queue lock during the door upcall. On success, it moves the event from the pending queue to the sent queue. On hold or transport errors, it updates status and sleeps until signaled.

It handles races where a daemon restart moves sent events back to the pending queue while an upcall is in progress by replaying from the new queue head.

## Event Allocation And Attributes

Publisher APIs:

- `sysevent_alloc()`
- `sysevent_free()`
- `sysevent_add_attr()`
- `sysevent_free_attr()`
- `sysevent_attach_attributes()`
- `sysevent_detach_attributes()`
- `sysevent_attr_name()`
- `sysevent_attr_type()`

Events store class, subclass, and publisher strings in aligned payload space. Attributes are represented as nvlists and later repacked into contiguous event buffers by `se_repack()` before queueing.

`sysevent_free()` adjusts payload size when freeing attached nvlist attributes. Packed event buffers are freed by `free_packed_event()`.

## Queueing And IDs

`queue_sysevent()` assigns a monotonically increasing sequence number and high-resolution timestamp, appends the packed event to the pending queue, and wakes the delivery thread if the queue was previously empty.

If the queue is full:

- no transport returns `SE_NO_TRANSPORT`
- no-sleep callers get `SE_EQSIZE`
- sleep callers wait for space

`log_sysevent()` repacks a kernel-created event and queues it. `log_sysevent_new_id()` returns a fresh kernel event ID.

## Sent Event Data APIs

`log_sysevent_copyout_data()` searches `log_eventq_sent` by event timestamp and sequence ID, then copies the event to userland.

`log_sysevent_free_data()` removes a sent event by ID and frees its packed buffer. The source notes that delayed processing may mean the event is not on the sent queue yet and userland may need to retry.

## Channel Registration

The file maintains persistent sysevent channel registration metadata in `registered_channels[]`, protected by `registered_channel_mutex`.

Channel operations include:

- open/close channel
- bind/unbind publisher or subscriber IDs
- register/unregister class/subclass subscriptions
- cleanup IDs
- get registration data

Data structures include channel descriptors, class lists, subclass lists, subscriber bit arrays, and vmem ID allocators. `log_sysevent_register()` copies user arguments, dispatches operations, packs/unpacks nvlist registration data, and copies results back.

## User And DDI Event Posting

`log_usr_sysevent()` accepts a user-provided packed event, copies it into a kernel queue object, notifies lofi for relevant dev events, queues it with no-sleep semantics, and copies the assigned event ID out.

`ddi_log_sysevent()` is the driver-facing API. It builds publisher string `vendor:kern:driver`, allocates a sysevent, attaches attributes if present, posts it with sleep/no-sleep semantics, detaches attributes, frees the event, and maps sysevent errors to DDI return codes.

It rejects `DDI_SLEEP` from interrupt context.

## Lofi Cache

`lofi_nvl_init()` initializes a lock/CV/nvlist cache. `notify_lofi()` watches user-posted `EC_DEV_ADD` and `EC_DEV_REMOVE` events for driver `lofi`, stores/removes instance nvlist data by instance string, and broadcasts cache waiters.

## Concurrency

Important locks:

- `eventq_head_mutex`: pending queue and delivery state.
- `eventq_sent_mutex`: sent queue.
- `event_door_mutex`: door handle.
- `event_qfull_mutex`: queue-full waiters.
- `event_pause_mutex`: retry pause state.
- `registered_channel_mutex`: channel registration database.
- `lofi_devlink_cache.ln_lock`: lofi nvlist cache.

The async delivery thread intentionally releases the pending-queue lock during door upcalls.

## Dependencies

Depends on doors, sysevent structures, nvlists, vmem, DDI/devinfo, modctl event commands, CPR callbacks, timeouts, kernel threads, condition variables, lofi internals, and copyin/copyout.

## Research Notes

Key audit areas are event replay on daemon restart, sent-queue lifetime, queue-full blocking semantics, door error handling, registration table bounds, user buffer copyout sizes, nvlist packing/unpacking, no-sleep allocation paths, and lofi cache trust assumptions for user-posted dev events.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/os/log_sysevent.c -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/os/logsubr.c -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/os/logsubr.c

## Purpose

`logsubr.c` implements core kernel logging support for `/dev/log`, `/dev/conslog`, console/backlog queues, recent console message buffers, message allocation/recycling, zone-specific log clone state, and dispatch of kernel log messages to interested readers.

It is the common backend used by console logging, syslog-facing queues, panic-time message handling, and per-zone `/dev/log` clones.

## Global State

Important queues:

- `log_consq`: current console queue.
- `log_backlogq`: backlog queue used before a console reader exists.
- `log_intrq`: high-level interrupt message queue.
- `log_recentq`: recent console message buffer.
- `log_freeq`: reusable message block queue.

Important objects:

- `log_global`: global-zone log state.
- `log_backlog`: synthetic backlog log endpoint.
- `log_minorspace`: clone minor ID allocator.
- `log_cons_cache`: cache for `/dev/conslog` log structures.
- `log_zone_key`: zone-specific storage key.

`log_seq_no[]` tracks sequence numbers by log stream flag.

## Locking

`log_enter()` and `log_exit()` wrap logging operations with `log_rwlock`. The lock is writer-only in this file and supports recursive entry by the current thread through `log_rwlock_depth`. This allows grouped logging, such as multiline `printf()`, to remain ordered and non-interleaved.

## Initialization

`log_init()` creates the backlog/console queue, free-message queue, interrupt queue, recent-message queue, minor ID space, zone-specific storage key, backlog log structure, and conslog cache. It then activates console logging via `log_update()` and prints the boot banner.

`log_makeq()` creates minimal STREAMS queues sufficient for `canput()`, `putq()`, and `getq_noenab()`, with `QNOENB` so queues are never service-enabled.

Zone state is initialized by `log_zoneinit()` and freed by `log_zonefree()`. Each zone gets preallocated `/dev/log` clone records and minor numbers.

## Device Allocation

`log_alloc()` handles clone allocation:

- `LOG_CONSMIN`: allocate a write-only `/dev/conslog` structure from `log_cons_cache` and a fresh minor.
- `LOG_LOGMIN`: return an unused per-zone `/dev/log` clone from zone-specific storage.

`log_free()` releases a conslog minor and frees the conslog structure.

## Queue Updates And Backlog

`log_update()` updates a log endpoint’s queue, flags, and filter callback, then recomputes active message types for the target zone. For global-zone console readers, it updates `log_consq`.

When the primary console queue switches between the backlog and a real reader, `log_conswitch()` moves messages between queues. It marks moved messages `SL_LOGONLY` and repairs early boot timestamps that were recorded before reliable `hrestime` was available.

`log_flushq()` drains a queue by sending each message through `log_sendmsg()`.

## Filtering

Filter callbacks include:

- `log_error()`: selects error messages and normalizes kernel facility priority to error.
- `log_trace()`: matches trace IDs against `log_data` records and normalizes matching kernel messages to debug priority.
- `log_console()`: maps internal console flags to syslog priorities.

## Message Allocation

`log_makemsg()` creates a two-block STREAMS message: an `M_PROTO` header containing `log_ctl_t` and a continuation block containing the NUL-terminated text. It reuses `log_freeq` blocks for small messages when possible, including interrupt context, and avoids sleeping in interrupt paths.

`log_freemsg()` returns suitable small messages to `log_freeq` unless the free queue is full; otherwise it frees the message.

## Message Dispatch

`log_sendmsg()` is the central dispatcher. It:

1. Resolves the target zone’s log state.
2. Drops messages if no active endpoint wants their flags.
3. Marks panic-created messages and increases console queue high-water mark during panic.
4. Detects and later fills `FACILITY_AND_PRIORITY` placeholders.
5. Sets lbolt and wall-clock timestamps.
6. Updates sequence counters.
7. Sends copies to backlog and `/dev/log` clones whose flags and filter callbacks match.
8. Emits overflow warnings when a destination queue cannot accept messages.
9. Prints kernel console messages directly when needed.
10. Stores recent console messages in `log_recentq`.
11. Frees the original message.

Global-zone messages go to the backlog first, then clones. Non-global-zone messages go only to that zone’s clones.

Console fallback printing occurs if there is no copy for the console queue, the console queue is still backlog, or the system is panicking, provided `SL_LOGONLY` is not set.

## Panic/Console Printing

`log_printq()` prints queued messages directly to the console, skipping panic messages already displayed. It walks queue chains from tail to head order, strips message IDs when present, and uses `console_printf()` to avoid re-queueing through the logging system.

## Cache Constructors

`log_cons_constructor()` initializes `/dev/conslog` log objects as global-zone conslog devices.

`log_cons_destructor()` asserts the object is still a global-zone conslog with no attached data.

## Dependencies

Depends on STREAMS queues and message blocks, zones and zone-specific data, syslog priority/facility constants, console output, boot banner support, id spaces, kmem caches, time/lbolt functions, panic state, and kernel string formatting.

## Research Notes

Important invariants are recursive logging lock depth correctness, safe interrupt-context allocation, backlog-to-console timestamp repair, zone-specific clone isolation, queue overflow behavior, panic-time direct console output, placeholder priority rewriting, and ensuring log message copies are freed or queued exactly once.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/os/logsubr.c -->