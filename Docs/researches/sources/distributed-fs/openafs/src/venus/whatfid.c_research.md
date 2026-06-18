# sources/distributed-fs/openafs/src/venus/whatfid.c

## Purpose
`whatfid.c` implements a small command that prints the cell and AFS FID for one or more pathnames using `VIOCGETFID`. It predates or overlaps with `fs getfid` and provides a simple diagnostic view of cache-manager path-to-FID resolution.

## Important APIs, Types, And Functions
The local `struct VenusFid` contains `Cell` and `struct AFSFid`. `WhatFidCmd` iterates `-path` arguments, calls `pioctl(path, VIOCGETFID, &blob, follow)`, and prints `cell:volume.vnode.unique`. `PioctlError` formats common pioctl error cases. `main` registers the `initcmd` syntax with `-path` and `-link`.

## Control Flow
The command defaults to following symlinks/mount evaluation via pioctl follow flag `1`. If `-link` is present, it sets follow to `0`, despite the parameter description saying "do not follow symlinks". Each path is processed independently; failures print an error and continue. The program returns the command parser's dispatch result, not a per-path error count.

## State And Persistence
The utility is read-only. It stores only the program name pointer and command parameter indexes as process globals. It does not mutate cache-manager state or files.

## Dependencies And Integration Points
It depends on OpenAFS pioctl support, `vioc.h`, AFS FID structures, command parsing, and error translation. It integrates with the local cache manager's path resolution and FID reporting.

## Risks And Test Signals
Risks include no nonzero aggregate error status for failed paths, ambiguous `-link` naming versus follow behavior, local duplication of `struct VenusFid`, and reliance on `errno` in the error printer while passing the unused pioctl return code. Test signals include FID output for files, directories, symlinks with and without `-link`, mount points, non-AFS paths, missing files, and permission-denied paths.
