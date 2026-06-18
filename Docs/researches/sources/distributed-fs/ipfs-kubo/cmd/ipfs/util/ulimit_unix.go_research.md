# Research: sources/distributed-fs/ipfs-kubo/cmd/ipfs/util/ulimit_unix.go

Purpose: Generic Unix file descriptor limit implementation for non-Windows, non-plan9, non-FreeBSD platforms.

Important APIs/types/functions: `init()` enables FD management and wires `getLimit`/`setLimit`. `unixGetLimit()` calls `syscall.Getrlimit`; `unixSetLimit()` calls `syscall.Setrlimit`.

Control flow, state, and persistence: The implementation directly converts syscall `Rlimit` values to and from `uint64`. No file or repository state is touched; it modifies only process resource limits through the kernel.

Dependencies and integration points: Uses the standard `syscall` package and the shared hooks consumed by `ManageFdLimit`.

Risks and test signals: Unlike FreeBSD, this path has no signed-range validation because common Unix `Rlimit` fields are unsigned in Go. Behavior is still constrained by OS hard limits and process privileges. Covered indirectly by `ulimit_test.go` on supported Unix platforms.
