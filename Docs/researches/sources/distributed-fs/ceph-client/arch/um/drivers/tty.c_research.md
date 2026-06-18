<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/um/drivers/tty.c -->
# sources/distributed-fs/ceph-client/arch/um/drivers/tty.c

Purpose: implements the `tty:` channel backend, attaching a UML console/serial line to a named host terminal device.

Important APIs/types/functions: `struct tty_chan` stores the host device path, raw flag, and saved terminal attributes. Backend callbacks are `tty_chan_init()`, `tty_open()`, and `tty_ops`.

Control flow: `tty_chan_init()` requires `:device` syntax and stores a pointer to the parsed device string. `tty_open()` chooses `O_RDONLY`, `O_WRONLY`, or `O_RDWR` from channel direction, opens the host path, optionally saves and sets raw mode, reports the device string, and returns the FD. Reads/writes/window-size use generic helpers.

State and persistence: per-channel backend state stores path and terminal attributes. No persistent data is written.

Dependencies and integration points: depends on host `open`, termios/raw helpers, generic channel operations, and parser string lifetime from `chan_kern.c`.

Risks: the stored path points into the channel config string, so config lifetime must outlive the backend. Error paths after raw-mode setup return without closing FD in some failures. Raw-mode restoration is generic close only, so saved `tt` is not restored here.

Test signals: boot with `tty:/dev/tty...` for input/output/bidirectional modes, invalid paths, raw/non-raw serial config, and terminal window-size queries.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/um/drivers/tty.c -->
