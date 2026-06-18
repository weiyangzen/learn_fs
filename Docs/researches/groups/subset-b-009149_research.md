# subset-b-009149 research

Grouped research report for Kopia repository client, hashing, configuration, logging, maintenance, maintenance stats, manifest, and object manager files. Each section preserves the exact source path and is wrapped for reconciliation into source-tree-aligned per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/repo/grpc_repository_client.go -->
# sources/sync-backup/kopia/repo/grpc_repository_client.go

Purpose: implements Kopia's remote `Repository` client over the bidirectional gRPC API exposed by `kopia server`. It adapts the local repository interfaces for manifests, contents, objects, retention, notifications, flushes, and write sessions onto `apipb.SessionRequest` and `SessionResponse` messages.

Important APIs/types/functions: `grpcRepositoryClient`, `grpcInnerSession`, `MaxGRPCMessageSize`, `openGRPCAPIRepository`, `newGRPCAPIRepositoryForConnection`, `getOrEstablishInnerSession`, `sendRequest`, `readLoop`, `maybeRetry`, `WriteContent`, `GetContent`, manifest methods, `ContentInfo`, `Flush`, and `baseURLToURI`. `grpcCreds` injects Kopia auth/build metadata as per-RPC credentials.

Control flow: a repository client lazily establishes a streaming session, sends an initialize request, starts `readLoop`, then multiplexes logical requests by request ID through per-request response channels. High-level repository methods choose retryable or non-retryable session access, send one request, interpret the expected response variant, and convert remote error responses into local sentinel errors.

State/persistence behavior: durable state remains server-side; the client stores session state, active request channels, async write verification goroutines, a content cache, recent prefixed reads, object manager state, server parameters, and flush callbacks. `WriteContent` computes the expected content ID locally, sends cloned bytes asynchronously, and `Flush` waits for all asynchronous verification before invoking callbacks and issuing remote flush.

Dependencies/integration: integrates gRPC, TLS/fingerprint trust, OpenTelemetry trace propagation, retry backoff, Kopia content/object/manifest APIs, hashing parameters returned by the server, content cache, compression headers, and remote notification/retention APIs. It supports `https`, `kopia`, and `unix+https` server addresses.

Risks/test signals: the main risks are request-channel leaks, stream break races, losing async write errors until flush, retrying unsafe write operations, local/server hash mismatch, and URL/TLS credential misconfiguration. Tests cover message-size headroom and URL-to-gRPC-target conversion; broader behavior depends on integration coverage around server sessions.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/repo/grpc_repository_client.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/repo/grpc_repository_client_test.go -->
# sources/sync-backup/kopia/repo/grpc_repository_client_test.go

Purpose: verifies that the exported gRPC message-size limit is large enough for the largest possible splitter segment plus protocol overhead.

Important APIs/types/functions: `TestMaxGRPCMessageSize`, `repo.MaxGRPCMessageSize`, `splitter.SupportedAlgorithms`, and each splitter factory's `MaxSegmentSize`.

Control flow: iterate all supported splitters, record the maximum segment size, and fail if it exceeds `MaxGRPCMessageSize - maxGRPCMessageOverhead`.

State/persistence behavior: no repository state is created. The test protects a cross-package constant contract between object splitting and gRPC transport sizing.

Dependencies/integration: integrates the public `repo` package with the splitter registry, so newly registered splitters automatically participate.

Risks/test signals: catches oversized future splitters before they can produce contents that cannot be sent over the remote API. It does not measure real protobuf overhead or streaming behavior.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/repo/grpc_repository_client_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/repo/grpc_repository_client_unit_test.go -->
# sources/sync-backup/kopia/repo/grpc_repository_client_unit_test.go

Purpose: unit tests `baseURLToURI`, the helper that translates configured Kopia server URLs into gRPC dial targets.

Important APIs/types/functions: `TestBaseURLToURI`, `baseURLToURI`, and `require.ErrorContains`/`require.Equal`.

Control flow: table cases cover IPv4, IPv6, Unix socket HTTPS, `kopia://`, invalid Unix HTTP, and malformed addresses. Valid cases assert the exact dial target; invalid cases assert the expected error fragment.

State/persistence behavior: no persistent state; it validates parsing and scheme policy.

Dependencies/integration: protects integration between local config `APIServerInfo.BaseURL` and `grpc.NewClient` target syntax, including Unix socket support.

Risks/test signals: catches regressions in accepted schemes or host/port formatting. It does not validate TLS behavior or actual dialing.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/repo/grpc_repository_client_unit_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/repo/hashing/blake3_hashes.go -->
# sources/sync-backup/kopia/repo/hashing/blake3_hashes.go

Purpose: registers Kopia's BLAKE3 keyed hashing algorithms with full 256-bit and truncated 128-bit output lengths.

Important APIs/types/functions: `newBlake3`, `blake3KeySize`, and the package `init` registrations for `BLAKE3-256` and `BLAKE3-256-128`.

Control flow: `newBlake3` derives a 32-byte BLAKE3 key when the supplied repository secret is shorter, then creates a keyed BLAKE3 hash. Registration wraps that constructor with `truncatedKeyedHashFuncFactory`.

State/persistence behavior: the algorithm name and output length become part of repository format parameters. The derived-key context string is a compatibility-sensitive constant.

Dependencies/integration: depends on `github.com/zeebo/blake3` and the shared hashing registry in `hashing.go`.

Risks/test signals: key handling must remain deterministic across releases or repositories become unreadable. Generic hashing tests exercise output stability and data separation across all registered algorithms.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/repo/hashing/blake3_hashes.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/repo/hashing/blake_hashes.go -->
# sources/sync-backup/kopia/repo/hashing/blake_hashes.go

Purpose: registers keyed BLAKE2S and BLAKE2B hash variants used by repository content IDs.

Important APIs/types/functions: package `init`, `truncatedKeyedHashFuncFactory`, `blake2s.New128`, `blake2s.New256`, and `blake2b.New256`.

Control flow: initialization registers four algorithm names: `BLAKE2S-128`, `BLAKE2S-256`, `BLAKE2B-256-128`, and `BLAKE2B-256`, each with the intended truncation length.

State/persistence behavior: algorithm names are stored in repository content format; the default elsewhere is `BLAKE2B-256-128`.

Dependencies/integration: depends on `golang.org/x/crypto/blake2b` and `blake2s`, plus the registry in `hashing.go`.

Risks/test signals: registration order is not externally meaningful because supported algorithms are sorted. Tests cover round-trip stability and differing data outputs but not fixed golden digests.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/repo/hashing/blake_hashes.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/repo/hashing/hashing.go -->
# sources/sync-backup/kopia/repo/hashing/hashing.go

Purpose: provides the hashing registry and factory helpers used to produce repository content ID hash functions from repository format parameters.

Important APIs/types/functions: `Parameters`, `HashFunc`, `HashFuncFactory`, `Register`, `SupportedAlgorithms`, `DefaultAlgorithm`, `CreateHashFunc`, `truncatedHMACHashFuncFactory`, and `truncatedKeyedHashFuncFactory`.

Control flow: algorithm-specific files register factories at init time. `CreateHashFunc` looks up the configured name, initializes the algorithm with `GetHmacSecret`, validates non-nil output, and returns a function that writes `gather.Bytes` into a pooled hash and appends truncated digest bytes to the caller-provided output slice.

State/persistence behavior: global `hashFunctions` is process-local registry state; repository persistence stores only the algorithm name and secret. `sync.Pool` reduces allocations but requires each hash to be reset before reuse.

Dependencies/integration: used by repository initialization and remote/direct content managers for content ID generation. It relies on `gather.Bytes.WriteTo` and `crypto/hmac` for HMAC algorithms.

Risks/test signals: registry mutation is global and not locked after init, so dynamic registration would need care. Incorrect truncation or secret handling would corrupt content addressing. Tests exercise every registered algorithm for deterministic output and distinction between different data.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/repo/hashing/hashing.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/repo/hashing/hashing_test.go -->
# sources/sync-backup/kopia/repo/hashing/hashing_test.go

Purpose: validates the shared hashing contract for every registered algorithm.

Important APIs/types/functions: test-local `parameters`, `TestRoundTrip`, `hashing.SupportedAlgorithms`, `hashing.CreateHashFunc`, and `gather.FromSlice`.

Control flow: random inputs and a random secret are generated, then each algorithm hashes one input twice and another input once. The test requires stable output for identical input and differing output for different input.

State/persistence behavior: no repository state; it checks in-memory factory behavior and output-slice handling.

Dependencies/integration: spans all registered hash implementation files because `SupportedAlgorithms` enumerates the registry populated by init functions.

Risks/test signals: catches nil factories, non-deterministic hashing, and failure to use input data. It does not pin golden hashes, so compatible-but-incorrect algorithm changes may pass if they stay deterministic.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/repo/hashing/hashing_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/repo/hashing/sha_hashes.go -->
# sources/sync-backup/kopia/repo/hashing/sha_hashes.go

Purpose: registers HMAC-based SHA-2 and SHA-3 hashing algorithms for content IDs.

Important APIs/types/functions: package `init`, `truncatedHMACHashFuncFactory`, `sha256.New`, `sha256.New224`, `sha3.New224`, and `sha3.New256`.

Control flow: initialization registers `HMAC-SHA256`, `HMAC-SHA256-128`, `HMAC-SHA224`, `HMAC-SHA3-224`, and `HMAC-SHA3-256` with appropriate output lengths.

State/persistence behavior: the selected HMAC algorithm and secret are part of repository content format. Hash output length affects content ID size and compatibility.

Dependencies/integration: uses standard crypto packages and the hashing registry.

Risks/test signals: HMAC secret omission or algorithm-name drift affects repository compatibility. The shared hashing test covers registration and deterministic behavior.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/repo/hashing/sha_hashes.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/repo/initialize.go -->
# sources/sync-backup/kopia/repo/initialize.go

Purpose: builds initial repository format structures and calls `format.Initialize` to create a new Kopia repository in blob storage.

Important APIs/types/functions: `NewRepositoryOptions`, `Initialize`, `formatBlobFromOptions`, `blobCfgBlobFromOptions`, `repositoryObjectFormatFromOptions`, and default helpers for ints, strings, ranges, and random bytes.

Control flow: `Initialize` normalizes nil options, creates the format blob, blob retention configuration, and repository config, validates/adjusts format-version-dependent fields, then delegates to the format package with the password. Repository config defaults include hashing, encryption, ECC, pack/index version, splitter, HMAC secret, and master key.

State/persistence behavior: writes initial repository metadata to the supplied blob storage. It generates unique IDs, HMAC secrets, and master keys when not provided; disabling HMAC clears the secret. Format version 1 or zero ECC overhead disables ECC fields.

Dependencies/integration: integrates blob storage, content defaults, format version resolution, encryption, ECC, hashing, and splitter defaults.

Risks/test signals: random generation errors are ignored in helpers, so entropy-source failures would silently produce zeroed bytes. Format compatibility depends on default constants and `ResolveFormatVersion`. Tests for these defaults are indirect through repository integration suites.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/repo/initialize.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/repo/jsonencoding/jsonencoding.go -->
# sources/sync-backup/kopia/repo/jsonencoding/jsonencoding.go

Purpose: provides `jsonencoding.Duration`, a wrapper around `time.Duration` with text/JSON marshal and unmarshal behavior suitable for config files.

Important APIs/types/functions: `Duration`, `MarshalText`, and `UnmarshalText`.

Control flow: marshaling emits the duration's standard string form. Unmarshaling trims whitespace, first attempts `strconv.ParseFloat` and treats numeric values as raw nanoseconds, then falls back to `time.ParseDuration`.

State/persistence behavior: affects serialized configuration and manifest-like JSON that embeds durations. Numeric strings preserve legacy nanosecond-style duration encodings.

Dependencies/integration: used by JSON encoding via `encoding.TextMarshaler`/`TextUnmarshaler` semantics.

Risks/test signals: accepting floats can truncate fractional nanoseconds through `time.Duration(f)`. Error wrapping includes the invalid input. Tests cover string durations, whitespace, underscore numeric literals accepted by `ParseFloat`, and invalid input.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/repo/jsonencoding/jsonencoding.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/repo/jsonencoding/jsonencoding_test.go -->
# sources/sync-backup/kopia/repo/jsonencoding/jsonencoding_test.go

Purpose: tests JSON marshaling and unmarshaling behavior for `jsonencoding.Duration`.

Important APIs/types/functions: `MyStruct`, `TestDurationJSONMarshaling`, `TestDurationJSONUnmarshaling`, and `TestDurationJSONUnmarshalingError`.

Control flow: one test marshals a 20m10s duration and asserts JSON text. The table-driven unmarshal test parses duration strings, whitespace-padded values, and numeric nanoseconds. The error test verifies invalid strings report "invalid duration".

State/persistence behavior: no external state; it protects config compatibility for duration fields.

Dependencies/integration: uses `encoding/json`, `time`, and `testify/require`.

Risks/test signals: catches regressions in numeric legacy parsing and error propagation. It does not test fractional numeric strings or direct non-JSON text calls.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/repo/jsonencoding/jsonencoding_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/repo/local_config.go -->
# sources/sync-backup/kopia/repo/local_config.go

Purpose: defines and persists local client configuration for connecting to either a remote API server or direct blob storage.

Important APIs/types/functions: `ClientOptions`, `ApplyDefaults`, `Override`, `UsernameAtHost`, `LocalConfig`, `writeToFile`, `LoadConfigFromFile`, and `ErrCannotWriteToRepoConnectionWithPermissiveCacheLoading`.

Control flow: defaults fill hostname, username, description, and format-blob cache duration. `writeToFile` clones caching options, stores cache directory relative to the config file when possible, creates the private config directory, and writes indented JSON atomically. Loading decodes JSON, resolves relative cache paths, honors absolute `KOPIA_CACHE_DIRECTORY`, and rejects permissive cache loading unless `KOPIA_UPGRADE_LOCK_ENABLED` is set.

State/persistence behavior: local config files persist storage/API connection data, caching options, read-only and action flags, throttling, and client identity. Directory mode is `0700`; file writing uses `atomicfile`.

Dependencies/integration: integrates `blob.ConnectionInfo`, `content.CachingOptions`, throttling limits, OS path helpers, and environment-variable overrides.

Risks/test signals: environment overrides can change cache location at load time; permissive cache loading is intentionally gated because it can be unsafe for write connections. Tests cover cache path round trip, nil caching, and missing-file errors.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/repo/local_config.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/repo/local_config_test.go -->
# sources/sync-backup/kopia/repo/local_config_test.go

Purpose: tests local repository config persistence and loading edge cases.

Important APIs/types/functions: `TestLocalConfig_withCaching`, `TestLocalConfig_noCaching`, `TestLocalConfig_notFound`, and `mustParseJSONFile`.

Control flow: temporary config files are written through `writeToFile`, raw JSON is inspected, and `LoadConfigFromFile` is used to verify loaded values. Missing-file behavior checks `os.ErrNotExist` wrapping.

State/persistence behavior: creates temporary config files and verifies cache directories are stored relative but loaded as absolute.

Dependencies/integration: uses `testutil.TempDirectory`, `ospath.IsAbs`, `content.CachingOptions`, JSON decoding, and `testify/require`.

Risks/test signals: protects config portability across moved config directories. It does not cover environment overrides, permissive cache loading gate, or file permissions.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/repo/local_config_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/repo/locking_storage.go -->
# sources/sync-backup/kopia/repo/locking_storage.go

Purpose: exposes the blob ID prefixes that maintenance retention extension should treat as repository-managed storage.

Important APIs/types/functions: `GetLockingStoragePrefixes`.

Control flow: returns a slice containing content pack prefixes, index blob prefix, epoch-manager prefixes, the maintenance schedule blob ID, format blob prefix, and log blob prefix.

State/persistence behavior: no state mutation; the returned prefix set defines which persisted blobs are considered for object-lock retention extension.

Dependencies/integration: depends on content, epoch, format, blob constants, and maintenance schedule/log blob naming.

Risks/test signals: missing a prefix would leave repository blobs with stale retention, while adding overly broad prefixes could extend unrelated objects. Coverage is indirect via retention extension tests.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/repo/locking_storage.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/repo/logging/broadcast.go -->
# sources/sync-backup/kopia/repo/logging/broadcast.go

Purpose: creates a logger that fans each zap log entry out to multiple underlying loggers.

Important APIs/types/functions: `Broadcast`, `Logger`, zap `Core`, and `zapcore.NewTee`.

Control flow: unwrap each sugared logger, collect its core, track a shared logger name when all inputs match or `-` when they differ, then build a new sugared logger over the tee core.

State/persistence behavior: no persistent state; it composes in-memory logging sinks.

Dependencies/integration: used by `WithAdditionalLogger` to attach secondary logging to an existing context without replacing the original logger.

Risks/test signals: passing zero loggers would create a tee with no cores. Tests verify fan-out and field formatting to two test loggers.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/repo/logging/broadcast.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/repo/logging/ctx.go -->
# sources/sync-backup/kopia/repo/logging/ctx.go

Purpose: stores module logger factories in context and caches per-module loggers.

Important APIs/types/functions: `loggerCache`, `WithLogger`, `WithAdditionalLogger`, `loggerFactoryFromContext`, and `loggerCache.getLogger`.

Control flow: `WithLogger` installs a `loggerCache`, substituting the null factory for nil. `getLogger` uses `sync.Map` and `LoadOrStore` to create one logger per module. `WithAdditionalLogger` wraps the existing context factory with `Broadcast`.

State/persistence behavior: context-local in-memory cache only; no durable state.

Dependencies/integration: consumed by `logging.Module` across repository packages and by tests that inject writer/test loggers.

Risks/test signals: context values use a package-private key, reducing collision risk. Type assertions assume only this package writes that key. Tests cover additional logger fan-out and null/default behavior.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/repo/logging/ctx.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/repo/logging/logging.go -->
# sources/sync-backup/kopia/repo/logging/logging.go

Purpose: defines the repository logging abstraction over zap and helpers for module loggers and writer-backed test/debug loggers.

Important APIs/types/functions: `Logger`, `LoggerFactory`, `Module`, and `ToWriter`.

Control flow: `Module` returns a closure that pulls the cached logger factory from context and falls back to `NullLogger`. `ToWriter` builds a zap core with Kopia's standard console encoder and debug level, returning its `.Named` function as a module factory.

State/persistence behavior: no persistence; the context selects log sinks dynamically.

Dependencies/integration: depends on zap, zapcore, and `internal/zaplogutil`. Most repository packages define module loggers using this file.

Risks/test signals: missing context silently drops logs via null logger. Tests verify writer formatting and module lookup behavior.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/repo/logging/logging.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/repo/logging/logging_test.go -->
# sources/sync-backup/kopia/repo/logging/logging_test.go

Purpose: validates logger fan-out, writer formatting, null/default logger behavior, additional logger composition, and benchmark overhead.

Important APIs/types/functions: `TestBroadcast`, `TestWriter`, `TestNullWriterModule`, `TestNonNullWriterModule`, `TestWithAdditionalLogger`, and `BenchmarkLogger`.

Control flow: tests create in-memory buffers or printf-style test loggers, emit debug/info/warn/error entries, and compare exact output order/content.

State/persistence behavior: no persistent state; tests operate on in-memory buffers and contexts.

Dependencies/integration: uses `internal/testlogging`, `logging.ToWriter`, `logging.WithLogger`, `logging.WithAdditionalLogger`, and `logging.Module`.

Risks/test signals: exact string assertions catch encoder changes. They also document that default background contexts use a no-op logger.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/repo/logging/logging_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/repo/logging/null_logger.go -->
# sources/sync-backup/kopia/repo/logging/null_logger.go

Purpose: provides the package no-op logger and factory.

Important APIs/types/functions: `NullLogger` and `getNullLogger`.

Control flow: `NullLogger` is a sugared no-op zap logger; `getNullLogger` ignores the module and returns it.

State/persistence behavior: global immutable logger instance; no persistence.

Dependencies/integration: used as the default for contexts without logging and when `WithLogger` receives nil.

Risks/test signals: because no-op logging hides output, missing context may make debugging harder. Tests in `logging_test.go` verify null module behavior.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/repo/logging/null_logger.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/repo/maintenance/blob_retain.go -->
# sources/sync-backup/kopia/repo/maintenance/blob_retain.go

Purpose: extends object-lock retention on repository blobs when the blob backend supports retention.

Important APIs/types/functions: `ExtendBlobRetentionTimeOptions`, `extendBlobRetentionTime`, `CheckExtendRetention`, `parallelBlobRetainCPUMultiplier`, and `minRetentionMaintenanceDiff`.

Control flow: the task loads blob retention config, exits with nil stats when retention is disabled, starts worker goroutines, iterates all locking-storage prefixes in parallel, sends blob metadata to workers, and calls `ExtendBlobRetention` with repository retention mode/period. It records counts and fails if any extension failed.

State/persistence behavior: mutates backend blob retention metadata, not repository content. It uses content logs and returns `ExtendBlobRetentionStats`.

Dependencies/integration: depends on `repo.GetLockingStoragePrefixes`, blob storage retention APIs, `format.BlobStorageConfiguration`, content logging, and maintenance stats.

Risks/test signals: a broad prefix set could extend unrelated blobs; worker errors are counted and converted to a task error. `CheckExtendRetention` guards against full maintenance intervals too close to retention expiry. Tests cover enabled and disabled retention behavior.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/repo/maintenance/blob_retain.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/repo/maintenance/blob_retain_test.go -->
# sources/sync-backup/kopia/repo/maintenance/blob_retain_test.go

Purpose: integration tests retention extension against repository environments with and without configured retention.

Important APIs/types/functions: `TestExtendBlobRetentionTime`, `TestExtendBlobRetentionTimeDisabled`, `maintenance.ExtendBlobRetentionTime`, fake clock, and retention-capable storage test helpers.

Control flow: tests create repositories, write one object, flush blobs, inspect retention metadata, advance time, run the extension task, and assert stats plus updated expiry. The disabled case verifies no stats and continued ability to touch blobs.

State/persistence behavior: creates temporary repository blob state and mutates retention metadata in the test storage.

Dependencies/integration: uses `repotesting`, `faketime`, `blobtesting.RetentionStorage`, `cache.Storage`, object writers, and fixed crypto test keys.

Risks/test signals: catches failure to include newly written blobs in extension scope and ensures disabled retention is a no-op. It assumes a fixed number of blobs after writing.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/repo/maintenance/blob_retain_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/repo/maintenance/cleanup_logs.go -->
# sources/sync-backup/kopia/repo/maintenance/cleanup_logs.go

Purpose: deletes old repository log blobs according to count, age, and total-size retention limits.

Important APIs/types/functions: `LogRetentionOptions`, `OrDefault`, `defaultLogRetention`, and `CleanupLogs`.

Control flow: default limits are applied when all limits are unset. `CleanupLogs` lists `_`-prefixed log blobs, sorts newest first, walks until keeping another blob would violate size, count, or age limits, then deletes the suffix unless dry-run is set.

State/persistence behavior: deletes persisted log blobs from blob storage and returns retained/to-delete/deleted counts and sizes in `CleanupLogsStats`.

Dependencies/integration: uses blob listing/deletion, `clock.Now`, content logging, and `maintenancestats.ToUint64`.

Risks/test signals: sorting by timestamp is central; incorrect ordering could delete recent logs. Dry-run preserves blobs while reporting planned deletions. Covered indirectly by maintenance schedule/report tests and stats serialization tests.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/repo/maintenance/cleanup_logs.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/repo/maintenance/content_index_to_pack_check.go -->
# sources/sync-backup/kopia/repo/maintenance/content_index_to_pack_check.go

Purpose: optionally verifies that content index entries point to readable pack blobs before and after selected maintenance tasks.

Important APIs/types/functions: `checkContentIndexToPacks`, `shouldRunContentIndexVerify`, and `reportRunAndMaybeCheckContentIndex`.

Control flow: verification walks all contents with fixed parallelism and calls `VerifyContent`. The environment variable `KOPIA_MAINTENANCE_CONTENT_VERIFY_PERCENTAGE` controls whether a random percentage gate enables the check. The wrapper runs verification before and after the task when enabled.

State/persistence behavior: verification is read-only; task reporting still persists schedule run info through `ReportRun`.

Dependencies/integration: integrates content reader verification, maintenance task reporting, random sampling, and environment configuration.

Risks/test signals: random sampling makes failures probabilistic unless percentage is 100. The verification can add substantial maintenance cost, so it is opt-in.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/repo/maintenance/content_index_to_pack_check.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/repo/maintenance/content_rewrite.go -->
# sources/sync-backup/kopia/repo/maintenance/content_rewrite.go

Purpose: rewrites selected contents into new packs to compact short packs, migrate format versions, or rewrite explicit content IDs.

Important APIs/types/functions: `RewriteContentsOptions`, `RewriteContents`, `getContentToRewrite`, `findContentInfos`, `findContentWithFormatVersion`, `findContentInShortPacks`, and `shortPackThresholdPercent`.

Control flow: `RewriteContents` starts parallel workers, consumes content candidates, skips failed candidate lookups, retains contents younger than `SafetyParameters.RewriteMinAge`, and calls `ContentManager().RewriteContent` unless dry-run. Candidate generation can combine explicit IDs, short-pack scanning, and format-version scanning.

State/persistence behavior: successful rewrites create new content/index data and flush the content manager; old packs become unreferenced for later pack GC. Stats distinguish to-rewrite, rewritten, and retained content counts/sizes.

Dependencies/integration: depends on direct repository writer, content reader/manager, blob pack info, index ranges, content logging, stats counters, and maintenance safety windows.

Risks/test signals: duplicate candidates can overcount or attempt repeated rewrites; deleted-content errors may be ignored only with `KOPIA_IGNORE_MAINTENANCE_REWRITE_ERROR`. Tests verify blob deltas and stats for dry-run, prefix-filtered, and short-pack scenarios.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/repo/maintenance/content_rewrite.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/repo/maintenance/content_rewrite_test.go -->
# sources/sync-backup/kopia/repo/maintenance/content_rewrite_test.go

Purpose: integration tests content rewrite selection, dry-run behavior, prefix filtering, and stats.

Important APIs/types/functions: `TestContentRewrite`, `RewriteContentsOptions`, `maintenance.RewriteContents`, direct write sessions, and pack blob listings.

Control flow: each case creates separate write sessions to force multiple `p` and `q` pack blobs, runs rewrite inside a direct write session, lists pack blobs before/after, and compares blob-count deltas and `RewriteContentsStats`.

State/persistence behavior: creates real temporary repository content and pack blobs; rewrite cases persist new packs while dry-run cases do not.

Dependencies/integration: uses `repotesting`, object writers with default and custom prefixes, UUID payloads, blob listing, and `SafetyNone`.

Risks/test signals: verifies no rewrite for single-pack cases and correct prefix scoping. Expected sizes are format-sensitive and could need updates if pack encoding changes.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/repo/maintenance/content_rewrite_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/repo/maintenance/drop_deleted_contents.go -->
# sources/sync-backup/kopia/repo/maintenance/drop_deleted_contents.go

Purpose: drops old deleted content entries from indexes during full maintenance.

Important APIs/types/functions: `dropDeletedContents`, `content.CompactOptions`, and `CompactIndexesStats`.

Control flow: calls `ContentManager().CompactIndexes` with `DropDeletedBefore` and `DropDeletedExtraMargin` derived from safety, then returns stats indicating the cutoff time.

State/persistence behavior: rewrites/compacts repository content indexes so deleted entries older than a safe cutoff are removed from persisted index state.

Dependencies/integration: invoked by `runTaskDropDeletedContentsFull` after `findSafeDropTime` decides that enough snapshot-GC history exists.

Risks/test signals: the safety cutoff is critical; dropping too early can make race-recovered contents unreachable. Covered by maintenance safety and timing tests around safe drop time.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/repo/maintenance/drop_deleted_contents.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/repo/maintenance/helper_test.go -->
# sources/sync-backup/kopia/repo/maintenance/helper_test.go

Purpose: exposes unexported maintenance helpers to the external `maintenance_test` package.

Important APIs/types/functions: exported test-only wrapper `ExtendBlobRetentionTime`.

Control flow: the wrapper delegates directly to `extendBlobRetentionTime`.

State/persistence behavior: same as the underlying retention task; this file itself has no state.

Dependencies/integration: lets black-box tests call retention extension without exporting it in production files.

Risks/test signals: test-only API must remain aligned with the unexported helper signature. It has no direct assertions.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/repo/maintenance/helper_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/repo/maintenance/index_compaction.go -->
# sources/sync-backup/kopia/repo/maintenance/index_compaction.go

Purpose: runs quick-maintenance index compaction when the number of small index blobs is above a threshold.

Important APIs/types/functions: `runTaskIndexCompactionQuick`, `content.CompactOptions`, and `TaskIndexCompaction`.

Control flow: wraps `ContentManager().CompactIndexes` in `reportRunAndMaybeCheckContentIndex`, passing `MinSmallBlobs: 8` and current safety `DropContentFromIndexExtraMargin`.

State/persistence behavior: compacts persisted content indexes and records task run information in the encrypted maintenance schedule.

Dependencies/integration: called from quick maintenance after rewrite/delete decisions; integrates content manager compaction with maintenance stats and optional verification.

Risks/test signals: too-low compaction thresholds could churn indexes; too-high thresholds leave many small indexes. Covered indirectly by maintenance quick-run tests.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/repo/maintenance/index_compaction.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/repo/maintenance/maintenance_params.go -->
# sources/sync-backup/kopia/repo/maintenance/maintenance_params.go

Purpose: stores repository-wide maintenance configuration in manifests.

Important APIs/types/functions: `Params`, `CycleParams`, `DefaultParams`, `HasParams`, `IsOwnedByThisUser`, `GetParams`, `SetParams`, and `manifestIDs`.

Control flow: maintenance params are looked up by fixed manifest labels. Missing params return defaults; multiple params choose the latest manifest ID. Setting params replaces manifests with the maintenance labels.

State/persistence behavior: persists owner, quick/full cycle intervals, log retention, object-lock extension, and list parallelism as JSON manifest data. Owner is compared to `ClientOptions.UsernameAtHost`.

Dependencies/integration: integrates the manifest manager with maintenance scheduling and ownership checks.

Risks/test signals: multiple concurrent clients can briefly create multiple manifests, so latest-pick behavior is intentional. Wrong owner prevents auto maintenance. Tested indirectly through quick maintenance ownership setup.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/repo/maintenance/maintenance_params.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/repo/maintenance/maintenance_quick_test.go -->
# sources/sync-backup/kopia/repo/maintenance/maintenance_quick_test.go

Purpose: verifies quick maintenance behavior when the epoch manager is enabled.

Important APIs/types/functions: `TestQuickMaintenanceRunWithEpochManager`, `TestQuickMaintenanceAdvancesEpoch`, `setRepositoryOwner`, `verifyEpochManagerIsEnabled`, and `verifyEpochTasksRunsInQuickMaintenance`.

Control flow: tests create format v3 repositories, set maintenance owner, verify epoch manager availability, run quick snapshot maintenance, and assert schedule entries for epoch compaction and advancement. The second test writes enough index blobs and advances fake time to force epoch advancement.

State/persistence behavior: writes repository objects/index blobs, maintenance params, and encrypted maintenance schedules; verifies write epoch changes after maintenance.

Dependencies/integration: uses `repotesting`, `faketime`, `epoch.Manager`, object writers, and `snapshotmaintenance.Run`.

Risks/test signals: catches regressions where quick maintenance bypasses epoch tasks or fails to advance eligible write epochs. It is format-version specific.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/repo/maintenance/maintenance_quick_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/repo/maintenance/maintenance_run.go -->
# sources/sync-backup/kopia/repo/maintenance/maintenance_run.go

Purpose: orchestrates quick, full, and automatic maintenance under ownership, schedule, safety, and locking rules.

Important APIs/types/functions: `Mode`, `TaskType`, `shouldRun`, `RunExclusive`, `Run`, `runQuickMaintenance`, `runFullMaintenance`, task wrappers, `shouldQuickRewriteContents`, `shouldFullRewriteContents`, `shouldDeleteOrphanedPacks`, `hadRecentFullRewrite`, and `findSafeDropTime`.

Control flow: `RunExclusive` loads params, checks owner unless forced, resolves auto mode, takes a local flock on the config lock file, updates the schedule before work, validates clock skew from the schedule blob timestamp, refreshes indexes, and invokes the callback. `Run` dispatches quick or full mode. Quick mode prioritizes epoch maintenance when enabled, otherwise manages content rewrite, orphaned pack deletion, index compaction, and log cleanup. Full mode rewrites content, safely drops deleted content, deletes orphaned packs, optionally extends object locks, runs epoch cleanup, and cleans logs.

State/persistence behavior: mutates repository content/index/log/blob retention state and persists task history in the encrypted maintenance schedule. Schedule update before task execution prevents tight crash loops.

Dependencies/integration: ties together repository writer, content manager, epoch manager, content logs, flock locking, maintenance params, schedules, stats, snapshot GC safety, and pack/content rewrite helpers.

Risks/test signals: incorrect safety timing can delete data too early; local-only locking does not coordinate across hosts; clock skew checks refuse unsafe runs. Tests cover rewrite/delete decision functions, safe-drop timing, epoch quick maintenance, and schedule behavior.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/repo/maintenance/maintenance_run.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/repo/maintenance/maintenance_run_test.go -->
# sources/sync-backup/kopia/repo/maintenance/maintenance_run_test.go

Purpose: unit tests maintenance scheduling decisions for orphaned pack deletion, content rewrite gating, and safe deleted-content drop times.

Important APIs/types/functions: `TestShouldDeleteOrphanedBlobs`, `TestShouldRewriteContents`, `TestFindSafeDropTime`, shared test timestamps, `shouldDeleteOrphanedPacks`, `shouldQuickRewriteContents`, `shouldFullRewriteContents`, and `findSafeDropTime`.

Control flow: table-driven cases build synthetic `Schedule.Runs` histories and safety parameters, then assert boolean decisions or cutoff timestamps.

State/persistence behavior: no repository state; tests exercise pure scheduling logic.

Dependencies/integration: uses package-internal access because tests are in package `maintenance`.

Risks/test signals: protects the most safety-critical timing logic without needing slow integration tests. It cannot catch content-manager side effects.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/repo/maintenance/maintenance_run_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/repo/maintenance/maintenance_safety.go -->
# sources/sync-backup/kopia/repo/maintenance/maintenance_safety.go

Purpose: defines maintenance safety timing parameters and preset safety levels.

Important APIs/types/functions: `SafetyParameters`, `SafetyNone`, and `SafetyFull`.

Control flow: no functions; the file declares durations for rewrite age, snapshot-GC age/margins, deleted-index drop margin, pack deletion minimum age, session expiration, rewrite-to-orphan-deletion delay, and eventual-consistency behavior.

State/persistence behavior: safety parameters are runtime inputs to maintenance, not persisted by this file.

Dependencies/integration: consumed by content rewrite, snapshot GC, pack GC, index compaction, and full/quick maintenance decisions.

Risks/test signals: `SafetyNone` is intentionally unsafe for concurrent/eventually consistent environments, while `SafetyFull` encodes conservative defaults. Tests in safety and run test files validate practical behavior.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/repo/maintenance/maintenance_safety.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/repo/maintenance/maintenance_safety_test.go -->
# sources/sync-backup/kopia/repo/maintenance/maintenance_safety_test.go

Purpose: integration tests maintenance safety around content deletion, object readability, and garbage collection.

Important APIs/types/functions: `TestMaintenanceSafety`, `verifyContentDeletedState`, `verifyObjectReadable`, and `verifyObjectNotFound`.

Control flow: the test writes repository objects, triggers maintenance and snapshot-GC style transitions, then checks whether content deleted flags and object reads match safety expectations.

State/persistence behavior: uses a real repository test environment with persisted content, manifests, and indexes.

Dependencies/integration: integrates object access, repository content state, maintenance safety presets, and test repository helpers.

Risks/test signals: detects unsafe early deletion or failure to delete after safety windows. Its exact coverage depends on test setup timing and format-specific suite execution.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/repo/maintenance/maintenance_safety_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/repo/maintenance/maintenance_schedule.go -->
# sources/sync-backup/kopia/repo/maintenance/maintenance_schedule.go

Purpose: stores encrypted maintenance schedule and task history in a repository blob.

Important APIs/types/functions: `RunInfo`, `Schedule`, `ReportRun`, `getAES256GCM`, `TimeToAttemptNextMaintenance`, `GetSchedule`, `SetSchedule`, `buildRunStats`, and constants for blob ID/key purpose.

Control flow: `GetSchedule` reads `kopia.maintenance`, returns an empty schedule if missing, derives an AES-256-GCM key, decrypts nonce-prefixed ciphertext with associated data, and JSON-decodes. `SetSchedule` JSON-encodes, encrypts with a random nonce, and writes the blob. `ReportRun` times a task, stores success/error and serialized stats, caps per-task run history, and persists the schedule.

State/persistence behavior: schedule data is persisted as an encrypted blob separate from manifests. It tracks next quick/full times and recent runs per task.

Dependencies/integration: uses repository key derivation, blob storage, gather buffers, random nonce generation, maintenance stats serialization, and ownership params.

Risks/test signals: corrupt or short blobs fail to load; losing schedule write errors during `ReportRun` is logged but the task error is returned. Tests cover schedule persistence, next-attempt calculation, and stats round trips.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/repo/maintenance/maintenance_schedule.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/repo/maintenance/maintenance_schedule_test.go -->
# sources/sync-backup/kopia/repo/maintenance/maintenance_schedule_test.go

Purpose: tests encrypted maintenance schedule persistence and next-maintenance timing logic.

Important APIs/types/functions: `TestMaintenanceSchedule`, `TestTimeToAttemptNextMaintenance`, and `toJSON`.

Control flow: format-specific schedule tests save and reload schedules and run info. Timing tests exercise enabled/disabled cycles, zero next times, ownership checks, and quick-vs-full ordering.

State/persistence behavior: creates repository schedule blobs through `SetSchedule`/`GetSchedule`; timing cases use parameter and schedule state.

Dependencies/integration: uses repository test environments, maintenance params, and JSON comparison helpers.

Risks/test signals: catches encryption/decryption, JSON shape, run history, and ownership regressions. Does not inspect raw ciphertext beyond behavior.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/repo/maintenance/maintenance_schedule_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/repo/maintenance/pack_gc.go -->
# sources/sync-backup/kopia/repo/maintenance/pack_gc.go

Purpose: deletes pack and expired session blobs that are no longer referenced by the content index.

Important APIs/types/functions: `DeleteUnreferencedPacksOptions`, `DeleteUnreferencedPacks`, `ContentManager().IterateUnreferencedPacks`, `ListActiveSessions`, and `DeleteUnreferencedPacksStats`.

Control flow: default parallelism is set, delete workers are started unless dry-run, prefixes are selected, active sessions are loaded, cutoff time is determined with a one-second slack, and each unreferenced blob is retained or queued for deletion depending on timestamp, `PackDeleteMinAge`, and active-session checkpoint age.

State/persistence behavior: deletes unreferenced pack/session blobs from blob storage and reports unreferenced, retained, and deleted counts/sizes. It does not directly change content indexes.

Dependencies/integration: depends on direct repository writer, blob storage deletion, content manager unreferenced-pack iteration, session IDs, content logging, and stats counters.

Risks/test signals: deleting a still-needed pack is catastrophic, so timestamp and session retention checks are central. Tests cover referenced/unreferenced packs, dry-run-like retention behavior, and helper blob creation.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/repo/maintenance/pack_gc.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/repo/maintenance/pack_gc_test.go -->
# sources/sync-backup/kopia/repo/maintenance/pack_gc_test.go

Purpose: integration tests deletion of unreferenced pack and session blobs.

Important APIs/types/functions: `TestDeleteUnreferencedPacks`, `verifyBlobExists`, `verifyBlobNotFound`, `mustPutDummyBlob`, and `mustPutDummySessionBlob`.

Control flow: tests create repository data and dummy blobs, run `DeleteUnreferencedPacks` under safety options, and assert which blobs remain or are deleted. Helpers write dummy pack/session blobs and verify blob existence by metadata lookup.

State/persistence behavior: mutates temporary blob storage by adding and deleting pack/session blobs.

Dependencies/integration: uses test HMAC/master keys, content session info encoding, blob APIs, repository environments, and maintenance safety.

Risks/test signals: catches accidental deletion of active-session or too-young blobs and failure to delete eligible orphans. Test data is format-sensitive.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/repo/maintenance/pack_gc_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/repo/maintenance/suite_test.go -->
# sources/sync-backup/kopia/repo/maintenance/suite_test.go

Purpose: runs format-specific maintenance test suites across supported repository format versions.

Important APIs/types/functions: `formatSpecificTestSuite`, `TestFormatV1`, `TestFormatV2`, and `TestFormatV3`.

Control flow: each top-level test constructs a suite with a format version and runs `suite.Run`.

State/persistence behavior: no direct persistence; it parameterizes other tests that create repository state.

Dependencies/integration: integrates `testify/suite` with Kopia format versions.

Risks/test signals: ensures maintenance behavior is checked against legacy and current formats. Adding a new format version requires extending this suite.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/repo/maintenance/suite_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/repo/maintenancestats/builder.go -->
# sources/sync-backup/kopia/repo/maintenancestats/builder.go

Purpose: serializes and deserializes typed maintenance stats into generic schedule extras.

Important APIs/types/functions: `Extra`, `Summarizer`, `Kind`, `ErrUnSupportedStatKindError`, `BuildExtra`, and `BuildFromExtra`.

Control flow: `BuildExtra` validates non-nil stats, marshals the struct to JSON, and stores its kind string. `BuildFromExtra` switches on kind, allocates the matching stats struct, unmarshals raw JSON into it, and returns it as a `Summarizer`.

State/persistence behavior: `Extra` values are persisted in maintenance schedule `RunInfo.Extra`, preserving task-specific stats without coupling schedule schema to each struct.

Dependencies/integration: used by `maintenance.buildRunStats` and task stats files.

Risks/test signals: every new stats kind must be registered in the switch or stored extras become unsupported. Tests cover success and error cases for all known kinds.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/repo/maintenancestats/builder.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/repo/maintenancestats/builder_test.go -->
# sources/sync-backup/kopia/repo/maintenancestats/builder_test.go

Purpose: verifies maintenance stats JSON wrapping and reconstruction for every supported stats type.

Important APIs/types/functions: `TestBuildExtraSuccess`, `TestBuildExtraError`, `TestBuildFromExtraSuccess`, `TestBuildFromExtraError`, and `unmarshalable`.

Control flow: table-driven cases compare exact `Extra.Kind` and JSON bytes for concrete stats, then reconstruct stats from raw extras and compare structs. Error cases cover nil stats, marshal failure, unsupported kind, and bad JSON.

State/persistence behavior: no repository state; protects the JSON payloads persisted in maintenance schedule history.

Dependencies/integration: spans all stats structs and their kind constants.

Risks/test signals: exact JSON byte comparisons catch field/tag changes. The tests document compatibility expectations for stored maintenance run extras.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/repo/maintenancestats/builder_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/repo/maintenancestats/stats_advance_epoch.go -->
# sources/sync-backup/kopia/repo/maintenancestats/stats_advance_epoch.go

Purpose: records whether epoch advancement ran and what the current epoch is.

Important APIs/types/functions: `AdvanceEpochStats`, `WriteValueTo`, `Summary`, and `Kind`.

Control flow: writes `currentEpoch` and `wasAdvanced` into content logs, summarizes either advancement or staying at the same epoch, and returns kind `advanceEpochStats`.

State/persistence behavior: instances are serialized into maintenance schedule extras and emitted to content logs.

Dependencies/integration: produced by epoch maintenance tasks in `maintenance_run.go` and handled by `BuildFromExtra`.

Risks/test signals: kind string must match builder switch. Builder tests cover JSON and reconstruction.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/repo/maintenancestats/stats_advance_epoch.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/repo/maintenancestats/stats_clean_up_log.go -->
# sources/sync-backup/kopia/repo/maintenancestats/stats_clean_up_log.go

Purpose: captures log cleanup counts and byte totals.

Important APIs/types/functions: `CleanupLogsStats`, `WriteValueTo`, `Summary`, and `Kind`.

Control flow: writes to-delete, deleted, and retained counters into content logs; summary formats counts with human-readable byte strings.

State/persistence behavior: stats are persisted in maintenance schedule run extras after log cleanup.

Dependencies/integration: produced by `CleanupLogs` and reconstructed by `BuildFromExtra`.

Risks/test signals: field names are compatibility-sensitive for stored extras. Builder tests assert exact JSON.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/repo/maintenancestats/stats_clean_up_log.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/repo/maintenancestats/stats_cleanup_markers.go -->
# sources/sync-backup/kopia/repo/maintenancestats/stats_cleanup_markers.go

Purpose: records epoch marker and deletion watermark cleanup counts.

Important APIs/types/functions: `CleanupMarkersStats`, `WriteValueTo`, `Summary`, and `Kind`.

Control flow: writes marker/watermark counts to content logs and returns a compact human summary.

State/persistence behavior: stored as maintenance schedule extra data for epoch cleanup tasks.

Dependencies/integration: produced by epoch manager cleanup and registered in stats builder.

Risks/test signals: kind and JSON tags must remain aligned with builder tests and historical schedule data.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/repo/maintenancestats/stats_cleanup_markers.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/repo/maintenancestats/stats_cleanup_superseded_indexes.go -->
# sources/sync-backup/kopia/repo/maintenancestats/stats_cleanup_superseded_indexes.go

Purpose: records cleanup of superseded epoch index blobs.

Important APIs/types/functions: `CleanupSupersededIndexesStats`, `WriteValueTo`, `Summary`, and `Kind`.

Control flow: stores max replacement time plus deleted blob count/size, writes them to content logs, and formats a summary.

State/persistence behavior: persisted in maintenance schedule extras for epoch index cleanup.

Dependencies/integration: produced by `epoch.Manager.CleanupSupersededIndexes` through maintenance run reporting.

Risks/test signals: time serialization and kind names are compatibility points covered by builder tests.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/repo/maintenancestats/stats_cleanup_superseded_indexes.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/repo/maintenancestats/stats_compact_indexes.go -->
# sources/sync-backup/kopia/repo/maintenancestats/stats_compact_indexes.go

Purpose: records the cutoff used when compacting indexes and dropping deleted content entries.

Important APIs/types/functions: `CompactIndexesStats`, `WriteValueTo`, `Summary`, and `Kind`.

Control flow: emits `droppedContentsDeletedBefore` and summarizes the cutoff timestamp.

State/persistence behavior: stored as schedule extra data after index compaction/drop-deleted tasks.

Dependencies/integration: produced by `dropDeletedContents` and reconstructed by stats builder.

Risks/test signals: timestamp meaning must align with safety logic in maintenance. Builder tests assert JSON shape.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/repo/maintenancestats/stats_compact_indexes.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/repo/maintenancestats/stats_compact_single_epoch.go -->
# sources/sync-backup/kopia/repo/maintenancestats/stats_compact_single_epoch.go

Purpose: records stats from compacting one epoch of index blobs.

Important APIs/types/functions: `CompactSingleEpochStats`, `WriteValueTo`, `Summary`, and `Kind`.

Control flow: writes superseded blob count, total size, and epoch number; summary formats size and epoch.

State/persistence behavior: persisted as maintenance run extra data for quick/full epoch maintenance.

Dependencies/integration: produced by `epoch.Manager.MaybeCompactSingleEpoch`.

Risks/test signals: builder tests cover exact JSON; maintenance quick tests assert this task records runs.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/repo/maintenancestats/stats_compact_single_epoch.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/repo/maintenancestats/stats_delete_unreferenced_packs.go -->
# sources/sync-backup/kopia/repo/maintenancestats/stats_delete_unreferenced_packs.go

Purpose: records counts and sizes for pack garbage collection.

Important APIs/types/functions: `DeleteUnreferencedPacksStats`, `WriteValueTo`, `Summary`, and `Kind`.

Control flow: writes unreferenced, deleted, and retained pack counts/sizes into content logs and returns a readable summary.

State/persistence behavior: stored in maintenance schedule extras after pack GC tasks.

Dependencies/integration: produced by `DeleteUnreferencedPacks` and interpreted by `BuildFromExtra`.

Risks/test signals: fields distinguish retained from deleted, which is important for dry-run and safety-preserved blobs. Builder tests cover JSON.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/repo/maintenancestats/stats_delete_unreferenced_packs.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/repo/maintenancestats/stats_extend_blob_retention.go -->
# sources/sync-backup/kopia/repo/maintenancestats/stats_extend_blob_retention.go

Purpose: records object-lock retention extension results.

Important APIs/types/functions: `ExtendBlobRetentionStats`, `WriteValueTo`, `Summary`, and `Kind`.

Control flow: writes to-extend count, extended count, and retention period string; summary reports the same.

State/persistence behavior: persisted as full-maintenance extra data when object-lock extension is enabled.

Dependencies/integration: produced by `extendBlobRetentionTime` and handled by the stats builder.

Risks/test signals: retention period is a string rather than duration type, so formatting is part of the contract. Tests assert exact JSON.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/repo/maintenancestats/stats_extend_blob_retention.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/repo/maintenancestats/stats_generate_range_checkpoint.go -->
# sources/sync-backup/kopia/repo/maintenancestats/stats_generate_range_checkpoint.go

Purpose: records the epoch range covered by a generated range checkpoint.

Important APIs/types/functions: `GenerateRangeCheckpointStats`, `WriteValueTo`, `Summary`, and `Kind`.

Control flow: writes min and max epoch fields and summarizes the inclusive range.

State/persistence behavior: stored in maintenance schedule extras for epoch range compaction.

Dependencies/integration: produced by `epoch.Manager.MaybeGenerateRangeCheckpoint`.

Risks/test signals: kind/JSON fields are covered by builder tests. Incorrect range semantics would affect maintenance observability rather than data directly.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/repo/maintenancestats/stats_generate_range_checkpoint.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/repo/maintenancestats/stats_rewrite_contents.go -->
# sources/sync-backup/kopia/repo/maintenancestats/stats_rewrite_contents.go

Purpose: records content rewrite counts and byte totals.

Important APIs/types/functions: `RewriteContentsStats`, `WriteValueTo`, `Summary`, and `Kind`.

Control flow: writes to-rewrite, rewritten, and retained counters/sizes into content logs and formats a human summary.

State/persistence behavior: persisted in schedule extras after quick or full content rewrite tasks.

Dependencies/integration: produced by `RewriteContents` and registered in `BuildFromExtra`.

Risks/test signals: rewritten vs retained separation supports safety diagnostics. Builder and content rewrite tests validate JSON and selected stats values.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/repo/maintenancestats/stats_rewrite_contents.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/repo/maintenancestats/stats_snapshot_gc.go -->
# sources/sync-backup/kopia/repo/maintenancestats/stats_snapshot_gc.go

Purpose: records snapshot garbage collection results across unreferenced, deleted, recent, in-use, system, and recovered contents.

Important APIs/types/functions: `SnapshotGCStats`, `WriteValueTo`, `Summary`, and `Kind`.

Control flow: writes all content counters/sizes to a content log JSON object and generates a summary string covering deletion, retention, in-use, and recovery.

State/persistence behavior: persisted in maintenance schedule extras for snapshot GC runs.

Dependencies/integration: used by snapshot maintenance and stats builder.

Risks/test signals: summary currently formats raw byte numbers for some fields rather than `units.BytesString`, unlike other stats. Builder tests assert JSON structure and reconstruction.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/repo/maintenancestats/stats_snapshot_gc.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/repo/maintenancestats/typeconversion.go -->
# sources/sync-backup/kopia/repo/maintenancestats/typeconversion.go

Purpose: safely converts signed integer counts/sizes to `uint64` for stats fields.

Important APIs/types/functions: `ToUint64` and package-level `negativeValueWarningLimit`.

Control flow: if the input is negative, it logs a throttled warning and returns zero; otherwise it converts to `uint64`.

State/persistence behavior: prevents negative internal size/count values from being serialized as huge unsigned stats values.

Dependencies/integration: used by cleanup and GC stats builders; depends on `rate.Sometimes` for throttled warning logs.

Risks/test signals: negative values are hidden as zero after warning, which avoids bad metrics but may mask upstream bugs. Tests cover min, negative, zero, positive, and max values.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/repo/maintenancestats/typeconversion.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/repo/maintenancestats/typeconversion_test.go -->
# sources/sync-backup/kopia/repo/maintenancestats/typeconversion_test.go

Purpose: tests signed-to-unsigned stats conversion behavior.

Important APIs/types/functions: `TestToUint64` and `ToUint64`.

Control flow: table cases pass `math.MinInt`, `-1`, `0`, `1`, and `math.MaxInt`, then assert negative inputs become zero and non-negative inputs preserve value.

State/persistence behavior: no state; protects values that later become persisted maintenance stats.

Dependencies/integration: uses `testify/require` and `math` constants.

Risks/test signals: does not assert warning throttling, only conversion results.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/repo/maintenancestats/typeconversion_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/repo/manifest/committed_manifest_manager.go -->
# sources/sync-backup/kopia/repo/manifest/committed_manifest_manager.go

Purpose: manages committed manifest entries stored in `m`-prefixed repository contents, including loading, merging, writing, and compaction.

Important APIs/types/functions: `committedManifestManager`, `getCommittedEntryOrNil`, `findCommittedEntries`, `commitEntries`, `writeEntriesLocked`, `loadCommittedContentsLocked`, `loadManifestContentsLocked`, `compactLocked`, `mergeEntryLocked`, `ensureInitializedLocked`, `loadManifestContent`, and `newCommittedManager`.

Control flow: reads are guarded by a mutex and call `ensureInitializedLocked`, which reloads manifest contents when content-manager revision changes. Loading iterates manifest contents in parallel, decodes gzip-compressed JSON, merges latest entries by mod time/ID, and removes entries marked deleted. Writes encode entries into a gzip JSON manifest content. Compaction writes the current live set while index flushing is disabled, deletes old manifest contents, and flushes when auto-compaction triggers.

State/persistence behavior: maintains cached committed entries, committed content IDs, and last content revision in memory; persists manifest batches as repository content and deletes superseded manifest contents during compaction.

Dependencies/integration: depends on content manager, gather buffers, gzip/json encoding, content index prefix iteration, and serialized manifest decoder.

Risks/test signals: compaction must be atomic with index flush disabled or manifests can be lost. Malformed content normally prevents loading unless `KOPIA_IGNORE_MALFORMED_MANIFEST_CONTENTS` is set. Tests cover corrupted content, compaction, read-only auto-compaction behavior, and reloads.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/repo/manifest/committed_manifest_manager.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/repo/manifest/manifest_entry.go -->
# sources/sync-backup/kopia/repo/manifest/manifest_entry.go

Purpose: defines public manifest metadata and helpers for selecting or deduplicating metadata entries.

Important APIs/types/functions: `EntryMetadata`, `DedupeEntryMetadataByLabel`, `PickLatestID`, and `isLaterThan`.

Control flow: dedupe groups entries by a label value and keeps the latest entry per value, then sorts results by mod time and ID. `PickLatestID` scans entries and returns the ID with latest mod time, using ID tie-breaks.

State/persistence behavior: metadata mirrors persisted manifest entries but this file only manipulates in-memory slices.

Dependencies/integration: used by maintenance params and higher-level snapshot/manifest lookups where concurrent duplicate labels can exist.

Risks/test signals: entries missing the dedupe label collapse under the empty string key. Tie-breaking by lexicographic ID is arbitrary but deterministic. Tests cover latest picking and label dedupe.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/repo/manifest/manifest_entry.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/repo/manifest/manifest_entry_test.go -->
# sources/sync-backup/kopia/repo/manifest/manifest_entry_test.go

Purpose: tests manifest metadata latest-selection and label deduplication.

Important APIs/types/functions: `TestPickLatestID`, `TestDedupeEntryMetadataByLabel`, `PickLatestID`, and `DedupeEntryMetadataByLabel`.

Control flow: cases construct metadata with different mod times, IDs, and labels, then assert selected IDs or deduped result order.

State/persistence behavior: no persisted state; tests pure metadata helpers.

Dependencies/integration: uses Go time values and assertion helpers.

Risks/test signals: protects deterministic tie-breaking and ordering relied on by callers handling duplicate manifests.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/repo/manifest/manifest_entry_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/repo/manifest/manifest_manager.go -->
# sources/sync-backup/kopia/repo/manifest/manifest_manager.go

Purpose: provides the public JSON manifest manager used for snapshots, maintenance params, and other repository metadata records.

Important APIs/types/functions: `Manager`, `ID`, `ErrNotFound`, `ContentPrefix`, `TypeLabelKey`, `Put`, `GetMetadata`, `Get`, `Find`, `Flush`, `Delete`, `Compact`, `IDsToStrings`, `IDsFromStrings`, `ManagerOptions`, and `NewManager`.

Control flow: `Put` requires a non-empty `type` label, generates a random hex ID, JSON-marshals payload, and stores a pending entry. Reads check pending first, then committed. `Find` merges pending and committed label matches and sorts by mod time. `Flush` commits pending entries through the committed manager. `Delete` creates a pending tombstone for an existing entry. `NewManager` configures time source and auto-compaction threshold.

State/persistence behavior: pending entries are in memory until flush; committed entries are persisted as content batches. Deletes are tombstones that become effective after merge and compaction.

Dependencies/integration: depends on content manager, compression, logging, metrics registry placeholder, random ID generation, and committed manager.

Risks/test signals: failing to flush loses pending manifests; duplicate labels are allowed; delete races are resolved by mod time. Tests cover put/get/find/delete/flush, corrupted content, invalid puts, auto-compaction thresholds, read-only behavior, and benchmarks.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/repo/manifest/manifest_manager.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/repo/manifest/manifest_manager_test.go -->
# sources/sync-backup/kopia/repo/manifest/manifest_manager_test.go

Purpose: integration and unit tests for manifest manager lifecycle, persistence, corruption handling, validation, and compaction.

Important APIs/types/functions: `TestManifest`, `TestManifestInitCorruptedBlock`, helper `addAndVerify`, `verifyItem`, `verifyMatches`, `newManagerForTesting`, `TestManifestInvalidPut`, `TestManifestAutoCompaction`, `TestManifestConfigureAutoCompaction`, `TestManifestAutoCompactionWithReadOnly`, and `BenchmarkLargeCompaction`.

Control flow: tests add labeled manifests, verify find/get before and after flush, reopen a second manager over the same storage, delete and compact, corrupt underlying packs, validate bad puts, and check compaction behavior at thresholds and under read-only storage.

State/persistence behavior: uses in-memory blob storage plus content managers to persist manifest contents and indexes between manager instances.

Dependencies/integration: exercises content manager, format options, encryption/hashing defaults, read-only wrapper, blobtesting data maps, and test logging.

Risks/test signals: catches subtle reload/compaction and corruption paths. Benchmark covers large compaction performance but is not a correctness gate in normal tests.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/repo/manifest/manifest_manager_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/repo/manifest/serialized.go -->
# sources/sync-backup/kopia/repo/manifest/serialized.go

Purpose: implements memory-conscious decoding for serialized manifest content JSON.

Important APIs/types/functions: `manifest`, `manifestEntry`, `decodeManifestArray`, `parseFields`, `decodeArray`, `expectDelimToken`, `stringToken`, and `errEOF`.

Control flow: the decoder manually consumes the root object, looks for a single case-insensitive `entries` field, skips other fields, decodes each entry into a slice, and validates expected delimiters. EOF is converted to a package error for clearer diagnostics.

State/persistence behavior: decodes persisted manifest content batches; no writes occur here.

Dependencies/integration: called after gzip decompression in `loadManifestContent`; depends on `encoding/json` token streaming.

Risks/test signals: unknown fields are skipped only at token-label level; if an unknown field has a complex value, failing to consume it could break future extension unless handled by decoder token flow. Tests cover good and bad serialized inputs and all-field population.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/repo/manifest/serialized.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/repo/manifest/serialized_test.go -->
# sources/sync-backup/kopia/repo/manifest/serialized_test.go

Purpose: tests the custom manifest JSON decoder against complete structs, valid inputs, and malformed inputs.

Important APIs/types/functions: `checkPopulated`, `allPopulated`, `TestManifestDecode_GetsAllFields`, `TestManifestDecode_GoodInput`, and `TestManifestDecode_BadInput`.

Control flow: reflection helpers ensure fixture structs have non-zero fields so decoder tests are meaningful. Good inputs decode and compare expected manifests; bad inputs from testdata assert decoder errors.

State/persistence behavior: no repository state; validates the persisted manifest JSON format parser.

Dependencies/integration: uses `manifest/testdata`, `encoding/json`, reflection, slices, and `testify`.

Risks/test signals: catches field-loss when decoder changes. Bad-input fixtures protect error paths for repeated fields, malformed arrays, token mismatches, and EOF cases.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/repo/manifest/serialized_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/repo/manifest/testdata/manifests.go -->
# sources/sync-backup/kopia/repo/manifest/testdata/manifests.go

Purpose: provides serialized manifest JSON fixtures for decoder tests.

Important APIs/types/functions: `testInput`, `BadInputs`, good input fixture variables, and expected manifest fixture constants.

Control flow: no executable logic beyond variable initialization. The fixtures include realistic snapshot-like manifest data and malformed cases such as repeated fields or invalid JSON structure.

State/persistence behavior: models persisted manifest JSON payloads used by `serialized_test.go`; no runtime persistence.

Dependencies/integration: imported only by manifest tests.

Risks/test signals: fixture realism helps protect decoder compatibility with historical manifest data. If fixture structs lack populated fields, tests could miss decoder omissions; `allPopulated` in tests mitigates that.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/repo/manifest/testdata/manifests.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/repo/object/indirect.go -->
# sources/sync-backup/kopia/repo/object/indirect.go

Purpose: defines entries for indirect object index streams used to represent large or concatenated objects.

Important APIs/types/functions: `IndirectObjectEntry` and `endOffset`.

Control flow: `endOffset` returns `Start + Length`. The comment shows the JSON shape stored in indirect stream metadata.

State/persistence behavior: entries are serialized into indirect object indexes, pointing byte ranges at underlying object/content IDs.

Dependencies/integration: consumed by object manager concatenation, index loading, and object readers.

Risks/test signals: offset/length correctness is critical for reads and concatenation. Coverage is mostly through object manager and reader tests outside this work item.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/repo/object/indirect.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/repo/object/object_manager.go -->
# sources/sync-backup/kopia/repo/object/object_manager.go

Purpose: manages content-addressable repository objects on top of content storage, including writer creation, object concatenation, and backing-content prefetch.

Important APIs/types/functions: `Reader`, internal `contentReader`/`contentManager`, `Manager`, `NewWriter`, `closedWriter`, `Concatenate`, `appendIndexEntriesForObject`, `appendIndexEntries`, `PrefetchBackingContents`, and `NewObjectManager`.

Control flow: `NewWriter` reuses an `objectWriter` from a pool, selects configured or default splitter, configures compression, prefix, async write semaphore, and resets buffers. `Concatenate` converts each input object into indirect index entries, writes a new indirect index object, and returns an indirect object ID. Prefetch walks backing contents for object IDs, ignores not-found errors, and asks the content manager to prefetch collected IDs.

State/persistence behavior: writers persist split contents through the content manager; concatenation persists only a new indirect index object rather than rewriting source data. The manager stores default splitter factory and a writer pool.

Dependencies/integration: integrates content manager read/write APIs, compression registry, splitter registry, object index loading/writing, metrics placeholder, and content prefetching.

Risks/test signals: pooled writers must be fully reset to avoid leaking prior state; concatenation relies on correct lengths and offsets, with a small deduplication cost at externally chosen split boundaries. Errors while opening component objects abort concatenation. Tests likely live in neighboring object files not in this subset.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/repo/object/object_manager.go -->
