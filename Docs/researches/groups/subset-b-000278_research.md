# subset-b-000278 Research

Grouped research for the listed stargz-snapshotter files. Each section preserves its original source path and is delimited for deterministic splitting into `Docs/researches/<source_path>_research.md`.

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/stargz-snapshotter/fs/reader/reader.go -->
# sources/cloud-native/stargz-snapshotter/fs/reader/reader.go

## Purpose
Implements the filesystem-facing reader for an eStargz blob. It bridges `metadata.Reader`, a blob cache, digest verification, metrics, on-demand chunk reads, bulk caching, and optional whole-file passthrough file descriptor retrieval.

## Important APIs, Types, And Functions
`Reader` exposes `OpenFile`, `Metadata`, `Close`, and `LastOnDemandReadTime`. `VerifiableReader` wraps a `reader` until callers choose `VerifyTOC` or `SkipVerify`; `VerifyTOC` validates the TOC digest and enables per-chunk digest verification. `Cache` walks regular files and caches chunks concurrently. `file.ReadAt` is the primary lazy-read path, while `GetPassthroughFd`, `prefetchEntireFile`, `prefetchEntireFileSequential`, `processBatchChunks`, and `checkHoles` build a full-file cache object for passthrough FUSE use.

## Control Flow
`NewReader` wires metadata, cache, layer digest, and verifier. `OpenFile` opens a metadata file with a preread callback that caches adjacent chunks if the estargz reader exposes them. `ReadAt` maps the request to chunk entries, tries chunk cache first, fetches/decompresses missing chunks through `metadata.File`, verifies if enabled, writes them into cache, and copies only the requested slice. Whole-file passthrough enumerates all chunks, chooses sequential mode if any chunk is larger than the merge buffer, otherwise processes chunks in parallel by batch and validates that the batch has no holes or overlaps before writing to cache.

## State And Persistence
State is in memory except for the supplied `cache.BlobCache`, which may be persistent depending on implementation. The reader tracks closed state, last on-demand read time, verification status, last verification error, and a pooled buffer. Cache keys are SHA-256 hashes of `id-offset-size`; whole-file passthrough uses `id-0-totalSize`.

## Dependencies And Integration
Depends on `metadata.Reader`/`File`, `cache.BlobCache`, `estargz` constants, OpenContainers digest verification, errgroup/semaphore concurrency, and common metrics counters. It is consumed by higher-level snapshot/FUSE code that needs metadata lookup plus chunk-backed `io.ReaderAt`.

## Risks And Test Signals
Important risks are stale or malformed metadata chunk entries, verification being skipped intentionally, cache writer commit/abort correctness, buffer sizing for passthrough, and concurrent batch reads producing gaps. Tests in `reader_test.go` and `testutil.go` cover compressed formats, cache hits/misses, verification timing, preread cache population, failed readers/verifiers, and batch hole detection.
<!-- END_FILE_RESEARCH: sources/cloud-native/stargz-snapshotter/fs/reader/reader.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/stargz-snapshotter/fs/reader/reader_test.go -->
# sources/cloud-native/stargz-snapshotter/fs/reader/reader_test.go

## Purpose
Adapts the generic reader test suite to the in-memory metadata backend. It is intentionally small because the real behavioral matrix lives in `testutil.go`.

## Important APIs, Types, And Functions
`TestReader` constructs a `TestRunner` that adapts `testing.T` to the local suite interface, then invokes `TestSuiteReader(testRunner, memorymetadata.NewReader)`.

## Control Flow
Each subtest name and body is delegated to `testing.T.Run`. The suite receives `memorymetadata.NewReader` as the `metadata.Store` factory, so all file-read, cache, verification, preread, and batch-processing cases run against the in-memory metadata implementation.

## State And Persistence
No production state is persisted. Test state is scoped to the `testing.T` lifecycle and in-memory caches created by the suite.

## Dependencies And Integration
Depends on `metadata/memory` and the same package's `TestSuiteReader`. This file is the integration point ensuring the generic reader contract remains true for the default in-memory metadata reader.

## Risks And Test Signals
The main risk is that the suite adapter hides failures if it mishandles `TestingT`; it checks the concrete type before invoking `Run`. Passing this test signals that `reader.go` works with the memory metadata reader across the comprehensive shared suite.
<!-- END_FILE_RESEARCH: sources/cloud-native/stargz-snapshotter/fs/reader/reader_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/stargz-snapshotter/fs/reader/testutil.go -->
# sources/cloud-native/stargz-snapshotter/fs/reader/testutil.go

## Purpose
Provides the reusable test suite for reader behavior. It builds eStargz fixtures, injects metadata stores and caches, and validates lazy reads, preread behavior, verification, failure handling, and whole-file batch merge logic.

## Important APIs, Types, And Functions
`TestSuiteReader` runs `testFileReadAt`, `testCacheVerify`, `testFailReader`, `testPreReader`, and `testProcessBatchChunks`. `makeFile` builds sample eStargz data and returns a concrete `*file`. Helpers such as `exceptFile`, `failIDVerifier`, `breakReaderAt`, `calledReaderAt`, `mockCache`, and `mockFile` force cache-hit, cache-miss, verifier-failure, and partial-read scenarios.

## Control Flow
The suite iterates over offsets, sizes, file sizes, cache population patterns, and compression formats. It verifies expected bytes, then confirms chunks were cached or avoided. Verification tests deliberately race `Cache` with `VerifyTOC` or `SkipVerify` to ensure errors before TOC verification surface from `VerifyTOC`, while later errors surface from `Cache`. Preread tests assert reading one file can cache neighbor file chunks that share compressed ranges. Batch tests run workers over artificial chunk sets and validate `checkHoles`.

## State And Persistence
All fixtures are in memory. State includes per-test memory caches, mock read call lists, mutable verifier failure sets, and a global `MockReadAtOutput` that is restored with cleanup.

## Dependencies And Integration
Depends on `util/testutil` to build eStargz data, gzip/zstd/external TOC compression factories, `metadata.Store`, `cache.NewMemoryCache`, and digest verifiers. It is reusable by any metadata backend that satisfies the reader contract.

## Risks And Test Signals
Signals include byte-accurate reads across chunk boundaries, cache avoidance for prefilled chunks, propagation of bad source readers and digest failures, preread side effects, and detection of incomplete or overlapping batch reads. Risks are combinatorial test cost and reliance on assumptions about eStargz chunk placement for preread fixtures.
<!-- END_FILE_RESEARCH: sources/cloud-native/stargz-snapshotter/fs/reader/testutil.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/stargz-snapshotter/fs/remote/blob.go -->
# sources/cloud-native/stargz-snapshotter/fs/remote/blob.go

## Purpose
Implements `Blob`, the lazy remote byte-range reader and cache manager for layer blobs. It handles cache-first reads, HTTP/IPFS handler-backed fetching, chunk-aligned prefetching, health checks, refresh, fetched byte accounting, and singleflight coalescing.

## Important APIs, Types, And Functions
`Blob` exposes `Check`, `Size`, `FetchedSize`, `ReadAt`, `Cache`, `Refresh`, and `Close`. `makeBlob` constructs internal state. `ReadAt` maps arbitrary reads to chunk-aligned `region`s, `prepareChunksForRead` tries cache and schedules misses, `fetchRange` coalesces identical range misses with `singleflight`, `fetchRegions` streams multipart results into cache and readers, and `cacheChunkData` commits fetched chunks.

## Control Flow
Reads first reject closed blobs and empty/out-of-range requests, compute aligned regions, and fill any cache hits directly into the caller buffer. Misses are represented by writers that copy only the requested subsection while the whole chunk is cached. Fetches use the current fetcher snapshot, request missing regions, parse multipart/singlepart responses, update `lastCheck`, and verify every requested region was delivered. Shared fetch callers copy the completed chunks from cache.

## State And Persistence
Persistent data lives in the supplied `cache.BlobCache`. In-memory state tracks fetcher, blob size, chunk sizes, check interval, fetch timeout, fetched `regionSet`, closed flag, and locks. `FetchedSize` sums merged fetched regions, not cache contents discovered before this process.

## Dependencies And Integration
Depends on `remote.fetcher` from `resolver.go`, `cache.BlobCache`, OCI descriptors, source registry hosts, errgroup, and singleflight. It is the remote content backend used by snapshotter filesystem code when source labels resolve to registry or custom handlers.

## Risks And Test Signals
Risks include incomplete multipart bodies, cache writer commit errors, stale signed redirect URLs, singleflight key granularity, and context/fetch timeout behavior. `blob_test.go` covers read/cache matrices, broken bodies/headers, parallel download coalescing, and check interval updates.
<!-- END_FILE_RESEARCH: sources/cloud-native/stargz-snapshotter/fs/remote/blob.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/stargz-snapshotter/fs/remote/blob_test.go -->
# sources/cloud-native/stargz-snapshotter/fs/remote/blob_test.go

## Purpose
Tests remote blob byte-range reads, cache population, multipart and single-range transports, failure handling, concurrent fetch coalescing, and health-check timing.

## Important APIs, Types, And Functions
`TestReadAt` drives the main matrix. `cacheAll`, `checkRead`, `checkCache`, and `checkAllCached` verify cache state. `TestFailReadAt` covers HTTP errors, truncated bodies, and missing headers. `TestParallelDownloadingBehavior` checks `fetchRange` singleflight behavior. `multiRoundTripper`, `failRoundTripper`, `brokenBodyRoundTripper`, and `brokenHeaderRoundTripper` simulate registries.

## Control Flow
The matrix varies request sizes, offsets, blob sizes, prefetch size, cache state, and multi-range support. Tests build `blob` instances with memory cache and fake HTTP fetchers, seed cache where needed, perform `ReadAt` or `Cache`, and compare returned data plus full chunk cache contents. Parallel tests launch three goroutines with identical, overlapping, or disjoint region maps and assert round-trip counts.

## State And Persistence
Only in-memory cache and mock transport counters are used. `callsCountRoundTripper.count` is atomic to support concurrent assertions.

## Dependencies And Integration
Depends on `cache.NewMemoryCache`, HTTP response construction, multipart writers, and the production `blob`/`httpFetcher` internals. It gives direct signals for registry range behavior without real network access.

## Risks And Test Signals
Strong signals are byte-accurate partial reads, chunk cache completeness, fallback from multi-range-disabled transports, error returns on malformed registry responses, singleflight behavior for identical requests, and `Check` avoiding work until expiration. Gaps include no real registry auth, no disk cache implementation, and limited stress for huge header/range lists.
<!-- END_FILE_RESEARCH: sources/cloud-native/stargz-snapshotter/fs/remote/blob_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/stargz-snapshotter/fs/remote/resolver.go -->
# sources/cloud-native/stargz-snapshotter/fs/remote/resolver.go

## Purpose
Resolves OCI layer descriptors into fetchers and blob readers. It supports custom remote handlers, Docker registry hosts, authenticated transports, redirects, size discovery, retry/backoff, multipart range parsing, signed URL refresh, and single-range fallback.

## Important APIs, Types, And Functions
`NewResolver` normalizes `config.BlobConfig`. `Resolver.Resolve` returns a `Blob`; `resolveFetcher` chooses a custom `Handler` or HTTP fetcher. `newHTTPFetcher`, `redirect`, and `getSize` build a registry URL and determine blob size. `httpFetcher.fetch`, `check`, `refreshURL`, and `genID` implement remote range access. `Handler` and `Fetcher` define extension points.

## Control Flow
Resolution first tries configured handlers. If none succeed, registry hosts are enumerated. Each host is validated, wrapped with authorization if needed, redirected with a `GET` range probe, and measured with `HEAD` or fallback `GET`. Fetching squashes adjacent/overlapping regions, optionally collapses to one range, performs `GET Range`, and interprets 200, 206 multipart, and 206 singlepart responses. Forbidden responses trigger URL refresh once; bad multi-range requests switch to single-range mode once.

## State And Persistence
HTTP fetcher state is in memory: current URL, headers, original registry headers, single-range mode, timeout, digest, and transport. Cache identity uses SHA-256 over `blobURL-b-e`, so refreshed redirected URLs do not change cache keys.

## Dependencies And Integration
Depends on containerd Docker resolver types, retryablehttp, registry authorizers, `fs/source.RegistryHosts`, blob config, metrics, OCI descriptors, and digest IDs. `remoteFetcher` adapts non-HTTP handlers into the same internal fetcher interface.

## Risks And Test Signals
Risks include registry-specific redirect and HEAD behavior, large multi-range headers, unsigned `Content-Range` parsing, random jitter panics if crypto randomness fails, and unsupported nested redirects. Tests cover mirror selection, custom headers, redirects, check failures, and retry behavior.
<!-- END_FILE_RESEARCH: sources/cloud-native/stargz-snapshotter/fs/remote/resolver.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/stargz-snapshotter/fs/remote/resolver_test.go -->
# sources/cloud-native/stargz-snapshotter/fs/remote/resolver_test.go

## Purpose
Tests HTTP fetcher resolution against registry mirrors, redirects, headers, check behavior, and retryable transport configuration.

## Important APIs, Types, And Functions
`TestMirror` is the main resolver matrix. `checkFetcherURL` validates selected hosts. `sampleRoundTripper` simulates success, error status codes, redirects, and expected headers. `TestCheck` exercises `httpFetcher.check`; `TestRetry` verifies retryablehttp integration. `hostSimple`, `hostWithHeaders`, and `hostsConfig` build `source.RegistryHosts` fixtures.

## Control Flow
Tests construct a dummy reference and digest, then invoke `newHTTPFetcher` with configured mirrors. The fake transport validates custom headers, returns redirect locations or status codes per URL pattern, and provides content lengths for size detection. After resolution, tests call `check` and `refreshURL` to ensure the selected host remains consistent.

## State And Persistence
No persistence. State consists of fake transport maps and retry counters.

## Dependencies And Integration
Depends on containerd `reference`, Docker registry host structs, retryablehttp, OCI descriptors, and the production resolver internals. It specifically validates integration with `source.RegistryHosts` ordering and per-host headers.

## Risks And Test Signals
Signals include fallback from bad mirrors to good mirrors or origin, rejection of invalid mirror hostnames, redirect host selection, preservation of headers to registry but not redirected backend, check behavior, and retry count across transient failures. It does not exercise real TLS, authentication token exchange, or actual registry behavior.
<!-- END_FILE_RESEARCH: sources/cloud-native/stargz-snapshotter/fs/remote/resolver_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/stargz-snapshotter/fs/remote/util.go -->
# sources/cloud-native/stargz-snapshotter/fs/remote/util.go

## Purpose
Defines range primitives used by remote blob and resolver code. Regions model inclusive HTTP byte ranges, and `regionSet` maintains sorted, minimally merged coverage.

## Important APIs, Types, And Functions
`region` stores beginning `b` and inclusive end `e`; `size` returns `e-b+1`. `superRegion` spans a non-empty slice of regions. `regionSet.add` inserts and merges overlapping or adjacent ranges, and `totalSize` sums merged region sizes.

## Control Flow
`regionSet.add` scans from the tail of the sorted slice. It returns early if an existing range contains the new one, expands the new range while removing overlapped entries, inserts once no further overlap is possible, or prepends if the new region belongs before all existing entries.

## State And Persistence
State is the in-memory sorted `[]region`; there is no persistence. The add operation mutates the slice in place and is documented as O(n).

## Dependencies And Integration
Used by `blob.go` to track fetched coverage and by `resolver.go` to collapse requested ranges before HTTP or custom fetches. Its inclusive-end semantics match HTTP `Range` and `Content-Range` headers.

## Risks And Test Signals
Risks are off-by-one errors around adjacency and inclusive ends, which would cause overfetch, underfetch, or incorrect `FetchedSize`. `util_test.go` covers containment, overlap, adjacency, ordering, and multi-region merging.
<!-- END_FILE_RESEARCH: sources/cloud-native/stargz-snapshotter/fs/remote/util.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/stargz-snapshotter/fs/remote/util_test.go -->
# sources/cloud-native/stargz-snapshotter/fs/remote/util_test.go

## Purpose
Validates `regionSet.add` merging behavior for inclusive HTTP byte ranges.

## Important APIs, Types, And Functions
`TestRegionSet` feeds ordered and unordered region sequences into `regionSet.add` and compares the final `rs` slice with expected merged ranges using `reflect.DeepEqual`.

## Control Flow
Each case constructs an empty `regionSet`, inserts all input regions, then asserts merged output. Cases cover partial overlap, total containment, duplicate ranges, end-start adjacency, bridging gaps with a later region, and multiple disjoint outputs.

## State And Persistence
All state is local to each table entry. No persistence or external IO.

## Dependencies And Integration
Depends only on `testing` and `reflect`. The test is small but important because both remote request collapsing and fetched byte accounting depend on this primitive.

## Risks And Test Signals
Passing tests signal correct inclusive-end adjacency behavior such as `{1,3}` plus `{4,6}` merging into `{1,6}`. Gaps remain around empty inputs to `superRegion`, negative ranges, and concurrency, which are handled by caller assumptions rather than this test.
<!-- END_FILE_RESEARCH: sources/cloud-native/stargz-snapshotter/fs/remote/util_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/stargz-snapshotter/fs/source/source.go -->
# sources/cloud-native/stargz-snapshotter/fs/source/source.go

## Purpose
Converts containerd snapshot/image labels into typed remote blob source information and appends the labels needed by stargz snapshotter during unpack.

## Important APIs, Types, And Functions
`GetSources` and `RegistryHosts` are function types. `Source` carries registry hosts, image reference, target descriptor, and manifest layer context. `FromDefaultLabels` parses stargz labels into `Source`. `AppendDefaultLabelsHandlerWrapper` annotates layer descriptors during image traversal. `AppendExtraLabelsHandler`, `appendWithValidation`, and `layerFromDigest` add optional URL and prefetch metadata while respecting label size limits.

## Control Flow
Default label parsing requires reference and digest labels, optionally parses neighboring layer digests and per-index URLs, copies target URLs into descriptor URLs, and returns one source. Handler wrappers intercept manifest children, identify layer descriptors, populate annotations with reference, digest, later layer digests, neighboring URLs, prefetch size, and layer URLs.

## State And Persistence
No long-lived local state. State is embedded in OCI descriptor annotations and later persisted by containerd snapshot labels. Label validation can truncate optional lists, affecting prefetch optimization rather than correctness.

## Dependencies And Integration
Depends on containerd images, labels, Docker registry references, snapshotter config labels, OCI descriptors, and opencontainers digest parsing. It is the handoff between image unpack/conversion and remote filesystem resolution.

## Risks And Test Signals
Risks include missing required labels, invalid digest strings, label length truncation, and mismatched layer-index URL annotations. Tests are not in this subset; integration signal is downstream snapshot mount resolving sources successfully and pre-resolving neighboring layers when labels are present.
<!-- END_FILE_RESEARCH: sources/cloud-native/stargz-snapshotter/fs/source/source.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/stargz-snapshotter/fusemanager/api/api.pb.go -->
# sources/cloud-native/stargz-snapshotter/fusemanager/api/api.pb.go

## Purpose
Generated gogo/protobuf and gRPC bindings for the fuse manager service. It provides Go structs, client interface, server interface, registration, and unary RPC handlers corresponding to `api.proto`.

## Important APIs, Types, And Functions
Defines `StatusRequest`, `InitRequest`, `MountRequest`, `CheckRequest`, `UnmountRequest`, `StatusResponse`, and empty `Response`. `StargzFuseManagerServiceClient` exposes `Status`, `Init`, `Mount`, `Check`, and `Unmount`. `StargzFuseManagerServiceServer`, `UnimplementedStargzFuseManagerServiceServer`, and `RegisterStargzFuseManagerServiceServer` define server-side integration.

## Control Flow
Client methods invoke full method names such as `/fusemanager.StargzFuseManagerService/Mount`. Server handler functions decode requests, call the implementation directly or through a unary interceptor, and return either a response struct or a gRPC error.

## State And Persistence
Generated structs hold request/response fields and proto runtime caches. There is no business persistence; errors are returned through gRPC status, not encoded in `Response`.

## Dependencies And Integration
Depends on `github.com/gogo/protobuf/proto` and `google.golang.org/grpc`. Used by `fusemanager/client.go`, `service.go`, `fusemanager.go`, and tests.

## Risks And Test Signals
Risks are proto/source drift and generated code becoming stale after `api.proto` edits. Compile-time assertions check protobuf and gRPC compatibility. Functional signals come from `fusemanager_test.go`, which exercises the generated client/server path.
<!-- END_FILE_RESEARCH: sources/cloud-native/stargz-snapshotter/fusemanager/api/api.pb.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/stargz-snapshotter/fusemanager/api/api.proto -->
# sources/cloud-native/stargz-snapshotter/fusemanager/api/api.proto

## Purpose
Defines the fuse manager gRPC API contract used between clients and the long-running fuse manager server.

## Important APIs, Types, And Functions
`StargzFuseManagerService` has unary RPCs `Status`, `Init`, `Mount`, `Check`, and `Unmount`. `InitRequest` carries `root` and serialized config bytes. `MountRequest` and `CheckRequest` carry mountpoint plus labels. `UnmountRequest` carries mountpoint. `StatusResponse` carries an `int32` status code; `Response` is empty.

## Control Flow
The proto is declarative. Runtime flow is generated by `api.pb.go`: clients call unary RPCs and the server returns empty success messages or gRPC errors.

## State And Persistence
No state is stored here. The schema determines what state can cross the process boundary; persisted mount state is implemented separately in `fusestore.go`.

## Dependencies And Integration
Uses proto3 with `go_package = "github.com/stargz-snapshotter/fusemanager/api"` and gogo/protobuf generation via `generate.go`. Integrated by fuse manager client and server code.

## Risks And Test Signals
Schema changes require regenerating `api.pb.go` and updating both sides. Empty `Response` means any future structured error or metadata would be a protocol change. Tests indirectly validate the schema through real gRPC calls in `fusemanager_test.go`.
<!-- END_FILE_RESEARCH: sources/cloud-native/stargz-snapshotter/fusemanager/api/api.proto -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/stargz-snapshotter/fusemanager/api/generate.go -->
# sources/cloud-native/stargz-snapshotter/fusemanager/api/generate.go

## Purpose
Hosts the `go:generate` directive for regenerating gogo/protobuf gRPC bindings from `api.proto`.

## Important APIs, Types, And Functions
The only executable directive is `//go:generate protoc --gogo_out=paths=source_relative,plugins=grpc:. api.proto`.

## Control Flow
When a developer runs `go generate` in this package, `protoc` reads `api.proto` and rewrites `api.pb.go` with source-relative paths and gRPC plugin output.

## State And Persistence
The directive itself has no runtime state. Generated output is persisted in `api.pb.go` by the generator.

## Dependencies And Integration
Requires `protoc` and `protoc-gen-gogo` with gRPC plugin support. It couples the protobuf schema to generated bindings used by the fuse manager client/server.

## Risks And Test Signals
Risks are missing generator tools, version skew, or forgetting to regenerate after schema changes. Compile/tests of fusemanager packages are the practical signal that generated code matches the proto and current dependencies.
<!-- END_FILE_RESEARCH: sources/cloud-native/stargz-snapshotter/fusemanager/api/generate.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/stargz-snapshotter/fusemanager/client.go -->
# sources/cloud-native/stargz-snapshotter/fusemanager/client.go

## Purpose
Implements a `snapshot.FileSystem` client backed by the fuse manager gRPC service. It lets containerd-stargz-grpc delegate mount, check, and unmount operations to a separate process.

## Important APIs, Types, And Functions
`Client` wraps `pb.StargzFuseManagerServiceClient`. `NewManagerClient` dials the Unix socket and sends `Init`. `newClient` configures grpc transport credentials, containerd Unix dialer, backoff, and message size limits. `Mount`, `Check`, and `Unmount` translate filesystem calls to RPC requests.

## Control Flow
Client creation dials `unix://<socket>`, marshals `Config` as JSON bytes, and calls `Init` with the root path. Later methods allocate the corresponding protobuf request, call the RPC, log on error, and return the gRPC error directly.

## State And Persistence
The client keeps only the generated gRPC client. It does not close the connection explicitly in this file. Durable mount state is owned by the server.

## Dependencies And Integration
Depends on containerd defaults/dialer, grpc insecure transport and backoff, fusemanager protobufs, snapshot `FileSystem`, and the local `Config` type from `service.go`.

## Risks And Test Signals
Risks include connection lifecycle leaks, Init coupling to every client creation, and opaque JSON config compatibility. `fusemanager_test.go` exercises `NewManagerClient` and the Mount/Check/Unmount RPC wrappers against an in-process server.
<!-- END_FILE_RESEARCH: sources/cloud-native/stargz-snapshotter/fusemanager/client.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/stargz-snapshotter/fusemanager/fusemanager.go -->
# sources/cloud-native/stargz-snapshotter/fusemanager/fusemanager.go

## Purpose
Provides the fusemanager executable entrypoints and process supervisor helpers. It can run the server in the foreground, self-spawn a detached manager process, and start the manager from another process.

## Important APIs, Types, And Functions
`Run` is the public entrypoint. `parseFlags` defines version, action, socket, fusestore, log level, and log path flags. `startNew` self-invokes the executable in the background. `waitUntilReady` polls status once through the global `address`. `runFuseManager` hosts the Unix socket gRPC server. `StartFuseManager` launches a separate fusemanager binary if the socket is absent.

## Control Flow
`run` handles version printing and dispatches `-action start` to self-spawn; otherwise it runs the server. The server removes stale socket files, listens on Unix socket, registers `Server`, serves in a goroutine, waits for SIGINT/SIGTERM or serve error, stops gRPC, and closes the fuse manager. `StartFuseManager` checks socket and executable paths, invokes the binary with `-action start`, and waits for it to finish.

## State And Persistence
State comes from package-level flag variables and process state. Persistent mount state is configured through `fusestore-path` and managed in `service.go`/`fusestore.go`.

## Dependencies And Integration
Depends on grpc, logrus, Unix signals, process execution, version metadata, and the generated protobuf server registration. It is the operational boundary for running fuse manager outside the main daemon.

## Risks And Test Signals
Risks include stale sockets, file descriptor/log file handling, `waitUntilReady` doing only one status call, global flag state in tests, and subprocess lifecycle ambiguity. Unit tests in this subset focus on the gRPC behavior rather than CLI process behavior.
<!-- END_FILE_RESEARCH: sources/cloud-native/stargz-snapshotter/fusemanager/fusemanager.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/stargz-snapshotter/fusemanager/fusemanager_test.go -->
# sources/cloud-native/stargz-snapshotter/fusemanager/fusemanager_test.go

## Purpose
Exercises the fuse manager client/server RPC path with a mocked filesystem implementation.

## Important APIs, Types, And Functions
`mockFileSystem` implements `snapshot.FileSystem` methods and records calls/errors. `mockServer` embeds `Server` and overrides `Init` to avoid constructing a real snapshot filesystem. `TestFuseManager` creates Unix sockets, registers the mock server, and runs table-driven client operations.

## Control Flow
For each case, the test sets mock error fields, creates a `NewManagerClient` which triggers `Init`, then for successful cases calls `Mount`, `Check`, and `Unmount`, asserting the mock filesystem methods were called. Init and mount error cases expect client creation or mount paths to return errors.

## State And Persistence
Uses a temporary directory for Unix sockets and Bolt fusestore path. Mock filesystem state is an in-memory mountpoint map. The test defers `fm.Close`, which removes the fusestore file.

## Dependencies And Integration
Depends on grpc, generated protobufs, service config, the real `NewFuseManager`, and real `Client` code. It validates RPC wiring without real FUSE mounts.

## Risks And Test Signals
Signals include successful gRPC init/mount/check/unmount flow and error propagation. Gaps include real `Server.Init`, Bolt restore behavior, process startup, signal shutdown, actual mountinfo checks, and real snapshot filesystem interaction.
<!-- END_FILE_RESEARCH: sources/cloud-native/stargz-snapshotter/fusemanager/fusemanager_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/stargz-snapshotter/fusemanager/fusestore.go -->
# sources/cloud-native/stargz-snapshotter/fusemanager/fusestore.go

## Purpose
Persists fuse mount information in BoltDB so the fuse manager can restore mount tracking after reinitialization.

## Important APIs, Types, And Functions
`fuseInfo` stores root, mountpoint, labels, and service config. `storeFuseInfo` creates or opens `fuse-info-bucket` and stores JSON by mountpoint. `removeFuseInfo` deletes a mountpoint key. `restoreFuseInfo` scans the bucket and remounts each stored entry through `fm.mount`.

## Control Flow
Mount stores an entry after `fm.mount` succeeds. Unmount deletes the entry after filesystem unmount succeeds. `Init` calls `restoreFuseInfo`, which reads all stored JSON values and remounts through the current filesystem, skipping already-present mountpoints indirectly through `fm.mount`.

## State And Persistence
Durable state is a BoltDB bucket keyed by mountpoint. Values are JSON-serialized `fuseInfo`. Although root and config are stored, restore currently only uses mountpoint and labels.

## Dependencies And Integration
Depends on bbolt, JSON encoding, `service.Config`, and `Server.mount`. It is opened and closed by `NewFuseManager`/`Close` in `service.go`.

## Risks And Test Signals
Risks include stale entries after failed unmount/store errors being ignored by callers, restore using current config rather than stored config, and loss of store on `Server.Close` because the file is removed. Tests in this subset do not directly assert store/restore behavior.
<!-- END_FILE_RESEARCH: sources/cloud-native/stargz-snapshotter/fusemanager/fusestore.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/stargz-snapshotter/fusemanager/service.go -->
# sources/cloud-native/stargz-snapshotter/fusemanager/service.go

## Purpose
Implements the fuse manager gRPC server. It owns current snapshot filesystem configuration, handles lifecycle/status, delegates mount/check/unmount operations, and manages BoltDB handles for persisted fuse state.

## Important APIs, Types, And Functions
`Config` wraps service config plus IPFS, metadata store, and default image service settings. `ConfigContext`, `ConfigFunc`, and `RegisterConfigFunc` let other packages add service options during `Init`. `dbOpener` deduplicates Bolt handles. `Server` implements protobuf RPCs: `Status`, `Init`, `Mount`, `Check`, `Unmount`, `Close`, and internal `mount`.

## Control Flow
`NewFuseManager` creates the fusestore directory and opens Bolt. `Init` marks status wait-init, unmarshals config, stops any previous CRI server, runs registered config funcs, creates a new filesystem through `service.NewFileSystem`, restores persisted mounts, and marks ready. `Mount`, `Check`, and `Unmount` require ready status under read lock and delegate to the correct filesystem in `fsMap`. `Unmount` treats already-unmounted mountpoints as success if mountinfo confirms absence.

## State And Persistence
In-memory state includes status, root/config, current filesystem, mountpoint-to-filesystem map, CRI server, and shared Bolt opener. Persistent state is the main fusestore BoltDB plus any Bolt DBs opened via config funcs.

## Dependencies And Integration
Depends on generated protobufs, `service.NewFileSystem`, `snapshot.FileSystem`, bbolt, mountinfo, grpc, and containerd logging. It is hosted by `fusemanager.go` and called by `client.go`.

## Risks And Test Signals
Risks include global config func ordering, status set to ready even after deferred cleanup paths if not careful, ignored `storeFuseInfo`/`removeFuseInfo` errors, removing the fusestore on close, and mount restore semantics. `fusemanager_test.go` covers the RPC delegate path with a mock filesystem.
<!-- END_FILE_RESEARCH: sources/cloud-native/stargz-snapshotter/fusemanager/service.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/stargz-snapshotter/ipfs/client/client.go -->
# sources/cloud-native/stargz-snapshotter/ipfs/client/client.go

## Purpose
Implements a small HTTP client for Kubo/IPFS RPC APIs used by the snapshotter's IPFS conversion and resolver paths.

## Important APIs, Types, And Functions
`Client` holds an API base address and HTTP client. `New` constructs it. `FileInfo` mirrors `/api/v0/files/stat` JSON. `StatCID` posts to files/stat, `Get` posts to cat with optional offset and length, `Add` streams multipart form data to add with CID v1 and pin enabled, and `GetIPFSAPIAddress` reads the local IPFS repo `api` file and converts its multiaddr to a URL.

## Control Flow
Each RPC checks that `Address` is set, defaults nil HTTP client, builds a POST request with query parameters, executes it, drains/closes the body on error, validates 2xx status, and decodes or returns the body. `Add` uses `io.Pipe` and a multipart writer goroutine so content streams without prebuffering.

## State And Persistence
Client state is only address and HTTP client. IPFS persistence occurs externally in the IPFS daemon: `Add` pins uploaded data. `GetIPFSAPIAddress` reads `~/.ipfs/api` or a specified repository path.

## Dependencies And Integration
Depends on standard HTTP/multipart/JSON packages, homedir expansion, multiaddr parsing, and multiaddr/net dial args. Used by `ipfs/converter.go` and `ipfs/resolver.go`.

## Risks And Test Signals
Risks include no explicit request contexts, body ownership differences between success and error paths, blocking pipe writes if request construction fails late, and assuming HTTP scheme. `client_test.go` provides optional live IPFS coverage for add/stat/ranged cat.
<!-- END_FILE_RESEARCH: sources/cloud-native/stargz-snapshotter/ipfs/client/client.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/stargz-snapshotter/ipfs/client/client_test.go -->
# sources/cloud-native/stargz-snapshotter/ipfs/client/client_test.go

## Purpose
Provides an integration test for the IPFS client against a real IPFS API endpoint.

## Important APIs, Types, And Functions
The package-level `ipfsAPI` flag selects the API address. `TestIPFSClient` adds sample data and verifies full and ranged reads. `checkData` calls `StatCID` and `Get`, reads the returned body, and compares size/content.

## Control Flow
If `-ipfs-api` is absent, the test logs and skips. Otherwise it creates a client, adds `"hello world 0123456789"`, checks the whole content, and checks bytes 10 through 13 through `offset` and `length` query parameters.

## State And Persistence
State is external to the test process: `Add` pins data in the configured IPFS node. Test-local state is the CID returned by the node.

## Dependencies And Integration
Depends on a running IPFS daemon and is intended for `make test-ipfs`. It exercises real HTTP Kubo APIs through `client.go`.

## Risks And Test Signals
Passing signals confirm add/stat/cat compatibility with the configured IPFS daemon and ranged reads. It is skipped by default, so normal unit runs do not catch IPFS API regressions. It also leaves pinned data unless the daemon/test harness cleans it up.
<!-- END_FILE_RESEARCH: sources/cloud-native/stargz-snapshotter/ipfs/client/client_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/stargz-snapshotter/ipfs/converter.go -->
# sources/cloud-native/stargz-snapshotter/ipfs/converter.go

## Purpose
Converts and pushes a containerd image into an IPFS-addressed form. Converted blobs and the root descriptor are added to IPFS, and blob descriptors receive `ipfs://` URLs.

## Important APIs, Types, And Functions
`Push` calls `PushWithIPFSPath` with default IPFS path behavior. `PushWithIPFSPath` creates a containerd lease, finds the image, resolves IPFS API address, runs a converter with `pushBlobHook`, marshals the converted root descriptor, and adds it to IPFS. `pushBlobHook` uploads descriptor content and sets `URLs`. `GetCID` extracts the first `ipfs://` URL from a descriptor.

## Control Flow
The conversion uses `converter.IndexConvertFuncWithHook`, passing the layer conversion function and a post-convert hook. For each descriptor, the hook chooses the new descriptor if present or copies the original, reads content from containerd, uploads it to IPFS, and annotates the descriptor with the CID URL. The root descriptor JSON is also uploaded, and its CID is returned.

## State And Persistence
Containerd lease state protects content during conversion. IPFS daemon state persists uploaded/pinned blobs. Descriptor URL state records content addressing as `ipfs://<cid>`.

## Dependencies And Integration
Depends on containerd client, content store, image converter package, platforms matcher, local IPFS client, OCI descriptors, and environment/configured `IPFS_PATH`.

## Risks And Test Signals
Risks include uploading large blobs serially through HTTP, relying on IPFS path discovery, and descriptor URL replacement with a single IPFS URL. No direct tests are in this subset; live behavior depends on IPFS client tests and integration conversion tests elsewhere.
<!-- END_FILE_RESEARCH: sources/cloud-native/stargz-snapshotter/ipfs/converter.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/stargz-snapshotter/ipfs/resolver.go -->
# sources/cloud-native/stargz-snapshotter/ipfs/resolver.go

## Purpose
Implements a containerd `remotes.Resolver` for immutable IPFS/IPNS references whose root object is a JSON-encoded OCI descriptor containing IPFS URLs.

## Important APIs, Types, And Functions
`ResolverOptions` selects `Scheme` (`ipfs` or `ipns`) and optional `IPFSPath`. `NewResolver` resolves the local IPFS API URL and returns a resolver. `Resolve` fetches and decodes the root descriptor. `Fetcher` returns a fetcher whose `Fetch` downloads descriptor content by CID. `Pusher` returns an immutable-remote error.

## Control Flow
`NewResolver` validates the scheme, chooses `IPFS_PATH` or explicit option, and creates an IPFS client. `Resolve` calls `/api/v0/cat` for `/<scheme>/<ref>`, decodes an OCI descriptor, and requires at least one `ipfs://` URL. `Fetch` extracts the CID from the requested descriptor and cats `/<scheme>/<cid>`.

## State And Persistence
Resolver state is just scheme and IPFS client. Content persistence is external in IPFS. The resolver does not cache descriptors or fetched blobs.

## Dependencies And Integration
Depends on containerd remotes interfaces, local IPFS client, OCI descriptors, JSON decoding, and `GetCID` from `converter.go`. It lets containerd pull image content from IPFS-addressed descriptors.

## Risks And Test Signals
Risks include unsupported schemes, lack of push support, assuming the root ref is a CID/path compatible with containerd reference constraints, and no context-aware IPFS client calls. Tests are not in this subset; signals come from IPFS live client tests and resolver integration elsewhere.
<!-- END_FILE_RESEARCH: sources/cloud-native/stargz-snapshotter/ipfs/resolver.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/stargz-snapshotter/metadata/memory/reader.go -->
# sources/cloud-native/stargz-snapshotter/metadata/memory/reader.go

## Purpose
Provides an in-memory `metadata.Reader` implementation over an `estargz.Reader`. It maps eStargz TOC entries to stable numeric IDs and exposes metadata/file access through the common metadata interface.

## Important APIs, Types, And Functions
`NewReader` opens an eStargz section reader with metadata options. `assignIDs` builds `idMap` and `idOfEntry`. Methods implement `RootID`, `TOCDigest`, `GetOffset`, `GetAttr`, `GetChild`, `ForeachChild`, `OpenFile`, `OpenFileWithPreReader`, `Clone`, `Close`, and test helper `NumOfNodes`. `attrFromTOCEntry` converts TOC metadata to `metadata.Attr`.

## Control Flow
New reader options translate telemetry and decompressors into estargz open options. The root TOC entry is looked up by empty name, then entries are recursively assigned IDs, rejecting unresolved hardlink entries. File open calls use the eStargz reader and wrap section readers. `OpenFileWithPreReader` converts preread callbacks from TOC entries to numeric IDs.

## State And Persistence
All metadata is in memory: the estargz reader, root ID, ID maps, and open options. `Clone` opens a new estargz reader over a new section reader while sharing the same ID maps, preserving ID stability. `Close` is a no-op.

## Dependencies And Integration
Depends on `estargz`, the common `metadata` interfaces/options, OpenContainers digest, and filesystem modes. Used by reader tests and as the default lightweight metadata backend.

## Risks And Test Signals
Risks include memory scaling with TOC size, shared ID maps assuming cloned content has identical TOC entries, no cleanup in `Close`, and path/name identity for hardlinks. `metadata/memory/reader_test.go` runs the shared metadata suite across many file types and compression formats.
<!-- END_FILE_RESEARCH: sources/cloud-native/stargz-snapshotter/metadata/memory/reader.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/stargz-snapshotter/metadata/memory/reader_test.go -->
# sources/cloud-native/stargz-snapshotter/metadata/memory/reader_test.go

## Purpose
Adapts the shared metadata reader test suite to the in-memory metadata implementation.

## Important APIs, Types, And Functions
`TestReader` constructs a `testutil.TestRunner` and calls `testutil.TestReader(testRunner, readerFactory)`. `readerFactory` wraps `NewReader` and type-asserts to `*reader` so the suite can access `NumOfNodes`.

## Control Flow
The runner maps suite subtests onto `testing.T.Run`. Each fixture in the shared suite is built as eStargz and opened with `memory.NewReader`, then validated.

## State And Persistence
No persistent state. Test state consists of in-memory eStargz section readers and metadata maps.

## Dependencies And Integration
Depends on `metadata/testutil`, the common `metadata.Option` type, and the local memory reader. It verifies that the default metadata backend satisfies both production and test-only interfaces.

## Risks And Test Signals
Passing this test signals correct metadata traversal, attributes, file reads, preread callbacks, telemetry calls, and clone ID stability for memory metadata. It does not cover persistent database-backed metadata behavior.
<!-- END_FILE_RESEARCH: sources/cloud-native/stargz-snapshotter/metadata/memory/reader_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/stargz-snapshotter/metadata/metadata.go -->
# sources/cloud-native/stargz-snapshotter/metadata/metadata.go

## Purpose
Defines the common metadata abstraction used by stargz snapshotter readers, independent of a concrete memory or database-backed implementation.

## Important APIs, Types, And Functions
`Attr` represents file metadata including size, mode, ownership, device numbers, xattrs, symlink target, and link count. `Store` constructs a `Reader`. `Reader` exposes ID-based tree traversal, offsets, TOC digest, file opening, preread opening, clone, and close. `File` combines chunk lookup with `ReadAt`. `Decompressor` extends `estargz.Decompressor` with `DecompressTOC`. Options include `WithTOCOffset`, `WithTelemetry`, and `WithDecompressors`.

## Control Flow
This file is interface and option plumbing. Implementations consume options, expose stable IDs, and provide chunk entries for reader cache logic. Telemetry hooks allow implementations to report footer, TOC fetch, and TOC deserialization latency.

## State And Persistence
No state is stored in this file. It defines what state implementations expose and how callers configure them.

## Dependencies And Integration
Depends on `estargz`, standard IO/filesystem/time types, and OpenContainers digest. It is the contract between metadata backends, `fs/reader`, and tests.

## Risks And Test Signals
Risks include interface changes affecting all metadata implementations and ambiguous ID stability requirements without documentation in the interface. Shared tests in `metadata/testutil` validate important contract behavior against implementations.
<!-- END_FILE_RESEARCH: sources/cloud-native/stargz-snapshotter/metadata/metadata.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/stargz-snapshotter/metadata/testutil/testutil.go -->
# sources/cloud-native/stargz-snapshotter/metadata/testutil/testutil.go

## Purpose
Provides a comprehensive reusable test suite for `metadata.Reader` implementations.

## Important APIs, Types, And Functions
`ReaderFactory`, `TestableReader`, `TestingT`, `Runner`, and `TestRunner` abstract over test frameworks and metadata backends. `TestReader` builds fixture archives and runs check functions including `numOfNodes`, `hasFile`, `hasDirChildren`, `sameNodes`, `linkName`, `hasNumLink`, device checks, xattr/owner/mode/modtime checks, chunk checks, and preread checks.

## Control Flow
The suite iterates over path prefixes, compression formats, chunk sizes, and file layouts. It builds eStargz archives, opens readers with telemetry and decompressor options, dumps node trees for diagnostics, applies all expected checks, verifies telemetry hooks were called, then clones a second reader and repeats checks. A final clone-ID-stability test compares path-to-ID maps.

## State And Persistence
All fixture data is generated in memory. Test state includes telemetry call booleans, random 64KB payloads, and reader-specific metadata maps. No durable state is written by the suite.

## Dependencies And Integration
Depends on eStargz building utilities, gzip/zstd/external TOC compression factories, the common metadata interfaces, and digest calculations. Memory and other metadata backends reuse this suite to prove contract compliance.

## Risks And Test Signals
Signals cover empty archives, regular files, directories, hardlinks, symlinks, device nodes, FIFOs, normalized paths, chunks, preread of neighboring files, telemetry, and clone stability. Risks include assumptions about generated eStargz layout and test runtime from the compression/prefix matrix.
<!-- END_FILE_RESEARCH: sources/cloud-native/stargz-snapshotter/metadata/testutil/testutil.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/stargz-snapshotter/nativeconverter/estargz/estargz.go -->
# sources/cloud-native/stargz-snapshotter/nativeconverter/estargz/estargz.go

## Purpose
Provides containerd image converter functions that rewrite layer blobs into eStargz format and annotate descriptors with TOC and uncompressed-size metadata.

## Important APIs, Types, And Functions
`LayerConvertWithLayerAndCommonOptsFunc` supports common eStargz options plus per-layer options keyed by digest. `LayerConvertFunc` returns a `converter.ConvertFunc` that converts layer descriptors, writes converted content to the content store, updates diffID labels, digest, size, media type, TOC digest annotation, and uncompressed-size annotation.

## Control Flow
Non-layer descriptors return nil, meaning no conversion. Layer conversion reads the source blob from content store, builds an eStargz blob with context, opens a content writer with deterministic ref, truncates stale writer state, copies converted bytes, commits with labels unless already exists, adjusts media type if source was uncompressed, and returns an updated descriptor.

## State And Persistence
Converted blobs are persisted in the containerd content store. Labels preserve/update uncompressed digest information. Descriptor annotations carry eStargz TOC digest and uncompressed size. Common options are copied defensively to avoid data races.

## Dependencies And Integration
Depends on containerd content store and converter APIs, image media type helpers, uncompress media helpers, labels, errdefs, local `estargz` builder, and OCI descriptors. Intended to be composed with Docker-to-OCI conversion so annotations are retained.

## Risks And Test Signals
Risks include interrupted writers requiring truncation, already-existing content handling, media type annotation loss for Docker formats without OCI conversion, and per-digest option ambiguity when duplicate layers share a digest. `estargz_test.go` verifies conversion creates at least one layer with a TOC annotation.
<!-- END_FILE_RESEARCH: sources/cloud-native/stargz-snapshotter/nativeconverter/estargz/estargz.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/stargz-snapshotter/nativeconverter/estargz/estargz_test.go -->
# sources/cloud-native/stargz-snapshotter/nativeconverter/estargz/estargz_test.go

## Purpose
Tests the native eStargz layer converter as a pure unit test without requiring a daemon.

## Important APIs, Types, And Functions
`TestLayerConvertFunc` uses `testutil.EnsureHello` to create sample content, `LayerConvertFunc` with prioritized file option, `converter.DefaultIndexConvertFunc`, and `images.Walk` to inspect converted descriptors.

## Control Flow
The test builds or locates a sample hello image in a content store, converts the image with Docker-to-OCI enabled and default platform matching, walks the converted descriptor graph, collects any `estargz.TOCJSONDigestAnnotation`, and fails if no converted eStargz layer was found.

## State And Persistence
State is limited to the test content store returned by `EnsureHello`. Converted blobs and descriptors live in that store for the duration of the test.

## Dependencies And Integration
Depends on containerd image walking/converter APIs, platforms matcher, local eStargz converter, local eStargz annotations, and test utility content fixtures.

## Risks And Test Signals
Passing confirms the converter can process a real sample layer and emit TOC annotations through an index conversion. It does not verify byte-for-byte layer contents, lazy-read performance, all media type variants, or uncompressed-size annotation correctness.
<!-- END_FILE_RESEARCH: sources/cloud-native/stargz-snapshotter/nativeconverter/estargz/estargz_test.go -->
