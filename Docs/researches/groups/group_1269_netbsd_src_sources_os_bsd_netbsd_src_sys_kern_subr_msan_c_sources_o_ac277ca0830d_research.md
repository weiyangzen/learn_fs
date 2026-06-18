# Group Research: group_1269_netbsd_src_sources_os_bsd_netbsd_src_sys_kern_subr_msan_c_sources_o_ac277ca0830d

Scope: `Docs/research_subset_a.md`. This grouped report covers the listed NetBSD kernel support files under `sources/os/bsd/netbsd-src/sys/kern/`. Each source file was read completely and is reported in its own marker-delimited section for deterministic splitting into source-tree-aligned reports.

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/sys/kern/subr_msan.c -->
# File Research: sources/os/bsd/netbsd-src/sys/kern/subr_msan.c

## Purpose
Implements the machine-independent part of NetBSD KMSAN, the kernel memory sanitizer runtime used by compiler instrumentation to track uninitialized-memory shadow/origin metadata. It supplies compiler ABI entry points, kernel wrapper hooks for memory/string/user-copy/atomic/bus/DMA operations, and report formatting for detected uninitialized reads.

## Main Entry Points
- `kmsan_init()`, `kmsan_shadow_map()`, `kmsan_lwp_alloc()`, `kmsan_lwp_free()`, `kmsan_intr_enter()`, `kmsan_intr_leave()`, and `kmsan_softint()` initialize global KMSAN state, per-LWP TLS contexts, interrupt nesting contexts, and shadow/origin mappings.
- `kmsan_mark()`, `kmsan_orig()`, `kmsan_check_mbuf()`, and `kmsan_check_buf()` expose kernel-facing marking/checking helpers.
- Compiler ABI functions include `__msan_metadata_ptr_for_load_n`, `__msan_metadata_ptr_for_store_n`, fixed-size metadata variants, `__msan_get_context_state()`, `__msan_poison_alloca()`, `__msan_unpoison_alloca()`, `__msan_instrument_asm_store()`, `__msan_chain_origin()`, and `__msan_warning()`.
- Wrapper functions include `kmsan_memcpy`, `kmsan_memset`, `kmsan_memmove`, `kmsan_memcmp`, string routines, `kmsan_kcopy`, `kmsan_copyin`, `kmsan_copyout`, `kmsan_copyinstr`, `kmsan_copyoutstr`, user fetch/store/CAS wrappers, generated atomic wrappers, bus-space read/write wrappers, and DMA sync/load helpers.

## Control Flow And State
The core helpers translate kernel addresses to shadow and origin metadata through MD hooks from `<machine/msan.h>`. Unsupported or disabled regions use dummy shadow/origin pages so compiler instrumentation can continue without touching invalid metadata. Shadow bytes mark initialized/uninitialized state; origin words encode stack/kmem/malloc/pool/uvm origin type plus either a program counter or stack descriptor.

Reports are guarded by `kmsan_reporting`, `panicstr`, and DDB activity to avoid recursion. Reporting decodes origins, optionally resolves symbols under a pserialize read section, prints via `kprintf` or `panic` depending on `KMSAN_PANIC`, unwinds with `kmsan_md_unwind()`, and releases the reporting guard.

Per-LWP sanitizer state is `msan_lwp_t`, holding a small stack of TLS contexts for normal and interrupt execution. `kmsan_enabled` gates all runtime work. `msan_lwp0` seeds the bootstrap LWP.

## Integration Points
Depends on machine-dependent KMSAN address/origin routines, kernel symbol lookup, pserialize, kprintf, copyin/copyout, atomics, bus space APIs, mbufs, bufs, uio, and bus DMA maps. `subr_pool.c` calls into KMSAN to poison/unpoison pool allocations.

## Risks And Notes
Correctness depends on exact compiler ABI names and on keeping wrappers semantically identical to the real kernel routines. Missing a wrapper can create false positives or false negatives. Origin handling assumes MD metadata mappings are valid for supported addresses. DMA and bus-space hooks intentionally mark post-read data initialized and check pre-write data, so wrong `dm_buftype` or sync flags can hide real bugs.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/sys/kern/subr_msan.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/sys/kern/subr_once.c -->
# File Research: sources/os/bsd/netbsd-src/sys/kern/subr_once.c

## Purpose
Provides the backing implementation for NetBSD one-time initialization/finalization objects used by `RUN_ONCE()`-style kernel code.

## Main Entry Points
- `once_init()` initializes the global mutex and condition variable.
- `_init_once()` runs an initializer function exactly once for the first reference, records its error, and returns the stored error to all callers.
- `_fini_once()` decrements the reference count and runs a finalizer when the last user releases the once object.

## Control Flow And State
All once objects share `oncemtx` and `oncecv`. `_init_once()` waits while the object is `ONCE_RUNNING`, increments `o_refcnt`, and when transitioning from zero references marks the object running, drops the lock, calls the initializer, records `o_error`, marks `ONCE_DONE`, and wakes waiters. Other callers wait for any running transition and then return `o_error`.

`_fini_once()` similarly waits for active initialization/finalization, asserts there is a reference to release, and when the count reaches zero marks running, drops the lock, calls the finalizer, resets status to `ONCE_VIRGIN`, and broadcasts.

## Dependencies
Uses kernel mutexes, condition variables, and `once_t` state from `<sys/once.h>`.

## Risks And Notes
Initializer/finalizer callbacks run without `oncemtx`, avoiding deadlock but requiring callbacks to provide their own synchronization for external state. `KASSERT(o_refcnt != 0)` catches overflow after increment and invalid finalization before initialization. A failed initializer still transitions to `ONCE_DONE`; future callers receive the stored error rather than retrying until `_fini_once()` resets the object.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/sys/kern/subr_once.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/sys/kern/subr_optstr.c -->
# File Research: sources/os/bsd/netbsd-src/sys/kern/subr_optstr.c

## Purpose
Parses kernel option strings of the form `key=value key2=value2` and extracts values as strings, numbers, or Ethernet MAC addresses.

## Main Entry Points
- `optstr_get()` copies a matched value into a caller buffer.
- `optstr_get_string()` returns a pointer into the original option string.
- `optstr_get_number()`, `optstr_get_number_hex()`, and `optstr_get_number_binary()` parse values in base 10, 16, and 2.
- `optstr_get_macaddr()` is compiled when `NETHER > 0` and parses an Ethernet address through `ether_aton_r()`.

## Control Flow And State
The private `optstr_get_pointer()` skips leading spaces and tabs, scans words separated by spaces, matches an exact key immediately followed by `=`, and returns a pointer to the value after the equal sign. It does not allocate or mutate state. String copy stops at space or NUL and always writes a terminating NUL if the key is found.

Numeric helpers call `strtoul` with the requested base and fail if no digits were consumed. The MAC helper parses into a temporary array before copying to the caller output.

## Dependencies
Uses `<sys/optstr.h>`, kernel string helpers, `strtoul`, and optionally Ethernet parsing/types when network Ethernet support is present.

## Risks And Notes
The scanner treats only spaces as separators after the initial tab-skip logic; tabs inside the option list are not skipped as separators. `optstr_get_string()` returns a pointer into the original string and does not bound the value length. Numeric parsers do not require the whole value token to be consumed, so trailing nonnumeric characters after at least one digit are accepted.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/sys/kern/subr_optstr.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/sys/kern/subr_pcq.c -->
# File Research: sources/os/bsd/netbsd-src/sys/kern/subr_pcq.c

## Purpose
Implements a lockless producer/consumer queue for many concurrent producers and a caller-serialized single consumer.

## Main Entry Points
- `pcq_create()` allocates a queue with up to `PCQ_MAXLEN` slots.
- `pcq_destroy()` frees the queue.
- `pcq_put()` reserves and publishes an item.
- `pcq_peek()` reads the next item without consuming it.
- `pcq_get()` consumes the next published item.
- `pcq_maxitems()` returns the configured capacity.

## Control Flow And State
`struct pcq` stores `pcq_nitems`, a packed 32-bit producer/consumer cursor `pcq_pc`, and a flexible array of item slots separated onto cache lines. The low 16 bits hold the producer cursor and the high 16 bits hold the consumer cursor.

`pcq_put()` CAS-loops on `pcq_pc` to reserve the next producer position, returns false if advancing would collide with the consumer, and then publishes the item with `atomic_store_release`. `pcq_get()` snapshots cursors, returns NULL if empty or if a producer reserved but has not yet published the item, consumes the item by clearing the slot, issues a producer barrier, and CAS-loops to advance the consumer cursor. `pcq_peek()` uses a consume load of the item slot.

## Dependencies
Uses NetBSD atomics, memory barriers, kmem allocation, and queue definitions from `<sys/pcq.h>`.

## Risks And Notes
The concurrency proof depends on the release/consume ordering and the explicit `membar_producer()` before publishing the updated consumer cursor. Multiple consumers are not supported; callers must serialize `pcq_get()`. A transient NULL from `pcq_get()` can mean a producer has reserved a slot but not published yet, so users must rely on the producer's later notification path to retry.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/sys/kern/subr_pcq.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/sys/kern/subr_pcu.c -->
# File Research: sources/os/bsd/netbsd-src/sys/kern/subr_pcu.c

## Purpose
Implements the MI Per CPU Unit framework, used to manage LWP-owned per-CPU hardware context such as FPU state. It coordinates lazy load, save, discard, and release of machine-dependent PCU units across CPU migration and remote ownership.

## Main Entry Points
- `pcu_switchpoint()` releases state when the current LWP switches away from the CPU holding its PCU state.
- `pcu_load()` loads or initializes the current LWP's PCU state on the current CPU.
- `pcu_discard_all()`, `pcu_save_all()`, `pcu_discard()`, `pcu_save()`, and `pcu_save_all_on_cpu()` manage state during exec, exit, coredump, explicit discard/save, and CPU-local flushing.
- `pcu_valid_p()` reports whether an LWP's state for a unit is considered valid.

## Control Flow And State
The file is compiled only when `PCU_UNIT_COUNT > 0`. Per-unit state is tracked in `lwp_t::l_pcu_valid`, `lwp_t::l_pcu_cpu[id]`, and `cpu_info::ci_pcu_curlwp[id]`. Machine-dependent operations come from `pcu_ops_md_defs[id]`.

All state transitions happen at `splpcu()`/high IPL. If a target state is local, `pcu_do_op()` calls MD save/release callbacks directly. If the state resides on a remote CPU, `pcu_lwp_op()` sends an IPI to run `pcu_cpu_ipi()`, waits for completion, and handles races where ownership changed first. `pcu_load()` saves/releases any remote state for the current LWP, evicts any other LWP currently loaded on this CPU, then calls the MD load callback with `PCU_VALID` or fresh-state flags and records ownership.

## Dependencies
Depends on MD `pcu_ops_t` callbacks, CPU/LWP fields, IPL/IPI infrastructure, and scheduler context-switch hooks.

## Risks And Notes
The framework's invariants are strict: only the current CPU may mutate `ci_pcu_curlwp[id]`, and only the CPU holding loaded state may clear `l_pcu_cpu[id]`. Incorrect MD callbacks or missing high-IPL protection can corrupt lazy hardware context. Several assertions encode special cases for system LWPs, suspended LWPs, and failed LWP creation paths.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/sys/kern/subr_pcu.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/sys/kern/subr_percpu.c -->
# File Research: sources/os/bsd/netbsd-src/sys/kern/subr_percpu.c

## Purpose
Implements dynamically allocated per-CPU storage with optional constructors/destructors, remote traversal, and xcall-based per-CPU callbacks.

## Main Entry Points
- `percpu_init()` creates the offset arena and global locks.
- `percpu_init_cpu()` allocates storage for a CPU and runs constructors for existing per-CPU objects.
- `percpu_alloc()`, `percpu_create()`, and `percpu_free()` allocate/free per-CPU regions.
- `percpu_getref()` and `percpu_putref()` access current-CPU data with preemption disabled.
- `percpu_traverse_enter()`, `percpu_traverse_exit()`, `percpu_getptr_remote()`, `percpu_foreach()`, and `percpu_foreach_xcall()` support remote traversal and callbacks.

## Control Flow And State
`struct percpu` records offset, size, optional ctor/dtor, cookie, and a list entry for objects with constructors. `percpu_offset_arena` hands out offsets; its import callback grows every CPU's `percpu_cpu_t` backing buffer. Growth allocates a new buffer per CPU and swaps it in via `percpu_cpu_swap()` locally or through an xcall, copying old data while interrupts are blocked so interrupt handlers cannot lose updates.

`percpu_swap_lock` protects stable remote traversal: growth takes it as writer, traversal as reader. Constructor list access is serialized by `percpu_allocation.lock`, `busy`, and `cv` so CPU initialization and new per-CPU object creation do not race while running callbacks.

## Dependencies
Uses kmem, vmem, CPU iteration, kernel preemption controls, rwlocks, mutexes/condition variables, and xcall infrastructure.

## Risks And Notes
Allocation/free are explicitly expensive and sleepable. Callback contracts matter: `percpu_foreach()` runs callbacks under the traversal lock on the current CPU and callbacks must be short and non-sleeping for allocations; `percpu_foreach_xcall()` runs in soft-interrupt context. Remote pointers are safe only inside traverse sections or when accessing the current CPU with preemption disabled.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/sys/kern/subr_percpu.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/sys/kern/subr_physmap.c -->
# File Research: sources/os/bsd/netbsd-src/sys/kern/subr_physmap.c

## Purpose
Builds compact physical segment lists from virtual address ranges, iovecs, or `vm_page` arrays, and provides helpers to temporarily map those physical segments into kernel virtual address space when needed.

## Main Entry Points
- `physmap_create_linear()` creates a physmap for a locked linear virtual range.
- `physmap_create_iov()` creates a physmap from a locked iovec array.
- `physmap_create_pagelist()` creates a physmap from an array of `vm_page` pointers.
- `physmap_destroy()` frees a physmap.
- `physmap_map_init()`, `physmap_map()`, and `physmap_map_fini()` iterate through temporary KVA mappings for physmap segments.
- `physmap_zero()` maps segments and zeroes a requested range.

## Control Flow And State
`physmap_alloc()` allocates a variable-sized `physmap_t` with room for the maximum possible segments. `physmap_fill()` walks virtual pages through `pmap_extract()`, coalescing physically contiguous pages into fewer segments while preserving offsets and lengths. Linear and iovec creation assume callers have already locked pages into memory.

Mapping uses a `physmap_cookie_t` cursor. `physmap_map_init()` skips to the segment containing the requested offset. Each `physmap_map()` releases the previous non-direct KVA mapping, advances to the next segment, tries MD direct mapping when available, and otherwise allocates VA-only kernel_map space, enters physical mappings with the requested protection, updates the pmap, and returns a KVA plus segment length. `physmap_map_fini()` removes the last temporary mapping and frees the cookie.

## Dependencies
Uses pmap extraction and kernel mappings, UVM page/KVA APIs, optional `mm_md_direct_mapped_phys()`, kmem, and physmap types from `<sys/physmap.h>`.

## Risks And Notes
Creation fails with `EFAULT` if any virtual page cannot be translated. Callers must supply locked/pinned backing pages for virtual ranges. `physmap_zero()` assumes each `physmap_map()` call yields a nonzero segment length until the requested length is exhausted. Temporary KVA mappings must be finalized to avoid leaking VA space.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/sys/kern/subr_physmap.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/sys/kern/subr_pool.c -->
# File Research: sources/os/bsd/netbsd-src/sys/kern/subr_pool.c

## Purpose
Implements NetBSD's general fixed-size kernel pool allocator and the higher-level pool cache object allocator. It manages pages split into fixed-size items, per-CPU magazines/cache groups, low/high/hard water marks, reclaim/drain paths, diagnostics, KMSAN/KASAN/redzone integration, and `kern.pool` sysctl statistics.

## Main Entry Points
- Pool lifecycle and allocation: `pool_subsystem_init()`, `pool_init()`, `pool_destroy()`, `pool_get()`, `pool_put()`, `pool_prime()`, `pool_setlowat()`, `pool_sethiwat()`, `pool_sethardlimit()`, `pool_reclaim()`, `pool_drain()`, `pool_totalpages()`, and `pool_totalpages_locked()`.
- Pool cache lifecycle and operations: `pool_cache_init()`, `pool_cache_bootstrap()`, `pool_cache_destroy()`, `pool_cache_bootstrap_destroy()`, `pool_cache_get_paddr()`, `pool_cache_put_paddr()`, `pool_cache_invalidate()`, `pool_cache_reclaim()`, and setter/stat wrappers.
- Backend allocators: `pool_page_alloc()`, `pool_page_free()`, metadata-page variants, standard allocator structs, and large-object allocator selection.
- Diagnostics: `pool_printall()`, `pool_printit()`, `pool_chk()`, optional DDB `pool_whatis()`, and `pool_sysctl()`.

## Control Flow And State
Pools keep pages on empty, full, and partially full lists. A page header may live in the page (`PR_PHINPAGE`) or in a private page-header pool; free items are tracked either by bitmap (`PR_USEBMAP`) or linked list. `pool_get()` enforces context and wait flags, checks hard limits, grows the pool if `pr_curpage` is empty, removes an item, updates page lists and counters, optionally catches up to low water marks, fills redzones, marks KMSAN origins, and zeroes on `PR_ZERO`. `pool_put()` optionally quarantines the object, checks redzones/freecheck, returns it to a bitmap/list, wakes waiters, and frees whole pages when above limits.

Pool caches layer per-CPU current/previous cache groups over a backing pool. Fast paths run at `splvm()` and avoid locks when current/previous groups have space. Slow get pulls a full group from global lists or allocates/constructs a new object. Slow put obtains an empty group or destructs the object immediately. Invalidation broadcasts xcalls so CPUs transfer local groups to global lists, then destructs cached objects. Lockless cache-group lists use atomic CAS and `pcg_dummy` as a temporary busy marker.

## Integration Points
Depends on UVM/VMEM for page allocation, CPU/xcall APIs, atomics, sysctl, DDB, lockdebug/freecheck, KMSAN, KASAN/ASAN, pserialize barriers for `PR_PSERIALIZE`, and kernel logging. It is itself foundational for many kernel subsystems and has bootstrap pools for page headers and cache metadata.

## Risks And Notes
This file is heavily invariant-driven. Misconfiguring item size, alignment, `PR_NOTOUCH`, `PR_PSERIALIZE`, or allocator page size can break page-header lookup or object lifetime guarantees. Cache invalidation is expensive and prohibited in interrupt context. `POOL_QUARANTINE` disables caching through `POOL_NOCACHE`. Redzone/KASAN modes avoid passive-serialization pools because freed objects may need to remain valid until a barrier. The `kern.pool` sysctl takes references while copying records out to avoid racing destruction.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/sys/kern/subr_pool.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/sys/kern/subr_prf.c -->
# File Research: sources/os/bsd/netbsd-src/sys/kern/subr_prf.c

## Purpose
Implements NetBSD kernel printing, logging, panic reporting, autoconfiguration print helpers, DDB printing, tty/user printing helpers, `snprintf`/`vasprintf`, and the kernel `kprintf` formatter.

## Main Entry Points
- Initialization and locking: `kprintf_init()`, `kprintf_lock()`, and `kprintf_unlock()`.
- Panic/logging: `panic()`, `vpanic()`, `log()`, `vlog()`, `logpri()`, `klogpri()`, `addlog()`, and `tablefull()`.
- Console/TTY APIs: `printf()`, `vprintf()`, `printf_flags()`, `vprintf_flags()`, `printf_tolog()`, `printf_nolog()`, `printf_nostamp()`, `uprintf()`, `uprintf_locked()`, `tprintf_open()`, `tprintf()`, `tprintf_close()`, `ttyprintf()`, and `device_printf()`.
- Autoconfiguration helpers: `aprint_normal*`, `aprint_error*`, `aprint_naive*`, `aprint_verbose*`, `aprint_debug*`, and `aprint_get_error_count()`.
- Formatting APIs: `snprintf()`, `vsnprintf()`, `vasprintf()`, and `kprintf()`.

## Control Flow And State
`kprintf_mtx` serializes console/log/buffer output after early bootstrap. `putchar()` handles timestamp insertion, syslog priority markers, DDB output, entropy collection for `RND_PRINTF`, and dispatches to `putone()`. `putone()` sends characters to the controlling tty, log buffer, or virtual console; it enters pserialize read sections around `constty` access and clears `constty` during panic.

`vpanic()` stops SPL debugging, elects the first panic CPU with atomic CAS, binds/offlines scheduling state to keep other CPUs out, formats and records `panicstr`, optionally enters KGDB/DDB, and reboots with dump flags depending on `dumponpanic` and recursive shutdown state.

`kprintf()` is a compact integer/string formatter supporting flags, width, precision, length modifiers, bases, pointers, and strings. `%n` is intentionally consumed but produces no output. `vsnprintf()` uses `TOBUFONLY` and then NUL-terminates according to returned length.

## Dependencies
Touches console drivers, msgbuf/log wakeups, tty/session/proc state, pserialize, device and ifnet naming, boot flags, DDB/KGDB, reboot/dump policy, syslog priorities, random source collection, and kmem for `vasprintf`.

## Risks And Notes
Printing is used in panic and interrupt-adjacent paths, so recursion and locking order matter. Some user/tty print helpers intentionally avoid the global kprintf mutex when writing only to a tty. Timestamp precision is clamped to 0-9. The formatter is not full libc `printf`; unsupported/unsafe features such as `%n` are suppressed, and floating point is not implemented despite internal flag names.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/sys/kern/subr_prf.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/sys/kern/subr_prof.c -->
# File Research: sources/os/bsd/netbsd-src/sys/kern/subr_prof.c

## Purpose
Provides kernel and user profiling support. When `GPROF` is enabled it allocates and exposes kernel gprof buffers through `kern.profiling`; regardless of `GPROF`, it implements the `profil(2)` syscall and profile tick accounting for user processes.

## Main Entry Points
- Under `GPROF`: `kmstartup()` allocates kernel profiling buffers; `sysctl_kern_profiling()` serves and updates profiling sysctls; `sysctl_kern_gprof_setup` creates the sysctl tree; `prof_set_state_xc()` updates per-CPU state on MP builds.
- User profiling: `sys_profil()` configures a process profiling buffer and starts/stops the profiling clock.
- Tick handling: `addupc_intr()` records pending profile ticks from interrupt context and schedules an AST; `addupc_task()` performs faultable user-buffer updates later.

## Control Flow And State
`kmstartup()` computes text bounds, histogram/from/to buffer sizes, and either allocates a single buffer set or per-CPU `struct gmonparam` blocks on multiprocessor kernels. MP builds expose per-CPU sysctl subtrees and can merge per-CPU data for global reads. Sysctl writes to state start/stop `proc0`'s profiling clock and broadcast/unicast state changes to CPUs; writes to global profiling arrays propagate data to per-CPU arrays.

`sys_profil()` validates fixed-point scale, disables profiling for scale zero, or installs base/size/offset/scale under the process statistics mutex. `addupc_intr()` checks range under the same mutex, drops it to update pending tick fields, and requests a profiling AST. `addupc_task()` later copies the 16-bit sample counter from user memory, adds ticks, writes it back, and disables profiling on copy failure.

## Dependencies
Uses gprof structures, malloc type `M_GPROF`, sysctl, CPU iteration and xcalls, process statistics locks, profile clocks, copyin/copyout, AST/profile tick hooks, and optional multiprocessor support.

## Risks And Notes
MP kernel profiling has compatibility behavior where global `_gmonparam.state` can override per-CPU state. Merged reads allocate temporary profiling storage and can fail with `ENOMEM`. User profiling intentionally may lose ticks if AST delivery lags. Failed user buffer access in `addupc_task()` stops profiling rather than retrying.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/sys/kern/subr_prof.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/sys/kern/subr_pserialize.c -->
# File Research: sources/os/bsd/netbsd-src/sys/kern/subr_pserialize.c

## Purpose
Implements passive serialization: very cheap read-side sections with an expensive write-side barrier that waits for all CPUs to pass a quiescent point.

## Main Entry Points
- `pserialize_init()` initializes global write-side locking.
- `pserialize_create()` and `pserialize_destroy()` allocate/free opaque passive serialization objects.
- `pserialize_perform()` performs the write-side synchronization barrier.
- `pserialize_read_enter()` and `pserialize_read_exit()` bracket read-side sections.
- `pserialize_in_read_section()` and `pserialize_not_in_read_section()` provide diagnostic predicates.

## Control Flow And State
The opaque `struct pserialize` currently contains only a dummy byte; serialization state is effectively global. Read enter raises to `splsoftserial()`, increments the current CPU's `ci_psz_read_depth`, and returns the previous priority for exit. Read exit asserts preemption is disabled in non-cold paths, decrements the depth with mismatch panic protection, and restores priority.

`pserialize_perform()` refuses interrupt/softint context, returns immediately during panic, counts an exclusive event directly when multiprocessor is not online, and otherwise issues a high-priority xcall barrier to all CPUs. It then briefly takes `psz_lock` to increment the event counter, serializing write-side accounting.

## Dependencies
Uses CPU per-CPU fields, SPL softserial, xcall barriers, kmem, mutexes, evcnt, panic/mp state, and LWP preemption counters.

## Risks And Notes
The API relies on read sections preventing preemption. `pserialize_not_in_read_section()` samples `lwp_pctr()` around the per-CPU depth check to account for context switches. Write-side barriers are intentionally expensive; frequent writers should use another synchronization primitive.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/sys/kern/subr_pserialize.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/sys/kern/subr_psref.c -->
# File Research: sources/os/bsd/netbsd-src/sys/kern/subr_psref.c

## Purpose
Implements passive references: CPU-local references that are cheap to acquire/release and expensive to drain, intended for objects whose destruction can wait for xcall-based global checks.

## Main Entry Points
- `psref_init()` initializes optional debug LWP-specific state.
- `psref_class_create()` and `psref_class_destroy()` manage reference classes.
- `psref_target_init()` and `psref_target_destroy()` initialize and drain/destroy reference targets.
- `psref_acquire()`, `psref_release()`, and `psref_copy()` manage individual stack-allocated `struct psref` references.
- `psref_held()` is a diagnostic predicate; `psref_debug_init_lwp()` and `psref_debug_barrier()` are available with `PSREF_DEBUG`.

## Control Flow And State
Each class owns a mutex/CV, a per-CPU `struct psref_cpu` list, an IPL cookie, and xcall flags. Acquiring a reference asserts the caller cannot migrate CPUs unless it is in softint or bound LWP context, raises to the class IPL, gets the current CPU's per-CPU list, inserts the `psref`, records target/LWP/CPU, and drops the per-CPU reference. Release performs matching target/LWP/CPU checks, removes from the current CPU list, updates diagnostic counters, and broadcasts if the target is draining.

Destroying a target sets `prt_draining` so new acquires assert, then repeatedly broadcasts a high-priority class xcall. Each CPU runs `_psref_held()` to see whether its local list contains the target. If any reference remains, the destroyer timed-waits on the class CV and retries until all references are gone, then clears `prt_class`.

## Dependencies
Built on `percpu`, xcalls, IPL raising, mutex/CV, LWP and CPU identity, SLIST queues, and optional LWP-specific debug storage.

## Risks And Notes
Passive references must not move across CPUs or LWPs; the code has explicit assertions for both. Callers must remove targets from discoverable data structures before `psref_target_destroy()` so no new references can be acquired. Target initialization requires the caller to publish with a producer memory barrier before other CPUs can find the target. Debug mode tracks per-LWP held references and can panic on leaks at barriers.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/sys/kern/subr_psref.c -->