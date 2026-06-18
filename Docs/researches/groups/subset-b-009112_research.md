# Research Group: subset-b-009112

This grouped report covers bup external command tests and Python integration tests under `test/ext` and `test/int`. The files are primarily WvTest shell scripts and pytest modules that exercise bup repository commands against temporary Git repositories, generated source trees, metadata fixtures, remote-style transports, and platform-gated filesystem features.

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/bup/test/ext/test-ls -->
# sources/sync-backup/bup/test/ext/test-ls

Purpose: validates `bup ls` output for local and remote repositories, including short and long formats, hidden entries, classifier suffixes, numeric IDs, commit/tree hashes, symlinks, sockets, fifos, and time zone rendering. Important APIs are the shell helpers `bup()`, `with-tty()`, and `bup-ls()`, plus `bup init`, `index`, `save`, `tag`, `ls`, and Git log/tree lookups. Control flow builds a temp repo with a fixed timestamped tree, two saves, and one tag, then compares exact stdout across option combinations such as `-A`, `-a`, `-F`, `--file-type`, `-l`, `-n`, `-d`, `-s`, and `--commit-hash`. State is held in `BUP_DIR`/`GIT_DIR`, the temporary source tree, and Git refs for `src` and `.tag`. Dependencies include WvTest, `dev/mksock`, Perl date extraction, platform `ls`, `id`, and optional `dev/with-tty`. Risks are platform-specific symlink sizes, socket mode strings, NetBSD behavior, TTY truncation, and local timezone effects. Test signals are exact `WVPASSEQ` listings, hash equality against Git, and a 3000-line TTY listing check.
<!-- END_FILE_RESEARCH: sources/sync-backup/bup/test/ext/test-ls -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/bup/test/ext/test-ls-remote -->
# sources/sync-backup/bup/test/ext/test-ls-remote

Purpose: runs the normal `test-ls` suite through the remote-repository path by setting `BUP_TEST_REMOTE_REPO=1`. It has no custom APIs beyond delegating to `./test-ls`; the integration point is the conditional `bup-ls()` helper in that script, which switches to `bup ls -r "-:$BUP_DIR"`. Control flow is a thin wrapper: export the mode flag and exec the local test. State and persistence are inherited from `test-ls`; this wrapper only changes command routing, not fixture creation. Dependencies are the same WvTest and bup CLI dependencies as `test-ls`, plus remote syntax support for the `-:` local transport. The main risk is that a failure may appear in the delegated test while the actual regression is in remote argument handling or remote object streaming. Test signal is that every local `ls` assertion also passes over the remote transport.
<!-- END_FILE_RESEARCH: sources/sync-backup/bup/test/ext/test-ls-remote -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/bup/test/ext/test-main -->
# sources/sync-backup/bup/test/ext/test-main

Purpose: smoke-tests top-level `bup` option parsing and environment overrides. The important surface is the `bup()` wrapper around the repository executable and invocations of `bup --bup-dir=repo init` and `bup -d repo fsck`. Control flow creates a temp directory, initializes a repository through the long option form, then verifies the short `-d` form can find and check it. State is the `repo` directory under the temp workspace; no source tree is saved. Dependencies are minimal: WvTest, the bup command dispatcher, and Git repository initialization/checking. Risks are narrow but important because global option parsing runs before subcommand dispatch; regressions here can break every command. Test signals are successful initialization, `fsck`, and cleanup.
<!-- END_FILE_RESEARCH: sources/sync-backup/bup/test/ext/test-main -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/bup/test/ext/test-meta -->
# sources/sync-backup/bup/test/ext/test-meta

Purpose: exercises bup metadata archive creation/extraction and save/restore metadata fidelity across ordinary files, directories, hardlinks, ownership, atime, Linux attributes, xattrs, and POSIX ACLs. Important helpers include `genstat()`, `test-src-create-extract()`, `test-src-save-restore()`, `setup-test-tree()`, `setup-hardlink-test()`, and `hardlink-test-run-restore()`. Main APIs are `bup meta --create/--extract/--start-extract/--finish-extract/--edit`, `bup xstat`, `bup save -t`, `bup restore`, and comparison tools `compare-trees` and `hardlink-sets`.

Control flow first verifies metadata round trips for a sample tree and a top-level file, then validates save/restore metadata and a deeper subdirectory restore where only the destination top directory may differ. It checks that unchanged files use index metadata during later saves, then runs hardlink scenarios covering unchanged hardlinks, hardlink membership changes between index runs, membership changes between index and save, no linking outside a partial restore tree, and linking across separate saved subtrees. Later sections test metadata editing precedence for uid/gid/user/group, `--no-recurse`, empty metadata handling, unprivileged ownership restoration, privileged/fakeroot ownership restoration, and root-only loopback ext4/vfat coverage for atime, `chattr`, xattrs, and ACL failure reporting on limited filesystems.

State is persisted in temp `BUP_DIR` repositories, `.meta` files, Git commits, restored trees, hardlink inode relationships, and mounted loopback filesystems. Dependencies include root/fakeroot detection, `find`, `sort-z`, `xargs`, `mke2fs`, `mkfs`, `mount`, `chattr`, `attr`, `setfacl`, and platform filesystem support. Risks include timestamp resolution, observer effects around atime, root-only branches, SGID/group behavior, Cygwin owner limitations, hardlink restore boundaries, and error-count assertions on limited filesystems. Test signals are `diff` of `bup xstat` output, `compare-trees -c`, hardlink set diffs, expected `xstat` owner fields, and precise error-message counts.
<!-- END_FILE_RESEARCH: sources/sync-backup/bup/test/ext/test-meta -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/bup/test/ext/test-meta-acls -->
# sources/sync-backup/bup/test/ext/test-meta-acls

Purpose: provides focused POSIX ACL coverage for bup save/restore beyond the broader `test-meta` root-only path. Important APIs are `bup features`, `compare-trees --features`, `id-other-than`, `getfacl`, `setfacl`, `bup index`, `bup save`, `bup restore`, and `compare-trees -c`. Control flow gates on installed ACL tools and feature support, locates an alternate user/group, creates files and directories with user and group ACL entries plus default ACLs, records expected ACL behavior, and then runs `test-save-restore` for same-bup and optionally cross-bup restore paths via `BUP_TEST_OTHER_BUP`. State is the temp source tree ACL metadata and the restored tree ACL metadata. Dependencies are POSIX.1e ACL support in both bup and the comparison tool, plus available alternate IDs. Risks are platform support gaps, ACL inheritance differences, missing alternate users/groups, and cross-version compatibility when `BUP_TEST_OTHER_BUP` is set. Test signals are successful ACL creation, save/restore, and `compare-trees` agreement.
<!-- END_FILE_RESEARCH: sources/sync-backup/bup/test/ext/test-meta-acls -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/bup/test/ext/test-misc -->
# sources/sync-backup/bup/test/ext/test-misc

Purpose: collects broad command smoke tests for repository setup, bloom filters, memory tests, Git fsck compatibility, pack naming, FTP access, alternate index files, rsnapshot import, feature reporting, and owner lookup helpers. Important APIs are `bup init`, `random`, `index`, `save`, `bloom`, `memtest`, `split`, `ftp`, `ls`, `import-rsnapshot`, `features`, and `dev/id-other-than`. Control flow creates a baseline repo and saved tree, ruins and rebuilds bloom filters, runs `memtest`, repeatedly saves sample data and checks `git fsck --full --strict`, compares bup pack/index names with Git `index-pack`, reads saved files through `bup ftp`, verifies custom `INDEXFILE` exclusions, imports an rsnapshot-style tree, and checks reported Python version and owner lookup. State includes pack files, bloom files, index files, imported snapshot branches, and restored FTP output. Dependencies include Git plumbing, checksum helper, optional TTY support, and sample data. Risks are loose coupling of many commands in one script, Git fsck output changes, bloom corruption/rebuild expectations, and platform differences in interactive output. Test signals are WvTest pass/fail checks, SHA-1 comparisons, `fsck` empty/acceptable output, `ls` branch contents, and exact feature strings.
<!-- END_FILE_RESEARCH: sources/sync-backup/bup/test/ext/test-misc -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/bup/test/ext/test-on -->
# sources/sync-backup/bup/test/ext/test-on

Purpose: validates `bup on - ...` execution through the remote command transport while targeting the current machine. Important APIs are `bup on`, `index`, `save`, `split`, `join`, `restore`, Git `ls-tree`/`cat-file`, repository ID config, index-cache files, XDG cache handling, and pack suggestion output. Control flow initializes a repo, saves a source tree via `on -`, validates emitted tree/commit IDs and restores content locally, splits a file through `on -`, joins it back, checks cache paths under both default and custom `XDG_CACHE_HOME`, and exercises pack suggestion logging with a large file. State is the local `BUP_DIR`, command output in `get.log`, cache directories keyed by repo id, and restored files. Dependencies include SSH-like bup server/client code even though `-` keeps execution local, `compare-trees`, and Git plumbing. Risks include quoting and stdin/stdout routing through `on`, cache path isolation, and suggestions depending on repository pack state. Test signals are matching Git tree IDs, restored tree equality, joined file equality, expected cache entries, and successful debug invocations.
<!-- END_FILE_RESEARCH: sources/sync-backup/bup/test/ext/test-on -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/bup/test/ext/test-packsizelimit -->
# sources/sync-backup/bup/test/ext/test-packsizelimit

Purpose: verifies bup respects Git `pack.packSizeLimit` in local, remote, and `bup on` write paths. Important APIs are `git config pack.packSizeLimit`, `bup split -n`, `bup -d ... init`, remote `-r "-:$repo"` writes, and `bup on - split`. Control flow compares an unlimited 50k split against limited repositories, checks local versus remote config precedence, then validates `bup on` behavior where stdin mode fails under the limit but pathname mode succeeds and can be joined back. State is held in multiple temp repositories and generated pack files. Dependencies are Git config parsing, pack writer rollover, bup remote local transport, and random data generation. Risks include pack-size limits being advisory in Git, object count/size variance from chunking, and a known behavioral difference between `on` stdin and file argument modes. Test signals are successful or failed WvTest commands and byte-for-byte join output.
<!-- END_FILE_RESEARCH: sources/sync-backup/bup/test/ext/test-packsizelimit -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/bup/test/ext/test-redundant-saves -->
# sources/sync-backup/bup/test/ext/test-redundant-saves

Purpose: checks that repeated saves without meaningful changes do not create divergent tree objects or leave invalid index state. Important APIs are `bup init`, `index -u`, `save -t`, `index -m`, `index -s /`, and root-path saving. Control flow creates a temp source tree, indexes and saves it, checks the index modification listing is empty, saves the same tree again and compares tree IDs, then saves `/` after verifying no deleted root entries leak into status. State is the bup index, temporary source tree, and tree IDs printed by `save -t`. Dependencies are WvTest, root path traversal, and stable index metadata behavior. Risks are timestamp capping, parent directory metadata changing outside the test tree, and accidentally treating unchanged paths as modified. Test signals are equal tree IDs and empty/expected index status output.
<!-- END_FILE_RESEARCH: sources/sync-backup/bup/test/ext/test-redundant-saves -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/bup/test/ext/test-restore-map-owner -->
# sources/sync-backup/bup/test/ext/test-restore-map-owner

Purpose: root-only test for `bup restore` owner remapping options. Important APIs are `restore --map-user`, `--map-group`, `--map-uid`, `--map-gid`, `bup xstat`, `id-other-than`, and Python `pwd`/`grp` lookup for uid/gid zero. Control flow creates a saved file, restores it unchanged as a control, then restores with user/group mappings, verifies named mappings override numeric mappings, verifies numeric uid/gid mappings, and conditionally maps the current owner to root if uid/gid zero are present. State is the saved metadata and restored `dest/foo` ownership. Dependencies include root privileges, available alternate users/groups, and reliable `xstat` name/ID reporting. Risks are host account database variance, root/fakeroot behavior, and name-vs-ID precedence. Test signals are `bup xstat` output containing the expected user, group, uid, and gid fields.
<!-- END_FILE_RESEARCH: sources/sync-backup/bup/test/ext/test-restore-map-owner -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/bup/test/ext/test-restore-single-file -->
# sources/sync-backup/bup/test/ext/test-restore-single-file

Purpose: regression test for restoring a single file path from a save into an empty destination. Important APIs are `bup init`, `index`, `save -n`, `tick`, and `restore -C`. Control flow creates `foo/bar` and `foo/baz`, indexes the `foo` directory, saves it as branch `foo`, advances bup time, then restores only `baz` through a full VFS path. State is the small temp tree, the saved branch, and the restore directory. Dependencies are WvTest and normal bup path resolution. Risks are off-by-one path handling for a file target versus a directory target, especially when the save path includes the tempdir prefix. Test signal is successful restore command completion for the requested single file.
<!-- END_FILE_RESEARCH: sources/sync-backup/bup/test/ext/test-restore-single-file -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/bup/test/ext/test-rewrite -->
# sources/sync-backup/bup/test/ext/test-rewrite

Purpose: tests `bup get --rewrite` and related transfer behavior across repositories with different split settings and exclusions. Important helpers are `extract_all()` and `compare()`, plus a temporary Python override of `bup.metadata.Metadata._encode_common` that omits size fields. APIs include `bup get --append`, `--rewrite`, `--exclude-rx`, `--exclude-rx-from`, `split`, `index`, `save`, `restore`, `ls`, `join`, and Git tree inspection. Control flow initializes several repos, copies split objects, creates multiple saves, rewrites to a repo configured for tree splitting and smaller file split sizes, confirms unchanged remote transfer keeps tree identity, verifies rewrite after missing size metadata, excludes files during rewrite, excludes files already present in the source repo, and rewrites trees without `.bupm`. State spans multiple `BUP_DIR*` repositories, generated module overrides, save branches, rewritten object graphs, and restored comparison trees. Dependencies include Git config, bup import-module support, sample data, and regex exclusion logic. Risks are object-order completeness, metadata backward compatibility, excluded `.bupm` handling, and differences between copy and rewrite semantics. Test signals are `compare-trees`, matching or intentionally changed tree IDs, successful joins, and `ls-tree` assertions.
<!-- END_FILE_RESEARCH: sources/sync-backup/bup/test/ext/test-rewrite -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/bup/test/ext/test-rm -->
# sources/sync-backup/bup/test/ext/test-rm

Purpose: validates the dangerous `bup rm --unsafe` command for removing branches and individual saves while preserving remaining history and metadata. Important helpers are `compare-trees()`, `verify-changes-caused-by-rewriting-save()`, `commit-hash-n()`, and `rm-safe-cinfo()`. Control flow covers removing a lone branch, one branch among many, multiple branches, all branches, a lone save equivalent to branch removal, first/middle/last saves from a branch, and a save with a missing `.bupm`. State is a temp bup repository with several branches/saves, rewritten branch histories, and restored trees used to prove retained saves still match originals. Dependencies include Git commit inspection, bup VFS naming, compare-trees, and WvTest. Risks are accidental removal of too many refs, parent-chain rewrite errors, dangling/missing `.bupm` handling, and branch deletion edge cases. Test signals are exact `bup ls` output, commit hash expectations, compare-tree equality for retained saves, and successful validation of rewritten save metadata.
<!-- END_FILE_RESEARCH: sources/sync-backup/bup/test/ext/test-rm -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/bup/test/ext/test-rm-between-index-and-save -->
# sources/sync-backup/bup/test/ext/test-rm-between-index-and-save

Purpose: checks save behavior when files or directories disappear after indexing but before saving. Important APIs are `bup index`, `bup save`, `bup restore`, `ls`, and `diff`. Control flow has two scenarios: remove a file after indexing and save the parent tree; remove a directory after indexing and save the parent tree. It verifies the saved/restored tree reflects the actual filesystem at save time, not stale index entries. State is the bup index, mutable source tree, branch contents, and restore directory. Dependencies are WvTest, filesystem rename/delete semantics, and diff. Risks are stale index entries causing phantom restored paths, or save failures on missing indexed paths. Test signals are successful save/restore and directory listings/diffs that exclude removed entries.
<!-- END_FILE_RESEARCH: sources/sync-backup/bup/test/ext/test-rm-between-index-and-save -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/bup/test/ext/test-save-creates-no-unrefs -->
# sources/sync-backup/bup/test/ext/test-save-creates-no-unrefs

Purpose: regression test that `bup save` does not leave unreferenced objects behind. Important APIs are `bup init`, `index`, `save`, and validation through Git/bup repository checks. Control flow creates a small source tree, saves it, and inspects the repository for unreferenced objects after the save. State is only the temporary bup repo and saved branch. Dependencies are WvTest and Git object reachability checks. Risks are pack writer flush ordering and transient refs during save causing later garbage or `fsck` noise. Test signals are successful save and absence of unreferenced object reports.
<!-- END_FILE_RESEARCH: sources/sync-backup/bup/test/ext/test-save-creates-no-unrefs -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/bup/test/ext/test-save-data-race -->
# sources/sync-backup/bup/test/ext/test-save-data-race

Purpose: simulates a data race where a regular file changes between metadata capture and content hashing during `bup save`. Important APIs are a generated Python module that monkey-patches `bup.cmd.save` with `test_save_data_race_pause_save()`, an `instrumented-bup()` wrapper, and normal `index`/`save`/`restore` checks. Control flow creates a source file, indexes it, starts an instrumented save that pauses at a chosen file, mutates the file while the save is in progress, and verifies bup either records a consistent version or reports the intended race handling. State includes the temp source file, instrumented module path, save branch, and logs. Dependencies are Python import override support, timing/sleep coordination, and filesystem mtime/size behavior. Risks are flakiness from scheduling, timestamp resolution, and false positives if the write happens outside the critical window. Test signals are expected command status, diagnostics, and restored content consistency.
<!-- END_FILE_RESEARCH: sources/sync-backup/bup/test/ext/test-save-data-race -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/bup/test/ext/test-save-errors -->
# sources/sync-backup/bup/test/ext/test-save-errors

Purpose: verifies save error handling for metadata read failures and duplicate index entries. Important APIs are generated Python monkey patches of `bup.metadata.from_path`, a `DupReader(index.Reader)` subclass, `bup index`, `bup save`, and stderr assertions. Control flow initializes a repo, injects a metadata exception for a file and then for a folder, confirms save reports the failure path correctly, then injects duplicate index records to test duplicate-entry detection. State is the temp bup repo, source tree, generated override modules, and captured logs. Dependencies include `--import-py-module`, bup Python module internals, WvTest, and index reader behavior. Risks are brittle coupling to internal exception text, path quoting, and duplicate-index injection needing to match current index APIs. Test signals are failed saves with expected diagnostics and no silent success when metadata or index invariants are broken.
<!-- END_FILE_RESEARCH: sources/sync-backup/bup/test/ext/test-save-errors -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/bup/test/ext/test-save-restore -->
# sources/sync-backup/bup/test/ext/test-save-restore

Purpose: broad external test for save and restore command behavior, argument validation, branch naming, empty files, remote restore parity, no-index behavior, and disjoint top-level saves. Important helper `validate-local-and-remote-restore()` compares restore through local and remote repository syntax. APIs include `bup init`, `index`, `save`, `restore`, `split`, `ls`, `tick`, `random`, Git config for `bup.split.trees`, and `compare-trees`. Control flow builds a source tree, saves it, checks invalid save and restore arguments with expected error text, restores directories and empty split data, tests restoring via remote syntax, checks save behavior without an index, and verifies disjoint top-level directories can be saved and restored without collision. State is the temp source tree, bup index, branch `main`, split branch, restore directories, and error logs. Dependencies include WvTest, Git config parsing, sample filesystem operations, and local remote transport. Risks are exact error text drift, root path handling, branch-name validation, and interaction between no-index save and indexed save behavior. Test signals are expected failures, matching restored trees, empty file content, and successful local/remote restore comparisons.
<!-- END_FILE_RESEARCH: sources/sync-backup/bup/test/ext/test-save-restore -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/bup/test/ext/test-save-restore-excludes -->
# sources/sync-backup/bup/test/ext/test-save-restore-excludes

Purpose: validates exclusion semantics for both indexing and restoring, including literal paths, exclude files, regexes, root anchors, tail anchors, directory-only anchors, directory-content regexes, and regex-from files. Important APIs are `bup index --exclude`, `--exclude-from`, `--exclude-rx`, `--exclude-rx-from`, `bup save`, `bup restore --exclude-rx`, and filesystem listing comparisons. Control flow repeatedly constructs small trees with `foo` as file or directory, applies each exclusion form during index/save or restore, and compares resulting repository or restored tree contents. State includes exclusion files, bup index state, saved branches, and restore trees. Dependencies are regex engine behavior, path normalization, WvTest, and shell quoting. Risks are root-relative versus relative path ambiguity, directory trailing slash handling, and restore exclusions diverging from index exclusions. Test signals are exact `ls`/`find` outputs and expected absence or presence of `foo` and its children.
<!-- END_FILE_RESEARCH: sources/sync-backup/bup/test/ext/test-save-restore-excludes -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/bup/test/ext/test-save-smaller -->
# sources/sync-backup/bup/test/ext/test-save-smaller

Purpose: tests `bup save --smaller`, which saves only files smaller than a configured threshold. Important APIs are `bup random`, `index`, `save --smaller`, `restore`, `join`/checksums through `dev/checksum`, and `index --fake-valid`. Control flow creates files of different sizes, saves with thresholds, verifies only qualifying files appear in the backup, then marks index entries fake-valid to ensure size filtering still behaves under cached index metadata. State is the source tree, bup index, branch contents, and checksum files. Dependencies include deterministic random data generation and checksum helper. Risks are boundary handling around exact size thresholds and stale index metadata. Test signals are expected branch listings, restored content equality for included files, and excluded large files remaining absent.
<!-- END_FILE_RESEARCH: sources/sync-backup/bup/test/ext/test-save-smaller -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/bup/test/ext/test-save-strip-graft -->
# sources/sync-backup/bup/test/ext/test-save-strip-graft

Purpose: validates path rewriting options for `bup save`: `--strip`, `--strip-path`, and `--graft`, including collision detection. Important APIs are `bup index`, `save -n`, `restore`, `ls`, and `compare-trees`. Control flow creates source hierarchies, saves with strip modes for relative and absolute paths, verifies no-match behavior, checks invalid empty graft points, then tests grafts where source and destination path depths differ or map to root. It finishes with a collision case where rewritten paths would overlap. State is the source tree, rewritten branch layout, restore tree, and error logs. Dependencies include path normalization, absolute path handling, and WvTest. Risks are accidental path traversal, root mapping errors, duplicate destination entries, and inconsistent restore layout. Test signals are exact `bup ls` output, restored tree equality under expected target paths, and failed saves for invalid/colliding options.
<!-- END_FILE_RESEARCH: sources/sync-backup/bup/test/ext/test-save-strip-graft -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/bup/test/ext/test-save-symlink-race -->
# sources/sync-backup/bup/test/ext/test-save-symlink-race

Purpose: simulates a race where a symlink changes between metadata capture and content handling during save. Important APIs are a generated `bup.cmd.save` monkey patch with `test_save_symlink_race_pause_save()`, `instrumented-bup()`, symlink creation/replacement, and normal save/restore commands. Control flow indexes a tree containing a symlink, pauses save at the chosen path, mutates the symlink target, and verifies bup handles the metadata/content mismatch safely. State is the mutable symlink, temp repo, generated import module, and restore/log output. Dependencies include Python import override, symlink support, timing coordination, and WvTest. Risks are scheduler flakiness, filesystem timestamp resolution, and unsafe dereferencing of a changed symlink. Test signals are expected save status and restored symlink metadata/content consistency.
<!-- END_FILE_RESEARCH: sources/sync-backup/bup/test/ext/test-save-symlink-race -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/bup/test/ext/test-save-with-valid-parent -->
# sources/sync-backup/bup/test/ext/test-save-with-valid-parent

Purpose: regression test for saving a path whose parent directory is already up to date in the index. Important APIs are `bup index`, `save`, `restore`, and `compare-trees`. Control flow creates a nested source tree, indexes it, saves a child path with an up-to-date parent, then restores and compares the result to ensure parent validity does not suppress the requested child save. State is the bup index validity state, branch tree, and restored directory. Dependencies are WvTest and compare-trees. Risks are optimization logic skipping traversal when a parent is marked valid, producing incomplete saves. Test signal is restored tree equality with the original requested subtree.
<!-- END_FILE_RESEARCH: sources/sync-backup/bup/test/ext/test-save-with-valid-parent -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/bup/test/ext/test-sparse-files -->
# sources/sync-backup/bup/test/ext/test-sparse-files

Purpose: validates sparse-file restoration with `--sparse` and `--no-sparse` across all-zero files, sparse starts/ends/middles, boundary-sized zero runs, random content, and random sparse regions. Important APIs are `bup split`, `bup restore`, `bup random`, filesystem block-size detection, `du`/stat-style space checks, and an embedded Python generator for boundary cases. Control flow creates saved file objects with controlled zero and nonzero regions, restores them with different sparse options, verifies byte content, and compares allocated blocks against expectations. State is the repository object data, restored files, and filesystem allocation metadata. Dependencies include filesystem sparse support, block size assumptions, Python content generation, and WvTest. Risks are filesystem-dependent allocation, compression/chunk boundaries, short zero runs near buffer limits, and random data reproducibility. Test signals are content equality plus allocated-block checks that distinguish sparse from non-sparse restore behavior.
<!-- END_FILE_RESEARCH: sources/sync-backup/bup/test/ext/test-sparse-files -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/bup/test/ext/test-split-files-config -->
# sources/sync-backup/bup/test/ext/test-split-files-config

Purpose: verifies `bup.split.files` configuration for file chunk splitting in `split`, `split --noop`, and `save`. Important APIs are Git config `bup.split.files`, `bup split`, `--noop`, `--git-ids`, `save`, `ls-tree`, and regression fixtures for `legacy:13`, `legacy:16`, and `legacy:21`. Control flow confirms the default matches `legacy:13`, checks `--noop` behavior without a repo, compares known regression outputs for several split settings, and verifies saved object layouts under configured split sizes. State is Git config, split output hashes, pack objects, and saved tree entries. Dependencies are deterministic test input data, Git object IDs, and WvTest exact-output comparison. Risks are intentionally brittle hash expectations when split algorithms change, confusion between repo config and no-repo defaults, and save using different config than split. Test signals are exact object IDs and tree layouts for each configured split mode.
<!-- END_FILE_RESEARCH: sources/sync-backup/bup/test/ext/test-split-files-config -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/bup/test/ext/test-split-join -->
# sources/sync-backup/bup/test/ext/test-split-join

Purpose: broad external test for `bup split`, `join`, `midx`, `margin`, remote split, boundary handling, copy/noop modes, and empty data. Important APIs are `split --noop`, `--copy`, `-b`, `-t`, `-c`, `--keep-boundaries`, `--git-ids`, `--fanout`, `--max-pack-objects`, `join`, `midx`, `margin`, `ls`, and remote `-r`. Control flow verifies noop/copy produce no repository objects, handles short reads from a fifo, compares split IDs with and without boundary preservation, builds and checks midx files, creates tree/commit/tag outputs, exercises remote split writes, checks branch listing, then joins objects back to original files including an empty split. State is pack/midx files, split tag files, branch refs, and joined output files. Dependencies include sample test files, fifo support, Git object semantics, and WvTest. Risks are exact object ID drift from splitter changes, midx file ordering, remote/local parity, and empty input handling. Test signals are diffs against original files, expected tag counts, successful midx checks, and failed invalid command combinations.
<!-- END_FILE_RESEARCH: sources/sync-backup/bup/test/ext/test-split-join -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/bup/test/ext/test-tag -->
# sources/sync-backup/bup/test/ext/test-tag

Purpose: tests `bup tag` creation, deletion, validation, force deletion, and error handling. Important APIs are `bup tag`, `bup index`, `bup save`, Git `tag`, and stderr capture. Control flow saves sample data on branch `main`, verifies no initial tags, checks delete of missing tags with and without force, rejects missing target and invalid empty/dotted tag names, rejects nonexistent targets, creates `tag-1`, rejects duplicate creation, then deletes it. State is Git `refs/tags/*` in the bup repo. Dependencies are Git tag plumbing and bup VFS target resolution. Risks are tag name validation differences and accidentally leaving refs after failed commands. Test signals are exact `git tag` output and expected command failures.
<!-- END_FILE_RESEARCH: sources/sync-backup/bup/test/ext/test-tag -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/bup/test/ext/test-treesplit -->
# sources/sync-backup/bup/test/ext/test-treesplit

Purpose: validates tree-splitting saves with deterministic custom record boundaries and correct `.bupm` placement. Important APIs are Git config `bup.split.trees=true`, `bup save`, `bup ls`, Git `ls-tree`, and an imported Python replacement for `_helpers.RecordHashSplitter`. Control flow creates a source tree, configures tree splitting, injects a custom splitter that records boundaries, saves the tree, then verifies VFS listing, file-type suffixes, long listing timestamps, and recursive Git tree layout where `.bupm` metadata appears at expected split boundaries. State is the saved branch, split subtrees, `.bupm` entries, and custom module path. Dependencies include Python import override, Git tree inspection, and WvTest. Risks are splitter internals changing, hidden metadata ordering, and `.bupm` placement becoming inconsistent with VFS listing. Test signals are exact `bup ls` output and normalized `git ls-tree` paths.
<!-- END_FILE_RESEARCH: sources/sync-backup/bup/test/ext/test-treesplit -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/bup/test/ext/test-tz -->
# sources/sync-backup/bup/test/ext/test-tz

Purpose: verifies bup save naming and commit author timezone formatting for half-hour time zones. Important APIs are `TZ`, `bup save -d`, Git `cat-file commit`, and `bup ls`. Control flow sets `TZ=Australia/Adelaide`, saves an empty `src` directory with a fixed Unix timestamp, checks the Git commit author timestamp contains the expected `+1030` offset, and verifies `bup ls /src` uses the correct local save name. State is the saved branch and environment timezone. Dependencies are system timezone data and Git commit formatting. Risks are missing zoneinfo data or timezone conversion changes. Test signals are exact author timestamp suffix and save listing.
<!-- END_FILE_RESEARCH: sources/sync-backup/bup/test/ext/test-tz -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/bup/test/ext/test-validate-object-links -->
# sources/sync-backup/bup/test/ext/test-validate-object-links

Purpose: tests low-level object-link validation for missing Git objects referenced from a saved tree. Important APIs are `bup validate-object-links`, `bup index`, `save --strip`, Git `ls-tree`, `rev-parse`, and manual object removal. Control flow saves a nested tree, validates successfully, finds the `.bupm` object under `src:a`, deletes or hides the referenced object, then expects validation failure and checks diagnostics for the missing object/reference path. State is the Git object database and branch `src`. Dependencies include Git object layout, btl helpers for tree entries, and WvTest. Risks are object traversal order and exact diagnostic content. Test signals are successful validation before corruption and exit code 1 after object removal.
<!-- END_FILE_RESEARCH: sources/sync-backup/bup/test/ext/test-validate-object-links -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/bup/test/ext/test-validate-ref-links -->
# sources/sync-backup/bup/test/ext/test-validate-ref-links

Purpose: validates reference-level link checking and selective ref validation. Important helper `expect-one-src-missing()` asserts exactly one missing source reference diagnostic. APIs include `bup validate-ref-links`, `bup rm --unsafe`, `bup index`, `save --strip`, Git tree entry lookup, and stdout/stderr capture. Control flow creates a valid `src` branch and checks validation succeeds, corrupts or removes an object link to force one missing diagnostic, creates an additional `more` branch to verify selecting specific refs, then removes `src` and validates remaining refs. State is branch refs, object links, and validation logs. Dependencies are Git object/ref state and bup validation commands. Risks are false positives when unrelated refs are present and fragile counts in diagnostic output. Test signals are exit codes, empty output on valid refs, and expected missing-reference messages.
<!-- END_FILE_RESEARCH: sources/sync-backup/bup/test/ext/test-validate-ref-links -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/bup/test/ext/test-validate-refs -->
# sources/sync-backup/bup/test/ext/test-validate-refs

Purpose: integrates bup reference validation modes for object links and `.bupm` completeness. Important APIs are `bup validate-refs --links`, `--bupm`, default `validate-refs`, `index`, `save`, Git `mktree`, `commit-tree`, and `branch -f`. Control flow first checks correct refs pass all validation modes, then creates two saves, constructs a broken commit whose current tree reuses an older abridged `.bupm` entry, moves branch `src` to that commit, and expects validation failures. State is the `src` branch history, Git tree objects, and altered `.bupm` entry. Dependencies include Git tree editing and WvTest. Risks are exact tree structure assumptions and validators producing overlapping diagnostics. Test signals are zero output for valid refs and exit code 1 with logs for abridged metadata.
<!-- END_FILE_RESEARCH: sources/sync-backup/bup/test/ext/test-validate-refs -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/bup/test/ext/test-versioning-and-archive -->
# sources/sync-backup/bup/test/ext/test-versioning-and-archive

Purpose: verifies bup version strings and release archive behavior across clean/dirty release and non-release trees. Important APIs are Git clone/status/commit/archive, `./bup version`, `make check`, and unpacked tarball execution. Control flow clones the current repo, computes base/head version information, checks non-release clean and dirty suffix behavior, edits release-version state to check dirty and clean release strings, creates a `git archive` tarball, verifies archive version output, and runs `make check` in the unpacked archive. State is a cloned worktree, modified files, Git commits, and a tar archive. Dependencies include Git archive metadata, make, test suite availability, and version-generation scripts. Risks are dirty worktree detection, archive export losing Git metadata, and expensive `make check` runtime. Test signals are exact version strings with or without `+` and successful archive test run.
<!-- END_FILE_RESEARCH: sources/sync-backup/bup/test/ext/test-versioning-and-archive -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/bup/test/ext/test-walk-object-order -->
# sources/sync-backup/bup/test/ext/test-walk-object-order

Purpose: ensures object walking transfers dependencies before dependents so interrupted/missing-source cases do not leave unusable destination state. Important APIs are `bup get --ff`, `bup join`, `validate-object-links`-style object removal, Git `ls-tree`, and repository copying. Control flow creates a save, identifies a `.bupm` object likely to be late in traversal, copies the repo to a broken source with that object missing, verifies `get` and `join` fail from the broken source, then copies from the intact source and verifies `join` of the saved commit succeeds. State is the source repo, broken repo copy, destination repo, and missing object. Dependencies include Git object database layout and bup object walker ordering. Risks are relying on `.bupm` being late enough to expose ordering bugs and diagnostics varying by object type. Test signals are expected failure from broken source and successful transfer/join from intact source.
<!-- END_FILE_RESEARCH: sources/sync-backup/bup/test/ext/test-walk-object-order -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/bup/test/ext/test-web -->
# sources/sync-backup/bup/test/ext/test-web

Purpose: smoke-tests `bup web` with Tornado and HTTP clients, including UTF-8 branch names and optional non-UTF-8 path handling. Important APIs are `bup web`, `curl`, `wait-for-server-start()`, `bup init`, `index`, `save`, and HTTP GETs against the web server. Control flow gates on `curl`, available port behavior, and importable Tornado, saves a branch with a non-ASCII name, starts the web server in the background, waits for readiness, fetches pages/files, and conditionally tests non-UTF-8 content. State is the temp repo, background server process, saved branch, and fetched output. Dependencies include Tornado, curl, free localhost port, process cleanup, and UTF-8 locale behavior. Risks are flaky server startup, port conflicts, encoding differences, and cleanup after failure. Test signals are successful HTTP responses and expected page/file content.
<!-- END_FILE_RESEARCH: sources/sync-backup/bup/test/ext/test-web -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/bup/test/ext/test-xdev -->
# sources/sync-backup/bup/test/ext/test-xdev

Purpose: Linux root-only test for filesystem boundary exclusion using `-x`/xdev behavior in `drecurse`, `index`, `save`, and `restore`. Important APIs are loopback/bind mounts, `bup drecurse -x`, `bup index -x`, `save`, `restore`, and directory comparisons. Control flow creates mounted subtrees, verifies default recursion crosses mount points while `-x` excludes them, then tests index/save/restore with no `-x`, with `-x` excluding mounted subtrees, with explicit mount roots included, with symlink-to-mount paths, and with deeper nested mount arguments. State includes mount points, source trees, bup index, saved branches, and restored trees. Dependencies are root privileges, Linux mount support, WvTest, and cleanup unmounts. Risks are mount leakage on failure, symlink/mount identity confusion, and platform-only behavior. Test signals are exact `drecurse` output and restored tree listings matching the selected boundary policy.
<!-- END_FILE_RESEARCH: sources/sync-backup/bup/test/ext/test-xdev -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/bup/test/ext/test_argv.py -->
# sources/sync-backup/bup/test/ext/test_argv.py

Purpose: verifies argument byte preservation through the `test-argv` helper. Important APIs are `rand_bytes(n)`, `subprocess.check_output`, and WvTest `wvpasseq`. Control flow generates random byte strings of random lengths, passes them as process arguments to the helper, and checks the helper echoes exactly the expected argv encoding. State is ephemeral random input only; no repository is used. Dependencies include Python subprocess argument handling and the built `test-argv` binary/script on PATH. Risks are platform encoding differences, embedded NUL exclusion, and randomness making failures hard to reproduce without captured inputs. Test signal is exact byte-for-byte argv round trip.
<!-- END_FILE_RESEARCH: sources/sync-backup/bup/test/ext/test_argv.py -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/bup/test/ext/test_ftp.py -->
# sources/sync-backup/bup/test/ext/test_ftp.py

Purpose: pytest coverage for the interactive `bup ftp` command language. Important helpers are `bup()`, `jl()` for joined lines, and `match_rx_grp()` for regex-group assertions. APIs include `bup ftp` commands such as `ls`, `pwd`, `cd`, `cat`, `get`, `mget`, symlink handling, and error reporting. Control flow sets deterministic Git author/committer identity, builds a saved repository with files, directories, and symlinks, invokes `bup ftp` with scripted command input, and checks stdout/stderr for listings, data output, prompt behavior, and failures. State is the temp bup repo, saved branch, working directory, and downloaded files. Dependencies include pytest tmpdir, bup subprocess helpers, timezone formatting, and regex assertions. Risks are prompt/output formatting drift, pattern matching in `mget`, symlink resolution behavior, and locale/timezone effects. Test signals are exact or regex-matched command transcripts and restored/downloaded file content.
<!-- END_FILE_RESEARCH: sources/sync-backup/bup/test/ext/test_ftp.py -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/bup/test/ext/test_get.py -->
# sources/sync-backup/bup/test/ext/test_get.py

Purpose: exhaustive pytest matrix for `bup get` transfer semantics across copy/rewrite modes and optional transport dispositions. Important helpers include `rmrf()`, `verify_trees_match()`, `verify_rcz()`, regex validators, `validate_blob()`, `validate_tree()`, `validate_commit()`, `_get_save_coid()`, `_validate_save()`, `validate_save()`, `validate_new_save()`, `validate_tagged_save()`, `validate_new_tagged_commit()`, `_run_get()`, `run_get()`, `verify_only_refs()`, category functions `_test_universal`, `_test_replace`, `_test_ff`, `_test_append`, `_test_pick_common`, `_test_new_tag`, `_test_unnamed`, and `create_get_src()`.

Control flow creates a source repository with unrelated, zero, first, and second saves, branches, tags to blobs/trees/commits, saved working-tree copies, and known object IDs. Pytest parametrizes every selected disposition (`get`, and at higher `BUP_TEST_LEVEL`, `get-on`, `get-to`, `get-from`) across categories. The tests validate invalid arguments, missing sources, root fetch rejection, replacement of tags/branches, fast-forward rules, append rules for commit/save/tree sources, pick versus force-pick overwrite behavior, new-tag creation, unnamed object transfer, rewrite-specific restrictions, and implicit destination naming. Each transfer is followed by `bup fsck`, Git ref checks, archive comparison through `git archive`/`tar`, and bup restore comparison.

State includes `get-src`, `get-dest`, branch/tag refs, rewritten commits, restored trees, and deterministic commit metadata from environment variables. Dependencies are Git plumbing, tar, bup remote URL parsing, ssh-style local paths, pytest parametrization, and bup VFS path semantics. Risks are the large combinatorial surface, exact diagnostic regexes, branch/tag type confusion, rewrite producing new commit IDs, and test cost when remote dispositions are enabled. Test signals are exit codes, ref sets, object ID equality/inequality, clean fsck, restored tree equality, and expected error messages.
<!-- END_FILE_RESEARCH: sources/sync-backup/bup/test/ext/test_get.py -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/bup/test/ext/test_prune_older.py -->
# sources/sync-backup/bup/test/ext/test_prune_older.py

Purpose: generative pytest coverage for experimental `bup prune-older`. Important helpers are `create_older_random_saves()`, `expected_dispositions()`, `period_spec()`, `unique_period_specs()`, `period_spec_to_period_args()`, `utc_save_name()`, `check_prune_result()`, and `check_pretend_intent()`. APIs include `bup prune-older --unsafe`, `--keep-*-for`, `--wrt`, `--no-gc`, `--pretend`, Git commits/log/gc/reset, `period_as_secs()`, and `save_names_for_commit_utcs()`.

Control flow seeds randomness from `BUP_TEST_SEED`, creates thousands of Git commits with random timestamps over a three-year window and deliberate duplicates, then compares bup prune decisions against an independent expected-disposition algorithm. It first verifies no keep arguments fail without mutation, then runs many no-GC cycles with `--pretend` output checks and actual prune checks, then runs more expensive GC cycles by restoring a clean repo copy for each spec. A second test validates argument errors for missing `--unsafe`, missing keep options, non-integer `--wrt`, invalid period strings, zero periods, and very large period values.

State is a Git-backed bup repo in `work/.git`, the generated branch history, clean repo copies, random specs, and stderr/stdout intent logs. Dependencies include Git commit dating, localtime grouping, random seed control, and bup VFS save-name formatting. Risks are high runtime, randomness without seed capture, localtime/year/month/day boundary behavior, duplicate timestamp naming, and experimental command semantics. Test signals are exact branch commit timestamp lists after prune, exact pretend `+`/`-` intent lines, and expected validation diagnostics.
<!-- END_FILE_RESEARCH: sources/sync-backup/bup/test/ext/test_prune_older.py -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/bup/test/ext/test_split_trees.py -->
# sources/sync-backup/bup/test/ext/test_split_trees.py

Purpose: pytest test for large tree splitting through the external bup command. Important APIs are `bup.path.exe()`, `bup init`, Git config/environment, `bup save` with tree splitting enabled, and command helpers `exc`/`exo`. Control flow creates a large directory tree under pytest `tmpdir`, configures the repository for split trees, saves the tree, and validates the operation completes with expected repository output. State is the temp source tree, `BUP_DIR`, and saved branch. Dependencies include pytest tmpdir, bup executable lookup, and Git config. Risks are runtime/memory cost for large trees and sensitivity to tree-split thresholds. Test signal is successful save of a large tree without command failure.
<!-- END_FILE_RESEARCH: sources/sync-backup/bup/test/ext/test_split_trees.py -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/bup/test/int/__init__.py -->
# sources/sync-backup/bup/test/int/__init__.py

Purpose: marks `test/int` as a Python package for integration tests. It defines no APIs, functions, classes, control flow, or state. Persistence behavior is limited to the file's presence in the source tree, which can influence import/package discovery. Dependencies are Python's package import rules and the test runner's collection behavior. Risks are low; deleting or renaming it could change relative import behavior for tests or helper modules on older tooling. Test signal is implicit: pytest and local imports collect and run integration tests without package import errors.
<!-- END_FILE_RESEARCH: sources/sync-backup/bup/test/int/__init__.py -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/bup/test/int/sample.conf -->
# sources/sync-backup/bup/test/int/sample.conf

Purpose: fixture Git config file for `test_git.py` config parsing. Important data keys include `bup.foo=bar`, `bup.bup=is great`, `bup.end=end`, invalid-looking comment keys, boolean-like values, empty values, and integer/hex values. Control flow is declarative; `git.git_config_get()` reads it through Git config semantics during tests. State is static file content only. Dependencies are Git config syntax, including comment parsing and section/key normalization. Risks are accidental formatting changes altering Git's parsed output, especially comments, empty values, boolean aliases, and hex integer conversion. Test signals are `test_config()` assertions that expected keys resolve, invalid bool/int conversions raise `ConfigError`, missing keys return `None`, and typed values parse correctly.
<!-- END_FILE_RESEARCH: sources/sync-backup/bup/test/int/sample.conf -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/bup/test/int/test_bloom.py -->
# sources/sync-backup/bup/test/int/test_bloom.py

Purpose: tests the Python bloom filter reader/writer implementation. Important APIs are `BloomWriter`, `BloomReader`, a local dataclass fixture, and pytest tmpdir. Control flow writes bloom filters containing object IDs, reopens them, verifies membership and non-membership behavior, checks error handling for missing/corrupt files, and runs a larger bloom population path. State is the temporary bloom file and in-memory object IDs. Dependencies include `bup.bloom`, Python file IO, errno constants, and pytest. Risks are probabilistic false positives, file format compatibility, large-filter memory cost, and platform-specific error codes. Test signals are membership assertions, expected exceptions, and successful large bloom read/write.
<!-- END_FILE_RESEARCH: sources/sync-backup/bup/test/int/test_bloom.py -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/bup/test/int/test_client.py -->
# sources/sync-backup/bup/test/int/test_client.py

Purpose: integration tests for bup client/server pack transfer, suggestions, deduplicated writes, midx refreshing, legacy cache IDs, and config parsing. Important helpers are `randbytes()`, `local_writer()`, and `subproc_client()`. APIs include `bup.client`, `LocalRepo`, `client.Client`, server subprocess mode, `git.PackWriter`, `PackIdxList`, `midx`, `ConfigError`, and `URL`. Control flow writes random objects, tests server-side split with indexes, verifies multiple pack suggestions, checks dumb client/server conflict behavior, parametrizes deduplication by explicit mode or config, validates midx refresh after new packs, parses legacy cache identifiers, and verifies remote/client configuration handling. State includes temporary repositories, pack files, midx files, client caches, and environment `BUP_DIR`. Dependencies are subprocess bup server execution, Git object storage, random data, pytest, and URL parsing. Risks are race-like cache refresh behavior, config precedence, dedup mode differences, and subprocess cleanup. Test signals are object existence, pack count/size expectations, raised `ConfigError`, and successful client operations.
<!-- END_FILE_RESEARCH: sources/sync-backup/bup/test/int/test_client.py -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/bup/test/int/test_commit.py -->
# sources/sync-backup/bup/test/int/test_commit.py

Purpose: tests commit parsing, GPG signature parsing, Git date string formatting, and trailer detection. Important APIs are `parse_commit`, `_git_date_str`, `has_trailers`, `git`, and buptest command helpers. Control flow creates commits with controlled environment identities and messages, parses commit objects back into structured fields, verifies multi-parent/message behavior, tests commits containing `gpgsig` blocks, checks date string formatting for offsets, and validates trailer detection on message bodies. State is a temporary Git/bup repository and generated commit objects. Dependencies include Git commit-tree behavior, environment author/committer variables, timezone offsets, and WvTest assertions. Risks are Git output format drift, signature indentation rules, and false trailer positives. Test signals are exact parsed fields, expected signature content, formatted date strings, and boolean trailer outcomes.
<!-- END_FILE_RESEARCH: sources/sync-backup/bup/test/int/test_commit.py -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/bup/test/int/test_config.py -->
# sources/sync-backup/bup/test/int/test_config.py

Purpose: tests config URL resolution for remote options. Important APIs are `bup.config`, `bup.url.URL`, `IPv4Address`, and `IPv6Address`. Control flow constructs remote option values and expected URL objects, including local paths, host/path forms, IPv4/IPv6 addresses, and port/user variants, then checks `url_for_remote_opt` behavior. State is in-memory URL/config objects only. Dependencies are Python `ipaddress`, bup URL parsing/rendering, and pytest-style assertions. Risks are ambiguous colon syntax between local paths and host URLs, IPv6 bracket handling, and default scheme/user behavior. Test signals are equality of returned `URL` objects and parsed address fields.
<!-- END_FILE_RESEARCH: sources/sync-backup/bup/test/int/test_config.py -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/bup/test/int/test_git.py -->
# sources/sync-backup/bup/test/int/test_git.py

Purpose: comprehensive integration tests for bup's Git abstraction layer. Important APIs include `git.is_suitable_git`, `require_suitable_git`, `mangle_name`, `demangle_name`, `_encode_packobj`, `_decode_packobj`, `PackWriter`, `PackIdxV2Writer`, `PackIdxV2`, `PackIdxList`, `establish_default_repo`, `check_repo_or_die`, `get_commit_items`, `list_refs`, `catpipe`, `auto_midx`, `parse_git_int`, `git_config_get`, and `repo_config_file`. Helpers are `local_writer()`, `check_establish_default_repo_variant()`, and `_create_idx()`.

Control flow validates Git version classification and override env behavior, bup filename mangling for `.bup*` suffixes and chunked metadata, pack object encoding/decoding including compression level validation, pack writing/aborting/index lookups, source pack name lookup, long pack offsets, repository establishment and failure exit codes for invalid repo paths, commit creation/parsing with timezone offsets, listing refs filtered by heads/tags including blob/tree tags, catpipe data and metadata modes, midx refresh closing deleted file descriptors on `/proc/self/fd` systems, Git integer parsing with suffixes and bounds, and config-file typed reads using `sample.conf`.

State includes temporary bup repos, pack/idx/midx files, global `git.repodir`, environment `BUP_DIR`, generated commits/refs/tags, and sample config values. Dependencies are Git, `/proc/self/fd` for one skipped test, pytest, WvTest, and bup helpers. Risks are global repo state leakage, file descriptor leaks, Git version output changes, config parsing differences, and exact exit-code assumptions. Test signals are WvTest equality checks, raised `ConfigError`/`SystemExit`, object existence lookups, parsed commit fields, and descriptor state after midx refresh.
<!-- END_FILE_RESEARCH: sources/sync-backup/bup/test/int/test_git.py -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/bup/test/int/test_hashsplit.py -->
# sources/sync-backup/bup/test/int/test_hashsplit.py

Purpose: tests bup's rolling hash and content-defined chunk splitting implementations. Important APIs are `bup.hashsplit`, `_helpers`, `HashSplitter`, `RecordHashSplitter`, `BUP_BLOBBITS`, `fanout`, and `BytesIO`. Control flow checks sample split outputs, rolling sum values, fanout behavior, file splitting against temporary inputs, split boundary calculations for several bit settings, object-oriented `HashSplitter` iteration, and short-read behavior. State is in-memory byte streams, temporary files, generated blobs/trees, and splitter counters. Dependencies include C helper bindings, Python hashsplit wrapper, math, and WvTest. Risks are algorithm compatibility because expected boundaries encode historical behavior, especially the documented ignored bit between levels, and short reads from file-like objects. Test signals are exact chunk boundaries, fanout levels, object IDs/counts, and stable iteration results.
<!-- END_FILE_RESEARCH: sources/sync-backup/bup/test/int/test_hashsplit.py -->
