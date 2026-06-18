<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/plugins/snapshots/overlay/overlay.go -->
# sources/cloud-native/containerd/plugins/snapshots/overlay/overlay.go

## Purpose
Implements the Linux overlayfs snapshotter, storing per-snapshot upper/work directories and returning bind or overlay mounts that compose parent snapshots.

## Important APIs, Types, And Functions
Configuration includes `SnapshotterConfig`, `Opt`, `AsynchronousRemove`, `WithUpperdirLabel`, `WithMountOptions`, `WithMetaStore`, `WithRemapIDs`, and `WithSlowChown`. The `snapshotter` implements `NewSnapshotter`, `Stat`, `Update`, `Usage`, `Prepare`, `View`, `Mounts`, `Commit`, `Remove`, `Walk`, `Cleanup`, and `Close`. Helpers include `createSnapshot`, `prepareDirectory`, `mounts`, `upperPath`, `workPath`, `supportsIndex`, and cleanup directory scanners.

## Control Flow
Initialization validates backing filesystem `d_type`, opens or accepts a metastore, creates `snapshots/`, auto-adds `userxattr` if needed in user namespaces, and adds `index=off` when supported. Snapshot creation creates a `new-*` directory with `fs` and optional `work`, writes snapshot metadata, applies user namespace ownership or parent ownership, then renames to the snapshot ID. Mount construction returns bind mounts for no-parent and single-parent views, and overlay mounts with `workdir`, `upperdir`, `lowerdir`, ID-map options, and configured options for active or multi-parent views.

## State And Persistence
Persistent state is `metadata.db` and `snapshots/<id>/fs` plus `work` for active snapshots. Removed metadata is decoupled from disk cleanup when `asyncRemove` is enabled; `Cleanup` removes directories not present in `storage.IDMap`.

## Dependencies And Integration Points
Uses containerd mount/snapshot storage APIs, `overlayutils`, `internal/userns`, continuity `fs`, Linux `syscall.Stat_t`, and plugin-provided metadata store injection for tests or embedding.

## Risks And Edge Cases
Overlayfs requires `d_type`, correct `userxattr` behavior in user namespaces, and support for multiple lowerdirs. ID mapping depends on valid snapshot labels and root mapping extraction. Async removal can leave disk usage until cleanup. Mount option ordering is tested and can break callers that compare options.

## Test Signals
`overlay_test.go` runs the generic suite and checks mount forms, commit parent rebasing, real overlay reads, view behavior, ID-mapped ownership and mount options, and invalid mapping rejection.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/plugins/snapshots/overlay/overlay.go -->
