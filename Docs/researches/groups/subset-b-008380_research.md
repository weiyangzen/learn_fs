# Research Group subset-b-008380

This grouped report covers Badger transaction/value-log utility code and FoundationDB build/binding-tester orchestration files. Each section is delimited for reconciliation into source-tree-aligned per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/badger/txn_test.go -->
# sources/storage-engines/badger/txn_test.go

## Purpose
This Go test file validates Badger transaction semantics: write/read visibility, asynchronous commit behavior, MVCC version reads, iterator ordering across versions and deletes, managed timestamp mode, architecture regressions, and conflict detection. It is a behavioral specification for `DB.NewTransaction`, `Update`, `View`, `Commit`, `CommitAt`, `CommitWith`, `Get`, `SetEntry`, `Delete`, and `Iterator`.

## Important APIs, Types, And Functions
Key tests include `TestTxnSimple`, `TestTxnReadAfterWrite`, `TestTxnCommitAsync`, `TestTxnVersions`, `TestTxnWriteSkew`, three iterator edge cases, two `AllVersions` deletion tests, `TestManagedDB`, `TestArmV7Issue311Fix`, and `TestConflict`. The file uses `runBadgerTest`, `getTestOptions`, `DefaultIteratorOptions`, `ErrConflict`, `ErrKeyNotFound`, `y.KeyWithTs`, and `z.Closer`.

## Control Flow
Most tests create a temporary DB, stage transactions, commit them, then open read transactions with explicit read timestamps or iterator options. The async commit test runs a continuous reader while many writers transfer balances and requires the invariant total to remain 4000. Iterator edge cases build small version histories and tombstones, then check forward/reverse seeks and rewinds. Managed mode creates transactions with explicit timestamps and verifies `CommitAt` rather than ordinary `Commit`.

## State And Persistence Behavior
The tests exercise MVCC state in the oracle read timestamp, pending write buffers inside active transactions, in-memory and disk-backed DB modes, and direct LSM insertion of tombstones for an all-versions regression. They do not create long-lived persisted fixtures except through the helper DB lifecycle, but they are sensitive to WAL/LSM visibility and commit ordering.

## Dependencies And Integration Points
The suite integrates transaction code with iterators, the oracle conflict checker, value copying, async commit callback paths, managed timestamp gates, and internal key timestamp encoding. It also validates InMemory mode for selected transaction paths.

## Risks And Edge Cases
Important risks covered are write skew, duplicate concurrent set-if-absent attempts, deleted versions being hidden or exposed under `AllVersions`, and iterator seek behavior when pending writes add/delete nearby keys. The tests intentionally panic on `CommitAt` in unmanaged mode. Remaining gaps include crash recovery for transactions and detailed callback ordering beyond success/failure.

## Test Signals
Failures indicate regressions in MVCC visibility, conflict ranges, iterator merge logic across pending writes and committed tables, async commit atomicity, managed transaction restrictions, or timestamped key ordering.
<!-- END_FILE_RESEARCH: sources/storage-engines/badger/txn_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/badger/util.go -->
# sources/storage-engines/badger/util.go

## Purpose
This file provides small Badger package utilities for validating LSM level invariants, reserving table file IDs, scanning existing table IDs from a directory, and seeding the package random generator.

## Important APIs, Types, And Functions
`(*levelsController).validate` iterates all `levelHandler`s and wraps validation errors. `(*levelHandler).validate` checks non-L0 tables are sorted and have valid internal key ranges using `y.CompareKeys`, `Smallest`, `Biggest`, and table IDs. `reserveFileID` atomically increments `nextFileID`. `getIDMap` reads a directory and parses table file names via `table.ParseFileID`.

## Control Flow
Validation skips level 0 because L0 may overlap. For higher levels it takes an `RLock`, walks adjacent table pairs, rejects inter-table overlap, and rejects a table whose smallest key sorts after its biggest key. `getIDMap` ignores subdirectories and non-table filenames.

## State And Persistence Behavior
The file reads filesystem directory entries but does not mutate persistent state. File ID reservation mutates the in-memory atomic `nextFileID` counter. Validation observes the current in-memory table list under a read lock.

## Dependencies And Integration Points
It integrates with the table package, LSM level controller/handler structures, Badger key ordering helpers, and logging/error wrapping in `y`. The debug-print helpers are commented out and not active.

## Risks And Edge Cases
Validation depends on all table keys carrying timestamp suffixes acceptable to `y.CompareKeys`. `getIDMap` calls `y.Check`, so directory read errors terminate the process rather than returning an error. Random seeding in `init` introduces package-global nondeterminism for tests that use `math/rand`.

## Test Signals
There is no direct test in this file. Regressions surface through compaction, opening existing tables, or explicit LSM validation callers.
<!-- END_FILE_RESEARCH: sources/storage-engines/badger/util.go -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/badger/value.go -->
# sources/storage-engines/badger/value.go

## Purpose
This file implements Badger's value-log core: entry encoding/decoding safety, append/rotation of `.vlog` files, reading by value pointer, value-log garbage collection and rewrite, discard-stat updates, iterator-safe deletion, and dynamic value-threshold tracking.

## Important APIs, Types, And Functions
Important constants are value metadata bits (`bitDelete`, `bitValuePointer`, `bitTxn`, `bitFinTxn`) and `vlogHeaderSize`. `safeRead.Entry` decodes a header, decrypts key/value bytes when enabled, and validates CRC. `valueLog` owns `filesMap`, `maxFid`, `writableLogOffset`, `garbageCh`, and `discardStats`. Main methods include `init`, `open`, `Close`, `createVlogFile`, `write`, `Read`, `readValueBytes`, `rewrite`, `pickLog`, `runGC`, `updateDiscardStats`, and `validateWrites`. `request` and `requests` carry batched write entries and value pointers with ref-counted lifecycle. `vlogThreshold` tracks histogram-based dynamic threshold updates.

## Control Flow
Open populates existing `.vlog` files, opens them read/write or read-only, deletes empty non-latest logs, scans/truncates the latest log to the last valid offset, then creates a fresh writable log. Writes validate total request sizes against the 32-bit pointer offset limit, append large values directly into the mmap-backed current log, strip transaction marker bits from value-log copies, update metrics and threshold histograms, and rotate logs when size or entry count limits are crossed. Reads lock the target log file, read the byte range, optionally verify checksum, decrypt, decode the header, and return the value slice plus an unlock callback.

## State And Persistence Behavior
Persistent state is the `.vlog` file set under `ValueDir`, discard stats, mmap file sizes, and value pointers stored in LSM entries. `SyncWrites` causes append syncs; otherwise `sync` explicitly syncs the latest log when needed. GC rewrite scans an old log, skips deleted/expired/stale entries, re-inserts still-current values via `batchSet`, and deletes or defers deletion of the old file depending on active iterator count. `dropAll` deletes value logs and creates a new first log outside InMemory mode.

## Dependencies And Integration Points
This code depends on `logFile`, `Entry`, `valuePointer`, DB LSM `get`/`batchSet`, discard stats, Badger options, OpenTelemetry spans, `y` metrics/checksum utilities, and Ristretto `z.Closer`/histogram support. Encryption hooks route through `logFile.encryptionEnabled` and `decryptKV`.

## Risks And Edge Cases
Critical risks are partial/corrupt entry truncation, checksum mismatch handling, pointer offset overflow, log rotation races, deleting logs still needed by iterators, stale LSM versions after GC, and read-only opening when replay/truncation is required. `vlogThreshold.update` sends to a buffered channel and can block if the listener stalls. `safeRead.Entry` allocates a combined buffer and overwrites entry key/value slices with decoded data.

## Test Signals
`value_test.go` and benchmarks cover append/read round trips, checksum and partial-WAL recovery, GC rewrite correctness, iterator survival during GC, persisted discard stats, transaction-bit stripping, write validation overflow, and first-vlog ID expectations.
<!-- END_FILE_RESEARCH: sources/storage-engines/badger/value.go -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/badger/value_gc_rewrite_bench_test.go -->
# sources/storage-engines/badger/value_gc_rewrite_bench_test.go

## Purpose
This benchmark measures value-log GC rewrite performance when early log files contain many expired entries followed by live entries. It targets the cost of `valueLog.rewrite` on an expired-heavy candidate file.

## Important APIs, Types, And Functions
Constants define expired/live key counts, value size, value-log file size, threshold, and expiry. `benchmarkValueGCRewriteOptions` tunes Badger for stable rewrite benchmarking and disables compaction/metrics noise. `benchmarkWriteEntries` writes entries in transactions and handles `ErrTxnTooBig` by committing and continuing. `benchmarkPrepareRewriteFixture` builds a reusable fixture DB. `copyDir` clones the fixture for each iteration. `BenchmarkValueGCRewriteExpiredOnlyFile` performs the timed rewrite.

## Control Flow
The benchmark builds one fixture outside the timed loop, then for each `b.N` iteration copies it to a fresh run directory, opens DB, selects the first sorted vlog fid, times `db.vlog.rewrite(lf)`, closes DB, and removes the run directory.

## State And Persistence Behavior
It creates real Badger directories and value logs. The per-iteration copy preserves identical persisted state, making rewrite timing independent of fixture construction. The measured rewrite may rewrite live entries and delete the old vlog in the copied run.

## Dependencies And Integration Points
It integrates with Badger option setup, transaction write paths, value-log file selection under `filesLock`, and filesystem copy/removal. It intentionally avoids metrics to reduce benchmark overhead.

## Risks And Edge Cases
`copyDir` rejects non-regular files, so symlinks or special files in fixtures would fail. The benchmark assumes at least two vlog files and direct access to internal `vlog.filesMap`. Results include DB open/close and directory copy outside timing but may still be affected by filesystem cache.

## Test Signals
The primary signal is allocation and time cost of `rewrite` when expired entries should be skipped cheaply. It complements `TestValueGCRewriteSkipsLSMGetOnlyForExpiredEntriesInMixedVlogFile`.
<!-- END_FILE_RESEARCH: sources/storage-engines/badger/value_gc_rewrite_bench_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/badger/value_test.go -->
# sources/storage-engines/badger/value_test.go

## Purpose
This large test file specifies Badger value-log behavior: basic writes/reads, GC rewrite correctness, managed-mode GC, discard stats persistence, checksum/truncation recovery, memtable corruption recovery, dynamic threshold behavior, value-log metadata bits, overflow validation, and first-file numbering.

## Important APIs, Types, And Functions
Core tests include `TestValueBasic`, `TestValueGCManaged`, `TestValueGC` through `TestValueGC4`, `TestPersistLFDiscardStats`, `TestValueChecksums`, `TestPartialAppendToWAL`, `TestReadOnlyOpenWithPartialAppendToWAL`, `TestPenultimateMemCorruption`, `TestValueGCRewriteSkipsLSMGetOnlyForExpiredEntriesInMixedVlogFile`, `TestBug578`, `TestValueLogTruncate`, `TestSafeEntry`, `TestValueEntryChecksum`, `TestValidateWrite`, `TestValueLogMeta`, and `TestFirstVlogFile`. Helpers include `createMemFile`, `checkKeys`, and `testHelper`.

## Control Flow
The tests create temporary DBs with small value-log/table thresholds, write large values to force vlog pointers, delete or overwrite subsets, invoke `vlog.rewrite` or `RunValueLogGC`, close/reopen, and verify reads. Recovery tests construct or corrupt `.mem` files to simulate partial appends and checksum failures. The mixed expired/live rewrite test clears expvar metrics and asserts only non-expired entries trigger LSM gets.

## State And Persistence Behavior
Persistent state includes value logs, memtable WAL files, SSTs, discard-stat logs, and DB reopen behavior. Several tests deliberately avoid clean close or release locks to simulate crashes. `TestPersistLFDiscardStats` captures discard stats on close and compares them after reopen. `TestValueLogMeta` verifies transaction bits are stripped from vlog records while LSM entries retain the transaction bit.

## Dependencies And Integration Points
The file exercises transaction write/delete APIs, internal `valueLog` and `logFile` methods, memtable WAL paths, expvar metrics, compaction/flattening, checksum verification, and iterator APIs. It uses `humanize`, `reflect`, and Badger test helpers.

## Risks And Edge Cases
Covered risks include stale versions after GC (#578), iterators reading through GC, partially written or corrupted WAL entries, read-only open when truncation would be required, value-pointer offset overflow, and corrupt value bytes. Some tests are skipped or contain TODOs around broken checksum error propagation and difficult value-log trigger reproduction.

## Test Signals
Failures reveal regressions in value-log append/read encoding, GC liveness decisions, crash recovery truncation, discard-stat durability, metrics behavior during rewrite, transaction metadata handling, and file ID initialization.
<!-- END_FILE_RESEARCH: sources/storage-engines/badger/value_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/badger/watermark_edge_test.go -->
# sources/storage-engines/badger/watermark_edge_test.go

## Purpose
This regression test stresses Badger transaction watermarks and conflict detection under many concurrent overlapping transactions. It expects each worker to observe a conflict in a constructed interleaving.

## Important APIs, Types, And Functions
`TestWaterMarkEdgeCase` launches 1000 goroutines through `runBadgerTest`. `doWork` creates two random keys, opens two writable transactions, interleaves reads/writes, commits `tx2`, then tries to commit `tx1`. Helper functions generate random key suffixes, wrap `Txn.Get`, wrap `Txn.Set`, and add crypto-random millisecond delays.

## Control Flow
Each goroutine reads key state through both transactions, writes `tx2` to two keys, commits it, then writes and rereads `tx1` on a key that was changed by `tx2`. The top-level test expects `doWork` to return an error wrapping `ErrConflict`; any success or different error is fatal.

## State And Persistence Behavior
The test mutates real DB state but uses randomly generated keys per worker, so conflicts are local to each pair of transactions. It exercises oracle/watermark state for read timestamps and conflict windows rather than long-lived persisted files.

## Dependencies And Integration Points
It integrates transaction read sets, write sets, commit conflict checks, and Badger's watermark/oracle internals indirectly. Crypto randomness and timed delays increase scheduling diversity.

## Risks And Edge Cases
Because delays are random, the test is partly timing-sensitive, though the operation order is deterministic inside each goroutine. It panics from helpers on unexpected non-`ErrKeyNotFound` or set failures.

## Test Signals
The signal is strict: all 1000 workers must report conflicts. A success indicates a lost conflict edge or watermark/oracle ordering regression.
<!-- END_FILE_RESEARCH: sources/storage-engines/badger/watermark_edge_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/badger/y/bloom.go -->
# sources/storage-engines/badger/y/bloom.go

## Purpose
This utility implements Badger's LevelDB-style Bloom filter encoding and hash function for table block membership checks.

## Important APIs, Types, And Functions
`type Filter []byte` exposes `MayContainKey` and `MayContain`. `NewFilter` builds an encoded filter from precomputed key hashes. `BloomBitsPerKey` estimates bit count from entry count and false-positive rate. `appendFilter` writes filter bits and a trailing probe-count byte. `extend` grows byte buffers. `Hash` is a Murmur-like 32-bit hash.

## Control Flow
Filter creation clamps bits per key, derives probe count `k`, enforces a minimum 64-bit filter, appends zeroed storage, and for each hash sets `k` bit positions by adding a rotated delta. Lookup reverses this logic and returns false when any required bit is absent; unknown future short-filter encodings with `k > 30` are treated as matches.

## State And Persistence Behavior
Filters are immutable encoded byte slices usually stored in table metadata/blocks. The last byte stores the number of probes; preceding bytes store bitset data. No external state is mutated except the provided buffer during append.

## Dependencies And Integration Points
The implementation mirrors LevelDB-Go behavior and is consumed by Badger table lookup code. It depends only on `math`.

## Risks And Edge Cases
Empty or one-byte filters never match. Small key sets get a minimum filter size to avoid high false-positive rates. `BloomBitsPerKey` divides by `numEntries`, so callers must avoid zero entries. Treating unknown encodings as match preserves forward compatibility but can increase false positives.

## Test Signals
`bloom_test.go` verifies bit layouts against C++ LevelDB fixtures, expected hash values, containment for inserted keys, and false-positive rates across filter sizes.
<!-- END_FILE_RESEARCH: sources/storage-engines/badger/y/bloom.go -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/badger/y/bloom_test.go -->
# sources/storage-engines/badger/y/bloom_test.go

## Purpose
This test file validates Bloom filter bit layout, containment behavior, false-positive rate, and hash compatibility with the LevelDB C++ implementation.

## Important APIs, Types, And Functions
`Filter.String` renders filter bytes as bit characters for fixture comparison. `TestSmallBloomFilter` checks two inserted words against an exact bit string. `TestBloomFilter` builds filters from 1 through 10000 keys and checks size and false positives. `TestHash` checks known hash outputs.

## Control Flow
The main false-positive test increases lengths nonlinearly, hashes little-endian integer keys, builds a filter at 10 bits/key, verifies all inserted keys match, then probes 10000 absent keys. It tracks mediocre versus good filters and fails if too many exceed the tighter false-positive threshold.

## State And Persistence Behavior
The tests are pure in-memory. Their fixtures act as compatibility signals for persisted table filter encodings.

## Dependencies And Integration Points
They directly exercise `Hash`, `NewFilter`, and `MayContainKey`, and indirectly protect table block behavior that depends on these filters.

## Risks And Edge Cases
Map iteration order in `TestSmallBloomFilter` does not affect assertions. The false-positive test is deterministic for generated keys but statistical by threshold. It does not exercise `BloomBitsPerKey`.

## Test Signals
Failures indicate incompatible Bloom encoding, hash drift, excessive filter size, missed positives, or false-positive regression.
<!-- END_FILE_RESEARCH: sources/storage-engines/badger/y/bloom_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/badger/y/checksum.go -->
# sources/storage-engines/badger/y/checksum.go

## Purpose
This file centralizes checksum calculation and verification for Badger protobuf checksum metadata.

## Important APIs, Types, And Functions
`ErrChecksumMismatch` is the public sentinel. `CalculateChecksum` supports `pb.Checksum_CRC32C` using the shared Castagnoli table and `pb.Checksum_XXHash64` using `cespare/xxhash/v2`. `VerifyChecksum` recalculates and compares the checksum, wrapping mismatch details with `Wrapf`.

## Control Flow
Checksum calculation switches on the protobuf algorithm enum and panics for unsupported algorithms. Verification delegates to calculation, compares `actual` and `expected.Sum`, and returns nil only on exact match.

## State And Persistence Behavior
The code is stateless. It validates persisted checksum fields attached to table/log metadata elsewhere.

## Dependencies And Integration Points
It depends on Badger's `pb.Checksum` enum and `CastagnoliCrcTable` from `y.go`. It is intended for table/value-log code that stores checksums in protobuf messages.

## Risks And Edge Cases
Unsupported algorithms panic rather than returning an error, so callers must validate enums before use. `VerifyChecksum` assumes `expected` is non-nil.

## Test Signals
`checksum_test.go` verifies both algorithms, success and mismatch paths, empty CRC32C input, and unsupported algorithm panic behavior.
<!-- END_FILE_RESEARCH: sources/storage-engines/badger/y/checksum.go -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/badger/y/checksum_test.go -->
# sources/storage-engines/badger/y/checksum_test.go

## Purpose
This test file validates the checksum helper contract for CRC32C and XXHash64.

## Important APIs, Types, And Functions
Tests cover `CalculateChecksum` for CRC32C and XXHash64, `VerifyChecksum` success and mismatch, and panic behavior for an unsupported `pb.Checksum_Algorithm`.

## Control Flow
Each test constructs byte slices and expected sums using the same underlying libraries, calls Badger helpers, and checks equality or error text. The unsupported algorithm test uses `defer`/`recover`.

## State And Persistence Behavior
The tests are pure in-memory but protect checksum values stored in persistent Badger metadata.

## Dependencies And Integration Points
They import `hash/crc32`, `xxhash`, `pb`, and `testify/require`.

## Risks And Edge Cases
The tests do not check nil checksum pointers or wrapped error identity with `errors.Is`; they only check message content for mismatch.

## Test Signals
Failures indicate checksum implementation drift or changed error/panic behavior.
<!-- END_FILE_RESEARCH: sources/storage-engines/badger/y/checksum_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/badger/y/encrypt.go -->
# sources/storage-engines/badger/y/encrypt.go

## Purpose
This file provides AES-CTR XOR helpers used for Badger encryption and decryption, plus random IV generation.

## Important APIs, Types, And Functions
`XORBlock` encrypts/decrypts from `src` into caller-provided `dst`. `XORBlockAllocate` allocates a destination and returns it. `XORBlockStream` writes transformed bytes to an `io.Writer` through `cipher.StreamWriter`. `GenerateIV` returns a random AES-block-sized IV.

## Control Flow
Each XOR helper creates an AES cipher from `key`, wraps it in CTR mode with `iv`, and applies `XORKeyStream` or `io.Copy`. Because CTR is symmetric, the same function decrypts when called with the same key and IV.

## State And Persistence Behavior
The code does not persist state directly. Correct key/IV pairing is essential for decrypting persisted Badger log/table bytes.

## Dependencies And Integration Points
It uses Go `crypto/aes`, `crypto/cipher`, `crypto/rand`, and `io`. Value-log code calls decryption through `logFile` helpers that ultimately rely on these primitives.

## Risks And Edge Cases
AES key and IV sizes are validated by the standard library. Reusing IVs with the same key would be cryptographically unsafe; this file only supplies primitives and does not enforce lifecycle policy. `XORBlockStream` wraps `io.Copy` errors with Badger's `Wrapf`.

## Test Signals
`encrypt_test.go` verifies round-trip encryption/decryption and same-slice in-place operation.
<!-- END_FILE_RESEARCH: sources/storage-engines/badger/y/encrypt.go -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/badger/y/encrypt_test.go -->
# sources/storage-engines/badger/y/encrypt_test.go

## Purpose
This test validates AES-CTR XOR helper symmetry and in-place behavior.

## Important APIs, Types, And Functions
`TestXORBlock` generates a 32-byte key, AES-block IV, random 1 KiB plaintext, and exercises `XORBlock`.

## Control Flow
The test encrypts `src` into `dst`, decrypts `dst` into `act`, and compares `act` to `src`. It then copies `src` into `cp`, encrypts in place, compares to `dst`, decrypts in place, and compares to the original source.

## State And Persistence Behavior
The test is in-memory only. It protects assumptions used when encrypting persisted log/table byte ranges.

## Dependencies And Integration Points
It uses Go crypto randomness, AES block sizing, and `testify/require`.

## Risks And Edge Cases
The test ignores random read errors for key, IV, and source generation. It does not exercise invalid key/IV sizes, stream writer encryption, IV generation, or cross-file integration.

## Test Signals
Failures indicate broken CTR setup, destination handling, or in-place XOR assumptions.
<!-- END_FILE_RESEARCH: sources/storage-engines/badger/y/encrypt_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/badger/y/error.go -->
# sources/storage-engines/badger/y/error.go

## Purpose
This file defines lightweight error and assertion helpers used across Badger's internal `y` package.

## Important APIs, Types, And Functions
`Check` fatals on non-nil errors. `Check2` adapts two-return call sites. `AssertTrue` and `AssertTruef` fatal on failed invariants. `Wrap` and `Wrapf` add context, using simple formatting unless `debugMode` is enabled. `CombineErrors` formats one or two errors into a single error.

## Control Flow
Fatal helpers terminate the process via `log.Fatalf`. `Wrap` returns nil for nil input in non-debug mode, but in debug mode it always formats with `%w`; callers rely on `debugMode` remaining false by default. `CombineErrors` avoids nil output only when both inputs are nil.

## State And Persistence Behavior
No persistence. The package-global `debugMode` changes wrapping semantics if toggled.

## Dependencies And Integration Points
These helpers are used throughout Badger for invariant checks, startup failure handling, and context-wrapped errors.

## Risks And Edge Cases
Fatal assertions are unsuitable for recoverable library errors. `Wrap` in non-debug mode does not use Go error wrapping, limiting `errors.Is` on wrapped sentinels. `CombineErrors` loses original error identity by formatting.

## Test Signals
`error_test.go` covers `CombineErrors` output for all nil/non-nil combinations; fatal and wrapping helpers are not directly tested here.
<!-- END_FILE_RESEARCH: sources/storage-engines/badger/y/error.go -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/badger/y/error_test.go -->
# sources/storage-engines/badger/y/error_test.go

## Purpose
This test file verifies `CombineErrors` formatting behavior.

## Important APIs, Types, And Functions
The four tests cover both errors present, only first present, only second present, and both nil.

## Control Flow
Each test constructs standard `errors.New` values, calls `CombineErrors`, and compares the resulting error string or nil result with `testify/require`.

## State And Persistence Behavior
The tests have no state or persistence effects.

## Dependencies And Integration Points
They protect callers that display combined close/sync errors but do not cover error identity.

## Risks And Edge Cases
The tests assert exact string formatting and therefore constrain presentation. They do not verify `errors.Is` behavior because `CombineErrors` does not preserve wrapped identity.

## Test Signals
Failures indicate changed combined-error formatting or nil handling.
<!-- END_FILE_RESEARCH: sources/storage-engines/badger/y/error_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/badger/y/file_dsync.go -->
# sources/storage-engines/badger/y/file_dsync.go

## Purpose
This platform-specific file sets the datasync open flag for platforms that support `O_DSYNC`.

## Important APIs, Types, And Functions
The `init` function assigns `datasyncFileFlag = unix.O_DSYNC`. Build tags exclude DragonFly, FreeBSD, Windows, Plan 9, JS, and WASI.

## Control Flow
At package initialization, the platform constant is copied into the shared variable used by file-opening helpers in `y.go`.

## State And Persistence Behavior
This affects persistence semantics of files opened with the `Sync` flag or `sync=true`, causing writes to wait for data sync on supported Unix-like systems.

## Dependencies And Integration Points
It depends on `golang.org/x/sys/unix` and integrates with `OpenExistingFile`, `CreateSyncedFile`, `OpenSyncedFile`, and `OpenTruncFile`.

## Risks And Edge Cases
Build tag coverage controls which synchronization semantics are used. Incorrect tags would silently choose the wrong flag file.

## Test Signals
There is no direct test. Persistence behavior is indirectly exercised by Badger write/recovery tests.
<!-- END_FILE_RESEARCH: sources/storage-engines/badger/y/file_dsync.go -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/badger/y/file_nodsync.go -->
# sources/storage-engines/badger/y/file_nodsync.go

## Purpose
This platform-specific file provides a fallback synchronization flag for platforms without `O_DSYNC`.

## Important APIs, Types, And Functions
The `init` function sets `datasyncFileFlag = syscall.O_SYNC` under build tags for DragonFly, FreeBSD, Windows, and Plan 9.

## Control Flow
The assignment happens at package initialization before file helper functions are used.

## State And Persistence Behavior
Files opened with sync semantics use full `O_SYNC` rather than datasync-only behavior on these platforms, potentially increasing durability cost.

## Dependencies And Integration Points
It depends on the standard `syscall` package and the shared helpers in `y.go`.

## Risks And Edge Cases
The build tags do not include JS/WASI, which are excluded from the dsync file but not included here; those platforms may be unsupported or handled elsewhere by build constraints.

## Test Signals
No direct test exists. Platform CI/build coverage is the main signal.
<!-- END_FILE_RESEARCH: sources/storage-engines/badger/y/file_nodsync.go -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/badger/y/iterator.go -->
# sources/storage-engines/badger/y/iterator.go

## Purpose
This file defines the serialized value payload stored with Badger keys and a minimal iterator interface shared by lower-level components.

## Important APIs, Types, And Functions
`ValueStruct` stores `Meta`, `UserMeta`, `ExpiresAt`, `Value`, and non-serialized `Version`. `EncodedSize`, `Decode`, `Encode`, and `EncodeTo` define the binary layout: meta byte, user meta byte, varint expiry, then raw value bytes. `Iterator` specifies `Next`, `Rewind`, `Seek`, `Key`, `Value`, `Valid`, and `Close`.

## Control Flow
Encoding writes fixed metadata bytes, varint expiry, and value data either into a caller-provided byte slice or a buffer. Decode reads in the same order and treats the remainder as the value. `sizeVarint` computes the size of a uvarint by shifting until zero.

## State And Persistence Behavior
The encoded `ValueStruct` format is persisted in Badger tables. `Version` is runtime-only and must be populated separately from timestamped keys.

## Dependencies And Integration Points
It depends on `bytes` and `encoding/binary`. Table builders and iterators use this layout, and tests in `y_test.go` verify size calculations.

## Risks And Edge Cases
`Decode` assumes a valid non-empty slice with enough bytes for metadata and varint. `Encode` assumes the destination length is at least `EncodedSize`. Layout changes would break existing SST compatibility.

## Test Signals
`TestSizeVarintForZero` and `TestEncodedSize` cover size math; broader table tests cover encode/decode integration.
<!-- END_FILE_RESEARCH: sources/storage-engines/badger/y/iterator.go -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/badger/y/metrics.go -->
# sources/storage-engines/badger/y/metrics.go

## Purpose
This file declares global expvar metrics and guarded helper functions for Badger read/write, LSM, value-log, compaction, and size counters.

## Important APIs, Types, And Functions
`BADGER_METRIC_PREFIX` is `badger_`. Global metrics include `lsmSize`, `vlogSize`, `pendingWrites`, VLOG read/write counts and bytes, LSM bytes and bloom/get maps, and user operation counters. Public helper functions add to counters or set/get map values only when an `enabled` flag is true. Internal helpers are `addInt`, `addToMap`, `storeToMap`, and `getFromMap`.

## Control Flow
Package `init` registers all metrics through `expvar.NewInt` or `expvar.NewMap`. Callers pass `Options.MetricsEnabled`; disabled calls return without touching global expvar state.

## State And Persistence Behavior
Metrics are process-global and cumulative across DB instances. They are not persisted, but tests can observe them through `expvar.Get`.

## Dependencies And Integration Points
Value-log writes/reads, DB get/put paths, compactions, and size reporters call these helpers. `value_test.go` uses `badger_get_num_user` to validate rewrite lookup avoidance.

## Risks And Edge Cases
Global expvar names can conflict if the package is initialized multiple times in unusual plugin/test environments. Metrics are shared across DBs, so tests must clear or isolate counters when asserting exact values.

## Test Signals
There is no dedicated metrics test here. Integration tests detect selected counter behavior.
<!-- END_FILE_RESEARCH: sources/storage-engines/badger/y/metrics.go -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/badger/y/watermark.go -->
# sources/storage-engines/badger/y/watermark.go

## Purpose
This file implements `WaterMark`, a concurrent tracker for the highest contiguous completed index. It is used by Badger/related systems to coordinate asynchronous work completion and waiters.

## Important APIs, Types, And Functions
`uint64Heap` is a min-heap of pending indices. `mark` represents begin/done events, batched indices, or waiters. `WaterMark` exposes `Init`, `Begin`, `BeginMany`, `Done`, `DoneMany`, `DoneUntil`, `SetDoneUntil`, `LastIndex`, and `WaitForMark`. The background `process` goroutine owns mutable maps.

## Control Flow
`Begin` and `Done` send events to `markCh`; processing increments or decrements a pending count per index, pushes first-seen indices onto the heap, and advances `doneUntil` while the minimum pending index has non-positive count. Waiters are closed when their requested index is already or newly covered.

## State And Persistence Behavior
State is in-memory: atomic `doneUntil`, atomic `lastIndex`, buffered channel, pending counts, heap, and waiter map. `SetDoneUntil` directly updates the atomic baseline and must not be intermingled incorrectly with begin/done events.

## Dependencies And Integration Points
It depends on `container/heap`, `context`, atomics, and `z.Closer`. Transaction/oracle code relies on watermark advancement for timestamp and conflict lifecycle.

## Risks And Edge Cases
The comments require each serial index to emit at least one begin watermark or waiters can block indefinitely. `processOne` fatals if an event arrives below `doneUntil`. Notification logic avoids huge loops when index arithmetic wraps or spans a very large range.

## Test Signals
`watermark_edge_test.go` indirectly stresses transaction watermark behavior. Direct unit tests are not in this subset.
<!-- END_FILE_RESEARCH: sources/storage-engines/badger/y/watermark.go -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/badger/y/y.go -->
# sources/storage-engines/badger/y/y.go

## Purpose
This utility file provides common Badger primitives: file open helpers with sync/read-only flags, timestamped key encoding and ordering, byte/slice conversion helpers, throttling, paged buffers/readers, allocator-backed protobuf allocation, human-readable byte formatting, and transfer-rate monitoring.

## Important APIs, Types, And Functions
Key APIs include `OpenExistingFile`, `CreateSyncedFile`, `OpenSyncedFile`, `OpenTruncFile`, `SafeCopy`, `Copy`, `KeyWithTs`, `ParseTs`, `CompareKeys`, `ParseKey`, `SameKey`, `Slice.Resize`, `FixedDuration`, `Throttle`, numeric byte conversion helpers, `PageBuffer`, `PageBufferReader`, `NewKV`, `IBytesToString`, and `RateMonitor`.

## Control Flow
File helpers compose OS flags from `Sync`/`ReadOnly` options and platform `datasyncFileFlag`. Timestamped keys append `math.MaxUint64 - ts` so newer versions sort first for the same user key. `Throttle` uses a buffered channel, wait group, and error channel to limit concurrent workers and propagate the first error. `PageBuffer` writes into exponentially growing pages and reads back through page-aware offsets.

## State And Persistence Behavior
File helpers affect on-disk open modes. Timestamped keys are the persisted key format in LSM tables. Unsafe slice conversions reinterpret numeric slices without copying, tying returned bytes to source memory. `PageBuffer` is in-memory and not thread-safe.

## Dependencies And Integration Points
This is a foundational package for table building, value-log CRCs, transaction key comparison, compaction throttling, protobuf serialization, and progress reporting. It depends on standard libraries plus Badger protobuf and Ristretto allocator.

## Risks And Edge Cases
`CompareKeys` assumes both keys have 8-byte timestamps. `SameKey` requires equal total lengths before comparing parsed keys. Unsafe slice conversions require correct alignment/lifetime and byte lengths divisible by element size. `PageBuffer.Truncate` asserts the offset is below current length, so truncating exactly to length or zero has constraints.

## Test Signals
`y_test.go` covers page-buffer writes/reads/truncation, varint sizing, encoded value sizing, allocator reuse, and `SafeCopy` nil-vs-empty behavior.
<!-- END_FILE_RESEARCH: sources/storage-engines/badger/y/y.go -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/badger/y/y_test.go -->
# sources/storage-engines/badger/y/y_test.go

## Purpose
This file tests and benchmarks core `y` utilities, especially `PageBuffer`, `ValueStruct` size math, allocator-backed protobuf allocation, and `SafeCopy` edge behavior.

## Important APIs, Types, And Functions
`BenchmarkBuffer` compares `bytes.Buffer` and `PageBuffer`. Page-buffer tests cover writes, truncation, readers from fixed/random offsets, chunked reads, oversized read buffers, and zero-length reads. `TestSizeVarintForZero`, `TestEncodedSize`, `TestAllocatorReuse`, and `TestSafeCopy_Issue2067` cover other helpers.

## Control Flow
Tests write random bytes into `PageBuffer`, mirror operations in `bytes.Buffer` or raw slices, and compare `Bytes`/reader output. Allocator reuse repeatedly resets a `z.Allocator`, builds many `pb.KV` entries, and marshals them.

## State And Persistence Behavior
All tests are in-memory. They protect structures used to buffer serialized data that can later be persisted.

## Dependencies And Integration Points
They depend on `bytes`, `binary`, `io`, protobuf marshal, Badger `pb`, Ristretto allocator, and `testify/require`.

## Risks And Edge Cases
Random test data changes per run but assertions are deterministic over mirrored data. Tests do not cover all unsafe byte conversion helpers or `Throttle`.

## Test Signals
Failures indicate broken paged buffer boundary handling, EOF behavior, varint encoded size calculation, allocator object layout, or `SafeCopy` compatibility with callers expecting non-nil empty slices.
<!-- END_FILE_RESEARCH: sources/storage-engines/badger/y/y_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/badger/y/zstd.go -->
# sources/storage-engines/badger/y/zstd.go

## Purpose
This file wraps `klauspost/compress/zstd` compression and decompression for Badger blocks and provides a compression-bound estimate.

## Important APIs, Types, And Functions
Global `decoder` and `encoder` are initialized lazily by `sync.Once`. `ZSTDDecompress` calls `DecodeAll`. `ZSTDCompress` maps an integer level to a zstd encoder level and calls `EncodeAll`. `ZSTDCompressBound` estimates the worst-case output size using a DataDog-derived formula.

## Control Flow
The first compress/decompress call initializes the shared codec and fatals via `Check` on construction error. Subsequent calls reuse the codec. Both APIs append into `dst[:0]`.

## State And Persistence Behavior
The code holds process-global encoder/decoder state. Compressed bytes may be persisted in Badger tables depending on compression options.

## Dependencies And Integration Points
It depends on `github.com/klauspost/compress/zstd` and Badger error helpers. Table/block compression code calls these wrappers.

## Risks And Edge Cases
The encoder is created only once, so later calls with different compression levels reuse the first level. Shared encoder/decoder concurrency safety depends on the library's `EncodeAll`/`DecodeAll` guarantees. Construction errors terminate the process.

## Test Signals
No direct tests in this subset. Compression integration tests elsewhere should catch round-trip or sizing regressions.
<!-- END_FILE_RESEARCH: sources/storage-engines/badger/y/zstd.go -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/.devcontainer/devcontainer.json -->
# sources/storage-engines/foundationdb/.devcontainer/devcontainer.json

## Purpose
This JSON file defines a VS Code/devcontainer environment for FoundationDB development.

## Important APIs, Types, And Functions
It selects image `docker.io/foundationdb/build:rockylinux9-latest`, enables `SYS_PTRACE`, privileged mode, unconfined seccomp, and a 60 GB storage requirement. It sets `CC=clang`, `CXX=clang++`, and `BOOST_ROOT=/opt/boost_1_78_0_clang`. VS Code extensions include clangd and CMake Tools, with CMake configured to export compile commands.

## Control Flow
There is no executable control flow. The devcontainer runtime reads the JSON and provisions the container.

## State And Persistence Behavior
The file influences container state and build environment but does not store application data.

## Dependencies And Integration Points
It integrates with VS Code Remote Containers, the FoundationDB build image, CMake, clang, and Boost.

## Risks And Edge Cases
Privileged mode and unconfined seccomp expand container permissions. The pinned Boost path must match the image. Storage below 60 GB may fail builds.

## Test Signals
Validation is by opening the devcontainer and configuring/building FoundationDB successfully.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/.devcontainer/devcontainer.json -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/.github/workflows/format.yml -->
# sources/storage-engines/foundationdb/.github/workflows/format.yml

## Purpose
This GitHub Actions workflow enforces C/C++ formatting on pull requests to `main` and `release-7.4`.

## Important APIs, Types, And Functions
The `clang-format` job runs on `ubuntu-24.04`, checks out the pull request head SHA, installs `clang-format-19`, formats all `.c`, `.cpp`, `.h`, and `.hpp` files while pruning `contrib`, then runs `git diff --exit-code`.

## Control Flow
On PR events, the job modifies files in place and fails if formatting produced any diff. It uses read-only content permissions.

## State And Persistence Behavior
The workflow mutates only the ephemeral Actions checkout. No repository state is committed by the job.

## Dependencies And Integration Points
It depends on `actions/checkout` pinned by SHA, Ubuntu apt, clang-format 19, and GitHub branch filters.

## Risks And Edge Cases
The `find` expression excludes all `contrib` paths and may miss generated or differently suffixed C++ files. Installing from apt makes the exact package availability tied to Ubuntu 24.04 repositories.

## Test Signals
Any formatting drift appears as a non-empty git diff and failed CI job.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/.github/workflows/format.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/.github/workflows/stale.yml -->
# sources/storage-engines/foundationdb/.github/workflows/stale.yml

## Purpose
This GitHub Actions workflow marks and closes stale pull requests.

## Important APIs, Types, And Functions
It runs `actions/stale` v10.2.0 pinned by SHA on a daily cron at 20:15 UTC. Permissions allow actions, issues, and pull-request writes. Configuration marks PRs stale after 150 inactive days, closes 14 days later, effectively disables issue staleness with 5475 days, processes 80 operations per run, and handles oldest items first.

## Control Flow
The scheduled job invokes the stale action with the configured message and thresholds.

## State And Persistence Behavior
It mutates GitHub PR labels/comments and may close PRs. It does not touch repository files.

## Dependencies And Integration Points
It integrates with GitHub Actions scheduling and the marketplace stale action.

## Risks And Edge Cases
Long-lived but intentionally open PRs can be closed if maintainers miss the label/comment window. Operation limits can delay processing large backlogs.

## Test Signals
Operational signals are action logs, applied stale labels, comments, and PR closures.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/.github/workflows/stale.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/.github/workflows/windows-boost-test.yml -->
# sources/storage-engines/foundationdb/.github/workflows/windows-boost-test.yml

## Purpose
This workflow verifies FoundationDB CMake configuration can find Boost in CONFIG mode on Windows.

## Important APIs, Types, And Functions
The `test-windows-boost` job runs on `windows-2025`, checks out code, installs Boost components and `lz4` through vcpkg, then configures a Release build with the vcpkg toolchain, Swift/C#/docs/tests disabled.

## Control Flow
It triggers on PRs to `main` and pushes to `main` or `boost-*`. The job installs dependencies, creates `build`, runs CMake configure, and prints a success message.

## State And Persistence Behavior
It mutates only the ephemeral Windows runner and vcpkg cache/install directories.

## Dependencies And Integration Points
It depends on GitHub hosted Windows, vcpkg, CMake, FoundationDB's Boost detection, and selected build options.

## Risks And Edge Cases
`actions/checkout@v4` is not SHA-pinned here unlike other workflows. The job configures but does not build targets despite the step name, so it mainly validates dependency discovery.

## Test Signals
Failure indicates Boost CONFIG/vcpkg integration or Windows CMake configuration regression.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/.github/workflows/windows-boost-test.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/.pre-commit-config.yaml -->
# sources/storage-engines/foundationdb/.pre-commit-config.yaml

## Purpose
This pre-commit configuration runs Python formatting and linting hooks.

## Important APIs, Types, And Functions
It configures `black` pinned to a frozen 22.8.0 commit and `flake8` pinned to a frozen 5.0.4 commit. Black excludes `contrib/Implib.so/implib-gen.py` and `documentation/sphinx/extensions/rubydomain.py`.

## Control Flow
When pre-commit runs, it installs the configured hook environments and applies black/flake8 to matching files.

## State And Persistence Behavior
Black may rewrite local working-tree files. Flake8 reports lint errors without persistence.

## Dependencies And Integration Points
It integrates with the pre-commit framework and Python code in the FoundationDB tree.

## Risks And Edge Cases
Pinned old tool versions may diverge from modern Python syntax expectations. The exclusion list is narrow and should be maintained if generated/third-party Python files change.

## Test Signals
Signals are local or CI pre-commit hook pass/fail results and black diffs.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/.pre-commit-config.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/CMakeLists.txt -->
# sources/storage-engines/foundationdb/CMakeLists.txt

## Purpose
This is the top-level FoundationDB CMake build definition. It configures project metadata, build type, compiler/tooling, versioning, components, dependencies, subdirectories, testing, packaging, and IDE compile-command generation.

## Important APIs, Types, And Functions
It requires CMake 3.24.2, defines project `foundationdb` version 8.0.0, blocks in-source builds, exposes options such as `OPEN_FOR_IDE`, `AUTO_DISCOVER_UNIT_TESTS`, `USE_SCCACHE`, `WITH_ACAC`, `WITH_CSHARP`, `NO_MULTIREGION_TEST`, and `NO_RESTART_TEST`, and includes modules like `ConfigureCompiler`, `FDBComponents`, `CompileActorCompiler`, `FlowCommands`, `CompileBoost`, `GetFmt`, and `GetMsgpack`.

## Control Flow
Configuration sets a default build type, resolves C#/.NET/Mono tooling, builds or skips actor/compiler-related tools, generates version and cluster files, enables CTest, sets sanitizer environment options, adds core subdirectories, conditionally adds bindings/docs/packaging, and prints selected components.

## State And Persistence Behavior
It writes generated files into the build tree (`version.txt`, `versions.target`, `fdb.cluster`) and may generate a source-tree `compile_commands.json` when requested. It configures packaging and install layout but does not run builds itself.

## Dependencies And Integration Points
This file is the integration hub for Flow, fdbrpc, fdbclient, fdbserver, bindings, tests, documentation, Boost, fmt, msgpack, CPack/MSI packaging, Swift, C#, Python, and platform-specific options.

## Risks And Edge Cases
In-source builds fatal. Release builds reject ACAC. Explicit C# tool enablement without a toolchain is fatal, while implicit enablement can skip coverage tooling. Cross-compiling disables selected subdirectories. The version variables must stay aligned with release branches.

## Test Signals
Signals include CMake configure success, component printout, generated files, CTest registration, and downstream platform workflows such as Windows Boost CONFIG testing.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/CMakeLists.txt -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/bindings/CMakeLists.txt -->
# sources/storage-engines/foundationdb/bindings/CMakeLists.txt

## Purpose
This CMake file coordinates optional language binding subdirectories and bindingtester packaging.

## Important APIs, Types, And Functions
It always adds `c`, conditionally adds `flow` when not `OPEN_FOR_IDE`, and gates `python`, `java`, `go`, `ruby`, and `swift` subdirectories on corresponding `WITH_*_BINDING` options. On non-Windows non-IDE builds it calls `package_bindingtester()` and `package_bindingtester2()`.

## Control Flow
CMake processes binding subdirectories in a fixed order. Swift binding inclusion also checks that `bindings/swift` exists before adding it.

## State And Persistence Behavior
The file configures build targets and packaging outputs; it does not directly write runtime data.

## Dependencies And Integration Points
It integrates top-level component options with language binding build systems and binding tester packaging functions defined elsewhere.

## Risks And Edge Cases
Flow and Go bindings are skipped for IDE-only configuration. Swift can be enabled but skipped if sources are absent, with only a status message. Bindingtester packaging is disabled on Windows.

## Test Signals
CMake configure/build target presence and packaged bindingtester artifacts are the main signals.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/bindings/CMakeLists.txt -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/bindings/__init__.py -->
# sources/storage-engines/foundationdb/bindings/__init__.py

## Purpose
This Python package initializer marks `bindings` as a package and carries FoundationDB license header text.

## Important APIs, Types, And Functions
It defines no runtime symbols, functions, classes, or imports.

## Control Flow
There is no executable control flow beyond module import producing an empty package namespace.

## State And Persistence Behavior
No state or persistence behavior.

## Dependencies And Integration Points
Its role is packaging/import structure for Python modules under `bindings`.

## Risks And Edge Cases
Because it is empty, consumers must import concrete subpackages directly. Any future package-level behavior would affect import side effects.

## Test Signals
Import success of `bindings` is the only direct signal.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/bindings/__init__.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/bindings/bindingtester/__init__.py -->
# sources/storage-engines/foundationdb/bindings/bindingtester/__init__.py

## Purpose
This module initializes the Python bindingtester package, selects the latest FoundationDB API version, configures logging, and defines the `Result` comparison model used by the binding tester.

## Important APIs, Types, And Functions
It prepends the in-tree Python binding path, imports `LATEST_API_VERSION`, sets `FDB_API_VERSION`, defines `LOGGING`, and defines class `Result`. `Result` unpacks keys relative to a subspace, compares tuple keys with type-sensitive equality and NaN handling, matches values, applies global error filters, exposes optional sequence numbers, and formats results.

## Control Flow
On import, it calls `fdb.api_version(FDB_API_VERSION)` and prepares logging configuration. `Result.matches` first requires key match, then accepts any equal value among candidate value tuples.

## State And Persistence Behavior
Module import mutates `sys.path` and FoundationDB binding API-version global state. `Result` objects are in-memory representations of persisted tester output key-values.

## Dependencies And Integration Points
It integrates with the in-tree Python binding, `bindingtester.util`, `bindingtester.tests.ResultSpecification`, and `bindingtester.py` result comparison.

## Risks And Edge Cases
`sys.path` manipulation can shadow installed packages. API version is bound at import time. Value matching allows any value overlap, which is deliberate for nondeterministic acceptable results but can hide multiplicity differences.

## Test Signals
Binding tester runs exercise `Result` alignment, comparison, and error-filter behavior.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/bindings/bindingtester/__init__.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/bindings/bindingtester/bindingtester.py -->
# sources/storage-engines/foundationdb/bindings/bindingtester/bindingtester.py

## Purpose
This executable Python driver generates FoundationDB binding tests, inserts instruction streams into a cluster, runs one or two language-specific testers, compares outputs, validates test-specific invariants, supports printing and bisection, and manages CLI options.

## Important APIs, Types, And Functions
`API_VERSIONS` lists supported API versions and is asserted to end at `FDB_API_VERSION`. `ResultSet` aligns and compares tester outputs. `choose_api_version` validates or randomly selects a compatible API version. `TestRunner` owns DB connection, tester selection, test generation, insertion, process execution, result collection, and validation. Top-level helpers are `bisect`, `parse_args`, `validate_args`, and `main`.

## Control Flow
`main` parses args, configures logging, sets a random seed and optional tracing, constructs `TestRunner`, then dispatches to bisect, print, insert-only, or run. `TestRunner.run_test` generates instructions, inserts them before each tester, calls `pre_run`, executes external tester commands with timeout, reads output subspaces, and compares results. `ResultSet.check_for_errors` walks ordered result lists, aligns by sequence number or minimum tuple key, filters permissible global errors, and counts mismatches.

## State And Persistence Behavior
The driver deletes all keys in the connected database before inserting each test instruction set. Testers write result key-values into output subspaces. The driver itself maintains in-memory selected API/tester/test options, random seeds, and subprocess state.

## Dependencies And Integration Points
It integrates with the FoundationDB Python binding, tuple/subspace APIs, bindingtester test classes, known tester registry, utility logging, and external tester binaries/scripts for Python, Ruby, Java, Go, Flow, and Swift.

## Risks And Edge Cases
`del self.db[:]` is destructive to the selected cluster and assumes a disposable binding-test database. Command splitting uses `test.cmd.split(" ")`, so quoted paths/arguments are fragile. Timeout kills only the direct process. Concurrent tests cannot be compared. Random API-version selection calls `random.random` multiple times, so branch probabilities are sequential rather than a single distribution.

## Test Signals
Exit codes distinguish tester execution failure, comparison/validation failure, and driver exceptions. Logs include seed, operation count, API version, tester commands, incorrect result blocks, and filtered nondeterministic errors.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/bindings/bindingtester/bindingtester.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/bindings/bindingtester/known_testers.py -->
# sources/storage-engines/foundationdb/bindings/bindingtester/known_testers.py

## Purpose
This module registers known language binding tester commands and capability constraints.

## Important APIs, Types, And Functions
`COMMON_TYPES` and `ALL_TYPES` define supported tuple value categories. `Tester` stores name, command, max integer bits, API version range, threading support, supported types, and directory snapshot support. `Tester.supports_api_version` checks a version range. `Tester.get_test` resolves a registered tester name or treats an arbitrary string as a command. `_absolute_path` builds paths relative to the bindings tree. `testers` maps Python, Ruby, Java, Java async, Go, Flow, and Swift.

## Control Flow
Imports set `MAX_API_VERSION` from `FDB_API_VERSION`, construct a Java classpath command, and instantiate registry entries with language-specific constraints.

## State And Persistence Behavior
The registry is in-memory and read by `bindingtester.py`. It does not persist data.

## Dependencies And Integration Points
It integrates bindingtester CLI names with built artifacts under `bindings/<language>` and with API/type feature negotiation in `TestRunner`.

## Risks And Edge Cases
Fallback command parsing uses simple string splitting later in the runner. Registry constraints must be updated as bindings gain API/type support. Flow and Swift disable directory snapshot ops.

## Test Signals
Bindingtester startup will fail or reject incompatible options if registry metadata is wrong; external tester invocation failures reveal bad command paths.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/bindings/bindingtester/known_testers.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/bindings/bindingtester/run_binding_tester.sh -->
# sources/storage-engines/foundationdb/bindings/bindingtester/run_binding_tester.sh

## Purpose
This Bash script repeatedly runs FoundationDB binding tester suites across configured language testers, records failures to an error log, and supports random/test-indexed execution.

## Important APIs, Types, And Functions
Environment variables configure operations, HCA operations, concurrency, binding list, break-on-error, test selection, logging, and output capture. Functions include `logError`, `runCommand`, `runScriptedTest`, and `runTest`. Test types are API, concurrent API, Directory, and Directory HCA.

## Control Flow
The script requires cycle count and error-file arguments, initializes runtime state, optionally selects one random binding/test type, optionally runs scripted tests, then loops cycles until max cycles or failure policy stops it. `runCommand` captures output, times commands, logs failures, and increments status. `runTest` invokes `bindingtester.py` with appropriate flags for each selected test type.

## State And Persistence Behavior
It writes an error log and optional console log, reads environment variables, and runs tests against the default cluster settings used by `bindingtester.py`. It does not modify source files.

## Dependencies And Integration Points
It depends on Bash, `python3`, `bindingtester.py`, language tester artifacts, and a reachable FoundationDB cluster. It is a higher-level orchestration wrapper for the Python driver.

## Risks And Edge Cases
The default `BINDINGTESTS` includes `python3`, but `known_testers.py` registers `python`; this may rely on fallback command behavior or fail if no command exists. `LOGSTDOUT` appends to one console log and then reads the entire file into memory on each command. The cycle loop can run forever when max cycles is zero.

## Test Signals
Console output reports pass/fail per command, cycle summaries, failed test count, and error count; the error file captures command output for failures.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/bindings/bindingtester/run_binding_tester.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/bindings/bindingtester/run_tester_loop.sh -->
# sources/storage-engines/foundationdb/bindings/bindingtester/run_tester_loop.sh

## Purpose
This Bash helper runs scripted binding tests once, then loops API/directory binding tests forever across supported languages.

## Important APIs, Types, And Functions
`LOGGING_LEVEL` defaults to `WARNING`. Function `run` invokes `bindingtester.py` for API compare, concurrent API, directory compare, and directory HCA with `--cluster-file fdb.cluster`. Function `scripted` runs scripted tests. `run_scripted` runs scripted tests for Python, Ruby, Java, Java async, Go, Flow, and Swift.

## Control Flow
The script executes `run_scripted`, initializes pass counter `i`, then enters an infinite `while true` loop and runs all test types for each language on every pass.

## State And Persistence Behavior
It writes only process output. The invoked tester mutates the configured FDB cluster by inserting/deleting test keys.

## Dependencies And Integration Points
It expects to be run from a directory containing `bindingtester.py` and `fdb.cluster`, with all language tester artifacts available.

## Risks And Edge Cases
There is no exit condition, error handling, or backoff. Indentation is cosmetic but inconsistent for Swift lines. Failures do not stop the loop unless the shell exits for external reasons.

## Test Signals
The signal is continuous stdout from each bindingtester invocation; operators must monitor failures externally.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/bindings/bindingtester/run_tester_loop.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/bindings/bindingtester/tests/__init__.py -->
# sources/storage-engines/foundationdb/bindings/bindingtester/tests/__init__.py

## Purpose
This module defines the bindingtester test framework: result specifications, abstract test lifecycle hooks, instruction models, single-threaded and multi-threaded instruction containers, and dynamic import of concrete tests.

## Important APIs, Types, And Functions
`ResultSpecification` describes output subspace comparison, key slicing, ordering index, and global error filters. `Test` defines lifecycle methods (`setup`, `generate`, `pre_run`, result specs, expected results, validation) plus versionstamp encoding helpers and `create_test`. `Instruction` and `PushInstruction` encode operations with `fdb.tuple.pack`. `InstructionSet` is a list with stack/core bookkeeping and transactional insertion. `ThreadedInstructionSet` maps subspaces to instruction sets.

## Control Flow
`InstructionSet.insert_operations` chunks operation insertion into 5000-instruction transactions. `Test.create_test` finds a subclass whose module matches `bindingtester.tests.<name>`. `ThreadedInstructionSet` inserts each thread under its own subspace, substituting the caller-provided subspace for `None`.

## State And Persistence Behavior
Instruction insertion writes packed operation records into FoundationDB. In-memory framework state tracks core test boundaries for printing and per-thread instruction maps.

## Dependencies And Integration Points
It depends on FoundationDB tuple/subspace APIs, `bindingtester.util`, and concrete test modules imported by `util.import_subclasses`. `bindingtester.py` uses these classes to generate, insert, print, and validate tests.

## Risks And Edge Cases
`ThreadedInstructionSet.create_thread` raises a string instead of an exception object, which is invalid in Python 3 if triggered. `Test.create_test` assumes one subclass per module. Versionstamp encoding branches on API version 520 compatibility.

## Test Signals
Bindingtester print/run modes exercise instruction insertion, subclass discovery, and result spec filtering. No standalone unit tests are present.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/bindings/bindingtester/tests/__init__.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/bindings/bindingtester/tests/api.py -->
# sources/storage-engines/foundationdb/bindings/bindingtester/tests/api.py

## Purpose
This concrete bindingtester test generates randomized FoundationDB API instruction streams to compare binding behavior across languages. It covers transactions, reads, ranges, mutations, atomic operations, version APIs, tuple operations, conflict ranges, transaction sizing, storage metrics, and versionstamps.

## Important APIs, Types, And Functions
Top-level helpers `matches_op` and `is_non_transaction_op` classify operation variants. `ApiTest` extends `Test`, creates workspace/scratch/stack subspaces, and implements `setup`, stack-depth helpers, key/value generation, database preload, outstanding read waiting, `generate`, `check_versionstamps`, `validate`, and `get_result_specifications`.

## Control Flow
Generation starts with a transaction, read version, and preloaded database. It then randomly selects operations for `args.num_ops`, ensuring required stack types exist before appending instructions. Single-threaded database mutations/read variants wait for futures to keep stack and transactional state coherent. Versionstamp operations write expected correlated keys/values for later validation. Finalization waits for reads, commits, starts a new transaction, logs the stack, and commits again.

## State And Persistence Behavior
Generated instructions mutate a FoundationDB workspace subspace and scratch subspaces for versionstamp validation. The generator tracks stack size, string/key depth, outstanding async reads, generated keys, and capability flags such as `can_set_version`, `can_get_commit_version`, and `can_use_key_selectors`.

## Dependencies And Integration Points
It integrates with `test_util.RandomGenerator`, stack manipulation helpers, FoundationDB tuple/versionstamp APIs, tester instruction interpreters in each language, and `ResultSpecification` comparison with permissible global error filters 1007, 1009, and 1021.

## Risks And Edge Cases
The generator must maintain stack-depth bookkeeping exactly; mismatches become tester failures rather than Python errors. It disables some operations after versionstamp use because key selectors cannot be used safely. Database operations in concurrent mode avoid some non-idempotent atomic choices. Storage metric operations use fixed chunk sizes and randomized non-identical ranges.

## Test Signals
Bindingtester result comparisons over workspace and stack subspaces, plus `validate` versionstamp checks, reveal cross-binding semantic drift or instruction interpreter bugs.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/bindings/bindingtester/tests/api.py -->
