# sources/cloud-native/nydus/builder/src/core/chunk_dict.rs

Purpose: defines the chunk dictionary abstraction used for cross-image/layer deduplication and provides a hash-map implementation backed by RAFS bootstrap metadata.

Important APIs/types/functions: `ChunkDict` trait supports adding chunks, lookup by digest and uncompressed size, blob metadata access, inner-to-real blob index mapping, and digester reporting. `()` implements a null dictionary. `HashChunkDict` stores `HashMap<RafsDigest, (Arc<ChunkWrapper>, AtomicU32)>`, blob infos, a mutexed blob index map, and a digest algorithm. `parse_chunk_dict_arg` supports `bootstrap=path` or bare path.

Control flow: `from_commandline_arg` parses the path and loads a bootstrap. `from_bootstrap_file` loads `RafsSuper`, captures blob table, checks compatibility, then either reconstructs a tree for v5/inlined-digest metadata or loads the v6 chunk table directly. `load_chunk_table` validates table byte size and converts each RAFS chunk-info entry into a `ChunkWrapper`.

State and persistence: dictionary state is in memory. It reads bootstrap files and uses mutable/atomic counters plus a mutex for blob index associations; no files are written.

Dependencies and integration points: used by `BlobManager`, `Bootstrap::load_parent_bootstrap`, compaction, and chunk dedup during node building. Depends on `nydus_api::ConfigV2`, RAFS super/config, storage `BlobInfo`, and digest utilities.

Risks: chunks are added only if the incoming digester equals the dictionary digester. Lookup permits dictionary chunks with uncompressed size 0 to match any requested size, which is intentional but broad. `()` returns `Some(inner_idx)` for `get_real_blob_idx`, while `HashChunkDict` returns `None` unless explicitly mapped. Unsupported dictionary types fail fast.

Test signals: tests cover null dictionary behavior, loading a fixture bootstrap, index mapping, argument parsing, constructor defaults, duplicate add counters, digester mismatch ignoring, lookups, and ordering/equality helper behavior.
