# Group Research: group_1261_netbsd_src_sources_os_bsd_netbsd_src_sys_kern_kern_exit_c_sources_o_f655ed660e57

Scope checked against `Docs/research_subset_a.md`: all requested files are under `sources/os/bsd/netbsd-src`, which is included in subset A. All 13 listed source files were read completely.

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/sys/kern/kern_exit.c -->
# File Research: sources/os/bsd/netbsd-src/sys/kern/kern_exit.c

Read completely: 1340 lines.

Implements NetBSD process termination, zombie collection, wait-family system calls, and process reparenting support. This is the main exit/wait side of the process lifecycle, paired with `kern_fork.c` and integrated with signals, ptrace/procfs, kqueue process notes, accounting, VFS/file descriptor teardown, and scheduler cleanup.

Core exit flow:
- `sys_exit()` prevents repeated process-wide exit by checking `PS_WEXIT`, then calls `exit1()` with `p->p_lock` held.
- `exit1()` marks the process exiting, forces all other LWPs out with `exit_lwps()`, handles stop-on-exit tracing, drains pending signals, marks the process dying, and runs `lwp_thread_cleanup()` so global LWP lookup can no longer find it.
- Resource teardown releases lwpctl, proc references, POSIX timers, RAS state, file descriptors, cwd state, exit hooks, signal actions, process accounting, ktrace descriptors, emulation exit hooks, VM space, profiling, fstrans state, LWP/proc specificdata, and PCU state.
- Session leader cleanup detaches and potentially revokes the controlling terminal, sends `SIGHUP` to the foreground process group, and clears session leader state.
- Children are reparented to `initproc`; traced children are detached/reparented and killed as orphaned traced processes.
- The exiting process is moved from `allproc` to `zombproc`, marked `SDEAD` and later `SZOMB`, has its final LWP converted to `LSZOMB`, notifies kqueue via `knote_proc_exit()`, signals or wakes the parent, drops `p_reflock`, and finally switches away permanently.

Wait and collection:
- `do_sys_waitid()` and `do_sys_wait()` implement common wait logic for `wait4`/`wait6`-style interfaces, filling status, `wrusage`, and optional `siginfo_t`.
- `sys___wait450()` and `sys_wait6()` handle user copyout for legacy and modern wait entry points.
- `match_process()` checks child selection criteria by `P_ALL`, `P_PID`, `P_PGID`, `P_SID`, `P_UID`, and `P_GID`, fills approximate or final `siginfo_t`, and snapshots resource usage for stopped or exited children.
- `find_stopped_child()` scans a parent's children for zombies, stopped/traced children, and continued children, validates wait options, handles `WAIT_MYPGRP`, sleeps on `p_waitcv` when needed, and accounts for ptrace-reparented children via `debugged_child_exists()`.
- `proc_free()` performs final zombie collection: handles traced children that must be returned to an original parent, rolls child resource usage into the parent, frees PID and LWP resources, leaves the process group, releases credentials/limits/stats/text vnode/path/locks/CVs, and frees the proc structure.

Reparenting and tracing:
- `exit_psignal()` builds exit signal information, using `CLD_EXITED`, `CLD_KILLED`, or `CLD_DUMPED` for `SIGCHLD`, and includes pid, uid, and CPU time snapshots.
- `proc_changeparent()` marks a process traced, remembers its original parent, sets `PSL_CHTRACED` on the old parent, and reparents under `proc_lock`.
- `proc_reparent()` moves a child between parent child lists, adjusts stopped-child counters for zombies/dead/unwaited stopped processes, and normalizes `SIGCHLD` when reparenting to init.

Concurrency and invariants:
- `exit1()` starts with only `p->p_lock` held and uses explicit transitions through `proc_lock`, `p_reflock`, LWP locks, tty lock, and scheduler locks.
- The code carefully wakes vfork parents waiting on `PL_PPWAIT` after VM teardown to avoid deadlock.
- Once the process reaches the no-sleep section after parent notification, only machine-dependent LWP cleanup and final `mi_switch()` remain.
- `proc_free()` assumes the zombie is unreachable after list removal and intentionally stops doing normal locking after the final resource-release boundary.

Risks and notes:
- `initproc` death is fatal and panics immediately.
- `find_stopped_child()` has special handling for `SDEAD` children to avoid returning to userland during the short dying-to-zombie transition.
- Several wait idtypes are placeholders (`P_CID`, `P_PSETID`, `P_CPUID`).
- Traced-child reparenting is subtle: wait may need to block even when a matching child has been temporarily stolen by a debugger.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/sys/kern/kern_exit.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/sys/kern/kern_fileassoc.c -->
# File Research: sources/os/bsd/netbsd-src/sys/kern/kern_fileassoc.c

Read completely: 643 lines.

Implements `fileassoc(9)`, a per-mount facility for attaching subsystem-private data to files identified by filesystem file handles. It provides registration of association types, mount-local hash tables keyed by file handles, per-file specificdata storage, cleanup callbacks, and fast-path avoidance when no associations exist.

Core structures:
- `struct fileassoc` records an association name, cleanup callback, and specificdata key.
- `struct fileassoc_file` records a file handle, specificdata reference, association count, and hash-chain linkage.
- `struct fileassoc_table` stores the per-mount hash table, mask, slot counts, and table specificdata.
- `fileassoc_global` tracks global association use count and an `inuse` flag so vnode fast paths can skip work without global locking when fileassoc is unused.

Initialization and registration:
- `fileassoc_init()` creates the mount-specific key with `table_dtor()` and initializes the specificdata domain and global lock.
- `fileassoc_register()` runs initialization once, creates a specificdata key, allocates a `fileassoc`, inserts it in the global list, and returns the handle.
- `fileassoc_deregister()` removes the association, deletes its key, and frees the descriptor.

Lookup, table, and file entry handling:
- `fileassoc_table_lookup()` first checks the relaxed global `inuse` flag, runs lazy initialization if needed, and fetches the table from mount-specific storage.
- `fileassoc_file_lookup()` composes or accepts a vnode file handle, hashes it, and compares fileid length/content to find an entry.
- `fileassoc_table_add()` creates the initial per-mount table and stores it in mount-specific data.
- `fileassoc_table_resize()` doubles table slots, rehashes existing file entries, checks consistency, and replaces the old hash/specificdata storage.
- `fileassoc_table_delete()` clears the mount-specific pointer and destroys the table with all entries.
- `file_free()` removes one file entry, runs cleanup for all registered associations, decrements global use counts, frees the file handle and specificdata, and releases memory.

Public operations:
- `fileassoc_lookup()` returns data for a vnode/association pair.
- `fileassoc_add()` creates a file entry if absent, rejects duplicate data with `EEXIST`, increments global use, stores the data, and increments the per-file association count.
- `fileassoc_clear()` runs the cleanup callback, clears association data, decrements the per-file association count, and decrements global use.
- `fileassoc_file_delete()` removes all association data for a vnode, using the kernel lock around lookup/free and then decrementing table usage.
- `fileassoc_table_run()` iterates over all file entries in a mount table and invokes a callback for non-null data for one association.
- `fileassoc_table_clear()` clears one association across a mount table.

Concurrency and integration:
- Mount-specific storage owns table lifetime through `table_dtor()`.
- `fileassoc_incuse()` uses `xc_barrier()` when transitioning from unused to used so relaxed readers see the enabled state before fast paths rely on it.
- Some operations rely on higher-level serialization or the big kernel lock; the file contains explicit comments that resizing needs to ensure no concurrent fileassoc users.

Risks and notes:
- `fileassoc_table_resize()` has an explicit concurrency warning: it needs assurance that nothing uses fileassoc during rehash.
- `fileassoc_table_clear()` comments that it may be missing `faf->faf_nassocs--`, so association counts can become stale for table-wide clears.
- File entries are not garbage-collected when their per-file association count drops to zero, except through explicit file/table deletion.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/sys/kern/kern_fileassoc.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/sys/kern/kern_fork.c -->
# File Research: sources/os/bsd/netbsd-src/sys/kern/kern_fork.c

Read completely: 673 lines.

Implements process creation for `fork(2)`, historical and NetBSD `vfork(2)` variants, Linux-compatible `__clone(2)`, kernel-internal `fork1()`, and the initial child return path. It is the process creation counterpart to `kern_exit.c`.

Entry points and flags:
- `sys_fork()` calls `fork1()` with normal `SIGCHLD` exit signaling.
- `sys_vfork()` uses `FORK_PPWAIT` without shared VM for 4.4BSD/Mach-style compatibility.
- `sys___vfork14()` uses `FORK_PPWAIT | FORK_SHAREVM` for original shared-address-space vfork semantics.
- `sys___clone()` translates Linux clone flags to NetBSD fork flags: VM, cwd, file table, signal actions, and vfork-style parent wait. It rejects unsupported `CLONE_PTRACE`, invalid signal numbers, `CLONE_SIGHAND` without `CLONE_VM`, and `CLONE_FILES` with close-on-fork state.

`fork1()` flow:
- Increments global `nprocs`, enforces `maxproc`, asks kauth for fork authorization, and enforces per-user `RLIMIT_NPROC`, with optional `forkfsleep` delay on limit failures.
- Allocates U-area and proc structure before the commit point; after this, later resource allocation is expected not to fail.
- Initializes the child proc by zeroing/copying prescribed proc regions, sets inherited process flags, emulation, exec switch, locks/CVs, RAS state, text vnode/path, file descriptor table, cwd, limits, vfork parent-wait state, signal actions, scheduler state, stats, VM space, and LWP.
- Supports shared files/cwd/signals/VM and clean file table creation depending on flags.
- Copies/inherits ktrace state when `KTRFAC_INHERIT` is set.
- Calls emulation fork hooks and general fork hooks before publishing the child.
- Under `proc_lock`, inserts the child in the parent list, process group list, and `allproc`, handles ptrace fork/vfork parent changes, updates CPU fork counters, notifies kqueue process filters through `knote_proc_fork()`, and makes the child runnable unless `PS_STOPFORK` is active.
- Returns the child pid to the parent and waits for vfork completion if `FORK_PPWAIT` was requested.

Tracing and vfork:
- `tracefork()`, `tracevfork()`, and `tracevforkdone()` test ptrace event flags and suppress ordinary fork tracing for parent-wait vfork cases as appropriate.
- For traced fork/vfork, the child may be reparented to the tracer via `proc_changeparent()`, flagged `PSL_TRACEDCHILD`, and parent events are delivered through `eventswitch()`.
- The parent waits on `l_waitcv` while `l_vforkwaiting` remains true and optionally emits `PTRACE_VFORK_DONE`.

Child return:
- `child_return()` emits child-side ptrace fork/vfork events with `eventswitchchild()`, calls `md_child_return()`, and records a ktrace syscall return using `SYS_fork` for all fork variants.

Concurrency and integration:
- Process counts use atomics and per-uid accounting through `chgproccnt()`.
- `proc_lock`, per-process locks, scheduler locks, and LWP locks coordinate publication and runnable state.
- Integrates with kauth, uidinfo, filedesc, cwd, limits, UVM, signals, profiling, ktrace, kqueue, ptrace, RAS, emulation hooks, and DTrace process create probes.

Risks and notes:
- Comments call out a racy copy of `p_mqueue_cnt`.
- After the commit point, allocation failures are not expected; pre-commit allocation is deliberately front-loaded.
- Linux clone stack handling passes stack size zero because the Linux ABI leaves stack growth direction to the caller.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/sys/kern/kern_fork.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/sys/kern/kern_heartbeat.c -->
# File Research: sources/os/bsd/netbsd-src/sys/kern/kern_heartbeat.c

Read completely: 773 lines.

Implements `heartbeat(9)`, a periodic CPU progress monitor that detects stalled timecounter updates, stuck soft interrupts on the local CPU, and stopped progress on peer CPUs. It uses per-CPU heartbeat counters/cached uptimes, a low-priority clock softint, sysctl tuning, cross-calls, and IPIs to force useful panic traces.

Core state:
- `heartbeat_lock` serializes updates to `heartbeat_max_period_secs` and `heartbeat_max_period_ticks`.
- `heartbeat_sih` is the softint handle established by `heartbeat_start()`.
- Per-CPU fields include heartbeat count, cached uptime, stamp, and suspend nesting count.

Control and sysctl:
- `heartbeat_suspend()` increments the current CPU's suspend count for CPU offline transitions or polling-mode console input.
- `heartbeat_resume()` resets local heartbeat state at `splsched()` and decrements the suspend count.
- `heartbeat_resume_cpu()` resets count, uptime cache, and stamp for a CPU.
- `set_max_period()` validates overflow boundaries, resets all CPU heartbeat state when enabling from disabled state, and stores seconds/ticks values atomically.
- `heartbeat_max_period_sysctl()` implements `kern.heartbeat.max_period`, allowing runtime enable/disable and period changes with overflow checks.
- `sysctl_heartbeat_setup()` creates `kern.heartbeat` and its read/write `max_period` node.

Monitoring:
- `heartbeat_start()` establishes a low-priority MPSAFE clock softint and enables monitoring with `HEARTBEAT_MAX_PERIOD_DEFAULT`.
- `heartbeat_intr()` runs as a softint, stamps the local heartbeat count, and updates the local cached `time_uptime32`.
- `heartbeat()` is called from hard timer context with stable current CPU. It exits if disabled, locally suspended, or panicking; increments local heartbeat count; checks whether the timecounter has failed to advance for too many ticks; checks whether local softints are stuck by comparing `time_uptime32` to the softint-updated cache; schedules the softint; selects another online unsuspended CPU; and checks whether that CPU's cached uptime has advanced recently.
- `heartbeat_timecounter_suspended()` suppresses timecounter-stall panics when the primary CPU is suspended because the timecounter may not advance.
- `select_patient()` chooses the next online, unsuspended CPU after the current CPU in CPU iteration order, wrapping to the first candidate.

Failure handling:
- `defibrillate()` reports the stalled peer CPU, sends it an IPI, waits up to one second for acknowledgement, and panics locally if the peer cannot respond.
- `defibrillator()` acknowledges the IPI and panics on the stalled CPU to capture that CPU's stack, unless a panic is already in progress.
- With DDB, `heartbeat_dump()` prints per-CPU heartbeat fields safely through debugger byte reads.

Concurrency and invariants:
- Most fast-path reads/writes use relaxed atomics because heartbeat data is diagnostic/progress state.
- Enabling checks uses cross-calls so online CPUs reset local caches before the global period becomes nonzero.
- Arithmetic bounds keep uptime/tick deltas safely below 32-bit wrap concerns.

Risks and notes:
- Single-CPU systems cannot check another CPU and rely on local timecounter/softint checks.
- Some high-IPL single-CPU stalls need a hardware watchdog; the file's manual test notes call this out.
- `heartbeat_resume_cpu()` asserts current CPU stability except during cold startup.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/sys/kern/kern_heartbeat.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/sys/kern/kern_history.c -->
# File Research: sources/os/bsd/netbsd-src/sys/kern/kern_history.c

Read completely: 562 lines.

Implements kernel history diagnostics: DDB dumping for `kern_history` ring buffers and a `kern.hist.*` sysctl export format that serializes events plus a compact string table for userland. It is enabled by build options such as `KERNHIST`, `UVMHIST`, `USB_DEBUG`, `BIOHIST`, and `SYSCALL_DEBUG`.

Core state:
- `kern_histories` is the global list of registered histories.
- `kernhist_sysctl_ready` gates sysctl node creation until `sysctl_kernhist_init()` has created `kern.hist`.
- `kernhist_print_enabled` controls printing behavior.
- `sysctl_hist_node` stores the created `kern.hist` node id.

DDB support:
- `kernhist_info()` prints metadata for one history.
- `kernhist_dump()` walks one ring buffer from either its oldest entry or the last `count` entries and prints nonempty events with `kernhist_entry_print()`.
- `kernhist_dump_histories()` merges multiple histories by event bintime, repeatedly printing the earliest current event across all selected histories.
- `kernhist_dumpmask()` builds a list of selected built-in histories from a bitmask and dumps them merged.
- `kernhist_print()` is the DDB hook: with modifier `i` it prints info, otherwise it dumps either the specified history or built-in histories.

Sysctl support:
- `sysctl_kernhist_init()` creates `kern.hist`, marks sysctl ready with a producer memory barrier, and calls `sysctl_kernhist_new(NULL)` to create nodes for existing histories.
- `sysctl_kernhist_new()` creates a `CTLTYPE_STRUCT` node for any history that lacks one, after a consumer barrier confirms sysctl readiness.
- `sysctl_kernhist_helper()` rejects writes, validates the sysctl path, finds the matching history, builds a translation table of unique function/format/name strings, allocates an output `struct sysctl_history`, copies event data and string offsets, appends the string table, copyouts as much as the caller requested, and reports required size through `oldlenp`.

String-table mechanics:
- `find_string()` matches strings by address and length rather than content.
- `add_string()` appends unique address/length pairs and precomputes offsets for the final output buffer.
- Offset zero is reserved for null/unused event fields; a `"?"` fallback string is added first for entries that appear after the unique-string pass due to concurrent history updates.

Concurrency and assumptions:
- DDB paths assume the system is quiesced and do no locking.
- Sysctl export does not lock the history while taking two passes; it tolerates concurrent updates by mapping unexpected strings to the fallback entry.
- Memory barriers around `kernhist_sysctl_ready` coordinate late history registration with sysctl initialization.

Risks and notes:
- The sysctl helper allocates based on worst-case two strings per event plus name/fallback and returns `ENOMEM` when the caller buffer is too small after partial copyout.
- Merged DDB dumping ignores the `count` parameter in `kernhist_dump_histories()`.
- The source comment for `sysctl_kernhist_init()` says `hw.hist`, but the code creates `kern.hist`.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/sys/kern/kern_history.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/sys/kern/kern_hook.c -->
# File Research: sources/os/bsd/netbsd-src/sys/kern/kern_hook.c

Read completely: 742 lines.

Implements NetBSD's generic hook infrastructure and several concrete hook families: shutdown, mountroot, root-spec resolution, exec, exit, fork, critical polling, deprecated power hooks, and dynamically allocated simple hook lists with safe disestablishment while callbacks are running.

Generic hook descriptors:
- `struct hook_desc` stores a callback, argument, and list linkage.
- `hook_establish()` lazily initializes hook locks, allocates a descriptor, optionally takes a writer rwlock, and inserts the hook.
- `hook_disestablish()` optionally takes a writer rwlock, validates membership in diagnostic builds, removes the descriptor, and frees it.
- `hook_destroy()` frees an entire simple linear list.
- `hook_proc_run()` runs process callbacks under an optional reader rwlock and casts the stored callback to the process-hook signature.

Process lifecycle hooks:
- `exechook_establish()`/`exechook_disestablish()` register callbacks protected by `exec_lock`; `doexechooks()` asserts `exec_lock` is held and runs callbacks without taking it again.
- `exithook_establish()`/`exithook_disestablish()` use `exithook_lock`; `doexithooks()` runs exit callbacks under a reader lock.
- `forkhook_establish()`/`forkhook_disestablish()` use `forkhook_lock`; `doforkhooks()` runs callbacks with child and parent proc pointers under a reader lock.

Boot and shutdown hooks:
- Shutdown hooks are removed from the list before invocation in `doshutdownhooks()` so they do not run twice; the code deliberately does not free hook descriptors during shutdown.
- Mountroot hooks map a root device to a callback and include establish/disestablish/destroy/run helpers.
- Root-spec hooks register prompt prefixes and callbacks that translate strings such as wedge names to devices. Establish/disestablish require cold boot or `kernconfig` lock; lookup and printing run under `kernconfig_lock()`.

Other hook families:
- Critical polling hooks are a simple list run by `docritpollhooks()`.
- Power hooks store a name, callback, and argument in a tail queue. Suspend/powerdown callbacks run in registration order; resume callbacks run in reverse. Establish prints a deprecation warning.

Simple hook lists:
- `simplehook_create()` allocates a `khook_list_t`, initializes a mutex/CV/list, and starts in idle state.
- `simplehook_dohooks()` marks the list in use, records the active LWP and active hook, drops the list lock around each callback, skips hooks whose function has been nulled, broadcasts waiters for hooks removed while active, removes marked nodes after traversal, and returns `EBUSY` if another traversal is already running.
- `simplehook_establish()` inserts a hook under the list lock.
- `simplehook_disestablish()` removes idle hooks immediately; if hooks are running, it nulls the callback/argument, waits if another LWP is currently executing that hook, and lets `simplehook_dohooks()` free the node.
- `simplehook_has_hooks()` reports whether the list is nonempty.

Concurrency and integration:
- Global process hook families use rwlocks so registration/removal excludes callback traversal.
- Simple hook traversal explicitly supports disestablish racing with callbacks by marking callbacks null and using a CV.
- Root-spec hooks are serialized by the kernel configuration lock.

Risks and notes:
- `simplehook_dohooks()` is single-runner only; concurrent execution returns `EBUSY`.
- `simplehook_has_hooks()` only checks list emptiness, so it can report true for hooks that have been marked null but not yet removed during a traversal.
- Power hooks are deprecated but still maintained for compatibility.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/sys/kern/kern_hook.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/sys/kern/kern_idle.c -->
# File Research: sources/os/bsd/netbsd-src/sys/kern/kern_idle.c

Read completely: 131 lines.

Implements the machine-independent idle LWP loop and idle LWP creation for each CPU.

Idle loop:
- `idle_loop()` runs as the per-CPU idle LWP. It marks the CPU running in `kcpuset_running`, updates the LWP start time, sets scheduler flags, converts the LWP to `LSIDL`, drops to `spl0()`, and then loops forever.
- Each loop iteration asserts that the current LWP/CPU is the idle context, no preemption disable is held, priority is `PRI_IDLE`, and the CPU is idle.
- It calls `sched_idle()`, gives UVM a chance to perform idle work through `uvm_idle()` when the CPU is not offline, enters the MD `cpu_idle()` path if no runnable LWP exists, and otherwise switches to runnable work through `mi_switch()`.

Idle LWP creation:
- `create_idle_lwp()` creates a bound `KTHREAD_IDLE`/`KTHREAD_MPSAFE` kernel thread on the target CPU with `PRI_IDLE`.
- It marks the LWP `LW_IDLE`, stores it in `ci->ci_data.cpu_idlelwp`, and for secondary CPUs pre-sets `LSIDL`, `LP_RUNNING`, and `ci_onproc` because MD CPU startup may enter the idle LWP directly before normal scheduler switching.

Concurrency and integration:
- Relies on scheduler per-CPU lock state and assertions around `spc_lwplock`.
- Integrates with `kthread_create()`, UVM idle processing, MD `cpu_idle()`, and scheduler rescheduling flags.

Risks and notes:
- Creation failure is considered fatal and panics.
- The loop deliberately uses `spl0()` on entry because the first thread on a CPU may arrive through unusual MD startup paths.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/sys/kern/kern_idle.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/sys/kern/kern_ksyms.c -->
# File Research: sources/os/bsd/netbsd-src/sys/kern/kern_ksyms.c

Read completely: 1618 lines.

Implements in-kernel ELF symbol table management and the `/dev/ksyms` interface. It tracks the base kernel and module symbol tables, supports symbol lookup by name/address, maintains DTrace name maps when enabled, publishes tables to lockless/pserialized readers, and presents a coherent snapshot ELF image to userland for read/mmap/ioctl consumers.

Core state:
- `struct ksyms_symtab` entries are held in both `ksyms_symtabs` tail queue for writers/snapshots and `ksyms_symtabs_psz` pslist for pserialized readers.
- `kernel_symtab` stores the base kernel table.
- `ksyms_hdr`, `ksyms_symsz`, `ksyms_strsz`, and `ksyms_ctfsz` describe the synthesized user-visible ELF image.
- `ksyms_lock`, `ksyms_cv`, `ksyms_snapshotting`, and `ksyms_snapshot` serialize module changes and snapshot creation/reuse.
- `struct ksyms_snapshot` stores a refcounted UVM anonymous object, size, device, generation, and max symbol-name length for one coherent `/dev/ksyms` view.

Initialization and loading:
- `ksyms_init()` optionally loads a copied boot symbol table from `db_symtab` when `COPY_SYMTAB` is enabled, initializes the lock/CV, and creates the pserialize domain.
- `ksyms_addsyms_elf()` validates an ELF image, finds `SHT_SYMTAB` and its string table, optionally finds `.SUNW_ctf`, initializes the synthesized ELF header, and adds the base kernel table.
- `ksyms_addsyms_explicit()` supports platforms that directly know symbol/string table addresses.
- `ksyms_verify()` reports missing symbol/string tables in diagnostic/debug kernels and refuses loading absent tables.

Symbol table packing and lookup:
- `addsymtab()` filters unusable symbols when DTrace is not enabled, copies/compacts symbols to a new location, normalizes non-absolute section indices to `SHBSS`, tracks maximum symbol-name length and min/max symbol addresses, sorts globals before locals and by name, builds DTrace original-to-new symbol maps, publishes the table at `splhigh()`, recalculates aggregate sizes, and marks ksyms loaded.
- `findsym()` binary-searches sorted global symbols and, unless external-only lookup is requested, linearly searches local symbols.
- `ksyms_getval()` and `ksyms_getval_unlocked()` look up a symbol value with pserialize protection.
- `ksyms_get_mod()` returns a module symtab by name for callers that already guarantee module lifetime.
- `ksyms_mod_foreach()` iterates symbols for a module under `ksyms_lock`.
- `ksyms_getname()` finds the nearest symbol at or below an address, with filters for procedure/object/any and exact-match options.

Module integration:
- `ksyms_modload()` allocates a new symtab and DTrace name map, adds it under `ksyms_lock`, and invalidates any cached snapshot.
- `ksyms_modunload()` finds the module table, waits for active snapshot creation, removes it from both queues at `splhigh()`, waits for a pserialize grace period, recalculates sizes, invalidates the snapshot, and frees the name map and symtab.
- DDB-only `ksyms_sift()` searches and prints matching symbols, with optional type markers.

Synthesized ELF image and snapshots:
- `ksyms_hdr_init()` copies the loaded ELF header and rewrites program/section header metadata for a synthetic image containing `.note.netbsd.ident`, `.symtab`, `.strtab`, `.shstrtab`, fake `.bss`, and optional `.SUNW_ctf`.
- `ksyms_sizes_calc()` walks all tables, adjusts `st_name` offsets to concatenate string tables for userland, and recomputes aggregate symbol/string sizes.
- `ksyms_snapshot_alloc()` creates a refcounted snapshot object backed by `uao_create()`.
- `ksyms_take_snapshot()` writes the ELF header, all symbol tables up to a captured last table, all string tables, and base-kernel CTF data into the snapshot UVM object.
- `ksymsopen()` validates device/minor and loaded state, allocates a file, reuses an existing cached snapshot or becomes the single snapshotting LWP, creates/fills/caches a new snapshot, and returns a cloned file using custom fileops.

`/dev/ksyms` file operations:
- `ksymsread()` reads from the snapshot UVM object, serializing shared `f_offset` updates with the file lock, rejecting negative offsets, and returning EOF at or past snapshot size.
- `ksymsmmap()` permits read-only mappings within the rounded snapshot size by referencing the UVM object.
- `ksymsseek()` implements `SEEK_SET`, `SEEK_CUR`, and `SEEK_END` with overflow and negative-offset checks.
- `ksymsstat()` reports a character-device-like stat structure with size and generation.
- `ksymsioctl()` supports old and current value/symbol lookup ioctls plus total-size query.
- `ksymsclose()` releases the snapshot reference.
- `ksyms_cdevsw` only uses device open; all subsequent operations are on the cloned fileops.

Concurrency and invariants:
- Readers that traverse live symtabs use pserialize; unload waits for a grace period before freeing.
- Queue publication/removal happens at `splhigh()` so DDB should not see an inconsistent queue state.
- Module unload waits for snapshot creation to finish before removing tables.
- Snapshot readers use immutable UVM objects, so later module loads/unloads invalidate only the global cached snapshot, not open file views.

Risks and notes:
- `KSYMS_MAX_ID` bounds the startup static DTrace name map; excess symbols are truncated with an error message.
- Comments note TODOs for mmap/poll even though this version implements fileops mmap, suggesting the TODO is stale or refers to device-level behavior.
- `ksyms_getname()` scans all symbols linearly within candidate modules.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/sys/kern/kern_ksyms.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/sys/kern/kern_ksyms_buf.c -->
# File Research: sources/os/bsd/netbsd-src/sys/kern/kern_ksyms_buf.c

Read completely: 16 lines.

Provides the optional boot-time storage buffer for a copied kernel symbol table when `makeoptions_COPY_SYMTAB` is enabled.

Behavior:
- Includes `opt_copy_symtab.h` when kernel options are available.
- Defines `SYMTAB_FILLER` as the sentinel string used by `kern_ksyms.c` to detect whether a real symbol table has been copied into `db_symtab`.
- If `makeoptions_COPY_SYMTAB` is enabled and `SYMTAB_SPACE` is not defined, declares `db_symtab[]` initialized to the filler.
- If `SYMTAB_SPACE` is defined, declares a fixed-size `db_symtab[SYMTAB_SPACE]` initialized to the filler.
- Exports `db_symtabsize` as `sizeof(db_symtab)`.

Integration:
- `kern_ksyms.c` checks whether `db_symtab` still begins with the filler before loading copied symbols in `ksyms_init()`.

Risks and notes:
- This file is entirely compile-option gated; without `makeoptions_COPY_SYMTAB`, it emits no symbol buffer.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/sys/kern/kern_ksyms_buf.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/sys/kern/kern_kthread.c -->
# File Research: sources/os/bsd/netbsd-src/sys/kern/kern_kthread.c

Read completely: 293 lines.

Implements creation, exit, join, and FPU access control for kernel threads, represented as system-only LWPs in `proc0`.

Initialization:
- `kthread_sysinit()` initializes the global mutex/CV used for join synchronization.

Creation:
- `kthread_create()` allocates a system U-area, chooses scheduling class (`SCHED_OTHER` for `KTHREAD_TS`, otherwise `SCHED_RR`), creates a detached LWP in `proc0`, optionally names it, assigns priority, optionally binds it to a CPU, sets join/intr/MPSAFE flags, and makes it runnable unless it is an idle thread.
- `KTHREAD_IDLE` can allocate the U-area on the target CPU and leaves the LWP idle rather than runnable.
- The function requires interrupt kthreads to be MPSAFE.

Exit and join:
- `kthread_exit()` drops the kernel lock for non-MPSAFE kthreads, logs nonzero exit codes, synchronizes with a joiner for `LP_MUSTJOIN` threads by waiting until `l_private` points to a joiner's stack flag, sets that flag, broadcasts, and calls `lwp_exit()`.
- `kthread_join()` asserts it is joining a system LWP marked `LP_MUSTJOIN`, stores a pointer to a stack-local `exited` flag in the target LWP's `l_private`, wakes the target, and waits until the target sets the flag. After publishing `l_private`, it must not touch the LWP because it may be freed.

FPU access:
- `kthread_fpu_enter()` asserts thread context and system-LWP context, records whether `LW_SYSTEM_FPU` was already set, sets it, and calls MD enable logic only on the outermost entry.
- `kthread_fpu_exit()` restores the previous `LW_SYSTEM_FPU` state and calls MD zero/disable logic when leaving the outermost FPU section.

Concurrency and integration:
- Creation manipulates `proc0.p_lock` and LWP scheduler locks.
- Join uses `kthread_lock`/`kthread_cv` and a stack flag handoff to avoid dereferencing the target after it may be freed.
- Integrates with UVM system U-area allocation, KMSAN origin tagging, scheduler priority/class selection, and MD FPU hooks.

Risks and notes:
- `kthread_join()` relies on the target calling `kthread_exit()`; a must-join kthread that exits another way would not complete this handshake.
- FPU enter/exit are explicitly forbidden in hard or soft interrupt context.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/sys/kern/kern_kthread.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/sys/kern/kern_ktrace.c -->
# File Research: sources/os/bsd/netbsd-src/sys/kern/kern_ktrace.c

Read completely: 1494 lines.

Implements the core kernel tracing facility: trace descriptor management, asynchronous trace entry queueing, writer kthreads, trace record construction for many event classes, `fktrace(2)`, common trace attach/detach logic, authorization, and user trace records. The VFS path-based syscall wrapper lives in `kern_ktrace_vfs.c`.

Core structures:
- `struct ktrace_entry` contains a trace header, payload pointer/size, and small inline payload buffer.
- `struct ktr_desc` represents one trace output target, with flags, error accounting, refcount, queue count, delay/wakeup tuning, output file, writer LWP, entry queue, callout, and CVs.
- Global state includes `ktrace_lock`, `ktrace_on`, descriptor queue `ktdq`, entry pool cache, and a kauth listener.

Initialization and authorization:
- `ktrinit()` initializes `ktrace_lock`, creates the trace entry pool cache, and registers a process-scope kauth listener.
- `ktrace_listener_cb()` allows nonpersistent tracing for same real/effective/saved uid and gid relationships when the target is not persistent-traced or set-id; privileged and persistent decisions are deferred to secmodel policy.
- `ktrcanset()` asks kauth whether the caller may change tracing state on a target process.

Descriptor lifetime:
- `ktdref()` and `ktdrel()` maintain descriptor refs and global `ktrace_on`; the last release marks the descriptor done and wakes the writer thread.
- `ktd_lookup()` finds or references an existing descriptor for the same file, using `ktrsamefile()` to compare either identical file objects or matching underlying file type/data.
- `ktrderef()` clears a process trace pointer/flags, wakes sync waiters, and releases the descriptor.
- `ktradref()` adds a process reference to its trace descriptor.
- `ktrderefall()` clears all processes using a descriptor, optionally checking authorization for each.

Entry allocation and queueing:
- `ktealloc()` prevents recursive tracing with `ktrenter()`, allocates a trace entry and payload storage, initializes common header fields, timestamp, pid, command, trace format version, and LWP id.
- `ktraddentry()` handles deferred emulation records, references the descriptor, drops entries if tracing was cancelled/done or queue limit is exceeded, enqueues entries, optionally waits for writer drain under backpressure, schedules delayed writer wakeups, and frees entries on failure.
- `ktefree()` frees external payload buffers and returns entries to the pool.

Trace event producers:
- `ktr_syscall()` and `ktr_sysret()` record syscall arguments and returns.
- `ktr_namei()` and `ktr_namei2()` record path lookup strings, with optional emulation-root prefix.
- `ktr_emul()`, `ktr_execarg()`, `ktr_execenv()`, and `ktr_execfd()` record emulation and exec-related data.
- `ktr_sigmask()` records signal mask changes.
- `ktr_genio()`, `ktr_geniov()`, and `ktr_mibio()` record copied user I/O buffers through `ktr_io()`, chunking large payloads to page-sized records and yielding to preemption between chunks when needed.
- `ktr_psig()` records signal delivery and optional siginfo.
- `ktr_csw()` records context-switch out/in pairs while avoiding mutex/rwlock blocking points and interrupt/softint contexts.
- `ktruser()` implements user-provided `KTR_USER` records from user pointers; `ktr_kuser()` records kernel-provided user records; `ktr_mib()` records sysctl MIB names.
- `ktr_point()` tests the current process trace flag for one facility bit.

Trace control:
- `ktrace_common()` implements shared attach/detach behavior for path-based and fd-based interfaces. It handles clear-by-file, set with descriptor creation and writer thread startup, clear, process-group or pid targeting, descendant recursion, error/ref cleanup, and facility validation.
- `sys_fktrace()` obtains a writable file descriptor and calls `ktrace_common()`.
- `ktrops()` applies one trace operation to a process: authorizes, validates trace record version, installs or clears descriptor/facility bits, marks persistent tracing when authorized, schedules an emulation record when enabled, updates fast trace-enabled state, and reinterns syscalls if needed.
- `ktrsetchildren()` recursively walks a process tree under `proc_lock` and applies `ktrops()`.
- `sys_utrace()` is the syscall entry for user trace records.

Writer thread:
- `ktrace_thread()` waits for queued entries, detaches the whole queue, reports accumulated descriptor errors, writes entries, wakes synchronous waiters when drained, removes the descriptor from the global queue at shutdown, halts/destroys callouts, closes the output file, destroys CVs, frees the descriptor, and exits as a kthread.
- `ktrwrite()` batches headers and payloads into an iovec array, adapts header layout for trace versions 0 and 1, repeatedly calls the output file's `fo_write`, retries `EWOULDBLOCK`, stops tracing all users of the descriptor on other write errors, and frees written entries.

Concurrency and integration:
- `ktrace_lock` protects descriptors, queues, refs, and process trace pointer changes in combination with per-process locks and `proc_lock`.
- Trace producers use `ktrenter()`/`ktrexit()` recursion guards to avoid tracing trace writes or allocations recursively.
- Writer threads decouple traced processes from potentially blocking file writes while still offering synchronous waiting under queue pressure.
- Integrates with filedesc, kauth, kthreads, callouts, syscall intern hooks, signals, sysctl/MIB tracing, and ktrace version compatibility.

Risks and notes:
- Queue overflow logs `KTDE_ENOSPC` and drops entries; allocation failure TODOs remain in comments.
- Blocking writer detection sets `KTDF_BLOCKING` after timeout so traced processes are not stopped indefinitely.
- The writer-thread comment says ktrace descriptors cannot be watched by kqueue, then notes that is wrong for `fktrace`.
- `ktrace_common()` has a comment questioning why zero facilities are rejected at that point.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/sys/kern/kern_ktrace.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/sys/kern/kern_ktrace_vfs.c -->
# File Research: sources/os/bsd/netbsd-src/sys/kern/kern_ktrace_vfs.c

Read completely: 146 lines.

Implements the VFS-facing `ktrace(2)` syscall wrapper. It opens a pathname as a regular writable vnode-backed file and then delegates trace control to `ktrace_common()` in `kern_ktrace.c`.

Behavior:
- `sys_ktrace()` first enters the ktrace recursion guard with `ktrenter()`.
- For operations other than `KTROP_CLEAR`, it copies in the pathname, opens it with `vn_open()` for read/write, destroys the path buffer, unlocks the vnode, rejects non-regular files with `EACCES`, allocates a temporary file descriptor/file object, and initializes it as a writable vnode file using `vnops`.
- It calls `ktrace_common()` with the operation, facilities, target pid, and optional file pointer.
- For file-requiring operations, it aborts the temporary fd with `fd_abort()` after `ktrace_common()` has consumed or referenced the file as needed.

Integration:
- This file isolates explicit VFS path handling from the trace core, which also supports fd-based tracing through `sys_fktrace()`.
- Uses pathbuf, vnode open/close, file descriptor allocation, and vnode fileops.

Risks and notes:
- The temporary file descriptor consumes a descriptor slot in the tracing process for the duration of the syscall; the source comments state this is expected not to matter.
- On `fd_allocfile()` failure, the code closes the vnode with `FWRITE` even though it was opened with `FREAD|FWRITE`.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/sys/kern/kern_ktrace_vfs.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/sys/kern/kern_lock.c -->
# File Research: sources/os/bsd/netbsd-src/sys/kern/kern_lock.c

Read completely: 469 lines.

Implements the legacy global kernel lock, sleepability assertions, lock debug hooks, spinout diagnostics, and nested acquire/release accounting. This file is central to code paths that still rely on the big kernel lock while coexisting with adaptive mutexes, preemption, lockstat, and DTrace probes.

Core state:
- `kernel_lock_cacheline` stores the simple lock and volatile holder CPU on a cacheline-aligned object; `kernel_lock` is a strong alias.
- `kernel_lock_holder` records the CPU that most recently acquired the lock.
- `kernel_lock_dodebug` tracks lockdebug registration state.
- SDT probes record kernel lock entry and exit with the number of holds.

Sleepability:
- `assert_sleepable()` panics if called from idle context, hard interrupt, soft interrupt, or a pserialize read section, except during panic. It avoids changing preemption state and samples `lwp_pctr()` until stable before checking idle state.

Initialization and debug:
- `kernel_lock_init()` initializes the simple lock and registers it with lockdebug.
- `_kernel_lock_dump()` prints current CPU biglock count and waiter pointer for lockdebug/DDB-style diagnostics.
- `kernel_lock_trace_ipi()` prints and optionally stacktraces the CPU that is holding the kernel lock too long.
- `kernel_lock_spinout()` rate-limits reports, identifies the holder CPU, avoids self-reporting races, sends an IPI to collect the holder stack, and triggers a lockdebug abort in LOCKDEBUG kernels.

Acquire path:
- `_kernel_lock(nlocks)` raises to `splvm()`, handles recursive acquisition by incrementing per-CPU `ci_biglock_count` and LWP `l_blcnt`, and otherwise tries the simple lock fast path.
- On contention, it sets `ci_biglock_wanted` with memory barriers to coordinate with adaptive mutex owner/waiter logic, records lockstat spin timing, spins with backoff while temporarily lowering/restoring IPL, reports spinout after 10 seconds once init exec has started, then records holder/count/debug state after acquiring.
- After acquisition, it restores the previous wanted pointer with atomic swap and a matching memory barrier so mutex waiters see consistent ordering.

Release path:
- `_kernel_unlock(nlocks, countp)` releases one, all, or the special `-1` hold, updates LWP/per-CPU hold counts, fully unlocks the simple lock when the count reaches zero, optionally preempts if `l_dopreempt` is set, emits the exit SDT probe, and returns the previous hold count through `countp`.
- `_kernel_locked_p()` reports the raw simple-lock state.

Concurrency and integration:
- Per-LWP `l_blcnt` and per-CPU `ci_biglock_count` implement nesting and ownership accounting.
- Memory barriers around `ci_biglock_wanted` are paired with adaptive mutex entry/exit ordering.
- Lockstat records spin time for initial acquisition, not recursive holds.
- DTrace SDT probes, lockdebug, DDB, IPIs, preemption, and SPL handling all participate in diagnostics and correctness.

Risks and notes:
- The source explicitly warns that `_kernel_lock()` behavior is relied on by much of the kernel.
- `kernel_lock_holder` is diagnostic and can be unreliable without holding the lock; spinout code treats it cautiously.
- `_kernel_unlock()` asserts `nlocks < 2`, with zero meaning release all and `-1` meaning release exactly one from a single-hold state.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/sys/kern/kern_lock.c -->