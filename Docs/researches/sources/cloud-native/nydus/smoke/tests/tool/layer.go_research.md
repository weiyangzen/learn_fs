# sources/cloud-native/nydus/smoke/tests/tool/layer.go

## Purpose
This helper models and materializes synthetic OCI layers, packs them into Nydus blobs, merges them into bootstraps, and computes expected file trees for verification.

## Important APIs, Types, And Functions
`Layer` stores `workDir` and `FileTree`. Creation helpers write files, large random files, sparse files, dirs, symlinks, hardlinks, special files, xattrs, whiteouts, and opaque markers. `TargetPath` maps absolute paths to layer-relative names. `Pack` streams an OCI tar through `converter.Pack` to a Nydus native blob. `PackWithAttributes` writes both internal and external blobs. `PackRef` creates an optional gzip OCI blob and corresponding RAFS/zran blob. `Overlay` mutates expected file trees according to OCI whiteout/opaque semantics. `recordFileTree` walks the source tree into `FileTree`. `ToOCITar` uses `archive.Diff`. `MergeLayers` opens blob readers and calls `converter.Merge`.

## Control Flow
Tests populate a layer, pack it to blobs, merge one or more blob digests into a bootstrap, then mount and compare against `FileTree`. Overlay tests mutate the lower `FileTree` with an upper layer to derive expected merged state.

## State And Persistence
This file writes real layer contents under `workDir`, blob files named by digest under `blobDir`, and temporary bootstraps. It renames temp blobs atomically to digest hex names. `FileTree` is an in-memory metadata snapshot.

## Dependencies And Integration Points
It depends on `snapshotter-converter`, containerd archive/content local readers, OpenContainers digest, xattr, Unix syscalls, and `tool.File`. It bridges synthetic test data to real Nydus builder/merge behavior.

## Risks
`Overlay` adds upper files inside a loop over lower files, which may fail to add files when the lower tree is empty and is sensitive to map mutation during iteration. Special files and xattrs need privileges. Random large files make digests non-stable across different layer creations, though repeatability is checked on the same layer contents.

## Test Signals
Digest outputs from `Pack`/`PackRef` and `MergeLayers`, plus later file-tree comparisons, are the main signals. Failures identify packing, merge accounting, or expected-tree modeling issues.
