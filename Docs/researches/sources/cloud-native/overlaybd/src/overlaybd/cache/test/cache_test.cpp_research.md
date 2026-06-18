<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/overlaybd/src/overlaybd/cache/test/cache_test.cpp -->
# sources/cloud-native/overlaybd/src/overlaybd/cache/test/cache_test.cpp

## Purpose
Provides GoogleTest coverage for OverlayBD full-file cache read/refill/eviction/xattr/pressure behavior.

## Important APIs, Types, And Functions
Defines `SetupTestDir`, `commonTest`, `worker`, and tests `RoCachedFs.Basic`, `BasicCacheFull`, `CacheWithOutSrcFile`, `RoCachedFS.xattr`, `CachedFS.write_while_full`, and `CachedFS.fn_trans_func`.

## Control Flow
`commonTest` creates source/cache filesystems, fills a large random source file plus unaligned tail, opens a cached file, validates first and repeated reads, explicit refill, eviction, fadvise prefetch, quota behavior, random aligned sections, small-file reads, and tail refill. Other tests cover cache without source, xattr forwarding, eviction while multiple workers read a huge file, and filename transformation causing two source paths to share one store key.

## State And Persistence
Creates and removes directories under `/tmp/ease/cache`, writes random data, cache media files, sparse/evicted files, and xattrs. Some tests shell out to `dd`, `mkdir`, and `cp`.

## Dependencies And Integration Points
Uses Photon local/aligned filesystems, libaio/fd event initialization, cache factories, `ICachedFile`, `ICachePool`, `IOAlloc`, and local random generator helper.

## Risks And Test Signals
Several buffers use `reserve` instead of `resize` before reading into `data()`, which is undefined in standard C++ even if it may pass in practice. Tests are host-dependent and can be heavy (`2 GiB` huge file). They provide strong behavioral signals for unaligned EOF, read-through refill, cache-only behavior, xattrs, eviction under pressure, and transformed dedupe. Source size reviewed: 558 lines.
<!-- END_FILE_RESEARCH: sources/cloud-native/overlaybd/src/overlaybd/cache/test/cache_test.cpp -->
