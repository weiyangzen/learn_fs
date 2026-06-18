# subset-b-009148 Research

This grouped report covers Kopia repository content/index-blob management, content verification/session helpers, ECC/encryption primitives, and repository format persistence/upgrade handling. Each section is delimited for deterministic splitting into source-tree-aligned per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/repo/content/indexblob/index_blob_manager_v0.go -->
# sources/sync-backup/kopia/repo/content/indexblob/index_blob_manager_v0.go

## Purpose
Implements the legacy v0 index-blob manager. It stores active index shards under `n`, compaction logs under `m`, and delayed cleanup records under `l`, then reconstructs the active index set by subtracting compacted inputs only when all compaction outputs are visible. The file is primarily about making index compaction work on eventually consistent blob stores without resurrecting old or deleted content entries.

## Important APIs, Types, And Functions
`ManagerV0` satisfies `indexblob.Manager` with `ListIndexBlobInfos`, `ListActiveIndexBlobs`, `Compact`, `WriteIndexBlobs`, and `Invalidate`. `compactionLogEntry` persists input/output `blob.Metadata` for compactions; `cleanupEntry` persists delayed deletion targets and schedule time. `IndexFormattingOptions` is the dependency boundary to format mutable parameters. Internal helpers include `registerCompaction`, `deleteOldBlobs`, `cleanup`, `getBlobsToCompact`, `compactIndexBlobs`, `dropContentsFromBuilder`, `addIndexBlobsToBuilder`, and `removeCompactedIndexes`.

## Control Flow
Listing runs two storage scans in parallel for `m` and `n` blobs, loads compaction entries, and removes compacted inputs only for logs whose outputs are present. Compaction lists active blobs, reads mutable parameters for pack/index sizing, selects candidates, builds a merged `index.Builder`, optionally drops deleted/manual content entries, writes replacement index blobs, registers the compaction, and then performs cleanup. Cleanup happens in stages: old input `n` blobs are deleted only after the compaction log is old enough, then old compaction logs are written into cleanup `l` markers, and only later are `m` and `l` blobs deleted.

## State And Persistence
Persistent state is entirely in blob storage: encrypted index blobs, encrypted JSON compaction logs, and encrypted JSON cleanup markers. `ListActiveIndexBlobs` returns a zero deletion watermark for v0. `timeNow` is injected but deletion decisions rely on server blob timestamps from storage metadata to tolerate client clock drift. Storage cache flushing is attempted after cleanup.

## Dependencies And Integration Points
The manager depends on `blob.Storage`, `EncryptionManager`, `content/index`, `format.MutableParameters`, `maintenancestats`, `gather`, and structured content logging. It is used by content managers that need v0 index discovery and by upgrade code that migrates legacy indexes into epoch-managed v1 indexes.

## Risks And Edge Cases
The critical correctness risk is deleting compaction logs before old index blobs, which can resurrect superseded indexes; this file explicitly deletes index blobs first. Another risk is compacting deleted entries too early or with incomplete compaction output visibility. Corrupt or unreadable compaction/cleanup blobs fail listing/cleanup, while missing blobs during reads are tolerated as concurrent deletion. Candidate selection depends on `MaxPackSize` and `CompactOptions`, so misconfigured mutable parameters can make compaction ineffective or too aggressive.

## Test Signals
`index_blob_manager_v0_test.go` stress-tests concurrent writing, reading, deletion, undelete, compaction, eventual consistency delays, and resurrection prevention. It also checks expected counts of `n`, `m`, and `l` blobs after delayed cleanup.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/repo/content/indexblob/index_blob_manager_v0.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/repo/content/indexblob/index_blob_manager_v0_test.go -->
# sources/sync-backup/kopia/repo/content/indexblob/index_blob_manager_v0_test.go

## Purpose
Tests the v0 index-blob manager under deterministic and randomized eventual-consistency scenarios. The tests validate the lifecycle of index blobs, compaction logs, cleanup records, and content deletion markers.

## Important APIs, Types, And Functions
Major tests are `TestIndexBlobManager`, `TestIndexBlobManagerStress`, `TestIndexBlobManagerPreventsResurrectOfDeletedContents`, `TestCompactionCreatesPreviousIndex`, and `TestIndexBlobManagerPreventsResurrectOfDeletedContents_RandomizedTimings`. Helpers create fake content-index entries, fake indexes, fake compactions, random writes/deletes/undeletes, active-index reads, and count checks for v0 blob prefixes. `newIndexBlobManagerForTesting` builds a `ManagerV0` with map storage, `ownwrites`, test crypto, and test hashing.

## Control Flow
The deterministic test writes several index blobs, registers compactions, advances fake storage time, and asserts the active blob list plus physical blob counts. The stress test starts multiple actors sharing storage; actors randomly read, write, delete, undelete, or compact, with only one actor allowed to compact. Resurrection tests generate sequences where deleted content and compaction overlap with visibility delays, then verify old contents do not reappear for either the writer or a separate reader.

## State And Persistence
All tests persist encrypted fake index JSON through `ManagerV0.WriteIndexBlobs` and compaction logs through `registerCompaction`. Separate fake local and storage clocks simulate clock drift and eventual consistency. `ownwrites.NewWrapper` models a client's read-your-own-writes behavior.

## Dependencies And Integration Points
The tests use `blobtesting`, `faketime`, `logging.NewWrapper`, `testlogging`, `ownwrites`, `blobcrypto.StaticCrypter`, `format.ContentFormat`, and encryption/hashing defaults. They exercise the same manager API used by production content code.

## Risks And Edge Cases
The most important tested risk is a compacted index with a deterministic blob ID causing a previously compacted input to be revived; fake indexes include a random ID to force unique output IDs. The stress test is intentionally nondeterministic and skipped/reduced in some environments. Several helpers retry when a listed blob disappears before read, matching eventual-consistency races.

## Test Signals
Strong behavioral coverage exists for v0 compaction ordering, delayed cleanup, concurrent actors, deleted-content dropping, and read-your-own-writes. It does not directly cover malformed compaction JSON or storage errors beyond missing blobs.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/repo/content/indexblob/index_blob_manager_v0_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/repo/content/indexblob/index_blob_manager_v1.go -->
# sources/sync-backup/kopia/repo/content/indexblob/index_blob_manager_v1.go

## Purpose
Implements the v1 index-blob manager using the epoch manager rather than v0 compaction logs. V1 index handling is append-oriented and delegates active-set computation, deletion watermark advancement, and atomic multi-shard writes to `epoch.Manager`.

## Important APIs, Types, And Functions
`ManagerV1` satisfies `Manager` and exposes `ListIndexBlobInfos`, `ListActiveIndexBlobs`, `Invalidate`, `Compact`, `CompactEpoch`, `WriteIndexBlobs`, `EpochManager`, and `PrepareUpgradeToIndexBlobManagerV1`. It stores the same storage, encryption, formatting-options, and logging dependencies as v0 plus an `epoch.Manager`.

## Control Flow
Listing calls `epochMgr.GetCompleteIndexSet(epoch.LatestEpoch)` and wraps returned `blob.Metadata` as indexblob `Metadata`, also returning the deletion watermark. Normal `Compact` only advances the deletion watermark when `DropDeletedBefore` is set. `CompactEpoch` merges selected index blobs into an `index.Builder`, builds v2-capable shards, creates a random compaction session suffix, encrypts each shard under an epoch prefix, and writes them to storage. `WriteIndexBlobs` encrypts all shards first with a suffix containing shard count, then calls `epochMgr.WriteIndex` so incomplete shard sets are ignored.

## State And Persistence
Active index state and watermarks are persisted by epoch blobs managed outside this file. V1 avoids v0 `m` and `l` logs for routine operations. Upgrade preparation reads active v0 index blob IDs and writes an initial epoch under `epoch.FirstEpoch`.

## Dependencies And Integration Points
This manager depends on `epoch.Manager`, `blobcrypto`, `content/index`, `EncryptionManager`, `gather`, and format mutable parameters. It reuses `addIndexBlobsToBuilder` from the v0 implementation for reading encrypted index blobs, creating a direct integration between migration and legacy index parsing.

## Risks And Edge Cases
Atomicity depends on suffix conventions and `epochMgr.WriteIndex`; any mismatch in shard-count suffixing can make readers ignore new shards or accept partial writes. `CompactEpoch` writes directly to storage after encryption, so errors after partial writes rely on epoch completeness rules. `Compact` performs no size compaction unless deletion watermark advancement is requested.

## Test Signals
This file has no direct test in the assigned set, but v0 tests indirectly validate the shared index-reading helper. Upgrade-lock tests cover repository format upgrades that rely on epoch/v1 behavior elsewhere in the repo.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/repo/content/indexblob/index_blob_manager_v1.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/repo/content/info.go -->
# sources/sync-backup/kopia/repo/content/info.go

## Purpose
Provides content-package aliases and small conversion helpers over `repo/content/index` identifiers and metadata. This keeps callers using `content.ID`, `content.Info`, and `content.IDRange` without importing the lower-level index package directly.

## Important APIs, Types, And Functions
Aliases include `ID`, `IDPrefix`, `Info`, and `IDRange`; `EmptyID` re-exports `index.EmptyID`. Functions are `IDFromHash`, `ParseID`, `IDsFromStrings`, and `IDsToStrings`.

## Control Flow
`IDFromHash` and `ParseID` delegate to index validation/parsing. `IDsFromStrings` loops through string inputs, parsing each and wrapping parse errors with the offending string. `IDsToStrings` maps each ID through `String()`.

## State And Persistence
This file has no mutable state and no persistence. It defines stable API surface for content identifiers.

## Dependencies And Integration Points
It depends on `repo/content/index` and `pkg/errors`. It is used by content APIs, verification, deletion, and callers that need identifier parsing without reaching into index internals.

## Risks And Edge Cases
The main edge case is invalid user-supplied content ID strings; `IDsFromStrings` stops on the first invalid value. Since these are aliases, behavioral compatibility follows the index package exactly.

## Test Signals
No dedicated tests are in this subset. Coverage is expected indirectly through content manager and verification tests that parse or compare content IDs.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/repo/content/info.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/repo/content/sessions.go -->
# sources/sync-backup/kopia/repo/content/sessions.go

## Purpose
Tracks active write sessions by writing encrypted session marker blobs. Session markers let repository upgrade and maintenance paths detect active writers and provide user/host/checkpoint metadata.

## Important APIs, Types, And Functions
Exports `BlobIDPrefixSession`, `SessionID`, `SessionInfo`, `SessionIDFromBlobID`, and `WriteManager.ListActiveSessions`. Internal functions include `checkClockSkewBounds`, `maybeCheckClockSkewBounds`, `generateSessionID`, `WriteManager.getOrStartSessionLocked`, `commitSession`, and `writeSessionMarkerLocked`.

## Control Flow
When a write manager starts a session, it generates a random session ID with a coarse monthly epoch suffix, fills user/host/start metadata, and writes a marker. A marker is JSON-marshaled, encrypted using `blobcrypto.Encrypt` with the session ID as suffix, then written to blob storage while optionally collecting the storage modification time. Commit deletes all marker blobs recorded in the session. Listing scans session-prefixed blobs, extracts the session ID from the blob name, decrypts each marker, decodes JSON, and keeps the latest checkpoint per session.

## State And Persistence
Session state lives both in memory on `WriteManager` (`currentSessionInfo`, `sessionMarkerBlobIDs`) and in storage as encrypted `s...` blobs. The optional clock-skew check is controlled by `KOPIA_ENABLE_CLOCK_SKEW_CHECK`; it is disabled unless the variable is present and not explicitly false.

## Dependencies And Integration Points
The file depends on `blobcrypto`, `gather`, `blob.Storage`, environment variables, JSON, and `WriteManager` fields. Upgrade-lock monitoring and repository availability checks use active session information to avoid unsafe upgrades during ongoing writes.

## Risks And Edge Cases
Clock skew detection can reject marker writes when enabled and storage timestamps differ by more than five minutes. Marker cleanup ignores already-missing blobs but returns other deletion errors. `SessionIDFromBlobID` searches dash-separated suffixes for an `s` prefix, so malformed session-prefixed blobs cause listing errors.

## Test Signals
`sessions_test.go` covers session ID uniqueness, blob ID parsing, explicit clock-skew checking, environment-gated skew checking, and marker writes with matching and skewed storage clocks.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/repo/content/sessions.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/repo/content/sessions_test.go -->
# sources/sync-backup/kopia/repo/content/sessions_test.go

## Purpose
Validates session ID creation, session blob parsing, optional clock-skew enforcement, and write-session marker persistence behavior.

## Important APIs, Types, And Functions
Tests include `TestGenerateSessionID`, `TestSessionIDFromBlobID`, `TestCheckClockSkewBounds_Positive`, `TestCheckClockSkewBounds_Negative`, `TestMaybeCheckClockSkewBounds_Disabled`, `TestMaybeCheckClockSkewBounds_Enabled`, `TestWriteSessionMarkerLockedWithoutClockSkew`, and `TestWriteSessionMarkerLockedWithClockSkew`.

## Control Flow
The tests generate multiple IDs at the same time and ensure uniqueness; table-drive blob ID parsing cases; compare local and modification times at and over the skew threshold; and build test write managers over map storage with controlled fake clocks. Marker-write tests enable `KOPIA_ENABLE_CLOCK_SKEW_CHECK` and assert success when manager and storage times match, failure when storage time is just beyond the permitted skew.

## State And Persistence
The marker-write tests persist encrypted marker blobs into `blobtesting.MapStorage`. Fake clock instances provide deterministic local and storage modification times.

## Dependencies And Integration Points
The tests use `blobtesting`, `faketime`, `epoch.DefaultParameters`, `format.ContentFormat`, `index.Version2`, and `NewManagerForTesting`. They exercise the session code through the same `WriteManager` path used by production writers.

## Risks And Edge Cases
The tests explicitly cover unset/false environment variables disabling skew checks, set/true variables enabling them, and boundary behavior at exactly `maxClockSkew`. They do not cover malformed encrypted session marker payloads or duplicate marker resolution in `ListActiveSessions`.

## Test Signals
Coverage is good for clock-skew gating and session naming. Active-session listing is only indirectly covered by constructing marker writes, not by scanning multiple stored marker blobs.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/repo/content/sessions_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/repo/content/stats.go -->
# sources/sync-backup/kopia/repo/content/stats.go

## Purpose
Defines thread-safe counters for content manager activity: content reads/writes/hashes, byte totals, encryption/decryption bytes, and valid/invalid content findings.

## Important APIs, Types, And Functions
`Stats` contains `atomic.Int64` and `atomic.Uint32` fields. Public methods are `Reset`, `ReadContent`, `WrittenContent`, `HashedContent`, `DecryptedBytes`, `EncryptedBytes`, `InvalidContents`, and `ValidContents`. Package-private increment helpers include `decrypted`, `encrypted`, `readContent`, `wroteContent`, `hashedContent`, `foundValidContent`, and `foundInvalidContent`.

## Control Flow
Readers load atomic values and return approximate snapshots. Writers increment byte and count fields independently, so count/byte pairs are eventually consistent rather than a single atomic tuple. `Reset` stores zero to all counters.

## State And Persistence
State is in-memory only and belongs to a `Stats` instance. There is no persistence or external synchronization beyond atomic operations.

## Dependencies And Integration Points
The only dependency is `sync/atomic`. Content read/write, hashing, encryption, and verification code can update these counters without taking locks.

## Risks And Edge Cases
`Reset` is not an atomic global transaction; concurrent readers or writers can observe mixed old/new values. Public comments describe counts as approximate, which is important for UI/progress use. There is a comment typo on `EncryptedBytes`, which says decrypted bytes.

## Test Signals
No dedicated tests in this subset. The design is simple enough that indirect coverage comes from content manager tests that update stats during operations.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/repo/content/stats.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/repo/content/verify.go -->
# sources/sync-backup/kopia/repo/content/verify.go

## Purpose
Verifies repository content index entries against physical pack blobs. It detects missing packs, truncated packs, and optionally corrupted/unreadable contents by sampling actual content reads.

## Important APIs, Types, And Functions
`VerifyOptions` controls content ID range, read percentage, deleted-content inclusion, iterator parallelism, and progress callback interval. `VerifyProgressStats` reports success/error counts. `WriteManager.VerifyContents` delegates to `contentVerifier.verifyContents`. Internal verification functions are `verify`, `verifyContentImpl`, and `logCountMap`.

## Control Flow
Verification first builds a map of all existing blob metadata with `blob.ReadBlobMap`. It then iterates repository contents using `WriteManager.IterateContents`, honoring range, parallelism, and deleted-content options. Each content entry is checked for pack existence and bounds; if configured, it probabilistically calls `GetContent` to validate decryption/hash/integrity. Counters and per-pack error maps are updated atomically, progress callbacks fire every configured interval, and a wrapped corruption error is returned when any content error count is nonzero.

## State And Persistence
The verifier is transient and stores an in-memory blob metadata map, atomic counters, and counter maps keyed by pack blob ID. It does not mutate repository state.

## Dependencies And Integration Points
Depends on `blob`, `internal/stats.CountersMap`, `logging`, `WriteManager.IterateContents`, and `WriteManager.GetContent`. It is a repository maintenance/integrity operation that relies on index metadata and pack layout correctness.

## Risks And Edge Cases
The existing blob map is a snapshot; concurrent repository writes/deletes could make verification report stale missing/truncated errors. `math/rand` sampling is non-cryptographic and nondeterministic. When `ContentReadPercentage` is zero, corruption inside otherwise correctly sized packs is not detected. Error reporting intentionally reuses `errMissingPacks` for all verification failures, including truncation and corruption.

## Test Signals
`verify_test.go` covers healthy packs, callback invocation on success and failure, deleted-content inclusion/exclusion, truncated packs, corrupted packs with 100% reads, and regular/special pack ranges.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/repo/content/verify.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/repo/content/verify_test.go -->
# sources/sync-backup/kopia/repo/content/verify_test.go

## Purpose
Exercises `WriteManager.VerifyContents` against healthy, missing, truncated, corrupted, deleted, regular-pack, and special-pack scenarios.

## Important APIs, Types, And Functions
Helpers `newTestingMapStorage` and `newTestWriteManager` create a test write manager with deterministic content format. Tests include `TestVerifyContents_NoMissingPacks`, `TestVerifyContentToPackMapping_EnsureCallbackIsCalled`, `TestVerifyContents_Deleted`, `TestVerifyContents_TruncatedPack`, `TestVerifyContents_CorruptedPack`, `TestVerifyContents_MissingPackP`, and `TestVerifyContentToPackMapping_MissingPackQ`.

## Control Flow
Tests write content, flush indexes/packs, then mutate underlying blob storage by deleting, truncating, or overwriting pack blobs. Verification is run with different options: deleted-content inclusion, `ContentIDRange` filters, 100% read sampling, and callback intervals. Assertions check either no error or `errMissingPacks` wrapping.

## State And Persistence
The tests use in-memory map storage and real content-manager flushes, so index entries and pack blobs are persisted in test storage. Mutations happen directly against blob storage to simulate corruption outside the content manager.

## Dependencies And Integration Points
Uses `blobtesting`, `epoch.DefaultParameters`, `format.ContentFormat`, `index.Version2`, `gather`, and `testlogging`. It tests the integration of content writes, index flushing, pack naming prefixes, and verification logic.

## Risks And Edge Cases
The tests distinguish non-prefixed regular `p` packs from prefixed special `q` packs using content ID ranges. They also verify that deleted contents only matter when `IncludeDeletedContents` is true. Callback tests use atomic counters so they remain valid if iterator parallelism is raised.

## Test Signals
Coverage is strong for repository-integrity outcomes. It does not test partial read percentages below 100%, concurrent mutation during verification, or logging contents.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/repo/content/verify_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/repo/content/write_temp_file.go -->
# sources/sync-backup/kopia/repo/content/write_temp_file.go

## Purpose
Provides a helper for writing temporary files atomically and durably enough for later rename/use by content code. It creates a temporary file in a target directory, writes bytes, syncs the file, and cleans up on any failure.

## Important APIs, Types, And Functions
Private interfaces `file` and `fsInterface` abstract file operations for testing. `localFS` adapts `os.CreateTemp`, `os.Remove`, and `os.MkdirAll`. Public-within-package functions are `writeTempFileAtomic` and `writeTempFileAtomicImp`.

## Control Flow
`writeTempFileAtomicImp` attempts `CreateTemp`; if the directory is missing, it creates the directory with `cache.DirMode` and retries. It defers file close and, if any error occurred, removes the temporary file and clears the returned name. It writes all data, calls `Sync`, and returns the temp filename without renaming it.

## State And Persistence
The only persistent side effect is a synced temp file under the requested directory on success. On write, sync, close, or cleanup errors, it returns joined errors and removes the temp file when possible.

## Dependencies And Integration Points
Depends on `os`, `io`, `io/fs`, `errors.Join`, `pkg/errors`, and `internal/cache` for directory mode. It is intended for code that needs to stage a file before an atomic rename.

## Risks And Edge Cases
The function name says atomic, but this helper only atomically creates a temp file; callers must perform any final rename themselves. It does not retry short writes because `Write` returning `n < len(data), nil` is not handled. Close errors are joined after success and force cleanup, which is conservative but can surprise callers if data was written and synced.

## Test Signals
`write_temp_file_test.go` covers successful writes, empty data, missing directory creation, unwritable directory, sync invocation, no leaked temp files on success, and cleanup on write/sync/close errors.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/repo/content/write_temp_file.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/repo/content/write_temp_file_test.go -->
# sources/sync-backup/kopia/repo/content/write_temp_file_test.go

## Purpose
Tests the temporary-file helper's success path, directory creation, durability call, and cleanup behavior under failures.

## Important APIs, Types, And Functions
Tests include `TestWriteTempFileAtomic_HappyPath`, `TestWriteTempFileAtomic_EmptyData`, `TestWriteTempFileAtomic_CreatesDirectoryIfMissing`, `TestWriteTempFileAtomic_NonExistentDirUnwritable`, `TestWriteTempFileAtomic_FileIsSynced`, `TestWriteTempFileAtomic_NoTempFilesLeft`, and `TestWriteTempFileAtomic_NoTempFilesLeftOnError`. Test doubles include `mockFileSynced`, `mockfs`, `mockFileWriteError`, `mockFileSyncError`, and `mockFileCloseError`.

## Control Flow
The tests call `writeTempFileAtomicImp` with `localFS` or wrapped file implementations, inspect returned paths, read file contents, and list target directories. Failure tests inject write, sync, and close errors and assert that the returned name is empty and no temp files remain.

## State And Persistence
Each test uses `t.TempDir`. Successful tests leave exactly the returned temp file in the directory; failure tests expect the directory to be empty. The permission test temporarily chmods a parent directory and restores it in cleanup.

## Dependencies And Integration Points
Uses `os`, `filepath`, `runtime`, `atomic`, `pkg/errors`, and `testify/require`. The mocked filesystem path exercises the file abstraction built into production code.

## Risks And Edge Cases
The unwritable-directory test is skipped on Windows and when running as root because permissions may not behave as expected. Tests do not cover short writes with nil error or remove failures during cleanup.

## Test Signals
Coverage is focused and high for intended helper behavior, especially the subtle deferred close/cleanup path.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/repo/content/write_temp_file_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/repo/doc.go -->
# sources/sync-backup/kopia/repo/doc.go

## Purpose
Defines the package documentation for `repo`, stating that it implements a content-addressable repository on top of blob storage.

## Important APIs, Types, And Functions
No APIs, types, or functions are defined; the file contains only the package comment and `package repo`.

## Control Flow
No runtime control flow.

## State And Persistence
No state or persistence.

## Dependencies And Integration Points
The package-level comment is used by Go documentation tooling and helps identify the high-level role of the `repo` package for callers.

## Risks And Edge Cases
No code risk. Documentation can become stale if the package role broadens beyond content-addressable repository concerns.

## Test Signals
No tests are applicable.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/repo/doc.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/repo/ecc/ecc.go -->
# sources/sync-backup/kopia/repo/ecc/ecc.go

## Purpose
Provides the registry and factory interface for ECC algorithms, exposing ECC implementations as `encryption.Encryptor` instances so they can be composed with content encryption.

## Important APIs, Types, And Functions
`CreateECCFunc` is a factory signature. `RegisterAlgorithm` adds factories to the package-global map. `SupportedAlgorithms` returns sorted registered names. `CreateAlgorithm` looks up and creates an algorithm from `Options`. `Parameters` captures format-layer ECC fields, and `CreateEncryptor` converts those parameters to `Options`.

## Control Flow
Algorithms register themselves in `init` functions. Creation is a map lookup followed by factory invocation. Supported algorithm listing iterates the map and sorts names for stable output.

## State And Persistence
The only state is the in-memory package-global registry. There is no persistence.

## Dependencies And Integration Points
Depends on `repo/encryption` for the shared encryptor interface. `format.NewFormattingOptionsProvider` calls `ecc.CreateEncryptor` when a repository format enables ECC.

## Risks And Edge Cases
Unknown algorithm names return an error. Registry mutation is not synchronized, but expected use is init-time registration before concurrent access. Since ECC is modeled as encryption, callers must understand it may add integrity/recovery data rather than secrecy.

## Test Signals
ECC creation and behavior are covered indirectly by `ecc_rs_crc_test.go` and `ecc_utils_test.go`, which use `CreateAlgorithm`.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/repo/ecc/ecc.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/repo/ecc/ecc_options.go -->
# sources/sync-backup/kopia/repo/ecc/ecc_options.go

## Purpose
Defines configuration for ECC algorithms.

## Important APIs, Types, And Functions
`Options` includes `Algorithm`, `OverheadPercent`, `MaxShardSize`, and `DeleteFirstShardForTests`. `DefaultAlgorithm` is `AlgorithmReedSolomonWithCrc32`.

## Control Flow
No functions are defined. Other ECC code reads these fields to select algorithms and tune shard layout.

## State And Persistence
Options are serializable via JSON tags, allowing repository format or blob-provider settings to persist ECC choices.

## Dependencies And Integration Points
Used by `CreateAlgorithm` and `newReedSolomonCrcECC`. The testing-only flag is consumed by the Reed-Solomon decrypt path to simulate data loss.

## Risks And Edge Cases
Comments say overhead should be between 0 and 100, but validation is not in this file. A zero algorithm disables ECC at higher layers; a zero max shard size triggers automatic selection in the implementation.

## Test Signals
Behavior of options is covered through Reed-Solomon tests with explicit overhead and shard sizes.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/repo/ecc/ecc_options.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/repo/ecc/ecc_rs_crc.go -->
# sources/sync-backup/kopia/repo/ecc/ecc_rs_crc.go

## Purpose
Implements `REED-SOLOMON-CRC32`, an error-correction transform that appends parity shards and CRC32 checksums to stored data. It can reconstruct corrupted or missing shards during decrypt/read.

## Important APIs, Types, And Functions
`ReedSolomonCrcECC` implements `encryption.Encryptor` with `Encrypt`, `Decrypt`, and a panic-only `Overhead`. Construction happens through `newReedSolomonCrcECC`, registered in `init`. Sizing helpers include `computeSizesFromOriginal`, `computeSizesFromStored`, `readLength`, `computeFinalFileSizeWithPadding`, and `sizesInfo`.

## Control Flow
Construction chooses `MaxShardSize` from overhead if absent, subtracts CRC overhead from the space budget, computes data/parity shard counts, sets small-file and block thresholds, and creates Reed-Solomon encoders. Encryption prepends original length, pads as needed, splits data into shards, computes parity, writes CRC+parity shards first, then writes CRC+data shards. Decryption reconstructs the same sizing from stored length, verifies CRCs to nil out corrupted shards, optionally deletes the first shard for tests, asks Reed-Solomon to reconstruct data shards, reads the embedded original length, and appends only original payload bytes.

## State And Persistence
The persisted byte layout is `([CRC32][parity shard])*` followed by `([CRC32][data shard])*`, potentially across blocks. Small files store padding; larger files avoid storing trailing padding and infer it on read.

## Dependencies And Integration Points
Depends on `github.com/klauspost/reedsolomon`, CRC32, binary big endian encoding, `gather`, and `repo/encryption`. It is inserted by the format provider as the outer transform after content encryption.

## Risks And Edge Cases
Correctness depends on exact symmetry between stored-length and original-length sizing. CRC32 is for corruption detection, not cryptographic authentication. `Overhead` panics because overhead is variable; callers must not use ECC wrappers where fixed overhead is required. Very small shard sizes require special `readLength` cases because the four-byte original length spans multiple shards.

## Test Signals
`ecc_rs_crc_test.go` checks fixed overhead examples, data/parity CRC corruption, reconstructable and unreconstructable numbers of changed shards, and monotonic sizing in a skipped slow test.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/repo/ecc/ecc_rs_crc.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/repo/ecc/ecc_rs_crc_test.go -->
# sources/sync-backup/kopia/repo/ecc/ecc_rs_crc_test.go

## Purpose
Validates Reed-Solomon CRC ECC sizing and recovery behavior for small, medium, and large payloads.

## Important APIs, Types, And Functions
Tests include `Test_RsCrc32_AssertSizeAlwaysGrow` (skipped by default), `Test_RsCrc32_2p_1b`, `Test_RsCrc32_2p_10kb`, and `Test_RsCrc32_10p_1mb`. Helpers mutate data shard bytes, data CRC bytes, parity shard bytes, and parity CRC bytes, then call shared `testPutAndGet`.

## Control Flow
Each active test creates ECC options, encrypts generated deterministic data, asserts final length, flips configured bytes in stored data, then decrypts and expects success or failure depending on parity capacity. The skipped monotonic test walks sizes up to 10 MiB, ensuring computed stored sizes do not decrease and stored-size decoding reproduces original sizing.

## State And Persistence
State is in-memory byte slices and `gather.WriteBuffer`s. There is no external storage.

## Dependencies And Integration Points
Uses `testutil.EnsureType` to inspect the concrete `ReedSolomonCrcECC`, and `CreateAlgorithm` to exercise registration rather than direct construction for active tests.

## Risks And Edge Cases
The tests encode important expected ECC overhead sizes, so implementation changes that alter layout will break them. They verify both recoverable and unrecoverable corruption thresholds. The slow monotonic test is skipped, so broad size regression coverage is manual unless enabled.

## Test Signals
Coverage is strong for representative payload sizes and corruption locations. It does not cover malformed truncated ECC streams beyond changed-byte scenarios.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/repo/ecc/ecc_rs_crc_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/repo/ecc/ecc_utils.go -->
# sources/sync-backup/kopia/repo/ecc/ecc_utils.go

## Purpose
Provides small numeric and slice utilities used by ECC sizing and buffer preparation.

## Important APIs, Types, And Functions
Functions are `computeShards`, `between`, `applyPercent`, `fillWithZeros`, `minInt`, `maxInt`, `maxFloat32`, and `ceilInt`.

## Control Flow
`computeShards` starts from 128 data shards, derives parity shards from the overhead percentage, clamps to 1..128, and if that would produce one parity shard, switches to two parity shards and computes the data-shard count instead. Other helpers are simple arithmetic or loops.

## State And Persistence
No state or persistence. `fillWithZeros` mutates the provided byte slice.

## Dependencies And Integration Points
Depends on `math`. Used heavily by `ecc_rs_crc.go` for shard count, shard size, block count, and zero padding.

## Risks And Edge Cases
Very low overhead percentages can produce high data-shard counts with two parity shards. `applyPercent` floors rather than rounds, which affects parity capacity. Division helpers assume positive denominators.

## Test Signals
`ecc_utils_test.go` checks representative shard-count outputs and uses the helpers through ECC round-trip tests.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/repo/ecc/ecc_utils.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/repo/ecc/ecc_utils_test.go -->
# sources/sync-backup/kopia/repo/ecc/ecc_utils_test.go

## Purpose
Tests ECC utility shard calculations and provides shared round-trip/corruption helpers for ECC tests.

## Important APIs, Types, And Functions
`TestComputeShares` verifies `computeShards` for 0.1%, 1%, 2%, and 10% overhead. `testPutAndGet` creates an ECC algorithm, encrypts deterministic data, mutates it through a callback, and decrypts. `flipByte` forces a byte to an opposite extreme value.

## Control Flow
Round-trip helper generates nonzero deterministic payload bytes, encrypts into a write buffer, checks expected size increase, applies caller mutations, decrypts, and asserts either recovered equality or an error.

## State And Persistence
Only in-memory buffers and slices are used.

## Dependencies And Integration Points
Uses `gather`, `repo/encryption` interface, and `CreateAlgorithm`, so tests exercise the registry/factory path.

## Risks And Edge Cases
Shard-count tests pin the floor/clamp behavior. Shared helper assumes `expectedEccSize` equals stored length minus original size, so layout changes require test updates.

## Test Signals
Useful support coverage for ECC implementation. It does not independently test every numeric helper, but most are exercised through Reed-Solomon tests.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/repo/ecc/ecc_utils_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/repo/encryption/aead_helpers.go -->
# sources/sync-backup/kopia/repo/encryption/aead_helpers.go

## Purpose
Contains shared AEAD sealing/opening helpers for encryption algorithms that prepend random nonces and authenticate content IDs as associated data.

## Important APIs, Types, And Functions
Private helpers are `aeadSealWithRandomNonce` and `aeadOpenPrefixedWithNonce`.

## Control Flow
Seal allocates one contiguous buffer containing nonce plus plaintext/ciphertext space, fills the nonce with `crypto/rand`, appends plaintext into the buffer, calls `AEAD.Seal` with content ID as associated data, and appends the whole nonce+ciphertext to output. Open checks minimum length, copies ciphertext into a contiguous buffer, splits nonce and ciphertext, calls `AEAD.Open` with the same content ID, and appends plaintext to output.

## State And Persistence
No persistent state. The nonce is persisted as the ciphertext prefix by callers.

## Dependencies And Integration Points
Depends on `crypto/cipher`, `crypto/rand`, `gather`, and `pkg/errors`. Used by AES-GCM-HMAC-SHA256 and ChaCha20-Poly1305-HMAC-SHA256 encryptors.

## Risks And Edge Cases
Random nonce generation failure aborts encryption. Decrypt rejects ciphertext shorter than nonce plus AEAD tag. Associated-data binding means decrypting with a wrong content ID fails, which is central to repository integrity.

## Test Signals
`encryption_test.go` indirectly covers random nonces, wrong content IDs, corrupted ciphertexts, short/corrupt authentication failures, and known ciphertext samples.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/repo/encryption/aead_helpers.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/repo/encryption/aes256_gcm_hmac_sha256_encryptor.go -->
# sources/sync-backup/kopia/repo/encryption/aes256_gcm_hmac_sha256_encryptor.go

## Purpose
Registers and implements the default AES-256-GCM content encryption algorithm with per-content keys derived from HMAC-SHA256.

## Important APIs, Types, And Functions
Constants define fixed overhead and key-derivation secret size. `aes256GCMHmacSha256` holds an HMAC hash pool. Methods are `aeadForContent`, `Encrypt`, `Decrypt`, and `Overhead`. `init` registers `AES256-GCM-HMAC-SHA256`.

## Control Flow
At construction, `deriveKey` creates a 32-byte secret for HMAC. For each content ID, `aeadForContent` hashes the content ID with pooled HMAC-SHA256 to derive a 32-byte AES key, creates an AES cipher, and wraps it in GCM. Encrypt/decrypt delegate to the AEAD helper functions with random nonce prefixing and content-ID associated data.

## State And Persistence
The encryptor stores only an HMAC pool. Persisted ciphertext layout is nonce-prefixed AEAD output with 28 bytes of fixed overhead: 12-byte GCM nonce plus 16-byte tag.

## Dependencies And Integration Points
Depends on standard AES/GCM/HMAC/SHA256 and the package registry. It is the `encryption.DefaultAlgorithm` used by format/content tests and default repository formats.

## Risks And Edge Cases
Security depends on high-quality random nonces and distinct content-ID-derived keys. The HMAC pool uses type assertion and must only contain hash.Hash values from its own `New` function. Wrong master keys or content IDs surface as decrypt authentication failures.

## Test Signals
`encryption_test.go` verifies round trips, ciphertext non-determinism, wrong content ID failure, mutation failure, and known AES sample decryptions.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/repo/encryption/aes256_gcm_hmac_sha256_encryptor.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/repo/encryption/chacha20_poly1305_hmac_sha256_encryptor.go -->
# sources/sync-backup/kopia/repo/encryption/chacha20_poly1305_hmac_sha256_encryptor.go

## Purpose
Registers and implements ChaCha20-Poly1305 content encryption with per-content keys derived from HMAC-SHA256.

## Important APIs, Types, And Functions
`chacha20poly1305hmacSha256Encryptor` holds an HMAC pool. Methods mirror the AES implementation: `aeadForContent`, `Encrypt`, `Decrypt`, and `Overhead`. `init` registers `CHACHA20-POLY1305-HMAC-SHA256`.

## Control Flow
Construction derives a 32-byte HMAC secret from the repository master key. For each content ID, HMAC-SHA256 derives the ChaCha20-Poly1305 key. Encrypt/decrypt use the shared nonce-prefixed AEAD helpers with content ID as associated data.

## State And Persistence
State is an HMAC pool. Persisted ciphertext has 28 bytes overhead: 12-byte nonce plus 16-byte Poly1305 tag.

## Dependencies And Integration Points
Depends on `golang.org/x/crypto/chacha20poly1305`, HMAC/SHA256, `gather`, and the encryption registry. It is listed by `SupportedAlgorithms` and can be selected in repository content format.

## Risks And Edge Cases
Same associated-data and nonce risks as the AES implementation. The code assumes the HMAC pool returns `hash.Hash`. Algorithm availability depends on the `init` registration running.

## Test Signals
Covered by `encryption_test.go` round trips, wrong-ID/corruption failures, and known ChaCha20-Poly1305 ciphertext samples.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/repo/encryption/chacha20_poly1305_hmac_sha256_encryptor.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/repo/encryption/encryption.go -->
# sources/sync-backup/kopia/repo/encryption/encryption.go

## Purpose
Defines the content encryption interface, registry, supported algorithm listing, and HKDF-based key derivation helper.

## Important APIs, Types, And Functions
`Encryptor` requires `Encrypt`, `Decrypt`, and `Overhead`. `Parameters` supplies encryption algorithm and master key. `CreateEncryptor`, `SupportedAlgorithms`, `Register`, and `deriveKey` are the key functions. `DefaultAlgorithm` is `AES256-GCM-HMAC-SHA256`.

## Control Flow
Algorithm implementations register factories in `init`. `CreateEncryptor` looks up the selected algorithm and calls its factory. `SupportedAlgorithms` filters deprecated entries unless requested and sorts names. `deriveKey` uses HKDF-SHA256 with the repository master key, purpose bytes, empty info, and a minimum output length of 32 bytes.

## State And Persistence
The package-global `encryptors` map is in-memory registry state. No ciphertext is persisted by this file directly.

## Dependencies And Integration Points
Used by format providers, blob crypto, content managers, and ECC wrappers. It depends on `crypto/hkdf`, SHA256, `gather`, and `pkg/errors`.

## Risks And Edge Cases
Unknown algorithms fail fast. Registry mutation is not synchronized but expected during package initialization. `deriveKey` rejects too-short output lengths. Algorithm descriptions are stored but not exposed by a public API here.

## Test Signals
`encryption_test.go` exercises all registered algorithms through `SupportedAlgorithms(true)` and `CreateEncryptor`.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/repo/encryption/encryption.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/repo/encryption/encryption_test.go -->
# sources/sync-backup/kopia/repo/encryption/encryption_test.go

## Purpose
Tests all registered encryption algorithms for round-trip correctness, nonce non-determinism, content-ID authentication, corruption detection, known-sample compatibility, and benchmark performance.

## Important APIs, Types, And Functions
The local `parameters` type implements `encryption.Parameters`. Tests are `TestRoundTrip`, `TestCiphertextSamples`, `verifyCiphertextSamples`, and `BenchmarkEncryption`.

## Control Flow
`TestRoundTrip` generates random data, master key, and two content IDs, then encrypts/decrypts with every supported algorithm. It asserts repeated encryption differs, correct IDs decrypt successfully, different content IDs produce different ciphertext, wrong IDs fail, and bit flips fail. `TestCiphertextSamples` decodes known ciphertext hex strings and verifies they decrypt to expected payloads for each algorithm.

## State And Persistence
All state is in-memory random bytes and buffers. Known sample ciphertexts act as compatibility fixtures.

## Dependencies And Integration Points
Uses the public encryption registry and `gather.WriteBuffer`, so it tests the same construction path used by repository format code.

## Risks And Edge Cases
Randomness means exact ciphertext output is not asserted for new encryptions; samples only test decryption compatibility. The corruption test mutates one slice inside `gather.Bytes`, assuming at least one slice and non-empty ciphertext.

## Test Signals
Strong coverage for confidentiality/integrity API behavior across algorithms. Benchmark covers default encryption throughput for an 8 MiB payload.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/repo/encryption/encryption_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/repo/format/blobcfg_blob.go -->
# sources/sync-backup/kopia/repo/format/blobcfg_blob.go

## Purpose
Manages the `kopia.blobcfg` blob, which persists blob-storage retention settings separately from the main format blob and encrypts them with the format encryption key.

## Important APIs, Types, And Functions
`KopiaBlobCfgBlobID` names the blob. `BlobStorageConfiguration` stores `RetentionMode` and `RetentionPeriod`. Methods/functions include `IsRetentionEnabled`, `Validate`, `serializeBlobCfgBytes`, `deserializeBlobCfgBytes`, and `KopiaRepositoryJSON.WriteBlobCfgBlob`.

## Control Flow
Validation requires retention mode and period to be provided together and enforces a minimum one-day period. Serialization JSON-marshals the config and either leaves it plaintext for `NONE` or AES-GCM encrypts it for `AES256_GCM`. Deserialization mirrors that path and returns an empty config for nil bytes. Writing encrypts serialized bytes and stores them under `kopia.blobcfg` with retention options applied to the blob write.

## State And Persistence
Persistent state is the `kopia.blobcfg` blob. It may carry retention settings that also affect both blobcfg and repository format blob writes.

## Dependencies And Integration Points
Depends on `blob.Storage`, retention types, `gather`, JSON, and repository format encryption helpers. `format.Manager.Initialize`, `SetParameters`, and `ChangePassword` call this code when creating or rewriting repository configuration.

## Risks And Edge Cases
Bad encryption algorithm names fail serialization/deserialization. Decryption failure is intentionally reported as a generic inability to decrypt blobcfg. Invalid retention values block initialization or parameter updates before partial state should be persisted.

## Test Signals
`format_manager_test.go` covers initialization with retention, retention updates, and invalid negative retention values. Direct serialization corruption is not tested in this subset.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/repo/format/blobcfg_blob.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/repo/format/content_format.go -->
# sources/sync-backup/kopia/repo/format/content_format.go

## Purpose
Defines repository content-format parameters: hashing, encryption, ECC, secrets, master key, mutable pack/index/epoch settings, and password-change support.

## Important APIs, Types, And Functions
`ContentFormat` embeds `MutableParameters` and implements encryption, hashing, ECC, and format-provider parameter interfaces. `ResolveFormatVersion` applies defaults for format versions 1, 2, and 3. `MutableParameters` stores `Version`, `MaxPackSize`, `IndexVersion`, and `EpochParameters`; `Validate` enforces supported ranges.

## Control Flow
`ResolveFormatVersion` enables password change and index v2/epoch defaults for format v2/v3, and disables password change with index v1/no epoch for v1. `Validate` checks pack size bounds, index version bounds, and epoch parameter validity.

## State And Persistence
These structs are serialized into encrypted repository config inside `kopia.repository`. Sensitive fields are tagged for scrubbing by surrounding tooling.

## Dependencies And Integration Points
Depends on `epoch`, `units`, and `content/index`. The format manager and static provider use this type to construct hash functions, encryptors, content managers, and index-blob managers.

## Risks And Edge Cases
Unsupported format versions fail. Default resolution is separate from validation, so callers must ensure version-specific defaults are applied when needed. Pack size boundaries affect content packing, compaction, and performance.

## Test Signals
Format manager tests use these fields extensively for initialization, cache refresh, mutable parameter updates, retention updates, and password changes.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/repo/format/content_format.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/repo/format/encryptor_wrapper.go -->
# sources/sync-backup/kopia/repo/format/encryptor_wrapper.go

## Purpose
Composes two `encryption.Encryptor` implementations, typically content encryption followed by ECC, into a single encryptor for the format provider.

## Important APIs, Types, And Functions
`encryptorWrapper` stores `impl` and `next`. It implements `Encrypt`, `Decrypt`, and `Overhead`.

## Control Flow
Encryption runs `impl.Encrypt` into a temporary buffer, then passes that ciphertext through `next.Encrypt`. Decryption reverses the order: `next.Decrypt` first, then `impl.Decrypt`. `Overhead` panics because composed ECC overhead can be variable and callers should not request fixed overhead from this wrapper.

## State And Persistence
No independent persistence. The persisted bytes are the nested output of the two encryptors.

## Dependencies And Integration Points
Used by `NewFormattingOptionsProvider` when content format enables ECC. Depends on `gather` and `repo/encryption`.

## Risks And Edge Cases
Order is significant: ECC protects encrypted bytes, not plaintext. Any caller that invokes `Overhead` on a wrapper will panic. Temporary buffers are correctly closed, but errors are passed through without additional context.

## Test Signals
ECC and encryption tests cover the individual transforms; this wrapper is indirectly exercised when repository formats enable ECC outside this subset.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/repo/format/encryptor_wrapper.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/repo/format/format_blob.go -->
# sources/sync-backup/kopia/repo/format/format_blob.go

## Purpose
Handles the top-level `kopia.repository` JSON blob, format-blob key derivation, encrypted repository config bytes, and recovery of embedded format blobs from packed data.

## Important APIs, Types, And Functions
Defines `KopiaRepositoryJSON`, constants for format encryption/checksum/recovery limits, `KopiaRepositoryBlobID`, `ErrInvalidPassword`, and helpers `ParseKopiaRepositoryJSON`, `DeriveFormatEncryptionKeyFromPassword`, `RecoverFormatBlob`, `recoverFormatBlobWithLength`, `verifyFormatBlobChecksum`, `WriteKopiaRepositoryBlob`, `WriteKopiaRepositoryBlobWithID`, AES-GCM encrypt/decrypt helpers, and `addFormatBlobChecksumAndLength`.

## Control Flow
Parsing JSON unmarshals the repository blob. Password derivation uses repository unique ID and configured KDF. Recovery optionally lists by prefix, reads prefix and suffix chunks, decodes a two-byte length, and validates HMAC-SHA256 checksum with a fixed identifier secret. Writing pretty-prints JSON and stores it with blob retention options. Checksum wrapping returns `<length><data+hmac><length>` so recovery can find it at either file boundary.

## State And Persistence
Persistent state is `kopia.repository`, which contains public metadata, unique ID, KDF name, format encryption algorithm, and encrypted repository configuration bytes. Recovery helpers operate on copies embedded elsewhere, such as format bytes stored inside pack data.

## Dependencies And Integration Points
Depends on `internal/crypto`, `blob.Storage`, `gather`, JSON, HMAC/SHA256, and retention-aware blob writes. The format manager calls these functions for initialization, refresh, password changes, and upgrades.

## Risks And Edge Cases
Invalid password is surfaced by callers after decrypt failure. Recovery only reads up to 64 KiB from each end and caps checksummed format bytes at 65,000 bytes. `decodeInt16` assumes at least two bytes; callers guard chunk lengths before use. The checksum secret identifies format blocks but is not intended to be secret.

## Test Signals
`format_blob_test.go` covers recovery from standalone, prefix, and suffix positions plus bad checksums, missing blobs, and too-short blobs.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/repo/format/format_blob.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/repo/format/format_blob_cache.go -->
# sources/sync-backup/kopia/repo/format/format_blob_cache.go

## Purpose
Implements small caches for root repository format blobs, supporting null, in-memory, and on-disk modes.

## Important APIs, Types, And Functions
`DefaultRepositoryBlobCacheDuration` is 15 minutes. `blobCache` defines `Get`, `Put`, and `Remove`. Implementations are `nullCache`, `inMemoryCache`, and `onDiskCache`. Constructors are `NewDiskCache`, `NewMemoryBlobCache`, and `NewFormatBlobCache`.

## Control Flow
`nullCache` never returns stored data. `inMemoryCache` stores byte slices and modification times under a mutex. `onDiskCache` maps blob IDs to files under a cache directory, reads file contents and mtimes, writes atomically, creates the directory and cache marker on first write if needed, and removes selected files on invalidation. `NewFormatBlobCache` selects disk cache when `cacheDir` is non-empty, memory cache when valid duration is positive, else null cache.

## State And Persistence
Memory cache state is process-local maps. Disk cache state is files named after blob IDs in the cache directory.

## Dependencies And Integration Points
Depends on `atomicfile`, `cache`, `cachedir`, `clock`, and logging. `format.Manager` uses this cache to avoid frequent `kopia.repository` and `kopia.blobcfg` reads.

## Risks And Edge Cases
Disk cache trusts file names derived from blob IDs. Cached byte slices from memory are returned as stored, so callers should not mutate them. Cache validity is enforced by `Manager`, not by cache implementations themselves.

## Test Signals
`format_blob_cache_test.go` covers null, disk existing, disk missing-directory, and memory caches for get/put/overwrite/remove behavior and disk file cleanup.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/repo/format/format_blob_cache.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/repo/format/format_blob_cache_test.go -->
# sources/sync-backup/kopia/repo/format/format_blob_cache_test.go

## Purpose
Tests format blob cache implementations for durability, overwrite timestamp updates, retrieval, and removal.

## Important APIs, Types, And Functions
`TestFormatBlobCache` table-drives `NullCache`, `DiskCache-Exists`, `DiskCache-NotExists`, and `MemoryCache` cases.

## Control Flow
Each case starts with a missing get, writes two blobs, reads the first blob, sleeps to force a later mtime, overwrites the first blob, reads it again, removes it, and checks it is gone. After subtests, it asserts disk cache removed `blob1` but retained `blob2`.

## State And Persistence
Temporary directories hold disk cache files. Memory cache stores process-local entries. Null cache discards all writes.

## Dependencies And Integration Points
Uses `clock.Now`, `testutil.TempDirectory`, `testlogging`, and `blob.ID`. Tests the public cache constructors used by format managers.

## Risks And Edge Cases
The three-second sleep makes mtime comparison robust but slow. Null cache writes return a nonzero mtime but cannot be read back, which the test codifies. The test does not inject filesystem write/remove errors.

## Test Signals
Good coverage for intended cache semantics and disk directory creation. It does not cover concurrent cache access.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/repo/format/format_blob_cache_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/repo/format/format_blob_key_derivation_nontesting.go -->
# sources/sync-backup/kopia/repo/format/format_blob_key_derivation_nontesting.go

## Purpose
Defines production build defaults for deriving the format encryption key from a repository password.

## Important APIs, Types, And Functions
Under `!testing`, `DefaultKeyDerivationAlgorithm` is `crypto.ScryptAlgorithm`. `SupportedFormatBlobKeyDerivationAlgorithms` returns Scrypt and PBKDF2.

## Control Flow
No dynamic control flow beyond returning a slice of supported names.

## State And Persistence
The default KDF name is persisted into new `kopia.repository` blobs when initialization does not specify one.

## Dependencies And Integration Points
Depends on `internal/crypto`. `format.Initialize` uses this default when the format blob lacks `KeyDerivationAlgorithm`.

## Risks And Edge Cases
Build tags mean tests may use a weaker default than production. Production compatibility includes both Scrypt and PBKDF2 for existing repositories or API clients.

## Test Signals
Tests under the `testing` build tag use the alternate file, so production KDF cost is not exercised by the assigned tests.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/repo/format/format_blob_key_derivation_nontesting.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/repo/format/format_blob_key_derivation_testing.go -->
# sources/sync-backup/kopia/repo/format/format_blob_key_derivation_testing.go

## Purpose
Defines test-build defaults for format encryption key derivation, replacing production Scrypt with an insecure fast algorithm to speed tests.

## Important APIs, Types, And Functions
Under `testing`, `DefaultKeyDerivationAlgorithm` is `crypto.TestingOnlyInsecurePBKeyDerivationAlgorithm`.

## Control Flow
No functions are defined in this file.

## State And Persistence
When built with the `testing` tag, new test repositories persist the insecure KDF name unless explicitly overridden.

## Dependencies And Integration Points
Depends on `internal/crypto` and is consumed by `format.Initialize` through the shared constant name.

## Risks And Edge Cases
This file must never be used in production builds; the build tag separation is the safety boundary. It intentionally changes security/performance behavior for tests.

## Test Signals
Format manager and upgrade tests indirectly rely on this faster default under test builds.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/repo/format/format_blob_key_derivation_testing.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/repo/format/format_blob_test.go -->
# sources/sync-backup/kopia/repo/format/format_blob_test.go

## Purpose
Tests recovery of checksummed format blob bytes from standalone blobs and blobs with extra prefix or suffix bytes.

## Important APIs, Types, And Functions
`TestFormatBlobRecovery` uses `addFormatBlobChecksumAndLength` and `RecoverFormatBlob`.

## Control Flow
The test creates checksummed bytes from sample data, stores them as a standalone blob, as a suffix after extra bytes, and as a prefix before extra bytes. It also stores a corrupted checksum, a missing-name case, and blobs of length zero through five. Each case asserts either recovered original bytes or the expected error.

## State And Persistence
Uses `blobtesting.DataMap` and map storage to persist test blobs.

## Dependencies And Integration Points
Uses `gather`, `blob.PutOptions`, `testlogging`, and `pkg/errors` for `errors.Is`. It directly validates format blob recovery used when repository format bytes are embedded in pack data.

## Risks And Edge Cases
The test covers too-short blobs and bad checksums. It does not cover multiple blobs matching a prefix or explicit optional length values other than `-1`.

## Test Signals
Good focused coverage for recovery boundary behavior and checksum validation.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/repo/format/format_blob_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/repo/format/format_change_password.go -->
# sources/sync-backup/kopia/repo/format/format_change_password.go

## Purpose
Re-encrypts repository format and blob storage configuration with a new password-derived format encryption key.

## Important APIs, Types, And Functions
`Manager.ChangePassword(ctx, newPassword)` is the sole function.

## Control Flow
The manager mutex is held for the whole operation. The method rejects repositories without password-change support, derives a new format encryption key from the existing `KopiaRepositoryJSON`, updates in-memory key and password, encrypts repository config with the new key, writes encrypted `kopia.blobcfg`, writes `kopia.repository`, and removes both cached blobs.

## State And Persistence
Mutates in-memory manager password/key and persists both central format blobs. Existing content master key and HMAC secrets remain inside repository config but are re-encrypted under the new password-derived key.

## Dependencies And Integration Points
Depends on `blob.ID` constants and manager fields. Used by repository password rotation workflows; interacts with format cache invalidation and multi-manager cache expiry.

## Risks And Edge Cases
If writing blobcfg succeeds but writing repository blob fails, storage may temporarily contain blobcfg encrypted with the new key while repository config still points to old encrypted format bytes. The method updates in-memory password before all writes complete. Old managers with cached format can continue until their cache expires, as tested.

## Test Signals
`TestChangePassword` covers v3 password-change support, immediate cached readability by old/new managers, old-password failure after cache expiry, and failed new manager creation with the old password.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/repo/format/format_change_password.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/repo/format/format_manager.go -->
# sources/sync-backup/kopia/repo/format/format_manager.go

## Purpose
Implements the central manager for `kopia.repository` and `kopia.blobcfg`, including cached refresh, immutable crypto/hash provider exposure, mutable parameter reads, initialization, and repository config rewrites.

## Important APIs, Types, And Functions
`Manager` implements `format.Provider`. Important methods include `getOrRefreshFormat`, `maybeRefreshNotLocked`, `refresh`, `readAndCacheRepositoryBlobBytes`, provider getters, `RepositoryFormatBytes`, `GetMutableParameters`, `UpgradeLockIntent`, `RequiredFeatures`, `BlobCfgBlob`, `ObjectFormat`, `ScrubbedContentFormat`, `updateRepoConfigLocked`, `NewManager`, `NewManagerWithCache`, `Initialize`, and `randomBytes`.

## Control Flow
Reads call `maybeRefreshNotLocked`, which checks `validUntil` under a read lock and calls `refresh` when expired. Refresh reads and caches `kopia.repository`, parses JSON, wraps raw bytes with checksum for legacy embedding, derives or reuses the format key, decrypts repository config, optionally reads/decrypts blobcfg, constructs a static provider, updates current state, and initializes immutable provider on first load. Initialization verifies repository/blobcfg absence, fills default encryption/KDF/unique ID, derives the key, validates parameters and blob config, encrypts repository config, writes blobcfg, then writes repository blob.

## State And Persistence
Manager state is protected by `mu` and includes decrypted repository config, blob config, format key, current provider, cache validity, and refresh count. Persistent state is `kopia.repository` and `kopia.blobcfg`.

## Dependencies And Integration Points
Depends on `blob.Storage`, `blobCache`, encryption/hashing providers, feature flags, logging, and `gather`. It is the format source for content managers, repository initialization, password changes, retention updates, and upgrade locks.

## Risks And Edge Cases
The immutable provider is set only on first refresh, so immutable crypto/hash parameters intentionally do not change during a manager lifetime. Negative valid duration skips cache on first refresh; excessive durations are capped. `randomBytes` ignores `io.ReadFull` errors, which is low-probability but security-sensitive. Initialization writes blobcfg before repository blob, so corruption detection handles blobcfg-without-format as suspicious.

## Test Signals
`format_manager_test.go` covers cache expiry and refresh failures, retention initialization/update/validation, password changes, valid-duration capping, and accessor behavior.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/repo/format/format_manager.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/repo/format/format_manager_test.go -->
# sources/sync-backup/kopia/repo/format/format_manager_test.go

## Purpose
Tests format manager initialization, cache refresh semantics, mutable parameter updates, blob retention behavior, password changes, and cache duration normalization.

## Important APIs, Types, And Functions
Major tests are `TestFormatManager`, `TestInitialize`, `TestInitializeWithRetention`, `TestUpdateRetention`, `TestUpdateRetentionNegativeValue`, `TestChangePassword`, and `TestFormatManagerValidDuration`. Helpers read mutable parameters, upgrade lock intent, repository bytes, features, blob config, and raw storage bytes.

## Control Flow
`TestFormatManager` initializes storage, opens managers with shared memory cache, advances fake time around cache expiry, injects storage faults, updates parameters from another manager, and verifies visibility before/after cache expiration. Retention tests use versioned map storage to inspect retained blob settings. Password tests use two managers and cache expiry to prove old passwords fail after refresh.

## State And Persistence
Tests persist real `kopia.repository` and `kopia.blobcfg` blobs in map/versioned storage. Fake time controls cache mtimes and retention expected expiry.

## Dependencies And Integration Points
Uses `blobtesting.FaultyStorage`, `faketime`, `feature`, `gather`, default encryption/hashing, and format public APIs. It validates interactions between manager, cache, repository config encryption, and blob storage retention.

## Risks And Edge Cases
Tests cover fault injection on format/blobcfg existence checks and refresh reads. Negative retention update confirms failed validation leaves previous config in effect. Global package test variables are mutated in `TestChangePassword`, which can be order-sensitive if future tests rely on the old value without reset.

## Test Signals
Coverage is broad for manager lifecycle and state visibility. It does not cover disk cache within manager refresh; that is covered separately by cache tests.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/repo/format/format_manager_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/repo/format/format_provider.go -->
# sources/sync-backup/kopia/repo/format/format_provider.go

## Purpose
Defines repository format version constants, provider interface, and static formatting provider construction from `ContentFormat`.

## Important APIs, Types, And Functions
Constants define supported read/write versions and pack-size bounds. `Version` values are `FormatVersion1`, `FormatVersion2`, and `FormatVersion3`. `Provider` combines encryption, hashing, ECC, mutable-parameter, and repository-format-byte access. `NewFormattingOptionsProvider` validates and builds a `formattingOptionsProvider`.

## Control Flow
Provider construction clones the input content format, checks supported format and index versions, applies legacy defaults for index version and max pack size, creates hash function and encryptor, optionally wraps encryption with ECC, validates encryptor behavior by encrypting an empty payload using the empty content ID, and returns a static provider.

## State And Persistence
The provider stores cloned content format, hash function, encryptor, and original format bytes. `RepositoryFormatBytes` returns nil for password-change-capable repositories because they no longer embed format bytes in packs.

## Dependencies And Integration Points
Depends on `content/index`, `ecc`, `encryption`, `hashing`, and `gather`. `Manager.refresh` creates this provider after decrypting repository config; content managers consume it for content IDs and blob crypto.

## Risks And Edge Cases
Read and write version checks both reject unsupported versions. If ECC is enabled, the returned encryptor wrapper panics on fixed overhead. Empty-payload encryptor validation catches many misconfigurations early.

## Test Signals
Format manager tests exercise provider construction for several format versions. Encryption and ECC tests cover the lower-level algorithms used by providers.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/repo/format/format_provider.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/repo/format/format_set_parameters.go -->
# sources/sync-backup/kopia/repo/format/format_set_parameters.go

## Purpose
Updates mutable repository parameters, blob storage retention configuration, and required feature flags.

## Important APIs, Types, And Functions
`Manager.SetParameters(ctx, mp, blobcfg, requiredFeatures)` is the sole function.

## Control Flow
The method locks the manager, validates mutable parameters and blob config, updates in-memory repository config fields, encrypts repository config, writes `kopia.blobcfg`, updates in-memory blob config so the following repository blob write uses new retention settings, writes `kopia.repository`, and invalidates both cache entries.

## State And Persistence
Persists encrypted repository config and encrypted blobcfg. Also updates in-memory `repoConfig` and `blobCfgBlob`.

## Dependencies And Integration Points
Depends on `internal/feature`, blob retention config, and manager encryption/write helpers. Called by repository maintenance/configuration paths that change format version, pack size, epoch parameters, or retention.

## Risks And Edge Cases
The order intentionally writes blobcfg before repository blob. If repository blob write fails after blobcfg write and in-memory blob config update, state may be partially changed. Validation happens before mutation for parameters and blob config.

## Test Signals
`format_manager_test.go` covers mutable parameter visibility through cache windows, retention update success, and invalid retention rejection.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/repo/format/format_set_parameters.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/repo/format/object_format.go -->
# sources/sync-backup/kopia/repo/format/object_format.go

## Purpose
Defines object-level repository formatting options.

## Important APIs, Types, And Functions
`ObjectFormat` contains the `Splitter` string, which names the splitter used to break objects into content chunks.

## Control Flow
No functions or runtime control flow.

## State And Persistence
`ObjectFormat` is embedded in `RepositoryConfig` and persisted encrypted inside `kopia.repository`.

## Dependencies And Integration Points
Used by object writer/reader configuration through `format.Manager.ObjectFormat` and repository initialization options.

## Risks And Edge Cases
Invalid splitter names are not validated in this file; validation is expected where splitters are resolved.

## Test Signals
Upgrade-lock tests initialize repositories with `ObjectFormat{Splitter: "FIXED-1M"}` and then write objects, indirectly exercising persistence and retrieval.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/repo/format/object_format.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/repo/format/repository_config.go -->
# sources/sync-backup/kopia/repo/format/repository_config.go

## Purpose
Defines the encrypted repository configuration payload stored inside `kopia.repository`, including content format, object format, upgrade lock, and required feature flags.

## Important APIs, Types, And Functions
`RepositoryConfig` embeds `ContentFormat` and `ObjectFormat`, plus `UpgradeLock` and `RequiredFeatures`. `EncryptedRepositoryConfig` wraps it for JSON. Methods on `KopiaRepositoryJSON` are `decryptRepositoryConfig` and `EncryptRepositoryConfig`.

## Control Flow
Encryption JSON-marshals `EncryptedRepositoryConfig`, encrypts it with AES-GCM using the format encryption key and repository unique ID, and stores bytes in `EncryptedFormatBytes`. Decryption reverses that and returns generic errors for decrypt failure or wrapped JSON errors for invalid plaintext.

## State And Persistence
`EncryptedFormatBytes` is persisted in the public `kopia.repository` JSON. The decrypted fields include sensitive content master keys/HMAC secrets and operational fields like upgrade intent.

## Dependencies And Integration Points
Depends on `internal/feature` and format blob AES-GCM helpers. Used by `Manager.refresh`, `Initialize`, `SetParameters`, `ChangePassword`, and upgrade lock operations.

## Risks And Edge Cases
Only `AES256_GCM` is accepted here; other encryption algorithms fail. Generic decrypt errors help avoid exposing whether password/key or ciphertext was wrong. JSON schema changes must remain backward compatible with persisted configs.

## Test Signals
Format manager and password-change tests exercise successful encrypt/decrypt and invalid-password behavior through manager refresh.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/repo/format/repository_config.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/repo/format/upgrade_lock.go -->
# sources/sync-backup/kopia/repo/format/upgrade_lock.go

## Purpose
Implements repository format upgrade locking, backup, commit, rollback, and legacy-index poisoning. It coordinates exclusive upgrade access by writing lock intent into the repository format blob.

## Important APIs, Types, And Functions
Constants are `BackupBlobIDPrefix` and `LegacyIndexPoisonBlobID`. Errors include `ErrFormatUptoDate`. Functions/methods are `BackupBlobID`, `Manager.SetUpgradeLockIntent`, `WriteLegacyIndexPoisonBlob`, `Manager.CommitUpgrade`, `Manager.RollbackUpgrade`, and `Manager.GetUpgradeLockIntent`.

## Control Flow
Setting a lock refreshes format, validates intent, and if no lock exists, rejects already-current formats, writes a backup `kopia.repository.backup.<owner>`, stores the lock, and bumps repository config version to `MaxFormatVersion`. Existing locks are updated through `UpgradeLockIntent.Update`. Commit writes a legacy poison index blob, clears the lock, and rewrites config. Rollback lists backup blobs, retains the oldest backup, deletes newer backups, restores the format blob from the oldest backup, deletes that backup, and invalidates cache.

## State And Persistence
Persistent state includes the upgrade lock inside encrypted repository config, backup format blobs, and the legacy poison blob. Rollback primarily restores `kopia.repository`; it does not roll back repository data changes.

## Dependencies And Integration Points
Depends on `blob.Storage`, `gather`, manager refresh/update helpers, and `UpgradeLockIntent`. Repository open/write paths and older clients rely on format version bump and poison blob behavior.

## Risks And Edge Cases
Multiple locks/backups can exist when stale managers set locks from cached state; rollback chooses the oldest backup to restore the original format. Partial failures during backup, restore, or delete are surfaced. Rollback is explicitly dangerous after data format changes because it cannot undo content/index mutations.

## Test Signals
`upgrade_lock_test.go` covers setting/updating locks, already-upgraded rejection, commit/rollback behavior, multiple backup rollback, backup/restore/delete failures, and active writer interruption after lock refresh intervals.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/repo/format/upgrade_lock.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/repo/format/upgrade_lock_intent.go -->
# sources/sync-backup/kopia/repo/format/upgrade_lock_intent.go

## Purpose
Defines the upgrade lock intent data model and timing rules used to drain repository writers before a format upgrade.

## Important APIs, Types, And Functions
`UpgradeLockIntent` stores owner ID, creation time, advance notice, IO drain timeout, status poll interval, message, and max permitted clock drift. Methods are `Update`, `Clone`, `Validate`, `UpgradeTime`, `totalDrainInterval`, and `IsLocked`.

## Control Flow
Validation requires owner, creation time, positive IO drain timeout, poll interval not exceeding drain timeout, message, positive clock drift, and if advance notice is set, it must exceed total drain interval. Updates require the same owner, preserve whether advance notice was originally set, and only allow extending upgrade time. `UpgradeTime` is either creation plus advance notice or creation plus total drain interval. `IsLocked` reports immediate lock when advance notice is insufficient, otherwise lock begins at `advanceNotice - totalDrainInterval`, and writers are drained at `UpgradeTime`.

## State And Persistence
Lock intents are serialized inside encrypted repository config. The methods themselves are pure except for returning clones.

## Dependencies And Integration Points
Used by format manager upgrade operations and repository availability checks. Depends only on `time` and `pkg/errors`.

## Risks And Edge Cases
Invalid negative timing values can make `IsLocked` panic when writers appear drained but lock is false; validation is expected before persistence. Update rules currently only allow advance-notice extension, not owner changes or earlier upgrade time.

## Test Signals
`upgrade_lock_intent_test.go` covers validation errors, update restrictions, immediate/sufficient/insufficient advance lock timing, upgrade time calculation, nil clone/lock behavior, and the panic invariant.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/repo/format/upgrade_lock_intent.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/repo/format/upgrade_lock_intent_test.go -->
# sources/sync-backup/kopia/repo/format/upgrade_lock_intent_test.go

## Purpose
Validates upgrade lock intent mutation, validation, timing, and clone behavior.

## Important APIs, Types, And Functions
Tests include `TestUpgradeLockIntentUpdatesWithAdvanceNotice`, `TestUpgradeLockIntentUpdatesWithoutAdvanceNotice`, `TestUpgradeLockIntentValidation`, `TestUpgradeLockIntentImmediateLock`, `TestUpgradeLockIntentSufficientAdvanceLock`, `TestUpgradeLockIntentInSufficientAdvanceLock`, `TestUpgradeLockIntentUpgradeTime`, and `TestUpgradeLockIntentClone`.

## Control Flow
Tests construct lock intents with controlled times and durations, then assert allowed advance-notice extensions, rejected owner mismatch or earlier upgrade time, validation failures for missing fields, lock/writer-drained booleans at key timestamps, and upgrade-time results for immediate and advance-notice modes.

## State And Persistence
All state is in-memory `UpgradeLockIntent` structs; no repository storage is used.

## Dependencies And Integration Points
Uses `clock.Now` and public `format` package APIs. It locks down semantics used by repository open/write paths and format manager upgrade methods.

## Risks And Edge Cases
The tests include a panic case for invalid negative timeout inputs, documenting that callers must validate before calling timing logic on untrusted data. Sufficient advance-notice update can temporarily unlock a previously drained lock, and the test codifies that behavior.

## Test Signals
Coverage is strong for timing math and update policy. It does not test JSON serialization, which is handled indirectly through format manager tests.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/repo/format/upgrade_lock_intent_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/repo/format/upgrade_lock_test.go -->
# sources/sync-backup/kopia/repo/format/upgrade_lock_test.go

## Purpose
Integration-tests repository format upgrade lock behavior with real repository environments, storage backups, rollback, commit, and active write sessions.

## Important APIs, Types, And Functions
Tests include `TestFormatUpgradeSetLock`, `TestFormatUpgradeAlreadyUpgraded`, `TestFormatUpgradeCommit`, `TestFormatUpgradeRollback`, `TestFormatUpgradeMultipleLocksRollback`, `TestFormatUpgradeFailureToBackupFormatBlobOnLock`, and `TestFormatUpgradeDuringOngoingWriteSessions`. Helper `writeObject` writes object data through repository writers.

## Control Flow
Tests create repositories at specific format versions, set locks with valid/invalid owners, update advance notice, commit or roll back, reopen repositories to observe persisted state, and inspect backup blob lists. Failure tests wrap storage with before-operation hooks to force backup, restore, delete, or get errors. Active-session tests open multiple writers, set an upgrade lock from another client, verify writes flush before cache refresh notices the lock, advance time beyond format cache duration, and assert later flushes fail with repository-unavailable errors.

## State And Persistence
Uses real repository initialization over map/versioned/reconnectable storage. Persistent artifacts include format blobs, backup blobs, legacy poison blobs, object contents, and session-related state.

## Dependencies And Integration Points
Depends on `repotesting`, `repo`, `content`, `object`, `blobtesting`, `beforeop`, format manager APIs, and repository writer interfaces. This is the main integration signal for upgrade locks across format, content, and object layers.

## Risks And Edge Cases
Multiple-lock rollback demonstrates stale-cache clients can create multiple backups and rollback must pick the oldest. Failure injection shows rollback can be retried after transient failures. Active writer behavior depends on format cache duration and lock monitoring; writes already in flight may complete until clients refresh lock state.

## Test Signals
Coverage is broad and high-value for upgrade safety. It does not validate that legacy clients actually fail on the poison blob within this test file, but it verifies poison write is attempted during commit.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/repo/format/upgrade_lock_test.go -->
