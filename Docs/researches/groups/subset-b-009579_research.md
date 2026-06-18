<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/internal/cache/metadata/stat_cache_test.go -->
# Research: sources/user-network-fs/gcsfuse/internal/cache/metadata/stat_cache_test.go

Purpose: validates the metadata stat cache bucket-view behavior for object entries, negative entries, folder entries, implicit directories, shared multi-bucket cache keys, expiration, and LRU eviction.

Important APIs/types/functions: `TestStatCache`, `testHelperCache`, `testMultiBucketCacheHelper`, `StatCacheTest`, `MultiBucketStatCacheTest`, and test cases around `Insert`, `InsertFolder`, `InsertImplicitDir`, `AddNegativeEntry`, `AddNegativeEntryForFolder`, `LookUp`, `LookUpFolder`, `EraseEntriesWithGivenPrefix`, and `NewStatCacheBucketView`.

Control flow: each suite creates an `lru.Cache` sized from `cfg.AverageSizeOfPositiveStatCacheEntry` and `cfg.AverageSizeOfNegativeStatCacheEntry`, wraps it as one or more bucket views, inserts entries with fixed expirations, and probes lookup results before, at, and after expiration. Multi-bucket tests use the same LRU backing cache with different bucket prefixes to prove same object names do not collide across bucket views.

State and persistence: all state is in-memory only. The tests deliberately mutate cache contents and LRU recency through lookup calls, so insertion order and access order are part of the asserted behavior. There is no disk persistence.

Dependencies and integration points: depends on `internal/cache/lru`, `internal/cache/metadata`, `internal/storage/gcs`, `cfg` cache sizing constants, `testify/suite`, and `assert`. These tests are direct unit coverage for metadata caching used by storage fast-stat layers and filesystem directory/type lookup paths.

Risks: many legacy cases exercise a helper wrapper instead of calling the production cache directly; the file comments call out that this weakens the safety net. Capacity assertions rely on approximate entry-size constants and could become brittle if cache-entry accounting changes. Expiration semantics are boundary-sensitive: entries are expected valid at exactly the expiration time and invalid after.

Test signals: strong coverage for generation/metageneration overwrite ordering, positive-negative replacement, folder negative entries, prefix erasure, implicit-directory compaction, implicit versus explicit precedence, and bucket-name isolation in a shared cache.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/internal/cache/metadata/stat_cache_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/internal/cache/metadata/type_cache.go -->
# Research: sources/user-network-fs/gcsfuse/internal/cache/metadata/type_cache.go

Purpose: implements a size-bounded, TTL-based LRU cache mapping inode names to coarse metadata types for directory lookups, including regular files, symlinks, explicit directories, implicit directories, nonexistent entries, and unknown state.

Important APIs/types/functions: `Type`, constants `UnknownType`, `SymlinkType`, `RegularFileType`, `ExplicitDirType`, `ImplicitDirType`, `NonexistentType`; `TypeCache` interface; `cacheEntry`; `cacheEntry.Size`; `SizeOfTypeCacheEntry`; concrete `typeCache`; `NewTypeCache`; `Insert`; `Erase`; and `Get`.

Control flow: `NewTypeCache` disables caching when TTL is zero or max size is zero, treats `maxSizeMB == -1` as effectively unlimited, otherwise constructs an `lru.Cache` in bytes. `Insert` stores a `cacheEntry` with expiry `now + ttl`; insertion errors panic because size accounting failures indicate an internal cache invariant problem. `Get` returns `UnknownType` when disabled, missing, or expired; expired entries are erased on access. Successful lookup updates LRU recency via `lru.LookUp`.

State and persistence: state is in-memory only and guarded externally; the type states are not persisted. Cache entries include a copied key string for heap/RSS size accounting. Expiration is lazy and depends on caller-provided time, usually the filesystem cache clock.

Dependencies and integration points: depends on `internal/cache/lru` and `internal/util` for MiB conversion and unsafe size accounting. Filesystem directory inodes use this cache to avoid repeated GCS type probes and to cache nonexistent names when configured.

Risks: external synchronization is required; misuse in concurrent paths can race. Size calculation is explicitly 64-bit Linux-specific and approximates RSS as a heap conversion factor. Lazy expiration means stale entries remain until looked up or evicted. Returning `UnknownType` conflates disabled, missing, and expired states.

Test signals: `type_cache_test.go` covers constructor disabling, overwrite behavior, TTL expiration, LRU size eviction, erase/reinsert, and disabled-cache behavior for zero size or zero TTL.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/internal/cache/metadata/type_cache.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/internal/cache/metadata/type_cache_test.go -->
# Research: sources/user-network-fs/gcsfuse/internal/cache/metadata/type_cache_test.go

Purpose: unit-tests the metadata type cache implementation, including constructor modes, TTL semantics, overwrite behavior, LRU capacity eviction, explicit erase, reinsert, and disabled-cache behavior.

Important APIs/types/functions: `TestTypeCache`, suites `TypeCacheTest`, `ZeroSizeTypeCacheTest`, `ZeroTtlTypeCacheTest`, helper `createNewTypeCache`, constants `TTL` and `TypeCacheMaxSizeMB`, and fixed timestamps `now`, `expiration`, `beforeExpiration`, and `afterExpiration`.

Control flow: the primary suite creates a one-MiB cache with millisecond TTL, inserts named entries, and calls `Get` at controlled times. The capacity test computes how many entries of a known key size fit, inserts one more than capacity, then verifies that the first entry is evicted while later entries remain. Separate suites construct caches with zero max size and zero TTL and assert that inserts never become observable.

State and persistence: all test state is in-memory. The tests rely on deterministic caller-supplied timestamps instead of wall-clock sleeps, so expiration behavior is repeatable.

Dependencies and integration points: uses `internal/util.MiBsToBytes`, ogletest assertions, and direct access to unexported `typeCache` internals because the test package is `metadata`. It validates the cache behavior that filesystem directory type lookups rely on.

Risks: the size-eviction test is sensitive to `cacheEntry.Size` and key length. The tests do not cover concurrent access, matching the production contract that external synchronization is required. Constructor tests inspect `entries == nil`, so internal representation changes would require updates even if public behavior remains stable.

Test signals: coverage confirms entries are valid before TTL expiration, invalid after expiration, overwritten entries return the last type, erased entries vanish, and disabled caches always return `UnknownType`.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/internal/cache/metadata/type_cache_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/internal/cache/util/util.go -->
# Research: sources/user-network-fs/gcsfuse/internal/cache/util/util.go

Purpose: provides low-level helpers and error sentinels for file-cache paths, cache directory creation, CRC computation, safe file deletion, memory-aligned buffers, and aligned copy behavior needed by direct-I/O cache writes.

Important APIs/types/functions: cache read error sentinels; constants `MiB`, `KiB`, `DefaultFilePerm`, `DefaultDirPerm`, `FileCache`, `SharedChunkCache`, `BufferSizeForCRC`; `CreateFile`; `GetObjectPath`; `GetDownloadPath`; `IsCacheHandleInvalid`; `CreateCacheDirectoryIfNotPresentAt`; `calculateCRC32`; `CalculateFileCRC32`; `TruncateAndRemoveFile`; `GetMemoryAlignedBuffer`; and `CopyUsingMemoryAlignedBuffer`.

Control flow: `CreateFile` creates parent directories, stats the target, adds `O_CREATE` only for missing files, and opens with requested flags and permissions. `CreateCacheDirectoryIfNotPresentAt` creates the cache directory if needed and verifies writability using `fsutil.AnonymousFile`. CRC calculation reads in 64 KiB chunks and checks context cancellation on each loop. `TruncateAndRemoveFile` truncates before removal so open file descriptors do not retain disk usage. `GetMemoryAlignedBuffer` overallocates and slices to an aligned address, retrying up to three times. `CopyUsingMemoryAlignedBuffer` validates buffer size, rounds each write size up to the configured minimum alignment, reads with `io.ReadFull`, writes padded buffers, and respects context cancellation.

State and persistence: helpers manipulate local filesystem state: cache directories, files, temp anonymous files, file contents, and deletion. There is no package-level mutable state.

Dependencies and integration points: used by file-cache creation in `internal/fs/fs.go`, downloader/cache handlers, direct-I/O sparse/chunk cache paths, and CRC validation. Depends on `cfg.CacheUtilMinimumAlignSizeForWriting`, `internal/cache/data.FileSpec`, `fsutil`, and standard filesystem APIs.

Risks: path joining uses `path` for object/cache paths and `filepath` for local parent directory creation; callers must pass platform-appropriate paths. `TruncateAndRemoveFile` returns an error for absent files. Aligned copy writes padded zero bytes and returns bytes written, not logical content bytes, which callers must interpret carefully. `unsafe` pointer alignment is platform-sensitive.

Test signals: `util_test.go` covers permissions, relative paths, sentinel error wrapping, CRC success/failure/cancellation, truncate-remove behavior with open handles, directory writability validation, alignment pointer checks, O_DIRECT offset behavior, padding, and cancellation.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/internal/cache/util/util.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/internal/cache/util/util_test.go -->
# Research: sources/user-network-fs/gcsfuse/internal/cache/util/util_test.go

Purpose: tests cache utility helpers for local file creation, path normalization, invalid-handle error classification, CRC calculation, truncating removal, cache-directory validation, memory alignment, and aligned copying for direct I/O.

Important APIs/types/functions: ogletest suite `utilTest`, helper `assertFileAndDirCreationWithGivenDirPerm`, tests for `CreateFile`, `GetDownloadPath`, `IsCacheHandleInvalid`, `CalculateFileCRC32`, `TruncateAndRemoveFile`, `CreateCacheDirectoryIfNotPresentAt`, `GetMemoryAlignedBuffer`, and `CopyUsingMemoryAlignedBuffer`.

Control flow: suite setup builds a `data.FileSpec` under the current user's home directory and removes prior test directories. `CreateFile` tests vary directory presence, permissions, open flags, file permissions, existing files, and relative paths. Standalone `testing` table tests create temp directories or random local files, optionally open with `syscall.O_DIRECT`, then assert write sizes and file contents after aligned copying.

State and persistence: creates and removes files/directories under the user's home directory, relative working directory, and random local test files. Tests inspect Unix owner/group and permission bits using `syscall.Stat_t`, so they are OS-sensitive.

Dependencies and integration points: depends on `operations.RemoveDir`, `internal/util.GenerateRandomBytes`, `testify`, ogletest, `syscall.O_DIRECT`, and `testdata/validfile.txt` plus `testdata/emptyfile.txt`. It validates filesystem behavior relied on by file cache setup and sparse/direct cache writing.

Risks: tests assume Unix permission semantics and may behave differently on non-Linux platforms or with unusual umask/filesystem behavior. O_DIRECT cases require alignment-sensitive local filesystem support. One test name says `Test_getObjectPath` but calls `GetDownloadPath`, so it may not directly cover `GetObjectPath`.

Test signals: broad coverage catches permission regressions, wrapped sentinel matching, context cancellation propagation, padding semantics for non-aligned content sizes, invalid buffer sizes, and invalid O_DIRECT write offsets.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/internal/cache/util/util_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/internal/canned/canned.go -->
# Research: sources/user-network-fs/gcsfuse/internal/canned/canned.go

Purpose: supplies a small fake GCS bucket with deterministic canned contents for tests and examples.

Important APIs/types/functions: constants `FakeBucketName`, `TopLevelFile`, `TopLevelFile_Contents`, `TopLevelDir`, `TopLevelDir_Contents`, `ExplicitDirFile`, `ExplicitDirFile_Contents`, `ImplicitDirFile`, `ImplicitDirFile_Contents`, and function `MakeFakeBucket`.

Control flow: `MakeFakeBucket` constructs a `fake.NewFakeBucket` with `timeutil.RealClock`, the intentionally invalid bucket name `fake@bucket`, and default `gcs.BucketType`. It then iterates over a map of object names to contents and creates each object with `CreateObject`. Any creation failure panics via `log.Panicf`, which is appropriate for fixture setup.

State and persistence: state is an in-memory fake bucket only. Contents include a top-level file, an explicit directory placeholder object, a file inside that explicit directory, and a file that implies a directory prefix without a placeholder.

Dependencies and integration points: depends on `internal/storage/fake`, `internal/storage/gcs`, `strings`, `timeutil`, and `context`. It is intended as helper code for tests that need standard object/directory layouts.

Risks: uses a Go map for setup ordering, but ordering should not matter because objects are independent. Panicking on setup error is convenient for tests but unsuitable for production. The bucket name is intentionally not a valid real GCS bucket name, preventing accidental use against real storage.

Test signals: no direct tests in this subset, but downstream filesystem tests use fake buckets with similar object layouts to validate explicit and implicit directory semantics.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/internal/canned/canned.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/internal/clock/clock.go -->
# Research: sources/user-network-fs/gcsfuse/internal/clock/clock.go

Purpose: defines a tiny clock abstraction for code that needs timer behavior and test substitution.

Important APIs/types/functions: `Clock` interface with one method, `After(d time.Duration) <-chan time.Time`.

Control flow: no implementation is present in this file; callers depend only on the `After` contract. Real and fake implementations live in sibling files.

State and persistence: no state and no persistence. Implementations decide whether time is real, delayed, or simulated.

Dependencies and integration points: depends only on `time`. `RealClock`, `FakeClock`, and `SimulatedClock` implement this interface. The abstraction is useful for retry/backoff or wait logic where unit tests should avoid sleeping.

Risks: the interface only abstracts `After`, not `Now`, timers, tickers, or cancellation; call sites needing current time use other clock abstractions such as `timeutil.Clock` elsewhere in gcsfuse. Because returned channels are receive-only, implementations must decide buffering and close behavior consistently enough for callers.

Test signals: `simulated_clock_test.go` validates the richest implementation. No direct test is needed for this interface file.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/internal/clock/clock.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/internal/clock/fake_clock.go -->
# Research: sources/user-network-fs/gcsfuse/internal/clock/fake_clock.go

Purpose: implements the `Clock` interface with a fixed real-time sleep duration for tests that need predictable shortened waits.

Important APIs/types/functions: `FakeClock` struct with `WaitTime time.Duration`, and method `After(time.Duration) <-chan time.Time`.

Control flow: `After` ignores the requested duration, creates an unbuffered channel, starts a goroutine, sleeps for `WaitTime`, and sends `time.Now()` on the channel.

State and persistence: state is only the configured `WaitTime`. There is no persistence and no tracking of outstanding timers beyond goroutines blocked on channel send.

Dependencies and integration points: depends on `time` and implements `Clock` from `clock.go`. It is appropriate for tests that need wait operations to complete faster than production, but still use wall-clock sleeping.

Risks: because the returned channel is unbuffered, the goroutine can remain blocked if the caller never receives. Ignoring the input duration is useful for tests but can hide bugs in code that relies on varying durations. It uses real wall-clock time, so tests using it can still be flaky under scheduler delays.

Test signals: no direct tests in this subset. `SimulatedClock` provides more deterministic timer test coverage and is preferable when exact scheduling semantics matter.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/internal/clock/fake_clock.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/internal/clock/real_clock.go -->
# Research: sources/user-network-fs/gcsfuse/internal/clock/real_clock.go

Purpose: production implementation of the local `Clock` interface backed by Go's wall-clock timer.

Important APIs/types/functions: `RealClock` empty struct and method `After(d time.Duration) <-chan time.Time`.

Control flow: `After` delegates directly to `time.After(d)` and returns its channel.

State and persistence: stateless wrapper; timer state is owned by the Go runtime. No persistence.

Dependencies and integration points: depends only on `time` and implements `Clock`. It is the natural production counterpart to `FakeClock` and `SimulatedClock` for code that depends on the package-local clock abstraction.

Risks: `time.After` allocates a timer that cannot be canceled by the caller through this interface. Repeated long-duration waits in loops can retain timers until they fire. This is a limitation of the minimal `Clock` interface rather than this wrapper specifically.

Test signals: no direct test in this subset; behavior is Go standard library behavior.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/internal/clock/real_clock.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/internal/clock/simulated_clock.go -->
# Research: sources/user-network-fs/gcsfuse/internal/clock/simulated_clock.go

Purpose: implements a deterministic, manually advanced clock for unit tests that need `After` behavior without sleeping.

Important APIs/types/functions: internal `afterRequest`, `SimulatedClock` with guarded fields `t` and `pending`, constructor `NewSimulatedClock`, methods `Now`, `SetTime`, `AdvanceTime`, `After`, and helper `processPending`.

Control flow: `Now` returns the guarded current simulated time. `SetTime` replaces the time and processes pending timers. `AdvanceTime` adds a duration and processes pending timers. `After` creates a buffered one-element channel, computes `targetTime = current + d`, immediately sends current time for non-positive durations, or appends a pending request. `processPending` scans requests and sends `targetTime` for each request whose target is reached, retaining only future requests.

State and persistence: state is in-memory and protected by `sync.RWMutex`. Pending requests are held until fired or until the clock is discarded. Channels are not closed, matching `time.After` behavior.

Dependencies and integration points: depends on `sync` and `time`, implements the package `Clock` interface, and adds `Now`/time-control methods for tests.

Risks: moving time backward with `SetTime` is allowed and can leave existing future timers pending longer in simulated time. There is no cancellation/removal API. Sending while holding the lock is safe because channels are buffered, but changing buffer behavior would risk deadlocks. Fired timer values are scheduled target times, while immediate non-positive durations send current time.

Test signals: `simulated_clock_test.go` covers `Now`, `SetTime`, positive/negative/zero advances, immediate timers, firing by set/advance past target, and non-firing before target.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/internal/clock/simulated_clock.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/internal/clock/simulated_clock_test.go -->
# Research: sources/user-network-fs/gcsfuse/internal/clock/simulated_clock_test.go

Purpose: validates deterministic behavior of `SimulatedClock` for current time mutation and timer firing.

Important APIs/types/functions: tests `TestSimulatedClock_Now`, `TestSimulatedClock_SetTime`, `TestSimulatedClock_AdvanceTime`, `TestSimulatedClock_After_ShouldFireZeroOrNegativeDuration`, `TestSimulatedClock_After_ShouldFirePositiveDuration`, and `TestSimulatedClock_After_ShouldNotFire`; timeout constants `shortTestTimeout` and `fireTestTimeout`.

Control flow: table-driven tests initialize a clock with a fixed UTC time, call setup actions, then assert `Now`. Timer tests call `After`, manipulate simulated time by `AdvanceTime` or `SetTime`, and select on the returned channel versus a short real-time timeout.

State and persistence: test state is in-memory. Real timers are used only as guard timeouts to prevent blocking tests.

Dependencies and integration points: uses `testify/assert` and `require`. It covers the clock implementation used by testable wait logic in the local `internal/clock` package.

Risks: real-time timeout constants are small; heavily loaded CI could theoretically cause false negatives in firing tests, though simulated firing itself is synchronous after clock mutation. The tests do not include concurrent access, multiple pending timers, or time moving backward with pending timers.

Test signals: confirms non-positive durations fire immediately with the current time, positive timers fire with the scheduled target time rather than the later current time, and timers do not fire before their target.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/internal/clock/simulated_clock_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/internal/contentcache/contentcache.go -->
# Research: sources/user-network-fs/gcsfuse/internal/contentcache/contentcache.go

Purpose: implements a disk-backed local content cache for GCS object bodies, with in-memory indexing and JSON checkpoint metadata so cache files can be recovered across process restarts.

Important APIs/types/functions: `CacheFilePrefix`, `CacheObjectKey`, `ContentCache`, `CacheFileObjectMetadata`, `CacheObject`, `ValidateGeneration`, `WriteMetadataCheckpointFile`, `Destroy`, `recoverFileFromCache`, `RecoverCache`, `matchPattern`, `New`, `NewTempFile`, `AddOrReplace`, `Get`, `Remove`, `NewCacheFile`, `recoverCacheFile`, and `Size`.

Control flow: `AddOrReplace` locks the cache, destroys any existing object for the key, creates a temp file under `tempDir`, wraps it as a cache file, writes a sibling JSON metadata checkpoint, stores a `CacheObject`, and returns it. `RecoverCache` defaults an empty temp dir to `/tmp`, scans directory entries, filters metadata filenames matching `gcsfusecache[0-9]+.json`, reads JSON, opens the referenced cache file, wraps it, and adds it to `fileMap`. `Remove` locks, destroys disk files and metadata, and deletes the map entry.

State and persistence: in-memory state is `fileMap` protected by a mutex. Persistent state is cache data files plus JSON metadata files storing bucket, object, generation, metageneration, and data filename. Cache validity is determined by generation/metageneration equality.

Dependencies and integration points: used by `fs.NewFileSystem` when `LocalFileCache` is enabled and by file inodes through `gcsx.TempFile`. Depends on `gcsx`, `logger`, `timeutil.Clock`, JSON, regexp, and local filesystem APIs.

Risks: recovery opens one descriptor per recovered file and has a TODO about descriptor scalability. `recoverFileFromCache` is not explicitly locked and is called from non-concurrent recovery. If writing metadata succeeds after data file creation but later operations fail, cleanup responsibility is limited. The file-level comment says not concurrent safe, while methods use a mutex; recovery remains non-concurrent.

Test signals: `contentcache_test.go` covers generation validation, metadata serialization, concurrent add/replace, concurrent get, and concurrent remove, but not recovery from corrupt/missing files.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/internal/contentcache/contentcache.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/internal/contentcache/contentcache_test.go -->
# Research: sources/user-network-fs/gcsfuse/internal/contentcache/contentcache_test.go

Purpose: tests content-cache metadata validation, checkpoint JSON round-trip, and basic thread-safety for add/replace, get, and remove operations.

Important APIs/types/functions: constants `numConcurrentGoRoutines`, `testTempDir`, generation/metageneration constants; tests `TestValidateGeneration`, `TestValidateGenerationNegative`, `TestReadWriteMetadataCheckpointFile`, `TestContentCacheAddOrReplace`, `TestContentCacheGet`, and `TestContentCacheRemove`.

Control flow: validation tests construct `CacheObject` values with metadata and compare generation/metageneration inputs. Checkpoint testing creates an anonymous file, writes metadata JSON, reads it back, unmarshals, and compares fields. Concurrency tests spawn 100 goroutines against a shared `ContentCache`: repeated `AddOrReplace` on one key, repeated `Get` of one cached object, and parallel `Remove` across many keys.

State and persistence: writes temporary cache metadata under `/tmp` and cache files through `os.CreateTemp`/anonymous files. Tests remove only the explicit metadata file in the checkpoint test; Add/Replace and Remove paths are expected to clean up through cache object destruction where applicable.

Dependencies and integration points: uses `contentcache`, `fsutil.AnonymousFile`, `timeutil.RealClock`, `sync.WaitGroup`, ogletest, and local `/tmp`. It validates the local content cache used by file inodes when local file caching is enabled.

Risks: tests use `/tmp` globally rather than `t.TempDir`, so leftovers or permissions could interfere. They do not test `RecoverCache`, corrupt metadata, missing cache files, or descriptor limits. The comment on `TestContentCacheAddOrReplace` says it should panic on concurrent map access, but the current assertion expects no panic/error because the implementation is mutex-protected.

Test signals: useful regression coverage for mutex-protected map access and metadata checkpoint formatting.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/internal/contentcache/contentcache_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/internal/fs/all_buckets_test.go -->
# Research: sources/user-network-fs/gcsfuse/internal/fs/all_buckets_test.go

Purpose: integration-tests filesystem behavior when gcsfuse mounts all accessible buckets at the root rather than a single bucket.

Important APIs/types/functions: `AllBucketsTest`, `SetUpTestSuite`, `BaseDir_Ls`, `BaseDir_Write`, `BaseDir_Rename`, and `SingleBucket_ReadAfterWrite`.

Control flow: setup creates three fake buckets and sets `serverCfg.BucketName` to empty through the shared `fsTest` harness. Tests assert that base-directory listing and writes are unsupported or fail with I/O errors, that renaming buckets or moving files across buckets is unsupported, and that normal read/write/seek/write-at behavior works inside an individual bucket subdirectory.

State and persistence: uses in-memory fake buckets and a real FUSE mount point created by `fsTest`. File contents written through the mount are persisted to the fake bucket for the life of the test suite.

Dependencies and integration points: depends on fake storage, `gcs.Bucket`, `fuse` mounted filesystem, and the shared test harness in `fs_test.go`. It validates `makeRootForAllBuckets`, base directory inode behavior, and rename restrictions across bucket roots.

Risks: error assertions match substrings such as `operation not supported` and `input/output error`, which may differ across platforms or FUSE layers. The tests rely on a real mounted filesystem, so they require FUSE support in the environment.

Test signals: confirms multi-bucket root is not a normal writable/listable GCS directory, cross-bucket renames are blocked, and bucket-scoped file operations still behave like regular file operations.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/internal/fs/all_buckets_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/internal/fs/caching_test.go -->
# Research: sources/user-network-fs/gcsfuse/internal/fs/caching_test.go

Purpose: integration-tests filesystem consistency behavior when stat caching and directory type caching are enabled, for both single-bucket and multi-bucket mounts, including implicit directories and conflicting names.

Important APIs/types/functions: constants `ttl` and `negativeCacheTTL`; `newLruCache`; `cachingTestCommon.SetUpTestSuite`; suites `CachingTest`, `CachingWithImplicitDirsTest`, and `MultiBucketMountCachingTest`; helper `getMultiMountBucketDir`; tests covering remote creation, remote changes, remote removals, conflict names, local modifier cache updates, implicit directories, symlink type caching, and negative-cache behavior after local removal plus remote recreation.

Control flow: setup wraps fake buckets with `caching.NewFastStatBucket`, using an LRU stat cache and the shared simulated `cacheClock`, then enables `DirTypeCacheTTL`. Tests mutate the uncached fake bucket to simulate remote changes, observe stale results before TTL expiry, advance `cacheClock`, and verify fresh results after expiry. Multi-bucket tests use a shared LRU with per-bucket views to verify isolation.

State and persistence: state includes fake bucket contents, stat-cache entries, directory type-cache entries, and mounted filesystem state. Cache staleness is time-controlled by simulated clock rather than sleeps.

Dependencies and integration points: depends on `internal/storage/caching`, `metadata.NewStatCacheBucketView`, `lru`, fake buckets, `inode.ConflictingFileNameSuffix`, `fusetesting`, metrics/tracing noops, and `fsTest`. It exercises the integration between storage caching and filesystem inode/type lookup.

Risks: these tests intentionally document consistency tradeoffs: remote type changes, deletions, and recreations can remain stale until TTL expiry. Multi-bucket teardown deletes objects through wrapped buckets and assumes cache state is sufficiently isolated/reset by suite lifecycle. Real FUSE mount requirements apply.

Test signals: strong external-behavior signal for cache TTL semantics, same-name file/directory conflicts, symlink versus directory conflicts, implicit directory discovery, bucket-isolated cache keys, and negative entries after local delete.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/internal/fs/caching_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/internal/fs/flat_bucket_test.go -->
# Research: sources/user-network-fs/gcsfuse/internal/fs/flat_bucket_test.go

Purpose: defines a testify suite for flat/non-hierarchical bucket rename behavior by combining shared filesystem setup with reusable rename test mixins.

Important APIs/types/functions: `FlatBucketTests`, `TestFlatBucketTests`, `SetT`, `SetupSuite`, `TearDownSuite`, `SetupTest`, and `TearDownTest`.

Control flow: `SetupSuite` sets `RenameDirLimit` to 20, enables implicit directories, and starts the shared `fsTest` mount. `SetupTest` seeds fake bucket objects representing directories, nested files, an implicit directory, and a separate `bar` prefix. Embedded `RenameDirTests` and `RenameFileTests` provide the actual test methods.

State and persistence: fake bucket objects are recreated before each test and removed through `fsTest.TearDown` after each test. The mount and server config live for the suite.

Dependencies and integration points: depends on `testify/suite`, `require`, the shared `fsTest`, and rename test types defined elsewhere in the repository. It targets the non-hierarchical directory rename path in `fs.go`, including object copy/delete or optional atomic rename for files.

Risks: this file's behavior depends heavily on embedded tests not listed in this subset; this setup file alone does not show the asserted rename cases. The seeded object names must match assumptions made by the shared rename suites.

Test signals: confirms the flat-bucket rename test matrix runs with implicit directories and a bounded rename directory limit, using representative explicit and implicit directory contents.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/internal/fs/flat_bucket_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/internal/fs/foreign_modifications_test.go -->
# Research: sources/user-network-fs/gcsfuse/internal/fs/foreign_modifications_test.go

Purpose: integration-tests read-only and externally modified GCS object scenarios, proving how the mounted filesystem observes remote object creation, overwrite, metadata changes, deletion, mtime metadata, symlinks, unreachable objects, and file/directory name conflicts.

Important APIs/types/functions: helper `setSymlinkTarget`; suite `ForeignModsTest`; tests `StatRoot`, `ReadDir_EmptyRoot`, `ReadDir_ContentsInRoot`, `ReadDir_EmptySubDirectory`, `ReadDir_ContentsInSubDirectory`, `UnreachableObjects`, `FileAndDirectoryWithConflictingName`, `SymlinkAndDirectoryWithConflictingName`, `StatTrailingNewlineName_NoConflictingNames`, `Inodes`, `OpenNonExistentFile`, `ReadFromFile_Small`, `ReadFromFile_Large`, `ReadBeyondEndOfFile`, overwrite/delete/metadata cases for files and directories, `Mtime`, `RemoteMtimeChange`, and `Symlink`.

Control flow: tests seed fake bucket contents out of band, then read/stat/open through the mounted filesystem. Conflict tests create both `foo` and `foo/` and assert directory wins the natural name while the file or symlink is exposed with `inode.ConflictingFileNameSuffix`. Overwrite/delete tests keep old file handles open, mutate the bucket remotely, and verify old handles still see old data or link count zero while new opens see new state or ENOENT.

State and persistence: fake bucket state is mutated directly outside the filesystem, while live inode/file-handle state remains in the mounted filesystem. Large-read testing repeatedly recreates a 4 MiB object and validates random ranges for about two seconds.

Dependencies and integration points: depends on `storageutil`, fake GCS bucket APIs, `inode` symlink metadata constants, `fusetesting`, Unix `syscall.Stat_t`, and `fsTest`. It validates generation-backed inode replacement and stale-handle semantics in `fs.go`.

Risks: time-bounded randomized large-read testing can be slow or variable. Error and stat details are Unix/FUSE-specific. Tests without implicit directories expect unreachable objects under missing placeholders.

Test signals: high-value coverage for consistency under remote modification, conflict-name exposure, mtime metadata parsing, symlink metadata handling, distinct inode IDs, EOF semantics, and stale open-handle behavior.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/internal/fs/foreign_modifications_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/internal/fs/fs.go -->
# Research: sources/user-network-fs/gcsfuse/internal/fs/fs.go

Purpose: implements the main gcsfuse FUSE filesystem server: mount construction, root selection, inode/handle registries, local and GCS-backed file lifecycle, directory listings, cache integration, rename/remove semantics, reads/writes, flushing/syncing, and kernel cache invalidation hooks.

Important APIs/types/functions: `ServerConfig`; `NewFileSystem`; file-cache constructors `createFileCacheHandler`, `createSharedChunkCacheManager`, `cacheDirVolumeBlockSize`, `createSingleMountFileCacheHandler`; root constructors `makeRootForBucket` and `makeRootForAllBuckets`; `fileSystem`; invariant checks; inode creation/lookup helpers; local file helpers; `flushFile`, `syncFile`, buffered-write initialization; lookup-count disposal helpers; FUSE methods `Destroy`, `StatFS`, `LookUpInode`, `GetInodeAttributes`, `SetInodeAttributes`, `ForgetInode`, `MkDir`, `MkNode`, `CreateFile`, `CreateSymlink`, `RmDir`, `Rename`, `Unlink`, directory/file open/read/write/sync/flush/release methods, xattr stubs, and `SyncFS`.

Control flow: `NewFileSystem` validates permissions, recovers local content cache when enabled, creates file-cache handlers if configured, initializes semaphores/caches/worker pools, sets up either all-buckets root or a single bucket root, applies bucket-type optimizations and kernel parameters for rapid buckets, stores root inode, then installs invariant checking. Lookup first checks local unsynced files, then asks the parent inode for a GCS core, then creates or reuses an inode if not stale by generation/metageneration/size. FUSE operations acquire locks following the documented order, operate on inode abstractions, and update maps, lookup counts, handles, and caches. Reads choose kernel reader, new read manager, or legacy read; writes initialize buffered write when eligible and promote synced local files to generation-backed maps.

State and persistence: persistent data lives in GCS objects, local content cache, and optional file-cache directories. In-memory state includes inode maps keyed by ID/name, generation-backed indexes, implicit/folder/local-file indexes, handle map, next IDs, semaphores, worker pools, dentry notifier, MRD cache, and file-cache handlers. Local files can exist before upload and are promoted after flush/sync.

Dependencies and integration points: integrates `cfg`, metadata/stat/type cache packages, file cache/downloader/shared chunk cache, content cache, inode and handle packages, `gcsx.SyncerBucket`, fake/real GCS bucket operations through interfaces, metrics/tracing, kernel params, FUSE operations, worker pools, and viper optimization tracking.

Risks: this is concurrency- and consistency-critical code; violating lock ordering can deadlock. Remote GCS mutation can stale generation-backed indexes, handled by retry and generation comparison but still exposes eventual-consistency tradeoffs. Rename has different paths for files, hierarchical folders, flat directories, atomic object rename, and copy-delete fallback. Local-file promotion and error cleanup must keep maps consistent. Dentry invalidation failures are appended to read/write errors. Cache invalidation must use correct object names and bucket ownership. `panic`-style `inodeOrDie` helpers assume FUSE/VFS never references forgotten IDs incorrectly.

Test signals: covered by filesystem integration tests in this subset for all-buckets, caching, foreign modifications, flat bucket rename setup, test harness behavior, and internal cache block-size selection. Other repository tests likely cover individual inode/handle paths.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/internal/fs/fs.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/internal/fs/fs_internal_test.go -->
# Research: sources/user-network-fs/gcsfuse/internal/fs/fs_internal_test.go

Purpose: unit-tests the internal file-cache disk block-size selection helper.

Important APIs/types/functions: `TestCacheDirVolumeBlockSize`, `cacheDirVolumeBlockSize`, `cfg.FileCacheConfig.ExperimentalDisableSizeCalculationFix`, `cfg.FileCacheConfig.ExperimentalEnableChunkCache`, and `diskutil.GetVolumeBlockSize`.

Control flow: the test creates a temporary directory, records the actual volume block size, then runs a table of configs. With the size calculation fix enabled and sparse/chunk cache disabled, the helper should return the real volume block size. When the fix is explicitly disabled, or sparse/chunk cache is enabled, it should return `1`.

State and persistence: uses a temporary directory only. No persistent state.

Dependencies and integration points: depends on the unexported helper in `fs.go`, `cfg`, `diskutil`, and `testify/assert`. This helper feeds file-cache size accounting in `createSingleMountFileCacheHandler` and downloader/cache handler construction.

Risks: the expected real block size is platform/filesystem dependent but read from the same directory immediately before assertions, reducing brittleness. The test does not verify logging or downstream cache-size accounting, only the branch decision.

Test signals: protects the compatibility behavior that disables block-size-based size accounting for sparse/chunk cache mode or when the experimental disable flag is set.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/internal/fs/fs_internal_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/internal/fs/fs_test.go -->
# Research: sources/user-network-fs/gcsfuse/internal/fs/fs_test.go

Purpose: provides the shared FUSE integration-test harness for `internal/fs`, including mount setup/teardown, fake bucket manager, default server configuration, helper object creation, and common file utilities.

Important APIs/types/functions: `TestFS`, package `init` signal handler, constants `filePerms`, `dirPerms`, `RenameDirLimit`, `SequentialReadSizeMb`, struct `fsTest`, globals `mntDir`, `ctx`, `mfs`, `mtimeClock`, `cacheClock`, `bucket`, `buckets`, `bucketType`, `defaultFileCacheConfig`, `SetUpTestSuite`, `TearDownTestSuite`, `TearDown`, object helpers, `getFileNames`, `randBytes`, `readRange`, `currentUid`, `currentGid`, `fakeBucketManager`, and its `SetUpBucket`.

Control flow: setup initializes clocks, chooses single-bucket or all-buckets mode, creates fake bucket manager and default config, fills ownership/permission fields, creates a temp mount directory, builds a server with `fs.NewServer`, configures logging, and mounts FUSE. Teardown retries unmount on resource-busy, joins the mounted filesystem, removes the mount point, resets global bucket state, and per-test cleanup removes mount contents and closes open files.

State and persistence: test state spans package globals, mounted FUSE server, fake buckets, simulated cache clock, temp mount directory, and open file handles. Data persists in fake bucket memory during a suite and is cleaned between tests where possible.

Dependencies and integration points: integrates `fs.NewServer`, `fuse.Mount`, `fusetesting`, fake storage, `gcsx.NewSyncerBucket`, permissions, metrics/tracing noops, logger, locker debugging, and ogletest. Other test files embed `fsTest`.

Risks: package-level globals make suites order-sensitive unless reset carefully. Real FUSE mount support is required. Signal handling stops tests after SIGINT. Cleanup ignores some removal errors intentionally, which can mask leftover state in unusual cases.

Test signals: this file is infrastructure rather than assertions, but it establishes representative default config: metadata cache defaults, new reader enabled, unlimited file cache size, fixed file/dir perms, rename limit, and sequential read size.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/internal/fs/fs_test.go -->
