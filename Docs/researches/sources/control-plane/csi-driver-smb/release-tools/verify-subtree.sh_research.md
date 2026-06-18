<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-smb/release-tools/verify-subtree.sh -->
# sources/control-plane/csi-driver-smb/release-tools/verify-subtree.sh

Purpose: Verifies that a directory managed by `git subtree` contains no non-upstream local modifications.

Important behavior: Requires a directory argument. It finds the latest non-merge commit touching that directory with `git log --remove-empty --no-merges`; if any exists, it prints the relevant log and exits nonzero, otherwise reports a clean upstream copy.

Control flow: Simple argument validation and git query branch.

State and persistence behavior: Read-only git inspection.

Dependencies and integration points: Useful for imported `release-tools` subtrees in CSI repos, where merge commits from subtree pulls are expected but direct edits are not.

Risks: It trusts merge commits as upstream-only; a manual edit hidden in a merge commit would bypass the check, as the comment notes. It must be run from the right repo context.

Test signals: Static git-history cleanliness signal.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-smb/release-tools/verify-subtree.sh -->
