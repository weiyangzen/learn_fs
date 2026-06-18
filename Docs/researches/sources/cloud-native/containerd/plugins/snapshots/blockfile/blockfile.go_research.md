# sources/cloud-native/containerd/plugins/snapshots/blockfile/blockfile.go

## Purpose
`blockfile.go` implements a snapshotter that represents each snapshot as a mountable filesystem image file, usually loop-mounted ext4.

## Important APIs, Types, And Functions
`SnapshotterConfig` controls scratch generation, filesystem type, mount options, scratch recreation, and a test-only view hook. Options include `WithScratchFile`, `WithFSType`, `WithMountOptions`, and `WithRecreateScratch`. The `snapshotter` implements snapshotter methods `Stat`, `Update`, `Usage`, `Prepare`, `View`, `Mounts`, `Commit`, `Remove`, `Walk`, `Close`, plus helpers `createSnapshot`, `getBlockFile`, `mounts`, and `copyFileWithSync`.

## Control Flow
`NewSnapshotter` creates the root, ensures a scratch image exists or is generated, sets defaults, creates a metadata store and snapshots directory, and returns the snapshotter. Active snapshots copy either the parent block file or scratch file into a new snapshot file. View snapshots with parents mount the parent block file read-only. Commit records file size usage. Remove deletes metadata transactionally and renames the block file to `rm-<id>` before final removal.

## State And Persistence
Snapshot metadata persists in `metadata.db`. Block files persist under `<root>/snapshots/<id>`, with a root-level `scratch` template. Usage is approximated by file sizes and parent subtraction.

## Dependencies And Integration Points
It depends on containerd snapshot storage metadata, mount specs, continuity file copy helpers, platform runtime checks, and plugin errors for skip behavior.

## Risks
Usage underreports or overreports when sparse files or shared extents are involved. `mounts` appends to `o.options` without copying, which can accidentally accumulate `ro` or `rw` across calls if the backing slice is reused. Scratch generation is mandatory for first startup unless an existing scratch is present. Remove rollback logs but cannot fully recover from failed renames.

## Test Signals
`blockfile_test.go` runs the generic snapshotter suite. Platform setup tests create ext4 loopback scratch images where supported and skip elsewhere.
