# Group Research: group_1262_netbsd_src_sources_os_bsd_netbsd_src_sys_kern_kern_lwp_c_sources_os_b9894aae6e49

Scope checked against `Docs/research_subset_a.md`: all requested files are under `sources/os/bsd/netbsd-src`, which is included in subset A. All 11 listed source files were read completely.

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/sys/kern/kern_lwp.c -->
# File Research: sources/os/bsd/netbsd-src/sys/kern/kern_lwp.c

Read completely: 2211 lines.

Implements NetBSD lightweight process (LWP) lifecycle and core thread management. It defines the LWP state model, bootstrap LWP setup, LWP allocation/recycling, creation, start, exit, wait/reap, suspension, continuation, migration, lookup, movable LWP locks, user-return work, LWP references, lwpctl shared pages, and debugger stack ownership reporting.

Core lifecycle:
- `lwpinit()` initializes the global `alllwp` list, LWP specificdata, `lwp_cache`, `kern.maxlwp`, and the pserialize-backed LWP pool safety model.
- `lwp0_init()` publishes bootstrap `lwp0`, initializes callouts/CVs/credentials/specificdata, and sets syscall timing state.
- `lwp_create()` allocates or recycles an LWP, enforces `RLIMIT_NTHR`, allocates a LID, copies scheduler/credential/signal/filedesc/PCU/VM context, inserts the LWP in the process list, and publishes it on `alllwp`.
- `lwp_start()` moves a new `LSIDL` LWP to runnable, suspended-at-userret, or stopped depending on flags and process stop state.
- `lwp_startup()` is the machine-independent new-thread entry handoff: it clears the previous LWP’s running bit, activates the VM context, drops to normal IPL, and enters kernel-lock state for non-MPSAFE kthreads.
- `lwp_exit()` handles non-last-LWP termination: delegates process exit when last live LWP, removes lookup visibility, frees thread/file/fstrans/specificdata/credential resources, drains references, marks `LSZOMB`, wakes waiters, and switches away if exiting the current LWP.
- `lwp_free()` waits until the zombie is off-CPU, resets it to `LSIDL`, merges runtime/resource usage into the process, removes process links, frees LID, signal queues, lwpctl, affinity, KMSAN/KCOV/DTrace/MD/UVM state, and either recycles or returns the object.

Wait/suspend/control behavior:
- `lwp_suspend()`, `lwp_continue()`, and `lwp_unstop()` implement user and process-level suspension/continuation semantics.
- `lwp_wait()` collects zombie LWPs, handles detached LWP reaping, specific-LID waits, waiter markers, simple mutual wait deadlock detection, and process-exit wait mode.
- `lwp_migrate()` retargets LWPs to another CPU differently for runnable, sleeping, stopped, suspended, idle, and on-CPU states.
- `lwp_userret()` processes deferred work before user return: preemption, cached credentials, pending signals, core/suspend parking, process/LWP exit, and lwpctl CPU publication.
- `lwp_need_userret()` forces remote running LWPs through trap/userret with AST/signotify synchronization.

Lookup and locking:
- `lwp_find2()`, `lwp_find()`, `lwp_find_first()`, and `lwp_alive()` exclude `LSIDL` and `LSZOMB` and coordinate with `p_lock` or pid-table lookups.
- `lwp_lock()`, `lwp_trylock()`, `lwp_unlock()`, `lwp_unlock_to()`, `lwp_setlock()`, and `lwp_locked()` abstract the movable `l_mutex` pointer.
- The file documents LWP state locks and lock order: sleepq -> turnstile -> per-CPU `spc_lwplock` -> per-CPU `spc_mutex`.
- Process counters for idle, zombie, stopped, suspended, and runnable LWPs are maintained under `p_lock`.

Shared user control pages:
- `lwp_ctl_alloc()` lazily creates per-process anonymous lwpctl storage, maps it into user and kernel space, allocates bitmap slots, and returns user addresses.
- `lwp_ctl_free()` returns slots unless borrowed during vfork.
- `lwp_ctl_exit()` tears down the per-process lwpctl mapping for the last LWP.

Integration points:
- Scheduler, pid table, credentials, file descriptors, signals, ptrace events, DTrace, syscall timing, PCU, UVM LWP uareas, futex robust-list cleanup, fstrans, KCOV/KMSAN, psets/affinity, and optional DDB.
- `lwp_thread_cleanup()` releases robust futexes before an exiting LWP becomes unfindable.
- `lwp_whatis()` reports kernel stack ownership for DDB.

Risks and notes:
- State transitions are lock-sensitive because `l_mutex` can change with state.
- Detached LWP recycling deliberately preserves and reuses structures; fields outside `l_startzero` must remain valid for lockless pid-table races.
- `lwp_wait()` detects direct mutual waits but not arbitrary wait cycles.
- Zombie publication is delayed until external LWP references drain.
- lwpctl mappings and vfork-borrowed lwpctl state require careful lifetime handling.

Filesystem relevance: indirect. This is scheduler/thread substrate used by VFS, file descriptor, fstrans, futex, raw I/O, and filesystem paths, but it does not implement filesystem policy itself.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/sys/kern/kern_lwp.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/sys/kern/kern_malloc.c -->
# File Research: sources/os/bsd/netbsd-src/sys/kern/kern_malloc.c

Read completely: 235 lines.

Provides the legacy `malloc(9)` wrapper interface on top of `kmem_intr_alloc/free`. It preserves old malloc type definitions, hidden allocation headers, large-allocation page alignment, sanitizer redzones, and realloc semantics.

Main interfaces:
- `kern_malloc(reqsize, flags)` maps `M_NOWAIT` to `KM_NOSLEEP`, applies KASAN redzone sizing, stores total allocation size in a header, optionally zeroes memory, and returns the payload.
- `kern_free(addr)` finds the header immediately before the payload, updates KASAN/KMSAN state, and frees either the small block or page-aligned large-allocation base.
- `kern_realloc(curaddr, newsize, flags)` handles `NULL` and zero-size special cases, asserts sleepability when needed, returns the old pointer if large enough, or allocates/copies/frees for growth.

Important details:
- Built-in malloc types include `M_DEVBUF`, `M_TEMP`, `M_UFSMNT`, routing/network buckets, and related legacy buckets.
- `struct malloc_header` records actual allocation size and, under KASAN, requested size.
- Large allocations reserve an extra page so the returned payload can be page-aligned with the header just before it.
- Small allocations put the header at the beginning of the allocation.

Risks and notes:
- Correct free depends on the header being immediately before the user pointer.
- Large-allocation overflow is handled by forcing an allocation failure later.
- KASAN requested-size tracking matters because real allocation size may include redzones.
- `kern_realloc()` does not shrink in place.

Filesystem relevance: indirect. Legacy kernel allocation is used throughout kernel subsystems, including VFS and filesystem code.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/sys/kern/kern_malloc.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/sys/kern/kern_module.c -->
# File Research: sources/os/bsd/netbsd-src/sys/kern/kern_module.c

Read completely: 2038 lines.

Implements NetBSD kernel module management: subsystem initialization, built-in module registration, runtime load/autoload/unload, dependency recursion, bootloader-pushed modules, module metadata lookup, sysctls, autounload thread, module-specific data, and load/unload callbacks.

Core state:
- Global lists: `module_list`, `module_builtins`, `module_bootlist`, and callback list `modcblist`.
- `module_netbsd` is a synthetic module for the running kernel.
- `module_base` holds the filesystem module path.
- `module_load_vfs_vec` is the VFS-backed loader hook supplied by `kern_module_vfs.c`.
- `module_active` tracks the currently initializing/finalizing module for section lookup.
- Module-specific storage uses a `specificdata_domain`.

Main interfaces:
- Initialization: `module_init()`, `module_start_unload_thread()`.
- Built-ins: `module_builtin_add()`, `module_builtin_remove()`, `module_init_class()`, `module_builtin_require_force()`.
- Runtime load paths: `module_load()`, `module_autoload()`, `module_unload()`.
- References and lookup: `module_lookup()`, `module_hold()`, `module_rele()`, `module_kernel()`, `module_name()`, `module_source()`.
- Boot modules: `module_prime()`.
- Sections and storage: `module_find_section()`, `module_specific_key_create/delete()`, `module_getspecific()`, `module_setspecific()`.
- Callbacks: `module_register_callbacks()`, `module_unregister_callbacks()`.

Load flow:
- `module_do_load()` is the central loader. It handles disabled built-ins, bootlist modules, filesystem modules, duplicate checks, `link_set_modules` metadata fetch, version/class compatibility, filename/modinfo mismatch rules, circular dependency checks, recursive required-module loading, `kobj_affix()`, property merge, sysctl setup, evcnt attachment, `MODULE_CMD_INIT`, list publication, autounload scheduling, and load callbacks.
- Dependency recursion uses a stack of pending lists so nested dependency loads can detect circular references and share pending state.
- Built-in initialization uses `module_do_builtin()` to recursively initialize prerequisites, call `MODULE_CMD_INIT`, move modules from `module_builtins` to `module_list`, and attach dependency references.

Unload flow:
- `module_do_unload()` rejects missing or referenced modules, prevents built-in secmodel unloads, invokes unload callbacks, calls `MODULE_CMD_FINI`, tears down sysctl and evcnt state, removes the module from `module_list`, decrements dependency references, unloads `kobj`, and either returns built-ins to the disabled list or frees filesystem modules.
- `module_thread()` autounloads autoloaded modules after `module_autotime` or under memory pressure. It asks modules via `MODULE_CMD_AUTOUNLOAD`; unaudited modules returning `ENOTTY` unload only if `kern.module.autounload_unsafe` is enabled.

Policy and sysctl:
- `kern.module.autoload`, `autounload_unsafe`, `verbose`, `path`, and `autotime` are registered by `sysctl_module_setup()`.
- `module_autoload()` refuses names containing `/`, `@`, or `.` and can be disabled globally.
- Kauth authorizes explicit load/unload and system autoload.

Risks and notes:
- Loader failure paths must unwind `kobj`, pending-list entries, property dictionaries, sysctl logs, evcnt attachments, dependency arrays, and module memory in the right order.
- Built-in failure recovery is intentionally limited during boot/class initialization.
- `module_active` is global and depends on `kernconfig_lock` serialization.
- Duplicate module names can arise from filename/modinfo mismatch or recursive loads and are explicitly checked.
- Autounload safety depends on module cooperation or unsafe policy.

Filesystem relevance: high indirect. Runtime module loading depends on VFS object and property-file loading through `module_load_vfs_vec`, and filesystem drivers may be loaded/unloaded by this subsystem.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/sys/kern/kern_module.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/sys/kern/kern_module_hook.c -->
# File Research: sources/os/bsd/netbsd-src/sys/kern/kern_module_hook.c

Read completely: 134 lines.

Provides synchronization primitives for optional module hooks. The design lets hot-path callers enter hook code with minimal overhead while module load/unload safely publishes or withdraws hook availability.

Main interfaces:
- `module_hook_init()` initializes the global mutex, condition variable, and pserialize domain.
- `module_hook_set(hooked, lc)` initializes a localcount, performs a global pserialize barrier, then publishes `*hooked = true`.
- `module_hook_unset(hooked, lc)` clears `hooked`, runs pserialize to block new entrants, drains active localcount users, and finalizes the localcount.
- `module_hook_tryenter(hooked, lc)` enters a pserialize read section, checks hook availability, and acquires localcount if enabled.
- `module_hook_exit(lc)` releases the localcount and wakes drain waiters.

Correctness model:
- Set/unset require `kernconfig_is_held()`.
- Heavy `pserialize_perform()` work happens only during module load/unload.
- Hook calls use relaxed atomic loads/stores plus pserialize ordering and localcount lifetime protection.

Risks and notes:
- Every successful `module_hook_tryenter()` must be paired with `module_hook_exit()`.
- `hooked` and localcount storage are owned by the hook user; this file only coordinates access.
- The approach relies on pserialize barriers making hook setup visible before publication.

Filesystem relevance: indirect. This can support optional hooks in kernel subsystems, including VFS or filesystem module integration points.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/sys/kern/kern_module_hook.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/sys/kern/kern_module_vfs.c -->
# File Research: sources/os/bsd/netbsd-src/sys/kern/kern_module_vfs.c

Read completely: 233 lines.

Connects the module subsystem to VFS-backed files. It loads `.kmod` kernel objects and optional `.plist` property dictionaries from module paths.

Main interfaces:
- `module_load_vfs_init()` installs `module_load_vfs` into `module_load_vfs_vec` and prints `kern.module.path`.
- `module_load_vfs(name, flags, autoload, mod, filedictp)` resolves explicit or autoload module paths, calls `kobj_load_vfs()`, optionally loads plist properties, enforces `noautoload`, and returns a property dictionary when requested.
- `module_load_plist_vfs(modpath, nochroot, filedictp)` derives a `.plist` path, opens a vnode, stats and reads the file, NUL-terminates it, and internalizes it as a proplib dictionary.

Path behavior:
- Explicit non-autoload with a slash loads the exact path under normal root/chroot rules.
- Autoload or fallback `ENOENT` with a plain name loads `${module_base}/${name}/${name}.kmod` with `NOCHROOT`.
- Names with unexpected slashes do not get fallback path construction.

VFS dependencies:
- Uses `vn_open()`, `vn_stat()`, `vn_rdwr()`, `VOP_UNLOCK()`, and `vn_close()`.
- Uses path buffers, `PNBUF_GET/PUT`, `pathbuf_create/destroy`, `curlwp` credentials, `kobj_load_vfs()`, `kobj_unload()`, and proplib.

Risks and notes:
- Plist files are limited to 8191 bytes plus NUL; larger files return `EFBIG`.
- Autoload property `noautoload=true` blocks loading with `EPERM`.
- On plist errors other than `ENOENT`, an already loaded object is unloaded.
- The code assumes `vn_open()` returns a locked vnode and unlocks before close.

Filesystem relevance: direct. This is the VFS-facing half of kernel module loading and exercises pathname resolution, vnode I/O, credentials, and chroot-bypass policy.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/sys/kern/kern_module_vfs.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/sys/kern/kern_mutex.c -->
# File Research: sources/os/bsd/netbsd-src/sys/kern/kern_mutex.c

Read completely: 956 lines.

Implements NetBSD kernel mutexes, including adaptive sleepable mutexes, spin mutexes, lockdebug integration, lockstat probes, turnstile blocking/wakeup, priority-inheritance owner lookup, and architecture fast-path aliases.

Main interfaces:
- `_mutex_init()` and `mutex_init()` initialize adaptive or spin mutexes based on IPL and debug mode.
- `mutex_destroy()` verifies no owner/waiters or held spin bit, frees lockdebug state, and poisons/destroys the mutex.
- `mutex_vector_enter()` is the generic enter path for adaptive and spin mutexes.
- `mutex_vector_exit()` is the generic exit path.
- `mutex_tryenter()`, `mutex_owned()`, `mutex_ownable()`.
- `mutex_spin_retry()` is the retry path for spin mutex stubs.
- `mutex_wakeup()` exists on non-simple-mutex architectures.

Core mechanics:
- Spin mutexes raise SPL and acquire a simple lock, with backoff/spinout handling under MP/debug builds.
- Adaptive mutexes first try atomic owner acquisition. If the owner is running on another CPU, they spin briefly; otherwise they set the waiter bit under the turnstile chain lock and block.
- Adaptive exit can release without interlocked operations when no waiters are observed; otherwise it looks up the turnstile and wakes all writer waiters.
- `mutex_oncpu()` tests whether the owner LWP is currently running and has special big-kernel-lock deadlock handling.

State and ordering:
- Owner pointer bits encode owner, waiters, spin, and nodebug state.
- Acquire/release barriers protect owner publication and release.
- The file has detailed comments for the subtle race between setting waiters and unlocked `mutex_exit()`.
- Spin mutex SPL nesting is tracked in per-CPU `ci_mtx_count` and `ci_mtx_oldspl`.
- Priority inheritance sees owners through `mutex_owner()` and `mutex_syncobj`.

Risks and notes:
- Adaptive mutex correctness depends on subtle waiter-bit, turnstile, owner-running, and memory-ordering checks.
- Recursive adaptive acquisition panics.
- Spin self-locking panics in non-MP/full paths.
- `mutex_oncpu()` relies on LWP lifetime rules and pserialize barriers in LWP teardown.
- Releasing adaptive mutexes before interrupts are fully initialized has a special `cold` path on architectures without stubs.

Filesystem relevance: foundational. VFS, vnode, buffer cache, and filesystem code rely on these mutex semantics for SMP and interrupt-context correctness.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/sys/kern/kern_mutex.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/sys/kern/kern_mutex_obj.c -->
# File Research: sources/os/bsd/netbsd-src/sys/kern/kern_mutex_obj.c

Read completely: 152 lines.

Provides dynamically allocated, reference-counted mutex objects aligned to cache coherency units.

Main interfaces:
- `mutex_obj_alloc(type, ipl)` allocates with sleep, initializes an embedded `kmutex_t`, sets magic and refcount, and returns the mutex address.
- `mutex_obj_tryalloc(type, ipl)` is the non-sleeping allocation variant.
- `mutex_obj_hold(lock)` increments the object reference count.
- `mutex_obj_free(lock)` decrements the reference count, destroys and frees the object on the last reference, and returns whether it freed.
- `mutex_obj_refcnt(lock)` returns the current raw reference count.

Implementation details:
- `struct kmutexobj` embeds `kmutex_t` at offset zero, a magic value, a refcount, and padding to `COHERENCY_UNIT`.
- Uses `kmem_intr_alloc/free`, `_mutex_init()`, `mutex_destroy()`, atomics, and release/acquire barriers.
- Last-reference free uses `membar_release()` before decrement and `membar_acquire()` before destruction.

Risks and notes:
- `mutex_obj_hold()` assumes the caller already owns a valid reference.
- `mutex_obj_refcnt()` is observational and returns a raw field.
- Correct casting depends on `kmutex_t` remaining the first field.

Filesystem relevance: indirect. Useful for dynamically shared locks in kernel subsystems, including possible filesystem or VFS objects.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/sys/kern/kern_mutex_obj.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/sys/kern/kern_ntptime.c -->
# File Research: sources/os/bsd/netbsd-src/sys/kern/kern_ntptime.c

Read completely: 986 lines.

Implements kernel NTP time discipline and `adjtime(2)` second-by-second slewing, with optional PPS synchronization and sysctl/syscall reporting.

Main interfaces:
- `ntp_gettime()` returns current time, maximum error, estimated error, TAI offset, and NTP state.
- `sys_ntp_adjtime()` copies user `timex`, authorizes adjustment modes, calls `ntp_adjtime1()`, and copies updated state back.
- `ntp_adjtime1()` applies status, max/estimated error, time constant, TAI, PPS interval, precision mode, clock source, frequency, and offset adjustments.
- `ntp_update_second()` advances leap-second state and computes the next per-second adjustment from NTP PLL/FLL plus `adjtime`.
- `ntp_init()` initializes fixed-point adjustment state.
- `hardupdate()` updates local PLL/FLL phase and frequency estimates.
- `hardpps()` disciplines against PPS samples when `PPS_SYNC` is enabled.
- `ntp_timestatus()`, `sys___ntp_gettime50()`, and `sysctl_kern_ntptime()` expose status.

Core state:
- Uses 64-bit fixed-point `l_fp` macros for time and frequency quantities.
- NTP globals include `time_state`, `time_status`, `time_tai`, `time_monitor`, `time_constant`, `time_precision`, `time_maxerror`, `time_esterror`, `time_reftime`, `time_offset`, `time_freq`, and `time_adj`.
- `time_adjtime` tracks `adjtime(2)` correction in microseconds.
- PPS state includes a three-sample phase median filter, frequency estimate, jitter/stability counters, watchdog, and adaptive averaging interval.
- Core state is protected by `timecounter_lock`.

Control flow:
- `ntp_update_second()` handles leap insert/delete/wait states, increases max error, reduces PLL offset, adds frequency correction, expires PPS signal validity, and layers `adjtime` slew at 5000 ppm or 500 ppm depending on remaining correction.
- `hardupdate()` clamps phase offset and applies PLL/FLL corrections based on elapsed time and mode bits.
- `hardpps()` rejects noisy or out-of-range samples, applies a median phase filter, tracks jitter/wander/calibration errors, adapts averaging interval, and optionally updates system frequency.

Risks and notes:
- Much code is under `NTP` and `PPS_SYNC`; callers must respect feature guards.
- Core routines assert or assume `timecounter_lock` at clock priority.
- Frequency and phase clamps prevent runaway discipline.
- Leap-second handling mutates `newsec` and TAI state.
- `sys_ntp_adjtime()` assumes authorized users know what they are doing; validation is intentionally limited.

Filesystem relevance: indirect. Timekeeping affects file timestamps, cache expiry, and sync timing, but this file is not VFS-specific.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/sys/kern/kern_ntptime.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/sys/kern/kern_pax.c -->
# File Research: sources/os/bsd/netbsd-src/sys/kern/kern_pax.c

Read completely: 833 lines.

Implements NetBSD PaX exploit-mitigation policy: ASLR, MPROTECT W^X enforcement, and SEGVGUARD crash throttling. Behavior is controlled by compile-time options, ELF PaX notes, process flags, ptrace policy, and sysctls.

Main interfaces:
- `pax_init()` adjusts maximum stack mapping for ASLR stack waste.
- `pax_setup_elf_flags()` derives exec-package PaX flags from ELF PaX notes.
- `pax_set_flags()` applies exec-package PaX flags to the process and optionally disables MPROTECT for traced processes.
- MPROTECT: `pax_mprotect_maxprotect()`, `pax_mprotect_validate()`, `pax_mprotect_prot()`.
- ASLR: `pax_aslr_init_vm()`, `pax_aslr_mmap()`, `pax_aslr_exec_offset()`, `pax_aslr_rtld_offset()`, `pax_aslr_stack()`, `pax_aslr_stack_gap()`.
- SEGVGUARD: `pax_segvguard()`, `pax_segvguard_cleanup()`.
- `sysctl_security_pax_setup()` registers `security.pax` subtrees.

Policy:
- Global modes apply protection unless an ELF `NO*` flag disables it.
- Non-global modes apply protection only when an ELF enable flag requests it.
- MPROTECT rejects simultaneous write+execute mappings for protected processes.
- `pax_mprotect_prot()` can allow ptrace extraction override depending on `pax_mprotect_ptrace`.
- ASLR computes mmap, executable, runtime linker, stack, and stack-gap randomization with architecture constants and 32-bit/topdown distinctions.
- ASLR debug can disable subfeatures or use fixed randomness.

SEGVGUARD:
- Stores crash history on executable vnodes in `v_segvguard`, keyed by uid.
- Repeated crashes within expiry suspend execution for a configured duration.
- Later exec attempts during suspension return `EPERM`.
- `pax_segvguard_cleanup()` frees per-vnode UID crash entries.

Locking and correctness:
- `pax_segvguard()` requires `exec_lock`; crash updates require write-held `exec_lock`.
- ASLR setup must happen during exec before VM layout decisions.
- SEGVGUARD state is attached to vnodes and must be cleaned during vnode lifecycle.

Risks and notes:
- Entropy and placement depend on architecture-provided constants such as `PAX_ASLR_DELTA_EXEC_LEN`.
- Ptrace policy deliberately weakens MPROTECT when configured.
- SEGVGUARD memory is allocated on crash/exec paths and is vnode-lifetime state.
- Compat32 stack handling is called out as not handled in `pax_init()`.

Filesystem relevance: moderate. SEGVGUARD stores per-executable state on vnodes, and PaX behavior is derived from executable ELF metadata loaded through exec/VFS paths.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/sys/kern/kern_pax.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/sys/kern/kern_physio.c -->
# File Research: sources/os/bsd/netbsd-src/sys/kern/kern_physio.c

Read completely: 462 lines.

Implements raw physical I/O between user buffers and character devices, bypassing the buffer cache. It supports concurrent disk I/O and asynchronous completion through a workqueue.

Main interfaces:
- `physio(strategy, obp, dev, flags, min_phys, uio)` maps user I/O vectors into buffers, locks user pages, calls device strategy routines, waits for completion, updates residuals/errors, and cleans up.
- `minphys(bp)` clamps transfer size to `MAXPHYS`.

Internal helpers:
- `physio_init()` creates the `physiod` workqueue.
- `physio_biodone()` is the buffer completion callback and enqueues post-I/O work.
- `physio_done()` unmaps kernel buffer mappings, unlocks user pages, records errors/residuals, signals waiters, and releases temporary iobufs.
- `physio_wait()` waits for outstanding request count to fall to a threshold.

Core state:
- `physio_workqueue` and tunable `physio_concurrency = 16`.
- Per-call `struct physio_stat` tracks running I/Os, first/lowest-offset error, failure count, residual bytes, original buffer, mutex, and CV.
- Uses `getiobuf/putiobuf`, buffer flags, `uvm_vslock/vsunlock`, `vmapbuf/vunmapbuf`, character-device type checks, and workqueues.

Control flow:
- Disks can run multiple requests concurrently; non-disks and caller-supplied raw buffers force synchronous one-at-a-time operation.
- Disk offsets must be `DEV_BSIZE` aligned.
- Disk transfers are split at `MAXPHYS`; non-disk transfers are bounded by `INT_MAX` and `min_phys`.
- Each request locks user pages with permission opposite to I/O direction, maps them into kernel space, sets `B_PHYS|B_RAW`, and calls `strategy`.
- Completion records the earliest failing disk offset so `uio_resid` represents bytes after the first failed region.

Risks and notes:
- `vmapbuf()` clobbers `b_data` until `vunmapbuf()` restores it, so cleanup order is critical.
- Partial completions and concurrent disk errors require careful lowest-offset accounting.
- Caller-supplied `obp` may be used by drivers as an identifier, so concurrency is disabled for that path.
- Diagnostic builds panic if `min_phys` leaves `b_bcount > MAXPHYS`.

Filesystem relevance: direct storage relevance. Used by raw device I/O paths beneath filesystems and block devices, bypassing the buffer cache.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/sys/kern/kern_physio.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/sys/kern/kern_pmf.c -->
# File Research: sources/os/bsd/netbsd-src/sys/kern/kern_pmf.c

Read completely: 1170 lines.

Implements the kernel Power Management Framework (PMF): system/device suspend, resume, shutdown, suspensor tracking, class helpers for network/input/display devices, generic PMF events, platform properties, sysctl debug controls, and workqueue initialization.

Main interfaces:
- System operations: `pmf_system_suspend()`, `pmf_system_resume()`, `pmf_system_bus_resume()`, `pmf_system_shutdown()`.
- Platform properties: `pmf_set_platform()`, `pmf_get_platform()`.
- Device registration: `pmf_device_register1()`, `pmf_device_deregister()`, `pmf_self_suspensor_init()`.
- Device transitions: `pmf_device_suspend()`, `pmf_device_resume()`, recursive suspend/resume, descendant release/resume, subtree release/resume.
- Class helpers: `pmf_class_network_register()`, `pmf_class_input_register()`, `pmf_class_display_register()`.
- Events: `pmf_event_inject()`, `pmf_event_register()`, `pmf_event_deregister()`.
- `pmf_init()` initializes pools, workqueues, and the display idle callout.

System suspend/resume:
- `pmf_system_suspend()` checks all devices have PMF support, blanks display when applicable, takes the kernel lock, syncs buffers with `do_sys_sync()` and `vfs_syncwait()` unless shutdown/panic already did, then suspends active devices leaves-first.
- `pmf_system_resume()` checks PMF support, resumes inactive enabled devices root-first, drops the kernel lock, and restores display state.
- `pmf_system_bus_resume()` invokes only bus resume handlers root-first.
- `pmf_system_shutdown()` runs driver/bus shutdown callbacks unless panicking.

Device state model:
- Suspensors are tracked separately at class, driver, and bus levels with fixed arrays.
- Standard suspensors include `system`, `drvctl`, and `self`.
- `pmf_device_suspend_locked()` records the suspensor, then calls class, driver, and bus suspend in that order.
- `pmf_device_resume_locked()` removes the suspensor; if other suspensors remain it stops, otherwise resumes bus, driver, then class.
- Recursive suspend descends to children before the parent; recursive resume resumes ancestors before the target.

Events and classes:
- Generic PMF events are queued to `pmfevent` workqueue and delivered to matching per-device or global handlers.
- Event workitems come from a small pool with `PR_NOWAIT`, so injection can fail under memory pressure.
- Network suspend stops the interface; resume restarts it only if `IFF_UP`.
- Input/display class helpers use a global idle callout to emit display-off events after inactivity.

Locking and correctness:
- Device PMF transitions acquire per-device PMF locks.
- Suspensor add/remove supports delegator replacement/removal rules.
- Display idle list manipulation raises to `splsoftclock`.
- Event handler list has no local lock in this file; correctness depends on external registration context/serialization.

Risks and notes:
- System suspend failure handling is incomplete; comments note failures are printed but do not abort the overall suspend.
- Multiple suspensors can keep a device logically suspended after one resume request.
- PMF event injection can drop events if pool allocation fails.
- `pmf_suspend_worker()` can complete delegated suspensions asynchronously via `pmfsuspend`.

Filesystem relevance: moderate. PMF system suspend explicitly syncs filesystem buffers with `do_sys_sync()` and `vfs_syncwait()`, coordinating power transitions with filesystem writeback.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/sys/kern/kern_pmf.c -->