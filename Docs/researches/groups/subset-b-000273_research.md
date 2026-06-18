# Research: subset-b-000273

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/soci-snapshotter/integration/util_soci_test.go -->
# sources/cloud-native/soci-snapshotter/integration/util_soci_test.go

Purpose: integration-test helpers for building and validating SOCI indexes through the real `soci` CLI, `nerdctl`, and local content stores. It centralizes index creation options, SOCI index descriptor validation, local-store digesting, and prefetch artifact validation.

Important APIs/types/functions: `indexBuildConfig` models `soci create` flags such as span size, min layer size, content store type, namespace, rebuild-db, force, and prefetch files. Functional options include `withSpanSize`, `withMinLayerSize`, `withContentStoreType`, `withNamespace`, `withForceRecreateZtocs`, and `withPrefetchPaths`. `buildIndex` pulls the source image with nerdctl, optionally rebuilds the SOCI DB, runs `soci create`, and returns the digest from `soci index list`. `validateSociIndex` checks media type, artifact type, annotations, subject digest, blob count, layer inclusion, blob size, and digest. `getSociLocalStoreContentDigest`, `sociIndexFromDigest`, and `assertPrefetchArtifactCreated` support store-state and artifact inspection.

Control flow: callers prepare an `imageInfo`, layer selection options, and a shell. `buildIndex` canonicalizes options, performs the pull, runs SOCI create, and queries index state. Validation then reads descriptors from content-store paths and compares actual bytes against OCI digest metadata. Prefetch validation follows descriptor annotations back to the image manifest and fetches the prefetch blob for decoding.

State and persistence: the file mutates integration container state: containerd content store, SOCI content store, SOCI DB, and optional prefetch artifacts. Digest helpers intentionally hash files larger than ten bytes in the SOCI blob path, so small metadata files do not affect the content-state fingerprint.

Dependencies/integration points: uses `util/dockershell`, `nerdctl`, `soci`, `soci/store`, `config.DefaultContentStoreType`, containerd namespaces/platforms, OCI descriptors, opencontainers digest, and `cmp.Diff`. It expects the integration container to have binaries and content-store paths available.

Risks: the helpers depend on exact CLI output shape, default annotation strings, and local content-store layouts. `buildIndex` returns an empty digest on list failure rather than an error, so calling tests must check for empty string. Prefetch validation assumes one prefetch descriptor for a requested path and that layer annotations are present.

Test signals: this file is itself test support; downstream integration tests exercise these helpers by creating indexes, validating descriptors, comparing content-store blob hashes, and asserting prefetch artifacts decode to non-empty span lists.
<!-- END_FILE_RESEARCH: sources/cloud-native/soci-snapshotter/integration/util_soci_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/soci-snapshotter/integration/util_test.go -->
# sources/cloud-native/soci-snapshotter/integration/util_test.go

Purpose: broad integration-test harness for SOCI snapshotter tests. It builds Docker Compose environments, renders containerd and snapshotter configs, manages local test registries with TLS/basic auth, starts/restarts containerd and `soci-snapshotter-grpc`, fetches registry/content-store metadata, and provides image and config utility types.

Important APIs/types/functions: config template helpers include `getContainerdConfigToml`, `getCRIContainerdConfigToml`, `getSnapshotterConfigToml`, and many `snapshotterConfigOpt` setters for metrics, pull modes, prefetch, content store, concurrency, CRI keychain, and decompression settings. Environment helpers include `newSnapshotterBaseShell`, `newShellWithRegistry`, `rebootContainerd`, `stopContainerd`, `addConfig`, and `removeDirContents`. Image/registry helpers include `imageInfo`, `registryConfig`, `dockerhub`, `mirror`, `copyImage`, `getImageIndex`, `getManifestDigest`, `getReferrers`, `FetchContentByDigest`, and `readLayerTarFiles`.

Control flow: tests request a shell environment, optionally with a registry. The harness renders compose YAML, builds/starts containers, creates TLS certs and htpasswd files, installs trust anchors, writes config files into the container, starts containerd and snapshotter, waits for startup logs, then verifies a basic snapshotter prepare command. Registry helpers can mirror upstream images into the test registry, then content helpers resolve manifests and blobs for assertions.

State and persistence: this file creates temporary host directories for registry certs/config, writes files into test containers, manipulates `/var/lib/containerd`, `/var/lib/soci-snapshotter-grpc`, `/run/containerd`, and snapshotter sockets, and starts long-running processes. It also creates temporary Docker networks and cleanup functions that remove compose services and kill snapshotter processes.

Dependencies/integration points: depends heavily on Docker Compose wrappers, dockershell, `nerdctl`, `ctr`, `crictl`, `containerd`, `soci-snapshotter-grpc`, `trust`, `bcrypt`, TOML marshaling, OCI image-spec, containerd images/platforms, and project testutil helpers. Config templates account for both proxy-plugin and built-in snapshotter modes plus containerd 1.7 and 2.x CRI paths.

Risks: shell-driven tests are sensitive to image availability, host architecture, CLI output, process cleanup, mounted tmpfs behavior, and timing. The self-signed certificate path and registry host naming must remain consistent. Cleanup functions must avoid leaving mounts, sockets, and child processes behind. Config defaults intentionally start from a partially populated config, so future default changes can alter test behavior.

Test signals: although this is helper code, it is exercised by most integration tests. It has embedded assertions through `t.Fatal`, startup log monitoring, retry loops for registry login and snapshotter readiness, content digest parsing, overlay fallback metric parsing, and release of compose resources through returned cleanup functions.
<!-- END_FILE_RESEARCH: sources/cloud-native/soci-snapshotter/integration/util_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/soci-snapshotter/integration/ztoc_test.go -->
# sources/cloud-native/soci-snapshotter/integration/ztoc_test.go

Purpose: integration tests for the `soci ztoc` CLI. It verifies listing, info output, file extraction, shared-layer filtering, invalid inputs, and eStargz layer handling against real SOCI indexes and containerd/SOCI content stores.

Important APIs/types/functions: local JSON mirror types `Info` and `FileInfo` model `soci ztoc info` output. Tests include `TestSociZtocList`, `TestSociZtocInfo`, `TestSociZtocGetFile`, and `TestSociZtocWithEstargzLayers`. Helpers include `verifyZtocListing`, `dedupeZtocBlobs`, and `verifyInfoOutput`.

Control flow: tests start a snapshotter shell, reboot services, prepare SOCI indexes, then run `soci ztoc list` with all combinations of no filter, ztoc digest, image ref, and both filters. Info tests call `soci ztoc info`, unmarshal JSON, load the original ztoc from the content-store blob path, and compare fields. Get-file tests locate sample regular files per span, compare CLI output against contents extracted from the original gzip tar, and cover output-file mode. eStargz tests convert an image, push it through a registry, build a SOCI index, verify extraction from concatenated gzip members, push/pull the SOCI artifact, and assert FUSE mounting.

State and persistence: tests pull and convert images, write temporary output files, create registry-backed image references, push SOCI artifacts, remove images, and read blobs from containerd and SOCI content stores. eStargz coverage specifically persists converted OCI layers in the registry and validates later lazy-pull mounting.

Dependencies/integration points: integrates `soci` CLI, `nerdctl`, local registry helpers, `ztoc.Unmarshal`, OCI descriptors, digest parsing, gzip/tar readers, SOCI index annotations, content-store utilities, and containerd platforms. Uses Go 1.21 `slices` utilities for matching/deduplication.

Risks: tests depend on deterministic CLI table columns being discoverable by substring, prepared image sets containing regular files across spans, and exact JSON field order matching ztoc file metadata. `verifyZtocListing` checks length before deduping shared ztocs, so duplicate descriptor behavior must remain aligned with expected output semantics. Get-file stdout trimming assumes the CLI appends one newline.

Test signals: positive cases verify digest, size, layer annotations, info fields, file contents, eStargz extraction, push/pull path, and FUSE mount count. Negative cases cover invalid digest strings, missing ztocs, missing files, and unexpected ztoc filters.
<!-- END_FILE_RESEARCH: sources/cloud-native/soci-snapshotter/integration/ztoc_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/soci-snapshotter/internal/archive/compression/compression.go -->
# sources/cloud-native/soci-snapshotter/internal/archive/compression/compression.go

Purpose: configurable decompression stream registry for unpacking compressed image layers. It adapts containerd archive decompression interfaces so SOCI can invoke configured external decompressors for gzip and zstd media types.

Important APIs/types/functions: `DecompressStream` mirrors containerd's stream signature. `InitializeDecompressStreams` validates configured executable paths and registers stream functions for Docker gzip, OCI gzip, and OCI zstd media types. `GetDecompressStream` looks up a stream by layer media type. Internal types include `decompressionKey`, `readCloserWrapper`, `decompressor`, `gzipDecompressor`, `zstdDecompressor`, `decompress`, and `cmdStream`.

Control flow: initialization runs once via `sync.Once`; each configured algorithm is sanitized with `internal/os.SanitizeExecutablePath`, copied into a sanitized config, and mapped to one or more OCI/Docker media types. A returned stream starts an `exec.CommandContext`, connects input to stdin and stdout to an `io.Pipe`, and exposes a read closer whose close cancels the command context.

State and persistence: global mutable state is `decompressStreams`, `initDecompressors`, and `initDecompressorsErr`. Once initialization is attempted, later calls return the first result and do not reconfigure streams unless tests reset internals. Runtime state is an external decompressor process per stream invocation.

Dependencies/integration points: depends on `config.DecompressStream`, `internal/os` path sanitization, containerd archive compression identifiers, OpenContainers layer media types, `exec.CommandContext`, and containerd logging for unsupported algorithms. It plugs into layer unpack paths that need custom decompression.

Risks: singleton initialization can preserve a failed or partial configuration for process lifetime. Unsupported algorithms are logged but ignored. The path sanitizer rejects shell metacharacters and requires executable files, but arguments are passed directly to the binary and must still be configured correctly. `cmdStream` only reports process failures to readers, so callers must read to observe stderr/exit errors.

Test signals: companion tests cover empty config, gzip mapping to two media types, unsupported algorithm ignore behavior, missing gzip/zstd executable failures, lookup before/after initialization, and `cmdStream` success/failure propagation including stderr text.
<!-- END_FILE_RESEARCH: sources/cloud-native/soci-snapshotter/internal/archive/compression/compression.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/soci-snapshotter/internal/archive/compression/compression_test.go -->
# sources/cloud-native/soci-snapshotter/internal/archive/compression/compression_test.go

Purpose: unit tests for configurable decompression-stream initialization, media-type lookup, and command-stream error propagation.

Important APIs/types/functions: `resetDecompressStreams` resets package globals for test isolation. `TestInitializeDecompressStreams` covers default, gzip, unsupported algorithm, and nonexistent executable configurations. `TestGetDecompressStream` checks lookups before initialization and after gzip setup. `TestCmdStream` and `TestCmdStreamBad` verify stdout capture and error formatting from subprocesses.

Control flow: tests reset globals, call `InitializeDecompressStreams`, then assert map cardinality and specific key presence. Lookup tests first assert no streams, initialize gzip, then assert Docker and OCI gzip media types are available. Command tests run small shell snippets through `cmdStream` and read from the returned pipe.

State and persistence: directly mutates package-level maps and `sync.Once`, which is intentional test-only access from the same package. It assumes `/usr/bin/gzip` exists for positive sanitizer validation and fake `/usr/bin/superfast*` paths do not.

Dependencies/integration points: uses `config.DecompressStream`, OCI media type constants, `os/exec`, `io.ReadAll`, and shell availability. It tests behavior that downstream unpackers rely on without invoking actual layer unpacking.

Risks: hard-coded `/usr/bin/gzip` can make the test environment-dependent. Resetting `sync.Once` is safe in tests but highlights that production cannot reinitialize. Command failure assertions compare exact error string including newline from stderr.

Test signals: high confidence around media-type registration and subprocess pipe behavior; no test directly decompresses gzip/zstd data or validates zstd success with a real binary.
<!-- END_FILE_RESEARCH: sources/cloud-native/soci-snapshotter/internal/archive/compression/compression_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/soci-snapshotter/internal/archive/compression/doc.go -->
# sources/cloud-native/soci-snapshotter/internal/archive/compression/doc.go

Purpose: package documentation for the internal configurable decompression package.

Important APIs/types/functions: declares package `compression` with import path `github.com/awslabs/soci-snapshotter/internal/archive/compression` and documents that it defines mechanisms for configuring decompression streams used to unpack image layer tarballs.

Control flow: no runtime behavior.

State and persistence: no state.

Dependencies/integration points: documents that the package was copied and modified from containerd archive compression. The actual implementation in `compression.go` depends on containerd archive compression contracts.

Risks: documentation must stay aligned with supported algorithms and configuration behavior.

Test signals: no direct tests; package behavior is covered by `compression_test.go`.
<!-- END_FILE_RESEARCH: sources/cloud-native/soci-snapshotter/internal/archive/compression/doc.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/soci-snapshotter/internal/http/auth.go -->
# sources/cloud-native/soci-snapshotter/internal/http/auth.go

Purpose: reusable authenticated HTTP client wrapper for challenge-response registry/blob access. It wraps `retryablehttp.Client`, delegates auth logic to an `AuthHandler`, supports custom auth policies/context creation, attaches global headers, and caches successful GET redirects.

Important APIs/types/functions: `AuthHandler` defines `HandleChallenge` and `AuthorizeRequest`. `AuthPolicy`, `DefaultAuthPolicy`, `AuthReqContextFunc`, and `DefaultAuthReqContext` configure challenge detection and replay context. `AuthClient` provides `Do`, `StandardClient`, `RoundTrip`, `CloneWithNewClient`, `Client`, `CacheRedirects`, `redirected`, and `shouldCache`. Options include `WithHeader`, `WithAuthPolicy`, `WithRetryableClient`, and `WithAuthRequestCtxFunc`.

Control flow: `Do` initializes defaults, applies cached redirect rewriting for GETs, authorizes the request, converts it to retryablehttp, and sends it. If the policy matches the response, it calls `HandleChallenge`, drains the response body for connection reuse, clones the request with a fresh auth context, reauthorizes, and resends. Redirect caching records original URL to final response URL after successful 200/206 GETs.

State and persistence: persistent in-memory state includes header, handler, retry client, policy, redirect map, redirect mutex, and redirect-cache flag. Redirects are cached per original URL string and are not affected when `CacheRedirects(false)` is called except for future writes.

Dependencies/integration points: integrates with HashiCorp retryablehttp, Go `http.RoundTripper`, and internal `Drain`. Resolver code builds this client around containerd's Docker authorizer. `StandardClient` allows APIs requiring `*http.Client` to use the auth client as transport.

Risks: `roundTrip` mutates request headers and passes the same request to the handler. `CloneWithNewClient` does not copy `getAuthCtx` or redirect cache settings, so clones rely on defaults. Redirect cache rewrites only GETs and sets `Referer`; stale signed URLs could be cached if upstream returns 200/206 but short TTL. `DefaultAuthReqContext` drops original cancellation unless a custom context func is provided.

Test signals: tests cover basic-auth challenge retry, custom auth policy, global headers, and redirect cache rewriting with `Referer`. Missing-handler errors are defined but not deeply tested here.
<!-- END_FILE_RESEARCH: sources/cloud-native/soci-snapshotter/internal/http/auth.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/soci-snapshotter/internal/http/auth_test.go -->
# sources/cloud-native/soci-snapshotter/internal/http/auth_test.go

Purpose: unit tests for the authenticated HTTP client wrapper.

Important APIs/types/functions: test doubles include `authRoundTripper`, `basicAuthHandler`, `policyAuthHandler`, `statusRoundTripper`, `headerRoundTripper`, `emptyAuthHandler`, `SimpleMockAuthClient`, and `redirectRoundTripper`. Tests are `TestAuthHandler`, `TestCustomAuthPolicy`, `TestCustomAuthHeaders`, and `TestRedirectCacheSetsRefererHeader`.

Control flow: tests wire a retryable client with a fake transport, create an `AuthClient`, issue requests, and assert second-round authorization, policy invocation count, headers, or redirect target/referer. The basic auth flow simulates first 401 then a second request with credentials obtained during challenge handling.

State and persistence: fake handlers store credentials or auth counts in memory. Redirect tests enable `CacheRedirects(true)` and use two requests to prove cache population then reuse.

Dependencies/integration points: uses base64-encoded basic auth, retryablehttp, and Go request/response primitives. It exercises `AuthClient.Do` but not real network or Docker auth.

Risks: `statusRoundTripper` has a value receiver, so its `reqCount` does not persist between calls; the custom-policy test only asserts challenge handling count and does not verify second-response status behavior. Redirect tests simulate a followed redirect by setting `resp.Request.URL` and do not cover non-GET or non-200/206 exclusions.

Test signals: strong signals for core challenge replay and header injection; limited coverage for error wrapping, missing handlers, clone behavior, and cache invalidation.
<!-- END_FILE_RESEARCH: sources/cloud-native/soci-snapshotter/internal/http/auth_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/soci-snapshotter/internal/http/errors.go -->
# sources/cloud-native/soci-snapshotter/internal/http/errors.go

Purpose: shared sentinel errors for the internal auth HTTP client.

Important APIs/types/functions: declares `ErrMissingAuthHandler`, `ErrFailedToAuthorizeRequest`, and `ErrFailedToHandleChallenge`.

Control flow: no standalone flow; `AuthClient.Do` wraps lower-level handler failures with these sentinels so callers can classify auth setup, authorization, and challenge-handling failures.

State and persistence: immutable package-level error values.

Dependencies/integration points: used by `auth.go` and any callers that check errors with `errors.Is`.

Risks: wrapped errors must preserve these sentinels with `%w`; current auth client does that for authorize/challenge failures.

Test signals: indirectly exercised by auth tests; no dedicated `errors.Is` assertions.
<!-- END_FILE_RESEARCH: sources/cloud-native/soci-snapshotter/internal/http/errors.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/soci-snapshotter/internal/http/util.go -->
# sources/cloud-native/soci-snapshotter/internal/http/util.go

Purpose: HTTP utility functions for redacting sensitive query values from URLs/errors and draining response bodies for connection reuse.

Important APIs/types/functions: `RedactHTTPQueryValuesFromError` detects `*url.Error`, parses its URL, redacts query values, and mutates `urlErr.URL`. `RedactHTTPQueryValuesFromURL` replaces every query value with `redacted`. `RedactHTTPQueryValuesFromString` parses and redacts a URL string. `Drain` reads up to 4 KiB from a response body and closes it.

Control flow: redaction functions parse or inspect URL values, mutate in place when possible, and leave invalid/non-URL errors unchanged. Drain defers close and copies from a limited reader to `io.Discard`.

State and persistence: no package state, but functions mutate passed URL objects and `*url.Error` values.

Dependencies/integration points: resolver retry/error handling uses these functions to avoid leaking credentials or pre-signed URL tokens in logs and errors. Auth replay uses `Drain` before resending after challenge.

Risks: redaction preserves query keys, which can still reveal parameter names. `RedactHTTPQueryValuesFromError` mutates the original `url.Error`, which can surprise callers holding the same error. `Drain` assumes non-nil body; callers must guard when responses can have nil body.

Test signals: companion tests cover nil/non-URL errors, no-query URLs, query redaction, nil URL handling, and benchmark logging overhead.
<!-- END_FILE_RESEARCH: sources/cloud-native/soci-snapshotter/internal/http/util.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/soci-snapshotter/internal/http/util_test.go -->
# sources/cloud-native/soci-snapshotter/internal/http/util_test.go

Purpose: tests and benchmarks for HTTP query redaction helpers.

Important APIs/types/functions: `TestRedactHTTPQueryValuesFromError`, `TestRedactHTTPQueryValuesFromURL`, and `BenchmarkRedactHTTPQueryValuesOverhead`. Constants model an S3-like URL with sensitive username/password query values and expected sorted redacted query output.

Control flow: table-driven tests feed nil errors, non-URL errors, URL errors with and without query strings, nil URLs, empty URLs, and raw query maps into redaction utilities. The benchmark compares baseline log writes against redaction with and without replacement.

State and persistence: no persistent state; tests mutate URL and error objects in-memory.

Dependencies/integration points: uses `logrus.Entry` with an in-memory buffer to measure logging overhead. Mirrors resolver error-redaction behavior.

Risks: expected query order depends on `url.Values.Encode` sorting keys. Tests do not cover malformed URL strings for `RedactHTTPQueryValuesFromString` or nil body behavior for `Drain`.

Test signals: confirms sensitive values are replaced with `redacted`, unrecognized errors are unchanged, and redaction has benchmark coverage for performance tracking.
<!-- END_FILE_RESEARCH: sources/cloud-native/soci-snapshotter/internal/http/util_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/soci-snapshotter/internal/os/doc.go -->
# sources/cloud-native/soci-snapshotter/internal/os/doc.go

Purpose: package documentation for internal OS utility functions.

Important APIs/types/functions: declares package `os` with import path `github.com/awslabs/soci-snapshotter/internal/os`.

Control flow: no runtime behavior.

State and persistence: no state.

Dependencies/integration points: documents helpers such as executable path sanitation used by configurable decompression setup.

Risks: package name shadows the standard library `os` in imports, so callers generally alias it as `intos` or similar.

Test signals: behavior is covered by `filepath_test.go`.
<!-- END_FILE_RESEARCH: sources/cloud-native/soci-snapshotter/internal/os/doc.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/soci-snapshotter/internal/os/filepath.go -->
# sources/cloud-native/soci-snapshotter/internal/os/filepath.go

Purpose: validates executable paths before using them as external command binaries, reducing command-injection and misconfiguration risk for decompression streams.

Important APIs/types/functions: `SanitizeExecutablePath` returns a resolved executable path or an error. Sentinel errors include `errFilePathContainsInvalidCharacters`, `errFilePathIsADirectory`, and `errFilePathIsNotExecutable`.

Control flow: validation rejects paths containing `#%{}\|;&$<>`, cleans the path, resolves symlinks, computes an absolute path for stat checks, rejects directories, verifies any executable bit is set, and returns the symlink-resolved path.

State and persistence: no persistent state; reads filesystem metadata and symlink targets.

Dependencies/integration points: used by `internal/archive/compression.InitializeDecompressStreams` before spawning configured decompressor binaries.

Risks: the returned value is `resolvedPath`, not the absolute path, so relative input can produce a relative resolved path even though stat was checked through `absPath`. Character filtering is conservative but not a complete policy for all OS/path edge cases. It validates the binary path only, not its arguments.

Test signals: tests cover valid executable, symlink resolution, invalid characters, nonexistent path, broken symlink, directory, and non-executable file.
<!-- END_FILE_RESEARCH: sources/cloud-native/soci-snapshotter/internal/os/filepath.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/soci-snapshotter/internal/os/filepath_test.go -->
# sources/cloud-native/soci-snapshotter/internal/os/filepath_test.go

Purpose: unit tests for executable path sanitation.

Important APIs/types/functions: `TestSanitizeExecutablePath` is table-driven and creates temporary files, directories, and symlinks to exercise sanitizer outcomes.

Control flow: each case builds a path under `t.TempDir`, calls `SanitizeExecutablePath`, checks errors using `errors.Is`, and compares returned path against expected resolved output.

State and persistence: creates temporary executable/non-executable files and symlinks with per-test cleanup through the testing package.

Dependencies/integration points: validates behavior that compression configuration relies on before executing custom decompression binaries.

Risks: test expectations depend on Unix permission semantics and symlink behavior. It does not cover relative paths or every rejected metacharacter individually.

Test signals: good coverage for success, symlink resolution, path-not-found, directory, permission, and injection-character rejection.
<!-- END_FILE_RESEARCH: sources/cloud-native/soci-snapshotter/internal/os/filepath_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/soci-snapshotter/metadata/db.go -->
# sources/cloud-native/soci-snapshotter/metadata/db.go

Purpose: bbolt schema and low-level serialization helpers for filesystem metadata derived from a ztoc TOC. It stores node attributes separately from parent/child and tar-offset metadata.

Important APIs/types/functions: bucket keys define the schema under `filesystems/<fsID>/nodes` and `filesystems/<fsID>/metadata`. `childEntry` and `metadataEntry` hold in-memory build state. Accessors include `getNodesBucket`, `getMetadataBucket`, `getNodeBucketByID`, and `getMetadataBucketByID`. Writers/readers include `writeNodeEntry`, `readNodeEntryToAttr`, `readNumLink`, `readChild`, `writeMetadataEntry`, and `getMetadataEntry`. Numeric helpers include `encodeID`, `decodeID`, `putInt`, and `encodeUint`.

Control flow: node attributes are stored sparsely, omitting zero values. Xattrs and children optimize the first entry as direct keys and store extra entries in sub-buckets. Metadata entries write tar name, tar header offsets/sizes, and uncompressed offsets. Reads iterate bucket keys and reconstruct `Attr` or metadata values.

State and persistence: persists filesystem metadata in a bbolt database. IDs are four-byte big-endian keys, integer values use varint/uvarint encoding, and modtime uses `time.GobEncode`. NumLink is stored as `NumLink-1`, making a missing/zero DB value mean one link.

Dependencies/integration points: used by `reader.go` to build and query metadata from ztoc entries. Depends on bbolt, `dbutil.EncodeInt`, `ztoc/compression.Offset`, and `metadata.Attr`.

Risks: sparse zero-value encoding means zero-valued attributes and missing attributes are indistinguishable. First xattr/child selection is map-iteration dependent, though extra children are sorted by base before writing. `readNodeEntryToAttr` stores xattr byte slices directly from bbolt values, which should not be retained past the transaction boundary unless copied. `decodeID` assumes a valid four-byte slice.

Test signals: metadata utility tests indirectly validate attributes, xattrs, child lookup, hardlinks, directory children, modes, device nodes, and link counts through the public Reader.
<!-- END_FILE_RESEARCH: sources/cloud-native/soci-snapshotter/metadata/db.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/soci-snapshotter/metadata/metadata.go -->
# sources/cloud-native/soci-snapshotter/metadata/metadata.go

Purpose: public metadata package contracts for storing and reading filesystem metadata for a compressed layer blob.

Important APIs/types/functions: `Attr` represents file attributes: size, modtime, symlink target, mode, UID/GID, device major/minor, xattrs, and link count. `Store` is a constructor function type. `Reader` exposes `RootID`, `GetAttr`, `GetChild`, `ForeachChild`, `OpenFile`, `Clone`, and `Close`. `File` exposes uncompressed file size/offset plus tar name/header offset/header size. `Options`, `Option`, `WithTelemetry`, `MeasureLatencyHook`, and `Telemetry` define initialization telemetry hooks.

Control flow: this file only defines interfaces and option application contracts. `NewReader` in `reader.go` applies `Option` functions and records telemetry.

State and persistence: no direct state; interfaces represent metadata persisted by the bbolt-backed implementation.

Dependencies/integration points: references `io.SectionReader`, `ztoc.TOC`, and `ztoc/compression.Offset`. The Reader interface is consumed by filesystem/lazy-read paths that need metadata lookup and file-open information.

Risks: interface methods use numeric node IDs, so callers need correct traversal through `GetChild`/`ForeachChild`. Telemetry currently only exposes initialization latency.

Test signals: `reader_test.go` and `util_test.go` validate an implementation of these contracts through `testableReader`.
<!-- END_FILE_RESEARCH: sources/cloud-native/soci-snapshotter/metadata/metadata.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/soci-snapshotter/metadata/reader.go -->
# sources/cloud-native/soci-snapshotter/metadata/reader.go

Purpose: bbolt-backed implementation of `metadata.Reader`. It parses ztoc TOC file metadata, builds a directory/node graph, persists attributes and tar-offset metadata, and serves lookup/open operations.

Important APIs/types/functions: `reader` holds db, fsID, rootID, section reader, ID counter/mutex, and init errgroup. Constructor `NewReader` applies options, records telemetry, initializes root and nodes, and returns a Reader. Build helpers include `init`, `initRootNode`, `initNodes`, `nextID`, `getIDByName`, `getOrCreateDir`, `setChild`, `cleanEntryPath`, `parentDir`, `partition`, and `attrFromZtocEntry`. Reader methods include `RootID`, `Clone`, `Close`, `GetAttr`, `GetChild`, `ForeachChild`, `OpenFile`, and test helper `NumOfNodes`.

Control flow: initialization creates a unique fsID bucket, root directory node, then partitions TOC entries into 5000-entry bbolt batches. For each TOC entry it normalizes paths, handles hardlinks by finding the destination node and incrementing link count, creates or updates node buckets for non-links, creates parent directories recursively, records parent-child relationships, and stores tar metadata for non-hardlinks. After node creation it writes sorted metadata buckets in batches. Read methods wait for initialization, open bbolt view/update transactions, find buckets by fsID and node ID, and reconstruct attributes or file metadata.

State and persistence: metadata lives under a unique bbolt filesystem bucket. `Close` deletes that fsID bucket from the shared DB. `Clone` shares db/fsID/rootID but swaps the section reader. Node IDs are process-generated uint32s guarded by a mutex. Hardlinks share node IDs and update link counts. Directory link counts are incremented for child directories.

Dependencies/integration points: consumes `ztoc.TOC` and `ztoc.FileMetadata`, stores bbolt buckets using helpers from `db.go`, and returns offset metadata needed to fetch file payloads. Uses `xid` for fsID uniqueness and `errgroup` for initialization wait plumbing, although current initialization is synchronous.

Risks: `NewReader` calls the telemetry hook immediately with `start`, so hook semantics are start-time based rather than after-duration unless the hook computes externally. `attr` is reused in the init loop; `attrFromZtocEntry` overwrites many fields but link count preservation for existing dirs depends on careful setup. `ForeachChild` returns map iteration order, not sorted order. Missing metadata in `OpenFile` yields zero offset/name rather than an explicit missing-metadata error if node exists. TODO notes no timeout for initialization wait.

Test signals: tests cover files, directories, hardlinks, symlinks, device nodes, FIFOs, xattrs, path cleanup, compression variants, telemetry hook invocation, and partition behavior.
<!-- END_FILE_RESEARCH: sources/cloud-native/soci-snapshotter/metadata/reader.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/soci-snapshotter/metadata/reader_test.go -->
# sources/cloud-native/soci-snapshotter/metadata/reader_test.go

Purpose: test entry point and bbolt-backed test factory for metadata Reader behavior, plus direct tests for the generic `partition` helper.

Important APIs/types/functions: `TestMetadataReader` delegates to shared `testReader`. `newTestableReader` creates a temp bbolt DB, calls `NewReader`, and returns `testableReadCloser`. `TestPartition` checks chunking behavior for exact division, remainder, empty input, oversized chunks, zero chunk size, and negative chunk size.

Control flow: metadata tests are shared with other possible reader factories. The factory creates a temp file, opens bbolt, initializes the reader, and wraps cleanup. Partition tests call `partition` and compare nested slice shape and values manually.

State and persistence: creates temporary bbolt DB files and removes them on close. `testableReadCloser.Close` closes/removes the DB and then calls reader `Close`, which deletes the fsID bucket.

Dependencies/integration points: depends on bbolt and shared test utilities from `util_test.go`. It validates production `NewReader` through generated ztoc fixtures.

Risks: deferred `os.Remove(f.Name())` in `newTestableReader` runs before the returned close function; on Unix the open DB can continue using the unlinked file, but this is platform-sensitive. Close order calls DB close before reader Close, so bucket deletion may operate on a closed DB if reached; tests may tolerate this through ignored close errors.

Test signals: partition helper has focused coverage; full reader coverage is provided by `testReader` cases.
<!-- END_FILE_RESEARCH: sources/cloud-native/soci-snapshotter/metadata/reader_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/soci-snapshotter/metadata/testutil.go -->
# sources/cloud-native/soci-snapshotter/metadata/testutil.go

Purpose: test utility store constructor that creates a metadata Reader backed by a temporary bbolt database.

Important APIs/types/functions: `NewTempDbStore` matches the `Store` signature, creates a temp DB file, opens bbolt, initializes `NewReader`, and wraps it in `readCloser`. `readCloser.Close` runs a cleanup function and then calls the embedded Reader's `Close`.

Control flow: create temp file, close it later with defer, open bbolt, create reader, and return a wrapper whose cleanup closes/removes DB resources.

State and persistence: temporary bbolt DB file stores metadata for the reader lifetime and is removed on close.

Dependencies/integration points: used by tests or callers needing an ephemeral metadata store. Depends on bbolt, `ztoc.TOC`, and the Reader implementation.

Risks: if `NewReader` returns an error after opening the DB, this helper does not close/remove the DB file. `readCloser.Close` ignores errors from both cleanup and Reader close by returning only the Reader close result after cleanup side effects.

Test signals: no direct tests in this file; behavior is similar to the factory used by `reader_test.go`.
<!-- END_FILE_RESEARCH: sources/cloud-native/soci-snapshotter/metadata/testutil.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/soci-snapshotter/metadata/util_test.go -->
# sources/cloud-native/soci-snapshotter/metadata/util_test.go

Purpose: shared behavioral test suite for metadata Readers. It builds synthetic tar/ztoc fixtures and asserts Reader traversal, attributes, link behavior, xattrs, and open-file metadata across compression modes and path prefixes.

Important APIs/types/functions: `readerFactory` and `testableReader` abstract the implementation under test. `testReader` defines test cases for files, directories, hardlinks, path cleanup/device types, and allowed prefixes. Check helpers include `numOfNodes`, `sameNodes`, `linkName`, `hasNumLink`, `hasDirChildren`, `hasChardev`, `hasBlockdev`, `hasFifo`, `hasFile`, `hasMode`, `hasOwner`, `hasModTime`, `hasXattrs`, and `lookup`. `newCalledTelemetry` verifies telemetry hook invocation.

Control flow: for each fixture, prefix, and gzip compression level, tests build a ztoc reader, construct the metadata reader with telemetry, optionally dump the node tree, run all checks, and assert telemetry was called. `lookup` recursively resolves paths through `GetChild` from the root.

State and persistence: generated tar/gzip/ztoc fixtures and metadata reader state are temporary per test. Check functions only read through the Reader interface.

Dependencies/integration points: uses project `util/testutil` tar-entry builders, `ztoc.BuildZtocReader`, Go gzip levels, and the metadata Reader interface. This suite anchors contract behavior for any Reader implementation.

Risks: extensive cross-product of prefixes and compression levels can be expensive. `ForeachChild` order is ignored by using a map. `hasModTime` allows equality through before/after checks. Tests assume hardlink targets appear before hardlinks so the reader can resolve them.

Test signals: strong functional coverage for regular files, directories, nested paths, owners, modes, modtimes, xattrs, hardlinks sharing node IDs, symlinks, directory link counts, char/block devices, FIFOs, path normalization, and telemetry.
<!-- END_FILE_RESEARCH: sources/cloud-native/soci-snapshotter/metadata/util_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/soci-snapshotter/scripts/add-ltag.sh -->
# sources/cloud-native/soci-snapshotter/scripts/add-ltag.sh

Purpose: applies license headers to project files using `ltag`.

Important APIs/types/functions: shell script computes its directory, project root, then runs `$(go env GOPATH)/bin/ltag -v -t .headers` from the root.

Control flow: `set -eux -o pipefail`, pushd root, execute ltag, popd.

State and persistence: mutates files in the repository by adding/updating license headers.

Dependencies/integration points: requires Go environment and `ltag` installed by `install-check-tools.sh`; uses `.headers` template.

Risks: broad file mutation if `.headers` or ltag matching changes. It assumes GOPATH bin contains ltag.

Test signals: paired with `check-ltag.sh`, which fails if headers are missing.
<!-- END_FILE_RESEARCH: sources/cloud-native/soci-snapshotter/scripts/add-ltag.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/soci-snapshotter/scripts/build-third-party-licenses.sh -->
# sources/cloud-native/soci-snapshotter/scripts/build-third-party-licenses.sh

Purpose: regenerates `THIRD_PARTY_LICENSES` for Go dependencies.

Important APIs/types/functions: truncates the license file, runs `go-licenses report` with Apache and other templates, appends the project Apache license text once, and ignores `github.com/awslabs/soci`.

Control flow: compute root and license path, truncate target, append generated Apache attribution, static Apache license text, then non-Apache license reports.

State and persistence: overwrites `THIRD_PARTY_LICENSES`.

Dependencies/integration points: requires `go-licenses`, template files under `scripts/third_party_licenses`, Go module graph, and project root.

Risks: only covers Go dependencies; comments direct non-Go notices to `NOTICE.md`. Dependency or template changes can produce large diffs.

Test signals: no direct test; used in release/compliance workflows.
<!-- END_FILE_RESEARCH: sources/cloud-native/soci-snapshotter/scripts/build-third-party-licenses.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/soci-snapshotter/scripts/bump-deps.sh -->
# sources/cloud-native/soci-snapshotter/scripts/bump-deps.sh

Purpose: updates Go module dependencies while constraining containerd to patch releases and excluding Kubernetes dependencies.

Important APIs/types/functions: runs `go get -u=patch github.com/containerd/containerd/v2`, runs `go get` on direct non-main modules excluding containerd and `k8s.io/`, runs `make tidy`, then repeats analogous updates under `./cmd` while excluding the main soci-snapshotter module.

Control flow: enter project root, update root module, tidy, enter `cmd`, update cmd module, return, tidy again.

State and persistence: mutates `go.mod`/`go.sum` in root and `cmd`, plus any tidy-generated module changes.

Dependencies/integration points: Go module tooling and Makefile `tidy` target.

Risks: command substitution can fail if module list is empty. Exclusions encode policy that k8s uses newer Go/features and containerd minor bumps must be intentional. Broad updates can still introduce transitive shifts.

Test signals: no direct test; downstream CI/lint/test suites validate updated deps.
<!-- END_FILE_RESEARCH: sources/cloud-native/soci-snapshotter/scripts/bump-deps.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/soci-snapshotter/scripts/check-all.sh -->
# sources/cloud-native/soci-snapshotter/scripts/check-all.sh

Purpose: convenience wrapper to run standard repository checks.

Important APIs/types/functions: executes `check-dco.sh`, `check-flatc.sh`, `check-ltag.sh`, and `check-lint.sh` sequentially.

Control flow: fail-fast shell with `set -eux -o pipefail`; each script must succeed.

State and persistence: read-only checks except any called tool side effects; no direct state.

Dependencies/integration points: relies on sibling scripts and installed check tools.

Risks: assumes it is run from the scripts directory or a working directory where `./check-*.sh` resolves correctly; unlike many other scripts it does not compute its own directory.

Test signals: aggregate CI signal for DCO, generated flatbuffers, headers, and lint.
<!-- END_FILE_RESEARCH: sources/cloud-native/soci-snapshotter/scripts/check-all.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/soci-snapshotter/scripts/check-config.sh -->
# sources/cloud-native/soci-snapshotter/scripts/check-config.sh

Purpose: verifies the checked-in default config matches output from the built `soci-snapshotter-grpc config default` command.

Important APIs/types/functions: computes root, expected `config/config.toml`, output binary under `out/soci-snapshotter-grpc`, generates a temp config, and diffs it against the checked-in file.

Control flow: create temp directory, run binary to generate default config, `diff -q`, print regeneration guidance and cleanup on mismatch, then remove tempdir on success.

State and persistence: creates and removes a temp directory; reads built binary and config file.

Dependencies/integration points: requires `out/soci-snapshotter-grpc` to be built and config generation command to be available.

Risks: failure cleanup is embedded in a shell OR expression; unexpected failures before that point may leave tempdir. The binary path must match build output.

Test signals: CI-style guard that config defaults and committed config stay in sync.
<!-- END_FILE_RESEARCH: sources/cloud-native/soci-snapshotter/scripts/check-config.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/soci-snapshotter/scripts/check-dco.sh -->
# sources/cloud-native/soci-snapshotter/scripts/check-dco.sh

Purpose: validates Developer Certificate of Origin signatures for recent commits.

Important APIs/types/functions: runs `git-validation -run DCO -range HEAD~20..HEAD`.

Control flow: fail-fast shell invokes GOPATH-installed `git-validation`.

State and persistence: read-only over git history.

Dependencies/integration points: requires `git-validation` installed by `install-check-tools.sh`.

Risks: only checks last 20 commits and includes comments about known historical exceptions. Shallow clones with less history may fail.

Test signals: CI signal for signed-off-by compliance in recent history.
<!-- END_FILE_RESEARCH: sources/cloud-native/soci-snapshotter/scripts/check-dco.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/soci-snapshotter/scripts/check-flatc.sh -->
# sources/cloud-native/soci-snapshotter/scripts/check-flatc.sh

Purpose: verifies generated Go flatbuffer files are up to date with ztoc and zinfo schemas.

Important APIs/types/functions: runs `flatc -o <tmp> -g` for `ztoc/fbs/ztoc.fbs` and `ztoc/compression/fbs/zinfo.fbs`, then diffs generated directories against checked-in generated code.

Control flow: generate into tempdir for ztoc, compare, cleanup; repeat for zinfo.

State and persistence: creates/removes temporary directories only; reads schema and generated code.

Dependencies/integration points: requires `flatc` installed, schema directory layout, and generated Go code under expected sibling folders.

Risks: exact generated output can vary by flatc version, so dependency version pinning matters. Failure path removes tempdir through shell expression but abrupt errors may leave temp dirs.

Test signals: CI guard for schema-generated code drift.
<!-- END_FILE_RESEARCH: sources/cloud-native/soci-snapshotter/scripts/check-flatc.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/soci-snapshotter/scripts/check-ltag.sh -->
# sources/cloud-native/soci-snapshotter/scripts/check-ltag.sh

Purpose: checks that repository files have required license headers.

Important APIs/types/functions: runs `ltag -t .headers -check -v` from the project root and prints guidance to run `scripts/add-ltag.sh` on failure.

Control flow: compute root, pushd, run ltag check, popd.

State and persistence: read-only validation.

Dependencies/integration points: requires GOPATH-installed `ltag` and `.headers`.

Risks: ltag's file selection controls what is checked; missing tool yields check failure.

Test signals: CI guard for license-header compliance.
<!-- END_FILE_RESEARCH: sources/cloud-native/soci-snapshotter/scripts/check-ltag.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/soci-snapshotter/scripts/check-regression.sh -->
# sources/cloud-native/soci-snapshotter/scripts/check-regression.sh

Purpose: compares benchmark JSON results and fails if current P90 timings regress beyond a threshold.

Important APIs/types/functions: `calculate_threshold` computes 110% of the past value. `calculate_p90_after_skip` sorts benchmark times after dropping the first sample. `compare_stat_p90` and `compare_p90_values` compare `fullRunStats`, `pullStats`, `lazyTaskStats`, and `localTaskStats` for each benchmark test.

Control flow: require two JSON paths, load JSON into variables, iterate test names from past JSON, compute past/current P90s for each stat, flag regressions, print success/failure, and exit accordingly.

State and persistence: read-only over input JSON files.

Dependencies/integration points: requires `jq`, `bc`, `awk`, `sort`, and benchmark JSON with `.benchmarkTests[].<stat>.BenchmarkTimes`.

Risks: comment says 150% but code uses 1.1 and error text says 110%. P90 index calculation uses original length despite skipping one sample, which may bias indexing. Missing current test/stat values can produce invalid numeric comparisons.

Test signals: serves as performance regression gate for benchmark result files.
<!-- END_FILE_RESEARCH: sources/cloud-native/soci-snapshotter/scripts/check-regression.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/soci-snapshotter/scripts/create-release-branch.sh -->
# sources/cloud-native/soci-snapshotter/scripts/create-release-branch.sh

Purpose: creates and optionally pushes a `release/<major>.<minor>` branch from a chosen base commit.

Important APIs/types/functions: parses `--assert`, `--base`, and `--dry-run` plus version argument. `sanitize_input` validates version and base commit. `assert_create_branch` verifies current branch and base commit.

Control flow: parse flags, strip leading `v`, validate semantic major/minor, resolve or validate base commit, checkout new release branch, optionally assert branch state, then either validate push command in dry-run mode or push to origin.

State and persistence: mutates local git branch state and may push a branch to origin.

Dependencies/integration points: requires git history and remote named `origin`; intended for release automation.

Risks: `git checkout -b` is stateful and fails if branch exists or worktree is dirty in incompatible ways. `grep "$BASE_COMMIT"` may match multiple commits but only checks non-empty. Dry-run does not exercise remote permission or branch existence.

Test signals: assert mode validates branch name and commit after checkout; no standalone tests.
<!-- END_FILE_RESEARCH: sources/cloud-native/soci-snapshotter/scripts/create-release-branch.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/soci-snapshotter/scripts/create-releases.sh -->
# sources/cloud-native/soci-snapshotter/scripts/create-releases.sh

Purpose: builds dynamic and static Linux release tarballs with checksums.

Important APIs/types/functions: validates a `vMAJOR.MINOR.PATCH` tag, determines arch (`amd64`/`arm64`), computes release filenames, runs `make build` and `STATIC=1 make build`, copies `NOTICE.md` and `THIRD_PARTY_LICENSES`, creates tarballs, and writes sha256sum files.

Control flow: validate one tag argument and supported architecture, clear/create `release/`, build dynamic artifacts into `out`, archive them, clean out, build static artifacts, archive them, then checksum tarballs.

State and persistence: mutates `out/` and `release/`, creates tarballs and checksum files.

Dependencies/integration points: requires Makefile build targets, project license/notice files, tar, sha256sum, and Linux architecture mapping.

Risks: cleanup commands use `rm -rf "{$OUT_DIR:?}"/*`, where braces are quoted literally, likely not deleting intended output. This can contaminate static/dynamic artifacts if not caught. Tag regex dots are unescaped, accepting broader strings than intended.

Test signals: paired with `verify-release-artifacts.sh` to validate tarball contents and checksums.
<!-- END_FILE_RESEARCH: sources/cloud-native/soci-snapshotter/scripts/create-releases.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/soci-snapshotter/scripts/install-check-tools.sh -->
# sources/cloud-native/soci-snapshotter/scripts/install-check-tools.sh

Purpose: installs Go-based repository check tools.

Important APIs/types/functions: runs `go install github.com/kunalkushwaha/ltag@v0.2.4` and `go install github.com/vbatts/git-validation@v1.2.0`.

Control flow: print message, enable fail-fast shell, install both tools.

State and persistence: writes binaries to Go install bin path.

Dependencies/integration points: supports `check-ltag.sh`, `add-ltag.sh`, and `check-dco.sh`.

Risks: requires network and compatible Go toolchain. Pin versions may become incompatible with future Go versions.

Test signals: no direct test; failure blocks check setup.
<!-- END_FILE_RESEARCH: sources/cloud-native/soci-snapshotter/scripts/install-check-tools.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/soci-snapshotter/scripts/install-dep.sh -->
# sources/cloud-native/soci-snapshotter/scripts/install-dep.sh

Purpose: installs native build dependencies such as cmake, flatc, and zlib from pinned source/binary downloads.

Important APIs/types/functions: creates temp dir, detects architecture, downloads cmake if missing with arch-specific checksum, builds/installs flatbuffers `flatc` if missing, then downloads/builds/installs zlib 1.2.12 with checksum verification.

Control flow: enter tempdir, conditionally install cmake, conditionally install flatc, always install zlib, then popd.

State and persistence: writes to `/usr/local` via installers and `sudo make install`; downloads/builds under a temp dir and removes archives/build dirs.

Dependencies/integration points: requires wget, sha256sum, tar, cmake/make/compiler toolchain, sudo, network access, and Linux arch names matching upstream artifacts.

Risks: zlib URL under `zlib.net/fossils` and pinned checksums can go stale. The variable `zmake_actual_shasum` appears typo-named but is used consistently. Always installing zlib can overwrite system libraries. Tempdir is not removed at the end.

Test signals: no direct tests; build/check-flatc workflows reveal missing dependencies.
<!-- END_FILE_RESEARCH: sources/cloud-native/soci-snapshotter/scripts/install-dep.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/soci-snapshotter/scripts/parallel-mode-install.sh -->
# sources/cloud-native/soci-snapshotter/scripts/parallel-mode-install.sh

Purpose: installs a released SOCI snapshotter binary and configures it as a systemd service/socket for parallel pull/unpack mode.

Important APIs/types/functions: environment defaults control concurrency, chunk size, discard behavior, SOCI version, root dir, and gzip decompressor path. It downloads release tarball and checksum, installs `soci-snapshotter-grpc`, writes `/etc/soci-snapshotter-grpc/config.toml`, writes systemd service/socket units, reloads systemd, and enables the service.

Control flow: derive arch, download artifacts to `/tmp`, verify checksum, extract binary to `/usr/local/bin`, remove downloads, write config and units via heredocs, start service.

State and persistence: mutates system directories `/usr/local/bin`, `/etc/soci-snapshotter-grpc`, `/etc/systemd/system`, and starts/enables a systemd unit.

Dependencies/integration points: integrates containerd content store, CRI keychain socket, parallel pull/unpack config, and custom gzip decompressor stream. Requires curl, sha256sum, tar, systemd, permissions to write system paths.

Risks: service starts before/with containerd via unit ordering but assumes containerd socket locations. Downloaded version default can drift from docs. The script trusts release checksum fetched from the same release location as the tarball.

Test signals: no direct tests; operational validation is service startup and containerd snapshotter behavior.
<!-- END_FILE_RESEARCH: sources/cloud-native/soci-snapshotter/scripts/parallel-mode-install.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/soci-snapshotter/scripts/update-version-in-docs.sh -->
# sources/cloud-native/soci-snapshotter/scripts/update-version-in-docs.sh

Purpose: updates release version strings in getting-started documentation and optionally asserts the resulting diff.

Important APIs/types/functions: parses `--assert` and `--verbose`, validates release version with optional leading `v`, runs `sed -i -E` on `docs/getting-started.md` and `docs/eks.md`, and `assert_diff` verifies git diff contains `+version="<VERSION>"`.

Control flow: parse flags, strip leading `v`, validate major.minor.patch with optional suffix, edit docs, optionally print diff, and optionally assert expected diff was produced.

State and persistence: mutates documentation files.

Dependencies/integration points: used by release automation. Requires GNU-compatible `sed` and git for assertion.

Risks: regex only matches existing `version="x.y.z"` strings without suffix, so prerelease existing versions may not update. `VERSION=${VERSION/v/}` removes the first `v` anywhere, not just prefix. Assert checks for at least one added line but not all target docs.

Test signals: assert mode provides automation signal that docs changed to target version.
<!-- END_FILE_RESEARCH: sources/cloud-native/soci-snapshotter/scripts/update-version-in-docs.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/soci-snapshotter/scripts/verify-release-artifacts.sh -->
# sources/cloud-native/soci-snapshotter/scripts/verify-release-artifacts.sh

Purpose: validates release tarballs and checksums generated by release automation.

Important APIs/types/functions: accepts release tag and optional arch, computes expected dynamic/static tarball names, verifies tarball and `.sha256sum` existence, runs `sha256sum -c`, lists tar contents, and compares contents against `soci-snapshotter-grpc`, `soci`, `THIRD_PARTY_LICENSES`, and `NOTICE.md`.

Control flow: validate args and release directory, derive release version, iterate expected tarballs, mark missing/invalid/unexpected content, print status, and exit nonzero if any validation failed.

State and persistence: read-only over `release/` artifacts.

Dependencies/integration points: paired with `create-releases.sh`; requires tar and sha256sum.

Risks: content membership checks use Bash regex-like substring matching against array expansion, which can produce false positives for similarly named files. It does not validate file modes or binary functionality.

Test signals: direct release artifact gate for presence, checksum integrity, and expected archive contents.
<!-- END_FILE_RESEARCH: sources/cloud-native/soci-snapshotter/scripts/verify-release-artifacts.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/soci-snapshotter/scripts/visualization-data-converter.sh -->
# sources/cloud-native/soci-snapshotter/scripts/visualization-data-converter.sh

Purpose: converts benchmark result JSON into per-test JSON metric files for visualization.

Important APIs/types/functions: `create_json_file` writes an array with lazy, local, and pull task duration P90 metrics. The main loop reads `.benchmarkTests[$i].testName`, `.lazyTaskStats.pct90`, `.localTaskStats.pct90`, and `.pullStats.pct90`.

Control flow: require input file and output directory args, check input exists, count benchmark tests with jq, iterate indices, extract fields, and write `<output_dir>/<testName>.json`.

State and persistence: writes one JSON file per benchmark test into the output directory.

Dependencies/integration points: requires `jq` and an existing output directory. Output format appears intended for dashboard/visualization ingestion.

Risks: does not create `output_dir`; test names with path separators or unsafe characters will affect output paths. JSON is hand-built with shell interpolation and can break if test names contain quotes or special characters.

Test signals: no direct tests; consumer visualization or JSON parsing would reveal malformed output.
<!-- END_FILE_RESEARCH: sources/cloud-native/soci-snapshotter/scripts/visualization-data-converter.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/soci-snapshotter/service/keychain/cri/v1/cri.go -->
# sources/cloud-native/soci-snapshotter/service/keychain/cri/v1/cri.go

Purpose: CRI image-service proxy and credential provider that captures credentials from CRI `PullImage` requests so the snapshotter can authenticate registry access for snapshots.

Important APIs/types/functions: `NewCRIKeychain` returns a `resolver.Credential` function and a `runtime.ImageServiceServer`. `instrumentedService` wraps a backend CRI `ImageServiceClient`, stores auth config per image reference, and implements `ListImages`, `ImageStatus`, `PullImage`, `RemoveImage`, and `ImageFsInfo`. `parseReference` normalizes Docker references into containerd reference specs.

Control flow: `NewCRIKeychain` starts a goroutine retrying backend CRI connection up to 100 times with 10-second sleeps. `PullImage` parses the image reference, stores `AuthConfig`, then forwards to backend CRI. `RemoveImage` deletes stored auth for that image and forwards. `credentials` maps docker.io hosts to `index.docker.io`, looks up auth by full image reference, and delegates parsing to `resolver.ParseAuth`.

State and persistence: in-memory map from image reference string to CRI `AuthConfig`, guarded by mutex. Backend CRI client is also guarded by mutex. State is not persisted across process restart.

Dependencies/integration points: used by `service/plugin` when CRI keychain is enabled. Integrates Kubernetes CRI v1 API, containerd reference parsing, distribution reference normalization, and resolver credential chains.

Risks: credentials are keyed by full image reference, so tag/digest normalization consistency is critical. If backend CRI connection is unavailable, calls fail with "server is not initialized yet". Stored credentials remain until `RemoveImage`; no TTL. Only implemented image-service methods are proxied.

Test signals: no direct tests in this file; integration tests enabling CRI keychain would validate pull authentication behavior.
<!-- END_FILE_RESEARCH: sources/cloud-native/soci-snapshotter/service/keychain/cri/v1/cri.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/soci-snapshotter/service/keychain/dockerconfig/dockerconfig.go -->
# sources/cloud-native/soci-snapshotter/service/keychain/dockerconfig/dockerconfig.go

Purpose: credential provider backed by the local Docker CLI config.

Important APIs/types/functions: `DockerCreds` loads Docker config, maps Docker Hub hosts to `https://index.docker.io/v1/`, reads auth config, and returns either identity token or username/password. `NewDockerConfigKeychain` returns a resolver credential function ignoring image reference and using only host.

Control flow: load config from default Docker config path, normalize host, call `GetAuthConfig`, prefer identity token, otherwise return basic credentials.

State and persistence: reads Docker config each call; no in-memory cache in this file.

Dependencies/integration points: default credential source registered by `service/plugin`; integrates Docker CLI config and resolver credential chain.

Risks: config load errors are swallowed as anonymous credentials, while `GetAuthConfig` errors are returned. Per-host only lookup cannot distinguish namespace-scoped credentials.

Test signals: no direct tests; behavior is indirectly exercised by registry auth flows.
<!-- END_FILE_RESEARCH: sources/cloud-native/soci-snapshotter/service/keychain/dockerconfig/dockerconfig.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/soci-snapshotter/service/keychain/kubeconfig/kubeconfig.go -->
# sources/cloud-native/soci-snapshotter/service/keychain/kubeconfig/kubeconfig.go

Purpose: Kubernetes secret-backed credential provider that watches `kubernetes.io/dockerconfigjson` secrets and serves registry credentials to resolver code.

Important APIs/types/functions: `WithKubeconfigPath`, `NewKubeconfigKeychain`, `newKeychain`, `keychain.credentials`, `startSyncSecrets`, `runWorker`, and `processNextItem`. `dockerconfigSelector` selects Docker config JSON secrets.

Control flow: a background goroutine optionally waits for a kubeconfig file, loads Kubernetes client config, creates a clientset, starts a shared informer for dockerconfigjson secrets across all namespaces, queues add/update/delete keys, waits for cache sync, then processes queued keys. Existing secrets are parsed into Docker config files; deleted secrets remove cached configs. Credential lookup normalizes Docker Hub and scans cached config files for matching host credentials.

State and persistence: in-memory map from namespace/name secret key to Docker config file, guarded by mutex. Informer and workqueue are initialized after kubeconfig/client setup. No persistence beyond Kubernetes API state.

Dependencies/integration points: used by plugin when kubeconfig keychain is enabled. Depends on client-go informers, workqueue, Docker configfile parser, containerd reference specs, and resolver credential function type.

Risks: kubeconfig file updates are not watched after initial load. The selector is assigned to `FieldSelector` even though secret type is usually a field/label nuance; if unsupported, list/watch may fail. Credential lookup scans all namespaces and may return the first matching secret without namespace/image scoping. Queue processing logs parse errors but does not retry.

Test signals: no direct tests here; Kubernetes-backed auth needs integration/e2e coverage.
<!-- END_FILE_RESEARCH: sources/cloud-native/soci-snapshotter/service/keychain/kubeconfig/kubeconfig.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/soci-snapshotter/service/plugin/plugin.go -->
# sources/cloud-native/soci-snapshotter/service/plugin/plugin.go

Purpose: registers SOCI snapshotter as a containerd snapshot plugin and wires service configuration, keychains, registry host configuration, and optional CRI image-service proxy.

Important APIs/types/functions: `Config` embeds `config.ServiceConfig` and adds `RootPath`, `CRIKeychainImageServicePath`, and resolver `Registry`. `init` registers a containerd plugin with type snapshot, ID `soci`, config, and init function. `getCriConn` creates a gRPC client connection to the backend CRI service with containerd dialer defaults and bounded backoff.

Control flow: plugin init validates config, resolves root path, exports root metadata, builds credential functions starting with Docker config, optionally adds kubeconfig keychain, optionally starts a Unix-socket CRI image service proxy and appends its credential provider, then creates the snapshotter service with custom registry hosts derived from CRI-compatible config.

State and persistence: creates/removes Unix socket path for CRI proxy, starts a gRPC server goroutine, and exposes root in plugin metadata. Service state is owned by `service.NewSociSnapshotterService`.

Dependencies/integration points: containerd plugin registry, service package, keychain packages, resolver registry host builder, gRPC, containerd dialer/default message sizes, and CRI API. It supports both external proxy plugin and built-in containerd plugin modes.

Risks: when `CRIKeychainConfig.EnableKeychain` is true, CRI proxy only starts if `CRIKeychainImageServicePath` is non-empty. `connectV1CRI` calls `getCriConn(config.CRIKeychainConfig.ImageServicePath)` rather than the resolved `criAddr`, so default-property fallback may not be used as intended. Socket removal with `RemoveAll` can remove non-socket paths if misconfigured.

Test signals: no direct unit tests; integration tests with snapshotter startup and CRI keychain settings validate registration and service boot.
<!-- END_FILE_RESEARCH: sources/cloud-native/soci-snapshotter/service/plugin/plugin.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/soci-snapshotter/service/resolver/client.go -->
# sources/cloud-native/soci-snapshotter/service/resolver/client.go

Purpose: HTTP client and authentication support for registry/blob resolver operations. It configures retryable HTTP behavior, Docker auth integration, sensitive URL redaction, token-expiration workarounds, and auth context propagation.

Important APIs/types/functions: `globalHeaders` sets the SOCI User-Agent. `newAuthClient` builds a `socihttp.AuthClient` around containerd `docker.Authorizer`. `newRetryableClientFromConfig` applies retry counts, waits, backoff, retry strategy, error handler, and timeouts. `CloneRetryableClient`, `jitter`, `backoffStrategy`, `retryStrategy`, and `handleHTTPError` define retry behavior. `dockerAuthHandler` implements `AuthHandler`. `shouldAuthenticate` handles 401, ECR expired-token 403, and S3 expired-token 400 XML. `newContextWithScope` carries Docker token scopes into replay contexts.

Control flow: resolver creates a retryable client, wraps it in AuthClient, sends requests through authorization/retry layers, retries transient errors with jittered backoff, redacts query values on logging/final errors, and reauthenticates on selected responses. ECR expired 403 bodies are parsed as Docker errors and may synthesize a `Www-Authenticate` header; S3 expired-token XML normalizes status to 401 but returns false so upstream blob fetch logic can refresh pre-signed URLs.

State and persistence: no global mutable state except `userAgent` string. Retryable clients carry configuration and HTTP transport timeouts. Auth state is delegated to containerd Docker authorizer and credential callbacks.

Dependencies/integration points: integrates `internal/http.AuthClient`, containerd remotes/docker authorizer, retryablehttp, project config, version, logrus/containerd logging, and XML/JSON registry error formats.

Risks: `CloneRetryableClient` intentionally does not clone HTTP timeout/transport settings, only retry policies. `shouldAuthenticate` reads and restores response bodies; nil bodies would panic if passed for 403/400 paths. ECR workaround hardcodes message/service. S3 branch returns false after mutating status, relying on caller behavior outside this function.

Test signals: `client_test.go` covers redacted final errors, response body drain/close, 401 auth, ECR expired-token 403 auth/header synthesis, and ordinary 403/200 no-auth cases.
<!-- END_FILE_RESEARCH: sources/cloud-native/soci-snapshotter/service/resolver/client.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/soci-snapshotter/service/resolver/client_test.go -->
# sources/cloud-native/soci-snapshotter/service/resolver/client_test.go

Purpose: unit tests for resolver HTTP error redaction, body draining, and authentication policy decisions.

Important APIs/types/functions: `TestHandleHTTPErrorRedactsHTTPQueries`, `TestHandleHTTPErrorReadsAndClosesResponseBody`, `mockBody`, and `TestAuthentication`. Constants define S3-like URL/query expectations.

Control flow: error tests create responses with sensitive query parameters and/or `url.Error`, call `handleHTTPError`, and compare final error strings. Body test verifies `handleHTTPError` reads and closes response body. Auth tests build Docker error JSON bodies for ECR expired token, normal forbidden, unauthorized, and OK, then assert `shouldAuthenticate` result and synthesized header where expected.

State and persistence: in-memory fake response bodies track read/close flags.

Dependencies/integration points: uses containerd Docker error types, Go URL/HTTP primitives, and resolver constants for ECR token expiration.

Risks: string comparisons are exact and can be brittle if error wording changes. Auth tests do not cover S3 XML expired-token branch. The test loop in `TestAuthentication` does not call `t.Run`, so a failure identifies the case through message only.

Test signals: confirms sensitive query redaction in final errors, response body cleanup on retry exhaustion, and major auth policy branches for Docker/ECR responses.
<!-- END_FILE_RESEARCH: sources/cloud-native/soci-snapshotter/service/resolver/client_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/soci-snapshotter/service/resolver/cri.go -->
# sources/cloud-native/soci-snapshotter/service/resolver/cri.go

Purpose: CRI-compatible registry host configuration and auth parsing for SOCI resolver. It ports containerd CRI registry config behavior to build `docker.RegistryHost` lists with mirrors, TLS, auth, and config-path support.

Important APIs/types/functions: config structs `Registry`, `Mirror`, `RegistryConfig`, `AuthConfig`, and `TLSConfig`. Main builder `RegistryHostsFromCRIConfig` returns `RegistryHosts`. Helpers include `hostDirFromRoots`, `toRuntimeAuthConfig`, `getTLSConfig`, `addDefaultScheme`, `registryEndpoints`, `ParseAlphaAuth`, and `ParseAuth`.

Control flow: if `ConfigPath` is set, host configuration delegates to containerd `ConfigureHosts` with a multi-credential callback combining external keychains and static auth config. Otherwise, for each mirror/default endpoint, it parses URL, applies registry TLS config to a retryable client's transport, creates a Docker authorizer with credentials, defaults path to `/v2`, and returns pull/resolve-capable registry hosts. Endpoint resolution applies host-specific or wildcard mirrors, adds default schemes, and appends Docker default host if not already present.

State and persistence: no persistent state; reads CA/cert/key files while constructing TLS config.

Dependencies/integration points: used by plugin and service resolver setup. Integrates containerd remotes/docker, Docker config host-dir support, CRI runtime `AuthConfig`, retryablehttp, TLS/x509, filesystem certificate files, and project credential chain helpers.

Risks: mirror/config behavior is copied from older containerd CRI versions and may drift from current containerd semantics. `TLSConfig.InsecureSkipVerify` is supported and can weaken verification. Static auth in `config.Configs[host]` is only appended in ConfigPath mode; non-ConfigPath mode relies on passed credential functions. Auth parsing trims NUL bytes from decoded password.

Test signals: this file has no direct tests in the listed set; auth parsing and registry behavior need coverage through resolver/plugin integration tests.
<!-- END_FILE_RESEARCH: sources/cloud-native/soci-snapshotter/service/resolver/cri.go -->
