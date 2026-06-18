# sources/distributed-fs/ceph-client/drivers/pps/clients/pps-ldisc.c

Purpose: TTY line discipline that exposes serial DCD transitions as PPS assert/clear events.

Important APIs/functions: `pps_tty_init()`, `pps_tty_cleanup()`, `pps_tty_open()`, `pps_tty_close()`, and `pps_tty_dcd_change()`. It inherits N_TTY operations through `n_tty_inherit_ops()`.

Control flow: init clones N_TTY ops, replaces owner, number, name, DCD-change, open, and close callbacks, then registers line discipline `N_PPS`. Open creates PPS source metadata from tty driver name/index, registers a PPS source with both-edge capture, stores the tty pointer in `lookup_cookie`, then opens the underlying N_TTY discipline. DCD changes timestamp immediately, find the PPS device by cookie, and emit assert on active or clear on inactive. Close calls the original N_TTY close, looks up the PPS device, and unregisters it.

State/dependencies: state is per-open PPS device plus global saved N_TTY callbacks. Uses `pps_lookup_dev()` cookie matching instead of tty-owned storage. Depends on TTY line discipline locking, serial DCD notifications, and PPS core.

Risks: comments acknowledge convoluted ldisc locking; lookup failure is only warned; open failure after PPS registration must unregister; close unregisters after base close; cookie lookup is a linear idr scan and must not dereference stale tty cookies.

Test signals: attach `N_PPS` to a serial tty, toggle DCD, verify assert/clear sequences and `/dev/ppsN` path, open error rollback, close cleanup, and module unload after line disciplines detach.
