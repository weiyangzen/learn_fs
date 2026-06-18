<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/ostree/tests/kolainst/destructive/itest-bare-root.sh -->
## sources/cloud-native/ostree/tests/kolainst/destructive/itest-bare-root.sh

Purpose: raw OSTree root test for committing and checking out security xattrs from the host repo.

Important APIs/functions: uses `ostree checkout -H`, `setfattr`, `ostree commit --link-checkout-speedup`, `ostree fsck`, `ostree ls -X`, and `getfattr`.

Control flow/state: in `/ostree/repo/tmp`, checks out the host commit, replaces a symlink copy to avoid corruption, adds custom `security.*` xattrs to a symlink and directory, commits to `testref`, verifies xattrs are present only in the new ref, then checks out and verifies materialized xattrs.

Dependencies/integration: requires root, writable sysroot, xattr support, and a likely `/usr/bin/gtar` symlink.

Risks/test signals: host content assumption for `/usr/bin/gtar` may fail on some images. Signals are `ostree ls -X`, `getfattr`, and `ostree fsck`.
<!-- END_FILE_RESEARCH: sources/cloud-native/ostree/tests/kolainst/destructive/itest-bare-root.sh -->
