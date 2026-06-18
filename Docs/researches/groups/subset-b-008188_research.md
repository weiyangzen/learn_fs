# subset-b-008188 Research

Grouped research for the listed MinIO files. Each section preserves its original source path and is delimited for deterministic splitting into `Docs/researches/<source_path>_research.md`.

<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio/cmd/callhome.go -->
# sources/object-store/minio/cmd/callhome.go

## Purpose
`callhome.go` implements MinIO's optional SUBNET callhome diagnostics loop. It elects one cluster node with a namespace lock, collects `madmin.HealthInfo`, gzip-compresses it, uploads it to SUBNET, and emits internal audit/log signals for each diagnostics attempt.

## Important APIs, Types, And Functions
`initCallhome` starts the background loop only when `globalCallhomeConfig.Enabled()` is true. `runCallhome` acquires `.minio.sys/callhome/runCallhome.lock` using `ObjectLayer.NewNSLock` and keeps the elected node running periodic calls. `performCallhome` builds a health query for all `madmin.HealthDataTypesList`, calls `fetchHealthInfo`, and sends the final report. `sendHealthInfo` uploads to `globalSubnetConfig.BaseURL + /api/health/upload`. `createHealthJSONGzip` writes a version header and health payload into a gzip JSON stream.

## Control Flow
The startup goroutine repeatedly tries `runCallhome`; a lock timeout means another node is leader, so it sleeps a randomized fraction of the configured frequency and retries. The leader performs one immediate callhome, then ticks on `globalCallhomeConfig.FrequencyDur()` until disabled or canceled. `performCallhome` uses a ten-second health collection context and returns silently on timeout.

## State And Persistence Behavior
The file does not persist local state. Cluster coordination is transient lock state in the object namespace. Uploaded diagnostics leave MinIO via `globalSubnetConfig.Upload`. Audit state is written through `auditLogInternal`.

## Dependencies And Integration Points
It depends on object-layer readiness, SUBNET configuration, callhome dynamic configuration from `config-current.go`, health collection helpers, namespace locks, internal logging, and madmin health schemas.

## Risks And Test Signals
Risks include silent skipped uploads when the object layer is unavailable, upload failures only logged/audited, and gzip helpers returning nil after encode errors. The lock path is critical for one-leader behavior. No direct tests are in this subset; coverage is mostly integration-level through config enablement, health collection, and SUBNET upload behavior.
<!-- END_FILE_RESEARCH: sources/object-store/minio/cmd/callhome.go -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio/cmd/common-main.go -->
# sources/object-store/minio/cmd/common-main.go

## Purpose
`common-main.go` contains process-wide startup plumbing shared by MinIO server modes: terminal/color setup, console UI configuration, CLI context construction, environment-file and secret handling, early/global env validation, DNS cache refresh, root credential loading, KMS connection, TLS certificate loading, and detached background contexts.

## Important APIs, Types, And Functions
`init` initializes logger behavior, color, gob registrations, retry policy, release metadata, and CI/orchestrator flags. `minioConfigToConsoleFeatures`, `buildOpenIDConsoleConfig`, and `initConsoleServer` translate MinIO runtime config into Console environment and server objects. `buildServerCtxt` reads CLI flags/config into `serverCtxt`; `handleCommonArgs` validates addresses and initializes global config/certs directories. `envKV`, `parsEnvEntry`, `minioEnvironFromFile`, `readFromSecret`, and `loadEnvVarsFromFiles` implement env-file and secret loading. `serverHandleEarlyEnvVars`, `serverHandleEnvVars`, `loadRootCredentials`, `autoGenerateRootCredentials`, `handleKMSConfig`, and `getTLSConfig` update global runtime state.

## Control Flow
Startup reads early browser settings, builds server context from flags or config files, applies common args, loads env files/secrets, validates env-derived URLs/domains/IPs/credential presence, then initializes credentials, KMS, TLS, Console, and DNS refresh as needed. Many invalid inputs call `logger.Fatal`, making this file part of MinIO's fail-fast boot boundary.

## State And Persistence Behavior
This file mostly mutates process globals and environment variables. It creates config/certs/CAs directories with `0700`, ignores permission errors for mounted Kubernetes-like paths, sets `CONSOLE_*` env vars, and loads TLS cert manager state. Secrets are read from direct paths or `/run/secrets/<name>` and trimmed.

## Dependencies And Integration Points
It integrates with MinIO CLI flags, Console API, IAM OpenID provider state, browser config, KMS/KES, certificate manager, DNS cache, global endpoint/domain state, auth credential validation, logger, and MinIO config env constants.

## Risks And Test Signals
Risks include broad global side effects, fatal exits that are hard to unit-test, env parsing that only supports simple `KEY=value`/`export KEY=value`, and address/port collisions. Tests in `common-main_test.go` cover secret trimming and env-file parsing for quotes, comments, malformed entries, and export/no-export forms; broader startup paths need integration coverage.
<!-- END_FILE_RESEARCH: sources/object-store/minio/cmd/common-main.go -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio/cmd/common-main_test.go -->
# sources/object-store/minio/cmd/common-main_test.go

## Purpose
`common-main_test.go` verifies the smaller, deterministic helpers in `common-main.go` that parse secret files and environment configuration files.

## Important APIs, Types, And Functions
`Test_readFromSecret` writes temporary secret files and checks that `readFromSecret` trims whitespace/newlines while preserving meaningful content. `Test_minioEnvironFromFile` exercises `minioEnvironFromFile` and indirectly `parsEnvEntry` for `export` syntax, plain syntax, single and double quotes, comments, blank lines, and malformed entries.

## Control Flow
Each test creates a temporary file, writes the test case content, syncs/closes it, calls the target helper, and compares returned values or expected error behavior. The env-file test uses `reflect.DeepEqual` on `[]envKV`.

## State And Persistence Behavior
Only temporary files under `t.TempDir()` are written. The tests do not mutate real process environment variables and do not invoke fatal startup paths.

## Dependencies And Integration Points
The tests depend on `os.CreateTemp`, `errors`, `reflect`, and the `envKV` type from `common-main.go`. They validate inputs used by Docker/Kubernetes secret and `MINIO_CONFIG_ENV_FILE` workflows.

## Risks And Test Signals
The suite is intentionally narrow. It does not cover missing secret files, `/run/secrets` fallback, scanner token-size limits, inline comments, escaped quotes, or `loadEnvVarsFromFiles` mutation behavior. It is a useful regression signal for the supported simple env-file grammar.
<!-- END_FILE_RESEARCH: sources/object-store/minio/cmd/common-main_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio/cmd/config-common.go -->
# sources/object-store/minio/cmd/config-common.go

## Purpose
`config-common.go` provides low-level object-store helpers for reading, writing, deleting, and checking MinIO configuration objects in `.minio.sys`.

## Important APIs, Types, And Functions
`errConfigNotFound` normalizes missing or empty config objects. `readConfigWithMetadata` reads an object through `objectIO.GetObjectNInfo`, returns bytes plus `ObjectInfo`, and maps object-not-found/empty content to `errConfigNotFound`. `readConfig` drops metadata. `objectDeleter` narrows delete dependencies. `deleteConfig` deletes exact config objects via prefix-delete optimization. `saveConfigWithOpts` wraps bytes in a SHA256 `hash.Reader` and writes through `PutObject`. `saveConfig` uses `MaxParity`. `checkConfig` probes object existence through `GetObjectInfo`.

## Control Flow
Read paths open a `GetObjectReader`, drain it fully, close it, and classify errors. Write paths construct a hash-validated reader and hand off to object-layer persistence. Delete/check paths translate object-not-found into the shared config sentinel.

## State And Persistence Behavior
All state lives as objects under `minioMetaBucket`. Writes use object-layer options, defaulting to maximum parity for durability. Deletes use `DeletePrefixObject` for exact-object optimization.

## Dependencies And Integration Points
These helpers are used by server config, config history, scanner state, background heal info, and data usage persistence. They integrate with MinIO object APIs, HTTP range reader conventions, `internal/hash`, `getSHA256Hash`, and `NewPutObjReader`.

## Risks And Test Signals
The helpers treat empty config files as missing, which is intentional but can hide corruption as reinitialization higher up. Full-object reads can be expensive for large configs, though config objects are expected small. There are no direct tests in this subset; behavior is exercised indirectly by config and scanner tests.
<!-- END_FILE_RESEARCH: sources/object-store/minio/cmd/config-common.go -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio/cmd/config-current.go -->
# sources/object-store/minio/cmd/config-current.go

## Purpose
`config-current.go` registers current configuration defaults/help, validates subsystem configuration, looks up persisted/env-overridden values, applies dynamic settings to global runtime systems, and loads/saves the current `config.Config`.

## Important APIs, Types, And Functions
`initHelp` registers default KVS and help for site, API, scanner, batch, identity, policy, logger/audit, notifications, lambda, SUBNET/callhome, drive, browser, ILM, and erasure-only storage/heal subsystems. `globalServerConfig` plus `globalServerConfigMu` hold process config. `validateSubSysConfig` and `validateConfig` validate a target subsystem, including live connection checks for etcd/LDAP and callhome license gating. `lookupConfigs` initializes DNS/etcd/site/encryption/notification/lambda and calls `applyDynamicConfig`. `applyDynamicConfigForSubSys` updates global API, compression, heal, batch, scanner, logger/audit, storage class, SUBNET, callhome, drive, browser, and ILM state. `GetHelp`, `newSrvConfig`, `getValidConfig`, and `loadConfig` expose help and config load/save flows.

## Control Flow
Defaults and help are registered once. Validation disables env merging under `env.LockSetEnv` to test persisted config alone, then validates one subsystem or all. Loading reads server config, overlays env-derived runtime settings in `lookupConfigs`, and swaps `globalServerConfig` under lock. Dynamic apply iterates `config.SubSystemsDynamic`; callhome startup is triggered when config changes from disabled to enabled.

## State And Persistence Behavior
The file mutates many global runtime systems but persists only through `saveServerConfig` in other files. It updates scanner atomics, logger targets, remote transports, worker counts, SUBNET env exports, and the in-memory server config map.

## Dependencies And Integration Points
It is a central integration point for MinIO's internal config packages, object layer drive counts, global root CAs, IAM identity config, notification/lambda target creation, logger target updates, scanner throttling, lifecycle workers, and callhome.

## Risks And Test Signals
Risks include global mutable state, partial dynamic-apply failures, live external validation causing startup/admin-set failures, and environment merging needing strict locking. `config-current_test.go` verifies region initialization and update lookup. Most subsystem behavior relies on package-specific tests and integration tests.
<!-- END_FILE_RESEARCH: sources/object-store/minio/cmd/config-current.go -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio/cmd/config-current_test.go -->
# sources/object-store/minio/cmd/config-current_test.go

## Purpose
`config-current_test.go` verifies basic server configuration initialization and region mutation through MinIO's current config map.

## Important APIs, Types, And Functions
`TestServerConfig` uses `prepareFS`, `newTestConfig`, `globalServerConfig`, `globalSite`, `config.SetRegion`, and `config.LookupSite`.

## Control Flow
The test creates a filesystem-backed object layer, initializes test config with the default MinIO region, asserts `globalSite.Region()`, mutates the region in `globalServerConfig`, and verifies `config.LookupSite` returns the new region.

## State And Persistence Behavior
The test creates and removes a temporary FS backend. It mutates package globals (`globalServerConfig`, `globalSite`) through normal test initialization paths.

## Dependencies And Integration Points
It integrates with filesystem object-layer test setup, current config defaults, site/region config helpers, and the config load path used by startup.

## Risks And Test Signals
This is a smoke test, not comprehensive config validation. It does not exercise dynamic subsystem application, env merging, encrypted config, migration, or external target validation. It is still a useful signal that default config creation and site region fields remain compatible.
<!-- END_FILE_RESEARCH: sources/object-store/minio/cmd/config-current_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio/cmd/config-dir.go -->
# sources/object-store/minio/cmd/config-dir.go

## Purpose
`config-dir.go` defines default MinIO config and certificate directory locations and the small `ConfigDir` wrapper used by startup and TLS loading.

## Important APIs, Types, And Functions
Constants define `.minio`, `certs`, `CAs`, `public.crt`, and `private.key`. `ConfigDir` wraps a path with `Get`. `getDefaultConfigDir`, `getDefaultCertsDir`, and `getDefaultCertsCADir` derive paths from the user home directory. `defaultConfigDir`, `defaultCertsDir`, `defaultCertsCADir`, `globalConfigDir`, `globalCertsDir`, and `globalCertsCADir` hold defaults/current directories. `mkdirAllIgnorePerm` creates directories while ignoring permission errors. `getConfigFile`, `getPublicCertFile`, and `getPrivateKeyFile` build current file paths.

## Control Flow
Defaults are computed at package initialization. Startup may replace globals through `newConfigDir` and `handleCommonArgs` in `common-main.go`; later helpers read the current paths.

## State And Persistence Behavior
The only filesystem mutation is directory creation with mode `0700`. Ignoring permission errors supports mounted read-only or externally managed paths.

## Dependencies And Integration Points
It depends on `go-homedir`, `os`, and `filepath`. It is used by config migration, TLS certificate loading, Console cert configuration, and KMS CA lookup.

## Risks And Test Signals
If home lookup fails, default paths become empty and startup must reject them unless explicitly set. Ignored permission errors can defer failures to later file reads. No direct tests are in this subset; startup integration covers the behavior.
<!-- END_FILE_RESEARCH: sources/object-store/minio/cmd/config-dir.go -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio/cmd/config-encrypted_test.go -->
# sources/object-store/minio/cmd/config-encrypted_test.go

## Purpose
`config-encrypted_test.go` verifies madmin encrypted config payload round-tripping with MinIO credentials.

## Important APIs, Types, And Functions
`TestDecryptData` builds two `auth.Credentials`, encrypts `config data` with `madmin.EncryptData`, and decrypts with `madmin.DecryptData`.

## Control Flow
The test table covers two encrypted payloads with matching credentials and one plaintext payload expected to fail decryption. Successful decryptions are byte-compared to the original data.

## State And Persistence Behavior
No persistent state is written. All encryption/decryption work is in memory.

## Dependencies And Integration Points
The test targets the same madmin encryption primitives used historically by config migration/decryption paths. It depends on `auth.Credentials.String()` as the encryption key material.

## Risks And Test Signals
This test does not directly call MinIO's `decryptData` wrapper or KMS-backed encryption. It is a focused compatibility signal that credential-derived encrypted blobs can still be read and plaintext is rejected by `madmin.DecryptData`.
<!-- END_FILE_RESEARCH: sources/object-store/minio/cmd/config-encrypted_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio/cmd/config-migrate.go -->
# sources/object-store/minio/cmd/config-migrate.go

## Purpose
`config-migrate.go` loads legacy MinIO configuration locations and schemas, migrates older `serverConfigV33` JSON into the current `config.Config`, and initializes new config when no readable config exists.

## Important APIs, Types, And Functions
`Save` and `Load` wrap `quick.SaveConfig`/`quick.LoadConfig` with `globalEtcdClient`. `readConfigWithoutMigrate` checks legacy filesystem paths, deprecated paths, and `.minio.sys/config/config.json`; decrypts object-stored config; tries current `readServerConfig`; falls back to legacy JSON; applies version-specific migrations from 29 through 33; preserves old credentials when env credentials are absent; and copies region, storage class, logger/audit, LDAP, OPA, compression, and notification settings into a new current config.

## Control Flow
The loader first tries quick config paths, then object-store config. Missing config creates and saves a fresh current config. If current unmarshalling succeeds, it returns merged current config. If not, legacy schema unmarshalling drives migration and returns a current map without writing it in this function.

## State And Persistence Behavior
Fresh initialization persists config via `saveServerConfig`. Migration updates `globalActiveCred` when appropriate but otherwise returns the migrated config to callers. It may read from filesystem, etcd, or `.minio.sys`.

## Dependencies And Integration Points
It integrates with config-dir paths, quick config storage, object-store config helpers, config encryption/decryption, legacy notification target structs, logger config setters, LDAP/OpenID/OPA/compression/storageclass packages, and global credential state.

## Risks And Test Signals
Risks include lossy migration if a legacy field has no current setter, silent reinitialization on unparsable legacy JSON, and mixed legacy/current locations. No direct migration tests are in this subset; coverage depends on broader config compatibility tests.
<!-- END_FILE_RESEARCH: sources/object-store/minio/cmd/config-migrate.go -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio/cmd/config-versions.go -->
# sources/object-store/minio/cmd/config-versions.go

## Purpose
`config-versions.go` defines legacy server config schema types needed for migration to the current `config.Config` representation.

## Important APIs, Types, And Functions
`FileLogger` and `ConsoleLogger` are compatibility structs for older logrus-era config. `serverConfigV33` embeds `quick.Config` and includes version, credentials, region, WORM flag, storage class, notification config, logger config, compression config, OpenID config, legacy OPA policy config, and legacy LDAP config.

## Control Flow
There is no runtime control flow. The structs are populated by JSON/quick config decoding in `config-migrate.go` and then read field-by-field during migration.

## State And Persistence Behavior
The file defines serialized JSON field names for legacy config. It does not persist by itself.

## Dependencies And Integration Points
It depends on `auth`, current/legacy config package types, notification config, storageclass, logger, OpenID, OPA, LDAP, and `quick.Config`. It is tightly coupled to migration code.

## Risks And Test Signals
Changing these structs can break old config decoding. Because only version 33 is represented here with comments about prior changes, migration support for older versions depends on compatibility branches in `config-migrate.go`. No direct tests are in this subset.
<!-- END_FILE_RESEARCH: sources/object-store/minio/cmd/config-versions.go -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio/cmd/config.go -->
# sources/object-store/minio/cmd/config.go

## Purpose
`config.go` implements current server config persistence, config history management, encrypted config read/write, and the `ConfigSys` initializer.

## Important APIs, Types, And Functions
Constants define config object prefixes and `config.json`. `listServerConfigHistory`, `delServerConfigHistory`, `readServerConfigHistory`, and `saveServerConfigHistory` manage `config/history/*.kv` entries. `saveServerConfig` marshals current config and optionally encrypts with `GlobalKMS`. `readServerConfig` reads/decrypts current config, returns defaults when missing, unmarshals with jsoniter, and merges missing entries. `ConfigSys.Init`, `NewConfigSys`, and `initConfig` drive boot-time config loading.

## Control Flow
History listing pages object listings, optionally reads/decrypts each entry, skips unreadable history data, and sorts by creation time. Current config reads from `.minio.sys/config/config.json` unless caller supplied bytes. Missing current config returns a default config after `lookupConfigs`; malformed/decryption errors propagate. `initConfig` calls migration-aware `readConfigWithoutMigrate`, applies env/runtime lookup, and swaps `globalServerConfig` under lock.

## State And Persistence Behavior
Current and history configs are objects under `.minio.sys`. If KMS is configured, values are encrypted with context binding to bucket/object path. Global in-memory config is updated after lookup.

## Dependencies And Integration Points
It integrates with object-layer list/read/write/delete, config common helpers, `GlobalKMS`, KMS encryption contexts, madmin config history APIs, json/jsoniter, migration, and runtime config lookup.

## Risks And Test Signals
History listing ignores unreadable/decrypt-failing entries, which favors resilience over strict audit completeness. Missing config silently produces defaults. Encryption context path changes would break decryption. Tests in this subset cover only basic current config initialization and madmin encryption primitives indirectly.
<!-- END_FILE_RESEARCH: sources/object-store/minio/cmd/config.go -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio/cmd/consolelogger.go -->
# sources/object-store/minio/cmd/consolelogger.go

## Purpose
`consolelogger.go` implements an HTTP-accessible console logger target that writes to the normal console sink, buffers recent log messages, publishes live logs to subscribers, and exposes target statistics.

## Important APIs, Types, And Functions
`HTTPConsoleLoggerSys` holds counters, a pubsub bus, console target, node name, and a ring buffer of `defaultLogBufferCount` entries. `NewConsoleLogger` constructs it. `SetNodeName`, `HasLogListeners`, `Subscribe`, `Content`, `Stats`, and `Send` provide the main behavior. It also implements target compatibility methods `Init`, `Endpoint`, `String`, `Cancel`, `Type`, and `IsOnline`.

## Control Flow
When a subscriber arrives and no listeners exist, `Subscribe` adds the logger as a system target. It snapshots up to `last` matching buffered messages under read lock, emits them in order, then registers the live pubsub subscription. `Send` converts `log.Entry` or string entries into `log.Info`, increments counters, publishes to pubsub, appends to the ring, forwards to the console target, and records failures.

## State And Persistence Behavior
State is in memory only: atomic counters, ring buffer, pubsub subscribers, and current node name. No logs are persisted by this file.

## Dependencies And Integration Points
It integrates with MinIO logger targets, madmin log masks, console target output, generic pubsub, distributed-node naming, and admin log streaming/content APIs.

## Risks And Test Signals
Risks include dropped live logs when subscriber channels block, bounded history overwriting older messages, and the `nodeName` parameter to `SetNodeName` being ignored in favor of `globalLocalNodeName` in distributed mode. No direct tests are in this subset; behavior is typically covered by admin log stream integration tests.
<!-- END_FILE_RESEARCH: sources/object-store/minio/cmd/consolelogger.go -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio/cmd/copy-part-range.go -->
# sources/object-store/minio/cmd/copy-part-range.go

## Purpose
`copy-part-range.go` enforces S3 `x-amz-copy-source-range` semantics for multipart UploadPartCopy requests and maps parse/range errors to S3-compatible API responses.

## Important APIs, Types, And Functions
`writeCopyPartErr` translates `errInvalidRange` to `ErrInvalidCopyPartRange`, `errInvalidRangeSource` to `ErrInvalidCopyPartRangeSource`, and unknown errors to `ErrInvalidCopyPartRangeSource` with a custom description. `parseCopyPartRangeSpec` delegates to `parseRequestRangeSpec` but rejects suffix/open-ended/negative ranges. `checkCopyPartRangeWithSize` verifies the parsed range is within the source object size.

## Control Flow
Parsing accepts only explicit `bytes=first-last`; empty range is handled by the shared parser as whole-resource behavior. Size checking is separate so syntactically valid but out-of-resource ranges can produce the source-range error required by S3 compatibility.

## State And Persistence Behavior
No state is persisted. The file only parses request header values and writes HTTP error responses.

## Dependencies And Integration Points
It depends on shared HTTP range parsing, S3 API error code mapping, and copy-object-part handlers that call these helpers before reading source data.

## Risks And Test Signals
Range semantics differ from ordinary HTTP `Range`, so accepting suffix or open-ended forms would violate UploadPartCopy compatibility. `copy-part-range_test.go` covers valid explicit ranges, malformed forms, and out-of-source ranges.
<!-- END_FILE_RESEARCH: sources/object-store/minio/cmd/copy-part-range.go -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio/cmd/copy-part-range_test.go -->
# sources/object-store/minio/cmd/copy-part-range_test.go

## Purpose
`copy-part-range_test.go` verifies strict parsing and source-size validation for `x-amz-copy-source-range`.

## Important APIs, Types, And Functions
`TestParseCopyPartRangeSpec` calls `parseCopyPartRangeSpec`, `HTTPRangeSpec.GetOffsetLength`, and `checkCopyPartRangeWithSize`.

## Control Flow
The test first validates successful ranges against a ten-byte object and checks resulting start/end offsets. It then asserts malformed or unsupported range strings fail parsing. Finally, it checks syntactically valid ranges outside object bounds fail size validation with `errInvalidRangeSource`.

## State And Persistence Behavior
No persistent state is used.

## Dependencies And Integration Points
The test depends on shared range parser behavior and the copy-part-specific helpers. It documents MinIO's expected UploadPartCopy range subset.

## Risks And Test Signals
The suite does not test empty range behavior or HTTP response mapping in `writeCopyPartErr`. It is a strong unit signal for the most error-prone grammar differences from normal HTTP range handling.
<!-- END_FILE_RESEARCH: sources/object-store/minio/cmd/copy-part-range_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio/cmd/crossdomain-xml-handler.go -->
# sources/object-store/minio/cmd/crossdomain-xml-handler.go

## Purpose
`crossdomain-xml-handler.go` provides middleware that serves a Flash/Acrobat-style `crossdomain.xml` policy at `/crossdomain.xml`.

## Important APIs, Types, And Functions
`crossDomainXML` stores the default permissive XML policy matching S3 behavior. `crossDomainXMLEntity` is the request path. `setCrossDomainPolicyMiddleware` wraps an `http.Handler`, serves `globalServerCtxt.CrossDomainXML` when configured, otherwise serves the default XML, and delegates all other paths.

## Control Flow
For every request, the middleware selects the configured/default XML string, compares `r.URL.Path` to `/crossdomain.xml`, writes the XML response and returns on match, or calls the next handler otherwise.

## State And Persistence Behavior
No persistent state is written. It reads `globalServerCtxt.CrossDomainXML`, which is populated from the `--crossdomain-xml` file in `common-main.go`.

## Dependencies And Integration Points
It integrates with the HTTP middleware chain and server context CLI option. It exists for compatibility with legacy cross-domain client behavior.

## Risks And Test Signals
The default policy is permissive. The middleware does not set an explicit content type. `crossdomain-xml-handler_test.go` only checks that `/crossdomain.xml` returns HTTP 200, not body or custom XML behavior.
<!-- END_FILE_RESEARCH: sources/object-store/minio/cmd/crossdomain-xml-handler.go -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio/cmd/crossdomain-xml-handler_test.go -->
# sources/object-store/minio/cmd/crossdomain-xml-handler_test.go

## Purpose
`crossdomain-xml-handler_test.go` smoke-tests the crossdomain middleware route.

## Important APIs, Types, And Functions
`TestCrossXMLHandler` constructs a MinIO mux router, wraps it with `setCrossDomainPolicyMiddleware`, starts an `httptest.Server`, and performs an HTTP GET for `crossDomainXMLEntity`.

## Control Flow
The test does not register any underlying routes; a successful 200 response proves the middleware intercepts `/crossdomain.xml` before the wrapped router handles it.

## State And Persistence Behavior
Only an in-memory HTTP test server is used. No config files or globals are mutated beyond reading defaults.

## Dependencies And Integration Points
It depends on `github.com/minio/mux`, `net/http/httptest`, and the middleware under test.

## Risks And Test Signals
The test does not close the response body, assert XML content, test custom `globalServerCtxt.CrossDomainXML`, or verify pass-through behavior for other paths. It is a minimal route-existence signal.
<!-- END_FILE_RESEARCH: sources/object-store/minio/cmd/crossdomain-xml-handler_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio/cmd/data-scanner-metric.go -->
# sources/object-store/minio/cmd/data-scanner-metric.go

## Purpose
`data-scanner-metric.go` records scanner operation counters, last-minute latency windows, ILM action metrics, active disk paths, current cycle info, and admin-reportable scanner metrics.

## Important APIs, Types, And Functions
`scannerMetric` enumerates realtime and trace-only scanner operations. `scannerMetrics` stores atomic operation counters, locked latency accumulators, lifecycle action counters, current path trackers, and cycle info. Timing helpers include `log`, `timeN`, `time`, `timeSize`, `incTime`, and `timeILM`. `currentPathUpdater`, `getCurrentPaths`, and `activeDrives` expose active scan locations. `setCycle`, `getCycle`, and `report` publish cycle/admin metrics.

## Control Flow
Scanner code wraps operations with returned closures that add counters/latencies when invoked. Trace-only metrics publish scanner traces only when subscribers exist. Current paths are stored per disk in `sync.Map`, with the current string pointer updated atomically. Reports snapshot counters and last-minute windows into `madmin.ScannerMetrics`.

## State And Persistence Behavior
All state is in memory and process-local. Counters are lifetime since process start; cycle completion history is copied from the persisted scanner cycle state but not persisted here.

## Dependencies And Integration Points
It integrates with `data-scanner.go`, lifecycle actions, madmin scanner metrics, global scanner tracing, last-minute latency accumulator types, and `globalLocalNodeName`.

## Risks And Test Signals
The unsafe pointer current-path tracker is intentionally lightweight but relies on careful atomic pointer use. Metrics can be approximate under concurrency. No direct tests are in this subset; scanner tests indirectly exercise ILM paths but not metric reporting.
<!-- END_FILE_RESEARCH: sources/object-store/minio/cmd/data-scanner-metric.go -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio/cmd/data-scanner.go -->
# sources/object-store/minio/cmd/data-scanner.go

## Purpose
`data-scanner.go` implements MinIO's background namespace scanner. It elects one cluster scanner, advances persisted scan cycles, scans disk folders into data-usage caches, applies lifecycle actions, queues healing and replication repair, detects excessive versions/folders, throttles itself dynamically, and emits scanner/audit/event metrics.

## Important APIs, Types, And Functions
`initDataScanner`, `runDataScanner`, `getCycleScanMode`, `readBackgroundHealInfo`, and `saveBackgroundHealInfo` manage cluster-level scanner scheduling and background heal mode. `scanDataFolder` and `folderScanner.scanFolder` perform recursive disk walking, cache compaction, update streaming, and abandoned-child healing checks. `scannerItem`, `sizeSummary`, `getSizeFn`, `applyHealing`, `applyActions`, `evalActionFromLifecycle`, `applyTransitionRule`, expiry helpers, `healReplication`, `dynamicSleeper`, and `auditLogLifecycle` implement object-level side effects and pacing.

## Control Flow
The scanner loop acquires `globalLeaderLock`, reads `dataUsageBloomNamePath`, waits on `scannerCycle`, starts backend usage storage, and calls `objAPI.NSScanner`. Successful cycles increment and persist `currentScannerCycle`. Folder scanning walks disk entries, skips/rescans compacted subtrees by hash/cycle, computes object sizes via injected `getSizeFn`, applies ILM/healing/replication, compacts small or overly broad subtrees, and repairs abandoned objects when erasure healing is enabled.

## State And Persistence Behavior
Persistent state includes scanner cycle data at `dataUsageBloomNamePath`, background heal info at `backgroundHealInfoPath`, and data usage caches saved by companion cache code. Runtime state includes scanner atomics from config, metrics, global heal/expiry/transition queues, events, and audit logs.

## Dependencies And Integration Points
It integrates with object layer `NSScanner`, storage disks, erasure healing, lifecycle evaluator, object lock retention, bucket versioning, replication config, expiry/transition workers, event notification, audit logging, scanner metrics, and `dataUsageCache`.

## Risks And Test Signals
Risks include complex global state, expensive scans on huge prefix trees, subtle compaction/skip behavior, lifecycle side effects during scan, and healing interactions with disk quorum. `data-scanner_test.go` covers noncurrent version expiration under replication/object-lock constraints and lifecycle delete-all/delete-marker evaluation; folder scanning and compaction need broader integration coverage.
<!-- END_FILE_RESEARCH: sources/object-store/minio/cmd/data-scanner.go -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio/cmd/data-scanner_test.go -->
# sources/object-store/minio/cmd/data-scanner_test.go

## Purpose
`data-scanner_test.go` validates lifecycle decisions made by scanner item processing, especially around noncurrent-version expiration, object lock retention, replication purge state, and delete-all/delete-marker lifecycle actions.

## Important APIs, Types, And Functions
`TestApplyNewerNoncurrentVersionsLimit` sets up erasure storage, bucket metadata, lifecycle/versioning config, expiry workers, `scannerItem.applyActions`, and an accounting callback. `TestEvalActionFromLifecycle` calls `evalActionFromLifecycle` for delete-all and delete-marker-expiration rules with and without object locking.

## Control Flow
The first test creates five synthetic object versions, varies retention metadata and replication purge status, runs `applyActions`, captures versions still counted by the accounting callback, drains expiry worker tasks, and compares expected expired versions. The second test parses lifecycle XML policies, creates current object/delete-marker `ObjectInfo`, and asserts resulting lifecycle actions.

## State And Persistence Behavior
The tests create temporary erasure disks, set global object layer and bucket metadata/versioning/expiry systems, and close worker channels. They do not persist external state.

## Dependencies And Integration Points
They integrate with lifecycle XML parsing, versioning XML, object lock, replication config, expiry worker queues, erasure test setup, and scanner accounting behavior.

## Risks And Test Signals
The tests cover key lifecycle correctness but not disk walking, cache compaction, heal queues, replication heal accounting, event/audit output, or dynamic sleeper behavior. They are strong regression signals for avoiding deletion of locked versions or versions pending replication purge.
<!-- END_FILE_RESEARCH: sources/object-store/minio/cmd/data-scanner_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio/cmd/data-usage-cache.go -->
# sources/object-store/minio/cmd/data-usage-cache.go

## Purpose
`data-usage-cache.go` defines MinIO's data-usage cache tree, serialized cache versions, bucket/tier usage aggregation, compaction/merge helpers, hash-based scan scheduling, and object-store load/save behavior for scanner results.

## Important APIs, Types, And Functions
Core types include `dataUsageHash`, `sizeHistogram`, `versionsHistogram`, `dataUsageEntry`, `allTierStats`, `tierStats`, `dataUsageCache`, legacy cache versions V2-V7, `dataUsageCacheInfo`, `dataUsageHashMap`, and `currentScannerCycle`. Entry/cache helpers include `addSizes`, `merge`, `mod`, `modAlt`, `addChild`, `clone`, `find`, `isCompacted`, `findChildrenCopy`, `searchParent`, `deleteRecursive`, `dui`, `replace`, `replaceHashed`, `copyWithChildren`, `reduceChildrenOf`, `forceCompact`, `flatten`, histogram conversion, `tiersUsageInfo`, `bucketsUsageInfo`, `sizeRecursive`, `merge`, `load`, `save`, `serializeTo`, `deserialize`, and `hashPath`.

## Control Flow
Scanner code builds/updates a tree keyed by cleaned path hashes. Recursive helpers copy or flatten children, compact least-useful subtrees when limits are exceeded, remove unreachable entries, merge per-drive roots, and convert flattened data into `DataUsageInfo`. Load first tries bucket metadata cache, falls back to the older `dataUsageBucket`, retries primary/backup objects, and ignores missing caches. Save serializes to zstd-compressed msgp with a version byte, writes the primary object, and best-effort writes a backup.

## State And Persistence Behavior
Caches are persisted as versioned compressed objects under `.minio.sys/buckets/...` via `saveConfig`; backups use `name + ".bkp"`. Saves are concurrency-limited to four. Deserialization migrates V2-V7 schemas to current version 8, including histogram conversion from V1 intervals.

## Dependencies And Integration Points
It integrates with scanner folder compaction, data usage admin reports, object-layer config I/O, msgp code generation, zstd compression, xxhash scheduling, bytebuffer pooling, bucket/tier metadata, lifecycle config references in cache info, and current scanner cycle metrics.

## Risks And Test Signals
Risks include cache corruption from lockless reads/writes, best-effort backup save errors being deferred/ignored, path-hash/key assumptions, expensive recursive flattening on huge trees, and migration gaps when cache versions change. There are no direct tests in this subset; behavior is indirectly exercised by scanner and data usage integration tests.
<!-- END_FILE_RESEARCH: sources/object-store/minio/cmd/data-usage-cache.go -->
