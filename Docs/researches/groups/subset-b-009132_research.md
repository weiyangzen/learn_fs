# subset-b-009132 research

Grouped research for Git LFS shell tests under `sources/sync-backup/git-lfs/t`. Each file section is source-tree-aligned and delimited for reconciliation into the mapped per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/git-lfs/t/t-custom-transfers.sh -->
# sources/sync-backup/git-lfs/t/t-custom-transfers.sh

## Purpose

Tests Git LFS custom transfer adapters and standalone transfer-agent selection across HTTP, local file, and pure SSH remotes. It verifies failure for an invalid custom adapter path, successful upload/download through configured test adapters, URL-specific standalone agent lookup, and safeguards around internal standard adapters such as `basic`, `ssh`, and `lfs-standalone-file`.

## Important APIs, control flow, and dependencies

The script uses `begin_test`/`end_test`, `setup_remote_repo`, `clone_repo`, `clone_repo_url`, `setup_pure_ssh`, `git config lfs.customtransfer.*`, `lfs.standalonetransferagent`, `remote.origin.lfsurl`, `git lfs track`, `lfstest-testutils addcommits`, `git push`, `git lfs fetch --all`, `git lfs pull`, `git lfs fsck`, and object assertion helpers. Control flow is a set of isolated repos: configure transfer settings, generate LFS-tracked `.dat`/`.bin` data, push, clear `.git/lfs/objects`, fetch or pull, then grep trace output and verify object storage.

## State, dependencies, integration points, risks, and test signals

Persistent state includes local `.git/lfs/objects`, remote/server object stores, `TEST_STANDALONE_BACKUP_PATH`, and per-repo Git config. Integration points are the LFS transfer queue, batch API transfer negotiation, standalone adapter process protocol, file URL adapter, URL config matching, lock verification bypass for standalone transfers, and SSH transfer support. Risks include silently falling back from a broken adapter, accepting the file adapter for HTTP remotes, standard/custom adapter name conflicts, quoting bugs in adapter args, and duplicate transfers under concurrency. Signals are transfer trace lines, expected nonzero push/pull failures, `Uploading LFS objects: 100%`, object counts, local/remote object assertions, and warning/error grep checks.
<!-- END_FILE_RESEARCH: sources/sync-backup/git-lfs/t/t-custom-transfers.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/git-lfs/t/t-dedup.sh -->
# sources/sync-backup/git-lfs/t/t-dedup.sh

## Purpose

Exercises `git lfs dedup` capability checks, safety checks, and output reporting. It confirms deduplication is refused when LFS clean/smudge extensions are configured, succeeds or skips gracefully for tracked files, supports `--test`, and rejects dirty working trees.

## Important APIs, control flow, and dependencies

The tests initialize repositories, set and unset `lfs.extension.foo.clean`, `smudge`, and `priority`, run `git lfs dedup` and `git lfs dedup --test`, track `*.dat`, commit files, manually remove one local media object from `.git/lfs/objects/<oid-prefix>/<oid>`, and inspect command output. They branch early when the platform reports no deduplication support.

## State, dependencies, integration points, risks, and test signals

State under test is the working tree cleanliness, Git config extension state, LFS pointer/object cache state, and platform dedup support. Integration points are filesystem clone/reflink/hardlink-style dedup support, extension configuration loading, local object lookup, and the dirty-worktree guard. Risks include dedup running with extensions that transform content, restoring or skipping missing media inconsistently, and modifying an uncommitted working tree. Signals are exact messages for unsupported extension use, support confirmation from `--test`, `Success:` or `Skipped:` rows for files, and the dirty-tree error.
<!-- END_FILE_RESEARCH: sources/sync-backup/git-lfs/t/t-dedup.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/git-lfs/t/t-duplicate-oids.sh -->
# sources/sync-backup/git-lfs/t/t-duplicate-oids.sh

## Purpose

Verifies that multiple revisions containing pointers with the same LFS OID produce only one upload during push, even when pointer text differs because one commit uses the legacy `http://git-media.io/v/2` pointer version and the next uses the current pointer format.

## Important APIs, control flow, and dependencies

The test uses `setup_remote_repo`, `clone_repo`, `git lfs track`, `calc_oid`, `pointer`, manual placement of media in `.git/lfs/objects`, two commits that change only pointer syntax around the same OID, and `git push origin main`. It delays the push until both commits exist so the server starts without the object.

## State, dependencies, integration points, risks, and test signals

State includes two Git revisions, one shared LFS object in the local cache, and no initial remote object. Integration points are pointer parsing for multiple spec URLs, pre-push object enumeration, duplicate OID collapse, and server object upload. The main risk is counting pointer blobs rather than unique OIDs, causing duplicate uploads or wrong progress totals. Signals are `Uploading LFS objects: 100% (1/1), 8 B` and `assert_server_object` for the shared OID.
<!-- END_FILE_RESEARCH: sources/sync-backup/git-lfs/t/t-duplicate-oids.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/git-lfs/t/t-env.sh -->
# sources/sync-backup/git-lfs/t/t-env.sh

## Purpose

Provides exact-output contract coverage for `git lfs env`. It validates repository discovery, remote endpoint rendering, LFS storage paths, transfer lists, default configuration, environment-variable reporting, bare repository handling, SSH endpoint conversion, Unicode paths, locale behavior outside a repo, and duplicate URL alias warnings.

## Important APIs, control flow, and dependencies

The script builds expected multiline output using `git lfs version`, `git version`, `canonical_path`, `native_path`, `setup_expected_concurrent_transfers`, current `GIT_*` environment variables, and expected filter config lines. It creates repos with no remote, one or more remotes, `lfs.url`, `remote.<name>.lfsurl`, `.lfsconfig`, explicit `GIT_DIR`/`GIT_WORK_TREE`, bare repos, SSH remotes, transfer config, and URL `insteadOf` aliases. Most tests compare `git lfs env | grep -v "^GIT_EXEC_PATH="` with `contains_same_elements`.

## State, dependencies, integration points, risks, and test signals

State includes `.git/config`, `.lfsconfig`, `.gitconfig`, global environment, bare/non-bare repo layout, `.git/lfs` paths, remote names, and URL rewrite config. Integration points are config precedence, endpoint discovery, path canonicalization, Git environment handling, transfer adapter registration, SSH URL derivation, and warning emission. Risks include unstable output ordering, leaking unrelated `TEST_GIT_*` variables, incorrect local path when run from `.git` or subdirectories, mishandling invalid relative work trees, broken Unicode/locale handling, and missing duplicate-alias warnings. Signals are full expected/actual output equality by element and targeted greps for endpoint, SSH, transfer, and warning lines.
<!-- END_FILE_RESEARCH: sources/sync-backup/git-lfs/t/t-env.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/git-lfs/t/t-expired.sh -->
# sources/sync-backup/git-lfs/t/t-expired.sh

## Purpose

Validates Git LFS behavior when server-provided transfer actions are expired. It covers absolute, relative, and combined expiration forms for both HTTP batch actions and SSH authentication flows.

## Important APIs, control flow, and dependencies

The script loops over `absolute`, `relative`, and `both` expiration types. For each type it creates a specially named remote repository, tracks `*.dat`, commits `a.dat`, runs `GIT_TRACE=1 git push origin main`, and expects failure or an SSH-expiration trace. SSH cases set `lfs.url` to an `ssh://git@...` equivalent so `git-lfs-authenticate` is used.

## State, dependencies, integration points, risks, and test signals

State is limited to the generated commit, local object cache, remote object store, and server-side behavior keyed by repo name. Integration points are batch action expiration parsing, retry/failure handling, remote object write suppression, and SSH auth cache expiration. Risks include accepting expired upload URLs, persisting objects after failed pushes, or not refreshing expired SSH auth data. Signals are nonzero HTTP push status, `refute_server_object`, and `grep "ssh cache expired"` in push traces.
<!-- END_FILE_RESEARCH: sources/sync-backup/git-lfs/t/t-expired.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/git-lfs/t/t-ext.sh -->
# sources/sync-backup/git-lfs/t/t-ext.sh

## Purpose

Tests `git lfs ext` and `git lfs ext list` reporting for configured LFS pointer extensions. It confirms extension names, clean/smudge commands, priority values, filtering by extension names, and default listing behavior.

## Important APIs, control flow, and dependencies

The test initializes one repository, configures `lfs.extension.foo`, `bar`, and `baz` clean/smudge/priority entries, builds expected output strings, and compares command output for `git lfs ext list foo`, `bar`, `baz`, multiple named args, no args, and `git lfs ext`.

## State, dependencies, integration points, risks, and test signals

State is Git config only. Integration points are extension config parsing, stable ordering, command alias behavior, and output formatting. Risks include sorting by name rather than priority, omitting fields, or diverging `ext` from `ext list`. Signals are exact string equality for every command form.
<!-- END_FILE_RESEARCH: sources/sync-backup/git-lfs/t/t-ext.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/git-lfs/t/t-extra-header.sh -->
# sources/sync-backup/git-lfs/t/t-extra-header.sh

## Purpose

Verifies that Git HTTP `extraHeader` settings are copied to Git LFS HTTP requests, including multiple headers, authorization headers, non-standard authorization casing, and mixed-case URL/config-key lookup.

## Important APIs, control flow, and dependencies

The tests use `setup_remote_repo`, `clone_repo`, `git config --add http.<url>.extraHeader`, `git config --add http.extraHeader`, `git lfs track`, `git push`, `GIT_CURL_VERBOSE=1`, and `GIT_TRACE=1`. Credential-required repositories use a Basic Authorization header built with `base64`. Mixed-case tests configure `http.<Git URL>.ExtraHeader` and verify it applies to the derived LFS URL.

## State, dependencies, integration points, risks, and test signals

State includes local Git config, remote URL-derived LFS endpoint selection, committed LFS object data, and credential helper side effects. Integration points are Git URL config matching, LFS API extra-header injection, header casing treatment, auth bypass when Authorization is supplied, and trace/curl logging. Risks include lowercasing too much of the URL, ignoring multiple headers, invoking credential helpers despite Authorization headers, or mishandling `AUTHORIZATION` casing. Signals are verbose curl header greps and zero counts for credential fill/approve/cache/reject trace lines.
<!-- END_FILE_RESEARCH: sources/sync-backup/git-lfs/t/t-extra-header.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/git-lfs/t/t-fetch-include.sh -->
# sources/sync-backup/git-lfs/t/t-fetch-include.sh

## Purpose

Checks that `git lfs fetch --include` fetches an object when any matching path points at it, even when the same OID is referenced by multiple files in different directories.

## Important APIs, control flow, and dependencies

The setup creates a remote repo, tracks `*.big`, writes identical content under `big/a/a1.big` and `big/b/b1.big`, adds several other `.big` files with a second OID, commits, pushes, and then creates two skip-smudge clones. Each clone pulls Git data without LFS media, runs `git lfs fetch --include=big/a` or `--include=big/b`, and verifies the shared object downloads.

## State, dependencies, integration points, risks, and test signals

State includes server objects for two OIDs, local clones without `.git/lfs/objects` content, and path-filter patterns. Integration points are include filter matching, pointer-to-OID discovery, skip-smudge clone behavior, and duplicate OID handling. Risks include stopping after the first nonmatching path for a duplicated OID or matching only leaf filenames. Signals are push progress for two unique objects, `refute_local_object` before fetch, and `assert_local_object` after each include fetch.
<!-- END_FILE_RESEARCH: sources/sync-backup/git-lfs/t/t-fetch-include.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/git-lfs/t/t-fetch-paths.sh -->
# sources/sync-backup/git-lfs/t/t-fetch-paths.sh

## Purpose

Validates fetch include/exclude path filters when patterns are directory-like and may be "unclean" or slash-terminated. It ensures config and CLI filters agree for a tracked file in `dir/a.dat`.

## Important APIs, control flow, and dependencies

The setup creates a remote repo with `dir/a.dat`, tracks `*.dat`, pushes the object, and clones a reusable working repo. Subsequent tests remove `.git/lfs/objects`, set `lfs.fetchinclude` or `lfs.fetchexclude`, or pass `-I=dir/` and `-X=dir/`, then run `git lfs fetch`.

## State, dependencies, integration points, risks, and test signals

State includes one remote object, one clone, and mutable per-repo filter config. Integration points are path normalization, include/exclude config loading, CLI filter override parsing, and local object cache writes. Risks include treating `dir/` as an invalid glob, failing to normalize path separators, or leaking previous filter config between tests. Signals are local object presence for include paths and absence for exclude paths.
<!-- END_FILE_RESEARCH: sources/sync-backup/git-lfs/t/t-fetch-paths.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/git-lfs/t/t-fetch-recent.sh -->
# sources/sync-backup/git-lfs/t/t-fetch-recent.sh

## Purpose

Tests recent-object fetching policy. It builds a repository with commits and branches at controlled dates, then verifies `git lfs fetch` behavior for `lfs.fetchrecentalways`, recent refs days, recent commits days, older commits, remote branches, and remote refs.

## Important APIs, control flow, and dependencies

The setup uses `lfstest-testutils addcommits` with dates from `get_date`, creates `main` and `other_branch`, pushes both, and clones a test repo. Follow-up tests mutate fetch-recent config values, delete `.git/lfs/objects`, call `git lfs fetch`, and assert which of `oid0` through `oid5` appear locally.

## State, dependencies, integration points, risks, and test signals

State includes commit timestamps, branch reachability, remote refs, LFS objects, and fetch-recent config. Integration points are revision scanning, time-window calculations, remote ref inclusion, branch checkout state, and object download scheduling. Risks include off-by-one day windows, local time variance, missing remote-only refs, or downloading old unreachable objects. Signals are object presence/absence assertions per scenario.
<!-- END_FILE_RESEARCH: sources/sync-backup/git-lfs/t/t-fetch-recent.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/git-lfs/t/t-fetch-refspec.sh -->
# sources/sync-backup/git-lfs/t/t-fetch-refspec.sh

## Purpose

Exercises how `git lfs fetch` resolves explicit refs, tracked branch refs, push-remote configuration, and bad refs. It is a focused contract around selecting the correct remote ref for object discovery.

## Important APIs, control flow, and dependencies

The tests create remotes and clones, track and commit `.dat` files, push to named refs, configure branch upstream or push remote settings, run `git lfs fetch` with explicit or implicit ref arguments, and verify downloaded objects. Bad-ref cases expect a nonzero command and diagnostic output.

## State, dependencies, integration points, risks, and test signals

State includes local branch config, remote refs, object cache contents, and remote object store. Integration points are Git ref resolution, upstream/pushRemote selection, remote name validation, and LFS batch downloads. Risks include fetching from `main` when the tracked ref is different, ignoring `--remote`, or reporting ambiguous ref errors poorly. Signals are local object assertions for good refs and exact greps for invalid ref diagnostics.
<!-- END_FILE_RESEARCH: sources/sync-backup/git-lfs/t/t-fetch-refspec.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/git-lfs/t/t-fetch.sh -->
# sources/sync-backup/git-lfs/t/t-fetch.sh

## Purpose

Comprehensive integration coverage for `git lfs fetch`: normal fetch, dry-run, JSON output, refetch of corrupt objects, shared repositories, remote/branch/commit arguments, stdin refs, include/exclude filters, missing objects, SSL key errors, `--all`, bare repos, no-origin default remote selection, prune, raw remote URLs, invalid inputs, and permission failures.

## Important APIs, control flow, and dependencies

The setup creates a remote with `a.dat` on `main`, `b.dat` on `newbranch`, an empty `.dat`, a clone, and a shared clone. Tests repeatedly clear `.git/lfs/objects`, run `git lfs fetch` variants, compare JSON against expected transfer action payloads, corrupt objects, delete server objects, generate a multi-branch/tag `fetch-all` fixture with `lfstest-testutils addcommits`, create a bare clone, and exercise `--stdin`.

## State, dependencies, integration points, risks, and test signals

State includes local object cache, remote object store, shared Git object database, refs/tags/branches, bare-repo LFS storage, path filters, corrupt object files, and filesystem permissions. Integration points are batch API action rendering, JSON serialization, object integrity checking, ref walking, raw URL endpoint creation, prune logic, SSL credential loading, and default remote selection. Risks include dry-run writing objects, refetch deduplicating incorrectly, `--all` missing tag-only or remote-only refs, pruning needed objects, failing in shared repos, or poor error handling for invalid remotes/refs and unwritable storage. Signals include exact push/fetch progress greps, JSON diffs, fsck OK output, object presence matrices, nonzero status for missing objects, and permission/error message greps.
<!-- END_FILE_RESEARCH: sources/sync-backup/git-lfs/t/t-fetch.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/git-lfs/t/t-filter-branch.sh -->
# sources/sync-backup/git-lfs/t/t-filter-branch.sh

## Purpose

Regression test for running Git LFS tracking inside `git filter-branch` tree filters. It ensures repeated history rewriting with LFS clean filters produces valid pointers and local objects for every rewritten `.dat` file.

## Important APIs, control flow, and dependencies

The test creates three commits containing `a.dat`, `b.dat`, and `c.dat`, then runs `git filter-branch -f --prune-empty --tree-filter` that removes all cached files, runs `git lfs track "*.dat"`, and re-adds the tree for all refs/tags. It then calls `assert_pointer` for all files on `main`.

## State, dependencies, integration points, risks, and test signals

State includes rewritten Git history, `.gitattributes`, pointer blobs, and local LFS object cache. Integration points are Git tree-filter execution, clean filter behavior, index rewriting, and pointer creation during history rewrite. Risks include filter-branch recursion, stale index state, missing LFS objects, or noncanonical pointers after rewrite. Signals are `assert_pointer` checks with calculated OIDs and sizes for all three files.
<!-- END_FILE_RESEARCH: sources/sync-backup/git-lfs/t/t-filter-branch.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/git-lfs/t/t-filter-process.sh -->
# sources/sync-backup/git-lfs/t/t-filter-process.sh

## Purpose

Validates Git's long-running `filter.lfs.process` integration. It covers clone/checkout smudge behavior, include/exclude filtering, clean behavior during add/hash-object, pointer extensions, skip-smudge checkout-index behavior, and avoiding SSH network use during `git archive`.

## Important APIs, control flow, and dependencies

The file requires Git 2.11+, configures `filter.lfs.process=git-lfs filter-process` while disabling clean/smudge fallbacks, and uses `GIT_TRACE_PACKET`. Tests create remotes, track `*.dat`, push branches, clone, checkout branches, configure global `lfs.fetchinclude`/`fetchexclude`, use `setup_case_inverter_extension`, inspect staged blobs with `git cat-file -p :path`, run `git hash-object --stdin --path`, `git checkout-index -af`, `git lfs pointer --check`, `git archive`, and pure SSH setup.

## State, dependencies, integration points, risks, and test signals

State includes the filter-process packet session, working tree files, index pointer blobs, local LFS objects, extension-transformed objects, global path-filter config, and SSH URL config. Integration points are Git filter protocol, clean/smudge ordering, pointer extension clean/smudge hooks, path filter matching, hash-object streaming, checkout-index, and archive export. Risks include filter-process hangs, choosing clean/smudge over process, wrong include/exclude smudge decisions, extension OID mismatch, 1024-byte boundary regressions, or unwanted SSH calls from archive. Signals are worktree content equality, pointer assertions, extension log greps, hash equality, pointer-check success, and absence of pure SSH trace in archive logs.
<!-- END_FILE_RESEARCH: sources/sync-backup/git-lfs/t/t-filter-process.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/git-lfs/t/t-fsck.sh -->
# sources/sync-backup/git-lfs/t/t-fsck.sh

## Purpose

Comprehensive coverage for `git lfs fsck` object and pointer validation. It checks default repair behavior, dry-run behavior, shell-character paths, outside-repo errors, malformed/noncanonical pointers, Git object directory overrides, no-object cases, symlink and negated attribute exemptions, object corruption/missing files, excluded paths, explicit refs/ranges, and invalid refs.

## Important APIs, control flow, and dependencies

Helper functions `create_invalid_pointers`, `setup_invalid_pointers`, and `setup_invalid_objects` build repositories with tracked data, CRLF/noncanonical pointer blobs, large non-pointer blobs added with LFS filters disabled, corrupted object files, and removed object files. Tests run `git lfs fsck`, `--dry-run`, `--pointers`, `--objects`, explicit refs/ranges, and commands under `GIT_WORK_TREE`, `GIT_DIR`, and `GIT_OBJECT_DIRECTORY`.

## State, dependencies, integration points, risks, and test signals

State includes `.git/lfs/objects`, `.git/lfs/bad`, Git blobs, `.gitattributes` and macro attributes, symlinks, excluded paths, and alternate object directories. Integration points are pointer parser canonicalization, attribute matching and negation, local object hash verification, repair movement, ref walking, shell-safe path handling, and object-directory plumbing. Risks include moving files during dry-run, checking exempt files, missing alternate object storage, mishandling macro order, or reporting path glob chars unsafely. Signals are exact output strings, nonzero statuses, grep counts for `nonCanonicalPointer`, `unexpectedGitObject`, `corruptObject`, `openError`, repair messages, and bad-object file existence checks.
<!-- END_FILE_RESEARCH: sources/sync-backup/git-lfs/t/t-fsck.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/git-lfs/t/t-happy-path.sh -->
# sources/sync-backup/git-lfs/t/t-happy-path.sh

## Purpose

Baseline end-to-end Git LFS smoke tests. It verifies tracking, pointer creation, upload, clone/pull download, non-origin remote use, branch-ref-aware object storage, tracked upstream refs, `git lfs clone --exclude`, and cleanup of stale temporary local objects.

## Important APIs, control flow, and dependencies

The tests use `setup_remote_repo`, `setup_remote_repo_with_file`, `clone_repo`, `git lfs track`, `git add/commit/push/pull`, `assert_pointer`, `assert_server_object`, `assert_local_object`, `git lfs clone`, branch config (`push.default`, `branch.main.merge`), and `git lfs env` for temp cleanup. The temp-object test creates files under `.git/lfs/tmp/objects` whose names correspond or do not correspond to complete local objects.

## State, dependencies, integration points, risks, and test signals

State includes working tree content, pointer blobs, local and remote LFS object stores, remote names, branch refs, and temporary object files. Integration points are clean/smudge filters, pre-push upload, pull smudge/download, ref-qualified server object storage, upstream tracking, and local storage janitor behavior. Risks include missing first-push upload, assuming only `origin`, wrong ref metadata for required-branch servers, and deleting unrelated tmp objects. Signals are commit/push greps, content equality, pointer assertions, local/server object assertions, and tmp file existence/refutation checks.
<!-- END_FILE_RESEARCH: sources/sync-backup/git-lfs/t/t-happy-path.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/git-lfs/t/t-install-custom-hooks-path-unsupported.sh -->
# sources/sync-backup/git-lfs/t/t-install-custom-hooks-path-unsupported.sh

## Purpose

Version-gated test for Git versions without `core.hooksPath` support. It confirms `git lfs install` falls back to `.git/hooks` instead of writing into a configured custom hook path.

## Important APIs, control flow, and dependencies

The script uses `ensure_git_version_isnt $VERSION_HIGHER "2.9.0"`, initializes a repo, creates `custom_hooks_dir`, sets `core.hooksPath`, runs `git lfs install`, and checks hook file locations.

## State, dependencies, integration points, risks, and test signals

State is the repository config and hook directories. Integration points are Git-version feature detection and hook installation path selection. Risks include blindly honoring unsupported `core.hooksPath` or failing to install hooks at all. Signals are `Updated Git hooks`, absence of `custom_hooks_dir/pre-push`, and presence of `.git/hooks/pre-push`.
<!-- END_FILE_RESEARCH: sources/sync-backup/git-lfs/t/t-install-custom-hooks-path-unsupported.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/git-lfs/t/t-install-custom-hooks-path.sh -->
# sources/sync-backup/git-lfs/t/t-install-custom-hooks-path.sh

## Purpose

Tests supported `core.hooksPath` handling during `git lfs install`, including normal custom paths, running install from a subdirectory, and shell-expanded `~` paths.

## Important APIs, control flow, and dependencies

The file requires Git 2.9+, defines `assert_hooks` and `refute_hooks`, initializes repos, sets `core.hooksPath`, runs `git lfs install`, and verifies `pre-push`, `post-checkout`, `post-commit`, and `post-merge` live in the configured hook directory rather than `.git` or a caller subdirectory.

## State, dependencies, integration points, risks, and test signals

State includes `.git/config`, custom hook directories, `$HOME/custom_hooks_dir`, and generated hook scripts. Integration points are hooksPath resolution, relative path behavior from subdirectories, tilde expansion, and hook installer coverage for all LFS hooks. Risks include writing to the wrong relative directory, leaving partial hooks, or failing to expand `~`. Signals are hook existence/refutation checks and `Updated Git hooks` grep.
<!-- END_FILE_RESEARCH: sources/sync-backup/git-lfs/t/t-install-custom-hooks-path.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/git-lfs/t/t-install-worktree-unsupported.sh -->
# sources/sync-backup/git-lfs/t/t-install-worktree-unsupported.sh

## Purpose

Version-gated test for Git versions without worktree-specific config support. It verifies `git lfs install --worktree` fails with an error instead of silently writing an unsupported scope.

## Important APIs, control flow, and dependencies

The script uses `ensure_git_version_isnt $VERSION_HIGHER "2.20.0"`, initializes a repo, runs `git lfs install --worktree`, captures stderr, and asserts nonzero status plus error text containing `--worktree`.

## State, dependencies, integration points, risks, and test signals

State is only repository config and command output. Integration points are Git version detection and `git config --worktree` availability. Risks include silently writing local/global config or reporting success on unsupported Git. Signals are nonzero exit status and greps for `error` and `--worktree`.
<!-- END_FILE_RESEARCH: sources/sync-backup/git-lfs/t/t-install-worktree-unsupported.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/git-lfs/t/t-install-worktree.sh -->
# sources/sync-backup/git-lfs/t/t-install-worktree.sh

## Purpose

Tests `git lfs install --worktree` on Git versions with worktree config support. It verifies outside-repo failure, single and multiple worktree config scopes, refusal without `extensions.worktreeConfig`, and conflicts with other install scopes.

## Important APIs, control flow, and dependencies

The script requires Git 2.20+, creates repos and linked worktrees, mutates global/local filter values, enables `core.repositoryformatversion=1` and `extensions.worktreeConfig=true`, runs `git lfs install --worktree`, and compares `git config`, `--local`, `--worktree`, and `--global` values. It also runs conflicting option combinations with `--local`, `--system`, and `--file`.

## State, dependencies, integration points, risks, and test signals

State includes global config, local repo config, worktree-specific config, linked worktree metadata, and command output files. Integration points are Git worktree config extension, filter installation scope selection, repository discovery, and option validation. Risks include overwriting global/local config, allowing worktree config without the extension, or accepting multiple scopes. Signals are exact filter value comparisons, nonzero outside-repo/error cases, and exact conflict error text.
<!-- END_FILE_RESEARCH: sources/sync-backup/git-lfs/t/t-install-worktree.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/git-lfs/t/t-install.sh -->
# sources/sync-backup/git-lfs/t/t-install.sh

## Purpose

Broad coverage for `git lfs install`: idempotence, upgrade behavior, repo hook generation/update, outside-repo behavior, `--skip-smudge`, `--local`, `--file`, permission failures, scope conflicts, inaccessible `.git/lfs`, `--skip-repo`, and multiple global config values.

## Important APIs, control flow, and dependencies

The tests inspect and set `filter.lfs.clean`, `smudge`, and `process` in global/local/file scopes; run `git lfs install` with `--skip-repo`, `--force`, `--skip-smudge`, `--local`, and `--file`; compare expected hook script bodies for `pre-push`, `post-checkout`, `post-commit`, and `post-merge`; create mirror/bare repos; simulate permission failures by chmodding `.git`; and verify conflicting scope options.

## State, dependencies, integration points, risks, and test signals

State includes Git config scopes, hook files, repository/bare hooks directories, permissions, and generated output. Integration points are Git config writes, hook updater, skip-smudge filter-process settings, non-repository install semantics, and error propagation from `git config`. Risks include using `--replace-all` unnecessarily, clobbering unknown hooks without force, modifying wrong config scope, failing in bare repos, and bad exit codes. Signals are exact config values, hook body equality, output string equality, grep for permission/config errors, and hook presence/absence checks.
<!-- END_FILE_RESEARCH: sources/sync-backup/git-lfs/t/t-install.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/git-lfs/t/t-lock.sh -->
# sources/sync-backup/git-lfs/t/t-lock.sh

## Purpose

Tests creating Git LFS locks across branch-ref requirements, remote selection, multiple paths, JSON output, absolute paths, client certificate auth, nonexistent files, duplicate locks, directories, nested paths, subdirectories, symlinked workdirs, ignored lockable files, and pure SSH transfer locking.

## Important APIs, control flow, and dependencies

The script uses `setup_remote_repo_with_file`, `clone_repo`, `setup_pure_ssh`, `git lfs lock`, `git lfs unlock`, `git lfs locks`, `assert_lock`, `assert_server_lock`, `assert_server_lock_ssh`, branch config (`push.default`, `branch.main.merge`, `remote.pushDefault`, `branch.main.pushRemote`), client cert config, `.gitattributes lockable`, `.gitignore`, symlink helpers, and `GIT_TRACE_PACKET`.

## State, dependencies, integration points, risks, and test signals

State includes server lock records keyed by path/ref, local branch/remote config, lockable file permissions, ignored-file config, client cert files, and SSH URL config. Integration points are locks API, ref validation, push remote precedence, path canonicalization, JSON formatting, local checkout permission updates, TLS client auth, and pure SSH protocol. Risks include locking against the wrong branch, failing to normalize absolute/subdirectory/symlink paths, permitting directory locks, or breaking lockable ignored files. Signals are JSON assertions, server lock/ref checks, output greps, nonzero failure checks, and writeability assertions.
<!-- END_FILE_RESEARCH: sources/sync-backup/git-lfs/t/t-lock.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/git-lfs/t/t-locks.sh -->
# sources/sync-backup/git-lfs/t/t-locks.sh

## Purpose

Tests listing Git LFS locks from the server and local cache. It covers ref mismatches, single lock listing, `--remote` override behavior, SSH via `git-lfs-authenticate`, pure SSH via `git-lfs-transfer`, JSON output, limits, pagination, and cached `--local` listings including failed duplicate-lock cleanup.

## Important APIs, control flow, and dependencies

The tests create remotes with lockable files, call `git lfs lock`, inspect locks using `git lfs locks --path`, `--json`, `--limit`, and `--local`, configure invalid `remote.pushDefault` and `branch.main.pushRemote`, set SSH transfer modes (`never`, `always`, `negotiate`), remove `origin` to prove local cache use, and unlock cached records.

## State, dependencies, integration points, risks, and test signals

State includes server lock records, local lock cache, branch refs, remote config, SSH config, and command logs. Integration points are locks API pagination, remote selection, SSH protocol negotiation, local lock cache persistence, JSON serialization, and unlock cache cleanup. Risks include using the wrong ref, ignoring `--remote`, missing paginated locks, requiring network for `--local`, or leaving stale cache entries after failed/duplicate lock operations. Signals are line counts, greps for paths/owners/IDs, trace greps for SSH helper selection, nonzero failure checks, and zero local locks after unlock cleanup.
<!-- END_FILE_RESEARCH: sources/sync-backup/git-lfs/t/t-locks.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/git-lfs/t/t-logs.sh -->
# sources/sync-backup/git-lfs/t/t-logs.sh

## Purpose

Tests `git lfs logs` output after an invalid log lookup has produced a Git LFS log file. It verifies the failure exit code, the stored command text in the log, and `git lfs logs last` replaying the newest log exactly.

## Important APIs, control flow, and dependencies

The test initializes a repo, runs `git lfs logs boomtown` with `set +e`, expects exit code `2`, finds the generated filename under `.git/lfs/logs`, greps the log for `$ git-lfs logs boomtown`, and compares the log file content to `git lfs logs last`.

## State, dependencies, integration points, risks, and test signals

State is the LFS logs directory and command failure metadata. Integration points are log file creation on command errors, `last` alias resolution, and log display. Risks include not writing logs on failure, using the wrong latest log, omitting the command line from the log, or returning the wrong error status. Signals are exit code `2`, the `.git/lfs/logs` file, the command-line grep, and exact equality with `git lfs logs last`.
<!-- END_FILE_RESEARCH: sources/sync-backup/git-lfs/t/t-logs.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/git-lfs/t/t-ls-files.sh -->
# sources/sync-backup/git-lfs/t/t-ls-files.sh

## Purpose

Comprehensive coverage for `git lfs ls-files`. It validates normal, debug, size, long OID, name-only, JSON, include/exclude, checkout/download status, subdirectory invocation, case sensitivity, index-vs-tree behavior, historical refs, `--all`, deleted files, invalid argument ordering, escaped Unicode paths, reference ranges, and independence from fetch filters.

## Important APIs, control flow, and dependencies

The tests initialize many repos, use `git lfs track`, commit/add/remove tracked files, mutate working tree and `.git/lfs/objects`, run `git lfs ls-files` with flags (`--debug`, `--size`, `--include`, `--exclude`, `--all`, `--deleted`, `--name-only`, `--json`, `--long`), compare exact output with heredocs, and inspect refs/tags/ranges. They also test path filter cache settings via `lfs.pathFilterCacheSize`.

## State, dependencies, integration points, risks, and test signals

State includes index entries, HEAD trees, historical refs, working-tree file presence, local object cache, `.gitattributes`, path filters, case sensitivity (`core.ignorecase`), deleted entries, and JSON output files. Integration points are pointer scanning from index/tree/history, local object existence checks, checkout status detection, include/exclude filtering, path normalization from subdirectories, Unicode path handling, and output serializers. Risks include mixing index state into historical refs, incorrect `downloaded` flags, duplicate OID collapse hiding duplicate files, path filters affecting `ls-files`, or malformed JSON/order. Signals are exact text diffs, grep counts, line counts, exit-code checks, and JSON heredoc diffs.
<!-- END_FILE_RESEARCH: sources/sync-backup/git-lfs/t/t-ls-files.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/git-lfs/t/t-malformed-pointers.sh -->
# sources/sync-backup/git-lfs/t/t-malformed-pointers.sh

## Purpose

Tests clone/smudge behavior when Git blobs match LFS-tracked attributes but are malformed or empty pointer candidates. It ensures malformed data is preserved as normal file content and empty blobs remain empty without noisy clone logging.

## Important APIs, control flow, and dependencies

The tests create remotes, track `*.dat`, disable LFS process/clean filters while adding files, generate malformed blobs of 1023, 1024, 1025, and 1048576 bytes with `lfstest-genrandom`, commit and push them, clone another repo, and compare source and cloned file contents. The empty case adds an empty `.dat` blob with filters disabled and checks blob and worktree byte counts.

## State, dependencies, integration points, risks, and test signals

State includes Git blobs that are not valid LFS pointers, clone logs, and worktree files. Integration points are pointer parser size limits, smudge filter fallback behavior, clone logging, and clean-filter bypass configuration. Risks include treating arbitrary tracked blobs as pointers, corrupting malformed files during checkout, or logging empty blobs as pointer errors. Signals are clone log greps for malformed files, exact content equality, zero-byte checks, and absence of empty-file clone log entries.
<!-- END_FILE_RESEARCH: sources/sync-backup/git-lfs/t/t-malformed-pointers.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/git-lfs/t/t-merge-driver.sh -->
# sources/sync-backup/git-lfs/t/t-merge-driver.sh

## Purpose

Tests `git lfs merge-driver` behavior for successful merges, explicit Git merge programs, custom merge programs, conflicts, and non-pointer inputs when LFS tracking is added after file history exists.

## Important APIs, control flow, and dependencies

Helper functions `setup_successful_repo`, `setup_custom_repo`, and `setup_conflicting_repo` create diverged branches with edited `a.dat`, optionally tracking LFS later. Tests configure `merge.lfs.driver` with `git lfs merge-driver --ancestor %O --current %A --other %B --marker-size %L --output %A` and optional `--program` commands, merge `other`, compare worktree content to expected merged/conflicted files, and assert pointer/local object results.

## State, dependencies, integration points, risks, and test signals

State includes branch histories, LFS-tracked pointer blobs, non-pointer historical blobs, merge output file, local LFS objects, and configured merge driver command. Integration points are Git merge driver placeholders, pointer smudge/clean for merge inputs, custom program substitution, conflict marker handling, and post-merge pointer storage. Risks include losing content when inputs are non-pointers, not propagating merge conflicts, quoting custom programs incorrectly, or writing wrong pointer OID. Signals are merge success/failure, `diff -u` against expected content, conflict-marker normalized diffs, and pointer/object assertions.
<!-- END_FILE_RESEARCH: sources/sync-backup/git-lfs/t/t-merge-driver.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/git-lfs/t/t-mergetool.sh -->
# sources/sync-backup/git-lfs/t/t-mergetool.sh

## Purpose

Ensures `git mergetool` receives smudged large-file contents for BASE, LOCAL, and REMOTE during an LFS-tracked conflict instead of pointer text.

## Important APIs, control flow, and dependencies

The test creates an LFS-tracked `conflict.dat`, makes conflicting `main` and `conflict` branch commits, runs a merge to produce a conflict, configures a custom mergetool `inspect` command that prints `$BASE`, `$LOCAL`, and `$REMOTE` file contents, and invokes `yes | git mergetool --no-prompt --tool=inspect -- conflict.dat`.

## State, dependencies, integration points, risks, and test signals

State includes conflicted index stages, LFS local object cache, mergetool temp files, and Git mergetool config. Integration points are Git conflict stage materialization, LFS smudge for mergetool files, and mergetool command environment. Risks include passing pointer files to tools, missing base content, or hanging on prompts. Signals are greps for `$BASE=base`, `$LOCAL=a`, and `$REMOTE=b`.
<!-- END_FILE_RESEARCH: sources/sync-backup/git-lfs/t/t-mergetool.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/git-lfs/t/t-migrate-export.sh -->
# sources/sync-backup/git-lfs/t/t-migrate-export.sh

## Purpose

Broad integration coverage for `git lfs migrate export`, which rewrites history from LFS pointers back to normal Git blobs. It covers local and remote refs, bare repositories, include/exclude filters, given branches, required filters, excluding remote refs, `--skip-fetch`, include/exclude ref selection, invalid refs/remotes, `.gitattributes` mode/symlink handling, object maps, verbose output, remote override, and invalid pointer robustness.

## Important APIs, control flow, and dependencies

The file sources `fixtures/migrate.sh`, uses setup helpers for tracked local/remote branch topologies, calculates OIDs from worktree content, calls `git lfs migrate export` with `--include`, `--exclude`, `--everything`, `--skip-fetch`, `--include-ref`, `--exclude-ref`, `--object-map`, `--verbose`, and `--remote`, and validates rewritten refs with `assert_pointer`/`refute_pointer`, local object pruning helpers, `.gitattributes` content checks, tree mode diffs, and commit-map diffs.

## State, dependencies, integration points, risks, and test signals

State includes rewritten Git refs, remote-tracking refs, tags, LFS object cache, `.gitattributes` blobs and modes, object map files, and downloaded/missing media. Integration points are history rewrite planning, pointer smudging into blobs, remote fetch/prune decisions, ref include/exclude filters, attribute mutation to `!text !filter !merge !diff`, object pruning, bare repo support, and object-map generation. Risks include rewriting unintended remote refs, pruning still-referenced objects, losing executable/symlink semantics, failing when objects must be downloaded, or producing incomplete object maps. Signals are pointer/refutation assertions, local object presence matrices, grep checks in `.gitattributes`, invalid-input diagnostics, tree diffs, verbose commit output, and sorted object-map diffs.
<!-- END_FILE_RESEARCH: sources/sync-backup/git-lfs/t/t-migrate-export.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/git-lfs/t/t-migrate-fixup.sh -->
# sources/sync-backup/git-lfs/t/t-migrate-fixup.sh

## Purpose

Tests `git lfs migrate import --fixup`, which infers files to migrate from existing `.gitattributes` instead of explicit include/exclude filters. It covers simple, special-attribute, nested negation, incompatible options, remote tags, `.gitattributes` symlinks, macros, LFS macros, and no-op cases.

## Important APIs, control flow, and dependencies

The script sources `fixtures/migrate.sh`, uses setup helpers such as `setup_single_local_branch_tracked_corrupt`, computes OIDs from current Git blobs, runs `git lfs migrate import --everything --fixup --yes`, and validates pointers and local objects. It also tests failures for `--include`, `--exclude`, `--no-rewrite`, symlinked `.gitattributes`, and checks no-op behavior by comparing original and migrated HEADs.

## State, dependencies, integration points, risks, and test signals

State includes corrupted/non-pointer tracked files, `.gitattributes` content including macros and negations, remote tags, rewritten refs, and local LFS object cache. Integration points are attribute parser fixup discovery, history rewrite, pointer insertion, macro expansion, symlink protection, option validation, and no-op detection. Risks include migrating files excluded by nested attributes, allowing incompatible flags, rewriting when no files qualify, or following `.gitattributes` symlinks. Signals are pointer/object assertions, grep diagnostics, `.gitattributes` content greps, tree-mode diffs, and ref-unmoved checks.
<!-- END_FILE_RESEARCH: sources/sync-backup/git-lfs/t/t-migrate-fixup.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/git-lfs/t/t-migrate-import-no-rewrite.sh -->
# sources/sync-backup/git-lfs/t/t-migrate-import-no-rewrite.sh

## Purpose

Tests `git lfs migrate import --no-rewrite`, which imports selected current files into LFS by adding a new commit without rewriting existing history. It covers default branch, bare repo rejection/behavior, multiple branches, missing or nested `.gitattributes`, custom commit messages including empty messages, and strict path matching in complex nested directories.

## Important APIs, control flow, and dependencies

The file sources `fixtures/migrate.sh`, uses setup helpers such as `setup_local_branch_with_gitattrs`, computes OIDs from index/worktree blobs, runs `git lfs migrate import --no-rewrite --yes` with pathspecs and `-m`, checks `HEAD~1` against the previous commit to confirm history was not rewritten, and verifies new HEAD commit messages and pointers. The strict test creates nested Yarn mirror paths and explicit `.gitattributes` entries.

## State, dependencies, integration points, risks, and test signals

State includes current branch tips, prior commit IDs, new import commits, `.gitattributes` at root and nested paths, local LFS objects, and bare/non-bare repo layout. Integration points are no-rewrite import planner, pathspec matching, attribute file update, commit creation, pointer generation, and local object storage. Risks include rewriting prior commits, using a default commit message when an empty one is supplied, missing nested attributes, overmatching similar paths, or failing to add local objects. Signals are pointer/object assertions, `HEAD~1` equality with prior head, new HEAD inequality, commit-message comparisons, and strict nested path pointer checks.
<!-- END_FILE_RESEARCH: sources/sync-backup/git-lfs/t/t-migrate-import-no-rewrite.sh -->
