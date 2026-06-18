<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/core/mount/mount_unix.go -->
# sources/cloud-native/containerd/core/mount/mount_unix.go

Purpose: Unix unmount helpers for non-Windows, non-OpenBSD platforms.

Important APIs/types/functions: `UnmountRecursive(target, flags)` canonicalizes a target, finds all mountinfo entries under it, sorts deepest paths first, and calls `UnmountAll`.

Control flow: empty target returns nil. Nonexistent canonical target is treated as no-op. Mountpoints are deduplicated through a map, sorted by descending path length, and unmounted; errors from children are tolerated unless the final/top-level target fails.

State and persistence: removes kernel mount state below a path; no metadata persistence.

Dependencies and integration points: used by temp mount cleanup, idmapped overlay cleanup, and mount manager cleanup paths. Depends on `moby/sys/mountinfo`, `CanonicalizePath`, and platform `UnmountAll`.

Risks: prefix filtering depends on canonical paths; non-final child unmount failures can be ignored, potentially leaving busy nested mounts. Sorting by string length is a practical deepest-first heuristic.

Test signals: `mount_linux_test.go` exercises recursive unmounts with nested bind mounts.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/core/mount/mount_unix.go -->
