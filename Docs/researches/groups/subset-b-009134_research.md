# subset-b-009134 Research

Grouped research for Git LFS shell integration tests and small Go utility packages. Each section preserves the source path in its title and is wrapped for deterministic per-file reconciliation.

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/git-lfs/t/t-push-failures-local.sh -->
# sources/sync-backup/git-lfs/t/t-push-failures-local.sh

Purpose: exercises local-object failure behavior for `git lfs push`, especially `lfs.allowincompletepush` and the SSH `git-lfs-transfer` path. It validates that missing or corrupt local LFS media can be either tolerated with an incomplete-push warning or rejected before remote upload.

Important APIs/functions: sources `testlib.sh`; uses `setup_remote_repo`, `clone_repo`, `setup_pure_ssh`, `ssh_remote`, `git lfs track`, `git lfs push`, `git push`, `delete_local_object`, `corrupt_local_object`, `assert_server_object`, and `refute_server_object`.

Control flow: each `begin_test` creates an isolated remote and clone, tracks `*.dat`, commits LFS files, mutates local media storage, and pushes. The first pair enables `lfs.allowincompletepush` and expects Git data to push while selected LFS objects are absent remotely. The default and explicit false cases expect failure messages. The final cases replace object content with zero-byte corrupt files and verify checksum/size validation failure.

State and persistence: mutates `.git/lfs/objects`, repository config, branch history, and remote test-server storage under `REMOTEDIR`. SSH variants set `lfs.url` to a pure SSH URL and exercise packet-transfer persistence on the same test repository state.

Dependencies and integration points: depends on the LFS pre-push hook, transfer queue, object scanner, local media verifier, test HTTP server, and optional `git-lfs-transfer` binary. Integrates with `testhelpers.sh` object helpers for both local disk and remote server assertions.

Risks: local failure handling is sensitive to config precedence, hook-vs-manual push differences, transfer adapter parity, and stale remote state. Corrupt-object checks guard against uploading invalid content or reporting success after a partial local read.

Test signals: eight tests cover allow-missing true, false, default rejection, corrupt object rejection, and equivalent pure SSH transfer cases.
<!-- END_FILE_RESEARCH: sources/sync-backup/git-lfs/t/t-push-failures-local.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/git-lfs/t/t-push-failures-remote.sh -->
# sources/sync-backup/git-lfs/t/t-push-failures-remote.sh

Purpose: verifies push error reporting when the server returns failure responses from either storage upload endpoints or the batch API.

Important APIs/functions: defines `push_fail_test`; uses `setup_remote_repo`, `clone_repo`, `repo_endpoint`, `git lfs track`, `git push`, and server-triggering content names such as `return-status-403`.

Control flow: `push_fail_test` creates a repo, writes a file whose payload causes the test server to emit a chosen status, commits it, attempts a push, and asserts the command fails with the expected status text. It parameterizes storage-layer and API-layer failures.

State and persistence: creates one disposable remote per case, commits a single LFS-tracked file, and relies on the test server's content-triggered response behavior rather than persistent error configuration.

Dependencies and integration points: integrates with the batch transfer client, HTTP status handling, LFS pre-push hook, credential helper, and lfstest server error simulation.

Risks: regressions here would hide authorization, missing object, gone, validation, and server-error messages from users, or could accidentally retry/continue after unrecoverable statuses.

Test signals: ten cases cover storage 403/404/410/500/503 and API 403/404/410/422/500 responses.
<!-- END_FILE_RESEARCH: sources/sync-backup/git-lfs/t/t-push-failures-remote.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/git-lfs/t/t-push-file-with-branch-name.sh -->
# sources/sync-backup/git-lfs/t/t-push-file-with-branch-name.sh

Purpose: regression test that pushing a file whose path matches a branch name still uploads the correct LFS object and does not confuse file-path and ref-name parsing.

Important APIs/functions: uses `setup_remote_repo`, `clone_repo`, `git lfs track`, regular Git commit/push, and `assert_server_object`.

Control flow: creates a file named `branch`, commits it on an LFS-tracked path, pushes `main`, and verifies the resulting object by SHA-256 on the server.

State and persistence: persists a single pointer in Git history and the matching media object in the test server's LFS object store.

Dependencies and integration points: exercises pointer generation, pre-push object enumeration, and ref/path disambiguation in Git LFS push code.

Risks: ambiguous names can cause missing uploads if revision arguments are resolved before paths or if scanner output is interpreted as refs.

Test signals: one focused integration test with explicit server-object assertion.
<!-- END_FILE_RESEARCH: sources/sync-backup/git-lfs/t/t-push-file-with-branch-name.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/git-lfs/t/t-push.sh -->
# sources/sync-backup/git-lfs/t/t-push.sh

Purpose: broad integration suite for `git lfs push`, covering refs, `--all`, `--object-id`, stdin input, remote selection, retries, raw URLs, invalid metadata, href rewriting, server-already-has-object optimization, tags, and custom refs.

Important APIs/functions: defines `push_repo_setup` and `push_all_setup`; uses `setup_remote_repo`, `clone_repo`, `setup_alternate_remote`, `lfstest-testutils addcommits`, `git lfs push`, `git push`, `assert_server_object`, `refute_server_object`, `delete_local_object`, `calc_oid`, and `get_date`.

Control flow: early tests validate ref requirements and remote precedence. The main push case checks dry-run output, stdin refs, remote ref simulation, and actual upload counts. `push_all_setup` builds multi-commit branch/tag histories, then `--all` tests ensure correct object sets for no refs, one ref, multiple refs, and deleted files. Later tests validate object-ID-only upload, stdin object IDs, modified-file histories, invalid remotes, ambiguous branch/tag names, expired action retry, raw remote URLs, invalid object sizes, deprecated `_links`, invalid `pushInsteadOf` href rewrite, skipping objects the server already has, multi-ref tag behavior, custom namespaces, and invalid OID diagnostics.

State and persistence: repeatedly creates bare remotes, clones, branch/tag histories, `.git/refs/remotes/origin/HEAD` simulations, local object deletions, config keys such as locks verification and href rewriting, and remote LFS object storage.

Dependencies and integration points: spans the pre-push hook, command-line push path, object scanner, rev-list traversal, batch API, transfer queue, remote URL resolution, Git config remote precedence, retry logic, and test server status/content triggers.

Risks: this is high-blast-radius behavior. Regressions could miss historical objects, upload deleted/unwanted objects, fail multi-ref pushes, re-upload known objects, honor the wrong remote, mis-handle raw URLs, or panic on malformed server metadata.

Test signals: over twenty integration blocks cover valid and invalid refs, `--all`, `--object-id`, stdin warnings, retries, raw URL push, invalid sizes, href rewrite failure, server object de-duplication, multi-ref/tag pushes, custom references, and invalid object-ID errors.
<!-- END_FILE_RESEARCH: sources/sync-backup/git-lfs/t/t-push.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/git-lfs/t/t-reference-clone.sh -->
# sources/sync-backup/git-lfs/t/t-reference-clone.sh

Purpose: validates Git LFS behavior when cloning or fetching with Git alternate object stores created by `git clone --reference`.

Important APIs/functions: defines `assert_same_inode`; uses `setup_remote_repo_with_file`, `clone_repo`, `git clone --reference`, `git lfs pull`, `git lfs fetch`, and filesystem inode checks.

Control flow: first creates a source clone with LFS media, then clones a second repository with `--reference` and confirms the LFS object is linked/reused rather than duplicated. The fetch case verifies later LFS downloads can also use referenced local storage.

State and persistence: creates alternate object references and media files under `.git/lfs/objects`; relies on inode equality for hardlink/shared-storage checks where supported.

Dependencies and integration points: integrates with Git alternates/reference clone setup, local media storage lookup, LFS fetch/pull, and filesystem semantics.

Risks: hardlink/reference handling is platform-sensitive; regressions could duplicate large files, fail to find referenced objects, or corrupt shared local media.

Test signals: two cases cover clone-time and fetch-time reuse of reference clone storage.
<!-- END_FILE_RESEARCH: sources/sync-backup/git-lfs/t/t-reference-clone.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/git-lfs/t/t-repo-format.sh -->
# sources/sync-backup/git-lfs/t/t-repo-format.sh

Purpose: checks that Git LFS commands do not silently operate in unsupported Git repository format versions.

Important APIs/functions: uses `git init`, direct `.git/config` mutation of repository format settings, and `git lfs env`.

Control flow: creates a repo, changes repository format metadata to an unsupported value, runs LFS command(s), and asserts the expected failure or diagnostic.

State and persistence: persists Git config keys in `.git/config`; no remote server state is required.

Dependencies and integration points: integrates with repository discovery, Git config parsing, and LFS environment initialization.

Risks: allowing unsupported repo formats can corrupt repositories or produce misleading behavior with newer Git storage/extensions.

Test signals: one focused repository-format test.
<!-- END_FILE_RESEARCH: sources/sync-backup/git-lfs/t/t-repo-format.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/git-lfs/t/t-smudge.sh -->
# sources/sync-backup/git-lfs/t/t-smudge.sh

Purpose: validates the `git lfs smudge` filter and checkout-time download behavior, including temp-file writes, invalid pointers, pointer extensions, include/exclude filters, skip modes, failure tolerance, and non-origin remotes.

Important APIs/functions: uses `setup_remote_repo_with_file`, `clone_repo`, `git lfs smudge`, `git lfs pull`, `git lfs install`, `GIT_LFS_SKIP_SMUDGE`, include/exclude config, pointer helpers, and local/server object assertions.

Control flow: early cases smudge valid pointers and temp-file paths, reject malformed pointer input, and process extension-bearing pointers. Include/exclude tests configure path filters and verify selected files download or stay as pointers. Skip tests exercise env/config-driven smudge bypass. Clone and failure cases check checkout behavior when downloads are filtered or unavailable. The non-origin case verifies endpoint resolution outside the default remote.

State and persistence: mutates local LFS media, `.git/config`, working tree files, env vars, and remote LFS object availability. Some tests deliberately delete local objects or server objects.

Dependencies and integration points: exercises clean/smudge filters, pointer parser, extension framework, checkout filter process, transfer queue, include/exclude path matching, and remote endpoint resolution.

Risks: smudge failures directly affect checkout correctness. Include/exclude and skip behavior can leave pointers where contents are expected, while extension or temp-file mistakes can corrupt working-tree output.

Test signals: nine integration blocks cover normal smudge, temp file handling, invalid pointers, extensions, include/exclude, skip, clone filters, skipped download failures, and non-origin remotes.
<!-- END_FILE_RESEARCH: sources/sync-backup/git-lfs/t/t-smudge.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/git-lfs/t/t-ssh.sh -->
# sources/sync-backup/git-lfs/t/t-ssh.sh

Purpose: verifies SSH endpoint support when `lfs.url` contains proxy-command syntax, both default and custom forms.

Important APIs/functions: uses `GIT_SSH`, `lfs-ssh-proxy-test`, `git lfs env`, `git lfs ls-files`, `git lfs fetch`, and LFS URL config.

Control flow: each case configures an SSH-style `lfs.url` with proxy command data, runs LFS commands, and checks that the custom SSH/proxy path is invoked correctly.

State and persistence: mutates repository-local LFS config and depends on the fake SSH command in the test environment; no long-lived remote state beyond the test repository.

Dependencies and integration points: integrates with SSH endpoint parsing, Git's SSH command environment, subprocess execution, and transfer adapter setup.

Risks: SSH URLs are quoting-sensitive; regressions can break proxy commands, mishandle spaces/options, or bypass configured transport.

Test signals: two cases cover default and custom proxy-command variants.
<!-- END_FILE_RESEARCH: sources/sync-backup/git-lfs/t/t-ssh.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/git-lfs/t/t-standalone-file.sh -->
# sources/sync-backup/git-lfs/t/t-standalone-file.sh

Purpose: exercises the standalone file transfer adapter used for local `file://` remotes and local paths, including upload/download, clone, missing-object failure, `lfs.url` overrides, HTTP fallback, and invalid local repositories.

Important APIs/functions: defines `do_upload_download_test` and `do_local_path_test`; uses `git lfs track`, `lfstest-testutils addcommits`, `git push`, `git lfs fetch --all`, `git lfs fsck`, `native_path`, `urlify`, and trace assertions for `xfer: started custom adapter process`.

Control flow: upload/download helper creates many LFS objects, pushes via local file remote, compares local and remote object lists, deletes local media, and fetches all objects back. Local path helper clones using absolute Unix-style, relative, and native paths. Dedicated tests cover bare and non-bare remotes, missing remote file continuation, clone from file URL, local path/trailing slash behavior, `lfs.url` pointing to file or HTTP endpoints, and an invalid non-repo path error.

State and persistence: creates bare and non-bare Git repositories on disk, writes LFS object files directly under those repos, removes local object stores, and modifies `remote.origin.url` and `lfs.url`.

Dependencies and integration points: integrates with custom transfer adapter discovery, file URL/path normalization, local object store layout, HTTP endpoint override behavior, and fsck validation.

Risks: path handling is platform-sensitive, especially Windows/native paths and trailing slashes. Failure semantics must download all available objects while surfacing missing files, and `lfs.url` must not accidentally write to the Git remote when overridden.

Test signals: nine integration blocks cover bare/non-bare local remotes, missing files, clone, path variants, file/HTTP `lfs.url`, and invalid remote errors.
<!-- END_FILE_RESEARCH: sources/sync-backup/git-lfs/t/t-standalone-file.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/git-lfs/t/t-status.sh -->
# sources/sync-backup/git-lfs/t/t-status.sh

Purpose: validates `git lfs status` human, porcelain, and JSON output across clean, dirty, staged, partially staged, missing, unpushed, bare/no-worktree, deleted, file-directory conflict, and permission-change scenarios.

Important APIs/functions: uses `setup_remote_repo`, `clone_repo`, `git lfs track`, `git lfs status`, `git status`, pointer/object helpers, `git update-index`, and direct working-tree mutations.

Control flow: the suite builds repositories with LFS-tracked files and compares status output after edits, staging, partial staging, conversions between Git and LFS content, missing local objects, unpushed objects, deleted files, and permission mode changes. Output modes are validated separately for normal, porcelain, and JSON.

State and persistence: mutates index, working tree, local LFS media, commits, remotes, and file permissions. Some cases run in subdirectories or repositories without a checkout.

Dependencies and integration points: integrates with Git index diffing, pointer detection, local media lookup, transfer state, JSON formatting, path relativization, and permission mode logic.

Risks: status output is user-facing and script-facing. Regressions can misclassify staged/unstaged LFS transitions, hide missing media, produce invalid JSON, or report wrong paths from subdirectories.

Test signals: seventeen cases cover output formats, subdirectory and outside-repo behavior, initial commit state, duplicate contents, partial staging, LFS/Git conversions, missing/unpushed objects, bare/no-worktree, deletion, file-to-dir, and permission changes.
<!-- END_FILE_RESEARCH: sources/sync-backup/git-lfs/t/t-status.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/git-lfs/t/t-submodule-lfsconfig.sh -->
# sources/sync-backup/git-lfs/t/t-submodule-lfsconfig.sh

Purpose: verifies that `.lfsconfig` inside submodules is honored for environment reporting and submodule update/download behavior.

Important APIs/functions: uses `setup_remote_repo`, `clone_repo`, `git submodule add/update`, `.lfsconfig`, `git lfs env`, and LFS object assertions.

Control flow: creates a submodule repository with LFS configuration, embeds it in a parent repo, and checks that LFS commands executed in the submodule use the configured endpoint. A second case updates submodules with `--init --remote` and verifies LFS content is fetched through `.lfsconfig`.

State and persistence: persists `.lfsconfig` in the submodule working tree/history and submodule metadata in the superproject.

Dependencies and integration points: integrates with Git submodules, per-repository LFS config discovery, endpoint resolution, and checkout/update hooks.

Risks: submodule config scope is easy to resolve incorrectly, causing downloads from the parent remote or failure to authenticate/fetch.

Test signals: two cases cover `git lfs env` and `git submodule update --init --remote` with `.lfsconfig`.
<!-- END_FILE_RESEARCH: sources/sync-backup/git-lfs/t/t-submodule-lfsconfig.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/git-lfs/t/t-submodule-recurse.sh -->
# sources/sync-backup/git-lfs/t/t-submodule-recurse.sh

Purpose: ensures LFS operations behave correctly when Git's `submodule.recurse` option is enabled.

Important APIs/functions: uses remote/submodule setup helpers, `git config submodule.recurse true`, submodule commands, and LFS checkout/fetch behavior.

Control flow: builds a parent repo with an LFS-backed submodule, enables recurse behavior, and runs operations that would traverse submodules to verify LFS does not double-process or fail from unexpected working directories.

State and persistence: stores superproject config, submodule metadata, and submodule LFS objects.

Dependencies and integration points: integrates with Git recursive submodule behavior, repository discovery, and LFS hook/filter execution inside nested working trees.

Risks: global recursion can change command cwd and repository scope, which can break object paths or cause parent/submodule remotes to be confused.

Test signals: one focused recursive-submodule integration test.
<!-- END_FILE_RESEARCH: sources/sync-backup/git-lfs/t/t-submodule-recurse.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/git-lfs/t/t-submodule.sh -->
# sources/sync-backup/git-lfs/t/t-submodule.sh

Purpose: verifies baseline LFS behavior in Git submodules, including local gitdir layout and environment reporting.

Important APIs/functions: uses `git submodule add`, `git lfs env`, `setup_remote_repo_with_file`, and repository path helpers.

Control flow: creates submodule repositories containing LFS files, embeds them in parent repos, then inspects local Git directory resolution and LFS environment output from inside the submodule.

State and persistence: creates `.git/modules/...` submodule gitdirs, working-tree gitfile pointers, and local LFS config/media state.

Dependencies and integration points: integrates with Git's submodule gitdir indirection, LFS local storage discovery, and environment command output.

Risks: wrong gitdir resolution can store media in the parent repository, break hooks, or report incorrect endpoints for nested repos.

Test signals: two cases cover submodule local git directory behavior and `git lfs env`.
<!-- END_FILE_RESEARCH: sources/sync-backup/git-lfs/t/t-submodule.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/git-lfs/t/t-tempfile.sh -->
# sources/sync-backup/git-lfs/t/t-tempfile.sh

Purpose: validates cleanup of old Git LFS temporary files and directories without deleting recent temp artifacts.

Important APIs/functions: uses temp-file creation under the LFS temp area, timestamp manipulation, `git lfs prune` or temp cleanup command paths, and filesystem assertions.

Control flow: creates temp files/directories with ages around the one-hour cutoff, runs cleanup, and verifies only old temp artifacts are removed.

State and persistence: manipulates files under repository LFS temp storage and their mtimes.

Dependencies and integration points: integrates with temp naming conventions, filesystem mtime behavior, and cleanup/prune logic.

Risks: overly aggressive cleanup can delete active transfers; too-conservative cleanup leaks disk space.

Test signals: one cutoff-focused cleanup test.
<!-- END_FILE_RESEARCH: sources/sync-backup/git-lfs/t/t-tempfile.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/git-lfs/t/t-track-attrs.sh -->
# sources/sync-backup/git-lfs/t/t-track-attrs.sh

Purpose: tests `git lfs track` modes that should not modify `.gitattributes`: `--no-modify-attrs` and `--dry-run`.

Important APIs/functions: uses `git lfs track`, `.gitattributes` inspection, `git status`, and output greps.

Control flow: runs track with no-modify or dry-run flags against patterns, checks user-facing output, and asserts attributes files remain unchanged.

State and persistence: initializes temporary Git repositories and intentionally avoids persisting new attributes for these modes.

Dependencies and integration points: integrates with track command option parsing, attributes writer, and status/index behavior.

Risks: dry-run/no-modify regressions can unexpectedly alter repositories or produce misleading output for automation.

Test signals: two tests cover no-modify attributes and dry-run behavior.
<!-- END_FILE_RESEARCH: sources/sync-backup/git-lfs/t/t-track-attrs.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/git-lfs/t/t-track-wildcards.sh -->
# sources/sync-backup/git-lfs/t/t-track-wildcards.sh

Purpose: validates leading-slash wildcard and filename pattern handling in `git lfs track`.

Important APIs/functions: uses `git lfs track`, `.gitattributes` comparison, file creation, add/commit, and `assert_pointer`.

Control flow: one case tracks wildcard patterns with a leading slash and confirms matching behavior; another tracks filename-style leading-slash patterns and verifies pointer conversion for expected files.

State and persistence: persists `.gitattributes`, working-tree files, index entries, and committed LFS pointers.

Dependencies and integration points: integrates with Git attributes pattern syntax, path normalization, and clean filter pointer generation.

Risks: leading slash and wildcard semantics are subtle; wrong escaping can track too much, too little, or produce unusable attributes.

Test signals: two tests cover wildcard and filename leading-slash variants.
<!-- END_FILE_RESEARCH: sources/sync-backup/git-lfs/t/t-track-wildcards.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/git-lfs/t/t-track.sh -->
# sources/sync-backup/git-lfs/t/t-track.sh

Purpose: broad suite for `git lfs track`, including attributes listing, duplicate detection, dry-run/verbose output, directory patterns, line endings, outside-repo errors, symlinks, forbidden patterns, lockable/read-only behavior, escaping, global/system attributes, and JSON output.

Important APIs/functions: uses `git lfs track`, `assert_attributes_count`, `assert_pointer`, file mode helpers, `compare_version`, `native_path_escaped`, and `.gitattributes` direct inspection.

Control flow: starts with ordinary pattern tracking/listing and excluded pattern output. It then validates no-excluded, verbose, dry-run, directories with spaces, no trailing newline, CRLF/autocrlf cases, outside-repo and `.git` directory errors, path representation duplicates, absolute paths, symlinked directories, blocklisted files/globs, lockable toggling and read-only transitions, escaped literals and glob patterns, symlinked repositories, hook installation suppression, comments, current-directory prefixes, global/system attributes, verbose matching logs, and structured JSON output.

State and persistence: creates many repos, writes `.gitattributes` in working tree, `.git/info/attributes`, global/system attributes files, modifies core.autocrlf, file permissions, hooks, symlinks, and committed pointer content.

Dependencies and integration points: integrates with Git attributes parsing/writing, path quoting/escaping, Git config scope, clean filter, lockable file mode handling, hook installation, and JSON output code.

Risks: `track` writes persistent repository policy. Bugs can corrupt `.gitattributes`, mishandle special filenames, track forbidden files, flip file writability incorrectly, or produce incompatible JSON for scripts.

Test signals: twenty-plus cases cover normal listing, option modes, line-ending preservation, repository-boundary errors, symlinks, forbidden patterns, lockable transitions, escapes/globs/spaces, comments, scoped attributes, verbose matching, and JSON schema.
<!-- END_FILE_RESEARCH: sources/sync-backup/git-lfs/t/t-track.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/git-lfs/t/t-umask.sh -->
# sources/sync-backup/git-lfs/t/t-umask.sh

Purpose: verifies Git LFS-created files and directories honor process `umask` and Git `core.sharedRepository`.

Important APIs/functions: defines `clean_setup`, `perms_for`, and `assert_dir_perms`; uses `umask`, `git config core.sharedRepository`, LFS tracking/commit, and filesystem mode inspection.

Control flow: creates clean repos under different `umask` and shared-repository settings, runs LFS operations that create object files/directories, and checks resulting modes.

State and persistence: writes LFS object storage directories/files and Git config; relies on POSIX permissions.

Dependencies and integration points: integrates with LFS file creation helpers, repository permission fetcher, Git shared repository config, and OS mode behavior.

Risks: incorrect permissions can expose private media, prevent collaborators from reading shared repos, or break object creation under restrictive umasks.

Test signals: four cases cover umask for files and directories plus sharedRepository for files and directories.
<!-- END_FILE_RESEARCH: sources/sync-backup/git-lfs/t/t-umask.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/git-lfs/t/t-uninstall-worktree-unsupported.sh -->
# sources/sync-backup/git-lfs/t/t-uninstall-worktree-unsupported.sh

Purpose: checks `git lfs uninstall --worktree` failure behavior when Git does not support or enable the required worktree config extension.

Important APIs/functions: uses `git init`, `git lfs install/uninstall --worktree`, and direct config extension checks.

Control flow: initializes a repo with unsupported worktree configuration state, invokes uninstall with worktree scope, and expects a clear failure.

State and persistence: mutates repository config but should not leave partial filter/hook removal after unsupported operation failure.

Dependencies and integration points: integrates with Git worktree config extension detection and LFS install/uninstall scope handling.

Risks: unsupported worktree operations could delete local/global config unexpectedly or leave filters half-installed.

Test signals: one unsupported-extension failure case.
<!-- END_FILE_RESEARCH: sources/sync-backup/git-lfs/t/t-uninstall-worktree-unsupported.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/git-lfs/t/t-uninstall-worktree.sh -->
# sources/sync-backup/git-lfs/t/t-uninstall-worktree.sh

Purpose: validates `git lfs uninstall --worktree` across outside-repo, single worktree, multiple worktrees, missing extension, and conflicting-scope scenarios.

Important APIs/functions: uses `git worktree`, `git lfs install --worktree`, `git lfs uninstall --worktree`, Git config inspection, and hook/filter assertions.

Control flow: cases assert outside-repo errors, then install/uninstall worktree-scoped filters in one worktree and multiple linked worktrees, checking that only worktree-local config is removed. It also verifies behavior without `extensions.worktreeConfig` and with incompatible flags.

State and persistence: writes per-worktree config, common repo config, hooks, and linked worktree metadata.

Dependencies and integration points: integrates with Git worktree config files, LFS filter config, hook management, and scope validation.

Risks: scope bugs can remove filters for all worktrees, fail to clean a worktree, or conflict with local/global/system uninstall flags.

Test signals: five cases cover outside repo, single worktree, multiple worktrees, missing extension, and conflicting scope.
<!-- END_FILE_RESEARCH: sources/sync-backup/git-lfs/t/t-uninstall-worktree.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/git-lfs/t/t-uninstall.sh -->
# sources/sync-backup/git-lfs/t/t-uninstall.sh

Purpose: tests `git lfs uninstall` for global, local, skip-repo, hook-only, inaccessible local storage, and explicit `--file` scopes.

Important APIs/functions: uses `git lfs install`, `git lfs uninstall`, hook files, Git config list/get, permission manipulation, and scope flags such as `--local`, `--skip-repo`, and `--file`.

Control flow: outside-repo cases verify global cleanup and no access requirement for `.git/lfs`. Inside-repo cases check skip-repo behavior, default pre-push hook removal, non-LFS hook preservation, hook cleanup, local-only uninstall, conflicting scopes, and uninstalling from a specified config file.

State and persistence: mutates global fake HOME config, local `.git/config`, hook files, and custom config files.

Dependencies and integration points: integrates with installer/uninstaller config scope logic, hook template detection, permission handling, and Git config file writing.

Risks: uninstall must avoid deleting user hooks or wrong-scope filters while still removing LFS-managed entries cleanly.

Test signals: ten cases cover outside/inside repository behavior, inaccessible `.git/lfs`, skip-repo, pre-push and hook cleanup, local scope, conflicting scope, and explicit config file uninstall.
<!-- END_FILE_RESEARCH: sources/sync-backup/git-lfs/t/t-uninstall.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/git-lfs/t/t-unlock.sh -->
# sources/sync-backup/git-lfs/t/t-unlock.sh

Purpose: comprehensive integration suite for `git lfs unlock`, covering path/id addressing, ref verification, remote override precedence, multi-file JSON, read-only lockable files, missing/removed paths, validation errors, force behavior, uncommitted/untracked files, and SSH transfer locks.

Important APIs/functions: defines `setup_repo`; uses `setup_remote_repo_with_file`, `git lfs track --lockable`, `git lfs lock`, `git lfs unlock`, `assert_lock`, `assert_server_lock`, `refute_server_lock`, SSH lock helpers, and file writability helpers.

Control flow: initial tests unlock by path or ID under required and non-required refs, including tracked upstream refs. Remote override tests intentionally configure invalid `remote.pushDefault` or `branch.main.pushRemote` and prove `--remote origin` wins. Bad-ref tests ensure lock remains when refs mismatch. Later cases cover multiple file unlock, JSON output, read-only transitions, removed/nonexistent/unlockable files, missing arguments, ambiguous id+path arguments, uncommitted modifications with and without `--force`, untracked files, and pure SSH `git-lfs-transfer`.

State and persistence: creates lock records on the test server, commits lockable attributes, changes file modes, removes or modifies working-tree files, and changes remote selection config.

Dependencies and integration points: integrates with lock API, ref verification, remote resolution, lockable attribute handling, JSON output, local dirty-state checks, and SSH transfer protocol.

Risks: unlock errors can leave server locks orphaned or remove locks from the wrong branch. File mode transitions can make user files unexpectedly read-only or writable, and force/dirty checks guard data loss.

Test signals: more than twenty cases cover path/id unlock, good/bad/tracked refs, remote override, multiple/JSON unlock, read-only behavior, missing paths, errors, dirty/untracked safety, force, and SSH transfer.
<!-- END_FILE_RESEARCH: sources/sync-backup/git-lfs/t/t-unlock.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/git-lfs/t/t-untrack.sh -->
# sources/sync-backup/git-lfs/t/t-untrack.sh

Purpose: tests `git lfs untrack` removal of tracked patterns from attributes files, including escaping, legacy prefixes, modern prefixes, outside-repo behavior, and `GIT_WORK_TREE`.

Important APIs/functions: uses `git lfs track`, `git lfs untrack`, `.gitattributes` inspection, Git worktree/env configuration, and pattern escaping assertions.

Control flow: tracks patterns, untracks them, and compares resulting attributes. Separate cases validate outside-repo failure, removing escape sequences, prefixed legacy/modern patterns, escaped patterns in `.gitattributes`, and use from a separate `GIT_WORK_TREE`.

State and persistence: mutates `.gitattributes` and repository environment variables; no remote storage needed.

Dependencies and integration points: integrates with attributes parser/writer, path prefix normalization, escape handling, repository discovery, and Git worktree environment handling.

Risks: untrack must delete only intended rules; bad parsing can leave stale LFS filters or remove unrelated attributes.

Test signals: seven cases cover normal untrack, outside repo, escape removal, prefixed patterns, escaped attributes, and `GIT_WORK_TREE`.
<!-- END_FILE_RESEARCH: sources/sync-backup/git-lfs/t/t-untrack.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/git-lfs/t/t-unusual-filenames.sh -->
# sources/sync-backup/git-lfs/t/t-unusual-filenames.sh

Purpose: verifies pushing LFS files with unusual filenames and quoting-sensitive paths.

Important APIs/functions: uses `git lfs track`, file creation with special names, commit/push, and server object assertions.

Control flow: creates specially named files, tracks and commits them, pushes to the test server, and confirms objects arrive.

State and persistence: stores unusual paths in Git history, `.gitattributes`, local LFS objects, and remote LFS storage.

Dependencies and integration points: integrates with path quoting, Git attributes matching, clean filter, pre-push scanner, and transfer upload.

Risks: shell/Git/path escaping bugs can skip files, create invalid attributes, or fail on platforms with filename limitations.

Test signals: one push case focused on unusual names.
<!-- END_FILE_RESEARCH: sources/sync-backup/git-lfs/t/t-unusual-filenames.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/git-lfs/t/t-update.sh -->
# sources/sync-backup/git-lfs/t/t-update.sh

Purpose: validates `git lfs update`, which migrates older LFS config keys and hook/config forms to current settings.

Important APIs/functions: uses `git lfs update`, Git config inspection, hook contents, and legacy config such as `lfs.{url}.access`.

Control flow: the main update test constructs legacy filter and hook state and checks update rewrites it correctly. Additional cases cover preserving leading spaces, migrating URL-specific access config, and reporting outside-repo errors.

State and persistence: mutates local/global Git config and hooks in test repositories.

Dependencies and integration points: integrates with installer/update logic, Git config parser/writer, hook templates, and repository discovery.

Risks: updater bugs can destroy user formatting, miss legacy keys, or fail to install required modern filters after upgrades.

Test signals: four cases cover normal update, leading-space preservation, `lfs.{url}.access`, and outside-repo behavior.
<!-- END_FILE_RESEARCH: sources/sync-backup/git-lfs/t/t-update.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/git-lfs/t/t-upload-redirect.sh -->
# sources/sync-backup/git-lfs/t/t-upload-redirect.sh

Purpose: verifies that LFS uploads follow server-provided redirects correctly.

Important APIs/functions: uses `setup_remote_repo`, `clone_repo`, content that triggers redirect behavior, `git push`, and `assert_server_object`.

Control flow: creates and commits an LFS file whose upload action redirects, pushes it, and confirms the object is stored.

State and persistence: persists one LFS object in remote storage after redirect handling.

Dependencies and integration points: integrates with batch API action parsing, HTTP redirect handling, authentication, and upload transfer code.

Risks: redirect handling can lose headers, credentials, or request body, causing failed uploads or security-sensitive cross-host behavior.

Test signals: one redirect upload case.
<!-- END_FILE_RESEARCH: sources/sync-backup/git-lfs/t/t-upload-redirect.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/git-lfs/t/t-usage.sh -->
# sources/sync-backup/git-lfs/t/t-usage.sh

Purpose: checks top-level usage output when no Git LFS subcommand is supplied.

Important APIs/functions: runs `git lfs` without command and greps usage/help output.

Control flow: invokes the binary with no arguments and verifies the command reports usage instead of crashing or silently succeeding.

State and persistence: no repository or remote state required beyond test harness environment.

Dependencies and integration points: integrates with CLI command dispatch and help text generation.

Risks: broken usage output affects discoverability and scripts that rely on non-command invocation behavior.

Test signals: one no-command usage test.
<!-- END_FILE_RESEARCH: sources/sync-backup/git-lfs/t/t-usage.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/git-lfs/t/t-verify.sh -->
# sources/sync-backup/git-lfs/t/t-verify.sh

Purpose: verifies transfer verification retry behavior, including successful retry, no-retry success, insufficient retries, and malformed retry config.

Important APIs/functions: uses content names that trigger verify responses, Git config retry settings, `git push`, log greps, and server object checks.

Control flow: creates LFS objects that require verify action retries, pushes with configured retry counts, and checks whether upload succeeds or fails. A malformed config case verifies fallback/error handling.

State and persistence: mutates Git config and remote LFS storage; uses server-triggered verify behavior.

Dependencies and integration points: integrates with batch verify action handling, retry scheduler, transfer queue, config parsing, and error reporting.

Risks: verification protects integrity after upload. Retry bugs can falsely fail transient verifies or accept objects without required verification.

Test signals: four cases cover retries, success without retry, insufficient retries, and bad `.gitconfig`.
<!-- END_FILE_RESEARCH: sources/sync-backup/git-lfs/t/t-verify.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/git-lfs/t/t-version.sh -->
# sources/sync-backup/git-lfs/t/t-version.sh

Purpose: checks that `git lfs --version` is accepted as a synonym for `git lfs version`.

Important APIs/functions: invokes both version forms and compares output.

Control flow: runs version commands and asserts synonym behavior.

State and persistence: no mutable repo state.

Dependencies and integration points: integrates with CLI flag parsing and version output code.

Risks: command-line compatibility regressions can break package managers and diagnostic scripts.

Test signals: one version synonym test.
<!-- END_FILE_RESEARCH: sources/sync-backup/git-lfs/t/t-version.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/git-lfs/t/t-worktree.sh -->
# sources/sync-backup/git-lfs/t/t-worktree.sh

Purpose: verifies Git LFS behavior in Git linked worktrees, including object storage and hooks.

Important APIs/functions: uses `git worktree add`, `git lfs track`, commits, checkout/filter behavior, and `assert_hooks`.

Control flow: creates a primary repo and linked worktree, performs LFS operations in the worktree, and checks content/object behavior. A second test validates hook installation/availability for worktrees.

State and persistence: uses common Git dir plus per-worktree working trees/config, LFS media directories, and hook files.

Dependencies and integration points: integrates with Git worktree discovery, local media path resolution, filter execution, and hook installation.

Risks: worktree-specific gitdir indirection can misplace objects or hooks, especially with common-dir/shared config.

Test signals: two cases cover normal worktree LFS use and worktree hooks.
<!-- END_FILE_RESEARCH: sources/sync-backup/git-lfs/t/t-worktree.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/git-lfs/t/t-zero-len-file.sh -->
# sources/sync-backup/git-lfs/t/t-zero-len-file.sh

Purpose: verifies zero-length LFS files can be pushed and pulled correctly.

Important APIs/functions: uses `git lfs track`, zero-byte file creation, push/pull or clone operations, and object assertions.

Control flow: one case commits and pushes a zero-length tracked file; another pulls or checks out the zero-length file and verifies it remains empty rather than missing or pointer text.

State and persistence: stores an LFS pointer with size 0, local object metadata, and remote object storage.

Dependencies and integration points: integrates with clean/smudge filters, pointer size handling, transfer upload/download, and filesystem zero-byte files.

Risks: zero-byte content can be confused with missing files or empty pointer reads, leading to skipped uploads/downloads.

Test signals: two cases cover push and pull of zero-length files.
<!-- END_FILE_RESEARCH: sources/sync-backup/git-lfs/t/t-zero-len-file.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/git-lfs/t/testenv.sh -->
# sources/sync-backup/git-lfs/t/testenv.sh

Purpose: shared environment bootstrap for Git LFS integration tests. It detects platform traits, sets paths and environment variables, creates temp/trash directories, locates the test server files, and sources `testhelpers.sh`.

Important APIs/functions: defines `native_path` and `resolve_symlink`; exports `ROOTDIR`, `BINPATH`, `TRASHDIR`, `REMOTEDIR`, credential/certificate paths, `GIT_LFS_FORCE_PROGRESS`, `GIT_CONFIG_NOSYSTEM`, `GIT_SSH`, `GIT_TEMPLATE_DIR`, and `LC_ALL`.

Control flow: detects Windows/Mac/Linux, selects checksum tool and path separator, resolves or creates `GIT_LFS_TEST_DIR`, derives per-test `TRASHDIR`, defines remote server metadata paths, sets Git/LFS environment defaults, clears Git env vars that would leak from callers, creates directories, disables Windows GUI askpass, and loads helpers.

State and persistence: creates a temp root and per-test trash directory, exports temp-root cleanup markers, and sets process-wide environment variables used by every test file.

Dependencies and integration points: integrates with compiled binaries under `bin`, fake SSH command `lfs-ssh-echo`, template fixtures, lfstest server URL/cert files, and all shell test scripts via `testlib.sh`.

Risks: incorrect environment isolation can leak user Git config, break path handling on Windows/Mac, reuse stale server state, or run tests inside the source repository.

Test signals: indirectly covered by all sourced shell tests; helper functions are exercised on platform-specific paths and symlink resolution.
<!-- END_FILE_RESEARCH: sources/sync-backup/git-lfs/t/testenv.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/git-lfs/t/testhelpers.sh -->
# sources/sync-backup/git-lfs/t/testhelpers.sh

Purpose: large shared helper library for Git LFS shell integration tests, providing pointer/object assertions, remote setup, credentials, server lifecycle, version comparisons, path utilities, symlink support, SSH packet helpers, and lock/server helpers.

Important APIs/functions: includes `assert_pointer`, `refute_pointer`, `local_object_path`, `assert_local_object`, `refute_local_object`, `delete_local_object`, `corrupt_local_object`, server object helpers, lock helpers, `assert_attributes_count`, worktree cleanliness helpers, `pointer`, `wait_for_file`, remote/clone setup functions, `repo_endpoint`, credential setup, `setup`, `shutdown`, `tap_show_plan`, `compare_version`, `calc_oid`, `get_date`, path escaping/canonicalization, symlink helpers, extension setup, `setup_pure_ssh`, `ssh_remote`, packet-line helpers, and `setup_expected_concurrent_transfers`.

Control flow: assertion helpers generally compute paths or query the test server and exit nonzero on mismatch. `setup` initializes the remote server via `lfstest-count-tests`, waits for URL/cert files, creates fake HOME config and credentials, and prints diagnostic environment lines. `shutdown` decrements server usage and removes temp directories when allowed. Remote helpers create bare repositories and clone them with the test credential helper.

State and persistence: owns `REMOTEDIR`, credentials under `remote/creds`, fake HOME `.gitconfig`, test server counters, bare remotes, local clones, local and remote `.git/lfs/objects`, generated logs, and optional symlink/environment state.

Dependencies and integration points: integrates with `curl`, the lfstest Git server, custom test binaries, Git config, credential helpers, SSH transfer proxy, filesystem permissions, and every `t-*.sh` script.

Risks: helper bugs can invalidate many tests at once. Server object checks depend on test-server API stability; path helpers must preserve Windows and POSIX behavior; cleanup must avoid deleting user paths; assertions often use shell greps and must remain quoting-safe.

Test signals: indirectly exercised throughout the integration suite. Individual helpers are validated by the many tests that assert pointers, locks, objects, attributes, credentials, symlinks, remotes, and pure SSH transfer behavior.
<!-- END_FILE_RESEARCH: sources/sync-backup/git-lfs/t/testhelpers.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/git-lfs/t/testlib.sh -->
# sources/sync-backup/git-lfs/t/testlib.sh

Purpose: minimal TAP-style shell test harness for Git LFS integration scripts.

Important APIs/functions: defines `atexit`, `begin_test`, and `end_test`; sources `testenv.sh`; calls `setup`, `shutdown`, and `tap_show_plan`.

Control flow: on load it sets strict mode, installs an exit trap, runs shared setup, reads server URLs, and changes to `TRASHDIR`. `begin_test` closes any previous test, increments counters, redirects stdout/stderr/trace to files, resets fake HOME from `TESTHOME`, and disables immediate shell exit so the subshell can report status. `end_test` restores fds, closes trace, prints `ok`/`not ok`, dumps logs on failure or when requested, and clears the current description. `atexit` prints the TAP plan, shuts down, and exits nonzero if failures occurred.

State and persistence: maintains process globals `tests`, `failures`, `test_description`, log files under `TRASHDIR`, fake HOME, and optional Git trace fd.

Dependencies and integration points: integrates with `testenv.sh`, `testhelpers.sh`, Git trace, TAP consumers, lfstest server lifecycle, and every shell test file.

Risks: harness misreporting can hide failures. Because tests must run assertions in `set -e` subshells, missing `set -e` inside blocks can cause false positives.

Test signals: indirectly exercised by all shell tests and visible through TAP output plus dumped stdout/stderr/trace on failure.
<!-- END_FILE_RESEARCH: sources/sync-backup/git-lfs/t/testlib.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/git-lfs/tasklog/list_task.go -->
# sources/sync-backup/git-lfs/tasklog/list_task.go

Purpose: implements `ListTask`, a tasklog task that emits unthrottled line-delimited entries and a final message.

Important APIs/types/functions: `type ListTask struct { msg string; ch chan *Update }`, `NewListTask`, `Entry`, `Complete`, `Throttled`, and `Updates`.

Control flow: constructor creates a buffered update channel. `Entry` sends an update string with a newline. `Complete` sends `<msg>: ...`, then closes the channel. `Throttled` returns false so the logger prints every update.

State and persistence: in-memory channel state only; no disk persistence. Completion closes the update channel and is a one-way state transition.

Dependencies and integration points: depends on `Update` and `Task` contracts in the same package and is enqueued by `Logger.List`.

Risks: sends can block if no logger/consumer drains the one-slot channel. Calling `Complete` multiple times would send/close on a closed channel.

Test signals: `list_task_test.go` covers completion update/closure, entry formatting, and unthrottled status.
<!-- END_FILE_RESEARCH: sources/sync-backup/git-lfs/tasklog/list_task.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/git-lfs/tasklog/list_task_test.go -->
# sources/sync-backup/git-lfs/tasklog/list_task_test.go

Purpose: unit tests for `ListTask` behavior.

Important APIs/types/functions: tests `NewListTask`, `Entry`, `Complete`, `Updates`, and `Throttled` using `testify/assert`.

Control flow: one test completes a task and reads the final update followed by channel closure. Another sends an entry and checks the newline-formatted update. The final test verifies `Throttled` is false.

State and persistence: uses in-memory channels only.

Dependencies and integration points: validates the `Task` contract consumed by `Logger`.

Risks: tests assume channel operations are immediately available because `ListTask` uses a buffered channel; changing channel buffering can deadlock these tests unless consumers are concurrent.

Test signals: directly verifies completion message, channel closure, entry formatting, and throttling flag.
<!-- END_FILE_RESEARCH: sources/sync-backup/git-lfs/tasklog/list_task_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/git-lfs/tasklog/log.go -->
# sources/sync-backup/git-lfs/tasklog/log.go

Purpose: implements the task progress logger used to serialize task updates to an `io.Writer`, with TTY detection, optional forced progress, throttling, and task sequencing.

Important APIs/types/functions: `Logger`, `Option`, `ForceProgress`, `NewLogger`, `tty`, `Close`, `Waiter`, `Percentage`, `List`, `Simple`, `Enqueue`, `consume`, `logTask`, `logLine`, and `log`.

Control flow: `NewLogger` initializes sink, terminal width function, channels, wait group, applies options, detects TTY, and starts `consume`. `Enqueue` increments the wait group and sends tasks; a nil logger drains task updates in goroutines. `consume` forwards queued tasks to a processor goroutine sequentially. `logTask` reads updates, suppresses progress when stdout is not TTY and progress is not forced, applies throttling unless task is unthrottled, writes carriage-return progress lines, emits a final `, done.` line after the channel closes, calls optional `OnComplete`, and decrements the wait group.

State and persistence: in-memory goroutines/channels/waitgroup only; writes progress text to the sink. `Close` closes the enqueue channel and waits for outstanding tasks.

Dependencies and integration points: depends on `github.com/mattn/go-isatty`, `github.com/olekukonko/ts`, `Task`/`Update` types, and task constructors. Used by commands that need progress output.

Risks: `Enqueue` calls `wg.Add(len(ts))` even for nil tasks but skips sending nil, which can leave the wait group unbalanced if nil tasks are passed to a non-nil logger. Progress suppression checks `os.Stdout` TTY rather than only the configured sink, so behavior can differ in tests or redirected sinks unless `ForceProgress` is used.

Test signals: `log_test.go` covers sequential logging, progress suppression, nonblocking enqueue, throttling, durable/unthrottled updates, silent tasks, task constructor enqueue helpers, nil logger behavior, and nil close.
<!-- END_FILE_RESEARCH: sources/sync-backup/git-lfs/tasklog/log.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/git-lfs/tasklog/log_test.go -->
# sources/sync-backup/git-lfs/tasklog/log_test.go

Purpose: unit tests for `Logger` sequencing, throttling, progress suppression, helper constructors, and nil handling.

Important APIs/types/functions: defines test `ChanTask` and `UnthrottledChanTask`; tests `NewLogger`, `ForceProgress`, `Enqueue`, `Close`, `Waiter`, `Percentage`, `List`, `Simple`, and logger internals such as throttle/width overrides.

Control flow: tests feed update channels through the logger and compare exact sink output. They validate multiple tasks run in order but enqueue does not block indefinitely, throttled updates are skipped except forced/last lines, unthrottled tasks log all updates, silent tasks print nothing, and constructors enqueue typed tasks.

State and persistence: in-memory channels and buffers only.

Dependencies and integration points: uses `testify/assert`; validates output consumed by command-line progress users.

Risks: exact string expectations couple tests to carriage-return and padding semantics. Timing tests use synthetic timestamps, avoiding real-time flakes.

Test signals: covers progress output with and without forced progress, task ordering, throttling edge cases, durable updates, silent tasks, helper methods, nil logger enqueue draining, and nil close.
<!-- END_FILE_RESEARCH: sources/sync-backup/git-lfs/tasklog/log_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/git-lfs/tasklog/percentage_task.go -->
# sources/sync-backup/git-lfs/tasklog/percentage_task.go

Purpose: implements `PercentageTask`, a throttled progress task for work with a known total.

Important APIs/types/functions: `PercentageTask`, `NewPercentageTask`, `Count`, `Entry`, `Complete`, `Updates`, and `Throttled`.

Control flow: constructor initializes a buffered channel and emits an initial zero-count update. `Count` atomically increments completed count, panics if it exceeds total, computes floored percentage (100 percent for total zero), sends a formatted update, and closes the channel when complete. `Entry` sends a forced line-delimited update. `Complete` atomically sets count to total and closes the channel if not already complete.

State and persistence: uses atomic `n`, immutable `total`, task message, and update channel. No persistent storage.

Dependencies and integration points: depends on `sync/atomic`, translation package `tr`, and the shared `Task`/`Update` logger contract. Created by `Logger.Percentage`.

Risks: callers must not call `Count` after the channel closes or over-count; both can panic. Forced entries can block on the one-slot channel without an active consumer.

Test signals: `percentage_task_test.go` covers percentage formatting, zero-total behavior, completion closure, throttled flag, and overcount panic.
<!-- END_FILE_RESEARCH: sources/sync-backup/git-lfs/tasklog/percentage_task.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/git-lfs/tasklog/percentage_task_test.go -->
# sources/sync-backup/git-lfs/tasklog/percentage_task_test.go

Purpose: unit tests for `PercentageTask` progress calculation and completion semantics.

Important APIs/types/functions: tests `NewPercentageTask`, `Count`, `Complete`, `Updates`, and `Throttled`.

Control flow: verifies initial 0 percent update, incremental 30 percent formatting, 100 percent for zero totals, channel closure at total count or explicit complete, idempotent complete after natural closure, and panic on overcount.

State and persistence: in-memory channel and atomic counter only.

Dependencies and integration points: validates formatting consumed by `Logger` progress output.

Risks: exact spacing in percentage strings is asserted, so UI formatting changes require test updates.

Test signals: direct coverage for normal, zero-total, complete, throttled, and overcount paths.
<!-- END_FILE_RESEARCH: sources/sync-backup/git-lfs/tasklog/percentage_task_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/git-lfs/tasklog/simple_task.go -->
# sources/sync-backup/git-lfs/tasklog/simple_task.go

Purpose: implements `SimpleTask`, an unthrottled task that emits arbitrary formatted strings and blocks completion until the logger acknowledges it.

Important APIs/types/functions: `SimpleTask`, `NewSimpleTask`, `Log`, `Logf`, `Complete`, `OnComplete`, `Updates`, and `Throttled`.

Control flow: `Log` delegates to `Logf`; `Logf` sends an update with formatted text. `Complete` adds one waitgroup count, closes the channel, and waits. `Logger.logTask` detects `OnComplete` and calls it after consuming all updates, which releases `Complete`.

State and persistence: in-memory unbuffered channel and wait group. No disk state.

Dependencies and integration points: relies on `Logger.logTask` optional `OnComplete` callback; created by `Logger.Simple`.

Risks: `Complete` blocks forever if no logger or consumer calls `OnComplete`. Calling `Log` without a consumer also blocks because the channel is unbuffered.

Test signals: `simple_task_test.go` covers logging, formatted logging, closure/completion acknowledgement, and unthrottled flag.
<!-- END_FILE_RESEARCH: sources/sync-backup/git-lfs/tasklog/simple_task.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/git-lfs/tasklog/simple_task_test.go -->
# sources/sync-backup/git-lfs/tasklog/simple_task_test.go

Purpose: unit tests for `SimpleTask`.

Important APIs/types/functions: tests `NewSimpleTask`, `Log`, `Logf`, `Complete`, `OnComplete`, `Updates`, and `Throttled`.

Control flow: tests run a goroutine to drain updates and call `OnComplete`, then verify emitted strings and channel closure. A separate test checks `Throttled` is false.

State and persistence: in-memory channels/waitgroup only.

Dependencies and integration points: validates the handshake expected by `Logger.logTask`.

Risks: tests must call `OnComplete`; otherwise they would deadlock, mirroring the production contract.

Test signals: direct coverage for plain log, formatted log, complete/channel close, and throttling.
<!-- END_FILE_RESEARCH: sources/sync-backup/git-lfs/tasklog/simple_task_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/git-lfs/tasklog/task.go -->
# sources/sync-backup/git-lfs/tasklog/task.go

Purpose: defines the common tasklog interfaces and update payload used by all task implementations.

Important APIs/types/functions: `Task` interface with `Updates() <-chan *Update` and `Throttled() bool`; `Update` struct with string, timestamp, and force flag; `Update.Throttled`.

Control flow: `Update.Throttled` compares the update timestamp with a supplied threshold and returns false for forced updates, enabling logger throttle decisions.

State and persistence: no persistent state; defines in-memory contracts.

Dependencies and integration points: consumed by `Logger`, `ListTask`, `PercentageTask`, `SimpleTask`, `WaitingTask`, and tests.

Risks: interface changes affect every progress task and command using tasklog. Throttle semantics must preserve forced updates for important messages.

Test signals: covered indirectly by logger and task-specific tests.
<!-- END_FILE_RESEARCH: sources/sync-backup/git-lfs/tasklog/task.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/git-lfs/tasklog/waiting_task.go -->
# sources/sync-backup/git-lfs/tasklog/waiting_task.go

Purpose: implements `WaitingTask`, a simple task that emits a waiting message until explicitly completed.

Important APIs/types/functions: `WaitingTask`, `NewWaitingTask`, `Complete`, `Updates`, and `Throttled`.

Control flow: constructor creates a buffered channel and sends an initial `<msg>: ...` update. `Complete` closes the channel. `Throttled` returns true, so repeated waiting updates would be progress-throttled by the logger.

State and persistence: in-memory channel only.

Dependencies and integration points: created by `Logger.Waiter` and consumed through the `Task` interface.

Risks: the initial buffered send assumes one-slot capacity; repeated completion or updates after close would panic if added later.

Test signals: `waiting_task_test.go` verifies initial update, close-on-complete, and throttled flag.
<!-- END_FILE_RESEARCH: sources/sync-backup/git-lfs/tasklog/waiting_task.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/git-lfs/tasklog/waiting_task_test.go -->
# sources/sync-backup/git-lfs/tasklog/waiting_task_test.go

Purpose: unit tests for `WaitingTask`.

Important APIs/types/functions: tests `NewWaitingTask`, `Complete`, `Updates`, and `Throttled`.

Control flow: reads the initial waiting update, completes the task, verifies channel closure, and asserts the task is throttled.

State and persistence: in-memory channel only.

Dependencies and integration points: validates behavior expected by `Logger.Waiter`.

Risks: exact waiting message string is asserted; UI copy changes require updates.

Test signals: direct coverage for initial message, completion closure, and throttling.
<!-- END_FILE_RESEARCH: sources/sync-backup/git-lfs/tasklog/waiting_task_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/git-lfs/tools/channels.go -->
# sources/sync-backup/git-lfs/tools/channels.go

Purpose: provides a small abstraction for asynchronous result channels that also expose deferred error collection.

Important APIs/types/functions: `ChannelWrapper` interface, `BaseChannelWrapper`, `NewBaseChannelWrapper`, and `(*BaseChannelWrapper).Wait`.

Control flow: `Wait` drains `errorChan` until closed, joining all received errors with Git LFS's `errors.Join`, then returns the combined error.

State and persistence: in-memory error channel only; no persistent state.

Dependencies and integration points: depends on `github.com/git-lfs/git-lfs/v3/errors`. Intended for iterator/result-channel producers that report async errors after consumers finish reading results.

Risks: callers must drain result channels before `Wait` and producers must close the error channel. Otherwise `Wait` can block indefinitely.

Test signals: no direct test in this subset; behavior is simple and likely covered by users of channel wrappers elsewhere.
<!-- END_FILE_RESEARCH: sources/sync-backup/git-lfs/tools/channels.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/git-lfs/tools/copycallback.go -->
# sources/sync-backup/git-lfs/tools/copycallback.go

Purpose: wraps readers/read-seek-closers to report copy progress through callbacks while preserving seek and close behavior.

Important APIs/types/functions: `CopyCallback`, `BodyWithCallback`, `NewByteBodyWithCallback`, `NewFileBodyWithCallback`, `NewBodyWithCallback`, `Read`, `Seek`, `ResetProgress`, `CallbackReader`, `ReadSeekCloser`, `NewByteBody`, `closingByteReader`, `NewFileBody`, and `closingFileReader`.

Control flow: `Read` delegates to the underlying reader, increments cumulative read size on positive reads, and calls the callback with total size, cumulative read, and bytes since last read when no error or EOF occurs. `Seek` updates tracked progress according to seek mode before delegating. `ResetProgress` reports a negative delta equal to consumed bytes. `CallbackReader` provides the same read-progress behavior for plain `io.Reader`.

State and persistence: tracks read progress in memory (`readSize`/`ReadSize`); does not persist data. File wrapper intentionally makes `Close` a no-op around an existing `*os.File`.

Dependencies and integration points: integrates with transfer progress meters, retry/seekable upload bodies, byte-backed test bodies, and file-backed readers.

Risks: callback errors replace read errors and can stop callers. `ResetProgress` assumes callback is non-nil and will panic if called without one. Seek bookkeeping trusts caller offsets and total size.

Test signals: `copycallback_test.go` covers callback invocation on underfilled EOF reads, cumulative byte counts, and seek offset tracking.
<!-- END_FILE_RESEARCH: sources/sync-backup/git-lfs/tools/copycallback.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/git-lfs/tools/copycallback_test.go -->
# sources/sync-backup/git-lfs/tools/copycallback_test.go

Purpose: unit tests for callback reader progress accounting.

Important APIs/types/functions: tests `CallbackReader.Read`, `BodyWithCallback.Read`, `BodyWithCallback.Seek`, and helper `EOFReader`.

Control flow: a custom `EOFReader` returns bytes with `io.EOF`; tests ensure callbacks still fire when bytes are read with EOF. Additional tests verify byte-body read size increments and seek modes update internal progress to start/current/end offsets.

State and persistence: in-memory byte slices and counters only.

Dependencies and integration points: uses `testify/assert`; validates progress accounting used by transfer code.

Risks: tests do not cover callback error propagation, nil callback reset behavior, or file-backed bodies.

Test signals: covers underfilled EOF callback, EOFReader behavior, cumulative reads, and seek bookkeeping.
<!-- END_FILE_RESEARCH: sources/sync-backup/git-lfs/tools/copycallback_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/git-lfs/tools/cygwin.go -->
# sources/sync-backup/git-lfs/tools/cygwin.go

Purpose: non-Windows implementation of Cygwin/MSYS detection.

Important APIs/types/functions: `isCygwin() bool`.

Control flow: build-tagged for `!windows`; always returns false.

State and persistence: none.

Dependencies and integration points: paired with `cygwin_windows.go`; callers can use `isCygwin` cross-platform without build-condition checks.

Risks: none beyond build tag correctness.

Test signals: no direct tests in this subset; platform build tags provide compile-time separation.
<!-- END_FILE_RESEARCH: sources/sync-backup/git-lfs/tools/cygwin.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/git-lfs/tools/cygwin_windows.go -->
# sources/sync-backup/git-lfs/tools/cygwin_windows.go

Purpose: Windows implementation that detects whether the process runs under Cygwin/MSYS-style environments.

Important APIs/types/functions: `cygwinSupport` enum, `Enabled`, package variable `cygwinState`, and `isCygwin`.

Control flow: `isCygwin` returns cached state when known. Otherwise it runs `uname` through the subprocess helper, reads output, marks enabled if it contains `CYGWIN` or `MSYS`, disabled otherwise, and returns the cached boolean. `Enabled` panics on unknown state.

State and persistence: caches detection in package global `cygwinState`; no disk state.

Dependencies and integration points: depends on `subprocess.ExecCommand` and translation package `tr`. Used by Windows path/terminal behavior elsewhere in tools.

Risks: global cache is not synchronized, so concurrent first calls can race under the Go race detector. Missing or failing `uname` disables Cygwin support. Panic in `Enabled` guards impossible unknown enum use.

Test signals: no direct tests in this subset; behavior is platform-specific and compile-tagged.
<!-- END_FILE_RESEARCH: sources/sync-backup/git-lfs/tools/cygwin_windows.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/git-lfs/tools/dir_walker.go -->
# sources/sync-backup/git-lfs/tools/dir_walker.go

Purpose: walks and optionally creates directory prefixes for Git-provided relative file paths, validating that each path segment is a directory.

Important APIs/types/functions: errors `errInvalidDir` and `errNotDir`, `DirWalker`, `NewDirWalkerForFile`, `walk`, `Walk`, and `WalkAndCreate`.

Control flow: `NewDirWalkerForFile` strips the filename from a slash-separated Git path, leaving only directory components. `walk` iterates path segments from `parentPath`, rejects empty, `.`, or `..` segments, stats each joined path, returns not-exist when missing and create is false, calls `Mkdir` when create is true, errors if an existing component is not a directory, and updates `parentPath`/`path` as it progresses. `Walk` checks only; `WalkAndCreate` creates missing directories.

State and persistence: mutates the `DirWalker` fields to track the deepest existing/created parent and remaining missing path. `WalkAndCreate` persists directories on disk using repository permissions.

Dependencies and integration points: depends on Git LFS `errors`, translation `tr`, `Mkdir`, and `repositoryPermissionFetcher`. Used wherever Git LFS must prepare working-tree directories safely for checkout/smudge operations.

Risks: intentionally does not guard TOCTOU races, matching Git-style behavior. It assumes Git-normalized relative paths; invalid paths are rejected but absolute/empty/trailing slash inputs have edge cases tested.

Test signals: `dir_walker_test.go` covers path derivation, existing/missing/created dirs, files and symlink conflicts, trailing slashes, invalid segments, and parent-path variants.
<!-- END_FILE_RESEARCH: sources/sync-backup/git-lfs/tools/dir_walker.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/git-lfs/tools/dir_walker_test.go -->
# sources/sync-backup/git-lfs/tools/dir_walker_test.go

Purpose: comprehensive unit tests for `DirWalker` path splitting and walking/creation behavior.

Important APIs/types/functions: tests `NewDirWalkerForFile`, `DirWalker.walk`, `Walk`, and `WalkAndCreate`; defines `dirWalkerTestConfig` and table-driven `dirWalkerWalkTestCase`.

Control flow: path-constructor tests assert filename-only, nested, leading/trailing slash, bare slash, and empty path behavior. Walk tests create temp directories/files/symlinks, run with and without creation, compare updated `parentPath`/`path`, and verify expected errors using `errors.Is`. Each case is rerun with an empty parent and with parent path `foo/bar`.

State and persistence: creates temporary filesystem trees, files, and symlinks; changes cwd to temp dirs while restoring original cwd.

Dependencies and integration points: uses `os`, `testify/assert`, `testify/require`, and repository permission config. Validates behavior used by checkout/file materialization code.

Risks: symlink creation can fail on platforms without symlink support; the test currently requires it. Table entries mutate expected paths during setup, so reuse must be controlled as the test does.

Test signals: covers extant and missing directories, directory creation, conflicting files/symlinks, trailing slash handling, invalid slash/dot/double-dot components, and parent-path handling.
<!-- END_FILE_RESEARCH: sources/sync-backup/git-lfs/tools/dir_walker_test.go -->
