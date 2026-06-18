## sources/control-plane/csi-driver-iscsi/hack/verify-update.sh

Purpose: verifies that dependency update operations did not leave uncommitted changes.

Control flow checks `git diff --shortstat`; if any diff exists it prints the full diff and exits nonzero, otherwise prints done. State is read-only git working tree inspection.

Dependencies are git. Risks include considering unrelated pre-existing user changes as update failures and ignoring untracked files. Test signal is manual or CI invocation after update scripts.
