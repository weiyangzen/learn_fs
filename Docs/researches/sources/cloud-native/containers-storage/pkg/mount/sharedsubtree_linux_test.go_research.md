# sources/cloud-native/containers-storage/pkg/mount/sharedsubtree_linux_test.go

Purpose: integration-tests Linux shared-subtree propagation semantics.

Important APIs, types, and functions: `TestSubtreePrivate`, `TestSubtreeShared`, `TestSubtreeSharedSlave`, `TestSubtreeUnbindable`, and helper `createFile`.

Control flow: root-only tests create source/target/outside directories, set propagation modes with `MakePrivate`, `MakeShared`, `MakeSlave`, or `MakeUnbindable`, perform bind mounts into source or target subdirectories, and check whether files appear across propagation boundaries.

State and persistence: mutates the mount namespace with self-bind, bind, and propagation remounts; temporary directories and mounts are cleaned in defers.

Dependencies and integration points: depends on `errors`, `os`, `path`, `testing`, and `x/sys/unix`. It validates `sharedsubtree_linux.go`, `Mount`, and `Unmount` against kernel behavior.

Risks and edge cases: requires root and a mount namespace where propagation changes are permitted. Cleanup must unmount in the right order. Tests may be sensitive to environment defaults.

Test signals: strong semantic signals for no propagation under private, target-to-source propagation under shared, one-way source-to-slave propagation, and bind failure for unbindable mounts.
