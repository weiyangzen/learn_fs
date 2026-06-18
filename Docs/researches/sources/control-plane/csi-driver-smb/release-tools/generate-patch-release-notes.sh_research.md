<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-smb/release-tools/generate-patch-release-notes.sh -->
# sources/control-plane/csi-driver-smb/release-tools/generate-patch-release-notes.sh

Purpose: Maintainer automation for generating patch release changelog PRs across Kubernetes CSI repositories.

Important behavior: Requires `CSI_RELEASE_TOKEN`, `GITHUB_USER`, `gh`, and `release-notes`. The editable `releases` array lists repo/version pairs. `gen_patch_relnotes` invokes `release-notes` from previous patch tag to release branch. The main loop parses minor/patch, checks out a `CHANGELOG` branch from `upstream/release-<minor>`, prepends generated notes to `CHANGELOG-<minor>.md`, commits, force-pushes, and opens a PR with `release-note NONE`.

Control flow: Uses `set -e -x`; any failed command aborts. It computes previous patch by subtracting one from the patch number.

State and persistence behavior: Mutates local git branches, changelog files, remote branches, and GitHub PRs.

Dependencies and integration points: Depends on a particular repository layout where changelogs live under `$repo/CHANGELOG`, upstream remotes exist, and release branches are named `release-X.Y`.

Risks: Force-pushes and branch deletion are destructive to the maintainer workspace. It does not handle patch zero, existing PR updates, or conflicts. The `releases` array is empty/commented by default, requiring manual edits.

Test signals: No automated tests; intended for manual maintainer execution.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-smb/release-tools/generate-patch-release-notes.sh -->
