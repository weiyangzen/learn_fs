# Research Report: subset-b-000060

This grouped report covers the requested containerd remote Docker registry, generic remotes, and runtime source files. Each source file section is delimited for reconciliation into `Docs/researches/<source_path>_research.md`.

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/core/remotes/docker/errdesc.go -->
# sources/cloud-native/containerd/core/remotes/docker/errdesc.go

## Purpose
Defines the Docker registry error descriptor registry used by the package's distribution error model. It maps symbolic Docker error values such as `UNKNOWN`, `UNAUTHORIZED`, and `TOOMANYREQUESTS` to internal `ErrorCode` values, human messages, descriptions, and HTTP status codes.

## Important APIs, Types, And Functions
- Package globals `errorCodeToDescriptors`, `idToDescriptors`, and `groupToDescriptors` are the in-memory registries keyed by generated code, string value, and group.
- `ErrorCodeUnknown`, `ErrorCodeUnsupported`, `ErrorCodeUnauthorized`, `ErrorCodeDenied`, `ErrorCodeUnavailable`, and `ErrorCodeTooManyRequests` are registered during package initialization.
- `Register(group string, descriptor ErrorDescriptor) ErrorCode` assigns monotonic codes starting at `1000`, validates duplicate values/codes, stores the descriptor, and returns the code.
- `GetGroupNames`, `GetErrorCodeGroup`, and `GetErrorAllDescriptors` expose sorted descriptor views.

## Control Flow
Initialization registers known errors by calling `Register`. `Register` takes a mutex, assigns the next code, panics on duplicate descriptor value or generated code, updates all maps, then increments `nextCode`. Read APIs sort group names or descriptor slices before returning.

## State And Persistence
State is process-local and persistent for the package lifetime. It is guarded for writes by `registerLock`, but `GetErrorCodeGroup` sorts the backing slice in place, so callers should treat returned slices as read-only views of global state.

## Dependencies And Integration Points
Uses `net/http` status codes and the package's `ErrorCode`/`ErrorDescriptor` definitions from the Docker error model. The descriptors are consumed when parsing registry error bodies and building user-facing unexpected-status errors elsewhere in the Docker remotes package.

## Risks And Edge Cases
Duplicate registration panics at runtime, so additional error descriptors must use globally unique `Value` strings. Because descriptor groups are sorted in place, concurrent calls while third-party registration is happening could be sensitive, although normal registration happens during init.

## Test Signals
No direct test file is listed for this descriptor registry. Coverage is indirect through resolver/fetcher tests that expect Docker error bodies to surface meaningful messages and HTTP status wrappers.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/core/remotes/docker/errdesc.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/core/remotes/docker/fetcher.go -->
# sources/cloud-native/containerd/core/remotes/docker/fetcher.go

## Purpose
Implements Docker/OCI registry content retrieval. It provides `dockerFetcher.Fetch`, `FetchByDigest`, low-level HTTP opening, content-encoding decoding, range seeking, and optional parallel chunked downloads.

## Important APIs, Types, And Functions
- `dockerFetcher` wraps `*dockerBase` and implements `remotes.Fetcher`, `remotes.FetcherByDigest`, and, via `referrers.go`, `remotes.ReferrersFetcher`.
- `Fetch(ctx, desc)` returns an `io.ReadCloser` for descriptor content, trying descriptor URLs, manifest endpoints for manifest/index media types, then blob endpoints.
- `FetchByDigest(ctx, dgst, opts...)` fetches content by digest, probing blobs first and manifests second, and returns a best-effort descriptor.
- `open(ctx, req, mediatype, offset, lastHost)` is the core HTTP path. It sets `Accept`, `Accept-Encoding`, optional `Range`, applies the download limiter, validates status/range, optionally parallelizes reads, and decodes zstd/gzip/deflate responses.
- `pipe`, `pipeReader`, `pipeWriter`, `bufferPool`, and `newPipeWriter` implement the asynchronous buffered in-memory pipes used to order chunk results from concurrent range requests.
- `fnOnClose` releases limiter capacity and cancels parallel fetch work before closing the wrapped reader.

## Control Flow
`Fetch` first filters hosts with `HostCapabilityPull` and injects repository pull scope into context. The returned `httpReadSeeker` calls back with offsets. For each open, external URLs are attempted only for HTTP(S), then registry `GET /manifests/<digest>` for manifests/indexes, then `GET /blobs/<digest>`. `FetchByDigest` does a `HEAD`-first `createGetReq` over blobs and manifests to discover size, then creates a seekable reader.

`open` decides parallelism from `transfer.ImageResolverPerformanceSettings`. Small buffers, request bodies, missing/ignored ranges, or small content force single-stream mode. In parallel mode it splits the remaining body into chunks, queues chunk indexes, reuses the first response body for chunk zero, opens cloned range requests for later chunks, writes each chunk into ordered pipe readers, and exposes an `io.MultiReader` over those readers. It then wraps the stream with decoders in reverse `Content-Encoding` order.

## State And Persistence
Fetcher itself persists no content. It consumes shared resolver state: host list, repository, headers, performance settings, and download limiter. The custom pipe holds transient buffered chunk data and returns buffers to a pool. The limiter is acquired per in-flight request and released through close/error cleanup.

## Dependencies And Integration Points
Depends on Docker registry endpoints, `dockerBase.request`, retry/error helpers in `resolver.go`, OCI/Docker media-type helpers from `images`, descriptor metadata from OCI image spec, and `remotes` interfaces. Integrates with `httpreadseeker.go` for reconnectable seeking and with `handlers.go` when content is copied into a content store.

## Risks And Edge Cases
Parallel range handling is sensitive: ignored `Range` headers must collapse concurrency, incorrect `Content-Range` offsets must fail, and body/limiter cleanup must happen even when decoders fail. Encoded range responses can be tricky because the code decodes after parallel assembly. Descriptor URLs bypass registry auth and only allow HTTP(S). `FetchByDigest` returns incomplete descriptors when media type is unknown.

## Test Signals
`fetcher_test.go` covers offset handling, registries that ignore ranges, invalid ranges, parallel reads, retry of mid-stream request timeouts, close behavior after copy errors, zstd/gzip/deflate decoding chains, registry error messages, and limiter release on decoder errors. `fetcher_fuzz_test.go` fuzzes arbitrary payload fetches through an HTTP test server.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/core/remotes/docker/fetcher.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/core/remotes/docker/fetcher_fuzz_test.go -->
# sources/cloud-native/containerd/core/remotes/docker/fetcher_fuzz_test.go

## Purpose
Fuzzes the Docker fetcher's low-level `open` path with arbitrary non-empty payloads served from a local HTTP server.

## Important APIs, Types, And Functions
- `FuzzFetcher(f *testing.F)` is the fuzz entry point.
- The test constructs a `dockerFetcher`, a `RegistryHost`, and a raw `GET` request, then calls `f.open`.

## Control Flow
Each fuzz input becomes server response data with matching `Content-Range` and `Content-Length`. The test opens offset zero, reads the whole body, and fails if the returned length differs from the original fuzz input.

## State And Persistence
All state is per-fuzz-iteration and in memory. Each iteration starts and closes its own `httptest.Server`.

## Dependencies And Integration Points
Exercises `dockerFetcher.open`, `dockerBase.request`, HTTP response header parsing, range validation, and body reading. It intentionally avoids content store integration and digest validation to focus on fetch transport behavior.

## Risks And Edge Cases
The fuzz currently checks length rather than byte-for-byte equality, so it catches truncation/expansion but not all content mutations. It skips empty data and silently returns on setup/open/read errors, which makes it a robustness fuzz rather than a strict oracle for every input.

## Test Signals
Provides broad randomized coverage of response sizes and byte patterns for the fetch open path, complementing deterministic range and encoding tests in `fetcher_test.go`.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/core/remotes/docker/fetcher_fuzz_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/core/remotes/docker/fetcher_test.go -->
# sources/cloud-native/containerd/core/remotes/docker/fetcher_test.go

## Purpose
Validates Docker fetcher transport behavior: ranged reads, parallel chunk reads, content encoding, retry behavior, error formatting, and limiter cleanup.

## Important APIs, Types, And Functions
- `TestFetcherOpen` tests serial offset reads and server `Content-Range` handling.
- `TestFetcherOpenParallel` tests concurrent range fetching with configurable chunk size and max downloads.
- `TestFetcherOpenParallel_CloseAfterCopyError` ensures closing a parallel reader after downstream copy failure does not block on unfinished range workers.
- `TestContentEncoding` validates identity, zstd, gzip, deflate, and chained encodings.
- `TestDockerFetcherOpen` covers unexpected registry statuses, Docker error bodies, and retry counts for timeout/too-many-requests/5xx paths.
- `TestDockerFetcherOpenLimiterDeadlock` verifies limiter capacity is released when opening fails during decoding.
- `parseRange` and `httpRange` are test helpers implementing enough RFC 7233 range parsing for local servers.

## Control Flow
Tests create local HTTP servers that vary `Range`, `Content-Range`, `Content-Length`, status codes, and encodings. They construct a `dockerFetcher` with local `RegistryHost` data, call `open`, consume the reader, and compare output bytes or errors. Parallel tests inject transient failures after specific offsets to verify retry policy and error propagation.

## State And Persistence
Test state is local: random deterministic content buffers, atomic failure flags, a semaphore limiter, and server-side toggles. No persistent content store is used.

## Dependencies And Integration Points
Exercises the fetcher with `httptest`, `semaphore.Weighted`, `transfer.ImageResolverPerformanceSettings`, compression libraries, and Docker error serialization from the package.

## Risks And Edge Cases
The tests highlight important operational risks: remote registries may ignore range requests, return wrong ranges, omit content length, close early, or send unsupported/corrupt encodings. Parallel fetch cleanup is especially important because leaked goroutines or unreleased limiter slots can deadlock future pulls.

## Test Signals
This is the main behavioral safety net for fetcher changes. A notable regression guard is the limiter-deadlock test, which confirms failed gzip initialization releases the limiter so a second open can proceed.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/core/remotes/docker/fetcher_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/core/remotes/docker/handler.go -->
# sources/cloud-native/containerd/core/remotes/docker/handler.go

## Purpose
Manages distribution source labels and cross-repository mount candidate selection. These labels record where content came from so pushes can try efficient registry-side blob mounts instead of reuploading common layers.

## Important APIs, Types, And Functions
- `AppendDistributionSourceLabel(manager, ref)` returns an image handler that appends a repository to the content label `containerd.io/distribution.source.<host>`.
- `appendDistributionSourceLabel(originLabel, repo)` sorts and deduplicates comma-separated repository values.
- `distributionSourceLabelKey(source)` builds the label key.
- `selectRepositoryMountCandidate(refspec, sources)` selects the best source repository for a cross-repo mount by longest common path-prefix components.
- `commonPrefixComponents(components, target)` scores path similarity.

## Control Flow
`AppendDistributionSourceLabel` parses the reference, extracts registry host and repository, and returns a descriptor handler. The handler reads content info, builds the source-label value, validates label size/key rules, and updates only the target label field. Pusher code later examines descriptor annotations to choose a mount source.

## State And Persistence
State is persisted as content-store labels through `content.Manager.Update`. The append helper uses sorted strings to keep deterministic label values and collapse duplicates.

## Dependencies And Integration Points
Depends on `content.Manager`, `images.HandlerFunc`, `labels.Validate`, `reference.Parse`, and OCI descriptors. Integrates with generic remotes handler annotation propagation and `pusher.go` cross-repo mount logic.

## Risks And Edge Cases
Content labels have size limits, and widely shared layers can accumulate many source repositories; the handler logs and skips label updates when validation fails. Candidate selection intentionally skips the target repo and may choose a later equal-score repo because it uses `>=`.

## Test Signals
`handler_test.go` covers label append sorting/deduplication, label key construction, prefix scoring, and mount candidate selection.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/core/remotes/docker/handler.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/core/remotes/docker/handler_test.go -->
# sources/cloud-native/containerd/core/remotes/docker/handler_test.go

## Purpose
Tests the Docker distribution-source label helpers used for cross-repository mount optimization.

## Important APIs, Types, And Functions
- `TestAppendDistributionLabel` validates empty values, duplicate removal, insertion sorting, and empty-repo filtering.
- `TestDistributionSourceLabelKey` asserts the `labels.LabelDistributionSource + "." + source` format.
- `TestCommonPrefixComponents` checks prefix scoring.
- `TestSelectRepositoryMountCandidate` verifies candidate choice from source labels.

## Control Flow
The tests are table-driven and call unexported helpers directly. They construct small `reference.Spec` and label maps rather than exercising a real content store.

## State And Persistence
No persistent state. The tests validate pure string and map transformations.

## Dependencies And Integration Points
Depends on the label prefix constant and reference spec shape. It protects behavior relied on by `AppendDistributionSourceLabel` and `dockerPusher.push`.

## Risks And Edge Cases
Tests capture duplicate source entries and target-repository exclusion behavior, but they do not cover the content-manager update path or label validation overflow.

## Test Signals
Strong unit signal for deterministic label formatting and repository candidate scoring.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/core/remotes/docker/handler_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/core/remotes/docker/httpreadseeker.go -->
# sources/cloud-native/containerd/core/remotes/docker/httpreadseeker.go

## Purpose
Provides a reconnectable `io.ReadCloser`/`io.Seeker` abstraction for HTTP-backed content. It lazily opens a response at the current offset and can reopen after seeks or unexpected EOFs.

## Important APIs, Types, And Functions
- `httpReadSeeker` stores total size, current offset, active reader, open callback, closed flag, and retry count for no-progress errors.
- `newHTTPReadSeeker(size, open)` constructs the object.
- `Read` opens lazily, advances offset, retries on `io.ErrUnexpectedEOF`, and closes at EOF for progress tracking.
- `Seek` supports start/current/end when size is known, rejects negative offsets and invalid whence values, and closes existing bodies when moving.
- `reader` opens a new body unless offset is at/after known size, where it returns an empty reader.

## Control Flow
Reads call `reader`, then delegate to the active response body. On unexpected EOF, the current body is closed and a reopen is attempted at the same updated offset; repeated zero-progress failures are capped by `maxRetry`. Seeks mutate offset and clear the current body to force the next read to call the fetcher's open function.

## State And Persistence
All state is in-memory and per-reader. The active HTTP body is the only external resource; it is closed on EOF, explicit close, seek movement, and reconnect.

## Dependencies And Integration Points
Used by `dockerFetcher.Fetch` and `FetchByDigest` to expose seekable registry content to content copy paths. Uses containerd `errdefs` to classify closed/invalid seek errors and `log` for close failures.

## Risks And Edge Cases
Unknown-size readers cannot seek from end. Repeated unexpected EOF without progress eventually returns the error. Returning an empty reader at exact content size avoids unnecessary range requests but relies on caller size accounting.

## Test Signals
Covered indirectly by `fetcher_test.go` offset, EOF, and range scenarios. There is no dedicated test file for closed seek behavior.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/core/remotes/docker/httpreadseeker.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/core/remotes/docker/pusher.go -->
# sources/cloud-native/containerd/core/remotes/docker/pusher.go

## Purpose
Implements Docker/OCI registry push support for blobs and manifests. It handles existence checks, cross-repository mounts, upload start/commit requests, streaming request bodies, upload status tracking, and content writer semantics.

## Important APIs, Types, And Functions
- `dockerPusher` wraps `dockerBase`, target object, and `StatusTracker`.
- `Writer(ctx, opts...)` implements content ingester semantics, validating `Ref`, digest, and media type, then calling `push` with `unavailableOnFail`.
- `Push(ctx, desc)` returns a writer using `remotes.MakeRefKey`.
- `push(ctx, desc, ref, unavailableOnFail)` is the core push state machine.
- `getManifestPath(object, dgst)` decides whether to PUT a manifest by tag or digest.
- `pushWriter` implements `content.Writer` over an async `io.Pipe` request body.
- `requestWithMountFrom` clones a request and adds `mount`/`from` query parameters.

## Control Flow
`push` locks by ref when the tracker supports it, injects pull/push auth scope, checks existing tracker status, filters push-capable hosts, and chooses the first host. It sends a `HEAD` to the target manifest/blob endpoint; existing content marks tracker status and returns `ErrAlreadyExists`.

For manifests it prepares `PUT /manifests/<tag-or-digest>` with content type. For blobs it sends `POST /blobs/uploads/`, optionally first with `mount` and `from` from distribution source annotations plus an appended pull scope. A `201 Created` mount marks committed status and returns already-exists. Otherwise it parses `Location`, adjusts host/scheme if redirected, strips authorizer when destination changes, appends the digest query, and prepares final `PUT`.

The returned `pushWriter` receives a pipe from the request goroutine, writes user bytes into it, tracks offset, closes/commits the pipe, waits for response or error, validates response status, optional `Docker-Content-Digest`, size, and expected digest, then marks status committed.

## State And Persistence
Push state lives in `StatusTracker`, usually the in-memory tracker from `status.go`. It records offsets, expected digest, start/update times, committed state, close errors, and mount/existence status. Registry state is mutated through HTTP uploads/manifests. No chunked resumable upload is implemented yet.

## Dependencies And Integration Points
Depends on `content.Writer`, `remotes.MakeRefKey`, Docker registry upload APIs, auth scopes from `scope.go`, distribution labels from `handler.go`, request/retry helpers from `resolver.go`, and `errdefs` classification.

## Risks And Edge Cases
Only the first push-capable host is used. Redirected upload destinations remove authorizer if host/scheme changes, which avoids credential leakage but can fail private redirects. Incomplete close sets `ErrClosed` so retries are allowed. `Commit` has no explicit timeout while waiting for the request goroutine. Manifests and blobs use different existence checks; tag/digest object handling is subtle.

## Test Signals
`pusher_test.go` covers manifest path selection, retry after closed incomplete upload, namespace query propagation, missing digest header acceptance, HTTP fallback, `ErrReset`, unauthorized mount fallback, existing content, successful/failed cross-repo mount, and blob/manifest push flows.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/core/remotes/docker/pusher.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/core/remotes/docker/pusher_test.go -->
# sources/cloud-native/containerd/core/remotes/docker/pusher_test.go

## Purpose
Validates Docker pusher behavior across manifest uploads, blob uploads, existence checks, mount optimization, status tracking, auth/fallback handling, and writer retry/reset semantics.

## Important APIs, Types, And Functions
- `TestGetManifestPath` checks tag-vs-digest path construction.
- `TestPusherErrClosedRetry` ensures an upload closed with an error can be retried.
- `TestPusherCustomNamespace` verifies proxy namespace query propagation on final PUT.
- `TestPusherAcceptsMissingDigestHeader` confirms commit can succeed without `Docker-Content-Digest`.
- `TestPusherHTTPFallback` exercises HTTPS-to-HTTP fallback during push with basic auth.
- `TestPusherErrReset` verifies writer reset when a request must be retried.
- `TestPusherInvalidAuthorizationOnMount` verifies private-source mount auth failures fall back to normal upload.
- `Test_dockerPusher_push` covers manifest, existing content, mounted blob, failed mount, and normal blob push.
- `uploadableMockRegistry` is a small in-memory registry simulator.

## Control Flow
Tests build `samplePusher` backed by `httptest.Server`, then drive content through `Writer` or `push`. The mock registry implements minimal `HEAD`, `POST /blobs/uploads/`, and `PUT` behavior, including optional auth, omitted digest headers, mount responses, and upload failures.

## State And Persistence
The mock registry persists uploaded digest strings in memory. The pusher uses `NewInMemoryTracker`, and several assertions inspect tracker `PushStatus` values.

## Dependencies And Integration Points
Uses `content.Copy`, OCI descriptors/manifests, `remotes.MakeRefKey`, `reference.Spec`, and registry host configuration. It tests integration among `pusher.go`, `status.go`, `handler.go`, `scope.go`, and HTTP fallback in `resolver.go`.

## Risks And Edge Cases
The tests show the pusher must tolerate missing digest headers but reject mismatched digest headers, must recover from mount authorization failures, and must not confuse existing remote content with active local uploads.

## Test Signals
High-value integration signal for registry upload state transitions. It does not cover multi-host push fallback because production code selects the first push-capable host.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/core/remotes/docker/pusher_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/core/remotes/docker/referrers.go -->
# sources/cloud-native/containerd/core/remotes/docker/referrers.go

## Purpose
Implements OCI Distribution referrers discovery for Docker fetchers, including fallback to the legacy tag schema.

## Important APIs, Types, And Functions
- `FetchReferrers(ctx, dgst, opts...)` returns descriptors that refer to a subject digest.
- `openReferrers(ctx, dgst, config)` fetches the raw referrers index from `/referrers/<digest>` or fallback `/manifests/<digest-with-colon-replaced>`.
- `remotes.FetchReferrersConfig` options filter by artifact type and allow extra query filters.

## Control Flow
`FetchReferrers` applies options, opens the referrers index, returns an empty list for not-found, enforces `MaxManifestSize`, decodes exactly one OCI index JSON object, and optionally filters returned descriptors by `ArtifactType`.

`openReferrers` first chooses hosts with `HostCapabilityReferrers`; if none exist, it falls back to resolve-capable hosts. It adds `artifactType` and additional query filters to the referrers endpoint, appends namespace for proxy hosts, and opens using the fetcher's `open`. If the real endpoint is unavailable, it tries the tag fallback where `sha256:...` becomes `sha256-...`.

## State And Persistence
No state is persisted. It streams and decodes remote index content and returns descriptors.

## Dependencies And Integration Points
Depends on Docker fetcher transport, registry host capabilities, auth scopes, OCI `Index`, and generic remotes referrers options. Integrates with content fetches because returned descriptors can be fetched by the same fetcher.

## Risks And Edge Cases
Unknown content length is capped by `MaxManifestSize`; oversized indexes return an error wrapping not-found. The endpoint may return extra trailing JSON data, which is rejected. Query filters are trusted and appended directly through URL encoding. Fallback tags are compatibility behavior and may hide registry support differences.

## Test Signals
`referrers_test.go` covers normal referrers, missing content length, oversize errors, artifact-type filtering, descriptor fetchability, and fallback tag registration.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/core/remotes/docker/referrers.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/core/remotes/docker/referrers_test.go -->
# sources/cloud-native/containerd/core/remotes/docker/referrers_test.go

## Purpose
Tests fetching and filtering OCI referrers through the Docker resolver/fetcher stack.

## Important APIs, Types, And Functions
- `TestFetchReferrers` has subtests for basic behavior, missing length, and oversized index content.
- `runReferrersTest` builds a manifest subject and an OCI index of two referrer manifests.
- `testIndex` creates and registers OCI index descriptors.

## Control Flow
The test server registers subject manifest routes, `/referrers/<digest>`, fallback manifest tag routes, and blob/manifest routes for the referrer descriptors. It resolves an image by digest, obtains the fetcher, casts it to `remotes.ReferrersFetcher`, fetches referrers, fetches each returned descriptor, then repeats with an artifact-type filter.

## State And Persistence
Uses only test-server routes and in-memory payloads. No content store is written.

## Dependencies And Integration Points
Exercises `NewResolver`, `Resolve`, `Fetcher`, `FetchReferrers`, `Fetch`, artifact-type options, `MaxManifestSize`, and OCI descriptor/index encoding.

## Risks And Edge Cases
The missing-length case validates the size fallback to `MaxManifestSize`; the too-long case verifies bounded reads and not-found classification. Query-filter options are not deeply asserted beyond artifact type.

## Test Signals
Good integration coverage for both the referrers endpoint and fallback schema, including ability to fetch returned referrer manifests.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/core/remotes/docker/referrers_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/core/remotes/docker/registry.go -->
# sources/cloud-native/containerd/core/remotes/docker/registry.go

## Purpose
Defines registry host configuration, trust capabilities, default registry construction, localhost matching, and default HTTP transport settings for Docker remotes.

## Important APIs, Types, And Functions
- `HostCapabilities` bitmask values: pull, resolve, push, and referrers.
- `RegistryHost` carries HTTP client, authorizer, host, scheme, path, capabilities, and headers.
- `RegistryHosts` maps a namespace host to ordered registry hosts/mirrors.
- `Registries` chains multiple `RegistryHosts` providers and returns the first non-empty result.
- `RegistryOpt` helpers configure authorizer, plain HTTP match, host translation, and client.
- `ConfigureDefaultRegistries` builds default `/v2` HTTPS hosts, including Docker Hub translation to `registry-1.docker.io`.
- `MatchAllHosts`, `MatchLocalhost`, and `DefaultHTTPTransport` provide common defaults.

## Control Flow
Callers pass `ResolverOptions.Hosts` or let `NewResolver` call `ConfigureDefaultRegistries`. Host capabilities determine which hosts are trusted for resolve, pull, push, or referrers. `RegistryHost.isProxy` detects when `ns=` should be appended for proxy/mirror requests.

## State And Persistence
No persistent state. Each resolver holds host configuration returned from the provided function.

## Dependencies And Integration Points
Used by resolver, fetcher, pusher, and referrers host filtering. The transport config feeds HTTP clients and fallback wrappers. Capability comments encode the trust model: mirrors may be pull-only and should not resolve mutable names unless trusted.

## Risks And Edge Cases
`MatchLocalhost` intentionally does not support odd IP encodings and returns errors for malformed host:port forms. Misconfigured capabilities can create security issues, such as resolving tags through an untrusted mirror or pushing to a mirror.

## Test Signals
`registry_test.go` covers bitmask inclusion and localhost matching for IPv4, IPv6, host:port, invalid IPs, and non-local hosts.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/core/remotes/docker/registry.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/core/remotes/docker/registry_test.go -->
# sources/cloud-native/containerd/core/remotes/docker/registry_test.go

## Purpose
Tests registry capability bitmasks and localhost host matching.

## Important APIs, Types, And Functions
- `TestHasCapability` validates `HostCapabilities.Has` for individual and combined capability masks.
- `TestMatchLocalhost` validates `MatchLocalhost` across IPv4, IPv6, hostnames, ports, malformed values, and non-local hosts.

## Control Flow
The tests are table-driven, directly invoking bitmask and matching helpers.

## State And Persistence
No state is persisted.

## Dependencies And Integration Points
Protects behavior consumed by host filtering in resolver/fetcher/pusher/referrers and default plain-HTTP decisions in resolver construction.

## Risks And Edge Cases
The test explicitly ensures invalid loopback-looking IPs do not panic and malformed host:port values do not match.

## Test Signals
Focused unit coverage for the registry trust/capability primitives.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/core/remotes/docker/registry_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/core/remotes/docker/resolver.go -->
# sources/cloud-native/containerd/core/remotes/docker/resolver.go

## Purpose
Implements the Docker registry resolver and shared HTTP request machinery for resolving references, creating fetchers/pushers, authorizing requests, retrying transient failures, sanitizing logs, and falling back from HTTPS to HTTP for configured scenarios.

## Important APIs, Types, And Functions
- `Authorizer` defines `Authorize` and `AddResponses` for challenge-based auth.
- `ResolverOptions` configures hosts, headers, tracker, legacy credentials/authorizer/client/plain HTTP settings.
- `NewResolver` builds a `dockerResolver`, clones headers to avoid races, splits resolve `Accept` headers, and creates default registry hosts when needed.
- `Resolve(ctx, ref)` resolves a tag/digest to an OCI descriptor using trusted hosts.
- `Fetcher` and `Pusher` construct Docker fetcher/pusher instances for a ref.
- `dockerBase` stores parsed reference, repository, hosts, headers, performance settings, and download limiter.
- `request` builds and executes registry HTTP requests, with auth, body replay, redirect authorization, namespace query support, retries, and sanitized logging.
- `withErrorCheck`, `withOffsetCheck`, `doWithRetries`, `retryRequest`, and `doWithTransportRetries` implement response and transport retry policy.
- `IsLocalhost`, `NewHTTPFallback`, `isTLSError`, and `isPortError` support local registry HTTP fallback.

## Control Flow
`Resolve` parses the reference, decides endpoint paths (`/manifests/<object>` for tags, `/manifests/<digest>` then possibly `/blobs/<digest>` for digests), filters hosts by pull/resolve capability, injects pull scope, and iterates paths and hosts. It prefers errors by priority: transport/auth, not found, unexpected HTTP status, and oversize manifest. HEAD is used first; if digest/size are missing it GETs the manifest to compute digest or size. Schema1 manifests are rejected. The final descriptor includes digest, media type, and size, bounded by `MaxManifestSize`.

`request.do` constructs an HTTP request, clones headers, attaches replayable body, authorizes initial and redirect requests, applies tracing, and returns the response. `doWithRetries` combines transport retries, auth challenge retries, selected status retries, and caller checks. Status retries include auth challenge, HEAD-to-GET for manifest 405, 408/429, and selected 5xx only on the last host. Transport retries apply only on last host and only for timeout/EOF/unexpected EOF, respecting context cancellation.

`NewHTTPFallback` wraps a transport. On TLS handshake/port errors it retries the same request as `http://` and remembers the host so future requests use HTTP directly. It replays the body with `GetBody` when needed.

## State And Persistence
Resolver state is in-memory: hosts, cloned headers, tracker, transfer performance options, and optional limiter. HTTP fallback stores the host that fell back behind a mutex. No registry data is persisted by resolver itself.

## Dependencies And Integration Points
Depends on containerd `images`, `remotes`, `transfer`, `reference`, tracing/logging, `errdefs`, OCI descriptors, digest validation, and registry host configuration. It is the factory for fetcher and pusher and provides common `request` behavior they reuse.

## Risks And Edge Cases
Resolving tags trusts only resolve-capable hosts; wrong host capabilities can be a security risk. Fallback from manifests to blobs is intentionally limited to 404 to avoid poisoning descriptors with blob media types after transient manifest failures. Query logging must redact secrets while preserving `ns`. `MaxManifestSize` prevents large-manifest DoS but may reject legitimate non-image artifacts with large annotations. Retry semantics differ by last-host status to preserve mirror fallback behavior.

## Test Signals
`resolver_test.go` covers HTTP/HTTPS resolution, header clone races, basic/token/refresh auth, bad/missing/wrong auth errors, host fallback, TLS fallback, proxy namespace queries, query sanitization, transient transport classification and retry counts, digest manifest 5xx vs 404 fallback, and unexpected status code wrapping.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/core/remotes/docker/resolver.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/core/remotes/docker/resolver_test.go -->
# sources/cloud-native/containerd/core/remotes/docker/resolver_test.go

## Purpose
Provides broad integration and unit tests for Docker resolver behavior, including auth schemes, host fallback, proxy namespace handling, sanitized URLs, retry policy, and digest resolution fallback rules.

## Important APIs, Types, And Functions
- Basic integration tests: `TestHTTPResolver`, `TestHTTPSResolver`, `TestBasicResolver`, `runBasicTest`, and `runNotFoundTest`.
- Auth tests: anonymous bearer tokens, basic-auth token requests, refresh token flows, POST password grant, direct basic auth, bad/missing/wrong credentials.
- Host/fallback tests: host failure fallback, TLS failure fallback, `NewHTTPFallback`, timeout fallback, and port-error helper checks.
- Proxy and query tests: `TestResolveProxy`, `TestResolveProxyFallback`, `TestAddQuery`, and `TestRequestSanitize`.
- Retry tests: `TestIsTransientTransportErr` and `TestDoWithTransportRetries`.
- Digest fallback tests: `TestResolveTransientManifestError`, `TestResolve404ManifestFallback`, and `TestResolverErrorStatusCodeOnFetch`.
- Fixtures: `testContent`, `testManifest`, `refreshTokenServer`, `namespaceRouter`, and local TLS/basic/token server helpers.

## Control Flow
The file builds miniature registries with `httptest` and exercises actual `NewResolver`, `Resolve`, `Fetcher`, `Fetch`, and `FetchByDigest` calls. Auth tests deliberately return `WWW-Authenticate` challenges and token endpoints. Fallback tests configure multiple `RegistryHost` entries or fallback transports. Retry tests isolate `request.doWithTransportRetries` with fake round trippers.

## State And Persistence
State is local to tests: in-memory manifests/blobs, local HTTP/TLS servers, refresh token server fields, and call counters. No real registry or content store is used.

## Dependencies And Integration Points
Touches most of the Docker remotes package: registry host config, authorizer, resolver, fetcher, request retry logic, error wrapping, HTTP fallback, and namespace proxy query generation.

## Risks And Edge Cases
The tests document important invariants: headers must be cloned for parallel use; 5xx on `/manifests/` must not fall back to `/blobs/`; 404 may fall back for legacy compatibility; URL logging must redact secrets; context cancellation must interrupt transport retry backoff.

## Test Signals
This is the primary resolver regression suite and gives strong coverage for network/auth behaviors. It relies on local test servers rather than external registries, making failures deterministic.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/core/remotes/docker/resolver_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/core/remotes/docker/resolver_unix.go -->
# sources/cloud-native/containerd/core/remotes/docker/resolver_unix.go

## Purpose
Provides the non-Windows implementation of connection-refused detection used by HTTP fallback logic.

## Important APIs, Types, And Functions
- `isConnError(err error) bool` returns true when the error wraps `syscall.ECONNREFUSED`.

## Control Flow
`isPortError` in `resolver.go` calls this helper. If a no-port host fails with connection refused or timeout, the fallback transport may retry the request using `http://`.

## State And Persistence
No state.

## Dependencies And Integration Points
Build-tagged with `//go:build !windows`; depends on `errors` and `syscall`. Integrated only through `resolver.go` fallback helpers.

## Risks And Edge Cases
Platform-specific error wrapping must preserve `errors.Is` compatibility. This file excludes Windows-specific Winsock errors, which are handled separately.

## Test Signals
Indirectly covered by resolver HTTP fallback and port-error tests on non-Windows platforms.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/core/remotes/docker/resolver_unix.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/core/remotes/docker/resolver_windows.go -->
# sources/cloud-native/containerd/core/remotes/docker/resolver_windows.go

## Purpose
Provides the Windows implementation of connection-refused detection used by HTTP fallback logic.

## Important APIs, Types, And Functions
- `isConnError(err error) bool` returns true for both `syscall.ECONNREFUSED` and `windows.WSAECONNREFUSED`.

## Control Flow
`isPortError` in `resolver.go` calls this helper when deciding whether a scheme fallback from HTTPS to HTTP is allowed for a host without an explicit port.

## State And Persistence
No state.

## Dependencies And Integration Points
Build-tagged with `//go:build windows`; depends on `golang.org/x/sys/windows` for Winsock error classification.

## Risks And Edge Cases
Correct fallback behavior on Windows depends on wrapping preserving `errors.Is` checks for Winsock constants.

## Test Signals
Covered indirectly by resolver fallback tests on Windows. No Windows-specific listed test targets this file directly.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/core/remotes/docker/resolver_windows.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/core/remotes/docker/scope.go -->
# sources/cloud-native/containerd/core/remotes/docker/scope.go

## Purpose
Builds and stores Docker registry auth scopes in context for pull, push, and cross-repository mount flows.

## Important APIs, Types, And Functions
- `RepositoryScope(refspec, push)` formats `repository:<repo>:pull` or `repository:<repo>:pull,push`.
- `ContextWithRepositoryScope(ctx, refspec, push)` appends the repository scope to context.
- `WithScope(ctx, scope)` appends arbitrary scope strings under a private context key.
- `ContextWithAppendPullRepositoryScope(ctx, repo)` appends a pull scope for an additional repo, used for mount sources.
- `GetTokenScopes(ctx, common)` returns sorted, deduplicated context and common scopes.

## Control Flow
References are parsed as dummy URLs to derive the repository path from the locator. Scopes are accumulated in a context value slice and then merged with common scopes. Deduplication happens after lexicographic sorting and is string-exact.

## State And Persistence
Scopes live only in `context.Context`. No global or persistent state is used.

## Dependencies And Integration Points
Used by resolver/fetcher/pusher before making registry requests so authorizers can request tokens with proper scopes. Cross-repo mount uses appended pull scope for the source repo.

## Risks And Edge Cases
Deduplication is syntax-based, not semantic; `pull,push` and `push,pull` are distinct. `WithScope` assumes any existing context value has the expected `[]string` type.

## Test Signals
`scope_test.go` covers pull vs pull/push scope formatting, sorted/deduplicated merging, and custom scope accumulation.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/core/remotes/docker/scope.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/core/remotes/docker/scope_test.go -->
# sources/cloud-native/containerd/core/remotes/docker/scope_test.go

## Purpose
Tests Docker registry auth scope formatting and context aggregation.

## Important APIs, Types, And Functions
- `TestRepositoryScope` validates repo path extraction and pull/push scope strings.
- `TestGetTokenScopes` validates merging, sorting, and exact-string deduplication.
- `TestCustomScope` validates arbitrary scopes plus appended pull repo scopes.

## Control Flow
Tests construct `reference.Spec` values or contexts with `tokenScopesKey{}` and call the scope helpers directly.

## State And Persistence
No persistent state; all scope data is context-local.

## Dependencies And Integration Points
Protects behavior consumed by Docker authorizers during resolve, fetch, push, and cross-repo mount requests.

## Risks And Edge Cases
Tests confirm exact-string deduplication but also reveal semantic duplicates with different action ordering are not collapsed.

## Test Signals
Focused unit coverage of scope string and ordering behavior.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/core/remotes/docker/scope_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/core/remotes/docker/status.go -->
# sources/cloud-native/containerd/core/remotes/docker/status.go

## Purpose
Defines push/fetch operation status tracking interfaces and an in-memory implementation used by Docker pusher uploads.

## Important APIs, Types, And Functions
- `Status` embeds `content.Status` and adds `Committed`, `ErrClosed`, `UploadUUID`, and `PushStatus`.
- `PushStatus` records `MountedFrom` and `Exists`.
- `StatusTracker` exposes `GetStatus` and `SetStatus`.
- `StatusTrackLocker` extends tracker with per-ref `Lock` and `Unlock`.
- `NewInMemoryTracker` returns a mutex-protected `memoryStatusTracker` with a `moby/locker` keyed lock.

## Control Flow
`GetStatus` returns not-found when no status exists. `SetStatus` overwrites the status for a ref. Per-ref locks are separate from the map mutex and are used by `dockerPusher.Writer/push` to serialize decisions for the same ref.

## State And Persistence
The default tracker persists state only in memory for the resolver/pusher lifetime. It tracks in-progress offsets and committed state but does not survive process restart.

## Dependencies And Integration Points
Used by `dockerPusher` to prevent concurrent duplicate uploads, record remote existence/mount outcomes, resume or reject active writer flows, and report content writer status.

## Risks And Edge Cases
The default tracker is process-local; external callers needing durable upload coordination need another implementation. `SetStatus` overwrites full status objects, so callers must preserve fields they care about.

## Test Signals
Covered indirectly by `pusher_test.go`, which inspects tracker status for already-existing and mounted content and validates retry behavior after close/reset.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/core/remotes/docker/status.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/core/remotes/errors/errors.go -->
# sources/cloud-native/containerd/core/remotes/errors/errors.go

## Purpose
Defines a serializable `ErrUnexpectedStatus` error for remote HTTP responses with unexpected status codes.

## Important APIs, Types, And Functions
- `ErrUnexpectedStatus` stores status string, status code, up to 64 KiB of response body, request URL, and request method.
- `Error()` formats a concise message including request method, URL, and status.
- `NewUnexpectedStatusErr(resp)` reads a bounded body and builds the error.
- `init` registers the error type with `typeurl` for wire serialization.

## Control Flow
When a response is unexpected, callers pass the response to `NewUnexpectedStatusErr`. The function drains at most 64 KiB from `resp.Body`, copies request metadata if available, and returns the structured error.

## State And Persistence
No mutable runtime state besides typeurl registration during init. Error values may be serialized by containerd APIs.

## Dependencies And Integration Points
Used by Docker remotes unexpected response helpers and tested through resolver/fetcher error paths. Integrates with `github.com/containerd/typeurl/v2`.

## Risks And Edge Cases
Calling `NewUnexpectedStatusErr` consumes response body content up to the limit. The captured request URL may include query data unless callers sanitize before exposing/logging; Docker request logging separately redacts URLs.

## Test Signals
No direct listed test, but resolver tests assert errors can be unwrapped as `remoteerrors.ErrUnexpectedStatus` and contain expected status codes.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/core/remotes/errors/errors.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/core/remotes/handlers.go -->
# sources/cloud-native/containerd/core/remotes/handlers.go

## Purpose
Provides generic image remotes handlers for fetching into content stores, pushing from content stores, filtering non-distributable content, platform-aware manifest traversal, distribution-source annotation propagation, and reference-key construction.

## Important APIs, Types, And Functions
- `WithMediaTypeKeyPrefix` adds context-scoped media type to ref-key prefix overrides.
- `MakeRefKey` builds stable content ingest refs from descriptor digest, ref-name annotation, media type classification, and context overrides.
- `FetchHandler` and `Fetch` fetch remote descriptors into a `content.Ingester`.
- `PushHandler`, `push`, and `PushContent` push local content to a `Pusher`.
- `SkipNonDistributableBlobs` filters foreign/non-distributable layers.
- `FilterManifestByPlatformHandler` lets non-target manifests only expose config descriptors.
- `annotateDistributionSourceHandler` and `copyDistributionSourceLabels` propagate distribution-source labels from parent descriptors/content info to children.
- `closeOnEOFReader` and `closeOnEOFReadSeeker` close remote bodies promptly on EOF while preserving seek support.

## Control Flow
Fetch opens a content writer using `MakeRefKey`, rejects zero-size descriptors, commits completed writers, copies inline `desc.Data` when available, otherwise fetches remote data and wraps the reader to close at EOF. Push opens either an ingester writer or pusher writer, obtains a section reader from the content provider, and copies bytes.

`PushContent` traverses an image graph with `images.Dispatch`. It first pushes configs/layers, records manifests and indexes, then pushes manifests and indexes in dependency order so child content exists before parent manifests. If the store can provide content info, distribution-source labels are copied into child annotations for cross-repo mount hints.

## State And Persistence
Fetch writes into a content store through `content.Ingester`; push writes to a remote registry through a pusher. Context stores media-type prefix overrides. `PushContent` keeps transient slices of manifests/indexes guarded by a mutex during dispatch.

## Dependencies And Integration Points
Integrates with `core/content`, `core/images`, `platforms`, `semaphore`, OCI descriptors, Docker pusher/fetcher implementations, and local content label conventions.

## Risks And Edge Cases
Zero-size remote descriptors are rejected because committing an empty entry for missing length would be misleading. Push ordering is critical for registry dependency checks. Non-distributable filtering must apply to both direct child lists and descriptor self-handling. Annotation propagation must not overwrite child annotations.

## Test Signals
`handlers_test.go` covers custom ref-key prefixes and non-distributable filtering against both synthetic child lists and a real local content store. Distribution-source propagation is exercised indirectly by pusher tests.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/core/remotes/handlers.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/core/remotes/handlers_test.go -->
# sources/cloud-native/containerd/core/remotes/handlers_test.go

## Purpose
Tests generic remotes handler helpers for ref-key prefix customization and non-distributable layer filtering.

## Important APIs, Types, And Functions
- `TestContextCustomKeyPrefix` validates built-in, unknown, overridden, and custom media-type prefixes in `MakeRefKey`.
- `TestSkipNonDistributableBlobs` validates descriptor filtering from a handler and from `images.ChildrenHandler` over a local content store.
- `memoryLabelStore` implements the local content store label interface for tests.

## Control Flow
The ref-key test builds contexts with prefix overrides and checks returned string prefixes. The non-distributable test first wraps a synthetic handler returning several layer media types, then creates a local labeled store, writes config and manifest content, and verifies child traversal excludes foreign/non-distributable layers while keeping config and normal layer.

## State And Persistence
Uses a temporary local content store and in-memory label store. Test artifacts are confined to `t.TempDir`.

## Dependencies And Integration Points
Exercises `content/local`, OCI manifests/configs, media-type classifiers from `images`, and the handler wrappers in `handlers.go`.

## Risks And Edge Cases
Protects compatibility for custom ingest refs and legal distribution filtering. It does not directly test `PushContent` ordering or distribution-source annotation copying.

## Test Signals
Good unit and small integration coverage for handler composition behavior.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/core/remotes/handlers_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/core/remotes/resolver.go -->
# sources/cloud-native/containerd/core/remotes/resolver.go

## Purpose
Defines the generic remote resolver, fetcher, pusher, fetch-by-digest, and referrers interfaces used by containerd remote implementations.

## Important APIs, Types, And Functions
- `Resolver` resolves references and creates namespace-bound `Fetcher` and `Pusher` instances.
- `ResolverWithOptions` extends resolver with transfer option support.
- `Fetcher`, `FetcherByDigest`, `ReferrersFetcher`, and `Pusher` define remote content operations.
- `FetcherFunc` and `PusherFunc` adapt functions to interfaces.
- `FetchByDigestConfig`, `FetchByDigestOpts`, and `WithMediaType` configure digest fetch requests.
- `FetchReferrersConfig`, `FetchReferrersOpt`, `WithReferrerArtifactTypes`, and `WithReferrerQueryFilter` configure referrers retrieval.

## Control Flow
This file is contract-only. Implementations such as Docker resolver/fetcher/pusher satisfy these interfaces. Option functions mutate small config structs used by implementation methods.

## State And Persistence
No state is stored here. Config structs are per-call.

## Dependencies And Integration Points
Depends on `content`, transfer options, digest, OCI descriptors, and `net/url`. It is imported by higher-level image pull/push code and concrete remote implementations.

## Risks And Edge Cases
`FetcherByDigest` explicitly returns incomplete descriptors, so callers must not assume annotations or exact media type unless they supplied one. Referrers query filters are implementation-dependent and may or may not be applied server-side.

## Test Signals
No direct tests in this subset; Docker fetcher/referrers tests validate concrete conformance.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/core/remotes/resolver.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/core/runtime/events.go -->
# sources/cloud-native/containerd/core/runtime/events.go

## Purpose
Maps runtime task event payload types to containerd event topic strings.

## Important APIs, Types, And Functions
- Topic constants such as `/tasks/create`, `/tasks/start`, `/tasks/exit`, `/tasks/delete`, and `/tasks/checkpointed`.
- `GetTopic(e any) string` returns the topic for known `api/events` task event pointer types, otherwise logs and returns `/tasks/?`.

## Control Flow
`GetTopic` uses a type switch over event pointer types. Unknown inputs are logged at warning level and mapped to `TaskUnknownTopic`.

## State And Persistence
No state; pure mapping plus logging side effect.

## Dependencies And Integration Points
Depends on `github.com/containerd/containerd/api/events` and `log`. Used by runtime event publishers/bridges to determine event exchange topics.

## Risks And Edge Cases
Only pointer types match; non-pointer event values return unknown. Adding new event types requires updating this switch.

## Test Signals
No direct test in this subset.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/core/runtime/events.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/core/runtime/monitor.go -->
# sources/cloud-native/containerd/core/runtime/monitor.go

## Purpose
Defines the runtime task monitoring abstraction and simple implementations for no-op and multi-monitor broadcasting.

## Important APIs, Types, And Functions
- `TaskMonitor` has `Monitor(task, labels)` and `Stop(task)`.
- `NewMultiTaskMonitor(monitors...)` returns a `multiTaskMonitor`.
- `NewNoopMonitor()` returns a monitor that ignores all calls.
- `multiTaskMonitor` forwards calls to each monitor and stops on first error.

## Control Flow
Calls to `Monitor` or `Stop` on the multi monitor iterate configured monitors in order. Any error aborts remaining calls and is returned. The noop implementation always returns nil.

## State And Persistence
`multiTaskMonitor` stores the monitor slice. No monitor state is persisted by this file.

## Dependencies And Integration Points
Depends on the `Task` interface from `task.go`. Used by runtime services that attach metrics/health/restart monitors to tasks.

## Risks And Edge Cases
No rollback is attempted when one monitor succeeds and a later monitor fails. Callers must decide whether partial monitoring is acceptable.

## Test Signals
No direct listed tests.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/core/runtime/monitor.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/core/runtime/nsmap.go -->
# sources/cloud-native/containerd/core/runtime/nsmap.go

## Purpose
Provides a generic namespace-aware map for runtime objects keyed by object ID and namespace.

## Important APIs, Types, And Functions
- `object` constraint requires `ID() string`.
- `NSMap[T]` stores `map[namespace]map[id]T` behind an RW mutex.
- `NewNSMap` constructs the map.
- `Get`, `GetAll`, `Add`, `AddWithNamespace`, `Delete`, and `IsEmpty` expose namespace-aware operations.

## Control Flow
Most methods require a namespace from context via `namespaces.NamespaceRequired`. `AddWithNamespace` creates the inner map when needed and rejects duplicate IDs with `ErrAlreadyExists`. `GetAll(noNS=true)` returns objects across all namespaces; otherwise it returns only the context namespace.

## State And Persistence
State is in-memory only. Deleted namespaces are not removed when their inner maps become empty, but `IsEmpty` checks inner lengths.

## Dependencies And Integration Points
Used by runtime managers and shim tracking code for namespace-scoped tasks/shims. Depends on containerd namespace context helpers and `errdefs`.

## Risks And Edge Cases
`Delete` silently returns when the context lacks a namespace. `GetAll(noNS=true)` order is map iteration order and not deterministic. Empty namespace maps can remain after deletions.

## Test Signals
No direct test in this subset; runtime v2 shim/task manager tests elsewhere likely exercise it.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/core/runtime/nsmap.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/core/runtime/opts/opts_linux.go -->
# sources/cloud-native/containerd/core/runtime/opts/opts_linux.go

## Purpose
Provides a Linux namespace deletion option that cleans cgroup resources by namespace.

## Important APIs, Types, And Functions
- `WithNamespaceCgroupDeletion(ctx, i *namespaces.DeleteInfo) error` removes the cgroup path derived from the namespace delete info.

## Control Flow
The function calls `cgroups.Remove(filepath.Join("/", constants.CgroupNamespace, i.Name))` and returns any error.

## State And Persistence
Mutates host cgroup state by deleting the namespace cgroup. No in-process state is stored.

## Dependencies And Integration Points
Builds on `core/cgroups`, runtime constants, and namespace delete hooks. Intended for Linux cleanup when namespaces are deleted.

## Risks And Edge Cases
This is Linux-only and operates on cgroup paths. Incorrect namespace names or cgroup layout changes can cause failed cleanup or unintended path targeting if upstream helpers do not sanitize as expected.

## Test Signals
No direct listed tests.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/core/runtime/opts/opts_linux.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/core/runtime/restart/restart.go -->
# sources/cloud-native/containerd/core/runtime/restart/restart.go

## Purpose
Defines restart policy labels, policy parsing, reconciliation rules, and container option helpers used by the restart monitor.

## Important APIs, Types, And Functions
- Labels: `StatusLabel`, `LogURILabel`, `PolicyLabel`, `CountLabel`, and `ExplicitlyStoppedLabel`.
- `Policy` stores policy name and maximum retry count.
- `NewPolicy` parses `no`, `always`, `on-failure[:max-retries]`, and `unless-stopped`, defaulting empty policy to `always`.
- `Reconcile(status, labels)` decides whether a task should be restarted.
- `WithLogURI`, `WithLogURIString`, `WithStatus`, `WithPolicy`, and `WithNoRestarts` mutate container labels.
- `ensureLabels` initializes `containers.Container.Labels`.

## Control Flow
`NewPolicy` splits the policy on `:` and validates which policies may have a retry suffix. `Reconcile` parses the configured policy and applies policy-specific rules: `always` restarts, `on-failure` restarts only for non-zero exits and below retry limit, and `unless-stopped` restarts unless explicitly stopped. Option helpers are returned as functions compatible with container creation/update option patterns.

## State And Persistence
Desired restart state is persisted in container labels. The code itself holds no process-global state.

## Dependencies And Integration Points
Integrates with the containerd client status model, container metadata, and restart monitor plugin. Log URI labels affect task IO setup in restart-managed tasks.

## Risks And Edge Cases
Invalid policies or invalid restart counts log errors and suppress restarts. `WithNoRestarts` removes status, policy, and log URI labels but does not remove count or explicitly-stopped labels, leaving historical metadata.

## Test Signals
`restart_test.go` covers policy parsing, string formatting, and reconciliation outcomes for always, on-failure with counts, invalid counts, and unless-stopped explicit stops.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/core/runtime/restart/restart.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/core/runtime/restart/restart_test.go -->
# sources/cloud-native/containerd/core/runtime/restart/restart_test.go

## Purpose
Tests restart policy parsing, rendering, and restart decision logic.

## Important APIs, Types, And Functions
- `TestNewRestartPolicy` validates supported and unsupported policy strings.
- `TestRestartPolicyToString` validates round-trip string formatting.
- `TestRestartPolicyReconcile` validates restart decisions from process status and labels.

## Control Flow
The tests are table-driven. Parsing tests compare returned `Policy` structs. Reconcile tests pass `containerd.Status` and labels to `Reconcile` and compare booleans.

## State And Persistence
No persistent state; labels are in-memory maps.

## Dependencies And Integration Points
Uses the public `containerd.Status` type and restart label constants. Protects behavior consumed by the restart monitor.

## Risks And Edge Cases
Tests capture that empty policy means always, `always` cannot have retry count, `on-failure` needs non-zero exit status, invalid count suppresses restart, and `unless-stopped` respects explicit stop.

## Test Signals
Focused unit coverage for restart policy behavior.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/core/runtime/restart/restart_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/core/runtime/runtime.go -->
# sources/cloud-native/containerd/core/runtime/runtime.go

## Purpose
Defines core runtime task creation options, process IO descriptors, exit information, and the platform runtime interface.

## Important APIs, Types, And Functions
- `IO` describes stdin/stdout/stderr paths and terminal mode.
- `CreateOpts` carries OCI spec, rootfs mounts, IO, checkpoint/restore flags, runtime options, task options, runtime name/path, sandbox ID, task API address, and version.
- `Exit` records PID, exit status, and timestamp.
- `PlatformRuntime` defines `ID`, `Create`, `Get`, `Tasks`, and `Delete`.

## Control Flow
This file is interface/data-model only. Runtime implementations consume `CreateOpts` and return `Task` objects; managers use `PlatformRuntime` for lifecycle operations.

## State And Persistence
No state is stored here. Struct fields are passed between services and runtime implementations.

## Dependencies And Integration Points
Depends on containerd mount types and typeurl for opaque runtime/spec options. Used by runtime v1/v2 managers and task services.

## Risks And Edge Cases
Several fields are opaque `typeurl.Any`, so correctness depends on type registration and runtime-specific decoding. `Runtime` can be a named runtime or absolute binary path, which affects shim launch logic.

## Test Signals
No direct test in this subset.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/core/runtime/runtime.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/core/runtime/task.go -->
# sources/cloud-native/containerd/core/runtime/task.go

## Purpose
Defines the core runtime process and task interfaces and state types used throughout containerd runtime management.

## Important APIs, Types, And Functions
- `TaskInfo` identifies a task by ID, runtime, spec bytes, and namespace.
- `Process` defines common process lifecycle methods: state, kill, resize, close IO, start, and wait.
- `ExecProcess` extends `Process` with `Delete`.
- `Task` extends `Process` with PID, namespace, pause/resume, exec, pids, checkpoint, update, process lookup, and stats.
- `ExecOpts`, `ConsoleSize`, `Status`, `State`, and `ProcessInfo` model runtime data.

## Control Flow
This file is contract-only. Runtime implementations such as v2 shim tasks satisfy these interfaces, while services and monitors consume them polymorphically.

## State And Persistence
No state is stored here. `State` and `ProcessInfo` are snapshots returned by implementations.

## Dependencies And Integration Points
Depends on containerd protobuf `types.Any`. Integrates with runtime services, monitors, shim clients, task managers, and API event generation.

## Risks And Edge Cases
`State.ExitStatus` and `ExitedAt` are meaningful only for stopped states. `ProcessInfo.Info` is platform-specific and requires caller type knowledge. Interface changes have broad compatibility impact.

## Test Signals
No direct test in this subset; runtime v2 tests elsewhere exercise concrete implementations.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/core/runtime/task.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/core/runtime/typeurl.go -->
# sources/cloud-native/containerd/core/runtime/typeurl.go

## Purpose
Registers common OCI runtime-spec and feature types with containerd's typeurl system.

## Important APIs, Types, And Functions
- `init()` registers `specs.Spec`, `specs.Process`, `specs.LinuxResources`, `specs.WindowsResources`, and `features.Features` under the `types.containerd.io` prefix with the OCI runtime-spec major version.

## Control Flow
Registration runs at package initialization. The major version is derived from `specs.VersionMajor`.

## State And Persistence
Mutates global typeurl registration state. No local state is kept.

## Dependencies And Integration Points
Enables `typeurl.Any` fields in runtime create/update options to serialize and deserialize OCI spec/resource types. Integrates with runtime services and shim protocols.

## Risks And Edge Cases
Registration names depend on the OCI runtime-spec major version. Missing registration would break decoding of runtime option payloads.

## Test Signals
No direct tests in this subset.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/core/runtime/typeurl.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/core/runtime/v2/binary.go -->
# sources/cloud-native/containerd/core/runtime/v2/binary.go

## Purpose
Manages invocation of runtime v2 shim binaries for start and delete operations, including log pipe setup, bootstrap parameter persistence, connection creation, and dead-shim cleanup.

## Important APIs, Types, And Functions
- `shimBinaryConfig` holds runtime path, containerd GRPC/TTRPC addresses, socket directory, and environment.
- `shimBinary(bundle, config)` constructs a `binary`.
- `binary.Start(ctx, opts, onClose)` starts a shim with `client.Command`, streams shim logs, parses bootstrap response, connects to the shim, persists shim metadata, and returns a `shim`.
- `binary.Delete(ctx)` runs the shim delete action for a dead shim, unmarshals `task.DeleteResponse`, deletes the bundle, and returns `runtime.Exit`.

## Control Flow
`Start` builds a shim command with action `start`, opens the shim log pipe under the current namespace, starts a goroutine copying logs to stderr, runs the command and captures combined output, writes `shim-binary-path`, parses bootstrap params, creates a client connection with an on-close callback that also stops log copying, writes `bootstrap.json`, and returns a shim instance with protocol/address/version.

`Delete` logs cleanup, chooses workdir carefully by OS, builds a shim command with action `delete`, captures stdout/stderr separately, logs command failures and warnings, unmarshals the delete response, deletes the bundle directory, and maps the response to `runtime.Exit`.

## State And Persistence
Persists `shim-binary-path` and `bootstrap.json` in the bundle directory on start. Deletes the bundle during dead-shim cleanup. Holds no global state.

## Dependencies And Integration Points
Depends on runtime v2 `Bundle`, shim command package, bootstrapping helpers from `shim.go`, protobuf task API types, namespace context, logging, and runtime `Exit`. This is central to containerd daemon to shim process lifecycle.

## Risks And Edge Cases
Start must avoid leaking shim log goroutines/files on errors. `CombinedOutput` output must parse as expected bootstrap JSON/protobuf response. Delete workdir differs on Windows and FreeBSD to avoid filesystem/executable constraints. Bundle deletion after delete is irreversible and must happen only after successful shim cleanup response.

## Test Signals
No direct listed test for `binary.go`, but runtime v2 shim and manager tests elsewhere likely cover shim start/delete integration paths.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/core/runtime/v2/binary.go -->
