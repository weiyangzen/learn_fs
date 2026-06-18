<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/hack/verify-update.sh -->
# sources/control-plane/csi-driver-nfs/hack/verify-update.sh

## Purpose
Checks that dependency update operations did not leave uncommitted repository changes.

## Important APIs, Types, and Functions
The script runs `git diff --shortstat`, and if non-empty, prints `git --no-pager diff` and exits one.

## Control Flow, State, and Persistence
It is read-only and purely checks the working tree after another update step has run. It prints "Done" on a clean tree.

## Dependencies and Integration Points
It depends on git and is intended to follow scripts such as `update-dependencies.sh` in CI to ensure generated files are checked in.

## Risks and Test Signals
Risks include failing on unrelated local changes and not checking untracked files. Signals are an empty `git diff --shortstat` and zero exit status.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/hack/verify-update.sh -->
