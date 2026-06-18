# sources/distributed-fs/openafs/src/external/heimdal/roken/cloexec.c

Purpose: provides helpers to mark file descriptors, `FILE *`, and directory streams close-on-exec.

Important APIs/types/functions: `rk_cloexec(int fd)`, `rk_cloexec_file(FILE *f)`, and `rk_cloexec_dir(DIR *d)`.

Control flow: on platforms with `fcntl`, `rk_cloexec()` reads existing descriptor flags with `F_GETFD` and writes them back with `FD_CLOEXEC` set. File and directory helpers convert to descriptors with `fileno()` and `dirfd()` where available.

State and persistence behavior: mutates kernel descriptor flags for the current process. No heap or global state.

Dependencies and integration points: used by RNG seed-file code and other roken callers that open descriptors before possible exec. Depends on `roken.h`, `fcntl`, and non-Windows directory APIs.

Risks: failures are silently ignored, so callers cannot distinguish unsupported platforms or bad descriptors. On platforms lacking `fcntl`, helpers are no-ops. Race-free close-on-exec still requires using `O_CLOEXEC` at open when possible.

Test signals: descriptor flag inspection after calls, invalid descriptor no-crash behavior, and platform builds without `HAVE_FCNTL`.
