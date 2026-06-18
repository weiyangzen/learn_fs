# subset-b-005466 research

Grouped research for `subset-b-005466`. Each section preserves the source path in its title and is delimited for deterministic splitting into source-tree-aligned per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/tty/tty_io.c -->
# sources/distributed-fs/ceph-client/drivers/tty/tty_io.c

Purpose: `tty_io.c` is the central Linux TTY core file. It registers the global TTY class and `/dev/tty`/`/dev/console` character devices, owns the global `tty_drivers` list, allocates and releases `struct tty_struct` and `struct tty_driver`, wires VFS file operations into line disciplines and low-level drivers, and implements the front-door ioctl dispatcher for generic TTY commands.

Important APIs, types, and functions: exported state includes `tty_std_termios`, `tty_drivers`, `tty_mutex`, `tty_name()`, `tty_dev_name_to_number()`, `tty_wakeup()`, `tty_hangup()`, `tty_vhangup()`, `tty_hung_up_p()`, `stop_tty()`, `start_tty()`, `tty_init_termios()`, `tty_standard_install()`, `tty_init_dev()`, `tty_save_termios()`, `tty_kref_put()`, `tty_kclose()`, `tty_release_struct()`, `tty_kopen_exclusive()`, `tty_kopen_shared()`, `tty_ioctl()`, `do_SAK()`, `alloc_tty_struct()`, `tty_put_char()`, `tty_register_device*()`, `tty_unregister_device()`, `__tty_alloc_driver()`, `tty_driver_kref_put()`, `tty_register_driver()`, `tty_unregister_driver()`, `tty_devnum()`, `tty_default_fops()`, `console_sysfs_notify()`, and `tty_init()`. Internal helper clusters cover file-private tracking, driver lookup, hangup file-operation replacement, redirected console writes, read/write iteration, open/reopen, final close, compat ioctl conversion, Secure Attention Key handling, device creation, and sysctl setup.

Control flow: read, write, and poll callbacks fetch the `tty_struct` from `file->private_data`, wait for a stable line discipline using `tty_ldisc_ref_wait()`, then call the ldisc methods. Writes serialize on `atomic_write_lock`, copy user iterators into `tty->write_buf`, and chunk requests to limit memory and driver complexity. Open first allocates `tty_file_private`, resolves `/dev/tty`, `/dev/console`, `tty0`, or a registered driver under `tty_mutex`, then either reopens an existing tty or calls `tty_init_dev()` for first open. Initial setup allocates the tty, installs it into the driver, attaches a port, locks and opens the line discipline, and returns with the tty lock held for the driver `open()` callback. Close decrements tty and pty-peer counts, removes file-private state, clears controlling tty state on final close, releases ldisc state, cancels pending work, saves termios, removes driver table entries, and drops krefs asynchronously through `release_one_tty()`.

State and persistence: persistent runtime state is in `tty_struct` fields: kref, driver, port, ldisc, termios, `termios_locked`, `winsize`, flow flags, file list, wait queues, session/pgrp pids, work items, and write buffers. Driver-wide state includes registered minors, cdevs, cached per-index termios, ports, and flip workqueue. Termios persists across closes unless the driver sets `TTY_DRIVER_RESET_TERMIOS`; dynamic device registration clears cached termios for reused minors. Hangup replaces live file operations with `hung_up_tty_fops`, clears session and pgrp pids, resets packet status and flow flags, and delegates to ldisc and driver hangup/close methods. Console redirection is a global file pointer protected by `redirect_lock`.

Dependencies and integration points: this file binds VFS, cdev, device core, sysfs, proc/sysctl, proc tty, console, VT, devpts, pty, signal/session, module refcounting, line discipline, tty buffer, termios, serial, and compatibility layers. Low-level TTY drivers integrate through `struct tty_operations`, `tty_register_driver()`, `tty_register_device_attr()`, driver `install/open/close/hangup/ioctl` callbacks, and `tty_port` helpers. Line disciplines receive reads, writes, poll, ioctl fallback, receive-buffer injection, hangup, and write wakeups. Job-control ioctls are delegated to `tty_jobctrl_ioctl()`, and mode/termios ioctls are often delegated to `tty_ioctl.c` through line discipline helpers.

Risks: lifecycle ordering is the main hazard. Miscounted tty, pty peer, kernel-open, file, driver, or module references can produce use-after-free or leaked devices. Lock ordering crosses `tty_mutex`, per-tty legacy mutex, ldisc semaphore, file-list spinlock, flow lock, termios rwsem, tasklist lock, and signal locks. Hangup races can leave stale file operations, blocked readers, stale line disciplines, or incorrect controlling tty references. `TIOCSTI`, `TIOCCONS`, `TIOCVHANGUP`, SAK, and compat serial ioctls have security-sensitive permission and namespace behavior. Driver callbacks are trusted to set `tty->port`, honor write-room contracts, and tolerate callbacks during close/hangup.

Test signals: exercise first open, reopen, final close, pty master/slave close ordering, kernel exclusive/shared open, driver unregister while open is impossible, ldisc open failure rollback, hangup during read/write/poll/open, `vhangup()` synchronicity, `/dev/tty` controlling-terminal reopen, `/dev/console` redirection, TIOCSTI permission/sysctl behavior, window resize `SIGWINCH`, modem and serial ioctls, compat ioctl paths, SAK process killing, dynamic device registration/unregistration, cached termios reuse/reset, sysfs `console/active`, and lockdep under concurrent ldisc changes and hangups.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/tty/tty_io.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/tty/tty_ioctl.c -->
# sources/distributed-fs/ceph-client/drivers/tty/tty_ioctl.c

Purpose: `tty_ioctl.c` implements generic TTY ioctl helpers for termios, legacy termio/sgtty modes, software and hardware flow control, flushing, output-drain waits, carrier-local state, baud/frame calculations, and line-discipline-visible ioctl handling. It is the common policy layer used by the N_TTY line discipline and by `tty_io.c` ioctl fallback.

Important APIs: exported helpers include `tty_chars_in_buffer()`, `tty_write_room()`, `tty_driver_flush_buffer()`, `tty_unthrottle()`, `tty_wait_until_sent()`, `tty_termios_copy_hw()`, `tty_termios_hw_change()`, `tty_get_char_size()`, `tty_get_frame_size()`, `tty_set_termios()`, `tty_mode_ioctl()`, `tty_perform_flush()`, and `n_tty_ioctl_helper()`. Internal helpers include `tty_throttle_safe()`, `tty_unthrottle_safe()`, `unset_locked_termios()`, termios copy/translation routines, `set_termios()`, legacy `sgttyb`/`tchars`/`ltchars` handlers when enabled, `tty_change_softcar()`, and `__tty_perform_flush()`.

Control flow: termios-setting ioctls call `set_termios()`, which first checks job-control write permission through `tty_check_change()`, copies current termios, imports the user format, normalizes input and output speeds, optionally waits for pending output and serializes against writers, optionally flushes ldisc buffers, calls driver `wait_until_sent()`, then commits through `tty_set_termios()`. `tty_set_termios()` updates `tty->termios` under `termios_rwsem`, reapplies locked termios bits, blocks users from changing `ADDRB` directly, notifies the driver `set_termios()` callback or preserves hardware bits for dumb drivers, and then notifies the active line discipline. Flush paths coordinate ldisc buffer flushing, unthrottling, and driver-buffer flushing. `n_tty_ioctl_helper()` handles `TCXONC` and `TCFLSH`, then falls back to `tty_mode_ioctl()`.

State and persistence: the main persistent state is `tty->termios`, `tty->termios_locked`, `tty->flow.tco_stopped`, `TTY_THROTTLED`, and `tty->flow_change`. Termios locks mask selected fields so requested updates may be silently reverted to previous values. Soft-carrier ioctls persist by toggling `CLOCAL` and notifying the driver. Legacy format conversions map user-visible old ABI structures onto the same `ktermios` state.

Dependencies and integration points: driver operations used here include `chars_in_buffer`, `write_room`, `flush_buffer`, `throttle`, `unthrottle`, `wait_until_sent`, and `set_termios`. Line discipline operations include `flush_buffer` and `set_termios`. Job-control permission comes from `tty_check_change()` in `tty_jobctrl.c`; low-level send of software flow-control characters uses `tty_send_xchar()` and `__stop_tty()`/`__start_tty()` from `tty_io.c`. Architecture-specific weak conversion functions allow ABI-specific termios layouts.

Risks: ioctl behavior is ABI-sensitive across `termio`, old `termios`, `termios2`, optional BSD sgtty ioctls, and compat callers. Waiting for output while writers are active can race unless `atomic_write_lock` and buffer rechecks are preserved. Driver `write_room()` is a contract; overreporting can lose data. Incorrect locked-termios masking can let restricted fields change or wrongly reject valid updates. Flow-control state spans `flow.lock`, `termios_rwsem`, and driver callbacks, so throttle/unthrottle races are important.

Test signals: cover TCGET/TCSET variants with and without wait/flush, locked termios get/set permissions, `CLOCAL` soft-carrier toggles, old ABI structures when configured, `TCXONC` output stop/start and START/STOP character injection, `TCFLSH` for input/output/both, driver callbacks absent or present, baud/frame helper calculations including parity, stop bits, and `ADDRB`, concurrent writers during `TCSETSW/F`, and interrupted waits returning restart errors.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/tty/tty_ioctl.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/tty/tty_jobctrl.c -->
# sources/distributed-fs/ceph-client/drivers/tty/tty_jobctrl.c

Purpose: `tty_jobctrl.c` implements POSIX job-control behavior for controlling terminals. It decides when background process groups are signaled, attaches and detaches controlling ttys, maintains session and foreground process-group references on a tty, clears task `signal->tty` references, and services job-control ioctls from the generic TTY ioctl path.

Important APIs: exported or externally used functions include `__tty_check_change()`, `tty_check_change()`, `proc_clear_tty()`, `tty_open_proc_set_tty()`, `get_current_tty()`, `session_clear_tty()`, `tty_signal_session_leader()`, `disassociate_ctty()`, `no_tty()`, `tty_get_pgrp()`, and `tty_jobctrl_ioctl()`. Internal helpers include `is_ignored()`, `__proc_set_tty()`, `proc_set_tty()`, `tiocsctty()`, `session_of_pgrp()`, `tiocgpgrp()`, `tiocspgrp()`, and `tiocgsid()`.

Control flow: foreground checks compare the caller's process group with `tty->ctrl.pgrp` when the caller's controlling tty is the target. If the process is background and the relevant signal is not blocked/ignored and the group is not orphaned, a signal is sent and `-ERESTARTSYS` is returned; ignored `SIGTTIN` can become `-EIO`. On open, `tty_open_proc_set_tty()` assigns a controlling tty only for a session leader without one, only when the tty is unattached, and only with read access. `TIOCSCTTY` performs the explicit version, optionally stealing a tty from another session for `CAP_SYS_ADMIN`. `TIOCNOTTY` calls `no_tty()`, and `TIOCSPGRP` validates that the target process group is in the caller's session before replacing `tty->ctrl.pgrp`.

State and persistence: state lives in `tty->ctrl.session`, `tty->ctrl.pgrp`, each task's `signal->tty`, and `signal->tty_old_pgrp`. PID references are acquired and released explicitly with `get_pid()`/`put_pid()`, while tty references are held through `tty_kref_get()` in task signal state. Hangup/session-exit logic clears task references and returns a count so the caller can drop deferred tty krefs outside the tasklist walk.

Dependencies and integration points: this file integrates with scheduler signal structures, pid namespaces through `pid_vnr()`, tasklist traversal, `sighand->siglock`, `tty->ctrl.lock`, capability checks, generic TTY open/close/hangup in `tty_io.c`, and termios/ioctl policy in `tty_ioctl.c`. The job-control ioctl dispatcher is called from `tty_ioctl()` after pty master requests are normalized to the real slave tty.

Risks: bugs here are user-visible and security-sensitive. Permission mistakes can let write-only terminal handles become controlling ttys, let a process steal another session's tty, or permit invalid foreground process groups. Reference mistakes leak pids or leave task signal structures pointing at freed ttys. Locking spans tasklist, sighand, tty legacy mutex, and tty control spinlock; ordering must avoid deadlocks. Orphaned process-group and ignored/blocked signal handling must match POSIX expectations.

Test signals: cover background reads/writes/ioctls with ignored, blocked, orphaned, and normal signals; automatic controlling tty assignment on session-leader open with read-only, write-only, and `O_NOCTTY`; `TIOCSCTTY` normal, repeated, steal, and permission-denied cases; `TIOCNOTTY`; `TIOCGPGRP`/`TIOCSPGRP`/`TIOCGSID` through pty master and real tty; session-leader exit with and without a tty; hangup signal delivery and `tty_old_pgrp` cleanup; pid namespace visible return values.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/tty/tty_jobctrl.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/tty/tty_ldisc.c -->
# sources/distributed-fs/ceph-client/drivers/tty/tty_ldisc.c

Purpose: `tty_ldisc.c` manages TTY line discipline registration, lookup, reference-taking, switching, hangup handling, and final release. It provides the synchronization layer that lets VFS read/write/poll/ioctl code call ldisc callbacks while another process may be changing the discipline or a hangup may be tearing it down.

Important APIs: exported functions include `tty_register_ldisc()`, `tty_unregister_ldisc()`, `tty_ldisc_ref_wait()`, `tty_ldisc_ref()`, `tty_ldisc_deref()`, `tty_ldisc_flush()`, `tty_set_ldisc()`, `tty_ldisc_reinit()`, `tty_ldisc_hangup()`, `tty_ldisc_setup()`, `tty_ldisc_release()`, `tty_ldisc_init()`, and `tty_ldisc_deinit()`. `tty_ldiscs_seq_ops` exposes registered disciplines for proc-style listing. Key internal helpers are `get_ldops()`, `put_ldops()`, `tty_ldisc_get()`, `tty_ldisc_put()`, ldisc semaphore locking helpers, `tty_set_termios_ldisc()`, `tty_ldisc_open()`, `tty_ldisc_close()`, `tty_ldisc_restore()`, `tty_ldisc_kill()`, and `tty_reset_termios()`.

Control flow: registration stores `tty_ldisc_ops` by discipline number under `tty_ldiscs_lock`. Lookup validates the range, tries to module-get registered ops, optionally autoloads `tty-ldisc-%d`, allocates a `struct tty_ldisc`, and binds it to the tty. Normal users of a tty take a read reference on `tty->ldisc_sem`; changing or releasing the ldisc takes the write side after marking `TTY_LDISC_CHANGING` and waking readers/writers. `tty_set_ldisc()` gets the new discipline, locks the tty and ldisc semaphore, rejects no-op and hung-up cases, asks the driver through `ldisc_ok`, closes the old ldisc, installs and opens the new one, restores old/N_TTY/N_NULL on open failure, notifies the driver via `set_ldisc`, restarts flip-buffer work, and drops the old extra reference.

State and persistence: the dispatch table `tty_ldiscs[]` is global. Per-tty state includes `tty->ldisc`, `tty->termios.c_line`, `tty->disc_data`, `tty->receive_room`, and flags `TTY_LDISC_OPEN`, `TTY_LDISC_CHANGING`, and `TTY_LDISC_HALTED`. Module refs on ldisc owners are held while a discipline object exists. Hangup may either reinitialize the current configured discipline, fall back to N_TTY/N_NULL, or kill the ldisc entirely.

Dependencies and integration points: it depends on the custom ldsem implementation in `tty_ldsem.c`, module autoloading, `tty_buffer_*` helpers, driver callbacks (`ldisc_ok`, `set_ldisc`), line discipline operations (`open`, `close`, `hangup`, `flush_buffer`, `write_wakeup`), termios helpers, and tty locks from `tty_mutex.c`. Read/write/poll/ioctl paths in `tty_io.c` depend on the ref APIs; `TIOCSETD` in `tty_io.c` calls `tty_set_ldisc()`.

Risks: line-discipline replacement is race-prone. Failing to hold the write side while closing/opening can allow callbacks into freed ldisc state. Error recovery must never leave `tty->ldisc` NULL on an active tty except intentional hangup/release paths. Autoload policy is security-sensitive because unprivileged callers may request modules only if enabled. Pty pairs require pair locking to avoid destroying one side while the other is active. Lockdep subclasses are necessary for nested pty ldisc locks.

Test signals: register/unregister valid and invalid ldisc numbers, autoload enabled/disabled with privilege variations, repeated no-op `TIOCSETD`, ldisc open failure and fallback to old/N_TTY/N_NULL, concurrent read/write/poll during ldisc change, hangup with and without reinit, pty-pair release ordering, driver `ldisc_ok` rejection, driver `set_ldisc` notification, proc ldisc listing, and lockdep under simultaneous pty master/slave teardown.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/tty/tty_ldisc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/tty/tty_ldsem.c -->
# sources/distributed-fs/ceph-client/drivers/tty/tty_ldsem.c

Purpose: `tty_ldsem.c` implements `struct ld_semaphore`, a TTY-specific reader/writer semaphore used for line-discipline lifetime synchronization. It behaves like an rwsem with timeout support, writer priority, no downgrade operation, and lockdep integration.

Important APIs and types: `struct ldsem_waiter` stores wait-list entries and task pointers. Public functions are `__init_ldsem()`, `ldsem_down_read()`, `ldsem_down_read_trylock()`, `ldsem_down_write()`, `ldsem_up_read()`, `ldsem_up_write()`, plus debug builds of `ldsem_down_read_nested()` and `ldsem_down_write_nested()`. Internal helpers include `__ldsem_wake_readers()`, `writer_trylock()`, `__ldsem_wake_writer()`, `__ldsem_wake()`, `ldsem_wake()`, `down_read_failed()`, `down_write_failed()`, and nested lock acquisition helpers.

Control flow: the semaphore count packs active owners in the low bits and waiters in the high bits. Fast-path read increments by `LDSEM_READ_BIAS` and succeeds while the count stays non-negative; otherwise it reverses the attempt, queues on `read_wait`, increments `wait_readers`, and sleeps until a wake grants ownership or a timeout removes the waiter. Fast-path write adds `LDSEM_WRITE_BIAS` and succeeds only when the active count becomes one; otherwise it queues on `write_wait` and repeatedly sleeps, then attempts write-lock stealing with `writer_trylock()`. Unlock subtracts the relevant bias and wakes a writer first, otherwise all queued readers.

State and persistence: state is entirely in each semaphore instance: `atomic_long_t count`, `wait_readers`, `wait_lock`, `read_wait`, `write_wait`, and optional lockdep map. There is no persistent storage beyond the in-memory tty object that owns the semaphore.

Dependencies and integration points: `tty_ldisc.c` initializes `tty->ldisc_sem` and uses this implementation for `tty_ldisc_ref*`, ldisc changes, hangup, and release. The code depends on atomic operations, raw spinlocks, task wakeups, scheduler timeouts, and lockdep rwsem annotations. It intentionally uses uninterruptible waits because ldisc transition callers rely on deterministic timeout semantics rather than signal interruption.

Risks: count arithmetic has no overflow checking, so bias constants and active/waiter transitions must remain correct for supported architectures. Timeout cleanup is subtle because a waiter may be granted ownership while timing out. Writer priority can starve readers if writers continually arrive, but that is intended to make ldisc changes complete. Wakeups use task pointers with release/acquire ordering; mistakes can wake freed tasks or leak task refs. Debug lockdep annotations must match real ownership.

Test signals: stress concurrent readers and writers, read trylock under free and contended states, write timeouts, read timeouts racing with grants, writer-first wake policy, reader wake batches, nested lockdep acquisition for pty pairs, unlock wakeups when active count reaches zero, and ldisc-change workloads under lockdep and scheduler debugging.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/tty/tty_ldsem.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/tty/tty_mutex.c -->
# sources/distributed-fs/ceph-client/drivers/tty/tty_mutex.c

Purpose: `tty_mutex.c` is small legacy glue around per-tty `legacy_mutex` locking. It provides the old "big tty mutex" API expected by TTY core and drivers while coupling lock ownership with tty krefs so a locked tty cannot be freed.

Important APIs: exported `tty_lock()` and `tty_unlock()` acquire/release `tty->legacy_mutex` while taking/dropping a tty kref. `tty_lock_interruptible()` does the same with interruptible acquisition and rolls back the kref on failure. `tty_lock_slave()` and `tty_unlock_slave()` lock a pty slave peer only when it exists and is not the same object as the current tty. `tty_set_lock_subclass()` marks the legacy mutex with `TTY_LOCK_SLAVE` for lockdep when nested slave locking is needed.

Control flow: callers take a kref before locking, then drop it after unlock. The interruptible variant handles `mutex_lock_interruptible()` failure by immediately putting the reference. Pty master close paths use slave helpers to maintain a stable lock order around both ends.

State and persistence: no independent state is introduced. The code operates on `tty->legacy_mutex` and `tty->kref`. Lockdep subclass state persists in the mutex debug map.

Dependencies and integration points: used heavily by `tty_io.c`, `tty_jobctrl.c`, `tty_ldisc.c`, and drivers that still rely on legacy tty locking. It depends on `tty_kref_get()`/`tty_kref_put()` from the core and lockdep subclasses declared in TTY headers.

Risks: forgetting that `tty_lock()` changes references can leak or prematurely drop ttys if paired incorrectly. Incorrect pty nested locking can deadlock master/slave operations. Interruptible callers must translate errors consistently, as `tty_open_by_driver()` does for `-EINTR` to `-ERESTARTSYS`.

Test signals: lock/unlock kref accounting, interruptible lock failure under signal, pty master/slave close lock ordering under lockdep, and nested subclass annotations for slave locks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/tty/tty_mutex.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/tty/tty_port.c -->
# sources/distributed-fs/ceph-client/drivers/tty/tty_port.c

Purpose: `tty_port.c` provides the generic `struct tty_port` helper layer used by TTY drivers for port lifetime, device registration, flip-buffer delivery, open/close sequencing, carrier handling, DTR/RTS management, hangup, transmit-buffer allocation, and optional serdev registration.

Important APIs: exported functions include `tty_port_init()`, `tty_port_link_wq()`, `tty_port_link_device()`, `tty_port_register_device*()`, `tty_port_register_device_attr_serdev()`, `tty_port_unregister_device()`, `tty_port_alloc_xmit_buf()`, `tty_port_free_xmit_buf()`, `tty_port_destroy()`, `tty_port_put()`, `tty_port_tty_get()`, `tty_port_tty_set()`, `tty_port_hangup()`, `__tty_port_tty_hangup()`, `tty_port_tty_wakeup()`, `tty_port_carrier_raised()`, `tty_port_raise_dtr_rts()`, `tty_port_lower_dtr_rts()`, `tty_port_block_til_ready()`, `tty_port_close_start()`, `tty_port_close_end()`, `tty_port_close()`, `tty_port_install()`, and `tty_port_open()`. Default client operations route received flip data and write wakeups to the active ldisc/tty.

Control flow: drivers initialize a port, link it to a `tty_driver` index or register a tty/serdev device, and use `tty_port_install()`/`tty_port_open()`/`tty_port_close()` as generic tty ops. Open increments `port->count`, associates the tty reference, serializes activation under `port->mutex`, clears `TTY_IO_ERROR`, calls optional `activate`, marks initialized, then calls `tty_port_block_til_ready()` to handle nonblocking behavior, DTR/RTS, CLOCAL, carrier-detect waits, signals, and hangups. Close decrements port count, waits for output and drain delay on last close, flushes ldisc state, calls shutdown, sets `TTY_IO_ERROR` for non-console ports, wakes blocked openers after `close_delay`, and drops the tty association.

State and persistence: `tty_port` tracks open counts, blocked openers, initialized/active/kopened flags, close and drain delays, closing waits, flip buffers, optional xmit page and kfifo, port mutexes/spinlocks, wait queues, `tty` kref, raw `itty` pointer used by flip delivery, and driver operations. The port object may be direct driver storage or refcounted via `kref`; destructor frees buffers and calls `ops->destruct` or `kfree()`.

Dependencies and integration points: integrates with `tty_io.c` driver install/open/close paths, `tty_buffer` flip-buffer work, line discipline receive/lookahead callbacks, serial modem semantics, serdev core, device registration helpers, and low-level `tty_port_operations` callbacks (`activate`, `shutdown`, `carrier_raised`, `dtr_rts`, `destruct`). Drivers such as `ttynull.c` and `vcc.c` use these helpers directly.

Risks: `port->tty` refcounted pointer and `port->itty` raw pointer have different lifetime rules; confusing them can cause stale receive delivery. Blocking open deliberately drops and reacquires the tty lock, so callers must tolerate changed state. Open and close counts can diverge from `tty->count`; the code warns and repairs some cases. Shutdown must not run for console ports. Serdev-vs-tty registration must unregister through the matching path. DTR/RTS and carrier behavior is driver-specific and easy to regress for modem-like devices.

Test signals: generic driver open/close with first and repeated opens, blocking carrier wait, nonblocking open, signal interruption, hangup during blocked open, CLOCAL bypass, DTR/RTS raise/lower, last-close output drain and flush, close delay waking blocked openers, console port close behavior, serdev parent with and without clients, xmit buffer allocation/free, refcounted destructor, and flip-buffer receive/lookahead/wakeup delivery to an active ldisc.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/tty/tty_port.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/tty/ttynull.c -->
# sources/distributed-fs/ceph-client/drivers/tty/ttynull.c

Purpose: `ttynull.c` implements a null TTY and console endpoint named `ttynull`. It accepts writes and discards them while presenting a real TTY driver and console device, useful as a sink when a console must exist but output should go nowhere.

Important APIs and functions: the tty operations are `ttynull_open()`, `ttynull_close()`, `ttynull_hangup()`, `ttynull_write()`, and `ttynull_write_room()`. Console integration uses `ttynull_device()` and `ttynull_console`. Module lifecycle is `ttynull_init()` and `ttynull_exit()`.

Control flow: init allocates a one-line tty driver with reset termios, raw mode, and unnumbered node flags. It initializes a global `tty_port`, assigns port ops, sets driver names and console type, customizes output flags, installs tty ops, links the port to driver index zero, registers the driver, stores the global driver pointer, and registers the console. Open/close/hangup delegate entirely to generic tty-port helpers. Writes return `count` without touching the buffer; write room reports a large constant.

State and persistence: global state is `ttynull_driver` and `ttynull_port`. There is no data buffer, no persisted terminal content, and no hardware state. Termios resets on open because of `TTY_DRIVER_RESET_TERMIOS`.

Dependencies and integration points: depends on the TTY core driver registration, `tty_port` helper layer, and console registration. The console's `.device` callback returns the singleton driver and index zero.

Risks: because writes always succeed, callers cannot detect discarded data. The large write-room value must remain consistent with the "accept everything" behavior. Init failure must release both driver and port. Exit ordering unregisters the console before removing the driver so console callbacks do not use freed driver state.

Test signals: module load/unload, `/dev/ttynull` open/close/hangup, writes of varied sizes returning full count, poll/write-room behavior through the core, console registration visibility, repeated unload after active handles close, and init failure injection around driver registration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/tty/ttynull.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/tty/vcc.c -->
# sources/distributed-fs/ceph-client/drivers/tty/vcc.c

Purpose: `vcc.c` is the Sun4v Logical Domains virtual console concentrator driver. It registers a dynamic TTY driver named `vcc`, probes VIO `vcc-port` devices, builds LDC channels to guest domains, and exposes each domain console as a TTY endpoint in the control domain.

Important APIs and types: `struct vcc_port` embeds `struct vio_driver_state`, a lock, domain name, open tty pointer, table index, refcount/exclusive-removal state, removal flag, buffered VIO packet, byte count, and rx/tx timers. Major helpers include `vcc_table_add/remove()`, `vcc_get()/vcc_put()/vcc_get_ne()`, `vcc_ldc_read()`, `vcc_rx_timer()`, `vcc_tx_timer()`, `vcc_event()`, `vcc_probe()`, `vcc_remove()`, tty ops `vcc_open()`, `vcc_close()`, `vcc_hangup()`, `vcc_write()`, `vcc_write_room()`, `vcc_chars_in_buffer()`, `vcc_break_ctl()`, `vcc_install()`, `vcc_cleanup()`, and module init/exit through `vcc_init()`/`vcc_exit()`.

Control flow: module init registers the TTY driver, then the VIO driver. Probe allocates a `vcc_port`, initializes VIO state and LDC channel, reserves a minor in `vcc_table`, registers a dynamic tty device, reads the domain name from machine description, creates sysfs `domain` and `break` attributes, initializes timers, stores driver data, and brings the VIO port up with rx IRQs temporarily disabled. LDC data-ready events read packets under `port->lock`; data packets are inserted into the tty flip buffer if there is room, otherwise rx IRQs are disabled and a timer retries. Writes copy bytes into the port's VIO packet buffer, attempt `ldc_write()`, report bytes accepted once buffered, and schedule a tx timer if the hypervisor cannot accept data immediately. Remove cancels timers, synchronously hangs up an open tty, obtains an exclusive port reference, unregisters the tty device, tears down LDC/sysfs/device data, and either frees immediately or marks removed for `vcc_cleanup()`.

State and persistence: per-port state is memory-only and tied to VIO device lifetime. `chars_in_buffer` tracks bytes accepted by the tty layer but not yet confirmed written to LDC, satisfying the write-room contract. `port->tty` is populated only while installed/open enough for callbacks; `removed` coordinates device removal with later tty cleanup. Global `vcc_table` maps tty indices to ports and implements a custom ref/exclusive lock protocol.

Dependencies and integration points: integrates with SPARC VIO/LDC APIs, machine-description properties, TTY core dynamic devices, `tty_port` open/close/hangup helpers, flip buffers, sysfs device attributes, timers, IRQ control, and module parameters controlling debug output. VIO control packets are used for break and hangup notifications.

Risks: the custom reference scheme uses busy `udelay()` loops and must balance exclusive and nonexclusive puts exactly. Removal races with open, write, timers, IRQ events, and cleanup are high risk. `port->tty` is a raw pointer, so timer/event paths must hold suitable port references and locks. `chars_in_buffer` covers only one packet buffer; write-room and retry behavior must not accept more bytes than can be retained. Sysfs `break` parsing uses `sscanf(buf, "%ud", &brk)` and accepts only value 1; any change affects admin ABI. IRQ disable/re-enable around rx backpressure must avoid lost events.

Test signals: VIO probe/remove success and each failure unwind, dynamic minor exhaustion, domain sysfs output, sysfs break and `TIOCSBRK`/`TCSBRK` sending control packets, single-open `-EBUSY`, write-room and chars-in-buffer accounting when `ldc_write()` fails then timer succeeds, rx backpressure disabling IRQ and timer retry, unknown packet type reset, hangup sending VCC_CTL_HUP, remove while tty is open and while timers are pending, and module unload after active ports.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/tty/vcc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/tty/vt/Makefile -->
# sources/distributed-fs/ceph-client/drivers/tty/vt/Makefile

Purpose: this Makefile defines the virtual-terminal build composition and generated-table rules. It builds VT core objects, console translation objects, and the host-side generator used to create the default console font Unicode table.

Important targets and variables: `FONTMAPFILE = cp437.uni`; `obj-$(CONFIG_VT)` includes `vt_ioctl.o`, `vc_screen.o`, `selection.o`, `keyboard.o`, `vt.o`, and `defkeymap.o`; `obj-$(CONFIG_CONSOLE_TRANSLATIONS)` includes `consolemap.o`, `consolemap_deftbl.o`, and `ucs.o`. `clean-files` removes generated C and UCS header tables. `hostprogs += conmakehash` builds the host utility. `cmd_conmk` invokes `$(obj)/conmakehash $< > $@` to generate `consolemap_deftbl.c`.

Control flow: when console translations are enabled, `consolemap_deftbl.c` depends on `cp437.uni` and the host `conmakehash` binary. Optional `GENERATE_KEYMAP` lets maintainers regenerate `defkeymap.c` from a map file via `loadkeys`. Optional `GENERATE_UCS_TABLES` regenerates width, recomposition, and fallback UCS headers with Python scripts, with value `2` passing `--full` to the recomposition generator. Normally shipped generated files are used instead.

State and persistence: generated files live under the object directory and are listed in `clean-files`. The Makefile itself encodes the default font map and build-time policy for generated versus shipped artifacts.

Dependencies and integration points: integrates with Kbuild object selection, host program compilation, `loadkeys`, `PYTHON3`, `conmakehash.c`, `consolemap.c`, `ucs.c`, and the VT Kconfig options `CONFIG_VT` and `CONFIG_CONSOLE_TRANSLATIONS`.

Risks: generated files must match shipped sources and runtime expectations. Requiring `loadkeys`, Python modules, or Unicode data during normal builds would break reproducibility, so regeneration remains opt-in. Wrong dependencies can leave stale UCS or consolemap tables. `FONTMAPFILE` changes alter the default hardware font mapping consumed by `consolemap.c`.

Test signals: clean and incremental Kbuild with VT enabled/disabled, console translations enabled/disabled, host `conmakehash` invocation, optional generated keymap and UCS table paths, `make clean` removing generated outputs, and reproducibility checks comparing regenerated shipped tables.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/tty/vt/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/tty/vt/conmakehash.c -->
# sources/distributed-fs/ceph-client/drivers/tty/vt/conmakehash.c

Purpose: `conmakehash.c` is a host-build utility that parses a console Unicode font mapping file such as `cp437.uni` and emits C arrays used by the kernel to initialize the default font-to-Unicode map.

Important APIs and data: it defines `MAX_FONTLEN` as 256, `typedef unsigned short unicode`, global `unitable[MAX_FONTLEN][255]`, and `unicount[MAX_FONTLEN]`. Helpers are `usage()`, `getunicode()`, `addpair()`, and `main()`.

Control flow: `main()` opens the input file or stdin, assumes a 256-glyph font, clears per-glyph counts, then parses each nonblank, noncomment line. Accepted syntax maps one glyph to a list of `U+hhhh` values, a glyph range to `idem`, or a glyph range to an equal-length Unicode range. `getunicode()` recognizes exactly four hex digits after `U+`. `addpair()` ignores values above `0xfffe`, deduplicates per glyph, enforces at most 255 Unicode values per glyph, and records the mapping. After EOF, it counts total Unicode entries and prints a generated C file containing `u8 dfont_unicount[256]` and packed `u16 dfont_unitable[n]`.

State and persistence: all state is process-local global arrays. Output is written to stdout and redirected by Kbuild to `consolemap_deftbl.c`; no files are modified directly by the program.

Dependencies and integration points: built as a Kbuild host program by `drivers/tty/vt/Makefile`. Its generated arrays are referenced by `consolemap.c` as `dfont_unicount[]` and `dfont_unitable[]`, then loaded by `con_set_default_unimap()`.

Risks: the parser only accepts four-digit Unicode values, so supplementary-plane mappings are ignored or rejected. Fixed 256-font assumptions must match console font expectations. A malformed range or too many mappings exits with sysexits codes, breaking the build. Duplicate filtering is per glyph only. Lines longer than 64 KiB are truncated with a warning, which could silently produce incomplete generated data.

Test signals: parse single glyph mappings, duplicate entries, `idem` ranges, Unicode ranges with matching and mismatched lengths, glyph range bounds, values above `0xfffe`, trailing junk warnings, stdin input, too many mappings for one glyph, and regenerated output matching shipped `consolemap_deftbl.c`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/tty/vt/conmakehash.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/tty/vt/consolemap.c -->
# sources/distributed-fs/ceph-client/drivers/tty/vt/consolemap.c

Purpose: `consolemap.c` maps console character sets and Unicode code points to loaded font glyph positions, supports user-loadable translation maps and Unicode maps, provides inverse translation for selection/copy-paste, and initializes the default virtual-console font map.

Important APIs, types, and data: static `translations` holds LAT1, VT100 graphics, IBM PC codepage 437, and user maps. `struct uni_pagedict` is a 32x32x64 sparse Unicode-to-glyph paged dictionary with refcount, checksum, inverse translation caches, and inverse Unicode map. Externally used functions include `set_translate()`, `inverse_translate()`, `con_set_trans_old/new()`, `con_get_trans_old/new()`, `con_free_unimap()`, `con_clear_unimap()`, `con_set_unimap()`, `con_set_default_unimap()`, `con_copy_unimap()`, `con_get_unimap()`, `conv_8bit_to_uni()`, `conv_uni_to_8bit()`, `conv_uni_to_pc()`, and `console_map_init()`.

Control flow: `set_translate()` records the active inverse map for a VC and returns a translation table. User translation ioctls copy data outside `console_lock`, then update `translations[USER_MAP]` and rebuild inverse maps. Unicode maps are sparse: `con_insert_unipair()` allocates directory and row tables on demand and records glyphs by decomposing the 16-bit Unicode value. `con_set_unimap()` duplicates user pairs, unshares a shared dictionary if necessary, inserts pairs, tries to unify with identical maps on other consoles by checksum and memcmp, then rebuilds inverse caches. `con_set_default_unimap()` builds a default dictionary from generated `dfont_unicount`/`dfont_unitable` arrays or reuses cached `dflt`. `conv_uni_to_pc()` handles control characters, direct-to-font private-use mappings, missing dictionaries, and glyph lookup failures with distinct negative codes.

State and persistence: runtime state includes global translation tables, per-console active inverse translation mode, global default dictionary `dflt`, and per-VC `uni_pagedict_loc` pointers. Dictionaries are refcounted and shared across consoles when identical. User changes persist for the lifetime of the console state until cleared, reset, copied, or replaced.

Dependencies and integration points: depends on VT console structures (`vc_cons`, `vc_data`, `fg_console`), `console_lock`, generated default font arrays from `conmakehash`, consolemap ioctl structures, selection/inverse translation users, and the keyboard conversion helpers. The file deliberately copies user memory outside `console_lock` to avoid mmap-lock to console-lock circular dependencies from page faults.

Risks: mapping behavior is user ABI and display correctness. Sparse dictionary refcounts must be exact when sharing, unsharing, defaulting, and freeing. Inverse translation is best-effort and not one-to-one, so selection output can differ from original input. User-memory access while holding console locks is explicitly avoided; regressions can reintroduce lock inversions. The implementation supports only 16-bit Unicode in `conv_uni_to_pc()`. Checksum collisions are guarded by full compare, but the compare logic must traverse sparse rows correctly.

Test signals: default map initialization, user translation old/new set/get, unimap clear/set/get/copy/default reset, map sharing and unsharing across consoles, inverse translation with Unicode and legacy maps, direct font mappings in `0xf000` range, missing glyph return codes, 512-glyph limits, copy-to/from-user fault injection, lockdep around console_lock and user faults, and selection/copy-paste of non-ASCII console text.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/tty/vt/consolemap.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/tty/vt/gen_ucs_fallback_table.py -->
# sources/distributed-fs/ceph-client/drivers/tty/vt/gen_ucs_fallback_table.py

Purpose: `gen_ucs_fallback_table.py` is a Python host generator for `ucs_fallback_table.h`. It uses Python `unicodedata` and the external `unidecode` package, plus many manual overrides, to build a compact C table mapping Unicode BMP characters to single-character fallback glyphs for terminal display when exact glyphs are unavailable.

Important functions and data: constants include `DEFAULT_OUT_FILE = "ucs_fallback_table.h"` and `RANGE_MARKER = 0x00`. The script records `unidecode_version` for generated-file provenance. Major functions are `generate_fallback_map()`, `get_special_overrides()`, `organize_by_pages()`, `compress_ranges()`, `generate_header()`, and `main()` using `argparse`.

Control flow: generation iterates BMP code points from `0x0080` through `0xffff`, skips unnamed/control characters, calls `unidecode()`, and stores mappings only when transliteration is exactly one character. Manual overrides replace or add mappings for ligatures, comparison operators, arrows, currency signs, symbols, punctuation, negated math, dashes, check/cross marks, stars, quadrant blocks, and exclusions. Full-width printable ASCII and selected line-separator behavior are assigned zero so later organization filters them out because runtime code handles or ignores them separately. Entries are grouped by high-byte page, sorted, and compressed when three or more consecutive offsets share the same fallback. The generated header emits page descriptors and page entries using range markers.

State and persistence: the script has no runtime kernel state. Its output is a deterministic generated C header when run with the same Python, Unicode database, `unidecode` version, and source overrides. `-o` selects the output file; otherwise it writes `ucs_fallback_table.h`.

Dependencies and integration points: opt-in regeneration is wired from `drivers/tty/vt/Makefile` when `GENERATE_UCS_TABLES` is set. The generated header is consumed by `ucs.c`, and runtime lookup is expected to handle full-width ASCII programmatically. The script depends on Python 3, `unicodedata`, `unidecode`, `argparse`, `collections.defaultdict`, and `pathlib`.

Risks: output can change when Python Unicode data or `unidecode` changes, so generated files may not be reproducible across environments without version control. Manual override choices are semantic and UI-visible. Restricting to single-character fallbacks means many transliterations are intentionally excluded. `RANGE_MARKER` must not conflict with valid fallback entry encoding. Compression/decompression must match `ucs.c` lookup expectations exactly.

Test signals: run the generator with and without `-o`, verify generated C syntax, compare regenerated shipped header under the expected dependency versions, spot-check overrides for ligatures, arrows, currency, negated operators, full-width ASCII exclusions, range compression for repeated fallbacks, empty/unassigned character filtering, and runtime `ucs_get_fallback()` lookup against generated ranges and individual entries.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/tty/vt/gen_ucs_fallback_table.py -->
