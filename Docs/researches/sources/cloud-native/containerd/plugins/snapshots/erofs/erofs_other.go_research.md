<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/plugins/snapshots/erofs/erofs_other.go -->
# sources/cloud-native/containerd/plugins/snapshots/erofs/erofs_other.go

## Purpose
Provides non-Linux stubs for EROFS platform operations so the package can compile while making Linux-only functionality explicitly unavailable.

## Important APIs, Types, And Functions
Defines `defaultWritableSize` as 64 MiB on non-Linux and stubs `checkCompatibility`, `setImmutable`, `cleanupUpper`, `convertDirToErofs`, and `getParentOwnership`.

## Control Flow
No real EROFS work is performed. Compatibility and cleanup are no-ops; immutable flag setting and directory-to-EROFS conversion return `errdefs.ErrNotImplemented`; ownership probing returns `-1, -1`.

## State And Persistence
No persistent state is created. The file intentionally avoids touching filesystem attributes or layer blobs on unsupported platforms.

## Dependencies And Integration Points
Compiled under `!linux`. It integrates with the common EROFS snapshotter code by satisfying platform-specific helper symbols and depends only on `context` and `errdefs`.

## Risks And Edge Cases
If common code invokes conversion or immutable operations on non-Linux, callers must surface `ErrNotImplemented` cleanly. The 64 MiB default writable size differs from Linux's zero default and can affect block-mode expectations in cross-platform configuration.

## Test Signals
No file-local tests. Coverage is compile-time plus any non-Linux package builds that exercise option parsing without invoking unsupported paths.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/plugins/snapshots/erofs/erofs_other.go -->
