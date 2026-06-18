# subset-b-000208 research

Grouped research report for the requested Moby test utilities, authorization helpers, platform parsers, pidfile/plugin helpers, plugin RPC generator, and plugin transport files. Each section is keyed by original source path for deterministic reconciliation into source-tree-aligned per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/internal/testutil/environment/environment.go -->
# sources/cloud-native/moby/internal/testutil/environment/environment.go

Purpose: defines the `environment.Execution` test-environment snapshot used by Moby integration tests to describe the daemon under test. Important APIs include `New`, `FromClient`, `APIClient`, daemon locality helpers, environment flag helpers, `HasExistingImage`, `EnsureFrozenImagesLinux`, and platform defaults for base image and daemon storage paths. Control flow builds a Docker API client from environment or caller input, pings with API negotiation, reads `/info` and server version, then records daemon info, minimum API version, default path conventions, and protected-element state. State is in-memory except for host environment reads such as `DOCKER_REMOTE_DAEMON`, `DOCKER_ROOTLESS`, `TEST_INTEGRATION_USE_GRAPHDRIVER`, and Windows base-image overrides. Dependencies integrate the Docker client, API `system.Info`, frozen-image loader, and `gotest.tools` assertions. Risks center on interpreting client-host versus daemon-host platform correctly, Windows path conversion, ambiguous image reference filtering, and environment variables silently changing test behavior; test signal is mostly indirect through integration suites that consume `Execution`.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/internal/testutil/environment/environment.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/internal/testutil/environment/protect.go -->
# sources/cloud-native/moby/internal/testutil/environment/protect.go

Purpose: captures pre-existing daemon resources so test cleanup code does not remove containers, images, networks, plugins, or volumes that existed before a suite ran. Important APIs include `ProtectAll`, `ProtectContainer`, `ProtectImage`, `ProtectNetwork`, `ProtectPlugin`, `ProtectVolume`, and the corresponding discovery helpers. Control flow lists daemon resources through the API client, normalizes image tags and digests while ignoring legacy `<none>` placeholders, adds Linux frozen images to protected image names, and stores identifiers in `Execution.protectedElements`. State is in-memory protection maps; persistence is the daemon state being protected from later cleanup. Dependencies include Docker client list APIs, containerd error classification for plugin-list unsupported cases, OpenTelemetry spans, and `testutil.CheckNotParallel`. Risks include stale IDs, daemon API differences, cluster plugin-management restrictions, and tests running in parallel despite shared protection maps. Test signal comes from cleanup behavior in higher-level integration suites rather than direct unit tests.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/internal/testutil/environment/protect.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/internal/testutil/environment/protect_linux.go -->
# sources/cloud-native/moby/internal/testutil/environment/protect_linux.go

Purpose: Linux-specific default bridge protection records and restores the CI daemon's `docker0` bridge addresses after tests that start custom daemons mutate bridge state. Important APIs are `ProtectDefaultBridge`, `Execution.ProtectDefaultBridge`, `getAddrs`, and `restoreDefaultBridge`; `defaultBridgeInfo` stores a netlink link and address map. Control flow finds the bridge, records all addresses, later recreates the bridge if it was deleted, removes newly added non-link-local addresses, and re-adds missing original addresses. State is host network state, not daemon API state, so cleanup has privileged side effects. Dependencies include libnetwork bridge constants, `nlwrap`, `vishvananda/netlink`, Go `maps.Clone`, and IPv6 link-local filtering. Risks are high because failed restore can poison later tests, netlink permissions vary, bridge deletion/recreation is host-invasive, and link-local handling intentionally preserves kernel-generated addresses. Test signal is operational: later networking tests should not inherit broken bridge addresses.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/internal/testutil/environment/protect_linux.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/internal/testutil/environment/protect_others.go -->
# sources/cloud-native/moby/internal/testutil/environment/protect_others.go

Purpose: non-Linux stub for default bridge protection so shared environment code compiles on Windows and other platforms. It defines an empty `defaultBridgeInfo`, a no-op `ProtectDefaultBridge`, and a no-op `restoreDefaultBridge`. Control flow and persistence are intentionally absent because non-Linux test hosts do not manage the Linux `docker0` bridge through this utility. Dependencies are only `context` and `testing`; integration is compile-time through build tags. Risks are low, but callers must not assume bridge restoration happened on non-Linux platforms. Test signal is build coverage across platforms.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/internal/testutil/environment/protect_others.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/internal/testutil/fakecontext/context.go -->
# sources/cloud-native/moby/internal/testutil/fakecontext/context.go

Purpose: creates temporary Docker build contexts for tests. Important APIs are `New`, modifiers `WithFile`, `WithDockerfile`, `WithFiles`, `WithBinaryFiles`, `Fake.Add`, `Fake.Delete`, `Fake.Close`, and `Fake.AsTarReader`. Control flow creates a 0755 temp directory when no directory is supplied, applies modifiers with fatal test failures on error, writes requested files with parent directory creation, deletes paths recursively, and tars the directory through `moby/go-archive`. State is the temporary filesystem tree and optional tar stream. Dependencies are standard filesystem APIs and archive generation. Risks include path traversal through caller-supplied file names, binary buffers being converted through `String`, and callers needing `Close` or test cleanup to remove temp state. Test signal is broad because many build and fake storage tests depend on reproducible context layout.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/internal/testutil/fakecontext/context.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/internal/testutil/fakegit/fakegit.go -->
# sources/cloud-native/moby/internal/testutil/fakegit/fakegit.go

Purpose: builds a throwaway HTTP-served bare Git repository for build-context tests. Important APIs are `FakeGit`, `New`, and `Close`; the local `gitServer` abstraction supports either a local `httptest.Server` or `fakestorage` so the daemon can access the repo on remote test hosts. Control flow creates a fake context, initializes a Git repo, configures identity, commits files, clones it bare into a temp root, runs `git update-server-info`, and exposes `<server>/<name>.git`. State persists in temp directories and an HTTP server until `Close`. Dependencies include the system `git` binary, `fakecontext`, `fakestorage`, and `httptest`. Risks include host Git availability, current working directory mutation, remote daemon reachability, and cleanup on fatal paths; test signal is for Docker build-from-git behavior.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/internal/testutil/fakegit/fakegit.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/internal/testutil/fakestorage/fixtures.go -->
# sources/cloud-native/moby/internal/testutil/fakestorage/fixtures.go

Purpose: builds and protects a tiny `httpserver` image used by remote fake storage when tests need an HTTP file server on the daemon host. The main API is `ensureHTTPServerImage`, guarded by `sync.Once`. Control flow writes a small Go file server, cross-compiles it for the daemon OS/architecture with `CGO_ENABLED=0`, writes a scratch Dockerfile, tars the build context, builds image `httpserver`, drains build output, and marks the image protected. State persists as a daemon image plus temporary build files. Dependencies include the local Go toolchain, `moby/go-archive`, Docker `ImageBuild`, and `testEnv`. Risks include build-tool availability, daemon platform mismatch, hard-coded port 80, and hidden global `testEnv`; test signal is indirect through remote build-context tests.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/internal/testutil/fakestorage/fixtures.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/internal/testutil/fakestorage/storage.go -->
# sources/cloud-native/moby/internal/testutil/fakestorage/storage.go

Purpose: exposes a fake static file server for tests, choosing a local `httptest.Server` when the daemon is local and a daemon-hosted container when the daemon is remote. Important APIs are `SetTestEnvironment`, `New`, the `Fake` interface, `localFileStorage`, and `remoteFileServer`. Control flow creates a fake context, rejects unusable remote/unix-socket setups, serves files locally or builds a container image from the context, starts a container with published port 80, inspects the mapped host port, and returns a reachable URL. State includes temp files, HTTP server, daemon images, daemon containers, and a stored client; `Close` removes container/image and closes the context. Dependencies integrate environment detection, Docker build/container APIs, request daemon host, random names, and network port parsing. Risks include global environment coupling, leaked remote resources on partial failure, host IP selection, and port mapping assumptions. Test signal is high for remote-context build paths.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/internal/testutil/fakestorage/storage.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/internal/testutil/fixtures/load/frozen.go -->
# sources/cloud-native/moby/internal/testutil/fixtures/load/frozen.go

Purpose: ensures the Linux integration suite has a fixed set of small images loaded under expected tags. Important APIs include `FrozenImagesLinux`, `imageExists`, `loadFrozenImages`, `pullImages`, `pullTagAndRemove`, and `readFrozenImageList`. Control flow checks each requested tag, loads all local `/docker-frozen-images` tar contents if present, otherwise parses digest-pinned image refs from the repository Dockerfile and pulls them concurrently, then retags special cases such as `hello-world:frozen`. State is daemon image store state; persistence includes pulled or loaded images and removed source refs. Dependencies include Docker image APIs, external `tar`, repository Dockerfile content, JSON message display, and OpenTelemetry spans. Risks include relying on Dockerfile line format, only returning the first concurrent pull error, local frozen directory drift, and network/pull failures. Test signal is suite startup readiness for image-dependent integration tests.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/internal/testutil/fixtures/load/frozen.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/internal/testutil/fixtures/plugin/basic/basic.go -->
# sources/cloud-native/moby/internal/testutil/fixtures/plugin/basic/basic.go

Purpose: executable fixture for a basic Docker plugin that listens on a Unix socket and serves plugin activation plus likely endpoint behavior used by plugin tests. The main API is the `main` function; it prepares the runtime path, creates a socket, starts an HTTP server, and blocks. State is the plugin socket and serving process inside a plugin rootfs. Dependencies are standard `net`, `net/http`, filesystem, and time packages. Risks include socket path creation, startup timing, platform specificity to Unix sockets, and tests depending on exact fixture routes. Test signal is end-to-end plugin lifecycle and communication behavior when bundled by `fixtures/plugin/plugin.go`.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/internal/testutil/fixtures/plugin/basic/basic.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/internal/testutil/fixtures/plugin/plugin.go -->
# sources/cloud-native/moby/internal/testutil/fixtures/plugin/plugin.go

Purpose: packages, installs, and optionally pushes a test plugin bundle. Important APIs are `Config`, `CreateOpt`, `WithInsecureRegistry`, `WithBinary`, `Create`, `CreateInRegistry`, `makePluginBundle`, and `ensureBasicPluginBin`. Control flow builds or locates the basic plugin binary, assembles a plugin rootfs/config bundle as a tar stream, calls daemon plugin creation, or pushes a plugin to a registry using distribution/registry plumbing. State includes generated plugin bundle data, daemon plugin records, registry contents, and built binaries. Dependencies include `moby/go-archive`, plugin API types, daemon plugin metadata, registry service code, Docker client plugin APIs, and compression. Risks include architecture/OS build compatibility, registry authentication/insecure registry setup, temp bundle cleanup, and tight coupling to daemon plugin internals. Test signal covers plugin install and registry workflows.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/internal/testutil/fixtures/plugin/plugin.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/internal/testutil/helper.go -->
# sources/cloud-native/moby/internal/testutil/helper.go

Purpose: defines the small `HelperT` interface used by test helpers that only need `Helper()`. It avoids requiring a full `testing.TB` when a narrower capability is enough. Control flow and state are absent. Dependencies are none. Risks are minimal; the value is compile-time decoupling of helper annotations from concrete testing types. Test signal is build-time compatibility.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/internal/testutil/helper.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/internal/testutil/helpers.go -->
# sources/cloud-native/moby/internal/testutil/helpers.go

Purpose: provides common test utilities for tracing, command execution, per-test contexts, a zero reader, and parallel-test safety checks. Important APIs include `DevZero`, `ConfigureTracing`, `StartSpan`, `RunCommand`, `GetContext`, `SetContext`, `CleanupContext`, and `CheckNotParallel`. Control flow configures an OTLP HTTP trace exporter once when environment variables request it, starts spans named from tests, stores contexts in a mutex-protected map keyed by testing object, and detects accidental `t.Parallel` by reflecting on private testing state. State includes global tracing initialization and global context map. Dependencies include OpenTelemetry SDK/exporter, containerd logging, `gotest.tools/icmd`, reflection, and environment variables. Risks include reflection against `testing` internals, leaked context map entries without cleanup, tracing exporter endpoint misconfiguration, and global once semantics. Test signal is infrastructure-level across integration tests.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/internal/testutil/helpers.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/internal/testutil/labelstore/memory_label_store.go -->
# sources/cloud-native/moby/internal/testutil/labelstore/memory_label_store.go

Purpose: implements a thread-safe in-memory label store keyed by OCI digests for tests. Important APIs are `InMemory.Get`, `Set`, and `Update`. Control flow locks a mutex, clones maps on reads/writes to avoid caller mutation, replaces labels on `Set`, and merges updates on `Update` while returning the new map. State is a process-local digest-to-label map. Dependencies include `maps.Clone`, `sync`, and `go-digest`. Risks are low; absence of persistence is intentional, but tests depending on insertion order should avoid map ordering. Test signal is for consumers that need deterministic label-store behavior without backing storage.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/internal/testutil/labelstore/memory_label_store.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/internal/testutil/logger.go -->
# sources/cloud-native/moby/internal/testutil/logger.go

Purpose: defines a narrow `Logger` interface with logging methods expected from `testing.T` and asserts `*testing.T` satisfies it. This lets helper packages accept any compatible logger without importing `testing.T` concretely everywhere. Control flow and persistence are absent. Dependencies are the testing package. Risks are minimal; API drift in helper expectations would be caught at compile time. Test signal is build-time.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/internal/testutil/logger.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/internal/testutil/netnsutils/context_unix.go -->
# sources/cloud-native/moby/internal/testutil/netnsutils/context_unix.go

Purpose: Unix test helper for pinning goroutines to OS threads and switching network namespaces safely during tests. Important APIs are `OSContext`, `WithSetNsHandles`, `SetupTestOSContext`, `SetupTestOSContextEx`, `Cleanup`, `restore`, `Set`, and `Go`. Control flow serializes namespace-sensitive tests with a global mutex, captures the original namespace/thread context, creates or opens target namespace handles, uses `runtime.LockOSThread`, `setns`, and cleanup callbacks to restore original state, and offers a `Go` helper that runs functions in the configured context. State includes OS-thread affinity and namespace file descriptors, which are process-global hazards. Dependencies include libnetwork `ns`, `vishvananda/netns`, `unix`, and test logging. Risks are high around failed restore, leaked namespace handles, tests using `t.Parallel`, and platform-specific setns behavior. Test signal is for networking tests that need reliable namespace isolation.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/internal/testutil/netnsutils/context_unix.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/internal/testutil/netnsutils/context_windows.go -->
# sources/cloud-native/moby/internal/testutil/netnsutils/context_windows.go

Purpose: Windows stub for network namespace test-context setup. It exposes `SetupTestOSContext` returning a no-op cleanup function so callers can compile across platforms. Control flow, namespace state, and persistence are intentionally absent. Dependencies are only `testing`. Risks are low, but tests needing real namespace isolation must be build-gated away from Windows. Test signal is compile-time portability.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/internal/testutil/netnsutils/context_windows.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/internal/testutil/netnsutils/sanity_linux.go -->
# sources/cloud-native/moby/internal/testutil/netnsutils/sanity_linux.go

Purpose: asserts that a socket's network namespace matches the current thread namespace on Linux. The main API is `AssertSocketSameNetNS`. Control flow obtains a raw socket control callback, calls `unix.GetsockoptInt` with `SO_NETNS_COOKIE`, compares it to the current netns cookie obtained from `netns.Get`, and fails the test on mismatch. State is observed kernel namespace identity only. Dependencies include syscall `Conn`, `vishvananda/netns`, `unix`, and assertions. Risks include kernel support for netns cookies, raw connection access, and false failures when sockets are intentionally cross-namespace. Test signal is strong for namespace setup bugs.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/internal/testutil/netnsutils/sanity_linux.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/internal/testutil/netnsutils/sanity_notlinux.go -->
# sources/cloud-native/moby/internal/testutil/netnsutils/sanity_notlinux.go

Purpose: no-op implementation of `AssertSocketSameNetNS` for non-Linux platforms. It preserves the call surface without attempting unavailable Linux namespace checks. State and control flow are absent. Dependencies are `syscall` and `testing` for signature compatibility. Risks are only that non-Linux tests receive no namespace sanity validation. Test signal is compile-time portability.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/internal/testutil/netnsutils/sanity_notlinux.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/internal/testutil/registry/ops.go -->
# sources/cloud-native/moby/internal/testutil/registry/ops.go

Purpose: option helpers for configuring the test registry fixture. Important APIs are `Htpasswd`, `Token`, `URL`, `WithStdout`, and `WithStderr`, each mutating `Config`. Control flow is simple option application: authentication, token endpoint, registry URL override, and process stream routing are configured before `NewV2` starts the registry. State lives in the pending registry config. Dependencies are the `Config` type and `io.Writer`. Risks are low, though option ordering can affect expected auth behavior. Test signal is through registry integration tests that need credentialed or token-backed registries.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/internal/testutil/registry/ops.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/internal/testutil/registry/registry.go -->
# sources/cloud-native/moby/internal/testutil/registry/registry.go

Purpose: manages a Docker distribution v2 registry process for integration tests and exposes helpers to inspect/mutate registry blobs. Important APIs are `NewV2`, `WaitReady`, `Ping`, `Close`, `ReadBlobContents`, `WriteBlobContents`, `TempMoveBlobData`, credential getters, and `Path`. Control flow prepares temp registry state, starts a registry binary with generated config/auth settings, waits for `/v2/` readiness, and cleans up the process and filesystem. Blob helpers map digests to registry storage layout and allow tests to corrupt or hide content. State persists in the registry storage directory and child process until close. Dependencies include an external registry executable/config, HTTP probing, filesystem paths, `go-digest`, and test assertions. Risks include process leaks, storage-layout coupling, port readiness races, and destructive blob mutation; test signal is high for pull/push/digest-integrity workflows.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/internal/testutil/registry/registry.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/internal/testutil/registry/registry_mock.go -->
# sources/cloud-native/moby/internal/testutil/registry/registry_mock.go

Purpose: implements a lightweight mock registry HTTP server with path-based handler registration. Important APIs are `Mock.RegisterHandler`, `NewMock`, `URL`, and `Close`. Control flow creates an `httptest.Server`, routes requests by registered paths or simple regex/string matching, and tracks handlers behind a mutex. State is in-memory handler mappings and the server listener. Dependencies are standard HTTP testing utilities and regexp/string matching. Risks include simplistic routing compared with a real registry and concurrency expectations around handler mutation. Test signal is useful for client behavior that only needs controlled HTTP responses.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/internal/testutil/registry/registry_mock.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/internal/testutil/request/helpers.go -->
# sources/cloud-native/moby/internal/testutil/request/helpers.go

Purpose: response-body helpers for test HTTP requests. Important APIs are `ReadBody` and generic `ReadJSONResponse[T]`. Control flow always closes bodies after reading, validates `Content-Type` as `application/json` with media-type parsing before JSON decoding, and includes up to 8 KiB of non-JSON body text in the error. State is none beyond consuming/closing response bodies. Dependencies are `encoding/json`, `mime`, and HTTP types. Risks include callers losing access to the body after helper use and strict content-type requirements. Test signal is covered by `helpers_test.go`.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/internal/testutil/request/helpers.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/internal/testutil/request/helpers_test.go -->
# sources/cloud-native/moby/internal/testutil/request/helpers_test.go

Purpose: unit tests for `ReadJSONResponse`. The single table-driven test covers valid JSON with plain and charset content types, malformed JSON, non-JSON content, and nil response handling. Control flow constructs synthetic `http.Response` values with controlled bodies and asserts decoded fields or error substrings. State is in-memory buffers only. Dependencies are `gotest.tools/assert` and the request package. Risks covered include content-type parsing and body decoding failures; it does not explicitly assert body closure side effects. Test signal is focused and fast.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/internal/testutil/request/helpers_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/internal/testutil/request/npipe.go -->
# sources/cloud-native/moby/internal/testutil/request/npipe.go

Purpose: non-Windows fallback for named-pipe dialing. `npipeDial` panics because the npipe protocol is only supported on Windows. Control flow exists only to fail loudly if non-Windows code attempts to dial an npipe daemon. State and persistence are absent. Dependencies are `net` and `time` for signature compatibility. Risks are intentional: callers must route by daemon URL scheme correctly. Test signal is compile-time portability plus runtime guard.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/internal/testutil/request/npipe.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/internal/testutil/request/npipe_windows.go -->
# sources/cloud-native/moby/internal/testutil/request/npipe_windows.go

Purpose: Windows implementation for named-pipe Docker daemon connections. `npipeDial` delegates to `winio.DialPipe` with the caller's timeout. State is the returned pipe connection. Dependencies are `github.com/Microsoft/go-winio`. Risks include path formatting, timeout behavior, and Windows-only daemon host semantics. Test signal is through request helpers on Windows.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/internal/testutil/request/npipe_windows.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/internal/testutil/request/ops.go -->
# sources/cloud-native/moby/internal/testutil/request/ops.go

Purpose: functional options for constructing raw HTTP requests to the daemon in tests. Important APIs include `Options`, `Host`, `With`, `Method`, `RawString`, `RawContent`, `ContentType`, `JSON`, and `JSONBody`. Control flow accumulates request mutators that later set method, body, and headers; `JSONBody` encodes arbitrary data into a buffer and marks content type. State is the mutable options struct and request body readers. Dependencies are standard HTTP, JSON, and IO packages. Risks include body readers being single-use, errors from JSON encoding surfacing during request construction, and option ordering. Test signal is indirect through API integration tests.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/internal/testutil/request/ops.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/internal/testutil/request/request.go -->
# sources/cloud-native/moby/internal/testutil/request/request.go

Purpose: raw Docker API request helper for tests that need direct HTTP-level access instead of generated client methods. Important APIs are `NewAPIClient`, `DaemonTime`, `DaemonUnixTime`, HTTP verb helpers, `Do`, `DaemonHost`, and `SockConn`. Control flow builds requests from `DOCKER_HOST`/TLS environment, configures unix/npipe/tcp transports, wraps response bodies for safe close, gets daemon time from `/info` for remote daemons, and opens raw socket connections. State is transient HTTP clients and network connections; behavior depends heavily on environment variables. Dependencies include Docker client host parsing, go-connections sockets/TLS, OpenTelemetry HTTP transport, ioutils wrappers, and environment execution state. Risks include duplicated client transport logic, disabled keep-alives, TLS env mismatch, npipe platform branching, and remote daemon clock assumptions. Test signal is broad for low-level API and hijack tests.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/internal/testutil/request/request.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/internal/testutil/specialimage/configtarget.go -->
# sources/cloud-native/moby/internal/testutil/specialimage/configtarget.go

Purpose: builds an OCI image layout that targets an image configuration descriptor directly rather than a normal manifest. The exported `ConfigTarget` writes a config blob and creates an index referencing it with image annotations. State is the generated OCI layout under the provided directory. Dependencies are OCI image-spec descriptors, containerd platform defaults, distribution references, and shared specialimage blob helpers. Risks include intentionally unusual descriptor shape that may expose loader assumptions; test signal is for import/load paths handling config targets.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/internal/testutil/specialimage/configtarget.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/internal/testutil/specialimage/dangling.go -->
# sources/cloud-native/moby/internal/testutil/specialimage/dangling.go

Purpose: creates an OCI/docker-archive-style image without a normal repository tag so tests can exercise dangling image import behavior. The exported `Dangling` writes descriptors and legacy manifest metadata with empty or special tag state. State is the OCI layout and `manifest.json` content under the directory. Dependencies are filesystem/path operations and OCI specs. Risks are in exact legacy manifest semantics because image load behavior may change around dangling tags. Test signal targets image load/listing edge cases.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/internal/testutil/specialimage/dangling.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/internal/testutil/specialimage/emptyfs.go -->
# sources/cloud-native/moby/internal/testutil/specialimage/emptyfs.go

Purpose: produces an image whose root filesystem is effectively empty, using a zero-byte or empty layer/config shape for load/import tests. Important APIs are `EmptyFS` and the local `zeroReader`. Control flow writes minimal blobs and metadata into an OCI layout. State is generated blobs and JSON metadata under the target directory. Dependencies include OCI specs and shared blob-writing helpers. Risks include archive/import code treating empty layers specially or rejecting zero-sized content. Test signal is for image-load handling of empty root filesystems.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/internal/testutil/specialimage/emptyfs.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/internal/testutil/specialimage/emptyindex.go -->
# sources/cloud-native/moby/internal/testutil/specialimage/emptyindex.go

Purpose: creates a valid-looking OCI layout with an empty index. `EmptyIndex` returns the written index after adding layout metadata. State is just `index.json` and `oci-layout` in the target directory. Dependencies are distribution references and OCI spec versioning. Risks are around whether consumers treat an empty index as malformed or simply empty. Test signal is for defensive image load/import validation.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/internal/testutil/specialimage/emptyindex.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/internal/testutil/specialimage/labeled.go -->
# sources/cloud-native/moby/internal/testutil/specialimage/labeled.go

Purpose: creates a single-platform OCI image whose config carries caller-supplied labels. `Labeled` writes a config, manifest, legacy manifest, and index for the requested image reference. State is generated OCI layout files. Dependencies include containerd platform defaults, distribution references, OCI image config, and shared layer/blob helpers. Risks include label map ordering not affecting JSON semantics but potentially affecting byte-level digests; test signal validates label preservation through image load paths.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/internal/testutil/specialimage/labeled.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/internal/testutil/specialimage/load.go -->
# sources/cloud-native/moby/internal/testutil/specialimage/load.go

Purpose: declares `SpecialImageFunc`, the common function signature for special image layout generators. It lets tests parameterize image fixture creation by passing a target directory and receiving an OCI index. Control flow and state are absent in this type-only file. Dependencies are OCI image-spec types. Risks are minimal; its value is API consistency across the specialimage package. Test signal is compile-time integration.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/internal/testutil/specialimage/load.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/internal/testutil/specialimage/multilayer.go -->
# sources/cloud-native/moby/internal/testutil/specialimage/multilayer.go

Purpose: core special-image writer for single-platform OCI/docker archive fixtures with one or more simple file layers. Important APIs include `SingleFileLayer`, `MultiLayer`, `MultiLayerCustom`, `singlePlatformImage`, `ociImage`, `writeLayerWithOneFile`, `writeJsonBlob`, `writeBlob`, and `blobPath`. Control flow creates tar layers, computes canonical digests while streaming blobs to temp files, renames blobs into `blobs/sha256`, writes config/manifest/index JSON, and writes legacy `manifest.json`. State is the complete OCI layout plus legacy docker archive metadata. Dependencies include `moby/go-archive`, compression, OCI specs, `go-digest`, UUID temp names, and distribution references. Risks include confusing layer digests with diff IDs, temp-file cleanup on write failures, uncompressed layer media types, and legacy manifest compatibility. Test signal is high because many specialimage variants reuse these helpers.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/internal/testutil/specialimage/multilayer.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/internal/testutil/specialimage/multiplatform.go -->
# sources/cloud-native/moby/internal/testutil/specialimage/multiplatform.go

Purpose: creates a multi-platform image index from caller-provided platforms and image reference. `MultiPlatform` returns both the top-level index and the per-platform manifest descriptors. Control flow writes one simple layer/config/manifest per platform through shared helpers and wraps them in a tagged image index. State is a nested OCI index layout. Dependencies include containerd platform formatting/defaults, distribution references, OCI specs, and specialimage shared writers. Risks include platform descriptor accuracy and consumers selecting the correct manifest. Test signal is for multi-platform image load and platform matching.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/internal/testutil/specialimage/multiplatform.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/internal/testutil/specialimage/partial.go -->
# sources/cloud-native/moby/internal/testutil/specialimage/partial.go

Purpose: creates a multi-platform index where some referenced platform manifests are intentionally missing from storage. Important APIs are `PartialOpts` and `PartialMultiPlatform`. Control flow writes real manifests for `Stored` platforms, constructs fake descriptors with deterministic digests for `Missing` platforms, then wraps all descriptors in a multi-platform image. State is a deliberately incomplete OCI layout. Dependencies include platform formatting, OCI specs, digest generation, and shared manifest writers. Risks are intentional: missing blobs must remain missing to test partial-load behavior. Test signal targets import validation, lazy platform selection, and missing-content error paths.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/internal/testutil/specialimage/partial.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/internal/testutil/specialimage/random.go -->
# sources/cloud-native/moby/internal/testutil/specialimage/random.go

Purpose: creates deterministic pseudo-random single-platform image layouts for tests that want varied layer counts and image refs. Important APIs are `RandomSinglePlatform`, `layersToDigests`, `blobPaths`, `readJson`, and `LegacyManifest`. Control flow uses a caller-provided `rand.Source`, chooses a random tag and 0-7 layers, writes config/manifest/index, and can synthesize legacy `manifest.json` from an existing manifest descriptor. State is generated image layout content. Dependencies include math/rand, OCI specs, digests, JSON, and shared blob helpers. Risks include non-cryptographic randomness being intentional, zero-layer images, and digest changes when fixture serialization changes. Test signal is for image import robustness across varied layer graphs.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/internal/testutil/specialimage/random.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/internal/testutil/specialimage/textplain.go -->
# sources/cloud-native/moby/internal/testutil/specialimage/textplain.go

Purpose: creates an OCI layout with a descriptor using `text/plain` content so tests can validate media-type filtering and rejection behavior. `TextPlain` writes a small text blob and references it from image metadata. State is a deliberately unusual layout under the target directory. Dependencies include strings, distribution references, OCI descriptors, and shared blob/index helpers. Risks are intentional incompatibility with normal image media types. Test signal targets loader validation for unsupported descriptor media types.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/internal/testutil/specialimage/textplain.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/internal/testutil/specialimage/twoplatform.go -->
# sources/cloud-native/moby/internal/testutil/specialimage/twoplatform.go

Purpose: builds a known two-platform OCI image fixture for `linux/amd64` and `linux/arm64`. Important APIs are `TwoPlatform`, `FileInLayer`, `oneLayerPlatformManifest`, and `multiPlatformImage`. Control flow writes one file layer per platform, creates platform-specific configs/manifests, assigns descriptor platform fields, embeds them in a child index, then writes a top-level annotated index and `oci-layout`. State is a nested multi-platform OCI layout. Dependencies include containerd platform parsing, OCI specs, distribution references, digest helpers, and shared writers. Risks include nested index semantics and platform selection behavior. Test signal is high for deterministic multi-platform image load tests.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/internal/testutil/specialimage/twoplatform.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/internal/testutil/storeutils/store.go -->
# sources/cloud-native/moby/internal/testutil/storeutils/store.go

Purpose: creates a temporary libnetwork datastore for tests. `NewTempStore` initializes a `datastore.Store` in a test temp directory and asserts creation succeeds. State is an on-disk temporary datastore removed by the testing framework. Dependencies are libnetwork datastore and `gotest.tools/assert`. Risks are low; backend behavior remains tied to datastore implementation details. Test signal supports networking tests needing isolated persistent store state.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/internal/testutil/storeutils/store.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/internal/testutil/stringutils.go -->
# sources/cloud-native/moby/internal/testutil/stringutils.go

Purpose: generates random alphabetic-only strings for test resource names. `GenerateRandomAlphaOnlyString` returns an `n`-length string using letters, likely backed by pseudo-random selection. State is only random generator state from the standard library if used. Dependencies are minimal. Risks include non-determinism, possible collisions for small lengths, and suitability only for tests rather than security. Test signal is defined in `stringutils_test.go`.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/internal/testutil/stringutils.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/internal/testutil/stringutils_test.go -->
# sources/cloud-native/moby/internal/testutil/stringutils_test.go

Purpose: unit tests for random alpha string generation. Helpers verify generated length and that repeated generated strings are not all identical, then tests call those helpers for `GenerateRandomAlphaOnlyString`. State is in-memory generated strings. Dependencies are `gotest.tools/assert` and comparisons. Risks include probabilistic uniqueness assertions that could theoretically flake, though probability is low for normal lengths. Test signal covers basic contract only, not character-class exhaustiveness if helper does not check it.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/internal/testutil/stringutils_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/internal/testutil/temp_files.go -->
# sources/cloud-native/moby/internal/testutil/temp_files.go

Purpose: creates temporary directories for tests with a helper-level API. `TempDir` wraps temp directory creation, likely normalizes permissions/path behavior, and registers cleanup or fails the test on error. State is filesystem temp directory content. Dependencies are `os`, `filepath`, and `testing`. Risks are low, mostly around cleanup and platform path handling. Test signal is through call sites that need predictable temp paths.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/internal/testutil/temp_files.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/man/Makefile -->
# sources/cloud-native/moby/man/Makefile

Purpose: builds and installs Moby man pages from Markdown sources. Important targets are `all`, `install`, and `clean`, with pattern rules for `man<section>/<page>` outputs. Control flow derives man-section directories from page names, runs the markdown-to-man tooling, installs generated pages under `DESTDIR`/`PREFIX` style paths, and removes generated artifacts on clean. State is generated manpage files in `man*` directories and installed copies. Dependencies include Make, the page list variables from included make context, and `go-md2man` tooling. Risks include fragile section inference, missing tool dependencies, and generated-file churn. Test signal is build-system validation rather than Go tests.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/man/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/man/tools.go -->
# sources/cloud-native/moby/man/tools.go

Purpose: Go tools file that pins the `go-md2man/v2` dependency for manpage generation. It imports the tool for side effects under package `man`, ensuring module-aware tooling retains it. Control flow and runtime state are absent. Dependencies are build/toolchain module resolution. Risks are low; deleting this file could drop the manpage generator from module dependencies. Test signal is build dependency reproducibility.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/man/tools.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/otelcol-ci-config.yml -->
# sources/cloud-native/moby/otelcol-ci-config.yml

Purpose: OpenTelemetry Collector configuration for CI trace capture. It configures OTLP gRPC on `0.0.0.0:4317`, OTLP HTTP on `0.0.0.0:4318`, a batch processor, and a file exporter with 1-second flush and size rotation below Jaeger upload limits. State is collector output files written by the file exporter. Dependencies are the OpenTelemetry Collector and CI services that upload or inspect the trace file. Risks include open bind addresses in CI context, file rotation losing expected trace chunks, and collector schema drift. Test signal is observability support for test runs, not application behavior.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/otelcol-ci-config.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/pkg/authorization/api.go -->
# sources/cloud-native/moby/pkg/authorization/api.go

Purpose: defines the wire contract between dockerd and authorization plugins. Important API constants are `AuthZApiRequest`, `AuthZApiResponse`, and `AuthZApiImplements`; important types are `PeerCertificate`, `Request`, and `Response`. Control flow is limited to JSON marshaling/unmarshaling of peer certificates as PEM bytes; request/response structs carry user identity, HTTP method/URI/body/headers, TLS certs, response status, and plugin allow/deny messages. State is serialized JSON exchanged with plugins. Dependencies include x509, PEM, and JSON encoding. Risks include `UnmarshalJSON` assuming `pem.Decode` succeeds before dereferencing, sensitive header/body exposure, and compatibility with plugin field names. Test signal is `api_test.go` certificate round-trip coverage.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/pkg/authorization/api.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/pkg/authorization/api_test.go -->
# sources/cloud-native/moby/pkg/authorization/api_test.go

Purpose: validates JSON PEM round-tripping for `PeerCertificate`. The test creates an RSA key, a self-signed x509 certificate with subject/key-usage fields, marshals through `PeerCertificate`, unmarshals, and compares selected certificate properties. State is temporary in-memory certificate data. Dependencies include crypto/x509, RSA, TLS-related structures, and gotest assertions. Risks covered include losing certificate metadata or malformed PEM generation; risks not covered include invalid PEM error handling. Test signal is focused on plugin API compatibility for TLS peer certificates.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/pkg/authorization/api_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/pkg/authorization/authz.go -->
# sources/cloud-native/moby/pkg/authorization/authz.go

Purpose: implements per-request authorization context logic for invoking authz plugins before and after daemon handlers. Important APIs are `NewCtx`, `Ctx.AuthZRequest`, `Ctx.AuthZResponse`, `sendBody`, `headers`, and authorization error helpers. Control flow optionally buffers JSON request bodies up to 4 MiB without consuming the downstream reader, excludes auth endpoints and sensitive registry/auth headers, sends request data to each plugin in order, captures response status/headers/body from a `ResponseModifier`, invokes response authorization, and flushes final response data. State is the per-transaction cached `Request` plus response modifier contents. Dependencies include plugin interface, MIME/url parsing, OpenTelemetry/logging, and ioutils reader wrappers. Risks include body-size rejection, partial body peeking behavior, exact auth-endpoint regex semantics, response body buffering limits, and leaking non-excluded sensitive data. Test signal is strong in Unix authz plugin tests.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/pkg/authorization/authz.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/pkg/authorization/authz_unix_test.go -->
# sources/cloud-native/moby/pkg/authorization/authz_unix_test.go

Purpose: Unix integration/unit tests for authorization plugin request/response flows and response modification. Tests create Unix-socket plugin servers, exercise request and response calls, plugin errors, body-size limits, `sendBody` URL/content-type matrix, response override behavior, and `ResponseModifier` flush/hijack-like behavior. State includes temporary sockets, HTTP test servers, buffered request/response bodies, and plugin client state. Dependencies include `plugins.NewClient`, gorilla mux, Unix sockets, TLS config, and JSON assertions. Risks covered include auth endpoint body suppression, content-type case handling, oversized body rejection, and plugin denial/error propagation. Remaining risks include Windows behavior and real daemon handler integration, which are covered elsewhere.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/pkg/authorization/authz_unix_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/pkg/authorization/middleware.go -->
# sources/cloud-native/moby/pkg/authorization/middleware.go

Purpose: daemon API middleware that wraps handlers with authorization plugin checks. Important APIs are `Middleware`, `NewMiddleware`, `SetPlugins`, `RemovePlugin`, and `WrapHandler`. Control flow snapshots the plugin chain under a mutex, extracts TLS common name as default user identity, runs request authorization, wraps the response writer in `ResponseModifier`, invokes the underlying handler, refreshes the plugin chain in case it changed, runs response authorization only when handler succeeded, and returns handler errors preferentially. State is the mutex-protected plugin slice. Dependencies include `plugingetter`, authorization context logic, HTTP, and containerd logging. Risks include global plugin getter mutation, plugin-chain changes mid-request, response buffering/hijacking interaction, and silently returning nil if plugins are removed after the handler. Test signal is in middleware tests.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/pkg/authorization/middleware.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/pkg/authorization/middleware_test.go -->
# sources/cloud-native/moby/pkg/authorization/middleware_test.go

Purpose: basic unit tests for authorization middleware construction and response modifier creation. Tests verify plugin list behavior, plugin removal/set helpers, and wrapper types using fake plugins/plugin getters. State is in-memory middleware state and `httptest` response writers. Dependencies include `plugingetter`, gotest assertions, and HTTP testing. Risks covered are basic chain management; deeper request/response authorization behavior is covered in Unix-specific middleware/authz tests. Test signal is narrow but fast.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/pkg/authorization/middleware_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/pkg/authorization/middleware_unix_test.go -->
# sources/cloud-native/moby/pkg/authorization/middleware_unix_test.go

Purpose: Unix-focused test for `Middleware.WrapHandler` behavior with authz plugins around a daemon handler. It exercises allow/deny responses, plugin getter stubs, wrapped handler execution, and error propagation. State is in-memory HTTP request/response and plugin chain state. Dependencies include context, httptest, and plugingetter interfaces. Risks covered include plugin denial blocking handler output and successful authorization allowing response flow. Test signal validates the middleware integration boundary rather than plugin transport.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/pkg/authorization/middleware_unix_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/pkg/authorization/plugin.go -->
# sources/cloud-native/moby/pkg/authorization/plugin.go

Purpose: adapts Docker plugin clients to the authorization `Plugin` interface. Important APIs are `Plugin`, `newPlugins`, `SetPluginGetter`, `GetPluginGetter`, `authorizationPlugin.AuthZRequest`, `AuthZResponse`, and `initPlugin`. Control flow deduplicates configured plugin names, lazily resolves each plugin once through a daemon plugin getter or legacy `plugins.Get`, updates the remote name for managed plugins, caches initialization errors, and calls `AuthZPlugin.AuthZReq`/`AuthZRes` methods. State includes global plugin getter and per-plugin `sync.Once`, client pointer, name, and init error. Dependencies include `plugingetter` and legacy plugin client package. Risks include global getter races, nil plugin from failed getter before `SetName`, lazy failures persisting for process lifetime, and legacy/v2 plugin compatibility. Test signal comes through middleware and authz plugin tests.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/pkg/authorization/plugin.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/pkg/authorization/response.go -->
# sources/cloud-native/moby/pkg/authorization/response.go

Purpose: buffers and exposes daemon HTTP responses so authorization plugins can inspect or override them before final flush. Important APIs are `ResponseModifier`, `NewResponseModifier`, and methods on `responseModifier` including `Write`, `WriteHeader`, `Header`, `OverrideBody`, `OverrideHeader`, `OverrideStatusCode`, `FlushAll`, `Flush`, `Hijack`, and `Hijacked`. Control flow captures headers/status/body until flush, auto-flushes when body exceeds 64 KiB, passes through directly after hijack, copies buffered headers/status/body to the underlying writer, and resets local header/status state after flush. State is buffered response bytes, headers, status, and hijack flag. Dependencies include HTTP flusher/hijacker interfaces and JSON header unmarshaling. Risks include partial flush semantics, repeated header `Add`, status reset after flush, body mutation after plugins, and hijack timing. Tests cover response modifier override and flushing behavior.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/pkg/authorization/response.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/pkg/homedir/homedir.go -->
# sources/cloud-native/moby/pkg/homedir/homedir.go

Purpose: returns the current user's home directory in a cross-platform way. `Get` prefers environment variables appropriate for OS conventions and falls back to `os/user`. Control flow avoids expensive user lookup when `HOME` or Windows equivalents are present. State is only environment-derived. Dependencies are `os`, `os/user`, and `runtime`. Risks include empty or misleading environment variables, cross-compiled/runtime OS differences, and user lookup failure in minimal containers. Test signal is basic path non-empty/shape coverage in `homedir_test.go`.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/pkg/homedir/homedir.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/pkg/homedir/homedir_linux.go -->
# sources/cloud-native/moby/pkg/homedir/homedir_linux.go

Purpose: Linux XDG directory helpers used by rootless and plugin path logic. Important APIs are `GetRuntimeDir`, `StickRuntimeDirContents`, `GetDataHome`, `GetConfigHome`, `GetLibHome`, and `GetLibexecHome`. Control flow reads XDG env vars or falls back to `$HOME`-derived paths, silently skips sticky-bit work when `XDG_RUNTIME_DIR` is unset, resolves absolute paths, and applies sticky mode only to files under the runtime directory. State changes include `chmod` sticky bit on selected runtime files. Dependencies are filesystem/env APIs and `homedir.Get`. Risks include prefix checks needing a trailing separator, permission failures on chmod, and rootless behavior depending on env availability. Test signal is indirect through plugin discovery/rootless tests.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/pkg/homedir/homedir_linux.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/pkg/homedir/homedir_others.go -->
# sources/cloud-native/moby/pkg/homedir/homedir_others.go

Purpose: non-Linux stubs for XDG-specific homedir helpers. Functions return unsupported errors except `StickRuntimeDirContents`, which cannot apply Linux runtime-dir sticky behavior. State changes are absent. Dependencies are only `errors`. Risks are low; callers must handle unsupported errors on non-Linux platforms. Test signal is compile-time portability and caller error handling.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/pkg/homedir/homedir_others.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/pkg/homedir/homedir_test.go -->
# sources/cloud-native/moby/pkg/homedir/homedir_test.go

Purpose: tests the basic `Get` home-directory helper. It asserts that the returned path is non-empty and is a clean path. State is environment/user lookup only. Dependencies are `filepath` and testing. Risks covered are minimal; it does not simulate missing environment variables or user lookup failures. Test signal is a smoke test for platform home resolution.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/pkg/homedir/homedir_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/pkg/ioutils/readers.go -->
# sources/cloud-native/moby/pkg/ioutils/readers.go

Purpose: reader wrappers for close callbacks and context-cancelable reads. Important APIs are `NewReadCloserWrapper`, `NewCancelReadCloser`, `cancelReadCloser.Read`, `Close`, and `subsequentCloseWarn`. Control flow wraps an `io.Reader` with a closer protected by atomic close detection, pipes reads from an input reader into an `io.Pipe` in a goroutine, closes with context cancellation errors, and logs warning stacks on repeated closes. State includes atomic closed flags, context cancellation, and pipe endpoints. Dependencies include context, IO pipes, atomics, containerd logging, and debug stacks. Risks include goroutine lifetime, close races, warning noise on intentional repeated closes, and cancellation semantics. Tests cover close callback once and cancelable read behavior.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/pkg/ioutils/readers.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/pkg/ioutils/readers_test.go -->
# sources/cloud-native/moby/pkg/ioutils/readers_test.go

Purpose: unit tests for read closer wrappers. Tests verify the custom closer runs only once and that `NewCancelReadCloser` stops a perpetual reader when context is canceled or closed. State is in-memory readers and contexts. Dependencies include `io`, context cancellation, and timeouts. Risks covered include double close and stuck reads; tests may be timing-sensitive around cancellation. Test signal is focused on wrapper lifecycle behavior.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/pkg/ioutils/readers_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/pkg/ioutils/writeflusher.go -->
# sources/cloud-native/moby/pkg/ioutils/writeflusher.go

Purpose: wraps a writer with flush tracking and close signaling. Important APIs are `WriteFlusher`, `Write`, `Flush`, `Flushed`, `Close`, and `NewWriteFlusher`. Control flow writes through to the underlying writer unless closed, calls an underlying `Flush` method when available or a no-op flusher otherwise, records that a flush happened, and protects state with a mutex/channel-like close guard. State includes flushed and closed flags. Dependencies are `io` and `sync`. Risks include writes after close, underlying flush errors not represented because `Flush` has no return, and concurrent write/close ordering. Test signal appears through consumers rather than a dedicated test in this subset.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/pkg/ioutils/writeflusher.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/pkg/ioutils/writers.go -->
# sources/cloud-native/moby/pkg/ioutils/writers.go

Purpose: writer equivalent of `NewReadCloserWrapper`, adding a custom close callback to any `io.Writer`. Important API is `NewWriteCloserWrapper`; `writeCloserWrapper.Close` uses atomic state to invoke the closer once and warn on repeated closes. State is the wrapped writer and closed flag. Dependencies include `io` and atomics. Risks are low, mainly repeated close behavior and logging side effects. Test signal is `writers_test.go`.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/pkg/ioutils/writers.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/pkg/ioutils/writers_test.go -->
# sources/cloud-native/moby/pkg/ioutils/writers_test.go

Purpose: unit test for `NewWriteCloserWrapper`. It writes through to an in-memory buffer and verifies the close callback executes only once across repeated closes. State is a bytes buffer and counter. Dependencies are standard testing and bytes. Risks covered are double-close behavior; write-after-close behavior is not deeply exercised. Test signal is narrow and fast.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/pkg/ioutils/writers_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/pkg/longpath/longpath.go -->
# sources/cloud-native/moby/pkg/longpath/longpath.go

Purpose: handles Windows long path prefixing while remaining harmless on other platforms. Important APIs are `AddPrefix` and `MkdirTemp`. Control flow adds `\\?\` for Windows paths that are not already prefixed, handles UNC paths with the correct long UNC form, and delegates temp-directory creation after prefixing. State is filesystem path strings and created temp directories. Dependencies are `os`, `runtime`, and string manipulation. Risks include subtle Windows path forms, already-prefixed paths, and UNC normalization. Test signal is in `longpath_test.go`.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/pkg/longpath/longpath.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/pkg/longpath/longpath_test.go -->
# sources/cloud-native/moby/pkg/longpath/longpath_test.go

Purpose: tests Windows long path prefix transformation. It covers standard drive paths and UNC paths, asserting expected prefixing and avoiding duplicate prefixes. State is string-only. Dependencies are testing and strings. Risks covered are path formatting regressions; actual filesystem behavior with long paths is not exercised. Test signal is focused on path-normalization logic.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/pkg/longpath/longpath_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/pkg/meminfo/meminfo.go -->
# sources/cloud-native/moby/pkg/meminfo/meminfo.go

Purpose: public entry point and data model for memory information. `Read` delegates to platform-specific `readMemInfo`, and `Memory` stores total/free/available memory plus swap totals/free values. State is a snapshot of host memory at call time. Dependencies are platform-specific files in the package. Risks depend on backend parsing/API behavior; fields may be zero where the platform cannot provide them. Test signal comes from Linux/unix parser tests.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/pkg/meminfo/meminfo.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/pkg/meminfo/meminfo_linux.go -->
# sources/cloud-native/moby/pkg/meminfo/meminfo_linux.go

Purpose: Linux implementation of memory info parsing from `/proc/meminfo`. Important APIs are `readMemInfo` and `parseMemInfo`. Control flow scans key-value-unit lines, accepts `kB` units, parses integers, multiplies to bytes, and fills known `Memory` fields while ignoring malformed or unknown lines. State is read-only host procfs data. Dependencies are bufio, os, strconv, and strings. Risks include unit assumptions, malformed kernel output, zero values for missing keys, and scanner limitations. Test signal is `meminfo_unix_test.go` fixture parsing.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/pkg/meminfo/meminfo_linux.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/pkg/meminfo/meminfo_unix_test.go -->
# sources/cloud-native/moby/pkg/meminfo/meminfo_unix_test.go

Purpose: tests Linux meminfo parser behavior using synthetic `/proc/meminfo` content. It verifies recognized fields are parsed from kB to bytes and malformed lines are ignored. State is in-memory string readers. Dependencies are testing and strings. Risks covered include bad tokens and non-kB units; actual host `/proc/meminfo` read errors are not exercised. Test signal is strong for parser resilience.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/pkg/meminfo/meminfo_unix_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/pkg/meminfo/meminfo_unsupported.go -->
# sources/cloud-native/moby/pkg/meminfo/meminfo_unsupported.go

Purpose: unsupported-platform implementation of memory info. `readMemInfo` returns an error indicating the platform cannot provide data. State is absent. Dependencies are minimal error creation. Risks are low; callers must handle unsupported errors. Test signal is compile-time portability.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/pkg/meminfo/meminfo_unsupported.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/pkg/meminfo/meminfo_windows.go -->
# sources/cloud-native/moby/pkg/meminfo/meminfo_windows.go

Purpose: Windows memory information backend. It defines a `MEMORYSTATUSEX`-compatible struct and calls `GlobalMemoryStatusEx` to populate physical and pagefile memory totals/free values. State is a host memory snapshot. Dependencies are `golang.org/x/sys/windows` and unsafe syscall struct layout. Risks include struct-size/layout correctness, API failure handling, and semantic differences between Windows pagefile and Unix swap. Test signal is platform integration rather than unit coverage in this subset.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/pkg/meminfo/meminfo_windows.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/pkg/parsers/kernel/kernel.go -->
# sources/cloud-native/moby/pkg/parsers/kernel/kernel.go

Purpose: non-Windows kernel version model, parser, formatter, and comparator. Important APIs are `VersionInfo`, `String`, `CompareKernelVersion`, and `ParseRelease`. Control flow parses strings like `4.1.2-generic` or `3.12-1-amd64`, tolerates missing minor patch by treating flavor as suffix, and compares only numeric kernel/major/minor fields. State is pure value data. Dependencies are fmt and errors. Risks include ignoring flavor in comparisons, accepting unusual release formats, and parser behavior around vendor suffixes. Test signal is in `kernel_unix_test.go`.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/pkg/parsers/kernel/kernel.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/pkg/parsers/kernel/kernel_darwin.go -->
# sources/cloud-native/moby/pkg/parsers/kernel/kernel_darwin.go

Purpose: Darwin kernel version backend using `system_profiler SPSoftwareDataType`. Important APIs are `GetKernelVersion`, `getRelease`, and `getSPSoftwareDataType`. Control flow executes `system_profiler`, finds the `Kernel Version:` line, extracts the Darwin release after the OS name, and parses it with `ParseRelease`. State is command output only. Dependencies include external `system_profiler` and string parsing. Risks include localized or changed profiler output, empty release returning parse errors later, and command execution cost. Test signal is `kernel_darwin_test.go` for release extraction.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/pkg/parsers/kernel/kernel_darwin.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/pkg/parsers/kernel/kernel_darwin_test.go -->
# sources/cloud-native/moby/pkg/parsers/kernel/kernel_darwin_test.go

Purpose: tests Darwin `getRelease` parsing from representative `system_profiler` output. It asserts kernel release extraction and error behavior for malformed data. State is in-memory strings. Dependencies are gotest assertions. Risks covered are formatting assumptions around `Kernel Version`; real command execution is not tested. Test signal is focused parser coverage.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/pkg/parsers/kernel/kernel_darwin_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/pkg/parsers/kernel/kernel_unix.go -->
# sources/cloud-native/moby/pkg/parsers/kernel/kernel_unix.go

Purpose: Linux/BSD kernel backend using `uname`. Important APIs are `GetKernelVersion` and `CheckKernelVersion`. Control flow calls platform `uname`, converts the release byte array to a string, parses it, and compares current version against requested minimum while logging and allowing success if version lookup fails. State is host kernel snapshot only. Dependencies are x/sys/unix and containerd logging. Risks include permissive failure behavior in `CheckKernelVersion`, release parsing limitations, and platform build tags. Test signal is parser/comparator tests in `kernel_unix_test.go`.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/pkg/parsers/kernel/kernel_unix.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/pkg/parsers/kernel/kernel_unix_test.go -->
# sources/cloud-native/moby/pkg/parsers/kernel/kernel_unix_test.go

Purpose: tests non-Windows kernel release parsing and version comparison. It covers typical kernel strings, missing patch versions, flavors, invalid releases, and compare outcomes for less/equal/greater numeric versions. State is pure value data. Dependencies are standard testing and fmt helper output. Risks covered include parser regressions and comparator ordering; runtime `uname` is not exercised. Test signal is strong for pure parser behavior.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/pkg/parsers/kernel/kernel_unix_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/pkg/parsers/kernel/kernel_windows.go -->
# sources/cloud-native/moby/pkg/parsers/kernel/kernel_windows.go

Purpose: Windows-specific kernel version backend and model. `GetKernelVersion` reads `BuildLabEx` from the registry and uses `windows.GetVersion` to fill major, minor, and build numbers; `String` formats those values. State is a snapshot of registry and OS version APIs. Dependencies are Windows registry and x/sys/windows. Risks include dockerd manifest requirements for correct `GetVersion`, registry access failure, and private lowercase fields limiting cross-platform API symmetry. Test signal is platform integration only.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/pkg/parsers/kernel/kernel_windows.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/pkg/parsers/kernel/uname_linux.go -->
# sources/cloud-native/moby/pkg/parsers/kernel/uname_linux.go

Purpose: Linux implementation of the package-local `uname` helper. It calls `unix.Uname` and returns the populated `unix.Utsname`. State is host kernel uname data. Dependencies are x/sys/unix. Risks are low; errors propagate to `GetKernelVersion`. Test signal is indirect through runtime kernel-version calls.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/pkg/parsers/kernel/uname_linux.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/pkg/parsers/kernel/uname_unsupported.go -->
# sources/cloud-native/moby/pkg/parsers/kernel/uname_unsupported.go

Purpose: unsupported-platform fallback for `uname`. It defines a compatible `utsName` shape and returns an unsupported error. State is absent. Dependencies are errors. Risks are low; callers must handle kernel version unavailability. Test signal is compile-time portability.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/pkg/parsers/kernel/uname_unsupported.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/pkg/parsers/operatingsystem/operatingsystem_linux.go -->
# sources/cloud-native/moby/pkg/parsers/operatingsystem/operatingsystem_linux.go

Purpose: Linux OS-release and containerization parser. Important APIs are `GetOperatingSystem`, `GetOperatingSystemVersion`, `getValueFromOsRelease`, and `IsContainerized`. Control flow reads `/etc/os-release` with fallback to `/usr/lib/os-release`, trims quotes/whitespace from requested keys, defaults missing pretty name to `Linux`, and detects containerization by scanning `/proc/1/cgroup` for non-root/non-init.scope cgroup paths. State is read-only host files, with package variables allowing tests to redirect paths. Dependencies are bufio, bytes, os, and strings. Risks include simplistic os-release parsing, last key wins, cgroup v1/v2 format assumptions, and false positives for systemd scopes. Test signal is broad in `operatingsystem_linux_test.go`.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/pkg/parsers/operatingsystem/operatingsystem_linux.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/pkg/parsers/operatingsystem/operatingsystem_linux_test.go -->
# sources/cloud-native/moby/pkg/parsers/operatingsystem/operatingsystem_linux_test.go

Purpose: unit tests for Linux OS-release parsing, version extraction, fallback file selection, and containerization detection. Tests use temp files and package variables to simulate `/etc/os-release`, `/usr/lib/os-release`, and `/proc/1/cgroup`. State is temporary filesystem fixtures. Dependencies are gotest assertions and filepath/os helpers. Risks covered include quoted values, missing `PRETTY_NAME`, dual `VERSION_ID`, fallback behavior, and cgroup paths for host versus container. Test signal is strong for parser behavior but not for real distro edge cases beyond fixtures.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/pkg/parsers/operatingsystem/operatingsystem_linux_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/pkg/parsers/operatingsystem/operatingsystem_unix.go -->
# sources/cloud-native/moby/pkg/parsers/operatingsystem/operatingsystem_unix.go

Purpose: generic Darwin/FreeBSD operating-system helpers. `GetOperatingSystem` returns the machine field from `uname`, while version and containerization detection return unsupported errors or false/error. State is host uname data only. Dependencies include x/sys/unix. Risks include returning machine architecture rather than marketing OS name and unsupported feature errors. Test signal is compile-time/platform coverage.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/pkg/parsers/operatingsystem/operatingsystem_unix.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/pkg/parsers/operatingsystem/operatingsystem_windows.go -->
# sources/cloud-native/moby/pkg/parsers/operatingsystem/operatingsystem_windows.go

Purpose: Windows OS description and version helpers. Important APIs are `GetOperatingSystem`, `GetOperatingSystemVersion`, `IsContainerized`, `IsWindowsClient`, and `getFirstStringValue`. Control flow gets product type/build from `RtlGetVersion`, best-effort reads `DisplayVersion` or `ReleaseId` plus `UBR` from registry, formats via `windowsOSRelease`, returns `osversion.Get().ToString()` for version, and treats Windows as not containerized. State is registry/OS API snapshot. Dependencies are hcsshim/osversion and Windows registry APIs. Risks include undocumented registry keys, fallback display strings, and product-type interpretation. Test signal is mostly `windows_os_string_test.go` for formatting.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/pkg/parsers/operatingsystem/operatingsystem_windows.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/pkg/parsers/operatingsystem/windows_os_string.go -->
# sources/cloud-native/moby/pkg/parsers/operatingsystem/windows_os_string.go

Purpose: formats Windows release metadata into strings resembling `winver.exe`. Important type is `windowsOSRelease` with server/client flag, display version, build, and UBR. Control flow appends `Server`, optional `Version <display>`, and `OS Build <build>[.<UBR>]`. State is pure value data. Dependencies are fmt and strings. Risks include string compatibility expectations with existing CLI/API output and omission of unset fields. Test signal is comprehensive table coverage in `windows_os_string_test.go`.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/pkg/parsers/operatingsystem/windows_os_string.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/pkg/parsers/operatingsystem/windows_os_string_test.go -->
# sources/cloud-native/moby/pkg/parsers/operatingsystem/windows_os_string_test.go

Purpose: table-driven tests for Windows OS release string formatting. Cases cover client/server, display version present/absent, and UBR present/absent. State is pure struct values. Dependencies are standard testing. Risks covered are formatting regressions; registry/API retrieval is not exercised. Test signal is strong for the formatter contract.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/pkg/parsers/operatingsystem/windows_os_string_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/pkg/pidfile/pidfile.go -->
# sources/cloud-native/moby/pkg/pidfile/pidfile.go

Purpose: small PID file reader/writer that ignores stale or malformed content but prevents overwriting a live process PID. Important APIs are `Read` and `Write`. Control flow reads and trims file content, parses an integer, returns zero for malformed/dead/zero PIDs, checks liveness via `process.Alive`, rejects non-positive new PIDs, and writes decimal PID with 0644 permissions. State is the pidfile path on disk and live process table observation. Dependencies include `os`, `strconv`, and Moby `process`. Risks include PID reuse races, malformed files silently treated as empty, and permissions. Test signal is in `pidfile_test.go`.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/pkg/pidfile/pidfile.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/pkg/pidfile/pidfile_test.go -->
# sources/cloud-native/moby/pkg/pidfile/pidfile_test.go

Purpose: unit/integration tests for pidfile read/write semantics. Tests cover invalid PIDs, writing/reading the current or child process PID, stale/dead PID handling, malformed content, missing files, and existing live process protection. State includes temp pidfiles and sometimes a child process. Dependencies include os/exec, runtime branching, and testing. Risks covered include stale-file overwrite safety and parser tolerance; PID reuse remains inherently race-sensitive. Test signal is strong for filesystem behavior.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/pkg/pidfile/pidfile_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/pkg/plugingetter/getter.go -->
# sources/cloud-native/moby/pkg/plugingetter/getter.go

Purpose: defines compatibility interfaces that let daemon code work with legacy v1 plugins and managed v2 plugins through one getter abstraction. Important APIs are mode constants `Lookup`, `Acquire`, `Release`, interfaces `CompatPlugin`, `PluginWithV1Client`, `PluginAddr`, `CountedPlugin`, and `PluginGetter`. Control flow is not implemented here; the file defines contracts for lookup/reference-counting, scoped paths, direct v1 clients, socket addresses, and capability callbacks. State is owned by implementations. Dependencies include net/time and legacy `plugins.Client`. Risks include interface drift across plugin systems and misuse of reference-count modes. Test signal is compile-time integration across plugin consumers.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/pkg/plugingetter/getter.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/pkg/plugins/client.go -->
# sources/cloud-native/moby/pkg/plugins/client.go

Purpose: HTTP client for legacy Docker plugins over unix, npipe, tcp, or TLS transports. Important APIs are `NewClient`, `NewClientWithTimeout`, `Client.Call`, `CallWithOptions`, `Stream`, `SendFile`, `WithRequestTimeout`, `callWithRetry`, `backoff`, and `httpScheme`. Control flow builds a transport with socket configuration and dummy host for local schemes, JSON-encodes request args, posts to plugin service paths with version MIME headers, retries connection failures with exponential backoff up to 30 seconds, applies optional request timeouts, decodes JSON responses, streams bodies, and converts non-200 plugin errors to `statusError`. State is an `http.Client` and request factory. Dependencies include go-connections sockets/TLS, plugin transport, ioutils, JSON, and logging. Risks include retrying with a consumed reader for streaming data, timeout/cancel handling, error-body decoding compatibility, and local scheme host quirks. Test signal is broad in `client_test.go`.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/pkg/plugins/client.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/pkg/plugins/client_test.go -->
# sources/cloud-native/moby/pkg/plugins/client_test.go

Purpose: unit tests for plugin HTTP client behavior. Tests cover failed connection retry/abort, fail-once retry, echo request/response JSON, backoff math, scheme normalization, client timeout construction, streaming responses, file sending, request timeout propagation, and status-error handling. State includes local HTTP test servers, request wrappers, buffers, and timing windows. Dependencies are httptest, JSON, plugin transport, TLS options, and gotest assertions. Risks covered include retry timing and request construction; tests may be timing-sensitive but use shortened special timeouts. Test signal is strong for plugin client protocol behavior.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/pkg/plugins/client_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/pkg/plugins/discovery.go -->
# sources/cloud-native/moby/pkg/plugins/discovery.go

Purpose: discovers legacy v1 plugins from socket directories and spec files. Important APIs are `LocalRegistry`, `NewLocalRegistry`, `Scan`, `Plugin`, `SpecsPaths`, `readPluginInfo`, `readPluginJSONInfo`, and `pluginPaths`. Control flow scans `/run/docker/plugins` sockets and platform-specific spec paths, supports `<name>.sock` and `<name>/<name>.sock`, reads `.spec` files as plugin addresses, decodes `.json` specs with TLS config, tolerates missing paths and rootless permission errors, and returns `ErrNotFound` when unresolved. State is filesystem plugin/spec content and decoded `Plugin` structs. Dependencies include JSON, filesystem APIs, user namespace detection, homedir platform paths, and logging. Risks include path priority, rootless permission handling, socket-mode checks, JSON TLS defaults, and compatibility with old plugin layouts. Test signal is in discovery tests.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/pkg/plugins/discovery.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/pkg/plugins/discovery_test.go -->
# sources/cloud-native/moby/pkg/plugins/discovery_test.go

Purpose: tests spec-file plugin discovery. It creates temp `.spec` and `.json` plugin definitions, invokes a `LocalRegistry`, and asserts plugin address/TLS config behavior including insecure defaults when CA is omitted. State is temporary spec files. Dependencies are os/path testing helpers. Risks covered include file parsing and JSON defaults; Unix socket scanning is covered separately. Test signal is focused on cross-platform spec discovery.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/pkg/plugins/discovery_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/pkg/plugins/discovery_unix.go -->
# sources/cloud-native/moby/pkg/plugins/discovery_unix.go

Purpose: Unix implementation of plugin spec search paths. It chooses rootless paths under XDG config/lib homes when `ROOTLESSKIT_STATE_DIR` is set, otherwise `/etc/docker/plugins` and `/usr/lib/docker/plugins`. State is environment-derived. Dependencies include `homedir` and filesystem path joining. Risks include a likely fallback subtlety in `rootlessConfigPluginsPath` where the error branch uses `configHome`, rootless env detection by variable only, and path existence/permission differences. Test signal is rootless/discovery behavior through Unix tests.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/pkg/plugins/discovery_unix.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/pkg/plugins/discovery_unix_test.go -->
# sources/cloud-native/moby/pkg/plugins/discovery_unix_test.go

Purpose: Unix tests for local socket discovery and registry scanning. Tests create Unix sockets and non-plugin files under temp plugin directories, scan names, and verify socket-based `Plugin` resolution. State includes temporary directories and socket listeners. Dependencies include net.Unix sockets, os paths, reflect/gotest assertions. Risks covered include directory layouts, socket mode detection, and filtering non-plugin files. Test signal is strong for Unix plugin discovery.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/pkg/plugins/discovery_unix_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/pkg/plugins/discovery_windows.go -->
# sources/cloud-native/moby/pkg/plugins/discovery_windows.go

Purpose: Windows implementation of plugin spec search paths. `specsPaths` returns `%programdata%\docker\plugins`. State is environment-derived path construction. Dependencies are os and filepath. Risks include empty `programdata`, Windows path permissions, and lack of socket scanning semantics compared with Unix. Test signal is compile-time/platform behavior.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/pkg/plugins/discovery_windows.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/pkg/plugins/errors.go -->
# sources/cloud-native/moby/pkg/plugins/errors.go

Purpose: defines plugin client status errors and helpers for classifying HTTP 404 responses. Important APIs are `statusError.Error`, `IsNotFound`, and `isStatusError`. Control flow checks concrete `*statusError` type and status code; `Error` formats method and remote error text. State is error value fields. Dependencies are fmt and net/http. Risks include lack of `errors.As` support for wrapped status errors and losing status in formatted output. Test signal is through client tests.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/pkg/plugins/errors.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/pkg/plugins/plugin_test.go -->
# sources/cloud-native/moby/pkg/plugins/plugin_test.go

Purpose: tests legacy plugin activation, storage, handler callbacks, wait behavior, `Get`, `GetAll`, and bad-plugin paths. Tests create fake plugin HTTP servers/transports, register extension handlers, populate temp registry paths, and assert manifest/implementation filtering. State includes global plugin storage/handlers, temp plugin specs, and HTTP servers; tests must reset globals carefully. Dependencies include plugin transport, TLS config, httptest, synchronization, and gotest assertions. Risks covered include activation races, handler re-run behavior, missing manifests, unsupported implementations, and registry scan loading. Test signal is strong for legacy plugin manager behavior.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/pkg/plugins/plugin_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/pkg/plugins/pluginrpc-gen/fixtures/foo.go -->
# sources/cloud-native/moby/pkg/plugins/pluginrpc-gen/fixtures/foo.go

Purpose: parser fixture file containing many interface shapes for `pluginrpc-gen` tests. It defines empty interfaces, interfaces with named/unnamed returns, embedded interfaces, aliased imports, selector types, maps/slices/pointers, skipped methods, and timeout annotations. State and runtime behavior are irrelevant; it is source input for AST parsing tests. Dependencies include an aliased `io` import and another fixture package. Risks are fixture drift if parser capabilities change, especially unsupported aliases or unnamed returns. Test signal is high for generator parser edge cases.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/pkg/plugins/pluginrpc-gen/fixtures/foo.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/pkg/plugins/pluginrpc-gen/fixtures/otherfixture/spaceship.go -->
# sources/cloud-native/moby/pkg/plugins/pluginrpc-gen/fixtures/otherfixture/spaceship.go

Purpose: tiny external fixture package used to test selector/import detection in `pluginrpc-gen`. It defines `Spaceship` so fixture interfaces can reference `otherfixture.Spaceship`. State and control flow are absent. Dependencies are none. Risks are minimal; deleting or renaming it would break parser import tests. Test signal is compile-time fixture support.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/pkg/plugins/pluginrpc-gen/fixtures/otherfixture/spaceship.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/pkg/plugins/pluginrpc-gen/main.go -->
# sources/cloud-native/moby/pkg/plugins/pluginrpc-gen/main.go

Purpose: command-line generator entrypoint for producing plugin RPC proxy Go code from an interface. Important APIs are CLI flags `-type`, `-name`, `-i`, `-o`, repeated `-skip`, repeated `-tag`, plus helpers `stringSet`, `checkFlags`, `errorOut`, and `toLower`. Control flow parses flags, stores skip/build-tag sets, parses the requested interface, executes the generated template with interface/RPC metadata, formats Go source, and writes the output file. State is process-global flag variables and skip/build-tag maps. Dependencies include Go formatting, flags, filesystem writes, and parser/template files. Risks include default flag values referencing initial pointer values, fatal `os.Exit`, unsupported interface forms, and generated output overwrites. Test signal is mostly parser/template unit tests rather than full CLI execution.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/pkg/plugins/pluginrpc-gen/main.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/pkg/plugins/pluginrpc-gen/parser.go -->
# sources/cloud-native/moby/pkg/plugins/pluginrpc-gen/parser.go

Purpose: AST parser for extracting named methods and import requirements from an interface for RPC proxy generation. Important APIs are `Parse`, `ParsedPkg`, `function`, `fnArg`, `importSpec`, `parseInterface`, `parseFunc`, `parseArgs`, `parseExpr`, `extractDocumentation`, and `parseTimeoutType`. Control flow parses a Go file with comments, finds the requested type, requires an interface, recursively expands embedded local interfaces, skips configured method names, requires all args/returns to be named, converts supported AST expression forms to type strings, detects selector packages for imports, and extracts timeout annotations from comments. State is parsed package metadata with default long/short timeouts. Dependencies are Go parser/AST/token, reflection for error reporting, and global `skipFuncs`. Risks include unsupported AST forms such as channels/functions/generics, import-name inference from paths with hyphens, map package selector loss when key/value both have selectors, and global skip state. Test signal is extensive in `parser_test.go`.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/pkg/plugins/pluginrpc-gen/parser.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/pkg/plugins/pluginrpc-gen/parser_test.go -->
# sources/cloud-native/moby/pkg/plugins/pluginrpc-gen/parser_test.go

Purpose: unit tests for `pluginrpc-gen` parser behavior using fixture interfaces. Tests cover empty interfaces, non-interface errors, one/multiple functions, unnamed return rejection, embedded interfaces, parsed imports including aliases, skipped functions, and timeout annotations including multiline comments. State is parser output structs and global skip function map. Dependencies are filepath/runtime fixture path resolution and test helpers. Risks covered include AST shape handling and import resolution; generated source execution is not tested here. Test signal is strong for parser contract.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/pkg/plugins/pluginrpc-gen/parser_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/pkg/plugins/pluginrpc-gen/template.go -->
# sources/cloud-native/moby/pkg/plugins/pluginrpc-gen/template.go

Purpose: Go text/template and helper functions for generated plugin RPC client proxies. Important APIs/helpers are `printArgs`, `buildImports`, `marshalType`, `isErr`, `buildTag`, `goduration`, `title`, and `generatedTempl`. Control flow emits generated-code headers/build tags, imports errors/time/plugins plus parsed imports, defines timeout constants, request/response structs per method, marshals errors as strings, calls `CallWithOptions` with short/long timeout, maps response fields back to named returns, and reconstructs errors. State is generated source text only. Dependencies are `text/template`, strings, time, and parser structs. Risks include deprecated `strings.Title`, formatting for unusual durations, named return assumptions, title-casing `id` specially, and generated code compatibility with Go versions. Test signal is `template_test.go` for duration formatting plus parser tests for inputs.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/pkg/plugins/pluginrpc-gen/template.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/pkg/plugins/pluginrpc-gen/template_test.go -->
# sources/cloud-native/moby/pkg/plugins/pluginrpc-gen/template_test.go

Purpose: tests `goduration` formatting used in generated source. Cases cover zero, second, minute, hour, and sub-second durations. State is pure values. Dependencies are time and testing. Risks covered are invalid Go duration expressions; broader template rendering is not directly snapshot-tested. Test signal is narrow but important for generated code validity.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/pkg/plugins/pluginrpc-gen/template_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/pkg/plugins/plugins.go -->
# sources/cloud-native/moby/pkg/plugins/plugins.go

Purpose: legacy v1 plugin registry/activation manager. Important APIs are `Manifest`, `Plugin`, `NewLocalPlugin`, `Get`, `Handle`, `LocalRegistry.GetAll`, plus methods `Name`, `Client`, `Protocol`, `IsV1`, `ScopedPath`, activation helpers, and implementation checks. Control flow caches plugins globally, discovers plugin specs, activates plugins by calling `Plugin.Activate`, stores manifests/clients, coordinates concurrent activation with a condition variable, runs extension-point handlers once per activated plugin, retries discovery for `Get`, and loads all matching plugins concurrently for `GetAll`. State includes global plugin storage, handler registry, per-plugin manifest/client/activation error, and handler-run flag. Dependencies include the legacy client, TLS options, local registry, synchronization, slices, and logging. Risks include global mutable state in tests, activation races, retry delays, handler re-run semantics after new handlers, and stale cached plugins after spec changes. Test signal is strong in `plugin_test.go`.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/pkg/plugins/plugins.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/pkg/plugins/transport/http.go -->
# sources/cloud-native/moby/pkg/plugins/transport/http.go

Purpose: HTTP request factory/round-tripper wrapper for plugin clients. Important APIs are `HTTPTransport`, `NewHTTPTransport`, and `HTTPTransport.NewRequest`. Control flow ensures service paths start with `/`, creates POST requests with the plugin body, sets the plugin version `Accept` header, and overrides URL scheme/host using transport fields while delegating actual round trips to the embedded transport. State is scheme/address configuration. Dependencies are HTTP and IO. Risks include request URL construction for unusual service names, POST-only semantics, and Accept header compatibility. Test signal is `http_test.go`.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/pkg/plugins/transport/http.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/pkg/plugins/transport/http_test.go -->
# sources/cloud-native/moby/pkg/plugins/transport/http_test.go

Purpose: unit test for plugin `HTTPTransport.NewRequest`. It asserts path normalization, POST method, URL scheme/host assignment, body propagation, and version MIME accept header. State is in-memory request data. Dependencies are gotest assertions and net/http. Risks covered are request construction regressions; actual network transport behavior is not tested. Test signal is focused and fast.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/pkg/plugins/transport/http_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/pkg/plugins/transport/mimetype.go -->
# sources/cloud-native/moby/pkg/plugins/transport/mimetype.go

Purpose: defines the plugin protocol version MIME type sent in plugin client `Accept` headers. `VersionMimetype` is aliased by the parent `plugins` package. State and control flow are absent. Dependencies are none. Risks are compatibility-sensitive: changing the string can break legacy plugin negotiation. Test signal is through transport and client tests.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/pkg/plugins/transport/mimetype.go -->
