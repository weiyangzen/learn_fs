# subset-b-000193 research

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/pkg/registry/registry_test.go -->
# sources/cloud-native/moby/daemon/pkg/registry/registry_test.go

## Purpose
Tests registry service endpoint selection and insecure-registry classification. It focuses on mirror inclusion for pulls but not pushes, default loopback insecurity, explicit insecure host/CIDR handling, and DNS lookup behavior used by registry configuration.

## Important APIs, Types, And Functions
`overrideLookupIP` temporarily replaces the package-level `lookupIP` hook and restores it with `t.Cleanup`. `TestMirrorEndpointLookup` exercises `NewService`/`newServiceConfig`, `LookupPushEndpoints`, and `LookupPullEndpoints`. `TestIsSecureIndex` drives `serviceConfig.isSecureIndex` through hostnames, ports, loopbacks, invalid DNS names, and CIDR matches.

## Control Flow
The mirror test creates a service with one mirror, resolves Docker Hub image endpoints, then asserts mirror presence differs between pull and push paths. The security test iterates table cases, builds fresh service configs, and checks the boolean result for each address.

## State And Persistence
Only package-global test state is mutated: `lookupIP` is replaced during individual tests and restored. No registry config persists beyond in-memory `serviceConfig` instances.

## Dependencies And Integration Points
The tests depend on `github.com/distribution/reference`, Moby registry service construction, and the package DNS hook. They validate behavior consumed by daemon auth, pull, push, and search code that relies on `isSecureIndex` and V2 endpoint lookup.

## Risks And Edge Cases
The table explicitly documents subtle behavior: localhost and loopback IPs are insecure by default, host-only insecure entries do not match arbitrary ports unless configured that way, and failed DNS lookup falls back to direct host matching. These rules are security-sensitive because they decide TLS verification and HTTP fallback.

## Test Signals
Failures indicate changed mirror ordering/exclusion or insecure registry matching. The DNS override makes results deterministic and catches regressions in CIDR expansion and hostname normalization.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/pkg/registry/registry_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/pkg/registry/resumable/resumablerequestreader.go -->
# sources/cloud-native/moby/daemon/pkg/registry/resumable/resumablerequestreader.go

## Purpose
Implements an `io.ReadCloser` that can transparently retry and resume HTTP response body reads by issuing Range requests after transport or body-read failures. It is used for registry pulls where network interruption should not restart an entire download.

## Important APIs, Types, And Functions
`requestReader` stores the `http.Client`, original request, byte offset (`lastRange`), total content size, current response, retry counters, and backoff duration. `NewRequestReader` starts without a response; `NewRequestReaderWithInitialResponse` continues from an already opened response. `Read`, `Close`, and `cleanUpResponse` implement the reader lifecycle.

## Control Flow
`Read` validates client/request, sets a `Range` header when resuming, optionally sleeps, performs the HTTP request when no response is active, and retries request creation errors until `maxFailures` is reached. It handles a final 416 response as EOF when the offset equals total size, rejects non-206 fresh resume responses, auto-detects total size from `ContentLength`, reads from the response body, advances `lastRange`, and suppresses non-EOF body-read errors so a later read can resume.

## State And Persistence
State is in-memory and mutable across reads: `lastRange`, `failures`, `totalSize`, `currentResponse`, and the original request header. Response bodies are closed whenever a request completes, errors, or is replaced. `Close` clears client/request references.

## Dependencies And Integration Points
Uses `net/http`, `io`, `time`, and containerd logging. It integrates with registry download code expecting a standard `io.ReadCloser`; callers must provide a request whose server supports byte ranges for resumed reads.

## Risks And Edge Cases
The code mutates the original request header, so reused requests can retain Range. The constructed range uses `bytes=start-totalSize`, which depends on server interpretation of an inclusive end. Non-EOF body errors are returned as nil after logging, so callers must continue reading for recovery. A zero or negative content length can fail auto-detection, and servers without Range support cause a hard error after the first resume attempt.

## Test Signals
The paired tests cover nil configuration, retry thresholds, read-error suppression, 416 EOF, servers without byte-range support, total-size auto-detection, normal reads, and initial-response reads.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/pkg/registry/resumable/resumablerequestreader.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/pkg/registry/resumable/resumablerequestreader_test.go -->
# sources/cloud-native/moby/daemon/pkg/registry/resumable/resumablerequestreader_test.go

## Purpose
Validates the resumable request reader's error handling, retry limits, byte-range assumptions, EOF handling, and successful read paths.

## Important APIs, Types, And Functions
The tests instantiate `requestReader` directly for internal state cases and use `NewRequestReader`/`NewRequestReaderWithInitialResponse` for public constructors. `errorReaderCloser` simulates a body read failure. `httptest.Server` provides successful responses and range-support failures.

## Control Flow
Individual tests exercise nil client/request and bad total size, request-level failures under and over `maxFailures`, non-EOF body errors, 416 responses at the known end offset, a server that ignores Range, auto-detected content length, explicit total size, and a pre-opened initial response.

## State And Persistence
Each test owns fresh readers, servers, and requests. Readers are closed with `defer` where needed to close response bodies and clear internal references. No external state persists.

## Dependencies And Integration Points
Uses Go `net/http/httptest`, `io.ReadAll`, and `gotest.tools` assertions. It pinpoints behavior expected by registry download consumers rather than making real registry calls.

## Risks And Edge Cases
The timeout/backoff tests reduce `waitDuration` manually to avoid slow tests; production uses five-second waits. The "server does not support byte ranges" test checks only missing partial-content response semantics, not full RFC Range parsing.

## Test Signals
Passing tests confirm the reader can be used as a robust `io.ReadCloser`: transient request errors can be retried, terminal errors surface, non-EOF body errors trigger resumability, and successful reads return exact payload data.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/pkg/registry/resumable/resumablerequestreader_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/pkg/registry/search.go -->
# sources/cloud-native/moby/daemon/pkg/registry/search.go

## Purpose
Implements Docker registry search for repositories. This is a legacy V1 search path with local filtering for official status and stars, plus compatibility handling for the deprecated automated-build field.

## Important APIs, Types, And Functions
`Service.Search` validates filters and returns `[]registry.SearchResult`. `searchUnfiltered` resolves index information, builds a V1 endpoint, authorizes the HTTP client, and calls `searchRepositories`. `splitReposSearchTerm` separates registry host from repository term. `newIndexInfo` converts service config into `registry.IndexInfo`. `searchRepositories` sends `/v1/search?q=...&n=...` and decodes `registry.SearchResults`.

## Control Flow
Search rejects unknown filters, parses booleans, computes the highest requested stars threshold, short-circuits `is-automated=true` to no results, fetches unfiltered remote results, then applies local `is-official` and `stars` filtering while forcing `IsAutomated=false`. `searchUnfiltered` rejects schemes in repository names, treats Docker Hub library names specially, creates an endpoint, chooses a V2-authenticated client for identity-token auth, otherwise wraps the V1 auth transport, and performs the search request.

## State And Persistence
The service config is read under `s.mu.RLock`; no persistent config is mutated. Search result values are copied through the filtered slice with `IsAutomated` normalized.

## Dependencies And Integration Points
Depends on Docker API registry types, daemon filters, V1 endpoint creation, V1/V2 auth helpers, and containerd logging. It is reached by API search endpoints and relies on service registry configuration for mirrors, insecure registries, and TLS.

## Risks And Edge Cases
Search only supports V1 endpoints and rejects `/v2` endpoint strings. Filter behavior is partly client-side and can diverge from registry-side semantics. `limit` is constrained to 1..100, with 25 as default. Authentication path differs when both identity token and username are present.

## Test Signals
`search_test.go` covers successful search, invalid filters, deprecated automated filtering, stars and official filtering, error classification, and index-info construction for default, mirrored, and insecure configurations.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/pkg/registry/search.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/pkg/registry/search_endpoint_v1.go -->
# sources/cloud-native/moby/daemon/pkg/registry/search_endpoint_v1.go

## Purpose
Provides the legacy V1 registry endpoint abstraction used only by search. It normalizes endpoint URLs, configures TLS and transport headers, pings endpoints, handles insecure fallback, and preserves redirect header behavior.

## Important APIs, Types, And Functions
`v1PingResult` records registry standalone status. `v1Endpoint` stores the client, URL, and secure flag. `newV1Endpoint`, `trimV1Address`, `newV1EndpointFromStr`, `(*v1Endpoint).String`, `(*v1Endpoint).ping`, `httpClient`, `trustedLocation`, and `addRequiredHeadersToRedirectedRequests` form the endpoint implementation.

## Control Flow
`newV1Endpoint` builds TLS config from `IndexInfo`, constructs an endpoint, skips ping for Docker Hub's known endpoint, then tries HTTPS `_ping`. Secure registries fail with an explicit insecure-registry hint on HTTPS error; insecure registries fall back to HTTP and require a successful ping. `ping` reads standalone status from `X-Docker-Registry-Standalone` or JSON body and defaults to standalone when absent. Redirect handling copies all headers except authorization unless both original and redirect targets are trusted HTTPS Docker domains.

## State And Persistence
No persistent state is stored beyond the endpoint object and its HTTP client. `newV1Endpoint` mutates the endpoint URL scheme during HTTPS/HTTP probing.

## Dependencies And Integration Points
Uses TLS config helpers from the registry package, Docker distribution transport modifiers, Docker API registry metadata, and Go HTTP redirect hooks. It feeds `searchUnfiltered` and `authorizeClient`.

## Risks And Edge Cases
This code intentionally permits HTTP fallback only for insecure registries. Redirect authorization retention is narrow but security-sensitive. `_ping` accepts 401 as a reachable registry through HTTP client behavior and assumes sane defaults on malformed JSON. Address trimming rejects explicit `/v2` endpoints because search is V1-only.

## Test Signals
`search_endpoint_v1_test.go` covers endpoint string normalization, secure/insecure fallback errors, V2 rejection, 401 validation, trusted-location classification, and redirect header propagation with and without authorization.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/pkg/registry/search_endpoint_v1.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/pkg/registry/search_endpoint_v1_test.go -->
# sources/cloud-native/moby/daemon/pkg/registry/search_endpoint_v1_test.go

## Purpose
Tests V1 endpoint construction, ping semantics, URL parsing, insecure fallback behavior, and redirect header safety for legacy registry search.

## Important APIs, Types, And Functions
Tests call `newV1Endpoint`, `newV1EndpointFromStr`, `(*v1Endpoint).ping`, `trustedLocation`, and `addRequiredHeadersToRedirectedRequests`. Helpers such as `makeIndex`, `makeHTTPSIndex`, and `makePublicIndex` come from registry test fixtures.

## Control Flow
The suite validates default/public standalone ping values, expands URL forms with or without `/v1`, rejects `/v2`, confirms invalid secure endpoints produce certificate or insecure-registry hints, accepts a 401 basic-auth ping as a valid registry, and checks header copying across redirect pairs.

## State And Persistence
All state is in `httptest` servers and local request objects. There is no persisted registry configuration.

## Dependencies And Integration Points
Uses Go HTTP request construction, `httptest`, Docker registry test server helpers, and `gotest.tools`. These tests guard behavior consumed by `search.go` and `search_session.go`.

## Risks And Edge Cases
The redirect tests ensure `Authorization` is stripped for untrusted or non-HTTPS redirects but retained for trusted Docker HTTPS hosts. The endpoint tests encode legacy expectations for URLs that may look malformed but were historically accepted.

## Test Signals
Failures indicate regressions in V1 search compatibility, insecure registry guidance, Docker Hub special-casing, or credential leakage prevention during redirects.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/pkg/registry/search_endpoint_v1_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/pkg/registry/search_session.go -->
# sources/cloud-native/moby/daemon/pkg/registry/search_session.go

## Purpose
Implements the V1 registry authentication transport used by legacy search. It injects basic auth or cached token auth, preserves cancellation compatibility, and installs cookie support on the HTTP client.

## Important APIs, Types, And Functions
`authTransport` wraps an `http.RoundTripper` with `authConfig`, token cache, and a `modReq` map from original to cloned requests. `newAuthTransport`, `cloneRequest`, `onEOFReader`, `(*authTransport).RoundTrip`, `CancelRequest`, and `authorizeClient` are the key functions.

## Control Flow
`RoundTrip` bypasses auth changes for redirected untrusted locations, clones the request, records the clone for cancellation, sets Basic auth when always enabled, otherwise uses Basic auth only when `X-Docker-Token: true` requests a token or sends cached token auth. Response `X-Docker-Token` values update the cache, and the response body wrapper removes the request mapping on EOF or close. `authorizeClient` pings standalone HTTPS registries to decide always-basic mode, wraps the client transport, and installs a cookie jar.

## State And Persistence
Token cache and in-flight request mappings are in-memory on the transport. `authorizeClient` mutates the passed `http.Client` by replacing `Transport` and `Jar`.

## Dependencies And Integration Points
Depends on registry auth config, V1 endpoint ping, Go cookie jars, and redirect trust logic from `search_endpoint_v1.go`. It is used by `searchUnfiltered` and test registry sessions.

## Risks And Edge Cases
`token` is read and written without the mutex used for `modReq`, so concurrent requests could race if the same transport is shared broadly. `CancelRequest` depends on the wrapped transport exposing the legacy method. Always-basic auth requires non-nil auth config and is limited to standalone HTTPS registries.

## Test Signals
`search_test.go` uses this transport to seed a fake token and verify authenticated search. Redirect behavior is covered in the V1 endpoint tests.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/pkg/registry/search_session.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/pkg/registry/search_test.go -->
# sources/cloud-native/moby/daemon/pkg/registry/search_test.go

## Purpose
Exercises registry search behavior, including authenticated test registry requests, filter validation, result filtering, error classification, and index-info generation from service configuration.

## Important APIs, Types, And Functions
`spawnTestRegistrySession` constructs an authenticated V1 client and endpoint for mock registry search. `debugTransport` logs HTTP requests/responses. Test cases call `searchRepositories`, `Service.Search`, `NewService`, `newServiceConfig`, and `newIndexInfo`.

## Control Flow
`TestSearchRepositories` verifies a mock registry returns the expected query and star count. `TestSearchErrors` checks invalid filters and upstream 500 handling. `TestSearch` iterates successful filter combinations for empty/no-filter/automated/official/stars cases. `TestNewIndexInfo` checks default, mirror, and custom insecure registry configurations across hostnames and IP ranges.

## State And Persistence
Tests use `httptest.Server`, transient registry service instances, and the DNS override from `registry_test.go`. The fake auth token is stored inside the `authTransport` created for the test client.

## Dependencies And Integration Points
Depends on Docker registry API types, daemon filter parser, containerd errdefs classification, and registry test mock handlers. It guards the search path exposed through the daemon API.

## Risks And Edge Cases
The tests encode that `is-automated=true` returns no results even if upstream reports automated builds, and that `IsAutomated` is reset to false in returned entries. They also lock in loopback IPv6 behavior and mirror URL normalization.

## Test Signals
Passing tests confirm client-side filter semantics, invalid argument versus unknown error typing, authenticated search setup, and secure/insecure index derivation.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/pkg/registry/search_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/pkg/registry/service.go -->
# sources/cloud-native/moby/daemon/pkg/registry/service.go

## Purpose
Defines the daemon registry `Service`, which stores registry configuration and provides auth resolution, login/auth checks, endpoint lookup, and insecure-registry queries.

## Important APIs, Types, And Functions
`Service` holds a `serviceConfig` under an RW mutex. Public APIs include `NewService`, `ServiceConfig`, `ReplaceConfig`, `Auth`, `ResolveAuthConfig`, `LookupPullEndpoints`, `LookupPushEndpoints`, and `IsInsecureRegistry`. `APIEndpoint` describes a registry URL, TLS config, and mirror flag.

## Control Flow
Construction validates options into `serviceConfig`. `ReplaceConfig` prepares a commit closure so daemon reload can validate first and swap config later. `Auth` normalizes server address, looks up V2 endpoints without mirrors, attempts `loginV2` in order, and stops on context cancellation, deadline, or unauthorized errors. Endpoint lookup functions delegate to `lookupV2Endpoints` under lock.

## State And Persistence
Registry configuration is in-memory and atomically replaced by `ReplaceConfig` commit closures. `ServiceConfig` returns a copy to avoid external mutation.

## Dependencies And Integration Points
Integrates with daemon reload (`reloadRegistryConfig`), image pull/push resolution, registry login, auth config resolution, and distribution reference parsing.

## Risks And Edge Cases
Credentials are deliberately not sent to mirrors during `Auth`. `LookupPullEndpoints` and `LookupPushEndpoints` use `context.TODO`, so caller cancellation is not propagated there. `ReplaceConfig` separates validation from mutation, which is important for transactional daemon reload.

## Test Signals
Registry tests cover mirror inclusion/exclusion, insecure registry behavior, and reload tests verify registry mirrors/insecure registries update transactionally.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/pkg/registry/service.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/pkg/registry/service_v2.go -->
# sources/cloud-native/moby/daemon/pkg/registry/service_v2.go

## Purpose
Builds ordered V2 registry endpoints for pulls, pushes, authentication, and registry communication. It handles Docker Hub defaults, mirrors, TLS config, and HTTP fallback for explicitly insecure registries.

## Important APIs, Types, And Functions
`(*Service).lookupV2Endpoints` returns `[]APIEndpoint` from a hostname and `includeMirrors` flag. It uses `DefaultNamespace`, `IndexHostname`, `DefaultV2Registry`, `newTLSConfig`, `isSecureIndex`, and `tlsconfig.ServerDefault`.

## Control Flow
For Docker Hub hostnames, pull lookup optionally prepends configured mirrors, normalizing schemes to HTTPS when absent and loading TLS config for each mirror, then appends the default V2 registry. For non-Hub hosts, it creates an HTTPS endpoint and, when TLS config has `InsecureSkipVerify`, appends an HTTP endpoint.

## State And Persistence
No state is modified. The caller must hold `s.mu` when accessing `s.config`, and public service methods do so.

## Dependencies And Integration Points
Called by registry auth, image pull/push, and service endpoint lookup. Mirrors interact with daemon configuration and certificate directories through `newTLSConfig`.

## Risks And Edge Cases
Mirror TLS config is recalculated on each call rather than memoized. Insecure registries receive an HTTP fallback endpoint, so accurate `isSecureIndex` classification is critical. Context cancellation is checked inside the mirror loop before potentially expensive TLS loading.

## Test Signals
`registry_test.go` verifies mirrors appear for pulls but not pushes. `search_test.go` and reload tests indirectly validate secure/insecure config feeding endpoint construction.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/pkg/registry/service_v2.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/prune.go -->
# sources/cloud-native/moby/daemon/prune.go

## Purpose
Implements daemon-side pruning for stopped containers and unused networks. It enforces one prune operation at a time and returns API prune reports with deleted objects and reclaimed space where available.

## Important APIs, Types, And Functions
`ContainerPrune`, `localNetworkPrune`, `clusterNetworkPrune`, `NetworkPrune`, `getUntilFromPruneFilters`, and `matchLabels` are key functions. `containersAcceptedFilters` allows `label`, `label!`, and `until`; `errPruneRunning` is a conflict error. `networkIsInUse` recognizes swarm network-in-use errors.

## Control Flow
Container prune validates filters, parses `until`, lists containers, skips running/newer/label-mismatched containers, fetches layer size for reporting, removes containers, and emits a prune event. Network prune builds a network filter, prunes swarm manager networks first when possible, prunes local networks by walking libnetwork networks, skips config-only/non-pruneable/in-use networks, and emits a network prune event if not canceled.

## State And Persistence
`daemon.pruneRunning` is an atomic guard shared by container and network prune. Successful prune mutates daemon state by removing containers/networks and logs events. Cancellation returns partial reports without rolling back completed removals.

## Dependencies And Integration Points
Depends on daemon container stores, image layer-size service, libnetwork, swarm cluster manager, filter parsing, timestamp parsing, and event logging. API handlers call these through backend interfaces.

## Risks And Edge Cases
Container size lookup failures are logged only because size is informational. Cluster network prune ignores specific "network ID is in use" errors but logs other removal failures. Context cancellation is cooperative and can return partially completed reports. The single prune guard serializes unrelated prune categories.

## Test Signals
No direct file-local tests are listed, but API prune routes, network filtering, and daemon integration tests exercise this behavior. Event logs and returned prune reports are the primary signals.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/prune.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/reload.go -->
# sources/cloud-native/moby/daemon/reload.go

## Purpose
Implements daemon configuration reload with a transaction-like two-phase model. It updates live daemon settings such as debug, registry config, concurrency limits, labels, live restore, features, network diagnostics, NRI, and platform-specific runtime settings.

## Important APIs, Types, And Functions
`reloadTxn` records commit and rollback callbacks. `Daemon.Reload` orchestrates reload hooks. Hook functions include `reloadDebug`, `reloadMaxConcurrentDownloadsAndUploads`, `reloadMaxDownloadAttempts`, `reloadShutdownTimeout`, `reloadLabels`, `reloadRegistryConfig`, `reloadLiveRestore`, `reloadNetworkDiagnosticPort`, `reloadFeatures`, and `reloadNRI`. `marshalAttributeSlice` formats event attributes.

## Control Flow
`Reload` locks `configReload`, deep-copies current config using `copystructure`, builds `newCfg`, runs each hook against the copy, and aborts with rollback callbacks on the first error. On success it stores the new config, commits side effects, and logs a daemon reload event with attributes. Hooks apply "only if value set" semantics for many fields and register side effects such as image service config updates, registry service replacement, diagnostic start/stop, and NRI reload commit.

## State And Persistence
Live config is atomically swapped through `daemon.configStore.Store(newCfg)` only after all prepare hooks succeed. Commit callbacks then mutate auxiliary services. The `init` function registers a custom `copystructure` copier for `netip.Addr` so DNS/host gateway addresses survive reload copying.

## Dependencies And Integration Points
Integrates with daemon config parsing, registry service `ReplaceConfig`, image service, network controller diagnostics, NRI, event logging, and platform hooks in `reload_unix.go`/`reload_windows.go`.

## Risks And Edge Cases
The intended rollback design is important for fallible hooks; as written, `OnRollback` appends callbacks to `tx.onCommit` rather than `tx.onRollback`, so rollback callbacks would not run through `Rollback`. Commit errors are returned after config is already stored and reload event is logged. Copying relies on `copystructure`, including the custom `netip.Addr` copier to avoid zero-value addresses.

## Test Signals
`reload_test.go` covers labels, mirrors, insecure registries, preserving unrelated settings, network diagnostic toggling, DNS address preservation, and the custom `netip.Addr` copier.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/reload.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/reload_test.go -->
# sources/cloud-native/moby/daemon/reload_test.go

## Purpose
Tests daemon reload behavior for labels, registry mirrors, insecure registries, preservation of unrelated fields, network diagnostics, and copied `netip.Addr` values.

## Important APIs, Types, And Functions
`muteLogs` lowers log noise. `newDaemonForReloadT` constructs a minimal daemon with image and registry services. Tests call `Daemon.Reload`, `registry.NewService`, `ServiceConfig`, `daemon.networkOptions`, and libnetwork diagnostic methods.

## Control Flow
Tests build initial daemon configs, prepare reload configs with `ValuesSet`, invoke `Reload`, and assert new live config or registry service state. Invalid mirror tests expect reload errors; valid mirror/insecure registry tests inspect normalized service config. The diagnostic test, run only as root, repeatedly enables/disables diagnostic ports.

## State And Persistence
State is in-memory daemon config and service objects. The network diagnostic test creates a real libnetwork controller rooted in a temporary directory and mutates diagnostic server state.

## Dependencies And Integration Points
Depends on daemon config types, image service, registry service, libnetwork, copystructure, `netip`, and gotest assertions. It validates the integration between reload hooks and downstream services.

## Risks And Edge Cases
Some tests use manually populated `ValuesSet`; reload behavior depends on those flags. The diagnostic test requires root and is skipped otherwise. Registry tests inspect merged CIDR/index config rather than every TLS side effect.

## Test Signals
Passing tests confirm reload updates selected fields, leaves unmentioned fields unchanged, normalizes mirrors, replaces insecure registries exactly once, and preserves DNS/host gateway `netip.Addr` values.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/reload_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/reload_unix.go -->
# sources/cloud-native/moby/daemon/reload_unix.go

## Purpose
Provides Unix platform-specific daemon reload for runtimes, default shared memory size, cgroup namespace mode, and IPC mode.

## Important APIs, Types, And Functions
`reloadPlatform` mutates `configStore` fields and calls `setupRuntimes`. It builds event attributes for configured runtimes, default runtime, default shm size, default IPC mode, and default cgroup namespace mode.

## Control Flow
The hook applies supplied default runtime and runtime map, reconstructs the `Runtimes` runtime resolver, applies `default-shm-size`, `default-cgroupns-mode`, and `default-ipc-mode` when set, then renders runtime attributes by iterating configured runtime paths.

## State And Persistence
Only the reload copy (`newCfg`) is changed during prepare. The live daemon sees changes after `Reload` stores the new config. Runtime wrapper scripts may be created by `setupRuntimes`.

## Dependencies And Integration Points
Depends on daemon config and `runtime_unix.go` setup. It is called from `Daemon.Reload` only on Linux/FreeBSD builds.

## Risks And Edge Cases
Runtime setup is fallible and aborts the whole reload. Attribute rendering only includes `Config.Runtimes` entries and their paths, not implicit stock runtimes or type-only runtime options.

## Test Signals
Runtime setup and wrapper behavior are covered by `runtime_unix_test.go`; reload tests exercise general reload transaction paths.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/reload_unix.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/reload_windows.go -->
# sources/cloud-native/moby/daemon/reload_windows.go

## Purpose
Provides the Windows implementation of `reloadPlatform`, currently a no-op to satisfy the cross-platform daemon reload hook contract.

## Important APIs, Types, And Functions
`reloadPlatform` accepts the same transaction, config store, config, and attributes parameters as Unix but returns nil without mutation.

## Control Flow
No control flow beyond returning success.

## State And Persistence
No daemon config or platform state is changed by this file.

## Dependencies And Integration Points
Compiles into Windows daemon builds and is invoked by `Daemon.Reload` through the shared hook list.

## Risks And Edge Cases
Platform-specific reload settings implemented for Unix are not handled here. Any Windows reloadable platform option must be added explicitly.

## Test Signals
No file-local tests. Compile-time build coverage verifies the hook signature, and Windows reload behavior depends on broader daemon tests.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/reload_windows.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/rename.go -->
# sources/cloud-native/moby/daemon/rename.go

## Purpose
Implements container rename, including name reservation, linked-container alias updates, checkpoint persistence, sandbox rename, endpoint DNS name updates, rollback on failure, and event emission.

## Important APIs, Types, And Functions
`Daemon.ContainerRename(oldName, newName string)` is the public operation. It uses `GetContainer`, container locking, `reserveName`/`releaseName`, `linkIndex`, `containersReplica`, `CheckpointTo`, libnetwork sandbox/endpoint methods, `buildEndpointDNSNames`, and rename events.

## Control Flow
The function trims and validates names, loads and locks the container, canonicalizes the new name, rejects same-name renames, snapshots linked child suffixes, reserves new names for the container and links, updates container name and link index, checkpoints state, then for running containers renames the sandbox and updates endpoint DNS names. Deferred rollback restores names, reservations, link index entries, checkpoint state, sandbox name, and DNS names if a later step fails.

## State And Persistence
Mutates in-memory container name, name indexes, link indexes, network endpoint settings, and sandbox state. Persists the new container name to disk with `CheckpointTo`; rollback attempts to persist the old name if a post-checkpoint error occurs.

## Dependencies And Integration Points
Integrates with container store, name reservation replica, legacy links, libnetwork sandbox and endpoints, daemon event service, and persistent container metadata.

## Risks And Edge Cases
The function has multiple partial-mutation stages and relies heavily on deferred rollback. Rollback of sandbox and DNS failures is logged but cannot be guaranteed. Linked child names must be prefixed by the old container name or the operation aborts. Running containers have more external state to coordinate than stopped containers.

## Test Signals
No listed direct test, but rename API and network integration tests should assert name reservation conflicts, persistent metadata, event attributes, and DNS alias updates.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/rename.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/resize.go -->
# sources/cloud-native/moby/daemon/resize.go

## Purpose
Implements resize operations for a container's primary TTY and for exec sessions.

## Important APIs, Types, And Functions
`Daemon.ContainerResize` resolves a container, gets its running task, calls task `Resize`, and logs a resize event. `Daemon.ContainerExecResize` resolves exec config, waits for `ExecConfig.Started`, validates `Process`, and calls process `Resize`.

## Control Flow
Container resize locks only while getting the running task, then resizes with `context.WithoutCancel` so request cancellation does not interrupt runtime resize. Exec resize waits up to ten seconds for exec startup before resizing; if the exec process is nil after startup it returns an invalid-parameter error.

## State And Persistence
No durable state is changed. Runtime terminal dimensions change in containerd/process state, and successful container resize logs an event with height/width attributes.

## Dependencies And Integration Points
Depends on container lookup, running task/process abstractions, exec store, event logging, and API handlers parsing `h` and `w`.

## Risks And Edge Cases
Exec resize has a hardcoded ten-second timeout, making tests slow and behavior inflexible. Context cancellation is intentionally ignored for the actual resize call. Width/height are passed to backend as width then height even though public parameters are height then width.

## Test Signals
`resize_test.go` covers missing exec IDs, successful resize propagation to a mock process, and timeout when exec startup never completes.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/resize.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/resize_test.go -->
# sources/cloud-native/moby/daemon/resize_test.go

## Purpose
Tests exec resize behavior for missing exec instances, successful resize calls, and timeout while waiting for exec startup.

## Important APIs, Types, And Functions
`execResizeMockProcess` embeds the containerd process interface and records width/height in its `Resize` method. Tests use `container.NewExecStore`, `Daemon.registerExecCommand`, and `ContainerExecResize`.

## Control Flow
The missing-exec test registers one exec config but resizes a different ID. The success test closes `ec.Started`, attaches a mock process, and asserts recorded dimensions. The timeout test leaves `Started` open and expects the timeout error.

## State And Persistence
All state is in in-memory daemon, container, and exec stores. No runtime process or disk state is used.

## Dependencies And Integration Points
Linux-only test because it imports daemon/containerd process types under the Linux build. It validates the daemon backend used by API exec resize routes.

## Risks And Edge Cases
The timeout test waits for the production ten-second timeout, which is slow for a unit test and noted by a TODO. It does not cover nil process after a closed `Started` channel.

## Test Signals
Failures indicate lookup error text changed, resize argument ordering regressed, or exec-start timeout behavior changed.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/resize_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/restart.go -->
# sources/cloud-native/moby/daemon/restart.go

## Purpose
Implements container restart as a stop-then-start sequence with graceful stop options, manual restart marking, mount optimization, and restart event logging.

## Important APIs, Types, And Functions
`Daemon.ContainerRestart` is the public lookup wrapper. `Daemon.containerRestart` performs restart using `containerStop`, `containerStart`, `Mount`, `Unmount`, container isolation, and backend `ContainerStopOptions`.

## Control Flow
The operation strips cancellation from the context to keep restart atomic after admission. It resolves effective isolation, pre-mounts non-Hyper-V containers to avoid unmount/remount churn, marks running containers as manually restarted, stops them with the provided options, starts the container, and logs an `ActionRestart` event.

## State And Persistence
Mutates container state through stop/start, marks `HasBeenManuallyRestarted`, may mount/unmount the filesystem, and emits an event. The operation delegates actual persistence to stop/start paths.

## Dependencies And Integration Points
Used by API restart route and daemon internals. It integrates with platform isolation, mount management, stop/start lifecycle, event logging, and restart policy semantics.

## Risks And Edge Cases
Request cancellation cannot interrupt the stop/start sequence once begun. Mount optimization is skipped for Hyper-V isolation. If stop succeeds but start fails, the container remains stopped and the error is returned.

## Test Signals
No direct file-local tests are listed; lifecycle integration tests should verify stop options, event emission, manual restart effects, and failure behavior.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/restart.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/runtime_unix.go -->
# sources/cloud-native/moby/daemon/runtime_unix.go

## Purpose
Configures containerd runtimes for non-Windows daemons, including stock runc runtime entries, custom path runtimes, custom shim-type runtimes, wrapper scripts for runtime arguments, feature discovery, and validation of implicit containerd runtime names.

## Important APIs, Types, And Functions
`shimConfig` stores shim name, options, features, and optional preflight check. `runtimes` stores default and configured runtimes. Key functions are `stockRuntimes`, `defaultV2ShimConfig`, `runtimeScriptsDir`, `initRuntimesDir`, `setupRuntimes`, `wrapRuntime`, `(*runtimes).Get`, `(*runtimes).Features`, and `isPermissibleC8dRuntimeName`.

## Control Flow
`setupRuntimes` rejects attempts to override the reserved stock runtime, installs stock entries, validates default runtime, then processes configured runtimes. Path runtimes become runc-v2 options, optionally via generated shell wrappers when args are present. Type runtimes become direct shim names with generated typed options. `Get` resolves explicit or default runtimes, runs preflight checks, and permits implicit containerd runtime names only if they are well-formed and not path-like.

## State And Persistence
`initRuntimesDir` removes and recreates the runtime script directory. `wrapRuntime` writes executable wrapper scripts named from a hash of their contents so existing scripts referenced by running containers are not modified. Runtime feature discovery runs the runtime binary's `features` command and stores decoded OCI runtime features in memory.

## Dependencies And Integration Points
Integrates with daemon config, containerd runc options, containerd plugin runtime names, shim option generation, atomic file writes, and start code that calls `runtimes.Get`.

## Risks And Edge Cases
Wrapper scripts concatenate binary and args into shell without quoting, so configured paths/args must be trusted daemon config. Feature discovery failures only warn. Blocking path-like implicit runtime names is security-sensitive because containerd can otherwise execute arbitrary host binaries as root. Custom path runtimes without args are not preflight-checked.

## Test Signals
`runtime_unix_test.go` covers invalid config combinations, default runtime validation, explicit versus implicit runtime resolution, shim option generation, preflight checks, wrapper content, and wrapper immutability across reloads.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/runtime_unix.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/runtime_unix_test.go -->
# sources/cloud-native/moby/daemon/runtime_unix_test.go

## Purpose
Tests non-Windows runtime configuration, runtime resolution, preflight behavior, and wrapper-script stability.

## Important APIs, Types, And Functions
Tests call `config.New`, `initRuntimesDir`, `setupRuntimes`, `runtimes.Get`, and inspect `runcoptions.Options`/runtime option protobufs. `mergo` overlays test configs onto defaults.

## Control Flow
`TestSetupRuntimes` runs invalid and valid configuration cases. `TestGetRuntime` builds configured path, args, shim, shim-by-path, and gVisor option runtimes, then verifies resolved shim/options or invalid-argument errors. `TestGetRuntime_PreflightCheck` asserts only wrapper-script runtimes check binary existence. `TestRuntimeWrapping` records wrapper scripts, changes runtime config, reruns setup, and verifies old wrappers remain untouched.

## State And Persistence
Tests create temporary daemon roots and runtime script directories. Wrapper files are written and read from disk to verify content and immutability.

## Dependencies And Integration Points
Uses containerd runtime option types, Moby system runtime API types, protobuf cloning, filesystem errors, and gotest/cmp assertions. It validates behavior consumed by daemon start and reload paths.

## Risks And Edge Cases
The tests intentionally allow configured runtime names with slashes while rejecting path-like implicit runtime names. They depend on `/bin/true` and `/bin/false` for wrapper content cases.

## Test Signals
Passing tests confirm reserved runtime protection, argument/type/options compatibility rules, shim option decoding, invalid runtime name rejection, wrapper hashing, and persistence of wrapper scripts for existing containers.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/runtime_unix_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/runtime_windows.go -->
# sources/cloud-native/moby/daemon/runtime_windows.go

## Purpose
Provides Windows stubs for the runtime configuration API used by shared daemon code.

## Important APIs, Types, And Functions
Defines empty `runtimes` type with `Get`, plus `initRuntimesDir` and `setupRuntimes`. `Get` returns "not implemented"; setup functions return nil/empty values.

## Control Flow
No runtime resolution is implemented on Windows in this file. Calls either no-op during setup or return an error for `Get`.

## State And Persistence
No runtime script directory or runtime state is created by these stubs.

## Dependencies And Integration Points
Compiles against daemon config on Windows and satisfies references from shared reload/start code.

## Risks And Edge Cases
Any shared code that unexpectedly calls `runtimes.Get` on Windows receives a generic not-implemented error. Windows runtime selection is handled elsewhere.

## Test Signals
No file-local tests. Windows build/test jobs provide compile coverage.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/runtime_windows.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/seccomp_linux.go -->
# sources/cloud-native/moby/daemon/seccomp_linux.go

## Purpose
Applies seccomp configuration to OCI specs for Linux containers, respecting container-specific profiles, daemon defaults, privileged mode, and kernels without seccomp support.

## Important APIs, Types, And Functions
`supportsSeccomp` is true on Linux. `WithSeccomp(daemon, c)` returns a containerd OCI `SpecOpts` closure. It uses `daemon.RawSysInfo`, `seccomp.GetDefaultProfile`, `seccomp.LoadProfile`, container `SeccompProfile`, and daemon profile fields.

## Control Flow
The option returns immediately for unconfined containers. Privileged containers run unconfined unless a custom container profile is provided. Non-privileged containers require kernel seccomp support for custom/default profiles; if unsupported, custom profiles error and default behavior becomes unconfined with a warning. Otherwise the code ensures `s.Linux` exists and chooses profile priority: explicit default, container custom, daemon custom profile bytes, daemon unconfined setting, or built-in default profile.

## State And Persistence
The OCI spec is mutated in memory by setting `s.Linux.Seccomp`. The container's `SeccompProfile` may be changed to `unconfined` when kernel support is absent or daemon profile path is unconfined.

## Dependencies And Integration Points
Integrates with containerd OCI spec generation, Moby container security options, daemon sysinfo, Moby profiles/seccomp, and runtime start.

## Risks And Edge Cases
Privileged containers with custom profiles are allowed to load that profile, while privileged default/daemon profiles are ignored. Missing kernel support changes container state to unconfined for default profiles. Invalid JSON/profile content returns errors during spec construction.

## Test Signals
`seccomp_linux_test.go` covers unconfined, privileged custom/default/daemon, disabled-kernel custom error, empty default loading, container custom, daemon custom, and profile priority.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/seccomp_linux.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/seccomp_linux_test.go -->
# sources/cloud-native/moby/daemon/seccomp_linux_test.go

## Purpose
Tests Linux seccomp OCI spec mutation across privilege, daemon profile, container profile, and kernel-support combinations.

## Important APIs, Types, And Functions
`TestWithSeccomp` builds table cases with `Daemon`, `container.Container`, input/output `coci.Spec`, and expected errors. It calls `WithSeccomp` and compares against specs built from `oci.DefaultLinuxSpec` and Moby seccomp profiles.

## Control Flow
Each case constructs a daemon sysinfo and container host config, invokes the returned `SpecOpts`, then asserts the mutated spec and error. Cases verify unconfined, privileged custom profile, privileged default, privileged daemon profile ignored, disabled kernel custom error, default profile, container profile, daemon profile, and container-over-daemon priority.

## State And Persistence
Only in-memory specs and container structs are mutated. No seccomp files are loaded from disk; custom profiles are inline JSON strings.

## Dependencies And Integration Points
Depends on containerd OCI spec types, daemon OCI helper defaults, sysinfo, Moby profiles/seccomp, and gotest assertions.

## Risks And Edge Cases
Spec equality depends on default profile generation remaining stable. The tests focus on JSON minimal profiles and do not cover profile file paths or malformed profile strings.

## Test Signals
Passing tests confirm profile precedence, privileged-mode semantics, error behavior when kernel seccomp is unavailable, and default profile attachment.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/seccomp_linux_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/seccomp_unsupported.go -->
# sources/cloud-native/moby/daemon/seccomp_unsupported.go

## Purpose
Provides the non-Linux seccomp implementation, where seccomp support is unavailable and applying seccomp options is a no-op.

## Important APIs, Types, And Functions
`supportsSeccomp` is false. `WithSeccomp` returns a containerd OCI `SpecOpts` closure that accepts the standard parameters and returns nil.

## Control Flow
No control flow beyond returning success from the spec option.

## State And Persistence
No spec, container, or daemon state is changed.

## Dependencies And Integration Points
Compiles on non-Linux platforms and satisfies shared OCI spec generation code.

## Risks And Edge Cases
Security behavior differs by platform: non-Linux builds silently do not apply seccomp profiles. Callers must gate seccomp expectations on `supportsSeccomp`.

## Test Signals
No file-local tests. Cross-platform builds validate the stub signature.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/seccomp_unsupported.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/secrets.go -->
# sources/cloud-native/moby/daemon/secrets.go

## Purpose
Stores swarm secret references on a container by name.

## Important APIs, Types, And Functions
`Daemon.SetContainerSecretReferences(name string, refs []*swarmtypes.SecretReference) error` resolves a container and assigns `c.SecretReferences`.

## Control Flow
The function calls `GetContainer`; on success it replaces the container's secret reference slice and returns nil.

## State And Persistence
Mutates the in-memory container object. Persistence, if required, is handled by callers or later checkpoint paths, not in this function.

## Dependencies And Integration Points
Integrates with swarm secret types and daemon container lookup. It is likely called during service/task container setup.

## Risks And Edge Cases
The assignment is not protected by an explicit container lock in this function, so callers must ensure safe timing. Existing references are replaced wholesale.

## Test Signals
No direct tests in the listed set; integration tests around swarm secret injection should validate correct references.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/secrets.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/server/backend/backend.go -->
# sources/cloud-native/moby/daemon/server/backend/backend.go

## Purpose
Defines shared backend data structures used between API routers and daemon implementations for containers, logs, stats, image commit, plugins, and networks.

## Important APIs, Types, And Functions
Key structs include `ContainerCreateConfig`, `ContainerRmConfig`, `ContainerAttachConfig`, `PartialLogMetaData`, `LogMessage`, `LogAttr`, `LogSelector`, `ContainerStatsConfig`, `ContainerInspectOptions`, `ContainerListOptions`, `ContainerLogsOptions`, `ContainerStopOptions`, `ExecStartConfig`, `CreateImageConfig`, `CommitConfig`, plugin configs, and `NetworkListConfig`.

## Control Flow
This file contains type definitions only. Control flow is supplied by routers and daemon backend methods consuming these structs.

## State And Persistence
The structs carry request options, streams, log payloads, and configuration between layers. They do not persist state themselves, but some fields such as `LogMessage.Line` warn that backing bytes may be reused after logging.

## Dependencies And Integration Points
Imports Docker API container/network types, distribution references, daemon filters, OCI platform specs, and Go `io`/`time`. It is a central contract for container router, daemon lifecycle code, image commit, logs, stats, and plugin handlers.

## Risks And Edge Cases
Because this package is a cross-layer contract, field semantics must remain compatible with API version shims. `ContainerStopOptions.Timeout` uses nil versus `-1` versus `0` semantics that handlers must preserve.

## Test Signals
No direct tests; compile-time interface use and router/daemon tests validate these shapes.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/server/backend/backend.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/server/backend/checkpoint.go -->
# sources/cloud-native/moby/daemon/server/backend/checkpoint.go

## Purpose
Defines backend option structs for checkpoint list and delete operations.

## Important APIs, Types, And Functions
`CheckpointListOptions` carries `CheckpointDir`. `CheckpointDeleteOptions` carries `CheckpointID` and `CheckpointDir`.

## Control Flow
Type definitions only.

## State And Persistence
No state is changed. These options guide daemon checkpoint filesystem operations elsewhere.

## Dependencies And Integration Points
Used by checkpoint router handlers and daemon checkpoint backend methods.

## Risks And Edge Cases
Correct directory and checkpoint ID validation is left to backend implementations.

## Test Signals
Router checkpoint tests or daemon checkpoint tests validate use of these structs.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/server/backend/checkpoint.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/server/backend/disk_usage.go -->
# sources/cloud-native/moby/daemon/server/backend/disk_usage.go

## Purpose
Defines backend contracts for system disk usage reporting.

## Important APIs, Types, And Functions
`DiskUsageOptions` selects containers, images, volumes, and verbose detail. `DiskUsage` groups image, container, volume, and build cache reports. Type aliases expose API disk usage types for containers, images, and volumes.

## Control Flow
Type definitions only.

## State And Persistence
No state is mutated. Values returned through these structs represent computed daemon storage state.

## Dependencies And Integration Points
Used by `/system/df` handlers and daemon disk usage implementations. Integrates API types from build, container, image, and volume packages.

## Risks And Edge Cases
Verbose options can be expensive in backend implementations. Nil pointers in `DiskUsage` represent omitted categories and must be handled by response writers.

## Test Signals
System disk usage tests and API response tests validate this contract.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/server/backend/disk_usage.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/server/buildbackend/build.go -->
# sources/cloud-native/moby/daemon/server/buildbackend/build.go

## Purpose
Defines build-backend option and data contracts for build execution, build cache disk usage/prune, image resolution, progress streaming, and build outputs.

## Important APIs, Types, And Functions
Important definitions include `DiskUsageOptions`, `CachePruneOptions`, `PullOption` constants, `ProgressWriter`, `AuxEmitter`, `BuildConfig`, `BuildOptions`, `BuildOutput`, and `GetImageAndLayerOptions`.

## Control Flow
Type definitions and enum constants only. Routers and build manager implementations supply execution flow.

## State And Persistence
These structs carry request state such as build context streams, tags, auth configs, resource limits, cache settings, BuildKit outputs, session IDs, and platform selection. Persistence occurs in builder/image layers, not here.

## Dependencies And Integration Points
Imports Docker API build/container/registry types, daemon filters, and OCI platform specs. It bridges API build routes, legacy builder, BuildKit, image pull policy, cache prune, and progress output.

## Risks And Edge Cases
`BuildArgs` uses `map[string]*string` to distinguish omitted from empty values. Pull policy controls network access. Resource fields mirror container host config and need version-compatible parsing upstream.

## Test Signals
Build route and builder integration tests validate these contracts; this file has no direct tests.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/server/buildbackend/build.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/server/httpstatus/status.go -->
# sources/cloud-native/moby/daemon/server/httpstatus/status.go

## Purpose
Maps daemon, containerd, gRPC, and distribution errors to HTTP status codes for API responses.

## Important APIs, Types, And Functions
`FromError` is the public mapper. Helpers `statusCodeFromGRPCError` and `statusCodeFromDistributionError` translate gRPC codes and Docker distribution `errcode` values.

## Control Flow
`FromError` resolves containerd errdefs from the outermost error, checks known errdefs categories, then tries gRPC and distribution mappings. If unresolved, it recursively unwraps single or joined errors looking for a non-500 status. Unknown/untyped errors log a debug FIXME and return 500.

## State And Persistence
No persistent state. It emits logs for nil or unexpected errors.

## Dependencies And Integration Points
Used by server error handling and debug middleware. Depends on containerd errdefs, Docker distribution errcode, gRPC status codes, HTTP constants, and containerd logging.

## Risks And Edge Cases
The order favors outermost resolved errdefs, then recursive unwrapping. Joined errors return the first non-500 status found, so ordering can affect responses. Nil errors log and map to 500.

## Test Signals
No listed direct tests, but API error response tests should cover common errdefs, gRPC, distribution, wrapped, and joined errors.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/server/httpstatus/status.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/server/httputils/contenttype/contenttype.go -->
# sources/cloud-native/moby/daemon/server/httputils/contenttype/contenttype.go

## Purpose
Provides content negotiation helpers for Docker API handlers, including strict explicit Accept matching and general negotiation.

## Important APIs, Types, And Functions
`MatchAcceptStrict(requestHeaders, offers)` returns the best exact media-type match from the Accept header, ignoring wildcards and q=0. `Negotiate(requestHeaders, offers, defaultOffer)` delegates to `httputil.NegotiateContentType`.

## Control Flow
Strict matching parses Accept specs, iterates offers first, then specs, keeps the match with the highest q value, and preserves offer order on ties. General negotiation builds a synthetic request and delegates to the upstream utility.

## State And Persistence
No state is mutated.

## Dependencies And Integration Points
Used by container logs to opt into JSON streaming only when clients explicitly ask for supported JSON stream media types. Depends on `github.com/golang/gddo/httputil/header`.

## Risks And Edge Cases
Strict matching intentionally ignores `*/*` and `type/*`, which differs from normal HTTP negotiation but prevents accidental opt-in to experimental stream formats.

## Test Signals
`contenttype_test.go` covers no header, wildcards, q=0, q ordering, duplicate media types, and general negotiation cases.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/server/httputils/contenttype/contenttype.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/server/httputils/contenttype/contenttype_test.go -->
# sources/cloud-native/moby/daemon/server/httputils/contenttype/contenttype_test.go

## Purpose
Tests strict Accept matching and general content negotiation behavior.

## Important APIs, Types, And Functions
`TestMatchAcceptStrict` table-tests `contenttype.MatchAcceptStrict`. `TestNegotiateContentType` ports Go/gddo negotiation cases for `contenttype.Negotiate`.

## Control Flow
Each strict test constructs headers, calls the helper, and compares the expected media type. Negotiation tests iterate Accept strings, offers, defaults, and expected results.

## State And Persistence
No external state. Some strict tests run in parallel with local header maps.

## Dependencies And Integration Points
Depends on Go `net/http`, the local contenttype package, and standard testing. It guards container log format negotiation.

## Risks And Edge Cases
The tests explicitly distinguish strict matching from wildcard negotiation, preventing future accidental JSON log opt-in through broad Accept headers.

## Test Signals
Failures indicate changed q-value ordering, wildcard treatment, exact-match requirements, or fallback negotiation semantics.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/server/httputils/contenttype/contenttype_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/server/httputils/form.go -->
# sources/cloud-native/moby/daemon/server/httputils/form.go

## Purpose
Provides request form/query parsing helpers for Docker API handlers, including booleans, integers, repository tags, archive parameters, and OCI platform JSON.

## Important APIs, Types, And Functions
Functions include `BoolValue`, `BoolValueOrDefault`, `Uint32Value`, `Int64ValueOrZero`, `Int64ValueOrDefault`, `RepoTagReference`, `ArchiveFormValues`, `DecodePlatform`, and `DecodePlatforms`. `ArchiveOptions` carries container archive name/path.

## Control Flow
Boolean parsing treats empty, `0`, `no`, `false`, and `none` as false and anything else as true. `Uint32Value` manually strips a negative sign to distinguish syntax and range errors. Repo/tag parsing normalizes names, rejects digest references, and defaults missing tags to `latest`. Platform decoding requires OS and architecture when any platform is specified and rejects optional-only payloads.

## State And Persistence
Helpers only read request form state and return values; `ArchiveFormValues` calls `ParseForm`, which may populate `r.Form`.

## Dependencies And Integration Points
Used throughout container/image/archive routes. Depends on distribution reference parsing, daemon errdefs, and OCI platform specs.

## Risks And Edge Cases
Loose boolean parsing makes arbitrary non-false strings true. `Int64ValueOrZero` suppresses parse errors, while `Int64ValueOrDefault` surfaces them. Platform JSON must be a full JSON object, not Docker platform shorthand.

## Test Signals
`form_test.go` covers boolean cases, int parsing, uint32 syntax/range behavior, and detailed platform validation.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/server/httputils/form.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/server/httputils/form_test.go -->
# sources/cloud-native/moby/daemon/server/httputils/form_test.go

## Purpose
Tests HTTP form helper parsing for booleans, int64s, uint32s, and OCI platform JSON.

## Important APIs, Types, And Functions
Tests call `BoolValue`, `BoolValueOrDefault`, `Int64ValueOrZero`, `Int64ValueOrDefault`, `Uint32Value`, and `DecodePlatform`.

## Control Flow
Table tests populate `http.Request.Form` values and assert parsed values or error categories. Platform tests cover empty, non-JSON, malformed JSON, missing OS/architecture, optional-only fields, and a valid platform.

## State And Persistence
Only local request form maps are mutated. No network or disk state is involved.

## Dependencies And Integration Points
Uses containerd errdefs, OCI platform types, and gotest assertions. It guards parser behavior used by routes such as resize and create.

## Risks And Edge Cases
The uint32 test checks that negative values return `strconv.ErrRange`, while absent or empty values return syntax errors. Platform tests distinguish optional-only payload errors from missing required field errors.

## Test Signals
Failures indicate request compatibility changes in common API parsers.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/server/httputils/form_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/server/httputils/httputils.go -->
# sources/cloud-native/moby/daemon/server/httputils/httputils.go

## Purpose
Defines core HTTP utilities for Docker API handlers: API function signature, hijacking, stream closing, JSON content validation/decoding/encoding, form parsing, API version context access, and content-type matching.

## Important APIs, Types, And Functions
`APIVersionKey`, `APIFunc`, `HijackConnection`, `CloseStreams`, `CheckForJSON`, `ReadJSON`, `WriteJSON`, `ParseForm`, `VersionFromContext`, and `matchesContentType` are the main APIs.

## Control Flow
`CheckForJSON` allows missing content type only when there is no body. `ReadJSON` validates content type, treats nil/empty body as no-op, decodes one JSON document, closes the body, maps invalid JSON to invalid-parameter errors, and rejects extra JSON documents/content using `dec.More`. `ParseForm` ignores MIME-only parse errors for compatibility. `CloseStreams` prefers `CloseWrite` when available.

## State And Persistence
`ReadJSON` consumes and closes request bodies. `ParseForm` populates request form fields. `WriteJSON` writes response headers and body. No persistent daemon state is touched.

## Dependencies And Integration Points
Used by most API routers. Depends on daemon errdefs, Go HTTP/JSON/mime packages, and stream interfaces.

## Risks And Edge Cases
`VersionFromContext` panics if the context value under `APIVersionKey` is not a string. `ReadJSON`'s use of `dec.More` detects extra tokens in common object cases but is a subtle JSON decoder API choice. Hijack assumes the writer implements `http.Hijacker`.

## Test Signals
`httputils_test.go` covers content type matching and JSON body decoding for nil, empty, valid, whitespace, extra content, and invalid JSON cases.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/server/httputils/httputils.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/server/httputils/httputils_test.go -->
# sources/cloud-native/moby/daemon/server/httputils/httputils_test.go

## Purpose
Tests content-type validation and JSON request decoding helpers.

## Important APIs, Types, And Functions
Tests directly call `matchesContentType` and `ReadJSON`.

## Control Flow
Content-type tests verify exact JSON, charset parameters, unsupported media type error text, and malformed header error text. JSON tests verify nil body, empty body, valid JSON, whitespace around JSON, extra content rejection, and invalid JSON error wrapping.

## State And Persistence
Each test constructs local `http.Request` objects with string readers. `ReadJSON` closes request bodies but no external state is affected.

## Dependencies And Integration Points
Uses Go HTTP and testing packages. It protects behavior used by all JSON-reading API handlers.

## Risks And Edge Cases
Tests assert exact error strings, so intentional wording changes require test updates. They do not cover multiple valid JSON top-level documents outside the object-plus-extra pattern.

## Test Signals
Failures indicate request content validation or JSON error classification changed.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/server/httputils/httputils_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/server/httputils/json-seq.go -->
# sources/cloud-native/moby/daemon/server/httputils/json-seq.go

## Purpose
Creates JSON stream encoders for Docker API streaming responses, including RFC-style JSON text sequences.

## Important APIs, Types, And Functions
`EncoderFn` is the encoder function type. `NewJSONStreamEncoder(w, contentType)` selects encoding based on media type. `jsonSeq.Encode` prefixes records with ASCII record separator `0x1E` before JSON encoding.

## Control Flow
For `types.MediaTypeJSONSequence`, the helper returns a `jsonSeq` encoder. For NDJSON, JSON, JSON Lines, and unknown content types, it returns the standard `json.Encoder.Encode`.

## State And Persistence
Encoders write to the supplied `io.Writer`; no other state persists.

## Dependencies And Integration Points
Used by JSON log streaming. Depends on Docker API media type constants and Go JSON encoding.

## Risks And Edge Cases
Unknown content types silently fall back to newline-delimited JSON. JSON-seq relies on `json.Encoder` to add the line feed after each record.

## Test Signals
No direct tests listed; log stream tests or API content negotiation tests should validate wire format.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/server/httputils/json-seq.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/server/httputils/logstream/json_logstream.go -->
# sources/cloud-native/moby/daemon/server/httputils/logstream/json_logstream.go

## Purpose
Writes container log messages as a JSON stream, supporting stdout/stderr filtering, optional details, partial-log metadata, timestamps, and in-band errors.

## Important APIs, Types, And Functions
`WriteJSON` streams `backend.LogMessage` values to an HTTP response. `jsonLogWriter`, `newJSONLogWriter`, `jsonLogMessage`, and `(*jsonLogWriter).write` handle record conversion and encoding.

## Control Flow
`WriteJSON` sends status 200 immediately, wraps the response in a write flusher, picks a JSON stream encoder based on response content type, then loops until context cancellation or channel close. Messages with `Err` are always written with an error field; stdout/stderr messages are filtered by `ContainerLogsOptions`. Writer details include attrs only when requested.

## State And Persistence
Writes streaming response bytes and flushes headers; no daemon state is changed. Once the header is written, later errors are encoded in-band rather than returned as HTTP errors.

## Dependencies And Integration Points
Used by container logs route when JSON format is requested. Depends on backend log types, `httputils.NewJSONStreamEncoder`, and ioutils write flushing.

## Risks And Edge Cases
`write` ignores encoder errors, so client disconnects may not surface here. `Line` is converted to string and assumes text-oriented JSON output. Headers are committed before the backend channel is drained.

## Test Signals
No direct listed tests. Container logs API tests should validate media type negotiation, filtering, detail attrs, metadata, and error records.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/server/httputils/logstream/json_logstream.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/server/httputils/logstream/logstream.go -->
# sources/cloud-native/moby/daemon/server/httputils/logstream/logstream.go

## Purpose
Writes container log messages as raw or multiplexed byte streams for traditional Docker log responses.

## Important APIs, Types, And Functions
`Write(ctx, w, msgs, config, mux)` streams logs. `rfc3339NanoFixed` defines fixed-width timestamps. `attrsByteSlice` formats sorted log attrs as query-escaped `key=value` pairs. `byKey` sorts attrs.

## Control Flow
The function writes status 200 and flushes immediately, sets stdout/stderr/system error writers, optionally wrapping them with stdcopy multiplex writers, then loops over messages until cancellation or channel close. Error messages are written to system error stream. Details and timestamps are prepended before routing by source.

## State And Persistence
Only response bytes are written. `attrsByteSlice` sorts the message's `Attrs` slice in place, mutating message metadata order.

## Dependencies And Integration Points
Used by container logs route for raw/multiplexed stream formats. Depends on stdcopy, daemon stdcopymux, backend log options, and ioutils flushing.

## Risks And Edge Cases
Response headers are committed before log processing, so later errors are in-band. Writer errors are ignored. Attribute sorting mutation is documented as acceptable because nothing else should use the attrs afterward.

## Test Signals
No direct listed tests. Log API tests should validate mux headers, timestamp format, detail attr encoding, stdout/stderr filtering, and in-band error text.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/server/httputils/logstream/logstream.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/server/imagebackend/image.go -->
# sources/cloud-native/moby/daemon/server/imagebackend/image.go

## Purpose
Defines image-backend request/response option contracts for pull, push, remove, list, get, inspect, attestations, and inspect data compatibility.

## Important APIs, Types, And Functions
Important structs include `PullOptions`, `PushOptions`, `RemoveOptions`, `ListOptions`, `GetImageOpts`, `ImageInspectOpts`, `AttestationOpts`, and `InspectData`.

## Control Flow
This file contains type definitions only.

## State And Persistence
The structs carry API request parameters and image inspection data. `InspectData` embeds the modern inspect response and includes legacy fields such as `Parent`, `DockerVersion`, `Container`, `ContainerConfig`, and `GraphDriverLegacy` for older API versions.

## Dependencies And Integration Points
Used by image API routers and daemon image service. Depends on Docker API image/container/registry/storage types, daemon filters, HTTP headers, and OCI platform specs.

## Risks And Edge Cases
API-version compatibility is embedded in field comments: some fields are removed or changed in newer API versions but retained for older responses. Attestation options can avoid content-store reads when statements are not requested.

## Test Signals
Image route and inspect tests validate field inclusion/exclusion and option handling.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/server/imagebackend/image.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/server/middleware.go -->
# sources/cloud-native/moby/daemon/server/middleware.go

## Purpose
Applies global server middlewares around API handlers and conditionally adds debug request logging when the daemon log level is debug or lower.

## Important APIs, Types, And Functions
`(*Server).handlerWithGlobalMiddlewares(handler httputils.APIFunc) httputils.APIFunc` wraps the handler using `s.middlewares` and `middleware.DebugRequestMiddleware`.

## Control Flow
Starting from the route handler, the function iterates configured middlewares in slice order and replaces `next` with each wrapper. If logging is at debug level, it wraps the result in debug middleware. Comments note that middleware evaluation order is backwards: the first in the list is evaluated last.

## State And Persistence
No persistent state is changed. The returned function closes over the middleware chain.

## Dependencies And Integration Points
Used by the API server route setup. Depends on containerd log level, HTTP utility handler signature, and middleware package.

## Risks And Edge Cases
Middleware order is subtle and can affect headers, version validation, experimental flags, and debug logging. Debug middleware adds body peeking overhead for small JSON POST requests.

## Test Signals
Middleware-specific tests cover debug masking and version behavior; route integration tests validate combined behavior.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/server/middleware.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/server/middleware/debug.go -->
# sources/cloud-native/moby/daemon/server/middleware/debug.go

## Purpose
Adds debug logging around API requests, including method, URL, route vars, status for errors, and sanitized small JSON POST bodies.

## Important APIs, Types, And Functions
`DebugRequestMiddleware` wraps an API handler. `maskSecretKeys` recursively redacts sensitive keys in decoded JSON maps/arrays.

## Control Flow
The middleware prepares log fields, optionally peeks at JSON POST bodies up to 4 KiB, restores the request body through a buffered reader wrapper, decodes JSON into a map, masks secrets, serializes form data for log fields, calls the wrapped handler, and logs any error response status. Non-POST, non-JSON, or large requests skip body logging.

## State And Persistence
It reads/peeks the request body but preserves it for downstream handlers. It mutates the decoded logging copy of request JSON by masking values. It writes debug logs only.

## Dependencies And Integration Points
Uses `httputils.CheckForJSON`, `httpstatus.FromError`, containerd/log, logrus formatter detection, and ioutils body wrappers. Installed by `handlerWithGlobalMiddlewares` when debug logging is enabled.

## Risks And Edge Cases
Only selected key names are scrubbed; new secret-bearing fields may need updates. Body logging is limited to JSON objects/arrays that fit in 4 KiB. `Peek(maxBodySize)` treats non-EOF as too large or read error and skips body fields.

## Test Signals
`debug_test.go` verifies recursive, case-insensitive masking for secret/config data and credential-like fields.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/server/middleware/debug.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/server/middleware/debug_test.go -->
# sources/cloud-native/moby/daemon/server/middleware/debug_test.go

## Purpose
Tests redaction behavior for debug request logging.

## Important APIs, Types, And Functions
`TestMaskSecretKeys` calls the unexported `maskSecretKeys` helper with map structures.

## Control Flow
Table cases cover redacting `Data` in secret/config-style payloads, recursive masking of password/secret/jointoken/unlockkey/signingcakey fields, and case-insensitive matching.

## State And Persistence
The input maps are mutated in place and compared to expected maps. No logging or HTTP request handling is exercised.

## Dependencies And Integration Points
Uses gotest assertions. It guards the security-sensitive part of `DebugRequestMiddleware`.

## Risks And Edge Cases
The tests do not cover arrays even though `maskSecretKeys` supports them. They also do not verify middleware body preservation.

## Test Signals
Failures indicate potential debug-log secret leakage or intentional scrub-list changes.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/server/middleware/debug_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/server/middleware/experimental.go -->
# sources/cloud-native/moby/daemon/server/middleware/experimental.go

## Purpose
Adds the `Docker-Experimental` response header to every wrapped API request.

## Important APIs, Types, And Functions
`ExperimentalMiddleware` stores the header value. `NewExperimentalMiddleware` converts a boolean into `"true"` or `"false"`. `WrapHandler` sets the header before calling the next handler.

## Control Flow
The wrapper sets `Docker-Experimental` on the response and delegates to the wrapped API function.

## State And Persistence
No daemon state changes. The middleware writes response headers.

## Dependencies And Integration Points
Installed in the API server middleware chain to advertise daemon experimental mode to clients.

## Risks And Edge Cases
The header is set before downstream handlers, so later middleware/handlers could overwrite it. It reflects the value captured at middleware construction.

## Test Signals
No direct listed tests; API header integration tests should verify the header.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/server/middleware/experimental.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/server/middleware/middleware.go -->
# sources/cloud-native/moby/daemon/server/middleware/middleware.go

## Purpose
Defines the common API middleware interface used by the daemon server.

## Important APIs, Types, And Functions
`Middleware` requires `WrapHandler(func(ctx, w, r, vars) error) func(ctx, w, r, vars) error`.

## Control Flow
Interface definition only.

## State And Persistence
No state.

## Dependencies And Integration Points
Implemented by experimental and version middlewares and consumed by server route setup.

## Risks And Edge Cases
All middleware must preserve the API handler signature and error propagation behavior.

## Test Signals
Compile-time checks through middleware implementations and server setup.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/server/middleware/middleware.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/server/middleware/version.go -->
# sources/cloud-native/moby/daemon/server/middleware/version.go

## Purpose
Validates requested Docker API versions, sets standard version/OS response headers, and stores the effective API version in request context.

## Important APIs, Types, And Functions
`VersionMiddleware`, `NewVersionMiddleware`, `versionUnsupportedError`, and `WrapHandler` are the core APIs. `versionUnsupportedError` implements `InvalidParameter`.

## Control Flow
Construction validates default and minimum API versions are within daemon-supported bounds and that minimum is not above default. The wrapper sets `Server`, `Api-Version`, and `Ostype` headers, defaults missing route version to the server default, rejects versions below minimum or above default, stores the effective version in context under `httputils.APIVersionKey`, and calls the handler.

## State And Persistence
No persistent state changes. The middleware writes headers and creates a derived context for downstream handlers.

## Dependencies And Integration Points
Uses daemon config version constants, version comparison helpers, Go runtime OS, and httputils context key. API routers consume `VersionFromContext` for compatibility behavior.

## Risks And Edge Cases
Version comparisons are string-based through helper functions and rely on normalized `major.minor` inputs. Error responses still include version headers because headers are set before validation.

## Test Signals
`version_test.go` covers constructor validation, context version defaults/requested values, too-old/too-new errors, and headers on error.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/server/middleware/version.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/server/middleware/version_test.go -->
# sources/cloud-native/moby/daemon/server/middleware/version_test.go

## Purpose
Tests API version middleware validation, effective version propagation, error messages, and response headers.

## Important APIs, Types, And Functions
Tests call `NewVersionMiddleware`, `WrapHandler`, and `httputils.VersionFromContext`.

## Control Flow
Constructor tests check valid defaults and invalid ranges. Version tests wrap a handler that reads the context version, then run missing, minimum, too-old, and too-new route versions. Header tests assert `Server`, `Api-Version`, and `Ostype` are set even when version validation fails.

## State And Persistence
Uses local `httptest.ResponseRecorder` and request objects. No daemon state is involved.

## Dependencies And Integration Points
Depends on daemon config API version constants, runtime GOOS, gotest assertions, and HTTP testing.

## Risks And Edge Cases
Tests reuse a recorder across subcases in one function, so header state is cumulative but acceptable for the assertions made. They do not cover malformed version strings.

## Test Signals
Failures indicate changes to supported API range validation, context propagation, or headers required by clients.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/server/middleware/version_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/server/networkbackend/network.go -->
# sources/cloud-native/moby/daemon/server/networkbackend/network.go

## Purpose
Defines request structs for connecting and disconnecting containers from networks.

## Important APIs, Types, And Functions
`ConnectRequest` includes a container identifier and optional `EndpointConfig`. `DisconnectRequest` includes a container identifier and force flag.

## Control Flow
Type definitions only.

## State And Persistence
No state is changed; daemon network backend methods consume these values to mutate network attachments.

## Dependencies And Integration Points
Used by network API routers. Depends on Docker API network endpoint settings.

## Risks And Edge Cases
Validation of container name, endpoint config, and force behavior is left to route/backends.

## Test Signals
Network route and daemon network integration tests validate these request shapes.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/server/networkbackend/network.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/server/router/checkpoint/backend.go -->
# sources/cloud-native/moby/daemon/server/router/checkpoint/backend.go

## Purpose
Defines the checkpoint router backend interface.

## Important APIs, Types, And Functions
`Backend` requires `CheckpointCreate`, `CheckpointDelete`, and `CheckpointList`, using API checkpoint request/summary types and backend checkpoint option structs.

## Control Flow
Interface definition only.

## State And Persistence
No state is changed by this file. Implementations perform checkpoint filesystem/runtime operations.

## Dependencies And Integration Points
Implemented by the daemon checkpoint backend and consumed by checkpoint router handlers.

## Risks And Edge Cases
The router depends on backend methods returning correctly classified errors for HTTP mapping.

## Test Signals
Compile-time conformance and checkpoint route tests validate this contract.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/server/router/checkpoint/backend.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/server/router/checkpoint/checkpoint.go -->
# sources/cloud-native/moby/daemon/server/router/checkpoint/checkpoint.go

## Purpose
Registers experimental checkpoint API routes.

## Important APIs, Types, And Functions
`checkpointRouter` stores a `Backend` and route slice. `NewRouter`, `Routes`, and `initRoutes` construct and expose the route table.

## Control Flow
`NewRouter` creates the router and initializes routes. `initRoutes` registers GET and POST `/containers/{name:.*}/checkpoints` plus DELETE `/containers/{name}/checkpoints/{checkpoint}`, all marked experimental.

## State And Persistence
Router state is an in-memory backend pointer and route list.

## Dependencies And Integration Points
Integrates with daemon server router abstractions and checkpoint route handlers in `checkpoint_routes.go`.

## Risks And Edge Cases
The GET/POST route allows greedy container names, while DELETE uses a non-greedy `{name}` pattern, which may affect names containing slashes.

## Test Signals
Route registration is usually covered by API router integration tests.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/server/router/checkpoint/checkpoint.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/server/router/checkpoint/checkpoint_routes.go -->
# sources/cloud-native/moby/daemon/server/router/checkpoint/checkpoint_routes.go

## Purpose
Implements HTTP handlers for creating, listing, and deleting container checkpoints.

## Important APIs, Types, And Functions
`postContainerCheckpoint`, `getContainerCheckpoints`, and `deleteContainerCheckpoint` parse requests and call the checkpoint backend. They use `httputils.ParseForm`, `httputils.ReadJSON`, `httputils.WriteJSON`, and backend checkpoint option structs.

## Control Flow
Create parses form and JSON body into `checkpoint.CreateRequest`, calls `CheckpointCreate`, and returns 201. List parses form, calls `CheckpointList` with optional `dir`, normalizes nil results to an empty slice, and writes JSON 200. Delete parses form, calls `CheckpointDelete` with route checkpoint ID and optional dir, and returns 204.

## State And Persistence
Handlers mutate checkpoint state only through backend calls. They write HTTP response status/body.

## Dependencies And Integration Points
Connects experimental checkpoint routes to daemon checkpoint implementation and API checkpoint types.

## Risks And Edge Cases
`ReadJSON` allows an empty body for create, so backend must validate required fields. Directory parameters are passed through from form data.

## Test Signals
Checkpoint API tests should cover status codes, empty list normalization, JSON parsing, and backend error propagation.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/server/router/checkpoint/checkpoint_routes.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/server/router/container/backend.go -->
# sources/cloud-native/moby/daemon/server/router/container/backend.go

## Purpose
Defines the composite backend interface required by the container API router.

## Important APIs, Types, And Functions
Subinterfaces include `execBackend`, `copyBackend`, `stateBackend`, `monitorBackend`, `attachBackend`, `systemBackend`, `commitBackend`, and `sysInfoProvider`. `Backend` embeds all of them.

## Control Flow
Interface definitions only.

## State And Persistence
No state is changed. Methods represented here perform container lifecycle, exec, archive, logs, stats, prune, attach, commit, and sysinfo operations in implementations.

## Dependencies And Integration Points
Connects container router handlers to daemon implementations. Depends on Docker API container/network types, daemon container state types, backend option structs, filters, archive changes, and sysinfo.

## Risks And Edge Cases
The interface is broad; adding a route often expands this contract. Correct error classification and stream ownership are delegated to backend implementations.

## Test Signals
Compile-time implementation by daemon plus container router tests validate this contract.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/server/router/container/backend.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/server/router/container/container.go -->
# sources/cloud-native/moby/daemon/server/router/container/container.go

## Purpose
Registers all container-related API routes.

## Important APIs, Types, And Functions
`containerRouter` stores the backend and route slice. `NewRouter`, `Routes`, and `initRoutes` create the router and route table.

## Control Flow
`initRoutes` registers HEAD, GET, POST, PUT, and DELETE routes for container archive, list, inspect, logs, stats, attach, exec, create, kill, pause/unpause, restart/start/stop/wait/resize, rename, update, prune, commit, and remove. The prune route has a minimum API version of 1.25.

## State And Persistence
Router state is an in-memory backend reference and route slice.

## Dependencies And Integration Points
Integrates the container HTTP API with route handlers in `container_routes.go` and the daemon backend interface.

## Risks And Edge Cases
Many routes use greedy `{name:.*}` matching to support names with slashes. Route ordering matters because overlapping patterns could otherwise shadow each other.

## Test Signals
API route registration and handler tests validate route methods, paths, and version guards.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/server/router/container/container.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/server/router/container/container_routes.go -->
# sources/cloud-native/moby/daemon/server/router/container/container_routes.go

## Purpose
Implements the Docker container HTTP API handler layer. It parses and validates requests, applies API-version compatibility behavior, negotiates stream formats, handles hijacked/websocket streams, and delegates actual container work to the container backend interface.

## Important APIs, Types, And Functions
Major handlers include `postCommit`, `getContainersJSON`, `getContainersStats`, `getContainersLogs`, `postContainersStart`, `postContainersStop`, `postContainersKill`, `postContainersRestart`, `postContainersPause`, `postContainersUnpause`, `postContainersWait`, `getContainersChanges`, `getContainersTop`, `postContainerRename`, `postContainerUpdate`, `postContainersCreate`, `deleteContainers`, `postContainersResize`, `postContainersAttach`, `wsContainersAttach`, `postContainersPrune`, exec handlers, and archive handlers. Compatibility helpers include `decodeCommitRequest`, `handleVolumeDriverBC`, `rejectLegacyCapabilities`, `handleMACAddressBC`, `handleSysctlBC`, `handlePortBindingsBC`, and `epConfigForNetMode`.

## Control Flow
Handlers generally call `httputils.ParseForm` and/or `ReadJSON`, convert query/body data to backend option structs, check `httputils.VersionFromContext`, and call backend methods. Create is the most complex path: it decodes the create request while teeing the body for removed legacy fields, normalizes default network mode, applies many API-version shims for mounts, IPC, cgroup namespace, console size, annotations, healthcheck start interval, multiple networks, image mounts, gateway priority, MAC address, sysctls, port bindings, and pids limits, then calls `ContainerCreate` and appends warnings. Logs validate stdout/stderr before streaming, parse since/until, optionally select experimental JSON streaming by query or strict Accept header, and otherwise choose raw versus multiplexed stream content type. Attach hijacks HTTP or uses websockets, prepares streams, and writes in-band error responses when hijack-time attach fails. Wait handles legacy pre-1.30 and pre-1.34 response timing/removal behavior.

## State And Persistence
The router itself persists no daemon state, but backend calls mutate containers, execs, archives, logs, images, and prune state. Handlers mutate decoded request structs for backward compatibility before passing them down. Streaming handlers commit headers early; after that, errors are written in-band or logged.

## Dependencies And Integration Points
This file is the main integration point between HTTP routes and daemon backends. It depends on Docker API media types, container/mount/network types, daemon filters, runconfig decoding, timestamp parsing, API version helpers, netlabel endpoint sysctls, backend option structs, HTTP status mapping, content negotiation, log stream writers, errdefs, OpenTelemetry, and websockets.

## Risks And Edge Cases
API compatibility logic is dense and version-sensitive. Create request body teeing is required because removed fields would otherwise disappear during JSON decoding. Hijack attach paths manually write HTTP status lines and ignore some write errors. Once logs/stats/wait streams write headers, status-code error reporting is no longer possible. MAC/sysctl migration must avoid ambiguous networks. The commented-out future port-binding behavior shows pending compatibility debt.

## Test Signals
The listed files do not include route-specific tests, but this handler should be covered by API integration tests for create compatibility, logs media types, attach streams, wait behavior, resize parsing, archive operations, exec lifecycle, prune, commit, update, and route error mapping.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/server/router/container/container_routes.go -->
