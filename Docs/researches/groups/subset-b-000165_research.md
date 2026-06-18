# subset-b-000165 grouped research

This grouped report covers the requested `sources/cloud-native/moby/client` files. Each section is source-tree aligned and bounded by reconciliation markers for deterministic splitting into `Docs/researches/<source>_research.md`.

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/client/checkpoint_remove_test.go -->
# sources/cloud-native/moby/client/checkpoint_remove_test.go

Purpose: validates the checkpoint delete client path for the experimental checkpoint API. The file does not define production APIs; it exercises `Client.CheckpointRemove`, `CheckpointRemoveOptions`, and the shared mock client helpers.

Control flow and dependencies: tests construct a client with `New(WithMockClient(...))`, call `CheckpointRemove` with a container id and checkpoint id, and assert either containerd `cerrdefs` error classes or the generated HTTP request. The success case expects `DELETE /containers/container_id/checkpoints/checkpoint_id`; error cases cover daemon 500 and empty or whitespace container ids through `trimID`.

State and integration behavior: no persistent state is modified in the test process beyond the mock transport. The test integrates with `client_mock_test.go` helpers, the versioned request path logic in `Client.getAPIPath`, and status-code-to-error mapping in the request layer.

Risks and test signals: the main risk covered is accidental route or method drift for checkpoint removal. It does not assert the optional `CheckpointDir` query, so that behavior depends on implementation coverage elsewhere.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/client/checkpoint_remove_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/client/client.go -->
# sources/cloud-native/moby/client/client.go

Purpose: defines the Docker/Moby Engine API `Client`, its default construction path, host parsing, version negotiation, redirect policy, raw dialers, and package-level API version constants. It is the central integration point for all endpoint wrapper files in this package.

Important APIs/types/functions: `Client`, `New`, deprecated `NewClientWithOpts`, `CheckRedirect`, `Close`, `ClientVersion`, `DaemonHost`, `ParseHostURL`, `Dialer`, `MaxAPIVersion`, `MinAPIVersion`, `DummyHost`, and `ErrRedirect`. `Client` embeds `clientConfig`, stores an atomic `negotiated` flag, a negotiation mutex, and `baseTransport` for direct transport operations such as closing idle connections and extracting dialers.

Control flow: `New` parses `DefaultDockerHost`, creates a default `http.Client`, applies functional options in caller order, resolves API version override precedence, stores the base transport when possible, infers `http` vs `https` from TLS configuration, wraps transport with OpenTelemetry, then optionally wraps it with response hooks. `getAPIPath` lazily triggers `Ping`-based negotiation, prefixes paths with `/v<version>` when a version is configured, and appends encoded query values. `negotiateAPIVersion` parses daemon ping version, rejects versions below `MinAPIVersion`, and downgrades from `MaxAPIVersion` when needed.

State and persistence behavior: client state is in-memory only: configured host/proto/address/version, negotiation completion, transport wrappers, idle connections, custom headers, hooks, and trace options. It persists no files. `Close` only closes idle connections on the saved base transport.

Dependencies and integration points: depends on `github.com/docker/go-connections/sockets` for `unix`, `npipe`, and TCP transport setup; containerd errdefs for invalid version errors; internal `versions` parsing/comparison; internal module version lookup for the default user agent; OpenTelemetry HTTP transport wrapping. Endpoint files depend on `getAPIPath`, request helpers, and `dialer`/`postHijacked`.

Risks and test signals: important risks are API negotiation races, option precedence, local-socket host handling via `DummyHost`, redirects changing non-GET semantics, and transport wrapper ordering. `client_test.go` covers construction, host parsing, API path generation, negotiation paths, fixed versions, connection failure behavior, and redirect policy.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/client/client.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/client/client_example_test.go -->
# sources/cloud-native/moby/client/client_example_test.go

Purpose: provides a package example showing how consumers create a client with environment-derived options and list containers. It documents the intended public API shape more than it validates daemon behavior.

Important APIs/functions: `Example` uses `client.New(client.FromEnv)`, `ContainerList`, `ContainerListOptions{All: true}`, and iterates over `ContainerListResult.Items`.

Control flow and integration: the example creates a context, constructs an API client, calls the container list endpoint, and prints selected fields. It integrates with the package doc in `client.go` and with `go test` example compilation.

State, risks, and test signals: no persistent state; network behavior is illustrative and not expected to run against a real daemon in normal unit tests. The signal is compile-time API usability: if names or return shapes change, the example fails to build.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/client/client_example_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/client/client_interfaces.go -->
# sources/cloud-native/moby/client/client_interfaces.go

Purpose: declares the public client interface graph for the Engine API. It groups endpoint methods by domain so callers can depend on narrower interfaces while `Client` satisfies the full `APIClient`.

Important APIs/types: `APIClient`, private `stableAPIClient`, `SwarmManagementAPIClient`, `HijackDialer`, and domain interfaces for checkpoint, container, exec, distribution, registry search, image build, image, network, node, plugin, service, task, swarm, system, volume, secret, and config operations.

Control flow and dependencies: this file has no runtime control flow. It imports `context`, `io`, and `net`, and refers to option/result types implemented throughout the package. `var _ APIClient = &Client{}` in `client.go` makes this file a compile-time contract for endpoint coverage.

State and integration behavior: no state or persistence. Integration risk is high because any method signature drift in endpoint files or generated API types breaks interface satisfaction and downstream compile-time compatibility.

Risks and test signals: the key risk is public API churn. Compile tests across the package are the primary signal; missing methods are caught by the `Client` interface assertion.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/client/client_interfaces.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/client/client_mock_test.go -->
# sources/cloud-native/moby/client/client_mock_test.go

Purpose: supplies test-only HTTP transport and assertion helpers used across endpoint tests. It centralizes request path/method checks, JSON response generation, ping mocking for version negotiation, and daemon-like default headers.

Important APIs/functions: `assertRequest`, `assertRequestWithQuery`, `ensureBody`, `makeTestRoundTripper`, `applyDefaultHeaders`, `WithMockClient`, `WithBaseMockClient`, `errorMock`, `mockJSONResponse`, `mockPingResponse`, and `mockResponse`.

Control flow: `WithMockClient` installs an `http.Client` whose transport automatically answers `/_ping`, letting regular endpoint tests exercise negotiation. Other requests are delegated to test callbacks and normalized with non-nil bodies/default daemon headers. `WithBaseMockClient` skips ping/default headers for tests that need precise lower-level behavior.

State and integration behavior: no persisted state. The helpers emulate enough daemon behavior for client-side logic, including version headers and JSON error bodies. They depend on `testRoundTripper` from `client_options.go`, API type packages, and standard `net/http`.

Risks and test signals: if the mock diverges from real daemon response headers, tests can miss production regressions. Conversely, these helpers make route, query, body, and error assertions consistent across the package.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/client/client_mock_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/client/client_options.go -->
# sources/cloud-native/moby/client/client_options.go

Purpose: defines the functional option system for constructing `Client` instances, including environment configuration, host/transport/TLS setup, API version overrides, tracing, headers, timeout, and response hooks.

Important APIs/types/functions: `clientConfig`, `ResponseHook`, `Opt`, `FromEnv`, `WithDialContext`, `WithHost`, `WithHostFromEnv`, `WithHTTPClient`, `WithTimeout`, `WithUserAgent`, `WithHTTPHeaders`, `WithScheme`, `WithTLSClientConfig`, `WithTLSClientConfigFromEnv`, `WithAPIVersion`, deprecated `WithVersion`, `WithAPIVersionFromEnv`, deprecated `WithVersionFromEnv`, no-op deprecated `WithAPIVersionNegotiation`, `WithTraceProvider`, `WithTraceOptions`, and `WithResponseHook`.

Control flow: `FromEnv` applies TLS, host, then API version env options. `WithHost` parses the host, updates proto/addr/basePath, and reconfigures the underlying `http.Transport` unless using the package test transport. `WithHTTPClient` clones caller clients/transports to avoid mutating external state. TLS options either mutate the existing transport or, for env TLS, replace the client with a TLS-configured one. API version options trim optional `v`, validate syntax, and store manual/env override slots for `New` to resolve.

State and persistence behavior: state is entirely in the in-memory `clientConfig`; TLS options read certificate files named by arguments or `DOCKER_CERT_PATH` but do not write. Environment options read `DOCKER_HOST`, `DOCKER_API_VERSION`, `DOCKER_CERT_PATH`, and `DOCKER_TLS_VERIFY`.

Dependencies and integration points: uses docker go-connections sockets/TLS helpers, containerd errdefs for duplicate header validation, OpenTelemetry tracing options, and `parseAPIVersion`. Endpoint requests later consume configured headers, user agent, scheme, client, and hooks.

Risks and test signals: risks include option order surprises, env/manual API version precedence, duplicate header canonicalization, replacing transports during TLS env setup, and nil response hooks. `client_options_test.go` covers host/env behavior, timeouts, API version parsing and priority, user agent/header rules, cloned HTTP clients, and response hook validation.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/client/client_options.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/client/client_options_test.go -->
# sources/cloud-native/moby/client/client_options_test.go

Purpose: validates the functional options used by `New`. It is the main regression suite for environment variables, API version override precedence, custom clients, user agents, headers, timeouts, and response hooks.

Important coverage: tests exercise `WithHostFromEnv`, `WithTimeout`, `WithAPIVersion`, `WithAPIVersionFromEnv`, deprecated version aliases, option override priority, `WithUserAgent`, `WithHTTPHeaders`, `WithHTTPClient`, and `WithResponseHook`.

Control flow and dependencies: tests set environment variables with Go test helpers, create clients with combinations of options, and inspect resulting client fields or outgoing mock requests. They depend on `gotest.tools` assertions, `net/http`, and package mock transports.

State and integration behavior: environment mutation is test-scoped. No persistent state. The tests protect integration with Docker CLI style env vars and request header generation in the request layer.

Risks and test signals: this file catches subtle compatibility regressions: empty API versions should allow negotiation, env API version wins over manual version per current implementation, duplicate canonical HTTP headers fail, custom HTTP clients are cloned, and nil response hooks are rejected.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/client/client_options_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/client/client_responsehook.go -->
# sources/cloud-native/moby/client/client_responsehook.go

Purpose: implements a transport wrapper that invokes configured `ResponseHook` callbacks after each successful underlying HTTP round trip.

Important APIs/types/functions: private `responseHookTransport` with `base http.RoundTripper`, `hooks []ResponseHook`, and `RoundTrip`.

Control flow: `RoundTrip` delegates to `base.RoundTrip`; if an error occurs it returns immediately without invoking hooks. For non-error responses it invokes hooks in stored order and returns the original response unchanged.

State and integration behavior: no persistence. Hook slices are cloned in `New`, so later mutation of the config slice does not affect the installed transport. Hooks must not consume or close the body; this file does not enforce that contract.

Risks and test signals: risks are hook side effects on response bodies and transport wrapping order with OpenTelemetry. `client_options_test.go` covers option validation and hook installation at construction.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/client/client_responsehook.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/client/client_test.go -->
# sources/cloud-native/moby/client/client_test.go

Purpose: tests central `Client` behavior: construction, env configuration, API path formatting, host URL parsing, version negotiation, connection failures, and redirect policy.

Important coverage: `TestNewClientWithNilOpt`, env-based client construction, `TestGetAPIPath`, `TestParseHostURL`, default version setting, negotiation with lower/equal/higher daemon versions, invalid/too-old versions, negotiation override behavior, automatic negotiation with empty/fixed versions, connection failure mapping, and `CheckRedirect`.

Control flow and dependencies: tests use mock transports and synthetic ping responses to drive `Client.checkVersion` and `negotiateAPIVersion`. Host parsing tests cover Unix sockets, Windows named pipes, TCP hosts, and invalid forms.

State and integration behavior: no persistent state; environment variables are scoped to tests. The tests protect all endpoint wrappers because every wrapper uses `getAPIPath`, negotiation, host setup, and redirect handling.

Risks and test signals: primary risks are incorrect version prefixing, silently using unsupported daemon API versions, unexpected redirect following for non-GET requests, and losing connection-failed classification. This suite is high-signal because many endpoint tests rely on this shared core.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/client/client_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/client/client_unix.go -->
# sources/cloud-native/moby/client/client_unix.go

Purpose: supplies Unix-like platform defaults for daemon connection handling.

Important APIs/functions: `DefaultDockerHost = "unix:///var/run/docker.sock"` and a stub `dialPipeContext` that returns an unsupported-protocol error on non-Windows builds.

Control flow and dependencies: no runtime branching beyond returning an error from `dialPipeContext`; imports `context`, `fmt`, and `net`.

State and integration behavior: no persistence. `client.go` uses `DefaultDockerHost` during `New`, and `dialer` only calls `dialPipeContext` for `npipe`.

Risks and test signals: platform build tags are the key risk. Unix builds must not accidentally attempt Windows named-pipe dialing.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/client/client_unix.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/client/client_windows.go -->
# sources/cloud-native/moby/client/client_windows.go

Purpose: supplies Windows-specific daemon connection defaults and named-pipe dialing.

Important APIs/functions: `DefaultDockerHost = "npipe:////./pipe/docker_engine"` and `dialPipeContext`, which delegates to `winio.DialPipeContext`.

Control flow and dependencies: minimal platform-specific implementation guarded by build tags. It imports `github.com/Microsoft/go-winio`.

State and integration behavior: no persistence. `client.go` uses this default host on Windows and calls `dialPipeContext` when the configured protocol is `npipe`.

Risks and test signals: compatibility depends on build tags and named-pipe address formatting. Cross-platform tests around `ParseHostURL` and request host behavior indirectly protect this path.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/client/client_windows.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/client/config_create.go -->
# sources/cloud-native/moby/client/config_create.go

Purpose: implements Swarm config creation through the Engine API.

Important APIs/types/functions: `ConfigCreateOptions{Spec swarm.ConfigSpec}`, `ConfigCreateResult{ID string}`, and `Client.ConfigCreate`.

Control flow: posts `options.Spec` as JSON to `/configs/create`, closes the response body, decodes `swarm.ConfigCreateResponse`, and returns only the created config ID.

State and integration behavior: no local persistence; daemon-side Swarm config state is created. Depends on shared `post`, JSON decoding, body closing, and `swarm` API types.

Risks and test signals: risks are route/body drift and decode failures. `config_create_test.go` asserts daemon errors are mapped and the successful route is `POST /configs/create`.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/client/config_create.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/client/config_create_test.go -->
# sources/cloud-native/moby/client/config_create_test.go

Purpose: validates `Client.ConfigCreate` error propagation and request routing.

Important coverage: internal-server-error mapping and successful `POST /configs/create` against the mock transport.

Control flow and dependencies: constructs a client with `WithMockClient`, uses `errorMock` or a callback that calls `assertRequest`, then calls `ConfigCreate` with a `ConfigCreateOptions` value.

State, risks, and test signals: no persistent state. The test confirms method/path behavior but does not deeply inspect the encoded `swarm.ConfigSpec` body.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/client/config_create_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/client/config_inspect.go -->
# sources/cloud-native/moby/client/config_inspect.go

Purpose: implements Swarm config inspection and returns both typed and raw JSON response data.

Important APIs/types/functions: `ConfigInspectOptions`, `ConfigInspectResult{Config swarm.Config, Raw json.RawMessage}`, and `Client.ConfigInspect`.

Control flow: validates/trims the config id with `trimID`, GETs `/configs/{id}`, and uses `decodeWithRaw` to fill the typed config and preserve raw daemon JSON.

State and integration behavior: no local persistence. Depends on `trimID`, shared `get`, `decodeWithRaw`, and Swarm config API types.

Risks and test signals: risks include missing body closure through `decodeWithRaw` semantics, invalid id handling, and not-found mapping. `config_inspect_test.go` covers empty ids, daemon errors, 404 classification, and success.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/client/config_inspect.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/client/config_inspect_test.go -->
# sources/cloud-native/moby/client/config_inspect_test.go

Purpose: tests `ConfigInspect` behavior for missing ids, daemon errors, not-found responses, and successful inspection.

Important coverage: empty and whitespace ids should produce `cerrdefs.IsInvalidArgument`; 404 responses should classify as not found; success expects `GET /configs/config_id` and JSON decoding into a Swarm config.

Control flow and dependencies: uses `WithMockClient`, `errorMock`, `mockJSONResponse`, and `assertRequest`.

State and risks: no persistent state. The tests protect public error contracts and route stability for config inspection.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/client/config_inspect_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/client/config_list.go -->
# sources/cloud-native/moby/client/config_list.go

Purpose: lists Swarm configs with optional filter encoding.

Important APIs/types/functions: `ConfigListOptions{Filters Filters}`, `ConfigListResult{Items []swarm.Config}`, and `Client.ConfigList`.

Control flow: creates query values, delegates filter JSON encoding to `Filters.updateURLValues`, GETs `/configs`, closes the response, and decodes a JSON array into `Items`.

State and integration behavior: read-only daemon operation with no local persistence. Depends on shared `Filters`, `get`, JSON decoding, and Swarm types.

Risks and test signals: risks are filter serialization drift and response body leaks. `config_list_test.go` asserts route, filter query behavior for empty/non-empty filters, daemon error mapping, and decode success.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/client/config_list.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/client/config_list_test.go -->
# sources/cloud-native/moby/client/config_list_test.go

Purpose: validates `ConfigList` error handling and filter query encoding.

Important coverage: internal server errors classify correctly; successful cases assert `GET /configs` and inspect `filters` query values, including empty filters and label filters.

Control flow and dependencies: table-driven tests build `Filters`, install mock transports, and decode returned JSON config lists.

State and risks: no persistent state. The tests are a signal for shared `Filters.updateURLValues` integration in config listing.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/client/config_list_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/client/config_remove.go -->
# sources/cloud-native/moby/client/config_remove.go

Purpose: removes a Swarm config by id.

Important APIs/types/functions: `ConfigRemoveOptions`, `ConfigRemoveResult`, and `Client.ConfigRemove`.

Control flow: validates the id with `trimID`, issues `DELETE /configs/{id}`, closes the response, and returns an empty future-proof result.

State and integration behavior: no local persistence; daemon-side config state is deleted. Depends on shared `delete`, `ensureReaderClosed`, and id validation.

Risks and test signals: risks are accidental id/path changes and body leaks. `config_remove_test.go` covers invalid ids, daemon error mapping, and successful route/method.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/client/config_remove.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/client/config_remove_test.go -->
# sources/cloud-native/moby/client/config_remove_test.go

Purpose: tests `ConfigRemove` invalid-id behavior, error propagation, and successful route construction.

Important coverage: empty and whitespace ids map to `cerrdefs.IsInvalidArgument`; daemon 500 maps to internal; success expects `DELETE /configs/config_id`.

Control flow and dependencies: uses package mock client helpers and gotest assertions.

State and risks: no persistent state. The test protects destructive route correctness for config removal.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/client/config_remove_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/client/config_update.go -->
# sources/cloud-native/moby/client/config_update.go

Purpose: updates an existing Swarm config specification at a particular object version.

Important APIs/types/functions: `ConfigUpdateOptions{Version swarm.Version, Spec swarm.ConfigSpec}`, `ConfigUpdateResult`, and `Client.ConfigUpdate`.

Control flow: validates id, sets `version=<Version.String()>` in the query, posts `options.Spec` to `/configs/{id}/update`, closes the response, and returns an empty result.

State and integration behavior: no local persistence; daemon-side config state changes subject to Swarm version concurrency. Depends on `trimID`, `post`, `ensureReaderClosed`, `url.Values`, and Swarm types.

Risks and test signals: risk is missing or wrong version query causing daemon update conflicts. `config_update_test.go` covers invalid ids, daemon errors, and method/path; query version coverage is comparatively light.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/client/config_update.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/client/config_update_test.go -->
# sources/cloud-native/moby/client/config_update_test.go

Purpose: validates `ConfigUpdate` error and routing behavior.

Important coverage: daemon 500 mapping, invalid empty/whitespace ids, and successful `POST /configs/config_id/update`.

Control flow and dependencies: uses mock clients, `assertRequest`, and `gotest.tools` error assertions.

State and risks: no persistence. The test verifies the update endpoint shape but does not assert the `version` query or encoded spec body in detail.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/client/config_update_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/client/container_attach.go -->
# sources/cloud-native/moby/client/container_attach.go

Purpose: implements attaching to a container’s stdio/log stream through an HTTP connection upgrade.

Important APIs/types/functions: `ContainerAttachOptions`, `ContainerAttachResult{HijackedResponse}`, and `Client.ContainerAttach`.

Control flow: validates container id, maps booleans and detach keys to query parameters (`stream`, `stdin`, `stdout`, `stderr`, `detachKeys`, `logs`), then calls `postHijacked` on `/containers/{id}/attach` with `Content-Type: text/plain`. It returns a `HijackedResponse`; the caller owns closing the connection.

State and integration behavior: no local persistence; it creates a long-lived network connection. Integrates with `hijack.go`, raw dialer selection in `client.go`, and Docker stream multiplexing conventions described in comments.

Risks and test signals: risks include leaked hijacked connections, incorrect query flags, and TTY vs multiplexed stream handling by callers. Dedicated attach tests are not in this subset, so coverage is indirect through hijack and exec attach tests.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/client/container_attach.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/client/container_commit.go -->
# sources/cloud-native/moby/client/container_commit.go

Purpose: creates a new image from a container’s filesystem changes.

Important APIs/types/functions: `ContainerCommitOptions`, `ContainerCommitResult{ID}`, and `Client.ContainerCommit`.

Control flow: validates container id, parses an optional normalized reference, rejects digest references, extracts repository/tag, builds query fields (`container`, `repo`, `tag`, `comment`, `author`, repeated `changes`, optional `pause=0`), posts optional container config to `/commit`, closes the response, and decodes `container.CommitResponse.ID`.

State and integration behavior: no local persistence; daemon creates image state. Depends on distribution reference parsing, shared request helpers, JSON decoding, and container API types.

Risks and test signals: risks are reference normalization, accidentally accepting digest tags, query encoding of Dockerfile changes, and pause semantics. `container_commit_test.go` asserts errors, invalid ids, route, query fields, `NoPause`, and response ID decoding.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/client/container_commit.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/client/container_commit_test.go -->
# sources/cloud-native/moby/client/container_commit_test.go

Purpose: tests `ContainerCommit` request construction and error behavior.

Important coverage: daemon internal errors, invalid container ids, method/path `POST /commit`, query parameters for container, repo/tag/comment/author/changes, `pause=0` when `NoPause` is true, and decoding the returned image ID.

Control flow and dependencies: mock callbacks inspect the request and return JSON commit responses. It depends on `assertRequest`, `errorMock`, and container API types.

State and risks: no local persistence. This is high-signal for compatibility with Docker image reference handling and commit query conventions.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/client/container_commit_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/client/container_copy.go -->
# sources/cloud-native/moby/client/container_copy.go

Purpose: implements stat, upload, and download operations for container filesystem archives.

Important APIs/types/functions: `ContainerStatPathOptions/Result`, `CopyToContainerOptions/Result`, `CopyFromContainerOptions/Result`, `Client.ContainerStatPath`, `Client.CopyToContainer`, `Client.CopyFromContainer`, and `getContainerPathStatFromHeader`.

Control flow: stat validates container id, normalizes the path with `filepath.ToSlash`, sends `HEAD /containers/{id}/archive`, and decodes `X-Docker-Container-Path-Stat` from base64 JSON. Copy-to sends a raw tar reader with `PUT /containers/{id}/archive`, path query, default `noOverwriteDirNonDir=true`, and optional `copyUIDGID=true`. Copy-from sends `GET /containers/{id}/archive`, decodes stat headers, and returns the response body to the caller without closing it.

State and integration behavior: no local persistence, but daemon filesystem content is read or modified. Streaming responses transfer body ownership to callers; simple HEAD/PUT paths close responses internally.

Dependencies: `encoding/base64`, `encoding/json`, `filepath`, shared raw request helpers, `container.PathStat`, and error mapping in the request layer.

Risks and test signals: risks include missing stat headers, body ownership leaks, platform path separator differences, and unsafe overwrite defaults. `container_copy_test.go` covers not-found/internal errors, invalid ids, missing/invalid stat header behavior, query flags, request body forwarding, and returned stream content.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/client/container_copy.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/client/container_copy_test.go -->
# sources/cloud-native/moby/client/container_copy_test.go

Purpose: validates the three archive-related container operations: stat path, copy to container, and copy from container.

Important coverage: daemon errors, 404 not-found classification, invalid ids, missing path stat headers, expected `HEAD`/`PUT`/`GET /containers/container_id/archive`, path query normalization, default `noOverwriteDirNonDir=true`, request body transmission, response stream return, and close behavior.

Control flow and dependencies: tests use mock headers containing base64 JSON `container.PathStat`, inspect query/body data, and read returned `io.ReadCloser` content.

State and risks: no persistent test state. The suite is high-signal for stream ownership and Docker archive protocol compatibility.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/client/container_copy_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/client/container_create.go -->
# sources/cloud-native/moby/client/container_create.go

Purpose: creates containers and normalizes selected inputs before sending a daemon create request.

Important APIs/functions: `Client.ContainerCreate`, helper `formatPlatform`, `normalizeCapabilities`, `normalizeCap`, and `allCapabilities`.

Control flow: defaults nil `Config` to an empty config, supports `options.Image` as a shortcut for `Config.Image`, rejects both image fields being set, requires an image, normalizes `HostConfig.CapAdd/CapDrop`, adds `platform` and `name` query values, posts a `container.CreateRequest` to `/containers/create`, closes response, and decodes ID/warnings.

State and integration behavior: no local persistence; daemon creates container state. Mutates the provided `HostConfig` capability slices in-place when non-nil, while copying `Config` when applying the `Image` shortcut to avoid mutating caller config.

Dependencies: container/network API types, Open Containers platform spec, containerd errdefs, shared request helpers, sorting/string normalization.

Risks and test signals: risks include caller-visible HostConfig mutation, capability normalization drift, image shortcut ambiguity, and multi-platform formatting. `container_create_test.go` covers error mapping, image-not-found classification, name query, AutoRemove body behavior, connection errors, and capabilities normalization.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/client/container_create.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/client/container_create_opts.go -->
# sources/cloud-native/moby/client/container_create_opts.go

Purpose: declares option and result types for `ContainerCreate`.

Important APIs/types: `ContainerCreateOptions` with container config, host config, networking config, platform, name, and `Image` shortcut; `ContainerCreateResult` with ID and warnings.

Control flow and dependencies: no runtime control flow. Depends on Moby container/network API types and OCI platform type.

State and integration behavior: no persistence. The type shape is a public API contract consumed by `ContainerCreate`, tests, and downstream callers.

Risks and test signals: field additions are compatibility-sensitive. `container_create_test.go` and compile-time users protect basic shape and encoding expectations.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/client/container_create_opts.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/client/container_create_test.go -->
# sources/cloud-native/moby/client/container_create_test.go

Purpose: tests the container create wrapper’s validation, route construction, body encoding, query handling, and capability normalization.

Important coverage: daemon internal errors, image-not-found mapping, `name` query, AutoRemove in host config, connection failure classification, and canonical capability output for add/drop lists including duplicate and `ALL` handling.

Control flow and dependencies: mock callbacks inspect request path and decode the JSON body. Tests use container API structs and gotest assertions.

State and risks: no persistent state. This suite protects one of the highest-impact wrapper methods because create request encoding affects container lifecycle behavior.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/client/container_create_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/client/container_diff.go -->
# sources/cloud-native/moby/client/container_diff.go

Purpose: fetches filesystem changes for a container.

Important APIs/functions: `Client.ContainerDiff`.

Control flow: validates container id, GETs `/containers/{id}/changes`, closes the response, decodes a JSON array of `container.FilesystemChange`, and returns it in `ContainerDiffResult`.

State and integration behavior: read-only daemon operation with no local persistence. Depends on `ContainerDiffOptions/Result`, shared `get`, JSON decoding, and container API types.

Risks and test signals: risks are invalid-id handling and route drift. `container_diff_test.go` covers daemon errors and successful decode.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/client/container_diff.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/client/container_diff_opts.go -->
# sources/cloud-native/moby/client/container_diff_opts.go

Purpose: declares public option and result types for container filesystem diff.

Important APIs/types: empty extensibility struct `ContainerDiffOptions` and `ContainerDiffResult{Changes []container.FilesystemChange}`.

Control flow and dependencies: no runtime flow; depends on the container API type package.

State and risks: no persistence. Compatibility risk is low but public type shape matters for callers and interface signatures.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/client/container_diff_opts.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/client/container_diff_test.go -->
# sources/cloud-native/moby/client/container_diff_test.go

Purpose: validates `ContainerDiff` error handling and success decoding.

Important coverage: internal server error mapping, invalid container ids through shared validation, expected `GET /containers/container_id/changes`, and JSON decoding of filesystem changes.

Control flow and dependencies: uses `WithMockClient`, `errorMock`, `mockJSONResponse`, and request assertions.

State and risks: no persistent state. The route/method assertion protects compatibility with the daemon changes endpoint.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/client/container_diff_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/client/container_exec.go -->
# sources/cloud-native/moby/client/container_exec.go

Purpose: implements Docker exec lifecycle client methods: create, start, attach, resize validation support, and inspect.

Important APIs/types/functions: `ExecCreateOptions/Result`, `ConsoleSize`, `ExecStartOptions/Result`, `ExecAttachOptions/Result`, `getConsoleSize`, `ExecInspectOptions`, `ExecInspectResult`, `Client.ExecCreate`, `Client.ExecStart`, `Client.ExecAttach`, and `Client.ExecInspect`.

Control flow: `ExecCreate` validates container id, validates console size only when TTY is true, maps options into `container.ExecCreateRequest`, posts to `/containers/{id}/exec`, and decodes the exec ID. `ExecStart` posts `container.ExecStartRequest` to `/exec/{id}/start` and closes the response. `ExecAttach` uses the same start endpoint through `postHijacked` and returns a hijacked connection. `ExecInspect` GETs `/exec/{id}/json`, decodes `container.ExecInspectResponse`, and flattens a nil `ExitCode` pointer to zero.

State and integration behavior: no local persistence; daemon creates and controls exec process state. Hijacked attach transfers connection ownership to the caller.

Dependencies: container API types, containerd errdefs, shared request/hijack helpers, and HTTP headers.

Risks and test signals: risks include allowing console size without TTY, losing nil exit-code semantics, leaked hijack connections, and route confusion between start and attach. `container_exec_test.go` covers errors, connection failures, create/start/attach/inspect routes and console-size validation.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/client/container_exec.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/client/container_exec_test.go -->
# sources/cloud-native/moby/client/container_exec_test.go

Purpose: tests exec create, start, attach-related request construction, console-size validation, and inspect behavior.

Important coverage: daemon and connection errors, invalid container id for create, successful `POST /containers/{id}/exec`, `POST /exec/{id}/start`, terminal size encoding when TTY is enabled, rejection of console size without TTY, and `GET /exec/{id}/json` decoding.

Control flow and dependencies: mock callbacks inspect requests and JSON bodies. Tests depend on container API types and package mock helpers.

State and risks: no persistent state. This suite is important because exec uses both JSON request/response paths and hijacked stream semantics.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/client/container_exec_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/client/container_export.go -->
# sources/cloud-native/moby/client/container_export.go

Purpose: exports a container filesystem as a tar stream.

Important APIs/types/functions: `ContainerExportOptions`, `ContainerExportResult` interface, `Client.ContainerExport`, private `containerExportResult`, and interface assertions.

Control flow: validates container id, GETs `/containers/{id}/export`, and returns `resp.Body` wrapped in a result type. The response body is not closed inside the method because ownership is transferred to the caller.

State and integration behavior: read-only daemon stream with no local persistence. Depends on shared `get`, `newCancelReadCloser` if used similarly in implementation, and `io.ReadCloser` semantics.

Risks and test signals: risks are stream leaks and incorrect not-found/error mapping. `container_export_test.go` covers daemon errors, invalid ids, route/method, body content, and caller close behavior.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/client/container_export.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/client/container_export_test.go -->
# sources/cloud-native/moby/client/container_export_test.go

Purpose: validates `ContainerExport` route, error classification, and returned stream content.

Important coverage: internal errors, invalid empty/whitespace ids, successful `GET /containers/container_id/export`, reading the returned `io.ReadCloser`, and closing it.

Control flow and dependencies: uses mock responses with body content and gotest assertions.

State and risks: no persistent state. The tests protect body ownership semantics for a streaming endpoint.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/client/container_export_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/client/container_inspect.go -->
# sources/cloud-native/moby/client/container_inspect.go

Purpose: inspects a container and returns both typed response and raw daemon JSON.

Important APIs/types/functions: `ContainerInspectOptions{Size bool}`, `ContainerInspectResult{Container container.InspectResponse, Raw json.RawMessage}`, and `Client.ContainerInspect`.

Control flow: validates id, optionally sets `size=1`, GETs `/containers/{id}/json`, and delegates decoding/raw preservation to `decodeWithRaw`.

State and integration behavior: read-only daemon operation. No local persistence. The `Size` option can cause a costly daemon-side filesystem-size calculation.

Dependencies: shared id validation, `get`, `decodeWithRaw`, and container API types.

Risks and test signals: risks include expensive size usage, not-found mapping, and raw JSON preservation. `container_inspect_test.go` covers errors, not found, invalid ids, route/query, and decode success.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/client/container_inspect.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/client/container_inspect_test.go -->
# sources/cloud-native/moby/client/container_inspect_test.go

Purpose: tests `ContainerInspect` error classes and successful decoding.

Important coverage: daemon internal error, not-found classification, invalid empty/whitespace ids, expected `GET /containers/container_id/json`, optional size query behavior, and typed response fields.

Control flow and dependencies: uses mock clients, JSON responses, and gotest assertions.

State and risks: no persistence. The tests protect the common inspect endpoint used by callers before stream demultiplexing and lifecycle operations.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/client/container_inspect_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/client/container_kill.go -->
# sources/cloud-native/moby/client/container_kill.go

Purpose: sends a signal to terminate or stop a container process.

Important APIs/types/functions: `ContainerKillOptions{Signal string}`, `ContainerKillResult`, and `Client.ContainerKill`.

Control flow: validates container id, optionally sets `signal=<Signal>`, posts to `/containers/{id}/kill`, closes the response, and returns an empty result.

State and integration behavior: no local persistence; daemon mutates container process state. Depends on shared `post`, id validation, and query encoding.

Risks and test signals: risks are signal query naming and destructive lifecycle route drift. `container_kill_test.go` covers daemon errors, invalid ids, and successful route/query behavior.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/client/container_kill.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/client/container_kill_test.go -->
# sources/cloud-native/moby/client/container_kill_test.go

Purpose: validates `ContainerKill` error mapping and request construction.

Important coverage: daemon internal errors, invalid empty/whitespace ids, expected `POST /containers/container_id/kill`, and optional signal query.

Control flow and dependencies: mock callbacks inspect requests and return empty responses.

State and risks: no persistent state. The test is important because this is a destructive lifecycle operation.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/client/container_kill_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/client/container_list.go -->
# sources/cloud-native/moby/client/container_list.go

Purpose: lists containers with size/all/limit/filter options.

Important APIs/types/functions: `ContainerListOptions`, including deprecated `Latest`, `Since`, and `Before`; `ContainerListResult{Items []container.Summary}`; and `Client.ContainerList`.

Control flow: builds query parameters for supported fields (`size`, `all`, `limit`) and filter JSON, ignores deprecated fields, GETs `/containers/json`, closes response, and decodes a JSON array into `Items`.

State and integration behavior: read-only daemon operation with no local persistence. Depends on `Filters.updateURLValues`, `strconv`, shared `get`, and container summary API types.

Risks and test signals: risks include accidentally reviving deprecated fields, filter encoding drift, and boolean/int query format changes. `container_list_test.go` asserts route, query values, filters, daemon errors, and decode success.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/client/container_list.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/client/container_list_test.go -->
# sources/cloud-native/moby/client/container_list_test.go

Purpose: tests `ContainerList` query generation and decoding.

Important coverage: internal errors, `GET /containers/json`, `all`, `size`, `limit`, filter query encoding, and JSON response decoding into container summaries.

Control flow and dependencies: table-driven mock transport cases inspect URL query values and return JSON arrays.

State and risks: no persistence. The suite protects Docker CLI-like listing behavior and the shared filter helper.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/client/container_list_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/client/container_logs.go -->
# sources/cloud-native/moby/client/container_logs.go

Purpose: retrieves container logs as a stream with stdout/stderr, time range, follow, tail, timestamps, and details options.

Important APIs/types/functions: `ContainerLogsOptions`, `ContainerLogsResult` interface, `Client.ContainerLogs`, and private `containerLogsResult`.

Control flow: validates container id, maps booleans to `1` query values, parses `Since` and `Until` through the internal timestamp helper, suppresses `tail` for empty or `all`, GETs `/containers/{id}/logs`, and returns a context-cancel-aware read closer. The caller owns closing the stream.

State and integration behavior: read-only daemon stream; no local persistence. Stream format depends on container TTY state and may be raw or stdcopy-multiplexed.

Dependencies: `client/internal/timestamp`, shared `get`, `newCancelReadCloser`, and `io.ReadCloser`.

Risks and test signals: risks include invalid timestamp error wrapping, stream leaks, incorrect default tail handling, and caller demultiplexing assumptions. `container_logs_test.go` and example tests cover errors, invalid ids, timestamp parsing, query cases, stream reading, and close behavior.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/client/container_logs.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/client/container_logs_example_test.go -->
# sources/cloud-native/moby/client/container_logs_example_test.go

Purpose: documents example usage for `Client.ContainerLogs`.

Important APIs/functions: the example calls `ContainerLogs` with output options, defers `Close`, and reads or copies the returned stream.

Control flow and dependencies: it demonstrates caller-owned stream lifecycle and integration with standard `io` helpers.

State and risks: no persistent state. The compile-time example protects public API usability and reinforces the need to close log streams.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/client/container_logs_example_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/client/container_logs_test.go -->
# sources/cloud-native/moby/client/container_logs_test.go

Purpose: validates log retrieval error handling, query encoding, timestamp parsing, and stream behavior.

Important coverage: not-found and internal errors, invalid empty/whitespace ids, invalid `Since`/`Until` parse errors, default suppression of `tail=all`, explicit tail values, stdout/stderr/follow/timestamps/details flags, and reading returned content.

Control flow and dependencies: table-driven tests inspect request queries and use mock bodies for stream reads.

State and risks: no persistence. The suite is high-signal for one of the common long-lived streaming client methods.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/client/container_logs_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/client/container_pause.go -->
# sources/cloud-native/moby/client/container_pause.go

Purpose: pauses a running container.

Important APIs/types/functions: `ContainerPauseOptions`, `ContainerPauseResult`, and `Client.ContainerPause`.

Control flow: validates container id, posts to `/containers/{id}/pause`, closes the response, and returns an empty result.

State and integration behavior: no local persistence; daemon mutates container cgroup/process state. Depends on shared id validation and `post`.

Risks and test signals: destructive lifecycle route must remain stable. `container_pause_test.go` covers daemon errors, invalid ids, and method/path.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/client/container_pause.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/client/container_pause_test.go -->
# sources/cloud-native/moby/client/container_pause_test.go

Purpose: tests `ContainerPause` error mapping and route construction.

Important coverage: daemon internal error, invalid empty/whitespace ids, and successful `POST /containers/container_id/pause`.

Control flow and dependencies: uses mock client helpers and gotest assertions.

State and risks: no persistence. The test protects lifecycle endpoint method/path.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/client/container_pause_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/client/container_prune.go -->
# sources/cloud-native/moby/client/container_prune.go

Purpose: prunes stopped containers using optional filters.

Important APIs/types/functions: `ContainerPruneOptions{Filters Filters}`, `ContainerPruneResult{ContainersDeleted []string, SpaceReclaimed uint64}`, and `Client.ContainerPrune`.

Control flow: encodes filters into query values, posts to `/containers/prune`, closes response, decodes `container.PruneReport`, and maps deleted IDs plus reclaimed bytes into the result.

State and integration behavior: no local persistence; daemon deletes container resources. Depends on shared filter helper, JSON decoding, and container prune API types.

Risks and test signals: destructive operation; filter encoding must be exact. `container_prune_test.go` covers internal errors, route, filter query combinations such as dangling/until/label, and decoded results.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/client/container_prune.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/client/container_prune_test.go -->
# sources/cloud-native/moby/client/container_prune_test.go

Purpose: validates container prune request filtering and result decoding.

Important coverage: daemon internal errors, `POST /containers/prune`, empty and populated `filters` JSON, dangling/until/label cases, and returned deleted IDs/space reclaimed.

Control flow and dependencies: table-driven mock callbacks inspect query values and return JSON prune reports.

State and risks: no persistence. This is high-signal because prune is destructive and filter mistakes can broaden deletion.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/client/container_prune_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/client/container_remove.go -->
# sources/cloud-native/moby/client/container_remove.go

Purpose: removes a container with optional volume, force, and link flags.

Important APIs/types/functions: `ContainerRemoveOptions{RemoveVolumes, RemoveLinks, Force bool}`, `ContainerRemoveResult`, and `Client.ContainerRemove`.

Control flow: validates container id, maps options to query keys `v`, `link`, and `force`, issues `DELETE /containers/{id}`, closes the response, and returns an empty result.

State and integration behavior: no local persistence; daemon deletes container state and optionally volumes/links. Depends on shared request helpers and id validation.

Risks and test signals: destructive route; option query names are terse and easy to regress. `container_remove_test.go` covers internal errors, not found, invalid ids, route, and option query behavior.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/client/container_remove.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/client/container_remove_test.go -->
# sources/cloud-native/moby/client/container_remove_test.go

Purpose: tests `ContainerRemove` error classes and route/query construction.

Important coverage: internal errors, not-found mapping, invalid ids, successful `DELETE /containers/container_id`, and remove options in query values.

Control flow and dependencies: uses mock clients and request assertions.

State and risks: no persistence. The test protects a destructive endpoint and its compatibility query names.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/client/container_remove_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/client/container_rename.go -->
# sources/cloud-native/moby/client/container_rename.go

Purpose: renames a container.

Important APIs/types/functions: `ContainerRenameOptions{Name string}`, `ContainerRenameResult`, and `Client.ContainerRename`.

Control flow: validates container id, sets `name=<Name>` query value, posts to `/containers/{id}/rename`, closes the response, and returns an empty result.

State and integration behavior: no local persistence; daemon mutates container metadata. Depends on shared `post` and id validation.

Risks and test signals: risk is missing name query or path drift. `container_rename_test.go` covers daemon errors, invalid ids, and successful route/query behavior.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/client/container_rename.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/client/container_rename_test.go -->
# sources/cloud-native/moby/client/container_rename_test.go

Purpose: validates `ContainerRename` error handling and request construction.

Important coverage: internal errors, invalid empty/whitespace ids, expected `POST /containers/container_id/rename`, and name query parameter.

Control flow and dependencies: mock transport inspects URL query and method/path.

State and risks: no persistence. The test protects metadata mutation behavior.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/client/container_rename_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/client/container_resize.go -->
# sources/cloud-native/moby/client/container_resize.go

Purpose: resizes container or exec TTY dimensions.

Important APIs/types/functions: `ContainerResizeOptions{Height, Width uint}`, `ContainerResizeResult`, `ExecResizeOptions`, `ExecResizeResult`, `Client.ContainerResize`, and `Client.ExecResize`.

Control flow: each method builds `h` and `w` query values, posts to `/containers/{id}/resize` or `/exec/{id}/resize`, closes the response, and returns an empty result. Container resize validates the container id; exec resize uses the exec id path directly.

State and integration behavior: no local persistence; daemon adjusts terminal state. Depends on shared `post`, query encoding, and id validation.

Risks and test signals: risks are swapped width/height query keys and missing id validation. `container_resize_test.go` covers both endpoints, error mapping, and query values.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/client/container_resize.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/client/container_resize_test.go -->
# sources/cloud-native/moby/client/container_resize_test.go

Purpose: tests resize endpoints for containers and exec sessions.

Important coverage: daemon errors for both APIs, invalid container id, successful `POST /containers/container_id/resize`, successful `POST /exec/exec_id/resize`, and correct `h`/`w` query values.

Control flow and dependencies: shared helper `resizeTransport` inspects requests.

State and risks: no persistence. The suite protects terminal size query compatibility.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/client/container_resize_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/client/container_restart.go -->
# sources/cloud-native/moby/client/container_restart.go

Purpose: restarts a container with optional signal and timeout controls.

Important APIs/types/functions: `ContainerRestartOptions` with signal and timeout-style fields, `ContainerRestartResult`, and `Client.ContainerRestart`.

Control flow: validates container id, maps non-default options to query values, posts to `/containers/{id}/restart`, closes the response, and returns an empty result.

State and integration behavior: no local persistence; daemon stops and starts container process state. Depends on shared lifecycle request helpers.

Risks and test signals: risks are timeout encoding and connection failure classification during lifecycle changes. `container_restart_test.go` covers internal errors, connection errors, route, and query behavior.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/client/container_restart.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/client/container_restart_test.go -->
# sources/cloud-native/moby/client/container_restart_test.go

Purpose: validates `ContainerRestart` error handling, connection failure behavior, and route construction.

Important coverage: internal daemon errors, transport connection errors classified through `IsErrConnectionFailed`, invalid ids, successful `POST /containers/container_id/restart`, and timeout/signal query expectations.

Control flow and dependencies: uses both mock response and failing transport scenarios.

State and risks: no persistence. The test protects lifecycle behavior and shared connection-failure wrapping.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/client/container_restart_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/client/container_start.go -->
# sources/cloud-native/moby/client/container_start.go

Purpose: starts a stopped or created container.

Important APIs/types/functions: `ContainerStartOptions`, `ContainerStartResult`, and `Client.ContainerStart`.

Control flow: validates container id, posts to `/containers/{id}/start`, closes the response, and returns an empty result.

State and integration behavior: no local persistence; daemon mutates container lifecycle state. Depends on shared `post` and id validation.

Risks and test signals: route drift is the main risk. `container_start_test.go` covers internal errors, invalid ids, and successful method/path.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/client/container_start.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/client/container_start_test.go -->
# sources/cloud-native/moby/client/container_start_test.go

Purpose: tests `ContainerStart` error mapping and request route.

Important coverage: daemon internal errors, invalid empty/whitespace ids, and successful `POST /containers/container_id/start`.

Control flow and dependencies: uses mock client helper and request assertions.

State and risks: no persistence. The test protects lifecycle start endpoint compatibility.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/client/container_start_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/client/container_stats.go -->
# sources/cloud-native/moby/client/container_stats.go

Purpose: retrieves container resource statistics as a stream or one-shot response.

Important APIs/types/functions: `ContainerStatsOptions{Stream bool, OneShot bool}`, `ContainerStatsResult` with body and metadata, and `Client.ContainerStats`.

Control flow: validates container id, sets `stream` and `one-shot` query values according to options, GETs `/containers/{id}/stats`, and returns the body stream to the caller with response metadata. The method does not close the body on success.

State and integration behavior: read-only daemon stream; no local persistence. Depends on shared `get`, query encoding, and caller-owned `io.ReadCloser` lifecycle.

Risks and test signals: risks include leaked stats streams and incorrect one-shot semantics. `container_stats_test.go` covers daemon errors, invalid ids, route/query behavior, stream reading, and close behavior.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/client/container_stats.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/client/container_stats_test.go -->
# sources/cloud-native/moby/client/container_stats_test.go

Purpose: validates stats request behavior and returned stream handling.

Important coverage: internal errors, invalid ids, expected `GET /containers/container_id/stats`, `stream` and `one-shot` query values, and reading returned body content.

Control flow and dependencies: mock callbacks inspect query values and provide response bodies.

State and risks: no persistence. The test protects a streaming endpoint where caller close semantics are critical.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/client/container_stats_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/client/container_stop.go -->
# sources/cloud-native/moby/client/container_stop.go

Purpose: stops a running container with optional signal and timeout controls.

Important APIs/types/functions: `ContainerStopOptions`, `ContainerStopResult`, and `Client.ContainerStop`.

Control flow: validates container id, encodes signal/timeout query fields when present, posts to `/containers/{id}/stop`, closes the response, and returns an empty result.

State and integration behavior: no local persistence; daemon changes container lifecycle state. Depends on shared post/id helpers.

Risks and test signals: risks are timeout/signal query compatibility and connection failure mapping. `container_stop_test.go` covers daemon errors, transport connection errors, route, and query behavior.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/client/container_stop.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/client/container_stop_test.go -->
# sources/cloud-native/moby/client/container_stop_test.go

Purpose: tests `ContainerStop` error handling, connection failure classification, and request construction.

Important coverage: internal errors, invalid ids, connection failures through `IsErrConnectionFailed`, successful `POST /containers/container_id/stop`, and timeout/signal query values.

Control flow and dependencies: uses mock and failing transports plus gotest assertions.

State and risks: no persistence. The test protects shutdown behavior and shared network error wrapping.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/client/container_stop_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/client/container_top.go -->
# sources/cloud-native/moby/client/container_top.go

Purpose: returns process information from inside a container.

Important APIs/types/functions: `ContainerTopOptions{Arguments []string}`, `ContainerTopResult` containing process titles/processes, and `Client.ContainerTop`.

Control flow: validates container id, joins/encodes process listing arguments as query data, GETs `/containers/{id}/top`, closes response, and decodes the daemon JSON process list.

State and integration behavior: read-only daemon operation with no local persistence. Depends on shared request helpers and container top response types.

Risks and test signals: risks are argument query formatting and decode shape. `container_top_test.go` covers internal errors, invalid ids, route/query, and successful decoding.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/client/container_top.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/client/container_top_test.go -->
# sources/cloud-native/moby/client/container_top_test.go

Purpose: validates `ContainerTop` error and success behavior.

Important coverage: daemon internal errors, invalid ids, expected `GET /containers/container_id/top`, argument query handling, and response decoding.

Control flow and dependencies: uses mock JSON responses and request assertions.

State and risks: no persistence. The test protects the process-list endpoint’s query shape.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/client/container_top_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/client/container_unpause.go -->
# sources/cloud-native/moby/client/container_unpause.go

Purpose: unpauses a paused container.

Important APIs/types/functions: `ContainerUnpauseOptions`, `ContainerUnpauseResult`, and `Client.ContainerUnpause`.

Control flow: validates container id, posts to `/containers/{id}/unpause`, closes the response, and returns an empty result.

State and integration behavior: no local persistence; daemon mutates lifecycle/cgroup state. Depends on shared post/id helpers.

Risks and test signals: lifecycle route drift is the main risk. `container_unpause_test.go` covers errors, invalid ids, and successful method/path.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/client/container_unpause.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/client/container_unpause_test.go -->
# sources/cloud-native/moby/client/container_unpause_test.go

Purpose: tests `ContainerUnpause` error mapping and request route.

Important coverage: daemon internal errors, invalid empty/whitespace ids, and successful `POST /containers/container_id/unpause`.

Control flow and dependencies: mock client callback asserts method/path.

State and risks: no persistence. The test protects lifecycle endpoint compatibility.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/client/container_unpause_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/client/container_update.go -->
# sources/cloud-native/moby/client/container_update.go

Purpose: updates container resource settings.

Important APIs/types/functions: `ContainerUpdateOptions` wrapping resource update configuration, `ContainerUpdateResult`, and `Client.ContainerUpdate`.

Control flow: validates container id, posts the update config as JSON to `/containers/{id}/update`, closes response, decodes daemon warnings when present, and returns them in the result.

State and integration behavior: no local persistence; daemon mutates container resource configuration. Depends on container API resource types and shared request helpers.

Risks and test signals: risks are body shape drift and warning decode loss. `container_update_test.go` covers internal errors, invalid ids, route, body/decode behavior.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/client/container_update.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/client/container_update_test.go -->
# sources/cloud-native/moby/client/container_update_test.go

Purpose: validates `ContainerUpdate` error handling, route, and response decoding.

Important coverage: daemon internal errors, invalid ids, successful `POST /containers/container_id/update`, and returned warnings.

Control flow and dependencies: mock callbacks assert request and return JSON update responses.

State and risks: no persistence. The test protects resource update endpoint compatibility.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/client/container_update_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/client/container_wait.go -->
# sources/cloud-native/moby/client/container_wait.go

Purpose: waits asynchronously for a container to reach a requested condition and reports either a wait response or an error over channels.

Important APIs/types/functions: `ContainerWaitOptions{Condition container.WaitCondition}`, `ContainerWaitResult{Result <-chan container.WaitResponse, Error <-chan error}`, `containerWaitErrorMsgLimit`, and `Client.ContainerWait`.

Control flow: creates result and buffered error channels, validates container id, encodes optional `condition`, posts to `/containers/{id}/wait`, and returns channels after response headers are received. A goroutine decodes the response body. If JSON syntax fails, it captures up to 2 KiB of proxy/plaintext error body through a tee reader and sends that as an error.

State and integration behavior: no local persistence. The method deliberately returns before the wait completes but after server acknowledgment, enabling caller synchronization with starts/restarts. It closes the response in the goroutine or immediately on request error.

Dependencies: JSON decoding, container wait API type, shared `post`, id validation, and proxy error handling.

Risks and test signals: risks include goroutine leaks if channels are not consumed, proxy-truncated JSON handling, and distinguishing connection errors from API-version negotiation errors. `container_wait_test.go` covers daemon/connection errors, condition query, normal wait result, proxy interruption, long errors capped by limit, and JSON decode behavior.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/client/container_wait.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/client/container_wait_example_test.go -->
# sources/cloud-native/moby/client/container_wait_example_test.go

Purpose: documents using `ContainerWait` with a timeout context.

Important APIs/functions: the example calls `ContainerWait`, then selects between `Result`, `Error`, and context cancellation paths.

Control flow and dependencies: demonstrates channel-based consumption and context timeout integration.

State and risks: no persistent state. The compile-time example protects the public channel result API and shows callers must handle both channels.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/client/container_wait_example_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/client/container_wait_test.go -->
# sources/cloud-native/moby/client/container_wait_test.go

Purpose: validates asynchronous wait behavior, error classification, proxy interruption handling, and result decoding.

Important coverage: daemon internal errors, transport connection errors, route `POST /containers/container_id/wait`, wait condition query, successful wait response, invalid ids through error channel, proxy plaintext errors after headers, and long proxy errors constrained by `containerWaitErrorMsgLimit`.

Control flow and dependencies: tests consume the returned result/error channels, use custom response bodies, and assert error contents/classes.

State and risks: no persistence. This is high-signal for concurrency and streaming decode behavior.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/client/container_wait_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/client/distribution_inspect.go -->
# sources/cloud-native/moby/client/distribution_inspect.go

Purpose: inspects an image distribution reference and returns descriptor/platform information.

Important APIs/types/functions: `DistributionInspectOptions`, `DistributionInspectResult`, and `Client.DistributionInspect`.

Control flow: rejects empty image refs with an image not-found error, builds the distribution inspect path for the image ref, GETs the daemon endpoint, closes response, and decodes the distribution inspect result.

State and integration behavior: read-only daemon/registry-related operation with no local persistence. Depends on shared request helpers and distribution/image API types.

Risks and test signals: risks include reference path escaping and empty-ref error compatibility. `distribution_inspect_test.go` covers empty id behavior; route/decode coverage is lighter in this subset.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/client/distribution_inspect.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/client/distribution_inspect_test.go -->
# sources/cloud-native/moby/client/distribution_inspect_test.go

Purpose: tests validation behavior for `DistributionInspect`.

Important coverage: empty image reference should return a not-found style error rather than issuing a malformed request.

Control flow and dependencies: constructs a client and calls the method with an empty string, using gotest assertions for error class.

State and risks: no persistence. This test protects a narrow validation branch; method/path success coverage is comparatively limited here.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/client/distribution_inspect_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/client/envvars.go -->
# sources/cloud-native/moby/client/envvars.go

Purpose: centralizes Docker-compatible environment variable names used by client options.

Important APIs/constants: `EnvOverrideHost` (`DOCKER_HOST`), `EnvOverrideAPIVersion` (`DOCKER_API_VERSION`), `EnvOverrideCertPath` (`DOCKER_CERT_PATH`), and `EnvTLSVerify` (`DOCKER_TLS_VERIFY`), with package comments explaining behavior.

Control flow and dependencies: no imports or runtime control flow. Constants are consumed by `FromEnv`, `WithHostFromEnv`, `WithAPIVersionFromEnv`, and TLS env setup.

State and integration behavior: no persistence. Integration point is compatibility with Docker CLI and daemon environment conventions.

Risks and test signals: changing names is a breaking compatibility issue. `client_options_test.go` and `client_test.go` indirectly protect these constants through env-based setup.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/client/envvars.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/client/errors.go -->
# sources/cloud-native/moby/client/errors.go

Purpose: defines client-specific error wrappers and version-gating helpers used by endpoint methods and request handling.

Important APIs/types/functions: `errConnectionFailed`, `IsErrConnectionFailed`, `connectionFailed`, `objectNotFoundError`, `requiresVersion`, `httpError`, and `httpErrorFromStatusCode`.

Control flow: connection failures wrap a formatted daemon reachability message so callers can classify with `errors.As`. Object-not-found errors implement a `NotFound` marker. `requiresVersion` triggers client version negotiation when needed and compares the negotiated client version against a required API version. `httpError` wraps lower-level errors and cooperates with `errors.Is`/errdefs via status codes.

State and integration behavior: no persistence. Depends on containerd errdefs/errhttp, standard error wrapping, HTTP status codes, and internal version comparison.

Risks and test signals: risks are losing error classification across wrapping, failing feature gates before negotiation, and mismatched HTTP status mapping. Signals are spread across endpoint tests and request/client tests that assert `cerrdefs.Is*` and `IsErrConnectionFailed`.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/client/errors.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/client/filters.go -->
# sources/cloud-native/moby/client/filters.go

Purpose: provides a small filter builder and URL encoder for Docker API filter maps.

Important APIs/types/functions: `Filters map[string]map[string]bool`, `Add`, `Clone`, and private `updateURLValues`.

Control flow: `Add` lazily creates nested maps and marks each supplied value true. `Clone` deep-copies the nested maps. `updateURLValues` JSON-encodes the filter map and sets it as the `filters` query parameter, including an empty string for nil/empty filters.

State and integration behavior: filters are caller-owned in-memory maps. No persistence. The helper integrates with list/prune APIs for configs, containers, images, networks, tasks, and similar endpoints.

Dependencies and risks: depends on JSON encoding and `url.Values`. Risks include map aliasing without `Clone`, unstable expectations around empty filters, and silently ignored JSON marshal errors if impossible map shape assumptions change. `filters_test.go` covers add, clone isolation, and query encoding.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/client/filters.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/client/filters_test.go -->
# sources/cloud-native/moby/client/filters_test.go

Purpose: tests the `Filters` helper.

Important coverage: adding multiple values to terms, encoding filters into URL values, empty filter behavior, and deep-copy behavior of `Clone`.

Control flow and dependencies: tests build filter maps, compare JSON query strings, mutate clones, and assert original maps are unaffected.

State and risks: no persistence. The tests protect shared query semantics used by many list/prune methods.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/client/filters_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/client/hijack.go -->
# sources/cloud-native/moby/client/hijack.go

Purpose: implements HTTP connection upgrade/hijack support for attach, exec attach, and raw daemon dialing.

Important APIs/types/functions: `postHijacked`, `DialHijack`, `setupHijackConn`, `hijackedConn`, `hijackedConnCloseWriter`, `NewHijackedResponse`, `HijackedResponse`, `CloseWriter`, `HijackedResponse.Close`, `MediaType`, and `CloseWrite`.

Control flow: `postHijacked` JSON-encodes a body, builds a request, and calls `setupHijackConn`. `setupHijackConn` adds `Connection: Upgrade`/`Upgrade`, dials using the client dialer, enables TCP keepalive when possible, writes/reads the HTTP request through a custom round tripper, requires `101 Switching Protocols`, preserves already-buffered bytes, and wraps the connection to preserve `CloseWrite` when supported. `DialHijack` exposes a lower-level request upgrade using caller-provided URL/protocol/meta headers.

State and integration behavior: no persistence, but it creates caller-owned network connections. `HijackedResponse.Close` and `CloseWrite` are lifecycle hooks for callers.

Dependencies: `net`, `bufio`, `net/http`, OpenTelemetry HTTP transport, and client request/header helpers.

Risks and test signals: risks include leaked connections on partial failures, dropping buffered data after HTTP upgrade, losing half-close support, and keepalive behavior on long-lived streams. `hijack_test.go` focuses on TLS close-writer behavior; exec/attach tests indirectly exercise request setup.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/client/hijack.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/client/hijack_test.go -->
# sources/cloud-native/moby/client/hijack_test.go

Purpose: validates close-writer behavior for hijacked TLS connections.

Important coverage: ensures `HijackedResponse.CloseWrite` behaves correctly when the underlying connection does or does not expose a write-half close operation.

Control flow and dependencies: uses in-memory or TLS-like connection test doubles and package hijack types.

State and risks: no persistence. The test protects stream shutdown semantics that affect attach/exec interactive sessions.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/client/hijack_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/client/image_attestations.go -->
# sources/cloud-native/moby/client/image_attestations.go

Purpose: retrieves in-toto attestation statements attached to an image.

Important APIs/functions: `Client.ImageAttestations`.

Control flow: rejects empty image IDs with an image not-found error, requires API version `1.55` via `requiresVersion`, applies functional options, encodes optional platform JSON, repeated predicate `type` filters, and `statement=1`, GETs `/images/{id}/attestations`, closes response, and decodes items.

State and integration behavior: read-only daemon operation; no local persistence. It is feature-gated by negotiated API version and integrates with image attestation API types.

Dependencies and risks: depends on `encodePlatform`, version negotiation, JSON decoding, and option application. Risks are feature gating on older daemons, query encoding of predicate types, and optional statement payload size. No dedicated tests in this subset; compile and request-layer tests are indirect signals.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/client/image_attestations.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/client/image_attestations_opts.go -->
# sources/cloud-native/moby/client/image_attestations_opts.go

Purpose: declares result and functional option types for image attestations.

Important APIs/types/functions: `ImageAttestationsResult`, `ImageAttestationsOption`, `ImageAttestationsWithPlatform`, `ImageAttestationsWithPredicateTypes`, and `ImageAttestationsWithStatement`.

Control flow: option functions mutate private `imageAttestationsOpts` by setting platform, appending predicate type filters, or enabling statement inclusion.

State and integration behavior: no persistence. Options are accumulated per method call and consumed by `ImageAttestations`.

Dependencies and risks: depends on image attestation API types and OCI platform structs. Risks include repeated option accumulation semantics and no validation of empty predicate strings. Coverage is mainly compile-time in this subset.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/client/image_attestations_opts.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/client/image_build.go -->
# sources/cloud-native/moby/client/image_build.go

Purpose: sends build context streams to the daemon and converts build options into Engine API query/header form.

Important APIs/functions: `Client.ImageBuild` and private `imageBuildOptionsToQuery`.

Control flow: `ImageBuild` converts options to query values, JSON-marshals registry auth configs, base64-url encodes them into `X-Registry-Config`, sets `Content-Type: application/x-tar`, posts the raw build context to `/build`, and returns the daemon response body to the caller. `imageBuildOptionsToQuery` maps tags, security options, extra hosts, booleans, remote context, isolation, CPU/memory/shm/cgroup options, Dockerfile/target, JSON-encoded ulimits/build args/labels/cache sources/outputs, session/build IDs, builder version, and exactly one platform; multiple platforms currently return invalid-argument.

State and integration behavior: no local persistence; daemon may create images/build cache. Build context and response are streams owned by caller/daemon. Auth secrets are marshaled into headers, so logging headers is sensitive.

Dependencies: container/network/build/registry API types, base64, JSON, raw request helpers, and containerd errdefs.

Risks and test signals: risks include secret exposure in headers, unsupported multi-platform behavior, query encoding drift, and leaked response body. `image_build_test.go` covers errors, route, headers, selected query parameters, and response body handling.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/client/image_build.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/client/image_build_opts.go -->
# sources/cloud-native/moby/client/image_build_opts.go

Purpose: declares the public build option/result structures.

Important APIs/types: `ImageBuildOptions`, `ImageBuildOutput`, and `ImageBuildResult`.

Control flow and dependencies: no runtime flow. The options type references build, container, registry, and OCI platform types plus `io.Reader` for build context.

State and integration behavior: no persistence. The struct is a large public encoding contract for `ImageBuild`, including auth configs, resource limits, BuildKit session/output settings, and build args where `*string` distinguishes empty value from absent value.

Risks and test signals: compatibility risk is high because fields map directly to daemon API query/header/body behavior. `image_build_test.go` and downstream compile-time use are the main signals.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/client/image_build_opts.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/client/image_build_test.go -->
# sources/cloud-native/moby/client/image_build_test.go

Purpose: validates build request construction, option query encoding, headers, errors, and returned stream behavior.

Important coverage: daemon internal errors, expected `POST /build`, tar content type, registry auth config header, tags and selected query values, JSON-encoded option fields, single-platform behavior, invalid multi-platform rejection, and response body reading.

Control flow and dependencies: tests provide a build context reader, inspect the request in a mock transport, and read the returned body.

State and risks: no persistence. The suite is high-signal because build options have many compatibility-sensitive query encodings and can include credentials.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/client/image_build_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/client/image_history.go -->
# sources/cloud-native/moby/client/image_history.go

Purpose: retrieves image layer history, optionally for a specific platform.

Important APIs/functions: `ImageHistoryWithPlatform` and `Client.ImageHistory`.

Control flow: applies options into `imageHistoryOpts`, rejects duplicate platform options, gates platform use on API version `1.48`, encodes platform JSON with `encodePlatform`, GETs `/images/{id}/history`, closes response, and decodes history items.

State and integration behavior: read-only daemon operation with no local persistence. Depends on version negotiation, platform encoding, and image history API types.

Risks and test signals: risks include feature-gating platform incorrectly, duplicate option handling, and empty image IDs not being explicitly validated in this file. `image_history_test.go` covers daemon errors, route, platform query behavior, and response decoding.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/client/image_history.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/client/image_history_opts.go -->
# sources/cloud-native/moby/client/image_history_opts.go

Purpose: declares functional option plumbing and result type for image history.

Important APIs/types/functions: `ImageHistoryOption`, private `imageHistoryOptionFunc`, `imageHistoryOpts`, `imageHistoryOptions`, and `ImageHistoryResult`.

Control flow: option funcs implement `Apply` to mutate private options. The result holds the decoded history item slice.

State and integration behavior: no persistence. The type structure lets `ImageHistory` evolve with additional options while preserving variadic call syntax.

Dependencies and risks: depends on image API history item types and OCI platform. Risks include duplicate option conflicts and public/private option struct drift.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/client/image_history_opts.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/client/image_history_test.go -->
# sources/cloud-native/moby/client/image_history_test.go

Purpose: tests `ImageHistory` error mapping, route construction, option handling, and decode behavior.

Important coverage: daemon internal errors, successful `GET /images/{id}/history`, decoded history items, and platform option query/version behavior where applicable.

Control flow and dependencies: uses mock JSON responses and request assertions.

State and risks: no persistence. The test protects an image read endpoint and its newer platform option path.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/client/image_history_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/client/image_import.go -->
# sources/cloud-native/moby/client/image_import.go

Purpose: imports an image from a source stream or named source and returns the daemon progress stream.

Important APIs/types/functions: `ImageImportResult` interface, `Client.ImageImport`, and private `imageImportResult`.

Control flow: validates non-empty `ref` with distribution reference parsing, builds query values for `fromSrc`, `repo`, `tag`, `message`, platform, and repeated `changes`, posts the raw source reader to `/images/create`, and returns a context-cancel-aware response body stream to the caller.

State and integration behavior: no local persistence; daemon creates image state. The caller owns source input and returned output stream lifecycle.

Dependencies: distribution reference parser, OCI platform formatting via `formatPlatform`, raw post helper, and `newCancelReadCloser`.

Risks and test signals: risks include invalid reference handling, ambiguous source stream ownership, platform formatting limitations, and leaked progress streams. `image_import_test.go` is outside the requested output set but exists in the package; within this subset, option type docs provide compile-time signal.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/client/image_import.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/client/image_import_opts.go -->
# sources/cloud-native/moby/client/image_import_opts.go

Purpose: declares option structures for image import.

Important APIs/types: `ImageImportSource{Source io.Reader, SourceName string}` and `ImageImportOptions{Tag, Message string, Changes []string, Platform ocispec.Platform}`.

Control flow and dependencies: no runtime flow. Depends on `io` and OCI platform types.

State and integration behavior: no persistence. These types define how callers provide either a source stream or source name plus metadata consumed by `ImageImport`.

Risks and test signals: risks are ambiguous combinations of `Source` and `SourceName` and platform formatting limitations. The production method and package tests enforce behavior.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/client/image_import_opts.go -->
