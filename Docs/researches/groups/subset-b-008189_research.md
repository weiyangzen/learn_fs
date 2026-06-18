# subset-b-008189 research

Grouped research for MinIO data-usage, dummy handler, dynamic timeout, encryption, and endpoint ellipses sources. Each file section preserves the original source path and is delimited for reconciliation splitting.

<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio/cmd/data-usage-cache_gen.go -->
## sources/object-store/minio/cmd/data-usage-cache_gen.go

Purpose: This is generated `msgp` serialization code for the data usage cache model used by the MinIO scanner. It provides MessagePack encode/decode, byte marshal/unmarshal, and size-estimation methods for the current cache types plus compatibility readers for older cache layouts. The file is not intended for manual logic changes; behavioral changes should come from the source structs and regenerating with `github.com/tinylib/msgp`.

Important APIs and types: Current generated methods cover `allTierStats`, `currentScannerCycle`, `dataUsageCache`, `dataUsageCacheInfo`, `dataUsageEntry`, `dataUsageHash`, `sizeHistogram`, `sizeHistogramV1`, `tierStats`, and `versionsHistogram`. Compatibility-only generated methods cover `dataUsageCacheV2` through `dataUsageCacheV7` and `dataUsageEntryV2` through `dataUsageEntryV7`. The current `dataUsageEntry` wire format is a map keyed with compact names: `ch` for children, `sz` for total size, `os` for objects, `vs` for versions, `dms` for delete markers, `szs` for object-size histogram, `vh` for version histogram, `ats` for optional tier stats, and `c` for compaction state. `dataUsageCache` serializes `Info` and a `Cache` map from path/hash strings to entries.

Control flow: Decode and unmarshal paths follow a repeated pattern: read a map or array header, switch on field names, decode known fields, and skip unknown fields. Map fields are initialized on demand and cleared before reuse, so decoding into a reused value does not retain stale map entries. Fixed-size histograms validate array lengths against `dataUsageBucketLen`, `dataUsageBucketLenV1`, or `dataUsageVersionLen` and return `msgp.ArrayError` on mismatches. The current entry decoder tracks an omitted-field mask so absent `ats` clears `AllTierStats`; this matters when decoding into reused entries.

State and persistence behavior: This file defines the binary persistence contract for `.usage-cache.bin`. Current cache persistence includes scanner metadata (`Name`, `NextCycle`, `LastUpdate`, `SkipHealing`), hierarchical cache entries, object/version/delete-marker counters, histograms, tier stats, and compaction flags. Legacy versions preserve read access to older cache files whose entry forms were arrays or had shorter histogram lengths. The generated code is tolerant of unknown map keys but strict about fixed array lengths.

Dependencies and integration points: It depends on `github.com/tinylib/msgp/msgp` and `time`. Runtime callers are in the data usage cache/scanner code, especially cache `load`, `save`, `serializeTo`, and `deserialize`. The shape must remain aligned with struct tags in `data-usage-cache.go`; otherwise persisted caches may fail to load or silently lose fields.

Risks: Generated code is large, repetitive, and easy to corrupt by hand. The main compatibility risk is changing current struct tags or histogram lengths without updating migration readers and tests. Map iteration order is nondeterministic, so persisted byte output is not stable for byte-for-byte comparison. The decoders skip unknown fields, which supports forward compatibility but can hide accidental field-name drift until higher-level tests notice missing data. Any change to `AllTierStats` nil/omitted behavior can affect tier accounting after cache reloads.

Test signals: `data-usage-cache_gen_test.go` round-trips zero-value generated types through marshal/unmarshal and encode/decode and benchmarks serialization. `data-usage_test.go` provides stronger integration signals by serializing a populated `dataUsageCache`, deserializing it, and comparing cache entries as JSON. `data-usage-cache_test.go` covers histogram migration from V1 to current buckets.
<!-- END_FILE_RESEARCH: sources/object-store/minio/cmd/data-usage-cache_gen.go -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio/cmd/data-usage-cache_gen_test.go -->
## sources/object-store/minio/cmd/data-usage-cache_gen_test.go

Purpose: This generated test file validates the basic `msgp` contract for the generated data usage cache serializers. It also provides allocation/throughput benchmarks for marshal, append-marshal, unmarshal, encode, and decode paths.

Important APIs and functions: The file defines paired tests and benchmarks for `allTierStats`, `currentScannerCycle`, `dataUsageCache`, `dataUsageCacheInfo`, `dataUsageEntry`, `sizeHistogram`, `sizeHistogramV1`, `tierStats`, and `versionsHistogram`. Test functions include `TestMarshalUnmarshal...` and `TestEncodeDecode...`; benchmark functions include `BenchmarkMarshalMsg...`, `BenchmarkAppendMsg...`, `BenchmarkUnmarshal...`, `BenchmarkEncode...`, and `BenchmarkDecode...`.

Control flow: Each marshal/unmarshal test constructs a zero-value instance, calls `MarshalMsg(nil)`, unmarshals the resulting bytes back into the same value, verifies that no bytes remain, then calls `msgp.Skip` on the same payload and verifies it consumes all bytes. Encode/decode tests serialize through `msgp.Encode` into a `bytes.Buffer`, compare the observed buffer length with `Msgsize()` as a warning-only upper-bound check, decode into a new value, then verify a reader can skip the encoded object. Benchmarks repeatedly run the same generated methods against zero values and use `msgp.NewEndlessReader` for decode loops.

State and persistence behavior: The tests do not construct populated cache state. They mainly prove that zero-value forms are syntactically valid MessagePack and that `Msgsize` is not an underestimate for those cases. Because all data is in memory, no object store or scanner persistence path is exercised here.

Dependencies and integration points: The tests depend on `bytes`, `testing`, and `github.com/tinylib/msgp/msgp`. They integrate directly with generated methods in `data-usage-cache_gen.go` and indirectly with the struct definitions in `data-usage-cache.go`.

Risks: Coverage is shallow for real cache data. It does not verify populated maps, optional `AllTierStats`, non-zero scanner cycles, non-empty histograms, old-version decoders, map clearing on reuse, or migration from older wire layouts. Because the file is generated, manual edits are likely to be lost on regeneration.

Test signals: These tests are useful as smoke tests for generated code compilation and basic wire validity. Stronger behavioral signals come from hand-written data-usage tests that serialize real scanned cache content and compare deserialized entries.
<!-- END_FILE_RESEARCH: sources/object-store/minio/cmd/data-usage-cache_gen_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio/cmd/data-usage-cache_test.go -->
## sources/object-store/minio/cmd/data-usage-cache_test.go

Purpose: This hand-written test file validates object-size histogram behavior used by data usage accounting. It focuses on bucket-label conversion and migration from an older histogram layout.

Important APIs and functions: `TestSizeHistogramToMap` exercises `sizeHistogram.add` and `sizeHistogram.toMap`. `TestMigrateSizeHistogramFromV1` exercises `sizeHistogram.mergeV1`. The tests use `github.com/dustin/go-humanize` constants to place sample object sizes in byte, KiB, MiB, and tens-of-MiB ranges.

Control flow: `TestSizeHistogramToMap` builds a histogram by adding object sizes, converts it to a map of public bucket labels, then checks that expected buckets have exact counts and unexpected buckets are zero or absent. The first case intentionally checks overlapping/coarser labels such as `LESS_THAN_1024_B`, `BETWEEN_64_KB_AND_256_KB`, and `BETWEEN_1024B_AND_1_MB`. `TestMigrateSizeHistogramFromV1` constructs V1 array values and verifies that they map into current histogram indexes, with older buckets shifted into the newer bucket layout.

State and persistence behavior: No files are persisted. The tests target in-memory histogram state, but the behavior matters for persisted `.usage-cache.bin` compatibility because current cache entries store `sizeHistogram`, while older entries may carry `sizeHistogramV1`.

Dependencies and integration points: These tests depend on the histogram definitions and methods in `data-usage-cache.go` and the generated serializers in `data-usage-cache_gen.go` for the persistent representation. The map labels are consumed by `BucketUsageInfo.ObjectSizesHistogram` in data usage API responses.

Risks: The test data covers only a small subset of bucket thresholds. It does not exhaustively assert all histogram labels or boundary values around every threshold, so off-by-one changes in less-common ranges could slip through. Migration checks cover two compact cases but not zero-filled or fully populated edge arrays beyond the shown values.

Test signals: The file provides targeted confidence that the public histogram labels and V1-to-current migration retain expected counts for common small and medium objects.
<!-- END_FILE_RESEARCH: sources/object-store/minio/cmd/data-usage-cache_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio/cmd/data-usage-utils.go -->
## sources/object-store/minio/cmd/data-usage-utils.go

Purpose: This file defines the public data usage structures and conversion helpers used to expose MinIO cluster, bucket, replication, and tier usage statistics. It is the JSON/API-facing model for scanner output.

Important APIs and types: `BucketTargetUsageInfo` reports per-replication-target bytes and counts for pending, failed, replicated, and replica objects. `BucketUsageInfo` reports bucket size, object/version/delete-marker counts, object-size and version histograms, replica counters, and per-target replication details; fields suffixed `V1` exist for backward compatibility with older replication accounting. `DataUsageInfo` aggregates cluster capacity, object/version/delete-marker totals, bucket count, per-bucket usage, legacy `BucketSizes`, optional replication info, and optional `TierStats`. Methods `DataUsageInfo.tierStats()` and `DataUsageInfo.tierMetrics()` transform internal tier statistics into admin API and metrics forms.

Control flow: `tierStats()` returns nil when no tier stats exist or tier configuration is empty. Otherwise it asks `allTierStats.populateStats` to fill `madmin.TierStats`, wraps each tier as `madmin.TierInfo`, adds tier type from `globalTierConfigMgr`, and sorts internal tiers first, then remaining tiers by name. `tierMetrics()` returns one metric each for transitioned bytes, transitioned objects, and transitioned versions per tier, using metric descriptors from cluster ILM metric helpers and labeling each sample by tier.

State and persistence behavior: The structs are serialized to JSON for `.usage.json` and API responses. `DataUsageInfo.TierStats` points to scanner/cache tier state persisted in the data usage cache. Compatibility is explicit: both new `BucketsUsage` and deprecated `BucketSizes` are retained, and V1 replication fields are still present so older persisted JSON can be upgraded by `loadDataUsageFromBackend`.

Dependencies and integration points: The file depends on `sort`, `time`, and `github.com/minio/madmin-go/v3`. It integrates with scanner cache aggregation, admin APIs, Prometheus metrics (`MetricV2`), global tier configuration, and replication config migration in `data-usage.go`.

Risks: These structs are API contracts; JSON tag changes or field removals can break clients. `tierStats()` depends on global tier config state, so tier stats can disappear from output when configuration is empty even if cache data exists. Sorting gives internal tiers priority with a comparator that returns true whenever the left item is internal, so multiple internal tiers rely on sort behavior rather than secondary ordering.

Test signals: There are no direct tests in this file. Coverage is indirect through data usage serialization tests, scanner tests, and any API/metrics tests that consume `DataUsageInfo`.
<!-- END_FILE_RESEARCH: sources/object-store/minio/cmd/data-usage-utils.go -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio/cmd/data-usage.go -->
## sources/object-store/minio/cmd/data-usage.go

Purpose: This file stores and loads high-level data usage JSON and provides a backend prefix-usage loader for erasure deployments. It bridges scanner/cache internals with MinIO metadata objects under the bucket metadata prefix.

Important APIs and functions: Constants define metadata object names and paths: `.usage.json`, `.usage-cache.bin`, `.bloomcycle.bin`, `.background-heal.json`, and backup paths under `bucketMetaPrefix`. `storeDataUsageInBackend(ctx, objAPI, dui)` consumes a channel of `DataUsageInfo`, marshals each value with json-iterator, saves the primary `.usage.json`, and periodically writes `.usage.json.bkp`. `loadPrefixUsageFromBackend(ctx, objAPI, bucket)` returns a prefix-to-size map for a bucket by reading `.usage-cache.bin` from all erasure sets. `loadDataUsageFromBackend(ctx, objAPI)` reads `.usage.json`, falls back to backup, unmarshals it, and performs compatibility migrations.

Control flow: Store flow is channel-driven: for each usage update, marshal JSON, optionally write a backup when the attempt counter exceeds ten, then write the primary config and log errors. Prefix loading first type-asserts `ObjectLayer` to `*erasureServerPools`; non-erasure deployments return an empty map. The cachevalue wrapper is initialized once with a 30-second TTL, `ReturnLastGood`, and `NoWait`. The loader iterates pools and sets, gives each cache load a two-second timeout, finds the bucket root entry, flattens children, decodes directory-object names, and sums sizes per prefix. JSON load flow falls back to backup on read failure, returns an empty `DataUsageInfo` for missing config, then fills `BucketsUsage` from legacy `BucketSizes` or `BucketSizes` from `BucketsUsage` when either side is absent.

State and persistence behavior: Primary persisted state is JSON in MinIO metadata plus an occasional backup. Prefix usage is derived from binary scanner cache files on each erasure set, but the returned map itself is cached in process for 30 seconds. Compatibility code also migrates legacy replication V1 fields into the newer `ReplicationInfo` map keyed by the bucket replication role ARN when a replication config is available.

Dependencies and integration points: The file depends on `jsoniter`, `cachevalue`, ObjectLayer config helpers (`readConfig`, `saveConfig`), erasure server pool internals, `dataUsageCache`, scanner logging, and replication config lookup. It integrates with background scanner output and admin/bucket usage consumers.

Risks: `storeDataUsageInBackend` runs until its input channel closes and has no explicit cancellation inside the loop beyond the context passed to save/log operations. Backup frequency is attempt-count based and only starts after more than ten updates. `loadPrefixUsageFromBackend` uses one global cache keyed only by its update function, so callers should be aware of the 30-second cached result behavior. The prefix loader silently skips sets where cache loading fails or where a bucket root is absent, which favors availability but can underreport prefixes during cache corruption or partial set failures.

Test signals: There are no direct tests for these functions in the listed files. Indirect coverage comes from scanner/cache serialization tests and from any object-layer tests that exercise stored data usage JSON.
<!-- END_FILE_RESEARCH: sources/object-store/minio/cmd/data-usage.go -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio/cmd/data-usage_test.go -->
## sources/object-store/minio/cmd/data-usage_test.go

Purpose: This hand-written test file validates scanner data usage cache updates, prefix compaction behavior, cache serialization/deserialization, and utility helpers for constructing test file trees.

Important APIs and functions: `usageTestFile` describes test file paths and sizes. `TestDataUsageUpdate` exercises `scanDataFolder` over a bucket rooted below a temporary xlStorage drive. `TestDataUsageUpdatePrefix` exercises scanning when paths include bucket prefixes and compaction thresholds. `TestDataUsageCacheSerialize` exercises `dataUsageCache.serializeTo` and `deserialize`. Helpers `createUsageTestFiles`, `generateUsageTestFiles`, and `equalAsJSON` support test setup and comparison.

Control flow: The update tests create a temporary directory tree, define a `getSize` callback that returns file size and one version for files, initialize `xlStorage.diskInfoCache`, and scan the bucket. They then call `find`, `flatten`, and compare expected size, object count, version count, and histograms for root and selected directories. The tests mutate the tree by adding files and deleting one file, run `scanDataFolder` for `dataUsageUpdateDirCycles`, increment `NextCycle`, and verify changed directories are reflected. Prefix tests also generate many small files to trigger compaction and check that deeply nested compacted entries are represented at expected parents. Serialization tests scan a richer tree, replace one entry, serialize to a buffer, deserialize into a new cache, verify `LastUpdate` is set and preserved, and compare each cache entry via JSON.

State and persistence behavior: All state is local to temporary directories and memory buffers, but it mirrors production cache lifecycle: scan from disk, update `dataUsageCache`, compact children, serialize to the binary cache format, and deserialize. The tests exercise cache mutation across scanner cycles, including adding and removing files.

Dependencies and integration points: The tests depend on scanner types (`scannerItem`, `sizeSummary`, `scanDataFolder`), `xlStorage`, `cachevalue`, `DiskInfo`, `dataUsageCache`, histogram methods, and filesystem functions. They integrate with production scanner code rather than mocking the entire scanner path.

Risks: The tests rely on production constants such as `dataUsageUpdateDirCycles`, `dataScannerCompactLeastObject`, and `dataScannerCompactAtFolders`; changes to compaction heuristics require expected values to be revisited. JSON comparison avoids Go map-order issues but can hide differences in unexported fields. The `getSize` callback models one version per file and does not cover delete markers, multipart metadata, tier stats, or healing behavior.

Test signals: This is the strongest listed test coverage for data usage cache behavior. It checks real filesystem traversal, incremental update detection, compaction, histograms, object/version counts, and binary serialization round-trip on populated cache data.
<!-- END_FILE_RESEARCH: sources/object-store/minio/cmd/data-usage_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio/cmd/decommetric_string.go -->
## sources/object-store/minio/cmd/decommetric_string.go

Purpose: This generated `stringer` file provides the `String()` method for the `decomMetric` enum defined in decommissioning code. It maps metric constants to stable names used in logs, metrics, or diagnostics.

Important APIs and functions: The compile-time guard function `_()` indexes a one-element array with expected enum offsets to fail compilation if `decomMetricDecommissionBucket`, `decomMetricDecommissionObject`, or `decomMetricDecommissionRemoveObject` change values without regeneration. `_decomMetric_name` stores concatenated names, `_decomMetric_index` stores offsets, and `(decomMetric).String()` returns the name for known enum values or `decomMetric(<n>)` for out-of-range values.

Control flow: `String()` checks whether the enum is greater than or equal to the last valid index; if so it formats an unknown numeric value with `strconv.FormatInt`. Otherwise it slices the concatenated name string using the generated index table.

State and persistence behavior: No mutable state or persistence exists. The generated strings may become externally visible through logs or metrics, so names are a lightweight compatibility surface.

Dependencies and integration points: It imports only `strconv` and integrates with `decomMetric` constants in `erasure-server-pool-decom.go`. It should be regenerated with `stringer -type=decomMetric -trimprefix=decomMetric erasure-server-pool-decom.go` when enum constants change.

Risks: Manual edits can be overwritten by regeneration. Adding, removing, or reordering enum constants without regenerating causes either a compile failure from the guard or incorrect string output if a change bypasses the guard pattern.

Test signals: No direct tests are present. The compile-time guard is the primary protection.
<!-- END_FILE_RESEARCH: sources/object-store/minio/cmd/decommetric_string.go -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio/cmd/dummy-data-generator_test.go -->
## sources/object-store/minio/cmd/dummy-data-generator_test.go

Purpose: This test helper file defines a deterministic repeating data generator and reader comparison utility used by tests that need predictable stream content without storing large fixtures.

Important APIs and types: `alphabets` is the repeating byte alphabet. `DummyDataGen` implements `io.ReadSeeker` with an internal repeated byte slice, current index, and total length. `NewDummyDataGen(totalLength, skipOffset)` constructs a finite reader over the infinite repeated alphabet stream, optionally starting at an offset. `(*DummyDataGen).Read` fills caller buffers until the configured length and returns `io.EOF` at the end. `(*DummyDataGen).Seek` supports start/current/end seeking with negative-position validation. `cmpReaders` compares two readers in 32 KiB chunks using `io.ReadFull`.

Control flow: Construction validates non-negative length and offset, normalizes the skip offset by the alphabet length, repeats the alphabet 100 times, and slices enough bytes to avoid wrapping during normal reads. Read loops copy from the repeated slice modulo its length until either the caller buffer is full or the logical length is reached, correcting over-read counts at EOF. Seek adjusts `idx` based on `whence` and rejects negative target positions. `cmpReaders` reads both readers chunk-by-chunk, compares byte counts and contents, and treats matching EOF or unexpected EOF on both readers as a clean end.

State and persistence behavior: State is in-memory only. The important invariant is stream composability: a full stream can equal the concatenation of shorter streams with matching offsets.

Dependencies and integration points: It depends on `bytes`, `errors`, `fmt`, `io`, and `testing`. It is located in a `_test.go` file, so it is test-only support for package `cmd`.

Risks: `Read` returns `len(p)` at the end of the non-EOF path, not the accumulated `n`; given the loop structure this is normally equivalent when the buffer is filled, but it is a subtle implementation detail. The fixed `multiply = 100` assumes the internal repeated slice is large enough for modulo-slice copy behavior; very large reads still work through modulo reuse, but construction is less direct than a simple modulo copy loop. `Seek` does not reject unknown `whence` values and returns the current index unchanged.

Test signals: `TestDummyDataGenerator` checks zero-length reads, offset normalization, composability, and seeking by one alphabet length. `TestCmpReaders` verifies equal small readers compare true and length-mismatched readers compare false.
<!-- END_FILE_RESEARCH: sources/object-store/minio/cmd/dummy-data-generator_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio/cmd/dummy-handlers.go -->
## sources/object-store/minio/cmd/dummy-handlers.go

Purpose: This file implements dummy S3-compatible bucket configuration handlers for APIs MinIO chooses not to fully support while still returning AWS-compatible responses or errors. The handlers validate authorization and bucket existence before returning fixed XML, missing-configuration errors, not-implemented errors, or success for no-op deletes.

Important APIs and functions: Methods on `objectAPIHandlers` include `GetBucketWebsiteHandler`, `GetBucketAccelerateHandler`, `GetBucketRequestPaymentHandler`, `GetBucketLoggingHandler`, `DeleteBucketWebsiteHandler`, `GetBucketCorsHandler`, `PutBucketCorsHandler`, and `DeleteBucketCorsHandler`. They use `newContext`, `logger.AuditLog`, `mux.Vars`, `api.ObjectAPI`, `checkRequestAuthType`, `GetBucketInfo`, `writeErrorResponse`, `writeSuccessResponseXML`, and `writeSuccessResponseHeadersOnly`.

Control flow: Most GET handlers share the same sequence: create request context, defer audit logging, extract bucket from route variables, reject uninitialized object API, authorize the relevant policy action, verify the bucket exists with `GetBucketInfo`, then return a fixed response. Website and CORS GETs return `ErrNoSuchWebsiteConfiguration` and `ErrNoSuchCORSConfiguration`. Accelerate, request payment, and logging GETs return static XML defaults. CORS PUT and DELETE validate auth/bucket and then return `ErrNotImplemented`. Website DELETE is a pure success-header no-op.

State and persistence behavior: These handlers do not read or write persistent configuration beyond bucket existence checks. Static XML responses are generated inline. No CORS, website, accelerate, request-payment, or logging state is stored.

Dependencies and integration points: The file depends on `net/http`, `github.com/minio/minio/internal/logger`, `github.com/minio/mux`, and `github.com/minio/pkg/v3/policy`. It integrates with S3 routing, request auth, audit logs, bucket metadata access, and S3 error serialization.

Risks: Dummy behavior must remain compatible with client expectations. Reusing `GetBucketPolicyAction` for several dummy GET APIs is deliberate but may not match a future fine-grained permission model. `DeleteBucketWebsiteHandler` does not audit, authorize, or verify bucket existence in this file, which is a notable difference from the other handlers and may rely on outer routing/middleware behavior. Static XML strings must stay valid and AWS-compatible.

Test signals: No direct tests are listed for these handlers. Coverage is likely indirect through S3 API compatibility tests, if present elsewhere.
<!-- END_FILE_RESEARCH: sources/object-store/minio/cmd/dummy-handlers.go -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio/cmd/dynamic-timeouts.go -->
## sources/object-store/minio/cmd/dynamic-timeouts.go

Purpose: This file implements an adaptive timeout helper that increases timeouts when recent operations often fail by timeout and decreases timeouts when recent successful durations are well below the current timeout. It is designed for concurrent use by callers recording operation outcomes.

Important APIs and types: Constants define thresholds and limits: failure rate above 33% increases the timeout, failure rate below 10% allows decrease, the adjustment window is 16 entries, and the maximum timeout is 24 hours. `dynamicTimeout` stores the current timeout and minimum as atomics, a fixed-size duration log, a mutex, and an optional retry interval. `dynamicTimeoutOpts` feeds `newDynamicTimeoutWithOpts`. Public methods include `Timeout()`, `RetryInterval()`, `LogSuccess(duration)`, and `LogFailure()`.

Control flow: Construction panics on non-positive timeout/minimum and clamps minimum down to timeout if needed. Each success or failure calls `logEntry`; failures are recorded as `maxDuration`, while negative success durations are ignored. `logEntry` atomically increments the entry count, writes entries into the fixed array under a mutex, and when the 16th entry arrives copies the array, resets the count to zero, releases the mutex, and calls `adjust`. `adjust` counts failures and the maximum successful duration. If the failure percentage exceeds the upper threshold, timeout grows by 25% up to `maxDynamicTimeout` and not below minimum. If failure percentage is below the lower threshold, the max success duration is padded by 25%, and the timeout moves halfway toward that target but not below minimum.

State and persistence behavior: State is in-memory only. Timeout and entry count use atomic int64 values; the log buffer is protected by a mutex. The comment notes entries may be leaked while copying, meaning some concurrent events can be dropped around adjustment boundaries rather than blocking heavily.

Dependencies and integration points: The file depends on `math`, `sync`, `sync/atomic`, and `time`. It is a generic helper used by MinIO components that need adaptive operation deadlines or retry intervals.

Risks: The adaptive algorithm is intentionally lossy under concurrency; callers should not treat every logged outcome as guaranteed input. Threshold boundaries are strict (`>` for increase, `<` for decrease), so exactly 33% or 10% failure rates do not adjust in that direction. A sequence of very fast successes can drive the timeout down to minimum, which may be too aggressive if the workload is bursty. `RetryInterval` is just stored configuration; this type does not enforce sleeps or retries.

Test signals: `dynamic-timeouts_test.go` covers increases, repeated increases, decreases, repeated decreases, convergence above success duration, minimum clamping, concurrent logging under race-style pressure, and random exponential/normal duration distributions.
<!-- END_FILE_RESEARCH: sources/object-store/minio/cmd/dynamic-timeouts.go -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio/cmd/dynamic-timeouts_test.go -->
## sources/object-store/minio/cmd/dynamic-timeouts_test.go

Purpose: This file validates the adaptive behavior and concurrent safety expectations of `dynamicTimeout`.

Important APIs and functions: Tests include `TestDynamicTimeoutSingleIncrease`, `TestDynamicTimeoutDualIncrease`, `TestDynamicTimeoutSingleDecrease`, `TestDynamicTimeoutDualDecrease`, `TestDynamicTimeoutManyDecreases`, `TestDynamicTimeoutConcurrent`, `TestDynamicTimeoutHitMinimum`, `TestDynamicTimeoutAdjustExponential`, and `TestDynamicTimeoutAdjustNormalized`. Helper `testDynamicTimeoutAdjust` logs a full adjustment window using a random duration function.

Control flow: Increase tests fill one or two full log windows with failures and assert the timeout grows. Decrease tests fill windows with 20-second successes against a one-minute timeout and assert timeout shrinks; repeated decrease tests assert continued movement. The many-decrease and hit-minimum tests repeatedly log successes and check eventual convergence above the success duration or exactly at the configured minimum. The concurrent test starts one goroutine per `GOMAXPROCS`, logs many random successes, reads `Timeout`, and panics if it escapes the expected min/max range. Randomized tests seed the global RNG and feed exponential or normal distributions through the helper, treating durations at or above one minute as failures.

State and persistence behavior: Tests exercise only in-memory timeout state. They are sensitive to the constants in `dynamic-timeouts.go`, especially log size and adjustment thresholds.

Dependencies and integration points: The file depends on `math/rand`, `runtime`, `sync`, `testing`, and `time`. It directly tests `newDynamicTimeout`, `LogSuccess`, `LogFailure`, and `Timeout`.

Risks: The concurrent test is most valuable when run with the Go race detector; without `-race`, it mainly checks gross timeout bounds. Randomized tests use fixed seeds but still assert only broad direction. The tests do not cover `newDynamicTimeoutWithOpts`, `RetryInterval`, invalid constructor panics, negative success durations, or the 24-hour cap.

Test signals: The file gives good confidence in core adjustment direction, minimum enforcement, and basic concurrent robustness for expected workloads.
<!-- END_FILE_RESEARCH: sources/object-store/minio/cmd/dynamic-timeouts_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio/cmd/encryption-v1.go -->
## sources/object-store/minio/cmd/encryption-v1.go

Purpose: This file implements MinIO's object encryption/decryption support for SSE-C, SSE-S3, and SSE-KMS. It covers metadata creation and rotation, request encryption readers, decryption readers, encrypted ETag handling, encrypted range calculations, and encrypted checksum metadata.

Important APIs and types: Constants define customer-key size, DARE IV size, DARE package block size, and DARE package metadata size. Error variables model AWS-compatible and MinIO-specific encryption failures. Public helpers include `KMSKeyID` on `ObjectInfo`/`MultipartInfo`, `DecryptETags`, `ParseSSECopyCustomerRequest`, `ParseSSECustomerRequest`, `ParseSSECustomerHeader`, `EncryptRequest`, `DecryptRequestWithSequenceNumberR`, `DecryptCopyRequestR`, `DecryptBlocksRequestR`, `ObjectInfo.DecryptedSize`, `DecryptETag`, `ObjectInfo.GetDecryptedRange`, `ObjectInfo.EncryptedSize`, `DecryptObjectInfo`, metadata checksum helpers, and `DecryptBlocksReader`.

Control flow: Request parsing rejects incompatible SSE-S3/SSE-C headers and delegates header validation to `internal/crypto`. Encryption creates or unseals object keys depending on type: SSE-S3 and SSE-KMS use `GlobalKMS.GenerateKey`, while SSE-C derives from the client key; metadata is populated with sealed object keys. `EncryptRequest` wraps large inputs in a buffered reader and returns an `sio.EncryptReader`. Decryption unseals the object key from metadata, validates SSE-C keys when needed, and returns `sio.DecryptReader` with a sequence number. Multipart decryption builds a `DecryptBlocksReader` that derives per-part keys using HMAC-SHA256 over the part number and reads each encrypted part through a limited DARE stream.

State and persistence behavior: Encryption metadata is written into the object user-defined metadata map. KMS encryption stores key IDs, encrypted data keys, sealed object keys, and optional KMS context; SSE-C stores sealed keys derived from client material. Key rotation mutates metadata in place. Object data size on disk includes DARE overhead; `DecryptedSize` and `GetDecryptedRange` translate between persisted encrypted sizes and client-visible plaintext sizes. Checksum metadata can itself be encrypted using an HMAC-derived metadata key.

Dependencies and integration points: The file integrates with `internal/crypto`, `internal/kms`, KES errors, `sio`, `etag`, `hash`, MinIO HTTP header constants, request logging, and object metadata types. It depends on global KMS and global context for KMS-backed operations and logging.

Risks: This is security-sensitive code. Incorrect header compatibility checks can expose encrypted objects or reject valid AWS-compatible requests. Range math is complex across DARE package boundaries and multipart boundaries; off-by-one errors can corrupt ranged GET/COPY responses. `DecryptBlocksReader.Read` must preserve reader contract while switching parts; changes need careful testing. Global KMS absence produces explicit errors, so startup/config state directly affects object access. Metadata encryption and checksum decryption intentionally log some failures and suppress secret-key mismatches, so observability and compatibility need balance.

Test signals: `encryption-v1_test.go` covers SSE-C request encryption metadata, `DecryptObjectInfo` error behavior, encrypted ETag handling, detailed decrypted range math for single-part and multipart objects including a regression case, and default encryption option detection via `getDefaultOpts`. More KMS integration, key rotation, checksum metadata, and live reader-stream tests would be needed for full coverage.
<!-- END_FILE_RESEARCH: sources/object-store/minio/cmd/encryption-v1.go -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio/cmd/encryption-v1_test.go -->
## sources/object-store/minio/cmd/encryption-v1_test.go

Purpose: This file tests selected encryption behaviors for SSE-C request handling, object info decryption validation, ETag decryption, encrypted range calculation, and default encryption option inference.

Important APIs and functions: `TestEncryptRequest` exercises `EncryptRequest`. `TestDecryptObjectInfo` exercises `DecryptObjectInfo`. `TestDecryptETag` exercises `DecryptETag`. `TestGetDecryptedRange_Issue50` and `TestGetDecryptedRange` exercise `ObjectInfo.GetDecryptedRange`. `TestGetDefaultOpts` exercises `getDefaultOpts` with MinIO Go encryption types.

Control flow: `TestEncryptRequest` forces TLS, builds requests with SSE-C headers, encrypts a 64-byte reader, and asserts encryption metadata keys exist. `TestDecryptObjectInfo` runs table cases for unencrypted objects, encrypted metadata with GET/HEAD headers, missing SSE-C keys, invalid SSE-C parameters on unencrypted objects, and tampered encrypted sizes. `TestDecryptETag` checks successful unsealing, invalid hex, tampered encrypted ETags, and special multipart-style random ETags with `-partcount` suffixes. Range tests build encrypted object sizes via `sio.EncryptedSize`, use explicit `HTTPRangeSpec` cases, and compare production range translation to a reference implementation for multipart objects. `TestGetDefaultOpts` checks SSE-C, SSE-S3, existing metadata, copy-source behavior, and malformed keys.

State and persistence behavior: Tests are in-memory. They construct metadata maps and `ObjectInfo` values that mimic persisted encrypted object state. The range tests encode important persistence assumptions: stored sizes include DARE overhead and multipart parts are independently encrypted.

Dependencies and integration points: The tests depend on `minio-go/v7/pkg/encrypt`, `internal/crypto`, MinIO HTTP constants, `sio`, and human-size constants. They validate integration between request headers, object metadata, and crypto helpers.

Risks: KMS-backed encryption paths are mostly not exercised because no real or fake `GlobalKMS` is configured. Streaming decrypt readers, key rotation, encrypted checksum metadata, and multipart `DecryptBlocksReader` behavior are not directly read/compared. Some tests assert broad error equality and do not validate response-to-S3-error mapping.

Test signals: The range tests are strong because they cover single-part, multipart, suffix ranges, large part counts, package-boundary skips, and a named regression. The request and ETag tests provide focused compatibility coverage for common SSE-C and encrypted ETag edge cases.
<!-- END_FILE_RESEARCH: sources/object-store/minio/cmd/encryption-v1_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio/cmd/endpoint-ellipses.go -->
## sources/object-store/minio/cmd/endpoint-ellipses.go

Purpose: This file implements support for ellipses/list expansion in `minio server` endpoint arguments and turns expanded endpoints into erasure-set layouts. It handles automatic and user-overridden set sizing, symmetry checks, config-file layouts, CLI layout merging, duplicate detection, and endpoint pool construction.

Important APIs and types: `endpointSet` stores parsed `ellipses.ArgPattern`, cached expanded endpoints, and set indexes. `setSizes` lists supported drives-per-set values from 2 through 16. `getDivisibleSize`, `commonSetDriveCount`, `possibleSetCountsWithSymmetry`, and `getSetIndexes` choose erasure set sizes. `parseEndpointSet` and `GetAllSets` parse and expand CLI arguments. `EnvErasureSetDriveCount` names the manual override variable. `endpointsList`, `node`, and `poolArgs` support config-file layouts. `buildDisksLayoutFromConfFile`, `mergeDisksLayoutFromArgs`, and `createServerEndpoints` build final `disksLayout` and `EndpointServerPools`.

Control flow: Set selection starts by validating total sizes, computing the GCD across argument expansions, finding supported set sizes that divide it, optionally applying a manual set-drive-count override, then filtering for symmetry against every ellipses sequence. The final set size prefers values that minimize total sets while preserving symmetry. `endpointSet.Get` slices expanded endpoint strings according to set indexes. `GetAllSets` handles non-ellipses arguments as legacy direct endpoints, parses ellipses arguments otherwise, and rejects duplicates. Config-file layout building expands list and ellipses patterns per pool, groups disks by host, interleaves disks by index across nodes, rejects uneven disk counts and mixed single-node/distributed layouts, hashes the resulting layout for `cmdline`, and calls `GetAllSets`. CLI merging reads `MINIO_ERASURE_SET_DRIVE_COUNT`, preserves legacy layout when no ellipses are present, and requires all multi-argument pool expansion args to use ellipses.

State and persistence behavior: The file mutates `serverCtxt.Layout` during argument merging and produces `PoolEndpoints` with layout metadata, platform string, set count, drives per set, and command-line identity. Config-file layouts use an xxhash of expanded disks rather than the raw command line.

Dependencies and integration points: It depends on `ellipses`, MinIO config errors, environment parsing, set utilities, URL parsing, `xxhash`, and endpoint creation functions such as `CreatePoolEndpoints`. It directly affects server startup topology and erasure coding distribution.

Risks: Layout decisions are startup-critical; incorrect symmetry or GCD handling can produce invalid or suboptimal erasure layouts. Duplicate detection happens after expansion and catches repeated endpoints but can be expensive for very large expansions. Config-file host grouping depends on URL parsing; local paths have an empty host and cannot be mixed with distributed URLs. The environment override bypasses automatic symmetry calculations, so invalid operator choices are rejected only against divisibility/supported-size checks.

Test signals: `endpoint-ellipses_test.go` covers endpoint creation success/failure, GCD calculation, set-index selection with and without environment override, invalid and valid ellipses parsing, padded numeric ranges, multiple ellipses, Kubernetes-style host/data layouts, and IPv6 hexadecimal expansion.
<!-- END_FILE_RESEARCH: sources/object-store/minio/cmd/endpoint-ellipses.go -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio/cmd/endpoint-ellipses_test.go -->
## sources/object-store/minio/cmd/endpoint-ellipses_test.go

Purpose: This file validates endpoint ellipses parsing, erasure set-size selection, endpoint-server creation, and special expansion cases for MinIO server startup arguments.

Important APIs and functions: `TestCreateServerEndpoints` tests `mergeDisksLayoutFromArgs` plus `createServerEndpoints`. `TestGetDivisibleSize` tests GCD behavior. `TestGetSetIndexesEnvOverride` and `TestGetSetIndexes` test `getSetIndexes`. Helpers `getHexSequences` and `getSequences` build expected sequences. `TestParseEndpointSet` tests `parseEndpointSet` and expected `endpointSet` structures.

Control flow: Creation tests cover invalid empty args, malformed ranges, duplicate disks, localhost port conflicts, and valid filesystem/distributed/ellipses inputs. Set-index tests construct `ellipses.ArgPattern` values from args and assert either exact set index arrays or expected failure. Override tests pass explicit set-drive counts to verify accepted and rejected manual choices. Parse tests compare full `endpointSet` values including pattern prefixes, suffixes, generated sequences, and computed set indexes for numeric, padded numeric, multi-dimensional, Kubernetes-style, standalone, multi-ellipses, and IPv6 hexadecimal cases.

State and persistence behavior: Tests operate in memory and mutate only temporary `serverCtxt` values. No persisted layout files are written. The expected `cmdline` behavior for config-file hashing is not covered in this listed test file.

Dependencies and integration points: The file depends on `reflect`, `testing`, `fmt`, and `github.com/minio/pkg/v3/ellipses`. It exercises startup layout code and, through `createServerEndpoints`, endpoint validation functions elsewhere in the package.

Risks: Many assertions use exact deeply nested slices; this is good for regression detection but means intentional layout-selection changes require broad fixture updates. Tests cover many expansion forms but not config-file list expansion, uneven per-node config-file disk counts, mixed local/distributed config-file pools, or duplicate detection performance on huge expansions. Environment parsing itself is not exercised through the real environment variable in the override tests; they pass the override value directly into `getSetIndexes`.

Test signals: The file provides strong coverage for the core endpoint expansion and set sizing algorithms, including failure paths and real-world distributed patterns.
<!-- END_FILE_RESEARCH: sources/object-store/minio/cmd/endpoint-ellipses_test.go -->
