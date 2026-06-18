# sources/distributed-fs/seaweedfs/weed/filer/posixlock/posixlock_test.go

## Purpose

`posixlock/posixlock_test.go` is the core unit test suite for the pure `Set` range-lock algorithm. It documents POSIX/flock semantics and many boundary cases.

## Important APIs, Types, and Functions

The tests use helper `mustAcquire` plus `Set.Acquire`, `Conflict`, `Release`, `ReleaseOwner`, `ReleasePosixOwner`, `ReleaseFlockOwner`, `ReleaseSession`, `HasPosix`, `Empty`, and direct `s.locks` inspection.

## Control Flow

Tests build sets, acquire ranges with different owners/sessions/namespaces, assert conflicts or grants, release partial ranges, and inspect resulting ranges. Cases cover shared reads, write/read and write/write conflicts, same-owner upgrade/downgrade, adjacent coalescing, mid-range splitting, whole-file locks, namespace separation, flock/posix owner releases, `MaxUint64` adjacency, and session-aware owner identity.

## State and Persistence Behavior

All lock state is local to a `Set`. Tests do not use the concurrent `Manager` except indirectly through shared types.

## Dependencies and Integration Points

The file depends on Go's `testing` and `math`. It protects the algorithm used by distributed FUSE lock management.

## Risks and Edge Cases

Direct slice assertions are valuable but couple tests to sorted storage. Tests do not run randomized interval fuzzing, so unusual interleavings of many locks could still hide bugs.

## Test Signals

Signals include exact split ranges after unlock/type replacement, no false merge at `MaxUint64`, same owner numbers in different sessions conflicting, flock and fcntl not conflicting, and empty set after releasing all locks.
