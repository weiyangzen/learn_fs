<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/um/drivers/chan_user.c -->
# sources/distributed-fs/ceph-client/arch/um/drivers/chan_user.c

Purpose: provides host-user helper routines shared by UML channel backends. It wraps read/write/close/window-size operations and implements SIGWINCH relay support for host TTYs attached to UML consoles.

Important APIs/types/functions: exported helpers are `generic_close()`, `generic_read()`, `generic_write()`, `generic_window_size()`, `generic_free()`, `generic_console_write()`, and `register_winch()`. Internal SIGWINCH support uses `winch_handler()`, `struct winch_data`, `winch_thread()`, and `winch_tramp()`.

Control flow: generic reads return a positive byte count, zero for EAGAIN, `-EIO` on EOF, or `-errno`. Writes retry interrupted short writes and distinguish EAGAIN/EOF/errors. Console writes temporarily enable terminal output processing so newline output behaves as users expect, then restore raw terminal state. `register_winch()` detects host TTYs, either uses existing SKAS winch handling or starts a helper thread with a controlling TTY; that thread waits in `sigsuspend()` for SIGWINCH and writes a byte to a pipe registered as a UML IRQ.

State and persistence: state is per-call except helper thread pipe FDs, helper pid, and stack passed to `line.c` through `register_winch_irq()`. Terminal attributes are saved and restored per backend.

Dependencies and integration points: depends on libc/syscalls, `termios`, `TIOCGWINSZ`, UML helper-thread APIs, signal masking, `os_*` wrappers, and `line.c` WINCH IRQ handling.

Risks: helper threads use host process/session/controlling-terminal semantics and synchronization pipes rather than kernel locks. Terminal state restoration must survive errors. `generic_write()` must handle blocking FDs used by time-travel output without losing short writes.

Test signals: attach consoles to host TTYs, resize terminal windows and watch guest SIGWINCH delivery, test raw-mode restoration on close/errors, verify EAGAIN and EOF mapping, and run console writes to ensure newline handling is correct.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/um/drivers/chan_user.c -->
