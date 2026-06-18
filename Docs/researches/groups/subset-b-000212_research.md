# subset-b-000212 research

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/nydus-snapshotter/pkg/remote/remotes/docker/authorizer.go -->
# sources/cloud-native/nydus-snapshotter/pkg/remote/remotes/docker/authorizer.go

## Purpose
Implements Docker Registry authentication for the local remotes resolver. It reacts to `WWW-Authenticate` challenges, builds Basic or Bearer credentials, caches per-host handlers, and fetches scoped tokens for repository pull/push operations.

## Important APIs, Types, And Functions
`NewDockerAuthorizer`, `WithAuthClient`, `WithAuthCreds`, `WithAuthHeader`, and `WithFetchRefreshToken` construct the authorizer. `dockerAuthorizer.Authorize` injects the `Authorization` header, and `AddResponses` learns challenges from 401 responses. `authHandler.doBasicAuth` and `doBearerAuth` implement the two schemes. `invalidAuthorization` detects repeated failed credentials.

## Control Flow
Requests initially run unauthenticated. On 401, `AddResponses` parses challenges, gets credentials for the registry host, builds common token options, and stores an `authHandler`. Later `Authorize` asks that handler for the correct header. Bearer auth derives current scopes from context, caches one `authResult` per joined scope string, and uses a wait group so concurrent callers share one token fetch. OAuth POST is preferred when a secret is available, with GET fallback for registries that reject POST.

## State And Persistence
State is in memory only: a host-to-handler map and each handler's scoped token cache. Mutexes protect handler lookup and token fetch coordination. Refresh tokens are exposed through a callback but not persisted here.

## Dependencies And Integration Points
Depends on the package-local `auth` subpackage for challenge parsing and token requests, `remote/remotes/errors` for status inspection, and `scope.go` context values for repository scopes. It is wired into `RegistryHost.Authorizer` and used by `request.doWithRetries`.

## Risks And Edge Cases
The token cache has no expiry awareness in this file, so expiry handling depends on retrying after registry rejection. Basic auth refuses empty username or secret. `invalidAuthorization` only treats repeated same-request challenge errors as invalid credentials to avoid rejecting first challenges and redirect flows.

## Test Signals
`resolver_test.go` exercises Basic auth, anonymous bearer tokens, password/refresh-token OAuth, GET fallback, bad-token rejection, and refresh-token callback behavior.
<!-- END_FILE_RESEARCH: sources/cloud-native/nydus-snapshotter/pkg/remote/remotes/docker/authorizer.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/nydus-snapshotter/pkg/remote/remotes/docker/config/config_unix.go -->
# sources/cloud-native/nydus-snapshotter/pkg/remote/remotes/docker/config/config_unix.go

## Purpose
Provides Unix, non-Windows host configuration helpers for Docker registry host directory discovery and system certificate pool loading.

## Important APIs, Types, And Functions
`hostPaths(root, host)` returns candidate registry config directories, including Docker's port-mangled directory form and `_default`. `rootSystemPool` delegates to `x509.SystemCertPool`.

## Control Flow
`HostDirFromRoot` in `hosts.go` calls `hostPaths` in order. For `host:port`, `hostDirectory` turns it into `host_port_`, and this Unix implementation tries that directory before the literal host and `_default`.

## State And Persistence
No state is held. It only maps filesystem paths and returns the OS certificate pool used by TLS setup.

## Dependencies And Integration Points
Used by `ConfigureHosts` when loading `hosts.toml`, `.crt`, `.cert`, and `.key` files from Docker-style cert directories. It is selected by the `!windows` build tag.

## Risks And Edge Cases
Path ordering determines which cert directory wins. System certificate loading can fail depending on OS trust store availability and is surfaced to host configuration.

## Test Signals
Covered indirectly by `hosts_test.go` on Unix platforms through default host directory and certificate-file parsing behavior.
<!-- END_FILE_RESEARCH: sources/cloud-native/nydus-snapshotter/pkg/remote/remotes/docker/config/config_unix.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/nydus-snapshotter/pkg/remote/remotes/docker/config/config_windows.go -->
# sources/cloud-native/nydus-snapshotter/pkg/remote/remotes/docker/config/config_windows.go

## Purpose
Provides Windows-specific host directory and TLS root-pool behavior for registry host configuration.

## Important APIs, Types, And Functions
`hostPaths(root, host)` produces Windows-compatible paths by removing colons after Docker-style port mangling. `rootSystemPool` returns a new empty `x509.CertPool`.

## Control Flow
The Windows implementation tries a colon-free port directory, a colon-free literal host directory, and `_default`. TLS CA material is then populated from configured cert files instead of the platform system pool.

## State And Persistence
No runtime state. It only participates in filesystem lookup and TLS setup.

## Dependencies And Integration Points
Compiled only on Windows and used by `HostDirFromRoot` plus `ConfigureHosts` in `hosts.go`.

## Risks And Edge Cases
The empty root pool means configured CA files are especially important for private registries. Colon-stripping can make host-directory names differ from Unix, so cross-platform config layouts must account for that.

## Test Signals
No dedicated Windows-only test is present in this subset; behavior is structurally parallel to Unix and validated indirectly by shared host parser tests where platform path conversion applies.
<!-- END_FILE_RESEARCH: sources/cloud-native/nydus-snapshotter/pkg/remote/remotes/docker/config/config_windows.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/nydus-snapshotter/pkg/remote/remotes/docker/config/docker_fuzzer_internal.go -->
# sources/cloud-native/nydus-snapshotter/pkg/remote/remotes/docker/config/docker_fuzzer_internal.go

## Purpose
Adds a go-fuzz entry point for the Docker `hosts.toml` parser and cert-file path handling.

## Important APIs, Types, And Functions
`FuzzParseHostsFile(data []byte) int` uses `go-fuzz-headers` to create a temporary file tree and parser input, then calls `parseHostsFile`.

## Control Flow
The fuzzer creates a temp directory, asks the fuzz consumer to populate files, pulls remaining bytes as TOML content, invokes the parser, and ignores parser errors. It returns `1` for inputs that reached the parser and `0` for setup failures.

## State And Persistence
Temporary directories and generated files are removed with `defer os.RemoveAll`. No repository state is modified.

## Dependencies And Integration Points
Compiled only with the `gofuzz` build tag. It targets private parser code in `hosts.go`, including relative path resolution and type-switch handling for CA/client/header fields.

## Risks And Edge Cases
The fuzzer is useful for panics and parser robustness, but it does not assert semantic results or TLS loading behavior. Setup failures return without exercising the parser.

## Test Signals
Complements `hosts_test.go`, which covers deterministic valid configurations; this fuzz target broadens malformed input coverage.
<!-- END_FILE_RESEARCH: sources/cloud-native/nydus-snapshotter/pkg/remote/remotes/docker/config/docker_fuzzer_internal.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/nydus-snapshotter/pkg/remote/remotes/docker/config/hosts.go -->
# sources/cloud-native/nydus-snapshotter/pkg/remote/remotes/docker/config/hosts.go

## Purpose
Builds a `docker.RegistryHosts` function from Docker/containerd host configuration. It supports `hosts.toml`, Docker cert-directory fallback, custom credentials, default TLS/client setup, headers, mirrors, capabilities, and Docker Hub/default-host normalization.

## Important APIs, Types, And Functions
`HostOptions`, `ConfigureHosts`, `HostDirFromRoot`, `loadHostDir`, `parseHostsFile`, `parseHostConfig`, `loadCertFiles`, and helper conversion functions form the API. Internal `hostConfig` and `hostFileConfig` model parsed registry endpoints.

## Control Flow
`ConfigureHosts` resolves a host directory, loads `hosts.toml` or cert files, appends a default host if needed, constructs a default transport/client, and attaches authorizers. For each host, it applies scheme/host/path/capabilities/header and clones the transport when host-specific TLS material is needed. `parseHostsFile` preserves TOML host order using line positions, parses mirror entries first, and appends root `server` config last. `parseHostConfig` normalizes missing schemes to HTTPS, appends `/v2` unless `override_path` is set, interprets capability strings, converts relative cert paths, and validates header/client shapes.

## State And Persistence
Configuration is read from the filesystem on each host lookup. Runtime state is held in created HTTP clients, TLS configs, and authorizers, with no file writes.

## Dependencies And Integration Points
Integrates with `docker.RegistryHost`, `docker.NewDockerAuthorizer`, containerd logging, `errdefs.ErrNotFound`, Go TLS/http transports, and `go-toml`. Host capabilities directly affect resolver, fetcher, pusher, and referrer selection.

## Risks And Edge Cases
`hosts.toml` parse failure silently falls back to cert files after logging, which can hide misconfiguration. TLS config cloning mutates a cloned transport but starts from a shared default config pointer. `skip_verify` is intentionally supported but security-sensitive. Empty configured host lists mean no endpoints, while nil host lists mean synthesize defaults.

## Test Signals
`hosts_test.go` validates Docker Hub defaults, ordered TOML host parsing, path/override behavior, capabilities, headers, CA/client cert variants, and legacy cert-directory fallback.
<!-- END_FILE_RESEARCH: sources/cloud-native/nydus-snapshotter/pkg/remote/remotes/docker/config/hosts.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/nydus-snapshotter/pkg/remote/remotes/docker/config/hosts_test.go -->
# sources/cloud-native/nydus-snapshotter/pkg/remote/remotes/docker/config/hosts_test.go

## Purpose
Validates registry host configuration parsing and Docker-compatible cert-directory fallback.

## Important APIs, Types, And Functions
Tests cover `ConfigureHosts`, `parseHostsFile`, `loadHostDir`, and comparison helpers `compareRegistryHost`, `compareHostConfig`, and `printHostConfig`.

## Control Flow
`TestDefaultHosts` checks that `docker.io` maps to `https://registry-1.docker.io/v2` with pull/resolve/push. `TestParseHostFile` feeds a rich TOML document, then compares the ordered host configs for mirrors, default server, headers, cert paths, client keypair variants, `skip_verify`, and `override_path`. `TestLoadCertFiles` creates temp Docker cert directories with `.crt`, `.cert`, and `.key` files and verifies fallback parsing.

## State And Persistence
Uses temporary directories for cert-file tests. No persistent state is modified.

## Dependencies And Integration Points
Imports `docker.HostCapability*` constants and `logtest` context. The expected values encode the contract consumed by resolver/fetcher/pusher host selection.

## Risks And Edge Cases
The test suite locks down host ordering, which is important because mirrors are tried before the default server. The embedded test private key is only file content for parser coverage, not used as a valid TLS identity in network tests.

## Test Signals
These are direct unit tests for config behavior and are strong signals for compatibility with containerd-style `hosts.toml` and Docker cert layouts.
<!-- END_FILE_RESEARCH: sources/cloud-native/nydus-snapshotter/pkg/remote/remotes/docker/config/hosts_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/nydus-snapshotter/pkg/remote/remotes/docker/converter.go -->
# sources/cloud-native/nydus-snapshotter/pkg/remote/remotes/docker/converter.go

## Purpose
Normalizes image manifests whose config descriptor uses legacy `application/octet-stream`, rewriting them to Docker schema2 config media type and storing the corrected manifest in the content store.

## Important APIs, Types, And Functions
`LegacyConfigMediaType` identifies the legacy media type. `ConvertManifest(ctx, store, desc)` is the main function.

## Control Flow
The function only handles Docker schema2 and OCI image manifests. It reads the manifest blob, unmarshals to `ocispec.Manifest`, returns unchanged if config media type is already modern, rewrites the config media type, marshals indented JSON, recalculates digest and size, creates GC labels for config and layers, and writes the new blob under `remotes.MakeRefKey`.

## State And Persistence
Writes a new content blob and labels into the content store. The original manifest is not deleted; comments note later GC will remove it.

## Dependencies And Integration Points
Uses containerd content APIs, image media-type constants, OCI descriptors, and `remotes.MakeRefKey`. This is a compatibility bridge for pull/import paths that expect schema2 config media type.

## Risks And Edge Cases
Manifest lists/indexes are intentionally skipped. Invalid JSON or missing content fails. Rewriting changes manifest digest, so callers must use the returned descriptor.

## Test Signals
`converter_fuzz.go` fuzzes `ConvertManifest` against random descriptors and local content stores. No regular unit test in this subset asserts positive rewrite content.
<!-- END_FILE_RESEARCH: sources/cloud-native/nydus-snapshotter/pkg/remote/remotes/docker/converter.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/nydus-snapshotter/pkg/remote/remotes/docker/converter_fuzz.go -->
# sources/cloud-native/nydus-snapshotter/pkg/remote/remotes/docker/converter_fuzz.go

## Purpose
Provides a go-fuzz entry point for `ConvertManifest`.

## Important APIs, Types, And Functions
`FuzzConvertManifest(data []byte) int` generates an OCI descriptor from fuzz input and invokes `ConvertManifest` against a local content store.

## Control Flow
The fuzzer suppresses warning logs, generates a descriptor, creates a temp directory, opens a containerd local store, calls `ConvertManifest`, ignores the result, and returns `1` if execution reached the converter.

## State And Persistence
Creates temporary local content store state. The code does not explicitly remove the temp directory, so fuzz runs may rely on the harness/environment for cleanup.

## Dependencies And Integration Points
Uses `go-fuzz-headers`, containerd local content store, OCI descriptors, and logrus log-level control.

## Risks And Edge Cases
The target mostly checks converter robustness for arbitrary descriptors and missing blobs. It does not validate semantic correctness of rewritten manifests.

## Test Signals
Useful for panic resistance around content reads, JSON unmarshalling, digest recalculation, and label generation paths.
<!-- END_FILE_RESEARCH: sources/cloud-native/nydus-snapshotter/pkg/remote/remotes/docker/converter_fuzz.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/nydus-snapshotter/pkg/remote/remotes/docker/errcode.go -->
# sources/cloud-native/nydus-snapshotter/pkg/remote/remotes/docker/errcode.go

## Purpose
Defines Docker distribution-style error codes, descriptors, error wrappers, and JSON envelope conversion.

## Important APIs, Types, And Functions
`ErrorCode`, `Error`, `ErrorDescriptor`, `Errors`, `ParseErrorCode`, `WithMessage`, `WithDetail`, `WithArgs`, and JSON marshal/unmarshal methods are the primary API.

## Control Flow
`ErrorCode` resolves metadata through descriptor maps populated in `errdesc.go`. `Errors.MarshalJSON` converts each element into a serializable `Error`, filling default messages. `Errors.UnmarshalJSON` decodes an `errors` array and collapses detail-less default-message entries back to bare `ErrorCode` values.

## State And Persistence
No persistent state here, but it depends on global descriptor registries initialized by `Register` in `errdesc.go`.

## Dependencies And Integration Points
Used by fetcher error handling to decode registry JSON errors and include server messages. The JSON shape matches Docker Registry API error envelopes.

## Risks And Edge Cases
Unknown text unmarshals to `ErrorCodeUnknown`. `Errors` is a slice of `error`, so callers must be prepared for `ErrorCode`, `Error`, or unknown wrapped errors. Error strings are for humans, not stable programmatic IDs.

## Test Signals
No direct tests in this subset, but `fetcher_test.go` verifies registry error envelopes can surface a server message when fetch requests fail.
<!-- END_FILE_RESEARCH: sources/cloud-native/nydus-snapshotter/pkg/remote/remotes/docker/errcode.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/nydus-snapshotter/pkg/remote/remotes/docker/errdesc.go -->
# sources/cloud-native/nydus-snapshotter/pkg/remote/remotes/docker/errdesc.go

## Purpose
Registers Docker distribution error descriptors and exposes descriptor lookup by group or globally.

## Important APIs, Types, And Functions
`Register`, `GetGroupNames`, `GetErrorCodeGroup`, `GetErrorAllDescriptors`, and variables such as `ErrorCodeUnknown`, `ErrorCodeUnsupported`, `ErrorCodeUnauthorized`, `ErrorCodeDenied`, `ErrorCodeUnavailable`, and `ErrorCodeTooManyRequests`.

## Control Flow
Package initialization calls `Register` for standard `errcode` descriptors. `Register` assigns monotonically increasing numeric codes, panics on duplicate values or codes, updates maps by code, value, and group, and returns the assigned `ErrorCode`. Query functions sort group names and descriptors by value.

## State And Persistence
Maintains process-global maps and `nextCode`, guarded by `registerLock` for registration. State is in memory only.

## Dependencies And Integration Points
Consumed by `errcode.go` for string/marshal behavior and by registry error decoding in fetch paths.

## Risks And Edge Cases
Registration panics on duplicates, which is acceptable during init but risky for dynamic extension. `GetErrorCodeGroup` sorts the backing slice in place, so callers should not rely on previous group order.

## Test Signals
No dedicated tests in this subset. Runtime coverage appears through JSON error decoding in fetcher tests.
<!-- END_FILE_RESEARCH: sources/cloud-native/nydus-snapshotter/pkg/remote/remotes/docker/errdesc.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/nydus-snapshotter/pkg/remote/remotes/docker/fetcher.go -->
# sources/cloud-native/nydus-snapshotter/pkg/remote/remotes/docker/fetcher.go

## Purpose
Implements registry content fetching for Docker/OCI manifests, blobs, external URLs, and digest-only fetches with HTTP range support.

## Important APIs, Types, And Functions
`dockerFetcher.Fetch`, `FetchByDigest`, `createGetReq`, and `open` are the core methods. `newHTTPReadSeeker` is used to provide seekable reads over repeated HTTP requests.

## Control Flow
`Fetch` filters pull-capable hosts, adds pull scope, and returns an HTTP read seeker. The seeker first tries descriptor `URLs`, then manifest endpoints for manifest media types, and finally blob endpoints. `FetchByDigest` performs HEAD/GET setup against `blobs/<digest>`, then falls back to `manifests/<digest>` with manifest accept headers. `open` sets Accept and Range headers, executes retries, decodes Docker error envelopes on non-2xx statuses, checks `Content-Range` when present, and otherwise discards bytes to emulate offset reads.

## State And Persistence
No durable state. It mutates request headers and relies on registry hosts, authorizers, and context scopes. Returned readers hold HTTP response bodies until closed.

## Dependencies And Integration Points
Integrates with `dockerBase.request`, `request.doWithRetries`, `scope.go`, Docker/OCI media types, `remote/remotes.FetcherByDigest`, and `httpreadseeker.go`.

## Risks And Edge Cases
If all hosts fail, the first error is returned and 404s are wrapped as not-found. External URLs use `http.DefaultClient` and only support HTTP(S). Range support is defensive because some registries advertise or ignore ranges inconsistently. Missing content length can lead to unknown-size seekers.

## Test Signals
`fetcher_test.go` covers offset reads, ignored and valid content ranges, invalid range errors, Docker error-envelope messages, plain status errors, and retry exhaustion for timeout/rate-limit statuses. `resolver_test.go` validates fetch and digest-fetch parity.
<!-- END_FILE_RESEARCH: sources/cloud-native/nydus-snapshotter/pkg/remote/remotes/docker/fetcher.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/nydus-snapshotter/pkg/remote/remotes/docker/fetcher_fuzz.go -->
# sources/cloud-native/nydus-snapshotter/pkg/remote/remotes/docker/fetcher_fuzz.go

## Purpose
Provides fuzz entry points for fetcher HTTP read behavior and Docker reference parsing.

## Important APIs, Types, And Functions
`FuzzFetcher(data []byte) int` builds an HTTP test server and reads through `dockerFetcher.open`. `FuzzParseDockerRef(data []byte) int` calls distribution reference parsing.

## Control Flow
For non-empty data, the fuzzer serves the bytes with content range/length headers, constructs a local registry host, opens offset zero, reads all bytes, and panics if length differs from input. The reference fuzzer simply parses arbitrary input and ignores errors.

## State And Persistence
Uses an ephemeral `httptest.Server`; no persistent state.

## Dependencies And Integration Points
Compiled under `gofuzz`. Exercises `dockerBase.request`, fetcher open logic, and distribution reference parsing.

## Risks And Edge Cases
Only offset zero is fuzzed, so it does not explore the discard/seek code paths. It checks length but not byte equality.

## Test Signals
Complements `fetcher_test.go` by expanding input bytes and server content sizes for panic detection.
<!-- END_FILE_RESEARCH: sources/cloud-native/nydus-snapshotter/pkg/remote/remotes/docker/fetcher_fuzz.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/nydus-snapshotter/pkg/remote/remotes/docker/fetcher_test.go -->
# sources/cloud-native/nydus-snapshotter/pkg/remote/remotes/docker/fetcher_test.go

## Purpose
Tests `dockerFetcher.open` around range handling, content-length reporting, server errors, and retry behavior.

## Important APIs, Types, And Functions
`TestFetcherOpen` and `TestDockerFetcherOpen` are the main tests.

## Control Flow
`TestFetcherOpen` serves random 128-byte content and varies server behavior: no range, matching content range, last byte, EOF-sized offset, and mismatched range. `TestDockerFetcherOpen` serves configured status codes and JSON bodies to assert Docker error envelope formatting, plain status formatting, and retry counts for request timeout and too many requests.

## State And Persistence
Uses local HTTP test servers only.

## Dependencies And Integration Points
Targets `dockerFetcher`, `RegistryHost`, `dockerBase.request`, Docker `Errors`, and `request.doWithRetries`.

## Risks And Edge Cases
The tests validate critical compatibility with registries that ignore range headers, but they do not cover external descriptor URLs or multi-host fallback directly.

## Test Signals
Strong direct coverage for fetch offset semantics and error reporting, including the five-response retry cap inherited from `request.retryRequest`.
<!-- END_FILE_RESEARCH: sources/cloud-native/nydus-snapshotter/pkg/remote/remotes/docker/fetcher_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/nydus-snapshotter/pkg/remote/remotes/docker/handler.go -->
# sources/cloud-native/nydus-snapshotter/pkg/remote/remotes/docker/handler.go

## Purpose
Adds Docker distribution source-label support so pulled blobs/configs remember source repositories and future pushes can attempt cross-repository blob mounts.

## Important APIs, Types, And Functions
`AppendDistributionSourceLabel`, `appendDistributionSourceLabel`, `distributionSourceLabelKey`, `selectRepositoryMountCandidate`, and `commonPrefixComponents`.

## Control Flow
`AppendDistributionSourceLabel` parses the image reference into source host and repository, then returns an image handler. For each descriptor, it reads current content info, appends the repo into the source label, validates label size/format, and updates that label. Push code later reads descriptor annotations derived from these labels and `selectRepositoryMountCandidate` picks a different source repo with the longest common path-prefix match.

## State And Persistence
Persists labels in the content manager under `containerd.io/distribution.source.<host>`. The label value is a sorted, deduplicated comma-separated repo list.

## Dependencies And Integration Points
Uses containerd content manager, image handlers, label validation, and reference parsing. It integrates with `remotes.annotateDistributionSourceHandler` and `dockerPusher` mount-from flow.

## Risks And Edge Cases
Long labels may exceed containerd label validation and are skipped with a warning. The insertion-sort dedupe treats empty repos specially. Mount candidate selection excludes the target repo but otherwise trusts label content.

## Test Signals
`handler_test.go` validates label append/dedupe/sort behavior, label key construction, common-prefix counting, and mount candidate selection.
<!-- END_FILE_RESEARCH: sources/cloud-native/nydus-snapshotter/pkg/remote/remotes/docker/handler.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/nydus-snapshotter/pkg/remote/remotes/docker/handler_test.go -->
# sources/cloud-native/nydus-snapshotter/pkg/remote/remotes/docker/handler_test.go

## Purpose
Tests distribution-source label manipulation and blob mount candidate selection helpers.

## Important APIs, Types, And Functions
`TestAppendDistributionLabel`, `TestDistributionSourceLabelKey`, `TestCommonPrefixComponents`, and `TestSelectRepositoryMountCandidate`.

## Control Flow
The tests assert that label values are deduplicated and sorted, empty repo entries are removed, generated keys include the source host suffix, prefix matching counts path components, and mount candidate selection ignores the target repo while choosing the best available alternate source.

## State And Persistence
No persistent state; all inputs are in-memory strings and reference specs.

## Dependencies And Integration Points
Uses containerd label constants and reference specs. These helpers are consumed by pull labeling and pusher cross-repository mount attempts.

## Risks And Edge Cases
The tested candidate selection is intentionally simple and string-based; it does not verify repository existence or permissions.

## Test Signals
Direct coverage for helper behavior that affects performance and bandwidth during pushes but not content correctness.
<!-- END_FILE_RESEARCH: sources/cloud-native/nydus-snapshotter/pkg/remote/remotes/docker/handler_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/nydus-snapshotter/pkg/remote/remotes/docker/httpreadseeker.go -->
# sources/cloud-native/nydus-snapshotter/pkg/remote/remotes/docker/httpreadseeker.go

## Purpose
Provides a seekable, retrying `io.ReadCloser` wrapper over HTTP range requests.

## Important APIs, Types, And Functions
`newHTTPReadSeeker`, `httpReadSeeker.Read`, `Seek`, `Close`, and internal `reader` implement the behavior.

## Control Flow
The reader lazily opens the current offset using the supplied `open(offset)` callback. `Seek` closes any active body and updates the offset. `Read` advances the offset by bytes read; on `io.ErrUnexpectedEOF`, it closes the body and attempts to reopen at the current offset, allowing up to `maxRetry` no-progress retries. If the current offset equals known size, it returns an empty reader instead of making another HTTP request.

## State And Persistence
State is in-memory: size, current offset, active read closer, closed flag, and no-progress retry count.

## Dependencies And Integration Points
Used by `dockerFetcher.Fetch` and `FetchByDigest`. Depends on `errdefs` for closed/invalid seek errors and logging for close failures.

## Risks And Edge Cases
No synchronization is provided, so it is not safe for concurrent reads/seeks. Unknown-size readers cannot seek from end. Retrying unexpected EOF can mask transient connection drops but may loop until retry cap if the server repeatedly makes no progress.

## Test Signals
No dedicated test file in this subset, but fetcher tests exercise offset reopen behavior through `dockerFetcher.open`.
<!-- END_FILE_RESEARCH: sources/cloud-native/nydus-snapshotter/pkg/remote/remotes/docker/httpreadseeker.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/nydus-snapshotter/pkg/remote/remotes/docker/pusher.go -->
# sources/cloud-native/nydus-snapshotter/pkg/remote/remotes/docker/pusher.go

## Purpose
Implements Docker registry push support for blobs and manifests, including existence checks, upload sessions, cross-repository mount attempts, streaming writers, and in-memory upload status tracking.

## Important APIs, Types, And Functions
`dockerPusher.Writer`, `Push`, `push`, `getManifestPath`, `pushWriter` methods, and `requestWithMountFrom` are core. It uses `StatusTracker` from `status.go`.

## Control Flow
`push` locks by ref when possible, adds push scope, checks tracker state, filters push-capable hosts, and HEAD-checks existing content. Manifests are pushed with a PUT to `manifests/<tag-or-digest>`. Blobs start with POST to `blobs/uploads/`, optionally first trying `mount`/`from` based on source annotations. It follows the upload `Location`, appends `digest`, and creates a `pushWriter` backed by an `io.Pipe`. A goroutine performs the final PUT while the caller writes content through the writer. `Commit` closes the pipe, waits for response/error/reset, checks status, size, and `Docker-Content-Digest`, then marks the tracker committed.

## State And Persistence
Status is kept in the provided tracker: ref, total, expected digest, offset, start/update times, commit flag, close error, and upload UUID field. Registry state changes are remote writes. No local durable upload resume is implemented.

## Dependencies And Integration Points
Integrates with registry requests/auth/retries, content writer API, remotes ref keys, distribution-source labels from `handler.go`, and `remote/remotes/errors`.

## Risks And Edge Cases
Chunked upload/resume is TODO. Redirecting upload locations strip the authorizer when host/scheme changes, which avoids credential leakage but can fail if redirected host needs auth. `Commit` waits without timeout. Incomplete close records `ErrClosed` so later retries are allowed.

## Test Signals
`pusher_test.go` covers manifest path selection, retry after closed incomplete upload, reset after timeout, already-exists handling, manifest push, blob push, and mock registry status flows.
<!-- END_FILE_RESEARCH: sources/cloud-native/nydus-snapshotter/pkg/remote/remotes/docker/pusher.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/nydus-snapshotter/pkg/remote/remotes/docker/pusher_test.go -->
# sources/cloud-native/nydus-snapshotter/pkg/remote/remotes/docker/pusher_test.go

## Purpose
Tests Docker pusher upload paths, already-exists detection, reset behavior, and helper path generation.

## Important APIs, Types, And Functions
`TestGetManifestPath`, `TestPusherErrClosedRetry`, `TestPusherErrReset`, `Test_dockerPusher_push`, `samplePusher`, `tryUpload`, and `uploadableMockRegistry`.

## Control Flow
The mock registry handles minimal POST/PUT/HEAD registry APIs. Tests create a `dockerPusher`, toggle registry uploadability, write content through returned writers, and inspect commit errors or response channels. Reset testing forces the first PUT to return request timeout so `doWithRetries` replaces the pipe and the writer reports `content.ErrReset`.

## State And Persistence
Uses in-memory mock registry state (`availableContents`) and `NewInMemoryTracker`.

## Dependencies And Integration Points
Targets pusher behavior against actual `httptest.Server` HTTP paths and containerd content writer semantics.

## Risks And Edge Cases
The mock is intentionally small and does not exercise auth, upload redirects across hosts, mount-from success, or resumable/chunked uploads.

## Test Signals
Strong coverage for high-risk writer state transitions: incomplete close retry, reset and rewrite, remote already-exists, and digest-confirmed commit.
<!-- END_FILE_RESEARCH: sources/cloud-native/nydus-snapshotter/pkg/remote/remotes/docker/pusher_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/nydus-snapshotter/pkg/remote/remotes/docker/referrers.go -->
# sources/cloud-native/nydus-snapshotter/pkg/remote/remotes/docker/referrers.go

## Purpose
Implements OCI artifact referrers fetching for Docker registry fetchers, with fallback to the older tag-based referrers convention.

## Important APIs, Types, And Functions
`dockerFetcher.FetchReferrers(ctx, dgst, artifactTypes...)` implements the `remotes.ReferrersFetcher` interface.

## Control Flow
The method filters hosts with resolve or referrers capability, adds pull scope, tries `GET /referrers/<digest>` with repeated `artifactType` query params and namespace proxy query when needed, and returns an image index descriptor with size from response. If not found and the host can resolve, it falls back to `GET /manifests/<digest-with-colon-replaced>`.

## State And Persistence
No state is persisted. Returned descriptor intentionally lacks digest because the referrers endpoint does not define a digest header.

## Dependencies And Integration Points
Uses `dockerFetcher.open`, host capability filtering, `scope.go`, OCI image index media type, and the `ReferrersFetcher` interface in `remote/remotes/resolver.go`.

## Risks And Edge Cases
The code currently attempts the referrers endpoint regardless of whether `HostCapabilityReferrers` is set, as the guard is commented out. Multiple artifact types are encoded as repeated query keys. Non-404 errors stop fallback.

## Test Signals
No dedicated tests in this subset. Behavior is structurally tied to fetcher open/error handling.
<!-- END_FILE_RESEARCH: sources/cloud-native/nydus-snapshotter/pkg/remote/remotes/docker/referrers.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/nydus-snapshotter/pkg/remote/remotes/docker/registry.go -->
# sources/cloud-native/nydus-snapshotter/pkg/remote/remotes/docker/registry.go

## Purpose
Defines registry host configuration, host capability flags, default registry generation, host matching helpers, and registry-host composition.

## Important APIs, Types, And Functions
`HostCapabilities`, `RegistryHost`, `RegistryHosts`, `Registries`, `RegistryOpt`, `WithPlainHTTP`, `WithAuthorizer`, `WithHostTranslator`, `WithClient`, `ConfigureDefaultRegistries`, `MatchAllHosts`, and `MatchLocalhost`.

## Control Flow
`ConfigureDefaultRegistries` returns a resolver function that builds one `RegistryHost` with HTTPS `/v2`, all core capabilities, default client, optional plain HTTP, optional host translation, and Docker Hub translation to `registry-1.docker.io`. `Registries` tries configured registry functions in order and returns the first non-empty result. `RegistryHost.isProxy` determines whether namespace query injection is needed.

## State And Persistence
No persistent state. Functions return immutable host config values except embedded clients/authorizers.

## Dependencies And Integration Points
Registry hosts are consumed by resolver/fetcher/pusher/referrers code. Capabilities control trust boundaries for pull, resolve, push, and referrers operations.

## Risks And Edge Cases
Resolve capability is security-sensitive because a mirror that can return arbitrary tag-to-digest mappings should not be trusted. `MatchLocalhost` handles IPv4/IPv6/ports but intentionally does not support octal/decimal/hex IP forms.

## Test Signals
`registry_test.go` validates capability matching and localhost detection across common host formats and invalid addresses.
<!-- END_FILE_RESEARCH: sources/cloud-native/nydus-snapshotter/pkg/remote/remotes/docker/registry.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/nydus-snapshotter/pkg/remote/remotes/docker/registry_test.go -->
# sources/cloud-native/nydus-snapshotter/pkg/remote/remotes/docker/registry_test.go

## Purpose
Tests host capability bitmask matching and localhost detection.

## Important APIs, Types, And Functions
`TestHasCapability` targets `HostCapabilities.Has`. `TestMatchLocalhost` targets `MatchLocalhost`.

## Control Flow
Capability tests verify single and combined required capability masks. Localhost tests cover empty host, IPv4 loopback ranges, invalid IPv4, host:port, DNS names, localhost, bracketed IPv6, bare `::1`, and malformed port cases.

## State And Persistence
No state; pure unit tests.

## Dependencies And Integration Points
The tested helpers affect default resolver plain-HTTP behavior and host filtering for pull/resolve/push/referrers.

## Risks And Edge Cases
The tests document intentional non-matches for invalid or ambiguous addresses, reducing the chance that insecure HTTP is enabled for non-local registries.

## Test Signals
Direct unit coverage for small but security-relevant registry helper behavior.
<!-- END_FILE_RESEARCH: sources/cloud-native/nydus-snapshotter/pkg/remote/remotes/docker/registry_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/nydus-snapshotter/pkg/remote/remotes/docker/resolver.go -->
# sources/cloud-native/nydus-snapshotter/pkg/remote/remotes/docker/resolver.go

## Purpose
Implements the Docker registry resolver: reference resolution to descriptors, fetcher/pusher construction, HTTP request composition, retry/auth handling, proxy namespace query support, and default resolver setup.

## Important APIs, Types, And Functions
`ResolverOptions`, `NewResolver`, `dockerResolver.Resolve`, `Fetcher`, `Pusher`, `dockerBase`, `request.do`, `doWithRetries`, `retryRequest`, `getManifestMediaType`, `DefaultHost`, and `IsLocalhost`.

## Control Flow
`NewResolver` prepares headers, default user agent, Accept headers, tracker, and hosts. `Resolve` parses a Docker reference, builds candidate manifest/blob paths depending on tag or digest input, filters hosts by pull/resolve capability, adds pull scope, and issues HEAD requests. It trusts `Docker-Content-Digest` only for tag resolution from resolve-capable hosts; if digest or size is absent it GETs the content and computes digest, with schema1 signature stripping. Oversized manifests are rejected. `request.doWithRetries` handles 401 auth learning, HEAD-to-GET fallback for unsupported manifest HEAD, and retryable timeout/rate-limit statuses.

## State And Persistence
Resolver state is headers, host function, resolve headers, and upload tracker. Requests clone headers to avoid concurrent map access. No disk state is used.

## Dependencies And Integration Points
Implements `remote/remotes.Resolver` and returns `dockerFetcher`/`dockerPusher`. Integrates with registry host config, authorizers, schema1 converter helpers, OpenTelemetry tracing, content media types, and `remote/remotes/errors`.

## Risks And Edge Cases
Manifest digest computation by GET can consume up to response size before enforcing `MaxManifestSize`; the size guard follows the read. Retry recursion is capped by response count. Auth errors are rewritten for user-facing pull/push access denial. Header mutation in `NewResolver` removes Accept from general headers when provided.

## Test Signals
`resolver_test.go` covers HTTP/TLS, Basic and bearer token auth, refresh tokens, bad tokens, host fallback, TLS fallback, proxy namespace resolution, fetcher construction, digest fetches, and content verification.
<!-- END_FILE_RESEARCH: sources/cloud-native/nydus-snapshotter/pkg/remote/remotes/docker/resolver.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/nydus-snapshotter/pkg/remote/remotes/docker/resolver_test.go -->
# sources/cloud-native/nydus-snapshotter/pkg/remote/remotes/docker/resolver_test.go

## Purpose
Integration-style tests for Docker resolver authentication, host fallback, proxy namespace support, and fetch correctness.

## Important APIs, Types, And Functions
Tests include `TestHTTPResolver`, `TestHTTPSResolver`, auth-token variants, refresh token tests, fallback tests, proxy tests, and helpers `runBasicTest`, `testFetch`, `testocimanifest`, `withTokenServer`, `tlsServer`, and `refreshTokenServer`.

## Control Flow
The suite builds local registries with manifests/configs/layers, resolves an image tag, creates fetchers, verifies manifest children, and fetches each child by descriptor and by digest. Auth tests wrap registries with Basic or Bearer challenge flows and token endpoints. Fallback tests supply multiple hosts where the first fails or has the wrong TLS mode. Proxy tests verify namespace query routing.

## State And Persistence
Uses `httptest` HTTP/TLS servers and in-memory content structs. No durable state.

## Dependencies And Integration Points
Exercises resolver, authorizer, fetcher, registry host configuration, schema media type handling, and reference parsing as a coordinated system.

## Risks And Edge Cases
The tests are broad but still use simplified registry handlers. They do not cover every status-code path, manifest size rejection, or pusher behavior.

## Test Signals
This is the strongest signal that resolver/auth/fetch integration works across common registry modes and fallback scenarios.
<!-- END_FILE_RESEARCH: sources/cloud-native/nydus-snapshotter/pkg/remote/remotes/docker/resolver_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/nydus-snapshotter/pkg/remote/remotes/docker/schema1/converter.go -->
# sources/cloud-native/nydus-snapshotter/pkg/remote/remotes/docker/schema1/converter.go

## Purpose
Converts deprecated Docker schema1 manifests into OCI or Docker schema2 manifests during pull while fetching layer blobs, calculating diff IDs, detecting empty layers, and writing converted config/manifest content.

## Important APIs, Types, And Functions
`Converter`, `NewConverter`, `Handle`, `Convert`, `UseDockerSchema2`, `ReadStripSignature`, `fetchManifest`, `fetchBlob`, `reuseLabelBlobState`, `schema1ManifestHistory`, `isEmptyLayer`, `stripSignature`, and `blobStateCalculator`.

## Control Flow
`Handle` first fetches and parses schema1 manifests, validates history/layer counts, and returns non-empty layer descriptors in reverse order. For layer descriptors, it fetches or reuses blobs, decompresses content through a tee, calculates uncompressed diff ID and empty status, updates labels, and records mappings. `Convert` builds OCI history/rootfs from schema1 history, creates config and manifest descriptors, adds GC labels, and writes both blobs. Signature stripping reads up to 8MB, decodes the protected JWS block, and reconstructs unsigned manifest bytes.

## State And Persistence
The converter holds the pulled manifest plus maps from compressed digest to blob state and diff ID to layer descriptor. It writes fetched blobs via content writers, updates labels, and writes converted config/manifest blobs.

## Dependencies And Integration Points
Integrates with containerd content store, image media types, compression helpers, remotes fetcher/ref keys, labels, errgroup, OCI specs, and Docker schema1 compatibility in `resolver.go`.

## Risks And Edge Cases
Schema1 is deprecated and fragile. Signature stripping depends on legacy JWS protected metadata. Existing blobs without labels require decompression to reconstruct state. Empty-layer detection from history is conservative. Manifest size is capped at 8MB.

## Test Signals
No direct tests in this subset, but resolver digest computation uses `ReadStripSignature` for schema1 manifests. Behavior is inherited from containerd-style conversion logic.
<!-- END_FILE_RESEARCH: sources/cloud-native/nydus-snapshotter/pkg/remote/remotes/docker/schema1/converter.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/nydus-snapshotter/pkg/remote/remotes/docker/scope.go -->
# sources/cloud-native/nydus-snapshotter/pkg/remote/remotes/docker/scope.go

## Purpose
Builds and carries Docker registry authorization scopes through contexts so token requests receive the required repository permissions.

## Important APIs, Types, And Functions
`RepositoryScope`, `ContextWithRepositoryScope`, `WithScope`, `ContextWithAppendPullRepositoryScope`, and `GetTokenScopes`.

## Control Flow
`RepositoryScope` parses the reference locator and emits `repository:<repo>:pull` or `repository:<repo>:pull,push`. Context helpers append scopes under a private key. `GetTokenScopes` merges context scopes with challenge-provided common scopes, sorts them, and removes exact duplicates.

## State And Persistence
Scopes live only in derived contexts. No global or persistent state.

## Dependencies And Integration Points
Used by fetcher, resolver, pusher, referrers, and authorizer token generation. Pull/push and mount-from flows rely on correct scope composition.

## Risks And Edge Cases
Deduplication is exact string-based and does not normalize semantically equivalent scope actions such as `pull,push` versus `push,pull`. The context value is type-asserted to `[]string`, so only package helpers should set it.

## Test Signals
`scope_test.go` covers pull/push scope generation, duplicate removal, sorting, and custom scope composition.
<!-- END_FILE_RESEARCH: sources/cloud-native/nydus-snapshotter/pkg/remote/remotes/docker/scope.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/nydus-snapshotter/pkg/remote/remotes/docker/scope_test.go -->
# sources/cloud-native/nydus-snapshotter/pkg/remote/remotes/docker/scope_test.go

## Purpose
Tests Docker registry scope generation and scope aggregation from contexts.

## Important APIs, Types, And Functions
`TestRepositoryScope`, `TestGetTokenScopes`, and `TestCustomScope`.

## Control Flow
The tests create reference specs with and without ports, assert pull and pull/push repository scopes, then verify `GetTokenScopes` output for empty, common-only, context-only, duplicate, and mixed scope lists. Custom scope testing combines arbitrary scope with appended repository pull scope.

## State And Persistence
No state beyond context values.

## Dependencies And Integration Points
These tests protect the scopes consumed by `dockerAuthorizer.doBearerAuth` and registry token endpoints.

## Risks And Edge Cases
The tests document exact string ordering and dedupe semantics, including the lack of grammar-aware action normalization.

## Test Signals
Direct unit coverage for auth scope behavior across pull, push, and custom mount-related scope additions.
<!-- END_FILE_RESEARCH: sources/cloud-native/nydus-snapshotter/pkg/remote/remotes/docker/scope_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/nydus-snapshotter/pkg/remote/remotes/docker/status.go -->
# sources/cloud-native/nydus-snapshotter/pkg/remote/remotes/docker/status.go

## Purpose
Defines upload status tracking abstractions and an in-memory implementation for Docker pusher operations.

## Important APIs, Types, And Functions
`Status`, `StatusTracker`, `StatusTrackLocker`, `NewInMemoryTracker`, and `memoryStatusTracker` methods `GetStatus`, `SetStatus`, `Lock`, and `Unlock`.

## Control Flow
The tracker stores status by ref under a mutex. Missing refs return `errdefs.ErrNotFound`. The locker wraps a `moby/locker` keyed lock so push operations can serialize concurrent attempts for the same ref.

## State And Persistence
All status lives in memory: content status fields, committed flag, close error, and upload UUID. State is lost when the process exits.

## Dependencies And Integration Points
`dockerPusher` relies on this tracker to detect already committed content, active uploads, incomplete closes, offsets, and commit state.

## Risks And Edge Cases
No durable resume exists. Trackers that do not implement `StatusTrackLocker` can race in `dockerPusher.Writer`, as noted in comments. `UploadUUID` is defined but not actively used by current pusher code.

## Test Signals
Pusher tests exercise the default in-memory tracker through normal, retry, reset, and already-exists paths.
<!-- END_FILE_RESEARCH: sources/cloud-native/nydus-snapshotter/pkg/remote/remotes/docker/status.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/nydus-snapshotter/pkg/remote/remotes/errors/errors.go -->
# sources/cloud-native/nydus-snapshotter/pkg/remote/remotes/errors/errors.go

## Purpose
Defines a structured error type for unexpected HTTP statuses from registry API requests.

## Important APIs, Types, And Functions
`ErrUnexpectedStatus` and `NewUnexpectedStatusErr(resp *http.Response)` are the full API.

## Control Flow
`NewUnexpectedStatusErr` reads up to 64KB from the response body, captures status text/code, request method, and request URL, and returns an `ErrUnexpectedStatus`. `Error` formats the method, URL, and status.

## State And Persistence
No state. The response body is consumed when creating the error.

## Dependencies And Integration Points
Used by resolver, fetcher, pusher, and authorizer fallback logic. Authorizer inspects this concrete type to handle OAuth POST fallback statuses.

## Risks And Edge Cases
Because the body is read and stored, callers must not expect to reuse the response body after creating the error. Body capture is capped, avoiding unbounded memory use but truncating very large server messages.

## Test Signals
Fetcher and pusher tests indirectly verify error conversion and body inclusion in logs/messages.
<!-- END_FILE_RESEARCH: sources/cloud-native/nydus-snapshotter/pkg/remote/remotes/errors/errors.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/nydus-snapshotter/pkg/remote/remotes/handlers.go -->
# sources/cloud-native/nydus-snapshotter/pkg/remote/remotes/handlers.go

## Purpose
Provides generic remotes helper handlers for fetching, pushing, ref-key naming, platform/non-distributable filtering, and distribution-source annotation.

## Important APIs, Types, And Functions
`WithMediaTypeKeyPrefix`, `MakeRefKey`, `FetchHandler`, `Fetch`, `PushHandler`, `PushContent`, `SkipNonDistributableBlobs`, `FilterManifestByPlatformHandler`, and `annotateDistributionSourceHandler`.

## Control Flow
`MakeRefKey` chooses stable content writer refs by descriptor media type, annotation ref name, and optional context prefix. `FetchHandler` downloads descriptors into an ingester, while `Fetch` handles existing writers, inline descriptor data, size-zero rejection, and remote fetch copy. `PushContent` traverses children, records manifests and indexes so children upload before parents, annotates source labels when possible, dispatches pushes with a limiter, and reports missing index dependencies specially. Filtering handlers skip non-distributable blobs or keep only config for non-target platform manifests.

## State And Persistence
Fetch and push write to content stores or remote registries. Context can hold media-type ref prefixes. Source annotations are copied from content labels into descriptor annotations during push traversal.

## Dependencies And Integration Points
Central integration layer between containerd `images.Dispatch`, content stores, the local `Fetcher`/`Pusher` interfaces, platform matchers, Docker source-label helpers, and registry push/fetch implementations.

## Risks And Edge Cases
`Fetch` rejects descriptors reporting size zero, which may reject broken registries before attempting streaming. Push order is managed manually for manifests/indexes to satisfy registry dependency rules. Non-distributable filtering must preserve configs so manifests remain parseable.

## Test Signals
`handlers_test.go` covers custom ref-key prefixes and non-distributable filtering, including child descriptor filtering from a real local content store.
<!-- END_FILE_RESEARCH: sources/cloud-native/nydus-snapshotter/pkg/remote/remotes/handlers.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/nydus-snapshotter/pkg/remote/remotes/handlers_test.go -->
# sources/cloud-native/nydus-snapshotter/pkg/remote/remotes/handlers_test.go

## Purpose
Tests generic remotes handler helpers for ref-key prefixing and non-distributable blob filtering.

## Important APIs, Types, And Functions
`TestContextCustomKeyPrefix`, `TestSkipNonDistributableBlobs`, and `memoryLabelStore`.

## Control Flow
The ref-key test sets context prefixes for a built-in media type and a custom media type, then verifies built-in fallback, unknown fallback, override, and custom prefix behavior. The non-distributable test first filters a synthetic child list, then writes a manifest/config to a local labeled store and filters children returned by `images.ChildrenHandler`.

## State And Persistence
Uses temporary local content-store state and an in-memory label store. No persistent files beyond test temp directories.

## Dependencies And Integration Points
Targets `MakeRefKey`, `SkipNonDistributableBlobs`, containerd local content store, OCI descriptors, and image media-type classification.

## Risks And Edge Cases
The tests do not cover `PushContent` ordering or platform filtering, but they protect two commonly reused helper paths.

## Test Signals
Direct unit coverage for ref-key context customization and for filtering Windows/foreign/non-distributable layer media types while preserving config and distributable layers.
<!-- END_FILE_RESEARCH: sources/cloud-native/nydus-snapshotter/pkg/remote/remotes/handlers_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/nydus-snapshotter/pkg/remote/remotes/resolver.go -->
# sources/cloud-native/nydus-snapshotter/pkg/remote/remotes/resolver.go

## Purpose
Defines the core resolver/fetcher/pusher interfaces used by this repository's remote content layer.

## Important APIs, Types, And Functions
Interfaces: `Resolver`, `Fetcher`, `FetcherByDigest`, `ReferrersFetcher`, and `Pusher`. Function adapters: `FetcherFunc` and `PusherFunc`.

## Control Flow
The file contains interface contracts only. A resolver maps a reference to a descriptor and creates namespace-bound fetchers/pushers. Fetchers retrieve content by descriptor, optional digest-only fetchers retrieve with incomplete descriptors, referrers fetchers return artifact referrer indexes, and pushers return content writers.

## State And Persistence
No state. Implementations decide whether content is local, remote, streamed, or persisted.

## Dependencies And Integration Points
Implemented by `dockerResolver`, `dockerFetcher`, and `dockerPusher`. Consumed by generic handlers in `handlers.go`, schema1 converter, and higher-level snapshotter pull/push logic.

## Risks And Edge Cases
The interfaces intentionally leave retry, auth, descriptor completeness, and persistence behavior to implementations. Callers must inspect optional interfaces with type assertions.

## Test Signals
`resolver_test.go` checks that Docker fetchers implement and correctly satisfy `FetcherByDigest`.
<!-- END_FILE_RESEARCH: sources/cloud-native/nydus-snapshotter/pkg/remote/remotes/resolver.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/nydus-snapshotter/pkg/remote/unpack.go -->
# sources/cloud-native/nydus-snapshotter/pkg/remote/unpack.go

## Purpose
Extracts a named file from a compressed tar stream and writes it to a target path.

## Important APIs, Types, And Functions
`Unpack(reader io.Reader, source, target string) error` is the only API.

## Control Flow
The function wraps the input with containerd compression auto-detection, iterates tar headers, and when `hdr.Name` equals `source`, creates the target file and copies the tar entry content into it. If iteration reaches EOF without a match, it returns a not-found error.

## State And Persistence
Writes one output file at `target` and closes both decompressor and file. It does not create parent directories.

## Dependencies And Integration Points
Uses Go `archive/tar`, `os.Create`, and containerd compression helpers. Likely used to pull specific files such as bootstrap/config artifacts from layer blobs.

## Risks And Edge Cases
Exact tar header-name matching means path normalization is caller responsibility. Existing target files are truncated. It does not validate regular-file type, size limits, path safety, permissions, or parent directory existence.

## Test Signals
No tests in this subset. Risk should be managed by callers controlling `source` and `target`.
<!-- END_FILE_RESEARCH: sources/cloud-native/nydus-snapshotter/pkg/remote/unpack.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/nydus-snapshotter/pkg/resolve/resolver.go -->
# sources/cloud-native/nydus-snapshotter/pkg/resolve/resolver.go

## Purpose
Provides a higher-level resolver that turns an image reference and digest into an authenticated HTTP reader for the resolved blob.

## Important APIs, Types, And Functions
`Resolver`, `NewResolver`, `Resolver.Resolve`, and `newRetryHTTPClient`.

## Control Flow
`Resolve` parses a Docker reference, reconstructs a go-containerregistry reference from domain/path, builds a keychain from labels, asks a shared transport resolver for a URL and authenticated round tripper, creates a retryable GET request, executes it, requires HTTP 200, and returns the response body.

## State And Persistence
`Resolver` holds a transport resolve pool. No files are written; callers own closing the returned body.

## Dependencies And Integration Points
Uses repository auth labels through `pkg/auth`, transport resolution through `pkg/utils/transport`, go-containerregistry reference/keychain concepts, distribution reference parsing, and hashicorp retryable HTTP.

## Risks And Edge Cases
Only HTTP 200 is accepted, so partial-content/range responses are not expected here. Non-OK responses return without draining/closing the body in this function. Digest is passed to transport resolver but not independently verified while streaming.

## Test Signals
No direct tests in this subset. Stargz resolver tests cover a related transport resolver pattern with range reads.
<!-- END_FILE_RESEARCH: sources/cloud-native/nydus-snapshotter/pkg/resolve/resolver.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/nydus-snapshotter/pkg/signature/signature.go -->
# sources/cloud-native/nydus-snapshotter/pkg/signature/signature.go

## Purpose
Verifies Nydus bootstrap signatures stored in image labels, optionally enforcing that signatures are present.

## Important APIs, Types, And Functions
`Verifier`, `NewVerifier`, `Verifier.Verify`, and private `getFromLabel`.

## Control Flow
`NewVerifier` returns a passive verifier when validation is disabled. When validation is enabled, it requires a public key path, reads the key, and initializes a signer verifier. `Verify` decodes the base64 signature from `label.NydusSignature`; missing signature is allowed unless `force` is true. If a signer exists and signature exists, it opens the bootstrap file and verifies it.

## State And Persistence
The verifier stores a signer and force flag. It reads public key and bootstrap files but writes nothing.

## Dependencies And Integration Points
Integrates with Nydus label constants and `pkg/utils/signer`. Used by bootstrap/image validation paths that need supply-chain integrity checks.

## Risks And Edge Cases
When validation is disabled, a present signature is ignored because signer is nil. Missing signature enforcement only happens when `force` is true. Base64 decoding errors surface directly. File existence is checked during verifier construction for the public key and during verification for the bootstrap.

## Test Signals
No active tests in this subset. A commented older function documents previous inline verification flow.
<!-- END_FILE_RESEARCH: sources/cloud-native/nydus-snapshotter/pkg/signature/signature.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/nydus-snapshotter/pkg/snapshot/storage.go -->
# sources/cloud-native/nydus-snapshotter/pkg/snapshot/storage.go

## Purpose
Wraps containerd snapshot metadata-store operations for reading, updating, and walking snapshot metadata.

## Important APIs, Types, And Functions
`WalkFunc`, `GetSnapshotInfo`, `GetSnapshot`, `IterateParentSnapshots`, and `UpdateSnapshotInfo`.

## Control Flow
Read functions open read-only metadata transactions, call containerd storage helpers, and roll back the transaction. `IterateParentSnapshots` walks from a key through parent links, invoking a callback with each id/info until it returns true or the chain ends. `UpdateSnapshotInfo` opens a writable transaction, updates selected fields, rolls back on update error, and commits on success.

## State And Persistence
Reads and writes snapshot metadata through `storage.MetaStore`. Update commits persist metadata changes. Rollback errors are logged.

## Dependencies And Integration Points
Uses containerd snapshots/storage APIs, containerd logging, repository errdefs, and pkg/errors wrapping. This is a helper layer for snapshotter metadata operations.

## Risks And Edge Cases
Read transactions always call rollback, which is correct for read-only cleanup but logs if rollback fails. Parent iteration returns repository `ErrNotFound` when no callback match is found. Update callers must pass precise field paths to avoid unintended metadata changes.

## Test Signals
No tests in this subset. Behavior depends heavily on containerd storage transaction guarantees.
<!-- END_FILE_RESEARCH: sources/cloud-native/nydus-snapshotter/pkg/snapshot/storage.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/nydus-snapshotter/pkg/stargz/resolver.go -->
# sources/cloud-native/nydus-snapshotter/pkg/stargz/resolver.go

## Purpose
Resolves remote stargz blobs and reads their table-of-contents data via HTTP range requests.

## Important APIs, Types, And Functions
`Resolver`, `NewResolver`, `Blob`, `Blob.GetTocOffset`, `Blob.ReadToc`, `GetDigest`, `GetImageReference`, `Resolver.GetBlob`, `parseFooter`, `resolve`, and `getSize`.

## Control Flow
`GetBlob` resolves a reference/digest/keychain into a `Blob`. `resolve` parses the Docker reference, obtains a URL and authenticated round tripper from the transport pool, determines blob size by requesting `Range: bytes=0-0` and parsing `Content-Range`, and returns a `SectionReader` backed by range GETs. `ReadToc` opens the stargz footer to find TOC offset, reads the compressed TOC region, creates a gzip reader with multistream disabled, expects the first tar entry to be `stargz.index.json`, and returns its contents.

## State And Persistence
No local persistence. The `Blob` holds image ref, digest, and a section reader that issues network range requests.

## Dependencies And Integration Points
Uses go-containerregistry auth/name, distribution reference parsing, Nydus transport resolver, `estargz.OpenFooter`, gzip/tar, and package logging. It supports lazy stargz metadata extraction for Nydus workflows.

## Risks And Edge Cases
`getSize` assumes `Content-Range` contains a slash and valid total size. Range requests accept any 2xx status, not specifically 206. Error messages say HEAD even though GET is used. Each range read creates a new request with a 15-second timeout.

## Test Signals
`resolver_test.go` uses a mock transport to validate size lookup, footer parsing, TOC range read, gzip/tar extraction, and expected TOC filename.
<!-- END_FILE_RESEARCH: sources/cloud-native/nydus-snapshotter/pkg/stargz/resolver.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/nydus-snapshotter/pkg/stargz/resolver_test.go -->
# sources/cloud-native/nydus-snapshotter/pkg/stargz/resolver_test.go

## Purpose
Tests stargz resolver range-reading and TOC discovery with a mock transport resolver.

## Important APIs, Types, And Functions
`TestResolver_resolve`, `MockResolver.Resolve`, and `mockRoundTripper.RoundTrip`.

## Control Flow
The test creates a resolver with mock URL/transport, builds a keychain from base64 credentials, resolves a stargz blob, reads the last 47-byte footer, parses the TOC offset, reads the TOC gzip range, opens it as a tar stream, and asserts the first entry is `stargz.index.json`.

## State And Persistence
Reads fixture files `testdata/stargzfooter.bin` and `testdata/stargztoc.bin`. No writes.

## Dependencies And Integration Points
Exercises `parseFooter`, `Resolver.resolve`, range handling, auth keychain setup, and stargz TOC extraction expectations.

## Risks And Edge Cases
The mock returns success for unspecified requests, so negative HTTP status and malformed header cases are not covered. The fixture sizes encode one known stargz layout.

## Test Signals
Direct positive-path coverage for remote stargz TOC resolution and partial range reads.
<!-- END_FILE_RESEARCH: sources/cloud-native/nydus-snapshotter/pkg/stargz/resolver_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/nydus-snapshotter/pkg/stargz/testdata/config/nydus.json -->
# sources/cloud-native/nydus-snapshotter/pkg/stargz/testdata/config/nydus.json

## Purpose
Provides test configuration for Nydus in direct registry-backed mode with blob cache, digest validation, xattrs, IO stats, amplified IO, and filesystem prefetch settings.

## Important APIs, Types, And Functions
This is JSON data, not code. Key fields are `device.backend.type=registry`, backend timeouts/retry limit, `device.cache.type=blobcache`, `mode=direct`, `digest_validate`, `iostats_files`, `enable_xattr`, `amplify_io`, and `fs_prefetch`.

## Control Flow
Consumers load this fixture as Nydus configuration. It describes runtime behavior rather than executing logic itself.

## State And Persistence
The cache work directory is an empty string, implying tests or callers fill or default it. Other fields configure runtime IO/cache behavior.

## Dependencies And Integration Points
Used by stargz/Nydus integration tests or fixtures that need a registry backend and blob cache configuration.

## Risks And Edge Cases
`auth` and `work_dir` are blank fixture values and should not be used as production defaults without caller substitution. Retry limit is zero, so tests using it may exercise no retry behavior.

## Test Signals
Acts as fixture data; no assertions live in this file.
<!-- END_FILE_RESEARCH: sources/cloud-native/nydus-snapshotter/pkg/stargz/testdata/config/nydus.json -->
