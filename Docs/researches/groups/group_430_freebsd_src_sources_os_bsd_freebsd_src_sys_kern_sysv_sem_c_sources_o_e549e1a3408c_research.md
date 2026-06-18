# Group Research: group_430_freebsd_src_sources_os_bsd_freebsd_src_sys_kern_sysv_sem_c_sources_o_e549e1a3408c

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sys/kern/sysv_sem.c -->
# File Research: sources/os/bsd/freebsd-src/sys/kern/sysv_sem.c

## Purpose
Implements FreeBSD System V semaphore support as the `sysvsem` kernel module, including `semget`, `semop`, `__semctl`, semaphore undo-on-exit state, sysctl export, RACCT accounting, MAC checks, jail scoping, and legacy/32-bit ABI compatibility.

## Main Structures and State
- `struct sem`: per-semaphore value, last-operation PID, wait-for-increase count, and wait-for-zero count.
- `struct sem_undo`: per-process SEM_UNDO adjustment vector, stored in active/free lists.
- Global pools: `sema` for semaphore identifiers, `sem` for contiguous semaphore objects, `semu` for undo records, `sema_mtx[]` for per-set locking.
- Global locks: `sem_mtx` protects allocation/removal and pool compaction; `sem_undo_mtx` protects undo lists.
- `seminfo` exposes tunables and limits such as `semmni`, `semmns`, `semopm`, `semume`, `semvmx`, and `semaem`.

## Core Behavior
- `seminit()` allocates pools, initializes locks/MAC labels, sets up jail OSD state, registers process-exit hooks, and installs syscalls.
- `sys_semget()` finds a keyed semaphore set in the caller prison or allocates a new set, enforces limits, initializes `ipc_perm`, records credentials, and consumes RACCT `RACCT_NSEM`.
- `kern_semctl()` handles `IPC_RMID`, `IPC_SET`, `IPC_STAT`, `SEM_STAT`, `GET*`, `SETVAL`, and `SETALL`, applying permission checks, MAC checks, copyin/copyout safety, undo clearing, and waiter wakeups.
- `kern_semop()` validates operation vectors, computes required permissions, executes operations atomically with rollback on blocking/error, supports timed waits, manages `SEM_UNDO`, and updates `sempid`/`sem_otime`.
- `semexit_myhook()` applies outstanding SEM_UNDO adjustments at process exit and returns undo records to the free list.
- `sem_remove()` clears permissions, drops RACCT/credential references, clears undo entries, wakes waiters, and compacts the contiguous semaphore pool while locking affected sets.

## Jail and Visibility Model
- `sem_find_prison()` maps caller credentials to the jail root controlling System V semaphore visibility.
- `sem_prison_cansee()` only permits access to semaphore sets owned by the root prison or its descendants.
- `sem_prison_check/set/get/remove/cleanup()` implement `sysvsem` jail parameter semantics, including disable/new/inherit modes and cleanup of semaphores owned by a removed prison.

## External Interfaces
- Syscalls: `__semctl`, `semget`, `semop`, and old `semsys` where enabled.
- Sysctls under `kern.ipc.*`: semaphore limits plus opaque `sema` export.
- `kern_get_sema()` provides sanitized kernel copies for consumers that need semaphore metadata.
- Compatibility blocks translate old `semid_ds` layouts and FreeBSD32 pointer/structure formats.

## Dependencies
Uses kernel IPC permission helpers, audit hooks, RACCT, MAC framework, jail OSD, eventhandler process-exit hooks, syscall helper registration, mutexes, and sysctl.

## Notes and Risks
- Removal compacts the global semaphore array, so pointer updates and locking around `__sem_base` are critical.
- `GETALL`/`SETALL` intentionally drop and reacquire the set mutex around allocation/copyin, relying on sequence validation to detect replacement.
- Undo accounting is bounded by `seminfo.semume` and `seminfo.semmnu`; overflow returns `EINVAL`/`ENOSPC` and rolls back semaphore changes.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sys/kern/sysv_sem.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sys/kern/sysv_shm.c -->
# File Research: sources/os/bsd/freebsd-src/sys/kern/sysv_shm.c

## Purpose
Implements FreeBSD System V shared memory support as the `sysvshm` module, covering `shmget`, `shmat`, `shmdt`, `shmctl`, VM object backing, process fork/exit mapping hooks, jail scoping, accounting, sysctl export, Linux ABI info commands, and compatibility shims.

## Main Structures and State
- `struct shmid_kernel *shmsegs`: segment table.
- `struct shmmap_state`: per-process mapping record containing attach VA and shmid.
- Global counters: `shm_last_free`, `shm_nused`, `shmalloced`, `shm_committed`.
- `shminfo`: tunable limits for max/min size, number of IDs, segments per process, and total pages.
- `sysvshmsx`: exclusive `sx` lock protecting segment table and per-process SysV shm mapping state.

## Core Behavior
- `shminit()` initializes tunables, allocates segment table, installs fork/exit/object-info hooks when modular, configures jail OSD state, and registers syscalls.
- `sys_shmget()` finds a segment by key in the caller prison or allocates a new one.
- `shmget_allocate_segment()` enforces size/count/page limits, RACCT limits, allocates a swap- or phys-backed VM object, marks it `OBJ_SYSVSHM`, fills permissions/metadata, and returns an IPC id.
- `kern_shmat_locked()` validates ID/permission/MAC policy, allocates the process `vm_shm` array if needed, chooses/validates attach VA, maps the VM object with `vm_map_find()`, records attachment state, and increments `shm_nattch`.
- `kern_shmdt_locked()` finds a process mapping by VA and removes it with `vm_map_remove()`.
- `shm_delete_mapping()` decrements attach count, updates detach time, and deallocates removed segments after the last detach.
- `kern_shmctl_locked()` implements `IPC_STAT`, `IPC_SET`, `IPC_RMID`, plus Linux-facing `IPC_INFO`, `SHM_INFO`, and `SHM_STAT`.
- `shmfork_*()` duplicates the process mapping table and increments attach counts.
- `shmexit_*()` detaches all mappings during vmspace exit.

## Jail and Visibility Model
- `shm_find_prison()` maps a caller to the jail root for SysV shm.
- `shm_find_segment()` validates allocation, removal visibility, sequence number, and prison visibility.
- `shm_prison_*()` mirrors the semaphore jail model with `sysvshm` new/inherit/disable settings and cleanup of segments owned by a jail.

## External Interfaces
- Syscalls: `shmat`, `shmdt`, `shmget`, `shmctl`, old `shmsys` on supported compatibility builds.
- Sysctls under `kern.ipc.*`: `shmmax`, `shmmin`, `shmmni`, `shmseg`, `shmall`, `shm_use_phys`, `shm_allow_removed`, and `shmsegs`.
- `kern_get_shmsegs()` returns sanitized segment metadata.
- FreeBSD32 and old-FreeBSD compatibility paths translate structure layouts and saturate fields where necessary.

## Dependencies
Uses VM object/pager/map APIs, resource limits, RACCT, audit, MAC, jail OSD, syscall helper registration, sysctl, credentials, and process/vmspace lifecycle hooks.

## Notes and Risks
- The implementation serializes most operations through one `sx` lock, simplifying correctness but limiting concurrency.
- Segment removal is two-phase: `IPC_RMID` marks removed, and actual deallocation waits for `shm_nattch == 0`.
- `shm_allow_removed` controls whether removed-but-attached segments remain attachable.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sys/kern/sysv_shm.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sys/kern/tty.c -->
# File Research: sources/os/bsd/freebsd-src/sys/kern/tty.c

## Purpose
Core FreeBSD TTY framework. It provides character-device operations, TTY allocation/lifetime, termios state, controlling-terminal management, foreground/background job-control checks, `/dev/console`, `/dev/tty`-adjacent behavior, init/lock devices, sysctl listing, hooks, and DDB debugging.

## Main Structures and State
- Global `tty_list` plus `tty_list_sx` tracks all exposed TTYs for sysctl/debugging.
- Each `struct tty` owns termios state, input/output queues, condition variables, poll/kqueue state, flags, session/pgrp references, driver switch, softc, hook state, and optional custom mutex.
- `dev_console` and `dev_console_filename` implement `/dev/console` indirection.
- Tunables: `kern.tty_drainwait`, `security.bsd.allow_tiocsti`.

## Device Operations
- `ttydev_open()` serializes open/close, rejects gone devices, enforces callin/callout exclusion, exclusive mode, carrier wait, driver open, discipline open, and queue watermarks.
- `ttydev_close()` clears open flags, handles revoke cleanup, wakes blocked waiters, and delegates final teardown through `ttydev_leave()`.
- `ttydev_read()` and `ttydev_write()` call the line discipline while holding the TTY lock; writes serialize through `TF_BUSY_OUT` unless nonblocking.
- `ttydev_ioctl()` applies background job-control waits for mutating ioctls, applies init/lock termios masks, then calls `tty_ioctl()`.
- Poll and kqueue paths reflect line-discipline readability/writability and hangup/gone state.
- `ttydev_mmap()` delegates to the driver switch.

## Termios and Ioctls
- `tty_generic_ioctl()` handles modem bits, async owner, byte counts, termios get/set, line discipline query, pgrp/session ioctls, controlling TTY assignment/drop, flush/drain, console redirection, window size, exclusive mode, start/stop, status, and `TIOCSTI`.
- `tty_sti_check()` gates `TIOCSTI` with a global sysctl, privilege, read-open requirement, and controlling-terminal requirement.
- Termios changes filter unsupported flags, drain/flush for `TIOCSETAW/F`, call driver `param`, update queue watermarks, canonicalize input when needed, and notify PTY packet mode about start/stop settings.

## Lifetime and Device Nodes
- `tty_alloc_mutex()` patches missing driver callbacks with defaults, initializes termios, CVs, queues, kqueue lists, and locking.
- `tty_rel_free()` frees a TTY only after it is gone, unopened, hook-free, and no longer referenced by sessions.
- `tty_makedevf()` creates primary tty nodes, optional `.init`/`.lock` nodes, optional `cua*` callout nodes, sets ownership/modes, and inserts the TTY into `tty_list`.
- `tty_rel_gone()` simulates carrier loss, wakes waiters, marks `TF_GONE`, and attempts deferred free.

## Job Control and Sessions
- `tty_wait_background()` implements SIGTTIN/SIGTTOU background access semantics with orphaned pgrp and signal-mask handling.
- `TIOCSCTTY`, `TIOCNOTTY`, and `TIOCSPGRP` manipulate session and foreground process group state under `proctree_lock`.
- `tty_signal_sessleader()` and `tty_signal_pgrp()` send terminal-generated signals and clear stopped/flush-output state.

## Hooks and Console
- `ttyhook_register()` validates a file descriptor with `CAP_TTYHOOK`, verifies it references a tty cdev, attaches a hook, and updates bypass optimization.
- `ttyhook_unregister()` detaches and may trigger deferred free.
- `/dev/console` resolves the selected tty by name on open and logs console writes to the kernel message buffer.

## Diagnostics
- `kern.ttys` sysctl exports sanitized `xtty` records respecting visibility rules.
- Optional DDB commands show one tty or all ttys, including queue sizes, flags, termios, hooks, session/pgrp state, and driver callbacks.

## Notes and Risks
- Many operations intentionally drop and reacquire the TTY lock around allocations, user copies, ownership changes, and proctree operations.
- Correctness depends heavily on `TF_OPENCLOSE`, `TF_GONE`, `TF_ZOMBIE`, revoke counters, and condition-variable wakeups.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sys/kern/tty.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sys/kern/tty_compat.c -->
# File Research: sources/os/bsd/freebsd-src/sys/kern/tty_compat.c

## Purpose
Maps historical BSD tty ioctls and sgtty-style flags to modern `termios` operations when `COMPAT_43TTY` support routes unknown tty ioctls here.

## Main Structures and State
- `struct speedtab` maps integer baud rates to old compact speed codes.
- `compatspeeds[]` and `compatspcodes[]` translate between old speed indices and numeric rates.
- `ttydebug` sysctl under `debug.ttydebug` enables trace prints.

## Core Behavior
- `tty_ioctl_compat()` handles old setters (`TIOCSETP`, `TIOCSETN`, `TIOCSETC`, `TIOCSLTC`, `TIOCLBIS`, `TIOCLBIC`, `TIOCLSET`) by copying current termios, translating legacy state with `ttsetcompat()`, and re-entering `tty_ioctl()`.
- It handles old getters (`TIOCGETP`, `TIOCGETC`, `TIOCGLTC`, `TIOCLGET`) by projecting current termios into legacy structures.
- Old line discipline commands and console command aliases are mapped to modern `TIOCSETD`/`TIOCCONS` behavior.
- `ttcompatgetflags()` reconstructs old `sg_flags`/local flags from modern input/output/control/local flags.
- `ttcompatsetflags()` and `ttcompatsetlflags()` apply old RAW/CBREAK/CRMOD/PASS8/LITOUT/parity/echo/local flag semantics into termios.

## Dependencies
Uses `struct tty`, `struct termios`, compatibility ioctl structure definitions, and the generic `tty_ioctl()` path.

## Notes and Risks
- This is a translation layer, not a separate line discipline.
- It preserves legacy quirks such as rounded-down speed mapping and approximate RAW/CBREAK detection.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sys/kern/tty_compat.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sys/kern/tty_info.c -->
# File Research: sources/os/bsd/freebsd-src/sys/kern/tty_info.c

## Purpose
Implements tty status reporting for SIGINFO/`TIOCSTAT`, printing load average and foreground process information to the terminal.

## Core Behavior
- `proc_compare()` selects the most interesting process in the foreground pgrp, preferring runnable processes, higher CPU use, non-zombies, then higher PID.
- `thread_compare()` selects the most interesting thread in that process, preferring runnable/high-CPU/noninterruptible work.
- `tty_info()` prints load, command, PID, thread state, elapsed time, user/system CPU time, percent CPU, and RSS.
- When compiled with `STACK`, optional `kern.tty_info_kstacks` controls whether compact/long kernel stacks are included.
- `sbuf_tty_drain()` writes status through `tty_putstrn()` or console output when KDB is active.

## Dependencies
Uses scheduler CPU accounting, process/thread locks, pgrp membership, rusage calculation, VM resident counts, sbuf, optional stack capture, and TTY output processing.

## Notes and Risks
- Selection is intentionally best-effort; process/thread state can become stale after locks are dropped.
- Output is skipped if `tty_checkoutq()` says the TTY lacks enough output space.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sys/kern/tty_info.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sys/kern/tty_inq.c -->
# File Research: sources/os/bsd/freebsd-src/sys/kern/tty_inq.c

## Purpose
Implements the TTY input queue: block allocation, canonical line boundaries, quote bits, erase support, secure flushing, reprint iteration, and zero-copy-ish reads to userspace.

## Main Structures and State
- `struct ttyinq_block`: doubly-linked 128-byte data block plus per-byte quote bitmap.
- `ttyinq_zone`: UMA zone for input blocks.
- Queue offsets track begin, canonicalized line start, reprint position, end, block pointers, block count, and quota.
- `kern.tty_inq_flush_secure` controls whether flush zeroes buffered data.

## Core Behavior
- `ttyinq_setsize()` adjusts quota and allocates blocks, temporarily dropping the TTY lock.
- `ttyinq_free()` flushes and frees all blocks.
- `ttyinq_write()` appends bytes and sets/clears quote bits.
- `ttyinq_write_nofrag()` requires enough room for the whole write.
- `ttyinq_canonicalize()` marks all current input readable; `ttyinq_canonicalize_break()` scans backward for newline/EOF/EOL-style break characters.
- `ttyinq_findchar()` searches canonicalized bytes for a break character while honoring quote bits.
- `ttyinq_read_uio()` removes data and copies to userspace, using a fast path that temporarily removes whole blocks before `uiomove()`.
- `ttyinq_peekchar()` and `ttyinq_unputchar()` support erase/backspace behavior at the queue tail.
- Reprint-position helpers and line iterators support canonical retyping and display-width recalculation.

## Dependencies
Used heavily by `tty_ttydisc.c`; relies on TTY lock discipline and UMA.

## Notes and Risks
- Quote bits are essential for distinguishing literal control characters from active line-editing delimiters.
- Secure flush is password-conscious and zeroes all block data by default.
- Callers must respect assumptions around `flen` trimming and block-crossing reads.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sys/kern/tty_inq.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sys/kern/tty_outq.c -->
# File Research: sources/os/bsd/freebsd-src/sys/kern/tty_outq.c

## Purpose
Implements the TTY output queue, a simpler block queue used for terminal output buffering and driver/PTM reads.

## Main Structures and State
- `struct ttyoutq_block`: singly-linked data block.
- `ttyoutq_zone`: UMA zone for output blocks.
- Queue offsets track begin, end, first/last blocks, block count, and quota.

## Core Behavior
- `ttyoutq_setsize()` sets quota and allocates blocks while temporarily dropping the TTY lock.
- `ttyoutq_free()` flushes and frees all blocks.
- `ttyoutq_flush()` resets begin/end offsets without freeing blocks.
- `ttyoutq_write()` appends bytes up to available quota.
- `ttyoutq_write_nofrag()` requires enough room for an entire write.
- `ttyoutq_read()` copies bytes into a kernel buffer and recycles blocks.
- `ttyoutq_read_uio()` copies output directly to userspace where possible, temporarily removing whole blocks during `uiomove()`.

## Dependencies
Used by the tty line discipline, tty core drain/flush logic, PTY master reads, and driver output wakeup paths.

## Notes and Risks
- Unlike the input queue, there are no quote bits or canonical boundaries.
- Fast-path UIO reads depend on careful block removal/recycling while the TTY lock is dropped.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sys/kern/tty_outq.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sys/kern/tty_pts.c -->
# File Research: sources/os/bsd/freebsd-src/sys/kern/tty_pts.c

## Purpose
Implements pseudo-terminal master support and `posix_openpt()`, allocating PTY pairs with a master file object and a slave TTY device under `/dev/pts/N`.

## Main Structures and State
- `pts_pool`: unit-number allocator.
- `struct pts_softc`: per-PTY state, unit, packet-mode flags, unread packet byte, master-side CVs/poll state, optional external master cdev, and credential for resource accounting.
- `ptsdev_ops`: file operations for the PTY master.
- `pts_class`: tty driver switch for the slave side.

## Master File Operations
- `ptsdev_read()` reads slave output through `ttydisc_getc_uio()`, emits packet-mode bytes first, blocks on `pts_outwait`, and handles nonblocking/EIO state.
- `ptsdev_write()` copies master input from userspace, feeds it into the line discipline with `ttydisc_rint_simple()`, blocks on input space, and wakes slave readers.
- `ptsdev_ioctl()` implements master-specific commands such as `FIODTYPE`, `FIONREAD`, `FIODGNAME`, `TIOCGPTN`, `TIOCGPGRP`, `TIOCGSID`, `TIOCPTMASTER`, `TIOCSIG`, `TIOCPKT`, Linux-friendly `TIOCGETA`, and redirects other ioctls to the slave tty.
- Poll/kqueue use reversed master-side semantics: master read watches slave output; master write watches slave input capacity.
- `ptsdev_stat()` fabricates character-device stat data from the slave or external master cdev.
- `ptsdev_close()` marks the tty gone and closes the original vnode if `/dev/ptmx` or old pty open changed the file type.

## Driver-Side Hooks
- `ptsdrv_outwakeup()` wakes master readers.
- `ptsdrv_inwakeup()` wakes master writers.
- `ptsdrv_open()` clears `PTS_FINISHED`; `ptsdrv_close()` sets it and wakes both sides.
- `ptsdrv_pktnotify()` accumulates packet-mode events and resolves conflicting start/stop flags.
- `ptsdrv_free()` releases unit number, RACCT/RLIMIT accounting, credentials, poll/kqueue resources, optional external cdev, and softc memory.

## Allocation
- `pts_alloc()` enforces `RACCT_NPTS` and `RLIMIT_NPTS`, allocates a unit, softc, tty, poll lists, exposes `pts/<unit>`, and initializes the master file as `DTYPE_PTS`.
- `pts_alloc_external()` supports old/external master cdev allocation without assigning a normal unit.
- `sys_posix_openpt()` validates flags, allocates a file descriptor/file, calls `pts_alloc()`, and returns the master fd.
- `pts_init()` initializes the unit allocator.

## Notes and Risks
- Packet mode multiplexes control notifications as leading bytes on master reads.
- Several comments document historical/Linux/POSIX compatibility behavior, including `fstat()` expectations and avoiding master-side drain deadlocks.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sys/kern/tty_pts.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sys/kern/tty_tty.c -->
# File Research: sources/os/bsd/freebsd-src/sys/kern/tty_tty.c

## Purpose
Implements `/dev/tty` clone behavior, resolving the calling process’s controlling terminal to the backing tty device or falling back to a dummy `ctty` device.

## Core Behavior
- `cttyopen()` always returns `ENXIO`; it is used when no valid controlling tty exists.
- `ctty_clone()` handles devfs clone requests for the name `tty`.
- It checks `curproc` under `proctree_lock` and `dev_lock()`:
  - If the process lacks `P_CONTROLT`, returns `ctty`.
  - If the session has no tty vnode, returns `ctty`.
  - If the vnode was revoked or lacks a device, returns `ctty`.
  - Otherwise returns the controlling tty vnode’s `v_rdev`.
- `ctty_drvinit()` registers the devfs clone event handler and creates the eternal `ctty` device.

## Dependencies
Uses devfs clone event handling, process/session controlling tty state, vnode/device references, and device reference locking.

## Notes and Risks
- This file does not implement normal tty I/O; it only maps `/dev/tty` opens to the right character device.
- The dummy device prevents invalid controlling-terminal lookups from accidentally resolving to stale devices.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sys/kern/tty_tty.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sys/kern/tty_ttydisc.c -->
# File Research: sources/os/bsd/freebsd-src/sys/kern/tty_ttydisc.c

## Purpose
Implements the standard termios TTY line discipline: canonical/raw reads, VMIN/VTIME semantics, output post-processing, input processing, echoing, erase/kill/word erase/reprint, signal generation, software flow control, bypass mode, hooks, and driver-facing getc/rint paths.

## Main State and Macros
- Counters: `kern.tty_nin` and `kern.tty_nout`.
- Termios helper macros compare control characters and flag fields.
- Control-character helpers classify tabs/newlines/control bytes/UTF-8 continuation bytes.
- Uses stack buffers for chunked input/output and UTF-8 erase handling.

## Read Path
- `ttydisc_read()` dispatches to canonical or raw implementations.
- Canonical reads use `ttyinq_findchar()` to stop at newline/VEOL/VEOF and trim VEOF from userspace output.
- Raw reads implement POSIX cases:
  - no timer (`VTIME == 0`),
  - read timer (`VMIN == 0`, `VTIME != 0`),
  - interbyte timer (`VMIN != 0`, `VTIME != 0`).
- Background reads call `tty_wait_background()` with `SIGTTIN`.
- After reading, input high-water state is cleared when enough space is available.

## Write Path
- `ttydisc_write()` chunks user data, applies `OPOST` processing, handles `FLUSHO`, writes into `ttyoutq`, sleeps on output high water unless nonblocking, and wakes the driver.
- `ttydisc_write_oproc()` handles `ONOEOT`, backspace column correction, tab expansion, newline-to-CRLF, CR-to-NL, `ONOCR`, `ONLRET`, and column/write-position maintenance.

## Input Path
- `ttydisc_rint()` processes received characters:
  - break/framing/parity handling with `IGNBRK`, `BRKINT`, `IGNPAR`, `PARMRK`;
  - `IXANY`, `ISTRIP`, literal-next;
  - discard/flush-output;
  - `VINTR`, `VQUIT`, `VSUSP`, `VSTATUS` signal generation;
  - `IXON` start/stop handling;
  - CR/NL conversion;
  - canonical erase, kill, word erase, and reprint.
- Accepted bytes are written to `ttyinq`; raw mode canonicalizes every byte, canonical mode canonicalizes on unquoted line delimiters.
- `ttydisc_rint_simple()` uses bypass mode when available; otherwise loops through `ttydisc_rint()`.
- `ttydisc_rint_bypass()` writes directly to input queue and canonicalizes all bytes for fast raw-like paths.
- `ttydisc_rint_done()` wakes readers and driver output for echo.

## Echo and Editing
- `ttydisc_echo_force()` renders control characters, `^X` notation, EOF backspacing, and normal echo.
- `ttydisc_rubchar()` removes the last canonical input byte, including quoted/control characters, tabs, and UTF-8 sequences using `teken` width helpers.
- `ttydisc_rubword()` implements word erase with optional `ALTWERASE`.
- `ttydisc_reprint()` reprints the current canonical line after `VREPRINT` or display disruption.

## Driver Output Side
- `ttydisc_getc()` drains output queue into a kernel buffer unless stopped and supports hooks for injection/capture.
- `ttydisc_getc_uio()` copies output to userspace, using direct queue UIO reads unless hooks require a shadow buffer.
- `ttydisc_getc_poll()` reports available output.
- `ttydisc_wakeup_watermark()` clears output high-water state when enough space is available.
- `tty_putstrn()` writes kernel strings through echo/output processing and wakes the driver.

## Hooks and Modem State
- `ttydisc_optimize()` enables `TF_BYPASS` when hooks or termios flags allow fast input.
- `ttydisc_modem()` handles carrier changes, wakes open waiters, enters zombie state on carrier loss, sends SIGHUP, and flushes queues.

## Dependencies
Depends on `tty_inq.c`, `tty_outq.c`, tty core locking/wakeup/signal helpers, `teken` UTF-8 width conversion, vnode/uio APIs, and tty hooks.

## Notes and Risks
- This is the behavioral center of terminal semantics; small flag interactions can change POSIX-visible behavior.
- UTF-8 erase logic must carefully restore input bytes when malformed sequences are detected.
- Bypass mode improves throughput but must be disabled when termios flags or hooks require per-character processing.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sys/kern/tty_ttydisc.c -->