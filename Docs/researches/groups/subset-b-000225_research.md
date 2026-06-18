# subset-b-000225 research

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/nydus/contrib/nydusify/pkg/snapshotter/external/backend/walker.go -->
# sources/cloud-native/nydus/contrib/nydusify/pkg/snapshotter/external/backend/walker.go

## Purpose

This file implements the local filesystem walker used by nydusify's external snapshotter metadata path. It scans a root directory, asks a backend handler to describe each regular file as external chunks, and aggregates chunk metadata, file attributes, and backend configuration into a `backend.Result`.

## Important APIs, Types, and Functions

`Walker` is a stateless facade constructed by `NewWalker`. `bfsWalk` recursively walks directories by first handling regular files in the current directory and then descending into child directories. `(*Walker).Walk` accepts a `context.Context`, root path, and `Handler`; it builds a delayed list of per-file closures, invokes `handler.Handle` with `File{RelativePath, Size}`, and finally calls `handler.Backend`.

## Control Flow

The walk starts with `os.Lstat`, ignores a root that is itself a non-directory, and processes only entries whose `DirEntry.Type().IsRegular()` returns true. For every handled source file, returned chunks are appended to the result. File attributes are emitted once per consecutive chunk file path by comparing each chunk's `FilePath()` with the last seen path.

## State and Persistence Behavior

The walker does not write persistent state. It accumulates slices in memory and returns them to the caller. Relative paths are derived with `filepath.Rel(root, path)`, so output paths depend on the supplied root and host path separator behavior.

## Dependencies and Integration Points

It integrates with the external backend interfaces in the same package: `Handler`, `File`, `Chunk`, `FileAttribute`, `Backend`, and `Result`. It is called by `external.Handle` before metadata generation and backend/attributes file emission.

## Risks and Test Signals

The function skips symlinks, special files, and regular files whose type is not reported in `DirEntry.Type`, and it groups file attributes only for consecutive chunks with the same `FilePath`, not globally. Handler work is deliberately postponed until after walking, so file changes between walk and handle can make sizes stale. Tests cover invalid paths, empty directories, traversal order, handler/backend errors, and attribute aggregation.
<!-- END_FILE_RESEARCH: sources/cloud-native/nydus/contrib/nydusify/pkg/snapshotter/external/backend/walker.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/nydus/contrib/nydusify/pkg/snapshotter/external/backend/walker_test.go -->
# sources/cloud-native/nydus/contrib/nydusify/pkg/snapshotter/external/backend/walker_test.go

## Purpose

This test file validates the external backend walker and supplies local mocks for `Chunk` and `Handler` so walker behavior can be tested without a real backend implementation.

## Important APIs, Types, and Functions

`setupTestDir` creates a nested directory tree. `MockChunk` implements all chunk metadata accessors used by the walker. `MockHandler` implements `Backend` and `Handle`. The tests exercise `bfsWalk`, `NewWalker`, normal `Walk`, error paths, and file-attribute aggregation.

## Control Flow

`TestBfsWalk` checks missing roots, an empty directory, a single nested directory, and a directory with files and subdirectories. `TestWalkErrors` injects handler, backend, and missing-root failures. `TestWalkAggregatesChunksByFile` returns multiple chunks for one logical file and one chunk for another, then checks `Result.Chunks`, `Result.Files`, and backend version propagation.

## State and Persistence Behavior

Tests create temporary directories and files under the OS temp directory or `t.TempDir`, then remove them. No repository state is mutated.

## Dependencies and Integration Points

The tests depend on `testify/assert` and `testify/require`. They mirror the `Handler` and `Chunk` contracts expected by `walker.go`, making them direct integration signals for external snapshotter metadata assembly.

## Risks and Test Signals

Coverage confirms the current traversal behavior and wrapped error labels. It does not cover symlinks, file type bits with `TypeUnknown`, cancellation propagation through context, or non-consecutive chunks for the same file path, which remain important behavioral risks for real backends.
<!-- END_FILE_RESEARCH: sources/cloud-native/nydus/contrib/nydusify/pkg/snapshotter/external/backend/walker_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/nydus/contrib/nydusify/pkg/snapshotter/external/external.go -->
# sources/cloud-native/nydus/contrib/nydusify/pkg/snapshotter/external/external.go

## Purpose

This file is the high-level entry point for generating external snapshotter metadata artifacts. It turns either local walked files or remote modctl-provided attributes into metadata, backend JSON, attribute text, and placeholder files for build context integration.

## Important APIs, Types, and Functions

`Options` carries the local directory, context directory, handler implementations, and output paths. `Handle` runs `backend.NewWalker().Walk`, constructs `Generators`, writes meta bytes, backend JSON, and attributes. `buildAttr` formats file attributes for local external files. `RemoteHandle` obtains backend and file attributes from `RemoteHandler`, writes backend and attributes, then calls `buildEmptyFiles`. `buildEmptyFiles` creates empty placeholder files with recorded modes.

## Control Flow

Local handling is a pipeline: walk source files, convert chunks to on-disk metadata, build attribute lines, and write all outputs. Remote handling bypasses metadata generation, formats richer attribute lines including file size and CRCs, writes backend configuration, and materializes empty files in the context directory.

## State and Persistence Behavior

The file writes `MetaOutput`, `BackendOutput`, `AttributesOutput`, and remote-mode placeholder files. Writes use fixed mode `0644` for outputs and the backend-provided file mode for placeholders. Existing files are overwritten.

## Dependencies and Integration Points

It integrates with `backend.Walker`, `backend.Handler`, `backend.RemoteHanlder`, `NewGenerators`, JSON serialization, and logrus debug logging. The generated attribute format is consumed by external snapshotter/image build flows.

## Risks and Test Signals

Risks include path traversal or absolute paths in remote `RelativePath` values because `buildEmptyFiles` joins with `fmt.Sprintf`, empty attribute files when no chunks are returned, and inconsistent local/remote attribute field sets. Tests cover happy paths and placeholder modes but not malicious relative paths or output write failures.
<!-- END_FILE_RESEARCH: sources/cloud-native/nydus/contrib/nydusify/pkg/snapshotter/external/external.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/nydus/contrib/nydusify/pkg/snapshotter/external/external_test.go -->
# sources/cloud-native/nydus/contrib/nydusify/pkg/snapshotter/external/external_test.go

## Purpose

This test file verifies local and remote external snapshotter handling at the file-output level using mock backend handlers.

## Important APIs, Types, and Functions

`mockHandler` implements local `backend.Handler`. `mockRemoteHandler` implements the remote handler interface. `TestHandle`, `TestRemoteHandle`, `TestBuildEmptyFiles`, and `TestBuildAttr` validate artifact creation and attribute helper behavior.

## Control Flow

The local test creates temp output paths and a handler returning a mock backend with no chunks, then checks that all three output files exist. The remote test returns one `FileAttribute`, runs `RemoteHandle`, and checks backend, attribute, and context placeholder files. `TestBuildEmptyFiles` verifies directory creation and file modes.

## State and Persistence Behavior

All outputs are under temporary directories. The tests intentionally assert creation side effects rather than parsing content in detail.

## Dependencies and Integration Points

The tests depend on `backend.FileAttribute`, `backend.Backend`, and `testify/assert`. They show that `RemoteHandle` is expected to materialize empty context files in addition to backend and attribute metadata.

## Risks and Test Signals

The tests prove output creation for basic cases, but they do not assert exact attribute text, JSON contents, metadata binary shape, or error paths for failed writes and invalid remote paths. That leaves formatting regressions and path-safety issues as residual risks.
<!-- END_FILE_RESEARCH: sources/cloud-native/nydus/contrib/nydusify/pkg/snapshotter/external/external_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/nydus/contrib/nydusify/pkg/snapshotter/external/generator.go -->
# sources/cloud-native/nydus/contrib/nydusify/pkg/snapshotter/external/generator.go

## Purpose

This file converts backend chunk descriptions into the binary external metadata format consumed by nydusd/external snapshotter logic. It also carries through backend configuration and file attributes into a generated `Result`.

## Important APIs, Types, and Functions

`Result` contains generated `Meta`, `Backend`, and `Files`. `MetaGenerator` embeds header, chunk meta, object meta, and slices of chunk/object records. `NewGenerators` deduplicates object metadata by chunk object ID and msgpack-encodes object content. `(*Generators).Generate` wraps `MetaGenerator.Generate`. `(*MetaGenerator).Generate` lays out header, chunk table, object meta, object-offset table, and encoded object bodies.

## Control Flow

`NewGenerators` iterates chunks in input order. Each new `ObjectID` gets an object index and msgpack payload; every chunk receives a `ChunkOndisk` pointing at that object index and its object offset. Binary generation computes offsets using `unsafe.Sizeof`, detects fixed object entry sizes, and writes all structs with little-endian encoding.

## State and Persistence Behavior

No files are written here. The generated metadata byte slice is deterministic for a fixed chunk order and msgpack encoding. The generator mutates its embedded header/meta/offset fields as part of `Generate`.

## Dependencies and Integration Points

It depends on the external backend on-disk structs and constants, `encoding/binary`, `unsafe`, and `vmihailenco/msgpack/v5`. It is called by `external.Handle` before writing `MetaOutput`.

## Risks and Test Signals

Binary layout depends on Go struct layout and `unsafe.Sizeof`; any struct definition change can break compatibility. Object deduplication is by object ID only, so conflicting contents under the same ID are silently collapsed. Tests cover normal and empty generation but do not decode or version-verify the binary stream.
<!-- END_FILE_RESEARCH: sources/cloud-native/nydus/contrib/nydusify/pkg/snapshotter/external/generator.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/nydus/contrib/nydusify/pkg/snapshotter/external/generator_test.go -->
# sources/cloud-native/nydus/contrib/nydusify/pkg/snapshotter/external/generator_test.go

## Purpose

This test file validates construction and byte generation for external metadata generators with mocked chunks.

## Important APIs, Types, and Functions

`MockChunk` uses `testify/mock` to implement the `backend.Chunk` interface. `TestNewGenerators` checks object/chunk counts and backend passthrough for normal and empty input. `TestGenerate` checks wrapper generation. `TestMetaGeneratorGenerate` checks non-empty byte output for populated and empty metadata.

## Control Flow

Tests create synthetic chunk and object content, call constructors or generators, and assert structural counts and selected fields. The generation tests do not parse the byte stream; they only assert success and non-zero length.

## State and Persistence Behavior

There is no filesystem or global state. All state is in-memory generator objects and mock call expectations.

## Dependencies and Integration Points

The tests depend on `backend.Result`, `backend.ChunkOndisk`, `backend.ObjectOndisk`, `testify/assert`, and `testify/mock`. They signal that empty metadata is considered valid and still has header/meta bytes.

## Risks and Test Signals

Coverage confirms basic construction but not byte-level ABI correctness, little-endian field values, object offset calculation, msgpack failure handling, or duplicate object ID semantics. ABI regression tests would be valuable for this file.
<!-- END_FILE_RESEARCH: sources/cloud-native/nydus/contrib/nydusify/pkg/snapshotter/external/generator_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/nydus/contrib/nydusify/pkg/utils/archive.go -->
# sources/cloud-native/nydus/contrib/nydusify/pkg/utils/archive.go

## Purpose

This utility file provides tar/tar.gz packing and unpacking helpers used by nydusify for layer, bootstrap, and file extraction workflows.

## Important APIs, Types, and Functions

`PackTargz` streams a single source file into a tar or tar.gz archive under a requested name. `PackTargzInfo` computes the digest and size of that generated stream. `UnpackTargz` decompresses an archive stream and applies it into a destination directory with optional overlay whiteout conversion.

## Control Flow

`PackTargz` returns an `io.PipeReader` immediately and writes archive data in a goroutine, closing the pipe with the first encountered error. `PackTargzInfo` tees the generated stream through a pipe so digest calculation and size counting proceed concurrently. `UnpackTargz` uses containerd compression detection, temporarily sets umask to zero, creates the destination, and calls `archive.Apply`.

## State and Persistence Behavior

Packing only reads the source file and streams bytes. Unpacking writes files under `dst` and temporarily mutates process umask, restoring it with `defer`. Overlay mode controls whether whiteouts are converted or skipped.

## Dependencies and Integration Points

It depends on Go tar/gzip, containerd archive/compression, OCI digest, and `unix.Umask`. `viewer` and other nydusify utilities use neighboring unpack helpers for bootstrap extraction.

## Risks and Test Signals

`PackTargz` uses `0666` archive mode and a directory header from `filepath.Dir(name)`, which can produce `"."` entries. `PackTargzInfo` uses unbuffered channels that assume the digest reader drains correctly. `UnpackTargz` delegates path handling to containerd archive logic. Tests cover deterministic digest/size, compressed/uncompressed streams, invalid streams, and unpacked content.
<!-- END_FILE_RESEARCH: sources/cloud-native/nydus/contrib/nydusify/pkg/utils/archive.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/nydus/contrib/nydusify/pkg/utils/archive_test.go -->
# sources/cloud-native/nydus/contrib/nydusify/pkg/utils/archive_test.go

## Purpose

This test file verifies tar/tar.gz packing and unpacking helpers, including security-sensitive path traversal behavior in the plain tar helper from `utils.go`.

## Important APIs, Types, and Functions

Tests cover `PackTargzInfo`, `UnpackTargz`, `UnpackFromTar`, path traversal rejection, parent directory creation, root directory entries, invalid streams, and compressed/uncompressed `PackTargz`.

## Control Flow

The tests build in-memory tar or gzip streams with `archive/tar` and `compress/gzip`, call the utility under test, then inspect created files and content. `TestPackTargzWithoutCompression` and `TestPackTargzCompressedStream` read the generated archive entries back to verify names and content.

## State and Persistence Behavior

All filesystem writes are under temporary directories, except temporary files created by `os.CreateTemp`. Traversal tests assert that escaped files are not created outside the target directory.

## Dependencies and Integration Points

The tests depend on Go archive primitives and `testify`. They validate both `archive.go` and the plain tar extraction helper in `utils.go`.

## Risks and Test Signals

The strongest signal is coverage for `../` traversal rejection in `UnpackFromTar`. The fixed digest in `TestPackTargzInfo` can be sensitive to gzip/tar metadata changes, and tests do not cover overlay whiteout conversion or umask restoration under error.
<!-- END_FILE_RESEARCH: sources/cloud-native/nydus/contrib/nydusify/pkg/utils/archive_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/nydus/contrib/nydusify/pkg/utils/backend.go -->
# sources/cloud-native/nydus/contrib/nydusify/pkg/utils/backend.go

## Purpose

This file builds and rewrites registry backend configuration used when nydusify and nydusd access external image blobs through registries and optional proxies.

## Important APIs, Types, and Functions

`RegistryBackendConfig` models registry scheme, host, repository path, auth, skip-verify, and proxy settings. `BackendProxyConfig` models proxy URL, cache directory, fallback, ping URL, and timeouts. `NewRegistryBackendConfig` derives a runtime config from a parsed image reference and Docker credential store. `BuildRuntimeExternalBackendConfig` injects runtime registry/proxy settings into an existing external backend JSON file.

## Control Flow

`NewRegistryBackendConfig` chooses `HTTP_PROXY`, falling back to `HTTPS_PROXY`, fills host/repo from `distribution/reference`, and loads Docker auth for the host. `BuildRuntimeExternalBackendConfig` reads an external backend file, unmarshals caller-provided registry JSON, applies environment overrides for proxy URL/cache dir, replaces `Backends[0].Config`, marshals, and overwrites the same file.

## State and Persistence Behavior

The first function only reads Docker config and environment. The second rewrites `externalBackendConfigPath` in place. It assumes at least one backend entry exists in the external backend JSON.

## Dependencies and Integration Points

It integrates with Docker CLI config loading, image references, and `snapshotter/external/backend.Backend`. `viewer.handleExternalBackendConfig` calls the rewrite path for model artifacts with external backend configs.

## Risks and Test Signals

Risks include panic on empty `Backends`, loss of existing backend config fields, proxy fallback always forced true during rewrite, and auth only populated when username/password fields are present. Tests cover proxy env selection, Docker auth, missing files, and normal rewrite but not empty backend arrays or invalid JSON variants.
<!-- END_FILE_RESEARCH: sources/cloud-native/nydus/contrib/nydusify/pkg/utils/backend.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/nydus/contrib/nydusify/pkg/utils/backend_test.go -->
# sources/cloud-native/nydus/contrib/nydusify/pkg/utils/backend_test.go

## Purpose

This test file verifies registry backend config derivation and runtime external backend config rewriting.

## Important APIs, Types, and Functions

`TestNewRegistryBackendConfig` checks host/repo extraction, proxy selection, skip-verify, and Docker auth encoding. `TestNewRegistryBackendConfigUsesHTTPSProxyFallback` covers HTTPS proxy fallback. `TestBuildExternalBackend` covers missing external config and normal rewrite.

## Control Flow

The tests set environment variables, create temporary Docker config directories, parse image references, call the utility functions, and inspect returned structs or rewritten JSON.

## State and Persistence Behavior

Tests write temporary Docker `config.json` and temporary external backend files. The rewrite test reads the modified file back into `backend.Backend`.

## Dependencies and Integration Points

The tests use `distribution/reference`, Docker auth format, `backend.Backend`, and `testify`. They demonstrate that the utility is intended to interoperate with standard Docker credential files.

## Risks and Test Signals

The tests validate the common path but leave malformed backend config, empty backend lists, environment override precedence, and preservation of existing backend fields uncovered.
<!-- END_FILE_RESEARCH: sources/cloud-native/nydus/contrib/nydusify/pkg/utils/backend_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/nydus/contrib/nydusify/pkg/utils/constant.go -->
# sources/cloud-native/nydus/contrib/nydusify/pkg/utils/constant.go

## Purpose

This file centralizes nydusify media types, layer filenames, manifest features, and OCI annotation keys shared across image conversion, parsing, snapshotter, and viewer code.

## Important APIs, Types, and Functions

It defines constants for the Nydus image manifest media type, Nydus OS feature marker, blob media type, bootstrap/backend filenames in layers, cache label, blob/bootstrap/source-chain/artifact annotations, uncompressed digest annotation, commit-blob and prefetch annotations.

## Control Flow

There is no executable control flow. The constants are imported by helpers such as platform matching, filesystem version detection, bootstrap extraction, and manifest construction.

## State and Persistence Behavior

The file itself has no state. Its values become persisted in OCI manifests, descriptors, layer annotations, and archive paths, making them part of the compatibility surface.

## Dependencies and Integration Points

Constants are consumed by `utils.GetNydusFsVersionOrDefault`, `viewer.PullBootstrap`, parser/generator code, and external snapshotter workflows. They align nydusify with containerd snapshot annotations and Nydus runtime expectations.

## Risks and Test Signals

Typos or value changes would break image recognition, bootstrap lookup, or snapshotter behavior across components. Adjacent tests cover some constants indirectly through platform and fs-version helpers, but the constants file has no direct exhaustive test.
<!-- END_FILE_RESEARCH: sources/cloud-native/nydus/contrib/nydusify/pkg/utils/constant.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/nydus/contrib/nydusify/pkg/utils/utils.go -->
# sources/cloud-native/nydus/contrib/nydusify/pkg/utils/utils.go

## Purpose

This file provides general nydusify utility functions for platform detection, retry policy, descriptor marshaling, archive extraction, path checks, and Blake3 file hashing.

## Important APIs, Types, and Functions

It defines supported OS/architecture constants, `FsVersion` (`V5`, `V6`), `GetNydusFsVersionOrDefault`, `WithRetry`, `RetryWithAttempts`, `RetryWithHTTP`, `MarshalToDesc`, `IsNydusPlatform`, `IsSupportedArch`, `MatchNydusPlatform`, `UnpackFile`, `UnpackFromTar`, `unpackTarPath`, `IsEmptyString`, `IsPathExists`, and `HashFile`.

## Control Flow

Retry helpers loop until success, non-retryable error, cancellation, or exhausted attempts. Platform helpers inspect OCI platform fields and `OSFeatures`. Archive helpers decompress streams, iterate tar entries, copy matching content, and sanitize tar paths before writing. `HashFile` streams 64 KiB chunks into a Blake3 hasher.

## State and Persistence Behavior

`UnpackFile` and `UnpackFromTar` write target files/directories. Other helpers are stateless except for sleeping in retries and reading files/environmental behavior through dependencies.

## Dependencies and Integration Points

The file integrates with containerd compression, Harbor acceleration retry classification, OCI image specs, OpenContainers digest, logrus, syscall errors, and Blake3. It is used by parser, viewer, image conversion, and tests.

## Risks and Test Signals

`UnpackFile` creates the target without parent directory creation and ignores non-EOF tar errors in the loop until the next iteration. `WithRetry` sleeps before retrying after the first failure and retries 401 as an HTTP retryable condition. `UnpackFromTar` has explicit traversal protection. Tests cover platform helpers, retries, descriptor digest, file extraction, hashing, and traversal rejection.
<!-- END_FILE_RESEARCH: sources/cloud-native/nydus/contrib/nydusify/pkg/utils/utils.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/nydus/contrib/nydusify/pkg/utils/utils_test.go -->
# sources/cloud-native/nydus/contrib/nydusify/pkg/utils/utils_test.go

## Purpose

This test file validates general utility behavior across platform matching, archive extraction, retry classification, descriptor marshaling, filesystem-version annotations, retry loops, and hashing.

## Important APIs, Types, and Functions

Helpers `makePlatform`, `makeDesc`, `createArchive`, `addToArchive`, and `writerToSlice` support tests for `IsSupportedArch`, `IsNydusPlatform`, `MatchNydusPlatform`, `UnpackFile`, `HashFile`, `MarshalToDesc`, `WithRetry`, `RetryWithHTTP`, `GetNydusFsVersionOrDefault`, `RetryWithAttempts`, and `UnpackFileNotFound`.

## Control Flow

Tests construct OCI platform descriptors, in-memory or on-disk tar.gz archives, temporary files, and controlled retry closures. Assertions check boolean classification, expected digest values, error propagation, and cancellation behavior.

## State and Persistence Behavior

Some tests create files in the current working directory (`example.txt`, `output.tar.gz`, `output.txt`, `test`) and remove them with defers; others use temp files. The retry test performs an HTTP GET to localhost:5000 and expects connection refused.

## Dependencies and Integration Points

The test suite depends on OCI spec types, digest helpers, HTTP/syscall errors, gzip/tar primitives, and `testify/require`. It gives broad regression signals for utility functions used across nydusify.

## Risks and Test Signals

The tests cover many happy and error paths, but the localhost retry test is environment-sensitive if a service happens to listen on port 5000. `UnpackFile` parent-directory behavior and malformed tar loop behavior remain under-tested.
<!-- END_FILE_RESEARCH: sources/cloud-native/nydus/contrib/nydusify/pkg/utils/utils_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/nydus/contrib/nydusify/pkg/utils/worker.go -->
# sources/cloud-native/nydus/contrib/nydusify/pkg/utils/worker.go

## Purpose

This file implements lightweight concurrent worker-pool helpers used by nydusify to run jobs with bounded parallelism and optionally preserve ordered result delivery.

## Important APIs, Types, and Functions

`Job` is a function returning an error. `RJob` adds `Do` and `Err`. `QueueWorkerPool` has an atomic first-error store, a job channel, and per-index result channels. `NewQueueWorkerPool`, `Put`, and `Waiter` manage ordered queued jobs. `Once` is an atomic one-shot helper. `WorkerPool` provides unordered job execution with a single-error channel and waitgroup via `NewWorkerPool`, `Put`, `Err`, and `Waiter`.

## Control Flow

`QueueWorkerPool` starts workers that assign monotonically increasing result indexes under a mutex, receive jobs, run them, send the job to the matching result channel, and stop after an error. `WorkerPool` workers drain a shared queue until closed or until a job fails, with `Once` recording only the first error.

## State and Persistence Behavior

All state is in memory: channels, atomic error value, waitgroup counters, and mutex-protected index allocation. There is no persistence.

## Dependencies and Integration Points

It uses Go `sync` and `sync/atomic`. Other nydusify code can use it for parallel pulls, pushes, checks, or conversion work that needs ordered result observation.

## Risks and Test Signals

`QueueWorkerPool` has subtle ordering semantics: result index is assigned when a worker receives, not when `Put` is called, and workers stop on first job error, potentially leaving later result channels empty if callers wait blindly. `WorkerPool.Put` can block if the queue fills and no worker remains after errors. Tests cover many concurrency sizes and first-error behavior but do not run with the race detector here.
<!-- END_FILE_RESEARCH: sources/cloud-native/nydus/contrib/nydusify/pkg/utils/worker.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/nydus/contrib/nydusify/pkg/utils/worker_test.go -->
# sources/cloud-native/nydus/contrib/nydusify/pkg/utils/worker_test.go

## Purpose

This test file exercises the utility worker pools under success, failure, and mismatched worker/job counts.

## Important APIs, Types, and Functions

`queueJob` implements `RJob` and injects an error when `before == 1500`. `TestQueueWorkerPool1` and `TestQueueWorkerPool2` validate ordered result channels and stopping on job error. `TestWorkerPool1` through `TestWorkerPool5` validate unordered worker-pool completion and first-error delivery.

## Control Flow

Queue tests enqueue many jobs and consume `Waiter` channels in index order. Worker pool tests enqueue sleeping jobs, close the queue through `Waiter`, and inspect the first receive from the returned error channel and `Err`.

## State and Persistence Behavior

All state is in memory. The tests rely on sleeps to allow concurrent jobs to overlap and expose first-error behavior.

## Dependencies and Integration Points

The tests use `testify/require`, `time`, and formatted errors. They document expected API behavior for callers: `Waiter` both closes and waits for `WorkerPool`, while `QueueWorkerPool.Waiter` only exposes result channels.

## Risks and Test Signals

The tests are concurrency-sensitive and would benefit from race-detector execution. They do not assert that all goroutines exit after early errors or that blocked `Put` calls are impossible under error conditions.
<!-- END_FILE_RESEARCH: sources/cloud-native/nydus/contrib/nydusify/pkg/utils/worker_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/nydus/contrib/nydusify/pkg/viewer/viewer.go -->
# sources/cloud-native/nydus/contrib/nydusify/pkg/viewer/viewer.go

## Purpose

This file implements the nydusify filesystem viewer: it parses a target Nydus image, pulls bootstrap/config artifacts, prepares nydusd configuration, mounts the image, and waits for a termination signal before cleanup.

## Important APIs, Types, and Functions

`Opt` captures workdir, target reference, mount path, nydusd path, backend type/config, expected arch, fs version, and prefetch flag. `FsViewer` holds options, a parser, and `tool.NydusdConfig`. `New` validates target and constructs provider/parser. `PullBootstrap`, `getBootstrapFile`, `MountImage`, `View`, `view`, and `handleExternalBackendConfig` implement the workflow.

## Control Flow

`View` calls `view` and retries once over HTTP if `utils.RetryWithHTTP` says the error is retryable and the remote can switch protocol. `view` parses the image, detects model artifacts, builds nydusd config paths under `WorkDir`, pulls bootstrap and optional backend JSON, rewrites external backend config, enables digest validation for RAFS v5, mounts nydusd, then blocks until SIGINT or SIGTERM before deleting `WorkDir`.

## State and Persistence Behavior

The viewer deletes and recreates `WorkDir`, writes pretty JSON dumps, writes extracted bootstrap/backend files, creates blob cache and mount directories, runs a nydusd process through `tool.NewNydusd`, and removes the work directory after signal. It does not unmount directly in this file; unmount behavior is implied by daemon/tool handling.

## Dependencies and Integration Points

It integrates with image providers, parser, model-spec artifact type, checker/tool nydusd wrapper, external backend config rewrite, bootstrap layer filenames from utils constants, and OS signal handling.

## Risks and Test Signals

Risks include destructive `WorkDir` cleanup, indefinite blocking in non-interactive contexts, reliance on signal delivery, and external backend rewrite assumptions. Tests cover constructor errors, pretty dump, bootstrap pull paths, mount errors, external backend handling, and HTTP retry, but not a full successful signal-driven view lifecycle.
<!-- END_FILE_RESEARCH: sources/cloud-native/nydus/contrib/nydusify/pkg/viewer/viewer.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/nydus/contrib/nydusify/pkg/viewer/viewer_test.go -->
# sources/cloud-native/nydus/contrib/nydusify/pkg/viewer/viewer_test.go

## Purpose

This test file verifies viewer construction, bootstrap extraction, external backend handling, mount setup, and retry behavior with monkey-patched dependencies.

## Important APIs, Types, and Functions

`failingJSON` exercises marshal errors. `buildBootstrapArchive` creates a gzip tar archive. Tests include `TestNewFsViewer`, `TestNewFsViewerErrors`, `TestPrettyDump`, `TestPullBootstrap`, `TestPullBootstrapWithoutNydusImage`, `TestGetBootstrapFile`, `TestHandleExternalBackendConfig`, `TestMountImage`, `TestViewParseError`, and `TestViewHTTPRetry`.

## Control Flow

Tests use `gomonkey` to patch parser methods, private methods, `utils.BuildRuntimeExternalBackendConfig`, `tool.NewNydusd`, and `Nydusd.Mount`. They assert wrapped errors and success paths without launching real nydusd or accessing a real registry.

## State and Persistence Behavior

Tests write temporary work directories and bootstrap/backend files; some hard-coded `/tmp/nydusify/fsviwer` and `/tmp/backend.json` paths are used. Monkey patches are reset with defers.

## Dependencies and Integration Points

The tests depend on parser, remote, checker/tool, backend config structs, utils constants, gzip/tar primitives, `gomonkey`, and `testify`. They are strong integration signals for viewer orchestration boundaries.

## Risks and Test Signals

Monkey patching can be brittle across compiler/runtime changes. Tests do not perform an end-to-end successful `View` because it blocks on signals, and they do not verify cleanup after signal or real nydusd process behavior.
<!-- END_FILE_RESEARCH: sources/cloud-native/nydus/contrib/nydusify/pkg/viewer/viewer_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/nydus/contrib/nydusify/plugin/main.go -->
# sources/cloud-native/nydus/contrib/nydusify/plugin/main.go

## Purpose

This file defines a minimal nydusify hook plugin implementation and registers it from `main`.

## Important APIs, Types, and Functions

`LocalHook` implements `BeforePushManifest` and `AfterPushManifest`, both returning nil. `main` calls `hook.NewPlugin(&LocalHook{})`.

## Control Flow

There is no branching. Hook callbacks are no-ops, and plugin startup delegates to the hook package.

## State and Persistence Behavior

The plugin stores no state and writes nothing itself. Runtime behavior depends on the hook framework invoked by `hook.NewPlugin`.

## Dependencies and Integration Points

The only dependency is `contrib/nydusify/pkg/hook`. This file is an extension point for manifest push lifecycle hooks in nydusify.

## Risks and Test Signals

As a no-op plugin, the main risk is that it is a placeholder and provides no validation or side effects. Tests assert `LocalHook` satisfies `hook.Hook` and callbacks return nil.
<!-- END_FILE_RESEARCH: sources/cloud-native/nydus/contrib/nydusify/plugin/main.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/nydus/contrib/nydusify/plugin/main_test.go -->
# sources/cloud-native/nydus/contrib/nydusify/plugin/main_test.go

## Purpose

This test file verifies the minimal local plugin hook implementation.

## Important APIs, Types, and Functions

The compile-time assertion `var _ hook.Hook = (*LocalHook)(nil)` checks interface conformance. `TestLocalHook` calls `BeforePushManifest` and `AfterPushManifest` with empty hook info.

## Control Flow

The test constructs `LocalHook`, invokes both callbacks, and expects no errors.

## State and Persistence Behavior

No state is read or written.

## Dependencies and Integration Points

It depends on the hook package and `testify/require`. It provides a narrow compile and callback signal for the plugin entry point.

## Risks and Test Signals

The test does not exercise `main` or plugin process registration. Its main value is guarding the hook interface shape.
<!-- END_FILE_RESEARCH: sources/cloud-native/nydus/contrib/nydusify/plugin/main_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/nydus/deny.toml -->
# sources/cloud-native/nydus/deny.toml

## Purpose

This file configures `cargo deny` policy for the Rust workspace, covering advisory handling, license allowlists, duplicate-version warnings, and allowed crate sources.

## Important APIs, Types, and Functions

Sections include `[graph]`, `[advisories]`, `[licenses]`, `[[licenses.clarify]]`, `[licenses.private]`, `[bans]`, and `[sources]`. Advisory ignores document current accepted risks for bincode, rand, ring, rsa, rustls-pemfile, hickory-proto, rustls-webpki, and proc-macro-error2. License policy allows common permissive licenses and clarifies `ring` as `ISC AND MIT AND OpenSSL`.

## Control Flow

`cargo deny check` reads this declarative policy and applies lint levels. Yanked crates warn, multiple versions warn, wildcard dependencies are allowed, unknown registries/git repositories warn, and crates.io is the allowed registry.

## State and Persistence Behavior

The file has no runtime state, but it persists the repository's dependency risk posture. Advisory ignore reasons are durable audit records and must be kept current as dependencies change.

## Dependencies and Integration Points

It integrates with CI or local `cargo deny` runs and the RustSec advisory database. It affects all Rust crates in the Nydus workspace, including `nydus-rafs`.

## Risks and Test Signals

Ignored advisories can mask real exposure if dependency usage changes. Several ignores cite transitive dependencies and no safe upgrades, so periodic review is essential. The policy currently warns rather than denies for yanked, duplicate, unknown source, and unknown git conditions.
<!-- END_FILE_RESEARCH: sources/cloud-native/nydus/deny.toml -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/nydus/goreleaser.sh -->
# sources/cloud-native/nydus/goreleaser.sh

## Purpose

This script generates a `.goreleaser.yml` for packaging static Nydus binaries for the host Go OS/architecture.

## Important APIs, Types, and Functions

It reads `GOOS` and `GOARCH`, defaults `GOARCH` from `go env`, and writes a GoReleaser version 2 configuration. Builds include `nydusify`, `nydus-overlayfs`, `nydus-image`, `nydusctl`, and `nydusd`, all using `contrib/goreleaser/main.go`, `CGO_ENABLED=0`, and post-build copying from `nydus-static`. It configures zip archives, checksums, snapshot versions, changelog filters, and deb/rpm nfpm packaging.

## Control Flow

The script is linear: detect environment, emit a heredoc to `.goreleaser.yml`, and exit. GoReleaser later executes hooks and package creation.

## State and Persistence Behavior

It overwrites `.goreleaser.yml` in the current directory. The generated release config creates `dist` artifacts and packages when GoReleaser runs.

## Dependencies and Integration Points

It depends on `go env`, GoReleaser, nfpm support, and a preexisting `nydus-static` directory containing binaries/configs. It is part of release automation rather than runtime code.

## Risks and Test Signals

The generated builds all point to the same main package and rely on binary names to select outputs, so release behavior depends on `contrib/goreleaser/main.go`. Host-only GOOS/GOARCH limits cross-platform output. There is no direct test; release validation is by running GoReleaser.
<!-- END_FILE_RESEARCH: sources/cloud-native/nydus/goreleaser.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/nydus/misc/configs/nydusd-blob-cache-entry-configuration-v2.toml -->
# sources/cloud-native/nydus/misc/configs/nydusd-blob-cache-entry-configuration-v2.toml

## Purpose

This sample TOML documents a version 2 Nydus image service configuration for a blob-cache entry with metadata blob path support.

## Important APIs, Types, and Functions

Top-level fields include `version = 2`, `id`, and `metadata_path`. It defines localfs, OSS, and registry backend examples, proxy settings, filecache/fscache/cache prefetch settings, encryption options, and bandwidth/thread limits.

## Control Flow

The file is declarative. Nydusd config loading selects the active backend by `backend.type` and active cache by `cache.type`; other backend sections are examples unless selected.

## State and Persistence Behavior

Configured paths point to local blob data, alternate cache directories, metadata blobs, and cache work directories. Credentials and encryption keys appear as placeholders but would be sensitive in real configs.

## Dependencies and Integration Points

It targets Nydus `ConfigV2` parsing and blob-cache entry runtime behavior. Proxy fields align with Dragonfly or HTTP proxy integration.

## Risks and Test Signals

The file contains a likely typo section `[backend.registy]` while proxy uses `[backend.registry.proxy]`, which may confuse users or be ignored by parsers. As a sample, correctness is validated only indirectly by config parser tests or manual nydusd startup.
<!-- END_FILE_RESEARCH: sources/cloud-native/nydus/misc/configs/nydusd-blob-cache-entry-configuration-v2.toml -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/nydus/misc/configs/nydusd-blob-cache-entry.toml -->
# sources/cloud-native/nydus/misc/configs/nydusd-blob-cache-entry.toml

## Purpose

This sample TOML describes a bootstrap blob-cache entry wrapping a nested version 2 Nydus configuration under `config_v2`.

## Important APIs, Types, and Functions

Top-level `type = "bootstrap"`, `id`, and `domain_id` identify the cache entry. Nested `[config_v2]` mirrors Nydus config v2 with metadata path, backend localfs/OSS/registry/proxy settings, cache settings, and cache prefetch controls.

## Control Flow

The file is loaded declaratively by consumers that understand bootstrap entry documents. The runtime selects backend/cache sections based on nested type fields.

## State and Persistence Behavior

It points to metadata blob paths, local blob files, cache work directories, and optional proxy endpoints. In real deployments, it persists domain-specific cache entry identity.

## Dependencies and Integration Points

It integrates with blob cache entry parsing and Nydus image service config v2. The top-level wrapper differs from plain `ConfigV2` files and is intended for cache entry/bootstrap management.

## Risks and Test Signals

Like the v2 sample, it includes a `[config_v2.backend.registry]` section here, avoiding the typo seen in the other sample. Placeholder credentials and broad encryption examples should not be copied into production without replacement. Validation is mostly by parser/runtime loading.
<!-- END_FILE_RESEARCH: sources/cloud-native/nydus/misc/configs/nydusd-blob-cache-entry.toml -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/nydus/misc/configs/nydusd-boostrap-blob-cache-entry.json -->
# sources/cloud-native/nydus/misc/configs/nydusd-boostrap-blob-cache-entry.json

## Purpose

This JSON sample defines a bootstrap blob-cache entry for localfs-backed metadata and fscache caching.

## Important APIs, Types, and Functions

Fields include top-level `type`, `id`, `domain_id`, and nested `config` with `id`, `backend_type`, `backend_config.dir`, `cache_type`, `cache_config.work_dir`, and `metadata_file`.

## Control Flow

There is no procedural logic. Consumers parse the entry and use the nested config to locate local blobs, cache data, and metadata.

## State and Persistence Behavior

The sample references `/tmp/nydus` for backend/cache data and `/tmp/nydus/bootstrap1` for metadata. It models persisted cache entry identity and paths.

## Dependencies and Integration Points

It integrates with older or JSON-based blob-cache entry configuration paths in nydusd tooling.

## Risks and Test Signals

The filename contains `boostrap`, likely preserving an existing typo. The sample uses tmp paths and should not be treated as production persistence. There are no direct tests for this specific file.
<!-- END_FILE_RESEARCH: sources/cloud-native/nydus/misc/configs/nydusd-boostrap-blob-cache-entry.json -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/nydus/misc/configs/nydusd-config-v2.toml -->
# sources/cloud-native/nydus/misc/configs/nydusd-config-v2.toml

## Purpose

This sample TOML documents the standard Nydus image service config v2 shape, covering backend, cache, RAFS, and prefetch settings.

## Important APIs, Types, and Functions

It defines version/id, localfs/OSS/registry backends with proxy options, filecache/fscache settings, encryption options, cache prefetch, RAFS mode/validation/xattr/stat/access-pattern settings, and RAFS prefetch controls.

## Control Flow

Nydusd's config parser selects active backend and cache by type. RAFS `mode = "direct"` and prefetch options guide mount-time filesystem behavior and data-fetch policy.

## State and Persistence Behavior

The config stores local blob paths, cache directories, network backend credentials, encryption key placeholders, and runtime validation/prefetch behavior. These settings directly influence nydusd cache persistence and remote access.

## Dependencies and Integration Points

It maps to `nydus_api::ConfigV2` used by `rafs::Rafs::new`, blobfs, and nydusd. Proxy fields match Dragonfly and HTTP proxy integration points.

## Risks and Test Signals

The sample has `[backend.registy]` typo while proxy uses `[backend.registry.proxy]`, creating a risk that registry examples are not loadable as written. Placeholder secrets and skip-verify examples require production hardening. Validation is through config parser/runtime tests rather than this file itself.
<!-- END_FILE_RESEARCH: sources/cloud-native/nydus/misc/configs/nydusd-config-v2.toml -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/nydus/misc/configs/nydusd-config.json -->
# sources/cloud-native/nydus/misc/configs/nydusd-config.json

## Purpose

This JSON sample provides a nydusd runtime configuration using a registry backend and blobcache.

## Important APIs, Types, and Functions

The JSON defines `device.backend.type = "registry"` with timeout, connect timeout, retry limit, skip-verify, and CA certificate file fields; `device.cache.type = "blobcache"` with work dir; and filesystem options including direct mode, digest validation, xattrs, iostats, and `fs_prefetch`.

## Control Flow

Nydusd reads this declarative config at startup. Backend host/repo are absent here, suggesting they are supplied externally or via snapshotter annotations.

## State and Persistence Behavior

Cache data is stored under `/var/lib/nydus/cache`. The config enables prefetch and extended attributes but disables digest validation and per-file IO stats.

## Dependencies and Integration Points

It integrates with nydusd JSON config loading and registry backend runtime configuration. The CA path option aligns with TLS trust customization.

## Risks and Test Signals

Missing registry host/repo fields make it a partial config for contexts that inject backend source dynamically. There are no direct tests for this sample.
<!-- END_FILE_RESEARCH: sources/cloud-native/nydus/misc/configs/nydusd-config.json -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/nydus/misc/dragonfly/dfdaemon.yaml -->
# sources/cloud-native/nydus/misc/dragonfly/dfdaemon.yaml

## Purpose

This YAML is a minimal Dragonfly dfdaemon configuration for local end-to-end tests with Nydus proxy-backed image access.

## Important APIs, Types, and Functions

It configures scheduler cluster ID, manager address, seed peer mode, upload/proxy ports, storage/log/cache directories, download socket path, dynamic config refresh, and console mode.

## Control Flow

Dragonfly dfdaemon reads this config at startup, connects to the local manager on port 65003, exposes proxy server port 4001, upload server port 4000, and a Unix download socket.

## State and Persistence Behavior

Runtime data is stored under `/tmp/dragonfly/storage`, `/tmp/dragonfly/cache/dfdaemon`, and `/tmp/dragonfly/logs/dfdaemon`.

## Dependencies and Integration Points

It integrates with the matching local Dragonfly manager and scheduler configs and with Nydus configs that point proxy URL/ping URL to `127.0.0.1:4001`.

## Risks and Test Signals

The config is local-test oriented and assumes writable `/tmp`, local manager availability, and no port conflicts. It is not hardened for production authentication or persistence.
<!-- END_FILE_RESEARCH: sources/cloud-native/nydus/misc/dragonfly/dfdaemon.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/nydus/misc/dragonfly/manager.yaml -->
# sources/cloud-native/nydus/misc/dragonfly/manager.yaml

## Purpose

This YAML configures a minimal Dragonfly Manager for local E2E testing.

## Important APIs, Types, and Functions

It sets gRPC port 65003, REST address `:8080`, log/cache directories, JWT settings, MySQL connection parameters, Redis address, migration enablement, and console mode.

## Control Flow

Dragonfly Manager reads the config at startup, opens gRPC/REST endpoints, connects to local MySQL and Redis, and performs database migrations when enabled.

## State and Persistence Behavior

Logs/cache are under `/tmp/dragonfly`; persistent manager state is in MySQL database `manager` and Redis at localhost.

## Dependencies and Integration Points

It is paired with local scheduler and dfdaemon configs. Scheduler and dfdaemon use the manager gRPC address to register and coordinate.

## Risks and Test Signals

Credentials are fixed local-test values (`root`/`dragonfly`), JWT key is static, and ports may conflict. This is an E2E fixture, not a production config.
<!-- END_FILE_RESEARCH: sources/cloud-native/nydus/misc/dragonfly/manager.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/nydus/misc/dragonfly/nydusd-config.json -->
# sources/cloud-native/nydus/misc/dragonfly/nydusd-config.json

## Purpose

This nydusd JSON config exercises registry access through a Dragonfly proxy with fallback enabled and filesystem prefetch enabled.

## Important APIs, Types, and Functions

It targets `ghcr.io/dragonflyoss/image-service/nginx`, uses HTTPS with skip-verify, sets proxy URL and ping URL to local dfdaemon port 4001, enables fallback, configures blobcache under `/tmp/nydus-test/cache/`, enables digest validation/xattrs, and configures `fs_prefetch`.

## Control Flow

At runtime, nydusd attempts blob reads through the proxy and may fall back to the registry when proxy health fails. Prefetch uses 10 threads, 128 KiB merging size, and a 1 MiB/s bandwidth rate.

## State and Persistence Behavior

Blob cache persists under `/tmp/nydus-test/cache/`. The config validates cache data and filesystem digests.

## Dependencies and Integration Points

It integrates with Dragonfly dfdaemon local proxy and GHCR registry image fixtures.

## Risks and Test Signals

Skip-verify is enabled for testing. The config depends on network availability, GHCR content, and local proxy health. It signals fallback behavior in E2E tests.
<!-- END_FILE_RESEARCH: sources/cloud-native/nydus/misc/dragonfly/nydusd-config.json -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/nydus/misc/dragonfly/nydusd-http-proxy-nofallback-config.json -->
# sources/cloud-native/nydus/misc/dragonfly/nydusd-http-proxy-nofallback-config.json

## Purpose

This nydusd config tests local Dragonfly HTTP proxy access without fallback to the source registry.

## Important APIs, Types, and Functions

It uses a registry backend for `ghcr.io/dragonflyoss/image-service/nginx`, proxy URL/ping URL `http://127.0.0.1:4001`, `fallback: false`, blobcache under `/tmp/nydus-http-proxy-nofallback-test/cache/`, digest validation, xattrs, and disabled filesystem prefetch.

## Control Flow

Nydusd routes registry blob access through the proxy. If the proxy is unhealthy or fails, no fallback path is allowed, so reads should fail.

## State and Persistence Behavior

Cache data is isolated under the no-fallback test cache directory. No persistent registry credentials are configured.

## Dependencies and Integration Points

It integrates with Dragonfly dfdaemon as an HTTP proxy and is useful for E2E assertions that proxy failures surface as runtime errors.

## Risks and Test Signals

The config intentionally makes availability depend on the proxy. Skip-verify remains enabled for test convenience.
<!-- END_FILE_RESEARCH: sources/cloud-native/nydus/misc/dragonfly/nydusd-http-proxy-nofallback-config.json -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/nydus/misc/dragonfly/nydusd-proxy-error-fallback.json -->
# sources/cloud-native/nydus/misc/dragonfly/nydusd-proxy-error-fallback.json

## Purpose

This nydusd config models a proxy error scenario where fallback to the source registry is allowed.

## Important APIs, Types, and Functions

It targets the nginx fixture image, sets proxy URL to local port 4001, enables `fallback: true`, uses `use_http: true`, lengthens proxy health check interval to 300 seconds, disables fs prefetch, and stores cache under `/tmp/nydus-proxy-error-fallback-test/cache/`.

## Control Flow

Nydusd first attempts proxy-based reads and may fall back to direct registry access when proxy operations fail.

## State and Persistence Behavior

Blob cache is isolated to the fallback error test directory. Registry requests are unauthenticated and skip TLS verification.

## Dependencies and Integration Points

It integrates with Dragonfly proxy error E2E tests and registry backend fallback code paths.

## Risks and Test Signals

The config intentionally tolerates proxy failure, so tests must distinguish successful fallback from healthy-proxy success. Long check intervals can preserve stale proxy state during tests.
<!-- END_FILE_RESEARCH: sources/cloud-native/nydus/misc/dragonfly/nydusd-proxy-error-fallback.json -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/nydus/misc/dragonfly/nydusd-proxy-error-nofallback.json -->
# sources/cloud-native/nydus/misc/dragonfly/nydusd-proxy-error-nofallback.json

## Purpose

This nydusd config models a proxy error scenario where fallback is disabled.

## Important APIs, Types, and Functions

It is similar to the fallback variant but sets `fallback: false`, uses `use_http: true`, disables fs prefetch, and stores cache under `/tmp/nydus-proxy-error-nofallback-test/cache/`.

## Control Flow

Registry blob reads are routed through the local proxy. Proxy errors should propagate instead of falling back to the source registry.

## State and Persistence Behavior

Cache state is isolated to the no-fallback error directory. Digest validation and cache validation are enabled.

## Dependencies and Integration Points

It is an E2E fixture for Dragonfly proxy error handling and nydusd registry backend fallback policy.

## Risks and Test Signals

This config should fail when proxy access fails, so test harnesses must ensure the intended proxy error is produced. Skip-verify and fixed GHCR image paths are test-only choices.
<!-- END_FILE_RESEARCH: sources/cloud-native/nydus/misc/dragonfly/nydusd-proxy-error-nofallback.json -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/nydus/misc/dragonfly/nydusd-sdk-config.json -->
# sources/cloud-native/nydus/misc/dragonfly/nydusd-sdk-config.json

## Purpose

This nydusd config tests Dragonfly SDK integration through a proxy with scheduler endpoint and no fallback.

## Important APIs, Types, and Functions

It targets `ghcr.io/dragonflyoss/image-service/java`, configures proxy URL/ping URL to dfdaemon, includes `dragonfly_scheduler_endpoint: http://127.0.0.1:8002`, disables fallback, enables fs prefetch, and uses blobcache under `/tmp/nydus-sdk-test/cache/`.

## Control Flow

Nydusd registry backend uses Dragonfly proxy/SDK settings to coordinate downloads through the local scheduler. Without fallback, SDK/proxy failures should surface.

## State and Persistence Behavior

Cached blobs live under the SDK test cache directory. Prefetch can populate cache proactively.

## Dependencies and Integration Points

It integrates with local Dragonfly scheduler, manager, dfdaemon, and the Java GHCR fixture image.

## Risks and Test Signals

The config depends on all local Dragonfly components plus network access. It is useful for validating scheduler-aware proxy behavior and prefetch interactions.
<!-- END_FILE_RESEARCH: sources/cloud-native/nydus/misc/dragonfly/nydusd-sdk-config.json -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/nydus/misc/dragonfly/nydusd-sdk-fallback-config.json -->
# sources/cloud-native/nydus/misc/dragonfly/nydusd-sdk-fallback-config.json

## Purpose

This nydusd config tests Dragonfly SDK/proxy integration with fallback enabled.

## Important APIs, Types, and Functions

It targets the Java fixture image, sets local proxy and scheduler endpoint, enables `fallback: true`, disables fs prefetch, and stores cache under `/tmp/nydus-sdk-fallback-test/cache/`.

## Control Flow

Nydusd may use the Dragonfly scheduler/proxy path but can return to direct registry access if the proxy path is unavailable.

## State and Persistence Behavior

Cache state is isolated under the SDK fallback directory. Digest and cache validation are enabled.

## Dependencies and Integration Points

It integrates with local Dragonfly scheduler/dfdaemon and registry backend fallback paths.

## Risks and Test Signals

Fallback can hide SDK/proxy failures unless tests assert which path served data. This fixture is intended to contrast with the no-fallback SDK config.
<!-- END_FILE_RESEARCH: sources/cloud-native/nydus/misc/dragonfly/nydusd-sdk-fallback-config.json -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/nydus/misc/dragonfly/scheduler.yaml -->
# sources/cloud-native/nydus/misc/dragonfly/scheduler.yaml

## Purpose

This YAML configures a minimal local Dragonfly Scheduler for E2E testing.

## Important APIs, Types, and Functions

It sets server port 8002, log/cache directories, default scheduling algorithm, retry limits and intervals, Redis DBs, manager address/cluster ID, keepalive interval, empty seed peer config, and console mode.

## Control Flow

The scheduler starts on port 8002, connects to Redis and Manager, and coordinates peer scheduling for dfdaemon/SDK clients.

## State and Persistence Behavior

Logs/cache live under `/tmp/dragonfly`. Scheduling state uses local Redis DBs 1 and 2.

## Dependencies and Integration Points

It pairs with `manager.yaml`, `dfdaemon.yaml`, and nydusd SDK configs that reference `http://127.0.0.1:8002`.

## Risks and Test Signals

The fixture assumes local Redis and Manager availability. Static ports and tmp paths are suitable for isolated tests but can conflict on shared hosts.
<!-- END_FILE_RESEARCH: sources/cloud-native/nydus/misc/dragonfly/scheduler.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/nydus/misc/fscache/setup.sh -->
# sources/cloud-native/nydus/misc/fscache/setup.sh

## Purpose

This root-oriented script installs and enables Linux cachefilesd/fscache support for Nydus fscache testing.

## Important APIs, Types, and Functions

It runs `apt update`, installs `cachefilesd`, edits `/etc/default/cachefilesd` to set `RUN=yes`, loads the `cachefiles` kernel module, starts `cachefilesd`, checks systemd status, verifies `/dev/cachefiles`, finds users with `lsof`, and kills the process using the device.

## Control Flow

The script is linear and lacks `set -e`; later commands may continue after earlier failures. It starts cachefilesd, then kills the process holding `/dev/cachefiles` to make the device available.

## State and Persistence Behavior

It mutates system packages, `/etc/default/cachefilesd`, kernel module state, systemd service state, and processes. It requires root and has host-wide side effects.

## Dependencies and Integration Points

It depends on Debian/Ubuntu apt, cachefilesd, modprobe, systemctl, lsof, and fscache kernel support. It supports Nydus fscache snapshotter/runtime tests.

## Risks and Test Signals

The `kill -9` behavior is destructive and should only run in disposable test environments. Lack of strict error handling can leave partial setup. Success is indicated by `/dev/cachefiles` existence and printed status.
<!-- END_FILE_RESEARCH: sources/cloud-native/nydus/misc/fscache/setup.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/nydus/misc/install-protoc.sh -->
# sources/cloud-native/nydus/misc/install-protoc.sh

## Purpose

This script installs a pinned protobuf compiler release for supported OS/architecture combinations.

## Important APIs, Types, and Functions

It uses `set -euo pipefail`, `PROTOC_VERSION=29.6`, auto-detects system (`linux` or `osx`) and architecture (`amd64`, `arm64`, `ppc64le`, `riscv64`), maps to protobuf release archive names, downloads with `curl`, unzips to `/usr/local` with sudo, and removes the zip.

## Control Flow

Optional command-line arguments override architecture and system. Unsupported OS/arch exit non-zero, while riscv64 exits zero after printing a skip message because upstream protoc archive is unsupported.

## State and Persistence Behavior

It writes a downloaded zip in the current directory, installs files under `/usr/local`, and removes the zip afterward.

## Dependencies and Integration Points

It depends on curl, sudo, unzip, uname, and GitHub protobuf releases. `misc/prepare.sh` calls it during performance environment setup.

## Risks and Test Signals

The script trusts the downloaded archive without checksum verification and requires sudo. Network or GitHub availability affects reproducibility.
<!-- END_FILE_RESEARCH: sources/cloud-native/nydus/misc/install-protoc.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/nydus/misc/musl-static/Dockerfile -->
# sources/cloud-native/nydus/misc/musl-static/Dockerfile

## Purpose

This Dockerfile defines a musl-based Rust build environment for producing static Nydus release binaries.

## Important APIs, Types, and Functions

It uses base image `clux/muslrust:1.72.1`, accepts `RUST_TARGET` defaulting to `x86_64-unknown-linux-musl`, installs `cmake`, sets workdir `/nydus-rs`, and runs rustup component/target setup followed by `make static-release`.

## Control Flow

At container runtime, the `CMD` installs clippy/rustfmt/target and invokes the static release make target.

## State and Persistence Behavior

The image layer installs cmake. Build outputs are produced in the mounted or copied `/nydus-rs` workspace at runtime.

## Dependencies and Integration Points

It integrates with the repository Makefile and musl static build/release workflow used by `goreleaser.sh` packaging assumptions.

## Risks and Test Signals

The base Rust version is pinned and may drift from workspace toolchain requirements. Installing rustup components in `CMD` adds runtime network/toolchain dependence unless cached.
<!-- END_FILE_RESEARCH: sources/cloud-native/nydus/misc/musl-static/Dockerfile -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/nydus/misc/performance/containerd_config.toml -->
# sources/cloud-native/nydus/misc/performance/containerd_config.toml

## Purpose

This containerd config enables the Nydus snapshotter as the CRI and transfer unpack snapshotter for performance testing.

## Important APIs, Types, and Functions

It sets containerd version/root/state/debug level, configures CRI `snapshotter = "nydus"`, keeps snapshot annotations, disables discard of unpacked layers, adds local transfer unpack config for linux, and defines proxy plugin `nydus` at `/run/containerd-nydus/containerd-nydus-grpc.sock`.

## Control Flow

Containerd reads this file at startup and routes snapshot operations to the external Nydus proxy plugin. Export `enable_remote_snapshot_annotations` allows remote snapshot metadata propagation.

## State and Persistence Behavior

Containerd state lives under `/var/lib/containerd` and `/run/containerd`. Snapshotter state is external to the proxy plugin address.

## Dependencies and Integration Points

It integrates with `nydus-snapshotter.service`, `snapshotter_config.toml`, and containerd CRI.

## Risks and Test Signals

The file appears to concatenate the proxy export line and service unit text if copied incorrectly in surrounding output, but the source file itself is a short TOML. Static socket paths and debug logging are test-focused.
<!-- END_FILE_RESEARCH: sources/cloud-native/nydus/misc/performance/containerd_config.toml -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/nydus/misc/performance/nydus-snapshotter.service -->
# sources/cloud-native/nydus/misc/performance/nydus-snapshotter.service

## Purpose

This systemd unit starts the containerd Nydus snapshotter gRPC service for performance tests.

## Important APIs, Types, and Functions

The unit describes service ordering after network and before containerd, sets `HOME=/root`, runs `/usr/local/bin/containerd-nydus-grpc --config /etc/nydus/config.toml`, restarts always with one-second delay, uses `KillMode=process`, and strongly lowers OOM score.

## Control Flow

Systemd starts the process as a simple service and restarts it on exit. Containerd can then connect to the configured socket.

## State and Persistence Behavior

Logs go to journald. Runtime state is managed by the snapshotter config and process.

## Dependencies and Integration Points

It is installed by `misc/prepare.sh` and paired with `containerd_config.toml` proxy plugin settings.

## Risks and Test Signals

`Before=containerd.service` only matters if dependencies/order are used correctly. `OOMScoreAdjust=-999` protects the process strongly and may be inappropriate outside controlled performance tests.
<!-- END_FILE_RESEARCH: sources/cloud-native/nydus/misc/performance/nydus-snapshotter.service -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/nydus/misc/performance/nydusd_config.json -->
# sources/cloud-native/nydus/misc/performance/nydusd_config.json

## Purpose

This nydusd JSON config supports local performance tests using a registry backend and blobcache.

## Important APIs, Types, and Functions

It configures registry backend scheme `http`, host `localhost:5077`, skip verify, timeouts, retry limit, blobcache workdir under the containerd Nydus snapshotter cache, direct mode, disabled digest validation, enabled xattrs, disabled IO/access tracing, and disabled fs prefetch.

## Control Flow

Nydusd reads the config when launched by the snapshotter and fetches blobs from a local registry endpoint.

## State and Persistence Behavior

Blob cache persists under `/var/lib/containerd/io.containerd.snapshotter.v1.nydus/cache`.

## Dependencies and Integration Points

It is referenced by `snapshotter_config.toml` as the daemon config and installed by `prepare.sh` to `/etc/nydus/nydusd-config.fusedev.json`.

## Risks and Test Signals

The config assumes a local registry on port 5077 and disables validation/prefetch for benchmark isolation. It is not production-ready.
<!-- END_FILE_RESEARCH: sources/cloud-native/nydus/misc/performance/nydusd_config.json -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/nydus/misc/performance/snapshotter_config.toml -->
# sources/cloud-native/nydus/misc/performance/snapshotter_config.toml

## Purpose

This TOML configures the containerd Nydus snapshotter for performance and takeover tests.

## Important APIs, Types, and Functions

It sets root/address, dedicated daemon mode, cleanup policy, system/debug endpoints, daemon paths/config, fs driver, recover policy, thread count, log rotation, optional cgroup memory limit, metrics address, remote auth controls, snapshot flags, cache manager behavior, signature validation, and experimental stargz/referrers/backend-source/tarfs settings.

## Control Flow

The snapshotter reads this config at service startup. `recover_policy` controls daemon failure handling and is modified by `prepare.sh` for takeover tests. The daemon section points to nydusd/nydus-image binaries and the nydusd config.

## State and Persistence Behavior

Snapshotter state is under `/var/lib/containerd/io.containerd.snapshotter.v1.nydus`, sockets under `/run/containerd-nydus`, logs rotate according to configured caps, and metrics bind on `:9110`.

## Dependencies and Integration Points

It integrates with containerd proxy plugin, systemd unit, nydusd binary/config, nydus-image, cache manager, Kubernetes/CRI auth options, and experimental tarfs support.

## Risks and Test Signals

Dedicated mode, cgroups, metrics, and debug endpoints affect host resources. Several experimental features are disabled by default. Static paths must match installed binaries from `prepare.sh`.
<!-- END_FILE_RESEARCH: sources/cloud-native/nydus/misc/performance/snapshotter_config.toml -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/nydus/misc/prepare.sh -->
# sources/cloud-native/nydus/misc/prepare.sh

## Purpose

This script prepares a host for Nydus snapshotter performance testing by installing binaries, downloading dependencies, configuring containerd and nydus, and starting services.

## Important APIs, Types, and Functions

It defaults `INSTALL_TARGET_TYPE=release`, optionally changes snapshotter `recover_policy` for `takeover_test`, queries latest release versions for nydus-snapshotter, nerdctl, and CNI plugins from GitHub, installs local Nydus binaries, downloads/extracts snapshotter, nerdctl, and CNI plugins, installs configs and systemd unit files, restarts containerd, starts nydus-snapshotter, and runs `misc/install-protoc.sh`.

## Control Flow

The script is mostly linear and uses command substitution for latest versions. It does not enable strict shell error handling, so failures may cascade.

## State and Persistence Behavior

It mutates `/usr/local/bin`, `/opt/cni/bin`, `/etc/containerd/config.toml`, `/etc/nydus`, `/etc/systemd/system`, systemd service state, and the working directory via downloaded archives.

## Dependencies and Integration Points

It depends on curl, wget, tar, sudo, systemctl, local built Nydus binaries, GitHub release APIs, and the performance config files in the same directory.

## Risks and Test Signals

It downloads latest external releases without pinning/checksum validation, assumes linux-amd64 archives, and lacks `set -e`. It should be used in controlled test environments, not production hosts.
<!-- END_FILE_RESEARCH: sources/cloud-native/nydus/misc/prepare.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/nydus/rafs/Cargo.toml -->
# sources/cloud-native/nydus/rafs/Cargo.toml

## Purpose

This manifest defines the `nydus-rafs` Rust crate, which implements the RAFS filesystem format and FUSE integration for Nydus Image Service.

## Important APIs, Types, and Functions

Package metadata declares version `0.4.1`, edition 2021, Apache-2.0 OR BSD-3-Clause license, and repository/homepage. Dependencies include config/error/logging/concurrency crates, `fuse-backend-rs`, `vm-memory`, `nydus-api`, `nydus-storage` with localfs backend feature, and `nydus-utils`. Features enable `fusedev`, `virtio-fs`, and `vhost-user-fs`.

## Control Flow

Cargo uses this manifest to compile the crate with feature-gated modules, especially `blobfs` under `virtio-fs`.

## State and Persistence Behavior

The manifest does not persist runtime state, but feature/dependency choices determine which filesystem backends and transports are compiled.

## Dependencies and Integration Points

It integrates with workspace dependencies and sibling Nydus crates. `nydus-storage` supplies blob devices/cache, `nydus-api` supplies config and error macros, and `fuse-backend-rs` supplies FUSE traits.

## Risks and Test Signals

Feature combinations affect public API availability. Dependency versions are part of the security/license surface governed by `deny.toml`. Tests are defined inside source modules rather than manifest targets.
<!-- END_FILE_RESEARCH: sources/cloud-native/nydus/rafs/Cargo.toml -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/nydus/rafs/src/blobfs/mod.rs -->
# sources/cloud-native/nydus/rafs/src/blobfs/mod.rs

## Purpose

This module implements setup for a virtio-fs blob passthrough filesystem that mirrors a host blob cache directory while using RAFS metadata/device logic to fetch blob ranges on demand.

## Important APIs, Types, and Functions

`BlobOndemandConfig` parses embedded JSON containing `ConfigV2`, bootstrap path, and blob cache directory. `Config` combines passthrough FS config with the on-demand config string. `BlobFs` holds `BlobfsState` and `PassthroughFs`. Important helpers include `BlobfsState::get_rafs_handle`, `BlobFs::new`, `import`, `ensure_path_exist`, `load_bootstrap`, `get_blob_id_and_size`, `stat`, and `open_file`.

## Control Flow

`BlobFs::new` parses and validates config, creates the passthrough FS, ensures cache dir exists, validates bootstrap file, and spawns a background thread to build/import a `Rafs` instance. `init` later joins that thread through `get_rafs_handle`. `get_blob_id_and_size` resolves a passthrough inode to a proc path, opens it with no-follow flags, stats it, and caches `(size, blob_id)` by inode.

## State and Persistence Behavior

The module creates cache directories and caches inode-to-blob mappings in memory. The RAFS handle transitions from a join handle to an initialized `Rafs` inside an `RwLock`. It reads bootstrap metadata but does not itself write blob data.

## Dependencies and Integration Points

It depends on `fuse_backend_rs` passthrough FS, `ConfigV2`, `BlobPrefetchRequest`, RAFS core, UNIX fd/path APIs, and serde JSON. `sync_io.rs` supplies the FUSE trait implementation and on-demand fetches.

## Risks and Test Signals

Initialization errors can be delayed until FUSE `init` joins the RAFS thread. Blob ID extraction trusts the file name from the passthrough path. Negative file sizes are rejected. Tests in the module actually cover generic RAFS IO writer/iterator behavior rather than blobfs construction.
<!-- END_FILE_RESEARCH: sources/cloud-native/nydus/rafs/src/blobfs/mod.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/nydus/rafs/src/blobfs/sync_io.rs -->
# sources/cloud-native/nydus/rafs/src/blobfs/sync_io.rs

## Purpose

This module implements synchronous FUSE operations for `BlobFs`, turning reads and DAX mappings into on-demand RAFS blob range fetches before delegating to the passthrough filesystem.

## Important APIs, Types, and Functions

`MAPPING_UNIT_SIZE` is 2 MiB. `BlobfsState::fetch_range_sync` calls `Rafs::fetch_range_synchronous`. `BlobFs::load_chunks_on_demand` computes a bounded `BlobPrefetchRequest`. The `FileSystem for BlobFs` implementation delegates read-only operations to `PassthroughFs`, denies mutating operations with `EACCES`, and intercepts `read` and `setupmapping`.

## Control Flow

`init` ensures the RAFS handle is ready before delegating to passthrough init. `read` validates/fetches the requested byte range, then calls `pfs.read`. `setupmapping` rejects writable mappings, rounds file offsets to 2 MiB boundaries, fetches the expanded range, then delegates mapping setup. All write/create/link/xattr mutation operations fail immediately.

## State and Persistence Behavior

The module does not persist new state beyond cache data fetched by the underlying `BlobDevice`. It reads cached inode-to-blob metadata and may cause backend/cache population through synchronous prefetch requests.

## Dependencies and Integration Points

It integrates with FUSE backend traits, virtio-fs fscache mapping requests, RAFS blob device prefetch, passthrough file operations, and Nydus error macros.

## Risks and Test Signals

Range validation rejects offsets beyond blob size and overflow, but `setupmapping` delegates with the rounded `len` while original `foffset` is passed, making careful compatibility with passthrough expectations important. Mutating operations are intentionally blocked. There are no focused tests for blobfs FUSE operations in this file.
<!-- END_FILE_RESEARCH: sources/cloud-native/nydus/rafs/src/blobfs/sync_io.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/nydus/rafs/src/fs.rs -->
# sources/cloud-native/nydus/rafs/src/fs.rs

## Purpose

This is the core RAFS filesystem implementation that glues FUSE requests, RAFS metadata, blob storage devices, cache/prefetch policy, metrics, and access checks together.

## Important APIs, Types, and Functions

`Rafs` stores instance id, `BlobDevice`, IO stats, `RafsSuper`, initialization flags, validation/prefetch/xattr settings, optional streaming `BlobPrefetcher`, and runtime UID/GID/time defaults. Key methods include `new`, `update`, `import`, `destroy`, `id`, `metadata`, `fetch_range_synchronous`, `get_root_inode`, `do_prefetch`, `convert_file_list`, `get_inode_attr`, and `get_inode_entry`. It implements `BackendFileSystem`, `FileSystem`, and Linux `Layer`.

## Control Flow

`new` validates config, loads metadata, creates a blob device, enforces RAFS v6 cache/validation constraints, and configures metrics. `import` starts stream prefetch, normal device prefetch, or no prefetch, then marks initialized. `destroy` stops prefetchers, destroys superblock, stops device prefetch, and closes the device. FUSE lookup/getattr/read/readdir/xattr/access calls read metadata, allocate blob IO vectors, fetch data, and record metrics.

## State and Persistence Behavior

The struct owns runtime initialization state and references blob cache/device state. Prefetch can populate local cache asynchronously or via streaming Dragonfly proxy optimization. `update` swaps metadata/device backend after initialization. RAFS itself is read-only through FUSE operations.

## Dependencies and Integration Points

It integrates with `fuse_backend_rs`, `nydus_storage::BlobDevice`, RAFS metadata traits, Nydus config v2, metrics, prefetcher, Linux overlay `Layer`, and Nydus error macros. It is the central runtime object mounted by nydusd.

## Risks and Test Signals

Read amplification and prefetch policies are performance-critical and differ between RAFS v5 and v6. `Arc::get_mut` in `destroy` assumes no extra superblock references. Access checks reimplement POSIX-like logic and need care for root/execute behavior. Tests cover simple constructor-like state, ID, xattr support, forget no-ops, negative entries, file-list conversion, plus commented historical integration tests.
<!-- END_FILE_RESEARCH: sources/cloud-native/nydus/rafs/src/fs.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/nydus/rafs/src/lib.rs -->
# sources/cloud-native/nydus/rafs/src/lib.rs

## Purpose

This crate root documents RAFS, declares public modules, defines crate-wide error/result types, abstracts bootstrap IO readers/writers, and provides an iterator over RAFS inode trees.

## Important APIs, Types, and Functions

Public modules include `blobfs` behind `virtio-fs`, `fs`, `metadata`, test-only `mock`, and `prefetch`. `RafsError` enumerates RAFS failure modes. `MetaType` classifies metadata errors. `RafsIoRead` and `RafsIoWrite` abstract file-like bootstrap IO, with helpers for alignment, padding, seeking, finalization, and byte extraction. `RafsIterator` walks all inodes depth-first.

## Control Flow

Reader/writer helpers wrap seek/write operations with Nydus errors and logging. `RafsIterator::new` starts from the root inode if available; `next` pops a node and pushes directory children in reverse order so iteration yields natural forward order.

## State and Persistence Behavior

The crate root itself maintains no global state. IO traits operate on supplied files/buffers, and iterator state is an in-memory stack of inode/path pairs.

## Dependencies and Integration Points

It brings in logging, bitflags, nydus-api, and nydus-storage macros. It exposes types consumed by metadata loading, RAFS building, and tests throughout the crate.

## Risks and Test Signals

`RafsIoWrite::as_bytes` is unimplemented by default and must be overridden by in-memory writers. Alignment helpers assume power-of-two alignment. Tests cover writer alignment/padding/seek helpers and iterator traversal over a fixture bootstrap.
<!-- END_FILE_RESEARCH: sources/cloud-native/nydus/rafs/src/lib.rs -->
