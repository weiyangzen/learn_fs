# sources/cloud-native/containers-storage/internal/rawfilelock/rawfilelock_unix.go

## Purpose
This Unix-only implementation provides the OS-specific file descriptor operations backing `internal/rawfilelock`. It wraps `unix.Open`, `unix.FcntlFlock`, and `unix.Close` behind the shared `fileHandle`, `openHandle`, `lockHandle`, `unlockAndCloseHandle`, and `closeHandle` functions.

## Important APIs and Functions
`type fileHandle uintptr` stores a Unix file descriptor. `openHandle(path, mode)` adds `O_CLOEXEC`, opens the path with mode `0644`, and returns the descriptor. `lockHandle(fd, lType, nonblocking)` maps `ReadLock` to `F_RDLCK` and everything else to `F_WRLCK`, prepares a whole-file `Flock_t` with `Len: 0`, and uses `F_SETLK` for nonblocking locks or `F_SETLKW` for blocking locks. `unlockAndCloseHandle` and `closeHandle` both call `unix.Close`.

## Control Flow and State
The blocking path loops until `FcntlFlock` succeeds; if a blocking call returns an error, it sleeps for 10 ms and retries. The nonblocking path returns the first result directly. There is no explicit unlock call before close because POSIX advisory locks are released by closing the descriptor. Persistent state is the lock file itself; active state is entirely in the open descriptor and kernel lock table.

## Dependencies and Integration Points
The file imports `time` and `golang.org/x/sys/unix`. It is called only through the shared rawfilelock API. `staging_lockfile` relies on these fcntl locks to coordinate both in-process and inter-process staging lock ownership.

## Risks and Edge Cases
The blocking retry loop can hide repeated errors other than contention because it retries any non-nil error when `nonblocking` is false. It does not retry `unix.Open` on transient errors. Closing a descriptor always releases locks on Unix, so `CloseHandle` cannot truly close without unlocking; callers must treat it as an error-path escape hatch.

## Test Signals
The paired tests verify open and lock success on Unix. Contention and cross-process behavior are indirectly covered by `staging_lockfile_test.go`, which runs a subprocess against the same lock path.
