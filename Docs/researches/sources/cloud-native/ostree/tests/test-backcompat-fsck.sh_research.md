# sources/cloud-native/ostree/tests/test-backcompat-fsck.sh

Purpose: verifies fsck compatibility for archive commits containing many user xattrs, including optional cross-check with the system-installed OSTree.

Important APIs/functions: `skip_without_user_xattrs`, `setup_test_repository "archive"`, `checkout`, `setfattr`, `commit --canonical-permissions --consume`, `fsck`, and optional `/usr/bin/ostree --repo=repo fsck`.

Control flow: checks out `test2`, adds 100 `user.*` xattrs to a file, recommits with canonical permissions, fscks with the built/test OSTree, then if `/usr/bin/ostree` exists, runs it with `LD_LIBRARY_PATH` unset to validate backward compatibility.

State/persistence: writes xattr-rich content objects and consumes the checkout. Dependencies include user xattrs and optionally a system OSTree binary.

Integration/risk/test signals: protects object/xattr canonicalization compatibility. Risks are environment-dependent skips and installed binary version variability. TAP reports fsck and optional compat.
