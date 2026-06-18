# Research Report: subset-b-009163

This grouped report covers the requested restic repository, pack, repair, lock, prune, and core `internal/restic` primitives. Each source file has its own fenced section for deterministic splitting into source-tree-aligned per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/restic/internal/repository/key.go -->
# sources/sync-backup/restic/internal/repository/key.go

Purpose: manages repository key files: encrypted master keys stored as raw backend key files and unlocked from a user password. The central type is `Key`, containing metadata, scrypt KDF parameters, salt, encrypted master-key data, derived user key, master key, and backend ID.

Important APIs are `AddKey`, `LoadKey`, `RemoveKey`, `searchKey`, `openKey`, and `createMasterKey`. `AddKey` calibrates or reuses global scrypt parameters, fills host/user metadata, derives a user key, encrypts either a new or template master key, hashes the resulting JSON, and saves it as `KeyFile`. `searchKey` optionally resolves a prefix hint via `restic.Find`, then lists key files until one decrypts or limits are reached.

State and persistence are explicit: key JSON is saved directly through `repo.be.Save`, not through encrypted unpacked storage, because key files bootstrap encryption. Risks include global mutable KDF params, hint lookup ambiguity, password-authentication errors being used for iteration, and refusal to remove the active key. Integration points include repository initialization/opening, config loading, crypto KDF/seal/open, backend handles, and restic ID prefix search. Test signals are mostly indirect through repository test helpers that lower KDF parameters and open initialized repositories.
<!-- END_FILE_RESEARCH: sources/sync-backup/restic/internal/repository/key.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/restic/internal/repository/lock.go -->
# sources/sync-backup/restic/internal/repository/lock.go

Purpose: provides the high-level repository lock lifecycle, including acquisition retries, periodic refresh, stale-refresh recovery, and removal of stale or all locks. Public entry points are `LockRepo`, `RemoveStaleLocks`, and `RemoveAllLocks`; `Unlocker` is the user-facing interface.

Control flow in `locker.Lock` repeatedly calls `newLock`, handles `alreadyLockedError` with exponential backoff up to `retryLock`, wraps invalid locks into a fatal unlock hint, and returns a child context that is cancelled on unlock or failed refresh. Two goroutines manage lock health: `refreshLocks` periodically replaces the lock file and removes the old one; `monitorLockRefresh` uses wall-clock Unix time so host sleep does not hide refresh expiry. If a refresh becomes stale, `tryRefreshStaleLock` freezes freeze-capable backends while attempting safe replacement.

State is persisted in lock files via `lockHandle` from `lock_file.go`; this file owns runtime state, cancellation, and wait groups. Risks include goroutine coordination, wall-clock drift, backend latency during refresh, and correctly cancelling the caller before further repository mutations when lock refresh cannot be trusted. Tests in `lock_test.go` cover cancellation, conflicts, failed refresh, slow stale refresh recovery, retry timeout/cancel/success, stale-lock deletion, and force unlock.
<!-- END_FILE_RESEARCH: sources/sync-backup/restic/internal/repository/lock.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/restic/internal/repository/lock_file.go -->
# sources/sync-backup/restic/internal/repository/lock_file.go

Purpose: implements the persisted lock-file format and low-level locking algorithm. `Lock` is JSON-serialized with timestamp, exclusivity flag, host/user/process identifiers, and optional UID/GID. `lockHandle` binds a `Lock` to the repository and current lock ID.

Important APIs include `newLock`, `LoadLock`, `IsAlreadyLocked`, `TestSetLockTimeout`, `unlock`, `refresh`, `refreshStaleLock`, `stale`, and `forAllLocks`. `newLock` checks for conflicts, writes a lock file using `restic.SaveJSONUnpacked`, waits for backend consistency, then checks again. Non-exclusive locks can coexist; exclusive locks conflict with any other valid lock. `forAllLocks` lists locks in parallel but serializes callbacks and ignores zero-length lock files left by non-atomic uploads.

State transitions are create-lock, optionally replace-lock-on-refresh, adopt replacement by updating `lockID`, then remove old lock with a delayed cancellation context. Stale detection uses age, host equality, and platform-specific process liveness. Risks include unreadable locks being treated as blocking, delayed lock visibility on eventual-consistency backends, and safe cleanup if replacement creation succeeds but old-lock verification fails. Tests in `lock_file_test.go` exercise mutual exclusion, invalid/unreadable locks, stale decisions, refresh, and missing stale refresh cases.
<!-- END_FILE_RESEARCH: sources/sync-backup/restic/internal/repository/lock_file.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/restic/internal/repository/lock_file_test.go -->
# sources/sync-backup/restic/internal/repository/lock_file_test.go

Purpose: tests the low-level lock-file implementation independent of the high-level locker refresh supervisor. It creates in-memory test repositories, shortens lock timing with `TestSetLockTimeout`, and validates lock-file creation, conflict behavior, stale handling, and refresh behavior.

Important test cases include `TestLockFile`, `TestDoubleUnlock`, `TestMultipleLock`, `TestMultipleLockFailure`, `TestLockExclusive`, `TestLockOnExclusiveLockedRepo`, `TestExclusiveLockOnLockedRepo`, `TestLockStale`, `TestLockRefresh`, `TestLockRefreshStale`, and `TestLockRefreshStaleMissing`. The helper `failLockLoadingBackend` forces lock loads to fail to verify unreadable lock files prevent unsafe acquisition. `checkSingleLock` confirms only one lock remains after refresh.

State and persistence checks are direct: tests list lock files, remove locks, mutate timestamps and PIDs, and validate that stale replacement removes the old ID only when the old lock still exists. Risks covered include double unlock erroring, non-exclusive coexistence, exclusive exclusion, stale process recognition, invalid lock load handling, and cleanup after failed stale refresh. The suite is an important signal for eventual-consistency lock semantics.
<!-- END_FILE_RESEARCH: sources/sync-backup/restic/internal/repository/lock_file_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/restic/internal/repository/lock_file_unix.go -->
# sources/sync-backup/restic/internal/repository/lock_file_unix.go

Purpose: provides Unix process-liveness detection for stale repository locks. It is compiled for non-Windows platforms.

The file installs a process-wide SIGHUP listener in `init` via `sync.Once`, logging received SIGHUP signals so restic can probe its own processes without terminating. `lockHandle.processExists` calls `os.FindProcess`, sends `syscall.SIGHUP`, releases the process handle, and treats signal failure as evidence that the process is gone or unreachable.

State behavior is external to the repository: this only queries local OS process state to support `lockHandle.stale`. Integration points are `lock_file.go` stale detection and the debug logger. Risks include platform differences around `FindProcess` semantics, permission failures being treated as stale, and process-ID reuse; the host-name check in `stale` limits probes to locks from the current host. Tests exercise this path indirectly through stale-lock tests using current and fake PIDs.
<!-- END_FILE_RESEARCH: sources/sync-backup/restic/internal/repository/lock_file_unix.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/restic/internal/repository/lock_file_windows.go -->
# sources/sync-backup/restic/internal/repository/lock_file_windows.go

Purpose: provides Windows-specific process-liveness support for stale lock detection. Unlike Unix, it does not signal the process; it only attempts `os.FindProcess` and releases the handle.

`lockHandle.processExists` returns false if `FindProcess` fails and true otherwise, logging release errors but not using them as nonexistence. This is intentionally weaker than Unix probing because Windows process signaling semantics differ.

State and persistence behavior are limited to OS process inspection; repository lock state is owned by `lock_file.go`. Integration points are `lockHandle.stale`, the `os` package, and debug logging. Risks include Windows `FindProcess` reporting success for processes that have already exited or for PID reuse, causing stale locks to linger until timestamp expiry. The behavior is indirectly validated by stale-lock tests where build tags select the platform implementation.
<!-- END_FILE_RESEARCH: sources/sync-backup/restic/internal/repository/lock_file_windows.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/restic/internal/repository/lock_test.go -->
# sources/sync-backup/restic/internal/repository/lock_test.go

Purpose: validates the high-level lock supervisor in `lock.go`, including acquisition, context cancellation, retry behavior, refresh failure, slow backend recovery, stale lock deletion, and force unlock.

Important helpers are `openLockTestRepo`, `checkedLockRepo`, `writeOnceBackend`, `loggingBackend`, `slowBackend`, `createFakeLock`, `lockExists`, and `removeLock`. Tests cover ordinary unlock cancellation, parent context cancellation, exclusive/non-exclusive conflicts, failed periodic refresh cancelling the wrapped context, successful refresh under normal and stale timing, wait timeout/cancel/success semantics, removal of stale locks, and removal of all locks.

State and persistence checks use actual lock files in an in-memory backend, often reopening a repository to simulate multiple clients. The tests intentionally shorten refresh intervals and timeouts to make goroutine behavior observable. Risks covered include backend write failure after initial lock creation, refresh blocked longer than the safe timeout, retry backoff respecting cancellation, and ensuring fresh current-process locks are not removed as stale. These tests are strong integration signals for lock safety during long-running commands.
<!-- END_FILE_RESEARCH: sources/sync-backup/restic/internal/repository/lock_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/restic/internal/repository/pack/blob.go -->
# sources/sync-backup/restic/internal/repository/pack/blob.go

Purpose: defines `pack.Blob`, the pack-file header entry used internally by repository indexing and pack parsing. It embeds `restic.BlobHandle` and records encrypted length, offset within the pack data region, and optional uncompressed plaintext length.

Important methods are `String`, `DataLength`, `UncompressedCiphertextLength`, and `IsCompressed`. `DataLength` returns `UncompressedLength` for compressed blobs; otherwise it derives plaintext length from ciphertext length through `crypto.PlaintextLength`. `UncompressedCiphertextLength` computes the ciphertext size that the uncompressed data would occupy, useful for statistics and prune accounting. `IsCompressed` is encoded as nonzero `UncompressedLength`.

State is not persisted directly here, but this struct mirrors pack header entries and index entries. Integration points include pack header creation/parsing, `restic.PackBlob` implementations, repository blob streaming, prune size accounting, and index storage. Risks are correctness of length conversions and the overloaded meaning of zero uncompressed length, especially for zero-size blobs where compression is intentionally not represented.
<!-- END_FILE_RESEARCH: sources/sync-backup/restic/internal/repository/pack/blob.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/restic/internal/repository/pack/blobs.go -->
# sources/sync-backup/restic/internal/repository/pack/blobs.go

Purpose: defines `Blobs`, a slice of pack `Blob` entries, with a single `Sort` method ordering entries by offset.

The control flow is intentionally small: `Sort` uses `slices.SortFunc` and `cmp.Compare` on `Offset`. Sorting is required before streaming sections of a pack so the loader can read contiguous ranges, skip gaps, and detect overlapping entries.

There is no persistence in this file; it provides an ordering invariant for pack operations. Integration points include `Repository.LoadBlobsFromPack`, `streamPack`, pack tests, and prune/repack paths that pass sets of blobs by pack. Risks are limited but important: incorrect sorting would make range coalescing fail or cause false overlap errors. `blobs_test.go` verifies sorted offsets and nil-slice tolerance.
<!-- END_FILE_RESEARCH: sources/sync-backup/restic/internal/repository/pack/blobs.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/restic/internal/repository/pack/blobs_test.go -->
# sources/sync-backup/restic/internal/repository/pack/blobs_test.go

Purpose: tests the `Blobs.Sort` helper.

`TestBlobsSort` constructs three blobs with offsets 100, 0, and 50, calls `Sort`, and asserts ascending offsets. `TestBlobsSortNilSlice` calls `Sort` on a nil `Blobs` slice to ensure the helper is safe for empty inputs.

The test has no backend or persistence state. Its integration value is defensive: many repository streaming paths sort blob lists before range reads, and nil or empty inputs can appear in repack and selective load paths. The main risk covered is regressions in offset ordering that could lead to corrupted pack reads or overlap detection failures.
<!-- END_FILE_RESEARCH: sources/sync-backup/restic/internal/repository/pack/blobs_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/restic/internal/repository/pack/doc.go -->
# sources/sync-backup/restic/internal/repository/pack/doc.go

Purpose: declares package documentation for `internal/repository/pack`.

The package comment states that `pack` provides functions for combining and parsing pack files. There are no APIs, state transitions, or persistence side effects in this file, but it anchors package-level documentation for Go tooling.

Integration points are the rest of the `pack` package: `Packer`, `Blob`, `Blobs`, `PackedBlob`, and header parsing/listing. Risks are documentation drift only; behavior is entirely in sibling files. Test signals come from `pack_test.go`, `pack_internal_test.go`, and `blobs_test.go`.
<!-- END_FILE_RESEARCH: sources/sync-backup/restic/internal/repository/pack/doc.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/restic/internal/repository/pack/pack.go -->
# sources/sync-backup/restic/internal/repository/pack/pack.go

Purpose: implements the restic pack-file writer and reader. A pack stores encrypted blob payloads followed by an encrypted header and a 4-byte header-length footer.

Important APIs include `NewPacker`, `Packer.Add`, `Packer.Finalize`, `Packer.Merge`, `Packer.Size`, `Packer.Count`, `Packer.HeaderFull`, `Packer.Blobs`, `List`, `CalculateEntrySize`, `CalculateHeaderSize`, and `Size`. Header entries encode blob type and length, with extra uncompressed length for compressed blobs. `Finalize` encrypts and appends the header, then verifies it by decoding it back with `List` before writing.

Control flow on read starts with `readHeader`, which eagerly reads the footer plus a small header window and only issues a second read for large headers. `List` decrypts the header, parses entries sequentially, and reconstructs offsets. `Size` computes pack sizes from index data.

State is persisted in the pack byte layout; errors mark a `Packer` as broken and future calls return `ErrBroken`. Risks include header length validation, compressed-entry compatibility, short writes, and max header size. Tests cover header parsing, eager reads, invalid headers, broken writers, pack creation, merge, and header self-verification.
<!-- END_FILE_RESEARCH: sources/sync-backup/restic/internal/repository/pack/pack.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/restic/internal/repository/pack/pack_internal_test.go -->
# sources/sync-backup/restic/internal/repository/pack/pack_internal_test.go

Purpose: tests unexported pack header parsing, footer/header reading, and header verification.

`TestParseHeaderEntry` validates plain and compressed header layouts. `TestParseHeaderEntryErrors` checks invalid type bytes and truncated input. `countingReaderAt` supports `TestReadHeaderEagerLoad`, which asserts when header reading needs one or two random-access reads based on `eagerEntries`. `TestReadRecords` exercises truncation and total-header-size reporting across data/header sizes. `TestUnpackedVerification` damages header plaintext, ciphertext, and length footer to ensure `verifyHeader` detects mismatches or decode failures.

State is in synthetic byte buffers, not a backend, but the tests model persisted pack bytes precisely. Integration risks covered include unnecessary extra backend reads, malformed or oversized headers, compressed header entry sizes, and write-time header corruption detection before upload.
<!-- END_FILE_RESEARCH: sources/sync-backup/restic/internal/repository/pack/pack_internal_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/restic/internal/repository/pack/pack_test.go -->
# sources/sync-backup/restic/internal/repository/pack/pack_test.go

Purpose: tests exported pack creation, listing, backend-backed random reads, JSON blob type compatibility, writer failure behavior, and pack merging.

Key helpers are `createBuffers`, `newPack`, and `verifyBlobs`. `TestCreatePack` writes random blobs and verifies decoded header entries, lengths, offsets, and payload bytes. `TestUnpackReadSeeker` saves a pack to an in-memory backend and reads it through `backend.ReaderAt`. `TestShortPack` checks a single-blob pack. `TestPackerBroken` verifies the first write error is recorded and subsequent `Add`/`Finalize` return `ErrBroken`. `TestPackMerge` merges two packers and confirms all blobs remain readable.

Persistence behavior is represented by actual pack bytes and backend save/load. Risks covered include offset/header consistency, compressed-entry accounting, broken writer reuse, and merge reading from another packer's data stream. These tests give high confidence that pack files created by repository upload code are parseable by index repair and load paths.
<!-- END_FILE_RESEARCH: sources/sync-backup/restic/internal/repository/pack/pack_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/restic/internal/repository/pack/packedblob.go -->
# sources/sync-backup/restic/internal/repository/pack/packedblob.go

Purpose: adapts internal pack blob metadata to the public `restic.PackBlob` interface used by repository, prune, and index consumers.

`PackedBlob` combines a pack ID with a `Blob`. Methods expose `PackID`, `Handle`, `CiphertextLength`, `UncompressedCiphertextLength`, `PlaintextLength`, and `IsCompressed`. The compile-time assertion ensures interface conformance.

There is no direct persistence here; it is a view over index entries and pack headers. Integration points include `Repository.LookupBlob`, `Repository.ListBlobs`, `pack.Size`, prune statistics, and associated blob sets. Risks are mainly semantic: consumers intentionally do not see blob offsets through `restic.PackBlob`, which prevents leaking pack internals but means offset-sensitive code must use `pack.Blob` internally.
<!-- END_FILE_RESEARCH: sources/sync-backup/restic/internal/repository/pack/packedblob.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/restic/internal/repository/packer_manager.go -->
# sources/sync-backup/restic/internal/repository/packer_manager.go

Purpose: manages open packers for blob writes, temporary pack files, random blob distribution across packers, flush-time pack merging, and final pack upload/index update.

Important types are local `packer` and `packerManager`. APIs include `newPackerManager`, `SaveBlob`, `Flush`, `mergePackers`, `pickPacker`, `newPacker`, `forgetPacker`, and `Repository.savePacker`. `SaveBlob` selects a packer, adds ciphertext, queues full/header-full packers, and reports storage size. `pickPacker` places oversized blobs in dedicated packs and otherwise randomly selects one of several open packers to reduce chunk-boundary leakage. `mergePackers` merges small pending packers during flush to reduce size leakage for small files.

State is persisted through temp files first, then `savePacker` finalizes the pack, hashes the pack bytes, saves it as `PackFile`, closes the temp file, and stores blob entries in the master index. Risks include lock contention, temp file cleanup on errors, random selection errors, pack merging correctness, and index/backend consistency after upload. Tests and benchmarks in `packer_manager_test.go` validate accounting and oversize behavior.
<!-- END_FILE_RESEARCH: sources/sync-backup/restic/internal/repository/packer_manager.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/restic/internal/repository/packer_manager_test.go -->
# sources/sync-backup/restic/internal/repository/packer_manager_test.go

Purpose: tests and benchmarks the packer manager's pack filling, flush, and accounting behavior.

`fillPacks` writes 102 random data blobs up to 1 MiB into a manager and validates `SaveBlob` byte accounting against blob length plus header-entry overhead, with optional final pack header overhead. `TestPackerManager` records total size once for benchmark reuse. `TestPackerManagerWithOversizeBlob` exercises the dedicated-packer path for blobs at or above the pack size. `BenchmarkPackerManager` measures repeated pack creation and flushing.

The tests use a `queueFn` that finalizes packers and accumulates size instead of saving to a backend. State coverage focuses on open packers, flush behavior, and pack sizes. Risks covered include invalid byte accounting, packer exhaustion, oversize blob treatment, and merge/flush output size mismatches.
<!-- END_FILE_RESEARCH: sources/sync-backup/restic/internal/repository/packer_manager_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/restic/internal/repository/packer_uploader.go -->
# sources/sync-backup/restic/internal/repository/packer_uploader.go

Purpose: implements asynchronous pack upload fan-out for finalized packers.

Important types are `savePacker`, `uploadTask`, and `packerUploader`. `newPackerUploader` creates a buffered task channel sized to twice the backend connection count and starts one worker goroutine per connection in the provided errgroup. Each worker reads tasks and calls `repo.savePacker`. `QueuePacker` sends tasks unless the context is cancelled; `TriggerShutdown` closes the queue.

State is in the queue and worker goroutines. Persistence happens through the repository's `savePacker`, which writes pack files and updates the index. Integration points are `Repository.startPackUploader`, `packerManager.SaveBlob`, `flushPackUploader`, and `WithBlobUploader`. Risks include queue closure ordering, backpressure while holding the packer manager lock, context cancellation losing pending uploads, and ensuring all workers drain before index flush. Repository async-save tests indirectly cover upload shutdown and error propagation.
<!-- END_FILE_RESEARCH: sources/sync-backup/restic/internal/repository/packer_uploader.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/restic/internal/repository/prune.go -->
# sources/sync-backup/restic/internal/repository/prune.go

Purpose: plans and executes repository pruning: deciding which packs to keep, repack, remove, or ignore, while preserving all used blobs and rewriting indexes.

Important APIs and types include `PruneOptions`, `PruneStats`, `PrunePlan`, `PlanPrune`, `packInfoFromIndex`, `calculateTargetPacksize`, `decidePackAction`, `PrunePlan.Execute`, and `deleteFiles`. `PlanPrune` obtains used blobs from a caller callback, derives per-pack usage and duplicate accounting from the index, selects actions, adjusts keep blobs for repacking, and calculates JSON-ready summary stats. `packInfoFromIndex` verifies every used blob exists, handles duplicate blob selection, and computes sizes. `decidePackAction` validates listed packs against index sizes, identifies unreferenced or missing packs, prioritizes repack candidates, and respects max unused/repack limits and compression repair needs.

Execution removes unreferenced packs first, repacks selected packs via `CopyBlobs`, rewrites or deletes indexes, removes old packs, optionally rebuilds fallback indexes for unsafe recovery, and clears the in-memory index. Risks include preventing data loss when indexes are incomplete, duplicate accounting, missing pack handling, dry-run differences, context cancellation, and pack size heuristics. Tests cover normal prune, small packs, duplicate MaxUnused accounting, and recovery-related paths.
<!-- END_FILE_RESEARCH: sources/sync-backup/restic/internal/repository/prune.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/restic/internal/repository/prune_internal_test.go -->
# sources/sync-backup/restic/internal/repository/prune_internal_test.go

Purpose: tests a subtle prune accounting case involving duplicate used blobs.

`TestPruneMaxUnusedDuplicate` constructs packs containing distinct used blobs plus a duplicated blob across all packs. It forces one packer, writes large blobs to avoid small-pack repacking, and marks all blobs as used. The prune options allow some unused bytes but less than one blob. The test asserts the plan repacks duplicates correctly rather than treating all duplicated storage as tolerable unused space.

State is a real test repository with blob upload and index state. The test targets `packInfoFromIndex` and `decidePackAction` duplicate handling, especially the logic that keeps one occurrence of a duplicate and marks the rest removable. Risk covered: a prune plan could leave duplicate data behind or incorrectly remove all copies if duplicate counters and global size stats drift.
<!-- END_FILE_RESEARCH: sources/sync-backup/restic/internal/repository/prune_internal_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/restic/internal/repository/prune_test.go -->
# sources/sync-backup/restic/internal/repository/prune_test.go

Purpose: integration-tests pruning behavior over generated repositories.

`testPrune` creates random blobs, chooses a subset as used, optionally inserts broken/wrong data, builds a `PruneOptions` plan, executes it, reloads indexes, and verifies kept blobs remain while unused packs are removed according to options. `TestPrune` covers multiple option combinations such as MaxUnused, MaxRepack, cacheable-only, unsafe recovery, and uncompressed repacking. `TestPruneSmall` checks small-pack behavior and the threshold that avoids endless repacking for too few small packs.

State and persistence are full repository state: pack files, index files, blob sets, and backend removal. Integration points include `PlanPrune`, `PrunePlan.Execute`, `CopyBlobs`, `RepairIndex`, and repository checker helpers. Risks covered include data-loss prevention, removing stale indexes, unreferenced pack deletion, pack rewrite correctness, and option-specific pruning behavior across repository versions.
<!-- END_FILE_RESEARCH: sources/sync-backup/restic/internal/repository/prune_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/restic/internal/repository/raw.go -->
# sources/sync-backup/restic/internal/repository/raw.go

Purpose: loads raw backend bytes for a repository file without decrypting or parsing, with integrity verification against the file ID for all non-config files.

`Repository.LoadRaw` builds a backend handle, calls `loadRaw`, checks `restic.Hash(buf)` against the requested ID, forgets cached data if present on mismatch, retries once, and returns corrupted bytes with `restic.ErrInvalidData` if the second read still mismatches. Config files are exempt because their ID is the null ID and they bootstrap repository metadata. `loadRaw` reads the full object through `backend.Load` into a `bytes.Buffer`.

State is read-only, except cache invalidation. Integration points include key loading, config backup during upgrades, unpacked file loading, raw repair workflows, and tests that simulate transient corruption. Risks include memory use for full-file loads, relying on hash ID for integrity, and preserving corrupt bytes so repair code can inspect them. Tests validate normal loads, corrupted retry, error wrapping, and cache forget-on-retry.
<!-- END_FILE_RESEARCH: sources/sync-backup/restic/internal/repository/raw.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/restic/internal/repository/raw_test.go -->
# sources/sync-backup/restic/internal/repository/raw_test.go

Purpose: tests raw backend loading and corruption retry behavior.

`TestLoadRaw` saves random pack files to a memory backend and confirms `LoadRaw` returns exact bytes. `TestLoadRawBroken` uses a mock backend to return corrupted bytes, validates the corrupt data is returned with `restic.ErrInvalidData` after repeated mismatch, then simulates transient corruption fixed on the second read. `TestLoadRawBrokenWithCache` enables cache wrapping and verifies the retry path still succeeds after the first corrupted cached read.

State includes backend objects and optional cache state. Risks covered include missing retry on damaged data, losing diagnostic corrupt bytes, failing to clear cache before retry, and accidentally applying ID checks to config files. These tests are a signal for repository robustness against transient backend/cache corruption.
<!-- END_FILE_RESEARCH: sources/sync-backup/restic/internal/repository/raw_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/restic/internal/repository/repack.go -->
# sources/sync-backup/restic/internal/repository/repack.go

Purpose: copies selected blobs out of selected packs into new packs, used by prune and repair workflows.

Important APIs are `CopyBlobs` and internal `repack`. The caller supplies source repository, destination repository/uploader, pack IDs, and a mutable `keepBlobs` set. `CopyBlobs` checks connection count for same-repository repacks, sets progress max, and delegates. `repack` optionally warms up cold-storage packs, lists target packs from the index, filters each pack's blob list against `keepBlobs`, and starts download workers. Each worker loads blobs from packs, rechecks/deletes the keep marker under a mutex so duplicates are saved once, and saves required blobs with `storeDuplicate=true`.

State changes are in destination packs and the caller's keep set; this function does not remove old packs or rewrite indexes directly. Integration points include `PrunePlan.Execute`, `RepairPacks`, repository warmup, `LoadBlobsFromPack`, and async blob uploading. Risks include concurrent duplicate handling, ensuring uploads can proceed by reserving one connection, context cancellation, cold-storage waits, and leaving unrepacked blobs detectable by a non-empty keep set. Tests in `repack_test.go` cover random selection, empty repacks, wrong blobs, and repair interactions.
<!-- END_FILE_RESEARCH: sources/sync-backup/restic/internal/repository/repack.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/restic/internal/repository/repack_test.go -->
# sources/sync-backup/restic/internal/repository/repack_test.go

Purpose: integration-tests repacking and helper functions used by prune and repair tests.

Helpers create random blobs across pack files, split blob sets, list packs/indexes, find packs containing selected blobs, run `CopyBlobs`, remove old packs, and rebuild/reload indexes. `TestRepack` verifies empty repacks are no-ops, then repacks selected packs while keeping chosen blobs and checks repository consistency. Additional tests exercise wrong blob IDs, missing blobs, and combinations that ensure only requested blobs survive after index rebuild.

State is full repository state with pack files and indexes; tests intentionally mutate backend state by removing old packs after copy. Integration points include `CopyBlobs`, `RepairIndex`, `ListPackHandles`, `LookupBlob`, and checker validation. Risks covered include duplicate or missing blob handling, data preservation during pack replacement, index repair after manual pack removal, and cross-version behavior via `TestAllVersions`.
<!-- END_FILE_RESEARCH: sources/sync-backup/restic/internal/repository/repack_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/restic/internal/repository/repair_index.go -->
# sources/sync-backup/restic/internal/repository/repair_index.go

Purpose: rebuilds or repairs repository index files by comparing index references with actual pack files and optionally reading all packs from scratch.

Important APIs are `RepairIndex`, `RepairIndexOptions`, and `rewriteIndexFiles`. In `ReadAllPacks` mode, existing index IDs are remembered as obsolete and the in-memory index is cleared. Otherwise, indexes are loaded with a callback that marks invalid indexes obsolete, then pack sizes are computed from index contents. The repair scans backend pack files, identifies missing/unindexed/size-mismatched packs, reindexes packs that need reading via `createIndexFromPacks`, and removes references to packs absent from the backend.

State changes include new index files, deletion of obsolete/old indexes via `MasterIndex.Rewrite`, and clearing the in-memory index after completion. Integration points include pack header parsing, repository index load/flush, prune's index rewrite path, and progress reporting. Risks include losing valid index entries, retaining missing-pack references, handling damaged indexes without aborting, and ensuring invalid pack files are skipped rather than indexed. Tests in `repair_index_test.go` cover valid, damaged, missing index, and missing pack cases in both modes.
<!-- END_FILE_RESEARCH: sources/sync-backup/restic/internal/repository/repair_index.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/restic/internal/repository/repair_index_test.go -->
# sources/sync-backup/restic/internal/repository/repair_index_test.go

Purpose: tests `RepairIndex` against common repository index damage scenarios.

`listIndex` lists index file IDs. `testRebuildIndex` creates random blobs, records old indexes, applies a damage function, reopens the backend, runs `RepairIndex` with either normal or `ReadAllPacks` mode, and validates the repository with `TestCheckRepo`. `TestRebuildIndex` runs scenarios for a valid index, damaged index bytes, a missing index file, and a missing pack file.

State and persistence are real backend mutations: files are damaged via `replaceFile` or removed. Integration points include repository reopen, index load callbacks, pack scanning, index rewrite, and checker validation. Risks covered include failure to recover from damaged indexes, dangling pack references, and mode differences between incremental repair and full pack reread.
<!-- END_FILE_RESEARCH: sources/sync-backup/restic/internal/repository/repair_index_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/restic/internal/repository/repair_pack.go -->
# sources/sync-backup/restic/internal/repository/repair_pack.go

Purpose: salvages intact blobs from specified pack files and then repairs indexes to drop broken pack references.

`RepairPacks` iterates requested pack IDs, loads pack entries from the index, attempts to copy all listed blobs through `CopyBlobs`, tracks successfully copied blobs, removes damaged pack files, and runs `RepairIndex` afterward to rebuild index state. It treats `io.ErrUnexpectedEOF` and corrupted blobs as salvageable failures where remaining valid blobs may still be copied; other errors are returned.

State changes include new replacement packs for successfully recovered blobs, deletion of specified bad pack files, and index rewrite through repair. Integration points are `CopyBlobs`, `LoadBlobsFromPack`, `RepairIndex`, progress counters, and backend pack removal. Risks include distinguishing expected corruption from fatal backend errors, avoiding deletion before recovery attempts, and ensuring already copied blobs are not lost if later blobs fail. Tests corrupt pack bytes and verify remaining blob sets after repair.
<!-- END_FILE_RESEARCH: sources/sync-backup/restic/internal/repository/repair_pack.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/restic/internal/repository/repair_pack_test.go -->
# sources/sync-backup/restic/internal/repository/repair_pack_test.go

Purpose: tests pack salvage from broken pack files.

Helpers include `listBlobs`, which lists all indexed blobs, and `replaceFile`, which loads a backend file, mutates bytes, removes the original, and saves the damaged bytes back under the same handle. `TestRepairBrokenPack` delegates to versioned tests that create repositories, damage selected pack content, run `RepairPacks`, reload indexes, and compare blob sets before and after.

State is intentionally corrupted pack persistence in the backend. Integration points include pack loading, blob copy fallback, backend removal, repair index, and checker validation. Risks covered include failing to salvage intact blobs from partially damaged packs, leaving corrupted pack references in indexes, and version-specific differences in compressed/uncompressed pack contents.
<!-- END_FILE_RESEARCH: sources/sync-backup/restic/internal/repository/repair_pack_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/restic/internal/repository/repository.go -->
# sources/sync-backup/restic/internal/repository/repository.go

Purpose: central repository implementation for backend access, encryption, compression, pack upload, index loading, blob save/load, config/key integration, and streaming pack reads.

Key types are `Repository`, `internalRepository`, `Options`, `CompressionMode`, `blobSaverRepo`, `associatedBlobSet`, `byteReader`, and `packBlobIterator`. Important APIs include `New`, `UseCache`, `LoadUnpacked`, `LoadBlob`, `SaveUnpacked`, `WithBlobUploader`, `flush`, `LoadIndex`, `createIndexFromPacks`, `SearchKey`, `Init`, `List`, `ListPackHandles`, `saveBlob`, `SaveBlobAsync`, `LoadBlobsFromPack`, and `ZeroChunk`.

Control flow for saving blobs computes or accepts plaintext IDs, reserves pending index entries to suppress duplicates, compresses in repo v2, encrypts and verifies ciphertext, then queues into data/tree packer managers. `WithBlobUploader` coordinates async blob saving, pack uploader workers, final flush, and index flush. Load paths prefer cached packs, retry after cache eviction on failures, decrypt/decompress, and verify hashes. Multi-blob pack streaming coalesces nearby ranges, skips large gaps, detects overlaps, and falls back to `LoadBlob` for corrupted ranges when possible.

State and persistence include backend config/key/index/pack files, in-memory master index, cache wrapping, zstd encoder/decoder singletons, pending blob entries, temp pack files, and async goroutines. Risks include duplicate suppression correctness, context cancellation, compression compatibility with repo versions, cache invalidation, pack range math, and index/backend consistency. Extensive repository tests cover save/load, cache retry, incremental indexes, async saves, verification, streaming, and initialization safeguards.
<!-- END_FILE_RESEARCH: sources/sync-backup/restic/internal/repository/repository.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/restic/internal/repository/repository_internal_test.go -->
# sources/sync-backup/restic/internal/repository/repository_internal_test.go

Purpose: tests internal repository helpers that are not exposed through the external repository package API, especially cached-pack ordering, index load benchmarks, streaming pack reads, and write-time verification.

Important tests include `TestSortCachedPacksFirst`, `BenchmarkLoadIndex`, `TestStreamPack`, `TestBlobVerification`, `TestUnpackedVerification`, and `TestStreamPackFallback`. `buildPackfileWithoutHeader` constructs deterministic encrypted blob sequences for streaming tests. `TestStreamPack` verifies range coalescing, sorting, split behavior for distant blobs, short read retry behavior, and invalid inputs such as duplicate/overlapping entries or too-short blobs. Verification tests damage plaintext, compressed bytes, and ciphertext to check error classification.

State is mostly synthetic pack bytes and test repositories. Integration points include zstd, crypto keys, backend load callbacks, `streamPack`, `verifyCiphertext`, `verifyUnpacked`, and cache handling. Risks covered include corrupted data detection, fallback to alternate blob copies, overlapping range defense, excessive backend reads, and verification bypass regressions.
<!-- END_FILE_RESEARCH: sources/sync-backup/restic/internal/repository/repository_internal_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/restic/internal/repository/repository_test.go -->
# sources/sync-backup/restic/internal/repository/repository_test.go

Purpose: broad integration and benchmark coverage for the public repository API.

Tests cover saving blobs with supplied or computed IDs, zero-size blob round-trip, flush-time pack merging, save/load benchmarks, variable caller buffer sizes in `LoadBlob`, cache retry on damaged first reads, loading index fixtures, broken unpacked files, retrying transient unpacked corruption, incremental index flushes, invalid compression options, pack handle listing, initialization safeguards, and async blob save callbacks/error handling. Helpers include `damageOnceBackend`, `saveRandomDataBlobs`, and test fixture loading.

State and persistence are realistic: initialized repositories, backend files, cache wrappers, indexes, pack files, config/key files, and async upload goroutines. Integration points span most files in this subset: key/config open, pack manager, pack parser, raw load retry, index flushing, cache clearing, compression, and blob verification. Risks covered include double initialization, corrupted cached data, pack merge counts, duplicate index entries across index files, context cancellation in async saves, and compatibility across repo versions.
<!-- END_FILE_RESEARCH: sources/sync-backup/restic/internal/repository/repository_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/restic/internal/repository/testing.go -->
# sources/sync-backup/restic/internal/repository/testing.go

Purpose: provides repository test helpers for creating, opening, and validating repositories across versions and backends.

Important APIs include `TestUseLowSecurityKDFParameters`, `TestBackend`, `TestRepositoryWithBackend`, `TestRepository`, `TestRepositoryWithVersion`, `TestFromFixture`, `TestOpenLocal`, `TestOpenBackend`, `TestAllVersions`, `BenchmarkAllVersions`, and `TestCheckRepo`. Helpers configure low-cost scrypt params, disable chunker polynomial validation for tests, initialize memory or local backends, open existing fixtures, and run checker passes over indexes and pack contents.

State and persistence are test-scoped repositories, optional `RESTIC_TEST_REPO` local directories, config/key files, and low-security global key params. Integration points include backend factories, retry/local/memory backends, repository initialization/opening, checker loading, and versioned test loops. Risks include global test configuration leaking across tests, leaving local test repositories for inspection, and tests depending on lowered KDF cost. This file is a key signal for how production APIs are expected to be assembled in tests.
<!-- END_FILE_RESEARCH: sources/sync-backup/restic/internal/repository/testing.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/restic/internal/repository/upgrade_repo.go -->
# sources/sync-backup/restic/internal/repository/upgrade_repo.go

Purpose: upgrades repository config from format version 1 to version 2, with a local config backup and rollback attempt on upload failure.

Important APIs are `UpgradeRepo`, internal `upgradeRepository`, and `upgradeRepoV2Error`. `UpgradeRepo` validates the repo is version 1, creates a temp dir, loads the raw config file, writes a backup file, then calls `upgradeRepository`. `upgradeRepository` removes the config first for backends without atomic replace, changes config version to 2, and saves it encrypted through `restic.SaveConfig`.

State and persistence include the backend config file and a local temporary backup. On failure, `UpgradeRepo` removes any partial config and attempts to reupload the original raw bytes; errors report both the new-upload failure and rollback failure plus backup path. Risks include non-atomic replace windows, rollback failure, temporary backup cleanup, and only supporting v1-to-v2 upgrades. Tests cover successful upgrade and injected config-save failure with backup path reporting.
<!-- END_FILE_RESEARCH: sources/sync-backup/restic/internal/repository/upgrade_repo.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/restic/internal/repository/upgrade_repo_test.go -->
# sources/sync-backup/restic/internal/repository/upgrade_repo_test.go

Purpose: tests repository config upgrade success and failure recovery.

`TestUpgradeRepoV2` creates a version 1 repository and verifies `UpgradeRepo` succeeds. `failBackend` wraps a backend and fails config-file saves after a configurable number of successful saves. `TestUpgradeRepoV2Failure` uses that wrapper so the initial repository creation succeeds but upgrade and rollback save fail, then asserts an `upgradeRepoV2Error` contains upload error, reupload error, and backup path. The test removes the backup file and directory afterward.

State is backend config persistence plus local temporary backup files. Integration points include `UpgradeRepo`, backend `Save`, raw config loading, config backup, and error wrapping. Risks covered include failure after removing/replacing config, missing backup reporting, and rollback errors being preserved for the caller.
<!-- END_FILE_RESEARCH: sources/sync-backup/restic/internal/repository/upgrade_repo_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/restic/internal/repository/warmup.go -->
# sources/sync-backup/restic/internal/repository/warmup.go

Purpose: exposes repository-level cold-storage warmup for pack files.

`warmupJob` implements `restic.WarmupJob` with `HandleCount` and `Wait`. `Repository.StartWarmup` converts a set of pack IDs to backend pack handles, calls `Backend.Warmup`, and returns a job containing only the handles still warming up. `Wait` delegates to `Backend.WarmupWait`.

State is backend-managed warmup state; the repository stores only the handles returned by the backend. Integration points include `CopyBlobs` when the S3 restore feature flag is enabled and any backend implementing cold storage restore. Risks include backend-specific semantics, unordered ID sets, context cancellation during warmup wait, and ensuring callers handle zero-handle jobs without unnecessary waits. Tests in `warmup_test.go` validate handle conversion and wait delegation.
<!-- END_FILE_RESEARCH: sources/sync-backup/restic/internal/repository/warmup.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/restic/internal/repository/warmup_test.go -->
# sources/sync-backup/restic/internal/repository/warmup_test.go

Purpose: tests repository warmup delegation to backend warmup APIs.

The test backend records handles passed to `Warmup` and `WarmupWait`. Tests create pack ID sets, call `StartWarmup`, inspect `HandleCount`, and call `Wait` to verify the same backend handles are used. Scenarios include empty pack sets and non-empty sets.

State is mock backend call recording, not persisted repository data. Integration points include `Repository.StartWarmup`, backend `Warmup`, backend `WarmupWait`, and `restic.WarmupJob`. Risks covered include incorrect handle type/name construction, losing returned handles, and waiting on the wrong handle list.
<!-- END_FILE_RESEARCH: sources/sync-backup/restic/internal/repository/warmup_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/restic/internal/restic/backend_find.go -->
# sources/sync-backup/restic/internal/restic/backend_find.go

Purpose: resolves an ID prefix to a unique repository file ID of a given file type.

Important APIs are `Find`, `MultipleIDMatchesError`, and `NoIDByPrefixError`. `Find` creates a cancellable child context, lists all files of the requested type through `Lister`, compares the requested prefix against full hex IDs, records the first match, and errors on a second match. It returns a null ID with either a no-match or multiple-match error when resolution is not unique.

State is read-only; cancellation is local and would allow future optimization but currently only stops through list error propagation. Integration points include key hint lookup, CLI commands resolving snapshots/locks/indexes by prefix, and tests using `ListHelper`. Risks include case sensitivity, prefixes longer than IDs, duplicate prefixes, and backend list errors. Tests in `backend_find_test.go` cover exact unique prefix, no match, too-long prefix, and ambiguous prefix.
<!-- END_FILE_RESEARCH: sources/sync-backup/restic/internal/restic/backend_find.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/restic/internal/restic/backend_find_test.go -->
# sources/sync-backup/restic/internal/restic/backend_find_test.go

Purpose: tests prefix-based ID lookup.

The test defines sample IDs and a `ListHelper` whose `ListFn` returns those IDs. `TestFind` verifies a unique long prefix returns the expected ID, an invalid prefix returns `NoIDByPrefixError` with a null ID, a prefix longer than any ID is also no-match, and a short prefix matching multiple sample IDs returns `MultipleIDMatchesError` with a null ID.

State is an in-memory slice of IDs. Integration points are `Find`, `Lister`, error types, and ID parsing. Risks covered include accidental partial match behavior for overlong prefixes, returning stale previous matches on error, and failing to distinguish no-match from ambiguity.
<!-- END_FILE_RESEARCH: sources/sync-backup/restic/internal/restic/backend_find_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/restic/internal/restic/blob.go -->
# sources/sync-backup/restic/internal/restic/blob.go

Purpose: defines repository blob identity and blob metadata interfaces shared by repository, index, pack, prune, and repair code.

Important types are `PackBlob`, `BlobHandle`, `BlobType`, and `BlobHandles`. `PackBlob` intentionally exposes pack ID, handle, lengths, and compression status but not offset, keeping pack layout internal. `BlobHandle` pairs an `ID` with `BlobType`. `BlobType` enumerates invalid/data/tree blobs, provides strings, metadata classification, and JSON marshal/unmarshal. `BlobHandles` implements sorting by ID bytes then type and a string representation.

State is pure value data, serialized in indexes and JSON where blob types appear. Integration points are almost every repository layer: pack entries embed handles, indexes return `PackBlob`, prune operates on handles, and JSON tests enforce stable type names. Risks include adding blob types without updating JSON/string logic, treating tree blobs as metadata for backend/cache handling, and offset hiding requiring internal code to use `pack.Blob` when needed.
<!-- END_FILE_RESEARCH: sources/sync-backup/restic/internal/restic/blob.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/restic/internal/restic/blob_set.go -->
# sources/sync-backup/restic/internal/restic/blob_set.go

Purpose: implements `BlobSet`, a map-backed set of `BlobHandle` values.

Important APIs include `NewBlobSet`, `Has`, `Insert`, `Delete`, `Len`, `Equals`, `Merge`, `Intersect`, `Sub`, `List`, and `String`. `List` returns sorted blob handles. `String` renders a compact stable representation, truncating after ten entries with a count of remaining entries to keep logs/errors readable.

State is in-memory only but frequently represents used, keep, remove, duplicate, or missing blob sets. Integration points include prune planning, repack keep sets, repair tests, checker diagnostics, and user-facing errors about missing blobs. Risks include map iteration nondeterminism if not sorted before display, large set logging, and set mutation while shared across goroutines; concurrent users add explicit locking elsewhere. `blob_set_test.go` verifies empty, single, and truncated string formats.
<!-- END_FILE_RESEARCH: sources/sync-backup/restic/internal/restic/blob_set.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/restic/internal/restic/blob_set_test.go -->
# sources/sync-backup/restic/internal/restic/blob_set_test.go

Purpose: tests `BlobSet.String`.

The test starts with an empty set, asserts `"{}"`, inserts a known tree blob and checks the compact `<tree/idprefix>` format, then inserts 100 random data blobs and validates the string with a regexp that expects ten rendered handles and a `(90 more)` suffix.

State is only an in-memory set. Integration value is in diagnostics: prune and checker errors may print blob sets, so stable compact formatting matters for user-facing messages and tests. Risks covered include verbose output for large sets, missing type labels, and unstable ID prefix formatting.
<!-- END_FILE_RESEARCH: sources/sync-backup/restic/internal/restic/blob_set_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/restic/internal/restic/blob_test.go -->
# sources/sync-backup/restic/internal/restic/blob_test.go

Purpose: tests JSON encoding and decoding of `BlobType`.

`TestBlobTypeJSON` iterates `DataBlob` and `TreeBlob`, marshals each to the expected string (`"data"` or `"tree"`), unmarshals back, and asserts equality. It does not cover invalid blob types, which return errors in production code.

State is simple JSON serialization data. Integration points include pack/index JSON representations and any persisted metadata containing blob types. Risks covered include accidental change of persisted blob type names and unmarshal drift. Missing test coverage: invalid JSON/type values and `InvalidBlob` marshal behavior.
<!-- END_FILE_RESEARCH: sources/sync-backup/restic/internal/restic/blob_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/restic/internal/restic/config.go -->
# sources/sync-backup/restic/internal/restic/config.go

Purpose: defines repository configuration and helpers to create, load, validate, and save it.

`Config` stores repository format version, repository ID, and chunker polynomial. Constants define min, max, and stable repo versions. `CreateConfig` generates a random chunker polynomial and repository ID. `LoadConfig` loads JSON through encrypted unpacked storage, validates version range, and optionally checks polynomial irreducibility. `SaveConfig` writes config JSON as a `ConfigFile` through `SaveJSONUnpacked`. `TestDisableCheckPolynomial` is a test hook guarded by `sync.Once`.

State is persisted as the repository config file; unlike other unpacked files it has the null ID and is bootstrapped during repository open. Integration points include repository initialization, key search, upgrade, chunking, and tests. Risks include invalid polynomial checks, version compatibility, global test hook leakage, and config load failure after key decryption. Tests check save/load round-trip and helper behavior.
<!-- END_FILE_RESEARCH: sources/sync-backup/restic/internal/restic/config.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/restic/internal/restic/config_test.go -->
# sources/sync-backup/restic/internal/restic/config_test.go

Purpose: tests config save/load round-trip through the generic unpacked repository interfaces.

It defines minimal `saver` and `loader` test doubles implementing `SaveUnpacked`, `LoadUnpacked`, and `Connections`. `TestConfig` creates a max-version config, saves it while asserting file type is `ConfigFile`, captures the serialized bytes, then loads from those bytes and asserts the original and loaded configs are equal.

State is captured in a local byte slice, not a backend. Integration points are `CreateConfig`, `SaveConfig`, `LoadConfig`, JSON helpers, and file-type routing. Risks covered include wrong file type use and serialization drift. It does not test invalid versions or polynomial validation failures.
<!-- END_FILE_RESEARCH: sources/sync-backup/restic/internal/restic/config_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/restic/internal/restic/doc.go -->
# sources/sync-backup/restic/internal/restic/doc.go

Purpose: package documentation for the central `internal/restic` package.

The comment describes this package as containing repository types and functions. There are no APIs or state in this file itself. Its value is organizational: source files in this package define IDs, file/blob types, config, JSON helpers, sets, repository interfaces, and backend listing helpers used by many internal packages.

Risks are documentation drift only. Behavioral test signals live in the sibling files such as ID tests, blob tests, config tests, and backend-find tests.
<!-- END_FILE_RESEARCH: sources/sync-backup/restic/internal/restic/doc.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/restic/internal/restic/id.go -->
# sources/sync-backup/restic/internal/restic/id.go

Purpose: defines restic content IDs as SHA-256 hashes and provides parsing, formatting, equality, JSON, and conversion helpers.

Important APIs include `Hash`, `ParseID`, `ID.String`, `(*ID).Str`, `ID.IsNull`, `ID.Equal`, `ID.MarshalJSON`, `(*ID).UnmarshalJSON`, and `IDFromHash`. IDs are fixed 32-byte arrays. `String` always emits full lowercase hex; `Str` emits an 8-character prefix and handles nil/null specially. JSON encoding uses full hex strings; unmarshal requires quotes and exact encoded length.

State is value-only but IDs are the naming and integrity backbone for packs, indexes, keys, snapshots, and blobs. Integration points include backend handles, hash verification, set/map keys, prefix lookup, and tests. Risks include accepting malformed or truncated IDs, accidentally using prefix strings as canonical names, and hash mismatch handling. Tests cover known hashes, equality, JSON round-trip, malformed JSON, null/nil `Str`, and `IDFromHash` expectations elsewhere.
<!-- END_FILE_RESEARCH: sources/sync-backup/restic/internal/restic/id.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/restic/internal/restic/id_int_test.go -->
# sources/sync-backup/restic/internal/restic/id_int_test.go

Purpose: tests special string formatting for null and nil IDs.

`TestIDMethods` checks that a zero-value `ID` renders as `"[null]"` through pointer-aware `Str`, and that a nil `*ID` renders as `"[nil]"`. These are diagnostic strings, not canonical backend names.

State is local value data. Integration points are logging, error messages, and lock string formatting where IDs may be absent. Risks covered include panics on nil receiver and ambiguous display of null IDs.
<!-- END_FILE_RESEARCH: sources/sync-backup/restic/internal/restic/id_int_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/restic/internal/restic/id_test.go -->
# sources/sync-backup/restic/internal/restic/id_test.go

Purpose: tests ID parsing, equality, and JSON encoding/decoding.

`TestStrings` contains known SHA-256 outputs for sample strings. `TestID` parses IDs, checks equality, marshals to quoted full hex, unmarshals back, and compares values. `TestIDUnmarshal` exercises invalid quote/length cases and one valid full-length ID.

State is pure value data. Integration points are backend file naming, config/key/index JSON, and integrity verification. Risks covered include malformed ID acceptance, JSON length drift, and equality implementation regressions. The tests do not cover case normalization explicitly, but `hex.Decode` behavior is inherited by `ParseID`.
<!-- END_FILE_RESEARCH: sources/sync-backup/restic/internal/restic/id_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/restic/internal/restic/ids.go -->
# sources/sync-backup/restic/internal/restic/ids.go

Purpose: defines `IDs`, a sortable slice of `ID` values with compact string formatting.

It implements `Len`, `Less`, `Swap`, and `String`. Sorting compares raw ID bytes via string conversion. `String` preallocates a builder and renders each ID as its 8-character hex prefix inside brackets, separated by spaces.

State is in-memory value lists, commonly used for index IDs, obsolete files, or diagnostics. Integration points include repair index obsolete lists, backend listing results, and user/log output. Risks include compact strings not being canonical IDs and raw-byte ordering differing only by ID bytes, which is intended. `ids_test.go` checks formatting and duplicate preservation.
<!-- END_FILE_RESEARCH: sources/sync-backup/restic/internal/restic/ids.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/restic/internal/restic/ids_test.go -->
# sources/sync-backup/restic/internal/restic/ids_test.go

Purpose: tests compact `IDs.String` formatting.

`TestIDsString` constructs three IDs, including a duplicate, and asserts the output contains 8-character prefixes in slice order inside brackets. The duplicate remaining duplicated is intentional because `IDs` is a list, not a set.

State is local ID values. Integration points are diagnostic output in repair and repository code. Risks covered include formatting drift and accidental deduplication in list rendering.
<!-- END_FILE_RESEARCH: sources/sync-backup/restic/internal/restic/ids_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/restic/internal/restic/idset.go -->
# sources/sync-backup/restic/internal/restic/idset.go

Purpose: implements `IDSet`, a map-backed set for repository object IDs.

Important APIs include `NewIDSet`, `Has`, `Insert`, `Delete`, `Len`, `List`, `String`, `Merge`, `Equals`, `Clone`, `Sub`, `Intersect`, and `HasSubset`. `List` returns sorted IDs to make output deterministic. `Clone` uses `maps.Clone` for safe snapshots.

State is in-memory but represents persistent repository objects such as packs, indexes, locks, and files selected for removal or repack. Integration points include prune plans, repair index, lock exclusion sets, pack listing, and parallel removal. Risks include mutating shared sets across goroutines, relying on map iteration order without `List`, and confusing set operations with list order. Tests cover core set operations, list/string behavior, subset/intersection/subtraction, and equality.
<!-- END_FILE_RESEARCH: sources/sync-backup/restic/internal/restic/idset.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/restic/internal/restic/idset_test.go -->
# sources/sync-backup/restic/internal/restic/idset_test.go

Purpose: tests map-backed ID set behavior.

The tests create known IDs, insert and delete entries, verify `Has`, `Len`, and `Equals`, inspect sorted `List` and compact `String` output, and exercise set algebra such as `Merge`, `Sub`, `Intersect`, and subset checks. They also confirm empty and nil-ish behavior remains stable.

State is local ID sets. Integration points are prune/repair/lock workflows that rely on precise set membership. Risks covered include duplicate insertion changing length, delete behavior, unstable ordering after list conversion, and incorrect set algebra leading to wrong pack removal or retention decisions.
<!-- END_FILE_RESEARCH: sources/sync-backup/restic/internal/restic/idset_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/restic/internal/restic/json.go -->
# sources/sync-backup/restic/internal/restic/json.go

Purpose: provides generic helpers for loading and saving JSON-encoded unpacked repository files.

`LoadJSONUnpacked` loads bytes through a `LoaderUnpacked`, decodes JSON with `json.Unmarshal`, and wraps errors with file type and ID. `SaveJSONUnpacked` marshals an item with `json.Marshal` and saves it through `SaverUnpacked`, preserving the generic file-type parameter. Both functions are intentionally thin wrappers that centralize error context.

State and persistence are delegated to repository implementations: callers use these helpers for config, locks, and other unpacked JSON files. Integration points include `LoadConfig`, `SaveConfig`, lock creation/loading, and any future JSON metadata files. Risks include full-buffer JSON processing, loss of streaming behavior, and type mismatches only detected at runtime by JSON. Test coverage is indirect through config and lock tests.
<!-- END_FILE_RESEARCH: sources/sync-backup/restic/internal/restic/json.go -->
