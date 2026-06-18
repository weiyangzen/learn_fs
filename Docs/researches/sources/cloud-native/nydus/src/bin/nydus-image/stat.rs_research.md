# sources/cloud-native/nydus/src/bin/nydus-image/stat.rs

## Purpose
`stat.rs` computes statistics for RAFS bootstraps: filesystem object counts, file-size and chunk-size distributions, compressed/uncompressed sizes, hardlink-aware file totals, and optional deduplication comparisons between base and target images.

## Important APIs, Types, And Functions
`DedupInfo` stores threshold-based dedup accounting. `ImageInfo` stores per-image directory/file/symlink/chunk counts, size histograms, owned/reference chunk counters, and deduplicated totals. `ImageStat` is the public command object with `new`, `stat`, `finalize`, `dump_json`, and `dump`. It owns a `HashChunkDict` used to compare target chunks against base chunks.

## Control Flow
`ImageStat::stat` loads a `RafsSuper`, constructs a temporary `HashChunkDict` through `Tree::from_bootstrap`, and walks the tree pre-order. Regular files update file and padding sizes, skip duplicate hardlink inodes, count chunks, sum compressed/uncompressed chunk sizes, and fill chunk-size buckets. Directories and symlinks update object counters. For base images, all dictionary chunks are added to the global dedup dictionary. For target images, each chunk is classified as referenced if present in the base dictionary, otherwise owned. `finalize` adds padding to uncompressed totals and, when dedup is enabled, builds threshold rows from chunk reference counts.

## State And Persistence
All analysis state is in memory until `dump_json` writes a JSON report or `dump` prints text. The RAFS bootstrap and blob metadata are read only. Dedup state persists only inside `ImageStat` for the lifetime of one command invocation.

## Dependencies And Integration Points
The module depends on `RafsSuper`, `Tree`, `HashChunkDict`, `ChunkDict`, `ConfigV2`, digest algorithms, and `serde::Serialize`. It is invoked by `nydus-image stat`, which handles selecting a single bootstrap, scanning a blob directory, and optionally loading a target bootstrap.

## Risks
Histogram indexes depend on bit-length calculations and fixed bucket lengths; unusual very large files are clamped to bucket 44. Hardlink suppression is by inode number within a bootstrap, so cross-bootstrap identity is not considered. Errors from `node.chunk_count` are logged but do not fail the stat command. Directory scanning in the caller treats extensionless files as bootstraps and ignores failures at debug level, which can hide skipped images.

## Test Signals
There are no unit tests in this file. Useful signals are `nydus-image stat --bootstrap`, `--blob-dir` with multiple bootstraps, `--target` dedup comparison, JSON serialization shape, hardlink fixtures, and images with mixed chunk sizes.
