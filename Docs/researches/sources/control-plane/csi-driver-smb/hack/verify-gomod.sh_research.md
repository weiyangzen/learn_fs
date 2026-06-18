# sources/control-plane/csi-driver-smb/hack/verify-gomod.sh

## Purpose
Verifies module and vendor state are tidy and reproducible.

## Important APIs, Types, and Functions
Runs `go mod tidy`, `go mod vendor`, `git diff`, and `go list -mod readonly -m all`.

## Control Flow
Tidies and vendors, fails if any git diff remains, then lists all modules in readonly mode.

## State and Persistence
May mutate `go.mod`, `go.sum`, and vendor before failing, which is intentional for detecting required updates.

## Dependencies
Requires Go toolchain, git, module network/cache, and vendor support.

## Integration Points
CI gate and companion to dependency update scripts.

## Risks and Edge Cases
Running in a dirty worktree can conflate existing diffs with gomod changes. Network-dependent module resolution can make verification flaky.

## Test Signals
No git diff after tidy/vendor and successful readonly module listing.
