<!-- BEGIN_FILE_RESEARCH: sources/control-plane/beegfs-csi-driver/release-tools/verify-subtree.sh -->
# sources/control-plane/beegfs-csi-driver/release-tools/verify-subtree.sh

Purpose: guard that a directory managed by `git subtree` remains an upstream-only copy.
Important APIs/functions: accepts exactly one directory argument and uses `git log -n1 --remove-empty --format=%H --no-merges -- <dir>` to find non-merge commits touching that path.
Control flow/state: validates input, queries git history, prints the non-merge log and exits 1 if any local non-merge change exists, otherwise reports the directory as clean. It has no persistent state.
Dependencies/integration: depends on git history shape where subtree updates are merge commits and local edits are non-merge commits.
Risks/test signals: can be bypassed by editing subtree files inside a merge commit; shallow clones may hide history; path renames can affect detection. Success is no non-merge revision for the directory.
<!-- END_FILE_RESEARCH: sources/control-plane/beegfs-csi-driver/release-tools/verify-subtree.sh -->
