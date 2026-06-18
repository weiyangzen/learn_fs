<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/client/container_opts_unix.go -->
# sources/cloud-native/containerd/client/container_opts_unix.go

Purpose: Unix-only container options for creating user-namespace-remapped snapshots and read-only views.

Important APIs/types/functions: `WithRemappedSnapshot`, `WithUserNSRemappedSnapshot`, `WithRemappedSnapshotView`, `WithUserNSRemappedSnapshotView`, internal `withRemappedSnapshotBase`, `remapRootFS`, and `chown`.

Control flow: computes image rootfs chain ID, derives a stable remapped snapshot ID from UID/GID mappings, reuses existing remapped snapshots if available, otherwise prepares a temporary remap snapshot, temp-mounts it, walks the filesystem and `Lchown`s every path through the userns map, commits the remapped snapshot, then prepares or views the requested container snapshot.

State/persistence: creates reusable remapped snapshot layers and per-container snapshots/views. Mutates file ownership in the remap snapshot while preserving special permission bits on non-symlinks.

Dependencies/integration: Unix build tag, snapshotters, mount temp mounts, internal userns mapping, OCI runtime-spec ID mappings, identity chain IDs, syscall stat, filesystem walking.

Risks: type asserts `i.(*image)`, so custom `Image` implementations can panic. Full filesystem walk can be slow and permission-sensitive. Error cleanup removes `usernsID` rather than the `usernsID+"-remap"` active snapshot in one path, which deserves scrutiny. Ownership remap must avoid symlink dereference, which `Lchown` handles.

Test signals: remap ID determinism, custom image interface behavior, reuse existing remap snapshot, cleanup on remap failure, symlink ownership, setuid/setgid/sticky preservation, read-only view creation, and large filesystem performance.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/client/container_opts_unix.go -->
