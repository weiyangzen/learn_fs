# sources/cloud-native/nydus/builder/src/core/blob.rs

Purpose: owns data blob dumping and blob metadata emission for RAFS builds.

Important APIs/types/functions: `Blob::dump` is the high-level data path. `Blob::finalize_blob_data` flushes batched data, writes inline tar headers/ToC entries, and validates external blob ids. `Blob::dump_meta_data` serializes, compresses, encrypts, writes, and indexes v6 blob chunk metadata. `get_compression_algorithm_for_meta` forces Zstd for ref conversions.

Control flow: for `DirectoryToRafs`, it asks `BlobLayout::layout_blob_simple` for prefetch-first nodes, dumps each node's chunk data, records prefetch size for early entries, and finalizes. Tar/ref conversions mostly derive blob id and compressed size from tar/zran readers, then finalize. Unsupported conversions are left `unimplemented!()`. Metadata dumping optionally appends zran or batch context, compresses chunk-info data, encrypts data/header if enabled, writes data and header, writes tar headers when inline meta or blob ToC is enabled, and records ToC entries plus chunk digest arrays.

State and persistence: writes blob bytes through an `Artifact`, updates `BlobContext` cursors, hash, sizes, chunk digest arrays, metadata header, and ToC entries. It may also write blob cache data via `BuildContext::blob_cache_generator`.

Dependencies and integration points: uses `BlobLayout`, `Node::dump_node_data`, `BlobManager`, storage blob meta layouts, compression, crypto, RAFS digesting, and conversion settings from `BuildContext`.

Risks: external blob id validation requires 64-character ids and fails late. Unsafe slice conversion is used to serialize chunk digests for ToC. Empty metadata or zero uncompressed size suppresses v6 meta output. Ref conversion correctness depends on tar/zran reader position and digest state.

Test signals: tests verify metadata compression algorithm selection for ref conversion variants.
