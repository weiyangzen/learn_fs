# subset-b-000194 research

This grouped report covers Moby daemon HTTP routers, route abstractions, selected server/backend option types, snapshotter mounting, and container lifecycle/statistics helpers. Each source file has its own marked section for reconciliation into source-tree-aligned per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/server/router/container/container_routes_test.go -->
# sources/cloud-native/moby/daemon/server/router/container/container_routes_test.go

## Purpose
This test file validates backward-compatibility helpers used by the container create/update HTTP routes, especially fields whose wire behavior changed across Docker API versions.

## Important APIs, Types, And Functions
The tests exercise `handleMACAddressBC`, `epConfigForNetMode`, `rejectLegacyCapabilities`, and `handleSysctlBC`. They construct `container.HostConfig`, `network.NetworkingConfig`, and endpoint maps, then assert warnings, errors, migrated endpoint settings, and retained/deleted host sysctls.

## Control Flow
Each table-driven test mutates request-like config objects through the compatibility helper under test. MAC tests cover old container-wide MAC migration, endpoint-specific MAC conflicts, no-network conflicts, and API 1.52 rejection. Network-mode tests verify endpoint selection rules before and after API 1.44. Sysctl tests migrate `net.ipv6.conf.eth0.*` settings into `netlabel.EndpointSysctls` for supported API versions and reject unsupported placement for newer ones.

## State And Persistence
No daemon state is persisted. The tests verify in-memory mutation of request structs before those structs are handed to daemon creation logic.

## Dependencies And Integration Points
The tests depend on API container/network types, `netlabel.EndpointSysctls`, `maps.Copy`, and `gotest.tools` assertions. They protect behavior in `container_routes.go`, which is outside this work item but directly adjacent to the listed router files.

## Risks
The main risk is compatibility drift: changing request normalization can silently break old clients, reject valid legacy inputs, or accept fields that newer APIs should reject.

## Test Signals
The file is itself the test signal for container-router compatibility lanes around MAC address, endpoint identity, legacy `Capabilities`, and per-interface sysctls.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/server/router/container/container_routes_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/server/router/container/copy.go -->
# sources/cloud-native/moby/daemon/server/router/container/copy.go

## Purpose
`copy.go` implements the container archive endpoints: stat a path, download a path as a tar stream, and upload/extract a tar stream into a container path.

## Important APIs, Types, And Functions
`setContainerPathStatHeader` JSON-encodes `container.PathStat` and stores it as base64 in `X-Docker-Container-Path-Stat`. Route handlers are `headContainersArchive`, `getContainersArchive`, and `putContainersArchive`. `writeCompressedResponse` negotiates `gzip` or `deflate` with `gddo/httputil.NegotiateContentEncoding`.

## Control Flow
Handlers parse archive form values through `httputils.ArchiveFormValues`, call the backend (`ContainerStatPath`, `ContainerArchivePath`, or `ContainerExtractToDir`), set metadata headers, then stream tar data. Upload converts the legacy `noOverwriteDirNonDir` flag into `allowOverwriteDirWithFile` and passes `copyUIDGID` plus the request body to the backend.

## State And Persistence
The router itself holds no durable state. Persistent effects happen only through the backend: archive extraction can modify the container filesystem, ownership, and overwrite behavior.

## Dependencies And Integration Points
This file integrates the container router with backend copy/archive operations, HTTP content negotiation, compression writers, `io.Copy`, and API `PathStat`.

## Risks
Header encoding must remain compatible because clients decode it directly. Streaming responses can only return structured errors before data is flushed. Upload semantics around directory/file overwrite are inverted for historical compatibility, which is easy to regress.

## Test Signals
No direct tests in this file; behavior is usually covered by API/integration tests for `GET/HEAD/PUT /containers/{id}/archive`.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/server/router/container/copy.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/server/router/container/exec.go -->
# sources/cloud-native/moby/daemon/server/router/container/exec.go

## Purpose
`exec.go` exposes HTTP endpoints for inspecting exec instances, creating an exec command in a container, starting it with optional stream hijacking, and resizing its TTY.

## Important APIs, Types, And Functions
Handlers are `getExecByID`, `postContainerExecCreate`, `postContainerExecStart`, and `postContainerExecResize`. `execCommandError` marks an empty command as invalid. Streaming uses `httputils.HijackConnection`, `stdcopymux.NewStdWriter`, and `stdcopy` stream IDs.

## Control Flow
Create parses JSON into `container.ExecCreateRequest`, rejects empty `Cmd`, strips `ConsoleSize` before API 1.42, and calls `ContainerExecCreate`. Start validates the exec ID with `ExecExists`, strips unsupported or non-TTY console sizing, hijacks the connection unless detached, writes an HTTP upgrade or raw stream response prelude, multiplexes stdout/stderr when no TTY is used, and calls `ContainerExecStart` with a background context. Resize parses `h` and `w` query values and delegates to `ContainerExecResize`.

## State And Persistence
Exec instances are registered and run by the backend/container state machinery. The router only wires streams and request options; it does not persist exec state.

## Dependencies And Integration Points
This file integrates container HTTP routes with backend exec lifecycle methods, API-version logic, hijacked HTTP connections, raw and multiplexed stream media types, and daemon logging.

## Risks
Hijack handling is sensitive: headers are manually written after hijack, errors after stream start are written to stdout, and `context.Background()` intentionally decouples exec execution from the HTTP request. Media type selection changed in API 1.42 and must stay compatible.

## Test Signals
Coverage is mostly integration-level through Docker exec API tests, including detached mode, TTY/non-TTY streaming, resize validation, and old API console-size behavior.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/server/router/container/exec.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/server/router/container/inspect.go -->
# sources/cloud-native/moby/daemon/server/router/container/inspect.go

## Purpose
`inspect.go` serializes container inspection responses while preserving old Docker API response shapes.

## Important APIs, Types, And Functions
`getContainersByName` calls `ContainerInspect` with size options, mutates response fields for older API versions, and uses `compat.Wrap` to inject removed legacy fields.

## Control Flow
The handler parses query fields, obtains inspection data plus a desired MAC address from the backend, then applies version gates. Before API 1.45 it appends short container ID and hostname aliases to user-defined network endpoints. Before API 1.48 it hides `ImageManifestDescriptor`. Before API 1.52 it injects bridge endpoint data into top-level `NetworkSettings`, restores legacy `Config.MacAddress`, and maps snapshotter `Storage.RootFS.Snapshot.Name` back into `GraphDriver`.

## State And Persistence
Only the response object is mutated. The daemon's stored container configuration is not persisted by this handler.

## Dependencies And Integration Points
The file depends on API container/storage types, `compat`, version helpers, `stringid`, `sliceutil`, and backend inspect options. It is part of the container router's GET `/containers/{name}/json` path.

## Risks
Because the code mutates the inspect object before writing it, accidental reuse of backend-owned objects could leak legacy-only fields. Version gates are dense and tied to public API compatibility.

## Test Signals
The neighboring container route compatibility tests cover related MAC migration logic; integration tests typically validate inspect response compatibility across API versions.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/server/router/container/inspect.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/server/router/container/notify_linux.go -->
# sources/cloud-native/moby/daemon/server/router/container/notify_linux.go

## Purpose
`notify_linux.go` provides Linux-specific connection-close notification support for hijacked container streams.

## Important APIs, Types, And Functions
`notifyClosed` accepts a `net.Conn` and callback, extracts a raw fd through `syscall.Conn`, creates an epoll fd through `unix_noeintr.EpollCreate`, registers `EPOLLHUP`, waits indefinitely, and calls `notify`.

## Control Flow
If the connection does not expose `SyscallConn`, or epoll setup/registration/wait fails, the function logs and returns. On success it blocks in `EpollWait` until hangup and then invokes the callback from inside `RawConn.Control`.

## State And Persistence
No persistent state is written. The function owns a temporary epoll fd and observes kernel state for a single connection.

## Dependencies And Integration Points
It depends on Linux epoll via `golang.org/x/sys/unix`, Moby's EINTR-safe unix wrappers, containerd logging, and callers in container attach/stream paths that need to detect a disconnected client.

## Risks
Blocking inside `RawConn.Control` is delicate because it pins raw fd access while waiting. Missing `EPOLLERR`/`EPOLLRDHUP` could miss some closure modes, and callback execution must be safe from the waiter goroutine.

## Test Signals
No direct unit tests are present; behavior is exercised indirectly by attach/exec stream disconnect integration tests on Linux.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/server/router/container/notify_linux.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/server/router/container/notify_unsupported.go -->
# sources/cloud-native/moby/daemon/server/router/container/notify_unsupported.go

## Purpose
`notify_unsupported.go` is the non-Linux stub for connection-close notifications.

## Important APIs, Types, And Functions
It defines `notifyClosed(ctx context.Context, conn net.Conn, notify func())` as a no-op under the `!linux` build tag.

## Control Flow
There is no runtime behavior. Calls compile on unsupported platforms but do not install a close watcher.

## State And Persistence
No state is read or written.

## Dependencies And Integration Points
The file keeps container stream code portable by satisfying the same function symbol as the Linux implementation.

## Risks
Non-Linux platforms do not get the Linux close-notification behavior, so callers must not rely on this function as the only cleanup path.

## Test Signals
Compilation on non-Linux platforms is the main signal.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/server/router/container/notify_unsupported.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/server/router/debug/debug.go -->
# sources/cloud-native/moby/daemon/server/router/debug/debug.go

## Purpose
`debug.go` registers daemon debug endpoints for expvar and pprof under the standard router abstraction.

## Important APIs, Types, And Functions
`NewRouter` constructs `debugRouter`, `initRoutes` registers `/debug/vars`, `/debug/pprof/`, specific pprof handlers, and `/debug/pprof/{name}`. `frameworkAdaptHandler` and `frameworkAdaptHandlerFunc` adapt standard `http.Handler` values into `httputils.APIFunc`.

## Control Flow
Route registration is static. Each adapted handler ignores router variables, invokes the standard library handler, and returns nil so server middleware/error conversion does not interfere.

## State And Persistence
No state is persisted. The endpoints expose process-global expvar and pprof state from the daemon process.

## Dependencies And Integration Points
Depends on `expvar`, `net/http/pprof`, `httputils`, and the router package. The server registers this router like any other API router.

## Risks
Debug endpoints expose sensitive runtime/process information and should only be registered in daemon configurations that intend to expose them. Handler adaptation bypasses structured error responses.

## Test Signals
No local tests; behavior is covered by route registration and standard library pprof functionality.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/server/router/debug/debug.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/server/router/debug/debug_routes.go -->
# sources/cloud-native/moby/daemon/server/router/debug/debug_routes.go

## Purpose
`debug_routes.go` contains the variable pprof profile route handler.

## Important APIs, Types, And Functions
`handlePprof` reads `vars["name"]`, obtains `pprof.Handler(name)`, and serves it through the current response/request.

## Control Flow
The server mux captures the `{name}` path segment and passes it to this handler. The standard pprof handler performs the actual profile lookup and response.

## State And Persistence
No state is changed; the handler reads runtime profiling state from the Go process.

## Dependencies And Integration Points
It integrates gorilla/mux route variables with `net/http/pprof`.

## Risks
Unknown profile names and handler-specific query parameters are delegated to the standard library. Access control must be handled outside this file.

## Test Signals
No direct tests.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/server/router/debug/debug_routes.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/server/router/distribution/backend.go -->
# sources/cloud-native/moby/daemon/server/router/distribution/backend.go

## Purpose
`backend.go` defines the narrow backend contract required by the distribution inspection router.

## Important APIs, Types, And Functions
`Backend` exposes `GetRepositories(context.Context, reference.Named, *registry.AuthConfig) ([]distribution.Repository, error)`.

## Control Flow
The route code parses and validates image references, decodes auth headers, and then uses this interface to obtain one or more registry repositories/endpoints to inspect.

## State And Persistence
The interface itself has no state. Implementations may open registry connections and consult daemon registry configuration but do not persist state through this contract.

## Dependencies And Integration Points
It depends on Docker distribution repository interfaces, distribution references, and API registry auth config.

## Risks
The interface hides endpoint ordering and mirror behavior; route behavior depends on implementations returning repositories in the correct fallback order.

## Test Signals
Compilation of the distribution router against daemon registry backends is the primary signal.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/server/router/distribution/backend.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/server/router/distribution/distribution.go -->
# sources/cloud-native/moby/daemon/server/router/distribution/distribution.go

## Purpose
`distribution.go` defines the distribution router object and registers the image-distribution inspection endpoint.

## Important APIs, Types, And Functions
`distributionRouter` stores `backend` and `routes`. `NewRouter`, `Routes`, and `initRoutes` implement the common router pattern.

## Control Flow
`initRoutes` installs `GET /distribution/{name:.*}/json` with minimum API version 1.30. The route is later registered both versioned and unversioned by the server.

## State And Persistence
No persistent state is managed; the router stores route metadata and a backend reference.

## Dependencies And Integration Points
Integrates the distribution route handler with the shared `router` package and `WithMinimumAPIVersion`.

## Risks
The `{name:.*}` matcher intentionally captures slashes for registry/image names. Changing it would break image references.

## Test Signals
No direct tests; route availability is covered by API integration behavior.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/server/router/distribution/distribution.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/server/router/distribution/distribution_routes.go -->
# sources/cloud-native/moby/daemon/server/router/distribution/distribution_routes.go

## Purpose
`distribution_routes.go` implements `GET /distribution/{name}/json`, returning manifest descriptor and platform information from registries.

## Important APIs, Types, And Functions
`getDistributionInfo` parses the reference, decodes `X-Registry-Auth`, asks the backend for repositories, and tries each repository. `fetchManifest` resolves tags to descriptors, fetches manifests, rejects schema1, and extracts platform data from manifest lists or schema2 configs.

## Control Flow
The handler normalizes the image reference and rejects full image IDs or unparseable references as invalid. It iterates repositories in backend order, preserving the last manifest error for fallback. `fetchManifest` gets tag descriptors when the reference is not canonical, obtains the manifest service, fetches by digest, corrects media type/size from payload data, and fills platform arrays.

## State And Persistence
No local state is persisted. It performs remote registry reads only.

## Dependencies And Integration Points
Depends on Docker distribution repositories, manifest list/schema2 packages, Moby distribution media-type helpers, registry auth decoding, `errdefs`, and OCI platform descriptors.

## Risks
Registry endpoints can return inconsistent descriptors or media types, so the code corrects descriptor fields from payloads. It ignores invalid auth headers for compatibility. Schema1 rejection and tag-versus-digest handling are important compatibility/security boundaries.

## Test Signals
No direct tests in this file; registry/distribution integration tests should cover tag lookup, digest lookup, auth, manifest list platforms, schema2 config platform extraction, and schema1 rejection.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/server/router/distribution/distribution_routes.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/server/router/experimental.go -->
# sources/cloud-native/moby/daemon/server/router/experimental.go

## Purpose
`experimental.go` wraps routes so they can be disabled unless the daemon is running with experimental features enabled.

## Important APIs, Types, And Functions
`ExperimentalRoute` extends `Route` with `Enable` and `Disable`. `experimentalRoute` stores the wrapped local route and the currently active handler. `Experimental` builds a disabled wrapper. `notImplementedError` marks disabled access as not implemented.

## Control Flow
When disabled, `Handler` returns `experimentalHandler`, which returns `notImplementedError`. `Enable` swaps the handler to the original route handler; `Disable` restores the disabled handler. Method and path always pass through to the wrapped route.

## State And Persistence
The wrapper stores mutable in-memory handler state. No persistent daemon state is written.

## Dependencies And Integration Points
It integrates with the shared router interfaces and daemon feature toggling code that can discover `ExperimentalRoute` values and call `Enable` or `Disable`.

## Risks
Because enablement mutates handler pointers, route setup must happen before concurrent request serving or use external synchronization. Error classification relies on the `NotImplemented` marker method.

## Test Signals
No direct tests; behavior is validated by routes that are registered as experimental and by HTTP error classification.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/server/router/experimental.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/server/router/grpc/backend.go -->
# sources/cloud-native/moby/daemon/server/router/grpc/backend.go

## Purpose
`backend.go` defines the registration contract for services exposed through the deprecated `/grpc` upgrade endpoint.

## Important APIs, Types, And Functions
`Backend` has one method, `RegisterGRPC(*grpc.Server)`, allowing each service provider to register its gRPC service definitions.

## Control Flow
The gRPC router constructs a server and calls this method for each backend during router initialization.

## State And Persistence
The interface itself has no state. Registration mutates the in-memory `grpc.Server`.

## Dependencies And Integration Points
Depends only on `google.golang.org/grpc`.

## Risks
Registration order and duplicate service registration are implementation concerns hidden behind this interface.

## Test Signals
Compilation and endpoint integration tests validate that backends register cleanly.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/server/router/grpc/backend.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/server/router/grpc/grpc.go -->
# sources/cloud-native/moby/daemon/server/router/grpc/grpc.go

## Purpose
`grpc.go` builds the deprecated `/grpc` router, wrapping a gRPC server behind an h2c HTTP upgrade endpoint with tracing and buildkit-compatible error handling.

## Important APIs, Types, And Functions
`grpcRouter` stores routes, a `grpc.Server`, and an `http2.Server`. `NewRouter` configures tracing stats handlers, unary/stream error interceptors, send/receive limits, registers supplied backends, and registers `/grpc`. `unaryInterceptor` logs failed unary calls except trace export calls.

## Control Flow
Router construction creates an OpenTelemetry tracer provider, configures gRPC server options, lets each backend register services, then exposes one POST route. Unary calls run through a custom interceptor and BuildKit gRPC error interceptor chain.

## State And Persistence
The gRPC server and h2 server are in-memory service dispatch state. No durable state is managed here.

## Dependencies And Integration Points
Integrates containerd defaults, BuildKit `grpcerrors`, OpenTelemetry gRPC instrumentation, daemon `otelutil`, `http2`, and the shared router package.

## Risks
The endpoint is deprecated; new clients should use direct HTTP/2/h2c. Tracing export is intentionally excluded from tracing to avoid recursive trace loops. Debug stack formatting to stderr only happens at debug log level.

## Test Signals
No direct tests; behavior depends on gRPC integration tests and any BuildKit/session services registered through this router.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/server/router/grpc/grpc.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/server/router/grpc/grpc_routes.go -->
# sources/cloud-native/moby/daemon/server/router/grpc/grpc_routes.go

## Purpose
`grpc_routes.go` implements the HTTP upgrade path that serves the gRPC server over a hijacked h2c connection.

## Important APIs, Types, And Functions
`serveGRPC` requires `http.Hijacker`, checks `Upgrade: h2c`, hijacks the connection, writes a `101 Switching Protocols` response, and calls `http2.Server.ServeConn` with the gRPC server as handler.

## Control Flow
Requests without upgrade or with any protocol other than h2c fail before hijack. After hijack, the function writes the upgrade response directly to the raw connection and transfers control to the HTTP/2 server.

## State And Persistence
No persistent state is written. The connection is removed from normal HTTP server management after hijack.

## Dependencies And Integration Points
Depends on `net/http`, `http2`, and the `grpcRouter` server fields. It is the implementation for POST `/grpc`.

## Risks
After hijack, normal HTTP error handling no longer applies. The code manually writes response bytes and has a TODO about serving a connection after it has already been written to.

## Test Signals
Integration tests for deprecated `/grpc` clients are the primary signal.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/server/router/grpc/grpc_routes.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/server/router/image/backend.go -->
# sources/cloud-native/moby/daemon/server/router/image/backend.go

## Purpose
`backend.go` defines the image router's backend interfaces for image CRUD, import/export, registry push/pull, attestations, prune, and search.

## Important APIs, Types, And Functions
`Backend` embeds `imageBackend`, `importExportBackend`, and `registryBackend`. Methods include `ImageDelete`, `ImageHistory`, `Images`, `GetImage`, `ImageInspect`, `ImageAttestations`, `TagImage`, `ImagePrune`, `LoadImage`, `ImportImage`, `ExportImage`, `PullImage`, and `PushImage`. `Searcher` exposes registry search.

## Control Flow
Router handlers parse HTTP inputs into option structs from `imagebackend` and call these methods. Streaming operations pass writer streams into backend methods for JSON progress.

## State And Persistence
The interface abstracts persistent image store and registry side effects: pulls, imports, loads, tags, deletes, pushes, and prune operations.

## Dependencies And Integration Points
Uses API image/registry types, daemon filters, internal image IDs, distribution references, OCI platforms, and `imagebackend` option structs.

## Risks
Because this is a broad interface, route changes can require daemon image service changes. Platform, manifest, and identity options have API-version gates in the router but must be honored by backends.

## Test Signals
Compilation against daemon image service plus image API integration tests validate the contract.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/server/router/image/backend.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/server/router/image/image.go -->
# sources/cloud-native/moby/daemon/server/router/image/image.go

## Purpose
`image.go` defines the image router and registers all image HTTP API routes.

## Important APIs, Types, And Functions
`imageRouter` stores a `Backend`, `Searcher`, and route list. `NewRouter`, `Routes`, and `initRoutes` implement the common router pattern.

## Control Flow
`initRoutes` registers list, search, export, history, inspect, attestations, load, create/pull/import, push, tag, prune, and delete endpoints. Attestations require API 1.55 and prune requires API 1.25.

## State And Persistence
The router stores only backend references and route metadata. Image state changes happen in backend handlers.

## Dependencies And Integration Points
Integrates image handlers with the shared router package and API-version wrappers.

## Risks
The wildcard `{name:.*}` matcher is required for repository references with slashes. Route ordering must avoid conflicts among `/images/{name}/...`, `/images/json`, and `/images/search`.

## Test Signals
No direct tests; route behavior is covered through image API tests.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/server/router/image/image.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/server/router/image/image_list_response_test.go -->
# sources/cloud-native/moby/daemon/server/router/image/image_list_response_test.go

## Purpose
This test verifies legacy image-list JSON compatibility for the `VirtualSize` field.

## Important APIs, Types, And Functions
`TestImageListVirtualSize` builds `image.Summary` values, wraps them with `compat.Wrap` and `compat.WithExtraFields`, marshals to JSON, and asserts `VirtualSize == Size` for old API behavior.

## Control Flow
The test has two subtests: one validates the wrapped pre-1.44 response includes `VirtualSize`; the other validates direct marshaling for newer APIs omits it.

## State And Persistence
No state is persisted. The test validates response serialization only.

## Dependencies And Integration Points
It protects the wrapping path in `getImagesJSON` and depends on API image types plus daemon `compat`.

## Risks
Removing or renaming legacy fields can break old clients that still expect `VirtualSize`.

## Test Signals
The test directly asserts the JSON-level wire contract rather than only Go struct fields.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/server/router/image/image_list_response_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/server/router/image/image_routes.go -->
# sources/cloud-native/moby/daemon/server/router/image/image_routes.go

## Purpose
`image_routes.go` implements the image API HTTP handlers, including pull/import, push, save/load, delete, inspect, list, history, tag, search, prune, and attestations.

## Important APIs, Types, And Functions
Key handlers include `postImagesCreate`, `postImagesPush`, `getImagesGet`, `postImagesLoad`, `deleteImages`, `getImagesByName`, `getImagesJSON`, `getImagesHistory`, `postImagesTag`, `getImagesSearch`, `postImagesPrune`, and `getImageAttestations`. Helper types include `missingImageError`; `validateRepoName` rejects `scratch`.

## Control Flow
Handlers parse forms/JSON, decode platforms based on API version, decode registry auth permissively, convert references with distribution/reference helpers, and delegate to backend methods. Streaming handlers use `ioutils.WriteFlusher` and write JSON progress/errors once output has begun. Inspect/list handlers perform extensive API-version shaping: legacy `VirtualSize`, descriptor removal, container count compatibility, legacy config fields, graph-driver restoration, and manifest/identity constraints.

## State And Persistence
Persistent state changes occur in the backend: pulling, importing, loading, deleting, tagging, pruning, and pushing images. The router mutates only request option structs and response payloads.

## Dependencies And Integration Points
Integrates authconfig, registry search, remote context downloads, stream formatters, filters, platform parsing, digest/tag references, `imagebackend` options, and API compatibility wrappers.

## Risks
Most risks are wire-compatibility and streaming-error related. Platform support is version-gated across multiple endpoints, `identity` requires `manifests`, `manifests` conflicts with `platform`, invalid auth is intentionally ignored, and errors after progress flush must be emitted as stream entries rather than normal HTTP errors.

## Test Signals
Local tests cover `VirtualSize` and legacy inspect config fields. Broader image API integration tests should cover reference parsing, reserved names, platform gates, streaming pull/push/load/save, and attestations.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/server/router/image/image_routes.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/server/router/image/inspect_response.go -->
# sources/cloud-native/moby/daemon/server/router/image/inspect_response.go

## Purpose
`inspect_response.go` centralizes legacy image config fields that must be injected into inspect responses for older API versions.

## Important APIs, Types, And Functions
`legacyConfigFields` maps version buckets (`v1.49` and `v1.50-v1.51`) to field/default-value maps used by `compat.Wrap`.

## Control Flow
`getImagesByName` selects a map based on API version and adds it as extra `Config` fields. Actual configured fields override legacy defaults during wrapping/JSON serialization.

## State And Persistence
No state is persisted; the maps are package-level constants for response shaping.

## Dependencies And Integration Points
Used by image inspect response compatibility code and tested by `inspect_response_test.go`.

## Risks
Wrong default values or version bucket selection can change JSON wire shape and break clients expecting pre-omitempty fields.

## Test Signals
The inspect response test serializes representative responses and verifies exact JSON for each legacy bucket.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/server/router/image/inspect_response.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/server/router/image/inspect_response_test.go -->
# sources/cloud-native/moby/daemon/server/router/image/inspect_response_test.go

## Purpose
This test validates image inspect response compatibility for legacy `Config` fields.

## Important APIs, Types, And Functions
`TestInspectResponse` builds `image.InspectResponse` values with optional OCI image config, wraps them with `compat.Wrap`, and asserts the serialized `Config` JSON.

## Control Flow
Cases cover nil config, no legacy config, API `< v1.50`, and API `v1.50-v1.51`. The test verifies real configured fields override defaults while missing legacy fields are injected.

## State And Persistence
No state is persisted. The test verifies JSON serialization behavior.

## Dependencies And Integration Points
Depends on Docker image-spec config types, OCI image config, API image types, and daemon `compat`. It protects `legacyConfigFields` and `getImagesByName`.

## Risks
Changing `omitempty` compatibility can break clients that deserialize old fields unconditionally.

## Test Signals
Exact JSON comparison provides strong signal for legacy field presence and ordering-insensitive object semantics through raw JSON extraction.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/server/router/image/inspect_response_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/server/router/local.go -->
# sources/cloud-native/moby/daemon/server/router/local.go

## Purpose
`local.go` implements the concrete route type and constructors used by all daemon HTTP routers.

## Important APIs, Types, And Functions
`RouteWrapper` decorates routes. `localRoute` implements `Route` with method/path/handler. Constructors include `NewRoute`, method-specific helpers (`NewGetRoute`, `NewPostRoute`, `NewPutRoute`, `NewDeleteRoute`, `NewOptionsRoute`, `NewHeadRoute`), and `WithMinimumAPIVersion`. `versionError` marks invalid parameters.

## Control Flow
Constructors create a `localRoute`, then apply wrappers in order. `WithMinimumAPIVersion` returns a route whose handler checks `httputils.VersionFromContext(ctx)` and rejects versions lower than the minimum before invoking the original handler.

## State And Persistence
Routes are immutable values except where wrappers provide mutable implementations such as experimental routes. No persistent state is written.

## Dependencies And Integration Points
Used by every router in the daemon server. Integrates version comparison helpers, `httputils.APIFunc`, and HTTP method constants.

## Risks
Minimum-version failures intentionally return invalid-parameter style errors rather than 404 to avoid conflicting with endpoint business semantics. Wrapper order matters when combining experimental/version wrappers.

## Test Signals
Route behavior is indirectly covered by server route registration and API-version integration tests.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/server/router/local.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/server/router/network/backend.go -->
# sources/cloud-native/moby/daemon/server/router/network/backend.go

## Purpose
`backend.go` defines local and swarm-cluster network backend contracts used by the network router.

## Important APIs, Types, And Functions
`Backend` covers local network list/inspect summaries, create, connect, disconnect, delete, and prune. `ClusterBackend` covers swarm network list/summaries, single get, lookup by name, create, and remove.

## Control Flow
Route handlers call both interfaces to merge local and swarm networks, resolve ambiguous names/IDs, and route create/delete operations to local or cluster implementations.

## State And Persistence
Implementations persist network definitions, endpoints, and pruning effects. The interface file holds no state.

## Dependencies And Integration Points
Depends on API network types, daemon filters, internal daemon network filters, server backend list config, and network backend connect/disconnect request types.

## Risks
The split backend contract makes ambiguity handling a router responsibility. Local and swarm data can race or duplicate by name/ID.

## Test Signals
Compilation plus network API tests validate that local and cluster implementations satisfy the contract.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/server/router/network/backend.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/server/router/network/network.go -->
# sources/cloud-native/moby/daemon/server/router/network/network.go

## Purpose
`network.go` defines the network router and registers Docker network API routes.

## Important APIs, Types, And Functions
`networkRouter` stores local and cluster backends plus route metadata. `NewRouter`, `Routes`, and `initRoutes` implement the common router pattern.

## Control Flow
Routes include list, inspect, create, connect, disconnect, prune, and delete. Prune is gated to API 1.25+.

## State And Persistence
The router stores only backend references. Network persistence is handled by backends.

## Dependencies And Integration Points
Integrates network route handlers with the shared router constructors and version wrappers.

## Risks
Path patterns use `{id:.+}` and `{id:.*}` to capture IDs/names that may include special characters while preserving empty-match behavior for some endpoints.

## Test Signals
No direct tests in this file; network API route tests exercise registrations.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/server/router/network/network.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/server/router/network/network_routes.go -->
# sources/cloud-native/moby/daemon/server/router/network/network_routes.go

## Purpose
`network_routes.go` implements network API handlers for list, inspect, create, connect, disconnect, delete, and prune across local and swarm scopes.

## Important APIs, Types, And Functions
Handlers include `getNetworksList`, `getNetwork`, `postNetworkCreate`, `postNetworkConnect`, `postNetworkDisconnect`, `deleteNetwork`, and `postNetworkPrune`. Helpers/errors include `invalidRequestError`, `ambiguousResultsError`, and `findUniqueNetwork`.

## Control Flow
List parses filters and merges swarm plus local results, using old `network.Inspect` responses before API 1.28 and `network.Summary` afterward. Inspect searches local full ID, full name, partial ID, then cluster network data and merges status for API 1.52+. Create rejects swarm duplicate names, strips `EnableIPv4` before API 1.48, validates locally, and redirects swarm-scoped creation to the cluster backend on `ManagerRedirectError`. Connect strips endpoint MAC before API 1.54. Delete resolves a unique network then dispatches to local or swarm removal.

## State And Persistence
Persistent changes are delegated to backends: network creation/removal, container endpoint attach/detach, and prune. The router only resolves targets and normalizes options.

## Dependencies And Integration Points
Depends on daemon filters, libnetwork errors/scope, local backend list config, cluster backend methods, API network types, and API-version helpers.

## Risks
Ambiguous names and partial IDs across local and swarm scopes are high-risk. Ignoring cluster errors in some list paths can hide manager problems. Version-gated fields such as `EnableIPv4`, status, and endpoint MAC must stay aligned with API docs.

## Test Signals
Network route behavior is mainly integration-tested; local unit coverage is absent in this file.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/server/router/network/network_routes.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/server/router/plugin/backend.go -->
# sources/cloud-native/moby/daemon/server/router/plugin/backend.go

## Purpose
`backend.go` defines the plugin router backend contract for plugin lifecycle, registry operations, and local plugin creation.

## Important APIs, Types, And Functions
`Backend` includes `Disable`, `Enable`, `List`, `Inspect`, `Remove`, `Set`, `Privileges`, `Pull`, `Push`, `Upgrade`, and `CreateFromContext`.

## Control Flow
Route handlers parse HTTP fields, decode auth/meta headers, then delegate plugin state changes and registry streaming operations to this interface.

## State And Persistence
Implementations persist plugin installation/configuration state and may perform registry push/pull/upgrade side effects.

## Dependencies And Integration Points
Depends on distribution references, API plugin/registry types, daemon filters, plugin creation options, and server backend option structs.

## Risks
The interface mixes local lifecycle and remote registry operations; streaming operations must be careful about progress output and late errors.

## Test Signals
Compile-time satisfaction by plugin manager implementations and plugin API integration tests validate the contract.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/server/router/plugin/backend.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/server/router/plugin/plugin.go -->
# sources/cloud-native/moby/daemon/server/router/plugin/plugin.go

## Purpose
`plugin.go` defines the plugin router and registers plugin HTTP API endpoints.

## Important APIs, Types, And Functions
`pluginRouter` stores a backend and route list. `NewRouter`, `Routes`, and `initRoutes` implement route setup.

## Control Flow
Routes include list, inspect, privileges, remove, enable, disable, pull, push, upgrade, set, and create. Upgrade is gated at API 1.26.

## State And Persistence
The router has no persistent state; plugin state changes occur in backend calls.

## Dependencies And Integration Points
Uses the shared router package and route constructors.

## Risks
The wildcard `{name:.*}` route patterns are necessary for plugin names containing slashes/tags but can overlap if new routes are added carelessly.

## Test Signals
Plugin API integration tests validate route behavior.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/server/router/plugin/plugin.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/server/router/plugin/plugin_routes.go -->
# sources/cloud-native/moby/daemon/server/router/plugin/plugin_routes.go

## Purpose
`plugin_routes.go` implements plugin API handlers for privilege discovery, pull, upgrade, create, enable/disable, remove, push, set, list, and inspect.

## Important APIs, Types, And Functions
Helpers include `parseHeaders`, `parseRemoteRef`, and `getName`. Handlers include `getPrivileges`, `upgradePlugin`, `pullPlugin`, `createPlugin`, `enablePlugin`, `disablePlugin`, `removePlugin`, `pushPlugin`, `setPlugin`, `listPlugins`, and `inspectPlugin`.

## Control Flow
Registry operations parse `remote`, preserve meta headers, ignore invalid auth headers for compatibility, normalize digest/tag references, derive local plugin names, and stream JSON progress through `WriteFlusher`. Lifecycle operations parse query/body values and delegate to backend option structs. `enablePlugin` parses timeout as an integer and marks bad values invalid.

## State And Persistence
Backend calls persist plugin installation, enabled state, settings, removals, and registry push/pull/upgrade effects. Router state is transient.

## Dependencies And Integration Points
Integrates distribution reference parsing, authconfig, plugin API types, daemon filters, stream formatters, backend plugin option structs, and error classification.

## Risks
Digest-plus-tag parsing is subtle: remote digest tags are preserved for local names but canonical refs drop tags. User-supplied local names cannot include digests. Streaming errors after flush must be formatted into progress output.

## Test Signals
No direct tests here; plugin integration tests cover remote ref handling, privilege negotiation, lifecycle operations, and registry streaming.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/server/router/plugin/plugin_routes.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/server/router/router.go -->
# sources/cloud-native/moby/daemon/server/router/router.go

## Purpose
`router.go` defines the minimal interfaces shared by all daemon HTTP routers.

## Important APIs, Types, And Functions
`Router` exposes `Routes() []Route`. `Route` exposes `Handler() httputils.APIFunc`, `Method() string`, and `Path() string`.

## Control Flow
Individual router packages return a `Router`; the server iterates each route and registers versioned and unversioned paths with gorilla/mux.

## State And Persistence
No state is stored in the interfaces themselves.

## Dependencies And Integration Points
This is the central contract between route packages and `daemon/server.Server`.

## Risks
Any interface change affects every router package and server registration code.

## Test Signals
Compilation across all router packages and `server.CreateMux` tests provide coverage.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/server/router/router.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/server/router/session/backend.go -->
# sources/cloud-native/moby/daemon/server/router/session/backend.go

## Purpose
`backend.go` defines the session router's backend contract.

## Important APIs, Types, And Functions
`Backend` exposes `HandleHTTPRequest(ctx context.Context, w http.ResponseWriter, r *http.Request) error`.

## Control Flow
The session route delegates the entire request/response handling to the backend, which owns upgrade/session protocol details.

## State And Persistence
The interface itself has no state. Backend implementations manage build/session connection state.

## Dependencies And Integration Points
Depends on standard HTTP and context packages. Used by the deprecated `/session` router.

## Risks
Because the backend writes directly to the response, normal router error behavior may be limited after output starts.

## Test Signals
Session/build integration tests validate backend behavior.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/server/router/session/backend.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/server/router/session/session.go -->
# sources/cloud-native/moby/daemon/server/router/session/session.go

## Purpose
`session.go` defines the deprecated `/session` router for BuildKit/session style HTTP requests.

## Important APIs, Types, And Functions
`sessionRouter` stores a backend and routes. `NewRouter`, `Routes`, and `initRoutes` implement route setup for POST `/session`.

## Control Flow
Construction stores the backend and registers a single route handled by `startSession`.

## State And Persistence
Only route metadata and the backend pointer are stored.

## Dependencies And Integration Points
Uses the shared router package. Comments note deprecation because the engine now supports HTTP/2 and h2c directly.

## Risks
Deprecated endpoint behavior must remain stable until removal for old clients.

## Test Signals
Integration tests for legacy session clients are the primary signal.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/server/router/session/session.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/server/router/session/session_routes.go -->
# sources/cloud-native/moby/daemon/server/router/session/session_routes.go

## Purpose
`session_routes.go` implements POST `/session`.

## Important APIs, Types, And Functions
`startSession` calls `sr.backend.HandleHTTPRequest` and wraps any error as `errdefs.InvalidParameter`.

## Control Flow
The handler performs no parsing itself; all protocol handling is delegated. Backend errors are reclassified as invalid parameters for the HTTP API.

## State And Persistence
State is owned by the backend session implementation.

## Dependencies And Integration Points
Depends on `errdefs` for API error classification and the session backend.

## Risks
Blanket invalid-parameter wrapping can hide backend error specificity. If the backend writes before returning an error, normal error response writing may not be useful.

## Test Signals
No direct unit tests.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/server/router/session/session_routes.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/server/router/swarm/backend.go -->
# sources/cloud-native/moby/daemon/server/router/swarm/backend.go

## Purpose
`backend.go` defines the swarm router backend contract for cluster, service, node, task, secret, config, and log operations.

## Important APIs, Types, And Functions
`Backend` includes swarm init/join/leave/inspect/update/unlock methods; service list/get/create/update/remove/logs; node list/get/update/remove; task list/get; secret CRUD; and config CRUD.

## Control Flow
Swarm route handlers parse HTTP request bodies/query values into API types and option structs, then call these methods.

## State And Persistence
Implementations persist swarm cluster state in the manager/control plane and retrieve task/service logs.

## Dependencies And Integration Points
Depends on API swarm types, server log selectors/options, and `swarmbackend` option structs.

## Risks
The interface is broad and version-sensitive. Route compatibility shims must align with backend expectations for older API clients.

## Test Signals
Compilation against swarm manager implementations and swarm API integration tests validate the contract.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/server/router/swarm/backend.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/server/router/swarm/cluster.go -->
# sources/cloud-native/moby/daemon/server/router/swarm/cluster.go

## Purpose
`cluster.go` defines the swarm router and registers swarm, service, node, task, secret, and config endpoints.

## Important APIs, Types, And Functions
`swarmRouter` stores backend and routes. `NewRouter`, `Routes`, and `initRoutes` implement setup.

## Control Flow
Route registration covers cluster lifecycle, unlock key, services and logs, nodes, tasks and logs, secrets, and configs. Secrets require API 1.25+ and configs require API 1.30+.

## State And Persistence
The router stores no durable state. Cluster state is handled by the backend.

## Dependencies And Integration Points
Uses the shared router constructors and API-version wrappers.

## Risks
The router has many endpoints with overlapping path parameters; adding new swarm paths requires care to avoid path conflicts.

## Test Signals
Swarm API integration tests verify registration and behavior.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/server/router/swarm/cluster.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/server/router/swarm/cluster_routes.go -->
# sources/cloud-native/moby/daemon/server/router/swarm/cluster_routes.go

## Purpose
`cluster_routes.go` implements most swarm API handlers: cluster lifecycle, services, nodes, tasks, secrets, configs, and legacy response shaping.

## Important APIs, Types, And Functions
Handlers include `initCluster`, `joinCluster`, `leaveCluster`, `inspectCluster`, `updateCluster`, `unlockCluster`, `getUnlockKey`, service CRUD/log handlers, node CRUD, task list/get/logs, secret CRUD, and config CRUD. `serviceWithLegacy` supports deprecated `ServiceSpec.Networks`; `backFillLegacyNetwork` injects old fields.

## Control Flow
Handlers decode JSON or filters, parse object versions and booleans, apply API-version stripping, and call backend methods. Service create/update carry registry auth headers and choose `queryRegistry` for API <1.30. Service update parses `registryAuthFrom` and rollback flags. Secret/config templating is rejected before API 1.37. Logs delegate to `swarmLogs`.

## State And Persistence
All persistent swarm state changes are delegated to the backend: Raft cluster membership/configuration, service specs, node specs, secrets, configs, and unlock keys.

## Dependencies And Integration Points
Depends on API swarm/registry types, filters, version helpers, compat wrappers, backend log selectors, and `swarmbackend` options.

## Risks
Version compatibility is dense. Missing version stripping can let old clients set unsupported fields. Version query parsing must reject malformed object versions to avoid unsafe updates. Legacy network backfill is required for pre-1.25 clients.

## Test Signals
`helpers_test.go` covers some version-stripping behavior. Swarm integration tests cover route-level semantics and backend interactions.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/server/router/swarm/cluster_routes.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/server/router/swarm/helpers.go -->
# sources/cloud-native/moby/daemon/server/router/swarm/helpers.go

## Purpose
`helpers.go` contains shared swarm route helpers for log streaming and API-version normalization of service specs.

## Important APIs, Types, And Functions
`swarmLogs` validates log flags, builds `backend.ContainerLogsOptions`, detects TTY from selected services/tasks, calls `ServiceLogs`, sets raw or multiplexed stream media type, and streams via `logstream.Write`. `adjustForAPIVersion` strips unsupported service-spec fields for older API versions.

## Control Flow
Log handling validates `stdout`/`stderr` before starting the stream, parses `since`, computes `Follow`, `Tail`, `Details`, and TTY mode, then writes logs. Version adjustment removes swap/memory swappiness before 1.52, tmpfs options before 1.46, sysctls/credential config/config runtime/max replicas before 1.40, capabilities/ulimits/pids/jobs before 1.41, security options and health start interval before 1.44, maps legacy `Networks` into `TaskTemplate.Networks` before 1.44, and strips `OomScoreAdj` before 1.46.

## State And Persistence
No persistent state is written directly. `adjustForAPIVersion` mutates the in-memory request spec before backend persistence.

## Dependencies And Integration Points
Integrates timestamp parsing, version helpers, backend log APIs, logstream writer, and API swarm/container/mount types.

## Risks
Errors must be returned before log streaming begins. TTY detection requires backend reads for every selector. Version stripping must remain synchronized with API evolution to avoid unsupported fields reaching swarmkit.

## Test Signals
`helpers_test.go` exercises key stripping boundaries for resources, tmpfs options, sysctls, credential specs, runtime config refs, max replicas, ulimits, and pids.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/server/router/swarm/helpers.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/server/router/swarm/helpers_test.go -->
# sources/cloud-native/moby/daemon/server/router/swarm/helpers_test.go

## Purpose
This test verifies that `adjustForAPIVersion` removes or preserves swarm service-spec fields at expected API version boundaries.

## Important APIs, Types, And Functions
`TestAdjustForAPIVersion` builds a service spec with sysctls, credential specs, config references, ulimits, tmpfs options, placement max replicas, pids limit, and resource swap/memory-swappiness pointers.

## Control Flow
The test applies `adjustForAPIVersion` with descending API versions and checks that fields remain for newer versions and are stripped for older versions.

## State And Persistence
No daemon state is persisted; the test validates in-memory request mutation.

## Dependencies And Integration Points
Depends on API swarm/container/mount types and the helper under test.

## Risks
The test intentionally does not verify every possible service field, so new version gates need new assertions.

## Test Signals
Provides focused regression coverage for version-gated swarm service fields.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/server/router/swarm/helpers_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/server/router/system/backend.go -->
# sources/cloud-native/moby/daemon/server/router/system/backend.go

## Purpose
`backend.go` defines system, cluster, build, and status-provider contracts used by the system router.

## Important APIs, Types, And Functions
`Backend` exposes `SystemInfo`, `SystemVersion`, `SystemDiskUsage`, event subscribe/unsubscribe, and registry auth. `ClusterBackend` exposes swarm info. `BuildBackend` exposes build-cache disk usage. `StatusProvider` exposes a swarm status string.

## Control Flow
System routes call these interfaces to build `/info`, `/version`, `/system/df`, `/events`, `/_ping`, and `/auth` responses.

## State And Persistence
Implementations read daemon/system state, subscribe to events, and authenticate to registries. The interface file stores no state.

## Dependencies And Integration Points
Depends on API events/registry/swarm/system types, daemon filters, and backend/buildbackend option structs.

## Risks
The router composes data from multiple backends concurrently; missing or nil implementations must be handled by routes.

## Test Signals
System route integration tests and compile-time backend satisfaction validate this contract.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/server/router/system/backend.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/server/router/system/disk_usage.go -->
# sources/cloud-native/moby/daemon/server/router/system/disk_usage.go

## Purpose
`disk_usage.go` defines compatibility response structs for `/system/df`.

## Important APIs, Types, And Functions
`diskUsageCompat` embeds `legacyDiskUsage` and `system.DiskUsage` so API 1.52 can return both old and new shapes. `legacyDiskUsage` contains `LayersSize`, `Images`, `Containers`, `Volumes`, and `BuildCache`.

## Control Flow
`getDiskUsage` fills `legacyDiskUsage` from the new `backend.DiskUsage` model and conditionally wraps/returns it based on API version and `verbose`.

## State And Persistence
No state is stored; these are response DTOs.

## Dependencies And Integration Points
Depends on API build/container/image/system/volume types and is used by `system_routes.go`.

## Risks
JSON tags and embedded structs define public wire shape; changing them can break clients.

## Test Signals
`disk_usage_test.go` verifies legacy image `VirtualSize` injection.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/server/router/system/disk_usage.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/server/router/system/disk_usage_test.go -->
# sources/cloud-native/moby/daemon/server/router/system/disk_usage_test.go

## Purpose
This test validates legacy `/system/df` image-list compatibility for `VirtualSize`.

## Important APIs, Types, And Functions
`TestDiskUsageVirtualSize` builds a `legacyDiskUsage`, wraps image summaries with `compat.Wrap`, marshals JSON, and checks `VirtualSize` presence/absence and empty-list behavior.

## Control Flow
Subtests verify API <1.44 wrapped responses include `VirtualSize`, API >=1.44 raw responses omit it, and an empty image slice remains an empty JSON array when wrapped.

## State And Persistence
No state is persisted.

## Dependencies And Integration Points
Protects `getDiskUsage` compatibility logic and depends on API image types plus `compat`.

## Risks
Legacy disk-usage clients may depend on `VirtualSize` and empty arrays instead of null/omitted values.

## Test Signals
Direct JSON assertions provide strong regression coverage for response shape.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/server/router/system/disk_usage_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/server/router/system/system.go -->
# sources/cloud-native/moby/daemon/server/router/system/system.go

## Purpose
`system.go` defines the system router, including routes for ping, events, info, version, disk usage, auth, and OPTIONS.

## Important APIs, Types, And Functions
`systemRouter` stores backend, cluster, builder, features callback, route list, and a `singleflight.Group` for `/info` responses keyed by API version. `NewRouter` registers all system routes.

## Control Flow
Construction stores backends and route metadata. `/info` later uses the singleflight group to collapse concurrent collection for the same API version.

## State And Persistence
The router stores in-memory backend references and singleflight state. It does not persist data.

## Dependencies And Integration Points
Integrates `compat`, shared router constructors, and `resenje.org/singleflight`.

## Risks
The singleflight key is API version because response shape differs by version; using a broader key would leak wrong compatibility fields.

## Test Signals
System API tests validate route behavior; no direct tests for router construction here.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/server/router/system/system.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/server/router/system/system_routes.go -->
# sources/cloud-native/moby/daemon/server/router/system/system_routes.go

## Purpose
`system_routes.go` implements daemon system endpoints for ping, info, version, disk usage, events, and registry authentication.

## Important APIs, Types, And Functions
Handlers include `optionsHandler`, `pingHandler`, `getInfo`, `getVersion`, `getDiskUsage`, `getEvents`, and `postAuth`. Helpers include `swarmStatus`, `nonNilSlice`, `invalidRequestError`, `jsonTypes`, and `backFillLegacy`.

## Control Flow
Ping writes cache-control, builder version, swarm status, and OK/HEAD response. Info uses singleflight, merges cluster swarm info/warnings, and strips/injects fields by API version. Disk usage parses object types, runs daemon and build-cache usage in an errgroup, emits legacy and/or new shapes, and injects image `VirtualSize` for older APIs. Events parse `since/until/filters`, choose content type from API version and Accept header, flush headers, emit buffered then live events, optionally backfilling legacy fields. Auth decodes credentials and delegates to the backend.

## State And Persistence
System routes mostly read daemon state. Event subscriptions allocate a backend channel until deferred unsubscribe. Auth may update registry auth state depending on backend implementation.

## Dependencies And Integration Points
Depends on API system/events/registry/swarm types, filters, timestamp parsing, content negotiation, build router builder-version helper, errgroup, stream encoders, and compatibility wrappers.

## Risks
Streaming events cannot return normal errors after headers flush. `/info` response shape is highly version-sensitive. Disk usage concurrently writes shared variables after errgroup tasks, so each variable has a single writer. API 1.52 dual legacy/current disk-usage behavior is temporary and fragile.

## Test Signals
Local disk-usage tests cover `VirtualSize`. Integration tests should cover ping headers, info fields by version, event streaming content types, and auth.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/server/router/system/system_routes.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/server/router/volume/backend.go -->
# sources/cloud-native/moby/daemon/server/router/volume/backend.go

## Purpose
`backend.go` defines local volume and swarm cluster-volume backend contracts for the volume router.

## Important APIs, Types, And Functions
`Backend` covers local volume `List`, `Get`, `Create`, `Remove`, and `Prune`. `ClusterBackend` covers cluster volume `GetVolume`, `GetVolumes`, `CreateVolume`, `RemoveVolume`, `UpdateVolume`, and `IsManager`.

## Control Flow
Routes try local volume operations first for normal volumes and use the cluster backend for API 1.42+ cluster volume features when the node is a manager.

## State And Persistence
Implementations persist local volume metadata/data and swarm cluster-volume specs.

## Dependencies And Integration Points
Depends on API volume types, daemon filters, `volumebackend` option structs, and volume service options.

## Risks
Local and cluster volumes can duplicate names; the router defines precedence rather than preventing all duplication.

## Test Signals
`volume_routes_test.go` uses fake implementations of both interfaces to test routing decisions.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/server/router/volume/backend.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/server/router/volume/volume.go -->
# sources/cloud-native/moby/daemon/server/router/volume/volume.go

## Purpose
`volume.go` defines the volume router and registers volume API endpoints.

## Important APIs, Types, And Functions
`volumeRouter` stores local and cluster backends plus routes. `NewRouter`, `Routes`, and `initRoutes` implement setup.

## Control Flow
Routes include list, inspect, create, prune, update, and delete. Prune requires API 1.25+, update requires API 1.42+.

## State And Persistence
Only backend references and route metadata are stored.

## Dependencies And Integration Points
Uses the shared router package and version wrappers.

## Risks
The wildcard `{name:.*}` can capture names with slashes but also requires careful route ordering for future additions.

## Test Signals
`volume_routes_test.go` exercises the handlers registered here.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/server/router/volume/volume.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/server/router/volume/volume_routes.go -->
# sources/cloud-native/moby/daemon/server/router/volume/volume_routes.go

## Purpose
`volume_routes.go` implements local and swarm cluster-volume API handlers.

## Important APIs, Types, And Functions
Handlers include `getVolumesList`, `getVolumeByName`, `postVolumesCreate`, `putVolumesUpdate`, `deleteVolumes`, and `postVolumesPrune`. `clusterVolumesVersion` is API 1.42.

## Control Flow
List parses filters, queries local volumes, and appends cluster volumes for API 1.42+ managers while converting cluster errors into warnings. Inspect prefers local volumes and falls back to cluster volumes on local not-found for managers. Create chooses cluster creation if `ClusterVolumeSpec` is present and API supports it, otherwise local create. Update requires manager state and parses a swarm object version. Delete first tries local removal, then cluster removal on not-found or force. Prune adds `all=true` before API 1.42 to preserve old behavior.

## State And Persistence
Backends persist volume creation, update, removal, and prune effects. Router mutations are limited to filters/options.

## Dependencies And Integration Points
Depends on containerd errdefs, daemon filters, version helpers, local volume service options, cluster volume backend options, and logging.

## Risks
Local/cluster name duplication and force-delete semantics are subtle. `force` makes local backend suppress not-found, so the router still attempts cluster removal. Manager availability affects cluster volume visibility and errors.

## Test Signals
`volume_routes_test.go` covers local-vs-cluster lookup/list/create/update/remove behavior, manager availability, conflicts, force removal, and fake backend behavior.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/server/router/volume/volume_routes.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/server/router/volume/volume_routes_test.go -->
# sources/cloud-native/moby/daemon/server/router/volume/volume_routes_test.go

## Purpose
This test file validates volume route behavior across local volumes and swarm cluster volumes.

## Important APIs, Types, And Functions
Helpers `callGetVolume` and `callListVolumes` invoke handlers with API 1.42. `fakeVolumeBackend` implements local volume backend behavior; `fakeClusterBackend` implements manager/swarm-aware cluster operations.

## Control Flow
Tests cover not-found handling with no swarm/not-manager/manager, local and swarm lookup, merged listing, regular and cluster creation, update manager requirements/version behavior, local and cluster deletion, not-found propagation, local in-use conflict, and force removal for cluster volumes that require force.

## State And Persistence
Fake backends persist test state in maps; no real daemon state is touched.

## Dependencies And Integration Points
Depends on HTTP test helpers, API volume types, filters, `httputils.APIVersionKey`, `volumebackend.UpdateOptions`, volume service opts, and errdefs classifiers.

## Risks
The tests encode local-first precedence and cluster fallback semantics; changes to that behavior need deliberate updates.

## Test Signals
Provides strong unit coverage for volume router decision logic without requiring a real swarm manager or volume service.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/server/router/volume/volume_routes_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/server/server.go -->
# sources/cloud-native/moby/daemon/server/server.go

## Purpose
`server.go` contains the Docker API server route registration and HTTP handler wrapper logic.

## Important APIs, Types, And Functions
`Server` stores middleware. `UseMiddleware` appends middleware. `makeHTTPHandler` wraps a route with OpenTelemetry, baggage/user-agent context, global middleware, route variables, and error conversion. `CreateMux` registers versioned and unversioned routes and not-found handlers. Constants include `versionMatcher` and `statusClientClosedRequest`.

## Control Flow
For each request, `makeHTTPHandler` builds context baggage, applies global middleware, gets mux variables, calls the route handler, and converts errors to JSON or plain text for very old API versions. If the request context is canceled, it writes/logs status 499 for telemetry. `CreateMux` registers every route at `/v{version}` and bare paths, then configures not-found/method-not-allowed responses.

## State And Persistence
The server stores middleware only. No durable daemon state is changed by this file.

## Dependencies And Integration Points
Integrates gorilla/mux, route interfaces, middleware, HTTP status mapping, OpenTelemetry HTTP instrumentation, daemon version/user-agent baggage, logging, and API error response types.

## Risks
Error handling after client cancellation must avoid writing JSON to closed clients. Route registration creates both versioned/unversioned paths, so duplicate/conflicting paths matter. Old API plain-text errors are a compatibility exception.

## Test Signals
`server_test.go` verifies middleware application and version/server header propagation.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/server/server.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/server/server_test.go -->
# sources/cloud-native/moby/daemon/server/server_test.go

## Purpose
`server_test.go` verifies global middleware wrapping for route handlers.

## Important APIs, Types, And Functions
`TestMiddlewares` constructs a `Server`, installs version middleware, invokes `handlerWithGlobalMiddlewares`, and checks API version context plus `Server` response header.

## Control Flow
The test builds a GET request, recorder, and local handler that asserts middleware side effects. The wrapped handler is called directly rather than through mux registration.

## State And Persistence
No persistent state is changed.

## Dependencies And Integration Points
Depends on daemon config API version constants, `httputils.VersionFromContext`, and server middleware construction.

## Risks
It covers middleware application but not route registration, error conversion, or OpenTelemetry wrapper behavior.

## Test Signals
Confirms middleware adds API version context and Docker server version header before route handler execution.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/server/server_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/server/swarmbackend/swarm.go -->
# sources/cloud-native/moby/daemon/server/swarmbackend/swarm.go

## Purpose
`swarm.go` defines option structs shared between HTTP swarm routers and daemon/swarm backend implementations.

## Important APIs, Types, And Functions
Types include `ConfigListOptions`, `NodeListOptions`, `TaskListOptions`, `UpdateFlags`, `ServiceUpdateOptions`, `ServiceListOptions`, and `SecretListOptions`.

## Control Flow
Routers fill these structs from filters/query parameters and pass them to backend methods.

## State And Persistence
No state is stored. The structs carry request options for backend operations that may mutate swarm state.

## Dependencies And Integration Points
Depends on API swarm registry-auth source type and daemon filters. Used by swarm router handlers and backend interfaces.

## Risks
Adding fields affects both routers and backend implementations. `ServiceUpdateOptions` must preserve registry-auth and rollback semantics.

## Test Signals
Compilation plus swarm route tests validate option wiring.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/server/swarmbackend/swarm.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/server/volumebackend/volume.go -->
# sources/cloud-native/moby/daemon/server/volumebackend/volume.go

## Purpose
`volume.go` defines option structs for cluster volume router/backend interactions.

## Important APIs, Types, And Functions
`ListOptions` carries filters. `UpdateOptions` carries an optional `*volume.ClusterVolumeSpec` as JSON field `Spec`.

## Control Flow
Volume routes parse filters or JSON request bodies into these structs and pass them to cluster backend methods.

## State And Persistence
No state is stored in this file.

## Dependencies And Integration Points
Depends on API volume types and daemon filters. Used by `router/volume` cluster backend methods.

## Risks
JSON field shape is public API for cluster volume update.

## Test Signals
`volume_routes_test.go` uses `UpdateOptions` in update route tests.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/server/volumebackend/volume.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/snapshotter/mount.go -->
# sources/cloud-native/moby/daemon/snapshotter/mount.go

## Purpose
`mount.go` implements snapshotter rootfs mounting with optional reference counting and per-target locking.

## Important APIs, Types, And Functions
`Mounter` exposes `Mount`, `Unmount`, and `Mounted`. `NewMounter` returns a `refCountMounter` wrapping `mounter`. `refCountMounter` uses `mountref.Counter` and `locker.Locker`; `mounter` handles actual target path creation and `mount.All`.

## Control Flow
`refCountMounter.Mount` computes the target, increments a mount refcount, returns early if already referenced, locks target setup, and rolls back refcount/mount/dir on error. `Unmount` decrements refcount and only unmounts/removes the target when it reaches zero. `Mounted` checks kernel mount state and then verifies an active refcount. `mounter.Mount` creates parent and target dirs with root/idmapped ownership and mounts all containerd mounts.

## State And Persistence
Persistent state includes temporary rootfs mount directories under `<home>/rootfs/<snapshotter>/<containerID>`. In-memory state tracks reference counts and locks.

## Dependencies And Integration Points
Integrates containerd mount specs, Moby mountref, locker, mountinfo checks, user identity mapping, and platform-specific `isMounted`/`unmount`.

## Risks
Reference-count correctness is critical; mismatched increments/decrements can leak mounts or unmount a rootfs still in use. Error rollback unmounts/removes only when the refcount drops to zero. Directory ownership must respect user namespace mappings.

## Test Signals
No direct tests listed; snapshotter container lifecycle integration tests should cover mount reuse, cleanup, and failure rollback.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/snapshotter/mount.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/snapshotter/mount_unix.go -->
# sources/cloud-native/moby/daemon/snapshotter/mount_unix.go

## Purpose
`mount_unix.go` provides non-Windows mount-state and unmount helpers for snapshotter rootfs mounts.

## Important APIs, Types, And Functions
`isMounted` calls `mountinfo.Mounted`. `unmount` calls containerd `mount.Unmount(target, unix.MNT_DETACH)`.

## Control Flow
The refcounted mounter uses `isMounted` when constructing the counter and `unmount` during cleanup. Detached unmount lets cleanup proceed even when references are being released asynchronously.

## State And Persistence
The functions read mount table state and unmount mount points. No in-memory state is stored.

## Dependencies And Integration Points
Depends on Moby mountinfo, containerd mount package, and `golang.org/x/sys/unix`.

## Risks
`MNT_DETACH` can hide busy mount cleanup issues. `isMounted` ignores mountinfo errors and returns false, which can affect refcount recovery.

## Test Signals
Covered indirectly by snapshotter mount lifecycle tests on Unix platforms.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/snapshotter/mount_unix.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/snapshotter/mount_windows.go -->
# sources/cloud-native/moby/daemon/snapshotter/mount_windows.go

## Purpose
`mount_windows.go` provides Windows implementations of snapshotter mount helpers.

## Important APIs, Types, And Functions
`isMounted` always returns false. `unmount` calls `mount.Unmount(target, 0)`.

## Control Flow
The common mounter compiles on Windows and delegates unmounts to containerd without Unix flags.

## State And Persistence
No in-memory state is stored. Unmount may affect snapshotter mount state through containerd.

## Dependencies And Integration Points
Depends on containerd's mount package.

## Risks
Always returning false means the refcount counter cannot recover existing mounted state the way Unix can.

## Test Signals
Windows snapshotter integration coverage is the relevant signal.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/snapshotter/mount_windows.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/start.go -->
# sources/cloud-native/moby/daemon/start.go

## Purpose
`start.go` implements container start orchestration and cleanup for failed or completed setup.

## Important APIs, Types, And Functions
`validateState` rejects paused/running/removal/dead containers. `ContainerStart` validates checkpoint mode and host settings, then calls `containerStart`. `containerStart` mounts storage, initializes networking, creates OCI spec, creates/replaces containerd container/task, starts it, updates container state, events, metrics, and checkpoints. `Cleanup` releases containerd, network, mounts, exec commands, volumes, and attach context.

## Control Flow
Start obtains daemon config/container, validates state and settings, then under container lock performs setup with deferred rollback. On error it records state error/exit code, checkpoints, resets, cleans up, and auto-removes if configured. Successful flow mounts, creates network sandbox, sets up dirs/mounts, builds spec, resets restart manager, saves AppArmor config, resolves checkpoint, creates containerd container/task, initializes task networking, starts task, sets running state, starts health monitor, checkpoints, logs start event, and records metrics.

## State And Persistence
Persists container state checkpoints, runtime assignment, mounted rootfs/volumes/secrets, network sandbox allocation, containerd container/task state, health monitor state, events, and metrics.

## Dependencies And Integration Points
Integrates containerd client/container/task APIs, daemon config, image service, libcontainerd, OCI spec generation, networking, mount setup, health monitor, events, metrics, and OpenTelemetry tracing.

## Risks
Start has many rollback paths; missed cleanup leaks mounts, network sandboxes, containerd tasks, or auto-remove containers. Locks must cover container state mutations without blocking backend cleanup indefinitely. Context cancellation is intentionally ignored for some containerd cleanup/start calls to avoid stuck integration tests.

## Test Signals
Broad daemon/container lifecycle integration tests cover start success, invalid states, checkpoints, failed setup cleanup, auto-remove, health, and event emission.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/start.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/start_linux.go -->
# sources/cloud-native/moby/daemon/start_linux.go

## Purpose
`start_linux.go` performs Linux-specific initialization after a containerd task is created but before it starts.

## Important APIs, Types, And Functions
`initializeCreatedTask` receives daemon config, task, container, and OCI spec. It sets the libnetwork sandbox key to `/proc/<pid>/ns/net` when the runtime created a new network namespace, then allocates network resources inside the daemon network namespace.

## Control Flow
If networking is disabled, it returns. Otherwise it checks the OCI spec network namespace; when the namespace path is empty, it fetches the sandbox by container ID and sets its key from the task PID. It then calls `allocateNetwork` through `runInNetNS`.

## State And Persistence
Updates libnetwork sandbox namespace key and allocates network endpoint state for the running container.

## Dependencies And Integration Points
Integrates OCI namespace inspection, libcontainerd task PID, daemon network controller, `runInNetNS`, and daemon networking allocation.

## Risks
Failure after task creation but before task start must propagate so `containerStart` rollback deletes task/container and networking. Namespace-key correctness is required for network operations and stats.

## Test Signals
Linux container start/network integration tests cover this path.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/start_linux.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/start_notlinux.go -->
# sources/cloud-native/moby/daemon/start_notlinux.go

## Purpose
`start_notlinux.go` provides the non-Linux stub for post-task creation initialization.

## Important APIs, Types, And Functions
`initializeCreatedTask` accepts the same signature as the Linux version and returns nil.

## Control Flow
No runtime work is performed on non-Linux platforms.

## State And Persistence
No state is changed.

## Dependencies And Integration Points
Keeps common `containerStart` code portable across platforms.

## Risks
Platform-specific setup required by future non-Linux runtimes must be added here or in more specific build-tag files.

## Test Signals
Compilation and non-Linux lifecycle tests validate the stub.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/start_notlinux.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/start_unix.go -->
# sources/cloud-native/moby/daemon/start_unix.go

## Purpose
`start_unix.go` selects containerd shim/runtime create options for Unix containers.

## Important APIs, Types, And Functions
`getLibcontainerdCreateOptions` ensures `HostConfig.Runtime` is set, checkpoints the container when defaulted, resolves the runtime through `daemonCfg.Runtimes.Get`, and maps errors through `setExitCodeFromError`.

## Control Flow
Callers must hold the container lock. If runtime is empty, it is set to the configured default runtime and persisted. The runtime store returns shim name and options for containerd creation.

## State And Persistence
May persist `HostConfig.Runtime` into the container checkpoint.

## Dependencies And Integration Points
Integrates daemon runtime configuration, container checkpointing, container state exit-code mapping, and containerd create flow in `containerStart`.

## Risks
Runtime resolution failures must set an exit code consistently. Mutating host config under lock is required to avoid races.

## Test Signals
Unix start/runtime integration tests cover default runtime assignment and invalid runtime errors.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/start_unix.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/start_windows.go -->
# sources/cloud-native/moby/daemon/start_windows.go

## Purpose
`start_windows.go` selects runtime create options for Windows containers.

## Important APIs, Types, And Functions
`getLibcontainerdCreateOptions` sets `HostConfig.Runtime` from `daemonCfg.DefaultRuntime` or containerd's default runtime, checkpoints the container, and returns the runtime string with nil options.

## Control Flow
If runtime is already configured it is returned unchanged. Otherwise the function chooses a default and persists it.

## State And Persistence
May persist `HostConfig.Runtime` in the container checkpoint.

## Dependencies And Integration Points
Integrates Windows container start with containerd default runtime selection and daemon configuration.

## Risks
Unlike Unix, this path returns no runtime options; future Windows runtime options would need explicit support.

## Test Signals
Windows lifecycle tests cover runtime defaulting.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/start_windows.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/stats.go -->
# sources/cloud-native/moby/daemon/stats.go

## Purpose
`stats.go` implements the high-level `ContainerStats` API and bridges daemon callers to the stats collector.

## Important APIs, Types, And Functions
`ContainerStats` streams or returns stats to a configured output stream. `subscribeToContainerStats` registers a container with the collector. `GetContainerStats` collects one platform-specific sample and augments it with system CPU and network stats.

## Control Flow
For non-streaming requests, stopped/restarting containers return an empty stats object. One-shot returns a single sample. Non-streaming non-one-shot consumes one previous sample so `PreRead`/`PreCPUStats` are populated. Streaming loops over collector updates, encodes JSON without HTML escaping, and exits on context cancellation. `GetContainerStats` calls platform `stats`, then `getSystemCPUUsage`, then network stats on non-Windows unless networking is disabled.

## State And Persistence
No durable state is persisted. The stats collector stores subscriptions; responses reflect runtime/container/network state.

## Dependencies And Integration Points
Integrates daemon container lookup, backend stats config streams, platform stats implementations, collector pubsub, containerd error classifiers, runtime GOOS, and libnetwork stats.

## Risks
First-sample semantics differ between one-shot, streaming, and normal non-streaming modes. Stats collection returns empty data for not-found/conflict to preserve API behavior. Slow clients can block encoding but subscriptions are cleaned up with defer.

## Test Signals
Platform stats tests cover CPU parsing; integration tests cover Docker stats streaming and one-shot behavior.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/stats.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/stats/collector.go -->
# sources/cloud-native/moby/daemon/stats/collector.go

## Purpose
`collector.go` manages periodic container stats polling and fan-out to subscribers.

## Important APIs, Types, And Functions
`Collector` stores a mutex/condition variable, supervisor, interval, and map from containers to pubsub publishers. Methods include `NewCollector`, `Collect`, `StopCollection`, `Unsubscribe`, and `Run`. `supervisor` requires `GetContainerStats`.

## Control Flow
`Collect` creates or reuses a publisher, broadcasts the condition, and returns a subscription channel. `Run` waits until publishers exist, snapshots container/publisher pairs under lock, unlocks, polls stats for each container, publishes empty stats on error, then sleeps for the configured interval. `Unsubscribe` evicts a channel and removes empty publishers.

## State And Persistence
All state is in-memory subscription/publisher state. No persistent state is written.

## Dependencies And Integration Points
Used by daemon stats APIs through `newStatsCollector`. Depends on Moby `pubsub` and API container stats types.

## Risks
Containers are map keys by pointer, so lifecycle code must pass the same container object. `Run` never exits. Polling is serialized across active containers, so many subscribers/containers can increase interval latency.

## Test Signals
No direct tests here; Docker stats integration tests exercise collector behavior.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/stats/collector.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/stats_collector.go -->
# sources/cloud-native/moby/daemon/stats_collector.go

## Purpose
`stats_collector.go` constructs and starts the daemon's stats collector.

## Important APIs, Types, And Functions
`newStatsCollector` reads machine memory on Linux, stores it in `daemon.machineMemory`, creates a `stats.Collector`, starts `Run` in a goroutine, and returns it.

## Control Flow
On Linux, meminfo is read best-effort and ignored on error. The collector starts immediately and waits until subscriptions exist.

## State And Persistence
Updates in-memory `daemon.machineMemory`; starts a long-lived goroutine. No durable state is persisted.

## Dependencies And Integration Points
Integrates the daemon with `daemon/stats.Collector` and `pkg/meminfo`.

## Risks
The collector goroutine has no stop path in this file. Incorrect machine memory affects reported memory limit clamping.

## Test Signals
Stats integration tests indirectly validate collector startup and memory limit reporting.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/stats_collector.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/stats_unix.go -->
# sources/cloud-native/moby/daemon/stats_unix.go

## Purpose
`stats_unix.go` converts containerd/cgroups metrics into Docker API stats responses on non-Windows platforms and reads host CPU counters.

## Important APIs, Types, And Functions
`stats` obtains a running task and dispatches metrics to `statsV1` or `statsV2`. `copyBlkioEntry`, `statsV1`, `statsV2`, `getNetworkSandboxID`, `getNetworkStats`, `getSystemCPUUsage`, and `readSystemCPUUsage` implement conversion and host/network augmentation.

## Control Flow
The daemon locks the container long enough to obtain a running task, reads task stats, builds a `StatsResponse`, then converts cgroup v1 or v2 metrics. Network stats resolve container-network namespace sharing chains before querying libnetwork sandbox statistics. CPU usage scans `/proc/stat`, sums aggregate CPU ticks, converts to nanoseconds, and counts per-CPU lines.

## State And Persistence
No state is persisted. It reads containerd metrics, libnetwork sandbox stats, and `/proc/stat`; it uses `daemon.machineMemory` to cap memory limit reporting.

## Dependencies And Integration Points
Depends on containerd cgroups v1/v2 stats, containerd errdefs, API container stats, daemon containers, libnetwork sandbox statistics, and `/proc/stat` format.

## Risks
Metric schema differences between cgroup v1 and v2 are substantial. Missing task stats map to not-found for API compatibility. Network-mode container chains can fail if referenced containers disappear. CPU parsing assumes cpu lines are at the start and fields are valid integers.

## Test Signals
`stats_unix_test.go` verifies `/proc/stat` parsing. Docker stats integration tests cover cgroup conversion and network stats.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/stats_unix.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/stats_unix_test.go -->
# sources/cloud-native/moby/daemon/stats_unix_test.go

## Purpose
This test validates parsing of Linux `/proc/stat` CPU usage data.

## Important APIs, Types, And Functions
`TestGetSystemCPUUsageParsing` embeds `testdata/stat`, passes it to `readSystemCPUUsage`, and checks expected total CPU nanoseconds and CPU count.

## Control Flow
The test avoids reading the real host by using an embedded fixture.

## State And Persistence
No state is persisted.

## Dependencies And Integration Points
Protects host CPU values used by `GetContainerStats` for Docker stats CPU percentage calculations.

## Risks
Only one fixture is covered; malformed or partial `/proc/stat` cases rely on function error paths.

## Test Signals
Directly verifies the parser's tick-to-nanosecond conversion and CPU line counting.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/stats_unix_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/stats_windows.go -->
# sources/cloud-native/moby/daemon/stats_windows.go

## Purpose
`stats_windows.go` converts Windows HCS/containerd task stats into Docker API stats responses.

## Important APIs, Types, And Functions
`stats` obtains a running task, reads task stats, and maps HCS processor, memory, storage, and network counters. `getNetworkStats` returns an empty map because network stats are already included. `getSystemCPUUsage` is a no-op returning zeros.

## Control Flow
The function locks only to get the running task. If HCS stats exist, it fills CPU total/kernel/user 100ns counters, memory commit/private working set, storage normalized counters, and per-endpoint network stats.

## State And Persistence
No state is persisted; reads HCS task metrics only.

## Dependencies And Integration Points
Depends on containerd task stats, Windows HCS stats shape, daemon platform `NumProcs`, API stats response types, and error classification.

## Risks
Windows stats units differ from Unix. System CPU usage is unavailable here, so consumers must handle zero host CPU fields.

## Test Signals
Windows Docker stats integration tests are the primary signal.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/stats_windows.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/stop.go -->
# sources/cloud-native/moby/daemon/stop.go

## Purpose
`stop.go` implements graceful container stop with timeout and force-kill fallback.

## Important APIs, Types, And Functions
`ContainerStop` resolves a container and checks running state. `containerStop` chooses stop signal/timeout from container defaults or request options, sends the signal, waits for not-running, and calls `Kill` on timeout.

## Control Flow
`ContainerStop` returns not-modified if already stopped and wraps stop failures as system errors. `containerStop` uses `context.WithoutCancel` so client cancellation does not abort stopping. It parses custom signals, builds a timeout context unless timeout is negative, waits for exit, logs signal errors, returns early for infinite wait interruption, and force-kills if the container missed the timeout. On success it logs a stop event and locks the container to wait for exit handler checkpointing.

## State And Persistence
Backend state changes include process signal/kill, container state transition by the monitor/exit handler, stop event emission, and state checkpoint synchronization.

## Dependencies And Integration Points
Integrates container state wait conditions, daemon kill functions, API stop options, signal parsing, events, logging, and errdefs.

## Risks
Negative timeout means no force kill; interrupted waits can return signal errors. The function intentionally outlives request cancellation. Waiting for the exit handler through a lock is subtle but ensures status persistence before returning.

## Test Signals
Container stop integration tests cover signal handling, timeout behavior, already-stopped responses, and kill fallback.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/stop.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/top_unix.go -->
# sources/cloud-native/moby/daemon/top_unix.go

## Purpose
`top_unix.go` implements `docker top` on non-Windows platforms by combining container task PIDs with host `ps` output.

## Important APIs, Types, And Functions
Helpers include `validatePSArgs`, `fieldsASCII`, `appendProcess2ProcList`, `hasPid`, `parsePSOutput`, and `psPidsArg`. `ContainerTop` obtains task PIDs, runs `ps`, parses output, and logs a top event.

## Control Flow
Default `psArgs` is `-ef`. Arguments are validated to disallow remapping non-`pid` columns to `PID`. The daemon obtains the running task, rejects restarting containers, reads task PIDs, runs `ps` with `-q<pids>`, retries without `-q` for incompatible options, extracts stderr on failures, parses rows with a PID column, and includes matching processes plus thread continuation lines with `PID` value `-`.

## State And Persistence
No durable state is changed except event emission.

## Dependencies And Integration Points
Depends on OS `ps`, containerd task PID listing, API top response types, daemon container lookup/state, lazy regex, and errdefs.

## Risks
Parsing `ps` output is locale/implementation sensitive. The file intentionally uses ASCII-only whitespace parsing to avoid Unicode column spoofing. Retrying without `-q` can process more output but filters by PID afterward.

## Test Signals
`top_unix_test.go` covers argument validation, ASCII whitespace behavior, missing PID column, and output parsing.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/top_unix.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/top_unix_test.go -->
# sources/cloud-native/moby/daemon/top_unix_test.go

## Purpose
This test file validates Unix `docker top` argument validation and `ps` output parsing.

## Important APIs, Types, And Functions
`TestContainerTopValidatePSArgs` exercises `validatePSArgs`. `TestContainerTopParsePSOutput` exercises `parsePSOutput`.

## Control Flow
Validation cases cover allowed and disallowed `PID` column renames, ASCII spaces, Unicode spaces, and empty/default args. Parse cases cover normal output, missing PID column, and Unicode whitespace that must not be treated as field separators.

## State And Persistence
No state is persisted.

## Dependencies And Integration Points
Protects the parser and validation logic used by `ContainerTop`.

## Risks
The tests do not execute real `ps`, so platform-specific `ps` option compatibility is covered elsewhere.

## Test Signals
Provides focused regression coverage for security-sensitive parsing rules.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/top_unix_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/top_windows.go -->
# sources/cloud-native/moby/daemon/top_windows.go

## Purpose
`top_windows.go` implements `docker top` for Windows containers using containerd/HCS task summaries.

## Important APIs, Types, And Functions
`ContainerTop` rejects ps arguments, obtains a running task, calls `task.Summary`, and returns titles `Name`, `PID`, `CPU`, and `Private Working Set`.

## Control Flow
After container lookup and restart/running validation, the function reads process summaries, formats combined kernel+user 100ns CPU time as `HH:MM:SS.mmm`, formats private working set with `units.HumanSize`, and appends rows to `TopResponse`.

## State And Persistence
No persistent state is changed.

## Dependencies And Integration Points
Integrates Windows task summaries from libcontainerd, API top response types, and Docker units formatting.

## Risks
Windows does not support Linux `psArgs`; clients passing args receive an error. CPU is cumulative time, not percentage.

## Test Signals
Windows top integration tests validate task summary mapping.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/top_windows.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/unpause.go -->
# sources/cloud-native/moby/daemon/unpause.go

## Purpose
`unpause.go` resumes a paused container.

## Important APIs, Types, And Functions
`ContainerUnpause` resolves a container and delegates to `containerUnpause`. `containerUnpause` checks paused state, gets the running task, calls `Resume`, updates state/health/events, and checkpoints.

## Control Flow
The container is locked during paused-state validation, task lookup, resume, state mutation, state counter update, health monitor update, event emission, and checkpoint attempt.

## State And Persistence
Updates in-memory paused state, state counters, health monitor behavior, emits an unpause event, and persists the container checkpoint.

## Dependencies And Integration Points
Integrates containerd task resume, container state, daemon health monitor, event logging, and container checkpoint replica.

## Risks
Returning plain formatted errors rather than errdefs for not-paused/resume failures may affect HTTP classification. Holding the container lock while calling `Resume` can block concurrent state operations.

## Test Signals
Container pause/unpause integration tests cover state transitions and event emission.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/unpause.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/update.go -->
# sources/cloud-native/moby/daemon/update.go

## Purpose
`update.go` updates container host/resource configuration and applies resource changes to running tasks.

## Important APIs, Types, And Functions
`ContainerUpdate` validates requested settings and returns warnings. `update` persists host config, updates restart policy monitor, and calls containerd task `UpdateResources` for running containers. `errCannotUpdate` wraps errors with container context.

## Control Flow
Validation runs before container lookup/update. `update` backs up `HostConfig`, sets a deferred rollback flag, locks the container, rejects removal/dead state, calls `UpdateContainer`, checkpoints, unlocks, updates monitor if restart policy changed, logs an update event, gets a running task unless stopped/restarting, converts resources to containerd resources, and applies them. On failure after mutation it restores the old host config and checkpoints if the container is still valid.

## State And Persistence
Persists `HostConfig` changes, restart monitor policy, container checkpoints, resource limits in the running containerd task, and update events.

## Dependencies And Integration Points
Integrates daemon config validation, container state/host config mutation, containerd resource conversion/update, restart monitor, errdefs, and events.

## Risks
Rollback is critical because config persistence can succeed before runtime resource update fails. Stopped/restarting containers keep only persisted config for next start. Containerd resource update errors are wrapped as system errors.

## Test Signals
Container update integration tests cover validation warnings, stopped/running update behavior, restart policy changes, and resource update failures.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/update.go -->
