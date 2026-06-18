# sources/cloud-native/nydus/builder/src/merge.rs

## Purpose
`merge.rs` implements image-level RAFS bootstrap merging. Given per-layer RAFS bootstraps, optional parent bootstrap, optional chunk dictionary bootstrap, and replacement blob metadata, it overlays trees using whiteout rules, remaps chunk blob indices, prunes dereferenced blobs, and writes a new merged bootstrap.

## Important APIs, types, and functions
`Merger` is a zero-sized public struct. Helper methods `get_string_from_list()`, `get_digest_from_list()`, and `get_size_from_list()` safely fetch optional per-layer metadata by index. `Merger::merge()` is the main entry point and accepts `BuildContext`, optional parent path, source bootstrap paths, optional blob digests/original ids/sizes/TOC metadata, target artifact storage, optional chunk dictionary path, and runtime config.

## Control flow, state, and persistence
`merge()` validates that optional metadata vectors match source count, then initializes a `BlobManager`, blob id-to-index map, and optional base tree. A parent bootstrap, if supplied, is loaded first; its blobs are added as `ChunkSource::Parent`, and its tree becomes the lower tree. A chunk dictionary bootstrap, if supplied, contributes a set of blob ids to ignore when identifying each layer's new data blob and provides compatibility config.

For each source layer, the bootstrap is loaded, metadata compatibility is checked, context compressor/digester/cipher/UID mode/tarfs flags are updated, blob contexts are created/remapped, and optional digest/size/original-id overrides are applied. The layer tree is loaded, all chunk blob indices are remapped into the merged blob manager's indices, layer indices are assigned, overlay state is set to `UpperAddition`, and the tree is merged into the accumulated tree. After all layers, the final tree is walked to build a used-blob manager containing only referenced blobs and to rewrite chunk blob indices again to compact the blob table. Finally it builds and dumps a new bootstrap.

## Dependencies and integration points
The module uses `RafsSuper::load_from_file()`, `ConfigV2`, `BlobContext`, `BlobManager`, `Bootstrap`, `BootstrapContext`, `Tree`, `Overlay`, `ChunkSource`, `BlobFeatures`, and crypto metadata. It relies on `Tree::from_bootstrap()` and `Tree::merge_overaly()` for topology and whiteouts, and on `Bootstrap::build/dump()` for output. It is likely invoked by CLI merge commands.

## Risks and test signals
Layer metadata must be consistent: chunk size mismatches, incompatible configs, unsupported cipher algorithms, too many layers, and multiple non-dictionary blobs per layer all fail. Blob id remapping is subtle because bootstrap blob ids may differ from runtime original tar ids depending on accessibility and conversion mode. Unit tests cover helper accessors, mismatched optional vector validation, empty source rejection, and a successful v6 fixture merge; chunk dictionary, tarfs conflicts, and cipher branches need integration coverage.
