# Group Research: group_1259_netbsd_src_sources_os_bsd_netbsd_src_sys_kern_kern_auth_c_sources_o_77969ab6bef2

Scope checked against `Docs/research_subset_a.md`: all requested files are under `sources/os/bsd/netbsd-src`, which is included in subset A. All 11 listed source files were read completely.

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/sys/kern/kern_auth.c -->
# File Research: sources/os/bsd/netbsd-src/sys/kern/kern_auth.c

Read completely: 1187 lines.

Implements NetBSD’s core kauth credential and authorization-scope framework. It manages `kauth_cred_t` allocation, reference counting, cloning/copying, UID/GID/group accessors and mutators, credential fork/chroot hooks, conversion to/from legacy credential structures, secmodel-specific credential data keys, and current-LWP credential lookup.

The file also owns authorization scope registration and listener dispatch. `kauth_init()` creates the credential pool, specificdata domain, global `kauth_lock`, and built-in scopes for credential, generic, system, process, network, machdep, device, and vnode authorization. `kauth_register_scope()`, `kauth_deregister_scope()`, `kauth_listen_scope()`, and `kauth_unlisten_scope()` maintain the scope/listener queues. `kauth_authorize_action_internal()` calls each listener and aggregates allow/deny/defer results, with `NOCRED` and `FSCRED` short-circuited to allow.

Public wrappers map callers into specific built-in scopes: generic, system, process, network, machdep, device, tty, raw device, device passthrough, and vnode authorization. Vnode authorization distinguishes explicit listener allow/deny from filesystem decisions and remote-filesystem fallback behavior. Helper translators convert vnode access modes and extended-attribute modes into kauth vnode actions.

Risks and notes: listener traversal in `kauth_authorize_action_internal()` has reader locking commented out, so listener lifetime depends on wider kauth conventions. Credential setters assert exclusive ownership via `cr_refcnt == 1`. `kauth_proc_fork()` explicitly relies on the parent being stalled during fork. `kauth_proc_setgroups()` has an indentation oddity around the failure return but behavior is straightforward. If no secmodels are registered, deferred non-denied actions are allowed by `kauth_authorize_action()`.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/sys/kern/kern_auth.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/sys/kern/kern_cctr.c -->
# File Research: sources/os/bsd/netbsd-src/sys/kern/kern_cctr.c

Read completely: 288 lines.

Implements a CPU cycle-counter-backed `timecounter` and multiprocessor calibration support. The primary CPU is treated as the reference counter; secondary CPUs maintain `ci_cc.cc_delta` offsets so `cc_get_timecount()` can return a primary-relative counter value.

`cc_init()` initializes the global `cc_timecounter`, optionally installs an MD counter reader, records frequency/name/quality, initializes the MP calibration spin mutex, and registers the timecounter. `cc_init_secondary()` seeds per-secondary calibration counters with CPU-index skew and immediately calibrates. `cc_calibrate_cpu()` serializes calibration attempts, triggers the primary CPU via `cc_get_primary_cc()`, waits for the primary-ready state, and retries if the secondary’s 32-bit counter wraps during measurement. `cc_primary_cc()` is the primary-side rendezvous routine that publishes the reference counter value.

The MP calibration protocol uses atomic release/acquire state transitions among `CC_CAL_START`, `CC_CAL_PRIMARY_READY`, `CC_CAL_SECONDARY_READY`, and `CC_CAL_FINISHED`. `cc_get_delta()` samples the secondary counter before and after the primary reference point, computes an overflow-safe midpoint, and stores the delta.

Risks and notes: calibration uses busy waits and expects primary-side interrupts to be blocked when `cc_primary_cc()` runs. A 32-bit counter wrap during the secondary measurement forces retry. The source notes that `cc_timecounter.tc_frequency` is not sysctl-adjustable and that variable-frequency counters should not be auto-selected without care.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/sys/kern/kern_cctr.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/sys/kern/kern_cfglock.c -->
# File Research: sources/os/bsd/netbsd-src/sys/kern/kern_cfglock.c

Read completely: 101 lines.

Provides the recursive kernel configuration lock used to serialize additions and removals of kernel functionality such as device configuration and module loading.

`kernconfig_lock_init()` initializes the backing mutex and owner/recurse state. `kernconfig_lock()` asserts it is not called from interrupt context, then either increments recursion for the current LWP or takes the mutex and records the owner. `kernconfig_unlock()` decrements recursion and releases the mutex when the outermost holder exits. `kernconfig_is_held()` reports whether the backing mutex is owned.

Risks and notes: recursion ownership is tracked manually with `kernconfig_lwp` and `kernconfig_recurse`, so correct pairing is essential. The unlocked current-LWP owner check is documented as safe only because the owner can be set to `curlwp` by the current thread itself, not by interrupts or other LWPs.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/sys/kern/kern_cfglock.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/sys/kern/kern_clock.c -->
# File Research: sources/os/bsd/netbsd-src/sys/kern/kern_clock.c

Read completely: 552 lines.

Implements machine-independent kernel clock handling for hardclock, statclock, schedclock, profiling clock control, clock tick sysctls, and entropy sampling from clock skew.

`initclocks()` calls MD clock initialization, adjusts `tick` and `tickadj` if `hz` changes, registers a fallback interrupt-resolution timecounter, computes profiling/stat ratios, creates `kern.clockrate` and `kern.hardclock_ticks` sysctls, and attaches hardclock/statclock random sources. `hardclock()` handles per-tick timers: entropy sampling, per-LWP process timers, fallback statclock, fallback scheduler clock at about 16 Hz, scheduler tick accounting, primary-CPU tick/timecounter advancement, heartbeat progress checks, and callout advancement.

`startprofclock()` and `stopprofclock()` maintain process profiling state and adjust `psdiv` when the statistics clock is the profiling source. `statclock()` samples entropy, updates per-CPU stat/prof divisors, records user/system/interrupt/idle CPU time, charges process tick counters, records profiling samples for user and optional kernel gprof/DTrace hooks, and runs cyclic DTrace clock hooks when enabled. `schedclock()` delegates runnable non-idle LWPs to scheduler accounting.

Risks and notes: if no separate statclock exists, profiling/statistics run from hardclock and comments explicitly say accuracy is poor. `hardclock_ticks` is advanced only by the primary CPU. `statclock()` changes the MD statclock rate when the per-CPU observed divisor changes. Interrupt time can be charged to the current process, by design, to account for real time spent in non-process work.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/sys/kern/kern_clock.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/sys/kern/kern_condvar.c -->
# File Research: sources/os/bsd/netbsd-src/sys/kern/kern_condvar.c

Read completely: 572 lines.

Implements NetBSD kernel condition variables on top of sleep queues. The private `kcondvar_t` storage holds a sleep queue and wait message. `cv_syncobj` integrates condition-variable sleeps with priority boosting, priority changes, lending, and unsleep handling.

`cv_init()` and `cv_destroy()` initialize and tear down the embedded sleep queue. `cv_enter()` hashes and locks the sleep queue, enqueues the current LWP, records whether the wait is interruptible, and releases the caller’s mutex. `cv_wait()`, `cv_wait_sig()`, `cv_timedwait()`, and `cv_timedwait_sig()` block through `sleepq_block()` and reacquire the mutex before returning. `cv_unsleep()` removes interrupted sleepers from the condition variable.

The bintime wait variants, `cv_timedwaitbt()` and `cv_timedwaitbt_sig()`, convert bintime timeouts into ticks, clamp very large waits, wait with at least one tick, and subtract elapsed tick time from the caller’s remaining-time value. `cv_signal()` and `cv_broadcast()` provide fast empty-queue checks and call noinline slow paths to wake one or all sleepers. Diagnostic helpers report waiters and basic validity.

Risks and notes: condition variables require the caller’s interlock discipline; `cv_signal()` and `cv_broadcast()` are documented for use with the interlocking mutex held or just released. Bintime waits are currently tick-based despite accepting an epsilon parameter, which is asserted but not otherwise used. The remaining-time update deliberately does not convert an explicit wakeup into `EWOULDBLOCK`, so callers must recheck their condition.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/sys/kern/kern_condvar.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/sys/kern/kern_core.c -->
# File Research: sources/os/bsd/netbsd-src/sys/kern/kern_core.c

Read completely: 360 lines.

Implements the loadable coredump module hook wiring and the generic coredump file creation/write path. `coredump_modcmd()` installs or removes hooks for the core writer, I/O helpers, NetBSD/ELF coredump formats, and UVM coredump map walkers.

`coredump()` enforces the core-size rlimit check, holds process credentials, blocks set-id coredumps unless explicitly configured, resolves the core filename pattern, checks `MNT_NOCOREDUMP` on the containing filesystem, opens the target with `O_CREAT | O_NOFOLLOW | FWRITE`, rejects non-regular files, multiply linked files, and files not owned by the dumping effective UID, truncates the target, optionally applies configured set-id core owner/group/mode, and calls the process execsw coredump routine. `coredump_write()` writes through `vn_rdwr()` with `IO_NODELOCKED | IO_UNIT` and advances the output offset; `coredump_offset()` returns the current offset.

`coredump_buildname()` expands `%n` process command, `%p` PID, `%u` session login name, and `%t` process start time into the configured pattern while enforcing `MAXPATHLEN`.

Risks and notes: the in-source comment says the data+stack+USPACE rlimit check is wrong for mapped data. Directory validation for complex paths uses an acknowledged double-lookup pattern. The return value from `VOP_SETATTR()` during truncation/metadata setup is not checked. Core files are opened no-follow and must have link count one, which reduces symlink/hardlink leakage risk.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/sys/kern/kern_core.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/sys/kern/kern_cpu.c -->
# File Research: sources/os/bsd/netbsd-src/sys/kern/kern_cpu.c

Read completely: 637 lines.

Implements machine-independent CPU attachment, `/dev/cpuctl` ioctl handling, CPU online/offline transitions, interrupt-routing control, CPU class comparison helpers, and optional CPU microcode firmware loading.

`mi_cpu_attach()` assigns CPU indexes, creates per-CPU cpusets, initializes CPU lock/debug lists and names, grows `cpu_infos`, attaches scheduler state, creates the idle LWP, initializes per-CPU subsystems such as percpu, softint, callout, xcall, pool cache, select, and cache state, and increments `ncpu`/`ncpuonline`. `cpuctl_ioctl()` handles get/set CPU state, map ordinal to CPU ID, CPU count, and optional microcode version/apply operations with kauth authorization for state and microcode changes.

`cpu_setstate()` uses cross-calls to run online/offline transitions on the target CPU while `cpu_lock` is held. Offline transition marks `SPCF_OFFLINE`, migrates non-bound/non-interrupt LWPs to an eligible CPU respecting affinity, saves PCU state, suspends heartbeat, and calls MD offline hooks. Online transition resumes heartbeat and clears the offline flag. The code refuses to offline the last online CPU in a processor set. Interrupt control, when supported by the port, uses cross-calls to set or clear `SPCF_NOINTR`, refuses disabling interrupts on the primary CPU, requires at least one interrupt-capable CPU to remain, and redistributes interrupts.

Risks and notes: `IOC_CPU_SETSTATE` calls `cpu_setintr()` and explicitly neglects errors before changing online state. Offline can fail if an affine LWP has no online eligible CPU, in which case the flag is cleared and `EBUSY` is returned. CPU microcode loading frees prior blobs, opens MD firmware, validates nonzero size, allocates firmware memory, and clears state on read failure.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/sys/kern/kern_cpu.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/sys/kern/kern_crashme.c -->
# File Research: sources/os/bsd/netbsd-src/sys/kern/kern_crashme.c

Read completely: 375 lines.

Provides deliberate crash/debug sysctl hooks under `debug.crashme` for testing kernel panic, fault, debugger, lock, SPL, and preemption failure paths. A separate writable `debug.crashme_enable` gate must be enabled before actions execute.

`crashme_add()` dynamically registers a named crashme sysctl node, avoiding duplicates and appending it to the linked list. `crashme_remove()` unlinks and destroys a registered node. `crashme_sysctl_forwarder()` maps the sysctl node number back to a `crashme_node`, handles read/list behavior through `sysctl_lookup()`, checks the enable gate for writes, invokes the node handler, and panics if the handler unexpectedly reports failure. `SYSCTL_SETUP()` creates the root node, enable boolean, mutex, and built-in crash nodes.

Built-in handlers include plain `panic()`, null pointer write, null function call, optional DDB entry, optional kernel-lock spinout, mutex recursion, infinite spin at raised IPL, and infinite spin with kernel preemption disabled.

Risks and notes: this file is intentionally destructive when enabled. `crashme_remove()` appears to print “unable to remove” when `sysctl_destroyv()` returns zero, which is usually success. The event handlers contain intentionally unreachable cleanup after infinite loops or deliberate crash paths.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/sys/kern/kern_crashme.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/sys/kern/kern_ctf.c -->
# File Research: sources/os/bsd/netbsd-src/sys/kern/kern_ctf.c

Read completely: 247 lines.

Implements kernel/module CTF metadata lookup and optional decompression support for DTrace-style consumers. The file avoids depending on the CDDL CTF header structure by using known offsets into the CTF header bytes.

`mod_ctf_get()` first checks cached module-specific CTF state through `fbt_module_key`. If absent, it allocates `mod_ctf_t`, finds module symbol/string tables either from the ksyms module table or the module kobj, locates `.SUNW_ctf`, validates the CTF magic and version 2 or 3, determines whether the CTF payload is compressed, and either references the existing CTF section or allocates a decompressed buffer. Compressed data is inflated with zlib after copying the fixed-size header. On success, the metadata is cached on the module and returned.

`z_alloc()` and `z_free()` are zlib allocation wrappers using `M_TEMP`.

Risks and notes: compressed size calculation trusts CTF header offsets after only magic/version checks. `inflateEnd()` is not called after `inflateInit2()`. `mc->ctfcnt` is set to the original section size even when `mc->ctftab` points to the decompressed buffer. Several string/symbol count fields are marked `XXX TBD`.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/sys/kern/kern_ctf.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/sys/kern/kern_descrip.c -->
# File Research: sources/os/bsd/netbsd-src/sys/kern/kern_descrip.c

Read completely: 2457 lines.

Implements NetBSD’s core file descriptor and open-file table management. It owns global file lists/counters, descriptor-table allocation and expansion, descriptor lookup/refcounting, close/dup/open-on-fd behavior, filedesc copy/share/free, close-on-exec and close-on-fork handling, file object lifetime, `/dev/fd` open redirection, descriptor owner signaling, cloned descriptor setup, fallback file operations, and `kern.file`/`kern.file2` sysctl reporting.

The descriptor table uses `fdfile_t` slots plus low/high bitmaps to find free descriptors quickly. `fd_getfile()` performs mostly lockless descriptor lookup and uses descriptor reference counts plus acquire/release barriers to coordinate with `fd_close()`. `fd_close()` first makes the descriptor invisible, drains outstanding descriptor references through `ff_closing`, restarts blocking file operations, removes knotes, releases POSIX locks as required, frees the descriptor slot, and then drops the underlying file reference with `closef()`. `closef()` releases BSD-style locks on last file reference, calls `fo_close()`, asserts `ERESTART` is not returned, and returns the file object to the cache.

`fd_alloc()`, `fd_tryexpand()`, `fd_affix()`, and `fd_abort()` manage allocation, table growth, file publication, and rollback. Table expansion publishes a new descriptor table with release ordering and defers freeing old tables while a filedesc is shared so lockless readers remain safe. `fd_copy()` creates fork copies, skips kqueue descriptors and close-on-fork descriptors, preserves close-on-exec flags, and can shrink large tables. `fd_free()` drops the final filedesc reference, closes remaining files, frees dynamic fdfile/table/bitmap/kqueue hash storage, and resets the object for cache reuse.

Other behavior includes `/dev/fd/N` support via `EDUPFD`, `fd_dupopen()` dup/move handling, `fd_closeexec()` unsharing shared tables across exec and clearing close-on-fork flags, `fsetown()`/`fgetown()`/`fownsignal()` for async I/O signal ownership, `fd_clone()` for cloner devices returning `EMOVEFD`, and sysctl walkers that filter by `KAUTH_PROCESS_CANSEE_OPENFILES` and hide kernel addresses unless address exposure is allowed.

Risks and notes: this is a high-risk concurrency file. The lockless lookup protocol depends on the documented memory-ordering relationship between `fd_getfile()` and `fd_close()`. `fd_dup2()` comments note potential deadlock while waiting for half-open descriptors. `fd_close()` may wait for references to drain after restarting file operations and notes it might need repeated restarts after a timeout. `fd_closeexec()` references Austin Group bug 1851 and intentionally clears `FD_CLOFORK` rather than preserving it across exec. Sysctl output uses a wraparound marker scheme protected by `sysctl_file_marker_lock`.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/sys/kern/kern_descrip.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/sys/kern/kern_drvctl.c -->
# File Research: sources/os/bsd/netbsd-src/sys/kern/kern_drvctl.c

Read completely: 685 lines.

Implements the `drvctl` driver-control pseudo-device, device-monitor event queue, ioctl handlers for suspend/resume/list/detach/rescan, plist command processing, and module glue.

`drvctl_init()` initializes the global event queue, mutex, condition variable, and select state. `devmon_insert()` is the devmon event insertion hook: it drops events when no process has drvctl open, adds the mandatory `"event"` string, bounds the FIFO to 64 entries by discarding the oldest event, wakes sleepers, and notifies poll/select waiters. `drvctlopen()` allocates a file descriptor and installs custom `drvctl_fileops` with `fd_clone()`, incrementing the open count. `drvctl_close()` decrements the open count and flushes queued events when the last opener closes.

Classic ioctls are handled under `KERNEL_LOCK`. `pmdevbyname()` suspends or resumes a named device recursively or by subtree. `listdevbyname()` lists direct children of a named device or root. `detachdevbyname()` finds a device through a writable deviter, checks parent detach notification support unless `XXXFULLRISK` is enabled, and calls `config_detach()`. `rescanbus()` validates bus/ifattr inputs, fills missing locators with `-1`, calls the bus attachment’s rescan hook for one or all interface attributes, and then runs deferred configuration.

Property-list commands currently support `"get-properties"`, which returns a device’s property dictionary. `drvctl_command()` copies in the command dictionary, validates command name and file access mode, calls the command handler, stores `"drvctl-error"` in the result dictionary, and copies results out. `drvctl_getevent()` requires read/write open mode, blocks interruptibly unless nonblocking, removes one queued event, copies it out, and releases it.

Module init attaches the devmon insertion hook, and loadable-module builds attach the device switch. Module fini refuses unload while open or while events remain, restores the previous devmon hook, detaches the device switch when applicable, and destroys state.

Risks and notes: event insertion silently releases and drops events when drvctl is unopened or the mandatory event string cannot be set. The event queue is lossy at depth 64. `drvctl_poll()` checks the queue without taking `drvctl_lock`, relying on broader select/poll conventions. `drvctl_command()` reports command-handler status inside the result dictionary but can overwrite the function return with copyout status. Detach is intentionally conservative unless built with `XXXFULLRISK`.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/sys/kern/kern_drvctl.c -->