# Research: sources/distributed-fs/ipfs-kubo/cmd/ipfs/util/ulimit_freebsd.go

Purpose: FreeBSD-specific file descriptor limit implementation.

Important APIs/types/functions: `init()` enables FD management and binds `getLimit`/`setLimit`. `freebsdGetLimit()` wraps `unix.Getrlimit`. `freebsdSetLimit()` wraps `unix.Setrlimit`.

Control flow, state, and persistence: At package initialization, this file switches the generic ulimit logic on. It validates that returned FreeBSD `Rlimit` values are non-negative and that requested uint64 values fit into `int64` before converting to `unix.Rlimit`.

Dependencies and integration points: Uses `golang.org/x/sys/unix`, `errors`, and `math`. Integrated by package-level hooks consumed by `ManageFdLimit`.

Risks and test signals: Integer conversion is the main safety concern; explicit checks prevent wraparound. Runtime behavior still depends on FreeBSD privilege and resource limit policy. Covered indirectly by non-Windows/non-plan9 ulimit tests when run on FreeBSD.
