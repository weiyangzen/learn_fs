# Group Research: group_548_illumos_gate_sources_os_illumos_illumos_gate_usr_src_uts_common_os_f_32a40a3a767c

Scope: `Docs/research_subset_a.md`  
Source tree: `sources/os/illumos/illumos-gate`  
Files researched: 8

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/os/flock.c -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/os/flock.c

## Purpose

`flock.c` implements illumos kernel record locking: traditional POSIX byte-range locks, open-file-description locks, mandatory-lock I/O checks, NFS/NLM lock-manager integration, PXFS/cluster lock state, and deadlock detection.

Read completely: 4,609 lines.

## Main Responsibilities

- Handles POSIX-style process-owned record locks through `reclock()`.
- Handles open-file-description locks through `ofdlock()` and `ofdcleanlock()`.
- Maintains vnode-hashed lock dependency graphs in `lock_graph[HASH_SIZE]`.
- Tracks active and sleeping locks per graph and wakes blocked requests when dependencies clear.
- Splits, coalesces, upgrades, downgrades, and deletes byte-range locks owned by the same owner.
- Performs process-level deadlock detection with a separate process dependency graph.
- Supports lock-manager shutdown/startup state per zone and per lock graph.
- Supports cluster/NLM state transitions and remote-lock cleanup by sysid, nlmid, and PXFS id.
- Implements mandatory-lock probes used by filesystem read/write/mmap paths.
- Builds lock snapshots for NLM reclaim and administrative queries.

## Lock Models

`reclock()` is the main POSIX record-lock entry point used by filesystem `frlock` paths. It validates permissions, canonicalizes ranges, handles local, remote, PXFS, I/O, blocking, nonblocking, and query requests, then dispatches through the lock graph.

`ofdlock()` implements open-file-description locking. These locks are tied to `file_t` through `f_filock`, use `l_ofd` for ownership, preserve locks across fork, avoid process-based deadlock detection, and currently require whole-file lock ranges as validated by the fcntl layer.

`cleanlocks()` removes non-OFD locks for a vnode/pid/sysid during close/exit style cleanup. OFD cleanup is separate in `ofdcleanlock()` because the lock belongs to the file description, not only the process.

## Dependency Graph

Each vnode hashes to a `graph_t`, protected by `gp_mutex`. Active locks are sorted by vnode and range. Sleeping locks are sorted by vnode. Requests that cannot proceed acquire directed edges to blocking locks.

Important routines:

- `flk_process_request()` decides whether a request can run, should fail with `EAGAIN`, should sleep, or would deadlock.
- `flk_execute_request()` applies the request and inserts active locks when needed.
- `flk_relation()` handles same-owner overlap, adjacent coalescing, unlock splitting, downgrade, and upgrade effects.
- `flk_add_edge()` adds graph edges and optionally checks lock-level cycles.
- `flk_recompute_dependencies()` repairs dependency edges after a lock is modified or removed.
- `flk_wakeup()` grants sleeping locks once all dependencies are gone.
- `flk_cancel_sleeping_lock()` removes a sleeping request and recomputes affected dependencies.

The graph is deliberately kept minimal: edges are not added when an existing path already represents the dependency.

## Deadlock Detection

`flk_check_deadlock()` projects lock dependencies onto a process graph keyed by pid/sysid. It creates `proc_vertex_t` and `proc_edge_t` records, tracks reference counts for multiple lock edges between the same owners, and detects cycles by graph traversal.

OFD locks skip this path because they are pid-less. That is an intentional semantic difference from POSIX locks and matches the file’s comments.

## Lock Manager And Cluster Paths

The file maintains per-zone lock manager state in `struct flock_globals`. `flk_set_lockmgr_status()` transitions the lock manager through up, wake-sleepers, and down states, waking or removing relevant NLM locks for the current zone.

Cluster support keeps an NLM status registry indexed by nlmid. Routines such as `cl_flk_set_nlm_status()`, `cl_flk_wakeup_sleeping_nlm_locks()`, `cl_flk_unlock_nlm_granted()`, `cl_flk_remove_locks_by_sysid()`, and `cl_flk_delete_pxfs_locks()` synchronize remote lock state with NLM or PXFS failure/recovery.

## Mandatory Locking And Filesystem Relevance

`chklock()` issues an internal lock probe for read/write paths on mandatory-lock files.

`nbl_lock_conflict()` checks active NBMAND or SVMAND locks against I/O ranges and is directly used by higher-level file access and mapping enforcement. `lock_blocks_io()` contains the final range/type conflict rule.

`convoff()`, `flk_convert_lock_data()`, and `flk_check_lock_data()` normalize and validate byte ranges, including EOF-relative and negative-length locks.

## Important Invariants

- Most lock graph operations require `gp_mutex`.
- Global graph-table and process-graph updates use `flock_lock`.
- Active locks must not block each other.
- Sleeping locks must have dependency paths to active or earlier sleeping blockers.
- `flk_set_state()` enforces ordered wake states: interrupted outranks cancelled, cancelled outranks granted.
- Remote lock-manager requests can cover ranges beyond local signed `MAXEND`, so blocker reporting must translate ranges carefully.

## Research Relevance

This is the central illumos file-locking implementation that filesystem code depends on for `fcntl`, NFS lock recovery, mandatory locking, mmap conflict checks, and vnode lock-list snapshots. It is highly relevant to VFS/filesystem semantics, especially where locks interact with close, fork, remote filesystems, and memory mappings.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/os/flock.c -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/os/fm.c -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/os/fm.c

## Purpose

`fm.c` provides kernel Fault Management Architecture support for ereport posting, FMA nvlist allocation, FMRI construction, ENA manipulation, panic banners, and crash-dump persistence of pending ereports.

Read completely: 1,384 lines.

## Main Responsibilities

- Initializes the kernel ereport sysevent channel and error queue in `fm_init()`.
- Drains queued ereports to sysevents or console output during panic.
- Prints compact nvlist telemetry through `fm_nvprint()` and `fm_nvprintr()`.
- Implements `fm_panic()`, `is_fm_panic()`, and `fm_banner()` for FMA-driven fatal errors.
- Writes pending ereports to the dump device through `fm_ereport_dump()`.
- Posts ereports to `FM_ERROR_CHAN` through `fm_ereport_post()`.
- Provides FMA-specific nvlist allocator wrappers.
- Builds standard ereport payloads and FMRIs for hc, dev, cpu, mem, and ZFS schemes.
- Generates and decodes ENA values.
- Converts stack program counters into symbolic payload strings.

## Event And Dump Flow

`fm_init()` binds `FM_ERROR_CHAN`, sizes the error queue, allocates a dump buffer, and installs kstats for dropped or malformed telemetry.

`fm_drain()` is the error queue drain callback. During normal operation it posts the nvlist to the sysevent channel. During panic it prints the nvlist to the console.

`fm_ereport_dump()` drains the error queue outside panic, then walks the sysevent channel and writes `erpt_dump_t` headers plus encoded event buffers to the dump device. It records checksums, event sizes, high-resolution timestamps, and wall-clock bases.

## Panic Behavior

`fm_panic()` records a panic format string atomically, disables fast reboot on x86, and calls `vpanic()`.

`fm_banner()` emits the special FMA panic message with `SUNOS-8000-0G`, platform, host, source version, event time, and recommended action. It intentionally uses console output for most text and `cmn_err()` only for the log summary.

## Nvlist And Payload Construction

`fm_nvlist_create()` creates nvlists using either the default kernel allocator or a caller-supplied fixed-buffer allocator. `fm_nvlist_destroy()` optionally frees or retains the allocator.

`i_fm_payload_set()` is the varargs payload encoder. It supports scalar values, arrays, strings, nested nvlists, and nvlist arrays for the nvpair types used by FMA.

`fm_ereport_set()` builds a category-1 ereport with class, ENA, detector, and extra payload members.

## FMRI Builders

The file provides scheme-specific helpers:

- `fm_fmri_hc_set()` and `fm_fmri_hc_create()` for hierarchical-component FMRIs.
- `fm_fmri_dev_set()` for device-path FMRIs.
- `fm_fmri_cpu_set()` for CPU FMRIs.
- `fm_fmri_mem_set()` for memory FMRIs.
- `fm_fmri_zfs_set()` for ZFS pool/vdev FMRIs.

Failures increment `erpt_kstat_data.fmri_set_failed` or related counters rather than panicking.

## ENA Helpers

`fm_ena_generate_cpu()`, `fm_ena_generate()`, `fm_ena_increment()`, `fm_ena_generation_get()`, `fm_ena_format_get()`, `fm_ena_id_get()`, and `fm_ena_time_get()` implement formats 1 and 2 of the Event Numeric Association field.

## Important Invariants

- Ereports larger than `ERPT_DATA_SZ` or with zero encoded size are dropped.
- FMA nvlist creation with default allocation may sleep and is only valid in passive kernel contexts.
- Fixed-buffer allocators exist for constrained contexts.
- Some FMRIs require exact protocol versions; version mismatch increments failure kstats.

## Research Relevance

For filesystem/storage work, the ZFS FMRI helper and ereport posting path are the key pieces. This file defines how kernel storage faults can be encoded, queued, persisted to crash dumps, and later consumed by FMA tooling.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/os/fm.c -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/os/fork.c -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/os/fork.c

## Purpose

`fork.c` implements process creation for user and kernel processes: `forkx`, `forkallx`, branded-zone `vfork`, `newproc()`, process structure allocation, LWP cloning, resource-control accounting, vfork address-space release, and parent waiting.

Read completely: 1,480 lines.

## Main Responsibilities

- Implements syscall entry points `vfork()` and `forksys()`.
- Performs shared fork logic in `cfork()`.
- Allocates and initializes child `proc_t` structures in `getproc()`.
- Duplicates or shares address spaces depending on fork type.
- Clones one LWP for fork1 or all LWPs for forkall.
- Handles process contracts, tasks, pools, projects, zones, sessions, credentials, file tables, and current/root directories.
- Creates kernel processes and init-style user processes through `newproc()`.
- Cleans up partially constructed children on fork failure.
- Releases address spaces in `relvm()`.
- Implements `vfwait()` for parents waiting on vfork children.

## Fork Entry Points

`forksys()` dispatches subcodes:

- `0`: `forkx(flags)` through `cfork(0, 1, flags)`.
- `1`: `forkallx(flags)` through `cfork(0, 0, flags)`.
- `2`: `vforkx(flags)` through `cfork(1, 1, flags)` and marks `t_post_sys`.

The legacy `vfork()` syscall remains for Solaris 10 branded zones.

Allowed flags are `FORK_NOSIGCHLD` and `FORK_WAITPID`.

## `cfork()` Flow

`cfork()` validates flags and policy, rejects `/proc` agent LWPs, holds parent LWPs with `SHOLDFORK1` or `SHOLDFORK`, enters the pool barrier, and calls `getproc()`.

For vfork, the child shares the parent address space, clears watchpoints temporarily, marks `SVFORK`, and uses the parent shared-memory accounting.

For normal fork, it sets `SFORKING`, holds `/proc` state with `sprlock_proc()`, duplicates the address space through `as_dup()`, removes inherited DTrace fasttrap probes from the child, and duplicates shared memory and DTrace helper state.

After address-space setup, it duplicates resource controls, allocates the child LWP directory and tid hash, clones one or all LWPs, attaches the child to process contracts, inherits core settings and process context ops, sets tracing stops, and arranges return values.

## Process Allocation

`getproc()` enforces zone shutdown, task/project/zone process resource controls, global process limits, per-user limits, and privilege checks. It allocates from `process_cache`, initializes locks and process fields, allocates a pid, holds executable vnodes, links the child into pid and active process lists, attaches it to the parent, task, pool, session, orphan list, and child chain, and duplicates user-area state.

It also increments file-table references through `fcntl_add()`/`flist_fork()`, holds cwd/root/cwd refstr, duplicates audit state, copies credentials, process flags, tracing masks, stack/heap layout fields, security flags, and resource-control cached values.

## Kernel Process Creation

`newproc()` creates either class-kernel processes or init-like user processes. Kernel processes are attached to task0/default pool, clear user tracing state, initialize process resource controls, and create a stopped kernel LWP. User init-style creation creates a new task and default rlimit controls before creating the first LWP.

## Cleanup Paths

`fork_fail()` releases file references, pending signals, uid process counts, credentials, file-list storage, cwd/root/executable references, cwd refstr, and brand state.

`forklwp_fail()` removes already-created LWPs from the child process, updates task/project/zone LWP counts, frees door data and LWP templates, removes threads from the global all-thread list, informs the scheduler, fixes lgroup load accounting, and frees thread structures.

Error paths unwind address spaces, shared memory, DTrace helpers, resource controls, task attachment, pid state, pool references, LWP directories, and tid hashes.

## Vfork Release And Wait

`relvm()` handles both vfork and normal exit/exec address-space release. For vfork children it clears `SVFORK`, switches the child to `kas`, notifies the HAT, copies heap/stack and shared-memory accounting back to the parent, restores watched pages, clears parent `SVFWAIT`, and signals the parent.

`vfwait()` waits until the vfork child exits or execs, carefully avoiding stale child references by re-looking up the pid and locking the child before dropping `pidlock`.

## Important Invariants

- Fork failure past each construction phase has a matching unwind path.
- `pool_barrier_exit()` is delayed until the child has enough resource-set identity to be safely visible.
- `pidlock` handoff to `CL_FORKRET()` prevents the child from running and disappearing before scheduler setup completes.
- vfork lock ordering between parent and child is explicitly delicate because the parent may exit once woken.
- `/proc` locks and DTrace probe removal are coordinated before child instrumentation is duplicated.

## Research Relevance

This file matters to filesystem research because fork semantics define file table inheritance, OFD lock preservation context, cwd/root/executable vnode references, address-space duplication for mmap state, and vfork sharing/release behavior. It is also a major consumer of process, task, zone, and resource-control infrastructure.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/os/fork.c -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/os/ftrace.c -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/os/ftrace.c

## Purpose

`ftrace.c` implements a low-overhead per-CPU fast tracing facility with circular buffers, global enable/disable state, dynamic CPU configuration support, and trace-record writers for zero to three arguments.

Read completely: 528 lines.

## Main Responsibilities

- Initializes global tracing state with `ftrace_init()`.
- Lazily initializes per-CPU tracing state in `ftrace_cpu_init()`.
- Allocates per-CPU ring buffers on first start through `ftrace_cpu_start()`.
- Stops tracing globally and per CPU.
- Frees per-CPU buffers during CPU unconfiguration in `ftrace_cpu_fini()`.
- Registers CPU dynamic reconfiguration callbacks.
- Records trace events through `ftrace_0()`, `ftrace_1()`, `ftrace_2()`, `ftrace_3()`, and `ftrace_3_notick()`.

## State Model

Global state uses `ftrace_state` with `FTRACE_READY` and `FTRACE_ENABLED`.

Each CPU has `cpu_ftrace.ftd_state`, `ftd_first`, `ftd_last`, and `ftd_cur`. `FTRACE_READY` means the CPU can trace. `FTRACE_ENABLED` means trace calls on that CPU may append records.

`ftrace_atboot` starts tracing during init if set. `ftrace_nent` controls per-CPU ring size.

## Locking And Trace Context

`ftrace_lock` protects global and per-CPU state transitions and buffer pointer assignment. Trace-context writers do not take this lock. Instead, they disable interrupts, recheck the per-CPU enabled bit, write one fixed-size record, advance the circular pointer, and restore interrupts.

This design avoids blocking in tracing paths and relies on CPU power-off state to make buffer freeing safe.

## CPU Dynamic Reconfiguration

`ftrace_cpu_setup()` responds to `CPU_CONFIG` by initializing the CPU and starting it if global tracing is enabled. It responds to `CPU_UNCONFIG` by finalizing the CPU trace state, requiring the CPU to be powered off before freeing its buffer.

## Trace Records

The trace functions store:

- event string pointer
- current thread
- timestamp from `gethrtime_unscaled()` except `ftrace_3_notick()`
- caller
- up to three data arguments

Buffers wrap from `ftd_last` back to `ftd_first`.

## Important Invariants

- `ftrace_nent < 1` prevents initialization.
- Per-CPU buffers are allocated lazily and published with `membar_producer()`.
- Buffer freeing only occurs when the CPU is powered off.
- Trace calls must tolerate stale global state reads and rely on the per-CPU enabled check.

## Research Relevance

This file is not filesystem-specific, but it provides a kernel tracing substrate that can capture low-level storage, VFS, and scheduler events with low overhead when instrumented callers use ftrace macros.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/os/ftrace.c -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/os/group.c -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/os/group.c

## Purpose

`group.c` implements a small generic kernel collection type, `group_t`, for storing pointer elements in a resizable array with iteration, indexed access, insertion/removal, and integer-list formatting support.

Read completely: 454 lines.

## Main Responsibilities

- Initializes and destroys `group_t` objects.
- Adds and removes pointer elements.
- Grows and shrinks the backing array in powers of two.
- Packs arrays after removal without preserving order.
- Supports pre-expansion and indexed insertion.
- Provides simple iterator state through `group_iter_t`.
- Converts groups of integer-like elements into compact range strings.

## Collection Semantics

`group_create()` zeroes a group. `group_destroy()` requires `grp_size == 0` and frees the backing set if allocated. `group_empty()` clears current entries but preserves capacity.

`group_add()` appends an element, optionally refusing to resize when `GRP_NORESIZE` is set. `group_remove()` searches for an element, nulls it, packs the set, decrements size, and can shrink capacity under `GRP_RESIZE`.

`group_expand()` grows capacity until it can hold at least a requested count.

## Storage Management

`group_grow_set()` doubles capacity or allocates the default capacity of 2. It copies old entries and frees old storage.

`group_shrink_set()` halves capacity down to the minimum default. It assumes capacity is a power of two and copies only the retained portion.

`group_pack_set()` moves later non-null entries into earlier holes. Element order is explicitly not preserved as a semantic guarantee.

## Access Helpers

`group_iter_init()` and `group_iterate()` provide sequential traversal over non-null entries up to `grp_size`.

`group_access_at()` returns the raw entry at an index, bounded by capacity. `group_add_at()` inserts at a specified index if capacity is sufficient and grows `grp_size` to include it. `group_remove_at()` clears an indexed slot. `group_find()` returns the index of a pointer or `(uint_t)-1`.

## Formatting

`group2intlist()` iterates group entries, maps each pointer through a caller-supplied converter, and emits compact integer ranges such as `1,2-5,8` into a caller buffer.

## Important Invariants

- Backing capacity is maintained as a power of two.
- `group_destroy()` expects the group to be logically empty.
- `group_add_at()` assumes the target slot is empty.
- The range formatter assumes iteration order is already meaningful for consecutive ID compression.

## Research Relevance

This is a general utility rather than a direct filesystem component. It is relevant as a shared kernel container used by subsystems that need small dynamic sets without list overhead.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/os/group.c -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/os/grow.c -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/os/grow.c

## Purpose

`grow.c` implements user address-space growth and mapping syscalls: `brk`, stack growth, anonymous mmap, file mmap, munmap, mprotect, and mincore. It also handles large-page heap/stack policy, mmap address selection, ASLR, and NBMAND mapping conflicts.

Read completely: 1,077 lines.

## Main Responsibilities

- Implements `brk()` and heap extension/shrink in `brk_internal()`.
- Chooses large-page heap sizes through `brk_lpg()`.
- Implements stack growth through `grow()` and `grow_internal()`.
- Chooses large-page stack sizes through `grow_lpg()`.
- Chooses mmap addresses through `choose_addr()`.
- Implements anonymous mappings through `zmap()`.
- Implements shared/private file mappings through `smmap_common()`.
- Provides 64-bit and 32-bit syscall wrappers: `smmap64()`, `smmap32()`, and `smmaplf32()`.
- Implements `munmap()`, `mprotect()`, and `mincore()`.

## Heap Growth

`brk()` serializes heap changes with `as_rangelock()`. A zero argument returns the current break for `sbrk()` support. If automatic large pages are enabled, `brk_lpg()` chooses a page size through `map_pgsz()` and backs off to smaller pages on failure.

`brk_internal()` initializes `p_brkbase` on first use, enforces `RLIMIT_DATA`, rounds requested mappings to the selected page size, maps zero-fill-on-demand memory through `as_map()` and `segvn_create`, or unmaps to shrink. It maintains `p_brksize` as the process heap size.

## Stack Growth

`grow()` serializes stack changes with `as_rangelock()`, calls the large-page or base implementation, and pre-faults newly granted stack pages with `as_fault()`.

`grow_internal()` assumes downward-growing stacks, enforces `RLIMIT_STACK`, avoids shrinking, sets executable-stack permissions from `p_stkprot`, and maps new stack memory through `segvn_create`. It can shrink the stack guard segment if the stack limit was expanded, but refuses to shrink the guard below `stack_guard_min_sz`.

## Address Selection And ASLR

`choose_addr()` accepts fixed mappings by unmapping the requested range. For non-fixed mappings it first tries the supplied hint unless randomization or alignment policy overrides it, then calls `map_addr()`.

`aslr_respect_mmap_hint` controls whether non-null unaligned hints suppress randomization. `smmap_common()` adds `_MAP_RANDOMIZE` when ASLR is enabled and the mapping is randomizable.

## Anonymous Mapping

`zmap()` validates protections and fixed-address ranges, selects an address with `choose_addr()`, and creates anonymous zero-fill mappings through `segvn_create` with a null vnode and amp.

## File Mapping

`smmap_common()` validates mmap flags, protections, file descriptor access, file offsets, fixed-address bounds, low-32-bit constraints, `MAP_TEXT` and `MAP_INITDATA` combinations, and `VFS_NOEXEC`.

For regular files it checks large-file overflow. Shared mappings require write access for writable protections. Mappings on noexec files remove executable max protection.

Before mapping a file with read/write/exec access, it enters NBMAND critical state if needed, asks `nbl_svmand()` for SVMAND behavior, and calls `nbl_conflict()` over the full mapping range. A conflict returns `EACCES`.

The actual mapping is delegated to `VOP_MAP()`. Successful shared mappings notify machine-specific shared-address-space code. Successful text/initdata regular-file mappings set `VVMEXEC` on the vnode.

## Unmap, Protect, And Residency

`munmap()` validates page alignment and user range, removes lwpchan mappings, and calls `as_unmap()`.

`mprotect()` validates address, length, and protections, then calls `as_setprot()`.

`mincore()` validates user range, walks the address interval in `MC_QUANTUM` chunks, calls `as_incore()`, and copies residency bytes back to user space.

## Important Invariants

- Heap and stack growth are serialized by `as_rangelock()`.
- Heap and stack large-page policies never deliberately reduce the selected page-size code.
- Fixed mappings unmap the target range before remapping.
- `MAP_FIXED` and `_MAP_RANDOMIZE` are rejected together.
- File mappings respect `VFS_NOEXEC`, descriptor access mode, regular-file offset overflow, and mandatory lock conflicts.
- lwpchan mappings are discarded on fixed mmap and munmap.

## Research Relevance

This file is central to filesystem/VFS research because it is the syscall-level bridge between files and virtual memory. The `VOP_MAP()` call path, `VVMEXEC` marking, noexec enforcement, and NBMAND conflict checks define how filesystem vnodes become memory mappings and how locking can block mappings.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/os/grow.c -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/os/id32.c -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/os/id32.c

## Purpose

`id32.c` provides a compact kernel service that maps arbitrary pointers to 32-bit identifiers by allocating aligned handle entries from a 32-bit-addressable arena.

Read completely: 114 lines.

## Main Responsibilities

- Initializes a `vmem` arena backed by `heap32_arena`.
- Creates an aligned kmem cache for handle entries.
- Allocates 32-bit IDs for pointers.
- Frees IDs after validation.
- Looks up pointers from IDs after validation.

## Encoding Model

Each allocated handle entry stores one pointer. The returned ID encodes the handle entry address with low-bit validation data.

On amd64, the ID encodes the offset from `heap_core_base` so the value fits in 32 bits. Other architectures encode the pointer value directly. `ID32_VALID()` verifies that decoding and re-encoding produces the original ID.

## Public API

`id32_init()` creates the arena and cache.

`id32_alloc()` allocates a handle entry, stores the pointer, encodes the handle address, asserts the result fits in `uint32_t`, and returns zero on allocation failure.

`id32_free()` validates the ID and frees the decoded handle entry, warning and rejecting bad IDs.

`id32_lookup()` validates the ID and returns the stored pointer, or `NULL` for invalid IDs.

## Important Invariants

- Handle entries are aligned to `ID32_ALIGN`.
- IDs include enough low-bit information to reject malformed values.
- Invalid frees/lookups warn but do not panic.
- The caller owns lifetime correctness for the stored pointer; this file only maps IDs to handle slots.

## Research Relevance

This is a small infrastructure utility. It is relevant where kernel/user or subsystem APIs need stable 32-bit handles for kernel pointers, including compatibility or ioctl-style interfaces.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/os/id32.c -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/os/inst_sync.c -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/os/inst_sync.c

## Purpose

`inst_sync.c` implements the loadable `inst_sync` syscall used to write kernel device instance-number assignments to stable storage.

Read completely: 372 lines.

## Main Responsibilities

- Registers a two-argument syscall module through `_init()`, `_info()`, and `_fini()`.
- Validates privilege and flags in `in_sync_sys()`.
- Serializes access to instance data with `e_ddi_enter_instance()` / `e_ddi_exit_instance()`.
- Avoids unnecessary writes when instance data is clean unless forced.
- Creates a new instance file without overwriting an existing file.
- Walks the kernel instance tree and writes permanent instance bindings.
- Flushes and fsyncs the created file.
- Removes the created file on error.

## Syscall Behavior

Userland sees `int inst_sync(pathname, flags)`.

Supported flags are:

- `INST_SYNC_IF_REQUIRED`: write only if instance information changed.
- `INST_SYNC_ALWAYS`: write even if instance information is clean.

The syscall requires `secpolicy_sys_devices()`. `inst_sync_disable` can make the syscall a no-op for debugging/testing.

If instance data is clean and the caller did not force a write, the syscall returns `EALREADY`.

## File Creation And Writing

`in_sync_sys()` opens the pathname with `vn_open()` using `FCREAT`, mode `0444`, and `CRCREAT`, explicitly refusing overwrite. `EISDIR` is translated to `EACCES`.

`in_write_instance()` wraps the vnode in a small local buffered `File` abstraction, writes a warning header, then walks the instance tree.

`in_write()`, `in_fputs()`, `in_fflush()`, and `in_fclose()` implement minimal kernel-side buffered output using `vn_rdwr()`, `VOP_FSYNC()`, `VOP_CLOSE()`, and `VN_RELE()`.

## Instance Tree Format

`in_walktree()` recursively walks `in_node_t` children. For each node with drivers, it builds a device path component using `node` or `node@unit-address`, then writes one line for each driver binding whose state is `IN_PERMANENT`.

It skips provisional and unknown assignments to avoid duplicate or `-1` instances.

Output lines encode:

- quoted device path
- instance number
- quoted driver name

## Important Invariants

- Only one instance sync runs at a time.
- The file is only marked clean after a full successful write, flush, and close.
- Partial files are removed on error.
- The path-building buffer is global/shared during recursion and must be treated carefully.
- Instance state must be permanent before it is persisted.

## Research Relevance

This file touches filesystem behavior through kernel-side file creation, write, fsync, close, and removal. It is also relevant to device-tree persistence, which affects stable device naming and therefore storage device identity across reboot.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/os/inst_sync.c -->