# Research: subset-b-008190

<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio/cmd/endpoint.go -->
## sources/object-store/minio/cmd/endpoint.go

Purpose: Defines MinIO server endpoint modeling and endpoint/pool construction for single-drive, local erasure, and distributed erasure deployments. It converts CLI layout strings into normalized `Endpoint` values, resolves locality, assigns pool/set/disk indexes, detects invalid topologies, and exposes peer/proxy helpers used by server startup and grid routing.

Important APIs/types/functions: `EndpointType`, `Endpoint`, `Node`, `ProxyEndpoint`, `PoolEndpoints`, `EndpointServerPools`, `Endpoints`, and `PoolEndpointList` are the main types. `NewEndpoint` parses either a filesystem path or URL endpoint, rejects empty/root paths, validates URL scheme/host/port/query shape, normalizes paths, and initializes indexes to `-1`. `NewEndpoints` enforces homogeneous endpoint style and scheme and rejects duplicates. `CreatePoolEndpoints` is the central layout builder: it validates the server address, handles single-drive path-only setups, expands pool/set layouts, runs cross-device checks, resolves local endpoints, assigns indexes, checks duplicate/local path conflicts, fills missing ports, computes setup type, and updates `globalDomainIPs` unless public IPs are configured. Peer helpers include `GridHosts`, `FindGridHostsFromPeer*`, `Hostnames`, `peers`, `GetLocalPeer`, and proxy helpers.

Control flow: Endpoint creation starts with syntax normalization, then locality is discovered through `UpdateIsLocal` on either an `Endpoints` slice or grouped `PoolEndpointList`. Locality resolution loops until at least one local endpoint is found or all endpoints resolve, with special retry behavior in orchestrated deployments and `_MINIO_SERVER_LOCAL` override support. `CreatePoolEndpoints` then validates topology invariants after locality is known, because local/remote classification affects duplicate path and port checks. State behavior is mostly in-memory but mutates global process state through `globalDomainIPs` and relies on global network/TLS/server-port values.

Dependencies and integration points: Uses `net`, `url`, `path/filepath`, `mountinfo.CheckCrossDevice`, MinIO config errors, `env`, MinIO set utilities, local IP/DNS helpers, and process globals such as `orchestrated`, `globalMinioPort`, `globalMinioHost`, `globalIsTLS`, and `globalOSSignalCh`. Startup code, object-layer initialization, grid host selection, proxying, and tests construct or consume these endpoint lists.

Risks: DNS/locality logic is environment-sensitive and can wait indefinitely in orchestrated mode until hostnames stop resolving to localhost. Topology validation depends on consistent `isLocalHost` and DNS results. `GetLocalPeer` returns an arbitrary set slice element if multiple local peers exist. The same-path validation is skipped for orchestrated/reverse-proxy cases, leaving those deployments to external correctness. Windows path handling and URL path cleaning are subtle.

Test signals: Covered by endpoint unit tests for parsing, homogeneous endpoint lists, pool creation, local/remote peer selection, and domain IP filtering. The implementation also contains startup-facing branches that depend on real network interfaces, DNS, and orchestrated flags, so tests are partly environment-sensitive.
<!-- END_FILE_RESEARCH: sources/object-store/minio/cmd/endpoint.go -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio/cmd/endpoint_contrib_test.go -->
## sources/object-store/minio/cmd/endpoint_contrib_test.go

Purpose: Contributed test coverage for endpoint-domain IP derivation. It verifies that `updateDomainIPs` records only non-loopback, non-localhost addresses with the correct port normalization.

Important APIs/types/functions: `TestUpdateDomainIPs` saves/restores `globalMinioPort` and `globalDomainIPs`, then feeds `set.StringSet` endpoint inputs into `updateDomainIPs`. Cases cover empty input, localhost-only input, hostnames/IPs without ports, and mixed explicit/default ports.

Control flow and state: The test mutates global endpoint-related variables in a scoped manner. Each case resets `globalDomainIPs`, calls the production helper, and compares the resulting set to the expected set.

Dependencies and integration points: Depends on `github.com/minio/minio-go/v7/pkg/set` and the `endpoint.go` helper. It is an integration signal for cluster bootstrap because `globalDomainIPs` is later used for domain/IP awareness.

Risks: The test uses literal private IPv4 values and does not exercise DNS hostnames, IPv6, or failure paths from `getHostIP`. It is sensitive to global-state cleanup, which it handles with defers.

Test signals: Strongly validates default port behavior and loopback filtering for IPv4-style endpoint inputs.
<!-- END_FILE_RESEARCH: sources/object-store/minio/cmd/endpoint_contrib_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio/cmd/endpoint_test.go -->
## sources/object-store/minio/cmd/endpoint_test.go

Purpose: Unit and topology tests for endpoint parsing, endpoint-list validation, pool endpoint creation, and peer discovery. These tests encode the expected behavior for local erasure versus distributed erasure setup selection.

Important APIs/types/functions: `TestNewEndpoint` validates path and URL parsing plus error messages for empty roots, bad schemes, bad query fragments, invalid ports, empty hosts, root URL paths, and IP-without-scheme input. `TestNewEndpoints` checks duplicate detection and mixed style/scheme rejection. `TestCreateEndpoints` drives `mergeDisksLayoutFromArgs` and `CreatePoolEndpoints` through single-drive path setup, URL-only local setups, distributed setups, path conflicts, same-host different-port conflicts, and local host naming conflicts. `TestGetLocalPeer` and `TestGetRemotePeers` validate peer selection.

Control flow and state: Tests temporarily set `globalMinioPort`, use local non-loopback IP discovery, build expected `url.URL` values, and compare endpoint strings/setup types. The tests run through real endpoint normalization and locality detection paths rather than stubbing all network behavior.

Dependencies and integration points: Integrates with server context layout parsing, setup type constants, `mustGetPoolEndpoints`, local IP discovery, and endpoint peer APIs from `endpoint.go`. It also exercises config-error wrapping through expected error strings.

Risks: Tests may skip or fail on hosts without a non-loopback IPv4 address. Because locality resolution depends on host/network behavior, assertions around local flags are tied to the test environment. The tests mostly compare strings and setup types, not every index field.

Test signals: Provides broad regression coverage for endpoint bootstrap rules, especially error text and topology invariants that operators see during startup.
<!-- END_FILE_RESEARCH: sources/object-store/minio/cmd/endpoint_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio/cmd/erasure-coding.go -->
## sources/object-store/minio/cmd/erasure-coding.go

Purpose: Wraps Reed-Solomon erasure coding parameters and shard math for MinIO object data. It centralizes construction, shard sizing, encode/decode primitives, and a startup self-test that detects incompatible erasure algorithm behavior.

Important APIs/types/functions: `Erasure` stores a lazy `reedsolomon.Encoder` factory plus `dataBlocks`, `parityBlocks`, and `blockSize`. `NewErasure` validates shard counts, rejects more than 256 total shards, and creates the encoder lazily with `WithAutoGoroutines`. `EncodeData` splits and encodes a block into data/parity shards. `DecodeDataBlocks` reconstructs only missing data shards, with a zero-length fast path. `DecodeDataAndParityBlocks` reconstructs all shards. `ShardSize`, `ShardFileSize`, and `ShardFileOffset` translate object/block offsets to shard-file sizing. `erasureSelfTest` hashes known encoded outputs and reconstructs a deleted shard across many data/parity configurations.

Control flow and state: The only persistent state is the in-memory lazy encoder captured behind `sync.Once`. The self-test is process-startup validation: on mismatch it writes diagnostics and uses `logger.Fatal`, preventing server startup rather than risking data corruption.

Dependencies and integration points: Depends on `github.com/klauspost/reedsolomon`, `xxhash`, MinIO block-size constants, erasure algorithm enums, and logger fatal behavior. Encode/decode/heal stream implementations call this wrapper for block-level operations.

Risks: The lazy encoder closure shares the outer `err` variable from `NewErasure`; errors are expected to be impossible after earlier validation and become panics inside `Once`. Shard offset math is critical for ranged reads and last-block handling. Any upstream Reed-Solomon behavior change will trip the self-test.

Test signals: Direct tests are in encode/decode/heal suites, while `erasureSelfTest` is an internal runtime safety net with known hashes.
<!-- END_FILE_RESEARCH: sources/object-store/minio/cmd/erasure-coding.go -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio/cmd/erasure-common.go -->
## sources/object-store/minio/cmd/erasure-common.go

Purpose: Provides utility methods on `erasureObjects` to select currently usable disks, especially local disks and non-healing online disks.

Important APIs/types/functions: `getOnlineDisks` randomizes disk order, concurrently calls `DiskInfo`, and excludes nil, inaccessible, and currently-healing disks. `getOnlineLocalDisks` filters the online set to local disks in randomized order. `getLocalDisks` returns local disks without probing `DiskInfo`.

Control flow and state: Disk probing uses goroutines, a mutex-protected result slice, and per-call random permutation seeded by current time. It does not persist state; it observes disk health through `StorageAPI.DiskInfo` and `IsLocal`.

Dependencies and integration points: Relies on `erasureObjects.getDisks`, `StorageAPI`, `DiskInfoOptions`, and `IsLocal`. Used by healing/listing code to avoid consuming unreachable or currently healing disks.

Risks: Random result ordering intentionally spreads load but can make behavior less deterministic. `getOnlineDisks` uses `context.Background`, so it does not honor caller cancellation. A disk transiently reporting `Healing` is skipped from selection.

Test signals: Coverage is indirect through healing/listing tests that rely on disk selection behavior.
<!-- END_FILE_RESEARCH: sources/object-store/minio/cmd/erasure-common.go -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio/cmd/erasure-decode.go -->
## sources/object-store/minio/cmd/erasure-decode.go

Purpose: Implements erasure-coded object reads and shard repair reads. It reads shards in parallel, reconstructs missing data, supports ranged reads, and heals missing/corrupt shards by reconstructing full data/parity blocks.

Important APIs/types/functions: `parallelReader` tracks `io.ReaderAt` sources, original reader positions, shard offsets/sizes, per-disk buffers, preferred-reader remapping, and pooled stash buffers. `newParallelReader` initializes shard offsets and optionally slices a global byte pool. `preferReaders` moves preferred disks earlier while preserving output buffer mapping. `Read` launches enough concurrent reads to satisfy data-block quorum, retries alternate readers on nil/error readers, marks original readers nil on failure, and returns reconstructable buffers plus expected heal signals (`errFileNotFound` or `errFileCorrupt`). `Erasure.Decode` validates range arguments, iterates erasure blocks, reconstructs data blocks, writes requested subranges with `writeDataBlocks`, and returns a deferred heal signal when data was readable but some source shard was missing/corrupt. `Erasure.Heal` reconstructs data and parity blocks and writes them through `multiWriter`.

Control flow and state: Reads are block-oriented. For each erasure block, `parallelReader.Read` advances shard offset only if enough shards are available to decode. `Decode` calculates block-relative offsets for first/middle/last blocks and checks the final written byte count. `Heal` walks all blocks from zero to object length and writes reconstructed shards to supplied writers with write quorum 1.

Dependencies and integration points: Uses bitrot reader implementations through `io.ReaderAt`, global byte-pool capacity, `writeDataBlocks`, `multiWriter`, erasure math from `erasure-coding.go`, and MinIO error values. Healing code calls `Erasure.Heal` after it builds bitrot readers/writers for specific object parts.

Risks: Concurrency is coordinated through a buffered trigger channel and goroutines; incorrect reader-to-buffer mapping would corrupt shard positions. Returned `errFileNotFound`/`errFileCorrupt` can be non-fatal and signal a heal need, so callers must not treat every non-nil decode error the same. Range math around block boundaries and last shard size is fragile.

Test signals: Decode tests cover many data/parity/offline combinations, range offsets/lengths, quorum failures, invalid arguments, random ranges, and benchmarks.
<!-- END_FILE_RESEARCH: sources/object-store/minio/cmd/erasure-decode.go -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio/cmd/erasure-decode_test.go -->
## sources/object-store/minio/cmd/erasure-decode_test.go

Purpose: Validates `Erasure.Decode` correctness and performance across erasure layouts, bitrot algorithms, offline/faulty disks, and ranged reads.

Important APIs/types/functions: Extends `badDisk` with `ReadFile` failure behavior. `erasureDecodeTests` enumerates data-block counts, total disks, offline disks, block sizes, object sizes, offsets, lengths, algorithms, and expected failure/quorum behavior. `TestErasureDecode` writes random data through `Erasure.Encode`, constructs bitrot readers, decodes ranges, compares bytes, then injects bad/nil readers to verify quorum behavior. `TestErasureDecodeRandomOffsetLength` stress-tests random ranges when not in short mode. Benchmarks exercise common data/parity layouts and failure mixes.

Control flow and state: Each case creates a temporary erasure setup, encodes random data, reopens shard readers with expected checksums, decodes into a buffer, and cleans up readers/writers. Fault injection replaces reader disks with `badDisk` or nil entries.

Dependencies and integration points: Depends on test setup helpers, bitrot readers/writers, `DefaultBitrotAlgorithm`, `BLAKE2b512`, `SHA256`, and `Erasure.Encode` as the writer-side counterpart. It tests decode as part of the storage stack rather than isolated Reed-Solomon calls.

Risks: Random data improves coverage but limits exact reproducibility of failing byte patterns. The long random-offset test is skipped under short mode and can be expensive. Some benchmark logic mutates writer state to simulate down disks.

Test signals: Strong coverage for boundary offsets, quorum thresholds, bitrot reader failures, and byte-for-byte range reconstruction.
<!-- END_FILE_RESEARCH: sources/object-store/minio/cmd/erasure-decode_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio/cmd/erasure-encode.go -->
## sources/object-store/minio/cmd/erasure-encode.go

Purpose: Streams object bytes into erasure-coded shard writers while enforcing write quorum. This is the write-side counterpart to decode/heal.

Important APIs/types/functions: `multiWriter` stores shard writers, write quorum, and per-writer errors. `multiWriter.Write` writes each shard block, tracks nil writers as `errDiskNotFound`, handles short writes, disables failed writers, and uses `reduceWriteQuorumErrs` for quorum failure reporting. `Erasure.Encode` reads full erasure blocks from `src`, encodes each block with `EncodeData`, writes shards through `multiWriter`, handles empty objects by writing empty data/parity files, and returns total source bytes consumed.

Control flow and state: The write loop uses `io.ReadFull` over the provided block buffer. EOF and unexpected EOF are accepted as final-block conditions. Writer error state is retained across blocks so a failed shard writer is skipped for the rest of the object. Persistence occurs through supplied `io.Writer`s, typically bitrot writers over storage disks.

Dependencies and integration points: Uses `EncodeData` from `erasure-coding.go`, quorum reducers from metadata utilities, object operation ignored errors, and bitrot writer implementations passed by callers such as PutObject and tests.

Risks: Quorum is caller-supplied and must match object semantics. A writer that succeeds partially is disabled after `io.ErrShortWrite`. Empty-object behavior intentionally writes empty shard files, which callers must preserve. The returned error wraps offline disk counts for operational visibility.

Test signals: Encode tests cover zero-byte objects, varied layouts/block sizes/offsets, faulty writers, and quorum failure thresholds; benchmarks cover common performance layouts.
<!-- END_FILE_RESEARCH: sources/object-store/minio/cmd/erasure-encode.go -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio/cmd/erasure-encode_test.go -->
## sources/object-store/minio/cmd/erasure-encode_test.go

Purpose: Tests erasure encode behavior across layouts, data sizes, offsets, algorithms, and disk-failure/quorum scenarios, and provides encode benchmarks.

Important APIs/types/functions: Defines `badDisk` with failing write/read/create methods and `Hostname`. `erasureEncodeTests` includes many combinations of data/parity counts, total disks, offline disks, block size, object size, source offset, bitrot algorithm, and expected quorum failure. `TestErasureEncode` creates erasure setups, writes random data through bitrot writers, validates byte counts, then injects nil/bad writers to assert quorum outcomes. Benchmarks measure write throughput under selected down-disk patterns.

Control flow and state: The test first verifies a normal encode for each case, updates disk state for failed writers, then repeats with injected failures. Temporary disk state is owned by the test setup and removed by helpers.

Dependencies and integration points: Exercises `Erasure.Encode`, `newBitrotWriter`, writer close/checksum behavior, and storage test fixtures. It is also the source of the shared `badDisk` type used by decode/heal tests.

Risks: Test cases rely on the exact `quorum := dataBlocks+1` used in production-like writes. The injected failure count and writer nil placement are important for matching expected quorum outcomes.

Test signals: Strong write-path regression coverage, including empty data and high data-block counts.
<!-- END_FILE_RESEARCH: sources/object-store/minio/cmd/erasure-encode_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio/cmd/erasure-errors.go -->
## sources/object-store/minio/cmd/erasure-errors.go

Purpose: Declares canonical erasure-layer sentinel errors for read quorum failure, write quorum failure, and no-op healing.

Important APIs/types/functions: `errErasureReadQuorum`, `errErasureWriteQuorum`, and `errNoHealRequired` are package-level `errors.New` sentinels.

Control flow and state: No runtime control flow or persistent state. These sentinels are compared/wrapped by quorum reducers, encode/decode, healing, and object error translation.

Dependencies and integration points: Used by `reduceReadQuorumErrs`, `reduceWriteQuorumErrs`, `multiWriter.Write`, `parallelReader.Read`, tests, and user-facing object error conversion.

Risks: Error identity matters because code uses `errors.Is`, direct comparison in some paths, and wrapping. Changing text or replacing sentinels can break tests and operational messages.

Test signals: Covered indirectly through encode/decode/healing tests that expect quorum and heal behavior.
<!-- END_FILE_RESEARCH: sources/object-store/minio/cmd/erasure-errors.go -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio/cmd/erasure-heal_test.go -->
## sources/object-store/minio/cmd/erasure-heal_test.go

Purpose: Tests low-level `Erasure.Heal`, independent of full object metadata healing. It verifies shard reconstruction into stale disks under combinations of offline, bad source, and bad destination disks.

Important APIs/types/functions: `erasureHealTests` defines data blocks, disk count, offline/stale disk counts, bad readable disks, bad stale writers, block sizes, object sizes, algorithms, and expected failure. `TestErasureHeal` encodes random data, creates bitrot readers, chooses stale disks by removing readers from one side and writers from the other, injects bad readers/writers, runs `Erasure.Heal`, and compares healed writer checksums against original shard checksums.

Control flow and state: Each case creates a temporary erasure setup, writes source shards, configures stale writer targets, reconstructs through `Heal`, closes readers/writers, and validates checksum parity for successfully healed shards.

Dependencies and integration points: Uses `Erasure.Encode`, `Erasure.Heal`, bitrot readers/writers, filesystem removal for stale target paths, and `badDisk` from encode tests.

Risks: Because this bypasses object metadata, it only validates shard reconstruction and writer behavior, not `xl.meta` correctness or object namespace locks. Failure expectations are sensitive to the number and position of unavailable data versus parity shards.

Test signals: Strong low-level repair coverage, including large object size and non-standard block sizes.
<!-- END_FILE_RESEARCH: sources/object-store/minio/cmd/erasure-heal_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio/cmd/erasure-healing-common.go -->
## sources/object-store/minio/cmd/erasure-healing-common.go

Purpose: Provides common metadata-reduction and part-verification helpers used to decide which disks are online, current, stale, corrupt, or missing before object healing rewrites data.

Important APIs/types/functions: `commonETags`, `commonTimeAndOccurrence`, `commonTime`, and `commonETag` choose quorum-common metadata values. `timeSentinel`/`timeSentinel1970` represent missing/legacy timestamps. `listObjectETags` and `listObjectModtimes` extract per-disk metadata signals. `listOnlineDisks` selects disks whose `FileInfo` matches quorum modtime or ETag fallback. `convPartErrToInt`, `partNeedsHealing`, and `countPartNotSuccess` normalize part-check states. `checkObjectWithAllParts` validates metadata consistency, erasure distribution reliability, inline data bitrot, and per-part presence/checksums via `CheckParts` or `VerifyFile`.

Control flow and state: `checkObjectWithAllParts` first detects unreliable erasure distributions, filters stale/corrupt metadata from `onlineDisks`, maps metadata errors into all part results, then verifies each disk’s data or inline data. It returns two maps: errors by disk and errors by part. It mutates the supplied `onlineDisks` and `partsMetadata` slices in place to remove unusable entries.

Dependencies and integration points: Depends on `FileInfo`, `StorageAPI`, bitrot verification, `madmin.HealScanMode`, storage `CheckParts`/`VerifyFile`, and check-part constants. `healObject` consumes its outputs to decide repair targets and dangling status.

Risks: In-place mutation is intentional but easy to misuse if callers expect original metadata. The ETag fallback can select a quorum when modtimes are missing, but only if common version quorum exists. Distribution reliability heuristics must avoid both false healing and false corruption under manually altered backends.

Test signals: Common tests cover quorum time selection, online disk filtering, small and regular object verification, corrupt/missing parts, and parity selection behavior.
<!-- END_FILE_RESEARCH: sources/object-store/minio/cmd/erasure-healing-common.go -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio/cmd/erasure-healing-common_test.go -->
## sources/object-store/minio/cmd/erasure-healing-common_test.go

Purpose: Validates helper logic for selecting the latest metadata, common modtimes/parities, online disks, and disks needing part healing.

Important APIs/types/functions: Defines test-local `getLatestFileInfo` using quorum reduction and common modtime. `TestCommonTime` checks quorum time selection and sentinel fallback. `TestListOnlineDisks` and `TestListOnlineDisksSmallObjects` prepare erasure backends, tamper parts or inline metadata, then assert list/filter behavior. `TestDisksWithAllParts` covers healthy data, stale modtime, stale DataDir, and corrupted part checks. `TestCommonParities` validates parity choice when different `FileInfo` versions occur equally but only one parity has read quorum.

Control flow and state: Tests create temporary erasure backends, put objects, read/modify `FileInfo`, sometimes write metadata back, then call production helpers and verify disk filtering or part-healing flags. Several tests skip or adapt to platform constraints.

Dependencies and integration points: Exercises object-layer helpers (`prepareErasure16`, `PutObject`, `readAllFileInfo`), storage disk operations, `madmin.HealDeepScan`, metadata write helpers, and parity helpers defined elsewhere in the erasure metadata stack.

Risks: Tests use actual filesystem-backed storage fixtures and direct file corruption/removal; failures can be platform-sensitive. The local `getLatestFileInfo` mirrors production concepts but is not the production picker, so drift is possible.

Test signals: Strong evidence for metadata quorum and part verification behavior, including inline small-object coverage.
<!-- END_FILE_RESEARCH: sources/object-store/minio/cmd/erasure-healing-common_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio/cmd/erasure-healing.go -->
## sources/object-store/minio/cmd/erasure-healing.go

Purpose: Implements object, directory, bucket-listing, and abandoned-data healing for erasure-coded storage. It repairs missing/corrupt metadata and shards, removes dangling objects when requested, emits audit/trace data, and reports per-drive heal states.

Important APIs/types/functions: `healingMetric` names trace operations. `listAndHeal` lists raw metadata entries and invokes a supplied heal callback for agreed or partial entries. `listAllBuckets` gathers bucket volume info across disks and keeps only read-quorum buckets. `shouldHealObjectOnDisk` classifies missing/corrupt/outdated legacy metadata and part errors. `FileInfo.SetHealing/Healing` and `SetDataMov/DataMov` mark internal metadata state. `auditHealObject`, `objectErrToDriveState`, `defaultHealResult`, and `healTrace` support reporting. `healObject` is the core repair path. `checkAbandonedParts` removes unreferenced data dirs. `healObjectDir` repairs empty directory marker volumes. `isObjectDangling` and related helpers decide when cleanup is safer than repair. Public `HealObject` wraps logging context, directory dispatch, quick missing check, locked repair, deep-scan retry on bitrot, and object-error conversion.

Control flow and state: `healObject` reads all `xl.meta`, computes quorum, deletes dangling objects if quorum cannot be established, selects latest metadata, verifies parts, classifies disks, and exits early for no-op or dry-run. If repair is possible, it shuffles disks/metadata by erasure distribution, creates temp IDs/data dirs, reconstructs each part through `Erasure.Heal`, writes either inline buffers or temp bitrot files, updates `FileInfo`, renames healed data into place with the healing marker, and deletes temp data. It locks the namespace unless `NoLock` is set. Persistent changes include metadata rewrites, shard part writes, temp bucket usage, final `RenameData`, abandoned data deletion, and directory volume creation/removal.

Dependencies and integration points: Heavily integrated with `StorageAPI`, `FileInfo`, object quorum selection, bitrot readers/writers, erasure coding, metadata shuffling, namespace locks, audit logging, global tracing, `madmin.HealOpts`, object error translation, and bucket/listing internals.

Risks: This is a high-risk correctness path. It must distinguish healable from dangling data without deleting recoverable objects. It mutates metadata and data on multiple disks, so distribution validation, temp cleanup, writer close handling, and lock usage are critical. Non-actionable errors intentionally block dangling deletion. Inline data and XLV1 migration paths add special cases. Dry-run must not persist changes.

Test signals: Extensive healing tests cover dangling decisions, object/bucket healing, versioned healing, corrupted pools, corrupted metadata, corrupted/missing parts, empty directories, lost quorum deletion, and last data shard reconstruction.
<!-- END_FILE_RESEARCH: sources/object-store/minio/cmd/erasure-healing.go -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio/cmd/erasure-healing_test.go -->
## sources/object-store/minio/cmd/erasure-healing_test.go

Purpose: End-to-end and edge-case test suite for erasure object healing, including dangling detection, bucket healing, versioned objects, pool selection, corrupted metadata/parts, empty directories, and last-shard reconstruction.

Important APIs/types/functions: `TestIsObjectDangling` table-tests dangling classification under metadata-not-found, corrupt, delete-marker, inline-data, and part-missing scenarios. `TestHealing` and `TestHealingVersioned` verify object metadata/data restoration, stale metadata correction, abandoned data cleanup, and bucket healing. `TestHealingDanglingObject` simulates under-quorum version/delete-marker races and recursive healing with removal. `TestHealCorrectQuorum` verifies healing across multiple pools and meta bucket config objects. `TestHealObjectCorruptedPools`, `TestHealObjectCorruptedXLMeta`, and `TestHealObjectCorruptedParts` corrupt or remove `xl.meta` and part files, then assert repair or deletion. `TestHealObjectErasure` checks whole-object folder loss and unrecoverable quorum loss. `TestHealEmptyDirectoryErasure` covers directory markers. `TestHealLastDataShard` verifies data hashes after reconstructing specific missing data shards across multiple sizes.

Control flow and state: Tests initialize real filesystem-backed erasure object layers, mutate on-disk backend files directly, invoke `HealObject`, `HealObjects`, or `HealBucket`, and then re-read metadata or objects to validate final state. They also manipulate global heal/storage-class state with cleanup defers.

Dependencies and integration points: Exercises the object layer, multipart upload path, versioning metadata system, storage class parity config, direct disk APIs, metadata readers/writers, and madmin heal options. It validates integration between healing, erasure coding, object metadata, and pool routing.

Risks: These tests are expensive and stateful because they use real temp disks and direct filesystem tampering. Some checks rely on exact `FileInfo.Equals` semantics and backend layout names. The versioned test contains subtle equality expectations and is important to watch during metadata-format changes.

Test signals: Very strong coverage for user-visible healing semantics, including recoverable versus unrecoverable corruption and preservation of object bytes after repair.
<!-- END_FILE_RESEARCH: sources/object-store/minio/cmd/erasure-healing_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio/cmd/erasure-metadata-utils.go -->
## sources/object-store/minio/cmd/erasure-metadata-utils.go

Purpose: Provides quorum reducers, metadata readers, disk/metadata shuffling, disk evaluation, deterministic distribution hashing, and multipart part-size calculation for erasure object operations.

Important APIs/types/functions: `counterMap[T].GetValueWithQuorum` returns a value occurring at least quorum times. `reduceCommonVersions` and `reduceCommonDataDir` pick quorum-common metadata version bytes/data dirs. `reduceErrs`, `reduceQuorumErrs`, `reduceReadQuorumErrs`, and `reduceWriteQuorumErrs` convert per-disk error slices into quorum decisions while respecting ignored errors and context cancellation. `diskCount` counts non-nil disks. `hashOrder` creates deterministic 1-based erasure distribution order from a CRC32 of bucket/object key. `readAllFileInfo` reads `xl.meta`/version info in parallel. `shuffleDisksAndPartsMetadataByIndex`, `shuffleDisksAndPartsMetadata`, `shuffleWithDist`, `shufflePartsMetadata`, `shuffleCheckParts`, and `shuffleDisks` align arrays to erasure distribution. `evalDisks` nils disks with corresponding errors. `calculatePartSizeFromIdx` returns expected multipart part size or validation errors.

Control flow and state: Most helpers are pure reducers over slices/maps. `readAllFileInfo` performs concurrent disk I/O through `errgroup.WithNErrs`. Shuffle helpers build new aligned slices and may fall back when metadata consistency is too poor. No persistent state is written directly; these helpers drive later read/write/heal decisions.

Dependencies and integration points: Depends on `StorageAPI.ReadVersion`, `ReadOptions`, `FileInfo`, MinIO error sentinels, `errgroup`, CRC32, and object operation ignored-error lists. Used by read, write, complete multipart upload, and healing paths.

Risks: Quorum reduction correctness directly affects data availability and safety. `reduceErrs` tie-breaking is map-order dependent except for nil preference, so callers must use quorum values that avoid ambiguous correctness. `hashOrder` is 1-based and must match metadata distribution expectations. `reduceCommonVersions` assumes non-empty version byte slices are at least 8 bytes.

Test signals: Covered indirectly by endpoint/healing/common tests and object-layer tests that rely on quorum decisions, distribution shuffling, and part-size calculation.
<!-- END_FILE_RESEARCH: sources/object-store/minio/cmd/erasure-metadata-utils.go -->
