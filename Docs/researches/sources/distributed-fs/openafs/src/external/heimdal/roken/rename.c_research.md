# sources/distributed-fs/openafs/src/external/heimdal/roken/rename.c

## Purpose
Implements `rk_rename` for platforms whose native `rename` does not unlink an existing destination before replacing it.

## Important APIs, Types, And Functions
The exported function is `rk_rename(const char *oldname, const char *newname)`. `roken.h.in` uses it when `RENAME_DOES_NOT_UNLINK` is configured; otherwise `rk_rename` is a macro to native `rename`.

## Control Flow
The function first calls `rename(oldname, newname)`. If it fails with `EEXIST` or `EACCES`, it tries `unlink(newname)` and then retries `rename` only if the unlink succeeds. It returns the final status code.

## State And Persistence
This function mutates filesystem namespace state. It may delete the destination path before the second rename attempt.

## Dependencies And Integration Points
It depends on POSIX-style `rename`, `unlink`, and `errno`, wrapped through roken portability headers. It is used by callers that want Unix replacement semantics across platforms.

## Risks And Test Signals
The unlink-plus-rename sequence is not atomic and can race with other processes; it can also delete the destination and fail to install the source. Tests should cover replacement of regular files, permission errors, missing source, same-file behavior, and platform configurations where native rename already replaces targets.
