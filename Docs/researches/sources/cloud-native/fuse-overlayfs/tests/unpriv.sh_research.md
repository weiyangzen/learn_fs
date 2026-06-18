<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/fuse-overlayfs/tests/unpriv.sh -->
# sources/cloud-native/fuse-overlayfs/tests/unpriv.sh

## Purpose
Validates unprivileged `fuse-overlayfs` behavior, especially lower-file deletion, mode changes, whiteout representation, security xattr isolation with `xattr_permissions=2`, and UID/GID preservation across `chgrp` and `chmod` inside user namespaces.

## Important APIs, Types, And Functions
- Starts with `test $(id -u) -gt 0`, requiring a non-root user.
- Uses `fusermount -u` for unprivileged unmounts.
- Uses `unshare -r setcap/getcap` to exercise security capabilities in a root user namespace.
- Uses `podman unshare` to check ownership after group and mode changes.
- Honors `FUSE_OVERLAYFS_DISABLE_OVL_WHITEOUT` to decide whether whiteout should be `.wh.a` or a character device at `upper/a`.

## Control Flow
The first overlay mounts read-only lower files, deletes `merged/a`, chmods `merged/b` to mode `406`, verifies merged and upper modes, and checks the expected whiteout representation. After unmount, it prepares an upper file with a capability, mounts with `xattr_permissions=2`, verifies the security xattr is hidden from the merged view until set through the merged file, then confirms ownership remains `0:1` after `podman unshare chgrp 1` and after `chmod 600`.

## State And Persistence
The script uses a local `unpriv-test` directory, resets layer directories between the two phases, and leaves cleanup to the initial `rm -rf` on subsequent runs. It intentionally inspects upperdir whiteouts and metadata as persistent side effects of merged operations.

## Dependencies And Integration Points
Requires unprivileged FUSE, user namespaces, `fusermount`, `setcap/getcap`, and Podman. It directly tests `fuse-overlayfs` behavior used by rootless container stacks.

## Risks And Edge Cases
Environment availability is the main risk: user namespaces, Podman, file capabilities, and whiteout implementation can vary. The script has no trap, so failed unmounts can leave mounted state. Assertions are numeric and Linux-specific.

## Test Signals
The strongest signals are successful non-root mount/unmount, correct hiding of deleted lower files, correct upper mode after chmod, matching configured whiteout representation, security xattr isolation, and UID/GID preservation through metadata changes.
<!-- END_FILE_RESEARCH: sources/cloud-native/fuse-overlayfs/tests/unpriv.sh -->
