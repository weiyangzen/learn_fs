# sources/control-plane/csi-driver-smb/hack/verify-update.sh

## Purpose
Checks whether previous update steps left the worktree dirty.

## Important APIs, Types, and Functions
Runs `git diff --shortstat`, prints full diff on failure, and exits nonzero.

## Control Flow
If any diff exists, reports dependency update changed files; otherwise prints Done.

## State and Persistence
Read-only.

## Dependencies
Requires git.

## Integration Points
Used after update scripts in CI to enforce committed generated output.

## Risks and Edge Cases
Any pre-existing uncommitted change causes failure, not only dependency updates.

## Test Signals
No shortstat output and zero exit status.
