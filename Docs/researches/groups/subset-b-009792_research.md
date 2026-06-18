# subset-b-009792 research

Grouped research for the rclone pacer, plugin, pool, proxy, random, ranges, readers, rest, system integration, transform, version, librclone, entrypoint, and selected VFS directory files.

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/lib/pacer/pacers.go -->
## sources/user-network-fs/rclone/lib/pacer/pacers.go

Purpose: defines pacing calculators used by rclone's `lib/pacer` package to choose delay durations after successful calls, retryable failures, and explicit retry-after errors. The file contains reusable option types (`MinSleep`, `MaxSleep`, `DecayConstant`, `AttackConstant`, `Burst`) and three concrete calculators: `Default`, `GoogleDrive`, and `S3`, plus `ZeroDelayCalculator` and `AzureIMDS`.

Important APIs and control flow: `NewDefault`, `NewGoogleDrive`, `NewS3`, and `NewAzureIMDS` construct calculators with defaults and apply typed options. Each calculator implements `Calculate(state State) time.Duration`, consuming `State.SleepTime`, `State.ConsecutiveRetries`, and `State.LastError`. `Default` uses retry-after when present, exponential attack on retries, and decayed sleep on success. `GoogleDrive` adds a `rate.Limiter` for successful calls and randomized truncated exponential backoff for retries. `S3` allows zero delay during healthy operation while using `minSleep`/`maxSleep` on failures. `AzureIMDS` follows Azure metadata-service retry guidance with capped additive backoff.

State, dependencies, and integration: calculator instances hold only tuning fields and, for Google Drive, a limiter. They depend on `math/rand`, `time`, `golang.org/x/time/rate`, and package-level helpers/types from `pacer` such as `State` and `IsRetryAfter`. Integration is indirect through the main Pacer implementation, which invokes `Calculate` between calls.

Risks and test signals: the random backoff uses package `math/rand`, which is fine for scheduling jitter but not security. Option updates rebuild the Google Drive limiter, so changing `MinSleep`/`Burst` resets rate state. Shifting durations by user-controlled constants can overflow if absurd values are supplied, though normal configuration bounds likely prevent this. This file is not directly tested in the requested set; it is covered by broader pacer tests outside the group.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/lib/pacer/pacers.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/lib/pacer/tokens.go -->
## sources/user-network-fs/rclone/lib/pacer/tokens.go

Purpose: provides a minimal token dispenser for bounding concurrency. It is intentionally smaller than a full semaphore wrapper and exposes blocking `Get`/`Put` operations over a buffered channel.

Important APIs and control flow: `TokenDispenser` owns `tokens chan struct{}`. `NewTokenDispenser(n)` constructs a channel with capacity `n` and pre-fills it with `n` tokens. `Get()` receives from the channel and blocks when no token is available. `Put()` sends a token back and blocks if the channel is already full.

State, dependencies, and integration: all state is the channel occupancy. There are no external package dependencies. The type integrates wherever rclone needs simple fixed-width admission control, especially code paths that prefer blocking semantics over context-aware acquisition.

Risks and test signals: `Put` can deadlock if called more often than `Get`; `Get` can block forever if tokens are leaked; there is no context cancellation. `NewTokenDispenser(0)` creates a permanently blocking dispenser. The paired test verifies initial fill and channel length changes for a normal size.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/lib/pacer/tokens.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/lib/pacer/tokens_test.go -->
## sources/user-network-fs/rclone/lib/pacer/tokens_test.go

Purpose: unit-tests the simple channel-backed `TokenDispenser` implementation.

Important APIs and control flow: `TestTokenDispenser` constructs a dispenser with five tokens, asserts the buffered channel length is five, calls `Get`, asserts length drops to four, calls `Put`, and asserts length returns to five.

State, dependencies, and integration: the test reaches into the unexported `tokens` channel because it is in package `pacer`, so it validates implementation state directly rather than using only public behavior. It depends on `testing` and `stretchr/testify/assert`.

Risks and test signals: the test confirms basic accounting but not blocking behavior, deadlock scenarios, over-release behavior, or zero/negative sizes. It is a smoke test for fixed-capacity channel initialization and one acquire/release cycle.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/lib/pacer/tokens_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/lib/plugin/package.go -->
## sources/user-network-fs/rclone/lib/plugin/package.go

Purpose: package-level documentation for rclone's optional Go plugin loader. It explains how out-of-tree storage backends can be compiled as `go build -buildmode=plugin` artifacts and loaded through `RCLONE_PLUGIN_PATH`.

Important APIs and control flow: this file declares package `plugin` only. The operational loader is in `plugin.go` behind Linux/macOS build tags. The docs specify the expected file naming convention `librcloneplugin_NAME.so` and require plugin packages to use package name `main`.

State, dependencies, and integration: there is no runtime state. The file keeps unsupported platforms buildable by providing a package file even when the real plugin loader is excluded by build tags. It integrates with the entrypoint and library builds through blank imports of `github.com/rclone/rclone/lib/plugin`.

Risks and test signals: plugin loading is platform- and toolchain-sensitive; Go plugins are not supported everywhere and are excluded for `gccgo` by the implementation file. There are no tests in the requested set for plugin discovery or failed loads.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/lib/plugin/package.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/lib/plugin/plugin.go -->
## sources/user-network-fs/rclone/lib/plugin/plugin.go

Purpose: implements runtime loading of Go backend plugins on supported platforms. The file is active for `(darwin || linux) && !gccgo`.

Important APIs and control flow: all behavior runs in `init()`. It reads `RCLONE_PLUGIN_PATH`; if empty, it returns. Otherwise it reads the directory, filters entries whose names start with `librcloneplugin_` and end with `.so`, and calls `plugin.Open` for each. Directory-read and plugin-open failures are printed to stderr and do not abort process startup.

State, dependencies, and integration: it uses `os`, `filepath`, Go's standard `plugin` package, and string filtering. It has no exported API and relies on blank imports from `rclone.go`, `librclone`, and gomobile code so the initializer runs before command/library use.

Risks and test signals: plugin initialization has process-wide side effects. It trusts every matching file in `RCLONE_PLUGIN_PATH`; loading arbitrary `.so` files is equivalent to executing code. Error reporting is stderr-only, which is appropriate for early init but difficult to test or observe programmatically. No tests in this group exercise plugin loading, naming, or unsupported-platform behavior.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/lib/plugin/plugin.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/lib/pool/pool.go -->
## sources/user-network-fs/rclone/lib/pool/pool.go

Purpose: implements a deterministic reusable byte-buffer pool with optional mmap allocation and an optional global memory semaphore. It is a lower-level resource manager used by transfer buffering and `pool.RW`.

Important APIs and control flow: `New(flushTime, bufferSize, poolSize, useMmap)` creates a `Pool`, selecting either `make([]byte, size)` or `mmap.Alloc`/`mmap.Free`. `Get` delegates to atomic `GetN(1)`, while `GetN(n)` acquires global memory capacity, removes cached buffers, allocates missing buffers, and retries with exponential sleep on allocation failure. `Put`/`PutN` validate buffer capacity, cache up to `poolSize`, free overflow, release memory quota, update `inUse`, and schedule the flusher. `Flush` frees all cached buffers. `flushAged` periodically frees the minimum idle fill seen during the previous interval.

State, dependencies, and integration: `Pool` protects `cache`, `minFill`, `inUse`, `alloced`, timer flags, and allocator functions with `mu`. `totalMemory` is a package-level `semaphore.Weighted` initialized once from `fs.ConfigInfo.MaxBufferMemory` and counts buffers in active use, not cached buffers. `Global()` lazily creates a standard 1 MiB buffer pool using `fs.GetConfig` and `UseMmap`.

Risks and test signals: returned buffers must have the original capacity or `Put` panics; callers must pair every `Get` with a `Put` to avoid leaked memory-quota permits. `GetN` requests quota for all `n` buffers even if some will come from cache, which limits active use conservatively but means cached memory is not globally counted. Tests cover get/put reuse order, flush aging, mmap paths, unreliable allocator retries, wrong-size panic, and `MaxBufferMemory` limiting.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/lib/pool/pool.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/lib/pool/pool_test.go -->
## sources/user-network-fs/rclone/lib/pool/pool_test.go

Purpose: validates `Pool` allocation, reuse, flush aging, mmap/non-mmap modes, failure retry behavior, and global memory limiting.

Important APIs and control flow: `testGetPut` checks `InUse`, `InPool`, and `Alloced` through several `Get`, `GetN`, `Put`, and `PutN` sequences, including pointer reuse order and overflow freeing. `makeUnreliable` replaces allocator/free functions to intermittently fail so retry/error logging paths are exercised. `testFlusher` uses short timers and manual `flushAged` calls to verify `minFill`-based eviction. `TestPoolMaxBufferMemory` resets package singleton state, sets `MaxBufferMemory`, then runs concurrent `Get`/`GetN` callers and asserts active buffers never exceed the configured limit.

State, dependencies, and integration: the test mutates global fs config and package globals (`totalMemoryInit`, `totalMemory`) and restores them afterward. It depends on `testy.SkipUnreliable` for flaky allocator/free simulation on some platforms.

Risks and test signals: these tests are strong signals for core pool invariants and resource accounting. They do not assert log output or exact retry timing. Because they manipulate package-level globals, they assume serial test execution around global memory tests.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/lib/pool/pool_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/lib/pool/reader_writer.go -->
## sources/user-network-fs/rclone/lib/pool/reader_writer.go

Purpose: implements `RW`, a pool-backed append-only in-memory FIFO that supports `io.Reader`, `io.Writer`, `io.ReaderFrom`, `io.WriterTo`, `io.Seeker`, `io.Closer`, and delayed read accounting. It is designed for buffering data through reusable pool pages while allowing reads and writes to run concurrently.

Important APIs and control flow: `NewRW(pool)` initializes state and a nonblocking write-signal channel. `Reserve(n)` preallocates enough pages for later writes. `Write` and `ReadFrom` append data page by page, growing from reserved pages or `Pool.Get`, updating `size` and `lastOffset`, and signalling waiters. `Read` and `WriteTo` consume from read offset `out`, fetch the current page with `readPage`, update accounting via `accountRead`, and return `io.EOF` when `out >= size`. `Seek` changes only read position and rejects invalid whence, negative positions, or seeking past written data. `WaitWrite(ctx)` waits for data, cancellation, or a one-second timeout. `Close` returns written and reserved pages to the pool.

State, dependencies, and integration: a mutex protects shared `pages`, `size`, `lastOffset`, and reserved pages during page selection and metadata changes. `account`, `accountOn`, `reads`, and `out` drive byte accounting, with `DelayAccounting` useful when initial rereads are hash/checksum passes. The type integrates with `io.Copy` through `ReadFrom` and `WriteTo`.

Risks and test signals: `out` is written without consistently holding `mu`, so the design supports one reader and one writer rather than arbitrary concurrent readers. `Reserve` is documented as safe only once. `Close` should be called to return buffers. Tests cover basic I/O, seeking errors, accounting errors/delay, page-boundary sizes, `ReadFrom`/`WriteTo`, and concurrent read/write patterns.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/lib/pool/reader_writer.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/lib/pool/reader_writer_test.go -->
## sources/user-network-fs/rclone/lib/pool/reader_writer_test.go

Purpose: validates the `RW` pool-backed reader/writer across simple operation, accounting, page boundaries, and concurrent producer/consumer usage.

Important APIs and control flow: `TestRW` builds small buffers with `ReadFrom`, checks EOF behavior, `Seek`, `Read`, `WriteTo`, writer error propagation, accounting callbacks, delayed accounting after N passes, and accounting-error propagation. `TestRWBoundaryConditions` iterates sizes and chunk sizes around page boundaries, combining `Write` or `ReadFrom` with `Read` or `WriteTo` to assert exact byte preservation and accounting totals. `TestRWConcurrency` starts writer and reader goroutines and uses `WaitWrite` to read as data arrives from pattern readers.

State, dependencies, and integration: the test uses a package-level `rwPool`, custom chunking reader/writer types, `readers.NewPatternReader`, random test data, and `sync.WaitGroup`. It checks `RW.Size`, returned byte counts, EOFs, and accounting side effects.

Risks and test signals: the tests give strong coverage for page-boundary correctness and the intended one-reader/one-writer concurrency model. They do not explicitly test `Reserve`, close-after-close behavior, multiple simultaneous readers, or races beyond normal `go test` unless run with `-race`.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/lib/pool/reader_writer_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/lib/proxy/http.go -->
## sources/user-network-fs/rclone/lib/proxy/http.go

Purpose: establishes outbound TCP connections through an HTTP or HTTPS proxy using the CONNECT method, optionally chained through another proxy dialer.

Important APIs and control flow: `HTTPConnectDial(network, addr, proxyURL, proxyDialer)` defaults the proxy dialer to `net.Dialer` when nil. If `proxyURL` is nil, it dials `addr` directly. Otherwise it adds a default port to the proxy host, dials the proxy, wraps the connection in TLS for `https` proxy URLs, writes a CONNECT request with optional Basic `Proxy-Authorization`, and reads the proxy response using `http.ReadResponse`. Only `200 OK` succeeds; all failure paths close the connection and wrap context into the error.

State, dependencies, and integration: there is no persistent state. Dependencies include `net`, `net/http`, `net/url`, `crypto/tls`, `bufio`, `base64`, and `golang.org/x/net/proxy`. It integrates with transport construction wherever rclone needs CONNECT tunneling and proxy chaining.

Risks and test signals: credentials are encoded using `proxyURL.User.String()`, which preserves URL escaping semantics and may differ from raw user/password expectations in unusual cases. TLS uses `ServerName` from hostname but otherwise default TLS settings. There are no tests in the requested set for direct dialing, auth header formation, TLS proxy behavior, or response parsing.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/lib/proxy/http.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/lib/proxy/socks.go -->
## sources/user-network-fs/rclone/lib/proxy/socks.go

Purpose: provides SOCKS5 dialing with optional inline username/password parsing.

Important APIs and control flow: `SOCKS5Dial(network, addr, socks5Proxy, proxyDialer)` defaults to `net.Dialer`, parses `socks5Proxy` as `[user[:password]@]host:port`, constructs a `proxy.Auth` when credentials are present, calls `proxy.SOCKS5("tcp", proxyAddress, proxyAuth, proxyDialer)`, and dials the target `addr` through the returned dialer.

State, dependencies, and integration: no state is retained. It uses simple string splitting plus `golang.org/x/net/proxy`, and integrates with rclone's network transport proxy selection.

Risks and test signals: parsing is intentionally simple and does not URL-decode credentials; usernames or passwords containing `@` or `:` are ambiguous. The SOCKS5 network parameter passed to the proxy server is hardcoded to `"tcp"`, while the final dial uses caller `network`. There are no tests in this group for auth parsing or connection errors.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/lib/proxy/socks.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/lib/random/random.go -->
## sources/user-network-fs/rclone/lib/random/random.go

Purpose: provides random strings for tests/user-friendly names and cryptographically strong URL-safe passwords.

Important APIs and control flow: `StringFn(n, randReader)` fills `n` bytes from a supplied reader and maps each byte into a repeating consonant/vowel/consonant/vowel/consonant/vowel/consonant/digit pattern. `String(n)` uses `crypto/rand.Reader`. `Password(bits)` rounds requested bits up to bytes, reads that many bytes from `crypto/rand`, verifies a full read, and returns raw URL-safe base64 without padding.

State, dependencies, and integration: functions are stateless. Dependencies include `crypto/rand`, `encoding/base64`, and `io`. `StringFn` accepts injected readers for deterministic/failure testing but panics on read failure because it is intended for non-password utility/test use.

Risks and test signals: `String` is explicitly not for passwords and its modulo mapping is biased. `Password` length is bit-count rounded up, so entropy is at least requested bits but output length follows base64 expansion. Tests cover output lengths and duplicate smoke checks.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/lib/random/random.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/lib/random/random_test.go -->
## sources/user-network-fs/rclone/lib/random/random_test.go

Purpose: validates random string and password helpers at the public API level.

Important APIs and control flow: `TestStringLength` checks `String(i)` returns exactly `i` bytes for sizes 0 through 99. `TestStringDuplicates` samples 100 eight-byte strings and asserts no duplicate in the sample. `TestPasswordLength` verifies base64 output length for requested bit sizes 0 through 128. `TestPasswordDuplicates` samples 100 64-bit passwords and asserts uniqueness in the sample.

State, dependencies, and integration: tests depend on real `crypto/rand` through the public helpers and use `testify/assert` and `require`. They do not use deterministic random readers.

Risks and test signals: duplicate tests are probabilistic smoke tests rather than formal distribution checks. The tests do not cover `StringFn` read failures or `Password` entropy source errors.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/lib/random/random_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/lib/ranges/ranges.go -->
## sources/user-network-fs/rclone/lib/ranges/ranges.go

Purpose: represents byte ranges and a sorted, coalesced set of present ranges. This is used by cache/download code to reason about which byte intervals are available, missing, or intersecting.

Important APIs and control flow: `Range` has `Pos`, `Size`, `End`, `IsEmpty`, `Clip`, and `Intersection`. `Ranges` is a slice kept sorted/coalesced by `Insert`, which finds an insertion point with `sort.Search`, merges overlaps or adjacency through `merge`, and removes redundant entries through `coalesce`. `Find` returns the next present or absent segment within a query plus a `next` range for iteration. `FindAll`, `Present`, `Intersection`, `Equal`, `Size`, and `FindMissing` build on `Find`.

State, dependencies, and integration: state is just value slices; no synchronization is provided. The package depends only on `sort`. Integration points include VFS cache/downloaders, where `Ranges` tracks downloaded or written spans.

Risks and test signals: callers must only mutate through `Insert` to preserve invariants. Negative positions/sizes are not explicitly rejected; empty ranges are ignored by insertion and treated as present in `Present`. Boundary behavior is subtle because adjacent ranges merge. Tests in this group extensively exercise insertion, coalescing, searching, intersections, equality, size, random inserts, and missing-range calculations.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/lib/ranges/ranges.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/lib/ranges/ranges_test.go -->
## sources/user-network-fs/rclone/lib/ranges/ranges_test.go

Purpose: provides comprehensive table-driven and randomized coverage for the `Range` and `Ranges` algorithms.

Important APIs and control flow: tests cover `End`, `IsEmpty`, `Clip`, single-range intersection, internal `merge`, `coalesce`, `Insert`, random insertion order, `Find`, `FindAll`, `Present`, `Ranges.Intersection`, `Equal`, `Size`, and `FindMissing`. Helpers such as `checkRanges` validate sorted/coalesced invariants and expected contents after operations.

State, dependencies, and integration: tests are in package `ranges`, so they can call unexported helpers like `merge`, `coalesce`, and `search`. Random insertion testing checks algorithm stability across shuffled ranges.

Risks and test signals: this is a strong signal for edge cases around adjacency, partial overlap, nil/empty ranges, and query segmentation. It does not add concurrency tests because the type is a plain slice and expected to be externally synchronized when shared.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/lib/ranges/ranges_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/lib/readers/context.go -->
## sources/user-network-fs/rclone/lib/readers/context.go

Purpose: wraps an `io.Reader` so reads fail promptly when a context is canceled or reaches a deadline.

Important APIs and control flow: `NewContextReader(ctx, r)` returns a `contextReader`. `Read(p)` first checks `ctx.Err()` and returns that error with zero bytes when set; otherwise it delegates to the underlying reader.

State, dependencies, and integration: state is the context and underlying reader. Dependencies are `context` and `io`. This wrapper integrates with long-running transfer reads where cancellation should be observed before attempting more I/O.

Risks and test signals: cancellation is only checked before each underlying `Read`; a blocking underlying read cannot be interrupted by this wrapper alone. The paired test verifies normal pattern-reader output and post-cancel `context.Canceled`.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/lib/readers/context.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/lib/readers/context_test.go -->
## sources/user-network-fs/rclone/lib/readers/context_test.go

Purpose: confirms `NewContextReader` delegates reads while active and returns the context error after cancellation.

Important APIs and control flow: the test wraps a `NewPatternReader(100)` with a cancellable context, reads three bytes and checks `{0,1,2}`, cancels, then reads again and expects zero bytes plus `context.Canceled`.

State, dependencies, and integration: dependencies are `context`, `testing`, and testify. It indirectly depends on `pattern_reader.go` for deterministic input.

Risks and test signals: it verifies pre-read cancellation checks but not deadlines, already-canceled contexts at construction, or underlying read blocking behavior.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/lib/readers/context_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/lib/readers/counting_reader.go -->
## sources/user-network-fs/rclone/lib/readers/counting_reader.go

Purpose: wraps an `io.Reader` and counts cumulative bytes successfully returned by `Read`.

Important APIs and control flow: `NewCountingReader(in)` returns `*CountingReader`. `Read(b)` delegates to `in.Read(b)`, adds `n` to an internal `uint64`, and returns the original `(n, err)`. `BytesRead()` exposes the total.

State, dependencies, and integration: state is the underlying reader and count. There is no synchronization, so it is for single-reader use or externally synchronized use. It depends only on `io`.

Risks and test signals: reads that return `n > 0` with an error still count those bytes, matching Go `io.Reader` convention. There is no direct test in this requested set, so behavior is simple but unverified here.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/lib/readers/counting_reader.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/lib/readers/error.go -->
## sources/user-network-fs/rclone/lib/readers/error.go

Purpose: provides a tiny `io.Reader` implementation that always fails with a configured error.

Important APIs and control flow: `ErrorReader{Err: err}` implements `Read(p)` by returning `(0, Err)` without touching `p`.

State, dependencies, and integration: state is only the stored error. It has no imports. It is useful for tests or adapter paths that need an `io.Reader` placeholder representing a prior failure.

Risks and test signals: if `Err` is nil, `Read` returns `(0, nil)`, which can cause callers to spin because it violates the useful progress convention. The paired test covers a non-nil error.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/lib/readers/error.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/lib/readers/error_test.go -->
## sources/user-network-fs/rclone/lib/readers/error_test.go

Purpose: unit-tests `ErrorReader`.

Important APIs and control flow: `TestErrorReader` creates a sentinel `errors.New("boom")`, reads into a buffer, and asserts the same error and zero bytes are returned.

State, dependencies, and integration: dependencies are `errors`, `testing`, and testify. The test is a direct package-level check.

Risks and test signals: it covers the intended non-nil-error path only. It does not cover nil error behavior.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/lib/readers/error_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/lib/readers/fakeseeker.go -->
## sources/user-network-fs/rclone/lib/readers/fakeseeker.go

Purpose: adapts a non-seekable `io.Reader` into an `io.ReadSeeker` for code that only needs to seek before reading, commonly to inspect or advertise a known length.

Important APIs and control flow: `NewFakeSeeker(in, length)` returns `in` unchanged if it already implements `io.ReadSeeker`; otherwise it returns `*FakeSeeker`. `Seek` supports standard whence values only before reading starts and records the virtual offset. `Read` fails if the first read is attempted from a nonzero offset, delegates to `in.Read`, marks the stream as read once bytes are returned, and stores the first read error in `readErr`; future `Read` or `Seek` return that stored error.

State, dependencies, and integration: state includes virtual `length`, `offset`, `read` flag, and sticky `readErr`. Dependencies are `errors`, `fmt`, and `io`. It integrates with APIs that require `io.ReadSeeker` but can tolerate only pre-read length seeking.

Risks and test signals: after EOF, all later operations return EOF. There is no synchronization. Seeking forward before reading makes the stream unreadable unless seeking back to zero. Tests cover pass-through, allowed seeks, invalid whence, negative positions, nonzero read failure, post-read seek failure, and sticky EOF.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/lib/readers/fakeseeker.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/lib/readers/fakeseeker_test.go -->
## sources/user-network-fs/rclone/lib/readers/fakeseeker_test.go

Purpose: validates the constraints and sticky-error behavior of `FakeSeeker`.

Important APIs and control flow: `TestFakeSeeker` verifies that real `io.ReadSeeker` inputs pass through unchanged, virtual seeking works before reads, reads from nonzero offsets fail, invalid whence and negative positions fail, reading from zero succeeds, and seeking after reading fails. `TestFakeSeekerError` reads to EOF and verifies subsequent read/seek return EOF.

State, dependencies, and integration: tests use `bytes.Buffer`, `bytes.Reader`, `io`, and testify. An interface assertion confirms `*FakeSeeker` implements `io.ReadSeeker`.

Risks and test signals: the tests clearly define the adapter's intentionally limited seek semantics. They do not test short reads with non-EOF errors or concurrent access.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/lib/readers/fakeseeker_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/lib/readers/gzip.go -->
## sources/user-network-fs/rclone/lib/readers/gzip.go

Purpose: wraps `gzip.Reader` so closing the gzip stream also closes the underlying `io.ReadCloser`.

Important APIs and control flow: `NewGzipReader(in)` constructs a `gzip.Reader` over `in` and returns `*gzipReader`. `Close()` closes the gzip reader first and the underlying stream second; it returns the underlying close error if present, otherwise the gzip close error.

State, dependencies, and integration: `gzipReader` embeds `*gzip.Reader` and stores `in io.ReadCloser`. Dependencies are `compress/gzip` and `io`. This integrates with transfer paths that wrap compressed HTTP or file bodies and need deterministic resource cleanup.

Risks and test signals: if `gzip.NewReader` fails, the underlying input is not closed by this function; caller retains ownership. Error precedence favors the underlying stream close. The test verifies decompression and underlying close invocation.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/lib/readers/gzip.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/lib/readers/gzip_test.go -->
## sources/user-network-fs/rclone/lib/readers/gzip_test.go

Purpose: tests gzip decompression and close propagation for `NewGzipReader`.

Important APIs and control flow: the test compresses random test data into a buffer, wraps it with a custom `checkClose` read closer, reads all decompressed data through `NewGzipReader`, compares it to the original string, then closes the gzip reader and asserts the underlying closer was called.

State, dependencies, and integration: dependencies include `compress/gzip`, `bytes`, `io`, `lib/random`, and testify. The custom closer records state in a boolean.

Risks and test signals: it covers the happy path and close propagation, but not invalid gzip input or close-error precedence.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/lib/readers/gzip_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/lib/readers/limited.go -->
## sources/user-network-fs/rclone/lib/readers/limited.go

Purpose: combines `io.LimitedReader` with `io.Closer` so callers can impose a byte limit while retaining close semantics.

Important APIs and control flow: `NewLimitedReadCloser(rc, limit)` returns `rc` unchanged for negative limits; otherwise it returns `*LimitedReadCloser` with an `io.LimitedReader{R: rc, N: limit}` and the original closer. `Close()` closes the underlying closer, but if close returns an error after all limited bytes were read (`N == 0`), it logs and suppresses that error.

State, dependencies, and integration: state is the embedded limited reader and closer. It depends on `io` and rclone `fs` logging. It integrates with partial-response readers where an underlying stream may complain on close even after the caller read exactly the intended content.

Risks and test signals: suppressing close errors when `N == 0` is a deliberate policy that could hide transport issues after complete reads. There is no direct test in the requested set.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/lib/readers/limited.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/lib/readers/noclose.go -->
## sources/user-network-fs/rclone/lib/readers/noclose.go

Purpose: hides `io.Closer` from an `io.Reader` so downstream code such as `http.NewRequest` cannot upgrade and close the original body unexpectedly.

Important APIs and control flow: `NoCloser(in)` returns nil unchanged, returns `in` unchanged when it does not implement `io.Closer`, and otherwise wraps it in an unexported `noClose` that exposes only `Read`. `noClose.Read` delegates directly to the underlying reader.

State, dependencies, and integration: state is a single underlying reader. It depends only on `io`. The REST client uses this wrapper when constructing request bodies.

Risks and test signals: callers that actually need close propagation must not use this wrapper. The test covers nil, non-closer pass-through, closer hiding, and delegated read errors.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/lib/readers/noclose.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/lib/readers/noclose_test.go -->
## sources/user-network-fs/rclone/lib/readers/noclose_test.go

Purpose: validates that `NoCloser` removes close capability only when necessary.

Important APIs and control flow: the test asserts nil remains nil, a read-only reader is returned unchanged, a read-closer is wrapped, the wrapper no longer satisfies `io.Closer`, and reading through the wrapper returns the underlying read error.

State, dependencies, and integration: test fixtures implement small `readOnly` and `readClose` types. Dependencies are `errors`, `io`, `testing`, and testify.

Risks and test signals: confirms type-level behavior and delegation. It does not test interactions with `http.NewRequest`, which is the main integration motivation.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/lib/readers/noclose_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/lib/readers/noseeker.go -->
## sources/user-network-fs/rclone/lib/readers/noseeker.go

Purpose: adapts an `io.Reader` to an `io.ReadSeeker` whose `Seek` always fails. This can satisfy interfaces while explicitly preventing seeking.

Important APIs and control flow: `NoSeeker` embeds `io.Reader`. `Seek` ignores offset and whence and returns `(0, errCantSeek)`.

State, dependencies, and integration: state is the embedded reader. Dependencies are `errors` and `io`. It integrates with code paths that require a read seeker but can handle seek failures.

Risks and test signals: callers may treat `io.Seeker` support as a guarantee of usable seeking, so this adapter should only be used where explicit seek failure is accepted. The paired test verifies read delegation and seek error.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/lib/readers/noseeker.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/lib/readers/noseeker_test.go -->
## sources/user-network-fs/rclone/lib/readers/noseeker_test.go

Purpose: tests `NoSeeker`'s read delegation and intentional seek failure.

Important APIs and control flow: `TestNoSeeker` reads four bytes from a `bytes.Buffer` through `NoSeeker` and checks the bytes, then calls `Seek` and expects `errCantSeek`. Interface assertions confirm `NoSeeker` satisfies both `io.Reader` and `io.Seeker`.

State, dependencies, and integration: dependencies are `bytes`, `io`, `testing`, and testify.

Risks and test signals: this is a direct smoke test. It does not cover nil embedded readers or caller behavior after a failed seek.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/lib/readers/noseeker_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/lib/readers/pattern_reader.go -->
## sources/user-network-fs/rclone/lib/readers/pattern_reader.go

Purpose: creates deterministic byte streams for tests and integrity checks without storing large buffers.

Important APIs and control flow: `NewPatternReader(length)` returns an `io.ReadSeeker`. `Read(p)` fills bytes with a repeating sequence modulo 251 until `offset >= length`, then returns `io.EOF`. `Seek` supports standard whence values, rejects invalid whence and negative absolute positions, and recalculates the next byte from `abs % 251`.

State, dependencies, and integration: state is `offset`, total `length`, and current byte `c`. It depends on `errors` and `io`. It is used by pool/RW and context-reader tests to generate predictable content.

Risks and test signals: seeking past `length` is allowed and will cause immediate EOF on read, which matches some reader conventions but not all. No synchronization is provided. Tests cover empty, fixed-length reads, byte sequence, valid seeks, and seek errors.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/lib/readers/pattern_reader.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/lib/readers/pattern_reader_test.go -->
## sources/user-network-fs/rclone/lib/readers/pattern_reader_test.go

Purpose: validates deterministic pattern generation and seek behavior.

Important APIs and control flow: `TestPatternReader` checks zero-length and ten-byte streams, EOF behavior, and expected byte values. `TestPatternReaderSeek` reads a 1024-byte reference, validates modulo 251 content, seeks from start/current/end, verifies subsequent reads match the reference slices, and checks invalid whence and negative seek errors.

State, dependencies, and integration: dependencies are `io`, `testing`, and testify. The test uses full reads as reference data for later seek checks.

Risks and test signals: strong coverage for deterministic output and seek offset recalculation. It does not test seeking beyond the end.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/lib/readers/pattern_reader_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/lib/readers/readfill.go -->
## sources/user-network-fs/rclone/lib/readers/readfill.go

Purpose: reads as much as possible into a buffer until the buffer is full or the reader returns an error, without requiring an exact fill like `io.ReadFull`.

Important APIs and control flow: `ReadFill(r, buf)` loops while `n < len(buf)` and `err == nil`, reading into `buf[n:]` and accumulating bytes. It returns the final count and the last error, including `io.EOF` if EOF stopped the loop before the buffer filled.

State, dependencies, and integration: stateless helper depending only on `io`. It integrates with callers that want a best-effort block read and need to retain partial bytes plus terminal error.

Risks and test signals: a reader returning `(0, nil)` repeatedly would cause an infinite loop. This is the same class of misuse many read loops must guard against, but no guard exists here. Tests cover empty, partial, and full buffer reads with a one-byte-at-a-time reader.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/lib/readers/readfill.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/lib/readers/readfill_test.go -->
## sources/user-network-fs/rclone/lib/readers/readfill_test.go

Purpose: tests `ReadFill` for EOF-before-data, partial fill with EOF, and full fill without error.

Important APIs and control flow: a custom `byteReader` emits decreasing byte values one byte per read until reaching EOF. `TestReadFill` verifies buffer contents and returned `(n, err)` for zero, three, and eight available bytes against a five-byte target buffer.

State, dependencies, and integration: dependencies are `io`, `testing`, and testify. The test intentionally leaves unread portions of the buffer unchanged for partial reads.

Risks and test signals: verifies core semantics but not the pathological `(0, nil)` reader case.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/lib/readers/readfill_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/lib/readers/repeatable.go -->
## sources/user-network-fs/rclone/lib/readers/repeatable.go

Purpose: implements a caching `io.ReadSeeker` that allows seeking within bytes already read from an underlying reader. It avoids rereading from the source while supporting limited replay.

Important APIs and control flow: `Read` serves from cache when `i < len(b)`; when positioned at cache end, it reads from `in`, appends any bytes read to cache, and advances `i`. `Seek` supports start/current/end relative to the cache length, rejects invalid whence, negative positions, and offsets beyond the cached bytes. Constructors create unsized, preallocated, limited, and caller-buffer-backed readers.

State, dependencies, and integration: `RepeatableReader` stores `in`, current index `i`, cached bytes `b`, and a mutex for concurrent method calls. It depends on `errors`, `io`, and `sync`. It integrates with upload/signing paths that need to replay already consumed request bodies without buffering the entire unknown stream in advance.

Risks and test signals: seeking cannot move beyond cached bytes, so callers must read before rewinding. Cache grows with all bytes read unless a limit reader is used. The mutex serializes operations but does not make the underlying reader itself independently safe for external concurrent use. Tests cover read, EOF, rewinds, partial reads, seek errors, and read-after-seek.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/lib/readers/repeatable.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/lib/readers/repeatable_test.go -->
## sources/user-network-fs/rclone/lib/readers/repeatable_test.go

Purpose: validates `RepeatableReader` caching and seek rules.

Important APIs and control flow: `TestRepeatableReader` reads an entire buffer, checks EOF, seeks back to start and rereads, checks partial sequential reads, verifies seeking past cache, negative seek, and invalid whence errors, then performs current/end-relative seeks and reads a slice spanning cached and newly read data.

State, dependencies, and integration: dependencies are `bytes`, `io`, `testing`, and testify. The test uses small fixed data to make cache positions clear.

Risks and test signals: covers essential cache/seek semantics. It does not test size-limited constructors, buffer-backed constructors, or concurrency.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/lib/readers/repeatable_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/lib/rest/headers.go -->
## sources/user-network-fs/rclone/lib/rest/headers.go

Purpose: extracts full object size from HTTP response headers.

Important APIs and control flow: `ParseSizeFromHeaders(headers)` defaults to `-1`. It first parses `Content-Length` when present. It then checks `Content-Range`; if absent, the content length result is returned. When `Content-Range` is present, it must start with `bytes ` and contain `/`; the value after slash is parsed and returned as the full size. Invalid data returns `-1`.

State, dependencies, and integration: stateless helper depending on `net/http`, `strconv`, and `strings`. It integrates with REST backends that need to infer total object size from range responses or normal responses.

Risks and test signals: wildcard total sizes such as `bytes 0-1/*` return `-1`. The parser does not validate the left-hand byte range, only the unit and total. Tests cover content length, valid/invalid content range, unit mismatch, wildcard totals, and `bytes */size`.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/lib/rest/headers.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/lib/rest/headers_test.go -->
## sources/user-network-fs/rclone/lib/rest/headers_test.go

Purpose: table-tests `ParseSizeFromHeaders`.

Important APIs and control flow: `TestParseSizeFromHeaders` builds headers with optional `Content-Length` and `Content-Range` values and asserts the returned full size or `-1`.

State, dependencies, and integration: dependencies are `net/http`, `testing`, and testify. It uses a compact table covering absent headers, valid length, invalid range, valid range overriding content length, unsupported units, wildcard total, and unsatisfied-range form.

Risks and test signals: the test confirms intended precedence and failure behavior. It does not test malformed numbers beyond wildcard or missing slash cases.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/lib/rest/headers_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/lib/rest/rest.go -->
## sources/user-network-fs/rclone/lib/rest/rest.go

Purpose: implements rclone's reusable REST client wrapper around `http.Client`, adding root URLs, default/extra headers, signing, redirects, multipart uploads, JSON/XML helpers, and response/error handling.

Important APIs and control flow: `NewClient` initializes `Client` with a default error handler. Setter methods update root URL, headers, signer, basic auth, and cookies under a mutex. `Call(ctx, opts)` validates options/root URL, builds the URL and request, wraps bodies with `readers.NoCloser`, handles content length/range/type, transfer encoding, trailers, open options, basic auth, redirect policy, signer invocation, HTTP execution, non-2xx error handling, and no-response draining. `CallJSON`/`CallXML` use `callCodec`, which marshals request bodies, optionally builds multipart bodies with `MultipartUpload`, calls `Call`, and decodes responses. `DecodeJSON`/`DecodeXML` drain and close bodies. Redirect helpers build client copies with specific `CheckRedirect` policies.

State, dependencies, and integration: `Client` stores `*http.Client`, root URL, default headers, error handler, and signer protected by `sync.RWMutex`. It depends on encoding packages, `multipart`, `http`, rclone `fs`, and `readers`. Integration is broad across rclone backends as the common HTTP API shim.

Risks and test signals: `Call` manually unlocks/relocks around signer and `Do`, which avoids blocking setters but is delicate; copied header maps prevent mutation races. `MultipartUpload` starts goroutines and relies on context cancellation/reader closure. `opts.ContentLength` may be mutated when multipart overhead is added. Tests in this subset cover only URL and header helpers, not `Call`, redirects, multipart, signer, or error handling.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/lib/rest/rest.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/lib/rest/url.go -->
## sources/user-network-fs/rclone/lib/rest/url.go

Purpose: provides URL path helpers for joining escaped paths and applying stricter percent encoding.

Important APIs and control flow: `URLJoin(base, path)` parses `path` as a URL reference and resolves it against `base`, returning parse errors with context. `URLPathEscape(in)` uses `url.URL{Path: in}.String()` to escape path content while preserving path semantics. `URLPathEscapeAll(in)` iterates bytes and percent-encodes every byte except RFC 3986 unreserved characters and `/`.

State, dependencies, and integration: stateless helpers depending on `net/url`, `fmt`, and `strings`. They integrate with REST backends constructing object URLs where path escaping rules vary.

Risks and test signals: `URLJoin` treats absolute URLs and absolute paths according to normal URL resolution, which can replace base paths. `URLPathEscape` has Go URL quirks such as colon handling; `URLPathEscapeAll` operates on UTF-8 bytes, producing percent-encoded UTF-8 for non-ASCII. Tests cover join cases, colon/percent/space escaping, and stricter all-character escaping.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/lib/rest/url.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/lib/rest/url_test.go -->
## sources/user-network-fs/rclone/lib/rest/url_test.go

Purpose: validates URL joining and escaping helpers against expected URL strings.

Important APIs and control flow: `TestURLJoin` table-tests base/path combinations, including relative paths, parent directories, absolute paths, absolute URLs, percent characters, and colon parsing. `TestURLPathEscape` checks path escaping quirks. `TestURLPathEscapeAll` verifies RFC-unreserved characters remain literal while spaces, colon, percent, dollar, question mark, and UTF-8 umlaut bytes are percent-encoded.

State, dependencies, and integration: dependencies are `fmt`, `net/url`, `testing`, and testify.

Risks and test signals: good coverage for expected escaping behavior. It does not test invalid percent escape sequences beyond the colon parse case.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/lib/rest/url_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/lib/sdactivation/sdactivation_stub.go -->
## sources/user-network-fs/rclone/lib/sdactivation/sdactivation_stub.go

Purpose: provides systemd socket activation stubs on Windows and Plan 9, where the upstream go-systemd activation package is not buildable or useful.

Important APIs and control flow: `ListenersWithNames()` returns an empty map and nil error. `Listeners()` returns nil slice and nil error. Both match the real package API without doing work.

State, dependencies, and integration: there is no state. It depends only on `net` for type signatures. It allows cross-platform imports of `lib/sdactivation` without conditional caller code.

Risks and test signals: callers cannot distinguish unsupported platform from "no activated sockets" except through build target knowledge. No tests are included in the requested set.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/lib/sdactivation/sdactivation_stub.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/lib/sdactivation/sdactivation_unix.go -->
## sources/user-network-fs/rclone/lib/sdactivation/sdactivation_unix.go

Purpose: wraps `github.com/coreos/go-systemd/v22/activation` for non-Windows, non-Plan-9 platforms.

Important APIs and control flow: `ListenersWithNames()` delegates directly to `activation.ListenersWithNames()`. `Listeners()` delegates to `activation.Listeners()`.

State, dependencies, and integration: there is no local state. It depends on `net` for signatures and go-systemd activation for behavior. It integrates with server commands that can be launched through systemd socket activation.

Risks and test signals: all semantics and environment parsing are inherited from go-systemd. The wrapper exists primarily for platform compatibility. No tests are present in this subset.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/lib/sdactivation/sdactivation_unix.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/lib/structs/structs.go -->
## sources/user-network-fs/rclone/lib/structs/structs.go

Purpose: reflection utilities for copying public struct fields across similar structs or applying default values without copying unexported internals.

Important APIs and control flow: `SetFrom(a, b)` expects pointers to structs, iterates fields of `b`, finds a same-named field in `a`, and assigns it when both values are valid/settable and `b`'s field type is assignable to `a`'s field type. `SetDefaults(a, b)` expects same-kind struct pointers and copies every settable field by index from `b` to `a`.

State, dependencies, and integration: stateless helpers depending on `reflect`. Integration points include generated cloud SDK structs and `http.Transport`-like structs where unexported mutexes prevent simple struct assignment.

Risks and test signals: functions panic if called with non-pointers, nil pointers, or non-struct elements. `SetDefaults` assumes same layout/type and does not check assignability by name. Tests cover copying defaults from `http.DefaultTransport` and name/type-filtered copying in both directions.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/lib/structs/structs.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/lib/structs/structs_test.go -->
## sources/user-network-fs/rclone/lib/structs/structs_test.go

Purpose: tests reflection copying helpers.

Important APIs and control flow: `TestSetDefaults` copies from `http.DefaultTransport` into a new transport and compares representative public fields, including function pointers by formatted pointer string. `TestSetFrom` copies matching assignable fields from `bType` to `aType`, leaving unmatched and differently typed fields unchanged. `TestSetFromReversed` validates the reverse direction.

State, dependencies, and integration: dependencies include `fmt`, `net/http`, `testing`, and testify. Tests use local struct types with same/different field names and types.

Risks and test signals: confirms expected public-field copying. It does not cover panic cases or embedded/anonymous fields.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/lib/structs/structs_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/lib/systemd/doc.go -->
## sources/user-network-fs/rclone/lib/systemd/doc.go

Purpose: package documentation for systemd service-manager communication utilities.

Important APIs and control flow: no functions are declared here; runtime behavior is in `notify.go`.

State, dependencies, and integration: no state or imports. The package integrates with commands that notify systemd of readiness, stopping, or status.

Risks and test signals: no testable behavior in this file.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/lib/systemd/doc.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/lib/systemd/notify.go -->
## sources/user-network-fs/rclone/lib/systemd/notify.go

Purpose: sends readiness, stopping, and status notifications to systemd.

Important APIs and control flow: `Notify()` sends `SdNotifyReady`, then returns a finalizer function that sends `SdNotifyStopping` exactly once. It also registers that finalizer with `atexit`, and the returned function unregisters it before finalizing. `UpdateStatus(status)` sends `STATUS=<status>` through `daemon.SdNotify`.

State, dependencies, and integration: `Notify` uses a local `sync.Once` and an atexit registration handle. Dependencies are go-systemd `daemon`, rclone `fs` logging, and rclone `lib/atexit`. It integrates with long-running commands under systemd.

Risks and test signals: docs warn `Notify` should generally be called once; multiple calls would create multiple atexit registrations. Errors are logged for ready/stopping but returned only for status updates. No tests in this subset exercise systemd notification behavior.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/lib/systemd/notify.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/lib/terminal/hidden_other.go -->
## sources/user-network-fs/rclone/lib/terminal/hidden_other.go

Purpose: non-Windows implementation of console hiding.

Important APIs and control flow: `HideConsole()` is a no-op on all non-Windows builds.

State, dependencies, and integration: no state or imports. It preserves a cross-platform API for callers that hide the console on Windows.

Risks and test signals: no behavior to test. Correctness is build-tag selection.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/lib/terminal/hidden_other.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/lib/terminal/hidden_windows.go -->
## sources/user-network-fs/rclone/lib/terminal/hidden_windows.go

Purpose: Windows implementation of console hiding.

Important APIs and control flow: `HideConsole()` lazily looks up `GetConsoleWindow` from `kernel32.dll` and `ShowWindow` from `user32.dll`. If both procedures are available and a console window handle exists, it calls `ShowWindow(hwnd, 0)` to hide it.

State, dependencies, and integration: no persistent state. It depends on `golang.org/x/sys/windows`. It integrates with GUI/daemon scenarios that should hide an inherited console window.

Risks and test signals: return values from `ShowWindow` are ignored; failure is silent. Behavior is Windows-only and untested in this subset.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/lib/terminal/hidden_windows.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/lib/terminal/terminal.go -->
## sources/user-network-fs/rclone/lib/terminal/terminal.go

Purpose: central terminal utility package defining VT100 escape constants and selecting an output writer that supports or strips color appropriately.

Important APIs and control flow: constants define erase/move/title/color/style escape sequences. `Start()` runs once, reads global config, checks whether stdout is a terminal, and selects `Out` as either raw stdout, `colorable.NewColorable`, or `colorable.NewNonColorable` depending on platform, `TERM`, and `TerminalColorMode`. `WriteString` and `Write` lazily initialize and write to `Out`. `EnableColorsStdout()` asks colorable to enable native Windows VT support.

State, dependencies, and integration: package state is `once` and `Out io.Writer`. It depends on `os`, `runtime`, `sync`, `context`, `go-colorable`, and rclone `fs`. Build-specific files provide `IsTerminal` and related helpers. It integrates with progress/status output throughout rclone.

Risks and test signals: because `Start` is guarded by `sync.Once`, later config changes will not affect `Out`. Writes ignore write errors. No tests in this subset cover color mode or terminal detection.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/lib/terminal/terminal.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/lib/terminal/terminal_normal.go -->
## sources/user-network-fs/rclone/lib/terminal/terminal_normal.go

Purpose: non-JavaScript terminal operations backed by `golang.org/x/term`.

Important APIs and control flow: `GetSize()` calls `term.GetSize` on stdout and falls back to `80x25` on error. `IsTerminal(fd)` delegates to `term.IsTerminal`. `ReadPassword(fd)` delegates to `term.ReadPassword`. `WriteTerminalTitle(title)` writes the VT100 title sequence to stdout.

State, dependencies, and integration: no persistent state. Dependencies are `fmt`, `os`, and `x/term`. It integrates with terminal UI sizing, password prompts, and title updates.

Risks and test signals: terminal title output writes directly to stdout, not `terminal.Out`. Password reading and terminal sizing are environment-dependent. No tests are present in this subset.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/lib/terminal/terminal_normal.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/lib/terminal/terminal_unsupported.go -->
## sources/user-network-fs/rclone/lib/terminal/terminal_unsupported.go

Purpose: JavaScript/unsupported terminal implementation.

Important APIs and control flow: `GetSize()` returns `80x25`; `IsTerminal` always false; `ReadPassword` returns an error; `WriteTerminalTitle` is a no-op.

State, dependencies, and integration: no state. It imports `errors` only. Build tags keep terminal-dependent code compiling on JS targets.

Risks and test signals: password prompts cannot work on this target through this API. No tests are present in the requested set.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/lib/terminal/terminal_unsupported.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/lib/transferaccounter/transferaccounter.go -->
## sources/user-network-fs/rclone/lib/transferaccounter/transferaccounter.go

Purpose: provides a context-carried accumulator for server-side and other transfers that still need stats accounting.

Important APIs and control flow: `New(ctx, add)` creates a `TransferAccounter`, stores it in a derived context, and returns both. `Start` marks the accounter started. `Started` reports the flag. `Add(n)` calls the supplied `add` function and atomically increments `total`. `Reset()` reverses all accounted bytes by adding the negative total only if started. `Get(ctx)` returns the context accounter or a global no-op accounter when absent or ctx is nil.

State, dependencies, and integration: state includes a caller-provided add callback, atomic total, and non-atomic started flag. It depends on `context` and `sync/atomic`. Integration is through contexts passed along transfer operations.

Risks and test signals: `started` is not atomic, so concurrent `Start`/`Started` calls need external ordering. `Reset` does not clear `total` directly; it relies on `Add(-total)` to bring the atomic total back to zero. The global `nullAccounter` can have `started` set by tests/callers, which is harmless for no-op adds but shared state. Tests cover creation, start, add/reset, context lookup, nil/missing fallback, and no-op behavior.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/lib/transferaccounter/transferaccounter.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/lib/transferaccounter/transferaccounter_test.go -->
## sources/user-network-fs/rclone/lib/transferaccounter/transferaccounter_test.go

Purpose: tests context storage, byte accounting, reset behavior, and fallback no-op accounter.

Important APIs and control flow: `TestNew` creates an accounter with an add callback, checks initial not-started state, starts it, adds bytes, checks callback and internal total, then resets and expects totals to return to zero. `TestGet` covers retrieving an existing accounter, missing context values, and nil context. `TestNullAccounterBehavior` ensures no-op accounter calls do not panic and can be started.

State, dependencies, and integration: tests use a local integer accumulator and compare pointer identity for retrieved accounters. Dependencies are `context`, `testing`, and testify.

Risks and test signals: verifies main semantics. It does not test concurrent `Add` calls or reset races.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/lib/transferaccounter/transferaccounter_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/lib/transform/cmap.go -->
## sources/user-network-fs/rclone/lib/transform/cmap.go

Purpose: exposes selectable character maps and helpers for lossy character-map transformations in the name-transform feature.

Important APIs and control flow: `CharmapChoices` is an `fs.Enum`. `cmapChoices.Choices()` iterates `charmap.All`, keeps `*charmap.Charmap` entries, creates display names by replacing spaces with hyphens, records each charmap in the package `cmaps` map under its enum index, and returns the choices. `charmapByID` looks up a charmap by enum value. `encodeWithReplacement` maps each rune through the charmap, replacing unencodable runes with `_`. `toASCII` strips non-ASCII runes.

State, dependencies, and integration: global `cmaps` is protected by `lock`. This file depends on `fmt`, `strings`, `sync`, rclone `fs`, and `x/text/encoding/charmap`. It integrates with `transformPathSegment` for `ConvCharmap`, legacy ISO-8859-1, Windows-1252, Macintosh, and ASCII transforms.

Risks and test signals: `charmapByID` relies on `Choices()` having populated `cmaps`; enum parsing normally calls `Choices`, but direct use before choices could return nil. Tests in `transform_test.go` cover some charmap output through high-level path transforms, not this map population directly.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/lib/transform/cmap.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/lib/transform/gen_help.go -->
## sources/user-network-fs/rclone/lib/transform/gen_help.go

Purpose: go-generate helper for producing `transform.md` help text from the current transform choices, charmap choices, encoder masks, command descriptions, and generated examples. It is excluded from normal builds with `//go:build none`.

Important APIs and control flow: local `commands` and `example` structs back `commandList` and `examples`. `example.command()` formats an example `rclone convmv` invocation. `example.output()` sets transform options in a background context and runs `transform.Path`. `SprintList()` builds a markdown table, conversion mode list, charmap list, encoding mask list, and examples. `main()` writes the generated help to stdout or a path argument with a generated-file banner.

State, dependencies, and integration: depends on `context`, `fmt`, `os`, `strings`, rclone `fs`, `encoder`, and `transform`. It integrates through the `go:generate` directive in `transform.go`.

Risks and test signals: generated examples execute real transform code, so a transform behavior bug can be embedded into help. `os.Create` errors are fatal through `fs.Fatalf`; close errors are ignored. No direct tests are included.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/lib/transform/gen_help.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/lib/transform/options.go -->
## sources/user-network-fs/rclone/lib/transform/options.go

Purpose: parses and caches `--name-transform` options into internal transform descriptors.

Important APIs and control flow: `Transforming(ctx)` checks `fs.ConfigInfo.NameTransform`. `SetOptions(ctx, s...)` overwrites that config slice and forces parsing. `getOptions(ctx)` returns cached parsed transforms when the configured slice equals `cachedNameTransform`; otherwise it parses each string and updates the cache. `parse` strips optional `file,`, `dir,`, or `all,` tags, then parses a key or `key=value`. `requiresValue` marks transforms that require a value. `Algo` and `transformChoices` define all supported transform names.

State, dependencies, and integration: package cache state includes `cachedNameTransform`, `cachedOpt`, and `cacheLock`. The initial cache equality check is outside the lock, while updates are locked. It depends on `context`, `errors`, `slices`, `strings`, `sync`, and rclone `fs`. It integrates with `transform.Path`.

Risks and test signals: `strings.Split(s, "=")` rejects values containing `=`, which may limit regex/command/value transforms. Cache reads are not fully locked, so concurrent config changes could race unless higher-level config access is serialized. `ConvIndex` requires a value but is not implemented in `transform.go`. Tests cover high-level option parsing and tag behavior through `Path`.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/lib/transform/options.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/lib/transform/transform.go -->
## sources/user-network-fs/rclone/lib/transform/transform.go

Purpose: applies configured path/name transformations for rclone's `convmv` and name-transform support. It includes Unicode normalization, base64, prefix/suffix/trim/truncate, encoder/decoder, charmap, case, ASCII, URL, date, regex, and external command transforms.

Important APIs and control flow: `Help()` returns embedded generated help with the banner removed. `Path(ctx, s, isDir)` loads parsed options, skips file-only transforms for directories, applies directory-only transforms to parent paths for files, logs/counts no-retry errors, and refuses transforms that change the number of path separators. `transformPath` applies a transform to each path segment or only the base. `transformPathSegment` switches on `Algo` and performs the actual conversion. Helpers handle extension preservation, rune/byte truncation without splitting UTF-8, segment validation, time glob parsing, and external command invocation.

State, dependencies, and integration: depends on embedded `transform.md`, rclone `fs`, `fserrors`, `encoder`, `x/text` normalization/charmaps, `exec`, `regexp`, `url`, and time. It integrates with config via `options.go` and logs transformed paths through rclone logging.

Risks and test signals: `transformPath` preallocates `transformedSegments := make([]string, len(segments))` and then appends, which can insert leading empty segments before `path.Join`; tests may miss some all-segment paths. `regexp.MustCompile` can panic on invalid regex values. `command` executes an external binary with the path as an argument, a deliberate but high-risk feature. Validation prevents empty or slash-containing segments and reverts if separator count changes. Tests cover tag selection and representative transforms, but not every transform or error path.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/lib/transform/transform.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/lib/transform/transform_test.go -->
## sources/user-network-fs/rclone/lib/transform/transform_test.go

Purpose: high-level tests for path transformation option parsing and tag scoping.

Important APIs and control flow: `newOptions` sets transform options in a background context. Tests check plain path transforms, file-only and dir-only tags on files, all-tag behavior, file-only/dir-only tags on directories, and a table of representative transforms including prefix/suffix/trims, date-like options, truncation, base64, encoding/charmap, case conversion, ASCII stripping, URL escaping, normalization, and regex/command style cases.

State, dependencies, and integration: tests mutate global config in `context.Background()` through `SetOptions`, so they rely on isolated sequential behavior. Dependencies are `context`, `testing`, and testify.

Risks and test signals: good coverage for the public `Path` API and tag behavior. Because it is table-driven over selected cases, it may not catch all parser limitations, regex panic cases, or the segment-slice preallocation issue in every path shape.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/lib/transform/transform_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/lib/version/version.go -->
## sources/user-network-fs/rclone/lib/version/version.go

Purpose: adds, removes, and detects timestamp version suffixes in file names.

Important APIs and control flow: `splitExt` separates base and extension using `path.Ext`, with special handling so dotfiles like `.file` are treated as base with no extension. `Add(fileName, t)` formats time with `-v2006-01-02-150405.000`, replaces the millisecond dot with a dash, and inserts before extension. `Remove(fileName)` checks the end of the base for a version-length suffix, restores the millisecond dot for parsing, and returns parsed time plus filename without version; if parsing fails, it returns zero time and original filename. `Match` uses a regexp to find version-like substrings.

State, dependencies, and integration: stateless. Dependencies are `path`, `regexp`, `strings`, and `time`. It integrates with backup/versioning logic that stores old object names with timestamp suffixes.

Risks and test signals: `Match` is regex-based and accepts impossible dates such as month 99, while `Remove` requires parseable time. `Remove` targets the final version suffix before extension. Tests cover extension insertion, dotfiles, stacked versions, removal, invalid versions, and regex matching.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/lib/version/version.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/lib/version/version_test.go -->
## sources/user-network-fs/rclone/lib/version/version_test.go

Purpose: tests timestamp version insertion, removal, and matching.

Important APIs and control flow: `TestVersionAdd` checks insertion before extensions, stacked versions, unusual extensions, extensionless names, dotfiles, and empty names. `TestVersionRemove` validates parsed times rounded to milliseconds, restoring original names, removing only the last version suffix, and leaving malformed versions unchanged. `TestVersionMatch` checks regex detection for normal names, versioned names, stacked versions, empty names, and syntactically matching impossible timestamps.

State, dependencies, and integration: tests use fixed `fstest.Time` values and package `version_test` to exercise only exported APIs.

Risks and test signals: good coverage of file-name edge cases. Tests document that `Match` is syntax-only, not semantic date validation.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/lib/version/version_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/librclone/ctest/Makefile -->
## sources/user-network-fs/rclone/librclone/ctest/Makefile

Purpose: builds and runs the C demonstration/test program for `librclone`'s C archive interface.

Important APIs and control flow: platform conditionals set executable suffix, library name (`librclone.lib` on Windows, `librclone.a` otherwise), and linker flags. `ctest` links `ctest.o` with the generated library. `ctest.o` compiles `ctest.c` and generated `librclone.h`. The library/header rule runs `go build --buildmode=c-archive -o $(LIB) github.com/rclone/rclone/librclone`. `test` runs the executable. `clean` removes build artifacts.

State, dependencies, and integration: integrates Go's c-archive output with a C compiler. It assumes `go`, `CC`, platform link libraries, and the generated header are available.

Risks and test signals: `ctest.o` compiles both `ctest.c` and `librclone.h` with `-c $^`, which may create header precompiled artifacts depending on compiler behavior. The Makefile is a smoke/demo build path rather than production packaging.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/librclone/ctest/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/librclone/ctest/ctest.c -->
## sources/user-network-fs/rclone/librclone/ctest/ctest.c

Purpose: simple C test/demo for calling rclone's exported C API.

Important APIs and control flow: `testRPC` calls `RcloneRPC`, prints status/output, and frees output with `RcloneFreeString`. `testNoOp` calls `rc/noop` with nested JSON and asserts exact pretty-printed output and status 200. `testError` calls `rc/error` and asserts exact JSON error output and status 500. `testCopyFile` and `testListRemotes` demonstrate other RPCs but are commented out in `main`. `main` initializes librclone, runs no-op and error tests, finalizes, and exits success if assertions pass.

State, dependencies, and integration: depends on generated `librclone.h`, libc, and the exported Go functions. It validates C-side memory ownership by freeing every RPC output.

Risks and test signals: exact JSON formatting makes the test sensitive to rclone RC formatting changes. Some demo functions assume `/tmp` or configured remotes and are intentionally disabled. The active tests provide a good C ABI smoke test for success/error calls and memory release.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/librclone/ctest/ctest.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/librclone/gomobile/gomobile.go -->
## sources/user-network-fs/rclone/librclone/gomobile/gomobile.go

Purpose: exposes librclone shims with signatures acceptable to gomobile/gobind.

Important APIs and control flow: `RcloneInitialize` and `RcloneFinalize` delegate to internal `librclone.Initialize` and `Finalize`. `RcloneRPCResult` carries `Output string` and `Status int`. `RcloneRPC(method, input)` calls `librclone.RPC` and returns a pointer to a result struct.

State, dependencies, and integration: imports all backends and plugins by blank import, plus a mobile key-event package to keep go.mod dependency. It integrates with mobile bindings that cannot use the cgo exported ABI.

Risks and test signals: lifecycle semantics mirror internal librclone; repeated initialize/finalize is not strongly managed. RPC methods needing raw request/response are unsupported by the internal layer. No gomobile tests are present in this subset.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/librclone/gomobile/gomobile.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/librclone/librclone.go -->
## sources/user-network-fs/rclone/librclone/librclone.go

Purpose: C-exported main package for building rclone as a shared or static library.

Important APIs and control flow: cgo declares `struct RcloneRPCResult { char* Output; int Status; }`. `RcloneInitialize` and `RcloneFinalize` delegate lifecycle to the internal library. `RcloneRPC(method, input)` converts C strings to Go strings, calls internal `librclone.RPC`, allocates the output as `C.CString`, and returns status/output in the C struct. `RcloneFreeString` frees strings returned by `RcloneRPC`. `main` is empty for library builds.

State, dependencies, and integration: blank imports register all backends, mount commands, operations/sync RC commands, and plugins. It depends on cgo and `unsafe` for C memory release. It is consumed by C, PHP FFI, Python ctypes, and other native integrations.

Risks and test signals: caller must free `Output`; failure to do so leaks C heap memory. All strings are expected UTF-8. Go panic handling is in internal `RPC`, not this wrapper. C demo and Python tests exercise this ABI.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/librclone/librclone.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/librclone/librclone/librclone.go -->
## sources/user-network-fs/rclone/librclone/librclone/librclone.go

Purpose: internal implementation shared by C and gomobile librclone bindings, translating JSON strings to rclone RC calls and JSON responses.

Important APIs and control flow: `Initialize` starts logging, installs config-file handling, and starts accounting using a background context. `Finalize` currently forces a GC and has TODOs for deeper cleanup. `RPC(method, input)` creates an `rc.Params`, recovers panics into JSON errors, decodes input JSON when non-empty, finds the registered RC call, rejects calls needing raw request or response, runs the call as a `jobs.NewJob`, defaults nil output to an empty params map, and serializes output with `rc.WriteJSON`. `writeError` logs, builds `rc.Error` params, and falls back to hand-written JSON if serialization fails.

State, dependencies, and integration: depends on rclone config, accounting, logging, RC registry, RC jobs, and standard JSON/http/runtime packages. It has process-wide initialization side effects but stores no explicit initialized flag.

Risks and test signals: unsupported request/response RC methods return 404. `Finalize` does not cancel async jobs or close all global services. Input must be a JSON object. Panic recovery returns stack traces in JSON errors. C and Python tests cover `rc/noop` and `rc/error`.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/librclone/librclone/librclone.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/librclone/php/rclone.php -->
## sources/user-network-fs/rclone/librclone/php/rclone.php

Purpose: PHP FFI wrapper around `librclone.so`.

Important APIs and control flow: class `Rclone` loads C definitions for `RcloneRPCResult`, lifecycle functions, `RcloneRPC`, and `RcloneFreeString` from a supplied shared library path. The constructor calls `RcloneInitialize`. `rpc($method, $input)` invokes `RcloneRPC`, copies the C string to a PHP string, stores status, frees the C output string, and returns an array with `output` and `status`. `close()` calls `RcloneFinalize`.

State, dependencies, and integration: object state is the FFI handle and latest output struct. It depends on PHP FFI and the C shared library ABI.

Risks and test signals: callers must pass JSON strings, not PHP arrays. `close` is manual; there is no destructor safety net. The wrapper does not throw on non-200 status. The companion PHP test demonstrates remote operations but depends on configured remotes.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/librclone/php/rclone.php -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/librclone/php/test.php -->
## sources/user-network-fs/rclone/librclone/php/test.php

Purpose: demonstration/test script for the PHP FFI wrapper using a configured remote.

Important APIs and control flow: the script constructs `Rclone`, lists remotes, creates a folder on `gdrive:/`, lists the remote, writes a local test file, copies it to the remote folder through `operations/copyfile`, lists the folder, checks the first listed item name, prints `SUCCESS` or `FAIL`, and closes the library.

State, dependencies, and integration: depends on `rclone.php`, `librclone.so`, PHP FFI, a configured `gdrive:/` remote, and local filesystem write access.

Risks and test signals: it is environment-dependent and can mutate a real remote. It is useful as an integration example but unsuitable as a hermetic unit test. It does not clean up the remote test folder/file.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/librclone/php/test.php -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/librclone/python/rclone.py -->
## sources/user-network-fs/rclone/librclone/python/rclone.py

Purpose: Python ctypes wrapper around the C `librclone` shared library.

Important APIs and control flow: `RcloneRPCString` subclasses `c_char_p` so ctypes preserves the raw pointer for `RcloneFreeString`. `RcloneRPCResult` mirrors the C struct. `RcloneException` carries decoded error output and status. `Rclone.__init__` loads the shared library, configures function restypes/argtypes, and initializes rclone. `rpc(method, **kwargs)` JSON-encodes kwargs, calls `RcloneRPC`, decodes JSON output, frees the C string, raises `RcloneException` on non-200 status, and returns the decoded dict. `close` finalizes and clears the handle. `build` compiles the shared library if missing.

State, dependencies, and integration: depends on `ctypes`, `json`, `os`, `subprocess`, and the Go toolchain for `build`. It integrates with Python applications needing local RC calls without an HTTP server.

Risks and test signals: `rpc` assumes output is valid JSON and frees after decode; if decode raises before free, the current code may leak the C string. `close` is manual and repeated calls after close would fail. The Python test covers success and RC error conversion.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/librclone/python/rclone.py -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/librclone/python/test_rclone.py -->
## sources/user-network-fs/rclone/librclone/python/test_rclone.py

Purpose: unittest coverage for the Python ctypes wrapper and shared library build path.

Important APIs and control flow: `setUpClass` builds `./librclone.so` if missing and initializes one shared `Rclone` instance. `tearDownClass` closes it and removes the shared object. `test_rpc` calls `rc/noop` and expects the same dict back. `test_rpc_error` calls `rc/error`, expects `RcloneException`, checks status 500, and checks the error prefix.

State, dependencies, and integration: depends on `go build`, local compiler support for `librclone`, and the Python wrapper. It mutates the current directory by creating/removing `librclone.so`.

Risks and test signals: this is an integration test, not a fast pure unit test. It does not cover memory-free behavior under JSON decode failures or finalizer edge cases.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/librclone/python/test_rclone.py -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/rclone.go -->
## sources/user-network-fs/rclone/rclone.go

Purpose: main executable entrypoint for rclone.

Important APIs and control flow: blank imports register all backends, all commands, and plugins. `main()` delegates to `cmd.Main()`, which owns command-line parsing and execution.

State, dependencies, and integration: this file has only startup side effects via imports. It integrates the full command set and backend registry into the binary.

Risks and test signals: correctness depends on imported packages' init functions. There are no direct tests here; executable behavior is tested elsewhere through command and integration tests.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/rclone.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/vfs/dir.go -->
## sources/user-network-fs/rclone/vfs/dir.go

Purpose: implements the VFS directory node: directory metadata, directory listing cache, virtual entries for pending changes, cache invalidation, lookup, creation, deletion, rename, metadata pseudo-files, and recursive operations.

Important APIs and control flow: `newDir` creates a `Dir` with inode, modtime, items map, and cleanup timer. Node methods expose type, mode, name/path, sys data, inode, modtime, size, fs/vfs, and sync/truncate behavior. Cache operations include `ForgetAll`, `ForgetPath`, `changeNotify`, `invalidateDir`, `_readDir`, `_readDirFromEntries`, and `readDirTree`. Virtual state (`vAddFile`, `vAddDir`, `vDel`) is managed by `AddVirtual`, `DelVirtual`, `_purgeVirtual`, and `manageVirtuals` so pending uploads/deletes survive remote listing lag. File-system operations include `Stat`, `ReadDirAll`, `Open`, `Create`, `Mkdir`, `Remove`, `RemoveAll`, `RemoveName`, and `Rename`.

State, dependencies, and integration: `Dir` holds VFS pointer, backend fs, parent, path, `fs.Directory` entry, read timestamp, cached `items`, virtual-state map, user sys value, modtime, cleanup timer, and atomic count of virtuals in this subtree. It integrates with `File`, `VFS`, `vfscache`, backend `fs.Fs`, `list`, `walk`, `operations`, unicode normalization, and metadata APIs.

Risks and test signals: concurrency is managed with several locks and recursive locking, so lock ordering matters. Virtual entries deliberately prevent cache eviction while uploads/writes are in progress. `statMetadata` assumes base node entry behavior and creates memory objects for JSON metadata. Rename updates cached paths and cache backing store, and must keep parent item keys in sync. Tests cover methods, cache forgets, walking, stat/listing, virtual entries, create/mkdir/remove/rename, open-file virtual survival, modtime invalidation, metadata pseudo-files, and read-only errors.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/vfs/dir.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/vfs/dir_handle.go -->
## sources/user-network-fs/rclone/vfs/dir_handle.go

Purpose: represents an open VFS directory handle and implements directory read APIs.

Important APIs and control flow: `newDirHandle(d)` stores the directory. `String`, `Stat`, and `Node` expose handle identity. `Readdir(n)` lazily calls `d.ReadDirAll()`, converts nodes to `os.FileInfo`, stores the remaining slice in `fh.fis`, and returns either all entries (`n <= 0`) or the next chunk (`n > 0`), returning `io.EOF` only when a positive-size read finds no entries left. `Readdirnames(n)` maps `Readdir` results to names. `Close()` clears cached file infos.

State, dependencies, and integration: state is the directory pointer and cursor slice. It embeds `baseHandle` from the VFS package and depends on `io` and `os`. It integrates with mounted filesystem directory listing operations.

Risks and test signals: `DirHandle` is not synchronized for concurrent reads. It snapshots entries on first read and does not see later directory changes until reopened. Tests cover string/stat/node/close, full and chunked readdir, EOF, and names.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/vfs/dir_handle.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/vfs/dir_handle_test.go -->
## sources/user-network-fs/rclone/vfs/dir_handle_test.go

Purpose: tests VFS directory handle behavior.

Important APIs and control flow: `TestDirHandleMethods` opens a directory, checks `String` including nil cases, `Stat`, `Node`, and `Close`. `TestDirHandleReaddir` creates a directory with two files and a subdirectory, reads all entries at once, then reads in chunks of two and verifies final `io.EOF`. `TestDirHandleReaddirnames` smoke-tests name extraction.

State, dependencies, and integration: uses shared VFS test helpers, remote fixture writes, `os.O_RDONLY`, `io.EOF`, and testify. It verifies sorted listing inherited from `Dir.ReadDirAll`.

Risks and test signals: good coverage for cursor semantics. It does not test concurrent calls or directory changes after the handle snapshot is populated.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/vfs/dir_handle_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/vfs/dir_test.go -->
## sources/user-network-fs/rclone/vfs/dir_test.go

Purpose: broad unit/integration tests for VFS directory nodes and directory cache behavior.

Important APIs and control flow: helper `dirCreate` sets up a VFS with `dir/file1`. Tests cover basic node methods, `ForgetAll`, `ForgetPath`, cached directory walking, `SetModTime`, `Stat`, `ReadDirAll`, virtual adds/deletes, opening directories read-only, creating files, mkdir/submkdir, remove/remove-all/remove-name, file and directory rename, parent map key updates after `renameTree`, open-file virtual entries surviving forgets, directory modtime invalidation after writes, and metadata pseudo-file generation.

State, dependencies, and integration: tests use `fstest.Run`, backend operations, VFS cache/state, feature flags such as `CanHaveEmptyDirectories` and `DirModTimeUpdatesOnWrite`, runtime platform skips, JSON metadata parsing, and read-only option mutation.

Risks and test signals: this is a strong signal for user-visible VFS semantics and virtual-entry edge cases. It also documents known limitations, such as a newly created file not appearing in stat until opened for write. Coverage is environment-dependent for backend features and filesystem timestamp precision.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/vfs/dir_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/vfs/errors.go -->
## sources/user-network-fs/rclone/vfs/errors.go

Purpose: defines cross-platform low-level VFS error values and maps common errors to Go `os` package sentinels.

Important APIs and control flow: `Error` is a byte enum with values `OK`, `ENOTEMPTY`, `ESPIPE`, `EBADF`, `EROFS`, `ENOSYS`, and `ELOOP`. `ENOENT`, `EEXIST`, `EPERM`, `EINVAL`, and `ECLOSED` alias `os` errors. `Error.Error()` returns a human-readable string from `errorNames`, or `Low level error N` for unknown values.

State, dependencies, and integration: no mutable state. It depends on `fmt` and `os`. Comments note that mount/cmount/mount2 translation code must be updated when changing values.

Risks and test signals: enum ordering is part of external translation expectations, so adding/reordering errors has cross-package impact. Tests cover known and unknown string output.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/vfs/errors.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/vfs/errors_test.go -->
## sources/user-network-fs/rclone/vfs/errors_test.go

Purpose: tests string rendering for custom VFS errors.

Important APIs and control flow: `TestErrorError` asserts `OK` renders as `Success`, `ENOSYS` as `Function not implemented`, and an unknown value as `Low level error 99`.

State, dependencies, and integration: dependencies are `testing` and testify. It is a direct enum string smoke test.

Risks and test signals: covers only rendering, not translation to platform mount error codes.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/vfs/errors_test.go -->
