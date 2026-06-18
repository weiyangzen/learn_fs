# Group Research: group_414_freebsd_src_sources_os_bsd_freebsd_src_sys_kern_kern_malloc_c_source_13552e16e7c0

Scope checked against `Docs/research_subset_a.md`: all requested files are under `sources/os/bsd/freebsd-src`, which is included in subset A. All listed source files were read completely.

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sys/kern/kern_malloc.c -->
# File Research: sources/os/bsd/freebsd-src/sys/kern/kern_malloc.c

Read completely: 1622 lines.

## Purpose
Implements FreeBSD's general-purpose kernel `malloc(9)` allocator on top of UMA, including fixed-size small allocation zones, page-backed large allocations, contiguous allocations, malloc type registration, per-CPU accounting, debugging hooks, and sysctl/DDB reporting.

## Main Elements
- Defines common malloc types `M_CACHE`, `M_DEVBUF`, and `M_TEMP`.
- Maintains `kmemzones[]` bucket zones from 16 bytes through 65536 bytes, with `kmemsize[]` mapping request sizes to zone indexes.
- `malloc()`, `malloc_domainset()`, `malloc_exec()`, `malloc_aligned()`, `mallocarray()`, and domain-aware variants allocate memory with type accounting.
- `free()`, `zfree()`, `realloc()`, `reallocf()`, `malloc_size()`, and `malloc_usable_size()` implement the normal allocator API.
- `contigmalloc()` and `contigmalloc_domainset()` allocate physically contiguous kernel memory through `kmem_alloc_contig*()`.
- Large and contiguous allocations are tagged through synthetic slab-cookie values so `free()` can distinguish UMA, large kmem, and contiguous allocations.
- `malloc_type_allocated()`, `malloc_type_freed()`, `malloc_init()`, and `malloc_uninit()` maintain per-type, per-CPU allocation statistics and leak warnings on type destruction.
- `kmeminit()` sizes the kernel memory arena from tunables, physical memory, KASAN/KMSAN shadow overhead, and architecture limits.
- `mallocinit()` initializes the UMA zones and size lookup table at `SI_SUB_KMEM`.
- Sysctls expose kmem sizing, malloc zone sizes/counts, malloc statistics, debug failure injection, and optional multi-zone debug separation.
- DDB support can show malloc type usage sorted by memory use.

## Dependencies And Integration
Uses UMA, kmem, vm domain sets, VM page accounting, KASAN/KMSAN, MemGuard, RedZone, DTrace malloc probes, DDB, sysctl, and the kernel `MALLOC_DEFINE` type framework. It underpins nearly every kernel subsystem in this group, including mbufs, modules, OSD, PMC, physio, and mutex pool allocation.

## Risk Notes
Allocator correctness depends on exact flag/context rules: `M_WAITOK` cannot be used from interrupt or sleep-prohibited contexts, sleep/spin critical sections are rejected under debug builds, and `M_EXEC` is forced down the large-allocation path. Slab-cookie tagging is central to safe `free()` and `malloc_usable_size()` behavior. `realloc()` intentionally does not fully rebalance per-type statistics for reused/copy paths, as noted in the source.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sys/kern/kern_malloc.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sys/kern/kern_mbuf.c -->
# File Research: sources/os/bsd/freebsd-src/sys/kern/kern_mbuf.c

Read completely: 1815 lines.

## Purpose
Implements FreeBSD mbuf and mbuf-cluster allocation, packet mbuf zones, jumbo clusters, external storage reference cleanup, unmapped external-page mbufs, send tags, receive-interface serialization, and debugnet emergency mbuf pools.

## Main Elements
- Tunables and sysctls manage `nmbufs`, `nmbclusters`, jumbo cluster limits, `maxmbufmem`, `mb_use_ext_pgs`, and active send-tag count.
- `mbuf_init()` creates UMA zones for mbufs, 2K clusters, packet mbufs, page-size jumbo clusters, 9K jumbo clusters, and 16K jumbo clusters.
- Constructors/destructors `mb_ctor_mbuf()`, `mb_ctor_clust()`, `mb_ctor_pack()`, `mb_dtor_mbuf()`, and `mb_dtor_pack()` initialize normal, cluster-backed, and packet-zone mbufs.
- `mb_zinit_pack()` and `mb_zfini_pack()` attach/release packet-zone clusters when objects move between UMA cache and backing keg.
- `m_clget()`, `m_cljget()`, `m_get2()`, `m_get3()`, `m_getjcl()`, `mc_get()`, and `m_getm2()` allocate mbufs and chains sized to caller needs.
- `m_extadd()` attaches caller-provided external storage.
- `m_freem()`, `m_freemp()`, `m_free_raw()`, `mb_free_ext()`, and `mb_free_extpg()` release chains and external backing storage based on `ext_type`.
- `mb_alloc_ext_pgs()`, `mb_alloc_ext_plus_pages()`, `mb_mapped_to_unmapped()`, `mb_unmapped_compress()`, and `mb_unmapped_to_ext()` handle unmapped page-backed mbufs for sendfile/TLS paths and fallback conversion.
- Debugnet support builds preallocated mbuf/cluster cache zones and temporarily swaps global zone pointers during panic-time network I/O.
- `m_snd_tag_*()` wraps interface send-tag lifecycle and accounting.
- `m_rcvif_serialize()` and `m_rcvif_restore()` preserve receive-interface identity across deferred processing.

## Dependencies And Integration
Uses UMA, VM pages, direct-map support, sf_bufs, KTLS, network `ifnet`, NET_EPOCH, eventhandlers, sysctl, counters, debugnet, and mbuf macros from `sys/mbuf.h`. It is core networking infrastructure but also supports kernel I/O paths that need packet buffers, TLS/sendfile page references, and panic-time network dump/debug flows.

## Risk Notes
Reference counting for external storage is subtle: embedded and shared refcounts, `M_NOFREE`, packet-zone special handling, and TLS deferred freeing all have different paths. Unmapped mbufs cannot always be converted, especially TLS mbufs. Debugnet overwrites global zone pointers and relies on careful start/finish pairing. Sysctl limit increases are allowed but shrinking is rejected.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sys/kern/kern_mbuf.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sys/kern/kern_membarrier.c -->
# File Research: sources/os/bsd/freebsd-src/sys/kern/kern_membarrier.c

Read completely: 254 lines.

## Purpose
Implements the `membarrier(2)` system call, providing process/global memory barrier operations and expedited IPI-based barriers for user-space synchronization runtimes.

## Main Elements
- Defines supported command mask for query, global, global expedited, private expedited, private sync-core expedited, registration, and registration query commands.
- `membarrier_action_seqcst()` executes a sequentially consistent fence.
- `membarrier_action_seqcst_sync_core()` executes a sequentially consistent fence plus `cpu_sync_core()`.
- `do_membarrier_ipi()` fences locally, rendezvous-calls selected CPUs, then fences again.
- `check_cpu_switched()` tracks CPU switch timestamps so non-expedited global barriers can wait until every CPU has either switched or is idle.
- `kern_membarrier()` validates flags/commands, handles registration bits in `p_flag2`, selects CPU masks through all CPUs or `pmap_active_cpus()`, and returns registered command state.
- `sys_membarrier()` is the syscall wrapper.

## Dependencies And Integration
Uses cpusets, SMP rendezvous, scheduler pinning, process flags, thread/pcpu state, vmspace pmap active CPU tracking, pause-with-signal handling, and architecture `cpu_sync_core()`.

## Risk Notes
Expedited commands require prior registration or return `EPERM`. Private expedited commands rely on pmap active CPU masks and architecture assumptions about syscall return after context switches. The global non-expedited path allocates per-CPU switch timestamp storage and may sleep/retry until all CPUs satisfy the ordering condition.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sys/kern/kern_membarrier.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sys/kern/kern_mib.c -->
# File Research: sources/os/bsd/freebsd-src/sys/kern/kern_mib.c

Read completely: 785 lines.

## Purpose
Defines core FreeBSD sysctl MIB roots and many fundamental kernel, hardware, user, compatibility, feature, host identity, jail-visible, and ABI-reporting sysctls.

## Main Elements
- Creates root nodes: `sysctl`, `kern`, `vm`, `vfs`, `net`, `debug`, `hw`, `machdep`, `user`, `p1003_1b`, `compat`, `security`, and optional `regression`.
- Exposes kernel identity, version, compiler version, OS type, process limits, `ARG_MAX`, POSIX feature constants, group limits, boot file, and `maxphys`.
- `sysctl_kern_arnd()` returns random bytes and explicitly zeroes its temporary buffer.
- Hardware sysctls report CPU count, byte order, page size, physical memory, firmware memory, user memory, available pages, and supported page sizes.
- ABI helpers report `hw.machine_arch` adaptively based on the calling process and `kern.supported_archs`.
- `sysctl_hostname()` handles jail-aware hostname, NIS domain, and host UUID reads/writes.
- `sysctl_kern_securelvl()` enforces monotonic securelevel increases across jail descendants, except in regression mode.
- `sysctl_hostid()`, `sysctl_bootid()`, `sysctl_osrelease()`, and `sysctl_osreldate()` expose jail-scoped host ID, random boot ID, OS release, and OS release date.
- `sysctl_build_id()` extracts and formats the ELF build-id note.
- Defines `kern.features.*` compatibility feature flags.
- Defines POSIX/user limit placeholder sysctls and `user.localbase`.
- Adds `debug.sizeof.*` entries for kernel structs including vnode, proc, bio, buf, kinfo_proc, and pcb.
- `sysctl_kern_pid_max()` validates and updates `pid_max` under process-list locks.
- Provides compatibility `kern.fallback_elf_brand`.

## Dependencies And Integration
Integrates with sysctl, jails/prisons, random subsystem, SMP globals, VM memory counters, process locks, ABI/sysent hooks, ELF build metadata, and compatibility options. The `vfs` root created here is the top-level sysctl namespace used by filesystem code.

## Risk Notes
Several sysctls are jail-aware and must preserve prison inheritance rules. Securelevel lowering is intentionally rejected outside regression builds. `boot_id` is unavailable until random seeding succeeds. ABI-adaptive `machine_arch` can change reported values depending on the caller's binary ABI.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sys/kern/kern_mib.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sys/kern/kern_module.c -->
# File Research: sources/os/bsd/freebsd-src/sys/kern/kern_module.c

Read completely: 569 lines.

## Purpose
Implements the kernel module registry: module registration, load/unload/quiesce/shutdown event dispatch, reference counting, per-linker-file module ordering, and userland module enumeration/stat syscalls.

## Main Elements
- `struct module` stores global/file list links, owning linker file, reference count, numeric ID, name, event handler, private arg, and module-specific data.
- `module_init()` initializes `modules_sx`, the global module list, and shutdown event handling.
- `module_shutdown()` walks modules in reverse order and sends `MOD_SHUTDOWN`.
- `module_register()` allocates and inserts a module, assigns a unique ID, checks for duplicate names, and links into the containing linker file.
- `module_register_init()` locates the module, invokes `MOD_LOAD`, unwinds on failure, and reorders file-local modules so unload happens in reverse load order.
- `module_reference()` and `module_release()` manage references and free zero-ref modules.
- Lookup/accessor helpers expose module lookup by name/id, next-in-file, name, ID, specific data, and owning linker file.
- `module_quiesce()` and `module_unload()` dispatch module events under Giant.
- Syscalls `modnext`, `modfnext`, `modstat`, and `modfind` enumerate and inspect loaded modules.
- Compatibility code supports 32-bit `modstat` layout and older v1/v2 structure sizes.
- Declares `MODULE_VERSION(kernel, __FreeBSD_version)`.

## Dependencies And Integration
Uses linker files, KLD startup ordering, sx locks through `MOD_*LOCK` macros, Giant around module event handlers, syscalls/copyin/copyout, shutdown eventhandlers, malloc type `M_MODULE`, and FreeBSD32 compatibility.

## Risk Notes
Module data is copied out after snapshotting under the shared lock, but name pointers are still derived from module state, so lifetime depends on module lock/ref discipline. Event handlers run under Giant, preserving older module assumptions. Duplicate module names are rejected globally, even across different linker files.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sys/kern/kern_module.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sys/kern/kern_mtxpool.c -->
# File Research: sources/os/bsd/freebsd-src/sys/kern/kern_mtxpool.c

Read completely: 186 lines.

## Purpose
Provides shared pools of mutexes selected by pointer hash or round-robin allocation, allowing subsystems to associate short-term leaf locks with objects without embedding a mutex in each object.

## Main Elements
- Defines `struct mtx_pool` with size/mask/shift metadata and a variable-length mutex array.
- Global `mtxpool_sleep` is created during `SI_SUB_MTX_POOL_DYNAMIC`.
- `mtx_pool_find()` maps an arbitrary pointer to a pool mutex using Fibonacci hashing.
- `mtx_pool_create()` validates power-of-two size, allocates the pool, and initializes all mutexes.
- `mtx_pool_destroy()` destroys pool mutexes and frees the pool.
- `mtx_pool_alloc()` returns the next mutex from the pool using an intentionally racy round-robin cursor.

## Dependencies And Integration
Uses kernel malloc, mutex initialization/destruction, cache-line alignment, KTR includes, and SYSINIT. Intended for leaf-level sleep mutex use where structural overhead would be too high.

## Risk Notes
Pool mutexes should be treated as leaf locks because unrelated objects may hash to the same lock and pool-to-pool ordering is not stable. `mtx_pool_next` is intentionally unprotected, which is acceptable only because exact round-robin fairness is not required.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sys/kern/kern_mtxpool.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sys/kern/kern_mutex.c -->
# File Research: sources/os/bsd/freebsd-src/sys/kern/kern_mutex.c

Read completely: 1371 lines.

## Purpose
Implements the machine-independent parts of FreeBSD mutexes, including sleep mutexes, spin mutexes, adaptive spinning, turnstile blocking, lock-class integration, thread lock handling, assertions, initialization/destruction, DDB display, and system mutex bootstrap.

## Main Elements
- Defines lock classes `lock_class_mtx_sleep` and `lock_class_mtx_spin`.
- Provides exported function forms of inline mutex operations: `__mtx_lock_flags()`, `__mtx_unlock_flags()`, `__mtx_lock_spin_flags()`, `__mtx_trylock_spin_flags()`, and `__mtx_unlock_spin_flags()`.
- `_mtx_trylock_flags_int()` implements trylock with recursion handling for sleep mutexes.
- `__mtx_lock_sleep()` handles contested sleep mutex acquisition, recursion, adaptive spinning on running owners, turnstile wait setup, waiters marking, lock profiling, and DTrace lockstat hooks.
- `_mtx_lock_spin_cookie()` handles contested spin mutex acquisition with spinlock enter/exit balancing and indefinite-spin detection.
- `_thread_lock()` and `thread_lock_flags_()` acquire a thread's current spin lock while tolerating lock migration.
- `thread_lock_block()`, `thread_lock_unblock()`, `thread_lock_block_wait()`, and `thread_lock_set()` support temporary thread-lock replacement.
- `__mtx_unlock_sleep()` handles recursion unwind, uncontested release, and contested wakeup through turnstiles.
- `__mtx_assert()` validates ownership, recursion, and non-ownership assertions.
- `_mtx_init()`, `mtx_sysinit()`, and `_mtx_destroy()` initialize and destroy mutexes with witness/profile flags.
- `mutex_init()` initializes turnstiles, `Giant`, `blocked_lock`, proc0 locks, device mutexes, and locks Giant during early boot.
- `mtx_spin_wait_unlocked()` and `mtx_wait_unlocked()` wait until spin or sleep mutexes become unlocked.
- DDB support prints mutex class, state, owner, and recursion count.

## Dependencies And Integration
Integrates with lock classes, witness, turnstiles, scheduler state, thread structures, spinlock sections, lock profiling, DTrace lockstat, HWPMC soft hooks, KTR, DDB, devfs mutexes, and early kernel bootstrap.

## Risk Notes
The file encodes core locking invariants: sleep mutexes cannot be used as spin mutexes, spin locks must balance interrupt state, recursion requires explicit flags, and thread locks can migrate while being acquired. Adaptive spinning depends on owner thread run state. Long-held spin mutexes panic after repeated indefinite checks.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sys/kern/kern_mutex.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sys/kern/kern_ntptime.c -->
# File Research: sources/os/bsd/freebsd-src/sys/kern/kern_ntptime.c

Read completely: 1049 lines.

## Purpose
Implements FreeBSD's kernel NTP clock discipline interface, including `ntp_gettime(2)`, `ntp_adjtime(2)`, `adjtime(2)`, PLL/FLL state updates, optional PPS synchronization, leap-second state handling, per-second tick adjustments, and periodic RTC save scheduling.

## Main Elements
- Maintains NTP state variables: `time_state`, `time_status`, TAI offset, max/estimated error, PLL time offset, frequency offset, tick adjustment, and pending `adjtime` slew.
- Uses 64-bit fixed-point helpers for time and frequency arithmetic.
- `ntp_is_time_error()` maps status bits to trusted/untrusted time state.
- `ntp_gettime1()`, `sys_ntp_gettime()`, and `ntp_sysctl()` report current nanosecond time, errors, TAI, and state.
- `kern_ntp_adjtime()` validates privilege, applies mode-controlled changes to status, errors, time constant, TAI, PPS parameters, frequency, and offset, then returns updated `timex` state.
- `sys_ntp_adjtime()` is the copyin/copyout syscall wrapper.
- `ntp_update_second()` advances error accounting, processes leap insert/delete state transitions, computes next-second adjustment from PLL/FLL and `adjtime`, and returns TAI offset.
- `hardupdate()` updates phase/frequency estimates from daemon-provided offsets, selecting PLL or FLL behavior based on interval and status.
- Optional `hardpps()` processes PPS events with range checks, median filtering, jitter/wander accounting, frequency calibration, interval adjustment, and PPS-driven clock discipline.
- `kern_adjtime()` and `sys_adjtime()` implement microsecond-level clock slewing.
- Periodic `resettodr` callout writes synchronized time to the RTC and also runs during shutdown pre-sync.

## Dependencies And Integration
Uses spin mutex `ntp_lock`, sysctl, privilege checks (`PRIV_NTP_ADJTIME`, `PRIV_ADJTIME`), timecounter interfaces, PPS/timepps support, eventhandlers, callouts, `resettodr()`, and syscall copyin/copyout.

## Risk Notes
All NTP state is protected by a spin mutex, except a few documented lockless status reads for RTC save decisions. Privileged callers can set broad clock discipline state. PPS logic rejects noisy or malformed samples but depends on precise timecounter captures. Leap-second handling mutates `newsec` and TAI offset inside the per-second update path.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sys/kern/kern_ntptime.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sys/kern/kern_osd.c -->
# File Research: sources/os/bsd/freebsd-src/sys/kern/kern_osd.c

Read completely: 443 lines.

## Purpose
Implements Object Specific Data (OSD), a slot-based extension mechanism that lets kernel subsystems attach typed private data and methods to core objects without changing their structure layout.

## Main Elements
- `struct osd_master` tracks per-type module locks, object locks, object lists, destructors, methods, slot counts, and method counts.
- `osdm[]` defines OSD domains, currently with jail-specific method count metadata.
- `osd_register()` allocates or reuses a slot, installs a destructor and optional methods, and expands arrays when needed.
- `osd_deregister()` deletes all data for a slot from every object, then marks the slot unused.
- `osd_reserve()`, `osd_set()`, `osd_set_reserved()`, and `osd_free_reserved()` support normal and preallocated slot-array updates.
- `osd_get()` and `osd_get_unlocked()` return slot values under object locking or caller-provided synchronization.
- `osd_del()` and `do_osd_del()` run destructors, clear slots, shrink arrays, and remove objects from the active OSD list when empty.
- `osd_call()` invokes registered methods for a type/method across occupied slots until an error occurs.
- `osd_exit()` destroys all OSD attached to an object during object teardown.
- `osd_init()` initializes locks and lists at `SI_SUB_LOCK`.

## Dependencies And Integration
Uses sx locks for module registration, rmlocks for object slot access, mutexes for global object lists, malloc/realloc, jail method constants, sysctl debug control, and OSD public interfaces from `sys/osd.h`.

## Risk Notes
Slot registration/deregistration crosses module-level and object-level locks and can call destructors while walking all live objects. Reserved arrays avoid allocation failure in some set paths, but non-reserved growth uses `M_NOWAIT` and can fail. Deregistration leaves arrays allocated for reuse rather than shrinking global slot metadata.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sys/kern/kern_osd.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sys/kern/kern_physio.c -->
# File Research: sources/os/bsd/freebsd-src/sys/kern/kern_physio.c

Read completely: 206 lines.

## Purpose
Implements `physio()`, the kernel helper for raw character-device I/O from a `uio`, splitting requests, pinning or mapping user pages, building BIOs, invoking the device strategy routine, and updating the caller's `uio`.

## Main Elements
- Validates the character device switch and normalizes too-small `si_iosize_max`.
- Rejects oversized or multi-vector I/O for devices marked `SI_NOSPLIT`.
- Allocates a BIO and chooses between direct kernel buffer use, pbuf-backed mapped user pages, or unmapped BIO page arrays for `SI_UNMAPPED`.
- For user I/O, `vm_fault_quick_hold_pages()` pins pages with read/write protection appropriate to I/O direction.
- Sets BIO command, offset, length, count, device pointer, data pointer or page-array fields, and `BIO_UNMAPPED` where applicable.
- Calls `d_strategy()` and waits with `biowait()`.
- Unmaps pbuf mappings, unholds pages, accounts block I/O/resource counters, advances iov base/resid/offset, and propagates BIO errors.
- Frees pbuf/page arrays and destroys the BIO on exit.

## Dependencies And Integration
Uses GEOM BIO allocation, cdev strategy methods, pbuf zone, VM page pinning, pmap quick mappings, unmapped buffer support, RACCT accounting, `maxphys`, and `uio` structures. This is a key bridge between device drivers and raw block-style user I/O.

## Risk Notes
Pinned-page lifetimes must exactly bracket device strategy completion. Zero progress without `BIO_ERROR` is treated as EOF. `SI_NOSPLIT` requests are rejected with `EFBIG` rather than partially processed. The read/write protection direction is intentionally inverted-looking because device reads write into user memory.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sys/kern/kern_physio.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sys/kern/kern_pmc.c -->
# File Research: sources/os/bsd/freebsd-src/sys/kern/kern_pmc.c

Read completely: 368 lines.

## Purpose
Provides kernel-side support glue for the HWPMC subsystem: hook pointers, CPU topology predicates, per-domain buffer header allocation, soft PMC event registration, and initialization of PMC support data.

## Main Elements
- Exposes `pmc_kernel_version`, `pmc_hook`, `pmc_intr`, `hwt_hook`, and `hwt_intr` for optional PMC/HWT module integration.
- Defines per-CPU `pmc_sampled`, global `pmc_ss_count`, global `pmc_sx`, per-CPU soft trapframes, and per-memory-domain PMC buffer headers.
- CPU helper functions report active, disabled, present, primary, maximum CPU count, and invariant active count.
- `pmc_soft_namecleanup()` normalizes soft event names by removing duplicate/trailing underscores and uppercasing.
- `pmc_soft_ev_register()` assigns dynamic soft event codes, reuses vacant slots when the table is full, and warns once if exhausted.
- `pmc_soft_ev_deregister()` clears a registered soft event slot.
- `pmc_soft_ev_acquire()` returns a soft event while holding the spin mutex; `pmc_soft_ev_release()` releases it.
- `init_hwpmc()` clamps the soft-event tunable, allocates the soft-event table, allocates per-domain buffer headers from preferred memory domains, initializes their locks/lists, and counts CPUs per domain.

## Dependencies And Integration
Uses HWPMC option hooks, SMP CPU masks, memory domains, malloc/domainset allocation, spin mutexes, sx locks, trapframes, sysctl, and PMC event definitions. The mutex file also emits HWPMC soft calls for lock contention when hooks are enabled.

## Risk Notes
Hook pointers are optional and require external locking discipline through `pmc_sx`. Soft event registration warns that event-code reuse can race with old users. `pmc_soft_ev_acquire()` intentionally returns with `pmc_softs_mtx` still held, requiring paired release.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sys/kern/kern_pmc.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sys/kern/kern_poll.c -->
# File Research: sources/os/bsd/freebsd-src/sys/kern/kern_poll.c

Read completely: 582 lines.

## Purpose
Implements legacy device polling for network interfaces, allowing drivers to replace interrupt-driven packet processing with clock/netisr/idle-loop polling and adaptive burst sizing.

## Main Elements
- Defines sysctls under `kern.polling` for burst size, max burst, per-handler burst, idle polling, user CPU fraction, register-check interval, and diagnostic counters.
- `init_device_poll()` initializes the polling mutex and shutdown handler.
- `hardclock_device_poll()` runs from hardclock, schedules `NETISR_POLL`, tracks pending/lost polls, short ticks, suspect phases, and stalls.
- `ether_poll()` runs polling handlers from the idle loop under NET_EPOCH.
- `netisr_poll()` invokes registered handlers with `POLL_ONLY` or periodic `POLL_AND_CHECK_STATUS`, consuming a chunk of the residual burst.
- `netisr_pollmore()` runs after other netisrs, adapts `poll_burst` based on measured kernel network processing time, and reschedules if work remains.
- `ether_poll_register()` adds an interface/handler pair, rejects duplicates and table overflow, and wakes idle polling.
- `ether_poll_deregister()` removes an interface by replacing it with the last table entry.
- `poll_idle()` is a low-priority kernel process that polls in the idle loop when enabled.
- SYSINIT creates the polling infrastructure and starts the `idlepoll` kproc.

## Dependencies And Integration
Uses network interfaces, netisr polling hooks, NET_EPOCH, hardclock, kernel threads, scheduler priorities, eventhandlers, sysctl, and `IFCAP_POLLING` driver integration.

## Risk Notes
The handler table is fixed at 128 entries. Polling holds `poll_mtx` while calling handlers, so handlers must be short and must follow polling assumptions. Adaptive burst sizing tries to avoid livelock and excessive user CPU starvation but can still record stalls when handlers run too long.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sys/kern/kern_poll.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sys/kern/kern_priv.c -->
# File Research: sources/os/bsd/freebsd-src/sys/kern/kern_priv.c

Read completely: 366 lines.

## Purpose
Implements centralized kernel privilege checks, combining MAC policy denial/grant hooks, jail restrictions, configurable superuser policy, special unprivileged allowances, and fast paths for common VFS privileges.

## Main Elements
- `suser_enabled()` checks the jail/prison `PR_ALLOW_SUSER` policy.
- `sysctl_kern_suser_enabled()` exposes and updates `security.bsd.suser_enabled` per prison.
- Sysctls control unprivileged `mlock`/`munlock` and unprivileged kernel message-buffer reads.
- SDT probes report successful and failed privilege checks.
- `priv_check_cred_pre()` calls MAC denial hooks when enabled.
- `priv_check_cred_post()` gives MAC grant hooks a final chance and otherwise defaults to `EPERM`.
- `priv_check_cred()` handles special VFS fast-path dispatch, MAC precheck, jail restriction, unprivileged allowances, superuser grants by effective or real uid, special kernel memory/process memory allowances, and unprivileged debug policy.
- `priv_check()` checks the current thread's credentials.
- `priv_check_cred_vfs_lookup()` and `_nomac()` provide optimized root/superuser checks unless MAC/probes require the slow path.
- `priv_check_cred_vfs_generation()` denies jailed callers and otherwise permits root when superuser policy is enabled.

## Dependencies And Integration
Uses credentials, jail/prison policy, MAC framework hooks, SDT probes, sysctl, privilege constants, and VFS-specific privilege helpers. Many files in this group call into it indirectly, including NTP time adjustment and filesystem/VFS metadata checks.

## Risk Notes
The default policy is deny unless a specific path grants privilege. Disabling superuser semantics can break traditional root assumptions. Fast paths intentionally bypass MAC only when MAC hooks/probes are inactive; otherwise they return slow-path results or `EAGAIN` for the nomac variant.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sys/kern/kern_priv.c -->