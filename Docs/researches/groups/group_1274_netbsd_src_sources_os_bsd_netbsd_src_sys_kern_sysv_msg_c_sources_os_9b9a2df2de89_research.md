# Group Research: group_1274_netbsd_src_sources_os_bsd_netbsd_src_sys_kern_sysv_msg_c_sources_os_9b9a2df2de89

Scope: `Docs/research_subset_a.md` includes `sources/os/bsd/netbsd-src`. All listed source files were read completely.

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/sys/kern/sysv_msg.c -->
# File Research: sources/os/bsd/netbsd-src/sys/kern/sysv_msg.c

## Purpose

`sysv_msg.c` implements NetBSD's System V message queue facility: queue creation/removal, message send/receive, queue metadata control, permission checks, blocking semantics, and runtime resizing of selected IPC limits.

## Main Responsibilities

- Initializes and tears down the global SysV message subsystem.
- Maintains message queue descriptors, message headers, segment maps, and the message byte pool.
- Implements `msgget`, `msgsnd`, `msgrcv`, and `msgctl`.
- Supports compatibility entry points through `msgsnd1`, `msgrcv1`, and `msgctl1`.
- Enforces `ipc_perm` permissions and privileged queue-size increases through kauth.
- Exposes writable `kern.ipc.msgmni` and `kern.ipc.msgseg` sysctls.

## Core Data Model

The subsystem allocates one wired block containing `msgpool`, `msgmaps`, `msghdrs`, and `msqs`. Message bodies are stored as chains of fixed-size segments indexed by `struct msgmap`; message metadata lives in `struct __msg` headers. Each queue is a `kmsq_t` containing `struct msqid_ds` plus a condition variable.

Queue IDs combine an array index with the queue sequence number, so stale IDs fail sequence validation after reuse.

## Send and Receive Behavior

`msgsnd1()` validates ID, sequence, permissions, and message type, then waits until the queue has room, free segment maps, and a free message header. While copying from user memory it marks the queue `MSG_LOCKED` so the descriptor is not reused mid-copy. On success it appends the message, updates byte/message counts, sender PID, timestamp, and wakes waiters.

`msgrcv1()` selects either the first message, an exact type, or the first type less than or equal to `abs(msgtyp)` for negative type requests. It honors `IPC_NOWAIT`, `MSG_NOERROR`, and sequence changes after sleeps. Bookkeeping is updated before copying to user memory, then the message header and segments are returned to the free lists.

## Control and Resizing

`msgctl1()` handles `IPC_STAT`, `IPC_SET`, and `IPC_RMID`. Removal frees all queued messages, marks the slot free by setting `msg_qbytes` to zero, and wakes sleepers.

`msgrealloc()` allocates a new wired layout, marks a global reallocation state, wakes and drains receive/send waiters, verifies the new limits can hold existing queues and segments, copies live queues/messages into the new arrays, swaps the global pointers, and frees the old block.

## Concurrency Notes

`msgmutex` protects all global message state. Per-queue condition variables coordinate senders/receivers. `msg_waiters`, `msg_realloc_state`, and `msg_realloc_cv` coordinate sysctl resizing with sleepers so waiters restart against the new arrays rather than retaining stale pointers.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/sys/kern/sysv_msg.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/sys/kern/sysv_sem.c -->
# File Research: sources/os/bsd/netbsd-src/sys/kern/sysv_sem.c

## Purpose

`sysv_sem.c` implements NetBSD's System V semaphore sets: allocation, control operations, vectorized atomic semaphore operations, timed waits, SEM_UNDO process cleanup, and runtime resizing of semaphore limits.

## Main Responsibilities

- Initializes and tears down semaphore identifiers, semaphore storage, wait condition variables, and undo records.
- Implements `semget`, `semctl`, `semop`, and `semtimedop`.
- Maintains per-process undo vectors and applies them at process exit.
- Supports dynamic resizing of `semmni`, `semmns`, and `semmnu`.
- Registers an exit hook lazily when semaphore syscalls are used.

## Core Data Model

The subsystem uses one wired memory block split into:

- `sema`: array of `struct semid_ds` semaphore-set descriptors.
- `sem`: packed array of individual `struct __sem` objects.
- `semcv`: one condition variable per semaphore set.
- `semu`: fixed-size pool of process undo vectors.

`semtot` tracks the number of live semaphores in the packed `sem` array. Removing a set compacts later semaphores and adjusts `_sem_base` pointers in other descriptors.

## Semaphore Operations

`semget()` finds an existing set by key or allocates a new one if requested, enforcing per-set and global semaphore limits.

`semctl1()` implements descriptor metadata operations plus `GETVAL`, `GETALL`, `SETVAL`, `SETALL`, `GETPID`, `GETNCNT`, and `GETZCNT`. Set/remove/value mutations clear affected SEM_UNDO entries and wake sleepers.

`do_semop1()` applies a vector of operations atomically. It rolls back partial changes if any operation cannot proceed, waits on the set condition variable unless `IPC_NOWAIT` applies, updates wait counters, supports timeouts, and translates timeout/interruption errors. SEM_UNDO adjustments are applied only after the vector succeeds; failures while adding undo records roll back both undo state and semaphore values.

## Process Exit

`semexit()` scans the global undo list for the exiting process, applies each stored adjustment to surviving semaphore sets, clamps negative underflow to zero, wakes affected waiters, and removes the undo vector.

## Concurrency Notes

`semlock` protects all semaphore state. `sem_realloc_state`, `sem_waiters`, and `sem_realloc_cv` coordinate resizing with blocked `semop` callers. `RUN_ONCE` protects lazy installation of the exit hook.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/sys/kern/sysv_sem.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/sys/kern/sysv_shm.c -->
# File Research: sources/os/bsd/netbsd-src/sys/kern/sysv_shm.c

## Purpose

`sysv_shm.c` implements NetBSD's System V shared memory facility: segment creation, lookup, attach/detach, control operations, fork/exit integration with VM spaces, memory wiring, and sysctl-tunable limits.

## Main Responsibilities

- Maintains global shared-memory segment descriptors and per-segment wait condition variables.
- Implements `shmget`, `shmat`, `shmdt`, and `shmctl`.
- Tracks per-vmspace shared-memory mappings through `vm_shm`.
- Integrates with UVM by installing `uvm_shmfork` and `uvm_shmexit` callbacks.
- Supports `SHM_LOCK`, `SHM_UNLOCK`, `_SHM_RMLINGER`, and global physical-memory locking policy.
- Exposes `shmmax`, `shmmni`, `shmseg`, `shmmaxpgs`, and `shm_use_phys` sysctls.

## Core Data Model

`shmsegs` is the global array of `struct shmid_ds` descriptors. Each allocated segment owns a UVM anonymous object in `_shm_internal`. `shm_nused` and `shm_committed` enforce descriptor and total-page limits.

Each vmspace's `vm_shm` points to a `shmmap_state`, which contains a refcounted list of mappings. Fork shares the mapping list and increments segment attach counts; detach or mutation uses `shmmap_getprivate()` to split a shared map.

## Segment Lifecycle

`shmget()` finds existing segments by key or allocates a new descriptor. During UAO allocation it marks the descriptor allocated but removed, increments `shm_realloc_disable`, drops the global lock, then finalizes permissions and wakes any key lookup waiters.

`shmat()` validates ID, sequence, permissions, attach count, address alignment, and flags, then inserts a mapping entry, references the UVM object, and maps it with shared inheritance.

`shmdt()` removes the per-vmspace mapping, decrements attach count, unmaps the address range, and frees the segment if it had been removed and the last attachment is gone.

`shmctl1()` supports `IPC_STAT`, `IPC_SET`, `IPC_RMID`, `SHM_LOCK`, and `SHM_UNLOCK`. Removal is deferred until `shm_nattch` reaches zero unless there are no attachments.

## Concurrency Notes

`shm_lock` protects descriptors, mapping lists, counters, and reallocation state. `shm_realloc_state`, `shm_realloc_disable`, and `shm_realloc_cv` prevent descriptor-array resizing while an allocation has dropped the lock. Per-segment condition variables wake waiters for in-progress keyed creation.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/sys/kern/sysv_shm.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/sys/kern/tty.c -->
# File Research: sources/os/bsd/netbsd-src/sys/kern/tty.c

## Purpose

`tty.c` is NetBSD's main terminal subsystem implementation. It handles terminal lifecycle, termios processing, input canonicalization, output processing, ioctls, read/write paths, job control, flow control, poll/kqueue support, tty allocation, controlling terminal state, and deferred tty-generated signal delivery.

## Main Responsibilities

- Provides global tty locking, tty lists, queue sizing, and subsystem initialization.
- Implements default terminal line discipline operations used by `tty_conf.c`.
- Processes input characters with termios rules, erase/kill/reprint/status controls, software flow control, canonical/noncanonical buffering, echoing, and signal generation.
- Processes output with termios output transformations, queueing, high/low water marks, and device start callbacks.
- Implements common tty ioctls for termios, line discipline changes, process groups, controlling terminal setup, console redirection, queue sizing, window size, and pty pass-through commands.
- Implements `ttread`, `ttwrite`, `ttpoll`, `ttykqfilter`, `ttywait`, `ttyflush`, and modem-carrier handling.
- Manages tty references used by `constty` and close/revoke synchronization.
- Defers tty-originated signal delivery through a soft interrupt.

## Core Data Model

Each `struct tty` owns raw, canonical, and output clists, termios flags/control characters, process/session pointers, condition variables, select/kqueue state, output callbacks, and deferred signal sets.

The subsystem uses a single global spin mutex `tty_lock` for tty state. `proc_lock` protects process group/session interactions. `constty_lock` plus pserialize and `t_refcnt` protect the special console tty reference path.

## Input and Read Path

`ttyinput_wlock()` handles break/parity/framing conditions, IXOFF and hardware input flow control, literal-next, discard, signals, IXON start/stop, CR/NL translation, canonical erase/kill/word erase/reprint/status handling, buffer overflow policy, line delimiter detection, and echoing.

`ttread()` enforces background read job-control rules, handles canonical reads from `t_canq`, noncanonical `VMIN`/`VTIME` behavior, delayed suspend, EOF processing, user copying, and unblocking of software/hardware input flow control as queues drain.

## Output and Write Path

`ttyoutput()` performs output post-processing including tab expansion, ONLCR/OCRNL/ONOCR/ONLRET handling, CEOT suppression, column accounting, and queue insertion.

`ttwrite()` enforces carrier and background write rules, fetches user data in chunks, fast-paths ordinary output with `b_to_q`, sends special characters through `ttyoutput`, starts device output, and sleeps when the output queue is above the high-water mark.

## Ioctl and Job Control

`ttioctl()` provides shared tty ioctl handling after line-discipline-specific logic. It implements termios get/set, discipline switching, process-group/session queries and updates, `TIOCSCTTY`, `TIOCSTI` authorization, `TIOCCONS`, queue flush/drain, queue size changes, `TIOCSTAT`, window-size changes, and compatibility/module hooks.

Foreground/background checks use `isbackground`, process group state, and `SIGTTIN`/`SIGTTOU`. `ttysig()` queues terminal-generated signals for later delivery to the foreground process group, async I/O process group, or session leader.

## Initialization and Lifetime

`tty_alloc()` allocates the tty, clists, condition variables, callout, line-discipline reference, and select state. `tty_attach()`/`tty_detach()` maintain the global tty list. `ttyclose()` removes console status, flushes queues, bumps the generation number, clears session/process group state, waits for references to drain, and releases the session reference.

`tty_init()` initializes locks, pserialize, condition variables, softint signal handling, a kauth listener for exclusive opens, and `kern.tkstat` / `kern.tty.qsize` sysctls.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/sys/kern/tty.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/sys/kern/tty_bsdpty.c -->
# File Research: sources/os/bsd/netbsd-src/sys/kern/tty_bsdpty.c

## Purpose

`tty_bsdpty.c` provides the legacy BSD pty naming and vnode-allocation backend for the pty multiplexor when `COMPAT_BSDPTY` is enabled and `/dev/ptm` support is present.

## Main Responsibilities

- Defines a `struct ptm_pty` handler named `ptm_bsdpty`.
- Generates legacy `/dev/[pt]tyXX` names from pty device minors.
- Looks up the corresponding vnode with `namei`.
- Supplies default slave ownership and mode attributes.
- Reports no associated ptyfs mount for the legacy backend.

## Behavior

`pty_makename()` fills `/dev/XtyXX`, using `p` or `t` for master/slave and choosing suffix tables for old and extended minor ranges.

`pty_allocvp()` builds the legacy path and performs a `NOFOLLOW|LOCKLEAF` lookup, returning a locked vnode.

`pty_getvattr()` sets slave attributes to the caller's real UID, fixed tty group `4`, and mode `0620`.

## Integration Notes

The file is compiled only under the relevant pty options. Its exported `ptm_bsdpty` handler is installed by `ptmattach()` in `tty_ptm.c` when compatibility BSD ptys are configured.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/sys/kern/tty_bsdpty.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/sys/kern/tty_conf.c -->
# File Research: sources/os/bsd/netbsd-src/sys/kern/tty_conf.c

## Purpose

`tty_conf.c` manages NetBSD line discipline registration, lookup, reference counting, and the built-in termios/ntty disciplines.

## Main Responsibilities

- Defines the default `termios` line discipline and the legacy-compatible `ntty` discipline.
- Initializes the line discipline list with the built-ins.
- Looks up disciplines by name or legacy number.
- Attaches and detaches dynamic line disciplines.
- Assigns legacy numeric discipline IDs.
- Provides default pass-through ioctl and error poll helpers.

## Core Data Model

`ttyldisc_list` is a global list of `struct linesw` entries protected by `tty_lock`. Built-in `termios_disc` and `ntty_disc` are considered static and are not refcounted. Dynamic disciplines use `l_refcnt` and cannot be detached while in use.

## Behavior

`ttyldisc_lookup()` and `ttyldisc_lookup_bynum()` return a held reference. `ttyldisc_release()` drops it. `ttyldisc_attach()` validates required callbacks, enforces name length and uniqueness, assigns a legacy number, and inserts the discipline. `ttyldisc_detach()` refuses removal while the discipline is static or referenced.

`ttyldisc_default()` returns the built-in termios discipline used by new ttys.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/sys/kern/tty_conf.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/sys/kern/tty_ptm.c -->
# File Research: sources/os/bsd/netbsd-src/sys/kern/tty_ptm.c

## Purpose

`tty_ptm.c` implements the pty multiplexor character device `/dev/ptm` and `/dev/ptmx`, allocating pty master/slave pairs and returning file descriptors and names to userland.

## Main Responsibilities

- Registers the `ptm_cdevsw` device switch, or a disabled no-op switch when `NO_DEV_PTM` is configured.
- Tracks pty master/slave major numbers.
- Finds a free pty minor and opens the master vnode.
- Grants/revokes the slave side by updating ownership/mode and revoking prior users.
- Allocates master and slave file descriptors for `TIOCPTMGET`.
- Supports `/dev/ptmx` open semantics using `EMOVEFD`.
- Provides hooks for alternate pty backends through `struct ptm_pty`.

## Allocation Flow

`pty_alloc_master()` reserves a file descriptor, finds a free pty, asks the active `ptm` backend for the master vnode, opens it as root credentials, initializes the file object, and affixes it to the process. Races for the same master retry when appropriate.

`pty_grant_slave()` obtains the slave vnode, applies backend-provided attributes if the filesystem is writable, revokes all existing users, and releases the stale vnode.

`pty_alloc_slave()` opens the slave vnode and affixes a second descriptor.

`ptmioctl(TIOCPTMGET)` combines these steps and fills `struct ptmget` with fds and pty names. `ptmopen()` handles `/dev/ptmx` by allocating a master and returning it via `l_dupfd`; the Linux-emulation minor also grants the slave immediately.

## Integration Notes

`ptmattach()` discovers the real pty cdev major numbers and installs the BSD compatibility backend when configured. `pty_sethandler()` lets another backend replace the active `ptm` handler.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/sys/kern/tty_ptm.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/sys/kern/tty_pty.c -->
# File Research: sources/os/bsd/netbsd-src/sys/kern/tty_pty.c

## Purpose

`tty_pty.c` implements NetBSD's pseudo-terminal master and slave character devices, including dynamic pty allocation, master/slave I/O, packet/user-control modes, remote mode, polling/kqueue readiness, and pty-specific ioctls.

## Main Responsibilities

- Defines master `ptc_cdevsw` and slave `pts_cdevsw` device switches.
- Maintains the dynamically growable `pt_softc` table and `npty`/`maxptys` limits.
- Allocates per-pty `struct tty` objects and select state.
- Implements slave open/close/read/write/poll via the tty line discipline.
- Implements master open/close/read/write/poll and kqueue filters.
- Bridges tty output from slave to master and master input to slave.
- Implements pty ioctls: `TIOCPKT`, `TIOCUCNTL`, `TIOCREMOTE`, `TIOCPTSNAME`, `TIOCGRANTPT`, `TIOCSIG`, and pty-specific `FIONREAD`.

## Core Data Model

Each `pt_softc` holds a `struct tty *`, pty flags, master-side select state, packet-mode pending byte, and user-control byte. `pt_softc_mutex` protects table growth and installation; normal tty I/O state is protected by `tty_lock`.

`pty_check()` validates a requested minor, grows the pty table up to `maxptys`, allocates missing softc/tty structures, initializes select state, and attaches the tty.

## Slave Side

`ptsopen()` initializes default termios state on first open, waits for carrier unless nonblocking, opens the line discipline, and wakes the master. `ptsclose()` closes the line discipline, calls `ttyclose()`, and wakes master waiters.

`ptsread()` normally delegates to the line discipline read path; in remote mode it reads from `t_canq` with a trailing NUL delimiter convention. `ptswrite()` delegates to the line discipline write path when the master is present.

## Master Side

`ptcopen()` claims an unused pty by setting `t_oproc = ptsstart`, marks carrier through the line discipline modem hook, and clears pty flags. `ptcclose()` drops carrier and clears `t_oproc`.

`ptcread()` returns pending packet/control bytes first, then drains slave output from `t_outq`. `ptcwrite()` injects master input into the slave side, either as remote-mode records or by feeding each byte to the line discipline receive routine.

`ptsstart()`, `ptsstop()`, and `ptcwakeup()` translate tty output/stop/flush state into master-side wakeups and packet-mode notifications.

## Ioctl Behavior

`ptyioctl()` handles pty-specific controls before falling through to line discipline and common tty ioctls. Packet mode and user-control mode are mutually exclusive. Remote mode flushes tty queues. `TIOCSIG` validates the signal, optionally flushes queues, marks SIGINFO state, and queues a tty signal. When external processing and packet mode are enabled, termios-setting ioctls generate `TIOCPKT_IOCTL`.

## Concurrency Notes

The pty table is protected separately from tty state. I/O paths carefully drop `tty_lock` while copying to/from user memory and re-check open/carrier state after reacquiring it.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/sys/kern/tty_pty.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/sys/kern/tty_subr.c -->
# File Research: sources/os/bsd/netbsd-src/sys/kern/tty_subr.c

## Purpose

`tty_subr.c` implements the clist queue primitives used by NetBSD tty input/output buffering. The clists are ring buffers with optional per-character quote-bit tracking.

## Main Responsibilities

- Allocates and frees clist backing storage.
- Provides single-character get/put/unput operations.
- Provides bulk queue-to-buffer and buffer-to-queue transfers.
- Flushes bytes from a queue.
- Counts contiguous queue bytes up to flag-matching characters.
- Iterates queue contents for tty echo/retype logic.
- Concatenates queues.

## Core Data Model

A `struct clist` stores a circular byte buffer with start/end pointers, first/last pointers, capacity, count, and optional quote metadata. With `QBITS` enabled, quote state is stored as a compact bit array rather than one byte per character.

## Behavior

`putc()` and `b_to_q()` append data and maintain quote state. `getc()`, `q_to_b()`, `ndflush()`, and `unputc()` consume or remove data while updating ring pointers and counts. `getc()` wipes consumed bytes to avoid information disclosure.

`firstc()` and `nextc()` provide cursor-style traversal for callers that prevent concurrent queue mutation. `catq()` drains one clist into another with `getc()`/`putc()`.

## Concurrency Notes

Most mutating primitives raise to `spltty()` while manipulating ring state. Higher-level tty code generally also uses `tty_lock` around clist operations that interact with terminal state.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/sys/kern/tty_subr.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/sys/kern/tty_tty.c -->
# File Research: sources/os/bsd/netbsd-src/sys/kern/tty_tty.c

## Purpose

`tty_tty.c` implements the indirect `/dev/tty` controlling-terminal character device. It forwards operations to the calling process's controlling terminal vnode.

## Main Responsibilities

- Resolves the current process's controlling tty vnode from session state.
- Forwards open, read, write, ioctl, poll, and kqueue filter operations.
- Implements `TIOCNOTTY` for non-session-leader callers.
- Rejects direct `TIOCSCTTY` through `/dev/tty`.

## Behavior

`cttyopen()` locks and opens the session's tty vnode if present. `cttyread()` and `cttywrite()` forward VOP reads/writes with `NOCRED`. `cttyioctl()` forwards most ioctls, clears `PL_CONTROLT` for non-session-leader `TIOCNOTTY`, and returns errors when no controlling tty exists.

`cttypoll()` returns `seltrue` if there is no controlling tty; otherwise it forwards to the underlying vnode. `cttykqfilter()` similarly attaches to the real vnode when available.

## Integration Notes

The exported `ctty_cdevsw` is a `D_TTY` character device wrapper and does not itself own a `struct tty`; it delegates through the session's vnode pointer.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/sys/kern/tty_tty.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/sys/kern/uipc_accf.c -->
# File Research: sources/os/bsd/netbsd-src/sys/kern/uipc_accf.c

## Purpose

`uipc_accf.c` implements the accept-filter registry and socket option support for NetBSD listen sockets. Accept filters delay completed accepts until protocol-specific readiness criteria are met.

## Main Responsibilities

- Initializes the global accept-filter list and `net.inet.accf` sysctl node.
- Registers and unregisters `struct accept_filter` implementations.
- Looks up filters by name, including module autoload attempts.
- Implements getsockopt/setsockopt support for `SO_ACCEPTFILTER`.
- Attaches filter instance state to listening sockets.
- Clears filters and releases in-flight queued sockets.

## Core Data Model

`accept_filtlsthd` is the global list of registered filters, protected by `accept_filter_lock`. Each filter has a reference count incremented on lookup and decremented when a socket filter instance is cleared or setup fails.

A listen socket's `so_accf` points to `struct so_accf`, which stores the selected filter, optional string, and filter-specific argument created by `accf_create`.

## Socket Option Behavior

`accept_filt_getopt()` requires a listening socket with an installed filter and returns `struct accept_filter_arg`.

`accept_filt_setopt()` treats a null/empty option as clear. Otherwise it copies and terminates the requested name/argument, looks up or autoloads the filter, preallocates instance storage, locks the socket, verifies it is a listen socket without an existing filter, calls `accf_create` if present, then installs `so_accf` and sets `SO_ACCEPTFILTER`.

`accept_filt_clear()` removes the filter from a listen socket, disables accept-filter upcalls on sockets still in the incomplete queue, calls `accf_destroy` if provided, frees stored state, clears `SO_ACCEPTFILTER`, and drops the filter reference.

## Concurrency Notes

The registry uses an rwlock and `RUN_ONCE` initialization. Socket operations assert or acquire the socket lock as documented: `accept_filt_clear()` expects it held, while `accept_filt_setopt()` is entered unlocked and returns with the socket locked.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/sys/kern/uipc_accf.c -->