<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/proc/proc_tty.c -->
## sources/distributed-fs/ceph-client/fs/proc/proc_tty.c

Purpose: implements `/proc/tty`, `/proc/tty/drivers`, `/proc/tty/ldiscs`, and per-driver proc hooks under `/proc/tty/driver`.

Important APIs and functions: exports `proc_tty_register_driver`, `proc_tty_unregister_driver`, and `proc_tty_init`. Internals include `show_tty_range`, `show_tty_driver`, `t_start`, `t_next`, `t_stop`, and `tty_drivers_op`.

Control flow: init creates the proc tty directories, ldisc/driver listing files, and a restricted `tty/driver` directory. `/proc/tty/drivers` locks `tty_mutex`, emits pseudo-driver rows once at the head of the global driver list, then emits one or more ranges per registered `tty_driver`. Driver registration creates `tty/driver/<driver_name>` when the driver provides `ops->proc_show`; unregister removes it and clears `driver->proc_entry`.

State and persistence behavior: persistent proc state is limited to `proc_tty_driver` and each `tty_driver->proc_entry`. The driver list and ldisc list are live TTY subsystem state. The driver directory is user-read/search-only due to serial timing information concerns.

Dependencies and integration points: depends on the TTY core's global `tty_drivers` list, `tty_mutex`, driver proc callbacks, tty ldisc seq ops, and procfs create/remove helpers.

Risks: per-driver proc entries must be removed before driver structures disappear. `/proc/tty/driver/serial` style outputs can leak usage timing, hence restricted permissions must remain. Formatting is ABI-like for procps and diagnostics.

Test signals: register/unregister TTY drivers with proc callbacks; read `/proc/tty/drivers` with pseudo drivers, multi-major ranges, PTYs, VT, console, and serial drivers; permission checks on `/proc/tty/driver`; concurrent driver unregister while reading.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/proc/proc_tty.c -->
