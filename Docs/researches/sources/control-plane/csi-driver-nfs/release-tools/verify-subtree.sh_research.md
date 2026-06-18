## sources/control-plane/csi-driver-nfs/release-tools/verify-subtree.sh

Purpose: checks that a directory managed through `git subtree` has not received local non-merge commits. It is intended for vendored release-tool copies or other upstream mirrored directories where changes should only arrive through subtree merge commits.

Important flow: the script requires one directory argument, then runs `git log -n1 --remove-empty --format=format:%H --no-merges -- "$DIR"`. If any non-merge commit touched the path, it prints the non-merge log for that directory and exits with failure; otherwise it reports the directory as a clean upstream copy.

State is entirely git history; no files are modified. Dependencies are POSIX shell and git. Risks include false negatives when a merge commit contains hand edits, false positives when legitimate local patches are expected, and reliance on local shallow history being complete enough. Test signal is a release verification failure when subtree-managed content drifts.
