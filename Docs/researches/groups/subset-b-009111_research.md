# Research Report: subset-b-009111

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/bup/lib/bup/repo/remote.py -->
## sources/sync-backup/bup/lib/bup/repo/remote.py

Purpose: implements `RemoteRepo`, the `RepoProtocol` adapter for repositories reached through `bup.client.Client`. It gives higher-level code the same read/write/ref surface as a local repo while routing object and ref operations over the remote client protocol.

Important APIs and control flow: construction validates the location through `Client`, exposes client methods (`rev_list`, `refs`, `resolve`, `join`, etc.), and builds shared write configuration via `_make_base`. Writes are lazy: `_ensure_packwriter()` opens a remote packwriter only when an object write is requested; `finish_writing()` closes and uploads that writer before ref updates. `cat()` wraps `client.cat_batch()` and, when the requested ref is a 40-hex oid, streams data through a SHA-1 check before allowing the batch call to finish.

State, dependencies, and integration: persistent state lives remotely in packs and refs; local state is the open client and optional `_packwriter`. It depends on `bup.client`, `bup.git`, and `bup.repo.base`. `update_ref()` flushes pending writes first, which is critical for remote visibility. Risks include protocol deadlock if a caller starts another remote operation before consuming a `cat()` iterator, and abort handling leaving `_packwriter` set after `abort_writing()`. Test signals come indirectly from remote save/get/gc/init scenarios such as `test-gc`, `test-init`, and import/save tests that use `-r -:repo`.
<!-- END_FILE_RESEARCH: sources/sync-backup/bup/lib/bup/repo/remote.py -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/bup/lib/bup/rewrite.py -->
## sources/sync-backup/bup/lib/bup/rewrite.py

Purpose: rebuilds saves from one repository into another, optionally rewriting split layout, applying excludes, and repairing missing objects/metadata. It is the core engine behind `bup get --rewrite` and `--repair`.

Important APIs and control flow: `Rewriter(split_cfg, db)` manages a SQLite mapping table keyed by split settings. `append_save()` resolves `latest`, walks a VFS save in DFS postorder via `_vfs_walk_dir_recursively()`, feeds entries to `_rewrite_save_item()`, then writes a new commit with repair trailers. `_previous_conversion()` reuses prior conversions when the destination still has the mapped oid. `_rewrite_link()` handles symlink metadata/blob restoration, mismatch detection, and repair. Replacement helpers create explanatory blobs for missing files, trees, and symlinks.

State, dependencies, and persistence: durable memoization lives in a SQLite database, either caller-supplied or temporary under XDG cache. Destination persistence is through repo writes and final commit refs outside this module. It depends heavily on `bup.vfs`, `bup.tree.Stack`, `bup.metadata`, `bup.hashsplit`, `bup.repair`, and `commit_message()`. Excludes invalidate remembered directory-tree conversions but not file conversions.

Risks and edge cases: correctness depends on VFS ordering, immutable metadata discipline, split configuration identity, and not reusing destructive repair blobs whose content includes contextual repair IDs. Non-repair rewrites raise on missing objects; destructive repairs replace whole files/trees rather than attempting partial reconstruction. Test signals are strong in `test-get-excludes`, `test-get-repair-bupm`, `test-get-repair-symlinks`, and `test-get-rewrite-missing`, covering contextual excludes, missing bupm metadata, symlink blob repair, missing split trees, repair IDs, and trailer accumulation.
<!-- END_FILE_RESEARCH: sources/sync-backup/bup/lib/bup/rewrite.py -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/bup/lib/bup/rm.py -->
## sources/sync-backup/bup/lib/bup/rm.py

Purpose: removes backup branches or individual saves by rewriting branch history and updating Git refs atomically at the end of the operation.

Important APIs and control flow: `dead_items(repo, paths)` resolves VFS paths and classifies requests into whole branches (`RevList`) and saves (`Commit`), rejecting `latest`, ordinary files, inaccessible paths, and mixed invalid inputs. `rm_saves()` computes commits to drop and calls `filter_branch()`, which walks the branch history oldest-to-newest and copies non-excluded commits through `append_commit()`. `bup_rm()` builds `updated_refs`, writes replacement commits with `PackWriter` for save removal, then performs `git.delete_ref()` or `git.update_ref()`.

State, dependencies, and integration: state changes are Git refs and new local pack objects. It depends on VFS resolution, `git.rev_list`, `git.catpipe`, `get_commit_items`, `LocalPackStore`, and error collection in `bup.helpers`. It integrates with GC because removed refs leave now-unreachable objects that `bup gc` later prunes.

Risks and tests: history rewriting assumes all selected saves are on one branch and that `filter_branch()` can find at least one removed commit. Ref updates are attempted per ref, so partial failure is possible after generated pack data exists. Direct tests are outside this subset (`test-rm*`), while this subset’s `test-gc` and `test-fsck` exercise branch deletion effects and orphaned pack cleanup after `bup rm --unsafe`.
<!-- END_FILE_RESEARCH: sources/sync-backup/bup/lib/bup/rm.py -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/bup/lib/bup/shquote.py -->
## sources/sync-backup/bup/lib/bup/shquote.py

Purpose: provides byte-oriented, shell-like token splitting and quoting utilities used by interactive completion and command rendering.

Important APIs and control flow: `_quotesplit()` is the state machine for quotes, backslashes, whitespace, and word offsets. `quotesplit()` returns successfully parsed `(offset, word)` tuples and suppresses `QuoteError` for unfinished input. `unfinished_word()` reports the current quote character and partial word. `quotify()`, `quotify_list()`, and `what_to_add()` render safe completions using minimal quoting.

State and dependencies: the module is stateless apart from constants `q` and `qq`; it depends only on `re`. It intentionally differs from POSIX shell parsing by dequoting only words that begin with a quote, which is important for readline completion stability.

Risks and tests: backslash handling in single quotes is deliberately narrow, and callers must not treat this as a general shell parser. Byte semantics are important; passing text strings would fail or produce incorrect regex behavior. Test coverage is likely in broader shell/completion tests outside this subset; this subset has no direct shquote test file.
<!-- END_FILE_RESEARCH: sources/sync-backup/bup/lib/bup/shquote.py -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/bup/lib/bup/source_info.py -->
## sources/sync-backup/bup/lib/bup/source_info.py

Purpose: archive-time fallback metadata for source checkout identity. It is intended for Git archive keyword expansion.

Important APIs and state: exports `commit`, `date`, and `modified`. In the source tree these default to `$Format:%H$`, `$Format:%ci$`, and `False`; archive generation can expand the placeholders. `version.py` imports this when `checkout_info` is unavailable.

Integration and risks: correctness depends on release/archive tooling replacing the placeholders. `version.py` asserts that fallback archive values no longer start with `$Format`, so an unexpanded archive without `checkout_info` fails fast. Test signals are indirect through `bup version`, `test-install`, and release/versioning tests outside this subset.
<!-- END_FILE_RESEARCH: sources/sync-backup/bup/lib/bup/source_info.py -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/bup/lib/bup/ssh.py -->
## sources/sync-backup/bup/lib/bup/ssh.py

Purpose: starts a remote `bup` subcommand over SSH, or a local subprocess in test mode.

Important APIs and control flow: `connect(destination, port, subcmd, stderr=None)` validates `subcmd` with a strict alphanumeric/dash/underscore regex. Empty destination or `b'-'` is accepted only when `BUP_TEST_LEVEL` is set, in which case it runs `[path.exe(), subcmd]`. Real remote mode builds `ssh [-p port] destination -- sh -c 'BUP_DEBUG=... BUP_FORCE_TTY=... bup subcmd'` and returns a `Popen` with piped stdin/stdout and a new session.

State and dependencies: environment values come from `bup.compat.environ`; executable path comes from `bup.path.exe()`. It integrates with remote repository operations through client-side transports.

Risks and tests: destination and port are passed as argv elements, but the remote shell command interpolates debug values and `subcmd`; the regex is the key injection control for `subcmd`. Test mode is guarded to avoid accidental local execution. Remote behavior is indirectly covered by `bup on`, `save -r -:repo`, `init --remote`, and `test-gc` remote scenarios.
<!-- END_FILE_RESEARCH: sources/sync-backup/bup/lib/bup/ssh.py -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/bup/lib/bup/tree.py -->
## sources/sync-backup/bup/lib/bup/tree.py

Purpose: constructs Git tree objects and `.bupm` metadata blobs from ordered filesystem/archive entries, including optional split-tree layout for very large directories.

Important APIs and control flow: `TreeItem`, `RawTreeItem`, and `SplitTreeItem` model tree entries. `_dir_metadata()` decides whether a `.bupm` is necessary and handles lost metadata during repair. `Stack` is the main builder: callers `push()` directories, `append_to_current()` entries, and `pop()` to write trees. `_write_tree()` writes a normal tree plus optional `.bupm`; `_write_split_tree()` chunks directory entries by name using `RecordHashSplitter`, builds `.bupd` subtrees, abbreviates internal names, and recursively writes upper levels.

State and persistence: stack state is in memory; persistence happens through repo `write_tree` and `write_bupm`. It depends on hashsplit config, Git mode constants, name mangling, `Metadata`, `LostMetadata`, and `add_error()` for duplicate names.

Risks and tests: correctness depends on stable sorting, name abbreviation uniqueness, metadata order matching VFS readers, and split-tree internal names ending in depth markers. Duplicate names are ignored with errors. Strong test signals include `test-get-rewrite-missing` for split-tree repair, `test-gc-removes-incomplete-trees` for incomplete split objects, and tree-splitting tests outside this subset.
<!-- END_FILE_RESEARCH: sources/sync-backup/bup/lib/bup/tree.py -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/bup/lib/bup/url.py -->
## sources/sync-backup/bup/lib/bup/url.py

Purpose: byte-preserving parsing and rendering of Bup path URLs, especially file/ssh-style URLs where command-line paths must not be decoded accidentally.

Important APIs and control flow: `URL` is a frozen dataclass with scheme, host, port, user, and path. `parse_bytes_path_url()` parses RFC-3986-like URLs, percent-decodes user/host but leaves path bytes untouched, handles IPv4/IPv6 literals, drops passwords, and returns either `None`, a `URL`, or an error string. `render_url()` percent-encodes user/host, handles IPv6 brackets, and can dot-encode relative paths under authorities via `dot_encode_path()`.

State and dependencies: stateless; depends on `ipaddress`, `urllib.parse.unquote_to_bytes`, regexes, and `path_msg()` for diagnostics. Integration points are remote repo/config parsing and command-line source/destination handling.

Risks and tests: path bytes are intentionally not percent-decoded, so callers must choose this parser only where that behavior is desired. `port=0` is not rendered because `if self.port` treats zero as absent. Invalid host handling is regex based after IP checks. Direct URL tests are outside this subset, while import and remote init/save scenarios exercise URL-like `-:repo` paths.
<!-- END_FILE_RESEARCH: sources/sync-backup/bup/lib/bup/url.py -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/bup/lib/bup/version.py -->
## sources/sync-backup/bup/lib/bup/version.py

Purpose: computes Bup’s byte-string version from checkout or archive metadata.

Important APIs and state: imports `checkout_info` when available; otherwise uses `source_info`. Exports `date`, `commit`, `modified`, `base_version`, and `version`. `base_version` is `b'0.34~'`; because it ends in `~`, the commit id is appended. A modified checkout appends `b'+'`.

Integration and risks: Debian-style `~` ordering is intentional. Archive fallback asserts expanded `source_info` values, so packaging must include valid metadata. User-facing commands (`bup version`, installer smoke tests, repair trailers) depend on this. Test signals include `test-install`, `test-help` indirectly, and repair trailer checks in `test-get-repair-bupm` and `test-get-rewrite-missing`.
<!-- END_FILE_RESEARCH: sources/sync-backup/bup/lib/bup/version.py -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/bup/lib/bup/vfs.py -->
## sources/sync-backup/bup/lib/bup/vfs.py

Purpose: exposes repository contents as a virtual filesystem shaped like `/BRANCH/latest/...`, `/BRANCH/SAVE-DATE/...`, and `/.tag/TAG/...`. It unifies Git objects, Bup metadata, split trees, chunked files, symlinks, tags, and revision lists behind path-oriented APIs.

Important APIs and control flow: item types include `Item`, `Chunky`, `FakeLink`, `Root`, `Tags`, `RevList`, and `Commit`. `contents()` dispatches by item kind to `root_items()`, `revlist_items()`, `tags_items()`, or `tree_items()`. `resolve()` walks path segments, handles `.`/`..`, symlink following and loop limits, and delegates to remote repos when available. File reads use `_FileReader` and `_ChunkReader` to concatenate blob or chunk-tree data. Metadata helpers include `item_mode()`, `item_size()`, `augment_item_meta()`, `fill_in_metadata_if_dir()`, and `ensure_item_has_metadata()`. `join()` recursively emits blob data reachable from a ref.

State and persistence: VFS itself persists nothing, but maintains a process cache for commit items, revlists, and path resolutions. Cache keys include repo identity, `want_meta`, follow mode, parent path, and requested path. It depends on Git object parsing, metadata encoding, stat mode constants, and Bup’s `.bupm`/`.bupd` conventions.

Risks and integration: metadata may be a full `Metadata`, an int mode, or `LostMetadata`; callers must not mutate metadata in place. Repair mode changes missing/broken metadata behavior and coordinates tightly with `tree.py` and `rewrite.py`. Split-tree traversal, bupm entry counts, symlink fallback to blobs, and remote delegation are high-risk areas. Test signals are broad: `test-cat-file`, `test-empty-metadata`, `test-fuse`, `test-get-missing`, `test-get-repair-bupm`, `test-get-repair-symlinks`, `test-get-rewrite-missing`, `test-gc-removes-incomplete-trees`, and many save/restore tests outside this subset.
<!-- END_FILE_RESEARCH: sources/sync-backup/bup/lib/bup/vfs.py -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/bup/lib/bup/vint.py -->
## sources/sync-backup/bup/lib/bup/vint.py

Purpose: implements Bup’s binary variable-length integer and byte-vector encodings, with C helper fast paths and Python fallbacks.

Important APIs and control flow: `encode_vuint()`/`read_vuint()` encode unsigned integers seven bits at a time. `encode_vint()`/`read_vint()` reserve sign information in the first byte. `write_bvec()`, `read_bvec()`, `encode_bvec()`, and `skip_bvec()` handle length-prefixed byte strings. `send()`, `recv()`, `pack()`, and `unpack()` provide simple format strings: `V`, `v`, and `s`.

State and dependencies: stateless; depends on `BytesIO` and `_helpers` C implementations. Fallback code handles overflows from C helpers and raises `ValueError` for negative unsigned values.

Risks and tests: EOF handling is strict for reads, but `skip_bvec()` reads once and only verifies some bytes were returned, so short skips can leave unread bytes if used with nonblocking/partial streams. Format strings reject unknown types. Direct tests are likely in metadata/vint unit tests outside this subset; metadata, repo protocol, and index formats indirectly depend on it.
<!-- END_FILE_RESEARCH: sources/sync-backup/bup/lib/bup/vint.py -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/bup/lib/bup/xstat.py -->
## sources/sync-backup/bup/lib/bup/xstat.py

Purpose: provides enhanced stat/time helpers with nanosecond precision and portable wrappers for Cygwin UID/GID assertions.

Important APIs and control flow: time converters map between `(sec,nsec)`, timeval, integer filesystem nanoseconds, floor seconds, and printable seconds bytes. `utime()` and `lutime()` set nanosecond timestamps, with `lutime()` avoiding symlink following. On non-Cygwin platforms, `stat`, `fstat`, and `lstat` alias `os` functions; Cygwin wrappers assert nonnegative uid/gid. `mode_str()`, `classification_str()`, and `local_time_str()` render ls-like modes/classifiers/times.

State and dependencies: stateless; depends on `os`, `sys`, `time`, and Python `stat`. It integrates with metadata capture, `bup xstat`, `ls`, restore, and FUSE presentation.

Risks and tests: negative timestamp formatting adjusts seconds when nanoseconds are nonzero; symlink timestamp support depends on platform `os.utime(..., follow_symlinks=False)`. Tests include `test-fuse` for pre-epoch clamping in mounted output, `test-empty-metadata` for displayed modes, and repair tests that inspect `bup xstat`.
<!-- END_FILE_RESEARCH: sources/sync-backup/bup/lib/bup/xstat.py -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/bup/lib/cmd/bup-import-rdiff-backup -->
## sources/sync-backup/bup/lib/cmd/bup-import-rdiff-backup

Purpose: imports an rdiff-backup repository into a Bup branch by restoring each increment to a temporary directory and saving it with the original timestamp.

Important APIs and control flow: the shell script supports `-n/--dry-run`, validates two arguments, lists increments using `rdiff-backup --list-increments --parsable-output`, then loops through `timestamp type` lines. Each iteration creates a temp restore directory, runs `rdiff-backup -r timestamp`, indexes with a temporary index file, and saves with `bup save --strip --date=timestamp -n branch`.

State and dependencies: creates temporary restore dirs and index files in the current directory, and writes Bup repo objects/refs through `bup index` and `bup save`. It depends on GNU-ish `date -d @timestamp`, `mktemp`, `rdiff-backup`, and the colocated `bup` executable.

Risks and tests: cleanup is manual per successful iteration; failures before `rm -rf` can leave temp directories or temp index names. Timestamp parsing and `date -d` are portability risks. `test-import-rdiff-backup` skips when `rdiff-backup` is unavailable and verifies imported save count and latest contents against `Documentation`.
<!-- END_FILE_RESEARCH: sources/sync-backup/bup/lib/cmd/bup-import-rdiff-backup -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/bup/lib/cmd/bup-import-rsnapshot -->
## sources/sync-backup/bup/lib/cmd/bup-import-rsnapshot

Purpose: imports rsnapshot-style directory snapshots into Bup branches.

Important APIs and control flow: supports dry-run, validates a snapshot root plus optional target branch, changes to the snapshot root, then iterates snapshot directories and branch subdirectories. For each selected branch, it obtains ctime using Perl `stat`, indexes the branch path into `bupindex.$BRANCH.tmp`, and saves with `--strip --date=$DATE -n $BRANCH`.

State and dependencies: writes temporary index files in the snapshot root and persists data through Bup repo objects/refs. It depends on `basename`, `perl`, shell globbing, and the local `bup` wrapper.

Risks and tests: branch names are used in temp index filenames without sanitization, so odd names can collide or create awkward paths. It uses ctime rather than snapshot directory names. There is no listed direct test in this subset; behavior is analogous to rdiff/duplicity import tests.
<!-- END_FILE_RESEARCH: sources/sync-backup/bup/lib/cmd/bup-import-rsnapshot -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/bup/lib/cmd/bup.c -->
## sources/sync-backup/bup/lib/cmd/bup.c

Purpose: native launcher for the `bup` command. It locates the installed library directory, prepends it to `PYTHONPATH`, exposes original argv through an embedded `bup_main` Python module, and starts Python with `-m bup.main` or development entry modes.

Important APIs and control flow: `get_argv()` returns C argv as Python bytes. `setup_bup_main_module()` records original `PYTHONPATH` and registers the module. Platform-specific `exe_parent_dir()` resolves the executable using macOS `_NSGetExecutablePath`, FreeBSD `sysctl`, Linux/Sun `/proc`, or PATH search plus `realpath`. `prepend_lib_to_pythonpath()` validates the lib dir and updates the environment. Three `main()` variants handle normal, `BUP_DEV_BUP_PYTHON`, and `BUP_DEV_BUP_EXEC` builds.

State and dependencies: process-global state stores argv and original Python path. It depends on Python C API, `bup/intprops.h` for overflow-safe buffer doubling, and `bup/io.h` for fatal diagnostics.

Risks and tests: path discovery is platform-sensitive; failures abort with Bup exit status 2. Python <3.7 is rejected at compile time, and Python <3.8 uses `bup_py_bytes_main()`. Test signals include `test-install` for installed launcher behavior, `test-help` for main command dispatch, and `test_argv.py` outside this subset for argv semantics.
<!-- END_FILE_RESEARCH: sources/sync-backup/bup/lib/cmd/bup.c -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/bup/pylint -->
## sources/sync-backup/bup/pylint

Purpose: repository wrapper for running pylint under Bup’s configured Python environment.

Important control flow: reads `config/config.var/with-pylint`. `yes` runs, `no` exits successfully with a message, and `maybe` runs only if `dev/have-pylint` succeeds. It prepends `test/lib` to `PYTHONPATH`. With no arguments it runs pylint on `lib`, then on tests with wildcard import warnings disabled; with arguments it execs pylint directly under `dev/bup-python`.

State and dependencies: depends on configure output, `dev/have-pylint`, `dev/bup-python`, and test support libraries. It changes only process environment.

Risks and tests: unexpected config values exit 2. The wrapper and `pytest` need synchronized environment behavior per comments. It is a developer quality gate rather than product runtime; no direct test in this subset.
<!-- END_FILE_RESEARCH: sources/sync-backup/bup/pylint -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/bup/pytest -->
## sources/sync-backup/bup/pytest

Purpose: repository wrapper for running pytest with Bup’s Python and default test selection.

Important control flow: shell prelude sets `BUP_DIR` and `GIT_DIR` to `/dev/null`, prepends `test/lib` to `PYTHONPATH`, and execs `dev/bup-python` on the script itself. Python code defaults to `pytest -v -m 'not release'`. If `xdist` is installed it enables work stealing for versions at least 3.2.1 and preserves user args; otherwise it strips `-n` options before invoking pytest.

State and dependencies: no persistent state; depends on `pytest`, optional `xdist`, `shlex`, `sys`, and the repo’s `conftest.py`.

Risks and tests: argument filtering only handles common `-n` forms. Mark defaults mean release tests are excluded unless requested. It is exercised whenever the suite is run, and `pytest.ini` supplies collection roots and marker declaration.
<!-- END_FILE_RESEARCH: sources/sync-backup/bup/pytest -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/bup/pytest.ini -->
## sources/sync-backup/bup/pytest.ini

Purpose: pytest configuration for Bup’s test suite.

Important content: declares `testpaths = test/int test/ext`, and registers the `release` marker. It intentionally does not set `addopts`; the `./pytest` wrapper owns defaults.

State, dependencies, and risks: no runtime state. Test discovery depends on `test/ext/conftest.py` for non-Python executable tests. Running plain `pytest` without the wrapper will not get the wrapper’s default arguments or environment.
<!-- END_FILE_RESEARCH: sources/sync-backup/bup/pytest.ini -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/bup/src/bup.h -->
## sources/sync-backup/bup/src/bup.h

Purpose: shared C header defining Bup process exit status constants.

Important APIs: `BupExit` maps success/true to 0, false to 1, and failure to 2. C launcher and support code use these constants for consistent command exit behavior.

State, dependencies, and risks: no state or dependencies. Consumers must preserve the semantic distinction between predicate false (`1`) and operational failure (`2`). Test scripts use expected failure codes across init/help/fsck/get scenarios.
<!-- END_FILE_RESEARCH: sources/sync-backup/bup/src/bup.h -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/bup/src/bup/compat.c -->
## sources/sync-backup/bup/src/bup/compat.c

Purpose: compatibility implementation for invoking Python with byte argv on Python 3.7.

Important APIs and control flow: when Python is older than 3.8, `bup_py_bytes_main(argc, argv)` allocates a wide argv array with `PyMem_RawMalloc`, decodes each byte argv using `Py_DecodeLocale`, reports decode/allocation errors with `die()`, and calls `Py_Main()`.

State and dependencies: transient allocation only; depends on Python C API, `bup.h`, `bup/io.h`, and compile-time Python version checks. For Python 3.8+, `bup.c` uses `Py_BytesMain` instead.

Risks and tests: decoded wide strings are not freed before `Py_Main()` exits, which is acceptable for process lifetime. Error paths must avoid returning with a Python exception only. Launcher behavior is covered indirectly by installed and development command tests.
<!-- END_FILE_RESEARCH: sources/sync-backup/bup/src/bup/compat.c -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/bup/src/bup/compat.h -->
## sources/sync-backup/bup/src/bup/compat.h

Purpose: declares compatibility entry points used by the native launcher.

Important APIs: exposes `int bup_py_bytes_main(int argc, char **argv);`. Actual use is gated in `bup.c` for Python 3.7.

State and risks: no state. Header is intentionally tiny; mismatches with `compat.c` would break old-Python builds.
<!-- END_FILE_RESEARCH: sources/sync-backup/bup/src/bup/compat.h -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/bup/src/bup/intprops.h -->
## sources/sync-backup/bup/src/bup/intprops.h

Purpose: vendored gnulib integer-properties header used for portable integer bounds and overflow-safe arithmetic in C code.

Important APIs: defines type/expression property macros (`TYPE_WIDTH`, `TYPE_MINIMUM`, `TYPE_MAXIMUM`, `EXPR_SIGNED`), overflow predicates (`INT_ADD_OVERFLOW`, `INT_SUBTRACT_OVERFLOW`, `INT_MULTIPLY_OVERFLOW`, division/remainder/shift variants), wrap helpers (`INT_*_WRAPV`), and success helpers (`INT_ADD_OK`, `INT_SUBTRACT_OK`, `INT_MULTIPLY_OK`). It uses compiler builtins when reliable and falls back to range calculations.

State and dependencies: preprocessor-only, dependent on `<limits.h>` and compiler feature detection. Bup uses it in the launcher for path-buffer growth and in `pyutil` allocation/type conversion helpers.

Risks and tests: macro arguments may be evaluated multiple times, so callers must avoid side effects. The header assumes two’s-complement integer representation without padding. Compiler-specific branches are high-risk for portability, but this is mature gnulib code. Bup test coverage is indirect via C extension builds, launcher execution, and memory allocation overflow paths where present.
<!-- END_FILE_RESEARCH: sources/sync-backup/bup/src/bup/intprops.h -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/bup/src/bup/io.c -->
## sources/sync-backup/bup/src/bup/io.c

Purpose: minimal C diagnostic helpers for Bup native code.

Important APIs: `msg(FILE*, fmt, ...)` writes `bup: ` plus formatted output to a stream. `die(exit_status, fmt, ...)` writes the same prefix to stderr and exits. Both are annotated for printf format checking and exit with `BUP_EXIT_FAILURE` if output itself fails.

State and dependencies: no persistent state; depends on stdio, stdarg, stdlib, `bup.h`, and `bup/io.h`.

Risks and tests: because diagnostics exit if writing fails, callers cannot recover from broken stderr/stdout. It is used by launcher and compatibility code; tests observe its output prefixes indirectly in command failure scenarios.
<!-- END_FILE_RESEARCH: sources/sync-backup/bup/src/bup/io.c -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/bup/src/bup/io.h -->
## sources/sync-backup/bup/src/bup/io.h

Purpose: header declaring C diagnostic helpers.

Important APIs: declares `msg()` and `die()` for use by launcher/support code.

State and risks: no state. It must stay in sync with printf attributes and signatures in `io.c`; consumers rely on `die()` not returning.
<!-- END_FILE_RESEARCH: sources/sync-backup/bup/src/bup/io.h -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/bup/src/bup/pyutil.c -->
## sources/sync-backup/bup/src/bup/pyutil.c

Purpose: C extension utility functions for safe allocation and Python integer conversion.

Important APIs and control flow: `checked_calloc()` returns `calloc()` memory or sets `PyErr_NoMemory()`. `checked_malloc(n, size)` uses `INT_MULTIPLY_OK` to reject allocation-size overflow, then mallocs or raises memory errors. `bup_ulong_from_py()`, `bup_uint_from_py()`, and `bup_ullong_from_py()` validate `PyLong` inputs, call Python unsigned conversion APIs, and replace generic overflow messages with argument-specific diagnostics.

State and dependencies: no persistent state; depends on Python C API, generated config, `pyutil.h`, and `intprops.h`.

Risks and tests: callers must check NULL/zero returns and propagate Python exceptions. Unsigned conversions reject negative Python ints through Python’s conversion APIs. Coverage is indirect through C helpers such as `_helpers` and any tests exercising large numeric inputs.
<!-- END_FILE_RESEARCH: sources/sync-backup/bup/src/bup/pyutil.c -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/bup/src/bup/pyutil.h -->
## sources/sync-backup/bup/src/bup/pyutil.h

Purpose: shared C/Python utility header for allocation, Python integer conversion, and integral assignment checks.

Important APIs: declares checked allocation and unsigned conversion helpers. `BUP_LONGISH_TO_PY(x)` chooses signed or unsigned Python long creation based on expression signedness. `BUP_ASSIGN_PYLONG_TO_INTEGRAL(dest, pylong, overflow)` assigns a Python integer into an arbitrary integral destination, distinguishing Python overflow from C range overflow.

State and dependencies: macro-only plus declarations; depends on `sys/types.h` and `intprops.h`, and assumes Python headers are already available in translation units using Python APIs.

Risks and tests: the assignment macro uses GNU statement-expression syntax, so portability depends on supported compilers. Callers must inspect both return value and overflow flag. Indirect test coverage comes from C extension behavior.
<!-- END_FILE_RESEARCH: sources/sync-backup/bup/src/bup/pyutil.h -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/bup/test/__init__.py -->
## sources/sync-backup/bup/test/__init__.py

Purpose: marks `test` as a Python package.

Important APIs and state: the file is empty and exports no symbols. Its presence can support imports such as `test.lib` in tools or tests depending on package semantics.

Risks and tests: no behavioral risk inside the file itself. Because it is empty, the research artifact records that there is no control flow, state, or dependency to inspect.
<!-- END_FILE_RESEARCH: sources/sync-backup/bup/test/__init__.py -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/bup/test/bin/sort-z -->
## sources/sync-backup/bup/test/bin/sort-z

Purpose: test helper that runs a null-delimited sort portably.

Important control flow: if `uname -s` is NetBSD, it executes `sort -R 000 "$@"`; otherwise it executes `sort -z "$@"`.

State and dependencies: stateless shell wrapper depending on platform `sort` behavior. It integrates with tests needing NUL-delimited ordering.

Risks and tests: platform-specific flags may drift with system utilities. The script exits immediately on command failure due to `set -e`.
<!-- END_FILE_RESEARCH: sources/sync-backup/bup/test/bin/sort-z -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/bup/test/ext/conftest.py -->
## sources/sync-backup/bup/test/ext/conftest.py

Purpose: pytest collector for Bup’s executable `test-*` shell scripts using the wvtest protocol.

Important APIs and control flow: `BupSubprocTestRunner.runtest()` creates a temporary HOME under `test/tmp`, runs the script as a subprocess, writes combined output to pytest stdout, maps `! ... skip ok` lines to `pytest.skip`, detects `! ... failed` lines and `AssertionError`, and raises `BupSubprocFailure` with status/failure lines. `BupSubprocTestFile.collect()` yields one runner per executable file. `pytest_collect_file()` supports pytest 6 and 7 APIs. `_collect_item()` ignores backup files and marks `test-versioning-and-archive` as release.

State and dependencies: per-test temporary HOME is the main state isolation mechanism. It depends on `pytest`, `bup.helpers.temp_dir`, and byte-stream output handling.

Risks and tests: all shell output is buffered before inspection, so very large output can be memory-heavy. Failure detection depends on wvtest line conventions. This file is the test harness for every listed `test/ext/test-*` script.
<!-- END_FILE_RESEARCH: sources/sync-backup/bup/test/ext/conftest.py -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/bup/test/ext/test-btl -->
## sources/sync-backup/bup/test/ext/test-btl

Purpose: validates helper functions from `test/lib/btl.sh` for redirecting stdout/stderr and preserving exit codes.

Important control flow: defines `out-err()` that writes to both streams, then checks `err-to`, `out-to`, and `both-to` capture the correct stream content. A second group verifies those wrappers preserve success, failure, and an explicit exit status 42.

State and dependencies: creates temporary log files under a temp directory. Depends on `wvtest-bup.sh` and `btl.sh`.

Risks and integration: these helpers are used by many later shell tests to assert stderr/stdout content, so this test protects the reliability of the test suite itself.
<!-- END_FILE_RESEARCH: sources/sync-backup/bup/test/ext/test-btl -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/bup/test/ext/test-cat-file -->
## sources/sync-backup/bup/test/ext/test-cat-file

Purpose: exercises `bup cat-file` argument validation and data/metadata extraction.

Important control flow: initializes a repo, saves a source file, checks invalid invocations and error messages, then compares `bup cat-file branch/latest/path` output to the original file. It verifies `--meta` output against `bup meta --create` while ignoring atime, and checks `--bupm` output against the raw `.bupm` object found via `git ls-tree`.

State and dependencies: uses a temp repo as both `BUP_DIR` and `GIT_DIR`, plus `dev/git-cat-tree`. It integrates with VFS path resolution, metadata encoding, and Git tree lookup.

Risks covered: rejects ambiguous flags, missing branch/revision paths, non-directory `--bupm` targets, and non-file data targets.
<!-- END_FILE_RESEARCH: sources/sync-backup/bup/test/ext/test-cat-file -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/bup/test/ext/test-comparative-split-join -->
## sources/sync-backup/bup/test/ext/test-comparative-split-join

Purpose: compares current Bup split/join behavior and repository artifacts against another Bup executable specified by `BUP_TEST_OTHER_BUP`.

Important control flow: skips without the other executable, classifies versions by pack-name algorithm, then for size 0 and five random sizes creates parallel repos, writes random data, compares split tree ids, compares joined data, optionally compares pack/index files, normalizes HEAD/repo-id differences, and compares repository trees.

State and dependencies: uses random seeds, temp repos, `bup random`, `split -t`, `join`, Git config, and `dev/compare-trees`.

Risks covered: split determinism, join compatibility, pack format changes across versions, default branch name changes, and repo-id/umask differences.
<!-- END_FILE_RESEARCH: sources/sync-backup/bup/test/ext/test-comparative-split-join -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/bup/test/ext/test-compression -->
## sources/sync-backup/bup/test/ext/test-compression

Purpose: verifies save compression levels affect repository size without changing saved contents.

Important control flow: saves `Documentation` once with `-0` and once with `-9`, compares latest archive listing to source listing each time, computes tar-based repo sizes, and asserts compression level 9 is smaller than level 0.

State and dependencies: repeatedly removes and recreates the temp Bup repo. Depends on `bup index`, `bup save`, `bup ls`, `tar`, and `wc`.

Risks covered: compression-level propagation into pack writing and preservation of directory contents under different compression settings.
<!-- END_FILE_RESEARCH: sources/sync-backup/bup/test/ext/test-compression -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/bup/test/ext/test-drecurse -->
## sources/sync-backup/bup/test/ext/test-drecurse

Purpose: verifies recursive directory listing order and exclude behavior for `bup drecurse`.

Important control flow: builds a small tree with files, directories, and a symlink, then compares output for base traversal, file/dir/symlink excludes, absolute path excludes, `--exclude-from`, and regex excludes for relative and absolute roots.

State and dependencies: temp repo and filesystem tree only; depends on `bup drecurse`.

Risks covered: postorder traversal expectations, directory trailing slash rendering, symlink handling, and consistency between literal and regex excludes.
<!-- END_FILE_RESEARCH: sources/sync-backup/bup/test/ext/test-drecurse -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/bup/test/ext/test-empty-metadata -->
## sources/sync-backup/bup/test/ext/test-empty-metadata

Purpose: tests VFS/metadata behavior when `.bupm` entries are empty or missing for non-directories.

Important control flow: saves files and a fifo, checks normal `bup ls -l`, then rewrites the tree’s `.bupm` with selected entries cleared via `dev/clear-bupm-entries`. It verifies lost metadata shows restrictive permissions and unknown owner/time, then restores under `umask 0` and checks filesystem modes.

State and dependencies: directly manipulates Git tree objects and branch refs inside the temp repo. Depends on `bup meta`, `bup join`, `git hash-object/mktree/commit-tree`, and restore.

Risks covered: lost metadata must not become overly permissive; special files with lost metadata become safe regular placeholders.
<!-- END_FILE_RESEARCH: sources/sync-backup/bup/test/ext/test-empty-metadata -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/bup/test/ext/test-fsck -->
## sources/sync-backup/bup/test/ext/test-fsck

Purpose: exercises repository integrity checking, par2 generation/repair, damaged pack/index handling, and orphaned pack-related file detection.

Important control flow: saves sample data, runs normal and quick fsck, tests par2 availability, damages idx and pack files with `bup damage`, checks repair return codes with and without par2, rejects empty par2 index/volume files, over-damages packs, and finally verifies fsck reports lingering files without corresponding `.pack`.

State and dependencies: mutates pack, idx, par2, and arbitrary pack-directory files. Depends on `bup fsck`, `damage`, `gc`, `rm --unsafe`, optional par2, and Git pack layout.

Risks covered: repair code must distinguish index-only damage from pack damage, avoid accepting empty par2 artifacts, and report orphaned sidecar files after GC.
<!-- END_FILE_RESEARCH: sources/sync-backup/bup/test/ext/test-fsck -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/bup/test/ext/test-fuse -->
## sources/sync-backup/bup/test/ext/test-fuse

Purpose: validates the FUSE view of a Bup repository.

Important control flow: skips if FUSE import/version, `fusermount`, or `/dev/fuse` access is unavailable. Creates a repo with two potential save timestamps, mounts `bup fuse -f`, checks branch/save/latest listings and file content, confirms new saves are not noticed by an existing mount, then remounts with `--meta` and verifies permissions, owner/group, and pre-epoch timestamp clamping.

State and dependencies: uses a live FUSE mount and cleanup trap. Depends on VFS, metadata public rendering, `stat`, and timezone UTC.

Risks covered: stale mount caching, metadata presentation, timestamp lower bound behavior, and mount cleanup.
<!-- END_FILE_RESEARCH: sources/sync-backup/bup/test/ext/test-fuse -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/bup/test/ext/test-gc -->
## sources/sync-backup/bup/test/ext/test-gc

Purpose: tests garbage collection preservation and pruning across normal, rewritten, remote, and threshold/ignore-missing scenarios.

Important control flow: verifies unchanged repos remain restorable, removed branch data is pruned, rewritten branches keep reachable data, remote save/get after GC works, `bup on -` workflows survive GC, `--threshold 0` rewrites packs without losing objects, and `--ignore-missing` reports missing source objects while still rewriting eligible packs.

State and dependencies: repeatedly recreates repos, removes refs manually, measures data size, uses remote `-:repo`, `bup get`, `bup rm --unsafe`, Git show-index, and `dev/perforate-repo`.

Risks covered: reachability accounting, remote pack reuse after GC, object identity preservation under repacking, and missing-object handling during collection.
<!-- END_FILE_RESEARCH: sources/sync-backup/bup/test/ext/test-gc -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/bup/test/ext/test-gc-removes-incomplete-trees -->
## sources/sync-backup/bup/test/ext/test-gc-removes-incomplete-trees

Purpose: regression test ensuring GC does not leave reusable incomplete split trees.

Important control flow: creates a save arranged across two packfiles with held, transient, and straddling trees. It copies a complete repo, promotes one subtree, removes the original branch, runs GC with a threshold, then fetches the original back from the complete repo and verifies `bup join` succeeds.

State and dependencies: manipulates pack size limit, branch refs, `bup get --append`, `bup rm --unsafe`, and GC. Uses object location checks with `git show-index`.

Risks covered: probabilistic pack retention must not keep parent split-tree fragments without required child objects, because later get/rewrite code may otherwise reuse broken trees.
<!-- END_FILE_RESEARCH: sources/sync-backup/bup/test/ext/test-gc-removes-incomplete-trees -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/bup/test/ext/test-get-excludes -->
## sources/sync-backup/bup/test/ext/test-get-excludes

Purpose: verifies contextual exclude handling for `bup get --rewrite`.

Important control flow: saves files `one`, `two`, and `three`, then rewrites with `--exclude-rx 't.*'`, with `--no-excludes`, and with multiple picks that change exclude context between destinations. It also checks that contextual arguments with no effect are rejected.

State and dependencies: temp repo, `bup get --rewrite`, and `bup ls`.

Risks covered: `rewrite.py` must invalidate directory mapping reuse when excludes change, while command parsing must reject ignored contextual options.
<!-- END_FILE_RESEARCH: sources/sync-backup/bup/test/ext/test-get-excludes -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/bup/test/ext/test-get-missing -->
## sources/sync-backup/bup/test/ext/test-get-missing

Purpose: verifies `bup get` behavior when source trees are incomplete.

Important control flow: saves two similar directories, prechecks a complete get, removes each directory’s `.bupm` object with `perforate-repo`, then tests failure without ignore, failure when ignore is overridden, skip-and-status behavior with `--ignore-missing --unnamed`, and ordering when multiple gets use different ignore contexts.

State and dependencies: mutates object storage by dropping oids. Depends on `bup get`, `bup join`, Git tree lookup, and stderr matching.

Risks covered: missing source objects must not be silently copied except in the limited unnamed ignore-missing mode, and contextual ignore settings must not leak across later operations.
<!-- END_FILE_RESEARCH: sources/sync-backup/bup/test/ext/test-get-missing -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/bup/test/ext/test-get-repair-bupm -->
## sources/sync-backup/bup/test/ext/test-get-repair-bupm

Purpose: tests repair of abridged `.bupm` metadata caused by older Bup bugs.

Important control flow: creates two saves, then replaces the newer save’s `.bupm` with the older shorter one. It validates refs detect the abridged metadata, verifies normal rewrite rejects it, then runs `bup get --repair`, captures the repair ID, checks commit trailers for version/argv/repair/save/lost-meta entries, restores the repaired save, and inspects restrictive metadata with `bup xstat`.

State and dependencies: direct Git tree and branch manipulation. Depends on `validate-refs --bupm`, `rewrite.py` repair mode, trailer generation, restore, and xstat.

Risks covered: metadata loss must be explicit in trailers and repaired files must restore with restrictive safe defaults, not guessed original metadata.
<!-- END_FILE_RESEARCH: sources/sync-backup/bup/test/ext/test-get-repair-bupm -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/bup/test/ext/test-get-repair-symlinks -->
## sources/sync-backup/bup/test/ext/test-get-repair-symlinks

Purpose: tests repair behavior for missing and mismatched symlink blobs.

Important control flow: first saves a symlink with metadata, drops its blob, verifies ordinary get notices the missing object, and checks `--rewrite` and `--repair` restore the link blob with trailers. It then rewrites the symlink blob to a mismatched target, verifies `--rewrite` rejects and `--repair` fixes it. Finally it creates a bare Git-style repo without Bup metadata, drops the symlink blob, and verifies only `--repair` replaces it with an explanatory blob.

State and dependencies: direct object deletion and Git tree edits. Depends on VFS symlink target rules, `rewrite._rewrite_link()`, `bup join`, and commit trailer checks.

Risks covered: Bup must prefer metadata symlink targets when present, detect inconsistent blob targets, and distinguish restorable metadata-backed links from unrecoverable old/git symlinks.
<!-- END_FILE_RESEARCH: sources/sync-backup/bup/test/ext/test-get-repair-symlinks -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/bup/test/ext/test-get-rewrite-missing -->
## sources/sync-backup/bup/test/ext/test-get-rewrite-missing

Purpose: comprehensive rewrite/repair regression test for missing files, directories, chunked files, split trees, repair IDs, and contextual command combinations.

Important control flow: builds a repo with ordinary missing objects, a chunked partial file, and a split tree, records relevant oids, drops selected objects, and validates invalid option combinations. `repair-to-dest()` runs `bup get --repair`; the test verifies repair-id reporting, commit trailers, replacement blob contents for missing files/trees/chunked files, split-tree top/leaf/bupm repairs, behavior differences between `--rewrite`, `--repair`, `--copy`, and `--ignore-missing`, multiple repair IDs, and trailer non-accumulation across repaired saves.

State and dependencies: heavily mutates repos and object stores, uses split-tree config, Git plumbing, `dev/make-splittable-tree`, `dev/perforate-repo`, and `bup get`.

Risks covered: this is the strongest signal for `rewrite.py`, `tree.py`, and VFS repair semantics. It guards against unsafe reuse of missing-object conversions, context leakage, incorrect replacement content, and trailer accumulation.
<!-- END_FILE_RESEARCH: sources/sync-backup/bup/test/ext/test-get-rewrite-missing -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/bup/test/ext/test-help -->
## sources/sync-backup/bup/test/ext/test-help

Purpose: verifies top-level and command-specific help dispatch.

Important control flow: checks `bup -?`, `bup -h`, and `bup --help` print usage. If generated manpage `Documentation/bup-save.1` exists, it creates a temporary `MANPATH`, runs `bup help save` and `bup save --help` through `PAGER=cat`, and checks expected save help text.

State and dependencies: temp repo environment, optional documentation/manpage files, `man`/pager behavior.

Risks covered: launcher/main dispatch, help aliases, and installed documentation lookup.
<!-- END_FILE_RESEARCH: sources/sync-backup/bup/test/ext/test-help -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/bup/test/ext/test-import-duplicity -->
## sources/sync-backup/bup/test/ext/test-import-duplicity

Purpose: integration test for importing duplicity backups.

Important control flow: skips if `duplicity` is unavailable, syncs sample data, creates two duplicity backups with a tick and a new file, runs `bup import-duplicity`, checks save count and latest listing, restores latest, and compares trees. Expected differences allow timestamp and symlink metadata differences.

State and dependencies: writes duplicity cache and backup directory, uses `PASSPHRASE`, Bup import command, restore, and `dev/compare-trees`.

Risks covered: import timeline handling, latest content correctness, and known metadata limitations of duplicity imports.
<!-- END_FILE_RESEARCH: sources/sync-backup/bup/test/ext/test-import-duplicity -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/bup/test/ext/test-import-rdiff-backup -->
## sources/sync-backup/bup/test/ext/test-import-rdiff-backup

Purpose: integration test for `bup import-rdiff-backup`.

Important control flow: skips if `rdiff-backup` is unavailable, creates an rdiff-backup archive from `lib/cmd`, ticks, updates it from `Documentation`, runs the import command into a branch, then checks save count and latest listing against `Documentation`.

State and dependencies: depends on rdiff-backup command availability, Bup init/import, and filesystem listings.

Risks covered: import script argument handling, increment listing/restoration, timestamped saves, and latest content correctness.
<!-- END_FILE_RESEARCH: sources/sync-backup/bup/test/ext/test-import-rdiff-backup -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/bup/test/ext/test-index -->
## sources/sync-backup/bup/test/ext/test-index

Purpose: broad functional test for `bup index` and save interactions with index state.

Important control flow: checks exclude-file failure, empty index status, missing path behavior, indexing directories/files, status output for added/modified/fake-valid/fake-invalid paths, relative path output, save requirements, fifo handling, removal after reindex, tree regeneration when no files changed, and remote save argument validation.

State and dependencies: manipulates `$BUP_DIR/bupindex`, filesystem content, symlinks, fifos, and temp repo refs. Depends on `bup index`, `bup save`, `bup random`, and remote `-:repo`.

Risks covered: index correctness across file types, stale index entries, status formatting, and save/index consistency.
<!-- END_FILE_RESEARCH: sources/sync-backup/bup/test/ext/test-index -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/bup/test/ext/test-index-check-device -->
## sources/sync-backup/bup/test/ext/test-index-check-device

Purpose: root-only test for device-number sensitivity in index change detection.

Important control flow: skips unless root and loop filesystem tools are available. It creates an ext filesystem image, mounts copies through loopback and bind mounts, indexes one device as fake-valid, then remounts identical content from another device. Default indexing reports modified entries; `--no-check-device` treats them unchanged.

State and dependencies: mounts and unmounts loop filesystems and bind mounts. Depends on root privileges, `losetup`, `mke2fs`, `mount`, and `umount`.

Risks covered: index invalidation across device changes and user-controlled relaxation with `--no-check-device`.
<!-- END_FILE_RESEARCH: sources/sync-backup/bup/test/ext/test-index-check-device -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/bup/test/ext/test-index-clear -->
## sources/sync-backup/bup/test/ext/test-index-clear

Purpose: verifies `bup index --clear` removes stale index entries.

Important control flow: indexes a directory with two files, checks path output, deletes one file, clears the index, reindexes, and verifies only the remaining file, directory, and root entries are listed.

State and dependencies: temp repo index file and filesystem tree. Depends on `bup index -p/-u/--clear`.

Risks covered: stale deleted paths must not survive after an explicit clear/reindex cycle.
<!-- END_FILE_RESEARCH: sources/sync-backup/bup/test/ext/test-index-clear -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/bup/test/ext/test-index-save-type-change -->
## sources/sync-backup/bup/test/ext/test-index-save-type-change

Purpose: regression test for saving when an indexed path changes file type.

Important control flow: indexes a dead symlink, replaces it with a regular file without reindexing, then verifies `bup save` fails and the saved folder listing is empty.

State and dependencies: temp repo, filesystem path type mutation, `bup index`, `bup save`, and `bup ls`.

Risks covered: save must not trust stale index type information and accidentally archive wrong content.
<!-- END_FILE_RESEARCH: sources/sync-backup/bup/test/ext/test-index-save-type-change -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/bup/test/ext/test-init -->
## sources/sync-backup/bup/test/ext/test-init

Purpose: tests repository initialization argument precedence and remote init.

Important control flow: verifies commands fail against an uninitialized `-d` repo, initializes via `-d repo`, positional repo argument, positional overriding `-d`, positional overriding `BUP_DIR`, and `bup init --remote -:repo`. It also asserts initializing `/dev/null` fails with the generic failure code.

State and dependencies: creates/removes temp repos and inspects `refs/heads` and `objects/pack`.

Risks covered: init destination precedence, environment interaction, remote URL handling, and failure on invalid repo path.
<!-- END_FILE_RESEARCH: sources/sync-backup/bup/test/ext/test-init -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/bup/test/ext/test-install -->
## sources/sync-backup/bup/test/ext/test-install

Purpose: smoke test for install layout and installed command execution.

Important control flow: ensures the working `bup` is a symlink and `lib/cmd/bup.c` exists, unsets `GIT_DIR`, runs `dev/make PREFIX=... install`, prepends installed `bin` to PATH, checks `bup version`, optionally checks installed help if pandoc is available, and initializes an installed repo.

State and dependencies: writes an installation tree under a temp directory. Depends on make/install rules, native launcher, documentation generation, and PATH lookup.

Risks covered: install-time library discovery, launcher `PYTHONPATH` setup, installed command availability, and docs integration.
<!-- END_FILE_RESEARCH: sources/sync-backup/bup/test/ext/test-install -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/bup/test/ext/test-list-idx -->
## sources/sync-backup/bup/test/ext/test-list-idx

Purpose: tests `bup list-idx` for listing and finding object hashes in pack indexes.

Important control flow: initializes a repo, saves random data, runs `bup list-idx` on generated `.idx` files, extracts a hash from output, then runs `list-idx --find HASH` and verifies the found hash matches and exactly one output line is produced.

State and dependencies: temp repo pack/index files created by `bup save`. Depends on `bup random`, `index`, `save`, and `list-idx`.

Risks covered: pack index parsing and exact-match lookup behavior.
<!-- END_FILE_RESEARCH: sources/sync-backup/bup/test/ext/test-list-idx -->
