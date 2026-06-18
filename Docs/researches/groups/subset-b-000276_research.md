# Research Group subset-b-000276

Grouped research for the requested stargz-snapshotter source files. Each section preserves the source path in its title and is bounded for deterministic splitting into source-tree-aligned per-file reports.

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/stargz-snapshotter/analyzer/fanotify/conn/conn.go -->
# sources/cloud-native/stargz-snapshotter/analyzer/fanotify/conn/conn.go

Purpose: Defines the small line-oriented stdio protocol used between the analyzer parent process and a fanotify helper process. The protocol messages are `start`, `started`, `ack`, and `fd:<number>`.

Important APIs: `NewClient`, `Client.Start`, `Client.GetPath`, `NewService`, `Service.WaitStart`, `Service.SendStarted`, and `Service.SendFd`. The client sends `start`, waits for `started`, receives file descriptor numbers, resolves them through `/proc/<servicePid>/fd/<fd>`, and acknowledges each descriptor. The service waits for start, signals readiness, sends descriptors, and waits for acknowledgements.

Control flow: `scanWithTimeout` wraps `bufio.Scanner.Scan` in a goroutine and races it with `time.After`. `GetPath` deliberately has no timeout because it is the blocking event stream. `writeMessage` appends a newline so scanner tokenization remains simple.

State and persistence: The only durable state is the external file descriptor held by the service process. In-memory state includes the scanner, service PID, and timeout.

Dependencies and integration: Used by `analyzer/fanotify/fanotify.go` and `analyzer/fanotify/service/service.go`; depends on `/proc` visibility in the client namespace.

Risks: `scanWithTimeout` can leave a blocked goroutine if the timeout wins. Scanner default token size is acceptable for short control messages. Path resolution fails if `/proc/<pid>/fd` is unavailable or the descriptor closes before resolution.

Test signals: No direct tests in this subset; behavior is indirectly exercised by analyzer fanotify flows.
<!-- END_FILE_RESEARCH: sources/cloud-native/stargz-snapshotter/analyzer/fanotify/conn/conn.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/stargz-snapshotter/analyzer/fanotify/fanotify.go -->
# sources/cloud-native/stargz-snapshotter/analyzer/fanotify/fanotify.go

Purpose: Spawns and controls the hidden `ctr-remote fanotify /` helper in a new mount namespace so the analyzer can observe file accesses inside a prepared root filesystem.

Important APIs: `SpawnFanotifier`, `Fanotifier.Start`, `Fanotifier.GetPath`, `Fanotifier.MountNamespacePath`, and `Fanotifier.Close`. `SpawnFanotifier` builds `exec.Command(fanotifierBin, "fanotify", "/")`, sets `CLONE_NEWNS`, wires stdin/stdout pipes, starts the process, and wraps those pipes with `conn.Client`.

Control flow: Callers create the process, use `MountNamespacePath` to join or bind work to the helper's mount namespace, call `Start` to trigger service-side marking, then repeatedly call `GetPath` for notified paths. `Close` kills the process and closes both pipes once.

State and persistence: Keeps process handle, client connection, and a `sync.Once` guarded close path. No persistent data is written here.

Dependencies and integration: Depends on Linux mount namespaces, `syscall.SysProcAttr`, and the fanotify service exposed by `cmd/ctr-remote/commands/notify.go`.

Risks: `Close` kills but does not `Wait`, so process reaping depends on surrounding code. Failure after one pipe is opened but before process start can leave cleanup responsibility with the caller. Requires privileges/capabilities for namespace and fanotify operations.

Test signals: No local unit tests; integration coverage would need privileged fanotify and namespace support.
<!-- END_FILE_RESEARCH: sources/cloud-native/stargz-snapshotter/analyzer/fanotify/fanotify.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/stargz-snapshotter/analyzer/fanotify/service/service.go -->
# sources/cloud-native/stargz-snapshotter/analyzer/fanotify/service/service.go

Purpose: Implements the service-side fanotify monitor and an in-process pre-container monitor. It converts kernel fanotify events into fd messages or path sets used for optimization recording.

Important APIs: `Serve(target, r, w)` runs the helper protocol and event loop. `PreContainerMonitor` exposes `NewPreContainerMonitor`, `Start`, `Monitor`, `GetPaths`, and `Close`.

Control flow: `Serve` initializes fanotify with `FAN_CLASS_NOTIF`, waits for the client start message, marks the target mount with `FAN_MARK_MOUNT` for access/open events, sends `started`, then reads `unix.FanotifyEventMetadata` records. Valid event fds are sent to the client via `conn.Service.SendFd`, then closed. `PreContainerMonitor.Start` marks an entire filesystem with `FAN_MARK_FILESYSTEM`; `Monitor` resolves event fds through `/proc/self/fd`, stores paths in a protected set, and exits on EOF, done channel, or fd close.

State and persistence: State is in memory: fanotify file, target dir, path set, done channel, close flags. No persistence.

Dependencies and integration: Uses `golang.org/x/sys/unix` fanotify APIs. `Serve` is invoked by the hidden ctr command; `PreContainerMonitor` is used by analyzer options for GPU/pre-monitor sampling.

Risks: Requires kernel fanotify support and privileges. Queue overflows only print warnings and lose events. `Monitor` can return read errors unless closure is observed. Path capture depends on `/proc/self/fd`.

Test signals: No direct tests; correctness needs privileged integration tests.
<!-- END_FILE_RESEARCH: sources/cloud-native/stargz-snapshotter/analyzer/fanotify/service/service.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/stargz-snapshotter/analyzer/option.go -->
# sources/cloud-native/stargz-snapshotter/analyzer/option.go

Purpose: Defines the functional options used to configure image access analysis runs.

Important APIs: `Option`, `SpecOpts`, `WithSpecOpts`, `WithTerminal`, `WithStdin`, `WithPeriod`, `WithWaitOnSignal`, `WithSnapshotter`, `WithWaitLineOut`, and `WithPreMonitor`. `SpecOpts` allows callers to provide OCI spec options and a cleanup callback based on the selected image and mounted rootfs.

Control flow: Each option mutates `analyzerOpts`; `Analyze` in the sibling analyzer package reads those fields to decide runtime duration, container IO, snapshotter, signal behavior, line-based termination, and whether to run a pre-container fanotify phase.

State and persistence: Only transient configuration. There is no I/O here.

Dependencies and integration: Couples analyzer configuration to containerd image and OCI spec option types. `cmd/ctr-remote/commands/optimize.go` constructs these options from CLI flags and sampler flags.

Risks: `WithTerminal` depends on `WithStdin`, but enforcement is performed by callers rather than this option package. Nil `SpecOpts` means analyzer must fall back to defaults.

Test signals: No direct tests in this file; coverage comes from optimize/analyzer command behavior.
<!-- END_FILE_RESEARCH: sources/cloud-native/stargz-snapshotter/analyzer/option.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/stargz-snapshotter/analyzer/recorder/recorder.go -->
# sources/cloud-native/stargz-snapshotter/analyzer/recorder/recorder.go

Purpose: Maps accessed image paths back to the layer index that currently provides each file, then writes recorder entries for use as prioritized files during eStargz or zstd:chunked conversion.

Important APIs: `NewImageRecorder`, `Record`, `RecordGlob`, `Commit`, and `Close`. Internally, `imageRecorderFromManifest` builds a per-layer path index by reading and optionally decompressing each layer tar. `cleanEntryName` normalizes root-relative paths.

Control flow: Construction resolves the image manifest for a platform, reads manifest JSON, iterates layers, opens each layer blob, decompresses when needed, and scans tar headers into `filesMap`. `Record` normalizes a name, skips duplicates, searches layers from top to bottom, rejects paths masked by whiteout files or opaque directory whiteouts, then emits a `recorder.Entry` with manifest digest and layer index. `RecordGlob` lazily merges all paths and applies an injected matcher.

State and persistence: Holds path indexes, a content writer for the record stream, a duplicate set, and an all-path cache. `Commit` commits the content writer and returns its digest.

Dependencies and integration: Uses containerd content/images APIs, manifest selection helpers, tar/compression utilities, and the shared `recorder` package. Used by `ctr-remote optimize --prefetch-list`.

Risks: Layer scanning is potentially expensive and comments note duplicate decompression during optimization. `RecordGlob` ignores individual `Record` failures, which is intentional for deleted or missing entries but can hide unexpected problems.

Test signals: `recorder_test.go` verifies layer selection, overlay precedence, path normalization, compressed and uncompressed layers, and whiteout rejection.
<!-- END_FILE_RESEARCH: sources/cloud-native/stargz-snapshotter/analyzer/recorder/recorder.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/stargz-snapshotter/analyzer/recorder/recorder_test.go -->
# sources/cloud-native/stargz-snapshotter/analyzer/recorder/recorder_test.go

Purpose: Validates that `ImageRecorder` maps paths to the correct image layer and handles OCI overlay semantics.

Important APIs tested: `imageRecorderFromManifest`, `ImageRecorder.Record`, `ImageRecorder.Commit`, and the emitted `recorder.Entry` JSON stream. Helper `gzipCompress` creates compressed layer inputs.

Control flow: Table cases build synthetic layer tar blobs into a local containerd content store, create a manifest descriptor list, instantiate the recorder, record requested paths, commit the output, then decode the resulting content blob and compare path/layer-index pairs in order. The tests run across accepted path prefixes (`""`, `"./"`, `"/"`, `"../"`) and both uncompressed and gzip layer media types.

State and persistence: Uses a temporary local content store and removes it after the test. Each layer and record output is committed as content-store data.

Dependencies and integration: Uses containerd local content store, testutil tar builders, OCI descriptors, gzip, and the production recorder JSON entry type.

Risks covered: Duplicate names across layers must resolve to the topmost layer. Whiteout files and opaque directory whiteouts must cause recording to fail for deleted paths. Non-regular tar entry types such as symlink, device, and fifo are indexed by name.

Test signals: Strong focused coverage for path normalization and overlay behavior. It does not cover `RecordGlob`, concurrent `Record`, or content-store error paths.
<!-- END_FILE_RESEARCH: sources/cloud-native/stargz-snapshotter/analyzer/recorder/recorder_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/stargz-snapshotter/cache/cache.go -->
# sources/cloud-native/stargz-snapshotter/cache/cache.go

Purpose: Provides blob cache implementations used by lazy pulling: a directory-backed cache with optional memory and fd LRU caches, and a simple in-memory cache.

Important APIs: `BlobCache`, `Reader`, `Writer`, `NewDirectoryCache`, `NewMemoryCache`, `Direct`, and `PassThrough`. `DirectoryCacheConfig` controls LRU sizes, sync behavior, supplied caches/pools, direct mode, and `FADV_DONTNEED`.

Control flow: `Get` checks closed state, applies options, returns memory cache hits, fd cache hits, or opens the cache file. In direct mode it avoids memory/fd caching and optionally drops page cache on close. `Add` writes to a WIP temp file. In normal mode it first writes to a pooled memory buffer, adds that buffer to LRU, then commits to disk synchronously or in a goroutine. Commit creates the final key directory and renames the WIP file.

State and persistence: Directory cache persists files under `<dir>/<first-two-key-bytes>/<key>` and WIP files under `<dir>/wip`; close removes the entire directory. Memory cache stores buffers in a mutex-protected map.

Dependencies and integration: Uses `cacheutil.LRUCache`, `namedmutex`, filesystem operations, and `unix.Fadvise`.

Risks: Asynchronous disk commit can make a memory-hit visible before the disk file exists. Duplicate adds may reuse existing memory cache data. `cachePath` assumes key length >= 2. `PassThrough` is only an option bit here; behavior depends on callers using `GetReaderAt`.

Test signals: `cache_test.go` covers directory and memory caches, hits, misses, duplicate adds, partial `ReadAt`, and LRU eviction behavior.
<!-- END_FILE_RESEARCH: sources/cloud-native/stargz-snapshotter/cache/cache.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/stargz-snapshotter/cache/cache_test.go -->
# sources/cloud-native/stargz-snapshotter/cache/cache_test.go

Purpose: Tests the `BlobCache` contract for directory-backed and memory-backed caches.

Important APIs tested: `NewDirectoryCache`, `NewMemoryCache`, `BlobCache.Add`, `Writer.Commit`, `BlobCache.Get`, and `Reader.ReadAt`.

Control flow: `TestDirectoryCache` runs the shared suite twice: once with enough memory LRU entries and once with a one-entry memory LRU to force disk fallback. `TestMemoryCache` runs the same suite against the in-memory implementation. `testCache` adds blobs by SHA-256 key, commits them, and runs hit or miss checks. `hit` validates whole-blob and partial reads. `miss` expects `Get` to fail for absent keys.

State and persistence: Directory tests create and clean temporary cache directories. `SyncAdd` is true so disk commit completion is deterministic during tests.

Dependencies and integration: Uses only package-level cache APIs plus SHA-256 helpers; this is a black-box style contract test.

Risks covered: Empty payloads, duplicate writes, multiple blobs, partial `ReadAt`, and memory cache eviction are covered. The tests do not cover direct mode, pass-through mode, async commit, close behavior, `FadvDontNeed`, key length assumptions, or concurrent accesses.

Test signals: Good baseline confidence for the cache interface, especially that directory cache still works after memory LRU eviction.
<!-- END_FILE_RESEARCH: sources/cloud-native/stargz-snapshotter/cache/cache_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/stargz-snapshotter/cmd/containerd-stargz-grpc/db/db.go -->
# sources/cloud-native/stargz-snapshotter/cmd/containerd-stargz-grpc/db/db.go

Purpose: Defines the bbolt schema and low-level encode/decode helpers for the persistent metadata reader used by the snapshotter and store.

Important APIs/types: Bucket key variables, `childEntry`, `chunkEntry`, `metadataEntry`, bucket accessors (`getNodes`, `getMetadata`, `getStream`), attribute helpers (`writeAttr`, `readAttr`), child/chunk helpers (`readChild`, `readChunks`, `readInnerChunks`, `writeMetadataEntry`), and binary encoders.

Control flow: Metadata is stored under `filesystems/<fsID>` with `nodes`, `metadata`, and `stream` buckets. Node buckets hold attributes. Metadata buckets hold first child/chunk inline and overflow entries in sub-buckets to avoid bucket creation for common single-entry cases. Stream buckets map compressed stream offsets to node ids when multiple chunks share a compressed stream.

State and persistence: Persists filesystem metadata in bbolt. Integers use varint/uvarint except ids and chunk entries, which use big-endian fixed fields for ordered keys and compact chunk payloads.

Dependencies and integration: Used heavily by `reader.go`; depends on `metadata.Attr` and bbolt.

Risks: `decodeID` assumes at least four bytes; corrupted DB data can panic or decode incorrectly. `readAttr` stores byte slices directly from bbolt values; callers should treat them as transaction-scoped. Map iteration chooses arbitrary first child/xattr, which is acceptable for storage but non-deterministic internally.

Test signals: Covered indirectly by `reader_test.go` through metadata reader, filesystem reader, and layer suites.
<!-- END_FILE_RESEARCH: sources/cloud-native/stargz-snapshotter/cmd/containerd-stargz-grpc/db/db.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/stargz-snapshotter/cmd/containerd-stargz-grpc/db/reader.go -->
# sources/cloud-native/stargz-snapshotter/cmd/containerd-stargz-grpc/db/reader.go

Purpose: Implements `metadata.Reader` backed by bbolt. It parses eStargz/zstd metadata once into buckets, then serves filesystem metadata and random file reads.

Important APIs: `NewReader`, `RootID`, `TOCDigest`, `Clone`, `Close`, `GetOffset`, `GetAttr`, `GetChild`, `ForeachChild`, `OpenFile`, `OpenFileWithPreReader`, `NumOfNodes`, and `NumOfChunks`.

Control flow: `NewReader` applies metadata options, tries gzip and configured decompressors, reads the footer, parses/decompresses TOC, creates a reader, and calls `init`. `init` creates a unique filesystem id and root node, copies the decompressed TOC to a temp file while computing TOC digest, then launches background node initialization. Most methods call `waitInit` before viewing bbolt. `initNodes` streams TOC JSON entries, creates or reuses nodes, resolves hardlinks, creates implicit directories, records chunks and stream relationships, then writes sorted metadata and stream addenda.

State and persistence: Persists each reader's metadata under a random `fsID` in shared bbolt. `Close` deletes that filesystem bucket. Runtime state includes section reader, root id, TOC digest, decompressor, and init errgroup.

Dependencies and integration: Implements the DB metadata store selected by `fsopts` and `stargz-store`. Depends on eStargz TOC types, metadata interfaces, bbolt, and `go-json`.

Risks: Initialization has no timeout. Read methods block on background init. Corrupt TOC/DB can surface late. `ReadAt` decompresses from compressed stream offsets and may read up to the next offset, which is correct but potentially costly.

Test signals: `reader_test.go` runs shared metadata, fs reader, and layer suites against this implementation.
<!-- END_FILE_RESEARCH: sources/cloud-native/stargz-snapshotter/cmd/containerd-stargz-grpc/db/reader.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/stargz-snapshotter/cmd/containerd-stargz-grpc/db/reader_test.go -->
# sources/cloud-native/stargz-snapshotter/cmd/containerd-stargz-grpc/db/reader_test.go

Purpose: Adapts broad metadata and filesystem conformance suites to the bbolt-backed metadata reader.

Important APIs tested: `NewReader`, `reader` as `testutil.TestableReader`, and the `metadata.Reader` interface through fs reader and layer suites.

Control flow: Each test constructs a runner that bridges custom testing interfaces to `*testing.T`. `newTestableReader` and `newStore` create a temp bbolt database, open it, instantiate `NewReader`, and wrap close behavior so the DB file is removed. `TestReader` invokes metadata testutil, `TestFSReader` invokes fs reader suite, and `TestFSLayer` invokes layer suite.

State and persistence: Temporary bbolt files hold metadata during each reader. Wrappers close the DB and remove the file.

Dependencies and integration: Integrates the DB metadata backend with shared packages `metadata/testutil`, `fs/reader`, and `fs/layer`.

Risks covered: Broad behavior such as lookup, attributes, file reads, chunk handling, and layer semantics are likely covered by the imported suites. The test file itself does not enumerate cases, so changes in upstream shared suites affect coverage. It does not test long-lived shared DB accumulation or concurrent readers beyond what the suites exercise.

Test signals: High-value integration coverage because the same suites can compare DB behavior against other metadata stores.
<!-- END_FILE_RESEARCH: sources/cloud-native/stargz-snapshotter/cmd/containerd-stargz-grpc/db/reader_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/stargz-snapshotter/cmd/containerd-stargz-grpc/fsopts/fsopts.go -->
# sources/cloud-native/stargz-snapshotter/cmd/containerd-stargz-grpc/fsopts/fsopts.go

Purpose: Builds filesystem options for the snapshotter daemon and FUSE manager from runtime configuration.

Important APIs: `Config`, `ConfigFsOpts`, and `getMetadataStore`. Config fields enable IPFS, choose metadata store type, and inject a bbolt opener.

Control flow: `ConfigFsOpts` starts with metrics log level, optionally registers an IPFS resolve handler for the `ipfs` scheme, resolves a metadata store, and returns `fs.Option` values. `getMetadataStore` returns the in-memory metadata reader by default or constructs a DB-backed store that reuses a bbolt DB at `<rootDir>/metadata.db`.

State and persistence: No state retained here. DB mode persists metadata in the configured root directory via the supplied `OpenBoltDB`.

Dependencies and integration: Used by `containerd-stargz-grpc/main.go` and `stargz-fuse-manager/main.go`. Connects `fs`, `metadata/memory`, `cmd/.../db`, bbolt, and IPFS resolver integration.

Risks: DB mode requires `OpenBoltDB`; missing opener is a configuration error. Unknown metadata store values are rejected. The function does not close the opened DB; lifecycle is owned by process-level service code.

Test signals: No direct test in this subset; behavior is exercised through daemon configuration/integration.
<!-- END_FILE_RESEARCH: sources/cloud-native/stargz-snapshotter/cmd/containerd-stargz-grpc/fsopts/fsopts.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/stargz-snapshotter/cmd/containerd-stargz-grpc/ipfs/resolvehandler.go -->
# sources/cloud-native/stargz-snapshotter/cmd/containerd-stargz-grpc/ipfs/resolvehandler.go

Purpose: Implements an `fs/remote` resolve handler that turns IPFS descriptors into fetchers for lazy layer reads.

Important APIs/types: `ResolveHandler.Handle`, `fetcher.Fetch`, `fetcher.Check`, and `fetcher.GenID`. `Handle` extracts a CID from the OCI descriptor, discovers the local IPFS HTTP API address, stats the CID for size, and returns a range-capable fetcher.

Control flow: `Fetch` validates offset against known blob size, converts offset and size to `int`, and calls the IPFS client `Get("/ipfs/"+cid, &off, &size)`. `Check` repeats `StatCID`. `GenID` produces a SHA-256 key from CID, offset, and size.

State and persistence: Holds CID, size, and IPFS client in memory. No local persistence.

Dependencies and integration: Registered by `fsopts.ConfigFsOpts` when IPFS is enabled. Depends on IPFS descriptor helpers, IPFS client configuration, environment variable `IPFS_PATH`, and `remote.Fetcher`.

Risks: Only HTTP is supported. Offset/size conversion from int64 to int can overflow on 32-bit platforms or huge ranges. Fetch accepts `off == size`, which likely returns EOF/empty from IPFS. CID stat failures prevent lazy resolution.

Test signals: No direct tests in this subset; requires IPFS daemon or mocked client for coverage.
<!-- END_FILE_RESEARCH: sources/cloud-native/stargz-snapshotter/cmd/containerd-stargz-grpc/ipfs/resolvehandler.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/stargz-snapshotter/cmd/containerd-stargz-grpc/main.go -->
# sources/cloud-native/stargz-snapshotter/cmd/containerd-stargz-grpc/main.go

Purpose: Main daemon for the containerd stargz snapshotter gRPC service. It loads config, configures filesystem/keychain/FUSE manager modes, serves snapshotter APIs, metrics, debug endpoints, and systemd notifications.

Important APIs/types: `snapshotterConfig`, `FuseManagerConfig`, `main`, and `serve`. Flags configure address, config path, log level, root, and version.

Control flow: `main` parses flags, configures logging, loads TOML, validates support, creates a gRPC server, forces direct mode when passthrough is enabled, configures keychains, then branches between detached FUSE manager mode and in-process service mode. In FUSE manager mode it starts or connects to manager and creates a snapshotter with restoration behavior based on whether the manager was newly started. Otherwise it configures CRI keychain socket if needed, filesystem options, and `service.NewStargzSnapshotterService`.

State and persistence: Uses root directories for snapshotter data, optional FUSE manager DB/log, and optional metadata DB. Removes listening sockets before binding.

Dependencies and integration: Integrates containerd snapshot service, stargz service, keychains, fsopts, fusemanager, bbolt, metrics, debug server, systemd notify, and Unix signals.

Risks: Many fatal configuration paths terminate the process. Cleanup semantics differ on SIGINT/SIGTERM and FUSE manager mode. Socket removal can remove stale or unexpected filesystem entries at configured paths.

Test signals: No direct tests; daemon-level integration tests would be needed.
<!-- END_FILE_RESEARCH: sources/cloud-native/stargz-snapshotter/cmd/containerd-stargz-grpc/main.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/stargz-snapshotter/cmd/containerd-stargz-grpc/server.go -->
# sources/cloud-native/stargz-snapshotter/cmd/containerd-stargz-grpc/server.go

Purpose: Provides the debug HTTP mux for the snapshotter daemon.

Important API: `debugServerMux` returns a new `http.ServeMux` with expvar and pprof handlers registered at `/debug/vars`, `/debug/pprof/`, `/debug/pprof/cmdline`, `/debug/pprof/profile`, `/debug/pprof/symbol`, and `/debug/pprof/trace`.

Control flow: The mux is constructed on demand and passed to `http.Serve` from `main.go` when `DebugAddress` is configured.

State and persistence: No persistent state. Handlers expose process runtime state from expvar and pprof.

Dependencies and integration: Uses standard library `expvar`, `net/http`, and `net/http/pprof`. Integrated by the daemon's debug listener on a local socket.

Risks: Debug endpoints expose profiling and process details; binding should remain restricted to the configured local/debug socket. No authentication is added here.

Test signals: No direct tests; behavior is simple standard library wiring.
<!-- END_FILE_RESEARCH: sources/cloud-native/stargz-snapshotter/cmd/containerd-stargz-grpc/server.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/stargz-snapshotter/cmd/ctr-remote/commands/convert.go -->
# sources/cloud-native/stargz-snapshotter/cmd/ctr-remote/commands/convert.go

Purpose: Defines `ctr-remote images convert`, a containerd image conversion command for eStargz, external TOC eStargz, zstd:chunked, uncompressed layers, and OCI media conversion.

Important APIs: `ConvertCommand`, `getESGZConvertOpts`, `getZstdchunkedConvertOpts`, and `readPathsFromRecordFile`. Flags control conversion type, compression/chunking, record-in prioritization, external TOC, keep-diff-id mode, gzip helper, and platform selection.

Control flow: The action validates source/target refs, selects platform matcher, builds a layer convert function based on mutually exclusive flags, optionally enables Docker-to-OCI conversion, opens a containerd client and lease, handles interrupts by cancelling context, runs `converter.Convert`, performs external TOC finalization if needed, and prints resulting digest and extra image name.

State and persistence: Writes converted image content and image records into containerd's content/image stores. Reads optional record JSON from the filesystem.

Dependencies and integration: Uses containerd converter APIs, native converter packages, eStargz options, zstd, recorder entries, and gzip helper utilities.

Risks: Some invalid flag combinations are caught explicitly. `readPathsFromRecordFile` streams JSON entries with `dec.More()` at top level, relying on recorder output format. External TOC creates an additional image and deletes any existing image by that name.

Test signals: No direct tests in this subset; conversion behavior is likely covered in converter package tests elsewhere.
<!-- END_FILE_RESEARCH: sources/cloud-native/stargz-snapshotter/cmd/ctr-remote/commands/convert.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/stargz-snapshotter/cmd/ctr-remote/commands/flags.go -->
# sources/cloud-native/stargz-snapshotter/cmd/ctr-remote/commands/flags.go

Purpose: Defines sampler/container runtime flags and converts CLI input into OCI spec options used by `optimize` analysis containers.

Important APIs: `samplerFlags`, `parseGPUs`, `getSpecOpts`, `withEntrypointArgs`, `withCNI`, `withResolveConfig`, `parseMountFlag`, `parseResolveFlag`, and `withStaticCDIRegistry`.

Control flow: `getSpecOpts` builds cleanup-aware OCI spec options: default spec/devices/rootfs/image/env/mounts, DNS/hosts bind mounts, optional env file/user/cwd/TTY, optional CNI network namespace setup, host networking, and GPU CDI device injection. `withEntrypointArgs` loads image config and overrides entrypoint/cmd from JSON flags. `withResolveConfig` creates temporary resolv.conf and hosts files. `withCNI` creates a netns, configures CNI, and returns cleanup that removes network and namespace.

State and persistence: Uses temporary directories for DNS/hosts files and netns mounts under `/var/run/netns`; cleanup callbacks remove them. CDI registry state is refreshed globally with auto-refresh disabled.

Dependencies and integration: Used by `optimize.go` via `analyzer.WithSpecOpts`. Integrates containerd OCI helpers, go-cni, netns, runtime-spec, CDI, and image config blobs.

Risks: Cleanup errors are aggregated but an error-wrapping bug can lose the cleanup error detail. Mount parsing is simple key/value CSV and rejects unknown keys. GPU parser ignores non-numeric non-`all` entries.

Test signals: No direct tests in this subset; flag parsing and cleanup deserve focused tests.
<!-- END_FILE_RESEARCH: sources/cloud-native/stargz-snapshotter/cmd/ctr-remote/commands/flags.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/stargz-snapshotter/cmd/ctr-remote/commands/get-toc-digest.go -->
# sources/cloud-native/stargz-snapshotter/cmd/ctr-remote/commands/get-toc-digest.go

Purpose: Defines `ctr-remote images get-toc-digest`, a debugging utility that reads a layer from containerd content store and prints its TOC digest or formatted TOC.

Important API: `GetTOCDigestCommand`. Flags select zstd:chunked parsing and optional `--dump-toc`.

Control flow: The action validates a layer digest argument, creates a containerd client, opens the content blob as `ReaderAt`, reads the appropriate footer size, selects gzip or zstd:chunked decompressor, parses footer to locate TOC, defaults TOC size when omitted, parses TOC from a section reader, then prints either marshaled indented TOC JSON or digest string.

State and persistence: Read-only against the containerd content store. No local writes.

Dependencies and integration: Uses eStargz and zstdchunked decompressors, OpenContainers digest parsing, and containerd ctr client setup.

Risks: Assumes footer read starts at `ra.Size()-footerSize`; too-small blobs cause read errors. Dumped TOC is re-marshaled and may not match original digest, as documented in flag text.

Test signals: No direct tests in this subset; coverage would need sample gzip and zstd chunked layers.
<!-- END_FILE_RESEARCH: sources/cloud-native/stargz-snapshotter/cmd/ctr-remote/commands/get-toc-digest.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/stargz-snapshotter/cmd/ctr-remote/commands/ipfs-push.go -->
# sources/cloud-native/stargz-snapshotter/cmd/ctr-remote/commands/ipfs-push.go

Purpose: Defines experimental `ctr-remote images ipfs-push`, which optionally converts image layers to eStargz and pushes image content to IPFS.

Important API: `IPFSPushCommand`. Flags select platforms/all-platforms and enable eStargz conversion, defaulting to true.

Control flow: The action validates an image ref, computes the platform matcher, opens a containerd client, chooses an eStargz layer converter if requested, calls `ipfs.Push`, logs the returned CID, and prints it.

State and persistence: Reads image/content from containerd and writes to IPFS through the IPFS package. The command itself maintains no persistent local state.

Dependencies and integration: Uses containerd client/commands, converter types, platform matching, native eStargz converter, and stargz-snapshotter IPFS package.

Risks: Experimental path. Platform selection must match available image manifests. Default eStargz conversion changes layer format unless disabled. IPFS daemon/network errors propagate directly.

Test signals: No direct tests in this subset; likely requires mocked IPFS or integration environment.
<!-- END_FILE_RESEARCH: sources/cloud-native/stargz-snapshotter/cmd/ctr-remote/commands/ipfs-push.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/stargz-snapshotter/cmd/ctr-remote/commands/notify.go -->
# sources/cloud-native/stargz-snapshotter/cmd/ctr-remote/commands/notify.go

Purpose: Defines hidden `ctr-remote fanotify`, the helper process invoked by analyzer fanotify code.

Important API: `FanotifyCommand`. It is hidden from normal CLI help and expects one target path argument.

Control flow: The action reads the target argument, errors if absent, and calls `service.Serve(target, os.Stdin, os.Stdout)`. That service performs the fanotify protocol and event streaming.

State and persistence: No state in this command file; service-side fanotify state is managed in `analyzer/fanotify/service`.

Dependencies and integration: Integrated with `SpawnFanotifier`, which launches the ctr-remote binary with `fanotify /` in a separate mount namespace and communicates over stdio.

Risks: Requires stdin/stdout to be reserved for the protocol. Any logging to stdout from the helper would corrupt protocol messages; service warnings go to stderr.

Test signals: No direct tests. Integration requires privileged fanotify execution.
<!-- END_FILE_RESEARCH: sources/cloud-native/stargz-snapshotter/cmd/ctr-remote/commands/notify.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/stargz-snapshotter/cmd/ctr-remote/commands/optimize.go -->
# sources/cloud-native/stargz-snapshotter/cmd/ctr-remote/commands/optimize.go

Purpose: Defines `ctr-remote images optimize`, which analyzes a workload or prefetch list, records accessed files, and converts the image with per-layer prioritized files for lazy pulling.

Important APIs: `OptimizeCommand`, `writeContentFile`, `readPrefetchList`, `buildLayerOptsFromRecord`, `analyzePrefetchList`, `analyze`, `isReusableESGZLayer`, `excludeWrapper`, and `logWrapper`.

Control flow: The command validates refs and flags, selects platforms, opens a containerd client/lease, runs `analyze`, optionally writes the record content to a file, builds an eStargz or zstd:chunked converter with per-layer options, wraps conversion for reuse/logging, handles interrupts, runs `converter.Convert`, performs external TOC finalization if configured, and prints digests. `analyze` can skip optimization, consume `--prefetch-list`, or run a sampled container through `analyzer.Analyze`. Prefetch-list paths can be exact or glob patterns matched by doublestar.

State and persistence: Reads/writes containerd content and images. Records are content blobs and optionally filesystem files. Conversion may create an extra TOC image.

Dependencies and integration: Central integration point for analyzer, recorder, native converters, containerd converter APIs, platform helpers, gzip helpers, and zstd.

Risks: Reuse is digest-keyed with a TODO noting layer index would be better. `RecordGlob` misses are logged but not fatal. External TOC and reuse are disallowed together. Analysis only runs for default platform unless all-platforms or matching platform flags allow it.

Test signals: No direct tests in this subset; multiple branches need CLI/integration coverage.
<!-- END_FILE_RESEARCH: sources/cloud-native/stargz-snapshotter/cmd/ctr-remote/commands/optimize.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/stargz-snapshotter/cmd/ctr-remote/commands/rpull.go -->
# sources/cloud-native/stargz-snapshotter/cmd/ctr-remote/commands/rpull.go

Purpose: Defines `ctr-remote images rpull`, a remote/lazy pull command that fetches and unpacks an image using the stargz snapshotter.

Important APIs/types: `RpullCommand`, `rPullConfig`, and `pull`. Flags include registry flags, labels, snapshotter selection, `--skip-content-verify`, `--ipfs`, and `--use-containerd-labels`.

Control flow: The action validates ref, opens a containerd client and lease, builds a fetch config, configures optional verification skip, optional IPFS resolver, and snapshotter name, then calls `pull`. `pull` creates a lightweight handler for fetch logging, sets snapshot labels for skip verification, chooses default or containerd label handler wrappers with prefetch size 10 MiB, and calls `client.Pull` with resolver, labels, unpack, snapshotter, and image handler wrapper.

State and persistence: Pulls image content into containerd content store and prepares snapshots with selected snapshotter. May attach labels affecting stargz snapshotter behavior.

Dependencies and integration: Uses containerd pull APIs, snapshot labels from fs config/source packages, optional IPFS resolver, and containerd snapshotter flags.

Risks: `--skip-content-verify` weakens integrity and logs a warning. Prefetch size is hard-coded. IPFS resolver path is experimental. Incorrect snapshotter name causes pull/unpack failures.

Test signals: No direct tests in this subset; integration with containerd is required.
<!-- END_FILE_RESEARCH: sources/cloud-native/stargz-snapshotter/cmd/ctr-remote/commands/rpull.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/stargz-snapshotter/cmd/ctr-remote/main.go -->
# sources/cloud-native/stargz-snapshotter/cmd/ctr-remote/main.go

Purpose: Builds the `ctr-remote` CLI by extending containerd's standard `ctr` app with stargz-specific image commands and the hidden fanotify command.

Important API: `main`.

Control flow: It creates the base `ctr` app, prepares custom commands (`rpull`, `optimize`, `convert`, `get-toc-digest`, `ipfs-push`), finds the `images` command, replaces any subcommands with matching names, appends missing custom subcommands, then appends the hidden top-level `FanotifyCommand`. It runs the CLI with `os.Args` and prints failures to stderr before exiting nonzero.

State and persistence: No persistent state; this is command registration and process exit handling.

Dependencies and integration: Imports containerd's `ctr/app`, urfave cli, and the local commands package. The hidden fanotify command is intentionally top-level so `SpawnFanotifier` can call `ctr-remote fanotify /`.

Risks: If containerd's app command shape changes and the `images` command is absent or renamed, custom image commands will not be inserted, but fanotify still appends. Map iteration means appended custom subcommand order is not deterministic for commands not replacing existing names.

Test signals: No direct tests; simple CLI assembly.
<!-- END_FILE_RESEARCH: sources/cloud-native/stargz-snapshotter/cmd/ctr-remote/main.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/stargz-snapshotter/cmd/stargz-fuse-manager/main.go -->
# sources/cloud-native/stargz-snapshotter/cmd/stargz-fuse-manager/main.go

Purpose: Entrypoint for the detached FUSE manager process used by the snapshotter daemon.

Important APIs: `init` registers two fusemanager configuration functions, and `main` calls `fusemanager.Run`.

Control flow: The first config function derives filesystem options from the manager config using `fsopts.ConfigFsOpts` and returns `service.WithFilesystemOptions`. The second config function builds keychain configuration, enforces that CRI keychain listen path is separated from the FUSE manager server when needed, optionally creates a dedicated CRI gRPC server/socket, configures credential functions, serves the CRI socket, and returns `service.WithCredsFuncs`.

State and persistence: Removes and binds Unix sockets for CRI keychain when configured. Metadata persistence is delegated to fsopts and bbolt opener from manager context.

Dependencies and integration: Integrates fusemanager, service options, keychainconfig, fsopts, gRPC, and Unix sockets. This mirrors parts of daemon in-process setup for detached manager mode.

Risks: Boolean precedence in the CRI listen-path validation relies on Go `&&` before `||`; it rejects empty listen path when keychain is enabled and any listen path equal to manager address. Socket removal can remove stale paths.

Test signals: No direct tests; behavior is configuration/integration heavy.
<!-- END_FILE_RESEARCH: sources/cloud-native/stargz-snapshotter/cmd/stargz-fuse-manager/main.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/stargz-snapshotter/cmd/stargz-store/helper/main.go -->
# sources/cloud-native/stargz-snapshotter/cmd/stargz-store/helper/main.go

Purpose: Small helper binary that reads credential JSON from stdin and sends it to a running `stargz-store` controller socket.

Important API: `main`.

Control flow: It chooses the Unix socket address from argv or defaults to `/var/lib/stargz-store/store.sock`, reads all stdin, builds a gRPC client using containerd's Unix dialer, insecure local credentials, backoff configuration, and containerd default message sizes, then calls `Controller.AddCredential`.

State and persistence: No local persistence. It transmits credential data to the store daemon, which merges it into an in-memory keychain.

Dependencies and integration: Uses containerd defaults/dialer and generated store protobuf client.

Risks: Uses `panic` for all errors, appropriate for a helper but rough for UX. Reads all stdin into memory. Does not close the gRPC connection explicitly. Credentials are passed over a local Unix socket without extra authentication.

Test signals: No direct tests.
<!-- END_FILE_RESEARCH: sources/cloud-native/stargz-snapshotter/cmd/stargz-store/helper/main.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/stargz-snapshotter/cmd/stargz-store/main.go -->
# sources/cloud-native/stargz-snapshotter/cmd/stargz-store/main.go

Purpose: Main daemon for `stargz-store`, a FUSE-backed store that mounts lazy-pulled layers and exposes a controller socket for dynamic credentials.

Important APIs/types: `Config`, `KubeconfigKeychainConfig`, `ResolverConfig`, `main`, `waitForSignal`, `getMetadataStore`, `controller.AddCredential`, `storeKeychain.add`, `storeKeychain.credentials`, and `serveController`.

Control flow: `main` parses flags, requires a mount point, configures logging and TOML config, starts the credential controller, builds credential functions from in-memory store keychain and optional kubeconfig keychain, creates registry hosts, prepares mountpoint, rejects disabled verification, configures metadata store, creates `store.LayerManager`, mounts FUSE store, sends systemd ready/stopping notifications, and waits for interrupt or controller error. `serveController` removes the socket path, starts a gRPC server, and returns an error channel.

State and persistence: Root dir holds optional metadata DB and store data through `store.NewLayerManager`. Credentials are held in memory keyed by image reference. The mounted filesystem is unmounted on exit.

Dependencies and integration: Integrates resolver config, kubeconfig keychain, metadata memory/DB stores, store package, protobuf controller, bbolt, gRPC, systemd notify, and Unix mount lifecycle.

Risks: `serveController` removes socket path without ensuring parent directory exists. Content verification cannot be disabled. Credentials are only applied when host matches the original ref hostname, avoiding mirrors. `waitForSignal` only listens for `os.Interrupt`, not SIGTERM.

Test signals: No direct tests in this subset.
<!-- END_FILE_RESEARCH: sources/cloud-native/stargz-snapshotter/cmd/stargz-store/main.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/stargz-snapshotter/estargz/build.go -->
# sources/cloud-native/stargz-snapshotter/estargz/build.go

Purpose: Builds optimized eStargz blobs from tar, gzip tar, or zstd tar input, with optional prioritized file ordering, chunk sizing, compression selection, context cancellation, and gzip helper decompression.

Important APIs/types: `GzipHelperFunc`, build `Option`s, `Blob`, `Build`, `closeWithCombine`, `sortEntries`, `importTar`, `moveRec`, `tarFile`, temp file helpers, `countReadSeeker`, and `decompressBlob`.

Control flow: `Build` applies options, selects compression, tracks temp files, handles context cleanup, decompresses input if needed, sorts entries with prefetch/no-prefetch landmarks, partitions entries across `GOMAXPROCS` unless `MinChunkSize` requires serial processing, writes sub-blobs in goroutines, combines TOCs with adjusted offsets, then streams payloads plus TOC/footer through an `io.Pipe` while computing diff ID and uncompressed size. `sortEntries` imports tar entries, moves prioritized paths and their parents/hardlink targets first, inserts a landmark, and appends the rest.

State and persistence: Uses temporary files for decompressed input and sub-blob payloads, removed on blob close or error. `Blob` tracks TOC digest, diffID, read-completion, and uncompressed size atomically.

Dependencies and integration: Core library used by native converters and command conversion paths. Depends on tar/gzip/zstd, digest, and writer implementation in `estargz.go`.

Risks: Callers must fully read before `UncompressedSize`. Parallel build uses temp disk proportional to layer size. Missing prioritized files are fatal unless explicitly allowed.

Test signals: `build_test.go` heavily tests sorting, landmarks, path normalization, hardlinks, duplicate entries, and count reader behavior.
<!-- END_FILE_RESEARCH: sources/cloud-native/stargz-snapshotter/estargz/build.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/stargz-snapshotter/estargz/build_test.go -->
# sources/cloud-native/stargz-snapshotter/estargz/build_test.go

Purpose: Tests eStargz build-time tar reordering and the count read seeker helper.

Important APIs tested: `Build`, `WithPrioritizedFiles`, `WithAllowPrioritizeNotFound`, `sortEntries` behavior through decompressed output, landmark handling, and `newCountReadSeeker`.

Control flow: `TestSort` defines many tar layouts and prioritized logs, runs each case across source compression modes plus log/tar path prefixes, builds an eStargz, decompresses it with gzip, skips TOC entries, and compares tar headers and payloads against expected order. It also verifies allowed missing file reporting. `TestCountReader` performs read and seek operation sequences and checks the tracked current position.

State and persistence: Uses in-memory tar construction and streamed build outputs. No durable state.

Dependencies and integration: Uses helper functions from estargz test utilities, gzip, tar, reflect, and bytes.

Risks covered: No-log no-prefetch landmark insertion, prioritized landmark insertion, directory-parent movement, hardlink target movement, symlink/device/fifo handling, long names, existing landmark removal, missing prioritized files, duplicate entries, and root-relative/absolute names.

Test signals: Strong coverage for ordering semantics. It does not directly validate parallel partition offset recombination, diffID/uncompressed size finalization, or gzip helper execution.
<!-- END_FILE_RESEARCH: sources/cloud-native/stargz-snapshotter/estargz/build_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/stargz-snapshotter/estargz/errorutil/errors.go -->
# sources/cloud-native/stargz-snapshotter/estargz/errorutil/errors.go

Purpose: Provides a deprecated error aggregation helper retained for compatibility.

Important API: `Aggregate(errs []error) error`. It returns nil for an empty slice, the sole error unchanged for one entry, or a new formatted error listing all messages for multiple entries.

Control flow: Uses a switch on slice length. The multiple-error case builds a string slice with header `N error(s) occurred:` and bullet lines prefixed with tab plus `*`, then returns `errors.New(strings.Join(...))`.

State and persistence: Stateless, no I/O.

Dependencies and integration: Uses standard `errors`, `fmt`, and `strings`. The comment marks it deprecated in favor of `errors.Join` and scheduled for removal in v0.19.0.

Risks: Unlike `errors.Join`, the returned aggregate does not preserve `errors.Is`/`errors.As` behavior for individual errors. Formatting is part of existing test expectations, so changing it can break consumers.

Test signals: `errors_test.go` covers nil/empty, single-error identity, and exact multi-error formatting.
<!-- END_FILE_RESEARCH: sources/cloud-native/stargz-snapshotter/estargz/errorutil/errors.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/stargz-snapshotter/estargz/errorutil/errors_test.go -->
# sources/cloud-native/stargz-snapshotter/estargz/errorutil/errors_test.go

Purpose: Verifies legacy behavior of the deprecated `errorutil.Aggregate` helper.

Important APIs tested: `Aggregate`.

Control flow: `TestNoError` expects nil for nil and empty slices. `TestOneError` expects the exact same error object to be returned for a single input. `TestMultipleErrors` expects a non-nil error whose string exactly matches the historical multi-line format.

State and persistence: No state or I/O.

Dependencies and integration: Uses standard `errors` and `testing`.

Risks covered: Protects compatibility-sensitive formatting and object identity. Since the helper is deprecated, these tests mainly prevent accidental behavior drift before removal.

Test signals: Complete for the tiny helper's current branching logic. Does not test nil elements inside a non-empty slice.
<!-- END_FILE_RESEARCH: sources/cloud-native/stargz-snapshotter/estargz/errorutil/errors_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/stargz-snapshotter/estargz/estargz.go -->
# sources/cloud-native/stargz-snapshotter/estargz/estargz.go

Purpose: Core eStargz reader/writer implementation. It opens stargz blobs for random access, verifies TOC/chunk digests, reads file chunks lazily, writes stargz streams, and appends TOC/footer metadata.

Important APIs/types: `Reader`, open options (`WithTOCOffset`, `WithDecompressors`, `WithTelemetry`), `Open`, `OpenFooter`, `TOCDigest`, `VerifyTOC`, `Verifiers`, `ChunkEntryForOffset`, `Lookup`, `OpenFile`, `OpenFileWithPreReader`, `Writer`, `Unpack`, `NewWriter`, `NewWriterLevel`, `NewWriterWithCompressor`, `Writer.Close`, `AppendTar`, `AppendTarLossLess`, and `DiffID`.

Control flow: `Open` selects decompressor candidates, reads the largest footer needed, parses footer/TOC, initializes maps and chunk lists, resolves hardlinks, creates implicit directories, fills uname/gname/modtime/link counts, and computes next offsets. File reads choose the chunk for the requested offset, open a section of compressed data, decompress from the chunk stream, discard to inner/file offset, and optionally pre-read sibling chunks that share a compressed stream. `Writer.appendTar` reads tar or gzip tar, records TOC entries, chunks regular files, computes regular and chunk digests, manages gzip stream boundaries based on chunk and min-chunk rules, and writes TOC/footer on close.

State and persistence: Reader holds the source section reader, TOC, digest, path maps, chunk index, and decompressor. Writer holds buffered/counting writers, compressor, TOC, diff hash, gzip stream, username/group caches, chunk settings, and uncompressed counters.

Dependencies and integration: Used by metadata readers, converters, TOC digest command, and build logic. Depends on compressor/decompressor interfaces from `types.go` and gzip implementations.

Risks: Random reads require decompressing from compressed chunk offsets and can be expensive. `VerifyTOC` requires complete chunk digests unless fallback to regular file digests is safe. Lossless append rejects existing TOC entries. Path normalization collapses absolute/root-relative names.

Test signals: Many tests exist elsewhere; this subset includes build tests, while symbol scan shows dedicated `estargz_test.go` and gzip tests outside this work item.
<!-- END_FILE_RESEARCH: sources/cloud-native/stargz-snapshotter/estargz/estargz.go -->
