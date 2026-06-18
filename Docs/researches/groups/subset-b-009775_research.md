# subset-b-009775 research

Grouped research for rclone `fs/operations` check, copy, dedupe, listing, logging, JSON, multithread, and shared operation helpers. Each section is source-tree aligned and bounded by reconciliation markers.

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/fs/operations/check.go -->
# sources/user-network-fs/rclone/fs/operations/check.go

## Purpose
`check.go` implements rclone's check and checksum-verification operations. It compares two filesystem trees by size/hash or by downloaded bytes, reports matches, differences, missing files, and errors into separate streams, and also supports validating a filesystem against a hash sum file.

## Important APIs, types, and functions
- `checkFn` is the injectable object comparison function used by `CheckFn`.
- `CheckOpt` carries source/destination filesystems, one-way mode, the comparison function, and output writers for combined and category-specific reports.
- `checkMarch` is the `march.March` callback implementation. It holds context, concurrency tokens, a wait group, output mutex, atomic counters, and copied options.
- `DstOnly`, `SrcOnly`, and `Match` classify tree-walk results into missing-on-source, missing-on-destination, type conflicts, or matched object pairs.
- `CheckFn` drives `march.March` and waits for concurrent object checks before summarizing.
- `Check` supplies hash/size comparison via `CheckHashes`.
- `CheckEqualReaders`, `CheckIdenticalDownload`, and `CheckDownload` implement byte-for-byte download verification.
- `ApplyTransforms` and `ToNormal` normalize checksum file paths for Unicode and case-insensitive matching.
- `CheckSum`, `HashSums`, `ParseSumFile`, `checkSum`, and `matchSum` validate filesystem objects against checksum files.

## Control flow
`CheckFn` builds a `checkMarch`, configures `march.March` with source, destination, traversal flags, and the callback, then runs the march. Directory-only callbacks recurse as needed; object matches spawn goroutines limited by `ci.Checkers`. Each comparison first checks size through `sizeDiffers`, honors `--size-only`, then delegates to the configured `checkFn`. Results are converted into sigils: `+` for source-only, `-` for destination-only, `=` for match, `*` for differ, and `!` for error.

`Check` sets `CheckOpt.Check` to a common-hash comparison. `CheckDownload` instead opens both objects, wraps them in accounting transfers, and compares buffered reads in 64 KiB blocks. `CheckSum` parses a sum file, lists destination objects, matches normalized object names against the parsed map, then performs either backend hash reads or downloaded hash streaming. Remaining unconsumed sums become missing-on-destination errors unless filtered out.

## State and persistence behavior
The file does not persist state itself. It mutates accounting counters, emits logs, writes to caller-provided writers, marks consumed checksum entries by overwriting map values with an empty string, and uses atomics for concurrent summary counters. Remote state is read-only except for implicit backend access caused by object opens and hash calls.

## Dependencies and integration points
The implementation integrates with `fs/accounting`, `fs/filter`, `fs/fserrors`, `fs/hash`, `fs/march`, `Open` from this package, `CheckHashes` and `sizeDiffers` from `operations.go`, synchronized output helpers, and `readers.ReadFill`. It is used by check-like commands and checksum commands, while tests exercise it through `operations.Check`, `CheckDownload`, and `CheckSum`.

## Risks and edge cases
Concurrency makes writer synchronization and counter accuracy important. `CheckEqualReaders` must prefer read errors over equality when an error appears after partial reads. Checksum parsing accepts only standard `hash  filename` or `hash *filename` shapes and suppresses warnings after three malformed or duplicate lines. Unicode normalization and case folding need to match `march.March` behavior so checksum validation aligns with normal check behavior. `CheckSum` uses a shared map across goroutines, so access is protected only around lookup/consume.

## Test signals
`check_test.go` covers normal check output categories, one-way mode, nonexistent filesystem errors, download checks, size-only behavior, reader equality and read-error propagation, checksum parsing, checksum validation in backend-hash and download modes, mixed-case checksums, and Unicode/case transform behavior.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/fs/operations/check.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/fs/operations/check_test.go -->
# sources/user-network-fs/rclone/fs/operations/check_test.go

## Purpose
`check_test.go` validates the tree comparison, download comparison, checksum-file parsing, checksum verification, and path normalization behavior implemented in `check.go`.

## Important APIs, types, and functions
- `testCheck` is a shared scenario runner for `operations.Check` and `operations.CheckDownload`.
- `TestCheck`, `TestCheckDownload`, and `TestCheckSizeOnly` exercise the main comparison modes.
- `TestCheckFsError` validates error propagation from failing filesystems.
- `TestCheckEqualReaders` unit-tests byte-stream comparison.
- `TestParseSumFile` validates checksum-file parser acceptance and rejection cases.
- `testCheckSum`, `TestCheckSum`, and `TestCheckSumDownload` validate `CheckSum` with backend hash reads and downloaded hash calculation.
- `TestApplyTransforms` verifies Unicode normalization and case-folding behavior for checksum filenames.

## Control flow
The tests build local/remote fixture trees with `fstest.NewRun`, then call check functions with every output writer backed by a `bytes.Buffer`. They capture log output, inspect accounting counters for errors and checks, and compare sorted report lines so concurrent check ordering does not make tests flaky. Checksum tests create a data subfilesystem, write a `test.sum` file, update file contents and sums across scenarios, and assert the expected sigil stream.

## State and persistence behavior
The tests create and mutate temporary local and remote test files. They reset `accounting.GlobalStats()` between scenarios and temporarily toggle config flags such as `SizeOnly`, `NoUnicodeNormalization`, and `IgnoreCaseSync`, restoring where needed. No persistent repository state is changed.

## Dependencies and integration points
The file uses rclone `fstest`, `fs`, `accounting`, `hash`, `operations`, `readers.ErrorReader`, `bilib.CaptureOutput`, `testify`, and Unicode normalization helpers. It provides coverage for `check.go` plus shared helpers in `operations.go` such as `CheckHashes` and output counting.

## Risks and edge cases
The expected outputs encode the meaning of check sigils and the distinction between missing-on-source and missing-on-destination. Tests account for concurrency by sorting lines. Unicode tests skip when the backend cannot preserve the requested filename encoding. Size-only tests intentionally accept changed content when sizes match.

## Test signals
The file is the main regression signal for check/report behavior: matching files increment check counts, differences increment error counts, one-way mode suppresses destination-only errors, malformed sum lines are ignored, duplicate sum entries are rejected, mixed-case digests are normalized, and checksum names can be matched through NFC normalization and case folding.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/fs/operations/check_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/fs/operations/copy.go -->
# sources/user-network-fs/rclone/fs/operations/copy.go

## Purpose
`copy.go` implements single-object copy behavior, including server-side copies, streamed/manual copies, multi-threaded copies, partial upload names, transfer-limit checks, retry handling, verification, and the exported `Copy`/`CopyFile` entry points.

## Important APIs, types, and functions
- `copy` stores one copy operation's destination filesystem/features, destination object, remote names, source object, config, common hash, transfer accounting, partial-upload state, and retry limit.
- `removeFailedCopy` and `removeFailedPartialCopy` clean up failed objects.
- `TruncateString` safely truncates byte length while preserving valid UTF-8 where possible.
- `checkPartial` chooses the real remote or a stable hashed partial remote based on config and destination features.
- `checkLimits` enforces `--max-transfer` with hard, cautious, and graceful cutoff semantics.
- `serverSideCopy`, `manualCopy`, `multiThreadCopy`, `rcat`, and `updateOrPut` implement the copy strategies.
- `verify` validates post-transfer size and hash.
- `Copy` prepares accounting and operation state; `CopyFile` invokes shared move/copy file logic.

## Control flow
`Copy` creates an accounting transfer, honors `SkipDestructive`, transforms the destination path, selects a common hash, resolves partial naming, and calls `copy.copy`. The copy loop checks transfer limits, tries server-side copy when the backend supports it and configs are compatible, falls back to manual copy on `fs.ErrorCantCopy`, and retries retriable or `Retry-After` errors up to low-level retry limits.

Manual copy builds upload and download open options from hash, headers, and metadata config. It chooses multi-thread copy when `doMultiThreadCopy` allows it, otherwise opens the source and uses `rcat` for unknown-size streams or `Put`/`Update` for known-size objects. On success it verifies size and hash, then renames a partial object into place when partial uploads were used. On failure it removes partial files or corrupt copies.

## State and persistence behavior
The operation creates, updates, deletes, or renames remote objects. Partial uploads use stable suffixes derived from destination name and source fingerprint, and failed partials are removed both through deferred cleanup and an `atexit` handler. Accounting transfer state is reset on retries and finalized through `tr.Done`.

## Dependencies and integration points
This file depends on `fs.Features` methods such as `Copy`, `Move`, `Put`, and object `Update`; accounting transfers; `CommonHash`, `Open`, `Rcat`, `rcatSrc`, `moveOrCopyFile`, `SkipDestructive`, and `sizeDiffers` from the operations package; `fserrors`, `pacer`, `atexit`, and path/name transforms. It is a core dependency for sync, move, copy command paths, and multi-thread copy.

## Risks and edge cases
Partial names must not exceed backend filename limits and must avoid collisions for long names. `TruncateString` has to preserve valid UTF-8 without corrupting invalid byte strings unexpectedly. Server-side copies may count bytes differently, so accounting is rewound on fallback. Verification must avoid leaving corrupt destination files. Unknown-size streams cannot use ordinary `Put` semantics. Max-transfer cutoff behavior differs by mode and can be affected by server-side copies.

## Test signals
`copy_test.go` covers UTF-8 truncation, basic copy idempotency, maximum local filename length, backup-dir moves, compare-dest and copy-dest behavior, in-place versus partial copy, long partial-name collisions, and max-transfer cutoff modes.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/fs/operations/copy.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/fs/operations/copy_test.go -->
# sources/user-network-fs/rclone/fs/operations/copy_test.go

## Purpose
`copy_test.go` validates single-file copy behavior, partial upload naming, backup/compare/copy destination integration, long filename handling, and transfer-limit enforcement.

## Important APIs, types, and functions
- `TestTruncateString` unit-tests byte truncation with ASCII, multibyte Unicode, emoji, and invalid UTF-8.
- `TestCopyFile` verifies normal copy and no-op self-copy behavior.
- `maxLengthFileName` and `TestCopyLongFile` probe local filesystem filename limits.
- `TestCopyFileBackupDir` validates moving overwritten destination objects into `--backup-dir`.
- `TestCopyFileCompareDest` and `TestCopyFileCopyDest` cover destination avoidance and server-side copy reuse.
- `TestCopyInplace`, `TestCopyLongFileName`, and `TestCopyLongFileNameCollision` exercise partial upload and long-name paths.
- `TestCopyFileMaxTransfer` validates hard, cautious, and soft cutoff behavior.

## Control flow
The tests create `fstest` local/remote files, mutate rclone config via `fs.AddConfig`, call `operations.CopyFile`, and check resulting remote listings. Compare/copy-dest tests create separate destination roots and alternate between stale, matching, and missing files to verify when data is transferred, skipped, copied server-side, or moved to backup. The max-transfer test uses random incompressible data and disables local server-side copies on macOS to force byte accounting.

## State and persistence behavior
All state is temporary test filesystem state. Config values such as `BackupDir`, `CompareDest`, `CopyDest`, `Inplace`, `Transfers`, `MaxTransfer`, and `CutoffMode` are mutated in scoped contexts. Accounting counters are reset around transfer-limit assertions.

## Dependencies and integration points
The file depends on `fs`, `accounting`, `operations`, `sync.CopyDir`, `fstest`, `testify`, crypto randomness, and runtime-specific behavior. It primarily tests `copy.go` but also covers `moveOrCopyFile`, `BackupDir`, `NeedTransfer`, `CompareOrCopyDest`, and partial-upload support from backend feature flags.

## Risks and edge cases
Some scenarios are backend-dependent and skipped when features are missing. Server-side copies can hide byte-transfer accounting, so tests adapt on Darwin/local remotes. Long filename and partial suffix behavior depends on filesystem limits. Copy-dest requires server-side copy support and backup-dir requires server-side move or copy.

## Test signals
The tests confirm copies are idempotent, overwritten files can be preserved in backup dirs, compare-dest can suppress transfers, copy-dest can seed the destination via server-side copy, partial upload names remain safe for long filenames and concurrent collisions, and max-transfer modes return the expected fatal or graceful errors.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/fs/operations/copy_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/fs/operations/dedupe.go -->
# sources/user-network-fs/rclone/fs/operations/dedupe.go

## Purpose
`dedupe.go` resolves duplicate file names or duplicate hashes on backends that can expose multiple objects at the same path, and can also merge duplicate directories before file deduplication.

## Important APIs, types, and functions
- `dedupeRename` renames duplicate files to numbered suffixes without colliding with existing names.
- `dedupeDeleteAllButOne` deletes all duplicate objects except a selected index.
- `dedupeDeleteIdentical` removes duplicates that share size or hash, while avoiding duplicate object IDs that appear multiple times in listings.
- `dedupeList` and `dedupeInteractive` print duplicate choices and optionally prompt the user.
- `DeduplicateMode` is the pflag-compatible mode enum with `Set`, `String`, and `Type`.
- `dedupeDir`, `dedupeDirsMap`, `dedupeFindDuplicateDirs`, and `dedupeMergeDuplicateDirs` detect duplicate directories and call backend `MergeDirs`.
- `Deduplicate` is the exported orchestration function.

## Control flow
`Deduplicate` selects a backend hash when needed, logs the duplicate criterion, optionally scans and merges duplicate directories for name-based dedupe, then lists all objects recursively. It groups objects either by remote path or by hash. For each duplicate group, name-based dedupe first removes identical copies where possible, then applies the requested mode: interactive, first, newest, oldest, rename, largest, smallest, skip, or list.

Directory dedupe walks all entries, builds directory nodes keyed by backend IDs when available, tracks parent relationships and recursive child counts, sorts duplicate directory names parent-first, and merges each duplicate set with the largest subtree first to minimize movement.

## State and persistence behavior
This file performs destructive remote mutations: object deletion, server-side object moves, and directory merges. It respects `SkipDestructive` before renames and directory merges, while `DeleteFile` handles its own destructive checks. It does not persist local state beyond in-memory grouping maps.

## Dependencies and integration points
It uses `fs.Features().Move`, `PutUnchecked`, `MergeDirs`, and `DirCacheFlush`; `fs.IDer` and `fs.ParentIDer`; `walk.ListR`; `operations.DeleteFile`; `accounting` checking transfers; `config.Command`; and hash support from `fs/hash`. It is the implementation behind the rclone dedupe command.

## Risks and edge cases
Backends can report the same object ID multiple times; deleting those would risk data loss, so repeated IDs are ignored. Hashless backends fall back to size-only behavior only when configured. Rename mode must avoid existing `name-N.ext` collisions and gives up after many attempts. Directory merging depends on backend support and cache flushing. Interactive mode can terminate the whole dedupe pass.

## Test signals
`dedupe_test.go` covers pflag compatibility, interactive/default behavior, skip, size-only duplicate deletion, first/newest/oldest/largest/smallest selection, by-hash dedupe, rename collision avoidance, and `MergeDirs` behavior.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/fs/operations/dedupe.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/fs/operations/dedupe_test.go -->
# sources/user-network-fs/rclone/fs/operations/dedupe_test.go

## Purpose
`dedupe_test.go` validates the duplicate-file and duplicate-directory behavior implemented by `dedupe.go` across supported backend features.

## Important APIs, types, and functions
- The compile-time assertion ensures `DeduplicateMode` satisfies `pflag.Value`.
- `skipIfCantDedupe`, `skipIfNoHash`, and `skipIfNoModTime` gate backend-dependent scenarios.
- Tests cover all selection modes: interactive, skip, first, newest, oldest, largest, smallest, rename, and newest by hash.
- `TestMergeDirs` directly validates backend `MergeDirs` behavior used by directory dedupe.

## Control flow
Tests create duplicate objects using `WriteUncheckedObject` where backends support duplicate files. They then call `operations.Deduplicate` with a specific mode and assert resulting remote listings through `CheckRemoteItems`, `CheckWithDuplicates`, `operations.Count`, or `walk.ListR`. Selection tests vary content size and modtime so the expected survivor is identifiable.

## State and persistence behavior
The tests mutate temporary remote state by creating duplicate files, deleting duplicates through the operation under test, renaming duplicates, and merging directories. `TestDeduplicateSizeOnly` temporarily sets `ci.SizeOnly` and restores it afterward.

## Dependencies and integration points
The file depends on backend feature flags, `fs/hash`, `operations`, `walk`, `fstest`, random content generation, `pflag`, and `testify`. It primarily tests `Deduplicate` but also exercises shared deletion and counting helpers.

## Risks and edge cases
Most tests are skipped unless the selected backend can represent duplicates and supports `PutUnchecked`, `MergeDirs`, hashes, or modtimes as needed. The first-mode test polls count because duplicate deletion may be eventually consistent. Rename tests verify existing non-duplicate numbered names are preserved.

## Test signals
The scenarios confirm that identical duplicates can be removed before mode-specific decisions, size-only mode groups by size, by-hash mode can dedupe same content at different paths, rename mode avoids collisions, and directory merge consolidates children into one directory.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/fs/operations/dedupe_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/fs/operations/listdirsorted_test.go -->
# sources/user-network-fs/rclone/fs/operations/listdirsorted_test.go

## Purpose
`listdirsorted_test.go` provides integration tests for `fs/list` directory sorting behavior from the operations test package to avoid import cycles in the list package itself.

## Important APIs, types, and functions
- `testListDirSorted` is a shared scenario runner for list functions.
- `TestListDirSorted` tests `list.DirSorted`.
- `TestListDirSortedFn` adapts and tests `list.DirSortedFn`.

## Control flow
The shared test creates a fixture tree with files, nested directories, and an `.ignore` file. It toggles `filter.GetConfig(ctx).Opt.MaxSize` and later `ExcludeFile`, then lists root and subdirectories with `includeAll` both true and false. It converts returned entries to strings with trailing `/` for directories and asserts sorted order and filtering behavior.

## State and persistence behavior
The file writes temporary test objects through `fstest.NewRun`. It mutates global filter options (`MaxSize` and `ExcludeFile`) during the test and resets them. No repository files are persisted.

## Dependencies and integration points
The tests integrate `fs/list` with `fs/filter`, `fstest`, and the operations test package. They indirectly validate behavior relied on by listing and sync operations that expect sorted, filter-aware directory entries.

## Risks and edge cases
The key edge cases are size filtering, include-all bypass behavior, directory ordering, nested ignore-file behavior, and ensuring `DirSortedFn` and `DirSorted` stay equivalent. Filter globals must be reset to avoid leaking state into later tests.

## Test signals
Expected results show that include-all lists files even when normal filtering excludes them, directories remain visible when they may contain included children, `.ignore` can suppress a directory's contents, and both list APIs produce identical sorted output.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/fs/operations/listdirsorted_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/fs/operations/logger.go -->
# sources/user-network-fs/rclone/fs/operations/logger.go

## Purpose
`logger.go` implements reusable sync/check logging primitives. It maps operation outcomes to sigils and writers, stores logger functions/options in context, predicts post-sync destination winners, and formats `--dest-after` output through `ListFormat`/`ListJSON`.

## Important APIs, types, and functions
- `Sigil` and constants `MissingOnSrc`, `MissingOnDst`, `Match`, `Differ`, `TransferError`, and `Other` categorize sync outcomes.
- `LoggerFn` is the callback signature used by sync-like operations.
- `LoggerOpt` contains output writers, JSON/list formatting options, filters, and a destination-after listJSON instance.
- `NewDefaultLoggerFn`, `WithLogger`, `WithLoggerOpt`, `GetLogger`, `GetLoggerOpt`, `WithSyncLogger`, and `NewLoggerOpt` manage logging callbacks and default buffers.
- `Winner` and `WinningSide` infer which source or destination entry should exist after sync.
- `SetListFormat`, `NewListJSON`, `JSONEntry`, and `PrintDestAfter` produce formatted destination-after lines.

## Control flow
Default logging locks a mutex, ignores non-object pairs unless handling destination-after directory output, chooses a filename from source or destination, writes to the category writer and combined writer, and optionally prints the predicted destination-after state. `WinningSide` branches on sigil, dry-run, delete-mode-off, ignore/update config flags, directory errors, and transfer errors to choose `src`, `dst`, or no winner. `SetListFormat` maps format characters to `ListFormat` output functions and parallel `ListJSONOpt` settings.

## State and persistence behavior
State is stored in contexts and caller-owned buffers/writers. `NewLoggerOpt` initializes in-memory buffers for every output class. The logger itself does not mutate remote state, but its winner prediction depends on config and may read metadata/hash fields when formatting destination-after output.

## Dependencies and integration points
It integrates with `operations.ListFormat`, `ListJSONOpt`, and `listJSON`, `fs.ConfigInfo`, `fs.DirEntry`/`Object`, hash types, `pflag`, and synchronized output helpers. Sync and bisync use these APIs to capture combined result logs and destination-after inventories.

## Risks and edge cases
Winner prediction is approximate for max-duration hard cutoffs, compare/copy-dest, high-level retries, server-side directory moves, and some error cases. The default logger must avoid nil writer panics and must not emit directories as ordinary file entries. `errors.Is(err, errors.New(...))` in one branch cannot match a freshly allocated error, so deadline handling is the reliable path there.

## Test signals
This file has no dedicated test in this subset, but it is exercised indirectly by sync/copy/check tests that install loggers or inspect combined output. `check.go` has a separate reporting implementation with similar sigils, and `operations.go` calls logger callbacks from equality, transfer, deletion, and move/copy decisions.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/fs/operations/logger.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/fs/operations/lsjson.go -->
# sources/user-network-fs/rclone/fs/operations/lsjson.go

## Purpose
`lsjson.go` converts filesystem directory entries into JSON-friendly listing records and implements recursive/non-recursive JSON list and stat operations.

## Important APIs, types, and functions
- `ListJSONItem` is the exported JSON record with path, name, encrypted names, size, MIME type, modtime, directory flags, hashes, IDs, tier, bucket marker, and metadata.
- `Timestamp.MarshalJSON` formats timestamps according to backend precision and emits `""` for zero time.
- `formatForPrecision` maps backend time precision to RFC3339-like formats.
- `ListJSONOpt` controls recursion, omitted fields, encrypted display, original IDs, hashes, file/dir filters, metadata, and selected hash types.
- `listJSON` stores resolved options, crypt cipher, hash types, and backend feature flags.
- `newListJSON`, `entry`, `ListJSON`, and `StatJSON` are the core constructors and listing/stat APIs.

## Control flow
`newListJSON` resolves file/dir inclusion mode, optionally loads crypt configuration and cipher for encrypted path display, captures backend precision and tier/bucket features, and normalizes requested hash types. `entry` filters files or directories, fills core fields, optionally reads modtime, MIME type, encrypted path, metadata, IDs, original IDs, hashes, tier, and bucket markers. `ListJSON` walks the tree with `walk.ListR` and calls a callback for every non-filtered item. `StatJSON` special-cases root, tries `NewObject` for file paths, then lists the parent directory to find directory entries or case-insensitive matches.

## State and persistence behavior
The file is read-only toward remotes. It may read object hashes, metadata, MIME type, tier, and directory listings. It stores only transient listing configuration and callback output.

## Dependencies and integration points
It depends on the `crypt` backend for encrypted name display, `fs` metadata/ID/tier interfaces, `accounting.Stats().Listed`, `hash`, `walk.ListR`, and shared `ConfigMaxDepth`. It is used by `lsjson`, `stat`, logger destination-after output, and list formatting.

## Risks and edge cases
Encrypted output only works for crypt remotes and requires loading the backend config. `FilesOnly` and `DirsOnly` both true intentionally means both are included. `StatJSON` lacks a direct generic `NewDirEntry` primitive, so directory stat falls back to parent listing and can be affected by backend case sensitivity or root existence semantics. Hash and metadata reads log errors but still return partial items.

## Test signals
`lsjson_test.go` covers default, files-only, dirs-only, recursive, subdirectory, no-modtime, no-mimetype, show-hash, explicit hash types, metadata, root stat, file stat, directory stat with trailing slash, not-found handling, and backend root error behavior.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/fs/operations/lsjson.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/fs/operations/lsjson_test.go -->
# sources/user-network-fs/rclone/fs/operations/lsjson_test.go

## Purpose
`lsjson_test.go` validates JSON listing and stat conversion for files, directories, recursion, optional fields, hash maps, metadata, and not-found behavior.

## Important APIs, types, and functions
- `compareListJSONItem` compares expected and actual `ListJSONItem` values with backend precision-aware modtime checks.
- `TestListJSON` exercises `operations.ListJSON` option combinations.
- `TestStatJSON` exercises `operations.StatJSON` for root, files, directories, trailing slashes, not-found paths, and file/dir filters.

## Control flow
The tests create two files, one at root and one in a subdirectory, then run table-driven scenarios. `ListJSON` callbacks collect items, sort by path, compare structural fields, and assert optional MIME, metadata, and hash behavior. `StatJSON` table scenarios call the single-entry API and compare nil or non-nil results.

## State and persistence behavior
Tests create temporary files on local and remote test backends. They do not mutate global config beyond what `fstest` requires. Assertions adapt to backend features such as metadata support, bucket-based roots, and available hashes.

## Dependencies and integration points
The file depends on `fs`, `operations`, `fstest`, `testify`, sorting, and precision helpers. It directly tests `lsjson.go` and indirectly checks backend metadata/hash implementations through optional assertions.

## Risks and edge cases
Hash expectations are conditional because different backends expose different hash families. Metadata assertions are feature-gated for files and directories. Root stat can return an error for non-bucket backends when the target root does not exist, while bucket-based backends may not.

## Test signals
The tests confirm `FilesOnly` and `DirsOnly` filtering, recursion depth, subdirectory listing, omitted modtime/MIME fields, hash selection, metadata population, root directory representation, trailing slash directory lookup, and nil results for filtered or missing entries.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/fs/operations/lsjson_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/fs/operations/multithread.go -->
# sources/user-network-fs/rclone/fs/operations/multithread.go

## Purpose
`multithread.go` implements chunked parallel object copying for large known-size transfers when the destination supports chunk or random-access writers and the source can satisfy ranged reads.

## Important APIs, types, and functions
- `doMultiThreadCopy` decides whether a transfer should use multi-thread copy based on config, source size, source/destination feature flags, cutoff, and local/local defaults.
- `multiThreadCopyState` holds source, size, chunk size, chunk count, accounting, and buffering mode.
- `copyChunk` performs a ranged read and writes one chunk.
- `calculateNumChunks` computes ceiling division for chunk counts.
- `multiThreadCopy` orchestrates writer setup, concurrency, abort behavior, metadata/modtime finalization, and destination lookup.
- `writerAtChunkWriter` adapts `fs.OpenWriterAt` into `fs.ChunkWriter`.
- `openChunkWriterFromOpenWriterAt` builds that adapter.

## Control flow
`multiThreadCopy` selects `OpenChunkWriter` or adapts `OpenWriterAt`. It disables buffering when the source is local, the writer does not seek, or the destination uses `OpenWriterAt`; otherwise each chunk is pre-read into a reserved multipart buffer. It opens the chunk writer, adjusts backend-provided chunk size and concurrency, limits concurrency to chunk count, and runs chunk goroutines under an `errgroup`. Each chunk opens a ranged source reader, accounts bytes, writes via `WriteChunk`, and reports failures. After all chunks complete, it closes the writer, finds the uploaded object, and for `OpenWriterAt` destinations sets metadata or modtime if needed.

## State and persistence behavior
The operation creates or overwrites a destination object. On error or process exit it aborts multipart state unless the backend requests leaving parts or upload completed successfully. For `OpenWriterAt` adapters, abort closes the writer and removes the temporary destination object. Accounting is attached to a single transfer account shared by chunk reads.

## Dependencies and integration points
It uses `fs.Features().OpenChunkWriter`, `OpenWriterAt`, `ChunkWriterDoesntSeek`, `NoMultiThreading`, metadata interfaces, `Open` from operations, accounting, `atexit`, multipart buffers, pool readers/writers, and `errgroup`. `copy.go` calls it from manual copy when eligible.

## Risks and edge cases
Unknown-size or zero-size objects cannot use this path. Backend-provided chunk size and concurrency can override config. Buffered mode reserves memory before opening source readers to avoid many blocked goroutines, but large concurrency/chunk sizes still carry memory pressure. Abort behavior must avoid deleting a pre-existing canary object when partial uploads are unsupported. Metadata setting may fail if destination lacks `SetMetadataer`.

## Test signals
`multithread_test.go` covers eligibility decisions, chunk-count calculation, actual multi-thread uploads/downloads around chunk boundaries, metadata preservation, backend chunk-size probing, and abort behavior when a later ranged read fails.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/fs/operations/multithread.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/fs/operations/multithread_test.go -->
# sources/user-network-fs/rclone/fs/operations/multithread_test.go

## Purpose
`multithread_test.go` validates the decision logic, chunk calculation, end-to-end chunked copy behavior, metadata handling, and abort safety for `multithread.go`.

## Important APIs, types, and functions
- `TestDoMultiThreadCopy` unit-tests feature/config eligibility.
- `TestMultithreadCalculateNumChunks` validates ceiling division.
- `skipIfNotMultithread` gates integration tests and probes backend chunk size.
- `TestMultithreadCopy` copies data across local/remote directions at chunk-boundary sizes.
- `errorObject`, `errorReadCloser`, and `wgReadCloser` simulate late ranged-read failure.
- `TestMultithreadCopyAbort` verifies abort does not overwrite or leave the wrong destination state.

## Control flow
The eligibility test constructs mock filesystems and toggles config and feature flags. The integration test probes chunk size, creates content with sizes just below, equal to, and above two chunks, alternates upload/download direction, optionally sets metadata on sources, calls `multiThreadCopy` directly with a transfer, and verifies listings, sizes, paths, metadata, and cleanup. The abort test writes a canary destination, then wraps the source so the final ranged read fails after earlier chunks start.

## State and persistence behavior
Tests create temporary local/remote files, toggle global multi-thread config fields and restore them, temporarily restrict hashes for local backend performance, create and abort multipart or writer-at uploads, and reset accounting counters. They remove copied source/destination objects after successful copy scenarios.

## Dependencies and integration points
The tests use mock fs/object packages, `fs`, `accounting`, `hash`, `object.NewStaticObjectInfo`, `fstest`, random content, synchronization primitives, and `testify`. They exercise internal unexported functions because the test package is `operations`.

## Risks and edge cases
Backends may skip because they lack chunk writers or because a probe file is too small for multipart upload. Size limits can skip large transfer cases. Abort expectations differ when a backend uses partial uploads versus direct overwrite semantics. The simulated read failure coordinates chunks with a wait group to ensure failure happens after some chunks have begun.

## Test signals
The tests confirm multi-threading is disabled for too few streams, small files, unsupported destinations, local/local defaults, or source opt-out; enabled when explicitly requested and supported; chunk counts are correct; copied files preserve size/modtime/listing and sometimes metadata; and failed chunk copies do not silently replace a canary destination.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/fs/operations/multithread_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/fs/operations/operations.go -->
# sources/user-network-fs/rclone/fs/operations/operations.go

## Purpose
`operations.go` is the central generic operations module for rclone filesystems and objects. It implements equality checks, move/delete/list/hash/count/directory operations, stream uploads, URL copies, backup/compare/copy-dest support, transfer decisions, destructive-operation prompting, list formatting, directory metadata, and filesystem info extraction.

## Important APIs, types, and functions
- Equality and identity: `CheckHashes`, `Equal`, `DirsEqual`, `CommonHash`, `SameObject`, `SameRemoteType`, `SameConfig`, `Same`, `SameDir`, `OverlappingFilterCheck`, `NeedTransfer`.
- Move/copy/delete orchestration: `Move`, `MoveTransfer`, `DeleteFileWithBackupDir`, `DeleteFilesWithBackupDir`, `Purge`, `Delete`, `RemoveExisting`, `MoveFile`, `TransformFile`.
- Listing/output/hash utilities: `ListFn`, `List`, `ListLong`, `HashSum`, `HashLister`, `HashSumStream`, `Count`, `ListDir`, `SizeString`, `CountString`, and synchronized print helpers.
- Directory and metadata operations: `Mkdir`, `MkdirMetadata`, `MkdirModTime`, `TryRmdir`, `Rmdir`, `Rmdirs`, `DirMove`, `DirMoveCaseInsensitive`, `CopyDirMetadata`, `SetDirModTime`.
- Streaming and external input: `Cat`, `Rcat`, `RcatSize`, `CopyURL`, `CopyURLToWriter`.
- Policy/config helpers: `GetCompareDest`, `GetCopyDest`, `CompareOrCopyDest`, `BackupDir`, `MoveBackupDir`, `SkipDestructive`, `Retry`, `GetFsInfo`.
- Formatting: `ListFormat` and `FormatForLSFPrecision`.

## Control flow
Equality first compares size unless ignored, then respects size-only/checksum/mtime/update flags, reads common hashes when useful, may update destination modtime, and emits logger callbacks. `NeedTransfer` layers higher-level policy on top: destination absence, ignore-existing, ignore-times, update-older, custom equal functions, and same-object detection.

Move tries backend server-side move when configs/types allow it, deleting or case-renaming destinations safely, then falls back to copy plus source delete. Copy behavior is implemented in `copy.go`, while `moveOrCopyFile` coordinates object lookup, backup-dir/copy-dest/compare-dest, case-insensitive two-step moves, transfer decisions, and optional deletion of moved sources.

Listing and hash functions walk filesystems with `walk.ListR`, use checkers/transfers concurrency, and serialize output through `StdoutMutex`. Stream upload functions choose between small buffered `Put`, spooled temporary file `Put`, or backend `PutStream`, then verify the uploaded result through equality logic. Directory move attempts backend `DirMove` first, otherwise creates destination directories, moves files in parallel, and removes source directories bottom-up.

## State and persistence behavior
This file performs most remote mutations in the operations package: object creation/update/removal, server-side moves/copies, directory creation/removal, trash cleanup, backup moves, tier changes, touch operations, and metadata/modtime updates. It mutates accounting statistics and logger outputs. Interactive skip decisions are cached in the package-level `skipped` map protected by `interactiveMu`; `checksumWarning` and `modTimeUploadOnce` suppress repeated logs.

## Dependencies and integration points
It integrates with nearly all rclone core primitives: `fs` interfaces and feature flags, `accounting`, `cache`, config/filter/fserrors/fshttp/hash/object/walk packages, `atexit`, `errcount`, `pacer`, `random`, `readers`, `transform`, `errgroup`, and Unicode normalization. Other files in this subset call its helpers heavily: `check.go` uses hashes/size/retry/listing/output, `copy.go` uses common hash and move/copy policies, `logger.go` is invoked by equality/transfer decisions, and `lsjson.go` reuses depth logic.

## Risks and edge cases
This is high-blast-radius code. Risks include accidental destructive operations when dry-run/interactive checks are bypassed, same-object detection on case-insensitive or Unicode-normalizing filesystems, overlapping backup/compare/copy destinations, partial failures during fallback directory moves, stream uploads that must spool large inputs, hashless remotes under checksum mode, modtime update semantics requiring reupload or delete, and global config/logging state leaking across operations. Some functions use backend optional features and must preserve fallback behavior when unsupported.

## Test signals
This subset includes `operations_internal_test.go` for `sizeDiffers`, while many exported functions are exercised indirectly by `copy_test.go`, `check_test.go`, `dedupe_test.go`, `lsjson_test.go`, and `multithread_test.go`. Broader rclone integration tests outside this work item cover sync, move, delete, listing, and backend feature combinations.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/fs/operations/operations.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/fs/operations/operations_internal_test.go -->
# sources/user-network-fs/rclone/fs/operations/operations_internal_test.go

## Purpose
`operations_internal_test.go` provides package-internal coverage for helpers that are not exported, currently focused on `sizeDiffers`.

## Important APIs, types, and functions
- `TestSizeDiffers` builds static object infos and tests `sizeDiffers` across ignore-size and unknown-size combinations.

## Control flow
The test iterates table cases with source size, destination size, `IgnoreSize`, and expected result. For each case it creates `object.NewStaticObjectInfo` values, temporarily mutates `ci.IgnoreSize`, calls `sizeDiffers`, restores the old config value, and asserts the result.

## State and persistence behavior
No remote state is created. The only state mutation is the temporary global config field `IgnoreSize`, restored after each case.

## Dependencies and integration points
The file uses the internal `operations` package, `fs.GetConfig`, `object.NewStaticObjectInfo`, `time`, and `testify`. It directly tests a helper that affects `Equal`, `Check`, `Copy.verify`, and transfer decisions.

## Risks and edge cases
Unknown sizes (`-1`) should not be treated as differing, and `--ignore-size` must suppress mismatches entirely. Because config is process-global for the context, restoration is essential to avoid contaminating later tests.

## Test signals
The test confirms exact equal sizes return false, positive mismatched known sizes return true, unknown source or destination sizes return false, and ignore-size forces false regardless of sizes.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/fs/operations/operations_internal_test.go -->
