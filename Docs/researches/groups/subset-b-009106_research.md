# Research: subset-b-009106

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/borg/src/borg/testsuite/archiver/key_cmds_test.py -->
# sources/sync-backup/borg/src/borg/testsuite/archiver/key_cmds_test.py

Purpose: integration coverage for `borg key` and related repository-key behavior across local, remote, and binary archivers. It exercises passphrase rotation, moving key material between repokey and keyfile storage, key export/import variants, paper keys, KDF metadata, and the multi-key-per-repository workflow.

Important APIs and helpers: `cmd`, `generate_archiver_tests`, `_extract_repository_id`, `_set_repository_id`, `Repository`, `AESOCBKey`, `CHPOKey`, `Passphrase`, `is_keyfile`, `keyfile_parse`, `msgpack`, `KeyBlobStorage`, and test helpers `_expect_error`, `_key_id_for_label`, `_exported_label`, `_store_corrupted_borg_key`. The second half defines `ENC_ARGS_AND_MODE` and `ENC_ARGS` for repokey/keyfile parametrization.

Control flow: tests create repositories with `RK_ENCRYPTION`, `KF_ENCRYPTION`, authenticated mode, or Blake3 modes, then mutate key location or passphrase and verify `repo-info`, key files, repository key blobs, and unlockability. Export/import tests round-trip keyfiles, repokeys, QR HTML, paper-key text, and invalid inputs. Multi-key tests add labels, remove by label/id/current passphrase, verify admin/last-key protection, confirm secrets are shared, and assert key selection ambiguity is rejected.

State and persistence: writes to the repository key store, `archiver.keys_path`, explicit `BORG_KEY_FILE`, passphrase environment variables, and repository IDs. Several tests intentionally overwrite key blobs, remove files, or inject corrupted key blobs.

Dependencies/integration: depends on archiver fixtures, environment passphrases, repository internals, key serialization, error classes, and binary/non-fork behavior differences. Risks are high around global `os.environ` mutation, content-addressed keyfile names, KDF algorithm preservation, and multi-key ambiguity. Test signals include expected exit codes, exception classes, repository listings, key list rows, and direct key material comparisons.
<!-- END_FILE_RESEARCH: sources/sync-backup/borg/src/borg/testsuite/archiver/key_cmds_test.py -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/borg/src/borg/testsuite/archiver/list_cmd_test.py -->
# sources/sync-backup/borg/src/borg/testsuite/archiver/list_cmd_test.py

Purpose: integration tests for `borg list` on archives, validating formatter fields, JSON-lines output, depth filtering, hardlink inode reporting, chunk counts, hashes, sizes, and content fingerprints.

Important APIs: `cmd`, `create_regular_file`, `requires_hardlinks`, `generate_archiver_tests`, `RK_ENCRYPTION`, JSON parsing, and archive `info --json` for expected archive IDs.

Control flow: each test creates a repository and archive, then invokes `list` with formatting flags. `test_list_hash`, `test_list_chunk_counts`, and `test_list_size` build specific files to check `{sha256}`, `{num_chunks}`, and `{size}`. `test_list_json` and `test_list_json_lines_includes_archive_keys_in_format` parse one JSON object per item. `test_list_depth` builds nested directories and asserts inclusion/exclusion for `--depth=0..3`. Hardlink and fingerprint tests compare formatter results across hardlinked files, changed content, and altered chunker parameters.

State and persistence: archives persist test input trees; temporary large files are removed after archive creation to save space. Fingerprint tests create multiple archives in one repository and rely on chunker-condition changes changing fingerprints.

Dependencies/integration: depends on item formatter fields, archive metadata formatting, chunker behavior, hardlink platform support, and JSON-lines schema. Risks include platform inode absence, exact SHA-256 fixtures, and depth semantics around directories versus files. Test signals are parsed formatter rows, JSON keys, hardlink inode equality, and fingerprint stability/change assertions.
<!-- END_FILE_RESEARCH: sources/sync-backup/borg/src/borg/testsuite/archiver/list_cmd_test.py -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/borg/src/borg/testsuite/archiver/lock_cmds_test.py -->
# sources/sync-backup/borg/src/borg/testsuite/archiver/lock_cmds_test.py

Purpose: tests repository lock commands, especially `break-lock` and `with-lock` command execution under contention.

Important APIs: `cmd`, `CommandError`, `Path.as_uri`, subprocess `Popen`, `generate_archiver_tests`, and platform flags `is_haiku`/`is_win32`.

Control flow: `test_break_lock` simply creates a repository and runs `break-lock`. `test_with_lock` initializes a repo via `python3 -m borg`, runs one long-lived command under `borg with-lock`, then starts a second `with-lock` process with a short `--lock-wait`; the second command must not execute and must return the lock-timeout code. `test_with_lock_non_existent_command` verifies command launch failures are surfaced as `CommandError` exit codes.

State and persistence: uses `BORG_REPO` pointing at a file URI and keeps one subprocess blocked on stdin to hold the lock. Repository lock state is transient but critical.

Dependencies/integration: depends on importability of `borg` from subprocess Python, PATH/PYTHONPATH, repository locking, process exit codes, and forked execution. Risks include timing sensitivity in lock contention, platform skips, and binary/fork behavior. Test signals are stdout/stderr text, subprocess return codes, and command non-execution.
<!-- END_FILE_RESEARCH: sources/sync-backup/borg/src/borg/testsuite/archiver/lock_cmds_test.py -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/borg/src/borg/testsuite/archiver/mount_cmds_test.py -->
# sources/sync-backup/borg/src/borg/testsuite/archiver/mount_cmds_test.py

Purpose: FUSE integration tests for `borg mount`, covering hardlinks, metadata fidelity, versions view, duplicate archive names, damaged chunks, mount filtering, and lock migration during daemonization.

Important APIs: `fuse_mount`, `cmd`, `assert_dirs_equal`, `create_test_files`, `create_src_archive`, `open_archive`, `Lock.migrate_lock`, `platform.process_alive`, xattr helpers, timestamp comparators, and capability flags for FUSE, hardlinks, symlinks, FIFOs, lchflags, and fakeroot.

Control flow: tests create repositories and archives, mount either whole repositories or selected archives, then inspect mounted paths. `test_fuse` compares extracted tree metadata and verifies stat/read/symlink/FIFO/xattr behavior. `test_fuse_versions_view` mounts with `-o versions` and checks per-file version directories. `test_fuse_allow_damaged_files` deletes a chunk and checks EIO versus zero-filled reads with `allow_damaged_files`. `test_migrate_lock_alive` monkeypatches `Lock.migrate_lock` to serialize process-liveness evidence from the background mount process.

State and persistence: creates mountpoints, archived trees, damaged repository objects, and a pickle side-channel for daemon process assertions. FUSE mount lifecycle is scoped by context managers.

Dependencies/integration: depends on FUSE implementation, OS permissions, xattrs, hardlink semantics, repository object deletion, lock migration, and local-only fork behavior. Risks include environmental flakiness, platform-specific permission checks, and global monkeypatch restoration. Test signals include filesystem metadata equality, mounted directory contents, expected `OSError(errno.EIO)`, and serialized lock assertions.
<!-- END_FILE_RESEARCH: sources/sync-backup/borg/src/borg/testsuite/archiver/mount_cmds_test.py -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/borg/src/borg/testsuite/archiver/patterns_test.py -->
# sources/sync-backup/borg/src/borg/testsuite/archiver/patterns_test.py

Purpose: small unit tests for archive item filtering built by `archiver._common.build_filter`.

Important APIs: `PatternMatcher`, `parse_pattern`, `IECommand.Include`, `Item`, and `build_filter`.

Control flow: `test_basic` creates an include matcher for `included` and verifies exact and child paths pass while unrelated paths fail. `test_empty` uses fallback-true matcher to accept anything. `test_strip_components` verifies that filter behavior rejects paths too shallow for `strip_components=1` but accepts deeper paths after stripping.

State and persistence: no persistent state; all state is in matcher instances and synthetic `Item` objects.

Dependencies/integration: integrates pattern parsing with archive filter generation and strip-components logic used by list/extract/recreate flows. Risks are subtle path-depth semantics and fallback handling. Test signals are direct boolean filter results.
<!-- END_FILE_RESEARCH: sources/sync-backup/borg/src/borg/testsuite/archiver/patterns_test.py -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/borg/src/borg/testsuite/archiver/prune_cmd_test.py -->
# sources/sync-backup/borg/src/borg/testsuite/archiver/prune_cmd_test.py

Purpose: broad prune coverage for CLI retention behavior plus unit-level tests of `prune_within` and `prune_split`.

Important APIs: `cmd`, `_create_archive_ts`, `prune_within`, `prune_split`, `interval`, `MockArchive`, retention flags (`--keep-daily`, `--keep-monthly`, quarterly variants, etc.), and archive match filters.

Control flow: CLI tests create timestamped archives and run dry-run and real `prune`, checking kept/pruned output and subsequent `repo-list` state. The documented prune example, quarterly strategies, oldest-retention expiration, prefix/glob matching, protected archive ignoring, metadata-format listing, and JSON/list-pruned schemas are covered. Unit tests build `MockArchive` instances in local timezone and assert selected archive IDs and `kept_because` rule labels.

State and persistence: archive metadata timestamps are deliberately controlled; real prune mutates repository archive visibility. Protected tags prevent deletion. Local timezone is captured because prune converts archive timestamps to local time.

Dependencies/integration: depends on CLI output wording, local timezone handling, retention bucket algorithms, archive matching, JSON schema, and tag semantics. Risks include date math edge cases, dry-run accidentally mutating state, and formatting lazy-load regressions after deletion. Test signals are regex matches, repository listings, JSON fields, and exact kept sets.
<!-- END_FILE_RESEARCH: sources/sync-backup/borg/src/borg/testsuite/archiver/prune_cmd_test.py -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/borg/src/borg/testsuite/archiver/recreate_cmd_test.py -->
# sources/sync-backup/borg/src/borg/testsuite/archiver/recreate_cmd_test.py

Purpose: integration coverage for `borg recreate`, including exclusion modes, subtree selection, hardlinks, rechunking, timestamps, comments, dry-run, list output, target archive creation, and protected archive handling.

Important APIs: `cmd`, `create_test_files`, `create_regular_file`, cache/tag helper setup/assertions, `_extract_hardlinks_setup`, `changedir`, and hardlink capability checks.

Control flow: tests first create archives with controlled input, then call `recreate` with filters such as `--exclude-caches`, `--exclude-if-present`, `--keep-exclude-tags`, explicit paths, excludes, `--target`, `--chunker-params`, `--timestamp`, `--comment`, `--list`, and `--info`. Follow-up commands run `check`, `list`, `extract`, or `info` to verify archive contents and metadata. Hardlink tests assert recreated subtrees preserve link counts.

State and persistence: `recreate` rewrites archive metadata and item streams unless dry-run or target mode is used. It may preserve original archive IDs when no work is needed, preserve nominal timestamps, or create new archive names.

Dependencies/integration: depends on archive item filtering, files cache/tag helpers, chunker parameter parsing, hardlink restoration, local timezone formatting, and protected tag semantics. Risks include unintended rechunking, losing comments/timestamps, deleting protected archives, or mishandling hardlinked exclude tags. Test signals are archive listings, chunk counts, `info` text, repository checks, and output inclusion/exclusion.
<!-- END_FILE_RESEARCH: sources/sync-backup/borg/src/borg/testsuite/archiver/recreate_cmd_test.py -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/borg/src/borg/testsuite/archiver/remote_repo_test.py -->
# sources/sync-backup/borg/src/borg/testsuite/archiver/remote_repo_test.py

Purpose: smoke/integration tests for non-local repository backends: rclone, REST, SFTP, and S3.

Important APIs: `have_rclone`, `cmd`, `create_regular_file`, `assert_dirs_equal`, `changedir`, backend URLs from `BORG_TEST_*_REPO`, and optional `BORG_REMOTE_PATH`.

Control flow: each backend test creates files, points `archiver.repository_location` at the backend URL, runs `repo-create`, `create`, `repo-list`, `list`, `extract`, `delete`, and `repo-delete`. The rclone test validates installed rclone version using `rclone rc --loopback core/version`; REST sets `BORG_REMOTE_PATH` to the local borg executable when needed.

State and persistence: creates actual remote/backend repositories and removes archives/repositories at the end. Extraction writes to the local output path for content comparison.

Dependencies/integration: depends on external services or env vars, rclone version, remote transport implementations, and repository cleanup. Risks are environmental flakiness, partial cleanup after failures, and backend-specific metadata differences hidden by ignored flags/xattrs. Test signals are archive names in listings, file paths in archive lists, directory equality, and successful delete/repo-delete.
<!-- END_FILE_RESEARCH: sources/sync-backup/borg/src/borg/testsuite/archiver/remote_repo_test.py -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/borg/src/borg/testsuite/archiver/rename_cmd_test.py -->
# sources/sync-backup/borg/src/borg/testsuite/archiver/rename_cmd_test.py

Purpose: verifies `borg rename` updates archive names while preserving archive accessibility and manifest consistency.

Important APIs: `cmd`, `create_regular_file`, `Repository`, `Manifest.load`, and `Manifest.archives`.

Control flow: creates two archives (`test`, `test.2`), confirms both can be dry-run extracted, renames them to `test.3` and `test.4`, confirms extraction by new names, then loads the manifest directly to assert exactly two archives with the new names exist.

State and persistence: repository manifest archive index is mutated by rename; archive payloads remain extractable.

Dependencies/integration: integrates CLI rename with manifest archive storage and repository loading. Risks include stale old names, duplicate manifest entries, or broken archive references after rename. Test signals are dry-run extraction success and manifest `count`/`exists` checks.
<!-- END_FILE_RESEARCH: sources/sync-backup/borg/src/borg/testsuite/archiver/rename_cmd_test.py -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/borg/src/borg/testsuite/archiver/repo_create_cmd_test.py -->
# sources/sync-backup/borg/src/borg/testsuite/archiver/repo_create_cmd_test.py

Purpose: tests repository creation failure paths and keyfile overwrite protection.

Important APIs: `cmd`, `FlexiKey.create`, `patch`, `CancelledByUser`, `Error`, `RK_ENCRYPTION`, `KF_ENCRYPTION`, `KF_LOCATION`, and `BORG_KEY_FILE`.

Control flow: `test_repo_create_interrupt` patches key creation to raise `EOFError`, expects cancellation/exit code, and asserts no repository path remains. `test_repo_create_requires_encryption_option` verifies missing encryption fails. `test_repo_create_refuse_to_overwrite_keyfile` creates one keyfile through `BORG_KEY_FILE`, then attempts a second repo-create pointing to the same file and verifies it fails without modifying file contents.

State and persistence: repository directory creation is rolled back on interrupted setup; explicit keyfile content must remain unchanged.

Dependencies/integration: depends on non-binary patchability, key creation, environment variables, fork/non-fork error behavior, and keyfile storage. Risks include partial repository creation, unsafe key overwrite, and divergent binary exit handling. Test signals are existence checks, exit codes/exceptions, and before/after keyfile content equality.
<!-- END_FILE_RESEARCH: sources/sync-backup/borg/src/borg/testsuite/archiver/repo_create_cmd_test.py -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/borg/src/borg/testsuite/archiver/repo_delete_cmd_test.py -->
# sources/sync-backup/borg/src/borg/testsuite/archiver/repo_delete_cmd_test.py

Purpose: verifies `borg repo-delete` confirmation protection and final repository removal.

Important APIs: `cmd`, `create_regular_file`, `CancelledByUser`, `BORG_DELETE_I_KNOW_WHAT_I_AM_DOING`, and `RK_ENCRYPTION`.

Control flow: creates a repository and two archives, sets confirmation env var to `no` and expects cancellation, verifies the repository still exists, then sets the env var to `YES`, runs `repo-delete`, and asserts the repository path no longer exists.

State and persistence: deletion mutates/removes the repository directory; cancellation must not.

Dependencies/integration: depends on env-driven destructive operation confirmation and fork/non-fork error behavior. Risks include accidental deletion without confirmation or incomplete deletion. Test signals are expected exception/exit code and filesystem existence.
<!-- END_FILE_RESEARCH: sources/sync-backup/borg/src/borg/testsuite/archiver/repo_delete_cmd_test.py -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/borg/src/borg/testsuite/archiver/repo_info_cmd_test.py -->
# sources/sync-backup/borg/src/borg/testsuite/archiver/repo_info_cmd_test.py

Purpose: tests `borg repo-info` text and JSON output for repository metadata.

Important APIs: `cmd`, `create_regular_file`, `checkts`, JSON parsing, and `RK_ENCRYPTION`.

Control flow: both tests create a repository and archive. The text test checks that `Repository ID:` appears. The JSON test parses `repo-info --json`, validates a 64-character repository ID, `last_modified` timestamp parseability, encryption mode matching the configured repokey mode, and absence of a keyfile field for repokey storage.

State and persistence: repository and archive metadata are persisted before inspection.

Dependencies/integration: depends on JSON schema, timestamp formatting, and encryption mode reporting. Risks include schema drift or incorrect exposure of keyfile details. Test signals are text containment and JSON field checks.
<!-- END_FILE_RESEARCH: sources/sync-backup/borg/src/borg/testsuite/archiver/repo_info_cmd_test.py -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/borg/src/borg/testsuite/archiver/repo_list_cmd_test.py -->
# sources/sync-backup/borg/src/borg/testsuite/archiver/repo_list_cmd_test.py

Purpose: integration tests for `borg repo-list`, covering archive matching, custom formats, archive sizes/file counts, date filters, JSON schema, deleted archive visibility, and Borg 1 listing compatibility.

Important APIs: `cmd`, `checkts`, `create_regular_file`, `_create_archive_ts`, JSON, and Borg 1 testdata tarball.

Control flow: tests create archives with names, comments, sizes, and timestamps, then run `repo-list` with `--match-archives`, default/custom formats, `--short`, date filters (`--oldest`, `--newest`, `--newer`, `--older` with multiple units), `--json`, `--deleted`, and `--from-borg1`. The Borg 1 test extracts `repo12.tar.gz`, sets passphrase/KDF env, and points the archiver at that repository.

State and persistence: repository archive index is populated, logical deletion hides archives from normal listings, and Borg 1 fixture repositories are read locally.

Dependencies/integration: depends on archive formatter, date interval parsing, deletion semantics, JSON metadata, and legacy repository reader. Risks include time-relative tests becoming brittle, short output length assumptions, and Borg 1 environment requirements. Test signals are string membership, parsed JSON fields, timestamp validation, and expected exit code for invalid interval.
<!-- END_FILE_RESEARCH: sources/sync-backup/borg/src/borg/testsuite/archiver/repo_list_cmd_test.py -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/borg/src/borg/testsuite/archiver/repo_space_cmd_test.py -->
# sources/sync-backup/borg/src/borg/testsuite/archiver/repo_space_cmd_test.py

Purpose: tests `borg repo-space` reserved-space management.

Important APIs: `cmd`, `generate_archiver_tests`, `RK_ENCRYPTION`, and repo-space flags `--reserve`/`--free`.

Control flow: tests create repositories, query initial reservation, reserve sizes such as `100M`, `50M`, `0`, and `1K`, assert human-readable rounded output, and free reserved space. The modify test verifies reservation can increase but not implicitly decrease.

State and persistence: repository reserved-space objects are created and removed; tests free reservations at the end to conserve tmp space.

Dependencies/integration: depends on 64 MiB reservation block rounding and output formatting using decimal MB. Risks include brittle exact strings if formatter units change and disk usage during tests. Test signals are exact output messages.
<!-- END_FILE_RESEARCH: sources/sync-backup/borg/src/borg/testsuite/archiver/repo_space_cmd_test.py -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/borg/src/borg/testsuite/archiver/restricted_permissions_test.py -->
# sources/sync-backup/borg/src/borg/testsuite/archiver/restricted_permissions_test.py

Purpose: local-only tests for repository permission modes controlled by `BORG_REPO_PERMISSIONS`.

Important APIs: `cmd`, `create_test_files`, `changedir`, `PermissionDenied`, and permission values `all`, `no-delete`, `read-only`, `write-only`.

Control flow: each test creates a repo under full permissions, then switches permission mode and exercises allowed/disallowed commands. `all` permits create/delete/repo-delete. `no-delete` permits create/list/check but rejects archive deletion, rename, repo-delete, compact, and repair. `read-only` permits list/extract but rejects create/delete/repo-delete/compact. `write-only` permits new archive creation, rejects reads/deletes/compact/check/repo-delete, then switches to read-only to verify both archives are readable.

State and persistence: environment variable changes gate repository backend operations. Archives and repository state persist across mode switches.

Dependencies/integration: depends on borgstore permission enforcement and local archiver behavior; only generated for local kinds. Risks include permission matrix drift and commands that internally read before writing. Test signals are successful allowed commands and `PermissionDenied` exceptions for blocked operations.
<!-- END_FILE_RESEARCH: sources/sync-backup/borg/src/borg/testsuite/archiver/restricted_permissions_test.py -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/borg/src/borg/testsuite/archiver/return_codes_test.py -->
# sources/sync-backup/borg/src/borg/testsuite/archiver/return_codes_test.py

Purpose: verifies warning/error exit code behavior in classic and modern modes.

Important APIs: `cmd`, `changedir`, `IncludePatternNeverMatchedWarning`, `Repository.DoesNotExist.exit_mcode`, `EXIT_ERROR`, and `BORG_EXIT_CODES`.

Control flow: `test_return_codes` creates and extracts an archive, then extracts with a non-matching include path under forked execution and expects the include-pattern warning exit code. `test_exit_codes` creates an uninitialized repo directory, runs `create` under `BORG_EXIT_CODES=classic` expecting generic `EXIT_ERROR`, then under `modern` expecting the specific repository-does-not-exist machine code.

State and persistence: manipulates repository directory existence without initialization and changes process environment for exit-code mode.

Dependencies/integration: depends on forked command execution and modern error code mapping. Risks include environment leakage and error taxonomy changes. Test signals are exact expected exit codes.
<!-- END_FILE_RESEARCH: sources/sync-backup/borg/src/borg/testsuite/archiver/return_codes_test.py -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/borg/src/borg/testsuite/archiver/tag_cmd_test.py -->
# sources/sync-backup/borg/src/borg/testsuite/archiver/tag_cmd_test.py

Purpose: local integration tests for `borg tag` operations and special tag safety.

Important APIs: `cmd`, `RK_ENCRYPTION`, tag flags `--set`, `--add`, `--remove`, and `EXIT_ERROR`.

Control flow: creates a repository/archive, then verifies `--set` replaces normal tags and sorts multiple tags; `--add` accumulates tags; `--remove` deletes them. Special tag tests ensure `@PROT` is not accidentally clobbered by `--set` unless included explicitly, and unknown special tags cannot be set, added, or removed.

State and persistence: archive metadata tags mutate in the repository manifest/archive record.

Dependencies/integration: depends on local archiver only, tag formatting, protected tag semantics, and special-tag validation. Risks include accidental removal of protection tags. Test signals are exact output fragments and expected error exits.
<!-- END_FILE_RESEARCH: sources/sync-backup/borg/src/borg/testsuite/archiver/tag_cmd_test.py -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/borg/src/borg/testsuite/archiver/tar_cmds_test.py -->
# sources/sync-backup/borg/src/borg/testsuite/archiver/tar_cmds_test.py

Purpose: integration coverage for `export-tar` and `import-tar`, including GNU/gzip compatibility, hardlinks, path normalization, concatenated tars, Borg/PAX metadata, xattrs, and POSIX ACLs.

Important APIs: `cmd`, `assert_dirs_equal`, `changedir`, `create_test_files`, `create_regular_file`, `_extract_hardlinks_setup`, `requires_hardlinks`, GNU tar/gzip probes, xattr helpers, `acl_get`, `acl_set`, and platform ACL skip markers.

Control flow: export tests create Borg archives, export tar/tar.gz with format/list/strip flags, extract via GNU tar, and compare trees. Import tests feed normal, gzip, unusual-path, dotdot, dotslash, and concatenated tar archives into Borg, then list or extract results. Roundtrip tests export/import Borg and PAX formats and verify xattrs/ACLs survive.

State and persistence: creates tar files in the workdir, repositories, extracted outputs, xattrs, ACLs, and hardlink relationships. Some tests intentionally remove flag files or tar intermediates before comparisons.

Dependencies/integration: depends on external GNU tar/gzip, filesystem xattrs/ACLs, hardlinks, platform-specific path and permission behavior, and archive metadata encoding. Risks include tar path traversal handling, metadata loss, brittle external tool availability, and exact tree comparison semantics. Test signals are directory equality, link counts, path lists, expected ValueError for `..`, xattr values, and ACL byte strings.
<!-- END_FILE_RESEARCH: sources/sync-backup/borg/src/borg/testsuite/archiver/tar_cmds_test.py -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/borg/src/borg/testsuite/archiver/transfer_cmd_test.py -->
# sources/sync-backup/borg/src/borg/testsuite/archiver/transfer_cmd_test.py

Purpose: integration and regression tests for `borg transfer`, especially Borg 1-to-2 migration, archive metadata preservation, recompression, rechunking, dry-run safety, and source index immutability.

Important APIs: `setup_repos`, `cmd`, `open_archive`, `open_item`, `parse_timestamp`, `parse_file_size`, `ChunkerParams`, Borg 1 `repo12.tar.gz`, JSON/tarfile/stat/hashlib helpers, and environment passphrases `BORG_PASSPHRASE`/`BORG_OTHER_PASSPHRASE`.

Control flow: Borg 1 tests extract fixture repos, create a Borg 2 destination with `--from-borg1`, transfer, compare repo-list and item JSON after normalizing expected schema differences, and inspect stored items directly. SSH legacy transfer uses `ssh://__testsuite__`. Normal transfer uses `setup_repos` to switch archiver from source repo to destination repo. Metadata, recompression, and rechunking tests compare archive JSON, compact-reported repository sizes, chunker params, expected fixed chunk counts, and SHA-256 of item contents. Dry-run ensures rechunking path does not create archives. Issue #9022 records source Borg 1 index metadata before/after transfer.

State and persistence: switches `archiver.repository_location`/`repository_path`, creates two repos with different passphrases, transfers archives, reads direct archive objects, and inspects legacy index files.

Dependencies/integration: depends on local-only legacy fixtures for Borg 1 cases, repository compatibility layers, compression/chunker implementations, JSON schema, and platform differences for block devices on Windows. Risks include fixture drift, source repo mutation, metadata normalization gaps, and memory size assumptions while reading item contents. Test signals are repo checks, JSON equality after normalization, archive metadata equality, repository size comparisons, chunk counts, content hashes, and unchanged index metadata.
<!-- END_FILE_RESEARCH: sources/sync-backup/borg/src/borg/testsuite/archiver/transfer_cmd_test.py -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/borg/src/borg/testsuite/archiver/undelete_cmd_test.py -->
# sources/sync-backup/borg/src/borg/testsuite/archiver/undelete_cmd_test.py

Purpose: tests logical archive undeletion via `borg undelete`.

Important APIs: `cmd`, `create_regular_file`, `RK_ENCRYPTION`, and archive selection with `-a sh:*`.

Control flow: tests create normal and deleted archives, run `delete`, verify deleted archives disappear from normal `repo-list`, then call `undelete` either by exact name, dry-run/list mode, or real multi-archive mode. Final listings verify whether archives returned.

State and persistence: archive deletion is logical/recoverable; undelete flips deleted archives back to visible. Dry-run must not mutate state.

Dependencies/integration: depends on archive deleted-state storage, matching, listing, and repository check after undelete. Risks include confusing dry-run output comments and accidentally undeleting non-candidates. Test signals are output membership and `check` success.
<!-- END_FILE_RESEARCH: sources/sync-backup/borg/src/borg/testsuite/archiver/undelete_cmd_test.py -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/borg/src/borg/testsuite/archives_test.py -->
# sources/sync-backup/borg/src/borg/testsuite/archives_test.py

Purpose: unit tests for the `Archives` manifest/archive-index implementation and its `ArchivesInterface` contract.

Important APIs/types: `Archives`, `ArchiveInfo`, `ArchivesInterface`, `Repository`, `ItemInfo`, `StoreObjectNotFound`, `CommandError`, `Error`, `_id`, `_archives`, `_archive_meta`, `_archiveinfo`, `_stub_info_tuples`, and `_stub_matching_info_tuples`.

Control flow: early tests check interface methods, ids/count/names/existence, deleted flags, and metadata loading. Metadata tests mock `repo.get`, `repo_objs.parse`, and `key.unpack_archive` for success, missing archive, tags, defaults, and bad versions. Mutation tests verify `create`, `delete_by_id`, `undelete_by_id`, and `nuke_by_id` call store APIs. Listing tests cover type checks, generator materialization regression, sorting, reverse, first/last, date filters, deleted flag propagation, match patterns (`name`, `user`, `host`, `tags`, `aid`), exact-one selection, and `list_considering` CLI argument delegation.

State and persistence: mostly mocked repository/store state; archive objects are represented by store names under `archives/<hex-id>` and metadata dictionaries unpacked from archive objects.

Dependencies/integration: depends on borgstore list/get/move/delete semantics, archive metadata schema version 2, timestamp parsing, match grammar, and date filter delegation. Risks include ambiguous archive-id prefixes, generator misuse, incorrect deleted flag propagation, and compatibility parameters such as ignored `overwrite`. Test signals are mock call assertions, returned `ArchiveInfo` values, raised errors, sorted lists, and exact matched sets.
<!-- END_FILE_RESEARCH: sources/sync-backup/borg/src/borg/testsuite/archives_test.py -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/borg/src/borg/testsuite/benchmark_test.py -->
# sources/sync-backup/borg/src/borg/testsuite/benchmark_test.py

Purpose: pytest-benchmark performance tests for common Borg CLI commands and propdict item attribute access.

Important APIs: `benchmark`, `cmd_fixture`, `changedir`, fixtures `repo_url`, `repo`, `testdata`, `repo_archive`, `Item`, and `zeros`.

Control flow: fixtures set isolated repository/cache/key env vars and create repositories under encryption modes `none` and `aes-ocb`; session test data is either zero-like memoryview content or `os.urandom`. Benchmarks time `create` with no compression/lz4, `extract`, `delete`, `list`, `info`, `check`, `help`, and attribute set/get/as_dict on `Item`.

State and persistence: creates temporary repositories, cache/key dirs, test data directories, and archives. Cleanup removes tmp dirs through fixture finalizers.

Dependencies/integration: depends on pytest-benchmark plugin, command fixture return conventions, compression support, and generated data size. Risks include high disk/CPU use, sparse detection avoidance via non-binary-zero memoryview, and benchmark-only semantics not being normal correctness tests. Test signals are command result code `0` and propdict attribute equality.
<!-- END_FILE_RESEARCH: sources/sync-backup/borg/src/borg/testsuite/benchmark_test.py -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/borg/src/borg/testsuite/cache_test.py -->
# sources/sync-backup/borg/src/borg/testsuite/cache_test.py

Purpose: unit/regression tests for ad-hoc file cache behavior and repository chunkindex cache helpers.

Important APIs: `AdHocWithFilesCache`, `FileCacheEntry`, `delete_chunkindex_cache`, `read_chunkindex_from_repo_cache`, `ChunksMixin`, `write_chunkindex_to_repo_cache`, `list_chunkindex_hashes`, `ChunkIndex`, `ChunkIndexEntry`, `Statistics`, `Manifest`, `Repository`, `AESOCBKey`, `safe_ns`, and `int_to_timestamp`.

Control flow: class fixtures create a real temporary repository, key, manifest, and cache. Tests verify manifest chunk is not treated as seen, chunk add/reuse returns sizes, file-known lookup leaves empty files cache, and no-change backups preserve current files cache entries when `_newest_cmtime` is `None`. Standalone tests cover missing chunkindex cache deletion/read handling and ensure `ChunksMixin.chunks` binds fragmented repository indexes without consolidating cache fragments.

State and persistence: writes repository chunks, manifests, compressed files-cache entries, and cache/chunks fragments. Some tests monkeypatch repository store methods to simulate races.

Dependencies/integration: depends on repository store cache layout, chunk index serialization, cache integrity metadata, and key/manifest setup. Risks include cache entry loss after no-change backups, races deleting missing cache objects, and costly cache fragment consolidation on read. Test signals are returned tuples, cache dictionaries, absence of raised exceptions, fragment counts, and in-memory index membership.
<!-- END_FILE_RESEARCH: sources/sync-backup/borg/src/borg/testsuite/cache_test.py -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/borg/src/borg/testsuite/chunkers/__init__.py -->
# sources/sync-backup/borg/src/borg/testsuite/chunkers/__init__.py

Purpose: shared helper module for chunker tests, especially sparse-file fixtures and chunk result normalization.

Important APIs/functions: `cf`, `cf_expand`, `make_sparsefile`, `make_content`, `fs_supports_sparse`, constants `BS`, `map_sparse1`, `map_sparse2`, `map_notsparse`, and `map_onlysparse`.

Control flow: `cf` maps chunk objects into either bytes for `CH_DATA` or integer lengths for `CH_HOLE`/`CH_ALLOC`, while asserting metadata/data consistency. `cf_expand` turns hole/allocation integers into zero bytes for reconstruction tests. Sparse helpers create real sparse files or expected content maps from `(offset, size, is_data)` triples. `fs_supports_sparse` creates a temporary sparse file and probes `SEEK_HOLE`/`SEEK_DATA`.

State and persistence: helper creates temporary or named files and uses filesystem sparse capabilities; maps describe block-level sparse layouts.

Dependencies/integration: used by fixed, buzhash, reader, and self-test modules. Depends on constants `CH_DATA`, `CH_HOLE`, `CH_ALLOC`, `BS`, and `has_seek_hole`. Risks are assuming block-size alignment and OS coalescing behavior. Test signals are assertions inside helpers and sparse capability return value.
<!-- END_FILE_RESEARCH: sources/sync-backup/borg/src/borg/testsuite/chunkers/__init__.py -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/borg/src/borg/testsuite/chunkers/buzhash64_self_test.py -->
# sources/sync-backup/borg/src/borg/testsuite/chunkers/buzhash64_self_test.py

Purpose: Borg self-test coverage for 64-bit buzhash chunker behavior without importing pytest.

Important APIs: `ChunkerBuzHash64`, `buzhash64`, `buzhash64_update`, `get_chunker`, `BaseTestCase`, `cf`, fixed test keys `key0`/`key1`/`key2`, and `CHUNKER64_PARAMS`.

Control flow: `test_chunkify64` feeds byte streams into the chunker with different keys and parameters and asserts exact chunk boundaries and full reconstruction. `test_buzhash64` checks known hash values, rolling update equivalence, and barrel-shift behavior beyond 63 bytes. `test_small_reads64` defines a file-like object returning one byte per read and verifies the default chunker reconstructs the expected data.

State and persistence: no persistent state; all tests use `BytesIO` and deterministic keys.

Dependencies/integration: part of Borg's self-test count, so it avoids pytest constructs. Risks include any chunk-boundary change bloating existing repositories and self-test count drift when methods change. Test signals are `BaseTestCase.assert_equal` exact values and reconstructed bytes.
<!-- END_FILE_RESEARCH: sources/sync-backup/borg/src/borg/testsuite/chunkers/buzhash64_self_test.py -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/borg/src/borg/testsuite/chunkers/buzhash64_test.py -->
# sources/sync-backup/borg/src/borg/testsuite/chunkers/buzhash64_test.py

Purpose: pytest regression/fuzz tests for 64-bit buzhash chunker stability, size distribution, keyed table generation, and reconstruction.

Important APIs: `ChunkerBuzHash64`, `buzhash64_get_table`, `cf`, `cf_expand`, `hex_to_bin`, `CHUNKER64_PARAMS`, and local digest helper `H`.

Control flow: `test_chunkpoints64_unchanged` runs many parameter/key combinations over deterministic pseudo-random data and hashes chunk digests to assert a golden overall hash. Distribution test chunks 1 MiB random data and checks counts and min/max clipping. Table test asserts 256 integer entries, deterministic per key, different across keys, and exactly half of entries set for each bit. Slow fuzz reconstructs random, repeated nonzero, and zero data for many keys/sizes.

State and persistence: in-memory only, gated slow fuzz by `BORG_TESTS_SLOW`.

Dependencies/integration: depends on chunker algorithm stability and keyed table balance. Risks include golden hash churn from performance changes, randomness making distribution tests statistically sensitive, and CPU-heavy fuzz. Test signals are golden digest, range/count assertions, table bit counts, and reconstructed content equality.
<!-- END_FILE_RESEARCH: sources/sync-backup/borg/src/borg/testsuite/chunkers/buzhash64_test.py -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/borg/src/borg/testsuite/chunkers/buzhash_self_test.py -->
# sources/sync-backup/borg/src/borg/testsuite/chunkers/buzhash_self_test.py

Purpose: Borg self-test coverage for the classic 32-bit buzhash chunker.

Important APIs: `Chunker`, `buzhash`, `buzhash_update`, `get_chunker`, `BaseTestCase`, `cf`, and `CHUNKER_PARAMS`.

Control flow: `test_chunkify` verifies exact chunk boundaries for empty, large, and repeated strings across seeds and chunker parameters. `test_buzhash` checks known hash outputs, rolling update equivalence, and barrel-shift behavior beyond 31 bytes. `test_small_reads` verifies chunking remains correct for a file-like object that returns one byte at a time.

State and persistence: no persistent state; all data is in `BytesIO`.

Dependencies/integration: self-test module must avoid pytest and match `borg.selftest` expected method count. Risks are repository deduplication compatibility if chunk boundaries change and subtle small-read buffer bugs. Test signals are exact chunk arrays, known hash integers, and reconstructed content.
<!-- END_FILE_RESEARCH: sources/sync-backup/borg/src/borg/testsuite/chunkers/buzhash_self_test.py -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/borg/src/borg/testsuite/chunkers/buzhash_test.py -->
# sources/sync-backup/borg/src/borg/testsuite/chunkers/buzhash_test.py

Purpose: pytest tests for classic buzhash chunker stability, chunk-size distribution, and slow fuzz reconstruction.

Important APIs: `Chunker`, `cf`, `cf_expand`, `hex_to_bin`, `CHUNKER_PARAMS`, `HASH_WINDOW_SIZE`, and helper `H`.

Control flow: deterministic `twist` data is chunked across window/min/max/mask/seed combinations, then a golden digest asserts chunkpoint compatibility. Distribution test chunks 1 MiB random data and checks number of chunks, min/max clipping, and low min/max clipping counts. Slow fuzz iterates random signed 32-bit seeds and sizes over random, repeated nonzero, and zero data, reconstructing output.

State and persistence: in-memory only; slow test gated by `BORG_TESTS_SLOW`.

Dependencies/integration: depends on default chunker parameters being `CH_BUZHASH` and algorithmic compatibility. Risks include statistical distribution failures, golden hash changes, and CPU-heavy fuzz. Test signals are golden digest, chunk size bounds, and reconstructed byte equality.
<!-- END_FILE_RESEARCH: sources/sync-backup/borg/src/borg/testsuite/chunkers/buzhash_test.py -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/borg/src/borg/testsuite/chunkers/failing_test.py -->
# sources/sync-backup/borg/src/borg/testsuite/chunkers/failing_test.py

Purpose: tests the synthetic `ChunkerFailing` used to simulate read/chunk failures.

Important APIs: `ChunkerFailing`, `BytesIO`, `pytest.raises`, and `CH_DATA`.

Control flow: creates data larger than two fixed-size blocks and a failing chunker configured as `rEErrr`. The first generator yields block 0 then raises on block 1; the second new generator raises again; the third generator succeeds for subsequent blocks. Assertions check data slices and allocation metadata.

State and persistence: no files; failure state is maintained by the chunker instance across `chunkify` calls.

Dependencies/integration: useful for testing retry/error paths elsewhere. Risks include stateful failure counters being surprising across generator instances. Test signals are raised `OSError` and exact recovered chunks.
<!-- END_FILE_RESEARCH: sources/sync-backup/borg/src/borg/testsuite/chunkers/failing_test.py -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/borg/src/borg/testsuite/chunkers/fixed_self_test.py -->
# sources/sync-backup/borg/src/borg/testsuite/chunkers/fixed_self_test.py

Purpose: Borg self-test coverage for `ChunkerFixed`.

Important APIs: `ChunkerFixed`, `BaseTestCase`, `cf`, `BytesIO`, and allocation constants.

Control flow: tests fixed block splitting with and without header size; then repeats with explicit file maps. Complete maps should emit all expected blocks, maps marking zero regions as holes should produce integer hole lengths, and partial maps should only emit mapped data ranges.

State and persistence: in-memory `BytesIO` only.

Dependencies/integration: self-test must avoid pytest and stay aligned with self-test counts. Risks include header offset arithmetic, file-map partial coverage, and hole/data metadata consistency. Test signals are exact normalized chunk lists.
<!-- END_FILE_RESEARCH: sources/sync-backup/borg/src/borg/testsuite/chunkers/fixed_self_test.py -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/borg/src/borg/testsuite/chunkers/fixed_test.py -->
# sources/sync-backup/borg/src/borg/testsuite/chunkers/fixed_test.py

Purpose: pytest tests for fixed-size chunking over sparse and nonsparse files plus slow fuzz reconstruction.

Important APIs: `ChunkerFixed`, `cf`, `cf_expand`, `make_sparsefile`, `make_content`, sparse maps, `BS`, and `pretty_print`.

Control flow: parametrized sparse test creates real files for each sparse map/header/sparse-mode combination, chunks them with `ChunkerFixed(BS, header_size, sparse)`, and compares normalized chunks with expected content. Slow fuzz reconstructs random, all-same, and all-zero data for several block/header sizes.

State and persistence: writes temporary sparse files and uses real filesystem behavior.

Dependencies/integration: depends on test sparse maps being aligned to fixed chunk size and on helper representation of holes/allocated zeros. Risks include filesystem sparse behavior, header handling across block boundaries, and slow test cost. Test signals are exact normalized chunk comparisons and reconstructed byte equality.
<!-- END_FILE_RESEARCH: sources/sync-backup/borg/src/borg/testsuite/chunkers/fixed_test.py -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/borg/src/borg/testsuite/chunkers/interaction_test.py -->
# sources/sync-backup/borg/src/borg/testsuite/chunkers/interaction_test.py

Purpose: integration-style tests for reader/chunker buffer interaction across fixed, buzhash, and buzhash64 chunkers.

Important APIs: `get_chunker`, chunker parameter constants (`CH_FIXED`, `CH_BUZHASH`, `CH_BUZHASH64`), allocation constants, and `BytesIO`.

Control flow: parametrized chunker settings generate a large byte stream containing random data, zeros, and random data. The test chunks it, counts `CH_DATA`, `CH_ALLOC`, and `CH_HOLE`, asserts data and allocated-zero chunks are present and holes are absent for `BytesIO`, then reassembles chunks by expanding non-data allocation to zeros and compares against original data.

State and persistence: in-memory only.

Dependencies/integration: checks boundary handling between reader block size and chunker block size, especially awkward fixed sizes. Risks include buffer slicing bugs, misclassified zero ranges, and absent allocation metadata. Test signals are allocation counts, reconstructed size, and exact byte equality.
<!-- END_FILE_RESEARCH: sources/sync-backup/borg/src/borg/testsuite/chunkers/interaction_test.py -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/borg/src/borg/testsuite/chunkers/reader_test.py -->
# sources/sync-backup/borg/src/borg/testsuite/chunkers/reader_test.py

Purpose: unit tests for sparse map detection, `FileReader`, and `FileFMAPReader` blockification/allocation behavior.

Important APIs: `sparsemap`, `FileReader`, `FileFMAPReader`, `Chunk`, `make_sparsefile`, `fs_supports_sparse`, sparse maps, `BS`, and allocation constants.

Control flow: `coalesce_sparse_map` models OS coalescing. Sparsemap tests create real sparse files and compare `sparsemap` results via file handle and file descriptor. `FileReader` tests cover simple reads, multiple reads, and reading from a mocked FMAP reader with mixed chunks. `FileFMAPReader` tests cover empty/small/multiple reads, zero-block detection as `CH_ALLOC`, explicit maps for data and holes, partial map seeking, all-zero allocation types, real sparse file behavior with sparse on/off, and default `_build_fmap`.

State and persistence: mostly `BytesIO`; sparse tests create temporary real sparse files and use `os.open` descriptors.

Dependencies/integration: depends on `SEEK_HOLE`/`SEEK_DATA`, chunk allocation metadata, zero-block detection, reader timing attribute compatibility, and default huge data map size `2**62`. Risks include OS-specific sparse reporting, accidental hole/allocation conflation, and partial fmap seek errors. Test signals are exact chunk data/allocation/size assertions and expected sparse maps.
<!-- END_FILE_RESEARCH: sources/sync-backup/borg/src/borg/testsuite/chunkers/reader_test.py -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/borg/src/borg/testsuite/cockpit_test.py -->
# sources/sync-backup/borg/src/borg/testsuite/cockpit_test.py

Purpose: slow optional UI integration test for the Textual-based Borg cockpit app running a create command.

Important APIs: optional import `BorgCockpitApp`, `asyncio.run`, Textual `run_test`, subprocess `borg repo-create`, platform flags `is_freebsd`/`is_win32`, and app fields `borg_args`, `process_running`, `total_lines_processed`, and `#status`.

Control flow: module-level skip applies if cockpit/Textual is unavailable. The test further skips except on FreeBSD or Windows, creates a repo and 5000 input files, initializes an unencrypted repository via subprocess, then runs the cockpit app test harness with `borg create --list`. It waits until the process finishes, asserts status return code 0, line processing occurred, and quits with `q`.

State and persistence: creates many temporary files and a temporary repository; drives an async UI app in test mode.

Dependencies/integration: depends on installed `borg` command, Textual app importability, platform-specific need for slow UI coverage, and async process state updates. Risks include long runtime, UI selector drift, subprocess PATH issues, and polling loop hangs if process state is not updated. Test signals are app title/running state, status panel return code, and processed-line count.
<!-- END_FILE_RESEARCH: sources/sync-backup/borg/src/borg/testsuite/cockpit_test.py -->
