# subset-b-009454 Research

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/flatrpc/flatrpc.h -->
# sources/test-tools/syzkaller/pkg/flatrpc/flatrpc.h

## Purpose
This is an automatically generated C++ FlatBuffers header for the `rpc` protocol used between syzkaller host-side code and executor-side code. It defines the serialized schema for connection handshakes, feature negotiation, execution requests and results, corpus/state sideband messages, and snapshot-mode shared-memory coordination. It is intentionally generated and should be changed by editing the FlatBuffers schema and regenerating rather than by hand.

## Important APIs, Types, And Functions
The header requires FlatBuffers 23.5.26 by static assertion and wraps all generated types in namespace `rpc`. It declares constants in `Const`, including snapshot doorbell size, maximum input/output sizes, and snapshot shared-memory size. Feature negotiation uses the `Feature` bitmask enum, covering coverage, comparisons, sandbox modes, fault/leak detection, network/device emulation, KCSAN, swap, and memory dump capabilities.

Host-to-executor traffic is modeled by `HostMessageRaw` carrying a `HostMessagesRawUnion`. The union can hold `ExecRequestRaw`, `SignalUpdateRaw`, `CorpusTriagedRaw`, or `StateRequestRaw`, with `As*` accessors, `Set`, `Reset`, `Pack`, and `UnPack`. Executor-to-host traffic is symmetric via `ExecutorMessageRaw` and `ExecutorMessagesRawUnion`, carrying `ExecResultRaw`, `ExecutingMessageRaw`, or `StateResultRaw`.

Execution-specific enums include `RequestType` (`Program`, `Binary`, `Glob`), `RequestFlag` (`ReturnOutput`, `ReturnError`), `ExecEnv` for executor environment/sandbox/device setup, `ExecFlag` for collection behavior (`CollectSignal`, `CollectCover`, `DedupCover`, `CollectComps`, `Threaded`), and `CallFlag` for per-call execution status, fault injection, and coverage overflow. `ExecOptsRaw` is a manually aligned 24-byte struct containing env flags, exec flags, and sandbox argument. `ComparisonRaw` is a 32-byte struct with comparison PC, operands, and constness.

Key table object APIs include `ConnectHelloRawT`, `ConnectRequestRawT`, `ConnectReplyRawT`, `InfoRequestRawT`, `InfoReplyRawT`, `FileInfoRawT`, `GlobInfoRawT`, `FeatureInfoRawT`, `ExecRequestRawT`, `ExecutingMessageRawT`, `CallInfoRawT`, `ProgInfoRawT`, `ExecResultRawT`, `StateResultRawT`, `SnapshotHeaderT`, `SnapshotHandshakeT`, and `SnapshotRequestT`. For each table the generated code provides table accessors, `Verify`, object API `UnPack`/`UnPackTo`, `Pack`, a builder, `Create*Raw`, and often `Create*RawDirect`.

## Control Flow
There is no business logic control flow beyond generated serialization helpers. Builders add fields to a `flatbuffers::FlatBufferBuilder`, finish tables, and direct builders allocate strings/vectors. `Verify*` methods walk table fields and vectors to validate serialized buffers. Union verification first checks matching value/type vectors and then dispatches by enum to the table verifier for the concrete message. Union pack/unpack dispatches by the stored enum and reinterpret-casts the stored object to the expected native/table type.

## State And Persistence Behavior
The persistent state is the wire format itself: field numbers, enum numeric values, struct layout, vector ordering, and table offsets are ABI. `HostMessagesRawUnion` and `ExecutorMessagesRawUnion` own heap-allocated native table objects and delete them in `Reset`/destructors. Snapshot coordination fields are explicitly modeled through `SnapshotHeader` state, output offset, and output size; companion Go helpers perform atomic state updates for the Go object API.

## Dependencies And Integration Points
The header depends on FlatBuffers and is consumed by executor C++ code and Go bindings generated from the same schema. It integrates with `pkg/flatrpc/helpers.go`, which aliases generated Go names and adds cloning/sandbox/snapshot helpers, and with `pkg/fuzzer/queue` and `pkg/fuzzer`, which populate `ExecOpts`, `ExecRequest`, and consume `ProgInfo`, `CallInfo`, and result flags.

## Risks
Because this is generated protocol code, manual edits can desynchronize C++ and Go bindings. Enum numeric values and table field positions are wire-compatible contracts. The generated union code relies on enum/type correctness and raw pointer reinterpret casts; stale enum values or mismatched value/type vectors can produce invalid decoding. The FlatBuffers version assertion prevents a known class of compatibility drift, but schema changes still require regenerating all language bindings and checking executor/manager compatibility.

## Test Signals
This header has no direct tests in this item. It is indirectly exercised by fuzzer tests that create `flatrpc.ExecOpts`, `ProgInfo`, `CallInfo`, and queue requests, by executor integration in `TestFuzz`, and by helper tests in adjacent packages. Queue request validation also checks protocol constraints such as mutually exclusive comparison collection and signal/coverage collection.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/flatrpc/flatrpc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/flatrpc/helpers.go -->
# sources/test-tools/syzkaller/pkg/flatrpc/helpers.go

## Purpose
This file adds Go-side conveniences around generated FlatBuffers object API types. It hides non-idiomatic `RawT` generated names behind stable aliases, provides deep cloning for execution results, translates sandbox names to execution environment flags, and exposes atomic snapshot header state accessors.

## Important APIs, Types, And Functions
`AllFeatures` is a bitmask with every `Feature` bit set. Type aliases such as `ConnectRequest`, `ExecRequest`, `ExecOpts`, `ProgInfo`, and `CallInfo` map generated `*RawT` names to idiomatic package names. `init` verifies that `prog.MaxPids` fits in the `ExecRequest.Avoid` bitset. `(*ProgInfo).Clone` deep-copies `Extra` and per-call `CallInfo` values. `(*CallInfo).clone` clones signal, cover, and comparison slices. `EmptyProgInfo` creates a placeholder result with `ENOSYS` for each call. `SandboxToFlags` maps textual sandbox names to `ExecEnv` bits. `SnapshotHeaderT.UpdateState` and `LoadState` use atomic `uint64` operations through `unsafe.Pointer`.

## Control Flow
Clone logic handles nil receivers, shallow-copies the struct, and then replaces mutable nested slices/pointers with cloned copies. `EmptyProgInfo` appends one failed `CallInfo` per call. `SandboxToFlags` is a simple switch returning either a sandbox enum or a descriptive error.

## State And Persistence Behavior
Cloning is important for queue result deduplication and broadcasting, where one result can be delivered to multiple waiters without sharing mutable slices. Snapshot state is shared-memory-oriented state; atomic store/load prevents torn reads while other fields remain normal generated object fields.

## Dependencies And Integration Points
The file depends on generated `flatrpc` symbols, `prog.MaxPids`, `slices`, `syscall`, and low-level `sync/atomic`/`unsafe`. It is used by fuzzer execution, queue result cloning, manager default exec option setup, and snapshot executor coordination.

## Risks
The `unsafe` atomic conversion assumes `SnapshotState` is represented compatibly with `uint64`. The `init` check guards only PID bitset width, not other wire-size constraints. `AllFeatures = ^Feature(0)` can include unknown future bits; callers must avoid using it as a negotiated capability set without filtering.

## Test Signals
No direct tests are in this item. Indirect signals come from queue clone/dedup behavior, fuzzer execution tests, and any snapshot code that uses atomic state helpers.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/flatrpc/helpers.go -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/fuzzer/cover.go -->
# sources/test-tools/syzkaller/pkg/fuzzer/cover.go

## Purpose
`Cover` tracks the maximum fuzzing signal known to a fuzzer and exposes deltas for synchronization. It distinguishes all observed max signal, including flaky observations, from newly observed signal that has not yet been grabbed.

## Important APIs, Types, And Functions
`Cover` holds a mutex, `maxSignal`, and `newSignal`. `newCover` registers a `stat` metric named `max signal`. `addRawMaxSignal` diffs raw signal against the current max with a priority, merges non-empty diffs into both max and new-signal state, and returns the diff. `CopyMaxSignal` returns a thread-safe copy. `GrabSignalDelta` returns accumulated new signal and clears the delta.

## Control Flow
All mutations take the write lock. `addRawMaxSignal` exits early if no new signal exists; otherwise it updates both long-lived and delta state. Readers take the read lock for copy and write lock for consuming deltas.

## State And Persistence Behavior
State is in-memory only. `maxSignal` is cumulative for the process lifetime, while `newSignal` is transient and is reset after `GrabSignalDelta`. The code intentionally treats flaky signal as max signal to suppress repeated triage on already observed bits.

## Dependencies And Integration Points
It depends on `pkg/signal` and `pkg/stat`. `Fuzzer.triageProgCall` and `triageJob.deflake` feed raw executor signals into it. Signal deltas are candidates for propagation to other components.

## Risks
Signal priority is supplied by callers, so wrong priority calculation changes corpus ranking. `GrabSignalDelta` returns the internal map value then nils the field; callers should treat it as owned output and not expect the fuzzer to retain that specific map.

## Test Signals
No direct test file targets `Cover`. It is exercised through fuzzer tests and deflake behavior that add and compare signal.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/fuzzer/cover.go -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/fuzzer/fuzzer.go -->
# sources/test-tools/syzkaller/pkg/fuzzer/fuzzer.go

## Purpose
This file defines the central `Fuzzer` object: configuration, execution queues, coverage tracking, candidate intake, request generation, execution result processing, choice-table maintenance, job tracking, and default executor options.

## Important APIs, Types, And Functions
`Fuzzer` embeds `Stats` and stores `Config`, `Cover`, context, RNG, target, hints limiter, running jobs, choice table state, and `execQueues`. `Config` controls corpus, logging, snapshot/coverage/comparison/collide/fault-injection modes, enabled calls, mutation exclusions, raw cover fetching, patch testing, and KFuzzTest mode. `NewFuzzer` initializes defaults, stats, cover, queue source ordering, choice table updater, and optional debug logging.

`execQueues` contains candidate, triage, and smash queues. `newExecQueues` orders sources as candidate triage, candidate execution, regular triage, alternated smash, then generated fuzz. `Next` returns the next request and panics on nil. `AddCandidates` enqueues corpus or hub candidates with signal collection and candidate flags. `execute`, `executeWithFlags`, `prepare`, and `enqueue` attach result callbacks and submit to a queue executor.

`processResult` handles completed requests. It triages newly discovered signal unless the program is already in triage or hanged, creates `triageJob`s, records execution time and overflow stats, retries corpus candidates for flaky coverage or risky crashes, and decrements candidate stats. `triageProgCall` computes signal priority, updates `Cover`, filters by `NewInputFilter`, and records `triageCall` state. `DefaultExecOpts` translates manager configuration and feature bits into `flatrpc.ExecOpts`.

## Control Flow
Normal fuzzing flows from `Next` through ordered queue sources. If queues are empty, `genFuzz` mutates a corpus program or generates a new program, optionally transforms it for collide mode, and attaches processing callbacks. On completion, `processResult` may start asynchronous triage jobs before unblocking waiters. Choice table refresh is signaled over a lossy channel when corpus growth crosses thresholds, and a goroutine rebuilds it.

## State And Persistence Behavior
Long-lived process state includes coverage max signal, corpus-driven choice table, stats, and running job registry. Persistent corpus state is delegated to `Config.Corpus.Save` in job code. Candidate retry state is stored in queue request flags and `attempt` recursion. Choice table update uses a mutex and only replaces the table when built from at least as many programs as the previous one.

## Dependencies And Integration Points
This code ties together `pkg/corpus`, `pkg/flatrpc`, `pkg/fuzzer/queue`, `pkg/signal`, `pkg/stat`, `prog`, `csource`, and `mgrconfig`. Queue requests use `flatrpc.ExecOpts`; results use `ProgInfo` and per-call `CallInfo`. The fuzzer is consumed by RPC/local executor loops that call `Next` and later `Done`.

## Risks
The nil panic in `Next` assumes `genFuzz` always succeeds; an empty or broken generation path would crash the fuzzer. Triage is intentionally skipped for hanged programs, which avoids executor starvation but can miss signal. Candidate retries differ in snapshot and non-snapshot mode, so crash attribution and flakiness handling are configuration-sensitive. `ctMu` is a normal mutex with a TODO for read/write locking, so choice-table access can serialize hot paths.

## Test Signals
`fuzzer_test.go` integration-runs a local executor in `TestFuzz`, benchmarks `Next`/`Done` loops, emulates execution signal, and checks goroutine cleanup. Job tests indirectly validate triage support logic.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/fuzzer/fuzzer.go -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/fuzzer/fuzzer_test.go -->
# sources/test-tools/syzkaller/pkg/fuzzer/fuzzer_test.go

## Purpose
This file provides an end-to-end fuzzer smoke test using syzkaller's test target and local RPC executor, plus a parallel benchmark for request generation and completion.

## Important APIs, Types, And Functions
`TestFuzz` builds a test executor with coverage instrumentation, creates a monitored corpus, constructs a fuzzer with one enabled syscall, runs `testFuzzer`, and asserts expected crashes and non-empty corpus/signal. `BenchmarkFuzzer` creates a full-call fuzzer and runs parallel `Next`/`Done` cycles using `emulateExec`. `emulateExec` derives deterministic per-call signal/cover from serialized program lines and syscall IDs.

`testFuzzer` implements `queue.Source` for `rpcserver.RunLocal`. Its `Next` delegates to `fuzzer.Next`, adds executor environment flags and output/error requests, and installs an `OnDone` hook. `OnDone` detects crash markers in executor output, tracks crash classes, logs progress, and cancels once iteration limit or success criteria are met. `checkGoroutineLeaks` scans runtime stacks for leaked fuzzer goroutines after context cancellation.

## Control Flow
The test starts a local RPC server with `MachineChecked` returning the `testFuzzer` source. Executor workers repeatedly call `Next`, execute requests, and invoke callbacks. The callback can mark results as crashed based on output and terminates the test by canceling context when all expected crashes and corpus/signal criteria are satisfied.

## State And Persistence Behavior
State is test-local: crash counters, iteration count, output buffer, temporary executor directory, monitored corpus, and an atomic finished flag. The finished flag avoids data races and late logging after the test ends.

## Dependencies And Integration Points
The test integrates `csource`, `rpcserver`, `vminfo`, `flatrpc`, `queue`, `corpus`, `prog`, `targets`, and `testutil`. It is the strongest signal that fuzzer queues, generated requests, local executor protocol, corpus saving, and crash handling work together.

## Risks
The test depends on target compiler availability and skips if the cross-compiler is broken. It has an iteration limit, so slow or unlucky fuzzing can fail even if the implementation is correct. Hints are not emulated in `OnDone`, leaving that path less covered by this integration test.

## Test Signals
Assertions require all expected crash classes, non-empty corpus, and non-empty signal. The benchmark checks for allocation/performance regressions in the hot fuzzer loop but does not assert behavioral outcomes beyond successful execution.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/fuzzer/fuzzer_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/fuzzer/job.go -->
# sources/test-tools/syzkaller/pkg/fuzzer/job.go

## Purpose
This file implements asynchronous fuzzer jobs: triage, minimization, corpus insertion, smash mutation, fault injection, and comparison-guided hints. It is where potentially interesting execution results are deflaked, minimized, and turned into persistent corpus inputs and follow-up work.

## Important APIs, Types, And Functions
`JobType` identifies `triage`, `candidate_triage`, `smash`, and `hints`. `JobInfo` provides introspection fields and a synchronized log buffer. `genProgRequest` and `mutateProgRequest` build execution requests for generated and mutated programs. `triageJob` stores the program, executor to avoid, flags, queue, candidate calls, and job info. `triageCall` tracks original errno, new signal, deflake run signals, stable signal, new stable signal, cover, and raw cover.

`triageJob.run` logs input and calls, deflakes, then handles each call concurrently. `deflake` reruns the program with signal/cover collection, avoids already-used executors, merges flaky max signal, computes signal common to required runs, and records coverage/raw cover. `stopDeflake` encodes different stopping policies for snapshot mode, new fuzz programs, and corpus retriage. `minimize` wraps `prog.Minimize` and reexecutes candidates to preserve new stable signal. `handleCall` starts smash, hints, and fault-injection jobs as configured and saves a new corpus input. `smashJob`, `faultInjectionJob`, and `hintsJob` implement follow-up execution strategies.

## Control Flow
Triage begins after `processResult` finds new signal. It reruns the same program until enough stable signal is found or stopping conditions say more runs are not useful. Calls with new stable signal are minimized unless already minimized, filtered by call name, saved to the corpus, and used to schedule extra work. Smash runs 25 mutations. Fault injection walks `FailNth` from 1 to 100 until the executor stops injecting. Hints first collect stable comparisons over three runs, applies the hints limiter, then mutates with hints and executes each generated program.

## State And Persistence Behavior
Persistent output is delegated to `Config.Corpus.Save` with program, call, stable signal, serialized cover, and optional raw cover. Job logs and exec counters are held in `JobInfo` for live introspection. Deflake state is per job/call and includes arrays of signal intersections by run count. Fault injection modifies cloned programs only.

## Dependencies And Integration Points
The code depends on `prog` generation/mutation/minimization/hints APIs, `pkg/corpus`, `pkg/cover`, `pkg/signal`, `flatrpc` call flags and exec flags, and the queue executor interface. It is launched by `Fuzzer.startJob` and observed via `Fuzzer.RunningJobs`.

## Risks
Deflake thresholds are probabilistic and tuned for flaky reproduction; changes can create duplicate work or drop useful inputs. `handleCall` launches follow-up jobs before corpus save completion is externally visible. Concurrent per-call handling shares the same base job and fuzzer state, relying on downstream thread safety. Hints can generate many executions and are limited only by `hintsLimiter` and mutation behavior.

## Test Signals
`job_test.go` targets deflake signal/coverage behavior. `fuzzer_test.go` indirectly exercises triage, corpus insertion, and follow-up jobs in an executor-backed fuzz run.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/fuzzer/job.go -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/fuzzer/job_test.go -->
# sources/test-tools/syzkaller/pkg/fuzzer/job_test.go

## Purpose
This file tests `triageJob.deflake`, especially how repeated executions are merged into stable signal and coverage.

## Important APIs, Types, And Functions
`TestDeflake` defines table-driven cases with initial `triageCall` state, an execution callback returning errno/signal/cover per run, and expected run count. It builds a minimal test target/program, creates a `triageJob` with `newCover` and empty config, and invokes `deflake` through a fake executor callback.

## Control Flow
Each case resets derived fields, seeds `signals[0]` from new signal, and calls `deflake`. The fake callback increments run count and returns a `queue.Result` with one `flatrpc.CallInfo`. Assertions compare whether deflake stopped normally, how many runs were used, and whether cover/stable/new-stable signal match expectations.

## State And Persistence Behavior
State is in-memory test data. It verifies that coverage is unioned across runs and that stable signal uses the required-run intersection logic. One case includes a differing errno comment, although the visible fake result still supplies call info directly to deflake.

## Dependencies And Integration Points
The test depends on `cover`, `signal`, `flatrpc`, `queue`, `prog`, `targets`, and `testify/assert`. It validates the core triage policy used before corpus insertion.

## Risks
The test focuses on single-call behavior and does not cover minimization, corpus saving, hints, fault injection, snapshot stopping, corpus-specific stopping, or executor stop statuses.

## Test Signals
Expected signals include empty stable output after fully flaky runs, unioned coverage, and new stable signal intersection. The run-count assertions guard deflake stopping conditions.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/fuzzer/job_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/fuzzer/queue/distributor.go -->
# sources/test-tools/syzkaller/pkg/fuzzer/queue/distributor.go

## Purpose
`Distributor` wraps a request source and distributes requests across VMs while honoring soft `Avoid` preferences used during triage reruns. It delays requests that should avoid the requesting VM when other active VMs are available.

## Important APIs, Types, And Functions
`Distributor` stores an underlying `Source`, sequence counter, delayed queue, active-VM array, and stats for delayed, undelayed, and violated requests. `Distribute` constructs it and registers stats. `Next(vm int)` records activity, first tries delayed work suitable for the VM, then pulls from the source until it finds a request that can run immediately or no request exists. `delay`, `delayed`, `noteActive`, `hasOtherActive`, and `contains` implement the policy.

## Control Flow
On each VM request, `Next` calls `noteActive`. If a delayed request is runnable on this VM, it returns it. Otherwise it pulls fresh requests; if a request wants to avoid this VM and some other recent active VM is available, the request is queued as delayed and polling continues. Delayed requests are eventually released after about 1000 sequence ticks even if this violates avoidance.

## State And Persistence Behavior
All state is in memory. `active` is an atomic pointer to a slice of atomic VM sequence markers and can grow when higher VM IDs appear. Delayed requests store `delayedSince` on the request itself. Stats accumulate process-wide observations.

## Dependencies And Integration Points
It depends on the queue `Source`/`Request` model and `stat`. `triageJob.deflake` uses `Avoid` to prefer not rerunning a program on the same executor that first observed it.

## Risks
Avoidance is intentionally soft; if active VM detection is stale or no alternative remains, a request can run on an avoided VM. The active slice growth path assumes `active` is non-nil by the time `hasOtherActive` is called; `Next` establishes that through `noteActive`. The 1000-tick threshold is heuristic.

## Test Signals
`distributor_test.go` verifies normal pass-through, avoid-delay behavior, eventual violation when only the avoided VM polls, and immediate dispatch when all active VMs are in the avoid set.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/fuzzer/queue/distributor.go -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/fuzzer/queue/distributor_test.go -->
# sources/test-tools/syzkaller/pkg/fuzzer/queue/distributor_test.go

## Purpose
This test documents and validates the soft VM-avoidance policy in `Distributor`.

## Important APIs, Types, And Functions
`TestDistributor` uses a `Plain` queue wrapped by `Distribute`, submits a reusable `Request`, mutates its `Avoid` list, and calls `dist.Next(vm)` for VM IDs 0 and 1.

## Control Flow
The test first checks pass-through with no avoidance. It then sets `Avoid` to VM 0, verifies VM 0 receives nil while VM 1 receives the request, then submits again and loops until VM 0 eventually receives it after the violation threshold. Finally it sets both active VMs in `Avoid` and expects immediate dispatch.

## State And Persistence Behavior
The test exercises delayed queue state, active VM sequence tracking, and `Request.delayedSince`.

## Dependencies And Integration Points
It depends only on `queue` package types and `testify/assert`. It supports the triage rerun behavior used by fuzzer jobs.

## Risks
The eventual-release loop has no explicit iteration cap, relying on the implementation's fixed 1000-tick cutoff.

## Test Signals
Assertions cover pass-through, delay, undelay on alternate VM, violation after repeated polling, and no delay when every active VM is avoided.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/fuzzer/queue/distributor_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/fuzzer/queue/prio_queue.go -->
# sources/test-tools/syzkaller/pkg/fuzzer/queue/prio_queue.go

## Purpose
This file provides a small generic heap wrapper used by dynamic ordering queues. Lower integer priority values are popped first.

## Important APIs, Types, And Functions
`priorityQueueOps[T]` wraps `priorityQueueImpl[T]` and exposes `Len`, `Push(item, prio)`, and `Pop`. `priorityQueueItem[T]` stores value and priority. `priorityQueueImpl[T]` implements `heap.Interface`: `Len`, `Less`, `Swap`, `Push`, and `Pop`.

## Control Flow
`Push` delegates to `heap.Push`; `Pop` returns the zero value when empty or heap-pops the next item. `Less` compares priorities ascending, making smaller priority values higher service priority.

## State And Persistence Behavior
State is an in-memory slice heap. `Pop` nils the removed slot to release references before shrinking the slice.

## Dependencies And Integration Points
It depends on the standard `container/heap` package and is used by `DynamicOrderer` in `queue.go` to order nested executor queues.

## Risks
Equal-priority ordering is not stable. Consumers that require FIFO ordering within a priority need a sequence tie-breaker, which this implementation does not provide.

## Test Signals
`prio_queue_test.go` confirms ascending priority order, zero value on empty pop, and zero length after all pops.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/fuzzer/queue/prio_queue.go -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/fuzzer/queue/prio_queue_test.go -->
# sources/test-tools/syzkaller/pkg/fuzzer/queue/prio_queue_test.go

## Purpose
This file unit-tests the generic priority queue wrapper.

## Important APIs, Types, And Functions
`TestPrioQueueOrder` constructs `priorityQueueOps[int]`, pushes values with priorities 1, 3, and 2, then pops and checks values.

## Control Flow
The test exercises heap insertion, ordered removal, empty pop, and final length.

## State And Persistence Behavior
All state is local heap memory.

## Dependencies And Integration Points
It uses `testify/assert`. It validates the primitive used by `DynamicOrderer`.

## Risks
The test does not cover equal priorities or non-int payloads, but generic behavior is independent of payload type.

## Test Signals
Expected pop sequence is 1, 2, 3, then zero on empty with length zero.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/fuzzer/queue/prio_queue_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/fuzzer/queue/queue.go -->
# sources/test-tools/syzkaller/pkg/fuzzer/queue/queue.go

## Purpose
This file defines the fuzzer execution queue abstraction and a set of composable queue/source wrappers. It is the boundary between request producers and executor consumers.

## Important APIs, Types, And Functions
`Request` describes executable work: request type, exec options, program or binary/glob data, signal/output/error return options, completion stat, importance, executor avoidance, completion callback chain, retry state, and wait channel. `ExecutorID` identifies VM/proc. `DoneCallback` can intercept completion. `Result` carries `ProgInfo`, executor ID, output, status, and error. `Status` distinguishes success, executor failure, crash, restart, and hang.

Core methods include `Request.OnDone`, `Done`, `Wait`, `Risky`, `Validate`, `hash`, and `initChannel`; `Result.clone`, `Stop`, and `GlobFiles`; and queue interfaces `Executor` and `Source`.

Queue implementations and wrappers include `PlainQueue` FIFO, `Order`, `Callback`, `Alternate`, `DynamicOrderer`, `DynamicSourceCtl`, `Deduplicate`, `DefaultOpts`, `RandomQueue`, and `Tee`.

## Control Flow
Producers call `Submit`; consumers call `Next`; executors eventually call `Done`. `OnDone` composes callbacks in LIFO order, and any callback can stop further processing by returning false. `Wait` blocks on request completion or context cancellation. `Deduplicator.Next` hashes requests, runs the first unique request, queues duplicate waiters until the result is known, then broadcasts cloned results. `DefaultOpts` ORs default flags into each request. `RandomQueue` randomly evicts or returns entries. `Tee` duplicates a minimal copy of each request to another executor while returning the original.

## State And Persistence Behavior
State is in-memory and concurrency-protected with mutexes/atomics. Requests carry mutable callback, result, done channel, crash/retry markers, and delayed sequence. `PlainQueue` compacts its slice after enough consumed entries. `Deduplicator` caches all seen request hashes and results for the life of the wrapper. `RandomQueue` can complete evicted requests with `ExecFailure`.

## Dependencies And Integration Points
It depends on `flatrpc` for request types and exec flags, `prog` for program serialization/cloning, `hash`, `stat`, `encoding/gob`, and standard concurrency packages. The fuzzer uses `Plain`, `DynamicOrder`, `Order`, and callbacks heavily; retry/distributor wrappers can sit between fuzzer and RPC executor.

## Risks
`Request.OnDone` mutates the callback chain without locking and is intended to be configured before concurrent completion. `Deduplicator` may grow without eviction and hashes serialized programs/options rather than all request sideband fields. `Request.Validate` requires a sandbox for program requests, so callers must apply defaults before validation. `Tee` only copies core execution identity fields and intentionally drops return flags/importance/callbacks.

## Test Signals
`queue_test.go` covers FIFO behavior, dynamic priority ordering, glob output parsing, and tee copy semantics. Retry and priority primitives have separate tests.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/fuzzer/queue/queue.go -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/fuzzer/queue/queue_test.go -->
# sources/test-tools/syzkaller/pkg/fuzzer/queue/queue_test.go

## Purpose
This file tests core queue behavior: FIFO ordering, dynamic priority ordering, glob output parsing, and tee request copying.

## Important APIs, Types, And Functions
`TestPlainQueue` verifies `PlainQueue.Submit`/`Next`. `TestPrioQueue` exercises `DynamicOrderer.Append` priority ordering. `TestGlobFiles` checks nul-separated output parsing. `TestTee` checks that `Tee` returns the original request and submits a sanitized copy to the duplicate queue.

## Control Flow
Tests submit requests, call `Next`, and compare identity or field values. `TestTee` builds a program request with fields that should and should not be copied, then inspects the duplicate request.

## State And Persistence Behavior
Tests exercise in-memory queue state and do not persist data.

## Dependencies And Integration Points
The file uses `flatrpc`, `prog`, and `testify/assert`. It covers primitives used by fuzzer execution scheduling and side-channel duplicate execution.

## Risks
No tests cover `Deduplicate`, `DefaultOpts`, `DynamicSourceCtl`, `Alternate`, `Callback`, or `RandomQueue` in this file.

## Test Signals
Assertions lock in FIFO order, low-priority-number-first dynamic ordering, nil/nonnull glob parsing, and tee dropping `ReturnOutput`/`Important` while copying type/options/program identity data.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/fuzzer/queue/queue_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/fuzzer/queue/retry.go -->
# sources/test-tools/syzkaller/pkg/fuzzer/queue/retry.go

## Purpose
`Retry` is a source wrapper that requeues requests when executor/VM outcomes indicate retry is appropriate. It handles VM restarts and important-request crash retries before allowing completion to propagate.

## Important APIs, Types, And Functions
`retryer` holds a retry `PlainQueue` and a base `Source`. `Retry(base Source)` constructs the wrapper. `Next` prefers retry-queue entries using `tryNext`, otherwise pulls from base, and installs `done` as a completion callback. `done` decides whether to propagate completion or requeue.

## Control Flow
On `Success`, `ExecFailure`, or `Hanged`, `done` returns true and completion continues. On `Restarted`, the same request is requeued and completion is intercepted. On `Crashed`, an important request that has not crashed before is marked `onceCrashed`, requeued, and intercepted; otherwise the crash is delivered. Unknown statuses panic.

## State And Persistence Behavior
State is in memory. Retried requests are the same request objects, preserving waiters and callbacks. `onceCrashed` on `Request` records the one allowed important crash retry and is later exposed as `Risky`.

## Dependencies And Integration Points
It depends on `PlainQueue`, `Source`, `Request`, and `Result` from the same package. Fuzzer result processing checks `req.Risky()` to adjust candidate retry behavior after a crash.

## Risks
Restarted requests retry forever; a permanently restarting VM/source path can cause unbounded cycling. Because the same request object is reused, callbacks must be written to tolerate multiple intercepted completions. Important crashed requests are retried only once.

## Test Signals
`retry_test.go` verifies indefinite restart retry, no crash retry for unimportant requests, one crash retry for important requests, and no second crash retry.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/fuzzer/queue/retry.go -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/fuzzer/queue/retry_test.go -->
# sources/test-tools/syzkaller/pkg/fuzzer/queue/retry_test.go

## Purpose
This file unit-tests the retry wrapper's status policy.

## Important APIs, Types, And Functions
`TestRetryerOnRestart` submits important and unimportant requests and repeatedly completes them as `Restarted`. `TestRetryerOnCrash` covers unimportant crash, important crash followed by success, and important crash followed by a second crash.

## Control Flow
Tests pull requests through `Retry(q)`, call `Done` with selected statuses, then check whether `Next` returns the same request again or nil. They also call `Wait` to ensure final delivered statuses match expectations.

## State And Persistence Behavior
The tests exercise retry queue state and the request's `onceCrashed` state.

## Dependencies And Integration Points
The file depends on `context`, `testing`, and `testify/assert`. It validates behavior relied on by fuzzer crash handling and `Request.Risky`.

## Risks
The restart loop test uses a fixed 10 iterations to represent unbounded retry. It does not cover `ExecFailure`, `Hanged`, callback stacking beyond retry, or context cancellation.

## Test Signals
Restarted requests must be returned repeatedly until success. Unimportant crashes complete immediately; important crashes get one retry only.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/fuzzer/queue/retry_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/fuzzer/queue/stats.go -->
# sources/test-tools/syzkaller/pkg/fuzzer/queue/stats.go

## Purpose
This file declares shared queue/fuzzing stats that are updated and read by different parts of the system.

## Important APIs, Types, And Functions
`StatNoExecRequests` tracks stalls when the fuzzer has no execution requests. `StatNoExecDuration` tracks aggregate stall duration in nanoseconds per second. `StatExecBufferTooSmall` tracks program serialization overflow of the executor buffer.

## Control Flow
There are no functions. Stats are registered at package initialization through `stat.New`.

## State And Persistence Behavior
Stats are process-global metric values managed by the `stat` package. They are not persisted by this file.

## Dependencies And Integration Points
The only dependency is `pkg/stat`. Executor/RPC loops and serialization paths can update these counters to expose scheduling and buffer issues.

## Risks
Global stat registration makes names part of the monitoring interface; renaming affects dashboards or consumers.

## Test Signals
No direct tests in this item.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/fuzzer/queue/stats.go -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/fuzzer/queue/status_string.go -->
# sources/test-tools/syzkaller/pkg/fuzzer/queue/status_string.go

## Purpose
This is generated `stringer` output for the `Status` enum in `queue.go`.

## Important APIs, Types, And Functions
The generated `_` function asserts constant values for `Success`, `ExecFailure`, `Crashed`, `Restarted`, and `Hanged`. `_Status_name` and `_Status_index` encode enum names. `Status.String` returns the symbolic name for known values and `Status(n)` for unknown values.

## Control Flow
`String` computes an index from the enum integer, bounds-checks it, and slices the packed name string for valid statuses.

## State And Persistence Behavior
There is no mutable state. The encoded names are compile-time constants.

## Dependencies And Integration Points
It depends on `strconv`. It is used by formatting/logging/status messages throughout queue and fuzzer code.

## Risks
Manual edits or changed enum ordering without regenerating would make status strings wrong. The compile-time invalid-index checks catch changed constant values during build.

## Test Signals
No direct tests in this item; build success is the main guard for enum drift.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/fuzzer/queue/status_string.go -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/fuzzer/stats.go -->
# sources/test-tools/syzkaller/pkg/fuzzer/stats.go

## Purpose
This file defines the fuzzer's metric registry and per-syscall overflow counters.

## Important APIs, Types, And Functions
`Stats` contains per-syscall `SyscallStats` plus many `stat.Val` pointers for candidates, new inputs, running jobs by type, execution counts by source/type, execution time, and coverage/comparison overflows. `SyscallStats` stores atomic cover and comparison overflow counters. `newStats(target)` allocates one syscall stat per syscall plus one extra/remote bucket and registers all named metrics.

## Control Flow
`newStats` is a constructor returning a populated `Stats` value. Metrics use graph, stacked graph, rate, distribution, console, link, and no-graph options.

## State And Persistence Behavior
Stats are in-memory process metrics. Per-syscall overflow counters are atomics updated by `Fuzzer.handleCallInfo`. The extra slot handles aggregate extra/remote call info.

## Dependencies And Integration Points
It depends on `pkg/stat` and `prog.Target`. `Fuzzer` embeds `Stats`, jobs update job/execution stats, and queue/fuzzer web endpoints can link job stats by type.

## Risks
Metric names and graph groupings are external observability contracts. The `Syscalls` slice indexing assumes syscall IDs align with `target.Syscalls` and reserves the last slot for extra info.

## Test Signals
No direct tests in this item. Integration tests observe some stats indirectly through corpus/signal behavior and debug logging.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/fuzzer/stats.go -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/gce/gce.go -->
# sources/test-tools/syzkaller/pkg/gce/gce.go

## Purpose
Package `gce` wraps Google Compute Engine APIs for syzkaller managers running on GCE. It discovers the current project, zone, network, and instance metadata, creates/deletes worker instances and images, rate-limits API calls, and tracks preferred zones for preemptible capacity.

## Important APIs, Types, And Functions
`Context` stores project/zone/region, current instance and IPs, network/subnetwork, preemptible and normal zone lists, compute service, metadata server, and API rate gate. `zoneList` stores preferred zone, ordered zone list, and scores. `InstanceConfig` describes worker VM creation parameters; `CreateArgs` exists for simple creation options.

`NewContext` creates an OAuth-backed compute service, reads metadata, validates zone, derives region, discovers current instance network/IPs, queries regional zones, and initializes zone lists. `CreateInstance` builds a `compute.Instance`, handles C4A disk sizing, nested virtualization, display device, spot/preemptible scheduling, max runtime deletion, zone retry/fallback, waits for operation completion, then returns internal IP and zone. `DeleteInstance`, `DeleteInstanceAcrossZones`, `IsInstanceRunning`, `CreateImage`, and `DeleteImage` wrap corresponding Compute APIs. `waitForCompletion` polls global/zonal operations and maps resource-pool exhaustion to `resourcePoolExhaustedError`. `apiCall` rate-gates and backs off rate-limit errors. Helpers include `localZone`, `validateZone`, `zoneToRegion`, `promote`, zone score updates, `ReportPreemption`, and `zoneList.get`.

## Control Flow
Initialization performs metadata reads before Compute API reads so it can address the current instance. Instance creation iterates scored zones; on resource exhaustion it tries later zones, and for preemptible instances can fall back to standard provisioning after exhausting preemptible zones. Operation waits loop until `DONE` or error. Zone scoring decays each insertion attempt and rewards success, then stable-sorts by score with preferred-zone promotion as a tie breaker.

## State And Persistence Behavior
GCE resources are persistent cloud state: instances, disks, images, metadata, scheduling policy, and network attachments. Local `Context` state caches zone scores and network metadata for the process. API rate gating is process-local. Delete helpers intentionally treat 404 as success for idempotence.

## Dependencies And Integration Points
The package depends on Google OAuth, Compute API client, Google API errors, metadata via HTTP, syzkaller logging, and target OS constants. It integrates with VM manager code that provisions fuzzing workers and images in the current GCE project/region.

## Risks
The package assumes it runs on GCE and can query metadata. `getMeta` does not check HTTP status codes before returning body text. `apiCall` uses a one-second ticker, making operations conservative but potentially slow. Zone scoring is in-memory and randomizes preferred zone 5 percent of the time, so behavior can vary across runs. `CreateInstance` returns immediately on an insert API error rather than trying later zones; only operation-level resource exhaustion uses zone fallback.

## Test Signals
`gce_test.go` covers zone validation, region extraction, C4A disk sizing, metadata local-zone parsing, and zone prioritization/score changes. Cloud API operations are not directly tested here.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/gce/gce.go -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/gce/gce_test.go -->
# sources/test-tools/syzkaller/pkg/gce/gce_test.go

## Purpose
This file unit-tests deterministic helper behavior in the GCE wrapper without calling real cloud APIs.

## Important APIs, Types, And Functions
`TestValidateZone` checks valid zone strings and rejects a region-only name. `TestZoneToRegion` checks region extraction from common and multi-part region names. `TestDiskSizeGB` checks special C4A disk sizing. `TestLocalZone` uses an `httptest.Server` to emulate metadata zone output. `TestZoneListPrioritization` exercises zone score sorting, success, preemption, insertion failure, and repeated success.

## Control Flow
The metadata test replaces `Context.metadataServer` with the test server URL and calls `localZone`. The zone-list test initializes equal scores, sorts, mutates scores through record methods, and asserts the expected list order after each step.

## State And Persistence Behavior
All state is in-memory test data. The HTTP server provides transient metadata response only.

## Dependencies And Integration Points
The tests use `net/http/httptest` and `testify/assert`. They cover helper functions used by real `NewContext` and VM creation.

## Risks
No tests mock `compute.Service`, so create/delete image/instance paths, operation waiting, API rate-limit handling, and resource exhaustion fallback are untested in this file.

## Test Signals
Assertions lock in zone regex behavior, region parsing, disk-size policy, metadata path handling, and zone score decay/reward ordering.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/gce/gce_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/gcpsecret/secret.go -->
# sources/test-tools/syzkaller/pkg/gcpsecret/secret.go

## Purpose
Package `gcpsecret` resolves secrets from GCP Secret Manager or environment variables for syzkaller configuration. It also exposes helpers to discover the current GCP project when running on GCE/GKE.

## Important APIs, Types, And Functions
`GcpSecret(name)` reads a Secret Manager version using a background context. `GcpSecretWithContext(ctx, name)` creates a Secret Manager client, calls `AccessSecretVersion`, closes the client, and returns payload bytes. `LatestGcpSecret(ctx, projectName, key)` formats the latest-version resource path. `ProjectName(ctx)` checks `metadata.OnGCE` and returns the metadata project ID. `Resolve(ctx, val)` returns `env:` values from `os.Getenv`, `gcp-secret:` values from Secret Manager in the current project, and unprefixed values unchanged. `init` calls `runtime.KeepAlive(GcpSecret)` for dashboard/app config usage.

## Control Flow
Resolution is prefix-based. Environment lookup is local and returns empty string without error for missing variables. GCP secret lookup first determines project name, then reads the latest secret version, wrapping errors with project/secret context.

## State And Persistence Behavior
The package does not persist local state. It reads external secret state from Secret Manager and process environment. Each secret read creates and closes a client, so there is no cached client state.

## Dependencies And Integration Points
It depends on GCP metadata and Secret Manager clients, `context`, `os`, `runtime`, and `strings`. It is intended for dashboard/app configs and any syzkaller component that accepts literal, environment-backed, or Secret Manager-backed config values.

## Risks
`Resolve` silently returns an empty string for missing environment variables. `ProjectName` fails off GCE/GKE, so `gcp-secret:` values are not portable to local environments without metadata. Creating a new Secret Manager client per call is simple but may be inefficient for many secrets.

## Test Signals
No tests for this file are included in the item. Useful tests would cover prefix parsing, env fallback, off-GCE errors, and a mocked Secret Manager access path.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/gcpsecret/secret.go -->
