<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/rsync/testsuite/sender-flist-symlink-leak_test.py -->
# sources/sync-backup/rsync/testsuite/sender-flist-symlink-leak_test.py

Purpose: Python regression test for a daemon sender file-list leak where `change_pathname()` and `change_dir()` could follow an attacker-controlled directory symlink outside a no-chroot daemon module during listing. It verifies that a pull of `rsync://daemon/module/cd/`, where `cd` points outside the module, does not enumerate outside names.

Important APIs and flow: imports `SCRATCHDIR`, `rsync_argv`, `start_test_daemon`, identity helpers, and failure/skip helpers from `rsyncfns`. It skips platforms lacking the secure resolver primitive, creates `module/`, `outside/`, a marker file, and `module/cd -> outside`, then writes a temporary `rsyncd.conf`. A positive-control dry-run recursive daemon pull of `realdir/` must list `in_module.txt`; only then does the leak probe dry-run-pull `cd/` and scan stdout/stderr for `leak_marker.txt`.

State and persistence: all state lives in scratch directories and a generated daemon config/log. The daemon port is fixed at `12881`, so concurrent runs need the harness to isolate workers or serialize daemon tests.

Dependencies and integration: exercises daemon-mode path resolution, sender flist generation, `start_test_daemon()`, and the secure `change_dir()` behavior in the C code. Risks are platform-specific skip accuracy, fixed port collision, and false confidence if the positive control is weakened. Test signal is binary: any marker listing is a metadata leak; daemon crash by signal is also failure.
<!-- END_FILE_RESEARCH: sources/sync-backup/rsync/testsuite/sender-flist-symlink-leak_test.py -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/rsync/testsuite/simd-checksum_test.py -->
# sources/sync-backup/rsync/testsuite/simd-checksum_test.py

Purpose: smoke/regression test for SIMD rolling/checksum helper implementations. It runs the built `simdtest` tool, which compares accelerated checksum code against the portable C reference.

Important APIs and flow: imports `TOOLDIR`, `test_fail`, and `test_skipped`. The script checks that `TOOLDIR/simdtest` exists and is executable, skips if the build did not produce it, and otherwise runs it with no arguments. Non-zero exit is reported as a test failure.

State and persistence: no source/destination fixture tree and no persistent state beyond process exit status. It depends entirely on the build tree layout and executable bit.

Dependencies and integration: integrates with optional rsync SIMD build features reported by `usage.c` as `SIMD-roll`/`asm-roll`. It is a narrow harness wrapper, not a checksum oracle itself. Main risks are skipped coverage on hosts where SIMD is unavailable and lack of stdout/stderr capture in the success path. Test signal is the helper’s return code.
<!-- END_FILE_RESEARCH: sources/sync-backup/rsync/testsuite/simd-checksum_test.py -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/rsync/testsuite/size-filter_test.py -->
# sources/sync-backup/rsync/testsuite/size-filter_test.py

Purpose: verifies `--max-size` and `--min-size` filtering across nested directories. The test ensures file-size filters apply consistently at each depth rather than only to top-level entries.

Important APIs and flow: imports `FROMDIR`, `TODIR`, `assert_not_exists`, `assert_same`, `make_data_file`, `rmtree`, and `run_rsync`. `seed()` rebuilds a four-level tree, placing `smallN` and `largeN` files at every level. The first pass runs `rsync -a --max-size=1000` and asserts each small file is byte-identical while each large file is absent. The second pass reseeds and runs `--min-size=1000`, asserting the inverse.

State and persistence: fixture state is fully recreated for each half, eliminating stale-output false positives. File sizes are deterministic constants (`500` and `5000` bytes).

Dependencies and integration: exercises option parsing and receiver/generator selection for per-file transfer decisions. It also indirectly covers recursive flist traversal. Risks are mostly harness-level: `assert_same` must compare content, and destination cleanup must be reliable. Test signal is precise absence/presence plus content equality at all four levels.
<!-- END_FILE_RESEARCH: sources/sync-backup/rsync/testsuite/size-filter_test.py -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/rsync/testsuite/sparse_test.py -->
# sources/sync-backup/rsync/testsuite/sparse_test.py

Purpose: validates `-S/--sparse` preservation for a sparse file several levels deep, while avoiding invalid assumptions about non-sparse copies on filesystems that auto-sparsify zero runs.

Important APIs and flow: imports tree helpers plus `assert_same`, `test_fail`, and `test_skipped`. `make_sparse()` writes `head`, seeks near 4 MiB, and writes `tail`. `allocated()` uses `st_blocks * 512`. The test skips if the source filesystem did not actually create a sparse file. With `rsync -a -S`, it asserts byte equality and allocated size below the apparent size. With `--no-sparse`, it only asserts byte equality.

State and persistence: source and destination trees are removed before each transfer; sparse behavior is inspected via filesystem metadata, not external tools.

Dependencies and integration: covers receiver file-writing choices, sparse-hole detection, and deep parent path handling. Risks include platform filesystems with unusual block accounting and sparse support; the skip protects the main premise. Test signal is content equality plus destination allocation below `SIZE` only for the sparse-enabled transfer.
<!-- END_FILE_RESEARCH: sources/sync-backup/rsync/testsuite/sparse_test.py -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/rsync/testsuite/ssh-basic_test.py -->
# sources/sync-backup/rsync/testsuite/ssh-basic_test.py

Purpose: basic remote-shell transfer coverage, using the test `lsh.sh` shim by default or real `ssh` when `rsync_enable_ssh_tests=yes`.

Important APIs and flow: imports `checkit`, `hands_setup`, `runtest`, paths, and skip helper. It probes `[SSH, -oBatchMode yes, localhost, echo, yes]`; if stdout is not exactly `yes`, the test skips. After `hands_setup()`, `_basic()` runs `checkit()` with `-avH -e SSH --rsync-path=RSYNC_PEER FROMDIR/ localhost:TODIR`. `_delete_after_rename()` renames destination `text` to `ThisShouldGo` and reruns with `--delete` to confirm remote deletion/update behavior.

State and persistence: uses the standard hands fixture tree, mutates `TODIR` between the two subtests, and relies on environment variable selection for real ssh.

Dependencies and integration: exercises remote-shell command construction, `--rsync-path`, hard-link preservation option plumbing, and delete pass behavior. Risks include localhost ssh authorization and multi-word rsync peer command quoting. Test signal comes from `checkit()` tree comparisons and `runtest()` failure propagation.
<!-- END_FILE_RESEARCH: sources/sync-backup/rsync/testsuite/ssh-basic_test.py -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/rsync/testsuite/stop-time_test.py -->
# sources/sync-backup/rsync/testsuite/stop-time_test.py

Purpose: covers `--stop-at` absolute-time parsing and `--stop-after` minute-count parsing, especially option paths that may be otherwise untested.

Important APIs and flow: builds a depth-2 data tree with `make_tree()`, records relative file paths, and computes a future timestamp one day from the current time in `%Y-%m-%dT%H:%M` format. It runs `rsync -a --stop-at=<future>` and asserts every file matches. It then runs a known-past `--stop-at=2000-01-01T00:00` with `check=False` and fails if parsing allows a successful transfer. Finally it runs `--stop-after=60` and asserts content equality.

State and persistence: destination is removed before each scenario. Time dependence is deliberate but uses a one-day future value to avoid fixed-date rot and 32-bit `time_t` overflow.

Dependencies and integration: exercises option parsing in rsync’s time handling and normal transfer continuation when limits are not reached. Risks include clock skew only inside the current process; test signal is parse rejection for past time and successful content copies for future/minute cases.
<!-- END_FILE_RESEARCH: sources/sync-backup/rsync/testsuite/stop-time_test.py -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/rsync/testsuite/symlink-dirlink-basis_test.py -->
# sources/sync-backup/rsync/testsuite/symlink-dirlink-basis_test.py

Purpose: regression coverage for updating files through in-tree directory symlinks with `-K/--copy-dirlinks` after secure path resolution changes for CVE-2026-29518. It targets issue #715, where `O_NOFOLLOW` on every component blocked legitimate directory symlinks.

Important APIs and flow: skips unless `resolve_beneath_supported()` proves the binary can securely follow in-tree dir symlinks. It sets `RSYNC_RSH` to `support/lsh.sh`, uses a scratch source base, and defines `push()` to run rsync from that base with `--rsync-path` before positional args. The eight scenarios cover basic dir-symlink initial/update, compressed update, nested symlinks, `--backup`, `--inplace`, top-level file updates, `--partial-dir` with protocol 28, and protocol 28 basic update. `make_testfile()` creates ~32 KiB files to trigger delta matching; `assert_same()` verifies content.

State and persistence: test state lives under `TMPDIR/src_files` and `SCRATCHDIR` home. Several cases unlink previous outputs and modify mtimes with `time.sleep(1)` plus `touch()` to force updates.

Dependencies and integration: exercises receiver secure opening, basis-file handling, remote shell mode, compression, backup, inplace, partial-dir, and legacy protocol behavior. Risks are resolver capability detection and remote-shell setup. Test signal is file existence through the symlink target plus byte identity and backup content correctness.
<!-- END_FILE_RESEARCH: sources/sync-backup/rsync/testsuite/symlink-dirlink-basis_test.py -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/rsync/testsuite/symlink-ignore_test.py -->
# sources/sync-backup/rsync/testsuite/symlink-ignore_test.py

Purpose: verifies default recursive copy behavior when symlink preservation or dereference options are not enabled. Without `-l`, `-L`, or `-a`, rsync should omit symlinks.

Important APIs and flow: imports symlink fixture helpers from `rsyncfns`. `build_symlinks()` creates a referent plus dangling, relative, and absolute links. The test runs `rsync -r FROMDIR/ TODIR`, asserts the referent regular file exists, checks there is no extra `from` directory level, and fails if any symlink appears in the destination.

State and persistence: relies on the shared symlink fixture and destination generated by one transfer. It performs no cleanup itself beyond what the harness fixtures provide.

Dependencies and integration: targets flist/generator symlink option handling and destination creation rules. Risks are helper behavior changes that alter fixture names. Test signal is absence of copied links and presence of the non-link referent.
<!-- END_FILE_RESEARCH: sources/sync-backup/rsync/testsuite/symlink-ignore_test.py -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/rsync/testsuite/temp-dir_test.py -->
# sources/sync-backup/rsync/testsuite/temp-dir_test.py

Purpose: covers `--temp-dir` for receiver scratch files outside the destination tree, including cross-directory rename behavior at depth and failure when the temp dir is missing.

Important APIs and flow: rebuilds `FROMDIR`, `TODIR`, and a sibling scratch temp directory, creates a depth-3 data tree, and records all relative files. It runs `rsync -a --temp-dir=<tmp> FROMDIR/ TODIR/`, asserts every destination file matches the source, asserts the temp dir is empty, and scans destination for stray dot-prefixed temp files. It then removes `TODIR` and verifies a non-existent temp dir causes a non-zero result.

State and persistence: all temp/destination state is scratch-local. The temp dir is deliberately outside both source and destination to force the path-resolution and rename boundary of interest.

Dependencies and integration: exercises temp-file creation, final rename through `robust_rename()`, and secure parent-dir operations. Risks are filesystem-specific hidden files in destination and broad `rglob('.*')` matching, but the controlled fixture limits that. Test signal is content equality, no leftovers, and expected failure for a missing temp dir.
<!-- END_FILE_RESEARCH: sources/sync-backup/rsync/testsuite/temp-dir_test.py -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/rsync/testsuite/trimslash_test.py -->
# sources/sync-backup/rsync/testsuite/trimslash_test.py

Purpose: unit-style test for the `trimslash` helper, which calls `trim_trailing_slashes()` on each argument and prints the result.

Important APIs and flow: constructs six path inputs covering no trailing slash, one/many trailing slashes, double leading slash, all slashes, and spaces/interior triple slashes. It runs `TOOLDIR/trimslash` with all inputs, fails on non-zero exit, and compares stdout exactly to the expected newline-terminated output.

State and persistence: no filesystem mutation. The only state is subprocess stdout/stderr.

Dependencies and integration: connects to `trimslash.c` and the shared path utility implementation from rsync core. Risks are platform path semantics if `trim_trailing_slashes()` intentionally treats double leading slashes differently, but the expected output documents current behavior. Test signal is exact stdout equality.
<!-- END_FILE_RESEARCH: sources/sync-backup/rsync/testsuite/trimslash_test.py -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/rsync/testsuite/unsafe-byname_test.py -->
# sources/sync-backup/rsync/testsuite/unsafe-byname_test.py

Purpose: direct behavioral test for `unsafe_symlink()` through the `t_unsafe` helper, using crafted symlink targets and current-directory paths.

Important APIs and flow: builds a table of `(link_target, curdir, expected)` cases and runs `TOOLDIR/t_unsafe target curdir` for each. Cases cover plain relative links, absolute and protocol-like double-slash paths, `..` escapes, repeated slashes, interior `dir/..` forms, empty targets, Vladimir Michl unsafe-links examples, and absolute current-directory forms based on the process CWD.

State and persistence: no fixture tree is required; the helper evaluates path strings. The test uses the current working directory exactly as the shell version did.

Dependencies and integration: targets `util1.c::unsafe_symlink()` and its path-depth model. Risks are CWD assumptions and helper output contract (`safe` or `unsafe`). Test signal is aggregated mismatch reporting after all cases, making it easier to see every rule regression in one run.
<!-- END_FILE_RESEARCH: sources/sync-backup/rsync/testsuite/unsafe-byname_test.py -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/rsync/testsuite/unsafe-links_test.py -->
# sources/sync-backup/rsync/testsuite/unsafe-links_test.py

Purpose: end-to-end symlink policy test for default archive behavior, `--copy-links`, and `--copy-unsafe-links`.

Important APIs and flow: creates `from/safe/files`, `from/safe/links`, and `from/unsafe`, with two safe relative links and one unsafe `../../unsafe/unsafefile` link. Default `rsync -avv from/safe/ to` must copy all three as symlinks. `--copy-links` must materialize all as regular files. `--copy-unsafe-links` must leave safe links as symlinks but materialize the unsafe one. The unsafe-copy scenario is repeated from a changed CWD and from an absolute source path.

State and persistence: operates under `TMPDIR`, manually removes `to` between scenarios, and uses helper assertions for symlink target and regular-file existence.

Dependencies and integration: integrates flist symlink classification, `unsafe_symlink()`, copy-link options, and relative/absolute source normalization. Risks include pre-existing `TMPDIR/from` if harness cleanup changes. Test signal distinguishes link preservation from dereferencing by both file type and symlink target text.
<!-- END_FILE_RESEARCH: sources/sync-backup/rsync/testsuite/unsafe-links_test.py -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/rsync/testsuite/update_test.py -->
# sources/sync-backup/rsync/testsuite/update_test.py

Purpose: validates `-u/--update` and `--force` decisions at depth, including a format-change case where a newer destination symlink should still be replaced by a source regular file.

Important APIs and flow: first creates a depth-3 tree, copies it, modifies a deep source file, makes the destination copy newer by mtime, and checks `rsync -a -u` preserves the destination content. It then makes destination older and expects an update. A second scenario creates source `foo` as a regular file and destination `foo` as a newer symlink; `-u` must replace the symlink. The final scenario sets source deep `f3` as a file and destination `f3` as a non-empty directory; without `--force` replacement must not happen, with `--force` it must.

State and persistence: each scenario resets `FROMDIR` and `TODIR`. Mtime manipulation uses `os.utime()`, including `follow_symlinks=False` for the symlink case.

Dependencies and integration: covers generator update decisions, file-type precedence, recursive parent handling, and forced deletion. Risks are filesystem mtime precision, mitigated by explicit offsets. Test signal is content preservation/update and file-type replacement at exact paths.
<!-- END_FILE_RESEARCH: sources/sync-backup/rsync/testsuite/update_test.py -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/rsync/testsuite/wildmatch_test.py -->
# sources/sync-backup/rsync/testsuite/wildmatch_test.py

Purpose: wrapper around the `wildtest` C helper to exercise rsync’s `wildmatch()` and `wildmatch_array()`/join behavior over the canonical `wildtest.txt` cases.

Important APIs and flow: iterates over twelve option sets, including plain matching plus combinations of `-x` explode sizes and `-e` empty-string insertion controls. For each, it runs `TOOLDIR/wildtest` with the option set and `SRCDIR/wildtest.txt`. Return code must be zero and stdout must exactly equal `No wildmatch errors found.\n`.

State and persistence: no mutable filesystem state. It depends on build output and the source test data file.

Dependencies and integration: connects to `wildtest.c` and `lib/wildmatch.c`, including array-fragment matching used by rsync filters. Risks are exact stdout coupling and helper availability. Test signal is strong because the helper validates every line and reports internal mismatch counts.
<!-- END_FILE_RESEARCH: sources/sync-backup/rsync/testsuite/wildmatch_test.py -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/rsync/testsuite/xattrs-depth_test.py -->
# sources/sync-backup/rsync/testsuite/xattrs-depth_test.py

Purpose: companion depth test for `-X` xattr preservation, ensuring xattrs on both directories and files survive through deep parent chains.

Important APIs and flow: skips when `xattrs_supported()` is false. It builds a depth-3 tree, collects relative directories and files, then sets a distinct `depth` user xattr value on every entry from inside the source directory. It captures expected xattrs with `xattr_dump()`, runs `rsync -aX -f-x_system.* -f-x_security.* --super`, then dumps destination xattrs and diffs on mismatch.

State and persistence: fixture state is recreated, and xattr values include the relative path to catch swaps. The process changes CWD to source and destination for tool-friendly relative paths.

Dependencies and integration: exercises `xattrs.c` end-to-end, xattr filters, super/fake namespace handling, and deep path operations. Risks are filesystem/xattr namespace support and privilege-dependent system/security attrs, handled by skips and filters. Test signal is exact dump equality.
<!-- END_FILE_RESEARCH: sources/sync-backup/rsync/testsuite/xattrs-depth_test.py -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/rsync/testsuite/xattrs_test.py -->
# sources/sync-backup/rsync/testsuite/xattrs_test.py

Purpose: comprehensive xattr transfer test, also serving as the hard-link xattr variant when invoked through a name containing `hlink`.

Important APIs and flow: skips without xattr support, builds source/check/link/destination trees, parses `tls` output to discover uid/gid for fake-super `%stat`, and seeds many file/dir xattrs including short, long, equal, changed, extra, and rsync-prefixed values. It snapshots expected xattrs with `xattr_dump()`. It verifies simple `-avX --super`, then `--copy-dest` or `--link-dest` with optional `-H`, then `--fake-super --link-dest`, then no-user-permission fake-super/chmod handling. The tail tests xattr behavior across local copies, delete/update, alternate destination, and final update rounds. The hlink variant additionally verifies inode link counts using `rsync_ls_lR`.

State and persistence: heavily mutates `FROMDIR`, `CHKDIR`, `TODIR`, and `lnkdir`, repeatedly changing CWD and removing trees. Expected xattr snapshots are stored in `SCRATCHDIR/xattrs.txt`.

Dependencies and integration: exercises almost every major path in `xattrs.c`: collection, filtering, interning, long-value checksums, request/response, setting/removal, fake-super stat xattrs, alt-dest, hard links, and permission workarounds. Risks include platform xattr namespaces, permission model differences, hard-link capability, and exact dump ordering. Test signal is repeated exact dump equality plus hard-link sanity.
<!-- END_FILE_RESEARCH: sources/sync-backup/rsync/testsuite/xattrs_test.py -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/rsync/tls.c -->
# sources/sync-backup/rsync/tls.c

Purpose: `tls` is a deterministic test-listing utility used by the rsync tests instead of platform `ls`, avoiding OS-specific output and symlink metadata quirks.

Important APIs/types/functions: defines stub globals required by shared syscall code. `stat_xattr()` optionally overlays fake-super stat data from `user.rsync.%stat`/`rsync.%stat`. `storetime()` formats UTC timestamps or fixed-width blanks. `list_file()` performs `do_lstat()`, optional create-time/fake-super handling, symlink target reading, permission formatting, size/device formatting, and output. `tls_usage()` and `main()` use popt for `--atimes`, `--crtimes`, `--link-times`, `--link-owner`, `--fake-super`, `--nsec`, and help.

Control flow and state: process-global flags control displayed metadata. Each command-line file is listed independently; the tool does not recurse or read directories. Symlink mode bits, owner, and mtime are masked unless options request them for reproducibility.

Dependencies and integration: depends on rsync wrappers (`do_lstat`, `do_readlink`, `permstring`, `do_big_num`), popt, xattr helpers, and optional create-time support. Tests use it for stable comparisons and uid/gid parsing in xattr fake-super tests. Risks include fixed 4096 symlink target buffer truncation for extreme links, fake-super parse hard failure on corrupt xattrs, and platform conditional output differences. Test signals come from many tests that compare `tls` output or parse its columns.
<!-- END_FILE_RESEARCH: sources/sync-backup/rsync/tls.c -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/rsync/token.c -->
# sources/sync-backup/rsync/token.c

Purpose: transfer-token stream implementation for rsync’s delta algorithm. It sends and receives literal data runs and matching-block token references, optionally compressed with zlib, zstd, or lz4.

Important APIs/types/functions: public entry points are `init_compression_level()`, `set_compression()`, `send_token()`, `recv_token()`, and `see_token()`. Internal suffix-tree functions parse skip-compress suffixes. Simple mode uses `simple_send_token()`/`simple_recv_token()`. Zlib mode uses token-run encodings (`TOKEN_REL`, `TOKENRUN_REL`, long forms), `send_deflated_token()`, `recv_deflated_token()`, and `see_deflate_token()` to keep compressor/decompressor histories aligned. Optional zstd and lz4 paths implement equivalent framed chunks using the same outer token flag format.

Control flow and state: compression uses static stream state across calls and resets when `last_token == -1` or receiver state returns to `r_init`. Literal runs are chunked to `CHUNK_SIZE`; compressed data records fit `MAX_DATA_COUNT`. Token runs compress consecutive token IDs into relative or long encodings. `recv_state`, `rx_token`, and `rx_run` model the receive-side state machine.

Dependencies and integration: depends on rsync I/O primitives, `map_ptr()`, negotiated `do_compression`, protocol version, daemon skip-compress config, zlib, and optional zstd/lz4. Risks include protocol desynchronization, integer overflows in token/run arithmetic, compressor flush edge cases, and static state reuse across files. The code includes hardening for oversized simple literal runs, zlib insert-only overflow/drain behavior, and invalid compressed token bounds. Test signals include transfer tests with compression, `symlink-dirlink-basis_test.py` compressed update, checksum/data integrity tests, and interoperability with older protocols.
<!-- END_FILE_RESEARCH: sources/sync-backup/rsync/token.c -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/rsync/trimslash.c -->
# sources/sync-backup/rsync/trimslash.c

Purpose: tiny test harness utility for `trim_trailing_slashes()`. It exists only to expose the shared path function as an executable for tests.

Important APIs and flow: defines stub globals required by `syscall.o`, checks at least one argument, then mutates each `argv[i]` in place with `trim_trailing_slashes()` and prints the result. Return code is `1` for missing args and `0` after processing.

State and persistence: no persistent state and no filesystem access. It writes normalized paths to stdout.

Dependencies and integration: includes `rsync.h` and links shared utility/syscall code. It is exercised by `trimslash_test.py`. Risks are minimal; because it edits argv memory directly, it assumes command-line argument storage is mutable on supported platforms, which is conventional for C programs but still a portability assumption. Test signal is exact stdout matching over edge-case slash inputs.
<!-- END_FILE_RESEARCH: sources/sync-backup/rsync/trimslash.c -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/rsync/uidlist.c -->
# sources/sync-backup/rsync/uidlist.c

Purpose: maps user/group IDs and names between sender and receiver, including explicit `--usermap`/`--groupmap`, numeric-id handling, ACL integration, and non-root group-skip behavior.

Important APIs/types/functions: `struct idlist` stores original ID/name/range/match flags and mapped ID. `uid_to_user()`, `gid_to_group()`, `user_to_uid()`, and `group_to_gid()` wrap system databases or `namecvt_call()`. `add_uid()`/`add_gid()` collect sender-side IDs; `send_id_lists()` serializes mappings; `recv_user_name()`, `recv_group_name()`, and `recv_id_list()` receive and apply mappings to flist entries. `parse_name_map()` parses number ranges, exact names, and wildcard names. `match_uid()`/`match_gid()` lazily map IDs and cache the last lookup. `getallgroups()` populates supplemental groups when available.

Control flow and state: four linked lists track transmitted uid/gid lists and configured maps. Sender transmits non-zero IDs plus optional ID-0 names. Receiver reads lists when preserving uid/gid/acls and `numeric_ids <= 0`, resolves names locally unless numeric mode suppresses names, then rewrites flist owner/group fields. Non-root receivers mark disallowed groups with `FLAG_SKIP_GROUP`.

Dependencies and integration: depends on passwd/group APIs, rsync varint I/O, wildcard matching, ACL ID matching, global option state, and name-converter subprocess support. Risks include syntax errors in map parsing, ID overflow detection in `id_parse()`, linked-list lookup cost for very large ID sets, and platform group-list quirks. Test signals are ownership-preservation, ACL, fake-super, and daemon tests rather than a single dedicated unit in this subset.
<!-- END_FILE_RESEARCH: sources/sync-backup/rsync/uidlist.c -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/rsync/usage.c -->
# sources/sync-backup/rsync/usage.c

Purpose: central version, capability, algorithm-list, and usage/help output for normal and daemon rsync modes.

Important APIs/functions: `print_info_flags()` emits capabilities/optimizations as human text or JSON. `output_nno_list()` prints checksum/compression/auth algorithm lists. `print_rsync_version()` emits program/version/protocol/copyright/url/capabilities/lists/license/warranty, using JSON when passed `FNONE`. `usage()` prints command forms and includes generated `help-rsync.h`; `daemon_usage()` includes `help-rsyncd.h`. `rsync_version()` selects `RSYNC_GITVER` or `RSYNC_VERSION` and strips a leading `v`; `default_cvsignore()` returns the generated ignore pattern string.

Control flow and state: most behavior is compile-time conditional. JSON generation reuses the same capability table but converts labels into keys and booleans/bit counts. `istring()` dynamically formats bit widths; several generated strings are intentionally process-lifetime allocations.

Dependencies and integration: depends on version headers, generated help/default-ignore headers, checksum/compression registries, and `rprintf()`. Risks include JSON formatting drift, capability labels not matching compile-time behavior, and generated header availability. Test signals include `--version`, `--version --json`, help-output smoke tests, and build-feature wrappers such as the SIMD checksum test.
<!-- END_FILE_RESEARCH: sources/sync-backup/rsync/usage.c -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/rsync/util1.c -->
# sources/sync-backup/rsync/util1.c

Purpose: broad utility layer for rsync process/file/path operations. In this snapshot it is especially important for secure no-chroot daemon path handling, partial-dir/temp-dir operations, unsafe symlink classification, glob expansion, and reusable containers.

Important APIs/functions: descriptor helpers `set_nonblocking()`, `set_blocking()`, `fd_pair()`; metadata/file helpers `set_times()`, `make_path()`, `full_write()`, `copy_file()`, `robust_unlink()`, `robust_rename()`; process helpers `do_fork()`, `kill_all()`, `lock_range()`; glob/path helpers `glob_expand()`, `glob_expand_module()`, `clean_fname()`, `sanitize_path()`, `change_dir()`, `normalize_path()`, `full_fname()`, `partial_dir_fname()`, `handle_partial_dir()`; symlink/time/fuzzy/list helpers `unsafe_symlink()`, `timestring()`, `same_time()`, `find_filename_suffix()`, `fuzzy_distance()`, `bitbag_*`, `flist_ndx_*`, `expand_item_list()`, and `force_memzero()`.

Control flow and state: maintains `curr_dir`, `curr_dir_len`, `curr_dir_depth`, `sanitize_paths`, static partial-dir buffer, static child PID list, and static glob buffers. `change_dir()` initializes from `getcwd()`, updates logical CWD, and in daemon/no-chroot mode uses `secure_relative_open()` plus `fchdir()` to avoid parent symlink escapes, including the `skipped_chdir` prefix case. `copy_file()` uses secure relative open for daemon relative sources and secure `do_open_at()` for recreating destinations.

Dependencies and integration: heavily used by generator/receiver/sender, syscall wrappers, filters, xattrs, daemon module code, and tests in this batch (`temp-dir`, `update`, `unsafe-*`, symlink leak, symlink dirlink basis). Risks are high because many functions mutate input buffers and global state, static buffers are not thread-safe, path cleanup semantics are subtle, and security depends on correct at-wrapper use. Test signals include deep option tests, symlink safety helpers, partial/temp-dir tests, and no-chroot daemon leak regression.
<!-- END_FILE_RESEARCH: sources/sync-backup/rsync/util1.c -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/rsync/util2.c -->
# sources/sync-backup/rsync/util2.c

Purpose: smaller utility layer for sleeping, allocation wrappers, checksum formatting, diagnostics, and source-file path shortening.

Important APIs/functions: `msleep()` sleeps milliseconds via `nanosleep`, `usleep`, or `select` fallback. `my_alloc()` backs rsync allocation macros, enforces `--max-alloc`, and supports malloc/calloc/realloc using the sentinel `do_calloc`. `sum_as_hex()` returns canonical digest bytes as hex, reversing order when requested by `canonical_checksum()`. `_out_of_memory()` and `_overflow_exit()` print contextual fatal errors and exit cleanup. `src_file()` strips the source directory prefix from file paths in diagnostics.

Control flow and state: uses global `max_alloc`, static source-prefix cache, and a static hex buffer. Allocation failures either return NULL for nonfatal callers or exit for checked macros.

Dependencies and integration: depends on rsync checksum metadata, logging, cleanup, and memory macros. Risks include static-buffer overwrite in nested `sum_as_hex()` use, integer guard dependence on non-zero `size`, and platform sleep precision. Test signals are broad: allocation overflow paths, diagnostics, and checksum display are exercised indirectly by many rsync modes.
<!-- END_FILE_RESEARCH: sources/sync-backup/rsync/util2.c -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/rsync/version.h -->
# sources/sync-backup/rsync/version.h

Purpose: build-time version constants for rsync.

Important declarations: `RSYNC_VERSION` is `"3.5.0dev"`. `MAINTAINER_TZ_OFFSET` is `10.0`, used by maintainer/build tooling that needs the maintainer timezone offset.

Control flow and state: no code or persistence. The header is consumed by `usage.c`, where `rsync_version()` may prefer `RSYNC_GITVER` and strips a leading `v`.

Dependencies and integration: included in version/help output and any generated release metadata. Risks are simple but user-visible: stale or malformed version strings affect protocol/support reporting and test expectations around `--version`. Test signals are version-output checks and build packaging validation.
<!-- END_FILE_RESEARCH: sources/sync-backup/rsync/version.h -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/rsync/wildtest.c -->
# sources/sync-backup/rsync/wildtest.c

Purpose: standalone test driver for rsync’s wildmatch implementation. It includes `lib/wildmatch.c` directly so the helper can exercise internal iteration counters and array matching.

Important APIs/functions: options are parsed with popt: `--iterations/-i`, `--empties/-e`, and `--explode/-x`. `run_test()` either calls `wildmatch(pattern, text)` or splits text into chunks/empty elements and calls `wildmatch_array()`. Optional `COMPARE_WITH_FNMATCH` can compare against libc `fnmatch()`. `main()` parses a test file where each non-comment line has two flags and two strings, handles quoting, and reports total wildmatch errors.

Control flow and state: global knobs control chunk size and inserted empty array elements. The parser is line-oriented and exits on syntax errors. Return status is zero even when mismatches are reported; wrappers check stdout.

Dependencies and integration: used by `wildmatch_test.py` with `wildtest.txt`. It depends on popt and rsync wildmatch code. Risks include fixed 2048-byte line buffer, direct inclusion of implementation, and stdout contract coupling. Test signal is the exact `No wildmatch errors found.` output across option sets.
<!-- END_FILE_RESEARCH: sources/sync-backup/rsync/wildtest.c -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/rsync/xattrs.c -->
# sources/sync-backup/rsync/xattrs.c

Purpose: extended attribute support for rsync, including xattr discovery, filtering, wire encoding, deduplicated list storage, long-value abbreviation/request protocol, destination setting/removal, ACL xattr shims, and fake-super stat metadata.

Important APIs/types/functions: `rsync_xa` stores datum/name lengths and item number; `rsync_xa_list` interns a sorted xattr item list; global `rsync_xal_l` and `rsync_xal_h` deduplicate lists. Collection uses `get_xattr_names()`, `get_xattr_data()`, `rsync_xal_get()`, and `get_xattr()`. Wire/list operations use `send_xattr()`, `receive_xattr()`, `xattr_diff()`, `send_xattr_request()`, and `recv_xattr_request()`. Destination operations use `set_xattr()` and `rsync_xal_set()`. Fake-super helpers are `get_stat_xattr()`, `set_stat_xattr()`, `x_stat()`, `x_lstat()`, and `x_fstat()`. ACL helpers expose `get_xattr_acl()`, `set_xattr_acl()`, and `del_def_xattr_acl()`.

Control flow and state: name buffers are reused globally. Collection filters xattrs according to xattr filters, Linux namespace rules, root/non-root mode, and `-X` count. Large datums are represented by `XSTATE_ABBREV` plus checksum, then requested lazily if receiver-side comparison needs full data. Received xattr lists can reference a prior interned index or transmit a literal list. Setting applies wanted values, resolves abbreviated values from `fnamecmp` when possible, and removes extraneous names.

Dependencies and integration: depends on `lib/sysxattrs`, filter rules, checksum registry, file-list `F_XATTR`, fake-super owner/mode fields, ACL support, and secure `*_at` stat wrappers. Risks include namespace portability, long-datum checksum collision risk bounded by digest choice, global/static non-thread-safe state, memory ownership subtleties when interning, and protocol hardening around counts/lengths/relative xattr requests. Test signals are strong in this subset: `xattrs_test.py` covers shallow, alt-dest, fake-super, and hlink paths; `xattrs-depth_test.py` covers deep parent chains.
<!-- END_FILE_RESEARCH: sources/sync-backup/rsync/xattrs.c -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/rsync/zlib/adler32.c -->
# sources/sync-backup/rsync/zlib/adler32.c

Purpose: bundled zlib Adler-32 checksum implementation and checksum-combine helpers.

Important APIs/functions: exports `adler32()`, `adler32_combine()`, and `adler32_combine64()`. Internal `adler32_combine_()` implements concatenation math for two Adler checksums and a second stream length. Macros `DO1` through `DO16` unroll byte accumulation; `MOD`, `MOD28`, and `MOD63` perform modulo reduction with optional no-division arithmetic.

Control flow and state: `adler32()` handles `buf == Z_NULL` by returning the initial checksum, has a fast single-byte path, a short-buffer path, and a block loop over `NMAX` chunks to avoid 32-bit overflow before modulo. No persistent state is used.

Dependencies and integration: included by bundled zlib and used where rsync links that zlib for compression/checksum support. Risks are mostly upstream zlib portability concerns: integer width assumptions, negative combine lengths returning `0xffffffffUL`, and performance tuning. Test signals are compression/decompression integrity tests and any zlib self-tests/build checks; no dedicated subset test targets Adler directly.
<!-- END_FILE_RESEARCH: sources/sync-backup/rsync/zlib/adler32.c -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/rsync/zlib/compress.c -->
# sources/sync-backup/rsync/zlib/compress.c

Purpose: bundled zlib convenience API for compressing an in-memory buffer in one call and computing an upper bound for compressed size.

Important APIs/functions: `compress2()` initializes a `z_stream`, calls `deflateInit(level)`, runs `deflate(..., Z_FINISH)`, stores `stream.total_out` in `*destLen`, and calls `deflateEnd()`. `compress()` calls `compress2()` with `Z_DEFAULT_COMPRESSION`. `compressBound()` returns the standard conservative bound based on source length.

Control flow and state: no static state. The destination length is input/output: caller supplies capacity and receives actual compressed size. Errors distinguish invalid level/stream, memory failure, and insufficient output buffer (`Z_BUF_ERROR`).

Dependencies and integration: depends on bundled `zlib.h`/deflate implementation. Rsync’s `token.c` mainly uses streaming deflate directly, but this file is part of the bundled library surface and may be used by tools/tests or other zlib consumers. Risks are caller-supplied buffer sizing and 16-bit `MAXSEG_64K` truncation checks. Test signals are zlib API compatibility and compressed transfer integrity.
<!-- END_FILE_RESEARCH: sources/sync-backup/rsync/zlib/compress.c -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/rsync/zlib/crc32.c -->
# sources/sync-backup/rsync/zlib/crc32.c

Purpose: bundled zlib CRC-32 implementation, including optional dynamic table generation, endian-optimized word-at-a-time paths, and CRC combination.

Important APIs/functions: exports `get_crc_table()`, `crc32()`, `crc32_combine()`, and `crc32_combine64()`. With `DYNAMIC_CRC_TABLE`, `make_crc_table()` computes the polynomial tables and can emit `crc32.h` under `MAKECRCH`; otherwise it includes the static table header. `crc32_little()` and `crc32_big()` handle BYFOUR optimized processing. `gf2_matrix_times()`, `gf2_matrix_square()`, and `crc32_combine_()` combine CRCs for concatenated streams.

Control flow and state: static CRC tables are either compiled in or lazily generated. The dynamic-generation path uses volatile flags but is explicitly not fully thread-safe unless initialized before concurrent use. `crc32()` returns zero for `Z_NULL`, xor-initializes/finalizes the CRC, selects endian path when safe, and falls back to byte/DO8 loops.

Dependencies and integration: used by bundled zlib inflate/deflate/gzip-adjacent code and possibly checksum utilities. Risks include dynamic-table concurrency, pointer alignment/endian assumptions in BYFOUR, and length semantics for combine (`len2 <= 0` returns `crc1`). Test signals are zlib compatibility, decompression integrity, and any CRC table generation checks; rsync compressed-transfer tests indirectly exercise it.
<!-- END_FILE_RESEARCH: sources/sync-backup/rsync/zlib/crc32.c -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/rsync/zlib/crc32.h -->
# sources/sync-backup/rsync/zlib/crc32.h

Purpose: generated static CRC lookup tables for `zlib/crc32.c`.

Important content: declares `local const z_crc_t FAR crc_table[TBLS][256]`. The first table supports byte-at-a-time CRC updates; additional tables under `#ifdef BYFOUR` support little-endian and big-endian word-at-a-time CRC processing. Values are precomputed for the standard CRC-32 polynomial used by zlib.

Control flow and state: no executable control flow. The header is included only when `DYNAMIC_CRC_TABLE` is not defined, making table initialization compile-time data rather than runtime generation.

Dependencies and integration: tightly coupled to `crc32.c` macros `TBLS`, `BYFOUR`, `local`, `FAR`, and `z_crc_t`. Risks are table/source mismatch if regenerated with different polynomial or formatting assumptions, and code size from static tables. Test signals are CRC output compatibility and compressed stream integrity; any corruption here would surface broadly in zlib consumers.
<!-- END_FILE_RESEARCH: sources/sync-backup/rsync/zlib/crc32.h -->
