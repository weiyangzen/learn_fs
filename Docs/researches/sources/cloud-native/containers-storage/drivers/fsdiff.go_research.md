# sources/cloud-native/containers-storage/drivers/fsdiff.go

## Purpose
`fsdiff.go` implements `NaiveDiffDriver`, a generic diff/apply/changes wrapper for `ProtoDriver` implementations that do not provide native diffing.

## Important APIs, Types, And Functions
`ApplyUncompressedLayer` is the injectable unpack function. `NaiveDiffDriver` embeds `ProtoDriver` and `LayerIDMapUpdater`. `NewNaiveDiffDriver` returns a complete `Driver`. Methods implement `Diff`, `Changes`, `ApplyDiff`, and `DiffSize`.

## Control Flow
`Diff` mounts the layer read-only, and for non-base layers also mounts the parent read-only, computes changes with `archive.ChangesDirs`, and exports changes. Base layers are tarred directly. Close wrappers call `driverPut`, and `Diff` sleeps until the next second to avoid mtime precision races. `ApplyDiff` gets the target layer, builds tar options with user namespace and mapping behavior, and calls `ApplyUncompressedLayer`. `DiffSize` computes changes and sums their sizes.

## State And Persistence
The wrapper does not persist its own state. It mounts/releases underlying driver layers and applies tar data into the target layer filesystem.

## Dependencies And Integration Points
It integrates with every driver that wraps a `ProtoDriver`, including Btrfs. Dependencies include `archive`, `chrootarchive`, `idtools`, `ioutils`, `unshare`, runtime OS checks, and logrus.

## Risks
Naïve diffing is slower and depends on mounted filesystem views. Mtime granularity is explicitly handled with a sleep. Forgetting to close returned diff readers can leak `Get` references. Parent mapping defaults must be correct for ID-mapped layer comparisons.

## Test Signals
`graphtest` diff/apply/changes tests exercise this path for drivers that use the wrapper.
