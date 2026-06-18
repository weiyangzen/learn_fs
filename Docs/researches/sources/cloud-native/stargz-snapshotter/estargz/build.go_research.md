# sources/cloud-native/stargz-snapshotter/estargz/build.go

Purpose: Builds optimized eStargz blobs from tar, gzip tar, or zstd tar input, with optional prioritized file ordering, chunk sizing, compression selection, context cancellation, and gzip helper decompression.

Important APIs/types: `GzipHelperFunc`, build `Option`s, `Blob`, `Build`, `closeWithCombine`, `sortEntries`, `importTar`, `moveRec`, `tarFile`, temp file helpers, `countReadSeeker`, and `decompressBlob`.

Control flow: `Build` applies options, selects compression, tracks temp files, handles context cleanup, decompresses input if needed, sorts entries with prefetch/no-prefetch landmarks, partitions entries across `GOMAXPROCS` unless `MinChunkSize` requires serial processing, writes sub-blobs in goroutines, combines TOCs with adjusted offsets, then streams payloads plus TOC/footer through an `io.Pipe` while computing diff ID and uncompressed size. `sortEntries` imports tar entries, moves prioritized paths and their parents/hardlink targets first, inserts a landmark, and appends the rest.

State and persistence: Uses temporary files for decompressed input and sub-blob payloads, removed on blob close or error. `Blob` tracks TOC digest, diffID, read-completion, and uncompressed size atomically.

Dependencies and integration: Core library used by native converters and command conversion paths. Depends on tar/gzip/zstd, digest, and writer implementation in `estargz.go`.

Risks: Callers must fully read before `UncompressedSize`. Parallel build uses temp disk proportional to layer size. Missing prioritized files are fatal unless explicitly allowed.

Test signals: `build_test.go` heavily tests sorting, landmarks, path normalization, hardlinks, duplicate entries, and count reader behavior.
