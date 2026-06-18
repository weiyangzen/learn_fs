## sources/control-plane/csi-driver-host-path/release-tools/generate-patch-release-notes.sh

Purpose: maintainer automation for generating patch release changelog PRs across Kubernetes CSI repos.

Control flow defines a commented `releases` array, computes previous patch version from each target, checks out a `release-x.y` branch, runs the Kubernetes `release-notes` tool with `CSI_RELEASE_TOKEN`, prepends generated notes to `CHANGELOG-x.y.md`, commits, force-pushes to the user's fork, and opens a GitHub PR with `release-note NONE`.

State and persistence include local repo branches, changelog files, commits, pushed branches, and PRs. Dependencies are bash, git remotes named upstream/origin, `gh`, `release-notes`, GitHub credentials, and repo layout. Risks include destructive branch deletion/force push, empty default release list hiding non-use, fragile semantic version parsing, and no update path for existing PRs. Test signal is manual; it is not part of normal CI.
