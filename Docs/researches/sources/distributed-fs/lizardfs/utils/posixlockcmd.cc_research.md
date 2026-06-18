# sources/distributed-fs/lizardfs/utils/posixlockcmd.cc

Purpose: interactive helper for testing POSIX byte-range `fcntl()` locks.

Important APIs/functions: maps `r` to `F_RDLCK` and `w` to `F_WRLCK`; initializes a global `struct flock` with `SEEK_SET`. Signal handlers unlock (`SIGUSR1`), report interruption (`SIGUSR2`), or close (`SIGINT`). Optional start and length arguments set `l_start` and `l_len`.

Control flow: validates `path [r/w/u]` shape, opens the file read/write, fills lock metadata, calls blocking `fcntl(fd, F_SETLKW, &lock)`, prints state, and pauses for signal-driven orchestration.

State and persistence: no file data persistence; it holds a POSIX advisory lock over the requested byte range until unlock/close/exit. Global variables carry fd/path/lock state.

Dependencies/integration: complements `flockcmd.cc` for tests that need POSIX record-lock semantics rather than BSD whole-file locks.

Risks and test signals: usage mentions `u` but command validation only accepts `r`/`w`, and invalid command handling does not immediately exit. Signal handlers use non-async-signal-safe operations. Test signals are shared/exclusive record lock interactions, byte-range overlap/non-overlap, unlock signal behavior, and lock visibility across clients.
