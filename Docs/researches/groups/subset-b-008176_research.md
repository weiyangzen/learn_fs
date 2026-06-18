# Research: subset-b-008176

Grouped source research for MinIO Client command files under `sources/object-store/minio-mc/cmd`. Each section is bounded for reconciliation into the source-tree-aligned per-file report.

<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio-mc/cmd/main.go -->
## sources/object-store/minio-mc/cmd/main.go

Purpose: this is the primary `mc` CLI bootstrap. It wires global flags, help rendering, profiling, configuration initialization, update checks, command registration, shell completion, and pager handling before dispatching to subcommands through `github.com/minio/cli`.

Important APIs and functions: `Main(args []string)` is the external entrypoint; `registerApp` builds the `cli.App`; `registerBefore` performs global setup; `initMC`, `migrate`, and `checkConfig` prepare and validate persisted client state; `commandNotFound` and `onUsageError` provide UX; `installAutoCompletion` integrates with `posener/complete`; `printMCVersion` overrides version output.

Control flow: `Main` handles completion mode, optional `MC_PROFILER`, probe metadata, terminal sizing, signal trapping, pager setup, and then runs the registered app. `registerApp` installs app-level action behavior for update checks, autocompletion, empty command help, and unknown-command suggestions. Every command is listed in `appCmds` and shares global flags.

State and persistence: reads `MC_CONFIG_FILE`, migrates config/share files, creates config/certs/CA directories, loads roots, and writes initial config if absent. It also stores profiler files under the mc profile directory and uses package globals for quiet/json/terminal/pager state.

Dependencies and integration: integrates all command files via `appCmds`, certificate/config helpers, probe metadata, terminal detection, MinIO update metadata, and trie/word-distance command suggestions.

Risks: `syscall.SIGKILL` cannot be trapped on Unix, but is passed to `trapSignals`; update checks run on normal command invocation; completion installation uses shell detection and rc-file modification; many setup failures terminate with `fatalIf`, which makes embedded use harder. Test coverage in this subset only indirectly exercises config helpers through `mc_test.go`.
<!-- END_FILE_RESEARCH: sources/object-store/minio-mc/cmd/main.go -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio-mc/cmd/mb-main.go -->
## sources/object-store/minio-mc/cmd/mb-main.go

Purpose: implements `mc mb`, creating object-storage buckets or filesystem directories, with optional region, ignore-existing, object-lock, and versioning behavior.

Important APIs and functions: `mbCmd` defines the CLI command and examples; `makeBucketMessage` implements the shared `message` contract with `String` and `JSON`; `checkMakeBucketSyntax` enforces at least one target; `mainMakeBucket` performs the operation.

Control flow: after syntax validation and color setup, `mainMakeBucket` iterates all targets. It creates a `Client` via `newClient`, creates a per-target cancellable context, calls `MakeBucket(region, ignoreExisting, withLock)`, optionally calls `SetVersion("enable")`, and prints success. Per-target failures set a final error status but allow later targets to continue.

State and persistence: bucket/directory creation and optional bucket versioning are persistent remote or filesystem mutations. No local state is written except normal global config reads done before command dispatch.

Dependencies and integration: uses `Client.MakeBucket`, `Client.SetVersion`, `BucketNameEmpty`, `urlJoinPath`, shared output printing, and global CLI flags.

Risks and tests: the defer in the loop delays cancellation until command exit for every target. Versioning failure is fatal after bucket creation, so partial success is possible. There are no direct tests in this subset for `mb`; coverage is integration-dependent.
<!-- END_FILE_RESEARCH: sources/object-store/minio-mc/cmd/mb-main.go -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio-mc/cmd/mc_test.go -->
## sources/object-store/minio-mc/cmd/mc_test.go

Purpose: provides package-level tests for common configuration, alias, permission, and duration display helpers used across the CLI.

Important APIs and functions: `Test` registers the `gopkg.in/check.v1` suite; `TestSuite` is the check suite; tests cover `accessPerms.isValidAccessPERM`, `getMcConfigDir`, `mustGetMcConfigDir`, `getMcConfigPath`, `mustGetMcConfigPath`, `isValidAlias`, and `timeDurationToHumanizedDuration`.

Control flow: `SetUpSuite` and `TearDownSuite` are empty. Each test uses check assertions to validate expected values and OS-dependent paths. Permission tests check accepted values `none`, `public`, `private`, `download`, `upload` and reject an invalid string.

State and persistence: tests call config directory/path discovery and may depend on the process environment and platform-specific path resolution, but do not intentionally write config.

Dependencies and integration: depends on global package helpers defined outside this subset. It is a smoke signal that CLI bootstrap assumptions about config paths and alias naming are stable.

Risks and test signals: the tests do not isolate environment variables or home/config directories, so behavior can vary under unusual CI environments. They validate helper behavior but do not exercise command execution or persistent object-store side effects.
<!-- END_FILE_RESEARCH: sources/object-store/minio-mc/cmd/mc_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio-mc/cmd/mirror-main.go -->
## sources/object-store/minio-mc/cmd/mirror-main.go

Purpose: implements `mc mirror`, synchronizing objects, prefixes, and optionally buckets from a source to a target, including watch mode, active-active mode, removals, metadata preservation, retry, Prometheus metrics, and summary output.

Important APIs and types: `mirrorCmd` defines a large CLI surface; `mirrorJob` owns watcher, status, `ParallelManager`, channels, source/target URLs, and options; `mirrorMessage` formats output; key methods are `doMirror`, `doMirrorWatch`, `doRemove`, `doCreateBucket`, `doDeleteBucket`, `startMirror`, `watchMirrorEvents`, `monitorMirrorStatus`, `mirror`, and `runMirror`.

Control flow: `mainMirror` validates encryption keys and syntax, optionally starts a `/metrics` HTTP endpoint, and repeatedly calls `runMirror` for watch/active-active modes. `runMirror` builds `mirrorOptions`, prepares clients, handles bucket-level create/delete/preserve policy work, joins the watcher, then executes a `mirrorJob`. The job lists differences from `prepareMirrorURLs`, filters by age, queues copies/removes through `ParallelManager`, and reports results through `statusCh`.

State and persistence: mutates target buckets, objects, metadata, storage class, replication-related active-active metadata, bucket policies, object lock settings, and deletions when `--remove` or active-active delete events are enabled. Metrics counters/histograms are process-global.

Dependencies and integration: integrates `objectDifference`, `bucketDifference`, `Watcher`, `ParallelManager`, `Status`, SSE key lookup, `uploadSourceToTargetURL`, retry manager, MinIO SDK retention/object-lock types, notification event types, and Prometheus.

Risks and tests: concurrency, cancellation, and watch restarts are complex. `--skip-errors` controls whether errors cancel the run; active-active loops are avoided with user-agent and metadata checks but remain sensitive. Prometheus uses global registration, which can conflict in repeated tests. No direct mirror tests are in this subset.
<!-- END_FILE_RESEARCH: sources/object-store/minio-mc/cmd/mirror-main.go -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio-mc/cmd/mirror-url.go -->
## sources/object-store/minio-mc/cmd/mirror-url.go

Purpose: prepares mirror copy/remove work by validating source/target syntax, applying exclude rules, comparing source and target listings, and emitting `URLs` tasks.

Important APIs and types: `checkMirrorSyntax`, `matchExcludeOptions`, `matchExcludeBucketOptions`, `deltaSourceTarget`, `mirrorOptions`, and `prepareMirrorURLs` are the core functions. `mirrorOptions` is the shared option bag consumed by listing, filtering, copying, and watch logic.

Control flow: syntax validation enforces exactly two arguments, warns on deprecated `--force`, checks preserve limitations on Windows, stats non-watch sources, ensures non-watch sources are directories, and absolutizes local source paths. `deltaSourceTarget` normalizes trailing separators, expands aliases, creates clients, compares objects with `objectDifference`, filters source and target suffixes by object, bucket, and storage-class options, then emits copy, overwrite-denied, remove, or error `URLs`.

State and persistence: this file does not mutate storage directly. It creates channels and client/listing state only; the generated work drives mutations in `mirror-main.go`.

Dependencies and integration: depends on alias expansion, URL typing, `url2Stat`, `objectDifference`, wildcard matching, MinIO checksum type, and shared error constructors.

Risks and tests: path prefix trimming is sensitive to slash normalization and Windows separators. Exclude matching is wildcard-based and operates on suffixes/bucket names. No direct tests cover mirror URL generation in this subset.
<!-- END_FILE_RESEARCH: sources/object-store/minio-mc/cmd/mirror-url.go -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio-mc/cmd/mv-main.go -->
## sources/object-store/minio-mc/cmd/mv-main.go

Purpose: implements `mc mv` by reusing copy-session behavior and deleting successfully moved sources through a shared remove manager.

Important APIs and types: `mvCmd` declares flags; `removeClientInfo` and `removeManager` multiplex remove operations by target alias; `readErrors`, `add`, and `close` manage remove streams; `mainMove` is the command entrypoint; `rmManager` is the package-global manager.

Control flow: `mainMove` validates copy syntax, rejects moving a source into its destination prefix for two-argument cases, parses encryption keys, calls `doCopySession(..., true)` to perform move-mode copies, then closes `rmManager` so queued source deletions complete. `removeManager.add` lazily creates one `Client.Remove` stream per alias and sends `ClientContent` entries into a buffered channel.

State and persistence: mutates destination objects through copy-session code and deletes source objects/files through `Client.Remove`. `rmManager` persists as package global state across invocations.

Dependencies and integration: relies heavily on copy command helpers outside this subset, shared `Client.Remove`, `RemoveResult`, `URLs`, context cancellation, and global copy status/output handling.

Risks and tests: the global `rmManager` can retain closed channels or client info across repeated in-process command calls, which is a test/embedding risk. Error handling in remove goroutines prints but does not directly fail `mainMove`. No direct tests are present.
<!-- END_FILE_RESEARCH: sources/object-store/minio-mc/cmd/mv-main.go -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio-mc/cmd/od-main.go -->
## sources/object-store/minio-mc/cmd/od-main.go

Purpose: implements the hidden or specialized `mc od` command for measuring single-stream upload/download/copy throughput with explicit part sizing and skip controls.

Important APIs and types: `odCmd` defines operands `if=`, `of=`, `size=`, `parts=`, and `skip=`; `odMessage` implements CLI/JSON output; `getOdUrls`, `odCheckType`, and `mainOD` route to transfer implementations.

Control flow: `mainOD` validates that operands exist, parses each argument as a `key=value` pair into `argKVS`, resolves source and target with `getOdUrls`, then calls `odCheckType`. Direction is inferred from aliases: S3-to-filesystem uses `odDownload`; filesystem-to-S3, S3-to-S3, and filesystem-to-filesystem use `odCopy` with an `odType` string.

State and persistence: copies or downloads data to the requested target. It does not persist local CLI config beyond normal startup behavior.

Dependencies and integration: reuses copy URL classification (`guessCopyURLType`, `makeCopyContentTypeA`), transfer helpers in `od-stream.go`, `printMsg`, and JSON formatting.

Risks and tests: operand parsing assumes every argument contains `=` and indexes `kv[1]`, so malformed operands can panic. There are no direct tests for `od` in this subset.
<!-- END_FILE_RESEARCH: sources/object-store/minio-mc/cmd/od-main.go -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio-mc/cmd/od-stream.go -->
## sources/object-store/minio-mc/cmd/od-stream.go

Purpose: contains the transfer mechanics for `mc od`, including part-size math, copy/upload timing, and S3 part download composition.

Important APIs and functions: `odSetSizes` calculates combined size, part size, part count, and byte skip; `odCopy` uploads a selected range or generated stream to a target; `odSetParts` validates download part controls; `odDownload` writes S3 content to a local target; `singleGet` and `multiGet` obtain one or many object parts.

Control flow: uploads calculate size/skip, open a source stream with optional range start, create `PutOptions`, disable multipart for small known sizes, count bytes with an accounter, call `PutPart`, and return an `odMessage`. Downloads choose full-object or multipart reads, then pipe them to `putTargetStream`.

State and persistence: reads source data and writes target data. Uses no local persistent state.

Dependencies and integration: uses `Client.GetPart`, `Client.PutPart`, `getSourceStreamFromURL`, `putTargetStream`, `newAccounter`, `PutOptions`, and human-readable byte parsing.

Risks and tests: `multiGet` loops from `1 + skip` to `parts` but calls `cli.GetPart(ctx, parts)` instead of the loop index, which looks suspicious. Division by `partSize` occurs when building `Skip`. There are no direct tests.
<!-- END_FILE_RESEARCH: sources/object-store/minio-mc/cmd/od-stream.go -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio-mc/cmd/parallel-manager.go -->
## sources/object-store/minio-mc/cmd/parallel-manager.go

Purpose: provides adaptive concurrent task execution for copy/mirror style workloads while considering bandwidth improvement and memory pressure.

Important APIs and types: `task` wraps a `func() URLs`, barrier flag, and upload size. `ParallelManager` owns worker count, queue/result channels, wait group, barrier lock, byte counter, max memory, and max worker cap. Key methods are `addWorker`, `Read`, `monitorProgress`, `queueTask`, `queueTaskWithBarrier`, `enoughMemForUpload`, `doQueueTask`, `stopAndWait`, and constructor `newParallelManager`.

Control flow: construction starts `runtime.NumCPU()` workers and a monitor goroutine. Tasks are queued under a read lock or exclusive lock for barriers. Workers execute tasks and send `URLs` to the result channel. The monitor samples bytes every four seconds and adds workers while bandwidth improves, up to `maxWorkers` or 128.

State and persistence: no persistent storage; process state includes goroutines and atomics. `Read` acts as a progress counter for readers that tee through the manager.

Dependencies and integration: used by mirror and likely copy status paths. It calls MinIO `OptimalPartInfo`, `gopsutil/mem`, cgroup memory limit files, and Go runtime GC/memstats.

Risks and tests: `for range defaultWorkerFactor` requires modern Go integer range syntax. Barrier tasks block queuing until running work finishes. Memory estimates panic on unexpected inputs or `OptimalPartInfo` errors. No direct tests cover concurrency behavior.
<!-- END_FILE_RESEARCH: sources/object-store/minio-mc/cmd/parallel-manager.go -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio-mc/cmd/parse_time_test.go -->
## sources/object-store/minio-mc/cmd/parse_time_test.go

Purpose: tests the custom duration parser used by commands with age/time flags such as `--older-than` and `--newer-than`.

Important APIs and data: `parseDurationTests` enumerates valid and invalid strings for `ParseDuration`; `TestParseDuration` checks parser success and exact `Duration` values; `TestParseDurationTime` adds command-style day/hour/minute scenarios and expected error strings.

Control flow: table tests run subtests over simple units, signs, decimals, composite durations, weeks/days, very large values, fractional precision, and overflow cases. Invalid cases require non-nil errors.

State and persistence: test-only, no persistent mutation.

Dependencies and integration: relies on package constants `Nanosecond`, `Microsecond`, `Millisecond`, `Second`, `Minute`, `Hour`, `Day`, `Week`, and type `Duration` defined elsewhere. These tests indirectly protect filtering flags used by mirror, move, and replication resync.

Risks and test signals: tests include Unicode microsecond symbols, so source encoding matters. Error matching in `TestParseDurationTime` only checks mismatching non-nil errors; if an expected error case returns nil with expected zero value, it would not fail for the error string.
<!-- END_FILE_RESEARCH: sources/object-store/minio-mc/cmd/parse_time_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio-mc/cmd/ping.go -->
## sources/object-store/minio-mc/cmd/ping.go

Purpose: implements `mc ping`, repeatedly checking MinIO liveness through anonymous admin APIs, optionally across distributed nodes, with summary statistics and signal-aware shutdown.

Important APIs and types: `pingCmd`, `PingResult`, `PingSummary`, `EndPointStats`, `ServerStats`, templates `Ping`/`PingDist`, helpers `fetchAdminInfo`, `filterAdminInfo`, `ping`, `pingStats`, `trimToTwoDecimal`, `pad`, `watchSignals`, and `mainPing`.

Control flow: `mainPing` validates args, builds admin and anonymous clients, optionally fetches server info for distributed/node mode, disables the global signal trap, installs its own summary-printing signal handler, and runs either a fixed-count loop or an infinite loop. Each `ping` call consumes `anonClient.Alive`, updates per-endpoint stats, prints a result, and sleeps by interval unless stopping.

State and persistence: no storage mutation. Maintains package-global `stop`, signal handlers, and a mutable summary map.

Dependencies and integration: uses `madmin` anonymous/admin clients, Go templates/tabwriter, shared `printMsg`, global context/cancel, and profiling shutdown.

Risks and tests: `stop` is package-global and not reset in `mainPing`, which can leak across repeated in-process invocations. `fetchAdminInfo` retries indefinitely until global cancellation. No direct tests exist.
<!-- END_FILE_RESEARCH: sources/object-store/minio-mc/cmd/ping.go -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio-mc/cmd/pipe-main.go -->
## sources/object-store/minio-mc/cmd/pipe-main.go

Purpose: implements `mc pipe`, streaming stdin to stdout or to one object target, with metadata, tags, storage class, multipart concurrency, pipe buffer tuning, checksums, and encryption.

Important APIs and types: `defaultPartSize`, `pipeCmd`, `pipeMessage`, `pipe`, `checkPipeSyntax`, and `mainPipe`. `pipeMessage` implements shared string/JSON output.

Control flow: `mainPipe` validates exactly one CLI argument, parses encryption keys, metadata and tags, and calls `pipe`. `pipe` optionally increases stdin pipe buffer size, copies stdin to stdout if no target is supplied, otherwise builds `PutOptions`, wraps stdin in a progress bar when interactive, and streams via `putTargetStreamWithURL`. Broken pipe from stdin is treated as graceful.

State and persistence: writes to the target object or file; can alter runtime GC percent when concurrent uploads are enabled. No local config writes.

Dependencies and integration: uses platform-specific `increasePipeBufferSize`, MinIO multipart sizing, SSE lookup, metadata parsing, checksum parsing, progress bars, and target stream upload helpers.

Risks and tests: `checkPipeSyntax` currently rejects zero args, while `mainPipe` still has a no-arg stdout branch that is unreachable through normal command flow. High concurrency can use substantial memory. No direct pipe command tests are in this subset.
<!-- END_FILE_RESEARCH: sources/object-store/minio-mc/cmd/pipe-main.go -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio-mc/cmd/pipe_supported.go -->
## sources/object-store/minio-mc/cmd/pipe_supported.go

Purpose: Linux-specific support for increasing pipe buffer size before streaming stdin in `mc pipe`.

Important APIs and functions: build tag `//go:build linux` selects this implementation. `pipeMaxSizeProcFile` points to `/proc/sys/fs/pipe-max-size`; `setPipeSize` calls `unix.FcntlInt` with `F_SETPIPE_SZ`; `getConfiguredMaxPipeSize` reads and parses the proc file; `increasePipeBufferSize` applies either the requested size or the system maximum.

Control flow: if desired size is zero or negative, it attempts to read the kernel-configured maximum and set that value, ignoring `setPipeSize` errors in that branch. Otherwise it sets the caller-provided size and returns errors.

State and persistence: changes the kernel pipe buffer size for the provided file descriptor only; no durable storage mutation.

Dependencies and integration: called by `pipe-main.go` before upload. Depends on `golang.org/x/sys/unix` and Linux procfs.

Risks and tests: when auto mode reads procfs successfully, `setPipeSize` errors are swallowed. Permissions and kernel limits can make explicit sizes fail. No tests cover this platform path.
<!-- END_FILE_RESEARCH: sources/object-store/minio-mc/cmd/pipe_supported.go -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio-mc/cmd/pipe_unsupported.go -->
## sources/object-store/minio-mc/cmd/pipe_unsupported.go

Purpose: non-Linux fallback for pipe buffer tuning.

Important APIs and functions: build tag `//go:build !linux` selects a no-op `increasePipeBufferSize(_ *os.File, _ int) error`.

Control flow: any caller request returns nil immediately, so `mc pipe` proceeds without pipe-size changes on unsupported platforms.

State and persistence: no state changes.

Dependencies and integration: satisfies the same function signature used by `pipe-main.go`, preserving cross-platform compilation.

Risks and tests: hidden `--pipe-max-size` has no effect on non-Linux systems, and callers receive no warning. No tests cover this fallback.
<!-- END_FILE_RESEARCH: sources/object-store/minio-mc/cmd/pipe_unsupported.go -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio-mc/cmd/pipechan.go -->
## sources/object-store/minio-mc/cmd/pipechan.go

Purpose: provides `PipeChan`, a dynamically resizing logical channel for filesystem notification events, intended to reduce sender blocking when event bursts exceed a fixed channel capacity.

Important APIs and functions: `PipeChan(capacity int) (inputCh, outputCh chan notify.EventInfo)` is the only exported API in this file. It returns an input channel for producers and an output channel for consumers.

Control flow: one goroutine reads from `inputCh`, creates internal channels, and switches to larger or smaller internal channels based on current length thresholds. A second goroutine drains each internal channel in sequence into `outputCh`, then closes output when all internal channels close.

State and persistence: in-memory channels only. It may allocate increasingly large buffers during bursts.

Dependencies and integration: works with `github.com/rjeczalik/notify.EventInfo`, likely used by watch code outside this subset.

Risks and tests: `capacity <= 0` would create zero-capacity channels and can make threshold logic problematic. The shrink condition checks `len(currCh) >= capacity && len(currCh) <= cap(currCh)/4`, which is hard to reach after the growth condition and may not shrink as intended. Covered by `pipechan_test.go`.
<!-- END_FILE_RESEARCH: sources/object-store/minio-mc/cmd/pipechan.go -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio-mc/cmd/pipechan_test.go -->
## sources/object-store/minio-mc/cmd/pipechan_test.go

Purpose: tests and benchmarks `PipeChan` against regular buffered channels for event delivery correctness and throughput.

Important APIs and functions: `testPipeChan` sends `totalMsgs` `notify.EventInfo` values and verifies all arrive unchanged; `TestPipeChannel` checks `PipeChan(1000)` with 10,000 messages; `TestRegularChannel` runs the same harness on a normal channel; benchmark helpers compare regular and pipe channels at 1K, 10K, 100K, and 1M message counts.

Control flow: producer and consumer goroutines are coordinated with a wait group. The producer closes input when done; the consumer counts messages until output closes and records corruption.

State and persistence: test-only in-memory channel state.

Dependencies and integration: depends on `github.com/rjeczalik/notify` and the pipe channel implementation. Benchmarks provide performance expectations but are not assertions.

Risks and test signals: the tests validate delivery count and value identity for nil event info, but they do not test non-nil events, capacity edge cases, cancellation, or memory behavior under long-running watch workloads.
<!-- END_FILE_RESEARCH: sources/object-store/minio-mc/cmd/pipechan_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio-mc/cmd/policy-main.go -->
## sources/object-store/minio-mc/cmd/policy-main.go

Purpose: retains a hidden legacy `mc policy` command that redirects users to `mc anonymous`.

Important APIs and functions: `policyFlags` keeps a legacy recursive flag; `policyCmd` is hidden and has a help template saying to use `mc anonymous`; `mainPolicy` prints the same guidance.

Control flow: invocation does not perform policy work. It runs global setup, then `mainPolicy` emits an informational line and returns nil.

State and persistence: no object-store or local-state mutation.

Dependencies and integration: exists in `appCmds` for compatibility and uses shared CLI/global flag plumbing and console output.

Risks and tests: command is intentionally minimal. Scripts expecting old `mc policy` behavior will not get functional policy management here, only guidance. No direct tests.
<!-- END_FILE_RESEARCH: sources/object-store/minio-mc/cmd/policy-main.go -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio-mc/cmd/pretty-record.go -->
## sources/object-store/minio-mc/cmd/pretty-record.go

Purpose: small formatter for colorized multi-line key/value records with a heading row and aligned subsequent rows.

Important APIs and types: `Row` stores a description and color theme; `PrettyRecord` stores row config, indent, and max description length; `newPrettyRecord` computes alignment; `buildRecord` renders supplied content.

Control flow: `buildRecord` uses the smaller of configured row count and content count. The first row is rendered as a heading with no key label. Later rows use the configured indent and max label width, then colorize the full formatted line per row theme.

State and persistence: no state outside returned structs and strings.

Dependencies and integration: uses `console.Colorize`; likely shared by command output formatters outside this subset.

Risks and tests: alignment uses byte length rather than display width, so wide Unicode and ANSI color content can misalign. There are no direct tests for `PrettyRecord`.
<!-- END_FILE_RESEARCH: sources/object-store/minio-mc/cmd/pretty-record.go -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio-mc/cmd/pretty-table.go -->
## sources/object-store/minio-mc/cmd/pretty-table.go

Purpose: small colorized row formatter for fixed-width command output tables.

Important APIs and types: `Field` stores a color theme and maximum length; `PrettyTable` stores fields and separator; `newPrettyTable` constructs a table; `buildRow` renders a single row.

Control flow: `buildRow` iterates over the smaller of configured fields and provided contents. For fields with `maxLen >= 0`, it pads/truncates using `fmt` precision and manually replaces overlong content with a suffix of `...`; negative max length leaves content unchanged. Separators are inserted between rendered columns.

State and persistence: pure formatting helper with no persistent state.

Dependencies and integration: used by replication backlog and resync status output, and likely other CLI views. Depends on `console.Colorize`.

Risks and tests: truncation uses byte slicing and assumes `maxLen >= len("...")`; small max lengths can panic from negative slice bounds. Unicode display width is not handled. `pretty-table_test.go` covers basic ASCII behavior.
<!-- END_FILE_RESEARCH: sources/object-store/minio-mc/cmd/pretty-table.go -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio-mc/cmd/pretty-table_test.go -->
## sources/object-store/minio-mc/cmd/pretty-table_test.go

Purpose: verifies core ASCII behavior of `PrettyTable.buildRow`.

Important APIs and functions: `TestPrettyTable` is a table-driven unit test over separators, field definitions, contents, and expected row strings.

Control flow: each test constructs a `PrettyTable`, calls `buildRow`, and fails immediately if the result differs. Cases cover empty table, one unlimited field, one truncated field, ignored separator for a single column, multi-column separator insertion, and mixed truncated/unlimited fields.

State and persistence: test-only, no mutation beyond local variables.

Dependencies and integration: directly protects `pretty-table.go`, which is used by replication and status output.

Risks and test signals: tests use only ASCII strings and max lengths greater than three, so they do not cover Unicode width, colorized output interactions, or negative slice risk when `maxLen < 3`.
<!-- END_FILE_RESEARCH: sources/object-store/minio-mc/cmd/pretty-table_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio-mc/cmd/print.go -->
## sources/object-store/minio-mc/cmd/print.go

Purpose: centralizes command message printing for human-readable and JSON output modes.

Important APIs and types: `message` requires `JSON() string` and `String() string`; `printMsg` chooses the representation based on `globalJSON`.

Control flow: for normal output it calls `String`. For JSON mode it calls `JSON`; if `globalJSONLine` is true and the JSON contains newlines, it attempts `json.Compact` to emit one line. It trims one trailing newline and writes through `console.Println`.

State and persistence: no persistent storage. Reads global output mode flags.

Dependencies and integration: every command message type in this subset implements this interface. It uses the standard JSON package only to compact output already produced by message implementations.

Risks and tests: if a `JSON` method returns invalid JSON, compaction failure is ignored and multiline output remains. It strips only suffix newline, not other whitespace. No direct tests.
<!-- END_FILE_RESEARCH: sources/object-store/minio-mc/cmd/print.go -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio-mc/cmd/profiling.go -->
## sources/object-store/minio-mc/cmd/profiling.go

Purpose: implements optional runtime profiling controlled by `MC_PROFILER` in `main.go`.

Important APIs and types: `profiler` interface; concrete `cpuProfiler`, `memProfiler`, `blockProfiler`, and `goroutineProfiler`; constructors for each; package-global `globalProfilers`; `enableProfilers` and `stopProfiling`.

Control flow: `enableProfilers` creates the output folder, opens one timestamped file per requested profiler, constructs the matching profiler, starts it, and stores it globally. CPU starts immediately; memory and goroutine write snapshots on stop; block enables `runtime.SetBlockProfileRate(100)` until stop. `stopProfiling` stops all registered profilers in order.

State and persistence: writes profile files under the profile directory. Mutates global profiler list and runtime block profiling rate.

Dependencies and integration: called from `Main` when `MC_PROFILER` is set and from ping signal handling before global cancellation.

Risks and tests: if an unknown profiler appears after earlier profilers started, the function returns an error without stopping already-started profilers or closing files. No direct tests.
<!-- END_FILE_RESEARCH: sources/object-store/minio-mc/cmd/profiling.go -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio-mc/cmd/progress-bar.go -->
## sources/object-store/minio-mc/cmd/progress-bar.go

Purpose: wraps `cheggaaa/pb` progress bars for byte-oriented transfers and caption formatting.

Important APIs and types: `progressBar` embeds `*pb.ProgressBar`; `newPB`, `newProgressReader`, `newProgressBar`, `SetCaption`, `Finish`, `Set64`, `Read`, `SetTotal`, `cursorAnimate`, `fixateBarCaption`, and `getFixedWidth`.

Control flow: `newPB` configures byte units, refresh rate, no automatic newline, speed display, and a colorized callback. `newProgressReader` returns a proxy reader with optional fixed caption. `Read` delegates to pb and clamps progress to total after retries. Caption functions fit display text to a percentage of terminal width.

State and persistence: no durable state; progress state is in memory and terminal output.

Dependencies and integration: used by `put`, `pipe`, `mirror` status implementations, and other transfer flows. Depends on global terminal width and console colorization.

Risks and tests: `cursorAnimate` starts an endless goroutine for every call. Caption truncation uses byte length rather than display width. No direct progress-bar tests in this subset.
<!-- END_FILE_RESEARCH: sources/object-store/minio-mc/cmd/progress-bar.go -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio-mc/cmd/put-main.go -->
## sources/object-store/minio-mc/cmd/put-main.go

Purpose: implements `mc put`, uploading one or more local files to an S3 object target with multipart, checksum, storage class, encryption, and progress support.

Important APIs and functions: `putFlags`, `putCmd`, `mainPut`, `printPutURLsError`, and `showLastProgressBar`.

Control flow: `mainPut` validates argument count, parses part size and thread count, encryption keys, checksum, storage class, and source/target arguments. A goroutine prepares `URLs` via `preparePutURLs`, updates total byte/object counts and progress total, and sends work to `putURLsCh`. The main loop handles context cancellation, preparation errors, and calls `doCopy` for each upload with multipart size/thread settings and optional `if-not-exists`.

State and persistence: writes objects to the target. Progress totals are mutable local state. No local config mutation.

Dependencies and integration: depends on `preparePutURLs`, `doCopy`, transfer progress readers, humanize parsing, checksum parsing, SSE validation, and shared copy URL structs.

Risks and tests: the preparer goroutine updates `totalBytes` and `pg` while the main goroutine may read/finish progress. Only local file sources and S3 targets are accepted by `put-url.go`. No direct tests.
<!-- END_FILE_RESEARCH: sources/object-store/minio-mc/cmd/put-main.go -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio-mc/cmd/put-url.go -->
## sources/object-store/minio-mc/cmd/put-url.go

Purpose: classifies and prepares source/target `URLs` for `mc put`.

Important APIs and functions: `preparePutURLs` wraps URL preparation in channels; `guessPutURLType` validates supported source/target combinations and selects copy type A or B.

Control flow: `preparePutURLs` calls `guessPutURLType`, maps type A to `prepareCopyURLsTypeA`, type B to `prepareCopyURLsTypeB`, and forwards any errors. `guessPutURLType` supports exactly one source. It stats the source, requires the source client to be filesystem, rejects directories as unsupported type C, requires the target client to be `S3Client`, requires a non-empty bucket, and treats empty or trailing-separator object paths as folder targets.

State and persistence: no direct mutation; emits prepared work that `put-main.go` uploads.

Dependencies and integration: uses alias expansion, `url2Stat`, client constructors, S3 bucket/object parsing, MinIO `ObjectInfo`, and copy URL helpers from the copy subsystem.

Risks and tests: multiple sources are rejected as invalid despite `mainPut` accepting `SOURCE [SOURCE...] TARGET` shape. Error text has a capitalized period style. No direct tests cover put URL classification.
<!-- END_FILE_RESEARCH: sources/object-store/minio-mc/cmd/put-url.go -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio-mc/cmd/quota-clear.go -->
## sources/object-store/minio-mc/cmd/quota-clear.go

Purpose: implements `mc quota clear`, removing bucket quota configuration.

Important APIs and functions: `quotaClearCmd`, `checkQuotaClearSyntax`, and `mainQuotaClear`.

Control flow: syntax requires exactly one target. The handler sets colors, creates an admin client for the target alias, derives the bucket path with `url2Alias`, calls `SetBucketQuota` with an empty `madmin.BucketQuota`, and prints a `quotaMessage`.

State and persistence: mutates remote bucket quota state by clearing it. No local storage mutation.

Dependencies and integration: uses `madmin.AdminClient`, `quotaMessage` from `quota-set.go`, shared output and fatal handling.

Risks and tests: bucket name extraction uses `url2Alias(args[0])` and assumes the path is a bucket suitable for quota APIs. There are no direct quota tests.
<!-- END_FILE_RESEARCH: sources/object-store/minio-mc/cmd/quota-clear.go -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio-mc/cmd/quota-info.go -->
## sources/object-store/minio-mc/cmd/quota-info.go

Purpose: implements `mc quota info`, displaying current bucket quota configuration.

Important APIs and functions: `quotaInfoCmd`, `checkQuotaInfoSyntax`, and `mainQuotaInfo`.

Control flow: syntax requires exactly one target. The handler creates an admin client, derives target bucket, calls `GetBucketQuota`, chooses `qCfg.Size` when nonzero otherwise `qCfg.Quota`, and prints a `quotaMessage` with quota type and size.

State and persistence: read-only remote operation; no persistent mutation.

Dependencies and integration: uses `madmin` quota APIs, shared `quotaMessage`, `probe.NewError`, and command/global output flags.

Risks and tests: legacy fields `Quota` and `Size` are reconciled by preference but edge cases with both set are implicit. No direct tests.
<!-- END_FILE_RESEARCH: sources/object-store/minio-mc/cmd/quota-info.go -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio-mc/cmd/quota-main.go -->
## sources/object-store/minio-mc/cmd/quota-main.go

Purpose: groups bucket quota subcommands under `mc quota`.

Important APIs and variables: `quotaSubcommands` lists `set`, `info`, and `clear`; `quotaCmd` defines the parent command; `mainQuota` handles parent invocation.

Control flow: invoking the parent without a valid subcommand delegates to `commandNotFound`, which can suggest closest subcommands or fail with a global error.

State and persistence: parent command itself performs no remote mutation; subcommands do.

Dependencies and integration: registered in `appCmds` from `main.go` and shares global flags/setup. It depends on subcommand variables defined in sibling quota files.

Risks and tests: no custom help template in this file, so parent UX depends on default CLI behavior plus `commandNotFound`. No direct tests.
<!-- END_FILE_RESEARCH: sources/object-store/minio-mc/cmd/quota-main.go -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio-mc/cmd/quota-set.go -->
## sources/object-store/minio-mc/cmd/quota-set.go

Purpose: implements `mc quota set` and defines the shared quota output message type.

Important APIs and types: `quotaSetCmd`, `quotaMessage`, `checkQuotaSetSyntax`, and `mainQuotaSet`. `quotaMessage.String` formats set, clear, and info variants; `JSON` emits structured output.

Control flow: syntax requires one target and `--size`. The handler parses size with `humanize.ParseBytes`, uses `madmin.HardQuota`, constructs an admin client, calls `SetBucketQuota`, and prints success.

State and persistence: mutates remote bucket quota state to a hard quota. No local state changes.

Dependencies and integration: uses `madmin.BucketQuota`, humanize byte parsing, colorized console themes, shared output, and sibling quota commands for message reuse.

Risks and tests: only hard quotas are supported by this CLI path. Size zero is not explicitly rejected. No direct tests.
<!-- END_FILE_RESEARCH: sources/object-store/minio-mc/cmd/quota-set.go -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio-mc/cmd/rb-main.go -->
## sources/object-store/minio-mc/cmd/rb-main.go

Purpose: implements `mc rb`, removing buckets or filesystem directory hierarchies, with force and site-wide safety controls.

Important APIs and functions: `rbCmd`, `removeBucketMessage`, `checkRbSyntax`, `listBucketsURLs`, `deleteBucket`, `isS3NamespaceRemoval`, and `mainRemoveBucket`.

Control flow: syntax requires targets and blocks alias-wide object-store namespace removal unless both `--force` and `--dangerous` are set. `mainRemoveBucket` stats each target, checks emptiness, requires force for non-empty targets, expands namespace removals into buckets, and calls `deleteBucket`. `deleteBucket` streams recursive listed contents to `Client.Remove`, then removes the bucket, retrying force removal on `BucketNotEmpty`.

State and persistence: destructive remote or filesystem mutation. Can delete all buckets under an alias when explicitly forced and marked dangerous.

Dependencies and integration: uses `Client.List`, `Client.Remove`, `Client.RemoveBucket`, S3 error conversion, URL alias helpers, and shared fatal/output functions.

Risks and tests: highly destructive path with safety checks dependent on URL classification. Listing errors inside emptiness checks are ignored. Direct tests are absent.
<!-- END_FILE_RESEARCH: sources/object-store/minio-mc/cmd/rb-main.go -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio-mc/cmd/ready-main.go -->
## sources/object-store/minio-mc/cmd/ready-main.go

Purpose: implements `mc ready`, polling MinIO health until the cluster is ready.

Important APIs and types: `readyCmd`, `readyFlags`, `readyMessage`, and `mainReady`.

Control flow: syntax requires a target. The handler builds an anonymous admin client, creates `madmin.HealthOpts` from `--cluster-read` and `--maintenance`, then starts an immediate timer. On each tick it calls `anonClient.Healthy`, prints a `readyMessage`, returns nil if healthy, otherwise waits five seconds and retries until context cancellation.

State and persistence: read-only remote health checks. No local persistence.

Dependencies and integration: uses `madmin.AnonymousClient.Healthy`, shared global context, JSON/human output via `printMsg`, and color formatting.

Risks and tests: command can loop indefinitely for unhealthy clusters. It prints errors but does not exit immediately on unreachable states unless context is cancelled. No direct tests.
<!-- END_FILE_RESEARCH: sources/object-store/minio-mc/cmd/ready-main.go -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio-mc/cmd/replicate-add.go -->
## sources/object-store/minio-mc/cmd/replicate-add.go

Purpose: implements `mc replicate add`, configuring a remote replication target and adding a bucket replication rule.

Important APIs and types: `replicateAddCmd`, `replicateAddMessage`, `extractCredentialURL`, `fetchRemoteTarget`, `getBandwidthInBytes`, and `mainReplicateAdd`.

Control flow: syntax requires one source target and `--remote-bucket`. Remote credentials are extracted either from URL userinfo-like forms or existing aliases; temporary tokens are rejected. `fetchRemoteTarget` validates path style, target bucket, bandwidth, proxy, sync, region, and health interval into `madmin.BucketTarget`. The handler ensures the source is S3, registers the remote target through admin API, fetches existing replication config, translates `--replicate` options into replication flags, and calls `SetReplication(AddOption)`.

State and persistence: mutates remote target configuration and bucket replication XML/configuration on the source bucket.

Dependencies and integration: uses `madmin`, MinIO replication package, alias config, credential regexes, S3 bucket validation, and shared CLI output.

Risks and tests: credentials embedded in CLI arguments are parsed and then stored in remote target config. Priority is required by help but not explicitly checked for nonzero here. No direct tests.
<!-- END_FILE_RESEARCH: sources/object-store/minio-mc/cmd/replicate-add.go -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio-mc/cmd/replicate-backlog.go -->
## sources/object-store/minio-mc/cmd/replicate-backlog.go

Purpose: implements `mc replicate backlog` and alias `diff`, showing recent replication failures or full unreplicated-object diffs.

Important APIs and types: `replicateBacklogCmd`, `replicateMRFMessage`, `replicateBacklogMessage`, `replicateBacklogUI`, `keyMap`, `initReplicateBacklogUI`, `waitForActivity`, table header/style helpers, UI `Update`/`View`, and `mainReplicateBacklog`.

Control flow: the command parses bucket/prefix from the target. Without `--full`, it calls `BucketReplicationMRF` for recent failures by node; with `--full`, it calls `BucketReplicationDiff` with verbose, ARN, and prefix options. JSON mode streams each message directly. Human mode runs a Bubble Tea UI with spinner, table, key bindings, and a 10,000-row in-memory display cap.

State and persistence: read-only remote admin streams; local in-memory UI buffers rows and counts. No persistent mutations.

Dependencies and integration: uses `madmin` replication backlog APIs, Bubble Tea/Bubbles/Lipgloss terminal UI, `PrettyTable`, node color helpers, global JSON flag, and console output.

Risks and tests: `waitForActivity` reads from channels without checking closure, relying on sentinel empty records. Human UI caps displayed rows and asks JSON for full listing. No direct tests cover UI or stream closure.
<!-- END_FILE_RESEARCH: sources/object-store/minio-mc/cmd/replicate-backlog.go -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio-mc/cmd/replicate-export.go -->
## sources/object-store/minio-mc/cmd/replicate-export.go

Purpose: implements `mc replicate export`, printing a bucket replication configuration.

Important APIs and types: `replicateExportCmd`, `checkReplicateExportSyntax`, `replicateExportMessage`, and `mainReplicateExport`.

Control flow: syntax requires one target. The handler creates a client, calls `GetReplication`, and prints a message. Human output prints only the replication config JSON or a no-config message; JSON mode wraps it with operation/status/url fields.

State and persistence: read-only object-store operation.

Dependencies and integration: uses MinIO replication config type, `colorjson` for marshaling, shared output and fatal helpers.

Risks and tests: human output is JSON even when global JSON mode is false, which is intentional for export but different from most commands. No direct tests.
<!-- END_FILE_RESEARCH: sources/object-store/minio-mc/cmd/replicate-export.go -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio-mc/cmd/replicate-import.go -->
## sources/object-store/minio-mc/cmd/replicate-import.go

Purpose: implements `mc replicate import`, reading replication configuration JSON from stdin and applying it to a bucket.

Important APIs and types: `replicateImportCmd`, `checkReplicateImportSyntax`, `replicateImportMessage`, `readReplicationConfig`, and `mainReplicateImport`.

Control flow: syntax requires one target. `readReplicationConfig` decodes a `replication.Config` from `os.Stdin`. The handler creates a client, reads config, calls `SetReplication` with `ImportOption`, and prints success.

State and persistence: mutates bucket replication configuration on the target bucket.

Dependencies and integration: uses `colorjson` decoder, MinIO replication config APIs, shared fatal/output functions, and global context.

Risks and tests: stdin must be valid JSON matching the replication config structure. No validation of remote targets occurs in this file; server/client `SetReplication` must reject incompatible configs. No direct tests.
<!-- END_FILE_RESEARCH: sources/object-store/minio-mc/cmd/replicate-import.go -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio-mc/cmd/replicate-list.go -->
## sources/object-store/minio-mc/cmd/replicate-list.go

Purpose: implements `mc replicate list`/`ls`, displaying bucket replication rules and resolving remote target endpoints.

Important APIs and types: `replicateListCmd`, `checkReplicateListSyntax`, `printReplicateListHeader`, `replicateListMessage`, and `mainReplicateList`.

Control flow: the handler fetches replication config, errors if empty, prints a header in human mode, lists remote targets through admin API, optionally filters rules by `--status`, and prints each rule. String output resolves destination ARN to bucket and endpoint when possible, then shows rule ID, priority, ARN, optional prefix/tags/storage class.

State and persistence: read-only remote calls.

Dependencies and integration: uses `Client.GetReplication`, `madmin.ListRemoteTargets`, MinIO replication rule types, ARN parsing, shared color/output utilities.

Risks and tests: `--status` accepts any string and only filters by case-insensitive equality; invalid values silently produce no rows. No direct tests.
<!-- END_FILE_RESEARCH: sources/object-store/minio-mc/cmd/replicate-list.go -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio-mc/cmd/replicate-main.go -->
## sources/object-store/minio-mc/cmd/replicate-main.go

Purpose: parent command for server-side bucket replication management.

Important APIs and variables: `replicateSubcommands` lists add, update, list, status, resync/reset, export, import, remove, and backlog; `replicateCmd` defines the parent; `mainReplicate` handles unknown or missing subcommands.

Control flow: parent invocation delegates to `commandNotFound`, while subcommands own their handlers and validation.

State and persistence: no direct state mutation; subcommands can mutate remote replication configuration.

Dependencies and integration: registered in `appCmds`; depends on sibling command variables, including some not in this subset (`replicateUpdateCmd`, `replicateStatusCmd`).

Risks and tests: compile-time integration requires all referenced subcommand variables to exist. No direct tests for parent routing.
<!-- END_FILE_RESEARCH: sources/object-store/minio-mc/cmd/replicate-main.go -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio-mc/cmd/replicate-remove.go -->
## sources/object-store/minio-mc/cmd/replicate-remove.go

Purpose: implements `mc replicate remove`/`rm`, removing one replication rule or all replication configuration.

Important APIs and types: `replicateRemoveCmd`, `checkReplicateRemoveSyntax`, `replicateRemoveMessage`, and `mainReplicateRemove`.

Control flow: syntax requires one target. `--all` and `--force` must appear together; otherwise a non-empty `--id` is required. The handler fetches replication config. All+force calls `RemoveReplication`; single-rule mode finds the destination ARN for that rule, calls `SetReplication(RemoveOption)`, then removes the corresponding remote target with admin API.

State and persistence: mutates replication rules and possibly remote target configuration on the source bucket.

Dependencies and integration: uses MinIO replication options, `madmin.RemoveRemoteTarget`, source bucket extraction, shared output.

Risks and tests: if the rule ID is not found, `removeArn` remains empty but the code still attempts rule removal and remote-target removal. Output string misses a space before "removed". No direct tests.
<!-- END_FILE_RESEARCH: sources/object-store/minio-mc/cmd/replicate-remove.go -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio-mc/cmd/replicate-reset-main.go -->
## sources/object-store/minio-mc/cmd/replicate-reset-main.go

Purpose: parent command for replication resync/reset operations.

Important APIs and variables: `replicateResyncSubcommands` lists `start` and `status`; `replicateResyncCmd` defines `mc replicate resync`, alias `reset`, and hidden aliases; `mainReplicateResync` handles parent invocation.

Control flow: invoking the parent without a valid subcommand delegates to `commandNotFound`; subcommands perform actual resync work.

State and persistence: no direct mutation in the parent. `start` mutates server-side resync state; `status` reads it.

Dependencies and integration: included under `replicateSubcommands` in `replicate-main.go`.

Risks and tests: alias compatibility is handled by CLI metadata. No direct tests.
<!-- END_FILE_RESEARCH: sources/object-store/minio-mc/cmd/replicate-reset-main.go -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio-mc/cmd/replicate-reset-start.go -->
## sources/object-store/minio-mc/cmd/replicate-reset-start.go

Purpose: implements `mc replicate resync start`, initiating re-replication of previously replicated objects for a remote target.

Important APIs and types: `replicateResyncStartCmd`, `checkReplicateResyncStartSyntax`, `replicateResyncMessage`, and `mainReplicateResyncStart`.

Control flow: syntax requires one target and `--remote-bucket`. Optional `--older-than` is parsed with `ParseDuration`, must include day/week/year-like units by string check, and must be nonzero. The handler creates a client, calls `ResetReplication(ctx, olderThan, remoteBucket)`, and prints target reset info.

State and persistence: mutates server-side replication resync/reset state for the bucket/target.

Dependencies and integration: uses MinIO replication resync APIs, custom duration parser, global context, and shared output.

Risks and tests: unit validation checks `strings.ContainsAny(olderThanStr, "dwy")`, but parser tests in this subset cover days/weeks, not years. Error handling passes possibly nil parse errors to `probe.NewError`. No direct tests.
<!-- END_FILE_RESEARCH: sources/object-store/minio-mc/cmd/replicate-reset-start.go -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio-mc/cmd/replicate-reset-status.go -->
## sources/object-store/minio-mc/cmd/replicate-reset-status.go

Purpose: implements `mc replicate resync status`, showing replication reset progress for all or one remote target.

Important APIs and types: `replicateResyncStatusCmd`, `checkreplicateResyncStatusSyntax`, `replicateResyncStatusMessage`, and `mainreplicateResyncStatus`.

Control flow: syntax requires one target. The handler creates a client, calls `ReplicationResyncStatus(ctx, remoteBucket)`, and prints the message. String output shows a warning when no status exists; otherwise it formats each target ARN, status, replicated size/count, and failed size/count with `PrettyTable`.

State and persistence: read-only server-side resync status.

Dependencies and integration: uses replication resync info types, humanize formatting, shared color themes, `PrettyTable`, and `printMsg`.

Risks and tests: function names use lowercase `replicate` after `main`, which is legal but inconsistent. The "Failed" row is colorized with the replicated theme index in one call. No direct tests.
<!-- END_FILE_RESEARCH: sources/object-store/minio-mc/cmd/replicate-reset-status.go -->
