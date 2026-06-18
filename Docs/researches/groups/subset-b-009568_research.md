# subset-b-009568 Research

Grouped research for the exact source set assigned to `subset-b-009568`. Each section is source-tree aligned and wrapped for deterministic reconciliation into `Docs/researches/<source_path>_research.md`.

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/blobfuse2/internal/handlemap/handle_map_test.go -->
# sources/user-network-fs/blobfuse2/internal/handlemap/handle_map_test.go

## Purpose
Unit test suite for the handle map package. It verifies handle construction, handle flag helpers, auxiliary value storage, cache object attachment, global handle registration, lookup, and deletion.

## Important APIs, Types, and Functions
`HandleMapSuite` is a `testify/suite` test fixture with an assertion helper. `TestNewHandle` validates `NewHandle` default state: `InvalidHandleID` and preserved path. `TestHandleFlags` exercises `Dirty`, `Fsynced`, `Cached`, `SetFileObject`, `GetFileObject`, `SetValue`, `GetValue`, `RemoveValue`, and `Cleanup`. `TestHandleMap` covers `GetHandles`, `Add`, `Load`, `Delete`, `CreateCacheObject`, and `Store`. `TestUnMountCommand` is the suite entry point despite the misleading name.

## Control Flow and State
Each test creates fresh handles but uses package-level handle-map state through `Add`, `Load`, and `Delete`. The suite checks that inserted handles receive nonzero IDs, can be loaded by ID, and disappear after deletion. Per-handle key/value state is populated and cleared via `Cleanup`; file object state is stored as an `*os.File` pointer.

## Dependencies and Integration Points
The tests depend on `github.com/stretchr/testify/assert` and `github.com/stretchr/testify/suite`. They integrate with the production `handlemap` package rather than mocks, so failures signal behavioral drift in the in-memory handle registry used by FUSE file operations.

## Risks and Edge Cases
The test assumes global handle-map state is clean enough between tests. It does not cover concurrent add/load/delete behavior, ID overflow, duplicate deletion, or cleanup interaction with real cache objects. The `TestUnMountCommand` name can mislead test selection and reporting.

## Test Signals
Passing tests show basic handle lifecycle and flag/value helpers work. Missing signals include race safety, cache object semantics beyond non-nil creation, and behavior under many handles.
<!-- END_FILE_RESEARCH: sources/user-network-fs/blobfuse2/internal/handlemap/handle_map_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/blobfuse2/internal/mock_component.go -->
# sources/user-network-fs/blobfuse2/internal/mock_component.go

## Purpose
Generated GoMock implementation of the `internal.Component` interface for unit tests. It lets tests assert and stub calls across the Blobfuse2 component pipeline and file-system operation surface.

## Important APIs, Types, and Functions
`MockComponent` holds a `gomock.Controller` and `MockComponentMockRecorder`. `NewMockComponent` constructs the mock, and `EXPECT` exposes recorder methods. The mock implements component lifecycle (`Configure`, `GenConfig`, `Start`, `Stop`, `Name`, `SetName`, `Priority`, `NextComponent`, `SetNextComponent`) and filesystem operations including directory, file, symlink, chmod/chown, stats, block-list, stage, and commit methods. Return types mirror production contracts such as `*handlemap.Handle`, `*ObjAttr`, `*common.BlockOffsetList`, `*CommittedBlockList`, `*syscall.Statfs_t`, and error values.

## Control Flow and State
Most methods are thin wrappers around `m.ctrl.Call` with type assertions for returned values. Recorder methods call `RecordCallWithMethodType` so test code can set expectations. `RenameFile` mutates `arg0.DstAttr` timestamps after invoking the mock call when a destination attribute is present. `GenConfig` is a manual stub returning an empty string rather than a mocked expectation.

## Dependencies and Integration Points
Depends on `github.com/golang/mock/gomock`, `context`, `syscall`, `time`, Blobfuse2 `common`, `handlemap`, and internal option/attribute types. It is coupled to the exact `Component` interface; interface changes require regenerating or editing this file.

## Risks and Edge Cases
Because this is generated code with manual additions, drift risk is high when `Component` changes. Several recorder methods for `GetCommittedBlockList`, `StageData`, and `CommitData` pass `reflect.TypeOf((*MockComponent)(nil).TruncateFile)` instead of their own methods, which can make gomock diagnostics or method type checks misleading. `StreamDir` discards the mocked string continuation/token and always returns `""`; tests relying on paged directory streaming can get false confidence. `GenConfig` cannot be expected through gomock.

## Test Signals
The file itself is test support. Good downstream tests using it can validate component chaining, option propagation, and error paths without real storage. Weak signals arise if tests overfit to mock behavior that differs from production, especially timestamp mutation and stream-token handling.
<!-- END_FILE_RESEARCH: sources/user-network-fs/blobfuse2/internal/mock_component.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/blobfuse2/internal/pipeline.go -->
# sources/user-network-fs/blobfuse2/internal/pipeline.go

## Purpose
Builds and controls an ordered chain of Blobfuse2 components. It converts configured component names into initialized `Component` instances, validates priority ordering, links them, and starts/stops them in lifecycle-safe order.

## Important APIs, Types, and Functions
`Pipeline` stores `components []Component` and `Header Component`. `NewComponent` is the constructor signature registered by components. `registeredComponents` maps component names to constructors. `GetComponent` returns a fresh component by name. `NewPipeline` configures components from string names. `Create` links components through `SetNextComponent`. `Start` calls `Create` and starts components from tail to head. `Stop` stops components from head to tail. `AddComponent` registers constructors. `init` initializes the registry.

## Control Flow and State
`NewPipeline` begins with the producer priority as the last accepted priority. For each configured name, it maps legacy `"stream"` to `"block_cache"` and sets `common.IsStream = true`, looks up the constructor, calls `Configure(isParent)`, and rejects components whose priority increases relative to the previous component. Successfully configured components are retained in order. `Create` sets `Header` to the first component and links every component to its successor. `Start` starts downstream components first; on a start error it stops already-started downstream components and returns `errors.Join` of all lifecycle errors. `Stop` attempts every component and joins errors.

## Dependencies and Integration Points
Depends on the internal `Component` interface and `ComponentPriority` ordering, `common.IsStream`, and `common/log` for diagnostics. It is central to config-driven assembly for libfuse, caches, storage backends, loopbackfs, xload, and other registered components.

## Risks and Edge Cases
`Create` assumes at least one component; an empty component list would panic. `registeredComponents` is global and unsynchronized, so concurrent registration or tests sharing names can interfere. `"stream"` is only special-cased in `NewPipeline`; callers of `GetComponent("stream")` do not get the alias behavior. Priority comparison relies on the numeric ordering semantics of `ComponentPriority`. `Start` continues its outer loop after an error, so multiple components can be started/stopped after an initial failure; this is intentional for error aggregation but can surprise tests.

## Test Signals
`pipeline_test.go` covers valid construction, invalid ordering, unknown components, lifecycle start/stop, and stream-to-block-cache mapping. Additional useful tests would cover empty pipelines, configure/start/stop error aggregation, and registry isolation.
<!-- END_FILE_RESEARCH: sources/user-network-fs/blobfuse2/internal/pipeline.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/blobfuse2/internal/pipeline_test.go -->
# sources/user-network-fs/blobfuse2/internal/pipeline_test.go

## Purpose
Unit tests for pipeline construction and basic lifecycle behavior using minimal in-package fake components.

## Important APIs, Types, and Functions
`ComponentA`, `ComponentB`, and `ComponentC` embed `BaseComponent` and return producer, mid, and consumer priorities. `ComponentStream` and `ComponentBlockCache` provide named test components for alias behavior. `pipelineTestSuite.SetupTest` registers these components through `AddComponent`. Tests cover `NewPipeline`, invalid priority ordering, unknown names, `Start`, `Stop`, and stream aliasing.

## Control Flow and State
The suite mutates the global component registry on each test setup. Valid pipelines use `ComponentA` then `ComponentB`. Invalid order uses `ComponentC` then `ComponentA` and asserts an "is out of order" error. Lifecycle test builds a two-component pipeline, starts it with `context.Background`, then stops it. Stream alias test registers both `"stream"` and `"block_cache"` and expects `NewPipeline([]string{"stream"})` to produce a component named `"block_cache"`.

## Dependencies and Integration Points
Uses `testify/suite` and `testify/assert`. The fake components rely on `BaseComponent` default implementations for configuration/start/stop/name behavior, so the suite indirectly tests compatibility between `Pipeline` and base component defaults.

## Risks and Edge Cases
The global registry is not cleared, so tests can be order-dependent if other package tests register the same names. It does not mock or assert `SetNextComponent` wiring directly. Error aggregation paths are not covered because fake components do not fail configure/start/stop. `print(p.components[0].Name())` is noisy in test output.

## Test Signals
Passing tests show the most common pipeline configuration path works and the legacy `stream` alias is preserved. Missing signals include empty config handling, duplicate names, lifecycle cleanup on partial start failure, and multiple stop errors.
<!-- END_FILE_RESEARCH: sources/user-network-fs/blobfuse2/internal/pipeline_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/blobfuse2/internal/stats_manager/stats_common.go -->
# sources/user-network-fs/blobfuse2/internal/stats_manager/stats_common.go

## Purpose
Defines the operation labels used by the stats manager for component statistic updates.

## Important APIs, Types, and Functions
Constants `Increment`, `Decrement`, and `Replace` are string operation names consumed by `StatsCollector.UpdateStats` and interpreted by `statsDumper`.

## Control Flow and State
No runtime flow or state is present. The constants form a small shared contract between components producing stats and the stats manager consuming them.

## Dependencies and Integration Points
The package is `stats_manager`. Components should use these constants rather than hard-coded strings when reporting counters or gauges.

## Risks and Edge Cases
Because the constants are strings, callers can still pass invalid operations; `stats_manager.go` logs and ignores unknown operations. There is no type-level enum enforcement.

## Test Signals
Coverage comes indirectly through stats manager tests or component tests that call `UpdateStats`. This file has no standalone test surface.
<!-- END_FILE_RESEARCH: sources/user-network-fs/blobfuse2/internal/stats_manager/stats_common.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/blobfuse2/internal/stats_manager/stats_manager.go -->
# sources/user-network-fs/blobfuse2/internal/stats_manager/stats_manager.go

## Purpose
Implements Blobfuse2 component stats/event collection for the health monitor path. It accepts asynchronous component events and counters, writes event records to a transfer named pipe, and responds to polling-pipe requests by sending changed aggregate stats.

## Important APIs, Types, and Functions
`StatsCollector` owns a buffered channel, worker wait group, and component index. `PipeMsg` is the JSON payload written to the monitor pipe. `Events`, `Stats`, and `ChannelMsg` represent internal event/stat messages. `NewStatsCollector` registers a component stats slot and starts goroutines when `common.MonitorBfs()` is enabled. `PushEvents` sends per-operation event records. `UpdateStats` sends aggregate stat updates. `statsDumper` consumes collector messages, writes events, and updates aggregate stats. `statsPolling` listens on `common.PollingPipe` and writes changed component stats to `common.TransferPipe`. `createPipe` creates FIFOs. `disableMonitoring` clears `common.EnableMonitoring`.

## Control Flow and State
Global `stMgrOpt` stores `statsList`, component last-transfer timestamps, `pollStarted`, and three mutexes. A collector appends a `PipeMsg` slot under `statsMtx`, records its component index, then starts `statsDumper`; the first collector also starts `statsPolling`. Events are copied into a new map before channeling. If the channel is full, the oldest message is dropped. `statsDumper` creates and opens the transfer pipe, marshals event messages immediately, and applies `Increment`, `Decrement`, or `Replace` operations to the component's aggregate value map. `statsPolling` waits for lines containing `"Poll at"`, then sends only components whose timestamp changed since the last poll.

## Dependencies and Integration Points
Depends on `common.MonitorBfs`, `common.TransferPipe`, `common.PollingPipe`, `common.EnableMonitoring`, and `common/log`. Integrates with external `bfusemon`/health monitor processes via named pipes and JSON lines. Component code integrates through `NewStatsCollector`, `PushEvents`, and `UpdateStats`.

## Risks and Edge Cases
Opening a FIFO for write can block if no reader exists; both `statsDumper` and `statsPolling` open `TransferPipe` as write-only. The channel-full path uses `len(sc.channel) == cap(sc.channel)` then receives one item, which is not atomic with other goroutines and can block if the channel is drained concurrently. `UpdateStats` assumes increment/decrement values and existing numeric values are `int64`; wrong types panic. `Destroy` closes the channel but callers can still panic if they push after destroy. `pollStarted` is never reset, so once polling exits due to an error, later collectors will not restart it. Monitoring is globally disabled on many pipe errors.

## Test Signals
This file needs integration tests with FIFOs or abstracted pipe writers to validate event JSON, stat aggregation, poll filtering, and failure behavior. Race testing would be valuable because it combines channels, global state, and mutexes.
<!-- END_FILE_RESEARCH: sources/user-network-fs/blobfuse2/internal/stats_manager/stats_manager.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/blobfuse2/main.go -->
# sources/user-network-fs/blobfuse2/main.go

## Purpose
Program entrypoint for the Blobfuse2 binary. It delegates all command-line behavior to the `cmd` package.

## Important APIs, Types, and Functions
`main` calls `cmd.Execute()` and discards its returned error. The file also contains a `go:generate` directive invoking `./cmd/componentGenerator.sh $NAME`.

## Control Flow and State
There is no local state. Startup flow is a single call into Cobra/command orchestration in `github.com/Azure/azure-storage-fuse/v2/cmd`.

## Dependencies and Integration Points
The executable is coupled to the `cmd` package for parsing, mount/unmount/subcommand dispatch, config initialization, logging, and process exit semantics. Go generation integrates with component scaffolding.

## Risks and Edge Cases
Discarding `cmd.Execute()` errors means this entrypoint relies on `cmd.Execute` to log, exit, or otherwise handle failures. If command execution changes to return errors without exiting, the binary could exit successfully after failure.

## Test Signals
`main_test.go` invokes `main` only when running as `blobfuse2.test`, primarily for coverage. Behavior is otherwise covered by command package tests.
<!-- END_FILE_RESEARCH: sources/user-network-fs/blobfuse2/main.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/blobfuse2/main_test.go -->
# sources/user-network-fs/blobfuse2/main_test.go

## Purpose
Coverage-oriented test for the binary entrypoint, excluded under the `unittest` build tag.

## Important APIs, Types, and Functions
`TestMain` filters `os.Args` to remove Go test flags, then invokes `main()` only if `os.Args[0]` contains `blobfuse2.test`; otherwise it records a test error.

## Control Flow and State
The test mutates global `os.Args`, which affects any later code in the same process. It uses the test binary name as a guard before invoking the real command entrypoint.

## Dependencies and Integration Points
Depends on standard `os`, `strings`, and `testing`. It integrates with the top-level `main` and transitively with the full command package, so it can trigger command initialization side effects.

## Risks and Edge Cases
Calling `main()` in a test can be brittle because command parsing may expect real CLI arguments, environment variables, or mount privileges. Mutating `os.Args` is process-global. The build tag keeps it out of unit-test mode, but coverage runs can still exercise broad startup behavior.

## Test Signals
Passing only indicates the test binary reached `main()` without failing this wrapper. It is not a focused assertion of CLI behavior.
<!-- END_FILE_RESEARCH: sources/user-network-fs/blobfuse2/main_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/blobfuse2/notices_fix.sh -->
# sources/user-network-fs/blobfuse2/notices_fix.sh

## Purpose
Shell utility that generates or updates the root `NOTICE` file from Go module dependencies listed in `go.sum`. It attempts to fetch third-party license text from common upstream locations and append missing notices.

## Important APIs, Types, and Functions
`dump_header` and `dump_footer` write fixed notice delimiters. `append_lic_to_notice` appends a dependency marker and `lic.tmp`. `download_and_dump` fetches a license URL with `wget`. `try_differ_names` tries `LICENSE`, `.txt`, and `.md`. `download_notice` contains host-specific rules for GitHub, Go package docs, gopkg.in, go-autorest, etcd, and other special cases. `generate_notices` walks `dependencies.lst`, reuses existing NOTICE entries, and fetches missing ones.

## Control Flow and State
The script creates `notice_tmp`, derives a sorted unique dependency list from `../go.sum`, copies the existing NOTICE without its footer if present, then loops through dependencies. Temporary files `lic.tmp`, `lic1.tmp`, `dependencies.lst`, and `notice.lst` live under `notice_tmp`. The final file is copied back to `../NOTICE`, and the temp directory is removed.

## Dependencies and Integration Points
Requires Bash, `wget`, `sed`, `grep`, `cut`, `head`, `diff`, `sort`, and network access to GitHub and pkg.go.dev. Integrates with release/compliance workflows and the repository `go.sum`.

## Risks and Edge Cases
The script assumes branch names `master` or `main` and common license filenames, so it can miss repositories with unusual layouts. It uses unquoted variables and command substitution heavily, so dependency names with unexpected characters can break commands. It fetches live network content and is not reproducible without pinning. It can append incomplete or HTML-parsed license content. It removes and recreates `notice_tmp` in the current directory.

## Test Signals
The final diff between `dependencies.lst` and notice markers is the main validation signal. Manual review remains required for failed fetches and license correctness.
<!-- END_FILE_RESEARCH: sources/user-network-fs/blobfuse2/notices_fix.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/blobfuse2/perf_testing/scripts/fio_bench.sh -->
# sources/user-network-fs/blobfuse2/perf_testing/scripts/fio_bench.sh

## Purpose
Performance harness that mounts Blobfuse2, runs FIO read/write jobs or a custom file-cache read test, captures bandwidth/latency summaries, and records network usage.

## Important APIs, Types, and Functions
Inputs are `<mount_dir> <test_name> <cache_mode>`. `cleanup_mount` unmounts all Blobfuse2 mounts. `mount_blobfuse` clears mount/cache directories and invokes `blobfuse2 mount` with `./config.yaml`. `run_fio_job` drops kernel caches, records `/sys/class/net/$INTERFACE` byte counters, runs `fio`, and emits summary JSON through `jq`. `run_test_suite` remounts per `.fio` file. `run_filecache_read_test` creates a 100GB file, remounts cold, reads with `dd iflag=direct`, and writes JSON summaries.

## Control Flow and State
The script validates arguments, creates an output directory named after the test type, performs an initial cleanup, selects write/read flow, and finally aggregates `*_bandwidth_summary.json` and `*_latency_summary.json` into result arrays. It mutates the mount directory, `/mnt/tempcache`, kernel page cache, and output directories.

## Dependencies and Integration Points
Requires `blobfuse2`, `fio`, `jq`, `bc`, `dd`, `timeout`, `sudo`, Linux `/proc` and `/sys`, and a `config.yaml` in the working directory. It integrates with `perf_testing/config/read` and `perf_testing/config/write` job files.

## Risks and Edge Cases
`set -e` makes failures stop the run, but some cleanup is best-effort. `INTERFACE` is hard-coded to `eth0`, which is wrong on many hosts. The mount cleanup uses `blobfuse2 unmount all`, affecting unrelated mounts. It deletes all contents under the mount directory. File-cache read creates a 100GB object, requiring substantial storage. The positional `cache_mode` is validated only indirectly for the file-cache branch.

## Test Signals
Outputs are FIO JSON files, per-job bandwidth/latency summary JSON, final aggregate JSON, and printed network stats. These are performance signals, not correctness tests.
<!-- END_FILE_RESEARCH: sources/user-network-fs/blobfuse2/perf_testing/scripts/fio_bench.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/blobfuse2/perf_testing/scripts/highspeed_create.py -->
# sources/user-network-fs/blobfuse2/perf_testing/scripts/highspeed_create.py

## Purpose
Creates multiple 20GB zero-filled files in parallel on a target folder and reports aggregate create/write throughput.

## Important APIs, Types, and Functions
`create_file(file_index, folder)` builds a timestamped filename and runs `dd if=/dev/zero bs=16M count=1280 oflag=direct`. `main(folder, num_files)` ensures the folder exists, runs work through a `ThreadPoolExecutor` sized to CPU count, and prints a JSON record.

## Control Flow and State
Each worker uses an external `dd` process and records elapsed time. The parent computes total time and total data as `num_files * 20` GB. Files are left in the target folder.

## Dependencies and Integration Points
Depends on Python standard libraries plus Unix `dd`. Intended for mounted Blobfuse2 paths or local disks under performance testing.

## Risks and Edge Cases
`subprocess.run(..., shell=True)` uses interpolated paths and is unsafe for untrusted folder names. Return codes are ignored, so failed `dd` processes still contribute to reported throughput. `oflag=direct` may fail depending on filesystem alignment/support. The JSON name says `create_10_20GB_file` regardless of `num_files`.

## Test Signals
Single JSON line reports total time, speed, and unit. It does not validate file sizes or failures.
<!-- END_FILE_RESEARCH: sources/user-network-fs/blobfuse2/perf_testing/scripts/highspeed_create.py -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/blobfuse2/perf_testing/scripts/highspeed_read.py -->
# sources/user-network-fs/blobfuse2/perf_testing/scripts/highspeed_read.py

## Purpose
Reads multiple files in parallel using `dd` to `/dev/null` and reports aggregate read throughput.

## Important APIs, Types, and Functions
`copy_file(src)` runs `dd if=<src> of=/dev/null bs=4M status=none`, then returns `os.path.getsize(src)`. `main(file_paths)` maps all input paths through a multiprocessing pool sized to CPU count and prints JSON throughput.

## Control Flow and State
The script expects file paths as command-line arguments. It starts all reads, sums known file sizes, divides by wall-clock time, and emits a JSON result named `read_10_20GB_file`.

## Dependencies and Integration Points
Depends on Python multiprocessing and Unix `dd`. Intended for reading files from Blobfuse2 mounts after creation by related performance scripts.

## Risks and Edge Cases
`Popen` stdout is read, but `dd` writes data to `/dev/null` and status to stderr, so the live byte counter is ineffective. Return code is not checked; `CalledProcessError` is never raised by `Popen` in this form. Failed reads can still count full file size. Very large file lists can spawn many processes.

## Test Signals
The JSON output is a performance estimate. It does not prove data integrity or verify `dd` success.
<!-- END_FILE_RESEARCH: sources/user-network-fs/blobfuse2/perf_testing/scripts/highspeed_read.py -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/blobfuse2/perf_testing/scripts/highspeed_write_nonzero.py -->
# sources/user-network-fs/blobfuse2/perf_testing/scripts/highspeed_write_nonzero.py

## Purpose
Copies a nonzero source file into multiple large target files in parallel to measure high-throughput write behavior with realistic data.

## Important APIs, Types, and Functions
`create_file_dd(file_index, folder, source_file, timestamp)` runs `dd if=<source_file> of=<target> bs=1G count=36 oflag=direct`, returning timing and throughput or an error string. `main(folder, num_files, source_file)` creates the folder, runs workers in a multiprocessing pool, and prints human-readable totals.

## Control Flow and State
The script creates timestamped `ddFile_*` outputs, waits for each async worker, filters successful results, and reports total data written, elapsed time, Gbps, and MiB/s. Files persist after completion.

## Dependencies and Integration Points
Depends on Unix `dd`, direct I/O support, Python multiprocessing, and a large readable source file. Used with Blobfuse2 mounted paths to stress upload paths.

## Risks and Edge Cases
Uses `shell=True` with unquoted interpolated paths. `bs=1G` with `oflag=direct` can fail on many systems or consume significant resources. Result tuple shape differs on failure and success, with positional indexing that is easy to break. It does not emit machine-readable JSON unlike related scripts.

## Test Signals
Printed throughput metrics indicate performance only for successful `dd` calls. There is no file-size or checksum validation.
<!-- END_FILE_RESEARCH: sources/user-network-fs/blobfuse2/perf_testing/scripts/highspeed_write_nonzero.py -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/blobfuse2/perf_testing/scripts/read.py -->
# sources/user-network-fs/blobfuse2/perf_testing/scripts/read.py

## Purpose
Simple sequential read benchmark for a file named `application_<size>.data` under a mount path.

## Important APIs, Types, and Functions
The script reads CLI args `mountpath` and `size`, opens the file in binary mode, reads 8MiB blocks until `bytes_read <= fileSize`, and prints timing/throughput JSON.

## Control Flow and State
It records open, read, close, and total wall-clock durations. It derives expected file size from integer GB input and accumulates bytes read from returned chunks.

## Dependencies and Integration Points
Uses Python standard libraries and expects the target file to have been created by `write.py` or an equivalent tool on a mounted Blobfuse2 path.

## Risks and Edge Cases
The loop condition `bytes_read <= fileSize` performs one extra read at EOF. If the file is shorter than expected, repeated empty reads can lead to an infinite loop because `bytes_read` stops increasing. There is no argument validation or exception handling.

## Test Signals
JSON output includes open/read/close/total times and MiB/s. It does not check content or guard against short files.
<!-- END_FILE_RESEARCH: sources/user-network-fs/blobfuse2/perf_testing/scripts/read.py -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/blobfuse2/perf_testing/scripts/rename.py -->
# sources/user-network-fs/blobfuse2/perf_testing/scripts/rename.py

## Purpose
Measures time to create and rename 5,000 1MiB files in a temporary folder.

## Important APIs, Types, and Functions
`create_folder` recreates the test folder. `create_files` writes zero-filled files. `rename_files` iterates directory entries and renames each file to `new_file_<i>.txt`. The script prints a JSON object with rename and create times.

## Control Flow and State
A timestamped folder under `./` is created, populated, renamed, removed, and summarized. The `output_file` variable is unused.

## Dependencies and Integration Points
Pure Python standard library. It is useful when run from a Blobfuse2 mount working directory to stress metadata-heavy create/rename operations.

## Risks and Edge Cases
The base folder is always current working directory, so accidental execution outside a test area writes 5GB locally. It is single-threaded and does not verify rename results before cleanup. Directory iteration order is filesystem-dependent but not semantically important.

## Test Signals
Single JSON line reports create and rename durations. No correctness signal remains after cleanup.
<!-- END_FILE_RESEARCH: sources/user-network-fs/blobfuse2/perf_testing/scripts/rename.py -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/blobfuse2/perf_testing/scripts/write.py -->
# sources/user-network-fs/blobfuse2/perf_testing/scripts/write.py

## Purpose
Simple sequential write benchmark for `application_<size>.data` under a mount path.

## Important APIs, Types, and Functions
The script accepts `mountpath` and integer `size` in GB. It allocates an 8MiB random buffer, writes it repeatedly until the target byte count is exceeded, then prints timing and throughput JSON.

## Control Flow and State
Open, write-loop, close, and total durations are measured separately. The target file remains on disk/mount after completion.

## Dependencies and Integration Points
Uses Python standard libraries. It is commonly paired with `read.py` for Blobfuse2 mount performance.

## Risks and Edge Cases
The loop condition `bytes_written <= fileSize` writes one extra block beyond the requested size. There is no argument validation, fsync, exception handling, or cleanup. `os.urandom(8MiB)` is generated once, so content repeats by block.

## Test Signals
JSON output reports MiB/s and timing breakdown. It does not verify uploaded data or final file size.
<!-- END_FILE_RESEARCH: sources/user-network-fs/blobfuse2/perf_testing/scripts/write.py -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/blobfuse2/sampleBlockCacheConfig.yaml -->
# sources/user-network-fs/blobfuse2/sampleBlockCacheConfig.yaml

## Purpose
Example Blobfuse2 configuration for a block-cache pipeline using account-key authentication.

## Important APIs, Types, and Functions
Key sections are `logging`, `components`, `libfuse`, `block_cache`, `attr_cache`, and `azstorage`. Components are ordered as `libfuse`, `block_cache`, `attr_cache`, `azstorage`. Block cache is configured with 32MiB blocks, 4096MiB memory, prefetch 80, and parallelism 128.

## Control Flow and State
This declarative YAML controls runtime pipeline assembly and cache sizing when passed to Blobfuse2. It does not persist state itself; the block cache may maintain memory/disk cache depending on full runtime defaults and extra config.

## Dependencies and Integration Points
Consumed by Blobfuse2 config parsing. Placeholders `<ACCOUNT_NAME>`, `<ACCOUNT_KEY>`, and `<CONTAINER_NAME>` must be replaced. It refers readers to `setup/baseConfig.yaml` for the full config surface.

## Risks and Edge Cases
The sample uses `log_debug`, which is verbose for production. Large prefetch and parallelism values can overconsume memory/network resources. Account-key placeholders must not be committed with real secrets.

## Test Signals
Serves as documentation/config smoke input rather than an automated test. It signals the intended component ordering for block-cache scenarios.
<!-- END_FILE_RESEARCH: sources/user-network-fs/blobfuse2/sampleBlockCacheConfig.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/blobfuse2/sampleFileCacheConfig.yaml -->
# sources/user-network-fs/blobfuse2/sampleFileCacheConfig.yaml

## Purpose
Example Blobfuse2 configuration for a file-cache pipeline using account-key authentication.

## Important APIs, Types, and Functions
Defines `logging`, `components`, `libfuse`, `file_cache`, `attr_cache`, and `azstorage`. Components are `libfuse`, `file_cache`, `attr_cache`, `azstorage`. File cache requires a local `path`, uses 120 second timeout, and caps size at 4096MiB.

## Control Flow and State
When used at mount time, it assembles a file-cache pipeline and persists cached file data under the configured cache path. Attribute cache timeout is set to 7200 seconds.

## Dependencies and Integration Points
Consumed by Blobfuse2 config parsing and Azure storage auth. Requires replacing cache path and account/container/key placeholders.

## Risks and Edge Cases
The local cache path must have enough disk space and appropriate permissions. `log_debug` can generate high log volume. Real account keys must not be stored in sample-derived committed configs.

## Test Signals
The file documents expected key-auth file-cache setup. Validating it requires a real mount or config parser smoke test.
<!-- END_FILE_RESEARCH: sources/user-network-fs/blobfuse2/sampleFileCacheConfig.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/blobfuse2/sampleFileCacheWithSASConfig.yaml -->
# sources/user-network-fs/blobfuse2/sampleFileCacheWithSASConfig.yaml

## Purpose
Example Blobfuse2 file-cache configuration using SAS-token authentication instead of account key.

## Important APIs, Types, and Functions
Sections mirror `sampleFileCacheConfig.yaml`, but `azstorage` uses `sas: <SAS_TOKEN>` and `mode: sas`. Pipeline remains `libfuse`, `file_cache`, `attr_cache`, `azstorage`.

## Control Flow and State
At runtime this config mounts a SAS-authenticated block blob container and caches file contents on local disk under `file_cache.path`.

## Dependencies and Integration Points
Requires a valid SAS token, account name, container name, and local cache path. Consumed by Blobfuse2 config parsing and Azure storage client initialization.

## Risks and Edge Cases
SAS tokens are secrets and often contain special characters; deployment tooling must preserve them correctly. Token expiry or insufficient permissions will fail mount or operations. `log_debug` may expose operational details.

## Test Signals
Documents intended SAS file-cache wiring. Real validation requires replacing placeholders and mounting against Azure Storage.
<!-- END_FILE_RESEARCH: sources/user-network-fs/blobfuse2/sampleFileCacheWithSASConfig.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/blobfuse2/scripts/askbuddy.py -->
# sources/user-network-fs/blobfuse2/scripts/askbuddy.py

## Purpose
Minimal manual smoke script for calling an Azure AI Foundry/OpenAI-compatible Blobfuse buddy endpoint.

## Important APIs, Types, and Functions
Creates an Azure bearer token provider with `DefaultAzureCredential` and scope `https://ai.azure.com/.default`, constructs an `OpenAI` client with a hard-coded Foundry application base URL and API version, calls `client.responses.create`, and prints `response.output_text`.

## Control Flow and State
The script executes top-level code only. It sends a fixed prompt about `direct-io` versus `disable-kernel-cache` and exits.

## Dependencies and Integration Points
Depends on `openai` Python SDK and `azure.identity`. Integrates with Azure AI Foundry and local Azure credential configuration.

## Risks and Edge Cases
The service URL and preview API version are hard-coded. No timeout, error handling, or environment override is provided. It will fail outside an authenticated Azure environment.

## Test Signals
Successful output validates local credentials and endpoint reachability, not Blobfuse2 behavior.
<!-- END_FILE_RESEARCH: sources/user-network-fs/blobfuse2/scripts/askbuddy.py -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/blobfuse2/scripts/call_agent.py -->
# sources/user-network-fs/blobfuse2/scripts/call_agent.py

## Purpose
GitHub workflow helper that responds to issues or discussions using an Azure AI Foundry agent grounded by optional DeepWiki context and local repository documentation snippets.

## Important APIs, Types, and Functions
Top-level code loads `GITHUB_EVENT_PATH`, detects issue versus discussion events, and supports a `DRY_RUN` fallback. `query_deepwiki` invokes `deepwiki_query.py`. `search_local_docs` ranks configured documentation files by keyword overlap. The script builds a prompt, calls `client.responses.create`, strips summary/source sections with regexes, prepends an AI disclaimer, optionally summarizes/truncates for GitHub limits, and posts through REST issue comments or GraphQL discussion comments.

## Control Flow and State
State comes from GitHub event JSON and environment variables including `DEEPWIKI_REPO`, `FOUNDRY_BASE_URL`, `FOUNDRY_API_VERSION`, `GITHUB_TOKEN`, and `DRY_RUN`. The script reads local docs but writes no repository files. It posts network side effects to GitHub unless in dry-run mode.

## Dependencies and Integration Points
Depends on `requests`, `openai`, `azure.identity`, the GitHub REST/GraphQL APIs, local docs, and the sibling `deepwiki_query.py`. It integrates with GitHub Actions event payloads.

## Risks and Edge Cases
Top-level execution makes import unsafe. It trusts environment-provided endpoints and tokens. Regex stripping may remove useful answer content. Local doc search is simple keyword matching and can miss relevant sections. Generated answers are explicitly non-authoritative. Discussion GraphQL errors are handled, but many OpenAI/Azure errors before posting are not.

## Test Signals
`DRY_RUN=true` prints target URL, question, and answer for validation without posting. Real workflow success is a posted comment URL.
<!-- END_FILE_RESEARCH: sources/user-network-fs/blobfuse2/scripts/call_agent.py -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/blobfuse2/scripts/deepwiki_query.py -->
# sources/user-network-fs/blobfuse2/scripts/deepwiki_query.py

## Purpose
Command-line MCP client that asks DeepWiki a repository question and prints the answer.

## Important APIs, Types, and Functions
`MCPClient` manages streamable HTTP transport and an MCP `ClientSession`. `connect_to_server` initializes the session. `ask_deepwiki` calls tool `ask_question` with `repoName` and `question`. `cleanup` exits async contexts. `main(repo, title, body)` connects, combines title/body, prints the response, and cleans up.

## Control Flow and State
The script loads `.env`, validates three CLI arguments, then runs the async main. Session and stream contexts are instance state and must be cleaned up in `finally`.

## Dependencies and Integration Points
Depends on `mcp`, `httpx`, `python-dotenv`, and network access to `https://mcp.deepwiki.com/mcp`. It is called by `call_agent.py`.

## Risks and Edge Cases
Imports include unused modules. `ask_deepwiki` returns `result.content`, which may be a list of MCP content objects rather than plain text; callers stringify stdout. There is no timeout in this script itself, relying on caller process timeout. Network/MCP failures propagate.

## Test Signals
A successful run prints DeepWiki content. Failures are surfaced by nonzero exit and stderr when invoked from `call_agent.py`.
<!-- END_FILE_RESEARCH: sources/user-network-fs/blobfuse2/scripts/deepwiki_query.py -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/blobfuse2/scripts/export_github_history.py -->
# sources/user-network-fs/blobfuse2/scripts/export_github_history.py

## Purpose
Exports GitHub issues, pull requests, issue comments, PR reviews, and PR review comments into JSONL files suitable for Azure AI Search indexing.

## Important APIs, Types, and Functions
Configuration uses `OWNER`, `REPO`, `GITHUB_TOKEN`, `OUT_DIR`, and `STATE_FILE`. `_headers` builds GitHub headers. `_request_json` handles rate limits and transient 5xx retries. `_paginate` walks paginated REST responses. `_stable_id` creates deterministic SHA-256 document IDs. `export` orchestrates issue/PR listing, thread document writing, comment/review export, flushing, and incremental state update.

## Control Flow and State
`state.json` stores the latest `updated_at` cursor. First/full runs open output files in write mode; incremental runs append when all prior outputs exist. The GitHub issues endpoint provides both issues and PRs. For PRs, the script additionally fetches reviews and diff comments. Files are flushed after each thread to preserve partial progress.

## Dependencies and Integration Points
Depends on `requests` and GitHub REST API. Outputs `threads_issues_prs.jsonl`, `issue_pr_comments.jsonl`, `pr_reviews.jsonl`, and `pr_review_comments.jsonl` under `OUT_DIR`.

## Risks and Edge Cases
Incremental append can duplicate documents, relying on downstream stable IDs for upsert behavior. The PR reviews endpoint has no since filter, so filtering by `submitted_at` can miss edits to older reviews. The issue list sorted desc by updated time stops only when pagination returns empty, which is correct but can be slow. API errors abort the export after partial writes.

## Test Signals
Console counts and `[ok]` messages plus valid JSONL files are the main signals. A useful validation is line-by-line JSON parsing and checking stable ID uniqueness.
<!-- END_FILE_RESEARCH: sources/user-network-fs/blobfuse2/scripts/export_github_history.py -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/blobfuse2/scripts/fetch_public_docs.py -->
# sources/user-network-fs/blobfuse2/scripts/fetch_public_docs.py

## Purpose
Fetches selected Microsoft Learn Blobfuse2 pages and converts them to Markdown files under `public/`.

## Important APIs, Types, and Functions
`DOCS` maps output Markdown names to Learn URLs. The script creates `public`, configures `html2text.HTML2Text`, requests each URL with a 30 second timeout, converts HTML to Markdown, and writes each file.

## Control Flow and State
All work occurs at top level. Existing files with the same names are overwritten. There is no persistent cursor.

## Dependencies and Integration Points
Depends on `requests`, `html2text`, network access to Microsoft Learn, and local filesystem write access. The generated public docs are likely used by support/agent grounding.

## Risks and Edge Cases
No retry/backoff is implemented. HTML-to-Markdown conversion may include navigation or boilerplate. The fetched docs are time-dependent, so outputs can change across runs.

## Test Signals
Successful console messages and generated Markdown files signal completion. Content quality requires manual review or post-processing checks.
<!-- END_FILE_RESEARCH: sources/user-network-fs/blobfuse2/scripts/fetch_public_docs.py -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/blobfuse2/scripts/issueMetrics.py -->
# sources/user-network-fs/blobfuse2/scripts/issueMetrics.py

## Purpose
Generates terminal reports for recent GitHub issue and PR activity, including counts, resolution times, first-comment times, author ownership, and Copilot-tagged activity.

## Important APIs, Types, and Functions
`get_env_var`, `get_gh_cli_token`, and `get_gh_cli_repo` discover credentials and repo. `parse_args` supports `--days`, `--only-copilot-tagged`, and `--summary`. `print_table` renders fixed-width tables. Formatting helpers convert durations and truncate titles. `is_copilot_tagged` inspects labels. `get_first_comment_time_display_for_pr` checks issue and review comments. `main` authenticates via PyGithub, scans issues and PRs, computes metrics, and prints tables.

## Control Flow and State
The script chooses token from env or `gh auth`, chooses repo from env or `gh repo view`, validates inputs, then fetches data since a UTC lookback timestamp. It skips PRs in the issue loop, filters PRs to base branch `main`, and breaks PR iteration once created dates are older than the window.

## Dependencies and Integration Points
Depends on `PyGithub`, `gh` CLI optionally, GitHub API access, and standard Python libraries. It is a local/reporting utility for maintainers.

## Risks and Edge Cases
API iteration can be slow and rate-limited. PR first-comment retrieval handles exceptions by returning `Unavailable`. Copilot detection is heuristic: labels containing copilot, author `dependabot[bot]`, or author `copilot`. The PR loop assumes created-date descending order and base branch `main`.

## Test Signals
Exit code `0` and printed tables signal success. Error messages cover missing token, missing repo, bad credentials, bad repo access, and invalid day count.
<!-- END_FILE_RESEARCH: sources/user-network-fs/blobfuse2/scripts/issueMetrics.py -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/blobfuse2/setup/11-blobfuse2.conf -->
# sources/user-network-fs/blobfuse2/setup/11-blobfuse2.conf

## Purpose
rsyslog filter that routes Blobfuse2 program logs into dedicated log files.

## Important APIs, Types, and Functions
The rule matches `:programname, isequal, "blobfuse2"`. It writes all messages to `/var/log/blobfuse2.log`, writes messages containing `"REQUEST"` to `/var/log/blobfuse2-rest.log`, then stops further processing.

## Control Flow and State
This is declarative rsyslog configuration. Runtime state is the log files managed by rsyslog and logrotate.

## Dependencies and Integration Points
Installed under `/etc/rsyslog.d/` and paired with `setup/blobfuse2-logrotate`. Integrates with syslog logging mode in Blobfuse2.

## Risks and Edge Cases
All Blobfuse2 logs are stopped after this rule, so downstream rsyslog rules will not receive them. The `"REQUEST"` substring filter can overmatch or undermatch REST traces.

## Test Signals
After rsyslog restart, Blobfuse2 syslog entries should appear in `/var/log/blobfuse2.log`; request traces should additionally appear in `/var/log/blobfuse2-rest.log`.
<!-- END_FILE_RESEARCH: sources/user-network-fs/blobfuse2/setup/11-blobfuse2.conf -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/blobfuse2/setup/12-bfusemon.conf -->
# sources/user-network-fs/blobfuse2/setup/12-bfusemon.conf

## Purpose
rsyslog filter for the Blobfuse2 monitor process `bfusemon`.

## Important APIs, Types, and Functions
The rule matches program name `bfusemon`, writes all messages to `/var/log/bfusemon.log`, and stops further processing.

## Control Flow and State
Declarative rsyslog config; state is the monitor log file.

## Dependencies and Integration Points
Installed under `/etc/rsyslog.d/`. Pairs with health monitor logging and logrotate configuration.

## Risks and Edge Cases
The stop directive prevents duplicate routing to generic logs, which may or may not be desired operationally. The rule depends on the program name being exactly `bfusemon`.

## Test Signals
Generate bfusemon logs and confirm they appear in `/var/log/bfusemon.log` after rsyslog reload.
<!-- END_FILE_RESEARCH: sources/user-network-fs/blobfuse2/setup/12-bfusemon.conf -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/blobfuse2/setup/advancedConfig.yaml -->
# sources/user-network-fs/blobfuse2/setup/advancedConfig.yaml

## Purpose
Comprehensive annotated Blobfuse2 configuration reference showing daemon, logging, pipeline, cache, storage, mount-all, and health-monitor options.

## Important APIs, Types, and Functions
Major sections include top-level mount/daemon flags, `logging`, `components`, `libfuse`, `entry_cache`, `xload`, `block_cache`, `file_cache`, `attr_cache`, `loopbackfs`, `azstorage`, `mountall`, and `health_monitor`. The file documents defaults, accepted values, production cautions, and interaction notes such as block cache versus file cache exclusivity.

## Control Flow and State
The file is a human-editable template, not a valid ready-to-run config because many values are placeholders with inline explanatory text. When converted into real YAML values, it controls pipeline composition, cache persistence paths/sizes, auth mode, retry behavior, ACL behavior, rate caps, and monitor output.

## Dependencies and Integration Points
Consumed conceptually by Blobfuse2 users and referenced by scripts/docs. It mirrors config fields parsed across Blobfuse2 components and setup rsyslog/logrotate files.

## Risks and Edge Cases
Copying it directly without removing explanatory placeholders will fail YAML/config parsing. Some options are production-sensitive: `loopbackfs` is testing-only, `log_debug` can expose detailed logs, cache paths need capacity, and `allow-other` also requires `/etc/fuse.conf` changes. The comments mention `sdk-trace` removal and stream/direct behavior constraints.

## Test Signals
This file is documentation. Signal comes from consistency with parser-supported config keys and from users successfully deriving working configs.
<!-- END_FILE_RESEARCH: sources/user-network-fs/blobfuse2/setup/advancedConfig.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/blobfuse2/setup/baseConfig.yaml -->
# sources/user-network-fs/blobfuse2/setup/baseConfig.yaml

## Purpose
Shorter reference template for common Blobfuse2 configuration sections.

## Important APIs, Types, and Functions
Includes `logging`, `components`, `xload`, `block_cache`, `file_cache`, and `azstorage`. The component order is `libfuse`, `xload`, `block_cache`, `file_cache`, `attr_cache`, `azstorage`.

## Control Flow and State
Like the advanced config, this is an annotated template rather than a directly usable YAML file. Realized values influence cache paths, cache sizes, auth mode, endpoint, account, and container.

## Dependencies and Integration Points
Used by sample configs and setup docs as the baseline option reference. Aligns with Blobfuse2 config parsing.

## Risks and Edge Cases
Inline explanatory placeholders make the file invalid as-is. It lists mutually exclusive cache components together to document choices, so users must remove unused components. Secret fields must be handled carefully.

## Test Signals
Documentation consistency and successful user-derived configs are the primary signals.
<!-- END_FILE_RESEARCH: sources/user-network-fs/blobfuse2/setup/baseConfig.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/blobfuse2/setup/blobfuse2.service -->
# sources/user-network-fs/blobfuse2/setup/blobfuse2.service

## Purpose
Example systemd unit for running a Blobfuse2 mount as a service.

## Important APIs, Types, and Functions
`[Unit]` requires network-online. `[Service]` sets `WorkingDirectory`, `User`, mount/cache/config environment variables, Azure auth environment variables, log level, FUSE timeouts, `Type=simple`, `ExecStart` invoking `blobfuse2 mount`, and `ExecStop` using `fusermount -u`. `[Install]` targets `multi-user.target`.

## Control Flow and State
systemd starts Blobfuse2 with configured environment and stops by unmounting the mount point. State persists in the mounted FUSE process, cache directory, and syslog/log files.

## Dependencies and Integration Points
Requires systemd, network, Blobfuse2 installed at `/usr/local/bin/blobfuse2`, `fusermount`, a valid user, config file, mount point, cache path, and Azure credentials. Integrates with setup docs and syslog filters.

## Risks and Edge Cases
The sample includes account-key placeholders and commented SAS/MSI alternatives; users must edit carefully. SAS tokens need `%` escaping in systemd. `User=AzureUser` and paths are environment-specific. `ExecStop` uses `fusermount`, which may differ for fuse3 systems.

## Test Signals
`systemctl start blobfuse2.service`, mount visibility, and `systemctl status`/logs validate the unit.
<!-- END_FILE_RESEARCH: sources/user-network-fs/blobfuse2/setup/blobfuse2.service -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/blobfuse2/setup/setupUBN.sh -->
# sources/user-network-fs/blobfuse2/setup/setupUBN.sh

## Purpose
Ubuntu setup script for installing development/runtime dependencies, Microsoft package repositories, Blobfuse2, and Azure security pack setup.

## Important APIs, Types, and Functions
Runs `../go_installer.sh ../../`, installs packages with `apt`, enables `user_allow_other` in `/etc/fuse.conf`, adds Microsoft package signing/repo config, installs `blobfuse2`, prints version, and calls `vmSetupAzSecPack.sh`.

## Control Flow and State
The script executes sequentially with many `sudo` mutations: package database updates, package installs, `/etc/fuse.conf` edit, repository addition, and Azure security extension setup. It does not set `set -e`, so failures may not abort later steps.

## Dependencies and Integration Points
Requires Ubuntu, sudo, apt, wget, add-apt-repository, Microsoft package endpoints, and sibling scripts. Integrates with developer/VM provisioning.

## Risks and Edge Cases
Uses deprecated `apt-key`. Unconditional `sed` can duplicate or alter fuse config unexpectedly. Lack of strict error handling can hide failed installs. Calling `vmSetupAzSecPack.sh` triggers Azure login and VM extension operations, which may be surprising for a dependency setup script.

## Test Signals
`go version`, successful package installation, `blobfuse2 --version`, and AzSecPack status output indicate setup progress.
<!-- END_FILE_RESEARCH: sources/user-network-fs/blobfuse2/setup/setupUBN.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/blobfuse2/setup/vmSetupAzSecPack.sh -->
# sources/user-network-fs/blobfuse2/setup/vmSetupAzSecPack.sh

## Purpose
Azure VM hardening/setup script that installs Azure CLI, configures Azure Monitor and Azure Security Linux Agent extensions, validates AzSecPack status, and applies critical security patches.

## Important APIs, Types, and Functions
Runs Azure CLI install/upgrade, `az login` for a Microsoft tenant, reads VM name from `hostname`, reads resource group from IMDS, installs `AzureMonitorLinuxAgent` and `AzureSecurityLinuxAgent` VM extensions, parses `azsecd status`, then runs `az vm assess-patches` and `az vm install-patches`.

## Control Flow and State
The script mutates local packages and Azure VM extensions. If VM name/resource group cannot be determined, it prints manual commands and exits. It sleeps 100 seconds before patch assessment/install.

## Dependencies and Integration Points
Requires Azure VM environment, IMDS access, Azure CLI, jq, sudo, interactive Azure login, and permissions to modify the VM. Called by `setupUBN.sh`.

## Risks and Edge Cases
Interactive `az login` makes automation brittle. Tenant ID is hard-coded. Variables are unquoted in Azure commands. Patch installation can reboot if required. The script assumes `/usr/local/bin/azsecd` exists after extension install.

## Test Signals
AzSecPack status checks for AutoConfig and resource tag presence plus Azure CLI command success are the main signals.
<!-- END_FILE_RESEARCH: sources/user-network-fs/blobfuse2/setup/vmSetupAzSecPack.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/blobfuse2/test/accoutcleanup/accountcleanup_test.go -->
# sources/user-network-fs/blobfuse2/test/accoutcleanup/accountcleanup_test.go

## Purpose
Nightly cleanup test that deletes temporary Azure Blob containers left behind by pipeline/test runs.

## Important APIs, Types, and Functions
`getGenericCredential` reads `STORAGE_ACCOUNT_NAME` and `STORAGE_ACCOUNT_KEY` and creates a shared-key credential. `getGenericServiceClient` builds a Blob service client. `TestDeleteAllTempContainers` lists containers and deletes names beginning with `fuseutc` or having length 40. `TestMain` simply runs tests.

## Control Flow and State
The test authenticates to a real storage account, pages through all containers, and issues delete calls for matching names. It logs delete failures but continues.

## Dependencies and Integration Points
Uses Azure Storage Go SDK `azblob/service`, real storage account credentials, and network access. Excluded under `unittest` build tag.

## Risks and Edge Cases
This is destructive. The length-40 heuristic can delete non-test containers if naming collides. Missing credentials call `log.Fatal`, aborting the test process. It does not check creation time or metadata ownership.

## Test Signals
Successful completion indicates cleanup attempts ran. Logs show deleted containers and failures.
<!-- END_FILE_RESEARCH: sources/user-network-fs/blobfuse2/test/accoutcleanup/accountcleanup_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/blobfuse2/test/ai/checkpointLoad.sh -->
# sources/user-network-fs/blobfuse2/test/ai/checkpointLoad.sh

## Purpose
AI workload benchmark harness for loading/saving model checkpoints through Blobfuse2 using preload, file-cache, and block-cache modes across CPU/CUDA configurations.

## Important APIs, Types, and Functions
`clear_cache` removes Hugging Face caches and drops kernel caches. The `models`, `fusemode`, and `devices` arrays define the matrix. In `model` mode, it downloads models via `load.py` and saves checkpoints to `/mnt/model`. In benchmark mode, it mounts a subdirectory with `./blobfuse2`, optionally parses preload progress from logs, then invokes `python3 load.py --checkpoint_path`.

## Control Flow and State
The script writes `stats.log`, mutates `/mnt/blobfuse/checkpoint`, `/mnt/cpramdisk`, `/mnt/hugging_cache`, mounts/unmounts Blobfuse2 and tmpfs, clears caches, and loops across all device/cache/model combinations.

## Dependencies and Integration Points
Requires Blobfuse2 binary, Azure MSI auth, large Azure container data, Hugging Face/transformers/torch stack, GPUs for CUDA modes, sudo, tmpfs capacity, and `bc`.

## Risks and Edge Cases
Hard-coded storage account/container and local mount paths make it environment-specific. It can allocate a 600G tmpfs and delete cache directories. `mcuda` requires multi-GPU support. Many commands are unquoted and the script lacks strict error mode.

## Test Signals
`stats.log` records model load/save times, checkpoint sizes, bandwidth, preload summaries, and mount failures.
<!-- END_FILE_RESEARCH: sources/user-network-fs/blobfuse2/test/ai/checkpointLoad.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/blobfuse2/test/ai/datasetDownload.py -->
# sources/user-network-fs/blobfuse2/test/ai/datasetDownload.py

## Purpose
Benchmarks Hugging Face dataset loading and optional saving to disk.

## Important APIs, Types, and Functions
CLI args are `--data_path`, `--subset`, and `--dest_path`. It calls `datasets.load_dataset(data_path, subset, num_proc=25)`, prints load time, and optionally calls `dataset.save_to_disk(dest_path, num_proc=25)`.

## Control Flow and State
All work is top-level after argument parsing. It reads remote or local datasets and optionally writes a saved dataset directory.

## Dependencies and Integration Points
Depends on Hugging Face `datasets`. Used by AI data benchmark shell scripts against Blobfuse2-mounted or local paths.

## Risks and Edge Cases
Unused imports indicate script drift. `num_proc=25` can overuse CPU and may not fit every dataset. No exception handling or validation is present.

## Test Signals
Printed load/save durations indicate performance. Dataset correctness is not independently verified.
<!-- END_FILE_RESEARCH: sources/user-network-fs/blobfuse2/test/ai/datasetDownload.py -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/blobfuse2/test/ai/kaggle.json -->
# sources/user-network-fs/blobfuse2/test/ai/kaggle.json

## Purpose
Template Kaggle API credential file for AI dataset download tests.

## Important APIs, Types, and Functions
Contains JSON keys `username` and `key`, with the key shown as a placeholder.

## Control Flow and State
No executable flow. If placed where the Kaggle client expects it, it controls Kaggle API authentication.

## Dependencies and Integration Points
Used by the `kaggle` Python package and `kaggle_download.py` when authenticating.

## Risks and Edge Cases
Credential files should not contain real secrets in source control. The sample includes a real-looking username and placeholder key; users must replace securely and set file permissions as required by Kaggle tooling.

## Test Signals
Kaggle authentication success is the only practical validation.
<!-- END_FILE_RESEARCH: sources/user-network-fs/blobfuse2/test/ai/kaggle.json -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/blobfuse2/test/ai/kaggle_download.py -->
# sources/user-network-fs/blobfuse2/test/ai/kaggle_download.py

## Purpose
Downloads a specific Kaggle dataset into a hard-coded Blobfuse2 mount path.

## Important APIs, Types, and Functions
Creates `kaggle.KaggleApi`, calls `authenticate`, then calls `dataset_download_files("miguelcalado/resnet50rafa", path="/mnt/blobfuse/mnt/resnet50rafa", unzip=True)`.

## Control Flow and State
All work executes at top level. It writes downloaded/unzipped dataset files into `/mnt/blobfuse/mnt/resnet50rafa`.

## Dependencies and Integration Points
Depends on Kaggle credentials, `kaggle` package, network access, and a mounted/writable `/mnt/blobfuse/mnt`. Several imported ML libraries are unused.

## Risks and Edge Cases
Hard-coded dataset and destination path make it non-general. It can consume significant disk/storage. No error handling or path creation exists.

## Test Signals
Kaggle download output and resulting files are the completion signals.
<!-- END_FILE_RESEARCH: sources/user-network-fs/blobfuse2/test/ai/kaggle_download.py -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/blobfuse2/test/ai/load.py -->
# sources/user-network-fs/blobfuse2/test/ai/load.py

## Purpose
Loads Hugging Face causal language models or local checkpoints, optionally saves checkpoints, and reports load/save bandwidth based on checkpoint size.

## Important APIs, Types, and Functions
`get_directory_size` sums file sizes recursively. `load_model` loads tokenizer/model from a model name with optional cache path. `load_checkpoint` loads tokenizer/model from a checkpoint path, supporting `cpu`, `cuda`, or `mcuda` device modes. `save_checkpoint` writes model/tokenizer to a timestamped directory using safe serialization and configurable shard size. `main` parses CLI args and selects model or checkpoint flow.

## Control Flow and State
The script reads from Hugging Face Hub or local checkpoint paths, may write a timestamped checkpoint under `dest_path`, and prints timing, size, and bandwidth summaries. It moves models to the selected device or uses `device_map="auto"` for `mcuda`.

## Dependencies and Integration Points
Depends on `transformers`, PyTorch, and local/GPU resources. Used by `checkpointLoad.sh` and related Blobfuse2 AI workload tests.

## Risks and Edge Cases
`trust_remote_code=True` executes model repository code and is risky for untrusted models. Large models require substantial memory/GPU capacity. `cache_path` can be `None`. If neither `model_name` nor `checkpoint_path` is supplied, the script exits silently. Imported `DataParallel` is not used.

## Test Signals
Printed load/save timing, checkpoint size, and bandwidth are performance signals. Successful model/tokenizer object creation is the functional signal.
<!-- END_FILE_RESEARCH: sources/user-network-fs/blobfuse2/test/ai/load.py -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/blobfuse2/test/ai/master_mount.sh -->
# sources/user-network-fs/blobfuse2/test/ai/master_mount.sh

## Purpose
Mounts a Blobfuse2 container in read-write mode for storing and accessing AI model data.

## Important APIs, Types, and Functions
Exports Azure storage account and MSI auth variables, prepares `/mnt/blobfuse/mnt`, `/mnt/blobfuse/cache`, and `/mnt/ramdisk`, installs Python ML packages, unmounts prior mount, creates a 200G tmpfs, and runs `blobfuse2 mount` with block cache and base logging.

## Control Flow and State
The script mutates system mounts, installs pip packages, clears the mount path, and starts Blobfuse2. It leaves the mount active.

## Dependencies and Integration Points
Requires Blobfuse2, Azure MSI access, sudo, tmpfs capacity, pip, transformers, torch, and a container named `vibhansa`.

## Risks and Edge Cases
Hard-coded account/container/path values. It deletes contents under `$MOUNT_PATH` after mounting or before use depending on current mount state, which can be destructive. It installs packages globally in the active Python environment.

## Test Signals
Successful mount and accessible `/mnt/blobfuse/mnt` are primary signals; logs go to `master_blobfuse2.log`.
<!-- END_FILE_RESEARCH: sources/user-network-fs/blobfuse2/test/ai/master_mount.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/blobfuse2/test/ai/mdata.sh -->
# sources/user-network-fs/blobfuse2/test/ai/mdata.sh

## Purpose
AI dataset benchmark driver that downloads datasets and measures loading them through different Blobfuse2 cache modes.

## Important APIs, Types, and Functions
Writes `stats.log`, invokes an external `data.sh` helper with modes such as `hugging`, `file-cache`, `block-cache`, `preload`, and `ramdisk`, then runs `datasetDownload.py` for Hugging Face datasets or mounted paths.

## Control Flow and State
The script first benchmarks remote Hugging Face loading for `cosmopedia` and `nvidia/OpenMathReasoning`, then iterates cache modes for each model/dataset name and appends timings to `stats.log`.

## Dependencies and Integration Points
Depends on sibling `datasetDownload.py`, an unlisted `data.sh`, Hugging Face datasets, and Blobfuse2 mounted paths prepared by the cache-mode helper.

## Risks and Edge Cases
The referenced `data.sh` is not in the assigned file list and may be missing. `datasetDownload.py` is called without `--dest_path`, so only load timing is captured. Hard-coded dataset names and mount path assumptions limit portability.

## Test Signals
`stats.log` with per-mode load timings is the primary output.
<!-- END_FILE_RESEARCH: sources/user-network-fs/blobfuse2/test/ai/mdata.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/blobfuse2/test/benchmark_test/benchmark_test.go -->
# sources/user-network-fs/blobfuse2/test/benchmark_test/benchmark_test.go

## Purpose
Go test suite for measuring large file creation times on a mount path.

## Important APIs, Types, and Functions
Globals `mntPath`, `n`, and `sizes` configure benchmark directory, repetitions, and GB sizes. `createSingleFile` allocates a buffer of requested size and writes it with `os.WriteFile`. `TestCreateSingleFiles` repeats each size, removes files, and logs mean/stddev using `montanaflynn/stats`. `TestMain` parses flags `mnt-path`, `n`, and `sizes`, prepares the benchmark directory, and cleans up afterward.

## Control Flow and State
The suite writes test files under `<mnt-path>/benchmark`, removes each after timing, and removes the base directory at exit. It mutates global config from flags.

## Dependencies and Integration Points
Depends on `testify/suite` and `github.com/montanaflynn/stats`. Intended for real Blobfuse2 mount paths and excluded under `unittest`.

## Risks and Edge Cases
Allocating full file-size buffers can consume multiple GiB of RAM. Errors during file creation are logged but durations are still appended, potentially skewing metrics. This is a test-style benchmark, not `go test -bench`.

## Test Signals
Logs mean and standard deviation per file size. It measures create/write time but does not validate content or upload completion beyond `os.WriteFile` returning.
<!-- END_FILE_RESEARCH: sources/user-network-fs/blobfuse2/test/benchmark_test/benchmark_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/blobfuse2/test/benchmark_test/bitmap_bench_test.go -->
# sources/user-network-fs/blobfuse2/test/benchmark_test/bitmap_bench_test.go

## Purpose
Microbenchmarks comparing atomic 64-bit bitmap operations with simple 16-bit bitmap operations.

## Important APIs, Types, and Functions
`BitMap64` implements `IsSet`, `Set`, `Clear`, and `Reset` using `sync/atomic` load/CAS loops. `BitMap16` implements equivalent non-atomic operations. Benchmarks cover set, is-set, clear, reset, and parallel set for both types.

## Control Flow and State
Each benchmark initializes a bitmap, resets the timer, then runs repeated operations with bit indices masked into valid ranges. Parallel benchmarks use `b.RunParallel` and shared bitmap state.

## Dependencies and Integration Points
Uses Go `testing` benchmark framework and `sync/atomic`. This appears to benchmark candidate implementations rather than directly importing production bitmap code.

## Risks and Edge Cases
`BitMap16_Set_Parallel` mutates shared non-atomic state in a parallel benchmark, producing a data race under `-race`; that may be intentional for comparison but is unsafe. `Set` and `Clear` benchmarks saturate state quickly, so many iterations measure already-set/already-cleared fast paths. It is not a correctness test.

## Test Signals
`go test bitmap_bench_test.go -bench=. -benchmem` reports allocation and timing comparisons for bitmap strategies.
<!-- END_FILE_RESEARCH: sources/user-network-fs/blobfuse2/test/benchmark_test/bitmap_bench_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/blobfuse2/test/benchmark_test/fio.cfg -->
# sources/user-network-fs/blobfuse2/test/benchmark_test/fio.cfg

## Purpose
FIO configuration for a 15GB random-read benchmark against a Blobfuse2-mounted file.

## Important APIs, Types, and Functions
`[global]` sets `ioengine=sync`, `size=15G`, `bs=16M`, `rw=randread`, `filename=/usr/blob_mnt/testFile15GB`, and `numjobs=20`. `[job]` names the job `seq_read`, despite random-read mode.

## Control Flow and State
FIO uses this config to perform read workload against the configured file. It does not create repository state but reads or may prepare workload state depending on FIO behavior and file existence.

## Dependencies and Integration Points
Requires `fio` and a mounted path containing or able to create `/usr/blob_mnt/testFile15GB`.

## Risks and Edge Cases
The job name conflicts with `rw=randread`, which can confuse reports. Hard-coded filename limits portability. `numjobs=20` can stress client and storage account heavily.

## Test Signals
FIO output provides throughput, IOPS, and latency metrics.
<!-- END_FILE_RESEARCH: sources/user-network-fs/blobfuse2/test/benchmark_test/fio.cfg -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/blobfuse2/test/e2e_tests/data_validation_test.go -->
# sources/user-network-fs/blobfuse2/test/e2e_tests/data_validation_test.go

## Purpose
End-to-end data integrity suite comparing local filesystem behavior with Blobfuse2-mounted paths across small, medium, large, huge, sparse, random-write, and panic-regression scenarios.

## Important APIs, Types, and Functions
Defines flags for mount path, temp/cache path, ADLS mode, quick mode, stream-direct mode, distro, and block size. `dataValidationTestSuite` provides helpers for cleanup, copying, MD5 computation, content validation, file creation, truncation, writes, sparse writes, random file generation, and local/remote path conversion. Tests include overwrite via shell, small/medium/large data copy validation, negative diff validation, multi-file concurrent validation, sparse/random writes, byte-count reads across block boundaries, and panic regressions around close/write/read paths.

## Control Flow and State
`TestDataValidationTestSuite` initializes buffers, skips non-Ubuntu or quick mode, creates a random test directory under the mount, sets local and cache paths, fills random buffers, runs the suite, and removes the mount test directory. Individual tests write both local and mounted files, compare size and MD5, and often clear cache paths to force Blobfuse2 re-read behavior.

## Dependencies and Integration Points
Depends on a live Blobfuse2 mount, local filesystem, cache directory, Linux commands `cp` and `diff`, `testify/suite`, and Go crypto/rand/md5. It integrates with block-cache behavior via `block-size-mb` and stream-direct skip logic.

## Risks and Edge Cases
The suite allocates up to hundreds of MiB and can create 10GiB sparse/truncated files. It is environment-gated and skipped in quick/non-Ubuntu modes, so coverage can be absent in many CI runs. Some helpers use package globals (`tObj`, buffers), limiting parallel safety. Cache deletion during mounted operation can expose timing/flakiness.

## Test Signals
Strong signal for data integrity: MD5 equality against local files, exact size checks, EOF byte counts, expected diff failure in negative test, and absence of panics in block-cache regression cases.
<!-- END_FILE_RESEARCH: sources/user-network-fs/blobfuse2/test/e2e_tests/data_validation_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/blobfuse2/test/e2e_tests/dir_test.go -->
# sources/user-network-fs/blobfuse2/test/e2e_tests/dir_test.go

## Purpose
End-to-end directory operation suite for Blobfuse2 mounts, covering create, duplicate errors, special names, rename/move/delete, ADLS path-depth, stat/chmod/listing, Git workflow behavior, tar behavior, and symlinked directory reads.

## Important APIs, Types, and Functions
`dirTestSuite` stores mount test path, ADLS flag, cache path, and random buffers. Flag helpers configure mount path, temp path, ADLS, clone, stream-direct, and ADLS symlink support. Tests include `TestDirCreateSimple`, `TestDirCreateDuplicate`, `TestDirCreateSplChar`, `TestDirCreateSlashChar`, `TestDirRename`, `TestDirMoveEmpty`, `TestDirMoveNonEmpty`, `TestDirDeleteEmpty`, `TestDirDeleteNonEmpty`, `TestDirCreateDeepPath`, `TestDirGetStats`, `TestDirChmod`, `TestDirList`, `TestDirRenameFull`, `TestGitStash`, and `TestReadDirLink`.

## Control Flow and State
`TestDirTestSuite` creates a random top-level test directory on the mount, sets cache path, detects ADLS mode, fills buffers, runs the suite, and removes the test directory. Tests mutate the mounted tree and clean up per case. Some tests are conditional for ADLS, clone, stream-direct, or symlink support.

## Dependencies and Integration Points
Requires mounted Blobfuse2 path, temp cache path, optional network/git access for clone tests, `tar`, and `testify/suite`. ADLS-specific tests exercise hierarchical namespace semantics and permissions.

## Risks and Edge Cases
`TestGitStash` changes process working directory and performs a network clone, making it slow/flaky unless explicitly enabled. Stream-direct skips full-directory rename. ADLS symlink tests are gated. Some sleep calls compensate for eventual consistency/timing. Cleanup assumes generated paths are safe.

## Test Signals
Passing tests indicate POSIX-like directory semantics, expected errors for duplicates/non-empty deletes/deep ADLS paths, listing correctness, chmod on ADLS, and symlink directory traversal behavior.
<!-- END_FILE_RESEARCH: sources/user-network-fs/blobfuse2/test/e2e_tests/dir_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/blobfuse2/test/e2e_tests/file_test.go -->
# sources/user-network-fs/blobfuse2/test/e2e_tests/file_test.go

## Purpose
End-to-end file operation suite for Blobfuse2 mounts, covering create/open/truncate/read/write/stat/chmod/copy/delete, special and Unicode names, and symlink behavior.

## Important APIs, Types, and Functions
`fileTestSuite` stores mount path, ADLS mode, cache path, and buffers. Flag helpers configure mount, temp, ADLS, clone, stream-direct, distro, and ADLS symlink support. Tests cover basic creation, `O_TRUNC`, UTF-8 and special names, long names, backslash names, label-like names, small read/write, duplicate create, truncate, file/dir name conflict, copy, stat, chmod, multiple medium files, delete, symlink create/read/write/rename/delete, symlink listing/readlink, ADLS read-only creation, and special-character rename.

## Control Flow and State
`TestFileTestSuite` creates a random test directory under the mount, initializes buffers, detects ADLS mode, runs the suite, and removes the directory. Tests manipulate mounted files directly and clean up paths individually.

## Dependencies and Integration Points
Requires live Blobfuse2 mount and temp cache path. Uses Go standard `os`, `io`, `time`, `crypto/rand`, and `testify/suite`. ADLS-specific chmod/read-only/symlink behavior is conditionally tested.

## Risks and Edge Cases
Several tests depend on timing (`time.Sleep`) and mounted filesystem consistency. `TestFileCopy` appears to call `io.Copy(srcFile, dstFile)` from newly created destination to source, which exercises copy plumbing weakly because source/destination naming is counterintuitive. `TestLinkDeleteReadTarget` calls `os.Remove(symName)` twice before asserting only the second error path could matter. Stream-direct/distro gating can skip multi-file coverage.

## Test Signals
Passing tests show broad POSIX file compatibility over Blobfuse2, especially path encoding, symlink behavior, truncation, and metadata. Some individual tests are smoke-level rather than deep data-integrity checks.
<!-- END_FILE_RESEARCH: sources/user-network-fs/blobfuse2/test/e2e_tests/file_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/blobfuse2/test/e2e_tests/truncate_test.go -->
# sources/user-network-fs/blobfuse2/test/e2e_tests/truncate_test.go

## Purpose
Additional truncation-focused end-to-end tests attached to `dataValidationTestSuite`.

## Important APIs, Types, and Functions
Tests include `TestShrinkExistingFile`, `TestExpandExistingFile`, `TestTruncateNonExistingFile`, `TestWriteBeforeTruncate`, `TestWriteAfterTruncate`, and `TestTruncateToZero`. They reuse helpers from `data_validation_test.go` to create local/remote files, truncate both, write at offsets, validate content, and clean up.

## Control Flow and State
Shrink and expand tests run multiple size pairs ranging from 512KiB to 10GiB boundaries. Each case creates matching local and mounted files, validates, truncates, validates again, and removes local/remote/cache paths.

## Dependencies and Integration Points
Depends on the data validation suite globals and setup. It is part of the same e2e package and only runs when `TestDataValidationTestSuite` runs.

## Risks and Edge Cases
Large 10GiB truncate cases can be expensive and storage-dependent. Because it shares the parent suite setup, skip conditions in `data_validation_test.go` also skip these tests. Local versus remote validation assumes local filesystem sparse/truncate behavior is the reference.

## Test Signals
Strong signal for truncate correctness across shrink, expand, missing file errors, write-before/after truncate, and zero-length truncation.
<!-- END_FILE_RESEARCH: sources/user-network-fs/blobfuse2/test/e2e_tests/truncate_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/blobfuse2/test/libs/test_extension/callback_handler.c -->
# sources/user-network-fs/blobfuse2/test/libs/test_extension/callback_handler.c

## Purpose
Sample Blobfuse2 FUSE extension callback implementation that wraps storage callbacks, logs calls, and demonstrates filtering one path.

## Important APIs, Types, and Functions
Implements `ext_init`, `ext_destroy`, and wrappers for `statfs`, `getattr`, directory operations, file operations, symlink/readlink, fsync/fsyncdir, and chmod. Most functions log to syslog and forward to the corresponding function in external `storage_callbacks`. `ext_getattr` returns `-ENOENT` for `/subtree.sh`.

## Control Flow and State
The file does not own persistent state. It relies on the global `storage_callbacks` populated by `extension.c`. Init/destroy call through if present; most other methods assume callbacks are populated and call directly.

## Dependencies and Integration Points
Includes `extension.h`; depends on FUSE 2.9 types and syslog. Compiled into `libextension.so` with `extension.c`. Integrates with Blobfuse2 extension loading.

## Risks and Edge Cases
Most wrappers do not check for null function pointers, so incomplete callback registration can crash. The hard-coded `/subtree.sh` filter changes filesystem semantics and is suitable only as sample/test behavior. Signature differences must match the FUSE version expected by Blobfuse2.

## Test Signals
Syslog messages confirm callback routing. Filtering `/subtree.sh` can be used to verify extension interception.
<!-- END_FILE_RESEARCH: sources/user-network-fs/blobfuse2/test/libs/test_extension/callback_handler.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/blobfuse2/test/libs/test_extension/callback_handler.h -->
# sources/user-network-fs/blobfuse2/test/libs/test_extension/callback_handler.h

## Purpose
Header declaring the sample extension callback functions implemented in `callback_handler.c`.

## Important APIs, Types, and Functions
Defines include guard `__CALLBACK_HANDLERS_H__`, sets `FUSE_USE_VERSION 29`, includes `<fuse.h>`, and declares `ext_*` functions for init/destroy, stat/getattr, directory operations, file operations, symlink/readlink, fsync/fsyncdir, and chmod.

## Control Flow and State
No runtime flow or state. It provides the compile-time contract between `extension.c` and `callback_handler.c`.

## Dependencies and Integration Points
Depends on libfuse headers. Comments document commands to build a shared or static extension library.

## Risks and Edge Cases
FUSE 2.9 is hard-coded; building against FUSE 3 without compatibility may fail. The include guard name differs from the filename singular/plural pattern, but remains functional.

## Test Signals
Successful compilation of the extension is the main validation.
<!-- END_FILE_RESEARCH: sources/user-network-fs/blobfuse2/test/libs/test_extension/callback_handler.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/blobfuse2/test/libs/test_extension/extension.c -->
# sources/user-network-fs/blobfuse2/test/libs/test_extension/extension.c

## Purpose
Sample extension entrypoints used by Blobfuse2 to validate an extension signature and exchange FUSE callback tables.

## Important APIs, Types, and Functions
Globals `signature_verified`, `launcher_call_sign`, and `my_call_sign` implement a handshake. `validate_signature` checks the launcher's string and returns the extension response string. `init_extension` logs the received config file. `register_fuse_callbacks` populates a provided `fuse_operations` table with local `ext_*` wrappers after signature verification. `register_storage_callbacks` copies Blobfuse2 storage callbacks into global `storage_callbacks`.

## Control Flow and State
Blobfuse2 is expected to call `validate_signature`, then `init_extension`, then registration functions. Until signature verification succeeds, registration returns `-1`. After storage callbacks are registered, wrapper functions in `callback_handler.c` can forward FUSE operations.

## Dependencies and Integration Points
Includes `extension.h` and `callback_handler.h`; depends on FUSE and syslog. This file is the dynamic-library boundary used by Blobfuse2 extension support.

## Risks and Edge Cases
The signature handshake is a simple string comparison and not security-sensitive authentication. `signature_verified` is global and not thread-safe, though registration is likely single-threaded. Callback table assignment assumes ABI compatibility with the FUSE version.

## Test Signals
Syslog entries and successful return from callback registration indicate extension loading. Negative testing can call registration before signature verification and expect failure.
<!-- END_FILE_RESEARCH: sources/user-network-fs/blobfuse2/test/libs/test_extension/extension.c -->
