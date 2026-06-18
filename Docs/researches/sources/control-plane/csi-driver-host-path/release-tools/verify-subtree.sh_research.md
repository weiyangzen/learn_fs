## sources/control-plane/csi-driver-host-path/release-tools/verify-subtree.sh

Purpose: verifies that a git-subtree-managed directory has no local non-upstream modifications.

Control flow requires a directory argument, finds the most recent non-merge commit touching that directory with `git log --remove-empty --no-merges`, and fails with the non-merge log if one exists; otherwise it reports the directory as a clean upstream copy.

State is git history only. Dependencies are POSIX shell and git. Risks include trusting merge commits completely, so local edits hidden in merge commits bypass the check; also, legitimate downstream patches are rejected. Test signal is CI failure with relevant commit history.
