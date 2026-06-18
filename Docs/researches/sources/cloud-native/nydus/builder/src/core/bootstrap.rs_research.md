# sources/cloud-native/nydus/builder/src/core/bootstrap.rs

Purpose: builds and dumps RAFS bootstrap metadata from a builder `Tree`, including inode numbering, directory layout, hardlink handling, parent bootstrap loading, and blob table integration.

Important APIs/types/functions: `Bootstrap::new`, `build`, `dump`, private `build_rafs`, and `load_parent_bootstrap`. `Bootstrap` owns a `Tree` and coordinates with `BuildContext`, `BootstrapContext`, `BootstrapManager`, and `BlobManager`.

Control flow: `build` assigns root inode number 1, inserts root into prefetch and hardlink maps, recursively builds RAFS metadata, then fixes v6 dirents from the root offset. `build_rafs` sets directory child counts and v5 child indexes or v6 directory offsets, assigns sequential indexes to children, detects hardlinks by `(layer_idx, src_ino, src_dev)`, reuses inode numbers for hardlinks, lays out v6 non-directory offsets, inserts nodes into prefetch, and recurses through directories. `dump` chooses v5 or v6 serialization based on blob table, then finalizes memory/file storage; directory storage is renamed to a digest-derived filename.

State and persistence: mutates tree nodes, prefetch tracking, `BootstrapContext` inode map/offset/writer, and bootstrap storage path. Parent bootstrap loading reads an existing RAFS superblock and prepends parent blobs.

Dependencies and integration points: depends on `nydus_rafs` metadata layout and compatibility checks, builder tree/node logic, artifact storage, and blob manager tables.

Risks: root inode assertions assume a fresh bootstrap context. Hardlink handling is layer-aware, but cross-layer real inode differences are called out as tricky. Digest-derived file finalization requires reading all bootstrap bytes. Parent compatibility must match compressor, digester, chunk size, uid/gid, version, and tarfs mode.

Test signals: no local tests in this file; exercised by builder integration and compaction/chunkdict paths that call build/dump.
