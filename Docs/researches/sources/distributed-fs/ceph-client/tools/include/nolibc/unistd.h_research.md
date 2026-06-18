# sources/distributed-fs/ceph-client/tools/include/nolibc/unistd.h

## Purpose
Provides unistd-style constants and small wrappers not housed in the main syscall header.

## APIs, Types, and Functions
Defines standard fd constants `STDIN_FILENO`, `STDOUT_FILENO`, `STDERR_FILENO`, access mode constants `F_OK`, `X_OK`, `W_OK`, `R_OK`, `_sys_faccessat`, `faccessat`, `access`, `msleep`, `sleep`, `usleep`, and `tcsetpgrp`.

## Control Flow, State, and Persistence
`access` delegates to `faccessat`; sleep helpers build `timespec` values and call `nanosleep`, returning remaining seconds for `sleep` semantics; `tcsetpgrp` issues the relevant terminal ioctl. No persistent state is held outside kernel fd/process/session state.

## Dependencies and Integration
Depends on `sys.h`, `time.h`, `fcntl`/AT constants, and ioctl definitions. It integrates with portable code expecting common `<unistd.h>` names under nolibc.

## Risks and Test Signals
Risks are incomplete unistd coverage, sleep interruption rounding, access checks differing from open-time permissions, and terminal ioctl availability. Test signals are access success/failure cases, interrupted and full sleeps, standard fd use, and terminal process-group tests where a tty is available.
