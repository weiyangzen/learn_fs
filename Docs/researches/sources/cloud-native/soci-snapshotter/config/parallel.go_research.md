## sources/cloud-native/soci-snapshotter/config/parallel.go

Purpose: configuration model and parser for parallel pull/unpack concurrency and decompression.

Important APIs/types/functions: `DecompressStream`, `ParallelConfig`, `defaultParallelConfig`, `parseParallelConfig`, and `parseSize`.

Control flow: parser converts `ConcurrentDownloadChunkSizeStr` into bytes. `parseSize` accepts B/KB/MB/GB units, decimals, whitespace, and zero-as-default.

State and persistence: none directly; parsed values guide runtime semaphores and chunked network reads.

Dependencies and integration: embedded in `PullModes.Parallel`, used by adaptive fetch/unpack job manager.

Risks and test signals: `parseSize` regex rejects negative values before numeric parsing, so the "negative" test expects an error rather than a negative value. Tests cover accepted units and invalid strings.
