# subset-b-000262 Research

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/overlaybd/src/overlaybd/cache/ocf_cache/ease_bindings/provider.h -->
# sources/cloud-native/overlaybd/src/overlaybd/cache/ocf_cache/ease_bindings/provider.h

## Purpose
Declares the C++ wrapper that owns an Open CAS Framework context, cache, core, queues, volume configuration, and read path for OverlayBD's OCF-backed cache filesystem.

## Important APIs, Types, And Functions
`ease_ocf_provider` exposes `start`, `stop`, `ocf_pread`, and `prefetch_unit`. It publishes `SectorSize` and keeps OCF identifiers for cache/core names and UUIDs. The private `alignment` struct plus `prepare_aligned_iov` and `copy_aligned_iov` support sector-aligned submissions for unaligned caller reads.

## Control Flow
Callers construct the provider with `ease_ocf_volume_params` and a prefetch size, call `start(reload_media)` to initialize OCF, and then call `ocf_pread` with a logical file offset plus namespace block base. Reads may be aligned with padding before submission to OCF and copied back afterward.

## State And Persistence
State is process-local OCF handles plus externally owned cache media parameters. Persistent cache media and namespace metadata are managed through the volume and namespace layers, not in this header.

## Dependencies And Integration Points
Includes Photon filesystem and `IOVector`, local OCF context/queue/volume bindings, and `OcfSrcFileCtx`. It is used by `ocf_cache.cpp` as the cache engine behind a Photon `IFileSystem`.

## Risks And Test Signals
The header documents that callers must avoid EOF-overrun reads; `OcfTruncateFile` in `ocf_cache.cpp` is the main guard. Alignment code depends on 512-byte sectors while cache line size is independently configured. Manual/perf coverage comes from `ocf_perf_test.cpp`; source size reviewed: 77 lines.
<!-- END_FILE_RESEARCH: sources/cloud-native/overlaybd/src/overlaybd/cache/ocf_cache/ease_bindings/provider.h -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/overlaybd/src/overlaybd/cache/ocf_cache/ease_bindings/queue.cpp -->
# sources/cloud-native/overlaybd/src/overlaybd/cache/ocf_cache/ease_bindings/queue.cpp

## Purpose
Implements OCF queue callbacks by mapping OCF queue kicks onto Photon threads or Photon work pools.

## Important APIs, Types, And Functions
Defines `QueueKicker`, `init_queues`, `queue_thread_kick`, `queue_thread_stop`, static `queue_ops`, and `get_queue_ops`.

## Control Flow
OCF calls the queue ops `kick`; the private `QueueKicker` runs `ocf_queue_run` either through a configured `photon::WorkPool` or a newly created Photon thread. `init_queues` installs one management kicker and one IO kicker, with different worker counts and Photon event/IO engines. The stop callback deletes the kicker stored in OCF queue private data.

## State And Persistence
State is transient queue-private `QueueKicker` objects. There is no durable state; queue lifetimes must match OCF cache/provider lifetimes.

## Dependencies And Integration Points
Depends on OCF queue APIs and Photon thread/workpool initialization constants. It is called from `ease_ocf_provider::start` after OCF queue creation.

## Risks And Test Signals
`QueueKicker::kick` captures `this` in a heap-allocated lambda for async work; stop must not race with queued callbacks. WorkPool initialization choices couple OCF IO to libcurl/epoll. Coverage is indirect through OCF cache startup and `ocf_perf_test`; source size reviewed: 70 lines.
<!-- END_FILE_RESEARCH: sources/cloud-native/overlaybd/src/overlaybd/cache/ocf_cache/ease_bindings/queue.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/overlaybd/src/overlaybd/cache/ocf_cache/ease_bindings/queue.h -->
# sources/cloud-native/overlaybd/src/overlaybd/cache/ocf_cache/ease_bindings/queue.h

## Purpose
Declares the queue binding surface used to plug Photon execution into OCF queue operations.

## Important APIs, Types, And Functions
Exports `init_queues(ocf_queue_t mngt_queue, ocf_queue_t io_queue)` and `get_queue_ops()`.

## Control Flow
Provider startup obtains queue ops through this header, creates OCF queues, and then initializes their queue-private kickers.

## State And Persistence
The header owns no state. Queue-private state is implemented in `queue.cpp`.

## Dependencies And Integration Points
Includes the C OCF headers inside `extern "C"`, making the wrapper callable from C++ OCF binding code.

## Risks And Test Signals
The narrow API hides ownership details; callers must pair queue creation and provider cleanup correctly. Test signal is indirect cache initialization. Source size reviewed: 9 lines.
<!-- END_FILE_RESEARCH: sources/cloud-native/overlaybd/src/overlaybd/cache/ocf_cache/ease_bindings/queue.h -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/overlaybd/src/overlaybd/cache/ocf_cache/ease_bindings/volume.cpp -->
# sources/cloud-native/overlaybd/src/overlaybd/cache/ocf_cache/ease_bindings/volume.cpp

## Purpose
Implements the OCF volume type that backs both cache-device IO and core/source-file IO with Photon `IFile` operations.

## Important APIs, Types, And Functions
Defines internal `ease_ocf_volume_io` and `ease_ocf_volume`, `volume_open`, `volume_submit_io`, flush/discard no-op completions, `volume_get_length`, volume data accessors, static `volume_properties`, `volume_init`, and `volume_cleanup`.

## Control Flow
OCF volume open stores UUID and optional cache params. For cache UUIDs, IO is dispatched as `preadv`/`pwritev` to `media_file` at OCF address. For core UUIDs, reads are translated from global cache namespace address to source-file offset, optionally trigger asynchronous prefetch, then read from `OcfSrcFileCtx::src_file`. Writes to core return `ENOSYS`.

## State And Persistence
Cache IO persists to the media file. Core IO reads source files only. Volume-private data stores UUID and cache params; IO-private data stores caller iovecs, OCF offset adjustment, source context, and error state.

## Dependencies And Integration Points
Depends on Photon IO allocation, logging/audit, `IOVector`, OCF volume registration, `ease_ocf_provider`, and `OcfSrcFileCtx`. It is the storage adapter OCF uses for cache and backing core volumes.

## Risks And Test Signals
Core reads reject nonzero data offset and null source context as internal bugs. EOF is treated as invalid because upper layers should truncate reads before OCF. Prefetch spawns a detached Photon thread and ignores useful return data, so failures are logged but do not directly fail the foreground read. Source size reviewed: 210 lines; exercised by OCF perf/manual tests.
<!-- END_FILE_RESEARCH: sources/cloud-native/overlaybd/src/overlaybd/cache/ocf_cache/ease_bindings/volume.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/overlaybd/src/overlaybd/cache/ocf_cache/ease_bindings/volume.h -->
# sources/cloud-native/overlaybd/src/overlaybd/cache/ocf_cache/ease_bindings/volume.h

## Purpose
Declares the OCF volume type ID, cache media parameter bundle, and volume registration helpers.

## Important APIs, Types, And Functions
`ease_ocf_volume_params` carries cache line/block size, media file size, Photon media file pointer, and logging flag. `volume_init` registers `EASE_OCF_VOLUME_TYPE`; `volume_cleanup` unregisters it.

## Control Flow
Provider startup fills `ease_ocf_volume_params`, registers this volume type with the OCF context, and passes the params as cache-device volume params.

## State And Persistence
The struct points at externally owned cache media. `enable_logging` is mutable runtime state toggled by provider start/stop.

## Dependencies And Integration Points
Includes Photon `IFile` and C OCF headers. Used by `provider.cpp` and `volume.cpp`.

## Risks And Test Signals
The struct does not own `media_file`, so lifetime is controlled by the cache filesystem. Invalid `blk_size` is caught in namespace/provider initialization. Source size reviewed: 20 lines.
<!-- END_FILE_RESEARCH: sources/cloud-native/overlaybd/src/overlaybd/cache/ocf_cache/ease_bindings/volume.h -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/overlaybd/src/overlaybd/cache/ocf_cache/ocf_cache.cpp -->
# sources/cloud-native/overlaybd/src/overlaybd/cache/ocf_cache/ocf_cache.cpp

## Purpose
Builds a Photon `IFileSystem` adapter that caches reads through Open CAS Framework while preserving source-file EOF semantics.

## Important APIs, Types, And Functions
Defines `OcfTruncateFile`, `OcfCachedFile`, `OcfCachedFs`, and public factory `FileSystem::new_ocf_cached_fs`.

## Control Flow
Factory creates and initializes an `OcfNamespace`, then constructs `OcfCachedFs`. `OcfCachedFs::init` validates prefetch alignment, sets global OCF allocator, derives media size, creates `ease_ocf_provider`, and starts or reloads the cache. `open` resolves source file namespace metadata through an object pool and returns an `OcfTruncateFile` wrapping an `OcfCachedFile`. Reads go `OcfTruncateFile` EOF clamp -> `OcfCachedFile::pread` -> `OcfCachedFs::ocf_pread` -> provider.

## State And Persistence
Persists cached blocks in `media_file` and file namespace mappings in the namespace filesystem. Keeps pooled `OcfSrcFileCtx` objects keyed by path. Destructor stops provider and frees namespace/params/provider ownership.

## Dependencies And Integration Points
Depends on Photon filesystem adapters, `ObjectCache`, `IOAlloc`, OCF namespace, and ease OCF bindings. Exposes the cache through `cache.h` factory conventions.

## Risks And Test Signals
Only open/read/fadvise/fstat/vioctl paths are implemented; most filesystem mutations return unimplemented. `OcfCachedFile` destructor releases by pathname, so pooling correctness depends on path consistency. `fadvise(POSIX_FADV_WILLNEED)` performs a real read into allocated memory. Source size reviewed: 295 lines; performance/manual coverage is `ocf_perf_test`.
<!-- END_FILE_RESEARCH: sources/cloud-native/overlaybd/src/overlaybd/cache/ocf_cache/ocf_cache.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/overlaybd/src/overlaybd/cache/ocf_cache/ocf_namespace.cpp -->
# sources/cloud-native/overlaybd/src/overlaybd/cache/ocf_cache/ocf_namespace.cpp

## Purpose
Implements a filesystem-backed namespace that assigns every source path a stable block-index range in the global OCF core address space.

## Important APIs, Types, And Functions
`OcfNamespaceOnFs` implements `init` and `locate_file`. Private helpers include `get_ns_info`, `append_ns`, and `write_ns_info`. Namespace files store `NsFileFormat` with magic, CRC32C checksum, and `NsInfo`.

## Control Flow
`init` validates the OCF cache-line/block size, walks existing namespace files, loads their mappings, and computes the next free block index. `locate_file` loads existing mapping if present; otherwise it stats the source file and appends a new namespace entry under a mutex. Writes go to `path.tmp` and are atomically renamed.

## State And Persistence
Persists namespace records in `m_fs`, one source-path-shaped record per file. In-memory `m_total_blocks` tracks the append frontier. The namespace file's CRC guards corruption of `NsInfo`.

## Dependencies And Integration Points
Uses Photon filesystem walking/path helpers, mutex, localfs, CRC32C from zfile, and OCF cache-line constants. Called from `OcfCachedFs::open`.

## Risks And Test Signals
`init` computes total blocks by the maximum starting block plus that file's size; corrupted or missing namespace files fail startup/open. Concurrent append is serialized only within one process. Source file growth after namespace creation is not represented unless a new namespace is written. Source size reviewed: 178 lines.
<!-- END_FILE_RESEARCH: sources/cloud-native/overlaybd/src/overlaybd/cache/ocf_cache/ocf_namespace.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/overlaybd/src/overlaybd/cache/ocf_cache/ocf_namespace.h -->
# sources/cloud-native/overlaybd/src/overlaybd/cache/ocf_cache/ocf_namespace.h

## Purpose
Declares the abstract namespace service used by OCF cache to map individual source files into one cache-core logical address space.

## Important APIs, Types, And Functions
`OcfNamespace` exposes `init`, `locate_file`, `block_size`, and nested `NsInfo { blk_idx, file_size }`. Factories declare filesystem-backed and RocksDB-backed namespace implementations.

## Control Flow
Consumers initialize the namespace once, then call `locate_file` per opened source path to get its base block index and file size.

## State And Persistence
The base class stores only configured block size. Persistence is implementation-specific; the filesystem implementation writes checked namespace files.

## Dependencies And Integration Points
Extends Photon `Object` and uses Photon `IFile`, `estring`, and callbacks. Integrated by `ocf_cache.cpp`.

## Risks And Test Signals
The RocksDB factory is declared here but not implemented in this subset. `NsInfo` size and checksum are part of the persisted format, so ABI changes affect compatibility. Source size reviewed: 46 lines.
<!-- END_FILE_RESEARCH: sources/cloud-native/overlaybd/src/overlaybd/cache/ocf_cache/ocf_namespace.h -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/overlaybd/src/overlaybd/cache/ocf_cache/test/CMakeLists.txt -->
# sources/cloud-native/overlaybd/src/overlaybd/cache/ocf_cache/test/CMakeLists.txt

## Purpose
Builds and registers the OCF cache performance/manual test executable.

## Important APIs, Types, And Functions
Creates `ocf_perf_test` from `ocf_perf_test.cpp`, adds include paths for CURL/Photon, links gflags, pthread, CURL, `photon_static`, and `overlaybd_lib`, and registers a CTest entry.

## Control Flow
CTest runs the executable with `--ut_pass=true`, making CI validate build/link/startup path without executing the heavy manual benchmark.

## State And Persistence
No runtime state in the CMake file. The executable itself writes temporary cache/media files depending on flags.

## Dependencies And Integration Points
Requires `GFLAGS` environment paths and `find_package(CURL)`. Integrates test target with the OCF cache library through `overlaybd_lib`.

## Risks And Test Signals
The registered test is intentionally shallow; it passes directly with `ut_pass`. Real OCF behavior requires manual invocation with `flags.conf`. Source size reviewed: 21 lines.
<!-- END_FILE_RESEARCH: sources/cloud-native/overlaybd/src/overlaybd/cache/ocf_cache/test/CMakeLists.txt -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/overlaybd/src/overlaybd/cache/ocf_cache/test/flags.conf -->
# sources/cloud-native/overlaybd/src/overlaybd/cache/ocf_cache/test/flags.conf

## Purpose
Provides sample gflags for running the OCF performance test manually.

## Important APIs, Types, And Functions
Configures single-file OCF cache mode, 8192-byte page/cache line size, libaio IO engine, 32-way concurrency, 2 GiB media file, no prefetch, random reads, source/destination paths, request limit, and multi-file parameters.

## Control Flow
The file is consumed by gflags-compatible invocation rather than C++ code directly. It selects single-file random-read benchmark behavior by default.

## State And Persistence
References `/root/cache-bench/media` and `/root/cache-bench/src`, so runs can create or reuse cache media and source data under that directory.

## Dependencies And Integration Points
Matches flags defined in `ocf_perf_test.cpp`.

## Risks And Test Signals
Paths and large media size are host-specific and unsuitable for ordinary CI. The file is useful as a reproducibility hint for manual benchmarks. Source size reviewed: 15 lines.
<!-- END_FILE_RESEARCH: sources/cloud-native/overlaybd/src/overlaybd/cache/ocf_cache/test/flags.conf -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/overlaybd/src/overlaybd/cache/ocf_cache/test/ocf_perf_test.cpp -->
# sources/cloud-native/overlaybd/src/overlaybd/cache/ocf_cache/test/ocf_perf_test.cpp

## Purpose
Implements a manual benchmark and correctness harness comparing OCF cache and full-file cache behavior for single-file and multi-file read workloads.

## Important APIs, Types, And Functions
Defines gflags for cache type, page size, media file, IO engine, concurrency, prefetch, source/destination, total requests, and multi-file generation. Core helpers include `random_read`, `sequential_read`, `work`, `single_file_ocf_cache`, `single_file_file_cache`, `prepare_copied_fs`, `crc_read`, and `multiple_files_test`.

## Control Flow
`main` parses flags, optionally exits on `ut_pass`, initializes Photon, creates a pooled allocator, and runs single- or multi-file mode. Single-file mode opens the selected cache filesystem and launches concurrent read loops with QPS reporting. Multi-file mode creates random data files, copies them to source, builds an OCF cache filesystem, opens all cached and reference files, then repeatedly compares CRC32C per random page.

## State And Persistence
Creates source, copied, namespace, destination, and media files under the selected root. Reuses existing media and copied files when present. Can drop host page cache through `system("echo 3 > /proc/sys/vm/drop_caches")`.

## Dependencies And Integration Points
Uses gflags, Photon threading/filesystems/net curl init paths, OverlayBD full-file and OCF cache factories, CRC32C, and global Photon allocator conventions.

## Risks And Test Signals
This is not a hermetic unit test: it depends on host paths, privileges, `/dev/urandom`, shell commands, large files, and manual stop/limits. It is valuable for throughput and data-integrity signals, especially OCF random/multi-file CRC checks. Source size reviewed: 508 lines.
<!-- END_FILE_RESEARCH: sources/cloud-native/overlaybd/src/overlaybd/cache/ocf_cache/test/ocf_perf_test.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/overlaybd/src/overlaybd/cache/policy/lru.h -->
# sources/cloud-native/overlaybd/src/overlaybd/cache/policy/lru.h

## Purpose
Provides a compact, generic LRU container optimized for cache eviction metadata.

## Important APIs, Types, And Functions
Template `FileSystem::LRU<ValueType, KeyType>` exports `push_front`, `access`, `mark_key_cleared`, `remove`, `pop_back`, `front`, `back`, `size`, and `empty`. Internal `Record` stores prev/next links plus value in a vector-backed ring.

## Control Flow
Construction creates a dummy list head. New entries allocate from a free ring or append to the vector, then become most-recent. `access` moves an entry to the head. `back` selects the least-recent real entry. `remove` detaches an entry and adds it to the free ring.

## State And Persistence
All state is in memory: vector records, a free-list pointer, logical size, and current head. No persistence or synchronization.

## Dependencies And Integration Points
Uses only standard C++ headers and lives in `FileSystem` namespace for cache policy use.

## Risks And Test Signals
Default `uint16_t` keys cap capacity below 64K records and all safety is via asserts. `mark_key_cleared` removes without reducing `m_size`, so callers must understand its special eviction semantics. No direct tests in this subset. Source size reviewed: 147 lines.
<!-- END_FILE_RESEARCH: sources/cloud-native/overlaybd/src/overlaybd/cache/policy/lru.h -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/overlaybd/src/overlaybd/cache/pool_store.h -->
# sources/cloud-native/overlaybd/src/overlaybd/cache/pool_store.h

## Purpose
Declares the generic cache pool/store interfaces used by OverlayBD cache filesystems for read-through refill, eviction, quotas, pinning, and transformed store keys.

## Important APIs, Types, And Functions
Defines `ListType`, reset/resize flags, `CacheFnTransFunc`, `CacheStat`, `ICachePool`, `ICacheStore`, `IMemCacheStore`, and `IMemCachePool`. `ICachePool` opens stores, manages quotas/stat/eviction/list/reset/resize, and tracks refill concurrency. `ICacheStore` exposes cached read/write/refill, query, eviction, source-file setup, size and allocator configuration.

## Control Flow
Cache filesystems open an `ICacheStore` through a pool; reads call `preadv2`, which checks cached ranges, opens source on miss, refills missing data, and returns user data. Writes go through `pwritev2` and may extend cache state depending on open flags.

## State And Persistence
Pool state includes open-store registry, optional thread pool/vCPU, refill counters, and filename transform callback. Store state includes source/store names, source file pointer, source filesystem, cached/actual sizes, page size, allocator, refcount, and range lock.

## Dependencies And Integration Points
Uses Photon filesystem/object/range-lock/iovec primitives and cache flags from `cache.h`. Implemented by `store.cpp` and concrete cache backends.

## Risks And Test Signals
Ownership is manual through `release` and source file setters. `O_CACHE_ONLY` and write-through/write-back flags change source-open behavior. Refill range correctness depends on concrete `queryRefillRange`, `do_preadv2`, and `do_pwritev2`. Tested indirectly in `cache_test.cpp`. Source size reviewed: 290 lines.
<!-- END_FILE_RESEARCH: sources/cloud-native/overlaybd/src/overlaybd/cache/pool_store.h -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/overlaybd/src/overlaybd/cache/store.cpp -->
# sources/cloud-native/overlaybd/src/overlaybd/cache/store.cpp

## Purpose
Implements shared `ICacheStore` read-through, write-through/cache-only, source-open, refill, and size-management logic.

## Important APIs, Types, And Functions
Implements destructor, `preadv2`, `pwritev2`, `try_refill_range`, `async_refill`, `do_refill_range`, `set_cached_size`, `try_preadv2`, mutable wrapper methods, `open_src_file`, `pwritev2_extend`, and `tryget_size`.

## Control Flow
`preadv2` validates range, clamps EOF, checks cache hit through `try_preadv2`, handles cache-only failure, opens source on miss, and refills the missing range. `do_refill_range` range-locks the refill span, reads source into an allocated buffer, copies overlapping bytes into the caller buffer, then writes cache synchronously or via pool async worker. `pwritev2` enforces page alignment and delegates to direct cache writes or append/extend mode.

## State And Persistence
Persists cached data through concrete `do_pwritev2`; reads source data through `src_file_`. Maintains `cached_size_`, `actual_size_`, source file pointer, refill lock, and async refill refcounts.

## Dependencies And Integration Points
Uses `pool_store.h`, Photon audit/logging, IO allocator, IOVector, range lock, and optional Photon thread pool on the owning `ICachePool`.

## Risks And Test Signals
Refill is sensitive to races, partial reads, ENOSPC, and async lifetime; range locks are released by async worker after write. If the pool's refill threshold is exceeded, reads bypass cache and go directly to source. Alignment requirements differ between normal and extending writes. `cache_test.cpp` covers EOF, refill, eviction, and pressure scenarios. Source size reviewed: 427 lines.
<!-- END_FILE_RESEARCH: sources/cloud-native/overlaybd/src/overlaybd/cache/store.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/overlaybd/src/overlaybd/cache/test/CMakeLists.txt -->
# sources/cloud-native/overlaybd/src/overlaybd/cache/test/CMakeLists.txt

## Purpose
Builds and registers the generic cache unit test executable.

## Important APIs, Types, And Functions
Adds gflags/gtest include and link directories, creates `cache_test` from `cache_test.cpp`, links gtest, gflags, pthread, `photon_static`, and `overlaybd_lib`, and registers it with CTest.

## Control Flow
CTest invokes the built `cache_test` binary directly.

## State And Persistence
No persistent state in CMake; tests write under `/tmp/ease/cache`.

## Dependencies And Integration Points
Requires environment-provided `GFLAGS` and `GTEST` paths and Photon include settings.

## Risks And Test Signals
The test target is more substantive than the OCF perf target but depends on local filesystem and libaio support. Source size reviewed: 13 lines.
<!-- END_FILE_RESEARCH: sources/cloud-native/overlaybd/src/overlaybd/cache/test/CMakeLists.txt -->

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

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/overlaybd/src/overlaybd/cache/test/random_generator.h -->
# sources/cloud-native/overlaybd/src/overlaybd/cache/test/random_generator.h

## Purpose
Defines small deterministic random generators used by cache tests.

## Important APIs, Types, And Functions
`RandomValueGen<T>` is the abstract base. `UniformInt32RandomGen` wraps `std::mt19937` and inclusive `uniform_int_distribution<uint32_t>`, with `seed`. `UniformCharRandomGen` generates unsigned-char values.

## Control Flow
Tests construct generators with fixed default seed `1213`, then call `next()` to fill source data and choose random offsets/sizes.

## State And Persistence
State is in-memory PRNG engine and distribution object only.

## Dependencies And Integration Points
Used by `cache_test.cpp`; depends on C++ `<random>` and `<algorithm>`.

## Risks And Test Signals
Deterministic default seed is good for reproducibility. `UniformCharRandomGen::next` does not use `override` despite inheriting from `RandomValueGen<unsigned char>`, but the signature matches. Source size reviewed: 58 lines.
<!-- END_FILE_RESEARCH: sources/cloud-native/overlaybd/src/overlaybd/cache/test/random_generator.h -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/overlaybd/src/overlaybd/config_util.h -->
# sources/cloud-native/overlaybd/src/overlaybd/config_util.h

## Purpose
Provides a RapidJSON-based configuration wrapper and template accessors for typed JSON pointer reads and recursive merging.

## Important APIs, Types, And Functions
Defines aliases for RapidJSON `Document`, `Value`, arrays/objects, enum `FORMAT`, class `Config`, `is_vector`, overloaded `GetResult`, and macros `APPCFG_CLASS` and `APPCFG_PARA`.

## Control Flow
`Config` can parse JSON files or strings, pretty-print itself, and merge another JSON value recursively: object-object conflicts merge recursively, otherwise the right-hand value replaces the left. `GetResult` overloads return scalar values, document subtrees, scalar vectors, or document vectors by RapidJSON pointer path.

## State And Persistence
Reads configuration from files or strings into RapidJSON DOM state. Does not write files; `DumpString` serializes to memory.

## Dependencies And Integration Points
Depends on RapidJSON file streams/pointers/writers and Photon logging/DEFER utility. Macros support application config classes that expose typed getters.

## Risks And Test Signals
Constructor accepts `FORMAT` but always calls `ParseJSON`, so YAML/INI are not implemented. Scalar `GetResult` assumes RapidJSON type matches `T`; mismatches can assert. Vector overloads assume path exists and is an array. Source size reviewed: 185 lines; no direct tests in this subset.
<!-- END_FILE_RESEARCH: sources/cloud-native/overlaybd/src/overlaybd/config_util.h -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/overlaybd/src/overlaybd/gzindex/CMakeLists.txt -->
# sources/cloud-native/overlaybd/src/overlaybd/gzindex/CMakeLists.txt

## Purpose
Builds the gzip random-access index library and optionally its tests.

## Important APIs, Types, And Functions
Globs all `*.cpp` into static library `gzindex_lib`, includes Photon headers, links `photon_static`, and adds `test` when `BUILD_TESTING` is enabled.

## Control Flow
CMake configures library before descending to test directory.

## State And Persistence
No runtime state.

## Dependencies And Integration Points
Exports library used by gzip stream/index tests and other OverlayBD components needing `new_gzfile` or `create_gz_index`.

## Risks And Test Signals
`file(GLOB)` can miss new files until CMake reconfigure depending on generator behavior. Source size reviewed: 9 lines.
<!-- END_FILE_RESEARCH: sources/cloud-native/overlaybd/src/overlaybd/gzindex/CMakeLists.txt -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/overlaybd/src/overlaybd/gzindex/gzfile.cpp -->
# sources/cloud-native/overlaybd/src/overlaybd/gzindex/gzfile.cpp

## Purpose
Implements a read-only random-access view of a gzip file using a separately generated index of deflate restart points and dictionaries.

## Important APIs, Types, And Functions
Defines internal `GzFile` with `pread`, `fstat`, `init`, `parse_index`, `seek_index`, `extract`, and `get_dict_by_index`. Exports `new_gzfile` and `is_gzfile`.

## Control Flow
First read or stat lazily initializes by reading and validating `IndexFileHeader`, checking CRC/magic/version/index size/gzip size, and parsing compressed or uncompressed `IndexEntry` array. `pread` finds the nearest index entry at or before requested decompressed offset, initializes raw deflate inflate state, primes partial bits if needed, loads the saved 32 KiB dictionary, skips bytes up to the requested offset, then fills the caller buffer.

## State And Persistence
State includes underlying gzip/index file pointers, parsed header, heap-owned vector of `IndexEntry*`, init mutex, and optional file ownership. Index file is read-only during normal use.

## Dependencies And Integration Points
Depends on zlib, Photon `VirtualReadOnlyFile`, Photon filesystem/stat APIs, CRC32C, and index format from `gzfile_index.h`. Used directly in gzindex tests and by gzip-cache integration.

## Risks And Test Signals
`pread` does not clamp count against uncompressed size itself; zlib stream end returns short reads. Index parsing allocates one entry per index point and destructor does not visibly free `index_` entries, implying a leak. `is_gzfile` changes file position and requires seekable input. Tests cover fixed, OOB, random, cached, and fstat reads. Source size reviewed: 381 lines.
<!-- END_FILE_RESEARCH: sources/cloud-native/overlaybd/src/overlaybd/gzindex/gzfile.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/overlaybd/src/overlaybd/gzindex/gzfile.h -->
# sources/cloud-native/overlaybd/src/overlaybd/gzindex/gzfile.h

## Purpose
Declares the public gzip-index API for creating random-access gzip file adapters and building index files.

## Important APIs, Types, And Functions
Exports `new_gzfile`, `create_gz_index`, and `is_gzfile`. Documents default chunk size and dictionary compression options.

## Control Flow
Consumers first create an index with `create_gz_index`, open gzip and index files, then wrap them with `new_gzfile` for `pread` support.

## State And Persistence
`create_gz_index` writes an index file; `new_gzfile` optionally owns the supplied file handles.

## Dependencies And Integration Points
Includes Photon filesystem and `gzfile_index.h`. Used by `gzip/gz.cpp` stream index save and `gzindex/test`.

## Risks And Test Signals
Ownership defaults to false, so caller lifetime management matters. Source size reviewed: 41 lines.
<!-- END_FILE_RESEARCH: sources/cloud-native/overlaybd/src/overlaybd/gzindex/gzfile.h -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/overlaybd/src/overlaybd/gzindex/gzfile_index.h -->
# sources/cloud-native/overlaybd/src/overlaybd/gzindex/gzfile_index.h

## Purpose
Defines the on-disk gzip index format, index entries, constants, and helper declarations shared by index creation, stream indexing, and indexed reads.

## Important APIs, Types, And Functions
Constants include `GZ_CHUNK_SIZE`, `GZ_DICT_COMPERSS_ALGO`, `WINSIZE`, and magic `ddgzidx`. `IndexFileHeader` stores version, dictionary compression, span/window, index sizing, gzip/uncompressed/index file sizes, offsets, and CRC. `IndexEntry` stores decompressed position, compressed position, dictionary position, bit prime count, and dictionary length. Declares `IndexFilterRecorder` helpers, header init, entry creation, and save routines.

## Control Flow
Index builders initialize a header, record entries while inflating gzip blocks, then serialize dictionaries and compressed index entries. Readers validate the header and use entries to restart inflate near a target offset.

## State And Persistence
This header defines the persisted packed ABI for `.gz_idx` files.

## Dependencies And Integration Points
Depends on zlib types, Photon `IFile`, and CRC32C. Shared by `gzfile.cpp`, `gzip_index_create.cpp`, and `gzip/gz.cpp`.

## Risks And Test Signals
Packed structs and `off_t` fields make cross-platform ABI/endian/word-size compatibility important. Misspelled macro `GZ_DICT_COMPERSS_ALGO` is part of the public header. Header CRC excludes only the trailing CRC field. Source size reviewed: 96 lines.
<!-- END_FILE_RESEARCH: sources/cloud-native/overlaybd/src/overlaybd/gzindex/gzfile_index.h -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/overlaybd/src/overlaybd/gzindex/gzip_index_create.cpp -->
# sources/cloud-native/overlaybd/src/overlaybd/gzindex/gzip_index_create.cpp

## Purpose
Builds gzip index files by scanning gzip streams, recording restartable deflate block positions and saved dictionaries.

## Important APIs, Types, And Functions
Implements `IndexFilterRecorder`, `zlib_compress`, `dict_compress`, `create_index_entry`, `new_index_filter`, `delete_index_filter`, `build_index`, `get_compressed_index`, `save_index_to_file`, `init_index_header`, and `create_gz_index`.

## Control Flow
`create_gz_index` validates dictionary compression options and span, creates/truncates index file, initializes header, inflates the gzip file with `inflateInit2(..., 47)` and `Z_BLOCK`, records entries when zlib reports block boundaries at or after span intervals, writes dictionary blobs as they are discovered, compresses and appends the final `IndexEntry` array, then writes the finalized header with CRC.

## State And Persistence
Writes a durable index file containing header, saved dictionaries, and compressed or raw entry array. In-memory `INDEX` owns heap `IndexEntry` pointers during creation.

## Dependencies And Integration Points
Uses zlib, Photon local file adapter, logging, and format declarations from `gzfile_index.h`. Stream indexing in `gzip/gz.cpp` reuses the recorder/save helpers.

## Risks And Test Signals
Index quality depends on zlib `data_type` block-boundary bits. Span below 64 KiB is rejected. `build_index` reads through sequential `read`, so caller file offset is consumed. Dictionary compression buffer assumes 64 KiB is enough for compressed 32 KiB dictionaries, which is safe for zlib overhead. Tested by `gzindex_test`. Source size reviewed: 386 lines.
<!-- END_FILE_RESEARCH: sources/cloud-native/overlaybd/src/overlaybd/gzindex/gzip_index_create.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/overlaybd/src/overlaybd/gzindex/test/CMakeLists.txt -->
# sources/cloud-native/overlaybd/src/overlaybd/gzindex/test/CMakeLists.txt

## Purpose
Builds and registers gzip index and gzip cache tests.

## Important APIs, Types, And Functions
Creates `gzindex_test` from `test.cpp`, links gtest/gflags/pthread, Photon, `gzindex_lib`, `gzip_lib`, `cache_lib`, and `checksum_lib`, and adds it as a CTest.

## Control Flow
CTest runs the executable with no extra flags.

## State And Persistence
No CMake runtime state; tests create files under `/tmp`.

## Dependencies And Integration Points
Requires gflags/gtest environment paths and all gzip/cache/checksum libraries.

## Risks And Test Signals
The linked test suite includes network-download stream tests, making it potentially slow/flaky if enabled in ordinary CI. Source size reviewed: 15 lines.
<!-- END_FILE_RESEARCH: sources/cloud-native/overlaybd/src/overlaybd/gzindex/test/CMakeLists.txt -->

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

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/overlaybd/src/overlaybd/gzip/CMakeLists.txt -->
# sources/cloud-native/overlaybd/src/overlaybd/gzip/CMakeLists.txt

## Purpose
Builds the gzip stream/adaptor library.

## Important APIs, Types, And Functions
Globs `*.cpp` into static library `gzip_lib`, includes Photon headers, and links `photon_static` plus `checksum_lib`.

## Control Flow
The test subdirectory is present but disabled in comments.

## State And Persistence
No runtime state.

## Dependencies And Integration Points
Library is consumed by gzindex tests and stream conversion paths needing `open_gzfile_adaptor` or `open_gzstream_file`.

## Risks And Test Signals
Test build is disabled here; coverage comes through `gzindex/test`. Source size reviewed: 11 lines.
<!-- END_FILE_RESEARCH: sources/cloud-native/overlaybd/src/overlaybd/gzip/CMakeLists.txt -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/overlaybd/src/overlaybd/gzip/gz.cpp -->
# sources/cloud-native/overlaybd/src/overlaybd/gzip/gz.cpp

## Purpose
Provides gzip read adapters: a simple zlib `gzFile` wrapper and a streaming gzip decompressor that can save a gzip index while reading from a Photon stream.

## Important APIs, Types, And Functions
Defines `GzAdaptorFile`, `GzStreamFile`, exported `open_gzfile_adaptor`, and `open_gzstream_file`. `GzStreamFile` implements `read`, `lseek`, `fstat`, `sha256_checksum`, and `save_index`.

## Control Flow
`GzAdaptorFile` delegates sequential reads/seeks to zlib `gzread/gzseek`. `GzStreamFile` reads compressed chunks from an `IStream`, validates gzip magic, inflates with `Z_BLOCK`, copies requested decompressed bytes to the caller, spills surplus decompressed bytes to a temporary buffer file, records index entries via `IndexFilterRecorder`, and later writes/renames the index using the stream SHA256.

## State And Persistence
Creates temporary buffer and index files under the workdir, tracks compressed/uncompressed offsets, zlib stream state, saved index entries, and optional SHA256 wrapper. Destructor deletes the buffer file and releases stream/index state. `save_index` persists the final `.gz_idx` file named from the checksum.

## Dependencies And Integration Points
Depends on zlib, Photon virtual files/localfs/subfs/socket streams, sha256 file wrapper, and gzindex helpers.

## Risks And Test Signals
`open_gzstream_file` ignores its `save_idx` parameter and always enables index save. `read` contains a fixed `assert(n + delta <= 65536)` even though callers can ask for larger counts. Temporary filenames use timestamp or UID and are unlinked on destructor. Covered indirectly by `gzindex/test` stream fixture. Source size reviewed: 297 lines.
<!-- END_FILE_RESEARCH: sources/cloud-native/overlaybd/src/overlaybd/gzip/gz.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/overlaybd/src/overlaybd/gzip/gz.h -->
# sources/cloud-native/overlaybd/src/overlaybd/gzip/gz.h

## Purpose
Declares gzip adapter APIs and the `IGzFile` interface for stream readers that can save generated indexes and report compressed-stream checksum.

## Important APIs, Types, And Functions
`IGzFile` extends Photon `VirtualReadOnlyFile` with `save_index` and `sha256_checksum`. Exports `open_gzfile_adaptor` and `open_gzstream_file`.

## Control Flow
Callers wrap either a filesystem gzip path or a Photon stream. Stream users read decompressed bytes and call `save_index` when complete.

## State And Persistence
The interface itself owns no state; implementations may create temporary files and persisted index outputs.

## Dependencies And Integration Points
Includes Photon filesystem/virtual-file and network socket stream types. Used by gzindex tests and stream conversion components.

## Risks And Test Signals
`open_gzstream_file` defaults `save_index=true` and workdir to current directory. Lifetime and stream ownership are implementation-defined. Source size reviewed: 33 lines.
<!-- END_FILE_RESEARCH: sources/cloud-native/overlaybd/src/overlaybd/gzip/gz.h -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/overlaybd/src/overlaybd/lsmt/CMakeLists.txt -->
# sources/cloud-native/overlaybd/src/overlaybd/lsmt/CMakeLists.txt

## Purpose
Builds the LSMT layer/image file library and optional tests.

## Important APIs, Types, And Functions
Globs `*.cpp` into static library `lsmt_lib`, includes Photon headers, and adds the `test` subdirectory when `BUILD_TESTING` is enabled.

## Control Flow
CMake creates the library before configuring tests.

## State And Persistence
No runtime state.

## Dependencies And Integration Points
Exports `lsmt_lib` for OverlayBD image/layer logic.

## Risks And Test Signals
`file(GLOB)` has reconfigure caveats. Test coverage is in `lsmt/test`, outside this work item. Source size reviewed: 10 lines.
<!-- END_FILE_RESEARCH: sources/cloud-native/overlaybd/src/overlaybd/lsmt/CMakeLists.txt -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/overlaybd/src/overlaybd/lsmt/file.cpp -->
# sources/cloud-native/overlaybd/src/overlaybd/lsmt/file.cpp

## Purpose
Implements OverlayBD LSMT layered file objects: read-only sealed layers, writable append-only layers, sparse writable layers, warp files with remote data mappings, stacking, compaction, sealing, and merge/open helpers.

## Important APIs, Types, And Functions
Key internal types are `HeaderTrailer`, `CompactOptions`, `LSMTReadOnlyFile`, `LSMTFile`, `LSMTSparseFile`, `LSMTWarpFile`, `parallel_load_task`, and many helpers including `write_header_trailer`, `compact`, `pcopy`, `load_layer_info`, `verify_ht`, `do_load_index`, `load_merge_index`, and `verify_order`. Exports `create_file_rw`, `open_file_rw`, `open_file_ro`, `open_files_ro`, `create_warpfile`, `open_warpfile_rw`, `open_warpfile_ro`, `merge_files_ro`, `stack_files`, `open_file_index`, `open_files_with_merged_index`, and `is_lsmt`.

## Control Flow
New RW files write headers to data/index files and insert mappings on aligned writes. Reads use `foreach_segments` over memory indexes, returning zero-filled holes and reading mapped data from tagged backing files. `close_seal` dumps the RW index into the data file and writes a sealed trailer. `commit`/`flatten` compact valid mappings into a new sealed file, writing header, live data, compressed index, and trailer. `open_file_ro`/`open_file_rw` validate headers/trailers and rebuild memory indexes. `open_files_ro` loads layer indexes in parallel, reverses to top-first order, and merges them. `stack_files` combines a writable upper layer with lower read-only layers via a combo index.

## State And Persistence
LSMT files persist 4 KiB headers/trailers, UUID/parent UUID/user tags, virtual size, data extents, discard mappings, and index arrays of 512-byte-sector `SegmentMapping`s. Runtime state includes memory indexes, backing file vectors, ownership flags, write mutex, group-commit buffer, current RW tag, compact counters, and virtual size.

## Dependencies And Integration Points
Uses Photon `IFile`/virtual file APIs, UUID, aligned memory helpers, Photon threads/mutexes, and index primitives from `index.h`. Provides the C API consumed by OverlayBD layer/image code.

## Risks And Test Signals
All read/write/discard operations require 512-byte alignment, and `set_max_io_size` requires 4 KiB alignment. Header/trailer packed ABI is compatibility-critical. `is_zero_block` currently returns `1` before its real scan, so compaction zero-detection is effectively disabled/incorrectly marked by the current code path. Parallel index loading mutates shared task state with minimal synchronization. Parent UUID order checks can reject invalid stacks. Tests are not in this subset but `lsmt/test` is enabled by CMake. Source size reviewed: 1969 lines.
<!-- END_FILE_RESEARCH: sources/cloud-native/overlaybd/src/overlaybd/lsmt/file.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/overlaybd/src/overlaybd/lsmt/file.h -->
# sources/cloud-native/overlaybd/src/overlaybd/lsmt/file.h

## Purpose
Declares the public LSMT file interfaces and constructors for OverlayBD layered image files.

## Important APIs, Types, And Functions
Defines constants `MAX_STACK_LAYERS`, `ALIGNMENT`, and `ALIGNMENT4K`; interfaces `IFileRO` and `IFileRW`; argument structs `CommitArgs`, `LayerInfo`, and `WarpFileArgs`; and exported C constructors/openers/mergers/stackers including `create_file_rw`, `open_file_rw`, `open_file_ro`, `open_files_ro`, `create_warpfile`, `open_warpfile_*`, `merge_files_ro`, `stack_files`, `open_file_index`, `open_files_with_merged_index`, and `is_lsmt`.

## Control Flow
Callers create or open RW layers, write aligned data/discards, optionally stack with RO layers, then seal or commit. RO callers open one or many sealed files and use `pread`, `seek_data`, `flatten`, and index access.

## State And Persistence
The header describes persistent layer inputs: data file, index file, sparse metadata, target/remote file, virtual size, UUIDs, parent UUID, and user tag. Runtime ownership can be transferred through `ownership` flags.

## Dependencies And Integration Points
Extends Photon virtual file interfaces and uses UUID plus LSMT memory index APIs. It is the stable C/C++ integration surface for LSMT layer files.

## Risks And Test Signals
Manual ownership and raw `IFile*` arrays make lifetime discipline important. `CommitArgs::user_tag` is capped by implementation at 256 bytes. `RemoteData` and `GetType` ioctl request values are part of the integration contract. Source size reviewed: 195 lines.
<!-- END_FILE_RESEARCH: sources/cloud-native/overlaybd/src/overlaybd/lsmt/file.h -->
