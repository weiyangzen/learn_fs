<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/plugins/snapshots/lcow/lcow.go -->
# sources/cloud-native/containerd/plugins/snapshots/lcow/lcow.go

## Purpose
Implements and registers the Windows LCOW snapshotter, which exposes Linux container layers on Windows through `lcow-layer` mounts and manages per-container or shared scratch VHDX files.

## Important APIs, Types, And Functions
Registration ID is `windows-lcow`. Labels include rootfs size/location and scratch reuse owner labels. Main APIs implement `snapshots.Snapshotter`: `NewSnapshotter`, `Stat`, `Update`, `Usage`, `Prepare`, `View`, `Mounts`, `Commit`, `Remove`, `Walk`, and `Close`. LCOW-specific helpers are `mounts`, `createSnapshot`, `handleSharing`, `openOrCreateScratch`, and `parentIDsToParentPaths`.

## Control Flow
Initialization requires the root to be on NTFS, creates `metadata.db` and `snapshots/`, and registers Linux platform support for the host architecture. Active snapshot creation creates metadata, a snapshot directory, then skips scratch creation for unpack keys. For container scratch snapshots it either symlinks to an owner snapshot's `sandbox.vhdx` when reuse labels are set, or creates/caches a scratch VHDX with runhcs and copies it into the snapshot directory.

## State And Persistence
Persistent state includes `metadata.db`, per-ID snapshot directories, cached `scratch.vhdx` or size-specific `scratch_<N>.vhdx` files, copied `sandbox.vhdx` files, optional symlinks, and `runhcs-scratch.log`. Removal renames snapshot directories to `rm-<id>` inside the metadata transaction and deletes them afterward.

## Dependencies And Integration Points
Uses `go-winio` filesystem detection, `hcsshim/pkg/go-runhcs` scratch creation, containerd snapshot storage, mount `ParentLayerPathsFlag`, plugin registry, `ocispec.Platform`, and continuity disk usage.

## Risks And Edge Cases
Correctness depends on NTFS semantics, scratch cache locking, key-name detection of unpack operations, and owner-key substring lookup for shared scratch. Size parsing ignores parse errors and treats bad values as zero. Rename rollback failures can leave inconsistent on-disk state.

## Test Signals
No file-local tests in this subset. Generic Windows snapshotter tests do not cover LCOW directly; practical coverage is mostly integration/runtime behavior on Windows.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/plugins/snapshots/lcow/lcow.go -->
