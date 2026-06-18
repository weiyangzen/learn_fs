# Research: subset-b-000008

Grouped research for BuildKit client connection helpers, client DTO/API helpers, and LLB graph construction files. Each section preserves the source path for reconciliation into source-tree-aligned per-file reports.

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/client/compatibility_test.go -->
# sources/cloud-native/buildkit/client/compatibility_test.go

Purpose: integration regression coverage for exporter `CompatibilityVersion` behavior across image and OCI exporters. It constructs deterministic image graphs, exports them under supported compatibility versions, compares manifests/configs/layers against embedded goldens under `testdata/compatibility`, and can update those goldens via `BUILDKIT_UPDATE_COMPAT_GOLDENS`.

Important APIs/types/functions: `compatibilityCase` describes exporter attribute cases such as gzip levels, uncompressed, zstd OCI media types, annotations, and provenance. `compatibilityActual` stores digests, raw JSON, normalized JSON, and layer expectations. `TestCompatibilityIntegration` runs three sandboxed integration cases with mirrored busybox. `testImageExporterCompatibilityVersion`, `testOCIExporterCompatibilityVersion`, and `testImageExporterCompatibilityVersionProvenance` drive direct push, OCI layout, and provenance assertions. Helper functions create fixture images and definitions, run exports, read image/OCI content providers, normalize JSON, diff mismatches, and write/read golden files.

Control flow: each test checks worker feature compatibility and Linux support, creates a client and registry, creates a stable base image from mirrored busybox, loops over `compat.SupportedCompatibilityVersions()` or `BUILDKIT_TEST_EXPECTED_COMPATIBILITY_VERSION`, prunes between cases, builds an LLB definition with image, HTTP, git, file, and exec inputs, exports it, then compares actual image artifacts to golden expectations. Unsupported zstd on compatibility v0.13 is asserted through structured unsupported-feature errors rather than golden comparison. Provenance-specific coverage verifies that SLSA predicate metadata records the requested compatibility version.

State and persistence: uses embedded golden files for expected manifests/configs; optional update mode writes files back into the source tree and deduplicates common image/OCI artifacts. Temporary registries, HTTP servers, git repos, OCI layout directories, and BuildKit content references are created during tests. Determinism depends on `source-date-epoch`, timestamp rewriting, fixed git dates, fixed HTTP last-modified time, and a pinned busybox digest.

Dependencies/integration points: integrates with `integration.Sandbox`, `workers.CheckFeatureCompat`, BuildKit `Client.Build`, gateway solve, LLB source and file APIs, `contentutil.ProviderFromRef`, OCI image-spec, image exporter metadata keys, provenance types, source resolver image config resolution, and gRPC error conversion. It is a high-level contract between client solve options, exporter implementation, compatibility gating, and generated artifact format.

Risks/test signals: the file is itself a broad integration test and is sensitive to exporter serialization, compression defaults, timestamp handling, provenance schema, registry behavior, and platform normalization. Golden update mode can hide regressions if used without review. Networked/local external tools such as git and registry setup make it slower and environment-dependent. It explicitly catches manifest/config JSON drift, layer media type/digest drift, unsupported feature reporting, and provenance compatibility-version propagation.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/client/compatibility_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/client/connhelper/connhelper.go -->
# sources/cloud-native/buildkit/client/connhelper/connhelper.go

Purpose: shared registry for client connection helpers keyed by URL scheme. It lets BuildKit clients map custom daemon URLs to a `grpc.WithContextDialer`-compatible connection function.

Important APIs/types/functions: `ConnectionHelper` exposes `ContextDialer func(context.Context, string) (net.Conn, error)`. `GetConnectionHelper` parses a daemon URL, looks up a registered scheme in package-global `helpers`, and returns nil when unsupported. `Register` installs a scheme handler.

Control flow: helper packages register themselves in `init`; caller passes a daemon URL; URL parse errors are returned; unknown schemes fall through without error; known schemes call the registered factory with the parsed URL.

State and persistence: the only state is the in-memory package-level `helpers` map. There is no locking, so registration is expected during package initialization before concurrent lookups.

Dependencies/integration points: standard `net`, `net/url`, and `context`; consumed by Docker, Podman, nerdctl, Kubernetes pod, SSH, and npipe helper packages. The returned dialer is intended for gRPC client configuration.

Risks/test signals: risks are duplicate/late registrations and concurrent map access if external packages register dynamically. The file has no direct test in this subset; scheme-specific tests validate parsing behavior in registered helpers.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/client/connhelper/connhelper.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/client/connhelper/dockercontainer/dockercontainer.go -->
# sources/cloud-native/buildkit/client/connhelper/dockercontainer/dockercontainer.go

Purpose: connection helper for `docker-container://<container>` URLs, allowing a client to talk to `buildctl dial-stdio` inside a Docker container.

Important APIs/types/functions: `init` registers scheme `docker-container`. `Helper` parses a `Spec` and returns a `ConnectionHelper` whose dialer runs `docker [--context=...] exec -i <container> buildctl dial-stdio` through Docker CLI `commandconn`. `Spec` stores `Context` and `Container`. `SpecFromURL` extracts query parameter `context` and the hostname as container name.

Control flow: URL parsing validates the container host is present; dialing builds optional context flags, then spawns the Docker CLI with a background context so the process can remain alive for the connection lifetime after gRPC dial setup.

State and persistence: no persistent state beyond global registration. Connections are external subprocess-backed streams into a running container.

Dependencies/integration points: uses Docker CLI `commandconn`, the shared `connhelper` registry, and `github.com/pkg/errors`. Integrates with BuildKit containers that provide `buildctl dial-stdio`.

Risks/test signals: container names are not further validated here, relying on argument-vector invocation to avoid shell interpolation. The background context means cancellation of the dial context will not necessarily terminate the helper process after connection establishment. Unit coverage in `dockercontainer_test.go` checks valid context parsing and missing container errors.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/client/connhelper/dockercontainer/dockercontainer.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/client/connhelper/dockercontainer/dockercontainer_test.go -->
# sources/cloud-native/buildkit/client/connhelper/dockercontainer/dockercontainer_test.go

Purpose: unit tests for Docker container connection-helper URL parsing.

Important APIs/types/functions: `TestSpecFromURL` table-tests `SpecFromURL` for a bare container URL, a URL with `context`, and an empty host.

Control flow: each input string is parsed by `net/url`, then `SpecFromURL` is called. Non-nil expected specs require no error and structural equality; nil expected specs require an error.

State and persistence: no persistent state; pure parser test.

Dependencies/integration points: standard `net/url`, Go testing, and `testify/require`.

Risks/test signals: confirms missing container rejection and context query extraction. It does not test dialer command arguments, URL path behavior, unexpected query keys, or Docker context value validation.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/client/connhelper/dockercontainer/dockercontainer_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/client/connhelper/kubepod/kubepod.go -->
# sources/cloud-native/buildkit/client/connhelper/kubepod/kubepod.go

Purpose: connection helper for `kube-pod://<pod>` URLs, tunneling to `buildctl dial-stdio` inside a Kubernetes pod/container through `kubectl exec`.

Important APIs/types/functions: `init` registers scheme `kube-pod`. `Helper` returns a dialer that runs `kubectl --context=<context> --namespace=<namespace> exec --container=<container> -i <pod> -- buildctl dial-stdio`. `Spec` stores context, namespace, pod, and container. `SpecFromURL` extracts query parameters and validates pod/namespace/container identifiers. `validKubeIdentifier` matches `^[-a-z0-9.]+$`.

Control flow: URL host becomes pod name; namespace and container are optional but validated if set; context is not validated and may contain characters like `@`. Dialing always includes context/namespace/container flags even if values are empty, then runs the subprocess via `commandconn` with background context.

State and persistence: no persistent state beyond scheme registration. The helper depends on the user’s kubeconfig and target pod runtime state.

Dependencies/integration points: shared `connhelper`, Docker CLI `commandconn`, `kubectl`, Kubernetes naming rules, and BuildKit’s stdio dial endpoint inside the container.

Risks/test signals: always passing empty `--context=`, `--namespace=`, or `--container=` can interact with kubectl defaults differently than omitting flags; parser validation excludes underscores and uppercase names for pod/container/namespace but intentionally leaves context unrestricted. Unit tests cover valid/invalid identifiers and context with `@`.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/client/connhelper/kubepod/kubepod.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/client/connhelper/kubepod/kubepod_test.go -->
# sources/cloud-native/buildkit/client/connhelper/kubepod/kubepod_test.go

Purpose: unit tests for Kubernetes pod connection-helper URL parsing and identifier validation.

Important APIs/types/functions: `TestSpecFromURL` covers minimal pod URLs, full context/namespace/container URLs, contexts containing `@`, empty pod names, and unsupported pod/container/namespace names.

Control flow: each URL string is parsed, passed to `SpecFromURL`, then compared to an expected `Spec` or expected error.

State and persistence: no persistent state.

Dependencies/integration points: standard `net/url`, testing, and `testify/require`.

Risks/test signals: test signals prove query extraction and validation boundaries for Kubernetes identifiers. It does not inspect actual kubectl command construction or behavior when optional query values are empty.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/client/connhelper/kubepod/kubepod_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/client/connhelper/nerdctlcontainer/nerdctlcontainer.go -->
# sources/cloud-native/buildkit/client/connhelper/nerdctlcontainer/nerdctlcontainer.go

Purpose: connection helper for `nerdctl-container://<container>` URLs, connecting to BuildKit inside a nerdctl-managed container.

Important APIs/types/functions: `init` registers `nerdctl-container`. `Helper` creates a dialer running `nerdctl exec [--namespace <namespace>] -i <container> buildctl dial-stdio`. `Spec` stores container and namespace. `SpecFromURL` extracts hostname and optional `namespace` query value.

Control flow: parser rejects missing container name. Dialer appends namespace arguments only when non-empty, then delegates to `commandconn.New` with background context.

State and persistence: no persistent state except registration. Runtime behavior depends on nerdctl/containerd namespace and target container availability.

Dependencies/integration points: Docker CLI `commandconn`, shared `connhelper`, `nerdctl`, and BuildKit’s `dial-stdio` command.

Risks/test signals: namespace value is not validated and command behavior is external. Cancellation semantics mirror other helpers through background context. Tests currently cover only basic container and missing-container parsing, not namespace extraction or subprocess arguments.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/client/connhelper/nerdctlcontainer/nerdctlcontainer.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/client/connhelper/nerdctlcontainer/nerdctlcontainer_test.go -->
# sources/cloud-native/buildkit/client/connhelper/nerdctlcontainer/nerdctlcontainer_test.go

Purpose: unit tests for nerdctl container helper URL parsing.

Important APIs/types/functions: `TestSpecFromURL` validates `nerdctl-container://containername` and rejects `nerdctl-container://`.

Control flow: parses each URL, calls `SpecFromURL`, and asserts either equality or error.

State and persistence: none.

Dependencies/integration points: `net/url`, testing, and `testify/require`.

Risks/test signals: confirms required container host handling. It does not currently test `namespace` query parsing, unknown query handling, or helper command construction.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/client/connhelper/nerdctlcontainer/nerdctlcontainer_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/client/connhelper/npipe/npipe.go -->
# sources/cloud-native/buildkit/client/connhelper/npipe/npipe.go

Purpose: registration shim for named-pipe connection support under `npipe://` URLs.

Important APIs/types/functions: package `init` registers scheme `npipe` with the platform-specific `Helper` function defined in build-tagged files.

Control flow: import side effect installs the helper during package initialization.

State and persistence: only shared registry mutation in `connhelper`.

Dependencies/integration points: shared `connhelper` registry and platform-specific implementations in `npipe_windows.go` or `npipe_other.go`.

Risks/test signals: behavior depends entirely on build tags. There are no direct tests in this subset; platform files define success/error behavior.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/client/connhelper/npipe/npipe.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/client/connhelper/npipe/npipe_other.go -->
# sources/cloud-native/buildkit/client/connhelper/npipe/npipe_other.go

Purpose: non-Windows implementation of the `npipe` helper that reports unsupported platform usage.

Important APIs/types/functions: build tag `!windows`; `Helper` returns nil helper and error `npipe connections are only supported on windows`.

Control flow: any non-Windows attempt to construct an npipe helper fails immediately.

State and persistence: none.

Dependencies/integration points: standard errors, URL type, and shared `ConnectionHelper`.

Risks/test signals: clear fail-fast behavior avoids silent unsupported connections. No direct tests in this subset.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/client/connhelper/npipe/npipe_other.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/client/connhelper/npipe/npipe_windows.go -->
# sources/cloud-native/buildkit/client/connhelper/npipe/npipe_windows.go

Purpose: Windows implementation for `npipe://` URLs using Windows named pipes.

Important APIs/types/functions: build tag `windows`; `Helper` parses the URL by splitting on `://`, converts forward slashes to backslashes, and returns a dialer calling `winio.DialPipeContext`.

Control flow: invalid URL strings without a scheme separator are rejected. Valid URLs produce a connection helper whose dialer uses the caller’s context for pipe dialing.

State and persistence: no persistent state; connects to OS named pipe endpoints.

Dependencies/integration points: `github.com/Microsoft/go-winio`, shared `connhelper`, URL parsing, and BuildKit daemon endpoints exposed over Windows named pipes.

Risks/test signals: address conversion is simple string manipulation after URL stringification, so unusual URL escaping or authority/path forms should be handled cautiously. No direct tests in this subset.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/client/connhelper/npipe/npipe_windows.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/client/connhelper/podmancontainer/podmancontainer.go -->
# sources/cloud-native/buildkit/client/connhelper/podmancontainer/podmancontainer.go

Purpose: connection helper for `podman-container://<container>` URLs, tunneling BuildKit client traffic through `podman exec`.

Important APIs/types/functions: `init` registers `podman-container`; `Helper` returns a `ConnectionHelper` that runs `podman exec -i <container> buildctl dial-stdio`; `SpecFromURL` extracts and requires the hostname as container name.

Control flow: parser rejects empty host; dialer launches the external command through `commandconn` using background context.

State and persistence: no persistent state except registration. Runtime depends on local Podman and the target container.

Dependencies/integration points: shared `connhelper`, Docker CLI `commandconn`, Podman CLI, and in-container BuildKit `dial-stdio`.

Risks/test signals: no query options or validation beyond non-empty container. Background context affects cancellation semantics. Unit tests cover valid and missing container parsing only.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/client/connhelper/podmancontainer/podmancontainer.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/client/connhelper/podmancontainer/podmancontainer_test.go -->
# sources/cloud-native/buildkit/client/connhelper/podmancontainer/podmancontainer_test.go

Purpose: unit tests for Podman container URL parsing.

Important APIs/types/functions: `TestSpecFromURL` verifies a valid container host and rejects an empty host.

Control flow: parse string, call `SpecFromURL`, require equality or error based on expected table entry.

State and persistence: none.

Dependencies/integration points: `net/url`, testing, and `testify/require`.

Risks/test signals: confirms minimal parse contract; does not test command execution, path handling, or unsupported query parameters.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/client/connhelper/podmancontainer/podmancontainer_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/client/connhelper/ssh/ssh.go -->
# sources/cloud-native/buildkit/client/connhelper/ssh/ssh.go

Purpose: connection helper for `ssh://` URLs, connecting to a remote BuildKit endpoint by running `buildctl dial-stdio` over SSH.

Important APIs/types/functions: `init` registers `ssh`. `Helper` turns a parsed `Spec` into a dialer running `ssh [-l user] [-p port] -- <host> buildctl [--addr unix://<socket>] dial-stdio`. `Spec` contains user, host, port, and optional socket path. `SpecFromURL` extracts URL components, rejects plaintext passwords, missing hosts, query strings, and fragments.

Control flow: URL user info may only contain username; path becomes a Unix socket override; raw query and fragment are disallowed to avoid ambiguous or unsupported settings. Dialer uses background context and argument-vector construction.

State and persistence: no persistent state except registry entry. Runtime state is the SSH session and optional remote Unix socket.

Dependencies/integration points: shared `connhelper`, Docker CLI `commandconn`, local `ssh` binary, remote `buildctl`, and BuildKit daemon address selection.

Risks/test signals: plaintext password rejection avoids credential leakage. Path-as-socket is Unix-specific and prepends `unix://`. Host/user/port are delegated to SSH; no validation beyond URL parsing. Unit tests cover user/port/socket, password rejection, queries/fragments, and missing host.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/client/connhelper/ssh/ssh.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/client/connhelper/ssh/ssh_test.go -->
# sources/cloud-native/buildkit/client/connhelper/ssh/ssh_test.go

Purpose: unit tests for SSH connection-helper URL parsing.

Important APIs/types/functions: `TestSpecFromURL` covers host-only URLs, user/port/socket paths, password rejection, socket-only path, query rejection, fragment rejection, and missing host rejection.

Control flow: table-driven parse/assert loop follows the same pattern as the container helpers.

State and persistence: none.

Dependencies/integration points: `net/url`, testing, and `testify/require`.

Risks/test signals: confirms parser security and ambiguity checks. It does not cover generated SSH command argument ordering or remote command behavior.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/client/connhelper/ssh/ssh_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/client/diskusage.go -->
# sources/cloud-native/buildkit/client/diskusage.go

Purpose: public client API for querying BuildKit disk usage and converting control API records into client-facing `UsageInfo` structures.

Important APIs/types/functions: `UsageInfo` exposes ID, mutability, in-use status, size, timestamps, usage count, parent IDs, description, record type, and shared status. `Client.DiskUsage` accepts `DiskUsageOption`s, calls `ControlClient().DiskUsage`, converts protobuf records, and sorts output. `DiskUsageInfo`, `DiskUsageOption`, `WithAgeLimit`, and `UsageRecordType` define option and record-type contracts.

Control flow: options mutate a `DiskUsageInfo`; request sends filters and age limit nanoseconds; response records are mapped one by one, including nil-safe `LastUsedAt`; slice is sorted ascending by size then ID.

State and persistence: no local persistence; reflects remote BuildKit worker/cache state at query time.

Dependencies/integration points: BuildKit control API, protobuf timestamp conversion, shared `Filter` option from `filter.go`, and `cmp`/`slices` for deterministic ordering.

Risks/test signals: age limit uses raw `time.Duration` int64, so units must match server expectations. Sorting by ascending size may be API-observable. No direct test in this subset; consumers rely on control API integration tests elsewhere.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/client/diskusage.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/client/exporters.go -->
# sources/cloud-native/buildkit/client/exporters.go

Purpose: defines public exporter type constants and parsing for local exporter modes.

Important APIs/types/functions: exporter constants `image`, `local`, `tar`, `oci`, and `docker`; `LocalExporterMode` with `copy` and `delete`; `ParseLocalExporterMode` normalizes input and validates supported mode.

Control flow: parser trims whitespace, lowercases input, maps empty string to `copy`, accepts `copy` and `delete`, and returns an error for anything else.

State and persistence: none.

Dependencies/integration points: used by client solve/export configuration and local exporter behavior selection; depends on `strings` and `pkg/errors`.

Risks/test signals: empty defaults to copy, which is compatibility-sensitive. No direct tests in this subset, but invalid mode errors protect callers from silent behavior changes.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/client/exporters.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/client/filter.go -->
# sources/cloud-native/buildkit/client/filter.go

Purpose: small shared option adapter that applies filter strings to multiple client APIs.

Important APIs/types/functions: `WithFilter` returns `Filter`; `Filter` implements `SetDiskUsageOption`, `SetPruneOption`, and `SetListWorkersOption`.

Control flow: each setter assigns the filter slice to the corresponding option struct.

State and persistence: no persistence; the caller-owned slice is assigned directly.

Dependencies/integration points: ties disk usage, prune, and list-workers option systems together.

Risks/test signals: direct slice assignment means subsequent caller mutation could affect options if reused before request construction. No direct tests in this subset.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/client/filter.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/client/graph.go -->
# sources/cloud-native/buildkit/client/graph.go

Purpose: client-facing graph/status data structures for solve progress and responses.

Important APIs/types/functions: `Vertex` captures graph vertex digest, inputs, name, timings, cache/error state, and progress group. `VertexStatus` tracks progress counters. `VertexLog` carries stream bytes. `VertexWarning` carries warning text, URL, source info, and ranges. `SolveStatus` groups progress events. `SolveResponse` stores exporter/cache exporter responses.

Control flow: this file contains data definitions only; flow is in clients that populate and consume these structs.

State and persistence: no internal state; JSON tags define serialized API shape.

Dependencies/integration points: `solver/pb` progress/source structures, OpenContainers digest, and solve/status streaming APIs.

Risks/test signals: schema changes are client API changes. No direct tests in this subset; integration is exercised through solve progress consumers.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/client/graph.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/client/info.go -->
# sources/cloud-native/buildkit/client/info.go

Purpose: public client API for retrieving daemon version information and converting API CDI device structures.

Important APIs/types/functions: `Info` contains `BuildkitVersion`. `BuildkitVersion` stores package, version, revision, and optional Dockerfile frontend version. `CDIDevice` mirrors CDI fields. `Client.Info` calls the control API and maps version data. `fromAPIBuildkitVersion` and `fromAPICDIDevices` convert API types.

Control flow: `Client.Info` issues an empty `InfoRequest`, wraps call errors, and returns an `Info` with nil-safe version conversion. CDI conversion appends each input device to output.

State and persistence: no local persistence; returns daemon state at call time.

Dependencies/integration points: BuildKit control API and API types. CDI conversion is a helper for other client-facing APIs even though `Client.Info` currently returns only version data.

Risks/test signals: nil version becomes zero-value fields. `fromAPICDIDevices` assumes non-nil device entries; nil entries would panic. No direct tests in this subset.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/client/info.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/client/llb/async.go -->
# sources/cloud-native/buildkit/client/llb/async.go

Purpose: lazy asynchronous state transformation support for LLB states, used for operations such as image metadata resolution.

Important APIs/types/functions: `asyncState` stores a transformation function, previous state, and `flightcontrol.CachedGroup` to deduplicate execution. It implements `Output`, `Vertex`, `ToInput`, and `Do`. `errVertex` adapts async errors into a `Vertex` that fails validation/marshal.

Control flow: async callbacks are not run when the state chain is created. During vertex/input/value resolution, `Do` calls the transformation once per constraints through the cached group; successful target state delegates output and input behavior. Errors return `errVertex` or propagate from `ToInput`.

State and persistence: in-memory cached result/error on the async state; `CacheError` is set by `State.Async` in `state.go`. No external persistence.

Dependencies/integration points: `flightcontrol.CachedGroup`, `solver/pb`, digest, and state value lookup/marshal paths.

Risks/test signals: cache key is empty string, so an `asyncState` caches one result independent of constraints passed to `Do`; correctness relies on the state instance being used consistently or callback considering constraints at first resolution. `async_test.go` verifies callbacks are lazy/nonblocking until marshal.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/client/llb/async.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/client/llb/async_test.go -->
# sources/cloud-native/buildkit/client/llb/async_test.go

Purpose: verifies lazy behavior of asynchronous state transforms.

Important APIs/types/functions: `TestAsyncNonBlocking` builds an image state, adds a blocking async transform, chains another run, releases the wait channel only before marshal, and inspects generated protobuf operations.

Control flow: after creating the async chain, the test confirms the callback has not run within 100ms. It then marshals, checks graph length and final pointer, and asserts command/cwd propagation through async result.

State and persistence: uses channels to observe callback execution; no external persistence.

Dependencies/integration points: LLB `Image`, `Dir`, `Async`, `Run`, `Shlex`, marshal, and test helpers `parseDef`/`last`.

Risks/test signals: catches eager async execution and metadata propagation regressions. It does not cover error caching or constraints-sensitive async behavior.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/client/llb/async_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/client/llb/definition.go -->
# sources/cloud-native/buildkit/client/llb/definition.go

Purpose: reconstructs an LLB vertex graph from a marshaled protobuf definition, allowing definitions received over the wire to become `State`/`Output` objects again.

Important APIs/types/functions: `DefinitionOp` implements `Vertex` and stores digest-indexed ops, raw definition bytes, metadata, source locations, platform map, current digest/index, and a shared input cache. `NewDefinitionOp` parses `pb.Definition`, reconstructs source maps, finds the terminal pointer input, and initializes metadata. Methods implement validation, marshaling, output creation, and input traversal.

Control flow: constructor unmarshals every op into maps keyed by digest, extracts platform specs, reconstructs nested source-map states via recursive `NewDefinitionOp`, then treats the last pointer op as the selected output digest/index. `Marshal` validates and returns original bytes/metadata for the current digest. `Inputs` walks protobuf inputs, reusing cached child `DefinitionOp`s per digest/output index to preserve graph identity and reduce duplicate traversal.

State and persistence: all state is in-memory maps shared between child definition ops. `inputCache` is a synchronized map to support parallel graph walks; `mu` protects map access and current op reads.

Dependencies/integration points: `pb.Definition`, `pb.Op`, source maps, platform metadata, deterministic digest calculation, and `NewState(op.Output())` consumers.

Risks/test signals: malformed definitions can panic if assumptions about final pointer inputs are violated, though nil definitions and missing maps are handled by errors. Shared map mutation requires careful locking. `definition_test.go` checks equivalence, input-cache vertex count, nil input errors, and parallel walk safety.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/client/llb/definition.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/client/llb/definition_test.go -->
# sources/cloud-native/buildkit/client/llb/definition_test.go

Purpose: regression tests for round-tripping marshaled definitions back into LLB states.

Important APIs/types/functions: `TestDefinitionEquivalence` covers scratch, image, exec, local, git, HTTP, file op, platform constraints, and mounts. `TestDefinitionInputCache` checks shared input caching and parallel traversal. `TestDefinitionNil` verifies nil input errors. `testParallelWalk` recursively traverses inputs with errgroup.

Control flow: each state is marshaled, converted to `DefinitionOp`, validated, converted back to state, marshaled again, and compared byte-for-byte plus metadata and platform. Cache test builds shared HTTP inputs through multiple mounts, verifies vertex count, then creates a large graph and recursively walks in parallel.

State and persistence: in-memory graph definitions only.

Dependencies/integration points: `NewDefinitionOp`, `NewState`, marshal helpers, `errgroup`, platform normalization, and digest metadata.

Risks/test signals: strong signal for deterministic roundtrip and race safety. It does not cover corrupted non-nil definitions with missing final inputs or malformed source location indexes beyond constructor checks.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/client/llb/definition_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/client/llb/diff.go -->
# sources/cloud-native/buildkit/client/llb/diff.go

Purpose: implements LLB diff operations, producing a state that represents changes from a lower state to an upper state.

Important APIs/types/functions: `DiffOp` implements `Vertex` with lower/upper outputs, constraints, output, and marshal cache. `NewDiff` creates the op and requires `pb.CapDiffOp`. `Diff` is the public helper that optimizes scratch cases.

Control flow: `Marshal` returns cached data when possible, marshals constraints without platform because diff is not platform-specific, assigns lower and upper input indexes or `pb.Empty`, serializes a `pb.DiffOp`, and stores it in cache. Public `Diff` returns scratch for scratch/scratch, upper for scratch/upper, otherwise creates a diff output attached to lower.

State and persistence: in-memory marshal cache only.

Dependencies/integration points: solver protobuf `DiffOp`, capability metadata, `Merge` workflows, and state/output conversion.

Risks/test signals: `Validate` is currently no-op, so invalid combinations depend on marshal/input errors or solver-side validation. Scratch shortcut semantics are important for callers. No direct test in this subset, but merge examples and compatibility use diff/merge behavior indirectly.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/client/llb/diff.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/client/llb/exec.go -->
# sources/cloud-native/buildkit/client/llb/exec.go

Purpose: core implementation of LLB exec operations and their public run/mount/secret/SSH/CDI/cache/network/security option APIs.

Important APIs/types/functions: `ExecOp` implements `Vertex`; `mount` stores target/source/output and mount options; `NewExecOp` creates the root mount; `AddMount`, `GetMount`, `Validate`, `Marshal`, `Inputs`, and `getMountIndexFn` manage graph behavior. Public option APIs include `Shlex`, `Args`, `AddMount`, `Readonly`, `SourcePath`, `AsPersistentCacheDir`, `Tmpfs`, `AddSecret`, `SecretAsEnv`, `AddSSHSocket`, `AddCDIDevice`, `WithProxy`, `ReadonlyRootFS`, `ValidExitCodes`, network/security constants, cache-sharing constants, ulimit names, and content-cache options.

Control flow: `State.Run` builds `ExecInfo`, creates `ExecOp`, adds requested mounts, secrets, SSH, and CDI devices. `Validate` requires args and working directory and validates mount sources. `Marshal` sorts mounts by target for deterministic output, gathers environment/cwd/user/hostname/cgroup/extra hosts/ulimits/valid exits/network/security/platform from state metadata, applies default PATH behavior based on cap negotiation, adds capability requirements for every used feature, deduplicates equal protobuf inputs, assigns output indexes only to writable non-cache non-tmpfs mounts, appends secret/SSH mounts, serializes deterministically, and caches by constraints pointer.

State and persistence: state is immutable at the public `State` layer but `ExecOp` mutates internal mount slices, constraint capability metadata, SSH target defaults, validation flag, and marshal cache. Persistent cache mounts are represented by `cacheID` and sharing mode but actual persistence is managed by BuildKit daemon workers.

Dependencies/integration points: `solver/pb` exec/mount/metadata capabilities, `system.DefaultPathEnv`, state metadata from `meta.go`, constraints from `state.go`, `MarshalCache`, BuildKit secret/SSH/CDI execution support, and solver-side mount semantics.

Risks/test signals: deterministic sorting is critical because mount order affects output indexes; mutating constraints and SSH targets during marshal makes concurrency/cache behavior sensitive. Background cache keyed by constraints pointer can miss equivalent constraints or reuse after mutation. Tmpfs and no-output mounts intentionally cannot be used as parent outputs. Tests in `exec_test.go` cover tmpfs errors, mount index stability with sorted tmpfs, Linux resource metadata/cache behavior, resource merging, and marshal determinism.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/client/llb/exec.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/client/llb/exec_test.go -->
# sources/cloud-native/buildkit/client/llb/exec_test.go

Purpose: regression tests for exec operation mount validation, output index stability, Linux resource metadata, and deterministic marshaling.

Important APIs/types/functions: `TestTmpfsMountError`, `TestValidGetMountIndex`, `TestLinuxResourcesMarshal`, `TestLinuxResourcesNotInCacheKey`, `TestLinuxResourcesMerge`, and `TestExecOpMarshalConsistency`.

Control flow: tests build LLB states with exec options, marshal them, inspect protobuf definitions/metadata, and compare repeated marshals. Tmpfs tests distinguish using tmpfs output as parent, valid scratch tmpfs mount, and invalid tmpfs with non-scratch source. Mount-index test verifies sorted tmpfs mounts do not shift writable mount output indexes. Resource tests verify `OpMetadata.LinuxResources` and that resources do not alter op bytes/cache key.

State and persistence: in-memory marshaled definitions only.

Dependencies/integration points: exec options, file ops for mount sources, protobuf metadata, and parse helpers.

Risks/test signals: strong coverage for subtle deterministic-index and cache-key behavior. It does not cover all secrets, SSH, CDI, network, security, proxy, or cache mount modes.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/client/llb/exec_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/client/llb/fileop.go -->
# sources/cloud-native/buildkit/client/llb/fileop.go

Purpose: implements LLB file operations and fluent `FileAction` builders for directory creation, file creation, symlinks, removals, and copies.

Important APIs/types/functions: `NewFileOp` binds actions to a base state. `FileAction` chains actions through `prev`, supports `Mkdir`, `Mkfile`, `Symlink`, `Rm`, `Copy`, `WithState`, and output discovery. Action implementations include `fileActionMkdir`, `fileActionMkfile`, `fileActionSymlink`, `fileActionRm`, and `fileActionCopy`. Option structures include `MkdirInfo`, `MkfileInfo`, `SymlinkInfo`, `RmInfo`, `CopyInfo`, `ChownOpt`, `ChmodOpt`, and `CreatedTime`. `marshalState` linearizes action graphs and assigns base/primary/secondary/relative inputs.

Control flow: public helpers build immutable-looking linked action nodes. `State.File` binds an action chain to a state and creates a `FileOp`. During marshal, file op validates action presence, derives platform from base but clears platform on the file op itself, collects all input outputs, recursively adds action states, deduplicates protobuf inputs, converts each action to protobuf with normalized paths and owner/timestamp data, assigns skipped output to intermediate actions and output zero to the final action, serializes deterministically, and caches.

State and persistence: no external persistence; file changes are declarative LLB actions executed by solver workers. Internally, `FileAction.bind` shallow-copies chains with bound state; `marshalState` tracks visited actions to avoid duplicate action expansion; `FileOp` stores marshal cache and validation state.

Dependencies/integration points: state metadata for working directories/platforms, solver protobuf file actions, capabilities for symlink/copy patterns/required paths/replace/mode string, `path` normalization, and file/action tests.

Risks/test signals: capability detection currently iterates `state.actions` before `state.add(f.action, c)`, so cap adders may not be applied at that moment; solver compatibility for newer file features depends on correct caps. `fileActionCopy.addCaps` dereferences `a.info.Mode.ModeStr` without nil guarding, though the method is only useful when reached. Path normalization and relative action indexes are subtle. Extensive tests in `fileop_test.go` cover action shapes, owner handling, timestamps, action-copy pipelines, deterministic marshaling, and parallel marshaling.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/client/llb/fileop.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/client/llb/fileop_test.go -->
# sources/cloud-native/buildkit/client/llb/fileop_test.go

Purpose: comprehensive unit tests for LLB file action marshaling.

Important APIs/types/functions: tests cover mkdir, chained mkdir/mkfile/rm/symlink, copy from states and action outputs, multi-stage file pipelines, owner parsing by name/root/UID/GID, created timestamps, deterministic marshal, and parallel marshal. Helpers `parseDef` and `last` decode protobuf definitions and final pointer ops.

Control flow: each test builds a state, marshals it, decodes ops into digest maps and ordered arrays, then asserts input indexes, secondary inputs, action outputs, normalized paths, mode/timestamp/owner fields, source identifiers, and graph length.

State and persistence: no external persistence. Parallel marshal test exercises shared marshal cache locking.

Dependencies/integration points: `pb.FileOp`, image/source ops, digest calculation, `errgroup`, and fileop public APIs.

Risks/test signals: strong signal for wire-format stability and deterministic graph generation. Tests would catch many path/index regressions but currently may not catch missing cap metadata for advanced copy/symlink features.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/client/llb/fileop_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/client/llb/git_test.go -->
# sources/cloud-native/buildkit/client/llb/git_test.go

Purpose: verifies git source identifier and attribute generation.

Important APIs/types/functions: `TestGit` table-tests `Git` with fragment refs, subdirs, option overrides, bundle URLs, OCI-layout bundle store settings, and checkout bundle mode.

Control flow: each case marshals the state, expects a two-op definition, locates the source op via final pointer, and compares the exact source identifier and attrs map.

State and persistence: no live git network access; source ops are declarative.

Dependencies/integration points: `Git`, `GitRef`, `GitSubDir`, `GitChecksum`, `GitBundleURL`, `GitBundleOCIStore`, `GitCheckoutBundle`, protobuf source attrs.

Risks/test signals: protects canonical URL/id construction and attribute compatibility. It does not exercise SSH known-host keyscan or actual git fetch behavior.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/client/llb/git_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/client/llb/imagemetaresolver/resolver.go -->
# sources/cloud-native/buildkit/client/llb/imagemetaresolver/resolver.go

Purpose: default client-side image metadata resolver for LLB image states, resolving image config bytes and digests from registries.

Important APIs/types/functions: `WithDefault` is an image option that attaches `Default()` resolver. `New` creates an `imageMetaResolver` with Docker resolver, BuildKit user-agent, content buffer, cache, locker, and optional default platform. `Default` uses `sync.Once`. `ResolveImageConfig` resolves config via `imageutil.Config`, caches by ref plus platform, and serializes concurrent same-ref resolution with a locker.

Control flow: resolution starts a tracing span, locks by ref, chooses platform from resolver default or request option, checks cache, calls registry image config resolution, stores digest/config, and returns the original ref plus resolved digest/config.

State and persistence: in-memory singleton cache for `Default` and per-resolver cache map. No disk persistence.

Dependencies/integration points: containerd remotes/docker resolver, BuildKit content buffer, imageutil, tracing, version user-agent, `llb.ImageMetaResolver`, and source resolver options.

Risks/test signals: cache key appends `platforms.FormatAll` without separator, which is probably acceptable but worth awareness. Lock is by ref only, so concurrent different-platform resolutions for same ref serialize. Default resolver has process-wide cache. No direct tests in this file; `resolver_test.go` covers the LLB resolver interface with a fake resolver.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/client/llb/imagemetaresolver/resolver.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/client/llb/llbbuild/llbbuild.go -->
# sources/cloud-native/buildkit/client/llb/llbbuild/llbbuild.go

Purpose: defines an LLB `BuildOp` wrapper that invokes the LLB builder on an input definition source.

Important APIs/types/functions: `Build` returns a `StateOption` that replaces state output with a build op. `NewBuildOp` creates a `build` vertex from a source output and options. `build` implements both `llb.Vertex` and `llb.Output` methods. `BuildInfo`, `WithFilename`, and `WithConstraints` configure definition filename and constraints.

Control flow: marshal builds a `pb.BuildOp` with builder `pb.LLBBuilder`, maps `pb.LLBDefinitionInput` to input 0, optionally sets `pb.AttrLLBDefinitionFilename`, adds `CapBuildOpLLBFileName`, marshals constraints, converts the source output to an input, appends it, serializes the op, and caches it.

State and persistence: in-memory marshal cache only. The build op represents solver-side nested build execution rather than local persistence.

Dependencies/integration points: `llb.StateOption`, `llb.Output`, `llb.MarshalConstraints`, solver `pb.BuildOp`, capabilities, and definition-file attribute.

Risks/test signals: `Validate` is no-op and `NewBuildOp` accepts nil source, so nil source would fail during marshal. It uses non-deterministic `pop.Marshal()` rather than `deterministicMarshal`, though fields are small and test covers expected shape. `llbbuild_test.go` checks marshaled build op fields.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/client/llb/llbbuild/llbbuild.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/client/llb/llbbuild/llbbuild_test.go -->
# sources/cloud-native/buildkit/client/llb/llbbuild/llbbuild_test.go

Purpose: validates marshaling of `llbbuild` build operations.

Important APIs/types/functions: `TestMarshal` uses `NewBuildOp` with `WithFilename`, decodes a protobuf op, and checks digest, input count, builder kind, build input mapping, and filename attr. `dummyOutput` supplies a fixed `pb.Input`.

Control flow: create build op, marshal with empty constraints, verify digest equals bytes digest, unmarshal bytes into `pb.Op`, then inspect `BuildOp` fields.

State and persistence: no persistence; dummy output avoids a real LLB graph.

Dependencies/integration points: `llb.Constraints`, `pb.BuildOp`, OpenContainers digest, and `testify/require`.

Risks/test signals: confirms basic wire shape. It does not test `Build` as a `StateOption`, constraints merging, nil source errors, or deterministic repeated marshals.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/client/llb/llbbuild/llbbuild_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/client/llb/llbtest/platform_test.go -->
# sources/cloud-native/buildkit/client/llb/llbtest/platform_test.go

Purpose: tests platform propagation through LLB source, exec, file, merge, mount, and marshal-capability paths by loading definitions through the solver.

Important APIs/types/functions: `TestCustomPlatform`, `TestDefaultPlatform`, `TestPlatformOnMarshal`, `TestPlatformMixed`, and `TestFallbackPath`. Helpers inspect solver edges, protobuf ops, parent edges, mount edges, source IDs, exec args, and environment variables.

Control flow: tests build LLB graphs with explicit per-state platforms, default platforms, marshal-time platforms, mixed-platform mounts, and cap-dependent PATH behavior; marshal definitions; load them with `llbsolver.Load`; traverse loaded solver edges; assert platform and metadata results.

State and persistence: in-memory definitions and solver edge graphs only.

Dependencies/integration points: `llbsolver.Load`, solver edges, `containerd/platforms`, `system.DefaultPathEnvUnix`, exec PATH cap negotiation in `exec.go`, and platform propagation in `state.go`/`source.go`.

Risks/test signals: strong signal for cross-platform graph correctness and default PATH compatibility. It does not execute the graph, but validates solver interpretation of marshaled definitions.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/client/llb/llbtest/platform_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/client/llb/marshal.go -->
# sources/cloud-native/buildkit/client/llb/marshal.go

Purpose: shared definition serialization, constraint merging, metadata conversion, marshal caching, and deterministic protobuf marshaling helpers.

Important APIs/types/functions: `Definition` wraps op bytes, metadata, source maps, and constraints. `ToPB`, `FromPB`, `Head`, `WriteTo`, and `ReadFrom` bridge client and protobuf definitions. `MarshalConstraints` merges base/override constraints and emits `pb.Op` plus metadata. `MarshalCache` and `MarshalCacheInstance` cache per-constraints marshal results behind a mutex. `deterministicMarshal` uses deterministic protobuf serialization.

Control flow: definitions convert metadata key types between digest and string. `Head` parses the final pointer op and returns its first input digest. `MarshalConstraints` clones worker constraints, applies override platform/worker constraints/metadata, defaults platform when missing, and returns an op with platform and worker filters. Cache `Acquire` locks, `Load` looks up by constraints pointer, `Store` hashes bytes and records result, `Release` unlocks.

State and persistence: no external persistence except `WriteTo`/`ReadFrom` caller-provided streams. Marshal cache is in-memory and keyed by `*Constraints` identity rather than deep equality.

Dependencies/integration points: protobuf definition/op metadata, containerd platform defaults, digest, BuildKit metadata caps, and every vertex marshal implementation.

Risks/test signals: pointer-keyed cache means equivalent constraints objects do not share cache and mutated constraints under same pointer can reuse stale results. `ReadFrom` reads full stream into memory. Many tests in this subset implicitly verify deterministic byte output and definition roundtrip behavior.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/client/llb/marshal.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/client/llb/merge.go -->
# sources/cloud-native/buildkit/client/llb/merge.go

Purpose: implements LLB merge operations that overlay multiple states into one state, commonly combined with `Diff`.

Important APIs/types/functions: `MergeOp` implements `Vertex`; `NewMerge` builds inputs and output; `Validate` requires at least two inputs; `Marshal` serializes `pb.MergeOp`; public `Merge` filters scratch inputs and applies capability `pb.CapMergeOp`.

Control flow: `Merge` removes scratch inputs, returns scratch for none, returns the single non-empty input unchanged for one, otherwise builds constraints, adds merge cap, and creates a merge output attached to the first input. Marshal validates, clears platform because merge is not platform-specific, appends each input as a protobuf input and merge input index, serializes deterministically, and caches.

State and persistence: in-memory marshal cache only; merged filesystem semantics are solver-side.

Dependencies/integration points: `Diff`, solver `pb.MergeOp`, capability metadata, and platform propagation tests.

Risks/test signals: merge order matters for overlay semantics and cache keys. `Validate` catches direct `NewMerge` misuse with less than two inputs; public helper optimizes those cases. `merge_test.go` covers scratch/single-input behavior.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/client/llb/merge.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/client/llb/merge_test.go -->
# sources/cloud-native/buildkit/client/llb/merge_test.go

Purpose: verifies public `Merge` shortcut behavior for scratch and single-input cases.

Important APIs/types/functions: `TestScratchMerge` checks nil/empty/scratch-only merges, single non-empty input, scratch mixed with one input, and scratch mixed with two non-empty inputs.

Control flow: calls `Merge` with different slices and asserts output nil, equality with original input output, or distinct merge output.

State and persistence: none beyond in-memory states.

Dependencies/integration points: `Scratch`, `Image`, and `Merge`.

Risks/test signals: protects API behavior that avoids unnecessary merge ops. It does not validate actual `pb.MergeOp` marshaling for multi-input non-scratch merges.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/client/llb/merge_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/client/llb/meta.go -->
# sources/cloud-native/buildkit/client/llb/meta.go

Purpose: implements state metadata options and accessors for environment, working directory, user, args, platform, extra hosts, ulimits, cgroup parent, Linux resources, network, security, and environment list behavior.

Important APIs/types/functions: state options include `AddEnv`, `AddEnvf`, `Dir`, `Dirf`, `User`, `Reset`, `Hostname`, `Network`, `Security`, plus internal `args`, `shlexf`, `platform`, `extraHost`, `ulimit`, and `cgroupParent`. Getter factories retrieve typed values from state chains. `LinuxResources` is a public resource-limit struct. `EnvList` is a persistent linked environment list with add/replace/default/delete/get/keys/to-array behavior.

Control flow: state options wrap previous state with a lazy value function. Relative `Dir` resolves against previous directory at lookup time and normalizes through `path.Join`. Environment additions build an `EnvList` chain; `makeValues` walks from newest to oldest, records first non-deleted value, reverses keys to preserve final order, and memoizes using `sync.Once`.

State and persistence: metadata lives in immutable `State` value chains and is evaluated lazily with constraints. `EnvList` memoizes computed maps/slices in memory. No external persistence.

Dependencies/integration points: used heavily by `exec.go`, `fileop.go`, `state.go`, image config application, platform tests, and shlex parsing. Network/security values are solver protobuf enums.

Risks/test signals: `shlexf` ignores split errors, which can silently produce nil args and later exec validation errors. `Dir` closure mutates captured `value` when resolving relative paths, making repeated/concurrent lookups subtle. `EnvList.Delete` returns a value not pointer, so call sites need care. Tests cover relative working directory normalization through `meta_test.go`.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/client/llb/meta.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/client/llb/meta_test.go -->
# sources/cloud-native/buildkit/client/llb/meta_test.go

Purpose: tests working directory normalization for relative and absolute `Dir` updates.

Important APIs/types/functions: `TestRelativeWd` chains `Scratch().Dir(...)` calls and uses `getDirHelper` to retrieve the current directory.

Control flow: asserts `foo` becomes `/foo`, `bar` appends, `..` resolves upward, absolute `/baz` replaces, and excessive `../../..` clamps to `/`.

State and persistence: no persistence; state metadata only.

Dependencies/integration points: `Scratch`, `State.Dir`, `State.GetDir`, and internal `getDir`.

Risks/test signals: protects path normalization semantics. It does not cover environment list ordering/deletion, shlex errors, user, network, security, ulimit, or resource metadata.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/client/llb/meta_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/client/llb/passthrough.go -->
# sources/cloud-native/buildkit/client/llb/passthrough.go

Purpose: implements passthrough LLB operations used to express dependencies/requirements while forwarding selected input outputs.

Important APIs/types/functions: `PassthroughInput` marks a state and whether it should be an output. `PassthroughOp` stores ID, input outputs, output map, constraints, and output objects. `NewPassthroughOp`, `NewPassthrough`, `Validate`, `Marshal`, `Output`, `OutputAt`, and `Inputs` define behavior.

Control flow: constructor filters scratch inputs, records all non-empty inputs, and creates output objects for inputs marked `Output`. Validation requires at least one input, a non-empty ID, at least one output, and valid output-map indexes. Marshal adds `CapPassthroughOp`, marshals constraints without platform, converts inputs to protobuf inputs, records output indexes, serializes deterministically, and caches.

State and persistence: in-memory op and marshal cache only; dependency semantics are solver-side.

Dependencies/integration points: `State.Requires` in `state.go`, solver `pb.PassthroughOp`, constraints/caps, and tests.

Risks/test signals: output closures capture `outputIndex` per loop with short declaration, which is safe in current Go semantics but worth preserving. Invalid `OutputAt` returns an output that fails later, making errors lazy. Tests cover requires, multiple outputs, no dependency shortcut, metadata preservation, and empty ID errors.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/client/llb/passthrough.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/client/llb/passthrough_test.go -->
# sources/cloud-native/buildkit/client/llb/passthrough_test.go

Purpose: unit tests for passthrough and `State.Requires` behavior.

Important APIs/types/functions: `TestPassthroughRequiresMarshal`, `TestPassthroughMultipleOutputsMarshal`, `TestPassthroughRequiresNoDeps`, `TestPassthroughRequiresPreservesMetadata`, `TestPassthroughEmptyID`, and helpers to find passthrough vertices.

Control flow: tests build image states with requires or explicit passthrough ops, marshal definitions, locate passthrough protobuf ops, and assert input counts, IDs, output maps, absence when no deps, state metadata preservation, and error on empty ID.

State and persistence: no external persistence.

Dependencies/integration points: `Image`, `Requires`, `NewPassthroughOp`, `NewState`, protobuf decoding, and `Dir` metadata.

Risks/test signals: validates core dependency-only graph behavior. It does not cover invalid output indexes directly or solver execution semantics.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/client/llb/passthrough_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/client/llb/resolver.go -->
# sources/cloud-native/buildkit/client/llb/resolver.go

Purpose: defines image metadata resolver options for LLB image sources.

Important APIs/types/functions: `WithMetaResolver` attaches an `ImageMetaResolver` to `ImageInfo`. `ResolveDigest` controls whether resolver output should rewrite image refs to digest-pinned refs. `WithLayerLimit` and `WithImageChecksum` set image source attrs. `ImageMetaResolver` aliases `sourceresolver.ImageMetaResolver`.

Control flow: these are option setters consumed by `Image` in `source.go`; actual resolution happens asynchronously during state marshal/value lookup.

State and persistence: options mutate per-image `ImageInfo` during state construction; no persistence here.

Dependencies/integration points: `source.go` image construction, sourceresolver interfaces, digest attrs, and image meta resolver implementations.

Risks/test signals: option combinations affect source identity and cache safety. `resolver_test.go` covers metadata resolver invocation and digest-pinning behavior.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/client/llb/resolver.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/client/llb/resolver_test.go -->
# sources/cloud-native/buildkit/client/llb/resolver_test.go

Purpose: tests image metadata resolver integration with image states.

Important APIs/types/functions: `TestImageMetaResolver`, `TestImageResolveDigest`, and fake `testResolver.ResolveImageConfig`.

Control flow: fake resolver returns config JSON with a working directory and digest. First test verifies resolver laziness before marshal, platform propagation from marshal constraints, source identifier without digest rewrite, and state directory from image config. Second test enables `ResolveDigest(true)` and verifies source identifier includes the resolved digest.

State and persistence: fake resolver records called/platform fields in memory.

Dependencies/integration points: `Image`, `WithMetaResolver`, `ResolveDigest`, `WithImageConfig`, source resolver opts, platform formatting.

Risks/test signals: catches resolver platform propagation and digest pinning regressions. Fake config omits broader image config fields, so env/user behavior is not covered here.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/client/llb/resolver_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/client/llb/source.go -->
# sources/cloud-native/buildkit/client/llb/source.go

Purpose: implements LLB source operations and public constructors/options for image, image blob, OCI layout blob, git, scratch, local directories, OCI layouts, HTTP downloads, auth, headers, checksums, file metadata, and capability annotation.

Important APIs/types/functions: `SourceOp` implements `Vertex` for source identifiers/attrs. Constructors include `ImageBlob`, `OCILayoutBlob`, `Image`, `Git`, `Scratch`, `Local`, `OCILayout`, and `HTTP`. Option types include `ImageOption`, `GitOption`, `LocalOption`, `OCILayoutOption`, `HTTPOption`, `FileInfoOption`, `AuthOption`, and bundle/image/blob/store helpers. `GitInfo`, `LocalInfo`, `HTTPInfo`, `OCILayoutInfo`, and `ImageBlobInfo` hold option state. `platformSpecificSource` and `addCap` control platform/cap metadata.

Control flow: each constructor parses/normalizes inputs, populates protobuf source attrs, adds required capabilities, creates a `SourceOp`, and returns a `State`. Image sources normalize references, set resolve mode/layer/checksum attrs, and optionally wrap in `Async` to resolve image config and optionally digest-pin the ref. Git sources parse URLs, support old fragment `ref:subdir`, canonicalize IDs independent of protocol where possible, set auth defaults, handle SSH known-hosts and socket attrs, bundle/import/export attrs, checksum/fetch flags, and source caps. Local and HTTP sources serialize patterns/headers/signatures and file metadata attrs.

State and persistence: source ops are declarative; external persistence lives in registries, local session transfers, git remotes, OCI layout stores, HTTP endpoints, and BuildKit worker caches. `SourceOp.Marshal` mutates local source attrs to add unique ID when no session ID exists. Image async resolution can cache through the async state/resolver.

Dependencies/integration points: distribution/reference parsing, BuildKit protobuf source attrs/caps, gitutil, sshutil keyscan, sourceresolver, image metadata resolver options, constraints, local session IDs, HTTP auth secret conventions, and tests for git/image blob/source/platform behavior.

Risks/test signals: many string attrs form public wire contracts. Image digest pinning is important for cache safety with mutable tags. `OCIChecksum` sets a field that is not currently emitted to attrs in this file, which may be intentional gap or pending feature. Git SSH keyscan is best-effort network work during graph construction. JSON pattern marshal errors are ignored. Tests cover git attrs, invalid image blob refs, OCI blob attrs, image resolver behavior, platform propagation, and source maps.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/client/llb/source.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/client/llb/sourcemap.go -->
# sources/cloud-native/buildkit/client/llb/sourcemap.go

Purpose: attaches source-code location metadata to LLB vertices so solver errors can point back to frontend source files and ranges.

Important APIs/types/functions: `SourceMap` stores optional state/definition, filename, language, and source data. `NewSourceMap` constructs it. `Location` returns a constraints option adding a `SourceLocation`. `equalSourceMap` deduplicates source maps. `sourceMapCollector` accumulates maps and digest-to-location mappings and marshals to `pb.Source`.

Control flow: frontend code creates a source map and passes `Location` as a constraints option. During state marshal, vertices return source locations; the collector deduplicates source maps by pointer or structural equality, later marshals each source map, recursively marshaling attached state if needed, and emits `pb.SourceInfo` plus per-digest locations.

State and persistence: source map definitions are cached in the `SourceMap.Definition` field after first marshal. Collector state is per-definition marshal.

Dependencies/integration points: `state.go` marshal flow, protobuf source/range structures, frontend error reporting, and source-map tests in `state_test.go`.

Risks/test signals: `equalSourceMap` accesses the last definition entry when both definitions are non-nil and one length is zero because its length check uses `&&`; this could panic for empty definitions. Recursive state marshaling can be expensive. Tests cover deduplication and multiple ranges but not empty-definition equality edge cases.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/client/llb/sourcemap.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/client/llb/sourceresolver/imageresolver.go -->
# sources/cloud-native/buildkit/client/llb/sourceresolver/imageresolver.go

Purpose: adapts a generic source metadata resolver into the `llb.ImageMetaResolver` interface used by image states.

Important APIs/types/functions: `ImageMetaResolver` interface declares `ResolveImageConfig`. `NewImageMetaResolver` wraps a `MetaResolver`. Internal `imageMetaResolver.ResolveImageConfig` constructs a `pb.SourceOp`, calls `ResolveSourceMetadata`, validates image metadata, and returns resolved ref/digest/config.

Control flow: input ref is normalized with distribution/reference. Default source identifier is `docker-image://<ref>`; if `OCILayoutOpt` is present, identifier becomes `oci-layout://<ref>` and OCI session/store attrs are set. The metadata resolver may rewrite the op; the wrapper strips docker/OCI prefixes from the returned identifier and returns image digest/config, or returns `ResolveToNonImageError` if metadata is not image data.

State and persistence: no local persistence; delegates to supplied `MetaResolver`.

Dependencies/integration points: generic solver source metadata resolution, source policies/options, OCI layout resolver options, and image state async config resolution.

Risks/test signals: assumes returned identifiers use known prefixes. Non-image responses are converted to a typed imageutil error. No direct test in this subset; exercised indirectly where frontends use metadata resolvers.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/client/llb/sourceresolver/imageresolver.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/client/llb/sourceresolver/types.go -->
# sources/cloud-native/buildkit/client/llb/sourceresolver/types.go

Purpose: type definitions for source metadata resolver requests and responses across image, OCI layout, git, and HTTP sources.

Important APIs/types/functions: `ResolverType`, `MetaResolver`, `Opt`, `MetaResponse`, `ResolveImageOpt`, `ResolveImageResponse`, `AttestationChain`, `Blob`, `ResolveGitOpt`, `ResolveGitResponse`, `ResolveHTTPOpt`, checksum request/response types, `ResolveOCILayoutOpt`, and `ResolveImageConfigOptStore`.

Control flow: no executable flow; structs are populated by callers and resolver implementations.

State and persistence: no internal state. `Opt` can carry source policies, platform, resolve modes, attestation requests, OCI store IDs, git return-object flags, and HTTP checksum requests.

Dependencies/integration points: solver `pb.SourceOp`, source policy protobuf, OCI descriptors/digests/platforms, and resolver implementations such as `imageresolver.go`.

Risks/test signals: these structs are cross-package contracts; field changes affect frontends, resolver implementations, and client image metadata flows. No direct tests in this subset.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/client/llb/sourceresolver/types.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/client/llb/state.go -->
# sources/cloud-native/buildkit/client/llb/state.go

Purpose: central public LLB state graph API, including immutable state chaining, graph marshaling, output/input/vertex interfaces, constraints, metadata options, and platform/resource helpers.

Important APIs/types/functions: `State`, `Output`, `Vertex`, `StateOption`, `Constraints`, `ConstraintsOpt`, `OpMetadata`, `NewState`, `NewConstraints`, `Marshal`, recursive `marshal`, `Run`, `File`, metadata getters/setters, `Requires`, `WithOutput`, `WithImageConfig`, `output.ToInput`, constraints option adapters, metadata merge/conversion, platform constants, `Require`, cache export controls, progress group, Linux resource options, and local unique ID.

Control flow: `NewState` initializes output, root dir, and platform from output. State options build linked value chains. `Marshal` creates constraints, recursively marshals vertex inputs with duplicate digest and vertex caches, adds a final pointer op to selected output, records root metadata caps, and serializes source maps. `Run`, `File`, and `Requires` construct exec, file, and passthrough vertices. Constraint options implement multiple option interfaces so the same option can apply to runs and sources.

State and persistence: states are value chains with pointers to previous states and optional async state; public operations return new states. Constraints include generated `LocalUniqueID`, platform, worker filters, metadata, caps, and source locations. Marshal caches live in individual vertices; no external persistence.

Dependencies/integration points: every LLB operation file, protobuf solver APIs, platform normalization, identity generation, source maps, image config JSON, API caps, and solver consumers.

Risks/test signals: recursive marshal can be sensitive to vertex identity and digest cache ordering. `Validate` assumes output/vertex are non-nil. Metadata merge overwrites several fields such as progress group and Linux resources. Linux resources intentionally live in metadata, not op bytes. Tests in `state_test.go`, `llbtest/platform_test.go`, `exec_test.go`, and many fileop tests cover platform, source maps, metadata, resources, and deterministic definitions.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/client/llb/state.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/client/llb/state_test.go -->
# sources/cloud-native/buildkit/client/llb/state_test.go

Purpose: tests state metadata, image/blob source validation, source-map marshaling, and platform propagation across state graph operations.

Important APIs/types/functions: `TestStateMeta`, `TestFormattingPatterns`, `TestImageBlobInvalid`, `TestImageBlobSource`, `TestOCILayoutBlobSource`, `TestStateSourceMapMarshal`, `TestPlatformFromImage`, `TestPlatformFromImageWithMerge`, and helper `getEnvHelper`.

Control flow: tests build states, query metadata, marshal definitions, decode protobuf ops, inspect source identifiers/attrs/source maps/platforms, and compare expected graph shapes. Source-map test checks deduplication and range ordering across repeated maps and merge. Platform tests verify file ops are platform-neutral while image/exec inherit correct platform through copy and merge graphs.

State and persistence: in-memory state graphs and protobuf definitions only.

Dependencies/integration points: image/blob constructors, OCI blob store attrs, source maps, merge/file/exec/image sources, platform constraints, parse helpers, and metadata getters.

Risks/test signals: good coverage for API-visible metadata and platform behavior. It does not execute graphs or test every source option.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/client/llb/state_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/client/mergediff_linux_test.go -->
# sources/cloud-native/buildkit/client/mergediff_linux_test.go

Purpose: Linux-only filesystem test helpers for merge/diff tests that need FIFOs and character devices.

Important APIs/types/functions: build tag `linux`; `mknod` returns an `fstest.Applier` invoking `unix.Mknod`; `mkfifo` and `mkchardev` specialize it with `S_IFIFO` and `S_IFCHR`.

Control flow: helper joins the requested path under the fstest root and applies the node creation with requested mode/device major/minor.

State and persistence: creates filesystem nodes in temporary test roots when applied.

Dependencies/integration points: containerd continuity `fstest`, `golang.org/x/sys/unix`, and merge/diff tests outside this listed subset.

Risks/test signals: requires Linux privileges/capabilities appropriate for device node creation; failures surface in tests using these appliers. Non-Linux fallback is in `mergediff_nolinux_test.go`.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/client/mergediff_linux_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/client/mergediff_nolinux_test.go -->
# sources/cloud-native/buildkit/client/mergediff_nolinux_test.go

Purpose: non-Linux fallback helpers for merge/diff tests that cannot create FIFOs or character devices.

Important APIs/types/functions: build tag `!linux`; `mkfifo` and `mkchardev` return `fstest.Applier`s that fail with not-implemented errors.

Control flow: applying either helper returns an explicit error instead of attempting unsupported node creation.

State and persistence: no filesystem mutation occurs because appliers fail.

Dependencies/integration points: containerd continuity `fstest`, `pkg/errors`, and platform-agnostic merge/diff tests that can skip or expect unsupported behavior.

Risks/test signals: tests using these helpers must handle the explicit errors on non-Linux. Keeps unsupported behavior visible rather than silently passing.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/client/mergediff_nolinux_test.go -->
