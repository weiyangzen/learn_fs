<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/ostree/tests/kolainst/nondestructive/itest-remotes.sh -->
## sources/cloud-native/ostree/tests/kolainst/nondestructive/itest-remotes.sh

Purpose: verifies installed systems have at least one OSTree remote configured, guarding `/etc/ostree/remotes.d` handling.

Important APIs/functions: runs `ostree remote list > remotes.txt` and fails if the output is empty.

Control flow/state: creates a tempdir and cleanup trap; otherwise read-only against system remote configuration.

Dependencies/integration: requires `libinsttest.sh`, rpm-ostree-derived host context, and `ostree` CLI.

Risks/test signals: image variants without remotes will fail even if OSTree itself is functional. Signal is non-empty `remotes.txt`.
<!-- END_FILE_RESEARCH: sources/cloud-native/ostree/tests/kolainst/nondestructive/itest-remotes.sh -->
