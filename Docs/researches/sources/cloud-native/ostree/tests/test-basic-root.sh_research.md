# sources/cloud-native/ostree/tests/test-basic-root.sh

Purpose: root-only ownership behavior tests for bare repositories and checkout modes.

Important APIs/functions: `id -u`, `skip`, `setup_test_repository "bare"`, `$OSTREE checkout`, `$OSTREE commit --owner-uid`, `$OSTREE ls`, hardlink checkout `-H`, user checkout `-U`, and `stat`.

Control flow: skips unless running as uid 0, commits a tree with owner uid incremented from root, validates `ostree ls` ownership, checks hardlinked/copy checkouts preserve ownership, then confirms user-mode checkout maps ownership to the current user.

State/persistence: writes a bare repo commit and temporary checkouts. Dependencies include root privileges and filesystem ownership support.

Integration/risk/test signals: protects ownership preservation in privileged bare repo operations. Risks are container uid assumptions and lack of `-C` coverage noted in comments. One TAP case reports ownership.
