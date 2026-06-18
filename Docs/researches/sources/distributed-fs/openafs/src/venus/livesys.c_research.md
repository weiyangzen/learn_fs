# sources/distributed-fs/openafs/src/venus/livesys.c

## Purpose
`livesys.c` implements `livesys`, a small utility that prints the first current AFS sysname value, the value normally substituted for `@sys`. It is a simplified read-only counterpart to `fs sysname`.

## Important APIs, Types, And Functions
The only function is `main`. It uses a static `space[AFS_PIOCTL_MAXSIZE]`, writes an input count of zero, and calls `pioctl(0, VIOC_AFS_SYSNAME, &blob, 1)`. It decodes the returned leading `afs_int32` count and prints the first string following that count.

## Control Flow
On startup it applies the AIX full-core signal action when applicable, prepares an in/out `ViceIoctl` using `space`, sets `setp` to zero to request the current sysname list, and invokes `VIOC_AFS_SYSNAME`. If the pioctl fails or returns zero entries, it prints an error and exits 1. Otherwise it prints the first returned sysname and exits 0.

## State And Persistence
The utility is read-only and has no state beyond the static buffer and stack variables. It does not modify the sysname list; persistence remains entirely inside the cache manager's current configuration/runtime state.

## Dependencies And Integration Points
It depends on OpenAFS pioctl headers and cache-manager support for `VIOC_AFS_SYSNAME`. It integrates with the same sysname state surfaced by `fs sysname`, but intentionally ignores additional entries in a sysname list.

## Risks And Test Signals
Risks include printing only the first sysname even when the cache manager returns a list, using `afs_error_message(code)` even though pioctl failures usually communicate via `errno`, and no bounds validation beyond trusting the pioctl buffer. Test signals include matching first output with `fs sysname`, failure on an absent cache manager, and behavior when the sysname list is empty or contains multiple values.
