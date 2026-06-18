# sources/distributed-fs/ceph-client/drivers/tty/tty_mutex.c

Purpose: `tty_mutex.c` is small legacy glue around per-tty `legacy_mutex` locking. It provides the old "big tty mutex" API expected by TTY core and drivers while coupling lock ownership with tty krefs so a locked tty cannot be freed.

Important APIs: exported `tty_lock()` and `tty_unlock()` acquire/release `tty->legacy_mutex` while taking/dropping a tty kref. `tty_lock_interruptible()` does the same with interruptible acquisition and rolls back the kref on failure. `tty_lock_slave()` and `tty_unlock_slave()` lock a pty slave peer only when it exists and is not the same object as the current tty. `tty_set_lock_subclass()` marks the legacy mutex with `TTY_LOCK_SLAVE` for lockdep when nested slave locking is needed.

Control flow: callers take a kref before locking, then drop it after unlock. The interruptible variant handles `mutex_lock_interruptible()` failure by immediately putting the reference. Pty master close paths use slave helpers to maintain a stable lock order around both ends.

State and persistence: no independent state is introduced. The code operates on `tty->legacy_mutex` and `tty->kref`. Lockdep subclass state persists in the mutex debug map.

Dependencies and integration points: used heavily by `tty_io.c`, `tty_jobctrl.c`, `tty_ldisc.c`, and drivers that still rely on legacy tty locking. It depends on `tty_kref_get()`/`tty_kref_put()` from the core and lockdep subclasses declared in TTY headers.

Risks: forgetting that `tty_lock()` changes references can leak or prematurely drop ttys if paired incorrectly. Incorrect pty nested locking can deadlock master/slave operations. Interruptible callers must translate errors consistently, as `tty_open_by_driver()` does for `-EINTR` to `-ERESTARTSYS`.

Test signals: lock/unlock kref accounting, interruptible lock failure under signal, pty master/slave close lock ordering under lockdep, and nested subclass annotations for slave locks.
