# sources/distributed-fs/openafs/src/external/heimdal/roken/daemon.c

Purpose: supplies a BSD-style `daemon()` implementation when the platform lacks one.

Important APIs/types/functions: `daemon(int nochdir, int noclose)` is compiled only under `#ifndef HAVE_DAEMON`.

Control flow: forks and exits the parent, calls `setsid()` in the child, optionally changes directory to `/`, and optionally redirects stdin/stdout/stderr to `_PATH_DEVNULL`.

State and persistence behavior: changes process session, working directory, and standard descriptors. No heap state.

Dependencies and integration points: roken portability layer for daemons in Heimdal/OpenAFS components. Depends on fork, setsid, chdir, open, dup2, close, and path constants.

Risks: classic single-fork daemonization leaves some traditional double-fork edge cases unhandled. `chdir()` and `dup2()` failures are not propagated except for fork/setsid. Not compiled where the system daemon exists.

Test signals: child process behavior, parent exit, descriptor redirection, `nochdir`/`noclose` options, and build coverage for fallback-only platforms.
