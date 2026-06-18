# sources/cloud-native/nydus/builder/src/lib.rs

## Purpose
`lib.rs` is the crate root for the Nydus builder library. It re-exports the public builder API, defines the shared `Builder` trait, provides common bootstrap/blob finalization helpers, and implements `TarBuilder`, a helper used by tarball and stargz builders to construct tree nodes from archive paths.

## Important APIs, types, and functions
Public exports include `Bootstrap`, chunk dictionary types, `ArtifactStorage`, `ArtifactWriter`, `BlobCacheGenerator`, `BlobContext`, `BlobManager`, `BootstrapContext`, `BootstrapManager`, `BuildContext`, `BuildOutput`, `ConversionType`, `Feature/Features`, `ChunkSource`, `NodeChunk`, `Overlay`, `WhiteoutSpec`, `Prefetch`, `Tree`, `DirectoryBuilder`, `Merger`, `OptimizePrefetch`, `StargzBuilder`, and `TarballBuilder`. `Builder::build()` is the common trait implemented by source-specific builders.

Shared helpers are `mode_bits()`, `build_bootstrap()`, `dump_bootstrap()`, `dump_toc()`, and `finalize_blob()`. `TarBuilder` exposes `new()`, `next_ino()`, `insert_into_tree()`, `create_directory()`, and `is_stargz_special_files()`.

## Control flow, state, and persistence
`build_bootstrap()` optionally loads and merges a parent bootstrap when the bootstrap context is layered, then creates a `Bootstrap` and calls `build()`. `dump_bootstrap()` finalizes the current blob id/size, converts the blob manager to a blob table, dumps bootstrap metadata, and optionally appends compressed or raw bootstrap bytes into the data blob when `blob_inline_meta` is enabled. `dump_toc()` writes a blob TOC entry and records its digest/size. `finalize_blob()` resolves blob ids and metadata digests for normal, ref, tarfs, and inline-meta modes, finalizes the writer, and finalizes optional blob cache data.

`TarBuilder::insert_into_tree()` walks target path components, replacing existing terminal nodes, creating missing intermediate directories, and preserving sorted insertion via `Tree::insert_child()`. `create_directory()` creates synthetic directory nodes with new inode numbers, default mode/nlink/rdev, and target/source paths rooted at `/`.

## Dependencies and integration points
This file ties together all internal modules (`attributes`, `chunkdict_generator`, `compact`, `core`, `directory`, `merge`, `optimize_prefetch`, `stargz`, `tarball`). It depends on `nydus_rafs`, `nydus_storage::meta::toc`, compression/digest utilities, and `sha2::Digest`. Source builders call its shared functions to avoid duplicating bootstrap/blob finalization logic.

## Risks and test signals
Blob id resolution has several mode-specific branches. Ref conversions may derive ids from tar/zran readers, inline metadata temporarily uses `"x".repeat(64)`, and tarfs skips data blob finalization. Ordering of `dump_bootstrap()` versus `finalize_blob()` changes when metadata is inlined. Tests cover stargz special-file recognition and synthetic directory creation/inode allocation; higher-level builder tests exercise shared finalization helpers.
