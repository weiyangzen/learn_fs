# sources/control-plane/csi-driver-nfs/release-tools/generate-patch-release-notes.sh

Purpose: automates generation of changelog PRs for Kubernetes CSI patch releases.

Important variables and functions: editable `releases` array, `gen_patch_relnotes`, `CSI_RELEASE_TOKEN`, and `GITHUB_USER`.

Control flow: for each configured `repo version`, parses the minor and patch numbers, computes the previous patch tag, enters the repo's `CHANGELOG` directory, fetches upstream, recreates a `changelog-release-<minor>` branch from the upstream release branch, runs the Kubernetes `release-notes` tool, prepends a new release notes section to `CHANGELOG-<minor>.md`, commits, force-pushes, and opens a GitHub PR.

State and persistence behavior: mutates local git branches and changelog files, writes temporary `out.md`/`tmp.md`, force-pushes branches, and creates PRs on GitHub.

Dependencies and integration points: depends on `gh`, `release-notes`, git remotes named upstream/origin, GitHub credentials, and Kubernetes CSI changelog layout.

Risks: the releases array is manual and empty by default. It force-pushes branches and deletes local branches. It assumes previous patch version exists and that changelog files live under `repo/CHANGELOG`.

Test signals: no tests; success is visible through generated changelog commits and PRs.
