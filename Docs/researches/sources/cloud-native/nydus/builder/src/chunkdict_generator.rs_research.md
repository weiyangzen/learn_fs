# sources/cloud-native/nydus/builder/src/chunkdict_generator.rs

Purpose: generates a RAFS bootstrap representing a chunk dictionary. It creates a minimal filesystem tree with root and `/chunkdict`, maps supplied chunk/blob metadata into RAFS chunk records, and dumps bootstrap metadata.

Important APIs/types/functions: `ChunkdictChunkInfo` describes per-chunk source image, blob id, digest, CRC, sizes, and offsets. `ChunkdictBlobInfo` describes blob-level sizes, compressor, and blob meta chunk-info positions. `Generator::generate` is the entry point. Internal helpers include `sort_chunks`, `validate_and_remove_chunks`, `build_root_tree`, `build_child_tree`, `insert_chunks`, and `validate_tree`.

Control flow: generation clones and sorts chunk inputs by blob id, compressed offset, uncompressed offset, and digest; removes blob groups whose total uncompressed size is smaller than `ctx.v6_block_size()`; builds a synthetic root directory; builds a child file named `chunkdict`; inserts chunk wrappers while creating/updating blob contexts; builds and dumps the bootstrap; then returns `BuildOutput`.

State and persistence: mutates `BuildContext`, `BootstrapManager`, and `BlobManager`. It writes bootstrap data through `bootstrap_mgr.bootstrap_storage`; blob data is referenced from chunk dictionary metadata, not produced by reading source files here.

Dependencies and integration points: integrates RAFS inode/chunk wrappers, blob metadata headers, compression algorithms, digest parsing, and builder tree/bootstrap managers. It relies on `BlobManager::get_or_cerate_blob_for_chunkdict`.

Risks: `insert_chunks` uses `unwrap()` when finding matching `ChunkdictBlobInfo`, so missing blob metadata panics. The meta compressed-size update first increments from current uncompressed size and is then overwritten by provided blob info; correctness depends on supplied metadata. Small-blob filtering prints warnings to stderr.

Test signals: tests validate small group removal, boundary-size retention, and root tree creation.
