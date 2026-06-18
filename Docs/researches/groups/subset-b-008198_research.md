# Research: subset-b-008198

Grouped research for the requested MinIO `cmd` source files. Each section is wrapped with the exact source-path markers used by the reconciliation lane.

<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio/cmd/metrics-v3-system-process.go -->
# sources/object-store/minio/cmd/metrics-v3-system-process.go

This file defines the v3 `/system/process` metric loader for the current MinIO process. It declares metric names and `MetricDescriptor` values for goroutine count, uptime, CPU time, resident and virtual memory, file descriptor limits and open descriptors, process IO byte/syscall counters, and distributed namespace lock read/write totals.

The main APIs are `loadProcessMetrics`, `loadProcFSMetrics`, `loadProcStatMetrics`, and `loadProcIOMetrics`. `loadProcessMetrics` is a `MetricsLoaderFn`; it always records `runtime.NumGoroutine`, records uptime when `globalBootTime` is set, skips procfs collection on Windows and macOS, and otherwise uses `procfs.Self()` to load `/proc` stat, IO, limits, and fd counts. In distributed erasure mode it also reads `globalLockServer.stats()` to expose lock pressure.

Control flow is defensive and best-effort. Procfs failures are logged through `metricsLogIf` but do not fail collection; missing or zero values are simply omitted because `MetricValues.Set` only stores positive values. State is read-only against process globals and Linux procfs, with no persistence. Integration points are `metrics-v3.go` registration, the shared `MetricValues` descriptor validation layer, `globalLockServer`, `globalBootTime`, and platform constants.

Risks: zero-valued metrics disappear rather than reporting zero, which can confuse dashboards after restart or on idle nodes. Procfs support is Linux-centric. Lock metrics depend on a non-nil lock server and distributed mode. Test signal is indirect: no dedicated test exists, so coverage comes through v3 metrics integration and the descriptor contract.
<!-- END_FILE_RESEARCH: sources/object-store/minio/cmd/metrics-v3-system-process.go -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio/cmd/metrics-v3-types.go -->
# sources/object-store/minio/cmd/metrics-v3-types.go

This file is the shared framework for MinIO v3 metric groups. It turns collector paths into Prometheus name prefixes, models metric type and descriptor metadata, stores loader-produced values, converts them to Prometheus metrics, joins loader functions, and implements `prometheus.Collector` for a `MetricsGroup`.

Important types are `collectorPath`, `MetricType`, `MetricDescriptor`, `MetricValues`, `MetricsLoaderFn`, `BucketMetricsLoaderFn`, and `MetricsGroup`. `MetricDescriptor` owns metric name, type, help, and variable labels; `getLabelSet` caches the label set. `MetricValues.Set` validates metric names and labels against descriptors and panics on descriptor or label misuse. `SetHistogram` converts an existing `HistogramVec` through `getHistogramMetrics`, applies label filters, bucket filters, label renames, and extra labels, then stores non-zero samples. `MetricsGroup.Collect` invokes either a normal loader or bucket loader, wraps any loader error with `logger.CriticalIf`, converts the collected values, and emits them.

State is mostly in-memory: descriptor maps, cached label sets, a shared `metricsCache`, and a locked bucket list for bucket metric collection. There is no persistence. Integration is broad: every v3 metric file contributes descriptors and loaders that plug into this contract, while `metrics-v3.go` registers groups and sets the cache.

Risks: `Set` and validation paths deliberately panic on programmer errors; this is useful at startup but can turn bad loader output into scrape failures. `Collect` uses `GlobalContext`, so it is coupled to server lifecycle globals. Values of zero are dropped. Test signal is implicit through any metrics loader or scrape tests; this file itself has no direct unit tests.
<!-- END_FILE_RESEARCH: sources/object-store/minio/cmd/metrics-v3-types.go -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio/cmd/metrics-v3.go -->
# sources/object-store/minio/cmd/metrics-v3.go

This file assembles the v3 metrics catalog. It defines collector paths under `/minio/metrics/v3`, constructs all `MetricsGroup` instances, adds labels and cache objects, registers each group into its own Prometheus sub-registry, and records the sorted path list for routing and discovery.

The exported behavior is centered on `newMetricGroups(r *prometheus.Registry) *metricsV3Collection`. The function builds groups for API requests, bucket API, bucket replication, internode network, drives, memory, CPU, process, cluster health, usage, erasure set health, notification, IAM, replication, config, ILM, scanner, audit, logger webhook, and debug Go collector output. Bucket groups use `NewBucketMetricsGroup` because the bucket list arrives from the request path; non-bucket groups use `NewMetricsGroup`. Non-cluster groups get constant `server` label data through `AddExtraLabels`, currently including `serverName` and `globalLocalNodeName`.

State is runtime registration state: maps from `collectorPath` to groups, a shared `metricsCache`, per-path gatherers, and the sorted collector path list. There is no durable persistence. Integration points include every metric descriptor/loader file in `cmd`, Prometheus `collectors.NewGoCollector`, the outer metrics v3 HTTP route, and global node identity.

Risks: descriptor and loader mismatches panic via `MetricsGroup.validate` or `MetricValues.Set`. Every path is registered into both a sub-registry and the supplied root registry; duplicate registration would be fatal. The group list is a central integration hotspot whenever metrics are renamed or added. Test signal is indirect, from compile-time references to all metric descriptors and any metrics endpoint tests.
<!-- END_FILE_RESEARCH: sources/object-store/minio/cmd/metrics-v3.go -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio/cmd/metrics.go -->
# sources/object-store/minio/cmd/metrics.go

This file implements the legacy Prometheus metrics endpoint and authentication middleware. It registers legacy histograms and collectors, gathers local server, storage, HTTP, network, healing, bucket usage, and version metrics, and serializes Prometheus output using negotiated exposition format.

Key APIs are `newMinioCollector`, `minioCollector.Collect`, `metricsHandler`, `AuthMiddleware`, and `NoAuthMiddleware`. The collector emits version info and delegates to `storageMetricsPrometheus`, `nodeHealthMetricsPrometheus`, `bucketUsageMetricsPrometheus`, `networkMetricsPrometheus`, `httpMetricsPrometheus`, and `healingMetricsPrometheus`. These functions read global subsystems such as `globalNotificationSys`, `globalBackgroundHealState`, `globalHTTPStats`, `globalConnStats`, replication stats, data usage from backend, endpoint disk metadata, and `ObjectLayer.StorageInfo`.

State is read from global runtime services and object-layer persisted usage data. No metrics state is persisted here beyond the globally registered Prometheus histograms. `metricsHandler` builds a fresh registry per handler setup, combines it with `prometheus.DefaultGatherer`, sets trace context names, negotiates content type, and streams metric families. `AuthMiddleware` calls `metricsRequestAuthenticate`, validates the `prometheus` issuer, builds credentials, and checks `policy.PrometheusAdminAction` via IAM.

Risks: legacy metrics gather many live global systems and can omit metrics when object layer or usage data is unavailable. Several counters are emitted from current snapshots, so semantic correctness depends on upstream stats. Auth failures intentionally map to generic authentication errors. Tests are not in this file; test signal is mostly endpoint integration and compile-time coupling.
<!-- END_FILE_RESEARCH: sources/object-store/minio/cmd/metrics.go -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio/cmd/mrf.go -->
# sources/object-store/minio/cmd/mrf.go

This file implements MinIO's background MRF queue for partial operations that reached quorum but could not update every disk. It queues affected buckets or objects, persists queued work during shutdown, reloads it on startup, and drives healing once disks reconnect.

Core types are `PartialOperation` and `mrfState`. `PartialOperation` records bucket, object, version IDs or packed version bytes, erasure set and pool indexes, queue time, and whether deep bitrot healing is needed. `mrfState` owns a large buffered channel, close flags, and a wait group. `addPartialOp` drops work silently if the state is closing, closed, nil, or the channel is full. `shutdown` stops acceptance, closes the queue, streams a four-byte format/version header followed by msgp-encoded operations to `.minio.sys/buckets/.heal/mrf/list.bin` on the first writable local drive. `startMRFPersistence` scans local drives for that file, validates header format/version, decodes operations back to `opCh`, and deletes the file after successful load.

`healRoutine` consumes queued operations until global shutdown or channel close. It skips transient MinIO internal paths, waits at least one second for recent network failures, applies a dynamic sleeper, chooses normal or deep scan, and calls `healBucket` or `healObject`.

Risks: enqueue overflow drops work; shutdown persistence succeeds on only one local drive and stops on first success. Invalid/corrupt MRF files are skipped by trying another drive. Version byte decoding assumes 16-byte UUID chunks. Test signal is in generated msgp tests, not the queue/heal logic itself.
<!-- END_FILE_RESEARCH: sources/object-store/minio/cmd/mrf.go -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio/cmd/mrf_gen.go -->
# sources/object-store/minio/cmd/mrf_gen.go

This generated file provides tinylib/msgp serialization for `PartialOperation`. It implements `DecodeMsg`, `EncodeMsg`, `MarshalMsg`, `UnmarshalMsg`, and `Msgsize`, allowing MRF state to be streamed to disk and restored without reflection.

The wire shape is an eight-field map: `Bucket`, `Object`, `VersionID`, `Versions`, `SetIndex`, `PoolIndex`, `Queued`, and `BitrotScan`. Decode paths read map keys, populate known fields, and skip unknown fields for forward compatibility. Encode and marshal paths write the fixed map header and fields in a stable order. `Msgsize` returns an upper-bound allocation estimate based on current field lengths.

Control flow is mechanical: decode loops over the incoming map count and wraps field-specific errors with `msgp.WrapError`; marshal preallocates through `msgp.Require`. State and persistence behavior are tied to `mrf.go`, where these methods serialize operations into `.minio.sys/buckets/.heal/mrf/list.bin`. The file itself has no durable state.

Dependencies are `github.com/tinylib/msgp/msgp` and the concrete `PartialOperation` definition. Integration risk is schema drift: changing `PartialOperation` requires regeneration, and editing this file manually would be overwritten. Because unknown fields are skipped, older readers can tolerate additive fields, but removed or renamed fields may lose data. Test signal is strong for serialization mechanics via `mrf_gen_test.go`, including marshal/unmarshal, encode/decode, skip, and benchmarks.
<!-- END_FILE_RESEARCH: sources/object-store/minio/cmd/mrf_gen.go -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio/cmd/mrf_gen_test.go -->
# sources/object-store/minio/cmd/mrf_gen_test.go

This file tests and benchmarks msgp serialization generated for `PartialOperation`. It does not test MRF queue behavior, healing, or shutdown persistence, but it verifies that the generated codecs can round-trip an empty `PartialOperation` and that msgp skip handling consumes the encoded payload fully.

The main tests are `TestMarshalUnmarshalPartialOperation` and `TestEncodeDecodePartialOperation`. The first marshals a zero-value operation to bytes, unmarshals it, asserts no trailing bytes remain, then verifies `msgp.Skip` also consumes the full buffer. The second encodes through the streaming `msgp.Encode` path, checks whether `Msgsize` underestimates, decodes into a new value, and checks that a reader can skip the encoded message.

Benchmarks cover allocation and throughput for `MarshalMsg`, append-style marshal reuse, `UnmarshalMsg`, streaming `EncodeMsg`, and streaming `DecodeMsg`. They use zero-value data, so they primarily measure framework overhead and fixed field encoding rather than large bucket/object names or version byte arrays.

Dependencies are Go `testing`, `bytes`, and `tinylib/msgp`. Integration point is the generated `mrf_gen.go` codec consumed by `mrf.go` persistence. Risks: tests do not cover non-empty fields, malformed headers from the persistence file, forward-compatible unknown fields, or version-byte UUID content. Still, they provide a basic regeneration guard for msgp API correctness.
<!-- END_FILE_RESEARCH: sources/object-store/minio/cmd/mrf_gen_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio/cmd/namespace-lock.go -->
# sources/object-store/minio/cmd/namespace-lock.go

This file defines MinIO namespace locking for object operations. It abstracts local and distributed read/write locks behind `RWLocker`, tracks lock contexts, manages local lock maps with reference counts, and delegates distributed locks to `dsync.DRWMutex`.

Core APIs include `newNSLock`, `nsLockMap.NewNSLock`, local `lock`/`unlock`, `localLockInstance.GetLock/GetRLock/Unlock/RUnlock`, `distLockInstance.GetLock/GetRLock/Unlock/RUnlock`, and `getSource`. Local mode stores `resource -> *nsLock` in `nsLockMap.lockMap`; each acquire increments `ref`, blocks on `lsync.LRWMutex`, and removes the map entry after failed acquisition or final unlock. Multi-path locks sort paths before construction to reduce deadlock risk and unwind previously acquired locks if a later path times out. Distributed mode creates a `dsync.DRWMutex` over prefixed paths and passes timeout and retry settings from `dynamicTimeout`.

State is in memory: the global local lock server, local lock maps, operation IDs, and contexts with cancel functions. There is no persistence. Integration points are all object-layer critical sections, distributed erasure lock servers, logger critical paths, timeout telemetry, and `runtime.Caller` source attribution.

Risks: local ref counting is concurrency-sensitive; a skipped race test documents historical risk around map entry deletion and competing lockers. Distributed read locking calls `GetRLock(ctx, cancel, ...)` while write locking uses `newCtx`, so cancellation behavior should be reviewed carefully. `getSource` tests hard-code line numbers and are fragile.
<!-- END_FILE_RESEARCH: sources/object-store/minio/cmd/namespace-lock.go -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio/cmd/namespace-lock_test.go -->
# sources/object-store/minio/cmd/namespace-lock_test.go

This file contains focused tests for namespace-lock source attribution and a skipped stress test for local lock map races. It exercises a narrow but important part of the locking implementation rather than full lock semantics.

`TestGetSource` wraps `getSource(2)` and compares the returned string to a hard-coded source location and function name. This validates the formatting contract used in lock diagnostics, but the test is intentionally fragile: adding lines above the test changes the expected line number. The comments warn maintainers about this coupling.

`TestNSLockRace` is skipped by default because it is long. It constructs repeated local `nsLockMap` instances and orchestrates a race in which a timed-out waiter can remove a lock-map entry while other waiters are trying to acquire the same resource. The failure condition is two later lockers acquiring what should be the same exclusive resource. The test includes a manual `lockMapMutex` hold to make the interleaving easier to reproduce.

State is test-local except for runtime scheduling. Dependencies are `runtime`, `testing`, and `time`. Integration value is diagnostic: it documents a known concurrency failure mode in `nsLockMap.lock`/`unlock`. Risk is limited default coverage because the race test is skipped; normal CI only catches `getSource` formatting regressions, not lock races.
<!-- END_FILE_RESEARCH: sources/object-store/minio/cmd/namespace-lock_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio/cmd/naughty-disk_test.go -->
# sources/object-store/minio/cmd/naughty-disk_test.go

This test helper wraps a `StorageAPI` and injects deterministic errors by API call number. It is used to simulate disk failures that are hard to reproduce with real storage, such as disk-not-found transitions, mid-operation IO failures, or persistent default failures.

The central type is `naughtyDisk`, containing the wrapped disk, a map from call number to error, an optional default error, a call counter, and a mutex. `newNaughtyDisk` creates the wrapper. `calcError` increments the call number under lock and returns a programmed error, the default error, or nil. Nearly every `StorageAPI` method calls `calcError` first and either returns that error in the method's expected shape or delegates to the real disk.

State is entirely in-memory and test-scoped. The wrapper preserves most real disk behavior when no error is injected, but deliberately overrides `GetDiskLoc` with `-1` indexes and special-cases `IsOnline`: if the injected error is `errDiskNotFound`, it reports true for the equality check path used by callers. `DeleteVersions` expands a single injected error across the returned error slice, and `ReadMultiple` closes the response channel on injected failure.

Dependencies are the broader MinIO storage interfaces and `madmin` scan modes. Risks: because this is a test helper, it can diverge from `StorageAPI` as methods evolve. Coverage signal is indirect; files using this helper define the actual behavioral assertions.
<!-- END_FILE_RESEARCH: sources/object-store/minio/cmd/naughty-disk_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio/cmd/net.go -->
# sources/object-store/minio/cmd/net.go

This file provides networking helpers for startup address validation, local interface discovery, endpoint rendering, host/IP classification, and comparing local addresses. It initializes package-level sets of local IPv4, IPv6, and loopback addresses from network interfaces.

Important functions include `mustSplitHostPort`, `mustGetLocalIPs`, `mustGetLocalIP4`, `mustGetLocalIP6`, `mustGetLocalLoopbacks`, `getHostIP`, `sortIPs`, `getConsoleEndpoints`, `getAPIEndpoints`, `isHostIP`, `extractHostPort`, `isLocalHost`, `sameLocalAddrs`, and `CheckLocalServerAddr`. Endpoint functions honor explicit global endpoint/host settings; otherwise they render URLs for local addresses using TLS state and configured ports. `sortIPs` keeps hostnames first, pushes loopback addresses later, and orders IPv4 addresses by the last octet for friendlier display.

State is computed from OS network interfaces and global MinIO configuration. DNS lookup uses `globalDNSCache.LookupHost(GlobalContext)`. There is no persistence. Integration points include command-line address validation, console/API startup output, endpoint construction, and config errors from `internal/config`.

Risks: package-level address sets are initialized once, so interface changes after startup are not reflected in `localIP4/localIP6/localLoopbacks`. Local-host checks depend on DNS behavior and loopback normalization. `extractHostPort` infers ports from scheme and errors when it cannot. Tests in `net_test.go` cover parsing, sorting, endpoint rendering, local address comparison, and IP detection.
<!-- END_FILE_RESEARCH: sources/object-store/minio/cmd/net.go -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio/cmd/net_test.go -->
# sources/object-store/minio/cmd/net_test.go

This file unit-tests the network helper behavior from `net.go`. It focuses on address parsing, local endpoint formatting, IP sorting, local-host validation, and IP literal detection.

`TestMustSplitHostPort` verifies numeric ports and service names such as `https` and `http`. `TestSortIPs` checks hostname preservation, loopback demotion, and last-octet sorting across mixed inputs. `TestMustGetLocalIP4` and `TestGetHostIP` assert that localhost resolves to a usable loopback address. `TestGetAPIEndpoints` temporarily mutates `globalMinioHost` and `globalMinioPort` to verify rendered API endpoints. `TestCheckLocalServerAddr` covers wildcard, localhost, empty, remote, and invalid port inputs. `TestExtractHostPort`, `TestSameLocalAddrs`, and `TestIsHostIP` cover URL-like, bare host/port, empty, remote, and IPv6-zone forms.

State mutation is limited but important: `TestGetAPIEndpoints` saves and restores globals. Other tests depend on host DNS and local interface behavior, so they may be environment-sensitive. Dependencies include `testing`, `reflect`, MinIO string sets, and real network lookup through production helpers.

Risks: tests assume `localhost` intersects with `127.0.0.1`, which is common but still environment-dependent. They do not cover dynamic interface changes, IPv6 endpoint rendering in detail, or DNS cache failure injection. The suite is still a useful guard for startup address UX.
<!-- END_FILE_RESEARCH: sources/object-store/minio/cmd/net_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio/cmd/notification-summary.go -->
# sources/object-store/minio/cmd/notification-summary.go

This small file provides capacity aggregation helpers used by metrics and notification/admin summaries. It computes raw and usable total/free capacity from `madmin.Disk` slices and object-layer storage backend parity information.

The APIs are `GetTotalCapacity`, `GetTotalUsableCapacity`, `GetTotalCapacityFree`, and `GetTotalUsableCapacityFree`. Raw helpers simply sum `TotalSpace` or `AvailableSpace` for all disks. Usable helpers skip disks with invalid pool indexes or pool indexes outside `StorageInfo.Backend.StandardSCData`, then exclude parity disks by comparing `disk.DiskIndex` with the pool's standard storage class data count. Only data disks contribute to usable capacity.

State is read-only input data with no persistence. Integration points include legacy `storageMetricsPrometheus`, cluster health metrics, `NotificationSys.StorageInfo`, and admin/server info paths that need aggregate capacity. The code depends on `madmin-go` disk structs and the MinIO `StorageInfo` alias defined in object API data types.

Risks: usable capacity depends on correct `PoolIndex`, `DiskIndex`, and `StandardSCData` values. Invalid indexes are silently skipped to avoid crashes, following a referenced historical issue. This can under-report capacity if backend metadata is incomplete. There are no direct tests in this file; test signal is integration-level through storage metrics and admin info behavior.
<!-- END_FILE_RESEARCH: sources/object-store/minio/cmd/notification-summary.go -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio/cmd/notification.go -->
# sources/object-store/minio/cmd/notification.go

This file implements MinIO peer notification and cluster fan-out for internal admin, IAM, bucket metadata, metrics, profile, service-control, rebalance, bandwidth, performance, and replication MRF operations. It is for peer-to-peer MinIO notifications, not external event targets.

Core types are `NotificationSys`, `NotificationPeerErr`, and `NotificationGroup`. `NotificationSys` holds remote peer REST clients and an all-peer slice that includes a nil/self slot. `NotificationGroup` wraps bounded workers, retry count, and indexed peer errors; `Go` retries calls with jitter unless context is canceled and logs final failures with peer tags.

The file follows repeated control-flow patterns: allocate result slices matching peers, launch bounded or unbounded goroutines over non-nil peer clients, call the matching `peerRESTClient` method, log peer errors, then append or merge local state where needed. IAM and policy methods fan out reload/delete calls. Profiling downloads remote profile data into a shared zip with a mutex and embeds local profile data. Storage/server info fills offline disk data on peer failure. Metrics methods open peer metric channels and merge them through `collectPeerMetrics`. Speed and network tests run remote and local work concurrently. Bucket deletion clears local caches before notifying peers. Replication MRF streams remote and local entries into a buffered channel.

State is mostly live global state: peer REST clients, replication stats, bucket metadata systems, object layer, endpoints, transition state, bucket monitor, service freeze state, and replication pool. Persistence is indirect through remote operations and object-layer metadata. Risks include high fan-out cost on large clusters, partial failure semantics, nil-peer handling, closure correctness, and channel closure under cancellation. Test signal is mostly integration; this file itself has no direct unit tests.
<!-- END_FILE_RESEARCH: sources/object-store/minio/cmd/notification.go -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio/cmd/object-api-common.go -->
# sources/object-store/minio/cmd/object-api-common.go

This file contains shared object-layer constants, the global object API pointer and mutex, storage initialization options, and the factory that chooses local or remote storage implementations for an endpoint.

Important constants include legacy and current erasure block sizes, bucket metadata prefix, deleted bucket prefix, and the empty-object ETag. `globalObjLayerMutex` protects updates to `globalObjectAPI`, which is the process-wide object layer accessed by helper functions elsewhere. `storageOpts` carries `cleanUp` and `healthCheck` options into disk construction. `newStorageAPI` checks `Endpoint.IsLocal`: local endpoints are opened with `newXLStorage`, wrapped in `newXLStorageDiskIDCheck`, and respect cleanup and health-check settings; remote endpoints are represented by `newStorageRESTClient` using the current global grid.

State is foundational runtime state. It does not persist data itself, but it selects components that read and write erasure data, metadata, and remote disk RPCs. Integration points include server bootstrap, erasure-set construction, storage health checks, bucket metadata paths, MRF storage persistence, and any object-layer code that reads `globalObjectAPI`.

Risks: initialization errors for local storage propagate directly and can stop disk setup. Remote storage depends on `globalGrid.Load()` being initialized. The global object layer must be updated under its mutex elsewhere; misuse can race. No direct tests appear here, so coverage comes from bootstrap and object-layer integration tests.
<!-- END_FILE_RESEARCH: sources/object-store/minio/cmd/object-api-common.go -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio/cmd/object-api-datatypes.go -->
# sources/object-store/minio/cmd/object-api-datatypes.go

This file defines many core object API data contracts: backend type aliases, object-size and version-count histogram intervals, bucket metadata, object metadata, replication payloads, multipart/listing responses, transition/delete records, completed multipart request structures, and get-object-attributes XML responses.

Key APIs and methods include `ObjectInfo.ExpiresStr`, `ObjectInfo.ArchiveInfo`, `ObjectInfo.Clone`, `ObjectInfo.tierStats`, `ReplicateObjectInfo.ToObjectInfo`, and `ListMultipartsInfo.Lookup`. `ObjectInfo` is the central structure and carries bucket/name, modtime, size, actual size, directory marker, ETag, version status, delete marker, transition/restore state, content headers, storage class, replication and purge status, user metadata/tags, parts, internal reader/writer handles excluded from msgp/json, access time, legacy/inlined flags, checksums, and data/parity counts. `Clone` deep-copies `UserDefined` but carries slices and readers by reference. `ArchiveInfo` decrypts archive metadata when marked encrypted.

State is structural and serialized by generated msgp code in `object-api-datatypes_gen.go`. These types are passed across object-layer, replication, listing, multipart, lifecycle, transition, and admin paths. Histogram interval globals feed data usage accounting and metrics.

Risks: schema changes affect on-disk or RPC msgp compatibility and require regeneration. `ToObjectInfo` is explicitly partial and sets `DeleteMarker: true`, so callers must not treat it as complete metadata. `Clone` is not a full deep copy for all nested fields. There are no direct tests in this file; generated serialization and higher-level object API tests provide coverage.
<!-- END_FILE_RESEARCH: sources/object-store/minio/cmd/object-api-datatypes.go -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio/cmd/object-api-datatypes_gen.go -->
# sources/object-store/minio/cmd/object-api-datatypes_gen.go

This generated msgp file serializes selected object API data types for fast internal persistence and RPC payloads. It implements `MarshalMsg`, `UnmarshalMsg`, and `Msgsize` for `BackendType`, `BucketInfo`, `CompleteMultipartUpload`, `CompletePart`, `DeletedObjectInfo`, `ListMultipartsInfo`, `ListObjectVersionsInfo`, `ListObjectsInfo`, `ListObjectsV2Info`, `ListPartsInfo`, `MultipartInfo`, `NewMultipartUploadResult`, `ObjectInfo`, `PartInfo`, `ReplicateObjectInfo`, and `TransitionedObject`.

Control flow is generated and uniform: marshal methods preallocate using `Msgsize`, write fixed map headers and fields in a stable order, and delegate nested values to their own msgp methods. Unmarshal methods read map headers, switch on field names, populate known fields, clear and reuse maps when possible, resize slices based on array headers, handle nil `ObjectInfo.ActualSize`, and skip unknown fields. Error wrapping includes field names and array indexes for diagnosis.

State and persistence are the serialized forms of object metadata, multipart/list responses, replication decisions/status, transition metadata, checksums, and bucket info. Dependencies include `tinylib/msgp` and replication status types that themselves implement msgp. Integration is tightly coupled to the definitions and `go:generate` directive in `object-api-datatypes.go`.

Risks: manual edits will be overwritten; source type changes require regeneration. Field order and map sizes must match generated code. The generated code supports unknown-field skipping for additive compatibility, but removing/renaming fields can drop data. Test signal is not local because generation disabled tests for this file; coverage is indirect through consumers and compile-time schema checks.
<!-- END_FILE_RESEARCH: sources/object-store/minio/cmd/object-api-datatypes_gen.go -->
