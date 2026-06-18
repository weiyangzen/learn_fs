# sources/control-plane/external-snapshotter/release-tools/generate-patch-release-notes.sh

Purpose: semi-automated release-manager script for generating patch release changelog entries and opening PRs against CSI sidecar release branches.

Important variables/functions: required env vars `CSI_RELEASE_TOKEN` and `GITHUB_USER`, editable `releases` array, `gen_patch_relnotes`, `minorPatchPattern`, branch naming `changelog-release-$minor`, and `gh pr create`.

Control flow: for each configured repo/version, derives minor and previous patch tag, checks out the upstream release branch into a local branch, runs Kubernetes `release-notes`, prepends generated notes to `CHANGELOG-$minor.md`, commits, force-pushes, and opens a PR with release-note-none body.

State and persistence: mutates local git worktrees, removes temporary files and `/tmp/k8s-repo`, creates commits, pushes branches, and opens GitHub PRs.

Dependencies and integration: depends on bash, git remotes named upstream/origin, GitHub CLI, release-notes tool, GitHub token, and CSI repo changelog layout.

Risks and test signals: destructive branch deletion/force-push behavior, empty default releases array, no regeneration handling, fragile version parsing, and direct changelog prepending. Signal is a generated PR with correct changelog diff and release-note body.
