# Research Report: subset-b-009140

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/fs/ignorefs/ignorefs.go -->
## sources/sync-backup/kopia/fs/ignorefs/ignorefs.go

Purpose: implements an `fs.Directory` wrapper that hides entries matched by Kopia policy ignore rules, dot-ignore files, cache-directory markers, file-size limits, and one-filesystem device constraints.

Important APIs/types/functions: `New`, `Option`, `ReportIgnoredFiles`, `ignoreDirectory`, `ignoreContext`, `ignoreDirIterator`, `parseIgnoreFile`, `resolveSymlink`, `overrideFromPolicy`, and `skipCacheDirectory`. `ignoreDirectory` preserves `fs.Directory` behavior while substituting filtered `Child` and `Iterate` results.

Control flow, state, and persistence: each directory builds or reuses an `ignoreContext` from its parent. Parent ignore decisions are applied first, then local policy and dotfile matchers can negate earlier decisions. Dot-ignore entries can be regular files or symlinks resolved through `resolveSymlink`, capped at 30 hops. The wrapper has no durable persistence; it derives state from policy trees, `.kopiaignore`-style files, and cachedir marker contents during traversal. `sync.Pool` recycles wrapper directories and iterators, so callers must respect `Close`.

Dependencies and integration points: depends on `fs` entry interfaces, `internal/wcmatch` wildcard semantics, `internal/cachedir` signatures, `snapshot/policy` trees, and optional `snapshot.HasDirEntryOrNil`. It integrates into snapshot traversal by making ignored entries appear absent.

Risks and test signals: core risks are rule ordering, negation behavior, symlink loops, accidentally traversing mount points, and pooled-object reuse after close. Tests cover nested policies, symlinked ignore files, negated patterns, one-filesystem filtering, cache directory skipping through behavior, and symlink loop protection.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/fs/ignorefs/ignorefs.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/fs/ignorefs/ignorefs_test.go -->
## sources/sync-backup/kopia/fs/ignorefs/ignorefs_test.go

Purpose: table-driven behavioral tests for `ignorefs.New` over a mock filesystem.

Important APIs/types/functions: `setupFilesystem`, policy fixtures (`defaultPolicy`, `rootAndSrcPolicy`, `oneFileSystemPolicy`), `cases`, `TestIgnoreFS`, `walkTree`, `verifyDirectoryTree`, and `addAndSubtractFiles`.

Control flow, state, and persistence: each test builds an in-memory `mockfs.Directory`, optionally mutates it with ignore files, symlinks, and nested directories, wraps it with `ignorefs`, walks the resulting tree, and compares sorted paths against expected additions/removals. There is no persistence beyond the mock tree and policy fixtures.

Dependencies and integration points: exercises `ignorefs` through public `fs.Directory` traversal helpers and `snapshot/policy` trees. Uses mock devices to validate one-filesystem semantics.

Risks and test signals: provides strong coverage of wildcard matching, directory exclusion, inherited ignore files, nested policy overrides, negated patterns, symlinked dot-ignore files, max-file-size filtering, and device filtering. The test suite is especially useful as a compatibility signal with `.gitignore`-style behavior, including the known behavior that empty included directories may remain visible.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/fs/ignorefs/ignorefs_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/fs/ignorefs/resolve_test.go -->
## sources/sync-backup/kopia/fs/ignorefs/resolve_test.go

Purpose: targeted internal-package regression test for symlink loop handling in ignore-file resolution.

Important APIs/types/functions: `TestNoInfiniteResolveLink` constructs a three-link cycle and calls unexported `resolveSymlink`.

Control flow, state, and persistence: the test uses `mockfs` symlinks `a -> b -> c -> a`, resolves one link, and asserts the resolver returns `errTooManySymlinks` with no file. It uses only in-memory state.

Dependencies and integration points: depends on `fs.Symlink`, `mockfs`, and test logging contexts. It validates a safety path that is reachable when dot-ignore files are symbolic links.

Risks and test signals: protects against infinite traversal and stack/resource exhaustion. It does not test successful resolution because those cases are covered in the broader ignorefs tests.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/fs/ignorefs/resolve_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/fs/localfs/doc.go -->
## sources/sync-backup/kopia/fs/localfs/doc.go

Purpose: package documentation declaring `localfs` as the virtual filesystem abstraction over the host local filesystem.

Important APIs/types/functions: no runtime symbols; the package comment is the exported documentation anchor.

Control flow, state, and persistence: none.

Dependencies and integration points: integrates with Go documentation for the `localfs` package, whose implementation maps OS files, directories, symlinks, error entries, and shallow placeholders into Kopia `fs` interfaces.

Risks and test signals: no direct tests required; correctness is tied to package documentation remaining accurate as `localfs` evolves.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/fs/localfs/doc.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/fs/localfs/local_fs.go -->
## sources/sync-backup/kopia/fs/localfs/local_fs.go

Purpose: defines core local filesystem entry types and public constructors for turning OS paths into Kopia `fs.Entry` and `fs.Directory` objects.

Important APIs/types/functions: `filesystemEntry`, `filesystemDirectory`, `filesystemFile`, `filesystemSymlink`, `filesystemErrorEntry`, `Directory`, `NewEntry`, `splitDirPrefix`, `fileWithMetadata.Entry`, `Open`, `Readlink`, and `Resolve`.

Control flow, state, and persistence: entries store name, size, mode, nanosecond mtime, owner/device info, and a prefix used to reconstruct the local path. `Directory` calls `NewEntry` and accepts real directories plus symlinks that may behave like directories, which supports Windows VSS edge cases. `filesystemFile.Open` opens the current OS path and returns a reader that can report updated metadata. There is no internal persistence; state mirrors OS metadata captured at entry creation.

Dependencies and integration points: uses `os`, `filepath`, platform-specific metadata helpers, and Kopia `fs` interfaces. `Resolve` uses `filepath.EvalSymlinks`, so returned paths are canonicalized by the OS.

Risks and test signals: risks include stale metadata, symlink resolution differences, path splitting on Windows/Unix, and object pooling interactions in companion files. Tests cover symlinks, file/directory enumeration, child lookup, root path handling, and split prefix cases.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/fs/localfs/local_fs.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/fs/localfs/local_fs_32bit.go -->
## sources/sync-backup/kopia/fs/localfs/local_fs_32bit.go

Purpose: build-tagged non-Windows helper for platforms where syscall device IDs are represented as `int32`.

Important APIs/types/functions: `platformSpecificWidenDev(dev int32) uint64`.

Control flow, state, and persistence: pure conversion helper with no state. It casts platform device values into the cross-platform `uint64` fields used by `fs.DeviceInfo`.

Dependencies and integration points: used by `local_fs_nonwindows.go` to populate `Dev` and `Rdev`; build tags include darwin/openbsd and non-listed non-Windows architectures.

Risks and test signals: risk is build-tag drift or lossy conversion if platform syscall types change. Device filtering in `ignorefs` indirectly depends on this metadata being stable.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/fs/localfs/local_fs_32bit.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/fs/localfs/local_fs_64bit.go -->
## sources/sync-backup/kopia/fs/localfs/local_fs_64bit.go

Purpose: build-tagged non-Windows helper for platforms where syscall device IDs are already `uint64`.

Important APIs/types/functions: `platformSpecificWidenDev(dev uint64) uint64`.

Control flow, state, and persistence: identity function used when recording `fs.DeviceInfo`.

Dependencies and integration points: used by `local_fs_nonwindows.go` on common Linux-style architectures. It supports downstream one-filesystem comparisons.

Risks and test signals: risk is primarily incorrect build constraints for a new architecture. There are no direct unit tests, but one-filesystem and localfs traversal tests exercise resulting metadata on supported platforms.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/fs/localfs/local_fs_64bit.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/fs/localfs/local_fs_nonwindows.go -->
## sources/sync-backup/kopia/fs/localfs/local_fs_nonwindows.go

Purpose: non-Windows metadata extraction for owner IDs, group IDs, and device identifiers.

Important APIs/types/functions: `isWindows`, `platformSpecificOwnerInfo`, `platformSpecificDeviceInfo`, and `trailingSeparator`.

Control flow, state, and persistence: reads `syscall.Stat_t` from `os.FileInfo.Sys()` and maps UID/GID and device fields into Kopia metadata. `trailingSeparator` is a no-op outside Windows.

Dependencies and integration points: feeds `filesystemEntry` metadata in `newEntry`; device data is consumed by filtering wrappers such as `ignorefs` one-filesystem mode.

Risks and test signals: risks include platform syscall variance and zero metadata when `Sys()` has an unexpected type. Permission-denied and traversal tests indirectly cover non-Windows behavior; device-specific correctness depends on platform integration tests.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/fs/localfs/local_fs_nonwindows.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/fs/localfs/local_fs_os.go -->
## sources/sync-backup/kopia/fs/localfs/local_fs_os.go

Purpose: implements OS directory iteration, child lookup, entry classification, and path-to-entry conversion.

Important APIs/types/functions: `filesystemDirectoryIterator`, `Iterate`, `Child`, `toDirEntryOrNil`, `NewEntry`, `entryFromDirEntry`, and `newEntry`.

Control flow, state, and persistence: directory iterators keep an open `os.File` handle and read `numEntriesToRead` directory entries at a time. For each name, `os.Lstat` decides whether to return a file, directory, symlink, shallow placeholder, or error entry. Permission-denied child `Lstat` failures become `fs.ErrorEntry` instances instead of aborting the directory. `NewEntry` cleans paths and has a Windows retry for direct volume paths that require a trailing separator.

Dependencies and integration points: integrates OS metadata with `fs` interfaces, shallow placeholder detection, and platform-specific metadata functions. `fs.IterateEntries` callers depend on `Close` to release directory handles.

Risks and test signals: risks include leaking directory handles if iterators are not closed, platform-specific path quirks, and inconsistent behavior between `ReadDir` and `Lstat`. Tests cover non-existent iteration, large/small iteration counts, child lookup, local path normalization, split paths, and permission-denied entries.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/fs/localfs/local_fs_os.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/fs/localfs/local_fs_pool.go -->
## sources/sync-backup/kopia/fs/localfs/local_fs_pool.go

Purpose: centralizes object pooling for localfs entry wrappers to reduce allocation churn during large tree traversals.

Important APIs/types/functions: pools for filesystem files, directories, symlinks, error entries, and shallow placeholder entries; constructors such as `newFilesystemFile`; `Close` methods returning objects to pools.

Control flow, state, and persistence: constructors take a pooled struct, overwrite its embedded `filesystemEntry`, and return it. `Close` returns the object to `freepool`. No durable state exists, but object identity is reused aggressively.

Dependencies and integration points: depends on `internal/freepool` and all localfs entry types. It relies on callers respecting `fs.Entry.Close` ownership rules.

Risks and test signals: biggest risk is use-after-close or stale fields if future constructors forget to reset new fields. Traversal tests provide indirect coverage; concurrency hazards are controlled by the assumption that a returned entry is not used after close.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/fs/localfs/local_fs_pool.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/fs/localfs/local_fs_test.go -->
## sources/sync-backup/kopia/fs/localfs/local_fs_test.go

Purpose: validates public localfs behavior against the real temporary filesystem.

Important APIs/types/functions: `TestSymlink`, `TestFiles`, `TestIterate1000`, `TestIterate10`, `TestIterateNonExistent`, `verifyChild`, `TestLocalFilesystemPath`, `TestSplitDirPrefix`, and `TestIteratePermissionDenied`.

Control flow, state, and persistence: tests create temporary files, directories, symlinks, and permission states; wrap them through `Directory`/`NewEntry`; then inspect Kopia `fs` metadata and traversal results. Temporary filesystem state is cleaned up by test helpers.

Dependencies and integration points: tests use OS syscalls directly, `fs.GetAllEntries`, `fs.IterateEntries`, `testutil.TempDirectory`, and platform gates for Windows/root behavior.

Risks and test signals: strong signals for symlink resolution, missing directory errors, callback error propagation, path splitting, local path canonicalization, and permission-denied entries. Platform-specific build files still need coverage on their respective operating systems.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/fs/localfs/local_fs_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/fs/localfs/local_fs_windows.go -->
## sources/sync-backup/kopia/fs/localfs/local_fs_windows.go

Purpose: Windows-specific localfs metadata and path behavior.

Important APIs/types/functions: `isWindows`, `platformSpecificOwnerInfo`, `platformSpecificDeviceInfo`, and `trailingSeparator`.

Control flow, state, and persistence: owner and device metadata return empty values on Windows. `trailingSeparator` detects VSS volume paths under `\\?\GLOBALROOT\Device\HarddiskVolumeShadowCopy...` and adds a separator so directory opens and stats can work.

Dependencies and integration points: used by `local_fs_os.go` during `NewEntry` and `Iterate`; supports snapshotting Windows shadow-copy paths that otherwise fail without a trailing slash.

Risks and test signals: risks include missed VSS path variants and lack of Windows owner/device metadata. Localfs tests include Windows-specific split-prefix cases but must run on Windows to validate the VSS behavior.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/fs/localfs/local_fs_windows.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/fs/localfs/localfs_benchmark_test.go -->
## sources/sync-backup/kopia/fs/localfs/localfs_benchmark_test.go

Purpose: benchmarks directory iteration cost over directories of varying sizes.

Important APIs/types/functions: `BenchmarkReadDir0`, `BenchmarkReadDir1`, `BenchmarkReadDir2`, `BenchmarkReadDir10`, `BenchmarkReadDir100`, `BenchmarkReadDir1000`, `BenchmarkReadDir10000`, and `benchmarkReadDirWithCount`.

Control flow, state, and persistence: each benchmark creates a temp directory with random UUID filenames, then repeatedly opens it through `localfs.Directory` and iterates entries through `fs.IterateEntries`.

Dependencies and integration points: exercises `filesystemDirectoryIterator`, batching size, object pools, and OS directory operations under benchmark conditions.

Risks and test signals: useful for detecting performance regressions in traversal, batching, and allocation behavior. It does not assert correctness beyond successful iteration.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/fs/localfs/localfs_benchmark_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/fs/localfs/shallow_fs.go -->
## sources/sync-backup/kopia/fs/localfs/shallow_fs.go

Purpose: implements shallow restore placeholders that store `snapshot.DirEntry` metadata on disk without materializing original file or directory contents.

Important APIs/types/functions: `WriteShallowPlaceholder`, `placeholderPath`, `dirEntryFromPlaceholder`, `checkedDirEntryFromPlaceholder`, `shallowFilesystemFile`, `shallowFilesystemDirectory`, and their `DirEntryOrNil` methods.

Control flow, state, and persistence: `WriteShallowPlaceholder` JSON-encodes a `snapshot.DirEntry` and writes it atomically to a file path with `.kopia-entry` suffix; directory placeholders are represented as a directory containing a nested `.kopia-entry` file. Reading verifies the real path does not also exist, preventing ambiguous/corrupt shallow trees. Shallow files cannot be opened, and shallow directories cannot be iterated or child-looked-up.

Dependencies and integration points: uses `internal/atomicfile`, `ospath.SafeLongFilename`, and `snapshot.HasDirEntryOrNil`. `entryFromDirEntry` detects the suffix and creates shallow wrappers.

Risks and test signals: risks include interrupted restores leaving both placeholder and real paths, JSON schema drift, and unsupported operations surfacing during traversal. Tests are indirect through localfs and restore behavior elsewhere.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/fs/localfs/shallow_fs.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/fs/localfs/shallowentry.go -->
## sources/sync-backup/kopia/fs/localfs/shallowentry.go

Purpose: defines shallow placeholder naming and a direct placeholder path adapter.

Important APIs/types/functions: `ShallowEntrySuffix`, `dirMode`, `TrimShallowSuffix`, `PlaceholderFilePath`, and `PlaceholderFilePath.DirEntryOrNil`.

Control flow, state, and persistence: suffix trimming normalizes visible entry names. `PlaceholderFilePath.DirEntryOrNil` reads metadata either from the path itself or from a nested `.kopia-entry` file when the path is a directory.

Dependencies and integration points: supports `shallow_fs.go` and any caller that needs to treat a placeholder path as `snapshot.HasDirEntryOrNil`.

Risks and test signals: risks include suffix collisions with real filenames and stale placeholder JSON. Direct tests are absent in this subset; behavior is integrated with shallow restore and localfs classification.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/fs/localfs/shallowentry.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/fs/loggingfs/loggingfs.go -->
## sources/sync-backup/kopia/fs/loggingfs/loggingfs.go

Purpose: provides a filesystem wrapper that logs timing and results for child lookup and directory reads.

Important APIs/types/functions: `Wrap`, `Option`, `Output`, `Prefix`, `loggingDirectory`, `loggingFile`, `loggingSymlink`, and `wrapWithOptions`.

Control flow, state, and persistence: wrapping preserves the underlying entry type when it is a directory, file, or symlink. `Child` times the underlying lookup and wraps the returned entry. `IterateEntries` materializes all entries with `fs.GetAllEntries`, logs count and duration, then invokes the caller callback. No persistence; state is limited to output callback and prefix.

Dependencies and integration points: uses `fs` abstractions and `internal/timetrack`. It is a diagnostic layer and can be inserted around any filesystem entry tree.

Risks and test signals: `applyOptions` defaults `printf` to the caller argument; passing nil without `Output` will panic on first log. Directory iteration changes streaming behavior by collecting all entries first. No dedicated tests in this subset.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/fs/loggingfs/loggingfs.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/fs/utc_timestamp.go -->
## sources/sync-backup/kopia/fs/utc_timestamp.go

Purpose: defines a compact UTC nanosecond timestamp type with JSON and time arithmetic helpers.

Important APIs/types/functions: `UTCTimestamp`, `MarshalJSON`, `UnmarshalJSON`, `ToTime`, `Add`, `Sub`, `After`, `Before`, `Equal`, `Format`, and `UTCTimestampFromTime`.

Control flow, state, and persistence: stores `time.Time.UnixNano()` as an `int64`. JSON unmarshalling delegates to `time.Time.UnmarshalJSON`, then stores the absolute instant; marshaling formats through `ToTime().UTC()`. Persistence format is a JSON timestamp string, not a raw integer.

Dependencies and integration points: used by filesystem/snapshot data needing stable UTC JSON representation.

Risks and test signals: risks include timezone expectations and nanosecond precision. Tests cover JSON round trip, timezone normalization, comparisons, duration arithmetic, formatting, and invalid JSON error wrapping.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/fs/utc_timestamp.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/fs/utc_timestamp_test.go -->
## sources/sync-backup/kopia/fs/utc_timestamp_test.go

Purpose: unit tests for `fs.UTCTimestamp`.

Important APIs/types/functions: `TestUTCTimestamp`.

Control flow, state, and persistence: constructs precise UTC and offset timestamps, marshals/unmarshals through JSON structs, and asserts the stored nanosecond value and UTC formatted output. No external state.

Dependencies and integration points: tests Go `encoding/json` integration and public `fs` timestamp helpers.

Risks and test signals: confirms offset input is normalized to UTC, nanosecond values survive JSON, comparison helpers behave consistently, and invalid input returns an error containing the wrapper message.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/fs/utc_timestamp_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/fs/virtualfs/virtualfs.go -->
## sources/sync-backup/kopia/fs/virtualfs/virtualfs.go

Purpose: implements in-memory `fs.Entry`, static directories, one-shot streaming directories, and one-shot streaming files.

Important APIs/types/functions: `NewStaticDirectory`, `NewStreamingDirectory`, `StreamingFileFromReader`, `StreamingFileWithModTimeFromReader`, `virtualEntry`, `staticDirectory`, `streamingDirectory`, `virtualFile`, and errors for reused readers/iterators.

Control flow, state, and persistence: static directories copy their entry slice for iteration and support repeated traversal. Streaming directories guard a single iterator with a mutex and consume it on first `Iterate`. Streaming files return their reader once and set it nil afterward. There is no persistence beyond in-memory entries and reader state.

Dependencies and integration points: supplies synthetic trees to components expecting `fs.Directory` or `fs.StreamingFile`, useful for generated content and tests.

Risks and test signals: risks are accidental multiple reads and data races on `virtualFile.GetReader`, which explicitly delegates concurrency safety to callers. Tests cover static lookup, streaming one-shot behavior, callback error propagation, and mod-time injection.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/fs/virtualfs/virtualfs.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/fs/virtualfs/virtualfs_test.go -->
## sources/sync-backup/kopia/fs/virtualfs/virtualfs_test.go

Purpose: verifies in-memory virtual filesystem wrappers.

Important APIs/types/functions: `TestStreamingFile`, `TestStreamingFileModTime`, `TestStreamingFileGetReader`, `TestStreamingDirectory`, `TestStreamingDirectory_MultipleIterationsFails`, and `TestStreamingDirectory_ReturnsCallbackError`.

Control flow, state, and persistence: tests pipe or byte-reader content into streaming files/directories, fetch entries through `fs` helpers, read data, and assert one-shot reuse errors. State is in-memory only.

Dependencies and integration points: validates `virtualfs` through public `fs` helpers and `testlogging`.

Risks and test signals: strong coverage for reader consumption and directory iterator consumption. Tests do not stress concurrent calls to `GetReader`, matching the implementation’s caller-safety note.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/fs/virtualfs/virtualfs_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/icons/convert.sh -->
## sources/sync-backup/kopia/icons/convert.sh

Purpose: shell utility for generating Kopia app, tray, and site icon assets from source artwork.

Important APIs/types/functions: `make_icns`, `make_ico`, calls to `sips`, `iconutil`, ImageMagick `convert`, and `cp`.

Control flow, state, and persistence: `set -e` aborts on failure. macOS `.icns` generation creates a temporary `MyIcon.iconset`, resizes multiple icon dimensions, converts it, removes the temp directory, and moves output. Windows `.ico` generation uses ImageMagick auto-resize. The script writes assets under app and site resource directories.

Dependencies and integration points: depends on macOS `sips`/`iconutil` and ImageMagick. Integrated into manual/release asset workflows rather than Go runtime.

Risks and test signals: unquoted variables and fixed temp directory `MyIcon.iconset` can fail with spaces or concurrent runs. There are no automated tests; validation is visual/asset-existence oriented.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/icons/convert.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/internal/acl/access_level.go -->
## sources/sync-backup/kopia/internal/acl/access_level.go

Purpose: defines ACL access-level enumeration and JSON/string conversion.

Important APIs/types/functions: `AccessLevel`, constants `AccessLevelNone`, `AccessLevelRead`, `AccessLevelAppend`, `AccessLevelFull`, `SupportedAccessLevels`, `ParseAccessLevel`, `MarshalJSON`, `UnmarshalJSON`, and `String`.

Control flow, state, and persistence: access levels are integers persisted as JSON strings (`NONE`, `READ`, `APPEND`, `FULL`). Reverse lookup is built in `init`. Unknown marshal values fail; unknown unmarshal strings silently map to zero because map lookup is unchecked.

Dependencies and integration points: used by `acl.Entry`, auth authorization aliases, and repository ACL manifests.

Risks and test signals: silent unknown-string unmarshal can produce invalid zero values that later `Validate` should reject, but direct JSON callers may need care. Tests cover valid JSON serialization round trip.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/internal/acl/access_level.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/internal/acl/access_level_test.go -->
## sources/sync-backup/kopia/internal/acl/access_level_test.go

Purpose: validates JSON serialization for all supported ACL access levels.

Important APIs/types/functions: `TestAccessLevelJSONSerialization`.

Control flow, state, and persistence: creates a struct containing each access level, marshals with indentation, compares exact JSON strings, then unmarshals and compares the struct.

Dependencies and integration points: exercises Go JSON integration for repository ACL manifests.

Risks and test signals: confirms only the valid happy path. It does not test unsupported strings or invalid numeric values, leaving error-path coverage to validation tests.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/internal/acl/access_level_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/internal/acl/acl.go -->
## sources/sync-backup/kopia/internal/acl/acl.go

Purpose: defines ACL entry schema, target matching rules, placeholders, and validation.

Important APIs/types/functions: `ContentManifestType`, `OwnUser`, `OwnHost`, `TargetRule`, `TargetRule.matches`, `Entry`, `Entry.Validate`, label validators, and allowed-label maps.

Control flow, state, and persistence: `Entry` is persisted as JSON in manifests while `ManifestID` is runtime-only. Validation requires `user@host`, a target `type`, labels allowed for that type, non-empty/one-of constraints, and a supported access level. Matching replaces `OWN_USER` and `OWN_HOST` placeholders with the authenticated username/hostname and then performs exact label matching.

Dependencies and integration points: integrates with manifest labels, snapshot/policy/user manifest types, and auth ACL evaluation.

Risks and test signals: risks include overly narrow label allowlists, placeholder substitution surprises, and the comment typo mentioning `OWN_VALUE` instead of `OWN_HOST`. ACL manager tests cover many validation errors and allowed target types.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/internal/acl/acl.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/internal/acl/acl_manager.go -->
## sources/sync-backup/kopia/internal/acl/acl_manager.go

Purpose: loads, filters, evaluates, and writes ACL manifest entries.

Important APIs/types/functions: `EntriesForUser`, `EffectivePermissions`, `LoadEntries`, `AddACL`, `matchOrWildcard`, and `userMatches`.

Control flow, state, and persistence: ACLs are stored as manifests labeled `type=acl`. `LoadEntries` lists manifests, reuses entries from a caller-provided cache by manifest ID, loads misses, and attaches IDs. `EffectivePermissions` scans matching user and target rules, returning the highest access level. `AddACL` validates, loads existing ACLs, optionally replaces same user+target entries, and writes the new manifest.

Dependencies and integration points: depends on repository manifest APIs and `Entry.Validate`. Auth uses this as the ACL source of truth.

Risks and test signals: risks include cache staleness if a manifest changes under the same ID, wildcard-only user matching, and overwrite semantics that delete old entries before writing new ones. Tests cover effective permissions, cache reuse loading, validation, and add behavior.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/internal/acl/acl_manager.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/internal/acl/acl_manager_test.go -->
## sources/sync-backup/kopia/internal/acl/acl_manager_test.go

Purpose: tests ACL matching, effective permission computation, repository load/add, and validation errors.

Important APIs/types/functions: `TestEffectivePermissions`, `TestLoadEntries`, and `TestACLEntryValidation`.

Control flow, state, and persistence: tests create in-memory repository environments, add ACL manifests, reload with cached prior entries, and evaluate label maps for users/hosts. Validation cases assert exact error messages for invalid target types, labels, policy types, users, missing type labels, and invalid access.

Dependencies and integration points: exercises `acl` package against real repository manifest operations through `repotesting`.

Risks and test signals: strong signal for intended ACL semantics, including highest-access-wins and placeholder matching. Does not test delete failure recovery in `AddACL` or concurrent ACL writes.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/internal/acl/acl_manager_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/internal/apiclient/apiclient.go -->
## sources/sync-backup/kopia/internal/apiclient/apiclient.go

Purpose: HTTP helper client for Kopia API server calls, including JSON/body handling, CSRF support, auth transport, logging, TLS pinning, and Unix-socket URLs.

Important APIs/types/functions: `KopiaAPIClient`, `Options`, `NewKopiaAPIClient`, `Get`, `Post`, `Put`, `Delete`, `FetchCSRFTokenForTesting`, `HTTPStatusError`, `requestReader`, `decodeResponse`, `basicAuthTransport`, and `loggingTransport`.

Control flow, state, and persistence: the client stores base URL, HTTP client/cookie jar, and an optional CSRF token. Requests choose binary or JSON request bodies, add CSRF and content type headers, run through configured transports, and decode bytes or JSON on HTTP 200. Non-200 responses become `HTTPStatusError`, optionally parsing an `error` JSON field. Unix URL schemes clone the transport and override dialing to a socket path.

Dependencies and integration points: integrates with server API tests and clients, `tlsutil.TransportTrustingSingleCertificate`, `timetrack`, and Go HTTP cookie management.

Risks and test signals: risks include nil/default transport type assertion assumptions for Unix sockets, greedy CSRF regex, response body consumed for error parsing, and lack of explicit timeout. No tests in this subset directly cover it.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/internal/apiclient/apiclient.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/internal/atomicfile/atomicfile.go -->
## sources/sync-backup/kopia/internal/atomicfile/atomicfile.go

Purpose: thin wrapper for atomic file writes that normalizes long filenames through Kopia path handling.

Important APIs/types/functions: `Write(filename string, r io.Reader) error`.

Control flow, state, and persistence: delegates to `atomic.WriteFile(ospath.SafeLongFilename(filename), r)`. It persists exactly the reader content through the third-party atomic-write implementation.

Dependencies and integration points: used by shallow placeholder writing and other code that needs atomic replacement on Windows-safe paths.

Risks and test signals: risks are inherited from `natefinch/atomic` behavior and path normalization. No direct tests in this subset.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/internal/atomicfile/atomicfile.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/internal/auth/authn.go -->
## sources/sync-backup/kopia/internal/auth/authn.go

Purpose: authentication abstraction and implementations for single-user credentials, composed authenticators, and htpasswd files.

Important APIs/types/functions: `Authenticator`, `AuthenticateSingleUser`, `CombineAuthenticators`, `AuthenticateHtpasswdFile`, `singleUserAuthenticator`, `combinedAuthenticator`, and `htpasswdAuthenticator`.

Control flow, state, and persistence: single-user auth stores expected username/password bytes and compares both with `subtle.ConstantTimeCompare`. Combined auth returns true on the first authenticator accepting credentials and refreshes all authenticators in order. htpasswd auth delegates matching and reload to the external `htpasswd.File`.

Dependencies and integration points: used by API/server authentication flows and repository-based authentication in companion files.

Risks and test signals: length-dependent behavior still exists in Go constant-time compare, but username and password comparisons avoid ordinary string equality. Tests cover accepted/rejected credentials and combining behavior.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/internal/auth/authn.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/internal/auth/authn_repo.go -->
## sources/sync-backup/kopia/internal/auth/authn_repo.go

Purpose: repository-backed user authenticator that loads `user.Profile` manifests and validates passwords.

Important APIs/types/functions: `AuthenticateRepositoryUsers`, `repositoryUserAuthenticator`, `IsValid`, `Refresh`, and `defaultProfileRefreshFrequency`.

Control flow, state, and persistence: the authenticator caches profiles per repository with a mutex and refresh deadline. If the repository changes, it clears the profile map and forces reload. On refresh, it calls `user.LoadProfileMap`, logs errors without failing closed beyond current cache state, and validates `username` via `Profile.IsValidPassword`; nil map/profile behavior is intentionally safe.

Dependencies and integration points: depends on repository interfaces, `internal/user`, and `clock`. Used in server auth to support repository-managed users.

Risks and test signals: risks include stale user cache for up to the refresh frequency and continuing with old profiles after load errors. Tests cover valid/invalid users and password hash versions.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/internal/auth/authn_repo.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/internal/auth/authn_repo_test.go -->
## sources/sync-backup/kopia/internal/auth/authn_repo_test.go

Purpose: verifies repository-backed authentication against stored user profiles.

Important APIs/types/functions: `TestRepositoryAuthenticator`, `TestRepositoryAuthenticatorPasswordHashVersion`, and `verifyRepoAuthenticator`.

Control flow, state, and persistence: tests create a repository environment, write user manifests inside write sessions, set passwords with different hash versions, and call the authenticator against valid and invalid credential combinations.

Dependencies and integration points: exercises `repo.WriteSession`, `user.SetUserProfile`, password hashing, and `AuthenticateRepositoryUsers`.

Risks and test signals: confirms hash-version compatibility and negative credential behavior. It does not test profile refresh timing, repository switching, or load-error cache retention.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/internal/auth/authn_repo_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/internal/auth/authn_test.go -->
## sources/sync-backup/kopia/internal/auth/authn_test.go

Purpose: tests single-user authentication and authenticator composition.

Important APIs/types/functions: `TestAuthentication`, `TestCombineAuthenticators_Empty`, `TestCombineAuthenticators`, and `verifyAuthenticator`.

Control flow, state, and persistence: constructs authenticators with hard-coded credentials and checks positive and negative combinations. No external state.

Dependencies and integration points: exercises `auth.Authenticator` through public constructors.

Risks and test signals: confirms empty composition returns nil and composed authenticators accept any configured credential set. Does not inspect timing characteristics.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/internal/auth/authn_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/internal/auth/authz.go -->
## sources/sync-backup/kopia/internal/auth/authz.go

Purpose: authorization interfaces plus legacy pre-ACL authorization rules.

Important APIs/types/functions: `Authorizer`, `AuthorizationInfo`, access-level aliases, `NoAccess`, `LegacyAuthorizer`, `legacyAuthorizationInfo`, and `ManifestAccessLevel`.

Control flow, state, and persistence: legacy authorization grants full content access, read access to global policy, read access to own host policy, and full access to manifests whose username/hostname labels match the authenticated `username@hostname`. No state is persisted in this file.

Dependencies and integration points: consumes manifest, snapshot, and policy labels; provides fallback behavior for `DefaultAuthorizer` when no ACLs exist.

Risks and test signals: risks include label-map omissions causing empty-string comparisons and full content access in legacy mode. Authz tests cover no-access and legacy/default behavior across policy/snapshot label combinations.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/internal/auth/authz.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/internal/auth/authz_acl.go -->
## sources/sync-backup/kopia/internal/auth/authz_acl.go

Purpose: ACL-backed authorizer with defaults and repository ACL caching.

Important APIs/types/functions: `ContentRule`, `DefaultACLs`, `DefaultAuthorizer`, `aclCache`, `aclEntriesAuthorizer`, `Authorize`, and `Refresh`.

Control flow, state, and persistence: `Authorize` parses `username@hostname`, refreshes cached ACL entries periodically via `acl.LoadEntries`, falls back to legacy rules when no ACLs exist, and returns an `AuthorizationInfo` that evaluates content and manifest access through ACL rules filtered for the user. ACL entries themselves persist as repository manifests.

Dependencies and integration points: integrates `acl` package, repository manifests, user/policy/snapshot label names, and `clock`.

Risks and test signals: the repository-change cache reset condition appears inverted (`if rep == ac.lastRep`) despite the comment saying reset when the server switches repositories; this may force unnecessary reloads for same repo and fail to clear cache for a new repo. Tests cover no-ACL fallback and default ACL equivalence, but not repository switching or refresh timing.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/internal/auth/authz_acl.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/internal/auth/authz_test.go -->
## sources/sync-backup/kopia/internal/auth/authz_test.go

Purpose: validates no-access, legacy authorization, and default ACL authorization behavior.

Important APIs/types/functions: label fixtures, `TestNoAccess`, `TestLegacyAuthorizer`, `TestDefaultAuthorizer_NoACLs`, `TestDefaultAuthorizer_DefaultACLs`, `verifyLegacyAuthorizer`, and `verifyManifestAccessLevel`.

Control flow, state, and persistence: tests create repository environments, optionally add `auth.DefaultACLs` as ACL manifests, authorize selected users, and assert content and manifest access for global policy, host policy, user/path policy, and snapshots.

Dependencies and integration points: exercises `auth`, `acl.AddACL`, and repository testing.

Risks and test signals: strong signal that default ACLs intentionally preserve legacy visible behavior. Does not test custom ACL entries, invalid usernames, or cache invalidation after repository changes.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/internal/auth/authz_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/internal/bigmap/bigmap_internal.go -->
## sources/sync-backup/kopia/internal/bigmap/bigmap_internal.go

Purpose: implements a memory-efficient append-only hash table for binary keys and optional values, with dense segment storage and mmap spillover.

Important APIs/types/functions: `Options`, `internalMap`, `entry`, `Contains`, `Get`, `PutIfAbsent`, `Close`, `newInternalMapWithOptions`, `growLocked`, `findSlot`, `newSegment`, and mmap helpers.

Control flow, state, and persistence: keys must be 4..255 bytes and are stored as `[keyLen][key][varint valueLen][value]` in append-only segments. Slots store segment/offset pointers and use double hashing with prime table sizes; growth rebuilds slots from segment contents. A fixed number of memory segments is kept before creating auto-delete mmap files. `Close` runs cleanup functions in reverse. State is in-memory/tempfile-backed and not durable.

Dependencies and integration points: backing implementation for `bigmap.Map` and `bigmap.Set`, uses `mmap-go`, temp files, and repository logging.

Risks and test signals: risks include panic-driven invalid input handling, table-size index overflow at extreme scale, mmap creation fallback reducing memory guarantees, and no deletion/iteration. Tests and benchmarks cover growth, mmap spillover with tiny options, panics, and map/set behavior.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/internal/bigmap/bigmap_internal.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/internal/bigmap/bigmap_internal_test.go -->
## sources/sync-backup/kopia/internal/bigmap/bigmap_internal_test.go

Purpose: tests and benchmarks the unexported internal hash table directly.

Important APIs/types/functions: `TestInternalMap`, `TestGrowingMap`, `TestGrowingSet`, `TestErrors`, `TestPanics`, `TestMapWithoutValue`, `sha256Key`, and internal/sync.Map benchmarks.

Control flow, state, and persistence: tests insert keys and values, force growth and segment rollover with small options, verify previous entries during insertion, and assert panics for invalid key lengths or values when disabled. Benchmarks compare internal map behavior against `sync.Map`.

Dependencies and integration points: uses test logging, SHA-256 key generation, and internal constructors.

Risks and test signals: strong coverage for append-only growth and no-value mode. It does not force mmap failure paths or extremely large table-size indexes.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/internal/bigmap/bigmap_internal_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/internal/bigmap/bigmap_map.go -->
## sources/sync-backup/kopia/internal/bigmap/bigmap_map.go

Purpose: exported encrypted value map built on `internalMap`.

Important APIs/types/functions: `Map`, `NewMap`, `NewMapWithOptions`, `PutIfAbsent`, `Get`, `Contains`, `Close`, and `decrypt`.

Control flow, state, and persistence: constructor creates a random AES-256 key and GCM AEAD. Non-empty values are encrypted with nonce bytes that contain an atomically incremented 64-bit counter and use the map key as associated data. The encrypted blob including nonce is stored in `internalMap`; empty values store nil. State is process-local and not durable.

Dependencies and integration points: used where a memory-efficient content/object ID map with confidential values is needed. Depends on `gather.WriteBuffer`, AES-GCM, and `internalMap`.

Risks and test signals: nonce is 12 bytes but only 8 are explicitly populated, leaving four zero bytes; uniqueness still follows the counter. Counter wrap panics. Decryption failure surfaces as an error. Tests cover growing encrypted maps and retrieval.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/internal/bigmap/bigmap_map.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/internal/bigmap/bigmap_map_test.go -->
## sources/sync-backup/kopia/internal/bigmap/bigmap_map_test.go

Purpose: external-package tests and benchmarks for exported `bigmap.Map`.

Important APIs/types/functions: `TestGrowingMap`, `BenchmarkMap_NoValue`, `BenchmarkMap_WithValue`, `benchmarkMap`, and local `sha256Key`.

Control flow, state, and persistence: inserts 20,000 SHA-256 keys with deterministic values using small segment/table options to force growth, validates contains/get during insertion, and benchmarks insertion plus repeated lookup.

Dependencies and integration points: uses only exported `bigmap` API, making it a good package-boundary test.

Risks and test signals: validates encryption/decryption under growth. Does not test tampered ciphertext or random-key initialization failures.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/internal/bigmap/bigmap_map_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/internal/bigmap/bigmap_set.go -->
## sources/sync-backup/kopia/internal/bigmap/bigmap_set.go

Purpose: exported set abstraction backed by `internalMap` without values.

Important APIs/types/functions: `Set`, `NewSet`, `NewSetWithOptions`, `Put`, `Contains`, and `Close`.

Control flow, state, and persistence: `Put` delegates to `inner.PutIfAbsent(ctx, key, nil)` and returns whether the key was newly added. No deletion or iteration is supported. State is in-memory/tempfile-backed through `internalMap`.

Dependencies and integration points: useful for large deduplication/member checks where keys are well-distributed binary IDs.

Risks and test signals: inherits key-length panics and append-only memory growth from `internalMap`. Tests cover duplicate insertion, growth, and panic conditions.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/internal/bigmap/bigmap_set.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/internal/bigmap/bigmap_set_test.go -->
## sources/sync-backup/kopia/internal/bigmap/bigmap_set_test.go

Purpose: external-package tests and benchmarks for exported `bigmap.Set`.

Important APIs/types/functions: `TestGrowingSet`, `BenchmarkSet`, and `TestSetPanics`.

Control flow, state, and persistence: inserts deterministic SHA-256 keys, verifies duplicate puts return false, checks previous and not-yet-inserted membership, benchmarks put/contains, and asserts invalid key lengths panic.

Dependencies and integration points: tests the public set API through test logging contexts.

Risks and test signals: confirms growth stability and input validation. Does not test close idempotence or mmap fallback behavior.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/internal/bigmap/bigmap_set_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/internal/bigmap/bigmapbench/main.go -->
## sources/sync-backup/kopia/internal/bigmap/bigmapbench/main.go

Purpose: standalone benchmark/profiling command for comparing `bigmap.Map` against `sync.Map` at very large insertion counts.

Important APIs/types/functions: flags `impl`, `profile-dir`, `profile-cpu`, `profile-memory`, `profile-memory-rate`; `main`; profiling helpers `maybeStartProfiling`, `startCPUProfiling`, and `dumpProfiles`.

Control flow, state, and persistence: generates 300 million SHA-256 keys without allocation, inserts into selected implementation, prints memory and throughput every million inserts, and optionally writes pprof files under the requested profile directory.

Dependencies and integration points: imports `internal/bigmap`, `runtime/pprof`, logging, and clock. It is a developer tool, not library runtime.

Risks and test signals: long-running and resource-intensive; ignores map creation errors in `main`, which is acceptable only for a benchmark utility. No automated tests; profile files are the output signal.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/internal/bigmap/bigmapbench/main.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/internal/blobcrypto/blob_crypto.go -->
## sources/sync-backup/kopia/internal/blobcrypto/blob_crypto.go

Purpose: whole-blob encryption/decryption utilities that derive blob IDs from hashes and encryption IVs from blob ID suffix bytes.

Important APIs/types/functions: `Crypter`, `Encrypt`, `Decrypt`, and `getIndexBlobIV`.

Control flow, state, and persistence: `Encrypt` hashes payload bytes, constructs `prefix + hex(hash) + optional "-" + suffix`, derives an AES-block-sized IV from the 32 hex characters before the first dash, resets output, and encrypts payload. `Decrypt` derives the same IV from the blob ID and lets the encryptor authenticate/decrypt. The blob ID and encrypted bytes are persisted by callers.

Dependencies and integration points: depends on repository hashing/encryption abstractions, `gather.Bytes`, and `repo/blob.ID`. Used by repository blob storage layers.

Risks and test signals: risks include invalid/short blob IDs, suffix parsing assumptions, and using blob ID-derived IVs that require stable hash naming. Tests cover round trips, ID mismatch failures, invalid IDs, and encryptor failures.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/internal/blobcrypto/blob_crypto.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/internal/blobcrypto/blob_crypto_test.go -->
## sources/sync-backup/kopia/internal/blobcrypto/blob_crypto_test.go

Purpose: verifies blob crypto naming, encryption/decryption round trips, and failure paths.

Important APIs/types/functions: `TestBlobCrypto`, `badEncryptor`, and `TestBlobCrypto_Invalid`.

Control flow, state, and persistence: tests create a `StaticCrypter` from default format hashing/encryption, encrypt different payloads with prefix/suffix, decrypt with matching IDs, assert mismatched IDs and invalid payloads fail, and simulate bad hash/encryptor behavior.

Dependencies and integration points: exercises hashing, encryption, format configuration, and `gather.WriteBuffer`.

Risks and test signals: strong correctness signal for ID-derived IV behavior. Does not cover all encryption algorithms, but uses defaults representative of repository format.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/internal/blobcrypto/blob_crypto_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/internal/blobcrypto/static_crypter.go -->
## sources/sync-backup/kopia/internal/blobcrypto/static_crypter.go

Purpose: simple `Crypter` implementation holding fixed hashing and encryption functions.

Important APIs/types/functions: `StaticCrypter`, `Encryptor`, and `HashFunc`.

Control flow, state, and persistence: methods return the struct fields without mutation. The type has no lifecycle or persistence.

Dependencies and integration points: useful in tests and format-derived crypto setup, because it adapts `hashing.HashFunc` and `encryption.Encryptor` to the `Crypter` interface.

Risks and test signals: nil fields are not guarded; callers must construct it correctly. Blob crypto tests exercise it with valid and deliberately bad components.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/internal/blobcrypto/static_crypter.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/internal/blobparam/blobid_params.go -->
## sources/sync-backup/kopia/internal/blobparam/blobid_params.go

Purpose: structured logging parameter helpers for blob IDs and metadata.

Important APIs/types/functions: `BlobMetadataList`, `BlobID`, `BlobIDList`, `BlobMetadata`, and the corresponding `WriteValueTo` implementations.

Control flow, state, and persistence: each helper stores a field key and value/list; `WriteValueTo` emits JSON fields or lists through `contentlog.JSONWriter`. Metadata emits `blobID`, `l`, and `ts` fields.

Dependencies and integration points: integrates repository blob metadata with Kopia content logging infrastructure.

Risks and test signals: risks include field-name drift or inconsistent abbreviations (`l` for length). No direct tests in this subset; correctness depends on log consumers and JSON writer behavior.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/internal/blobparam/blobid_params.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/internal/blobtesting/asserts.go -->
## sources/sync-backup/kopia/internal/blobtesting/asserts.go

Purpose: reusable assertions for blob storage provider tests.

Important APIs/types/functions: `AssertTimestampsCloseEnough`, `AssertGetBlob`, `AssertInvalidOffsetLength`, `AssertGetBlobNotFound`, `AssertInvalidCredentials`, `AssertGetMetadataNotFound`, `AssertListResults`, and `AssertListResultsIDs`.

Control flow, state, and persistence: helpers read blobs in full, zero-length, split-range, and invalid-range modes; verify not-found/credential errors; compare list and metadata results; and sort IDs for deterministic comparison. No persistence besides storage operations.

Dependencies and integration points: used by provider validation and in-memory storage tests. Depends on `gather.WriteBuffer`, `blob.Storage`, and test assertions.

Risks and test signals: timestamp tolerance is one minute to accommodate provider precision. `AssertGetBlob` assumes split reads are supported for blobs with length >=2. These helpers define expected storage contract behavior.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/internal/blobtesting/asserts.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/internal/blobtesting/cleanup.go -->
## sources/sync-backup/kopia/internal/blobtesting/cleanup.go

Purpose: test helper for deleting old blobs from a storage backend.

Important APIs/types/functions: `MinCleanupAge` and `CleanupOldData`.

Control flow, state, and persistence: lists all blobs, compares timestamps against `clock.Now()`, enqueues deletes for old blobs in a `parallelwork.Queue`, and processes with concurrency 16. It intentionally ignores list errors but asserts delete queue processing succeeds.

Dependencies and integration points: used in storage integration tests to clean test data.

Risks and test signals: risk of deleting real data if pointed at a non-test storage/prefix, since it lists with empty prefix. No direct tests in this subset; callers must isolate test buckets/prefixes.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/internal/blobtesting/cleanup.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/internal/blobtesting/concurrent.go -->
## sources/sync-backup/kopia/internal/blobtesting/concurrent.go

Purpose: stress helper for concurrent blob storage access.

Important APIs/types/functions: `ConcurrentAccessOptions` and `VerifyConcurrentAccess`.

Control flow, state, and persistence: generates a pool of random blob IDs, then runs getters, putters, deleters, and listers under an errgroup. Getters accept either valid data with the blob ID prefix or clean not-found errors; deleters accept success or not-found; listers expect no unexpected errors.

Dependencies and integration points: used in provider validation to catch data races and inconsistent error handling. Depends on `blob.Storage`, random data, and `gather.WriteBuffer`.

Risks and test signals: uses package-level `math/rand` concurrently, which may itself be a race concern depending on Go version/API usage. The helper is probabilistic and catches only clean-error contract violations, not strict linearizability.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/internal/blobtesting/concurrent.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/internal/blobtesting/doc.go -->
## sources/sync-backup/kopia/internal/blobtesting/doc.go

Purpose: package documentation for blob storage testing helpers.

Important APIs/types/functions: no runtime symbols.

Control flow, state, and persistence: none.

Dependencies and integration points: Go documentation anchor for helper package used by storage provider tests.

Risks and test signals: no direct risk; accuracy depends on package contents remaining testing-focused.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/internal/blobtesting/doc.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/internal/blobtesting/eventually_consistent.go -->
## sources/sync-backup/kopia/internal/blobtesting/eventually_consistent.go

Purpose: wraps a blob storage backend to simulate eventual consistency effects common in cloud object stores.

Important APIs/types/functions: `NewEventuallyConsistentStorage`, `eventuallyConsistentStorage`, `ecFrontendCache`, `GetBlob`, `GetMetadata`, `PutBlob`, `DeleteBlob`, `ListBlobs`, and `shouldApplyInconsistency`.

Control flow, state, and persistence: four frontend caches randomly serve stale hits or stale not-found states for full reads. Deletes record recently deleted metadata, and listing probabilistically hides new blobs or resurrects deleted ones until `listSettleTime` elapses. Underlying storage remains the durable source; wrapper caches expire after five seconds.

Dependencies and integration points: used to test repository/provider behavior under eventual consistency. Delegates capacity, close, connection info, display, flush, and retention extension to the real storage.

Risks and test signals: probabilistic behavior can make tests flaky if assumptions are too strict. Uses `math/rand` and custom time source. No direct tests here, but provider validation can use it to exercise consistency tolerance.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/internal/blobtesting/eventually_consistent.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/internal/blobtesting/faulty.go -->
## sources/sync-backup/kopia/internal/blobtesting/faulty.go

Purpose: fault-injection wrapper for `blob.Storage`.

Important APIs/types/functions: method constants, `FaultyStorage`, `NewFaultyStorage`, and wrapped storage methods.

Control flow, state, and persistence: before each supported operation, `GetNextFault` is consulted with method-specific arguments; if a fault is active, the injected error is returned, otherwise the call delegates to the base storage. List item faults can fire inside the callback path.

Dependencies and integration points: used heavily by cache and provider tests to simulate backend/cache failures. Depends on `internal/fault`.

Risks and test signals: retention extension is not fault-injected. Injected faults can alter concurrency timing in tests. Cache tests use it to validate write/read/open failure handling.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/internal/blobtesting/faulty.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/internal/blobtesting/map.go -->
## sources/sync-backup/kopia/internal/blobtesting/map.go

Purpose: in-memory `blob.Storage` implementation for tests, with optional capacity limit and timestamp control.

Important APIs/types/functions: `DataMap`, `NewMapStorage`, `NewMapStorageWithLimit`, `mapStorage`, and methods `GetBlob`, `GetMetadata`, `PutBlob`, `DeleteBlob`, `ListBlobs`, `TouchBlob`, and `GetCapacity`.

Control flow, state, and persistence: data and timestamps live in maps protected by an RW mutex. `PutBlob` rejects retention and do-not-recreate options, enforces optional byte limit, updates total bytes accounting, and supports set/get mod time. Listing snapshots matching keys, sorts them, then fetches metadata per key.

Dependencies and integration points: primary fake storage for cache, blobtesting verification, and many repository tests.

Risks and test signals: `DeleteBlob` is a no-op for missing IDs, matching tolerant storage behavior. `data.WriteTo` errors are ignored. Tests cover storage contract and capacity accounting.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/internal/blobtesting/map.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/internal/blobtesting/map_test.go -->
## sources/sync-backup/kopia/internal/blobtesting/map_test.go

Purpose: validates map-backed test storage and capacity limiting.

Important APIs/types/functions: `TestMapStorage`, `TestMapStorageWithLimit`, and `verifyCapacityAndFreeSpace`.

Control flow, state, and persistence: runs the generic `VerifyStorage` contract against map storage, then tests limited storage by adding/deleting blobs and asserting free-space accounting and limit errors.

Dependencies and integration points: uses `blobtesting.VerifyStorage`, `gather.FromSlice`, and blob capacity API.

Risks and test signals: confirms test storage behaves like a provider enough for generic tests. Does not test unsupported option errors directly.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/internal/blobtesting/map_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/internal/blobtesting/object_locking_map.go -->
## sources/sync-backup/kopia/internal/blobtesting/object_locking_map.go

Purpose: in-memory versioned object-locking storage for testing retention and delete-marker behavior.

Important APIs/types/functions: `ErrBlobLocked`, `RetentionStorage`, `NewVersionedMapStorage`, `objectLockingMap`, `GetBlob`, `GetMetadata`, `GetRetention`, `PutBlob`, `DeleteBlob`, `ExtendBlobRetention`, `ListBlobs`, and `TouchBlob`.

Control flow, state, and persistence: each put appends a new version entry with value, mtime, and optional retention parameters. Deletes append a delete marker unless already absent/deleted. Reads and lists use only the latest non-delete-marker version. Touch respects retention and returns `ErrBlobLocked` while locked. All state is in-memory behind an RW mutex.

Dependencies and integration points: simulates S3-style object locking for provider tests and generic storage verification with retention options.

Risks and test signals: `DeleteBlob` does not check retention before adding a delete marker, so it may not fully mimic locked-object deletion rules. Tests run generic storage verification with governance retention but do not deeply assert version histories.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/internal/blobtesting/object_locking_map.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/internal/blobtesting/object_locking_map_test.go -->
## sources/sync-backup/kopia/internal/blobtesting/object_locking_map_test.go

Purpose: smoke test for versioned object-locking map storage.

Important APIs/types/functions: `TestObjectLockingStorage`.

Control flow, state, and persistence: constructs `NewVersionedMapStorage` and runs the generic storage verifier with governance retention options.

Dependencies and integration points: validates the object-locking fake through the same contract as other blob storages.

Risks and test signals: broad smoke coverage only; retention-specific edge cases such as locked delete/touch semantics need targeted tests elsewhere.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/internal/blobtesting/object_locking_map_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/internal/blobtesting/storage.go -->
## sources/sync-backup/kopia/internal/blobtesting/storage.go

Purpose: declares a test-only retention-capable storage interface.

Important APIs/types/functions: `RetentionStorage`.

Control flow, state, and persistence: no implementation; interface embeds `blob.Storage` and adds `TouchBlob` plus `GetRetention`.

Dependencies and integration points: implemented by `objectLockingMap`; used by tests needing retention inspection and mutation simulation.

Risks and test signals: interface shape must track provider capabilities used in object-lock tests. No direct tests needed beyond implementer checks.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/internal/blobtesting/storage.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/internal/blobtesting/verify.go -->
## sources/sync-backup/kopia/internal/blobtesting/verify.go

Purpose: generic blob storage contract verifier and validation option defaults.

Important APIs/types/functions: `VerifyStorage`, `AssertConnectionInfoRoundTrips`, and `TestValidationOptions`.

Control flow, state, and persistence: verifier asserts initial not-found behavior, tolerant delete of missing blobs, concurrent initial puts, full/range reads, list behavior and callback errors, overwrite behavior subject to options, retention extension behavior, deletes/list after deletes, and set/get modification time handling. It mutates the target storage heavily.

Dependencies and integration points: central test suite used by in-memory and real provider tests. Uses `blob`, `gather`, and provider validation defaults.

Risks and test signals: destructive to the target storage namespace, so callers must use isolated test storage. It conditionally treats unsupported set-time as skip and adjusts add concurrency in CI. It encodes the expected provider behavior for many repository components.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/internal/blobtesting/verify.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/internal/cache/cache_metrics.go -->
## sources/sync-backup/kopia/internal/cache/cache_metrics.go

Purpose: defines metrics counters for content cache hits, misses, malformed data, and errors.

Important APIs/types/functions: `metricsStruct`, `initMetricsStruct`, and report helpers for miss errors, miss bytes, hit bytes, malformed data, and store errors.

Control flow, state, and persistence: initializes counters in a registry with a `cache` label. Report helpers increment counts/bytes; metric values persist only in the metrics registry.

Dependencies and integration points: used by persistent/content cache internals to expose operational visibility.

Risks and test signals: typo-level risk in metric descriptions, and nil registry handling depends on `metrics.Registry` behavior. No direct tests in this subset.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/internal/cache/cache_metrics.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/internal/cache/cache_storage.go -->
## sources/sync-backup/kopia/internal/cache/cache_storage.go

Purpose: creates a filesystem-backed storage for cache contents and defines the reduced storage interface required by caches.

Important APIs/types/functions: `Storage`, `DirMode`, `NewStorageOrNil`, `filesystemImplWrapper`, and testable `mkdirAll`.

Control flow, state, and persistence: returns nil when cache size or base directory disables caching; rejects relative cache paths; ensures the cache subdirectory exists; opens a sharded filesystem blob storage using `context.WithoutCancel`; wraps it to expose only cache storage methods. Persistent state is the on-disk cache directory.

Dependencies and integration points: integrates `repo/blob/filesystem` and `sharded` storage with content cache. Touch support is required by persistent cache expiration.

Risks and test signals: type assertion assumes filesystem storage implements `cache.Storage`. Directory creation and initialization errors are wrapped. Tests cover disabled caching, relative paths, and mkdir failure.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/internal/cache/cache_storage.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/internal/cache/cache_storage_test.go -->
## sources/sync-backup/kopia/internal/cache/cache_storage_test.go

Purpose: tests cache storage creation edge cases.

Important APIs/types/functions: `TestNewStorageOrNil`.

Control flow, state, and persistence: calls `NewStorageOrNil` with disabled cache settings, a relative path, and an injected `mkdirAll` failure. It restores the package variable after the test.

Dependencies and integration points: uses temporary directories and test logging.

Risks and test signals: covers the main guardrails around cache directory setup. Does not validate successful filesystem storage behavior beyond construction in other content cache tests.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/internal/cache/cache_storage_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/internal/cache/content_cache.go -->
## sources/sync-backup/kopia/internal/cache/content_cache.go

Purpose: implements content caching for pack blob ranges, either by individual content IDs or by whole blobs.

Important APIs/types/functions: `ContentCache`, `Options`, `NewContentCache`, `ContentIDCacheKey`, `BlobIDCacheKey`, `contentCacheImpl`, `GetContent`, `PrefetchBlob`, and `CacheStorage`.

Control flow, state, and persistence: content IDs and blob IDs are key-mangled to spread sharded cache paths. In full-blob mode, `GetContent` locks by blob, checks cached full blob ranges, fetches and stores the full blob on miss, then slices output. In partial mode, it shared-locks the blob to avoid racing with prefetch, checks full blob cache, exclusive-locks the content ID, checks content cache, fetches the requested range, and stores it. Persistent state lives in `PersistentCache` over cache storage.

Dependencies and integration points: depends on underlying `blob.Storage`, persistent cache, HMAC protection, metrics, gather buffers, and `mutexMap` locking.

Risks and test signals: risks include incorrect range handling for `length=-1`, lock-key collisions with content/blob IDs, and stale cache after underlying blob mutation. Tests cover data/metadata modes, prefetch races, corruption recovery, cache failures, expiration, and passthrough.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/internal/cache/content_cache.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/internal/cache/content_cache_concurrency_test.go -->
## sources/sync-backup/kopia/internal/cache/content_cache_concurrency_test.go

Purpose: stress tests content cache locking and fetch coalescing.

Important APIs/types/functions: cache constructors for data/metadata modes, prefetch/concurrency tests, `concurrencyTester`.

Control flow, state, and persistence: tests use `FaultyStorage` delays/fault hooks to observe when underlying `GetBlob` runs, then run concurrent `GetContent`/`PrefetchBlob` calls. They assert same-content races fetch once, different content IDs or blobs can fetch in parallel, and prefetch blocks content reads until full-blob caching is complete.

Dependencies and integration points: exercises `ContentCache`, `mutexMap`, `FaultyStorage`, and map-backed cache storage.

Risks and test signals: strong concurrency signal for avoiding duplicate fetches and over-serialization. Some goroutines ignore returned errors, so failures can manifest through counters/fault hooks rather than direct assertions.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/internal/cache/content_cache_concurrency_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/internal/cache/content_cache_data_test.go -->
## sources/sync-backup/kopia/internal/cache/content_cache_data_test.go

Purpose: tests content-ID based data cache mode and passthrough fallback.

Important APIs/types/functions: `TestContentCacheForData` and `TestContentCacheForData_Passthrough`.

Control flow, state, and persistence: uses map-backed underlying storage and cache storage, fetches missing and present ranges, verifies cache key mangling and entry counts, closes the cache, tests a later miss, and validates prefetched full blob use after deleting underlying data.

Dependencies and integration points: validates `NewContentCache`, `ContentIDCacheKey`, `BlobIDCacheKey`, `PrefetchBlob`, and passthrough mode when no cache storage is configured.

Risks and test signals: confirms partial range caching and full-blob prefetch interplay. Does not test HMAC secret changes between cache instances.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/internal/cache/content_cache_data_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/internal/cache/content_cache_metadata_test.go -->
## sources/sync-backup/kopia/internal/cache/content_cache_metadata_test.go

Purpose: tests full-blob metadata cache mode.

Important APIs/types/functions: `TestContentCacheForMetadata` and `TestContentCacheForMetadata_Passthrough`.

Control flow, state, and persistence: creates a disk-backed cache storage through `BaseCacheDirectory`, fetches a whole blob and ranges, lists cache entries to confirm only one full-blob item is stored, closes the cache, and verifies passthrough behavior when base directory is empty.

Dependencies and integration points: exercises filesystem cache storage, `FetchFullBlobs`, and range extraction from cached full blobs.

Risks and test signals: validates whole-blob caching behavior but does not test invalid range handling in metadata mode directly beyond shared content cache tests.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/internal/cache/content_cache_metadata_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/internal/cache/content_cache_passthrough.go -->
## sources/sync-backup/kopia/internal/cache/content_cache_passthrough.go

Purpose: no-cache implementation of `ContentCache` used when caching is disabled.

Important APIs/types/functions: `passthroughContentCache`, `GetContent`, `PrefetchBlob`, `Sync`, `CacheStorage`, and `Close`.

Control flow, state, and persistence: `GetContent` ignores content ID and delegates directly to underlying storage `GetBlob`; prefetch/sync/close are no-ops; cache storage is nil. No cache state is persisted.

Dependencies and integration points: returned by `NewContentCache` when no base cache directory or explicit storage is configured.

Risks and test signals: includes a `Sync` method not present in `ContentCache`, likely for compatibility with broader cache interfaces. Tests cover passthrough reads for data and metadata configurations.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/internal/cache/content_cache_passthrough.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/internal/cache/content_cache_test.go -->
## sources/sync-backup/kopia/internal/cache/content_cache_test.go

Purpose: broader content cache tests for expiration, disk cache behavior, corruption recovery, and cache failure tolerance.

Important APIs/types/functions: `newUnderlyingStorageForContentCacheTesting`, `verifyCacheExpiration`, `TestDiskContentCache`, `verifyContentCache`, failure tests, `verifyStorageContentList`, and `withoutTouchBlob`.

Control flow, state, and persistence: tests populate cache entries, manipulate fake time, delete underlying blobs to infer eviction, create disk cache storage, read ranges, corrupt cached protected bytes and expect refetch, inject cache open/write/read failures, and assert reads still succeed from underlying storage when cache operations fail.

Dependencies and integration points: exercises content cache, persistent cache sweeping, protected cache encoding, map and faulty storages, and filesystem cache creation.

Risks and test signals: strong operational signal for resilience and eviction policy. It relies on fake time to avoid platform clock granularity issues. Some behavior depends on persistent cache internals not listed in this subset.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/internal/cache/content_cache_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/internal/cache/export_test.go -->
## sources/sync-backup/kopia/internal/cache/export_test.go

Purpose: exposes an internal persistent cache method for tests.

Important APIs/types/functions: `PersistentCache.TestingGetFull`.

Control flow, state, and persistence: delegates to unexported `getFull`, writing cached content into a `gather.WriteBuffer` and returning whether the key was found.

Dependencies and integration points: enables external test packages to inspect full-cache content without broadening production API.

Risks and test signals: compiled only in tests. Keep narrow to avoid hiding production API needs.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/internal/cache/export_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/internal/cache/mutex_map.go -->
## sources/sync-backup/kopia/internal/cache/mutex_map.go

Purpose: keyed `sync.RWMutex` registry for per-content or per-blob cache locking.

Important APIs/types/functions: `mutexMap`, `mutexMapEntry`, `exclusiveLock`, `tryExclusiveLock`, `exclusiveUnlock`, `sharedLock`, `trySharedLock`, `sharedUnlock`, `getMutexAndAddRef`, and `getMutexAndReleaseRef`.

Control flow, state, and persistence: locks create or reuse a keyed RW mutex and increment a ref count under a global mutex. Unlock paths decrement the ref count and delete the entry at zero before unlocking the keyed mutex. Try-lock failures release the reference immediately. State is in-memory only.

Dependencies and integration points: used by persistent/content cache code to coalesce same-key fetches while allowing unrelated keys to proceed.

Risks and test signals: unlock-before-keyed-unlock deletion means a new mutex for the same key can be created while the old one is still locked/unlocking, but only after ref count reaches zero. Calling unlock without a matching lock can panic or nil-deref. Tests cover exclusive/shared locking and ref cleanup.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/internal/cache/mutex_map.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/internal/cache/mutex_map_test.go -->
## sources/sync-backup/kopia/internal/cache/mutex_map_test.go

Purpose: unit tests for keyed mutex reference tracking and lock compatibility.

Important APIs/types/functions: `TestMutexMap_ExclusiveLock` and `TestMutexMap_SharedLock`.

Control flow, state, and persistence: tests acquire exclusive and shared locks, attempt incompatible try-locks, release locks, and assert entry-map sizes shrink as ref counts reach zero.

Dependencies and integration points: package-internal tests directly inspect `mutexMap.entries`.

Risks and test signals: confirms basic lock semantics and cleanup. Does not test high-concurrency races or misuse unlock paths.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/internal/cache/mutex_map_test.go -->
