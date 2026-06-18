# subset-b-009201 grouped research

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/syncthing/lib/scanner/walk_test.go -->
# sources/sync-backup/syncthing/lib/scanner/walk_test.go

Purpose: exercises scanner walking, hashing, ignore handling, Unicode normalization, ownership capture, cancellation, and block verification. It builds fake and basic filesystems, drives `Walk`, `Blocks`, `HashFile`, and helpers such as `walkDir`, and compares returned `protocol.FileInfo` values against expected file lists.

Important APIs and control flow: `newTestFs` constructs a representative tree with `.stignore` includes. `TestWalk` and `TestWalkSub` validate full and subdirectory scans with inherited ignore rules. `TestVerify` checks block hash verification against exact, extended, truncated, and mutated readers. Normalization tests run twice to model rename-on-scan behavior and Darwin CaseFS behavior. Cancellation is stressed with `infiniteFS` and multiple hashers. Other tests cover symlinks, block-size hysteresis from `CurrentFiler`, receive-only local flags, POSIX/Windows ownership metadata, non-existing sub paths, ignored-directory skipping, and include patterns requiring recursion into otherwise ignored trees.

State and persistence: all state is test-local fake/basic filesystem content, fake current-file maps, and event logger lifetimes. No durable persistence is created beyond temp directories.

Dependencies and integration: depends on `lib/fs`, `lib/ignore`, `lib/protocol`, `lib/events`, `lib/rand`, Unicode normalization, and scanner package internals. It is a high-signal integration test for scanner behavior as consumed by model indexing.

Risks: timing-sensitive cancellation and platform-specific normalization/ownership tests can be flaky if filesystem abstractions change. Some helper assumptions support only simple one-block expected data. Test signals are broad and target historical issues 1507, 4799, 4841, 5385, and 6487.
<!-- END_FILE_RESEARCH: sources/sync-backup/syncthing/lib/scanner/walk_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/syncthing/lib/semaphore/semaphore.go -->
# sources/sync-backup/syncthing/lib/semaphore/semaphore.go

Purpose: implements a byte-counting semaphore with adjustable capacity and a `MultiSemaphore` composition helper.

Important APIs and control flow: `New` clamps negative capacity to zero and initializes `available == max`. `Take` and `TakeWithContext` acquire up to `max` bytes; oversized takes are clamped. `TakeWithContext` runs the blocking acquisition in a goroutine, broadcasts on cancellation, then waits for the inner path to observe the context. `Give` clamps returned size and caps availability at `max`. `SetCapacity` changes `max`, shifts `available` by the capacity diff, clamps into `[0,max]`, and broadcasts. `Available` returns a locked snapshot. `MultiSemaphore` takes semaphores in slice order and gives them back in reverse order, skipping nil entries.

State and persistence: all state is in-memory `max`, `available`, mutex, and condition variable. No persistence.

Dependencies and integration: used wherever Syncthing needs shared throughput or resource limits. `context` support allows cancellation-friendly startup/shutdown paths.

Risks: `MultiSemaphore.TakeWithContext` does not roll back earlier acquisitions if a later semaphore returns context error, so callers must use it where cancellation semantics tolerate that or arrange cleanup. `TakeWithContext` spawns a goroutine per call. Test coverage focuses on capacity mutation and clamping.
<!-- END_FILE_RESEARCH: sources/sync-backup/syncthing/lib/semaphore/semaphore.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/syncthing/lib/semaphore/semaphore_test.go -->
# sources/sync-backup/syncthing/lib/semaphore/semaphore_test.go

Purpose: validates edge cases in the adjustable semaphore implementation.

Important tests: `TestZeroByteSemaphore` asserts zero-capacity semaphores are no-ops for large takes/gives. `TestByteSemaphoreCapChangeUp` proves a blocked waiter unblocks when capacity grows. `TestByteSemaphoreCapChangeDown1` and `TestByteSemaphoreCapChangeDown2` cover shrinking capacity while bytes are checked out, including the case where available becomes zero. `TestByteSemaphoreGiveMore` confirms oversized takes/gives are clamped and capacity increases only add the diff to available.

State and persistence: tests inspect the package-private `available` field directly. No persistence.

Dependencies and integration: tests only use `testing`; they are white-box tests in package `semaphore`.

Risks and signals: coverage is strong for arithmetic invariants but does not cover context cancellation, goroutine behavior, or `MultiSemaphore` rollback/order semantics.
<!-- END_FILE_RESEARCH: sources/sync-backup/syncthing/lib/semaphore/semaphore_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/syncthing/lib/signature/signature.go -->
# sources/sync-backup/syncthing/lib/signature/signature.go

Purpose: provides PEM-based ECDSA key generation, signing, and verification for release signatures and tooling.

Important APIs and control flow: `GenerateKeys` creates an ECDSA P-521 key using Syncthing's random reader, marshals the private key with `x509.MarshalECPrivateKey`, and marshals the public key as PKIX. `Sign` loads a private key, hashes all reader data, signs the hash, ASN.1-marshals `R` and `S`, and wraps the result in a `SIGNATURE` PEM block. `Verify` loads a public key, decodes and unmarshals the PEM signature, rehashes the reader, and calls `ecdsa.Verify`. `hashReader` SHA-256 hashes reader content but returns the hex-encoded digest bytes rather than raw hash bytes; sign and verify match because both use the same representation.

State and persistence: no internal persistent state. Inputs and outputs are PEM byte slices and reader streams.

Dependencies and integration: used by upgrade verification; depends on crypto/x509, ASN.1, PEM, SHA-256, and `lib/rand`.

Risks: `loadPrivateKey` does not nil-check `pem.Decode`, so malformed private PEM can panic. The hex-encoded hash convention is nonstandard and must remain consistent with existing signatures. Tests cover happy path and wrong data, not malformed PEM.
<!-- END_FILE_RESEARCH: sources/sync-backup/syncthing/lib/signature/signature.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/syncthing/lib/signature/signature_test.go -->
# sources/sync-backup/syncthing/lib/signature/signature_test.go

Purpose: verifies key generation, signing, and signature verification against embedded fixture material.

Important tests: `TestGenerateKeys` checks generated PEM blocks contain private and public key labels. `TestSign` signs a known string with an embedded private key and verifies the returned PEM is labeled `SIGNATURE`. `TestVerify` verifies a precomputed signature for the expected string and confirms changed data is rejected.

State and persistence: uses static PEM private/public keys and signature bytes in memory only.

Dependencies and integration: exercises the public `signature` package from an external test package, matching real caller usage.

Risks and signals: good regression coverage for the public API and fixture compatibility, but no tests for invalid private keys, invalid public keys, malformed signatures, reader errors, or alternate curves.
<!-- END_FILE_RESEARCH: sources/sync-backup/syncthing/lib/signature/signature_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/syncthing/lib/sliceutil/sliceutil.go -->
# sources/sync-backup/syncthing/lib/sliceutil/sliceutil.go

Purpose: generic slice helpers for order-preserving removal and mapping.

Important APIs and control flow: `RemoveAndZero` shifts elements left from index `i+1`, writes the zero value into the old tail slot, and returns the slice shortened by one. This avoids retaining removed references in the backing array. `Map` allocates a result slice with the same length and applies a conversion function element by element.

State and persistence: pure in-memory helpers; `RemoveAndZero` mutates the input backing array.

Dependencies and integration: no external dependencies. Generic constraints preserve named slice types for removal while `Map` returns a plain `[]R`.

Risks: no bounds checks beyond Go's natural panics. Callers must understand that the original slice backing array is modified. Tests cover integer removal but not reference retention, named slice types, or `Map`.
<!-- END_FILE_RESEARCH: sources/sync-backup/syncthing/lib/sliceutil/sliceutil.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/syncthing/lib/sliceutil/sliceutil_test.go -->
# sources/sync-backup/syncthing/lib/sliceutil/sliceutil_test.go

Purpose: covers the main invariant of `RemoveAndZero`.

Important tests: `TestRemoveAndZero` removes index 2 from `[1,2,3,4,5]`, expects the returned slice `[1,2,4,5]`, and scans the original backing array to ensure the removed value no longer remains.

State and persistence: in-memory only.

Dependencies and integration: uses Go `slices.Equal` and imports `sliceutil` as an external package, so it validates exported behavior.

Risks and signals: narrow but useful for order and zeroing. No coverage for pointer/reference element types, index panics, length-one slices, or `Map`.
<!-- END_FILE_RESEARCH: sources/sync-backup/syncthing/lib/sliceutil/sliceutil_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/syncthing/lib/stats/device.go -->
# sources/sync-backup/syncthing/lib/stats/device.go

Purpose: stores and retrieves per-device runtime statistics backed by Syncthing's typed key-value database.

Important APIs and control flow: `DeviceStatistics` is the JSON-facing shape with `LastSeen` and `LastConnectionDurationS`. `DeviceStatisticsReference` wraps `*db.Typed`. `GetLastSeen` reads the `lastSeen` key and defaults missing data to Unix epoch rather than zero time. `GetLastConnectionDuration` reads `lastConnDuration` as nanoseconds and defaults missing data to zero. `WasSeen` writes current time truncated to seconds. `LastConnectionDuration` stores `time.Duration.Nanoseconds`. `GetStatistics` composes both fields.

State and persistence: persists typed keys `lastSeen` and `lastConnDuration` in the supplied database namespace.

Dependencies and integration: used by model/device statistics surfaces and API JSON output. Depends on `internal/db`.

Risks: database errors propagate, but partial updates are possible because operations are separate. Time truncation intentionally drops subsecond precision. Test coverage confirms basic write/read behavior.
<!-- END_FILE_RESEARCH: sources/sync-backup/syncthing/lib/stats/device.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/syncthing/lib/stats/folder.go -->
# sources/sync-backup/syncthing/lib/stats/folder.go

Purpose: stores and retrieves per-folder last-file and scan-completion statistics in typed KV storage.

Important APIs and control flow: `FolderStatistics` exposes `LastFile` and `LastScan`. `LastFile` records timestamp, filename, and whether the received file was deleted. `GetLastFile` reads `lastFileAt`, `lastFileName`, and `lastFileDeleted`; missing timestamp or filename returns an empty `LastFile`. `ReceivedFile` writes those three keys sequentially with current time truncated to seconds. `ScanCompleted` writes `lastScan`. `GetLastScanTime` defaults to zero time when missing. `GetStatistics` combines both getters.

State and persistence: persists `lastFileAt`, `lastFileName`, `lastFileDeleted`, and `lastScan` in `db.Typed`.

Dependencies and integration: used by folder statistics APIs and model reporting.

Risks: `ReceivedFile` is not transactional; write failures can leave mixed old/new metadata. Missing boolean is treated as false. Tests in this batch do not directly cover folder stats.
<!-- END_FILE_RESEARCH: sources/sync-backup/syncthing/lib/stats/folder.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/syncthing/lib/stats/stats_test.go -->
# sources/sync-backup/syncthing/lib/stats/stats_test.go

Purpose: provides basic coverage for device statistics persistence.

Important tests: `TestDeviceStat` opens a temporary SQLite DB, wraps a typed namespace, writes `WasSeen` and a 42-second connection duration, reads `GetStatistics`, and asserts `LastSeen` is recent and duration seconds equals 42.

State and persistence: uses a real temporary SQLite database and closes it in cleanup.

Dependencies and integration: exercises `internal/db/sqlite` and `db.Typed`, so it catches serialization/storage regressions in addition to stats code.

Risks and signals: useful smoke test for device stats. It does not cover default values, database error paths, folder stats, or partial write scenarios.
<!-- END_FILE_RESEARCH: sources/sync-backup/syncthing/lib/stats/stats_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/syncthing/lib/stringutil/stringutil.go -->
# sources/sync-backup/syncthing/lib/stringutil/stringutil.go

Purpose: small string/time formatting utilities.

Important APIs and control flow: `UniqueTrimmedStrings` trims ASCII space characters from both ends of each string, preserves first-seen order, and removes duplicates using a map. It returns nil for nil input because the result slice starts nil and no append occurs. `NiceDurationString` rounds durations to coarser units as magnitude grows: hours above a day, minutes above an hour, seconds above a minute, milliseconds above a second, and microseconds above a millisecond.

State and persistence: pure functions, no state.

Dependencies and integration: uses `strings` and `time`; likely feeds configuration/display normalization.

Risks: trimming uses `strings.Trim(v, " ")`, not Unicode whitespace. `NiceDurationString` uses strict greater-than thresholds, so exact boundary values are not rounded at the next unit. Tests cover uniqueness/trimming only.
<!-- END_FILE_RESEARCH: sources/sync-backup/syncthing/lib/stringutil/stringutil.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/syncthing/lib/stringutil/stringutil_test.go -->
# sources/sync-backup/syncthing/lib/stringutil/stringutil_test.go

Purpose: validates order-preserving uniqueness after space trimming.

Important tests: `TestUniqueStrings` covers distinct values, duplicate values, repeated duplicates, nil input, and strings padded with ASCII spaces. It checks both length and positional equality.

State and persistence: no state.

Dependencies and integration: white-box package test with only `testing`.

Risks and signals: covers `UniqueTrimmedStrings` behavior but not `NiceDurationString`, Unicode whitespace, empty strings, or mixed tabs/newlines.
<!-- END_FILE_RESEARCH: sources/sync-backup/syncthing/lib/stringutil/stringutil_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/syncthing/lib/structutil/structutil.go -->
# sources/sync-backup/syncthing/lib/structutil/structutil.go

Purpose: reflection helpers for applying defaults and filling nil composite fields in configuration/report structs.

Important APIs and control flow: `SetDefaults` walks a struct pointer, reads `default` tags, first offers the value or address to a `ParseDefault(string) error` implementation, then supports strings, integer types, floats, booleans, and intentionally defers `[]string` defaults. Untagged nested structs are recursed into. `FillNil` and `FillNilExceptDeprecated` allocate nil pointer chains, empty maps/slices/channels, and recurse through structs and slices of structs; deprecated fields can be skipped by name prefix. `FillNilSlices` applies comma-separated `default` tags to nil `[]string` fields only.

State and persistence: mutates caller-provided structs in memory.

Dependencies and integration: used by usage-report contract construction and configuration defaulting. Depends on `reflect`, `strconv`, and `strings`.

Risks: unsupported types and parse failures panic in `SetDefaults`. The helpers require pointers to settable structs. Reflection over unexported fields can panic when `Interface` is called if a tagged field is not interfaceable. Tests cover common defaults and nil filling.
<!-- END_FILE_RESEARCH: sources/sync-backup/syncthing/lib/structutil/structutil.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/syncthing/lib/structutil/structutil_test.go -->
# sources/sync-backup/syncthing/lib/structutil/structutil_test.go

Purpose: validates default tag parsing and nil-composite filling.

Important tests: `TestSetDefaults` checks string, int, float, bool, and custom `Defaulter.ParseDefault`. `TestFillNillSlices` confirms nil `[]string` gets comma-split defaults while already-provided or empty non-nil slices are preserved. `TestFillNil` confirms maps, slices, channels, pointer chains, and nested structs are allocated. `TestFillNilDoesNotBulldozeSetFields` confirms existing slices/maps/channels and pointer targets are not replaced.

State and persistence: in-memory reflection mutations only.

Dependencies and integration: package-level tests access helper behavior directly.

Risks and signals: strong coverage for intended config/report shapes. No tests for deprecated skipping, unsupported-type panics, parse errors, or slices of structs recursion.
<!-- END_FILE_RESEARCH: sources/sync-backup/syncthing/lib/structutil/structutil_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/syncthing/lib/stun/debug.go -->
# sources/sync-backup/syncthing/lib/stun/debug.go

Purpose: defines the package logger adapter for STUN functionality.

Important APIs and control flow: initializes package variable `l` with `slogutil.NewAdapter("STUN functionality")`. Other STUN code uses this adapter for debug logging.

State and persistence: package-level logger only; no persistence.

Dependencies and integration: integrates with Syncthing's structured logging utility and package debug controls.

Risks and test signals: no behavior beyond logger registration. Correctness depends on consistent package-level logger naming for diagnostics.
<!-- END_FILE_RESEARCH: sources/sync-backup/syncthing/lib/stun/debug.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/syncthing/lib/stun/stun.go -->
# sources/sync-backup/syncthing/lib/stun/stun.go

Purpose: runs STUN discovery/keepalive to classify NAT type and publish external UDP address changes.

Important APIs and control flow: `New` wraps a supplied `net.PacketConn` in a go-stun client and records a service name from the local address. `Serve` loops until context cancellation, respecting dynamic config disablement, iterating configured STUN servers, and sleeping for `stunRetryInterval` after failures or non-punchable NAT. `runStunForServer` resolves the server, runs `client.Discover` through `svcutil.CallWithContext`, filters unusable NAT results, notifies NAT type, and starts keepalive only for punchable NAT types. `stunKeepAlive` adapts keepalive sleep based on observed external port changes and aborts below the configured minimum. Subscriber callbacks are only fired on changes.

State and persistence: stores current NAT type and external host in memory. No durable state.

Dependencies and integration: depends on `github.com/ccding/go-stun/stun`, config options, and subscriber methods likely implemented by connection services/discovery.

Risks: no mutex protects `natType`/`addr`; service appears single-threaded except callbacks. `CallWithContext` cannot stop an underlying blocked STUN call, only returns early. Adaptive keepalive may be sensitive to config extremes. No local tests in this subset.
<!-- END_FILE_RESEARCH: sources/sync-backup/syncthing/lib/stun/stun.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/syncthing/lib/svcutil/svcutil.go -->
# sources/sync-backup/syncthing/lib/svcutil/svcutil.go

Purpose: utilities for Suture-managed services, fatal/no-restart error tagging, exit status values, event logging specs, and context-wrapped calls.

Important APIs and control flow: `FatalErr` wraps an error with an `ExitStatus` and reports `Is(suture.ErrTerminateSupervisorTree)`. `NoRestartErr` wraps errors so `errors.Is(..., suture.ErrDoNotRestart)` succeeds. `AsService` wraps a function as `ServiceWithError`, storing the most recent error behind a mutex and converting context-like errors to plain errors unless the service context is actually canceled. `OnSupervisorDone` adds a service that runs a callback after supervisor context completion. `SpecWithDebugLogger` and `SpecWithInfoLogger` configure Suture specs. `infoEventHook` suppresses repeated identical termination logs. `CallWithContext` runs a blocking function in a goroutine and returns context error if canceled first.

State and persistence: in-memory service error state and closure-local previous termination event.

Dependencies and integration: central to `syncthing.App`, STUN calls, failure reporting, and other supervised services.

Risks: `CallWithContext` leaks the goroutine until the function returns. Error identity conversion is deliberate but can hide timeout semantics from Suture. No tests in this subset.
<!-- END_FILE_RESEARCH: sources/sync-backup/syncthing/lib/svcutil/svcutil.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/syncthing/lib/syncthing/auditservice.go -->
# sources/sync-backup/syncthing/lib/syncthing/auditservice.go

Purpose: supervised service that writes all Syncthing events as JSON lines to an audit writer.

Important APIs and control flow: `newAuditService` stores an `io.Writer` and event logger. `Serve` subscribes to `events.AllEvents`, defers unsubscribe, creates a JSON encoder, and loops over subscription events or context cancellation. Each event received is encoded to the writer. If the subscription channel closes unexpectedly, it waits for context cancellation and returns that error. `String` returns a pointer-qualified service name.

State and persistence: state is the active event subscription and destination writer. Persistence depends on the writer supplied by the app.

Dependencies and integration: added during app startup when `Options.AuditWriter` is non-nil. Uses event logger subscription API and Suture service semantics.

Risks: `enc.Encode` errors are ignored, so failed audit writes do not stop the service. It logs only events after subscription starts. Test coverage checks event timing and stop behavior.
<!-- END_FILE_RESEARCH: sources/sync-backup/syncthing/lib/syncthing/auditservice.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/syncthing/lib/syncthing/auditservice_test.go -->
# sources/sync-backup/syncthing/lib/syncthing/auditservice_test.go

Purpose: verifies audit service subscription timing and shutdown behavior.

Important tests: `TestAuditService` starts an event logger, emits one event before creating the audit service, starts the service with a buffer writer, emits a second event, cancels the audit service, then emits a third event. It asserts the buffer excludes the first and third events and includes the second.

State and persistence: uses an in-memory `bytes.Buffer` and event logger goroutine.

Dependencies and integration: exercises `events.Logger` subscription delivery and audit service `Serve`.

Risks and signals: validates lifecycle behavior but uses sleeps to allow subscription and delivery, making it somewhat timing-sensitive. It does not check JSON validity or writer error handling.
<!-- END_FILE_RESEARCH: sources/sync-backup/syncthing/lib/syncthing/auditservice_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/syncthing/lib/syncthing/debug.go -->
# sources/sync-backup/syncthing/lib/syncthing/debug.go

Purpose: package-level logging setup and debug-level check for the main run facility.

Important APIs and control flow: initializes `l` with `slogutil.NewAdapter("Main run facility")`. `shouldDebug` asks the default slog logger whether debug is enabled for a background context; `App.stopWithErr` uses it before printing the service tree.

State and persistence: logger adapter only.

Dependencies and integration: integrates with Syncthing logging and app shutdown diagnostics.

Risks and signals: no tests needed for simple logger wiring. Behavior depends on current global logger configuration.
<!-- END_FILE_RESEARCH: sources/sync-backup/syncthing/lib/syncthing/debug.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/syncthing/lib/syncthing/globalmigrations.go -->
# sources/sync-backup/syncthing/lib/syncthing/globalmigrations.go

Purpose: tracks global database migration version for app startup.

Important APIs and control flow: constants define `globalMigrationVersion = 1` and DB key `globalMigrationVersion`. `globalMigration` reads the previous version from misc DB, returns if already current, has no active migration steps, and writes version 1.

State and persistence: persists one misc DB int64 key. It is called during app startup after version bookkeeping and before model construction.

Dependencies and integration: depends on `internal/db` and `lib/config`. The config parameter is currently unused but leaves room for migration logic that needs configuration context.

Risks and signals: future migrations must preserve idempotence and error propagation. No dedicated tests in this subset.
<!-- END_FILE_RESEARCH: sources/sync-backup/syncthing/lib/syncthing/globalmigrations.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/syncthing/lib/syncthing/internals.go -->
# sources/sync-backup/syncthing/lib/syncthing/internals.go

Purpose: exposes a deliberately unstable but narrower API over `model.Model` for direct package consumers, including mobile apps.

Important APIs and control flow: `Internals` stores `model.Model`. Methods forward to model operations for folder state, ignores, block download, availability, global file info/tree, connectivity, scans, completion, device stats, pending folders, subdirectory scans, global/local/need sizes, all global files, progress bytes, need-file pagination, remote need files, and local changed files. `Counts` aliases `db.Counts`.

State and persistence: no state beyond the model reference. Persistence and locks are owned by the underlying model/database.

Dependencies and integration: created in `App.startup` after `model.NewModel`. Integrates `db`, `protocol`, `stats`, and `model` types into an importable boundary.

Risks: because it forwards directly, model behavior changes can affect external consumers despite the intended boundary. No validation is added here; errors propagate as-is. No tests in this subset.
<!-- END_FILE_RESEARCH: sources/sync-backup/syncthing/lib/syncthing/internals.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/syncthing/lib/syncthing/superuser_unix.go -->
# sources/sync-backup/syncthing/lib/syncthing/superuser_unix.go

Purpose: Unix implementation of privileged-user detection.

Important APIs and control flow: build tags exclude Windows. `isSuperUser` returns `os.Geteuid() == 0`.

State and persistence: no state.

Dependencies and integration: called during app startup to warn when Syncthing runs as root/system. Depends only on `os`.

Risks and signals: simple platform-specific behavior. It treats only effective UID zero as superuser and does not check capabilities or service managers. No tests in this subset.
<!-- END_FILE_RESEARCH: sources/sync-backup/syncthing/lib/syncthing/superuser_unix.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/syncthing/lib/syncthing/superuser_windows.go -->
# sources/sync-backup/syncthing/lib/syncthing/superuser_windows.go

Purpose: Windows implementation of privileged/system-user detection.

Important APIs and control flow: `isSuperUser` opens the current process token, gets the token user, converts its SID to string, and compares it with the LocalSystem RID `S-1-5-18`. Errors are logged at debug and return false.

State and persistence: no state.

Dependencies and integration: called by app startup warning path. Depends on `syscall` token APIs and logging.

Risks: detects LocalSystem specifically, not all administrator contexts. Fail-open-to-false avoids startup failures but can suppress warnings when token APIs fail. No tests in this subset.
<!-- END_FILE_RESEARCH: sources/sync-backup/syncthing/lib/syncthing/superuser_windows.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/syncthing/lib/syncthing/syncthing.go -->
# sources/sync-backup/syncthing/lib/syncthing/syncthing.go

Purpose: main embeddable Syncthing app wiring: startup, service supervision, GUI/API setup, shutdown, and lifecycle status.

Important APIs and control flow: `Options` controls audit, upgrades, profiling, delta index reset, and DB maintenance interval. `App` owns config, DB, events, TLS certificate, main Suture supervisor, internals, exit status, error, and shutdown channels. `New` constructs a stopped app. `Start` starts the supervisor background and runs `startup`; failures call `stopWithErr`. `startup` adds failure handling, DB service, optional audit, API event subscriptions, file limit lift, device ID, Starting event, short-ID conflict check, optional profiler and CPU bench, delta reset, dropped-folder DB cleanup, previous-version handling, global migration, model construction, TLS config, discovery/connection service wiring, usage reporting, GUI/API setup, loaded-config logging, superuser warning, StartupComplete event, and optional low-priority setting. `wait` handles supervisor exit, closes DB with timeout, and closes `stopped`.

State and persistence: persists previous build version in misc DB, may drop folder metadata/index IDs, runs global migrations, and config modifications can save via wrappers elsewhere. Shutdown state is guarded by `sync.Once`.

Dependencies and integration: central integration point for db, config, model, connections, discovery, events, API, TLS, upgrade, and usage reporting.

Risks: startup has many side effects; failures after services start must cleanly cancel and close DB. `InsecureSkipVerify` is intentionally used for device-certificate identity verification elsewhere. Tests cover short-ID conflicts and startup failure cleanup.
<!-- END_FILE_RESEARCH: sources/sync-backup/syncthing/lib/syncthing/syncthing.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/syncthing/lib/syncthing/syncthing_test.go -->
# sources/sync-backup/syncthing/lib/syncthing/syncthing_test.go

Purpose: tests selected app startup validation and failure cleanup.

Important tests: `TestShortIDCheck` builds configs with non-conflicting and conflicting first-64-bit device IDs and asserts `checkShortIDs` behavior. `TestStartupFail` creates an in-memory certificate, constructs a conflicting device ID with the same short ID, starts an app with temp SQLite DB, expects `Start` to fail, verifies `Wait` returns within one second with `ExitError`, checks `Error` matches the startup error, and confirms the DB was closed.

State and persistence: uses temp config files and temp SQLite DBs.

Dependencies and integration: exercises config wrapping, TLS certificate generation, protocol device IDs, app lifecycle, and DB close behavior.

Risks and signals: good coverage for a critical startup failure path. It does not cover successful startup, GUI setup, migrations, or service runtime errors.
<!-- END_FILE_RESEARCH: sources/sync-backup/syncthing/lib/syncthing/syncthing_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/syncthing/lib/syncthing/time_android.go -->
# sources/sync-backup/syncthing/lib/syncthing/time_android.go

Purpose: Android-specific timezone initialization workaround.

Important APIs and control flow: `init` runs `/system/bin/getprop persist.sys.timezone`, trims output, loads that location, and assigns `time.Local`. Any command or location error returns without changing local time.

State and persistence: mutates process-global `time.Local`; no file persistence.

Dependencies and integration: built only for Android. It addresses Go timezone behavior on Android.

Risks: shelling out during init can fail silently. It trusts system property content and affects all time formatting/parsing using `time.Local`, including versioner timestamp parsing. No tests in this subset.
<!-- END_FILE_RESEARCH: sources/sync-backup/syncthing/lib/syncthing/time_android.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/syncthing/lib/syncthing/utils.go -->
# sources/sync-backup/syncthing/lib/syncthing/utils.go

Purpose: startup utilities for directories, certificates, default/config loading, config archiving, database opening, and LevelDB-to-SQLite migration.

Important APIs and control flow: `EnsureDir` creates a basic filesystem root and corrects permissions best-effort. `LoadOrGenerateCertificate` falls back to `GenerateCertificate`, which uses `tlsutil.NewCertificate`. `DefaultConfig` builds config, optionally probes free ports, and wraps it. `LoadConfigAtStartup` creates a default config when missing, rejects truncated config, archives/saves when version changes, and can reject newer configs unless allowed. `OpenDatabase` opens SQLite with delete retention and metrics wrapping. `TryMigrateDatabase` detects legacy LevelDB, opens SQLite migration DB, skips already-migrated DBs, iterates folders and file snapshots, writes batches of 1000 local file infos while applying delete retention, migrates mtimes, records migration metadata, and renames the old DB directory.

State and persistence: writes certificate/key files, config files and archives, SQLite DB content, migration metadata, and renames legacy DB directory.

Dependencies and integration: called by command startup before constructing `App`; integrates locations, fs, config, events, db/sqlite, olddb, backend, protocol, TLS.

Risks: migration is long-running and partially logs progress; failures can leave partial SQLite content before retry. `archiveAndSaveConfig` copies then saves, so archive cleanup on copy write failure is explicit. No tests in this subset.
<!-- END_FILE_RESEARCH: sources/sync-backup/syncthing/lib/syncthing/utils.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/syncthing/lib/syncutil/timeoutcond.go -->
# sources/sync-backup/syncthing/lib/syncutil/timeoutcond.go

Purpose: condition-variable-like primitive that supports broadcast wakeups with waiter-specific timeouts.

Important APIs and control flow: `NewTimeoutCond` stores a caller-supplied locker. `Broadcast` must be called while locked; if a channel exists, it closes it and resets to nil, waking all current waiters. `SetupWait` creates a waiter with a `time.Timer`. `Wait` must be called while locked; it lazily creates the shared channel, unlocks around the select, then re-locks before returning true on broadcast or false on timer expiry. `Stop` stops the timer when the waiter is no longer needed.

State and persistence: in-memory locker, shared channel, and timers.

Dependencies and integration: useful where `sync.Cond` semantics need timeouts without per-wait goroutines.

Risks: callers must obey locking requirements. Timer channels are not drained in `Stop`, so reuse is not supported. Broadcasts before a waiter captures the channel are not remembered, matching cond semantics. Tests exercise timing and deadlock behavior.
<!-- END_FILE_RESEARCH: sources/sync-backup/syncthing/lib/syncutil/timeoutcond.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/syncthing/lib/syncutil/timeoutcond_test.go -->
# sources/sync-backup/syncthing/lib/syncutil/timeoutcond_test.go

Purpose: stress-tests `TimeoutCond` for basic wait, broadcast, timeout, and lock behavior.

Important tests: `TestTimeoutCond` starts a periodic broadcaster and multiple routines waiting with staggered durations, each using `runLocks` for many iterations. `runLocks` ensures failed waits do not return significantly before their timeout and logs late successes as likely scheduler delay. The file also defines `testClock`, a manual clock helper unused by this test.

State and persistence: in-memory mutex, goroutines, timers, and result counters.

Dependencies and integration: tests locking and channel behavior under scheduling pressure.

Risks and signals: the test comments acknowledge timing instability. It is useful for deadlock detection but intentionally weak on exact success/failure counts.
<!-- END_FILE_RESEARCH: sources/sync-backup/syncthing/lib/syncutil/timeoutcond_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/syncthing/lib/testutil/testutil.go -->
# sources/sync-backup/syncthing/lib/testutil/testutil.go

Purpose: small reusable test I/O helpers.

Important APIs and control flow: `ErrClosed` marks closed blocking readers/writers. `BlockingRW` has a `done` channel; `Read` and `Write` block until `Close` closes `done`, then return `ErrClosed`. `Close` closes `done` idempotently through channel close semantics only if called once. `NoopRW` implements `Read` as immediate EOF and `Write` as accepting all bytes. `NoopCloser` implements no-op `Close`.

State and persistence: in-memory channel state only.

Dependencies and integration: test packages can use these to simulate blocked connections or harmless read/write endpoints.

Risks: `BlockingRW.Close` will panic if called more than once because it closes an already-closed channel. It is a test helper, so callers must coordinate close ownership. No tests in this subset.
<!-- END_FILE_RESEARCH: sources/sync-backup/syncthing/lib/testutil/testutil.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/syncthing/lib/tlsutil/tlsutil.go -->
# sources/sync-backup/syncthing/lib/tlsutil/tlsutil.go

Purpose: central TLS configuration, certificate generation, and listener protocol-detection helpers.

Important APIs and control flow: `SecureDefaultTLS13` returns TLS 1.3-only config with a disabled-size client session cache. `SecureDefaultWithTLS12` returns TLS 1.2+ config with a copied curated cipher-suite list, server cipher preference, and HTTP/2/HTTP/1.1 protos. `generateCertificate` creates either browser-compatible ECDSA P-256 or sync-oriented Ed25519 self-signed certs, with CN/DNS name, Syncthing org fields, server/client auth, and day-truncated validity. `NewCertificate` writes PEM cert/key files and returns parsed key pair; `NewCertificateInMemory` avoids filesystem. `DowngradingListener.AcceptNoWrapTLS` accepts a connection, reads one byte with a one-second deadline, wraps it in `UnionedConnection`, and classifies TLS by first byte `0x16`; `Accept` TLS-wraps classified TLS connections. `pemBlockForKey` supports RSA, ECDSA, and Ed25519.

State and persistence: certificate file writes use 0600 for keys; listener state wraps underlying net connections.

Dependencies and integration: used by app device certs, GUI certs, upgrade HTTP clients, and mixed HTTP/HTTPS listeners.

Risks: first-byte TLS detection is heuristic. Read errors return the raw connection as identification failure. Cert file write failures after cert creation can leave partial files. Tests cover cipher list and unioned first-byte behavior.
<!-- END_FILE_RESEARCH: sources/sync-backup/syncthing/lib/tlsutil/tlsutil.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/syncthing/lib/tlsutil/tlsutil_test.go -->
# sources/sync-backup/syncthing/lib/tlsutil/tlsutil_test.go

Purpose: tests connection first-byte preservation/TLS detection and TLS 1.2 cipher-suite set.

Important tests: `TestUnionedConnection` feeds fake accepted connections with first byte `0x16` and non-`0x16` data, checks `AcceptNoWrapTLS` classification, and reads all bytes back to ensure the initial byte is not lost and the first read returns exactly one byte. `TestCheckCipherSuites` verifies `SecureDefaultWithTLS12` returns exactly the expected cipher IDs with no duplicates or unknown suites.

State and persistence: fake in-memory listener and connection only.

Dependencies and integration: validates exported listener/helper behavior without network sockets.

Risks and signals: no tests for `Accept` TLS wrapping, certificate generation/writing, read-deadline errors, or empty first reads.
<!-- END_FILE_RESEARCH: sources/sync-backup/syncthing/lib/tlsutil/tlsutil_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/syncthing/lib/upgrade/debug.go -->
# sources/sync-backup/syncthing/lib/upgrade/debug.go

Purpose: package logger adapter for upgrade functionality.

Important APIs and control flow: initializes `l` with `slogutil.NewAdapter("Upgrade")` for debug logging in release selection and archive processing.

State and persistence: logger only.

Dependencies and integration: integrates upgrade internals with Syncthing logging.

Risks and test signals: no runtime logic beyond logger setup.
<!-- END_FILE_RESEARCH: sources/sync-backup/syncthing/lib/upgrade/debug.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/syncthing/lib/upgrade/signingkey.go -->
# sources/sync-backup/syncthing/lib/upgrade/signingkey.go

Purpose: embeds the public signing key used to verify downloaded upgrade archives.

Important APIs and control flow: uses `go:embed signingkey.pem` to expose `SigningKey []byte`. Upgrade verification passes this key to `signature.Verify`.

State and persistence: key is embedded into the binary at build time.

Dependencies and integration: depends on Go embed and must match release signing infrastructure/stsigtool.

Risks: changing this key without synchronized release signing breaks all built-in upgrades. No tests in this subset directly verify the embedded key.
<!-- END_FILE_RESEARCH: sources/sync-backup/syncthing/lib/upgrade/signingkey.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/syncthing/lib/upgrade/upgrade_common.go -->
# sources/sync-backup/syncthing/lib/upgrade/upgrade_common.go

Purpose: common upgrade data structures, single-flight locking, version comparison, and release asset naming.

Important APIs and control flow: `Release`, `Asset`, and `ReleaseCompatibility` model release metadata. Errors describe no download, no selectable version, unsupported upgrade, and in-progress upgrade. `To` and `ToURL` acquire `upgradeUnlocked`, find current executable, call platform-specific upgrade functions, and only unlock on failure so a successful upgrade cannot be repeated in-process. `CompareVersions` parses release and prerelease parts, handles optional `v`/`V`, ignores build metadata, treats 0.x and 1.x major transition specially, compares prerelease numbers/strings semver-style, and returns a `Relation`. `releaseNames` restricts acceptable asset prefixes by OS/arch and tag, with macOS name aliases.

State and persistence: `upgradeUnlocked` is a process-wide channel semaphore. Upgrade functions rename binaries elsewhere.

Dependencies and integration: used by app/API upgrade flows and usage-report upgrade flags.

Risks: `versionParts` treats invalid numeric release fields as zero. Single-flight unlock semantics assume process restart after successful upgrade. Tests heavily cover comparison and selection.
<!-- END_FILE_RESEARCH: sources/sync-backup/syncthing/lib/upgrade/upgrade_common.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/syncthing/lib/upgrade/upgrade_supported.go -->
# sources/sync-backup/syncthing/lib/upgrade/upgrade_supported.go

Purpose: build-enabled implementation for fetching release metadata, selecting upgrades, downloading archives, verifying signatures, and replacing the binary.

Important APIs and control flow: built when not `noupgrade` and not iOS. `upgradeClient` uses Syncthing dialer, TLS 1.2+, proxy, HTTP/2, and long read timeout. `FetchLatestReleases` GETs JSON with metadata limit. `SelectLatestRelease` sorts releases, skips prereleases unless allowed, prefers same-major/minor path before a later major when appropriate, and requires an asset prefix from `releaseNames`. `upgradeToURL` downloads/extracts to temp, renames current binary to `.old`, and renames temp into place with rollback on final rename failure. `readTarGz` and `readZip` scan bounded archive members/sizes for `syncthing`/`syncthing.exe` and `release.sig`. `verifyUpgrade` verifies the signature over `archiveName + "\n" + binary contents` with embedded signing key. `writeBinary` writes temp executable with 0755.

State and persistence: network metadata/downloads, temp files in binary directory, current binary rename, `.old` backup, embedded key verification.

Dependencies and integration: release API, `signature`, `tlsutil`, `dialer`, gopsutil OS version header, tar/zip/gzip.

Risks: partial upgrades depend on filesystem rename semantics. Archive limits and shallow binary path checks mitigate malicious archives. Tests cover version selection, not full download/extract/signature paths.
<!-- END_FILE_RESEARCH: sources/sync-backup/syncthing/lib/upgrade/upgrade_supported.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/syncthing/lib/upgrade/upgrade_test.go -->
# sources/sync-backup/syncthing/lib/upgrade/upgrade_test.go

Purpose: regression tests for version comparison and release selection.

Important tests: `TestCompareVersions` covers equal, older/newer, major transitions, 0.x/1.x special handling, numeric prerelease ordering, string prerelease ordering, build metadata ignoring, and `v`/`V` prefixes. `TestErrorRelease` expects selection failure on nil releases. `TestSelectedRelease` constructs candidate releases with matching assets and checks prerelease filtering, newest minor selection, and major-upgrade deferral behavior. `TestSelectedReleaseMacOS` validates both `macos` and legacy `macosx` asset prefixes on Darwin.

State and persistence: no persistence.

Dependencies and integration: depends on runtime/build OS info for platform-specific asset names.

Risks and signals: strong for selection policy. It does not test HTTP fetching, archive extraction, signature verification, or binary replacement.
<!-- END_FILE_RESEARCH: sources/sync-backup/syncthing/lib/upgrade/upgrade_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/syncthing/lib/upgrade/upgrade_unsupp.go -->
# sources/sync-backup/syncthing/lib/upgrade/upgrade_unsupp.go

Purpose: unsupported build implementation for the upgrade package.

Important APIs and control flow: built for `noupgrade` or iOS. Sets `DisabledByCompilation = true`. `upgradeTo`, `upgradeToURL`, and `LatestRelease` all return `ErrUpgradeUnsupported`.

State and persistence: no state and no binary modifications.

Dependencies and integration: allows callers to compile against the same API while disabling upgrades. Usage reporting reads `DisabledByCompilation` to report upgrade capability.

Risks and signals: simple build-tag fallback. Tests with `!noupgrade` do not exercise this file.
<!-- END_FILE_RESEARCH: sources/sync-backup/syncthing/lib/upgrade/upgrade_unsupp.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/syncthing/lib/upnp/debug.go -->
# sources/sync-backup/syncthing/lib/upnp/debug.go

Purpose: package logger adapter for UPnP discovery and port mapping.

Important APIs and control flow: initializes `l` with `slogutil.NewAdapter("UPnP discovery and port mapping")`.

State and persistence: logger only.

Dependencies and integration: used by UPnP discovery, SOAP, and IGD service debug logs.

Risks and test signals: no behavior beyond diagnostics.
<!-- END_FILE_RESEARCH: sources/sync-backup/syncthing/lib/upnp/debug.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/syncthing/lib/upnp/igd_service.go -->
# sources/sync-backup/syncthing/lib/upnp/igd_service.go

Purpose: represents a discovered UPnP IGD control service and implements NAT device operations for IPv4 port mapping and IPv6 pinholes.

Important APIs and control flow: `IGDService` records UUID, device, service ID, control URL, URN, local IPv4, and network interface. `AddPinhole` enumerates interface addresses, handles explicit listener IPs, skips IPv4/private/non-GUA addresses, and attempts WANIPv6FirewallControl pinholes for global IPv6 addresses. `tryAddPinholeForIP6` maps TCP/UDP to protocol numbers, sends SOAP with the internal IPv6 as local source, parses UPnP faults or logs returned unique ID. `AddPortMapping` requires `LocalIPv4`, sends SOAP `AddPortMapping`, and retries with permanent lease on UPnP error 725. `DeletePortMapping` sends SOAP delete. `GetExternalIPv4Address` parses SOAP response. `SupportsIPVersion` distinguishes IPv6 firewall service from IPv4 services. `ID` builds a unique diagnostic identifier.

State and persistence: no persisted state; remote router state changes via SOAP leases/pinholes.

Dependencies and integration: implements `nat.Device` expectations; depends on `netutil`, `nat`, SOAP helpers in `upnp.go`.

Risks: router SOAP behavior varies; partial IPv6 pinhole success is accepted. XML body fields interpolate description/IP data without escaping. Tests cover SOAP parsing indirectly in `upnp_test.go`.
<!-- END_FILE_RESEARCH: sources/sync-backup/syncthing/lib/upnp/igd_service.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/syncthing/lib/upnp/upnp.go -->
# sources/sync-backup/syncthing/lib/upnp/upnp.go

Purpose: UPnP InternetGatewayDevice discovery, device-description parsing, service extraction, local address selection, and SOAP transport.

Important APIs and control flow: `init` registers `Discover` with NAT discovery. `Discover` enumerates running multicast interfaces, runs IPv6 IGDv2 discovery only when a global IPv6 address exists, then IPv4 IGDv2 and IGDv1 discovery, deduplicating results by ID. `discover` sends SSDP M-SEARCH over multicast, reads responses until timeout/context cancellation, and sends parsed IGD services to a result channel. `parseResponse` reads HTTP-like SSDP responses, validates ST, Location, and USN, fixes IPv6 link-local location hosts with zone-aware source addresses, downloads XML device descriptions, determines local IPv4 via interface or fallback UDP dial, marks IPv6 root devices, and extracts services. `getServiceDescriptions` selects IGDv1/v2 and IPv4/IPv6 service URNs. `replaceRawPath` normalizes relative/absolute control URLs. `soapRequestWithIP` builds SOAP HTTP POSTs with optional local bind address and returns response bytes even on HTTP errors. `interfaceHasGUAIPv6` screens IPv6 discovery.

State and persistence: discovery is in-memory; router state changes occur through IGDService methods.

Dependencies and integration: uses `netutil`, `dialer`, `osutil`, `build.Version`, `nat`, HTTP/XML, and logging. It is the NAT backend for UPnP.

Risks: network discovery is nondeterministic and router compatibility is fragile. `replaceRawPath` assumes non-empty relative path. Direct `http.Get` for device descriptions bypasses custom dialer/proxy settings. Tests cover XML and URL parsing only.
<!-- END_FILE_RESEARCH: sources/sync-backup/syncthing/lib/upnp/upnp.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/syncthing/lib/upnp/upnp_test.go -->
# sources/sync-backup/syncthing/lib/upnp/upnp_test.go

Purpose: unit tests for UPnP SOAP XML parsing and control URL normalization.

Important tests: `TestExternalIPParsing` unmarshals a SOAP external-IP response and expects `1.2.3.4`. `TestSoapFaultParsing` unmarshals a UPnP fault and expects error code 725. `TestControlURLParsing` verifies `replaceRawPath` produces the expected control URL for absolute-path and absolute-URL inputs.

State and persistence: no state; static XML and URL strings.

Dependencies and integration: covers internal response structs used by `IGDService.GetExternalIPv4Address` and error handling in port mapping/pinhole paths.

Risks and signals: helpful for XML tag paths and URL handling. It does not test SSDP sockets, device-description parsing, SOAP HTTP transport, IPv6 link-local handling, or actual NAT operations.
<!-- END_FILE_RESEARCH: sources/sync-backup/syncthing/lib/upnp/upnp_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/syncthing/lib/ur/contract/contract.go -->
# sources/sync-backup/syncthing/lib/ur/contract/contract.go

Purpose: defines the JSON/database contract for anonymous usage reports and crash/failure reports.

Important APIs and control flow: `Report` contains versioned fields tagged with JSON, metric metadata, and `since` versions. It includes v1/v2/v3 usage, feature, GUI, block, transport, ignore, post-processing, and database fields. `New` allocates a report and calls `structutil.FillNil` so maps/slices are non-nil. `Validate` checks core fields and date length, and normalizes some nil slices. `ClearForVersion` recursively clears fields whose `since` tag is absent or greater than the accepted report version. `Value` marshals to JSON string for SQL driver storage. `Scan` resets the receiver before unmarshalling from `[]byte`, preventing stale fields. `FailureReport` and `FailureData` model aggregated failure uploads.

State and persistence: report values can be stored through database/sql value scanning. Clearing mutates report structs before sending/storing.

Dependencies and integration: used by `ur.Service`, failure reporting, and post-processing/metrics pipelines. Depends on reflection and `structutil`.

Risks: reflection clearing must maintain all `since` tags; missing tags zero fields. `Scan` accepts only `[]byte`, not string. Tests cover clearing and scan reset behavior.
<!-- END_FILE_RESEARCH: sources/sync-backup/syncthing/lib/ur/contract/contract.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/syncthing/lib/ur/contract/contract_test.go -->
# sources/sync-backup/syncthing/lib/ur/contract/contract_test.go

Purpose: validates version-gated clearing and SQL scan reset behavior for usage-report contracts.

Important tests: fixture structs with nested structs, pointers, maps, slices, arrays, and `since` tags are passed through `clear` at versions 0 through 6. Expectations prove untagged fields are cleared, future fields are cleared, nested structs are recursively filtered, and pointer contents are handled. `TestMarshallingBehaviour` scans one JSON payload, then another, confirming the receiver is zeroed before unmarshal so old fields do not linger.

State and persistence: in-memory struct transformations only.

Dependencies and integration: targets the same reflection mechanism used by real `Report.ClearForVersion`.

Risks and signals: good coverage for version filtering, but does not validate the full `Report` field set, `Validate`, `Value`, or string scan inputs.
<!-- END_FILE_RESEARCH: sources/sync-backup/syncthing/lib/ur/contract/contract_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/syncthing/lib/ur/debug.go -->
# sources/sync-backup/syncthing/lib/ur/debug.go

Purpose: registers the usage-reporting package for debug logging.

Important APIs and control flow: package `init` calls `slogutil.RegisterPackage("Usage reporting")`.

State and persistence: logger/debug registry side effect only.

Dependencies and integration: connects usage-report logging to Syncthing debug package controls.

Risks and test signals: no logic beyond registration.
<!-- END_FILE_RESEARCH: sources/sync-backup/syncthing/lib/ur/debug.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/syncthing/lib/ur/failurereporting.go -->
# sources/sync-backup/syncthing/lib/ur/failurereporting.go

Purpose: aggregates and sends failure reports when crash/failure reporting is enabled through configuration.

Important APIs and control flow: `FailureDataWithGoroutines` captures goroutine profiles into `contract.FailureData`. `NewFailureHandler` returns a Suture service and config committer. `Serve` subscribes to config changes, applies options to subscribe/unsubscribe from `events.Failure`, buffers failures by description with first/last/count, flushes reports once failures age past `minDelay` or accumulate beyond `maxDelay`, sends asynchronously, and on shutdown sends remaining reports with a shorter final timeout. `applyOpts` computes `CRURL + "/failure"` and subscribes when usage reporting is accepted. `CommitConfiguration` pushes changed CR options into `optsChan`. `sendFailureReports` JSON-encodes an array and POSTs with Syncthing dialer and TLS defaults.

State and persistence: in-memory aggregation map; remote HTTP POST side effects. No local persistence.

Dependencies and integration: started early in `App.startup`; depends on events, config, suture, TLS/dialer, and usage contract.

Risks: `CommitConfiguration` sends on an unbuffered channel and can block if service is not receiving. Enabling logic checks `URAccepted > 0`, not `CREnabled`, despite commit watching `CREnabled`. Network failures only warn and drop reports.
<!-- END_FILE_RESEARCH: sources/sync-backup/syncthing/lib/ur/failurereporting.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/syncthing/lib/ur/memsize_darwin.go -->
# sources/sync-backup/syncthing/lib/ur/memsize_darwin.go

Purpose: Darwin implementation of physical memory size for usage reports.

Important APIs and control flow: `memorySize` runs `syscall.SysctlUint64("hw.memsize")` and returns the value as `int64`, or zero on error.

State and persistence: no state.

Dependencies and integration: called by `ur.Service.reportData` to populate `MemorySize` in MiB.

Risks: errors collapse to zero, so reports can omit meaningful memory size silently. Platform-specific and untested in this subset.
<!-- END_FILE_RESEARCH: sources/sync-backup/syncthing/lib/ur/memsize_darwin.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/syncthing/lib/ur/memsize_linux.go -->
# sources/sync-backup/syncthing/lib/ur/memsize_linux.go

Purpose: Linux implementation of physical memory size for usage reports.

Important APIs and control flow: `memorySize` reads `/proc/meminfo`, parses the first line with `fmt.Sscanf("MemTotal: %d kB\n", &kb)`, and returns kilobytes converted to bytes. Any read/parse error returns zero.

State and persistence: reads procfs only.

Dependencies and integration: feeds `contract.Report.MemorySize`.

Risks: assumes first line format of `/proc/meminfo`; containers may report host memory. Error-to-zero behavior avoids report failures but loses signal. No tests in this subset.
<!-- END_FILE_RESEARCH: sources/sync-backup/syncthing/lib/ur/memsize_linux.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/syncthing/lib/ur/memsize_netbsd.go -->
# sources/sync-backup/syncthing/lib/ur/memsize_netbsd.go

Purpose: NetBSD implementation of physical memory size for usage reports.

Important APIs and control flow: `memorySize` calls `unix.SysctlUint64("hw.physmem64")` and returns the result as `int64`, or zero on error.

State and persistence: no state.

Dependencies and integration: uses `golang.org/x/sys/unix`; called by usage-report data generation.

Risks: sysctl failures or unsupported environments silently produce zero. No tests in this subset.
<!-- END_FILE_RESEARCH: sources/sync-backup/syncthing/lib/ur/memsize_netbsd.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/syncthing/lib/ur/memsize_solaris.go -->
# sources/sync-backup/syncthing/lib/ur/memsize_solaris.go

Purpose: Solaris implementation of physical memory size for usage reports.

Important APIs and control flow: `memorySize` obtains page size through `unix.Getpagesize`, gets physical page count with `unix.Sysconf(unix.SC_PHYS_PAGES)`, and returns pages multiplied by page size. Errors return zero.

State and persistence: no state.

Dependencies and integration: uses `golang.org/x/sys/unix`; feeds usage report memory size.

Risks: multiplication could overflow only on unrealistic values before conversion context; syscall errors silently become zero. No tests in this subset.
<!-- END_FILE_RESEARCH: sources/sync-backup/syncthing/lib/ur/memsize_solaris.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/syncthing/lib/ur/memsize_unimpl.go -->
# sources/sync-backup/syncthing/lib/ur/memsize_unimpl.go

Purpose: fallback memory-size implementation for unsupported platforms.

Important APIs and control flow: build tags select this for platforms other than Darwin, Linux, NetBSD, Solaris, and Windows. `memorySize` returns zero.

State and persistence: none.

Dependencies and integration: allows usage reporting to compile on all supported platforms while omitting physical memory size where not implemented.

Risks and signals: reports from these platforms lack memory-size data. No tests needed.
<!-- END_FILE_RESEARCH: sources/sync-backup/syncthing/lib/ur/memsize_unimpl.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/syncthing/lib/ur/memsize_windows.go -->
# sources/sync-backup/syncthing/lib/ur/memsize_windows.go

Purpose: Windows implementation of physical memory size for usage reports.

Important APIs and control flow: defines lazy proc lookup for `kernel32.dll` `GetPhysicallyInstalledSystemMemory`. `memorySize` calls the proc with a pointer to a kilobyte output value, checks `res == 0` for failure, and returns kilobytes converted to bytes.

State and persistence: no state beyond lazy DLL/proc handles.

Dependencies and integration: uses `golang.org/x/sys/windows`; called by usage-report generation.

Risks: API returns installed physical memory, which may differ from available/container memory. Failure returns zero. No tests in this subset.
<!-- END_FILE_RESEARCH: sources/sync-backup/syncthing/lib/ur/memsize_windows.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/syncthing/lib/ur/usage_report.go -->
# sources/sync-backup/syncthing/lib/ur/usage_report.go

Purpose: builds, previews, sends, and schedules anonymous usage reports; also measures hashing performance.

Important APIs and control flow: `Service` stores config, model, connections service, no-upgrade flag, and a buffered force-run channel. `ReportData` and `ReportDataPreview` call `reportData`. `reportData` computes folder totals/maxima from model global sizes, runtime memory, process RSS, CPU count, SHA-256 scanner benchmark, physical memory, folder/device feature counts, discovery/relay settings, upgrade capability flags, and v3 options including NAT type, GUI stats, pull/copy-order maps, ownership/xattr flags, and rate-limit counts. It calls `model.UsageReportingStats`, then clears fields above the accepted version. `sendUsageReport` JSON POSTs to configured URL with optional insecure TLS. `Serve` subscribes to config, waits initial delay, sends daily when `URAccepted >= 2`, and reacts to forced runs when acceptance/URL/unique ID changes. `CpuBench` runs repeated `scanner.Blocks` over random data and returns best MiB/s.

State and persistence: no local persistence here; reads config/model state and sends remote reports. `StartTime` and `blocksResult` are package globals.

Dependencies and integration: wired in app startup with model and connections service. Depends on config, db counts, protocol/scanner, upgrade, contract, dialer, process stats, and TLS.

Risks: report generation can be CPU-expensive due to benchmark. `CommitConfiguration` only watches UR fields. POST response status is not checked. Tests for this file are absent in the subset; contract tests cover version clearing.
<!-- END_FILE_RESEARCH: sources/sync-backup/syncthing/lib/ur/usage_report.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/syncthing/lib/versioner/_external_test/external.sh -->
# sources/sync-backup/syncthing/lib/versioner/_external_test/external.sh

Purpose: helper script for external versioner tests.

Important APIs and control flow: shell script prints both arguments with markers, then removes the target file with `rm -f "$1/$2"`, where `$1` is folder path and `$2` is file path supplied by placeholder expansion.

State and persistence: deletes the test file in the testdata tree.

Dependencies and integration: invoked by `external_test.go` on non-Windows platforms as the configured external versioning command.

Risks and signals: intentionally simple; path quoting is important and covered by test paths with spaces/parentheses.
<!-- END_FILE_RESEARCH: sources/sync-backup/syncthing/lib/versioner/_external_test/external.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/syncthing/lib/versioner/debug.go -->
# sources/sync-backup/syncthing/lib/versioner/debug.go

Purpose: package logger adapter for file versioning.

Important APIs and control flow: initializes `l` with `slogutil.NewAdapter("File versioning")`.

State and persistence: logger only.

Dependencies and integration: used by simple, staggered, trashcan, external, and helper cleanup paths for diagnostics.

Risks and test signals: no behavior beyond logging setup.
<!-- END_FILE_RESEARCH: sources/sync-backup/syncthing/lib/versioner/debug.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/syncthing/lib/versioner/empty_dir_tracker.go -->
# sources/sync-backup/syncthing/lib/versioner/empty_dir_tracker.go

Purpose: tracks directories under a version archive that can be removed after old files are cleaned.

Important APIs and control flow: `emptyDirTracker` is a map of directory paths. `addDir` adds non-root directories. `addFile` removes the file's directory and all ancestors from the candidate map, because they contain retained content. `emptyDirs` returns candidates sorted deepest-first by reverse string comparison, so children are removed before parents. `deleteEmptyDirs` removes each candidate through the supplied filesystem and warns on failures.

State and persistence: in-memory candidate set; `deleteEmptyDirs` mutates the version filesystem by removing directories.

Dependencies and integration: used by `trashcan.Clean` after deleting old files.

Risks: reverse lexicographic sort is intended to approximate deepest-first and works for nested paths in tests, but path-depth sorting would be more explicit. Removal failures are logged and ignored. Test coverage models nested keep/remove directories.
<!-- END_FILE_RESEARCH: sources/sync-backup/syncthing/lib/versioner/empty_dir_tracker.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/syncthing/lib/versioner/empty_dir_tracker_test.go -->
# sources/sync-backup/syncthing/lib/versioner/empty_dir_tracker_test.go

Purpose: verifies empty-directory candidate tracking and removal order.

Important tests: `TestEmptyDirs` models a `.stversions` tree with two kept branches containing files and two empty remove branches. It adds dirs/files to `emptyDirTracker`, normalizes paths for Windows, and expects only empty branches returned deepest-first.

State and persistence: in-memory path list only.

Dependencies and integration: uses `messagediff` for readable diffs.

Risks and signals: good coverage for the tracker algorithm. It does not call `deleteEmptyDirs` against a filesystem or cover removal errors.
<!-- END_FILE_RESEARCH: sources/sync-backup/syncthing/lib/versioner/empty_dir_tracker_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/syncthing/lib/versioner/external.go -->
# sources/sync-backup/syncthing/lib/versioner/external.go

Purpose: external command-based file versioner.

Important APIs and control flow: `init` registers factory `external`. `newExternal` reads the configured command and escapes backslashes on Windows. `Archive` lstat-checks the file, ignores nonexistent files, panics on symlinks, validates command presence, shell-splits the command, substitutes `%FOLDER_FILESYSTEM%`, `%FOLDER_PATH%`, and `%FILE_PATH%`, executes it with environment variables filtered to remove `STGUIAUTH` and `STGUIAPIKEY`, logs combined output, and succeeds only if the file no longer exists. `GetVersions` and `Restore` return `ErrRestorationNotSupported`; `Clean` is a no-op.

State and persistence: external command can perform arbitrary filesystem side effects; this code only verifies removal.

Dependencies and integration: uses folder filesystem abstraction, build OS flag, `go-shellquote`, and OS process execution.

Risks: command execution is powerful and configuration-controlled. Placeholder substitution occurs after shell splitting, so paths with spaces are passed as one arg only when placeholder occupies a quoted/split word appropriately. Tests cover missing command and successful quoted removal.
<!-- END_FILE_RESEARCH: sources/sync-backup/syncthing/lib/versioner/external.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/syncthing/lib/versioner/external_test.go -->
# sources/sync-backup/syncthing/lib/versioner/external_test.go

Purpose: tests external versioner command failure and success with paths containing spaces/parentheses.

Important tests: `TestExternalNoCommand` prepares a file, runs an invalid command, expects an error, and verifies the file remains. `TestExternal` selects a shell or batch helper command by platform, prepares a nested path with spaces and parentheses, runs `Archive`, and verifies the file is removed. `prepForRemoval` resets and creates the testdata file.

State and persistence: creates and removes local `testdata` under the package directory.

Dependencies and integration: invokes real external script/batch and basic filesystem.

Risks and signals: covers placeholder expansion and command execution at a functional level. It does not test secret environment filtering, symlink panic, restoration unsupported paths, or command stderr wrapping.
<!-- END_FILE_RESEARCH: sources/sync-backup/syncthing/lib/versioner/external_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/syncthing/lib/versioner/simple.go -->
# sources/sync-backup/syncthing/lib/versioner/simple.go

Purpose: simple count/age-based file versioner.

Important APIs and control flow: `init` registers factory `simple`. `newSimple` reads `keep` with default 5 and optional `cleanoutDays`, builds source and versions filesystems, and stores copy-range method. `Archive` moves the file to the versions filesystem using `archiveFile` with `TagFilename`, then calls `cleanVersions` for that file using `toRemove`. `GetVersions` and `Restore` delegate to shared retrieval/restore helpers. `Clean` runs global version cleanup. `toRemove` sorts version names, removes oldest entries beyond `keep`, then if `cleanoutDays > 0`, parses remaining timestamp tags and removes versions older than the max age.

State and persistence: moves files from folder filesystem into versions filesystem and deletes old version files.

Dependencies and integration: uses config versioning params, fs abstraction, shared versioner helpers, and local time parsing.

Risks: invalid timestamp tags are skipped for age cleanup. `keep <= 0` can remove all count-limited versions depending on slicing behavior. Tests cover count, tilde paths, permissions via shared helpers.
<!-- END_FILE_RESEARCH: sources/sync-backup/syncthing/lib/versioner/simple.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/syncthing/lib/versioner/simple_test.go -->
# sources/sync-backup/syncthing/lib/versioner/simple_test.go

Purpose: tests version filename tagging, simple retention, path expansion, and archive-directory permission helper behavior.

Important tests: `TestTaggedFilename` validates tag insertion before extensions and tag extraction across names containing tildes. `TestSimpleVersioningVersionCount` archives repeatedly with keep=2 and expects only the newest two versions. `TestPathTildes` sets HOME and verifies folder/version paths beginning with `~` expand correctly. `TestArchiveFoldersCreationPermission` checks version directory tree permissions mirror source directories and remain stable across repeated archive. `TestDupDirTreeWritePermissions` and `TestDupDirFastPath` validate helper behavior that creates/upgrades destination directory permissions with user-write bits.

State and persistence: temp directories, fake filesystems, and package `testdata` cleanup.

Dependencies and integration: covers simple versioner plus shared helper functions not in this specific source list.

Risks and signals: strong filesystem behavior coverage; count test is skipped in short mode. Age-based `cleanoutDays` is not tested here.
<!-- END_FILE_RESEARCH: sources/sync-backup/syncthing/lib/versioner/simple_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/syncthing/lib/versioner/staggered.go -->
# sources/sync-backup/syncthing/lib/versioner/staggered.go

Purpose: staggered retention file versioner that keeps dense recent versions and sparse older versions.

Important APIs and control flow: `init` registers factory `staggered`. `newStaggered` reads `maxAge` defaulting to about one year and configures four intervals: 30 seconds for first hour, one hour for next day, one day for next 30 days, and one week until max age. `Clean` delegates global cleanup. `toRemove` sorts versions, parses timestamp tags, removes versions older than max age, keeps the oldest first version as an anchor, then removes versions whose age spacing from the previous kept version is below the interval step. `Archive`, `GetVersions`, and `Restore` use shared helpers with `TagFilename`; `String` returns pointer identity.

State and persistence: archives source files to versions filesystem and deletes versions selected by retention logic.

Dependencies and integration: config params, fs abstraction, local time, and shared versioner helpers.

Risks: retention depends on filename timestamp parsing and local timezone. The algorithm iterates sorted filenames, so timestamp format order must remain lexicographic. Tests cover interval selection extensively.
<!-- END_FILE_RESEARCH: sources/sync-backup/syncthing/lib/versioner/staggered.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/syncthing/lib/versioner/staggered_test.go -->
# sources/sync-backup/syncthing/lib/versioner/staggered_test.go

Purpose: validates staggered retention interval math and archive path creation.

Important tests: `TestStaggeredVersioningVersionCount` defines a fixed `now`, a dense set of timestamped versions across seconds, hours, days, weeks, and over max age, then expects a precise delete list after `toRemove`. It sorts expected and actual lists and uses `messagediff`. `TestCreateVersionPath` configures a nested versions directory, archives a file, and confirms a version file is created under that directory.

State and persistence: fixed timestamp strings and temp directory archive writes.

Dependencies and integration: exercises `newStaggered`, timestamp parsing, and archive helper integration.

Risks and signals: high-signal retention coverage, including leap-year comments. It does not test restore or cleanup context cancellation.
<!-- END_FILE_RESEARCH: sources/sync-backup/syncthing/lib/versioner/staggered_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/syncthing/lib/versioner/trashcan.go -->
# sources/sync-backup/syncthing/lib/versioner/trashcan.go

Purpose: trashcan-style versioner that moves deleted/changed files into a versions area without timestamping the archived filename.

Important APIs and control flow: `init` registers `trashcan`. `newTrashcan` reads optional `cleanoutDays`, builds folder and versions filesystems, and stores copy-range method. `Archive` calls `archiveFile` with an identity tagger, so archive paths match original paths. `Clean` returns immediately when cleanout is disabled or versions dir is missing; otherwise it computes a cutoff, walks the versions filesystem, records directories, removes files older than cutoff, marks directories containing retained files, and deletes empty directories afterward. `GetVersions` delegates retrieval. `Restore` handles the untagged archive collision case by temporarily tagging any existing destination file, restoring the requested version, then renaming the temporary archive back if needed.

State and persistence: moves files into versions filesystem, deletes old trashcan files, removes empty directories, and may temporarily rename archived destination conflicts.

Dependencies and integration: config, fs abstraction, `emptyDirTracker`, and shared archive/restore helpers.

Risks: restore collision logic is subtle because untagged archive names can be overwritten. Clean uses file modtime, not embedded tag time. No direct tests in this batch for trashcan restore/clean.
<!-- END_FILE_RESEARCH: sources/sync-backup/syncthing/lib/versioner/trashcan.go -->
