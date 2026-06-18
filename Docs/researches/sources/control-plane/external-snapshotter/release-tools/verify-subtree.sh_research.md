<!-- BEGIN_FILE_RESEARCH: sources/control-plane/external-snapshotter/release-tools/verify-subtree.sh -->
# sources/control-plane/external-snapshotter/release-tools/verify-subtree.sh

## Purpose
`verify-subtree.sh` checks that a directory managed by `git subtree` contains no local non-upstream commits outside subtree merge commits.

## Important APIs, Types, and Functions
It is a POSIX `sh -e` script with one required argument, `DIR`. The key command is `git log -n1 --remove-empty --format=format:%H --no-merges -- "$DIR"` to detect non-merge commits touching the directory.

## Control Flow, State, and Persistence
The script validates the argument, computes `REV`, and if non-empty prints a failure header plus `git log --no-merges -- "$DIR"` before exiting 1. If empty, it prints that the directory is a clean copy of upstream. It does not mutate state.

## Dependencies and Integration Points
It depends on Git history preserving subtree merge commits and on the release-tools convention that subtree updates are merge commits while local modifications are ordinary commits. It is suitable for repositories that import release-tools as a subtree.

## Risks and Test Signals
Risks include false negatives if developers modify subtree files inside merge commits, false positives after history rewriting, and dependence on local clone history depth. Signals are a clean-copy message or a log of offending non-merge commits.
<!-- END_FILE_RESEARCH: sources/control-plane/external-snapshotter/release-tools/verify-subtree.sh -->
