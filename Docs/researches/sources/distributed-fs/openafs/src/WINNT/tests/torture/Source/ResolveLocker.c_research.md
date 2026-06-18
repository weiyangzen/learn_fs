# sources/distributed-fs/openafs/src/WINNT/tests/torture/Source/ResolveLocker.c

## Purpose

`ResolveLocker.c` is a Hesiod-backed locker resolver used by the WinTorture tooling when `HAVE_HESOID` is enabled. It converts a logical locker name into an AFS UNC submount or NFS UNC path and updates a `USER_OPTIONS` attach structure for downstream attach/resource-mount code.

## Important APIs, Types, and Functions

- Compiled only under `HAVE_HESOID`; it defines `_WIN32_WINNT 0x0500` and includes `hesiod.h` and `locker.h`.
- `ResolveLocker(USER_OPTIONS *attachOption)` validates `type == "locker"`, gets locker info, parses filesystem type, and fills `SubMount`, `type`, or `FileType`.
- `GetLockerInfo(char *Locker, char *Path)` calls Hesiod and selects an AFS or NFS filsys entry, preferring the lowest AFS weight if present.
- `ResolveHesName(char *locker)` calls `hes_resolve(locker, "filsys")`.

## Control Flow

`ResolveLocker()` only handles input type `locker`. It retrieves a filsys path string; an `AFS` entry becomes `\\afs\<locker>` with forward slashes normalized to backslashes, changes the type to `AFS`, and returns true. An `NFS` entry is accepted only if no submount is already set; it expects five parsed fields, builds `\\<HostName><path>`, normalizes slashes, sets `FileType` to `NFS`, and returns true. Unknown types, missing info, parse failures, or unsupported initial type return false.

`GetLockerInfo()` iterates Hesiod results. For AFS entries it reads a weight field if present and keeps the lowest-weight entry; if no weight is parsed, it copies that AFS entry. For NFS entries it copies the entry directly. `ResolveHesName()` is a thin wrapper around `hes_resolve`.

## State and Persistence

No persistent state is written. The function mutates the caller-provided `USER_OPTIONS` fields. Hesiod result memory ownership is not handled in this file.

## Dependencies and Integration Points

The module depends on MIT Hesiod and locker structures. It is referenced by `WinTorture.c` to resolve and attach lockers when `-l` is used and by `WinThreads.c` through optional locker attach operations.

## Risks and Edge Cases

- Uses `sprintf`, `strcpy`, and fixed-size buffers without bounds checks.
- Hesiod result memory is not freed, which may leak depending on resolver ownership rules.
- AFS resolution ignores the actual AFS path in the Hesiod entry and constructs `\\afs\<locker>`, which may not match weighted path details.
- The NFS `sprintf("\\\\%s%s", HostName, temp)` assumes `temp` already starts with a slash/backslash-like path.
- The file returns `TRUE` after an unreachable comment even though all active branches already returned.

## Test Signals

Tests need Hesiod fixtures for AFS weighted entries, unweighted AFS entries, NFS entries, unknown filesystem entries, and missing lockers. The observable signal is the mutated `USER_OPTIONS` structure and boolean return.
