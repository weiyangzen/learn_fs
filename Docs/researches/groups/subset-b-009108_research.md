# subset-b-009108 Research

Grouped source research for Borg repository-object/version/xattr tests and implementation files plus bup CI, build, development utilities, C extensions, Bloom/index support, remote client code, and command entry points. Each source file has its own marker-delimited section for deterministic reconciliation into source-tree-aligned per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/borg/src/borg/testsuite/repoobj_test.py -->
# sources/sync-backup/borg/src/borg/testsuite/repoobj_test.py

## Purpose
Tests Borg repository object formatting/parsing for Borg 2 objects, legacy Borg 1 objects, Borg 1 to Borg 2 transfer behavior, malformed objects, and repository-object type spoofing. It validates authenticated metadata/data boundaries around `RepoObj`, `RepoObj1`, `PlaintextKey`, `LZ4`, and object type constants.

## Important APIs, Types, and Functions
Fixtures create a `Repository` and `PlaintextKey`. Tests exercise `RepoObj.format`, `parse`, `parse_meta`, `extract_crypted_data`, `id_hash`, and legacy `RepoObj1.parse`. Security/error paths expect `IntegrityError`.

## Control Flow
Round-trip tests format data, parse metadata first, parse full data, and inspect encrypted payload prefixes. Transition coverage reads Borg 1 compressed data with `want_compressed=True` and writes Borg 2 with explicit `size`, `ctype`, and `clevel`. Malformation tests build too-short or inconsistent headers and assert clean rejection.

## State and Persistence Behavior
The tests use temporary repositories but primarily exercise serialized in-repository object bytes. Metadata such as `size`, `csize`, `ctype`, and `clevel` is persisted inside the object envelope and must stay consistent with raw payload boundaries.

## Dependencies and Integration Points
Integrates repository object codecs, key encryption framing, compression metadata, constants for file streams/manifests/archive metadata, and transfer code assumptions that Borg 1 objects can be copied without decompression.

## Risks and Test Signals
Risks are silent data corruption, uncaught `struct.error`/`IndexError`, metadata/header length confusion, and object type spoofing. Strong signals are exact metadata values, data equality, prefix bytes, Borg 1 csize adjustment, and `IntegrityError` for malformed/spoofed objects.
<!-- END_FILE_RESEARCH: sources/sync-backup/borg/src/borg/testsuite/repoobj_test.py -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/borg/src/borg/testsuite/repository_test.py -->
# sources/sync-backup/borg/src/borg/testsuite/repository_test.py

## Purpose
Regression tests for Borg repository storage, pack writing, chunk index persistence, REST serve command construction, partial reads, object listing, consistency, max object size, and failure rollback behavior. It locks down how `Repository` and `PackWriter` store and retrieve raw `RepoObj`-formatted chunks.

## Important APIs, Types, and Functions
Helpers include `reopen`, `fchunk`, `pchunk`, `pdchunk`, `check`, `MockStore`, and `FailingPackStore`. Tests call `Repository.put/get/delete/list/check/store_store`, `PackWriter.add/flush`, `ChunkIndex.add/update_pack_info`, cache functions, and `rest_serve_command`.

## Control Flow
Fixtures create repositories, insert synthetic raw chunks, close/reopen to verify persisted indexes, and manually inject pack/index entries for range reads. Pack writer tests cover non-full flushes, N=1 pack IDs, N=2 SHA256 pack IDs, final partial pack hashing, and rollback when storage fails.

## State and Persistence Behavior
Persistent state includes pack blobs under `packs/`, cached chunk index fragments, repository object membership, and object deletion records. The failure tests ensure in-memory and serialized chunk indexes do not retain phantom entries for packs that failed to store.

## Dependencies and Integration Points
The file integrates repository storage, cache serialization, hash index entries, REST-local/SSH command generation, binary object framing from `RepoObj`, and chunk index pack routing.

## Risks and Test Signals
Risks include stale/phantom dedup indexes causing data loss, off-by-one pack range reads, oversized data acceptance, and inconsistent list pagination. Test signals are object not found after delete/reopen, exact pack offsets/sizes, cache fragment membership, no temp files after check, and clean rollback on simulated pack-store failures.
<!-- END_FILE_RESEARCH: sources/sync-backup/borg/src/borg/testsuite/repository_test.py -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/borg/src/borg/testsuite/shell_completions_test.py -->
# sources/sync-backup/borg/src/borg/testsuite/shell_completions_test.py

## Purpose
Validates that Borg's Fish shell completion file is present and syntactically sourceable by Fish. It is a smoke test for generated/distributed shell completion assets.

## Important APIs, Types, and Functions
Uses `SHELL_COMPLETIONS_DIR`, `Path`, `subprocess.run`, and `pytest.skip`. The sole test is `test_fish_completion_is_valid`.

## Control Flow
The test computes the repository-relative completion path, asserts `scripts/shell_completions/fish/borg.fish` exists, probes `fish --version`, skips if Fish is unavailable, then sources the completion file with `fish -c`.

## State and Persistence Behavior
No persistent state is modified. The test reads a checked-in completion file and depends on the host system having Fish installed for full validation.

## Dependencies and Integration Points
Integrates the test suite with shell completion packaging. It catches syntax regressions that normal Python tests would miss.

## Risks and Test Signals
Risks are environment-dependent skips and shell-specific quoting errors. The key signal is zero exit status when sourcing the Fish completion file, with stderr reported on failure.
<!-- END_FILE_RESEARCH: sources/sync-backup/borg/src/borg/testsuite/shell_completions_test.py -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/borg/src/borg/testsuite/storelocking_test.py -->
# sources/sync-backup/borg/src/borg/testsuite/storelocking_test.py

## Purpose
Tests Borg store-backed locking semantics for exclusive and non-exclusive locks. It verifies context-manager acquisition, lock conflict behavior, stale lock cleanup, break-lock behavior, and lock migration across process identity changes.

## Important APIs, Types, and Functions
Uses `borgstore.store.Store`, `Lock`, `NotLocked`, `LockTimeout`, `ID1`, `ID2`, and the `lockstore` fixture. Test methods cover `got_exclusive_lock`, `acquire`, `release`, `break_lock`, `refresh`, `_get_locks`, `_find_locks`, and `migrate_lock`.

## Control Flow
The fixture creates a temporary store with lock configuration and destroys it after use. Tests acquire locks in nested contexts, expect timeouts for incompatible locks, allow double shared locks, assert releasing an unheld lock fails, refresh after age thresholds, then let stale locks expire.

## State and Persistence Behavior
Lock state is stored under the store's `locks/` namespace. Refresh creates new lock keys, stale discovery removes expired locks, and migration rewrites lock identity from old host/pid tuple to a new tuple.

## Dependencies and Integration Points
Integrates object-store primitives with repository/session coordination. It covers the behavior Borg depends on to prevent concurrent writers and permit shared readers.

## Risks and Test Signals
Risks include stale lock buildup, split-brain exclusive locks, shared/exclusive conflict mistakes, and PID changes after daemonization. Signals are raised `LockTimeout`/`NotLocked`, lock key set changes after refresh, empty store lock list after stale cleanup, and hostid changes after migration.
<!-- END_FILE_RESEARCH: sources/sync-backup/borg/src/borg/testsuite/storelocking_test.py -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/borg/src/borg/testsuite/version_test.py -->
# sources/sync-backup/borg/src/borg/testsuite/version_test.py

## Purpose
Tests Borg's remote-protocol version tuple parser and formatter. It ensures setuptools-scm-derived strings collapse into stable comparable tuples and that tuple formatting reverses the supported subset.

## Important APIs, Types, and Functions
Exercises `parse_version` and `format_version` from `borg.version` with pytest parametrization. Supported prerelease tags are `.dev`, `a`, `b`, and `rc`; final releases use sentinel `-1`.

## Control Flow
Parameterized parse tests pass final versions, prereleases, and setuptools local/date suffix examples. Invalid strings lacking `x.y.z` shape are expected to raise `ValueError`. Format tests convert tuples back to canonical strings.

## State and Persistence Behavior
No mutable state. The tuple format is effectively protocol state because remote compatibility depends on stable ordering semantics.

## Dependencies and Integration Points
This file directly guards `borg.version`, which is consumed by remote negotiation and version comparisons.

## Risks and Test Signals
Risks are changing tuple encodings in a remote-protocol-breaking way, accepting malformed short versions, or formatting prereleases incorrectly. Signals are exact tuple equality and exact string equality.
<!-- END_FILE_RESEARCH: sources/sync-backup/borg/src/borg/testsuite/version_test.py -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/borg/src/borg/testsuite/xattr_test.py -->
# sources/sync-backup/borg/src/borg/testsuite/xattr_test.py

## Purpose
Tests Borg extended attribute wrappers for filesystem enablement, get/set/list behavior, buffer growth, length-prefixed string splitting, symlink behavior, and fakeroot flag detection.

## Important APIs, Types, and Functions
Uses `is_enabled`, `getxattr`, `setxattr`, `listxattr`, `XATTR_FAKEROOT`, `platform.xattr.buffer`, `split_lstring`, and `is_linux`. Helper `assert_equal_se` ignores common system attributes.

## Control Flow
The fixture creates a temp file and symlink only if xattrs are available. Tests set multiple user attributes on file paths and fds, optionally symlink attrs on non-Linux, force small platform buffers, and verify buffer resizing during list/get operations.

## State and Persistence Behavior
State lives in filesystem xattrs on temporary files/symlinks and in the platform xattr buffer singleton. Empty xattr values are distinct and must round trip as `b""`.

## Dependencies and Integration Points
Integrates Borg's portable xattr layer with platform-specific wrappers, Linux symlink restrictions, SELinux/macOS provenance filtering, and fakeroot environment detection.

## Risks and Test Signals
Risks include buffer truncation, platform-specific symlink errors, false fakeroot detection, and races with system-added xattrs. Signals are exact xattr lists/values after filtering, buffer length growth, `split_lstring` results, and `XATTR_FAKEROOT` false conditions.
<!-- END_FILE_RESEARCH: sources/sync-backup/borg/src/borg/testsuite/xattr_test.py -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/borg/src/borg/upgrade.py -->
# sources/sync-backup/borg/src/borg/upgrade.py

## Purpose
Defines `UpgraderNoOp`, the baseline upgrader used when no transformation is required during archive/item/chunk transfer. It preserves selected archive metadata while dropping version/stats-specific fields.

## Important APIs, Types, and Functions
Class `UpgraderNoOp` exposes `new_archive`, `upgrade_item`, `upgrade_compressed_chunk`, and `upgrade_archive_metadata`. It stores `args` from initialization and inspects `args.chunker_params`.

## Control Flow
Most hooks are identity/no-op paths: new archives do nothing, items are returned unchanged, and compressed chunks return their metadata/data pair. Archive metadata is copied into a new dictionary for allowed attributes, with `cwd` normalized through `getattr`.

## State and Persistence Behavior
No file-backed state is owned. The returned metadata dictionary controls what future archive metadata persistence will include. Rechunking replaces `chunker_params` with CLI-provided values.

## Dependencies and Integration Points
Integrates transfer/upgrade code with archive save logic that interprets `cwd=None` as "leave unset". Uses Borg logger creation but does not log in this implementation.

## Risks and Test Signals
Risks are dropping metadata that should survive upgrade, retaining stale version/stats fields, or mishandling rechunking parameters. Tests should assert preserved fields, intentional omission of stats/version, identity item/chunk paths, and chunker replacement when requested.
<!-- END_FILE_RESEARCH: sources/sync-backup/borg/src/borg/upgrade.py -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/borg/src/borg/version.py -->
# sources/sync-backup/borg/src/borg/version.py

## Purpose
Implements Borg's simple version string parser and formatter for a protocol-stable integer tuple representation. It intentionally supports only `major.minor.patch` plus known prerelease forms.

## Important APIs, Types, and Functions
Exports `parse_version(version)` and `format_version(version)`. Prerelease mapping is `dev -> -9`, `a -> -4`, `b -> -3`, `rc -> -2`; final versions append `-1`.

## Control Flow
`parse_version` matches a verbose regex from the start of the string, extracts numeric parts, and appends prerelease markers if the optional group matched. `format_version` iterates tuple parts until it sees a negative sentinel, appending prerelease text to the previous numeric component.

## State and Persistence Behavior
No runtime persistence. The tuple format is part of the remote protocol, so changes persist externally as compatibility behavior between Borg versions.

## Dependencies and Integration Points
Depends only on `re`. Consumed by version tests and remote/protocol code that compares tuples lexicographically.

## Risks and Test Signals
Risks include regex accepting unwanted suffixes by prefix match, breaking tuple ordering, unknown negative markers causing `KeyError`, and malformed tuples. Tests cover valid/invalid parsing and canonical formatting.
<!-- END_FILE_RESEARCH: sources/sync-backup/borg/src/borg/version.py -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/borg/src/borg/xattr.py -->
# sources/sync-backup/borg/src/borg/xattr.py

## Purpose
Provides Borg's high-level extended attribute operations across Linux, FreeBSD, and macOS, including fakeroot detection and tolerant bulk get/set helpers.

## Important APIs, Types, and Functions
Exports `XATTR_FAKEROOT`, `is_enabled(path=None)`, `get_all(path, follow_symlinks=False)`, and `set_all(path, xattrs, follow_symlinks=False)`. Re-exports/imports platform functions `listxattr`, `getxattr`, `setxattr`, and `ENOATTR`.

## Control Flow
At import time, Linux fakeroot support is detected by scanning `LD_PRELOAD` for `libfakeroot`, running `fakeroot -v`, and requiring version at least 1.20.2. `is_enabled` writes and reads a temporary user xattr. `get_all` lists names, reads values individually, ignores disappearing attrs, and warns on unreadable attrs. `set_all` applies each attr and returns a warning flag.

## State and Persistence Behavior
State is filesystem xattrs on caller paths. Empty values use `None` in the all-xattrs mapping. Import-time `XATTR_FAKEROOT` is process-global and reflects the startup environment.

## Dependencies and Integration Points
Depends on platform xattr bindings, `packaging.version`, subprocess environment preparation, and Borg logging. Used by metadata backup/restore and tests that require xattr round trips.

## Risks and Test Signals
Risks include filesystem/platform unsupported errors, races between list and get, warning-only restoration failures, fakeroot subprocess dependency, and confusing `None` vs empty bytes. Tests should exercise unsupported filesystems, EPERM/EINVAL warning paths, empty values, symlinks, and fakeroot environment combinations.
<!-- END_FILE_RESEARCH: sources/sync-backup/borg/src/borg/xattr.py -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/bup/.cirrus.yml -->
# sources/sync-backup/bup/.cirrus.yml

## Purpose
Defines Cirrus CI tasks for bup across Debian, FreeBSD, and macOS. It runs normal checks, long checks, lint/dev checks, dependency preparation, and diagnostic scripts.

## Important APIs, Types, and Functions
CI tasks include `debian check (root)`, `debian long-check`, `debian check / lint`, `freebsd check / lint`, and `macos check / lint`. They invoke `dev/prep-for-*`, `dev/system-info`, `./configure`, `make check`, `make long-check`, and `make dev-check`.

## Control Flow
All tasks are skipped on `master` via `only_if`. Debian root check loads FUSE/loop modules and checks as root. Long/dev checks create a `bup` user and run make under that user. macOS installs Homebrew dependencies and an external bup for comparison.

## State and Persistence Behavior
CI mutates container/VM packages, creates users, changes checkout ownership, generates config/build/test artifacts, and may preserve failure diagnostics through `config.log`.

## Dependencies and Integration Points
Integrates platform prep scripts, GNU make targets, Python config selection, FUSE/loop availability, external packaged bup comparison, and lint tooling.

## Risks and Test Signals
Risks are OS package drift, Homebrew path/readline differences, root-vs-user behavior, and hidden configure failures. Signals are successful configure, system-info output, `make -j6` check/dev-check/long-check completion, and `config.log` printed on failure.
<!-- END_FILE_RESEARCH: sources/sync-backup/bup/.cirrus.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/bup/GNUmakefile -->
# sources/sync-backup/bup/GNUmakefile

## Purpose
Top-level GNU make build, install, test, documentation, cleanup, and compatibility target file for bup. It enforces GNU make 4.2+, records the make executable, includes configure output, builds C binaries/extensions, generates docs, prepares sample data, and runs tests/lint.

## Important APIs, Types, and Functions
Major targets are `all`, `install`, `check`, `dev-check`, `distcheck`, `long-check`, `Documentation/all`, `update-doc-branches`, `clean`, and legacy aliases. It builds `dev/python`, `dev/bup-exec`, `dev/bup-python`, `lib/cmd/bup`, and `lib/bup/_helpers$(soext)`.

## Control Flow
The file verifies make version, records `config/config.var/make`, includes `config/config.vars`, calculates OS/doc/sampledata settings, updates checkout info, compiles C objects with configured flags, validates the embedded Python launcher, and runs pytest with xdist derived from make parallelism.

## State and Persistence Behavior
Generated state includes `config/config.vars`, `config/config.h`, `config/config.var/*`, `lib/bup/checkout_info.py`, built binaries/shared objects, dependency `.d` files, docs, sampledata, `.pytest_cache`, and `test/tmp`. Install writes into `DESTDIR`-prefixed bin/lib/doc/man paths.

## Dependencies and Integration Points
Consumes `configure` outputs, platform prep scripts, `dev/refresh`, `dev/configure-sampledata`, C sources under `src/` and `lib/`, docs tooling (`pandoc`, `dot`), pytest, pylint, and shadow-bin to prevent accidental installed-bup use.

## Risks and Test Signals
Risks include stale configure state, wrong Python/readline flags, platform-specific shared-library extension mismatch, docs tool drift, cleanup of mounted test filesystems, and accidental local bup execution. Signals are successful `all`, `check`, `dev-check`, `clean`, generated dependency inclusion, shadow-bin assertion, and reproducible sampledata revision.
<!-- END_FILE_RESEARCH: sources/sync-backup/bup/GNUmakefile -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/bup/config/test/have-acls.c -->
# sources/sync-backup/bup/config/test/have-acls.c

## Purpose
Configure-time C probe that checks for complete POSIX ACL support needed by bup.

## Important APIs, Types, and Functions
Includes `<sys/acl.h>` and `<acl/libacl.h>`, then references `acl_from_text`, `acl_get_file`, `acl_set_file`, `acl_extended_file`, and `acl_to_any_text` from `main`.

## Control Flow
The program only prints function pointer values. Successful compilation/linking proves headers and symbols are usable.

## State and Persistence Behavior
No persistent state. Its success influences generated `config/config.h` and `config/config.vars` ACL flags.

## Dependencies and Integration Points
Called by `configure` with pkg-config or `-lacl` flags. Enables `_helpers.c` ACL read/apply functions and build/link flags.

## Risks and Test Signals
Risk is false-positive support if symbols compile but runtime filesystem support is absent. The configure signal is compile/link success for all required ACL functions.
<!-- END_FILE_RESEARCH: sources/sync-backup/bup/config/test/have-acls.c -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/bup/config/test/hello.c -->
# sources/sync-backup/bup/config/test/hello.c

## Purpose
Minimal configure-time C compiler sanity probe.

## Important APIs, Types, and Functions
Includes `<stdio.h>` and defines `main` that prints `Hello world!`.

## Control Flow
`configure` attempts to compile it with `-Wall -Werror`; execution is not required.

## State and Persistence Behavior
No state. Compile failure aborts configuration before generated config files are written.

## Dependencies and Integration Points
Used by `configure` to validate the selected `CC`.

## Risks and Test Signals
Signals are successful compilation with strict warnings. Risk is minimal; if this fails, the C toolchain is unusable for bup.
<!-- END_FILE_RESEARCH: sources/sync-backup/bup/config/test/hello.c -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/bup/configure -->
# sources/sync-backup/bup/configure

## Purpose
Bash configure script that discovers bup's C compiler, Python build flags, platform headers/functions, readline, libacl, and writes generated configuration files.

## Important APIs, Types, and Functions
Functions include `info`, `die`, `usage`, `find-cmd`, `find-prog`, `try-c-code`, `add-cflag-if-supported`, `find-header`, `summarize`, and trap handler `on-exit`. Outputs are `config/config.h`, `config/config.var/*`, and `config/config.vars`.

## Control Flow
Parses `--with-pylint`, redirects logs to `config.log`, selects `CC`, compiles `hello.c`, probes warning/aliasing/wrap flags, finds `python3.x-config`, obtains embed/non-embed flags, checks headers/mincore/readline/libacl, writes config with `dev/refresh`, and removes generated files on failure.

## State and Persistence Behavior
Successful configuration is represented by `config/config.vars`. Temporary files live under `config/tmp`; failure removes outputs to avoid inconsistent state. `config/config.var` records `bup-python-config` and `with-pylint`.

## Dependencies and Integration Points
Feeds `GNUmakefile` build variables and C preprocessor flags. Depends on compiler, pkg-config, git, Python config scripts, readline/libacl headers/libs, and `dev/refresh`.

## Risks and Test Signals
Risks include shell quoting limitations for flags with spaces, pkg-config/header mismatch, Python embed flag fallback, and feature probes silently disabling capabilities. Signals are generated config files, summarized found features, and clean failure with `config.log`.
<!-- END_FILE_RESEARCH: sources/sync-backup/bup/configure -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/bup/conftest.py -->
# sources/sync-backup/bup/conftest.py

## Purpose
Pytest configuration for bup tests. It sets common environment isolation, source import path, deterministic temp directories, saved-error checks, and collection ordering.

## Important APIs, Types, and Functions
Defines hooks `pytest_runtest_makereport` and `pytest_collection_modifyitems`, helper `bup_test_sort_order`, autouse fixtures `no_lingering_errors` and `common_test_environment`, and fixture `tmpdir`.

## Control Flow
At import, it prepends `lib` to `sys.path`, sets `BUP_TEST_LEVEL`, `BUP_DIR`, and `GIT_DIR`, normalizes cwd, and creates `test/tmp`. Each test gets a temporary `HOME`, environment restoration, saved-errors clear/check before and after, and per-test temp directory cleanup or preservation on failure.

## State and Persistence Behavior
Mutates process environment and cwd during tests, creates `test/tmp/home-*` and test-specific temp dirs, and preserves failed-test homes/tmpdirs for debugging. `helpers.saved_errors` is treated as a failure ledger.

## Dependencies and Integration Points
Integrates pytest with `bup.helpers.finalized`, byte environment helpers, test ordering for slow tests, and bup's global error collection.

## Risks and Test Signals
Risks include autouse fixture masking env interactions, unsafe cleanup permissions, and reliance on `request.node.bup['call-report']`. Signals are no lingering saved errors, isolated `HOME`, restored env/TZ, and preserved artifacts only on failures.
<!-- END_FILE_RESEARCH: sources/sync-backup/bup/conftest.py -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/bup/dev/checksum -->
# sources/sync-backup/bup/dev/checksum

## Purpose
Portable helper to compute a SHA1 or SHA256 digest from a path or stdin across GNU/Linux and BSD/macOS command naming.

## Important APIs, Types, and Functions
Shell options parse `-t sha1|sha256`, optional `--`, and optional single `PATH`. It chooses `sha1sum`/`sha256sum` when available or `sha1`/`sha256 -q` otherwise.

## Control Flow
Validates arguments, records the selected digest kind, runs the platform command with or without a source path, and strips GNU `*sum` filename suffixes by printing text before the first space.

## State and Persistence Behavior
No persistent state; reads stdin or one file.

## Dependencies and Integration Points
Used by tests/dev scripts needing platform-neutral checksums.

## Risks and Test Signals
Risks are unusual filename output formats, missing digest utilities, and stdin handling. Signals are exact hex digest and exit 2 on misuse or missing tools.
<!-- END_FILE_RESEARCH: sources/sync-backup/bup/dev/checksum -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/bup/dev/cleanup-mounts-under -->
# sources/sync-backup/bup/dev/cleanup-mounts-under

## Purpose
Polyglot shell/Python cleanup utility used by `make clean` to unmount FUSE or other mounts under target directories without relying on configured bup executables.

## Important APIs, Types, and Functions
Bootstraps a suitable Python interpreter, defines `mntent_unescape`, reads `/proc/mounts`, and runs `fusermount -uz` for FUSE filesystems or `umount -l` for others.

## Control Flow
For each target, verifies it is a directory, resolves its real path, scans mount entries, unescapes mountpoint names, and unmounts entries equal to or below the target.

## State and Persistence Behavior
Mutates system mount state; no files are written. Returns nonzero if targets are invalid or unmounts fail.

## Dependencies and Integration Points
Integrated into `GNUmakefile clean` before deleting test mount trees. Linux-specific `/proc/mounts`; no-op on platforms without it.

## Risks and Test Signals
Risks include common-prefix path checks, unmounting active mounts, missing `fusermount`, and no `/proc/mounts` on non-Linux. Signals are exit status and stderr diagnostics.
<!-- END_FILE_RESEARCH: sources/sync-backup/bup/dev/cleanup-mounts-under -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/bup/dev/clear-bupm-entries -->
# sources/sync-backup/bup/dev/clear-bupm-entries

## Purpose
Developer utility to replace selected metadata entries in a `.bupm` stream with empty entries for corruption/edge-case testing.

## Important APIs, Types, and Functions
Bootstraps `dev/bup-python`, uses `argparse`, `metadata._ArchiveIterator`, and `Metadata().write`.

## Control Flow
Parses zero-based indexes, iterates metadata records from stdin, writes empty metadata for requested indexes, writes original records otherwise, and errors if requested indexes were not present.

## State and Persistence Behavior
Transforms stdin to stdout; does not persist files itself. Output stream is a modified archive metadata stream.

## Dependencies and Integration Points
Depends on bup metadata encoding and the developer Python launcher.

## Risks and Test Signals
Risks are private `_ArchiveIterator` coupling and index mismatch. Signals are output stream decodability and exit 2 when requested entries do not exist.
<!-- END_FILE_RESEARCH: sources/sync-backup/bup/dev/clear-bupm-entries -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/bup/dev/compare-trees -->
# sources/sync-backup/bup/dev/compare-trees

## Purpose
Compares two filesystem trees as closely as bup can restore them, using rsync dry-run output as the difference oracle.

## Important APIs, Types, and Functions
Options include `-c`, `-x`, `--times`, `--no-times`, `--features`, and `--`. Builds rsync options `-rlpgoD -niH --delete` plus optional checksum, times, ACLs, and xattrs.

## Control Flow
Parses options, inspects `rsync --version` for ACL/xattr support, optionally prints feature support, runs rsync dry-run into a temp file, retries without `-X` if xattrs fail, and fails if any differences are reported.

## State and Persistence Behavior
Creates a temporary output file under `/tmp`; does not modify source/dest because rsync runs with `-n`.

## Dependencies and Integration Points
Used by restore/integration tests to compare bup output to source trees. Depends on rsync feature reporting and platform `OSTYPE`.

## Risks and Test Signals
Risks include rsync output semantics, unsupported ACL/xattr comparison, and timestamp policy differences. Signals are zero diff lines, feature output, and nonzero exit on differences.
<!-- END_FILE_RESEARCH: sources/sync-backup/bup/dev/compare-trees -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/bup/dev/configure-sampledata -->
# sources/sync-backup/bup/dev/configure-sampledata

## Purpose
Creates or cleans versioned sample data used by bup tests and the make build.

## Important APIs, Types, and Functions
Supports `--setup`, `--clean`, and `--revision`; internal `revision=3`, `rm_symlinks`, and `clean`.

## Control Flow
`--setup` cleans legacy/sample data, creates `test/sampledata/var`, symlinks, FIFO, copied Python/docs content, optional randomized path zoo, and `rev/v3` marker. `--clean` removes generated var/legacy entries. `--revision` prints the revision.

## State and Persistence Behavior
Writes generated sampledata under `test/sampledata/var` and removes prior generated data. The revision marker is a make dependency.

## Dependencies and Integration Points
Called by `GNUmakefile all/clean`; uses `dev/make-random-paths` when randomized sample paths are enabled.

## Risks and Test Signals
Risks include stale sampledata after content shape changes without revision bump, platform FIFO/symlink support, and optional random path instability. Signals are existence of `rev/v3` and clean idempotence.
<!-- END_FILE_RESEARCH: sources/sync-backup/bup/dev/configure-sampledata -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/bup/dev/data-size -->
# sources/sync-backup/bup/dev/data-size

## Purpose
Reports total apparent byte size of files under one or more paths for tests and dev diagnostics.

## Important APIs, Types, and Functions
Bootstraps `dev/bup-exec`, uses `bup.compat.get_argvb`, `os.walk`, `os.path.getsize`, and `isdir`.

## Control Flow
Iterates byte paths from argv, recursively sums regular file sizes for directories, directly sums file sizes for non-directories, and prints the total.

## State and Persistence Behavior
Read-only filesystem traversal; no persistence.

## Dependencies and Integration Points
Used where tests need byte-exact apparent data size independent of shell glob encoding.

## Risks and Test Signals
Risks include walk errors raising, symlink/file type behavior inherited from `os.walk`, and concurrent changes. Signal is exact integer output.
<!-- END_FILE_RESEARCH: sources/sync-backup/bup/dev/data-size -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/bup/dev/echo-argv-bytes -->
# sources/sync-backup/bup/dev/echo-argv-bytes

## Purpose
Debug/test utility that writes argv byte values exactly, preserving non-text path encodings.

## Important APIs, Types, and Functions
Bootstraps `dev/bup-exec`, uses `bup.compat.get_argvb`, `os.write`, and stdout.

## Control Flow
Loops over argv bytes, writes each argument followed by `NUL` and newline, and flushes stdout.

## State and Persistence Behavior
No persistence; output is raw bytes.

## Dependencies and Integration Points
Supports tests for command-line byte handling and filesystem path encoding.

## Risks and Test Signals
Risks are stdout text wrapper interference avoided via `os.write`. Signal is byte-exact output including argv[0].
<!-- END_FILE_RESEARCH: sources/sync-backup/bup/dev/echo-argv-bytes -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/bup/dev/force-delete -->
# sources/sync-backup/bup/dev/force-delete

## Purpose
Best-effort recursive deletion helper for stubborn test directories with restrictive permissions, ACLs, or Linux attributes.

## Important APIs, Types, and Functions
Runs `rm -rf`, optional `setfacl -Rb`, optional `chattr -R -aisu`, `chmod -R u+rwX`, `rm -r`, and diagnostics `find`, `lsattr`, `getfacl`.

## Control Flow
Attempts normal recursive delete first, then for remaining paths strips ACLs/attributes, fixes user permissions, retries removal, and records failure if the path remains.

## State and Persistence Behavior
Destructively removes requested paths and mutates metadata/permissions before deletion.

## Dependencies and Integration Points
Used by `make clean` for test tmp cleanup.

## Risks and Test Signals
Risks are destructive misuse on wrong paths and missing diagnostic tools. Signals are exit code 0 for full deletion, exit 1 with listings on failure.
<!-- END_FILE_RESEARCH: sources/sync-backup/bup/dev/force-delete -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/bup/dev/git-cat-tree -->
# sources/sync-backup/bup/dev/git-cat-tree

## Purpose
Recursively dumps all blob contents reachable from a Git tree/object ID.

## Important APIs, Types, and Functions
Shell function `cat-item` calls `git cat-file -t`, `git cat-file blob`, and `git ls-tree`. Supports optional `--git-dir DIR`.

## Control Flow
Validates args, optionally exports `GIT_DIR`, determines root object type, recurses through tree entries, writes blob contents in tree traversal order, and errors on unexpected object types.

## State and Persistence Behavior
Read-only Git object traversal; output is concatenated blob data.

## Dependencies and Integration Points
Used by tests/dev tooling that need raw subtree content independent of checkout.

## Risks and Test Signals
Risks include parsing `git ls-tree` text with tabs/spaces and lack of blob separators. Signal is successful recursive content dump or failure on non-tree/blob.
<!-- END_FILE_RESEARCH: sources/sync-backup/bup/dev/git-cat-tree -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/bup/dev/groups -->
# sources/sync-backup/bup/dev/groups

## Purpose
Prints current process group names, including the effective gid when `os.getgroups()` omits it.

## Important APIs, Types, and Functions
Bootstraps `dev/python`; uses `os.getegid`, `os.getgroups`, and `grp.getgrgid`.

## Control Flow
Collects groups, appends egid if missing, resolves group names, and prints them space-separated.

## State and Persistence Behavior
No persistence; reads process credentials and system group database.

## Dependencies and Integration Points
Parallels `helpers.getgroups()` behavior for test/dev scripts.

## Risks and Test Signals
Risks are unknown gids raising and platform group semantics. Signal is group-name output matching process membership.
<!-- END_FILE_RESEARCH: sources/sync-backup/bup/dev/groups -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/bup/dev/hardlink-sets -->
# sources/sync-backup/bup/dev/hardlink-sets

## Purpose
Lists hardlink groups beneath supplied paths, one group per block, for restore/index validation.

## Important APIs, Types, and Functions
Bootstraps `dev/bup-exec`, uses `get_argvb`, `os.walk`, `os.lstat`, `st_dev/st_ino`, and `byte_stream`.

## Control Flow
Builds a map from device/inode to full byte paths for all non-directory files, sorts paths within each group and groups by first path, and prints only groups with more than one path separated by blank lines.

## State and Persistence Behavior
Read-only traversal; no persistence.

## Dependencies and Integration Points
Used by tests checking hardlink preservation across save/restore.

## Risks and Test Signals
Risks include concurrent filesystem mutation and hardlink semantics across filesystems. Signal is deterministic sorted byte-path grouping.
<!-- END_FILE_RESEARCH: sources/sync-backup/bup/dev/hardlink-sets -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/bup/dev/have-pylint -->
# sources/sync-backup/bup/dev/have-pylint

## Purpose
Small probe for whether pylint imports successfully under bup's configured Python runtime.

## Important APIs, Types, and Functions
Bootstraps `dev/bup-exec` and attempts `import pylint`.

## Control Flow
Exits 0 if import succeeds, 1 on `ImportError`, and 2 with error text for other exceptions.

## State and Persistence Behavior
No persistence.

## Dependencies and Integration Points
Used by build/lint configuration to distinguish absent pylint from broken pylint.

## Risks and Test Signals
Signal is exit status. Risk is import side effects from installed pylint/plugin environment.
<!-- END_FILE_RESEARCH: sources/sync-backup/bup/dev/have-pylint -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/bup/dev/id-other-than -->
# sources/sync-backup/bup/dev/id-other-than

## Purpose
Finds a user or group ID/name different from excluded IDs/names for permission/ownership tests.

## Important APIs, Types, and Functions
Bootstraps `dev/bup-exec`, parses `--user` or `--group`, uses `pwd.getpwall`, `grp.getgrall`, `getpwnam`, and `getgrnam`.

## Control Flow
Builds an exclusion set from numeric arguments and resolved names, scans the user or group database, prints the first non-excluded `name:id`, and exits.

## State and Persistence Behavior
Read-only system account database access.

## Dependencies and Integration Points
Supports tests needing an alternate owner/group.

## Risks and Test Signals
Risks are systems with only excluded accounts or unresolved names. Signal is a valid `name:id` line or misuse exit.
<!-- END_FILE_RESEARCH: sources/sync-backup/bup/dev/id-other-than -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/bup/dev/lib.sh -->
# sources/sync-backup/bup/dev/lib.sh

## Purpose
Shared Bash helper library for bup development/test scripts.

## Important APIs, Types, and Functions
Defines `bup_dev_lib_top`, `bup_exit_failure`, `bup-cfg-py`, `bup-python`, `force-delete`, `resolve-parent`, `path-filesystems`, and `escape-erx`.

## Control Flow
Functions dispatch through repository-local dev executables, resolve parents through `bup.helpers.resolve_parent`, walk from a directory to root to print filesystem types, and escape regex metacharacters via sed.

## State and Persistence Behavior
No direct persistence. `force-delete` delegates destructive deletion.

## Dependencies and Integration Points
Sourced by Bash scripts that assume pipefail and source-tree cwd. Bridges shell tooling to configured bup Python.

## Risks and Test Signals
Risks are sourcing from wrong cwd and shell quoting around paths. Signals are correct helper outputs and successful delegated commands.
<!-- END_FILE_RESEARCH: sources/sync-backup/bup/dev/lib.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/bup/dev/make -->
# sources/sync-backup/bup/dev/make

## Purpose
Wrapper that re-executes the GNU make binary recorded during configuration.

## Important APIs, Types, and Functions
Reads `config/config.var/make` and `exec`s that command with all original arguments.

## Control Flow
If the recorded file cannot be read, prints a message asking the user to run GNU make first and exits 2. Otherwise replaces the process with the configured make.

## State and Persistence Behavior
Reads configure/build state only.

## Dependencies and Integration Points
Used by dev scripts such as doc-branch updates to ensure the same make implementation is used.

## Risks and Test Signals
Risk is stale or missing `config/config.var/make`. Signal is successful exec or clear exit 2.
<!-- END_FILE_RESEARCH: sources/sync-backup/bup/dev/make -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/bup/dev/make-random-paths -->
# sources/sync-backup/bup/dev/make-random-paths

## Purpose
Generates random byte-named files for path encoding and traversal stress tests.

## Important APIs, Types, and Functions
Bootstraps `dev/bup-exec`, uses `randint`, `re` invalid-fragment filtering, `fsencode`, `get_argvb`, and `open`.

## Control Flow
Parses `NUM DEST_DIR`, repeatedly creates 1 to 32 byte random names excluding NUL, slash, dot, and `..`, and writes empty files until count is reached.

## State and Persistence Behavior
Creates files in the destination directory.

## Dependencies and Integration Points
Used by `dev/configure-sampledata` when randomized sampledata paths are enabled.

## Risks and Test Signals
Risks are collisions, invalid path bytes on a filesystem, and unseeded randomness. Signal is the requested number of created files or error.
<!-- END_FILE_RESEARCH: sources/sync-backup/bup/dev/make-random-paths -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/bup/dev/make-splittable-tree -->
# sources/sync-backup/bup/dev/make-splittable-tree

## Purpose
Creates a large directory tree for split/index performance or behavior tests.

## Important APIs, Types, and Functions
Bootstraps `dev/python`, reads `BUP_SPLITTABLE_COUNT`, uses `mkdir` and empty `data` files.

## Control Flow
Requires one destination path, fails if it already exists, creates it, then creates numbered subdirectories each containing an empty file.

## State and Persistence Behavior
Writes a generated directory tree; default count is 10000.

## Dependencies and Integration Points
Used by tests/dev workflows that need many paths for splitting/indexing.

## Risks and Test Signals
Risks are large inode usage and existing target failure. Signal is exact tree shape and nonzero misuse exit.
<!-- END_FILE_RESEARCH: sources/sync-backup/bup/dev/make-splittable-tree -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/bup/dev/mksock -->
# sources/sync-backup/bup/dev/mksock

## Purpose
Creates a Unix-domain socket filesystem entry for metadata/save/restore tests.

## Important APIs, Types, and Functions
Bootstraps `dev/bup-exec`, creates `socket.AF_UNIX`, `SOCK_STREAM`, and binds to `get_argvb()[1]`.

## Control Flow
No explicit usage validation; it binds a socket to the first argument and exits, leaving the socket path.

## State and Persistence Behavior
Creates a socket node in the filesystem.

## Dependencies and Integration Points
Supports tests that need special file types.

## Risks and Test Signals
Risks are missing arg, stale existing path, and platform Unix socket availability. Signal is a created socket path.
<!-- END_FILE_RESEARCH: sources/sync-backup/bup/dev/mksock -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/bup/dev/ns-timestamp-resolutions -->
# sources/sync-backup/bup/dev/ns-timestamp-resolutions

## Purpose
Measures apparent nanosecond timestamp resolution for atime and mtime on a target filesystem.

## Important APIs, Types, and Functions
Bootstraps `dev/bup-exec`, uses bup `options`, `metadata.from_path`, `xstat.utime`, `argv_bytes`, and `saved_errors`.

## Control Flow
Parses one test filename, creates it, sets atime/mtime to `123456789` ns, reads metadata, computes trailing-zero decimal resolution for both timestamps, and prints two integers.

## State and Persistence Behavior
Creates/modifies the supplied test file. Reads bup metadata timestamps.

## Dependencies and Integration Points
Used by tests needing filesystem timestamp granularity.

## Risks and Test Signals
Risks include typo/undefined `log` in saved-error branch, filesystem rounding, and platform utime semantics. Signal is `atime_resolution mtime_resolution` output.
<!-- END_FILE_RESEARCH: sources/sync-backup/bup/dev/ns-timestamp-resolutions -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/bup/dev/path-fs -->
# sources/sync-backup/bup/dev/path-fs

## Purpose
Prints filesystem type for each supplied path in a platform-aware way.

## Important APIs, Types, and Functions
Uses `uname -s`, `df -G` on NetBSD, `df -g` on SunOS, and `df -T` with awk elsewhere.

## Control Flow
Defines an `fs` function based on kernel and loops over arguments printing one filesystem type per path.

## State and Persistence Behavior
Read-only system query.

## Dependencies and Integration Points
Used by `dev/lib.sh` and sparse-size fallback behavior.

## Risks and Test Signals
Risks are platform-specific `df` output changes and paths with unusual names. Signal is one filesystem type line per input.
<!-- END_FILE_RESEARCH: sources/sync-backup/bup/dev/path-fs -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/bup/dev/perf-glance -->
# sources/sync-backup/bup/dev/perf-glance

## Purpose
Quick manual performance glance for bup init/index/save/restore over supplied source data.

## Important APIs, Types, and Functions
Defines shell helpers `bup()` and `get-time()`, uses repository-local `./bup`, and runs `init`, `index`, `save -t`, and `restore`.

## Control Flow
Creates `test/tmp/perf-glance-*`, sets `BUP_DIR`, times each bup operation with Python `time.time()`, prints durations, and removes the temporary directory.

## State and Persistence Behavior
Creates a temporary bup repository and restore tree under `test/tmp`, then deletes it on normal completion.

## Dependencies and Integration Points
Requires a built `./bup` and source data paths. Useful for comparing performance changes.

## Risks and Test Signals
Risks are no cleanup on interrupted run, wall-clock variability, and source data dependence. Signals are printed operation durations and successful command completion.
<!-- END_FILE_RESEARCH: sources/sync-backup/bup/dev/perf-glance -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/bup/dev/perforate-repo -->
# sources/sync-backup/bup/dev/perforate-repo

## Purpose
Developer tool to intentionally remove selected object IDs from a Git/bup repository and repack it, creating damaged repositories for recovery/check tests.

## Important APIs, Types, and Functions
Bootstraps `dev/bup-python`, uses `argparse`, `git cat-file --batch-all-objects`, `git unpack-objects`, `git pack-objects`, `TemporaryDirectory`, and `unlink`.

## Control Flow
Requires `--drop-oids` and a repository. It unpacks all packs into a temporary bup repo, verifies object sets match, reads 40-character OIDs from stdin, deletes corresponding loose objects, removes original pack-related files, and repacks remaining objects into the original pack directory.

## State and Persistence Behavior
Destructively rewrites repository pack state and deletes selected objects. Temporary repo is under the victim repo and removed after use.

## Dependencies and Integration Points
Integrates Git plumbing with bup repository layout; caller must reset midx/bloom if needed.

## Risks and Test Signals
High risk by design: data loss, assumptions about no loose objects, SHA1-only OID regex, and locale/path assumptions. Signals are object-set verification and successful repack.
<!-- END_FILE_RESEARCH: sources/sync-backup/bup/dev/perforate-repo -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/bup/dev/prep-for-debianish-build -->
# sources/sync-backup/bup/dev/prep-for-debianish-build

## Purpose
Installs Debian/Ubuntu-style build and test dependencies for bup CI or local setup.

## Important APIs, Types, and Functions
Accepts optional `pyxattr` or `xattr` selector and installs packages including ACL/xattr tools, compilers, git, graphviz, pandoc, libacl/readline dev packages, pytest/xdist, tornado, FUSE, rsync, rdiff-backup, and duplicity.

## Control Flow
Validates xattr flavor, exports `DEBIAN_FRONTEND=noninteractive`, runs `apt-get update`, and installs the package list.

## State and Persistence Behavior
Mutates system package state.

## Dependencies and Integration Points
Used by Cirrus Debian tasks before configure and make targets.

## Risks and Test Signals
Risks include package name drift and root/package-manager requirements. Signal is successful apt install.
<!-- END_FILE_RESEARCH: sources/sync-backup/bup/dev/prep-for-debianish-build -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/bup/dev/prep-for-freebsd-build -->
# sources/sync-backup/bup/dev/prep-for-freebsd-build

## Purpose
Installs FreeBSD build/test dependencies for bup CI.

## Important APIs, Types, and Functions
Uses `pkg update` and `pkg install` for gmake, git, bash, rsync, curl, par2cmdline, readline, duplicity, rsnapshot, pandoc, graphviz, Python 3.11 packages, pytest, and xdist.

## Control Flow
Sets `ASSUME_ALWAYS_YES=yes`, updates package metadata, attempts `rdiff-backup` install tolerantly, then installs the main package set.

## State and Persistence Behavior
Mutates FreeBSD package state.

## Dependencies and Integration Points
Used by Cirrus FreeBSD task before `gmake dev-check`.

## Risks and Test Signals
Risks are package availability/version drift and tolerated rdiff-backup absence. Signal is package install completion.
<!-- END_FILE_RESEARCH: sources/sync-backup/bup/dev/prep-for-freebsd-build -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/bup/dev/prep-for-macos-build -->
# sources/sync-backup/bup/dev/prep-for-macos-build

## Purpose
Installs macOS build/test dependencies for bup CI using Homebrew and pip.

## Important APIs, Types, and Functions
Installs Homebrew if absent, then installs make, bash, par2, readline, rsync, pkg-config, md5sha1sum, Python, and pytest packages. Forces Homebrew readline link.

## Control Flow
Checks for `brew`, bootstraps it via official install script if needed, runs brew installs, force-links readline, then installs pytest/xdist with pip `--break-system-packages --user`.

## State and Persistence Behavior
Mutates Homebrew/pip state and readline symlink state.

## Dependencies and Integration Points
Used by Cirrus macOS task before configure/build.

## Risks and Test Signals
Risks are network/Homebrew drift, forced readline interference, and pip policy changes. Signal is successful dependency installation.
<!-- END_FILE_RESEARCH: sources/sync-backup/bup/dev/prep-for-macos-build -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/bup/dev/python.c -->
# sources/sync-backup/bup/dev/python.c

## Purpose
C wrapper executable for launching Python with bup's configured embedded Python flags.

## Important APIs, Types, and Functions
Includes generated `config/config.h`, Python headers, and `bup/compat.h`. Defines `bup_py_main` as `bup_py_bytes_main` before Python 3.8 or `Py_BytesMain` otherwise.

## Control Flow
`main` asserts `argc > 0` and delegates all args to the selected Python bytes-aware main function.

## State and Persistence Behavior
No persistence. Runtime behavior is process execution of Python.

## Dependencies and Integration Points
Built by `GNUmakefile` into `dev/python`; validated by `dev/validate-python`; used by scripts needing the configured Python runtime.

## Risks and Test Signals
Risks include Python C API version differences and config/header mismatch. Signals are successful compile/link and version validation.
<!-- END_FILE_RESEARCH: sources/sync-backup/bup/dev/python.c -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/bup/dev/refresh -->
# sources/sync-backup/bup/dev/refresh

## Purpose
Sponge-like helper that updates a destination file only when content changes, optionally appending and optionally reporting refreshes.

## Important APIs, Types, and Functions
Options are `-a`, `-v`, optional `--`, and `DEST`. Uses `mktemp`, `cp -Lp`, `cmp -s`, and `mv`.

## Control Flow
Copies existing destination permissions/content to a temp file if present, writes stdin by replace or append mode, compares temp with destination, and atomically moves temp into place only on content change.

## State and Persistence Behavior
Creates a temporary sibling file and may replace destination. Trap removes temp on exit.

## Dependencies and Integration Points
Used by `configure`, `update-checkout-info`, and generated docs/config workflows to avoid unnecessary rebuilds.

## Risks and Test Signals
Risks are temp filename creation next to nonexistent/permission-denied dest and symlink behavior via `cp -Lp`. Signals are unchanged mtime/content when equal and updated file when different.
<!-- END_FILE_RESEARCH: sources/sync-backup/bup/dev/refresh -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/bup/dev/root-status -->
# sources/sync-backup/bup/dev/root-status

## Purpose
Reports whether the current process is root, fakeroot, or non-root for tests.

## Important APIs, Types, and Functions
Bootstraps `dev/python`, uses `os.geteuid`, `FAKEROOTKEY`, and Cygwin group IDs 544/0.

## Control Flow
On Cygwin, checks effective group membership for administrator/root-like groups. Else prints `fake` if fakeroot is active, `root` if euid 0, otherwise `none`.

## State and Persistence Behavior
Read-only process credential/environment query.

## Dependencies and Integration Points
Used by tests that branch on root/fakeroot capability.

## Risks and Test Signals
Risks are Cygwin-specific group assumptions and fakeroot env spoofing. Signal is one of `root`, `fake`, or `none`.
<!-- END_FILE_RESEARCH: sources/sync-backup/bup/dev/root-status -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/bup/dev/shadow-bin/bup -->
# sources/sync-backup/bup/dev/shadow-bin/bup

## Purpose
Intentional failing `bup` executable placed early in `PATH` to catch tests or build steps that accidentally invoke an installed/local `bup` instead of repository wrappers.

## Important APIs, Types, and Functions
Shell script prints a fixed error message and exits 2.

## Control Flow
Always fails.

## State and Persistence Behavior
No persistence.

## Dependencies and Integration Points
Prepended to `PATH` by `GNUmakefile`; `run_check` asserts `command -v bup` points here while `./bup` is used explicitly.

## Risks and Test Signals
Signal is intentional failure on accidental `bup version`. Risk is scripts that legitimately need `bup` by PATH must override path intentionally.
<!-- END_FILE_RESEARCH: sources/sync-backup/bup/dev/shadow-bin/bup -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/bup/dev/shquote -->
# sources/sync-backup/bup/dev/shquote

## Purpose
Quotes a string for safe single-quoted shell use.

## Important APIs, Types, and Functions
Accepts zero args to read stdin or one arg directly; uses sed to replace single quotes and wrap with quotes.

## Control Flow
Validates arity, obtains source text, prints a single-quoted representation with embedded quotes escaped as `'\''`.

## State and Persistence Behavior
No persistence.

## Dependencies and Integration Points
General dev helper for shell command construction.

## Risks and Test Signals
Risks include multiline stdin semantics and shell portability. Signal is output that a POSIX shell reinterprets as the original string.
<!-- END_FILE_RESEARCH: sources/sync-backup/bup/dev/shquote -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/bup/dev/sort-z -->
# sources/sync-backup/bup/dev/sort-z

## Purpose
Portable null-delimited sort wrapper.

## Important APIs, Types, and Functions
Uses `sort -z` normally and `sort -R 000` on NetBSD.

## Control Flow
Checks `uname -s`; execs the appropriate sort command with original args.

## State and Persistence Behavior
No persistence; transforms stdin/files according to sort.

## Dependencies and Integration Points
Used by tests/scripts requiring NUL-delimited sorting across platforms.

## Risks and Test Signals
Risk is NetBSD option compatibility and differing sort collation. Signal is sorted NUL-delimited output.
<!-- END_FILE_RESEARCH: sources/sync-backup/bup/dev/sort-z -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/bup/dev/sparse-size -->
# sources/sync-backup/bup/dev/sparse-size

## Purpose
Computes sparse/hole byte count for a file, using `SEEK_DATA/SEEK_HOLE` when available and `du` fallback otherwise.

## Important APIs, Types, and Functions
Bootstraps `dev/bup-python`, parses `-v`, uses `os.lseek`, `SEEK_HOLE`, `SEEK_DATA`, `ENXIO`, `getsize`, fallback `du -s`, `path-fs`, and `BLOCKSIZE=512`.

## Control Flow
With seek support, walks hole/data extents and sums holes, logging when verbose. Without seek support, waits on btrfs/zfs for allocation to settle, compares apparent size to `du`, and prints apparent minus allocated bytes.

## State and Persistence Behavior
Read-only file inspection; fallback sleeps but does not modify files.

## Dependencies and Integration Points
Used by sparse-file tests to verify restore/save sparseness.

## Risks and Test Signals
Risks are filesystem-specific allocation reporting, btrfs/zfs delay heuristics, and `du` block-size behavior. Signal is exact sparse byte count.
<!-- END_FILE_RESEARCH: sources/sync-backup/bup/dev/sparse-size -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/bup/dev/sparse-test-data -->
# sources/sync-backup/bup/dev/sparse-test-data

## Purpose
Generates randomized test data with zero and nonzero regions around bup sparse-detection thresholds.

## Important APIs, Types, and Functions
Bootstraps `dev/bup-exec`; generator functions include `smaller_region`, `possibly_larger_region`, `initial_region`, `final_region`, and `region_around_min_len`.

## Control Flow
Chooses random output size up to ten read blocks, selects two sparse regions, merges overlap into offsets, alternates writing `x` and NUL byte runs, and logs offsets/write runs to stderr.

## State and Persistence Behavior
Writes a file supplied as the sole argument. Intended output may include holes only semantically as zero bytes, not filesystem sparse holes.

## Dependencies and Integration Points
Supports sparse write/read tests by producing threshold-sensitive byte patterns.

## Risks and Test Signals
Risks include apparent bug in zero-argument handling (`len(argv) == 0` impossible for normal argv) and unseeded randomness. Signals are generated file plus stderr offsets useful for debugging.
<!-- END_FILE_RESEARCH: sources/sync-backup/bup/dev/sparse-test-data -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/bup/dev/subtree-hash -->
# sources/sync-backup/bup/dev/subtree-hash

## Purpose
Finds the Git tree hash for a path within a root tree hash.

## Important APIs, Types, and Functions
Bootstraps `dev/bup-exec`, uses bup `options`, `argv_bytes`, `git ls-tree -z`, and byte-stream stdout.

## Control Flow
Parses `ROOT_HASH [PATH_ITEM...]`, iteratively lists the current tree, finds the named child entry, replaces the current tree hash with the child hash, and prints the final hash. If a path item is missing, prints an error and exits 1.

## State and Persistence Behavior
Read-only Git object lookup.

## Dependencies and Integration Points
Used by tests/dev scripts that need to verify tree identities inside bup/Git repositories.

## Risks and Test Signals
Risks include assuming path items are tree objects and parsing specific `git ls-tree` format. Signal is final hash on stdout or path-not-found failure.
<!-- END_FILE_RESEARCH: sources/sync-backup/bup/dev/subtree-hash -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/bup/dev/sync-tree -->
# sources/sync-backup/bup/dev/sync-tree

## Purpose
Synchronizes a destination tree to a source tree using rsync with bup-relevant metadata support where available.

## Important APIs, Types, and Functions
Uses rsync options `-aH --delete` plus optional `-A` for ACLs and `-X` for xattrs. Supports `-h`.

## Control Flow
Parses two paths, inspects rsync feature support and `OSTYPE`, tries rsync with xattrs when available, and retries without `-X` if xattr sync fails.

## State and Persistence Behavior
Mutates destination tree to match source and deletes extra destination files.

## Dependencies and Integration Points
Used by tests/dev workflows needing a reference tree copy.

## Risks and Test Signals
Risks include destructive `--delete`, platform ACL gaps, xattr failure fallback, and rsync feature output parsing. Signal is rsync exit status.
<!-- END_FILE_RESEARCH: sources/sync-backup/bup/dev/sync-tree -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/bup/dev/system-info -->
# sources/sync-backup/bup/dev/system-info

## Purpose
Prints OS, hardware, tool, filesystem, mount, identity, and cwd diagnostics for CI and failure debugging.

## Important APIs, Types, and Functions
Runs `uname -a`, platform-specific `/proc`/`sysctl`/`system_profiler`, `git --version`, `rsync --version`, optional `par2 -V`, `df -h`, `mount`, `id`, and `pwd`.

## Control Flow
Prints basic system info, branches by `OSTYPE`, enables shell tracing for command diagnostics, then runs tool/environment commands.

## State and Persistence Behavior
Read-only diagnostics.

## Dependencies and Integration Points
Called by Cirrus tasks before builds/tests.

## Risks and Test Signals
Risks are noisy logs and platform command availability. Signal is diagnostic output sufficient to debug CI environment differences.
<!-- END_FILE_RESEARCH: sources/sync-backup/bup/dev/system-info -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/bup/dev/unknown-owner -->
# sources/sync-backup/bup/dev/unknown-owner

## Purpose
Generates a user or group name that should be unknown by making it longer than any existing account/group name.

## Important APIs, Types, and Functions
Bootstraps `dev/python`, parses `--user` or `--group`, uses `pwd.getpwall` or `grp.getgrall`.

## Control Flow
Computes maximum name length in the selected database and prints `x` repeated one more than that.

## State and Persistence Behavior
Read-only system account/group database query.

## Dependencies and Integration Points
Supports tests for unknown owner/group metadata handling.

## Risks and Test Signals
Risks include empty databases and systems permitting very long names. Signal is a likely-unknown name string.
<!-- END_FILE_RESEARCH: sources/sync-backup/bup/dev/unknown-owner -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/bup/dev/update-checkout-info -->
# sources/sync-backup/bup/dev/update-checkout-info

## Purpose
Generates checkout metadata containing the current Git commit, commit date, and dirty status.

## Important APIs, Types, and Functions
Uses `pwd -P`, validates `lib/bup/bupsplit.c`, checks `.git`, runs `git status --porcelain -uno`, `git log -1 --pretty`, and writes through `dev/refresh`.

## Control Flow
Requires one destination path. If not in a Git checkout, removes the destination. Otherwise writes Python-style assignments `commit=`, `date=`, and `modified=` to the destination only when changed.

## State and Persistence Behavior
Creates/updates or removes the destination checkout info file, usually `lib/bup/checkout_info.py`.

## Dependencies and Integration Points
Called by `GNUmakefile`; installed as source info when present.

## Risks and Test Signals
Risks are dirty-state sensitivity and branchless/source-archive builds. Signals are generated metadata matching Git state and idempotent refresh behavior.
<!-- END_FILE_RESEARCH: sources/sync-backup/bup/dev/update-checkout-info -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/bup/dev/update-doc-branches -->
# sources/sync-backup/bup/dev/update-doc-branches

## Purpose
Updates dedicated Git branches containing generated manpage and HTML documentation from current Markdown docs.

## Important APIs, Types, and Functions
Requires full refs for man/html branches, checks clean working tree, runs `dev/make`, uses temporary Git index, `git add -f`, `git write-tree --prefix=Documentation`, `git commit-tree`, and `git update-ref`.

## Control Flow
Validates args/refs, refuses uncommitted changes, builds docs, creates a temp index, stages generated files per format, creates a commit with parent `refs/heads/<fmt>`, and updates the target ref.

## State and Persistence Behavior
Mutates Git refs for documentation branches and creates temporary index files under `t/tmp`.

## Dependencies and Integration Points
Invoked by `make update-doc-branches`; depends on doc generation and Git plumbing.

## Risks and Test Signals
Risks include hard-coded parent refs, destructive ref updates, clean-tree requirement, and missing `t/tmp` vs `test/tmp` convention. Signals are updated refs pointing to commits with generated docs.
<!-- END_FILE_RESEARCH: sources/sync-backup/bup/dev/update-doc-branches -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/bup/dev/validate-python -->
# sources/sync-backup/bup/dev/validate-python

## Purpose
Validates that a Python executable is new enough for bup.

## Important APIs, Types, and Functions
Runs the candidate with `-c 'import sys; print(sys.version_info[0/1])'` and `--version`.

## Control Flow
Requires one executable, reads major/minor version, and exits 2 with an error if Python is older than 3.7.

## State and Persistence Behavior
No persistence.

## Dependencies and Integration Points
Used by `GNUmakefile` before copying `dev/python-proposed` to `dev/python`.

## Risks and Test Signals
Risk is minor shell function typo (`die` defined, `usage` called) on misuse. Main signal is successful version check or explicit too-old error.
<!-- END_FILE_RESEARCH: sources/sync-backup/bup/dev/validate-python -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/bup/dev/with-tty -->
# sources/sync-backup/bup/dev/with-tty

## Purpose
Runs a command under a pseudo-terminal using the platform `script(1)` command, preserving child exit status where possible.

## Important APIs, Types, and Functions
Supports `with-tty command [arg ...]`; probes `script -qec`, `script -q -c`, and `script -q /dev/null command` variants; rejects NetBSD up front.

## Control Flow
Validates args, tries known script invocation forms with a `true` command, verifies false returns nonzero for variants lacking `-e`, then runs the requested command through the supported form.

## State and Persistence Behavior
No persistent files beyond `/dev/null` script output target.

## Dependencies and Integration Points
Used by tests needing terminal behavior. Depends on non-POSIX `script` command variants.

## Risks and Test Signals
Risks are platform-specific `script` semantics, quoted command construction, and NetBSD unsupported behavior. Signal is correct child exit propagation and PTY allocation.
<!-- END_FILE_RESEARCH: sources/sync-backup/bup/dev/with-tty -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/bup/lib/__init__.py -->
# sources/sync-backup/bup/lib/__init__.py

## Purpose
Empty package marker for bup's top-level `lib` import path.

## Important APIs, Types, and Functions
No code, exports, or runtime symbols.

## Control Flow
No executable control flow.

## State and Persistence Behavior
No state or persistence.

## Dependencies and Integration Points
Allows Python import machinery to treat `lib` as a package when repository-local paths are inserted during tests or execution.

## Risks and Test Signals
Risk is only packaging/import layout drift. Test signal is successful imports from the repository's `lib` tree.
<!-- END_FILE_RESEARCH: sources/sync-backup/bup/lib/__init__.py -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/bup/lib/bup/__init__.py -->
# sources/sync-backup/bup/lib/bup/__init__.py

## Purpose
Empty package initializer for the `bup` Python package.

## Important APIs, Types, and Functions
No code, exports, or runtime symbols.

## Control Flow
No executable control flow.

## State and Persistence Behavior
No state or persistence.

## Dependencies and Integration Points
Enables imports such as `from bup import helpers`, command modules, and extension modules from `lib/bup`.

## Risks and Test Signals
Risk is package discovery failure if removed or packaging metadata changes. Signal is successful import of bup modules.
<!-- END_FILE_RESEARCH: sources/sync-backup/bup/lib/bup/__init__.py -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/bup/lib/bup/_hashsplit.c -->
# sources/sync-backup/bup/lib/bup/_hashsplit.c

## Purpose
C implementation of bup's content-defined splitting Python extension types. It provides streaming file splitting and record-oriented split decisions using the rolling checksum from `bupsplit.h`.

## Important APIs, Types, and Functions
Defines Python types `_helpers.HashSplitter` and `_helpers.RecordHashSplitter`; initialization function `hashsplit_init`; helpers `HashSplitter_nextfile`, `HashSplitter_read`, `HashSplitter_roll`, `HashSplitter_iternext`, `RecordHashSplitter_feed`, and optional `HashSplitter_uncache`.

## Control Flow
`HashSplitter` iterates input files, reads fd or `.read()` data into an advice-sized buffer, finds rolling checksum boundaries, forces max-blob splits, optionally keeps file boundaries, and returns `(memoryview_slice, level)`. `RecordHashSplitter.feed` rolls through a supplied record and returns `(split, bits)` while resetting after split or max size.

## State and Persistence Behavior
State is in C structs: file iterator/current object, fd, buffer start/end, EOF, rollsum, split sizes, fanbits, progress callback, and optional mincore page cache tracking. It does not persist files but can issue `POSIX_FADV_DONTNEED`.

## Dependencies and Integration Points
Depends on generated config, Python C API, OS fd/read/mmap/mincore/fadvise support, `bup/intprops.h`, `bup/pyutil.h`, and `bupsplit.h`. Registered by `_helpers.c`.

## Risks and Test Signals
Risks include overflow, buffer lifetime via memoryviews, fd vs Python read behavior, page-cache advice correctness, and split boundary regressions. Signals are deterministic chunk boundaries, max-blob enforcement, progress callbacks, overflow exceptions, and rollsum selftests.
<!-- END_FILE_RESEARCH: sources/sync-backup/bup/lib/bup/_hashsplit.c -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/bup/lib/bup/_hashsplit.h -->
# sources/sync-backup/bup/lib/bup/_hashsplit.h

## Purpose
Header exposing hashsplit Python extension types and initializer to the `_helpers` module.

## Important APIs, Types, and Functions
Declares `PyTypeObject HashSplitterType`, `PyTypeObject RecordHashSplitterType`, and `int hashsplit_init(void)`.

## Control Flow
No executable control flow in the header. `_helpers.c` calls `hashsplit_init`, then adds the ready types to the module.

## State and Persistence Behavior
No state is owned here; declarations refer to C extension type objects defined in `_hashsplit.c`.

## Dependencies and Integration Points
Requires Python C API types from including translation units. Integrates `_hashsplit.c` with `_helpers.c`.

## Risks and Test Signals
Risks are type declaration/definition mismatch and initialization ordering. Signals are successful module import and availability of `_helpers.HashSplitter` and `_helpers.RecordHashSplitter`.
<!-- END_FILE_RESEARCH: sources/sync-backup/bup/lib/bup/_hashsplit.h -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/bup/lib/bup/_helpers.c -->
# sources/sync-backup/bup/lib/bup/_helpers.c

## Purpose
Main native Python extension module for bup performance and platform primitives. It combines sparse writing, rolling checksums, Bloom/midx/idx operations, random data generation, no-atime opens, Linux attributes, passwd/group wrappers, readline integration, ACL support, vint packing, string parsing, and hashsplit type registration.

## Important APIs, Types, and Functions
Exports methods `write_sparsely`, `selftest`, `rollsum`, `bitmatch`, `firstword`, `bloom_contains`, `bloom_add`, `extract_bits`, `merge_into`, `write_idx`, `write_random`, `random_sha`, `open_noatime`, `openat_noatime`, optional `get_linux_file_attr`/`set_linux_file_attr`, passwd/group lookups, hostname, optional readline callbacks, optional `read_acl`/`apply_acl`, `vuint_encode`, `vint_encode`, `limited_vint_pack`, and `strtoimax`.

## Control Flow
Module init calls `hashsplit_init`, creates the module, validates integral assumptions, sets constants, detects stderr TTY, imports `math.inf`, and registers types. Individual functions are mostly direct C/POSIX operations with Python argument parsing and overflow checks.

## State and Persistence Behavior
State includes module state `istty2`, global readline callback pointers, infinity objects, and hashsplit type globals. Persistent effects include writing sparse regions to fds, writing idx/midx mmaps, changing Linux file flags, applying ACLs, and reading account databases.

## Dependencies and Integration Points
Depends on generated config feature macros, Python C API, POSIX I/O, mmap/msync, Linux fs ioctls, readline, libacl, `bupsplit`, `_hashsplit`, and bup integer/pyutil helpers. It is the backend for Python modules such as `bup.bloom`, `bup.git`, sparse restore code, shell readline support, and metadata ACL handling.

## Risks and Test Signals
Risks are memory/buffer misuse, overflow, platform feature mismatch, endian/pack-index format errors, sparse-hole miscalculation, readline callback lifetime leaks, ACL unavailable behavior, and dirty mmap flushing. Signals include extension import, rollsum selftest, Bloom membership tests, idx/midx validation by Git, sparse-size tests, no-atime fallback, ACL round trips, and vint encode/decode compatibility.
<!-- END_FILE_RESEARCH: sources/sync-backup/bup/lib/bup/_helpers.c -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/bup/lib/bup/bloom.py -->
# sources/sync-backup/bup/lib/bup/bloom.py

## Purpose
Implements bup Bloom filter readers/writers over mmap-backed `.bloom` files, using C helpers for k=4/k=5 bit addressing. It accelerates object existence checks against pack indexes.

## Important APIs, Types, and Functions
Constants include `BLOOM_VERSION`, `MAX_BITS_EACH`, `MAX_BLOOM_BITS`, and `MAX_PFALSE_POSITIVE`. Classes are `_BloomBase`, `BloomReader`, `BloomWriter`, `BloomInvalid`, and `BloomNotFound`; helpers include `_validate_and_get_info`, `_create`, `_open_write_map`, and `clear_bloom`.

## Control Flow
Readers open and mmap existing bloom files, validate the `BLOM` header, version, bit count, k, entries, and idx names. Writers create or update through temporary files, choose k/bits from expected entries, add index shatables, optionally delay writes with a private mmap, update entry counts, append idx names, and atomically rename into place.

## State and Persistence Behavior
Persistent state is the `.bloom` file: 16-byte header, bit array of `2**bits` bytes, and NUL-delimited idx names. Runtime state tracks mmap/file/temp path, entries, k, bits, and delaywrite mode.

## Dependencies and Integration Points
Depends on `_helpers.bloom_contains`/`bloom_add`, bup mmap helpers, logging, umask handling, and index objects exposing `shatable`/`name`. Used by `bup bloom` and object index caches.

## Risks and Test Signals
Risks include false-positive tuning, invalid/old/new bloom rejection, interrupted temp files, mmap dirty-page behavior, and idx-name mismatch. Signals are header validation, pfalse calculations, object membership, atomic close/rename, and check-mode verification against idx contents.
<!-- END_FILE_RESEARCH: sources/sync-backup/bup/lib/bup/bloom.py -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/bup/lib/bup/bupsplit.c -->
# sources/sync-backup/bup/lib/bup/bupsplit.c

## Purpose
Implements rolling checksum support used by bup's content-defined splitter, plus an optional selftest.

## Important APIs, Types, and Functions
Exports `rollsum_sum(uint8_t *buf, size_t ofs, size_t len)` and, unless `BUP_NO_SELFTEST`, `bupsplit_selftest()`.

## Control Flow
`rollsum_sum` initializes a `Rollsum`, rolls bytes from offset to length, and returns the digest. The selftest fills a deterministic random buffer, compares rolling sums over shifted windows, prints sums, and returns nonzero on mismatch.

## State and Persistence Behavior
No persistence. State is stack/local rollsum and selftest heap buffer.

## Dependencies and Integration Points
Depends on `bupsplit.h` inline rollsum functions. Used by `_hashsplit.c` and `_helpers.c`.

## Risks and Test Signals
Risks are checksum regression altering split boundaries and selftest memory allocation failure not explicitly handled. Signals are selftest success and stable split behavior in higher-level tests.
<!-- END_FILE_RESEARCH: sources/sync-backup/bup/lib/bup/bupsplit.c -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/bup/lib/bup/bupsplit.h -->
# sources/sync-backup/bup/lib/bup/bupsplit.h

## Purpose
Header defining bup's rolling checksum state and inline operations for content-defined chunking.

## Important APIs, Types, and Functions
Defines `BUP_WINDOWBITS`, `BUP_WINDOWSIZE`, `ROLLSUM_CHAR_OFFSET`, `Rollsum`, `rollsum_init`, `rollsum_add`, `rollsum_roll`, `rollsum_digest`, `rollsum_sum`, and `bupsplit_selftest`.

## Control Flow
Inline functions initialize a rolling window, update checksum state by dropping/adding bytes, and combine `s1/s2` into a 32-bit digest. `rollsum_roll` is a macro for optimizer behavior.

## State and Persistence Behavior
No persistence. `Rollsum` stores rolling sums, a 64-byte window, and window offset.

## Dependencies and Integration Points
Used by `_hashsplit.c`, `_helpers.c`, and `bupsplit.c`.

## Risks and Test Signals
Risks are ABI/algorithm changes causing different chunk boundaries and dedup behavior. Signals are rollsum selftest and deterministic chunking tests.
<!-- END_FILE_RESEARCH: sources/sync-backup/bup/lib/bup/bupsplit.h -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/bup/lib/bup/client.py -->
# sources/sync-backup/bup/lib/bup/client.py

## Purpose
Implements bup's remote repository client and remote pack store. It supports SSH, TCP bup daemon, and reverse/fd transports, command negotiation, index syncing, remote object writes, refs, object reads, rev-list, path resolution, and remote config queries.

## Important APIs, Types, and Functions
Exports `ClientError`, `Config`, `Client`, and `RemotePackStore`. Internal context managers `_TypicalCall` and `_LineBasedCall` synchronize protocol calls. Transport classes are `ViaBupRev`, `ViaSsh`, and `ViaBup`.

## Control Flow
`Client.__init__` opens the selected transport, asks `help` for commands, optionally sets/init-dir, prepares cache by repo id or legacy id, then exposes methods for indexes, pack writing, refs, cat/join, rev-list, resolve, and config-get. `RemotePackStore.write` frames objects with length, SHA, CRC, and data, throttles by `bwlimit`, handles server suggestions, and finishes packs with a zero-length marker.

## State and Persistence Behavior
Persistent local state is the index cache directory and synced `.idx`/midx files. Remote state includes repository refs, objects, packs, and optional config. Runtime state tracks busy protocol command, transport handles, object cache, bandwidth counters, and pack-open state.

## Dependencies and Integration Points
Depends on `git`, `ssh`, `vint`, `protocol`, `PackWriter`, helper connection classes, path index cache, URL parsing, sockets, and zlib. It is the client side of the bup server protocol and must match server command names and framing.

## Risks and Test Signals
Risks include protocol desynchronization on exceptions, stale index cache naming, bandwidth sleep behavior, remote process/socket cleanup, ref/object parsing, and inability to abort remote pack writes. Signals are help negotiation, command availability errors, synced indexes, successful remote pack writes, refs/rev-list equality, resolve errors, and config-get type handling.
<!-- END_FILE_RESEARCH: sources/sync-backup/bup/lib/bup/client.py -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/bup/lib/bup/cmd/__init__.py -->
# sources/sync-backup/bup/lib/bup/cmd/__init__.py

## Purpose
Empty initializer for bup command modules.

## Important APIs, Types, and Functions
No code, exports, or runtime symbols.

## Control Flow
No executable control flow.

## State and Persistence Behavior
No state or persistence.

## Dependencies and Integration Points
Allows modules under `bup.cmd` to be imported by the command dispatcher.

## Risks and Test Signals
Risk is command package import failure if packaging changes. Signal is successful import of command modules such as `bup.cmd.bloom`.
<!-- END_FILE_RESEARCH: sources/sync-backup/bup/lib/bup/cmd/__init__.py -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/bup/lib/bup/cmd/bloom.py -->
# sources/sync-backup/bup/lib/bup/cmd/bloom.py

## Purpose
Command implementation for `bup bloom`, supporting creation/update, validation against idx/midx files, forced regeneration, output/dir selection, hash count selection, and deliberate bloom ruin for tests.

## Important APIs, Types, and Functions
Defines `optspec`, `ruin_bloom`, `check_bloom`, `do_bloom`, and `main`. Uses `BloomReader`, `BloomWriter`, `BloomInvalid`, `BloomNotFound`, `git.open_idx`, `git.open_object_idx`, and `git.repo`.

## Control Flow
`main` parses options, resolves the pack directory and output path, dispatches check/ruin/build. `do_bloom` reads existing bloom when allowed, counts idx files into add/rest sets, decides whether to append or regenerate based on entry count/k/false-positive threshold, adds idx shatables, and renames temp bloom into place.

## State and Persistence Behavior
Reads `.idx`/`.midx` files and writes/updates `bup.bloom` or requested output. `ruin` zeroes the bitfield while preserving file structure.

## Dependencies and Integration Points
Command layer over `bup.bloom` and Git pack indexes. Integrates with repository discovery, progress/logging, saved error status, and object index formats.

## Risks and Test Signals
Risks include stale idx name lists, false-positive threshold decisions, division by zero when add_count is zero avoided by early return, and temporary bloom cleanup. Signals are successful check membership, invalid/missing bloom errors, force regeneration, and correct exit codes.
<!-- END_FILE_RESEARCH: sources/sync-backup/bup/lib/bup/cmd/bloom.py -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/bup/lib/bup/cmd/cat_file.py -->
# sources/sync-backup/bup/lib/bup/cmd/cat_file.py

## Purpose
Implements `bup cat-file`, which prints file contents, encoded metadata, or raw `.bupm` metadata for a bup VFS path.

## Important APIs, Types, and Functions
Defines `optspec` and `main`. Uses `options`, `git.check_repo_or_die`, `LocalRepo`, `vfs.resolve`, `vfs.item_mode`, `vfs.tree_data_and_bupm`, `vfs.tree_data_reader`, `vfs.augment_item_meta`, `vfs.fopen`, and `chunkyreader`.

## Control Flow
Validates exactly one target and incompatible flags, requires `/branch/revision/...` shape, resolves without following symlinks, errors if missing, then branches: `--bupm` requires directory and streams `.bupm`; `--meta` writes encoded augmented metadata; default streams regular file data only.

## State and Persistence Behavior
Read-only repository access; writes selected bytes to stdout.

## Dependencies and Integration Points
Integrates command parsing, Git repo discovery, local repo abstraction, VFS resolution, metadata encoding, and byte-stream stdout.

## Risks and Test Signals
Risks include path validation excluding unusual but valid paths, symlink handling, non-regular file rejection, and missing `.bupm` silently writing nothing. Signals are exact stdout bytes and fatal errors for invalid targets/flag combinations.
<!-- END_FILE_RESEARCH: sources/sync-backup/bup/lib/bup/cmd/cat_file.py -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/bup/lib/bup/cmd/daemon.py -->
# sources/sync-backup/bup/lib/bup/cmd/daemon.py

## Purpose
Implements `bup daemon`, a TCP listener that accepts bup protocol connections and spawns `bup mux -- bup server` for each connection.

## Important APIs, Types, and Functions
Defines `optspec` and `main`. Uses `socket.getaddrinfo`, `SO_REUSEADDR`, `listen`, `select.select`, `os.dup`, `fcntl.FD_CLOEXEC`, `subprocess.Popen`, `path.exe`, and logging helpers.

## Control Flow
Parses listen address and port, creates listen sockets for all address families returned by `getaddrinfo`, sets close-on-exec on listeners, loops with 60-second select, accepts connections, duplicates the socket fd for stdin/stdout of the spawned mux/server process, and closes duplicates in the parent.

## State and Persistence Behavior
Maintains listening sockets and child server processes; no file persistence. Network connections carry repository protocol state handled by the spawned server.

## Dependencies and Integration Points
Integrates with `bup mux`, `bup server`, TCP clients (`Client.ViaBup`), and bup path resolution.

## Risks and Test Signals
Risks include bug-prone error reporting when no sockets are created (`e` remains `None`), fd lifecycle issues, unbounded child process spawning, and shutdown exceptions on already-closed sockets. Signals are successful listen logs, accepted connection logs, client protocol success, and clean socket close.
<!-- END_FILE_RESEARCH: sources/sync-backup/bup/lib/bup/cmd/daemon.py -->
