# sources/cloud-native/moby/hack/validate/dco

## Purpose
Validates Developer Certificate of Origin signoffs on changed commits.

## Important APIs and Types
Uses `validate_diff`, `validate_log`, `dcoRegex`, `githubUsernameRegex`, and `check_dco`.

## Control Flow, State, and Persistence
The script sums added/deleted lines. If there are changes, it iterates changed commits, skips contentless commits, checks commit bodies for a valid `Signed-off-by:` marker, and fails with a list of bad commits.

## Dependencies, Integration Points, Risks, and Test Signals
Depends on git history and `.validate`. Risks include regex rejecting unusual but valid identities, shell array behavior with many commits, and bypass when diff has no additions/deletions. CI DCO validation is the signal.
