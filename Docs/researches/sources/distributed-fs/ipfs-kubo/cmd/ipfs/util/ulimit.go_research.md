# Research: sources/distributed-fs/ipfs-kubo/cmd/ipfs/util/ulimit.go

Purpose: Cross-platform entry point for raising the process file descriptor limit at startup.

Important APIs/types/functions: Package variables `supportsFDManagement`, `getLimit`, and `setLimit` are installed by platform files. `userMaxFDs()` parses `IPFS_FD_MAX`. `ManageFdLimit()` selects a target limit, compares current soft/hard limits, and attempts to raise them.

Control flow, state, and persistence: If platform support is disabled, `ManageFdLimit` is a no-op. Otherwise it defaults to `maxFds` (8192) unless `IPFS_FD_MAX` is a valid uint. It reads the current soft/hard limits, exits if the soft limit already satisfies the target, then tries to set soft and hard to target. On `syscall.EPERM`, it lowers the target to the hard limit if needed and tries setting only the soft limit, producing warnings when the result is below requested or below `minFds` (2048). No persistent state is written; only process resource limits and logs are affected.

Dependencies and integration points: Depends on `os`, `strconv`, `syscall`, and `go-log`. Platform implementations supply `getLimit`/`setLimit` in `ulimit_unix.go`, `ulimit_freebsd.go`, or no-op Windows behavior. Startup code can use the returned `changed`, `newLimit`, and `err` values for user-facing diagnostics.

Risks and test signals: Invalid `IPFS_FD_MAX` silently falls back to no user target after logging, which may surprise operators. Permission and hard-limit handling is subtle and OS-dependent. `ulimit_test.go` covers default value stability and invalid oversized env values on non-Windows/non-plan9.
