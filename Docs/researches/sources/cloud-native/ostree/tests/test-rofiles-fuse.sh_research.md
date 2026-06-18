# sources/cloud-native/ostree/tests/test-rofiles-fuse.sh

## Purpose
This integration test validates `rofiles-fuse` read-only checkout behavior, allowed creation of new mutable files, deletion, commit-back behavior, hardlink fallback, flock creation, copyup mode, xattr changes, symlink handling, and optional fsverity copyup.

## Important APIs, Types, And Functions
It uses `skip_without_fuse`, `skip_without_user_xattrs`, `setup_test_repository`, `rofiles-fuse`, `fusermount`, `ostree checkout -H/-U/-UH`, `ostree commit --link-checkout-speedup`, `setfattr`, `getfattr`, `flock`, `fsverity enable`, and helper functions `copyup_reset` and `assert_test_file`.

## Control Flow
The test creates a hardlink checkout, mounts it through `rofiles-fuse`, confirms existing content is readable, verifies truncation/chmod/chown/xattr mutation of existing read-only files fails, creates new files and directories through the mount, writes through a new symlink, sets xattrs, deletes existing files/dirs, commits the modified checkout, and verifies checkout copy fallback across the FUSE mount. It then remounts with `--copyup` several times to test truncation, xattr changes, writes through symlinks preserving symlink identity, new-file creation plus `sed -i` rename behavior, and fsverity-enabled copyup when supported.

## State And Persistence
State spans the OSTree repo, hardlink checkout `checkout-test2`, FUSE mount `mnt`, xattrs, deleted paths, new files, copied-up replacement inodes, and optional fsverity metadata. Cleanup unmounts the FUSE mount through an exit hook.

## Dependencies And Integration Points
This integrates FUSE, rofiles-fuse, checkout hardlink/copy modes, xattr tools, chown/chmod errors, commit link speedups, flock, sed rename behavior, and fsverity if available.

## Risks
Read-only existing files must not be mutated unless copyup mode is active. Copyup must replace regular file inodes while preserving symlink objects. Cross-device hardlink checkout must fall back or fail clearly. FUSE cleanup and host feature availability are common flake risks.

## Test Signals
Thirteen TAP results cover mount, failed mutations, new content, xattrs, deletion, commit, checkout fallback, flock, copyup mount, copyup behavior, and optional fsverity copyup skip/pass.
