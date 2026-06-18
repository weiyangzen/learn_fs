# Research Group subset-b-009502

This grouped report covers syzkaller report fixtures plus reproduction, RPC execution, runtime test, serialization, signal, statistic, syzbot-stat, and subsystem support code. Each section is delimited for reconciliation into source-tree-aligned per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/starnix/report/2 -->
# sources/test-tools/syzkaller/pkg/report/testdata/starnix/report/2

## Purpose

This fixture is a captured Starnix crash report used by the report parser tests. It models a Rust panic in `netlink_packet_route::route::next_hops::RouteNextHopBuffer::attributes` from `third_party/rust_crates/forks/netlink-packet-route-0.20.0/src/route/next_hops.rs:78:31`, with the title normalized as a Starnix kernel panic and an overflow message.

## Important Content And Control Flow

The file begins with a `TITLE:` line, then raw console output with `STARNIX KERNEL PANIC`, panic text, `SYZFATAL` EOF from the executor RPC path, Rust backtrace frames, crashsvc/klog process exception details, module BuildID listings, register dumps, memory near PC, and a final `REPORT:` block. Parser control flow exercises title extraction, report body boundaries, Rust frame recognition, and the ability to ignore surrounding Fuchsia component-manager noise.

## State, Dependencies, Integration, Risks, And Test Signals

The fixture has no executable state, but it persists a real-world log shape that report matching must continue to support. It integrates with `pkg/report` Starnix testdata and indirectly with crash deduplication and dashboard titles. Main risks are brittle parsing around interleaved WARN/INFO prefixes, path/version changes, Unicode-ish symbol formatting, and EOF lines that should not replace the kernel panic. The test signal is that Starnix reporter tests can recover the intended title and stack from this noisy multi-section log.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/starnix/report/2 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/starnix/report/3 -->
# sources/test-tools/syzkaller/pkg/report/testdata/starnix/report/3

## Purpose

This fixture is another Starnix parser input, representing a panic in `src/starnix/kernel/vfs/symlink_node.rs:28:5` with message `internal error: entered unreachable code: Symlink nodes cannot be opened.` It verifies that Starnix panic reports are classified by the application-level panic rather than by the later process teardown noise.

## Important Content And Control Flow

The log carries `TITLE:` and `REPORT:` regions, Starnix panic text, syz-executor EOF, Rust backtrace frames through `create_file_ops`, `FsNode::open`, `open_file_at`, `sys_openat`, and `sys_creat`, plus crashsvc exception processing and critical-process shutdown messages. The reporter must find the panic marker, preserve the relevant Rust path/function frames, and stop unrelated job death messages from becoming the report title.

## State, Dependencies, Integration, Risks, And Test Signals

The file is immutable test data for Starnix report extraction. It depends on the Starnix reporter regular expressions and symbolization conventions used by `pkg/report`. Risks include parser overmatching on `SYZFATAL`, missing the `REPORT:` copy of the panic, or being confused by BuildID/module lines. Passing tests show that syzkaller can normalize Starnix Rust panics from noisy Fuchsia kernel logs and keep symlink-open crashes distinct from other Starnix panics.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/starnix/report/3 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/title_stat.go -->
# sources/test-tools/syzkaller/pkg/report/title_stat.go

## Purpose

`title_stat.go` maintains a JSON trie of crash-report title sequences. It lets report processing accumulate how often one report title is followed by later titles in the same report set, which is useful for understanding chains of warnings or repeated crash signatures.

## Important APIs, Types, And Functions

`AddTitleStat(file string, reps []*Report) error` extracts report titles, reads the existing stat file, updates counts, and writes JSON through `osutil.WriteJSON`. `ReadStatFile` returns an empty `titleStat` for missing files or decodes JSON otherwise. `titleStat` stores `Count` and nested `Nodes`; `titleStat.add` recursively increments prefix counts; `titleStat.visit` walks leaves and invokes a callback with count and title chain.

## Control Flow, State, Dependencies, And Risks

The update path is read-modify-write with no locking, so concurrent writers could lose increments. Empty report lists are ignored. Counts live only in the JSON file named by the caller. The code depends on `osutil.IsExist`, `ReadJSON`, `WriteJSON`, and Go 1.23-style `maps.Keys` iteration; traversal order is intentionally map-defined unless callers sort. Risks are corrupted JSON, non-atomic multi-process updates, and hidden nondeterminism in `visit` ordering.

## Test Signals

`title_stat_test.go` covers missing files, single-title chains, two-title chains, and branching chains sharing a prefix. Extra useful tests would cover malformed JSON and repeated updates from multiple independent calls.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/title_stat.go -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/title_stat_test.go -->
# sources/test-tools/syzkaller/pkg/report/title_stat_test.go

## Purpose

This test validates the JSON-backed crash-title trie update logic from `title_stat.go`.

## Important APIs, Types, And Flow

`TestAddTitleStat` uses table-driven cases with temporary files. Each case calls `AddTitleStat` zero or more times, then `ReadStatFile`, and compares the resulting nested `titleStat` structure with `testify/assert`. The scenarios cover an empty read, one report title, a two-title chain, and two chains sharing the same first title but diverging at the second.

## State, Dependencies, Risks, And Test Signals

The tests persist state only inside `t.TempDir`. They exercise the real JSON read/write path and the recursive count/node allocation behavior. They do not cover `visit`, malformed existing files, or concurrent modification, so those remain residual risks. The strongest signal is that counts increment at each prefix node, not just at leaves.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/title_stat_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/repro/repro.go -->
# sources/test-tools/syzkaller/pkg/repro/repro.go

## Purpose

`repro.go` is syzkaller's crash reproducer extraction engine. Given a crash log, manager config, reporter, feature set, and VM pool, it finds a syz program that reproduces the crash, minimizes it, optionally converts it into a C reproducer, simplifies options, and validates reliability.

## Important APIs, Types, And Functions

Public types are `Result`, `Stats`, `Environment`, and `ErrEmptyCrashLog`; public entry points are `Run`, `Stats.FullLog`, and `Result.CProgram`. `Result` records the final `prog.Prog`, duration, `csource.Options`, C-repro status, final report, and reliability. `reproContext` holds crash identity, parsed log entries, timeouts, options, observed report titles, and executor abstraction. `execInterface` lets production code use `poolWrapper` while tests inject fake runners.

## Control Flow

`Run` delegates to `runInner`, which parses log entries, extracts the initial crash report, chooses timeout tiers based on crash type, creates starting C options from enabled features, and calls `reproContext.run`. `repro` trims entries after the crash, tries single-program extraction from the crash executor or last program per proc, then whole-log bisection and concatenation. After extraction it minimizes calls/arguments, tries C reproduction, simplifies syz and C options, and runs `calculateReliability` with up to ten validation attempts requiring at least 15 percent reliability.

Minimization uses `prog.Minimize`; multi-program bisection uses `minimize.SliceWithFixed` and preserves the crash-reported executor ID. Test execution funnels through `testProgs`/`testProg`/`testCProg` into `getVerdict`, which retries transient VM errors, filters suppressed reports, rejects non-leak reports for leak reproduction, and avoids low-priority crash diversion once a high-priority title is known.

## State, Dependencies, Integration, And Risks

State is in-memory except for VM-side execution and generated C source formatting. The package depends on `prog`, `csource`, `instance`, `mgrconfig`, `report`, `crash`, `targets`, VM dispatcher, and the bisection minimizer. Integration points include manager crash handling, dashboard artifacts, strace, VM execution, and syz-execprog/C executor paths. Risks are expensive VM loops, flaky crashes passing or failing reliability heuristics, lost original crash identity when unrelated high-priority crashes appear, races around no-output/lost-connection timeouts, and option simplification accidentally masking required setup. `checkOpts` specifically guards long non-repeating repros from false no-output bugs.

## Test Signals

`repro_test.go` covers bisection, option simplification validity, plain repro extraction, transient VM retry, too many errors, concatenation under `prog.MaxCalls`, flaky crash rejection, broken compiler C-repro skip, and avoiding low-priority lost-connection diversion. Benchmarks characterize reliability sampling cost.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/repro/repro.go -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/repro/repro_test.go -->
# sources/test-tools/syzkaller/pkg/repro/repro_test.go

## Purpose

This file tests the reproducer engine using fake executor behavior so the extraction, minimization, reliability, and crash-priority logic can be validated without real VMs.

## Important APIs, Types, And Control Flow

`initTest`, `testExecInterface`, `runTestRepro`, `fakeCrashResult`, and `testExecRunner` build a Linux/amd64 test environment and simulate crashes from serialized programs. `TestBisect` fuzzes `bisectProgs` with random guilty entries. `TestSimplifies` recursively verifies all C option simplification combinations remain valid. The plain repro, VM error, too-many-errors, concatenation, flaky, broken-compiler, and lost-connection tests drive `runInner` end to end.

## State, Dependencies, Risks, And Test Signals

Tests use `testutil.RandSource`, real `prog` target parsing, real reporter construction, and fake `instance.RunResult` values. They validate retry limits, minimum reliability behavior, title filtering, and C-repro skipping. The suite does not execute real generated C or real VM pools; integration with `poolWrapper` is covered elsewhere. Flaky probabilistic tests have thresholds rather than exact outcomes, so random seed quality and short-mode iteration counts matter.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/repro/repro_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/repro/strace.go -->
# sources/test-tools/syzkaller/pkg/repro/strace.go

## Purpose

`strace.go` reruns an established reproducer under `strace` to collect syscall-level output and check whether the traced run hits the same bug.

## Important APIs, Types, And Control Flow

`StraceResult` contains a crash `Report`, captured `Output`, and `Error`. `RunStrace` requires `cfg.StraceBin`, leases a VM from the dispatcher, updates VM status to `running strace`, calls `instance.SetupExecProg` with `StraceBin` and a 2 MiB before-context buffer, then executes either `RunCProg` or `RunSyzProg` according to `Result.CRepro`. `straceFailed` wraps setup/run errors. `IsSameBug` compares titles between strace and repro reports while handling nils.

## State, Dependencies, Integration, Risks, And Test Signals

State is transient VM execution plus captured output. Dependencies are `instance`, `mgrconfig`, `report`, VM dispatcher, and logging. It integrates after successful reproduction and before reporting richer diagnostics. Risks include missing strace binary, strace perturbing timing-sensitive crashes, insufficient output context, setup failures, and title-only equality treating changed reports as different even if semantically related. There is no dedicated unit test in this subset; integration tests need a configured VM and strace binary.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/repro/strace.go -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/rpcserver/last_executing.go -->
# sources/test-tools/syzkaller/pkg/rpcserver/last_executing.go

## Purpose

`last_executing.go` keeps recent executor programs per proc so crash reports can be prefixed with the programs most likely running at crash time.

## Important APIs, Types, And Control Flow

`LastExecuting` stores a ring of `ExecRecord` values for each proc plus a never-dropped list of hanged programs. `MakeLastExecuting` allocates `procs * count` ring slots. `Note` records the program, proc, ID, and monotonic timestamp in the proc's ring position. `Hanged` appends a record with a synthetic proc ID above `prog.MaxPids` so repro extraction includes it. `Collect` concatenates rings and hanged entries, sorts by start time, drops zero records, converts absolute start times into "duration ago", and invalidates internal slices. `PrependExecuting` writes these records into `report.Report.Output` and adjusts report offsets.

## State, Dependencies, Integration, Risks, And Test Signals

The type is not internally synchronized; callers use it from the runner connection goroutine and shut it down before collecting. It depends on `prog.MaxPids`, monotonic time from callers, and `report.Report` offsets. Risks include panics for invalid proc indexes, use-after-`Collect`, losing older non-hanged entries per proc, and incorrect offset adjustment if the prepended buffer length changes. Tests cover empty collection, ring wrap, ordering, duration conversion, and hanged record retention.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/rpcserver/last_executing.go -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/rpcserver/last_executing_test.go -->
# sources/test-tools/syzkaller/pkg/rpcserver/last_executing_test.go

## Purpose

This test file verifies `LastExecuting` ring-buffer semantics and hanged-program retention.

## Important APIs, Types, And Flow

`TestLastExecutingEmpty` confirms an untouched tracker collects no records. `TestLastExecuting` records programs across several procs with a per-proc capacity of three and expects sorted records with older overflow removed and `Time` rewritten as time-before-latest. `TestLastExecutingHanged` verifies hanged programs survive later ring overwrites and receive synthetic proc IDs starting at `prog.MaxPids`.

## State, Dependencies, Risks, And Test Signals

The tests use fixed integer `time.Duration` values and byte-slice program labels, so expectations are deterministic. They do not test `PrependExecuting` offset changes or invalid proc indexes. Passing tests strongly signal that crash context preserves the latest per-proc executions and always includes hanged programs.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/rpcserver/last_executing_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/rpcserver/local.go -->
# sources/test-tools/syzkaller/pkg/rpcserver/local.go

## Purpose

`local.go` runs a syz-executor process locally against the same `rpcserver` machinery used for remote VMs. It is used by runtest and executor integration tests to avoid a full manager/VM stack.

## Important APIs, Types, And Control Flow

`LocalConfig` embeds `Config` and adds executor path, run directory, interrupt handling, gdb mode, output capture, initial max signal/filter, and a `MachineChecked` callback. `RunLocal` sets up a local server, runs server and executor lifetimes together, and cancels the counterpart when either ends. `setupLocal` fills defaults, enables cover edges/filtering, listens on `:0`, and optionally wraps context cancellation around interrupts. `local` implements the `Manager` interface. `RunInstance` registers an instance, starts `executor runner <id> localhost <port>` or `gdb --args`, waits for RPC connection errors or context cancellation, kills the process on connection end, and returns executor/process errors.

## State, Dependencies, Integration, Risks, And Test Signals

State consists of a local server, setup synchronization channel, subprocess, and temp working directory owned by callers. Dependencies include `flatrpc`, `queue`, `osutil.HandleInterrupts`, `signal`, `vminfo`, and `os/exec`. It integrates with `pkg/runtest` and machine-check tests. Risks include process cleanup timing, gdb stdin/stdout behavior, missing executor binary, cancellation races, and returning a synthetic "executor process exited" error for normal exits unless context cancellation explains it. Tests in `runtest` and `rpcserver_test.go` exercise local setup, restart, machine check, and coverage flows.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/rpcserver/local.go -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/rpcserver/mocks/Manager.go -->
# sources/test-tools/syzkaller/pkg/rpcserver/mocks/Manager.go

## Purpose

This generated file provides a testify/mock implementation of `rpcserver.Manager` for unit tests.

## Important APIs, Types, And Control Flow

`NewManager` binds the mock to a testing object and registers cleanup-time expectation assertions. `Manager` embeds `mock.Mock`; `Manager_Expecter` exposes typed expectation builders. Mocked methods are `BugFrames`, `CoverageFilter`, `MachineChecked`, and `MaxSignal`, each calling `_mock.Called(...)`, supporting direct return values or return functions, and panicking if no return value is configured. Per-method call wrapper types provide `Run`, `Return`, and `RunAndReturn` helpers with typed arguments.

## State, Dependencies, Integration, Risks, And Test Signals

State is the testify mock call registry. Dependencies include `flatrpc`, `queue`, `signal`, `vminfo`, `prog`, and `github.com/stretchr/testify/mock`. It integrates with `rpcserver_test.go` to isolate server behavior from manager state. Risks are typical generated mock risks: stale signatures after interface changes, panics on missing expectations, and unsafe type assertions if test return values are wrong. The file itself is not directly tested; compilation and tests using `mocks.NewManager` are the signal.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/rpcserver/mocks/Manager.go -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/rpcserver/rpcserver.go -->
# sources/test-tools/syzkaller/pkg/rpcserver/rpcserver.go

## Purpose

`rpcserver.go` manages FlatRPC connections from syz-executor runners, performs machine checks, distributes fuzzing requests, tracks runner lifecycle, and exposes server operations used by managers and local tests.

## Important APIs, Types, And Functions

`Config`, `RemoteConfig`, `Manager`, `Server`, `Stats`, `NewStats`, `NewNamedStats`, and `New` define the public surface. The private `server` owns the FlatRPC listener, target/timeouts, `vminfo.Checker`, queue distributor, runner map, feature state, coverage canonicalizer/filter, handshake channel, stats, and triaged-corpus flag. Lifecycle methods include `Listen`, `Serve`, `Close`, `Port`, `CreateInstance`, `StopFuzzing`, `ShutdownInstance`, `DistributeSignalDelta`, and `TriagedCorpus`.

## Control Flow

`New` translates manager config into RPC config, feature flags, sandbox flags, PC base, cover-edge/filter policy, and stats. `Serve` runs the listener and the first machine check under an `errgroup`. `handleConn` sends an auth cookie challenge, validates `ConnectRequest`, checks revisions unless VM-less, finds the pre-created runner, and hands off to `handleRunnerConn`. That method builds handshake options, obtains bug frames and machine-check files, runs `Runner.Handshake`, optionally sends corpus-triaged, and enters `connectionLoop`. `runCheck` uses `vminfo.Checker` output to compute enabled calls/features, prints diagnostics, asks the manager for the post-check queue source, swaps the dynamic source, and marks setup complete.

## State, Dependencies, Integration, And Risks

Persistent runtime state includes runner map under `mu`, atomic check/triage flags, coverage filter/modules, dynamic queue source, and stat counters. Dependencies include `flatrpc`, `queue`, `cover`, `backend`, `vminfo`, `mgrconfig`, `stat`, `signal`, `prog`, and VM dispatcher types. Integration points are manager startup, fuzzer corpus distribution, executor runner protocol, machine-check feature detection, coverage canonicalization, and crash report context. Risks include fatal revision mismatches, machine-check failure loops, unauthenticated-but-cookie-gated TCP clients, async runner sends after disconnect, races avoided by mutex/atomics, and signal filtering being disabled for non-Linux targets.

## Test Signals

`rpcserver_test.go` validates config feature derivation, revision checking, unknown VM connection rejection, and machine-check crash/restart handling through `LocalConfig`. Broader coverage comes from `runtest` local executor tests.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/rpcserver/rpcserver.go -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/rpcserver/rpcserver_test.go -->
# sources/test-tools/syzkaller/pkg/rpcserver/rpcserver_test.go

## Purpose

This file tests key `rpcserver` construction, handshake validation, and local machine-check restart behavior.

## Important APIs, Types, And Control Flow

`getTestDefaultCfg` builds a minimal test manager config. `TestNew` checks sandbox errors and feature flag derivation for remote coverage and memory dump settings. `TestCheckRevisions` validates architecture, git revision, and syscall revision mismatch errors. `TestHandleConn` uses `net.Pipe` and `flatrpc.Conn` to perform the cookie handshake and assert an unknown VM connection is rejected. `TestMachineCheckCrash` builds a test executor, starts a local server, kills an instance during machine check, restarts it, and waits for successful completion.

## State, Dependencies, Risks, And Test Signals

Tests depend on generated `mocks.Manager`, `prog` test targets, `csource.BuildExecutor`, `LocalConfig`, and `errgroup`. `TestMachineCheckCrash` is integration-heavy and can skip on broken compilers. The tests do not fully emulate normal runner execution or signal distribution, but they guard several high-risk setup paths: invalid config, version skew, unexpected VM IDs, and executor death during machine check.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/rpcserver/rpcserver_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/rpcserver/runner.go -->
# sources/test-tools/syzkaller/pkg/rpcserver/runner.go

## Purpose

`runner.go` represents one connected executor runner. It performs the executor handshake, streams execution requests, receives execution/status messages, updates queues and stats, canonicalizes coverage, tracks last executing programs, and handles shutdown.

## Important APIs, Types, And Functions

`Runner` holds identity, queue distributor, proc count, coverage/filter/debug flags, sys target, stats, connection, request/executing/hanged maps, `LastExecuting`, VM status callbacks, machine info, and result channel. `handshakeConfig` and `handshakeResult` carry setup options, files, features, coverage filter, and canonicalizer. Core methods are `Handshake`, `ConnectionLoop`, `sendRequest`, `handleExecutingMessage`, `handleExecResult`, `convertCallInfo`, `SendSignalUpdate`, `SendCorpusTriaged`, `Stop`, `Shutdown`, `MachineInfo`, `QueryStatus`, and `Alive`.

## Control Flow

`Handshake` sends `ConnectReply`, receives `InfoRequest`, invokes the server callback, sends `InfoReply`, and stores connection/machine/canonicalizer state. `ConnectionLoop` marks the VM executing, services pending status requests, fills the executor queue up to `2 * procs`, receives executor messages, and dispatches executing, exec-result, or state-result handling. `sendRequest` serializes syz programs, binaries, or glob requests into `flatrpc.ExecRequest`, sets return flags, avoid masks, and debug env flags, and records the request by ID. `handleExecResult` normalizes call counts, converts coverage/signal/comparisons, merges extra coverage, adds fallback signal if coverage is disabled, reports success/failure/hang, and completes the queue request.

## State, Dependencies, Integration, And Risks

Mutable request state is mostly touched by the connection goroutine, while `mu` protects connection, stop, and machine info. Dependencies include `flatrpc`, `queue`, `cover`, `stat`, `osutil`, `report`, `prog`, `targets`, and dispatcher status hooks. Integration points are executor FlatBuffers protocol, queue scheduling, VM crash context, coverage canonicalization/filtering, and manager signal distribution. Risks include blocked sends to a dead executor, malformed proc/request IDs, program serialization failures, stale hanged request results, bad coverage poisoning corpus signal, and shutdown needing to finish outstanding requests exactly once.

## Test Signals

Runner behavior is exercised indirectly by `rpcserver_test.go` and the `runtest` executor/local RPC tests, especially coverage/comparison canonicalization, status handling, restarts, and queue completion paths.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/rpcserver/runner.go -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/rpctype/rpc.go -->
# sources/test-tools/syzkaller/pkg/rpctype/rpc.go

## Purpose

`rpc.go` is the older compressed `net/rpc` transport wrapper used by syzkaller components such as syz-manager and syz-hub.

## Important APIs, Types, And Control Flow

`RPCServer` wraps a TCP listener and `rpc.Server`; `NewRPCServer` listens and registers a named receiver; `Serve` accepts forever, enables TCP keepalive, wraps the connection with flate compression, and serves it in a goroutine. `RPCClient` wraps a TCP connection and `rpc.Client`; `NewRPCClient` dials with a three-minute timeout and compression; `Call` sets a ten-minute deadline around each RPC; `Close` closes the client. `flateConn` adapts `io.ReadWriteCloser` through `flate.Reader` and level-9 `flate.Writer`, flushing on every write and closing all layers.

## State, Dependencies, Integration, Risks, And Test Signals

State is the listener, TCP connection, RPC codec, and compression streams. Dependencies are Go `net/rpc`, `compress/flate`, TCP keepalive, and `pkg/log`. Risks include `Serve` never exiting on listener close because accept errors are only logged, unchecked TCP type assertions in `setupKeepAlive`, per-write flush overhead, and deadlines being unavailable on some platforms by comment. No tests are in this subset; integration with hub RPC call paths is the expected signal.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/rpctype/rpc.go -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/rpctype/rpctype.go -->
# sources/test-tools/syzkaller/pkg/rpctype/rpctype.go

## Purpose

`rpctype.go` defines serializable message shapes exchanged over the legacy manager-to-hub `net/rpc` protocol.

## Important APIs, Types, And State

`HubConnectArgs` carries authentication, manager identity, HTTP URL, domain, fresh-corpus flag, supported syscall names, and current corpus. `HubSyncArgs` carries auth identity, repro request flag, corpus additions/removals, and new repros. `HubSyncRes` returns inputs, legacy program list, repros, and a `More` count prompting another sync. `HubInput` adds source domain metadata to a program.

## Dependencies, Integration, Risks, And Test Signals

These are plain exported data structs with no methods or persistence. They integrate with syz-hub RPC server/client code through Go's gob-compatible `net/rpc` encoding. Risks are backward compatibility, especially `HubSyncRes.Progs` retained for legacy managers, and auth material being present in memory/loggable structs. Tests are protocol-level rather than in this file; compile-time field use and hub sync tests are the main signals.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/rpctype/rpctype.go -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/runtest/executor_test.go -->
# sources/test-tools/syzkaller/pkg/runtest/executor_test.go

## Purpose

This file runs executor-specific integration tests from Go, including built-in executor unit tests, zlib comparison behavior, and extension-hook behavior.

## Important APIs, Types, And Control Flow

`qemuBinary` maps Go arch names to qemu-user binaries for cross-arch execution. `handleCrossArchError` fails on CI or executor assertions but skips local cross-arch environment problems. `TestExecutor` builds each host-OS executor target and runs its `test` subcommand natively or under qemu. `TestZlib` builds the test executor, starts a local RPC server, sends random compressed/uncompressed image comparisons through `syz_compare_zlib`, and expects zero errno. `TestExecutorCommonExt` builds with `-DSYZ_TEST_COMMON_EXT_EXAMPLE=1` and checks that the common extension hook initialized memory visible to `syz_compare`.

## State, Dependencies, Risks, And Test Signals

Tests create temp dirs, executor binaries, local RPC servers, queue requests, random mount images, and optional qemu subprocesses. Dependencies include `csource`, `queue`, `image`, `osutil`, `testutil`, targets, and `startRPCServer` from `run_test.go`. Risks include qemu availability, cross-compiler availability, CI/local behavior differences, and subprocess cleanup. Passing tests prove executor built-ins, zlib helpers, and common extension setup work through the same RPC execution path used by fuzzing.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/runtest/executor_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/runtest/run.go -->
# sources/test-tools/syzkaller/pkg/runtest/run.go

## Purpose

`run.go` is the syzkaller program runtime-test driver. It generates syz-executor and C-source test requests across sandboxes, threading, repetition, and coverage modes, submits them to a queue executor, and checks observed call results against expectations encoded in test program comments.

## Important APIs, Types, And Functions

`Context` is the main driver configuration: test directory, target, supported features, enabled calls by sandbox, logging, retry count, verbosity, debug flag, and filename filter. `Init`, `Run`, and `Next` form the public workflow. Private helpers include `generatePrograms`, `progFileList`, `generateFile`, `parseProg`, `produceTest`, `createTest`, `submit`, `createSyzTest`, `createCTest`, `checkResult`, `checkCallResult`, `checkCallStatus`, `checkCallCoverage`, and `parseBinOutput`.

## Control Flow

`Run` calls `generatePrograms`, waits for created requests, reports per-test status, removes generated binaries, and fails if any test failed. `generateFile` parses a seed/test file, expands it over enabled sandboxes, threaded/unthreaded modes, repeat counts, and coverage modes, creates syz or C requests, and skips/breaks unsupported combinations. C requests build source asynchronously behind a `GOMAXPROCS` semaphore, then become binary queue requests. Completion goes through `onDone`, which tolerates flaky timing by rerunning until successes outnumber failures or retry budget is exhausted.

## State, Dependencies, Integration, And Risks

State includes generated request list, dynamic orderer executors, build semaphore, temporary binaries, per-request pass/fail counts, expected `flatrpc.ProgInfo`, and C repeat counts. Dependencies are `csource`, `flatrpc`, `queue`, `manager.ParseSeedWithRequirements`, `prog`, and `targets`. Integration points include `tools/syz-runtest`, `pkg/runtest` tests, executor RPC, csource generation, and sys/*/test files. Risks include combinatorial test expansion, flaky timing heuristics, platform-specific errno/comment mapping, missing coverage for pseudo syscalls, C output parser fragility, and broken non-fork repeat modes.

## Test Signals

`run_test.go` validates parsing, feature expectations, coverage/signal/comparison handling, and local executor execution. `executor_test.go` covers executor built-ins and extension behavior.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/runtest/run.go -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/runtest/run_test.go -->
# sources/test-tools/syzkaller/pkg/runtest/run_test.go

## Purpose

This file provides end-to-end tests for `pkg/runtest`, local RPC execution, coverage/signal/comparison extraction, and parsing of sys test programs.

## Important APIs, Types, And Control Flow

Flags `-filter`, `-debug`, and `-gdb` select test subsets and executor diagnostics. `TestUnit` builds a test-OS executor and runs `Context.Run` over sys test files. `TestCover` defines `CoverTest` cases for 32/64-bit coverage, deduplication, signal hashing, invalid PCs, comparisons, max-signal filtering, cover filters, and extra coverage. Helpers `makeCover64`, `makeCover32`, and `makeComps` construct executor-injected binary payloads. `startRPCServer` creates a temp local `rpcserver.LocalConfig`, launches `RunLocal`, and returns a context used by queue requests. `TestParsing` parses all sys test files by OS/arch and checks C-source generation where possible.

## State, Dependencies, Risks, And Test Signals

The tests build executors, create local temp dirs, run RPC server goroutines, submit queue requests, and clean up executor work dirs with retries. Dependencies include `rpcserver`, `vminfo`, `csource`, `queue`, `flatrpc`, `prog`, `targets`, and `testutil`. Risks include compiler/toolchain availability, long runtime, race-mode narrowing, coverage order assumptions, and cleanup of executor subprocesses. Passing tests are a strong integration signal for executor protocol, coverage canonicalization, feature detection, and test-program parsing.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/runtest/run_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/serializer/serializer.go -->
# sources/test-tools/syzkaller/pkg/serializer/serializer.go

## Purpose

`serializer.go` writes a compact Go-syntax representation of values for syzkaller diagnostics and generated data, improving on `fmt %#v` for pointer-heavy structs and default-valued fields.

## Important APIs, Types, And Control Flow

`Write(io.Writer, any)` and `WriteString(any)` are public entry points. The private `writer` recursively handles pointers, interfaces, slices, structs, booleans, signed/unsigned integers, strings, and nil funcs. Structs omit default or unsettable fields and then switch to named-field syntax; slices of pointer/interface/struct elements are rendered multiline. Interfaces wrapping named primitive types are emitted as `Type(value)` so deserialization preserves the user type. `isDefaultValue` recursively recognizes zero values.

## State, Dependencies, Integration, Risks, And Test Signals

The serializer is stateless beyond the destination writer and reflection stack. Dependencies are `reflect`, `strings`, `fmt`, and `io`. It does not support maps, channels, non-nil functions, or pointers to non-structs, and it panics for unsupported cases. `reflect.Value.CanSet` is used to skip unexported/default fields, which makes output sensitive to addressability. `serializer_test.go` covers nested structs, pointers, slices, escaped strings, named primitive interface values, nils, and nil funcs.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/serializer/serializer.go -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/serializer/serializer_test.go -->
# sources/test-tools/syzkaller/pkg/serializer/serializer_test.go

## Purpose

This test checks the exact textual format emitted by `serializer.Write`.

## Important APIs, Types, And Flow

`TestSerializer` builds a nested `*X` value containing embedded struct `Y`, pointer fields, a slice of structs, booleans, escaped strings, an enum-like named int, a heterogeneous `[]any`, typed nils, named primitive aliases, and a nil function. It writes into a `bytes.Buffer` and compares to a fixed expected string.

## State, Dependencies, Risks, And Test Signals

The test is deterministic and uses `testify/require`. It is intentionally golden-output sensitive, catching formatting changes in commas, newlines, address markers, type names, and interface wrapping. It does not cover panic cases for unsupported kinds or default-field omission in named-field mode beyond the selected fixture.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/serializer/serializer_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/signal/signal.go -->
# sources/test-tools/syzkaller/pkg/signal/signal.go

## Purpose

`signal.go` defines syzkaller's feedback signal abstraction: a set of coverage-like elements with priorities used for corpus minimization and manager/fuzzer signal exchange.

## Important APIs, Types, And Control Flow

`Signal` is `map[elemType]prioType` with methods `Len`, `Empty`, `Copy`, `DiffRaw`, `IntersectsWith`, `Intersection`, `Merge`, and `ToRaw`; `FromRaw` builds a signal from raw `uint64` elements at one priority. `Context` pairs a signal with arbitrary caller context, and `Minimize` returns contexts that own the highest priority for at least one signal element. Priority comparisons are central: an existing element covers a new one only if its priority is greater or equal.

## State, Dependencies, Integration, Risks, And Test Signals

State is caller-owned map data; `Merge` mutates the receiver map and allocates on nil. `Copy` uses `maps.Copy`. Integration points include fuzzer corpus minimization, RPC server max-signal propagation, and feedback deduplication. Risks include map iteration nondeterminism in `ToRaw` and `Minimize`, nil-map behavior callers must understand, and priority semantics being easy to invert. `signal_test.go` specifically covers `IntersectsWith`, including lower-priority non-intersection.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/signal/signal.go -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/signal/signal_test.go -->
# sources/test-tools/syzkaller/pkg/signal/signal_test.go

## Purpose

This test validates priority-aware signal intersection.

## Important APIs, Types, And Flow

`TestIntersectsWith` constructs a base signal from raw elements `0..4` at priority 1. It asserts intersection with an overlapping signal at the same priority, no intersection with disjoint elements, and no intersection when the other signal overlaps but has lower priority.

## State, Dependencies, Risks, And Test Signals

The test uses `testify/assert` and deterministic raw input. It does not cover `Merge`, `DiffRaw`, `Intersection`, `Minimize`, or raw ordering. Its signal is focused but important: priority is part of intersection, not only element membership.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/signal/signal_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/stat/avg.go -->
# sources/test-tools/syzkaller/pkg/stat/avg.go

## Purpose

`avg.go` provides a thread-safe incremental average helper currently constrained to `time.Duration`-like values.

## Important APIs, Types, And Control Flow

`AverageParameter` is a type constraint over `time.Duration`. `AverageValue[T]` stores a mutex, sample count, and current average. `Save` increments the sample count and applies the incremental formula `avg += (val - avg) / total`; `Value` returns the current average under lock.

## State, Dependencies, Integration, Risks, And Test Signals

State is in-memory and protected by `sync.Mutex`. It depends only on `time` and `sync`. The integer-duration formula is stable and O(1), but truncates fractional parts and `total` could overflow after extreme runtimes. There are no tests in this subset; callers should test first sample behavior, multiple samples, and concurrent `Save`/`Value`.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/stat/avg.go -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/stat/sample/pvalue.go -->
# sources/test-tools/syzkaller/pkg/stat/sample/pvalue.go

## Purpose

`pvalue.go` exposes a Mann-Whitney U test for two `Sample` values by reusing benchmark-statistics code.

## Important APIs, Types, And Control Flow

`UTest(old, new *Sample) (float64, error)` wraps each sample's `Xs` slice in `benchstat.Metrics{RValues: ...}` and calls `benchstat.UTest`. It returns the p-value and any error from benchstat.

## State, Dependencies, Integration, Risks, And Test Signals

The function is stateless and does not sort or copy sample data. It depends on `golang.org/x/perf/benchstat`, with a comment noting the internal stats package is inaccessible. Integration is statistical comparison of experiment/benchmark samples. Risks are upstream API drift, sample-size validation errors, and callers assuming a direction/effect size that p-value alone does not provide. There are no direct tests here; `sample_test.go` covers only percentile/outlier helpers.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/stat/sample/pvalue.go -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/stat/sample/sample.go -->
# sources/test-tools/syzkaller/pkg/stat/sample/sample.go

## Purpose

`sample.go` provides basic statistical operations over a collection of float64 measurements.

## Important APIs, Types, And Control Flow

`Sample` holds `Xs []float64` and a `Sorted` flag. `Percentile` sorts in place if needed and uses the R8 percentile estimator copied from `x/perf/internal/stats`. `Median` calls `Percentile(0.5)`. `RemoveOutliers` uses Tukey fences based on Q1 and Q3, returning a copied sample unchanged for fewer than four points. `Copy` clones the slice and flag, and `Sort` sorts in place once.

## State, Dependencies, Integration, Risks, And Test Signals

Operations mutate `Sample.Xs` order and `Sorted`, except `Copy` and returned outlier samples. Dependencies are `math` and `slices`. Risks include panics on empty samples, in-place sorting surprises, preserving `Sorted` in the outlier result even though filtered order follows sorted input, and floating-point tolerance. `sample_test.go` covers median ranges and sanity outlier removal.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/stat/sample/sample.go -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/stat/sample/sample_test.go -->
# sources/test-tools/syzkaller/pkg/stat/sample/sample_test.go

## Purpose

This file tests sample median and outlier-removal behavior.

## Important APIs, Types, And Flow

`TestMedian` checks odd and even input sets using min/max tolerance rather than exact floating equality. `TestRemoveOutliers` checks Tukey-fence behavior for a low outlier, a high outlier, and a spread with no outliers, then sorts the result and compares slices.

## State, Dependencies, Risks, And Test Signals

The tests use deterministic `Sample` values and `reflect.DeepEqual`. They do not cover empty input, percentile endpoints, copy behavior, sorted-flag preservation, or U-test p-values. Passing tests indicate the chosen R8 percentile and Tukey-fence implementations behave sanely on representative small samples.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/stat/sample/sample_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/stat/set.go -->
# sources/test-tools/syzkaller/pkg/stat/set.go

## Purpose

`set.go` implements syzkaller's in-process metric registry, values, collection UI rows, graph history, rate formatting, distribution histories, and optional Prometheus gauge export.

## Important APIs, Types, And Functions

Global helpers `New`, `Collect`, and `RenderGraphs` delegate to a global ticking registry. `set.New` creates `Val` metrics with options: `Level`, `Link`, `Prometheus`, `Rate`, `Distribution`, `Graph`, `StackedGraph`, `NoGraph`, external `func() int`, and custom formatter. `Val.Add` and `Val.Val` update/read counters, external values, or histogram means. `Collect` returns sorted UI rows; `RenderGraphs` returns `UIGraph`/`UIPoint` history. `LenOf` builds external length metrics, and `FormatMB` formats byte counters.

## Control Flow

`newSet` optionally starts a one-second ticker. Each `tick` creates graph lines lazily, records max counter values, rate deltas, or per-period histograms, and advances history positions after `historyScale` ticks. When full, `compress` halves history resolution and doubles the scale, preserving maxes for counters, averages for rates, and one available histogram for distributions. `RenderGraphs` orders lines by creation order and expands distribution lines into 10/50/90 percentiles.

## State, Dependencies, Integration, And Risks

State is protected by `set.mu`, while metric counters use atomics and histogram samples use `histMu`. Dependencies include Prometheus client, `gohistogram`, `sync/atomic`, reflection, and sorting helpers. Integration points are manager/fuzzer UI, heartbeat logs, Prometheus scraping, and RPC server stats. Risks include duplicate metric names overwriting registry entries, ignored Prometheus registration errors, unsigned atomic underflow when `Add` receives negatives, graph stacked flag being graph-wide and last-writer sensitive, and long-running compression losing detail. Tests stress concurrency and history behavior.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/stat/set.go -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/stat/set_test.go -->
# sources/test-tools/syzkaller/pkg/stat/set_test.go

## Purpose

This test suite validates metric creation, collection formatting, graph history, compression, distributions, rates, and concurrent access.

## Important APIs, Types, And Flow

`TestSet` covers counters, external metrics, custom formatters, distribution means, graph/no-graph options, panic paths, and UI sorting by level/name. `TestSetRateFormat` checks second/minute/hour formatting thresholds. `TestSetHistoryCounter`, `TestSetHistoryRate`, and `TestSetHistoryDistribution` manually tick a small history registry to verify compression semantics. `TestSetStress` starts concurrent goroutines that create metrics, add values, read values, collect UI, render graphs, and tick for one second.

## State, Dependencies, Risks, And Test Signals

The tests use `newSet(4, false)` to avoid the global ticker and make history deterministic. They intentionally call negative `Add` in counter history tests, which relies on conversion behavior when read back as `int`. Stress testing is probabilistic and mainly race-detector oriented. Missing coverage includes Prometheus registration errors and duplicate-name behavior beyond unknown-option panic.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/stat/set_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/stat/syzbotstats/bug.go -->
# sources/test-tools/syzkaller/pkg/stat/syzbotstats/bug.go

## Purpose

`bug.go` defines the compact summary model for syzbot bug statistics.

## Important APIs, Types, And State

`BugStatSummary` records title, syzbot IDs, first/released/repro/cause-bisect/resolved times, status, subsystems, strace availability, hit rate, fix hashes, and managers where the bug happened. `BugStatus` is a string enum with values `fixed`, `invalidated`, `auto-invalidated`, `dup`, and `pending`.

## Dependencies, Integration, Risks, And Test Signals

The only dependency is `time.Time`. The struct is designed for serialization/reporting by syzbot statistics code outside this file. Risks are semantic drift in status strings, zero `time.Time` values representing absent milestones, and consumers needing to treat `IDs`, `FixHashes`, and `HappenedOn` as sets despite slice representation. There are no direct tests here; schema compatibility and downstream stats rendering are the signals.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/stat/syzbotstats/bug.go -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/subsystem/entities.go -->
# sources/test-tools/syzkaller/pkg/subsystem/entities.go

## Purpose

`entities.go` defines subsystem metadata used for ownership, mailing-list routing, path matching, and debugging.

## Important APIs, Types, And Control Flow

`Subsystem` stores name, path rules, syscall names, mailing lists, maintainers, parent subsystems, and flags controlling reminders and indirect CC. `ReachableParents` recursively walks parent links, panicking on a direct/recursive return to the starting subsystem. `Emails` returns this subsystem's lists and maintainers plus parent lists unless `NoIndirectCc` is set. `FilterList` applies a predicate to a subsystem list, mutates each kept subsystem's `Parents` to only kept parents, and returns kept items. `PathRule.IsEmpty` checks include/exclude regex strings. `DebugInfo` stores parent-child comments and file lists.

## State, Dependencies, Integration, Risks, And Test Signals

The file has no external dependencies. State is caller-owned graph data, and `FilterList` mutates it in place. Integration points include subsystem matching, report CC generation, and syzbot dashboard/reporting logic. Risks include cycles not involving the starting node causing unbounded recursion, map iteration nondeterminism in parent email ordering, duplicate emails, and surprising parent mutation during filtering. No direct tests are in this subset; callers should test cycle handling, filtering side effects, and email ordering/dedup expectations.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/subsystem/entities.go -->
