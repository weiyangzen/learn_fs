# sources/cloud-native/containers-storage/pkg/mount/mounter_linux_test.go

Purpose: validates Linux mount syscall sequencing and resulting mountinfo options.

Important APIs, types, and functions: `TestMount`, `ensureUnmount`, `validateMount`, `clean`, and `has`.

Control flow: root-only test creates a tmpfs source, then runs table-driven cases for bind, propagation modes, rw/ro, and remount data changes. After each mount, it reads mountinfo, compares expected ordinary options, optional propagation fields, and VFS options while allowing kernel-volunteered defaults.

State and persistence: temporarily mutates the current mount namespace and cleans up with `Unmount`.

Dependencies and integration points: depends on `fmt`, `os`, `strings`, and `testing`. It integrates `Mount`, `MakeShared`, `MakePrivate`, `GetMounts`, and Linux mountinfo parsing.

Risks and edge cases: root required. Shared/slave propagation cases depend on the source mount being made shared and then restored private. Kernel/default option variation is partially allowed by volunteered maps.

Test signals: strong coverage for Linux bind read-only remount mechanics, propagation remounts, remount data changes, and mountinfo validation.
