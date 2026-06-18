# subset-b-009173 research

Grouped research report for rsync testsuite files under `sources/sync-backup/rsync/testsuite`. Each section preserves the exact source path and is delimited for deterministic reconciliation into source-tree-aligned per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/rsync/testsuite/abdiff.py -->
# sources/sync-backup/rsync/testsuite/abdiff.py

Purpose: developer-only A/B differential regression hunter for rsync. It runs a build under test against a baseline rsync across curated transfer scenarios, matrix interop cases, fuzzed option sets, daemon/ssh/rrsync transports, and optional resource-cost checks. It is not a normal runtests.py test; it is intended to find behavior deltas and then minimize them into focused testsuite files.

Important APIs/types/functions: global configuration (`RSYNC_A`, `RSYNC_B`, `REPEAT`, `CMD_TIMEOUT`, `COST`), process helpers (`sh`, `_group_rss`, `supports`), filesystem oracles (`snapshot`, `_xattrs`, `_acl`, `diff_snapshots`), transfer runners (`run_xfer`, `run_daemon_xfer`, `run_daemon_pull`, `run_ssh_xfer`, `run_rrsync_push`, `run_rrsync_pull`, `_tcp_daemon`), fixture builders (`build_kitchen`, `build_recvtree`, `setup_with_basis`, many `_ft_*` helpers), `Scenario`, all `*_sweep()` factories, comparison engine (`_compare`, `run_scenario`), cross-version role matrix (`run_matrix`), stochastic fuzzer (`run_fuzz`), and CLI `main`.

Control flow: `main()` parses flags, selects fixed sweeps or matrix/fuzz mode, creates work and log directories, then runs scenarios through a `ThreadPoolExecutor`. Each `Scenario` creates a fresh work tree, builds source and optional destination/basis state, runs both binaries repeatedly, snapshots destination state, compares exit/error/literal-data/itemize/stdout/stderr/tree metadata, quarantines within-binary nondeterminism as FLAKY, and records DIFF/TIMEOUT/ERROR findings. Matrix and fuzz modes compare mixed A/B client/server roles against a pure baseline.

State and persistence behavior: workdirs are created under `--workdir` and deleted unless `--keep` or a finding exists. Findings append to a curated findings file plus a timestamped run log. Snapshot state captures type, mode, uid/gid, mtime, content hash, sparseness, hardlink grouping, symlink targets, device numbers, xattrs, and ACLs. Support caches option support checks and patches per-binary rrsync wrappers into the workdir.

Dependencies and integration points: uses rsync binaries, support scripts `support/lsh.sh`, `support/rrsh.sh`, `support/rrsync`, optional `getfacl`, Linux `/proc` for RSS sampling, TCP loopback for real daemon lanes, daemon config files, and Python concurrency. Integrates with the rsync source tree as a manual discovery tool, not a test harness module.

Risks and test signals: false positives are controlled with repeat runs, stability escalation, mtime ignore rules for intentionally unmanaged times, stderr/stdout normalization, and an allowlist for intentional refusals. Risks include high runtime, root-only and platform-specific fixture gaps, broad option interactions producing noisy failures, and reliance on current baseline semantics. Signal is exit status 1 when DIFF/TIMEOUT/ERROR candidates are found, with detail in findings logs.
<!-- END_FILE_RESEARCH: sources/sync-backup/rsync/testsuite/abdiff.py -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/rsync/testsuite/acls-default_test.py -->
# sources/sync-backup/rsync/testsuite/acls-default_test.py

Purpose: verifies that destination parent default POSIX ACLs influence newly created transfer directories and files even when the ACL-bearing parent is outside the transfer itself.

Important APIs/types/functions: `run_rsync('-VV')` gates on ACL support, environment variable `setfacl_nodef` selects default-ACL clearing syntax, helper `testit(dirname, default_acl, file_expected, prog_expected)`, `check_perms`, `test_skipped`, and `test_fail`.

Control flow: seed `SCRATCHDIR` with a default ACL to prove ACL support, create source `dir`, `file`, and executable `program`, change umasks, then call `testit()` for several default ACL and no-default ACL cases. Each case clears inherited defaults, optionally installs a default ACL, runs directory/file transfers into fresh destinations, and checks mode strings for container dirs, regular files, executable files, single-file local-name transfer, and sole-directory transfer.

State and persistence behavior: modifies scratch ACLs, umask, and destination file modes. The important persisted state is the mode inherited through destination default ACLs when rsync creates names.

Dependencies and integration points: depends on rsync ACL support, `setfacl`, the harness-provided `setfacl_nodef`, filesystem ACL support, and `rsyncfns.check_perms`.

Risks and test signals: skips on unsupported ACL tooling. Failures mean rsync ignored default ACL inheritance or incorrectly handled single-file/local-name and directory-only creation paths. Ambient umask is deliberately varied and not incidental.
<!-- END_FILE_RESEARCH: sources/sync-backup/rsync/testsuite/acls-default_test.py -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/rsync/testsuite/acls-depth_test.py -->
# sources/sync-backup/rsync/testsuite/acls-depth_test.py

Purpose: depth companion for `-A`; it checks that a distinctive POSIX ACL is preserved on every file and directory in a tree at least three levels deep.

Important APIs/types/functions: `make_tree`, `walk_dirs`, `walk_files`, `run_rsync('-aA')`, direct `setfacl` and `getfacl`, local `getfacl(path)` normalizer, and `test_fail`/`test_skipped`.

Control flow: skip unless rsync advertises ACL support and `setfacl`/`getfacl` exist. Build a depth-3 tree, apply `u:0:r-x` to every entry, sync with `-aA`, then compare normalized getfacl output for every relative path.

State and persistence behavior: source ACLs are durable filesystem metadata and are expected to appear identically on destination paths. Path-dependent getfacl comments are stripped before comparison.

Dependencies and integration points: POSIX ACL filesystem support, external ACL commands, and rsync archive ACL preservation.

Risks and test signals: skips if ACLs cannot be set. Failure indicates ACL loss at depth, identity-name rendering issues beyond accepted root/0 spelling, or resolver/path traversal regressions for deep ACL metadata.
<!-- END_FILE_RESEARCH: sources/sync-backup/rsync/testsuite/acls-depth_test.py -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/rsync/testsuite/acls_test.py -->
# sources/sync-backup/rsync/testsuite/acls_test.py

Purpose: shallow POSIX ACL preservation test for `rsync -A`, with support for either GNU `setfacl` or macOS-style `chmod +a` ACL manipulation.

Important APIs/types/functions: `_chmod_plus_a_supported`, `_setfacl`, `_chmod_acl`, `see_acls`, `run_rsync('-avvA')`, `makepath`, and harness skip/fail helpers.

Control flow: gate on rsync ACL support. Create directory `foo` and files `file1`/`file2`, install several user/group ACL entries using the available ACL command surface, run rsync from `FROMDIR` into `TODIR`, capture ACL listings in source and destination cwd, and fail if listings differ.

State and persistence behavior: writes ACL metadata to three source entries and stores the expected ACL listing in `SCRATCHDIR/acls.txt`. The tested persistent state is exact ACL list preservation through archive transfer.

Dependencies and integration points: depends on `rsyncfns` scratch paths, host ACL tooling, `setfacl_nodef`, and platform ACL listing differences.

Risks and test signals: may skip on unsupported platforms or filesystems. Signal is strict source-vs-destination ACL listing equality, so harmless formatting changes in external tools can be noisy.
<!-- END_FILE_RESEARCH: sources/sync-backup/rsync/testsuite/acls_test.py -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/rsync/testsuite/alt-dest-deep_test.py -->
# sources/sync-backup/rsync/testsuite/alt-dest-deep_test.py

Purpose: property-level depth coverage for `--link-dest`, `--copy-dest`, and `--compare-dest` using an alternate tree outside both source and destination.

Important APIs/types/functions: `make_tree`, `walk_files`, `run_rsync`, `assert_hardlinked`, `assert_not_hardlinked`, `assert_same`, `assert_exists`, and `assert_not_exists`.

Control flow: build a depth-3 source tree, copy it to sibling `altref`, mutate the deepest file, then run each alt-dest option into a fresh destination. For `--link-dest`, unchanged files must be hardlinked to `altref` and the changed file must not. For `--copy-dest`, every file must exist, match source bytes, and not be hardlinked. For `--compare-dest`, only the changed file should be created.

State and persistence behavior: persists a reference tree and checks inode relationships as well as content. The changed deepest file exercises outside-tree basis lookup below multiple path components.

Dependencies and integration points: rsync alternate-destination receiver logic and harness inode/content assertions.

Risks and test signals: the test distinguishes semantic properties that a plain tree compare would miss. Failures identify link/copy/compare behavior confusion or deep basis path resolution regressions.
<!-- END_FILE_RESEARCH: sources/sync-backup/rsync/testsuite/alt-dest-deep_test.py -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/rsync/testsuite/alt-dest-symlink-race_test.py -->
# sources/sync-backup/rsync/testsuite/alt-dest-symlink-race_test.py

Purpose: daemon security regression for basedir confinement in alternate-destination lookup when the basedir parent is a symlink planted inside the module.

Important APIs/types/functions: daemon config writing, `start_test_daemon`, `rsync_argv`, uid/gid helpers, `rmtree`, and inode comparison between module and outside files.

Control flow: create module, outside directory, and source. Plant `module/cd -> outside`; create source `target.txt` matching outside content, mode, and mtime. Start a writable daemon module and push with `--link-dest=cd` into the module root. Fail if destination is hardlinked to `outside/target.txt`.

State and persistence behavior: uses inode identity as the escape signal. The daemon may run as root when available; uid/gid lines are commented when not root.

Dependencies and integration points: daemon receiver alternate-basis lookup, secure relative open behavior, loopback test daemon, and filesystem symlinks/hardlinks.

Risks and test signals: if the daemon fails before creating the destination, the test fails as vacuous. A failure after creation means parent-symlink confinement was bypassed and daemon-readable outside content was used as basis.
<!-- END_FILE_RESEARCH: sources/sync-backup/rsync/testsuite/alt-dest-symlink-race_test.py -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/rsync/testsuite/alt-dest_test.py -->
# sources/sync-backup/rsync/testsuite/alt-dest_test.py

Purpose: broad functional coverage of local and remote-shell alternative-destination options, including stacked `--compare-dest`/`--copy-dest` and `copy_file()` tmpfile paths.

Important APIs/types/functions: `hands_setup`, `run_rsync`, `checkit`, `rmtree`, `test_fail`, `RSYNC_PEER`, support `lsh.sh`, and inode checks with `os.stat`.

Control flow: seed `alt1` and `alt2` with selected subtrees of `FROMDIR`, create `alt3/likely` as a same-name candidate, update source mtimes, build `CHKDIR`, then run stacked compare-dest and copy-dest checks. It then loops over normal and `--inplace` copy-dest transfers, locally and through lsh remote-source/remote-dest variants, verifying destination equality and that `--copy-dest` copies rather than hardlinks the candidate.

State and persistence behavior: maintains several alternate basis directories, destination resets, and source timestamp changes to force comparison logic. Destination content must match source while selected alt-dest files are excluded or copied as expected.

Dependencies and integration points: rsync local transfer, remote-shell stand-in, alternate-dest receiver logic, tmpfile copy path, and harness directory comparison.

Risks and test signals: failures identify stacked basis lookup errors, copy-vs-link semantic regressions, or protocol/remote-shell argument handling issues.
<!-- END_FILE_RESEARCH: sources/sync-backup/rsync/testsuite/alt-dest_test.py -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/rsync/testsuite/append-shortsum_test.py -->
# sources/sync-backup/rsync/testsuite/append-shortsum_test.py

Purpose: regression for `--append-verify` redo with a negotiated strong checksum shorter than legacy 16-byte sums, specifically forced `xxh64`.

Important APIs/types/functions: JSON `run_rsync('-VV')`, `make_data_file`, `run_rsync('--append-verify', '--checksum-choice=xxh64', '--no-whole-file')`, `assert_same`, and `test_skipped`.

Control flow: skip if `xxh64` is unavailable. Create a 40KB source, write a corrupted 20KB prefix in destination, then run append-verify with xxh64 and no-whole-file. The run must complete and destination must match source.

State and persistence behavior: destination starts as a corrupt prefix so append-verify must append, detect whole-file verification failure, and redo via normal delta/inplace logic.

Dependencies and integration points: checksum negotiation, append redo generator/sender protocol, and xxhash support.

Risks and test signals: pre-fix failure was protocol incompatibility due to overstated `s2length`. The signal is nonzero rsync or mismatched final file.
<!-- END_FILE_RESEARCH: sources/sync-backup/rsync/testsuite/append-shortsum_test.py -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/rsync/testsuite/append_test.py -->
# sources/sync-backup/rsync/testsuite/append_test.py

Purpose: depth coverage for `--append` and `--append-verify`, including their semantic split at protocol >= 30.

Important APIs/types/functions: `make_tree`, `walk_files`, `forced_protocol`, `dest_prefix`, `run_rsync`, `assert_same`, and `test_fail`.

Control flow: build a depth-3 data tree, create destination prefixes for every file, and verify `--append` completes them. If protocol is not forced below 30, corrupt the deep file prefix and show plain `--append` leaves it wrong, while `--append-verify` repairs it.

State and persistence behavior: destination files are partial prefixes; the deep file can have corrupted leading bytes. The test asserts tail-only completion and verification-driven redo behavior.

Dependencies and integration points: append receiver/generator paths, protocol feature gating, and deep file traversal.

Risks and test signals: old protocol behavior skips distinguishing cases. Failures indicate incorrect trust/verification split or broken append repair at depth.
<!-- END_FILE_RESEARCH: sources/sync-backup/rsync/testsuite/append_test.py -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/rsync/testsuite/atimes_test.py -->
# sources/sync-backup/rsync/testsuite/atimes_test.py

Purpose: verifies access-time preservation when rsync advertises atime support.

Important APIs/types/functions: `run_rsync('-VV')`, `rsyncfns.TLS_ARGS = '--atimes'`, `os.utime`, and `checkit(['-rtUgvvv', ...])`.

Control flow: skip without atime support. Create `FROMDIR/foo`, set its atime to a fixed 2001 timestamp while retaining mtime, enable atime-aware test listing, then sync with `-U` and compare source/destination listings.

State and persistence behavior: source atime is explicit metadata; destination atime should be persisted by rsync and visible through the harness listing.

Dependencies and integration points: filesystem atime support, rsync `-U`/`--atimes`, and `rsyncfns` listing configuration.

Risks and test signals: filesystems mounted with unusual atime behavior can make this fragile. Failure means atime metadata is not preserved or not reflected in the listing.
<!-- END_FILE_RESEARCH: sources/sync-backup/rsync/testsuite/atimes_test.py -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/rsync/testsuite/backup-deep_test.py -->
# sources/sync-backup/rsync/testsuite/backup-deep_test.py

Purpose: property-level depth coverage for `--backup`, custom suffixes, `--backup-dir` outside the destination tree, and deletion capture under backup-dir.

Important APIs/types/functions: `make_tree`, `walk_files`, `run_rsync`, `assert_same`, `assert_not_exists`, `test_fail`, and sibling backup path `SCRATCHDIR/backups`.

Control flow: `seed()` creates a v1 source, copies it to destination, records old bytes, then mutates source to v2. The test verifies same-directory suffix backups contain v1, external backup-dir preserves deep relative paths with v1 bytes, and `--backup-dir --delete` moves a deep extraneous destination file into the backup tree.

State and persistence behavior: compares old content, new destination content, and backup-tree placement. The backup directory is outside both source and destination to exercise cross-directory rename/copy behavior.

Dependencies and integration points: rsync backup receiver logic, delete handling, no-whole-file updates, and harness content assertions.

Risks and test signals: failures show missing backups, wrong saved content, path flattening, or deletion loss at depth.
<!-- END_FILE_RESEARCH: sources/sync-backup/rsync/testsuite/backup-deep_test.py -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/rsync/testsuite/backup_test.py -->
# sources/sync-backup/rsync/testsuite/backup_test.py

Purpose: ported regression coverage for `--backup`, `--backup-dir`, `--delete-delay`, and `--backup --inplace` behavior on changed files.

Important APIs/types/functions: `_cat_glob`, `_run_and_capture`, `checkit`, `verify_dirs`, `cp_touch`, `rsync_argv`, `diff`, and backup info output checks.

Control flow: build two source files from source-code glob concatenations, establish destination and check copies, mutate source, then run plain backup and verify `name~` output and content. Next add a destination-only file and run backup-dir with delete-delay, verifying backup messages and backup-dir contents. Finally reset check state, mutate again, run inplace backup-dir, verify destination and backup tree, then sync bakdir cleanly.

State and persistence behavior: uses `CHKDIR` as the pre-rsync content oracle and `TMPDIR/bak` as backup storage. It moves same-directory backups back into place before the next phase.

Dependencies and integration points: backup itemization, delta transfer, delete-delay, backup-dir pathing, inplace updates, and external `diff`.

Risks and test signals: relies on backup info text fragments. Failures mean backup output or saved-content semantics changed.
<!-- END_FILE_RESEARCH: sources/sync-backup/rsync/testsuite/backup_test.py -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/rsync/testsuite/bare-do-open-symlink-race_test.py -->
# sources/sync-backup/rsync/testsuite/bare-do-open-symlink-race_test.py

Purpose: daemon receiver security regression for bare `do_open`, `do_symlink`, and `do_mknod` paths following parent symlinks out of a module.

Important APIs/types/functions: `setup`, `positive_control`, `run_attack`, `verify_outside_unchanged`, `verify_outside_unchanged_or_absent`, daemon config for normal and fake-super modules, uid/gid helpers, `mkfifo`, and platform skip.

Control flow: skip on platforms lacking needed secure-open support. Start one daemon with `upload` and `upload_fake`. First prove normal uploads work. Then run three attacks through `module/cd -> outside`: `--inplace --backup --backup-dir=cd`, fake-super symlink push, and fake-super FIFO push. Each must not signal-crash and must not change/create outside files.

State and persistence behavior: outside sentinel content/mode and absence of created `sym`/`fifo` are the security oracles. Fake-super module changes receiver metadata encoding paths.

Dependencies and integration points: daemon receiver path confinement, fake-super, symlink/mknod/open wrappers, platform kernel support, and test daemon.

Risks and test signals: skips if FIFO unavailable. Positive control avoids vacuous passes. Any outside mutation means module escape via a low-level syscall wrapper.
<!-- END_FILE_RESEARCH: sources/sync-backup/rsync/testsuite/bare-do-open-symlink-race_test.py -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/rsync/testsuite/batch-mode_test.py -->
# sources/sync-backup/rsync/testsuite/batch-mode_test.py

Purpose: exercises rsync batch generation and replay modes locally and against daemon source/destination modules.

Important APIs/types/functions: `build_rsyncd_conf`, `hands_setup`, `run_rsync`, `checkit`, `verify_dirs`, `rsync_argv`, generated `BATCH` files and `BATCH.sh`, and helper `ignore23`.

Control flow: build expected `CHKDIR`, verify `--only-write-batch` does not create destination, replay with `--read-batch`, generate a local write-batch and replay it, start daemon, generate/replay daemon sender batch, run generated `BATCH.sh` twice, then push to daemon with `--write-batch` through `ignore23` and verify destination.

State and persistence behavior: batch side files live in `TMPDIR`; destination is repeatedly wiped and recreated. The expected tree excludes daemon global `foobar.baz`.

Dependencies and integration points: local batch mode, daemon sender/receiver batch mode, generated shell script replay, and harness directory verification.

Risks and test signals: daemon paths may return code 23 on otherwise acceptable transfers. Failures show bad batch replay, unwanted destination creation, or non-idempotent `BATCH.sh`.
<!-- END_FILE_RESEARCH: sources/sync-backup/rsync/testsuite/batch-mode_test.py -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/rsync/testsuite/chdir-symlink-race_test.py -->
# sources/sync-backup/rsync/testsuite/chdir-symlink-race_test.py

Purpose: daemon receiver security regression for `chdir()` following an attacker-planted destination subdirectory symlink out of the module after earlier symlink-race hardening.

Important APIs/types/functions: `reset_outside`, `verify_unchanged`, `run_attack`, `positive_control`, `make_data_file`, daemon setup, and platform skip.

Control flow: create `module/subdir -> outside`, outside sentinel, and source files with matching size but different content/mode. Start writable daemon, prove ordinary writes to `realdir` work, then run four transfer shapes: single-file size-only into symlinked subdir, recursive size-only into subdir, recursive normal transfer into subdir, and recursive root upload regression check. Each must not signal-crash and must leave outside content/mode unchanged.

State and persistence behavior: outside sentinel is reset before every attack. Destination symlink state remains attacker-controlled.

Dependencies and integration points: daemon receiver chdir path, secure path traversal, size-only and delta/rename receiver flows, kernel support.

Risks and test signals: positive control guards against false passes caused by daemon refusal. Outside mode/content changes indicate chmod/write escape.
<!-- END_FILE_RESEARCH: sources/sync-backup/rsync/testsuite/chdir-symlink-race_test.py -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/rsync/testsuite/chgrp_test.py -->
# sources/sync-backup/rsync/testsuite/chgrp_test.py

Purpose: verifies group preservation with `-g` for every supplementary group available to the test user.

Important APIs/types/functions: `rsync_getgroups`, `os.chown`, fallback `chgrp`, `checkit(['-rtgpvvv', ...])`, and `test_fail`.

Control flow: obtain groups, create one source file per group, set its group via `os.chown` or `chgrp`, wait for timestamp separation, then sync with group preservation and compare listings.

State and persistence behavior: source files carry varied group IDs; destination group metadata must match.

Dependencies and integration points: host group database, permissions to chgrp to member groups, external `chgrp`, and rsync group preservation.

Risks and test signals: fails if no groups or no chgrp tool. Signal is harness listing mismatch for group ownership.
<!-- END_FILE_RESEARCH: sources/sync-backup/rsync/testsuite/chgrp_test.py -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/rsync/testsuite/chmod-option_test.py -->
# sources/sync-backup/rsync/testsuite/chmod-option_test.py

Purpose: tests client `--chmod` transforms and daemon `incoming chmod`, including a historical directory misclassification bug.

Important APIs/types/functions: `check_perms`, `checkit`, `check_permcopy`, `build_rsyncd_conf`, `start_test_daemon`, `run_rsync`, and mode manipulation with `os.chmod`/`os.umask`.

Control flow: build a source with varied modes, copy it to `checkdir`, set umask 002, manually apply the expected `ug-s,a+rX,D+w` transform to `checkdir`, and compare rsync output with that expected tree. It then tests chmod permission-copy expressions (`g=o,o=`, `g=u`, `g-o`, etc.), verifies invalid `g=ur` is rejected, checks `Fo-x` file-only chmod, and pushes with `--no-perms` to a daemon module with `incoming chmod = Fo-x`.

State and persistence behavior: deliberately leaves umask at 002 for consistent transform semantics. Destination modes are the main persistent state.

Dependencies and integration points: chmod parser, receiver mode-setting logic, daemon incoming chmod handling, and harness permissions checks.

Risks and test signals: mode semantics depend on umask and platform permission behavior. Failures reveal parser mistakes, wrong F/D scoping, or daemon directory/file misclassification.
<!-- END_FILE_RESEARCH: sources/sync-backup/rsync/testsuite/chmod-option_test.py -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/rsync/testsuite/chmod-symlink-race_test.py -->
# sources/sync-backup/rsync/testsuite/chmod-symlink-race_test.py

Purpose: security regression for receiver-side chmod operations escaping through parent symlinks, delegated to the compiled helper `t_chmod_secure`.

Important APIs/types/functions: filesystem setup of `module`, `trap`, symlinks `inside_link` and `escape_link`, `subprocess.run([TOOLDIR/t_chmod_secure, mod])`, and final Python sentinel mode check.

Control flow: build in-module and outside sentinel files, symlink shapes expected by the helper, run `t_chmod_secure`, fail on helper error, then verify the outside sentinel mode remains `0600`.

State and persistence behavior: outside `trap/sentinel` mode is the security oracle; in-module paths provide positive and negative chmod targets.

Dependencies and integration points: compiled rsync test tool `t_chmod_secure`, receiver `do_chmod_at` hardening, and symlink path semantics.

Risks and test signals: relies on helper coverage for the detailed scenario enumeration. Failure means chmod escaped module confinement or helper detected another secure-chmod bug.
<!-- END_FILE_RESEARCH: sources/sync-backup/rsync/testsuite/chmod-symlink-race_test.py -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/rsync/testsuite/chmod-temp-dir_test.py -->
# sources/sync-backup/rsync/testsuite/chmod-temp-dir_test.py

Purpose: mirrors chmod transfer coverage while routing temp files through a different filesystem to force cross-filesystem rename fallback.

Important APIs/types/functions: `_fsdev`, `TOOLDIR/getfsdev`, `hands_setup`, `_try_chmods`, `checkit`, and `test_skipped`.

Control flow: prepare standard hands tree, find a writable temp directory on a different device than `SCRATCHDIR`, set varied file modes, run a normal copy with `--temp-dir`, then run an update with `-I --no-whole-file --temp-dir`.

State and persistence behavior: source mode metadata and destination content/modes are verified after temp-file copy/unlink fallback rather than same-filesystem rename.

Dependencies and integration points: `getfsdev` test tool, availability of another writable filesystem, rsync temp-dir code, and chmod preservation.

Risks and test signals: skips if no separate filesystem is available. Failures identify metadata/content loss in cross-device temp-file handling.
<!-- END_FILE_RESEARCH: sources/sync-backup/rsync/testsuite/chmod-temp-dir_test.py -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/rsync/testsuite/chmod_test.py -->
# sources/sync-backup/rsync/testsuite/chmod_test.py

Purpose: verifies transfer of varied read-only and special permission bits across whole-file and delta updates.

Important APIs/types/functions: `hands_setup`, `_try_chmods`, `os.chmod`, and two `checkit` calls for normal and `-I --no-whole-file` transfers.

Control flow: set modes on representative files in the hands tree, with fallbacks when special bits are refused. First sync normally, then force a delta update of all files.

State and persistence behavior: source file modes include read-only and setuid/setgid/sticky attempts; destination must preserve them through both transfer paths.

Dependencies and integration points: platform chmod permissions, rsync archive mode preservation, and harness tree comparison.

Risks and test signals: special bits may be downgraded by fallback setup. Failures indicate mode loss during initial copy or delta update.
<!-- END_FILE_RESEARCH: sources/sync-backup/rsync/testsuite/chmod_test.py -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/rsync/testsuite/chown_test.py -->
# sources/sync-backup/rsync/testsuite/chown_test.py

Purpose: verifies ownership preservation in real `--super` mode and, when invoked as the fake symlink variant, `--fake-super` ownership emulation via xattrs.

Important APIs/types/functions: script-name `fake_variant` detection, `xattrs_supported`, `xattr_set`, `RSYNC_PREFIX`, mutation of `rsyncfns.RSYNC` and `TLS_ARGS`, `chown_or_fake`, optional fakeroot re-exec, and `checkit`.

Control flow: select fake or real behavior. Fake mode encodes uid/gid in rsync fake-super `%stat` xattrs and adds `--fake-super`; real mode adds `--super` and may re-exec under `FAKEROOT_PATH`. Create two files, set distinct uid/gid pairs, then sync and compare.

State and persistence behavior: source ownership is either real inode uid/gid or fake-super xattr state. Destination listing must reflect the same ownership semantics.

Dependencies and integration points: root/fakeroot for real chown, xattr support for fake mode, rsync fake-super metadata, and harness listing.

Risks and test signals: skips if chown or xattrs are unavailable. Failures mean ownership metadata is not preserved or fake-super encoding is mishandled.
<!-- END_FILE_RESEARCH: sources/sync-backup/rsync/testsuite/chown_test.py -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/rsync/testsuite/clean-fname-underflow_test.py -->
# sources/sync-backup/rsync/testsuite/clean-fname-underflow_test.py

Purpose: regression for `clean_fname()` buffer underflow and mis-collapse when handling `..` in a crafted server-side merge filter name.

Important APIs/types/functions: direct rsync server invocation using the binary from `RSYNC`, `subprocess.run`, `--server --sender -vlr --filter=merge a/../test`, and `test_fail`.

Control flow: create a workdir with `mod`, run rsync in server sender mode with the crafted filter filename, discard output, then require a nonzero non-signal exit.

State and persistence behavior: no successful transfer state is expected. The tested state is parser/path-cleaning rejection without crash.

Dependencies and integration points: rsync internal server mode and filter merge-file path cleaning.

Risks and test signals: exit >=128 means crash; exit 0 means bogus input was accepted or mis-collapsed. Correct behavior is a clean nonzero rejection.
<!-- END_FILE_RESEARCH: sources/sync-backup/rsync/testsuite/clean-fname-underflow_test.py -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/rsync/testsuite/compare_test.py -->
# sources/sync-backup/rsync/testsuite/compare_test.py

Purpose: depth coverage for file comparison and skip options: default quick check, `-c`, `-I`, `--size-only`, and `--modify-window`.

Important APIs/types/functions: `seed`, `stealth_change`, `samesize_newmtime`, `run_rsync`, `assert_same`, and dry-run itemization checks.

Control flow: build and copy a depth-3 data tree. Create same-size same-mtime content changes and prove default quick check skips them, while checksum and ignore-times catch them. Then prove `--size-only` skips a same-size file even with changed mtime, while default catches it. Finally use dry runs to show `--modify-window=2` absorbs a one-second mtime difference.

State and persistence behavior: manipulates deep file content and mtimes to target selection decisions without changing path structure.

Dependencies and integration points: rsync generator quick-check logic, checksum comparison, size-only selection, modify-window itemization, and harness assertions.

Risks and test signals: timing is controlled via explicit `os.utime`. Failures distinguish wrong transfer selection from bad content copying.
<!-- END_FILE_RESEARCH: sources/sync-backup/rsync/testsuite/compare_test.py -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/rsync/testsuite/compress-options_test.py -->
# sources/sync-backup/rsync/testsuite/compress-options_test.py

Purpose: breadth coverage of compression and checksum option negotiation at depth without changing transfer results.

Important APIs/types/functions: JSON `-VV` parsing for `compress_list` and `checksum_list`, `fresh`, `verify`, `run_rsync`, `--debug=NSTR`, regex checks, and `assert_same`.

Control flow: for every advertised compressor except `none`, build a fresh depth-3 data tree, run `-az --compress-choice=ALGO --debug=NSTR`, assert debug output selected that compressor, and verify bytes. Then test `--compress-level=9`, `--skip-compress=gz`, every checksum algorithm with `-c --checksum-choice=ALGO`, and `--checksum-seed=12345`.

State and persistence behavior: repeatedly recreates source and destination, and injects a pseudo-gzip file for skip-compress. Destination content must remain byte-identical.

Dependencies and integration points: rsync algorithm negotiation, debug output contracts, compression/checksum lists from `-VV`, and data-tree helpers.

Risks and test signals: depends on debug text format. Failures mean requested algorithms were not negotiated or data was corrupted.
<!-- END_FILE_RESEARCH: sources/sync-backup/rsync/testsuite/compress-options_test.py -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/rsync/testsuite/compress-zlib-insert_test.py -->
# sources/sync-backup/rsync/testsuite/compress-zlib-insert_test.py

Purpose: regression for issue #951 in zlib delta uploads where inserting a large matched block into deflate history could overflow or leave pending output.

Important APIs/types/functions: `make_data_file`, daemon config, `start_test_daemon`, `rsync_argv('-zI', '--compress-choice=zlib', '--no-whole-file', '--block-size=65535')`, `filecmp.cmp`, and `test_fail`.

Control flow: create an 8 MiB incompressible source, copy it into daemon module as basis, alter a few bytes in source, start writable daemon, force a compressed delta upload with a block size larger than the deflate output buffer, then require success and byte-identical module file.

State and persistence behavior: module basis file and changed source trigger many matched-token inserts into compressor history. Final module file must equal source.

Dependencies and integration points: daemon connection, zlib compressor path, delta token generation, and block-size handling.

Risks and test signals: local transfers would skip the needed compression path, so daemon transport is essential. Failure is nonzero transfer or corrupt uploaded file.
<!-- END_FILE_RESEARCH: sources/sync-backup/rsync/testsuite/compress-zlib-insert_test.py -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/rsync/testsuite/copy-dest-source-symlink_test.py -->
# sources/sync-backup/rsync/testsuite/copy-dest-source-symlink_test.py

Purpose: daemon security regression for `--copy-dest` source opens escaping through a parent symlink in the alternate-destination path.

Important APIs/types/functions: daemon config, `start_test_daemon`, `rsync_argv('-rtp', '--copy-dest=cd')`, `filecmp.cmp`, uid/gid helpers, and scratch path setup.

Control flow: create module, outside directory, and source. Plant `module/cd -> outside`; make source `target.txt` same size/mtime/mode as outside but with different content. Push to daemon with `--copy-dest=cd`, then require destination exists, does not match outside content, and does match source content.

State and persistence behavior: content equality, not inode identity, is the oracle because copy-dest copies basis bytes. Outside content must never be read into module output.

Dependencies and integration points: daemon receiver copy-altdest path, secure source open behavior, and loopback daemon.

Risks and test signals: if destination is absent the test fails as vacuous. Matching outside content is a direct read-disclosure/escape signal.
<!-- END_FILE_RESEARCH: sources/sync-backup/rsync/testsuite/copy-dest-source-symlink_test.py -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/rsync/testsuite/crtimes_test.py -->
# sources/sync-backup/rsync/testsuite/crtimes_test.py

Purpose: verifies create-time preservation when rsync advertises crtimes support.

Important APIs/types/functions: `run_rsync('-VV')`, `_utime`, `rsyncfns.TLS_ARGS = '--crtimes'`, and `checkit(['-rtgvvv', '--crtimes', ...])`.

Control flow: skip without crtimes support. Create a directory and file, touch each first to an old time and then to a newer time to leave create time pinned on supporting systems, enable crtime-aware listing, and sync with `--crtimes`.

State and persistence behavior: source birth/create times are expected to be preserved and visible through the test listing.

Dependencies and integration points: filesystem/kernel create-time behavior, rsync crtimes support, and harness listing.

Risks and test signals: platform semantics for birth time can vary. Failure means crtime metadata was lost or listing comparison disagreed.
<!-- END_FILE_RESEARCH: sources/sync-backup/rsync/testsuite/crtimes_test.py -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/rsync/testsuite/cvs-exclude_test.py -->
# sources/sync-backup/rsync/testsuite/cvs-exclude_test.py

Purpose: depth coverage for `-C`/`--cvs-exclude`, including built-in CVS cruft patterns and scoped `.cvsignore`.

Important APIs/types/functions: `makepath`, `run_rsync('-aC')`, `assert_exists`, and `assert_not_exists`.

Control flow: create a four-level tree containing real `.c` files plus built-in cruft (`*.o`, `*~`) at each level. Add `.cvsignore` under `d1/d2` for `*.junk`, create both a scoped junk file and a top-level junk file, sync with `-C`, and verify only intended files are excluded.

State and persistence behavior: destination tree should contain real files and top-level junk while excluding built-in cruft and deep scoped junk.

Dependencies and integration points: rsync filter engine, CVS exclude defaults, per-directory `.cvsignore` scope.

Risks and test signals: failures identify incorrect built-in pattern handling or `.cvsignore` scope leakage.
<!-- END_FILE_RESEARCH: sources/sync-backup/rsync/testsuite/cvs-exclude_test.py -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/rsync/testsuite/daemon-access-ip_test.py -->
# sources/sync-backup/rsync/testsuite/daemon-access-ip_test.py

Purpose: real-TCP daemon coverage for numeric `hosts allow`/`hosts deny` exact-IP and CIDR matching, plus client `--address`.

Important APIs/types/functions: `require_tcp`, hand-written config, `start_test_daemon`, `connect(mod)`, `rsync_argv`, and `test_fail`.

Control flow: require TCP because stdio daemon has no peer IP. Build source tree and daemon modules with exact allow, CIDR allow, CIDR deny, and nonmatching allow rules. Start daemon, assert allowed modules connect and denied modules fail, then assert `--address=127.0.0.1` can bind and connect to the CIDR-allowed module.

State and persistence behavior: no data copy is required; connection success/refusal is the state under test.

Dependencies and integration points: rsync daemon access.c address matching, real loopback socket transport, and socket local bind.

Risks and test signals: global allow settings are intentionally omitted to avoid short-circuiting module rules. Failure means IP/CIDR ACL decisions or client bind behavior regressed.
<!-- END_FILE_RESEARCH: sources/sync-backup/rsync/testsuite/daemon-access-ip_test.py -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/rsync/testsuite/daemon-access_test.py -->
# sources/sync-backup/rsync/testsuite/daemon-access_test.py

Purpose: daemon module access-control coverage for read-only, read/write, write-only, hidden listing, and deep sub-path resolution.

Important APIs/types/functions: `write_daemon_conf`, `start_test_daemon`, `fails`, `run_rsync`, `verify_dirs`, `assert_same`, `walk_files`, and `rsync_argv`.

Control flow: build a depth-3 source and modules `ro`, `rw`, `wo`, and hidden `list=no`. Pull from read-only module and a deep sub-path, reject push to read-only, push to read/write, push to write-only and reject pull, inspect module listing for visible/hidden modules, then prove hidden module is still usable by explicit name.

State and persistence behavior: uses separate module backing directories for push/pull checks. Destination trees must match expected source paths.

Dependencies and integration points: daemon module permissions, module list generation, path resolution inside modules, and harness verify helpers.

Risks and test signals: allowed rsync code 23 is tolerated in some daemon transfers. Failures show access rule inversion, list leakage, or path resolution problems.
<!-- END_FILE_RESEARCH: sources/sync-backup/rsync/testsuite/daemon-access_test.py -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/rsync/testsuite/daemon-auth_test.py -->
# sources/sync-backup/rsync/testsuite/daemon-auth_test.py

Purpose: daemon authentication coverage for `auth users`, secrets files, password files, invalid credentials, and strict secrets-file modes.

Important APIs/types/functions: environment `RSYNC_PASSWORD`, `pwfile`, `push`, `write_daemon_conf`, `start_test_daemon`, `verify_dirs`, and `rsync_argv`.

Control flow: set a wrong fallback password to avoid interactive prompts, create an auth module with `tuser:secretpass`, push with correct password and verify data, push with wrong password and require rejection, try unauthenticated/invalid credentials with stdin closed and require rejection, then chmod secrets file world-readable and require strict-modes rejection.

State and persistence behavior: module backing directory is reset per push. Secrets file permissions are changed as part of the test.

Dependencies and integration points: daemon challenge/response auth, password-file handling, strict modes, and environment password fallback.

Risks and test signals: without fallback password the test could hang on `/dev/tty`. Failures indicate auth bypass, prompt behavior, or strict mode regression.
<!-- END_FILE_RESEARCH: sources/sync-backup/rsync/testsuite/daemon-auth_test.py -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/rsync/testsuite/daemon-chroot-acl_test.py -->
# sources/sync-backup/rsync/testsuite/daemon-chroot-acl_test.py

Purpose: regression for hostname-based daemon `hosts deny` matching when `daemon chroot` is enabled and reverse DNS resources may be absent inside the chroot.

Important APIs/types/functions: `require_tcp`, `_can_chroot`, optional `unshare --user --map-root-user` re-exec, `_client_hostname`, `write_conf`, `run_check`, `start_test_daemon`, and `test_xfail`/skip/fail helpers.

Control flow: require Linux TCP and chroot capability. Determine reverse hostname for 127.0.0.1, create a chroot with module root, start daemon once, then rewrite config between two scenarios: global reverse lookup and per-module reverse lookup only. In both cases, a pull should be denied with `@ERROR access denied`.

State and persistence behavior: daemon chroot directory contains module data; config file is rewritten per connection because rsyncd rereads it. Log output is printed for diagnosis.

Dependencies and integration points: real TCP peer address, chroot, NSS/reverse DNS behavior, daemon ACL evaluation, and module/global `reverse lookup`.

Risks and test signals: platform and privilege heavy, so many skips are legitimate. Failure means hostname deny was bypassed after chroot, matching the security advisory scenario.
<!-- END_FILE_RESEARCH: sources/sync-backup/rsync/testsuite/daemon-chroot-acl_test.py -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/rsync/testsuite/daemon-config_test.py -->
# sources/sync-backup/rsync/testsuite/daemon-config_test.py

Purpose: daemon config parser coverage for the `&include` directive and failure behavior for a module whose path does not exist.

Important APIs/types/functions: hand-written `rsyncd.conf`, included config file, `start_test_daemon`, `rsync_argv`, and `test_fail`.

Control flow: build source, write `included.conf` defining `inc-mod`, write main config with `&include included.conf` and a `badpath` module. Start daemon, prove `inc-mod` is reachable and appears in listing, then prove `badpath` refuses a connection.

State and persistence behavior: config files under scratch drive daemon module state. No final data copy is required.

Dependencies and integration points: params.c include parsing, daemon module listing, clientserver path failure.

Risks and test signals: failures show include directive regression or missing-path modules serving unexpectedly.
<!-- END_FILE_RESEARCH: sources/sync-backup/rsync/testsuite/daemon-config_test.py -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/rsync/testsuite/daemon-delete-stats_test.py -->
# sources/sync-backup/rsync/testsuite/daemon-delete-stats_test.py

Purpose: verifies daemon upload delete itemization and, for protocol >= 31, delete statistics.

Important APIs/types/functions: `build_rsyncd_conf`, `forced_protocol`, `start_test_daemon`, `rsync_argv('-a', '--delete', '-i', '--stats')`, and output substring checks.

Control flow: create source with `keep.txt` and destination with matching keep plus extra `delete.txt`, start daemon, upload with delete/itemize/stats, require success, require `*deleting   delete.txt`, and require `Number of deleted files: 1 (reg: 1)` unless protocol is pinned below 31.

State and persistence behavior: daemon destination loses one file; stdout/stderr is also an asserted protocol signal.

Dependencies and integration points: daemon receiver delete reporting, itemize output, stats message `NDX_DEL_STATS`, and protocol gating.

Risks and test signals: older forced protocols cannot receive the delete-stats count. Failures distinguish missing itemization from missing stats.
<!-- END_FILE_RESEARCH: sources/sync-backup/rsync/testsuite/daemon-delete-stats_test.py -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/rsync/testsuite/daemon-exec_test.py -->
# sources/sync-backup/rsync/testsuite/daemon-exec_test.py

Purpose: daemon hook coverage for `pre-xfer exec` and `post-xfer exec`, including environment variables and abort-on-pre-failure behavior.

Important APIs/types/functions: `script`, `wait_for`, `write_daemon_conf`, `start_test_daemon`, marker files, `rsync_argv`, and `test_fail`.

Control flow: create a source tree, marker directory, hook scripts that write `RSYNC_MODULE_NAME` and `RSYNC_EXIT_STATUS`, plus a failing pre-hook. Start daemon with `hook` and `failhook` modules. Push through `hook`, wait for marker files to contain `hook` and `0`, then push through `failhook` and require nonzero exit and no files written.

State and persistence behavior: marker files persist daemon-side hook environment observations; hook destination and fail destination show transfer side effects.

Dependencies and integration points: daemon exec hook invocation, environment population, asynchronous post-transfer timing, and module abort semantics.

Risks and test signals: post hook can race after client disconnect, hence polling. Failures mean hooks did not run, environment values changed, or failing pre-hook did not block writes.
<!-- END_FILE_RESEARCH: sources/sync-backup/rsync/testsuite/daemon-exec_test.py -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/rsync/testsuite/daemon-filter_test.py -->
# sources/sync-backup/rsync/testsuite/daemon-filter_test.py

Purpose: daemon-side filter and chmod coverage: `exclude`, `incoming chmod`, and `outgoing chmod` at depth.

Important APIs/types/functions: `write_daemon_conf`, `pull`, `assert_not_exists`, `assert_same`, `assert_mode`, `walk_files`, `rsync_argv`, and `test_fail`.

Control flow: build depth-3 tree and secret files, configure modules for exclude, incoming chmod `F600`, and outgoing chmod `Fg-r,Fo-r`. Pull filtered module and verify secrets absent but normal files present. Push into incoming module and check every file mode is 0600. Pull outgoing module and ensure group/other read bits are cleared on every file.

State and persistence behavior: destination backing directories show daemon-side mode rewriting and filter application.

Dependencies and integration points: daemon filter rules, incoming/outgoing chmod parameters, file mode preservation, and harness assertions.

Risks and test signals: loops check non-vacuous file counts. Failures indicate filters not applied at depth or chmod rewrite gaps.
<!-- END_FILE_RESEARCH: sources/sync-backup/rsync/testsuite/daemon-filter_test.py -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/rsync/testsuite/daemon-groupmap-wild_test.py -->
# sources/sync-backup/rsync/testsuite/daemon-groupmap-wild_test.py

Purpose: regression for issue #829 where daemon option argument escaping caused `--groupmap=*:<gid>` wildcard to be treated literally.

Important APIs/types/functions: group selection via `grp` or `os.getgroups`, `check(label, *extra_opts)`, `write_daemon_conf`, `start_test_daemon`, `rsync_argv('-rg', '--groupmap=*:<gid>')`, and `os.stat`.

Control flow: choose two usable group IDs, start writable daemon, then run two uploads: default args and `--secluded-args`. Each creates a source file with source group, uploads with wildcard groupmap, and asserts destination gid equals target group.

State and persistence behavior: destination file group ID is the oracle. Source/module directories are reset before each subcase.

Dependencies and integration points: daemon argument parsing/unescaping, groupmap receiver logic, safe_arg behavior, secluded args, and host group permissions.

Risks and test signals: skips when fewer than two usable groups exist. Failure means wildcard was ignored or escaped incorrectly over daemon protocol.
<!-- END_FILE_RESEARCH: sources/sync-backup/rsync/testsuite/daemon-groupmap-wild_test.py -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/rsync/testsuite/daemon-gzip-download_test.py -->
# sources/sync-backup/rsync/testsuite/daemon-gzip-download_test.py

Purpose: verifies compressed daemon downloads with high verbosity/double `-z` style compression options, covering an old doubly-compressed transfer bug.

Important APIs/types/functions: `build_rsyncd_conf`, `hands_setup`, `run_rsync`, `start_test_daemon`, and `checkit(['-avvvvzz', daemon-url, dest])`.

Control flow: build hands tree and expected `CHKDIR` excluding daemon global `foobar.baz`, start daemon, then download `test-from` with `-avvvvzz` and compare to expected tree.

State and persistence behavior: destination must match the expected filtered source tree.

Dependencies and integration points: daemon sender compression path, optional TCP transport through harness, and directory comparison.

Risks and test signals: allowed code 23 is tolerated. Failure indicates compressed daemon download corruption or protocol failure.
<!-- END_FILE_RESEARCH: sources/sync-backup/rsync/testsuite/daemon-gzip-download_test.py -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/rsync/testsuite/daemon-gzip-upload_test.py -->
# sources/sync-backup/rsync/testsuite/daemon-gzip-upload_test.py

Purpose: verifies compressed daemon uploads with high verbosity/double `-z` style compression options.

Important APIs/types/functions: `build_rsyncd_conf`, `hands_setup`, `run_rsync`, `start_test_daemon`, and `checkit(['-avvvvzz', source, daemon-url])`.

Control flow: build hands tree and expected `CHKDIR` excluding daemon global `foobar.baz`, start daemon, then upload to `test-to` with `-avvvvzz` and compare daemon destination to expected tree.

State and persistence behavior: daemon writable destination must match filtered source tree after compressed upload.

Dependencies and integration points: daemon receiver compression path, test daemon config, and harness comparison.

Risks and test signals: allowed code 23 is tolerated. Failure indicates compressed daemon upload corruption or transfer failure.
<!-- END_FILE_RESEARCH: sources/sync-backup/rsync/testsuite/daemon-gzip-upload_test.py -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/rsync/testsuite/daemon-munge_test.py -->
# sources/sync-backup/rsync/testsuite/daemon-munge_test.py

Purpose: daemon coverage for `munge symlinks = yes`, ensuring symlinks are stored safely with `/rsyncd-munged/` and unmunged on download.

Important APIs/types/functions: `make_tree`, `assert_is_symlink`, `write_daemon_conf`, `start_test_daemon`, `rsync_argv('-al')`, and `os.readlink`.

Control flow: create depth-3 source with deep symlink `d1/d2/sl -> f3`, configure writable munge module, push with links preserved and verify stored symlink target is `/rsyncd-munged/f3`. Then pull back and verify output symlink target is `f3`.

State and persistence behavior: module backing directory stores munged symlink target; pulled directory stores unmunged target.

Dependencies and integration points: daemon symlink munging, sender/receiver link handling, and symlink assertions.

Risks and test signals: failures mean unsafe symlink storage or missing unmunge on read.
<!-- END_FILE_RESEARCH: sources/sync-backup/rsync/testsuite/daemon-munge_test.py -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/rsync/testsuite/daemon-path-root-read_test.py -->
# sources/sync-backup/rsync/testsuite/daemon-path-root-read_test.py

Purpose: functional regression for daemon modules with `path = /` and `use chroot = no`, where secure sender open could reject absolute module-root paths with EINVAL.

Important APIs/types/functions: `write_daemon_conf`, `start_test_daemon`, `rsync_argv('-a', url-root-subpath, dest)`, `test_xfail`, and content checks.

Control flow: create a served subtree under scratch, configure a read-only daemon module rooted at `/`, request the served subtree by stripping the leading slash in the daemon URL, and inspect output. If the known `Invalid argument (22)` symptom appears, mark xfail. Otherwise require successful transfer and exact content for root and nested files.

State and persistence behavior: destination should receive `README` and `sub/deep.txt` from the absolute path served through root module.

Dependencies and integration points: daemon sender file open hardening, module-root path handling, and test xfail mechanism.

Risks and test signals: currently may xfail on affected versions. Unexpected nonzero exit or content mismatch after the known symptom is absent is a failure.
<!-- END_FILE_RESEARCH: sources/sync-backup/rsync/testsuite/daemon-path-root-read_test.py -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/rsync/testsuite/daemon-refuse-compress_test.py -->
# sources/sync-backup/rsync/testsuite/daemon-refuse-compress_test.py

Purpose: verifies a daemon module configured with `refuse options = compress` rejects compressed clients but still serves uncompressed clients.

Important APIs/types/functions: `build_rsyncd_conf`, appended module config, `start_test_daemon`, `rsync_argv('-avz')`, `checkit`, and stderr check for `--compress`.

Control flow: append `no-compress` module to base config, build hands tree and expected `CHKDIR`, start daemon, run a compressed download and require nonzero exit plus refusal text mentioning `--compress`, then run the same download without `-z` and compare to expected data.

State and persistence behavior: destination is reset between refused and allowed runs. Error output is persisted to `SCRATCHDIR/refuse.err`.

Dependencies and integration points: daemon refuse-options matching for aliases (`-z`/compress), module config, and harness comparison.

Risks and test signals: failure means compression was not refused or refusal blocked allowed transfers.
<!-- END_FILE_RESEARCH: sources/sync-backup/rsync/testsuite/daemon-refuse-compress_test.py -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/rsync/testsuite/daemon-refuse_test.py -->
# sources/sync-backup/rsync/testsuite/daemon-refuse_test.py

Purpose: broader daemon `refuse options` coverage for named options, wildcard patterns, and allow-list negation syntax.

Important APIs/types/functions: `write_daemon_conf`, `refused`, `allowed`, `verify_dirs`, `start_test_daemon`, `rsync_argv`, and `make_tree`.

Control flow: configure modules refusing `delete`, refusing `checksum*`, and allowing only `-a`/`-v` via `* !a !v`. Assert `--delete` push is refused but plain push succeeds, `--checksum` pull is refused by wildcard, `-av` pull is allowed, and `-avz` is refused by allow-list module.

State and persistence behavior: allowed cases verify actual destination data, not just exit code.

Dependencies and integration points: daemon option parser/refusal engine, wildcard option matching, negated allow-list semantics, and transfer verification.

Risks and test signals: failures indicate option names are not normalized/matched correctly or allowed transfers are falsely blocked.
<!-- END_FILE_RESEARCH: sources/sync-backup/rsync/testsuite/daemon-refuse_test.py -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/rsync/testsuite/daemon_test.py -->
# sources/sync-backup/rsync/testsuite/daemon_test.py

Purpose: basic daemon-mode listing and path coverage through both remote-shell daemon syntax and the test daemon transport.

Important APIs/types/functions: `fleet_nonroot`, `listed_paths`, `build_rsyncd_conf`, `start_test_daemon`, `run_and_check`, `run_rsync('-VV')`, `rsync_argv`, `RSYNC_PEER`, and support `lsh.sh --no-cd`.

Control flow: create source paths under `foo` and `bar`, ensure `rsyncd.conf` symlink, add `--config` when running as root, verify module listing through lsh and daemon includes expected modules and not `test-hidden`, recursively list hidden module by explicit name and compare exact path set, list `test-from/f*` glob and compare exact path set, and repeat glob listing with `-U` if atime support exists.

State and persistence behavior: no full copy is required; exact listing sets are the assertions. Hidden module remains usable by name while absent from module listing.

Dependencies and integration points: daemon module list generation, hidden module handling, glob expansion, remote-shell daemon invocation, optional atime listing format, fleet nonroot pass.

Risks and test signals: parser extracts last listing token and assumes no spaces in paths. Failures indicate listing leaks/omissions or glob path resolution regressions.
<!-- END_FILE_RESEARCH: sources/sync-backup/rsync/testsuite/daemon_test.py -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/rsync/testsuite/delay-updates-deep_test.py -->
# sources/sync-backup/rsync/testsuite/delay-updates-deep_test.py

Purpose: property-level depth coverage for `--delay-updates`, including stale per-directory staging cleanup.

Important APIs/types/functions: `make_tree`, `walk_files`, `walk_dirs`, `run_rsync('--delay-updates')`, `assert_same`, `no_staging_left`, and `test_fail`.

Control flow: build depth-3 data tree, run initial delayed update, verify every file and no `.~tmp~` directories. Then mutate every source file, plant stale `TODIR/d1/d2/d3/.~tmp~/f3`, rerun delayed update, verify all files match and no staging dirs remain.

State and persistence behavior: destination staging directories are transient state that must be cleaned. A stale staged file tests overwrite behavior.

Dependencies and integration points: receiver delayed-update staging, end-of-run rename, deep parent path handling, and harness assertions.

Risks and test signals: failures mean visible stale staging, missed update, or bad cleanup at depth.
<!-- END_FILE_RESEARCH: sources/sync-backup/rsync/testsuite/delay-updates-deep_test.py -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/rsync/testsuite/delay-updates_test.py -->
# sources/sync-backup/rsync/testsuite/delay-updates_test.py

Purpose: basic `--delay-updates` regression covering stale root staging file overwrite.

Important APIs/types/functions: `checkit`, `os.utime`, `FROMDIR`, `TODIR`.

Control flow: create source `foo=1`, sync with `--delay-updates`, then create `TODIR/.~tmp~/foo=2`, touch staged and visible files to a reference time, change source to `3`, and sync again. Both transfers compare destination to source.

State and persistence behavior: root-level `.~tmp~` staging content is deliberately stale and should not survive or corrupt the final file.

Dependencies and integration points: delayed-update receiver logic and harness directory comparison.

Risks and test signals: failure means stale staging content won or destination did not match source.
<!-- END_FILE_RESEARCH: sources/sync-backup/rsync/testsuite/delay-updates_test.py -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/rsync/testsuite/delete-deep_test.py -->
# sources/sync-backup/rsync/testsuite/delete-deep_test.py

Purpose: depth coverage for the delete family, `--max-delete`, `--existing`, `--ignore-existing`, and backup-delete handling of already-suffixed files.

Important APIs/types/functions: `seed_src`, `fresh_dest`, `make_tree`, `run_rsync`, `assert_not_exists`, `assert_exists`, `assert_same`, `makepath`, and `test_fail`.

Control flow: build depth-3 source and destination, add deep extraneous file/subtree, and verify `--delete` removes them. Repeat for delete timing variants. Add five extras and verify `--max-delete=2` leaves three. Verify `--existing` updates existing deep files but creates no new paths. Verify `--ignore-existing` preserves existing file content while creating missing files. Finally run `-b --delete --filter=R *~` and assert plain extra is backed up to `plain~` while already-suffixed `stale~` is unlinked without creating `stale~~`.

State and persistence behavior: destination extra paths, backup suffix files, and source/destination content are persistent test oracles.

Dependencies and integration points: delete traversal at depth, delete timing modes, max-delete exit behavior, selection flags, backup auto-protect/risk rules, and `is_backup_file`.

Risks and test signals: max-delete intentionally allows nonzero exit. Failures reveal deletion timing differences, limit enforcement bugs, or backup-delete suffix mishandling.
<!-- END_FILE_RESEARCH: sources/sync-backup/rsync/testsuite/delete-deep_test.py -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/rsync/testsuite/delete-missing-args-files-from_test.py -->
# sources/sync-backup/rsync/testsuite/delete-missing-args-files-from_test.py

Purpose: functional regression for `--delete-missing-args` with `--files-from` over daemon upload, covering missing file and directory entries.

Important APIs/types/functions: `write_daemon_conf`, `start_test_daemon`, `rsync_argv('-a', '--delete', '--delete-missing-args', '--files-from=...')`, `test_xfail`, and final filesystem assertions.

Control flow: create daemon module containing stale `keep.txt`, missing-on-sender `ghost.txt`, and `ghostdir`; create sender with only `keep.txt`; write files-from list containing all three names. Upload to daemon. If output shows known `invalid file mode 00`/protocol code 2 symptom while ghosts remain, mark xfail. Otherwise require success, ghosts deleted, and keep updated.

State and persistence behavior: module destination state is the oracle: missing args should be deleted and present file updated.

Dependencies and integration points: flist mode-0 missing entry handling, daemon receiver/generator delete logic, files-from, and xfail harness.

Risks and test signals: currently may xfail on affected versions. Unexpected failures after known symptom is absent indicate a different regression.
<!-- END_FILE_RESEARCH: sources/sync-backup/rsync/testsuite/delete-missing-args-files-from_test.py -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/rsync/testsuite/delete_test.py -->
# sources/sync-backup/rsync/testsuite/delete_test.py

Purpose: ported delete behavior coverage for dry-run output parity, `--remove-source-files`, and protect/exclude filter interaction with `--delete-excluded`.

Important APIs/types/functions: `hands_setup`, `_run_capture`, `_strip_chatter`, `checkit`, `rsync_argv`, `diff`, `makepath`, and `test_fail`.

Control flow: set up destination extras, capture output of a plain copy to `CHKDIR/copy`, capture output of `--del --dry-run` to `copy2`, strip chatter, and require output equality. Build `CHKDIR/empty` as directories-only source mirror. Run `--del --remove-source-files` and verify destination equals copy while source equals dirs-only mirror. Then create a per-dir filter file with `P foo` and `- bar`, plus excluded `baz`, run `--delete-excluded`, and verify protected foo survives while bar and baz are deleted.

State and persistence behavior: modifies both source and destination; remove-source-files should leave source files gone but directories present. Filter file state controls deletion.

Dependencies and integration points: delete dry-run output, source removal, filter protect/exclude semantics, and harness comparisons.

Risks and test signals: output comparison intentionally strips variable chatter. Failures identify user-visible dry-run drift, source cleanup bugs, or filter-protection errors.
<!-- END_FILE_RESEARCH: sources/sync-backup/rsync/testsuite/delete_test.py -->
