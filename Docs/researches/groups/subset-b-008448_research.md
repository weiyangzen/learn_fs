# Research Report: subset-b-008448

This grouped report covers fdbrpc asynchronous file backends, checksum/file-transfer helpers, Base64 utilities, gRPC integration tests, and Flow runtime tests for `subset-b-008448`. Each source section is delimited for reconciliation into the mapped source-tree-aligned research document.

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbrpc/AsyncFileKAIO.h -->
# sources/storage-engines/foundationdb/fdbrpc/AsyncFileKAIO.h

## Purpose
`AsyncFileKAIO.h` implements FoundationDB's Linux-only unbuffered `IAsyncFile` backend using kernel AIO, `eventfd`, and direct I/O. It is selected when POSIX KAIO is enabled and exposes asynchronous read/write, truncate, size, sync, zero-range, file locking, and atomic-create behavior.

## Important APIs, Types, and Functions
The main type is `AsyncFileKAIO`, a final `IAsyncFile`/`ReferenceCounted` implementation. Important entry points are `open`, `init`, `setTimeout`, `read`, `write`, `zeroRange`, `truncate`, `sync`, `size`, `debugFD`, `launch`, and `poll`. Internal types include `IOBlock`, which embeds `linux_iocb` and carries result promises, owner references, priority, timeout-list pointers, and start times, and `Context`, the singleton KAIO context holding `io_context_t`, eventfd, queues, outstanding counts, timeout state, metrics, and fallocate capability flags. `AsyncFileKAIOMetrics` exposes latency samples for reads, writes, and syncs; `SlowAioSubmit` is an event metric payload for slow submissions.

## Control Flow
`open` translates Flow open flags to `O_DIRECT | O_CLOEXEC` POSIX flags, optionally uses `filename + ".part"` for atomic create, applies advisory mandatory-lock setup, records initial file size, and returns the file object. `init` calls `io_setup`, stores the eventfd, starts the `poll` actor, and registers `launch` as the network run-cycle hook. Reads and writes allocate an `IOBlock`, set buffer/length/offset, enqueue it by task priority, and return the block promise. `launch` drains queued blocks up to `MAX_OUTSTANDING`, extends files before submit when `nextFileSize` exceeds `lastFileSize`, calls `io_submit`, increments outstanding counts, and requeues unsubmitted requests. `poll` waits on eventfd, collects completions with `io_getevents`, handles timeout scanning, records latency, and delivers promises at the original task priority.

## State and Persistence Behavior
Persistent state is the underlying file descriptor plus tracked logical file size (`lastFileSize`/`nextFileSize`) and open flags. Durability depends on `sync`, which uses `AsyncFileEIO::async_fdatasync`; if `OPEN_ATOMIC_WRITE_AND_CREATE` is set, the `.part` file is atomically renamed after the sync future completes. The global `Context` owns all KAIO queueing and timeout state for the process. A timeout marks the file failed unless configured warn-only, causing later operations to fail with `io_timeout`.

## Dependencies and Integration Points
The file depends on Linux KAIO wrappers (`linux_kaio.h`), `eventfd`, POSIX file APIs, Flow futures/actors, knobs, metrics, CRC32C for optional logging, and `AsyncFileEIO` for fdatasync/rename fallback. It integrates with `IAsyncFileSystem`, Flow network global run-cycle hooks, task priorities, network disk-stall metrics, and trace/event metrics.

## Risks and Edge Cases
All enqueued buffers, offsets, and lengths must be 4096-byte aligned; violations assert. `zeroRange` checks `fallocate` incorrectly against `EOPNOTSUPP` as a direct return code rather than via `errno`, so unsupported zeroing can be misdetected. Pre-submit file extension synchronously calls `truncate`/`fallocate` inside `launch`, which can stall the network loop and is monitored as slow submit. Partial `io_submit` handling assumes non-EAGAIN errors correspond to the first I/O. Timeout handling marks file-level failure but cannot cancel already submitted KAIO requests. `KAIO_LOGGING` writes to a hardcoded path and should remain disabled outside investigations.

## Test Signals
Signals are mostly integration-level: direct-I/O file tests, storage engine simulation tests using unbuffered files, latency/slow-submit events, timeout fault-injection behavior, and atomic-create rename correctness. There is no focused unit test in this subset for KAIO queue ordering, timeout list removal, or fallocate fallback.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbrpc/AsyncFileKAIO.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbrpc/AsyncFileNonDurable.cpp -->
# sources/storage-engines/foundationdb/fdbrpc/AsyncFileNonDurable.cpp

## Purpose
`AsyncFileNonDurable.cpp` implements simulation wrappers that make async file behavior process-aware and fault-injectable. It models non-durable disks, shutdown races, machine/process context switching, delete/open serialization, and detachable files for FoundationDB simulation.

## Important APIs, Types, and Functions
Top-level helpers include `waitShutdownSignal`, `sendOnProcess`, and `sendErrorOnProcess`. `AsyncFileDetachable` provides `open`, `doShutdown`, and forwarded `read`, `write`, `truncate`, `sync`, and `size` methods that fail after simulated shutdown. `AsyncFileNonDurable::open` wraps a real `IAsyncFile`, initializes approximate size, waits for ongoing deletion, and returns an `AsyncFileNonDurable`. `read`, `closeFile`, and `removeOpenFile` manage machine/process transitions and cleanup.

## Control Flow
Opening captures the current simulated process and task priority, switches to the machine context, waits for the wrapped file or shutdown, blocks behind `filesBeingDeleted` for the same logical filename, constructs the wrapper, initializes its size through the wrapper path, then switches back to the original process. Reads switch to the machine, invoke `onRead`, and switch back before returning or rethrowing. Closing marks the file as deleting/closing, signals pending sync, waits for outstanding modifications, waits for kill completion if needed, removes machine bookkeeping entries, erases deletion guards, and deletes the wrapper.

## State and Persistence Behavior
The wrapper does not implement durable persistence by itself; it records and mediates simulated state around a wrapped file. Shared state includes `AsyncFileNonDurable::filesBeingDeleted`, machine `openFiles`, `closingFiles`, `deletingOrClosingFiles`, pending modification ranges, kill promises, and open address. Shutdown clears detachable references and turns later file calls into injected `io_error`.

## Dependencies and Integration Points
The code depends on `fdbrpc/AsyncFileNonDurable.h`, simulator machine/process info, Flow coroutines, simulator shutdown signals, `g_simulator`, and `g_network`. It integrates tightly with simulation disk fault behavior, process scheduling, and machine-local open file tracking.

## Risks and Edge Cases
The file depends on correct process/machine switching around every operation; missed switches can run callbacks in the wrong simulated process. Delete/open serialization is keyed by logical filename and can block unrelated reopen paths if cleanup fails. `removeOpenFile` defensively handles stale map entries and renamed files, which shows open-file bookkeeping can diverge during simulated deletes or atomic renames. Errors during open must erase `openFiles` based on either the resolved wrapped filename or actual filename.

## Test Signals
Primary signals are simulation tests that kill processes during file operations, delete or rename files while opens are pending, and exercise non-durable disk faults. There are no direct unit tests here; correctness is inferred from simulation stability and absence of leaked open-file/deletion state.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbrpc/AsyncFileNonDurable.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbrpc/AsyncFileWinASIO.h -->
# sources/storage-engines/foundationdb/fdbrpc/AsyncFileWinASIO.h

## Purpose
`AsyncFileWinASIO.h` provides the Windows `IAsyncFile` backend using `boost::asio::windows::random_access_handle` over a `CreateFile` handle opened with no buffering and overlapped flags.

## Important APIs, Types, and Functions
The main type is `AsyncFileWinASIO`. Important methods include `open`, `deleteFile`, `lastWriteTime`, `read`, `write`, `truncate`, `sync`, `size`, `renameFile`, `debugFD`, and callback helpers `onReadReady`/`onWriteReady`. The implementation stores the ASIO random-access handle, open flags, and original filename.

## Control Flow
`open` handles atomic-create by opening `filename + ".part"`, maps Flow flags to `CreateFile` access/share/creation options, and wraps the handle in the ASIO file object. `read` checks the current file size, returns zero at EOF, and issues `async_read_some_at`. `write` issues `boost::asio::async_write_at` and validates the exact byte count. `truncate` uses `SetFilePointerEx` plus `SetEndOfFile`. `sync` calls `FlushFileBuffers` and, for atomic create, moves the `.part` file to the target.

## State and Persistence Behavior
Persistent state is the Windows file handle and open flags. Writes become durable only when `sync` flushes the handle. Atomic create state is stored in the flags until the first `sync`, which performs the move and clears `OPEN_ATOMIC_WRITE_AND_CREATE`.

## Dependencies and Integration Points
The file is compiled only under `WIN32`, aliases `Net2AsyncFile` to `AsyncFileWinASIO`, and depends on Windows APIs plus Boost.Asio. It integrates with Flow's `IAsyncFile` abstraction and platform helpers `deleteFile`/`renameFile`.

## Risks and Edge Cases
The file comments note that the implementation is not fully asynchronous: truncate and sync are synchronous and can block the network thread. `getClassName` contains a spelling typo (`AsnycFileWinASIO`). `MoveFile` during atomic sync does not use write-through semantics and its result is not checked. No-buffering on Windows imposes alignment constraints, but this wrapper does not assert alignment the way KAIO does. `read` calls `size().get()` inline, so size errors propagate synchronously.

## Test Signals
Signals are Windows builds and file-system integration tests that use unbuffered I/O. This subset has no Windows-specific unit test for short writes, atomic rename failure, alignment enforcement, or blocking sync/truncate behavior.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbrpc/AsyncFileWinASIO.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbrpc/AsyncFileWriteChecker.cpp -->
# sources/storage-engines/foundationdb/fdbrpc/AsyncFileWriteChecker.cpp

## Purpose
`AsyncFileWriteChecker.cpp` defines static storage for the write-checker wrapper and contains a focused unit test for its LRU checksum-history data structure.

## Important APIs, Types, and Functions
It initializes `AsyncFileWriteChecker::checksumHistoryBudget` and `checksumHistoryPageSize`. `compareWriteInfo` asserts equality of timestamp/checksum pairs. The local `LRU2` reference implementation uses a linked list plus unordered map to model expected LRU behavior. The test case `/fdbrpc/AsyncFileWriteChecker/LRU` compares the production `LRU` against `LRU2`.

## Control Flow
The test runs 1000 randomized operations. Each iteration either updates a random page with a new checksum/timestamp, removes a random existing page, or truncates at a random page. After each operation it checks existence, stored write info, and least-recently-used page agreement between the production and reference implementations.

## State and Persistence Behavior
The file owns process-static checker budget and page size defaults. Test state is transient and uses deterministic randomness. It does not touch disk directly; persistence behavior belongs to the header implementation wrapping `IAsyncFile`.

## Dependencies and Integration Points
The file depends on `AsyncFileWriteChecker.h` and `flow/UnitTest.h`. The test integrates with the FoundationDB unit-test runner and validates the helper used by the runtime checker.

## Risks and Edge Cases
The LRU test validates metadata behavior but not actual asynchronous file read/write verification. It uses deterministic random coverage over a small page range, so it can miss pathological map-order or truncation cases. `LRU2::truncate` is intentionally linear in page number and only suitable for test-sized ranges.

## Test Signals
Passing `/fdbrpc/AsyncFileWriteChecker/LRU` indicates update/remove/truncate/least-recent behavior matches the reference model. It does not validate checksum failure detection, sync-time gating, global budget exhaustion, or interaction with concurrent file writes.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbrpc/AsyncFileWriteChecker.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbrpc/AsyncFileWriteChecker.h -->
# sources/storage-engines/foundationdb/fdbrpc/AsyncFileWriteChecker.h

## Purpose
`AsyncFileWriteChecker.h` implements an `IAsyncFile` wrapper that records checksums for recently written full pages, then continuously reads synced pages back to detect lost or corrupted writes.

## Important APIs, Types, and Functions
The primary type is `AsyncFileWriteChecker`. It forwards most `IAsyncFile` methods while instrumenting `read`, `readZeroCopy`, `write`, `truncate`, and `sync`. `WriteInfo` stores CRC32C and millisecond timestamp. The nested `LRU` stores page-to-write-info history with maps for page order and truncation support. Private actors `sweep` and `runChecksumLogger`, plus helpers `verifyChecksum` and `updateChecksumHistory`, implement verification and logging.

## Control Flow
Writes compute CRC32C for each fully covered checker page, reserve global history budget, insert those pages into the LRU, mark them as actively writing, then erase the writing marks when the underlying write completes. Reads compute page checksums over full pages and compare them against stored history only for pages written before the last successful `sync`. `sync` forwards to the wrapped file and updates `syncedTime` after success. `sweep` repeatedly chooses the least-recently-used page, skips invalid or currently writing pages, and reads it through the wrapper path so successful verification removes it.

## State and Persistence Behavior
The wrapper's persistent state is in memory: wrapped file reference, page buffer, LRU checksum history, global optional budget, `syncedTime`, active-writing set, counters, and background actors. It does not persist metadata to disk. It only treats pages as eligible for verification after sync, matching durability expectations. Truncate removes history at and beyond the new full-page boundary and refunds budget.

## Dependencies and Integration Points
It depends on `flow/IAsyncFile.h`, CRC32C, Flow knobs, trace events, deterministic randomness for LRU sampling, and Valgrind annotations. It can wrap any `IAsyncFile` implementation and is useful for simulation or diagnostic configurations that need lost-write detection.

## Risks and Edge Cases
Only full checker pages are tracked; partial-page writes or reads are skipped. `readZeroCopy` casts `data` rather than `*data` when verifying, which appears suspicious for zero-copy buffers. `syncedTime` is not explicitly initialized in the constructor before first sync, so pre-sync reads rely on default object initialization behavior. The `sweep` actor loops forever and may repeatedly delay if no page is available. Budget exhaustion skips remaining pages in an update range, reducing detection coverage. The class assumes all operations run in Flow's single-threaded event context.

## Test Signals
The companion `.cpp` file tests LRU behavior. Runtime signals include `AsyncFileLostWriteDetected`, periodic `AsyncFileWriteChecker` trace events, success/failure counters, and simulation workloads that enable page write checksum history.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbrpc/AsyncFileWriteChecker.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbrpc/Base64Decode.cpp -->
# sources/storage-engines/foundationdb/fdbrpc/Base64Decode.cpp

## Purpose
`Base64Decode.cpp` implements regular padded Base64 and unpadded URL-safe Base64 decoding, arena-returning decode helpers, decoded-length calculations, and shared unit tests for both encode/decode implementations.

## Important APIs, Types, and Functions
Internal templates include `decodeValue<UrlDecode>`, `doDecode<UrlDecode>`, `getDecodedLength`, and `decodeStringRef<UrlDecode>`. Public functions are `base64::decodedLength`, `base64::decode` overloads, `base64::url::decodedLength`, and `base64::url::decode` overloads. Test helpers include `urlEncodedTestData`, `runTest`, and `transformBase64UrlToBase64`.

## Control Flow
Decoding maps input bytes through a 256-entry table, rejects illegal bytes as `_X`, and emits one to three plaintext bytes per group. Regular Base64 requires length divisible by four and strips up to two trailing `=` padding bytes before decoding. URL-safe Base64 accepts unpadded lengths except the invalid `4n+1` case. Arena decoders precompute output length, allocate in the supplied arena, call `doDecode`, and return an empty `Optional` on invalid input.

## State and Persistence Behavior
The implementation has no persistent runtime state. Arena decode failures may still leave allocated memory in the arena, as documented by the header. Unit-test data is static in the translation unit.

## Dependencies and Integration Points
It depends on `Base64Encode.h`, `Base64Decode.h`, Flow `Arena`, `StringRef`, `Optional`, `UnitTest`, deterministic randomness, and `fmt` for failure diagnostics. It integrates with fdbrpc utility code and tests both itself and the encoder.

## Risks and Edge Cases
Regular `decodedLength(int)` is a conservative estimate because padding is not known from length alone. The pointer-output API assumes callers allocated enough space. Whitespace and line-wrapped Base64 are rejected. Negative input lengths are not defended beyond integer pointer arithmetic expectations. URL-safe decoding intentionally rejects `=` padding.

## Test Signals
`/fdbrpc/Base64UrlEncode` and `/fdbrpc/Base64Encode` cover static vectors, random round trips, alphabet validation, URL-safe no-padding behavior, and regular padding behavior.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbrpc/Base64Decode.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbrpc/Base64Decode.h -->
# sources/storage-engines/foundationdb/fdbrpc/Base64Decode.h

## Purpose
`Base64Decode.h` declares the fdbrpc Base64 decoding API for regular and URL-safe encodings.

## Important APIs, Types, and Functions
In namespace `base64`, it declares raw-buffer `decode`, conservative `decodedLength`, and arena `decode(Arena&, StringRef)`. In `base64::url`, it declares equivalent URL-safe functions whose decoded length can be exact or `-1` for invalid encoded lengths.

## Control Flow
The header has no executable control flow; it defines the API contract consumed by callers and implemented in `Base64Decode.cpp`. The contract distinguishes one-shot decoding from streaming and documents that no line wrapping is supported.

## State and Persistence Behavior
There is no state. Arena decode results are tied to caller-supplied arena lifetime, and invalid decode attempts may still consume arena memory.

## Dependencies and Integration Points
The header includes `<cstdint>` and `flow/Arena.h`, and exposes `StringRef`/`Optional`-based helpers for Flow code. It pairs with `Base64Encode.h` and the implementation tests in `Base64Decode.cpp`.

## Risks and Edge Cases
Callers of raw-buffer decode must size `plaintextOut` correctly. Regular Base64 requires padding-compatible length, while URL-safe Base64 omits padding and rejects `4n+1` lengths. The API is not streaming and does not accept wrapped MIME-style input.

## Test Signals
Coverage is supplied by the unit tests in `Base64Decode.cpp`, which exercise both regular and URL-safe decode declarations through round trips.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbrpc/Base64Decode.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbrpc/Base64Encode.cpp -->
# sources/storage-engines/foundationdb/fdbrpc/Base64Encode.cpp

## Purpose
`Base64Encode.cpp` implements one-shot regular Base64 encoding with `=` padding and URL-safe Base64 encoding without padding.

## Important APIs, Types, and Functions
Internal templates include `encodeValue<UrlEncode>`, `doEncode<UrlEncode>`, `getEncodedLength<UrlEncode>`, and `doEncodeWithArena<UrlEncode>`. Public functions are `base64::encode`, `base64::encodedLength`, `base64::encode(Arena&, StringRef)`, plus `base64::url` equivalents.

## Control Flow
The encoder consumes input in groups of three bytes and emits four 6-bit alphabet characters. For one or two trailing bytes, regular Base64 emits padding while URL-safe Base64 emits only the required unpadded characters. Arena helpers compute exact encoded length, allocate, encode, assert the actual length, and return a `StringRef`.

## State and Persistence Behavior
The implementation has no mutable persistent state. Encoded arena results live for the supplied arena lifetime.

## Dependencies and Integration Points
It depends on `Base64Encode.h` and Flow `Arena`/`StringRef` through the header. `Base64Decode.cpp` contains the test cases that validate this implementation.

## Risks and Edge Cases
The raw-buffer API assumes output capacity is at least `encodedLength(dataLength)`. Negative lengths are not guarded. The implementation intentionally does not line-wrap output and is not streaming. URL-safe output omits padding, so consumers expecting padded Base64 need the regular namespace.

## Test Signals
Round-trip unit tests in `Base64Decode.cpp` validate known vectors, random inputs, padding rules, and URL-safe alphabet constraints.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbrpc/Base64Encode.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbrpc/Base64Encode.h -->
# sources/storage-engines/foundationdb/fdbrpc/Base64Encode.h

## Purpose
`Base64Encode.h` declares the fdbrpc Base64 encoding API for regular and URL-safe one-shot encoders.

## Important APIs, Types, and Functions
The regular namespace declares raw-buffer `encode`, exact `encodedLength`, and arena `encode`. `base64::url` declares the same shape for URL-safe output, replacing `+` and `/` with `-` and `_` and omitting `=` padding.

## Control Flow
The header only declares functions and documents behavior. It establishes that callers must use non-streaming, one-shot input and that no 72-character line wrapping is performed.

## State and Persistence Behavior
There is no state. Arena-returning overloads allocate output in caller-owned `Arena`.

## Dependencies and Integration Points
The header includes `<cstdint>` and `flow/Arena.h` and is consumed by Base64 utilities and tests in fdbrpc.

## Risks and Edge Cases
Raw-buffer callers must use `encodedLength` to avoid overflow. URL-safe and regular encodings are not interchangeable where padding or alphabet constraints matter.

## Test Signals
The implementation is validated by Base64 tests embedded in `Base64Decode.cpp`.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbrpc/Base64Encode.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbrpc/CMakeLists.txt -->
# sources/storage-engines/foundationdb/fdbrpc/CMakeLists.txt

## Purpose
`CMakeLists.txt` defines how the fdbrpc static libraries, link test, fdbrpc test executable, optional coroutine/eio support, optional gRPC/protobuf bindings, benches, and subtests are built.

## Important APIs, Types, and Functions
Key CMake functions/macros include `fdb_find_sources`, `add_flow_target`, `target_link_libraries`, `target_include_directories`, `generate_grpc_protobuf`, `add_library`, `add_dependencies`, and `add_subdirectory`. Targets include `fdbrpc`, `fdbrpc_sampling`, `fdbrpclinktest`, `fdbrpc_test`, optional `eio`, and optional `coro`.

## Control Flow
The script gathers fdbrpc sources, removes standalone test/link sources from the library list, decides whether to compile bundled libeio, disables actor diagnostics for selected actor-heavy files, creates normal and sampling fdbrpc libraries, adds standalone tests, conditionally builds libeio/libcoroutine, configures include paths and libraries, conditionally generates gRPC protobuf code and links gRPC targets, enables sampling definitions, adds Windows actor dependency, and includes bench/tests subdirectories.

## State and Persistence Behavior
It does not affect runtime state. Its persistent effect is build graph structure, compile definitions, include directories, generated protobuf artifacts, and linked dependencies.

## Dependencies and Integration Points
It integrates fdbrpc with Flow, `libb64`, `md5`, `rapidjson`, optional `gRPC::grpc++`, protobuf include directories, generated proto targets, bundled `libeio`, bundled `libcoroutine`, Valgrind, bench builds, and fdbrpc tests.

## Risks and Edge Cases
Source auto-discovery can unexpectedly include new files unless explicitly removed. gRPC linking repeats `proto_fdbrpc_test` for `fdbrpc`, suggesting harmless duplication but possible maintenance drift. Cross-compiling skips benches. The coroutine path depends on `COROUTINE_IMPL` and platform-specific source choices. Third-party warning suppression hides diagnostics from bundled C code.

## Test Signals
Build success for `fdbrpc`, `fdbrpc_sampling`, `fdbrpclinktest`, and `fdbrpc_test` is the main signal. gRPC-enabled builds additionally validate protobuf generation and gRPC link dependencies.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbrpc/CMakeLists.txt -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbrpc/ContinuousSample.h -->
# sources/storage-engines/foundationdb/fdbrpc/ContinuousSample.h

## Purpose
`ContinuousSample.h` provides a small template reservoir sampler that tracks a bounded random sample from a stream plus aggregate min, max, sum, population size, mean over the sample, median, and percentile queries.

## Important APIs, Types, and Functions
The template class `ContinuousSample<T>` exposes `addSample`, `getSamples`, `sum`, `mean`, `median`, `percentile`, `min`, `max`, `clear`, `getPopulationSize`, and `swap`. Private state includes `sampleSize`, `populationSize`, `sorted`, `samples`, `_min`, `_max`, and `_sum`.

## Control Flow
`addSample` updates aggregates, increments population, appends samples until capacity, then uses reservoir sampling probability `sampleSize / populationSize` to replace a random existing sample. Percentile queries sort the retained sample lazily and return the smallest element at least as large as the requested fraction.

## State and Persistence Behavior
All state is in memory. The sampler preserves aggregate population count and sum over all observed samples, but `mean()` is computed over retained samples rather than total `_sum / populationSize`. `clear` resets state but assigns zero to `_min`, `_max`, and `_sum`, which only works for numeric-like `T`.

## Dependencies and Integration Points
It depends on Flow platform/random headers, deterministic randomness, STL vector/algorithm, and math. It is a generic utility for metrics or diagnostics needing bounded samples.

## Risks and Edge Cases
`sampleSize == 0` would cause invalid replacement behavior after the first sample if not avoided by callers. `mean()` may surprise callers because it uses the sample reservoir, while `sum()` returns total accumulated sum. `clear` is not fully generic despite the template. Percentiles on an empty sample or invalid percentile return default `T()`.

## Test Signals
There are no direct tests in this subset. Indirect signals come from metrics or components using `ContinuousSample` and validating percentile/min/max behavior.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbrpc/ContinuousSample.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbrpc/DDSketchTest.cpp -->
# sources/storage-engines/foundationdb/fdbrpc/DDSketchTest.cpp

## Purpose
`DDSketchTest.cpp` contains unit/performance-style tests for the fdbrpc `DDSketch` approximate percentile data structure.

## Important APIs, Types, and Functions
The file imports `fdbrpc/DDSketch.h`, defines `forceLinkDDSketchTests`, and declares test cases `/fdbrpc/ddsketch/accuracy` and `/fdbrpc/ddsketch/correctness`. It uses `DDSketch<double>::addSample` and `percentile`.

## Control Flow
The accuracy test runs 100 trials of one million skewed samples, stores exact values, sorts them, compares selected percentiles against `DDSketch`, accumulates relative error, and prints average errors. The correctness test adds 4000 small positive samples and asserts common percentiles are positive and finite.

## State and Persistence Behavior
All state is transient test memory. The tests do not persist data or modify external state.

## Dependencies and Integration Points
It depends on Flow unit tests, deterministic random sampling, `<limits>`, `<random>`, and `DDSketch`. The `forceLink` function ensures the tests are retained by the linker.

## Risks and Edge Cases
The accuracy test is computationally heavy due to 100 million generated values and sorting one million values per trial. It prints error statistics but does not assert an accuracy threshold, so regressions could be visible only in logs. Correctness only checks positive finite outputs, not exact rank guarantees.

## Test Signals
Passing correctness proves nonzero percentile outputs for a representative positive range. Accuracy logs give diagnostic signals for relative error at extreme and central percentiles.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbrpc/DDSketchTest.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbrpc/FailureMonitor.cpp -->
# sources/storage-engines/foundationdb/fdbrpc/FailureMonitor.cpp

## Purpose
`FailureMonitor.cpp` implements helper waits for endpoint failure state and the simple in-memory failure monitor used by Flow transport to track address health, permanently failed endpoints, unauthorized endpoint access, and disconnect notifications.

## Important APIs, Types, and Functions
Important functions include `waitForStateEqual`, `waitForContinuousFailure`, `IFailureMonitor::onStateEqual`, and `IFailureMonitor::onFailedFor`. `SimpleFailureMonitor` implements `setStatus`, `endpointNotFound`, `unauthorizedEndpoint`, `notifyDisconnect`, `onDisconnectOrFailure`, `onDisconnect`, `onStateChanged`, `getState` overloads, `onlyEndpointFailed`, `permanentlyFailed`, `knownUnauthorized`, and `reset`.

## Control Flow
Wait helpers subscribe to monitor change futures, check current state, and loop until the requested state or sustained-failure condition is met. `SimpleFailureMonitor::setStatus` updates the address-status map and triggers endpoint ranges when address health changes. Endpoint-not-found and unauthorized paths record permanent endpoint failure and trigger that endpoint. Disconnect notification triggers all endpoints on the address plus address-level disconnect watchers. Query methods combine permanent endpoint failures with address status.

## State and Persistence Behavior
State is process-local and in memory: `addressStatus`, `failedEndpoints`, `endpointKnownFailed`, and `disconnectTriggers`. The constructor marks local primary and secondary addresses healthy. `failedEndpoints` can grow for public endpoints; a safety clear occurs after 100000 entries. `reset` clears maps and trigger state.

## Dependencies and Integration Points
It depends on `fdbrpc/FailureMonitor.h`, Flow transport local addresses, network knobs, `AsyncMap`-style triggers, `Endpoint`, `NetworkAddress`, `UID`, and trace events. It is a core integration point for RPC failure handling and load balancing.

## Risks and Edge Cases
`endpointNotFound` comments that permanent endpoint state can leak memory. Well-known endpoint-not-found is logged but not permanently marked. `onStateChanged` returns `Never()` for permanently failed endpoints because their state cannot change, so callers must check state before waiting. Sustained failure wait uses a slope formula and timeout polling rather than only change notifications. Public endpoint failure map clearing loses diagnostic memory to cap growth.

## Test Signals
Flow tests in this subset exercise `waitValueOrSignal` behavior around peer disconnect and retry. Broader transport tests should validate address status changes, unauthorized endpoints, disconnect triggers, and sustained failure waits.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbrpc/FailureMonitor.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbrpc/FileTransfer.cpp -->
# sources/storage-engines/foundationdb/fdbrpc/FileTransfer.cpp

## Purpose
`FileTransfer.cpp` implements a gRPC file-transfer service and client, conditionally compiled when `FLOW_GRPC_ENABLED` is set. It supports metadata lookup, server-streamed chunk downloads, optional CRC32C verification, and test error injection.

## Important APIs, Types, and Functions
Important functions are `crc32_checksum_ifstream`, `FileTransferServiceImpl::DownloadFile`, `FileTransferServiceImpl::GetFileInfo`, `FileTransferClient::GetFileInfo`, and `FileTransferClient::DownloadFile`.

## Control Flow
The service `DownloadFile` opens the requested file at end to determine size, chooses request chunk size or a default, seeks to `first_chunk_index * chunk_size`, then streams `DownloadChunk` messages with offsets and data until EOF. It can randomly fail or flip a byte for testing. `GetFileInfo` returns requested size and/or CRC. The client first fetches expected size and optional CRC, starts the streaming RPC, writes chunks sequentially to the output file, rejects offset gaps/reordering, verifies byte count and CRC, checks final gRPC status, and deletes the output file on failure.

## State and Persistence Behavior
Server state is the `error_inject_` enum and local filesystem contents. Client persistence is the output file, which is truncated on open and removed on failed transfer when `delete_on_close_` is true. No resume metadata is persisted.

## Dependencies and Integration Points
It depends on generated `file_transfer` protobuf/gRPC stubs, gRPC C++ APIs, CRC32C, deterministic randomness, C++ streams, and `FileTransfer.h`. It is built only in gRPC-enabled fdbrpc builds.

## Risks and Edge Cases
The server error text for missing file in `DownloadFile` says "File found not". `DownloadFile` ignores `ServerContext` cancellation. `expected_size` is stored as `uint32_t` even though protobuf file size may exceed 4 GiB. Client download does not set chunk size or resume index, so resume support is absent despite proto fields. CRC verification opens the output file without explicit binary mode. The service trusts requested file paths without path policy.

## Test Signals
`FlowGrpcTests.cpp` includes file transfer success for a 40 MiB file, byte-flip detection through CRC mismatch, and random internal failure handling.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbrpc/FileTransfer.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbrpc/FileTransfer.h -->
# sources/storage-engines/foundationdb/fdbrpc/FileTransfer.h

## Purpose
`FileTransfer.h` declares the gRPC file-transfer service implementation and client wrapper for fdbrpc.

## Important APIs, Types, and Functions
`FileTransferServiceImpl` derives from `fdbrpc::FileTransferService::Service` and declares `DownloadFile`, `GetFileInfo`, test `ErrorInjection` modes, and `SetErrorInjection`. `FileTransferClient` owns a generated stub and declares `GetFileInfo` and `DownloadFile`.

## Control Flow
The header does not implement control flow, but it defines unary metadata lookup and server-streamed download as the service surface. The client API wraps these RPCs into optional-returning C++ calls.

## State and Persistence Behavior
The service stores only the selected error-injection mode. The client stores a stub and a constant policy to delete failed output files.

## Dependencies and Integration Points
It is compiled only under `FLOW_GRPC_ENABLED`, includes gRPC headers, and uses generated `file_transfer.pb.h` and `file_transfer.grpc.pb.h`. It integrates with the fdbrpc CMake gRPC/protobuf generation path and gRPC tests.

## Risks and Edge Cases
The API exposes raw filenames to remote callers, leaving access control/path restrictions to deployment context. Return values collapse all client errors to `std::nullopt`, making failure diagnosis coarse. Resume is not part of the public client API even though download requests support a first chunk index.

## Test Signals
The declarations are exercised by `FlowGrpcTests.cpp` file-transfer tests when gRPC support is enabled.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbrpc/FileTransfer.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbrpc/FlowGrpc.cpp -->
# sources/storage-engines/foundationdb/fdbrpc/FlowGrpc.cpp

## Purpose
`FlowGrpc.cpp` implements fdbrpc's optional gRPC runtime initialization and `GrpcServer` lifecycle management.

## Important APIs, Types, and Functions
Important functions include `FlowGrpc::init`, `GrpcServer` constructor/destructor, `GrpcServer::run`, `runInternal`, `shutdown`, `stopServer`, `stopServerSync`, `stopServerSyncInternal`, `registerService`, `registerRoleServices`, `deregisterRoleServices`, and `deregisterRoleServicesSync`.

## Control Flow
`FlowGrpc::init` installs a global `FlowGrpc` state object, chooses insecure or TLS credential provider, and optionally creates a server. `GrpcServer::run` awaits `runInternal` and shuts down unless already shutdown. `runInternal` waits until services are registered, stops any existing server, builds a new `grpc::ServerBuilder`, registers all service instances, starts the server, increments start count, triggers start waiters, and then waits for service-list changes to restart. Deregistration stops the current server, removes services by owner UID, and triggers a rebuild.

## State and Persistence Behavior
Runtime state includes global `FlowGrpc`, credential provider, optional server, registered service map keyed by owner `UID`, server pointer, lifecycle state enum, start count, trigger variables, an async task executor pool, and the server actor future. No application data is persisted.

## Dependencies and Integration Points
It depends on `fdbrpc/FlowGrpc.h`, Flow errors/tracing/network globals, gRPC server builder, credential providers, `AsyncTaskExecutor`, and TLS config. It integrates gRPC services into Flow's actor lifecycle and network-global storage.

## Risks and Edge Cases
`stopServerSyncInternal` appears to have an inverted null check: it returns when `server_ != nullptr` and otherwise dereferences `server_`, which would prevent shutdown of a live server and crash on null if reached. `deregisterRoleServicesSync` calls the internal stop function directly, so it inherits that risk. Service registration with `registerService` uses a fresh random UID that cannot be deregistered by caller. Restarting the entire gRPC server for service changes can interrupt in-flight RPCs.

## Test Signals
`FlowGrpcTests.actor.cpp` and `FlowGrpcTests.cpp` test basic server/client RPCs, stream reads, no-server failure, destructor cleanup, lifecycle restart behavior, and TLS credential behavior under `FLOW_GRPC_ENABLED`.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbrpc/FlowGrpc.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbrpc/FlowGrpcTests.actor.cpp -->
# sources/storage-engines/foundationdb/fdbrpc/FlowGrpcTests.actor.cpp

## Purpose
`FlowGrpcTests.actor.cpp` contains actor-compiler style unit tests for the optional gRPC wrapper using synchronous wait syntax.

## Important APIs, Types, and Functions
It defines `forceLinkGrpcTests` and test cases `/fdbrpc/grpc/basic_sync_client`, `/fdbrpc/grpc/basic_async_client`, `/fdbrpc/grpc/actor_basic_stream_server`, `/fdbrpc/grpc/no_server_running`, and `/fdbrpc/grpc/destroy_server_without_shutdown`. It uses `GrpcServer`, `TestEchoServiceImpl`, `EchoClient`, `AsyncGrpcClient`, `AsyncTaskExecutor`, and generated echo service stubs.

## Control Flow
Tests start a `GrpcServer` on fixed localhost ports, register echo services, run the server actor, wait for `onRunning`, and issue sync or async RPCs. Streaming tests consume responses until `end_of_stream`. The no-server test verifies async RPC failure. The destroy-without-shutdown test leaves scope after starting a server to exercise destructor cleanup.

## State and Persistence Behavior
State is transient network listener state on localhost ports and in-memory service/client objects. No data is persisted.

## Dependencies and Integration Points
The file is compiled only under `FLOW_GRPC_ENABLED`, includes actor compiler support, Flow unit tests, `FlowGrpc.h`, and `FlowGrpcTests.h`. It validates integration between Flow actors/futures and gRPC client/server wrappers.

## Risks and Edge Cases
Fixed ports can collide with local processes or parallel test runs. Tests do not always explicitly shut down the server actor after success, relying on object lifetime or cancellation behavior. The actor stream test treats `end_of_stream` as the normal completion path.

## Test Signals
Passing tests show basic unary RPC, async client dispatch, server-stream consumption, expected failure with no listener, and server destructor cleanup work in actor syntax.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbrpc/FlowGrpcTests.actor.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbrpc/FlowGrpcTests.cpp -->
# sources/storage-engines/foundationdb/fdbrpc/FlowGrpcTests.cpp

## Purpose
`FlowGrpcTests.cpp` provides coroutine-style tests for gRPC clients/servers, file transfer, async task execution, server lifecycle restarts, and TLS/mTLS credentials.

## Important APIs, Types, and Functions
Helpers include `generate_random_string`, `WriteTestFile`, and `GPRC_FILE_TRANSFER_TEST_FILE_SIZE`. Test cases cover `/fdbrpc/grpc/basic_coro`, `/basic_stream_server`, `/future_destroy`, `/stream_destroy`, `/file_transfer`, `/file_transfer_byte_flip`, `/file_transfer_fail_random`, `/basic_thread_pool`, `/server_lifecycle_basic`, `/server_lifecycle_combine_register_into_one_start`, and `/basic_tls`.

## Control Flow
The basic tests start a `GrpcServer`, register echo services, create `AsyncGrpcClient`, and await unary or streaming responses. Lifetime tests drop futures or streams early. File-transfer tests create temporary source/destination files, start a raw gRPC server with `FileTransferServiceImpl`, run downloads, and assert success or expected failure under byte-flip/random-failure injection. Thread-pool tests post void and value-returning lambdas and verify errors propagate. Lifecycle tests register/deregister services and observe server restart counts. TLS tests create static credential providers and verify insecure, correct, incorrect, and different-root client behaviors.

## State and Persistence Behavior
State is transient: localhost server sockets, temporary files, generated random file contents, test TLS certificate strings, service registry state, and thread-pool work queues. Temporary files are destroyed in file-transfer tests after assertions.

## Dependencies and Integration Points
The file depends on `FlowGrpc.h`, `FlowGrpcTests.h`, `FileTransfer.h`, Flow unit tests, TLS config, deterministic randomness, gRPC C++ APIs, and platform temp files. It is active only with `FLOW_GRPC_ENABLED`.

## Risks and Edge Cases
Fixed localhost ports can conflict. File-transfer tests use large 40 MiB temp files and comments mention 1 GiB despite the constant, which can confuse diagnostics. TLS certificates are embedded static material with long validity and are not regenerated. Some server actors are not explicitly awaited for shutdown. The tests may expose the `stopServerSyncInternal` shutdown bug if destructor/sync paths are exercised strictly.

## Test Signals
These tests are the strongest signals for fdbrpc gRPC: unary calls, streaming end-of-stream, future/stream destruction, file integrity checks, failure cleanup, thread-pool error forwarding, service restart behavior, and TLS credential enforcement.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbrpc/FlowGrpcTests.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbrpc/FlowGrpcTests.h -->
# sources/storage-engines/foundationdb/fdbrpc/FlowGrpcTests.h

## Purpose
`FlowGrpcTests.h` defines the generated echo service test implementation and a small synchronous echo client used by gRPC unit tests.

## Important APIs, Types, and Functions
`TestEchoServiceImpl` implements `Echo`, `EchoRecvStream10`, and `EchoSendStream10` on `fdbrpc::test::TestEchoService::Service`. `EchoClient` wraps a generated stub and exposes `Echo`. The header aliases common gRPC and std types into `fdbrpc_test`.

## Control Flow
Unary `Echo` prefixes request messages with `"Echo: "`. Server-streaming `EchoRecvStream10` writes ten identical responses unless the context is cancelled. Client-streaming `EchoSendStream10` reads ten requests, concatenates messages, asserts count ten, and returns the concatenation. `EchoClient::Echo` performs a blocking unary RPC and returns either the response message or `"RPC failed"`.

## State and Persistence Behavior
The service is stateless beyond per-RPC locals. The client stores a generated stub. No data is persisted.

## Dependencies and Integration Points
The header is compiled only under `FLOW_GRPC_ENABLED` and depends on generated `fdbrpc/test/echo.grpc.pb.h`, gRPC C++ APIs, Flow errors/asserts, and test code in both gRPC test translation units.

## Risks and Edge Cases
Service methods use fixed counts and assertions, so malformed client-stream tests abort rather than return gRPC errors. `EchoClient` collapses all failures into a string, limiting diagnostics. `EchoRecvStream10` writes in a tight loop and only checks cancellation before each write.

## Test Signals
All gRPC test files use these helpers; passing tests validate generated stubs, service registration, unary RPCs, server streaming, and basic failure handling.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbrpc/FlowGrpcTests.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbrpc/FlowTests.actor.cpp -->
# sources/storage-engines/foundationdb/fdbrpc/FlowTests.actor.cpp

## Purpose
`FlowTests.actor.cpp` is a broad unit/performance test suite for Flow actor compiler behavior, futures, promises, streams, cancellation, yielded futures, async maps, deterministic randomness, mutexes, thread-return streams, and fdbrpc `waitValueOrSignal` disconnect/retry behavior.

## Important APIs, Types, and Functions
The file defines many small actor helpers (`emptyActor`, `oneWaitActor`, `chooseTwoActor`, `sumActor`, `testCancelled`, `waitAfterCancel`, `mutexTest`, etc.), callback helper templates (`LambdaCallback`, `onReady` overloads), `YieldMockNetwork`, `YAMRandom`, serializable test type `flow_tests_details::Int`, `Tracker`, and numerous `TEST_CASE`s under `/flow`, `/fdbrpc`, and `/flow/thread`.

## Control Flow
Early tests validate actor line-number preservation, buggified delay ordering, future/promise/stream readiness and callbacks, cancellation propagation, simple actor return/wait/choose behavior, quorum, and networked serialization of request streams. Yielded-future tests replace `g_network` with `YieldMockNetwork` and verify readiness throttling. Performance tests create one million actors/futures under several patterns. AsyncMap/YieldedAsyncMap tests run randomized operations and basic/cancel cases. Later tests cover actor compiler class-context parsing, deterministic random signed bounds, PromiseStream move/copy behavior, randomized `FlowMutex` locking with injected errors, `ThreadReturnPromiseStream` sequencing/error/destruction behavior, and `waitValueOrSignal` peer-disconnect retry cases.

## State and Persistence Behavior
The tests mutate only process-local test state, Flow futures/promises, mock network globals, local peer objects, and thread-pool queues. `YieldMockNetwork` temporarily replaces `g_network` and restores it in the destructor. No durable external state is written.

## Dependencies and Integration Points
It depends on Flow actor compiler, Arena, Error, ProtocolVersion, UnitTest, DeterministicRandom, thread pools, WriteOnlySet, fdbrpc transport primitives, TLS config, `AsyncTaskExecutor`, and `Peer`/`waitValueOrSignal` behavior. It is a central regression suite for Flow primitives used throughout FoundationDB.

## Risks and Edge Cases
Several performance tests are intentionally heavy. Randomized tests depend on deterministic randomness but still cover a bounded subset of interleavings. `YieldMockNetwork` delegates most methods manually, so additions to `INetwork` may require updates. Some tests intentionally inspect moved-from objects or broken promises. Fixed assumptions about error codes (`request_maybe_delivered`, `broken_promise`, `end_of_stream`) encode important fdbrpc retry semantics and can fail if error mapping changes.

## Test Signals
Passing this file is a strong signal that actor compiler transformations, callback lifetimes, cancellation, PromiseStream move semantics, FlowMutex error propagation, thread-to-Flow stream delivery, and peer-disconnect retry handling behave correctly. The final `waitValueOrSignal` tests specifically guard against hangs when a peer disconnects before failure monitor signals fire.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbrpc/FlowTests.actor.cpp -->
