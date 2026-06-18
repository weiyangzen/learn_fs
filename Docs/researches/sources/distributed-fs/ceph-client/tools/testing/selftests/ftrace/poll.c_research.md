<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/ftrace/poll.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/ftrace/poll.c

## Purpose
This small helper polls a file for `POLLIN` or `POLLPRI` events and is used by ftrace tests that need deterministic polling of tracefs files.

## Important APIs, Types, And Functions
`main()` parses `-I`, `-P`, and `-t timeout`, opens the target file, optionally drains it before `POLLIN`, calls `poll()`, and maps timeout to exit code `1`.

## Control Flow
The helper defaults to infinite timeout and `POLLIN`. For `POLLIN`, it reads in 4096-byte chunks until a short read to reset readiness, then polls one fd. `EINTR` is treated as a non-timeout return path, while other poll errors fail.

## State And Persistence
It reads but does not otherwise mutate the target file. Draining tracefs files can consume pending data intentionally.

## Dependencies And Integration Points
It depends on POSIX `poll()`, `open()`, `read()`, and tracefs/debugfs file semantics.

## Risks
Returning `0` for interrupted polls may be interpreted as event success by callers. The usage error path returns `-1`, which maps to shell exit 255.

## Test Signals
Exit `0` means event or interrupt, exit `1` means timeout, and exit 255/error output indicates open/poll/argument failure.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/ftrace/poll.c -->
