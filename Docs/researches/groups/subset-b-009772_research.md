# subset-b-009772 research

Grouped source research for rclone `fs` support files. Each section preserves the source path and is wrapped for reconciliation into source-tree-aligned per-file reports.

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/fs/asyncreader/asyncreader_test.go -->
# sources/user-network-fs/rclone/fs/asyncreader/asyncreader_test.go

Purpose: exercises the asynchronous read-ahead reader implementation in `fs/asyncreader`, especially EOF propagation, `io.WriterTo`, abandoned streams, and bounded skipping across prefetched buffers. The tests are implementation-aware: they reference `New`, `AsyncReader.Read`, `WriteTo`, `Close`, `Abandon`, `SkipBytes`, `BufferSize`, `softStartInitial`, and `ErrorStreamAbandoned`.

Important APIs and helpers: `TestAsyncReader` validates simple read/EOF behavior, repeated EOF after the terminal error, idempotent close, and closing before draining a large stream. `TestAsyncWriteTo` verifies the `io.Copy`/`WriteTo` path returns bytes once and no error on a second copy after EOF. `TestAsyncReaderErrors` covers nil reader and invalid buffer counts. `readMaker`, `bufReader`, `reads`, `bufsizes`, and the size/write tests borrow bufio-style cases to vary upstream reader behavior, downstream read sizes, internal `bufio.Reader` sizes, and async buffer counts. `zeroReader` and `testAsyncReaderClose` model an infinite source so `Abandon` can interrupt both `Read` loops and `WriteTo`. `TestAsyncReaderSkipBytes` uses deterministic random data and many initial-read/skip combinations to check successful in-buffer forward/backward skipping and failure paths.

Control flow: most tests construct `AsyncReader` with `context.Background()` and an `io.NopCloser` source, then drive either `Read`, `io.Copy`, direct `WriteTo`, or `readers.ReadFill`. The skip test reads an initial prefix, calls `SkipBytes`, then reads 1024 bytes and compares the result with the expected offset when the skip succeeds. When the skip is impossible, it expects either EOF or `ErrorStreamAbandoned` because `SkipBytes` abandons the reader on failure.

State and persistence: the tests are in-memory only, but they assert important lifecycle state: EOF is sticky once observed, `Close` closes underlying resources without double-close panics, and `Abandon` unblocks concurrent readers. The `zeroReader.closed` flag is a guard against double-closing the input.

Dependencies and integration points: depends on `testing/iotest` reader wrappers, `bufio`, `readers.ReadFill`, `israce.Enabled`, and the async reader implementation. The race detector skip avoids a known Go runtime race-related issue for multi-buffer cases.

Risks: async reader correctness is concurrency-sensitive. The tests cover many data paths but do not inspect internal goroutine cleanup directly beyond unblocking and close behavior. `TimeoutReader` is intentionally treated as non-recovering for async reads, so it documents a behavioral difference from some synchronous reader expectations.

Test signals: strong coverage for EOF semantics, `WriterTo`, abandoning, invalid constructor input, buffer sizing, read sizes, and skip boundaries. The test matrix gives high confidence in byte-for-byte delivery across read-ahead boundaries.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/fs/asyncreader/asyncreader_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/fs/backend_config.go -->
# sources/user-network-fs/rclone/fs/backend_config.go

Purpose: implements rclone's backend configuration state-machine primitives and wrapper. It lets backend `RegInfo.Config` functions expose UI/API-neutral steps through `ConfigIn` and `ConfigOut`, while the fs layer handles internal states such as full option prompting and OAuth.

Important APIs/types/functions: `ConfigIn` carries `State` and previous `Result`; `ConfigOut` carries next `State`, optional `Option`, optional `OAuth`, display `Error`, and immediate `Result`. Helper constructors include `ConfigInputOptional`, `ConfigInput`, `ConfigPassword`, `ConfigGoto`, `ConfigResult`, `ConfigError`, `ConfigConfirm`, `ConfigChooseExclusiveFixed`, `ConfigChooseExclusive`, `ConfigChooseFixed`, and `ConfigChoose`. Constants include `ConfigToken`, `ConfigKeyEphemeralPrefix`, and `ConfigAll`. `ConfigOAuth` is an injected function set by OAuth code to avoid circular imports. `StatePush`/`StatePop` encode nested state values using comma separation with wide-comma escaping. `ConfigOAuthOnly` marks context so authorization can stop after OAuth. `BackendConfig` repeatedly calls `backendConfigStep` until a terminal state, question, or error. `MatchProvider` filters provider-specific options/examples.

Control flow: callers pass a backend name, config mapper, registry info, noninteractive choices, and `ConfigIn`. `BackendConfig` loops over internal no-question transitions, feeding returned `State` and `Result` back into the next step. `backendConfigStep` dispatches `ConfigAll` to `configAll`, `*oauth` to `ConfigOAuth`, `*postconfig` back into backend post-config, and unknown `*` states to errors; otherwise it invokes the backend's own `Config`. If a step returns `OAuth`, it rewrites the state to an internal `*oauth` stack. If it returns an `Option`, the wrapper may satisfy it from explicit `choices`, from `AutoConfirm`, or update defaults for edit mode.

State and persistence behavior: backend config state is deliberately serialized in strings rather than retained in memory. `configAll` advances through `ri.Options` with encoded action, option index, and advanced-mode flag. When a user result differs from the current mapper value, it writes through `m.Set`. Ephemeral inputs should use names starting with `config_`; persistent backends should keep state in config storage via the mapper. OAuth-only context can truncate the return state to finish after authorization.

Dependencies and integration points: depends on `configmap.Mapper` and `Getter`, `RegInfo`, `Options`, `Option`, `OptionExample`, `GetConfig`, logging, and backend registry metadata. It is used by interactive config UI, rc/noninteractive config creation/update, and OAuth authorization flows.

Risks: malformed internal state strings can produce internal errors, and provider filtering depends on exact comma-separated provider names. The full-config path mutates `Option` values via mapper writes and can skip hidden, advanced, or provider-mismatched options, so registry metadata mistakes are user-visible. `ConfigOAuth` must be installed before OAuth states are reached.

Test signals: `backend_config_test.go` covers state push/pop escaping and provider matching. Broader behavior is indirectly tested by config/UI and backend tests, but this file's internal state machine has limited direct unit coverage in the listed subset.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/fs/backend_config.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/fs/backend_config_test.go -->
# sources/user-network-fs/rclone/fs/backend_config_test.go

Purpose: unit tests the small pure helpers in `backend_config.go` that are critical for serializing state and filtering provider-specific options.

Important APIs/functions: `TestStatePush` validates empty and non-empty state stacking, including escaping commas in pushed values as Unicode wide commas. `TestStatePop` validates decoding, empty values, final-element handling, and wide-comma restoration. `TestMatchProvider` validates blank-provider permissiveness, exact provider membership, and negated membership lists.

Control flow: each test is table-driven or assertion-driven over pure functions. No config storage, registry, or OAuth setup is needed.

State and persistence behavior: the tests document the state encoding contract used by `configAll` and OAuth return-state stacking. Correct escaping is important because state fields are comma-separated and may themselves contain commas.

Dependencies and integration points: uses `testify/assert`. It constrains behavior used by `BackendConfig`, provider-specific option filtering, and config state handoff through API/UI frontends.

Risks: tests do not cover malformed deeply nested state, `BackendConfig` loop behavior, choice overrides, edit defaults, or OAuth routing. They do catch regressions in the primitive encoding/matching behavior.

Test signals: focused and deterministic coverage for pure helper functions.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/fs/backend_config_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/fs/bits.go -->
# sources/user-network-fs/rclone/fs/bits.go

Purpose: defines a generic bitmask flag option type for rclone settings that can be represented as named choices, parsed from comma-separated strings, scanned, and marshaled to JSON.

Important APIs/types/functions: `Bits[C BitsChoices] uint64` is the flag type. `BitsChoicesInfo` pairs bit values with display names. `BitsChoices` requires `Choices() []BitsChoicesInfo`. Methods include `String`, `Help`, `Choices`, `Set`, `IsSet`, `Type`, `Scan`, `UnmarshalJSON`, and `MarshalJSON`. `Type` supports a custom `Type() string` method on the choices type via the package-level `typer` convention.

Control flow: `String` emits the zero-value choice name when one exists, then emits known nonzero bits in choice order and appends `Unknown-0x...` if unknown bits remain. `Set` splits input on commas, trims spaces, ignores empty parts, case-insensitively matches choice names, ORs matched bits, and only assigns on success. `UnmarshalJSON` delegates to `UnmarshalJSONFlag`, accepting either string flag names or integer values. `MarshalJSON` always serializes the `String` form.

State and persistence behavior: no global state. The parsed bitmask is stored in the `Bits` value. JSON and config persistence use string names by default, while numeric JSON input remains backward-compatible.

Dependencies and integration points: uses `encoding/json`, `fmt`, and `strings`. Integrates with rclone option parsing through `Flagger`, `FlaggerNP`, JSON config, `fmt.Scanner`, and CLI help generation.

Risks: duplicate names or overlapping bits in a choices implementation would create ambiguous output/input. `String` consumes known bits from a local copy, so unknown combined bits are reported as one residual mask. A zero input serializes to an empty string if no zero choice is provided.

Test signals: `bits_test.go` checks interfaces, string/help output, case-insensitive parsing, no mutation on parse error, `IsSet`, scan support, JSON string/numeric input, and JSON output.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/fs/bits.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/fs/bits_test.go -->
# sources/user-network-fs/rclone/fs/bits_test.go

Purpose: tests the generic `Bits` option type using a local `bitsChoices` implementation with `OFF`, `A`, `B`, and `C`.

Important APIs/functions: the test declares `type bits = Bits[bitsChoices]` and constants `bitA`, `bitB`, `bitC`. It asserts `bits` implements `Flagger` and `FlaggerNP`. `TestBitsString`, `TestBitsHelp`, `TestBitsSet`, `TestBitsIsSet`, `TestBitsType`, `TestBitsScan`, `TestBitsUnmarshallJSON`, and `TestBitsMarshalJSON` cover the exposed behavior.

Control flow: parse tests initialize a value to all bits set, call `Set` or `json.Unmarshal`, and assert successful parses assign the wanted value while failed parses leave the original value unchanged. JSON tests cover quoted strings and numeric literals.

State and persistence behavior: test data documents that zero renders as `OFF`, unknown residual bits render as `Unknown-0x...`, and JSON marshaling persists string names rather than integers.

Dependencies and integration points: uses `encoding/json`, `fmt.Sscan`, `strconv`, and `testify`. It anchors behavior required by CLI/config flag parsing.

Risks: no test covers a choices type with no zero option, duplicate choice names, custom `Type`, or overlapping bit masks.

Test signals: strong table coverage for normal parsing, invalid choice errors, JSON compatibility, and interface satisfaction.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/fs/bits_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/fs/bwtimetable.go -->
# sources/user-network-fs/rclone/fs/bwtimetable.go

Purpose: implements bandwidth limit parsing and lookup for rclone global and per-file bandwidth timetables.

Important APIs/types/functions: `BwPair` stores upload `Tx` and download `Rx` as `SizeSuffix`; methods are `String`, `Set`, and `IsSet`. `BwTimeSlot` stores weekday, HHMM time, and a `BwPair`. `BwTimetable` is a slice of slots with `String`, `Set`, `LimitAt`, `Type`, `UnmarshalJSON`, and `MarshalJSON`. Helpers include `validateHour`, `parseWeekday`, and `timeDiff`.

Control flow: `BwPair.Set` accepts either one size for both directions or `tx:rx`. `BwTimetable.Set` rejects empty input; a single value with no space/comma becomes a constant Sunday-midnight slot. Otherwise it splits tokens by spaces or semicolons. Tokens without a weekday expand a time to all seven weekdays; tokens with `Day-HH:MM` create one slot. Each token parses bandwidth through `BwPair.Set`. `LimitAt` computes current weekday/time as `DHHMM`, defaults to the last slot for wraparound, then chooses the closest slot not after the requested time.

State and persistence behavior: the timetable is stored as an ordered slice. The code does not sort slots after parsing; lookup correctness relies on scanning all slots for closest prior time and uses the last slot as wraparound. JSON persists the same string representation used by flags.

Dependencies and integration points: uses `SizeSuffix`, rclone flag interfaces, JSON config, and `time.Time`. It is wired into global options `bwlimit` and `bwlimit_file` in `fs/config.go`.

Risks: because `Set` appends to the receiver, callers reusing a non-empty `BwTimetable` without clearing it can accumulate slots. Time parsing checks length and numeric ranges but does not explicitly require the separator at index 2 to be `:`, relying on failed minute parsing for malformed strings. Slot ordering is display order from input expansion, not normalized chronological order.

Test signals: `bwtimetable_test.go` extensively covers invalid formats, constant and directional limits, daily expansion, weekday-specific entries, semicolon separators, wraparound lookup, and JSON marshal/unmarshal.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/fs/bwtimetable.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/fs/bwtimetable_test.go -->
# sources/user-network-fs/rclone/fs/bwtimetable_test.go

Purpose: provides broad tests for bandwidth pair and timetable parsing, rendering, current-limit lookup, and JSON conversion.

Important APIs/functions: interface assertions ensure `BwTimetable` satisfies `Flagger` and `FlaggerNP`. `TestBwTimetableSet` is a large table for bad inputs, constant limits, `tx:rx` limits, all-days time expansion, weekday-specific schedules, semicolon separators, and documented examples. `TestBwTimetableLimitAt` validates empty timetable unlimited behavior, exact and in-between slot selection, same-day slots, and week wraparound. JSON tests check string conversion in both directions.

Control flow: tests instantiate a fresh timetable for each parse case, call `Set`, assert error/no-error, compare the exact slot slice, and compare `String`. `LimitAt` uses fixed UTC dates with known weekdays to validate lookup.

State and persistence behavior: expected outputs document canonical string formatting such as `Sun-10:20,666Ki`, `off`, and omitted `:rx` when upload/download limits match. Empty timetable lookup returns an unlimited slot (`-1` sizes) even though empty parse input is invalid.

Dependencies and integration points: uses `encoding/json`, `time`, and `testify`. It constrains global `bwlimit` behavior consumed by transfer throttling.

Risks: the tests rely on exact expanded ordering and therefore protect compatibility but make parser output changes noisy. They do not test reusing a non-empty timetable receiver or non-UTC local timezone edge cases.

Test signals: very strong parser and lookup coverage across normal, edge, and documented cases.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/fs/bwtimetable_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/fs/cache/cache.go -->
# sources/user-network-fs/rclone/fs/cache/cache.go

Purpose: implements the process-wide cache of `fs.Fs` backend instances, with canonicalization, expiration, finalizer shutdown, pinning, and special treatment for paths that resolve to files.

Important APIs/types/functions: package-level state includes `once`, cache `c`, mutex `mu`, `remap`, and `childParentMap`. Public functions include `Canonicalize`, `GetFn`, `Get`, `GetArr`, `PutErr`, `Put`, `Pin`, `PinUntilFinalized`, `Unpin`, `ClearConfig`, `Clear`, `Entries`, `ClearMappings`, `ClearMappingsPrefix`, and `EntriesWithPinCount`. Internal helpers include `createOnFirstUse`, `addMapping`, `addChild`, `isChild`, and `getError`. Job hooks `JobGetJobID` and `JobOnFinish` allow rc jobs to pin remotes until completion.

Control flow: on first use, `createOnFirstUse` creates a `lib/cache.Cache`, applies expiration settings from global config, and installs a finalizer that calls backend `Shutdown` when supported. `GetFn` canonicalizes the requested string, calls cache `Get` with a create function using the original string, and stores successful results or `ErrorIsFile` parents. When a newly created backend reports a canonical string different from the lookup key, directories are renamed in cache and mapped; files are renamed to the parent backend, stored without error, and the child path is recorded so later child lookups return `fs.ErrorIsFile`. `Get` copies config/filter settings into a detached background context before calling `fs.NewFs`, then pins for active rc jobs.

State and persistence behavior: cache entries are in-memory only and expire per config. `remap` maps user-supplied strings to canonical cache keys. `childParentMap` tracks file-child to parent relationships so the same cached parent can report file-vs-directory errors based on the original lookup. `ClearConfig` deletes entries and mappings for a config prefix; `Clear` resets cache and mappings.

Dependencies and integration points: depends on `fs`, `filter`, `lib/cache`, `context`, `runtime`, and backend `Shutdowner`. It is a central integration point for all remote creation through `cache.Get`, rc jobs, and config edits that call `ClearConfig`.

Risks: global mutable maps and cache require correct locking; `Canonicalize` and child tracking determine whether callers see `ErrorIsFile`. `ClearMappingsPrefix` counts deletions across two maps and deletes based on mapped parent prefix, so prefix collisions could matter. Long-lived backends intentionally detach from request cancellation, which is correct for reuse but can surprise code expecting context cancellation to close remotes.

Test signals: `cache_test.go` covers cache hits, file-child handling, canonicalization, errors, put/puterr, pin/unpin counts, clear operations, and entries.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/fs/cache/cache.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/fs/cache/cache_test.go -->
# sources/user-network-fs/rclone/fs/cache/cache_test.go

Purpose: tests the fs cache using a mock backend factory to verify canonicalization, file-parent caching, error handling, pinning, and clearing.

Important APIs/functions: `mockNewFs` returns `mockfs.NewFs` for directories, parent `Fs` plus `fs.ErrorIsFile` for file paths, or a sentinel error. Tests include `TestGet`, `TestGetFile`, `TestGetFile2`, `TestGetError`, `TestPutErr`, `TestPut`, `TestPin`, `TestPinFile`, `TestClearConfig`, `TestClear`, and `TestEntries`.

Control flow: most tests call `GetFn` with a deterministic factory and assert the factory is only called on cache misses. File tests first resolve a child path, then resolve the same child and parent path to confirm they all share one cached `Fs` while child lookups retain `fs.ErrorIsFile`.

State and persistence behavior: tests call `Clear` via cleanup and sometimes `ClearMappings` explicitly because package state is global. `TestPinFile` inspects `childParentMap` length and `EntriesWithPinCount` to verify pinning a child and parent affects the same cache entry.

Dependencies and integration points: uses `mockfs`, `fs.ErrorIsFile`, and `testify`. It constrains behavior relied on by all rclone operations using cached remotes.

Risks: tests use package globals (`called`, maps) and therefore require cleanup discipline. They do not exercise cache expiration timers, finalizer shutdown, rc job pin hooks, or concurrent access.

Test signals: good coverage for canonical cache semantics and file-vs-directory error preservation.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/fs/cache/cache_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/fs/chunkedreader/chunkedreader.go -->
# sources/user-network-fs/rclone/fs/chunkedreader/chunkedreader.go

Purpose: defines the public chunked reader abstraction and chooses sequential or parallel implementations for reading an `fs.Object` in ranges.

Important APIs/types/functions: package errors `ErrorFileClosed` and `ErrorInvalidSeek`; interface `ChunkedReader` combining `io.Reader`, `io.Seeker`, `io.Closer`, `fs.RangeSeeker`, and `Open`; constructor `New(ctx, o, initialChunkSize, maxChunkSize, streams)`.

Control flow: `New` normalizes chunk sizes. `initialChunkSize <= 0` disables chunking by setting `-1`; `maxChunkSize` below initial is raised to initial unless `-1`; negative stream count becomes zero. It chooses sequential mode for streams <= 1 or unknown object size, otherwise parallel mode.

State and persistence behavior: no persistent state in this file. It determines initial runtime state for `sequential` or `parallel` readers.

Dependencies and integration points: depends on `fs.Object`, `fs.RangeSeeker`, and standard IO interfaces. Used by multi-thread downloads and backends that benefit from ranged reads.

Risks: parallel mode requires known object size; the constructor guards this. `maxChunkSize` is irrelevant to parallel mode, which uses fixed rounded chunks in `parallel.go`.

Test signals: `chunkedreader_test.go` checks implementation selection for chunk sizes, stream counts, and unknown size.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/fs/chunkedreader/chunkedreader.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/fs/chunkedreader/chunkedreader_test.go -->
# sources/user-network-fs/rclone/fs/chunkedreader/chunkedreader_test.go

Purpose: contains shared tests and helpers for sequential and parallel chunked readers.

Important APIs/functions: `TestMain` initializes fstest. `TestChunkedReader` validates `New` chooses `sequential` or `parallel`. `testRead` returns a reusable subtest that performs many `RangeSeek` plus `Read` checks over content. `testErrorAfterClose` validates closed readers reject `Close`, `Read`, `Seek`, and `RangeSeek`. `makeContent` creates deterministic random bytes.

Control flow: `testRead` iterates initial chunk sizes, max chunk sizes, offsets, and range lengths, calling `RangeSeek` then reading a fixed 32-byte buffer and comparing exact content. Offsets beyond content length must error. The helper is invoked by sequential and parallel-specific tests with different stream counts.

State and persistence behavior: no persistence. It documents that `RangeSeek` should defer opening until read and should preserve byte-exact offsets across chunk boundaries.

Dependencies and integration points: uses `mockobject` seek modes, `fstest`, `testify`, and shared error values from the package. It validates both implementations through the public constructor and interface.

Risks: tests use small content and a fixed read buffer, so very large stream behavior is handled in `parallel_test.go`. Error-after-close asserts errors generically rather than exact error values.

Test signals: high signal for public behavior consistency across implementations and source seek modes.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/fs/chunkedreader/chunkedreader_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/fs/chunkedreader/parallel.go -->
# sources/user-network-fs/rclone/fs/chunkedreader/parallel.go

Purpose: implements multi-stream chunked reading of known-size `fs.Object` values by opening ranged streams in parallel and serving them in order.

Important APIs/types/functions: `parallel` tracks source object, current offset, end offset with launched streams, rounded chunk size, target stream count, active `stream` slice, and closed state. `stream` wraps one ranged download, its cancelable context, `io.ReadCloser`, offset/size, bytes served, `pool.RW` buffer, error channel, and debug name. Methods include `newStream`, `stream.readFrom`, `stream.eof`, `stream.read`, `stream.close`, `newParallel`, `_open`, `_popStream`, `_popStreams`, `Read`, `Close`, `Seek`, `RangeSeek`, and `Open`.

Control flow: `newParallel` rounds chunk size up to a multiple of `multipart.BufferSize` and defaults negative sizes to that buffer size. `_open` launches enough streams to reach `nstreams`, clipping the final chunk to object size. Each stream goroutine opens the object with `operations.Open` and a `RangeOption`, then pipes the response into a multipart RW buffer. `Read` holds the reader mutex, ensures streams are open, reads from the first stream, advances global offset, closes completed streams, and continues until the caller buffer is full or an error/EOF occurs. `Seek` computes the new absolute offset, rejects out-of-range seeks, drops completed/out-of-range streams, seeks within the current buffered stream when possible, or restarts stream scheduling from the new offset.

State and persistence behavior: runtime-only state is guarded by `mu`. Stream goroutines are canceled and drained during `_popStream`/`Close`. `endStream` records how far prefetch has been scheduled so new streams continue after retained streams. `RangeSeek` ignores the length argument and delegates to `Seek`.

Dependencies and integration points: depends on `fs.Object`, `operations.Open`, `hash.None`, `RangeOption`, `multipart.NewRW`, `pool.RW`, logging, and standard `io`. It is selected by `New` when streams > 1 and object size is known.

Risks: concurrency and cancellation are the main risks. `stream.close` waits on the goroutine error channel, so `readFrom` must always send exactly one error. `Seek` waits for buffered data to reach the seek target within a stream, which can block if the stream stalls or context is canceled. `RangeSeek` length is ignored in parallel mode, which is intentional but different from sequential mode. The code rejects seeking exactly to `size`, so callers cannot seek to EOF.

Test signals: `parallel_test.go` exercises multi-mode reads, close errors, large sequential reads, rewinds, end-relative seeks, and randomized backward seeks.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/fs/chunkedreader/parallel.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/fs/chunkedreader/parallel_test.go -->
# sources/user-network-fs/rclone/fs/chunkedreader/parallel_test.go

Purpose: tests the parallel chunked reader implementation over multiple mock object seek modes and larger multi-stream scenarios.

Important APIs/functions: `TestParallel` invokes shared `testRead` with three streams. `TestParallelErrorAfterClose` reuses close-error checks. `TestParallelLarge` constructs content larger than multiple chunks and streams, then tests straight reads, rewind, near-start seek, near-end seek, and randomized read/backward-seek loops.

Control flow: `TestParallelLarge` creates one reader for several full-read subtests and a fresh reader for the randomized seek loop. End-relative seeks are converted by passing `offset-size` with `io.SeekEnd`, then `io.ReadAll` verifies the suffix exactly.

State and persistence behavior: no persistence. Tests stress stream state retention, popping, restarting, and seeking within current buffered streams.

Dependencies and integration points: uses `mockobject`, `multipart.BufferSize`, `io`, deterministic random data, and `testify`.

Risks: tests do not force stream open failures, context cancellation, or slow/stalled streams. The first set of subtests shares a reader after full reads and seeks, which validates reuse but can make failures stateful.

Test signals: good behavioral coverage for normal parallel reads and seeks across chunk/stream boundaries.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/fs/chunkedreader/parallel_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/fs/chunkedreader/sequential.go -->
# sources/user-network-fs/rclone/fs/chunkedreader/sequential.go

Purpose: implements a single-stream chunked reader for `fs.Object`, supporting optional range chunking, chunk-size growth, `RangeSeek`, and reuse of range-seekable open readers.

Important APIs/types/functions: `sequential` stores context, source object, current `io.ReadCloser`, next read offset, current chunk start/size, initial and max chunk sizes, custom range-size flag, and closed state. Methods include `newSequential`, `Read`, `Close`, `Seek`, `RangeSeek`, `Open`, `openRange`, and `resetReader`.

Control flow: `Read` locks, rejects closed readers, opens on first read or after seeking, reads up to current chunk boundary with `io.ReadFull`, advances offset, converts `io.ErrUnexpectedEOF` to `io.EOF`, and when a chunk is fully read doubles chunk size up to max unless the last size came from `RangeSeek`, in which case it resets to initial. `RangeSeek` computes the new chunk offset relative to start/current/end, validates object size where needed, sets the next chunk size to the requested length or initial size, and defers reopening until read. `openRange` first tries `RangeSeek` on the existing reader; if that fails it opens the object with `HashesOption{None}` and an optional `RangeOption`.

State and persistence behavior: runtime state is mutex-protected. `offset == -1` means reopen on next read. `chunkSize == -1` means read to end. Closing resets/cleoses the current reader and makes subsequent operations return `ErrorFileClosed`.

Dependencies and integration points: depends on `fs.Object`, `fs.RangeSeeker`, `fs.RangeOption`, `fs.HashesOption`, and hash suppression. It is chosen for unknown-size objects, single-stream mode, or disabled parallelism.

Risks: validation rejects `chunkOffset >= size`, so seeking exactly to EOF is invalid. When object size is unknown, seeking from end is invalid. Reusing an existing `RangeSeeker` is an optimization but falls back to reopening if the returned offset or error is unsuitable.

Test signals: shared tests and `sequential_test.go` cover read correctness across chunk sizes, source seek modes, and closed-reader errors.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/fs/chunkedreader/sequential.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/fs/chunkedreader/sequential_test.go -->
# sources/user-network-fs/rclone/fs/chunkedreader/sequential_test.go

Purpose: runs the shared chunked reader tests against sequential mode.

Important APIs/functions: `TestSequential` creates deterministic 1024-byte content and runs `testRead` over all `mockobject.SeekModes` with streams set to zero. `TestSequentialErrorAfterClose` reuses shared close-error checks.

Control flow: the tests go through the public `New` constructor, which selects `sequential` because stream count is zero. The blank local backend import ensures backend registration for fstest context.

State and persistence behavior: no persistence. It validates sequential state transitions through public reads, range seeks, and closing.

Dependencies and integration points: depends on `mockobject`, shared test helpers, and local backend registration.

Risks: this file is intentionally thin; detailed coverage lives in `chunkedreader_test.go`.

Test signals: confirms the shared behavior matrix applies to sequential mode.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/fs/chunkedreader/sequential_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/fs/chunksize/chunksize.go -->
# sources/user-network-fs/rclone/fs/chunksize/chunksize.go

Purpose: calculates the minimum upload chunk size needed to keep a file within a backend's maximum part count while avoiding unnecessary memory growth.

Important APIs/functions: `Calculator(o any, size int64, maxParts int, defaultChunkSize fs.SizeSuffix) fs.SizeSuffix`.

Control flow: for streaming/unknown size (`size < 0`), it logs the upload capacity implied by the default and returns the default. For known sizes, it computes how many default-size chunks would be needed. If the default is sufficient, including exact boundary divisibility, it returns the default. Otherwise it divides file size by `maxParts`, rounds up to the nearest MiB, and adds another MiB for boundary cases that would still produce too many parts.

State and persistence behavior: pure calculation with debug logging only. No persistent state.

Dependencies and integration points: uses `fs.SizeSuffix`, `fs.Mebi`, and `fs.Debugf`. Backends can call it when preparing multipart uploads to pick an upload chunk size from object size and service part limits.

Risks: assumes `maxParts` is positive; callers must validate that. Rounds to MiB, which is conservative but may be larger than a backend with byte-granular chunks strictly needs. The boundary condition uses modulo by `maxParts` rather than `minChunk`, matching the current test expectations but worth preserving carefully.

Test signals: `chunksize_test.go` covers streaming, default sufficiency, rounding, one-byte overflow, minimum MiB behavior, and a forum-derived large file case.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/fs/chunksize/chunksize.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/fs/chunksize/chunksize_test.go -->
# sources/user-network-fs/rclone/fs/chunksize/chunksize_test.go

Purpose: validates `chunksize.Calculator` over representative multipart upload sizing cases.

Important APIs/functions: `TestComputeChunkSize` is table-driven and uses `toSizeSuffixMiB` for expected MiB values.

Control flow: each case calls `Calculator`, compares the returned chunk size, and for known-size inputs verifies the returned size yields at most `maxParts`. When the returned size is larger than the default, it also verifies one MiB less would exceed the part limit, proving the result is minimal under the MiB rounding rule.

State and persistence behavior: no state. Test names document expected behavior for streaming files, exact divisibility, one-byte overflow, and real-world issue sizing.

Dependencies and integration points: depends on `fs.SizeSuffix` and `fs.Mebi`. It protects upload behavior for backends using the shared calculator.

Risks: no tests cover invalid `maxParts` values or zero/negative default chunk sizes, which are caller preconditions.

Test signals: strong deterministic coverage for arithmetic edge cases and minimality.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/fs/chunksize/chunksize_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/fs/config.go -->
# sources/user-network-fs/rclone/fs/config.go

Purpose: defines rclone's global filesystem configuration model, option metadata, config context helpers, reload validation, and environment-variable naming helpers.

Important APIs/types/functions: package globals include `globalConfig`, config-file function hooks (`ConfigFileGet`, `ConfigFileSet`, `ConfigFileHasSection`), `CountError`, `ConfigProvider`, and `ConfigEdit`. `ConfigOptionsInfo` is the large registry of global options and defaults. `ConfigInfo` is the typed runtime config struct with `config` tags. Key functions/methods include `init`, `(*ConfigInfo).Reload`, `InitialLogLevel`, `TimeoutOrInfinite`, `GetConfig`, `CopyConfig`, `AddConfig`, `ConfigToEnv`, and `OptionToEnv`.

Control flow: `init` sets nonzero defaults, registers `ConfigOptionsInfo` against `globalConfig`, and initializes a preliminary log level from command-line/env arguments. `Reload` applies derived behavior and validation: dump implies debug logging, dry-run/interactive raise stats visibility, compare/copy dest conflict is rejected, stats-one-line date settings imply parent flags, partial suffix length is bounded, retries/transfers/checkers are forced positive, stats unit defaults to bytes on invalid input, and logging reload hook is invoked. `InitialLogLevel` scans `os.Args` for verbose/debug forms and `RCLONE_LOG_LEVEL=DEBUG`.

State and persistence behavior: `globalConfig` is process-wide default state. `AddConfig` makes a shallow mutable copy stored in context, while `CopyConfig` propagates config and rc request markers into another context. Config persistence itself is decoupled through function pointers installed by `fs/config`.

Dependencies and integration points: central to all packages that call `fs.GetConfig`, register global options, create remotes, or parse CLI flags. Depends on option registration infrastructure, logging, network types, and many custom flag types (`BwTimetable`, `DumpFlags`, `SizeSuffix`, `Duration`, etc.).

Risks: `ConfigOptionsInfo` and `ConfigInfo` tags must stay synchronized; missing tags or default mismatches can break CLI/config loading. `AddConfig` is shallow, so slice/map pointer fields may share backing data. `InitialLogLevel` intentionally does a manual early parse and may not understand every pflag spelling.

Test signals: no direct tests in the listed file set, but many downstream configflags/configstruct tests and general rclone tests depend on this metadata and reload behavior.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/fs/config.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/fs/config/authorize.go -->
# sources/user-network-fs/rclone/fs/config/authorize.go

Purpose: implements `rclone authorize` for headless remote authorization, running a backend's post-config/OAuth flow locally and printing a token or encoded config blob for transfer.

Important APIs/functions: `Authorize(ctx, args, noAutoBrowser, templateFile) error`. It uses constants `ConfigAuthorize`, `ConfigAuthNoBrowser`, `ConfigTemplateFile`, `ConfigClientID`, `ConfigClientSecret`, and `ConfigToken`.

Control flow: the function suppresses confirmation and marks the context OAuth-only. It accepts one, two, or three args: backend type only, backend type plus base64 config map blob, or backend type plus client id/secret. It finds the backend, validates it has config support, builds an input `configmap.Simple`, decodes or sets extra parameters, creates a temporary remote name, builds a config mapper, replaces setters with an output map, calls `PostConfig`, then prints either the token or an encoded output blob.

State and persistence behavior: uses in-memory maps only and a temporary remote name `**temp-fs**`; it does not write normal config storage. Output is printed to stdout in a paste-delimited block. Context is modified to stop after OAuth where supported.

Dependencies and integration points: depends on backend registry lookup, `fs.ConfigMap`, `PostConfig`, `configmap.Simple.Encode/Decode`, and UI confirmation suppression. It integrates with OAuth-capable backends and remote machines that paste the resulting token/config.

Risks: assumes the backend writes `token` to the output map. Errors in encoded input blob or unsupported backend config are surfaced. The function prints sensitive token material to stdout by design.

Test signals: no direct test in this subset; behavior is partially covered by backend OAuth/config tests elsewhere.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/fs/config/authorize.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/fs/config/config.go -->
# sources/user-network-fs/rclone/fs/config/config.go

Purpose: owns configuration storage selection/loading/saving, remote creation/update helpers, config path/cache/temp path discovery, environment-precedence reads, and config dump/list helpers.

Important APIs/types/functions: constants define config filenames and common backend keys. `Storage` is the persistent config interface. Globals include `Password`, `configPath`, `cacheDir`, `data`, and `dataLoaded`. Path helpers include `findFile`, `findHomeDir`, `findLocalConfig`, `findAppDataConfig`, `findXDGConfig`, `findDotConfigConfig`, `findOldHomeConfig`, and `makeConfigPath`. Public storage functions include `GetConfigPath`, `SetConfigPath`, `SetData`, `Data`, `LoadedData`, `SaveConfig`, `FileSections`, `FileGetValue`, `FileSetValue`, `FileDeleteKey`, `GetValue`, and `SetValueAndSave`. Remote APIs include `Remote`, `GetRemotes`, `GetRemoteNames`, `UpdateRemoteOpt`, `UpdateRemote`, `CreateRemote`, `PasswordRemote`, `JSONListProviders`, `DumpRcRemote`, `DumpRcBlob`, `Dump`, `GetCacheDir`, `SetCacheDir`, and `SetTempDir`.

Control flow: `init` installs fs package function hooks, chooses initial config/cache dirs, and installs default storage. `makeConfigPath` searches executable-local, platform config dirs, XDG, home `.config`, and legacy home config, creating a new default config dir unless config was explicitly supplied. `LoadedData` lazily loads storage, sets `RCLONE_CONFIG_DIR`, treats missing config as defaults, and fatals on other load errors. `SaveConfig` retries storage save with random short sleeps. `updateRemote` validates options, finds backend type, determines password fields to obscure, builds a mapper, applies key-values and choices, runs interactive or noninteractive backend config, saves, and clears cached remotes for the name.

State and persistence behavior: `configPath` controls storage; empty, OS null, or `/notfound` means memory-only behavior. `dataLoaded` gates lazy load. Remote updates write to config storage except ephemeral keys with `config_` prefix. Environment variables override file values in `GetValue` and are included first in `GetRemotes`.

Dependencies and integration points: ties together `fs` hooks, `configmap`, `obscure`, `fspath`, `rc.Params`, backend registry, cache invalidation, path libraries, random sleeps, and OS environment. It is the core integration point for CLI, rc, backend config, and configfile storage.

Risks: global mutable config state can make tests and concurrent operations order-dependent. `SetData` is ignored in memory-only mode. `SaveConfig` logs failure but does not return an error. `updateRemote` must avoid saving ephemeral keys and must handle obscure/no-obscure options correctly to avoid leaking passwords or double-obscuring.

Test signals: `config_test.go` checks loading via configfile, while configfile, crypt, configmap, and configstruct tests cover major dependencies. Many path and update flows are tested elsewhere outside this subset.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/fs/config/config.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/fs/config/config_read_password.go -->
# sources/user-network-fs/rclone/fs/config/config_read_password.go

Purpose: provides terminal-aware password input for supported OSes.

Important APIs/functions: `ReadPassword() string`, built under `!plan9`.

Control flow: obtains stdin file descriptor, falls back to `ReadLine("")` when stdin is not a terminal, otherwise calls `terminal.ReadPassword`, prints a newline to stderr, fatals on read error, and returns the password bytes as a string.

State and persistence behavior: no persistence. It reads from process stdin and writes a newline to stderr to restore prompt layout.

Dependencies and integration points: depends on `terminal.IsTerminal`, `terminal.ReadPassword`, `fs.Fatalf`, and the UI `ReadLine` fallback. Used by config password prompts in `crypt.go`/`ui.go`.

Risks: fatal-on-read-error exits the process. Non-terminal input echoes through `ReadLine`, which is appropriate for pipes but less secure than terminal password mode.

Test signals: no direct test in this subset; password behavior is indirectly exercised through crypt/UI tests with mocked input elsewhere.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/fs/config/config_read_password.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/fs/config/config_read_password_unsupported.go -->
# sources/user-network-fs/rclone/fs/config/config_read_password_unsupported.go

Purpose: provides a Plan 9 fallback for password input where `golang.org/x/term` support is unavailable.

Important APIs/functions: `ReadPassword() string`, built under `plan9`.

Control flow: simply delegates to `ReadLine("")`, meaning input is read as a normal line.

State and persistence behavior: no persistence; reads from stdin through the shared UI line reader.

Dependencies and integration points: keeps the config password API available on unsupported terminal platforms.

Risks: password entry is echoed on this platform fallback. This is explicitly documented in the file comments.

Test signals: no direct test in this subset.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/fs/config/config_read_password_unsupported.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/fs/config/config_test.go -->
# sources/user-network-fs/rclone/fs/config/config_test.go

Purpose: externally tests config loading through the installed `configfile` storage implementation.

Important APIs/functions: package init calls `configfile.Install`. `TestConfigLoad` switches `configPath` to `./testdata/plain.conf`, clears any config password, then inspects sections and keys from `config.Data()`.

Control flow: saves old config path, sets a test path, defers restoration, and asserts loaded section/key order matches expectations.

State and persistence behavior: mutates global `configPath` and password state during the test and restores config path afterward. It relies on `config.Data()` storage loading the selected file.

Dependencies and integration points: imports config as an external package, plus `configfile`, to verify the public install/load path rather than internals.

Risks: limited scope; it does not test save, missing config, environment overrides, or encrypted load. Global config path mutation makes restoration important.

Test signals: basic integration signal that configfile storage can load the bundled plaintext fixture.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/fs/config/config_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/fs/config/configfile/configfile.go -->
# sources/user-network-fs/rclone/fs/config/configfile/configfile.go

Purpose: implements `config.Storage` using an INI-like file via `goconfig`, with encrypted load/save support, auto-reload on external changes, symlink-aware atomic replacement, and mutex protection.

Important APIs/types/functions: `Install` installs `&Storage{}` into config. `Storage` stores a mutex, `*goconfig.ConfigFile`, and last file info. Internal methods `_check` and `_load`; public methods `Load`, `Save`, `Serialize`, `HasSection`, `DeleteSection`, `GetSectionList`, `GetKeyList`, `GetValue`, `SetValue`, and `DeleteKey`.

Control flow: `_check` stats the current config path and reloads if mtime or size changed. `_load` opens the config path, maps not-found to `config.ErrorConfigFileNotFound`, decrypts with `config.Decrypt`, and loads goconfig data; a defer guarantees an empty config object exists on errors. `Save` resolves symlinks, creates the config dir, writes serialized and encrypted data to a temp file, syncs and closes it, preserves existing file mode where possible, attempts group ownership copy on Unix, creates a backup temp file, renames old config to backup, then renames the new temp file into place and updates cached file info.

State and persistence behavior: all access locks `Storage.mu`. Data is persisted to the configured path unless config path is empty. Sections starting with `:` are treated as on-the-fly backends and are not saved. Save defaults new files to `0600` but preserves existing permissions. Temporary files are cleaned up by defers.

Dependencies and integration points: depends on `config.GetConfigPath`, `config.Decrypt`, `config.Encrypt`, `goconfig`, `file.MkdirAll`, and platform `attemptCopyGroup`. It satisfies `config.Storage`.

Risks: reload detection uses modtime/size and may miss rare same-size same-modtime changes. Atomic replacement behavior depends on filesystem rename semantics. Errors during rename can leave backup temp files intentionally preserved. On-the-fly backend sections are silently not saved beyond a log.

Test signals: `configfile_test.go` covers read/write operations, reload, missing/no-config behavior, save permissions, symlink targets, and piped config decryption behavior.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/fs/config/configfile/configfile.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/fs/config/configfile/configfile_other.go -->
# sources/user-network-fs/rclone/fs/config/configfile/configfile_other.go

Purpose: supplies a no-op `attemptCopyGroup` implementation for non-Unix platforms.

Important APIs/functions: `attemptCopyGroup(fromPath, toPath string)` is compiled when the OS is not in the Unix build tag set.

Control flow: no operation. It exists so `Storage.Save` can call the same helper cross-platform.

State and persistence behavior: does not alter file ownership or permissions.

Dependencies and integration points: complements `configfile_unix.go`. Used only during config save.

Risks: group ownership is not preserved on non-Unix platforms, which matches the stated platform model.

Test signals: no direct tests; platform-specific save tests are Linux-only in `configfile_test.go`.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/fs/config/configfile/configfile_other.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/fs/config/configfile/configfile_test.go -->
# sources/user-network-fs/rclone/fs/config/configfile/configfile_test.go

Purpose: tests configfile storage read/write/reload/save behavior, missing config behavior, symlink handling, and plaintext decrypt handling for non-seekable inputs.

Important APIs/functions: helpers `setConfigFile`, `toUnix`, and `pipedInput`. Tests include `TestConfigFile`, `TestConfigFileReload`, `TestConfigFileDoesNotExist`, `TestConfigFileNoConfig`, `TestConfigFileSave`, `TestConfigFileSaveSymlinkAbsolute`, and `TestPipedConfig`.

Control flow: `TestConfigFile` loads an INI fixture, verifies serialization/sections/keys/values, mutates values, deletes keys/sections, saves, and checks file contents. Reload test appends to the file after load and verifies the next read sees the change. Save tests create nested paths, check directory/file creation, permission preservation, read-only behavior, and expected Linux permission failures. Symlink tests verify saving through absolute and relative symlinks writes the target while preserving the link. Piped config tests ensure `config.Decrypt` can handle non-seekable plaintext without consuming the first line.

State and persistence behavior: tests mutate global config path and real temporary files. They validate temp-file replacement and mode behavior, not just in-memory storage.

Dependencies and integration points: uses `config.SetConfigPath`, `config.Decrypt`, OS filesystem calls, runtime OS checks, and `testify`.

Risks: some tests are platform-gated to Linux because permission semantics differ. Timing-based reload depends on file metadata changes but appending changes both size and content.

Test signals: strong integration coverage for configfile's core persistence guarantees and edge cases.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/fs/config/configfile/configfile_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/fs/config/configfile/configfile_unix.go -->
# sources/user-network-fs/rclone/fs/config/configfile/configfile_unix.go

Purpose: preserves group ownership when saving config files on Unix-like systems.

Important APIs/functions: `attemptCopyGroup(fromPath, toPath string)`.

Control flow: stats the existing config file, extracts `syscall.Stat_t`, starts with the old file's UID, prefers the current process user's UID when available, and calls `os.Chown` on the temp file with that UID and the old GID. Chown failures are logged at debug level.

State and persistence behavior: modifies ownership of the temporary config file before it is renamed into place. It does not alter file contents.

Dependencies and integration points: used by `Storage.Save` after creating the new temp file and before final rename. Depends on Unix build tags, `os/user`, `syscall`, and `fs.Debugf`.

Risks: user lookup or UID parsing may fail silently, falling back to the old UID. Chown can fail due to permissions; the save continues with a debug log.

Test signals: no direct unit test for group ownership in this subset; file mode behavior is tested on Linux in `configfile_test.go`.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/fs/config/configfile/configfile_unix.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/fs/config/configflags/configflags.go -->
# sources/user-network-fs/rclone/fs/config/configflags/configflags.go

Purpose: registers and applies global CLI flags that either map to `fs.ConfigOptionsInfo` or require special handling outside the generic config system.

Important APIs/functions: package globals store raw flag values such as verbosity, config/cache/temp dirs, delete mode booleans, bind address, disabled features, headers, metadata, and DSCP. `AddFlags(ci, flagSet)` registers generic options and special flags. `SetFlags(ci)` applies special flags to `fs.ConfigInfo`, config paths, and temp/cache dirs. `parseDSCP` maps numeric and named DSCP values to 6-bit codes.

Control flow: `AddFlags` delegates generic option registration to `flags.AddFlagsFromOptions`, then registers legacy/special flags. `SetFlags` folds obsolete dump flags into `ci.Dump`, resolves `-v`/`-q` conflicts with `--log-level`, chooses delete mode, resolves bind address to exactly one IP, parses disabled features/help, parses upload/download/general headers, parses lowercase metadata keys, shifts DSCP into traffic class bits, applies `--config`, `--cache-dir`, and `--temp-dir`, records whether `--multi-thread-streams` changed, then calls `ci.Reload`.

State and persistence behavior: raw flag package globals persist process-wide after parsing. Applying config path changes global config storage path; temp dir writes environment variables; cache dir updates config package global cache path. `ci` is mutated in place.

Dependencies and integration points: depends on pflag, config path helpers, rclone header parsers, metadata, network DNS lookup, and global `ConfigInfo.Reload`. It is part of CLI startup.

Risks: conflict errors call `fs.Fatalf`, exiting the process. `net.LookupIP` for `--bind` may depend on DNS and must return exactly one address. Package-level raw values make repeated flag parsing in tests difficult unless reset. DSCP names must remain accurate.

Test signals: no direct tests in this subset for configflags; behavior is indirectly validated by CLI/config tests elsewhere.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/fs/config/configflags/configflags.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/fs/config/configmap/configmap.go -->
# sources/user-network-fs/rclone/fs/config/configmap/configmap.go

Purpose: provides a small abstraction for reading/writing configuration from multiple sources with priorities, plus a simple map implementation that can be stringified or base64-encoded.

Important APIs/types/functions: `Priority` values are `PriorityNormal`, `PriorityConfig`, `PriorityDefault`, and `PriorityMax`. Interfaces are `Getter`, `Setter`, and `Mapper`. `Map` stores setter list and priority-sorted getters. Methods include `New`, `AddGetter`, `AddSetter`, `ClearSetters`, `ClearGetters`, `GetPriority`, `Get`, and `Set`. `Simple map[string]string` implements mapper methods plus `Human`, `String`, `Encode`, and `Decode`.

Control flow: getters are stable-sorted by priority so lower numeric priorities win while preserving insertion order within a priority. `GetPriority` scans until priority exceeds the provided max. `Set` writes to every setter. `Simple.string` sorts keys, optionally omits `=true` in human mode, quotes values containing parser-sensitive characters, and doubles single quotes. `Encode` JSON-marshals the map and base64 raw-encodes it; `Decode` strips all whitespace, base64-decodes, and JSON-unmarshals into the map.

State and persistence behavior: `Map` holds references to external getter/setter stores; `Set` mutates all configured setters. `Simple` is in-memory but its string and encoded forms are used in inline remotes and authorization blobs.

Dependencies and integration points: used throughout config loading, backend config, rc update/create, inline remote parsing, and `rclone authorize`. Depends on JSON, base64, sorting, and Unicode whitespace handling.

Risks: not internally synchronized; callers must avoid concurrent mutation. Decode into a nil `Simple` map works only when JSON allocates the map; empty input leaves the map unchanged. String quoting must stay compatible with fspath parser.

Test signals: internal and external configmap tests cover priority, setters/getters, clearing, string/human output, parser round trips, and encode/decode errors.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/fs/config/configmap/configmap.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/fs/config/configmap/configmap_external_test.go -->
# sources/user-network-fs/rclone/fs/config/configmap/configmap_external_test.go

Purpose: tests `configmap.Simple` string rendering from an external package and verifies the output round-trips through the public fspath parser.

Important APIs/functions: `TestSimpleString` covers machine string form with quoted values. `TestSimpleHuman` covers human-readable form with unquoted simple values and omitted `=true` booleans.

Control flow: each case renders a `Simple`, builds an inline remote string like `:local,<params>:`, parses it with `fspath.Parse`, and compares the parsed config map when applicable.

State and persistence behavior: no persistent state. The tests document stable sorted key order, quoting for special characters, and single-quote escaping.

Dependencies and integration points: depends on `configmap`, `fspath.Parse`, and `testify`. It protects compatibility between config map rendering and inline remote syntax.

Risks: tests intentionally assert exact strings, so formatting changes must be deliberate and parser-compatible.

Test signals: high signal for user-visible inline config representation and round-trip behavior.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/fs/config/configmap/configmap_external_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/fs/config/configmap/configmap_test.go -->
# sources/user-network-fs/rclone/fs/config/configmap/configmap_test.go

Purpose: tests the internal behavior of `configmap.Map` and `Simple` encode/decode.

Important APIs/functions: interface assertions for `Simple`; `TestConfigMapGet`, `TestConfigMapSet`, `TestConfigMapGetPriority`, `TestConfigMapClearGetters`, `TestConfigMapClearSetters`, `TestSimpleEncode`, and `TestSimpleDecode`.

Control flow: map tests add getters/setters in different orders and priorities, assert lookup precedence and mutation propagation, then clear by priority or all setters. Encode/decode tests compare exact base64 raw strings and decode whitespace-tolerant inputs, invalid base64, JSON `null`, and invalid JSON.

State and persistence behavior: tests mutate in-memory maps and verify `Map` stores getter/setter references. Encoded strings are stable because JSON map output is expected for the tested keys and used in CLI/token flows.

Dependencies and integration points: uses base64 and `testify`. It constrains behavior used by backend config, config storage overlays, and authorization blob passing.

Risks: map JSON order can be a compatibility concern, though Go's JSON encoder sorts map keys for string keys. No concurrency tests are present.

Test signals: strong coverage for priority and setter semantics plus error-wrapped encode/decode paths.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/fs/config/configmap/configmap_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/fs/config/configstruct/configstruct.go -->
# sources/user-network-fs/rclone/fs/config/configstruct/configstruct.go

Purpose: maps unstructured config maps into typed option structs and back through string conversion, using reflection and config tags.

Important APIs/types/functions: `camelToSnake`, `StringToInterface`, `InterfaceToString`, `Item`, `Items`, `Set`, `SetAny`, plus helpers `setValue` and `setIfSameType`. Supported built-ins include strings, numeric types, bool, `time.Duration`, `[]string`, and custom types implementing `Set(string) error` or `fmt.Stringer`.

Control flow: `Items` requires a pointer to a struct, iterates exported fields, uses `config` tags or CamelCase-to-snake conversion, skips `config:"-"`, recursively expands nested structs unless the field's address implements `Set`, and returns setters that write reflected values back. `Set` reads string config values and parses them into field types. `SetAny` first assigns values that already match the field type, otherwise stringifies the input and reparses it. Empty string parse errors are masked so empty config is treated like unset for non-string types.

State and persistence behavior: no global state. The target struct is mutated in place. Returned `Item.Set` closures capture struct fields and should be used while the original value remains valid.

Dependencies and integration points: used by option registration/config loading to fill `ConfigInfo` and backend option structs from `configmap.Getter` or rc maps. Depends on `encoding/csv`, reflection, time parsing, and configmap.

Risks: reflection panics are possible with unexported fields because `field.Addr().Interface()` requires interfaceable values; comments require public fields. Nested structs with `Set` are treated as scalar config items, which is important for rclone flag types. CSV handling for `[]string` must remain aligned with config syntax.

Test signals: configstruct tests cover item discovery, nested structs, tags, setting values, `SetAny`, conversions, error messages, and camel-to-snake internals.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/fs/config/configstruct/configstruct.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/fs/config/configstruct/configstruct_test.go -->
# sources/user-network-fs/rclone/fs/config/configstruct/configstruct_test.go

Purpose: externally tests the reflection-based config struct mapper and string conversion helpers.

Important APIs/types/functions: local structs `Conf`, `Conf2`, and `ConfNested` exercise plain fields, config tags, numeric/bool/duration/size suffix types, embedded structs, nested tagged structs, and a struct-like scalar `fs.Tristate`. Tests include `TestItemsError`, `TestItems`, `TestItemsNested`, `TestSetBasics`, `TestSetMore`, `TestSetFull`, `TestSetAnyFull`, `TestStringToInterface`, and `TestInterfaceToString`.

Control flow: item tests clean closure fields before comparing expected metadata. Set tests apply simple getter maps or `map[string]any` values and compare fully populated structs. Conversion tests are table-driven and assert exact values or exact wrapped error strings.

State and persistence behavior: no persistence; target structs are mutated in memory. Tests document that absent config preserves defaults and that empty arrays encode as empty strings while `[]string{""}` encodes as `""`.

Dependencies and integration points: imports `fs.Duration`, `fs.SizeSuffix`, and `fs.Tristate`, making sure custom rclone types work with the generic mapper. Uses `testify`.

Risks: exact error strings can be sensitive to upstream parser changes. Tests do not cover unexported fields or `config:"-"` in this file.

Test signals: strong behavioral coverage for type conversion, nested item naming, and default preservation.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/fs/config/configstruct/configstruct_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/fs/config/configstruct/internal_test.go -->
# sources/user-network-fs/rclone/fs/config/configstruct/internal_test.go

Purpose: tests the unexported `camelToSnake` helper inside the `configstruct` package.

Important APIs/functions: `TestCamelToSnake` covers empty string, simple field names, normal CamelCase, and all-caps initialisms such as `AccessKeyID`.

Control flow: table-driven pure function assertions compare generated config names.

State and persistence behavior: none. The helper determines default config key names when struct fields lack tags.

Dependencies and integration points: uses `testify/assert`. It protects naming used by `Items`, `Set`, and `SetAny`.

Risks: the regex strategy inserts underscores before uppercase runs; tests cover common initialism behavior but not every acronym pattern.

Test signals: focused coverage for a key naming primitive.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/fs/config/configstruct/internal_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/fs/config/crypt.go -->
# sources/user-network-fs/rclone/fs/config/crypt.go

Purpose: handles encrypted rclone config files, password acquisition, encryption/decryption, password key derivation, and password change/remove workflows.

Important APIs/functions: global `configKey`, `PasswordPromptOutput`, and `PassConfigKeyForDaemonization`. Public functions include `IsEncrypted`, `Decrypt`, `GetPasswordCommand`, `Encrypt`, `SetConfigPassword`, `ClearConfigPassword`, `ChangeConfigPasswordAndSave`, and `RemoveConfigPasswordAndSave`. Internal helpers include `getConfigPassword` and `changeConfigPassword`.

Control flow: `Decrypt` scans to the first non-empty non-comment line. Plaintext is returned as-is, including non-seekable stream recovery with `io.MultiReader`; unsupported encryption versions error. For encrypted configs it obtains a key from `--password-command`, `RCLONE_CONFIG_PASS`, `_RCLONE_CONFIG_KEY_FILE`, or interactive prompt, then base64-decodes secretbox ciphertext, extracts nonce, and retries prompts until secretbox opens. `Encrypt` passes plaintext through when no key is set; otherwise it writes a marker header, random nonce, and base64-encoded NaCl secretbox output. `SetConfigPassword` validates/normalizes via `checkPassword`, hashes `[` + password + `][rclone-config]` with SHA-256, and optionally writes an obscured key temp file for daemonized child processes.

State and persistence behavior: `configKey` is process-global and controls future saves. `_RCLONE_CONFIG_KEY_FILE` handoff deletes the temp file after reading. Password changes update `configKey` then call `SaveConfig`; removal clears the key and saves plaintext.

Dependencies and integration points: depends on `fs.ConfigInfo` for `AskPassword` and `PasswordCommand`, UI password functions, `obscure`, `secretbox`, base64, OS env/temp files, and configfile storage's `Decrypt`/`Encrypt` calls.

Risks: config encryption depends on global mutable key state, so tests and long-running processes must clear or set it deliberately. `Decrypt` can prompt interactively in loops unless disabled by config. Temp key file handling must avoid leaving key material behind on errors. Tokens/passwords may appear in subprocess command output if password command is misconfigured.

Test signals: `crypt_internal_test.go` covers password validation/normalization and password-command change flow; broader crypt tests outside this subset likely cover encrypt/decrypt round trips and password command errors.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/fs/config/crypt.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/fs/config/crypt_internal_test.go -->
# sources/user-network-fs/rclone/fs/config/crypt_internal_test.go

Purpose: internal tests for config password hashing/validation and password-change behavior using `--password-command`.

Important APIs/functions: helper `hashedKeyCompare`, `TestPassword`, and `TestChangeConfigPassword`.

Control flow: `TestPassword` clears `configKey` afterward, verifies empty and invalid UTF-8 passwords fail, checks different passwords hash differently, Unicode-normalized equivalents hash the same, and case differences remain distinct. `TestChangeConfigPassword` points config path at an encrypted fixture, writes a temporary Go password-command program that asserts `RCLONE_PASSWORD_CHANGE=1` and prints `asdf`, sets `ci.PasswordCommand`, calls `changeConfigPassword`, then loads config data and verifies decrypted sections/keys.

State and persistence behavior: directly mutates package-global `configKey`, global config path, and `fs.ConfigInfo.PasswordCommand`, restoring them in defers. It verifies password changes affect subsequent config load.

Dependencies and integration points: uses `go run` as a subprocess password command, OS temp files, encrypted testdata, and config storage `Data().Load`.

Risks: the subprocess requires a working Go toolchain in test environment. Global config state must be restored to avoid cross-test contamination.

Test signals: strong coverage for password normalization security expectations and the password-command environment contract during password changes.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/fs/config/crypt_internal_test.go -->
