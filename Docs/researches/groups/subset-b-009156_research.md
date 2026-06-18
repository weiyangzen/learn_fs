# subset-b-009156 research

Grouped research for restic command files under `sources/sync-backup/restic/cmd/restic`. Each section is delimited for deterministic splitting into source-tree-aligned per-file reports.

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/restic/cmd/restic/cmd_generate.go -->
# sources/sync-backup/restic/cmd/restic/cmd_generate.go

Purpose: implements `restic generate`, which writes generated man pages and shell completions for bash, fish, zsh, and PowerShell.

Important APIs/types/functions: `newGenerateCommand` registers the cobra command; `generateOptions` stores output paths; `writeManpages` uses `cobra/doc.GenManTree` with a fixed Jan 2017 date for deterministic man pages; `writeCompletion` writes either to a named file or terminal stdout when the target is `-`; `checkStdoutForSingleShell` rejects multiple stdout completion targets; `runGenerate` orchestrates all generation.

Control flow and state: the command rejects positional arguments, constructs a fresh root command with default global options, emits requested artifacts, and fails if no output option was set. Persistent writes are filesystem writes for generated files/directories only; repository state is not opened or modified.

Dependencies and integration points: depends on cobra, pflag, cobra/doc, restic `global.Options`, terminal/progress printers, and `newRootCommand`. Its output is sensitive to root command registration and command help text.

Risks: completion-to-stdout must stay single-shell to avoid interleaved output. Any command tree changes affect generated docs. File creation uses `os.Create`, so existing completion files are truncated.

Test signals: `cmd_generate_integration_test.go` verifies stdout completion headers for all shells and the multiple-stdout error path.
<!-- END_FILE_RESEARCH: sources/sync-backup/restic/cmd/restic/cmd_generate.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/restic/cmd/restic/cmd_generate_integration_test.go -->
# sources/sync-backup/restic/cmd/restic/cmd_generate_integration_test.go

Purpose: integration coverage for `runGenerate` when completions are written to stdout.

Important APIs/types/functions: `testRunGenerate` wraps `runGenerate` with `withCaptureStdout`; `TestGenerateStdout` drives bash, fish, zsh, and powershell options plus a negative case with two `-` outputs.

Control flow and state: tests use an in-memory stdout buffer and do not create repositories or files. Each shell case asserts the generated text contains a shell-specific completion header.

Dependencies and integration points: depends on integration terminal helpers, `global.Options`, and `internal/test` assertions. It indirectly verifies cobra completion generation through the full root command tree.

Risks: header-string assertions are lightweight and can fail if cobra changes comment wording while completions remain valid. The test does not verify generated files or man pages.

Test signals: confirms each stdout mode works and `checkStdoutForSingleShell` blocks ambiguous multi-shell stdout output.
<!-- END_FILE_RESEARCH: sources/sync-backup/restic/cmd/restic/cmd_generate_integration_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/restic/cmd/restic/cmd_init.go -->
# sources/sync-backup/restic/cmd/restic/cmd_init.go

Purpose: implements `restic init`, creating a new repository with a selected repository format and optional chunker parameters copied from a secondary repository.

Important APIs/types/functions: `newInitCommand`; `InitOptions` embedding `global.SecondaryRepoOptions`; `runInit`; `maybeReadChunkerPolynomial`; `initSuccess` JSON output. Flags include `--repository-version`, `--copy-chunker-params`, and secondary repository options.

Control flow and state: `runInit` rejects positional arguments, parses version as `stable`, `latest`, empty, or numeric, optionally opens a secondary repository to read its chunker polynomial, then calls `global.CreateRepository`. It writes repository config, key, and layout through global repository creation. Text output strips repository passwords; JSON emits `message_type`, repository ID, and stripped repository location.

Dependencies and integration points: uses `restic.StableRepoVersion`, `restic.MaxRepoVersion`, `location.StripPassword`, `chunker.Pol`, and global backend/repository creation. Secondary repository handling integrates with copy workflows.

Risks: accepting numeric versions pushes validation into repository creation. Secondary repository options are rejected unless `--copy-chunker-params` is set, preventing accidental unintended reads. JSON/text output behavior diverges.

Test signals: integration test covers invalid secondary options, successful chunker parameter copying, and repository reopening.
<!-- END_FILE_RESEARCH: sources/sync-backup/restic/cmd/restic/cmd_init.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/restic/cmd/restic/cmd_init_integration_test.go -->
# sources/sync-backup/restic/cmd/restic/cmd_init_integration_test.go

Purpose: shared `init` test helper plus coverage for copying chunker parameters from a secondary repository.

Important APIs/types/functions: `testRunInit` lowers KDF cost and disables polynomial checks for tests, invokes `runInit`, and creates junk files in repository subdirectories; `TestInitCopyChunkerParams` validates `InitOptions.SecondaryRepoOptions` behavior.

Control flow and state: the helper creates a real local test repository and intentionally adds temporary junk files under index/snapshots/keys/locks/data to ensure later commands tolerate unknown files. The copy test initializes two repos, first expecting failure without `CopyChunkerParameters`, then success with it, then opens both repos to compare config polynomials.

Dependencies and integration points: relies on `withTestEnvironment`, `global.OpenRepository`, repository test hooks, and progress printers.

Risks: test code mutates repository directories directly, so it assumes local backend layout. It does not test JSON output or repository-version parsing.

Test signals: validates guardrail for secondary options and the exact config-level chunker polynomial copy.
<!-- END_FILE_RESEARCH: sources/sync-backup/restic/cmd/restic/cmd_init_integration_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/restic/cmd/restic/cmd_key.go -->
# sources/sync-backup/restic/cmd/restic/cmd_key.go

Purpose: registers the parent `restic key` command and its key-management subcommands.

Important APIs/types/functions: `newKeyCommand` creates a cobra command with subcommands from `newKeyListCommand`, `newKeyAddCommand`, `newKeyRemoveCommand`, and `newKeyPasswdCommand`.

Control flow and state: the parent command does not itself open repositories or mutate state; all behavior is delegated to subcommands.

Dependencies and integration points: integrates with command grouping and cobra's command hierarchy. The child commands share repository key operations from `internal/repository`.

Risks: missing child registration would silently remove key functionality from the CLI. Parent has no `RunE`, so invoking `restic key` depends on cobra help/default behavior.

Test signals: key integration tests exercise child commands and flags tests parse root command children.
<!-- END_FILE_RESEARCH: sources/sync-backup/restic/cmd/restic/cmd_key.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/restic/cmd/restic/cmd_key_add.go -->
# sources/sync-backup/restic/cmd/restic/cmd_key_add.go

Purpose: implements `restic key add`, adding another password/key record to a repository.

Important APIs/types/functions: `KeyAddOptions`; `runKeyAdd`; `addKey`; `getNewPassword`; `switchToNewKeyAndRemoveIfBroken`; test-only `testKeyNewPassword`.

Control flow and state: `runKeyAdd` rejects arguments, opens the repository with an append lock, gets a new password from a test override, `--new-insecure-no-password`, `--new-password-file`, or interactive double prompt, then calls `repository.AddKey` with current key material. It immediately searches the new key; if validation fails it removes the broken key. Persistent state is a new key file, with rollback attempt on failure.

Dependencies and integration points: uses global password loading/prompting and repository key APIs. Append lock permits adding key data without exclusive snapshot mutation.

Risks: empty-password behavior is intentionally gated. The test override is global package state and must be reset. Rollback ignores remove errors, so a broken key may remain if backend removal fails.

Test signals: key integration tests cover adding normal keys, username/hostname metadata, invalid option combinations, empty password policy, empty-password opt-in, and backend-corruption failure recovery.
<!-- END_FILE_RESEARCH: sources/sync-backup/restic/cmd/restic/cmd_key_add.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/restic/cmd/restic/cmd_key_integration_test.go -->
# sources/sync-backup/restic/cmd/restic/cmd_key_integration_test.go

Purpose: end-to-end integration tests for key list/add/passwd/remove behavior and error handling.

Important APIs/types/functions: helpers `testRunKeyListOtherIDs`, `testRunKeyAddNewKey`, `testRunKeyAddNewKeyUserHost`, `testRunKeyPasswd`, `testRunKeyPasswdUserHost`, `testRunKeyRemove`; `emptySaveBackend` corrupts saved key payloads.

Control flow and state: tests initialize repositories, rotate passwords, add keys, remove all non-current keys, reopen with changed passwords, and run `check`. Metadata tests inspect loaded key username/hostname. Failure tests use backend hooks to save empty key files, ensuring passwd/add failures do not break existing access.

Dependencies and integration points: depends on global terminal helpers, repository key loading/searching, backend wrappers, and `testKeyNewPassword`.

Risks: package-global password override requires careful defers. Regex extraction in `testRunKeyListOtherIDs` is coupled to text table formatting. Backend corruption tests cover only one failure shape.

Test signals: strong coverage for key lifecycle, invalid args, empty-password policy, current-key preservation, and repository accessibility after failed key writes.
<!-- END_FILE_RESEARCH: sources/sync-backup/restic/cmd/restic/cmd_key_integration_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/restic/cmd/restic/cmd_key_list.go -->
# sources/sync-backup/restic/cmd/restic/cmd_key_list.go

Purpose: implements `restic key list`, listing repository key metadata and identifying the active key.

Important APIs/types/functions: `runKeyList`; `listKeys`; local `keyInfo` struct with JSON fields; table output setup.

Control flow and state: command rejects arguments, opens with a read lock, then `restic.ParallelList` enumerates key files. Each key is loaded; load errors are printed and skipped. A mutex protects concurrent append to the result slice. Output is JSON array or a table with current-key marker.

Dependencies and integration points: uses `repository.LoadKey`, `restic.KeyFile`, `restic.ParallelList`, terminal/table packages, and repository connection count.

Risks: skipped load errors mean partial output can still return success. Concurrent listing yields nondeterministic key order, which tests avoid by parsing IDs.

Test signals: key integration tests rely on list output to discover removable non-current key IDs and verify command accepts no arguments.
<!-- END_FILE_RESEARCH: sources/sync-backup/restic/cmd/restic/cmd_key_list.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/restic/cmd/restic/cmd_key_passwd.go -->
# sources/sync-backup/restic/cmd/restic/cmd_key_passwd.go

Purpose: implements `restic key passwd`, replacing the currently used key/password with a newly created key and removing the old one.

Important APIs/types/functions: `KeyPasswdOptions` embeds `KeyAddOptions`; `runKeyPasswd`; `changePassword`.

Control flow and state: rejects positional arguments, opens repository under an exclusive lock, obtains the new password through the same path as key add, creates a new key from current key material, records old key ID, validates access through the new key, removes the old key, and prints the new key ID. Persistent state changes include one new key file and deletion of the old key file.

Dependencies and integration points: reuses `getNewPassword` and `switchToNewKeyAndRemoveIfBroken`; uses repository `AddKey` and `RemoveKey`.

Risks: failure after new key creation but before old key removal can leave multiple valid keys. Failure in key validation attempts rollback. Exclusive lock is appropriate because this command removes a key.

Test signals: key integration tests cover password rotation, username/hostname metadata, invalid args, and corrupted save failure with old password still usable.
<!-- END_FILE_RESEARCH: sources/sync-backup/restic/cmd/restic/cmd_key_passwd.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/restic/cmd/restic/cmd_key_remove.go -->
# sources/sync-backup/restic/cmd/restic/cmd_key_remove.go

Purpose: implements `restic key remove [ID]`, deleting a non-current key from the repository.

Important APIs/types/functions: `runKeyRemove`; `deleteKey`.

Control flow and state: the command requires exactly one key ID/prefix, opens with an exclusive lock, resolves the key through `restic.Find`, rejects removal of the active key, removes the key file through `repository.RemoveKey`, and prints confirmation.

Dependencies and integration points: uses repository key storage, restic file prefix matching for `KeyFile`, progress terminal output, and exclusive locking.

Risks: ambiguous or invalid ID prefix behavior is delegated to `restic.Find`. Refusing current-key removal is critical to prevent self-lockout.

Test signals: key integration tests remove all non-current keys, verify repository accessibility with the last password, and cover missing/extra argument errors.
<!-- END_FILE_RESEARCH: sources/sync-backup/restic/cmd/restic/cmd_key_remove.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/restic/cmd/restic/cmd_list.go -->
# sources/sync-backup/restic/cmd/restic/cmd_list.go

Purpose: implements `restic list`, printing repository object IDs for `blobs`, `packs`, `index`, `snapshots`, `keys`, or `locks`.

Important APIs/types/functions: `newListCommand`; `runList`; cobra `ValidArgs` and exact-arg validation.

Control flow and state: `runList` checks one type argument, opens the repository with a read lock except lock listing can bypass locks, maps the type string to a `restic.FileType`, then lists IDs. For `blobs`, it iterates `repository.AllIndexBlobs` and prints blob type plus blob ID from the loaded indexes; for other types it calls `repo.List`.

Dependencies and integration points: depends on repository index functions, restic file-type constants, cobra argument validation, and terminal printer. It is used heavily by integration tests to discover snapshots/packs.

Risks: `list blobs` output shape differs from other types, which consumers must handle. Blob listing depends on a usable index and can surface index errors.

Test signals: list integration tests compare `list blobs` output against `repo.ListBlobs` after a backup.
<!-- END_FILE_RESEARCH: sources/sync-backup/restic/cmd/restic/cmd_list.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/restic/cmd/restic/cmd_list_integration_test.go -->
# sources/sync-backup/restic/cmd/restic/cmd_list_integration_test.go

Purpose: helper and integration coverage for `restic list`, especially blob enumeration.

Important APIs/types/functions: `testRunList`; `parseIDsFromReader`; `testListSnapshots`; `testListBlobs`; `TestListBlobs`.

Control flow and state: helpers capture stdout, parse either bare 64-character IDs or `type id` blob lines, and return `restic.IDs`. The blob test creates a backup, runs `list blobs`, builds an ID set, independently opens the repo, loads the index, calls `repo.ListBlobs`, and compares sets.

Dependencies and integration points: depends on backup test helpers, repository index loading, ID parsing, and stdout capture.

Risks: parser assumes any non-64-char line ends with an ID, so unrelated output could be misparsed. The test compares blob IDs but not blob type counts.

Test signals: validates that `runList("blobs")` sees the same blob IDs as the repository index API.
<!-- END_FILE_RESEARCH: sources/sync-backup/restic/cmd/restic/cmd_list_integration_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/restic/cmd/restic/cmd_ls.go -->
# sources/sync-backup/restic/cmd/restic/cmd_ls.go

Purpose: implements `restic ls`, listing files in a snapshot with text, JSON lines, or ncdu export output, optional path filters, recursion, and sorting.

Important APIs/types/functions: `LsOptions`; `lsPrinter` interface; `jsonLsPrinter`; `ncduLsPrinter`; `textLsPrinter`; `runLs`; `sortedPrinter`; `SortMode`. `lsNodeJSON` and `lsNcduNode` serialize nodes for machine formats.

Control flow and state: `runLs` validates snapshot argument, incompatible `--json/--ncdu/--sort/--reverse` combinations, and absolute path filters. It opens a read lock, memoizes snapshots, loads the index, selects an output printer, optionally wraps it in `sortedPrinter`, resolves latest/snapshot/subfolder with `SnapshotFilter.FindLatest`, then walks the tree. Two path predicates decide whether a node is inside requested dirs or on the path toward them; walker skips irrelevant directories. No repository mutation occurs.

Dependencies and integration points: uses `data.FindTreeDirectory`, `walker.Walk`, `fs.HasPathPrefix`, `formatNode`, global terminal/JSON mode, and restic snapshot filtering. Ncdu output follows ncdu JSON format.

Risks: sorted output collects all printed nodes in memory. Path filter semantics are absolute and slash-based. Prefix-directory callbacks are suppressed in JSON and sorted modes. Ncdu nesting relies on balanced `Node`/`LeaveDir` calls.

Test signals: integration tests cover ncdu validity, sort modes, and JSON lines; unit tests cover JSON/ncdu node serialization and ncdu tree formatting.
<!-- END_FILE_RESEARCH: sources/sync-backup/restic/cmd/restic/cmd_ls.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/restic/cmd/restic/cmd_ls_integration_test.go -->
# sources/sync-backup/restic/cmd/restic/cmd_ls_integration_test.go

Purpose: integration tests for `runLs` output modes over real test repositories.

Important APIs/types/functions: `testRunLsWithOpts`; `testRunLs`; `assertIsValidJSON`; `TestRunLsNcdu`; `TestRunLsSort`; `TestRunLsJson`.

Control flow and state: tests create backups from fixture data, then capture stdout from `runLs`. Ncdu cases verify valid top-level JSON for full and filtered listings. Sort tests compare exact text line order for size, extension, and default name order. JSON tests unmarshal the snapshot line and node lines and compare IDs and paths.

Dependencies and integration points: depends on backup/list helpers, `LsOptions`, `global.Options.JSON`, and restic fixture layout.

Risks: exact order/path assertions are fixture-coupled. JSON test uses a partial copy of output structs, which intentionally tracks public fields but can drift.

Test signals: confirms user-facing `ls` formats remain parseable and stable for common modes.
<!-- END_FILE_RESEARCH: sources/sync-backup/restic/cmd/restic/cmd_ls_integration_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/restic/cmd/restic/cmd_ls_test.go -->
# sources/sync-backup/restic/cmd/restic/cmd_ls_test.go

Purpose: unit tests for `ls` JSON node encoding and ncdu export formatting.

Important APIs/types/functions: `lsTestNode`; `lsTestNodes`; `TestLsNodeJSON`; `TestLsNcduNode`; `TestLsNcdu`.

Control flow and state: tests build synthetic `data.Node` values for regular files, empty files, symlinks, directories, and sticky/setuid/setgid modes. They assert exact JSON strings for restic JSON-lines nodes and exact ncdu node JSON, then build a small ncdu tree with `ncduLsPrinter`.

Dependencies and integration points: depends on `data.Node` fields, Go `os.FileMode`, JSON encoding, and restic test assertions.

Risks: exact JSON strings intentionally lock the wire format and will fail on field order or naming changes. Zero time and mode behavior is part of the contract.

Test signals: strong serialization regression coverage, including empty-file size emission and non-regular size omission.
<!-- END_FILE_RESEARCH: sources/sync-backup/restic/cmd/restic/cmd_ls_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/restic/cmd/restic/cmd_migrate.go -->
# sources/sync-backup/restic/cmd/restic/cmd_migrate.go

Purpose: implements `restic migrate`, listing available migrations or applying named migrations to a repository.

Important APIs/types/functions: `MigrateOptions`; `checkMigrations`; `applyMigrations`; `runMigrate`.

Control flow and state: `runMigrate` opens an exclusive lock. With no args it checks each `migrations.All` entry and prints applicable migrations. With names, it matches each migration, checks applicability, optionally continues with `--force`, runs repository integrity checks for migrations requiring them with `NoLock` because the exclusive lock is already held, applies the migration, prints status, and returns the first apply error after trying remaining migrations.

Dependencies and integration points: depends on `internal/migrations`, `runCheck`, restic repository interfaces, and progress output.

Risks: unknown migration names only print an error and do not affect `firsterr`. Forced migrations can run despite failed prechecks. RepoCheck migrations invoke a full check before mutation.

Test signals: no file-specific tests in this shard; coverage likely comes from migration package tests and command flag parsing.
<!-- END_FILE_RESEARCH: sources/sync-backup/restic/cmd/restic/cmd_migrate.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/restic/cmd/restic/cmd_mount.go -->
# sources/sync-backup/restic/cmd/restic/cmd_mount.go

Purpose: implements FUSE-backed `restic mount` on darwin/freebsd/linux, exposing snapshots read-only at a mountpoint.

Important APIs/types/functions: `registerMountCommand`; `MountOptions`; `runMount`; `validateMountpoint`; `checkMountpointOverlap`; `resolvePath`; `isInside`.

Control flow and state: validates time template and mountpoint argument, checks mountpoint existence, write/execute access, and local repository overlap. It opens a read lock, loads the index, creates read-only FUSE mount options including allow-other/default-permissions flags, constructs `fuse.NewRoot`, preloads snapshots via `ReadDirAll`, starts `fs.Serve` in a goroutine, and waits for context cancellation or serve completion. On cancellation it attempts unmount and returns `ErrOK`. No repository mutation occurs.

Dependencies and integration points: uses `github.com/anacrolix/fuse`, restic `internal/fuse`, local backend location parsing, unix access checks, snapshot filters, and debug logging.

Risks: FUSE lifecycle and unmount behavior are OS-sensitive. Overlap checks are critical to avoid deadlocks when mounting over/under a local repository. Path-template/time-template changes affect virtual directory layout.

Test signals: mount integration tests cover snapshot visibility, same-timestamp disambiguation, and overlap/symlink overlap detection.
<!-- END_FILE_RESEARCH: sources/sync-backup/restic/cmd/restic/cmd_mount.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/restic/cmd/restic/cmd_mount_disabled.go -->
# sources/sync-backup/restic/cmd/restic/cmd_mount_disabled.go

Purpose: build-tag fallback for platforms without mount support.

Important APIs/types/functions: `registerMountCommand` is a no-op under `!darwin && !freebsd && !linux`.

Control flow and state: no command is added, no repository is opened, and no state changes occur.

Dependencies and integration points: shares the same symbol as `cmd_mount.go` so root command registration can call `registerMountCommand` unconditionally across builds.

Risks: platform build tags must remain complementary with the enabled file. Unsupported platforms silently omit the command.

Test signals: no direct tests here; successful cross-platform builds and flags tests exercise command tree consistency.
<!-- END_FILE_RESEARCH: sources/sync-backup/restic/cmd/restic/cmd_mount_disabled.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/restic/cmd/restic/cmd_mount_integration_test.go -->
# sources/sync-backup/restic/cmd/restic/cmd_mount_integration_test.go

Purpose: FUSE integration coverage for `restic mount` and local repository/mountpoint overlap validation.

Important APIs/types/functions: `waitForMount`; `testRunMount`; `testRunUmount`; `checkSnapshots`; `TestMount`; `TestCheckMountpointOverlap`; `TestCheckMountpointOverlapSymlink`; `TestMountSameTimestamps`.

Control flow and state: tests run mount in a goroutine, poll for the virtual `snapshots` directory, inspect virtual snapshot names including `latest`, then unmount and wait. Backup sequences create zero, one, two, and three snapshots to verify virtual directory counts. Overlap tests call `checkMountpointOverlap` directly with equal, nested, sibling, prefix, and symlink paths.

Dependencies and integration points: requires `rtest.RunFuseTest`, anacrolix fuse unmount, debug logging, snapshot loading, and integration environment helpers.

Risks: timing and OS FUSE availability can make tests flaky or skipped. Virtual snapshot naming is tied to RFC3339 defaults and duplicate timestamp suffixing.

Test signals: validates the core mount lifecycle and the deadlock-prevention overlap guard.
<!-- END_FILE_RESEARCH: sources/sync-backup/restic/cmd/restic/cmd_mount_integration_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/restic/cmd/restic/cmd_options.go -->
# sources/sync-backup/restic/cmd/restic/cmd_options.go

Purpose: implements `restic options`, printing the list of extended options.

Important APIs/types/functions: `newOptionsCommand`; inline `Run` handler; `options.List`.

Control flow and state: command prints a header, computes the maximum `namespace.name` width, then prints each extended option with aligned name and description. It does not open a repository or mutate state.

Dependencies and integration points: depends on `internal/options` as the source of available extended options and `globalOptions.Term.Print` for output.

Risks: output order and alignment depend on `options.List`. There is no JSON mode handling; it is plain text.

Test signals: root flag parsing tests cover command construction; no direct output test in this shard.
<!-- END_FILE_RESEARCH: sources/sync-backup/restic/cmd/restic/cmd_options.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/restic/cmd/restic/cmd_prune.go -->
# sources/sync-backup/restic/cmd/restic/cmd_prune.go

Purpose: implements `restic prune`, planning and executing repository cleanup of unneeded data.

Important APIs/types/functions: `PruneOptions`; `AddFlags`; `AddLimitedFlags`; `verifyPruneOptions`; `runPrune`; `runPruneWithRepo`; `printPruneStats`; `getUsedBlobs`.

Control flow and state: option verification parses max unused space, max repack size, small-pack threshold, and unsafe no-space recovery. `runPrune` rejects incompatible compression/no-lock settings, opens an exclusive lock unless dry-run/no-lock is used, validates unsafe recovery by exact repository ID, and calls `runPruneWithRepo`. The latter loads the index, builds `repository.PruneOptions`, calls `repository.PlanPrune` with a callback that finds used blobs from snapshots, prints stats or JSON, triggers GC, then executes the plan. Persistent mutations can include repacking, deleting packs/indexes, and cleaning unreferenced data unless dry-run.

Dependencies and integration points: deeply depends on `internal/repository` prune planner/executor, `data.ForAllSnapshots`, `data.FindUsedBlobs`, UI byte parsing/formatting, and locks.

Risks: destructive behavior makes lock and option validation important. Unsafe recovery disables repacking and requires exact repo ID. Percent parsing forbids values >=100. JSON output bypasses text stats.

Test signals: prune integration tests cover max-unused variants, unsafe recovery mode, damaged and edge-case repos, small-pack threshold, and JSON stats.
<!-- END_FILE_RESEARCH: sources/sync-backup/restic/cmd/restic/cmd_prune.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/restic/cmd/restic/cmd_prune_integration_test.go -->
# sources/sync-backup/restic/cmd/restic/cmd_prune_integration_test.go

Purpose: broad integration coverage for prune behavior on normal, damaged, and edge-case repositories.

Important APIs/types/functions: `testRunPrune`; `testRunPruneMustFail`; `testRunPruneOutput`; `createPrunableRepo`; `testRunForgetJSON`; `testPrune`; `TestPruneWithDamagedRepository`; `TestEdgeCaseRepos`; `testEdgeCaseRepo`; `TestPruneRepackSmallerThanSmoke`; `TestPruneJSON`.

Control flow and state: tests build repositories with forgotten snapshots to create unused data, run prune with multiple policies, then run check. Edge cases load fixture repositories with missing indexes, missing blobs, unused missing data, unreferenced data, obsolete indexes, mixed packs, and duplicate blobs. JSON test captures `repository.PruneStats`.

Dependencies and integration points: uses backend list-once hooks, forget/check helpers, fixture tar repositories, and repository error values such as `ErrPacksMissing`.

Risks: fixture expectations encode repository invariants. Some tests deliberately manipulate packs and rely on local backend behavior.

Test signals: high-value coverage for prune safety and repair boundaries, including cases prune must not repair.
<!-- END_FILE_RESEARCH: sources/sync-backup/restic/cmd/restic/cmd_prune_integration_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/restic/cmd/restic/cmd_recover.go -->
# sources/sync-backup/restic/cmd/restic/cmd_recover.go

Purpose: implements `restic recover`, creating a new snapshot from unreferenced tree roots found in raw repository data.

Important APIs/types/functions: `newRecoverCommand`; `runRecover`; `createSnapshot`.

Control flow and state: obtains hostname, opens exclusive lock, memoizes snapshot list, repairs index completeness, loads index, collects all tree blob IDs as potential roots, loads every tree and marks subtree references, marks snapshot root trees as referenced, then saves a synthetic tree containing one directory per unreferenced root. If roots exist, `createSnapshot` saves a `/recover` snapshot tagged `recovered`; otherwise it prints no snapshot to write.

Dependencies and integration points: uses `repository.RepairIndex`, `repo.ListBlobs`, `data.LoadTree`, `data.ForAllSnapshots`, `data.NewTreeWriter`, and `data.SaveSnapshot`.

Risks: tree load failures are logged and skipped, possibly leaving roots classified conservatively. Recovery can expose orphan data but cannot reconstruct original names above root boundaries. It mutates repository by writing tree and snapshot files.

Test signals: recover integration test forgets a snapshot, runs recover, checks one new snapshot exists, and verifies the old root tree is reachable.
<!-- END_FILE_RESEARCH: sources/sync-backup/restic/cmd/restic/cmd_recover.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/restic/cmd/restic/cmd_recover_integration_test.go -->
# sources/sync-backup/restic/cmd/restic/cmd_recover_integration_test.go

Purpose: integration test for recovering a forgotten snapshot's root tree.

Important APIs/types/functions: `testRunRecover`; `TestRecover`.

Control flow and state: the test creates backup data, backs it up, loads the snapshot metadata, forgets the snapshot, verifies snapshot list is empty, runs recover, verifies one snapshot exists, runs check, and cats the recovered snapshot path to the original tree ID.

Dependencies and integration points: uses backup/forget/list/check/cat helpers and the shared test environment. It disables the default list-once backend hook because recover/list operations may enumerate index files repeatedly.

Risks: focuses on forgotten snapshot recovery, not partially corrupt tree cases. Success depends on unpruned tree data remaining in packs.

Test signals: proves recover can create a new snapshot exposing the original forgotten root tree.
<!-- END_FILE_RESEARCH: sources/sync-backup/restic/cmd/restic/cmd_recover_integration_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/restic/cmd/restic/cmd_repair.go -->
# sources/sync-backup/restic/cmd/restic/cmd_repair.go

Purpose: registers the parent `restic repair` command and its repair subcommands.

Important APIs/types/functions: `newRepairCommand` registers `repair index`, `repair packs`, and `repair snapshots`.

Control flow and state: parent command only defines help text and command grouping; all repository mutation occurs in child subcommands.

Dependencies and integration points: integrates repair functionality into the cobra command tree.

Risks: missing subcommand registration removes repair tools. The parent has no run behavior.

Test signals: repair subcommand integration tests cover child behavior; flags tests parse command tree help.
<!-- END_FILE_RESEARCH: sources/sync-backup/restic/cmd/restic/cmd_repair.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/restic/cmd/restic/cmd_repair_index.go -->
# sources/sync-backup/restic/cmd/restic/cmd_repair_index.go

Purpose: implements `restic repair index` and deprecated `rebuild-index`, rebuilding repository indexes from pack files.

Important APIs/types/functions: `RepairIndexOptions`; `newRepairIndexCommand`; `newRebuildIndexCommand`; `runRebuildIndex`.

Control flow and state: command opens repository with an exclusive lock and calls `repository.RepairIndex`, passing `ReadAllPacks`. It prints `done` on success. The deprecated command creates a separate options capture to avoid sharing state with replacement command.

Dependencies and integration points: repository index repair logic lives in `internal/repository`; command exposes it with locking and progress.

Risks: index rebuild is repository-mutating and can fail in append-only backends when obsolete indexes cannot be removed. `--read-all-packs` is more expensive but can recover from worse index damage.

Test signals: integration tests verify duplicate-pack index repair, damaged index reads, and append-only removal failure.
<!-- END_FILE_RESEARCH: sources/sync-backup/restic/cmd/restic/cmd_repair_index.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/restic/cmd/restic/cmd_repair_index_integration_test.go -->
# sources/sync-backup/restic/cmd/restic/cmd_repair_index_integration_test.go

Purpose: integration coverage for index rebuild and related failure modes.

Important APIs/types/functions: `testRunRebuildIndex`; `testRebuildIndex`; `indexErrorBackend`; `errorReadCloser`; `appendOnlyBackend`; `TestRebuildIndex`; `TestRebuildIndexDamage`; `TestRebuildIndexFailsOnAppendOnly`.

Control flow and state: tests load a fixture repo with duplicate packs in indexes, verify `check` suggests `restic repair index`, run rebuild, and verify check becomes silent. Damage test corrupts the first index during load to ensure repair can tolerate bad index reads. Append-only test wraps backend removal to fail and expects rebuild failure.

Dependencies and integration points: uses backend wrappers, checker output, fixture tar repos, and repository commands.

Risks: output substring checks are coupled to checker messages. Backend wrappers simulate only specific corruption/removal failures.

Test signals: validates that repair index fixes duplicated index entries, handles index read corruption, and reports append-only constraints.
<!-- END_FILE_RESEARCH: sources/sync-backup/restic/cmd/restic/cmd_repair_index_integration_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/restic/cmd/restic/cmd_repair_packs.go -->
# sources/sync-backup/restic/cmd/restic/cmd_repair_packs.go

Purpose: implements `restic repair packs`, salvaging intact blobs from specified damaged pack files.

Important APIs/types/functions: `newRepairPacksCommand`; `runRepairPacks`.

Control flow and state: parses each argument as a full restic ID into an ID set and rejects empty input. It opens an exclusive lock, loads the index, saves raw backup copies of each target pack into current working directory as `pack-<id>` with exclusive create, then calls `repository.RepairPacks`. It prints a follow-up hint to run `repair snapshots --forget`.

Dependencies and integration points: uses raw pack loading, local filesystem backup writes, repository pack repair, and index state.

Risks: backup files are written to the process CWD and fail if names already exist. If `LoadRaw` returns nil, the load error is returned. Full ID parsing rejects short IDs. Command mutates repository by removing/replacing damaged pack references.

Test signals: no direct integration test file in this shard, but repair snapshots tests create damaged pack scenarios after index rebuild.
<!-- END_FILE_RESEARCH: sources/sync-backup/restic/cmd/restic/cmd_repair_packs.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/restic/cmd/restic/cmd_repair_snapshots.go -->
# sources/sync-backup/restic/cmd/restic/cmd_repair_snapshots.go

Purpose: implements `restic repair snapshots`, rewriting broken snapshots with unreadable trees, invalid nodes, or missing file blobs removed/fixed.

Important APIs/types/functions: `RepairOptions`; `runRepairSnapshots`; walker `TreeRewriter`; shared `filterAndReplaceSnapshot` from rewrite command.

Control flow and state: opens an exclusive lock, using dry-run as no-lock allowance, memoizes snapshots, loads index, builds a tree rewriter. File nodes with invalid types are removed; missing content blobs are dropped and file size recalculated; unreadable subtrees become empty directories, while unreadable root trees cause snapshot removal. For each filtered snapshot it calls `filterAndReplaceSnapshot` with tag `repaired`, optional `--forget`, and no metadata changes. It reports modified count.

Dependencies and integration points: depends on snapshot filtering, repository blob lookup, `walker.NewTreeRewriter`, and rewrite's snapshot replacement helper.

Risks: command intentionally causes data loss to make snapshots consistent. It requires a correct index first. In-place node mutation during rewrite must not leak unexpected state. Root tree failures can delete snapshots.

Test signals: integration tests cover lost data blobs, lost subtrees, lost root trees, and intact snapshots remaining unchanged.
<!-- END_FILE_RESEARCH: sources/sync-backup/restic/cmd/restic/cmd_repair_snapshots.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/restic/cmd/restic/cmd_repair_snapshots_integration_test.go -->
# sources/sync-backup/restic/cmd/restic/cmd_repair_snapshots_integration_test.go

Purpose: integration tests for snapshot repair after data or tree loss.

Important APIs/types/functions: `testRunRepairSnapshot`; `createRandomFile`; `TestRepairSnapshotsWithLostData`; `TestRepairSnapshotsWithLostTree`; `TestRepairSnapshotsWithLostRootTree`; `TestRepairSnapshotsIntact`.

Control flow and state: tests generate deterministic random files, create backups, remove packs to simulate missing data/tree blobs, rebuild index, run repair snapshots with and without `--forget`, then verify snapshot counts and `check` outcomes. Intact test verifies no new snapshot is created when no changes are needed.

Dependencies and integration points: uses pack removal helpers, repair index helper, forget/check/list helpers, and deterministic file data generation.

Risks: direct pack deletion assumes local backend behavior. Tests focus on repository consistency, not detailed restored file contents after repair.

Test signals: strong validation that repair snapshots creates fixed snapshots, optionally deletes broken originals, and does not alter intact snapshots.
<!-- END_FILE_RESEARCH: sources/sync-backup/restic/cmd/restic/cmd_repair_snapshots_integration_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/restic/cmd/restic/cmd_restore.go -->
# sources/sync-backup/restic/cmd/restic/cmd_restore.go

Purpose: implements `restic restore`, extracting a snapshot or snapshot subfolder to a target directory with filtering, overwrite/delete behavior, sparse restore, verification, and xattr selection.

Important APIs/types/functions: `RestoreOptions`; `runRestore`; `getXattrSelectFilter`.

Control flow and state: collects include/exclude filters, validates one snapshot arg, target presence, mutually exclusive include/exclude and dry-run/verify, and guards `--target / --delete` unless filtered. It opens a read lock, resolves snapshot/latest/subfolder, loads index, creates a `restorer.Restorer`, attaches error/warn/info callbacks, configures file and xattr selection filters, restores to target, finishes progress, returns aggregate errors, and optionally verifies restored files. Repository state is read-only; filesystem target is mutated unless dry-run.

Dependencies and integration points: uses `internal/restorer`, restore UI progress, filter package, snapshot filtering, tree directory resolution, and global JSON mode.

Risks: destructive `--delete` needs the root-target guard. Include/exclude filter semantics affect both traversal and metadata restoration. Verification can surface post-restore errors. JSON mode suppresses info messages.

Test signals: restore integration tests cover include/exclude patterns and files, latest selection, full directory restore, permission errors, metadata on intermediate dirs, and default-layout repos.
<!-- END_FILE_RESEARCH: sources/sync-backup/restic/cmd/restic/cmd_restore.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/restic/cmd/restic/cmd_restore_integration_test.go -->
# sources/sync-backup/restic/cmd/restic/cmd_restore_integration_test.go

Purpose: integration tests for restore behavior, filters, latest selection, metadata handling, and layout compatibility.

Important APIs/types/functions: restore helper functions; `TestRestoreMustFailWhenUsingBothIncludesAndExcludes`; `TestRestoreIncludes`; `TestRestoreFilter`; `TestRestore`; `TestRestoreLatest`; `TestRestoreWithPermissionFailure`; `setZeroModTime`; `TestRestoreNoMetadataOnIgnoredIntermediateDirs`; `TestRestoreDefaultLayout`.

Control flow and state: tests create repositories and files, back up fixture data, restore into temp targets, then inspect filesystem sizes/existence/diffs. Include/exclude tests exercise inline and file-based patterns. Latest tests create multiple snapshots with different paths. Metadata test checks filtered intermediate directories do not get original metadata unless selected.

Dependencies and integration points: uses backup/check/list helpers, directory diff helpers, random data appending, syscall utimes, and fixture repos.

Risks: filesystem metadata tests can be OS-sensitive. Permission failure fixture assumes expected behavior of restore error handling.

Test signals: broad coverage for restore selection, output filesystem correctness, filter validation, and compatibility with older default layout repos.
<!-- END_FILE_RESEARCH: sources/sync-backup/restic/cmd/restic/cmd_restore_integration_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/restic/cmd/restic/cmd_rewrite.go -->
# sources/sync-backup/restic/cmd/restic/cmd_rewrite.go

Purpose: implements `restic rewrite`, creating replacement snapshots with files excluded/included, metadata changed, or summary records added.

Important APIs/types/functions: `snapshotMetadataArgs.convert`; `RewriteOptions`; `rewriteSnapshot`; `filterAndReplaceSnapshot`; `runRewrite`; `gatherIncludeFilters`; `gatherExcludeFilters`.

Control flow and state: `runRewrite` requires some action, rejects simultaneous include/exclude, opens append lock for additive rewrites or exclusive lock when `--forget` may remove originals, memoizes snapshots, loads index, then rewrites each filtered snapshot. `rewriteSnapshot` builds include/exclude walkers and optional summary generation. `filterAndReplaceSnapshot` uploads the new tree, handles empty results, compares tree/metadata/summary to skip no-ops, saves a new snapshot with `Original` set, adds a tag unless forgetting, applies metadata, and optionally removes the old snapshot.

Dependencies and integration points: depends on filter package, walker snapshot-size rewriter, repository blob uploader, data snapshot save/remove, and shared snapshot filter helper. Repair snapshots reuses `filterAndReplaceSnapshot`.

Risks: rewrite can duplicate snapshots or delete originals. Include mode keeps explicitly matched empty directories; include-nothing with `--forget` preserves original snapshot. Time parsing uses `global.TimeFormat` in local time. No-op detection must include summary equality.

Test signals: rewrite integration tests cover exclude/additive, unchanged no-op, replace with forget, metadata changes, summary generation, include modes, exclude files, contradiction, empty directory include, and include-nothing preservation.
<!-- END_FILE_RESEARCH: sources/sync-backup/restic/cmd/restic/cmd_rewrite.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/restic/cmd/restic/cmd_rewrite_integration_test.go -->
# sources/sync-backup/restic/cmd/restic/cmd_rewrite_integration_test.go

Purpose: integration coverage for snapshot rewrite features and edge cases.

Important APIs/types/functions: `testRunRewriteExclude`; `testRunRewriteWithOpts`; `testLsOutputContainsCount`; `createBasicRewriteRepo`; `createBasicRewriteRepoWithEmptyDirectory`; `getSnapshot`; tests for rewrite, no-op, replace, metadata, summary, include/exclude, contradictions, empty directory, and include nothing.

Control flow and state: tests create real snapshots, run rewrite with different options, inspect snapshot counts/IDs, load snapshots to compare summaries/metadata, use `ls` to verify retained paths, and run prune/check when old data becomes unused.

Dependencies and integration points: uses filter option structs, list/check/prune helpers, snapshot loading, and ls helpers.

Risks: several assertions depend on fixture file names and sizes. Helper `testRunRewriteWithOpts` currently asserts success before returning nil, so callers cannot inspect expected errors through it.

Test signals: validates rewrite correctness for additive and replacement modes, summary recalculation, metadata conversion, and include/exclude tree semantics.
<!-- END_FILE_RESEARCH: sources/sync-backup/restic/cmd/restic/cmd_rewrite_integration_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/restic/cmd/restic/cmd_self_update.go -->
# sources/sync-backup/restic/cmd/restic/cmd_self_update.go

Purpose: build-tagged implementation of `restic self-update`, downloading and replacing the restic binary when built with `selfupdate`.

Important APIs/types/functions: `registerSelfUpdateCommand`; `SelfUpdateOptions`; `runSelfUpdate`.

Control flow and state: if `--output` is absent, resolves the current executable. It validates that an existing output is a regular file or that the parent directory exists and is a directory, prints the target path, then calls `selfupdate.DownloadLatestStableRelease` with the current version and progress callback. Persistent state is the downloaded binary at the output path, potentially replacing the running executable.

Dependencies and integration points: uses `internal/selfupdate`, `os.Executable`, filesystem stat checks, and progress printer. Build tag `selfupdate` controls availability.

Risks: replacing the running binary is platform-sensitive. Output path validation avoids writing to directories or non-regular files but does not create missing parent directories. Network/signature behavior is delegated to `selfupdate`.

Test signals: no direct test in this shard; build-tag coverage and selfupdate package tests are expected.
<!-- END_FILE_RESEARCH: sources/sync-backup/restic/cmd/restic/cmd_self_update.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/restic/cmd/restic/cmd_self_update_disabled.go -->
# sources/sync-backup/restic/cmd/restic/cmd_self_update_disabled.go

Purpose: build-tag fallback when `selfupdate` is not enabled.

Important APIs/types/functions: no-op `registerSelfUpdateCommand`.

Control flow and state: no command is registered; no filesystem, network, or repository state is touched.

Dependencies and integration points: provides the same symbol as the enabled self-update file so root command setup can be build-tag agnostic.

Risks: build tags must remain mutually exclusive and exhaustive. Users of builds without `selfupdate` will not see the command.

Test signals: command tree construction and cross-build compilation are the main validation signals.
<!-- END_FILE_RESEARCH: sources/sync-backup/restic/cmd/restic/cmd_self_update_disabled.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/restic/cmd/restic/cmd_snapshots.go -->
# sources/sync-backup/restic/cmd/restic/cmd_snapshots.go

Purpose: implements `restic snapshots`, listing snapshots with filtering, grouping, latest limits, text tables, and JSON output.

Important APIs/types/functions: `SnapshotOptions`; `runSnapshots`; `filterLatestSnapshotsInGroup`; `PrintSnapshots`; `PrintSnapshotGroupHeader`; JSON wrapper types `Snapshot` and `SnapshotGroup`; `printSnapshotGroupJSON`.

Control flow and state: opens read lock, streams filtered snapshots, groups them by configured host/path/tag options, optionally keeps latest N per group, sorts lists newest-to-oldest for group storage then text output re-sorts oldest-to-newest. JSON emits either a flat snapshot array or grouped array; text prints optional group headers and tables with summary size when available. No repository mutation occurs.

Dependencies and integration points: uses `FindFilteredSnapshots`, `data.GroupSnapshots`, `data.SnapshotGroupByOptions`, table rendering, UI byte formatting, and global time formatting.

Risks: map iteration makes group order nondeterministic. Text output includes local timezone footer. Deprecated `--last` path remains for compatibility.

Test signals: integration test verifies JSON grouping by host and latest limit; unit test ensures empty JSON is `[]` rather than `null`.
<!-- END_FILE_RESEARCH: sources/sync-backup/restic/cmd/restic/cmd_snapshots.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/restic/cmd/restic/cmd_snapshots_integration_test.go -->
# sources/sync-backup/restic/cmd/restic/cmd_snapshots_integration_test.go

Purpose: integration coverage for snapshots JSON output, grouping, and latest filtering.

Important APIs/types/functions: `testRunSnapshots`; `TestSnapshotsGroupByAndLatest`.

Control flow and state: helper captures JSON snapshots and builds a map by ID plus newest pointer. The test creates two snapshots on the same host with different paths and increasing timestamps, runs `runSnapshots` in JSON mode with `GroupBy.Host` and `Latest: 1`, then asserts a single host group with no path/tag key and the second snapshot as the only entry.

Dependencies and integration points: uses backup helpers, snapshot map helpers, JSON structs from command code, and fixture data.

Risks: timestamp ordering depends on explicit one-second offset. JSON shape is part of the asserted contract.

Test signals: verifies grouping by host does not implicitly group by path and latest selection is per group.
<!-- END_FILE_RESEARCH: sources/sync-backup/restic/cmd/restic/cmd_snapshots_integration_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/restic/cmd/restic/cmd_snapshots_test.go -->
# sources/sync-backup/restic/cmd/restic/cmd_snapshots_test.go

Purpose: regression test for empty snapshots JSON output.

Important APIs/types/functions: `TestEmptySnapshotGroupJSON`.

Control flow and state: calls `printSnapshotGroupJSON` with a nil snapshot group map for both grouped and ungrouped modes and checks the trimmed output is `[]`.

Dependencies and integration points: uses `strings.Builder` and restic test assertions.

Risks: small but important JSON compatibility contract; nil slices/maps must encode as empty arrays due explicit construction in implementation.

Test signals: protects regression for issue where empty output could be `null`.
<!-- END_FILE_RESEARCH: sources/sync-backup/restic/cmd/restic/cmd_snapshots_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/restic/cmd/restic/cmd_stats.go -->
# sources/sync-backup/restic/cmd/restic/cmd_stats.go

Purpose: implements `restic stats`, walking snapshots or raw blobs to report repository size/count statistics in several counting modes.

Important APIs/types/functions: `StatsOptions`; `runStats`; `statsWalkSnapshot`; `statsWalkTree`; `makeFileIDByContents`; `verifyStatsInput`; `statsContainer`; count-mode constants; debug helpers; `sizeHistogram`.

Control flow and state: validates mode, opens read lock, memoizes snapshots, loads index, optionally runs debug histograms. Normal flow collects filtered snapshots, creates progress, walks each snapshot. `restore-size` counts restored file sizes with hardlink de-duplication; `files-by-contents` hashes content blob sequences; `blobs-per-file` counts unique blob references per path; `raw-data` uses `data.FindUsedBlobs` then looks up ciphertext and uncompressed sizes. Output is JSON `statsContainer` or text summary. No repository mutation occurs.

Dependencies and integration points: uses walker, restorer hardlink index, repository blob lookup, chunker/repository size limits for histograms, stats UI progress, and table rendering.

Risks: `makeFileIDByContents` only considers content IDs, so metadata differences are ignored by design. Raw-data compression metrics depend on repo version and index metadata. Blob lookup failures abort. Debug mode is accepted but not listed in public shell completion.

Test signals: stats unit tests cover histogram construction, bucket insertion/oversized values, and string formatting.
<!-- END_FILE_RESEARCH: sources/sync-backup/restic/cmd/restic/cmd_stats.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/restic/cmd/restic/cmd_stats_test.go -->
# sources/sync-backup/restic/cmd/restic/cmd_stats_test.go

Purpose: unit tests for the `sizeHistogram` helper used by stats debug output.

Important APIs/types/functions: `TestSizeHistogramNew`; `TestSizeHistogramAdd`; `TestSizeHistogramString`.

Control flow and state: tests construct a histogram with limit 42, verify bucket layout, add sizes 0 through 44 to assert counts/total/oversized, and compare formatted output for overflow and zero-inclusive cases.

Dependencies and integration points: uses restic test equality helpers and `ui.FormatBytes` indirectly via `String`.

Risks: exact string assertions tie the debug table format to tests. Main stats counting modes are not covered here.

Test signals: protects bucket boundary behavior, oversized tracking, and human-readable debug formatting.
<!-- END_FILE_RESEARCH: sources/sync-backup/restic/cmd/restic/cmd_stats_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/restic/cmd/restic/cmd_tag.go -->
# sources/sync-backup/restic/cmd/restic/cmd_tag.go

Purpose: implements `restic tag`, modifying tags on selected snapshots by setting, adding, or removing tags.

Important APIs/types/functions: `TagOptions`; JSON structs `changedSnapshot` and `changedSnapshotsSummary`; `changeTags`; `runTag`.

Control flow and state: validates that some tag action is requested and `--set` is not combined with add/remove, opens exclusive lock, chooses text or JSON print callbacks, iterates filtered snapshots, mutates snapshot tags, preserves original snapshot ID, saves a new snapshot file, removes the old snapshot file, and prints a changed summary. Setting a single empty tag means no tags.

Dependencies and integration points: uses `data.TagLists`, snapshot filtering, repository snapshot save/remove, debug logging, and JSON terminal output.

Risks: command rewrites snapshot metadata by creating new IDs, so consumers must follow `Original`. Errors per snapshot are printed and ignored, allowing partial success. Tag order is determined by `data.Snapshot` helpers.

Test signals: tag integration test covers set, add, remove, remove all, original ID preservation, and repository check after each mutation.
<!-- END_FILE_RESEARCH: sources/sync-backup/restic/cmd/restic/cmd_tag.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/restic/cmd/restic/cmd_tag_integration_test.go -->
# sources/sync-backup/restic/cmd/restic/cmd_tag_integration_test.go

Purpose: integration coverage for snapshot tag mutation lifecycle.

Important APIs/types/functions: `testRunTag`; `TestTag`.

Control flow and state: creates a repository and backup, verifies no initial tags/original ID, then runs tag set, add, remove, combined add/remove-all, and set-empty operations. After each mutation it runs check and reloads newest snapshot through `testRunSnapshots`, asserting tags and `Original` ID remain tied to the first snapshot.

Dependencies and integration points: uses `data.TagLists`, backup/check/snapshots helpers, and test assertions.

Risks: assumes newest snapshot after tag rewrite is the modified one. Does not cover JSON output or invalid option combinations.

Test signals: validates user-visible tag semantics and snapshot lineage preservation.
<!-- END_FILE_RESEARCH: sources/sync-backup/restic/cmd/restic/cmd_tag_integration_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/restic/cmd/restic/cmd_unlock.go -->
# sources/sync-backup/restic/cmd/restic/cmd_unlock.go

Purpose: implements `restic unlock`, removing stale locks or all locks from a repository.

Important APIs/types/functions: `UnlockOptions`; `runUnlock`.

Control flow and state: opens the repository without taking a standard lock via `global.OpenRepository`, selects `repository.RemoveStaleLocks` or `repository.RemoveAllLocks` based on `--remove-all`, runs it, and prints the count when nonzero. Persistent state is deletion of lock files.

Dependencies and integration points: uses repository lock cleanup functions, global repository open, and terminal progress printer.

Risks: `--remove-all` can remove active locks and should be used carefully. Append-only server support is documented in help and depends on repository cleanup implementation.

Test signals: no direct test in this shard; lock behavior is likely covered elsewhere.
<!-- END_FILE_RESEARCH: sources/sync-backup/restic/cmd/restic/cmd_unlock.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/restic/cmd/restic/cmd_version.go -->
# sources/sync-backup/restic/cmd/restic/cmd_version.go

Purpose: implements `restic version`, printing version and build runtime information.

Important APIs/types/functions: `newVersionCommand`; local `jsonVersion` struct.

Control flow and state: command does not open a repository. In JSON mode it encodes `message_type`, restic version, Go version, GOOS, and GOARCH; otherwise it prints a text line with the same runtime data.

Dependencies and integration points: uses `global.Version`, Go `runtime`, JSON encoder, terminal output, and progress printer for JSON encode errors.

Risks: JSON encode errors are printed but do not affect command return because cobra `Run` has no error return. Output is part of CLI compatibility.

Test signals: no direct tests in this shard; flags tests exercise command parsing.
<!-- END_FILE_RESEARCH: sources/sync-backup/restic/cmd/restic/cmd_version.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/restic/cmd/restic/doc.go -->
# sources/sync-backup/restic/cmd/restic/doc.go

Purpose: package documentation file declaring that this package contains the restic executable code.

Important APIs/types/functions: package comment and `package main` declaration only.

Control flow and state: no runtime behavior and no state.

Dependencies and integration points: contributes package documentation to Go tooling.

Risks: none beyond documentation drift.

Test signals: compilation is the only relevant signal.
<!-- END_FILE_RESEARCH: sources/sync-backup/restic/cmd/restic/doc.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/restic/cmd/restic/exclude.go -->
# sources/sync-backup/restic/cmd/restic/exclude.go

Purpose: provides a reject filter that excludes restic's cache directory from archiving.

Important APIs/types/functions: `rejectResticCache(repo *repository.Repository)`.

Control flow and state: if repository cache is nil, returns a function that never rejects. Otherwise it reads `repo.Cache().BaseDir`, errors if empty, and returns a predicate that rejects items having the cache base as a path prefix while logging the rejection.

Dependencies and integration points: uses archiver reject function type, repository cache, `fs.HasPathPrefix`, debug logging, and restic errors.

Risks: path-prefix direction must remain correct to avoid backing up cache contents or rejecting unrelated paths. Empty cache base is treated as an error to avoid matching everything.

Test signals: no direct tests in this shard; backup behavior likely exercises it.
<!-- END_FILE_RESEARCH: sources/sync-backup/restic/cmd/restic/exclude.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/restic/cmd/restic/find.go -->
# sources/sync-backup/restic/cmd/restic/find.go

Purpose: centralizes snapshot filter flag registration, RESTIC_HOST defaulting, and filtered snapshot iteration.

Important APIs/types/functions: `initMultiSnapshotFilter`; `initSingleSnapshotFilter`; `finalizeSnapshotFilter`; `FindFilteredSnapshots`.

Control flow and state: flag helpers register host/tag/path filters for multi-snapshot and single-snapshot commands. `finalizeSnapshotFilter` applies `RESTIC_HOST` only when host flags were not set and treats an explicit single empty host as no host filter. `FindFilteredSnapshots` starts a goroutine, memoizes snapshot listing, delegates to `SnapshotFilter.FindAll`, logs per-snapshot errors, and sends successful snapshots on a channel while honoring context cancellation.

Dependencies and integration points: used by ls, restore, snapshots, stats, tag, rewrite, repair snapshots, and mount. Depends on pflag, `data.SnapshotFilter`, restic lister/loader interfaces, and progress printer.

Risks: goroutine logs errors rather than returning them to callers, so commands must check `ctx.Err` but cannot see all load failures as errors. Host defaulting semantics are subtle and user-facing.

Test signals: `find_test.go` covers RESTIC_HOST and explicit host flag combinations.
<!-- END_FILE_RESEARCH: sources/sync-backup/restic/cmd/restic/find.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/restic/cmd/restic/find_test.go -->
# sources/sync-backup/restic/cmd/restic/find_test.go

Purpose: unit tests for snapshot host filter finalization.

Important APIs/types/functions: `TestSnapshotFilter`.

Control flow and state: table-driven cases set `RESTIC_HOST`, parse flags through both single and multi snapshot filter initializers, call `finalizeSnapshotFilter`, and compare resulting `Hosts`.

Dependencies and integration points: uses pflag, `data.SnapshotFilter`, and restic test assertions.

Risks: only host finalization is tested; tag/path filtering and `FindFilteredSnapshots` channel behavior are not covered here.

Test signals: protects semantics that environment default applies only when the host flag is absent, and `--host ""` clears the default.
<!-- END_FILE_RESEARCH: sources/sync-backup/restic/cmd/restic/find_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/restic/cmd/restic/flags_test.go -->
# sources/sync-backup/restic/cmd/restic/flags_test.go

Purpose: smoke test ensuring command flags do not panic or conflict during help parsing.

Important APIs/types/functions: `TestFlags`.

Control flow and state: iterates immediate root command children, discards flag output, calls `ParseFlags(["--help"])`, treats `pflag: help requested` as success, and fails on other errors.

Dependencies and integration points: depends on `newRootCommand` and global options. It indirectly exercises command construction and shorthand registration.

Risks: only immediate commands are parsed, so nested subcommand conflicts may need separate coverage if not exposed through root children.

Test signals: catches duplicate shorthand definitions and command setup panics.
<!-- END_FILE_RESEARCH: sources/sync-backup/restic/cmd/restic/flags_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/restic/cmd/restic/format.go -->
# sources/sync-backup/restic/cmd/restic/format.go

Purpose: formats snapshot tree nodes for text `ls` output.

Important APIs/types/functions: `formatNode(path string, n *data.Node, long bool, human bool) string`.

Control flow and state: short mode returns the path only. Long mode maps restic node types to Go file mode bits, formats size as raw decimal or human-readable, appends symlink target when applicable, and returns mode, UID, GID, size, local modtime, path, and target.

Dependencies and integration points: used by `textLsPrinter` in `cmd_ls.go`; depends on `data.Node`, `os.FileMode`, `global.TimeFormat`, and `ui.FormatBytes`.

Risks: local timezone affects output. Device/fifo/socket type mode mapping must match expected CLI conventions. Human-readable width differs from raw width.

Test signals: `format_test.go` covers short, long raw, and long human-readable file output with UTC timezone forced.
<!-- END_FILE_RESEARCH: sources/sync-backup/restic/cmd/restic/format.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/restic/cmd/restic/format_test.go -->
# sources/sync-backup/restic/cmd/restic/format_test.go

Purpose: unit tests for `formatNode`.

Important APIs/types/functions: `TestFormatNode`.

Control flow and state: temporarily forces `time.Local` to UTC, constructs a file node, and checks output for non-long path-only mode, long raw-size mode, and long human-readable mode.

Dependencies and integration points: uses `data.Node`, time formatting, and restic test equality.

Risks: only regular file formatting is covered; symlinks, dirs, devices, fifos, and sockets are not tested here.

Test signals: protects the basic text `ls -l` output shape and stable timestamp formatting under UTC.
<!-- END_FILE_RESEARCH: sources/sync-backup/restic/cmd/restic/format_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/restic/cmd/restic/integration_filter_pattern_test.go -->
# sources/sync-backup/restic/cmd/restic/integration_filter_pattern_test.go

Purpose: integration tests that invalid filter patterns are rejected consistently by backup and restore commands.

Important APIs/types/functions: `TestBackupFailsWhenUsingInvalidPatterns`; `TestBackupFailsWhenUsingInvalidPatternsFromFile`; `TestRestoreFailsWhenUsingInvalidPatterns`; `TestRestoreFailsWhenUsingInvalidPatternsFromFile`.

Control flow and state: tests initialize repos, pass invalid include/exclude glob patterns inline or via pattern files, call backup/restore helpers expecting failure, and compare exact fatal error strings for each flag variant, including case-insensitive flags.

Dependencies and integration points: uses filter option structs, backup and restore command paths, temp files, and test environment setup.

Risks: exact error string comparisons are intentionally strict but can require updates when validation wording changes. Restore pattern tests may fail before snapshot lookup/target validation because filter collection happens first.

Test signals: validates command-layer propagation of filter validation errors and correct attribution to the relevant flag.
<!-- END_FILE_RESEARCH: sources/sync-backup/restic/cmd/restic/integration_filter_pattern_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/restic/cmd/restic/integration_helpers_test.go -->
# sources/sync-backup/restic/cmd/restic/integration_helpers_test.go

Purpose: shared integration-test support for command tests in this package.

Important APIs/types/functions: `dirEntry`; `walkDir`; `directoriesContentsDiff`; `dirStats`; `testEnvironment`; `withTestEnvironment`; `testSetupBackupData`; `listPacks`; `listTreePacks`; `captureBackend`; `removePacks`; `removePacksExcept`; `loadSnapshotMap`; `lastSnapshot`; `testLoadSnapshot`; `appendRandomData`; `testFileSize`; `withCaptureStdout`; `withTermStatus`; `withTermStatusRaw`.

Control flow and state: creates temp local repos/caches/mountpoints/testdata with low-security test KDF and fast retries, installs a default backend hook that detects multiple listings, and returns cleanup. Helpers compare restored directory trees, directly remove packs through captured backend, load snapshots, generate random files, capture stdout, and install terminal status wrappers.

Dependencies and integration points: central dependency for most integration tests; uses backend/all, retry, repository test knobs, restic fixtures, termstatus, progress printers, and OS filesystem APIs.

Risks: direct backend and filesystem manipulation is powerful and local-backend-oriented. Default list-once hook requires tests to disable it when repeated listings are expected. Directory comparison depends on OS-specific `dirEntry.equals`.

Test signals: not a test itself but enables broad command integration coverage and fault injection.
<!-- END_FILE_RESEARCH: sources/sync-backup/restic/cmd/restic/integration_helpers_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/restic/cmd/restic/integration_helpers_unix_test.go -->
# sources/sync-backup/restic/cmd/restic/integration_helpers_unix_test.go

Purpose: Unix-specific implementations for integration directory comparison and hardlink grouping.

Important APIs/types/functions: `(*dirEntry).equals`; `nlink`; `createFileSetPerHardlink`.

Control flow and state: equality checks path, mode, modification time, UID, GID, and link count using `syscall.Stat_t`. `nlink` extracts link count. `createFileSetPerHardlink` groups directory entries by inode number.

Dependencies and integration points: used by shared integration helpers and restore tests on non-Windows platforms. Depends on syscall stat fields and filepath.

Risks: UID/GID and link-count comparisons can be sensitive to filesystem behavior and privilege. Symlink modtime handling is delegated to shared `sameModTime`.

Test signals: indirectly exercised by restore directory diff tests and hardlink-related tests elsewhere.
<!-- END_FILE_RESEARCH: sources/sync-backup/restic/cmd/restic/integration_helpers_unix_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/restic/cmd/restic/integration_helpers_windows_test.go -->
# sources/sync-backup/restic/cmd/restic/integration_helpers_windows_test.go

Purpose: Windows-specific implementations for integration directory comparison and hardlink grouping.

Important APIs/types/functions: `(*dirEntry).equals`; `nlink`; `inode`; `createFileSetPerHardlink`.

Control flow and state: equality checks path, mode, and modification time only. `nlink` returns 1, `inode` returns 0, and hardlink grouping assigns synthetic IDs by directory entry index.

Dependencies and integration points: complements the Unix helper file under the `windows` build tag and supports shared tests without relying on Unix stat fields.

Risks: synthetic inode/link behavior means Windows tests cannot validate hardlink identity the same way Unix tests can. Fewer metadata fields are compared.

Test signals: indirectly exercised by cross-platform integration tests that compare restored directory contents.
<!-- END_FILE_RESEARCH: sources/sync-backup/restic/cmd/restic/integration_helpers_windows_test.go -->
