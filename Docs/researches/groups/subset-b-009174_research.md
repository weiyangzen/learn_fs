# subset-b-009174 research

This grouped report covers the requested rsync testsuite files. Each file section preserves the source path and is intended to be split into `Docs/researches/<source_path>_research.md`.

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/rsync/testsuite/devices_test.py -->
## sources/sync-backup/rsync/testsuite/devices_test.py

Purpose: executable regression coverage for rsync device handling, including character devices, block devices, FIFOs, hard-linked special files, and the `devices-fake` symlink variant that uses fake-super xattrs instead of real `mknod`.

Important APIs and control flow: imports `rsyncfns` helpers such as `run_rsync`, `checkdiff`, `rsync_ls_lR`, `xattr_set`, `xattrs_supported`, and itemize constants. At startup it detects the script name to select real-device or fake-super mode. Real mode requires root or re-execs through `FAKEROOT_PATH`; fake mode requires xattrs and patches `rsyncfns.RSYNC` and `TLS_ARGS` with `--fake-super`. `make_special()` creates real specials with `os.mkfifo`/`os.mknod` or fake specials via `user.rsync.%stat`. The test probes `rsync -VV` for `hardlink_specials`, builds source nodes, compares focused itemize output for device-number differences, then verifies a full `-aiHvv` transfer and directory listings.

State and dependencies: mutates `FROMDIR`, `TODIR`, optional `CHKDIR`, process environment through helper globals, filesystem device nodes or xattrs, and mtimes. It depends on platform privilege, fakeroot, xattr support, and `tls`.

Integration points: validates receiver/generator itemize semantics, fake-super metadata encoding, hard-link metadata for specials, and `--link-dest` behavior over device entries.

Risks and test signals: skip paths avoid false failures on unsupported systems. Strong signals are exact itemize strings, recursive `tls` listing equality, and hard-linked special output when supported. Main risk is privilege/platform variance around device creation and xattr namespaces.
<!-- END_FILE_RESEARCH: sources/sync-backup/rsync/testsuite/devices_test.py -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/rsync/testsuite/dir-sgid_test.py -->
## sources/sync-backup/rsync/testsuite/dir-sgid_test.py

Purpose: verifies rsync respects a setgid destination parent when creating new destination directories outside the transferred tree.

Important APIs and control flow: imports `SCRATCHDIR`, `run_rsync`, `check_perms`, `test_fail`, and `test_skipped`. It sets umask to `077`, discovers a secondary group when available, and defines `testit(dirname, dirperms, file_expected, prog_expected, dir_expected, setgid)`. `testit()` creates a parent destination, optionally changes its group, applies integer or symbolic permissions, runs `rsync -rvv` with a source directory, regular file, and program into `todir/to/`, then checks modes and setgid group inheritance.

State and dependencies: creates scratch source entries and two destination parents. It mutates process umask and restores it at the end. It uses `chmod` and optionally `getfacl`; default ACLs on Cygwin cause a skip.

Integration points: covers permission and gid propagation in receiver-side directory creation when rsync creates missing parent components rather than transferring them directly.

Risks and test signals: test is sensitive to filesystem setgid semantics and OS group inheritance differences, so it only asserts the portable setgid case. Signals are exact mode strings and gid equality for `to` and `to/dir`.
<!-- END_FILE_RESEARCH: sources/sync-backup/rsync/testsuite/dir-sgid_test.py -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/rsync/testsuite/dirs_test.py -->
## sources/sync-backup/rsync/testsuite/dirs_test.py

Purpose: focused coverage for `-d`/`--dirs`, confirming rsync copies named directories as empty directory entries without recursing.

Important APIs and control flow: uses `make_tree()` to create `FROMDIR/f0` plus nested `d1/d2/d3` files. After clearing `FROMDIR` and `TODIR`, it runs `run_rsync('-d', f'{src}/', f'{TODIR}/')`. It asserts the top-level file matches, top-level directory `d1` exists, and no child files or entries were copied inside `d1`.

State and dependencies: mutates only the standard `from` and `to` scratch trees. It depends on `rsyncfns` tree creation, file comparison, cleanup, and failure helpers.

Integration points: exercises file-list recursion control and destination creation for directory entries.

Risks and test signals: the test is intentionally narrow and low-flake. Signals are concrete filesystem assertions rather than broad directory equality, making it useful for distinguishing `-d` from recursive `-r` behavior.
<!-- END_FILE_RESEARCH: sources/sync-backup/rsync/testsuite/dirs_test.py -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/rsync/testsuite/duplicates_test.py -->
## sources/sync-backup/rsync/testsuite/duplicates_test.py

Purpose: regression coverage for duplicate source arguments. It ensures `clean_flist()` deduplicates repeated directory inputs so each file and symlink transfers exactly once.

Important APIs and control flow: creates `FROMDIR/name1` and a symlink `name2` to it. It invokes rsync manually through `subprocess.run(rsync_argv('-avv', *sources, f'{TODIR}/'))` with the same source directory repeated ten times. It counts verbose output lines for `name1` and `name2 -> ...`, requiring each to appear once, then compares recursive listings with `rsync_ls_lR`.

State and dependencies: uses symlink-capable filesystem state in `FROMDIR` and `TODIR`, and captures stdout to inspect copy behavior.

Integration points: ties directly to sender file-list normalization, duplicate source handling, symlink output, and listing verification through `tls`.

Risks and test signals: symlink creation may fail on restricted platforms and becomes a hard failure. The strongest signal is output cardinality, which catches duplicate-transfer regressions that final tree equality alone would miss.
<!-- END_FILE_RESEARCH: sources/sync-backup/rsync/testsuite/duplicates_test.py -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/rsync/testsuite/exclude_test.py -->
## sources/sync-backup/rsync/testsuite/exclude_test.py

Purpose: broad regression suite for excludes, includes, filter rules, merge files, CVS exclusions, delete timing, prune-empty behavior, update output, and the `exclude-lsh` remote-shell variant.

Important APIs and control flow: detects `lsh` in the script name and configures `RSYNC_RSH`, `--rsync-path`, and host prefixes. It builds a complex `FROMDIR` tree with `.filt`, `.filt2`, `.cvsignore`, wildcard-sensitive file names, update fixtures, and expected `CHKDIR` state. It runs a sequence of `run_rsync`, `checkit`, `verify_dirs`, and `checkdiff` calls, mutating `CHKDIR` between cases to model expected filtered output. `run_with_stdin_filter()` feeds a materialized merge filter file on stdin.

State and dependencies: sets `CVSIGNORE`, uses `FROMDIR`, `TODIR`, `CHKDIR`, `SCRATCHDIR`, and optional local remote-shell support. It imports `cp_touch` and `verify_dirs` mid-file for fixture adjustment.

Integration points: exercises filter parser ordering, per-directory merge filters, side-specific rules, delete modes, relative mode interaction, and itemized update output.

Risks and test signals: high value but stateful. Risks include stale expected-tree mutations, timing sensitivity around directory mtimes, and push/pull ordering differences. Signals include exact tree comparisons after each major filter phase and exact `--update --info=skip` itemize output.
<!-- END_FILE_RESEARCH: sources/sync-backup/rsync/testsuite/exclude_test.py -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/rsync/testsuite/executability_test.py -->
## sources/sync-backup/rsync/testsuite/executability_test.py

Purpose: validates `--executability`/`-E`, where rsync propagates only executable bits from source to destination while leaving other permission bits alone.

Important APIs and control flow: creates two shell files, attempts a sticky/setuid-style mode on file `1`, skips only on expected permission errors, and runs a baseline `rsync -rvv`. It verifies initial destination modes, then changes source and destination permissions. A second normal rsync run must leave destination permissions unchanged. A final `-rvvE` run must remove execute bits from `1` and add execute bits to `2` while preserving non-execute bits as documented.

State and dependencies: uses `FROMDIR`, `TODIR`, `os.chmod`, `run_rsync`, `check_perms`, and `test_skipped`. Platform behavior around sticky/setuid chmod is explicitly handled.

Integration points: tests receiver permission update logic independent of full `-p` mode preservation.

Risks and test signals: exact permission strings are the primary signal. The setup has portable skip handling for platforms that reject the initial chmod, reducing false failures.
<!-- END_FILE_RESEARCH: sources/sync-backup/rsync/testsuite/executability_test.py -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/rsync/testsuite/exitcodes.py -->
## sources/sync-backup/rsync/testsuite/exitcodes.py

Purpose: centralizes autotools-style test exit codes for the Python testsuite.

Important APIs and control flow: defines `Exit(enum.IntEnum)` with `PASS=0`, `FAIL=1`, `ERROR=2`, `SKIP=77`, and `XFAIL=78`. It has no import-time side effects by design, allowing `runtests.py` and `rsyncfns.py` to import it without triggering environment validation.

State and dependencies: depends only on the standard `enum` module and persists no state.

Integration points: re-exported by `rsyncfns` and consumed by tests through helper functions such as `test_fail`, `test_skipped`, and `test_xfail`. It is part of the contract between executable test scripts and the runner.

Risks and test signals: risk is low but changes are compatibility-sensitive because numeric values are conventional. The absence of side effects is itself important test infrastructure behavior.
<!-- END_FILE_RESEARCH: sources/sync-backup/rsync/testsuite/exitcodes.py -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/rsync/testsuite/file-to-file-mkpath-dry-run_test.py -->
## sources/sync-backup/rsync/testsuite/file-to-file-mkpath-dry-run_test.py

Purpose: regression coverage for issue #880 and a related dry-run itemize regression around `--mkpath` file-to-file copies.

Important APIs and control flow: defines `itemize(*args)` to run `rsync -ai` and return `(returncode, combined_output)`. First, it checks `--dry-run --mkpath` to a missing parent succeeds and produces itemized output equivalent to the real `--mkpath` run after normalizing directory names. Second, it checks a plain dry-run overwrite of an existing differing destination reports the same change as a real overwrite, avoiding false "brand new" output.

State and dependencies: uses `SCRATCHDIR`, `makepath`, `rmtree`, `rsync_argv`, and `test_fail`. It creates isolated `mk` and `ex` scratch subtrees.

Integration points: covers dry-run path creation, file-to-file destination resolution, and itemized output consistency.

Risks and test signals: exact stdout/stderr comparison is the key signal. It intentionally compares dry-run to real-run behavior, catching regressions that do not affect final filesystem state.
<!-- END_FILE_RESEARCH: sources/sync-backup/rsync/testsuite/file-to-file-mkpath-dry-run_test.py -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/rsync/testsuite/files-from-depth_test.py -->
## sources/sync-backup/rsync/testsuite/files-from-depth_test.py

Purpose: covers `--files-from`, `--from0`, `--exclude-from`, and `--include-from` for paths several levels deep.

Important APIs and control flow: `seed()` rebuilds a depth-3 tree. The test writes newline and NUL-delimited file lists, verifies only listed deep paths transfer, checks comment handling for `#` and `;` entries in both list modes, then verifies exclude and include filter files at top-level and nested paths.

State and dependencies: uses `FROMDIR`, `SCRATCHDIR`, `TODIR`, `make_tree`, cleanup helpers, `run_rsync`, and existence/content assertions. It writes list files under `SCRATCHDIR`.

Integration points: exercises sender file-list input parsing, implied parent creation, NUL-delimited parsing, comment skipping, and filter-file matching at depth.

Risks and test signals: signals are specific positive and negative path assertions. The test avoids broad tree equality so it can prove omitted paths remain absent.
<!-- END_FILE_RESEARCH: sources/sync-backup/rsync/testsuite/files-from-depth_test.py -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/rsync/testsuite/files-from_test.py -->
## sources/sync-backup/rsync/testsuite/files-from_test.py

Purpose: verifies `--files-from=LIST` for a canonical hands fixture locally and across local remote-shell combinations.

Important APIs and control flow: calls `hands_setup()` to populate `FROMDIR`, writes a `filelist` containing anchored `from/./` entries and selected nested paths, then builds `CHKDIR` by syncing source while excluding entries that should not be present. It first runs a local `checkit`, then loops over four combinations of files-list host and source/destination host using `lsh.sh`, `--rsync-path`, and `-e`.

State and dependencies: uses standard scratch dirs plus `SRCDIR/support/lsh.sh`, `RSYNC_PEER`, and `rmtree` between remote-shell cases.

Integration points: covers files-from path anchoring, remote files-from retrieval, local-to-remote and remote-to-local transfers, and expected tree comparison through `checkit`.

Risks and test signals: remote-shell helper availability and path prefix handling are the main risk. Signal is final `CHKDIR` versus `TODIR` equality for every host placement combination.
<!-- END_FILE_RESEARCH: sources/sync-backup/rsync/testsuite/files-from_test.py -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/rsync/testsuite/filter-depth_test.py -->
## sources/sync-backup/rsync/testsuite/filter-depth_test.py

Purpose: focused depth coverage for `--exclude`, ordered `--include`, and `-F` per-directory merge filters.

Important APIs and control flow: `seed_ext()` creates a four-level tree with `.txt` and `.log` files at every level. The test first excludes all `*.log`, then includes directories and `*.txt` before excluding everything else. A separate fixture places `.rsync-filter` at `d1/d2` with `- secret*`; it verifies files above the merge directory survive and files at/below it are excluded.

State and dependencies: mutates only `FROMDIR` and `TODIR`; uses `makepath`, `rmtree`, `run_rsync`, and assert helpers.

Integration points: validates filter precedence and per-directory filter loading as rsync descends through parent components.

Risks and test signals: clear path-specific existence assertions give strong signals. The main risk is forgetting the `.rsync-filter` scope: rules must not affect ancestors.
<!-- END_FILE_RESEARCH: sources/sync-backup/rsync/testsuite/filter-depth_test.py -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/rsync/testsuite/fleettest.py -->
## sources/sync-backup/rsync/testsuite/fleettest.py

Purpose: standalone fleet CI harness. It pushes a source-only rsync checkout to configured local or remote targets, builds it, runs the Python testsuite under pipe/TCP/older protocols/non-root modes, retries configured flakes, reports unexpected results, and cleans run remnants.

Important APIs and types: `Target`, `CmdResult`, `TransportResult`, and `TargetResult` dataclasses model target config and outcomes. Key functions include `load_fleet()`, `run_on()`, `push_argv()`, `parse_workflow_skip()`, `discover_nonroot_tests()`, `build_script()`, `test_script()`, `parse_transport()`, `retry_failed()`, `run_target()`, `print_report()`, `print_timing()`, `cleanup_run()`, `cleanup_remnants()`, and `main()`.

Control flow: `main()` parses CLI arguments, validates repo/testsuite, loads fleet JSON, optionally lists or cleans, assigns a random run id to build dirs, stages `git archive HEAD`, overlays an alternate testsuite when requested, discovers non-root tests, and runs targets concurrently. Each target is pinged, pushed with rsync, built, tested by selected transports and protocols, optionally non-root tested, then summarized.

State and persistence: reads fleet config and workflows, creates temporary staging dirs, remote build dirs, global cleanup target lists, and optional retained run dirs. Cleanup uses shell scripts with guarded patterns and `sudo -n` fallback.

Dependencies and integration: depends on ssh, rsync, git, tar, target toolchains, workflow skip lists, `runtests.py`, and target privilege model. It integrates with CI matrix semantics and tests marked `fleet_nonroot = True`.

Risks and test signals: high operational blast radius around remote `rm -rf` and process cleanup, mitigated by `_unsafe_builddir`, random suffixes, and scoped patterns. Signals are parsed PASS/FAIL/ERROR/SKIP counts, skip-list diffs, per-cell status, recovered flaky lists, and timing summaries.
<!-- END_FILE_RESEARCH: sources/sync-backup/rsync/testsuite/fleettest.py -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/rsync/testsuite/fuzzy-basis_test.py -->
## sources/sync-backup/rsync/testsuite/fuzzy-basis_test.py

Purpose: verifies `--fuzzy` candidate scoring chooses the closest same-directory basis by name similarity, not merely that the final file contents match.

Important APIs and control flow: builds a deep source file `d1/d2/archive-v2.tar` and destination candidates `archive-v1.tar`, `archive-old.tar`, and `unrelated.dat`. It runs `rsync -a --fuzzy --no-whole-file --debug=FUZZY`, then requires debug output naming `archive-v1.tar` as the selected basis before comparing final bytes.

State and dependencies: uses `make_data_file`, direct byte writes for candidate contents, and `run_rsync(capture_output=True)`.

Integration points: exercises generator fuzzy-basis selection and delta basis lookup at depth.

Risks and test signals: the debug-line assertion is the crucial signal because a full transfer could also produce correct bytes. Risk is debug message wording drift.
<!-- END_FILE_RESEARCH: sources/sync-backup/rsync/testsuite/fuzzy-basis_test.py -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/rsync/testsuite/fuzzy_test.py -->
## sources/sync-backup/rsync/testsuite/fuzzy_test.py

Purpose: canonical `--fuzzy` regression test using an existing destination file under a different name as the delta basis, while `--delete-delay` removes the stale basis later.

Important APIs and control flow: copies `rsync.c` to `FROMDIR/rsync.c`, copies it with preserved times to `TODIR/rsync2.c`, sleeps to avoid timestamp ambiguity, and runs `rsync -avvi --no-whole-file --fuzzy --delete-delay --debug=FUZZY`. It asserts debug output says `rsync2.c` was selected as the basis, then calls `verify_dirs(FROMDIR, TODIR)`.

State and dependencies: depends on `SRCDIR/rsync.c`, `cp_p`, `cp_touch`, timing, and `verify_dirs`.

Integration points: covers generator fuzzy matching, delta update path, delayed delete cleanup, and final tree equality.

Risks and test signals: debug output is required to prove fuzzy engaged. Final tree equality verifies delete-delay removed the old basis.
<!-- END_FILE_RESEARCH: sources/sync-backup/rsync/testsuite/fuzzy_test.py -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/rsync/testsuite/hands_test.py -->
## sources/sync-backup/rsync/testsuite/hands_test.py

Purpose: canonical end-to-end transfer smoke test over a rich fixture produced by `hands_setup()`.

Important APIs and control flow: performs six phases: basic `-av`; hard-link preservation after linking `filelist` into a subdir with `-H`; single-file repair after deleting destination `text`; delta repair after appending extra data and using `--no-whole-file`; `--delete` cleanup of a stray destination file; and non-recursive globbed copy of top-level entries followed by an exclude-all comparison pass.

State and dependencies: mutates the standard `from`/`to` trees, creates hard links, appends files, changes cwd to `TMPDIR`, and uses `checkit` plus direct `run_rsync`.

Integration points: broad integration coverage for archive transfer, hard links, delta algorithm, delete behavior, and argument expansion.

Risks and test signals: primarily final directory and file diffs from `checkit` after each phase. It is broad but less diagnostic than focused tests.
<!-- END_FILE_RESEARCH: sources/sync-backup/rsync/testsuite/hands_test.py -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/rsync/testsuite/hardlinks-deep_test.py -->
## sources/sync-backup/rsync/testsuite/hardlinks-deep_test.py

Purpose: verifies `-H` preserves a hard-link relationship across different nested directories, and that omitting `-H` creates independent files.

Important APIs and control flow: builds `FROMDIR/a/aa/orig` and hard links it to `FROMDIR/b/bb/hardlink`. It runs `rsync -aH` and asserts the destination paths share an inode, then clears `TODIR`, runs `rsync -a`, and asserts they do not.

State and dependencies: uses `os.link`, `makepath`, `rmtree`, `run_rsync`, and hard-link assertion helpers.

Integration points: targets hard-link bookkeeping across directory boundaries, complementing root-level hard-link tests.

Risks and test signals: filesystem hard-link support is assumed; same-inode versus not-same-inode checks are strong behavioral signals.
<!-- END_FILE_RESEARCH: sources/sync-backup/rsync/testsuite/hardlinks-deep_test.py -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/rsync/testsuite/hardlinks_test.py -->
## sources/sync-backup/rsync/testsuite/hardlinks_test.py

Purpose: comprehensive hard-link regression test for `-H`, incremental recursion, remote-shell transfers, alternate basis dirs, checksum mode, and single-file/single-directory edge cases.

Important APIs and control flow: creates three linked names and one copied file, plus a large `text` file from source `.c` files. It checks local `-aHivv`, delta overwrite preservation, then adds many small files and a deep hard link to stress incremental recursion over `lsh.sh`. It tests `--link-dest`, `--copy-dest`, and a `--checksum` run that must not copy an outside-linked `solo`. Finally it verifies single-file and single-directory `-H` copies through `diff`.

State and dependencies: uses hard links, many generated files, `CHKDIR`, `TODIR`, `OUTFILE`, `RSYNC_PEER`, and remote shell support.

Integration points: validates hard-link tables across sender/receiver modes, basis dirs, checksum, and protocol edge cases.

Risks and test signals: exact tree comparisons and output absence of `solo` are key. It skips only if initial hard-link creation is unsupported.
<!-- END_FILE_RESEARCH: sources/sync-backup/rsync/testsuite/hardlinks_test.py -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/rsync/testsuite/inplace_test.py -->
## sources/sync-backup/rsync/testsuite/inplace_test.py

Purpose: verifies `--inplace` updates a deep destination file without replacing its inode, while the default temp-and-rename path does replace it.

Important APIs and control flow: `seed()` builds a depth-3 data tree; `inode()` returns `st_ino`; `modify_deep()` flips bytes in the middle of the source file and bumps mtime to force a delta. The first phase syncs, records inode, runs `--inplace --no-whole-file`, checks content and same inode. The control phase syncs fresh, runs default `--no-whole-file`, and requires a different inode.

State and dependencies: uses data files, mtimes, and inode observations in `FROMDIR`/`TODIR`.

Integration points: covers receiver update strategy, temporary file rename behavior, and deep path resolution.

Risks and test signals: inode equality is filesystem-sensitive but appropriate for local POSIX tests. Content equality guards against a no-op or corrupt update.
<!-- END_FILE_RESEARCH: sources/sync-backup/rsync/testsuite/inplace_test.py -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/rsync/testsuite/itemize_test.py -->
## sources/sync-backup/rsync/testsuite/itemize_test.py

Purpose: detailed regression suite for itemized output (`-i`, `-ii`) and verbose output across normal, hard-link, symlink, checksum, copy/link/compare-dest, dry-run, and delta cases.

Important APIs and control flow: builds a small tree with files from source fixtures, a symlink, and a hard link. It probes `rsync -VV` for `hardlink_symlinks` and `symtimes`, adjusts expected output tokens, then runs many `checkdiff()` calls with exact expected stdout. Between phases it retouches directories, modifies modes/content, replaces symlinks, and creates/removes `to2dir`.

State and dependencies: uses `FROMDIR`, `TODIR`, `to2dir`, source fixture files, itemize constants, `v_filt`, and build-feature detection.

Integration points: exercises itemize formatting for file, dir, symlink, hard-link, basis-dir, compare-dest, link-dest, and copy-dest decisions.

Risks and test signals: exact output comparisons are high-signal but brittle to intentional format changes or feature variation. Feature probes reduce portability risk.
<!-- END_FILE_RESEARCH: sources/sync-backup/rsync/testsuite/itemize_test.py -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/rsync/testsuite/link-dest-module-escape_test.py -->
## sources/sync-backup/rsync/testsuite/link-dest-module-escape_test.py

Purpose: security regression guard ensuring a daemon receiver does not honor a relative `--link-dest` path that climbs outside the module root.

Important APIs and control flow: creates a daemon module `mod/00`, a source tree, and an outside sibling containing an identical `f.dat`. It starts a test daemon with writable module `bak` and pushes with `--link-dest=../../OUTSIDE` to `bak/00/`. Return code `0` or `23` is allowed. It then asserts the destination exists but is not hard-linked to the outside secret file.

State and dependencies: uses daemon config helpers, `start_test_daemon`, fixed port 12916, `make_data_file`, and inode comparison.

Integration points: validates confined resolver behavior for daemon alt-basis dirs and module boundary enforcement.

Risks and test signals: same-inode detection catches information leak/cross-module hard-link regressions. Platform resolver differences are tolerated by allowing rc 23.
<!-- END_FILE_RESEARCH: sources/sync-backup/rsync/testsuite/link-dest-module-escape_test.py -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/rsync/testsuite/link-dest-pathroot_test.py -->
## sources/sync-backup/rsync/testsuite/link-dest-pathroot_test.py

Purpose: functional regression test for relative `--link-dest=../01` against a daemon module configured with `path = /`.

Important APIs and control flow: creates sibling basis `base/01` and source `src`, copies identical `f.dat` to the basis, serves a root module, and addresses `base` through the module using its absolute path without the leading slash. It pushes to `root/<base_rel>/00/` with `--link-dest=../01`, allows rc `0` or `23`, then requires the destination file to be hard-linked to the basis or reports an expected failure with `test_xfail`.

State and dependencies: fixed daemon port 12931, daemon config, `shutil.copy2`, inode comparison.

Integration points: covers daemon receiver alt-basis re-anchoring when module path length is zero.

Risks and test signals: intentionally XFAILs on platforms that cannot safely honor `..` via `openat2`/`RESOLVE_BENEATH`. Passing signal is inode identity with the sibling basis.
<!-- END_FILE_RESEARCH: sources/sync-backup/rsync/testsuite/link-dest-pathroot_test.py -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/rsync/testsuite/link-dest-relative-basis_test.py -->
## sources/sync-backup/rsync/testsuite/link-dest-relative-basis_test.py

Purpose: regression test for issue #915, where daemon receivers ignored relative alt-basis dirs such as `../01`, silently re-transferring files instead of using the basis.

Important APIs and control flow: builds module root `bakmod` with basis `01/f.dat` and source `src915/f.dat`. `push(opt)` creates a fresh dest `00` and runs rsync with `--stats`; `same_inode()` checks hard links; `literal_bytes()` parses stats. It tests three modes: `--link-dest` must hard-link, `--copy-dest` must send little literal data, and `--compare-dest` must skip creating the file. Any regression list is reported as `test_xfail`.

State and dependencies: starts daemon on port 12915, writes daemon config, uses regex parsing and inode checks.

Integration points: exercises shared `check_alt_basis_dirs()` behavior across link/copy/compare-dest in daemon sanitize-path contexts.

Risks and test signals: intentionally XFAILs where safe relative basis climbs are unsupported. Distinct signals per option reduce false positives.
<!-- END_FILE_RESEARCH: sources/sync-backup/rsync/testsuite/link-dest-relative-basis_test.py -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/rsync/testsuite/links_test.py -->
## sources/sync-backup/rsync/testsuite/links_test.py

Purpose: depth coverage for source-side symlink handling options `-l`, `-L`, and `-k`.

Important APIs and control flow: `seed()` builds a depth-3 tree with a deep file symlink `sl` and directory symlink `dirlink`. With `-rl`, both links must remain symlinks with exact targets. With `-rL`, both links must be dereferenced into regular file/directory contents. With `-rlk`, only the directory symlink is followed, while the file symlink remains a symlink.

State and dependencies: uses `os.symlink`, `make_tree`, cleanup, `run_rsync`, `assert_is_symlink`, `assert_same`, and `test_fail`.

Integration points: validates file-list symlink treatment and source-side link dereferencing at nested paths.

Risks and test signals: symlink support is assumed. Signals are exact symlink target checks plus regular content checks for dereferenced paths.
<!-- END_FILE_RESEARCH: sources/sync-backup/rsync/testsuite/links_test.py -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/rsync/testsuite/longdir_test.py -->
## sources/sync-backup/rsync/testsuite/longdir_test.py

Purpose: regression test for historical path handling bugs with very long directory names.

Important APIs and control flow: calls `hands_setup()`, constructs a 175-character directory name nested three times under `FROMDIR`, creates two leaf files with deterministic content through `make_text_file`, and runs `checkit(['--delete', '-avH', ...], FROMDIR, TODIR)`.

State and dependencies: mutates `FROMDIR` and `TODIR`, requires filesystem support for long path components, and skips if directory or file creation fails.

Integration points: broad transfer, delete, and hard-link logic over long nested paths.

Risks and test signals: platform path length limits are handled via skip. Final `checkit` listing and file diffs prove the long paths survived transfer unchanged.
<!-- END_FILE_RESEARCH: sources/sync-backup/rsync/testsuite/longdir_test.py -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/rsync/testsuite/merge_test.py -->
## sources/sync-backup/rsync/testsuite/merge_test.py

Purpose: verifies rsync merges multiple source directories and explicit file arguments into one destination with the expected precedence and conflict behavior.

Important APIs and control flow: changes cwd to `TMPDIR`, creates `from1`, `from2`, `from3`, `deep`, and `shallow` fixtures, builds expected `CHKDIR`, and uses `cp_touch()` to normalize copied file timestamps. `_flatten_dirs(src, dst)` pre-syncs existing directory times with a filter that excludes non-directories. The final `checkit()` invokes rsync with explicit `deep/arg-test`, `shallow`, and three source dirs into `to/`.

State and dependencies: uses relative paths intentionally, mutates `CHKDIR`, `TODIR`, and source dirs, and sleeps to move mtimes forward.

Integration points: covers multi-source file-list generation, merge precedence, directory/file conflicts, and timestamp normalization.

Risks and test signals: timing and expected-tree construction are the main risks. Final tree equality is the acceptance signal.
<!-- END_FILE_RESEARCH: sources/sync-backup/rsync/testsuite/merge_test.py -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/rsync/testsuite/metadata-depth_test.py -->
## sources/sync-backup/rsync/testsuite/metadata-depth_test.py

Purpose: validates permission, mtime, and `--chmod` metadata handling for files and directories at every level of a nested tree.

Important APIs and control flow: `seed()` creates a depth-3 tree, sets all file modes to `0640`, directory modes to `0750`, and distinct old file mtimes. First `run_rsync('-rlpt')` must preserve modes and times. Then a fresh seed with `run_rsync('-a', '--chmod=D710,F600')` must rewrite directory modes to `0710` and file modes to `0600`.

State and dependencies: uses `walk_files`, `walk_dirs`, `assert_mode`, `assert_mtime_close`, and fixed mtimes.

Integration points: covers receiver metadata application over deep parent chains and chmod rule parsing.

Risks and test signals: exact mode assertions are strong. Mtime tolerance accounts for filesystem precision.
<!-- END_FILE_RESEARCH: sources/sync-backup/rsync/testsuite/metadata-depth_test.py -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/rsync/testsuite/missing_test.py -->
## sources/sync-backup/rsync/testsuite/missing_test.py

Purpose: guards three regressions in missing-destination/dry-run logic.

Important APIs and control flow: creates `FROMDIR/subdir/file` and a stray `TODIR/other`. `run_capture()` runs rsync and prints combined output. Test 1 runs dry-run `--ignore-non-existing -vv` and fails if it emits "not creating new" for `subdir/file` whose parent exists. Test 2 runs dry-run `-R --no-implied-dirs -y` unless forced protocol 29 rejects it. Test 3 runs dry-run `--delete-after -i` and requires a `*deleting other` line.

State and dependencies: uses `RSYNC` string for protocol detection, `TMPDIR/out1` for captured output, and direct subprocess calls.

Integration points: covers dry-run file-list handling, fuzzy dirlist construction, implied dirs, and delete-after reporting.

Risks and test signals: exact output substring checks are targeted. Protocol gating avoids false failures on older wire behavior.
<!-- END_FILE_RESEARCH: sources/sync-backup/rsync/testsuite/missing_test.py -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/rsync/testsuite/mkpath_test.py -->
## sources/sync-backup/rsync/testsuite/mkpath_test.py

Purpose: verifies `--mkpath` creates missing destination parent directories for several file and directory destination forms.

Important APIs and control flow: copies source fixtures into `FROMDIR`, changes cwd to `TMPDIR`, and defines `assert_file(path, label, src='from/text')` using `filecmp.cmp`. It first proves a transfer without `--mkpath` fails and creates nothing. It then tests file-to-file deep destination, trailing-slash directory destination, pre-existing destination directory, alternate final filename, whole-directory multi-source with and without trailing slash, and a simple current-directory file destination.

State and dependencies: uses relative paths, `rmtree`, `run_rsync`, `makepath`, and fixture files from `SRCDIR`.

Integration points: covers destination path creation and disambiguation of final component as file versus directory.

Risks and test signals: content comparison for each expected file is strong; negative control ensures the successes are attributable to `--mkpath`.
<!-- END_FILE_RESEARCH: sources/sync-backup/rsync/testsuite/mkpath_test.py -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/rsync/testsuite/omit-times_test.py -->
## sources/sync-backup/rsync/testsuite/omit-times_test.py

Purpose: verifies `-O` omits directory mtimes while preserving file mtimes, and `-J` omits symlink mtimes where supported.

Important APIs and control flow: `seed()` builds a depth-3 tree and sets all file and directory mtimes to a fixed old timestamp. With `run_rsync('-rlt', '-O')`, every file mtime must match `OLD` while every directory mtime must differ. For `-J`, it creates a deep symlink, attempts to set its mtime with `follow_symlinks=False`, skips that subcheck when unsupported, then requires copied symlink mtime not to equal `OLD`.

State and dependencies: uses `os.utime`, symlink support, `walk_files`, `walk_dirs`, and mtime assertions.

Integration points: covers receiver time-setting exclusions for directories and symlinks.

Risks and test signals: symlink mtime portability is explicitly handled. Directory checks require every directory to omit times, catching partial regressions.
<!-- END_FILE_RESEARCH: sources/sync-backup/rsync/testsuite/omit-times_test.py -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/rsync/testsuite/open-noatime_test.py -->
## sources/sync-backup/rsync/testsuite/open-noatime_test.py

Purpose: verifies `--open-noatime` leaves the source access time unchanged during transfer of a non-empty file.

Important APIs and control flow: probes `rsync -VV` for atime support and skips non-Linux platforms because `O_NOATIME` is Linux-specific. It creates `FROMDIR/foo`, pins its atime to a fixed historical timestamp, sets `rsyncfns.TLS_ARGS = '--atimes'`, captures a `tls` listing before transfer, runs rsync with `--open-noatime --archive --recursive --times --atimes -vvv`, captures a second listing, and diffs on mismatch.

State and dependencies: mutates `TLS_ARGS`, writes `TMPDIR/atime-from-before` and `atime-from-after`, depends on `TOOLDIR/tls`.

Integration points: covers source file opening flags and atime preservation through rsync's archive/atime paths.

Risks and test signals: avoids `checkit` because diffing source files would change atime. Exact `tls` listing equality is the signal.
<!-- END_FILE_RESEARCH: sources/sync-backup/rsync/testsuite/open-noatime_test.py -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/rsync/testsuite/output-options_test.py -->
## sources/sync-backup/rsync/testsuite/output-options_test.py

Purpose: breadth coverage for rsync output/reporting options rather than path semantics.

Important APIs and control flow: defines `out(*args, want_rc=0, env=None, text=True)` to capture output and require expected return codes. It checks `--version`, `--help`, `-i`, `--dry-run`, `--stats`, `--out-format=%n`, `--list-only`, `--quiet`, `--progress`, `-h`, and `-8`. For each successful transfer option it also verifies behavior, such as dry-run/list-only not creating files and quiet still transferring.

State and dependencies: rebuilds source/dest trees multiple times, creates a 50 KiB file for human-readable stats, and attempts a high-bit filename under `LC_ALL=C` for `-8`.

Integration points: validates CLI output contracts, itemize/stat formatting, progress output, and filename escaping.

Risks and test signals: output formats can intentionally change, but checks are documented-shape assertions. The high-bit filename case is best effort where filesystems preserve raw bytes.
<!-- END_FILE_RESEARCH: sources/sync-backup/rsync/testsuite/output-options_test.py -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/rsync/testsuite/ownership-depth_test.py -->
## sources/sync-backup/rsync/testsuite/ownership-depth_test.py

Purpose: verifies group and owner remapping options at depth, with root and non-root paths.

Important APIs and control flow: declares `fleet_nonroot = True` so fleet runs it as a normal user too. `seed()` builds a depth-3 tree and normalizes source group to the primary gid. `assert_all()` checks uid/gid for every destination entry. As root it tests numeric and wildcard `--groupmap`, named/nameless empty-source group mapping, `--chown`, `--usermap`, and combined user/group chown. As non-root it uses a secondary group for group-only remaps and skips user remap.

State and dependencies: depends on user/group IDs, `grp`, `rsync_getgroups`, privilege helpers, and filesystem ownership changes.

Integration points: covers idlist mapping, archive ownership application, numeric IDs, and fleet non-root discovery.

Risks and test signals: highly environment-sensitive. Skip paths handle missing secondary groups. Signals are uid/gid equality over all files and directories.
<!-- END_FILE_RESEARCH: sources/sync-backup/rsync/testsuite/ownership-depth_test.py -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/rsync/testsuite/partial_nowrite_test.py -->
## sources/sync-backup/rsync/testsuite/partial_nowrite_test.py

Purpose: tests that `--partial --delay-updates` succeeds when destination temp-file permissions initially prevent writing, exercising chmod/retry behavior for partials.

Important APIs and control flow: creates a 1 MiB read-only source file, pre-populates `TODIR/.~tmp~/some_file`, and detects whether the run is root. On Linux root with `os.unshare` and `setpriv`, it tries to drop DAC override inside a private mount namespace so the permission-denied path is meaningful. Finally it runs `checkit(['-avv', '--partial', '--delay-updates', ...], FROMDIR, TODIR)`.

State and dependencies: local `FROMDIR`/`TODIR` are redefined under `TMPDIR`; it may mutate `rsyncfns.RSYNC` to prefix `setpriv`. It depends on Linux namespace/capability tooling when root.

Integration points: receiver temp update and partial retry logic.

Risks and test signals: root can bypass DAC, so the exact chmod-retry path may not be exercised on all root environments. Final tree equality is the acceptance signal.
<!-- END_FILE_RESEARCH: sources/sync-backup/rsync/testsuite/partial_nowrite_test.py -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/rsync/testsuite/partial_test.py -->
## sources/sync-backup/rsync/testsuite/partial_test.py

Purpose: comprehensive coverage for `--partial` and relative/absolute `--partial-dir` at deep paths and across directory boundaries.

Important APIs and control flow: `seed_big()` creates a large deep file. `is_prefix()` validates partial contents. `interrupt_transfer(extra_args, partial_path)` starts a throttled delta transfer, polls for an in-progress temp file, sends SIGTERM, then waits for the expected partial. The test covers plain `--partial` resume, relative partial-dir preseed and cleanup, relative partial-dir interrupt/resume, absolute partial-dir outside the destination tree, and absolute partial-dir delta resume consuming the basis.

State and dependencies: uses `subprocess.Popen`, signals, polling deadlines, `SCRATCHDIR/partials`, and direct file prefix checks.

Integration points: receiver cleanup, partial storage resolution, delta basis opening, and verification after interrupted transfers.

Risks and test signals: timing-sensitive under heavy load, mitigated by low bandwidth and long deadlines. Signals include valid partial prefix, final content equality, and partial-dir cleanup.
<!-- END_FILE_RESEARCH: sources/sync-backup/rsync/testsuite/partial_test.py -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/rsync/testsuite/perftest.py -->
## sources/sync-backup/rsync/testsuite/perftest.py

Purpose: standalone developer benchmark for comparing transfer performance of two local rsync binaries over deterministic generated or existing trees.

Important APIs and types: `Binary` dataclass records label, path, and version. Tree generation uses `parse_size()`, `human()`, `gen_sizes()`, `build_dirs()`, `write_file()`, `rel_symlink()`, `safe_rmtree()`, and `generate_tree()`. Benchmarking uses `rsync_version()`, `drop_caches()`, `time_transfer()`, `run_benchmark()`, `_stats()`, `report()`, `_write_csv()`, and `main()`.

Control flow: CLI validates two executable binaries and run count, creates or uses a workdir, generates a heavy-tailed tree unless `--src` is provided, pre-populates a no-op destination, alternates binary order each loop, optionally drops caches, times full and/or no-op transfers, drops warmups from statistics, reports mean/stddev/min/median and regression/faster/no-change verdicts, optionally writes raw CSV, and cleans scratch unless `--keep`.

State and dependencies: creates scratch source/dest trees marked by `.perftest`, may write CSV, and may write `/proc/sys/vm/drop_caches` as root.

Integration points: not part of `runtests.py`; it evaluates real binary performance for archive/hard-link default args and generated symlinks/hardlinks/modes.

Risks and test signals: benchmark noise, caching, storage performance, and non-fsync behavior affect interpretation. Signals are repeated timing samples and threshold comparison against run-to-run stddev.
<!-- END_FILE_RESEARCH: sources/sync-backup/rsync/testsuite/perftest.py -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/rsync/testsuite/preallocate_test.py -->
## sources/sync-backup/rsync/testsuite/preallocate_test.py

Purpose: validates receiver file allocation paths: `--preallocate`, `--preallocate --sparse`, and `--inplace --sparse` hole punching.

Important APIs and control flow: probes `--preallocate` support with a trivial transfer. `fs_can_punch_holes()` uses `ctypes` to call libc `fallocate(PUNCH_HOLE|KEEP_SIZE)` and observes block reduction. `seed_plain()` and `seed_holey()` create deep regular and zero-run files. The test verifies content after preallocation, asserts sparse allocation when punch holes are supported, then modifies a synced file to introduce a zero run and verifies `--inplace --sparse --no-whole-file` punches it.

State and dependencies: Linux/Cygwin allocation support, `st_blocks`, libc, random file contents, and deep scratch paths.

Integration points: covers syscall wrappers `do_fallocate` and `do_punch_hole`, sparse writer behavior, and inplace sparse updates.

Risks and test signals: filesystem capability varies; allocation assertions run only when the real punch-hole probe succeeds. Content equality is always required.
<!-- END_FILE_RESEARCH: sources/sync-backup/rsync/testsuite/preallocate_test.py -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/rsync/testsuite/protected-regular_test.py -->
## sources/sync-backup/rsync/testsuite/protected-regular_test.py

Purpose: Linux-specific guard that `--inplace` can write to a protected regular file in a world-writable sticky directory when `fs.protected_regular` is enabled.

Important APIs and control flow: checks `/proc/sys/fs/protected_regular`, skips if unavailable or disabled, creates `TMPDIR/files` with mode `1777`, writes `src` and `dst`, and tries to `chown` `dst` to uid 5001. If not root, it attempts to re-exec under `unshare --user --map-root-user --map-users`. It runs `rsync --inplace src dst` and asserts destination content is exactly `"Source\n"`.

State and dependencies: Linux procfs, user namespaces or root, chown permissions, and sticky-directory semantics.

Integration points: receiver open/write behavior for inplace updates under kernel protected-regular restrictions.

Risks and test signals: environment-sensitive with many skip paths. A zero exit is not enough; content verification proves the write occurred.
<!-- END_FILE_RESEARCH: sources/sync-backup/rsync/testsuite/protected-regular_test.py -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/rsync/testsuite/proxy-response-line-too-long_test.py -->
## sources/sync-backup/rsync/testsuite/proxy-response-line-too-long_test.py

Purpose: regression test for an off-by-one stack out-of-bounds write in HTTP proxy response parsing.

Important APIs and control flow: requires real TCP via `require_tcp()`, claims fixed port 12873, starts an in-process loopback listener that accepts one CONNECT-style client, reads request headers, sends exactly 1023 `X` bytes without a newline, and closes. It runs rsync against an irrelevant daemon URL with `RSYNC_PROXY` pointing to the fake proxy, then checks the process did not die by signal, did not return success, and emitted `proxy response line too long`.

State and dependencies: binds a TCP socket, uses `claim_ports`, a serving thread, environment variable `RSYNC_PROXY`, and `SCRATCHDIR/workdir`.

Integration points: tests `establish_proxy_connection()` error handling and process safety.

Risks and test signals: only runs in `--use-tcp` mode. Strong signals are non-signal nonzero exit and exact stderr diagnostic.
<!-- END_FILE_RESEARCH: sources/sync-backup/rsync/testsuite/proxy-response-line-too-long_test.py -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/rsync/testsuite/prune-empty-dirs_test.py -->
## sources/sync-backup/rsync/testsuite/prune-empty-dirs_test.py

Purpose: verifies `-m`/`--prune-empty-dirs` removes directory chains that are empty in the source or become empty after filtering.

Important APIs and control flow: `reseed()` clears source and destination. First fixture creates an empty deep chain and a populated deep chain; `rsync -a -m` must omit `empty` and keep the file under `full`. Second fixture creates mixed keep/drop files and a logs-only subtree; with `--exclude=*.log`, rsync must keep the mixed subtree's `.txt` file and prune `onlylogs`.

State and dependencies: uses `makepath`, `rmtree`, `run_rsync`, and existence/content assertions.

Integration points: covers sender/receiver pruning decisions after filter evaluation.

Risks and test signals: simple and robust. Path-specific absence/presence assertions prove both empty-source and filter-emptied behavior.
<!-- END_FILE_RESEARCH: sources/sync-backup/rsync/testsuite/prune-empty-dirs_test.py -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/rsync/testsuite/recv-discard-nullderef_test.py -->
## sources/sync-backup/rsync/testsuite/recv-discard-nullderef_test.py

Purpose: regression test for a receiver NULL dereference on the delta discard path when output temp creation fails.

Important APIs and control flow: skips as root or when chmod cannot deny writes. It creates a daemon module with destination basis dir `d`, a source file sharing a leading block with the basis, starts a daemon, chmods the destination dir to `0555`, and probes that `mkstemp` fails there. It then runs a client-to-daemon delta transfer with `--no-whole-file -a` to overwrite `d/f`. The expected result is exit 23, not exit 12 protocol error from receiver crash and not 0.

State and dependencies: daemon config, fixed port 12895, chmod restoration in `finally`, temporary-file writability probe, `RSYNC` command splitting.

Integration points: covers `receive_data()` discard path, delta token draining, and daemon receiver failure handling.

Risks and test signals: privilege/capability variance can skip. Exit-code distinction is precise: 12 indicates pre-fix crash, 23 indicates benign forced discard.
<!-- END_FILE_RESEARCH: sources/sync-backup/rsync/testsuite/recv-discard-nullderef_test.py -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/rsync/testsuite/relative-implied_test.py -->
## sources/sync-backup/rsync/testsuite/relative-implied_test.py

Purpose: verifies `-R` implied directory behavior and `--no-implied-dirs` attribute behavior at depth.

Important APIs and control flow: sets umask to `022`, builds `SCRATCHDIR/rbase/a/b/c/file`, gives implied directory `b` mode `0750`, and changes cwd to `base/a`. A `run_rsync('-aR', 'b/c/file', TODIR)` must create implied dir `b` with source mode `0750` and copy the file. For protocol 30+, a fresh `--no-implied-dirs` run must create `b` with default mode `0755`, not source mode.

State and dependencies: uses `forced_protocol()` to skip the second half for protocol <30, and exact mode/content assertions.

Integration points: covers relative path file-list construction and implied directory metadata application.

Risks and test signals: protocol sensitivity is explicit. Mode assertions distinguish creation from attribute mirroring.
<!-- END_FILE_RESEARCH: sources/sync-backup/rsync/testsuite/relative-implied_test.py -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/rsync/testsuite/relative_test.py -->
## sources/sync-backup/rsync/testsuite/relative_test.py

Purpose: broad `--relative`/`-R` regression test for anchored paths, hard links, delete behavior, and merging extra anchored files.

Important APIs and control flow: creates a deep `FROMDIR/down/3/deep` and temporarily overrides `rsyncfns.FROMDIR` so `hands_setup()` populates that nested directory. It builds an external `extra` tree and a `./`-anchored extra file path. It seeds `CHKDIR`, changes cwd to `FROMDIR`, and runs `checkit()` for basic `-R`, hard-link preservation with `-H`, and `--del`. It manually captures output for no-op delete runs and fails on any `deleting ` line. It then tests merging the deep source with the extra anchored file, with and without `--del`.

State and dependencies: mutates module global `rsyncfns.FROMDIR` temporarily, uses `CHKDIR`, `TODIR`, `OUTFILE`, and cwd changes.

Integration points: file-list anchoring, implied parent paths, hard links under relative mode, and delete scoping.

Risks and test signals: output grep for erroneous deletes catches regressions final tree equality might miss. Global override is restored in `finally`.
<!-- END_FILE_RESEARCH: sources/sync-backup/rsync/testsuite/relative_test.py -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/rsync/testsuite/reverse-daemon-delta_test.py -->
## sources/sync-backup/rsync/testsuite/reverse-daemon-delta_test.py

Purpose: version-mixing smoke test for old client to current daemon and current daemon to old client, ensuring delta transfer still engages in both directions with and without compression.

Important APIs and control flow: starts a daemon using current `RSYNC`, drives the client with `RSYNC_PEER`, and parses old/new rsync summary formats via regex. `make_versions()` creates related old/new files with shared blocks and changed tail. `peer_client()` runs the peer binary and returns sent/received bytes. `assert_delta()` requires moved bytes less than half the file size. `run_push()` and `run_pull()` cover sender/receiver roles, each with optional `-z`.

State and dependencies: daemon config, fixed port 12894, `FROMDIR`, `TODIR`, `TMPDIR/client-src`, `TMPDIR/client-dst`, locale forced to C.

Integration points: daemon protocol compatibility, delta algorithm, compression, and alternate client/server binaries.

Risks and test signals: summary parsing must handle old wording. File content equality plus low wire bytes prove delta behavior rather than whole-file copying.
<!-- END_FILE_RESEARCH: sources/sync-backup/rsync/testsuite/reverse-daemon-delta_test.py -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/rsync/testsuite/rsyncfns.py -->
## sources/sync-backup/rsync/testsuite/rsyncfns.py

Purpose: shared Python helper module for the rsync testsuite, replacing the shell `rsync.fns` subset needed by rewritten tests.

Important APIs and state: validates required environment (`scratchdir`, `srcdir`, `TOOLDIR`, `RSYNC`), defines `SCRATCHDIR`, `SRCDIR`, `TOOLDIR`, `SUITEDIR`, `TMPDIR`, `FROMDIR`, `TODIR`, `CHKDIR`, `CHKFILE`, `OUTFILE`, `RSYNC_PEER`, `TLS_ARGS`, and `USE_TCP`, and normalizes umask/HOME. Result helpers are `test_fail`, `test_skipped`, and `test_xfail`.

Control flow and functions: rsync invocation helpers include `rsync_argv`, `forced_protocol`, and `run_rsync`. Daemon/port helpers include secure lock-file handling, `claim_ports`, `start_rsyncd`, `start_test_daemon`, and `require_tcp`. Filesystem/fixture helpers include `makepath`, `rmtree`, `cp_p`, `cp_touch`, `make_data_file`, `make_text_file`, `build_symlinks`, `hands_setup`, `make_tree`, `walk_files`, and `walk_dirs`. Verification helpers include `rsync_ls_lR`, `checkit`, `verify_dirs`, `v_filt`, `checkdiff`, `check_perms`, and path/property assertions. Ownership/xattr/daemon config helpers support privilege-sensitive and fake-super tests.

State and persistence: writes skip reasons, daemon config, lock files, output/listing diffs, temporary daemon processes, and may mutate global `TLS_ARGS`/`RSYNC`. It registers daemon cleanup with `atexit`.

Dependencies and integration: depends on POSIX tools (`find`, `sort`, `sed`, `xargs`, `diff`, `tls`), Python stdlib, and runner environment. It is the primary integration layer between executable tests and `runtests.py`.

Risks and test signals: helper bugs can cascade across the suite. Security-sensitive areas include `/tmp` lock-file validation, loopback daemon binding, and cleanup. Strong helper signals come from exact listing diffs, file diffs, itemize output diffs, and explicit skip/fail exit codes.
<!-- END_FILE_RESEARCH: sources/sync-backup/rsync/testsuite/rsyncfns.py -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/rsync/testsuite/safe-links-absolute-intree_test.py -->
## sources/sync-backup/rsync/testsuite/safe-links-absolute-intree_test.py

Purpose: documents and tests that `--safe-links` classifies symlink safety by literal target text, so absolute symlinks are dropped even when they resolve inside the copied tree.

Important APIs and control flow: creates `from/linked_file`, an absolute symlink to it, and a relative symlink to the same file. It first verifies plain `-a` preserves both links. Then `-av --safe-links` must emit `ignoring unsafe symlink`, omit the absolute link, preserve the relative link, and copy the referent. Finally `--copy-unsafe-links` must materialize the absolute link as a regular file while preserving the relative link.

State and dependencies: changes cwd to `TMPDIR`, uses local helper assertions built on `is_a_link`, `os.readlink`, and `os.path`.

Integration points: covers `unsafe_symlink()` policy and safe/copy-unsafe link options.

Risks and test signals: exact stderr substring and filesystem type checks distinguish dropping from dereferencing. It intentionally encodes surprising but documented behavior.
<!-- END_FILE_RESEARCH: sources/sync-backup/rsync/testsuite/safe-links-absolute-intree_test.py -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/rsync/testsuite/safe-links_test.py -->
## sources/sync-backup/rsync/testsuite/safe-links_test.py

Purpose: verifies `--safe-links` drops relative symlinks whose literal targets escape the transfer root while preserving in-tree relative symlinks.

Important APIs and control flow: creates `from/safe/files`, `from/safe/links`, and `from/unsafe`. It adds two safe links pointing to `../files/file1` and `../files/file2`, plus two escape attempts using `../../unsafe/unsafefile` and a normalized-upward path. It runs `rsync -avv --safe-links from/safe/ to` and checks safe links exist with exact targets while unsafe links do not exist, including dangling symlink checks.

State and dependencies: changes cwd to `TMPDIR`, uses symlink and path existence helpers.

Integration points: covers symlink safety classification for relative targets and destination omission behavior.

Risks and test signals: symlink support is required. Signals are exact target equality and lexists/islink absence for unsafe names.
<!-- END_FILE_RESEARCH: sources/sync-backup/rsync/testsuite/safe-links_test.py -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/rsync/testsuite/secure-relpath-validation_test.py -->
## sources/sync-backup/rsync/testsuite/secure-relpath-validation_test.py

Purpose: regression test for front-door validation of relative paths passed to `secure_relative_open()`, ensuring all literal `..` components are rejected by the portable resolver path.

Important APIs and control flow: creates `SCRATCHDIR/relpath-test`, then runs the compiled helper `TOOLDIR/t_secure_relpath` with that directory. The helper owns the individual suspect-input cases and returns nonzero if any path is accepted or rejected incorrectly. The Python script fails with a concise diagnostic on nonzero return.

State and dependencies: uses `rmtree`, scratch directory creation, and a built C test helper under `TOOLDIR`.

Integration points: tests low-level secure path resolver validation used by receiver-side safe opens, especially on platforms without kernel `RESOLVE_BENEATH` equivalents.

Risks and test signals: depends on the helper being built and accurate. The signal is the helper process return code; stderr identifies the specific failing case.
<!-- END_FILE_RESEARCH: sources/sync-backup/rsync/testsuite/secure-relpath-validation_test.py -->
