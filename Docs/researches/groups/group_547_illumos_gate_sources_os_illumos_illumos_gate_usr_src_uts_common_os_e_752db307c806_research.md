# Group Research: group_547_illumos_gate_sources_os_illumos_illumos_gate_usr_src_uts_common_os_e_752db307c806

Scope confirmed against `Docs/research_subset_a.md`: all files are under `sources/os/illumos/illumos-gate`. Each listed source file was read completely.

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/os/exec.c -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/os/exec.c

## Purpose

`exec.c` implements the generic illumos kernel `exec(2)` path: syscall entry, executable lookup, exec-switch dispatch, permission and privilege handling, process state replacement, VM/address-space replacement, stack construction, auxiliary-vector string placement, and exec-module lookup.

It is central process lifecycle code, with heavy coupling to VFS/vnodes, credentials/privileges, `/proc`, brands/zones, DTrace, resource controls, doors, schedctl, timers, lwp management, and VM segment mapping.

## Main Entry Points

- `exece()` (`exec.c:134`) is the syscall wrapper. It validates flags and supports `EXEC_DESCRIPTOR`, where the `file` argument is interpreted as an fd. For descriptor exec it obtains a vnode with `fgetstartvp()`, tries to copy `vp->v_path`, and falls back to `/dev/fd/<fd>` if no cached path exists.
- `exec_common()` (`exec.c:197`) performs pathname or vnode setup, brand policy checks, `/proc` exec-start notification, signal hold adjustments, `pfexec` integration, and calls `gexec()`. On success it completes process-state reset and returns to the new image.
- `gexec()` (`exec.c:637`) performs generic executable validation, opens the vnode, reads magic bytes, finds the exec handler, computes credential/setid/secflag transitions, invokes the format-specific `exec_func`, and commits new credentials and tracing state.
- `exec_args()` (`exec.c:2002`) builds the new process stack, terminates other LWPs, tears down exec-sensitive state, replaces the address space, sets stack/heap metadata, and installs optional 64-bit stack guard mapping.

## Exec Flow

`exec_common()` rejects `/proc` agent LWP execs, enforces brand transitions, and calls `prexecstart()` while temporarily holding default-ignored signals. It either uses a supplied vnode or resolves the user pathname with `pn_get()` and `lookuppn()`, preserving both the executable pathname and the containing directory for `p_execdir`.

Before format dispatch, it enforces `secpolicy_basic_exec()`, rejects execution from attribute directories in the specific current-directory case, stores accounting command text, and optionally calls `pfexec_call()` when `PRIV_PFEXEC` is set. It initializes default stack/data protections, fires DTrace `proc:::exec`, applies process branding if needed, and calls `gexec()`.

After `gexec()` succeeds, the old process image is considered replaced. `exec_common()` frees floating-point state and context ops, clears accounting fork state and DTrace predicate cache, clears contract templates, updates `p_execdir`, resets signal stack/signal disposition metadata, refreshes saved rlimits, clears profiling, closes `FD_CLOEXEC` descriptors via `close_exec()`, clears native brand state if requested, calls `setregs()`, marks the vnode `VVMEXEC`, and rebuilds the process LWP directory/hash so the now-single-threaded process has LWP id 1.

## Permission, Format, and Credential Handling

`execpermissions()` (`exec.c:1214`) gets mode/uid/gid/size attributes, checks `VEXEC`, verifies regular file or `/proc` object file, rejects `VFS_NOEXEC`, and requires at least one execute mode bit. For traced processes it may also require read permission or arrange `/proc` invalidation.

`gexec()` opens the executable vnode with `VOP_OPEN()`, reads `MAGIC_BYTES`, resolves the handler with `findexec_by_hdr()`, and holds the exec switch entry with `hold_execsw()`. It calculates setuid/setgid/forced privilege behavior via `execsetid()` and promotes inheritable secflags with `secflags_promote()` before calling the format-specific `exec_func`.

`execsetid()` (`exec.c:1111`) evaluates `VFS_NOSETUID`, `VSUID`, `VSGID`, forced privileges for setuid-root programs, privilege-aware reset needs, inherited/limit/permitted privilege relationships, MAC awareness flags, and ptrace compatibility. It returns flags indicating whether credentials, privilege sets, MAC flags, or setuid protections must change.

On successful level-0 exec, `gexec()` closes the previous executable vnode, installs new credentials on both process and current thread, updates saved uid/gid, sets `SNOCD|SUGID` when privilege increased or effective ids differ, updates per-uid process counts if real uid changed, handles `/proc` invalidation, and sends `SIGTRAP` for ptrace compatibility.

## Exec Switch Management

- `allocate_execsw()` installs an exec switch name and magic bytes into the global `execsw` table.
- `findexecsw()`, `findexec_by_hdr()`, and `findexec_by_magic()` locate handlers by magic bytes.
- `hold_execsw()` acquires the handler reader lock and autoloads the corresponding `exec` module with `modload()` until `LOADED_EXEC()` is true.

The exec switch lock is intentionally held across `exec_func()` and released immediately after the format-specific handler returns.

## VM and Segment Mapping

`execmap()` (`exec.c:1261`) maps file-backed executable sections or copies them into anonymous mappings. It page-aligns addresses and offsets, validates user ranges, uses `VOP_MAP()` for page-mapped segments, optionally prefaults small segments, and adjusts memory deficit accounting when not prefaulting.

For zero-fill-on-demand trailing data, it carefully handles partial pages. If the last page lacks write permission, it temporarily adds `PROT_WRITE`, zeroes with `uzero()` under `on_fault()`, and restores protections. Remaining zfod space is mapped with `segvn_create`, using large-page mapping hints when `szc` is set.

`setexecenv()` updates process brk/bss metadata and swaps `p_exec` vnode references.

## Stack Construction

The stack-building helpers use an in-kernel staging buffer where strings grow upward from `stk_base` and string offsets grow downward from the top.

- `stk_add()` copies strings from user or kernel space into the staging buffer.
- `stk_getptr()` and `stk_putptr()` handle native versus 32-bit pointer models.
- `stk_copyin()` copies interpreter arguments, original argv, environment, optional `pfexec`-scrubbed environment variables, and aux-vector strings into the staging buffer.
- `stk_copyout()` writes `argc`, argv pointers, envp pointers, string data, and aux-vector string addresses to the new user stack. It also records `u_argc`, `u_argv`, `u_envp`, and `u_psargs`.

`exec_get_spslew()` supplies stack-pointer ASLR when `PROC_SEC_ASLR` is enabled; on `sun4v`, it can provide cache-coloring skew even without ASLR.

`exec_args()` selects native or ILP32 stack model, repeatedly grows the staging buffer until arguments fit or `NCARGS`/`NCARGS32` is exceeded, then calls `exitlwps()` to make the process single-threaded. It revokes process doors, cleans schedctl/DTrace/lwpchan/timer state, audits arguments, uses pool barriers around `relvm()`, resets process address-space metadata, allocates a fresh `as`, joins the executable vnode’s shared region domain with `hat_join_srd()`, copies out the new stack, and for 64-bit processes maps a `seg_hole` stack guard.

## Error and Fatality Boundaries

Before old VM destruction, errors unwind with errno and restore signal holds, exec-start state, secflags, credentials, vnode opens, and brand state as appropriate. After `relvm()` in `exec_args()`, comments state errors are fatal to the execing process; callers must treat `-1`/post-destruction failure as requiring process death.

## External Interactions

This file is tightly integrated with:

- VFS/vnode operations: `lookuppn()`, `VOP_ACCESS()`, `VOP_GETATTR()`, `VOP_OPEN()`, `VOP_CLOSE()`, `VOP_MAP()`, `vn_rdwr()`.
- Descriptor table code in `fio.c`: `fgetstartvp()`, `close_exec()`, `falloc()`, `setf()`, `closeandsetf()`.
- Process exit/LWP code: `exitlwps()`, LWP directory/hash rebuild, `lwp_exit()` behavior on failure paths.
- VM: `relvm()`, `as_alloc()`, `as_map()`, `as_setprot()`, `segvn_create`, `seghole_create`.
- Security: privileges, secflags, setuid/setgid, `pfexec`, MAC flags, noexec stack policy.
- Observability: `/proc`, DTrace, audit, accounting.

## Research Notes

The most delicate invariants are around the boundary where the old process image is still recoverable versus after `relvm()`, credential replacement under `p_crlock`, `execsw` module locking, and keeping `/proc`/tracing semantics consistent while mutating process identity and address space.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/os/exec.c -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/os/exit.c -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/os/exit.c

## Purpose

`exit.c` implements process termination, zombie creation, child wait status collection, process table detachment, resource/accounting cleanup, and special handling for zone init restart or shutdown. It is the counterpart to `exec.c` in process lifecycle management.

## Main Entry Points

- `rexit()` (`exit.c:137`) implements the simple exit syscall wrapper by calling `exit(CLD_EXITED, rval)`.
- `exit()` (`exit.c:317`) calls `proc_exit()` and, if another LWP already owns process exit, falls into `lwp_exit()`.
- `proc_exit()` (`exit.c:462`) is the full process-exit state machine.
- `waitid()` (`exit.c:1055`) implements wait semantics over child process state.
- `freeproc()` (`exit.c:1342`) frees zombie process state after the parent has accepted it or the process evaporates.

## Wait Status Helpers

`wstat()` converts `CLD_*` code/data pairs into traditional wait status bits. `exit_reason()` formats a short diagnostic string for zone init failure/restart messages. `winfo()` fills kernel `siginfo` for wait operations and optionally clears wait state and `CLDPEND`.

## Zone Init Restart Handling

`restart_init()` (`exit.c:155`) is called when a zone’s init exits but policy says it should be restarted. It logs the reason, cleans file descriptors with `pollcleanup()` and `closeall()`, resets process flags, signal state, queued signal info, current/root directories, cwd refstr, secflags, credentials, and controlling tty. It then calls `exec_init()` for the zone init path.

`zone_init_exit()` (`exit.c:352`) decides whether to restart, reboot, halt, or proceed with normal exit when the zone init exits. It considers boot errors, zone/global shutdown state, `zone_restart_init`, `zone_reboot_on_init_exit`, and `zone_restart_init_0`.

This path is unusual because successful restart returns through the normal syscall path rather than continuing process teardown.

## Process Exit Flow

`proc_exit()` first marks the process exiting with `proc_is_exiting()`, calls `exitlwps()` to remove other LWPs, accounts remaining process ticks to the task, fires DTrace exit probes, and clears brand state.

If the process is the zone init, `zone_init_exit()` may restart it and return. Otherwise the function proceeds with teardown:

- Calls `lwp_pcb_exit()`.
- Allocates a `sigqueue_t` for `SIGCLD` unless the process will evaporate.
- Revokes doors, releases schedctl state, waits for AIO cleanup, destroys lwpchan cache, cleans DTrace helpers and signalfd state.
- Removes interval timers, alarm timeout, realtime profile cyclics, and upanic state.
- Runs `pollcleanup()` before descriptor closure.
- Enters `p_lock`, cleans DTrace probes, cancels `p_itimerid`, runs `lwp_cleanup()`, enters pool barrier, blocks `/proc` via `prbarrier()`, clears pending signals and signal info, marks current thread `TP_LWPEXIT`, removes LWP hash state, calls `prexit()`, sets `p_lwpcnt = 0`, clears thread list, frees sigqueues, terminates microstate accounting, and detaches executable vnode pointers.

After dropping `p_lock`, it frees watched pages, closes all files, releases controlling tty, frees SPARC utraps, exits SysV semaphore state, performs accounting/audit/exacct, frees address space with `relvm()`, closes/releases `p_exec`, releases `p_execdir`, exits contracts, leaves process contracts, and removes pool association.

## Parent/Child and Zombie State

Under `pidlock`, `proc_exit()` removes the exiting process from the parent’s newstate list, reassigns orphan relationships to next-of-kin, reparents children to `proc_init`, kills ptraced reparented children, and posts state for zombie children as needed.

It then aggregates task and child resource usage, sets `p_stat = SZOMB`, clears ptrace compatibility flag, stores wait data/code, snapshots cwd/root/cwd refstr references for later release, frees resource controls, decrements task/project/zone LWP counters, clears LWP directory/hash structures, runs process-context exit hooks, and temporarily points `curthread` at `zsched` or `p0` so zone references remain valid while the process may be freed.

If not evaporating, `sigcld()` notifies the parent. If evaporating, it mimics ignored `SIGCHLD`, broadcasts `p_srwchan_cv`, and immediately calls `freeproc()`.

Finally it releases cwd/root/cwd references, moves the thread to `p0`, frees LWP directory/hash memory including retired hash tables, and calls `thread_exit()`.

## Wait Implementation

`waitid()` validates options and id type, strips obsolete `_WNOCHLD`, and scans child state under `pidlock`.

It optimizes the common `P_ALL | WNOHANG | WEXITED` case by checking `p_child_ns`. The main loop first scans `p_child_ns` for exited/dumped/killed children, respecting `CLDWAITPID` and `WNOWAIT`. If a waitable child is found, it fills `siginfo`, optionally frees the process, drops `pidlock`, and updates SIGCLD bookkeeping.

If no child on the newstate list qualifies, it scans all children for trapped/stopped/continued states and validates stopped state with `jobstopped()`. It returns `ECHILD`, zeroed `siginfo` for `WNOHANG`, or waits interruptibly on the parent condition variable.

`waitsys()` and `waitsys32()` are syscall wrappers that copy out native or 32-bit siginfo.

## Process Freeing

`freeproc()` assumes a zombie with no thread list under `pidlock`. It clears remaining signal queues, informs `/proc` with `prfree()`, preserves `proc_init`, decrements per-uid process count, frees credentials and core-control references, propagates child CPU/accounting/resource usage to next-of-kin when appropriate, removes orphan links, detaches task/project membership, detaches from parent child lists, releases pid/proc memory through `pid_exit()`, and releases the task.

`proc_detach()` removes a process from its parent’s child list and newstate list. `delete_ns()` and `add_ns()` maintain the parent newstate list.

## External Interactions

This file coordinates with:

- `exec.c`: `restart_init()` uses `exec_init()` after resetting state.
- Descriptor management in `fio.c`: `closeall()` and poll cleanup.
- VFS/vnodes: executable/current/root directory reference release and close.
- VM: `relvm()`.
- Process contracts, tasks, projects, zones, pools, and resource controls.
- `/proc`, DTrace, audit, exacct, accounting, signal and wait subsystems.

## Research Notes

The important invariants are single-LWP ownership of process exit, the `pidlock` ordering around child lists and zombie state, delayed release of cwd/root until after `SZOMB`, and careful `curthread->t_procp` reassignment so late vnode/task releases still have a valid zone context.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/os/exit.c -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/os/fbio.c -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/os/fbio.c

## Purpose

`fbio.c` implements pseudo-buffer-I/O routines backed by `segmap` mappings. It gives filesystem/kernel code an `fbuf` abstraction for accessing file data through locked kernel virtual addresses, then releasing or writing those mappings through `segmap_release()`.

## Main Operations

- `fbread()` maps a `MAXBSIZE`-aligned file window with `segmap_getmapflt()`, validates that `off + len` stays within a `MAXBSIZE` boundary, soft-locks the pages with `segmap_fault(F_SOFTLOCK)`, allocates an `fbuf`, and returns `fb_addr` pointing at the requested byte offset.
- `fbzero()` maps or creates pages for a file range, allocates an `fbuf`, calls `segmap_pagecreate()`, and zeroes the requested page-rounded memory region.
- `fbrelse()` releases a read or other mapping without forcing writeback.
- `fbwrite()` releases with `SM_WRITE` for direct writeback.
- `fbdwrite()` releases without `SM_WRITE`, corresponding to delayed-write style behavior.
- `fbiwrite()` writes an fbuf synchronously to an indirect block/device vnode through a temporary `buf` from `pageio_setup()` and `bdev_strategy()`.

## Shared Release Logic

The `FBCOMMON` macro computes the page-rounded region containing the fbuf, soft-unlocks it with `segmap_fault(F_SOFTUNLOCK)`, frees the `fbuf`, and releases the base segmap mapping with the caller-supplied flags. It is used for normal release, direct write, delayed write, and the cleanup half of indirect write.

## VM/VFS Interaction

The file depends on:

- `segkmap` and `segmap_getmapflt()`/`segmap_getmap()`.
- `segmap_fault()` for soft-lock and soft-unlock.
- `segmap_pagecreate()` for zero-fill/create behavior.
- `segmap_release()` for final mapping release and writeback policy.
- `pageio_setup()`, `bdev_strategy()`, `biowait()`, and `pageio_done()` for synchronous device write in `fbiwrite()`.

## Constraints and Edge Cases

Both `fbread()` and `fbzero()` panic if the requested range crosses a `MAXBSIZE` boundary. `fbzero()` contains an explicit warning that it will not work correctly when filesystem block size is smaller than `PAGESIZE`. `fbread()` converts object fault errors to the underlying errno when `FC_CODE(err) == FC_OBJERR`, otherwise returning `EIO`.

## Research Notes

This is a small but sensitive bridge between filesystem logical byte ranges and VM-backed kernel mappings. Correctness depends on strict `MAXBSIZE` windowing, balanced softlock/softunlock, and the caller choosing the right release/writeback variant.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/os/fbio.c -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/os/fio.c -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/os/fio.c

## Purpose

`fio.c` implements kernel file descriptor and `file_t` management: descriptor allocation, descriptor-table growth, get/release reference tracking, close/replacement, fork/exec/exit descriptor handling, file object allocation/freeing, fd flags, `*at()` start-vnode helpers, poll/event-port descriptor associations, and zone-change checks.

It is foundational VFS/process glue and is used heavily by exec, exit, open/close/fcntl, poll, event ports, and auditing.

## Descriptor Allocation Model

The file descriptor table is represented as an infix binary tree embedded in an array of `uf_entry_t`. Each entry’s `uf_alloc` tracks allocation counts for descriptor-search subtrees. The large comment at the top derives the math for `fd_find()`, `fd_reserve()`, `flist_minsize()`, and `flist_nalloc()`.

- `fd_find()` finds the smallest free fd >= `minfd` in `O(log n)`.
- `fd_reserve()` increments or decrements allocation counts along left ancestors and toggles `uf_busy`.
- `flist_minsize()` finds the minimum table size needed for fork copying.
- `flist_nalloc()` counts currently allocated descriptors.
- `flist_grow()` expands `fi_list` to a `2^n - 1` size, copies entries, uses memory barriers to publish `fi_list` before `fi_nfiles`, wakes waiters on old condition variables, and retires old tables on `fi_rlist` for later exit cleanup.

The grow path is concurrency-heavy: it locks old entries and visible new entries to preserve `UF_ENTER()` semantics while the array pointer changes.

## Active File Descriptor Tracking

Each thread has `t_activefd`, used to detect and interrupt syscalls using an fd that another LWP is closing.

- `set_active_fd()` records fd activity and grows the per-thread active-fd buffer if needed.
- `clear_active_fd()` removes a recorded active fd.
- `is_active_fd()` checks another thread under its active-fd lock.
- `clear_stale_fd()` runs from `post_syscall()` to clear stale state.
- `free_afd()` frees or resets active-fd buffers.

This supports `closeandsetf()` invalidating concurrent users without stopping every LWP.

## File Lookup, Release, and Close

`getf_gen()` validates fd range, reserves active-fd space, locks the descriptor entry, increments `uf_refcnt`, optionally returns generation, records the active fd, and returns the `file_t`. `getf()` is the simple wrapper.

`releasef()` decrements `uf_refcnt`, clears the active fd, and wakes close waiters when the count reaches zero. `areleasef()` performs the same reference drop against an explicitly supplied `uf_info_t`.

`closeandsetf()` is the core close/replace path. It handles table growth for installing a new file, waits for reserved-but-not-yet-filled slots, rejects the process poison fd, removes the old `uf_file`, wakes other LWPs using the fd by marking active-fd stale state, waits for `uf_refcnt` to drain, cleans poll cache and event port associations, calls `closef()`, and finally installs `newfp` with `setf()`.

`closef()` decrements the `file_t` reference count, calls `VOP_CLOSE()` with the current count/flags/offset, removes OFD locks on the last reference, invokes a DTrace close barrier if installed, releases the vnode, frees audit and credential state, and returns the `file_t` to `file_cache`.

## Allocation and File Object Lifecycle

- `ufalloc_file()` combines descriptor allocation and optional immediate `file_t` installation, enforcing `RLIMIT_NOFILE`.
- `ufalloc()` allocates a reserved descriptor with no file pointer.
- `ufcanalloc()` estimates whether a process can allocate a future number of fds and triggers rctl action on likely failure.
- `falloc()` allocates a `file_t`, initializes flags, offset, vnode, credential hold, and audit state, optionally reserving an fd first. It returns the `file_t` locked.
- `unfalloc()` undoes a failed allocation path.
- `finit()` creates the `file_cache` kmem cache.

`setf()` installs or clears a descriptor slot, updates descriptor generation when installing a real file, broadcasts waiters, and audits the fd assignment.

## Fork, Exec, and Exit Descriptor Handling

`flist_fork()` copies the parent descriptor table into the child when fork has already reduced parent concurrency. It preserves files and flags except descriptors marked `FD_CLOFORK`, which are omitted from the child and unreserved in allocation accounting.

`fcntl_add()` increments or decrements `file_t` reference counts across fork success/failure.

`close_exec()` is called by exec. It closes descriptors marked `FD_CLOEXEC` and writable self-open `/proc` descriptors, clears poll/event-port state, and closes the underlying file. It also clears `FD_CLOFORK` on surviving descriptors, deliberately diverging from early POSIX 2024 wording to avoid surprising post-exec descriptor disappearance. Finally it resets the poison fd state.

`closeall()` is the exit path: because exit is single-threaded, it iterates without locking, closes every open file, removes event-port associations, frees `fi_list`, and frees retired descriptor lists.

## Descriptor Flags and Poison FD

`f_getfl()` returns file status flags plus BSD-compatible socket `FASYNC` state. `f_getfd_error()` returns fd flags and forces `FD_CLOEXEC` for writable self-open `/proc` files. `f_getfd()` is the getf-era wrapper.

`f_setfd_int()` updates `FD_CLOEXEC`/`FD_CLOFORK`, either replacing or OR-ing flags. `f_setfd_error()` and `f_setfd_or()` expose that behavior.

`f_badfd()` allocates a “poison” bad fd for ILP32 compatibility cases. The selected fd cannot be reused normally; attempts to use it can trigger configured signal action. It is restricted to fd 3 through 255 and only one poison fd may exist per process.

## Vnode Helpers and Zone Checks

`fassign()` allocates a descriptor and `file_t`, opens a vnode with `VOP_OPEN()`, installs the vnode into the file, and publishes the fd.

`fgetstartvp()` is used by `*at()` syscalls and descriptor exec. It returns a held starting vnode for `(fd, path)` unless `AT_FDCWD` or an absolute path means normal cwd/root lookup should apply.

`fsetattrat()` implements common `fchownat()`/`fchmodat()` setup: obtains start vnode, optionally audits, resolves path with follow/no-follow semantics, rejects chmod of symlinks, rejects readonly filesystems, then calls `VOP_SETATTR()`.

`fisopen()` checks whether the current process has a vnode open. `files_can_change_zones()` returns false if any open file’s vnode disallows zone changes.

## Poll and Event Port Associations

The file tracks fd-to-poll cache membership with `fpollinfo_t` lists:

- `addfpollinfo()` records current thread polling an fd.
- `delfpollinfo()` removes it.
- Debug-only `checkfpollinfo()` and `infpollinfo()` assert/inspect membership.

Event port associations are tracked with `portfd_t` lists:

- `addfd_port()` links a port fd entry into a descriptor.
- `delfd_port()` unlinks it.
- `port_close_fd()` closes all event port associations for a descriptor after the descriptor slot has been cleared.

## External Interactions

This file is coupled to VFS (`VOP_CLOSE`, `VOP_OPEN`, `VOP_SETATTR`, vnode references), process limits/resource controls, `/proc` self-open semantics, poll cache cleanup, event ports, DTrace close barriers, audit hooks, credentials, fork/exec/exit paths, and zone migration policy.

## Research Notes

The most important invariants are descriptor-table publication ordering in `flist_grow()`, `uf_refcnt` draining before fd reuse, active-fd stale signaling for concurrent close, correct accounting through `fd_reserve()`, and fork/exec special handling for `FD_CLOFORK`, `FD_CLOEXEC`, and writable self-open `/proc` descriptors.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/os/fio.c -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/os/firmload.c -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/os/firmload.c

## Purpose

`firmload.c` provides a small firmware-loading API for device drivers. It is derived from NetBSD’s firmload interface and adapted to illumos kernel object loading primitives.

## Data Model

`struct firmware_handle` contains:

- `fh_buf`: a `struct _buf *` returned by `kobj_open_path()`.
- `fh_size`: cached firmware file size.

Handles are allocated and freed with small wrappers around `kmem_alloc()` and `kmem_free()`.

## API Functions

`firmware_open()` validates `drvname`, `imgname`, and output handle pointer. It constructs `firmware/<drvname>/<imgname>` with `kmem_asprintf()`, allocates a handle, opens the image with `kobj_open_path(path, 1, 0)`, frees the path string, and maps open failure to `ENOENT`. It then retrieves file size with `kobj_get_filesize()`; on failure it closes the file and frees the handle. On success it stores the handle in `*fhp`.

`firmware_close()` closes the kobj file and frees the handle when non-NULL. It always returns 0.

`firmware_get_size()` asserts a non-NULL handle and returns the cached size.

`firmware_read()` asserts a non-NULL handle and reads `len` bytes from `offset` into `buf` via `kobj_read_file()`. It returns `0` on success and `-1` on read failure, matching the underlying kobj convention rather than errno-style reporting.

## External Interactions

The implementation depends on the kernel runtime linker/object APIs:

- `kobj_open_path()`
- `kobj_get_filesize()`
- `kobj_read_file()`
- `kobj_close_file()`

It also uses kernel allocation helpers and string allocation/freeing.

## Research Notes

This is intentionally minimal: it does no path normalization beyond fixed `firmware/<driver>/<image>` construction, caches only size and open buffer, and leaves firmware interpretation to callers. The main cleanup invariant is that every successful `kobj_open_path()` is closed by `firmware_close()` or the error path after failed size lookup.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/os/firmload.c -->