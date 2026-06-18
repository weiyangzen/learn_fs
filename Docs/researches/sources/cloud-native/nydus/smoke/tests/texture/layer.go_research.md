# sources/cloud-native/nydus/smoke/tests/texture/layer.go

## Purpose
This package creates synthetic filesystem layers for Nydus smoke tests. The layers intentionally include regular files, large files, sparse files, directories, hardlinks, symlinks, special files, non-ASCII and long names, whiteouts, opaque markers, and xattrs to stress pack/merge/mount behavior.

## Important APIs, Types, And Functions
`LayerMaker` is a callback for customizing a `tool.Layer`. `LargerFileMaker` returns a callback that adds a large random file. `MakeChunkDictLayer` creates files useful for dictionary content. `MakeLowerLayer` creates the broad lower-layer fixture. `MakeThinLowerLayer` creates a privilege-light layer without special files for UFFD tests. `MakeUpperLayer` creates overlay updates, whiteouts, an opaque directory, and a capability xattr. `MakeMatrixLayer` creates small named files for parent-bootstrap matrix tests. `PrepareLayerWithContext` creates a default context, workdir, lower layer, OCI/RAFS blob pair, merges a bootstrap, and returns both context and layer.

## Control Flow
Most functions allocate a new `tool.Layer`, call `Create*` helpers to populate files, apply optional makers, and return the layer. `PrepareLayerWithContext` additionally packs via `PackRef`, merges with `tool.MergeLayers`, asserts the original OCI digest is returned, and sets `ctx.Env.BootstrapPath`.

## State And Persistence
The functions write real files, directories, links, sparse files, device nodes/FIFO, xattrs, blobs, and bootstraps under the caller-provided workdir. `MakeUpperLayer` and `MakeLowerLayer` call `setcap`, altering security xattrs on test files.

## Dependencies And Integration Points
This package depends on `tool.Layer`, `snapshotter-converter`, OpenContainers digests, `syscall`, and host `setcap`. It feeds most test suites, so its exact file set is an implicit contract for CAS counts, file-tree verification, overlay behavior, and chunkdict content.

## Risks
Special file creation and `setcap` require privileges/capabilities. The path with emoji and Chinese characters intentionally uses Unicode, which can reveal encoding/path handling issues but may be host-sensitive. Large random files increase disk and time cost.

## Test Signals
There are no direct tests in this file, but downstream `tool.Verify`, digest checks, CAS row counts, and mount comparisons all depend on these fixtures being constructed as expected.
