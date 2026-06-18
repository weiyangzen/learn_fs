# sources/cloud-native/containers-storage/pkg/mount/sharedsubtree_linux.go

Purpose: exposes helpers to set Linux mount propagation modes on a mountpoint.

Important APIs, types, and functions: `MakeShared`, `MakeRShared`, `MakePrivate`, `MakeRPrivate`, `MakeSlave`, `MakeRSlave`, `MakeUnbindable`, `MakeRUnbindable`, and private `ensureMountedAs`.

Control flow: each public helper calls `ensureMountedAs` with the matching propagation flag. `ensureMountedAs` checks whether the path is mounted; if not, it bind-mounts the path onto itself, then applies the propagation remount.

State and persistence: mutates the current mount namespace by creating a self-bind mount when necessary and changing propagation attributes.

Dependencies and integration points: uses `Mounted` and platform `mount` from this package. It is Linux-only and feeds container mount propagation setup.

Risks and edge cases: requires privileges. Making an unmounted path into a self-bind mount changes mount topology and must be undone by callers. Propagation changes can affect child mount behavior broadly.

Test signals: `sharedsubtree_linux_test.go` verifies private, shared, slave, and unbindable propagation semantics using real bind mounts.
