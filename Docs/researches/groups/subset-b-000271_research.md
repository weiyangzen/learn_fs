# subset-b-000271 Research

Grouped research report for the requested SOCI snapshotter filesystem subset. Each section is delimited for deterministic reconciliation into the source-tree-aligned per-file reports.

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/soci-snapshotter/fs/backgroundfetcher/background_fetcher.go -->
# sources/cloud-native/soci-snapshotter/fs/backgroundfetcher/background_fetcher.go

Purpose: implements the filesystem-wide background span fetch loop used after lazy SOCI layers have been mounted. The fetcher drains a bounded work queue of `Resolver` instances and repeatedly asks each resolver to fetch the next span, letting image startup remain lazy while unused spans are warmed into the span cache over time.

Important APIs and flow: `Option` functions configure silence period, fetch period, max queue size, and metric emission period. `NewBackgroundFetcher` builds a `rate.Limiter`, work queue, close channel, pause channel, and default `time.Sleep` pauser. `Add` queues a resolver, `Pause` queues a mount-triggered pause signal, `Close` signals shutdown, and `Run` loops until context cancellation or close. Each loop drains pending pause signals, optionally sleeps for the silence period, checks shutdown, pulls one resolver from `workQueue`, skips closed resolvers, runs `Resolve` in a goroutine, requeues it if more spans remain, and waits on the rate limiter. `emitWorkQueueMetric` periodically records queue depth through common metrics.

State and persistence: state is in-memory only: queue contents, pause signals, close signal, rate limiter, and pauser. It persists fetched bytes indirectly through the resolver/span manager/cache that it invokes. It does not own files or registry handles.

Dependencies and integration: depends on `backgroundfetcher.Resolver`, `golang.org/x/time/rate`, containerd logging, and `fs/metrics/common`. It is constructed by `fs.NewFilesystem` when background fetch is enabled and receives sequential layer resolvers from `layer.Resolver.Resolve`.

Risks and test signals: `Add`, `Pause`, and `Close` are blocking sends; if the queue or close channel has no receiver these calls can block. `Run` launches one goroutine per dequeued resolver and requeues from that goroutine, so queue backpressure can hold resolver goroutines. The tests verify pause coalescing and full cache warming for one and multiple span managers with zero fetch period, but they do not cover blocking shutdown, saturated queues, or metric ticker behavior.
<!-- END_FILE_RESEARCH: sources/cloud-native/soci-snapshotter/fs/backgroundfetcher/background_fetcher.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/soci-snapshotter/fs/backgroundfetcher/background_fetcher_test.go -->
# sources/cloud-native/soci-snapshotter/fs/backgroundfetcher/background_fetcher_test.go

Purpose: tests the background fetcher pause path and end-to-end span warming behavior using real ztoc/span-manager objects and an in-memory counting cache.

Important APIs and flow: `withPauser` injects a mock pauser. `countingPauser` records pause invocations. `TestBackgroundFetcherPause` starts `Run`, calls `Pause`, waits briefly, and asserts exactly one pause call. `TestBackgroundFetcherRun` builds one or two gzip tar ztoc readers with large random files, wraps each span manager with `NewSequentialResolver`, starts a fetcher with `WithFetchPeriod(0)`, adds the resolvers, waits, then checks that the cache saw one add per span and byte count equal to compressed archive size minus the gzip header.

State and persistence: tests are in-memory except for helper-created ztoc/tar readers. `countingCache` records write calls and bytes under a mutex. No remote registry, filesystem mount, or Prometheus registry is required.

Dependencies and integration: uses `ztoc.BuildZtocReader`, `spanmanager.New`, `cache.BlobCache` interfaces, random testutil tar entries, and OpenContainers digest. It exercises the real resolver/span-manager cache path rather than a fake resolver for the main run test.

Risks and test signals: good signal that the fetch loop requeues until `ErrExceedMaxSpan` and populates all spans. The tests use sleeps (`10ms`, `1s`, `3s`), so slow CI or scheduling changes can make them flaky. They do not assert `Close` behavior under a full queue or that metric emission stops cleanly.
<!-- END_FILE_RESEARCH: sources/cloud-native/soci-snapshotter/fs/backgroundfetcher/background_fetcher_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/soci-snapshotter/fs/backgroundfetcher/resolver.go -->
# sources/cloud-native/soci-snapshotter/fs/backgroundfetcher/resolver.go

Purpose: defines the background fetch resolver contract and the sequential layer resolver that warms layer spans from span 0 upward.

Important APIs and flow: `Resolver` exposes `Resolve(context.Context) (more bool, err error)`, `Close`, and `Closed`. `base` embeds a span manager, layer digest, close state, and start timestamp protected by a mutex. `NewSequentialResolver` returns a `sequentialLayerResolver`. `Resolve` logs the current span, stores the start time on span 0, calls `FetchSingleSpan`, increments success metrics and `nextSpanFetchID` on success, returns `(true, nil)` while more spans might exist, returns `(false, nil)` and records total background-fetch latency on `spanmanager.ErrExceedMaxSpan`, and increments failure metrics plus wraps unexpected errors.

State and persistence: resolver state is the next span ID, closed flag, layer digest, and first-span start time. Actual persistence is delegated to `SpanManager.FetchSingleSpan`, which writes to the configured span cache.

Dependencies and integration: integrates `fs/span-manager`, ztoc compression span IDs, common metrics, containerd/logrus logging, and OCI digests. It is added to `BackgroundFetcher` by `layer.Resolver.Resolve` after the span manager has been initialized.

Risks and test signals: `Closed` and `Close` protect only the closed flag; `Resolve` itself does not check closed, relying on the fetcher to skip closed resolvers. A successful fetch always returns `more=true`, so completion is detected only by trying one span past `MaxSpanID`. Tests verify sequential ID progression and completion against real ztoc data, but they do not cover error metrics or concurrent `Close` while `Resolve` is active.
<!-- END_FILE_RESEARCH: sources/cloud-native/soci-snapshotter/fs/backgroundfetcher/resolver.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/soci-snapshotter/fs/backgroundfetcher/resolver_test.go -->
# sources/cloud-native/soci-snapshotter/fs/backgroundfetcher/resolver_test.go

Purpose: validates that `NewSequentialResolver` fetches spans in increasing order until all spans in a ztoc have been resolved.

Important APIs and flow: `TestSequentialResolver` builds a gzip ztoc reader for a large random tar file, creates a `spanmanager.SpanManager` with memory cache, constructs a sequential resolver, repeatedly records `nextSpanFetchID`, calls `Resolve`, and stops when `more` is false. It checks that the final span ID equals `ztoc.MaxSpanID + 1` and that every recorded span index matches its position.

State and persistence: entirely test-local memory cache and generated ztoc reader. It directly type-asserts to `*sequentialLayerResolver` to inspect internal state.

Dependencies and integration: uses the same span manager and ztoc helpers as production, so it validates the resolver against real span boundaries. It depends on package-private access by being in the same package.

Risks and test signals: strong signal for normal sequential progression. It does not test `Close`, `Closed`, `ErrExceedMaxSpan` metric behavior, or unexpected `FetchSingleSpan` failures.
<!-- END_FILE_RESEARCH: sources/cloud-native/soci-snapshotter/fs/backgroundfetcher/resolver_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/soci-snapshotter/fs/client.go -->
# sources/cloud-native/soci-snapshotter/fs/client.go

Purpose: provides an OCI artifact/referrers client abstraction used to find SOCI index artifacts attached to an image manifest.

Important APIs and flow: `IndexSelectionPolicy` chooses one descriptor from a descriptor list; `SelectFirstPolicy` returns `descs[0]`. `ReferrersClient` exposes `SelectReferrer`. `ReferrersCaller` abstracts ORAS `Repository.Referrers` for tests. `Inner` combines ORAS content storage and referrers. `OCIArtifactClient` embeds `Inner`. `SelectReferrer` calls `AllReferrers`, maps fetch failures, returns `ErrNoReferrers` for an empty list, and otherwise applies the supplied policy. `AllReferrers` calls `Referrers` with `soci.SociIndexArtifactType` and appends all pages passed to the callback.

State and persistence: no state beyond the embedded remote/content store. It reads registry referrer metadata and does not write artifacts.

Dependencies and integration: used by `fs.findSociIndexDescReferrer` when SOCI v1 referrer discovery is enabled. Depends on ORAS content/referrers interfaces, OCI descriptors, and SOCI artifact type constants.

Risks and test signals: `SelectFirstPolicy` assumes the list is non-empty and is safe only after `SelectReferrer` checks length. Selection policy quality determines which index is mounted when multiple SOCI indexes exist. Tests cover empty referrers and first-descriptor selection with a fake ORAS inner, but not pagination errors, artifact type filtering, or richer selection policies.
<!-- END_FILE_RESEARCH: sources/cloud-native/soci-snapshotter/fs/client.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/soci-snapshotter/fs/client_test.go -->
# sources/cloud-native/soci-snapshotter/fs/client_test.go

Purpose: verifies `OCIArtifactClient.SelectReferrer` behavior for empty and non-empty referrer lists.

Important APIs and flow: `fakeInner` implements `Inner` with no-op content store methods and a `Referrers` method that passes a predefined descriptor slice to the callback. `TestOCIArtifactClientSelectReferrer` constructs an empty case expecting `ErrNoReferrers` and a non-empty case expecting `SelectFirstPolicy` to return the first descriptor. It compares descriptors with `go-cmp`.

State and persistence: fully in-memory fake descriptors. No ORAS repository, registry, or content store is contacted.

Dependencies and integration: exercises the public client wrapper and policy callback shape. It confirms the error sentinel can be checked with `errors.Is`.

Risks and test signals: narrow but useful regression signal for referrer selection. It does not verify that `soci.SociIndexArtifactType` is passed to the underlying `Referrers` call, because the fake ignores the artifact type.
<!-- END_FILE_RESEARCH: sources/cloud-native/soci-snapshotter/fs/client_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/soci-snapshotter/fs/fs.go -->
# sources/cloud-native/soci-snapshotter/fs/fs.go

Purpose: implements the SOCI snapshotter `snapshot.FileSystem`: constructing filesystem services, resolving SOCI indexes, choosing lazy FUSE mount versus local/parallel unpack paths, managing mounted layer references, and checking/refreshing lazy remote layer connectivity.

Important APIs and flow: option functions inject source discovery, remote handlers, metadata store, overlay opaque behavior, preresolve concurrency, and pull modes. `NewFilesystem` validates parallel pull/content-store compatibility, creates the content store, optional background fetcher, layer resolver, preresolver, metrics controllers, FUSE failure listener, and parallel unpack job storage. `Mount` resolves labels for image ref/manifest/index, fetches SOCI artifacts through `getSociContext`, resolves the target layer in a goroutine, preresolves neighboring layers, waits up to `mountTimeout`, builds a root FUSE node, registers the layer and metrics, and starts a go-fuse server. `MountLocal` downloads/unpacks a layer through the content store and archive verifier. `MountParallel`, `preloadAllLayers`, `premount`, and `rebase` implement parallel pull/unpack and move the completed unpack directory into the requested mountpoint. `Check` inspects cached/fetched size and refreshes remote blob access when needed. `Unmount` removes mountpoint state, evicts non-ID-mapped layers, removes metrics, and force-unmounts FUSE.

State and persistence: maintains in-memory maps for mounted layers and per-image SOCI contexts, a preresolver queue/cache, background fetcher, metrics registry membership, content-store client, and parallel unpack job registry. Persistent effects include content store reads/writes, temporary unpack directories, moved mountpoint directories, FUSE mounts, ID-mapped directory copies, and remote SOCI artifact/layer fetches.

Dependencies and integration: central integration point for config, snapshot labels, source discovery, layer resolver, remote ORAS stores, SOCI index/prefetch artifacts, containerd content/images/mount APIs, go-fuse, idtools, metrics, HTTP auth clients, and parallel unpack support. Index discovery tries explicit digest first, SOCI v2 manifest annotation second, and SOCI v1 referrers third, gated by pull-mode config.

Risks and test signals: the preresolver goroutine reads from `pr.queue` in a `default` branch and can block there until work arrives, which is acceptable but means cancellation may not be observed while blocked. Mount resolution goroutines send on unbuffered channels and may remain blocked if the caller times out before receiving. Parallel premount/rebase has significant lifecycle complexity: cancellation, temp directory poisoning checks, content verification, and job removal must stay aligned. Tests in this file only cover `Check` success/failure with a fake layer; broader behavior relies on other package tests and integration coverage.
<!-- END_FILE_RESEARCH: sources/cloud-native/soci-snapshotter/fs/fs.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/soci-snapshotter/fs/fs_test.go -->
# sources/cloud-native/soci-snapshotter/fs/fs_test.go

Purpose: unit-tests the filesystem `Check` path that validates or refreshes a mounted lazy layer connection.

Important APIs and flow: `TestCheck` creates a `filesystem` with a single fake `breakableLayer` registered at mountpoint `test` and default source resolver wiring. It sets `success=true` and expects `fs.Check` to pass, then sets `success=false` and expects failure. `breakableLayer` implements the `layer.Layer` interface with simple success-controlled `Check` and `Refresh` methods plus stubbed mount/read APIs.

State and persistence: in-memory fake filesystem map only. No FUSE server, remote registry, content store, or mountpoint is touched.

Dependencies and integration: validates the `filesystem.Check` behavior against the `layer.Layer` interface contract. The fake `Info` reports `Size: 1` and default `FetchedSize: 0`, forcing the connectivity check path.

Risks and test signals: confirms the basic branch that skips fully fetched layers is not used and that layer check errors propagate. It does not cover retry across multiple sources, refresh success after initial failure, labels parsing, or behavior when no layer is registered.
<!-- END_FILE_RESEARCH: sources/cloud-native/soci-snapshotter/fs/fs_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/soci-snapshotter/fs/layer/layer.go -->
# sources/cloud-native/soci-snapshotter/fs/layer/layer.go

Purpose: resolves a SOCI layer into a reusable lazy `Layer` object backed by a remote blob, metadata reader, span manager, optional background fetch resolver, and optional prefetch artifact execution.

Important APIs and flow: `Layer` exposes status, root FUSE node creation, connectivity check/refresh, remote reads, xattr policy, reference release, and cache key. `Info` reports digest, size, fetched bytes, and last read time. `NewResolver` creates LRU caches for layers and blobs, a named resolve lock, remote resolver, metadata/artifact stores, and optional prefetch semaphore. `Resolve` serializes by ref/digest key, reuses a valid layer cache entry when possible, resolves/caches the remote blob, creates a span cache, fetches and unmarshals the SOCI ztoc artifact, initializes metadata store telemetry, creates a span manager, optionally queues background fetching, executes prefetch ranges, builds a verified reader, reads the disable-xattrs annotation, caches the new layer, and returns a reference wrapper. `resolveBlob` performs equivalent cache/reuse behavior for remote blobs. `executePrefetch` loads a SOCI prefetch artifact and resolves listed span ranges with a bounded worker fanout.

State and persistence: resolver state includes root directory, LRU caches with eviction close hooks, blob/span caches, named locks, metadata/artifact stores, config, background fetcher, and prefetch semaphore. Persistent data includes directory span caches and artifact/content-store reads. Layer close cascades to background resolver close, reader close, span-manager close, and blob ref release.

Dependencies and integration: integrates `fs/remote`, `fs/reader`, `fs/span-manager`, `metadata`, `ztoc`, SOCI artifact formats, cache implementations, named mutex/LRU utilities, containerd/docker refs, and go-fuse node creation. `fs.Mount` and preresolver call `Resolve`; `fs.Unmount` calls `Done`/`Evict`.

Risks and test signals: correctness depends on cache reference counting and eviction close hooks. Failed resolves must unwind blob and span cache resources via deferred cleanup. Prefetch uses `runtime.GOMAXPROCS` workers and ignores per-span errors because `ResolveSpan` has no checked return here, so prefetch failures may be silent. Tests for this file mostly exercise node behavior and a waiter helper, not resolver cache/prefetch paths.
<!-- END_FILE_RESEARCH: sources/cloud-native/soci-snapshotter/fs/layer/layer.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/soci-snapshotter/fs/layer/layer_test.go -->
# sources/cloud-native/soci-snapshotter/fs/layer/layer_test.go

Purpose: groups high-level layer node tests and includes a small condition-variable waiter regression test.

Important APIs and flow: `TestLayer` delegates to shared helpers `testNodeRead`, `testExistence`, and `testStatfs` using `metadata.NewTempDbStore`, thereby exercising file reads, whiteout/opaque/xattr handling, state files, modes, symlink sizes, and statfs behavior through layer node construction. `TestWaiter` defines a local `waiter`, starts a goroutine waiting on a condition, sleeps, calls `done`, and asserts the wait did not return early.

State and persistence: helper tests create temporary metadata DB stores and synthetic gzip/tar ztoc readers. The local waiter uses memory synchronization only.

Dependencies and integration: relies heavily on `util_test.go` helpers and the node implementation. It indirectly validates `reader.NewReader`, span manager reads, FUSE node operations, and metadata store behavior.

Risks and test signals: strong signal for node-facing layer behavior, but little direct coverage of `Resolver.Resolve`, blob/layer LRU caches, background fetch queueing, or prefetch artifacts. The local waiter test is self-contained and not connected to production code in this file.
<!-- END_FILE_RESEARCH: sources/cloud-native/soci-snapshotter/fs/layer/layer_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/soci-snapshotter/fs/layer/node.go -->
# sources/cloud-native/soci-snapshotter/fs/layer/node.go

Purpose: implements the go-fuse node tree for a lazy SOCI layer, translating metadata and span-backed reads into FUSE directory, file, symlink, xattr, whiteout, statfs, and state-file operations.

Important APIs and flow: `OverlayOpaqueType` controls which overlay opaque xattrs are exposed. `FuseOperationCounter` aggregates FUSE operation counts for delayed image-level metric/log emission. `newNode` builds the root `node` and shared `fs` state from a layer reader, root metadata, overlay config, layer digest, operation counter, and blob status. `node.Readdir` enumerates metadata children, hides `.wh.*` files, converts whiteouts to overlay-style char-device entries, sorts entries, and caches them. `Lookup` hides whiteout internals, exposes `.soci-snapshotter`, serves cached children, maps whiteout lookups, and creates child nodes. `Open` returns a lazy file handle, `Getattr` maps metadata attrs, `Getxattr`/`Listxattr` expose stored xattrs and synthetic opaque xattrs, `Readlink` returns symlink targets, and `Statfs` reports backing filesystem stats when available. `file.Read` delegates to the reader and emits synchronous read metrics. `state` and `statFile` expose a hidden observability directory containing JSON with digest, size, fetched bytes, fetched percent, and last error.

State and persistence: per-node state includes metadata attr, child entry cache, id mapper, and shared filesystem state. The state JSON is generated dynamically from the remote blob and recorded error string; it is not persisted as a real file. Statfs reads the resolver root directory with `unix.Statfs` when configured.

Dependencies and integration: depends on go-fuse interfaces, `metadata.Reader`, `reader.Reader`, remote blob status, idtools mapping, common metrics, containerd logging, and Unix mode/device conversion. It is returned by `layer.RootNode` and mounted by `fs.setupFuseServer`.

Risks and test signals: FUSE paths must preserve overlay semantics while hiding tar whiteout files. Child-entry caching can make later metadata mutations invisible, which is acceptable for immutable layers. `statFile.updateStatUnlocked` divides by size, so zero-size blobs would produce non-finite percentages. Tests cover block calculations, file reads, whiteouts, opaque xattrs, mode bits, symlink size, hidden state file, and statfs fallback/real paths.
<!-- END_FILE_RESEARCH: sources/cloud-native/soci-snapshotter/fs/layer/node.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/soci-snapshotter/fs/layer/node_test.go -->
# sources/cloud-native/soci-snapshotter/fs/layer/node_test.go

Purpose: tests the `entryToAttr` block-count conversion used when exposing metadata attributes through FUSE.

Important APIs and flow: `TestEntryToAttr` creates a metadata attr with size `1774757`, calls `node.entryToAttr`, normalizes mtime, and asserts that FUSE `Blocks` is reported in 512-byte physical blocks derived from 4096-byte `blockSize`, not a simple ceiling of size divided by block size. It also validates default mode, block size, size, and link count.

State and persistence: pure in-memory conversion test.

Dependencies and integration: targets go-fuse `fuse.Attr` output and metadata attr mapping. It protects behavior observed by overlay/container consumers that inspect stat information.

Risks and test signals: focused regression signal for one subtle stat field. It does not cover owner mapping, symlink size, xattrs, device numbers, or stable inode generation; those are covered partly by broader layer utility tests.
<!-- END_FILE_RESEARCH: sources/cloud-native/soci-snapshotter/fs/layer/node_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/soci-snapshotter/fs/layer/util_test.go -->
# sources/cloud-native/soci-snapshotter/fs/layer/util_test.go

Purpose: provides shared test fixtures and assertions for layer FUSE node behavior, including span-backed reads, whiteouts, opaque directories, mode bits, state files, and statfs reporting.

Important APIs and flow: `testNodeRead` enumerates read sizes, offsets, base spans, and file sizes, builds a node reader with synthetic ztoc data, reads through a FUSE file handle, and compares bytes. `makeNodeReader`, `makeFile`, `getRootNode`, and `getRootNodeWithStatfsBase` construct real metadata readers, span managers, `reader.Reader`, and layer nodes around fake blob state. `testExistenceWithOpaque` checks whiteout translation, hidden whiteout source entries, opaque xattr variants, preserved xattrs, state directory lookup, suid/sgid/sticky mode conversion, and symlink size. Assertion helpers walk the FUSE tree through `Lookup`/`Readdir`, read file content, inspect attrs/xattrs, and parse the state JSON. `testStatfs` verifies default zero stats and real backing filesystem stats.

State and persistence: uses temporary metadata stores, temporary statfs directories, synthetic gzip/tar ztoc readers, memory caches, and fake blob fetched-size state. It does not mount a real FUSE filesystem; it calls go-fuse node operations directly.

Dependencies and integration: integrates metadata stores, span manager, reader package, testutil tar builders, go-fuse node APIs, Unix statfs/device helpers, and idtools. It is the main behavioral test bed for `node.go`.

Risks and test signals: broad coverage of read and metadata semantics across multiple span sizes. It still does not exercise actual kernel FUSE mounting, concurrent node operations under real VFS pressure, or real remote blob refresh failures.
<!-- END_FILE_RESEARCH: sources/cloud-native/soci-snapshotter/fs/layer/util_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/soci-snapshotter/fs/metrics/common/metrics.go -->
# sources/cloud-native/soci-snapshotter/fs/metrics/common/metrics.go

Purpose: defines shared Prometheus metrics and helper functions for SOCI filesystem latency, operation counts, bytes served, image-level counts, and global FUSE failure signaling.

Important APIs and flow: constants name histogram/counter/gauge keys and operation labels such as mount, remote registry GET, metadata init, synchronous read, background fetch, FUSE failures, and background queue size. Package-level Prometheus collectors include millisecond and microsecond latency histograms, operation counters, byte gauges, and image operation gauges. `Register` uses `sync.Once` to register collectors. `MeasureLatencyInMilliseconds`, `MeasureLatencyInMicroseconds`, `IncOperationCount`, `AddBytesCount`, and `AddImageOperationCount` wrap label binding. `ListenForFuseFailure` waits for failure signals and increments `FuseFailureState` at most once per five-minute block. `ReportFuseFailure` increments the operation-specific failure count and sends a nonblocking notification.

State and persistence: all state is process-local Prometheus collector state plus the unbuffered `fuseFailureSignal` channel and `sync.Once`. No filesystem persistence.

Dependencies and integration: used across fs mount, remote HTTP fetch, layer node operations, reader reads, background fetch, and metrics controllers. Registered from `fs.NewFilesystem` unless Prometheus is disabled.

Risks and test signals: metrics with layer/image digest labels can increase cardinality. `AddBytesCount` uses a gauge with additive behavior, which is semantically counter-like but implemented as gauge. `ListenForFuseFailure` blocks during each time block after a signal, intentionally coalescing failures. No tests are present for registration idempotency, label values, or fuse failure coalescing.
<!-- END_FILE_RESEARCH: sources/cloud-native/soci-snapshotter/fs/metrics/common/metrics.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/soci-snapshotter/fs/metrics/layer/layer.go -->
# sources/cloud-native/soci-snapshotter/fs/metrics/layer/layer.go

Purpose: declares the per-layer metrics exposed by the layer metrics controller.

Important APIs and flow: `layerMetrics` contains two `metric` definitions: `layer_fetched_size`, which reports `l.Info().FetchedSize`, and `layer_size`, which reports `l.Info().Size`. Both use byte units and `prometheus.CounterValue`, and both rely on the controller to add digest and mountpoint labels.

State and persistence: no mutable state in this file. Metric values are read from live `layer.Layer` instances at scrape time.

Dependencies and integration: depends on the layer interface, Docker go-metrics units, and Prometheus value types. `metrics.go` appends this list into a `Controller` registered in a Docker metrics namespace by `fs.NewFilesystem`.

Risks and test signals: `CounterValue` for fetched size can be problematic if a layer object is replaced or fetched-size reporting decreases, because Prometheus counters should be monotonic. No tests directly validate descriptor names, units, or scrape values.
<!-- END_FILE_RESEARCH: sources/cloud-native/soci-snapshotter/fs/metrics/layer/layer.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/soci-snapshotter/fs/metrics/layer/metrics.go -->
# sources/cloud-native/soci-snapshotter/fs/metrics/layer/metrics.go

Purpose: implements a Prometheus collector/controller that tracks mounted layers and emits per-layer metrics with digest and mountpoint labels.

Important APIs and flow: `NewLayerMetrics` returns a no-op controller when the namespace is nil; otherwise it initializes maps, appends `layerMetrics`, and adds itself to the Docker metrics namespace. `Describe` emits descriptors for each metric. `Collect` takes a read lock, starts a goroutine per registered layer, and each goroutine emits all metric values for that mountpoint. `Add` and `Remove` mutate the mountpoint-to-layer map under lock and no-op when metrics are disabled. `metric.desc` builds descriptors and `metric.collect` calls `prometheus.MustNewConstMetric`.

State and persistence: in-memory map of mountpoint keys to live `layer.Layer` references protected by an RW mutex. No persistent state.

Dependencies and integration: `fs.Mount` registers layers, `fs.Unmount` removes them, and Docker go-metrics namespace exposes the controller to Prometheus. It calls `Layer.Info` during collection.

Risks and test signals: `Collect` holds the read lock while launching and waiting for goroutines, so `Add`/`Remove` block until the scrape completes. The closure uses loop variables in a goroutine; in modern Go this is safe for range variables, but older language versions would have been risky. No tests cover concurrent add/remove/scrape or no-op mode.
<!-- END_FILE_RESEARCH: sources/cloud-native/soci-snapshotter/fs/metrics/layer/metrics.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/soci-snapshotter/fs/parallel_artifact_fetcher.go -->
# sources/cloud-native/soci-snapshotter/fs/parallel_artifact_fetcher.go

Purpose: implements the layer artifact fetcher used by parallel pull/unpack mode, fetching missing compressed layer blobs into a temporary ingest file with optional ranged concurrent requests and asynchronous digest verification.

Important APIs and flow: `newParallelArtifactFetcher` wraps the base artifact fetcher with a layer unpack job, chunk size, and compressed verifier. `Fetch` first tries the local content store and returns `(rc, true, nil)` on hit. On miss it resolves zero-size descriptors when needed, downloads to the job ingest path, starts async digest verification, and returns `(rc, false, nil)`. `fetchFromRemoteAndWriteToTempDir` refuses pre-existing ingest files, creates/truncates the file to descriptor size, decides whether multiple fetches are useful by checking ORAS blob range support, dispatches one full request or multiple range requests, rewinds the file, and starts verification. `multiRequestFetchWrite` uses an errgroup, per-range download semaphore acquisition, `FetchRange`, and `io.NewOffsetWriter`. `writeToFileRange` uses `io.CopyN` for exact range length and drains remaining response data.

State and persistence: writes a temporary ingest file under the layer unpack job, preallocates it with `Truncate`, and hands the same file back as the read source. It uses unpack-job download semaphores and optional verifier state. It does not commit to content store directly; the parallel unpacker can store from the ingest reader.

Dependencies and integration: depends on content store `store.BasicStore`, remote resolver storage/ORAS blob store, layer unpack job resource controller, errgroup, descriptor metadata, and async verifier. It is created by `filesystem.premount`.

Risks and test signals: concurrent writes to one `os.File` through offset writers rely on independent offsets and exact range boundaries. `multiRequestFetchWrite` acquires semaphores before goroutine launch; if a later acquire fails, already-started goroutines still run. `asyncVerifyBlobDigest` opens a file and passes it to the verifier; lifecycle depends on verifier closing/consuming it. No direct tests are listed for this file in the subset.
<!-- END_FILE_RESEARCH: sources/cloud-native/soci-snapshotter/fs/parallel_artifact_fetcher.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/soci-snapshotter/fs/parallel_unpacker.go -->
# sources/cloud-native/soci-snapshotter/fs/parallel_unpacker.go

Purpose: applies a fetched layer archive into a mountpoint during parallel pull/unpack, optionally storing remotely fetched compressed content into the content store while unpacking.

Important APIs and flow: `NewParallelLayerUnpacker` wraps a fetcher, archive applier, resource controller, and discard flag. `Unpack` fetches the descriptor, acquires an unpack lease, optionally opens an ingest reader and starts a goroutine to `fetcher.Store` when the layer was remote and unpacked layers should be retained, prepares archive apply options including overlay whiteout conversion and parent lowerdirs from mounts, verifies the unpack destination is ready/empty, applies the archive to the mountpoint, logs latency, and waits for the optional store goroutine.

State and persistence: reads from the fetcher, writes extracted filesystem data into `mountpoint`, and may write the compressed layer into the content store from the ingest reader. Resource leases are held for the duration of unpack.

Dependencies and integration: depends on the parallel artifact fetcher, `LayerUnpackResourceController`, containerd archive/mount packages, overlay whiteout conversion, and the archive wrapper that performs digest verification/decompression.

Risks and test signals: storage and unpack consume related readers concurrently, so controller-provided ingest reader behavior is critical. `VerifyUnpackDestinationIsReady` is a security guard against unpacking into poisoned directories. Store errors surface only after archive apply completes via `errGroup.Wait`. No direct tests in this subset cover this file.
<!-- END_FILE_RESEARCH: sources/cloud-native/soci-snapshotter/fs/parallel_unpacker.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/soci-snapshotter/fs/reader/reader.go -->
# sources/cloud-native/soci-snapshotter/fs/reader/reader.go

Purpose: provides a metadata-backed file reader for lazy SOCI layers, mapping file reads to span-manager byte ranges and verifying tar-header metadata before first read.

Important APIs and flow: `Reader` exposes `OpenFile`, `Metadata`, `Close`, and `LastOnDemandReadTime`. `NewReader` stores a metadata reader, layer digest, span manager, and verification flag. `OpenFile` rejects closed readers, opens a metadata file by ID, and returns a `file` reader. `file.ReadAt` optionally calls `Verify`, handles empty/out-of-range reads, computes uncompressed file start/end from metadata offsets, reads contents from `SpanManager.GetContents`, records synchronous remote-fetch/read metrics, stores last on-demand read time, and fills the caller buffer with `io.ReadFull`. `Verify` is once-only and mutex-protected; it reads the tar header bytes via span manager, parses a tar header, checks exact header size, compares attrs/xattrs/name against metadata, and marks verified on success. `attrMatchesTarHeader` handles most tar-visible attributes but intentionally ignores link count.

State and persistence: reader state includes metadata reader, span manager, last read time, closed flag, and disable-verification flag. File state includes metadata file handle and an atomic verified bit. Persistence is delegated to the span manager/cache as reads materialize spans.

Dependencies and integration: used by `layer.Resolver.Resolve` and `layer/node.go` file handles. Depends on `metadata`, `fs/span-manager`, ztoc compression offsets/xattr parsing, common metrics, and tar parsing.

Risks and test signals: verification requires fetching tar header spans before first file read, which adds latency but catches metadata/content mismatch. If verification is disabled, corrupt metadata can drive reads unchecked. `io.ReadFull` turns short reads into errors, which is appropriate for immutable layer content. Tests cover many read offset/span/file-size combinations and non-existent file errors, but not verification mismatch cases or disabled verification.
<!-- END_FILE_RESEARCH: sources/cloud-native/soci-snapshotter/fs/reader/reader.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/soci-snapshotter/fs/reader/reader_test.go -->
# sources/cloud-native/soci-snapshotter/fs/reader/reader_test.go

Purpose: validates lazy file reads through `reader.file.ReadAt` across span sizes, offsets, and file sizes, and checks error behavior for missing file IDs.

Important APIs and flow: `TestFsReader` calls `testFileReadAt` and `testFailReader` using `metadata.NewTempDbStore`. `testFileReadAt` enumerates read size, inner offset, base offset, file size, span size, and optional tar prefix, builds a synthetic ztoc and metadata reader, opens the test file, reads through the returned `file`, and compares bytes. `testFailReader` finds an unused metadata ID, verifies `OpenFile` fails for it, then opens and reads a valid file successfully.

State and persistence: uses temporary metadata DB stores, memory span cache, and generated gzip/tar ztoc readers. No remote HTTP or FUSE mount is involved.

Dependencies and integration: exercises `ztoc.BuildZtocReader`, `spanmanager.New`, metadata stores, and the reader package together. The tar prefix cases protect name handling for paths with `./`.

Risks and test signals: good signal for offset arithmetic and EOF handling. Tests do not intentionally corrupt tar headers, attrs, xattrs, or span data, so `Verify` failure behavior is not strongly covered despite verification being enabled by default.
<!-- END_FILE_RESEARCH: sources/cloud-native/soci-snapshotter/fs/reader/reader_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/soci-snapshotter/fs/remote/blob.go -->
# sources/cloud-native/soci-snapshotter/fs/remote/blob.go

Purpose: implements the lazy remote blob abstraction used by layer readers: range reads, fetched-size accounting, health checks, refresh, and close state over a fetcher.

Important APIs and flow: `Blob` exposes connectivity check, size, fetched size, `ReadAt`, refresh, and close. `makeBlob` constructs a `blob` with fetcher, size, last-check state, interval, and resolver. `Refresh` resolves a new fetcher through the resolver and swaps it only if size matches. `Check` skips network checks until `checkInterval` expires, then calls `fetcher.check` and updates `lastCheck` on success. `ReadAt` bounds empty/out-of-range reads, builds a requested `region`, applies options, fetches the range into a `bytesWriter`, adjusts returned length for EOF, and returns bytes read. `fetchRegion` snapshots the current fetcher, performs a retryable fetch, iterates multipart/singlepart results, copies exactly the requested region size, updates last-check time, and merges fetched regions into `regionSet`.

State and persistence: protects fetcher, last check time, fetched region set, and closed flag with mutexes. It does not cache data itself; fetched bytes flow to the caller and fetched-size state tracks covered ranges only.

Dependencies and integration: depends on `remote.fetcher` implementations from `resolver.go`, Docker hosts/reference types for refresh, OCI descriptors, and `regionSet` from `util.go`. Used by `layer.layer.ReadAt`, state-file reporting, and connection checks.

Risks and test signals: fetched-size accounting marks an entire requested region fetched after successful copy, not individual multipart subregions. `fetchRegion` copies `reg.size()` for every part rather than the part's returned region, which is fine for current single requested region use but would be risky if multiple disjoint regions were passed. Tests cover normal reads, broken body/header, check intervals, and concurrent fetch behavior; they do not test refresh size mismatch.
<!-- END_FILE_RESEARCH: sources/cloud-native/soci-snapshotter/fs/remote/blob.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/soci-snapshotter/fs/remote/blob_test.go -->
# sources/cloud-native/soci-snapshotter/fs/remote/blob_test.go

Purpose: tests remote blob range reading, failure paths, check interval behavior, and helper round trippers for single and multipart HTTP responses.

Important APIs and flow: `TestReadAt` enumerates chunk sizes, offsets, blob sizes, and multi-range support, then validates returned bytes. `TestFailReadAt` covers HTTP failure responses, truncated bodies, and missing/broken headers. `TestParallelDownloadingBehavior` starts three concurrent `fetchRange` calls and checks round-trip counts/content with a counting transport. `TestCheckInterval` ensures `Check` skips network calls before interval expiry and updates `lastCheck` after an expired successful check. Helper transports validate Range headers and synthesize full, single-part partial, multipart partial, broken body, and broken header responses.

State and persistence: all in-memory bytes and fake `http.RoundTripper` implementations. No real registry or cache.

Dependencies and integration: exercises `blob`, `httpFetcher.fetch`, multipart parsing, range parsing, and `bytesWriter` together. It gives strong signal around HTTP response shape handling.

Risks and test signals: the comment in `TestParallelDownloadingBehavior` mentions expecting one round trip, but test data expects three, matching the current implementation without singleflight coalescing. Tests do not cover 401/403 URL refresh, force single-range mode from config, or `Blob.Refresh`.
<!-- END_FILE_RESEARCH: sources/cloud-native/soci-snapshotter/fs/remote/blob_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/soci-snapshotter/fs/remote/errors.go -->
# sources/cloud-native/soci-snapshotter/fs/remote/errors.go

Purpose: centralizes sentinel errors for remote blob resolution, HTTP status/header parsing, redirect, fetcher creation, and registry request failures.

Important APIs and flow: exported errors include unexpected status, failed layer-size retrieval, invalid host, failed redirect, unable to create fetcher, no regions, parse failures for content length/range/type, failed URL refresh, and request failure. Callers wrap these with `%w` so higher layers can classify failures with `errors.Is`.

State and persistence: no state or side effects.

Dependencies and integration: used by `remote/resolver.go` and exposed through `Blob.Check`, `Resolver.Resolve`, and filesystem check/mount paths.

Risks and test signals: useful for error classification, but the file itself has no tests. Consistency depends on all call sites wrapping rather than formatting without `%w`.
<!-- END_FILE_RESEARCH: sources/cloud-native/soci-snapshotter/fs/remote/errors.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/soci-snapshotter/fs/remote/resolver.go -->
# sources/cloud-native/soci-snapshotter/fs/remote/resolver.go

Purpose: resolves OCI layer descriptors into remote blob fetchers and implements HTTP range fetching, redirect handling, size discovery, retry/auth client adaptation, multipart parsing, and custom remote handlers.

Important APIs and flow: `Resolver.Resolve` converts blob config into durations/retry counts, calls `resolveFetcher`, and wraps the fetcher in a `blob`. `resolveFetcher` first tries configured handlers that return a custom `Fetcher`; otherwise it creates an HTTP fetcher. `newHTTPFetcher` validates digest/hosts, derives Docker pull scope, adapts `socihttp.AuthClient` retry/timeout settings while reusing global transports, constructs distribution blob URLs, follows redirect/range probe, and returns the first usable host/mirror. `httpFetcher.fetch` sends GET Range requests, squashes regions, optionally enters single-range mode, handles 200 full-body, 206 single or multipart, retries URL refresh on 401/403, and falls back to single-range on 400 multi-range rejection. `check` probes `bytes=0-1` and refreshes URL on 403. `GetHeader` tries HEAD, ranged GET, and full GET to discover size; `ParseSize` reads `Content-Length` or `Content-Range`; `remoteFetcher` adapts custom handlers to the internal multipart interface.

State and persistence: HTTP fetcher state includes round tripper, auth scope, registry URL, mutable real redirected URL, digest, and single-range flag protected by mutexes. No local persistence; network requests may update auth/redirect caches in the transport.

Dependencies and integration: used by `layer.Resolver.resolveBlob` and `blob.Refresh`. Integrates containerd Docker host/reference handling, SOCI auth/retry HTTP client, retryablehttp, common metrics for registry GET latency, ORAS registry references, and custom handler plugins.

Risks and test signals: correctness depends on registry-specific Range and redirect behavior. The fallback full GET in `GetHeader` can fetch an entire blob just to learn size. URL refresh on 403 assumes refreshed redirects can repair authorization/storage URLs. Tests cover mirror selection, check success/failure, retryable transport behavior, user-agent preservation, size parsing, and HEAD-to-GET fallback, but not every status path or auth-client clone branch.
<!-- END_FILE_RESEARCH: sources/cloud-native/soci-snapshotter/fs/remote/resolver.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/soci-snapshotter/fs/remote/resolver_test.go -->
# sources/cloud-native/soci-snapshotter/fs/remote/resolver_test.go

Purpose: validates remote HTTP resolver behavior around mirror selection, connectivity checks, retry handling, user-agent propagation, layer-size parsing, and header fallback.

Important APIs and flow: `TestMirror` builds registry host lists with optional mirrors and a sample round tripper to ensure `newHTTPFetcher` selects the first usable mirror or falls back to the original host, handles invalid mirror hostnames, observes redirects, and errors when all hosts fail. `TestCheck` verifies `httpFetcher.check` status handling. `TestRetry` wraps a fake transport in retryablehttp and expects retries through transient errors/statuses. `TestCustomUserAgent` verifies `socihttp.AuthClient` attaches global User-Agent headers during fetch. `TestParseSize` covers 200 `Content-Length`, 206 `Content-Range`, and unsupported status. `TestGetHeader` confirms HEAD success and HEAD failure followed by GET success.

State and persistence: fake round trippers and in-memory HTTP responses only. No real registry traffic.

Dependencies and integration: exercises `newHTTPFetcher`, `fetch`, `check`, `ParseSize`, `GetHeader`, `socihttp.AuthClient`, retryablehttp, Docker registry host configuration, and reference parsing.

Risks and test signals: strong coverage for resolver decision logic and HTTP shape handling. It does not test URL refresh after 401/403 in `fetch`, bad `Content-Type` multipart parsing, custom handler resolution, or auth-client retry option cloning.
<!-- END_FILE_RESEARCH: sources/cloud-native/soci-snapshotter/fs/remote/resolver_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/soci-snapshotter/fs/remote/util.go -->
# sources/cloud-native/soci-snapshotter/fs/remote/util.go

Purpose: provides range-region utilities for HTTP byte range operations and fetched-size accounting.

Important APIs and flow: `region` stores inclusive byte bounds and `size` returns `e-b+1`. `superRegion` returns the smallest region covering a non-empty list. `regionSet` stores sorted non-overlapping regions. `add` inserts a region while merging overlapping or adjacent regions and ignoring regions already contained by an existing entry. `totalSize` sums merged region sizes.

State and persistence: `regionSet` is an in-memory slice that callers must protect if shared concurrently. The blob implementation wraps it with a mutex.

Dependencies and integration: used by `httpFetcher.fetch` to coalesce requested ranges, `remoteFetcher.fetch` to map custom fetchers to a single super-region, and `blob.FetchedSize` to report fetched coverage.

Risks and test signals: `superRegion` assumes at least one region. The insertion algorithm is O(n) and uses slice splicing/allocations, which is acceptable for small region lists but could cost more with many ranges. Tests cover overlapping, containing, duplicate, adjacent, and disjoint merge cases.
<!-- END_FILE_RESEARCH: sources/cloud-native/soci-snapshotter/fs/remote/util.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/soci-snapshotter/fs/remote/util_test.go -->
# sources/cloud-native/soci-snapshotter/fs/remote/util_test.go

Purpose: tests `regionSet.add` merge behavior for overlapping, contained, duplicate, adjacent, and disjoint byte ranges.

Important APIs and flow: `TestRegionSet` iterates table cases, adds each input region to a fresh set, and compares the resulting sorted merged slice with `reflect.DeepEqual`. Cases explicitly note that `region.e` is inclusive, so `{1,3}` and `{4,6}` merge into `{1,6}`.

State and persistence: pure in-memory table test.

Dependencies and integration: protects range coalescing used by remote HTTP fetch requests and fetched-size accounting.

Risks and test signals: good branch coverage for merge semantics. It does not test `totalSize`, `superRegion`, negative bounds, or concurrent access, which are handled by callers or assumed invalid.
<!-- END_FILE_RESEARCH: sources/cloud-native/soci-snapshotter/fs/remote/util_test.go -->
