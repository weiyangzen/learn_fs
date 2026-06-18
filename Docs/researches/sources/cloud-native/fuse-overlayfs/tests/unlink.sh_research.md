<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/fuse-overlayfs/tests/unlink.sh -->
# sources/cloud-native/fuse-overlayfs/tests/unlink.sh

## Purpose
Tests unlink and hardlink semantics through a simple `fuse-overlayfs` mount. It verifies removing a lower-layer file hides it and that hardlinked upper files preserve content and link behavior after one name is removed and recreated.

## Important APIs, Types, And Functions
- Uses POSIX shell with `set -ex`.
- Mounts `fuse-overlayfs` with `lowerdir`, `upperdir`, `workdir`, `suid`, and `dev`.
- Uses `unlink`, `rm`, `ln`, `grep`, and an umount status override via `EXPECT_UMOUNT_STATUS`.

## Control Flow
The script creates `unlink-test`, prepares a lower file `a`, mounts the overlay, unlinks `merged/a`, and asserts it is no longer visible. It then creates `merged/foo`, hardlinks `foo2`, removes `foo`, checks `foo2`, recreates `foo` as a hardlink to `foo2`, appends through `foo2`, and verifies both names expose the combined content before unmounting.

## State And Persistence
State is local to `unlink-test`, which is removed at startup but not explicitly removed at the end. Overlay upper state is inspected indirectly through merged visibility only.

## Dependencies And Integration Points
Depends on `fuse-overlayfs` and hardlink support in the backing filesystem. It complements the larger stress unlink/hardlink tests with a small deterministic regression case.

## Risks And Edge Cases
The script does not install an EXIT trap, so interrupted runs can leave a mounted test tree. It assumes the current directory is safe for creating `unlink-test`. The `suid,dev` options may be relevant to privilege-sensitive environments.

## Test Signals
Failures catch regressions where lower unlinks fail to create a hiding entry, hardlink content is lost after unlink/relink, or unmount status differs from `EXPECT_UMOUNT_STATUS`.
<!-- END_FILE_RESEARCH: sources/cloud-native/fuse-overlayfs/tests/unlink.sh -->
