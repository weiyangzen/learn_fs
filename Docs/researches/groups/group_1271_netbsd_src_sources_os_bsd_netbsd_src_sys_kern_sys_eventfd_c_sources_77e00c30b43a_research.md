# Group Research: group_1271_netbsd_src_sources_os_bsd_netbsd_src_sys_kern_sys_eventfd_c_sources_77e00c30b43a

Scope checked against `Docs/research_subset_a.md`; all files are under `sources/os/bsd/netbsd-src`, which is included in subset A. Every source file listed for this group was read completely and summarized separately below.

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/sys/kern/sys_eventfd.c -->
# File Research: sources/os/bsd/netbsd-src/sys/kern/sys_eventfd.c

Read completely: 588 lines.

Implements NetBSD's Linux-compatible `eventfd(2)` object: a descriptor-backed 64-bit counter that can be read, written, polled, selected, and monitored with kqueue.

Main interfaces:
- `do_eventfd` and `sys_eventfd` validate `EFD_CLOEXEC`, `EFD_NONBLOCK`, and `EFD_SEMAPHORE`, allocate a descriptor, and attach `DTYPE_EVENTFD` fileops.
- `eventfd_fop_read` blocks until the counter is nonzero, then returns either `1` in semaphore mode or the full counter and resets/decrements it.
- `eventfd_fop_write` imports an `eventfd_t`, rejects the overflow sentinel value, waits for counter capacity, and increments the counter.
- `eventfd_fop_poll`, `eventfd_fop_kqfilter`, `eventfd_ioctl`, `eventfd_fop_stat`, `eventfd_fop_close`, and `eventfd_fop_restart` provide descriptor behavior.

State/control flow: `struct eventfd` owns a mutex, read/write condition variables, read/write `selinfo`, counter value, waiter count, restart flag, semaphore mode flag, and timestamps. Blocking read/write loops hold `efd_lock`, call `eventfd_wait`, update access/modify timestamps, and use `eventfd_wake` to notify the opposite side. `fo_restart` marks `efd_restarting` and broadcasts so blocked syscalls return `ERESTART` and descriptor close/revalidation can proceed.

Dependencies/integration: file descriptor allocation (`fd_allocfile`, `fd_affix`), generic `fileops`, `uiomove`, `selnotify`, kqueue filterops, stat metadata, credentials, and close-on-exec descriptor handling.

Reliability notes: `eventfd_destroy` asserts there are no waiters, so close/restart ordering matters. Write-side errors restore `uio_resid` after the initial `uiomove` so generic write accounting reports errors correctly. `FIONSPACE` passes through because write readiness depends on the specific value being written. Linux's kernel-internal overflow `POLLERR` case is intentionally unreachable through normal read/write.

Filesystem relevance: indirect but important descriptor substrate. It is a pseudo-file object with fileops/stat/poll/kqueue behavior, but no VFS vnode or persistent filesystem state.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/sys/kern/sys_eventfd.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/sys/kern/sys_futex.c -->
# File Research: sources/os/bsd/netbsd-src/sys/kern/sys_futex.c

Read completely: 2130 lines.

Implements NetBSD futex syscalls: userspace-addressed wait/wake synchronization, exact futex identity tracking, requeue operations, wake-op atomic update semantics, bitset waits, and Linux-style robust futex list cleanup on LWP exit.

Main interfaces:
- `futex_sys_init` and `futex_sys_fini` initialize/finalize global futex rb-trees.
- `do_futex` and `sys___futex` dispatch `FUTEX_WAIT`, `FUTEX_WAKE`, `FUTEX_REQUEUE`, `FUTEX_CMP_REQUEUE`, `FUTEX_WAIT_BITSET`, `FUTEX_WAKE_BITSET`, and `FUTEX_WAKE_OP`.
- `sys___futex_set_robust_list` and `sys___futex_get_robust_list` manage per-LWP robust-list head pointers.
- `futex_release_all_lwp` scans and releases robust futexes for a dying LWP.
- Lookup/refcount helpers include `futex_lookup`, `futex_lookup_create`, `futex_insert`, `futex_hold`, and `futex_rele`.

State/control flow: futex identity is exact, not hash-approximate. Private futexes are keyed by `vmspace + va`; shared futexes are keyed by `uvm_voaddr`. Global `futex_tab` stores separate rb-trees. Each `struct futex` has a refcount, queue lock, waiter queue, abort lock/list, and key. Each waiter is a `struct futex_wait` with its own mutex/cv, current futex pointer, bitset, and abort state. `FUTEX_WAIT` tests the user word before lookup and again under the futex queue lock before enqueueing to avoid missed wakeups. `futex_wake` wakes matching waiters or transfers them to a second futex for requeue operations. `FUTEX_WAKE_OP` performs a userland atomic compare-and-swap update under queue locks, then wakes one or both queues depending on the comparison result.

Dependencies/integration: UVM address/object identity (`uvm_voaddr_*`), user atomic access helpers (`ufetch_int`, `ucas_int`), condition variables, rb-trees, LWP IDs, process/LWP lookup, compat-netbsd32 robust-list layouts, and robust-list ABI constants.

Reliability notes: lock ordering is explicit and delicate: `futex_tab.lock`, futex queue locks ordered by futex address, waiter locks, and abort locks. `futex_wait_abort` handles a lock-order reversal by publishing the waiter on an abort list before taking the queue lock. Refcount overflow is treated as `ENFILE`; requeue reference transfer asserts destination holds do not fail. Robust-list cleanup is best-effort and can abandon malformed, unmapped, looping, or racing userspace lists. Priority inheritance is explicitly unsupported.

Filesystem relevance: indirect. Futexes synchronize userspace runtimes that may perform filesystem I/O, but this file implements process/VM synchronization, not filesystem or vnode behavior.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/sys/kern/sys_futex.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/sys/kern/sys_generic.c -->
# File Research: sources/os/bsd/netbsd-src/sys/kern/sys_generic.c

Read completely: 706 lines.

Implements generic file-related syscalls for read, write, vectored I/O, and ioctl dispatch over NetBSD `fileops`.

Main interfaces:
- `sys_read` and `dofileread` validate descriptor/read permission, build a single-iovec `uio`, call `fo_read`, trace I/O, and return transferred byte count.
- `sys_readv` and `do_filereadv` copy/use iovec arrays, enforce `IOV_MAX` and `SSIZE_MAX`, optionally seek, and call `fo_read`.
- `sys_write` and `dofilewrite` mirror the read path and generate `SIGPIPE` on `EPIPE` unless `FNOSIGPIPE` is set.
- `sys_writev` and `do_filewritev` provide vectored write handling and tracing.
- `sys_ioctl` stages ioctl arguments, handles descriptor-level commands, normalizes disklabel ioctl sizes, and dispatches `fo_ioctl`.

State/control flow: I/O paths hold a file reference from `fd_getfile` until `fd_putfile`. They convert user buffers into `uio` structures for the caller's VM space, clamp transfers to `SSIZE_MAX`, and suppress `EINTR`, `ERESTART`, and `EWOULDBLOCK` after partial transfer. Vectored I/O uses a small stack iovec array where possible and heap allocation for larger vectors. `sys_ioctl` chooses stack or heap staging buffers based on encoded ioctl length and zeroes output buffers before copyout.

Dependencies/integration: descriptor table lookup, `fileops`, `uio`, ktrace, signals, vnode/file object implementations, disklabel compatibility, descriptor flag updates for `FNONBLOCK`/`FASYNC`, and generic ioctl pass-through semantics.

Reliability notes: explicit offset callers must not alias `fp->f_offset` where seek validation is needed. Partial-transfer behavior intentionally masks selected restart/interruption errors. `FIONBIO` and `FIOASYNC` update `f_flag` around non-atomic fileops dispatch, as noted by comments. Ioctl encoded sizes, disklabel compatibility, and output zeroing are ABI-sensitive.

Filesystem relevance: high. This is a core syscall-to-`fileops` bridge used by VFS vnodes, pipes, sockets, devices, memfd, eventfd, and other descriptor-backed objects.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/sys/kern/sys_generic.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/sys/kern/sys_getrandom.c -->
# File Research: sources/os/bsd/netbsd-src/sys/kern/sys_getrandom.c

Read completely: 245 lines.

Implements `getrandom(2)` and shared random-data generation logic for user buffers via `uio`.

Main interfaces:
- `sys_getrandom` validates `GRND_RANDOM`, `GRND_INSECURE`, and `GRND_NONBLOCK`, constructs a single-iovec `uio`, calls `dogetrandom`, and returns a byte count with partial-success semantics.
- `dogetrandom` fills the supplied `uio` using either the fast per-CPU CPRNG or a local NIST Hash DRBG seeded from the entropy pool.

State/control flow: short non-`GRND_RANDOM` reads use `cprng_strong(user_cprng)` when entropy is ready or insecure output is allowed. Otherwise the function extracts seed material, instantiates a NIST Hash DRBG, generates output in 512-byte chunks, reseeds when the DRBG interval is exhausted, checks for pending signals after progress, and wipes seed/buffer material before freeing. `/dev/random`-style output is clamped to entropy capacity/seed size and stops after one buffer.

Dependencies/integration: entropy pool APIs, CPRNG, NIST Hash DRBG, `uiomove`, signal pending checks, preemption points, and process VM-space `uio` setup.

Reliability notes: `GRND_RANDOM | GRND_INSECURE` is rejected. `GRND_NONBLOCK` prevents waiting for full entropy unless insecure output is allowed. Large requests may return partial data if reseeding fails or a signal is pending after data transfer. Temporary sensitive buffers are explicitly zeroed.

Filesystem relevance: indirect. It is not a filesystem implementation, but its `uio` helper style overlaps with character-device random reads and generic user-buffer transfer paths.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/sys/kern/sys_getrandom.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/sys/kern/sys_lwp.c -->
# File Research: sources/os/bsd/netbsd-src/sys/kern/sys_lwp.c

Read completely: 766 lines.

Implements user-facing lightweight process syscalls: LWP creation, exit, identity/private data, suspend/continue/wait/kill/detach, park/unpark synchronization, naming, and user control page allocation.

Main interfaces:
- `sys__lwp_create`, `do_lwp_create`, and `mi_startlwp` create LWPs from user contexts and report traced creation events.
- `sys__lwp_exit`, `sys__lwp_self`, `sys__lwp_getprivate`, and `sys__lwp_setprivate` handle identity and per-LWP private pointer state.
- `sys__lwp_suspend`, `sys__lwp_continue`, `sys__lwp_wait`, `sys__lwp_detach`, and `sys__lwp_kill` manage LWP state and signaling.
- `lwp_park`, `lwp_unpark`, `sys____lwp_park60`, `sys__lwp_unpark`, and `sys__lwp_unpark_all` implement park/unpark synchronization.
- `sys__lwp_setname`, `sys__lwp_getname`, and `sys__lwp_ctl` manage LWP names and shared user/kernel control pages.

State/control flow: LWP creation copies and validates `ucontext_t`, allocates a U-area, calls `lwp_create`, and starts the new LWP only after copying out the new LID. Park/unpark uses `lwp_park_syncobj` and `LW_UNPARKED`/`LW_CANCELLED` flags to avoid lost wakeups when unpark races with a later park. Suspend/continue/wait paths hold process locks and use LWP locks around state transitions.

Dependencies/integration: process/LWP lifecycle from `kern_lwp.c`, CPU context validation, UVM U-area allocation, sleep queues, ptrace event reporting, signal delivery, pserialize lookup for unlocked LWP scans, and `lwpctl` user-control pages.

Reliability notes: `_lwp_create` must free copied contexts and U-areas correctly on copyout/start failure. Self-suspend and all-LWP suspension have deadlock checks, with comments noting races around runnable counts. `lwp_unpark` handles targets that have not parked yet by setting `LW_UNPARKED`. Timed park can return remaining relative time to userland. Detached zombie cleanup may release the process lock through `lwp_free`.

Filesystem relevance: indirect. LWPs are scheduler/thread substrate for filesystem syscalls, blocking I/O, and synchronization, but this file does not implement filesystem behavior.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/sys/kern/sys_lwp.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/sys/kern/sys_memfd.c -->
# File Research: sources/os/bsd/netbsd-src/sys/kern/sys_memfd.c

Read completely: 463 lines.

Implements `memfd_create(2)`: anonymous memory-backed file descriptors with Linux-style sealing, read/write, mmap, seek, stat, and truncate behavior.

Main interfaces:
- `sys_memfd_create` validates flags, creates `struct memfd`, creates a UVM anonymous object, names it `memfd:<name>`, and attaches `DTYPE_MEMFD` fileops.
- `memfd_read` and `memfd_write` transfer data through `ubc_uiomove`.
- `memfd_fcntl` supports `F_GETPATH`, `F_ADD_SEALS`, and `F_GET_SEALS`.
- `memfd_mmap` returns the underlying UVM object with protection and size checks.
- `memfd_seek`, `memfd_truncate`, `memfd_truncate_locked`, `memfd_stat`, and `memfd_close` implement regular-file-like behavior.

State/control flow: each descriptor owns logical size, UVM object, seal mask, name, and timestamps. Reads clamp to current size. Writes reject write seals, enforce grow seals, extend via truncate when needed, update offsets when requested, and refresh timestamps. Truncation grows with zero-fill or shrinks by freeing backing pages through object paging operations.

Dependencies/integration: descriptor allocation, `fileops`, `uao_create`/`uao_detach`, UBC transfers, UVM object references for mmap, `fcntl` sealing ABI, credentials for stat ownership, and close-on-exec/close-on-fork descriptor flags.

Reliability notes: adding `F_SEAL_WRITE` is rejected when the object has extra references, approximating active mmap protection; a comment notes this should ideally detect writable mappings specifically. `F_SEAL_FUTURE_WRITE` and `F_SEAL_WRITE` both deny writes. `mmap` rejects ranges beyond the logical size and shared writable mappings under write seals. Shrinking relies on UVM object paging operations that may drop/reacquire the object lock.

Filesystem relevance: high for virtual-filesystem research. It is an anonymous, memory-backed file implementation outside a mounted filesystem, but it shares file operation, mmap, truncate, and stat semantics with regular files.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/sys/kern/sys_memfd.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/sys/kern/sys_module.c -->
# File Research: sources/os/bsd/netbsd-src/sys/kern/sys_module.c

Read completely: 334 lines.

Implements `modctl(2)` syscall support for loading, unloading, querying, existence checks, and compatibility dispatch for kernel modules.

Main interfaces:
- `sys_modctl` dispatches `MODCTL_LOAD`, `MODCTL_UNLOAD`, `MODCTL_STAT`, `MODCTL_EXISTS`, and compatibility hooks.
- `handle_modctl_load` copies a module path and optional property dictionary string, parses properties, and calls `module_load`.
- `handle_modctl_stat` snapshots active and built-in module metadata into user-provided iovec storage.

State/control flow: load validates optional property pointer/length pairing, bounds property input to `MAXPROPSLEN`, copies the module path through a pathname buffer, internalizes properties, and releases temporary objects. Stat holds `kernconfig_lock`, counts modules and required-module strings, copies metadata into kernel buffers, unlocks, then copies the count, `modstat_t` array, required-module strings, and final iovec length to userland.

Dependencies/integration: kernel module lists, kobj stats, kauth kernel-pointer visibility checks, property dictionaries, module autoloading, syscall compatibility hooks, and kernel config locking.

Reliability notes: kernel object addresses are exposed only when `KAUTH_REQ_PROCESS_CANSEE_KPTR` permits it. Output is truncated to the caller's iovec length while reporting the full required size. Module-list sizing is protected by `kernconfig_lock`. Property strings are size-limited to reduce allocation abuse.

Filesystem relevance: indirect. Module loading may load filesystem modules and uses a pathname for the module file, but this file is module-management syscall glue rather than filesystem logic.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/sys/kern/sys_module.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/sys/kern/sys_mqueue.c -->
# File Research: sources/os/bsd/netbsd-src/sys/kern/sys_mqueue.c

Read completely: 1218 lines.

Implements POSIX message queues as named, descriptor-backed kernel objects with send/receive, timed waits, notification, attributes, unlink, poll, stat, sysctl, and module registration.

Main interfaces:
- `mqueue_sysinit`, `mqueue_sysfini`, `mqueue_modcmd`, and `mqueue_syscalls` establish module/syscall state.
- `mq_handle_open`, `mqueue_create`, `mqueue_lookup`, and `mqueue_get` implement open/lookup/reference behavior.
- `mq_send1`, `sys_mq_send`, `sys___mq_timedsend50`, `mq_recv1`, `sys_mq_receive`, and `sys___mq_timedreceive50` implement I/O.
- `sys_mq_notify`, `sys_mq_getattr`, `sys_mq_setattr`, `sys_mq_unlink`, and `sys_mq_close` implement control operations.
- `mq_poll_fop`, `mq_stat_fop`, and `mq_close_fop` provide descriptor fileops.

State/control flow: global `mqueue_head` name state is protected by `mqlist_lock`. Each queue has `mq_mtx`, condition variables, select info, reference count, attributes, owner/mode, message priority queues, and optional notification target. Send allocates/copies a message, blocks while full unless nonblocking/timed out, inserts by priority, optionally sends SIGEV_SIGNAL notification, then wakes receivers. Receive blocks while empty, removes the highest-priority message, wakes senders, and copies message/prio to userland after releasing the queue lock.

Dependencies/integration: descriptor `fileops`, per-process mqueue count accounting, `genfs_can_access` for mode checks, kauth unlink permissions, pool cache for default-sized messages, condition variables, poll/select, signals, sysctl tunables, and module syscall establishment.

Reliability notes: comments acknowledge POSIX-sensitive behavior where receive can remove a message even if copyout fails. `mq_setattr` applies `O_NONBLOCK` before optional old-attribute copyout, also noted as POSIX-sensitive. `mq_prio_max` sysctl growth can force high-priority messages into a reserved sorted queue. Unlink removes the name, marks live queues `MQ_UNLINKED`, wakes blocked send/receive waiters, and defers destruction until last close/reference release.

Filesystem relevance: moderate. POSIX mqueues are named descriptor objects with permission/mode/stat behavior resembling filesystem nodes, but they live in kernel lists rather than VFS directories.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/sys/kern/sys_mqueue.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/sys/kern/sys_pipe.c -->
# File Research: sources/os/bsd/netbsd-src/sys/kern/sys_pipe.c

Read completely: 1201 lines.

Implements high-performance kernel pipes as paired `DTYPE_PIPE` file descriptors backed by pageable kernel virtual buffers, replacing the older socket-based pipe behavior.

Main interfaces:
- `pipe_init` initializes reader/writer pipe pool caches.
- `pipe1` creates paired read/write file descriptors, pipe structures, shared lock, peer links, and descriptor flags.
- `pipe_read` and `pipe_write` implement circular-buffer blocking I/O with `PIPE_BUF` atomicity guarantees.
- `pipe_ioctl`, `pipe_poll`, `pipe_kqfilter`, `pipe_stat`, `pipe_close`, `pipe_restart`, `pipe_fpathconf`, and `pipe_posix_fadvise` provide descriptor operations.
- Buffer/lifecycle helpers include `pipe_create`, `pipespace`, `pipe_free_kmem`, `pipeclose`, `pipelock`, `pipeunlock`, and `pipeselwakeup`.

State/control flow: each endpoint has a `struct pipe`, peer pointer, shared mutex, condition variables, select info, state flags, timestamps, and a circular `pipebuf`. The read endpoint preallocates normal pipe KVA; write-side buffering is through the peer. Large writes can expand an empty pipe to `BIG_PIPE_SIZE` subject to `maxbigpipes`. Reads block on `pipe_rcv`, writes block on `pipe_wcv`, and both coordinate long-running I/O with `PIPE_LOCKFL`.

Dependencies/integration: descriptor allocation, `fileops`, UVM pageable kernel mappings, pool caches, `uiomove`, select/poll/kqueue, async I/O ownership/signals, stat metadata, sysctl pipe counters, and generic close/restart handling.

Reliability notes: close sets `PIPE_EOF`, wakes peer waiters, waits for busy I/O to drain, and clears remaining kqueue internals directly. Nonblocking read has an unlocked fast path using atomic loads for parallel empty-pipe probes. `PIPE_RESTART` converts blocked syscalls to `ERESTART` for descriptor revalidation during close. Buffer resize/free must maintain `nbigpipe` and `amountpipekva` accounting. Poll/write readiness references the peer, so closed-peer paths must avoid stale pointer use.

Filesystem relevance: high descriptor/VFS-adjacent relevance. Pipes are non-vnode file objects with read/write/poll/stat/kqueue semantics and are central to Unix file descriptor behavior.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/sys/kern/sys_pipe.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/sys/kern/sys_process.c -->
# File Research: sources/os/bsd/netbsd-src/sys/kern/sys_process.c

Read completely: 199 lines.

Provides process memory access support used by ptrace and ktrace, plus a hook symbol required by ptrace module linkage.

Main interfaces:
- `process_domem` performs traced-process memory I/O through `uvm_io`.
- `ptrace_hooks` is a dummy symbol under `PTRACE_HOOKS` so `ptrace_common` load fails if hooks are unavailable.

State/control flow: `process_domem` rejects zero-length operations early, checks the target LWP is not exiting and its VM space is live, takes a VM-space reference, performs `uvm_io` with PaX mprotect-derived access permissions, optionally calls `pmap_procwr` after successful writes for architectures needing instruction-cache/process-write maintenance, then releases the VM-space reference.

Dependencies/integration: target process VM space, UVM map I/O, PaX mprotect policy, machine pmap hooks, ptrace/ktrace configuration, and LWP exit state.

Reliability notes: target VM lifetime is protected by explicit `uvmspace_addref`/`uvmspace_free`. Writes may need machine-dependent coherency repair through `pmap_procwr`. Access permissions are mediated through `pax_mprotect_prot`.

Filesystem relevance: low. It is process debugging memory I/O support, not filesystem logic, though ptrace can observe or modify processes performing filesystem operations.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/sys/kern/sys_process.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/sys/kern/sys_process_lwpstatus.c -->
# File Research: sources/os/bsd/netbsd-src/sys/kern/sys_process_lwpstatus.c

Read completely: 282 lines.

Implements ptrace/process helpers for reading LWP status and register sets, including compat-netbsd32 register layout handling.

Main interfaces:
- `ptrace_read_lwpstatus` and `process_read_lwpstatus` fill `ptrace_lwpstatus` from an LWP.
- `ptrace_update_lwp` switches a held target LWP reference to a requested LID.
- `process_validregs`, `process_validfpregs`, and `process_validdbregs` validate register access availability and reject system LWPs.
- `process_doregs`, `process_dofpregs`, and `process_dodbregs` read/write general, floating-point, and debug registers via `uio`.
- `proc_regio` is the common register-buffer transfer helper when register ptrace support is compiled in.

State/control flow: LWP status includes LID, signal mask, pending signal set, LWP name, and private pointer. Register I/O reads the machine register set into a kernel buffer, transfers the requested slice with `uiomove`, and writes back only for `UIO_WRITE` if the target LWP is stopped.

Dependencies/integration: machine `process_read_*`/`process_write_*` register functions, ptrace ABI structures, LWP references/locks, compat-netbsd32 type selection, and `uio` transfer mechanics.

Reliability notes: `ptrace_update_lwp` drops and reacquires LWP references under the process lock and rejects system LWPs. A 32-bit tracer is blocked from tracing a 64-bit target register image. Register writes require `LSSTOP`; otherwise `EBUSY`. `proc_regio` bounds offsets and scratch-buffer size to avoid overruns.

Filesystem relevance: low. Debugger register/status support does not implement filesystem behavior.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/sys/kern/sys_process_lwpstatus.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/sys/kern/sys_pset.c -->
# File Research: sources/os/bsd/netbsd-src/sys/kern/sys_pset.c

Read completely: 611 lines.

Implements processor sets: creation/destruction, CPU assignment, process/LWP binding, kauth policy defaults, and sysctl exposure.

Main interfaces:
- `psets_init` allocates the processor-set table and installs a kauth listener.
- `sys_pset_create` and `sys_pset_destroy` implement privileged processor-set lifecycle.
- `sys_pset_assign` assigns or queries a CPU's processor set.
- `sys__pset_bind` binds a process or LWP to a processor set.
- `sysctl_psets_max` and `sysctl_psets_list` manage/report processor-set limits and active IDs.
- Helpers include `psets_realloc`, `psid_validate`, `kern_pset_create`, and `kern_pset_destroy`.

State/control flow: global `psets` is an array of `pset_info_t *` protected by `cpu_lock`, with `psets_max` and `psets_count`. Destroying a set clears matching CPU scheduler state and all LWPs using that set. Assigning a CPU validates the target, prevents removing the last default CPU, handles offline CPUs, rejects conflicts with explicit affinity masks, updates scheduler state, and migrates affected LWPs.

Dependencies/integration: scheduler per-CPU state, global CPU/LWP lists, `cpu_lock`, `proc_lock`, LWP migration, kauth authorization, sysctl, and CPU affinity masks.

Reliability notes: scheduler code may read `l_psid` locklessly, so updates must tolerate transient states. Reallocating to a smaller table rejects ranges containing active sets. Binding copies out only one old pset ID even when multiple LWPs are affected. Assignment must avoid affinity-mask conflicts and bound/intr LWP migration issues.

Filesystem relevance: indirect. Processor sets affect scheduling of filesystem and I/O workloads but do not implement filesystem state.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/sys/kern/sys_pset.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/sys/kern/sys_ptrace.c -->
# File Research: sources/os/bsd/netbsd-src/sys/kern/sys_ptrace.c

Read completely: 220 lines.

Provides the native `ptrace(2)` syscall wrapper, native ABI copy methods, register method table, and module registration for ptrace.

Main interfaces:
- `sys_ptrace` forwards native ptrace requests to `do_ptrace`.
- `native_ptm` is the native `struct ptrace_methods` table containing copyin/copyout helpers and register callbacks.
- `ptrace_copyin_piod` and `ptrace_copyout_piod` validate/copy `ptrace_io_desc`.
- `ptrace_copyin_siginfo`, `ptrace_copyout_siginfo`, and `ptrace_copyout_lwpstatus` handle native ABI transfer.
- `ptrace_init`, `ptrace_fini`, and `ptrace_modcmd` establish/disestablish `SYS_ptrace` for `emul_netbsd`.

State/control flow: the native syscall extracts request, pid, address, and data arguments, then delegates all policy and operation logic to `sys_ptrace_common.c`. The module declares dependency on `ptrace_common`.

Dependencies/integration: `ptrace_common`, syscall package establishment, native process register helpers from `sys_process_lwpstatus.c`, and the NetBSD emulation switch.

Reliability notes: copy helpers enforce exact ABI sizes for siginfo and exact-or-zero size for `ptrace_io_desc`. If syscall establishment/disestablishment fails, module init/fini reports the error directly. Most safety policy lives in `do_ptrace`, not this wrapper.

Filesystem relevance: low. Native ptrace syscall plumbing is process-debugging infrastructure, not filesystem code.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/sys/kern/sys_ptrace.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/sys/kern/sys_ptrace_common.c -->
# File Research: sources/os/bsd/netbsd-src/sys/kern/sys_ptrace_common.c

Read completely: 1603 lines.

Implements common ptrace policy and operations shared by native/compat frontends: attach/detach, memory I/O, register access dispatch, event masks, signal info/pass masks, LWP enumeration/status, stop/resume, syscall tracing, coredump requests, and module-level kauth listener setup.

Main interfaces:
- `do_ptrace` is the central request dispatcher.
- Policy helpers include `ptrace_listener_cb`, `ptrace_find`, `ptrace_allowed`, and `ptrace_needs_hold`.
- Signal/event helpers include `ptrace_get_siginfo`, `ptrace_set_siginfo`, `ptrace_get_sigpass`, `ptrace_set_sigpass`, `ptrace_get_event_mask`, `ptrace_set_event_mask`, and `ptrace_get_process_state`.
- LWP helpers include `ptrace_lwpinfo`, `ptrace_lwpstatus`, and `ptrace_startstop`.
- I/O helpers include `ptrace_doio`, `ptrace_regs`, `ptrace_dumpcore`, and `process_auxv_offset`.
- Module hooks include `ptrace_common_init`, `ptrace_common_fini`, and `ptrace_common_modcmd`.

State/control flow: `do_ptrace` enters `proc_lock`, finds the target, validates ptrace permission and kauth policy, obtains a target LWP reference, optionally releases process locks for requests that do not require them, and dispatches by request. Attach reparents and stops the target. Detach clears traced flags, signal-pass state, syscall tracing, parentage, and single-step state. Continue/step/syscall requests validate signal numbers, optional LWP targeting, deadlock hazards, program counter updates, and single-step state before resuming or signaling.

Dependencies/integration: process hierarchy/reparenting, process locks/ref locks, LWP references, kauth process authorization, PaX/VM memory I/O through `process_domem`, register helpers via `ptrace_methods`, RAS protection, signal delivery, syscall tracing internals, coredump module hooks, compat hooks, and machine-dependent ptrace requests.

Reliability notes: lock handling is request-dependent; incorrect `pheld`/reference logic would risk races with exit/exec or lock leaks. Chroot containment is enforced for attach and memory/register access through `proc_isunder`. Deadlock checks prevent resuming only suspended/debug-suspended LWPs. `PT_READ_*`/`PT_WRITE_*` preserve legacy success semantics even for incomplete or zero transfers. `PT_SYSCALLEMU` requires syscall tracing state and a stopped target. `process_auxv_offset` reconstructs AUXV location from `ps_strings` and handles 32-bit targets.

Filesystem relevance: low direct relevance. It is debugger/process-control infrastructure, although it can read/write traced process memory and inspect processes performing filesystem calls.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/sys/kern/sys_ptrace_common.c -->