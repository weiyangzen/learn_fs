# sources/control-plane/csi-driver-smb/hack/verify-helm-chart-files.sh

## Purpose
Verifies packaged Helm chart archives match committed chart sources.

## Important APIs, Types, and Functions
Disables git filemode tracking, checks initial diff, extracts chart `.tgz` files into chart directories, then checks git diff again.

## Control Flow
Fails immediately if the worktree is dirty, expands each packaged chart, and fails if expansion changes committed files.

## State and Persistence
Mutates git config `core.filemode` and extracts archives into chart directories during verification.

## Dependencies
Requires git, tar, chart archives, and shell glob behavior.

## Integration Points
Called by `verify-all.sh`; remediation is Helm package update.

## Risks and Edge Cases
Dirty worktree blocks verification. Extraction can overwrite files. The `[ -f $dir/*.tgz ]` glob test is fragile with multiple/no archives.

## Test Signals
No git diff after extraction and "chart tgz files verified."
