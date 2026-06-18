<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/plugins/snapshots/overlay/overlay_test.go -->
# sources/cloud-native/containerd/plugins/snapshots/overlay/overlay_test.go

## Purpose
Validates the Linux overlay snapshotter through the generic snapshotter suite and targeted tests for mount option construction, rebase semantics, real overlay reads, views, and ID-mapped mounts.

## Important APIs, Types, And Functions
`newSnapshotterWithOpts` constructs configured snapshotters. Main tests are `TestOverlay` plus helpers `testOverlayMounts`, `testOverlayCommit`, `testOverlayOverlayMount`, `testOverlayRemappedBind`, `testOverlayRemappedActive`, `testOverlayRemappedInvalidMapping`, `testOverlayOverlayRead`, and `testOverlayView`.

## Control Flow
`TestOverlay` runs three option sets: no option, async remove, and remap IDs. It invokes `testsuite.SnapshotterSuite` and then runs targeted subtests. Tests create snapshots, inspect returned mounts, write files into bind or overlay sources, commit, create children/views, and in one case mount the overlay to verify file reads.

## State And Persistence
Each case uses a temporary root and snapshot metadata. Helper functions open read transactions to map keys to internal snapshot IDs and parent directories.

## Dependencies And Integration Points
Depends on root privileges, containerd client remapper label helpers, snapshot testsuite, mount package, overlayutils, internal user namespace IDMap, and Linux stat ownership data.

## Risks And Edge Cases
Root and kernel mount support gate coverage. Tests depend on exact mount option ordering and feature probes such as `supportsIndex` and `NeedsUserXAttr`. Invalid mapping tests protect the snapshotter from accepting malformed UID/GID labels.

## Test Signals
Strong coverage for API compliance, bind-vs-overlay mount selection, rebase validation via `snapshots.WithParent`, user namespace remap labels, and read-only view lowerdir composition.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/plugins/snapshots/overlay/overlay_test.go -->
