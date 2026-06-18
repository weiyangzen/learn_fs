# Research: sources/distributed-fs/ipfs-kubo/cmd/ipfs/util/ulimit_test.go

Purpose: Non-Windows/non-plan9 tests for file descriptor limit management.

Important APIs/types/functions: `TestManageFdLimit` calls `ManageFdLimit` and locks `maxFds == 8192`. `TestManageInvalidNFds` sets `IPFS_FD_MAX` above the current maximum and expects an error path.

Control flow, state, and persistence: The tests mutate the process environment variable `IPFS_FD_MAX` and inspect kernel `RLIMIT_NOFILE` via `syscall.Getrlimit`. They do not persist files. Their behavior depends on the test process privileges and OS hard limit.

Dependencies and integration points: Uses `os`, `syscall`, `testing`, `fmt`, and string matching. It exercises the generic `ulimit.go` logic plus the active platform implementation.

Risks and test signals: The invalid-limit test can vary by platform if privileged processes can raise hard limits or if resource limits have unusual values. It provides useful regression coverage for default constants and error reporting, but not for all EPERM fallback combinations.
