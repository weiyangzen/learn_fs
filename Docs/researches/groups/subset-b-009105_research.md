# subset-b-009105 research

Grouped research report for Borg store locking and the selected archive/archiver test files in subset B. Each source-file section is delimited for deterministic source-tree-aligned splitting.

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/borg/src/borg/storelocking.py -->
# sources/sync-backup/borg/src/borg/storelocking.py

Purpose: implements Borg's borgstore-backed shared/exclusive lock protocol. It stores lock records as JSON objects under `locks/<sha256>` in an abstract store so multiple Borg clients can coordinate repository access without relying on local filesystem lock primitives.

Important APIs/types/functions: `LockError`, `LockErrorT`, `LockFailed`, `LockTimeout`, `NotLocked`, and `NotMyLock` provide Borg error classes with distinct exit codes. `Lock.__init__` records the store, exclusive/shared mode, timeout, stale interval, refresh interval, timing constants, and process identity from `platform.get_process_id()`. `_create_lock` serializes `exclusive`, `hostid`, `processid`, `threadid`, and an ISO timestamp, hashes the JSON payload for the store key, and optionally updates `last_refresh_dt`. `_delete_lock`, `_get_locks`, `_find_locks`, `acquire`, `release`, `got_exclusive_lock`, `break_lock`, `migrate_lock`, and `refresh` form the public/control surface.

Control flow: `acquire` loops until timeout. It first checks for existing exclusive locks; if none are visible, it creates its own lock, sleeps briefly for race detection, then rechecks. Exclusive acquisition succeeds only when this client's exclusive lock is the only exclusive lock and later the only lock of any kind. Shared acquisition succeeds when no exclusive locks remain after creation. Failed attempts delete the just-created lock and sleep for a random backoff. `release` looks up this process/thread's lock and removes it. `refresh` rotates a held lock after half the stale interval by creating a fresh record and deleting the old one; if this client's lock disappeared, it raises `LockTimeout` because continuing a backup could be unsafe.

State and persistence behavior: lock state lives entirely in store objects below `locks/`. Lock values include wall-clock UTC timestamps; liveness is determined by timestamp age and `platform.process_alive`. Stale locks are opportunistically deleted while listing locks, including locks belonging to other clients. `last_refresh_dt` is in-memory state used to throttle refreshes and is reset on release, break, deletion of this client's stale lock, and context-manager cleanup.

Dependencies and integration points: depends on `borgstore.store.ObjectNotFound`, Borg platform process identity/liveness APIs, Borg error/logging helpers, JSON, SHA-256, UTC datetimes, monotonic timeout measurement, and store methods `store`, `delete`, `list`, and `load`. It is intended for repository/store users that need read/write lock semantics and context-manager safety.

Risks: the protocol is optimistic and depends on eventual visibility of store objects; slow remotes may need larger race/recheck delays. Timestamp skew and suspended hosts can cause locks to be considered stale. `_get_locks` assumes every listed lock object is valid JSON with expected fields. `release` asserts exactly one matching lock, so duplicate self locks become assertion failures. `NotMyLock` and `LockFailed` are defined but not exercised in this file, suggesting compatibility with older lock error taxonomy.

Test signals: useful tests should simulate shared/shared compatibility, exclusive exclusion, simultaneous exclusive creation races, stale lock deletion, disappeared-lock refresh failure, lock migration, and store `ObjectNotFound` during cleanup. The surrounding Borg test suites that exercise repository operations also indirectly validate acquisition/release under normal CLI use.
<!-- END_FILE_RESEARCH: sources/sync-backup/borg/src/borg/storelocking.py -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/borg/src/borg/testsuite/__init__.py -->
# sources/sync-backup/borg/src/borg/testsuite/__init__.py

Purpose: provides shared test-suite utilities and platform capability probes used across Borg's tests. It is intentionally lightweight enough for `borg.selftest`, so pytest is optional and many helpers are pure stdlib wrappers.

Important APIs/types/functions: module constants expose FUSE availability, nanosecond timestamp precision, filesystem feature flags, and rejected `..` path cases. `same_ts_ns` compares timestamps within platform granularity. `granularity_sleep` waits long enough for filesystem timestamp changes, including a Windows ctime tunneling workaround. `unopened_tempfile`, `changedir`, `is_root`, `are_symlinks_supported`, `are_hardlinks_supported`, `are_fifos_supported`, `is_utime_fully_supported`, `is_birthtime_fully_supported`, and `filter_xattrs` are reused fixtures/helpers. `BaseTestCase` maps unittest assertions to old Borg naming. `FakeInputs` simulates repeated `input()` calls.

Control flow: platform capability booleans are computed at import time or via `functools.lru_cache`. Capability probes create temporary paths, attempt the operation, verify observable metadata, and return False on unsupported OS errors. Timestamp granularity is derived from Python/posix build flags and OS overrides. `FakeInputs.__call__` prints a prompt if given and pops a queued answer, raising `EOFError` when exhausted.

State and persistence behavior: all filesystem writes occur in temporary directories created by `tempfile`; lru-cached probes persist results in-process to avoid repeated expensive feature checks. `granularity_sleep` intentionally affects test timing but writes no state. `filter_xattrs` removes SELinux and Apple provenance attributes from comparisons because those can be injected by the host environment.

Dependencies and integration points: imports Borg FUSE implementation flags, platform abstraction, platform flags, and standard OS/stat/sysconfig/tempfile APIs. It is imported by archive and archiver tests for skip conditions, filesystem setup, timestamp assertions, and xattr filtering.

Risks: import-time probing of flags and FUSE metadata can be sensitive to unusual filesystems. Cached capability results assume the temp filesystem represents the test workspace. Windows ctime workaround can add a 15 second sleep when requested. Optional pytest import means `BaseTestCase.assert_raises` can be either pytest's `raises` or unittest's context manager.

Test signals: this file is mostly infrastructure; signals come from downstream tests being stable across Linux, macOS, Windows, BSD, FUSE, fakeroot, and filesystems with different timestamp/xattr behavior.
<!-- END_FILE_RESEARCH: sources/sync-backup/borg/src/borg/testsuite/__init__.py -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/borg/src/borg/testsuite/archive_test.py -->
# sources/sync-backup/borg/src/borg/testsuite/archive_test.py

Purpose: unit-tests core archive data helpers: statistics accounting/progress output, archive timestamp parsing, cache chunk buffering, robust item unpacking/resync, msgpack item validation, backup I/O exception wrapping, UID/GID restoration selection, path sanitization, and archive lookup by ID.

Important APIs/types/functions: `stats` fixture builds a `Statistics` object. `MockCache` supplies `add_chunk` and repository async response behavior for `CacheChunkBuffer`. `make_chunks`, `_validator`, `process`, and `split` construct msgpacked item streams and exercise `RobustUnpacker`. Tests cover `Statistics.show_progress`, `Archive.ts`, `CacheChunkBuffer.flush`, `valid_msgpacked_dict`, `backup_io`, `backup_io_iter`, `get_item_uid_gid`, `Item` path validation, and `Archives.get_by_id`.

Control flow: progress tests route output through `StringIO` and a TTY-like subclass to check terminal padding/truncation versus file newline behavior and JSON progress records. Chunk-buffer tests pack `Item` instances, force full and partial flushes, then unpack cached bytes to verify order and completeness. Robust unpacking tests feed split/corrupt/missing chunks, optionally call `resync`, and assert which dicts or garbage bytes emerge. UID/GID tests walk numeric, named, forced, default, invalid, and Windows-specific branches.

State and persistence behavior: tests use in-memory mocks and msgpack buffers rather than real repositories. The only external state is OS user/group lookup for the current uid/gid and nonexistent names. `PlaintextKey`, `Manifest`, and `Archive` are constructed with mocks for timestamp parsing.

Dependencies and integration points: integrates with `borg.archive` (`Archive`, `CacheChunkBuffer`, `RobustUnpacker`, `Statistics`, `backup_io` helpers), `borg.item.Item`, `borg.manifest.Archives`, `borg.crypto.key.PlaintextKey`, Borg msgpack helpers, and platform user/group lookup.

Risks: progress string expectations are tightly coupled to formatting widths and terminal columns. User/group tests depend on the current process uid/gid resolving to names on Unix. Robust unpacker expectations deliberately expose msgpack garbage as integers before resync, so changing unpacker policy will affect tests.

Test signals: strong unit-level coverage for archive helper invariants, especially byte stream recovery and metadata coercion. It does not cover full repository persistence; CLI integration suites cover that separately.
<!-- END_FILE_RESEARCH: sources/sync-backup/borg/src/borg/testsuite/archive_test.py -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/borg/src/borg/testsuite/archiver/__init__.py -->
# sources/sync-backup/borg/src/borg/testsuite/archiver/__init__.py

Purpose: central test harness for Borg archiver command tests. It abstracts invoking Borg in-process or through a forked/binary executable, creates common repository/source fixtures, and supplies filesystem assertion helpers.

Important APIs/types/functions: `exec_cmd` runs Borg either by `subprocess.check_output` or by constructing an `Archiver`, parsing args, redirecting stdio to buffers, running `archiver.run`, and flushing logging. `cmd_fixture`, `generate_archiver_tests`, `checkts`, and `cmd` provide parametrized command execution with repository injection and exit-code assertions. Setup helpers include `create_src_archive`, `open_archive`, `open_repository`, `create_regular_file`, `create_test_files`, `_extract_repository_id`, `_set_repository_id`, cache/tagged fixture builders, and hardlink setup. Assertion/context helpers include `assert_creates_file`, `assert_dirs_equal`, `assert_line_exists`, `assert_line_not_exists`, `read_only`, `wait_for_mountstate`, and `fuse_mount`.

Control flow: tests call `cmd(archiver, ...)`, which prepends `--repo`, selects fork behavior from the fixture, asserts expected return code, and filters pure-Python msgpack warnings. `create_test_files` builds a representative tree with regular files, directories, permissions, hardlinks, symlinks, xattrs, FIFO, flags, devices, ownership, and a newer empty file, skipping unsupported operations. `assert_dirs_equal` recursively compares file type, mode, uid/gid/rdev, nlink, flags, mtime, and xattrs with FUSE/timestamp adjustments. `fuse_mount` handles forked Borg mount, OS double-fork mode, wait/umount cleanup, and expected mount failure cases.

State and persistence behavior: creates and mutates temporary input/output/repository/cache trees owned by test fixtures. It may alter file flags, permissions, xattrs, hardlinks, and mountpoints. In-process command execution temporarily replaces `sys.stdin`, `sys.stdout`, and `sys.stderr` and restores them in `finally`.

Dependencies and integration points: depends on `Archiver`, repository/manifest/archive classes, Borg constants, platform feature probes from `borg.testsuite`, xattr/platform modules, and OS utilities such as chmod/chattr/chflags/umount. Nearly every command test imports this module.

Risks: global stdio replacement in `exec_cmd` is fragile under concurrency. Device, flag, xattr, fakeroot, FUSE, and binary/fork behavior varies by platform. `read_only` shells out and skips when immutable flags cannot be set. `assert_dirs_equal` encodes many platform-specific comparison relaxations and can fail when host metadata is injected.

Test signals: this harness is itself validated indirectly by broad command suites across local, remote, and binary modes. Failures here usually cascade widely, making it a high-impact integration point.
<!-- END_FILE_RESEARCH: sources/sync-backup/borg/src/borg/testsuite/archiver/__init__.py -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/borg/src/borg/testsuite/archiver/_common_test.py -->
# sources/sync-backup/borg/src/borg/testsuite/archiver/_common_test.py

Purpose: verifies repository factory selection in `borg.archiver._common.get_repository` for legacy Borg v1 compatibility paths.

Important APIs/types/functions: `test_get_repository_ssh_v1_uses_legacy_remote` and `test_get_repository_local_v1_uses_legacy_repository` patch `borg.legacy.remote.LegacyRemoteRepository` and `borg.legacy.repository.LegacyRepository` respectively, then call `get_repository`.

Control flow: each test constructs a `MagicMock` location with `proto` set to `ssh` or `file`. With `v1_legacy=True`, SSH must instantiate `LegacyRemoteRepository`; local/file mode must bypass the borgstore branch and instantiate `LegacyRepository` with `location.path`.

State and persistence behavior: no repository is created; all effects are captured through mocks.

Dependencies and integration points: depends on the archiver common repository factory and the legacy repository import paths. It guards compatibility routing for commands that still access Borg 1 repositories.

Risks: import-path refactors or constructor signature changes will break these tests. The test is narrow and does not validate actual legacy repository behavior.

Test signals: confirms the correct class is selected and called with create/exclusive/lock options preserved.
<!-- END_FILE_RESEARCH: sources/sync-backup/borg/src/borg/testsuite/archiver/_common_test.py -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/borg/src/borg/testsuite/archiver/analyze_cmd_test.py -->
# sources/sync-backup/borg/src/borg/testsuite/archiver/analyze_cmd_test.py

Purpose: integration test for `borg analyze`, ensuring it reports cumulative chunk-change contribution for a path across archive history.

Important APIs/types/functions: `test_analyze` uses `cmd`, `RK_ENCRYPTION`, and `generate_archiver_tests` in local mode. Nested helpers create an archive named `archive` repeatedly and run `analyze -a archive`.

Control flow: the test creates a repository, writes `file1`, creates archive 1, writes `file2`, creates archive 2, and expects `/input: 2`. It then writes `file3`, creates archive 3, expects `/input: 5`, deletes `file2`, creates archive 4, and expects `/input: 7`.

State and persistence behavior: mutates files under the archiver input path and persists multiple archives with the same logical match name/history. Repository objects and manifest history are used by analyze to compute deltas.

Dependencies and integration points: covers `analyze` command behavior, archive creation, manifest/archive selection via `-a`, path handling with `pathlib`, and the shared CLI harness.

Risks: expected numeric contributions are tightly tied to chunking/item metadata implementation. Reusing archive name matching can be confusing if archive naming semantics change.

Test signals: validates plain-text analyze output contains expected path contribution counts after additions and deletion.
<!-- END_FILE_RESEARCH: sources/sync-backup/borg/src/borg/testsuite/archiver/analyze_cmd_test.py -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/borg/src/borg/testsuite/archiver/argparsing_test.py -->
# sources/sync-backup/borg/src/borg/testsuite/archiver/argparsing_test.py

Purpose: tests Borg archiver argument parsing, forced-command merging, REST backend restrictions, duplicate/highlander options, filter validation, and common-option propagation across subcommands.

Important APIs/types/functions: tests use `Archiver.get_args`, `Archiver.check_rest_restrictions`, `ArgumentParser`, `flatten_namespace`, `PathNotAllowed`, and the CLI `cmd` wrapper. `TestCommonOptions` defines an artificial common-option set and parser/subparser fixtures to exercise Borg's custom parser machinery.

Control flow: `test_bad_filters` checks invalid archive filters return parse error. `test_highlander` confirms repeated `--umask` combinations fail while single default/custom values work. `test_get_args` combines forced SSH command arguments with `SSH_ORIGINAL_COMMAND`-like strings, rejecting attempts to override path/repository restrictions, change subcommands, or enable REST mode when not forced. It also preserves REST `--backend` so restriction checks can validate it. `test_check_rest_restrictions` accepts unrestricted and allowed `FILE:` backends and raises for outside, non-exact, or non-FILE backends. `TestCommonOptions` verifies options before and after subcommands merge into one namespace and invalid placement is rejected.

State and persistence behavior: most tests are parser-only. Some create a repository/archive to exercise real CLI validation. No durable state beyond fixture repositories.

Dependencies and integration points: integrates with Borg's top-level archiver parser, serve/REST security restrictions, helper path authorization, and common option infrastructure shared by all commands.

Risks: parser tests are sensitive to option defaults, subcommand parser internals, and exact error wording. Security-sensitive forced-command tests must remain conservative because mistakes could permit SSH users to escape restrictions.

Test signals: parse results, exception types, and CLI exit codes provide strong signals for argument handling and serve restriction safety.
<!-- END_FILE_RESEARCH: sources/sync-backup/borg/src/borg/testsuite/archiver/argparsing_test.py -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/borg/src/borg/testsuite/archiver/benchmark_cmd_test.py -->
# sources/sync-backup/borg/src/borg/testsuite/archiver/benchmark_cmd_test.py

Purpose: verifies the `borg benchmark` command in both CRUD and CPU modes, including human-readable and JSON output shapes.

Important APIs/types/functions: `test_benchmark_crud`, `test_benchmark_crud_json_lines`, `test_benchmark_cpu`, and `test_benchmark_cpu_json` use `cmd`, `RK_ENCRYPTION`, `json`, and environment variables `_BORG_BENCHMARK_CRUD_TEST` / `_BORG_BENCHMARK_CPU_TEST` to force small deterministic benchmark workloads.

Control flow: CRUD tests create a repository, set test-mode env var, run `benchmark crud`, and assert all eight operation/sample IDs appear. The JSON-lines variant filters merged stdout/stderr for JSON records, decodes eight entries, and validates id, command, sample metadata, timing, and I/O types. CPU tests set test mode, run `benchmark cpu`, and assert expected text sections or JSON categories.

State and persistence behavior: CRUD mode creates and mutates repository archives as part of benchmark operations. CPU mode is computational and writes no repository. Environment variables alter benchmark scale for tests.

Dependencies and integration points: covers the benchmark command, JSON serialization, compression/hash/encryption/chunker/msgpack benchmark category naming, and the shared archiver harness.

Risks: timing and I/O fields are expected to be positive, which can be brittle if a mocked or extremely fast path reports zero. Output section/category names are part of the tested contract.

Test signals: verifies benchmark command does meaningful work, emits all expected operation IDs, and maintains parseable machine output.
<!-- END_FILE_RESEARCH: sources/sync-backup/borg/src/borg/testsuite/archiver/benchmark_cmd_test.py -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/borg/src/borg/testsuite/archiver/check_cmd_test.py -->
# sources/sync-backup/borg/src/borg/testsuite/archiver/check_cmd_test.py

Purpose: broad integration tests for `borg check`, archive selection filters, repository/archive repair, manifest rebuild, corrupted/missing objects, lost archive recovery, spoofed object defense, and data verification.

Important APIs/types/functions: `corrupt` flips a byte reliably. `check_cmd_setup` creates a repository and two archives with a patched small `ChunkBuffer.BUFFER_SIZE`. Tests use `open_archive`, `Repository`, `Manifest`, `ChunkBuffer`, `bin_to_hex`, `msgpack`, `fchunk`, and `create_src_archive`.

Control flow: usage tests assert repository-only and archives-only modes print the right phases and archive filters select expected archives. Date matching creates old and current timestamped archives and exercises oldest/newest/newer/older units. Corruption tests delete file chunks, archive item chunks, archive metadata, or manifest objects, run check with and without `--repair`, and assert repair restores checkability where possible. Spoofing tests write fake manifest/archive objects with wrong `ro_type` and ensure check rejects/removes them. `--find-lost-archives` verifies a missing archive directory entry can be rediscovered. Data verification corrupts file content objects and distinguishes normal archive checks from `--verify-data`.

State and persistence behavior: tests directly mutate repository object storage, manifest bytes, archive entries, and archive directory files. Repair commands rewrite manifest/archive metadata or delete bad chunks. Remote and binary parametrization is used where supported; some tests skip local-only direct object mutation.

Dependencies and integration points: integrates check command, repository object API, manifest load/write/rebuild, authenticated object type metadata, archive item iteration, chunk index behavior, archive filters, and repair paths.

Risks: direct repository mutation depends on storage layout and object IDs. Some expected archive names in date edge assertions look historical and may be weak. Repair semantics are security-sensitive: fake objects must not be accepted as manifests/archives merely because bytes parse.

Test signals: high-value regression coverage for repository integrity, repair safety, missing/corrupt object diagnostics, and `--verify-data` behavior across encrypted and unencrypted repositories.
<!-- END_FILE_RESEARCH: sources/sync-backup/borg/src/borg/testsuite/archiver/check_cmd_test.py -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/borg/src/borg/testsuite/archiver/checks_test.py -->
# sources/sync-backup/borg/src/borg/testsuite/archiver/checks_test.py

Purpose: tests security and compatibility checks around repository identity, cache/security metadata, mandatory feature flags, remote extraction behavior, and old cache integrity data.

Important APIs/types/functions: helper `get_security_directory` derives Borg's security directory from repository ID. `add_unknown_feature` injects mandatory feature flags into a manifest. `cmd_raises_unknown_feature` abstracts forked CLI exit versus in-process `MandatoryFeatureUnsupported`. Tests use `Cache`, `Manifest`, `Repository`, `Location`, `get_security_dir`, `bin_to_hex`, and shared file/repo helpers.

Control flow: repository swap tests create an encrypted repository, cache it, replace it with an unencrypted or different repository sharing location/ID characteristics, and assert Borg aborts. No-cache variants delete cache/security state and retest. Blank-passphrase repokey tests ensure encrypted-with-empty-passphrase is treated like plaintext from a warning perspective. Repository move tests require explicit `BORG_RELOCATED_REPO_ACCESS_IS_OK` once, then persist the new location. Unknown unencrypted repository tests require confirmation when cache/security knowledge is gone. Unknown feature tests inject mandatory flags for WRITE, CHECK, READ, DELETE, and mount/rename operations and assert the relevant commands reject unsupported features, except whole-repo delete. Cache mandatory-feature cleanup verifies stale unknown cache features are cleared after a forked create. Remote strip-components extraction asserts no cached remote responses leak.

State and persistence behavior: heavily mutates repositories, cache directories, security directories, manifest feature flags, and environment variables. It also replaces repository directories to simulate attacks or relocations.

Dependencies and integration points: covers Borg cache/security-dir trust model, manifest feature negotiation, command operation classification, remote repository response cache cleanup, and FUSE mount restrictions when llfuse is available.

Risks: tests depend on precise cache/security path layout and environment-variable confirmation names. Direct manifest feature injection must stay aligned with feature flag schema. Remote-only leak detection relies on a debug marker string.

Test signals: strong security regression signals for repository swap/move warnings, unknown feature handling, and remote extraction response draining.
<!-- END_FILE_RESEARCH: sources/sync-backup/borg/src/borg/testsuite/archiver/checks_test.py -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/borg/src/borg/testsuite/archiver/compact_cmd_test.py -->
# sources/sync-backup/borg/src/borg/testsuite/archiver/compact_cmd_test.py

Purpose: tests `borg compact` output, behavior after archive deletions, chunk-index safety after interrupted compaction, and files-cache cleanup for deleted archives.

Important APIs/types/functions: tests use `cmd`, `create_src_archive`, `create_regular_file`, `open_repository`, `Manifest`, `ArchiveGarbageCollector`, cache helpers `get_cache_dir`, `files_cache_name`, `discover_files_cache_names`, and `list_chunkindex_hashes`.

Control flow: initial tests create empty or populated repositories, delete zero/some/all archives, run compact with and without `--stats`, and assert expected status/stat lines. `test_compact_index_corruption` repeatedly compacts to guard against incomplete index warnings. `test_compact_interrupted_does_not_poison_chunk_index` deletes the only archive containing unique content, instantiates `ArchiveGarbageCollector`, monkeypatches `save_chunk_index` to raise after object deletion, and asserts cached chunk indexes no longer list deleted objects; a subsequent identical backup must re-upload and extract correctly. `test_compact_files_cache_cleanup` records per-archive files cache names, deletes one archive, compacts, and verifies only remaining archive cache files exist.

State and persistence behavior: repository object stores shrink during compact, cache/chunk index files are invalidated or rewritten, files cache entries are removed, and archive manifests change after delete. The interruption test intentionally leaves a mid-compaction state.

Dependencies and integration points: covers compaction command, garbage collector internals, cache directory layout, chunk index discovery, manifest delete operation, extraction integrity after compaction, and local/remote/binary parametrization where applicable.

Risks: tests introspect cache files and GC internals, so implementation refactors can require test updates. The interruption scenario is critical because stale chunk indexes could cause future archives with dangling references.

Test signals: validates both user-facing compact output and a severe data-loss regression path involving interrupted deletion before chunk-index save.
<!-- END_FILE_RESEARCH: sources/sync-backup/borg/src/borg/testsuite/archiver/compact_cmd_test.py -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/borg/src/borg/testsuite/archiver/completion_cmd_test.py -->
# sources/sync-backup/borg/src/borg/testsuite/archiver/completion_cmd_test.py

Purpose: tests generated shell completion scripts for Bash and Zsh, including size sanity, syntax validity, and Borg-specific Bash completion helper behavior.

Important APIs/types/functions: `cmd_available` detects shell availability. `needs_bash` and `needs_zsh` skip tests when shells are unavailable. `_run_bash_completion_fn` writes a generated completion script to a temp file, sources it in Bash, runs setup code, and captures output. `_check_shell_syntax` validates generated scripts with `shell -n`.

Control flow: nontriviality tests assert generated Bash/Zsh scripts are large enough and have many lines. Syntax tests run Bash/Zsh parsers. Bash helper tests simulate `COMP_WORDS`/`COMP_CWORD` for sort-key completion, files-cache mode mutual exclusions, archive name completion from a real repository, and `aid:` archive ID completion.

State and persistence behavior: temporary shell script files are created and unlinked. Archive completion tests create repositories and archives. Bash subprocesses source generated scripts and emit completion candidates without persisting shell state.

Dependencies and integration points: covers `borg completion bash/zsh`, generated preamble helper functions, repository archive listing used by completion, shell availability, and subprocess execution.

Risks: generated script size thresholds are coarse. Tests depend on internal Bash function names such as `_borg_complete_sortby`, `_borg_complete_filescachemode`, and `_borg_complete_archive`. Shell versions may differ in syntax handling.

Test signals: ensures completion output is not truncated, is syntactically valid for supported shells, and implements important dynamic completions and mutual-exclusion rules.
<!-- END_FILE_RESEARCH: sources/sync-backup/borg/src/borg/testsuite/archiver/completion_cmd_test.py -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/borg/src/borg/testsuite/archiver/corruption_test.py -->
# sources/sync-backup/borg/src/borg/testsuite/archiver/corruption_test.py

Purpose: tests detection of cache integrity metadata modified by older Borg versions that did not maintain the integrity section consistently.

Important APIs/types/functions: `corrupt_archiver` creates test files, initializes a repository, and extracts the cache path from `repo-info --json`. `test_old_version_interfered` uses `ConfigParser` to modify the cache config's main `manifest` value while leaving integrity metadata untouched.

Control flow: after setup, the test skips if no cache path exists for the cache implementation. It edits `<cache>/config`, sets `cache.manifest` to the hex representation of 32 zero bytes, writes the config, then runs `repo-info` and expects a warning that old Borg modified the cache and integrity data is unavailable.

State and persistence behavior: directly modifies the on-disk cache configuration file for the test repository. Repository contents remain valid; only cache metadata is corrupted.

Dependencies and integration points: covers cache config parsing, `repo-info` cache integrity checks, `bin_to_hex`, JSON repo-info output, and the shared archiver harness.

Risks: depends on cache implementation exposing a filesystem `path` and a `config` file with a `[cache] manifest` key. Alternative cache backends skip or need adapted tests.

Test signals: verifies Borg surfaces a clear warning instead of silently trusting mismatched cache integrity data.
<!-- END_FILE_RESEARCH: sources/sync-backup/borg/src/borg/testsuite/archiver/corruption_test.py -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/borg/src/borg/testsuite/archiver/create_cmd_test.py -->
# sources/sync-backup/borg/src/borg/testsuite/archiver/create_cmd_test.py

Purpose: comprehensive integration coverage for `borg create`: filesystem metadata preservation, path sanitation, stdin/command-sourced content, path list ingestion, include/exclude patterns, cache/status modes, JSON/log output, special files, compression, large data, dataless/nodump exclusions, tags, and platform-specific behavior.

Important APIs/types/functions: tests use the shared `cmd`, `create_test_files`, `create_regular_file`, `assert_dirs_equal`, cache/tag helpers, timestamp helpers, platform probes, `Repository`, `Manifest`, Borg `zeros`, exceptions `CommandError` and `BackupPermissionError`, and platform flag APIs. Parametrization runs local, remote, and binary variants where possible.

Control flow: baseline tests create representative file trees, run repo creation and archive creation, extract, list, info, and compare output. Path tests verify POSIX archive paths, MSYS2 warnings, duplicate roots, unreadable parents, slash-dot root stripping, stdin names, `..` rejection, and pattern roots. Input-source tests cover stdin content, content from commands, failed/missing commands, paths from stdin, commands, and shell commands. Pattern/tag/cache tests cover excludes, exclude-tag preservation, path sanitation, repeated files, dry run, progress, file status letters/counters, files-cache modes, files-changed modes, topical filters, JSON archive metadata, explicit hostname/username, and tags. Special/platform tests cover Unix sockets, birthtime omission, FIFOs via `--read-special`, broken symlinks, JSON logging, big zero/random files, multiple compression algorithms, dataless cloud-file exclusion, and nodump directory exclusion.

State and persistence behavior: creates many repositories/archives and mutates input trees, file modes, timestamps, flags, links, FIFOs, sockets, xattrs/metadata, environment variables, and output directories. Some tests verify no archive is persisted after dry runs or failed external commands. Cache state drives unchanged/modified/add status expectations.

Dependencies and integration points: exercises create command interactions with archive metadata, manifest, cache/files-cache, chunking, compression, pattern engine, platform metadata, stdin/subprocess handling, JSON/logging, and extraction/list/info commands used as verification oracles.

Risks: high platform sensitivity around Windows, MSYS2, Cygwin, birthtime, filesystem flags, roots/fakeroot, timestamp granularity, permissions, and special files. Large-data tests can be resource-heavy. Some status expectations depend on Borg's documented but non-obvious cache behavior where newer files may appear added rather than unchanged.

Test signals: very broad end-to-end coverage for create correctness. Strong signals include archive list contents, extracted byte-for-byte comparisons, metadata equality, expected warnings/errors, JSON schema checks, and repository check passing after error-handling scenarios.
<!-- END_FILE_RESEARCH: sources/sync-backup/borg/src/borg/testsuite/archiver/create_cmd_test.py -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/borg/src/borg/testsuite/archiver/debug_cmds_test.py -->
# sources/sync-backup/borg/src/borg/testsuite/archiver/debug_cmds_test.py

Purpose: integration tests for Borg's `debug` subcommands: profiling conversion, dumping archive/repository objects, raw object put/get/delete, object format/parse, manifest/archive JSON dumps, and debug environment info.

Important APIs/types/functions: tests use `pstats.Stats`, JSON, shared command/file helpers, `Compressor`, and constants such as `ROBJ_ARCHIVE_STREAM` and `ITEM_KEYS`. Commands covered include `debug convert-profile`, `dump-archive-items`, `dump-repo-objs`, `id-hash`, `put-obj`, `get-obj`, `delete-obj`, `format-obj`, `parse-obj`, `dump-manifest`, `dump-archive`, and `debug info`.

Control flow: profile tests create archives with `--debug-profile`, convert formats, and load resulting pstats. Dump tests create archives and assert output directories contain generated object/item files. Raw object tests compute an ID hash, put a file as an object, retrieve it, compare bytes, delete it, and handle repeated/invalid deletes. Format/parse tests build data and metadata JSON, format a repo object with compression, put/get/parse it, and validate plain data plus metadata including compressed size/type/level. Type-respecting tests ensure metadata `type` survives formatting. Manifest/archive dump tests write JSON files and verify expected keys. `debug info` checks for Python information.

State and persistence behavior: writes profile files, dump directories, repo object files, data/meta JSON files, and output objects in fixture directories. Mutates repository object storage via debug commands.

Dependencies and integration points: covers debug command plumbing, repository object serialization, compression metadata, manifest/archive JSON dumping, profiling hooks, and constants defining object/item schemas.

Risks: debug commands expose low-level internals, so tests are tightly coupled to object metadata names and repository object formatting. Loading pstats is only safe because test-created files are trusted.

Test signals: validates debug tooling remains operational for diagnostics and low-level object inspection/manipulation.
<!-- END_FILE_RESEARCH: sources/sync-backup/borg/src/borg/testsuite/archiver/debug_cmds_test.py -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/borg/src/borg/testsuite/archiver/delete_cmd_test.py -->
# sources/sync-backup/borg/src/borg/testsuite/archiver/delete_cmd_test.py

Purpose: tests `borg delete` archive-selection behavior, multi-archive deletion, and protected archive handling.

Important APIs/types/functions: `test_delete_options`, `test_delete_multiple`, and `test_delete_ignore_protected` use `cmd`, `create_regular_file`, archive creation, `repo-list`, and `tag --add=@PROT`.

Control flow: `test_delete_options` creates several archives, deletes matching archives via shell match, last archive selection, and explicit `-a`, verifies one archive remains extractable, then deletes it and expects empty repo-list output. `test_delete_multiple` deletes two explicit archives and expects no archives left. Protected test tags one archive with `@PROT`, deletes explicit and pattern-matched archives, and verifies the protected archive remains while unprotected one is gone.

State and persistence behavior: repository archives and manifest entries are created, tagged, deleted, and listed. Archive data may remain pending compaction but manifest visibility changes.

Dependencies and integration points: covers delete command, archive matching/filtering, tag command, protected tag semantics, extraction as existence check, and local/remote/binary harness variants.

Risks: protected behavior is policy-sensitive; accidental changes could allow deleting protected backups. Output equality to empty string assumes no warnings/noise.

Test signals: validates archive selection deletes only intended archives and respects `@PROT`.
<!-- END_FILE_RESEARCH: sources/sync-backup/borg/src/borg/testsuite/archiver/delete_cmd_test.py -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/borg/src/borg/testsuite/archiver/diff_cmd_test.py -->
# sources/sync-backup/borg/src/borg/testsuite/archiver/diff_cmd_test.py

Purpose: comprehensive integration tests for `borg diff`, covering text and JSON output for file content changes, metadata changes, symlinks, hardlinks, directories, sorting, content-only mode, timestamp differences, and hardlink deletion/replacement edge cases.

Important APIs/types/functions: `test_basic_functionality` contains nested `do_asserts` and `do_json_asserts` helpers. Other tests cover `--format`, `--sort-by`, invalid sort fields, every sort key/direction, and hardlink-specific behavior. Shared helpers include `cmd`, `create_regular_file`, `assert_line_exists`, `assert_line_not_exists`, `granularity_sleep`, and platform capability probes.

Control flow: the main test builds snapshot `test0` with empty/unchanged/removed/replaced/touched files, directories, symlinks, and hardlinks, mutates the tree extensively, then creates two second snapshots with different chunking. It compares archives in normal, content-only, and JSON-lines modes and asserts exact change categories while excluding unchanged or symlink-target-only cases. Sorting tests create controlled removed/changed/added files and assert order or valid coverage for sort keys. Timestamp tests distinguish recreated files from chmod-only metadata changes across Windows/POSIX. Hardlink tests compare deletion and recreation with and without patterns, verifying ctime-only hints and absence of false content changes.

State and persistence behavior: creates multiple archives from mutating input trees. Uses filesystem timestamps, modes, symlinks, hardlinks, and content sizes as diff inputs. No direct repository mutation.

Dependencies and integration points: covers diff command, archive item comparison, hardlink identity semantics, pattern engine, JSON output schema, sort-key implementation, platform timestamp behavior, and archive creation.

Risks: many assertions depend on exact human output phrasing/spacing and platform-specific metadata availability. Hardlink behavior differs on unsupported or problematic platforms, so skip conditions exclude FreeBSD/NetBSD/Windows for one case.

Test signals: strong behavioral coverage that diff reports meaningful changes, suppresses irrelevant changes in content-only mode, emits valid JSON changes, and maintains deterministic sorting.
<!-- END_FILE_RESEARCH: sources/sync-backup/borg/src/borg/testsuite/archiver/diff_cmd_test.py -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/borg/src/borg/testsuite/archiver/disk_full_test.py -->
# sources/sync-backup/borg/src/borg/testsuite/archiver/disk_full_test.py

Purpose: slow stress test for Borg behavior when the repository filesystem fills up. It requires a separately mounted writable 700 MB filesystem at `/tmp/borg-mount`.

Important APIs/types/functions: `DF_MOUNT` names the required mount. `make_files` rebuilds an input directory with a random number and size of random files. `test_disk_full` is parametrized for ten passes and uses `cmd_fixture` to run a Borg executable-style command path.

Control flow: the test skips unless `DF_MOUNT` exists. For each pass it sets confirmation environment variables, removes old repo/input directories, creates an unencrypted repo, then loops creating random input files and archives until file creation or `borg create` fails from ENOSPC. It forcibly removes old lock directories after each create attempt, deletes input to free space, runs `repo-list`, repairs with `check --repair`, asserts repair success, and finally deletes the repository to free disk.

State and persistence behavior: intentionally fills the mounted filesystem with repository and input data, leaves partial archives/objects after ENOSPC, removes lock directories, and runs repair. It mutates environment variables and performs cleanup in `finally`.

Dependencies and integration points: covers repo-create, create, lock cleanup, repo-list, check repair, repo-delete, and filesystem ENOSPC handling. Depends on external mount provisioning and enough permissions.

Risks: very resource-heavy and slow; incorrect mount selection could fill a real filesystem. Manual lock directory removal references older lock paths and may not align with newer store-locking internals. Random inputs make exact failure point nondeterministic.

Test signals: validates Borg can recover to a repairable repository state after disk-full failures and does not leave unrecoverable locks.
<!-- END_FILE_RESEARCH: sources/sync-backup/borg/src/borg/testsuite/archiver/disk_full_test.py -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/borg/src/borg/testsuite/archiver/extract_cmd_test.py -->
# sources/sync-backup/borg/src/borg/testsuite/archiver/extract_cmd_test.py

Purpose: comprehensive integration tests for `borg extract`: symlink/hardlink restoration, directory timestamp repair, atime/birthtime, sparse files, filename/pattern handling, strip-components, xattrs/capabilities, overwrite behavior, continue/resume extraction, missing chunk handling, existing directory preservation, dry-run listing, and post-y2038 timestamps.

Important APIs/types/functions: tests use shared helpers `cmd`, `create_test_files`, `create_regular_file`, `assert_dirs_equal`, `_extract_hardlinks_setup`, `assert_creates_file`, `open_archive`, and `create_src_archive`. They also use xattr/platform APIs, `has_seek_hole`, `same_ts_ns`, `granularity_sleep`, `flags_noatime`, `BackupPermissionError`, `bin_to_hex`, and `get_birthtime_ns`.

Control flow: early tests create archives with symlinks, hardlinked symlinks, directories/files in different archive orders, atime/birthtime metadata, and sparse files, then extract and compare metadata/content. Include/exclude tests combine positional patterns, fnmatch/regex, `--exclude`, `--exclude-from`, and `--pattern`. Output tests verify default/info/list/progress behavior. Xattr tests patch setters to simulate E2BIG/ENOTSUP/EACCES, preserve Linux capabilities under patched chown, handle percent signs, and macOS resource forks. Overwrite tests verify replacing existing file/dir targets but warning on non-empty directory conflicts. `--continue` simulates partial extraction and checks which files/directories are reused or re-extracted. Missing chunk test deletes a referenced object and expects zero-byte substitution warning. Existing directory and year-2261 tests guard specific filesystem behaviors.

State and persistence behavior: creates repositories/archives, output trees, hardlinks, symlinks, sparse files, xattrs, flags, timestamps, and direct repository object deletion. Some tests patch OS/xattr functions in-process. `--continue` relies on existing output directory state.

Dependencies and integration points: covers extract command, archive item restoration, platform metadata APIs, pattern engine, repository object retrieval fallback, hardlink map behavior, sparse extraction, xattr/capability handling, and local/remote/binary variants.

Risks: highly platform-sensitive around symlink/hardlink support, Darwin/FreeBSD flags, fakeroot xattrs, sparse-file detection, Windows ctime, and filesystem timestamp range. Missing chunk behavior currently returns success-like output with zeros, noted as a TODO in the test.

Test signals: broad end-to-end extraction correctness signals through metadata comparisons, exact restored contents, warning/exit-code checks, and preservation of tricky filesystem features.
<!-- END_FILE_RESEARCH: sources/sync-backup/borg/src/borg/testsuite/archiver/extract_cmd_test.py -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/borg/src/borg/testsuite/archiver/help_cmd_test.py -->
# sources/sync-backup/borg/src/borg/testsuite/archiver/help_cmd_test.py

Purpose: tests Borg command help generation, topic rendering, parser discovery, and per-command `--help` invocations.

Important APIs/types/functions: `get_all_parsers` builds `Archiver(prog="borg")` and `Archiver(prog="borgfs")` parsers, recursively discovers subcommand parsers from argparse subparser actions, and returns a command-to-parser map. Tests use `RstToTextLazy`, `rst_to_terminal`, `cmd`, and `exec_cmd`.

Control flow: usage/help tests invoke root help, topic help, command help, epilog-only, and usage-only variants. Formatting tests ensure lazy RST epilogs carry source RST and all helptext topics render to terminal text. Main help test asserts additional topic names appear. Parametrized command help test invokes every discovered command's `--help`, with a special borgfs parser path, and asserts usage appears without traceback.

State and persistence behavior: parser construction is in-memory. No repository state is required.

Dependencies and integration points: covers parser construction for Borg and borgfs, help topic dictionary, nanorst rendering, custom subcommand action discovery, and top-level command invocation.

Risks: introspects argparse internals by checking class-name strings and `_actions`; parser implementation changes may require updates. Exact help topic names are part of the tested user interface.

Test signals: validates help remains renderable for every command/topic and does not crash with traceback.
<!-- END_FILE_RESEARCH: sources/sync-backup/borg/src/borg/testsuite/archiver/help_cmd_test.py -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/borg/src/borg/testsuite/archiver/info_cmd_test.py -->
# sources/sync-backup/borg/src/borg/testsuite/archiver/info_cmd_test.py

Purpose: tests `borg info` archive and repository output, JSON schema for archive metadata, empty archive selection behavior, and recorded working directory metadata.

Important APIs/types/functions: `test_info`, `test_info_json`, `test_info_json_of_empty_archive`, and `test_info_working_directory` use `cmd`, `create_regular_file`, `checkts`, `changedir`, JSON decoding, and `RK_ENCRYPTION`.

Control flow: basic info creates one archive and checks text output for `Archive name: test`, including selection by `--first 1`. JSON info decodes `info -a test --json`, asserts a single archive, validates name, command line type, duration, 64-character ID, empty tags, stats presence, and ISO-like start/end timestamps via `checkts`. Empty repo JSON with `--first`/`--last` must return an empty archives list. Working-directory test creates an archive from inside the input directory and asserts text info records that absolute cwd.

State and persistence behavior: creates repositories, archives, and input files. Working-directory metadata is persisted in archive metadata and later rendered by info.

Dependencies and integration points: covers info command, archive selection filters, archive metadata serialization, timestamp formatting, and creation metadata.

Risks: output string expectations depend on text formatting. JSON schema changes for archive metadata must keep these keys or update tests.

Test signals: confirms both human and machine-readable info output expose core archive metadata and handle empty selections cleanly.
<!-- END_FILE_RESEARCH: sources/sync-backup/borg/src/borg/testsuite/archiver/info_cmd_test.py -->
