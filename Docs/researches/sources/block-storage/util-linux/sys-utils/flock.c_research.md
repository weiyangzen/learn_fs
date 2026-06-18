# File Research: sources/block-storage/util-linux/sys-utils/flock.c

Purpose: Implements the `flock(1)` command-line utility for shell-level file locking. It supports locking a named file/directory while running a command, or operating directly on an already-open file descriptor.

Core behavior:
- Parses shared/exclusive/unlock modes, nonblocking and timed waits, command execution (`-c` via the default shell or argv passthrough), `--close`, `--no-fork`, verbose timing, and custom conflict exit status.
- Uses `flock(2)` by default and can switch to Linux open-file-description locks via `fcntl(F_OFD_SETLK/F_OFD_SETLKW)` for byte ranges selected by `--start` and `--length`.
- Opens path locks with `O_CREAT|O_NOCTTY`, falls back for directories when Linux rejects `O_CREAT` on directories, and opens OFD exclusive locks writable because fcntl write locks require that.
- Implements timeouts through util-linux timer helpers and treats `-w 0` as equivalent to nonblocking mode.
- On NFS-style `flock()` failures (`EIO`/`EBADF`) it attempts a reopen in read-write mode when an exclusive lock on an accessible named file might need fcntl-compatible semantics.

Important implementation details:
- `do_lock()` dispatches between the `flock()` and OFD `fcntl()` APIs, while `flock_to_fcntl_type()` maps lock modes to `F_RDLCK`, `F_WRLCK`, and `F_UNLCK`.
- The parent process keeps the lock while waiting for a forked child; `--close` closes the lock fd only in the child before `execvp()`. `--no-fork` directly replaces the `flock` process and is incompatible with `--close`.
- Exit status mirrors command status where a command is executed, maps signal termination to `128 + signal`, and uses sysexits values for setup errors.

Dependencies and integration:
- Relies on util-linux helpers from `strutils.h`, `timer.h`, `monotonic.h`, `default_shell.h`, `closestream.h`, and NLS wrappers.
- Exposes user-facing behavior documented as `flock(1)`.

Risks and edge cases:
- OFD lock constants are locally defined when libc/kernel headers lack them, so build/runtime kernel support can diverge.
- The lock loop only treats `EACCES`/`EWOULDBLOCK` as normal conflict errors; other errors become data or OS errors.
- Verbose elapsed timing is monotonic and only measures lock acquisition, not child execution.
