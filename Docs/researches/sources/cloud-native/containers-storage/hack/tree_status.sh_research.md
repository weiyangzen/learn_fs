<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containers-storage/hack/tree_status.sh -->
# sources/cloud-native/containers-storage/hack/tree_status.sh

## Purpose
This helper verifies that the git worktree is clean.

## Important APIs, Types, And Functions
It captures `git status --porcelain`.

## Control Flow
With empty status, it prints `tree is clean`. Otherwise it prints a dirty-tree message, the porcelain status, and exits 1.

## State And Persistence
No state is modified.

## Dependencies And Integration Points
It is suitable for CI or release checks that require no uncommitted changes.

## Risks And Test Signals
It reports all untracked files as dirty and assumes it is run inside a git worktree.
<!-- END_FILE_RESEARCH: sources/cloud-native/containers-storage/hack/tree_status.sh -->
