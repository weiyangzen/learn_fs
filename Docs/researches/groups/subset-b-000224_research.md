# Research: subset-b-000224

This grouped report covers the listed nydusify provider, converter, copier, modctl, hook, metrics, optimizer, packer, parser, remote, and snapshotter external backend files. Each source file has its own source-tree-aligned section for reconciliation into per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/nydus/contrib/nydusify/pkg/converter/provider/provider_test.go -->
# sources/cloud-native/nydus/contrib/nydusify/pkg/converter/provider/provider_test.go

Purpose: broad regression coverage for the converter provider package, especially provider state helpers, local import/export paths, content store replacement, and the StreamContent adapter used by streaming copy flows.

Important APIs and behavior under test: `New`, `ContentStore`, `SetContentStore`, `UsePlainHTTP`, `SetPushRetryConfig`, `WithLocalSource`, `WithLocalTarget`, `Resolver`, `Image`, `NewRemoteCache`, `Import`, `Export`, `Pull`, `Push`, and most StreamContent methods. The test host function validates insecure routing for a sentinel reference.

Control flow and state: tests construct a provider with a temporary work directory, mutate provider fields through public helpers, and validate image descriptor lookup through the internal `images` map. Local source and target branches verify error behavior for missing tar files and successful creation of output tar files.

Dependencies and integration points: containerd content APIs, platform matchers, acceleration-service remote credentials, OCI descriptors, local filesystem tar import/export, and StreamContent in-memory storage.

Risks and test signals: coverage is strongest for state mutation and StreamContent edge cases. Several local push/export tests only assert file creation and tolerate provider export errors, so manifest correctness and real registry behavior remain integration risks.
<!-- END_FILE_RESEARCH: sources/cloud-native/nydus/contrib/nydusify/pkg/converter/provider/provider_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/nydus/contrib/nydusify/pkg/converter/provider/stream_content.go -->
# sources/cloud-native/nydus/contrib/nydusify/pkg/converter/provider/stream_content.go

Purpose: implements `StreamContent`, a `content.Store` adapter that avoids ingesting pulled remote content locally while still supporting generated JSON/blob writes needed by converter handlers.

Important APIs/types/functions: `StreamContent`, `NewStreamContent`, `SetDefaultRef`, `Writer`, `ReaderAt`, `Info`, `Update`, `Walk`, `Delete`, ingest status methods, `memWriter`, `bytesReaderAt`, `copyMap`, `isFetchRef`, and `hasPrefix`.

Control flow: `Writer` classifies containerd fetch refs with prefixes such as `manifest-`, `index-`, `layer-`, `config-`, and `attestation-`; those return `ErrAlreadyExists` so fetch code treats content as already available remotely. Non-fetch refs receive a `memWriter`, whose `Commit` stores bytes keyed by expected or computed digest. `ReaderAt` first checks in-memory generated blobs, then fetches remotely with `remote.Fetch` using `defaultRef`.

State and persistence: labels, generated blobs, and `defaultRef` are in-memory behind an RW mutex. No durable local content is stored; `Walk` is empty and `Delete` only clears in-memory maps.

Dependencies and integration points: containerd content store interfaces, `errdefs`, Harbor acceleration-service registry fetch helpers, OCI descriptors, and digest validation.

Risks and test signals: default-ref absence is a hard not-found path. `memWriter.Truncate` does not reset the incremental digester, so digest after truncation can reflect pre-truncation data unless commit uses an expected digest. Tests document this behavior.
<!-- END_FILE_RESEARCH: sources/cloud-native/nydus/contrib/nydusify/pkg/converter/provider/stream_content.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/nydus/contrib/nydusify/pkg/converter/provider/stream_content_test.go -->
# sources/cloud-native/nydus/contrib/nydusify/pkg/converter/provider/stream_content_test.go

Purpose: focused unit tests for the standalone StreamContent implementation.

Important APIs under test: `Writer`, `ReaderAt`, `SetDefaultRef`, `Info`, `Update`, `Delete`, `Status`, `ListStatuses`, `Abort`, `copyMap`, `isFetchRef`, `hasPrefix`, `newMemWriter`, `memWriter.Truncate`, `memWriter.Commit`, and `bytesReaderAt`.

Control flow and state: tests write generated payloads through the memory writer, commit them, and read them back by digest. Fetch refs are expected to return `ErrAlreadyExists` with no writer. Info/update/delete tests prove label maps are copied on read/update and cleared by delete. Helper tests verify prefix classification.

Dependencies and integration points: uses containerd writer options and errors, OCI descriptors, and digest helpers, but avoids network fetch by reading from in-memory blobs.

Risks and test signals: tests explicitly assert that truncating after a digest was computed keeps the original digest value, which is a surprising behavior for callers expecting digest to track truncated content. The remote fetch branch with a populated default ref is not exercised here.
<!-- END_FILE_RESEARCH: sources/cloud-native/nydus/contrib/nydusify/pkg/converter/provider/stream_content_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/nydus/contrib/nydusify/pkg/converter/reverse_converter.go -->
# sources/cloud-native/nydus/contrib/nydusify/pkg/converter/reverse_converter.go

Purpose: provides experimental reverse conversion from a Nydus image back to a conventional OCI image.

Important APIs/functions: `ReverseConvert` is the main entry point. `reconvertWithSnapshotter` wires containerd nydus-snapshotter conversion functions with the local provider content store.

Control flow: `ReverseConvert` enters the `nydusify` containerd namespace, parses requested platforms, prepares a work directory and temporary subdirectory, constructs a converter provider, parses push retry delay, optionally enables plain HTTP, pulls the source image, resolves its root descriptor, reconverts it through snapshotter converter functions, and pushes the returned OCI descriptor to the target reference.

State and persistence: work directories are temporary unless the configured work dir pre-exists. The provider content store holds pulled source descriptors and generated converted descriptors. Push retry count/delay and plain HTTP state live on the provider.

Dependencies and integration points: containerd namespaces/platforms, Harbor platform parsing, converter provider, nydus-snapshotter `LayerReconvertFunc`, `UnpackOption`, and `DefaultIndexConvertFunc`, plus `nydus-image` path and compressor options.

Risks and test signals: marked experimental. Failure points include duration parsing, work-dir permissions, registry pull/push, missing source descriptors, nil converter result, and external builder behavior. It relies on snapshotter reconversion semantics for manifest/index correctness.
<!-- END_FILE_RESEARCH: sources/cloud-native/nydus/contrib/nydusify/pkg/converter/reverse_converter.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/nydus/contrib/nydusify/pkg/converter/reverse_converter_test.go -->
# sources/cloud-native/nydus/contrib/nydusify/pkg/converter/reverse_converter_test.go

Purpose: smoke, flow, error, performance, integration, and CI-friendly tests for reverse conversion setup and early failure behavior.

Important fixtures and functions: `MockRemoter` models the remote interface, `checkNydusImageAvailable` and `skipIfNydusImageNotAvailable` gate tool-dependent tests, and `TestHelperProcess` can emulate selected `nydus-image` command behavior.

Control flow: most tests construct `Opt` values and call `ReverseConvert`, asserting that invalid platform strings, bad push retry delays, canceled contexts, unavailable registries, or invalid work dirs produce errors. Registry-backed tests require `NYDUS_TEST_REGISTRY`; tool-backed tests skip if `nydus-image` is absent.

State and persistence: tests use `./tmp` in many cases and rely on ReverseConvert cleanup. Environment variables influence availability, registry selection, and helper process behavior.

Dependencies and integration points: external `nydus-image`, optional registry, containerd content interfaces, testify assertions/mocks.

Risks and test signals: tests are useful for parameter validation but provide limited deterministic coverage of a successful reconversion. Many assertions only require some error, so regressions deeper in manifest conversion or push output could remain undetected without a real integration environment.
<!-- END_FILE_RESEARCH: sources/cloud-native/nydus/contrib/nydusify/pkg/converter/reverse_converter_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/nydus/contrib/nydusify/pkg/copier/copier.go -->
# sources/cloud-native/nydus/contrib/nydusify/pkg/copier/copier.go

Purpose: copies images from a source reference or local tar to a target reference or local tar, with special handling for Nydus backend blobs so registry targets can receive externally stored blobs.

Important APIs/types/functions: `Opt`, `Copy`, `hosts`, `getLocalPath`, `getPlatform`, `getPusherInChunked`, and `pushBlobFromBackend`.

Control flow: `Copy` sets a containerd namespace, parses platforms, optionally creates a backend for source Nydus blobs, prepares work dirs, builds a streaming content store, imports or pulls the source, exports immediately for local targets, otherwise resolves manifests, optionally injects backend blob descriptors via `pushBlobFromBackend`, pushes target manifests, and pushes a rebuilt index for multi-platform sources. `pushBlobFromBackend` reads the manifest/config/bootstrap, runs nydus inspector output, deduplicates blob IDs, uploads each backend blob with chunked or normal push, prepends blob layers, updates config `RootFS.DiffIDs`, and writes new JSON descriptors.

State and persistence: uses temporary work dirs, provider content store state, transient `output.json`, unpacked bootstrap, and remote registry blobs/manifests. StreamContent minimizes local layer ingestion.

Dependencies and integration points: containerd images/content/remotes/compression, acceleration-service remote/platform utilities, nydus checker builder, backend readers/range readers, parser bootstrap detection, and provider push/pull/import/export.

Risks and test signals: plain HTTP retry is heuristic. Source/target identical refs collapse insecure settings. Manifest/config rewrite correctness and chunked push behavior are high-impact areas. Semaphore acquisition ignores returned errors.
<!-- END_FILE_RESEARCH: sources/cloud-native/nydus/contrib/nydusify/pkg/copier/copier.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/nydus/contrib/nydusify/pkg/copier/copier_test.go -->
# sources/cloud-native/nydus/contrib/nydusify/pkg/copier/copier_test.go

Purpose: unit coverage for copier helper behavior and early Copy error paths.

Important APIs under test: `getPlatform`, `getLocalPath`, `hosts`, `Copy`, and `pushBlobFromBackend` media type validation.

Control flow and state: tests validate default and explicit platform formatting, `file://` detection and absolutization, host credential/insecure mapping, unsupported backend type errors, invalid platform parsing, invalid source references, and unsupported media types for backend blob injection.

Dependencies and integration points: containerd platform formatting, Harbor remote credential function type, OCI descriptors, digest helpers, and local filesystem path handling.

Risks and test signals: tests document that `file://` with an empty suffix maps to the current working directory and that same source/target keys cause target insecurity to overwrite source insecurity in the map. The tests do not exercise successful registry copy, bootstrap inspection, backend blob upload, or multi-platform index push.
<!-- END_FILE_RESEARCH: sources/cloud-native/nydus/contrib/nydusify/pkg/copier/copier_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/nydus/contrib/nydusify/pkg/copier/store.go -->
# sources/cloud-native/nydus/contrib/nydusify/pkg/copier/store.go

Purpose: wraps a containerd `content.Store` so newly added remote backend blob descriptors can be reported as present even when they are not in the local content store.

Important APIs/types/functions: unexported `store`, `newStore`, and `Info`.

Control flow: `Info` delegates to the embedded base store. If the base store returns an error other than not found, the error is preserved. If the digest is not found, the wrapper searches its `remotes` descriptor slice and returns synthetic `content.Info` with digest and size for a matching remote descriptor; otherwise it returns the original not-found error.

State and persistence: the wrapper stores only an in-memory descriptor slice and delegates all other content-store methods through embedding. It does not persist or fetch actual content.

Dependencies and integration points: containerd content store and errdefs, OCI descriptors, and copier manifest push flow after `pushBlobFromBackend` prepends backend blobs.

Risks and test signals: synthetic info can make remote-only blobs visible to code that checks content existence, but read paths still depend on the underlying store/provider. Duplicate descriptors return the first match.
<!-- END_FILE_RESEARCH: sources/cloud-native/nydus/contrib/nydusify/pkg/copier/store.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/nydus/contrib/nydusify/pkg/copier/store_test.go -->
# sources/cloud-native/nydus/contrib/nydusify/pkg/copier/store_test.go

Purpose: validates the copier store wrapper's `Info` fallback semantics.

Important fixtures/APIs: `stubStore` implements enough of `content.Store` for tests; tests call `newStore` and `Info`.

Control flow and state: tests cover fallback to remote descriptors on base-store not found, preservation of unexpected base-store errors, preference for base-store info when present, not-found when neither base nor remote descriptors match, construction of the wrapper, multiple remote descriptors, and empty remote descriptor lists.

Dependencies and integration points: containerd content interfaces, errdefs, digest, and OCI descriptors.

Risks and test signals: coverage is narrow but precise for `Info`. Other embedded store methods are not customized and only rely on the underlying store. Tests do not validate behavior when remote descriptor sizes are zero or when duplicate remote descriptors exist.
<!-- END_FILE_RESEARCH: sources/cloud-native/nydus/contrib/nydusify/pkg/copier/store_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/nydus/contrib/nydusify/pkg/external/modctl/modctl.go -->
# sources/cloud-native/nydus/contrib/nydusify/pkg/external/modctl/modctl.go

Purpose: implements a filesystem-backed external snapshotter backend handler for model-control registry layout data, converting OCI model tar layers into backend blob/chunk metadata.

Important APIs/types/functions: constants for registry blob/repo paths and model media types, `Handler`, `blobInfo`, `chunk`, `Object`, `Option`, `NewHandler`, `GetOption`, `Handle`, `Backend`, `GetConfig`, `GetLayers`, `convertToBlobs`, `needIgnore`, and `readTarBlob`.

Control flow: `NewHandler` initializes manifest and blob maps from a local registry root. `Handle` ignores irrelevant files, opens a tar blob, extracts tar file offsets, computes object offsets with `backend.SplitObjectOffsets`, and returns chunks carrying blob digest/size/index, file path, chunk size, and compressed offsets. `Backend` returns a registry backend config with converted blobs.

State and persistence: state is held in `Handler` fields parsed from registry files. `mediaTypeChunkSizeMap` is package-global and mutated by `setWeightChunkSize`.

Dependencies and integration points: local Docker registry storage layout, OCI manifest descriptors, tar reader offsets, go-humanize byte parsing, and snapshotter external backend interfaces.

Risks and test signals: `Option.WeightChunkSize` has a misspelled JSON tag. Global chunk-size mutation can leak across handlers/tests. `GetOption` only accepts `host/namespace/image:tag` with exactly three slash parts, excluding deeper namespaces. Offset correctness depends on tar reader seek position semantics.
<!-- END_FILE_RESEARCH: sources/cloud-native/nydus/contrib/nydusify/pkg/external/modctl/modctl.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/nydus/contrib/nydusify/pkg/external/modctl/modctl_test.go -->
# sources/cloud-native/nydus/contrib/nydusify/pkg/external/modctl/modctl_test.go

Purpose: tests the local modctl handler, tar parsing, option parsing, blob conversion, backend output, and helper methods.

Important fixtures/APIs: `MockReadSeeker`, `TestReadImageRefBlob`, `TestReadTarBlob`, `TestGetOption`, `TestHandle`, `TestModctlBackend`, `TestConvertToBlobs`, `TestExtractManifest`, `TestSetBlobsMap`, `TestSetWeightChunkSize`, `TestNewHandler`, `TestInitHandler`, `TestChunkMethods`, `TestGetChunkSizeByMediaType`, `TestGetConfig`, `TestGetLayers`, and `TestNeedIgnore`.

Control flow and state: tests build in-memory tar files, temporary registry-like blob paths, and handlers with preloaded blob maps. Gomonkey patches initialization in some constructor tests. `TestReadImageRefBlob` is environment-gated by `NYDUS_MODEL_IMAGE_REF` and exercises real remote model images.

Dependencies and integration points: tar archive format, local `/tmp` files in some tests, gomonkey monkey-patching, model provider remote, snapshotter external backend structs, humanize parsing, and OCI digests.

Risks and test signals: local tests cover many edge cases, but several use fixed `/tmp/test` paths and global chunk-size map state. Real-image coverage is optional. Tests validate offset expectations for small tar entries and confirm invalid CRC annotation JSON is rejected in the remote path indirectly.
<!-- END_FILE_RESEARCH: sources/cloud-native/nydus/contrib/nydusify/pkg/external/modctl/modctl_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/nydus/contrib/nydusify/pkg/external/modctl/remote.go -->
# sources/cloud-native/nydus/contrib/nydusify/pkg/external/modctl/remote.go

Purpose: remote-image variant of modctl handling, reading model layer tar contents directly from a registry and producing external backend plus file attribute metadata.

Important APIs/types/functions: `RemoteInterface`, `RemoteHandler`, `FileCrcList`, `FileCrcInfo`, `NewRemoteHandler`, `initRemoteHandler`, `Handle`, `GetModelConfig`, `GetLayers`, `setManifest`, `backend`, `handle`, and `hackFileWrapper`.

Control flow: constructor creates a default remote and initializes the manifest. `Handle` processes manifest layers concurrently with limit 10 and five retries per layer, accumulating file attributes under a mutex. `handle` obtains a `ReadSeekCloser` for a layer, parses tar file offsets, reads optional CRC annotations, applies environment-controlled file mode hacks, and maps files to blob indexes/digests/sizes/chunk sizes. `GetModelConfig` pulls and unmarshals model config.

State and persistence: handler stores manifest and converted blob metadata in memory. It reads remote registry data only; no durable local files are written. `HACK_FILE` and `HACK_MODE` environment variables mutate emitted file modes.

Dependencies and integration points: provider default remotes, CloudNativeAI model spec, snapshotter external backend attributes, tar parsing shared with local modctl, retry helpers, logrus, and OCI annotations.

Risks and test signals: the goroutine loop closes over `idx` and `layer`; modern Go per-iteration semantics reduce risk, but compatibility matters. `io.Copy` result in `setManifest` is not checked. File attribute ordering can vary due to concurrent append.
<!-- END_FILE_RESEARCH: sources/cloud-native/nydus/contrib/nydusify/pkg/external/modctl/remote.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/nydus/contrib/nydusify/pkg/external/modctl/remote_test.go -->
# sources/cloud-native/nydus/contrib/nydusify/pkg/external/modctl/remote_test.go

Purpose: tests remote modctl handling using mocked registry remotes and in-memory tar data.

Important fixtures/APIs: `MockRemote`, local `readSeekCloser`, and tests for `RemoteHandler.Handle`, `GetModelConfig`, `setManifest`, `backend`, `NewRemoteHandler`, `initRemoteHandler`, `hackFileWrapper`, and `GetLayers`.

Control flow and state: the main handle test builds an in-memory tar with three files, attaches CRC annotations, and verifies emitted file attributes and backend metadata. It then supplies invalid CRC JSON and expects an error. Constructor tests monkey-patch default remote creation and initialization.

Dependencies and integration points: gomonkey, provider and remote packages, model spec JSON, snapshotter backend structs, OCI descriptors, tar archive readers, and environment variables for hack mode.

Risks and test signals: coverage confirms CRC propagation and invalid annotation rejection. It does not validate concurrent ordering determinism or plain HTTP fallback behavior. Some mocks omit methods not used by the tested path, so interface drift may only be caught at compile time.
<!-- END_FILE_RESEARCH: sources/cloud-native/nydus/contrib/nydusify/pkg/external/modctl/remote_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/nydus/contrib/nydusify/pkg/hook/hook.go -->
# sources/cloud-native/nydus/contrib/nydusify/pkg/hook/hook.go

Purpose: defines an optional HashiCorp go-plugin hook mechanism for invoking external logic before and after manifest push operations.

Important APIs/types/functions: `Blob`, `Info`, `Hook`, RPC client/server adapters, `Plugin`, global `Caller`, handshake config, `NewPlugin`, `Init`, and `Close`.

Control flow: package init sets `hookPluginPath` from `NYDUS_HOOK_PLUGIN_PATH` if present. `NewPlugin` serves an implementation under plugin key `hook`. `Init` is idempotent when `Caller` is already set, skips missing plugin binaries, creates a plugin client for an executable path, dispenses the hook implementation, and assigns it to global `Caller`. `Close` kills the plugin client if present.

State and persistence: global mutable state includes plugin path, plugin client, and caller implementation. Hook info carries bootstrap path, source/target refs, and blob IDs/sizes; no persistence is performed by this package.

Dependencies and integration points: `net/rpc`, HashiCorp go-plugin/hclog, `os/exec`, logrus, environment configuration, and pack/conversion push workflows that call `Caller`.

Risks and test signals: global state is process-wide and not synchronized. Failed client creation logs and returns silently, which makes hooks best-effort. Plugin executable trust and handshake configuration are operational concerns.
<!-- END_FILE_RESEARCH: sources/cloud-native/nydus/contrib/nydusify/pkg/hook/hook.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/nydus/contrib/nydusify/pkg/hook/hook_test.go -->
# sources/cloud-native/nydus/contrib/nydusify/pkg/hook/hook_test.go

Purpose: validates hook RPC adapters, plugin wrapper construction, initialization no-op paths, environment path behavior, and RPC round trips.

Important fixtures/APIs: `fakeHook`, `RPCServer.BeforePushManifest`, `RPCServer.AfterPushManifest`, `Plugin.Server`, `Plugin.Client`, `Init`, `Close`, and `RPC` client methods.

Control flow and state: tests preserve and restore global `Caller`, `hookPluginPath`, and `client`. They validate that initialized callers prevent plugin loading, missing paths leave `Caller` nil, stat errors are logged without panics, and a net.Pipe RPC server/client can dispatch before/after calls and propagate hook errors.

Dependencies and integration points: net/rpc, net.Pipe, go-plugin mux broker types, testify require, and process-global hook state.

Risks and test signals: tests do not execute a real external plugin process, so handshake, process startup, and binary compatibility are not covered. They do document the silent no-op behavior for absent hook binaries.
<!-- END_FILE_RESEARCH: sources/cloud-native/nydus/contrib/nydusify/pkg/hook/hook_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/nydus/contrib/nydusify/pkg/metrics/fileexporter/fileexporter.go -->
# sources/cloud-native/nydus/contrib/nydusify/pkg/metrics/fileexporter/fileexporter.go

Purpose: provides a simple metrics exporter that writes the current nydusify Prometheus registry to a textfile.

Important APIs/types/functions: `FileExporter`, `New`, and `Export`.

Control flow: `New` records the target file name. `Export` calls `prometheus.WriteToTextfile` with that name and the package-global `metrics.Registry`.

State and persistence: output is persisted to the filesystem path supplied to `New`. The exporter does not hold metric state itself; it depends on the global registry from `pkg/metrics`.

Dependencies and integration points: Prometheus client_golang textfile export and nydusify metrics registration.

Risks and test signals: `Export` ignores the returned error from `WriteToTextfile`, so callers cannot detect unwritable paths or nil registry failures. There is no locking around registry access beyond Prometheus internals.
<!-- END_FILE_RESEARCH: sources/cloud-native/nydus/contrib/nydusify/pkg/metrics/fileexporter/fileexporter.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/nydus/contrib/nydusify/pkg/metrics/fileexporter/fileexporter_test.go -->
# sources/cloud-native/nydus/contrib/nydusify/pkg/metrics/fileexporter/fileexporter_test.go

Purpose: verifies that the file exporter writes Prometheus metrics to disk.

Important APIs under test: `New` and `FileExporter.Export`.

Control flow and state: the test creates a fresh Prometheus registry, registers and increments a counter, installs it into `metrics.Registry`, exports to a temporary file, reads the file back, and asserts that the counter name is present.

Dependencies and integration points: Prometheus registry/counter APIs, the global metrics registry, temporary filesystem output, and testify require.

Risks and test signals: the test validates the happy path only. It does not cover unwritable paths or nil registry behavior, matching the implementation's error-ignoring behavior.
<!-- END_FILE_RESEARCH: sources/cloud-native/nydus/contrib/nydusify/pkg/metrics/fileexporter/fileexporter_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/nydus/contrib/nydusify/pkg/metrics/metrics.go -->
# sources/cloud-native/nydus/contrib/nydusify/pkg/metrics/metrics.go

Purpose: defines nydusify conversion metrics and a one-time registration/export hook.

Important APIs/types/functions: `Exporter`, metric key constants, global counter vectors, `Register`, `Export`, `ConversionDuration`, `ConversionSuccessCount`, `ConversionFailureCount`, `StoreCacheDuration`, and `sinceInSeconds`.

Control flow: `Register` uses `sync.Once` to create a new Prometheus registry, register all counter vectors, and store the exporter. Recorder functions add elapsed seconds or increment counters with labels. `Export` calls the registered exporter when present.

State and persistence: metrics live in global Prometheus counter vectors and a global `Registry`. Registration is one-shot per process unless tests reset internals. The exporter determines persistence, commonly the file exporter.

Dependencies and integration points: Prometheus client_golang, conversion and cache workflows that record timings/counts, and file/exporter implementations.

Risks and test signals: `sync.Once` prevents reconfiguration after first register. Labels include source references and failure reasons, which may increase cardinality. Duration is represented as a counter rather than histogram/summary, limiting distribution analysis.
<!-- END_FILE_RESEARCH: sources/cloud-native/nydus/contrib/nydusify/pkg/metrics/metrics.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/nydus/contrib/nydusify/pkg/metrics/metrics_test.go -->
# sources/cloud-native/nydus/contrib/nydusify/pkg/metrics/metrics_test.go

Purpose: validates metrics registration/export and individual recorder functions.

Important fixtures/APIs: `mockExporter`, `resetMetricsForTest`, `Register`, `Export`, and all metric recorder functions.

Control flow and state: tests reset global registry, exporter, `sync.Once`, and counter vectors. They verify only the first exporter is registered, `Export` invokes it once, nil exporter is tolerated, and counters are updated with expected label values.

Dependencies and integration points: Prometheus `testutil.ToFloat64`, sync.Once, time-based duration calculations, and testify require.

Risks and test signals: tests prove global reset is needed for deterministic unit tests. They do not assert registry text output or high-cardinality behavior.
<!-- END_FILE_RESEARCH: sources/cloud-native/nydus/contrib/nydusify/pkg/metrics/metrics_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/nydus/contrib/nydusify/pkg/optimizer/builder.go -->
# sources/cloud-native/nydus/contrib/nydusify/pkg/optimizer/builder.go

Purpose: wraps the external `nydus-image optimize` command used to build an optimized bootstrap and prefetch blob.

Important APIs/types/functions: package logger, `isSignalKilled`, `BuildOption`, `outputJSON`, and `Build`.

Control flow: `Build` constructs optimize arguments from prefetch file, bootstrap, output blob dir, output bootstrap, and output JSON paths. For `localfs` it passes `--blob-dir`; otherwise it passes backend type/config. It optionally runs under a timeout context, streams stdout/stderr to logrus, reads the output JSON, unmarshals blob IDs, and returns the last blob ID as the prefetch blob.

State and persistence: outputs are written by the external command into configured blob/bootstrap/output JSON paths. No internal persistence exists beyond reading `OutputJSONPath`.

Dependencies and integration points: `os/exec`, context timeouts, logrus, JSON output contract from `nydus-image`, and optimizer `Optimize`.

Risks and test signals: if `output.Blobs` is missing or empty, indexing the last element panics. Timeout detection is string-based on `"signal: killed"`. Backend config is passed on command line, which can expose secrets in process listings/logs.
<!-- END_FILE_RESEARCH: sources/cloud-native/nydus/contrib/nydusify/pkg/optimizer/builder.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/nydus/contrib/nydusify/pkg/optimizer/optimizer.go -->
# sources/cloud-native/nydus/contrib/nydusify/pkg/optimizer/optimizer.go

Purpose: optimizes an existing Nydus image by creating and pushing a new prefetch blob, bootstrap layer, config, and manifest.

Important APIs/types/functions: `Opt`, `BuildInfo`, `File`, `hosts`, `remoter`, `makeDesc`, `packToTar`, `getOriginalBlobLayers`, `fetchBlobs`, `Optimize`, `pushBlob`, `pushNewBootstrap`, `pushConfig`, and `pushNewImage`.

Control flow: `Optimize` parses the source Nydus image for the host arch, prepares work dirs, optionally fetches localfs blobs, pulls and unpacks the source bootstrap, invokes `Build`, then pushes a new image. Push flow uploads the prefetch blob, packs optimized bootstrap plus prefetch file into a tar and gzip layer, computes compressed digest and uncompressed diffID, rewrites config RootFS diff IDs, then writes and pushes a manifest containing original Nydus blobs plus the new prefetch blob and bootstrap.

State and persistence: uses temporary build directories, blob directories, generated bootstrap/tar/tar.gz/output JSON files, and remote registry uploads. Source parser and remoter hold registry state.

Dependencies and integration points: provider remote, parser, converter provider for localfs blob preparation, nydus-image optimize, containerd local readers/content readers, OCI descriptors, gzip/tar, and committer ref validation.

Risks and test signals: annotation map from old bootstrap is reused and mutated, which can alias source manifest state. Missing bootstrap/prefetch files fail late. Push retry is inconsistent across blob/config/bootstrap/manifest.
<!-- END_FILE_RESEARCH: sources/cloud-native/nydus/contrib/nydusify/pkg/optimizer/optimizer.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/nydus/contrib/nydusify/pkg/optimizer/optimizer_test.go -->
# sources/cloud-native/nydus/contrib/nydusify/pkg/optimizer/optimizer_test.go

Purpose: unit tests for optimizer helpers and external builder argument construction.

Important fixtures/APIs: fake optimizer shell script helpers, `makeDesc`, `packToTar`, `getOriginalBlobLayers`, `isSignalKilled`, `Build`, `hosts`, `remoter`, and uncompressed tar packing.

Control flow and state: tests create fake executable scripts that record arguments and write output JSON. They verify localfs vs remote backend flags, invalid JSON errors, and documented panics for missing/empty blob lists. Tar tests inspect directory and file entries. Remoter tests validate reference handling.

Dependencies and integration points: temporary shell executables, OCI descriptors/digests, parser image structs, Nydus utility media types, gzip/tar readers, filesystem temp dirs, and Docker reference validation through `remoter`.

Risks and test signals: tests explicitly capture panic behavior for empty output JSON, indicating a known robustness gap. Full `Optimize` and remote push sequencing are not covered with mocks here.
<!-- END_FILE_RESEARCH: sources/cloud-native/nydus/contrib/nydusify/pkg/optimizer/optimizer_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/nydus/contrib/nydusify/pkg/packer/artifact.go -->
# sources/cloud-native/nydus/contrib/nydusify/pkg/packer/artifact.go

Purpose: centralizes local artifact path construction for packer bootstrap, blob, and `output.json` files.

Important APIs/types/functions: `Artifact`, `NewArtifact`, `bootstrapPath`, `blobFilePath`, `outputJSONPath`, and `ensureOutputDir`.

Control flow: `NewArtifact` initializes an artifact with a user-provided or default output directory and ensures the directory exists. `bootstrapPath` preserves file names with extensions or appends `.meta`. `blobFilePath` returns digest-named blobs when requested, otherwise replaces existing extension with `.blob` or appends `.blob`.

State and persistence: creates the output directory on disk with mode `0755`. It does not create artifact files itself.

Dependencies and integration points: packer build/push flows, path utilities, and nydus build output contracts.

Risks and test signals: extension-based path decisions mean image names containing dots are treated as explicit file names. Default output dir is relative, which depends on caller working directory.
<!-- END_FILE_RESEARCH: sources/cloud-native/nydus/contrib/nydusify/pkg/packer/artifact.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/nydus/contrib/nydusify/pkg/packer/artifact_test.go -->
# sources/cloud-native/nydus/contrib/nydusify/pkg/packer/artifact_test.go

Purpose: verifies artifact path derivation and output directory creation.

Important APIs under test: `NewArtifact`, `bootstrapPath`, `blobFilePath`, `outputJSONPath`, and `ensureOutputDir`.

Control flow and state: tests cover default and explicit output directories, extension-preserving metadata paths, extension-to-blob rewriting, digest-named blob paths, `.` output JSON path behavior, and nested directory creation.

Dependencies and integration points: local filesystem and testify require.

Risks and test signals: confirms default `.nydus-build-output` creation and cleanup in one test. Does not cover permission errors or unusual path separators.
<!-- END_FILE_RESEARCH: sources/cloud-native/nydus/contrib/nydusify/pkg/packer/artifact_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/nydus/contrib/nydusify/pkg/packer/backend.go -->
# sources/cloud-native/nydus/contrib/nydusify/pkg/packer/backend.go

Purpose: defines packer backend configuration abstractions for OSS and S3 storage, separating metadata and blob object prefixes.

Important APIs/types/functions: `BackendConfig`, `OssBackendConfig`, `S3BackendConfig`, `rawMetaBackendCfg`, `rawBlobBackendCfg`, and `backendType`.

Control flow: each concrete config converts user-facing fields into JSON expected by the shared backend package. OSS emits simple string maps with `object_prefix` set to meta or blob prefix. S3 emits `backend.S3Config` JSON with endpoint, scheme, credentials, bucket, region, and prefix.

State and persistence: no state beyond config structs. Sensitive access keys are serialized into JSON byte slices for backend initialization and temporary config dumps.

Dependencies and integration points: packer pusher, backend factory, S3/OSS backend implementations, and compactor temp config creation.

Risks and test signals: JSON marshal errors are ignored, though these structs should marshal successfully. Secrets may be written to disk or command arguments by callers. Empty config fields are allowed and may fail only when backend clients initialize or upload.
<!-- END_FILE_RESEARCH: sources/cloud-native/nydus/contrib/nydusify/pkg/packer/backend.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/nydus/contrib/nydusify/pkg/packer/backend_test.go -->
# sources/cloud-native/nydus/contrib/nydusify/pkg/packer/backend_test.go

Purpose: validates OSS/S3 backend config JSON conversion and backend config parsing.

Important APIs under test: `rawMetaBackendCfg`, `rawBlobBackendCfg`, `backendType`, `ParseBackendConfigString`, and `ParseBackendConfig`.

Control flow and state: tests instantiate S3 and OSS configs, create backend clients from raw configs, unmarshal JSON to assert prefix and credential fields, verify empty OSS fields still marshal, and exercise supported/unsupported parsing paths.

Dependencies and integration points: shared backend factory, JSON decoding, and testify require.

Risks and test signals: tests cover config shape but not real cloud authentication or upload behavior. Empty-field tests confirm local validation is permissive.
<!-- END_FILE_RESEARCH: sources/cloud-native/nydus/contrib/nydusify/pkg/packer/backend_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/nydus/contrib/nydusify/pkg/packer/packer.go -->
# sources/cloud-native/nydus/contrib/nydusify/pkg/packer/packer.go

Purpose: builds Nydus artifacts from a source directory and optionally pushes metadata/blob artifacts to a configured backend.

Important APIs/types/functions: `Opt`, `Builder`, `Packer`, `BlobManifest`, `PackRequest`, `PackResult`, `New`, `getBlobsFromBootstrap`, `getChunkDictBlobs`, `getNewBlobsHash`, `dumpBlobBackendConfig`, `tryCompactParent`, `Pack`, `ensureNydusImagePath`, and `initLogger`.

Control flow: `New` initializes logger, artifacts, binary path, builder, and optional pusher. `Pack` optionally compacts a parent bootstrap, reads parent/chunk-dict blobs, runs the builder with rootfs/bootstrap/blob/output paths, finds the first newly generated blob from `output.json`, renames it to digest form when needed, returns local paths or pushes via `Pusher`. Parent compaction dumps secret backend config temporarily and zeroes/removes it afterward.

State and persistence: output directory contains bootstrap, blob, output JSON, temporary backend config, and possible compacted bootstrap. Pusher writes remote backend artifacts.

Dependencies and integration points: nydus-image binary, build package, checker inspector, compactor, backend configs, local filesystem, and logrus.

Risks and test signals: `ensureNydusImagePath` only tries PATH fallback if a non-empty path was supplied. Blob detection chooses first blob not already known. Secret cleanup is best-effort. Push requires backend config.
<!-- END_FILE_RESEARCH: sources/cloud-native/nydus/contrib/nydusify/pkg/packer/packer.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/nydus/contrib/nydusify/pkg/packer/packer_test.go -->
# sources/cloud-native/nydus/contrib/nydusify/pkg/packer/packer_test.go

Purpose: exercises packer construction, local pack flow, push flow with mocked backend, chunk-dict parsing, compaction skips, binary lookup errors, blob hash parsing, logger creation, and backend config cleanup.

Important fixtures/APIs: `mockBuilder`, `setUpTmpDir`, `copyFile`, `New`, `Pack`, `getNewBlobsHash`, `getChunkDictBlobs`, `tryCompactParent`, `ensureNydusImagePath`, `getBlobsFromBootstrap`, and `dumpBlobBackendConfig`.

Control flow and state: tests create fake `nydus-image` files under `testdata`, copy canned `output.json`, replace the builder with a mock, inject mocked push backends, and assert returned local/remote paths. Cleanup tests verify temporary backend config files are zeroed/removed without panic.

Dependencies and integration points: testify mock/require, local filesystem, testdata JSON, OCI descriptors, packer pusher, logrus.

Risks and test signals: tests cover many error edges but use relative `testdata/TestName` directories. Successful compactor execution and real inspector output are not covered.
<!-- END_FILE_RESEARCH: sources/cloud-native/nydus/contrib/nydusify/pkg/packer/packer_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/nydus/contrib/nydusify/pkg/packer/pusher.go -->
# sources/cloud-native/nydus/contrib/nydusify/pkg/packer/pusher.go

Purpose: uploads local packer metadata and blob artifacts to OSS/S3-like backends.

Important APIs/types/functions: `Pusher`, `PushRequest`, `PushResult`, `NewPusherOpt`, `NewPusher`, `Push`, `ParseBackendConfig`, and `ParseBackendConfigString`.

Control flow: constructor validates output dir and initializes separate meta and blob backend clients from corresponding raw configs. `Push` uploads parent blobs first without force, uploads the new blob when present, finalizes blob backend, uploads bootstrap metadata with force, finalizes meta backend, and returns first URL from each descriptor. On any error it attempts cancel finalization for both backends.

State and persistence: reads files from `Artifact` paths and persists objects to remote backends. Backend clients hold upload state until finalized.

Dependencies and integration points: shared backend factory, packer artifacts, JSON config files/strings, context background, logrus, and OSS/S3 config structs.

Risks and test signals: mock backend `Upload` tests assume non-nil descriptors. Parent blob uploads use digest-named files and size zero. Context is not caller-controlled and lacks timeout. Finalize error handling can mask upload cleanup details.
<!-- END_FILE_RESEARCH: sources/cloud-native/nydus/contrib/nydusify/pkg/packer/pusher.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/nydus/contrib/nydusify/pkg/packer/pusher_test.go -->
# sources/cloud-native/nydus/contrib/nydusify/pkg/packer/pusher_test.go

Purpose: validates backend config parsing and pusher upload sequencing with mocked backends.

Important fixtures/APIs: `mockBackend`, `ParseBackendConfig`, `ParseBackendConfigString`, `Pusher.Push`, and `NewPusher`.

Control flow and state: tests parse OSS/S3 configs from file and strings, reject unsupported backend types and invalid JSON, simulate pushing meta/blob files with URL descriptors, skip blob upload when blob ID is empty, upload parent blobs, and check constructor validation for output directories and backend initialization.

Dependencies and integration points: testify mock, local testdata output/backend config, OCI descriptors, backend interface types, and logrus.

Risks and test signals: tests do not simulate upload or finalize failures because mock `Finalize` always succeeds and `Upload` always returns nil error. They validate URL extraction and high-level ordering through mock expectations.
<!-- END_FILE_RESEARCH: sources/cloud-native/nydus/contrib/nydusify/pkg/packer/pusher_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/nydus/contrib/nydusify/pkg/packer/testdata/backend-config.json -->
# sources/cloud-native/nydus/contrib/nydusify/pkg/packer/testdata/backend-config.json

Purpose: test fixture containing an OSS backend configuration.

Important fields: `endpoint`, `access_key_id`, `access_key_secret`, `bucket_name`, `meta_prefix`, and `blob_prefix`.

Control flow and state: parsed by packer pusher tests through `ParseBackendConfig("oss", ...)` and expected to produce an `OssBackendConfig` with metadata prefix `test/` and empty blob prefix.

Dependencies and integration points: packer backend config parser and OSS backend config raw JSON generation.

Risks and test signals: contains placeholder credentials and should stay test-only. It validates field names used by user-supplied backend config files.
<!-- END_FILE_RESEARCH: sources/cloud-native/nydus/contrib/nydusify/pkg/packer/testdata/backend-config.json -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/nydus/contrib/nydusify/pkg/packer/testdata/output.json -->
# sources/cloud-native/nydus/contrib/nydusify/pkg/packer/testdata/output.json

Purpose: test fixture modeling `nydus-image` build output consumed by packer.

Important fields: `version`, `blobs`, and nested `trace` metrics. The `blobs` array contains the digest-like blob hash used by tests.

Control flow and state: `getNewBlobsHash` reads this file and returns the first blob hash not present in parent/chunk-dict lists. Pack and pusher tests copy it to temporary output dirs to drive blob rename/push behavior.

Dependencies and integration points: packer `BlobManifest` only consumes `blobs`; trace content is ignored by current code but represents realistic builder output.

Risks and test signals: fixture confirms parser tolerates extra fields. It has a single blob, so multi-blob ordering behavior is covered only by separate generated JSON in tests.
<!-- END_FILE_RESEARCH: sources/cloud-native/nydus/contrib/nydusify/pkg/packer/testdata/output.json -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/nydus/contrib/nydusify/pkg/parser/parser.go -->
# sources/cloud-native/nydus/contrib/nydusify/pkg/parser/parser.go

Purpose: parses OCI/Nydus image references into manifest, config, index, and categorized OCI/Nydus image objects.

Important APIs/types/functions: `Parser`, `Image`, `Parsed`, `New`, `FindNydusBootstrapDesc`, pull helpers, `parseImage`, `PullNydusBootstrap`, `matchImagePlatform`, and `Parse`.

Control flow: `Parse` resolves the remote descriptor, then handles single manifests or indexes. Single manifests are pulled once and classified as Nydus when the last layer is a gzip layer annotated as Nydus bootstrap. Indexes are searched for matching linux arch; descriptors are classified via artifact type, platform features, or manifest inspection. `parseImage` pulls config and enforces OS/arch unless ignoreArch is enabled for single manifests.

State and persistence: parser stores the remote and interested arch. It does not cache fetched JSON beyond returned parsed structs.

Dependencies and integration points: remote registry wrapper, containerd media types, OCI specs, nydus utility annotations/platforms, and optimizer/provider flows needing parsed images.

Risks and test signals: index parsing can overwrite earlier matches with later descriptors. Images with no matching platform return parsed results with nil images instead of a direct error. Certificate errors only trigger a warning hint.
<!-- END_FILE_RESEARCH: sources/cloud-native/nydus/contrib/nydusify/pkg/parser/parser.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/nydus/contrib/nydusify/pkg/parser/parser_test.go -->
# sources/cloud-native/nydus/contrib/nydusify/pkg/parser/parser_test.go

Purpose: deterministic unit tests for parser classification, platform matching, bootstrap detection, and parse error paths.

Important fixtures/APIs: `testResolver`, `newTestParser`, `New`, `FindNydusBootstrapDesc`, `matchImagePlatform`, `parseImage`, `PullNydusBootstrap`, and `Parse`.

Control flow and state: tests build mocked remotes whose resolver/fetcher return JSON by descriptor digest. They validate unsupported arch rejection, bootstrap layer annotation detection, platform matching, ignored arch mismatch for single manifests, bootstrap pulling, certificate resolve errors, single-manifest OCI mode, index classification via artifact type, no matching arch, manifest pull failure, and config missing architecture errors.

Dependencies and integration points: containerd remotes, OCI image/index/manifest JSON, digest helpers, nydus utility constants, and the remote package.

Risks and test signals: tests cover classification well without registry dependency. They do not cover descriptor platform feature-based Nydus detection directly or multiple matching descriptor precedence.
<!-- END_FILE_RESEARCH: sources/cloud-native/nydus/contrib/nydusify/pkg/parser/parser_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/nydus/contrib/nydusify/pkg/provider/logger.go -->
# sources/cloud-native/nydus/contrib/nydusify/pkg/provider/logger.go

Purpose: defines progress logging abstraction and a default logrus implementation for conversion/provider workflows.

Important APIs/types/functions: `LoggerFields`, `ProgressLogger`, `defaultLogger`, `defaultLogger.Log`, and `DefaultLogger`.

Control flow: `Log` ensures a non-nil field map, logs the start message, records the current time, and returns a closure. The closure adds a `"Time"` field with elapsed duration, logs the same message again, and returns its input error unchanged.

State and persistence: logging state is transient. The closure mutates the provided `fields` map by adding `"Time"`.

Dependencies and integration points: logrus and callers that use deferred completion logging around conversion steps.

Risks and test signals: mutating caller-provided fields can affect reused maps. The logger does not encode success/failure beyond returning the error; callers must include error fields themselves if desired.
<!-- END_FILE_RESEARCH: sources/cloud-native/nydus/contrib/nydusify/pkg/provider/logger.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/nydus/contrib/nydusify/pkg/provider/provider_test.go -->
# sources/cloud-native/nydus/contrib/nydusify/pkg/provider/provider_test.go

Purpose: tests provider package defaults for platform parsing, remote construction/auth, source providers/layers, and logging.

Important APIs under test: `ExtractOsArch`, `newDefaultClient`, `DefaultRemoteWithAuth`, `DefaultRemote`, `defaultSourceProvider` methods, `defaultSourceLayer` getters, `DefaultSource`, `defaultLogger.Log`, and `DefaultLogger`.

Control flow and state: tests validate valid/invalid platform strings, TLS client settings, base64 auth parsing and rejection, Docker Hub auth host mapping, source layer ChainID/ParentChainID construction, mismatched layer/diffID errors, parser integration branches for nydus-only and OCI images, and logger closure duration mutation.

Dependencies and integration points: gomonkey patches for parser/remote construction, HTTP transport settings, Docker config credentials, OCI identity ChainID, digest helpers, and nydus utility arch constants.

Risks and test signals: tests avoid real registry pulls/mounts, so `defaultSourceLayer.Mount` is not exercised. Auth parsing splits on `:`, so passwords containing colons are rejected and covered by tests.
<!-- END_FILE_RESEARCH: sources/cloud-native/nydus/contrib/nydusify/pkg/provider/provider_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/nydus/contrib/nydusify/pkg/provider/remote.go -->
# sources/cloud-native/nydus/contrib/nydusify/pkg/provider/remote.go

Purpose: constructs default registry remotes backed by containerd Docker resolver/auth clients.

Important APIs/functions: `newDefaultClient`, `withCredentialFunc`, `withRemote`, `DefaultRemote`, and `DefaultRemoteWithAuth`.

Control flow: `newDefaultClient` configures a short-lived HTTP transport with optional TLS skip verify, disabled keepalives, and HTTP/2 disabled via `TLSNextProto`. `withRemote` creates a resolver function that configures Docker registries with authorizer, client, and plain HTTP toggled by retry state. `DefaultRemote` reads Docker config credentials, mapping Docker Hub's resolver host to `https://index.docker.io/v1/`. `DefaultRemoteWithAuth` decodes base64 `username:password` and supplies fixed credentials.

State and persistence: no durable state; remotes hold reference and resolver factory. Docker config is read when credential callback is invoked.

Dependencies and integration points: containerd docker resolver, Docker CLI config loading, HTTP/TLS, base64 auth, and the local `remote.Remote` wrapper.

Risks and test signals: `InsecureSkipVerify` is used for insecure mode. Base64 auth cannot contain additional colons. Plain HTTP is controlled per resolver request from `remote.Remote` state.
<!-- END_FILE_RESEARCH: sources/cloud-native/nydus/contrib/nydusify/pkg/provider/remote.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/nydus/contrib/nydusify/pkg/provider/source.go -->
# sources/cloud-native/nydus/contrib/nydusify/pkg/provider/source.go

Purpose: provides default source image abstraction for build systems that need manifest, config, and mountable OCI source layers.

Important APIs/types/functions: `SourceLayer`, `SourceProvider`, `defaultSourceProvider`, `defaultSourceLayer`, `Manifest`, `Config`, `Layers`, `Mount`, getters, `ExtractOsArch`, and `DefaultSource`.

Control flow: `DefaultSource` validates `linux/arch`, creates a parser, parses the remote image, rejects Nydus-only or missing OCI images, and returns a provider for the OCI image. `Layers` pairs manifest layers with config diff IDs, computes ChainIDs incrementally, and creates layer objects with mount dirs keyed by ChainID. `Mount` pulls a layer with retry, unpacks targz to the mount dir, and returns an `oci-directory` mount plus cleanup function.

State and persistence: layers unpack into work-dir subdirectories and are removed by the returned cleanup. Provider stores parsed image and remote pointer.

Dependencies and integration points: parser, remote registry pull, OCI identity ChainID, containerd mount type, nydus utils unpack/retry, and buildkit-like source consumers.

Risks and test signals: layer/diffID mismatch is rejected. Mount cleanup depends on caller invoking the returned function. Only Linux amd64/arm64-like supported arches are accepted.
<!-- END_FILE_RESEARCH: sources/cloud-native/nydus/contrib/nydusify/pkg/provider/source.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/nydus/contrib/nydusify/pkg/remote/reader.go -->
# sources/cloud-native/nydus/contrib/nydusify/pkg/remote/reader.go

Purpose: adapts containerd remote fetchers and the local `Remote` wrapper into content `ReaderAt` and `ReadSeekCloser` interfaces.

Important APIs/types/functions: `FromFetcher`, `fetchedProvider`, `readerAt`, `readerAt.ReadAt`, `readerAt.Size`, `Remote.ReaderAt`, and `Remote.ReadSeekCloser`.

Control flow: `FromFetcher` returns a content provider whose `ReaderAt` fetches a descriptor and wraps the returned reader. `readerAt.ReadAt` seeks when the requested offset differs from its tracked offset, then reads until the caller buffer is full or an error occurs. `Remote.ReaderAt` and `ReadSeekCloser` derive the request ref, instantiate a fresh resolver/fetcher, and either wrap fetched content or require the returned reader to implement `io.ReadSeekCloser`.

State and persistence: `readerAt` tracks current offset and size in memory. No data is persisted.

Dependencies and integration points: containerd content/remotes, OCI descriptors, and registry fetchers that support seeking/range reads.

Risks and test signals: `ReadAt` fails if the fetcher returns a non-seekable reader and a non-current offset is requested. The offset state is not concurrency-safe; `ReaderAt` should not be shared across concurrent reads without synchronization.
<!-- END_FILE_RESEARCH: sources/cloud-native/nydus/contrib/nydusify/pkg/remote/reader.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/nydus/contrib/nydusify/pkg/remote/reader_test.go -->
# sources/cloud-native/nydus/contrib/nydusify/pkg/remote/reader_test.go

Purpose: tests remote resolver/fetcher/pusher wrappers, reader adapters, plain HTTP toggling, request references, and push behavior.

Important fixtures/APIs: `MockResolver`, `mockReadSeekCloeser`, `readSeekCloser`, `readerAt.ReadAt`, `Remote.ReadSeekCloser`, `Remote.Resolve`, `Remote.Pull`, `Remote.ReaderAt`, `Remote.Push`, `MaybeWithHTTP`, `WithHTTP`, `namedReference`, `requestRef`, and `FromFetcher`.

Control flow and state: tests create remotes with mock resolver factories, assert refs passed to resolver methods, fetch in-memory content, verify seeking reads, reject non-seekable readers, toggle HTTP when error strings contain the registry host, handle already-exists pushes as success, and ensure content writers commit on successful push.

Dependencies and integration points: containerd remotes/content interfaces, errdefs, digest, OCI descriptors, and testify.

Risks and test signals: coverage is comprehensive for wrapper mechanics but not for real registry auth/token expiry behavior. The typo `mockReadSeekCloeser` is test-local only.
<!-- END_FILE_RESEARCH: sources/cloud-native/nydus/contrib/nydusify/pkg/remote/reader_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/nydus/contrib/nydusify/pkg/remote/remote.go -->
# sources/cloud-native/nydus/contrib/nydusify/pkg/remote/remote.go

Purpose: wraps containerd remote resolver operations for resolving, pulling, and pushing OCI descriptors with reference normalization and plain HTTP retry state.

Important APIs/types/functions: `Remote`, `New`, `MaybeWithHTTP`, `WithHTTP`, `IsWithHTTP`, `namedReference`, `requestRef`, `Push`, `Pull`, and `Resolve`.

Control flow: `New` parses a normalized Docker reference. `requestRef` returns repository name for digest-addressed blob operations or tag-normalized reference for manifest operations. Each operation creates a fresh resolver from `resolverFunc` to avoid stale auth tokens. `Push` serializes concurrent pushes by containerd ref key using a sync.Map of mutexes, creates a pusher, treats already-exists as success, and streams content through `content.Copy`. `Pull` fetches descriptors, and `Resolve` resolves the tag reference.

State and persistence: `Remote` stores parsed reference, resolver factory, pushed mutex map, and `withHTTP` flag. Remote registry persistence happens through pusher/fetcher.

Dependencies and integration points: distribution/reference, containerd remotes/content, errdefs, OCI descriptors, provider remote constructors, parser, optimizer, and modctl.

Risks and test signals: `MaybeWithHTTP` relies on error-string host matching. The mutex map can grow with unique ref keys. Resolver factory must be safe to call repeatedly.
<!-- END_FILE_RESEARCH: sources/cloud-native/nydus/contrib/nydusify/pkg/remote/remote.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/nydus/contrib/nydusify/pkg/snapshotter/external/backend/backend.go -->
# sources/cloud-native/nydus/contrib/nydusify/pkg/snapshotter/external/backend/backend.go

Purpose: defines shared data contracts for external snapshotter backend generation and file/chunk metadata.

Important APIs/types/functions: `Backend`, `Config`, `Blob`, `BlobConfig`, `Result`, `FileAttribute`, `File`, `Handler`, `RemoteHanlder`, `Chunk`, and `SplitObjectOffsets`.

Control flow: handlers return backend configuration and chunks for files. Remote handlers return backend configuration plus file attributes. `SplitObjectOffsets` computes zero-based offsets for fixed-size chunks, returning empty for non-positive chunk size or zero total size, and including a final partial offset when needed.

State and persistence: structs are JSON-serializable where tagged and are used as metadata records; no persistence is implemented here.

Dependencies and integration points: modctl local/remote handlers, snapshotter external generator/walker code elsewhere, and external backend metadata layout.

Risks and test signals: `RemoteHanlder` is misspelled in the type name but part of the package API. `FileAttribute` lacks JSON tags, so encoding relies on default field names if used directly.
<!-- END_FILE_RESEARCH: sources/cloud-native/nydus/contrib/nydusify/pkg/snapshotter/external/backend/backend.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/nydus/contrib/nydusify/pkg/snapshotter/external/backend/backend_test.go -->
# sources/cloud-native/nydus/contrib/nydusify/pkg/snapshotter/external/backend/backend_test.go

Purpose: validates external backend metadata struct sizes and chunk offset splitting.

Important APIs under test: `Header`, `ChunkMeta`, `ObjectMeta`, and `SplitObjectOffsets`.

Control flow and state: `TestLayout` asserts the unsafe sizes of header and metadata structs match the on-disk layout assumptions. `TestSplitObjectOffsets` covers non-positive chunk size, zero total size, divisible totals, and final partial chunk offsets.

Dependencies and integration points: `unsafe.Sizeof`, reflect comparison, and testify require.

Risks and test signals: layout tests guard accidental struct changes that would break binary metadata compatibility. They do not validate `ChunkOndisk` size or object encoding details.
<!-- END_FILE_RESEARCH: sources/cloud-native/nydus/contrib/nydusify/pkg/snapshotter/external/backend/backend_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/nydus/contrib/nydusify/pkg/snapshotter/external/backend/layout.go -->
# sources/cloud-native/nydus/contrib/nydusify/pkg/snapshotter/external/backend/layout.go

Purpose: declares binary on-disk layout structs and constants for external backend metadata.

Important APIs/types/constants: `MetaMagic`, `MetaVersion`, `Header`, `ChunkMeta`, `ObjectMeta`, `ChunkOndisk`, `ObjectOffset`, and `ObjectOndisk`.

Control flow: no executable flow; the file defines fixed-size header/meta structures and variable-size object records. Comments describe section ordering: header, chunk metadata and entries, object metadata, optional object offsets, and object records.

State and persistence: these structs represent persisted metadata layout. `Header` is 4096 bytes, `ChunkMeta` and `ObjectMeta` are 256 bytes each, with reserved padding for future compatibility.

Dependencies and integration points: snapshotter external backend metadata writer/reader code and tests that assert layout sizes.

Risks and test signals: changing field order, types, or padding breaks on-disk compatibility. `ObjectOndisk` contains a slice and is not fixed-size directly; encoding code must handle its variable payload explicitly.
<!-- END_FILE_RESEARCH: sources/cloud-native/nydus/contrib/nydusify/pkg/snapshotter/external/backend/layout.go -->
