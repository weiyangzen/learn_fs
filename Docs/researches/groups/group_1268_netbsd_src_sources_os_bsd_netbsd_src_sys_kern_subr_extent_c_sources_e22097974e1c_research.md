# Group Research: group_1268_netbsd_src_sources_os_bsd_netbsd_src_sys_kern_subr_extent_c_sources_e22097974e1c

Scope checked against `Docs/research_subset_a.md`: all requested files are under `sources/os/bsd/netbsd-src`, which is included in subset A. All listed source files were read completely.

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/sys/kern/subr_extent.c -->
# File Research: sources/os/bsd/netbsd-src/sys/kern/subr_extent.c

Read completely: 1188 lines.

Implements NetBSD's general-purpose extent manager for tracking allocated address/resource ranges. It supports dynamically allocated extents and fixed-storage extents for early boot or constrained callers, with a global `extent_region` pool and optional preallocated region descriptors.

Core behavior:
- `extent_create()` builds an extent over `[start, end]`, optionally using caller-provided fixed storage and prepopulating a descriptor freelist.
- `extent_alloc_region()` allocates an exact range, detects conflicts in the sorted allocated-region list, and can wait on the extent CV with `EX_WAITSPACE`/`EX_CATCH`.
- `extent_alloc_subregion1()` implements first-fit or best-fit allocation inside a subrange with alignment, skew, boundary, and `EX_BOUNDZERO` handling.
- `extent_insert_and_optimize()` inserts allocated ranges and coalesces adjacent regions unless `EXF_NOCOALESCE` is set.
- `extent_free()` removes, trims, or splits an allocated region and wakes waiters.
- `extent_destroy()` and `extent_print()` free/debug the tracked map.

Concurrency and risks:
- Normal extents use `ex_lock` and `ex_cv`; `EX_EARLY` extents intentionally skip locking.
- Descriptor allocation must happen before taking the extent lock because it may sleep.
- Fixed extents can block waiting for descriptors unless `EX_MALLOCOK` or non-wait flags change behavior.
- Freeing partial regions is disallowed under `EXF_NOCOALESCE`; only exact descriptor removal works.
- The allocator has many overflow-sensitive checks around `start + size`, alignment, and boundary calculations.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/sys/kern/subr_extent.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/sys/kern/subr_fault.c -->
# File Research: sources/os/bsd/netbsd-src/sys/kern/subr_fault.c

Read completely: 282 lines.

Implements the kernel fault-injection control device and API. The exported `fault_inject()` checks either a global fault configuration or the current LWP's specific-data configuration and returns true on every configured Nth call, with one-shot behavior after the first injected fault.

Control surface:
- `FAULT_IOC_ENABLE` supports `FAULT_MODE_NTH_ONESHOT` for global or per-LWP scope.
- `FAULT_IOC_DISABLE` turns off global or current-LWP injection.
- `FAULT_IOC_GETINFO` returns the number of injected faults for the chosen scope.
- Per-LWP state is allocated lazily through `lwp_setspecific()` and freed by the LWP-specific-data destructor.
- The module initializes the global mutex and LWP key, and refuses unload.

Concurrency and risks:
- Global enable/disable is serialized by `fault_global_lock`; fast-path reads use atomic loads.
- Per-LWP configuration is not globally locked, matching the LWP-specific-data ownership model.
- One-shot and counters are volatile/atomic enough for the intended debug use, but not a transactional policy interface.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/sys/kern/subr_fault.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/sys/kern/subr_hash.c -->
# File Research: sources/os/bsd/netbsd-src/sys/kern/subr_hash.c

Read completely: 268 lines.

Provides generic kernel hash-table allocation and hash-statistics registration. `hashinit()` rounds the requested element count up to a power of two, allocates an array of list heads for `HASH_LIST`, `HASH_PSLIST`, `HASH_SLIST`, or `HASH_TAILQ`, initializes each bucket, and returns a mask. `hashdone()` frees the table using the mask and bucket-head size.

The second half implements `hashstat_register()` and the `kern.hashstat` sysctl. Registered providers supply `hashstat_sysctl` records; the sysctl supports list/describe behavior and query-by-name through `CTL_QUERY`, dropping the sysctl lock while traversing providers under `hashstat_lock`.

Risks and notes:
- `elements` must be nonzero; oversized requests are capped before rounding.
- Query names are copied in from userland and unmatched queries return `ENOENT`.
- Provider callbacks run under the hashstat reader lock, so callback locking behavior matters.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/sys/kern/subr_hash.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/sys/kern/subr_humanize.c -->
# File Research: sources/os/bsd/netbsd-src/sys/kern/subr_humanize.c

Read completely: 117 lines.

Implements compact byte-count formatting. `humanize_number()` writes an integer value with optional SI or binary prefixes so the result fits the supplied buffer length, using decimal powers to decide when to scale by the divisor. It supports suffixes such as `"B"` and prefixes through exa.

`format_bytes()` wraps `humanize_number(..., "B", 1024)` and removes a trailing `" B"` for unscaled byte values.

Risks and notes:
- Returns `-1` for null buffers/suffixes or buffers too small for the minimal formatted value.
- Scaling uses integer division, so output is intentionally coarse rather than fractional.
- The binary-prefix mode still uses legacy `K/M/G...` prefix spelling rather than IEC `Ki/Mi`.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/sys/kern/subr_humanize.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/sys/kern/subr_interrupt.c -->
# File Research: sources/os/bsd/netbsd-src/sys/kern/subr_interrupt.c

Read completely: 497 lines.

Implements machine-independent interrupt-control sysctls used by `intrctl`. It can list interrupt IDs, assigned CPUs, and per-CPU counts; set interrupt affinity; and mark a CPU as accepting or avoiding interrupts through scheduler-state shielding.

Core paths:
- `interrupt_shield()` changes `SPCF_NOINTR` on a target CPU, using an xcall when needed.
- `interrupt_avert_intr()` moves assigned interrupts away from a CPU to available CPUs.
- `interrupt_intrio_list_size()` and `interrupt_intrio_list()` build variable-sized `intrio_list` snapshots.
- Sysctls under `kern.intr` provide `list`, `affinity`, `intr`, and `nointr`.
- Authorization uses `KAUTH_SYSTEM_INTR` for affinity and `KAUTH_SYSTEM_CPU` for CPU interrupt state.

Risks and notes:
- `intr`/`nointr` accept a cpuset but use only the first CPU.
- Interrupt list generation can return `EAGAIN` if interrupts are added after size calculation.
- `nointr` first shields the CPU, then attempts migration; if no destination CPU is available, migration fails.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/sys/kern/subr_interrupt.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/sys/kern/subr_iostat.c -->
# File Research: sources/os/bsd/netbsd-src/sys/kern/subr_iostat.c

Read completely: 506 lines.

Implements kernel I/O statistics objects and legacy-compatible `hw.disk*`/`hw.iostat*` sysctls. A global `iostatlist` tracks all `struct io_stats` records under `iostatlist_lock`.

Core behavior:
- `iostat_alloc()`, `iostat_free()`, `iostat_rename()`, and `iostat_find()` manage stats object lifetime and names.
- `iostat_wait()`, `iostat_busy()`, and `iostat_unbusy()` maintain wait/busy counters, timestamps, cumulative time, and weighted time sums.
- `iostat_unbusy()` also accounts read/write byte and transfer counts.
- `iostat_seek()` increments seek counts.
- Sysctls return disk-only names, all iostat names, and arrays of `io_sysctl` records, including old `hw.diskstats` size behavior.

Risks and notes:
- Per-device counters are updated without an internal per-object lock; callers are expected to serialize appropriately.
- Time accumulation depends on balanced wait/busy/unbusy transitions.
- Name sysctl output is a space-separated string with NUL-copy behavior inherited from older interfaces.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/sys/kern/subr_iostat.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/sys/kern/subr_ipi.c -->
# File Research: sources/os/bsd/netbsd-src/sys/kern/subr_ipi.c

Read completely: 453 lines.

Implements the MI inter-processor interrupt interface. It provides asynchronous registered IPI handlers and synchronous message-based IPIs built on reserved handler slot zero.

Core behavior:
- `ipi_sysinit()` initializes handler slots and reserves `IPI_SYNCH_ID` for mailbox messages.
- `ipi_register()`/`ipi_unregister()` allocate asynchronous handler IDs; unregister broadcasts a no-op synchronous IPI to drain in-flight calls.
- Per-CPU pending bitfields record asynchronous IPIs; `ipi_cpu_handler()` atomically drains and invokes handlers.
- `ipi_unicast()`, `ipi_multicast()`, and `ipi_broadcast()` enqueue `ipi_msg_t` pointers into per-CPU cache-line mailboxes and trigger the synchronous IPI.
- `ipi_wait()` spin-waits until remote CPUs decrement the message pending count.

Concurrency and risks:
- Triggering requires preemption disabled for multi/broadcast paths.
- Mailboxes have a fixed number of slots and spin with an event counter when full.
- `ipi_multicast()` executes the local handler directly but only waits for remote acknowledgements.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/sys/kern/subr_ipi.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/sys/kern/subr_kcov.c -->
# File Research: sources/os/bsd/netbsd-src/sys/kern/subr_kcov.c

Read completely: 805 lines.

Implements NetBSD's KCOV coverage device and sanitizer coverage hooks. Opening `/dev/kcov` clones a file descriptor backed by `kcov_fileops`; ioctls allocate buffers, enable/disable tracing, and attach/detach remote coverage buffers.

Core behavior:
- `kcov_allocbuf()` creates an anonymous UVM object, maps it wired into the kernel, and exposes it to userland via `fo_mmap`.
- Normal descriptors are owned by one enabled LWP through `l->l_kcov`.
- Remote coverage records are registered by subsystem/id and use preallocated maximum-size buffers.
- Remote enter/leave temporarily assigns a remote descriptor to the current LWP if enabled.
- Trace PC mode records return addresses; trace CMP mode records comparison metadata and operands.
- `kcov_silence_enter()`/`leave()` suppress tracing around sensitive instrumentation paths such as lockdebug.

Risks and notes:
- Tracing is skipped during cold boot and interrupt context.
- Descriptor close defers freeing if the descriptor is still active on an LWP.
- Remote registration assumes one active reference at a time and panics on duplicate registration or missing remote IDs.
- Instrumentation functions must avoid external calls and are marked `__nomsan`.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/sys/kern/subr_kcov.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/sys/kern/subr_kcpuset.c -->
# File Research: sources/os/bsd/netbsd-src/sys/kern/subr_kcpuset.c

Read completely: 546 lines.

Implements dynamic kernel CPU sets. A `kcpuset_t` is a variable-sized bitfield embedded after a small implementation header carrying a reference count and deferred-free chain pointer.

Core behavior:
- Early boot users receive temporary static one-word bitsets recorded by pointer; `kcpuset_sysinit()` replaces them with dynamically allocated full-size sets.
- `kcpuset_create()`, `clone()`, `destroy()`, `use()`, and `unuse()` manage allocation and references.
- Copyin/copyout bridge user `cpuset_t` data.
- Bit operations include zero/fill/copy/set/clear/test, match/intersection checks, first-set-bit, merge/intersect/remove, and population count.
- Atomic variants set/clear and merge/intersect/remove through atomic word operations.

Risks and notes:
- Early boot support is limited to `KC_SAVE_NITEMS` entries and one 32-bit word until fixup.
- Reference-counted sets must not be modified after being placed on a deferred free list.
- User copy length larger than the kernel bitfield is rejected.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/sys/kern/subr_kcpuset.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/sys/kern/subr_kmem.c -->
# File Research: sources/os/bsd/netbsd-src/sys/kern/subr_kmem.c

Read completely: 653 lines.

Implements the kernel wired-memory allocator API layered over pool caches and UVM. Small allocations are rounded and served from size-class `pool_cache_t` arrays; larger allocations come from `kmem_va_arena`.

Core behavior:
- Size classes cover small caches up to 1024 bytes and selected larger caches up to a page, with alignment chosen around coherency units and page boundaries.
- `kmem_intr_alloc()`/`free()` are interrupt-capable allocation primitives.
- `kmem_alloc()`/`zalloc()`/`free()` assert non-interrupt context and integrate KMSAN marking.
- Large allocations use `uvm_km_kmem_alloc()`/`uvm_km_kmem_free()`.
- SDT probes expose allocation/free events per size class and for large allocations.
- Helpers provide `kmem_asprintf()`, string duplication/freeing, and stack-or-heap temporary buffers.

Debug and risks:
- DIAGNOSTIC hard kernels add a footer storing the requested size and panic on size-mismatched free.
- KASAN redzones adjust requested sizes and mark freed allocations.
- `LOCKDEBUG_MEM_CHECK` detects active locks inside memory being freed.
- Free callers must pass the original requested size.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/sys/kern/subr_kmem.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/sys/kern/subr_kobj.c -->
# File Research: sources/os/bsd/netbsd-src/sys/kern/subr_kobj.c

Read completely: 1280 lines.

Implements the modular-kernel ELF relocatable object loader. Under `MODULAR`, it loads ET_REL objects from memory or a provider-specific read function, maps sections, resolves symbols, applies relocations, registers kernel symbols, and unloads module memory.

Core behavior:
- `kobj_load_mem()` creates a memory-backed object; VFS-backed loading is implemented separately.
- `kobj_load()` validates ELF header/version/type/machine, reads section headers, symbol/string tables, section-name strings, and relocation tables.
- PROGBITS/NOBITS sections are mapped into separate text, data, and rodata VM regions, with symbols adjusted to their loaded addresses.
- Local relocations happen during `kobj_load()`; undefined globals are resolved and global relocations are applied later by `kobj_affix()`.
- `kobj_affix()` renames the object, checks for symbol conflicts, applies global relocations, registers ksyms, jettisons relocation/header data, calls machine-dependent finalization, and changes text/rodata protections.
- `kobj_unload()` closes sources, frees relocation/header/symbol/string data, unregisters ksyms, calls machine-dependent unload notifications, and frees mapped segments.

Risks and notes:
- Only one symbol table is supported; weak undefined symbols are rejected.
- Duplicate global definitions are rejected except for selected linker-generated boundary symbols.
- Error paths unload the whole object.
- Non-`MODULAR` builds provide stubs that return `ENOSYS` or panic for impossible module operations.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/sys/kern/subr_kobj.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/sys/kern/subr_kobj_vfs.c -->
# File Research: sources/os/bsd/netbsd-src/sys/kern/subr_kobj_vfs.c

Read completely: 199 lines.

Provides the VFS-backed object source for the kobj loader when `MODULAR` is enabled. `kobj_load_vfs()` opens a path with `vn_open()`, initializes a `kobj_t` as `KT_VNODE`, installs VFS read/close callbacks, and calls `kobj_load()`.

Core behavior:
- `kobj_read_vfs()` optionally allocates a buffer, or reads directly into already mapped text/data/rodata segment memory.
- Reads use `vn_rdwr()` with `IO_NODELOCKED`; short reads are treated as `EINVAL`.
- `kobj_close_vfs()` unlocks and closes the vnode.
- Paths without a slash are rejected with `ENOENT`.
- Non-modular builds return `ENOSYS`.

Risks and notes:
- DIAGNOSTIC builds verify non-allocated read targets lie inside dedicated text/data/rodata segments.
- `nochroot` controls whether `vn_open()` uses `NOCHROOT`.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/sys/kern/subr_kobj_vfs.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/sys/kern/subr_localcount.c -->
# File Research: sources/os/bsd/netbsd-src/sys/kern/subr_localcount.c

Read completely: 291 lines.

Implements `localcount(9)`, a CPU-local reference-counting scheme optimized for cheap acquire/release and expensive drain. Each object owns a percpu counter and an optional global total pointer used only while draining.

Core behavior:
- `localcount_init()` allocates the percpu counter storage.
- `localcount_acquire()` increments the current CPU's counter without interprocessor synchronization.
- `localcount_release()` normally decrements the current CPU counter; during drain it decrements the shared total under the caller-provided interlock and wakes the caller-provided CV when zero.
- `localcount_drain()` marks the object draining, broadcasts an xcall to aggregate all per-CPU counts into a stack total, then waits for the total to reach zero.
- `localcount_fini()` frees percpu storage after drain.
- DEBUG/LOCKDEBUG builds maintain a diagnostic total reference count.

Risks and notes:
- Callers must prevent new acquisitions before draining.
- The same CV and interlock must be used for drain and release.
- Release disables preemption so a racing drain cannot miss the CPU-local decrement/wakeup transition.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/sys/kern/subr_localcount.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/sys/kern/subr_lockdebug.c -->
# File Research: sources/os/bsd/netbsd-src/sys/kern/subr_lockdebug.c

Read completely: 1096 lines.

Implements shared lock-debugging infrastructure for NetBSD lock primitives. With `LOCKDEBUG`, each initialized lock can get a `lockdebug_t` record stored in an RB tree by lock address and tracked on per-LWP or per-CPU held-lock lists.

Core behavior:
- `lockdebug_alloc()` allocates and registers a debug record at lock initialization, using an early static batch and later kmem-allocated batches.
- `lockdebug_free()` removes a record at lock destruction and panics if the lock is still held or shared.
- `lockdebug_wantlock()`, `lockdebug_locked()`, and `lockdebug_unlocked()` track attempted, acquired, and released locks, detecting recursion, interrupt-context sleep-lock acquisition, wrong-owner unlock, double-lock, and unlock-without-lock errors.
- `lockdebug_barrier()` verifies no unexpected spin/sleep/shared locks are held at barrier points.
- `lockdebug_mem_check()` checks whether a memory region being freed contains an active lock.
- DDB helpers print one lock, all locks by LWP/CPU, stack traces, and aggregate lock stats.
- `lockdebug_abort()` provides a fallback diagnostic path even without full `LOCKDEBUG`.

Concurrency and risks:
- Global modification uses `ld_mod_lk`; RB-tree lookup is protected through per-CPU lockdebug locks.
- The allocator must avoid unbounded recursion because allocating debug records can itself initialize locks.
- Once a lockdebug panic starts, `ld_panic` suppresses further diagnostics because state may be stale.
- KCOV is silenced around some lookup/memory-check paths to avoid instrumentation recursion.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/sys/kern/subr_lockdebug.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/sys/kern/subr_log.c -->
# File Research: sources/os/bsd/netbsd-src/sys/kern/subr_log.c

Read completely: 547 lines.

Implements the kernel message-buffer device and sysctls backing `/dev/klog` style access. It manages the circular `kern_msgbuf`, blocking reads, poll/select/kqueue readiness, async SIGIO notification, and `kern.msgbuf*` sysctls.

Core behavior:
- `initmsgbuf()` validates or initializes the persistent ring buffer and enables logging.
- `loginit()` initializes locks, CV/select state, softint, and `kern.msgbufsize`/`kern.msgbuf`.
- `logopen()` enforces a single open reader and sets the async owner to the opener's process.
- `logread()` waits for available bytes unless nonblocking, copies ring contents out in small chunks, and advances `msg_bufr`.
- `logpoll()` and `logkqfilter()` report readable data through select/poll/kqueue.
- `logputchar()` appends one character to the ring, dropping oldest data up to the next line when full.
- `logwakeup()` notifies waiters and schedules SIGIO delivery if async mode is enabled.
- `sysctl_msgbuf()` returns buffer size or a full ring snapshot.

Risks and notes:
- `msg_magic` corruption disables message-buffer logging rather than panicking.
- Sysctl buffer snapshots copy mostly unlocked after grabbing write/end positions.
- Async ownership uses fown helpers, while `FIOASYNC` updates `log_async` without full locking because it is treated as thread-private.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/sys/kern/subr_log.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/sys/kern/subr_lwp_specificdata.c -->
# File Research: sources/os/bsd/netbsd-src/sys/kern/subr_lwp_specificdata.c

Read completely: 139 lines.

Wraps the generic `specificdata(9)` facility to provide LWP-specific kernel data. A single domain is created by `lwpinit_specificdata()`, and subsystem keys can be created/deleted with optional destructors.

Core behavior:
- `lwp_initspecific()` initializes a new LWP's specific-data reference.
- `lwp_finispecific()` finalizes it and runs destructors as appropriate through the generic facility.
- `lwp_getspecific()` and `lwp_setspecific()` access the current LWP's data.
- `_lwp_getspecific_by_lwp()` and `lwp_setspecific_by_lwp()` access a supplied LWP.

Risks and notes:
- The file explicitly states LWP-specific data is not interlocked.
- An LWP should normally access only its own data; callers accessing another LWP must guarantee no concurrent get/set inconsistency.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/sys/kern/subr_lwp_specificdata.c -->