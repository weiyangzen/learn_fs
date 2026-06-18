# Research: subset-b-009776

Grouped research for rclone operation, rc, pacing, override, duration/time parsing, and job-control files. Each section preserves its source path for deterministic splitting.

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/fs/operations/operations_test.go -->
## sources/user-network-fs/rclone/fs/operations/operations_test.go

Purpose: broad integration and unit coverage for `fs/operations`, usually through `fstest.Run` against local or configured remotes. It validates public operation behavior rather than implementing production APIs. Important signals include listing variants, `HashLister`, `HashSumStream`, delete/max-delete limits, `Cat`, `Purge`, `Rmdirs`, `CopyURL`, `MoveFile`, overlap checks, `ListFormat`, `DirMove`, `Rcat`, directory metadata/modtime, `DirsEqual`, and `RemoveExisting`.

Control flow is table-driven where possible and otherwise builds remote/local fixtures, writes objects, invokes operations, then checks object and directory listings with precision-aware assertions. State is mostly test fixture state plus context-local config mutations via `fs.AddConfig`, filter replacement, accounting resets, and backend feature toggles. Integration points cover `fstest`, `filter`, `accounting`, `fshttp`, `hash`, `pacer`, and backend feature interfaces. Risks caught include global config non-concurrency, backend capability skips, eventual listing consistency, delete safeguards, case-insensitive moves, metadata support, and temporary backup cleanup. Test signal is very strong for operations behavior across real backends.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/fs/operations/operations_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/fs/operations/operationsflags/operationsflags.go -->
## sources/user-network-fs/rclone/fs/operations/operationsflags/operationsflags.go

Purpose: defines CLI flag helpers for operations logger/report outputs, kept in a separate package so command wiring can be replaced. APIs include embedded `Help`, `AddLoggerFlagsOptions`, `AnySet`, `AddLoggerFlags`, and `ConfigureLoggers`. `AddLoggerFlags` registers report file flags and related `lsf` formatting flags into a `pflag.FlagSet`, filling `operations.LoggerOpt`.

Control flow in `ConfigureLoggers` normalizes time format, initializes list formatting against the destination filesystem, opens each requested report destination, and returns a closer that logs close failures. State is limited to passed option structs and opened file handles; persistence is the report files created with `os.Create`, or stdout for `-`. Dependencies include Cobra/pflag, rclone flag helpers, hash selection, and `operations.LoggerOpt`. Integration points are sync/check commands that need combined/missing/match/differ/error/dest-after reports. Risks include truncating existing report files, caller responsibility to invoke the closer, and warnings for `--no-traverse` combinations that make some reports incomplete.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/fs/operations/operationsflags/operationsflags.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/fs/operations/rc.go -->
## sources/user-network-fs/rclone/fs/operations/rc.go

Purpose: registers remote-control endpoints that expose `fs/operations` behavior as `rc.Call`s. It wires `operations/list`, `stat`, `about`, `copyfile`, `movefile`, single-command mutators, `size`, `publiclink`, `fsinfo`, `backend/command`, `core/du`, `check`, `hashsum`, and `hashsumfile`. Important functions are `rcList`, `rcStat`, `rcAbout`, `rcMoveOrCopyFile`, `rcSingleCommand`, `rcSize`, `rcPublicLink`, `rcFsInfo`, `rcBackend`, `rcDu`, `rcCheck`, `parseHashParameters`, `rcHashsum`, and `rcHashsumFile`.

Control flow mostly parses `rc.Params`, resolves filesystems with `rc.GetFs*`, delegates to operations functions, and shapes results into `rc.Params`. Multipart upload streams request parts into `Rcat`; check/hash endpoints capture writer output into string slices. There is no durable state except remote filesystem mutations and uploaded data. Dependencies include rc cache helpers, config cache-dir, hash parsing, disk usage, HTTP/multipart parsing, and backend feature methods. Risks include parameter validation drift from CLI behavior, feature nil checks, closure capture in registration loops, upload path joining, partial report defaults in `rcCheck`, and unsupported hash/backend paths. Tests in `rc_test.go` cover most endpoint contracts.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/fs/operations/rc.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/fs/operations/rc_test.go -->
## sources/user-network-fs/rclone/fs/operations/rc_test.go

Purpose: endpoint-level tests for `fs/operations/rc.go`. `rcNewRun` constrains tests to local remotes, creates a fixture, finds the registered call, and seeds the fs cache. Tests cover about/cleanup, copy/move file, copyurl, delete/deletefile, list/stat, tier operations, mkdir/rmdir/rmdirs/purge, size, publiclink, fsinfo, multipart uploadfile, backend command, disk usage, check, hashsum, single-file hashsum, and hashsumfile.

Control flow sets up local/remote files, invokes `call.Fn(context.Background(), rc.Params{...})`, then asserts returned params and final listings. State and persistence are fixture filesystem writes, cache entries, HTTP test servers, multipart request bodies, and generated remote objects. Dependencies include `fstest`, `cache`, `hash`, `diskusage`, `rest.MultipartUpload`, and `httptest`. Integration points verify rc parameter names and output shapes expected by API clients. Risks signaled include unsupported backend features, non-local remote skips, map/slice type shapes after `rc.Reshape`, check report ordering requiring sorting, and hash support variations. Test signal is strong for externally visible rc behavior.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/fs/operations/rc_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/fs/operations/reopen.go -->
## sources/user-network-fs/rclone/fs/operations/reopen.go

Purpose: implements `ReOpen`, an `io.ReadSeekCloser`/`io.ReaderAt` wrapper around `fs.Object.Open` that retries failed reads by reopening the object at the current offset. APIs include `AccountFn`, `NewReOpen`, convenience `Open`, `Read`, `ReadAt`, `Seek`, `Close`, `SetAccounting`, and `DelayAccounting`.

Control flow records base open options, strips hash options for nonzero-range reopen attempts, tracks optional range/seek starts and ends, and mutates a stored `fs.RangeOption` before reopening. `Read` serializes through `mu`, applies pending seeks, fills the caller buffer, reopens on retryable read errors, and accounts bytes after optional delayed full-data reads. `ReadAt` serializes separately, seeks, reads, then restores position. State is in-memory offsets, retry counters, current reader, open/error flags, and accounting counters; no persistence. Dependencies include `fs.OpenOption`, `fserrors`, and object size semantics. Risks include mutable option aliasing, unknown-size seek-end behavior, sticky errors after failures/close, serialized `ReadAt` rather than true parallel reads, and exact retry-count semantics.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/fs/operations/reopen.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/fs/operations/reopen_test.go -->
## sources/user-network-fs/rclone/fs/operations/reopen_test.go

Purpose: unit tests for `ReOpen` retry, seek, range, unknown-size, `ReadAt`, close, and accounting behavior. It defines `reOpenTestObject`, a mock object wrapper whose `Open` asserts requested start offsets and injects read or open failures at configured byte breakpoints.

Control flow runs the same nested test set across normal, range-option, seek-option, and unknown-size modes. It checks full reads, EOF, rewind, double close, immediate open error, retry recovery, too-many-retries sticky errors, `ReadAt` position preservation, seek validation, seek-from-end restrictions for unknown size, and accounting delay/error propagation. State is test-only expected offsets, injected break slices, accounting totals, and mock object size flags. Dependencies include `mockobject`, `fs.RangeOption`, `fs.SeekOption`, `HashesOption`, `pool.DelayAccountinger`, and `readers.ErrorReader`. Risks covered are option mutation by `fs.FixRangeOption`, hash options during ranged reopens, retry counters reset on seek, and serialized ReaderAt semantics. Test signal is high for the reader state machine.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/fs/operations/reopen_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/fs/override.go -->
## sources/user-network-fs/rclone/fs/override.go

Purpose: defines `OverrideRemote`, a lightweight `ObjectInfo` wrapper that substitutes the `Remote()` and `String()` value while forwarding optional object capabilities. APIs include `NewOverrideRemote`, `Remote`, `String`, `MimeType`, `ID`, `UnWrap`, `GetTier`, and `Metadata`.

Control flow is straightforward delegation: construction unwraps an existing `OverrideRemote` to avoid wrapper stacking, while optional methods type-assert the embedded `ObjectInfo` to capability interfaces and return default empty or nil values when unsupported. State is only the embedded object info and replacement remote string; persistence is none. Dependencies are core fs interfaces such as `ObjectInfo`, `Object`, `MimeTyper`, `IDer`, `GetTierer`, and `Metadataer`. Integration points are operations that need to upload/copy data under a different destination name while preserving source metadata, hashes, size, and optional object behavior. Risks are subtle interface exposure changes: unsupported optional methods silently return empty values, and `UnWrap` only returns when the wrapped value is an `Object`, not arbitrary nested wrappers.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/fs/override.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/fs/override_dir.go -->
## sources/user-network-fs/rclone/fs/override_dir.go

Purpose: defines `OverrideDirectory`, a `Directory` wrapper that changes `Remote()` and `String()` while preserving all other directory behavior through embedding. APIs are `NewOverrideDirectory`, `Remote`, and `String`.

Control flow mirrors `OverrideRemote`: construction unwraps an existing `OverrideDirectory` to keep a single wrapper around the original `Directory`, then stores the new remote name. State is only the embedded directory and replacement remote string. There is no persistence or concurrency behavior. Dependencies are the fs `Directory` interface. Integration points include directory listing, sync, and metadata flows that need a directory entry to be presented at a different path without copying or reconstructing all fields. Risks are low but include identity confusion when callers compare string/remote names to underlying directory fields, and the fact that optional directory capabilities are not explicitly forwarded beyond what embedding already exposes.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/fs/override_dir.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/fs/override_dir_test.go -->
## sources/user-network-fs/rclone/fs/override_dir_test.go

Purpose: compile-time interface assertion for `OverrideDirectory`. The single assertion verifies `*OverrideDirectory` satisfies `Directory`.

There is no runtime control flow, persistence, or fixture setup. Its primary test signal is API compatibility: if embedding or method signatures change so `OverrideDirectory` no longer implements the directory contract, compilation fails. Dependencies are limited to the local `fs` package interfaces. Integration relevance is narrow but important for wrappers passed anywhere a `Directory` is expected. Risk coverage is minimal; it does not validate constructor unwrapping, `Remote`, or `String` behavior.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/fs/override_dir_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/fs/override_test.go -->
## sources/user-network-fs/rclone/fs/override_test.go

Purpose: compile-time interface assertion for `OverrideRemote`. It verifies `*OverrideRemote` satisfies `FullObjectInfo`.

The file has no runtime control flow or persistent state. Its dependency is the local fs object-info interface set. The integration signal is that `OverrideRemote` can be passed to code requiring full object information, including operations that depend on metadata-capable object info wrappers. Risks not covered include forwarding correctness for optional methods, rewrapping behavior, nil metadata defaults, and `UnWrap` behavior; those are enforced by implementation review or higher-level operation tests rather than this file.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/fs/override_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/fs/pacer.go -->
## sources/user-network-fs/rclone/fs/pacer.go

Purpose: wraps `lib/pacer.Pacer` with rclone fs configuration defaults and logging. APIs include `Pacer`, `NewPacer`, `SetCalculator`, `ModifyCalculator`, and `pacerInvoker`. `logCalculator` decorates a pacer calculator to log sleep increases and decreases.

Control flow in `NewPacer` reads low-level retry and max-connection settings from context config, creates a pacer with invoker, connection, retry, and calculator options, then wraps the calculator for logging. `SetCalculator` converts nil to the default calculator and prevents double-wrapping. `ModifyCalculator` unwraps the logging decorator while the pacer lock is held. State lives inside the embedded pacer and calculator; no persistence. Dependencies include `fserrors.RetryError` and `lib/pacer`. Integration points are backend retry loops and rate-limit handling. Risks include logging volume under frequent rate limits, reliance on context config defaults, and invalid calculator types being tolerated with log messages. Tests cover retry wrapping and no-retry call counts.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/fs/pacer.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/fs/pacer_test.go -->
## sources/user-network-fs/rclone/fs/pacer_test.go

Purpose: validates `fs.Pacer` retry behavior. It defines `dummyPaced`, whose `fn` increments a call counter and returns a configured retry signal plus `errFoo`.

Control flow creates a pacer with short sleep bounds, invokes `Call` or `CallNoRetry`, and asserts call counts and returned error interface. `TestPacerCall` accounts for default low-level retry config, injecting a test config with 20 retries when needed. `TestPacerCallNoRetry` verifies a single invocation while still wrapping retry errors. State is test-local retry flags, counters, and optional condition variable support. Dependencies are `lib/pacer`, `fserrors.Retrier`, and context fs config. Integration signal is focused: callers can rely on retryable errors being wrapped and retry counts matching low-level retry settings. Risks not covered include calculator logging, max connection limiting, and `ModifyCalculator`.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/fs/pacer_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/fs/parseduration.go -->
## sources/user-network-fs/rclone/fs/parseduration.go

Purpose: implements `fs.Duration`, a flag/JSON/scanner-friendly duration type with rclone-specific suffixes and date parsing. APIs include `Duration`, `DurationOff`, `String`, `IsSet`, `ParseDuration`, readable string variants, `Set`, `Type`, `UnmarshalJSON`, and `Scan`.

Control flow parses `"off"`, Go durations, custom suffixes (`d`, `w`, `M`, `y`, default seconds), and absolute dates interpreted as duration before an epoch. Formatting chooses larger suffixes for `String`, while `readableString` decomposes into years/weeks/days/hours/minutes/seconds/milliseconds with optional truncation. JSON accepts strings or integer nanoseconds. State is none except package-level suffix and date format tables, and shared `timeNowFunc` from time parsing. Dependencies are standard `time`, `encoding/json`, `strconv`, and `fmt.Scanner`. Risks include approximate month/year definitions, local timezone date parsing, float conversions near max duration, empty string parse errors, and off sentinel collisions with max int64. Tests cover parsing, formatting round-trips, JSON, scanner, negatives, and readable strings.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/fs/parseduration.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/fs/parseduration_test.go -->
## sources/user-network-fs/rclone/fs/parseduration_test.go

Purpose: verifies `Duration` parsing, formatting, readable output, scanning, and JSON unmarshalling. It also asserts pointer and non-pointer flag interfaces.

Control flow uses table-driven tests with a fixed `now` callback for date-derived durations. It covers numeric defaults, Go duration syntax, custom suffixes, negative durations, `"off"`, absolute date formats, reverse `String` parsing, long and short readable strings, scanner input, JSON strings, JSON integer nanoseconds, invalid data, and max-int64 mapping to `DurationOff`. State mutation is limited to temporarily overriding `timeNowFunc` in scanner tests. Dependencies are `assert`, `require`, `encoding/json`, and `fmt.Sscan`. Integration points are config flags and rc/config JSON parsing that consume `Duration`. Risks highlighted include local-time tolerance for date tests, floating-point precision near `DurationOff`, and accepting raw integer JSON as nanoseconds. Test signal is strong for public conversion semantics.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/fs/parseduration_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/fs/parsetime.go -->
## sources/user-network-fs/rclone/fs/parsetime.go

Purpose: implements `fs.Time`, a `time.Time` wrapper for flags, scanning, and JSON that accepts absolute timestamps, relative durations before now, and `"off"` as zero time. APIs include `Time`, `String`, `IsSet`, `ParseTime`, `Set`, `Type`, `UnmarshalJSON`, `MarshalJSON`, and `Scan`.

Control flow first handles `"off"`, then tries shared absolute date formats, then Go duration syntax, then custom duration suffixes. Relative durations subtract from `timeNowFunc`, so negative durations produce future times. JSON unmarshalling requires a string; marshalling delegates to `time.Time`, so zero time emits the Go zero timestamp rather than `"off"`. State is limited to the package-level `timeNowFunc` used by both duration and time parsing. Dependencies are standard JSON/time/fmt and parser helpers from `parseduration.go`. Risks include local timezone date parsing, surprising JSON zero-time output, mutable global time callback in tests, and permissive bare numeric string interpretation as seconds. Tests cover parse, string round-trip, scanner, JSON, and relative behavior.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/fs/parsetime.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/fs/parsetime_test.go -->
## sources/user-network-fs/rclone/fs/parsetime_test.go

Purpose: tests `Time` parsing, formatting, scanner, JSON unmarshal, and JSON marshal behavior. It also asserts flag interfaces.

Control flow temporarily replaces `timeNowFunc` with a fixed instant, then runs table cases for empty/error input, relative units, bare numeric seconds, negative offsets, `"off"`, absolute local and RFC3339 dates, scanner reads, JSON string values, non-string JSON errors, and marshal output. State is the global time callback restored with defer. Dependencies include `encoding/json`, `fmt.Sscan`, and testify. Integration signal is strong for config/flag behavior where users specify cutoff times as either absolute timestamps or ages. Risks covered include erroring on non-string JSON, zero time semantics, local-vs-UTC dates, and future timestamps from negative relative inputs. A small gap is concurrency safety around the global test override, which relies on non-parallel tests.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/fs/parsetime_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/fs/rc/cache.go -->
## sources/user-network-fs/rclone/fs/rc/cache.go

Purpose: provides rc helpers for resolving filesystem parameters and exposes fs-cache rc endpoints. APIs include `GetFsNamed`, `GetFsNamedFileOK`, `GetFs`, `GetFsAndRemoteNamed`, `GetFsAndRemote`, plus registered `fscache/clear` and `fscache/entries`.

Control flow parses a named parameter as either a string fs path or a structured config map. Structured configs use `type` or `_name`, optional `_root`, and remaining config values to build an fspath. `GetFsNamedFileOK` handles `fs.ErrorIsFile` by adding a single-file filter to a new context. State/persistence lives in the global `fs/cache` package; this file only clears or counts it. Dependencies include `cache.Get`, `configmap.Simple`, `filter`, and `fspath.Split`. Integration points are nearly all rc operation handlers. Risks include structured config string escaping, rejecting single-file limiting when filters are already active, global cache invalidation through `fscache/clear`, and parameter type ambiguity. Tests cover string, struct, single-file, and cache endpoints.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/fs/rc/cache.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/fs/rc/cache_test.go -->
## sources/user-network-fs/rclone/fs/rc/cache_test.go

Purpose: unit tests for rc fs-resolution helpers and fscache endpoints. `mockNewFs` seeds the global cache with mock filesystems and an `ErrorIsFile` entry.

Control flow tests normal named fs lookup, missing parameters, structured config maps with `type` or `_name`, single-file resolution creating include filters, `getConfigMap` error and string generation cases, default `GetFs`, remote pairing helpers, and nested `fscache/entries`/`clear` rc calls. State is global cache content that is cleared via deferred cleanup, plus context-local filter replacement for single-file cases. Dependencies include `mockfs`, `cache`, `filter`, and testify. Integration signal is high because rc operations rely on these helper functions for every filesystem parameter. Risks covered include invalid structured config values, missing keys, active-filter incompatibility for single-file scopes, and cache clearing. Remaining gaps include config value quoting edge cases beyond the tested generated string.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/fs/rc/cache_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/fs/rc/config.go -->
## sources/user-network-fs/rclone/fs/rc/config.go

Purpose: implements rc endpoints for reading and mutating global and local option blocks without creating an fs package cycle. Registered paths are `options/blocks`, `options/get`, `options/info`, `options/local`, and `options/set`.

Control flow lists `fs.OptionsRegistry`, filters selected block names from an optional comma-separated `blocks` parameter, returns either current option structs or option metadata, returns context-local config/filter state, and writes option blocks via `Reshape`. `options/set` calls a block reload hook when present. State is significant: it mutates global option structs registered in `fs.OptionsRegistry`, while `options/local` reads context-local config/filter values. There is no file persistence here, but changed options can affect later operations process-wide. Dependencies include `fs.OptionsRegistry`, `filter.GetConfig`, and rc reshape utilities. Risks include global mutable state, unknown block errors, silently ignored unknown fields inside known blocks through reshape behavior, reload failure after partial mutation, and exposing internal option field names. Tests cover selection, marshalability, mutation, reload, and errors.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/fs/rc/config.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/fs/rc/config_test.go -->
## sources/user-network-fs/rclone/fs/rc/config_test.go

Purpose: tests rc option registry endpoints and mutation behavior. It uses `clearOptionBlock` to replace `fs.OptionsRegistry` with a temporary map, registers a synthetic `potato` option block, and optionally attaches a reload callback.

Control flow verifies registration, `options/blocks`, filtered and unfiltered `options/get`, JSON marshalability with real main/rc options, `options/info`, and `options/set`. Mutation tests assert a single field update reshapes defaults, reload is called, reload errors propagate, unknown blocks error, and bad payload shapes error. State is global option registry and shared `testOptions`, restored after each test. Dependencies are `fs.RegisterGlobalOptions`, `rc.Calls`, JSON, and testify. Integration signal is strong for API clients changing runtime options. Risks covered include global state restoration, reload side effects, and block filtering. A residual risk is that tests depend on reshape behavior setting omitted fields to defaults, which is important for callers but can surprise partial update users.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/fs/rc/config_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/fs/rc/disks.go -->
## sources/user-network-fs/rclone/fs/rc/disks.go

Purpose: platform-supported implementation of `getMounts` for `core/disks`, compiled except on `netbsd/386`. It uses `gopsutil/v4/disk.Partitions(false)` and returns each partition mountpoint.

Control flow ignores the partitions error, iterates all returned partitions, and appends `Mountpoint` strings. State and persistence are none. Dependencies are `github.com/shirou/gopsutil/v4/disk` and build tags. Integration point is `rcDisks` in `internal.go`, which filters these mount points through `mountOK` and combines them with home/root/user dirs. Risks include silently returning no mounts on gopsutil error, platform-specific mount naming, and potentially including duplicate or inaccessible mountpoints before later filtering. Test coverage for final disk output is in `internal_test.go`, not this file directly.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/fs/rc/disks.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/fs/rc/disks_unsupported.go -->
## sources/user-network-fs/rclone/fs/rc/disks_unsupported.go

Purpose: fallback `getMounts` implementation for `netbsd && 386`, where the gopsutil-backed disk implementation is excluded. It returns a single mount point, `"/"`.

Control flow and state are trivial: no dependencies beyond the local package and no persistence. Integration point is `rcDisks` in `internal.go`, which will include root and user directories and deduplicate paths. Risk is reduced functionality on this platform, since only root is surfaced as a mount candidate. The build tag makes correctness dependent on Go’s build selection. There is no direct unit test for this build-constrained file in the current platform run.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/fs/rc/disks_unsupported.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/fs/rc/internal.go -->
## sources/user-network-fs/rclone/fs/rc/internal.go

Purpose: registers core/internal rc endpoints: noop, error, panic/fatal test calls, command listing, pid, memory stats, GC, version, obscure, quit, runtime debug knobs, raw `core/command`, and local disk discovery. Key functions include `rcNoop`, `rcError`, `rcPanic`, `rcFatal`, `rcList`, `rcPid`, `rcMemStats`, `rcGc`, `rcVersion`, `rcObscure`, `rcQuit`, debug setters, `rcRunCommand`, `mountOK`, and `rcDisks`.

Control flow is mostly direct parameter parsing and response construction. `rcQuit` exits asynchronously after running atexit hooks. `rcRunCommand` reconstructs command-line args from `command`, `arg`, and `opt`, executes the current binary, and either returns combined output or streams stdout/stderr to an HTTP response. State includes process runtime settings, memory stats, exit scheduling, and external subprocess execution; no durable files are written by this file. Dependencies include buildinfo, obscure, xdg dirs, runtime/debug, os/exec, and rc HTTP response hooks. Risks include exposing command execution, process termination, global runtime knob mutation, response object requirements for streaming, and platform-specific disk filtering. Tests cover most endpoints.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/fs/rc/internal.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/fs/rc/internal_job_test.go -->
## sources/user-network-fs/rclone/fs/rc/internal_job_test.go

Purpose: external-package tests ensuring internal `rc/panic` and `rc/fatal` behavior is safely captured by the job framework. They invoke registered calls through `jobs.NewJob`.

Control flow finds `rc/panic` or `rc/fatal`, runs it synchronously as a job, and asserts the returned error includes the original message plus panic/fatal framing and that output is an empty params map. State is limited to the global rc call registry and global job queue side effects. Dependencies are `fs/rc`, `fs/rc/jobs`, and testify. Integration signal is important because direct panic/fatal calls would otherwise crash the process; through jobs they become structured job failures with stack text. Risks covered include panic recovery and fatal-to-panic wrapping. It does not test the direct call path outside jobs, which is intentionally unsafe for these endpoints.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/fs/rc/internal_job_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/fs/rc/internal_test.go -->
## sources/user-network-fs/rclone/fs/rc/internal_test.go

Purpose: tests internal/core rc endpoints. `TestMain` simulates current-binary behavior for `core/command` by intercepting `version` and `unknown_command` arguments.

Control flow tests noop echo, error, command list, pid type, memory stats, GC nil output, version fields, obscure/reveal, quit parameter validation, `core/command` combined and streaming return types, and `core/disks` output shape. State touched includes process args in `TestMain`, runtime memory reads, HTTP recorder bodies, and current executable subprocesses. Dependencies include `httptest`, `obscure`, `fs.Version`, runtime info, and rc call registry. Integration signal is high for GUI/API clients using core endpoints. Risks covered include subprocess error handling, stdout/stderr stream routing, required response writer, non-empty disk paths, and platform-dependent version fields. Destructive paths like successful `core/quit` are intentionally not executed.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/fs/rc/internal_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/fs/rc/jobs/job.go -->
## sources/user-network-fs/rclone/fs/rc/jobs/job.go

Purpose: manages synchronous/asynchronous rc jobs, job status/list/stop/group-stop endpoints, JSON job dispatch, and batch execution. APIs include `Job`, `Jobs`, `NewJob`, `OnFinish`, `GetJob`, `GetJobID`, `NewJobFromParams`, `NewJobFromBytes`, and `rcBatch`.

Control flow creates jobs with atomic IDs and process-wide `executeID`, parses special `_async`, `_config`, `_filter`, and `_group` parameters, wraps contexts with cancellation and RC markers, runs functions in goroutines or inline, records output/error/duration, notifies finish listeners, and expires finished jobs after configured durations. Batch dispatch validates input objects and runs commands sequentially or via `errgroup` with a concurrency limit. State is global: `running`, `jobID`, job maps, timers, listeners, and links into `cache.JobOnFinish`. No disk persistence. Dependencies include rc registry, fs/accounting/filter/cache, UUID, errgroup, and HTTP status shaping. Risks include global mutable job state, listener races, cancellation blocking in `Stop`, closure capture in concurrent batch loops, special-parameter mutation, context detachment for async jobs, and expiration timing. Tests are extensive.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/fs/rc/jobs/job.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/fs/rc/jobs/job_test.go -->
## sources/user-network-fs/rclone/fs/rc/jobs/job_test.go

Purpose: comprehensive tests for job lifecycle, async/sync execution, context mutation, status/list/stop endpoints, listeners, JSON dispatch, and batch behavior. It defines helper job functions for no-op, long-running, short-running, context-cancelled, and context-parameter-controlled jobs.

Control flow covers new job maps, expiration timers, IDs and execute IDs, finish state, panic recovery, `_async` output, synchronous output/error propagation, `_config`, `_filter`, `_group`, RC request markers, job status/list, async and sync stop, stopgroup, `OnFinish` for running/already-finished jobs, listener race stress, `NewJobFromParams`, `NewJobFromBytes`, batch error shaping, and concurrent batch ordering for 100 inputs. State includes reset global `jobID`, global rc call registry, global running jobs for some tests, timers, and goroutines. Dependencies include accounting groups, filters, rc calls, JSON, and testify. Risks covered are broad: races, cancellation, panic conversion, invalid paths, request/response-ineligible calls, bad input types, and concurrency ordering.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/fs/rc/jobs/job_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/fs/rc/js/Makefile -->
## sources/user-network-fs/rclone/fs/rc/js/Makefile

Purpose: small developer Makefile for building and serving the rc WebAssembly JavaScript demo. Targets are `build` and `serve`.

Control flow is delegated to make: `build` runs `GOARCH=wasm GOOS=js go build -o rclone.wasm`; `serve` depends on `build` and runs `go run serve.go`. State/persistence is the generated `rclone.wasm` artifact in the working directory and any local server process launched by `serve`. Dependencies include Go’s wasm target and a local `serve.go` file outside this listed scope. Integration point is `loader.js`, which expects `rclone.wasm` and `wasm_exec.js` to be available. Risks include generated binary churn, implicit current package build target, no cleanup target, and missing `serve.go`/wasm support causing make failures. No tests directly cover this file.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/fs/rc/js/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/fs/rc/js/loader.js -->
## sources/user-network-fs/rclone/fs/rc/js/loader.js

Purpose: browser loader/demo for the rclone rc WebAssembly build. It dynamically loads `wasm_exec.js`, instantiates `rclone.wasm`, runs the Go runtime, waits for `rcValid`, and logs sample rc calls.

Control flow creates a global `rcValid` promise and resolver, injects a script tag, polyfills `WebAssembly.instantiateStreaming` when missing, constructs `new Go()`, fetches and instantiates wasm, and runs the module. After validity resolves, it calls `rc("core/version")`, `rc/noop`, `operations/mkdir`, and `operations/list` against a memory remote. State is global browser variables `rc`, `rcValidResolve`, and `rcValid`, plus DOM script insertion and the WebAssembly runtime. Dependencies include Go’s `wasm_exec.js`, `rclone.wasm`, browser fetch/WebAssembly APIs, and a wasm-exported `rc` function. Risks include globals, no fetch/instantiate error handling, sample calls running automatically, and dependency on same-origin assets. No automated tests are present.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/fs/rc/js/loader.js -->
