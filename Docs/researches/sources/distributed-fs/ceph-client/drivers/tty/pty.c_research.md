# sources/distributed-fs/ceph-client/drivers/tty/pty.c

## Purpose
Implements Linux pseudoterminal support for both legacy BSD PTYs and Unix98 `/dev/ptmx`/`devpts` PTYs. It creates paired `tty_struct` objects, wires master/slave data paths through flip buffers, exposes PTY ioctls, manages packet mode and window-size signaling, and registers the `ptm`/`pts` tty drivers plus the `/dev/ptmx` character device.

## Important APIs, types, and functions
- Global Unix98 state: `ptm_driver`, `pts_driver`, `devpts_mutex`, and `ptmx_cdev`.
- Common tty operations: `pty_open()`, `pty_close()`, `pty_write()`, `pty_write_room()`, `pty_flush_buffer()`, `pty_unthrottle()`, `pty_resize()`, `pty_set_termios()`, `pty_start()`, and `pty_stop()`.
- Pair allocation and lifetime: `pty_common_install()` allocates both tty ports and the peer tty, links them via `tty->link`, sets buffer limits, and bumps driver refs; `pty_cleanup()` releases the tty port.
- Ioctls: `pty_set_lock()`, `pty_get_lock()`, `pty_set_pktmode()`, `pty_get_pktmode()`, and `pty_signal()` back `TIOCSPTLCK`, `TIOCGPTLCK`, `TIOCPKT`, `TIOCGPKT`, `TIOCGPTN`, and `TIOCSIG`.
- Legacy path: `legacy_pty_init()`, `pty_install()`, `pty_remove()`, `master_pty_ops_bsd`, and `slave_pty_ops_bsd`.
- Unix98 path: `ptmx_open()`, `ptm_open_peer()`, `ptm_open_peer_file()`, `ptm_unix98_lookup()`, `pts_unix98_lookup()`, `pty_unix98_install()`, `pty_unix98_remove()`, `ptm_unix98_ops`, `pty_unix98_ops`, and `unix98_pty_init()`.

## Control flow
Initialization runs from `device_initcall(pty_init)`, first registering legacy PTYs when enabled, then Unix98 drivers and `/dev/ptmx`. Opening `/dev/ptmx` allocates a tty file, acquires a devpts instance, reserves an index, initializes the master tty under `tty_mutex`, locks the slave with `TTY_PTY_LOCK`, creates the devpts slave dentry, and opens the master. Slave lookup is deliberately devpts-mediated: `pts_unix98_lookup()` returns the master-private tty only when the master exists.

I/O is a direct paired-tty path. `pty_write()` inserts bytes into the peer port's flip buffer and pushes it. `pty_write_room()` reports the peer buffer's available space. The unthrottle path wakes writers on the peer and intentionally keeps `TTY_THROTTLED` set so line disciplines keep issuing unthrottle notifications. Packet mode state changes are latched in `tty->ctrl.pktstatus` and wake the master read side on flow-control, ioctl, stop/start, or flush events.

Close marks I/O error, wakes local wait queues, clears packet mode, marks the peer as closed, and for a master close kills the devpts node and vhangups the slave. Last-close removal releases devpts index and fs info for Unix98 PTYs.

## State and persistence behavior
State lives in tty flags (`TTY_IO_ERROR`, `TTY_OTHER_CLOSED`, `TTY_PTY_LOCK`, `TTY_THROTTLED`), `tty->ctrl.packet`/`pktstatus`, paired `tty_port` buffers, devpts indexes and dentries, tty refcounts, and driver arrays for legacy PTYs. There is no persistent storage beyond kernel device model/devpts state. Window size is mirrored to both ends and foreground process groups receive `SIGWINCH`.

## Dependencies and integration points
This file integrates with the tty core, line disciplines, devpts, VFS file allocation/opening, cdev registration, poll wait queues, signal delivery, compat ioctl handling, and tty console/device class registration. Unix98 behavior depends on `CONFIG_UNIX98_PTYS`; legacy BSD support depends on `CONFIG_LEGACY_PTYS` and `CONFIG_LEGACY_PTY_COUNT`.

## Risks and edge cases
- Pair lifetime depends on tty core locking and refcounts; stale `tty->link` assumptions are guarded in several paths but remain central to correctness.
- Packet mode uses ctrl spinlocks and memory ordering; missed packet status wakeups could break applications that depend on `TIOCPKT`.
- `ptmx_open()` has several staged cleanup paths; devpts index/fs references must stay paired with tty release on every failure.
- Legacy driver arrays are updated manually in `pty_common_install()`/`pty_remove()`.
- Slave open rules reject locked slaves and opens after peer closure; regressions are user-visible in pty allocation/open behavior.

## Test signals
Useful signals include Unix98 pty allocation/open/close tests through `/dev/ptmx` and `/dev/pts/N`, `TIOCSPTLCK`/`TIOCGPTLCK`, `TIOCPKT` status events for stop/start/flush/ioctl, `TIOCSWINSZ`/`SIGWINCH`, `TIOCSIG`, `TIOCGPTN`, `ptm_open_peer()`, namespace/devpts mount coverage, and stress around concurrent close, hangup, and slave open.
