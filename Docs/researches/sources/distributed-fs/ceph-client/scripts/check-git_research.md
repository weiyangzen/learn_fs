# sources/distributed-fs/ceph-client/scripts/check-git

## Purpose
`check-git` verifies that the kernel source tree is a Git repository at its top level.

## APIs, Types, And Functions
It uses `git -C <srctree> rev-parse --verify HEAD` and `git rev-parse --show-cdup`.

## Control Flow
The script derives `srctree` as `scripts/..`, fails if HEAD cannot be verified, and fails if `show-cdup` indicates the command is not at the repository root.

## State And Persistence
No state is stored.

## Dependencies And Integration Points
It depends on Git and a repository checkout. It integrates with build or release steps that require Git metadata.

## Risks And Test Signals
Risks include failure in source archives without `.git` and ambiguous behavior in worktrees/submodules. Test signals are exit 0 at the top of a valid Git tree and exit 1 outside one.
