# Research: subset-b-009100

This grouped report covers the BorgBackup source files assigned to `subset-b-009100`. Each section is source-tree aligned and wrapped for deterministic reconciliation into the mapped per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/borg/scripts/shell_completions/fish/borg.fish -->
# sources/sync-backup/borg/scripts/shell_completions/fish/borg.fish

## Purpose
This Fish shell completion script provides static and dynamic completions for the `borg` command. It enumerates top-level Borg commands, nested command groups such as `key`, `benchmark`, and `help`, common global options, and command-specific options for repository, archive, backup, restore, transfer, tar import/export, and server workflows. It is installed under Fish vendor completions and is user-facing CLI metadata rather than runtime Borg backup logic.

## Important APIs, Types, and Functions
- Fish `complete -c borg ...` declarations are the primary API. They associate subcommands, options, descriptions, argument candidates, file-completion behavior, and `-n` predicates with the `borg` command.
- `__fish_borg_seen_key`, `__fish_borg_seen_benchmark`, and `__fish_borg_seen_help` restrict second-level completions to the relevant command groups and prevent suggesting already-selected nested commands.
- `__fish_borg_archives` shells out to `borg repo-list --format="aid:{id:.8}{TAB}{archive} {start}{NEWLINE}"` to produce archive identifiers plus display metadata.
- `__fish_borg_archive_arg --argument command token_count` checks the tokenized Fish command line and current token to decide whether dynamic archive-name completions should be offered at a specific positional argument slot.
- Local candidate variables such as `sort_keys`, `files_cache_mode`, `compression_methods`, `recompress_when`, and `fuse_options` provide enumerated values for selected options.

## Control Flow
The file is declarative in broad sections: top-level command completions, subgroup predicate functions, common options, per-command option groups, and finally dynamic archive argument completion. Fish evaluates the `-n` predicates lazily while the user types. Most options are gated by `__fish_seen_subcommand_from <command>`, so command-specific options are suggested only after Fish sees the matching command token. At the end, the script erases default filename completions for archive-argument contexts, adds explicit `--no-files` completions for exact token positions, then adds high-priority archive suggestions from `__fish_borg_archives`.

## State and Persistence Behavior
The script itself persists no Borg state. Its dynamic archive completion reads repository state indirectly by invoking `borg repo-list`, which can prompt or fail depending on repository configuration, `BORG_REPO`, and authentication environment such as `BORG_PASSPHRASE`. It redirects errors to `/dev/null`, so completion failures are silent. The static option lists can become stale unless regenerated or manually kept in sync with argparse definitions.

## Dependencies and Integration Points
It depends on Fish built-ins and helper functions (`complete`, `commandline`, `__fish_seen_subcommand_from`, `__fish_is_first_token`, `string`, `test`, `count`) and on a working `borg` executable for archive listing. Its integration target is the CLI built by `src/borg/archiver/__init__.py` and command mixins under `src/borg/archiver/`. Several options mirror helpers in `_common.py`, including archive filters, include/exclude pattern options, common logging/repository flags, and command-specific options from modules such as `check_cmd.py` and `benchmark_cmd.py`.

## Risks and Edge Cases
- Drift risk is high: the script is manually enumerated and can diverge from argparse command definitions, option spelling, defaults, or new subcommands.
- The import-tar exclusion block is gated with `__fish_seen_subcommand_from recreate`, which looks suspicious because the preceding section is for `import-tar`; that likely prevents those completions from appearing for import-tar.
- Dynamic archive completion may be slow for large or remote repositories because it invokes `borg repo-list` during completion.
- Password-protected repositories only list archives when the needed authentication is already available, as noted in the file header.
- `__fish_borg_archive_arg` assumes token 1 is `borg` and token 2 is the command; aliases, wrappers, environment assignments, or `command borg` forms may not match.

## Test Signals
Useful tests include `fish -n borg.fish` syntax validation, interactive completion checks for every top-level command, parity checks against `borg --help`/subcommand help output, and targeted checks that archive-name completions appear only in the intended positional slots. Dynamic completion should be tested with empty, encrypted, local, and remote repositories. The likely import-tar predicate bug deserves a regression test that `borg import-tar --exclude` is suggested while `borg recreate --exclude` remains unaffected.
<!-- END_FILE_RESEARCH: sources/sync-backup/borg/scripts/shell_completions/fish/borg.fish -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/borg/scripts/sign-binaries -->
# sources/sync-backup/borg/scripts/sign-binaries

## Purpose
This release helper signs every `dist/borg-*` artifact with a detached ASCII-armored GPG signature and then normalizes timestamps in `dist/` to a supplied timestamp. It is intended for Borg release/binary distribution workflows, not runtime execution.

## Important APIs, Types, and Functions
- Positional argument `$1` is required and expected in a `touch -t` compatible format, shown as `201912312359`.
- `$QUBES_GPG_DOMAIN` selects the signing command. When unset, it uses `gpg`; when set, it uses `qubes-gpg-client-wrapper`.
- The `for file in dist/borg-*` loop signs each matching artifact with local user `"Thomas Waldmann"`, writing `$file.asc`.
- `touch -t "$D" dist/*` adjusts timestamps on all files in `dist`.

## Control Flow
The script validates that the timestamp argument is present, selects the GPG wrapper, iterates over distribution artifacts, signs each one, then touches the directory contents after signing. There is no `set -e`, so a failed signature command does not automatically abort later signatures or the timestamp rewrite.

## State and Persistence Behavior
It writes persistent `.asc` signature files next to artifacts in `dist/` and mutates file mtimes for everything matching `dist/*`. It relies on the user's local GPG or Qubes GPG configuration and private key availability. It does not create logs, lock files, or rollback state.

## Dependencies and Integration Points
The script depends on Bash, `gpg` or `qubes-gpg-client-wrapper`, `touch`, the `dist/` directory, and release artifacts named `borg-*`. It integrates with packaging outputs produced by setup/build tooling and complements `scripts/upload-pypi`, which uploads a source distribution.

## Risks and Edge Cases
- Missing `set -euo pipefail` means signing failures can be missed.
- If `dist/borg-*` has no matches, Bash's default unmatched glob behavior leaves the literal string, causing an attempted signature of `dist/borg-*`.
- The signing identity is hard-coded; release maintainers using different keys must edit the script or configure GPG accordingly.
- `touch -t "$D" dist/*` mutates all files under `dist`, including signatures and unrelated files.

## Test Signals
Test with a temporary `dist/` containing sample files and a fake `gpg` on `PATH` to assert arguments and `.asc` outputs. Check that a missing timestamp exits nonzero, that `QUBES_GPG_DOMAIN` switches the command, and that invalid timestamps cause an observable failure. Release validation should verify signatures with `gpg --verify`.
<!-- END_FILE_RESEARCH: sources/sync-backup/borg/scripts/sign-binaries -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/borg/scripts/upload-pypi -->
# sources/sync-backup/borg/scripts/upload-pypi

## Purpose
This Bash release helper uploads a Borg source distribution tarball to PyPI or the configured Borg test repository via `twine`. It is a small operational script for maintainers.

## Important APIs, Types, and Functions
- Positional argument `$1` is the release version, used to construct `dist/borgbackup-$R.tar.gz`.
- Optional positional argument `$2` equal to `test` selects `TWINE_REPOSITORY=testborgbackup`; otherwise it selects `TWINE_REPOSITORY=borgbackup`.
- `twine upload $D` performs the upload.

## Control Flow
The script validates the release argument, sets `TWINE_REPOSITORY` based on the optional mode, constructs a single source-distribution path, and invokes Twine. It does not verify that the file exists before calling Twine and does not upload wheels or binary artifacts.

## State and Persistence Behavior
The script mutates only the process environment for `TWINE_REPOSITORY`; persistent effects happen remotely through Twine's package upload and locally through Twine credential/cache behavior. No repository source files are modified.

## Dependencies and Integration Points
It depends on Bash, `twine`, a built `dist/borgbackup-<version>.tar.gz`, and Twine credentials/configuration for the named repository aliases. It integrates with Python packaging generated by `setup.py`/`pyproject.toml` and with release signing scripts.

## Risks and Edge Cases
- No `set -euo pipefail` and no quoting around `$D`; spaces are unlikely in this path but still a shell hygiene gap.
- The repository names are Borg-specific aliases and require matching Twine configuration.
- It uploads only the sdist tarball, so binary wheels or standalone binaries need separate release handling.
- There is no preflight verification of signatures, checksums, version consistency, or existing remote files.

## Test Signals
Use `twine check dist/borgbackup-$R.tar.gz` before upload, dry-run against the test repository, and shell tests with a fake `twine` to validate repository selection and path construction. A release checklist should assert that the target tarball exists and matches the version argument.
<!-- END_FILE_RESEARCH: sources/sync-backup/borg/scripts/upload-pypi -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/borg/setup.py -->
# sources/sync-backup/borg/setup.py

## Purpose
This is BorgBackup's build-time setup entry for extension compilation. Project metadata largely lives in `pyproject.toml`; this file focuses on Cython/C extension discovery, platform-specific extension selection, Cython source generation, long description extraction, and passing build configuration into `setuptools.setup()`.

## Important APIs, Types, and Functions
- Top-level source path constants name Cython modules for compression, crypto, chunkers, hash index, item handling, and platform-specific system calls.
- `cython_sources` lists all `.pyx` files that may need generated C files for source distributions.
- `Sdist` is either the normal setuptools `sdist` command or a guard class that raises if Cython is unavailable when an sdist is requested from a Git checkout lacking generated C files.
- `members_appended(*ds)` merges extension keyword dictionaries by appending list-valued members.
- `lib_ext_kwargs(pc, prefix_env_var, lib_name, lib_pkg_name, pc_version, lib_subdir="lib")` discovers headers/libs from an explicit `BORG_*_PREFIX` environment variable, then from `pkgconfig`, otherwise raises a build error.
- `long_desc_from_readme()` reads `README.rst`, trims content before "What is BorgBackup?", removes badges and unsupported directives, and returns the package long description.
- `setup(cmdclass=..., ext_modules=..., long_description=...)` hands the resulting extension list to setuptools.

## Control Flow
At import time the script attempts to import Cython, records platform flags, builds warning flags, and validates whether generated `.c` files are available if Cython is missing. Unless building on ReadTheDocs, it imports `pkgconfig` when available, discovers OpenSSL/libcrypto, lz4, and platform libraries, constructs extension objects, chooses POSIX/Windows/Linux/BSD/macOS modules by `sys.platform`, and conditionally runs `cythonize` when the command is not `clean`, `egg_info`, help, or version-only. Cythonization first generates C for all platform-specific modules for sdist completeness, then cythonizes extensions for the current platform.

## State and Persistence Behavior
Build execution may generate or update C files from `.pyx` sources and produce compiled extension artifacts in build directories. Environment variables such as `READTHEDOCS`, `BORG_OPENSSL_PREFIX`, `BORG_OPENSSL_NAME`, `BORG_LIBLZ4_PREFIX`, and `BORG_LIBACL_PREFIX` control discovery and whether extensions are built. There is no runtime Borg state, but packaging outputs and generated C files affect reproducibility and installability.

## Dependencies and Integration Points
The file depends on setuptools, optional Cython, optional `pkgconfig`, multiprocessing, compiler toolchains, OpenSSL/libcrypto, liblz4, libacl on Linux, and platform-specific headers. It integrates with `pyproject.toml`, generated Borg Cython modules, ReadTheDocs builds, source distribution generation, and downstream packagers that use `SETUPTOOLS_SCM_PRETEND_VERSION` or library prefix variables.

## Risks and Edge Cases
- Most logic runs at import time, so build failures surface early and can be hard to customize.
- Missing `pkgconfig` is tolerated only until library discovery is needed; users then need explicit prefix variables.
- OpenBSD links a static OpenSSL archive from a versioned path/name, which can break when ports update naming.
- The condition deciding when to cythonize is based on `sys.argv[1]`; unusual chained build commands can skip or trigger Cython unexpectedly.
- Long description extraction asserts a specific README heading and can fail if README structure changes.

## Test Signals
Important coverage includes source builds with and without Cython, sdist generation, installs from sdist without Cython, platform matrix builds for Linux/macOS/Windows/BSD/OpenBSD, and prefix-variable discovery for OpenSSL/lz4/acl. Packaging CI should validate `python -m build`, `pip install .`, import of all compiled modules, and ReadTheDocs mode.
<!-- END_FILE_RESEARCH: sources/sync-backup/borg/setup.py -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/borg/src/borg/__init__.py -->
# sources/sync-backup/borg/src/borg/__init__.py

## Purpose
This package initializer exposes Borg's version and validates that dynamically generated version metadata is sane. It is imported by runtime CLI code, packaging/build helpers, and callers that need `borg.__version__`.

## Important APIs, Types, and Functions
- Imports `parse` from `packaging.version` and `version` from `._version`.
- Exports `__version__` as the dynamic Borg version string.
- Computes `__version_tuple__` from the parsed release tuple.
- A top-level assertion rejects `0.1.dev...` fallback versions and non-integer release components.

## Control Flow
Importing `borg` immediately imports `_version`, parses the version, and asserts that the result is not the setuptools-scm fallback and has integer semantic-release components. If the assertion fails, import aborts with a detailed message for broken repackaging or missing Git tags/version override.

## State and Persistence Behavior
The module has no persistence and no mutable runtime state beyond module globals. It depends on installation-time/generated `_version.py` content, usually produced by setuptools-scm. Import failure affects all Borg CLI and library entry points.

## Dependencies and Integration Points
It integrates with setuptools-scm version generation, `setup.py`, CLI version display in `archiver/__init__.py`, and package metadata. The assertion message explicitly points maintainers toward correct tags or `SETUPTOOLS_SCM_PRETEND_VERSION`.

## Risks and Edge Cases
- Assertion-based validation can be disabled by optimized Python (`-O`), but Borg's archiver separately refuses to run with assertions disabled.
- Non-standard version schemes may fail if release components are not integers.
- Any missing or malformed `_version.py` makes the whole package unimportable.

## Test Signals
Tests should import `borg`, check `__version__` and `__version_tuple__`, verify `borg --version`, and exercise packaging from Git and sdist contexts. A packaging regression test should cover `SETUPTOOLS_SCM_PRETEND_VERSION` and absence of Git metadata.
<!-- END_FILE_RESEARCH: sources/sync-backup/borg/src/borg/__init__.py -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/borg/src/borg/__main__.py -->
# sources/sync-backup/borg/src/borg/__main__.py

## Purpose
This module is the `python -m borg` entry point. It performs a Windows-specific DLL search path workaround, imports the top-level CLI `main`, and executes it.

## Important APIs, Types, and Functions
- Uses `sys.platform.startswith("win32")` to detect Windows.
- Builds a PATH prefix from `sys.path` entries containing a `DLLs` component.
- Imports `main` via absolute `from borg.archiver import main`, which is explicitly needed for PyInstaller binaries.
- Calls `main()` unconditionally at module import/execution time.

## Control Flow
On Windows, the module prepends discovered DLL directories to `os.environ["PATH"]` so bundled `libcrypto` can be loaded. On all platforms, it imports and calls `borg.archiver.main()`, transferring control to argument parsing, logging setup, signal handling, and command dispatch.

## State and Persistence Behavior
The module mutates only the current process environment by changing `PATH` on Windows. It persists no Borg repository/cache state. Because it calls `main()` at top level, importing `borg.__main__` for introspection can execute the CLI.

## Dependencies and Integration Points
It depends on `sys`, `os`, and `borg.archiver.main`. It integrates with Python's `-m` entry point mechanism, PyInstaller packaging, and Windows Python DLL layout.

## Risks and Edge Cases
- PATH mutation prepends all `sys.path` entries with a `DLLs` component, which can change DLL resolution order.
- If no DLL paths are found on Windows, it still prepends an empty string plus path separator, which may have subtle PATH semantics.
- Top-level execution makes import-time side effects expected but important.

## Test Signals
Test `python -m borg --version` on supported platforms, especially Windows bundled builds. A unit-level smoke test can monkeypatch `sys.platform`/`sys.path` and assert PATH construction. PyInstaller tests should verify the absolute import works.
<!-- END_FILE_RESEARCH: sources/sync-backup/borg/src/borg/__main__.py -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/borg/src/borg/_item.c -->
# sources/sync-backup/borg/src/borg/_item.c

## Purpose
This C helper provides low-level pointer wrapping/unwrapping for Python objects. It converts a `PyObject *` pointer address into a small `bytes` object and later turns that byte representation back into the original object pointer without serializing or copying the object.

## Important APIs, Types, and Functions
- Includes `Python.h` and uses the CPython C API.
- `_object_to_optr(PyObject *obj)` increments the object's refcount and returns a bytes object containing the address of the local pointer variable's value, sized as `sizeof(void*)`.
- `_optr_to_object(PyObject *bytes)` validates that the input is bytes of pointer-size length, then reads the `PyObject *` value from the bytes payload and returns it.

## Control Flow
Wrapping calls `Py_INCREF(obj)` to keep the object alive, then creates a `PyBytes` payload from the pointer value. Unwrapping validates type and size, raises `TypeError` on invalid inputs, extracts the pointer value with `PyBytes_AsString`, and returns the object pointer. The comments describe the contract that wrap/unwrap calls must be symmetric because the reference increment is conceptually transferred and not decref'd in the unwrap helper.

## State and Persistence Behavior
There is no external persistence, but reference counts are persistent process state. Incorrect pairing of wrap and unwrap can leak references; unwrapping invalid or stale byte payloads can return arbitrary pointers and crash or corrupt process state. The representation is intentionally process-local and cannot survive serialization across processes or interpreter lifetimes.

## Dependencies and Integration Points
This file depends on CPython internals and is likely included or used by the Borg item Cython extension built from `src/borg/item.pyx`/`setup.py`. It integrates with Python object identity/pointer passing where Cython or C code needs to pass object references without msgpack serialization.

## Risks and Edge Cases
- Pointer bytes are not safe across processes, Python interpreters, architectures, or after object lifetime violations.
- The API accepts any bytes object of pointer size, so callers must ensure the payload came from `_object_to_optr`.
- Reference lifecycle correctness relies on strict symmetry; missing unwraps leak references, and duplicate unwrap semantics could be unsafe depending on the surrounding generated code.
- This is CPython-specific and not portable to Python implementations with different object models.

## Test Signals
Tests should cover wrapping/unwrapping live Python objects, invalid type input, invalid byte length input, and reference count behavior under debug builds or leak checks. Fuzzing should avoid arbitrary pointer dereference; validation should focus on caller constraints and generated Cython integration.
<!-- END_FILE_RESEARCH: sources/sync-backup/borg/src/borg/_item.c -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/borg/src/borg/archive.py -->
# sources/sync-backup/borg/src/borg/archive.py

## Purpose
`archive.py` is Borg's central archive model and archive data-plane implementation. It handles archive metadata, item-stream chunking, statistics, extraction, filesystem and tar object processing, chunk reuse, repository consistency checking and repair, and archive recreation. It bridges high-level CLI commands with repository objects, manifests, caches, cryptographic keys, chunkers, item metadata, platform metadata, and filesystem I/O.

## Important APIs, Types, and Functions
- `Statistics` tracks original size, deduplicated/unique size, file counts, status counts, chunking/hashing time, and remote byte counters, with text/JSON progress output.
- `BackupIO`, `backup_io_iter`, `OsOpen`, and `stat_update_check` wrap filesystem I/O errors into Borg backup exceptions and guard against file-type/inode race conditions between stat and open/fstat.
- `DownloadPipeline` fetches repository objects, parses them with `RepoObj`, replaces missing file chunks with zero bytes when requested, and unpacks item metadata streams.
- `ChunkBuffer` and `CacheChunkBuffer` pack `Item` dictionaries into msgpack streams, content-chunk the metadata stream, and write archive stream chunks through the cache.
- `archive_get_items` and `archive_put_items` abstract legacy v1 `items` lists versus v2+ `item_ptrs` indirection chunks.
- `Archive` loads, creates, saves, extracts, renames, deletes, and compares archives. It owns archive metadata, item iteration, `ArchiveItem` packing, manifest archive directory updates, and extraction attribute restoration.
- `MetadataCollector` reads mode, timestamps, ownership, names, inode, birthtime, BSD flags, xattrs, and ACLs according to backup options.
- `ChunksProcessor`, `cached_hash`, and `zero_chunk_ids` hash chunks, optimize all-zero chunk hashing, write chunks to the cache, and update file item chunk lists.
- `FilesystemObjectProcessors` builds `Item` records from live filesystem objects, handles hardlink tracking, special file treatment, files-cache reuse, chunkification, race detection for files changed while reading, and status accounting.
- `TarfileObjectProcessors` imports tar members into Borg items, including Borg-specific pax metadata, SCHILY xattrs/ACLs, hardlink chunk reuse, and file content chunking.
- `RobustUnpacker` and `valid_msgpacked_dict` support resynchronization while reading damaged item metadata streams during archive checks.
- `ArchiveChecker` performs archive consistency checks, optional cryptographic data verification, missing/corrupt manifest recovery, lost archive directory reconstruction, archive item stream validation, and repair writes.
- `ArchiveRecreater` recreates archives with filters, optional rechunking/recompression coordination, exclude-tag handling, metadata preservation, and original archive deletion.

## Control Flow
Archive creation starts with an `Archive(..., create=True)` and a `CacheChunkBuffer`. Filesystem or tar processors create `Item` objects, collect metadata, chunk file data, update stats, and call `Archive.add_item()`. `Archive.save()` flushes the item stream, writes `item_ptrs`, packs archive metadata as an `ArchiveItem`, adds the archive metadata chunk, waits for async repository responses, creates a manifest archive entry, and writes the manifest.

Archive reading loads metadata by archive name or id through the manifest, fetches the archive metadata object, parses/decrypts it, resolves item stream chunk ids, and iterates items via `DownloadPipeline.unpack_many()`. Extraction dispatches by item mode: regular files stream chunks to stdout/dry-run or to disk, directories are created/preserved, symlinks/fifos/devices are recreated, hardlinks are coordinated by `HardLinkManager`, and attributes are restored late to preserve ownership, xattrs/ACLs, timestamps, and flags.

Filesystem backup processing is race-aware. It stats by name, opens by directory fd/name where possible, fstats, checks type and inode stability, collects simple and extended metadata, excludes tagged items by xattr/flag, reuses files-cache chunks when valid, chunks changed content, checks whether ctime/mtime changed while reading, and memorizes unchanged files only when safe. Tar import follows a similar item creation path but derives metadata from `tarinfo` and pax headers rather than live filesystem calls.

Archive checking first builds a repository chunk index, obtains a key from the manifest or sampled chunks, optionally verifies all encrypted objects by parsing/decompressing them, loads or rebuilds the manifest, optionally scans all objects for lost archive metadata, and then validates selected archives. During archive validation it detects missing metadata/file chunks, validates msgpack item dictionaries against required/known keys, can resynchronize damaged streams, and in repair mode rewrites item pointer streams/archive metadata and manifest entries. `finish()` writes repaired manifest state and invalidates chunk-index caches.

Archive recreation opens a source archive, creates a target temporary/archive object, optionally adds tagged-directory excludes, filters items, reuses chunks or rechunkifies content, saves target metadata with original command/timestamp metadata as appropriate, and deletes the original archive when configured.

## State and Persistence Behavior
This module performs substantial persistent mutation: repository object writes via cache/repo objects, manifest writes, archive directory creates/deletes, chunk-index cache deletion, filesystem extraction writes, metadata restoration, and optional repository object deletion during repair. It also maintains in-memory state including archive stats, item buffers, hardlink maps, seen chunks, `zero_chunk_ids` LRU cache, progress state, and check error flags. Dry-run paths avoid writes for extraction/recreation/check repair, but many normal operations mutate repository or filesystem state.

## Dependencies and Integration Points
It depends on Borg subsystems for chunking, cache, crypto keys, constants, helpers, hash index, manifest, patterns, item types, platform ACL/xattr/flags, repository, and repo object formatting. It integrates with command mixins such as create/extract/list/info/diff/check/recreate/tar/import/export, with `_common.with_repository` for repository/cache lifecycle, and with shell/user output via loggers and progress indicators. Platform integration is extensive: POSIX ownership/mode/timestamps, Windows timestamp behavior, macOS dataless/nodump flags, BSD birthtime/flags, Linux xattrs/capabilities, and hardlink support.

## Risks and Edge Cases
- Race handling is security-critical. Any gap around `stat_update_check`, symlink handling, or fd-based access can lead to backing up the wrong object from a live filesystem.
- `ArchiveChecker --repair` is intentionally lossy in some corruption cases; it may delete corrupt chunks or remove broken archive entries.
- Missing chunks may be replaced with zeros during extraction/fetch paths, which preserves stream length but can hide data loss unless surfaced by logs/checks.
- Attribute restoration order is delicate; ownership can remove Linux capabilities, immutable flags must be set late, and platform support for symlink timestamps/permissions varies.
- Files-cache reuse depends on accurate metadata; incorrect changed-while-reading detection could archive inconsistent file content.
- `Archive.delete()` only removes manifest/archive-directory references and can orphan chunks until compaction.
- Robust msgpack resynchronization is heuristic and must balance recovery with avoiding false item interpretation.

## Test Signals
High-value tests include archive create/extract/list/info round trips, hardlink/symlink/fifo/device handling, ACL/xattr/bsdflags restoration, sparse extraction, files-cache reuse and invalidation, changed-while-reading retries, tar import/export with pax metadata, missing chunk behavior, archive compare output, recreate filtering/rechunking, and check/repair flows on deliberately damaged repositories. Platform CI is important because much behavior is OS-specific. Repository mutation tests should verify manifest/archive directory updates, chunk reference behavior, and cache invalidation after repair.
<!-- END_FILE_RESEARCH: sources/sync-backup/borg/src/borg/archive.py -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/borg/src/borg/archiver/__init__.py -->
# sources/sync-backup/borg/src/borg/archiver/__init__.py

## Purpose
This module is Borg's top-level CLI orchestrator. It composes command mixins into the `Archiver` class, builds the argument parser hierarchy, parses and normalizes command-line arguments, sets up logging/profiling/signal handling, dispatches commands, handles user-facing exceptions, and provides the `main()` entry point used by console scripts and `borg.__main__`.

## Important APIs, Types, and Functions
- Top-level assertion guard refuses Python optimized mode by requiring working `assert` statements.
- `Archiver` inherits all command mixins, including analyze, benchmark, check, create, extract, repo operations, tar operations, transfer, and version.
- `Archiver.print_warning`, `print_warning_instance`, and `print_file_status` centralize warning/exit-code registration and list/json file-status output.
- `Archiver.CommonOptions` registers common options at multiple parser hierarchy levels with top-level defaults and subparser `SUPPRESS` semantics.
- `build_parser()` constructs the root parser, common parsers, optional `borgfs` parser, and all subcommand parsers by calling each mixin's `build_parser_*`.
- `get_args()` handles normal parsing and SSH forced-command `borg serve` reconciliation, allowing only a small allowlist of client-supplied options to override forced command attributes.
- `parse_args()` preprocesses args, flattens nested namespaces, validates cross-option constraints, applies timestamp-based placeholder overrides, and resolves the function to dispatch.
- `run()` sets umask, logging, progress defaults, selftests, msgpack compatibility checks, optional profiling, and invokes the selected command.
- `sig_info_handler`, `sig_trace_handler`, `format_tb`, and `main()` implement runtime diagnostics and final exception-to-exit-code handling.

## Control Flow
At import time the module imports dependencies in a protective `try` block so import-time crashes exit as Borg errors rather than Python warning rc mismatches. Runtime starts in `main()`, which wraps stdout/stderr for replacement encoding errors, installs signal/fault handlers, constructs `Archiver`, parses args including `SSH_ORIGINAL_COMMAND`, optionally runs the Cockpit TUI, otherwise calls `archiver.run(args)` under the SIGINT helper. `run()` configures logging only after determining whether the command is `serve`, applies implied loggers for options such as `--stats` and `--progress`, warns about unsupported option combinations, runs selftests, checks msgpack implementation, optionally profiles, and dispatches. Exceptions are normalized into Borg exit codes and optionally formatted tracebacks/sysinfo.

## State and Persistence Behavior
This module mutates process-level state: `umask`, stdout/stderr wrappers, logging levels/handlers, signal handlers, debug logger levels, optional profile output files, and process exit code. It does not directly mutate repositories except through dispatched command mixins. It may run selftests and can launch the Cockpit TUI. `get_args()` mutates parsed namespaces for forced-command serve scenarios.

## Dependencies and Integration Points
It integrates with every `archiver/*_cmd.py` mixin, `_common` parser/decorator helpers, Borg helpers/constants/logging, selftests, legacy remote error formatting, platform flags, and optional Cockpit UI. It is the endpoint called by `src/borg/__main__.py` and console entry points. The parser output supplies attributes consumed by `_common.with_repository` and command methods.

## Risks and Edge Cases
- Parser/common-option precedence is subtle; `flatten_namespace()` and `CommonOptions` must preserve the intended "most specific wins" behavior.
- Forced-command `borg serve` security depends on a strict denylist/allowlist and correct parsing of `SSH_ORIGINAL_COMMAND`.
- The top-level import block exits the interpreter on import errors, which is appropriate for CLI but makes library-style import behavior less flexible.
- Signal handlers inspect stack frames and local variable names, so refactors of create/extract internals can break SIGUSR1/SIGINFO diagnostics.
- Profiling writes potentially sensitive execution data to user-specified files.
- `assert rc is None` in `run()` assumes command methods communicate exit status through Borg's global exit-code helpers.

## Test Signals
Tests should cover parser construction for all commands, common-option placement before/after subcommands, placeholder replacement under `--timestamp`, forced `borg serve` allowlist behavior, Cockpit import failure path, logging level implications, unsupported msgpack/pure-Python msgpack warnings, profiling output formats, and exception-to-exit-code mapping. CLI smoke tests should include `borg -h`, `borg help`, `borg --version`, invalid args, and signal behavior where practical.
<!-- END_FILE_RESEARCH: sources/sync-backup/borg/src/borg/archiver/__init__.py -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/borg/src/borg/archiver/_common.py -->
# sources/sync-backup/borg/src/borg/archiver/_common.py

## Purpose
`_common.py` contains shared archiver infrastructure: repository-opening decorators, archive-loading wrappers, parser help processing, common option registration, include/exclude pattern options, archive filter options, and matcher/filter construction. It is the main integration layer between command methods and repository/manifest/cache lifecycles.

## Important APIs, Types, and Functions
- `get_repository(location, create, exclusive, lock_wait, lock, args, v1_legacy)` selects `Repository`, legacy repository, legacy remote repository, or direct BorgStore-backed protocols based on location protocol and Borg 1 compatibility.
- `compat_check(...)` validates decorator arguments and derives manifest compatibility checks for create operations.
- `with_repository(...)` decorates command methods, opens the primary repository, checks repository version, loads manifest/repo object adapter, optionally asserts security, opens cache, and passes `repository`, `manifest`, and/or `cache`.
- `with_other_repository(...)` mirrors that behavior for `--other-repo` source repositories used by transfer-like commands.
- `with_archive(method)` resolves `args.name` to an archive id and injects an `Archive` instance configured from CLI flags.
- `process_epilog(epilog)` dedents RST help, removes man-only lines for command-line/build usage, and converts references for terminal display.
- `define_exclude_and_patterns`, `define_exclusion_group`, and `define_archive_filters_group` register shared argparse options for path patterns and archive selection.
- `define_common_options(add_common_option)` registers global options such as logging, progress, lock wait, repository location, remote path, upload throttling, profiling, and shell command.
- `build_matcher` and `build_filter` create pattern matchers and item filters for include/exclude and strip-components behavior.

## Control Flow
Decorator factories validate compatibility arguments at definition time and return wrappers. At command invocation, `with_repository` validates that a repository location is present, computes lock behavior, opens the repository context, checks supported repository version, loads a `Manifest` with `RepoObj` or legacy `RepoObj1` when needed, applies compression overrides, asserts secure cache/repository state, optionally opens `Cache`, and then calls the command. `with_other_repository` follows the same flow for secondary source repositories but returns without opening one when the other location is absent. Parser helper functions are invoked during `Archiver.build_parser()` and produce consistent option groups across commands.

## State and Persistence Behavior
The wrappers acquire repository locks, open/close repository and cache contexts, may create repositories when requested, and may initialize or validate local cache state. They do not themselves write archive content, but create/exclusive/cache options determine whether downstream commands can mutate repository state. Parser helpers create argparse state only. Matchers are in-memory structures derived from CLI patterns and paths.

## Dependencies and Integration Points
The module depends on `borg` package doc-mode metadata, `Archive`, constants, `Cache`, `assert_secure`, helper validators/types (`Location`, `SortBySpec`, `Highlander`, `PositiveInt`, etc.), RST terminal conversion, `Manifest`, `PatternMatcher`, repository classes, repo object adapters, and argparse pattern actions. It is imported by command mixins throughout `src/borg/archiver/` and by the top-level `Archiver`.

## Risks and Edge Cases
- Repository protocol/version selection is security-sensitive, especially legacy `ssh://` support and direct BorgStore protocols.
- Compatibility checks are enforced by decorator configuration; a command using the wrong compatibility tuple can allow unsupported manifest feature access.
- `with_archive` assumes `args.name` exists and resolves exactly one archive through the manifest.
- Common option defaults depend on being registered once with defaults and again under subparsers with `SUPPRESS`; mistakes can change precedence.
- `build_filter` strip-components matching compares `os.sep`-split path components; archive paths are generally POSIX-like, so platform path separator assumptions should be considered.

## Test Signals
Tests should exercise decorated commands with file/rest/sftp/cloud protocols, legacy Borg 1 allowed/disallowed paths, missing repository location, repository version mismatch, manifest compatibility errors, cache opening modes, secure cache assertions, other-repository handling, and archive resolution. Parser tests should validate common option precedence, archive filter mutual exclusions, pattern-file actions, strip-components filters, and terminal/RST help rendering.
<!-- END_FILE_RESEARCH: sources/sync-backup/borg/src/borg/archiver/_common.py -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/borg/src/borg/archiver/analyze_cmd.py -->
# sources/sync-backup/borg/src/borg/archiver/analyze_cmd.py

## Purpose
This command module implements `borg analyze`, which compares consecutive selected archives and reports directory paths with the largest amount of chunk churn. It helps users find hot spots such as caches, temporary directories, or high-change data that may need exclusion or recreation.

## Important APIs, Types, and Functions
- `ArchiveAnalyzer.__init__(args, repository, manifest)` stores the repository, manifest, args, and a `defaultdict(int)` mapping directory path to cumulative changed chunk size.
- `analyze()` logs start/end, runs archive analysis, and prints the report.
- `analyze_archives()` obtains selected archives through `manifest.archives.list_considering(args)`, requires at least two, iterates archives in order, and compares adjacent archive chunk maps.
- `analyze_archive(id)` opens an `Archive`, iterates items, and builds `directory_path -> {chunk_id: plaintext_size}` for file items.
- `analyze_change(base, new)` adds sizes for chunk ids added or removed per directory.
- `report()` prints a sorted descending text report.
- `AnalyzeMixIn.do_analyze` is decorated with `with_repository(compatibility=(Manifest.Operation.READ,))`.
- `build_parser_analyze()` registers the `analyze` subcommand and shared archive filters.

## Control Flow
The command opens a read-compatible repository and manifest through `_common.with_repository`. It selects archives with standard archive filter arguments, analyzes the first as the base, then for each subsequent archive builds a new per-directory chunk map and compares it with the previous one. The comparison is adjacent-pair based, so churn accumulates across the selected time series.

## State and Persistence Behavior
`borg analyze` is read-only. It reads archive metadata and item streams, but it does not write repository, manifest, cache, or filesystem state. Its only persistent-like output is terminal output; in-memory state is `difference_by_path` and per-archive chunk maps.

## Dependencies and Integration Points
It depends on `_common.with_repository`, `_common.define_archive_filters_group`, `Archive`, `Manifest`, `Repository`, `ProgressIndicatorPercent`, and helper formatting/logging. It integrates with the archive item model (`item.chunks` as chunk id/size entries) and the same archive selection options used by list/check/info-like commands.

## Risks and Edge Cases
- It uses plaintext chunk sizes, not compressed repository object sizes, so results approximate logical churn rather than storage impact.
- It groups by direct parent directory only, not recursive subtree aggregation.
- The nested `analyze_path_change` uses the outer `directory_path` variable rather than its `path` parameter; because calls pass the same variable name, behavior is currently correct but fragile under refactoring.
- Large archive series can require significant metadata reads and memory for per-directory chunk maps.
- Chunks reused across files/directories are represented in per-directory dicts, so duplicate chunks within the same directory collapse by id.

## Test Signals
Tests should create multiple archives with controlled file additions/removals/modifications and verify reported directory churn ordering and sizes. Edge coverage should include fewer than two archives, archive filters selecting no/one archive, repeated chunks, files in repository root, and large archives to watch performance/progress behavior.
<!-- END_FILE_RESEARCH: sources/sync-backup/borg/src/borg/archiver/analyze_cmd.py -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/borg/src/borg/archiver/benchmark_cmd.py -->
# sources/sync-backup/borg/src/borg/archiver/benchmark_cmd.py

## Purpose
This module implements Borg's `benchmark` command group. `benchmark crud` measures end-to-end create, extract, update, and delete throughput against a repository using generated test files. `benchmark cpu` measures CPU-bound chunking, hashing/MAC, encryption, compression, and msgpack performance using in-memory data.

## Important APIs, Types, and Functions
- `BenchmarkMixIn.do_benchmark_crud(args)` orchestrates CRUD measurement.
- Nested `parse_args(args, cmd)` reparses internal Borg command invocations while propagating `--rsh` and `--remote-path`.
- Nested `measurement_run(repo, path)` invokes `do_create`, `do_delete`, and `do_extract` directly, times phases with `time.monotonic()`, and asserts zero Borg exit codes via `get_reset_ec`.
- Nested `test_files(path, count, size, random)` creates temporary benchmark input files using `SyncFile`, all-zero buffers, or `os.urandom`.
- `do_benchmark_cpu(args)` uses `timeit` across chunker specs, crypto hash/MAC functions, encryption modes, compression specs, and msgpack packing.
- `build_parser_benchmarks()` registers `benchmark`, nested `crud`, nested `cpu`, `PATH`, `--json-lines`, and `--json`.

## Control Flow
For CRUD benchmarks, the command selects a test matrix. Normal mode uses six datasets ranging from ten 100 MB files to ten thousand 10 KB files, each with zero and random variants; `_BORG_BENCHMARK_CRUD_TEST` selects tiny CI-friendly cases. For each dataset, it creates temporary input under `args.path`, measures first archive creation with disabled files cache, creates/deletes a second archive to populate cache, measures no-change update, measures dry-run extraction, and measures deletion of the last remaining benchmark archive. Output is plain text throughput or JSON Lines.

For CPU benchmarks, the command selects iteration counts and data size based on `_BORG_BENCHMARK_CPU_TEST`, creates random buffers and keys, times chunkers, hash/MAC functions, authenticated encryption algorithms, compression algorithms/levels, and msgpack packing, then prints human-readable timings or a structured JSON object.

## State and Persistence Behavior
CRUD benchmarking writes temporary input files under the supplied path and creates/deletes archives named `borg-benchmark-crud*` in the supplied repository. It intentionally mutates repository contents and cache state; it suppresses some delete warnings because the repository is expected to be temporary or disposable. CPU benchmarking is in-memory except for normal process memory pressure and imports. Both commands reset Borg global exit-code state after internal command calls.

## Dependencies and Integration Points
The CRUD path integrates tightly with other Archiver methods (`do_create`, `do_delete`, `do_extract`) and relies on normal repository/cache/manifest command decorators. It depends on `SyncFile`, tempfile, logging, constants, and helper format/JSON functions. CPU benchmarking depends on Borg chunkers, crypto low-level extension classes/functions, `blake3`, compression specs, `Item`, and msgpack.

## Risks and Edge Cases
- `benchmark crud` can consume substantial disk space and repository bandwidth; normal datasets need roughly gigabyte-scale input per case plus repository overhead.
- It assumes benchmark archive names are safe to create/delete; running against a valuable existing repository risks name collisions or unwanted churn.
- Direct internal command invocation means parser/command side effects such as global exit-code state and logging must be handled carefully.
- Assertions enforce success; under Python optimized mode assertions would be disabled, but Borg refuses optimized mode in the top-level archiver.
- CPU timings can be noisy and depend heavily on CPU frequency scaling, memory pressure, native extensions, and optional blake3 threading.

## Test Signals
CI should use `_BORG_BENCHMARK_CRUD_TEST` and `_BORG_BENCHMARK_CPU_TEST` to keep runtime bounded. Tests should validate JSON/JSON Lines schema, internal command propagation of `--rsh`/`--remote-path`, no leftover temporary input directories, expected creation/deletion of benchmark archives, and successful CPU benchmark imports. Manual performance runs should be done on idle systems with disposable repositories.
<!-- END_FILE_RESEARCH: sources/sync-backup/borg/src/borg/archiver/benchmark_cmd.py -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/borg/src/borg/archiver/check_cmd.py -->
# sources/sync-backup/borg/src/borg/archiver/check_cmd.py

## Purpose
This module implements `borg check`, the command that verifies repository-level consistency and archive-level metadata/data consistency. It wires CLI validation, repair confirmation, repository checks, archive checks, and parser help/options around the `Repository.check()` and `ArchiveChecker` implementations.

## Important APIs, Types, and Functions
- `CheckMixIn.do_check(args, repository)` is decorated with `with_repository(exclusive=True, manifest=False)`, so it opens the repository exclusively but defers manifest/key handling to check logic.
- `yes(...)` confirmation with `BORG_CHECK_I_KNOW_WHAT_I_AM_DOING` environment override gates `--repair`.
- Cross-option validation rejects contradictions: `--repository-only` with archive filters or `--verify-data`, `--repository-only` with `--find-lost-archives`, `--repair` with `--max-duration`, and `--max-duration` without `--repository-only`.
- It pre-fetches the archive key from the manifest when archive checks will run, so passphrase prompting happens before lengthy repository checks.
- `repository.check(repair=args.repair, max_duration=args.max_duration)` performs low-level repository verification.
- `ArchiveChecker.check(...)` performs archive metadata/chunk verification, optional data verification, repair, lost archive recovery, and archive filter handling.
- `build_parser_check()` registers check options and shared archive filters with a detailed epilog.

## Control Flow
The command opens the repository with an exclusive lock. If repair is requested, it prompts for an exact `YES` unless overridden by environment. It validates incompatible option combinations. If archive checks are needed, it instantiates `ArchiveChecker` and attempts `make_key(..., manifest_only=True)` early. It runs repository checks unless `--archives-only` is set; failures set Borg's warning exit code. It then runs archive checks unless `--repository-only` is set; archive-check failure also sets the warning exit code.

## State and Persistence Behavior
Without `--repair`, the command is intended to be read-only, though repository partial-check bookkeeping may be internal to `Repository.check()`. With `--repair`, it can delete corrupt repository objects, rebuild or write manifests, recreate lost archive-directory entries, remove broken archive entries, and delete chunk-index caches through `ArchiveChecker`. `--max-duration` enables partial repository checks only and cannot be combined with archive checks or repair.

## Dependencies and Integration Points
It depends on `_common.with_repository`, `_common.Highlander`, `ArchiveChecker`, constants, helper exit-code and prompt classes/functions, and shared archive filter parser helpers. It delegates most deep behavior to `Repository.check()` and `archive.py`'s `ArchiveChecker`. The parser's archive filter options must stay aligned with `ArchiveChecker.check()` parameters.

## Risks and Edge Cases
- `--repair` is explicitly dangerous and can cause data loss when corruption is not fully recoverable.
- Partial checks are non-cryptographic repository checks only; users may overestimate their coverage.
- Early key prompting improves UX but falls back silently if manifest-only key creation fails; archive checking later tries again.
- The command uses warning exit codes for detected issues, so automation must interpret Borg's modern/legacy exit code semantics correctly.
- Archive filters with check can leave unselected archives unchecked; this is useful but can surprise users expecting full repository validation.

## Test Signals
Tests should cover option contradiction errors, repair confirmation and environment override, repository-only/archive-only branching, partial check requirements, archive filter forwarding, warning exit-code setting, and passphrase/key-prompt ordering. Integration tests should use repositories with missing chunks, corrupt archive metadata, corrupt data objects, missing manifests, and lost archive entries, with and without repair.
<!-- END_FILE_RESEARCH: sources/sync-backup/borg/src/borg/archiver/check_cmd.py -->
