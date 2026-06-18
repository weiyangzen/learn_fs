<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/plugins/snapshots/windows/windows.go -->
# sources/cloud-native/containerd/plugins/snapshots/windows/windows.go

## Purpose
Implements and registers the legacy WCOW Windows snapshotter for `windows-layer` mounts, base layer conversion, sandbox VHDX creation, and writable-to-read-only layer commit conversion.

## Important APIs, Types, And Functions
Registration ID is `windows`. Labels include `uvmScratchLabel`, deprecated GB rootfs size, and byte rootfs size. Main APIs are `NewWindowsSnapshotter`, `Prepare`, `View`, `Commit`, `Remove`, `Mounts`, `createSnapshot`, `createScratchLayer`, `convertScratchToReadOnlyLayer`, and `mounts`.

## Control Flow
Initialization requires NTFS and creates a base snapshotter. Parentless active snapshots create a `Files` directory for a future base layer. Child scratch snapshots gather parent layer paths, parse scratch size labels, optionally create UVM scratch, and copy/expand `blank.vhdx` into `sandbox.vhdx`. Commit converts parentless layers to base layers or reimports scratch layers as read-only layers unless the key is an unpack key.

## State And Persistence
Stores metadata in `metadata.db`, snapshot directories under `snapshots/<id>`, `Files` for base layers, `sandbox.vhdx`, optional `vm/sandbox.vhdx`, and converted on-disk Windows layer data. Removal delegates directory rename to `preRemove` and destroys the renamed layer with hcsshim.

## Dependencies And Integration Points
Uses go-winio privileges, hcsshim, OCI Windows layer import/export, containerd mount flags, platform registration, and common Windows base snapshotter helpers.

## Risks And Edge Cases
Commit conversion duplicates data because `sandbox.vhdx` is retained for later export. Privilege enabling is required for import/export. Key-name detection of unpack snapshots controls whether scratch creation or conversion is skipped.

## Test Signals
`windows_test.go` runs the generic snapshotter suite on Windows as root/admin. Specific conversion and scratch-size paths need broader Windows integration coverage.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/plugins/snapshots/windows/windows.go -->
