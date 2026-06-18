# sources/storage-engines/foundationdb/fdbclient subset-b-008431 research

Work item `subset-b-008431` covers four FoundationDB fdbclient files:

- `sources/storage-engines/foundationdb/fdbclient/DatabaseContext.cpp`
- `sources/storage-engines/foundationdb/fdbclient/FDBAWSCredentialsProvider.cpp`
- `sources/storage-engines/foundationdb/fdbclient/FDBAWSCredentialsProvider.h`
- `sources/storage-engines/foundationdb/fdbclient/FDBTypes.cpp`

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbclient/DatabaseContext.cpp -->
# sources/storage-engines/foundationdb/fdbclient/DatabaseContext.cpp

## Purpose

`DatabaseContext.cpp` implements a large part of the native FoundationDB client database context. It owns client-side state shared by transactions, watches, GRV caching, special key-space registration, client status reporting, TSS request duplication/mismatch handling, storage-server interface caching, health metric caching, and periodic trace counters. It is the concrete runtime backing for `Database` references created from client cluster metadata or from an internal server-side `ClientDBInfo`.

The file is actor-heavy. Long-lived actors run beside the context to log metrics, monitor proxy set changes, publish sampled client transaction status, and react to TSS mismatches. The destructor cancels those actors and breaks reference cycles explicitly, so lifetime and cancellation semantics are part of the implementation contract.

## Important APIs, types, and functions

- Watch metadata API:
  - `DatabaseContext::getWatchMetadata()`, `setWatchMetadata()`, `deleteWatchMetadata()` maintain `watchMap`.
  - `increaseWatchRefCount()` and `decreaseWatchRefCount()` maintain `watchCounterMap` by `WatchMapKey` and `Version`. When the last version reference goes away, `decreaseWatchRefCount()` cancels `WatchMetadata::watchFutureSS` and removes metadata to avoid a future waiting on state that keeps itself alive.
- TSS state:
  - `addTssMapping()` maps a storage server UID to a TSS interface, creates `TSSMetrics`, and updates `queueModel` endpoint duplication for data and non-data storage RPC endpoints.
  - `removeTssMapping()` removes the mapping and removes all duplicated queue-model endpoints.
  - `tssLogger()` periodically traces per-pair metrics, latency sketches, and error histograms, then clears the sample window.
  - `handleTssMismatches()` consumes `tssMismatchStream`, writes mismatch evidence to system key-backed maps, and either quarantines or kills the TSS by setting `tssQuarantineKeyFor()` or clearing `serverTagKeyFor()`.
- Version-vector and read-version cache:
  - `addSSIdTagMapping()`, `getLatestCommitVersionForSSID()`, `getLatestCommitVersion()`, and `getLatestCommitVersions()` expose storage-server commit-version information from `ssVersionVectorCache`.
  - `updateCachedReadVersion()`, `getCachedReadVersion()`, and `getLastGrvTime()` update/read the GRV cache either from context fields or from `DatabaseSharedState` under a mutex.
  - `validateVersion()` rejects version `0`, old versions after a switchable cluster changed, and invalid versions except `latestVersion`.
- Storage server interface cache:
  - `StorageServerInfo::getInterface()` interns `StorageServerInterface` objects by server UID in `DatabaseContext::server_interf`, updating an interface in place when only the endpoint token changes and replacing it when locality changes.
  - `StorageServerInfo::~StorageServerInfo()` unregisters itself from the context unless the context already called `notifyContextDestroyed()`.
- Health and special keys:
  - `getHealthMetricsActor()`, `DatabaseContext::getHealthMetrics()`, and `getStorageStats()` cache aggregate and detailed health metrics from GRV proxies.
  - `SingleSpecialKeyImpl` adapts a single-key async getter into a `SpecialKeyRangeReadImpl`.
  - `HealthMetricsRangeImpl` exposes aggregate, tlog, and storage health JSON under `\xff\xff/metrics/health/`.
  - `registerSpecialKeysImpl()` registers module implementations conditionally on API version and deprecation version.
- Client status persistence:
  - `TrInfoChunk` stores chunk key/value pairs for persisted client latency/status payloads.
  - `transactionInfoCommitActor()` writes chunks with `SetVersionstampedKey` and updates `client_latency_counter/`.
  - `delExcessClntTxnEntriesActor()` trims old `client_latency/` entries based on a byte counter and configured limit.
  - `clientStatusUpdateActor()` drains `clientStatusUpdater.inStatusQ`, chunks large values under `VALUE_SIZE_LIMIT`, commits bounded transaction batches, samples cleanup through global config, and explicitly resets `Transaction` objects to release context references.
- Proxy-change validation:
  - `assertFailure()` and `attemptGRVFromOldProxies()` send causal-read-risky GRV requests to old GRV proxies and assert if an old proxy still returns a read version after a recovery that has completed.
  - `monitorClientDBInfoChange()` watches `ClientDBInfo`, triggers proxy-change notifications, clears `ssVersionVectorCache`, and probabilistically runs the old-proxy GRV check.
- Lifecycle:
  - The primary `DatabaseContext` constructor initializes counters, caches, actors, `GlobalConfig`, `SpecialKeySpace`, special-key implementations gated by API version, and periodic throttle expiry.
  - The error constructor builds a context that carries `deferredError`.
  - `DatabaseContext::create()` is the server/internal factory.
  - The destructor cancels background actors, releases shared state, notifies cached `StorageServerInfo` objects, clears location cache, and traces destruction.

## Control flow

Initialization starts in the main constructor. It records connection/client metadata, initializes counters and latency sketches, sets the initial `connected` future based on proxy availability, sizes metadata and location caches from knobs, starts `databaseLogger() && tssLogger()`, starts `monitorClientDBInfoChange()`, `handleTssMismatches()`, and `clientStatusUpdateActor()`, constructs `GlobalConfig`, and registers special key-space implementations according to API version gates (`>= 740`, `>= 700`, `>= 630`) and deprecation gates.

Read-version cache updates are monotonic. Both shared and local cache paths only accept a version greater than or equal to the cached version. Time is updated only if the request start time is newer than the last GRV time. Consumers use `getCachedReadVersion()` and `getLastGrvTime()` with shared-state locking when applicable.

Latest commit-version calculation starts from `LocationInfo` storage-server IDs. `getLatestCommitVersions()` only returns data if the read version came from a GRV proxy and the version-vector cache has data. It validates that the read version is not newer than the cache maximum unless GRV cache use makes that expected. It groups tags by commit version and writes an ordered `VersionVector`.

Client status reporting loops forever. Each cycle waits for a connected database, refreshes a transaction, swaps the input status queue into an output queue, splits serialized status payloads into versionstamped chunks, commits chunks in bounded batches, handles `transaction_too_large` by halving the batch byte limit, samples cleanup according to global config, resets the transaction, and sleeps. Errors are traced; cancellation is rethrown, and non-cancellation failures delay before retry.

TSS mismatch handling is event driven. The actor reads detailed mismatch batches from `tssMismatchStream`, finds the paired source storage server in `tssMapping`, builds a `ReadYourWritesTransaction` with system-key access, updates quarantine/kill state and mismatch maps, retries through `onError()`, and releases the transaction reference after success or bounded retries.

`monitorClientDBInfoChange()` keeps snapshots of current commit and GRV proxy vectors. On changes it may launch old-proxy GRV validation, updates snapshots, clears storage-server version-vector cache because a recovery may invalidate prior commit-version data, and triggers `proxiesChangeTrigger`.

## State and persistence behavior

Most state is process-local:

- `watchMap`, `watchCounterMap`, `outstandingWatches`, and `maxOutstandingWatches` track client watch lifecycle.
- `tssMapping`, `tssMetrics`, `queueModel`, and `tssMismatchStream` track TSS request duplication and mismatch handling.
- `server_interf` interns `StorageServerInfo` objects and must be emptied or detached on context destruction.
- `cachedReadVersion`, `lastGrvTime`, and optionally `DatabaseSharedState::grvCacheSpace` hold GRV cache state.
- `ssidTagMapping` and `ssVersionVectorCache` are local caches of storage-server tag/version data.
- `healthMetrics`, `healthMetricsLastUpdated`, and `detailedHealthMetricsLastUpdated` cache health metrics.
- `clientStatusUpdater` queues serialized status payloads and owns its writer actor.
- Numerous `Counter` and `DDSketch` members accumulate telemetry until `databaseLogger()` and `tssLogger()` flush and clear samples.

Persistent cluster state is touched through transactions and system key ranges:

- Client transaction profiling data is persisted under `fdbClientInfoPrefixRange` with `client_latency/` entries and a `client_latency_counter/` byte counter.
- TSS mismatch/quarantine handling writes `tssMappingKeys`, `tssMismatchKeys`, `tssQuarantineKeyFor()`, and `serverTagKeyFor()` related system keys.
- Special-key implementations expose and, for management/configuration modules, mutate system state through their own implementation classes registered here.

## Dependencies and integration points

This file sits at the center of fdbclient. It depends on `NativeAPI.actor.h`, `DatabaseContext.h`, transaction classes, `ClusterInterface`, GRV and commit proxy interfaces, `StorageServerInterface`, `SpecialKeySpace`, `GlobalConfig`, key-backed maps, system key definitions, tracing, flow actors/futures, locality data, and client knobs. It integrates with the load balancer through `queueModel`, with server recovery metadata through `ClientDBInfo`, with client APIs through `Database`/`Transaction`, with status JSON through `getJSON()`, and with special key-space modules for management, metrics, configuration, tracing, actor lineage, profiler configuration, worker interfaces, connection strings, cluster ID, and transaction conflict introspection.

The TSS path integrates storage-server RPC endpoint tokens with test storage server endpoints. The health metrics path integrates `GrvProxyInterface::getHealthMetrics`. The client status path depends on `GlobalConfig` keys `fdbClientInfoTxnSampleRate` and `fdbClientInfoTxnSizeLimit`, plus knobs for payload and transaction byte limits.

## Risks and edge cases

- Lifetime cycles are a recurring risk. Comments call out why `clientStatusUpdateActor()` takes a raw `DatabaseContext*`, why `Transaction` objects are reset, and why watch futures are manually cancelled when the last reference disappears.
- `StorageServerInfo::getInterface()` mutates an interned `StorageServerInterface` in place when locality is unchanged. The comment notes that load balancing holds pointers into interface members, making this technically correct but unnatural and fragile.
- Version-vector logic asserts in simulation when a read version is newer than the version-vector maximum, but production avoids returning stale commit versions. Incorrect GRV-cache flags could suppress useful latest-commit-version data.
- Client status persistence relies on byte accounting through a counter updated by atomic add operations. Bugs in key/value size accounting or versionstamped-key layout could make cleanup delete too much or too little profiling data.
- TSS mismatch handling gives up after bounded retries, so persistent transaction failures can leave mismatch evidence/quarantine state unwritten until another mismatch or operator action.
- `removeTssMapping()` erases `tssMetrics` by the storage-server ID even though `addTssMapping()` stores metrics by TSS ID; this deserves caution when changing this code because an ID mismatch could leave stale metric entries.
- The AWS or special-key dependencies are not in this file, but constructor registration means API-version gates and deprecation gates are observable client behavior.
- Health metrics output returns empty under `CLIENT_BUGGIFY`, and detailed metrics are only refreshed when detail-specific staleness requires it.

## Test signals

There are no `TEST_CASE` blocks in this file. Test coverage is likely through NativeAPI, special key-space, client status, status JSON, TSS simulation, recovery, and transaction tests elsewhere. Useful test signals for changes here include watch cancellation/reference-count tests, GRV cache monotonicity tests, proxy recovery simulation that exercises `attemptGRVFromOldProxies()`, TSS mismatch quarantine/kill simulation, special key-space API-version compatibility tests, and client transaction profiling size-limit cleanup tests.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbclient/DatabaseContext.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbclient/FDBAWSCredentialsProvider.cpp -->
# sources/storage-engines/foundationdb/fdbclient/FDBAWSCredentialsProvider.cpp

## Purpose

`FDBAWSCredentialsProvider.cpp` provides the FoundationDB client helper for retrieving AWS credentials when the build enables AWS backup support. The implementation is compiled only under `WITH_AWS_BACKUP`.

## Important APIs, types, and functions

- Namespace: `FDBAWSCredentialsProvider`.
- Function: `Aws::Auth::AWSCredentials getAwsCredentials()`.
- It uses `Aws::SDKOptions`, `Aws::InitAPI()`, `Aws::Auth::DefaultAWSCredentialsProviderChain`, and `TraceEvent`.

## Control flow

`getAwsCredentials()` uses a function-local static `bool doneInit` to initialize the AWS SDK once per process. On the first call it sets the flag, constructs default SDK options, calls `Aws::InitAPI(options)`, and emits `AWSSDKInitSuccessful`. Every call then constructs a default AWS credentials provider chain, asks it for credentials, and returns the resulting `Aws::Auth::AWSCredentials`.

The code intentionally does not call `Aws::ShutdownAPI()`. The comment explains that the AWS SDK is intended to live for the lifetime of the process.

## State and persistence behavior

The only local state is `doneInit`, which persists for the lifetime of the process. Credentials are not cached by this wrapper; it delegates caching/refresh behavior to the AWS SDK's default provider chain. No FoundationDB keys or files are written.

## Dependencies and integration points

The source includes `FDBAWSCredentialsProvider.h` and `fdbclient/Tracing.h`. Through the header it depends on AWS SDK core and auth provider-chain headers. Callers in backup/blob-store code can use this helper to obtain credentials without managing AWS SDK initialization themselves.

## Risks and edge cases

- `doneInit` is a plain function-local static boolean, not an atomic or `std::call_once`. In modern C++, initialization of the static variable itself is thread-safe, but writes to the bool are not protected if multiple threads enter the function concurrently after construction.
- If `Aws::InitAPI()` fails or has side effects that depend on options, this wrapper has no error path and no retry path.
- The process never shuts down the AWS SDK, by design. That avoids teardown ordering problems but can leak SDK-global resources until process exit.
- The default provider chain can read environment, profile, metadata, and other AWS-standard sources; behavior depends on deployment environment rather than FoundationDB configuration in this file.

## Test signals

There are no local tests. Coverage should come from AWS-backup builds and backup integration tests that verify credentials can be resolved from the expected default AWS provider sources. A targeted unit test would need to compile with `WITH_AWS_BACKUP` and control the AWS SDK credential environment.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbclient/FDBAWSCredentialsProvider.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbclient/FDBAWSCredentialsProvider.h -->
# sources/storage-engines/foundationdb/fdbclient/FDBAWSCredentialsProvider.h

## Purpose

`FDBAWSCredentialsProvider.h` declares the AWS credentials helper used by FoundationDB backup-related code when AWS backup support is enabled. The entire header content is guarded by `WITH_AWS_BACKUP`, so projects that do not build AWS backup support do not include AWS SDK declarations through this header.

## Important APIs, types, and functions

- Header guard: `FDB_AWS_CREDENTIALS_PROVIDER_H`, active only when `WITH_AWS_BACKUP` is defined.
- Includes:
  - `aws/core/Aws.h`
  - `aws/core/auth/AWSCredentialsProviderChain.h`
- Namespace: `FDBAWSCredentialsProvider`.
- Declaration: `Aws::Auth::AWSCredentials getAwsCredentials();`

## Control flow

The header has no runtime control flow. Preprocessor control flow is important: the outer guard is `#if (!defined FDB_AWS_CREDENTIALS_PROVIDER_H) && (defined WITH_AWS_BACKUP)`, followed by a redundant inner `#ifdef WITH_AWS_BACKUP`. If `WITH_AWS_BACKUP` is absent, the header expands to no declarations and no includes.

## State and persistence behavior

The header declares no state and performs no persistence. Runtime state lives in the `.cpp` implementation's one-time AWS SDK initialization flag and in AWS SDK internals.

## Dependencies and integration points

This header is a narrow boundary between fdbclient code and the AWS SDK. It allows AWS-dependent callers to request credentials without directly duplicating initialization logic. Because the declaration itself disappears when `WITH_AWS_BACKUP` is not defined, callers must also be conditionally compiled or otherwise avoid referencing `FDBAWSCredentialsProvider::getAwsCredentials()` in non-AWS builds.

## Risks and edge cases

- The conditional header guard means accidental inclusion in non-AWS builds silently provides no declaration. That is fine for guarded callers but can lead to confusing compile errors if a caller forgets its own `WITH_AWS_BACKUP` guard.
- The inner `#ifdef WITH_AWS_BACKUP` is redundant with the outer guard, but harmless.
- This header exposes AWS SDK types directly, so ABI and include-path compatibility are coupled to the configured AWS SDK.

## Test signals

There are no local tests. Build matrix coverage is important: one build with `WITH_AWS_BACKUP` should compile AWS SDK includes and the declaration, and one build without it should compile callers that correctly exclude AWS-specific use.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbclient/FDBAWSCredentialsProvider.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbclient/FDBTypes.cpp -->
# sources/storage-engines/foundationdb/fdbclient/FDBTypes.cpp

## Purpose

`FDBTypes.cpp` implements small but shared fdbclient type utilities for key ranges, key selectors, key-value-store type names, and perpetual storage wiggle locality parsing/matching. These helpers sit below higher-level transaction and storage configuration code and encode behavior that must stay compatible with FoundationDB key-size limits and configuration strings.

## Important APIs, types, and functions

- Key range utilities:
  - `toPrefixRelativeRange(KeyRangeRef range, Optional<KeyRef> prefix)` converts an absolute range into a prefix-relative range, returning `allKeys` boundaries where the absolute boundary is outside the prefix.
  - `keyBetween(const KeyRangeRef& keys)` returns a compact key at or near the range end, capped by `CLIENT_KNOBS->SPLIT_KEY_SIZE_LIMIT`, useful for split keys.
  - `randomKeyBetween(const KeyRangeRef& keys)` attempts to produce a deterministic-random key strictly inside a non-empty, non-single-key range, falling back to `keys.end` if no valid interior key can be produced.
- Key selector methods:
  - `KeySelectorRef::setKey()` truncates oversized keys to a maximum legal key-selector representation using `getMaxKeySize()`.
  - `KeySelectorRef::setKeyUnlimited()` stores a key without truncation.
  - `KeySelectorRef::toString()` renders selectors in first-greater/first-greater-or-equal/last-less/last-less-or-equal form based on `offset` and `orEqual`.
- Description overloads:
  - `describe(const std::string&)` returns the string as-is.
  - `describe(const UID&)` returns `UID::shortString()`.
- Store type mapping:
  - `KeyValueStoreType::getStoreTypeStr()` maps enum values to storage engine strings such as `ssd-2`, `ssd-redwood-1`, `ssd-rocksdb-v1`, `ssd-sharded-rocksdb`, `memory`, and `memory-radixtree`.
  - `KeyValueStoreType::fromString()` parses accepted names and aliases such as `ssd` and `redwood`, throwing `unknown_storage_engine()` for unknown input.
- Perpetual storage wiggle locality:
  - `ParsePerpetualStorageWiggleLocality()` parses semicolon-separated `key:value` locality filters, with `"0"` meaning no filters.
  - `localityMatchInList()` returns true if any parsed key/value pair matches a `LocalityData` value.

## Control flow

`toPrefixRelativeRange()` has a simple three-way behavior: no prefix returns the original range; prefixed boundaries have the prefix stripped; non-prefixed begin/end boundaries widen to `allKeys.begin` or `allKeys.end`.

`keyBetween()` scans common bytes between `begin` and `end` until a differing byte or `SPLIT_KEY_SIZE_LIMIT`. If a differing byte is found, it returns the end prefix through that byte. If begin is a prefix of a longer end and one more byte is allowed, it returns one more end byte; otherwise it returns `end`.

`randomKeyBetween()` first handles empty or single-key ranges by returning `end`. If `begin` is shorter than `end`, it appends a random byte constrained by the corresponding `end` byte. Otherwise it finds the first differing byte, tries to mutate a later non-`0xff` byte upward, then tries to choose a byte between the differing begin/end bytes, then appends a byte if key-size limits allow, finally returning `end` when no interior key is possible.

`KeyValueStoreType::fromString()` uses a static map and throws when the string is absent. `getStoreTypeStr()` uses a switch and returns `"unknown"` for unexpected enum values.

`ParsePerpetualStorageWiggleLocality()` asserts the input passes `isValidPerpetualStorageWiggleLocality()`, treats `"0"` as an empty match list, splits on `;`, then splits each item on `:` into `Optional<Value>` key/value pairs. `localityMatchInList()` scans those pairs and checks `LocalityData::get(key) == value`.

## State and persistence behavior

This file has no persistent state and does not access disk or FoundationDB keys. The only static runtime state is the local `names` map in `KeyValueStoreType::fromString()`. Random key generation uses `deterministicRandom()`, so it participates in FoundationDB's deterministic simulation behavior rather than external nondeterminism.

## Dependencies and integration points

The file includes `fdbclient/FDBTypes.h`, `fdbclient/Knobs.h`, `fdbclient/NativeAPI.actor.h`, and Boost string splitting. It depends on client knobs for key-size and split-key limits, `LocalityData` for locality matching, `UID` formatting, FoundationDB `KeyRef`/`KeyRangeRef`/`ValueRef` arena-backed string types, and the error factory `unknown_storage_engine()`.

Storage engine string mapping is an integration point for configuration and process/storage initialization. Locality parsing is used by perpetual storage wiggle configuration to target storage processes by locality fields. Key/range utilities are shared primitives for splitting, selector rendering, and prefix-range calculations.

## Risks and edge cases

- `randomKeyBetween()` has several fallback paths that return `keys.end`, so callers must tolerate the result not being strictly inside the range for empty, single-key, or saturated key-space cases.
- The branch where `begin.size() < end.size()` reads `end[begin.size()]`; this relies on `begin < end` and the size relation to make that index valid.
- `KeySelectorRef::setKey()` truncation is intentional but can surprise callers comparing stringified selectors to original oversized input.
- `KeyValueStoreType::getStoreTypeStr()` returns `"unknown"` for default enum cases, while `fromString()` throws for unknown strings. Round-trip behavior is therefore only guaranteed for known enum values.
- `ParsePerpetualStorageWiggleLocality()` uses `ASSERT` validation rather than returning an error, so invalid strings are expected to be rejected before calling it or will abort in assert-enabled contexts.
- Parsed `ValueRef` objects reference bytes from `localityKeyValues.c_str()`. Because they are stored as `Optional<Value>` rather than `Optional<ValueRef>`, this should deep-copy into owned values; preserving that ownership property is important if the type changes.

## Test signals

This file contains inline unit tests:

- `/KeyRangeUtil/randomKeyBetween` validates interior-key generation for prefix and non-prefix ranges and verifies the no-interior-key fallback for `q` to `q\x00`.
- `/KeyRangeUtil/KeyRangeComplement` validates subtracting subranges from a parent range across middle, outside, overlapping-left, overlapping-right, and covering cases.
- `/PerpetualStorageWiggleLocality/Validation` validates accepted and rejected locality filter strings, including multi-filter and `"0"` cases.
- `/PerpetualStorageWiggleLocality/ParsePerpetualStorageWiggleLocality` validates parsed key/value pairs and matching behavior against `LocalityData`.

Additional useful tests would cover `toPrefixRelativeRange()`, `keyBetween()` at `SPLIT_KEY_SIZE_LIMIT`, key selector truncation/string rendering, and storage engine string aliases/error behavior.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbclient/FDBTypes.cpp -->
