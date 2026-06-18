# subset-b-000168 Research

Grouped source research for Moby daemon archive, attach, auth/build callbacks, classic builder backend, Dockerfile evaluator, remote context, git, and tarsum files. Each section preserves the source path in its title and is bounded by reconciliation markers.

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/archive_windows.go -->
## sources/cloud-native/moby/daemon/archive_windows.go

**Purpose:** Implements Windows-specific container filesystem archive operations used by `docker cp`, archive download/upload, and path stat APIs. It handles mounted rootfs and volume lifecycle while respecting Windows Hyper-V isolation limits.

**Important APIs:** `containerStatPath`, `containerArchivePath`, `containerExtractToDir`, `containerCopy`, and `isOnlineFSOperationPermitted` are daemon methods over `*container.Container`. They normalize slash paths to Windows paths, mount the container and volumes, resolve paths through container helpers, and use `chrootarchive` plus `archive` tar options.

**Control flow:** Each public helper locks the container, checks whether online filesystem access is permitted, mounts the rootfs, mounts volumes, resolves the requested path, performs stat/tar/untar work, logs an event, and then unmounts. Archive readers deliberately hold the container lock until the returned `ReadCloser` is closed by wrapping the underlying tar stream.

**State and persistence:** No durable state is created except extracted archive contents in the container filesystem. Temporary state consists of mount references, volume attachments, and deferred cleanup. Event log actions include `ArchivePath`, `ExtractToDir`, and `Copy`.

**Dependencies and integration:** Depends on daemon mount/unmount, container path resolution, `go-archive`, `chrootarchive`, compression, `errdefs`, and ioutils wrappers. It integrates with HTTP archive/copy endpoints and volume event logging.

**Risks:** Cleanup ordering is critical because leaked mounts or locks can wedge container operations. Windows drive-letter handling and symlink resolution are security-sensitive. `copyUIDGID` is silently ignored on Windows. Running Hyper-V containers reject online filesystem operations.

**Test signals:** This file has no adjacent direct test in this subset; coverage is likely endpoint/integration based. Useful regression cases include archive reader early close, symlink path rebasing, drive-letter extraction validation, and Hyper-V running-container rejection.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/archive_windows.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/attach.go -->
## sources/cloud-native/moby/daemon/attach.go

**Purpose:** Implements daemon-side attach for API clients and raw internal callers, wiring container stdio/log streams to client streams with detach handling, multiplexing, and event logging.

**Important APIs:** `ContainerAttach` validates detach keys, resolves the container, rejects paused/restarting states, builds `stream.AttachConfig`, obtains client streams, optionally muxes stdout/stderr, and delegates to `containerAttach`. `ContainerAttachRaw` is used by builder execution and internal callers. `containerAttach` can replay logs, stream live IO, and handle detach/error outcomes.

**Control flow:** Attach config is registered with `ctr.StreamConfig.AttachStreams`. For log replay, the logger must implement `logger.LogReader`; messages are copied to stdout/stderr according to source. For live streaming, stdin may be buffered through a pipe, disabled if `OpenStdin` is false, and `CopyStreams` runs under the container attach context.

**State and persistence:** No persistent data is written. Runtime state includes stream registrations, goroutines for client disconnect and stdin pipe copying, logger read watchers, and attach/detach events.

**Dependencies and integration:** Uses `stdcopy`, internal `stdcopymux`, `stream.AttachConfig`, container logger APIs, terminal detach parsing, and backend attach config. The classic Dockerfile builder depends on `ContainerAttachRaw` while running build containers.

**Risks:** Goroutine and pipe cleanup depends on context cancellation and stream closure. Log replay uses `context.TODO`, so cancellation is mediated by watcher cleanup rather than request context. StdinOnce waits for container stop, which can block if lifecycle assumptions break.

**Test signals:** No direct tests in this subset. Integration coverage should exercise TTY vs non-TTY muxing, detach key errors, paused/restarting conflicts, logs-only attach, stream disconnect, and raw attach synchronization via the `attached` channel.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/attach.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/auth.go -->
## sources/cloud-native/moby/daemon/auth.go

**Purpose:** Provides the daemon registry authentication API shim.

**Important APIs:** `AuthenticateToRegistry(ctx, authConfig)` calls `daemon.registryService.Auth` with the supplied `registry.AuthConfig` and Docker user agent from `dockerversion.DockerUserAgent(ctx)`.

**Control flow:** There is no branching; validation and registry interaction are delegated to the registry service.

**State and persistence:** No local state is stored. Any credential verification side effects belong to the registry service or remote registry.

**Dependencies and integration:** Integrates daemon API auth endpoint handling with `daemon.registryService` and API registry types.

**Risks:** Behavior is entirely dependent on the registry service contract. Context user-agent extraction matters for remote registry requests and diagnostics.

**Test signals:** No direct test in this subset; registry package tests elsewhere should cover auth behavior. This wrapper mainly needs compile/interface coverage.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/auth.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/build.go -->
## sources/cloud-native/moby/daemon/build.go

**Purpose:** Supplies daemon callbacks used by BuildKit to log image create/tag events when BuildKit bypasses normal image-service paths.

**Important APIs:** `ImageExportedByBuildkit` logs `events.ActionCreate` for an untagged image ID. `ImageNamedByBuildkit` logs `events.ActionTag` using the descriptor digest and familiar tag string.

**Control flow:** Both functions directly call `daemon.imageService.LogImageEvent`.

**State and persistence:** They do not persist images themselves; they add daemon event records for observability.

**Dependencies and integration:** Integrates BuildKit builder callbacks, distribution references, OCI descriptors, and daemon image-service event logging.

**Risks:** Incorrect ID/reference choice would produce confusing event streams, especially under the containerd image store. These functions assume BuildKit has already completed export/tag operations.

**Test signals:** No direct test in this subset. Event stream integration tests should confirm untagged BuildKit exports and BuildKit-managed tags emit expected daemon events.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/build.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/builder/backend/backend.go -->
## sources/cloud-native/moby/daemon/builder/backend/backend.go

**Purpose:** Exposes build functionality to the API router and selects between classic Dockerfile builder and BuildKit. It also handles tag application, squashing, cache prune, cancellation, and BuildKit gRPC registration.

**Important APIs:** `ImageComponent` abstracts image tagging/squashing. `Builder` abstracts classic build execution. `Backend` stores classic builder, BuildKit builder, image component, and events service. `NewBackend`, `RegisterGRPC`, `Build`, `PruneCache`, `Cancel`, and `squashBuild` are the main entry points.

**Control flow:** `Build` parses tags, checks `options.Version`, runs BuildKit or classic builder, optionally squashes the result, emits aux image ID after squashing, prints classic-builder success text, and tags non-BuildKit images. `PruneCache` delegates to BuildKit and logs a builder prune event.

**State and persistence:** Build results create/tag/squash images via downstream components. Backend itself is stateless beyond component references. Prune emits event metadata with reclaimed bytes.

**Dependencies and integration:** Integrates API `buildbackend.BuildConfig`, BuildKit `builder-next`, daemon image component, events, distribution references, and classic builder result objects.

**Risks:** `PruneCache` and `Cancel` assume `buildkit` is non-nil. Classic tag printing only occurs for non-BuildKit builds. Squash must preserve correct base image ID from `FromImage`.

**Test signals:** Adjacent tag tests are not listed here, but `tag.go` logic is testable. Backend integration needs coverage for BuildKit vs classic selection, nil results, squash aux emission, duplicate tags, and prune events.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/builder/backend/backend.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/builder/backend/tag.go -->
## sources/cloud-native/moby/daemon/builder/backend/tag.go

**Purpose:** Parses and applies build tags after a successful classic build.

**Important APIs:** `tagImages` iterates normalized references, calls `ImageComponent.TagImage`, and prints success. `sanitizeRepoAndTags` normalizes raw tag strings, ignores empty entries, rejects digested references, applies default tags, and removes duplicates.

**Control flow:** Tag parsing uses `reference.ParseNormalizedNamed`, rejects `reference.Digested`, then canonicalizes through `reference.TagNameOnly`. Deduplication is based on the normalized string.

**State and persistence:** `tagImages` mutates daemon image tag state through `ImageComponent`. `sanitizeRepoAndTags` only creates an in-memory reference slice.

**Dependencies and integration:** Used by build backend after image creation. Depends on distribution reference parsing and daemon internal `image.ID`.

**Risks:** Digest-containing tags are rejected because build tags must be mutable names, not content addresses. Deduping after default-tag normalization prevents repeated tag writes.

**Test signals:** Should be covered by backend/tag unit tests or build API tests. Key cases are empty tags, duplicate tags, implicit `latest`, invalid references, and digest rejection.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/builder/backend/tag.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/builder/builder.go -->
## sources/cloud-native/moby/daemon/builder/builder.go

**Purpose:** Defines shared interfaces between daemon build implementations and Dockerfile evaluator code.

**Important APIs/types:** `Source` supplies `Root`, `Close`, and deterministic `Hash`. `Backend` combines image, execution, commit, workdir, create-image, and image-cache operations. `ImageBackend`, `ExecBackend`, `Result`, `ImageCacheBuilder`, `ImageCache`, `Image`, `ROLayer`, and `RWLayer` define the classic builder dependency boundary.

**Control flow:** This file has no executable orchestration; it is a contract package.

**State and persistence:** Implementations behind these interfaces manage images, layers, containers, cache entries, and temporary build contexts. The interfaces explicitly model layer release/commit and source cleanup.

**Dependencies and integration:** Used by Dockerfile builder, daemon image/container backends, remote contexts, and tests/mocks. It decouples evaluator logic from concrete daemon services.

**Risks:** Interface shape is broad; changes affect many packages. Resource lifecycle methods (`Close`, `Release`, `Commit`) are critical because leaks occur outside this package.

**Test signals:** Mock implementations in `mockbackend_test.go` exercise much of this surface. Compile-time conformance from real daemon components is an important signal.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/builder/builder.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/builder/dockerfile/buildargs.go -->
## sources/cloud-native/moby/daemon/builder/dockerfile/buildargs.go

**Purpose:** Tracks Dockerfile `ARG` values, meta args before `FROM`, user-supplied build args, referenced args, builtin proxy args, and warning behavior for unused args.

**Important APIs/types:** `BuildArgs` stores `allowedBuildArgs`, `allowedMetaArgs`, `referencedArgs`, and `argsFromOptions`. Methods include `NewBuildArgs`, `Clone`, `MergeReferencedArgs`, `WarnOnUnusedBuildArgs`, `ResetAllowed`, `AddMetaArg`, `AddArg`, `IsReferencedOrNotBuiltin`, `GetAllAllowed`, `GetAllMeta`, `FilterAllowed`, and internal lookup helpers.

**Control flow:** Lookup prefers user-supplied non-nil option values, then Dockerfile defaults, then meta args for unset regular args. Filtering removes args already present in image env. Unused warnings exclude builtin proxy args unless referenced.

**State and persistence:** State is in-memory for one build and per-stage clones. It influences cache keys and command environments but does not persist directly into the image except through dispatchers.

**Dependencies and integration:** Used by meta-arg processing, `FROM` expansion, `ARG`, `RUN`, and cache-command construction.

**Risks:** Builtin proxy args are intentionally transparent; changing reference logic can alter image history/cache behavior. Nil pointer values represent declared-but-unset args and must be preserved.

**Test signals:** `buildargs_test.go` covers allowed/meta lookup, unused warnings, and builtin reference filtering.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/builder/dockerfile/buildargs.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/builder/dockerfile/buildargs_test.go -->
## sources/cloud-native/moby/daemon/builder/dockerfile/buildargs_test.go

**Purpose:** Unit tests for build-arg lookup, meta-arg handling, unused-arg warnings, and builtin proxy arg reference behavior.

**Important APIs:** Tests call `NewBuildArgs`, `AddArg`, `AddMetaArg`, `GetAllAllowed`, `GetAllMeta`, `WarnOnUnusedBuildArgs`, and `IsReferencedOrNotBuiltin`.

**Control flow:** Table-like assertions construct option/default values, then compare resulting maps or output text. The builtin test asserts an unreferenced proxy arg is treated transparently.

**State and persistence:** Uses in-memory `BuildArgs`; no filesystem or daemon state.

**Dependencies and integration:** Uses Go testing and buffers. It protects semantics used by `RUN`, `FROM`, and build cache formation.

**Risks:** Tests are narrow and do not cover `FilterAllowed`, clone merging, or nil-option edge cases exhaustively.

**Test signals:** Strong direct signal for the most visible `BuildArgs` behaviors: precedence, warnings, and builtin transparency.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/builder/dockerfile/buildargs_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/builder/dockerfile/builder.go -->
## sources/cloud-native/moby/daemon/builder/dockerfile/builder.go

**Purpose:** Implements the classic Dockerfile builder orchestration: context detection, builder initialization, Dockerfile parsing, stage execution, cache use, progress output, and commit-change support.

**Important APIs/types:** `BuildManager` owns daemon backend, path cache, and ID mapping. `NewBuildManager`, `Build`, `builderOptions`, `Builder`, `newBuilder`, `buildLabelOptions`, `build`, `emitImageID`, `processMetaArg`, `printCommand`, `dispatchDockerfileWithCancellation`, `BuildFromConfig`, and conversion helpers are key.

**Control flow:** `BuildManager.Build` defaults Dockerfile name, detects remote/archive context, creates a cancellable context and `Builder`, then runs `build`. `build` parses stages/meta args, applies target truncation and CLI labels, prints warnings, dispatches stages, and returns image ID. Dispatch loops process meta args first, then each `FROM` stage and instruction with cancellation checks.

**State and persistence:** Uses a shared `syncmap` path cache for copy hashes, per-build `imageSources`, `containerManager`, `imageProber`, and build args. Persistent outputs are committed images/layers through backend methods.

**Dependencies and integration:** Depends on BuildKit Dockerfile parser/instructions, remotecontext, daemon builder interfaces, platform parsing, metrics, and progress writers.

**Risks:** Classic builder compatibility depends on exact output formatting, stage order, label sorting, and cache-key command strings. Context cleanup is deferred and must run after all source users finish.

**Test signals:** Broader behavior is covered by dispatcher/internals tests plus daemon integration tests. Direct risks include target selection, meta arg expansion, empty Dockerfile errors, and commit-change command whitelist.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/builder/dockerfile/builder.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/builder/dockerfile/builder_unix.go -->
## sources/cloud-native/moby/daemon/builder/dockerfile/builder_unix.go

**Purpose:** Defines the default shell for non-Windows classic Dockerfile builds.

**Important APIs:** `defaultShellForOS` returns `[]string{"/bin/sh", "-c"}` regardless of requested image OS on Unix daemon builds.

**Control flow:** No branching.

**State and persistence:** No state.

**Dependencies and integration:** Used by `getShell`, `resolveCmdLine`, and NOP-comment command construction for RUN/CMD/ENTRYPOINT and commit metadata.

**Risks:** LCOW or cross-platform behavior is handled elsewhere; this file assumes Unix daemon semantics.

**Test signals:** Indirectly covered by Unix dispatcher normalization and command resolution tests.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/builder/dockerfile/builder_unix.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/builder/dockerfile/builder_windows.go -->
## sources/cloud-native/moby/daemon/builder/dockerfile/builder_windows.go

**Purpose:** Defines Windows default shell behavior and a Docker-specific absolute-path helper.

**Important APIs:** `defaultShellForOS(os)` returns Linux shell for LCOW (`os == "linux"`) and `cmd /S /C` for Windows containers. `isAbs` treats drive-qualified paths and separator-prefixed paths as absolute.

**Control flow:** Simple OS branch for shell selection; `isAbs` combines `filepath.IsAbs` and separator prefix checks.

**State and persistence:** No state.

**Dependencies and integration:** Used by Windows dispatchers and path normalization. It affects command line generation and WORKDIR/COPY path interpretation.

**Risks:** Windows path semantics differ from Go's `filepath.IsAbs`; this helper prevents Dockerfile paths like `\windows` from being misclassified.

**Test signals:** Windows dispatcher tests cover workdir normalization paths that rely on `isAbs`.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/builder/dockerfile/builder_windows.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/builder/dockerfile/containerbackend.go -->
## sources/cloud-native/moby/daemon/builder/dockerfile/containerbackend.go

**Purpose:** Manages temporary build containers for classic Dockerfile `RUN`, `WORKDIR` creation, and Windows helper execution.

**Important APIs/types:** `containerManager` tracks `tmpContainers` and an execution backend. `Create`, `Run`, `RemoveAll`, `statusCodeError`, `errCancelled`, and `logCancellationError` implement lifecycle and error adaptation.

**Control flow:** `Run` starts attach in a goroutine, waits for attach readiness, starts a cancellation watcher that force-removes the container if context is canceled, starts the container, waits for attach completion, then waits for non-running status. Nonzero exit codes become `statusCodeError`.

**State and persistence:** Tracks temporary container IDs in memory and removes them with force/remove-volume. Persistent container side effects are committed by callers, not here.

**Dependencies and integration:** Uses builder `ExecBackend` methods, daemon backend container configs, container wait states, and string ID formatting. Called by RUN dispatch and internal Windows account lookup.

**Risks:** Ordering around attach/start/wait is concurrency-sensitive. Cancellation races are handled via `finished` and `cancelErrCh`; mistakes can deadlock. `RemoveAll` must tolerate already-removed containers.

**Test signals:** Mock backend implements required methods, but direct unit tests are not in this subset. Integration should cover cancellation, nonzero exit messages, and cleanup under `--rm`/`--force-rm`.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/builder/dockerfile/containerbackend.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/builder/dockerfile/copy.go -->
## sources/cloud-native/moby/daemon/builder/dockerfile/copy.go

**Purpose:** Implements shared ADD/COPY source resolution, hashing, URL download, wildcard expansion, and filesystem copy/decompression logic for the classic builder.

**Important APIs/types:** `copyInfo`, `copyInstruction`, `copier`, `copierFromDispatchRequest`, `createCopyInstruction`, `calcCopyInfo`, `copyWithWildcards`, `copyInfoForFile`, `walkSource`, `sourceDownloader`, `downloadSource`, `identity`, `copyFileOptions`, `performCopyForInfo`, `copyDirectory`, `copyFile`, and `isExistingDirectory`.

**Control flow:** A dispatcher builds a `copier`, source paths become `copyInfo` records from context, image mount, or downloaded URL. Wildcards walk the source tree. File sources hash with `source.Hash`; directories hash sorted child hashes. Copy execution resolves source/destination through symlink scope, copies directories or files with tar helpers, and optionally untars local archives for ADD.

**State and persistence:** Per-build path cache stores image-source hashes by image ID plus path. URL downloads create temporary directories cleaned by `Cleanup`. Copy writes to an RW layer that is later committed by `performCopy`.

**Dependencies and integration:** Uses remotecontext, URL utilities, progress output, longpath temp dirs, go-archive archiver, symlink scope helpers, user chown helpers, and platform-specific `normalizeDest`/`fixPermissions`.

**Risks:** This is security-sensitive for path traversal, symlinks, remote downloads, archive decompression, permission ownership, and cache correctness. Missing `Cleanup` leaks temp dirs/RW layers. Directory hash order must remain deterministic.

**Test signals:** `copy_test.go` covers directory existence and download filename inference; platform files add path behavior. Full ADD/COPY behavior needs integration coverage for .dockerignore, wildcard matching, remote URLs, archive extraction, and COPY --from.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/builder/dockerfile/copy.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/builder/dockerfile/copy_test.go -->
## sources/cloud-native/moby/daemon/builder/dockerfile/copy_test.go

**Purpose:** Tests focused helpers in ADD/COPY implementation.

**Important APIs:** `TestIsExistingDirectory` validates existing directory, existing file, and missing path handling. `TestGetFilenameForDownload` validates URL path and `Content-Disposition` filename inference.

**Control flow:** Tests create temporary files/directories or synthetic HTTP responses and assert boolean/name results.

**State and persistence:** Uses temp filesystem state only.

**Dependencies and integration:** Protects helper behavior used by `performCopyForInfo` and `downloadSource`.

**Risks:** Coverage is intentionally narrow; it does not exercise copy execution, wildcards, hashes, URL network fetching, or chown behavior.

**Test signals:** Good direct signal for filename inference edge cases, including unnamed downloads and trailing slash handling.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/builder/dockerfile/copy_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/builder/dockerfile/copy_unix.go -->
## sources/cloud-native/moby/daemon/builder/dockerfile/copy_unix.go

**Purpose:** Provides Unix-specific ADD/COPY destination normalization, wildcard detection, permission fixing, and source path validation.

**Important APIs:** `fixPermissions` walks the source tree and `Lchown`s corresponding destination paths, optionally skipping an existing destination root. `normalizeDest` resolves relative destinations under WORKDIR while preserving trailing slashes. `containsWildcards` honors backslash escaping. `validateCopySourcePath` is a no-op on Unix.

**Control flow:** Permission fixing walks source paths and maps each relative path to the destination. Destination normalization uses POSIX path semantics even before conversion to daemon filesystem paths.

**State and persistence:** Mutates filesystem ownership on copied files/directories in the RW layer.

**Dependencies and integration:** Used by common copy execution in `copy.go` and `internals.go`; depends on `os`, `filepath`, and path semantics.

**Risks:** Chown must avoid changing pre-existing directory roots unless override is requested. Wildcard escaping differs from Windows and impacts matching compatibility.

**Test signals:** Direct tests for Unix normalizeWorkdir exist in dispatcher Unix tests; copy-specific Unix chown and wildcard behavior need integration tests.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/builder/dockerfile/copy_unix.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/builder/dockerfile/copy_windows.go -->
## sources/cloud-native/moby/daemon/builder/dockerfile/copy_windows.go

**Purpose:** Provides Windows-specific ADD/COPY permissions, destination normalization, wildcard detection, and restrictions on copying from sensitive system paths.

**Important APIs:** `pathDenyList`, `fixPermissions`, `fixPermissionsReexec`, `fixPermissionsWindows`, `normalizeDest`, `containsWildcards`, and `validateCopySourcePath`. Permission changes run via a reexec helper and Windows security descriptors/SIDs.

**Control flow:** `fixPermissions` runs `windows-fix-permissions` when a SID is present. `normalizeDest` rejects non-`C:` destinations, strips drive letters, resolves relative paths under system-drive WORKDIR, and preserves trailing separators. `validateCopySourcePath` denies `c:\` and `c:\windows` when copying from image sources.

**State and persistence:** Mutates ACL/owner metadata on copied destination paths. Registers a reexec command at init time.

**Dependencies and integration:** Uses go-winio privileges, Windows syscalls, reexec, system SDDL constants, and common copy logic.

**Risks:** Windows ACL handling requires elevated privileges and correct SID mapping. Destination drive rules are compatibility-sensitive. Deny-list normalization must catch drive-relative oddities such as `c:.`.

**Test signals:** `internals_windows_test.go` covers `normalizeDest`; broader ACL and deny-list behavior likely needs Windows integration tests.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/builder/dockerfile/copy_windows.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/builder/dockerfile/dispatchers.go -->
## sources/cloud-native/moby/daemon/builder/dockerfile/dispatchers.go

**Purpose:** Implements Dockerfile instruction handlers for the classic builder.

**Important APIs:** Dispatchers include `dispatchEnv`, `dispatchMaintainer`, `dispatchLabel`, `dispatchAdd`, `dispatchCopy`, `initializeStage`, `dispatchTriggeredOnBuild`, `getExpandedString`, `getImageOrStage`, `getFromImage`, `dispatchOnbuild`, `dispatchWorkdir`, `dispatchRun`, `prependEnvOnCmd`, `dispatchCmd`, `dispatchHealthcheck`, `dispatchEntrypoint`, `dispatchExpose`, port parsing helpers, `dispatchUser`, `dispatchVolume`, `dispatchStopSignal`, `dispatchArg`, and `dispatchShell`.

**Control flow:** `FROM` resolves platform and image/stage references, resets cache, starts dispatch state, and runs ONBUILD triggers. Metadata commands mutate run config and commit NOP layers. `RUN` builds cache config, creates/runs a container on miss, converts nonzero exit to JSON stream error, and commits. ADD/COPY delegate to copier and performCopy. EXPOSE parses Docker port syntax.

**State and persistence:** Mutates `dispatchState.runConfig`, build args, image ID, and stage results. Commits images/layers through builder internals. Records cache history through NOP command strings.

**Dependencies and integration:** Uses BuildKit instruction AST types, shell expansion, daemon image/cache/container backends, network port types, signal parsing, and platform parsing.

**Risks:** This is compatibility-critical. Cache key strings, Windows `ArgsEscaped`, ONBUILD recursion, build-arg transparency, and port parsing all affect user-visible behavior. Unsupported BuildKit-only flags must fail clearly.

**Test signals:** `dispatchers_test.go`, platform-specific dispatcher tests, and evaluator tests cover many handlers, port parsing, build args, unsupported options, and workdir normalization.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/builder/dockerfile/dispatchers.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/builder/dockerfile/dispatchers_test.go -->
## sources/cloud-native/moby/daemon/builder/dockerfile/dispatchers_test.go

**Purpose:** Broad unit coverage for Dockerfile instruction dispatch behavior.

**Important APIs:** Exercises env, maintainer, label, FROM scratch/args/multistage, ONBUILD, WORKDIR, CMD, HEALTHCHECK, ENTRYPOINT, EXPOSE, USER, VOLUME, STOPSIGNAL, ARG, SHELL, `prependEnvOnCmd`, RUN with build args, healthcheck suppression, unsupported options, and port/network parsing helpers.

**Control flow:** Tests build dispatch requests with mock builders/configs and assert resulting `runConfig`, errors, or parsed port maps.

**State and persistence:** Uses mocks and in-memory config state; no real daemon containers.

**Dependencies and integration:** Depends on mock backend and instruction parsing helpers. It is the main safety net for `dispatchers.go`.

**Risks:** Because mocks bypass real container/image backends, tests cannot fully validate commit, runtime attach, platform-specific container behavior, or actual image cache storage.

**Test signals:** Strong direct signal for parser-to-dispatch semantics and many legacy compatibility cases, especially port grammar and build-arg cache command construction.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/builder/dockerfile/dispatchers_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/builder/dockerfile/dispatchers_unix.go -->
## sources/cloud-native/moby/daemon/builder/dockerfile/dispatchers_unix.go

**Purpose:** Provides Unix-specific WORKDIR normalization and command-line resolution.

**Important APIs:** `normalizeWorkdir` rejects empty requests, converts slashes, resolves relative paths under current workdir, and cleans absolute paths. `resolveCmdLine` prepends the configured shell for shell-form commands and always returns `argsEscaped=false`.

**Control flow:** Simple path branch on absolute vs relative; shell prepending depends on `ShellDependantCmdLine.PrependShell`.

**State and persistence:** No direct persistence, but output becomes image `WorkingDir`, `Cmd`, `Entrypoint`, and cache command data.

**Dependencies and integration:** Used by `dispatchWorkdir`, `dispatchRun`, `dispatchCmd`, and `dispatchEntrypoint`.

**Risks:** Path cleaning must preserve Docker compatibility for relative workdirs. Command resolution must match legacy shell-form behavior.

**Test signals:** `dispatchers_unix_test.go` covers workdir normalization cases.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/builder/dockerfile/dispatchers_unix.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/builder/dockerfile/dispatchers_unix_test.go -->
## sources/cloud-native/moby/daemon/builder/dockerfile/dispatchers_unix_test.go

**Purpose:** Tests Unix `normalizeWorkdir` behavior.

**Important APIs:** `TestNormalizeWorkdir` validates empty path rejection and normalization of absolute/relative workdir requests.

**Control flow:** Table assertions compare normalized output or expected errors.

**State and persistence:** No persistent state.

**Dependencies and integration:** Protects `dispatchWorkdir` Unix path semantics.

**Risks:** Narrow coverage; command-line resolution is not directly tested here.

**Test signals:** Good platform-specific signal for WORKDIR compatibility on Unix.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/builder/dockerfile/dispatchers_unix_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/builder/dockerfile/dispatchers_windows.go -->
## sources/cloud-native/moby/daemon/builder/dockerfile/dispatchers_windows.go

**Purpose:** Implements Windows-specific WORKDIR normalization and command-line resolution for classic builds, including LCOW behavior.

**Important APIs:** `normalizeWorkdir`, `normalizeWorkdirUnix`, `normalizeWorkdirWindows`, and `resolveCmdLine`. A lazy regexp detects invalid `C:.` drive-current-directory forms.

**Control flow:** `normalizeWorkdir` dispatches to Windows or Unix normalization based on target platform. Windows normalization cleans current/requested paths, rejects drive-current-directory forms, converts relative or separator-rooted paths to `C:\...`, joins with current when appropriate, and uppercases drive letters. `resolveCmdLine` returns single escaped shell-form strings for WCOW and normal argv arrays for exec form or LCOW.

**State and persistence:** Affects persisted image `WorkingDir`, `Cmd`, `Entrypoint`, `ArgsEscaped`, and cache keys.

**Dependencies and integration:** Used by dispatchers on Windows daemon builds. It integrates with container runtime expectations around HCS command-line escaping.

**Risks:** Windows shell-form handling intentionally uses original Dockerfile text, not parsed args, to preserve `cmd.exe` behavior. Small changes can break compatibility. Drive/path normalization is security- and UX-sensitive.

**Test signals:** `dispatchers_windows_test.go` covers workdir normalization. Dispatcher tests also validate warnings around mixed shell/exec forms.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/builder/dockerfile/dispatchers_windows.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/builder/dockerfile/dispatchers_windows_test.go -->
## sources/cloud-native/moby/daemon/builder/dockerfile/dispatchers_windows_test.go

**Purpose:** Tests Windows `normalizeWorkdir` compatibility behavior.

**Important APIs:** `TestNormalizeWorkdir` exercises Windows path cleaning, relative joining, drive-letter casing, separator-rooted paths, and invalid drive-current-directory forms.

**Control flow:** Table-driven cases compare returned path or expected error.

**State and persistence:** No persistent state.

**Dependencies and integration:** Protects `dispatchWorkdir` behavior for Windows container images.

**Risks:** Does not test `resolveCmdLine`, `ArgsEscaped`, or warnings for CMD/ENTRYPOINT combinations.

**Test signals:** Good direct signal for one of the most error-prone platform compatibility helpers.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/builder/dockerfile/dispatchers_windows_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/builder/dockerfile/evaluator.go -->
## sources/cloud-native/moby/daemon/builder/dockerfile/evaluator.go

**Purpose:** Defines the dispatch jump table and per-stage dispatch state for classic Dockerfile evaluation.

**Important APIs/types:** `dispatch`, `dispatchState`, `newDispatchState`, `stagesBuildResults`, `newStagesBuildResults`, `getByName`, `validateIndex`, `get`, `checkStageNameAvailable`, `commitStage`, `dispatchRequest`, `newDispatchRequest`, `updateRunConfig`, `hasFromImage`, `beginStage`, and `setDefaultPath`.

**Control flow:** `dispatch` performs platform checks, builds environment with allowed build args, expands single-word commands, defers intermediate container cleanup according to options, and switches on concrete instruction type. Stage result lookup supports names and numeric indexes while rejecting current-stage self-reference.

**State and persistence:** `dispatchState` holds mutable run config, maintainer, image ID, base image, stage name, build args, and OS. Stage results persist run configs in memory for later `COPY --from` and `FROM <stage>`.

**Dependencies and integration:** Connects BuildKit parser instruction types to dispatcher functions, builder options, OCI default path env, image OS checks, and error definitions.

**Risks:** Cleanup defers run after every dispatch and depend on `Remove`/`ForceRemove`. Stage indexing has subtle boundary behavior. Default PATH injection affects image config and cache results.

**Test signals:** `evaluator_test.go` covers dispatch routing. Dispatcher and internals tests cover state-copy behavior and stage-related cases.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/builder/dockerfile/evaluator.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/builder/dockerfile/evaluator_test.go -->
## sources/cloud-native/moby/daemon/builder/dockerfile/evaluator_test.go

**Purpose:** Verifies that parsed Dockerfile commands are dispatched successfully through the evaluator jump table.

**Important APIs:** `TestDispatch` uses `dispatchTestCase` entries and `TestMain` setup to run command dispatch scenarios.

**Control flow:** Test cases parse or construct commands, pass them through `dispatch`, and assert expected errors/state.

**State and persistence:** Uses in-memory dispatch state and mocks.

**Dependencies and integration:** Protects evaluator-to-dispatcher wiring rather than real daemon side effects.

**Risks:** It does not replace instruction-specific tests; errors in backend integration, container lifecycle, or image persistence can pass these tests.

**Test signals:** Useful compile/runtime signal that supported command types are recognized and unsupported paths fail predictably.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/builder/dockerfile/evaluator_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/builder/dockerfile/imagecontext.go -->
## sources/cloud-native/moby/daemon/builder/dockerfile/imagecontext.go

**Purpose:** Manages mounted image sources used for base images, cache/export layers, scratch images, and `COPY --from`.

**Important APIs/types:** `getAndMountFunc`, `imageSources`, `newImageSources`, `Get`, `Unmount`, `Add`, `imageMount`, `newImageMount`, `unmount`, `Image`, `NewRWLayer`, and `ImageID`.

**Control flow:** `newImageSources` builds a closure over backend image retrieval with pull policy based on local-only and `PullParent`. `Get` returns cached mounts by image ID/ref or fetches and adds a new mount. `Add` synthesizes image metadata for nil/scratch images and appends to mount cleanup list.

**State and persistence:** Maintains in-memory mount list and image-ID cache. Underlying layers are released by `Unmount`; exported images are created elsewhere.

**Dependencies and integration:** Uses builder backend image retrieval, build options auth/output/platform, internal image type, and container platform defaults.

**Risks:** Mount release failures can leak layer refs. Scratch image OS handling differs on Windows daemon vs target platform. Cache keying only by passed ID/ref can miss aliases until `Add` records actual image ID.

**Test signals:** `imagecontext_test.go` covers scratch add behavior, platform propagation, and Get adding mounts.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/builder/dockerfile/imagecontext.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/builder/dockerfile/imagecontext_test.go -->
## sources/cloud-native/moby/daemon/builder/dockerfile/imagecontext_test.go

**Purpose:** Tests image source mount tracking and scratch image platform behavior.

**Important APIs:** Helper constructors create mock image sources/mounts. Tests cover `Add` with scratch images, platform population, immutability of input platform, nil platform defaults, and `Get` adding returned mounts.

**Control flow:** Tests instantiate `imageSources`, call `Add` or `Get`, then inspect `mounts`, image metadata, and platform fields.

**State and persistence:** In-memory only.

**Dependencies and integration:** Uses mock image/layer implementations from test support.

**Risks:** Tests do not exercise real layer release failures or backend pull-policy behavior.

**Test signals:** Strong direct signal for scratch handling and mount list management.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/builder/dockerfile/imagecontext_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/builder/dockerfile/imageprobe.go -->
## sources/cloud-native/moby/daemon/builder/dockerfile/imageprobe.go

**Purpose:** Wraps image cache probing for classic builder steps and enforces cache-busted behavior after the first miss.

**Important APIs/types:** `ImageProber`, `resetFunc`, `imageProber`, `newImageProber`, `Reset`, `Probe`, and `nopProber`.

**Control flow:** `newImageProber` returns `nopProber` for `NoCache`, otherwise builds an image cache from `cacheFrom`. `Probe` skips if cache is busted, asks cache for parent/runconfig/platform match, marks busted on miss, and returns cached image ID on hit. `Reset` rebuilds cache at each new stage.

**State and persistence:** In-memory cache handle and `cacheBusted` boolean. Persistent cache entries are owned by backend image cache implementation.

**Dependencies and integration:** Called by `initializeStage`, `probeCache`, and build internals. Depends on `builder.ImageCacheBuilder`.

**Risks:** One miss disables further cache probing within the current stage, matching classic builder semantics. Incorrect reset scope would make cache too aggressive or too weak.

**Test signals:** Indirectly covered through dispatcher/internals tests. Dedicated tests would help for `NoCache`, miss-after-hit, and reset behavior.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/builder/dockerfile/imageprobe.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/builder/dockerfile/internals.go -->
## sources/cloud-native/moby/daemon/builder/dockerfile/internals.go

**Purpose:** Provides lower-level builder operations for committing layers, exporting copied RW layers, cache probing, container creation, host config construction, and run-config copying.

**Important APIs:** `getArchiver`, `commit`, `commitContainer`, `exportImage`, `performCopy`, `createDestInfo`, `getSourceHashFromInfos`, `hashStringSlice`, run-config modifiers, `copyRunConfig`, `getShell`, `probeCache`, `probeAndCreate`, `create`, `hostConfigFromOptions`, and `getPlatform`.

**Control flow:** Metadata commands call `commit`, which probes cache and creates a temporary container if needed, then commits through backend. ADD/COPY calls `performCopy`, computes source hash, probes cache, mounts destination image, creates RW layer, normalizes destination, resolves chown, copies sources, and exports a child image from the committed layer.

**State and persistence:** Mutates dispatch image ID after commit/export. Creates images/layers through backend. Copies run configs deeply enough for mutable slices/maps. Host config carries build resource/network/security options.

**Dependencies and integration:** Uses daemon builder interfaces, image/layer types, chroot archiver, network defaults, OCI platforms, and server backend commit configs.

**Risks:** Cache compatibility depends on exact NOP command format. Copy export depends on parent image type assertion and content-store digest. Shallow config copying would cause stage mutation bleed; tests protect this.

**Test signals:** `internals_test.go` covers Dockerfile context read errors, run-config copy depth, and export image. Platform tests cover chown and destination normalization.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/builder/dockerfile/internals.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/builder/dockerfile/internals_linux.go -->
## sources/cloud-native/moby/daemon/builder/dockerfile/internals_linux.go

**Purpose:** Implements Linux/Unix `--chown` parsing for ADD/COPY.

**Important APIs:** `parseChownFlag`, `lookupUser`, and `lookupGroup`. The parser accepts `user`, `user:group`, numeric IDs, and names looked up in container `/etc/passwd` and `/etc/group`, then maps IDs through user namespace identity mapping.

**Control flow:** `parseChownFlag` splits on colon, defaults group to user when omitted, resolves passwd/group paths with symlink scope inside container rootfs, resolves IDs/names, then converts to host UID/GID.

**State and persistence:** No persistent state; returns an `identity` used by copy code to chown files in the RW layer.

**Dependencies and integration:** Uses `moby/sys/user`, symlink scope checks, and user namespace mapping from builder.

**Risks:** Path resolution for `/etc/passwd` and `/etc/group` is security-sensitive. Missing user/group produces user-facing build errors. Namespace mapping errors must not be ignored.

**Test signals:** `internals_linux_test.go` covers chown parsing behavior and lookup combinations.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/builder/dockerfile/internals_linux.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/builder/dockerfile/internals_linux_test.go -->
## sources/cloud-native/moby/daemon/builder/dockerfile/internals_linux_test.go

**Purpose:** Tests Linux `--chown` parsing and identity lookup.

**Important APIs:** `TestChownFlagParsing` exercises `parseChownFlag`, numeric and named user/group values, defaults, and error cases.

**Control flow:** Test data creates passwd/group fixtures under a temp container root and validates returned UID/GID or errors.

**State and persistence:** Temporary filesystem fixtures only.

**Dependencies and integration:** Protects ADD/COPY ownership behavior on Unix with user namespace mapping.

**Risks:** Does not cover actual file chown during copy or symlink attack variants beyond scoped path resolution in code.

**Test signals:** Strong direct signal for the parser/lookup layer used by copy execution.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/builder/dockerfile/internals_linux_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/builder/dockerfile/internals_test.go -->
## sources/cloud-native/moby/daemon/builder/dockerfile/internals_test.go

**Purpose:** Tests core builder internals around Dockerfile reading, run-config copying, and image export.

**Important APIs:** Tests include empty Dockerfile, symlink Dockerfile, Dockerfile outside context, missing Dockerfile, `copyRunConfig`, deep-copy behavior, mock RW/RO layers, and `exportImage`.

**Control flow:** Filesystem fixtures validate remote context Dockerfile lookup/parse behavior. Config tests mutate copies to confirm original configs are not aliased. Export tests validate image/layer creation path with mocks.

**State and persistence:** Uses temporary dirs and mock layers/images; no real daemon state.

**Dependencies and integration:** Bridges remotecontext behavior and Dockerfile builder internals.

**Risks:** Mock export cannot fully validate content store behavior or actual layer release ordering.

**Test signals:** Good regression signal for path safety, Dockerfile parsing errors, and run-config copy depth.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/builder/dockerfile/internals_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/builder/dockerfile/internals_windows.go -->
## sources/cloud-native/moby/daemon/builder/dockerfile/internals_windows.go

**Purpose:** Implements Windows-specific `--chown` handling by mapping account names or SIDs to Windows SIDs for ADD/COPY.

**Important APIs:** Constants for `SeTakeOwnershipPrivilege`, `ContainerAdministrator`, and `ContainerUser` SIDs; `parseChownFlag`, `getAccountIdentity`, and `lookupNTAccount`.

**Control flow:** For Windows target platform, chown is interpreted as an account/SID. Direct SID strings are validated, built-in aliases/well-known groups use host lookup results, container-specific names are mapped to constants, and remaining names are resolved by running `containerutility.exe getaccountsid` inside a temporary container with a bind mount.

**State and persistence:** Returns an `identity` with SID for later ACL application. Creates/runs a temporary helper container for dynamic account lookup.

**Dependencies and integration:** Uses Windows syscalls, platform parsing, container manager, bind mounts, JSON stream errors, and copy permission code.

**Risks:** Helper-container lookup depends on `containerutility.exe` path and container runtime behavior. Host vs container account resolution must not confuse identities. Non-Windows platform option returns root UID/GID instead.

**Test signals:** Adjacent Windows tests cover destination normalization, not SID lookup. Integration tests are needed for built-in and container-local account chown.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/builder/dockerfile/internals_windows.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/builder/dockerfile/internals_windows_test.go -->
## sources/cloud-native/moby/daemon/builder/dockerfile/internals_windows_test.go

**Purpose:** Tests Windows COPY/ADD destination normalization.

**Important APIs:** `TestNormalizeDest` exercises `normalizeDest` from `copy_windows.go`.

**Control flow:** Table cases validate system-drive enforcement, relative path handling under WORKDIR, trailing separator preservation, and platform-consistency errors.

**State and persistence:** No persistent state.

**Dependencies and integration:** Protects ADD/COPY path behavior on Windows.

**Risks:** Does not cover ACL/SID chown behavior, denied source paths, or actual copy operations.

**Test signals:** Useful direct signal for one of the most compatibility-sensitive Windows copy helpers.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/builder/dockerfile/internals_windows_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/builder/dockerfile/metrics.go -->
## sources/cloud-native/moby/daemon/builder/dockerfile/metrics.go

**Purpose:** Defines and registers Prometheus-style metrics for classic builder invocations and failure reasons.

**Important APIs:** Package vars `buildsTriggered` and `buildsFailed`; constants for failure labels such as syntax, empty Dockerfile, unsupported command, target unreachable, unknown instruction, and canceled build; `init` registers a `builder` metrics namespace.

**Control flow:** Init creates counters, preinitializes labeled counters for all known reasons, and registers the namespace.

**State and persistence:** Metrics live in process memory and are exported through the daemon metrics registry.

**Dependencies and integration:** Used by `BuildManager.Build`, parser error handling, target errors, and cancellation paths.

**Risks:** Missing labels make dashboards sparse or inconsistent. Metrics registration in init affects package import behavior and tests.

**Test signals:** No direct tests in this subset; compile-time use and metrics endpoint integration are the main signals.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/builder/dockerfile/metrics.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/builder/dockerfile/mockbackend_test.go -->
## sources/cloud-native/moby/daemon/builder/dockerfile/mockbackend_test.go

**Purpose:** Provides mock implementations of builder backend, image cache, image, and layer interfaces for Dockerfile unit tests.

**Important APIs/types:** `MockBackend` implements attach, create, remove, commit, start, wait, workdir, copy, get image/layer, make cache, and create image methods. `mockImage`, `mockImageCache`, `mockLayer`, and `mockRWLayer` implement image/cache/layer contracts.

**Control flow:** Most methods return preconfigured fields or nil values. `mockImageCache.GetCache` returns a configured cache ID. Layers expose fixed roots/digests and commit behavior.

**State and persistence:** In-memory mock fields; no daemon state. It simulates image IDs and layer lifecycle for tests.

**Dependencies and integration:** Used by dispatcher, evaluator, imagecontext, and internals tests.

**Risks:** Mock permissiveness can hide backend contract mistakes. Methods that no-op should be used carefully when tests need lifecycle assertions.

**Test signals:** Enables isolated tests; its existence is not a behavioral test itself, but it defines what unit tests can observe.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/builder/dockerfile/mockbackend_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/builder/dockerfile/utils_test.go -->
## sources/cloud-native/moby/daemon/builder/dockerfile/utils_test.go

**Purpose:** Supplies small filesystem helper functions for Dockerfile tests.

**Important APIs:** `createTestTempFile` writes a test file with given contents and permissions; `createTestSymlink` creates a symlink in a test directory.

**Control flow:** Helpers call `t.Helper`, perform filesystem operations, and fail the test immediately on errors.

**State and persistence:** Creates temporary test files/symlinks in caller-provided directories.

**Dependencies and integration:** Used by internals and context-related tests.

**Risks:** Helpers assume caller handles temp dir cleanup. Symlink behavior is platform-sensitive.

**Test signals:** Support utility only; no direct production behavior.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/builder/dockerfile/utils_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/builder/remotecontext/archive.go -->
## sources/cloud-native/moby/daemon/builder/remotecontext/archive.go

**Purpose:** Converts a build-context tar stream into a `builder.Source` backed by a temporary extracted directory and deterministic tarsum hashes.

**Important APIs/types:** `archiveContext`, `Close`, `convertPathError`, `modifiableContext`, `FromArchive`, `Root`, `Remove`, `Hash`, and `normalize`.

**Control flow:** `FromArchive` creates a temp dir, decompresses the stream, wraps it in tarsum, untars into the temp root, stores file sums, and returns the context. `Hash` normalizes/scopes paths, resolves symlinks inside root, finds the relative tarsum entry, and falls back to path for legacy cases.

**State and persistence:** Temporary extracted context is removed by `Close`. `sums` keeps per-file archive hashes in memory and drives cache keys.

**Dependencies and integration:** Used by local archive, URL archive, and git contexts. Depends on chroot untar, compression, longpath temp dirs, symlink scope checks, and internal tarsum.

**Risks:** Path normalization and symlink scoping are security-critical. Hash fallback may preserve compatibility but can mask missing tarsum entries. Caller must close context to remove temp directories.

**Test signals:** Remotecontext/tarsum tests outside the listed file set cover hash/remove/close behavior; internals tests cover Dockerfile path safety.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/builder/remotecontext/archive.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/builder/remotecontext/detect.go -->
## sources/cloud-native/moby/daemon/builder/remotecontext/detect.go

**Purpose:** Detects and constructs the build context and Dockerfile parser result from local archive, Git URL, remote URL, or unsupported client-session source.

**Important APIs:** `ClientSessionRemote`, `Detect`, `newArchiveRemote`, `withDockerfileFromContext`, `newGitRemote`, `newURLRemote`, `removeDockerfile`, `readAndParseDockerfile`, `openAt`, `StatAt`, and `FullPath`.

**Control flow:** `Detect` switches on `RemoteContext`. Archive/git/archive-URL paths create a modifiable context, open/parse Dockerfile, and remove Dockerfile/.dockerignore if ignored. Plain-text URL content is parsed as Dockerfile without a build context. Missing default `Dockerfile` falls back to lowercase.

**State and persistence:** May mutate the extracted build context by removing `.dockerignore` and Dockerfile entries before build. Temporary context lifecycle belongs to returned source.

**Dependencies and integration:** Uses BuildKit parser, URL utilities, Git remote context, ignorefile/patternmatcher, symlink scope, and buildbackend config/progress reader.

**Risks:** Dockerfile path handling must prevent escape from context. Removal semantics depend on .dockerignore matching. Client session is explicitly rejected for v1 builder. Plain text remote Dockerfiles have no build context, so COPY should fail.

**Test signals:** `detect_test.go` covers removeDockerfile behavior. Internals tests cover missing/empty/symlink/outside Dockerfile handling.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/builder/remotecontext/detect.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/builder/remotecontext/detect_test.go -->
## sources/cloud-native/moby/daemon/builder/remotecontext/detect_test.go

**Purpose:** Tests `.dockerignore`-driven removal of Dockerfile and `.dockerignore` from modifiable build contexts.

**Important APIs:** Helpers inspect directories and invoke `removeDockerfile` using a `stubRemote` implementing source/remove methods.

**Control flow:** Tests create context directories, write ignore files, execute removal, and compare remaining filenames.

**State and persistence:** Temporary filesystem state only.

**Dependencies and integration:** Protects `withDockerfileFromContext` cleanup behavior used after parsing Dockerfile.

**Risks:** Does not cover remote URL/Git detection, Dockerfile parsing errors, or symlink-scoped `FullPath`.

**Test signals:** Direct signal for whether ignored Dockerfile/.dockerignore files are removed from the context before build instructions can copy them.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/builder/remotecontext/detect_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/builder/remotecontext/filehash.go -->
## sources/cloud-native/moby/daemon/builder/remotecontext/filehash.go

**Purpose:** Builds deterministic per-file hashes for lazy build contexts using tar header metadata plus file content writes.

**Important APIs/types:** `NewFileHash` creates a hash initialized with a tarsum V1 header. `tarsumHash` embeds `hash.Hash` and overrides `Reset` to reapply the header.

**Control flow:** For symlinks, readlink target is included in the archive header. `archive.FileInfoHeader` and security xattrs populate tar metadata, then `tarsum.WriteV1Header` seeds the SHA-256 hash.

**State and persistence:** No persistence. Returned hash object accumulates data written by callers and can reset to the header-initialized state.

**Dependencies and integration:** Used by remote context lazy sources to produce cache keys compatible with tar archive contexts.

**Risks:** Header selection must stay compatible with tarsum V1. Security xattr read failures propagate and can break hashing.

**Test signals:** Tarsum and remotecontext hash tests outside this file exercise hash behavior. Direct tests for xattrs/symlinks would be valuable.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/builder/remotecontext/filehash.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/builder/remotecontext/git.go -->
## sources/cloud-native/moby/daemon/builder/remotecontext/git.go

**Purpose:** Builds a `builder.Source` from a Git URL by cloning to a temp directory, tarring it, and feeding it through archive context creation.

**Important APIs:** `MakeGitContext(gitURL)` calls `git.Clone` with isolated config, archives the clone root with no compression, defers tar close and clone deletion, and returns `FromArchive(c)`.

**Control flow:** Clone first, tar second, defer cleanup/logging, then create an archive-backed source whose own temp dir survives until source close.

**State and persistence:** Temporary Git clone is removed before return completes. The returned source has its own extracted temporary directory and tarsum state.

**Dependencies and integration:** Connects remotecontext detection with `remotecontext/git` utility and archive/tarsum source handling.

**Risks:** Two-stage temp handling must avoid deleting data before `FromArchive` finishes. Clone cleanup errors are logged only. Isolated Git config reduces host config influence.

**Test signals:** `git/gitutils_test.go` covers clone parsing/checkout behavior; archive context tests cover returned source semantics.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/builder/remotecontext/git.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/builder/remotecontext/git/gitutils.go -->
## sources/cloud-native/moby/daemon/builder/remotecontext/git/gitutils.go

**Purpose:** Implements Git URL parsing, secure clone/fetch/checkout, shallow-clone detection, submodule update, and subdirectory selection for remote build contexts.

**Important APIs/types:** `gitRepo`, `CloneOption`, `WithIsolatedConfig`, `Clone`, `clone`, `parseRemoteURL`, `getRefAndSubdir`, `fetchArgs`, `supportsShallowClone`, `checkout`, `gitWithinDir`, `isGitTransport`, and `getScheme`.

**Control flow:** `Clone` parses URL/fragments, applies options, initializes a temp repo, adds origin, fetches selected ref with optional depth, checks out branch or `FETCH_HEAD`, updates submodules, and returns either root or scoped subdirectory. HTTP shallow support is probed via smart-HTTP service discovery.

**State and persistence:** Creates a temporary `docker-build-git` directory and deletes it on error. Successful clone root is later archived and removed by caller.

**Dependencies and integration:** Uses external `git`, HTTP probing, URL parsing, symlink scope for subdir, and environment controls `GIT_PROTOCOL_FROM_USER=0`, `GIT_CONFIG_NOSYSTEM=1`, `HOME=/dev/null`.

**Risks:** Remote URL/ref handling is command-injection-sensitive; refs starting with `-` are rejected and fetch uses `--`. File protocol is disabled for submodules. HTTP probing performs network requests. Subdir symlinks must stay within repo root.

**Test signals:** `gitutils_test.go` covers URL parsing, shallow args, checkout/subdir/submodule behavior, transport detection, and invalid refspecs.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/builder/remotecontext/git/gitutils.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/builder/remotecontext/git/gitutils_test.go -->
## sources/cloud-native/moby/daemon/builder/remotecontext/git/gitutils_test.go

**Purpose:** Tests Git remote context parsing, fetch arguments, checkout behavior, submodule handling, transport detection, and ref validation.

**Important APIs:** `TestParseRemoteURL`, shallow clone argument tests, `TestCheckoutGit`, `TestValidGitTransport`, and `TestGitInvalidRef`.

**Control flow:** Tests use HTTP test servers and `git http-backend` to create smart/dumb Git scenarios, initialize repos/submodules, exercise refs and subdirs, and assert checked-out Dockerfile contents or failures.

**State and persistence:** Creates temporary Git repositories, commits, branches, submodules, and server state under test temp dirs.

**Dependencies and integration:** Requires a working `git` binary. It validates security controls around refspec parsing and path scoping.

**Risks:** Some symlink cases are skipped on Windows. Network behavior is local test-server based and may not cover all real Git hosting quirks.

**Test signals:** Strong integration-level signal for the Git context utility, including submodule and smart HTTP behavior.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/builder/remotecontext/git/gitutils_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/builder/remotecontext/internal/tarsum/builder_context.go -->
## sources/cloud-native/moby/daemon/builder/remotecontext/internal/tarsum/builder_context.go

**Purpose:** Extends `TarSum` with removal semantics needed for `.dockerignore` processing during builder context setup.

**Important APIs:** `BuilderContext` interface embeds `TarSum` and adds `Remove(string)`. `(*tarSum).Remove` deletes all sums matching a filename.

**Control flow:** `Remove` iterates the `sums` slice and splices out every entry with the requested name, continuing because duplicate path entries can exist.

**State and persistence:** Mutates in-memory tarsum file list only; it does not edit tar bytes or filesystem contents.

**Dependencies and integration:** Used conceptually by builder context filtering; archive-backed context has a separate `Remove` implementation that deletes files from extracted root.

**Risks:** Removing while ranging over a slice can skip adjacent duplicate entries after splice; tests should guard duplicate behavior. Matching is exact and not Windows case-insensitive here.

**Test signals:** `builder_context_test.go` covers nonexistent removal and removing duplicate entries.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/builder/remotecontext/internal/tarsum/builder_context.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/builder/remotecontext/internal/tarsum/builder_context_test.go -->
## sources/cloud-native/moby/daemon/builder/remotecontext/internal/tarsum/builder_context_test.go

**Purpose:** Tests `tarSum.Remove` behavior.

**Important APIs:** `TestTarSumRemoveNonExistent` and `TestTarSumRemove` operate on `tarSum.sums`.

**Control flow:** Tests create in-memory `FileInfoSums`, remove names, and compare expected remaining entries.

**State and persistence:** In-memory only.

**Dependencies and integration:** Protects .dockerignore-oriented tarsum filtering semantics.

**Risks:** Coverage should ensure duplicate removal does not skip adjacent entries; this is important because tar archives can contain duplicate paths.

**Test signals:** Direct signal for the only behavior in `builder_context.go`.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/builder/remotecontext/internal/tarsum/builder_context_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/builder/remotecontext/internal/tarsum/fileinfosums.go -->
## sources/cloud-native/moby/daemon/builder/remotecontext/internal/tarsum/fileinfosums.go

**Purpose:** Defines sortable/accessor structures for per-file tar checksum metadata.

**Important APIs/types:** `FileInfoSumInterface`, `fileInfoSum`, `FileInfoSums`, `GetFile`, `GetAllFile`, `GetDuplicatePaths`, `Len`, `Swap`, `SortByPos`, `SortByNames`, `SortBySums`, and sort adapters `byName`, `bySum`, `byPos`.

**Control flow:** Lookup is case-insensitive on Windows for `GetFile`. Sorting by name uses original tar position to break ties. Sorting by sums uses position only for duplicate paths to preserve deterministic duplicate handling.

**State and persistence:** In-memory slice of file checksum records generated while reading tar streams.

**Dependencies and integration:** Used by `tarSum.Sum`, archive context `Hash`, and tests. Runtime GOOS affects matching behavior.

**Risks:** Sorting mutates the slice in place; callers must understand ordering changes. Windows case-insensitive lookup can return a different casing's first match.

**Test signals:** `fileinfosums_test.go` covers sorting behavior.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/builder/remotecontext/internal/tarsum/fileinfosums.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/builder/remotecontext/internal/tarsum/fileinfosums_test.go -->
## sources/cloud-native/moby/daemon/builder/remotecontext/internal/tarsum/fileinfosums_test.go

**Purpose:** Tests sorting behavior for `FileInfoSums`.

**Important APIs:** `newFileInfoSums` helper and `TestSortFileInfoSums` exercise `SortByNames`, `SortBySums`, and `SortByPos`.

**Control flow:** Creates deterministic in-memory sums and validates order after each sort.

**State and persistence:** In-memory only.

**Dependencies and integration:** Protects deterministic tarsum order used for aggregate checksums.

**Risks:** Does not cover Windows case-insensitive `GetFile` or duplicate-path edge cases in depth.

**Test signals:** Good signal for ordering primitives that affect cache checksum stability.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/builder/remotecontext/internal/tarsum/fileinfosums_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/builder/remotecontext/internal/tarsum/tarsum.go -->
## sources/cloud-native/moby/daemon/builder/remotecontext/internal/tarsum/tarsum.go

**Purpose:** Implements deterministic tar stream checksumming and optional recompressed/identity tar streaming for builder cache keys and archive context hashes.

**Important APIs/types:** `NewTarSum`, `NewTarSumHash`, `NewTarSumForLabel`, `TarSum`, `tarSum`, `THash`, `NewTHash`, `DefaultTHash`, `encodeHeader`, `initTarSum`, `Read`, `Sum`, and `GetSums`.

**Control flow:** `Read` lazily streams tar data: it reads current file data, hashes selected header fields and content, writes through a tar writer, flushes through gzip or nop writer, advances headers on EOF, records per-file sums, and marks finished at archive EOF. `Sum` sorts file sums by checksum and hashes all sums plus optional extra bytes with a version/hash label prefix.

**State and persistence:** Maintains reader/writer buffers, current hash, file counter, current file name, per-file sums, compression setting, version, and hash provider. No durable state.

**Dependencies and integration:** Used by `remotecontext.FromArchive` and file hash compatibility. Depends on archive/tar, gzip, crypto hash providers, and version-specific header selectors.

**Risks:** Streaming state machine is subtle; EOF handling, writer flushing, compression mode, duplicate paths, and header selection all affect cache compatibility. Only SHA-256/SHA-512 labels are accepted for standard hashes.

**Test signals:** Tarsum tests outside the listed subset cover labels, empty tars, read sizes, iteration, checksums, and benchmarks. Listed `fileinfosums` and builder-context tests cover supporting behavior.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/builder/remotecontext/internal/tarsum/tarsum.go -->
