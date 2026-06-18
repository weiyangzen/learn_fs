# subset-b-000180 research

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/internal/stdcopymux/writer.go -->
# sources/cloud-native/moby/daemon/internal/stdcopymux/writer.go

## Purpose
Implements Docker's stdout/stderr multiplexing writer format for daemon stream output. `NewStdWriter` wraps a shared `io.Writer` and prefixes every payload with the 8-byte stdcopy header so the receiver can demultiplex frames by stream type.

## Important APIs, Types, And Functions
`stdWriter` embeds `io.Writer` and stores a stream prefix byte derived from `stdcopy.StdType`. `Write` validates the wrapped writer, builds the header with stream id at byte 0 and payload size at bytes 4-7 in big-endian order, appends the payload, and writes a single framed buffer. `bufPool` reuses `bytes.Buffer` instances to reduce allocations.

## Control Flow
Each write is transformed into `header + payload`, sent once to the underlying writer, then translated back to the number of payload bytes by subtracting the header length. Negative adjusted counts are clamped to zero. A nil payload is a no-op.

## State And Persistence
There is no persistent state beyond the pooled temporary buffers. Correctness assumes stdout, stderr, and system-error wrappers share the same underlying writer so frame order is preserved by the caller.

## Dependencies And Integration Points
Integrates with `api/pkg/stdcopy` framing constants and consumers such as attach/log streaming. The wire format is compatibility-sensitive.

## Risks And Test Signals
Partial writes can report adjusted payload counts that do not distinguish header-only progress from payload progress. Concurrent calls rely on the underlying writer's safety; this wrapper adds no locking. No tests are listed in this subset for this package, so coverage is indirect through stdcopy and attach behavior.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/internal/stdcopymux/writer.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/internal/stream/attach.go -->
# sources/cloud-native/moby/daemon/internal/stream/attach.go

## Purpose
Connects client attach streams to a container stream `Config`, including stdin forwarding, stdout/stderr forwarding, close propagation, detach-key handling for TTY input, and cancellation cleanup.

## Important APIs, Types, And Functions
`AttachConfig` carries requested stream flags, container-side pipes, client-side streams, TTY/detach settings, and stdin close policy. `Config.AttachStreams` populates container pipes according to requested streams. `Config.CopyStreams` starts an `errgroup` of copy goroutines and returns a single error channel. `copyEscapable` wraps TTY input with `term.NewEscapeProxy` and uses the default ctrl-p ctrl-q detach sequence when no keys are supplied.

## Control Flow
For stdin, a goroutine copies client input into `CStdin`; when it exits it either closes container stdin for non-TTY `CloseStdin`, or closes output pipes to unblock readers. Separate goroutines copy `CStdout` and `CStderr` to the client and close client stdin plus their pipe when done. A supervisor goroutine races group completion against context cancellation; on cancel it closes all container pipes and client stdin so blocked `io.Copy` calls can unwind.

## State And Persistence
State is transient stream lifecycle state. The function mutates and closes caller-provided pipe handles but persists no daemon metadata.

## Dependencies And Integration Points
Uses `pools.Copy`, containerd logging, `pkg/errors`, `errgroup`, and `moby/term`. It is called by daemon attach/exec APIs after `AttachStreams` wires stream `Config` broadcasters.

## Risks And Test Signals
The main risk is goroutine leaks from blocked reads when containers exit without I/O. `io.ErrClosedPipe` is normalized to success. `attach_test.go` exercises no-I/O combinations and expects cancellation to return `context.Canceled` within 10 seconds.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/internal/stream/attach.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/internal/stream/attach_test.go -->
# sources/cloud-native/moby/daemon/internal/stream/attach_test.go

## Purpose
Regression-tests attach stream cancellation for stream combinations that have no active I/O. The goal is to ensure `CopyStreams` closes enough pipes for all goroutines to exit when the container context is canceled.

## Important APIs, Types, And Functions
`TestAttachNoIO` runs subtests for stdin only, stdout only, stderr only, stdout+stderr, stdin+stdout, stdin+stderr, and all three streams. `testStreamCopy` builds an `AttachConfig`, calls `NewConfig`, `AttachStreams`, `CopyStreams`, cancels the context, and waits for the returned error.

## Control Flow
Each subtest creates `io.Pipe` endpoints but does not write data. `testStreamCopy` first verifies that `CopyStreams` does not immediately report an unexpected error, then cancels the context and waits for either `context.Canceled` or a 10-second timeout.

## State And Persistence
All pipes and stream configs are in-memory and closed via defers. No external state is touched.

## Dependencies And Integration Points
Uses the same public attach APIs that daemon attach code uses. Assertions come from `gotest.tools/v3/assert`.

## Risks And Test Signals
This test does not validate byte transfer, detach keys, close-stdin semantics, or error propagation. Its strong signal is leak prevention: cancellation must unblock `io.Copy` across every requested stream shape.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/internal/stream/attach_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/internal/stream/bytespipe/buffer.go -->
# sources/cloud-native/moby/daemon/internal/stream/bytespipe/buffer.go

## Purpose
Provides the fixed-size buffer primitive used by `BytesPipe`. It stores one run of bytes in a preallocated slice capacity and tracks unread data without reallocating.

## Important APIs, Types, And Functions
`fixedBuffer` contains `buf`, write position `pos`, and read position `lastRead`. `Write` copies into `buf[pos:cap(buf)]` and returns `errBufferFull` when the capacity is exhausted. `Read` copies unread bytes to the caller and advances `lastRead`. `Len`, `Cap`, `Reset`, and `String` expose unread length, capacity, reset-for-pool behavior, and unread content.

## Control Flow
Writes grow only the logical positions, not the slice length. Reads consume bytes monotonically. `Reset` clears positions and shortens the slice to length zero so pooled buffers can be reused cleanly.

## State And Persistence
The object is mutable and intentionally not synchronized; `BytesPipe` owns synchronization. No persistence exists.

## Dependencies And Integration Points
Used by `bytespipe.go` as the RLE-like chunk storage unit behind a blocking pipe. The sentinel `errBufferFull` is an expected internal control-flow result.

## Risks And Test Signals
The implementation never compacts read space for later writes; once capacity is consumed the buffer is full even if earlier bytes were read. Tests validate capacity, unread length, stringing unread data, full-buffer errors, and sequential reads.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/internal/stream/bytespipe/buffer.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/internal/stream/bytespipe/buffer_test.go -->
# sources/cloud-native/moby/daemon/internal/stream/bytespipe/buffer_test.go

## Purpose
Unit-tests `fixedBuffer`, the low-level storage block used by `BytesPipe`, with attention to capacity, unread length, short writes, reset behavior, and read offsets.

## Important APIs, Types, And Functions
Tests cover `Cap`, `Len`, `String`, `Write`, `Read`, and the `errBufferFull` sentinel. They construct buffers with explicit capacities and use byte slices and strings to verify exact contents.

## Control Flow
The suite writes small strings, reads partial data, attempts writes after capacity is exhausted, resets the buffer, and reads across multiple calls. The `TestFixedBufferWrite` case confirms that a second oversized write copies only the remaining capacity and returns `errBufferFull`.

## State And Persistence
Only in-memory buffers are used. Tests inspect internal fields such as `buf.buf[:5]`, so they are tightly coupled to representation.

## Dependencies And Integration Points
Uses Go's standard testing package plus `bytes` and `errors`. These tests protect `BytesPipe` assumptions about one-way consumption and full-buffer signaling.

## Risks And Test Signals
Tests do not exercise concurrency because `fixedBuffer` is intentionally unsynchronized. The strongest signals are preserving unread-only `String`, not reusing consumed capacity before `Reset`, and returning the exact number of bytes copied before capacity exhaustion.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/internal/stream/bytespipe/buffer_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/internal/stream/bytespipe/bytespipe.go -->
# sources/cloud-native/moby/daemon/internal/stream/bytespipe/bytespipe.go

## Purpose
Implements a blocking in-memory `io.ReadWriteCloser` for daemon stream fan-out. It buffers bytes in pooled fixed buffers, supports backpressure, and allows readers to drain data once.

## Important APIs, Types, And Functions
`BytesPipe` has a mutex, condition variable, buffer list, buffered byte count, close error, and read-block flag. `New` initializes a minimum-capacity buffer. `Write` appends across fixed buffers, doubles buffer capacity up to `maxCap`, and blocks while buffered data is at or above `blockThreshold`. `Read` waits for data or close, drains buffers, returns buffers to pools, and wakes writers. `CloseWithError` and `Close` set the terminal read error.

## Control Flow
Writers loop until all input is copied or close/error occurs. When allocation would happen with too much buffered data, the writer waits and wakes a blocked reader if present. Readers wait only while empty and open, then copy as much as the caller buffer can hold and return emptied fixed buffers to capacity-keyed pools.

## State And Persistence
State is in memory. Buffer pools persist process-wide by capacity and may retain allocations after peak stream load. Closed pipes return `ErrClosed` to writers and the configured close error to readers.

## Dependencies And Integration Points
Used by `stream.Config.StdoutPipe` and `StderrPipe` as per-consumer pipes behind unbuffered broadcasters. It integrates with `io.Copy` paths in attach and container I/O.

## Risks And Test Signals
Backpressure and condition-variable ordering are deadlock-sensitive. `readBlock` is used only as a wake-up hint. Tests cover sequential reads/writes, a deadlock regression around `blockThreshold`, random chunk checksums, and benchmarks for allocation/performance.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/internal/stream/bytespipe/bytespipe.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/internal/stream/bytespipe/bytespipe_test.go -->
# sources/cloud-native/moby/daemon/internal/stream/bytespipe/bytespipe_test.go

## Purpose
Validates `BytesPipe` read/write ordering, buffer growth behavior, deadlock avoidance, data integrity under mismatched chunk sizes, and rough performance characteristics.

## Important APIs, Types, And Functions
Tests exercise `New`, `Write`, `Read`, and `Close`. `TestBytesPipeDeadlock` constructs a near-threshold buffer and runs read/write goroutines under a timer. `TestBytesPipeWriteRandomChunks` compares SHA-256 hashes of expected and pipe-read bytes. Benchmarks cover repeated write and read workloads.

## Control Flow
Simple tests write numeric chunks and read fixed-size buffers. The deadlock test starts a reader, then writes `blockThreshold+1` bytes and requires both goroutines to finish within one second. Random chunk tests interleave variable write/read sizes and close the pipe to terminate the reader.

## State And Persistence
All state is in-memory. Tests inspect internal `buf` fields in one case to confirm direct concatenation for small writes.

## Dependencies And Integration Points
Uses crypto hashing, random delays, timers, and Go benchmarks. These tests protect stream attach and log-following consumers from blocked pipe behavior.

## Risks And Test Signals
Random tests use nondeterministic sleeps, so failures may be timing-sensitive. The strongest signal is that large writes unblock when a waiting reader drains a byte and that hash equality survives arbitrary chunk boundaries.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/internal/stream/bytespipe/bytespipe_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/internal/stream/streams.go -->
# sources/cloud-native/moby/daemon/internal/stream/streams.go

## Purpose
Defines the daemon stream `Config` abstraction that groups stdin, stdout, stderr, and containerd `DirectIO` copying for container processes.

## Important APIs, Types, And Functions
`Config` owns unbuffered stdout/stderr broadcasters, stdin pipe ends, a `cio.DirectIO`, a wait group, and a closed flag. `NewConfig`, `Stdout`, `Stderr`, `Stdin`, `StdinPipe`, `StdoutPipe`, and `StderrPipe` expose stream endpoints. `NewInputPipes` creates an `io.Pipe`; `NewNopInputPipe` discards input. `CloseStreams`, `CopyToPipe`, and `Wait` manage shutdown and DirectIO copying.

## Control Flow
Output pipes create a `bytespipe.BytesPipe` and add it to the broadcaster. `CopyToPipe` starts goroutines from containerd stdout/stderr into broadcasters and stdin into containerd stdin. Errors after `CloseStreams` are suppressed; other copy/close failures are logged. `Wait` waits for output copy goroutines or cancels/closes DirectIO on context timeout.

## State And Persistence
Stream state is in memory. `closed` gates logging after teardown. The object mutates pipe fields and DirectIO references but does not checkpoint daemon state.

## Dependencies And Integration Points
Integrates containerd `cio.DirectIO`, `bytespipe`, `unbuffered`, and `pools.Copy`. It is the substrate used by attach and container runtime wiring.

## Risks And Test Signals
Blocking stdout/stderr consumers can stall broadcaster writes. Stdin copy is started with a raw goroutine rather than the wait group, so `Wait` mainly tracks output streams. Tests in this subset validate attach cancellation and broadcaster behavior indirectly.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/internal/stream/streams.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/internal/stream/unbuffered.go -->
# sources/cloud-native/moby/daemon/internal/stream/unbuffered.go

## Purpose
Implements a simple synchronized broadcaster for stdout and stderr. Each write is delivered to all registered `io.WriteCloser` consumers, and failed consumers are removed.

## Important APIs, Types, And Functions
`unbuffered` holds a mutex and slice of writers. `Add` appends a consumer. `Write` locks, writes the full byte slice to each writer, records writers that returned an error or short count, evicts them, and reports success for the original length. `Clean` closes all writers and clears the slice.

## Control Flow
Writes are synchronous under a single lock, so every active writer receives data serially. Eviction is deferred until after the loop and index-adjusted while removing multiple failed writers.

## State And Persistence
The writer list is in-memory. Failed or closed consumers disappear on the next write; `Clean` closes all current writers. No stream content is retained.

## Dependencies And Integration Points
Used by `stream.Config.Stdout` and `Stderr` to fan container output into all active attach/log consumers. Consumers are commonly `bytespipe.BytesPipe` instances.

## Risks And Test Signals
One slow writer blocks all writers and future `Add` calls while `Write` holds the lock. Write errors are swallowed after eviction, which favors continued fan-out over surfacing partial delivery. Tests cover multi-writer delivery, eviction, race behavior, and benchmark fan-out.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/internal/stream/unbuffered.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/internal/stream/unbuffered_test.go -->
# sources/cloud-native/moby/daemon/internal/stream/unbuffered_test.go

## Purpose
Tests the unbuffered broadcaster's delivery, failed-writer eviction, concurrent add/write safety, and benchmark fan-out cost.

## Important APIs, Types, And Functions
`dummyWriter` records writes and can fail on demand. `devNullCloser` accepts all bytes. `TestUnbuffered` exercises `Add`, `Write`, and `Clean`. `TestRaceUnbuffered` is specifically valuable under the race detector. `BenchmarkUnbuffered` measures repeated writes to hundreds of consumers.

## Control Flow
The main test adds writers, writes `"foo"` and `"bar"`, adds another writer midstream, forces failures, verifies failed writers stop receiving data, and checks multiple simultaneous evictions. Cleanup closes the broadcaster.

## State And Persistence
All writer state is local buffers. There is no external persistence.

## Dependencies And Integration Points
Uses standard testing and in-memory writer fakes. It protects the stream package's stdout/stderr broadcaster used by attach and DirectIO copying.

## Risks And Test Signals
The race test only detects issues when run with `-race`. The tests do not check close errors from `Clean`, matching production behavior where close errors are ignored. Strong signal is correct index handling when several writers are evicted in one pass.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/internal/stream/unbuffered_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/internal/streamformatter/streamformatter.go -->
# sources/cloud-native/moby/daemon/internal/streamformatter/streamformatter.go

## Purpose
Formats daemon progress, status, error, and aux messages as Docker JSON stream records with CRLF framing.

## Important APIs, Types, And Functions
`FormatStatus` builds `jsonstream.Message{ID, Status}`. `FormatError` wraps ordinary errors or existing `jsonstream.Error` values and uses `compat.Wrap` to include both `error` and `errorDetail`. `jsonProgressFormatter.formatProgress` serializes progress and optional aux JSON. `NewJSONProgressOutput` returns a `progress.Output`. `progressOutput.WriteProgress` serializes updates under a mutex and optionally emits a final blank status. `AuxFormatter.Emit` writes aux messages and checks short writes.

## Control Flow
Progress messages with `Message` become status lines; otherwise fields are copied to `jsonstream.Progress` and serialized with action, id, and aux. Every successful message is terminated with `\r\n`.

## State And Persistence
State is limited to the output writer and a mutex protecting interleaved writes. No durable state is stored.

## Dependencies And Integration Points
Used by pull/build/push style daemon APIs that stream JSON to clients. Depends on `api/types/jsonstream`, daemon `progress`, and compatibility wrapping for legacy fields.

## Risks And Test Signals
Aux marshal failures in progress formatting return nil formatted bytes, which may become empty writes. Client compatibility depends on exact field names and CRLF framing. Tests cover status, error, JSON error, progress aux decoding, output construction, and aux emission.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/internal/streamformatter/streamformatter.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/internal/streamformatter/streamformatter_test.go -->
# sources/cloud-native/moby/daemon/internal/streamformatter/streamformatter_test.go

## Purpose
Verifies JSON stream formatter output for status, errors, progress, output initialization, and aux messages.

## Important APIs, Types, And Functions
Tests call `FormatStatus`, `FormatError`, `jsonProgressFormatter.formatProgress`, `jsonProgressFormatter.formatStatus`, `NewJSONProgressOutput`, and `AuxFormatter.Emit`. `cmpJSONMessageOpt` ignores the derived deprecated `ProgressMessage` field when comparing decoded messages.

## Control Flow
Tests compare exact JSON strings for status/errors and decode progress JSON into `jsonstream.Message` to compare structured fields, including raw aux JSON.

## State And Persistence
All state is an in-memory `bytes.Buffer`. No external files or daemon state are involved.

## Dependencies And Integration Points
Uses `google/go-cmp`, `gotest.tools`, and `jsonstream` types. These tests protect client-facing JSON wire compatibility.

## Risks And Test Signals
Exact string checks are sensitive to JSON field ordering, but Go's marshal order for struct fields is stable. Tests do not cover concurrent `WriteProgress` locking or short-write behavior. Strong signal is preserved CRLF framing and legacy `error` plus `errorDetail` fields.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/internal/streamformatter/streamformatter_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/internal/streamformatter/streamwriter.go -->
# sources/cloud-native/moby/daemon/internal/streamformatter/streamwriter.go

## Purpose
Provides stdout and stderr writers that transform raw byte chunks into JSON stream messages for Docker API clients.

## Important APIs, Types, And Functions
`streamWriter` wraps an `io.Writer` and a `lineFormat` function. `Write` formats the input into a `jsonstream.Message{Stream: ...}`, writes the formatted bytes, returns `io.ErrShortWrite` on partial formatted writes, and reports the original input length on success. `NewStdoutWriter` passes content through; `NewStderrWriter` wraps content in red ANSI color escape sequences.

## Control Flow
Each write becomes one JSON message terminated by CRLF. There is no line splitting; the caller's byte chunk is the stream payload.

## State And Persistence
No persistent state. The only mutable state belongs to the wrapped writer.

## Dependencies And Integration Points
Used by daemon code that needs to expose stdout/stderr as JSON stream messages, especially non-multiplexed HTTP responses. Relies on `jsonstream.Message` and `FormatError`.

## Risks And Test Signals
Short writes return the formatted byte count rather than input bytes, which differs from the success path. Stderr coloring is embedded in JSON and assumes terminal-compatible clients. Tests verify exact stdout/stderr JSON.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/internal/streamformatter/streamwriter.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/internal/streamformatter/streamwriter_test.go -->
# sources/cloud-native/moby/daemon/internal/streamformatter/streamwriter_test.go

## Purpose
Tests `NewStdoutWriter` and `NewStderrWriter` JSON formatting and returned write sizes.

## Important APIs, Types, And Functions
`TestStreamWriterStdout` and `TestStreamWriterStderr` write `"content"` into a `bytes.Buffer`, assert no error, assert the returned size equals the original content length, and compare exact JSON output with `streamNewline`.

## Control Flow
Each test creates a writer, performs one write, then inspects the resulting buffer string.

## State And Persistence
State is only an in-memory buffer.

## Dependencies And Integration Points
Uses `gotest.tools` assertions. These tests protect the client-visible JSON stream format and stderr color escape sequence encoding.

## Risks And Test Signals
Short-write/error behavior is not covered. The exact JSON expectations make field names, escaping of ANSI sequences, and CRLF framing explicit compatibility signals.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/internal/streamformatter/streamwriter_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/internal/stringid/stringid.go -->
# sources/cloud-native/moby/daemon/internal/stringid/stringid.go

## Purpose
Provides helpers for Docker-style hexadecimal IDs: generating random full IDs and presenting short prefixes.

## Important APIs, Types, And Functions
`TruncateID` removes any algorithm prefix before `:` and returns at most 12 characters. `GenerateRandomID` reads 32 random bytes, hex-encodes them into a 64-character ID, and retries if the first 12 characters are numeric-only. `allNum` checks whether a byte string contains only ASCII digits.

## Control Flow
Random ID generation loops until the shortened hostname-safe prefix contains at least one non-digit. `rand.Read` errors panic because cryptographic randomness is expected to be available.

## State And Persistence
No state is stored. Generated IDs are returned to callers for persistence elsewhere.

## Dependencies And Integration Points
Used throughout daemon object creation and display. The numeric-prefix guard exists because truncated container IDs can become default hostnames, and all-numeric hostnames are problematic.

## Risks And Test Signals
The short length is fixed at 12 but documented as not a stable external contract. `TruncateID` does not validate hex content or uniqueness. Tests cover length, digest-prefix truncation, invalid short input, and numeric-only detection.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/internal/stringid/stringid.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/internal/stringid/stringid_test.go -->
# sources/cloud-native/moby/daemon/internal/stringid/stringid_test.go

## Purpose
Tests ID generation length, truncation behavior, digest-prefix handling, and numeric-only prefix detection.

## Important APIs, Types, And Functions
`TestGenerateRandomID` checks that `GenerateRandomID` returns `fullLen` characters. `TestTruncateID` covers empty strings, invalid short IDs, full IDs, `sha256:` digest strings, and very long strings. `TestAllNum` verifies mixed, alphabetic, and numeric-only inputs.

## Control Flow
All tests are table-driven except the random ID length check. Subtests name each truncation and numeric case.

## State And Persistence
No external state. Randomness is consumed from `crypto/rand`.

## Dependencies And Integration Points
Standard testing only. The tests support daemon assumptions that short IDs are display prefixes and that generated IDs are 64 hex characters.

## Risks And Test Signals
The random generation test does not assert non-numeric truncated prefixes even though production guarantees it. Collision behavior is out of scope. The important signal is backward-compatible truncation of digest strings by stripping the algorithm before shortening.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/internal/stringid/stringid_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/internal/system/chtimes.go -->
# sources/cloud-native/moby/daemon/internal/system/chtimes.go

## Purpose
Wraps `os.Chtimes` with platform-safe bounds checking and platform-specific creation-time handling.

## Important APIs, Types, And Functions
Package globals `unixEpochTime` and `unixMaxTime` are initialized according to the size of `syscall.Timespec.Nsec`. `Chtimes` clamps access and modification times before the Unix epoch or beyond the platform maximum back to the epoch, calls `os.Chtimes`, then delegates to `setCTime`.

## Control Flow
Initialization detects 64-bit versus 32-bit timespec limits. At runtime each timestamp is validated independently before the filesystem call. `setCTime` is a no-op on Unix and a Windows file-time operation on Windows.

## State And Persistence
The function mutates filesystem timestamps for the named path. The only package state is immutable time bounds after init.

## Dependencies And Integration Points
Used by archive extraction/copy paths that need safe timestamp restoration across platforms. Integrates with build-tagged `setCTime` implementations.

## Risks And Test Signals
Clamping invalid high times to epoch may surprise callers expecting best-effort maximum values, but avoids undefined `os.Chtimes` behavior. Tests cover mtime and platform-specific atime/ctime behavior around epoch, valid post-epoch, and max time.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/internal/system/chtimes.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/internal/system/chtimes_linux_test.go -->
# sources/cloud-native/moby/daemon/internal/system/chtimes_linux_test.go

## Purpose
Linux-specific atime tests for `Chtimes`, complementing cross-platform mtime tests.

## Important APIs, Types, And Functions
`TestChtimesATime` creates a temp file, calls `Chtimes` with epoch, pre-epoch, post-epoch, and max-time combinations, then reads `syscall.Stat_t.Atim`.

## Control Flow
Each subtest updates the same temp file and verifies atime. Pre-epoch atime or mtime inputs are expected to clamp to `unixEpochTime`. Max-time comparisons truncate to seconds to tolerate filesystem precision differences.

## State And Persistence
Mutates a temporary file's timestamps only. The temp directory is test-managed.

## Dependencies And Integration Points
Linux build only. Uses `os.Stat` and syscall stat fields, so it verifies actual kernel/file-system behavior rather than mocks.

## Risks And Test Signals
Atime behavior can be filesystem or mount-option sensitive, but explicit `Chtimes` updates should be visible. The strongest signal is that sytem timestamp clamping applies to atime as well as mtime on Linux.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/internal/system/chtimes_linux_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/internal/system/chtimes_nowindows.go -->
# sources/cloud-native/moby/daemon/internal/system/chtimes_nowindows.go

## Purpose
Provides the non-Windows `setCTime` implementation for `Chtimes`.

## Important APIs, Types, And Functions
`setCTime(path string, ctime time.Time) error` always returns nil. Its comment explains that Unix create/change time behavior is updated as a side effect of modifying mtime, so no explicit creation-time call exists.

## Control Flow
There is no conditional behavior; every call is a no-op success.

## State And Persistence
No additional state is mutated beyond the preceding `os.Chtimes` call in `Chtimes`.

## Dependencies And Integration Points
Selected by the `!windows` build tag. It satisfies the shared `Chtimes` call site.

## Risks And Test Signals
The abstraction name says create time, but Unix exposes ctime as metadata change time rather than creation time on most filesystems. Tests for Unix focus on atime/mtime and do not verify birth time.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/internal/system/chtimes_nowindows.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/internal/system/chtimes_test.go -->
# sources/cloud-native/moby/daemon/internal/system/chtimes_test.go

## Purpose
Cross-platform tests for `Chtimes` modification-time behavior and timestamp clamping.

## Important APIs, Types, And Functions
`TestChtimesModTime` creates a temp file and checks `os.FileInfo.ModTime()` after calls to `Chtimes` with epoch, pre-epoch, valid post-epoch, and `unixMaxTime`.

## Control Flow
Subtests reuse the same file and verify expected mtime after each timestamp update. Invalid pre-epoch values are expected to be replaced by epoch. Max-time comparison truncates to seconds.

## State And Persistence
Only temporary file timestamps are changed.

## Dependencies And Integration Points
Uses standard `os`, `filepath`, and `time`. It validates the shared `Chtimes` logic independent of platform-specific atime/ctime tests.

## Risks And Test Signals
The test ignores atime because it is OS-dependent. It also does not test beyond-max input explicitly, only exactly `unixMaxTime`. Strong signal is that pre-epoch mtime is clamped instead of passed to `os.Chtimes`.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/internal/system/chtimes_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/internal/system/chtimes_windows.go -->
# sources/cloud-native/moby/daemon/internal/system/chtimes_windows.go

## Purpose
Implements Windows creation-time update support used after `Chtimes` changes access and modification times.

## Important APIs, Types, And Functions
`setCTime` converts the path to UTF-16, opens it with `windows.CreateFile` using `FILE_WRITE_ATTRIBUTES`, `FILE_SHARE_WRITE`, `OPEN_EXISTING`, and `FILE_FLAG_BACKUP_SEMANTICS`, converts Unix nanoseconds with `windows.NsecToFiletime`, and calls `windows.SetFileTime` with a creation-time pointer.

## Control Flow
Errors from path conversion, file open, or `SetFileTime` are returned. The file handle is closed via defer.

## State And Persistence
Mutates the Windows creation time for a file or directory. It does not alter access or write times directly; those are handled by `os.Chtimes`.

## Dependencies And Integration Points
Selected on Windows and used by shared `Chtimes`. Depends on `golang.org/x/sys/windows`.

## Risks And Test Signals
Opening with backup semantics is needed for directories. Sharing mode is limited to write share, which may fail when files are open with incompatible modes. Windows tests verify atime behavior; creation time is not directly asserted in this subset.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/internal/system/chtimes_windows.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/internal/system/chtimes_windows_test.go -->
# sources/cloud-native/moby/daemon/internal/system/chtimes_windows_test.go

## Purpose
Windows-specific tests for `Chtimes` access-time behavior using Win32 file attribute data.

## Important APIs, Types, And Functions
`TestChtimesATimeWindows` writes a temp file, calls `Chtimes`, reads `os.Stat`, and extracts `LastAccessTime.Nanoseconds()` from `syscall.Win32FileAttributeData`.

## Control Flow
The same timestamp scenarios as the Linux atime and cross-platform mtime tests are covered: epoch, pre-epoch clamping, valid post-epoch, and max time.

## State And Persistence
Only temporary file timestamps are mutated.

## Dependencies And Integration Points
Windows build only. It validates that the shared clamping logic and Windows `os.Chtimes` interaction set access time as expected.

## Risks And Test Signals
Creation time, the Windows-specific `setCTime` behavior, is not explicitly checked. Filesystem timestamp precision can vary, so max-time checks truncate to seconds. The main signal is parity with Unix atime clamping behavior.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/internal/system/chtimes_windows_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/internal/system/filesys_windows.go -->
# sources/cloud-native/moby/daemon/internal/system/filesys_windows.go

## Purpose
Provides Windows directory creation helpers that apply explicit ACLs while preserving `os.MkdirAll`-like behavior and volume-path handling.

## Important APIs, Types, And Functions
`SddlAdministratorsLocalSystem` grants full access to built-in Administrators and Local System with inheritance. `MkdirAllWithACL` converts SDDL to `windows.SecurityAttributes` and calls `mkdirAllWithACL`. `mkdirAllWithACL` mirrors Go's `os.MkdirAll` recursive logic. `mkdirWithACL` calls `windows.CreateDirectory`. `makeSecurityAttributes` builds inherited security attributes from SDDL.

## Control Flow
The helper first returns success for existing directories and `ENOTDIR` for existing non-directories. Otherwise it recursively creates parents until the volume root, then creates the target with the supplied security descriptor.

## State And Persistence
Creates directories on disk with the requested DACL. Security attributes are temporary process memory.

## Dependencies And Integration Points
Windows-only and likely used by daemon storage/runtime paths that need predictable permissions for service accounts.

## Risks And Test Signals
Behavior intentionally tracks Go 1.23.4 `MkdirAll`; upstream changes may need porting. Invalid SDDL or path conversion errors become `os.PathError`. No tests for this file are included in the subset.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/internal/system/filesys_windows.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/internal/system/utimes_unix.go -->
# sources/cloud-native/moby/daemon/internal/system/utimes_unix.go

## Purpose
Provides `LUtimesNano`, a symlink-preserving timestamp update helper for Linux and FreeBSD.

## Important APIs, Types, And Functions
`LUtimesNano(path string, ts []syscall.Timespec) error` converts two syscall timespecs to `unix.Timespec` and calls `unix.UtimesNanoAt` with `AT_FDCWD` and `AT_SYMLINK_NOFOLLOW`.

## Control Flow
The function updates access and modification times on the link itself. It returns syscall errors except `ENOSYS`, which is ignored for compatibility with systems lacking the syscall.

## State And Persistence
Mutates filesystem timestamps on the named path, specifically not following symlinks.

## Dependencies And Integration Points
Used by archive/extraction code that must preserve symlink metadata. Depends on `golang.org/x/sys/unix`.

## Risks And Test Signals
The function assumes `ts` has at least two elements and will panic otherwise. Ignoring `ENOSYS` means callers may believe timestamps were applied when the kernel could not support it. Tests verify symlink timestamp changes without target-file changes and error on missing paths.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/internal/system/utimes_unix.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/internal/system/utimes_unix_test.go -->
# sources/cloud-native/moby/daemon/internal/system/utimes_unix_test.go

## Purpose
Tests `LUtimesNano` on Linux/FreeBSD for symlink no-follow timestamp updates and missing-path errors.

## Important APIs, Types, And Functions
`prepareFiles` creates a real file, an invalid path, and a symlink to the file. `TestLUtimesNano` captures the target file's original stat, sets symlink times to zero, checks `os.Lstat` on the symlink, checks `os.Stat` on the target, and verifies missing-path error behavior.

## Control Flow
The test first validates that the symlink mtime differs after `LUtimesNano`, then confirms the target file mtime remains the same. It finally calls the function on a nonexistent path and expects an error.

## State And Persistence
All files live in a temporary test directory.

## Dependencies And Integration Points
Requires symlink support and the Unix `UtimesNanoAt` path. It validates metadata preservation behavior used by archive extraction.

## Risks And Test Signals
Comparisons use Unix seconds, so subsecond precision changes are not asserted. On platforms where `ENOSYS` is ignored, the symlink-change assertion could expose unsupported behavior.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/internal/system/utimes_unix_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/internal/system/xattrs_linux.go -->
# sources/cloud-native/moby/daemon/internal/system/xattrs_linux.go

## Purpose
Wraps Linux extended attribute operations with daemon-specific error context and no-follow semantics.

## Important APIs, Types, And Functions
`XattrError` stores operation, attribute, path, and underlying error, implements `Error`, `Unwrap`, and `Timeout`. `Lgetxattr` reads an xattr without following symlinks, starting with a 128-byte buffer and resizing on `ERANGE`. Missing attributes (`ENODATA`) return nil data and nil error. `Lsetxattr` writes an xattr and wraps failures.

## Control Flow
`Lgetxattr` retries size discovery using a zero-sized buffer when the initial buffer is too small, then performs the real read. All other syscall errors are wrapped.

## State And Persistence
`Lsetxattr` mutates xattrs on filesystem objects. `Lgetxattr` is read-only.

## Dependencies And Integration Points
Linux-only helper around `golang.org/x/sys/unix`. Used by layer/archive code that preserves xattrs and needs distinguishable path/attribute errors.

## Risks And Test Signals
Race between size discovery and second read can still produce `ERANGE` if the xattr changes concurrently; the loop handles initial ERANGE but not repeated growth after allocation. No tests are listed in this subset.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/internal/system/xattrs_linux.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/internal/timestamp/timestamp.go -->
# sources/cloud-native/moby/daemon/internal/timestamp/timestamp.go

## Purpose
Parses Docker timestamp inputs for log and event filters, accepting durations, partial RFC3339 forms, date forms, and Unix timestamps with optional fractional seconds.

## Important APIs, Types, And Functions
`Parse(value, reference)` returns UTC time, treating durations as `reference - duration`. It chooses layouts based on zones, `T`, fractional seconds, and date-only input. `ParseUnixTimestamp` wraps `parseTimestamp` and permits empty input as zero time. `parseTimestamp` parses seconds and fractional nanoseconds, pads/truncates to nine digits, and rejects fractional parts over 20 digits or containing non-digits.

## Control Flow
`Parse` rejects blank strings, tries `time.ParseDuration` except literal `"0"`, then selects either `time.ParseInLocation` using the reference zone or absolute `time.Parse`. Failed non-date parsing falls back to Unix timestamp parsing.

## State And Persistence
No persistent state. Returned times are normalized to UTC.

## Dependencies And Integration Points
Used by daemon API query parameters such as `docker logs --since/--until` and `docker events`. Behavior is client-facing and compatibility-sensitive.

## Risks And Test Signals
Heuristics around `-`, `+`, and `Z` determine local versus absolute parsing. Whitespace is rejected except for the initial empty check. Tests cover partial RFC3339, zones, Unix timestamps, fractional bounds, durations, invalid values, and empty Unix timestamp behavior.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/internal/timestamp/timestamp.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/internal/timestamp/timestamp_test.go -->
# sources/cloud-native/moby/daemon/internal/timestamp/timestamp_test.go

## Purpose
Provides broad compatibility tests for timestamp parsing accepted by Docker log/event APIs.

## Important APIs, Types, And Functions
`TestParse` covers `timestamp.Parse` against a fixed reference time. `TestParseUnixTimestamp` covers the lower-level Unix timestamp parser. Assertions compare UTC RFC3339Nano strings or Unix seconds/nanoseconds.

## Control Flow
Table-driven cases include full and partial RFC3339 with/without zones, date-only inputs, Unix timestamps, fractional nanoseconds with padding/truncation, relative durations, invalid strings, whitespace, and empty values.

## State And Persistence
No state beyond fixed test data.

## Dependencies And Integration Points
Uses `gotest.tools` assertions and imports the package externally as `timestamp_test`, exercising the public API rather than internals.

## Risks And Test Signals
The suite assumes UTC reference zone, so local-zone parsing paths are only partially represented. Strong signals include rejecting whitespace-wrapped numeric timestamps, preserving fractional nanosecond rules, and treating negative durations as future offsets relative to the reference.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/internal/timestamp/timestamp_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/internal/unix_noeintr/epoll_linux.go -->
# sources/cloud-native/moby/daemon/internal/unix_noeintr/epoll_linux.go

## Purpose
Provides Linux epoll syscall wrappers that transparently retry on `EINTR`.

## Important APIs, Types, And Functions
`EpollCreate` calls `unix.EpollCreate1` with `EPOLL_CLOEXEC`. `EpollCtl` wraps `unix.EpollCtl`. `EpollWait` wraps `unix.EpollWait`. Each loops until the syscall returns a non-`EINTR` error or success.

## Control Flow
Every wrapper is a small `for` loop: call syscall, continue on `errors.Is(err, unix.EINTR)`, otherwise return result.

## State And Persistence
`EpollCreate` allocates a kernel file descriptor. Other wrappers mutate or wait on kernel epoll state supplied by the caller.

## Dependencies And Integration Points
Used by daemon components that need robust epoll behavior under signal interruption. Depends on `golang.org/x/sys/unix`.

## Risks And Test Signals
Infinite retry is intentional for interruptible syscalls but can mask repeated signal storms. Callers still own fd close and timeout behavior. No tests are listed in this subset.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/internal/unix_noeintr/epoll_linux.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/internal/unix_noeintr/fs_unix.go -->
# sources/cloud-native/moby/daemon/internal/unix_noeintr/fs_unix.go

## Purpose
Provides non-Darwin, non-Windows filesystem syscall wrappers that retry operations interrupted by signals.

## Important APIs, Types, And Functions
`Retry` runs a function until it returns something other than `unix.EINTR`. Wrappers include `Mount`, `Unmount`, `Open`, `Close`, `Openat`, `Openat2`, `Fstat`, and `Fstatat`, each capturing syscall results and returning them after retry.

## Control Flow
Each wrapper uses a closure passed to `Retry`, assigning return values on every attempt. The final non-EINTR error or nil is returned to the caller.

## State And Persistence
Operations can mutate mount state, open/close file descriptors, or read file metadata. The wrappers themselves keep no state.

## Dependencies And Integration Points
Used wherever daemon code wants uniform no-EINTR Unix syscall behavior. Excludes Darwin and Windows via build tags.

## Risks And Test Signals
`Close` retrying on EINTR can be subtle on Unix because fd state after interrupted close is platform-dependent; this package intentionally centralizes that policy. No tests are included in this subset.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/internal/unix_noeintr/fs_unix.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/internal/unshare/unshare_linux.go -->
# sources/cloud-native/moby/daemon/internal/unshare/unshare_linux.go

## Purpose
Runs functions in a new goroutine locked to an OS thread whose Linux execution state has been unshared, while protecting the Go startup thread from namespace mutation.

## Important APIs, Types, And Functions
`init` locks the startup thread with `runtime.LockOSThread` to avoid `/proc/self` reflecting a mutated startup-thread namespace. `reversibleSetnsFlags` maps namespace flags that can be saved/restored with `setns`. `Go(flags, setupfn, fn)` locks a new goroutine to its thread, optionally saves namespace fds, calls `unix.Unshare`, runs setup, signals readiness, runs `fn`, and restores reversible namespaces when possible.

## Control Flow
`Go` determines whether all requested flags are reversible. For reversible flags it opens `/proc/self/task/<tid>/ns/<name>` fds and defers `Setns` restoration. If unshare or setup fails, the error is sent on `started` and `fn` is skipped. For irreversible state, the thread may be allowed to terminate after the goroutine returns.

## State And Persistence
Mutates per-thread kernel namespace and execution state. The caller observes only setup errors; `fn` runs asynchronously after readiness.

## Dependencies And Integration Points
Used by daemon code that needs isolated namespace operations without poisoning process-global `/proc/self` consumers such as mountinfo.

## Risks And Test Signals
The startup-thread lock has global runtime implications. Pdeathsig subprocesses may see early signals if the unshared thread exits. No tests are included here, so comments document much of the safety contract.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/internal/unshare/unshare_linux.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/internal/usergroup/add_linux.go -->
# sources/cloud-native/moby/daemon/internal/usergroup/add_linux.go

## Purpose
Creates a Linux system user/group for user namespace remapping and ensures subordinate UID/GID ranges exist.

## Important APIs, Types, And Functions
`AddNamespaceRangesUser` calls `addUser`, runs `id`, parses uid/gid with `idOutRegexp`, then calls `createSubordinateRanges`. `addUser` selects `adduser` or `useradd` once using `resolveBinary`. `createSubordinateRanges` checks `/etc/subuid` and `/etc/subgid`, finds non-overlapping defaults with `findNextUIDRange`/`findNextGIDRange`, and applies ranges with `usermod -v` and `-w`. `wouldOverlap` detects range conflicts.

## Control Flow
The flow shells out to distro tools, parses results, then fills subordinate ranges only when absent. Existing ranges are preserved.

## State And Persistence
Mutates system accounts and `/etc/subuid`/`/etc/subgid` via system utilities. This is privileged host state.

## Dependencies And Integration Points
Used by daemon user namespace remap setup. Depends on `adduser` or `useradd`, `id`, `usermod`, and `github.com/moby/sys/user` parsers.

## Risks And Test Signals
Command availability and distro output format are external risks. `once` caches the selected user command for process lifetime. Root-only tests create and delete a temp user, load identity mapping, and verify mapped-user filesystem access.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/internal/usergroup/add_linux.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/internal/usergroup/add_linux_test.go -->
# sources/cloud-native/moby/daemon/internal/usergroup/add_linux_test.go

## Purpose
Integration-tests Linux user creation, subordinate ID mapping, lookup, and mapped filesystem access for user namespace support.

## Important APIs, Types, And Functions
`TestNewIDMappings` calls `AddNamespaceRangesUser`, `LoadIdentityMapping`, `RootPair`, `MkdirAllAndChown`, and runs `ls` with `syscall.Credential`. `TestLookupUserAndGroup` verifies name and numeric lookup parity. `delUser` removes the temporary user with `userdel`.

## Control Flow
Tests skip unless running as root. Each creates `tempuser`, defers deletion, then checks either identity mapping and directory access or lookup by name and id.

## State And Persistence
These tests mutate host user/group databases and subordinate ID files. Cleanup uses `userdel` but failures may leave state behind.

## Dependencies And Integration Points
Requires root, system account tools, subordinate ID support, and `moby/sys/user`. It validates daemon setup against real OS behavior.

## Risks And Test Signals
The fixed username can conflict with existing users or parallel tests. The strongest signal is that a process running as the remapped root uid/gid can access a chowned directory.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/internal/usergroup/add_linux_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/internal/usergroup/add_unsupported.go -->
# sources/cloud-native/moby/daemon/internal/usergroup/add_unsupported.go

## Purpose
Provides the non-Linux fallback for user namespace remap account creation.

## Important APIs, Types, And Functions
`AddNamespaceRangesUser(name)` returns `-1, -1` and an error stating that adding users or groups is unsupported on this OS.

## Control Flow
No work is attempted on unsupported platforms.

## State And Persistence
No state is mutated.

## Dependencies And Integration Points
Selected by the `!linux` build tag to satisfy call sites that compile across platforms.

## Risks And Test Signals
The error string starts with a capitalized "No", which may matter if callers or tests compare exact text. There are no tests in this subset for unsupported platforms.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/internal/usergroup/add_unsupported.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/internal/usergroup/lookup_unix.go -->
# sources/cloud-native/moby/daemon/internal/usergroup/lookup_unix.go

## Purpose
Looks up Unix users/groups through local files first and `getent` fallback, then builds subordinate ID mappings for user namespace remapping.

## Important APIs, Types, And Functions
`LookupUser`, `LookupUID`, `LookupGroup`, and `LookupGID` call `moby/sys/user` local lookup then fallback to `getentUser`/`getentGroup`. `callGetent` resolves and runs `getent`, translates exit codes, and returns output. `LoadIdentityMapping` loads a user and reads `/etc/subuid` and `/etc/subgid` via `lookupSubRangesFile`, building sequential container ID maps.

## Control Flow
Fallback only occurs after local lookup fails. `getent` output is parsed using `user.ParsePasswd` or `user.ParseGroup`. Subordinate ranges can match by username or numeric uid and are appended in file order with cumulative container IDs.

## State And Persistence
Lookup is read-only against system files/NSS. No persistent state is changed.

## Dependencies And Integration Points
Supports hosts where users/groups come from LDAP, SSSD, or other NSS sources. Uses `resolveBinary` to avoid symlink spoofing and avoids `/dev/null` stdin assumptions.

## Risks And Test Signals
Exact `getent` exit-code semantics vary by implementation. No sorting is applied to mapping ranges. Tests cover nonexistent users/groups and root integration tests cover successful paths.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/internal/usergroup/lookup_unix.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/internal/usergroup/lookup_unix_test.go -->
# sources/cloud-native/moby/daemon/internal/usergroup/lookup_unix_test.go

## Purpose
Tests negative user and group lookup paths on Unix.

## Important APIs, Types, And Functions
`TestLookupUserAndGroupThatDoesNotExist` calls `LookupUser`, `LookupUID`, `LookupGroup`, and `LookupGID` with fake names or `-1` IDs and asserts errors.

## Control Flow
The test expects named lookups to fall through to `getent` and return specific "unable to find entry" messages for passwd and group databases. Numeric negative lookups only assert a non-empty error.

## State And Persistence
Read-only; no accounts are created or removed.

## Dependencies And Integration Points
Requires a `getent` command on the test host. It validates the fallback error mapping used by daemon user namespace lookup.

## Risks And Test Signals
Exact error strings depend on this package's translation of getent exit status 2; systems without getent may produce different errors. The test does not cover successful NSS-only fallback.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/internal/usergroup/lookup_unix_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/internal/usergroup/parser.go -->
# sources/cloud-native/moby/daemon/internal/usergroup/parser.go

## Purpose
Provides small helpers to parse subordinate UID and GID ranges for a specific username from standard Linux files.

## Important APIs, Types, And Functions
Constants `subuidFileName` and `subgidFileName` point to `/etc/subuid` and `/etc/subgid`. `parseSubuid` and `parseSubgid` call `user.ParseSubIDFileFilter` and retain entries whose `sid.Name` equals the requested username.

## Control Flow
Each helper delegates parsing and filtering to `github.com/moby/sys/user`; no additional validation or sorting is done here.

## State And Persistence
Read-only access to subordinate ID files.

## Dependencies And Integration Points
Used by `createSubordinateRanges` to decide whether distro user creation already created ranges.

## Risks And Test Signals
Numeric uid aliases are not matched here, only names; `LoadIdentityMapping` has broader matching. Tests in `parser_test.go` exercise underlying parser behavior with comments and blank lines rather than these exact constants.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/internal/usergroup/parser.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/internal/usergroup/parser_test.go -->
# sources/cloud-native/moby/daemon/internal/usergroup/parser_test.go

## Purpose
Tests subordinate ID file parsing across comments and blank lines using the shared `moby/sys/user` parser.

## Important APIs, Types, And Functions
`TestParseSubidFileWithNewlinesAndComments` writes a temporary subuid-style file and calls `user.ParseSubIDFileFilter` for `dockremap`.

## Control Flow
The test file includes one ordinary range, a comment line, a blank line, and a target range. The test expects exactly one returned range with `SubID` 231072 and `Count` 65536.

## State And Persistence
Uses a temporary directory and file only.

## Dependencies And Integration Points
Although it does not call `parseSubuid` directly, it validates the parser behavior those helpers rely on.

## Risks And Test Signals
The test does not cover malformed lines, numeric-name matching, duplicate ranges, or the package constants pointing at `/etc/subuid` and `/etc/subgid`. Its signal is that comments and blank lines are tolerated.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/internal/usergroup/parser_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/internal/usergroup/utils_unix.go -->
# sources/cloud-native/moby/daemon/internal/usergroup/utils_unix.go

## Purpose
Safely resolves required Unix helper binaries from `PATH`.

## Important APIs, Types, And Functions
`resolveBinary(binname)` calls `exec.LookPath`, resolves symlinks with `filepath.EvalSymlinks`, and returns success only when the resolved basename still matches the requested binary name.

## Control Flow
Lookup failure or symlink resolution failure is returned. A basename mismatch produces an explicit error mentioning the requested binary and resolved path.

## State And Persistence
No state is mutated.

## Dependencies And Integration Points
Used before invoking `adduser`, `useradd`, and `getent` so daemon account-management code does not accidentally run an alias to another binary.

## Risks And Test Signals
The symlink basename check can reject legitimate alternatives managed through symlinks, trading flexibility for predictability. No tests are listed in this subset for the resolver itself.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/internal/usergroup/utils_unix.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/internal/versions/compare.go -->
# sources/cloud-native/moby/daemon/internal/versions/compare.go

## Purpose
Implements simple dot-separated numeric version comparison helpers.

## Important APIs, Types, And Functions
Private `compare(v1, v2)` returns -1, 0, or 1. Public helpers `LessThan`, `LessThanOrEqualTo`, `GreaterThan`, `GreaterThanOrEqualTo`, and `Equal` wrap it as booleans.

## Control Flow
Versions are split on `"."`; missing components are treated as zero. Each component is converted with `strconv.Atoi`; conversion errors are ignored, making invalid components compare as zero. The first differing numeric component decides the result.

## State And Persistence
Stateless.

## Dependencies And Integration Points
Used wherever daemon internals need lightweight numeric version checks without semantic-version prerelease/build handling.

## Risks And Test Signals
Ignoring parse errors means `"1.x"` equals `"1.0"` and negative or nonnumeric inputs are not rejected. This is not full semver. Tests cover equality with trailing zeros and basic numeric ordering.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/internal/versions/compare.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/internal/versions/compare_test.go -->
# sources/cloud-native/moby/daemon/internal/versions/compare_test.go

## Purpose
Tests numeric dot-separated version comparison ordering.

## Important APIs, Types, And Functions
`assertVersion` wraps private `compare`. `TestCompareVersion` covers equal versions, trailing zero equivalence, longer/shorter comparisons, and multi-component ordering.

## Control Flow
The test calls `compare` with fixed pairs and expected -1, 0, or 1 results, failing immediately on mismatch.

## State And Persistence
No state.

## Dependencies And Integration Points
Standard testing only. It validates the assumptions behind public comparison helpers.

## Risks And Test Signals
No tests cover invalid components, prerelease strings, whitespace, or leading signs. The key compatibility signal is that `"1.0.0"` equals `"1"` while `"1.0.1"` is greater.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/internal/versions/compare_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/keys.go -->
# sources/cloud-native/moby/daemon/keys.go

## Purpose
Raises Linux root keyring limits for the daemon when the kernel configuration is below Docker's expected threshold.

## Important APIs, Types, And Functions
Constants point to `/proc/sys/kernel/keys/root_maxkeys` and `root_maxbytes`, with `rootKeyLimit` 1,000,000 and byte multiplier 25. `modifyRootKeyLimit` reads the current key limit and calls `setRootKeyLimit` only when it is lower. `setRootKeyLimit` writes both maxkeys and maxbytes. `readRootKeyLimit` reads and trims the proc file.

## Control Flow
Startup code can call `modifyRootKeyLimit`; if the existing setting is already high enough, no writes occur. When writing, maxkeys is updated first, then maxbytes.

## State And Persistence
Mutates kernel sysctl state via procfs. These settings affect the running system and may persist depending on host sysctl configuration outside this code.

## Dependencies And Integration Points
Linux-only daemon startup support for overlay/network/security features that can consume kernel keys.

## Risks And Test Signals
Requires permission to write procfs. If maxkeys write succeeds and maxbytes write fails, the system is left partially updated. No tests are included in this subset.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/keys.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/keys_unsupported.go -->
# sources/cloud-native/moby/daemon/keys_unsupported.go

## Purpose
Provides the non-Linux no-op implementation of daemon key limit adjustment.

## Important APIs, Types, And Functions
`modifyRootKeyLimit()` returns nil without doing work.

## Control Flow
There is no conditional behavior.

## State And Persistence
No state is mutated.

## Dependencies And Integration Points
Selected by `!linux` so daemon startup can call the same function on all platforms.

## Risks And Test Signals
Unsupported platforms silently skip key-limit configuration, which is appropriate because the Linux procfs key sysctls do not exist. No tests are included.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/keys_unsupported.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/kill.go -->
# sources/cloud-native/moby/daemon/kill.go

## Purpose
Implements daemon container signal delivery and force-kill behavior, including stop-signal parsing, paused-container handling, manual-stop persistence, and exit-event races.

## Important APIs, Types, And Functions
`ContainerKill` parses an optional signal, validates platform support, resolves the container, and dispatches to `Kill` for default SIGKILL or `killWithSignal` otherwise. `killWithSignal` locks the container, gets its running task, marks `ExitOnNext` for configured stop signals or SIGKILL, checkpoints manual-stop state, handles restarting containers, calls task `Kill`, resumes paused containers when needed, and logs kill events. `Kill` sends SIGKILL, waits, tries direct process kill on timeout, then waits again. `errNoSuchProcess` implements `NotFound`.

## Control Flow
Signal parse errors are invalid-parameter errors. Not-found task kill errors trigger an asynchronous wait and possible exit handling rather than immediate failure. Windows receives a longer force-kill wait timeout.

## State And Persistence
Mutates container state flags (`ExitOnNext`, `HasBeenManuallyStopped`), checkpoints to `containersReplica`, emits events, and may resume paused tasks.

## Dependencies And Integration Points
Integrates daemon container store, containerd task APIs, event logging, signal parsing, and platform-specific `killProcessDirectly`.

## Risks And Test Signals
Races with already-exited tasks are explicitly handled but still timing-sensitive. Checkpoint failures are logged but nonfatal. No direct tests are included in this subset.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/kill.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/libnetwork/agent.go -->
# sources/cloud-native/moby/daemon/libnetwork/agent.go

## Purpose
Implements libnetwork's cluster agent integration around NetworkDB gossip, service discovery, driver table watches, encryption-key distribution, and swarm-scoped network membership.

## Important APIs, Types, And Functions
`nwAgent` stores `NetworkDB`, bind/advertise/datapath addresses, and cancel functions. Address helpers resolve IPs, hostnames, or interface names. Controller methods `agentSetup`, `agentInit`, `agentJoin`, `agentDriverNotify`, `agentClose`, `handleKeyChange`, `getKeys`, and `getPrimaryKeyTag` manage cluster lifecycle and keys. Network/Endpoint methods join/leave networks, publish/delete driver entries, publish/disable/delete service info, and add/cancel driver watches. `handleEpTableEvent` translates NetworkDB endpoint events into service binding or container name-resolution calls.

## Control Flow
Setup reads cluster provider addresses, initializes NetworkDB if an advertise address exists, registers table watches, notifies global drivers, then joins remote peers. Endpoint publication marshals `EndpointRecord` into `libnetworkEPTable`; deletion either removes the entry or marks it disabled. Watch handlers unmarshal previous/current records, compare semantic equivalence ignoring `ServiceDisabled`, remove stale bindings, and add or disable current bindings.

## State And Persistence
State lives in NetworkDB gossip tables, local controller key slices, driver watch cancel maps, and local DNS/LB binding stores. Key changes update NetworkDB gossip keys and notify datapath drivers.

## Dependencies And Integration Points
Depends on cluster provider, NetworkDB, driver discovery/table APIs, protobuf records, overlay/service binding code, and diagnostic handlers.

## Risks And Test Signals
Key ordering is subtle: primary key is the second Lamport-sorted key and `getKeys` swaps the first two. Endpoint add/delete paths guard sandbox races with service locks. Tests focus on endpoint equivalence and transition actions across create/update/delete/replace events.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/libnetwork/agent.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/libnetwork/agent.pb.go -->
# sources/cloud-native/moby/daemon/libnetwork/agent.pb.go

## Purpose
Generated gogo/protobuf implementation for `agent.proto`, defining the wire-compatible Go types and serialization code used in libnetwork gossip tables.

## Important APIs, Types, And Functions
Defines `PortConfig_Protocol` enum values `ProtocolTCP`, `ProtocolUDP`, and `ProtocolSCTP`; message structs `EndpointRecord` and `PortConfig`; getters; registration; `Marshal`, `MarshalTo`, `MarshalToSizedBuffer`, `Size`, `String`, `GoString`, and `Unmarshal` methods; varint helpers; unknown-field skipping; and generated errors for invalid lengths, integer overflow, and unexpected groups.

## Control Flow
Marshal methods write fields in reverse into sized buffers, omitting zero values. Unmarshal loops over wire fields, validates wire types and lengths, appends repeated fields, skips unknown fields, and returns EOF/overflow/length errors for malformed input.

## State And Persistence
No runtime state beyond message values. Serialized bytes are persisted or propagated through NetworkDB endpoint tables.

## Dependencies And Integration Points
Generated from `agent.proto` with gogo options and used by `agent.go`, diagnostics, tests, and any NetworkDB peers expecting the same schema.

## Risks And Test Signals
Manual edits would be overwritten by generation. Schema field numbers are compatibility-critical. Tests indirectly exercise marshal/unmarshal through `agent_test.go` and diagnostic decoding.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/libnetwork/agent.pb.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/libnetwork/agent.proto -->
# sources/cloud-native/moby/daemon/libnetwork/agent.proto

## Purpose
Defines the protobuf schema for endpoint records and ingress port configs gossiped between libnetwork cluster nodes.

## Important APIs, Types, And Functions
`EndpointRecord` carries endpoint name, service name/id, virtual IP, endpoint IP, ingress ports, service aliases, task aliases, and `service_disabled`. `PortConfig` carries port name, protocol enum, target port, and published port. Gogo options request custom names, marshalers, unmarshalers, stringers, sizers, and GoString methods.

## Control Flow
There is no executable flow in the schema. Generated code serializes these fields into NetworkDB values consumed by `agent.go`.

## State And Persistence
The schema defines persistent/gossiped NetworkDB value layout. Field numbers are the compatibility contract across nodes and versions.

## Dependencies And Integration Points
Imported by protoc with `gogoproto`. `EndpointRecord` is stored in `endpoint_table`; `PortConfig` ingress data is used for service binding and diagnostics.

## Risks And Test Signals
Changing field numbers or semantics can break mixed-version clusters. `service_disabled` is treated specially by event logic as a state toggle that may not change endpoint equivalence. Tests cover generated records through event transition handling.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/libnetwork/agent.proto -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/libnetwork/agent_test.go -->
# sources/cloud-native/moby/daemon/libnetwork/agent_test.go

## Purpose
Tests the high-risk endpoint event logic in libnetwork agent gossip handling.

## Important APIs, Types, And Functions
`TestEndpointEvent_EquivalentTo` validates semantic equality rules for endpoint events, including unordered ingress ports and aliases while ignoring `ServiceDisabled`. `mockServiceBinder` records binding actions. `TestHandleEPTableEvent` builds `networkdb.WatchEvent` values with marshaled previous/current `EndpointRecord` data and asserts expected add/remove operations.

## Control Flow
Transition cases cover insert, update, delete, and replace for service endpoints and attachable-network containers with `ServiceDisabled` true/false combinations. Service transitions use `addServiceBinding` or `rmServiceBinding`; container transitions use add/delete name resolution.

## State And Persistence
All state is in memory. Protobuf marshal/unmarshal is exercised for event payloads.

## Dependencies And Integration Points
Uses `gogo/protobuf`, NetworkDB watch events, and `gotest.tools` assertions. It isolates agent event logic behind the `serviceBinder` interface.

## Risks And Test Signals
The tests do not start real NetworkDB or drivers. Their strong signal is preventing DNS/LB flapping and ensuring disabled endpoints remove bindings without fully deleting service records unless appropriate.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/libnetwork/agent_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/libnetwork/bitmap/sequence.go -->
# sources/cloud-native/moby/daemon/libnetwork/bitmap/sequence.go

## Purpose
Implements a fixed-length, non-concurrent bitmap using run-length encoded 32-bit blocks. It supports efficient allocation/free operations, range allocation, selected-bit counting, copying, and binary/JSON persistence.

## Important APIs, Types, And Functions
`Bitmap` stores total bits, unselected count, RLE `head`, and serial scan cursor. Public APIs include `New`, `Copy`, `Set`, `Unset`, `SetAny`, `SetAnyInRange`, `IsSet`, `OnesCount`, `MarshalBinary`, `UnmarshalBinary`, JSON marshal/unmarshal, `Bits`, `Unselected`, and `String`. Internal helpers include `sequence`, `findSequence`, `getFirstAvailable`, `getAvailableFromCurrent`, `checkIfAvailable`, `pushReservation`, and `mergeSequences`.

## Control Flow
Allocation finds an unset bit, then `pushReservation` splits or merges RLE nodes depending on whether the affected block is first, last, or middle of a sequence. Release clears a bit through the same path. Serial allocation starts scanning at `curr` and rolls over to the requested start.

## State And Persistence
Bitmap state is mutable and explicitly not safe for concurrent use. Binary persistence stores `bits`, `unselected`, and sequence nodes; `curr` is not persisted or reset by unmarshal.

## Dependencies And Integration Points
Used by libnetwork allocators for long ordinal spaces. JSON serialization preserves on-disk compatibility through base64-encoded binary data.

## Risks And Test Signals
Boundary math is complex around non-32-bit lengths, range ends, and RLE splitting. Tests are extensive, including random allocation/deallocation, golden JSON, rollover, and property-based `OnesCount`.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/libnetwork/bitmap/sequence.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/libnetwork/bitmap/sequence_test.go -->
# sources/cloud-native/moby/daemon/libnetwork/bitmap/sequence_test.go

## Purpose
Exhaustively tests the RLE bitmap implementation's bit search, sequence mutation, allocation/deallocation, serialization, rollover, and counting behavior.

## Important APIs, Types, And Functions
Tests cover internal helpers (`getAvailableBit`, `equal`, `getCopy`, `getFirstAvailable`, `findSequence`, `checkIfAvailable`, `mergeSequences`, `pushReservation`, `getAvailableFromCurrent`) and public APIs (`Set`, `Unset`, `SetAny`, `SetAnyInRange`, `Bits`, `Unselected`, JSON marshal/unmarshal, `OnesCount`).

## Control Flow
The suite uses large table-driven cases for masks and sequence shapes, randomized allocation/deallocation patterns with logged seeds, a golden JSON serialization for backward compatibility, and `rapid` property checks comparing `OnesCount` to a straightforward selected-ordinal count.

## State And Persistence
All bitmaps are in-memory except JSON serialization bytes. Random tests mutate bitmaps heavily and verify final compressed sequence strings.

## Dependencies And Integration Points
Uses `gotest.tools` and `pgregory.net/rapid`. These tests protect libnetwork address/ordinal allocation behavior and persisted bitmap compatibility.

## Risks And Test Signals
Randomized tests can be seed-sensitive, but seeds are logged. The golden JSON test is a strong signal that persisted sequence encoding remains backward compatible. The property test covers many range-count edge cases.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/libnetwork/bitmap/sequence_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/libnetwork/cluster/provider.go -->
# sources/cloud-native/moby/daemon/libnetwork/cluster/provider.go

## Purpose
Defines the libnetwork-facing interface for swarm/cluster providers and event types emitted by cluster control.

## Important APIs, Types, And Functions
Constants define `EventSocketChange`, `EventNodeReady`, `EventNodeLeave`, and `EventNetworkKeysAvailable`. `ConfigEventType` is a `uint8`. `Provider` exposes manager/agent role checks, local/listen/advertise/datapath/remote addresses, event listening, network attach/detach/update, and detachment waiting.

## Control Flow
The file only declares contracts. Implementations provide event channels and operations; libnetwork consumers call these methods during agent setup and swarm network attachment.

## State And Persistence
No state is stored here. Implementations may persist or mutate swarm/network state.

## Dependencies And Integration Points
Imports Docker API network types and `context`. `agent.go` uses address getters and remote lists to initialize NetworkDB and join peers.

## Risks And Test Signals
Interface changes affect cluster provider implementations and tests across the daemon. No direct tests are included in this subset.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/libnetwork/cluster/provider.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/libnetwork/cmd/diagnostic/daemon.json -->
# sources/cloud-native/moby/daemon/libnetwork/cmd/diagnostic/daemon.json

## Purpose
Provides a minimal daemon configuration for libnetwork diagnostic scenarios.

## Important APIs, Types, And Functions
The JSON enables `"debug": true` and sets `"network-diagnostic-port": 2000`.

## Control Flow
There is no executable flow. Docker daemon startup reads this file when used as configuration.

## State And Persistence
It configures daemon runtime behavior by enabling diagnostics on port 2000 and debug logging.

## Dependencies And Integration Points
Paired with the diagnostic command in the same folder, which defaults to port 2000 and calls diagnostic HTTP endpoints.

## Risks And Test Signals
Using this config in a real environment exposes diagnostics on a known port and increases logging verbosity. No tests are associated with the JSON itself.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/libnetwork/cmd/diagnostic/daemon.json -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/libnetwork/cmd/diagnostic/main.go -->
# sources/cloud-native/moby/daemon/libnetwork/cmd/diagnostic/main.go

## Purpose
Command-line diagnostic client for libnetwork NetworkDB tables. It checks daemon readiness, fetches cluster/network peers, dumps service-discovery or overlay peer tables, identifies orphan entries, and can optionally delete orphaned entries.

## Important APIs, Types, And Functions
Flags include `-ip`, `-port`, `-net`, `-t`, `-r`, `-a`, and `-v`. URL templates target `/ready`, `/joinnetwork`, `/leavenetwork`, `/clusterpeers`, `/networkpeers`, `/gettable`, and `/deleteentry`. `httpIsOk` validates readiness responses. `fetchNodePeers` decodes `diagnostic.TablePeersResult`. `fetchTable` decodes table entries, base64-decodes values, unmarshals `libnetwork.EndpointRecord` or `overlay.PeerRecord`, and optionally remediates.

## Control Flow
`main` parses flags, blocks disruptive join/leave unless `DIND_CLIENT` is set, checks readiness, optionally joins the target network, fetches peers, dumps the selected table, prompts before deletion when remediation is requested, and leaves the network if it joined.

## State And Persistence
Read-only by default. With `-r`, it can delete NetworkDB entries through daemon diagnostic endpoints after an exact `Yes` confirmation.

## Dependencies And Integration Points
Depends on libnetwork diagnostic HTTP result types, endpoint protobuf decoding, overlay peer decoding, and containerd logging.

## Risks And Test Signals
Uses unauthenticated HTTP URLs from flags and has potentially disruptive remediation. Error handling is fatal and exits the process. No tests are included in this subset.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/libnetwork/cmd/diagnostic/main.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/libnetwork/cmd/networkdb-test/Dockerfile -->
# sources/cloud-native/moby/daemon/libnetwork/cmd/networkdb-test/Dockerfile

## Purpose
Builds a tiny Alpine-based container image for running a `testMain` binary used by NetworkDB tests or diagnostics.

## Important APIs, Types, And Functions
The Dockerfile starts from `alpine`, installs `curl`, copies `testMain` into `/app/`, sets `WORKDIR app`, and uses `/app/testMain` as the entrypoint.

## Control Flow
Image build installs dependencies and copies the binary. Container start executes the test binary directly.

## State And Persistence
No persistent state beyond image layers. Runtime state depends on `testMain`.

## Dependencies And Integration Points
Requires an external `testMain` build artifact in the Docker build context. `curl` suggests the binary or tests interact with HTTP endpoints.

## Risks And Test Signals
The `WORKDIR app` path is relative and resolves under the current root as `/app` after creation/copy behavior; the absolute entrypoint avoids ambiguity. No tests are included here, and build success depends on the binary existing.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/libnetwork/cmd/networkdb-test/Dockerfile -->
