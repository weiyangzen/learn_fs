# sources/control-plane/csi-lib-utils/release-tools/generate-patch-release-notes.sh

## Purpose

This bash utility automates changelog pull request creation for Kubernetes CSI patch releases. It is configured by editing an in-script `releases` array.

## Important Behavior

The script requires `CSI_RELEASE_TOKEN`, `GITHUB_USER`, `gh`, and `release-notes`. `gen_patch_relnotes` runs Kubernetes `release-notes` between the previous patch tag and the release branch. For each configured `repo version`, it parses minor and patch numbers, computes the previous patch tag, checks out an upstream release branch into a temporary changelog branch, prepends generated notes to `CHANGELOG-<minor>.md`, commits, force-pushes to the user's fork, and creates a GitHub PR with `release-note NONE`.

## State, Dependencies, and Integration

It mutates local git checkouts, temporary files, branches, remote refs, and GitHub PR state. It depends on repo remotes named `upstream` and `origin`, the GitHub CLI, the release-notes binary, GitHub auth, and changelog file conventions.

## Risks and Test Signals

The script is deliberately manual and edits need to be made before use. It force-pushes, deletes local branches, and does not update existing PRs. Regex parsing assumes numeric `MAJOR.MINOR.PATCH` without a `v` prefix in the array. Test signals are command failures, generated changelog diffs, and created PRs.
