<!-- BEGIN_FILE_RESEARCH: sources/compression/xz/src/common/tuklib_open_stdxxx.c -->
# sources/compression/xz/src/common/tuklib_open_stdxxx.c

Purpose: ensures file descriptors 0, 1, and 2 are open before a command-line tool proceeds.

Important APIs/types/functions: `tuklib_open_stdxxx(int err_status)`, `fcntl(F_GETFD)`, `open("/dev/null")`, `close`, and `exit`.

Control flow: on DOS-like systems do nothing. Else iterate descriptors 0-2; when a descriptor is closed, open `/dev/null` with mode chosen to occupy that exact descriptor, otherwise exit with the supplied status.

State and persistence: mutates process file descriptor table only.

Dependencies and integration: protects later opens from accidentally becoming stdin/stdout/stderr.

Risks: mode selection appears reversed from the comment's intuitive direction (`stdin` gets `O_WRONLY`, outputs get `O_RDONLY`), likely intentionally making accidental wrong-direction I/O fail but worth preserving carefully. If `/dev/null` open returns a different descriptor, it exits silently.

Test signals: run a small tool with closed fd 0/1/2 and verify descriptors are reopened predictably.
<!-- END_FILE_RESEARCH: sources/compression/xz/src/common/tuklib_open_stdxxx.c -->
