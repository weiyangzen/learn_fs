# sources/control-plane/csi-lib-utils/release-tools/verify-subtree.sh

## Purpose

This POSIX shell script verifies that a directory managed by `git subtree` has no local non-upstream modifications.

## Important Behavior

It requires a directory argument. It finds the newest non-merge commit that touched the directory with `git log -n1 --remove-empty --no-merges -- <dir>`. If such a commit exists, it prints the non-merge history for that directory and exits nonzero; otherwise it reports the directory is a clean upstream copy.

## State, Dependencies, and Integration

It has no persistent state and depends only on git and shell. It integrates with repositories that vendor `release-tools` or other upstream content through `git subtree` and want to ensure local edits are not made inside the imported tree.

## Risks and Test Signals

The check trusts merge commits as subtree imports, so a developer could hide local changes in a merge commit. It also assumes the subtree history is represented by merges. Test signal is the printed offending git log and exit status.
