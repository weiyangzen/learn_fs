# sources/cloud-native/stargz-snapshotter/fs/reader/reader.go

## Purpose
Implements the filesystem-facing reader for an eStargz blob. It bridges `metadata.Reader`, a blob cache, digest verification, metrics, on-demand chunk reads, bulk caching, and optional whole-file passthrough file descriptor retrieval.

## Important APIs, Types, And Functions
`Reader` exposes `OpenFile`, `Metadata`, `Close`, and `LastOnDemandReadTime`. `VerifiableReader` wraps a `reader` until callers choose `VerifyTOC` or `SkipVerify`; `VerifyTOC` validates the TOC digest and enables per-chunk digest verification. `Cache` walks regular files and caches chunks concurrently. `file.ReadAt` is the primary lazy-read path, while `GetPassthroughFd`, `prefetchEntireFile`, `prefetchEntireFileSequential`, `processBatchChunks`, and `checkHoles` build a full-file cache object for passthrough FUSE use.

## Control Flow
`NewReader` wires metadata, cache, layer digest, and verifier. `OpenFile` opens a metadata file with a preread callback that caches adjacent chunks if the estargz reader exposes them. `ReadAt` maps the request to chunk entries, tries chunk cache first, fetches/decompresses missing chunks through `metadata.File`, verifies if enabled, writes them into cache, and copies only the requested slice. Whole-file passthrough enumerates all chunks, chooses sequential mode if any chunk is larger than the merge buffer, otherwise processes chunks in parallel by batch and validates that the batch has no holes or overlaps before writing to cache.

## State And Persistence
State is in memory except for the supplied `cache.BlobCache`, which may be persistent depending on implementation. The reader tracks closed state, last on-demand read time, verification status, last verification error, and a pooled buffer. Cache keys are SHA-256 hashes of `id-offset-size`; whole-file passthrough uses `id-0-totalSize`.

## Dependencies And Integration
Depends on `metadata.Reader`/`File`, `cache.BlobCache`, `estargz` constants, OpenContainers digest verification, errgroup/semaphore concurrency, and common metrics counters. It is consumed by higher-level snapshot/FUSE code that needs metadata lookup plus chunk-backed `io.ReaderAt`.

## Risks And Test Signals
Important risks are stale or malformed metadata chunk entries, verification being skipped intentionally, cache writer commit/abort correctness, buffer sizing for passthrough, and concurrent batch reads producing gaps. Tests in `reader_test.go` and `testutil.go` cover compressed formats, cache hits/misses, verification timing, preread cache population, failed readers/verifiers, and batch hole detection.
