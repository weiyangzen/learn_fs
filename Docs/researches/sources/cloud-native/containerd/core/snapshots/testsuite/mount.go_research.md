# sources/cloud-native/containerd/core/snapshots/testsuite/mount.go

## Purpose
Provides mount and unmount helpers for snapshotter tests, with optional integration through the containerd mount manager.

## APIs, Flow, State, Dependencies, Risks, And Tests
`withMountManager` creates a temp target root, opens a Bolt DB, constructs a mount manager, registers cleanup, and stores it in context. `mountAll` checks for a mount manager in context, tries `Activate` to transform mounts, falls back only on `ErrNotImplemented`, then calls `mount.All`. `unmountCtx` unmounts all mounts at the target and deactivates the mount manager entry, ignoring `ErrNotFound`. `unmountAll` is a test helper that fails the test on unmount errors. `umountflags` is zero.

State includes temp mount targets, a temporary mount-manager Bolt DB, active mount-manager records, and real OS mounts. Dependencies include bbolt, mount manager, errdefs, mount package, testing, and context values.

Risks include leaked mounts if cleanup order fails, context key misuse, requiring platform mount privileges/capabilities, and activation errors hiding mount transformations. Test signals are conformance tests passing with and without mount manager activation and cleanup leaving no mounts active.
