# sources/cloud-native/nydus/builder/src/directory.rs

## Purpose
`directory.rs` implements `DirectoryBuilder`, the builder that scans a local filesystem directory and produces RAFS bootstrap/blob output. It constructs a `Tree` of `Node`s from `fs::read_dir()`, handles whiteout filtering, supports external blob attributes by building a parallel external tree, and runs the common bootstrap/blob dump sequence.

## Important APIs, types, and functions
`FilesystemTreeBuilder::load_children()` recursively builds child trees from the source directory. It reads external file size from `ctx.attributes`, creates nodes through `Node::from_fs_object()`, skips single-layer whiteout marker files, recurses into directories, calculates v5 directory size, and divides results between the normal tree and external tree. `DirectoryBuilder::build_tree()` creates root nodes and delegates recursion. `DirectoryBuilder::one_build()` performs one complete build for a provided tree. `impl Builder for DirectoryBuilder::build()` orchestrates normal and external builds.

## Control flow, state, and persistence
The public `build()` computes layer index from parent-bootstrap presence, scans the source into `(tree, external_tree)`, creates a blob writer, and runs `one_build()` for the normal tree. Then it disables prefetch by replacing `ctx.prefetch` with `PrefetchPolicy::None`, creates a separate external `BlobManager` and cloned `BootstrapManager` with `external` suffix, and runs `one_build()` on `external_tree`. The final `BuildOutput` combines normal bootstrap/blob data with external bootstrap path and external blob list.

`one_build()` creates a bootstrap context, calls shared `build_bootstrap()` (which may merge with parent), dumps blob data through `Blob::dump()`, optionally dumps blob metadata, and orders `dump_bootstrap()`/`finalize_blob()` depending on whether metadata is inlined into the blob.

## Dependencies and integration points
The module integrates `Node`, `Tree`, `Blob`, `BuildContext`, `BootstrapManager`, `BlobManager`, `ArtifactWriter`, `NoopArtifactWriter`, `Overlay`, and common helpers from `lib.rs`. It depends on `attributes` behavior through `ctx.attributes.is_external()`, `is_prefix_external()`, and value lookups. It is one of the main implementations of the crate-level `Builder` trait.

## Risks and test signals
Directory traversal uses `read_dir()` and then sorts tree children, so source filesystem order is normalized. Whiteout markers are skipped only for layer index 0 and only when not overlayfs opaque. External tree construction is subtle: fully external paths are excluded from normal tree but included in external tree, while prefix-external paths can appear in both. Local tests cover zero-sized constructors/defaults; scanning and output behavior depend on integration tests.
