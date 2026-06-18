# sources/cloud-native/ostree/tests/test-basic-user.sh

Purpose: wrapper plus extra tests for `bare-user` repositories with user xattrs.

Important APIs/functions: `skip_without_user_xattrs`, `setup_test_repository bare-user`, sources `basic-test.sh`, uses object-path helpers, `checkout -U -H`, `commit --statoverride`, `--link-checkout-speedup`, `--owner-uid/gid`, and `-I` devino canonicalization.

Control flow: runs shared basic tests with six extras, resets state, verifies committed object modes, checkout modes, unwritable/unreadable file handling, unioning component checkouts with distinct ownership, and precedence between owner overrides, link-checkout speedup, and devino cache reuse.

State/persistence: creates bare-user content objects, component refs, rootfs checkouts, and mode-specific object files. Dependencies include user xattrs and uid/gid support.

Integration/risk/test signals: protects user-mode storage semantics and ownership preservation. Risks include many setup resets and filesystem permission assumptions. TAP ok lines report each mode-specific behavior.
