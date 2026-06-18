# subset-b-000028 research

Grouped research for the subset-b-000028 BuildKit files. Each file section is bounded by the required reconciliation markers and preserves the source path in the section title.

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/solver/pb/platform.go -->
# sources/cloud-native/buildkit/solver/pb/platform.go

## Purpose
This file adapts the generated solver protobuf `Platform` type to and from the OCI image-spec `ocispecs.Platform` structure. It is a small boundary layer used by source identifiers and solver metadata code that need to carry platform data through protobuf APIs without leaking protobuf-specific structs into containerd/OpenContainers helper calls.

## Important APIs
`(*Platform).Spec()` converts protobuf fields into `ocispecs.Platform`. `PlatformFromSpec` performs the reverse conversion. `ToSpecPlatforms` and `PlatformsFromSpec` map slices in both directions. `OSFeatures` is cloned with `slices.Clone` when present, which prevents callers from accidentally sharing mutable slice backing arrays between protobuf and OCI representations.

## Control Flow
All functions are straight conversions. The slice functions preallocate output to the input length and call the scalar conversion for each element. No validation or normalization is performed here; callers are expected to pass already-valid platform data.

## State and Persistence
The file has no persistent state. Its main state behavior is alias avoidance for `OSFeatures`, preserving value semantics across conversion boundaries.

## Dependencies and Integration Points
It depends only on Go `slices` and `github.com/opencontainers/image-spec/specs-go/v1`. It is used by source resolution code such as container image and blob identifiers when converting frontend/platform metadata into OCI platform structs.

## Risks
`Spec()` assumes the receiver is non-nil; a nil `*Platform` would panic. The conversions also intentionally omit any future fields not represented in the protobuf type, so schema drift must be handled when platform definitions evolve.

## Test Signals
No direct tests are in this subset. Coverage is indirect through source identifier and image pull tests that pass platform constraints into image resolution.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/solver/pb/platform.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/solver/progress.go -->
# sources/cloud-native/buildkit/solver/progress.go

## Purpose
This file exposes build progress from a `Job` as client-facing `SolveStatus` messages. It translates internal progress records into vertex updates, status bars, logs, and warnings while preserving ordering and adding final cancellation/completion updates for active vertices.

## Important APIs
`(*Job).Status(ctx, ch)` is the public streaming loop. It reads from `j.pr.Reader(ctx)` and writes `*client.SolveStatus` until EOF, error, or context cancellation. `vertexStream` tracks the last known `client.Vertex` by digest and whether a vertex was observed as cached. Its methods are `append`, `markCached`, and `encore`.

## Control Flow
`Status` reads batches from the progress reader. Each item is switched by `p.Sys` type: `client.Vertex` is passed through `vertexStream.append`; `progress.Status` becomes a `client.VertexStatus`; `client.VertexLog` and `client.VertexWarning` inherit the vertex digest and timestamp from progress metadata when missing. Before sending a status batch, vertices are sorted by start time, and status/log entries by timestamp. On EOF, the deferred block emits `vertexStream.encore()` updates and closes the channel.

## State and Persistence
State is in-memory only. `vertexStream.cache` stores mutable vertex copies, and `wasCached` records cached subgraphs. `append` also marks incomplete input vertices as cached when a downstream vertex starts and the input has not completed, producing deterministic client-side cached events for skipped vertices.

## Dependencies and Integration Points
It integrates with `client.SolveStatus`, `util/progress`, BuildKit logging, and digest metadata stored on progress records. The output channel is consumed by BuildKit clients and frontends that render solve progress.

## Risks
Progress entries without `vertex` metadata are skipped with warnings, so producer bugs can silently reduce UI detail. Type assertions on metadata assume a `digest.Digest`; malformed metadata can panic. `encore` marks active uncached vertices as canceled when the stream ends without explicit completion, which is useful for cleanup but can make abrupt stream termination look like vertex cancellation.

## Test Signals
No direct tests are in this subset. Scheduler and solver tests indirectly rely on jobs completing and being discardable, but progress rendering details are not directly asserted here.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/solver/progress.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/solver/resolvercache.go -->
# sources/cloud-native/buildkit/solver/resolvercache.go

## Purpose
This file implements the per-job `ResolverCache` contract. It serializes remote resolution work by key, lets later callers observe values published by earlier releases, and can combine several resolver caches into one parallel fan-out cache.

## Important APIs
`newResolverCache()` constructs the mutex-protected map. `(*resolverCache).Lock(key)` either acquires the key immediately or waits for the current holder to release it. The returned `release(value)` optionally appends a non-nil value to the key's accumulated values. `combinedResolverCache` returns a `combinedCache`, whose `Lock` calls all child caches concurrently and merges values and releasers.

## Control Flow
For a local cache, `Lock` creates or finds an `entry`. If it is unlocked, it marks it locked and returns a clone of current values plus a release closure. If locked, it appends a wait channel, blocks until release closes it, then rechecks the map and takes the lock if still present. Release appends the value, wakes all waiters, clears waiting channels, unlocks the entry, and deletes the key if there are still no values.

For a combined cache, each child `Lock` runs in its own goroutine. Values and releasers are collected under a mutex. If any child fails, all already-acquired releasers are called with nil for rollback.

## State and Persistence
All state is process memory. Values persist for a key until the cache object is discarded; nil releases do not add values and can delete an empty entry.

## Dependencies and Integration Points
It depends on `sync` and `slices`. The interface is exposed through `JobContext.ResolverCache()` and used by source resolvers to deduplicate registry or remote resolution decisions inside a solve.

## Risks
`Lock` waits without a context, so a caller that never invokes release can block all waiters indefinitely. Combined cache releases are sequential; a slow child release delays the combined release. Only the first release error is reported.

## Test Signals
`resolvercache_test.go` covers serial accumulation, concurrent waiters, independent keys, nil release deletion, sequential locks, combined value merge, empty combined caches, rollback on child error, and release error propagation.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/solver/resolvercache.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/solver/resolvercache_test.go -->
# sources/cloud-native/buildkit/solver/resolvercache_test.go

## Purpose
This file is the focused test suite for `resolverCache` and `combinedResolverCache`. It documents the intended synchronization, value accumulation, rollback, and error propagation behavior of the resolver cache abstraction.

## Important Tests and Helpers
`TestResolverCache_SerialAccess` verifies that released non-nil values are returned to later lock holders. `TestResolverCache_ConcurrentWaiters` proves waiters block while a key is locked and receive the released value afterward. `TestResolverCache_MultipleIndependentKeys` checks isolation by key. `TestResolverCache_ReleaseNilDoesNotAdd` and `TestResolverCache_SequentialLocks` cover empty release and repeated accumulation. `mockResolverCache` implements `ResolverCache` for combined-cache tests.

The combined-cache tests validate parallel child locking, value merging, empty input behavior, rollback when one child fails, and release error propagation while still calling every child releaser.

## Control Flow
The tests use direct lock/release calls rather than a full solver job. Concurrency is exercised with `sync.WaitGroup`, result channels, and a short timeout asserting that waiter goroutines are actually blocked before release.

## State and Persistence
The tests assert in-memory state only: values persist across locks, key state is independent, and nil release avoids adding durable values. Combined-cache tests track release side effects in local slices and counters.

## Dependencies and Integration Points
The suite imports `testify/assert` and `testify/require`, plus `github.com/pkg/errors` for synthetic failure paths. It directly exercises unexported constructors because it lives in package `solver`.

## Risks Covered
The tests cover deadlocks for normal release, duplicated key values, missing rollback, and partial release failures. They do not cover a lock holder that never releases, because the production API has no context-aware wait cancellation.

## Test Signals
Strong local signal for resolver cache behavior. These tests are narrow and deterministic except for the 100 ms waiter-blocking timeout, which is short but acceptable for the intended synchronization assertion.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/solver/resolvercache_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/solver/result.go -->
# sources/cloud-native/buildkit/solver/result.go

## Purpose
This file implements shared and split wrappers for solver `Result`, `CachedResult`, and `ResultProxy` lifetimes. It lets multiple consumers clone references while ensuring the underlying result or proxy is released exactly once after all split references are released.

## Important APIs
`NewSharedResult` wraps a `Result`. `(*SharedResult).Clone` replaces the stored main reference with one half of `dup` and returns the other half. `NewCachedResult` attaches exportable cache keys to a result. `NewSharedCachedResult`, `CloneCachedResult`, and `clonedCachedResult.CacheKeys` preserve cache-key access across cloned cached results. `SplitResultProxy` does the same split-release logic for `ResultProxy`.

## Control Flow
`dup` creates two `splitResult` values sharing an atomic semaphore. Each split has its own atomic `released` guard. On release, the split detects double release, logs an error, and returns it; otherwise it increments the shared semaphore and only calls the underlying `Result.Release` when both halves have released. `SharedResult.Clone` repeats this pattern under a mutex, creating a chain of split results as more clones are requested.

## State and Persistence
State is in memory: a mutex protects the current main reference, and atomics protect per-split and shared release counts. No data is persisted, but release timing controls cache reference and snapshot lifetimes elsewhere in the solver.

## Dependencies and Integration Points
It depends on BuildKit logging, `pkg/errors`, and the solver result interfaces from `types.go`. Scheduler/cache code returns `SharedCachedResult` instances so multiple jobs or merged edges can consume the same cached result safely.

## Risks
Release correctness depends on every clone eventually being released. A missing release leaks the underlying result. A double release returns an error and logs, but cannot undo side effects from any previous release chain. Cache keys in `clonedCachedResult` are delegated to the original cached result, so callers must treat cache-key slices as immutable.

## Test Signals
`scheduler_test.go` includes `TestSlowCacheErrorResultCloneRelease`, which checks that a result returned inside `SlowCacheError` is not released with the job and releases exactly once when the error-held result is explicitly released.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/solver/result.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/solver/result/attestation.go -->
# sources/cloud-native/buildkit/solver/result/attestation.go

## Purpose
This file defines generic attestation payload metadata attached to BuildKit results. It covers SBOM/provenance attestation reasons, inline-only/core metadata keys, in-toto subject information, digest map conversion, and reference conversion across result backends.

## Important APIs and Types
`Attestation[T]` holds the frontend attestation kind, metadata, an optional typed reference, path, lazy `ContentFunc`, and `InTotoAttestation`. `InTotoAttestation` contains a predicate type and `InTotoSubject` entries. `ToDigestMap` and `FromDigestMap` convert between digest slices and algorithm-to-encoded maps. `ConvertAttestation` maps a referenced value from `U` to `V` while preserving metadata, path, content callback, and in-toto data.

## Control Flow
The digest map helpers iterate directly over their inputs. `ConvertAttestation` checks the zero value of the source type: zero refs are preserved as zero refs without calling the transformer, while non-zero refs are transformed and errors are returned immediately.

## State and Persistence
No persistent state is owned here. Metadata maps, content functions, and in-toto structures are passed through by reference, so callers should treat them as immutable or copy them before mutation.

## Dependencies and Integration Points
It depends on gateway protobuf attestation enums, `context`, and OCI digest types. It is consumed by `solver/result/result.go` and by image/exporter paths that attach SBOM and provenance information to result references.

## Risks
`ToDigestMap` collapses multiple digests with the same algorithm, keeping the last encoded value. `FromDigestMap` has map iteration order nondeterminism. `ConvertAttestation` does not deep-copy metadata or in-toto slices, so mutation after conversion can affect both versions.

## Test Signals
No direct tests in this subset. It is indirectly exercised by generic result conversion logic and exporter/provenance paths elsewhere.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/solver/result/attestation.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/solver/result/result.go -->
# sources/cloud-native/buildkit/solver/result/result.go

## Purpose
This file defines a generic result container for one primary reference, named reference maps, metadata, and attestations. It provides helper methods for adding, finding, iterating, comparing, and converting typed references.

## Important APIs
`Result[T]` stores `Ref`, `Refs`, `Metadata`, and `Attestations`. Methods include `Clone`, `AddMeta`, `AddRef`, `AddAttestation`, `SetRef`, `SingleRef`, `FindRef`, `EachRef`, and `IsEmpty`. Package functions `EachRef` and `ConvertResult` coordinate references between two results or convert all references from one comparable type to another.

## Control Flow
Mutation methods lazily allocate maps under a mutex. `SingleRef` rejects a map-only result where the primary ref is the zero value. `FindRef` returns an exact named ref, falls back to the only map entry if there is exactly one, and otherwise reports false. `EachRef` walks the primary ref, map refs, and attestation refs, returning the first error but continuing iteration. `ConvertResult` applies a transformer to non-zero refs and delegates attestation conversion to `ConvertAttestation`.

## State and Persistence
State is in memory. The mutex protects some methods, but `Clone`, package-level `EachRef`, and `ConvertResult` read fields without locking; callers should avoid concurrent mutation during these operations. `Clone` shallow-copies maps and slices, not metadata byte slices or attestation slices' nested fields.

## Dependencies and Integration Points
It uses Go `maps`, `sync`, and `pkg/errors`. It is the common result shape used by BuildKit frontends and exporters for multi-output references and attested artifacts.

## Risks
The mix of locked and unlocked access can race if callers mutate results concurrently. Shallow metadata copies can share byte slices. `EachRef` assumes paired results have matching keys and attestation ordering; mismatches are silently skipped.

## Test Signals
No direct tests in this subset. Behavior is indirectly covered where result references are converted or exported, but concurrency assumptions are not locally tested.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/solver/result/result.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/solver/scheduler.go -->
# sources/cloud-native/buildkit/solver/scheduler.go

## Purpose
This file is the event scheduler for BuildKit solver edges. It owns the dispatch loop that unparks edges, routes pipe requests between dependent edges, handles asynchronous function requests, and merges equivalent edges when cache-key state proves they can share work.

## Important APIs and Types
`newScheduler` creates a `scheduler`, initializes wait queues and pipe maps, and starts `loop`. `scheduler.Stop` stops the loop. `dispatch` is the core edge-processing method. `signal` enqueues an edge for dispatch exactly once. `build` creates a completion request pipe and returns a cloned cached result. `newPipe`, `newRequestWithFunc`, and `pipeFactory` connect `edge.unpark` to input and function requests. `mergeTo` rewires pipes and secondary exporters from a source edge to a target edge.

## Control Flow
The scheduler loop waits on a stateful condition, pops a queued dispatcher from `next/last`, removes it from `waitq`, and calls `dispatch`. Dispatch receives outgoing pipe updates, records whether active outgoing requests remain, calls `e.unpark`, prunes completed incoming/outgoing pipes, then considers cache-key based merging. Merge is skipped if edges are dependencies of each other or if an ignore-cache edge would incorrectly merge into a non-ignore-cache target. On successful merge, incoming pipes are retargeted, outgoing pipes are moved and canceled, the target is signaled, and secondary exporter data is copied from the source.

## State and Persistence
State is in-memory scheduler state: wait queue membership, linked dispatch queue, incoming and outgoing pipe lists, and condition state. It does not persist data, but it controls result lifetime indirectly through active edges and pipes.

## Dependencies and Integration Points
It depends on solver `edge` internals, `solver/internal/pipe`, `util/cond`, `errdefs`, and scheduler debug hooks. `edgeFactory` bridges the scheduler to the shared active graph maintained by the solver.

## Risks
Deadlocks can arise if `edge.unpark` leaves only incoming or only outgoing pipes open; the scheduler detects this and marks the edge failed with an internal error. Merge correctness is delicate: dependency cycles, stale owners, ignore-cache semantics, and secondary exporter propagation all need to stay consistent with edge state.

## Test Signals
`scheduler_test.go` heavily exercises this behavior: active graph sharing, parallel builds, cancellations, slow cache, selectors, cache export, merged edge races/cycles, stale edge merge, load failures, and input request deadlock regressions.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/solver/scheduler.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/solver/scheduler_test.go -->
# sources/cloud-native/buildkit/solver/scheduler_test.go

## Purpose
This large suite is the main behavioral specification for the solver scheduler, active graph, cache lookup, slow-cache calculation, result sharing, and cache export interactions.

## Important Tests and Fixtures
The early tests cover single-level active graph sharing, cache hits, parallel cache deduplication, cancellation in cache and exec phases, multi-level calculations, huge random graphs, optimized cache access, slow-cache hits, parallel inputs, error propagation, multiple cache sources, ignore-cache behavior, subbuilds, selectors, cache export modes, multiple cache maps, and partial selector export. Later tests target merged-edge races and regressions: merged edge lookup, cycle avoidance, multiple owners, missing cache records, cache load failure fallback, input request deadlock, unknown job IDs, and stale edge merge cleanup.

The fixture types `vertex`, `vertexConst`, `vertexSum`, `vertexAdd`, and `vertexSubBuild` implement both `Vertex` and `Op` patterns. They synthesize cache maps, execute deterministic dummy results, support slow cache functions/selectors/multiple cache maps, and count cache/exec calls with atomics. `trackingCacheManager` counts and optionally fails cache loads. `testExporterTarget` records exported cache graph records.

## Control Flow
Tests construct solvers with `ResolveOpFunc: testOpResolver`, create jobs, build `Edge` graphs, assert returned dummy values, and discard jobs to exercise active state cleanup. Parallelism uses `errgroup`, blocking functions, and repeated loops to surface races. Many assertions compare cache/exec counts and load counts to confirm that the scheduler avoids unnecessary work.

## State and Persistence
The tests inspect active solver maps, result release counters, in-memory cache managers, and exporter target records. They intentionally discard jobs at different times to validate active edge reference tracking.

## Dependencies and Integration Points
The suite is package-internal and reaches solver internals such as `actives`, `cacheManager`, `inMemoryStore`, and exporter implementations. It integrates with `session.Group`, OCI descriptors, BuildKit identity generation, and `testify/require`.

## Risks Covered
It covers duplicate execution, cache overloading, cancellation cause confusion, slow-cache result leaks, merged-edge cycles, stale active graph ownership, cache load fallback, and cache export graph shape. Because the fake vertices are synthetic, registry/image/git source behaviors are covered elsewhere.

## Test Signals
This is a high-signal regression suite for scheduler correctness. Several race-prone cases run multiple iterations, and call-count assertions give precise evidence for cache and execution decisions.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/solver/scheduler_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/solver/testutil/cachestorage_testsuite.go -->
# sources/cloud-native/buildkit/solver/testutil/cachestorage_testsuite.go

## Purpose
This file defines a reusable conformance suite for implementations of `solver.CacheKeyStorage`. It verifies result storage, cache links, release cascading, backlinks, and reverse lookup by result ID.

## Important APIs
`RunCacheStorageTests` accepts a factory for a fresh `CacheKeyStorage` and runs six test functions. `runStorageTest` wraps each case in a named subtest. The individual tests are `testResults`, `testLinks`, `testResultReleaseSingleLevel`, `testBacklinks`, `testResultReleaseMultiLevel`, and `testWalkIDsByResult`. Helpers `getFunctionName` and `rootKey` provide readable subtest names and expected backlink digests.

## Control Flow
Each test gets a new storage instance. Result tests add results with timestamps, walk by key, and load by key/result ID. Link tests add multiple targets under the same link and walk them. Release tests remove result IDs and check whether cache IDs and graph links are retained or pruned. Backlink tests verify reverse edges from child cache IDs to parent links. Reverse lookup tests walk all cache IDs associated with a result ID.

## State and Persistence
The suite exercises storage semantics but owns no persistent state itself. It assumes each storage factory returns isolated state. Several tests run in parallel, so implementations must tolerate independent concurrent test processes over separate instances.

## Dependencies and Integration Points
It imports `solver`, OCI digest, `pkg/errors`, and `testify/require`. It is used by storage implementation tests, including the in-memory cache storage test in this subset.

## Risks Covered
The suite catches orphaned links after release, accidental parent deletion while children still reference it, missing backlink root-key normalization, incorrect not-found errors, and missing reverse result indexes. It does not test durable on-disk crash recovery.

## Test Signals
Strong contract-level signal for cache storage implementations. The Windows timestamp guard avoids false failures from coarse clock resolution.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/solver/testutil/cachestorage_testsuite.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/solver/testutil/memorycachestorage_test.go -->
# sources/cloud-native/buildkit/solver/testutil/memorycachestorage_test.go

## Purpose
This file binds the generic cache storage conformance suite to the in-memory storage implementation. It is intentionally tiny: all behavioral coverage lives in `cachestorage_testsuite.go`.

## Important APIs
`TestMemoryCacheStorage` calls `RunCacheStorageTests(t, solver.NewInMemoryCacheStorage)`.

## Control Flow
The single test delegates to the reusable suite, which creates fresh storage instances per subtest and validates result, link, release, backlink, and reverse lookup behavior.

## State and Persistence
The implementation under test is in-memory, so there is no durable persistence. The test ensures the memory-backed storage maintains consistent graph state during the process lifetime.

## Dependencies and Integration Points
It depends on package `solver/testutil` and `solver.NewInMemoryCacheStorage`. It provides direct regression coverage for the default memory storage used by many solver tests.

## Risks
Because this file only delegates, failures point to either the implementation or the shared suite. It does not add in-memory-specific edge cases beyond the common storage contract.

## Test Signals
High signal as a smoke and conformance test for the in-memory backend; detailed assertions are inherited from the suite.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/solver/testutil/memorycachestorage_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/solver/types.go -->
# sources/cloud-native/buildkit/solver/types.go

## Purpose
This file defines the central solver interfaces and data contracts: graph vertices, operation execution, result lifetimes, cache export, cache lookup, remote descriptors, and job-scoped services.

## Important APIs and Types
`Vertex`, `Edge`, `Index`, `VertexOptions`, and `VertexMetadata` model the build graph. `Result`, `CachedResult`, `CachedResultWithProvenance`, and `ResultProxy` model solver outputs. `Op` defines cache mapping, execution, and resource acquisition. `JobContext` exposes session, cleanup, resolver cache, and compatibility version. Cache contracts include `CacheMap`, `CacheManager`, `CacheRecord`, `ExportableCacheKey`, `CacheExporter`, `CacheExporterTarget`, `CacheLink`, `CacheExportResult`, `CacheExportOpt`, and `Remote`.

## Control Flow
This file is declarative except for `CacheExporterRecordBase.isCacheExporterRecord` and `(*CacheRecord).TraceFields`. Control flow is imposed by implementers: solver edges call `Op.CacheMap`, use `CacheManager.Query/Records/Load/Save`, run `Op.Exec` when no cache hit exists, and export records through `CacheExporter.ExportTo`.

## State and Persistence
The types describe both transient and persistent-ish state. `CacheRecord` carries stored record metadata such as ID, size, creation time, and priority. `Remote` describes content descriptors and providers used for transferable cache/image data. `JobContext.Cleanup` lets sources attach temporary resources to job lifetime.

## Dependencies and Integration Points
Dependencies include containerd content APIs, BuildKit sessions, protobuf progress groups, compression config, OCI descriptors, and digests. All solver source implementations in this subset implement or consume these interfaces.

## Risks
The contracts rely on implementers preserving cache-key purity: `CacheMap.Opts` must not affect computed cache keys, while `Digest`, selectors, and content digest functions must. Mutable slices/maps such as cache sources, descriptions, and descriptors should be treated carefully to avoid cross-solve mutation.

## Test Signals
The scheduler and cache storage tests exercise many of these contracts through fake `Op`, `CacheManager`, `Result`, and exporter implementations. Source-specific tests elsewhere validate registry/git/image implementations.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/solver/types.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/source/containerblob/blobfetch/fetch.go -->
# sources/cloud-native/buildkit/source/containerblob/blobfetch/fetch.go

## Purpose
This package provides a shared helper for fetching a single content-addressed blob from either a registry-backed docker-image blob source or a client-side OCI layout content store. It is factored so both the container blob source and git bundle flow can reuse the same blob locator logic.

## Important APIs
`FetchOpt` carries scheme, reference, digest, registry hosts, session manager, optional session ID, and OCI store ID. `FetchBlob` validates the digest, dispatches by scheme, and returns an owned `io.ReadCloser` plus the digest. `fetchFromOCILayoutStore` reads from a session content store. `withOCICaller` selects either a pinned session or any caller in a session group.

## Control Flow
For `OCIBlobScheme`, `FetchBlob` requires `StoreID`, gets a caller, opens `sessioncontent.NewCallerStore(caller, "oci:"+StoreID)`, reads content info, and wraps `ReaderAt` as a read closer. For `DockerImageBlobScheme`, it obtains a resolver from the default pool, creates a fetcher for the ref, asserts `remotes.FetcherByDigest`, and fetches the digest directly.

## State and Persistence
No local persistent state. Registry and OCI content are external. Returned readers must be closed by callers. Pinned OCI sessions use a five-second lookup timeout before falling back to the parent context for actual IO.

## Dependencies and Integration Points
It depends on containerd remotes/docker, BuildKit sessions/content, source type scheme constants, resolver pool, and IO helpers. It is used by `containerblob/pull.go` and `source/git/bundle.go`.

## Risks
Unsupported schemes fail fast. OCI layout calls require a non-nil session manager and valid store ID. Registry fetchers must implement `FetcherByDigest`; otherwise the function returns an explicit type error. There is no size cap at this layer, so callers must handle large streams safely.

## Test Signals
No direct tests in this subset. Git bundle identifier tests validate locator parsing, while integration-style source tests elsewhere would cover actual fetch behavior.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/source/containerblob/blobfetch/fetch.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/source/containerblob/identifier.go -->
# sources/cloud-native/buildkit/source/containerblob/identifier.go

## Purpose
This file defines the identifier for a single image blob source. It parses digest-qualified blob references, stores file materialization attributes, and records provenance for blob inputs.

## Important APIs and Types
`ImageBlobIdentifier` stores a containerd `reference.Spec`, scheme name, optional OCI session/store IDs, usage record type, output filename, permissions, UID, and GID. `NewImageBlobIdentifier` parses a reference and requires an object digest. `Scheme` defaults to `DockerImageBlobScheme` when unset. `Capture` validates the pinned digest and records an image blob source in provenance.

## Control Flow
Construction parses the input string and rejects references without an object. `Capture` parses the solver-provided pin, requires the reference object to be an `@digest`, parses that digest, compares it to the pin, and adds provenance with `Local` set for OCI-layout blobs.

## State and Persistence
The identifier itself is immutable after parsing except for attributes populated by `source.go`. It does not persist content. Its fields influence cache keys and snapshot materialization in `pull.go`.

## Dependencies and Integration Points
It depends on containerd reference parsing, BuildKit client usage record types, source scheme constants, provenance capture types, and OCI digest parsing. `containerblob/source.go` creates and populates these identifiers.

## Risks
Digest mismatch in `Capture` fails the provenance path, which protects correctness but can surface late depending on capture timing. The constructor only requires an object; stronger digest validation happens later through `Reference.Digest().Validate` in the puller.

## Test Signals
No direct tests in this subset. Behavior is indirectly validated by blob source resolution and provenance tests elsewhere.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/source/containerblob/identifier.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/source/containerblob/pull.go -->
# sources/cloud-native/buildkit/source/containerblob/pull.go

## Purpose
This file implements the source instance that turns a single image/blob digest into a one-file snapshot. It fetches the blob, computes a stable cache key from digest and file attributes, writes the blob into a new cache ref, and commits the snapshot.

## Important APIs and Types
`puller` stores the source, identifier, session manager, cached read closer, and digest. `hash` returns a digest over the blob digest plus filename, permission, UID, and GID. `ensureResolver` opens the blob stream through `blobfetch.FetchBlob`. `CacheKey` returns the stable hash and image digest. `Snapshot` materializes the file into a cache mount.

## Control Flow
`CacheKey` validates the reference digest, checks the content store for existing content/source metadata, and returns the hash as a completed cache key regardless of whether the content already exists. `Snapshot` gets the session group, ensures a reader, creates a retained mutable cache ref, mounts it, chooses the file mode and safe filename, opens the mount root with `os.OpenRoot`, writes the stream while hashing, applies identity-mapped ownership if needed, normalizes mtime to Unix epoch, unmounts, and commits.

## State and Persistence
The persistent artifact is the committed cache snapshot containing one file. Temporary state includes `p.rc`, which is closed and cleared after snapshot. File metadata is deterministic: default mode 0600, name defaults to digest hex, and mtime is zero.

## Dependencies and Integration Points
It depends on BuildKit cache, snapshot local mounter, sessions, content store, blobfetch, path utilities, and OCI digest. It implements the source instance methods expected by the solver.

## Risks
The code computes a SHA256 while copying but does not compare it to `p.dgst`; integrity relies on upstream fetch/content validation. Snapshot cleanup is carefully deferred, but mount unmount errors are only captured through the main error path. Large blobs stream directly into the snapshot and can consume disk.

## Test Signals
No direct tests in this subset. Related coverage should come from source integration tests that assert cache keys, file metadata, and registry/OCI fetch behavior.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/source/containerblob/pull.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/source/containerblob/source.go -->
# sources/cloud-native/buildkit/source/containerblob/source.go

## Purpose
This file registers the container blob source for docker-image blob and OCI-layout blob schemes. It parses frontend attributes into `ImageBlobIdentifier` values and resolves them into `puller` source instances.

## Important APIs
`SourceOpt` carries the content store, cache accessor, and registry host resolver config. `NewSource` constructs `Source`. `Schemes` returns supported blob schemes. `Identifier` dispatches by scheme. `Resolve` type-checks identifiers and returns a `puller`. `registryIdentifier`, `ociLayoutIdentifier`, `parseIdentifierAttrs`, and `parseImageRecordType` handle attributes.

## Control Flow
`Identifier` chooses registry or OCI path. Both create a base `ImageBlobIdentifier`; OCI additionally requires `StoreID`. `parseIdentifierAttrs` accepts HTTP-style filename/permission/UID/GID attributes, image usage record type, and OCI session/store IDs only when allowed. Unknown attributes are ignored.

## State and Persistence
`Source` is a thin holder for content/cache/registry dependencies. Identifier attributes become state on the puller and affect cache keys and file materialization. No content is persisted until `puller.Snapshot`.

## Dependencies and Integration Points
It integrates with BuildKit source registry interfaces, solver sessions, protobuf attribute constants, cache/content backends, Docker registry hosts, and safe filename utilities.

## Risks
Unknown attributes being ignored can hide frontend typos. Numeric attributes are parsed as base-0 integers, so octal-style values are accepted. OCI store/session attributes are ignored for registry blobs by design. Invalid record types and missing OCI store IDs fail early.

## Test Signals
No direct tests in this subset. The attribute parser mirrors container image source parsing, and integration tests should cover the resulting snapshot and usage record behavior.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/source/containerblob/source.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/source/containerimage/identifier.go -->
# sources/cloud-native/buildkit/source/containerimage/identifier.go

## Purpose
This file defines source identifiers for registry images and client-side OCI layout images. Identifiers store parsed references, platform constraints, resolve mode, record type, layer limit, checksum, and OCI layout session/store data.

## Important APIs and Types
`ImageIdentifier` is used for `docker-image://` style sources. `NewImageIdentifier` parses and requires a reference object. `Scheme` returns `DockerImageScheme`, and `Capture` records image provenance. `OCIIdentifier` is the analogous local OCI-layout identifier with session/store fields; its `Scheme` returns `OCIScheme`, and `Capture` records the image as local provenance.

## Control Flow
Both constructors parse containerd references and reject missing objects. Both `Capture` methods parse the pinned digest and call `provenance.Capture.AddImage`, including platform and digest. OCI capture sets `Local: true`.

## State and Persistence
Identifiers are per-source state. They do not persist content but drive resolver selection, cache-key calculation, layer limiting, and provenance capture in `source.go` and `pull.go`.

## Dependencies and Integration Points
Dependencies include containerd reference parsing, BuildKit provenance types, source scheme constants, resolver mode, client usage record types, OCI platform/digest types, and solver frontend attributes parsed elsewhere.

## Risks
Constructors require a reference object, which means callers must provide tag or digest-qualified refs according to containerd parser expectations. Capture validates only the pin digest string, not that it equals the original reference digest; resolution code is responsible for final digest behavior.

## Test Signals
No direct tests in this subset. Identifier behavior is normally exercised through source identifier parsing tests and provenance capture tests elsewhere.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/source/containerimage/identifier.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/source/containerimage/ocilayout.go -->
# sources/cloud-native/buildkit/source/containerimage/ocilayout.go

## Purpose
This file implements a containerd `remotes.Resolver`/`Fetcher` backed by a client-side OCI layout content store exposed over a BuildKit session. It lets the normal image resolution and pull utilities operate against local OCI content.

## Important APIs and Types
`getOCILayoutResolver` constructs an `ociLayoutResolver` for a store/session group. `Fetcher` returns the resolver as its own fetcher. `Fetch` opens content by descriptor from `sessioncontent.NewCallerStore`. `Resolve` maps a digest-qualified reference to a descriptor with detected media type. `info` reads content info, and `withCaller` selects a pinned or group session caller.

## Control Flow
`Resolve` parses the ref, requires a digest, gets content info from the remote store, creates a descriptor with digest and size, fetches the root blob, reads up to `maxReadSize` bytes, detects whether it is an image manifest or index, and sets descriptor media type. `Fetch` and `info` use `withCaller`; pinned sessions use a five-second lookup timeout.

## State and Persistence
No local durable state. The resolver reads remote content through the session. `maxReadSize` limits root manifest media-type probing to 4 MiB.

## Dependencies and Integration Points
It integrates with BuildKit `sourceresolver.ResolveImageConfigOptStore`, sessions, session content stores, containerd remotes/content interfaces, reference parsing, and image media-type detection. It is used by container image source metadata and pull paths when resolver type is OCI layout.

## Risks
OCI layout tag references are not supported; references must include a digest. Missing or wrong store IDs fail at session content lookup. The root manifest reader is not explicitly closed after `io.ReadAll`, which relies on the wrapped reader's lifecycle and could be tightened. Large or malformed root blobs fail media type detection.

## Test Signals
No direct tests in this subset. It is covered indirectly by OCI layout source integration tests outside this subset.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/source/containerimage/ocilayout.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/source/containerimage/pull.go -->
# sources/cloud-native/buildkit/source/containerimage/pull.go

## Purpose
This file implements image source cache-key and snapshot behavior. It resolves manifests, computes stable manifest/config cache keys, wires descriptor handlers for lazy layer fetch/progress, applies layer limits/checksums, and materializes image layers into cache refs.

## Important APIs and Types
`puller` embeds `*pull.Puller` and holds cache, lease, resolver, image store, record type, session, layer limit, checksum, manifest state, descriptor handlers, and `flightcontrol.Group` state. `mainManifestKey` hashes manifest digest plus platform and layer limit. `CacheKey` resolves/pulls metadata and returns either manifest or config cache keys. `Snapshot` materializes layers. `cacheKeyFromConfig` prefers OCI chain ID when possible.

## Control Flow
`CacheKey` chooses a registry or OCI-layout resolver, then runs resolution once through `p.g.Do`. It creates a temporary lease, emits resolve progress, calls `PullManifests`, checks expected checksum, enforces layer limit, creates descriptor handlers with inherited labels and estargz snapshot labels, computes the manifest key, reads config, computes config key, and marks cache-key work done. It returns the manifest key for index 0; later indexes can return the config key and set `cacheDone`.

`Snapshot` reconstructs the resolver, returns nil for empty layer sets, releases temporary leases on exit, walks layer descriptors through `CacheAccessor.GetByBlob`, releases parents, marks Windows layers when needed, ensures non-layer blobs still exist or re-pulls manifests, attaches non-layer content to the final ref lease, sets record type, and returns the final immutable ref.

## State and Persistence
Persistent artifacts include pulled content in the content store, cache snapshots for layer chains, and lease resource links. Temporary leases are held between cache-key and snapshot phases and released after snapshot.

## Dependencies and Integration Points
It depends on containerd content/images/leases/remotes/snapshots, BuildKit cache, sessions, source resolver options, progress controller, pull utilities, resolver pool, estargz labels, and OCI image identity.

## Risks
State spans `CacheKey` and `Snapshot`; callers must run them in the expected solver lifecycle. Layer limits can change both manifest and config keys. Manifest/config blobs can be garbage-collected between phases, so `Snapshot` has a re-pull path. Cache load failures fall back to execution in scheduler tests, but source-specific IO errors still fail the solve.

## Test Signals
`scheduler_test.go` exercises generic cache-key/load fallback behavior, not image-specific pulling. Image pull behavior should be covered by container image integration tests elsewhere.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/source/containerimage/pull.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/source/containerimage/source.go -->
# sources/cloud-native/buildkit/source/containerimage/source.go

## Purpose
This file registers and resolves container image sources for registry and OCI-layout modes, parses image attributes, and exposes metadata resolution helpers used by frontends. It also resolves attestation chains for registry images.

## Important APIs and Types
`ResolverType` distinguishes registry and OCI layout. `SourceOpt` carries snapshotter, content store, applier, cache accessor, optional image store, registry hosts, resolver type, and lease manager. `Source` stores options and two `flightcontrol.Group`s for image config and attestation chain deduplication. Key methods are `NewSource`, `Schemes`, `Identifier`, `Resolve`, `ResolveImageMetadata`, `ResolveOCILayoutMetadata`, `registryIdentifier`, `ociIdentifier`, `addAttestationBlobs`, and `parseImageRecordType`.

## Control Flow
`Resolve` type-checks the identifier by resolver type, derives platform/defaults, resolve mode, record type, ref, store, layer limit, and checksum, builds a `pull.Puller`, and returns the local `puller`. `ResolveImageMetadata` creates a registry resolver with image-store behavior, fetches config through `imageutil.Config`, falls back to local image store when allowed, and optionally resolves an attestation chain from an image index. Attestation resolution reads signature/attestation manifests and selected predicate blobs, stores blobs in the response, and sets GC labels. `ResolveOCILayoutMetadata` uses `getOCILayoutResolver` and returns config metadata only.

`registryIdentifier` and `ociIdentifier` parse frontend attributes into identifier fields, including platform clones, resolve mode, record type, positive layer limits, checksum, and OCI session/store IDs.

## State and Persistence
`Source` persists no content directly but holds backend handles and in-flight deduplication groups. Metadata resolution creates temporary leases for registry attestation/config content; those leases expire or are pruned later.

## Dependencies and Integration Points
It integrates with BuildKit source APIs, solver, cache, sessions, image resolver frontend APIs, policy-helper image referrers, containerd content/diff/images/leases, resolver pool, image utilities, and provenance capture.

## Risks
Attribute parsing ignores unknown keys. Attestation chain resolution only proceeds for image indexes; non-index images return nil chains. Digest mismatches between config and attestation root are hard errors. OCI layout metadata requires a store ID from opts or identifier.

## Test Signals
No direct tests in this subset. The source's generic solver interactions are covered by scheduler/cache tests; registry/OCI metadata and attestation paths need integration tests with content stores and sessions.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/source/containerimage/source.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/source/git/bundle.go -->
# sources/cloud-native/buildkit/source/git/bundle.go

## Purpose
This file implements git bundle import and checkout-bundle support. Bundle import lets a git source fetch commits from a digest-addressed blob rather than the remote repository. Checkout-bundle mode emits a single `bundle` file instead of a worktree.

## Important APIs
Constants define `bundleFileName`, transient import filename, and fallback ref. `bundleTargetRef` normalizes user refs for emitted bundles. `detectBundleSHA256` probes bundle object format. `stageBundle`, `ensureStagedBundle`, and `releaseStagedBundle` manage temporary imported bundle repos. `downloadBundleToFile` and `openBundleBlob` fetch and verify bundle blobs. `resolveBundleMetadata` handles metadata lookup in bundle mode. `checkoutAsBundle` and `writeBundleToMount` create the output bundle snapshot safely.

## Control Flow
Import flow parses the bundle locator, creates a temp directory, downloads the blob through `blobfetch`, verifies SHA256 digest, detects object format via `git ls-remote`, initializes a temp bare repo, fetches all refs from the bundle, and checks the pinned commit exists. `ensureStagedBundle` caches the staged file URL and registers idempotent cleanup with `JobContext.Cleanup` when available. Metadata resolution skips staging for empty/SHA refs because the checksum already pins the commit.

Checkout-bundle flow creates a mutable cache ref, mounts it, builds an isolated temp bare repo, fetches the pinned commit from the shared repo, updates a natural target ref, runs `git bundle create`, and copies the staged bundle into the mount through `os.OpenRoot`.

## State and Persistence
Temporary bundle repos live under OS temp directories and are cleaned by job cleanup or explicit handler release. Checkout-bundle persists a committed cache snapshot containing one file named `bundle`.

## Dependencies and Integration Points
It integrates with solver job cleanup, BuildKit cache/snapshot/session, git CLI helpers, `blobfetch`, source type schemes, and git source handler fields such as registry hosts, session manager, cache, and SHA256 object-format state.

## Risks
Cleanup registration is critical; staging without a job context relies on later handler teardown. Blob fetch can stream large bundles to disk. Security-sensitive writes use `os.OpenRoot` and temp staging to avoid symlink escape. Only SHA256 bundle blob digests are accepted, matching the verification hasher.

## Test Signals
`identifier_test.go` covers static bundle locator and checkout-bundle validation. Runtime staging, import, cleanup, and checkout-bundle materialization require integration tests with git and blob stores.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/source/git/bundle.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/source/git/identifier.go -->
# sources/cloud-native/buildkit/source/git/identifier.go

## Purpose
This file defines `GitIdentifier`, git signature verification options, URL parsing, provenance capture, and static validation for git bundle-related attributes.

## Important APIs and Types
`GitIdentifier` stores remote URL, ref, checksum, subdir, auth/SSH options, submodule and mtime behavior, fetch-by-commit, bundle locator/session/store overrides, checkout-bundle flag, and signature verification options. `GitSignatureVerifyOptions` stores public key and signed tag policy. `NewGitIdentifier` normalizes non-transport remotes to HTTPS and parses git URL options. `Scheme` returns `GitScheme`. `Capture` records git provenance and secret/SSH dependencies. `validateBundleAttrs`, `splitBundleLocator`, and `parseBundleLocator` enforce bundle constraints.

## Control Flow
`NewGitIdentifier` checks transport, prepends `https://` if needed, parses with `gitutil.ParseURL`, and copies ref/subdir options. `Capture` appends `#ref` for provenance URL display, records the pinned commit, adds bundle provenance when set, and records optional auth/SSH inputs. `validateBundleAttrs` parses the bundle locator, requires checksum, rejects mismatched SHA refs, and checks checkout-bundle incompatibilities. `parseBundleLocator` avoids `net/url`, parses the body with containerd reference parsing, validates digest and scheme, and requires SHA256.

## State and Persistence
Identifiers hold solve-time configuration only. Bundle fields influence later staging and checkout behavior. Provenance capture writes to the passed capture object.

## Dependencies and Integration Points
It depends on BuildKit git utilities, source type constants, provenance types, containerd reference parsing, and OCI digests. `Source.Identifier` elsewhere populates fields and invokes `validateBundleAttrs`.

## Risks
Bundle locator parsing supports only `docker-image+blob` and `oci-layout+blob`. Requiring SHA256 protects `downloadBundleToFile` verification but rejects other digest algorithms even if content-addressed. `Capture` marks secrets and SSH inputs optional, matching BuildKit provenance conventions but not proving they were actually used.

## Test Signals
`identifier_test.go` exercises URL parsing, subdir sanitization behavior from `gitutil`, valid/invalid bundle locators, checksum requirements, checkout-bundle incompatibilities, and SHA/ref mismatch handling.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/source/git/identifier.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/source/git/identifier_test.go -->
# sources/cloud-native/buildkit/source/git/identifier_test.go

## Purpose
This file tests git identifier URL parsing and bundle/checkout-bundle attribute validation. It is the main local test signal for the identifier logic introduced around git bundle support.

## Important Tests
`TestNewGitIdentifier` covers SSH URLs, git protocol URLs, scp-style GitHub URLs, bare host paths that default to HTTPS, refs, subdirs, URL-encoded users, and unsafe subdir cleanup such as `../../escape` and absolute paths. `TestIdentifierBundleValidation` covers valid registry and OCI-layout bundle locators, missing checksum, unsupported HTTPS locator scheme, unsupported SHA512 digest, checkout-bundle incompatibility with keep-git-dir and subdir, standalone checkout-bundle, bundle plus checkout-bundle, and checksum/ref SHA mismatch or match.

## Control Flow
The URL tests table-drive `NewGitIdentifier` and compare the resulting struct. Bundle validation creates a `Source{}` and calls its `Identifier("git", url, attrs, nil)` path so it tests production attribute parsing plus validation rather than calling helpers directly.

## State and Persistence
No persistent state. Each case creates fresh identifiers and attribute maps.

## Dependencies and Integration Points
It imports solver protobuf attribute constants and `testify/require`. It indirectly depends on the git source `Source.Identifier` implementation and `gitutil.ParseURL` subdir normalization.

## Risks Covered
The suite catches dangerous or unsupported bundle configurations before runtime: bundle without checksum, digest algorithm mismatch, unsupported scheme, checkout-bundle with worktree-only options, and contradictory ref/checksum pins. It does not test actual bundle download, staging, git import, or checkout-bundle snapshot creation.

## Test Signals
Strong unit-level signal for parsing and static validation. Runtime behavior still requires integration coverage with git CLI and blob/OCI content sources.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/source/git/identifier_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/source/git/mtime_unix.go -->
# sources/cloud-native/buildkit/source/git/mtime_unix.go

## Purpose
This Unix-only file implements symlink-aware mtime setting for git source checkout paths. It exists so git source code can adjust file timestamps without following symlinks.

## Important APIs
`lchtimes(path, t)` converts a Go `time.Time` to a Unix timespec and calls `unix.UtimesNanoAt` with `AT_FDCWD` and `AT_SYMLINK_NOFOLLOW`.

## Control Flow
The function is a direct syscall wrapper. Both access and modification times are set to the same timestamp.

## State and Persistence
It mutates filesystem metadata on the target path. It does not store state in memory or elsewhere.

## Dependencies and Integration Points
It is built only when `!windows` applies. It depends on `golang.org/x/sys/unix` and is used by git checkout code to apply deterministic checkout or commit mtimes.

## Risks
Errors are returned directly from the syscall. Platform-specific filesystem behavior can vary, especially on filesystems with coarse timestamp resolution or limited symlink timestamp support.

## Test Signals
No direct tests in this subset. Coverage is indirect through git source checkout tests that assert mtime behavior on Unix-like systems.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/source/git/mtime_unix.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/source/git/mtime_windows.go -->
# sources/cloud-native/buildkit/source/git/mtime_windows.go

## Purpose
This Windows-only file provides a no-op implementation of `lchtimes` for git source checkout timestamp handling.

## Important APIs
`lchtimes(_ string, _ time.Time) error` always returns nil.

## Control Flow
There is no branching or syscall. The function intentionally ignores its arguments.

## State and Persistence
It does not modify filesystem state. On Windows builds, callers that invoke `lchtimes` get successful no-op behavior.

## Dependencies and Integration Points
It is built only on Windows and imports `time` to match the shared signature. It satisfies the platform-specific function used by git checkout code.

## Risks
Because it is a no-op, Windows checkouts will not get the symlink timestamp behavior provided on Unix. This is likely intentional because Windows symlink timestamp semantics differ and may not be needed by current callers.

## Test Signals
No direct tests in this subset. Windows-specific git checkout mtime behavior would need platform CI coverage.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/source/git/mtime_windows.go -->
