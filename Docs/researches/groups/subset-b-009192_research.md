# subset-b-009192 research

Grouped research report for the subset B work item. Each section is source-tree aligned and bounded by the required reconciliation markers.

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/syncthing/internal/gen/dbproto/structs.pb.go -->
# sources/sync-backup/syncthing/internal/gen/dbproto/structs.pb.go

Purpose: Generated Go protobuf bindings for `dbproto/structs.proto`, defining database persistence messages used by Syncthing's internal index and metadata database. It mirrors selected BEP protocol structures while omitting or separating heavy fields for storage efficiency.

Important APIs/types/functions: The exported message types are `FileInfoTruncated`, `FileVersion`, `VersionList`, `BlockList`, `IndirectionHashesOnly`, `Counts`, `CountsSet`, `ObservedFolder`, and `ObservedDevice`. Each has generated `Reset`, `String`, `ProtoReflect`, deprecated `Descriptor`, and nil-safe getters. `FileInfoTruncated` stores file metadata without inline blocks: name, size, type, permissions, modified time split into seconds/nanos, modified-by, version vector, sequence, symlink target, block hashes, encryption metadata, platform data, deletion/invalid/no-permission flags, and host-local implementation fields such as local flags, version hash, and encryption trailer size. `BlockList` carries the omitted BEP block list separately. `Counts` and `CountsSet` persist summary counts and creation timestamps. `ObservedFolder` and `ObservedDevice` persist remote observation metadata.

Control flow: There is no domain logic beyond generated protobuf runtime behavior. `init` calls `file_dbproto_structs_proto_init`, which builds a `protoreflect.FileDescriptor` through `protoimpl.TypeBuilder`, wires BEP and timestamp dependencies, and nils raw descriptor/type slices after initialization. Raw descriptor compression is guarded by `sync.Once`.

State and persistence behavior: These message structs are persistence contracts. Field numbers, names, and protobuf wire types are the durable database schema, including high-numbered local fields. Changing or removing fields risks breaking database compatibility and migrations. Nil getters intentionally return zero values for partially decoded or absent data.

Dependencies and integration points: Depends on generated `internal/gen/bep` types (`Vector`, `FileInfoType`, `PlatformData`, `BlockInfo`) and `google.protobuf.Timestamp`. Consumers are expected to marshal/unmarshal through `google.golang.org/protobuf/proto` in Syncthing database code.

Risks: Because this is generated code, manual edits will be overwritten and may diverge from the `.proto` source. The most sensitive risks are schema drift, accidental reuse of removed field numbers, and confusing host-local fields with protocol wire fields. No validation is performed by the generated accessors; callers must enforce semantic constraints.

Test signals: No direct tests in this file. Coverage comes indirectly from database/index serialization tests and any tests that round-trip file metadata, counts, observed folders/devices, or block indirection through the database.
<!-- END_FILE_RESEARCH: sources/sync-backup/syncthing/internal/gen/dbproto/structs.pb.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/syncthing/internal/gen/discoproto/local.pb.go -->
# sources/sync-backup/syncthing/internal/gen/discoproto/local.pb.go

Purpose: Generated protobuf bindings for local discovery announce packets.

Important APIs/types/functions: Defines the `Announce` message with `Id []byte`, repeated `Addresses []string`, and `InstanceId int64`. Generated methods provide reflection, stringification, reset, descriptor access, and nil-safe getters.

Control flow: Runtime initialization builds one message descriptor from the raw `discoproto/local.proto` descriptor. Descriptor gzip compression is lazy and protected by `sync.Once`.

State and persistence behavior: The file does not persist state itself. It defines the serialized shape for local discovery announcements, so field numbers and types are network compatibility contracts. `InstanceId` helps distinguish process instances advertising the same device identity.

Dependencies and integration points: Uses the Go protobuf runtime. Integrated by discovery/beacon code that marshals local announcements and decodes inbound announcements.

Risks: Generated code should not be edited directly. Compatibility risk lies in altering the `.proto` schema without considering older nodes that expect these fields.

Test signals: No direct test in this file; exercised indirectly by local discovery tests and runtime interoperability.
<!-- END_FILE_RESEARCH: sources/sync-backup/syncthing/internal/gen/discoproto/local.pb.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/syncthing/internal/gen/discosrv/discosrv.pb.go -->
# sources/sync-backup/syncthing/internal/gen/discosrv/discosrv.pb.go

Purpose: Generated protobuf bindings for discovery server database and replication records.

Important APIs/types/functions: `DatabaseRecord` stores announced `DatabaseAddress` entries plus a `Seen` unix-nanos timestamp. `ReplicationRecord` adds the raw 32-byte device ID `Key` for replication transport. `DatabaseAddress` stores an address string and unix-nanos expiry. Generated reset, reflection, descriptor, and getter methods are present for all messages.

Control flow: `init` builds a descriptor with three messages and dependency indexes linking address lists to `DatabaseAddress`. The raw descriptor is lazily gzipped under `sync.Once`.

State and persistence behavior: These messages represent durable discovery-server state and replication payloads. Timestamp fields use nanoseconds, so callers must keep units consistent when pruning or comparing records.

Dependencies and integration points: Uses only the protobuf runtime. It integrates with discovery server storage/replication code that stores device addresses and distributes address updates between discovery nodes.

Risks: Address expiry and seen timestamps are plain `int64` values without validation here. Schema changes may break persisted discovery server data or replication compatibility.

Test signals: No direct test in the generated file; validated by discovery server storage and replication tests elsewhere.
<!-- END_FILE_RESEARCH: sources/sync-backup/syncthing/internal/gen/discosrv/discosrv.pb.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/syncthing/internal/itererr/itererr.go -->
# sources/sync-backup/syncthing/internal/itererr/itererr.go

Purpose: Utility helpers for Go `iter` sequences that carry their terminal error through a separate error function.

Important APIs/types/functions: `Collect` consumes an `iter.Seq[T]` into a slice and returns `errFn()`. `Zip` converts a value iterator plus error function into an `iter.Seq2[T,error]`, yielding values with nil errors and one zero-value item with the final error if non-nil. `Map` and `Map2` transform single-value sequences into new `Seq` or `Seq2` values while preserving the original iterator error and any mapping error.

Control flow: `Map`/`Map2` close over `retErr`. Iteration stops immediately when `mapFn` returns an error or when the downstream yield returns false. The returned error function gives priority to the upstream `errFn`, then returns the mapping error.

State and persistence behavior: No persistence. The only state is the captured `retErr`, so returned iterators are not designed for concurrent or repeated independent consumption.

Dependencies and integration points: Depends on the standard `iter` package. Used by code that wants idiomatic range-over-function iteration while still surfacing I/O or database scan errors after iteration.

Risks: `Zip` calls `yield` for the terminal error but does not observe that return value. `Map` and `Map2` store one shared error variable, which can surprise callers if a sequence is reused. Callers must always call the returned error function after iteration.

Test signals: No direct test in this subset. Expected coverage should include early-yield cancellation, upstream error priority, mapper errors, and successful collection.
<!-- END_FILE_RESEARCH: sources/sync-backup/syncthing/internal/itererr/itererr.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/syncthing/internal/protoutil/protoutil.go -->
# sources/sync-backup/syncthing/internal/protoutil/protoutil.go

Purpose: Small protobuf marshaling helper for writing into caller-provided buffers without unexpected allocation.

Important APIs/types/functions: `MarshalTo(buf []byte, pb proto.Message) (int, error)` checks `proto.Size(pb)` against `len(buf)`, returns `errBufferTooSmall` when insufficient, returns zero for zero-size messages, then uses `proto.MarshalOptions.MarshalAppend(buf[:0], pb)`.

Control flow: After marshaling, it compares the first element address of the original buffer and returned slice. If they differ, it panics because the earlier size check should have prevented reallocation.

State and persistence behavior: Stateless. It serializes protobuf messages into transient buffers, likely on network or storage hot paths.

Dependencies and integration points: Depends on `google.golang.org/protobuf/proto`. Integrates with generated protobuf messages across Syncthing.

Risks: `errBufferTooSmall` is package-private, so callers can only compare by error string unless they are in-package. The address check relies on non-empty buffers and is bypassed for zero-size protobufs. Callers must use the returned byte count rather than assuming the whole buffer was filled.

Test signals: No direct test in this subset. Useful tests would cover too-small buffers, exact-fit buffers, zero-size messages, and marshal errors.
<!-- END_FILE_RESEARCH: sources/sync-backup/syncthing/internal/protoutil/protoutil.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/syncthing/internal/slogutil/expensive.go -->
# sources/sync-backup/syncthing/internal/slogutil/expensive.go

Purpose: Deferred slog value wrapper for log attributes that are expensive to compute.

Important APIs/types/functions: `Expensive(fn func() any) expensive` returns a value implementing `slog.LogValuer` through `LogValue`, which calls `fn` only when slog resolves the value.

Control flow: No branching. `LogValue` delegates to the captured callback and wraps the result with `slog.AnyValue`.

State and persistence behavior: Stateless apart from the callback closure. No persistence.

Dependencies and integration points: Depends on `log/slog`. Intended for use with Syncthing's `formattingHandler`, which calls `Value.Resolve()` only after the record has passed handler/package-level filtering.

Risks: The callback can still run more than once if a value is resolved more than once. Callback side effects would be risky. Nil callbacks will panic on resolution.

Test signals: No direct test in this subset. A useful test would assert the callback is not invoked for a filtered-out debug message.
<!-- END_FILE_RESEARCH: sources/sync-backup/syncthing/internal/slogutil/expensive.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/syncthing/internal/slogutil/formatting.go -->
# sources/sync-backup/syncthing/internal/slogutil/formatting.go

Purpose: Syncthing's custom `slog.Handler` that formats log records into the legacy human-readable line style while preserving structured attributes for expansion and recording.

Important APIs/types/functions: `LineFormat` controls timestamp, textual level, and syslog priority rendering. `formattingOptions` carries output writer, recorders, and a test time override. `formattingHandler` implements `slog.Handler` with `Enabled`, `Handle`, `WithAttrs`, and `WithGroup`. `SetLineFormat` mutates the global formatter. Helpers include `expandAttrs`, `appendAttr`, and `funcNameToPkg`.

Control flow: `Handle` derives package/type/source information from `rec.PC`, checks package log level through `globalLevels`, appends package/source log attributes, prefixes grouped attrs, expands nested slog groups into dotted keys, quotes confusing or empty values, records the final `Line`, and writes it to the configured writer. `WithAttrs` applies active group prefixes to new attrs, while `WithGroup` prepends group names for later prefixing.

State and persistence behavior: Global formatting state lives in `globalFormatter`; in-memory log lines are copied into configured `lineRecorder`s. There is no disk persistence in this handler.

Dependencies and integration points: Depends on `runtime.CallersFrames`, `log/slog`, `Line`, `lineRecorder`, and the package-level log tracker. It is installed as the default slog handler by `sloginit.go` and feeds API log endpoints through recorders.

Risks: `SetLineFormat` mutates global state without synchronization. `WithGroup` prepends group names, which produces the observed `bar.foo` order for nested groups and is a compatibility behavior to preserve. Function-name parsing assumes Syncthing package path conventions. Attribute formatting is lossy compared with structured JSON logs.

Test signals: `formatting_test.go` verifies quoting, grouping, level filtering, package metadata, and debug filtering at default info level.
<!-- END_FILE_RESEARCH: sources/sync-backup/syncthing/internal/slogutil/formatting.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/syncthing/internal/slogutil/formatting_test.go -->
# sources/sync-backup/syncthing/internal/slogutil/formatting_test.go

Purpose: Golden-style unit test for the custom slog formatter.

Important APIs/types/functions: `TestFormattingHandler` constructs a `formattingHandler` with `DefaultLineFormat`, a buffer writer, and a fixed UTC timestamp. It logs info, debug, warn, and error records with plain attrs, attrs needing quoting, empty values, nested `slog.Group`s, and logger-level groups.

Control flow: The test emits messages, trims actual and expected output, and fails on exact mismatch while logging both strings. Debug output is expected to be filtered by package-level defaults.

State and persistence behavior: No persistence. It uses an in-memory `bytes.Buffer` and a deterministic `timeOverride`.

Dependencies and integration points: Exercises `formattingHandler`, `Line.WriteTo`, `appendAttr`, `expandAttrs`, `funcNameToPkg`, and global package-level filtering.

Risks: The expected string encodes current group prefix order and package attribution. Any intentional formatter change requires updating the golden output. It does not test syslog priority mode, recorder capture, or source file/line output when package debug is enabled.

Test signals: This is the direct regression signal for human log formatting compatibility.
<!-- END_FILE_RESEARCH: sources/sync-backup/syncthing/internal/slogutil/formatting_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/syncthing/internal/slogutil/leveler.go -->
# sources/sync-backup/syncthing/internal/slogutil/leveler.go

Purpose: Tracks per-package log levels and descriptions, including compatibility with the traditional `STTRACE` package override format.

Important APIs/types/functions: Public functions expose package descriptions/levels and set package/default levels: `PackageDescrs`, `PackageLevels`, `SetPackageLevel`, `SetDefaultLevel`, and `SetLevelOverrides`. `levelTracker` stores `defLevel`, package descriptions, and package-specific level overrides under an RW mutex.

Control flow: `SetLevelOverrides` splits comma-separated input, defaults each listed package to DEBUG, and optionally parses `pkg:LEVEL` via `slog.Level.UnmarshalText`. `levelTracker.Get` returns explicit levels or the default. Setters log an info message when a value changes. `Levels` returns a map for all registered descriptions, using defaults where no explicit override exists.

State and persistence behavior: In-memory global state only. Changes affect log filtering immediately but are not persisted here.

Dependencies and integration points: Used by `formattingHandler` to filter records by caller package. `slogadapter.RegisterPackage` and `NewAdapter` register descriptions. REST API endpoints expose and mutate levels through `/rest/system/loglevels`.

Risks: `SetLevelOverrides` logs warnings through the same logging system it configures, so bad early configuration could be noisy. The `Levels` snapshot only includes described packages, not arbitrary package strings set without descriptions.

Test signals: Indirectly tested by formatter output and API log-level endpoint tests. Dedicated tests should cover STTRACE parsing and invalid levels.
<!-- END_FILE_RESEARCH: sources/sync-backup/syncthing/internal/slogutil/leveler.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/syncthing/internal/slogutil/line.go -->
# sources/sync-backup/syncthing/internal/slogutil/line.go

Purpose: Defines the internal log-line representation used by the formatter, in-memory recorders, and API responses.

Important APIs/types/functions: `Line` contains `When`, `Message`, and `Level`. `WriteTo` renders optional syslog priority, timestamp, level string, message, and newline. `levelStr` maps slog levels to `DBG`, `INF`, `WRN`, and `ERR`, preserving numeric offsets. `syslogPriority` maps levels to syslog priorities. `MarshalJSON` emits short level strings instead of slog's default numeric encoding.

Control flow: Rendering builds a buffer and writes it to the supplied writer. JSON marshaling constructs a small map with the custom level string.

State and persistence behavior: A `Line` is immutable-by-convention value state for logs. No persistence is performed here; recorders and API handlers store or expose it.

Dependencies and integration points: Used by `formattingHandler`, `lineRecorder`, `/rest/system/log`, `/rest/system/error`, and support bundles.

Risks: JSON output uses a map, so field ordering is not part of the contract. The syslog priority mapping is simple and should be kept consistent with operational logging expectations.

Test signals: Covered indirectly by `formatting_test.go` and API log endpoint tests.
<!-- END_FILE_RESEARCH: sources/sync-backup/syncthing/internal/slogutil/line.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/syncthing/internal/slogutil/recorder.go -->
# sources/sync-backup/syncthing/internal/slogutil/recorder.go

Purpose: Bounded in-memory log recorder.

Important APIs/types/functions: `Recorder` exposes `Since(time.Time) []Line` and `Clear()`. `NewRecorder(level slog.Level)` returns a `lineRecorder`. `lineRecorder.record` filters below its level, appends lines, and retains only the newest `maxLogLines` entries.

Control flow: All mutations and reads are protected by a mutex. `Since` scans from oldest to newest and returns a slice starting at the first line whose timestamp is after the supplied time.

State and persistence behavior: Keeps up to 1000 `Line` values in memory. `Clear` drops the buffer. The returned slice aliases internal storage, so callers should treat it as read-only.

Dependencies and integration points: Global and error recorders are wired in `sloginit.go`; API endpoints and support bundles read from them.

Risks: Returning an internal slice after unlocking can expose races if callers mutate it or if later appends re-use storage. Bounded retention means older log data disappears from API responses.

Test signals: No direct tests in this subset; API log and support bundle tests exercise read paths indirectly.
<!-- END_FILE_RESEARCH: sources/sync-backup/syncthing/internal/slogutil/recorder.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/syncthing/internal/slogutil/slogadapter.go -->
# sources/sync-backup/syncthing/internal/slogutil/slogadapter.go

Purpose: Compatibility adapter from Syncthing's older debug logging style to `log/slog`, plus package registration.

Important APIs/types/functions: `RegisterPackage` and `NewAdapter` derive the caller package from the runtime stack and register a description. `adapter` exposes `Debugln`, `Debugf`, and `ShouldDebug`. Internal `log` builds a `slog.Record` with the caller PC and sends it to the underlying handler.

Control flow: Debug methods format the message, check handler enablement, capture the caller PC with `runtime.Callers(3, ...)`, and invoke `Handle` on the default slog handler. `ShouldDebug` asks `globalLevels` for the facility level.

State and persistence behavior: Registers package descriptions in global in-memory log-level state. No persistence.

Dependencies and integration points: Used by packages such as API and beacon to keep `l.Debugf`/`l.Debugln` calls while using slog formatting and filtering.

Risks: Caller skip depths are fragile; wrapper changes can misattribute package names. Only debug-level logging is implemented by the adapter.

Test signals: Formatter test indirectly verifies package attribution for logs from `slogutil`.
<!-- END_FILE_RESEARCH: sources/sync-backup/syncthing/internal/slogutil/slogadapter.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/syncthing/internal/slogutil/sloginit.go -->
# sources/sync-backup/syncthing/internal/slogutil/sloginit.go

Purpose: Initializes Syncthing's global slog handler, default recorders, default line format, and package-level tracker.

Important APIs/types/functions: Defines `GlobalRecorder`, `ErrorRecorder`, `DefaultLineFormat`, `globalLevels`, `globalFormatter`, and `slogDef`. `logWriter` returns `io.Discard` when `LOGGER_DISCARD` is set, otherwise stdout. `init` installs `slogDef` as the process default logger.

Control flow: Package initialization constructs the formatter with both recorders and an output writer, then calls `slog.SetDefault`.

State and persistence behavior: Creates global in-memory recorder state. Output goes to stdout unless explicitly discarded through environment configuration.

Dependencies and integration points: This is the root logging setup used throughout Syncthing, including API log endpoints and legacy adapters.

Risks: Package import order controls when the default logger is installed. `LOGGER_DISCARD` disables stdout output but still records in memory. Global mutable formatter/level state can affect tests if not isolated.

Test signals: Formatter and API tests depend on this initialization behavior, though they often use custom recorders.
<!-- END_FILE_RESEARCH: sources/sync-backup/syncthing/internal/slogutil/sloginit.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/syncthing/internal/slogutil/slogvalues.go -->
# sources/sync-backup/syncthing/internal/slogutil/slogvalues.go

Purpose: Convenience constructors for common structured log attributes.

Important APIs/types/functions: `Address`, `Error`, `FilePath`, and `URI` return standardized slog attributes. `Error(nil)` returns an empty attribute so callers can pass it conditionally. Generic `Map` turns a map into sorted `[]any` slog args.

Control flow: `Map` sorts map keys with `slices.Sorted(maps.Keys(m))`, producing deterministic log attribute ordering.

State and persistence behavior: Stateless.

Dependencies and integration points: Used across API, beacon, support bundle, and other packages for consistent key names and deterministic map logging.

Risks: `Error(nil)` produces an empty key, which the formatter ignores; other handlers may represent it differently. `Map` allocates and is intended for logging convenience, not hot path data conversion.

Test signals: Deterministic map ordering is not directly tested here but affects stable log output.
<!-- END_FILE_RESEARCH: sources/sync-backup/syncthing/internal/slogutil/slogvalues.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/syncthing/internal/timeutil/timeutil.go -->
# sources/sync-backup/syncthing/internal/timeutil/timeutil.go

Purpose: Provides strictly increasing unix-nanosecond timestamps independent of wall-clock resolution or backward jumps.

Important APIs/types/functions: `StrictlyMonotonicNanos` loops on an atomic `prevNanos`, computes `max(time.Now().UnixNano(), old+1)`, and commits with compare-and-swap.

Control flow: The function retries until its CAS succeeds, guaranteeing each caller observes a value greater than the last committed value.

State and persistence behavior: Maintains process-global atomic timestamp state. No disk persistence.

Dependencies and integration points: Depends on `sync/atomic` and `time`. Useful where database keys, event timestamps, or token expiries need monotonic nanosecond ordering.

Risks: If the process emits many timestamps while wall time moves backward, returned values can run ahead of real time. It is process-local only and does not coordinate across restarts or nodes.

Test signals: No direct test in this subset. Concurrency and clock-backward tests would be valuable.
<!-- END_FILE_RESEARCH: sources/sync-backup/syncthing/internal/timeutil/timeutil.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/syncthing/lib/api/api.go -->
# sources/sync-backup/syncthing/lib/api/api.go

Purpose: Implements Syncthing's GUI/API service: listener setup, HTTP routing, security middleware, REST handlers, event streaming, support diagnostics, upgrade actions, file/index views, and helper serialization.

Important APIs/types/functions: `Service` combines `suture.Service`, `config.Committer`, and `WaitForStart`. `New` wires device ID, config, model, events, discovery, connections, UR service, recorders, upgrade flag, and misc DB into `service`. Core lifecycle methods are `WaitForStart`, `getListener`, `Serve`, `Complete`, `VerifyConfiguration`, `CommitConfiguration`, and `fatal`. Middleware includes `debugMiddleware`, `corsMiddleware`, `redirectToHTTPSMiddleware`, `noCacheMiddleware`, `withDetailsMiddleware`, and `localhostMiddleware`. REST handlers cover cluster pending devices/folders, DB completion/status/need/file/browse/ignores/scan/prio/override/revert, stats, system status/version/log/errors/discovery/paths/upgrade/reset/restart/shutdown/browse/profiling/support, events, language negotiation, QR generation, and config routes registered through `confighandler.go`. Helper types include `fileEntry`, `jsonFileInfo`, `jsonVersionVector`, `discoveryStatusEntry`, and `bufferedResponseWriter`.

Control flow: `Serve` obtains a TLS-capable downgrading listener, subscribes for config commits, builds `httprouter` routes, wraps them in no-cache, static asset, metadata, metrics, CSRF, details, optional auth/session, optional HTTPS redirect, CORS, localhost host checking, and debug logging middleware, then starts `http.Server.Serve` in a goroutine. It waits on context cancellation, config change, fatal exit, or serve error, then gracefully shuts down with a short timeout. Config GUI changes call `CommitConfiguration`, update theme if needed, and signal `configChanged` to restart the listener. Many POST handlers intentionally kick off model operations asynchronously or signal process exit through `fatal`.

State and persistence behavior: State includes listener address, event subscription cache, startup channels, fatal exit channel, shutdown timeout, and recorders. It persists HTTPS cert/key through locations and `tlsutil.NewCertificate`, writes config through the config wrapper in config handlers, writes a backup support zip into the config directory, and reads logs/panic files from configured locations. Token and CSRF persistence is delegated to `tokenmanager.go`.

Dependencies and integration points: This is a central integration surface for `config`, `model`, `events`, `discover`, `connections`, `ur`, `upgrade`, `locations`, `fs`, `protocol`, `tlsutil`, `slogutil`, Prometheus, suture, and generated/compiled assets. It exposes runtime state to the GUI and external REST clients.

Risks: The file is high blast radius. Security-sensitive points include auth ordering, CSRF bypass for API keys/noauth/debug paths, CORS behavior, localhost host checks, reverse-proxy handling, profiling/debug endpoints, and support bundle redaction. Operational risks include long CPU profiling sleeps inside handlers, assumptions that response writers implement `http.Flusher`, config-change restart races, and duplicate route registration for `/rest/db/localchanged`. Certificate regeneration logic intentionally leaves non-Syncthing/custom certs alone.

Test signals: `api_test.go` exercises service startup, asset precedence, many GET endpoints, login/session/API-key paths, CSRF, host checking, CORS/OPTIONS, event masks, browse completion, certificate regeneration, config changes, and hostname sanitization. `api_auth_test.go` covers static auth and token manager behavior. Config handler behavior is also covered by config-change tests.
<!-- END_FILE_RESEARCH: sources/sync-backup/syncthing/lib/api/api.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/syncthing/lib/api/api_auth.go -->
# sources/sync-backup/syncthing/lib/api/api_auth.go

Purpose: Authentication middleware and helpers for GUI/API access, supporting API keys, session cookies, Basic auth, JSON password login, static bcrypt credentials, and LDAP.

Important APIs/types/functions: Constants bound active sessions, random token length, and login body size. `emitLoginAttempt`, `remoteAddress`, `antiBruteForceSleep`, `unauthorized`, `forbidden`, and `isNoAuthPath` support audit events and responses. `basicAuthAndSessionMiddleware` implements `ServeHTTP`, `passwordAuthHandler`, and logout handling. `attemptBasicAuth`, `auth`, `authStatic`, `authLDAP`, `formatOptionalPercentS`, and `iso88591ToUTF8` implement credential checks.

Control flow: Middleware accepts valid API-key headers first, then valid session cookies, then Basic auth. Successful Basic auth creates a non-persistent session cookie. Public paths and static assets are allowed after auth attempts. If protected and unauthenticated, it returns either 401 with a Basic realm or 403 depending on config. JSON password login is limited to 1 KiB, creates a session on success, and sleeps 100-199 ms on failure. LDAP auth dials plain/TLS/StartTLS, binds with interpolated DN, and optionally searches for exactly one matching user.

State and persistence behavior: Session persistence is delegated to `tokenCookieManager` and misc DB. Login attempts are emitted to the event logger. Failed credentials are logged with redacted structured metadata.

Dependencies and integration points: Integrates with config GUI and LDAP config, event logging, random jitter, IP parsing utilities, and `tokenmanager.go`. Used from `api.go` around the full handler chain when GUI auth is enabled.

Risks: Security-sensitive code. Reverse proxy address trust is intentionally limited to loopback/private/link-local/unix-socket peers. LDAP TLS can be configured with insecure verification. `formatOptionalPercentS` uses `fmt.Sprintf` with counted `%s`; malformed templates with other formatting directives could still behave unexpectedly. Basic auth ISO-8859-1 fallback preserves compatibility but expands accepted credential encodings.

Test signals: `api_test.go` covers Basic, API-key, bearer, session cookie, logout, UTF-8 and ISO-8859-1 credentials, noauth exceptions, and password-change invalidation. `api_auth_test.go` covers static auth and percent-s formatting.
<!-- END_FILE_RESEARCH: sources/sync-backup/syncthing/lib/api/api_auth.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/syncthing/lib/api/api_auth_test.go -->
# sources/sync-backup/syncthing/lib/api/api_auth_test.go

Purpose: Unit tests for static authentication, LDAP template formatting, token expiry/eviction, no-expiry token mode, and session cookie Max-Age behavior.

Important APIs/types/functions: Tests `authStatic`, `formatOptionalPercentS`, `tokenManager`, and `tokenCookieManager.sessionCookieMaxAge`. `mockClock` provides deterministic nanosecond ticking and controlled time jumps.

Control flow: The token manager test creates three tokens, verifies them, creates a fourth to force max-item eviction, advances the clock to test sliding expiry, and verifies expired tokens are rejected. The no-expiry test confirms expiry zero survives long clock advances.

State and persistence behavior: Uses a temporary sqlite misc DB. Token manager save scheduling is asynchronous in production, but tests inspect in-memory token maps and validation behavior.

Dependencies and integration points: Uses `internal/db/sqlite`, misc DB, and config GUI password hashing.

Risks: Tests do not wait for scheduled DB persistence, so they primarily verify in-memory semantics. LDAP network flows are not exercised here.

Test signals: Strong unit signal for static auth, template interpolation edge cases with escaped `%%s`, active-token limit eviction, sliding token lifetime, no-expiry sessions, and negative session-cookie duration.
<!-- END_FILE_RESEARCH: sources/sync-backup/syncthing/lib/api/api_auth_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/syncthing/lib/api/api_csrf.go -->
# sources/sync-backup/syncthing/lib/api/api_csrf.go

Purpose: CSRF protection middleware for REST endpoints and shared API-key header validation.

Important APIs/types/functions: `csrfManager` stores unique cookie/header suffix, protected path prefix, API-key validator, next handler, and token manager. `newCsrfManager` creates a token manager under key `csrfTokens`. `ServeHTTP` enforces token policy. `hasValidAPIKeyHeader` accepts either `X-API-Key` or `Authorization: Bearer`.

Control flow: Valid API keys bypass CSRF and add `Access-Control-Allow-Origin: *`. `/rest/debug` bypasses CSRF. Non-protected paths issue a `CSRF-Token-<unique>` cookie if missing/invalid, then pass through. Protected noauth paths bypass CSRF. All other protected paths require an `X-CSRF-Token-<unique>` header matching a stored token.

State and persistence behavior: CSRF tokens are bounded to 25 active items, expire after one hour, and are persisted by `tokenManager` in misc DB.

Dependencies and integration points: Used by `api.go` before auth wrapping. Depends on GUI config implementing `IsValidAPIKey` and on token persistence in `tokenmanager.go`.

Risks: Debug endpoint bypass is acceptable only because debug routes are separately gated. API-key bypass means API keys are full CSRF bypass credentials, so they must remain secret. Token cookies lack explicit SameSite/Secure attributes here.

Test signals: `TestCSRFRequired` verifies cookie issuance, protected failure without token, success with token, bad API-key failure, and valid API-key/bearer bypass success.
<!-- END_FILE_RESEARCH: sources/sync-backup/syncthing/lib/api/api_csrf.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/syncthing/lib/api/api_statics.go -->
# sources/sync-backup/syncthing/lib/api/api_statics.go

Purpose: Static GUI asset server with theme support and development override directory support.

Important APIs/types/functions: `staticsServer` stores asset override directory, compiled asset map, available themes, current theme, and last theme-change time. `newStaticsServer`, `ServeHTTP`, `serveAsset`, `serveFromAssetDir`, `serveFromAssets`, `serveThemes`, `setTheme`, and `String` implement serving and theme changes.

Control flow: Requests to `/themes.json` return theme names. Other paths normalize `/` to `index.html`, resolve the current theme, honor `theme-assets/<theme>/<file>` explicit theme paths, then try override current theme, compiled current theme, override default theme, compiled default theme, and finally 404. `setTheme` updates theme and modification timestamp under lock.

State and persistence behavior: Current theme and last-change time are in-memory. Override files are read from disk through `http.ServeFile`; compiled assets are served from memory.

Dependencies and integration points: Uses `lib/api/auto.Assets`, `lib/assets.Serve`, and config default theme. `api.go` mounts this at `/`, and `CommitConfiguration` updates the theme.

Risks: Asset override directory can shadow compiled GUI assets and must be trusted. Cache is disabled at the static server level, while asset ETags still exist lower down. Available themes are collected once at server creation and do not update if directories appear later.

Test signals: `TestAssetsDir` verifies override precedence. `TestDirNames` verifies sorted directory listing used for theme discovery.
<!-- END_FILE_RESEARCH: sources/sync-backup/syncthing/lib/api/api_statics.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/syncthing/lib/api/api_test.go -->
# sources/sync-backup/syncthing/lib/api/api_test.go

Purpose: Broad integration and unit test coverage for the API service, static assets, authentication, CSRF, headers, event subscriptions, browsing, certificate policy, config modifications, and hostname sanitization.

Important APIs/types/functions: Defines shared test config, `startHTTP`, request helpers, session-cookie helpers, `httpTestCase`, and many `Test...` functions. It uses mocks for model, events, discovery, connections, and folder summaries.

Control flow: `startHTTP` constructs a `service`, starts it under suture, waits for a random localhost listener address, and returns a base URL. Endpoint tests send real HTTP requests with API keys or auth cookies. Config tests use a live config wrapper and verify PUT/PATCH/DELETE behavior through REST routes.

State and persistence behavior: Tests use temporary sqlite misc DBs, temp config files, testdata config base directory, and temporary fake filesystems. Cleanup cancels supervisors and closes DBs.

Dependencies and integration points: Exercises `api.go`, `api_auth.go`, `api_csrf.go`, `api_statics.go`, `confighandler.go`, `tokenmanager.go`, `assets`, config wrappers, and mocks generated in other packages.

Risks: Because many tests run in parallel and use actual listeners, timeouts and port/listener behavior can be environment-sensitive. Several tests rely on noauth paths returning 200 even when unauthenticated, which encodes middleware order.

Test signals: Very strong signal for public REST compatibility: expected status codes/content types, auth success/failure, cookie lifecycle, CSRF, host checking including IPv6/container skip, CORS/OPTIONS, event mask parsing, browse sorting and prefix matching, certificate regeneration, config changes, and sanitized hostnames.
<!-- END_FILE_RESEARCH: sources/sync-backup/syncthing/lib/api/api_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/syncthing/lib/api/auto/auto_test.go -->
# sources/sync-backup/syncthing/lib/api/auto/auto_test.go

Purpose: Verifies that the compiled GUI asset bundle exposes a gzipped default `index.html` containing HTML.

Important APIs/types/functions: `TestAssets` calls `auto.Assets`, checks `default/index.html`, verifies `Gzipped`, decompresses content, and checks for `<html`.

Control flow: Straight-line asset lookup and gzip read.

State and persistence behavior: No persistence; reads compiled asset map in memory.

Dependencies and integration points: Tests the generated asset package used by `api_statics.go`.

Risks: Under the `noassets` build tag, the fallback asset must still satisfy this test. The test only checks minimal presence, not full GUI asset completeness.

Test signals: Build-time guard that an asset bundle exists and is gzip-compatible.
<!-- END_FILE_RESEARCH: sources/sync-backup/syncthing/lib/api/auto/auto_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/syncthing/lib/api/auto/doc.go -->
# sources/sync-backup/syncthing/lib/api/auto/doc.go

Purpose: Package documentation and generation directive for compiled web assets.

Important APIs/types/functions: Contains `go:generate go run ../../../script/genassets.go -o gui.files.go ../../../gui` and declares package `auto`.

Control flow: No runtime control flow.

State and persistence behavior: No runtime state. Generation creates source files from the GUI asset tree.

Dependencies and integration points: Generated `gui.files.go` supplies `Assets()` consumed by `api_statics.go` and tested by `auto_test.go`.

Risks: If the generation command or GUI path changes, the compiled asset bundle can become stale or missing.

Test signals: `auto_test.go` verifies the generated or fallback bundle at runtime.
<!-- END_FILE_RESEARCH: sources/sync-backup/syncthing/lib/api/auto/doc.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/syncthing/lib/api/auto/noassets.go -->
# sources/sync-backup/syncthing/lib/api/auto/noassets.go

Purpose: Minimal fallback implementation of `auto.Assets` when built with the `noassets` tag.

Important APIs/types/functions: `Assets() map[string]assets.Asset` returns only `default/index.html` with gzipped `<html></html>` content.

Control flow: Builds a gzip buffer, flushes it, and returns a map literal.

State and persistence behavior: Stateless, in-memory asset generation on each call.

Dependencies and integration points: Satisfies the same API as generated GUI assets so API/static tests and minimal builds can run without embedding the full GUI.

Risks: The returned `Asset` does not set `Length`, `Filename`, or `Modified`, so full production serving semantics are reduced under `noassets`. It is intentionally not a complete GUI.

Test signals: `auto_test.go` passes against this fallback because it only requires gzipped default index HTML.
<!-- END_FILE_RESEARCH: sources/sync-backup/syncthing/lib/api/auto/noassets.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/syncthing/lib/api/confighandler.go -->
# sources/sync-backup/syncthing/lib/api/confighandler.go

Purpose: Registers and implements REST endpoints for reading and modifying Syncthing configuration.

Important APIs/types/functions: `configMuxBuilder` embeds an `httprouter.Router` and holds device ID plus config wrapper. Register methods cover whole config, deprecated config path, restart status, folders/devices collections and items, defaults, ignores, options, LDAP, and GUI. Adjustment helpers include `adjustConfig`, `adjustFolder`, `adjustDevice`, `adjustOptions`, `adjustGUI`, `postAdjustGui`, `adjustLDAP`, `unmarshalTo`, `unmarshalToRawMessages`, and `finish`.

Control flow: GET handlers return raw config or subsections. PUT collection handlers replace folder/device lists after applying defaults to each raw message. POST collection and PUT item handlers create/replace from defaults; PATCH item handlers merge into existing values. DELETE removes folders/devices. Whole-config and GUI updates call `postAdjustGui` to hash changed cleartext passwords before committing. `finish` waits on the config waiter then saves the config.

State and persistence behavior: Mutates the live config wrapper through `cfg.Modify`, waits for config application, and persists with `cfg.Save`. Password changes are transformed into hashed config values before saving.

Dependencies and integration points: Integrated into the `api.go` router. Depends on config wrapper semantics, `structutil.SetDefaults`, protocol device ID parsing, and JSON decoding.

Risks: `finish` does not explicitly return after save failure, so handlers may have partially written status behavior depending on prior writes. Whole-config modification captures errors inside the modify closure through outer variables. Body reads are unbounded except where callers wrap them. Password hashing depends on detecting a string difference from the existing hashed value.

Test signals: `TestConfigPostOK`, `TestConfigPostDupFolder`, `TestConfigChanges`, and password-change tests in `api_test.go` exercise create, patch, delete, whole-config updates, and GUI password hashing.
<!-- END_FILE_RESEARCH: sources/sync-backup/syncthing/lib/api/confighandler.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/syncthing/lib/api/debug.go -->
# sources/sync-backup/syncthing/lib/api/debug.go

Purpose: API package debug logger registration and HTTP debug-level predicate.

Important APIs/types/functions: Package variable `l` is a `slogutil` adapter registered as "REST API". `shouldDebugHTTP` returns whether package `api` is set to debug level.

Control flow: `shouldDebugHTTP` delegates to `l.ShouldDebug("api")`.

State and persistence behavior: Registers API package metadata in global slogutil state. No persistence.

Dependencies and integration points: Used by `debugMiddleware` and server error-log configuration in `api.go`, plus debug logs in auth/CSRF/statics/config code.

Risks: The explicit `"api"` facility string must match `funcNameToPkg` package derivation. If package names change, debug toggles could stop matching.

Test signals: API log-level endpoint and debug behavior are indirectly covered by API tests.
<!-- END_FILE_RESEARCH: sources/sync-backup/syncthing/lib/api/debug.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/syncthing/lib/api/mocked_config_test.go -->
# sources/sync-backup/syncthing/lib/api/mocked_config_test.go

Purpose: Test helper for constructing config wrapper mocks with successful default mutation behavior.

Important APIs/types/functions: `newMockedConfig` returns `*mocks.Wrapper` with `Modify`, `RemoveFolder`, and `RemoveDevice` preconfigured to return `noopWaiter` and nil errors. `noopWaiter.Wait` is a no-op.

Control flow: Straight-line mock setup.

State and persistence behavior: No real persistence; tests that require save behavior use real config wrappers elsewhere.

Dependencies and integration points: Used heavily by `api_test.go` to start API services without a real config file.

Risks: Because it defaults modifications to success without mutating state, tests using it can miss real config state transitions unless they assert through explicit mock returns.

Test signals: Supports API service tests by removing config persistence as a variable.
<!-- END_FILE_RESEARCH: sources/sync-backup/syncthing/lib/api/mocked_config_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/syncthing/lib/api/support_bundle.go -->
# sources/sync-backup/syncthing/lib/api/support_bundle.go

Purpose: Support-bundle helpers for redacting config and writing zip archives.

Important APIs/types/functions: `getRedactedConfig` copies the service config and replaces GUI API key, password, user, and folder-device encryption passwords with `REDACTED`. `writeZip` writes `fileEntry` values to an archive.

Control flow: Redaction walks folders and embedded devices in the copied config. Zip writing creates each entry and writes its byte data, returning the first create/write error.

State and persistence behavior: `getRedactedConfig` works on a copy and does not mutate live config. `writeZip` writes to an arbitrary writer; `api.go` uses it for in-memory and backup support zips.

Dependencies and integration points: Called by `getSupportBundle` in `api.go`. Depends on config structures and the local `fileEntry` type.

Risks: Redaction covers known sensitive fields in this config shape; new secret fields require updating this helper. `writeZip` defers `Close` and also calls `Close` explicitly, which can lead to a second close on return but the explicit close result is what is returned.

Test signals: No direct tests in this subset. Support bundle endpoint tests should verify redaction and zip contents.
<!-- END_FILE_RESEARCH: sources/sync-backup/syncthing/lib/api/support_bundle.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/syncthing/lib/api/testdata/config/config.xml -->
# sources/sync-backup/syncthing/lib/api/testdata/config/config.xml

Purpose: Test fixture configuration used as API test config base directory.

Important data: Defines configuration version 28 with two folders, multiple devices, GUI settings, LDAP placeholder, and options. It includes localhost device addresses, GUI address `127.0.0.1:8081`, user/password/API key values for tests, disabled global announce, enabled local announce, and a folder ID containing non-ASCII characters to exercise encoding paths.

Control flow: Not executable. It is loaded by config code during tests after `TestMain` points `locations.ConfigBaseDir` at `testdata/config`.

State and persistence behavior: Static fixture on disk. Tests may read it as initial config input but should avoid mutating the source fixture.

Dependencies and integration points: Used by `api_test.go` through Syncthing locations/config loading. The GUI API key and bcrypt password support auth-related test scenarios.

Risks: Fixture drift can change API test assumptions. Embedded credentials are test-only but still should not be copied into production examples. Non-ASCII content is intentional and should be preserved.

Test signals: Supports endpoint tests requiring realistic folders, devices, GUI config, and options.
<!-- END_FILE_RESEARCH: sources/sync-backup/syncthing/lib/api/testdata/config/config.xml -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/syncthing/lib/api/tokenmanager.go -->
# sources/sync-backup/syncthing/lib/api/tokenmanager.go

Purpose: Bounded persistent token storage and cookie session management for API auth and CSRF.

Important APIs/types/functions: `tokenManager` stores tokens in an `apiproto.TokenSet`, backed by misc DB. Methods are `Check`, `New`, `newExpiryNanos`, `Delete`, `saveLocked`, and `scheduledSave`. `tokenCookieManager` wraps session cookie naming, creation, validation, deletion, and `sessionCookieMaxAge`.

Control flow: `newTokenManager` best-effort loads a token set from DB. `Check` validates presence and expiry, refreshes sliding expiry, and schedules save. `New` creates a random token and schedules save. `saveLocked` removes expired tokens, enforces max count by oldest expiry, and debounce-schedules DB persistence one second after inactivity. Cookie creation detects HTTPS directly or through reverse-proxy headers and sets Secure when connection or GUI TLS warrants it.

State and persistence behavior: Token state is held in memory and persisted to misc DB keys such as `sessions` and `csrfTokens` through delayed protobuf marshaling. Session cookies are browser-side state with configurable path, persistence, max age, and secure flag.

Dependencies and integration points: Used by auth middleware and CSRF manager. Depends on misc DB, generated `apiproto.TokenSet`, protobuf marshaling, config GUI settings, event logging, and random token generation.

Risks: Persistence is best effort and delayed; crashes can lose very recent token changes. Sorting eviction by expiry treats no-expiry tokens as oldest (`0`) and can evict them first when over limit. Cookie deletion uses the path from the incoming cookie; historical multiple-path cookies are handled by iterating all same-name cookies.

Test signals: `api_auth_test.go` covers token validity, max item eviction, sliding expiry, no-expiry behavior, and negative session-cookie duration. `api_test.go` covers login/logout cookie lifecycle.
<!-- END_FILE_RESEARCH: sources/sync-backup/syncthing/lib/api/tokenmanager.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/syncthing/lib/assets/assets.go -->
# sources/sync-backup/syncthing/lib/assets/assets.go

Purpose: Utilities for serving embedded static assets over HTTP with MIME, caching, and gzip handling.

Important APIs/types/functions: `Asset` describes embedded content, compression, decompressed length, original filename, and modified time. `Serve` writes an asset with content type, ETag, Last-Modified, conditional GET support, and gzip negotiation. `MimeTypeForFile` maps common GUI extensions to stable MIME types and falls back to `mime.TypeByExtension`.

Control flow: `Serve` sets headers, checks `If-Modified-Since` and `If-None-Match`, returns 304 if matched, writes plain content directly, writes gzipped content when accepted, or decompresses gzipped content on the fly otherwise.

State and persistence behavior: Stateless. Content comes from memory; no file I/O.

Dependencies and integration points: Used by `api_statics.go` for compiled GUI assets and by generated `auto` asset bundles.

Risks: For gzipped assets, `gzip.NewReader` errors are ignored, assuming generated assets are valid. ETag is based only on modified unix seconds, so different content with the same timestamp collides. `Accept-Encoding` matching is substring-based.

Test signals: `assets_test.go` verifies gzip/plain serving, content length, MIME type, quoted ETag, and 304 behavior.
<!-- END_FILE_RESEARCH: sources/sync-backup/syncthing/lib/assets/assets.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/syncthing/lib/assets/assets_test.go -->
# sources/sync-backup/syncthing/lib/assets/assets_test.go

Purpose: Unit tests for embedded asset serving behavior.

Important APIs/types/functions: Helpers `compress` and `decompress` create and inspect gzip content. `TestServe` and `TestServeGzip` call `testServe` for plain and gzipped asset paths.

Control flow: The test handler serves a synthetic `index.html`. It requests with and without gzip support, validates OK status, content type, quoted ETag, content length matching actual encoded body length, decoded body content, and conditional 304 responses for ETag and Last-Modified.

State and persistence behavior: In-memory only, using `httptest`.

Dependencies and integration points: Directly validates `assets.Serve` and indirectly protects `api_statics.go` serving behavior.

Risks: Tests use a simple HTML asset and do not cover every MIME type, malformed gzip, or fallback `mime.TypeByExtension`.

Test signals: Strong signal for HTTP caching and gzip negotiation correctness.
<!-- END_FILE_RESEARCH: sources/sync-backup/syncthing/lib/assets/assets_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/syncthing/lib/beacon/beacon.go -->
# sources/sync-backup/syncthing/lib/beacon/beacon.go

Purpose: Shared supervisor-backed abstraction for UDP broadcast and multicast discovery beacons.

Important APIs/types/functions: `recv` pairs payload bytes with source address. `Interface` combines `suture.Service`, `fmt.Stringer`, `Send`, `Recv`, and `Error`. `cast` embeds a suture supervisor and owns reader/writer services plus inbox/outbox channels. `newCast`, `addReader`, `addWriter`, `createService`, `String`, `Send`, `Recv`, and `Error` implement common behavior.

Control flow: `newCast` creates a supervisor with debug logging and slow restart backoff, initializes channels, and closes `stopped` when the supervisor finishes. `Send` writes to the inbox unless stopped. `Recv` reads one message from the outbox or returns nils when stopped. `Error` reports reader error first, then writer error.

State and persistence behavior: In-memory channels and service error state only. No persistence.

Dependencies and integration points: Used by `NewBroadcast` and `NewMulticast`. Integrates with suture supervision and `svcutil.ServiceWithError`.

Risks: `Send` can block if the writer service is not draining inbox. `Recv` returns nil data/address on stop, so callers must handle that sentinel. Reader/writer errors depend on service wrapper semantics.

Test signals: Broadcast address calculation is tested in `broadcast_test.go`; cast orchestration is not directly tested here.
<!-- END_FILE_RESEARCH: sources/sync-backup/syncthing/lib/beacon/beacon.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/syncthing/lib/beacon/broadcast.go -->
# sources/sync-backup/syncthing/lib/beacon/broadcast.go

Purpose: IPv4 UDP broadcast beacon implementation for local discovery.

Important APIs/types/functions: `NewBroadcast(port int)` creates a `cast` with broadcast reader and writer. `writeBroadcasts` sends inbound payloads to interface-specific broadcast addresses or global `255.255.255.255`. `readBroadcasts` listens on a UDP4 port and forwards received payloads. `bcast` computes the broadcast IP for an `IPNet`.

Control flow: Writer opens an ephemeral UDP4 socket, closes it on context cancellation, reads payloads from inbox, enumerates running broadcast-capable interfaces, skips Android point-to-point cellular interfaces, computes destinations from global-unicast IPv4 addresses, writes with one-second deadlines, and returns an error if no writes succeed. Reader binds the port, reads into a 64 KiB buffer, copies each datagram, and non-blockingly sends to outbox, dropping when full.

State and persistence behavior: Network sockets and transient datagrams only. No persistence.

Dependencies and integration points: Uses `netutil.Interfaces`, `netutil.InterfaceAddrsByInterface`, build flags for Android behavior, slogutil logging, and the common cast interface. Used by local discovery.

Risks: Broadcast availability varies by OS/interface/firewall. Writer returns the last error when all sends fail, which may be nil in some no-destination paths after fallback. Dropping messages when outbox is full is intentional but can lose discovery packets.

Test signals: `broadcast_test.go` validates `bcast` for multiple CIDR masks. Network send/read behavior is not directly exercised.
<!-- END_FILE_RESEARCH: sources/sync-backup/syncthing/lib/beacon/broadcast.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/syncthing/lib/beacon/broadcast_test.go -->
# sources/sync-backup/syncthing/lib/beacon/broadcast_test.go

Purpose: Unit test for IPv4 broadcast address calculation.

Important APIs/types/functions: `addrToBcast` lists CIDR inputs and expected broadcast CIDRs. `TestBroadcastAddr` parses each CIDR, calls `bcast`, and compares string output.

Control flow: Table-driven straight-line test.

State and persistence behavior: No state or persistence.

Dependencies and integration points: Protects the address computation used by `writeBroadcasts`.

Risks: Does not test interface enumeration, UDP socket writes, or Android-specific filtering.

Test signals: Good signal for netmask arithmetic across /0, /22, /24, /25, and /32 cases.
<!-- END_FILE_RESEARCH: sources/sync-backup/syncthing/lib/beacon/broadcast_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/syncthing/lib/beacon/debug.go -->
# sources/sync-backup/syncthing/lib/beacon/debug.go

Purpose: Package-level debug logger registration for beacon discovery.

Important APIs/types/functions: Variable `l` is a `slogutil.NewAdapter` registered as "Multicast and broadcast discovery".

Control flow: No functions; initialization occurs at package load.

State and persistence behavior: Registers beacon package description in global slogutil state. No persistence.

Dependencies and integration points: Used by broadcast and multicast implementations for debug logging and package-level log control.

Risks: Global logger side effects occur on import. The description controls API log-level visibility.

Test signals: Indirectly visible through log-level package descriptions.
<!-- END_FILE_RESEARCH: sources/sync-backup/syncthing/lib/beacon/debug.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/syncthing/lib/beacon/doc.go -->
# sources/sync-backup/syncthing/lib/beacon/doc.go

Purpose: Package documentation for UDP broadcast beacon functionality.

Important APIs/types/functions: Declares package `beacon` and documents it as implementing a UDP broadcast beacon.

Control flow: None.

State and persistence behavior: None.

Dependencies and integration points: Documentation-only file for the beacon package.

Risks: The package now includes multicast as well as broadcast, so the short package comment is narrower than the implementation.

Test signals: No tests.
<!-- END_FILE_RESEARCH: sources/sync-backup/syncthing/lib/beacon/doc.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/syncthing/lib/beacon/multicast.go -->
# sources/sync-backup/syncthing/lib/beacon/multicast.go

Purpose: IPv6 multicast beacon implementation for local discovery.

Important APIs/types/functions: `NewMulticast(addr string)` creates a `cast` with multicast reader and writer. `writeMulticasts` sends payloads to an IPv6 multicast group on each eligible interface with hop limit 1. `readMulticasts` joins the multicast group on eligible interfaces and forwards received datagrams.

Control flow: Writer resolves the UDP6 multicast address, opens a packet connection, sets an IPv6 control message with hop limit 1 and per-interface index, enumerates running multicast-capable interfaces, skips Android point-to-point cellular interfaces, writes to each interface with one-second deadlines, and returns if no sends succeed. Reader resolves and listens on the group address, joins the group on each eligible interface, errors if none joined, then reads datagrams, copies them, and non-blockingly sends to outbox.

State and persistence behavior: Network socket state only. No persistence.

Dependencies and integration points: Depends on `golang.org/x/net/ipv6`, `netutil`, build flags, slog logging, and the common `cast` abstraction. Used by local discovery for IPv6 LAN advertisements.

Risks: IPv6 multicast behavior is platform and interface dependent. `joined` increments even when `JoinGroup` fails, so a system with eligible interfaces but failed joins may proceed and then never receive packets. Outbox full conditions drop messages.

Test signals: No direct tests in this subset. Multicast network behavior is likely covered only by integration/manual testing.
<!-- END_FILE_RESEARCH: sources/sync-backup/syncthing/lib/beacon/multicast.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/syncthing/lib/config/authmode.go -->
# sources/sync-backup/syncthing/lib/config/authmode.go

Purpose: Text-marshaled enum for GUI authentication mode.

Important APIs/types/functions: `AuthMode` has `AuthModeStatic` and `AuthModeLDAP`. `String`, `MarshalText`, and `UnmarshalText` convert between enum values and `static`/`ldap`.

Control flow: `UnmarshalText` defaults unknown values to static and returns nil.

State and persistence behavior: Used in config XML/JSON text representation. Defaulting unknown values to static preserves a conservative local-auth fallback.

Dependencies and integration points: Consumed by API auth logic, specifically `auth` in `api_auth.go`, and by config serialization.

Risks: Unknown config values silently become static, which may hide typos. Adding new modes requires updating string conversion and auth dispatch.

Test signals: No direct test in this subset. Auth tests exercise the static path.
<!-- END_FILE_RESEARCH: sources/sync-backup/syncthing/lib/config/authmode.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/syncthing/lib/config/blockpullorder.go -->
# sources/sync-backup/syncthing/lib/config/blockpullorder.go

Purpose: Text-marshaled enum for file block pull order.

Important APIs/types/functions: `BlockPullOrder` has `BlockPullOrderStandard`, `BlockPullOrderRandom`, and `BlockPullOrderInOrder`. `String`, `MarshalText`, and `UnmarshalText` convert to/from `standard`, `random`, and `inOrder`.

Control flow: Unknown text values default to standard and return nil.

State and persistence behavior: Used in folder config serialization. The fixture config uses `random`, showing persisted XML integration.

Dependencies and integration points: Consumed by folder pulling/config code outside this subset and by config REST handlers that marshal/unmarshal folder options.

Risks: Silent fallback to standard can mask invalid config. String values are user-visible config compatibility contracts.

Test signals: No direct test in this subset; config API tests indirectly round-trip folder configuration.
<!-- END_FILE_RESEARCH: sources/sync-backup/syncthing/lib/config/blockpullorder.go -->
