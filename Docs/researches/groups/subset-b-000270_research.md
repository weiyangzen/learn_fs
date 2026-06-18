# subset-b-000270 Research

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/soci-snapshotter/benchmark/parser/main.go -->
## sources/cloud-native/soci-snapshotter/benchmark/parser/main.go

Purpose: command-line helper that scans a benchmark log and groups JSON benchmark events by test UUID and benchmark event name.

Important APIs/types/functions: `BenchmarkEvent` maps expected JSON fields, `ProfileEvent` stores start/stop timestamps, `BenchmarkProfile` groups events for one test, `parseLogLineToMap` updates the map, and `printLogMap` dumps the collected profile.

Control flow: `main` opens `os.Args[1]`, scans line by line, filters lines containing `benchmark`, unmarshals JSON, records `Start` and `Stop` times using RFC3339 parsing, then prints the map.

State and persistence: all parsed state is in memory; output is printed to stdout. It reads one log file but does not write files.

Dependencies and integration: depends only on standard library packages and the benchmark framework's JSON log shape.

Risks and test signals: argument count, JSON unmarshal errors, and time parse errors are ignored, so malformed input can silently produce zero timestamps. There are no tests in this subset for this parser.
<!-- END_FILE_RESEARCH: sources/cloud-native/soci-snapshotter/benchmark/parser/main.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/soci-snapshotter/benchmark/performanceTest/main.go -->
## sources/cloud-native/soci-snapshotter/benchmark/performanceTest/main.go

Purpose: benchmark driver that runs full SOCI benchmark workloads, optionally parsing file-access logs after each run.

Important APIs/types/functions: top-level flags configure test count, workload JSON, commit tagging, and file-access parsing. It constructs `framework.BenchmarkTestDriver` values whose `TestFunction` calls `benchmark.SociFullRun`.

Control flow: parse flags, choose commit hash, optionally recreate `output/file_access_logs`, load default or JSON image descriptors, create `output/benchmark_log`, create a framework context, build one driver per image, and invoke `BenchmarkFramework.Run`.

State and persistence: writes benchmark output under `../performanceTest/output`, truncates `benchmark_log`, and may delete/recreate file access logs.

Dependencies and integration: integrates with `benchmark` package workload descriptors, SOCI run helpers, `benchmark/framework`, Go `testing.B`, and `benchmark/framework/parser`.

Risks and test signals: closures capture `testName` and `image` from loop variables; with current Go semantics this is safe, but older compiler assumptions would be risky. It panics on most setup failures and has no direct tests here.
<!-- END_FILE_RESEARCH: sources/cloud-native/soci-snapshotter/benchmark/performanceTest/main.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/soci-snapshotter/benchmark/soci_config.toml -->
## sources/cloud-native/soci-snapshotter/benchmark/soci_config.toml

Purpose: minimal benchmark configuration enabling the CRI keychain for SOCI snapshotter benchmark runs.

Important settings: `[cri_keychain] enable_keychain = true` enables lookup through a CRI image service, and `image_service_path = "/tmp/containerd-grpc/containerd.sock"` points at the benchmark containerd socket.

Control flow: not executable itself; consumed by `soci-snapshotter-grpc` through the config loader when benchmark helpers launch the SOCI process.

State and persistence: no persistence; its values affect runtime credential resolution and socket dialing.

Dependencies and integration: matches `config.CRIKeychainConfig` TOML fields and integrates with the daemon's CRI keychain registration.

Risks and test signals: path is benchmark-environment-specific and will fail if the benchmark containerd socket is elsewhere. No standalone tests cover this file.
<!-- END_FILE_RESEARCH: sources/cloud-native/soci-snapshotter/benchmark/soci_config.toml -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/soci-snapshotter/benchmark/soci_utils.go -->
## sources/cloud-native/soci-snapshotter/benchmark/soci_utils.go

Purpose: benchmark utilities for launching/stopping a SOCI snapshotter process and creating containerd containers through the SOCI snapshotter.

Important APIs/types/functions: `SociProcess` tracks the launched command, socket address, root, stdout, and stderr files. `StartSoci` starts the binary and waits for the Unix socket. `StopProcess` kills it and unmounts/removes snapshot roots. `SociRPullImageFromRegistry` pulls using snapshotter `soci` and appends SOCI labels. `CreateSociContainer` creates containers with the SOCI snapshotter.

Control flow: `StartSoci` builds an exec command, creates output log files, starts the process, polls for socket creation up to about 15 seconds, and returns process metadata.

State and persistence: writes stdout/stderr logs, creates snapshotter root state, removes socket/root on stop, and force-unmounts snapshot mountpoints.

Dependencies and integration: containerd client APIs, snapshotter labels from `fs/source`, and benchmark framework resolver/container helpers.

Risks and test signals: process kill errors are ignored, polling uses fixed sleeps, and failed socket startup can leak open files/processes. No direct tests here.
<!-- END_FILE_RESEARCH: sources/cloud-native/soci-snapshotter/benchmark/soci_utils.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/soci-snapshotter/benchmark/stargzTest/main.go -->
## sources/cloud-native/soci-snapshotter/benchmark/stargzTest/main.go

Purpose: benchmark driver for full stargz snapshotter runs against image descriptors from JSON.

Important APIs/types/functions: positional arguments supply commit, workload JSON, count, and stargz binary. For each image, a `framework.BenchmarkTestDriver` calls `benchmark.StargzFullRun`.

Control flow: parse positional arguments, load image descriptors, create `./output/benchmark_log`, create framework context, build drivers, and run the benchmark framework.

State and persistence: writes under local `./output`, truncating `benchmark_log` on each run.

Dependencies and integration: depends on the shared benchmark package, benchmark framework, and `StargzFullRun` implementation outside this source set.

Risks and test signals: direct `os.Args` indexing can panic on missing arguments. Invalid count and workload failures panic. No direct tests in this subset.
<!-- END_FILE_RESEARCH: sources/cloud-native/soci-snapshotter/benchmark/stargzTest/main.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/soci-snapshotter/benchmark/stargz_config.toml -->
## sources/cloud-native/soci-snapshotter/benchmark/stargz_config.toml

Purpose: placeholder stargz benchmark configuration file.

Important APIs/types/functions: none; the file is empty.

Control flow: not executable. If passed to a stargz process, behavior depends entirely on the external stargz snapshotter's defaults for an empty config.

State and persistence: no state and no persisted settings.

Dependencies and integration: benchmark launch helpers pass a config path to the stargz binary; this file can satisfy that argument while leaving defaults active.

Risks and test signals: empty config may be accepted or rejected depending on the external stargz snapshotter version. No tests cover the file.
<!-- END_FILE_RESEARCH: sources/cloud-native/soci-snapshotter/benchmark/stargz_config.toml -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/soci-snapshotter/benchmark/stargz_utils.go -->
## sources/cloud-native/soci-snapshotter/benchmark/stargz_utils.go

Purpose: benchmark utilities for launching/stopping stargz snapshotter and pulling images through it.

Important APIs/types/functions: `StargzProcess` stores command/socket/root/log file handles. `StartStargz` starts the binary and waits for socket creation. `StopProcess` kills the command, removes socket/root, and unmounts snapshots. `StargzRpullImageFromRegistry` pulls with `WithPullSnapshotter("stargz")`.

Control flow: mirrors SOCI process startup: create output dir and logs, start command, poll socket for up to 15 seconds, then return process metadata.

State and persistence: writes snapshotter stdout/stderr files and manages the stargz root directory and Unix socket.

Dependencies and integration: containerd client, snapshotter pull options, benchmark framework resolver, and OS mount cleanup.

Risks and test signals: fixed startup wait, ignored kill/unmount errors, and possible leaks on partial startup failure. No direct tests here.
<!-- END_FILE_RESEARCH: sources/cloud-native/soci-snapshotter/benchmark/stargz_utils.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/soci-snapshotter/benchmark/utils.go -->
## sources/cloud-native/soci-snapshotter/benchmark/utils.go

Purpose: shared benchmark image descriptor model, container creation options, workload loading, and default workload list.

Important APIs/types/functions: `ImageDescriptor`, `ImageOptions`, `Timeout`, `ContainerOpts`, `GetImageList`, `GetImageListFromJSON`, `GetCommitHash`, and `GetDefaultWorkloads`.

Control flow: descriptor JSON is decoded into workload structs; `ContainerOpts` converts image options into containerd `NewContainerOpts` plus OCI spec options for mounts, GPU, env, shm, and host networking.

State and persistence: reads JSON workload files and invokes `git rev-parse HEAD`; otherwise no durable state.

Dependencies and integration: containerd client and OCI helpers, NVIDIA runtime spec helpers, default public ECR workload images, and benchmark drivers.

Risks and test signals: `ContainerOpts` panics if hostname lookup fails for host network mode. Default workload digests can drift if upstream images change. No direct tests here in this subset.
<!-- END_FILE_RESEARCH: sources/cloud-native/soci-snapshotter/benchmark/utils.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/soci-snapshotter/cache/cache.go -->
## sources/cloud-native/soci-snapshotter/cache/cache.go

Purpose: generic blob cache implementations backed by a directory or memory, used for cached byte blobs with `ReaderAt` access.

Important APIs/types/functions: `BlobCache`, `Reader`, `Writer`, `DirectoryCacheConfig`, `NewDirectoryCache`, `NewMemoryCache`, `Direct`, `directoryCache.Get/Add/Close`, and `MemoryCache.Get/Add`.

Control flow: directory cache validates absolute path, creates root and `wip`, initializes LRU buffers and file descriptor caches, writes via temp files, and commits by rename. Reads prefer memory, then open-file cache, then disk. Memory cache stores committed buffers in a mutex-protected map.

State and persistence: directory cache persists blobs under the cache directory until `Close`, with temp work in `wip`; memory cache is process-local only. Async `Add` commits to disk unless `SyncAdd` is true.

Dependencies and integration: uses local `lrucache` and `namedmutex` utilities, OS filesystem primitives, and standard `io.ReaderAt` contracts.

Risks and test signals: async commit can report success before disk write failure; duplicate keys keep the first memory entry but still write through cached bytes. `wipLock` is allocated but unused. Tests cover hit/miss and eviction-size scenarios.
<!-- END_FILE_RESEARCH: sources/cloud-native/soci-snapshotter/cache/cache.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/soci-snapshotter/cache/cache_test.go -->
## sources/cloud-native/soci-snapshotter/cache/cache_test.go

Purpose: validates common `BlobCache` behavior across directory and memory implementations.

Important APIs/types/functions: `TestDirectoryCache`, `TestMemoryCache`, `testCache`, `hit`, `miss`, `testBlob`, and `digestFor`.

Control flow: tests create caches, add empty/data/multiple/duplicate blobs, commit writers, then verify full-blob and chunk `ReadAt` reads plus expected cache misses.

State and persistence: directory tests use `t.TempDir` with `SyncAdd: true` to make disk writes deterministic; memory tests use in-process buffers.

Dependencies and integration: exercises `NewDirectoryCache`, `NewMemoryCache`, writer commit, reader close, and SHA-256 digest keying.

Risks and test signals: tests do not cover async directory commits, `Direct`, `Close`, failed writes, invalid relative cache paths, concurrent writers/readers, or file descriptor cache behavior.
<!-- END_FILE_RESEARCH: sources/cloud-native/soci-snapshotter/cache/cache_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/soci-snapshotter/cmd/soci-snapshotter-grpc/config.go -->
## sources/cloud-native/soci-snapshotter/cmd/soci-snapshotter-grpc/config.go

Purpose: adds `config` subcommands to the snapshotter daemon binary for inspecting effective and default configuration.

Important APIs/types/functions: `ConfigCommand`, with `dump` and `default` child commands.

Control flow: `dump` loads TOML through `config.NewConfigFromToml(cmd.String("config"))` and emits the parsed config as TOML. `default` calls `config.NewConfig()` and emits defaults.

State and persistence: reads config files but writes only to stdout; no state mutation.

Dependencies and integration: uses `pelletier/go-toml/v2`, `urfave/cli/v3`, containerd logging, and the config package.

Risks and test signals: on load error it calls `log.Fatal`, which exits rather than returning a normal CLI error. Main tests exercise env var override for config dump.
<!-- END_FILE_RESEARCH: sources/cloud-native/soci-snapshotter/cmd/soci-snapshotter-grpc/config.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/soci-snapshotter/cmd/soci-snapshotter-grpc/main.go -->
## sources/cloud-native/soci-snapshotter/cmd/soci-snapshotter-grpc/main.go

Purpose: main daemon for the SOCI snapshotter gRPC service.

Important APIs/types/functions: `buildApp`, `serve`, `getMetadataStore`, `getCriConn`, `listen`, `listenUnix`, and `listenFd`.

Control flow: CLI/env flags set socket, config, log level, and root. The action configures logging, loads config, checks snapshotter support, registers namespace interceptors, builds credential keychains, opens metadata DB, creates `service.NewSociSnapshotterService`, registers containerd snapshots gRPC, starts optional metrics/debug endpoints, listens on Unix or systemd fd, handles signals, and conditionally closes snapshotter on SIGINT.

State and persistence: creates root directories, socket files, optional metrics socket, and Bolt metadata DB at `root/metadata.db`.

Dependencies and integration: containerd snapshotservice API, gRPC, systemd activation/notify, Docker/kube/CRI keychains, resolver, metadata, service, fs, and config packages.

Risks and test signals: fatal logging inside command action complicates library-style testing; metrics/debug goroutines report through one error channel and can stop serve. Tests cover env overrides for config path and log level, not full daemon serving.
<!-- END_FILE_RESEARCH: sources/cloud-native/soci-snapshotter/cmd/soci-snapshotter-grpc/main.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/soci-snapshotter/cmd/soci-snapshotter-grpc/main_test.go -->
## sources/cloud-native/soci-snapshotter/cmd/soci-snapshotter-grpc/main_test.go

Purpose: tests environment variable overrides for the daemon CLI.

Important APIs/types/functions: `TestEnvVarOverridesDefaultConfigPath`, `TestEnvVarOverridesDefaultLogLevel`, and `writeTestConfig`.

Control flow: first test writes a custom TOML, sets `SOCI_SNAPSHOTTER_CONFIG`, redirects stdout to a temp file, runs `config dump`, and reloads output to assert CRI path. Second test sets config/log/root/address env vars, starts app in a goroutine, waits briefly, and checks logrus level.

State and persistence: uses temp dirs/files and environment variables via `t.Setenv`.

Dependencies and integration: exercises `buildApp`, config loader/dumper, log-level flag source, and daemon startup enough to mutate global logrus level.

Risks and test signals: second test launches `app.Run` without synchronizing shutdown result, so failures can be hidden. It does not assert socket serving or cleanup.
<!-- END_FILE_RESEARCH: sources/cloud-native/soci-snapshotter/cmd/soci-snapshotter-grpc/main_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/soci-snapshotter/cmd/soci-snapshotter-grpc/namespaces.go -->
## sources/cloud-native/soci-snapshotter/cmd/soci-snapshotter-grpc/namespaces.go

Purpose: gRPC interceptors that preserve containerd namespace metadata on outgoing contexts.

Important APIs/types/functions: `unaryNamespaceInterceptor`, `streamNamespaceInterceptor`, and `wrappedSSWithContext`.

Control flow: for unary and stream RPCs, read incoming namespace using `namespaces.Namespace(ctx)`. If present, wrap the context with `namespaces.WithNamespace`; stream calls wrap `grpc.ServerStream` so `Context()` returns the updated context.

State and persistence: no durable state; modifies request context only.

Dependencies and integration: copied from containerd server namespace handling and used by the daemon's gRPC server options.

Risks and test signals: no direct tests in this subset; correctness depends on containerd namespace metadata format and interceptor ordering.
<!-- END_FILE_RESEARCH: sources/cloud-native/soci-snapshotter/cmd/soci-snapshotter-grpc/namespaces.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/soci-snapshotter/cmd/soci/commands/convert.go -->
## sources/cloud-native/soci-snapshotter/cmd/soci/commands/convert.go

Purpose: implements `soci convert`, creating SOCI-enabled OCI images either in containerd or standalone OCI-layout mode.

Important APIs/types/functions: `ConvertCommand`, `verifyRef`, `runStandaloneConvert`, and `parseBuilderOptions`.

Control flow: validate source/destination, branch to standalone when requested, otherwise connect to containerd, load source image, open selected SOCI/content store and artifacts DB, build index builder options, resolve platforms, call `builder.Convert`, then create or update the destination image with the converted descriptor.

State and persistence: mutates containerd image metadata/content store and SOCI artifacts DB. Standalone mode creates temp OCI/artifact dirs, loads tar/dir input, converts into ORAS-backed layout, and writes tar or directory output.

Dependencies and integration: containerd image/content services, SOCI builder/store/DB, platform and prefetch helpers, OCI archive utilities.

Risks and test signals: destination validation rejects digest refs. Standalone temp directory behavior depends on `/tmp` availability. No direct tests in this subset.
<!-- END_FILE_RESEARCH: sources/cloud-native/soci-snapshotter/cmd/soci/commands/convert.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/soci-snapshotter/cmd/soci/commands/create.go -->
## sources/cloud-native/soci-snapshotter/cmd/soci/commands/create.go

Purpose: implements `soci create`, generating SOCI indexes and zTOCs for an existing containerd image.

Important APIs/types/functions: `CreateCommand`, `createZtocFlags`, and constants for span size, min layer size, optimizations, force, and GC label.

Control flow: validate image ref, parse optimizations and prefetch paths, connect to containerd, get image, open configured content store, resolve platforms, open artifacts DB, build `soci.IndexBuilder`, then for each platform open a batch, build the index, and label the source image with the SOCI index digest.

State and persistence: writes SOCI layer/index artifacts to selected store, updates artifacts DB, and mutates containerd image labels for GC rooting.

Dependencies and integration: containerd client/image service, SOCI builder/store/DB, global root flag, platform helpers.

Risks and test signals: `defer done(ctx)` inside the platform loop delays all batch cleanup until command return. `is.Update` errors are ignored. No direct tests here.
<!-- END_FILE_RESEARCH: sources/cloud-native/soci-snapshotter/cmd/soci/commands/create.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/soci-snapshotter/cmd/soci/commands/global/global.go -->
## sources/cloud-native/soci-snapshotter/cmd/soci/commands/global/global.go

Purpose: defines shared CLI flags for the `soci` command.

Important APIs/types/functions: constants for `address`, `namespace`, `timeout`, `debug`, `content-store`, and `root`, plus `Flags`.

Control flow: no runtime logic beyond flag declarations. Defaults use containerd default address, containerd default namespace, default content store type, and snapshotter root path.

State and persistence: flag values drive later command context, client connections, content-store selection, and root DB/store paths.

Dependencies and integration: config defaults, containerd defaults/namespaces, and urfave cli flag sources from env vars.

Risks and test signals: content-store accepts arbitrary strings at flag level; validation happens later in store creation. No direct tests for global flags.
<!-- END_FILE_RESEARCH: sources/cloud-native/soci-snapshotter/cmd/soci/commands/global/global.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/soci-snapshotter/cmd/soci/commands/index/index.go -->
## sources/cloud-native/soci-snapshotter/cmd/soci/commands/index/index.go

Purpose: command group definition for `soci index`.

Important APIs/types/functions: `Command` with `listCommand`, `infoCommand`, and `rmCommand`.

Control flow: urfave cli dispatches subcommands; this file performs no data operations itself.

State and persistence: none directly, but subcommands inspect and mutate artifacts DB/content stores.

Dependencies and integration: depends on urfave cli and sibling command implementations.

Risks and test signals: no direct tests; correctness is command registration coverage.
<!-- END_FILE_RESEARCH: sources/cloud-native/soci-snapshotter/cmd/soci/commands/index/index.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/soci-snapshotter/cmd/soci/commands/index/info.go -->
## sources/cloud-native/soci-snapshotter/cmd/soci/commands/index/info.go

Purpose: implements `soci index info`, printing the raw JSON of a SOCI index artifact.

Important APIs/types/functions: `infoCommand` and `prettyPrintJSON`.

Control flow: parse digest argument, open artifacts DB, verify digest is not a zTOC layer entry, open selected content store, fetch descriptor by digest, read all bytes, and JSON-indent them to stdout.

State and persistence: read-only against DB and content store.

Dependencies and integration: artifacts DB identifies artifact type; selected store fetches bytes; JSON formatting is standard library.

Risks and test signals: missing or malformed digest errors surface directly; large indexes are fully buffered. No direct tests here.
<!-- END_FILE_RESEARCH: sources/cloud-native/soci-snapshotter/cmd/soci/commands/index/info.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/soci-snapshotter/cmd/soci/commands/index/list.go -->
## sources/cloud-native/soci-snapshotter/cmd/soci/commands/index/list.go

Purpose: implements `soci index list`, listing SOCI index artifacts with optional image ref/platform filters.

Important APIs/types/functions: filters `indexFilter`, `platformFilter`, `originalDigestFilter`, `anyMatch`, `listCommand`, `writeArtifactEntry`, and `getDuration`.

Control flow: parse flags, connect to containerd, build a filter based on ref and platforms, walk artifacts DB, sort by creation time descending, then print quiet digest list or tabular metadata. Ref filtering resolves image manifests for relevant platforms.

State and persistence: read-only on containerd image/content service and artifacts DB.

Dependencies and integration: containerd image platform resolution, SOCI image manifest descriptor helpers, artifacts DB, tabwriter.

Risks and test signals: image service is opened even for DB-only platform filtering. Image refs with missing platform manifests return explicit errors. No direct tests here.
<!-- END_FILE_RESEARCH: sources/cloud-native/soci-snapshotter/cmd/soci/commands/index/list.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/soci-snapshotter/cmd/soci/commands/index/rm.go -->
## sources/cloud-native/soci-snapshotter/cmd/soci/commands/index/rm.go

Purpose: implements `soci index remove/rm`, deleting index metadata and content by digest or by image ref.

Important APIs/types/functions: `rmCommand` and `removeArtifactsAndContent`.

Control flow: reject simultaneous digest args and `--ref`, open configured content store and artifacts DB, then either remove explicit digest args or look up entries associated with the image target digest and remove each artifact plus content blob.

State and persistence: mutates artifacts DB and selected content store; may connect to containerd to resolve image refs.

Dependencies and integration: SOCI artifacts DB, SOCI store abstraction, containerd image service, digest parsing.

Risks and test signals: `RemoveArtifactEntryByIndexDigest` runs before digest parsing/content deletion, so later failures may leave partial state. No direct tests here.
<!-- END_FILE_RESEARCH: sources/cloud-native/soci-snapshotter/cmd/soci/commands/index/rm.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/soci-snapshotter/cmd/soci/commands/internal/client.go -->
## sources/cloud-native/soci-snapshotter/cmd/soci/commands/internal/client.go

Purpose: centralizes containerd client creation and command context setup.

Important APIs/types/functions: `AppContext` and `NewClient`.

Control flow: `AppContext` applies namespace, optional timeout, and `SOURCE_DATE_EPOCH`. `NewClient` appends containerd timeout option, trims `unix://` socket prefix, creates a containerd client, and returns the prepared context plus cancel function.

State and persistence: no durable state; creates network/socket client connections and context metadata.

Dependencies and integration: global flags, config socket trimming, containerd client, namespaces, epoch, and logging.

Risks and test signals: callers must close the returned cancel function but this function does not close the containerd client. No direct tests here.
<!-- END_FILE_RESEARCH: sources/cloud-native/soci-snapshotter/cmd/soci/commands/internal/client.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/soci-snapshotter/cmd/soci/commands/internal/index.go -->
## sources/cloud-native/soci-snapshotter/cmd/soci/commands/internal/index.go

Purpose: shared existing-index push policy flags and helper.

Important APIs/types/functions: `ExistingIndexFlag`, policy constants `warn`, `skip`, `allow`, `SupportedExistingIndexOptions`, `ExistingIndexFlags`, and generic `SupportedArg`.

Control flow: no command execution; push command validates and switches behavior based on the chosen policy.

State and persistence: none directly.

Dependencies and integration: used by `soci push` to handle remote referrer conflicts before uploading.

Risks and test signals: validation is opt-in by callers; unsupported values are not rejected by flag parsing itself. No direct tests here.
<!-- END_FILE_RESEARCH: sources/cloud-native/soci-snapshotter/cmd/soci/commands/internal/index.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/soci-snapshotter/cmd/soci/commands/internal/platform.go -->
## sources/cloud-native/soci-snapshotter/cmd/soci/commands/internal/platform.go

Purpose: shared platform flag parsing for CLI commands.

Important APIs/types/functions: `PlatformFlags`, `GetPlatforms`, `PlatformFlag`, and `AllPlatformsFlag`.

Control flow: if `--all-platforms` is set, return platforms from image manifest/index using content store. Otherwise parse each `--platform` string. If neither is set, return an empty slice and let callers choose defaults.

State and persistence: read-only content store access when all platforms are requested.

Dependencies and integration: containerd images/content and `containerd/platforms`.

Risks and test signals: comments contain a typo in `all-plaforms`; no tests cover precedence or invalid platform parsing in this subset.
<!-- END_FILE_RESEARCH: sources/cloud-native/soci-snapshotter/cmd/soci/commands/internal/platform.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/soci-snapshotter/cmd/soci/commands/internal/prefetch.go -->
## sources/cloud-native/soci-snapshotter/cmd/soci/commands/internal/prefetch.go

Purpose: shared flags and parsing for embedding prefetch file paths in SOCI metadata.

Important APIs/types/functions: `PrefetchFlags`, `ParsePrefetchFiles`, `loadPrefetchFilesFromJSON`, and `trimAndFilterFiles`.

Control flow: collect repeated `--prefetch-file` values, trim/filter blank entries, optionally read JSON array from `--prefetch-files-json`, trim/filter those, and return combined paths.

State and persistence: reads a JSON file when configured; no writes.

Dependencies and integration: used by create/convert builder option construction to call `soci.WithPrefetchPaths`.

Risks and test signals: no deduplication or path normalization; JSON must be a raw string array. No direct tests here.
<!-- END_FILE_RESEARCH: sources/cloud-native/soci-snapshotter/cmd/soci/commands/internal/prefetch.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/soci-snapshotter/cmd/soci/commands/internal/registry.go -->
## sources/cloud-native/soci-snapshotter/cmd/soci/commands/internal/registry.go

Purpose: shared registry transport/auth flags and credential resolution.

Important APIs/types/functions: registry flag constants, `RegistryFlags`, and `ResolveCredentials`.

Control flow: `ResolveCredentials` prefers explicit `--user username[:password]`; otherwise it loads Docker CLI default config and returns matching host credentials, falling back to empty public credentials.

State and persistence: reads Docker config; does not write.

Dependencies and integration: used by push to configure ORAS remote auth and transport options.

Risks and test signals: TLS and tracing flags are declared but not consumed in the push path shown here. Passwordless `--user` returns empty password. No direct tests here.
<!-- END_FILE_RESEARCH: sources/cloud-native/soci-snapshotter/cmd/soci/commands/internal/registry.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/soci-snapshotter/cmd/soci/commands/internal/snapshotter.go -->
## sources/cloud-native/soci-snapshotter/cmd/soci/commands/internal/snapshotter.go

Purpose: defines a shared snapshotter name flag.

Important APIs/types/functions: `SnapshotterFlag` and `SnapshotterFlags`.

Control flow: no direct execution; commands can read the flag, defaulting to empty or `CONTAINERD_SNAPSHOTTER`.

State and persistence: none.

Dependencies and integration: used by commands that need to pass a snapshotter name to containerd operations.

Risks and test signals: no validation and no direct tests in this subset.
<!-- END_FILE_RESEARCH: sources/cloud-native/soci-snapshotter/cmd/soci/commands/internal/snapshotter.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/soci-snapshotter/cmd/soci/commands/internal/standalone.go -->
## sources/cloud-native/soci-snapshotter/cmd/soci/commands/internal/standalone.go

Purpose: OCI-layout load/save helpers for standalone conversion without containerd.

Important APIs/types/functions: `StandaloneImageInfo`, `LoadImage`, `SaveImageToTar`, `SaveImageToDir`, `resolveLayoutRoot`, and `blobPath`.

Control flow: load copies a directory or extracts a tar into a temp layout, reads `index.json`, resolves a root descriptor, and opens ORAS/local content stores. Save-to-tar exports a manifest through containerd archive. Save-to-dir copies layout and writes a clean `index.json` containing only the converted descriptor. Root resolution handles single manifests, nested indexes, and filtered platform lists with missing blobs.

State and persistence: reads/writes OCI layout directories, blobs, `index.json`, and tar output.

Dependencies and integration: containerd archive/content, ORAS OCI store, OCI specs, digest utilities.

Risks and test signals: `SaveImageToDir` removes output path before copying. `os.CopyFS` behavior depends on destination cleanliness. No direct tests here.
<!-- END_FILE_RESEARCH: sources/cloud-native/soci-snapshotter/cmd/soci/commands/internal/standalone.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/soci-snapshotter/cmd/soci/commands/internal/store.go -->
## sources/cloud-native/soci-snapshotter/cmd/soci/commands/internal/store.go

Purpose: converts global CLI flags into SOCI store options.

Important APIs/types/functions: `ContentStoreOptions`.

Control flow: reads content-store type, containerd address, and root flags, then returns `store.WithType`, `store.WithContainerdAddress`, and `store.WithSnapshotterRoot`.

State and persistence: no direct state; returned options determine later DB/content-store paths and connections.

Dependencies and integration: used by create, convert, push, index, ztoc, prefetch, and rebuild commands when opening `store.NewContentStore`.

Risks and test signals: this helper does not trim `unix://` prefixes unlike `NewClient`; downstream store must handle address shape. No direct tests here.
<!-- END_FILE_RESEARCH: sources/cloud-native/soci-snapshotter/cmd/soci/commands/internal/store.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/soci-snapshotter/cmd/soci/commands/prefetch/info.go -->
## sources/cloud-native/soci-snapshotter/cmd/soci/commands/prefetch/info.go

Purpose: implements `soci prefetch info`, displaying details of a prefetch artifact.

Important APIs/types/functions: `infoCommand` and `prettyPrintJSON`.

Control flow: parse digest, open artifacts DB, verify artifact type is prefetch, fetch artifact bytes from selected content store, unmarshal prefetch artifact, walk DB for metadata, print summary and span ranges, and optionally print raw JSON.

State and persistence: read-only against artifacts DB and content store.

Dependencies and integration: SOCI prefetch artifact unmarshalling, store abstraction, digest parsing, command context.

Risks and test signals: DB walk uses `fmt.Errorf("found")` as a sentinel to stop but ignores the returned error, which is intentional but brittle. No direct tests here.
<!-- END_FILE_RESEARCH: sources/cloud-native/soci-snapshotter/cmd/soci/commands/prefetch/info.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/soci-snapshotter/cmd/soci/commands/prefetch/list.go -->
## sources/cloud-native/soci-snapshotter/cmd/soci/commands/prefetch/list.go

Purpose: implements `soci prefetch list`, listing prefetch artifacts and span counts.

Important APIs/types/functions: `listCommand`, local `prefetchInfo`, `addPrefetchInfo`, and `getDuration`.

Control flow: open command context, artifacts DB, and content store; walk DB entries of prefetch type; parse digest and fetch/unmarshal each artifact when possible to compute total spans; then print JSON or tabular output.

State and persistence: read-only against artifacts DB and content store.

Dependencies and integration: SOCI artifact DB, store fetch, prefetch artifact schema, tabwriter/JSON encoder.

Risks and test signals: malformed or missing artifacts are still listed with `N/A`, which is user-friendly but can hide store/DB drift unless JSON is inspected. No direct tests here.
<!-- END_FILE_RESEARCH: sources/cloud-native/soci-snapshotter/cmd/soci/commands/prefetch/list.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/soci-snapshotter/cmd/soci/commands/prefetch/prefetch.go -->
## sources/cloud-native/soci-snapshotter/cmd/soci/commands/prefetch/prefetch.go

Purpose: command group definition for `soci prefetch`.

Important APIs/types/functions: `Command` and `JSONFlag`.

Control flow: registers `listCommand` and `infoCommand`; execution is delegated to those files.

State and persistence: none directly.

Dependencies and integration: urfave cli and sibling prefetch command implementations.

Risks and test signals: no direct tests; coverage depends on subcommand registration and behavior.
<!-- END_FILE_RESEARCH: sources/cloud-native/soci-snapshotter/cmd/soci/commands/prefetch/prefetch.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/soci-snapshotter/cmd/soci/commands/push.go -->
## sources/cloud-native/soci-snapshotter/cmd/soci/commands/push.go

Purpose: implements `soci push`, uploading local SOCI v1 artifacts for an image to a registry.

Important APIs/types/functions: `PushCommand`, `pushDescs`, `debugClient`, and constants for quiet/concurrency flags.

Control flow: parse image ref, connect to containerd, resolve platforms, open artifacts DB and selected source store, build ORAS remote repository and auth, validate existing-index policy, choose most recent v1 SOCI index per platform while warning on v2, optionally inspect remote referrers, then copy each artifact graph with ORAS.

State and persistence: reads local content/artifacts DB and writes remote registry artifacts; no local mutation except network-side effects.

Dependencies and integration: containerd image/content, SOCI descriptor lookup, ORAS copy graph, remote auth, OCI artifact referrers, registry credentials.

Risks and test signals: v2 indexes are intentionally skipped. Existing remote checks rely on referrers support. TLS-related flags are declared elsewhere but not fully wired here. No direct tests here.
<!-- END_FILE_RESEARCH: sources/cloud-native/soci-snapshotter/cmd/soci/commands/push.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/soci-snapshotter/cmd/soci/commands/rebuild_db.go -->
## sources/cloud-native/soci-snapshotter/cmd/soci/commands/rebuild_db.go

Purpose: implements `soci rebuild-db`, synchronizing artifacts DB with local content store blobs.

Important APIs/types/functions: `RebuildDBCommand`.

Control flow: connect to containerd, open artifacts DB, open configured blob store, compute content-store blob path from store type/root, and call `artifactsDb.SyncWithLocalStore`.

State and persistence: mutates artifacts DB based on local store and containerd content.

Dependencies and integration: containerd content store, SOCI store path helpers, artifacts DB sync logic.

Risks and test signals: correctness depends on store path layout and `SyncWithLocalStore`. No direct tests here.
<!-- END_FILE_RESEARCH: sources/cloud-native/soci-snapshotter/cmd/soci/commands/rebuild_db.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/soci-snapshotter/cmd/soci/commands/ztoc/get-file.go -->
## sources/cloud-native/soci-snapshotter/cmd/soci/commands/ztoc/get-file.go

Purpose: implements `soci ztoc get-file`, extracting one file from a local image layer using a zTOC.

Important APIs/types/functions: `getFileCommand`, `getZtoc`, and `getLayer`.

Control flow: require zTOC digest and file path args, connect to containerd, fetch/unmarshal zTOC from selected SOCI store, open artifacts DB, find original layer digest, open layer `ReaderAt` from containerd content store, extract file via zTOC, and write to output path or stdout.

State and persistence: read-only except optional output file write.

Dependencies and integration: zTOC package, artifacts DB, selected store for zTOC, containerd content for layer data.

Risks and test signals: `os.WriteFile` errors and permissions use mode `0`, and output write error is ignored. No direct tests here.
<!-- END_FILE_RESEARCH: sources/cloud-native/soci-snapshotter/cmd/soci/commands/ztoc/get-file.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/soci-snapshotter/cmd/soci/commands/ztoc/info.go -->
## sources/cloud-native/soci-snapshotter/cmd/soci/commands/ztoc/info.go

Purpose: implements `soci ztoc info`, emitting JSON metadata for a zTOC.

Important APIs/types/functions: `Info`, `FileInfo`, and `infoCommand`.

Control flow: parse digest, open artifacts DB, reject SOCI index digests, open selected content store, fetch and unmarshal zTOC, open gzip index info, clear checkpoints, compute per-file span ranges and multi-span count, marshal indented JSON, and print.

State and persistence: read-only against DB/store.

Dependencies and integration: SOCI artifact metadata, zTOC compression metadata, store abstraction.

Risks and test signals: full file metadata is printed, which can be very large or sensitive. No direct tests here.
<!-- END_FILE_RESEARCH: sources/cloud-native/soci-snapshotter/cmd/soci/commands/ztoc/info.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/soci-snapshotter/cmd/soci/commands/ztoc/list.go -->
## sources/cloud-native/soci-snapshotter/cmd/soci/commands/ztoc/list.go

Purpose: implements `soci ztoc list`, listing zTOC layer artifacts globally or for an image.

Important APIs/types/functions: `listCommand` with filters for zTOC digest, image ref, and quiet output.

Control flow: open artifacts DB; if no image ref, walk DB for layer entries. If image ref is supplied, connect to containerd, resolve image platforms, find SOCI index descriptors, decode each index from content store, collect SOCI layer blob descriptors, then map them back to DB entries for layer digest metadata.

State and persistence: read-only against artifacts DB and containerd content/image services.

Dependencies and integration: SOCI index decode, artifacts DB, containerd image platform resolution, content store reader.

Risks and test signals: stale DB entries missing content are skipped only during image-ref path. Digest plus image-ref mismatch returns explicit error. No direct tests here.
<!-- END_FILE_RESEARCH: sources/cloud-native/soci-snapshotter/cmd/soci/commands/ztoc/list.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/soci-snapshotter/cmd/soci/commands/ztoc/ztoc.go -->
## sources/cloud-native/soci-snapshotter/cmd/soci/commands/ztoc/ztoc.go

Purpose: command group definition for `soci ztoc`.

Important APIs/types/functions: `Command` with `infoCommand`, `getFileCommand`, and `listCommand`.

Control flow: no logic beyond registering subcommands.

State and persistence: none directly; subcommands read zTOC and layer artifacts and may write an extracted file.

Dependencies and integration: urfave cli and sibling zTOC command implementations.

Risks and test signals: no direct tests; registration bugs would hide subcommands from the CLI.
<!-- END_FILE_RESEARCH: sources/cloud-native/soci-snapshotter/cmd/soci/commands/ztoc/ztoc.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/soci-snapshotter/cmd/soci/main.go -->
## sources/cloud-native/soci-snapshotter/cmd/soci/main.go

Purpose: entrypoint for the `soci` CLI.

Important APIs/types/functions: `main` builds a `cli.Command` with global flags, version, command groups, and a `Before` hook.

Control flow: register index, ztoc, prefetch, create, convert, push, and rebuild-db commands. Before each command, ensure snapshotter root exists except for standalone convert. Run app with cancellable background context and exit nonzero on error.

State and persistence: may create the snapshotter root path before most commands.

Dependencies and integration: command packages, config/global flags, version metadata, and `soci.EnsureSnapshotterRootPath`.

Risks and test signals: the `Before` hook assumes the nested command lookup for standalone convert is safe. No direct tests for command registration in this subset.
<!-- END_FILE_RESEARCH: sources/cloud-native/soci-snapshotter/cmd/soci/main.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/soci-snapshotter/config/config.go -->
## sources/cloud-native/soci-snapshotter/config/config.go

Purpose: root configuration model and TOML loading/defaulting entrypoints.

Important APIs/types/functions: `Config`, `NewConfig`, `NewConfigFromToml`, `parseConfig`, `parseRootConfig`, and default path constants.

Control flow: `NewConfig` initializes defaults that differ from zero values, then runs root/service/fs/parallel parsers. `NewConfigFromToml` returns defaults when the default config path is absent, otherwise decodes TOML over defaults and reparses normalization/default logic.

State and persistence: reads a TOML file; no writes.

Dependencies and integration: embeds `ServiceConfig`, used by daemon startup and config dump/default commands.

Risks and test signals: `NewConfig` returns nil if parser errors, though current defaults should not error. Tests cover defaults, empty TOML, and parse failures for chunk size.
<!-- END_FILE_RESEARCH: sources/cloud-native/soci-snapshotter/config/config.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/soci-snapshotter/config/config.toml -->
## sources/cloud-native/soci-snapshotter/config/config.toml

Purpose: sample/default TOML configuration for soci-snapshotter-grpc.

Important settings: covers top-level metrics/debug/metadata flags, HTTP retry/timeout config, blob fetch settings, directory cache behavior, FUSE timeouts, background fetch, content store selection, prefetch, pull modes, keychains, resolver, and snapshotter mount policy.

Control flow: consumed by `config.NewConfigFromToml`; values are decoded into `Config` then normalized by parser functions.

State and persistence: no runtime state itself; selecting stores, paths, and pull modes affects daemon persistence and network behavior.

Dependencies and integration: mirrors TOML tags across `config` package structs.

Risks and test signals: this file sets content store type to `soci`, while `DefaultContentStoreType` constant is `containerd` for CLI default and parser default is SOCI when empty, so readers must distinguish sample config from CLI defaults. Tests validate parser behavior, not this exact file.
<!-- END_FILE_RESEARCH: sources/cloud-native/soci-snapshotter/config/config.toml -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/soci-snapshotter/config/config_test.go -->
## sources/cloud-native/soci-snapshotter/config/config_test.go

Purpose: verifies config defaults, TOML parsing, decompression stream parsing, parallel fallback settings, and size-string parsing.

Important APIs/types/functions: `TestConfigDefaults`, `TestNewConfigFromToml`, and `TestSizeParser`.

Control flow: default test compares many fields from `NewConfig` with default constants. TOML tests write temporary config files and assert decoded structures or errors. Size parser tests cover units, decimals, spacing, zero, negative, and invalid strings.

State and persistence: uses temporary config files only.

Dependencies and integration: exercises `NewConfigFromToml`, `DefaultPullModes`, parser functions, and `parseSize`.

Risks and test signals: broad default coverage is strong. It does not test default config path missing behavior, content-store socket trimming, or invalid relationships between parallel limits.
<!-- END_FILE_RESEARCH: sources/cloud-native/soci-snapshotter/config/config_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/soci-snapshotter/config/defaults.go -->
## sources/cloud-native/soci-snapshotter/config/defaults.go

Purpose: centralizes default constants for root, service, filesystem, blob, HTTP retry, content store, pull mode, and parallel pull settings.

Important APIs/types/functions: constants such as `defaultMetricsNetwork`, `DefaultImageServiceAddress`, `Unbounded`, `defaultMaxConcurrency`, `DefaultContentStoreType`, `DefaultSOCIV1Enable`, `DefaultSOCIV2Enable`, and parallel limit defaults.

Control flow: no executable logic; parser files consume these constants to fill zero-value configuration.

State and persistence: none directly.

Dependencies and integration: used throughout config parser and tests.

Risks and test signals: comments note experimental GC edge cases for parallel-pull fallback. Defaults can diverge from sample config if not kept in sync; tests assert many constant-to-config relationships.
<!-- END_FILE_RESEARCH: sources/cloud-native/soci-snapshotter/config/defaults.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/soci-snapshotter/config/doc.go -->
## sources/cloud-native/soci-snapshotter/config/doc.go

Purpose: package documentation and import path declaration for `github.com/awslabs/soci-snapshotter/config`.

Important APIs/types/functions: no functions; package comment describes default configuration and TOML parsing utilities.

Control flow: none.

State and persistence: none.

Dependencies and integration: affects Go documentation and import identity.

Risks and test signals: no behavior and no tests needed.
<!-- END_FILE_RESEARCH: sources/cloud-native/soci-snapshotter/config/doc.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/soci-snapshotter/config/fs.go -->
## sources/cloud-native/soci-snapshotter/config/fs.go

Purpose: defines filesystem/lazy-pull related configuration structs and normalization logic.

Important APIs/types/functions: `FSConfig`, `PrefetchConfig`, `BlobConfig`, `DirectoryCacheConfig`, `FuseConfig`, `BackgroundFetchConfig`, `RetryConfig`, `TimeoutConfig`, `ContentStoreConfig`, `TrimSocketAddress`, `parseFSConfig`, and nested parse functions.

Control flow: `parseFSConfig` fills defaults for mount timeout, FUSE metrics wait, max concurrency, and prefetch concurrency, then runs FUSE/background/HTTP/blob/content-store parsers. Blob retries inherit HTTP retry defaults. Content store defaults to SOCI and trims `unix://` from containerd addresses.

State and persistence: no direct state; config drives cache, FUSE, background fetch, content-store, and network behavior.

Dependencies and integration: daemon service config, cache config, resolver/fetch code, and store selection.

Risks and test signals: negative `PrefetchConfig.MaxConcurrency` is reset to default zero, while negative `MaxConcurrency` disables limits. Tests cover many defaults but not every normalization branch.
<!-- END_FILE_RESEARCH: sources/cloud-native/soci-snapshotter/config/fs.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/soci-snapshotter/config/parallel.go -->
## sources/cloud-native/soci-snapshotter/config/parallel.go

Purpose: configuration model and parser for parallel pull/unpack concurrency and decompression.

Important APIs/types/functions: `DecompressStream`, `ParallelConfig`, `defaultParallelConfig`, `parseParallelConfig`, and `parseSize`.

Control flow: parser converts `ConcurrentDownloadChunkSizeStr` into bytes. `parseSize` accepts B/KB/MB/GB units, decimals, whitespace, and zero-as-default.

State and persistence: none directly; parsed values guide runtime semaphores and chunked network reads.

Dependencies and integration: embedded in `PullModes.Parallel`, used by adaptive fetch/unpack job manager.

Risks and test signals: `parseSize` regex rejects negative values before numeric parsing, so the "negative" test expects an error rather than a negative value. Tests cover accepted units and invalid strings.
<!-- END_FILE_RESEARCH: sources/cloud-native/soci-snapshotter/config/parallel.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/soci-snapshotter/config/pull_modes.go -->
## sources/cloud-native/soci-snapshotter/config/pull_modes.go

Purpose: defines pull mode switches for SOCI v1, SOCI v2, and parallel pull/unpack.

Important APIs/types/functions: `PullModes`, `V1`, `V2`, `Parallel`, `defaultPullModes`, and `DefaultPullModes`.

Control flow: defaulting creates SOCI v1 disabled, SOCI v2 enabled, parallel disabled, and default parallel config embedded.

State and persistence: no direct state; controls snapshotter runtime strategy for lazy loading, v2 manifest annotation discovery, and parallel fallback.

Dependencies and integration: consumed by daemon service creation and adaptive fetch job setup.

Risks and test signals: fallback mode is marked experimental and tied to containerd content-store GC concerns. Config tests assert defaults and a fallback TOML scenario.
<!-- END_FILE_RESEARCH: sources/cloud-native/soci-snapshotter/config/pull_modes.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/soci-snapshotter/config/resolver.go -->
## sources/cloud-native/soci-snapshotter/config/resolver.go

Purpose: TOML model for registry resolver mirrors and per-host settings.

Important APIs/types/functions: `ResolverConfig`, `HostConfig`, and `MirrorConfig`.

Control flow: no parsing logic in this file; TOML decoder fills maps/slices based on tags.

State and persistence: none directly; values influence registry resolution elsewhere.

Dependencies and integration: embedded in `ServiceConfig` and used by service/resolver code outside this subset.

Risks and test signals: no validation here for hostnames, mirror schemes, or timeout ranges. No direct tests in this subset.
<!-- END_FILE_RESEARCH: sources/cloud-native/soci-snapshotter/config/resolver.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/soci-snapshotter/config/service.go -->
## sources/cloud-native/soci-snapshotter/config/service.go

Purpose: service-level configuration composition for filesystem, pull modes, keychains, resolver, and snapshotter behavior.

Important APIs/types/functions: `ServiceConfig`, `KubeconfigKeychainConfig`, `CRIKeychainConfig`, `SnapshotterConfig`, and `parseServiceConfig`.

Control flow: `parseServiceConfig` defaults CRI image service path to containerd's image service socket when unset.

State and persistence: no direct state; values configure daemon credential sources and snapshotter mounting policy.

Dependencies and integration: daemon startup reads these fields to configure kube/CRI/docker keychains, resolver, filesystem options, and service behavior.

Risks and test signals: only CRI path receives parser validation/defaulting here; other fields rely on consumers. Config tests assert CRI default path.
<!-- END_FILE_RESEARCH: sources/cloud-native/soci-snapshotter/config/service.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/soci-snapshotter/fs/adaptive_fetch_image_layers.go -->
## sources/cloud-native/soci-snapshotter/fs/adaptive_fetch_image_layers.go

Purpose: manages parallel image layer download/unpack jobs, resource limits, on-disk temporary unpack state, and garbage collection.

Important APIs/types/functions: `SemaphoreWithNil`, `unpackJobs`, `newUnpackJobs`, `checkParallelPullUnpack`, `LayerUnpackJobStorage`, `LayerUnpackDiskStorage`, `imageUnpackJob`, `layerUnpackJob`, `LayerUnpackResourceController`, and garbage collector policies.

Control flow: create job manager from parallel config, validate limits, build global semaphores, start garbage collector, add image/layer jobs, claim layer jobs for unpack, acquire download/unpack leases, read ingest tarballs, verify empty unpack destination, and remove or cancel jobs. Disk storage recreates `root/unpack` fresh and creates random job dirs with `fs` subdirs.

State and persistence: in-memory image/layer maps plus temporary disk job directories under `unpack`; GC removes untracked disk jobs and expires long-running in-memory jobs.

Dependencies and integration: config parallel settings, containerd logging, OS filesystem, semaphores, and unpacker consumers.

Risks and test signals: random ID generation has finite retries; `newLayerUnpackDiskStorage` deletes existing unpack root on startup; expiry cancels whole image jobs. Tests cover validation, GC, disk storage, claims, paths, and disabled parallel struct creation.
<!-- END_FILE_RESEARCH: sources/cloud-native/soci-snapshotter/fs/adaptive_fetch_image_layers.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/soci-snapshotter/fs/adaptive_fetch_image_layers_test.go -->
## sources/cloud-native/soci-snapshotter/fs/adaptive_fetch_image_layers_test.go

Purpose: validates parallel pull job manager, garbage collection, disk storage, and layer job behavior.

Important APIs/types/functions: `TestParallelPullUnpackValidation`, `TestNoGoroutinesAreLeakedWhenGarbageCollectionIsCancelled`, GC tests, `LayerUnpackVirtualStorage`, `TestLayerUnpackDiskStorage`, `TestLayerUnpackJob`, and `TestParallelStructCreation`.

Control flow: tests use a shortened GC interval, virtual storage for most GC behavior, temp dirs for disk storage, `goleak` for goroutine cleanup, and fake timestamps to simulate expired jobs.

State and persistence: temp directories and virtual `sync.Map` storage emulate persistent unpack jobs.

Dependencies and integration: exercises `newUnpackJobs`, storage interface, job claim/path methods, and `createParallelPullStructs` from nearby fs code.

Risks and test signals: strong coverage of lifecycle and cleanup. Tests do not exercise actual network download, decompression, semaphore blocking under contention, or destination poisoning beyond path setup.
<!-- END_FILE_RESEARCH: sources/cloud-native/soci-snapshotter/fs/adaptive_fetch_image_layers_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/soci-snapshotter/fs/artifact_fetcher.go -->
## sources/cloud-native/soci-snapshotter/fs/artifact_fetcher.go

Purpose: fetches SOCI artifacts from local store or remote registry and stores/labels them locally.

Important APIs/types/functions: `Fetcher`, `artifactFetcher`, `orasBlobStore`, `newRemoteBlobStore`, `Resolve`, `Fetch`, `FetchRange`, `doInitialFetch`, `newArtifactFetcher`, `FetchSociArtifacts`, and helper error redaction.

Control flow: remote blob store resolves descriptors with registry blob headers and supports ranged GETs. `artifactFetcher.Fetch` tries local store first, resolves size when descriptor size is zero, then fetches remote. `FetchSociArtifacts` fetches and decodes an index, opens a store batch, stores and GC-labels index if remote, then concurrently fetches/stores each zTOC and labels GC refs.

State and persistence: writes artifacts to local SOCI/content store and applies GC labels; reads remote registry content.

Dependencies and integration: ORAS remote/content APIs, containerd reference/docker localhost handling, SOCI store/index encoding, fs remote URL helpers, internal HTTP redaction.

Risks and test signals: `GetContentWithRange` returns an error wrapping a possibly nil `err` for bad status. Concurrent blob fetch labels depend on stable loop index capture. Tests cover ref construction, local-vs-remote fetching, size resolve, store digest errors, remote store plain HTTP, and corrupted artifact failures.
<!-- END_FILE_RESEARCH: sources/cloud-native/soci-snapshotter/fs/artifact_fetcher.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/soci-snapshotter/fs/artifact_fetcher_test.go -->
## sources/cloud-native/soci-snapshotter/fs/artifact_fetcher_test.go

Purpose: validates artifact fetcher reference construction, local cache behavior, descriptor resolution, store verification, remote store creation, and SOCI artifact graph fetch.

Important APIs/types/functions: `TestConstructRef`, `TestArtifactFetcherFetch`, `TestArtifactFetcherResolve`, `TestArtifactFetcherFetchOnlyOnce`, `TestArtifactFetcherStore`, `TestNewRemoteStore`, `TestFetchSociArtifacts`, and fake local/remote stores.

Control flow: tests use ORAS memory stores and fake resolver/storage to simulate local miss, remote fetch, subsequent local hit, digest mismatch, localhost plain HTTP, and corrupted index/zTOC data.

State and persistence: all state is in memory; fake local store implements batch/delete/label methods needed by `FetchSociArtifacts`.

Dependencies and integration: SOCI index marshal/unmarshal, ORAS memory content, digest verification, containerd reference parsing.

Risks and test signals: good behavioral coverage for fetcher core. Tests do not cover real HTTP range requests, redaction paths, auth behavior, GC label failures, or remote status-code edge cases.
<!-- END_FILE_RESEARCH: sources/cloud-native/soci-snapshotter/fs/artifact_fetcher_test.go -->
