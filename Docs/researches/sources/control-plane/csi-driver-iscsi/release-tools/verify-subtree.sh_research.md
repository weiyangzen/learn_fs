# sources/control-plane/csi-driver-iscsi/release-tools/verify-subtree.sh

Purpose: verifies that a git subtree-managed directory has no local non-merge commits modifying it.

Important APIs and types: takes one required directory argument.

Control flow: finds the latest non-merge commit touching the directory with `git log --remove-empty --no-merges`. If one exists, prints the non-upstream log and exits nonzero; otherwise reports the directory as a clean upstream copy.

State and persistence: read-only Git history inspection.

Dependencies and integration: intended for repos importing `release-tools` via git subtree.

Risks: it trusts merge commits as upstream imports; local edits hidden inside a merge commit can bypass the check, as the comment notes. Requires full enough Git history for the directory.

Test signals: Prow verifier pass/fail and printed git log.
