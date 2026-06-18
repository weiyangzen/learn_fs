# sources/control-plane/beegfs-csi-driver/release-tools/generate_patch_release_notes.sh

Purpose: Manual automation for generating Kubernetes CSI patch release changelog PRs across selected repos.

Important APIs/types/functions: Requires environment variables `CSI_RELEASE_TOKEN` and `GITHUB_USER`. Contains an editable `releases` array of `repo version` pairs. Function `gen_patch_relnotes` runs `release-notes --discover=patch-to-latest` with GitHub token and writes `out.md`.

Control flow: For each configured release, the script parses the minor version, enters the repo's `CHANGELOG` directory, fetches upstream, creates/reset a `changelog-release-<minor>` branch from `upstream/release-<minor>`, generates release notes, prepends a new `# Release notes for v<version>` section plus docs link to `CHANGELOG-<minor>.md`, commits, force-pushes to the user's fork, and opens a GitHub PR with `release-note NONE`.

State and persistence: Deletes local `out.md` and `/tmp/k8s-repo`, modifies changelog files, creates/deletes branches, commits, pushes to GitHub, and opens PRs.

Dependencies and integration points: Requires `gh`, `release-notes`, git remotes named `upstream`/`origin`, authenticated GitHub access, and a local directory layout one level above the CSI repos.

Risks: Force-pushes and branch deletion are destructive for matching branch names. The hardcoded `releases` array is empty by default and must be edited. It does not update existing PRs. It assumes changelog files and branch naming conventions match Kubernetes CSI repos.

Test signals: No automated tests; intended for manual use with visible git and PR results.
