# sources/cloud-native/fuse-overlayfs/tests/test-hardlinks.sh

## Purpose
`tests/test-hardlinks.sh` validates hardlink creation, shared data, link counts, unlink survival, cross-directory links, rename interaction, relinking, and lower-layer hardlink copy-up cycles.

## Important APIs, Types, And Functions
The script uses `ln`, `rm`, `mv`, `stat`, `chown`, and `grep` across fresh fuse-overlayfs mounts.

## Control Flow
It creates writable overlays and runs nine scenarios: basic hardlink creation, data sharing through links, removing one link, linking to a lower-layer file, multiple hardlinks, rename with hardlinks, cross-directory hardlinks, relink after delete, and a containers/storage-like flow where lower-layer hardlinked binaries are chowned, one link is removed, and links are recreated in both orders.

## State And Persistence
State lives in temporary lower/upper/workdir/merged trees. The critical persistent state is upper-layer copied-up hardlink topology and inode/link count consistency.

## Dependencies And Integration Points
Exercises `link`, `unlink`/`do_rm`, `rename`, copy-up, inode table registration, nlink calculation, and inode invalidation after unlinking one hardlink while survivors remain.

## Risks
Some link-count assertions use `-ge`, so they tolerate over-counting. The test does not inspect upper-layer inode equality after every copy-up, mostly merged view/content behavior.

## Test Signals
Pass indicates hardlinked overlay entries share data, survive unlink/rename/relink operations, and lower-layer hardlinks remain usable through chown/unlink/link cycles that previously caused container storage failures.
