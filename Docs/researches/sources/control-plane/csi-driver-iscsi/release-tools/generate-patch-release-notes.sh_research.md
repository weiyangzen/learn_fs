# sources/control-plane/csi-driver-iscsi/release-tools/generate-patch-release-notes.sh

Purpose: maintainer automation for generating patch release changelog PRs across CSI repositories.

Important APIs and types: configurable `releases` array contains `repo version` pairs. `gen_patch_relnotes` wraps Kubernetes `release-notes` with `CSI_RELEASE_TOKEN`, start revision, branch, org, repo, markdown links, and output file.

Control flow: for each release entry, the script parses minor and patch versions, computes the previous patch tag, checks out a changelog branch from `upstream/release-<minor>`, generates release notes, prepends a release header to `CHANGELOG-<minor>.md`, commits, force pushes, and creates a GitHub PR with `gh pr create`.

State and persistence: mutates local Git checkouts, branches, changelog files, remote branches, and GitHub PRs.

Dependencies and integration: depends on `gh`, `release-notes`, git remotes named `upstream` and `origin`, `CSI_RELEASE_TOKEN`, `GITHUB_USER`, and a local directory layout where repos are sibling directories.

Risks: `set -x` can expose command details. Branches are force-pushed and deleted locally. The release list is empty by default and must be edited. Existing PR regeneration is explicitly not handled.

Test signals: generated changelog diff, successful commit/push, and created PR.
