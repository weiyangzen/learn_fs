# Group Research: group_1405_openbsd_src_sources_os_bsd_openbsd_src_sys_kern_sys_pipe_c_sources__df36774d51e5

Scope checked against `Docs/research_subset_a.md`: all files are under `sources/os/bsd/openbsd-src`, which is included in subset A. Each listed source file was read completely.

<!-- BEGIN FILE RESEARCH: sources/os/bsd/openbsd-src/sys/kern/sys_pipe.c -->
# File Research: sources/os/bsd/openbsd-src/sys/kern/sys_pipe.c

Implements OpenBSD anonymous pipes as a dedicated `DTYPE_PIPE` file type rather than socket-backed pipes. It provides pipe creation syscalls, file operations, kqueue filters, async notification, blocking/nonblocking read-write semantics, and pipe-pair lifetime management.

Major structures and globals:
- `struct pipe_pair`: two peer `struct pipe` objects plus one shared `rwlock`.
- `pipeops`: `read`, `write`, `ioctl`, `kqfilter`, `stat`, and `close` handlers for pipe files.
- `pipe_pair_pool`: pool allocator for pipe pairs.
- `nbigpipe`, `amountpipekva`: accounting for expanded pipe buffers and pageable kernel virtual memory.

Creation path:
- `sys_pipe()` and `sys_pipe2()` both call `dopipe()`.
- `sys_pipe2()` accepts only `O_CLOEXEC`, `O_CLOFORK`, and `FNONBLOCK`.
- `dopipe()` allocates a pipe pair, two file structures, two file descriptors, installs descriptor close flags, copies the descriptor pair to userland, and unwinds descriptors and pipe buffers on partial failure.

Buffer and lifetime behavior:
- Each pipe side owns a pageable circular buffer initialized to `PIPE_SIZE`.
- Large writes may grow an empty normal pipe to `BIG_PIPE_SIZE`, limited by `LIMITBIGPIPES`.
- `pipe_destroy()` marks EOF, wakes peer waiters, waits for active I/O via `pipe_busy`, disconnects the peer, frees buffers, and destroys the pair when both sides are gone.
- `pipe_rundown()` coordinates close-time waiters with in-flight read/write paths.

I/O behavior:
- `pipe_read()` drains the read pipe buffer with wraparound handling, resets indices when empty, sleeps on empty pipes, returns EOF on closed peers, and wakes blocked writers once enough space is available.
- `pipe_write()` writes into the peer pipe, preserves atomicity for writes up to `PIPE_BUF`, supports wraparound copies, blocks or returns `EAGAIN` when full, and returns `EPIPE` when the read side is gone.
- Both paths drop the pipe lock around `uiomove()` and use an internal `PIPE_LOCK` I/O lock to serialize buffer mutations.

Notifications and metadata:
- `pipe_ioctl()` supports async mode, `FIONREAD`, and signal-owner ioctls.
- `pipe_stat()` reports FIFO mode, buffer size, buffered byte count, block count, timestamps, and file credential uid/gid.
- kqueue filters implement read readiness, write readiness, poll hangup behavior, and except-filter behavior for poll-style users.

Filesystem/storage relevance:
- Not a filesystem implementation, but directly relevant to VFS/file-descriptor semantics: it defines OpenBSD pipe file operations, `stat(2)` behavior for pipes, descriptor allocation, readiness notification, and close races for a non-vnode kernel file type.
<!-- END FILE RESEARCH: sources/os/bsd/openbsd-src/sys/kern/sys_pipe.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/openbsd-src/sys/kern/sys_process.c -->
# File Research: sources/os/bsd/openbsd-src/sys/kern/sys_process.c

Implements `ptrace(2)` and process memory access helpers when `PTRACE` is enabled, plus common process I/O permission checks used outside the conditional block.

Main entry points:
- `sys_ptrace()`: dispatches ptrace requests, centralizes user/kernel copyin/copyout handling, and allocates temporary register/xstate buffers where needed.
- `ptrace_ctrl()`: handles trace control operations such as trace-me, attach, detach, continue, kill, and optional single-step.
- `ptrace_kstate()`: handles kernel state queries and updates such as thread iteration, event masks, and process-state snapshots.
- `ptrace_ustate()`: handles target memory access, register access, auxiliary vector reads, stack cookie/PAC mask queries, and optional machine xstate operations.
- `process_domem()`: maps ptrace memory I/O to `uvm_io()` against the target process VM map.

Request handling:
- `sys_ptrace()` classifies each request as no-copy, fixed stack copy, allocated input, allocated output, or input-output.
- Kernel-state requests use fixed local structs for thread state, events, and process state.
- Register and extended register requests allocate buffers sized to the machine structures.
- `PT_IO` updates the requested length by subtracting remaining `uio_resid`.

Permission and state checks:
- `process_checktracestate()` requires the target to be traced by the caller, not in exec, and, for thread-specific operations, stopped and waited.
- `PT_ATTACH` rejects self-attach, system processes, already traced processes, exec-in-progress targets, unauthorized uid/sugid targets, disallowed non-child tracing unless privileged or `global_ptrace`, protected init, and ancestor cycles.
- `process_checkioperm()` separately protects target memory access from unauthorized users, setuid/setgid exec targets, init at securelevel, and exec-in-progress processes.

Process/thread lookup:
- `process_tprfind()` accepts either a process id or thread id offset by `THREAD_PID_OFFSET`, returning the process and a selected target thread.
- Process-state APIs expose traced thread ids as offset thread ids.

Filesystem/storage relevance:
- No filesystem implementation. Relevant because debuggers and proc-like tooling depend on safe cross-process VM access, `uio` setup, and kernel permission rules that interact with file-backed mappings and executable image state.
<!-- END FILE RESEARCH: sources/os/bsd/openbsd-src/sys/kern/sys_process.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/openbsd-src/sys/kern/sys_socket.c -->
# File Research: sources/os/bsd/openbsd-src/sys/kern/sys_socket.c

Defines file operations for sockets represented as kernel files.

Core behavior:
- `socketops` maps file operations to `soo_read`, `soo_write`, `soo_ioctl`, `soo_kqfilter`, `soo_stat`, and `soo_close`.
- `soo_read()` calls `soreceive()` and translates `FNONBLOCK` to `MSG_DONTWAIT`.
- `soo_write()` calls `sosend()` and likewise honors nonblocking mode.
- `soo_close()` calls `soclose()` with `MSG_DONTWAIT` when the file is nonblocking, then clears `f_data`.

Ioctls:
- `FIOASYNC` toggles async flags on both receive and send socket buffers while holding their mutexes.
- `FIONREAD` returns receive-buffer data byte count.
- owner and process-group ioctls use `sigio_setown()` and `sigio_getown()`.
- `SIOCATMARK` reports receive-at-mark state.
- interface ioctls are delegated to `ifioctl()`, routing ioctls return `EOPNOTSUPP`, and other protocol controls go to `pru_control()`.

Stat behavior:
- `soo_stat()` reports `S_IFSOCK`.
- Read permission bits are set if receive is still possible or data remains buffered.
- Write permission bits are set if send has not been shut down.
- uid/gid come from socket effective credentials, and protocol-specific status comes from `pru_sense()`.

Filesystem/storage relevance:
- Not filesystem code, but important for VFS file abstraction: sockets are non-vnode files with read/write/ioctl/stat/close behavior exposed through the same descriptor table as regular files.
<!-- END FILE RESEARCH: sources/os/bsd/openbsd-src/sys/kern/sys_socket.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/openbsd-src/sys/kern/syscalls.c -->
# File Research: sources/os/bsd/openbsd-src/sys/kern/syscalls.c

Generated system-call name table for OpenBSD.

Contents:
- Defines `const char *const syscallnames[]`.
- Maps syscall numbers 0 through 330 to printable names or placeholder strings for obsolete/unimplemented entries.
- Includes conditional names based on kernel options such as `PTRACE`, `KTRACE`, `ACCOUNTING`, `NFSCLIENT`, `NFSSERVER`, `SYSVSEM`, `SYSVMSG`, and `SYSVSHM`.

Role:
- Provides stable syscall-number-to-name metadata for tracing, diagnostics, ktrace-like output, and kernel/user debugging.
- The header warns that it is generated from `syscalls.master`, not edited manually.

Filesystem/storage relevance:
- Contains no implementation logic. It identifies filesystem-related syscall names such as `open`, `close`, `link`, `unlink`, `mount`, `unmount`, `stat`, `fstat`, `getfsstat`, `statfs`, `fstatfs`, `fsync`, `getdents`, `rename`, `mkdir`, `rmdir`, `quotactl`, pathconf variants, `fhopen`, `fhstat`, and many `*at` calls.
<!-- END FILE RESEARCH: sources/os/bsd/openbsd-src/sys/kern/syscalls.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/openbsd-src/sys/kern/sysv_ipc.c -->
# File Research: sources/os/bsd/openbsd-src/sys/kern/sysv_ipc.c

Shared permission helper for System V IPC objects.

Main function:
- `ipcperm(struct ucred *cred, struct ipc_perm *perm, int mode)`.

Behavior:
- For `IPC_M`, permits root, the owner uid, or creator uid; otherwise returns `EPERM`.
- For read/write-style checks, calls `vaccess()` twice: once against current owner uid/gid and once against creator uid/gid.
- Returns success if either access check passes; otherwise returns `EACCES`.

Design note:
- Reuses vnode access semantics (`vaccess(VNON, ...)`) for IPC permission-bit checks even though the target is not a vnode.

Filesystem/storage relevance:
- Not filesystem logic, but it reuses VFS permission-check machinery and is a common authorization dependency for the message queue, semaphore, and shared-memory implementations in this group.
<!-- END FILE RESEARCH: sources/os/bsd/openbsd-src/sys/kern/sysv_ipc.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/openbsd-src/sys/kern/sysv_msg.c -->
# File Research: sources/os/bsd/openbsd-src/sys/kern/sysv_msg.c

Implements System V message queues.

Global state:
- `msg_queues`: global TAILQ of active queues.
- `sysvmsgpl`: pool for `struct msg`.
- `msginfo`: tunables/limits such as max message size, queue count, queue bytes, and total messages.
- `num_ques`, `num_msgs`, `sequence`, `maxmsgs`: queue/message accounting and sequence generation.

Syscall behavior:
- `msginit()` initializes tunables, the message pool, and global queue state.
- `sys_msgget()` looks up or creates a queue by key, enforces `IPC_CREAT`/`IPC_EXCL`, permission checks, and max queue count.
- `sys_msgsnd()` checks queue existence, message size limits, write permission, queue byte space, and total message limit; it sleeps unless `IPC_NOWAIT`, copies message data from userland into mbufs, enqueues, and wakes readers.
- `sys_msgrcv()` checks read permission, finds a matching message by type rule, sleeps unless `IPC_NOWAIT`, copies out without losing the message on copyout error, dequeues on success, wakes writers, and returns copied size.
- `sys_msgctl()` implements `IPC_RMID`, `IPC_SET`, and `IPC_STAT`.

Queue and message lifecycle:
- Queue ids combine a queue index with an IPC sequence value.
- `que_create()` keeps queues ordered by index and handles key races caused by sleeping allocation.
- `QREF`/`QRELE` reference management is used while removing queues so waiters and active callers see `MSGQ_DYING` and unwind cleanly.
- `msg_create()` uses the pool and detects queues removed during allocation.
- `msg_free()` frees mbuf chains and decrements global message count.

Message storage:
- The user buffer layout is a leading `long` message type followed by opaque bytes.
- Message payloads are stored in mbuf chains, using clusters for larger messages.
- `msg_lookup()` implements System V type matching: exact positive type, any type for zero, and bounded match for negative types.

Sysctl export:
- `sysctl_sysvmsg()` exports `msginfo` and an array of `msqid_ds` entries for compatibility with `ipcs(1)`, preserving old array-index behavior.

Filesystem/storage relevance:
- Not filesystem code. Relevant as kernel object lifetime, permission, wait/wakeup, and copyin/copyout infrastructure that parallels many VFS object-management patterns.
<!-- END FILE RESEARCH: sources/os/bsd/openbsd-src/sys/kern/sysv_msg.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/openbsd-src/sys/kern/sysv_sem.c -->
# File Research: sources/os/bsd/openbsd-src/sys/kern/sysv_sem.c

Implements System V semaphore sets, semaphore operations, undo records, process-exit cleanup, and sysctl tunables.

Global state:
- `sema`: array mapping semaphore indexes to `struct semid_ds_kern`.
- `semseqs`: per-index sequence numbers for id generation.
- `semu_list`: global list of per-process undo vectors.
- `sema_pool`, `semu_pool`: pools for semaphore sets and undo structures.
- `semtot`, `semutot`: allocated semaphore and undo accounting.

Initialization and allocation:
- `seminit()` initializes pools, allocates `sema` and `semseqs`, and initializes the undo list.
- `sys_semget()` preallocates new sets when creation may be needed, handles key lookup and races, enforces `semmni`, `semmns`, and `semmsl`, initializes permissions, sequence, timestamps, and semaphore arrays.

Control operations:
- `sys___semctl()` handles `IPC_RMID`, `IPC_SET`, `IPC_STAT`, `GETNCNT`, `GETPID`, `GETVAL`, `GETALL`, `GETZCNT`, `SETVAL`, and `SETALL`.
- Removal clears the `sema` slot, drops references, clears undo records for that set, and wakes waiters.
- `SETVAL`/`SETALL` clear affected undo entries and wake waiters.
- `GETALL` and `SETALL` use references around sleeping allocations/copyin and retry if the set is replaced.

Semaphore operation semantics:
- `sys_semop()` copies small operation vectors onto the stack and larger vectors from heap allocation.
- It applies a vector atomically: if any operation cannot proceed, prior changes are rolled back before sleeping or returning.
- Negative operations wait for sufficient value, zero operations wait for zero, and positive operations increment values.
- `IPC_NOWAIT` returns `EAGAIN` instead of sleeping.
- Waiters increment `semncnt` or `semzcnt`, sleep on the semaphore slot, then revalidate that the set still exists.
- Successful operations update `sempid`, `sem_otime`, and wake other waiters when needed.

Undo handling:
- `semu_alloc()` allocates one undo vector per process, with a second lookup after sleeping allocation to avoid duplicates.
- `semundo_adjust()` creates, updates, or removes per-process undo entries and enforces `SEMUME`.
- `semundo_clear()` removes undo entries for an entire set or individual semaphore.
- `semexit()` applies pending undo adjustments when a process exits, clamps underflow to zero, wakes waiters, and frees the undo vector.

Sysctl behavior:
- `sysctl_sysvsem()` exposes bounded tunables and can grow `semmni` dynamically via `sema_reallocate()`.
- Some limits are read-only or only growable to avoid invalidating active state.

Filesystem/storage relevance:
- Not filesystem logic. Relevant as a kernel resource manager with id/sequence validation, permission checks, sleep-safe allocation, reference counting, and process-exit cleanup patterns.
<!-- END FILE RESEARCH: sources/os/bsd/openbsd-src/sys/kern/sysv_sem.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/openbsd-src/sys/kern/sysv_shm.c -->
# File Research: sources/os/bsd/openbsd-src/sys/kern/sysv_shm.c

Implements System V shared memory segments backed by UVM anonymous objects.

Global state and structures:
- `shmsegs`: array mapping shmid indexes to `struct shmid_ds`.
- `shmseqs`: per-index sequence numbers.
- `shm_pool`: pool for `struct shmid_ds` plus an internal `struct shm_handle`.
- `shm_last_free`, `shm_nused`, `shm_committed`: allocation cursor and accounting.
- Per-vmspace `struct shmmap_head` tracks attached shared-memory mappings.
- `struct shm_handle` stores the backing `uvm_object`.

Lookup and allocation:
- `shm_find_segment_by_key()` and `shm_find_segment_by_shmid()` locate segments by key or id/sequence.
- `sys_shmget()` handles existing-key lookup, `IPC_CREAT`, `IPC_EXCL`, and new segment allocation.
- `shmget_allocate_segment()` enforces size, count, and total committed-page limits; allocates a pool object; creates a UAO object; initializes permissions, sequence, pid, timestamps, and size.
- Allocation retries when a keyed segment appears while sleeping.

Attach/detach:
- `sys_shmat()` lazily allocates per-vmspace mapping state, validates permissions, finds a free attachment slot, computes fixed or chosen attach address, references the backing UAO, maps it with `MAP_INHERIT_SHARE`, and records the attachment.
- `sys_shmdt()` finds an attachment by virtual address and delegates to `shm_delete_mapping()`.
- `shm_delete_mapping()` decrements attachment count, unmaps the range, records detach time, and deallocates removed segments once the final attach is gone.

Control and lifecycle:
- `sys_shmctl()` implements `IPC_STAT`, `IPC_SET`, and `IPC_RMID`; lock/unlock commands are unsupported.
- `IPC_RMID` marks a segment removed and either deallocates immediately or waits for the last detach.
- `shmfork()` copies attachment state and increments segment attach counts in child vmspaces.
- `shmexit()` detaches all mappings and frees the per-vmspace attachment table.
- `shminit()` initializes the pool and arrays and converts `shmmax` from pages to bytes.

Sysctl behavior:
- `sysctl_sysvshm()` exposes bounded shared-memory tunables.
- `shmmni` can grow dynamically via `shm_reallocate()`.
- `shmall` and other constraints are handled conservatively so existing allocations remain valid.

Filesystem/storage relevance:
- Not filesystem code, but storage-relevant through virtual memory object backing, shared mappings inherited across fork, and lifecycle patterns similar to file-backed mmap objects.
<!-- END FILE RESEARCH: sources/os/bsd/openbsd-src/sys/kern/sysv_shm.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/openbsd-src/sys/kern/tty.c -->
# File Research: sources/os/bsd/openbsd-src/sys/kern/tty.c

Core OpenBSD terminal subsystem implementation. It provides the default termios line discipline, character input processing, output processing, generic tty ioctls, read/write paths, kqueue filters, job-control behavior, flow control, tty allocation/freeing, and tty sysctl statistics.

Global state:
- `char_type[]`: classification/parity table used by input, output, erase, and column tracking logic.
- `ttylist`, `tty_count`, `ttylist_lock`: global list of allocated tty structures.
- `tk_cancc`, `tk_nin`, `tk_nout`, `tk_rawcc`: global tty statistics counters.
- Symbolic sleep strings such as `ttyin`, `ttyout`, `ttybg`, `ttopen`, and `ttclos`.

Open/close/lifecycle:
- `ttyopen()` initializes open state, device id, window size, and column state.
- `ttyclose()` detaches console redirection if needed, flushes queues, bumps `t_gen` so sleepers detect reuse/revoke, releases session references, and clears state.
- `ttymalloc()` allocates a tty and clists sized by baud rate, registers it in `ttylist`, and initializes restart timeout state.
- `ttyfree()` removes the tty from the global list, invalidates kqueue lists, frees queues, and frees the tty.

Input processing:
- `ttyinput()` handles receiver enable, pending reinput, stats, break/parity/framing errors, `PARMRK`, software/hardware flow control, stripping, literal-next, discard, signals, IXON start/stop, CR/LF translations, canonical editing, erase/kill/word erase/reprint/status, overflow behavior, canonical line completion, echo, and output restart.
- Canonical mode moves completed lines from raw queue to canonical queue.
- Noncanonical mode wakes readers directly and relies on `VMIN`/`VTIME` in `ttread()`.

Output processing:
- `ttyoutput()` handles `OPOST`, tab expansion, newline/carriage-return translation, uppercase/xcase mapping, `ONOEOT`, `ONOCR`, column accounting, and queue insertion.
- `ttwrite()` copies user data in chunks, fast-paths ordinary output runs, processes special output characters through `ttyoutput()`, mirrors console output to the console message buffer, sleeps on high-water output, and honors nonblocking mode.
- `ttstart()` invokes the device output routine when present.

Read behavior:
- `ttread()` enforces background read job control with `SIGTTIN`, processes pending input, implements canonical reads, noncanonical `VMIN`/`VTIME` timing, EOF handling, delayed suspend, user copyout via `ureadc()`, and unblocks input flow control after queue drain.

Generic ioctls:
- `ttioctl()` handles async mode, read counts, exclusive mode, flushing, virtual console redirection, drain, termios get/set, line discipline switching, start/stop, controlling terminal setup, foreground process group ownership, window size changes, timestamp control, and status output.
- Modifying ioctls enforce background job-control rules with `SIGTTOU`.
- `TIOCSETD` safely closes the old line discipline, opens the new one, and rolls back if open fails.

Flow control and wakeups:
- `ttyblock()` sends VSTOP and/or requests hardware input flow control when input queues exceed thresholds.
- `ttyunblock()` sends VSTART and/or clears hardware flow control when queues drain.
- `ttyflush()` drains read/write queues and wakes waiters/selectors.
- `ttwakeup()` and `ttwakeupwr()` notify readers, writers, selectors, and async recipients.

Kqueue and polling:
- `ttkqfilter()` attaches read, write, and poll-style except filters.
- Read filters report available input and carrier loss EOF/HUP.
- Write filters report output queue space and poll/select hangup.
- Except filters are restricted to poll-style hangup behavior.

Utility and stats:
- `ttyinfo()` prints load and foreground-process status for `^T`/`TIOCSTAT`.
- `ttysleep_nsec()` returns `ERESTART` if the tty generation changed while sleeping.
- `ttspeedtab()`, `ttsetwater()`, `ttychars()`, `tputchar()`, `ttycheckoutq()`, `ttywflush()`, and `ttywait()` support drivers and kernel tty writers.
- `sysctl_tty()` exposes counters and `KERN_TTY_INFO`; privileged callers see session pointers in exported tty stats.
- `ttytstamp()` records modem-signal transition timestamps when configured.

Filesystem/storage relevance:
- Not filesystem code. Important for character-device/VFS integration: tty device file operations rely on this line discipline for read/write/ioctl/poll semantics, controlling-terminal session state, revoke/restart behavior, and `/dev/console` access checks.
<!-- END FILE RESEARCH: sources/os/bsd/openbsd-src/sys/kern/tty.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/openbsd-src/sys/kern/tty_conf.c -->
# File Research: sources/os/bsd/openbsd-src/sys/kern/tty_conf.c

Defines the kernel line-discipline switch table.

Contents:
- `linesw[]`: array of `struct linesw` entries for termios, defunct legacy disciplines, optional PPP, optional NMEA, optional MSTS, and optional EndRun.
- `nlinesw`: number of registered line disciplines.
- `nullioctl()`: discipline ioctl stub returning `-1` so generic tty ioctl handling can continue.

Behavior:
- The default discipline uses `ttyopen`, `ttylclose`, `ttread`, `ttwrite`, `ttyinput`, `ttstart`, and `ttymodem`.
- Disabled or defunct disciplines are wired to `enodev`/error stubs.
- Optional disciplines are included only when their config counts are nonzero.

Filesystem/storage relevance:
- Not filesystem logic. It is the dispatch table behind tty character-device behavior and determines which line-discipline methods handle reads, writes, input, close, and ioctl fallback.
<!-- END FILE RESEARCH: sources/os/bsd/openbsd-src/sys/kern/tty_conf.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/openbsd-src/sys/kern/tty_endrun.c -->
# File Research: sources/os/bsd/openbsd-src/sys/kern/tty_endrun.c

TTY line discipline that decodes EndRun Technologies native time-of-day serial messages and exports kernel sensors.

Data model:
- `struct endrun` contains a fixed receive buffer, time and signal sensors, sensor device identity, current and last timestamps, timeout state, sentence gap tracking, last decoded time, sync state, buffer position, and PPS-missing state.

Open/close:
- `endrunopen()` requires superuser, allocates per-tty state, initializes a timedelta sensor and signal sensor, attaches sensors, delegates base tty open to `TTYDISC`, installs a timeout, and stores state in `tp->t_sc`.
- `endrunclose()` switches back to `TTYDISC`, removes timeout and sensors, frees state, resets instance numbering when last instance closes, and delegates base close.

Input and parsing:
- `endruninput()` collects fixed-length EndRun messages ending in CRLF, treats the character after LF as the on-time TFOM character, captures the best timestamp, checks optional tty PPS/modem timestamps, and passes all input through to the normal termios discipline.
- `endrun_scan()` splits the sentence into fields.
- `endrun_decode()` validates field count, date, time, optional local-time offset, monotonicity, TFOM, and PPS state; then updates sensor timedelta and signal status.

Conversion helpers:
- `endrun_atoi()` validates fixed-width decimal strings.
- `endrun_date_to_nano()` converts year plus day-of-year to nanoseconds since the epoch.
- `endrun_time_to_nano()` converts `HH:MM:SS`.
- `endrun_offset_to_nano()` converts signed half-hour UTC offsets for local mode.

Sensor degradation:
- `endrun_timeout()` degrades the time sensor from OK to WARN and then CRIT when valid strings stop arriving.
- TFOM values 6/7/8 are OK, 9 warns, invalid TFOM is critical; timestamping requested without detected PPS marks the time sensor critical.

Filesystem/storage relevance:
- No filesystem logic. Relevant as a specialized tty line discipline using character-device input, tty timestamp flags, and kernel sensor registration.
<!-- END FILE RESEARCH: sources/os/bsd/openbsd-src/sys/kern/tty_endrun.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/openbsd-src/sys/kern/tty_msts.c -->
# File Research: sources/os/bsd/openbsd-src/sys/kern/tty_msts.c

TTY line discipline that decodes Meinberg Standard Time String data and exposes time/signal sensors.

Data model:
- `struct msts` stores a sentence buffer, time and signal sensors, sensor device identity, timestamp/gap tracking, timeout state, last decoded time, sync state, input position, and PPS-missing flag.

Open/close:
- `mstsopen()` requires superuser, allocates state, initializes sensors, sets sync mode to wait for STX, delegates base tty open, installs the sensor device, and sets a timeout.
- `mstsclose()` restores `TTYDISC`, deletes timeout, deinstalls sensors, frees state, and delegates base tty close.

Input and parsing:
- `mstsinput()` starts a sentence at ASCII STX, ends at ETX, records best available timestamp, validates optional tty PPS/modem timestamp proximity, scans completed sentences, and still passes bytes to termios.
- `msts_scan()` splits fields on semicolons.
- `msts_decode()` validates field count, parses date/time, applies CET/CEST offset based on status field, checks monotonicity, computes timedelta, updates signal/time status, and arms the trust timeout only for valid status.

Conversion helpers:
- `msts_date_to_nano()` converts `D:DD.MM.YY` to epoch nanoseconds.
- `msts_time_to_nano()` converts `U:HH.MM.SS` to nanoseconds since midnight with digit-by-digit bounds.

Sensor degradation:
- `msts_timeout()` degrades time status from OK to WARN and then CRIT if valid strings stop arriving.
- Requested tty timestamping without PPS sets time status critical.

Filesystem/storage relevance:
- No filesystem logic. Relevant as tty line-discipline parsing and kernel sensor publication for serial time devices.
<!-- END FILE RESEARCH: sources/os/bsd/openbsd-src/sys/kern/tty_msts.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/openbsd-src/sys/kern/tty_nmea.c -->
# File Research: sources/os/bsd/openbsd-src/sys/kern/tty_nmea.c

TTY line discipline that decodes NMEA 0183 GNSS serial data and exposes time, signal, position, altitude, and speed sensors.

Data model:
- `struct nmea` stores an NMEA sentence buffer, sensors for timedelta/signal/latitude/longitude/altitude/speed, sensor-device identity, timestamp/gap tracking, trust timeout, last decoded time, sync state, PPS-missing state, and current GPS mode.

Open/close:
- `nmeaopen()` requires superuser, allocates per-tty state, initializes all sensors as unknown/invalid, attaches them to a sensor device, delegates base tty open, installs the sensor device, and sets a timeout.
- `nmeaclose()` restores `TTYDISC`, removes timeout and sensors, frees state, resets instance numbering when appropriate, and delegates base close.

Input and parsing:
- `nmeainput()` starts collection at `$`, ends at CR or LF, records the best timestamp, optionally compares tty PPS/modem timestamps, and passes all bytes to the termios discipline.
- `nmea_scan()` splits fields, computes and validates optional checksum, filters known GNSS talkers (`BD`, `GA`, `GL`, `GN`, `GP`), and dispatches only `RMC` and `GGA` sentences.
- `nmea_gprmc()` decodes time/date, fix status, mode, latitude, longitude, and ground speed.
- `nmea_decode_gga()` decodes altitude from GPS fix data.

Conversion helpers:
- `nmea_atoi()` parses decimal numeric fields to fixed thousandths.
- `nmea_degrees()` converts NMEA degree-minute coordinates to angle sensor units.
- `nmea_date_to_nano()` converts `DDMMYY` to epoch nanoseconds.
- `nmea_time_to_nano()` converts `HHMMSS[.fraction]` to nanoseconds since midnight.

Sensor behavior:
- Valid RMC fix status marks time, signal, latitude, longitude, and speed OK and clears invalid flags.
- Void status marks signal critical and location/speed warning.
- GGA altitude clears altitude invalid flag when parsed.
- Timeout marks signal critical and degrades or invalidates all exposed sensors.
- Missing PPS when timestamping was requested marks time critical.

Filesystem/storage relevance:
- No filesystem logic. Relevant as a tty line discipline that turns character-device serial input into kernel sensor state while preserving normal termios input flow.
<!-- END FILE RESEARCH: sources/os/bsd/openbsd-src/sys/kern/tty_nmea.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/openbsd-src/sys/kern/tty_pty.c -->
# File Research: sources/os/bsd/openbsd-src/sys/kern/tty_pty.c

Implements OpenBSD pseudo-terminal devices: slave side (`pts`), controller/master side (`ptc`), dynamic pty allocation, readiness notification, packet/user-control modes, and `/dev/ptm` allocation.

Major structures and globals:
- `struct pt_softc`: per-pty state containing the tty, flags, read/write selectors, packet/user-control bytes, and master/slave device names.
- `pt_softc`: dynamically grown array of pty softc pointers.
- `pt_softc_lock`: protects the pty array.
- `pts_major`, `npty`, `maxptys`, `tty_gid`: device and allocation metadata.

Allocation and naming:
- `ptyattach()` allocates the initial pty table and ensures ptm support is attached.
- `check_pty()` grows the pty array by powers of two up to `maxptys`, allocates missing softc objects, allocates the backing tty with `ttymalloc()`, and constructs `/dev/ptyXX` and `/dev/ttyXX` names.
- `ptydevname()` maps minor numbers to traditional pty letter/suffix names.
- `pty_getfree()` finds a free pty by checking whether the tty has an output procedure.

Slave side:
- `ptsopen()` initializes tty defaults, waits for carrier unless nonblocking, and opens the current line discipline.
- `ptsclose()` closes the line discipline, closes the tty, and wakes the controller.
- `ptsread()` handles remote mode reads from canonical queue or delegates to the active line discipline.
- `ptswrite()` writes through the active line discipline when the controller is present.
- `ptsstart()` and `ptsstop()` notify the controller of output availability and packet-mode stop/start/flush events.

Controller side:
- `ptcopen()` marks the controller active by setting `t_oproc`, asserts modem carrier through the line discipline, clears external processing, and resets pty mode flags.
- `ptcclose()` drops modem carrier and clears `t_oproc`.
- `ptcread()` reads slave output, packet-mode and user-control headers, and termios state for `TIOCPKT_IOCTL`.
- `ptcwrite()` injects controller input into the slave side, either as remote-mode canonical records or through the active line discipline input function.

Ioctls and modes:
- `ptyioctl()` handles controller-specific behavior for packet mode, user-control mode, remote mode, process group query, signal injection, and master-side `FIONREAD`.
- It delegates to line-discipline and generic tty ioctls, translates break ioctls into user-control notifications when enabled, and emits packet-mode ioctl/start/stop notifications.

Readiness notification:
- Controller kqueue filters report output available for master reads, input capacity for master writes, out-of-band packet/user-control data, and poll/select hangup state.
- `ptcwakeup()` wakes selectors and sleepers on either perspective of the pty pair.

`/dev/ptm`:
- `ptmattach()` locates the pty slave major number.
- `ptmioctl(PTMGET)` allocates two file descriptors, races to open a free master, changes slave ownership/mode when possible, revokes existing slave users, reopens the slave, fills `struct ptmget`, and installs both vnode-backed files into the descriptor table.
- `ptm_vn_open()` is a constrained vnode open helper using temporary root credentials for pty nodes.

Filesystem/storage relevance:
- Strong character-device/VFS relevance: the `PTMGET` path opens and installs master/slave vnodes, updates vnode timestamps, changes slave ownership and mode, revokes aliases, and coordinates file-descriptor insertion for pty allocation.
<!-- END FILE RESEARCH: sources/os/bsd/openbsd-src/sys/kern/tty_pty.c -->