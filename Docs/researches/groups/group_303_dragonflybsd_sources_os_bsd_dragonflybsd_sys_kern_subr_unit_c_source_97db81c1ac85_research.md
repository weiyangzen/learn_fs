# Group Research: group_303_dragonflybsd_sources_os_bsd_dragonflybsd_sys_kern_subr_unit_c_source_97db81c1ac85

Scope: `Docs/research_subset_a.md`; all listed source files were read completely.

<!-- BEGIN FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/kern/subr_unit.c -->
# File Research: sources/os/bsd/dragonflybsd/sys/kern/subr_unit.c

## Summary
Implements DragonFly BSD's compact unit-number allocator. It manages integer allocation ranges with a hybrid representation of leading allocated count, trailing free count, run-length list entries, and inline-sized bitmaps.

## Main Responsibilities
- Creates and destroys allocation spaces with `new_unrhdr()` and `delete_unrhdr()`.
- Allocates the lowest available unit via `alloc_unr()` and prelocked `alloc_unrl()`.
- Frees allocated units via `free_unr()` and internal `free_unrl()`.
- Converts fragmented run sequences into bitmap entries through `optimize_unr()`.
- Collapses empty, adjacent, fully allocated, and fully free entries through `collapse_unr()`.
- Provides diagnostic consistency checking and a userland stochastic test driver under `#ifndef _KERNEL`.

## Important Behavior
The allocator always returns the lowest free unit. The ideal case with only a prefix of allocated units and suffix of free units uses no list nodes. List entries represent free runs (`ptr == NULL`), allocated runs (`ptr == uh`), or bitmap chunks (`ptr` points to `struct unrb`). Bitmap storage is deliberately the same size as `struct unr`, allowing conversion without net extra memory in some cases.

`alloc_unrl()` requires the caller to hold the allocator lock and does not sleep. `free_unr()` may allocate two cached list nodes before taking the lock because freeing a unit can split an allocated run into several pieces.

## Dependencies and Integration
Kernel builds use `kmalloc`/`kfree`, `M_UNIT`, and a default global `unit_lock` unless the caller supplies a lock. Consumers are expected to use this for driver/device minor numbers, clone indexes, and other small kernel identifier spaces.

## Risks
The data structure has subtle invariants around `first`, `last`, `busy`, `alloc`, bitmap `busy`, and list length. Freeing an unallocated number or deleting a non-empty allocator triggers assertions. Correct prelocking is required for `alloc_unrl()`, while `free_unr()` must remain sleepable because it may need memory.
<!-- END FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/kern/subr_unit.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/kern/sys_generic.c -->
# File Research: sources/os/bsd/dragonflybsd/sys/kern/sys_generic.c

## Summary
Implements generic descriptor-based I/O syscalls and compatibility plumbing: `read`, `write`, vectored and positioned variants, `ioctl`, mapped ioctl translation, `select`, `pselect`, `poll`, `ppoll`, OpenBSD poll compatibility, and a helper to wait on sockets through a temporary kqueue.

## Main Responsibilities
- Builds `uio`/`iovec` structures for scalar, vectored, positioned read and write syscalls.
- Holds and drops file references with access checks, then dispatches through `fo_read()` and `fo_write()`.
- Implements `mapped_ioctl()` including command translation maps, stack-vs-heap ioctl buffers, `FIONBIO`, `FIOASYNC`, and copyin/copyout handling.
- Provides registration and unregistration for mapped ioctl handler ranges.
- Implements `select` and `pselect` by translating fd sets into transient kqueue events and copying results back into fd sets.
- Implements `poll` and `ppoll` by translating `pollfd` entries into kqueue events with per-call serial/index tagging.
- Provides `socket_wait()` by temporarily wrapping a referenced socket in a file object and private kqueue.

## Important Behavior
`kern_preadv()` and `kern_pwritev()` reject explicit offsets for non-vnode file types with `ESPIPE`. The common read/write helpers return successful byte counts for partial transfers interrupted by restart, interrupt, or would-block errors. Non-socket `EPIPE` writes signal `SIGPIPE`; sockets handle their own signal semantics.

`mapped_ioctl()` honors optional emulation maps before interpreting IOC direction and length bits. It uses an inline 128-byte stack buffer for small ioctl payloads and heap allocation for larger payloads. `FIONCLEX` and `FIOCLEX` are handled at the descriptor layer before file operation dispatch.

`select`/`poll` are old-API frontends over kqueue. The implementation tags generated events with `lwp_kqueue_serial` so stale events can be filtered or deleted. Unsupported read/write filter errors are often swallowed to match old `select`/`poll` behavior, while bad descriptors propagate as `EBADF` or `POLLNVAL`.

## Dependencies and Integration
This file is tightly coupled to the file descriptor layer (`holdfp`, `dropfp`, descriptor flags), file operation vectors, kqueue, signal masking, ktrace, and socket file operations. It is the generic syscall bridge used by vnode, pipe, socket, device, and message-queue file types.

## Filesystem/Storage Relevance
All regular file and vnode read/write syscalls flow through this layer before reaching filesystem-specific `fo_read`/`fo_write` implementations. Ioctl handling also carries block device, filesystem, terminal, and network control operations.

## Risks
The select/poll emulation depends on careful stale-event cleanup to avoid livelock. `mapped_ioctl()` must keep command length/direction, translation maps, and user copies synchronized or it can expose ABI incompatibilities. The simple `sys_read()` and `sys_write()` negative-size checks assign `EINVAL` but do not return immediately before rebuilding the `uio`, so correctness depends on later paths and unsigned syscall argument conventions.
<!-- END FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/kern/sys_generic.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/kern/sys_mqueue.c -->
# File Research: sources/os/bsd/dragonflybsd/sys/kern/sys_mqueue.c

## Summary
Implements POSIX message queues as descriptor-backed kernel objects. Queues live in a global named list, are opened through normal file descriptors, support priority-ordered messages, timed send/receive, notification, attributes, unlink semantics, and kqueue readiness.

## Main Responsibilities
- Initializes the global queue-list lock in `mqueue_sysinit()`.
- Maintains system tunables/sysctls for maximum descriptors, priorities, message size, default message count, and maximum message count.
- Implements queue creation/opening in `sys_mq_open()` with permission checks and descriptor allocation.
- Implements descriptor close through `mq_close_fop()` and unlink through `sys_mq_unlink()`.
- Implements receive paths `sys_mq_receive()` and `sys_mq_timedreceive()` via `mq_receive1()`.
- Implements send paths `sys_mq_send()` and `sys_mq_timedsend()` via `mq_send1()`.
- Implements `mq_notify`, `mq_getattr`, `mq_setattr`, stat, and kqueue filters.

## Important Behavior
The global list and per-process `p_mqueue_cnt` are protected by `mqlist_mtx`; individual queue state is protected by `mq_mtx`, with lock order `mqlist_mtx -> mq_mtx`.

Priorities below `MQ_PQSIZE` are mapped into fixed priority buckets tracked by a bitmap. Higher priorities go into a reserved sorted queue (`MQ_PQRESQ`) so runtime increases to `mq_prio_max` can still work. Receivers pull from the reserved queue first, then from the highest-priority bitmap bucket.

Blocking receive sleeps on `mq_send_cv`; blocking send sleeps on `mq_recv_cv`. Timed operations convert absolute timespecs to ticks with `abstimeout2timo()`. Unlink marks `MQ_UNLINK`, wakes waiters, notifies kqueue listeners, and destroys the queue immediately only when the reference count is zero; otherwise the last close destroys it.

## Dependencies and Integration
The implementation uses DragonFly file descriptors (`falloc`, `fsetfd`, `fdrop`, `sys_close`), `struct fileops`, kqueue filters, `vaccess`, process credentials, signals, and sysctl. Message queues are typed as `DTYPE_MQUEUE` and are not vnode-backed despite exposing `fo_stat`.

## Risks
The source comments explicitly note POSIX violations where queue state is changed before user copyout in receive and setattr paths. Notification is mostly signal-based; richer `sigevent` payload setup is commented out. Queue nonblocking state is stored in shared queue attributes, so it affects all descriptors for the queue rather than only one open file description.
<!-- END FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/kern/sys_mqueue.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/kern/sys_pipe.c -->
# File Research: sources/os/bsd/dragonflybsd/sys/kern/sys_pipe.c

## Summary
Implements DragonFly BSD's high-performance full-duplex pipe file type. It replaces socket-backed pipes with two VM-backed circular buffers, one for each direction, and supports `pipe`, `pipe2`, read/write, ioctl, stat, close, shutdown, kqueue filters, SIGIO, and per-CPU structure caching.

## Main Responsibilities
- Creates pipe descriptor pairs in `kern_pipe()`, honoring `O_CLOEXEC`, `O_CLOFORK`, and `O_NONBLOCK` for `pipe2`.
- Allocates and resizes pageable VM-backed pipe buffers in `pipespace()`.
- Caches pipe structures per CPU to reduce allocation churn.
- Serializes simultaneous reads and writes with per-buffer LWKT tokens and `pipe_start_uio()` / `pipe_end_uio()`.
- Implements circular-buffer read/write paths with nonblocking behavior, atomic writes up to `PIPE_BUF`, busy-delay optimization, and wait/wakeup handling.
- Provides socket-compatible ioctls for async I/O, byte count, and owner process/group.
- Implements close and shutdown state transitions for half-closed and fully closed pipes.
- Implements kqueue read/write filters with EOF, HUP, and capacity/data reporting.

## Important Behavior
Each `struct pipe` contains `bufferA` and `bufferB`. A file pointer stores the pipe address with the low bit selecting which side it represents. Reads consume from the selected side's buffer; writes append to the peer-visible buffer.

The read and write paths use monotonic `rindex`/`windex` counters masked by buffer size for offsets. Memory fences protect ordering between data copies and index publication. Writers cap a single transfer to half the buffer to improve reader wakeup behavior, and writes whose original size is at most `PIPE_BUF` do not proceed unless enough space exists for the whole write.

On SMP systems with timestamp counter support, both readers and writers can busy-wait for a few microseconds before sleeping, reducing wakeup/IPI overhead for synchronous pipe traffic. Large transfers periodically yield and check for pending signals.

## Dependencies and Integration
This file integrates with file descriptors, `struct fileops`, kqueue, signal ownership, VM objects, kernel maps, per-CPU globaldata, sysctls, and scheduler sleep/wakeup primitives. It returns `S_IFIFO` stat data with anonymous inode numbers derived per CPU.

## Filesystem/Storage Relevance
Pipes are a core file type used by the VFS/file-descriptor layer even though they are not filesystem-backed. Their read/write and readiness behavior must match regular descriptor semantics expected by shells, daemons, and event loops.

## Risks
The implementation has many concurrency-sensitive state bits (`PIPE_WANTR`, `PIPE_WANTW`, `PIPE_REOF`, `PIPE_WEOF`, `PIPE_CLOSED`, `PIPE_ASYNC`) and relies on token ordering plus atomic operations. Buffer VM allocation and per-CPU cache teardown can contend with `kernel_map` under mass process exit. Kqueue filter paths intentionally avoid locking and rely on knote processing plus later wakeups to tolerate races.
<!-- END FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/kern/sys_pipe.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/kern/sys_process.c -->
# File Research: sources/os/bsd/dragonflybsd/sys/kern/sys_process.c

## Summary
Implements `ptrace` syscall handling and procfs stop-event support. It performs tracing permission checks, attach/detach, continuation, single-step, process memory I/O, register access, and debugger-induced process stops.

## Main Responsibilities
- Copies ptrace request payloads between userland and kernel temporary storage in `sys_ptrace()`.
- Resolves and validates target processes in `kern_ptrace()`.
- Enforces tracing permissions, jail visibility, setuid restrictions, securelevel restrictions for init, and parent/tracer relationships.
- Implements `PT_TRACE_ME`, `PT_ATTACH`, `PT_DETACH`, `PT_CONTINUE`, `PT_STEP`, `PT_KILL`, memory read/write, `PT_IO`, and register/fpreg/dbreg get/set variants.
- Uses procfs helpers for target memory and register access.
- Provides `stopevent()` for procfs event stops and `trace_req()` as a permissive trace hook.

## Important Behavior
Target processes are held with `PHOLD()` and protected with `p_token`. Tracing is rejected while the target has `P_INEXEC`. Attach reparents the traced process to the tracer and sends `SIGSTOP`; detach attempts to restore the old parent from `p_oppid`, clears tracing flags, and optionally continues with a signal.

Memory access is expressed as `uio` operations against `procfs_domem()`. Register access is similarly routed through procfs architecture helpers. Short or failed integer read/write memory requests are converted to `EINVAL` in some cases.

## Dependencies and Integration
The file depends on process lifetime, LWPs, signals, procfs memory/register routines, architecture ptrace helpers, credentials/caps, and jail checks. It is not filesystem code, but it depends directly on procfs interfaces.

## Risks
Only the first LWP in the process is selected for ptrace operations, marked by the `XXX lwp` comment. Parent restoration during detach can fail if the old parent no longer exists. The procfs memory path returns are normalized in ways that may obscure original `EPERM`/EOF causes.
<!-- END FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/kern/sys_process.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/kern/sys_socket.c -->
# File Research: sources/os/bsd/dragonflybsd/sys/kern/sys_socket.c

## Summary
Provides the `fileops` implementation for sockets. It adapts generic descriptor operations to socket protocol operations for read, write, ioctl, stat, close, shutdown, and kqueue.

## Main Responsibilities
- Defines global `socketops`.
- Implements `soo_read()` using `so_pru_soreceive()`.
- Implements `soo_write()` using `so_pru_sosend()` and `SIGPIPE` handling.
- Implements socket ioctls for nonblocking, async, readable byte count, owner process/group, at-mark checks, interface ioctls, routing ioctls, and protocol control.
- Implements `soo_stat()` with `S_IFSOCK`, read/write permission bits based on socket state, receive-buffer size, credential owner, inode, and protocol sense data.
- Implements `soo_close()` and `soo_shutdown()`.

## Important Behavior
Read and write choose blocking behavior from explicit file-operation flags first, then from `fp->f_flag & FNONBLOCK`. `soo_write()` sends `SIGPIPE` on `EPIPE` unless `MSG_NOSIGNAL`, `SO_NOSIGPIPE`, or lack of LWP suppresses it.

`FIONBIO` is handled as a no-op at this layer because the generic ioctl path updates `fp->f_flag`. `FIOASYNC` updates both socket state and receive/send sockbuf async flags. Interface and routing ioctls are dispatched to `ifioctl()` and `rtioctl()` by ioctl group.

## Dependencies and Integration
This file is the bridge from the descriptor/file layer to socket protocol operations, routing, interface control, signal ownership, and kqueue socket filters.

## Risks
Close swaps `fp->f_ops` to `badfileops` before calling `soclose()` and then clears `f_data`, so any stale user of the file object must tolerate revoked operations. Ioctl routing by command group assumes protocol, interface, and route command namespaces remain compatible.
<!-- END FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/kern/sys_socket.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/kern/syscalls.c -->
# File Research: sources/os/bsd/dragonflybsd/sys/kern/syscalls.c

## Summary
Generated syscall-name table for DragonFly BSD. It maps syscall numbers 0 through 555 to string names used for tracing, diagnostics, and ABI introspection.

## Main Responsibilities
- Defines `const char *syscallnames[]`.
- Names active syscalls, obsolete syscalls, compatibility entries, reserved holes, `nosys` slots, and loadable syscall placeholders.
- Documents the generation path: edit `syscalls.master`, then run `make sysent`.

## Important Contents
The table covers core process, VFS, descriptor, socket, memory-management, SysV IPC, POSIX message queue, kqueue, module, jail, varsym, VM-space, LWP, `*at`, and newer filesystem-adjacent syscalls. Filesystem-relevant names include `open`, `close`, `link`, `unlink`, `chdir`, `mknod`, `chmod`, `mount`, `unmount`, `sync`, `revoke`, `symlink`, `readlink`, `execve`, `chroot`, `msync`, `rename`, `flock`, `mkfifo`, `mkdir`, `rmdir`, `utimes`, `quotactl`, `statfs`, `fstatfs`, `getfh`, `fhstatfs`, `fhopen`, ACL and extattr calls, `sendfile`, `statvfs`, `getvfsstat`, `openat`, `fstatat`, `unlinkat`, `renameat`, `mkdirat`, `mknodat`, `readlinkat`, `symlinkat`, `linkat`, `fexecve`, `posix_fallocate`, `fdatasync`, and `futimesat`.

## Dependencies and Integration
This file must stay synchronized with `syscalls.master`, generated syscall prototypes, syscall numbers, and the dispatch table in `init_sysent.c`.

## Risks
Manual edits will be overwritten. Any mismatch between this name table and the actual syscall dispatch ABI can mislead tracing, debugging, and compatibility tooling.
<!-- END FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/kern/syscalls.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/kern/sysv_ipc.c -->
# File Research: sources/os/bsd/dragonflybsd/sys/kern/sysv_ipc.c

## Summary
Implements the shared SysV IPC permission check helper `ipcperm()`.

## Main Responsibilities
- Compares caller credentials against IPC creator/owner UID and GID fields.
- Applies owner, group, or other permission bits by shifting the requested mode.
- Allows metadata-control requests (`IPC_M`) for privileged callers.
- Allows read/write style access when requested bits are present or the caller has restricted-root capability.

## Important Behavior
If the effective UID does not match creator or owner, group membership is checked against both current and creator group IDs; otherwise permission falls through to "other" bits. `IPC_M` bypasses normal mode matching for privileged callers. Non-control operations succeed when all requested bits are present in `perm->mode` or `caps_priv_check(..., SYSCAP_RESTRICTEDROOT)` succeeds.

## Dependencies and Integration
`ipcperm()` is shared by SysV message queues, semaphores, and shared memory. It depends on process credentials, group membership, and DragonFly capability checks.

## Risks
Permission semantics are central to all SysV IPC objects. Any change affects message queues, semaphores, and shared memory together, including jail/capability behavior enforced by callers.
<!-- END FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/kern/sysv_ipc.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/kern/sysv_msg.c -->
# File Research: sources/os/bsd/dragonflybsd/sys/kern/sysv_msg.c

## Summary
Implements SVID/System V message queues. It maintains fixed-size pools of queue descriptors, message headers, message-map segments, and message data storage, and exposes `msgctl`, `msgget`, `msgsnd`, and `msgrcv`.

## Main Responsibilities
- Initializes global SysV message pools and validates segment sizing in `msginit()`.
- Tracks free message-map segments and free message headers.
- Frees message headers and their segment chains with `msg_freehdr()`.
- Implements `sys_msgctl()` for `IPC_RMID`, `IPC_SET`, and `IPC_STAT`.
- Implements `sys_msgget()` for keyed lookup and queue creation.
- Implements `sys_msgsnd()` for permission checks, resource waiting, segment allocation, user copyin, queue append, and wakeups.
- Implements `sys_msgrcv()` for type matching, optional blocking, truncation rules, user copyout, resource release, and wakeups.
- Exposes tunables/sysctls for message limits and a `msqids` sysctl dump.

## Important Behavior
All queue state is protected by a single `msg_token`. Message bodies are split into fixed-size `msgssz` segments linked through `msgmaps`; `msg_spot` points to the first segment. Queue IDs combine a table index with a sequence number to detect stale IDs.

`sys_msgsnd()` may sleep for queue bytes, free segments, free headers, or another sender/receiver's `MSG_LOCKED` copy window. Before copying from user memory, it marks the queue locked so the descriptor cannot be reused while the token may be temporarily lost during copy faults. `sys_msgrcv()` removes the selected message from the queue before copying it out and frees it even if copyout fails.

Message receive type rules support first-message (`msgtyp == 0`), exact positive type, and first type less than or equal to `-msgtyp`. `MSG_NOERROR` allows truncation to the caller's buffer size.

## Dependencies and Integration
This file uses `ipcperm()` from `sysv_ipc.c`, jail capability checks, process credentials, SysV IPC ID macros, sysctl/tunables, and sleep/wakeup primitives.

## Risks
The fixed global pools make resource exhaustion and wakeup ordering important. The single-token design serializes state but copyin/copyout paths can temporarily block, requiring `MSG_LOCKED` to avoid descriptor reuse races. As with historical SysV implementations, failed receive copyout can still consume a message because bookkeeping is done before user copies.
<!-- END FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/kern/sysv_msg.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/kern/sysv_sem.c -->
# File Research: sources/os/bsd/dragonflybsd/sys/kern/sysv_sem.c

## Summary
Implements SVID/System V semaphores, including semaphore-set creation, control operations, atomic multi-operation `semop`, process-exit undo records, and SysV IPC tunables.

## Main Responsibilities
- Initializes the semaphore ID pool and per-set locks in `seminit()`.
- Maintains global semaphore totals under `sema_lk`.
- Allocates and manages per-process `sem_undo` records for `SEM_UNDO`.
- Clears undo entries when semaphore sets or members are reset or removed.
- Implements `sys___semctl()` for `IPC_RMID`, `IPC_SET`, `IPC_STAT`, `SEM_STAT`, `GET*`, `SETVAL`, and `SETALL`.
- Implements `sys_semget()` for keyed lookup and semaphore-set creation.
- Implements `sys_semop()` with atomic vector execution, rollback, wait counts, sleeps, wakeups, and undo adjustment.
- Implements `semexit()` to apply process-exit undo adjustments and clean up undo structures.

## Important Behavior
Each semaphore set has a lock; individual semaphore operations also use pool tokens based on the semaphore address. `sys_semop()` first tries to apply the whole operation vector. If one operation cannot proceed, it increments the appropriate wait counter (`semncnt` or `semzcnt`), rolls back all earlier changes, optionally sleeps, then retries from the beginning. This preserves atomic visibility of the vector.

`SEM_UNDO` adjustments are applied after a successful operation vector. If undo allocation fails partway through, the code rolls back earlier undo adjustments and then rolls back semaphore value changes. `semexit()` later applies stored adjustments while revalidating set and entry state under locks.

Semaphore IDs use index-plus-sequence encoding. Set removal clears `SEM_ALLOC`, frees the semaphore array, decrements `semtot`, and removes matching undo entries.

## Dependencies and Integration
This file depends on `ipcperm()`, process credentials and tokens, jail SysV IPC capability checks, per-process `p_sem_undo`, lockmgr locks, pool tokens, sysctl/tunables, and sleep/wakeup.

## Risks
Correctness depends on rollback paths for both semaphore values and undo records. The wait path must handle destroy/recreate races, so it tracks a per-set generation counter. `semexit()` includes race-aware rechecks but still asserts if it finds impossible stale allocation state outside expected races.
<!-- END FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/kern/sysv_sem.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/kern/sysv_shm.c -->
# File Research: sources/os/bsd/dragonflybsd/sys/kern/sysv_shm.c

## Summary
Implements SVID/System V shared memory. It manages shared-memory segment descriptors, VM objects, per-vmspace attachment maps, attach/detach/control/get syscalls, fork/exit inheritance, and shared-memory tunables.

## Main Responsibilities
- Initializes shared-memory limits and descriptor table in `shminit()`.
- Finds segments by key or shmid with sequence validation and optional removed-segment attachment support.
- Allocates segments in `shmget_allocate_segment()` using physical or swap pager VM objects.
- Handles keyed lookup and creation in `sys_shmget()`.
- Maps segments into process address spaces in `sys_shmat()`.
- Detaches mappings in `sys_shmdt()` and `shm_delete_mapping()`.
- Handles `IPC_STAT`, `IPC_SET`, and `IPC_RMID` in `sys_shmctl()`.
- Copies attachment state across fork in `shmfork()` and detaches all segments on vmspace exit in `shmexit()`.
- Deallocates segment VM objects when removed and no longer attached.

## Important Behavior
Global state is serialized by `shm_token`. Each process vmspace lazily receives a `vm_shm` array of `struct shmmap_state`, capped by `shminfo.shmseg`. Attach reserves an entry before VM operations because blocking may temporarily lose serialization.

`shmget_allocate_segment()` marks a descriptor as allocated-but-removed while allocating memory so competing keyed creators wait instead of creating a duplicate. After pager object creation it installs owner/mode metadata, accounts committed pages, and wakes waiters if needed. `shm_use_phys` selects physical pager allocation by default; values above 1 trigger eager page preallocation up to available free pages.

`sys_shmat()` supports fixed addresses, `SHM_RND`, read-only protection, inherited shared mappings, and segment-size alignment to `SEG_SIZE` for large mappings when possible. `IPC_RMID` marks a segment removed and deallocates it only after the attachment count reaches zero. `shm_allow_removed` permits attaching to removed-but-still-referenced segments by shmid.

## Dependencies and Integration
This file depends on `ipcperm()`, jail SysV IPC capability checks, VM maps, VM objects, physical/swap pagers, pmap/page APIs, process vmspaces, sysctl/tunables, and SysV IPC ID macros.

## Risks
Attachment bookkeeping and VM map removal must stay synchronized with `shm_nattch`; failed or racing detach paths can leak mappings or deallocate too early. `shmfork()` assumes the parent vmspace has a valid `vm_shm` array when invoked. Eager physical-page preallocation can stall the kernel for large segments, which the comments acknowledge.
<!-- END FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/kern/sysv_shm.c -->