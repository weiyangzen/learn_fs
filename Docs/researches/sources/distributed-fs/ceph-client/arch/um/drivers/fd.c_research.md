<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/um/drivers/fd.c -->
# sources/distributed-fs/ceph-client/arch/um/drivers/fd.c

Purpose: implements the `fd:` UML channel backend, attaching a console or serial line to an already-open host file descriptor.

Important APIs/types/functions: `struct fd_chan` stores the host FD, raw-mode flag, saved terminal attributes, and printable FD string. Backend callbacks are `fd_init()`, `fd_open()`, and `fd_close()`, exported through `fd_ops`.

Control flow: `fd_init()` requires `:number` syntax and records the descriptor. `fd_open()` optionally switches terminal FDs to raw mode, formats the descriptor for config output, and returns the existing FD. `fd_close()` restores saved terminal attributes if raw mode was enabled on a TTY.

State and persistence: state is backend-private and lives as long as the channel configuration. It does not own the underlying FD lifetime in the normal sense; it merely uses the descriptor supplied by the UML process environment.

Dependencies and integration points: uses generic channel I/O helpers, libc `isatty`, termios, and UML `raw()` helper. `winch=1` lets line code register window-size notifications for TTY descriptors.

Risks: using process-standard FDs means close/restore semantics can affect the host terminal running UML. Invalid FD numbers fail only when used. Raw-mode restoration must be reliable.

Test signals: boot with `con0=fd:0,fd:1`, use raw/non-raw modes, close stdin/stdout externally, resize the terminal, and verify config strings report numeric FDs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/um/drivers/fd.c -->
