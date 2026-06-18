# subset-b-009141 research

Grouped research report for Kopia internal cache, clock, logging, crypto, diff, directory, editor, and epoch files. Each section title preserves the exact source path and is wrapped for reconciliation into source-tree-aligned per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/internal/cache/persistent_lru_cache.go -->
# sources/sync-backup/kopia/internal/cache/persistent_lru_cache.go

Purpose: implements Kopia's persistent on-disk LRU cache with optional cache-entry protection, write coalescing per key, metrics, and size-based sweeping.

Important APIs/types/functions: `PersistentCache`, `GetOrLoad`, `Put`, `CacheStorage`, `Close`, `SweepSettings`, `NewPersistentCache`, `contentMetadataHeap`, and internal helpers `getPartial`, `getPartialCacheHit`, `deleteInvalidBlob`, `sweepLocked`, and `initialScan`.

Control flow: `GetOrLoad` first attempts a full cache read, then takes a per-key exclusive lock, retries the read, invokes the caller fetcher on miss, records miss metrics, and writes protected data through `Put`. `Put` reserves `pendingWriteBytes`, sweeps while holding `listCacheMutex`, releases the lock for protection/storage I/O, writes via `PutBlob`, then updates heap metadata. `initialScan` lists all storage blobs into an age-ordered heap and immediately sweeps.

State and persistence behavior: durable state is in `Storage` blobs named by cache keys. In-memory state tracks LRU timestamps, total protected bytes, pending writes, and failed deletion reinsertion. Full reads verify HMAC/encryption protection; partial reads intentionally disable integrity verification. Touches update storage mtimes subject to `TouchThreshold`.

Dependencies/integration: integrates `cacheprot.StorageProtection`, `gather`, `blob.Storage` metadata, `clock.Now`, `metrics`, `timetrack`, `releasable`, and package-local mutex/metric helpers.

Risks/test signals: risks include stale heap accounting after storage write failure, partial reads bypassing integrity checks, and sweep behavior under delete errors. Tests cover LRU eviction, protection mismatch, corrupt data deletion, nil receiver behavior, storage faults, min sweep age, and default storage setup.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/internal/cache/persistent_lru_cache.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/internal/cache/persistent_lru_cache_test.go -->
# sources/sync-backup/kopia/internal/cache/persistent_lru_cache_test.go

Purpose: validates persistent LRU cache correctness, fault tolerance, nil behavior, protection mismatch handling, and default construction against map-backed blob storage.

Important APIs/types/functions: `TestPersistentLRUCache`, `TestPersistentLRUCache_Invalid`, `TestPersistentLRUCache_GetDeletesInvalidBlob`, `TestPersistentLRUCache_PutIgnoresStorageFailure`, sweep tests, `faultyCache`, and helpers `verifyCached`, `verifyNotCached`, `verifyBlobExists`, `verifyBlobDoesNotExist`.

Control flow: tests create map/faulty storages, instantiate `NewPersistentCache`, write blobs through `Put`, read with `TestingGetFull`/`GetOrLoad`, inject storage faults, corrupt stored bytes, close/reopen caches, and assert storage-visible blob presence.

State and persistence behavior: tests prove entries persist across cache instances, protection keys gate readability, corrupted entries are treated as misses and scheduled for deletion, and sweep decisions are observable in the backing `DataMap`.

Dependencies/integration: uses `blobtesting`, `cacheprot.ChecksumProtection`, `clock.Now`, `fault`, `gather`, `testlogging`, `testutil`, and `blob` errors.

Risks/test signals: good coverage for single-thread behavior and storage errors, but little concurrency stress. Sleep-based sweep timing can be slow/flaky if timing thresholds change. The file documents that `Put` logs but does not propagate storage write failures.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/internal/cache/persistent_lru_cache_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/internal/cachedir/cachedir.go -->
# sources/sync-backup/kopia/internal/cachedir/cachedir.go

Purpose: writes the `CACHEDIR.TAG` marker that tells backup/indexing tools that a directory contains disposable cache data.

Important APIs/types/functions: `CacheDirMarkerFile`, `CacheDirMarkerHeader`, `WriteCacheMarker`, and private `cacheDirMarkerContents`.

Control flow: `WriteCacheMarker` no-ops for an empty directory string, stats the target marker, accepts any existing file at least as large as the Kopia marker contents, otherwise creates/truncates the marker file, writes the fixed tag text, and closes it.

State and persistence behavior: persistent state is a file named `CACHEDIR.TAG` under the cache directory. The function does not create the parent directory and treats non-`IsNotExist` stat errors as unexpected.

Dependencies/integration: uses `os`, `filepath`, and `pkg/errors`. Cache directory setup code can call this after ensuring the directory exists.

Risks/test signals: a too-large but wrong marker file is accepted without validating the header. Error paths include stat, create, write, and close failures. No tests are listed for this file in the work item.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/internal/cachedir/cachedir.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/internal/cacheprot/storage_protection.go -->
# sources/sync-backup/kopia/internal/cacheprot/storage_protection.go

Purpose: defines pluggable protection for local cache entries: no protection, HMAC checksum protection, and authenticated encryption.

Important APIs/types/functions: `StorageProtection`, `NoProtection`, `ChecksumProtection`, `AuthenticatedEncryptionProtection`, `nullStorageProtection`, `checksumProtection`, `authenticatedEncryptionProtection`, and `OverheadBytes`.

Control flow: callers pass cache bytes to `Protect`, which resets the output and writes either raw bytes, HMAC-appended bytes, or AES-GCM-encrypted bytes. `Verify` reverses that process, returning an error on HMAC or decryption failure. Authenticated encryption derives an IV from SHA-256 of the cache item id.

State and persistence behavior: no package-local mutable state. The protected bytes are stored by the cache layer. `OverheadBytes` must match the exact storage overhead because `PersistentCache.Put` reserves space based on it.

Dependencies/integration: uses `gather`, internal `hmac`, `impossible`, and repository `encryption` with algorithm `AES256-GCM-HMAC-SHA256`.

Risks/test signals: deterministic IVs are safe only if each key/id is unique for a stable plaintext write domain. A mismatch between overhead and encryptor output panics in the cache. Tests cover bit-flip detection for HMAC/encryption and pass-through behavior for no protection.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/internal/cacheprot/storage_protection.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/internal/cacheprot/storage_protection_test.go -->
# sources/sync-backup/kopia/internal/cacheprot/storage_protection_test.go

Purpose: verifies the three `StorageProtection` implementations reset output buffers, round-trip payloads, and detect corruption where expected.

Important APIs/types/functions: `TestNoStorageProtection`, `TestHMACStorageProtection`, `TestEncryptionStorageProtection`, and shared helper `testStorageProtection`.

Control flow: each test protects a fixed payload into a buffer preloaded with dummy bytes, verifies into another preloaded buffer, compares unprotected bytes, flips the first protected byte, and asserts verification behavior based on whether the implementation should protect against bit flips.

State and persistence behavior: tests are in-memory only. They assert buffer reset semantics that matter to callers reusing `gather.WriteBuffer`.

Dependencies/integration: uses `cacheprot`, `gather`, `bytes`, and `testify/require`.

Risks/test signals: coverage is compact but important. It does not validate overhead values, id binding for authenticated encryption, wrong-key failures, or behavior with empty/large payloads.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/internal/cacheprot/storage_protection_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/internal/clock/now.go -->
# sources/sync-backup/kopia/internal/clock/now.go

Purpose: provides shared wall-clock normalization for Kopia clock abstractions by stripping Go's monotonic time component.

Important APIs/types/functions: private `discardMonotonicTime(time.Time) time.Time`.

Control flow: converts a `time.Time` to Unix nanoseconds and reconstructs it with `time.Unix(0, ...)`, preserving wall time while discarding monotonic metadata.

State and persistence behavior: no state or persistence. The normalized timestamp is suitable for persisted timestamps and long-duration wall-clock comparisons, including across system sleep.

Dependencies/integration: used by production and testing `Now` implementations. It avoids using monotonic durations where Kopia wants wall-clock duration semantics.

Risks/test signals: behavior depends on Unix nanosecond range and loses location information. It is indirectly tested through clock consumers and sleep/timing tests, not by a dedicated unit test here.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/internal/clock/now.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/internal/clock/now_prod.go -->
# sources/sync-backup/kopia/internal/clock/now_prod.go

Purpose: production implementation of `clock.Now` for non-`testing` builds.

Important APIs/types/functions: build tag `!testing` and function `Now() time.Time`.

Control flow: calls `time.Now()` and immediately passes the result through `discardMonotonicTime`.

State and persistence behavior: no state. It returns wall-clock timestamps without monotonic components, which are safe to compare after serialization and across long sleeps.

Dependencies/integration: used by packages such as cache, content logging, and epoch manager when no injected time function is supplied.

Risks/test signals: no direct tests in this file. Runtime correctness depends on the shared `discardMonotonicTime` helper and callers accepting wall-clock rather than monotonic timing.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/internal/clock/now_prod.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/internal/clock/now_testing.go -->
# sources/sync-backup/kopia/internal/clock/now_testing.go

Purpose: testing-build implementation of `clock.Now` that can be overridden by a fake time HTTP endpoint.

Important APIs/types/functions: build tag `testing`, variable `Now`, `init`, `getTimeFromServer`, and constant `refreshServerTimeEvery`.

Control flow: default `Now` mirrors production. During init, `KOPIA_FAKE_CLOCK_ENDPOINT` replaces `Now` with a closure that fetches `{time, validFor}` JSON over HTTP, caches an offset from real local time to server time, and refreshes after `validFor` expires.

State and persistence behavior: closure state includes a mutex, latest server time info, next refresh real time, and local offset. No persistent writes. Fatal logging aborts tests on endpoint failures or malformed responses.

Dependencies/integration: uses `net/http`, `encoding/json`, `os`, `sync`, and `log`. Supports integration/fake-time tests across processes.

Risks/test signals: uses `http.Get` without context and `log.Fatalf`, so fake endpoint issues terminate the process. No direct tests are listed; coverage is mostly through testing builds that set the environment variable.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/internal/clock/now_testing.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/internal/clock/sleep.go -->
# sources/sync-backup/kopia/internal/clock/sleep.go

Purpose: provides an interruptible sleep helper that returns whether the requested duration completed.

Important APIs/types/functions: `SleepInterruptibly(ctx context.Context, dur time.Duration) bool`.

Control flow: performs a `select` between `ctx.Done()` and `time.After(dur)`. It returns `false` when the context is canceled first and `true` when the timer fires first.

State and persistence behavior: no state or persistence. The `time.After` timer is allocated for each call and not stopped explicitly, which is acceptable for simple one-shot sleep use.

Dependencies/integration: used anywhere long waits should honor cancellation.

Risks/test signals: for very high-frequency use, repeated `time.After` can allocate. Tests assert both cancellation-before-duration and full-duration completion with broad timing bounds.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/internal/clock/sleep.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/internal/clock/sleep_test.go -->
# sources/sync-backup/kopia/internal/clock/sleep_test.go

Purpose: validates that `SleepInterruptibly` exits early on context cancellation and returns true after a complete sleep.

Important APIs/types/functions: `TestSleepInterruptibly_ContextCanceled`, `TestSleepInterruptibly_ContextNotCanceled`, `context.WithTimeout`, and `timetrack.StartTimer`.

Control flow: the cancellation test sets a 100 ms timeout against a 3 second sleep and expects `false` plus elapsed time between 90 ms and 1 second. The non-canceled test sleeps 100 ms on `context.Background()` and expects `true` within the same broad duration bounds.

State and persistence behavior: no persistent state. Tests measure elapsed real time.

Dependencies/integration: uses `testify/require`, `timetrack`, `context`, and `time`.

Risks/test signals: wall-clock assertions may be flaky on overloaded systems, though the 1 second upper bound is generous. The tests do not cover already-canceled contexts or zero/negative durations.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/internal/clock/sleep_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/internal/completeset/complete_set.go -->
# sources/sync-backup/kopia/internal/completeset/complete_set.go

Purpose: detects complete groups of blob metadata following Kopia's `<prefix>-s<set>-c<count>` naming convention.

Important APIs/types/functions: `FindFirst`, `ExcludeIncomplete`, and `FindAll`.

Control flow: `FindAll` scans metadata in input order. Malformed names or malformed counts are emitted as singleton complete sets. Well-formed entries are grouped by set id (`s...`), and a group is emitted as soon as its observed length reaches the declared count. `FindFirst` returns the first emitted complete set; `ExcludeIncomplete` flattens all emitted sets.

State and persistence behavior: no persistent state. Output ordering depends on input order and on the first moment a set becomes complete.

Dependencies/integration: used by epoch manager to ignore incomplete/crashed compaction blob sets.

Risks/test signals: the parser only examines split parts 1 and 2, so prefixes containing dashes do not match the documented convention. Duplicate or over-complete sets can produce surprising grouping. Tests cover empty, malformed, complete, incomplete, and competing sets.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/internal/completeset/complete_set.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/internal/completeset/complete_set_test.go -->
# sources/sync-backup/kopia/internal/completeset/complete_set_test.go

Purpose: table-driven coverage for complete-set detection and filtering.

Important APIs/types/functions: `TestFindFirstAndAll`, `idsFromMetadataSets`, and `dummyMetadataForIDs`.

Control flow: each case builds metadata from blob IDs, calls `FindFirst`, `FindAll`, and `ExcludeIncomplete`, converts results back to IDs, and compares expected ordering.

State and persistence behavior: in-memory only. The tests encode the important ordering rule that the first complete set is whichever set becomes complete earliest in input order, with malformed IDs treated as singleton sets.

Dependencies/integration: uses `completeset`, `blob`, and `testify/require`.

Risks/test signals: tests do not cover duplicate members in the same set or names with extra dash-separated parts before `s`/`c`. The existing cases are strong regression signals for epoch compaction set discovery.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/internal/completeset/complete_set_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/internal/connection/reconnector.go -->
# sources/sync-backup/kopia/internal/connection/reconnector.go

Purpose: manages a single reusable connection and reconnects/retries operations when connector-specific closed-connection errors occur.

Important APIs/types/functions: `Connection`, `ConnectorImpl`, `Reconnector`, `GetOrOpenConnection`, generic `UsingConnection[T]`, `UsingConnectionNoResult`, `CloseActiveConnection`, and `NewReconnector`.

Control flow: `GetOrOpenConnection` lazily opens a connection under mutex and caches it. `UsingConnection` wraps open/callback execution in `retry.WithExponentialBackoff`, closes the active connection on open errors or callback errors classified by `IsConnectionClosedError`, and returns the callback result. `CloseActiveConnection` clears and closes the cached connection.

State and persistence behavior: state is only the in-memory active connection protected by a mutex. There is no pool, persistence, or per-operation lock around callback use.

Dependencies/integration: integrates with storage/provider connectors that implement closed-error classification, and with `retry` and Kopia logging.

Risks/test signals: callbacks can use the same connection concurrently because reuse is not serialized after retrieval. A connector must classify errors correctly or retries will not happen. Tests cover reuse, reconnect after closed errors, fatal open errors, nested use, close, and parallel callers.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/internal/connection/reconnector.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/internal/connection/reconnector_test.go -->
# sources/sync-backup/kopia/internal/connection/reconnector_test.go

Purpose: exercises `Reconnector` lifecycle, retry behavior, connection reuse, explicit close, and concurrent use with a fake connector.

Important APIs/types/functions: `fakeConnector`, `fakeConnection`, `TestConnection`, `UsingConnection`, `UsingConnectionNoResult`, and `errgroup.Group`.

Control flow: the test opens a first connection, forces a closed-connection callback error to trigger reconnect, verifies later calls reuse connection 2, nests a use inside another callback, explicitly closes, verifies a new connection 3, tests fatal open error propagation, tests retry after a classified open failure, and runs three parallel callbacks.

State and persistence behavior: fake connector tracks connection IDs via `atomic.Int32` and one-shot `nextError`. No durable state.

Dependencies/integration: uses `testlogging`, `testutil.EnsureType`, `errgroup`, `time.Sleep`, and `testify/require`.

Risks/test signals: the fake connection `isClosed` flag is not used by connector operations, so tests validate control flow rather than real I/O failure. Parallel assertions confirm shared connection reuse but not data-race safety of real connection implementations.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/internal/connection/reconnector_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/internal/contentlog/contentlog_benchmark_test.go -->
# sources/sync-backup/kopia/internal/contentlog/contentlog_benchmark_test.go

Purpose: benchmarks the low-allocation content logger across context params, logger params, content ID params, and `Log` through `Log6`.

Important APIs/types/functions: `BenchmarkLogger`, `contentlog.WithParams`, `contentlog.NewLogger`, `Log`, `Log1` through `Log6`, `logparam`, and `contentparam.ContentID`.

Control flow: parses a fixed content index ID, attaches context params, creates a logger with one logger-level param and a sink that discards bytes, then repeatedly emits messages with zero through six strongly typed params inside `b.Loop()`.

State and persistence behavior: benchmark output is discarded; state is pooled JSON writer reuse and context-carried params.

Dependencies/integration: uses `repo/content/index` parsing and logging parameter packages.

Risks/test signals: benchmark checks performance shape but has no assertions about allocation counts in this file. It is useful for catching regressions in generic logging paths when run with Go benchmark allocation reporting.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/internal/contentlog/contentlog_benchmark_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/internal/contentlog/contentlog_json_writer.go -->
# sources/sync-backup/kopia/internal/contentlog/contentlog_json_writer.go

Purpose: implements a pooled JSON writer optimized for direct, low-allocation construction of log entries and parameter values.

Important APIs/types/functions: `JSONWriter`, `ParamWriter`, object/list methods, field/element writers for strings, ints, uints, bools, null, errors, times, `RawJSONField`, `NewJSONWriter`, `Release`, `Result`, and `GetBufferForTesting`.

Control flow: writer methods maintain a current separator and a stack of enclosing separators. Fields call `beforeField`; array elements call `beforeElement`. Strings are escaped byte by byte, with standard escapes and `\u00XX` escapes for control characters below space. Times are formatted manually as UTC microsecond timestamps.

State and persistence behavior: state is an internal byte buffer, separator, and separator stack returned to a `freepool`. Callers must not retain/mutate writer state after `Release`; logger output receives the byte slice before release.

Dependencies/integration: used by `contentlog.Logger`, `logparam`, and content-specific params.

Risks/test signals: `RawJSONField` trusts callers to provide valid JSON. String iteration is byte-oriented, which is fine for UTF-8 pass-through but must preserve multi-byte data. Tests cover JSON validity, escaping, numeric/time values, nesting, and control-character output.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/internal/contentlog/contentlog_json_writer.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/internal/contentlog/contentlog_json_writer_test.go -->
# sources/sync-backup/kopia/internal/contentlog/contentlog_json_writer_test.go

Purpose: validates `JSONWriter` output for object/list structure, scalar types, string escaping, time formatting, edge numeric values, and control characters.

Important APIs/types/functions: tests for empty objects, all types, int/uint field and element variants, null/error/time fields, list writing, string escaping raw output, and exhaustive control-character handling.

Control flow: tests construct JSON through writer methods, parse with `encoding/json`, compare maps/slices, and inspect raw output for escape sequences.

State and persistence behavior: in-memory only. Tests exercise writer reuse only through `NewJSONWriter`/`Release`, not cross-call buffer aliasing.

Dependencies/integration: uses `encoding/json`, `strings`, `time`, `os.Stdout` in one debug encode, and `testify/require`.

Risks/test signals: the file includes an older test comment describing unescaped control-character behavior, while later tests require proper `\u00XX` escaping; the current implementation matches the stronger later expectations. Numeric comparisons through `map[string]any` lose integer precision by converting to `float64`.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/internal/contentlog/contentlog_json_writer_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/internal/contentlog/contentlog_logger.go -->
# sources/sync-backup/kopia/internal/contentlog/contentlog_logger.go

Purpose: provides strongly typed JSON content logging with context params, logger-level params, generic entries, and low allocation message helpers.

Important APIs/types/functions: `WriterTo`, `Logger`, `OutputFunc`, `Emit`, `Log`, `Log1` through `Log6`, `WithParams`, `NewLogger`, `RandomSpanID`, `HashSpanID`, and `debugMessageWithParams`.

Control flow: `Emit` returns early for nil logger/output, gets a pooled `JSONWriter`, writes object start, timestamp `t`, logger params, context params from a private context key, entry fields, newline, and sends the buffer to output. `LogN` helpers instantiate generic message structs with void params for unused slots.

State and persistence behavior: logger stores immutable params, output callback, and a time function defaulting to `clock.Now`. Context params are copied/appended when nested. Span IDs are random 5-byte base32 or SHA-256-derived base32 prefixes.

Dependencies/integration: used by epoch manager and other structured logging code; integrates `logparam` and `contentparam`.

Risks/test signals: output callback receives a pooled buffer slice; it must copy if retaining asynchronously. `rand.Read` errors are ignored. Tests cover nil handling, param ordering/content, custom entries, multiple newline-delimited records, errors, and span ID shape indirectly.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/internal/contentlog/contentlog_logger.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/internal/contentlog/contentlog_logger_test.go -->
# sources/sync-backup/kopia/internal/contentlog/contentlog_logger_test.go

Purpose: validates logger construction, nil-safe logging, typed log helpers from zero to six params, custom entries, multiple records, and error parameter handling.

Important APIs/types/functions: `TestNewLogger`, `TestLog`, `TestLog1` through `TestLog6`, `TestEmit`, `TestLoggerMultipleLogs`, `TestLoggerErrorHandling`, `customLogEntry`, and local `testError`.

Control flow: tests capture output into byte slices, emit logs with different helper functions, unmarshal JSON, and assert message field `m`, timestamp presence, logger params, context/custom params, and newline-delimited multi-entry behavior.

State and persistence behavior: in-memory capture only. Tests rely on output callbacks appending/copying bytes before writer release.

Dependencies/integration: uses `contentlog`, `logparam`, `encoding/json`, `strings`, and `testify/require`.

Risks/test signals: tests parse uint64/int64 through JSON float values, so they do not detect precision-preserving downstream requirements. They do not assert allocation counts; those are covered in `logparam` tests and benchmarks.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/internal/contentlog/contentlog_logger_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/internal/contentlog/logparam/logparam.go -->
# sources/sync-backup/kopia/internal/contentlog/logparam/logparam.go

Purpose: supplies typed parameter constructors that write fields into `contentlog.JSONWriter`.

Important APIs/types/functions: `String`, `Int64`, `Int`, `Int32`, `Bool`, `Time`, `Error`, `UInt64`, `UInt32`, `Duration`, and param structs implementing `WriteValueTo`.

Control flow: each constructor returns a small value struct containing key and typed value. `WriteValueTo` dispatches to the matching JSON writer field method. `Duration` logs microseconds, and `Error` logs `null` for nil.

State and persistence behavior: no mutable state. Values are intended to be stack-friendly and zero-allocation when used directly.

Dependencies/integration: imports `contentlog` and `time`. Used by content logging callers, especially epoch manager diagnostics.

Risks/test signals: caller-provided keys are not escaped beyond JSON string field writing, and duplicate keys are allowed. Duration truncates sub-microsecond values. Tests assert output and zero allocations for constructors and writer methods.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/internal/contentlog/logparam/logparam.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/internal/contentlog/logparam/logparam_test.go -->
# sources/sync-backup/kopia/internal/contentlog/logparam/logparam_test.go

Purpose: verifies typed log parameter constructors and `WriteValueTo` methods produce valid JSON and avoid allocations.

Important APIs/types/functions: tests for `String`, `Int64`, `Int`, `Int32`, `Bool`, `Time`, `Error`, `UInt64`, `Duration`, and `TestWriteValueToMemoryAllocations`.

Control flow: table-driven tests measure `testing.AllocsPerRun` for each constructor, write a one-field JSON object through `JSONWriter`, unmarshal it, and compare expected values. The allocation test reuses one writer while invoking each `WriteValueTo`.

State and persistence behavior: in-memory only. The tests verify param values are immutable enough for repeated writer use.

Dependencies/integration: uses `clock.Now`, `contentlog`, `pkg/errors`, `encoding/json`, and `testify/require`.

Risks/test signals: repeated writes to the same writer in allocation tests do not reset the buffer, so allocation measurement is the main signal rather than JSON validity there. JSON unmarshalling converts large integers to floats, masking precision concerns.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/internal/contentlog/logparam/logparam_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/internal/contentparam/contentid_params.go -->
# sources/sync-backup/kopia/internal/contentparam/contentid_params.go

Purpose: provides a content-ID-specific logging parameter that writes shortened content IDs as raw JSON.

Important APIs/types/functions: `ContentID`, private `contentIDParam`, `WriteValueTo`, and `maxLoggedContentIDLength`.

Control flow: `ContentID` captures key and `index.ID`. `WriteValueTo` allocates a fixed stack buffer, asks `index.ID.AppendToJSON` to append a JSON value capped to five content ID characters, and writes it with `RawJSONField`.

State and persistence behavior: no mutable or persistent state. The raw JSON value comes from the content index ID implementation.

Dependencies/integration: integrates `contentlog.JSONWriter` with `repo/content/index.ID`. Used by content logging benchmark and likely content operation logs.

Risks/test signals: because it uses `RawJSONField`, correctness depends on `AppendToJSON` returning valid JSON. The five-character cap deliberately trades traceability for concise logs. No direct test file is listed for this package item.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/internal/contentparam/contentid_params.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/internal/crypto/aesgcm.go -->
# sources/sync-backup/kopia/internal/crypto/aesgcm.go

Purpose: encrypts and decrypts byte slices using AES-256-GCM with keys derived from a master key and salt.

Important APIs/types/functions: `EncryptAes256Gcm`, `DecryptAes256Gcm`, `initCrypto`, constants `purposeAESKey` and `purposeAuthData`, and `errPlaintextTooLarge`.

Control flow: `initCrypto` derives a 32-byte AES key and 32-byte auth-data value via HKDF, builds AES and GCM. Encryption allocates nonce+ciphertext+tag, fills a random nonce, and seals with derived auth data as additional authenticated data. Decryption derives the same material, checks minimum length, copies input, splits nonce/payload, and opens in place.

State and persistence behavior: ciphertext stores the nonce prefix and GCM payload. There is no package state. Auth data binds ciphertext to master key/salt/purpose separation.

Dependencies/integration: uses `crypto/aes`, `cipher`, `rand.Reader`, `io.ReadFull`, and `DeriveKeyFromMasterKey`.

Risks/test signals: random nonce generation errors propagate. The decrypt comment says "encrypts" but implementation decrypts. No direct AES-GCM test is listed; coverage likely comes through repository encryption callers.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/internal/crypto/aesgcm.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/internal/crypto/key_derivation.go -->
# sources/sync-backup/kopia/internal/crypto/key_derivation.go

Purpose: derives purpose-specific keys from a primary master key using HKDF-SHA256.

Important APIs/types/functions: `DeriveKeyFromMasterKey` and `errInvalidMasterKey`.

Control flow: rejects nil/empty master keys, then calls `hkdf.Key(sha256.New, masterKey, salt, purpose, length)` and wraps any error.

State and persistence behavior: stateless. Derived keys are returned to callers such as AES-GCM initialization and are not stored by this package.

Dependencies/integration: uses Go `crypto/hkdf` and `crypto/sha256`, plus `pkg/errors`.

Risks/test signals: security depends on non-empty high-entropy master keys and unique purpose strings. Tests assert a stable known vector and error behavior for nil/empty master keys.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/internal/crypto/key_derivation.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/internal/crypto/key_derivation_test.go -->
# sources/sync-backup/kopia/internal/crypto/key_derivation_test.go

Purpose: checks HKDF master-key derivation against a fixed expected output and invalid key handling.

Important APIs/types/functions: `TestDeriveKeyFromMasterKey` with subtests `ReturnsKey`, `ErrorOnNilMasterKey`, and `ErrorOnEmptyMasterKey`.

Control flow: derives a 32-byte key from fixed master key, salt, and purpose, formats it as hex, and compares to a hard-coded expected string. Error subtests call derivation with nil and empty keys and require nil output plus an error.

State and persistence behavior: no state or persistence.

Dependencies/integration: uses `crypto.DeriveKeyFromMasterKey`, `fmt.Sprintf`, and `testify/require`.

Risks/test signals: the vector protects against accidental HKDF parameter changes. It does not test different lengths, empty salt, or AES-GCM integration.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/internal/crypto/key_derivation_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/internal/crypto/pb_key_deriver_insecure_testing.go -->
# sources/sync-backup/kopia/internal/crypto/pb_key_deriver_insecure_testing.go

Purpose: testing-only password key deriver that produces fast deterministic keys for tests.

Important APIs/types/functions: build tag `testing`, `TestingOnlyInsecurePBKeyDerivationAlgorithm`, `insecureKeyDeriver`, and its `deriveKeyFromPassword`.

Control flow: init registers the algorithm name. Derivation hashes only the password with SHA-256 and returns the requested prefix of the digest.

State and persistence behavior: mutates the package-global key-deriver registry at init. No persistent state.

Dependencies/integration: used by tests that need password derivation without PBKDF2/scrypt cost.

Risks/test signals: intentionally ignores salt and is insecure; build tag must prevent production inclusion. If `keySize` exceeds SHA-256 length it will panic by slicing beyond the digest, so tests should request safe sizes.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/internal/crypto/pb_key_deriver_insecure_testing.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/internal/crypto/pb_key_deriver_pbkdf2.go -->
# sources/sync-backup/kopia/internal/crypto/pb_key_deriver_pbkdf2.go

Purpose: registers and implements PBKDF2-SHA256 password-based key derivation.

Important APIs/types/functions: `Pbkdf2Algorithm`, constants for minimum salt length and iterations, `pbkdf2KeyDeriver`, init registration, and `deriveKeyFromPassword`.

Control flow: init registers algorithm `pbkdf2-sha256-600000` with 600,000 iterations and 16-byte minimum salt. Derivation rejects short salts, calls `pbkdf2.Key(sha256.New, password, salt, iterations, keySize)`, wraps errors, and returns the derived key.

State and persistence behavior: updates the global deriver registry during init. Derived keys are returned only to callers.

Dependencies/integration: used by `DeriveKeyFromPassword`; imports Go `crypto/pbkdf2`, `sha256`, and `pkg/errors`.

Risks/test signals: high iteration count impacts latency by design. Error string has typo "atleast". No direct listed test covers PBKDF2 vectors or short salt behavior in this work item.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/internal/crypto/pb_key_deriver_pbkdf2.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/internal/crypto/pb_key_deriver_scrypt.go -->
# sources/sync-backup/kopia/internal/crypto/pb_key_deriver_scrypt.go

Purpose: registers and implements scrypt password-based key derivation.

Important APIs/types/functions: `ScryptAlgorithm`, `scryptMinSaltLength`, `scryptKeyDeriver`, init registration, and `deriveKeyFromPassword`.

Control flow: init registers algorithm `scrypt-65536-8-1` with N=65536, r=8, p=1, and a 16-byte minimum salt. Derivation rejects short salts and calls `scrypt.Key`.

State and persistence behavior: only global registry mutation at init. Derived key bytes are returned to the caller.

Dependencies/integration: used by `DeriveKeyFromPassword`; imports `golang.org/x/crypto/scrypt` and `pkg/errors`.

Risks/test signals: scrypt memory/CPU cost is substantial and can affect unlock performance. No direct tests listed here cover vectors, salt rejection, or unsupported key sizes.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/internal/crypto/pb_key_deriver_scrypt.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/internal/crypto/pb_key_derivers.go -->
# sources/sync-backup/kopia/internal/crypto/pb_key_derivers.go

Purpose: provides the registry and dispatch function for password-based key derivation algorithms.

Important APIs/types/functions: `passwordBasedKeyDeriver`, global `keyDerivers`, `registerPBKeyDeriver`, `DeriveKeyFromPassword`, and `supportedPBKeyDerivationAlgorithms`.

Control flow: concrete deriver files register algorithm names during init. Registration panics on duplicates. `DeriveKeyFromPassword` looks up the requested algorithm, returns an error listing supported names if absent, otherwise delegates to the deriver.

State and persistence behavior: package-global map stores derivers for process lifetime. No synchronization is used because mutation occurs during init.

Dependencies/integration: called by repository password/key setup code. Testing builds add the insecure testing algorithm.

Risks/test signals: supported algorithm list is map-order dependent, so error messages are nondeterministically ordered. No direct test listed here covers duplicate registration or unsupported algorithms.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/internal/crypto/pb_key_derivers.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/internal/diff/diff.go -->
# sources/sync-backup/kopia/internal/diff/diff.go

Purpose: compares two Kopia filesystem trees, emits human-readable differences, accumulates stats, optionally runs an external diff command, and finds related snapshot manifests.

Important APIs/types/functions: `EntryTypeStats`, `Stats`, `Comparer`, `Compare`, `Close`, `Stats`, `NewComparer`, `GetPrecedingSnapshot`, `GetTwoLatestSnapshotsForASource`, `compareEntry`, `compareDirectories`, `compareFiles`, and `compareMetadata`.

Control flow: comparison recurses directory entries by name. Matching object IDs short-circuit content comparison but still check metadata. Adds/removes update stats and can download files to temp `old/` and `new/` paths for external diff. Existing entries compare metadata, type changes, and file changes. Snapshot helpers sort manifests by start time and return predecessor/latest pair.

State and persistence behavior: comparer owns a temp directory removed by `Close`; external diff downloads transient file copies. Stats are reset per `Compare`.

Dependencies/integration: integrates `fs`, `object`, `snapshotfs`, `snapshot`, `repo`, external commands, and `iocopy`.

Risks/test signals: external diff exit status is ignored. Directory comparison assumes names are unique. Tests cover directory/file changes, metadata-only object-ID matches, stats, and snapshot helper ordering/errors.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/internal/diff/diff.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/internal/diff/diff_test.go -->
# sources/sync-backup/kopia/internal/diff/diff_test.go

Purpose: validates filesystem comparison output/stats and snapshot-selection helpers.

Important APIs/types/functions: fake `testFile`/`testDirectory`, `TestCompareEmptyDirectories`, `TestCompareIdenticalDirectories`, `TestCompareDifferentDirectories`, metadata-difference tests, `TestGetPrecedingSnapshot`, `TestGetTwoLatestSnapshots`, and helper manifest/object ID functions.

Control flow: tests build synthetic entries with names, modes, owners, mtimes, content, and object IDs, run `NewComparer`/`Compare`, assert output strings and `Stats`, then use an in-memory repository test environment to save snapshot manifests and query predecessor/latest behavior.

State and persistence behavior: comparer temp dirs are cleaned through `t.Cleanup`. Repository tests persist manifests in a test repository.

Dependencies/integration: uses `repotesting`, `snapshot.SaveSnapshot`, `content.IDFromHash`, `blake3`, and filesystem interfaces.

Risks/test signals: tests do not exercise external diff command execution or download error paths. They strongly cover object-ID metadata shortcuts and snapshot time sorting.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/internal/diff/diff_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/internal/dirutil/mksubdirall.go -->
# sources/sync-backup/kopia/internal/dirutil/mksubdirall.go

Purpose: safely creates subdirectories under an existing top-level directory without recreating the top-level directory if it is missing or unmounted.

Important APIs/types/functions: `ErrTopLevelDirectoryNotFound`, `OSInterface`, `MkSubdirAll`, `trimTrailingSeparator`, and `getParent`.

Control flow: trims trailing separators, rejects `subDir` paths not longer than `topLevelDir`, tries to `Mkdir(subDir)`, recursively creates the parent only on `IsNotExist`, retries, and treats success or `IsExist` as success.

State and persistence behavior: persistent effect is directory creation below the top-level path. It deliberately refuses to create the top-level directory itself.

Dependencies/integration: abstraction over OS calls enables tests and portability.

Risks/test signals: it compares path strings by length/prefix shape rather than canonical path containment, so callers must pass normalized compatible paths. Tests cover direct subdir, nested subdir, already exists, top-level rejection, and unexpected mkdir errors.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/internal/dirutil/mksubdirall.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/internal/dirutil/mssubdirall_test.go -->
# sources/sync-backup/kopia/internal/dirutil/mssubdirall_test.go

Purpose: tests `MkSubdirAll` behavior with a small OS abstraction wrapper around real filesystem calls.

Important APIs/types/functions: `testOSI`, `TestMkSubdirAll`, `testutil.TempDirectory`, and `dirutil.ErrTopLevelDirectoryNotFound`.

Control flow: ordered cases check rejecting creation at or above top-level, creating one subdirectory, creating nested subdirectories, accepting existing directories, then injecting a generic mkdir error and requiring it to propagate.

State and persistence behavior: creates directories inside a temporary test directory; no state survives the test.

Dependencies/integration: uses real `os.Mkdir`, `os.IsExist`, `os.IsNotExist`, path separators, `filepath.Join`, and `testify/require`.

Risks/test signals: filename appears as `mssubdirall_test.go`, likely a typo relative to `mksubdirall.go`, but package tests still run. Tests do not cover trailing separators, relative path traversal, or symlink behavior.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/internal/dirutil/mssubdirall_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/internal/editor/editor.go -->
# sources/sync-backup/kopia/internal/editor/editor.go

Purpose: encapsulates launching an external editor and repeatedly parsing edited content until accepted or aborted.

Important APIs/types/functions: `EditLoop`, package variable `EditFile`, `readAndStripComments`, `getEditorCommand`, and `parseEditor`.

Control flow: `EditLoop` creates a temp directory/file with initial content, invokes `EditFile`, reads content with optional comment stripping, calls caller parse function, and on parse error prompts whether to reopen. `EditFile` resolves editor command from `VISUAL`, `EDITOR`, Windows notepad, or `vi`, then runs it attached to stdio.

State and persistence behavior: temporary edit file is removed by deferred `os.RemoveAll`. No durable state unless the editor itself has side effects.

Dependencies/integration: used by CLI flows needing user-edited JSON/text. Integrates `os/exec`, stdin/stdout/stderr, and Kopia logging.

Risks/test signals: interactive prompt uses `fmt.Scanf`, making automation difficult. `parseEditor` handles simple quoted paths and space splitting but not shell-like escaping. No test file is listed for this item.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/internal/editor/editor.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/internal/epoch/epoch_advance.go -->
# sources/sync-backup/kopia/internal/epoch/epoch_advance.go

Purpose: decides whether the current repository epoch should advance based on age, blob count, and total blob size.

Important APIs/types/functions: private `shouldAdvance`.

Control flow: returns false for no blobs, scans metadata to find min timestamp, max timestamp, and total length, rejects if elapsed time is below `minEpochDuration`, then returns true if blob count meets/exceeds the count threshold or total size meets/exceeds the size threshold.

State and persistence behavior: stateless computation over blob metadata. Epoch marker writing is handled by `Manager.MaybeAdvanceWriteEpoch`.

Dependencies/integration: used by epoch manager maintenance logic with `Parameters` thresholds.

Risks/test signals: threshold comparisons are inclusive for count and size, but time duration must be at least the minimum. Tests cover empty, insufficient age, size threshold, count threshold, and non-advancing cases.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/internal/epoch/epoch_advance.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/internal/epoch/epoch_advance_test.go -->
# sources/sync-backup/kopia/internal/epoch/epoch_advance_test.go

Purpose: table-driven verification of `shouldAdvance` epoch advancement criteria.

Important APIs/types/functions: `TestShouldAdvanceEpoch`, `DefaultParameters`, and `blob.Metadata` test cases.

Control flow: constructs metadata at fixed timestamps and lengths, including a generated slice large enough to meet the count threshold, then calls `shouldAdvance` with default thresholds and compares expected booleans.

State and persistence behavior: in-memory only.

Dependencies/integration: uses `time`, `blob`, and `testify/require`.

Risks/test signals: captures boundary behavior for duration and thresholds. It does not test negative/zero thresholds or unordered timestamps beyond a few cases.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/internal/epoch/epoch_advance_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/internal/epoch/epoch_manager.go -->
# sources/sync-backup/kopia/internal/epoch/epoch_manager.go

Purpose: manages Kopia repository index epochs, including current write epoch discovery, index writes, compaction selection, range checkpoints, deletion watermarks, and cleanup of superseded markers/indexes.

Important APIs/types/functions: `Parameters`, `DefaultParameters`, `CurrentSnapshot`, `Manager`, `NewManager`, `Current`, `Refresh`, `WriteIndex`, `GetCompleteIndexSet`, `MaybeAdvanceWriteEpoch`, `MaybeCompactSingleEpoch`, `MaybeGenerateRangeCheckpoint`, `CleanupMarkers`, `CleanupSupersededIndexes`, `AdvanceDeletionWatermark`, and blob prefix helpers.

Control flow: refresh loads epoch markers, deletion watermarks, single-epoch compactions, and range checkpoints concurrently, then loads nearby uncompacted epochs and sets `ValidUntil`. Writes choose the current uncompacted prefix and retry/cleanup if the snapshot expires or the epoch changes mid-write. Complete index set assembly starts from longest range checkpoints and fills remaining epochs from single compactions or uncompacted blobs. Maintenance compacts settled epochs, generates range checkpoints when enough settled epochs accumulate, advances epoch markers, and deletes superseded data only after safety margins.

State and persistence behavior: persistent protocol is encoded in blob names under prefixes `xe`, `xn`, `xs`, `xr`, and `xw`. In-memory state is `lastKnownState` guarded by mutex plus slow-operation counters and background wait group.

Dependencies/integration: uses blob storage/list/delete, `completeset`, `contentlog`, `maintenancestats`, `errgroup`, fake/injected time, and compactor callbacks.

Risks/test signals: correctness depends on storage clocks, complete-set naming, snapshot validity windows, and cleanup safety margins. Tests stress sequential/parallel writes, slow refresh/write retries, read-only refresh, compaction failures, range checkpointing, watermark behavior, parameter validation, and cleanup.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/internal/epoch/epoch_manager.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/internal/epoch/epoch_manager_test.go -->
# sources/sync-backup/kopia/internal/epoch/epoch_manager_test.go

Purpose: comprehensive behavioral tests for the epoch manager under normal operation, concurrency, failures, cleanup, compaction, range checkpoint generation, parameter validation, and slow-operation retries.

Important APIs/types/functions: `epochManagerTestEnv`, fake index helpers, `verifySequentialWrites`, `TestIndexEpochManager_Regular`, `Parallel`, rogue/compaction/deletion/read-only tests, slow write/refresh tests, maintenance tests, cleanup marker tests, and `forceAdvanceEpoch`.

Control flow: tests use map-backed/faulty storage with fake time, write fake JSON index shards, advance time, call refresh/maintenance methods, merge returned complete index sets, inject list/put/delete faults, and assert stats, epochs, watermarks, and retained data.

State and persistence behavior: the shared `DataMap` simulates repository blob persistence across manager instances. Tests observe blob prefixes directly and through manager snapshots.

Dependencies/integration: uses `blobtesting`, `faketime`, `fault`, `readonly`, `logging` wrappers, `errgroup`, `maintenancestats`, and `gather`.

Risks/test signals: strong coverage for protocol races, including allowed `ErrBlobNotFound` during concurrent cleanup. Some tests are nondeterministic/long and skipped under coverage or short mode. Randomness means rare failures can expose real race assumptions.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/internal/epoch/epoch_manager_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/internal/epoch/epoch_range.go -->
# sources/sync-backup/kopia/internal/epoch/epoch_range.go

Purpose: represents range checkpoint metadata and selects the best contiguous checkpoint chain starting at epoch 0.

Important APIs/types/functions: `RangeMetadata`, `findLongestRangeCheckpoint`, and recursive memoized `findLongestRangeCheckpointStartingAt`.

Control flow: groups range metadata by `MinEpoch`, then recursively tries checkpoints starting at the requested epoch, chaining to `MaxEpoch+1`. It chooses the chain whose final max epoch is greatest; ties prefer fewer checkpoint segments.

State and persistence behavior: no persistence here. `RangeMetadata.Blobs` references blob metadata for compacted checkpoint sets loaded by the manager.

Dependencies/integration: used during manager refresh after complete range compaction sets are discovered.

Risks/test signals: assumes valid non-overlapping semantics are enforced by selection rather than input validation. Empty input returns nil. Tests cover gaps, overlapping ranges, duplicate starts, and tie-breaking toward shorter chains.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/internal/epoch/epoch_range.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/internal/epoch/epoch_range_test.go -->
# sources/sync-backup/kopia/internal/epoch/epoch_range_test.go

Purpose: validates longest contiguous range checkpoint selection and tie-breaking.

Important APIs/types/functions: `TestLongestRangeCheckpoint` and `newEpochRangeMetadataForTesting`.

Control flow: constructs reusable range metadata for ranges such as 0-9, 0-29, 10-59, etc., passes different combinations to `findLongestRangeCheckpoint`, and compares exact pointer slices.

State and persistence behavior: in-memory only; `Blobs` are irrelevant for these tests.

Dependencies/integration: uses `testify/require`.

Risks/test signals: good coverage for chain continuity and shorter-chain tie preference. It does not cover invalid ranges where `MinEpoch > MaxEpoch` or negative epochs.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/internal/epoch/epoch_range_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/internal/epoch/epoch_utils.go -->
# sources/sync-backup/kopia/internal/epoch/epoch_utils.go

Purpose: provides parsing, grouping, compacted-range, and oldest-uncompacted-epoch helpers for epoch manager state.

Important APIs/types/functions: `epochNumberFromBlobID`, `epochRangeFromBlobID`, `groupByEpochNumber`, `groupByEpochRanges`, `deletionWatermarkFromBlobID`, `closedIntRange`, `getRangeCompactedRange`, `oldestUncompactedEpoch`, `filterLowerThan`, and `getOldestUncompactedAfterEpoch`.

Control flow: blob ID parsers strip prefix text before first digit and parse epoch numbers separated by underscores. Grouping functions collect metadata by parsed single epoch or range. `oldestUncompactedEpoch` starts after the longest range checkpoint, verifies range compaction begins at epoch 0, then skips contiguous single-epoch compactions using sorted filtered keys.

State and persistence behavior: stateless helpers over `CurrentSnapshot` and blob metadata. They interpret persistent state encoded in blob IDs and watermark names.

Dependencies/integration: used by refresh, cleanup, and compaction selection logic.

Risks/test signals: parsers are permissive about prefixes and can ignore malformed IDs silently. Invalid range compaction not starting at epoch 0 returns `errInvalidCompactedRange`. Direct tests are represented through manager and range tests; parser-specific edge coverage is limited.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/internal/epoch/epoch_utils.go -->
