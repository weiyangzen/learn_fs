# sources/distributed-fs/ceph-client/tools/testing/selftests/exec/recursion-depth.c

## Purpose
Tests that a shebang script whose interpreter is itself does not recurse indefinitely and fails with `ELOOP`.

## Important APIs, Types, And Functions
Uses `unshare(CLONE_NEWNS)`, `mount` to private root and ramfs on `/tmp`, `creat`, `write`, `execve`, and kselftest helpers.

## Control Flow
The program creates a private mount namespace, mounts ramfs at `/tmp`, writes `/tmp/1` containing `#!/tmp/1`, closes it, then calls `execve("/tmp/1", NULL, NULL)`. It expects return `-1` and `errno == ELOOP`.

## State And Persistence
Creates an isolated mount namespace and a ramfs file at `/tmp/1` inside it. No host filesystem persistence after process exit.

## Dependencies And Integration Points
Requires unprivileged or privileged mount namespace creation and ramfs mount permission. Skips if `unshare` is unavailable or denied with `EPERM`.

## Risks
Requires mount privileges in the namespace. Uses null argv/env intentionally, so it also exercises null argv behavior.

## Test Signals
Single kselftest result passes only when `execve` fails with `ELOOP`.
