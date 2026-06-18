# subset-b-009151 research

Grouped research for Kopia snapshot policy, restore, snapshotfs, snapshot GC, snapshot maintenance, snapshot source/stat helpers, and upload checkpoint/estimate files. Each source file section preserves the original source path in its title and is delimited for deterministic splitting into source-tree-aligned per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/snapshot/policy/policy_merge_test.go -->
# sources/sync-backup/kopia/snapshot/policy/policy_merge_test.go

Purpose: reflective regression coverage for Kopia snapshot policy definition and inheritance merge behavior. It ensures every `policy.Policy` field has a matching `policy.Definition` provenance field unless explicitly omitted, and that `MergePolicies` chooses child, parent, and default values correctly.

Important APIs/types/functions: `TestPolicyDefinition`, `ensureTypesMatch`, `TestPolicyMerge`, `testPolicyMergeSingleField`, `policyWithField`, `disableParentMerging`, plus focused tests for `CompressionPolicy.OnlyCompress` and `SchedulingPolicy.TimesOfDay`. The tests use `reflect.TypeFor`, `snapshot.SourceInfo`, `policy.DefaultPolicy`, and `policy.MergePolicies`.

Control flow: generic reflection cases synthesize policies with zero, parent, and child values, then compare stringified merged policies. Special tests leave parent merging enabled to validate append, sort, dedupe, and `NoParent` cutoffs.

State and persistence: no repository state is written; the observable state is merged in-memory policy plus definition metadata.

Dependencies and integration points: covers all policy substructs, optional scalar wrappers, compression names, action commands, OS snapshot modes, and labels used to derive targets.

Risks and test signals: reflection only handles known field types, so adding a policy field requires updating this test. Signals are exact `String()` equality and definition JSON tag parity.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/snapshot/policy/policy_merge_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/snapshot/policy/policy_tree.go -->
# sources/sync-backup/kopia/snapshot/policy/policy_tree.go

Purpose: builds and queries an inherited policy tree keyed by relative source paths. It provides the default policy values used when no explicit policy exists and exposes tree nodes that distinguish explicitly defined policy from inherited policy.

Important APIs/types/functions: global `DefaultPolicy`, `DefaultDefinition`, `Tree`, `DefinedPolicy`, `EffectivePolicy`, `IsInherited`, `Child`, `BuildTree`, `buildTreeNode`, and `childrenWithPrefix`. Defaults include files, compression, metadata compression, error handling, logging, retention, scheduling, OS snapshot, and upload policy defaults.

Control flow: `BuildTree` starts at `"."`, chooses the defined policy for that path or the passed default, then recursively groups descendants by the next path element. `Child` walks slash-separated names, treats `""` and `"."` as the current node, returns explicit children when present, and synthesizes inherited nodes otherwise.

State and persistence: state is an in-memory immutable-ish tree after construction; nil trees are valid and map to `DefaultPolicy`.

Dependencies and integration points: used by upload, estimate, scheduling, and policy lookup code to carry source-specific policy down filesystem traversal.

Risks and test signals: path normalization is caller-sensitive; paths are expected to be relative and dot-rooted. Tests assert inherited flags and effective policies across missing, nested, and dot path segments.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/snapshot/policy/policy_tree.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/snapshot/policy/policy_tree_test.go -->
# sources/sync-backup/kopia/snapshot/policy/policy_tree_test.go

Purpose: unit tests for policy tree child lookup and construction from dot-rooted policy maps.

Important APIs/types/functions: package-level sample policies `defPolicy`, `policyA`, `policyB`, `policyC`, `TestTreeChild`, `TestBuildTree`, `verifyTreePolicy`, and `dumpTree`.

Control flow: `TestTreeChild` manually constructs a tree and checks nil tree fallback, direct children, missing siblings, and inherited descendants. `TestBuildTree` uses `BuildTree` with policies at `.`, `./foo`, and `./bar/baz/bleh`, then queries paths containing empty and `"."` segments.

State and persistence: all state is in-memory `Tree` and `Policy` values. The test intentionally compares pointers/deep equality rather than stored repository policies.

Dependencies and integration points: validates behavior required by policy-aware filesystem traversal where `Tree.Child(name)` is called for every path element.

Risks and test signals: `dumpTree` prints to stdout and is diagnostic noise, but not behavioral. Signals are exact effective policy and `IsInherited` values for each path case.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/snapshot/policy/policy_tree_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/snapshot/policy/retention_policy.go -->
# sources/sync-backup/kopia/snapshot/policy/retention_policy.go

Purpose: defines snapshot retention policy fields and computes why individual snapshot manifests should be retained. It also compacts retention and pin reason lists for display.

Important APIs/types/functions: `RetentionPolicy`, `RetentionPolicyDefinition`, `ComputeRetentionReasons`, `EffectiveKeepLatest`, `getRetentionReasons`, `CompactRetentionReasons`, `CompactPins`, and `SortRetentionTags`. Defaults are 10 latest, 48 hourly, 7 daily, 4 weekly, 24 monthly, 3 annual, and no identical-snapshot ignoring.

Control flow: computation finds max complete and overall start times, builds cutoffs, sorts manifests newest-first, assigns reasons to complete snapshots by unique latest/time buckets, then keeps recent or minimum-count incomplete snapshots with `"incomplete"`.

State and persistence: mutates each `snapshot.Manifest.RetentionReasons`; it does not save manifests. Merge records definition source for each optional field.

Dependencies and integration points: depends on `snapshot.SortByTime`, `fs.UTCTimestamp`, optional policy wrappers, and retention consumers that expire or display snapshots.

Risks and test signals: retention uses the latest complete snapshot as the anchor, so all-incomplete or clock-skewed sets need care. RLE compaction assumes numeric suffixes after the last dash. Tests cover latest, hourly/daily/monthly/weekly, incomplete, pins, and compaction.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/snapshot/policy/retention_policy.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/snapshot/policy/retention_policy_test.go -->
# sources/sync-backup/kopia/snapshot/policy/retention_policy_test.go

Purpose: table-driven coverage for retention reason assignment and compact display helpers.

Important APIs/types/functions: `TestRetentionPolicyTest`, `TestCompactPins`, and `TestCompactRetentionReasons`. The tests create `snapshot.Manifest` instances with RFC3339 timestamps, optional `IncompleteReason`, and expected retention tags.

Control flow: each retention case builds a full manifest set and a filtered retained-only set, calls `ComputeRetentionReasons` on both, and compares the resulting tags with `cmp.Diff`. Helper tests verify pin dedupe/sort and RLE-style reason compaction.

State and persistence: no repository state is used; the tests mutate manifest slices in memory. `Description` stores the original timestamp key to map results back to expectations.

Dependencies and integration points: exercises the same `RetentionPolicy` behavior consumed by snapshot expiration and UI output.

Risks and test signals: expectations encode exact cutoff semantics around missing months, week numbers, and incomplete minimum count. Failures show as tag diffs for specific timestamps.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/snapshot/policy/retention_policy_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/snapshot/policy/scheduling_policy.go -->
# sources/sync-backup/kopia/snapshot/policy/scheduling_policy.go

Purpose: defines automatic snapshot scheduling policy, including fixed intervals, local times of day, cron expressions, missed-run handling, and manual-only snapshots.

Important APIs/types/functions: `TimeOfDay.Parse`, `TimeOfDay.String`, `SortAndDedupeTimesOfDay`, `SchedulingPolicy`, `Interval`, `SetInterval`, `NextSnapshotTime`, `getNextTimeOfDaySnapshot`, `getNextCronSnapshot`, `checkMissedSnapshot`, `Merge`, `IsManualSnapshot`, `SetManual`, `ValidateSchedulingPolicy`, and `stripCronComment`.

Control flow: `NextSnapshotTime` exits for manual policies, computes interval, time-of-day, and cron candidates in local time, chooses the earliest, then may return `now` when `RunMissed` is enabled and the next regular run is more than 30 minutes away. Merge appends parent times unless `NoParentTimesOfDay` blocks it.

State and persistence: `SetManual` loads or creates a defined repository policy for a source and saves `Manual=true`; other scheduling operations are in-memory.

Dependencies and integration points: uses `hashicorp/cronexpr`, repository policy APIs, `snapshot.SourceInfo`, and policy tree consumers.

Risks and test signals: invalid cron is ignored during scheduling but rejected by validation; manual cannot combine with other fields. Tests cover intervals, cron, time-of-day, missed runs, and dedupe.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/snapshot/policy/scheduling_policy.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/snapshot/policy/scheduling_policy_test.go -->
# sources/sync-backup/kopia/snapshot/policy/scheduling_policy_test.go

Purpose: validates snapshot scheduling edge cases and time-of-day normalization.

Important APIs/types/functions: `TestNextSnapshotTime` and `TestSortAndDedupeTimesOfDay`. The schedule cases exercise `SchedulingPolicy.NextSnapshotTime` with interval seconds, time-of-day slices, cron strings, `RunMissed`, and `Manual`.

Control flow: each table row supplies `now`, `previousSnapshotTime`, policy, expected next time, and expected availability. Cases cover overdue intervals, future previous snapshots, mixed interval and time-of-day priority, tomorrow rollover, cron month/day rules, and missed-run immediate execution.

State and persistence: no persistent policy writes; all times use `time.Local` and fixed dates.

Dependencies and integration points: indirectly validates `cronexpr` interpretation and the scheduler behavior used by automatic snapshot runners.

Risks and test signals: time-zone dependence is constrained by constructing expected values in `time.Local`. Missing validation tests mean cron parsing errors and manual-combination validation are covered elsewhere or by callers. Signals are exact `time.Time` equality and boolean availability.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/snapshot/policy/scheduling_policy_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/snapshot/policy/splitter_policy.go -->
# sources/sync-backup/kopia/snapshot/policy/splitter_policy.go

Purpose: defines the content splitter algorithm policy used while uploading files.

Important APIs/types/functions: `SplitterPolicy`, `SplitterPolicyDefinition`, `SplitterForFile`, and `Merge`. The only policy field is `Algorithm`, with provenance stored in `SplitterPolicyDefinition.Algorithm`.

Control flow: `SplitterForFile` currently ignores the `fs.Entry` and returns the configured algorithm directly. `Merge` uses the shared `mergeString` helper to fill an unset child value from a source policy and record the defining `snapshot.SourceInfo`.

State and persistence: no persistence in this file; values become persistent only as part of broader policy serialization.

Dependencies and integration points: used by upload/chunker selection through policy evaluation and the `fs.Entry` interface, leaving room for future per-file algorithm decisions.

Risks and test signals: the entry parameter is unused, so any intended file-sensitive splitter selection would require new logic. Reflection-based policy merge tests cover field presence and merge behavior.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/snapshot/policy/splitter_policy.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/snapshot/policy/upload_policy.go -->
# sources/sync-backup/kopia/snapshot/policy/upload_policy.go

Purpose: defines upload concurrency and large-file parallelization policy.

Important APIs/types/functions: `UploadPolicy`, `UploadPolicyDefinition`, `Merge`, and `ValidateUploadPolicy`. Fields are optional max parallel snapshots, optional max parallel file reads, and optional size threshold for parallel upload.

Control flow: merge fills optional ints/int64s from a source policy and records source provenance. Validation rejects `MaxParallelSnapshots` on path-specific source policies because that limit is only valid globally, per user-host, or per host.

State and persistence: in-memory policy values are serialized by the wider policy subsystem. Defaults are defined in `policy_tree.go` as one parallel snapshot, CPU-based reads when nil, and 2 GiB parallel-upload threshold.

Dependencies and integration points: consumed by uploader scheduling and policy manager validation, with `snapshot.SourceInfo.Path` determining scope legality.

Risks and test signals: validation is narrow and does not bound numeric values here; callers or UI must avoid nonsensical optional values. Generic policy merge tests cover merge/provenance shape.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/snapshot/policy/upload_policy.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/snapshot/restore/local_fs_output.go -->
# sources/sync-backup/kopia/snapshot/restore/local_fs_output.go

Purpose: implements `restore.Output` for writing a snapshot tree to the local filesystem with overwrite, ownership, permissions, timestamp, sparse, atomic, flush, and shallow-placeholder cleanup options.

Important APIs/types/functions: `FilesystemOutput`, `Init`, `BeginDirectory`, `FinishDirectory`, `WriteFile`, `FileExists`, `CreateSymlink`, `SymlinkExists`, `setAttributes`, `createDirectory`, `copyFileContent`, `write`, `getStreamCopier`, and `progressReportingReader`.

Control flow: initialization chooses sparse or regular copy. Directories are created before traversal and attributed after children. Files are opened from the snapshot, copied to a safe long filename, optionally via `atomicfile.Write`, then attributed. Symlinks are overwritten only when allowed and use OS-specific lchown/chmod/chtimes helpers.

State and persistence: writes real files, directories, symlinks, permissions, owners, mtimes, and optionally fsyncs file data. It removes shallow placeholder sidecars after writing real entries.

Dependencies and integration points: used by `restore.Entry`; depends on `localfs`, `atomicfile`, `ospath`, `sparsefile`, `stat`, and platform symlink helpers.

Risks and test signals: overwrite and delete-extra behavior can remove local data when enabled. Atomic writes do not use sparse copy. Permission failures may be ignored by option. Existing-file skip uses size and mtime tolerance.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/snapshot/restore/local_fs_output.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/snapshot/restore/local_fs_output_darwin.go -->
# sources/sync-backup/kopia/snapshot/restore/local_fs_output_darwin.go

Purpose: Darwin-specific symlink attribute helpers for local filesystem restore.

Important APIs/types/functions: `symlinkChown`, `symlinkChmod`, and `symlinkChtimes`.

Control flow: owner changes use `unix.Lchown`, mode changes use `unix.Fchmodat` with `AT_SYMLINK_NOFOLLOW`, and timestamp updates use `unix.Lutimes` with nanosecond conversion.

State and persistence: modifies metadata on the symlink itself rather than its target, preserving restore semantics for archived symlink entries.

Dependencies and integration points: selected by Go build constraints for Darwin and called by `FilesystemOutput.setAttributes` when the remote entry implements `fs.Symlink`.

Risks and test signals: platform support for symlink modes varies, and permission errors may be filtered by `IgnorePermissionErrors` in the caller. Coverage is mostly integration-level through restore behavior on macOS.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/snapshot/restore/local_fs_output_darwin.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/snapshot/restore/local_fs_output_unix.go -->
# sources/sync-backup/kopia/snapshot/restore/local_fs_output_unix.go

Purpose: Linux, FreeBSD, and OpenBSD symlink attribute helpers for local filesystem restore.

Important APIs/types/functions: `symlinkChown`, `symlinkChmod`, and `symlinkChtimes`.

Control flow: owner changes use `unix.Lchown`; chmod is a no-op because Linux does not support symlink permissions in the way restore needs; timestamp updates use `unix.Lutimes`.

State and persistence: changes symlink owner and timestamps where the OS permits, without following the link target. Mode restoration is intentionally skipped.

Dependencies and integration points: called by `FilesystemOutput.setAttributes` for symlink entries under the Unix build tag.

Risks and test signals: no-op chmod means restored symlink permission bits may not match metadata on platforms with different semantics. Errors are surfaced to the common caller unless permission ignoring is enabled.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/snapshot/restore/local_fs_output_unix.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/snapshot/restore/local_fs_output_windows.go -->
# sources/sync-backup/kopia/snapshot/restore/local_fs_output_windows.go

Purpose: Windows-specific symlink attribute handling for local filesystem restore.

Important APIs/types/functions: `symlinkChown`, `symlinkChmod`, and `symlinkChtimes`. Ownership and mode changes are no-ops; timestamp updates use Windows file APIs.

Control flow: `symlinkChtimes` converts access and write times to `windows.Filetime`, normalizes long filenames with `ospath.SafeLongFilename`, opens the reparse point with `FILE_FLAG_OPEN_REPARSE_POINT`, and calls `windows.SetFileTime`.

State and persistence: only symlink timestamps are modified. Chown/chmod are skipped because Windows restore metadata does not map cleanly to POSIX UID/GID/mode.

Dependencies and integration points: selected on Windows and used by `FilesystemOutput.setAttributes`.

Risks and test signals: handle opening requires suitable permissions and sharing flags; failures propagate through restore unless permission errors are ignored. Long path conversion is essential for deep restore targets.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/snapshot/restore/local_fs_output_windows.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/snapshot/restore/long_paths_plan9.go -->
# sources/sync-backup/kopia/snapshot/restore/long_paths_plan9.go

Purpose: Plan 9 implementation of placeholder suffix safety checks for shallow restore cleanup.

Important APIs/types/functions: `MaxFilenameLength` and `SafelySuffixablePath`.

Control flow: the check returns true when the whole path length plus `localfs.ShallowEntrySuffix` fits within `math.MaxUint16`. Unlike Unix/Windows variants, it does not inspect only the base name.

State and persistence: no state is changed; the result gates whether `SafeRemoveAll` may attempt to remove a placeholder sidecar.

Dependencies and integration points: used by shallow restore output and cleanup helpers to avoid generating impossible long placeholder filenames.

Risks and test signals: the constant is derived by code inspection and may be looser than a specific Plan 9 filesystem limit. The shared shallow helper test exercises boundary behavior through the platform-specific limit.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/snapshot/restore/long_paths_plan9.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/snapshot/restore/long_paths_unix.go -->
# sources/sync-backup/kopia/snapshot/restore/long_paths_unix.go

Purpose: Unix implementation of filename-length checks for shallow placeholder suffixing.

Important APIs/types/functions: `MaxFilenameLength = syscall.NAME_MAX` and `SafelySuffixablePath`.

Control flow: `SafelySuffixablePath` checks `len(filepath.Base(path)) + len(localfs.ShallowEntrySuffix)` against the platform name limit. Directory components are irrelevant because only the final placeholder filename is extended.

State and persistence: no persistent state; it protects later `os.RemoveAll` and placeholder creation from avoidable `ENAMETOOLONG` failures.

Dependencies and integration points: used by `restore.SafeRemoveAll` and shallow directory placeholder decisions on non-Windows, non-Plan9 builds.

Risks and test signals: byte length rather than rune or filesystem encoding details is used. The companion test sweeps lengths around `MaxFilenameLength` and expects cleanup to be harmless even when the placeholder cannot exist.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/snapshot/restore/long_paths_unix.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/snapshot/restore/long_paths_windows.go -->
# sources/sync-backup/kopia/snapshot/restore/long_paths_windows.go

Purpose: Windows filename-length check for shallow placeholder suffixing.

Important APIs/types/functions: `MaxFilenameLength = 255` and `SafelySuffixablePath`.

Control flow: the check uses `filepath.Base(path)` plus `localfs.ShallowEntrySuffix`, matching the per-component compatibility limit used by Linux and macOS rather than full Windows long-path capacity.

State and persistence: no state is changed; callers use the boolean to avoid impossible placeholder sidecar operations.

Dependencies and integration points: paired with Windows long path normalization in local restore and with `SafeRemoveAll` shallow cleanup.

Risks and test signals: the conservative 255 value may reject some paths Windows could represent with long-path APIs, but it prevents sidecar cleanup errors. Boundary behavior is covered by `shallow_helper_test.go`.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/snapshot/restore/long_paths_windows.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/snapshot/restore/restore.go -->
# sources/sync-backup/kopia/snapshot/restore/restore.go

Purpose: central restore engine that walks an `fs.Entry` snapshot tree and writes it to any `Output` implementation, including filesystem, tar, zip, or shallow filesystem output.

Important APIs/types/functions: `Output`, `Stats`, `Options`, `Entry`, internal `copier`, `copyEntry`, `copyEntryInternal`, `copyDirectory`, `deleteExtraFilesInDir`, and `copyDirectoryContent`.

Control flow: `Entry` builds a parallelwork queue, enqueues the root, chooses worker count from options/CPU/output serializability, processes work, closes output, and returns atomic stats. Directories are enqueued to the front, files to the back. Incremental mode skips matching existing files/symlinks. Delete-extra prunes local filesystem entries absent from the snapshot.

State and persistence: maintains atomic restore counters and may create, overwrite, skip, or delete target data through the output. Cancellation returns through completion callbacks rather than abruptly killing queued state.

Dependencies and integration points: relies on `fs.GetAllEntries`, `parallelwork.Queue`, `FilesystemOutput`, and shallow output wrapping.

Risks and test signals: delete-extra is filesystem-only and destructive when enabled. Error ignoring increments counters and suppresses failures. Depth-based shallow behavior depends on `RestoreDirEntryAtDepth` and placeholder suffix safety.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/snapshot/restore/restore.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/snapshot/restore/shallow_fs_output.go -->
# sources/sync-backup/kopia/snapshot/restore/shallow_fs_output.go

Purpose: local filesystem output wrapper that writes shallow placeholder files instead of full snapshot contents past a configured restore depth or for large files.

Important APIs/types/functions: `ShallowFilesystemOutput`, `makeShallowFilesystemOutput`, overridden `WriteDirEntry`, overridden `WriteFile`, `writeShallowEntry`, and `readonlyfilemode`.

Control flow: only wraps a `*FilesystemOutput`; other outputs are returned unchanged. Directory and large-file entries must implement `snapshot.HasDirEntry`, are serialized via `localfs.WriteShallowPlaceholder`, and then attributed with write bits cleared. Small files below `MinSizeForPlaceholder` are restored normally.

State and persistence: creates placeholder sidecar files on disk and refuses to write one when the real path already exists, avoiding ambiguous future snapshots.

Dependencies and integration points: used by `restore.Entry` when traversal depth exceeds the configured limit. Integrates with localfs shallow placeholder parsing and `SafeRemoveAll`.

Risks and test signals: placeholder writes preserve metadata but not content locally; real-path existence causes a hard error to avoid data loss. Long filename checks happen in the caller for shallow directories and cleanup helpers.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/snapshot/restore/shallow_fs_output.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/snapshot/restore/shallow_helper.go -->
# sources/sync-backup/kopia/snapshot/restore/shallow_helper.go

Purpose: helper functions for recognizing and safely deleting shallow placeholder sidecar files.

Important APIs/types/functions: `PathIfPlaceholder` and `SafeRemoveAll`.

Control flow: `PathIfPlaceholder` returns the base path when a path ends with `localfs.ShallowEntrySuffix`, otherwise `""`. `SafeRemoveAll` checks `SafelySuffixablePath`; if true it removes `path + suffix` through `ospath.SafeLongFilename`, otherwise it returns nil because such a placeholder could not have been created safely.

State and persistence: only `SafeRemoveAll` mutates filesystem state, and only by removing placeholder sidecars, not the real restored path.

Dependencies and integration points: called by local restore after writing real directories/files and by shallow restore cleanup paths.

Risks and test signals: correctness depends on the platform-specific suffixability check. The test sweeps near filename limits to ensure cleanup succeeds whether or not the sidecar could be created.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/snapshot/restore/shallow_helper.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/snapshot/restore/shallow_helper_test.go -->
# sources/sync-backup/kopia/snapshot/restore/shallow_helper_test.go

Purpose: boundary test for shallow placeholder cleanup around platform filename length limits.

Important APIs/types/functions: `TestSafeRemoveAll`, `MaxFilenameLength`, `localfs.ShallowEntrySuffix`, and `SafeRemoveAll`.

Control flow: the test creates a temp directory, iterates filename lengths around the maximum minus suffix space, tries to create the placeholder sidecar, calls `SafeRemoveAll` on the unsuffixed path, and verifies any actually-created sidecar is removed.

State and persistence: uses temporary files only. Some attempted writes are expected to fail because the filename is too long; that is not a test failure.

Dependencies and integration points: validates the contract shared by `long_paths_*` implementations and restore placeholder cleanup.

Risks and test signals: the loop depends on the platform-specific `MaxFilenameLength` constant and filesystem behavior. The key signal is no cleanup error and no leftover sidecar when creation succeeded.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/snapshot/restore/shallow_helper_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/snapshot/restore/tar_output.go -->
# sources/sync-backup/kopia/snapshot/restore/tar_output.go

Purpose: `restore.Output` implementation that serializes restored entries into a tar stream.

Important APIs/types/functions: `TarOutput`, `Parallelizable`, `BeginDirectory`, `Close`, `WriteFile`, `CreateSymlink`, and `NewTarOutput`.

Control flow: tar output is not parallelizable, so restore uses one worker. Non-root directories emit directory headers. Files open their snapshot reader, write a `tar.Header`, then stream bytes with `io.Copy`. Symlinks read their target and emit `tar.TypeSymlink` headers. Incremental existence checks always return false.

State and persistence: writes tar records to the supplied `io.WriteCloser`; no local filesystem entries are inspected or modified.

Dependencies and integration points: consumed by `restore.Entry` as an archive target and relies on `archive/tar` plus Kopia `fs` metadata.

Risks and test signals: directory finish and shallow dir-entry hooks are no-ops; extended attributes are not represented here. Caller must close to flush tar footer and wrapped writer. Restore statistics provide indirect signals.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/snapshot/restore/tar_output.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/snapshot/restore/zip_output.go -->
# sources/sync-backup/kopia/snapshot/restore/zip_output.go

Purpose: `restore.Output` implementation that serializes restored files into a zip stream.

Important APIs/types/functions: `ZipOutput`, `Parallelizable`, `Close`, `WriteFile`, `CreateSymlink`, and `NewZipOutput`.

Control flow: zip output is serial. Directory begin/finish hooks are no-ops; zip entries are created for files when `WriteFile` opens the snapshot file, prepares a `zip.FileHeader` with method, modified time, and mode, then copies data. Symlink creation only logs that it is unimplemented.

State and persistence: writes to the provided `io.WriteCloser` through `archive/zip`; it does not mutate local filesystem state and reports no existing files.

Dependencies and integration points: used by restore archive export paths where `method` controls zip compression/storage.

Risks and test signals: symlinks are silently skipped except for debug logging, and empty directories are not emitted. Callers must close the output to finalize the central directory. Integration tests should inspect produced archives.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/snapshot/restore/zip_output.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/snapshot/snapshot_test.go -->
# sources/sync-backup/kopia/snapshot/snapshot_test.go

Purpose: black-box tests for the snapshot package public API around manifest storage, source parsing, pins, and time sorting.

Important APIs/types/functions: `TestSnapshotsAPI`, `verifySnapshotManifestIDs`, `mustSaveSnapshot`, `verifySources`, `verifyListSnapshots`, `verifyLoadSnapshots`, `TestParseSourceInfo`, `TestParseInvalidSourceInfo`, `TestUpdatePins`, `TestSortByTimeAscending`, and `TestSortByTimeDescending`.

Control flow: tests create an in-memory repo environment, save manifests for two sources, list/filter/load them, update pins and verify a new manifest ID, parse source strings, and assert sort ordering with same start times but different end times.

State and persistence: writes snapshot manifests to the test repository and updates one manifest's pins. Source parsing uses the current working directory for bare paths.

Dependencies and integration points: covers repository manifest APIs, `snapshot.SourceInfo`, `manifest.ID`, and `repotesting`.

Risks and test signals: expected values rely on local absolute path normalization. Signals are exact manifest lists, source lists, pin sorting/deduplication, parse errors for invalid host syntax, and sort monotonicity.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/snapshot/snapshot_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/snapshot/snapshotfs/all_sources.go -->
# sources/sync-backup/kopia/snapshot/snapshotfs/all_sources.go

Purpose: exposes a virtual read-only root directory containing all snapshot sources in a repository grouped by user and host.

Important APIs/types/functions: `repositoryAllSources`, its `fs.Directory` methods, `Iterate`, and `AllSourcesEntry`.

Control flow: `Iterate` lists all source infos, deduplicates `username@host`, converts each to a filesystem-safe name via `safeNameForMount`, disambiguates case-insensitive collisions, and returns `sourceDirectories` children.

State and persistence: no repository writes. Directory metadata is synthetic, with modification time from `rep.Time()` and read-only directory mode.

Dependencies and integration points: used by browse/mount features that present repository snapshots as a filesystem. Depends on `snapshot.ListSources`, `fs.StaticIterator`, and source directory helpers.

Risks and test signals: source names with slashes, backslashes, or case collisions need deterministic disambiguation. Tests under `source_directories_test.go` validate expected tree names for mixed source paths and usernames.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/snapshot/snapshotfs/all_sources.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/snapshot/snapshotfs/dir_manifest_builder.go -->
# sources/sync-backup/kopia/snapshot/snapshotfs/dir_manifest_builder.go

Purpose: concurrent builder for serialized directory manifests and recursive directory summaries.

Important APIs/types/functions: `DirManifestBuilder`, `Clone`, `AddEntry`, `AddFailedEntry`, `Build`, `isDir`, and `sortedTopFailures`.

Control flow: `AddEntry` appends a `snapshot.DirEntry` and updates aggregate summary counts, sizes, max mod time, and child failure summaries. `AddFailedEntry` records ignored or fatal errors. `Build` increments total directory count, sets max mod time for empty directories, stores incomplete reason, trims/sorts failures, sorts entries with directories first, and returns a `snapshot.DirManifest`.

State and persistence: state is mutex-protected in memory. Persistence happens later through `WriteDirManifest`.

Dependencies and integration points: used by upload checkpointing, directory rewrite, and directory writer paths.

Risks and test signals: `Build` mutates internal entry order and failure list; callers should not assume stable insertion order. Symlink file sizes are not propagated into total file size. Tests cover files, symlinks, and directory child summaries.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/snapshot/snapshotfs/dir_manifest_builder.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/snapshot/snapshotfs/dir_manifest_builder_test.go -->
# sources/sync-backup/kopia/snapshot/snapshotfs/dir_manifest_builder_test.go

Purpose: unit coverage for `DirManifestBuilder.AddEntry` summary aggregation.

Important APIs/types/functions: `TestAddEntry`, `DirManifestBuilder`, `snapshot.DirEntry`, and `fs.DirectorySummary`.

Control flow: three subcases add a file, a symlink, and a directory with a child summary, then assert the builder summary counters and max modification time.

State and persistence: only in-memory builder state is inspected; no directory manifest is written to the repository.

Dependencies and integration points: validates summary fields consumed by repository-backed directory entries, storage stats, restore progress, and UI display.

Risks and test signals: the symlink case intentionally skips total-size checking because symlink size is not propagated. The test does not cover `Build` sorting, failed-entry trimming, or concurrent `AddEntry`, so those rely on other coverage or code review.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/snapshot/snapshotfs/dir_manifest_builder_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/snapshot/snapshotfs/dir_reader.go -->
# sources/sync-backup/kopia/snapshot/snapshotfs/dir_reader.go

Purpose: parses a serialized Kopia directory object from JSON.

Important APIs/types/functions: `directoryStreamType` and `readDirEntries`.

Control flow: `readDirEntries` decodes a `snapshot.DirManifest` from an `io.Reader`, checks `StreamType == "kopia:directory"`, and returns entries plus summary.

State and persistence: read-only; it interprets repository object bytes opened by `repofs` and `dir_rewriter`.

Dependencies and integration points: paired with `WriteDirManifest`, used by `repositoryDirectory.loadLocked` and `DirRewriter.processDirectory` to materialize directory contents.

Risks and test signals: any schema or stream type change must preserve this validation. Errors distinguish invalid JSON from wrong stream type, which helps diagnose corrupt or misidentified objects. Coverage is mostly through repository filesystem and tree walker tests.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/snapshot/snapshotfs/dir_reader.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/snapshot/snapshotfs/dir_rewriter.go -->
# sources/sync-backup/kopia/snapshot/snapshotfs/dir_rewriter.go

Purpose: recursively rewrites snapshot directory trees, allowing callers to replace, remove, keep, or stub entries and then write new directory manifests.

Important APIs/types/functions: `RewriteDirEntryCallback`, `RewriteFailedEntryCallback`, `UnreadableDirEntryReplacement`, `DirRewriterOptions`, `DirRewriter`, `RewriteSnapshotManifest`, `RewriteKeep`, `RewriteAsStub`, `RewriteFail`, `RewriteRemove`, and `NewDirRewriter`.

Control flow: entries are keyed by SHA1 of JSON metadata in a `bigmap` cache. Rewrites may run through a workshare pool. Directory replacements are recursively opened, read, children rewritten, rebuilt with `DirManifestBuilder`, and persisted with `WriteDirManifest`; unreadable directories go through the configured failure callback.

State and persistence: writes new directory objects and optional stub file objects to the repository, and mutates `man.RootEntry` when changed. Cache and worker pool are closed explicitly.

Dependencies and integration points: integrates with repository object writers, metadata compression policy, snapshot manifests, and maintenance/repair workflows.

Risks and test signals: cache keys ignore parent path, so identical metadata entries share rewritten output. Failure callback choice controls whether corrupt subtrees are kept, removed, stubbed, or fatal. Stub creation depends on effective global policy.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/snapshot/snapshotfs/dir_rewriter.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/snapshot/snapshotfs/dir_writer.go -->
# sources/sync-backup/kopia/snapshot/snapshotfs/dir_writer.go

Purpose: writes a `snapshot.DirManifest` as a repository object and returns its object ID.

Important APIs/types/functions: `WriteDirManifest`.

Control flow: creates an object writer with description `DIR:<relative path>`, directory object prefix `"k"`, and the requested compressor/metadata compressor. It JSON-encodes the manifest, calls `Result`, and returns the object ID.

State and persistence: persists directory metadata into the repository object store. The writer is deferred closed even after successful `Result`.

Dependencies and integration points: paired with `readDirEntries`, used by uploader and directory rewriter. Object prefix drives `IsDirectoryID` autodetection in `repofs`.

Risks and test signals: JSON encode or writer result failures leave no valid directory object. Compressor choice must match policy expectations. Integration tests that upload, browse, restore, and verify snapshots exercise this path indirectly.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/snapshot/snapshotfs/dir_writer.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/snapshot/snapshotfs/objref.go -->
# sources/sync-backup/kopia/snapshot/snapshotfs/objref.go

Purpose: resolves user-facing snapshot or object references into repository-backed filesystem entries or nested object IDs.

Important APIs/types/functions: `ParseObjectIDWithPath`, `GetNestedEntry`, `FindSnapshotByRootObjectIDOrManifestID`, `FilesystemEntryFromIDWithPath`, `FilesystemDirectoryFromIDWithPath`, `consistentSnapshotMetadata`, and `GetEntryFromPlaceholder`.

Control flow: references may be manifest IDs, root object IDs, or object IDs followed by slash paths. Manifest IDs are tried first; otherwise snapshots sharing the root object are listed and checked for consistent root metadata. Nested paths descend through `fs.Directory.Child`.

State and persistence: read-only; it opens repository objects and manifests but does not write.

Dependencies and integration points: supports CLI restore/browse paths, shallow placeholder expansion, and object ID parsing via `repo/object` and `repo/manifest`.

Risks and test signals: multiple snapshots can share root objects but differ in root attributes; `consistentAttributes` decides whether that is an error or latest-manifest selection. Nested paths disable consistency checks because parent entries carry attributes.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/snapshot/snapshotfs/objref.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/snapshot/snapshotfs/repofs.go -->
# sources/sync-backup/kopia/snapshot/snapshotfs/repofs.go

Purpose: implements a virtual filesystem over Kopia repository snapshot objects.

Important APIs/types/functions: `repositoryEntry`, `repositoryDirectory`, `repositoryFile`, `repositorySymlink`, `EntryFromDirEntry`, `DirectoryEntry`, `SnapshotRoot`, `AutoDetectEntryFromObjectID`, `IsDirectoryID`, and `withFileInfo`.

Control flow: directory contents are lazily loaded from repository objects through `readDirEntries` under a mutex and cached by name. Files open object readers. Symlinks read their target object. Auto-detection treats IDs with directory content prefix as possible directories and falls back to synthetic files.

State and persistence: read-only repository access with per-directory cached entries/summary that can be dropped by `Close`. It mutates loaded directory child metadata to reflect summary size and max mod time for directories.

Dependencies and integration points: core adapter used by restore, tree walking, verification, object reference resolution, mounts, and storage stats.

Risks and test signals: `Resolve` for symlinks is not implemented. Directory autodetection opens and iterates objects, so corrupt directory-looking objects become files. Unknown entry types become `fs.ErrorEntry`. Tests exercise walker, verifier, source browsing, and storage stats through this adapter.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/snapshot/snapshotfs/repofs.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/snapshot/snapshotfs/snapshot_storage_stats.go -->
# sources/sync-backup/kopia/snapshot/snapshotfs/snapshot_storage_stats.go

Purpose: computes per-snapshot new data and running total storage usage across a sequence of manifests.

Important APIs/types/functions: `CalculateStorageStats`, `snapshot.StorageUsageDetails`, `snapshot.StorageStats`, `TreeWalker`, and repository `VerifyObject`/`ContentInfo`.

Control flow: one `TreeWalker` and one unique-content `bigmap.Set` are reused across manifests. For each manifest, `unique` counters reset, the root is walked, each previously unseen object/content contributes to new and running totals, and the callback receives the manifest after `StorageStats` is populated.

State and persistence: mutates `Manifest.StorageStats` in memory only. Running totals and unique content set persist across the input manifest order.

Dependencies and integration points: depends on repository object verification, content metadata, and snapshot root conversion. Used by reporting and analysis features.

Risks and test signals: input manifest ordering matters for "new" data. The code assumes `manifests` is non-empty and uses `manifests[0].Source`. TreeWalker dedupes by object ID, so repeated identical snapshots produce zero new data.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/snapshot/snapshotfs/snapshot_storage_stats.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/snapshot/snapshotfs/snapshot_storage_stats_test.go -->
# sources/sync-backup/kopia/snapshot/snapshotfs/snapshot_storage_stats_test.go

Purpose: validates `CalculateStorageStats` for duplicate content, repeated snapshots, and incremental additions.

Important APIs/types/functions: `TestCalculateStorageStats`, `mockfs`, `repotesting`, `upload.NewUploader`, and `snapshotfs.CalculateStorageStats`.

Control flow: the test uploads a directory with two unique file contents and one duplicate, uploads the same tree again, adds one new file, uploads a third snapshot, computes stats for all three, and compares exact `StorageStats` structs.

State and persistence: writes snapshot objects and manifests to a test repository and flushes between uploads. Stats are collected from callback-mutated manifests.

Dependencies and integration points: covers uploader, repository object/content accounting, tree walker dedupe, and packed/original content sizes.

Risks and test signals: expected packed byte counts are format/implementation-sensitive. The key behavioral signals are nonzero first snapshot, all-zero new data for identical second snapshot, and only changed root/dir/file content for the third.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/snapshot/snapshotfs/snapshot_storage_stats_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/snapshot/snapshotfs/snapshot_tree_walker.go -->
# sources/sync-backup/kopia/snapshot/snapshotfs/snapshot_tree_walker.go

Purpose: parallel, de-duplicating traversal of repository-backed snapshot filesystem trees.

Important APIs/types/functions: `EntryCallback`, `TreeWalker`, `ReportError`, `GetErrors`, `Err`, `TooManyErrors`, `Process`, `Close`, `TreeWalkerOptions`, and `NewTreeWalker`.

Control flow: `Process` rejects entries without object IDs, dedupes by object ID in a `bigmap.Set`, invokes the callback, and recursively processes directories. Directory children may be handled through a workshare pool. Iteration stops early when `MaxErrors` is reached.

State and persistence: in-memory walker state persists across multiple `Process` calls, so the same walker skips objects already seen in previous roots. It records total error count plus a bounded list of errors.

Dependencies and integration points: used by verifier, snapshot GC, and storage stats to avoid reprocessing shared objects.

Risks and test signals: dedupe by object ID means identical content at different paths is visited once. `MaxErrors <= 0` means unlimited but only one stored error when zero. Tests cover dedupe, missing object ID, single/multiple errors, and shared-OID errors.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/snapshot/snapshotfs/snapshot_tree_walker.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/snapshot/snapshotfs/snapshot_tree_walker_test.go -->
# sources/sync-backup/kopia/snapshot/snapshotfs/snapshot_tree_walker_test.go

Purpose: exercises `TreeWalker` traversal, dedupe, and error reporting.

Important APIs/types/functions: `TestSnapshotTreeWalker`, `TestSnapshotTreeWalker_Errors`, `TestSnapshotTreeWalker_MultipleErrors`, and `TestSnapshotTreeWalker_MultipleErrorsSameOID`.

Control flow: tests first assert processing a local mock directory without object IDs fails. They upload mock trees, process snapshot roots, count callback invocations, reprocess roots to verify dedupe, add new content to verify only new objects are visited, and inject callback errors by entry path.

State and persistence: uses a test repository populated through `upload.NewUploader`; walker state persists within each test until `Close`.

Dependencies and integration points: covers uploader output, `SnapshotRoot`, repository-backed filesystem entries, and workshare-disabled deterministic paths with `Parallelism: 1`.

Risks and test signals: shared object IDs deliberately collapse multiple paths into one callback/error opportunity. Expected callback counts encode object sharing assumptions for directories and files.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/snapshot/snapshotfs/snapshot_tree_walker_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/snapshot/snapshotfs/snapshot_verifier.go -->
# sources/sync-backup/kopia/snapshot/snapshotfs/snapshot_verifier.go

Purpose: verifies snapshot filesystem objects and optional backing blob presence in parallel, with progress statistics and bounded error reporting.

Important APIs/types/functions: `Verifier`, `VerifierStats`, `VerifierOptions`, `VerifierResult`, `AddToExpectedTotals`, `VerifyFile`, `verifyObject`, `readEntireObject`, `InParallel`, and `NewVerifier`.

Control flow: `InParallel` creates a `TreeWalker`, starts file verification workers, lets the caller enqueue roots through the walker, closes the file queue, waits, then returns accumulated stats and errors. Directories count as processed immediately; files are queued for object verification, optional blob-map checking, and probabilistic full reads.

State and persistence: read-only repository access. Stats live on the verifier instance and are not reset by `InParallel`; callers needing isolated stats should create a new verifier.

Dependencies and integration points: integrates with `TreeWalker`, repository `VerifyObject`, `ContentInfo`, `OpenObject`, blob maps, JSON stats logging, and CLI verification commands.

Risks and test signals: random read sampling depends on `VerifyFilesPercent`. Blob-map mode detects missing pack blobs before full reads. `MaxErrors` limits stored errors and worker processing.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/snapshot/snapshotfs/snapshot_verifier.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/snapshot/snapshotfs/snapshot_verifier_test.go -->
# sources/sync-backup/kopia/snapshot/snapshotfs/snapshot_verifier_test.go

Purpose: integration tests for verifier success, enqueue errors, full file reads, missing blob detection, and max-error limiting.

Important APIs/types/functions: `TestSnapshotVerifier`, `snapshotfs.NewVerifier`, `VerifierOptions`, `InParallel`, `DirectoryEntry`, `blob.ReadBlobMap`, and repository blob deletion.

Control flow: the test uploads a directory with three files, opens another repository handle, then runs subtests for enqueue errors, positive blob-map verification, full reads with blob map, missing pack blobs in the blob map, `MaxErrors=1`, and missing underlying blobs without a blob map.

State and persistence: writes real repository objects, flushes, reads blob maps, mutates an in-memory blob map, and deletes pack blobs in the final scenario.

Dependencies and integration points: covers verifier, tree walker, repository object verification, blob storage, uploader, and error aggregation.

Risks and test signals: subtests use separate verifier instances except where zero-stat runs are intentional. Signals include error counts, specific missing-blob messages, nonzero processed/read stats, and max-error truncation.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/snapshot/snapshotfs/snapshot_verifier_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/snapshot/snapshotfs/source_directories.go -->
# sources/sync-backup/kopia/snapshot/snapshotfs/source_directories.go

Purpose: virtual directory level that groups snapshots for one `user@host` by source path using filesystem-safe names.

Important APIs/types/functions: `sourceDirectories`, `Iterate`, `disambiguateSafeNames`, and `safeNameForMount`.

Control flow: `Iterate` lists all sources, filters to the configured `userHost`, maps original paths to safe names, disambiguates case-insensitive collisions recursively, and returns `sourceSnapshots` entries. `safeNameForMount` normalizes root, Windows drive prefixes, forward/back slashes, trailing underscores, and trailing colons.

State and persistence: read-only synthetic directory state; modification time comes from repository time.

Dependencies and integration points: child of `repositoryAllSources` and parent of timestamped snapshot directories for mount/browse features.

Risks and test signals: name disambiguation must be deterministic and collision-safe on case-sensitive and case-insensitive filesystems. Internal tests cover path normalization and recursive collision resolution; source tree tests cover full mount names.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/snapshot/snapshotfs/source_directories.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/snapshot/snapshotfs/source_directories_internal_test.go -->
# sources/sync-backup/kopia/snapshot/snapshotfs/source_directories_internal_test.go

Purpose: direct tests for safe mount-name generation and collision disambiguation.

Important APIs/types/functions: `TestSafeNameForMount`, `TestDisambiguateSafeNames`, `safeNameForMount`, and `disambiguateSafeNames`.

Control flow: path cases cover Unix roots, trailing slashes, Windows drives, UNC paths, forward slashes, backslashes, and mixed separators. Disambiguation cases feed maps where several originals collapse to the same safe lowercase name and verify deterministic suffixes like `" (2)"`.

State and persistence: pure in-memory string mapping tests.

Dependencies and integration points: protects `AllSourcesEntry` and repository mount browsing from invalid or ambiguous directory names.

Risks and test signals: map iteration is made deterministic by sorting conflicting originals. Recursive disambiguation is tested by including an original that already contains `" (2)"` and collides with a generated suffix.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/snapshot/snapshotfs/source_directories_internal_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/snapshot/snapshotfs/source_directories_test.go -->
# sources/sync-backup/kopia/snapshot/snapshotfs/source_directories_test.go

Purpose: integration test for the virtual all-sources filesystem hierarchy.

Important APIs/types/functions: `TestAllSources`, `iterateAllNames`, and `mustWriteSnapshotManifest`.

Control flow: the test uploads one base manifest, rewrites copies of it with varied users, hosts, source paths, case differences, roots, and timestamps, then walks `snapshotfs.AllSourcesEntry` recursively and compares the exact set of directory names.

State and persistence: writes multiple snapshot manifests into a test repository. The same root entry is reused while source and start time are changed.

Dependencies and integration points: covers `AllSourcesEntry`, `sourceDirectories`, `sourceSnapshots`, safe-name disambiguation, manifest listing, and repository-backed directory entries.

Risks and test signals: expected names encode timestamp formatting and collision suffixing. The helper uses recursive `fs.IterateEntries`, so failures can come from iterator behavior as well as naming logic.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/snapshot/snapshotfs/source_directories_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/snapshot/snapshotfs/source_snapshots.go -->
# sources/sync-backup/kopia/snapshot/snapshotfs/source_snapshots.go

Purpose: virtual directory that lists all snapshots for one source as timestamp-named child directories.

Important APIs/types/functions: `sourceSnapshots`, its `fs.Directory` methods, and `Iterate`.

Control flow: `Iterate` calls `snapshot.ListSnapshots` for the configured source, formats each start time as `YYYYMMDD-HHMMSS`, appends the incomplete reason in parentheses when present, builds a synthetic directory `DirEntry` with the snapshot root object ID, and returns repository entries.

State and persistence: read-only synthetic entries backed by actual root objects. Directory summary is copied from `m.RootEntry.DirSummary` when present.

Dependencies and integration points: leaf level under `AllSourcesEntry` for browsing historical snapshots and feeding restore/mount traversal.

Risks and test signals: snapshots with identical second-level start times and same incomplete reason would map to duplicate child names. Tests validate typical naming through the all-sources integration suite.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/snapshot/snapshotfs/source_snapshots.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/snapshot/snapshotgc/gc.go -->
# sources/sync-backup/kopia/snapshot/snapshotgc/gc.go

Purpose: snapshot-aware garbage collection that finds content no longer referenced by snapshot manifests, optionally deletes it, and repairs referenced content that was previously marked deleted.

Important APIs/types/functions: `findInUseContentIDs`, `Run`, `runInternal`, `findUnreferencedAndRepairRereferenced`, and `buildGCResult`.

Control flow: GC loads all snapshot manifests, walks each root with `snapshotfs.TreeWalker`, verifies objects to collect referenced content IDs, then iterates all contents including deleted entries. Manifest/system contents are counted separately. Referenced deleted contents are undeleted; unreferenced recent contents are protected by safety age; older unreferenced contents are logged and optionally deleted.

State and persistence: can undelete and delete repository content and flushes periodically and at the end. Maintenance run statistics are recorded through `maintenance.ReportRun`.

Dependencies and integration points: used by full snapshot maintenance, integrates with content logs, maintenance safety parameters, repository content manager, and maintenancestats.

Risks and test signals: safety window depends on maintenance start time and content timestamps. Without `gcDelete`, finding unused content returns an error after stats. Tests cover simple deletion, min-age protection, and undelete of reused referenced content.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/snapshot/snapshotgc/gc.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/snapshot/snapshotmaintenance/helper_test.go -->
# sources/sync-backup/kopia/snapshot/snapshotmaintenance/helper_test.go

Purpose: test helper for creating saved snapshots through the same policy and upload path used by maintenance tests.

Important APIs/types/functions: `createSnapshot`.

Control flow: cleans the source path, obtains the policy tree for the source, finds previous manifests, uploads the filesystem entry, sets the description, and saves the manifest.

State and persistence: writes snapshot objects and a snapshot manifest into the provided repository writer. It uses previous manifests to preserve uploader behavior around incremental/cache decisions.

Dependencies and integration points: shared by snapshot maintenance tests for realistic repository state setup. Depends on `policy.TreeForSource`, `snapshot.FindPreviousManifests`, `upload.NewUploader`, and `snapshot.SaveSnapshot`.

Risks and test signals: helper errors wrap policy and save failures, which makes maintenance test failures easier to locate. Since it normalizes source paths with `filepath.Clean`, tests should not rely on unclean path strings.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/snapshot/snapshotmaintenance/helper_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/snapshot/snapshotmaintenance/snapshotmaintenance.go -->
# sources/sync-backup/kopia/snapshot/snapshotmaintenance/snapshotmaintenance.go

Purpose: orchestrates snapshot GC plus low-level repository maintenance for writable repositories.

Important APIs/types/functions: `ErrReadonly` and `Run`.

Control flow: `Run` rejects read-only repository connections, enables the repository log manager, and invokes `maintenance.RunExclusive`. For full maintenance it runs `snapshotgc.Run` with deletion enabled before calling generic `maintenance.Run`; auto/quick modes skip snapshot GC unless maintenance scheduling chooses full mode.

State and persistence: can mutate repository maintenance metadata, logs, content indexes, content deletion state, and snapshot GC state through delegated maintenance tasks.

Dependencies and integration points: used by CLI/server maintenance entry points. Integrates `repo.DirectRepositoryWriter`, `maintenance.Mode`, `maintenance.SafetyParameters`, and `snapshotgc`.

Risks and test signals: read-only protection is the only guard in this wrapper; exclusive maintenance handles concurrency. Snapshot GC failures abort full maintenance. Tests assert read-only error and full maintenance behavior across repository format versions.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/snapshot/snapshotmaintenance/snapshotmaintenance.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/snapshot/snapshotmaintenance/snapshotmaintenance_test.go -->
# sources/sync-backup/kopia/snapshot/snapshotmaintenance/snapshotmaintenance_test.go

Purpose: format-parametrized integration tests for snapshot maintenance, snapshot GC safety, auto-maintenance liveness, and read-only rejection.

Important APIs/types/functions: `testHarness`, `TestSnapshotGCSimple`, `TestMaintenanceReuseDirManifest`, `TestSnapshotGCMinContentAgeSafety`, `TestMaintenanceAutoLiveness`, `TestNoMaintenanceReadOnly`, plus helpers for fake time, snapshots, flushing, raw object creation, and content deletion checks.

Control flow: tests create mock filesystem snapshots, delete manifests, advance fake time past or near safety windows, run full/auto maintenance, verify content deletion/undeletion, simulate concurrent reuse of directory manifests, and ensure auto maintenance keeps task runs recent over 21 days.

State and persistence: heavily mutates test repositories: manifests, content objects, deleted flags, maintenance schedules, and direct writer sessions.

Dependencies and integration points: covers snapshot maintenance wrapper, snapshot GC, generic repository maintenance, faketime, repotesting, uploader, object/content APIs, and format versions.

Risks and test signals: timing safety uses fake time and a 20-second buffer around `MinContentAgeSubjectToGC`. Reuse test checks that referenced content can be undeleted by a later maintenance run. Read-only test expects `ErrReadonly`.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/snapshot/snapshotmaintenance/snapshotmaintenance_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/snapshot/snapshotmaintenance/suite_test.go -->
# sources/sync-backup/kopia/snapshot/snapshotmaintenance/suite_test.go

Purpose: drives the snapshot maintenance test suite against multiple repository format versions.

Important APIs/types/functions: `formatSpecificTestSuite`, `TestFormatV1`, `TestFormatV2`, and `TestFormatV3`.

Control flow: each top-level test calls `testutil.RunAllTestsWithParam` with a suite value carrying one `format.Version`, causing the methods in `snapshotmaintenance_test.go` to run for that format.

State and persistence: this file creates no repository state itself; it parameterizes the stateful integration tests.

Dependencies and integration points: ensures snapshot GC and maintenance behavior remains valid across format versions 1, 2, and 3.

Risks and test signals: suite discovery depends on the test utility recognizing methods on `formatSpecificTestSuite`. Failures identify format-specific persistence or maintenance regressions rather than logic isolated to this file.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/snapshot/snapshotmaintenance/suite_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/snapshot/source.go -->
# sources/sync-backup/kopia/snapshot/source.go

Purpose: defines the canonical source identity for snapshots and parsing/string conversion for user-provided source selectors.

Important APIs/types/functions: `SourceInfo`, `SourceInfo.String`, and `ParseSourceInfo`.

Control flow: `String` renders empty source as `"(global)"`, host-only/user-host scopes as `user@host`, and path scopes as `user@host:path`. Parsing recognizes `"(global)"`, `user@host:path`, `@host`, `user@host`, and otherwise treats input as a local path that is absolutized and cleaned with the supplied default host/user.

State and persistence: no persistence here, but `SourceInfo` values are serialized into snapshot manifests and policy definitions.

Dependencies and integration points: used throughout snapshot listing, policy targeting, upload, maintenance, and source browsing.

Risks and test signals: parsing is simple delimiter-based and does not support usernames/hosts containing `@` or pathful selectors without `:`. Bare paths depend on process working directory. Tests cover round trips and invalid `"@"`.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/snapshot/source.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/snapshot/stats.go -->
# sources/sync-backup/kopia/snapshot/stats.go

Purpose: defines snapshot generation counters and a helper for excluded entries.

Important APIs/types/functions: `Stats` and `AddExcluded`.

Control flow: `AddExcluded` checks `md.IsDir()`. Directories increment `ExcludedDirCount`; files increment `ExcludedFileCount` and add `md.Size()` to `ExcludedTotalFileSize` using atomic operations.

State and persistence: stats are in-memory counters intended for concurrent snapshot/upload/estimate progress reporting and JSON serialization. The struct arranges int64 and int32 fields for atomic updates.

Dependencies and integration points: used by upload estimation and snapshot generation to report included, cached, non-cached, excluded, ignored-error, and fatal-error counts.

Risks and test signals: only exclusion helper logic lives here; callers must atomically update other fields themselves. Directory sizes are not added to excluded total size. Tests assert file and directory exclusion effects exactly.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/snapshot/stats.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/snapshot/stats_test.go -->
# sources/sync-backup/kopia/snapshot/stats_test.go

Purpose: unit test for `snapshot.Stats.AddExcluded`.

Important APIs/types/functions: `TestStats`, `mockfs.NewDirectory`, `AddFile`, and `snapshot.Stats.AddExcluded`.

Control flow: creates a mock directory and a file, then runs two cases: excluding the directory should increment only `ExcludedDirCount`; excluding the file should increment `ExcludedFileCount` and `ExcludedTotalFileSize`.

State and persistence: all state is in memory through mock filesystem entries.

Dependencies and integration points: protects upload estimate and ignore handling code that relies on excluded counters.

Risks and test signals: test compares the entire `Stats` struct, so unintended changes to additional fields are caught. It does not cover concurrent atomic updates or other stats counters.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/snapshot/stats_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/snapshot/upload/checkpoint_registry.go -->
# sources/sync-backup/kopia/snapshot/upload/checkpoint_registry.go

Purpose: tracks active upload checkpoint callbacks and materializes checkpointed directory entries into a directory manifest builder.

Important APIs/types/functions: `checkpointFunc`, `checkpointRegistry`, `addCheckpointCallback`, `removeCheckpointCallback`, and `runCheckpoints`.

Control flow: callbacks are stored by entry name under a mutex. `runCheckpoints` invokes each callback, skips nil results, randomizes names for non-directory checkpoint entries using `.checkpointed.<name>.<uuid>`, and adds entries to a `snapshotfs.DirManifestBuilder`.

State and persistence: registry state is in-memory. Checkpoint results may later be persisted when the builder's manifest is written by the upload path. Randomized file names intentionally prevent checkpoint objects from becoming authoritative normal entries in later runs.

Dependencies and integration points: used by the snapshot uploader during long directory uploads and checkpoint creation.

Risks and test signals: callback map iteration order is nondeterministic, but final builder sorting provides stable manifest order. Callback errors abort the checkpoint run. Tests verify removal, nil skip, directory name preservation, and file name randomization prefix.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/snapshot/upload/checkpoint_registry.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/snapshot/upload/checkpoint_registry_test.go -->
# sources/sync-backup/kopia/snapshot/upload/checkpoint_registry_test.go

Purpose: unit coverage for upload checkpoint registration, removal, nil checkpoints, and generated entry names.

Important APIs/types/functions: `TestCheckpointRegistry`, `checkpointRegistry`, `snapshotfs.DirManifestBuilder`, and mock filesystem entries.

Control flow: the test registers callbacks for a directory and several files, removes one duplicate-name callback twice, seeds the builder with a pre-existing entry, runs checkpoints, builds a manifest, and inspects sorted entry names.

State and persistence: all state is in memory. UUID suffixes are only checked by prefix because they are random.

Dependencies and integration points: validates checkpoint output shape consumed by uploader directory manifests.

Risks and test signals: duplicate entry names in the registry overwrite earlier callbacks before removal. Expected order relies on `DirManifestBuilder.Build` sorting directories before non-directories by name. The test does not cover callback errors.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/snapshot/upload/checkpoint_registry_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/snapshot/upload/estimate.go -->
# sources/sync-backup/kopia/snapshot/upload/estimate.go

Purpose: estimates snapshot traversal statistics and size buckets without uploading data.

Important APIs/types/functions: `SampleBucket`, `SampleBuckets`, `makeBuckets`, `EstimateProgress`, `Estimate`, and recursive `estimate`.

Control flow: `Estimate` initializes stats and included/excluded buckets, wraps the source directory with `ignorefs.New`, records ignored entries through policy callbacks, defers final progress stats, then recursively walks entries. Directories increment total directory count, skip children when they do not support multiple iterations, report processing/progress, and account ignored or fatal directory iteration errors. Files add included bucket samples and total file counts/size.

State and persistence: no repository writes. It mutates `snapshot.Stats` atomically and reports through the progress interface.

Dependencies and integration points: used by UI/CLI estimate commands before snapshot upload; integrates policy tree ignore rules and error handling policy.

Risks and test signals: streaming directories are counted but not traversed. Directory iteration errors are reported and returned even when marked ignored. Bucket examples are capped by caller-provided max examples.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/snapshot/upload/estimate.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/snapshot/upload/estimate_test.go -->
# sources/sync-backup/kopia/snapshot/upload/estimate_test.go

Purpose: regression test that upload estimation does not consume streaming directories.

Important APIs/types/functions: `fakeProgress`, `TestEstimate_SkipsStreamingDirectory`, `virtualfs.NewStreamingDirectory`, `policy.BuildTree`, and `upload.Estimate`.

Control flow: the test creates a virtual root containing a streaming directory with one file, runs estimate with the default policy tree, and verifies final stats through `fakeProgress.Stats`.

State and persistence: all filesystem entries are virtual/mock in-memory objects; no repository is used.

Dependencies and integration points: protects `estimate` behavior for directories where `SupportsMultipleIterations` is false, which prevents destructive or one-shot iteration during estimation.

Risks and test signals: only final callback assertions are checked. Expected result is zero files, two directories, and zero errors, proving the streaming child file was not traversed.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/snapshot/upload/estimate_test.go -->
