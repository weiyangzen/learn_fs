<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/overlaybd/src/overlaybd/gzindex/test/test.cpp -->
# sources/cloud-native/overlaybd/src/overlaybd/gzindex/test/test.cpp

## Purpose
Tests indexed gzip random reads, gzip-decompression cache integration, and stream-to-index generation over Unix-domain sockets.

## Important APIs, Types, And Functions
Defines `GzIndexTest`, `GzCacheTest`, `PreadTestCase`, gzip test-data builders, `download`, UDS server/client helpers, and tests for `stream`, `pread`, `pread_oob`, `pread_rand`, `cache_store`, `pread_little`, and `fstat`.

## Control Flow
Fixtures generate random uncompressed data, gzip-compress it, create an index, and compare `new_gzfile` reads against the original file. Cache fixture wraps gzip file behind full-file cache and decompressed gzip cache, then checks sparse cache-store contents. Stream test downloads real `.tar.gz` archives, sends compressed bytes over UDS, reads through `open_gzstream_file`, saves an index, and checks output SHA256.

## State And Persistence
Creates and removes files under `/tmp`, `/tmp/gzip_src`, `/tmp/gzip_cache_*`, `/tmp/gzstream_test`, and `/tmp/dest`. Performs network downloads in the stream test.

## Dependencies And Integration Points
Uses Photon init/network/socket/threading, zlib, gzip index API, gzip stream API, cache/gzip-cache factories, and sha256 helper.

## Risks And Test Signals
Network-dependent stream test can fail offline or when upstream artifacts change availability. Several buffers allocate by `new char[count]`, so huge random cases can be memory-sensitive. Provides strong random/OOB/fstat regression signals for indexed gzip and gzip cache. Source size reviewed: 666 lines.
<!-- END_FILE_RESEARCH: sources/cloud-native/overlaybd/src/overlaybd/gzindex/test/test.cpp -->
