# sources/cloud-native/nydus/builder/src/optimize_prefetch.rs

## Purpose
`optimize_prefetch.rs` generates an optimized prefetch blob from an existing RAFS tree/blob set and rewrites selected file chunks to point to that new blob. It is intended to improve startup or hot-path reads by copying configured chunks into a separate blob marked with prefetch-related features, then dumping an updated bootstrap.

## Important APIs, types, and functions
`OptimizePrefetch` is a zero-sized public struct. `PrefetchBlobState` groups the new `BlobInfo`, `BlobContext`, and writer. `PrefetchFileInfo` stores an absolute path and optional byte ranges parsed from JSON. `generate_prefetch()` is the main entry point. Important helpers are `PrefetchBlobState::new()`, `process_prefetch_node()`, `dump_blob()`, `build_dump_bootstrap()`, `rewrite_blob_id()`, `update_ctx_from_bootstrap()`, `generate_prefetch_file_info()`, and `range_overlap()`.

## Control flow, state, and persistence
`generate_prefetch()` creates a new blob index at the end of the existing blob table, initializes a `PrefetchBlobState`, and processes each configured file. `process_prefetch_node()` finds the tree node, skips missing paths, filters chunks by optional ranges, reads compressed bytes from the backend using the original blob id and compressed offset, writes those bytes to the prefetch blob, and mutates each selected `NodeChunk` to the new blob index, chunk index, compressed/uncompressed offsets, and metadata. For v6 it also generates chunk-info metadata through `BatchContextGenerator`.

After all chunks are copied, `dump_blob()` appends the placeholder `prefetch-blob` info into the blob table, finalizes blob data/meta, calculates the real blob id, and rewrites the placeholder in the table. `build_dump_bootstrap()` rebuilds/dumps the bootstrap using the extended blob table and adjusts hardlink sibling chunk vectors in `bootstrap_ctx.inode_map` so hardlinks point to the rewritten chunks. `generate_prefetch_file_info()` reads a v1 JSON file and keeps only absolute paths.

## Dependencies and integration points
The module depends on `RafsBlobTable`, `RafsSuper`, `BlobBackend`, `BlobInfo`, `BlobContext`, `BlobManager`, `BootstrapManager`, `Bootstrap`, `Tree`, and shared finalization from `lib.rs`. It consumes backend readers for source blob bytes and writes output through `ArtifactWriter`. `update_ctx_from_bootstrap()` initializes build context from an existing bootstrap before optimization.

## Risks and test signals
`process_prefetch_node()` uses `expect()` on backend `get_reader()` and `read()`, so backend failures can panic instead of returning `Result`. The `encrypted` variable is derived from `blob_compressor != None`, which looks suspiciously named and may not reflect encryption state. `range_overlap()` treats touching boundaries as overlap because it uses `<=`; for half-open byte ranges this includes zero-byte intersection at edges. Tests cover JSON parsing, range overlap, struct cloning, and blob id rewriting, but not full backend IO or generated bootstrap output.
