# subset-b-009602 Research

This grouped report covers the requested gcsfuse tracing files and go-fuse CI, benchmark, example, and fs package files. Each section preserves the source path for deterministic splitting into source-tree-aligned per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/tracing/span_names.go -->
# sources/user-network-fs/gcsfuse/tracing/span_names.go

Purpose: defines the canonical OpenTelemetry span-name vocabulary for gcsfuse FUSE, cache, prefetch, metadata, xattr, and write/upload flows. The file has no runtime control flow; its value is the shared contract between instrumentation call sites and trace consumers.

Important APIs/types/functions: exported string constants such as `FileCacheRead`, `LookUpInode`, `ReadDirPlus`, `CreateFile`, `WriteFileStreaming`, and `StreamingUploadFinalize`. Constants are grouped by operation class and are intended to be passed into the tracing handle in `trace_handle.go` and concrete tracers elsewhere in the package.

State/persistence: immutable compile-time constants only. No persistence or mutable state.

Dependencies/integration: package `tracing`; integrates with OpenTelemetry spans indirectly through `TraceHandle`. Risks are mostly naming drift, cardinality changes, and observability compatibility if callers hard-code names or dashboards depend on these exact strings. Test signals should come from tracing tests that assert emitted span names or from static usage searches that ensure each canonical operation uses a constant.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/tracing/span_names.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/tracing/trace_handle.go -->
# sources/user-network-fs/gcsfuse/tracing/trace_handle.go

Purpose: declares the tracing abstraction used by gcsfuse to record spans without coupling call sites to a specific OpenTelemetry implementation. It also defines the instrumentation library name constant `name = "cloud.google.com/gcsfuse"`.

Important APIs/types/functions: `TraceHandle` includes span lifecycle methods (`StartSpan`, `StartServerSpan`, `EndSpan`, `RecordError`), optimized attribute setters (`SetCacheReadAttributes`, `SetUploadAttributes`), `TraceUpload` for deferred upload finalization, and `PropagateTraceContext`. The comments explain an allocation-sensitive API choice: callers pass primitive values so a noop tracer can avoid attribute construction.

Control flow/state: this file is pure interface definition. Concrete behavior is supplied by noop or OTEL implementations.

Dependencies/integration: depends on `context` and `go.opentelemetry.io/otel/trace`. Risks include interface churn affecting all tracers, nil span handling in implementations, and pointer-based `TraceUpload` inputs requiring callers to keep bytes/error variables live until the finisher runs. Tests should validate both noop and OTEL implementations against this contract.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/tracing/trace_handle.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/go-fuse/.github/workflows/ci.yml -->
# sources/user-network-fs/go-fuse/.github/workflows/ci.yml

Purpose: GitHub Actions CI definition for go-fuse. It runs on push, pull request, and a daily scheduled job at 12:00 UTC.

Important configuration: matrix tests Go versions 1.21.x through 1.26.x and `GOMAXPROCS` values default/all CPUs and `1`, with `fail-fast: false`. Steps install Go, check out full history for `git describe`, install `fuse3`, `libssl-dev`, and `libfuse-dev`, enable `user_allow_other`, then run `./all.bash`.

Control flow/state: CI is stateless per job but relies on Ubuntu runner kernel/FUSE support and root via sudo for selected tests.

Dependencies/integration: integrates with `all.bash`, package tests, benchmark compilation, and root-required FUSE paths. Risks include future Go-version availability, Ubuntu package changes, and scheduled failures from kernel/libfuse behavior. Test signal is the complete matrix across versions and single-CPU mode, which is important for deadlock/race exposure.
<!-- END_FILE_RESEARCH: sources/user-network-fs/go-fuse/.github/workflows/ci.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/go-fuse/all.bash -->
# sources/user-network-fs/go-fuse/all.bash

Purpose: central CI/test driver for go-fuse. It prints kernel information, verifies builds, runs tests, root-only tests, virtiofs tests, benchmark builds, and benchmark runs.

Important flow: `set -eux`; `go build ./...`; cross-builds key packages for Darwin and FreeBSD; sets `GO_TEST="go test -timeout 5m -p 1 -count 1"` to expose hangs, serialize output, and avoid cache; runs all tests as current user; runs selected `DirectMount`, `Forget`, `Passthrough`, and `IDMappedMount` tests with sudo; runs virtiofs tests with shorter timeout; builds benchmark C/Go helpers and executes benchmarks with CPU 1,2.

Dependencies/integration: requires Go, FUSE permissions, sudo, benchmark toolchain, optional QEMU/KVM behavior in virtiofs. Risks include tests that need root or kernel capabilities and external tools such as `make`, `g++`, `pkg-config fuse`. Test signal is broad and intentionally includes GOMAXPROCS-sensitive behavior via CI.
<!-- END_FILE_RESEARCH: sources/user-network-fs/go-fuse/all.bash -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/go-fuse/benchmark/Makefile -->
# sources/user-network-fs/go-fuse/benchmark/Makefile

Purpose: builds external benchmark helpers used by the Go benchmark suite.

Important targets: `all` depends on `cstatfs` and `bulkstat.bin`; `cstatfs` compiles `statfs.cc` with `g++ -O2 -Wall -std=c++0x` and `pkg-config fuse --cflags --libs`; `bulkstat.bin` builds `bulkstat/main.go` and copies the produced binary.

State/persistence: creates local artifacts `cstatfs`, `bulkstat/main`, and `bulkstat.bin`.

Dependencies/integration: used by `all.bash` and `BenchmarkLibfuseHighlevelThreadedStat`/`TestingBOnePass`. Risks are dependency on libfuse development headers, pkg-config naming, and stale binaries if source changes are not rebuilt. Test signal is benchmark build success and subsequent benchmark execution.
<!-- END_FILE_RESEARCH: sources/user-network-fs/go-fuse/benchmark/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/go-fuse/benchmark/benchmark.go -->
# sources/user-network-fs/go-fuse/benchmark/benchmark.go

Purpose: small utility support for benchmark code.

Important APIs: `ReadLines(name string) []string` reads an entire file, splits on newline with `bytes.Split`, filters empty lines, and returns strings. On read failure it calls `log.Fatal`.

Control flow/state: no retained state; all data is local to the read. The fatal-on-error behavior is acceptable for benchmark helpers but would be too abrupt for reusable library code.

Dependencies/integration: used by stat filesystem benchmarks and example/statfs to consume path-list inputs. Risks include memory use for very large path lists because the whole file is loaded, and no trimming of whitespace except newline splitting. Test signal is indirect through `stat_test.go` and example benchmark paths.
<!-- END_FILE_RESEARCH: sources/user-network-fs/go-fuse/benchmark/benchmark.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/go-fuse/benchmark/bulkstat/main.go -->
# sources/user-network-fs/go-fuse/benchmark/bulkstat/main.go

Purpose: external helper that repeatedly stats path lists in parallel so benchmark timing can focus on FUSE server work rather than in-process benchmark overhead.

Important APIs/functions: `BulkStat(parallelism, files)` starts worker goroutines consuming a buffered channel of paths and calling `os.Lstat`; `ReadLines` streams a file list with `bufio.Reader.ReadLine`; `main` parses `-N`, `-cpu`, `-prefix`, `-quiet`, prefixes paths, and loops until N stat operations are performed.

Control flow/state: workers terminate on zero-value string after channel close. Since the channel is buffered to `len(files)`, enqueueing does not block for normal inputs.

Dependencies/integration: built as `bulkstat.bin` and invoked by `stat_test.go`. Risks: `ReadLine` can truncate very long lines, `log.Fatal` exits the process on the first stat error, and an empty filename sentinel means blank path entries are unsupported. Test signal is benchmark success against generated path lists.
<!-- END_FILE_RESEARCH: sources/user-network-fs/go-fuse/benchmark/bulkstat/main.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/go-fuse/benchmark/latencymap.go -->
# sources/user-network-fs/go-fuse/benchmark/latencymap.go

Purpose: concurrency-safe accumulator for benchmark latency counts and durations by operation name.

Important APIs/types: `LatencyMap` embeds `sync.Mutex` and holds `map[string]*latencyMapEntry`; `NewLatencyMap` initializes the map; `Add` increments count and total duration; `Get` returns count and duration; `Counts` returns a copy of operation counts.

Control flow/state: all map access is mutex-protected. `Get` releases the lock before checking the copied pointer, which is safe for nil detection but reads `count`/`dur` after unlock; concurrent `Add` may race under the Go race detector because the entry fields are mutable. A safer implementation would copy values while locked.

Dependencies/integration: used by benchmark/instrumented examples. Test signal in `latencymap_test.go` covers simple accumulation but not concurrency.
<!-- END_FILE_RESEARCH: sources/user-network-fs/go-fuse/benchmark/latencymap.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/go-fuse/benchmark/latencymap_test.go -->
# sources/user-network-fs/go-fuse/benchmark/latencymap_test.go

Purpose: validates basic `LatencyMap` accumulation semantics.

Important test flow: creates a map, calls `Add("foo", 100ms)` and `Add("foo", 200ms)`, then asserts `Get("foo")` returns count `2` and total duration `300ms`.

State/dependencies: uses no external state beyond Go test runtime and `time.Duration`.

Integration/risk coverage: confirms same-key aggregation but does not test missing keys, `Counts`, concurrent access, or data-race behavior. The error text says "want 2, 150ms" while the assertion expects `300ms`; this is a minor diagnostic mismatch that could confuse failure triage.
<!-- END_FILE_RESEARCH: sources/user-network-fs/go-fuse/benchmark/latencymap_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/go-fuse/benchmark/mem_test.go -->
# sources/user-network-fs/go-fuse/benchmark/mem_test.go

Purpose: optional integration benchmark/test that mounts an in-memory go-fuse filesystem and runs `fio` against it.

Important types/functions: `memFile` embeds `fs.MemRegularFile`, suppresses xattr security probes with `ENOSYS`, and returns OK from `Fsync`; `memDir.Create` creates a `memFile` inode and adds it as a child; `TestBenchmarkMemFSFio` locates `fio`, mounts the fs with long attr/entry timeouts, then runs a 1 GiB direct-read fio workload.

Control flow/state: created files are in-memory slices; the mount is cleaned up through `t.Cleanup`.

Dependencies/integration: requires `fio`, FUSE mount capability, and `fs.Mount`. Risks include high resource use, direct I/O behavior, and test flakiness under constrained CI; it skips if `fio` is absent.
<!-- END_FILE_RESEARCH: sources/user-network-fs/go-fuse/benchmark/mem_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/go-fuse/benchmark/read_test.go -->
# sources/user-network-fs/go-fuse/benchmark/read_test.go

Purpose: benchmarks read throughput for synthetic go-fuse memory reads, loopback FD reads, and optional libfuse passthrough.

Important functions: `BenchmarkGoFuseMemoryRead` mounts `readFS` and runs `benchmarkRead` with `dd iflag=direct`; `benchmarkRead` launches one `dd` process per `GOMAXPROCS`, sets benchmark bytes to readers times block size, captures output unless verbose, and reports subprocess failures; `BenchmarkGoFuseFDRead` writes a backing file and mounts loopback; `BenchmarkLibfuseHP` starts an external libfuse passthrough binary when `--passthrough_hp` is supplied.

Dependencies/integration: uses `dd`, `fusermount`, optional libfuse helper, temp dirs, and `setupFS` from `stat_test.go`.

Risks/test signals: external process failures are surfaced with buffered output. Large `b.N` can create large backing files. The benchmarks exercise direct I/O, loopback file handles, and subprocess interaction with mounted FUSE filesystems.
<!-- END_FILE_RESEARCH: sources/user-network-fs/go-fuse/benchmark/read_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/go-fuse/benchmark/readfs.go -->
# sources/user-network-fs/go-fuse/benchmark/readfs.go

Purpose: implements a synthetic filesystem for raw read-throughput benchmarking.

Important APIs/types: `readFS` embeds `fs.Inode` and implements `NodeLookuper`, `NodeGetattrer`, `NodeOpener`, and `fs.FileReader`. Any lookup returns a regular-file inode. `Getattr` reports a huge `fileSize` (`2 << 60`) and one-hour attr timeout. `Open` returns a `readFS` file handle with `FOPEN_DIRECT_IO`; `Read` returns the incoming destination buffer as zero-filled data.

Control flow/state: stateless and allocation-minimal. There is no backing storage; reads are synthesized.

Dependencies/integration: used by `BenchmarkGoFuseMemoryRead`. Risks include unrealistic semantics compared with real files, and every name resolves successfully, but that is intentional for throughput isolation. Test signal comes through `dd` benchmark success.
<!-- END_FILE_RESEARCH: sources/user-network-fs/go-fuse/benchmark/readfs.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/go-fuse/benchmark/stat_test.go -->
# sources/user-network-fs/go-fuse/benchmark/stat_test.go

Purpose: tests and benchmarks a static in-memory stat/readdir workload and compares it with a libfuse C filesystem.

Important functions: `setupFS` mounts a node and registers cleanup; `TestNewStatFs` verifies constructed directory hierarchy and file mode behavior; `BenchmarkGoFSStat` populates `StatFS` from `testpaths.txt` and shells out to `bulkstat.bin`; `BenchmarkGoFSReaddir` times directory reads; `TestingBOnePass` measures an external stat pass and optionally logs GC data; `BenchmarkLibfuseHighlevelThreadedStat` creates a C `cstatfs` mount and runs the same stat helper.

State/dependencies: uses FUSE mounts, temp files, `bulkstat.bin`, `cstatfs`, `fusermount`, path-list fixtures, and GOMAXPROCS.

Risks/test signals: strong integration coverage of namespace construction and stat scalability; fragile where benchmark binaries or libfuse are absent.
<!-- END_FILE_RESEARCH: sources/user-network-fs/go-fuse/benchmark/stat_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/go-fuse/benchmark/statfs.cc -->
# sources/user-network-fs/go-fuse/benchmark/statfs.cc

Purpose: libfuse C benchmark filesystem used as a comparison point for stat-heavy workloads.

Important APIs/functions: `StatFs::readFrom` loads paths from `$STATFS_INPUT` into an `unordered_map<string,bool>` indicating directory vs file; `StatFs::GetAttr` handles root, known directories, and known files, optionally sleeping for `$STATFS_DELAY_USEC`; `global_getattr` bridges to libfuse; `main` reads env config, initializes `fuse_operations.getattr`, and calls `fuse_main`.

Control flow/state: global singleton `global`; in-memory map of path metadata; read-only getattr-only filesystem.

Dependencies/integration: compiled with libfuse headers/libs by `Makefile`; invoked by `BenchmarkLibfuseHighlevelThreadedStat`. Risks include no null check after `fopen`, fixed 1024-byte input line buffer, global state, and libfuse version/API assumptions. Test signal is benchmark startup and stat success.
<!-- END_FILE_RESEARCH: sources/user-network-fs/go-fuse/benchmark/statfs.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/go-fuse/benchmark/statfs.go -->
# sources/user-network-fs/go-fuse/benchmark/statfs.go

Purpose: builds a static in-memory file tree for stat/readdir benchmarks.

Important APIs/types: `StatFS` embeds `fs.Inode` and buffers `files map[string]fuse.Attr` before mount. `AddFile` records paths; `OnAdd` materializes all pending paths; `addFile` walks directory components, creates persistent directory inodes as needed, creates persistent `fs.MemRegularFile` leaves with requested attributes, and attaches children.

Control flow/state: before `OnAdd`, file metadata is stored in the map. After `OnAdd`, the source of truth is persistent inodes and `files` is set nil.

Dependencies/integration: used by `stat_test.go` and `example/statfs/main.go`. Risks include overwriting duplicate paths, default stable attrs for files, and memory use proportional to files plus content sizes. Tests validate hierarchy and benchmark stat/readdir.
<!-- END_FILE_RESEARCH: sources/user-network-fs/go-fuse/benchmark/statfs.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/go-fuse/doc.go -->
# sources/user-network-fs/go-fuse/doc.go

Purpose: repository-level package documentation for the module root package `lib`.

Important content: describes go-fuse as Go bindings for writing FUSE filesystems and points users toward the modern `fs` package documentation plus older deprecated `pathfs` and `nodefs` APIs.

Control flow/state: none; documentation-only source file.

Dependencies/integration: package declaration allows root package documentation in Go tooling. Risks are documentation drift because links still point at godoc URLs and mention older APIs. Test signal is build/doc generation success; no behavioral tests are needed for this file.
<!-- END_FILE_RESEARCH: sources/user-network-fs/go-fuse/doc.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/go-fuse/example/benchmark-read-throughput/readbench.go -->
# sources/user-network-fs/go-fuse/example/benchmark-read-throughput/readbench.go

Purpose: standalone helper for measuring repeated single-file read throughput.

Important functions: `gulp` opens a file, reads it in blocks until a short read, and returns bytes read; `main` parses block size in KiB and total MB limit, repeatedly calls `gulp`, accumulates duration and MB read, then prints MB/s.

Control flow/state: no persistent state; repeated full-file reads until total MB threshold is reached.

Dependencies/integration: uses standard `os`, `flag`, and `time`; intended to run against mounted FUSE files. Risks include ignoring non-EOF read errors inside `gulp` because it discards the error from `f.Read`, and integer truncation in throughput output. Test signal is manual benchmark output rather than automated tests.
<!-- END_FILE_RESEARCH: sources/user-network-fs/go-fuse/example/benchmark-read-throughput/readbench.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/go-fuse/example/benchmark.sh -->
# sources/user-network-fs/go-fuse/example/benchmark.sh

Purpose: legacy shell workflow for benchmarking `zipfs` stat performance and optional internal latency monitoring.

Important flow: validates a ZIP input, sets `GOMAXPROCS` from `/proc/cpuinfo`, builds `zipfs` and `bulkstat` with `gomake`, mounts zipfs, generates a file list with `find`, reruns zipfs, runs `bulkstat`, attaches `6prof`, reruns `bulkstat`, unmounts, then runs zipfs with `-latencies` and dumps `.debug`.

State/dependencies: writes under `/tmp`, uses `/tmp/zipbench`, `/tmp/zipfiles.txt`, `zipfs.log`, `fusermount`, `6prof`, `gomake`, Linux `/proc`.

Risks: non-POSIX `==` under `/bin/sh`, missing tools, stale mount cleanup, and unquoted paths. It is useful as manual benchmark documentation but not robust CI. Test signal is manual successful execution and profiler output.
<!-- END_FILE_RESEARCH: sources/user-network-fs/go-fuse/example/benchmark.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/go-fuse/example/hello/main.go -->
# sources/user-network-fs/go-fuse/example/hello/main.go

Purpose: minimal go-fuse example analogous to libfuse `hello.c`, exposing one file at the mount root.

Important APIs/types: `HelloRoot` embeds `fs.Inode`, implements `NodeOnAdder` to create persistent `fs.MemRegularFile` child `file.txt`, and implements `NodeGetattrer` to set root permissions to `0755`. `main` parses `-debug`, mounts via `fs.Mount`, and waits.

Control flow/state: static in-memory tree populated at mount time. File content is the bytes `file.txt`; no backing persistence.

Dependencies/integration: demonstrates `fs.Options`, `fs.MemRegularFile`, `fuse.Attr`, and stable inode assignment. Risks are educational rather than production: fixed content and no cleanup beyond normal unmount. Test signal is successful mount and reading `/file.txt`.
<!-- END_FILE_RESEARCH: sources/user-network-fs/go-fuse/example/hello/main.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/go-fuse/example/loopback/main.go -->
# sources/user-network-fs/go-fuse/example/loopback/main.go

Purpose: command-line loopback filesystem that mirrors operations to a backing directory.

Important functions/options: `writeMemProfile` writes heap profiles on SIGUSR1; `main` parses debug, allow-other, idmapped, quiet, read-only, direct mount, CPU/memory profile flags; creates `fs.NewLoopbackRoot`; configures attr/entry one-second TTLs, `NullPermissions`, FUSE mount names, allow_other/default_permissions, read-only mount option, and logger; mounts and waits while handling SIGINT/SIGTERM for unmount.

State/dependencies: persistent state is the backing filesystem. Profiles are written to requested files.

Integration/risks: relies on `fs.LoopbackNode` syscall passthrough and kernel FUSE options. Risks include allow_other requiring fuse.conf, profiles needing graceful unmount, and backing mutations being real. Test signal comes from loopback tests and manual use.
<!-- END_FILE_RESEARCH: sources/user-network-fs/go-fuse/example/loopback/main.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/go-fuse/example/memfs/main.go -->
# sources/user-network-fs/go-fuse/example/memfs/main.go

Purpose: legacy example mounting the deprecated `nodefs` in-memory filesystem.

Important flow: parses `-debug`, requires mountpoint and backing-prefix args, creates `nodefs.NewMemNodeFSRoot(prefix)`, wraps it in `nodefs.NewFileSystemConnector`, starts a raw fuse server with `fuse.NewServer`, and calls `Serve`.

State/dependencies: stores filesystem data in the old nodefs memory implementation, seeded by prefix behavior from that package.

Integration/risks: illustrates older API surface (`fuse/nodefs`) rather than modern `fs`. Risks include deprecated API drift and no signal handling/cleanup. Build coverage in `go build ./...` is the main test signal.
<!-- END_FILE_RESEARCH: sources/user-network-fs/go-fuse/example/memfs/main.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/go-fuse/example/multizip/main.go -->
# sources/user-network-fs/go-fuse/example/multizip/main.go

Purpose: mounts a read-only `zipfs.MultiZipFs` filesystem, intended for serving multiple archives selected through config symlinks.

Important flow: parses `-debug`, requires mountpoint, constructs `zipfs.MultiZipFs`, sets one-second entry/attr timeouts, mounts via `fs.Mount`, and waits.

State/dependencies: archive/config state is managed by `zipfs.MultiZipFs`; this file is just the command driver.

Integration/risks: depends on `zipfs` package behavior and FUSE mount availability. Error handling exits process on mount failure. Test signal is build coverage and manual mount/list behavior; no direct automated tests are in this file.
<!-- END_FILE_RESEARCH: sources/user-network-fs/go-fuse/example/multizip/main.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/go-fuse/example/statfs/main.go -->
# sources/user-network-fs/go-fuse/example/statfs/main.go

Purpose: command-line driver for the benchmark `StatFS` filesystem.

Important flow: parses debug, CPU profile, memory profile, post-mount command, and TTL; reads filenames from an input file; populates `benchmark.StatFS` with regular-file attrs; mounts with attr/entry TTLs; starts CPU profiling after mount; optionally starts a command; waits for unmount; writes heap profile at exit.

State/dependencies: filesystem tree is in memory; optional profile files are persistent artifacts; optional command runs outside the server.

Integration/risks: integrates benchmark package, `fs.Mount`, `runtime/pprof`, and external commands. Risks include `strings.Split` not respecting shell quoting for `-run`, and profile output requiring graceful unmount. Test signal is manual benchmark and build coverage.
<!-- END_FILE_RESEARCH: sources/user-network-fs/go-fuse/example/statfs/main.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/go-fuse/example/virtiofs/main.go -->
# sources/user-network-fs/go-fuse/example/virtiofs/main.go

Purpose: serves a loopback filesystem over virtiofs rather than mounting through the normal FUSE mount path.

Important flow: parses args, uses `flag.Arg(0)` as socket path and `flag.Arg(1)` as backing directory, creates `fs.NewLoopbackRoot`, enables debug logging, builds a raw node filesystem with `fs.NewNodeFS`, and calls `virtiofs.ServeFS`.

State/dependencies: backing filesystem persists data; virtiofs server listens on the socket path.

Integration/risks: depends on `virtiofs` package, loopback implementation, and correct argument count. The code does not validate missing args before use. Test signal is build coverage plus virtiofs integration tests driven by `all.bash`.
<!-- END_FILE_RESEARCH: sources/user-network-fs/go-fuse/example/virtiofs/main.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/go-fuse/example/winfs/main.go -->
# sources/user-network-fs/go-fuse/example/winfs/main.go

Purpose: loopback filesystem variant that emulates Windows semantics by rejecting unlink/rename of open files.

Important types/functions: `WindowsNode` embeds `fs.LoopbackNode` and tracks `openCount` under a mutex. `Open` and `Create` increment counts; `Release` decrements and forwards file release; `isBusy` sleeps for a configurable delay then checks child open count; `Unlink` and `Rename` return `EBUSY` when source or destination is busy. `newWindowsNode` customizes `LoopbackRoot.NewNode`.

State/dependencies: persistent state lives in the backing filesystem; transient open counts live in each node.

Risks/integration: the delay is a race workaround because kernel close does not synchronize release before subsequent operations. It depends on deprecated `LoopbackRoot.NewNode`. Test signal is manual behavior and analogous Windows example tests elsewhere.
<!-- END_FILE_RESEARCH: sources/user-network-fs/go-fuse/example/winfs/main.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/go-fuse/example/zipfs/main.go -->
# sources/user-network-fs/go-fuse/example/zipfs/main.go

Purpose: command-line driver for mounting a ZIP archive as a read-only filesystem.

Important flow: parses debug, CPU profile, memory profile, post-mount command, and TTL; creates root with `zipfs.NewArchiveFileSystem`; mounts with attr/entry TTLs; starts optional CPU profiling and command; waits; writes heap profile on exit.

State/dependencies: archive contents are the source of filesystem data; optional profile files are generated.

Integration/risks: integrates `zipfs`, `fs.Mount`, pprof, and external command execution. Risks include `strings.Split` command parsing, memory use for archive metadata, and profile files only being complete after graceful unmount. Test signal is build coverage and manual archive mount behavior.
<!-- END_FILE_RESEARCH: sources/user-network-fs/go-fuse/example/zipfs/main.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/go-fuse/fs/abort_test.go -->
# sources/user-network-fs/go-fuse/fs/abort_test.go

Purpose: verifies Linux FUSE connection abort propagates cancellation to a blocked filesystem operation.

Important types/functions: `hangingRootNode` implements `OpendirHandle`, closes `openCalled`, waits for `ctx.Done`, records `canceled`, and returns `EINTR`. `TestAbort` mounts the node, derives the FUSE connection ID from mount device, starts a blocking directory open, writes to `/sys/fs/fuse/connections/<id>/abort`, expects the open to fail, unmounts, and asserts cancellation was observed.

State/dependencies: Linux-only, requires `/sys/fs/fuse/connections` access and a real FUSE mount.

Risks/test signals: high-value coverage for abort/cancel path; can be environment-sensitive due to kernel permissions and timing. It explicitly skips non-Linux.
<!-- END_FILE_RESEARCH: sources/user-network-fs/go-fuse/fs/abort_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/go-fuse/fs/api.go -->
# sources/user-network-fs/go-fuse/fs/api.go

Purpose: public contract for the tree-based go-fuse filesystem API. The top-level documentation explains inode-based design, kernel caches, interrupts, locking/deadlock caveats, dynamic lookup/readdir, and static persistent in-memory trees.

Important APIs/types: `InodeEmbedder`; many optional `Node*` operation interfaces for statfs, access, getattr/setattr, xattrs, link/symlink/create/rename, read/write/fsync/flush/release, fallocate, copy_file_range, statx, lseek, locks, ioctl, lifecycle; `DirStream`; file-handle interfaces such as `FileReader`, `FileWriter`, `FileReaddirenter`, `FileSeekdirer`, and `FilePassthroughFder`; `Options` for cache TTLs, automatic inode numbering, root `OnAdd`, permissions, UID/GID defaults, test callbacks, logging, and root stable attrs.

Control flow/state: interfaces are implemented by user nodes and dispatched by `bridge.go`. `Options` influences default attr rewriting, cache timeouts, negative lookup caching, and mount behavior.

Risks/test signals: API stability is critical. Risks include subtle defaults (`Unlink`/`Rmdir` default success, zero permissions rewritten unless `NullPermissions`), interrupt handling expectations, and deterministic `Readdir` requirements. Broad tests in this subset exercise direct I/O, caching, rename, forget, statx, ioctl, and loopback integration.
<!-- END_FILE_RESEARCH: sources/user-network-fs/go-fuse/fs/api.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/go-fuse/fs/bridge.go -->
# sources/user-network-fs/go-fuse/fs/bridge.go

Purpose: core raw FUSE bridge that translates kernel requests into optional `fs` node/file interfaces while maintaining inode and file-handle bookkeeping.

Important APIs/types/functions: `rawBridge`, `fileEntry`, `ServerCallbacks`; `NewNodeFS`; request handlers for `Lookup`, `Mkdir`, `Mknod`, `Create`, `Forget`, `GetAttr`, `SetAttr`, `Rename`, `Link`, `Symlink`, xattrs, `Open`, `Read`, locks, `Release`, `Write`, `Flush`, `Fsync`, `Fallocate`, `OpenDir`, `ReadDirPlus`, `ReadDir`, `FsyncDir`, `StatFs`, `CopyFileRange`, `Ioctl`, `Lseek`, `OnUnmount`.

Control flow/state: bridge maps kernel node IDs to `Inode`, stable attrs to deduplicated inodes, allocates file handles, tracks free handles, registers backing FDs for passthrough, applies attr/entry timeouts, and uses locks ordered with inode locks before bridge mutex. `readDirMaybeLookup` handles overflow, seek offsets, interrupted reads, and readdirplus lookup.

Dependencies/integration: depends on `fuse`, `internal.HasAccess`, and interfaces from `api.go`. Risks are concurrency, lookup-count lifecycle, stale stable attrs, file-handle release races, readdir offset correctness, and passthrough reference counts. Tests cover virtual entries, type changes, negative cache, direct I/O, dir seek, cache behavior, ioctl, forget, and loopback operations.
<!-- END_FILE_RESEARCH: sources/user-network-fs/go-fuse/fs/bridge.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/go-fuse/fs/bridge_linux.go -->
# sources/user-network-fs/go-fuse/fs/bridge_linux.go

Purpose: Linux-specific `Statx` support for `rawBridge`.

Important functions: `setStatx` mirrors attr defaulting for permissions, UID/GID, and block fields; `setStatxTimeout` applies attr timeout; `Statx` resolves inode/file handle, dispatches to `NodeStatxer` or file statx implementation, then normalizes inode number and mode from stable attrs before returning status.

Control flow/state: reads bridge options and inode stable attrs; no independent persistent state.

Dependencies/integration: depends on Linux `fuse.Statx*` types and `setStatxBlocks` from `files_linux.go`. One apparent risk is the fallback type assertion checks `n.ops.(FileStatxer)` rather than the file handle, so file-level statx may not dispatch as intended unless node ops also implement it. Test signal should include Linux statx tests and loopback statx behavior.
<!-- END_FILE_RESEARCH: sources/user-network-fs/go-fuse/fs/bridge_linux.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/go-fuse/fs/bridge_nonlinux.go -->
# sources/user-network-fs/go-fuse/fs/bridge_nonlinux.go

Purpose: non-Linux fallback for `rawBridge.Statx`.

Important API: `Statx` has the same signature as Linux bridge support and always returns `fuse.ENOSYS`.

Control flow/state: none beyond immediate status return.

Dependencies/integration: build-tagged `!linux`; ensures the fs package compiles on platforms without Linux statx support. Risks are minimal; platform consumers must tolerate statx absence and fall back to getattr. Cross-builds in `all.bash` for Darwin and FreeBSD are the main test signal.
<!-- END_FILE_RESEARCH: sources/user-network-fs/go-fuse/fs/bridge_nonlinux.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/go-fuse/fs/bridge_test.go -->
# sources/user-network-fs/go-fuse/fs/bridge_test.go

Purpose: targeted tests for raw bridge behavior around readdirplus virtual entries, inode type changes, orphan paths, inode number 1, negative lookup caching, and nil options.

Important tests: `TestBridgeReaddirPlusVirtualEntries` inspects raw buffer layout to ensure `.`/`..` have `NodeId` zero; `TestTypeChange` reuses inode number with changing file type; `TestDeletedInodePath` verifies orphan paths get `.go-fuse.../deleted`; `TestIno1` allows inode number 1; `TestNegativeLookupCache` checks lookup counts with/without negative TTL; `TestNewNodeFSNilOpts` ensures defaults.

State/dependencies: uses real FUSE mounts plus in-memory test nodes.

Risks/test signals: covers subtle kernel cache and stable-attr behavior. It is sensitive to low-level buffer layout and FUSE mount support, but gives strong regression signals for bridge invariants.
<!-- END_FILE_RESEARCH: sources/user-network-fs/go-fuse/fs/bridge_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/go-fuse/fs/cache_test.go -->
# sources/user-network-fs/go-fuse/fs/cache_test.go

Purpose: validates kernel cache controls exposed through open flags, notifications, symlink caching, and auto invalidation.

Important tests/types: `keepCacheFile` changes content on reads and optionally returns `FOPEN_KEEP_CACHE`; `TestKeepCache` checks cached reads stay stable until `NotifyContent`; `countingSymlink` tracks `Readlink` calls; `TestSymlinkCaching` enables `EnableSymlinkCaching`, verifies one readlink until notification, and documents attr-size truncation behavior; `autoInvalNode` changes mtime/content and `TestAutoInvalData` verifies a stat triggers reread.

State/dependencies: uses mutable in-memory content protected by mutexes and real FUSE kernel caching.

Risks/test signals: strong coverage for cache invalidation semantics, but kernel feature support can skip or vary behavior. Timing uses short TTLs, which may be flaky on slow systems.
<!-- END_FILE_RESEARCH: sources/user-network-fs/go-fuse/fs/cache_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/go-fuse/fs/constants.go -->
# sources/user-network-fs/go-fuse/fs/constants.go

Purpose: central constants and errno helpers for the fs package.

Important APIs: `OK` is `syscall.Errno(0)`; `ToErrno(err)` converts arbitrary errors through `fuse.ToStatus`; `RENAME_EXCHANGE` defines renameat2 exchange flag; `_SEEK_DATA` and `_SEEK_HOLE` provide lseek constants; `ENOATTR` aliases internal xattr missing-attribute errno.

Control flow/state: only `ToErrno` has logic; no mutable state.

Dependencies/integration: used broadly across bridge, loopback, memory nodes, and tests. Risks are mostly portability: numeric constants must match target OS/kernel expectations, and `ToErrno(nil)` must continue to map to success through fuse status conversion. Tests indirectly cover all constants through rename, lseek, and xattr behavior.
<!-- END_FILE_RESEARCH: sources/user-network-fs/go-fuse/fs/constants.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/go-fuse/fs/default.go -->
# sources/user-network-fs/go-fuse/fs/default.go

Purpose: placeholder source file declaring package `fs`.

Important APIs/functions: none.

Control flow/state/dependencies: none beyond package membership.

Integration/risks: may exist to keep package layout or historical compatibility. It has no behavioral surface and no direct test needs, but build success confirms it remains syntactically valid.
<!-- END_FILE_RESEARCH: sources/user-network-fs/go-fuse/fs/default.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/go-fuse/fs/dir_test.go -->
# sources/user-network-fs/go-fuse/fs/dir_test.go

Purpose: tests directory-stream error propagation, seek behavior, and fsyncdir support.

Important tests/types: `errDirStream` returns one valid entry then `EBADMSG`; `TestDirStreamError` checks error delivery with readdirplus enabled and disabled. `dirStreamSeekNode` and `listDirEntries` produce custom offsets and implement `Seekdir`; `testDirSeek` verifies resuming after each offset. `syncNode`/`syncDir` implement `FileFsyncdirer`; `TestFsyncDir` opens the mount directory and calls `fsync`.

State/dependencies: real FUSE mounts, mutable counters protected by mutex, directory streams.

Risks/test signals: validates tricky readdir offset semantics and partial-error behavior. Kernel/platform differences in directory offsets can influence failures, but the tests use controlled streams.
<!-- END_FILE_RESEARCH: sources/user-network-fs/go-fuse/fs/dir_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/go-fuse/fs/dircache_test.go -->
# sources/user-network-fs/go-fuse/fs/dircache_test.go

Purpose: verifies `FOPEN_CACHE_DIR` directory caching behavior.

Important types/functions: `dirCacheTestNode` counts open calls and reads that occur after the first open. `OpendirHandle` builds 1024 deterministic entries, wraps them in `countingReaddirenter`, and returns `fuse.FOPEN_CACHE_DIR`. `TestDirCacheFlag` reads directory entries twice through `NewLoopbackDirStream`, compares results, and expects two opens but zero cached second-open read callbacks when kernel directory caching works.

State/dependencies: mutex-protected counters and kernel support for FUSE protocol 7.28 directory caching.

Risks/test signals: skips on kernels without required support. The test is sensitive to kernel cache behavior and `DisableReadDirPlus`.
<!-- END_FILE_RESEARCH: sources/user-network-fs/go-fuse/fs/dircache_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/go-fuse/fs/directio_example_test.go -->
# sources/user-network-fs/go-fuse/fs/directio_example_test.go

Purpose: documentation example showing direct I/O for per-open dynamic file content.

Important types/functions: `bytesFileHandle` implements `FileReader` over per-handle bytes; `timeFile.Open` rejects write flags, captures current time into a new handle, and returns `FOPEN_DIRECT_IO`; `Example_directIO` mounts a root and adds a persistent `clock` file in `OnAdd`.

Control flow/state: each open gets independent content. Direct I/O prevents kernel page cache from hiding changes between opens.

Dependencies/integration: demonstrates `fs.Mount`, `FileReader`, `NodeOpener`, persistent inodes, and `fuse.ReadResultData`. Risk: the write-flag check uses `fuseFlags` instead of `openFlags`, so the example as written does not actually reject writes based on caller flags. Example is manual and not assertion-based.
<!-- END_FILE_RESEARCH: sources/user-network-fs/go-fuse/fs/directio_example_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/go-fuse/fs/directio_test.go -->
# sources/user-network-fs/go-fuse/fs/directio_test.go

Purpose: tests `FOPEN_DIRECT_IO` read and file-handle `Lseek` behavior.

Important types/functions: `dioRoot.OnAdd` adds `file`; `dioFile.Open` returns `dioFH` with `FOPEN_DIRECT_IO`; `dioFH.Read` returns bytes encoding the offset; `dioFH.Lseek` rounds offsets up to the next 1024-byte boundary. `TestFUSEDirectIO` reads initial bytes, conditionally tests kernel lseek support, and verifies subsequent read starts at offset 1024.

State/dependencies: real FUSE mount and kernel protocol support for lseek 7.24.

Risks/test signals: covers direct I/O bypassing cache and file-handle operation dispatch. It skips lseek assertions when unsupported.
<!-- END_FILE_RESEARCH: sources/user-network-fs/go-fuse/fs/directio_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/go-fuse/fs/dirstream.go -->
# sources/user-network-fs/go-fuse/fs/dirstream.go

Purpose: implements in-memory and loopback directory-stream adapters used by bridge directory operations.

Important types/functions: `dirArray` wraps `[]fuse.DirEntry` with sequential offsets and seek support; `NewListDirStream`; `dirStreamAsFile` adapts a `DirStream` creator to file-handle readdir/release/seek interfaces; `loopbackDirStream` reads OS directory entries via `getdents`, buffers raw records, parses them with `fuse.DirEntry.Parse`, supports `Seekdir`, `Fsyncdir`, `Releasedir`, and ioctl forwarding.

Control flow/state: `loopbackDirStream` owns an fd, buffer, pending bytes, and pending errno under mutex. `load` lazily refills only when no pending entries/error exist.

Dependencies/integration: used by `LoopbackNode.OpendirHandle`, bridge fallback directory listing, and tests. Risks include fd lifecycle, platform `getdents` differences, unsafe ioctl buffer indexing when input/output slices are empty, and directory offset correctness. Tests cover seek, errors, fsyncdir, caching, and loopback dirs.
<!-- END_FILE_RESEARCH: sources/user-network-fs/go-fuse/fs/dirstream.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/go-fuse/fs/dirstream_darwin.go -->
# sources/user-network-fs/go-fuse/fs/dirstream_darwin.go

Purpose: Darwin implementation of the directory-entry syscall adapter.

Important API: `getdents(fd, buf)` calls `unix.Getdirentries(fd, buf, nil)`.

Control flow/state: no retained state; wraps a platform syscall for `dirstream.go`.

Dependencies/integration: selected for Darwin builds; used by `loopbackDirStream.load`. Risks are OS-specific directory entry layout and offset handling differences. Cross-build coverage in `all.bash` is the main signal, but runtime behavior needs macOS-specific tests.
<!-- END_FILE_RESEARCH: sources/user-network-fs/go-fuse/fs/dirstream_darwin.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/go-fuse/fs/dirstream_test.go -->
# sources/user-network-fs/go-fuse/fs/dirstream_test.go

Purpose: focused test for list-backed `DirStream` seek behavior through a mounted filesystem.

Important types/functions: `SimpleFS.Readdir` returns 16 deterministic regular-file entries through `NewListDirStream`; `TestDirSeek` mounts `SimpleFS`, defers cleanup/unmount, and invokes shared `testDirSeek` from `dir_test.go`.

State/dependencies: real FUSE mount plus deterministic in-memory directory entries.

Risks/test signals: validates that the generic list stream path cooperates with bridge/loopback directory seeking. It relies on helper behavior in `dir_test.go`; failures point to offset management rather than filesystem content generation.
<!-- END_FILE_RESEARCH: sources/user-network-fs/go-fuse/fs/dirstream_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/go-fuse/fs/dirstream_unix.go -->
# sources/user-network-fs/go-fuse/fs/dirstream_unix.go

Purpose: non-Darwin implementation of the directory-entry syscall adapter.

Important API: build-tagged `!darwin`; `getdents(fd, buf)` calls `unix.Getdents`.

Control flow/state: no state; wraps syscall for `loopbackDirStream`.

Dependencies/integration: used on Linux and other non-Darwin Unix platforms. Risks include differences on FreeBSD or unsupported platforms under the broad `!darwin` tag, but package cross-builds and platform-specific files reduce that. Runtime tests on Linux cover the common path.
<!-- END_FILE_RESEARCH: sources/user-network-fs/go-fuse/fs/dirstream_unix.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/go-fuse/fs/dynamic_example_test.go -->
# sources/user-network-fs/go-fuse/fs/dynamic_example_test.go

Purpose: example of a dynamically discovered filesystem where numbers are files or directories and stable inode numbers deduplicate repeated nodes.

Important types/functions: `numberNode` embeds `fs.Inode` and stores `num`; `isPrime` and `numberToMode` choose file vs directory; `Readdir` lists smaller numbers; `Lookup` parses a child name, validates bounds, sets `StableAttr{Mode, Ino:uint64(i)}`, creates a new inode, and returns it; `Example_dynamic` mounts root `10`.

State/dependencies: no persistent backing store; stable inode numbers deduplicate repeated lookups across paths.

Integration/risks: demonstrates `NodeLookuper`, `NodeReaddirer`, and dynamic hard-link-like identity. Risks are pedagogical: generated filesystem is synthetic and prime function treats edge values simply. Build/example coverage is primary signal.
<!-- END_FILE_RESEARCH: sources/user-network-fs/go-fuse/fs/dynamic_example_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/go-fuse/fs/example_test.go -->
# sources/user-network-fs/go-fuse/fs/example_test.go

Purpose: documentation example for creating and mounting a loopback filesystem.

Important flow: creates a temp mount dir, reads `$HOME`, creates `fs.NewLoopbackRoot(home)`, mounts it with debug enabled, prints caution that writes under the mount affect `$HOME`, and waits for unmount.

State/dependencies: mirrors the user's home directory; persistent state is the real `$HOME` tree.

Integration/risks: demonstrates `fs.Mount` and `fuse.MountOptions`. The explicit risk is destructive write-through behavior if users treat the mount as disposable. It is example documentation rather than an automated assertion.
<!-- END_FILE_RESEARCH: sources/user-network-fs/go-fuse/fs/example_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/go-fuse/fs/files.go -->
# sources/user-network-fs/go-fuse/fs/files.go

Purpose: implements `LoopbackFile`, a file-handle wrapper around a Unix fd that satisfies most file-level go-fuse interfaces.

Important APIs/functions: `NewLoopbackFile`; `PassthroughFd`; `Read` returns `fuse.ReadResultFd`; `Write` uses `Pwrite`; `Release` closes once; `Flush` closes a dup; `Fsync`; OFD/flock locking through `Getlk`, `Setlk`, `Setlkw`; `Setattr`/`setAttr` handle chmod/chown/times/truncate; `Getattr`; `Lseek`; `Allocate`; ioctl passthrough; platform-specific `utimens`.

Control flow/state: fd protected by `mu`; `Release` marks fd `-1`. Operations serialize on the file handle.

Dependencies/integration: used by `LoopbackNode.Open/Create`; integrates fallocate, ioctl, unix syscalls, passthrough backing FDs. Risks include operations after release, serializing all I/O on one mutex, syscall portability, and fd ownership requirements documented by `NewLoopbackFile`. Tests cover loopback reads/writes, ioctl, copy, stat, direct I/O, and mount behavior.
<!-- END_FILE_RESEARCH: sources/user-network-fs/go-fuse/fs/files.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/go-fuse/fs/files_darwin.go -->
# sources/user-network-fs/go-fuse/fs/files_darwin.go

Purpose: Darwin-specific file helpers for block defaults and timestamp updates.

Important functions: `setBlocks` is a no-op on Darwin; `LoopbackFile.utimens` emulates `utimensat`/`UTIME_OMIT` using `Futimes`, first calling `Getattr` when either atime or mtime should be preserved.

State/dependencies: uses the file descriptor in `LoopbackFile` and current attrs when preserving times.

Integration/risks: selected for Darwin builds. Risks include timestamp precision loss from timeval microseconds and extra getattr calls. Cross-builds provide compile signal; runtime timestamp behavior needs macOS coverage.
<!-- END_FILE_RESEARCH: sources/user-network-fs/go-fuse/fs/files_darwin.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/go-fuse/fs/files_freebsd.go -->
# sources/user-network-fs/go-fuse/fs/files_freebsd.go

Purpose: FreeBSD-specific no-op block defaulting helper.

Important API: `setBlocks(out *fuse.Attr)` intentionally does nothing.

Control flow/state: none.

Dependencies/integration: selected in FreeBSD builds and used by bridge attr normalization. Risks are minimal, but leaving block fields unset may affect callers that expect Linux-like `Blocks`/`Blksize`. Cross-build in `all.bash` is the primary signal.
<!-- END_FILE_RESEARCH: sources/user-network-fs/go-fuse/fs/files_freebsd.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/go-fuse/fs/files_linux.go -->
# sources/user-network-fs/go-fuse/fs/files_linux.go

Purpose: Linux-specific block defaulting and file-handle statx support.

Important functions: `setBlocks` and `setStatxBlocks` fill `Blksize=4096` and `Blocks=ceil(Size/4096)*8` when unset; `LoopbackFile.Statx` calls `unix.Statx` on the fd and fills `fuse.StatxOut`.

State/dependencies: reads size fields from attr/statx output; uses the loopback fd under mutex.

Integration/risks: used by bridge attr/statx normalization and loopback statx dispatch. Risks include assumptions about 4KiB block size and statx on fd with empty path/flags semantics. Linux statx and attr tests are relevant signals.
<!-- END_FILE_RESEARCH: sources/user-network-fs/go-fuse/fs/files_linux.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/go-fuse/fs/files_unix.go -->
# sources/user-network-fs/go-fuse/fs/files_unix.go

Purpose: non-Darwin Unix timestamp update helper for `LoopbackFile`.

Important functions: `LoopbackFile.utimens` builds two `syscall.Timespec` values with `fuse.UtimeToTimespec`; `futimens` invokes `SYS_UTIMENSAT` with fd, null pathname, and flags zero to emulate `futimens(3)`.

State/dependencies: operates on the file descriptor in `LoopbackFile`.

Integration/risks: build-tagged `!darwin`, so it covers Linux and FreeBSD unless overridden. Risks include syscall availability and `unsafe.Pointer` usage. Timestamp behavior is indirectly tested by loopback setattr paths.
<!-- END_FILE_RESEARCH: sources/user-network-fs/go-fuse/fs/files_unix.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/go-fuse/fs/forget_test.go -->
# sources/user-network-fs/go-fuse/fs/forget_test.go

Purpose: validates inode FORGET cleanup, memory compaction expectations, and `NodeOnForgetter` callbacks.

Important tests/types: `allChildrenNode` dynamically produces a 100x100 tree; root-only Linux `TestForget` walks it, drops kernel dentries via `/proc/sys/vm/drop_caches`, waits for TTL, and expects only root in `kernelNodeIds`. `forgetTestRootNode`/`forgetTestSubNode` count `OnForget`; `TestOnForget` verifies rmdir alone does not forget persistent child, `ForgetPersistent` triggers child/dir callbacks, and unmount triggers root callback.

Dependencies/state: root/Linux required for cache drop; uses lookup counts, persistent inodes, and bridge maps.

Risks/test signals: strong lifecycle coverage but environment-sensitive. Timing around FORGET processing is acknowledged with sleeps.
<!-- END_FILE_RESEARCH: sources/user-network-fs/go-fuse/fs/forget_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/go-fuse/fs/idmapped_mount_test.go -->
# sources/user-network-fs/go-fuse/fs/idmapped_mount_test.go

Purpose: Linux test for FUSE idmapped mount support.

Important functions: `TestIDMappedMount` requires root/CAP_SYS_ADMIN, creates a test case with idmapped mount enabled, checks kernel `CAP_ALLOW_IDMAP`, creates a user namespace fd via `usernsFD(offset)`, clones and applies idmap attributes with `idMapMount`, then verifies UID/GID are shifted by offset. `idMapMount` uses `OpenTree`, `MountSetattr`, and `MoveMount`. `usernsFD` starts a sleeping process in a new user namespace with UID/GID maps and opens `/proc/<pid>/ns/user`.

State/dependencies: Linux-only, root, user namespaces, modern mount API.

Risks/test signals: high-value but highly environment-sensitive; skips when capability/kernel support is missing.
<!-- END_FILE_RESEARCH: sources/user-network-fs/go-fuse/fs/idmapped_mount_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/go-fuse/fs/inmemory_example_test.go -->
# sources/user-network-fs/go-fuse/fs/inmemory_example_test.go

Purpose: example of constructing a static in-memory filesystem with persistent inodes.

Important types/functions: global `files` maps paths to content; `inMemoryFS.OnAdd` walks path components, creates persistent directory inodes, creates `fs.MemRegularFile` leaves, and attaches children. `Example` mounts the root with debug enabled and waits.

State/dependencies: all file data persists in memory for the lifetime of the mount; no backing disk except temporary mount directory.

Integration/risks: demonstrates `NodeOnAdder`, `NewPersistentInode`, `AddChild`, and `MemRegularFile`. Risks are memory growth for large static trees and lack of cleanup beyond unmount. Build/example execution is the test signal.
<!-- END_FILE_RESEARCH: sources/user-network-fs/go-fuse/fs/inmemory_example_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/go-fuse/fs/inode.go -->
# sources/user-network-fs/go-fuse/fs/inode.go

Purpose: defines the in-memory inode model, stable attributes, tree links, locking helpers, lifecycle/removal, and cache notification methods.

Important APIs/types/functions: `StableAttr` with immutable mode/ino/gen and `Reserved`; `Inode` fields for ops, bridge, node ID, open files, backing IDs, persistent flag, change counter, lookup count, children, and parents; locking helpers `lockNodes`; lifecycle `NewInode`, `NewPersistentInode`, `ForgetPersistent`, `removeRef`; tree operations `GetChild`, `AddChild`, `RmChild`, `MvChild`, `ExchangeChild`, `Path`; notification/cache APIs `NotifyEntry`, `NotifyPrune`, `NotifyDelete`, `NotifyContent`, `WriteCache`, `ReadCache`.

Control flow/state: inode liveness depends on lookup count, persistence, children, and parents. Lock ordering by address prevents deadlocks for multi-inode operations. Removal can cascade to unused parents and call `OnForget`.

Risks/test signals: concurrency and lifecycle correctness are critical. Risks include stale paths for orphaned nodes, parent selection for hard links, change-counter retry logic, and notification server availability. Tests cover `IsDir`, parent storage, forget callbacks, rename/exchange, deleted paths, and cache notifications.
<!-- END_FILE_RESEARCH: sources/user-network-fs/go-fuse/fs/inode.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/go-fuse/fs/inode_children.go -->
# sources/user-network-fs/go-fuse/fs/inode_children.go

Purpose: deterministic child map for directory inodes.

Important types/functions: `childEntry`; `inodeChildren` stores `childrenMap` name-to-index plus insertion-ordered `children` slice. `set` adds/replaces children, compacts when slice capacity is exhausted, updates parent and child change counters, and records parent links. `del` removes child mapping and parent link. `list` returns entries in deterministic insertion order; `toMap` returns a copy.

Control flow/state: deleted slots remain until compaction; ordering stability supports directory offsets and avoids cache corruption from randomized map iteration.

Dependencies/integration: used by `Inode` tree operations and bridge fallback readdir. Risks include offset stability after mutation, compaction timing, and parent link consistency. Directory and inode tests exercise this indirectly.
<!-- END_FILE_RESEARCH: sources/user-network-fs/go-fuse/fs/inode_children.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/go-fuse/fs/inode_parents.go -->
# sources/user-network-fs/go-fuse/fs/inode_parents.go

Purpose: tracks one or more parent directory/name links for an inode, supporting hard links and path reconstruction.

Important types/functions: `inodeParents` stores a `newest` parent plus an `other` map. `add` keeps the most recently added parent as newest and avoids duplicates; `get` returns newest; `all` returns every known parent; `delete` removes a parent and promotes an arbitrary other parent when needed; `clear` removes all parents; `count` reports cardinality. `parentData` holds name and parent inode.

Control flow/state: no internal locking; callers must hold appropriate inode locks.

Integration/risks: used by `Inode.Path`, child set/delete, directory single-parent enforcement, and removal cascading. Risks include nondeterministic parent promotion from map iteration and caller lock misuse. `inode_parents_test.go` covers counts and newest behavior.
<!-- END_FILE_RESEARCH: sources/user-network-fs/go-fuse/fs/inode_parents.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/go-fuse/fs/inode_parents_test.go -->
# sources/user-network-fs/go-fuse/fs/inode_parents_test.go

Purpose: unit tests for `inodeParents` bookkeeping.

Important test flow: starts with an empty store and verifies count zero and `all()==nil`; adds five distinct `parentData` values and checks count increments and `get` returns the last added; re-adds duplicates and verifies count remains stable while newest changes; finally checks `all` length matches expected count.

State/dependencies: pure in-memory test with local `Inode` values; no FUSE mount.

Risks/test signals: covers add/newest/count/all behavior but not deletion, clear, or nondeterministic promotion after deleting newest. It is a fast regression test for hard-link parent tracking basics.
<!-- END_FILE_RESEARCH: sources/user-network-fs/go-fuse/fs/inode_parents_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/go-fuse/fs/inode_test.go -->
# sources/user-network-fs/go-fuse/fs/inode_test.go

Purpose: unit test for `Inode.IsDir`.

Important test flow: iterates over standard `syscall.S_IF*` file type modes and asserts only `S_IFDIR` returns true.

State/dependencies: mutates a local `Inode.stableAttr.Mode`; no mount or external state.

Risks/test signals: narrow but useful guard that `IsDir` depends on file type bits rather than permissions. Broader inode behavior is covered in bridge, forget, loopback, and parent tests.
<!-- END_FILE_RESEARCH: sources/user-network-fs/go-fuse/fs/inode_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/go-fuse/fs/interrupt_test.go -->
# sources/user-network-fs/go-fuse/fs/interrupt_test.go

Purpose: verifies kernel interrupt/cancellation can reach a blocked `Open` operation.

Important types/functions: `interruptRoot.Lookup` exposes a `file` inode; `interruptOps.Open` waits either for 100ms and returns `EIO` or for context cancellation and returns `EINTR` while setting `interrupted`; `TestInterrupt` runs `cat` on the file, kills it shortly after start, unmounts, and asserts interruption was observed.

State/dependencies: real FUSE mount and process signaling.

Risks/test signals: valuable for context cancellation semantics but timing-sensitive. The test comment notes it is also investigative for INTERRUPT opcode handling.
<!-- END_FILE_RESEARCH: sources/user-network-fs/go-fuse/fs/interrupt_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/go-fuse/fs/ioctl_test.go -->
# sources/user-network-fs/go-fuse/fs/ioctl_test.go

Purpose: tests FUSE ioctl dispatch into a node implementation.

Important types/functions: `ioctlNode.Ioctl` copies input bytes plus one into output and returns result code `1515`; `TestIoctl` opens the mounted root, builds a read/write ioctl command with internal `ioctl.New`, calls raw `SYS_IOCTL` with a byte buffer, and verifies result and transformed buffer.

State/dependencies: real FUSE mount, unsafe pointer to buffer, ioctl command encoding.

Risks/test signals: covers input/output buffer wiring and result propagation. It is Linux/Unix syscall-sensitive and assumes non-empty buffers for unsafe pointer use.
<!-- END_FILE_RESEARCH: sources/user-network-fs/go-fuse/fs/ioctl_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/go-fuse/fs/linearraid_linux_example_test.go -->
# sources/user-network-fs/go-fuse/fs/linearraid_linux_example_test.go

Purpose: Linux example demonstrating zero-copy pipe-backed reads by assembling one virtual file from chunk files.

Important types/functions: `linearRaidNode` implements `NodeGetattrer`, `NodeOpener`, and `NodeReader`; `Read` clamps requested range, obtains a `splice.Pair`, grows it, opens each chunk, loads segments with `LoadFromAt`, and returns `fuse.ReadResultPipe`. `Example_linearRaid` creates chunk files with known content, mounts a root with persistent `raid`, reads it, and expects "content matches".

State/dependencies: chunk files persist in temp dir during example; splice pipe resources are returned with `splice.Done` unless transferred.

Risks/test signals: covers pipe `ReadResult` cleanup and multi-chunk boundary logic. Risks include fd leaks on early loop errors and Linux-only splice behavior. The example has output assertion.
<!-- END_FILE_RESEARCH: sources/user-network-fs/go-fuse/fs/linearraid_linux_example_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/go-fuse/fs/loopback.go -->
# sources/user-network-fs/go-fuse/fs/loopback.go

Purpose: implements the main loopback filesystem node that delegates FUSE operations to an underlying POSIX filesystem.

Important APIs/types/functions: `LoopbackRoot` holds backing path, device, optional `NewNode`, and root node; `LoopbackNode` embeds `Inode` and implements statfs, lookup, mknod, mkdir, rmdir, unlink, rename, create, symlink, link, readlink, open, opendir/readdir, getattr, setattr, xattrs, copy_file_range, and root construction. `idFromStat` combines device/inode into stable attrs. `path`/`relativePath` map inodes to backing paths.

Control flow/state: persistent state is the backing filesystem. New children are created from backing `stat` data. Root-owned paths and cross-root renames are guarded. Root preserves caller owner when running as root.

Dependencies/integration: uses syscalls, `openat.OpenSymlinkAware`, `renameat`, unix xattrs, and `LoopbackFile`. Risks include TOCTOU around paths, symlink safety, inode reuse, path lookup for orphaned nodes, ownership/chown failures ignored in create paths, and platform-specific copy/statx behavior. Tests cover rename exchange, non-root loopback subtree, xattrs, copy, mknod, ioctl, and direct mount.
<!-- END_FILE_RESEARCH: sources/user-network-fs/go-fuse/fs/loopback.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/go-fuse/fs/loopback_darwin.go -->
# sources/user-network-fs/go-fuse/fs/loopback_darwin.go

Purpose: Darwin-specific loopback helpers.

Important APIs: defines `unix_UTIME_OMIT` fallback, `timeToTimeval` conversion for pre-1970-safe timeval creation, `doCopyFileRange` returning `ENOSYS`, and `intDev` converting device numbers to int.

Control flow/state: no retained state; platform adapter only.

Dependencies/integration: selected on Darwin; used by loopback setattr and copy-file-range code paths. Risks include unavailable copy_file_range on Darwin and timestamp compatibility. Cross-build is the main CI signal; runtime coverage requires macOS FUSE tests.
<!-- END_FILE_RESEARCH: sources/user-network-fs/go-fuse/fs/loopback_darwin.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/go-fuse/fs/loopback_freebsd.go -->
# sources/user-network-fs/go-fuse/fs/loopback_freebsd.go

Purpose: FreeBSD-specific loopback helpers for timestamps, copy-file-range, device conversion, and xattr listing format conversion.

Important functions: `doCopyFileRange` manually invokes syscall 569; `intDev` returns `uint64`; `rebuildAttrBuf` prefixes FreeBSD xattr names with `user.` and null-terminates them; `LoopbackNode.Listxattr` calls `unix.Llistxattr`, parses names, rebuilds Linux-flavored listxattr output, and copies into dest when provided.

State/dependencies: no persistent state beyond backing filesystem xattrs.

Integration/risks: bridges FreeBSD syscall behavior to Linux FUSE expectations. Risks include syscall constant drift, namespace mapping assumptions, truncated-copy semantics, and platform differences in xattr permissions. FreeBSD cross-build covers compilation; runtime tests would be needed for xattr behavior.
<!-- END_FILE_RESEARCH: sources/user-network-fs/go-fuse/fs/loopback_freebsd.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/go-fuse/fs/loopback_linux.go -->
# sources/user-network-fs/go-fuse/fs/loopback_linux.go

Purpose: Linux-specific loopback helpers.

Important APIs: `unix_UTIME_OMIT` alias; `doCopyFileRange` uses `unix.CopyFileRange`; `intDev` returns int; `LoopbackNode.Statx` dispatches to file-handle `FileStatxer` when present, otherwise calls `unix.Statx` on the backing path and fills `fuse.StatxOut`.

Control flow/state: no independent state; operates on backing filesystem path or file handle.

Dependencies/integration: used by `LoopbackNode.CopyFileRange`, `Setattr`, and bridge statx. Risks include path-based statx following semantics controlled by flags, copy_file_range partial-copy behavior, and kernel capability differences. Linux tests cover copy file range and statx paths elsewhere in the suite.
<!-- END_FILE_RESEARCH: sources/user-network-fs/go-fuse/fs/loopback_linux.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/go-fuse/fs/loopback_linux_test.go -->
# sources/user-network-fs/go-fuse/fs/loopback_linux_test.go

Purpose: Linux-specific loopback integration tests for rename flags, xattrs, copy_file_range, mount races, direct/id options, ioctl passthrough, and mknod.

Important tests/functions: `TestRenameNoOverwrite`, `TestRenameWhiteOut`, `TestXAttrSymlink`, `TestCopyFileRange`, `waitMount` helpers for `/proc/self/mounts`, `TestParallelDiropsHang`, `TestRoMount`, `TestDirectMount`, `TestIoctlLoopbackFile`, `TestIoctlLoopbackDir`, and `TestMknod`.

State/dependencies: real backing dirs and FUSE mounts; Linux syscalls `Renameat2`, `CopyFileRange`, ioctl flags, `/proc`, `/sys/class/bdi`, and sometimes root/direct mount capability.

Risks/test signals: strong coverage of Linux-specific kernel integration. Environment sensitivity is high: kernel version, permissions, filesystem support for noatime/xattrs, and FUSE capabilities can affect results.
<!-- END_FILE_RESEARCH: sources/user-network-fs/go-fuse/fs/loopback_linux_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/go-fuse/fs/loopback_test.go -->
# sources/user-network-fs/go-fuse/fs/loopback_test.go

Purpose: cross-platform loopback tests for rename exchange and using loopback roots below a larger synthetic root.

Important tests: `TestRenameExchange` creates two files, performs `RENAME_EXCHANGE`, verifies backing stat metadata swaps, and checks go-fuse inode tree stable attrs update for root and nested paths. `TestLoopbackNonRoot` mounts a synthetic root containing two different loopback roots, verifies reads through a submount, expects `EXDEV` for cross-root renames, and succeeds for rename within the same loopback root.

State/dependencies: real temp backing dirs, FUSE mounts, renameat helper, syscall stats.

Risks/test signals: covers hard namespace integration between `LoopbackNode` and in-memory parent roots. Rename exchange support may be skipped if unsupported.
<!-- END_FILE_RESEARCH: sources/user-network-fs/go-fuse/fs/loopback_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/go-fuse/fs/loopback_unix.go -->
# sources/user-network-fs/go-fuse/fs/loopback_unix.go

Purpose: non-FreeBSD loopback xattr-list implementation.

Important API: `LoopbackNode.Listxattr` calls `unix.Llistxattr(n.path(), dest)` and returns size/error converted to `syscall.Errno`.

Control flow/state: no retained state; delegates to backing filesystem.

Dependencies/integration: build-tagged `!freebsd`, used on Linux/Darwin where Linux-style listxattr data is acceptable to the rest of the stack. Risks are platform differences under the broad build tag, especially Darwin xattr format expectations. Tests cover Linux symlink xattr behavior; additional platform-specific runtime tests would help.
<!-- END_FILE_RESEARCH: sources/user-network-fs/go-fuse/fs/loopback_unix.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/go-fuse/fs/maxwrite_test.go -->
# sources/user-network-fs/go-fuse/fs/maxwrite_test.go

Purpose: Linux test for mount `MaxWrite`, `MaxReadAhead`, and `max_read` effects on observed kernel request sizes.

Important types/functions: `maxWriteTestRoot` records largest read/write sizes; `maxWriteTestNode` reports a 1 GiB file and returns `maxWriteTestFH`; the file handle records request sizes in `Read`/`Write`. `TestMaxWrite` iterates many mount option combinations, verifies `/sys/class/bdi/.../read_ahead_kb`, performs 2 MiB direct and buffered I/O, and checks observed sizes against kernel capabilities. `bdiReadahead` reads sysfs.

State/dependencies: Linux-only, real FUSE mount, O_DIRECT, sysfs, kernel capability flags.

Risks/test signals: valuable kernel negotiation coverage but environment-sensitive. It accounts for pre-4.20 lack of `CAP_MAX_PAGES`.
<!-- END_FILE_RESEARCH: sources/user-network-fs/go-fuse/fs/maxwrite_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/go-fuse/fs/mem.go -->
# sources/user-network-fs/go-fuse/fs/mem.go

Purpose: simple in-memory file and symlink node implementations for examples/tests/static filesystems.

Important types/functions: `MemRegularFile` embeds `Inode`, owns `Data []byte` and `fuse.Attr` under mutex, and implements open/read/write/getattr/setattr/flush/allocate. `Open` returns `FOPEN_KEEP_CACHE`; `Write` grows data and copies bytes; `Setattr` resizes on size changes; `Allocate` grows capacity/data and respects platform `keepSizeMode`. `MemSymlink` stores attrs and symlink target bytes, implementing `Readlink` and `Getattr`.

State/persistence: all content is process memory; data is lost on unmount/process exit.

Risks/test signals: `Setattr` slicing to larger size without ensuring capacity can panic if asked to grow; `Read` assumes non-negative offset. Used heavily by examples and benchmarks, with indirect tests through in-memory filesystems.
<!-- END_FILE_RESEARCH: sources/user-network-fs/go-fuse/fs/mem.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/go-fuse/fs/mem_linux.go -->
# sources/user-network-fs/go-fuse/fs/mem_linux.go

Purpose: Linux-specific helper for in-memory fallocate behavior.

Important API: `keepSizeMode(mode uint32) bool` returns whether `unix.FALLOC_FL_KEEP_SIZE` is set.

Control flow/state: no state; used by `MemRegularFile.Allocate` to decide whether allocation should grow capacity without changing visible size.

Dependencies/integration: Linux build uses `golang.org/x/sys/unix`. Risks are minimal; non-Linux implementations must provide compatible behavior. Test signal is indirect through fallocate/memory-file behavior.
<!-- END_FILE_RESEARCH: sources/user-network-fs/go-fuse/fs/mem_linux.go -->
