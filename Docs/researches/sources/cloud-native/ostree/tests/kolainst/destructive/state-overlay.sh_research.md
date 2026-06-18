<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/ostree/tests/kolainst/destructive/state-overlay.sh -->
## sources/cloud-native/ostree/tests/kolainst/destructive/state-overlay.sh

Purpose: tests `ostree-state-overlay@.service` persistence and shadowing behavior for top-level mutable state overlays.

Important APIs/functions: creates a `foobar` commit with top-level content, enables `ostree-state-overlay@foobar.service`, uses reboot phases to mutate overlay contents, and upgrades back to a base commit.

Control flow/state: phase 1 commits `/foobar` content and rebases. Phase 2 verifies `/foobar` is overlay, creates persistent state files, shadows base files with changed types/symlinks/deletions/opaque dirs, and reboots. Phase 3 verifies state and shadowing persisted across reboot, commits an upgrade removing the top-level content, upgrades and reboots. Phase 4 verifies state files persist while base shadowings are gone/restored.

Dependencies/integration: requires rpm-ostree, systemd template service, overlayfs, reboot harness, and host commit.

Risks/test signals: manipulates root-level paths and overlay state. Signals are mount source `overlay`, file contents/types, deleted/restored base paths, symlink targets, and opaque dir behavior.
<!-- END_FILE_RESEARCH: sources/cloud-native/ostree/tests/kolainst/destructive/state-overlay.sh -->
