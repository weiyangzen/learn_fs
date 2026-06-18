# Group Research: group_1260_netbsd_src_sources_os_bsd_netbsd_src_sys_kern_kern_entropy_c_source_a8eb2c93be90

Scope checked against `Docs/research_subset_a.md`: all requested files are under `sources/os/bsd/netbsd-src`, which is included in subset A. All three listed source files were read completely.

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/sys/kern/kern_entropy.c -->
# File Research: sources/os/bsd/netbsd-src/sys/kern/kern_entropy.c

Read completely: 2855 lines.

Implements NetBSD's kernel entropy subsystem and legacy random-source compatibility API. The design centers on per-CPU entropy input pools, a global extraction pool, accounting for trusted entropy bits and timing samples, asynchronous consolidation, `/dev/random` readiness notifications, entropy source registration, on-demand source callbacks, and legacy `rnd(9)`/`rndio(4)` ioctls.

Core state:
- `struct entropy_cpu` holds each CPU's `entpool`, pending bit/sample counters, and drop/truncation/softint event counters.
- `entropy_global` (`E`) holds the global pool, entropy deficits, pending aggregate counts, epoch, select/kqueue waiters, source-list lock state, registered `krndsource` list, and seed/consolidation flags.
- `struct rndsource_cpu` keeps per-source per-CPU contributed bit/sample statistics and timer-delta estimator state.

Initialization and seeding:
- `entropy_init()` runs the `entpool` self-test, creates `kern.entropy.*` sysctls, initializes locks/CVs/select state, attaches the synthetic `seed` rndsource, allocates per-source/per-CPU state, and mixes early timer samples.
- `entropy_init_late()` establishes the entropy softint and starts the housekeeping thread `entbutler`.
- `entropy_seed()` validates a bootloader seed checksum with SHA1, handles byte-swapped/corrupt entropy counts, prevents double-counting repeated seeds, enters the seed, and zeroes it.
- `entropy_bootrequest()` requests entropy from all callback-capable sources before userland.

Entropy ingestion:
- `entropy_enter()` is the full non-interrupt path. It binds the LWP to the current CPU, enters data into the per-CPU pool, updates pending counters, then calls `entropy_account_cpu()` when consolidation may matter.
- `entropy_enter_intr()` is the interrupt/spin-lock path. It avoids blocking, drops samples if the per-CPU pool is busy, uses `entpool_enter_nostir()`, schedules the softint if stirring or accounting is needed, and only credits entropy if the whole sample fit.
- `entropy_softintr()` stirs the per-CPU pool after interrupt truncation and accounts pending entropy.
- Early boot uses `entropy_enter_early()` to enter data directly into the global pool under `splhigh()`.

Consolidation and readiness:
- `entropy_account_cpu()` performs immediate global transition when one CPU can satisfy the remaining bit deficit, otherwise aggregates pending counts and wakes the housekeeping thread when enough bits or samples exist across CPUs.
- `entropy_thread()` periodically checks `entropy_pending()` or waits for `E->consolidate`, then calls `entropy_do_consolidate()`.
- `entropy_do_consolidate()` broadcasts `entropy_consolidate_xc()` to extract each CPU pool into a temporary pool, mixes it into the global pool, decrements deficits, records timestamps, and calls `entropy_notify()`.
- `entropy_notify()` advances the entropy epoch, prints first readiness/best-effort messages, wakes CV waiters, and notifies poll/kqueue readers.
- `entropy_epoch()` and `entropy_ready()` expose reseed/readiness state to other kernel code.
- `entropy_reset()` handles VM clone/exposure-style resets by clearing pending counters on all CPUs and restoring maximum deficits.

Extraction and readiness APIs:
- `entropy_extract()` fills caller buffers from the global pool, optionally waiting, optionally failing hard, and warning/reresetting deficits when output is produced before full entropy. It supports the test-only `kern.entropy.depletion` mode.
- `entropy_poll()` and `entropy_kqfilter()` implement `/dev/random` style readiness for select/poll/kqueue. Readiness depends on either bit or sample deficit being zero unless depletion testing is active; writes are always ready.

Random source API and ioctls:
- `rnd_attach_source()`, `rnd_detach_source()`, and `rndsource_setcb()` manage kernel entropy sources and optional request callbacks.
- `rnd_add_data()`, `rnd_add_data_intr()`, `rnd_add_uint32()`, `_rnd_add_uint32()`, `_rnd_add_uint64()`, and `rnd_add_data_sync()` feed source data/timer samples through `rnd_add_data_internal()` and `rnd_add_data_1()`.
- Source flags honor `RND_FLAG_NO_COLLECT`, `RND_FLAG_NO_ESTIMATE`, `RND_FLAG_COLLECT_VALUE`, `RND_FLAG_COLLECT_TIME`, `RND_FLAG_ESTIMATE_TIME`, and `RND_FLAG_HASCB`; network sources default to no collection.
- `entropy_request()` serializes source callbacks with `rnd_lock_sources()` so detach cannot race callback traversal.
- `entropy_ioctl()` implements `RNDGETENTCNT`, `RNDGETPOOLSTAT`, source/stat enumeration by number or name, `RNDCTL` flag changes with reset/gather side effects, and `RNDADDDATA` user seed injection. Unknown legacy commands are forwarded through compatibility module hooks.

Concurrency and integration:
- Per-CPU pool access is protected by `entropy_cpu_get()`/`entropy_cpu_put()`, which block soft interrupts and preemption on the current CPU but deliberately allow hard-interrupt callers to drop samples instead of blocking.
- Global state is protected by `E->lock` after cold boot; selected counters are read with relaxed atomics for fast readiness checks.
- Source-list locking is separate (`E->sourcelock`) to allow callers to drop `E->lock` while invoking source callbacks.
- Integrates with sysctl, evcnt, softint, xcall, kthread, select, kqueue, kauth, module compatibility hooks, and the `entpool` cryptographic pool implementation.

Risks and notes:
- The code intentionally exposes only limited counters because event counters can become side channels.
- The timer entropy estimator is simple differential logic and only credits one sample, not bit entropy.
- `RNDCTL` can reset all pending entropy when collection/estimation is disabled for a trusted source.
- `RNDADDDATA` counts user-provided entropy only for privileged callers and only if a bootloader seed was not already counted.
- `entropy_extract()` can still fill buffers on shortage unless `ENTROPY_HARDFAIL` is set; callers are warned to use output only for CPRNG/DRBG seeding.
- Several comments flag policy concerns: writable sysctls at securelevel, readable deficit sysctls, legacy anonymous `rnd_add_data(NULL)`, and interrupt-context callers using the non-intr API.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/sys/kern/kern_entropy.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/sys/kern/kern_event.c -->
# File Research: sources/os/bsd/netbsd-src/sys/kern/kern_event.c

Read completely: 3042 lines.

Implements NetBSD's kqueue/kevent subsystem, including kqueue file operations, kevent registration/scanning, built-in and dynamically registered filters, knote lifetime management, process/timer/user filters, klist helpers used by backing objects, and the kernel-facing notification API.

Core structures and filter registry:
- `struct knote_impl` wraps public `struct knote` with a private in-flux counter and per-knote filter-operation lock.
- `sys_kfilters[]` maps built-in filters: read, write, vnode, proc, signal, timer, fs, user, empty, and placeholders for unsupported AIO.
- `kfilter_register()` and `kfilter_unregister()` maintain dynamically registered user filters under `kqueue_filter_lock`, with per-filter refcounts preventing unregister while in use.
- `kqueue_init()` initializes the filter lock and registers a kauth listener that permits process-event monitoring for same-uid non-SUGID processes.

Locking and lifetime model:
- The file documents a strict order: `kqueue_filter_lock` -> filedesc `fd_lock` -> knote `foplock` -> backing-object lock -> kqueue spin lock.
- `filter_attach()`, `filter_detach()`, `filter_event()`, and `filter_touch()` wrap filterops and acquire the big kernel lock for non-MPSAFE filters.
- `klist_fini()` neuters knotes by replacing their filterops with no-op stubs while holding each knote's foplock, preventing use-after-free of backing objects or module code.
- The in-flux protocol (`kn_enter_flux()`, `kn_leave_flux()`, `kn_wait_flux()`, `knote_detach_quiesce()`) lets complex submitters such as process fork tracking drop locks temporarily while preventing concurrent detach/free.

Kqueue system calls and file operations:
- `kqueue1()`, `sys_kqueue()`, and `sys_kqueue1()` allocate a kqueue file, initialize `kq_lock`, CV, select state, queue head, descriptor state, and optional close-on-exec.
- `sys___kevent100()` and `kevent1()` copy in changes in bounded chunks, register each change, optionally return EV_RECEIPT/EV_ERROR results, then scan for pending events.
- `kqueue_ioctl()` maps filter IDs to names and names to filter IDs for `KFILTER_BYFILTER` and `KFILTER_BYNAME`.
- `kqueue_poll()`, `kqueue_stat()`, `kqueue_kqfilter()`, `kqueue_restart()`, and `kqueue_close()` provide normal file behavior for kqueue descriptors.
- `kqueue_close()` marks `KQ_CLOSING`, walks fd-attached and hash-attached knote lists, detaches all knotes, then destroys kqueue resources.

Registration and scanning:
- `kqueue_register()` validates filters, finds existing knotes by fd list or internal hash, handles `EV_ADD`, `EV_DELETE`, enable/disable updates, `f_touch` updates for supported filters, immediate `f_event` checks, and filter refcounts.
- `kqueue_scan()` waits with optional timeout, uses a marker knote to bound queue traversal, coordinates with in-flux/detaching knotes, re-polls non-oneshot events, copies out events in chunks, handles `EV_ONESHOT`, `EV_CLEAR`, and `EV_DISPATCH`, and wakes flux waiters when traversal state changes.
- `knote_enqueue()`, `knote_activate_locked()`, `knote_activate()`, and `knote_deactivate_locked()` maintain the active/queued state, event count, CV wakeups, and select notifications.
- `knote_detach()` removes a knote from the monitored object, descriptor/hash table, and kqueue queue, drops fd references for fd filters, decrements filter refcount, and frees the knote.

Built-in filters:
- File filters (`EVFILT_READ`, `EVFILT_WRITE`, `EVFILT_VNODE`, `EVFILT_EMPTY`) delegate attach to the file's `fo_kqfilter`.
- Kqueue-read filters report pending kqueue event count and are used when monitoring a kqueue descriptor.
- Process filters attach to `p_klist`, enforce kauth, mask user-provided internal `NOTE_CHILD`, and support `NOTE_EXEC`, `NOTE_FORK`, `NOTE_TRACK`, `NOTE_TRACKERR`, and `NOTE_EXIT`.
- `knote_proc_exec()`, `knote_proc_fork()`, and `knote_proc_exit()` submit process lifecycle notifications; fork tracking allocates both a one-shot `NOTE_CHILD` event and a new child-tracking knote.
- Timer filters convert event data across seconds/milliseconds/microseconds/nanoseconds, support relative and absolute `NOTE_ABSTIME`, allocate callouts with a global limit, reschedule repeating timers, and support safe reconfiguration through `f_touch`.
- User filters are purely kqueue-local and support `NOTE_TRIGGER`, `NOTE_FFNOP`, `NOTE_FFAND`, `NOTE_FFOR`, `NOTE_FFCOPY`, `EV_CLEAR`, and `f_touch`.
- `seltrue_filtops` and `seltrue_kqfilter()` provide always-ready read/write filters for simple devices.

Klist API:
- `knote()` walks a backing object's `klist` and activates knotes whose `f_event` returns true; the backing object is assumed to hold its own lock.
- `knote_fdclose()` detaches all knotes for a closing file descriptor.
- `knote_set_eof()` and `knote_clear_eof()` update EOF flags under the kqueue lock.
- `klist_init()`, `klist_fini()`, `klist_insert()`, and `klist_remove()` are the backing-object list helpers.

Risks and notes:
- The in-flux detach protocol is essential; violating it can free knotes while fork tracking or scan traversal still expects them to exist.
- `filter_touch()` is deliberately allowed only for known-safe timer and user filters during registration because it does not take the foplock.
- `kqueue_register()` contains a comment noting `hashinit()` can block while `fd_lock` is held.
- Process fork tracking uses `KM_NOSLEEP`; allocation failure is reported as `NOTE_TRACKERR`.
- Timer callouts are globally capped by `kq_calloutmax`; attaching a timer can fail with `ENOMEM`.
- Kqueue stat reports a dummy FIFO-like object with size equal to pending events.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/sys/kern/kern_event.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/sys/kern/kern_exec.c -->
# File Research: sources/os/bsd/netbsd-src/sys/kern/kern_exec.c

Read completely: 2993 lines.

Implements NetBSD process image replacement and spawn support: `execve(2)`, `fexecve(2)`, `posix_spawn(2)`, executable format dispatch, exec argument buffering/copyout, VM command execution, credentials and emulation switching, signal trampoline mapping, and dynamic exec format registration.

Core state and initialization:
- `execsw`/`nexecs` is the ordered executable-format switch table, protected by global `exec_lock`.
- `ex_head` stores dynamically registered `struct exec_entry` records.
- `struct execve_data` carries the `exec_package`, path buffers, vnode attributes, argument buffer, ps_strings state, resolved name, signal-code size, argument counts, and copied argument length across exec phases.
- `struct spawn_exec_data` carries prepared exec state, file actions, attributes, parent pointer, child-ready synchronization, error status, and a refcount for `posix_spawn`.
- `exec_init()` initializes the exec lock, exec argument submap/pool, sorts exec handlers by priority, rebuilds the `execsw` array, and recomputes `exec_maxhdrsz`.

Executable lookup and format dispatch:
- `check_exec()` resolves either path-based or fd-based executables, requires a regular vnode with execute access, applies `MNT_NOEXEC`/`MNT_NOSUID`, opens the vnode for read, reads the maximum exec header, runs veriexec and PaX segvguard checks when enabled, sets default VM bounds, then tries each registered exec handler's `es_makecmds()`.
- Handler success is followed by entry-address and data/text size limit checks. Handler failure resets fields that a probe may have modified.
- Script/indirect destructive failures can return early via `EXEC_DESTR`.
- `exec_autoload()` attempts to load native or compatibility exec modules after `ENOEXEC`, depending on whether any exec handlers are already present.
- `exec_makepathbuf()` copies user/kernel paths into a `pathbuf`, converting relative paths to absolute paths via the process cwd.
- `exec_resolvename()` resolves vnode-to-path for `fexecve()` style execution.

Exec load phase:
- `execve_loadvm()` enforces `RLIMIT_NPROC` for SUGID cases, takes `p_reflock` writer to block debugger/procfs references, builds path state, initializes the exec package, enters `exec_lock` as reader, calls `check_exec()`, allocates the NCARGS argument buffer, copies arguments/environment, calculates argument and stack sizes, and returns prepared state.
- `copyinargs()` handles fake interpreter arguments (`EXEC_HASARGL`), `EXEC_SKIPARG`, user argv, and environment strings.
- `copyinargstrs()` fetches argument pointers through an abstract fetch callback, copies strings into the kernel argument buffer, enforces `ARG_MAX`, and emits ktrace argument/environment records.
- `calcargs()` and `calcstack()` account for argc/argv/envp pointers, aux data, ASLR stack gap, signal trampoline, `ps_strings`, and machine stack alignment.

Exec commit phase:
- `execve_runproc()` converts prepared state into the live process image. It kills other LWPs, releases robust futexes and lwpctl state, removes POSIX timers, applies PaX flags, replaces the VM space with `uvmspace_exec()`, records text/data/stack sizing, closes close-on-exec descriptors, resets caught signals, marks `PK_EXEC`, and updates credentials through `credexec()`.
- `credexec()` handles setuid/setgid transitions, requires an argument list for set-id binaries, ensures fd 0..2 are open, drops non-persistent ktrace, updates effective and saved credentials, and updates process master credentials.
- `execve_dovmcmds()` runs loader-provided VM commands, handles relative VM commands, records `p_textvp`, then closes/releases the executable vnode.
- `copyoutargs()` and `copyoutpsstrs()` copy argv/env/aux structures and `ps_strings` into the new user stack.
- The commit path runs exec hooks, initializes machine registers via emulation and format hooks, clears LWP private state, discards PCU state, maps sigcode, notifies `EVFILT_PROC` listeners via `knote_proc_exec()`, switches emulation via `emulexec()`, releases locks, and handles ptrace/stop-on-exec behavior.
- If commit fails after the old image has been destroyed, the non-spawn path exits the process with `SIGABRT`; spawn returns the error through its child path.

Signal trampoline and emulation:
- `exec_sigcode_alloc()` creates/refcounts an anonymous UVM object for an emulation's signal trampoline, maps it writable in the kernel to copy code, then later maps it read/execute into processes.
- `exec_sigcode_map()` chooses a user VA through the emulation's address chooser and maps the trampoline into the new process, recording `p_sigctx.ps_sigcode`.
- `exec_sigcode_free()` drops references and clears the emulation sigobject pointer for the last user.
- `emulexec()` installs emulation root, calls old/new emulation process hooks, updates `p_emul`/`p_execsw`, interns syscall handling, and updates ktrace emulation state.

Exec format registration:
- `exec_add()` rejects duplicate handler triples, allocates `exec_entry` records, allocates sigcode objects for emulations, inserts handlers, and rebuilds `execsw`.
- `exec_remove()` refuses removal while any process uses the target `p_execsw`, removes entries, frees sigcode references, and rebuilds `execsw`.
- `exec_free_emul_arg()` frees loader-provided emulation arguments through the package callback.

Posix spawn:
- `check_posix_spawn()` increments global process count, performs fork authorization, and enforces per-user process limits.
- `sys_posix_spawn()` copies file actions and attributes, calls `do_posix_spawn()`, copies out the child pid, and returns errors through `retval` as NetBSD's syscall convention requires here.
- `posix_spawn_fa_alloc()` copies action arrays and duplicates path strings from user memory; `posix_spawn_fa_free()` releases them.
- `do_posix_spawn()` runs `execve_loadvm()` in the parent first, allocates a U-area and new process, initializes process/LWP structures, copies credentials/fd/cwd/limits/signal state, installs spawn data, creates the child LWP at `spawn_return()`, inserts the child into global process lists, makes it runnable, waits for child-ready status, and coordinates ptrace `PTRACE_POSIX_SPAWN` events.
- `spawn_return()` runs in the child, optionally releases the parent early if it can take `exec_lock` itself and no parent-sensitive attrs/errors require waiting, applies spawn attrs and file actions, then calls `execve_runproc()` with spawn-specific lock ownership. It reports child-side errors to the parent when required or exits 127 for POSIX child-side failure behavior.
- `handle_posix_spawn_attrs()` handles process group, scheduler attributes, reset IDs, signal mask, and default signal actions while temporarily making the child visible as stopped for pid-based operations.
- `handle_posix_spawn_file_actions()` performs open/dup2/close/chdir/fchdir actions in the child before exec commit.

Risks and notes:
- `p_reflock` and `exec_lock` ownership is split between normal exec and spawn paths; spawn has explicit `no_local_exec_lock` handling to support parent-held locks.
- `execve_runproc()` has a point of no return after `uvmspace_exec()`; later failures terminate the old process image rather than restoring it.
- Set-id exec refuses zero-argument execution and forces standard descriptors open before credential changes.
- `copyinargstrs()` relies on `ARG_MAX` remaining within the NCARGS pool allocation.
- `check_exec()` tries all handlers under `exec_lock` and can autoload modules on `ENOEXEC`; loader probe functions must clean up modified package state on failure.
- `posix_spawn()` error reporting intentionally differs depending on whether the parent is still waiting and whether `POSIX_SPAWN_RETURNERROR` was requested.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/sys/kern/kern_exec.c -->