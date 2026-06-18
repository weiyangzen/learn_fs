# sources/cloud-native/containers-storage/drivers/graphtest/testutil.go

## Purpose
`testutil.go` contains reusable filesystem mutation and verification helpers for graphdriver tests and benchmarks.

## Important APIs, Types, And Functions
Helpers include `randomContent`, `addFiles`, `checkFile`, `addFile`, `addDirectory`, `removeAll`, `checkFileRemoved`, `addManyFiles`, `changeManyFiles`, `checkManyFiles`, `addLayerFiles`, `addManyLayers`, `checkManyLayers`, `readDir`, and `removeLayer`.

## Control Flow
Helpers obtain a layer root with `driver.Get`, defer `Put`, then write/read/remove filesystem entries. Multi-file helpers batch files into directories of up to 100 entries. Change helpers produce expected `archive.Change` records alongside actual filesystem mutations.

## State And Persistence
All state is temporary layer content created under active graphdriver roots. `randomContent` is deterministic by seed, allowing later verification.

## Dependencies And Integration Points
The file is used by `graphtest_unix.go` and `graphbench_unix.go`. It depends on `graphdriver`, `archive`, `stringid`, and logrus.

## Risks
Failures in cleanup `Put` calls are logged rather than returned in many helpers, so primary operation errors may hide release failures. `readDir` filters `lost+found`, which is useful for ext filesystems but could hide a real test artifact with that name.

## Test Signals
These helpers generate the file trees used to validate diffs, changes, deep layer reads, and list behavior across drivers.
