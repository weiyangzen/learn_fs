# subset-b-009133 research

Grouped research report for Git LFS shell tests in `sources/sync-backup/git-lfs/t`. Each section title preserves the exact source path and is wrapped for reconciliation into source-tree-aligned per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/git-lfs/t/t-migrate-import.sh -->
# sources/sync-backup/git-lfs/t/t-migrate-import.sh

Purpose: broad integration coverage for `git lfs migrate import`, the destructive history-rewrite command that converts selected Git blobs into LFS pointer files and populates `.git/lfs/objects`. It checks default-branch behavior, explicit refs, bare repositories, `--everything`, include/exclude path filters, ref include/exclude filters, `--skip-fetch`, tags, `--above`, `--object-map`, dirty worktrees, nonstandard refs, copied files, symlinks, and special-character paths.

Important APIs/functions: sources `fixtures/migrate.sh` plus `testlib.sh`; uses fixture builders such as `setup_multiple_local_branches`, `setup_multiple_remote_branches`, `setup_single_local_branch_untracked`, `setup_local_branch_with_gitattrs`, `setup_local_branch_with_symlink`, and remote/multiple-remote setup helpers. Assertions are mostly `assert_pointer`, `refute_pointer`, `assert_local_object`, `refute_local_object`, `assert_ref_unmoved`, `git cat-file`, `git rev-parse`, `git check-attr`, `git ls-tree`, and `diff`.

Control flow: each `begin_test` creates an isolated repository, captures original blob OIDs and ref positions, runs `git lfs migrate import` with a specific option set, then validates rewritten refs, pointer contents, generated `.gitattributes`, local LFS object presence, hook installation, object maps, and command failures for invalid option combinations or refs. Several tests rerun the same migration or loop across path filter cache sizes to assert idempotency and cache-independent behavior.

State/persistence behavior: this suite intentionally mutates Git history, branch/tag refs, `.gitattributes`, the LFS object cache, hooks under `.git/hooks`, and optionally an object-map file. It also verifies state that must not change: untouched remote refs, excluded branches, symlinked `.gitattributes`, empty commits, multi-remote branch tips, and denied dirty-copy migrations.

Dependencies/integration points: integrates with Git revision walking, ref selection, fast-import rewriting, Git attributes, LFS clean/pointer generation, filesystem mode bits, symlink handling, Windows path conversion guards, and fixture-created bare/local/remote repositories.

Risks/test signals: failures indicate history rewrite data loss, wrong path/ref selection, missing LFS objects, broken `.gitattributes` synthesis, unintended ref movement, unsafe dirty-worktree overwrites, or platform-specific path/mode regressions. Many assertions depend on exact command output and exact pointer size/OID values, so formatting changes can produce noisy failures even when core migration behavior is intact.
<!-- END_FILE_RESEARCH: sources/sync-backup/git-lfs/t/t-migrate-import.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/git-lfs/t/t-migrate-info.sh -->
# sources/sync-backup/git-lfs/t/t-migrate-info.sh

Purpose: read-only reporting coverage for `git lfs migrate info`. It verifies that the command summarizes candidate migration data by file pattern, size, count, percentage, pointer-following mode, threshold, top-N limit, units, and `--fixup` semantics without rewriting refs.

Important APIs/functions: sources `fixtures/migrate.sh` and `testlib.sh`; uses the same migration fixtures as import tests, then compares `git lfs migrate info` output with here-doc expectations via `diff -u`, `tail`, `wc`, and `grep`. It uses `assert_ref_unmoved` around `git rev-parse` snapshots to enforce read-only behavior.

Control flow: tests set up local, remote, bare, tracked, corrupt-tracked, nested, alternate-name, and symlinked-attribute repositories. Each test runs `git lfs migrate info` with options such as explicit refs, `--include`, `--exclude`, `--include-ref`, `--exclude-ref`, `--skip-fetch`, `--above`, `--top`, `--unit`, `--everything`, `--pointers=follow|no-follow|ignore`, and `--fixup`, then compares only the relevant output tail or validates an empty result.

State/persistence behavior: no migration state should be persisted. The suite repeatedly records `HEAD`, local branches, feature branches, and remote refs before and after reporting. It also validates that failure cases, such as symlinked `.gitattributes` or invalid refs/options, leave tree and ref state unchanged.

Dependencies/integration points: exercises Git revision traversal, Git attribute matching, LFS pointer parsing, report aggregation, size formatting, tracked-versus-untracked file classification, remote ref discovery, and command-line validation. `--fixup` specifically depends on attribute evaluation to identify files that should already be LFS pointers but are not.

Risks/test signals: failures show as output drift, incorrect aggregation, read-only commands moving refs, bad pointer-following semantics, or bad validation for incompatible options. Because many tests assert tabular formatting exactly, legitimate presentation changes need coordinated test updates.
<!-- END_FILE_RESEARCH: sources/sync-backup/git-lfs/t/t-migrate-info.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/git-lfs/t/t-multiple-remotes.sh -->
# sources/sync-backup/git-lfs/t/t-multiple-remotes.sh

Purpose: validates LFS object download behavior when a repository has multiple remotes and checkout/reset/pull/rebase/cherry-pick operations refer to objects hosted by a remote other than the current branch's remote.

Important APIs/functions: `prepare_consumer`, `prepare_forks`, and `exec_fail_git` are local helpers layered over `setup_remote_repo`, `git remote add`, `git fetch`, `git lfs track`, `git push`, and normal Git porcelain. The key configuration knobs are `lfs.remote.searchall` and `lfs.remote.autodetect`.

Control flow: `prepare_forks` creates two bare remotes, a main consumer that pushes an LFS-tracked `a.bin` to both remotes and then only to the main remote, and a fork consumer that fetches both. The first six tests enable either autodetection or search-all and expect reset, pull, checkout, rebase, sparse-checkout add, and cherry-pick to hydrate the object successfully. The second six disable both and require the same operations to fail through `exec_fail_git`.

State/persistence behavior: remote refs and local tracking refs are the tested state. LFS object presence differs between the main and fork endpoints, so success requires the LFS transfer layer to infer the correct endpoint from Git operation metadata rather than from the checked-out branch alone.

Dependencies/integration points: requires Git 2.27 or newer for treeish metadata used by autodetection. Integrates Git remote configuration, sparse checkout, branch tracking, cherry-pick/rebase object checkout, and LFS remote endpoint selection.

Risks/test signals: regressions either accept a download from the wrong remote configuration or reject valid cross-remote operations. The tests are sensitive to Git version behavior and to fixture server path handling through `file://` URLs.
<!-- END_FILE_RESEARCH: sources/sync-backup/git-lfs/t/t-multiple-remotes.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/git-lfs/t/t-no-remote.sh -->
# sources/sync-backup/git-lfs/t/t-no-remote.sh

Purpose: verifies LFS smudge/archive behavior in bare repositories that fetch from a URL without configuring a persistent remote, and ensures the `FETCH_HEAD` fallback is ignored once a real remote exists.

Important APIs/functions: uses `setup_remote_repo_with_file`, bare `git init`, direct `git fetch <url> refs/heads/main:refs/heads/main`, `git archive`, `tar -tvf`, and ordinary remote configuration via `git remote add origin`.

Control flow: the first test creates a source repo containing an LFS-tracked file, fetches it into a bare destination with no remote, archives the fetched revision, and expects the archive to include the hydrated file. The second creates two source repos, configures origin to repo A, then fetches repo B directly; `git archive` for repo A's revision must use origin instead of the newer `FETCH_HEAD` fallback.

State/persistence behavior: the important state is remote configuration versus transient `FETCH_HEAD`, plus the bare repository's refs. The archive output demonstrates whether LFS can resolve the needed object endpoint without a checked-out worktree.

Dependencies/integration points: integrates `git archive` filter behavior, bare repository operation, LFS URL fallback selection, fixture Git server URLs, and tar inspection.

Risks/test signals: failures mean archives from bare repos can miss LFS content or can leak endpoint selection from an unrelated direct fetch. The second test is subtle because it expects the first repo's file to appear and the second repo's file not to appear.
<!-- END_FILE_RESEARCH: sources/sync-backup/git-lfs/t/t-no-remote.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/git-lfs/t/t-object-authenticated.sh -->
# sources/sync-backup/git-lfs/t/t-object-authenticated.sh

Purpose: checks that uploading an LFS object to an authenticated remote path works when terminal prompts are disabled, which exercises credential handling in noninteractive environments.

Important APIs/functions: uses `ensure_git_version_isnt` to require Git 2.3 or newer for `GIT_TERMINAL_PROMPT`, plus `setup_remote_repo`, `clone_repo`, `git lfs track`, `git commit`, and `git lfs push`.

Control flow: the test creates and clones a remote named from the script, tracks `*.dat`, writes `hi.dat`, commits `.gitattributes` and the file, then runs `GIT_CURL_VERBOSE=1 GIT_TERMINAL_PROMPT=0 git lfs push origin main`.

State/persistence behavior: the repository gains one LFS-tracked blob and its pointer commit. The remote LFS store should receive the object without needing interactive credential prompts.

Dependencies/integration points: integrates Git credential behavior, HTTP/curl verbosity, test server authentication defaults, LFS batch upload, and noninteractive environment variables.

Risks/test signals: the test has no explicit object assertion; command success is the signal. A failure usually points to authentication prompt leakage, missing credentials, or transfer setup regressions.
<!-- END_FILE_RESEARCH: sources/sync-backup/git-lfs/t/t-object-authenticated.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/git-lfs/t/t-path.sh -->
# sources/sync-backup/git-lfs/t/t-path.sh

Purpose: security regression tests ensuring Git LFS does not execute a malicious `git` or PATHEXT-derived binary from the current working directory when resolving Git or credential-helper commands.

Important APIs/functions: uses `lfstest-badpathcheck`, `$BINPATH`, `$X`, `PATHEXT`, `PATH`, `GODEBUG=execerrdot=0`, `git lfs env`, `git lfs pull`, `git lfs uninstall/install`, credential-helper execution paths, and file checks for an `exploit` marker.

Control flow: the first test places a malicious `git` in the repo and runs `git-lfs env` with a restricted PATH, then asserts no exploit output or file appears. The credential test commits the malicious binary into an LFS repo, reclones with smudge disabled by temporarily uninstalling LFS, then runs `git-lfs pull` from a checkout containing the malicious binary to catch both general Git lookup and credential-helper lookup. The Windows-only PATHEXT test creates dummy `git.exe` and malicious `.exe`-style files to ensure fallback extension probing does not execute the wrong file.

State/persistence behavior: the tests deliberately create and sometimes commit suspicious executables, remove them from the worktree, and inspect generated logs plus the absence of an `exploit` file. The intended persistent state is normal LFS object storage, not execution side effects.

Dependencies/integration points: depends on Go `os/exec` path behavior, Git for Windows PATHEXT semantics, credential helpers, clone/smudge/pull filter invocation, and test binaries in `$BINPATH`.

Risks/test signals: failures are high severity because they imply current-directory command execution. The tests are platform-sensitive and carry comments documenting Go 1.19 `execerrdot` behavior to avoid false failures during setup.
<!-- END_FILE_RESEARCH: sources/sync-backup/git-lfs/t/t-path.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/git-lfs/t/t-pointer.sh -->
# sources/sync-backup/git-lfs/t/t-pointer.sh

Purpose: command-line coverage for `git lfs pointer`, including pointer generation, pointer parsing, comparison, strict validation, stdout/stderr routing, and extension-aware pointer generation.

Important APIs/functions: uses `git lfs pointer` flags `--file`, `--stdin`, `--pointer`, `--check`, `--strict`, `--no-strict`, `--compare`, and `--no-extensions`; helper functions include `is_stdin_attached`, `setup_case_inverter_extension`, `calc_oid`, `invert_case`, and `$LFSTEST_EXT_LOG`.

Control flow: early tests compare generated pointer text for file input and STDIN, including match/mismatch cases and missing or malformed pointer files. Validation tests run `--check` against valid pointers, invalid text, empty files, zero-size pointers, CRLF pointers, and invalid flag combinations. Output-routing tests ensure pointer payload goes to stdout while labels go to stderr when redirected. Extension tests configure a case-inverter extension, confirm warning and `ext-0-caseinverter` lines, compare extension versus no-extension pointers, and verify extension clean invocations across multiple files.

State/persistence behavior: most tests create temporary files in fresh repos and compare deterministic SHA-256 OIDs, Git blob OIDs, status codes, and extension logs. Extension cases persist `.gitattributes` and extension configuration, and then check whether transformation logs were or were not written.

Dependencies/integration points: integrates pointer parser/serializer code, Git blob hashing, LFS extension clean filters, terminal/stdin detection, CRLF tolerance, and command validation.

Risks/test signals: regressions include invalid pointers accepted, valid pointers rejected, wrong exit status, broken stream separation, incorrect extension OIDs, or missing mismatch diagnostics. Exact output expectations make this suite sensitive to wording and formatting changes.
<!-- END_FILE_RESEARCH: sources/sync-backup/git-lfs/t/t-pointer.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/git-lfs/t/t-post-checkout.sh -->
# sources/sync-backup/git-lfs/t/t-post-checkout.sh

Purpose: verifies the Git LFS post-checkout hook updates lockable-file permissions correctly after clone, branch checkout, path checkout, and lock state changes.

Important APIs/functions: uses `setup_remote_repo`, `clone_repo`, `git lfs track --lockable`, `lfstest-testutils addcommits`, `git checkout`, `git lfs lock`, `assert_file_writeable`, and `refute_file_writeable`.

Control flow: the main test builds a history with lockable `.dat` files and non-lockable `.big` files across `main` and `branch2`, pushes both branches, reclones, then checks contents and write permissions on initial checkout, branch checkout, path checkout after deleting files, and checkout after locking selected paths. The subdirectory test repeats the same lockable behavior with `bin/*.dat` patterns.

State/persistence behavior: repository state includes `.gitattributes`, LFS objects, branch histories, lock records, and filesystem read-only bits. The hook must update permissions without corrupting file contents, including files that were read-only before checkout.

Dependencies/integration points: integrates Git checkout hooks, LFS smudge/checkout behavior, lockable attribute matching, remote locks, pathspec checkout, and platform filesystem permission support.

Risks/test signals: failures indicate lockable files remain writable when they should be protected, locked files become read-only incorrectly, or checkout fails to hydrate/update content. Permission assertions can be platform-sensitive.
<!-- END_FILE_RESEARCH: sources/sync-backup/git-lfs/t/t-post-checkout.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/git-lfs/t/t-post-commit.sh -->
# sources/sync-backup/git-lfs/t/t-post-commit.sh

Purpose: validates the post-commit hook's lockable-file permission updates and ensures it does not traverse submodule contents.

Important APIs/functions: uses `git lfs track --lockable`, `git lfs lock`, `assert_file_writeable`, `refute_file_writeable`, `git submodule add`, and `GIT_TRACE` output inspection.

Control flow: the primary test commits lockable `.dat` files and non-lockable `.big` files, expects newly committed unlocked lockable files to become read-only, then locks two files, edits and commits them, and expects them to remain writable. A second test covers a non-LFS file marked `lockable` in `.gitattributes`, intentionally split across two commits to avoid initial-commit post-checkout behavior. The submodule test commits a submodule and uses trace output to ensure the post-commit filter logic does not enter `submodule/foo`.

State/persistence behavior: the suite mutates `.gitattributes`, committed files, lock state, file mode/read-only bits, and submodule metadata. It checks post-commit side effects on the worktree rather than remote object transfer.

Dependencies/integration points: integrates Git hooks, lockable attributes outside and inside LFS tracking, LFS locks API, submodule boundaries, and trace instrumentation.

Risks/test signals: regressions can leave lockable files editable without locks, make locked files read-only, mishandle lockable non-LFS paths, or scan into submodules. The submodule case relies on trace text matching `filepathfilter`.
<!-- END_FILE_RESEARCH: sources/sync-backup/git-lfs/t/t-post-commit.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/git-lfs/t/t-post-merge.sh -->
# sources/sync-backup/git-lfs/t/t-post-merge.sh

Purpose: verifies the post-merge hook reapplies read-only permissions to lockable files changed by a merge.

Important APIs/functions: uses `setup_remote_repo`, `clone_repo`, `git lfs track --lockable`, `lfstest-testutils addcommits`, `git merge`, `git reset --hard`, `GIT_LFS_SET_LOCKABLE_READONLY`, `assert_file_writeable`, and `refute_file_writeable`.

Control flow: the test creates a main/branch2 history with lockable `.dat` files and non-lockable `.big` files, reclones, verifies initial content and permissions, then performs a merge with readonly handling disabled to demonstrate files would stay writable. It resets and repeats the merge with normal settings, expecting branch-updated lockable files to become read-only while contents are correct.

State/persistence behavior: persisted state includes branch histories, LFS objects, and `.gitattributes`; worktree state includes merge results and filesystem permissions. The hook's side effect is permission correction after Git updates files.

Dependencies/integration points: integrates Git merge hooks, lockable attribute resolution, LFS checkout/smudge behavior, environment-controlled readonly behavior, and branch-tracking from the fixture remote.

Risks/test signals: failures indicate merged lockable files are left writable, merge content is not hydrated correctly, or the readonly environment escape changes behavior unexpectedly.
<!-- END_FILE_RESEARCH: sources/sync-backup/git-lfs/t/t-post-merge.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/git-lfs/t/t-pre-push.sh -->
# sources/sync-backup/git-lfs/t/t-pre-push.sh

Purpose: comprehensive integration suite for the Git LFS pre-push hook, which decides which LFS objects must be uploaded before Git refs are pushed and enforces missing-object, locking, redirect, remote, and optimization behavior.

Important APIs/functions: uses `git lfs pre-push`, normal `git push`, `git lfs push --dry-run`, `git lfs track`, `assert_server_object`, `refute_server_object`, `assert_local_object`, lock helpers, fixture HTTP status injection for locks verification, remote setup/clone helpers, and explicit stdin-style ref lines for hook invocation.

Control flow: early tests feed good, tracked, and bad refs to `git lfs pre-push`, then compare real push, dry-run, and skip-push behavior. Upload tests cover redirects, existing objects, untracked existing server objects, missing local objects with default rejection, allowed incomplete push modes, multiple branches, bad remotes, deleted remote branches after server GC, branch deletion, and force-pushed refs. Lock tests cover own locks, other users' locks on LFS and non-LFS lockable files, multiple HTTP status codes for lock verification, and URL-scoped config disabling. Later tests cover `pushDefault`, remote URL optimization, avoiding traversal for objects the server already has, and local-path remotes.

State/persistence behavior: the suite mutates local LFS object storage, server-side object storage, Git refs, branch tracking config, lock records, remote URLs, and LFS config such as `lfs.allowincompletepush` and locksverify settings. It verifies both positive uploads and negative non-uploads.

Dependencies/integration points: integrates Git pre-push hook stdin protocol, LFS transfer queue, batch API, locks verification API, HTTP redirects/statuses, ref negotiation, remote URL matching, server object existence checks, and Git branch deletion/force-push behavior.

Risks/test signals: failures can block valid pushes, allow Git refs to move without required LFS objects, ignore locks, upload to wrong endpoints, or do excessive object traversal. Several cases depend on exact stderr/log text and fixture HTTP behavior.
<!-- END_FILE_RESEARCH: sources/sync-backup/git-lfs/t/t-pre-push.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/git-lfs/t/t-progress-meter.sh -->
# sources/sync-backup/git-lfs/t/t-progress-meter.sh

Purpose: ensures the human-facing upload progress meter reports positive progress for a many-object push.

Important APIs/functions: uses `setup_remote_repo`, `clone_repo`, `git lfs track`, a `seq 1 128` loop creating `.dat` files, `git push`, `tee`, `${PIPESTATUS[0]}`, and `grep` for the final progress line.

Control flow: the test creates a repo, commits tracking attributes, writes 128 small LFS files, commits them, pushes to origin, checks the push command succeeded, and expects `Uploading LFS objects: 100% (128/128), 276 B` in the log.

State/persistence behavior: creates 128 local LFS objects and uploads them to the fixture remote. The tested state is mostly transfer progress accounting rather than object content.

Dependencies/integration points: integrates transfer queue progress aggregation, terminal/log output, push hook upload behavior, and fixture remote storage.

Risks/test signals: regressions show as missing or incorrect aggregate progress, wrong byte totals, or push failure. The byte total is exact, so changes in fixture file content or output formatting require test updates.
<!-- END_FILE_RESEARCH: sources/sync-backup/git-lfs/t/t-progress-meter.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/git-lfs/t/t-progress.sh -->
# sources/sync-backup/git-lfs/t/t-progress.sh

Purpose: verifies machine-readable progress logging via the `GIT_LFS_PROGRESS` environment variable for clone/download, fetch, and checkout operations.

Important APIs/functions: uses `setup_remote_repo`, `clone_repo`, `git lfs track`, `git push`, `git lfs clone`, `GIT_LFS_SKIP_SMUDGE=1 git clone`, `git lfs fetch --all`, `git lfs checkout`, and progress-log `grep` assertions.

Control flow: the test pushes five `.dat` LFS objects, then clones with `GIT_LFS_PROGRESS` pointing at a log file and checks `download 1/5` through `download 5/5`. It repeats with a smudge-skipped clone by deleting `.git/lfs/objects`, running `git lfs fetch --all`, and checking download progress again. Finally it removes the progress file, runs `git lfs checkout`, and checks `checkout 1/5` through `checkout 5/5`.

State/persistence behavior: local object storage is deliberately removed before fetch to force downloads. Progress state is persisted to an external log path, while checkout writes hydrated worktree files.

Dependencies/integration points: integrates transfer progress callbacks, environment-driven progress writer, clone/fetch/checkout commands, smudge skipping, and object cache behavior.

Risks/test signals: failures indicate missing progress callbacks, wrong counters, or stale progress files. The suite assumes deterministic five-object ordering is not needed because it only checks counter lines.
<!-- END_FILE_RESEARCH: sources/sync-backup/git-lfs/t/t-progress.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/git-lfs/t/t-prune-worktree.sh -->
# sources/sync-backup/git-lfs/t/t-prune-worktree.sh

Purpose: verifies `git lfs prune` retains LFS objects referenced by linked worktrees and by staged files in those worktrees, including when the primary repository is bare.

Important APIs/functions: uses `setup_remote_repo`, `clone_repo`, `git lfs track`, `lfstest-testutils addcommits`, `calc_oid`, `git config lfs.fetchrecent*`, `lfs.fetchexclude`, `git worktree add/remove/prune`, `git add`, and `git lfs prune --dry-run`.

Control flow: the main test creates branches with included and excluded `.dat` objects, configures recent-object pruning to be aggressive, and first records the prune count before adding worktrees. It then adds worktrees for two branches, stages new LFS files inside them, and expects retention counts to increase. Removing a worktree and pruning Git worktree metadata should progressively reduce retained counts. The bare-main test converts the main clone to a bare repository, uses one linked worktree, stages a file, and expects all objects to be retained.

State/persistence behavior: relevant state spans shared LFS object storage, main repo refs, linked worktree HEAD/index files, Git worktree metadata, and fetch-exclude configuration. Dry-run logs are used to assert object accounting without deleting files.

Dependencies/integration points: integrates Git worktree metadata discovery, LFS prune reachability scanning, staged pointer parsing, fetch include/exclude rules, and bare repository layout.

Risks/test signals: regressions can delete objects needed by other worktrees or fail to release objects after worktree metadata is removed. Count-based assertions are sensitive to fixture changes but give clear retention signals.
<!-- END_FILE_RESEARCH: sources/sync-backup/git-lfs/t/t-prune-worktree.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/git-lfs/t/t-prune.sh -->
# sources/sync-backup/git-lfs/t/t-prune.sh

Purpose: large integration suite for `git lfs prune`, covering when local LFS objects may be deleted and which references must retain them.

Important APIs/functions: uses remote/clone fixtures, `lfstest-testutils addcommits`, `calc_oid`, `assert_local_object`, `refute_local_object`, `assert_server_object`, `git lfs prune` flags `--dry-run`, `--verify-remote`, `--verbose`, `--recent`, and `--force`, plus Git stash, index, branch, remote, config, and diff controls.

Control flow: tests cover old unreferenced object deletion, all paths excluded by fetch filters, unpushed commits, recent refs/commits, remote reachability, remote verification including large ref counts, unreachable refs, stashed worktree/index/untracked data, `--recent`, index-retained files, force pruning with repeated runs, empty files, external diff avoidance, and long-line diff/stash-diff hang prevention. Each scenario builds specific commits and object OIDs, tunes `lfs.fetchrecentrefsdays`, `lfs.fetchrecentremoterefs`, `lfs.fetchrecentcommitsdays`, or fetch include/exclude settings, runs prune, and validates retained/deleted local objects and sometimes server objects.

State/persistence behavior: mutates `.git/lfs/objects` by pruning, while preserving objects reachable from current refs, recent refs, unpushed commits, stashes, indexes, and configured retention windows. It also checks behavior against remote object availability and local Git diff configuration.

Dependencies/integration points: integrates Git ref traversal, reflog/recent logic, remote LFS batch verification, stash representation, index parsing, path filters, prune dry-run accounting, filesystem object deletion, and protection against invoking external diff/textconv programs.

Risks/test signals: failures risk data loss by deleting needed LFS objects, disk bloat by retaining too much, hangs on pathological diffs, or incorrect trust in remote availability. Count and OID assertions are extensive and intentionally conservative.
<!-- END_FILE_RESEARCH: sources/sync-backup/git-lfs/t/t-prune.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/git-lfs/t/t-pull.sh -->
# sources/sync-backup/git-lfs/t/t-pull.sh

Purpose: comprehensive integration suite for `git lfs pull`, including object download, checkout hydration, include/exclude filters, filesystem conflict handling, remotes, missing objects, permissions, bare repositories, partial clone/sparse checkout, and pointer extensions.

Important APIs/functions: uses `setup_remote_repo`, `clone_repo`, `assert_pointer`, `assert_server_object`, `assert_local_object`, `assert_clean_status`, `assert_clean_index`, `assert_clean_worktree_with_exceptions`, `git lfs pull`, `git lfs fetch`, `git lfs checkout`, `git clone`, config keys for fetch include/exclude and remote URLs, hard-link checks, sparse checkout, partial clone flags, and extension helpers.

Control flow: the first large test pushes several `.dat` files, clears local object state, and repeatedly pulls with default remote, explicit remote, config filters, command-line filters, changed filter sets, and filename encodings. Conflict suites verify pull skips paths blocked by directory/file/symlink and case-collision conflicts while still downloading objects and keeping the index clean. Later tests cover changed files, hard-link breakage, operation without clean filter, raw remote URLs, multiple remotes, invalid `insteadOf`, merge conflicts, missing objects, outside-repo errors, read-only directories/files, empty-file mtime stability, bare repo fetch-only behavior, partial clone with sparse checkout and index state, and extension-aware pointer downloads.

State/persistence behavior: the command populates `.git/lfs/objects`, writes hydrated worktree files, respects modified/read-only files, preserves index cleanliness, and in bare repos avoids a worktree checkout. Tests deliberately remove object caches, create conflicts, alter remotes/config, and compare file contents/permissions/mtimes.

Dependencies/integration points: integrates transfer queue downloads, checkout scanner, path filters, Git remote resolution, filesystem conflict detection, symlink and case-sensitivity behavior, hard-link safety, partial clone filters, sparse index/checkout, and LFS extension processing.

Risks/test signals: regressions can overwrite user changes, fail to hydrate objects, dirty the index, mishandle conflicting paths, preserve unsafe hard links, use wrong remotes, or fail in sparse/partial environments. Several tests are platform-sensitive for symlinks, case handling, and read-only permissions.
<!-- END_FILE_RESEARCH: sources/sync-backup/git-lfs/t/t-pull.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/git-lfs/t/t-push-bad-dns.sh -->
# sources/sync-backup/git-lfs/t/t-push-bad-dns.sh

Purpose: verifies a push fails safely when the configured LFS endpoint has a bad DNS name and does not upload the object to the normal server.

Important APIs/functions: requires Git 2.3 or newer for `GIT_TERMINAL_PROMPT`; uses `setup_remote_repo`, `clone_repo`, `git lfs track`, `git config lfs.url`, `GIT_TERMINAL_PROMPT=0 git push`, `${PIPESTATUS[0]}`, `refute_server_object`, and `calc_oid`.

Control flow: the test creates a repo, commits `good.dat` tracked by LFS, points `lfs.url` at `http://git-lfs-bad-dns:<port>`, runs `git push origin main` noninteractively, records the exit status, asserts the fixture server does not contain the object, and fails if the push command succeeded.

State/persistence behavior: local commit and pointer exist, but the remote Git/LFS state must not receive the LFS object through fallback behavior. The failed push log is kept for diagnostics.

Dependencies/integration points: integrates LFS endpoint URL override, DNS/network failure handling, noninteractive push, pre-push upload gating, and fixture server object inspection.

Risks/test signals: a regression could treat DNS failures as ignorable, push Git refs without LFS content, or accidentally upload to the default endpoint despite an overridden bad URL.
<!-- END_FILE_RESEARCH: sources/sync-backup/git-lfs/t/t-push-bad-dns.sh -->
