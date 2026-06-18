# subset-b-009113 research

Grouped research report for bup integration tests and test support files under `sources/sync-backup/bup/test`. Each section preserves the source path and is wrapped for reconciliation into source-tree-aligned per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/bup/test/int/test_helpers.py -->
# sources/sync-backup/bup/test/int/test_helpers.py

Purpose: integration-style unit coverage for `bup.helpers` path, parsing, process-cleanup, atomic-write, timezone, shell-string, and save-name helpers. It verifies both pure utility behavior and filesystem/process side effects that bup commands depend on.

Important APIs/types/functions: imports `parse_num`, `detect_fakeroot`, `path_components`, `stripped_path_components`, `grafted_path_components`, `shstr`, `finalized`, `stopped`, `partition`, `atomically_replaced_file`, `utc_offset_str`, and `helpers.valid_save_name`. It also defines `set_tz()` to mutate `bup.compat.environ[b'TZ']` and call `tzset()`.

Control flow: tests are independent pytest functions. Numeric parsing covers bytes/str, decimal and exponential units, and negative values. Path tests validate absolute-only behavior, strip roots, and graft mapping. `test_stopped()` launches `true`, ordinary `sleep`, and a SIGTERM-ignoring child, then exercises normal exit, exception exit, SIGTERM, and SIGKILL escalation. Atomic replacement writes a target, verifies rollback on exception, and checks text/binary modes with both sync settings.

State and persistence behavior: mutates subprocess state, local temporary files, and process environment. `test_utc_offset_str()` restores the original `TZ`; `atomically_replaced_file()` must leave the previous target content intact on failure. The process tests assert real signal-derived return codes.

Dependencies/integration points: uses `Popen`, POSIX signals, `tzset`, pytest parametrization, `wvpytest` aliases, `bup.compat.environ`, and helper internals. It validates helpers used by bup command-line execution, archive path construction, cleanup contexts, and Git save-name safety.

Risks and test signals: signal tests are timing/platform sensitive and assume `sleep` is available. Timezone tests depend on libc TZ parsing. The strongest signals are exact result lists for path helpers, expected process termination codes, preserved file contents after failed atomic replacement, and rejection of Git-unsafe save names.
<!-- END_FILE_RESEARCH: sources/sync-backup/bup/test/int/test_helpers.py -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/bup/test/int/test_index.py -->
# sources/sync-backup/bup/test/int/test_index.py

Purpose: exercises bup index creation, index metadata storage, merge ordering, dirty/valid flags, parent resolution, and support for negative filesystem timestamps.

Important APIs/types/functions: `index.MetaStoreWriter`, `index.Writer`, `index.BlankNewEntry`, `index.merge`, `metadata.empty_metadata`, `xstat.stat`, `resolve_parent`, local helpers `dump()`, `fake_validate()`, and `eget()`.

Control flow: `test_index_basic()` checks `resolve_parent()` versus `realpath()` for sample data and symlinks. `test_index_writer()` writes several file and directory entries to a temporary index. `test_index_negative_timestamps()` creates a file, assigns pre-epoch timestamps, updates a blank entry from stat data, and asserts it packs. `test_index_dirty()` creates three partial indexes, reads them before close, compares reader ordering, merges them, validates selected entries, and checks invalidation propagation to ancestors.

State and persistence behavior: creates temporary index and metadata files, changes CWD, stores metadata offsets, and mutates packed index entry validity flags. It intentionally works with not-yet-closed writers through `new_reader()` to validate live index state.

Dependencies/integration points: integrates filesystem stat wrappers, bup index binary serialization, metadata offset storage, merge conflict rules, fake SHA validation, and path parent resolution used by indexing commands.

Risks and test signals: relies on old negative timestamp support in the host filesystem. Merge order and invalidation expectations are exact byte-path lists. Failures reveal broken path sorting, metadata offset handling, dirty-entry propagation, or inability to serialize pre-1970 timestamps.
<!-- END_FILE_RESEARCH: sources/sync-backup/bup/test/int/test_index.py -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/bup/test/int/test_io.py -->
# sources/sync-backup/bup/test/int/test_io.py

Purpose: validates quoting/escaping helpers in `bup.io` for shell-safe bytes/strings, display of command messages, and SQL identifier/string quoting.

Important APIs/types/functions: `enc_dsq`, `enc_dsqs`, `enc_sh`, `enc_shs`, `cmd_msg`, `qsql_id`, and `qsql_str`. `_dsq_enc_byte()` is a local oracle for ANSI-C `$'...'` byte escaping.

Control flow: byte quoting loops through byte values 1..255 and string quoting loops through ASCII 1..127, testing standalone, prefix, suffix, and infix positions. Shell quoting tests distinguish empty strings, control bytes, single quotes, NUL, DEL, shell metacharacters, printable Unicode, and surrogate-escaped undecodable bytes. SQL tests assert doubled quote behavior for identifiers and string literals.

State and persistence behavior: pure functional tests with no persistent state. The only state is local in-memory byte/string construction.

Dependencies/integration points: integrates with bup's command logging and shell rendering logic, especially code paths that must safely display arbitrary bytes from filesystem paths or subprocess arguments. SQL quoting supports SQLite-facing call sites.

Risks and test signals: exhaustive byte coverage catches regressions in escaping tables. Test expectations encode bash-style ANSI-C quoting and may need review if bup deliberately changes shell dialect support. Failures are exact quoted-string mismatches.
<!-- END_FILE_RESEARCH: sources/sync-backup/bup/test/int/test_io.py -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/bup/test/int/test_metadata.py -->
# sources/sync-backup/bup/test/int/test_metadata.py

Purpose: tests metadata path sanitization, archive/extract safety checks, metadata capture from saved archives, restricted-access error recording, restore-over-existing behavior, Linux xattr cleanup, and maximal metadata hashing.

Important APIs/types/functions: `metadata._clean_up_path_for_archive`, `_risky_path`, `_clean_up_extract_path`, `metadata.from_path`, `Metadata.apply_to_path`, `Metadata.create_path`, `metadata.xattr`, `helpers.clear_errors`, `detect_fakeroot`, `is_superuser`, `LocalRepo`, `vfs.resolve`, `vfs.contents`, `setup_testfs()`, and `cleanup_testfs()`.

Control flow: path tests enumerate absolute, relative, dot, parent, slash, and empty cases. `test_metadata_method()` creates a directory with a file and symlink, sets nanosecond mtimes, runs `bup init/index/save`, opens the repository, resolves the saved path, and validates metadata for the directory, file, and symlink. Restricted-access tests chmod paths to `000` and assert saved error prefixes. Restore tests alternate directory/file metadata over existing file, directory, and non-empty directory targets. Linux-only tests mount a loop ext filesystem with ACL/xattr support and verify xattr replacement and hashability with optional `attr`, `setfacl`, and `chattr`.

State and persistence behavior: creates bup repositories, files, symlinks, loopback filesystem images, mount points, xattrs, ACLs, Linux attributes, and saved error global state. It deliberately mutates permissions and relies on cleanup/finally blocks to clear errors and unmount/remove test images.

Dependencies/integration points: depends on Linux mount tools for privileged tests, bup CLI commands, Git repository checks, VFS resolution, metadata serialization, xstat timestamp wrappers, and optional xattr/ACL/attr tools.

Risks and test signals: several tests skip under superuser, fakeroot, Cygwin, non-Linux, or missing mount support. The risk surface is high because metadata restore can overwrite filesystem objects; tests isolate in `tmpdir` and a hidden `testfs`. Signals include exact sanitized path outputs, expected error counts/prefixes, preserved symlink metadata, and correct xattr replacement.
<!-- END_FILE_RESEARCH: sources/sync-backup/bup/test/int/test_metadata.py -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/bup/test/int/test_midx.py -->
# sources/sync-backup/bup/test/int/test_midx.py

Purpose: verifies that `bup midx --check -a` tolerates a missing `.idx` file when a generated `.midx` still covers pack indexes.

Important APIs/types/functions: local wrappers `runc()` and `bupc()`, `bup.path.exe()`, `glob`, `unlink`, and the bup commands `init`, `index`, `save`, and `midx`.

Control flow: initializes a temporary bup repository, saves two sampledata subsets to create multiple pack indexes, forces midx generation, asserts one `.midx` exists and more than one `.idx` exists, deletes one `.idx`, then reruns `midx --check -a`.

State and persistence behavior: writes a real bup repository under `tmpdir`, mutates `GIT_DIR`/`BUP_DIR` in `os.environb`, creates pack index and midx files, and removes one pack index file to simulate partial index loss.

Dependencies/integration points: exercises bup CLI integration with Git pack/index layout and the multi-index verifier. It depends on bundled `test/sampledata` paths and the repository executable returned by `bup.path.exe()`.

Risks and test signals: assumes enough sample data to produce multiple `.idx` files. The only explicit signal after deletion is successful completion of `midx --check -a`; a failure would indicate the checker cannot fall back to the midx or mishandles missing per-pack indexes.
<!-- END_FILE_RESEARCH: sources/sync-backup/bup/test/int/test_midx.py -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/bup/test/int/test_options.py -->
# sources/sync-backup/bup/test/int/test_options.py

Purpose: covers bup's custom option parser, option dictionary aliases, negated options, defaults parsed from optspec text, short option clustering, long options, and numeric compression aliases.

Important APIs/types/functions: `options.OptDict`, `options.Options`, invalid optspec fixtures, and the multiline `optspec` containing aliases such as `q,quiet`, `s,smart,no-stupid`, `#,compress=`, and default annotations.

Control flow: `test_optdict()` builds an alias map, writes values through canonical and negated keys, and checks attribute access. `test_invalid_optspec()` ensures empty/minimal/malformed optspecs do not crash parsing. `test_options()` parses two argument vectors and validates flag history, extra arguments, occurrence counts, typed parameter conversion, long-only toggles, negated aliases, default values, and `#` compression option mapping.

State and persistence behavior: pure parser tests with no external state.

Dependencies/integration points: targets the parser used by bup command-line tools. The flags list is an integration contract for callers that need both parsed state and original flag order.

Risks and test signals: optspec text parsing is brittle because behavior is inferred from whitespace and bracketed defaults. Exact assertions detect regressions in alias normalization, negation semantics, numeric conversion, and leftover argument handling.
<!-- END_FILE_RESEARCH: sources/sync-backup/bup/test/int/test_options.py -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/bup/test/int/test_protocol.py -->
# sources/sync-backup/bup/test/int/test_protocol.py

Purpose: round-trip test for protocol serialization of VFS item records.

Important APIs/types/functions: `BytesIO`, `vfs.Root`, `protocol.write_item`, and `protocol.read_item`.

Control flow: constructs a `vfs.Root(meta=13)`, writes it to an in-memory byte stream, logs the raw stream for debugging, rewinds, and asserts the deserialized item equals the original.

State and persistence behavior: no persistent state; only stream position and bytes in memory.

Dependencies/integration points: covers the transport encoding used when repository/VFS objects cross protocol boundaries. It depends on VFS namedtuple equality and the protocol's type tagging for item subclasses.

Risks and test signals: narrow coverage exercises only a `Root` item with integer metadata. The signal is exact object equality after serialization and deserialization.
<!-- END_FILE_RESEARCH: sources/sync-backup/bup/test/int/test_protocol.py -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/bup/test/int/test_repo.py -->
# sources/sync-backup/bup/test/int/test_repo.py

Purpose: tests repository location normalization for local, remote, and reverse-server modes.

Important APIs/types/functions: `bup.client.Config`, `main_repo_location`, `repo_location_url`, `bup.url.URL`, `os.environb`, `fsencode`, and `devnull`.

Control flow: `test_repo_location_url()` verifies URL passthrough for a URL directly and for a `Config` containing a URL. `test_main_repo_location()` defines helper constructors, temporarily mutates `BUP_SERVER_REVERSE`, and checks default local repository, `host:path` SSH config parsing, invalid remote handling via injected `die`, and reverse server URL construction.

State and persistence behavior: temporarily changes `BUP_SERVER_REVERSE` and restores or removes it in a `finally` block. No repository is created.

Dependencies/integration points: integrates repo-location parsing with URL representation, client configuration, test harness default `GIT_DIR`/`BUP_DIR` behavior from `conftest.py`, and reverse-server environment semantics.

Risks and test signals: environment leakage would affect later tests, so restoration is critical. Signals are structural equality of `URL`/`Config` objects and an expected exception for malformed remote strings.
<!-- END_FILE_RESEARCH: sources/sync-backup/bup/test/int/test_repo.py -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/bup/test/int/test_resolve.py -->
# sources/sync-backup/bup/test/int/test_resolve.py

Purpose: comprehensive integration coverage for repository path resolution through local and file-remote repository implementations, including root normalization, branch/revlist contents, tags, latest links, symlink following, bad symlinks, ENOTDIR paths, relative parent resolution, directory symlinks, and symlink loops.

Important APIs/types/functions: `prep_and_test_repo()`, `_test_resolve()`, `_test_resolve_loop()`, `LocalRepo`, `repo_for_url`, `URL`, `repo.resolve`, `vfs.clear_cache`, `vfs.contents`, `vfs.IOError`, `vfs.RevList`, `vfs.Commit`, `vfs.FakeLink`, `vfs.Item`, `tree_dict`, `exc`, `exo`, and bup CLI commands `init`, `index`, `save`, `tag`.

Control flow: setup creates a source tree with a file, directory, file symlink, directory symlink, and bad symlink, saves it with a fixed timestamp, and tags the branch. The test reads Git object IDs, builds expected VFS items from independent tree parsing, clears the VFS cache before each case, then resolves many normalized paths. It validates root, `.tag`, branch, latest save, file, bad symlink with and without following, file symlink with and without following, missing leaves, file-as-directory ENOTDIR cases, relative lookup with a file parent, and directory symlink trailing-slash behavior. Separate tests run the same body for `LocalRepo` and `repo_for_url(file://...)`; loop tests expect ELOOP for a self-referential symlink.

State and persistence behavior: creates real repositories under `tmpdir`, mutates `GIT_DIR`/`BUP_DIR` and `git.repodir`, writes Git refs, tags, trees, symlinks, and cached VFS entries. Cache clearing is part of the tested state because metadata may be promoted after traversal.

Dependencies/integration points: ties together CLI save/index, Git ref inspection, VFS tree/materialized metadata semantics, local and remote repository adapters, URL-based repository selection, and independent `buptest.vfs.tree_dict` validation.

Risks and test signals: expected tuples are sensitive to cache metadata promotion and exact save timestamp formatting. Tests assume symlink support. Signals include exact resolution terminus lists, errno values for ENOTDIR/ELOOP, and matching contents for root, branch, tag, and latest directories.
<!-- END_FILE_RESEARCH: sources/sync-backup/bup/test/int/test_resolve.py -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/bup/test/int/test_shquote.py -->
# sources/sync-backup/bup/test/int/test_shquote.py

Purpose: validates shell-like byte command-line splitting and completion quoting helpers in `bup.shquote`.

Important APIs/types/functions: `shquote.quotesplit`, `shquote.unfinished_word`, `shquote.what_to_add`, `shquote.quotify_list`, and local `qst()` to strip offsets.

Control flow: tests split whitespace, backslash-escaped quotes, single/double quotes, unfinished quotes, and adjacent quoted/unquoted segments. Completion tests derive the unfinished word and quote type, then ask what suffix to add for unquoted, single-quoted, double-quoted, and escaped words. Final assertion checks list quoting for empty strings, embedded quotes, lone quote, and spaces.

State and persistence behavior: pure byte-string parsing with no external state.

Dependencies/integration points: supports bup shell completion and user-facing command rendering. It overlaps with but is distinct from `bup.io` shell escaping because it parses/edit-completes partially typed command lines.

Risks and test signals: behavior is exact and shell-dialect-specific. Signals are offset-preserving split tuples, unfinished quote markers, completion suffixes including closing quotes when requested, and a canonical quoted list.
<!-- END_FILE_RESEARCH: sources/sync-backup/bup/test/int/test_shquote.py -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/bup/test/int/test_treesplit.py -->
# sources/sync-backup/bup/test/int/test_treesplit.py

Purpose: regression/integration coverage for split-tree naming and depth decisions when bup stores directories with many entries under `bup.split.trees=1`.

Important APIs/types/functions: `tree._abbreviate_tree_names`, `split_tree_for_filenames()`, `pruned_ls_files()`, `diff_split()`, `git.init_repo`, `mkdirp`, bup CLI `index` and `save`, and Git `ls-tree -r --name-only`.

Control flow: `test_abbreviate()` checks shortest unique abbreviations for ordinary names, `.bupm`, strange names, and a single entry. Large fixtures `split_src`, `split_1`, and `split_2` encode deterministic source filenames and expected split-tree layouts. `split_tree_for_filenames()` initializes a repo, enables split trees, creates files, indexes and saves them, lists the saved Git tree, then prunes paths and collapsed `.bupm` internals. Depth-1 and depth-2 tests compare actual layout to expected fixtures with unified diff output.

State and persistence behavior: creates a temporary bup repository, writes many files, sets Git config `bup.split.trees`, saves into Git objects, and reads resulting tree names. The test's persistent state is the exact split directory structure using `..1.bupd` and `..2.bupd` names plus `.bupm` metadata placement.

Dependencies/integration points: bridges bup tree-splitting logic, metadata tree entries, Git storage, command execution helpers, and filesystem filename ordering. `pruned_ls_files()` intentionally normalizes Git output to focus on the saved source subtree.

Risks and test signals: fixture lists are large and brittle but provide strong regression coverage for deterministic split boundaries. Failures produce a unified diff of expected versus actual split layout, making off-by-one depth or abbreviation changes visible.
<!-- END_FILE_RESEARCH: sources/sync-backup/bup/test/int/test_treesplit.py -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/bup/test/int/test_url.py -->
# sources/sync-backup/bup/test/int/test_url.py

Purpose: tests byte URL parsing/rendering, dot-encoded relative paths, percent escaping, host/user/port handling, IPv4/IPv6 representation, and authentication requirements.

Important APIs/types/functions: `bup.url.URL`, `render_url`, `dot_encode_path`, `parse_bytes_path_url`, `IPv4Address`, `IPv6Address`, and `pytest.raises`.

Control flow: `test_dot_encode_path()` verifies empty, relative, and absolute path encoding. `symmetric_cases` lists URL byte strings that should parse/render round-trip. `test_render_url()` checks every symmetric rendering, invalid relative path with host, escaped host/user cases, `//` path preservation, and dot-encoding when requested. `test_parse_bytes_path_url()` checks auth-required rejection of non-authority forms, invalid schemes/remotes, invalid host text, alternate serialized forms, percent-decoded user/host, SSH URLs, and all symmetric cases.

State and persistence behavior: pure parser/renderer tests with no external state.

Dependencies/integration points: feeds repository remote parsing and command-line URL handling. It integrates Python `ipaddress` objects into bup's byte-oriented URL model.

Risks and test signals: URL grammar has ambiguous forms (`x:`, `x://`, `x:/`, `x:///`) and tests encode the chosen canonical renderings. Signals are structural `URL` equality, exact rendered bytes, and expected `ValueError` or string error for invalid cases.
<!-- END_FILE_RESEARCH: sources/sync-backup/bup/test/int/test_url.py -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/bup/test/int/test_vfs.py -->
# sources/sync-backup/bup/test/int/test_vfs.py

Purpose: broad integration coverage for bup virtual filesystem behavior: default modes, cache eviction, metadata augmentation, symlink/blob size and readlink handling, file copy semantics, streaming/seeking reads, tree contents with metadata/Git ordering mismatches, duplicate save-date naming, and split-tree depth parsing.

Important APIs/types/functions: `vfs.default_*_mode`, `vfs._cache`, `vfs.cache_notice`, `vfs.clear_cache`, `vfs.resolve`, `vfs.contents`, `vfs.item_size`, `vfs.readlink`, `vfs.augment_item_meta`, `vfs.copy_item`, `vfs.fopen`, `vfs._reverse_suffix_duplicates`, `vfs._parse_tree_depth`, `LocalRepo`, `Metadata`, `write_random`, `tree_dict`, and bup CLI `init/index/save`.

Control flow: cache tests reduce max items and verify eviction. `run_augment_item_meta_tests()` resolves saved file/link items, manually thaws metadata, removes size or replaces metadata with modes, and checks augmentation behavior with and without `include_size`. `test_misc()` creates and saves a file plus symlink, inspects Git tree rows, checks readlink/item_size, resolves latest, and verifies copy independence. Read tests generate random file sizes up to 2 MiB, save them, then compare VFS streaming and seek reads against original files for random block sizes. Ordering tests create `foo` directory and `foo.` file to compare VFS contents with independently parsed trees. Duplicate-date tests save the same timestamp 11 times and assert suffix names. Tree-depth parsing accepts valid `..N.bupd` names and rejects malformed ones.

State and persistence behavior: mutates global VFS cache settings, environment variables (`GIT_DIR`, `BUP_DIR`, `TZ`), `git.repodir`, temporary repositories, Git objects, symlinks, random file contents, and timezone state. Cache cleanup in `finally` prevents cross-test contamination.

Dependencies/integration points: integrates CLI saves, Git object inspection, VFS readers, metadata records, split-tree support, random content generation from `_helpers`, and independent `buptest.vfs` tree parsing.

Risks and test signals: read tests are randomized but print seeds for reproduction. Tests assume symlink support and functioning bup CLI. Signals include exact cache dictionaries, item metadata values, byte-for-byte read comparisons, independent tree-content equality, duplicate suffix ordering, and expected parse exceptions.
<!-- END_FILE_RESEARCH: sources/sync-backup/bup/test/int/test_vfs.py -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/bup/test/int/test_vint.py -->
# sources/sync-backup/bup/test/int/test_vint.py

Purpose: validates bup variable-length integer, byte-vector, and typed pack/send/recv serialization primitives.

Important APIs/types/functions: `vint.write_vuint`, `read_vuint`, `encode_vuint`, `write_vint`, `read_vint`, `write_bvec`, `read_bvec`, `skip_bvec`, `send`, `recv`, `pack`, `unpack`, `BytesIO`, and `combinations_with_replacement`.

Control flow: helper functions encode then decode unsigned ints, signed ints, and byte vectors. Tests cover negative unsigned rejection, zero/small/huge integers, empty streams returning `None`, truncated continuation bytes raising `EOFError`, byte-vector concatenation and skipping, bad format strings and argument count errors for `send/recv`, and all pair combinations of candidate `s`, `v`, and `V` pack/unpack values.

State and persistence behavior: in-memory stream state only; stream position and bytes are the persistence model under test.

Dependencies/integration points: these primitives underpin bup protocol and on-disk/in-stream compact encodings. Tests also enforce error wording for invalid formats and EOF contexts.

Risks and test signals: huge integer values test arbitrary precision behavior. Signals are exact round-trip lists, `None` on clean EOF, `EOFError` on truncation, and `ValueError` messages for format misuse.
<!-- END_FILE_RESEARCH: sources/sync-backup/bup/test/int/test_vint.py -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/bup/test/int/test_xstat.py -->
# sources/sync-backup/bup/test/int/test_xstat.py

Purpose: tests filesystem timestamp conversion helpers in `bup.xstat`, especially negative timestamp rounding and integer type preservation.

Important APIs/types/functions: `xstat.timespec_to_nsecs`, `nsecs_to_timespec`, `nsecs_to_timeval`, and `fstime_floor_secs`.

Control flow: a single test asserts conversions between `(sec,nsec)` pairs and nanoseconds, nanoseconds to timespec, nanoseconds to timeval microseconds, and floor-to-seconds behavior for positive and negative half-second values.

State and persistence behavior: pure arithmetic tests with no filesystem mutation despite targeting filesystem timestamp formats.

Dependencies/integration points: timestamp conversion is used by metadata/index code to preserve stat times across platforms and before/after the Unix epoch.

Risks and test signals: negative timestamp handling is easy to get wrong due to floor versus truncation semantics. Signals are exact numeric equality and checks that returned tuple elements remain Python ints.
<!-- END_FILE_RESEARCH: sources/sync-backup/bup/test/int/test_xstat.py -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/bup/test/lib/__init__.py -->
# sources/sync-backup/bup/test/lib/__init__.py

Purpose: empty package marker for the bup test support library directory.

Important APIs/types/functions: no imports, exports, functions, classes, or runtime statements are defined.

Control flow: none. Importing this package performs no work.

State and persistence behavior: no state, side effects, or persistence behavior.

Dependencies/integration points: enables Python package-style imports from `test/lib` when the test harness places it on `PYTHONPATH`, including modules such as `buptest` and `wvpytest`.

Risks and test signals: behavior depends only on file presence. Any future code added here would become import-time behavior for the entire test suite and should be kept minimal.
<!-- END_FILE_RESEARCH: sources/sync-backup/bup/test/lib/__init__.py -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/bup/test/lib/btl.sh -->
# sources/sync-backup/bup/test/lib/btl.sh

Purpose: shell helper library for bup tests, focused on extracting Git tree object IDs, displaying file contents in logs, and capturing stdout/stderr while preserving wrapped command exit status.

Important APIs/types/functions: `btl-ent-oid`, `btl-display-file`, `out-to`, `err-to`, and `both-to`.

Control flow: `btl-ent-oid()` accepts either stdin or one argument, rejects other arities with status 2, trims a `git ls-tree` line at the tab, then emits the final space-delimited field as the object ID. `btl-display-file()` prints quoted delimiters around `cat` output. `out-to()` tees stdout to a file and returns the command status via `PIPESTATUS[0]`. `err-to()` uses dynamic file descriptors to tee stderr while preserving stdout and command status. `both-to()` composes `err-to` and `out-to`.

State and persistence behavior: writes capture files passed by the caller and emits diagnostic content to stdout/stderr. It intentionally supports unknown `set +e` and `pipefail` states.

Dependencies/integration points: intended for shell tests using WVPASS/WVFAIL wrappers where shell redirection around the wrapper would capture the wrong command. It relies on bash features such as `local`, `$'...'`, arrays/`PIPESTATUS`, and dynamic file descriptors.

Risks and test signals: status preservation is the critical behavior; mistakes can produce false passing tests. `err-to()` is the most delicate function because descriptor ordering determines whether stdout and stderr remain separated.
<!-- END_FILE_RESEARCH: sources/sync-backup/bup/test/lib/btl.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/bup/test/lib/buptest/__init__.py -->
# sources/sync-backup/bup/test/lib/buptest/__init__.py

Purpose: Python subprocess helper module for bup tests, providing logged command execution with consistent result objects and optional stdout capture.

Important APIs/types/functions: `logcmd`, `exc`, `exo`, `ex_res = namedtuple('SubprocResult', ('out', 'err', 'rc'))`, `subprocess.run`, `PIPE`, and `bup.io.enc_shs`.

Control flow: `logcmd()` renders bytes or str command components through shell-safe quoting and prints the command to stderr. `exc()` logs, defaults `check=True`, runs the command, mirrors captured stderr to the real stderr if present, and returns `ex_res`. `exo()` ensures `stdout=PIPE`, logs, and delegates to `exc()`.

State and persistence behavior: executes real subprocesses, writes command traces and captured stderr to stderr, and returns captured output/return-code state. No module-level mutable state is maintained.

Dependencies/integration points: used across integration tests to run bup and Git commands while keeping readable logs. It depends on byte-safe shell rendering from `bup.io`.

Risks and test signals: default `check=True` means failing subprocesses raise before returning a result unless tests pass `check=False`. `logcmd()` currently only enters its print path when `cmd` is a string, while most callers pass byte sequences; command argument type handling is part of the helper contract.
<!-- END_FILE_RESEARCH: sources/sync-backup/bup/test/lib/buptest/__init__.py -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/bup/test/lib/buptest/vfs.py -->
# sources/sync-backup/bup/test/lib/buptest/vfs.py

Purpose: independent VFS test helper that reads bup Git tree objects into dictionaries so tests can cross-check `bup.vfs` behavior without using the exact same traversal path.

Important APIs/types/functions: `TreeDictValue`, `tree_items(repo, oid)`, `tree_dict(repo, oid)`, `vfs.tree_data_and_bupm`, `vfs._FileReader`, `vfs.ordered_tree_entries`, `Metadata.read`, `BUP_CHUNKED`, `tree_entries`, and `S_ISDIR`.

Control flow: `tree_items()` fetches raw tree data and optional `.bupm` metadata object, opens a metadata reader if present, yields a synthetic `.` entry, orders Git entries in bupm-aware order, skips the `.bupm` entry itself, then yields directory entries with default or read metadata and file/symlink entries with read metadata. It closes the metadata reader in `finally`. `tree_dict()` materializes the iterator keyed by name.

State and persistence behavior: reads Git object data and metadata streams from a repo; no writes. Stream position in `.bupm` is significant because metadata records are consumed sequentially.

Dependencies/integration points: used by `test_resolve.py` and `test_vfs.py` as an oracle for saved tree contents. It intentionally shares low-level Git reading but avoids full VFS resolution to reduce common-mode test failures.

Risks and test signals: still depends on several `bup.vfs` internals, so it is not fully independent. Metadata EOF raises an explicit `EOFError` naming the entry, which is useful for detecting `.bupm` ordering or truncation bugs.
<!-- END_FILE_RESEARCH: sources/sync-backup/bup/test/lib/buptest/vfs.py -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/bup/test/lib/wvpytest.py -->
# sources/sync-backup/bup/test/lib/wvpytest.py

Purpose: compatibility shim that maps historical bup WV test macros to pytest assertions.

Important APIs/types/functions: lower-case helpers `wvpass`, `wvfail`, `wvpasseq`, `wvpassne`, `wvpasslt`, `wvpassle`, `wvpassgt`, `wvpassge`, `wvexcept`, `wvcheck`, `wvmsg`, `wvstart`, and upper-case aliases `WVPASS`, `WVFAIL`, `WVPASSEQ`, `WVPASSNE`, `WVPASSLT`, `WVPASSLE`, `WVPASSGT`, `WVPASSGE`, `WVEXCEPT`, `WVCHECK`, `WVMSG`, `WVSTART`.

Control flow: each helper wraps a direct `assert`, pytest `raises`, or `print`. Equality and pass helpers optionally accept a failure value/message. Alias assignments at the bottom preserve legacy naming used throughout the test suite.

State and persistence behavior: no persistent state. `wvmsg`/`wvstart` print to stdout.

Dependencies/integration points: imported by most bup Python tests with `from wvpytest import *`, allowing older WV-style assertions to run under pytest without rewriting every test.

Risks and test signals: semantics are simpler than a dedicated assertion framework. `wvpass(cond=True)` defaults to passing if called without arguments, and `wvfail(cond=True)` defaults to failing unless passed a false condition, matching legacy macro usage.
<!-- END_FILE_RESEARCH: sources/sync-backup/bup/test/lib/wvpytest.py -->
