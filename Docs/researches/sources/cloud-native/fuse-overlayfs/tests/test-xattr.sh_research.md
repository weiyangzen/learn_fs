<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/fuse-overlayfs/tests/test-xattr.sh -->
# sources/cloud-native/fuse-overlayfs/tests/test-xattr.sh

## Purpose
Exercises extended attribute support in `fuse-overlayfs`: setting, reading, listing, removing, directory xattrs, lower-layer xattr visibility, internal xattr filtering, large values, copy-up preservation, xattr-triggered copy-up, multiple xattrs, and the `noxattrs=1` mount option.

## Important APIs, Types, And Functions
- `cleanup` is the only shell function and performs unmount/removal on exit.
- Test operations use `setfattr`, `getfattr`, `grep`, Python-generated 4000-byte values, `test -f upper/...`, and `fuse-overlayfs` mount options.
- The `noxattrs=1` case verifies that setting a user xattr fails.

## Control Flow
Eleven isolated cases mount a fresh overlay, run one xattr scenario, assert expected values or errors, then unmount and delete layers. Lower-layer cases prepare xattrs before mounting. Copy-up cases modify or set xattrs on lower files and then validate that metadata remains visible and, for xattr setting, that the file appears in the upperdir.

## State And Persistence
Temporary state is under `/tmp/test-xattr.*`. Each case deletes layers, so xattr state is not shared. The copy-up tests intentionally inspect the backing `upper` path before teardown, which couples the test to upperdir implementation details.

## Dependencies And Integration Points
Requires xattr-capable backing filesystems and the attr tools package. Integrates with `fuse-overlayfs` internal metadata filtering by checking that `user.fuseoverlayfs.origin` does not leak through `getfattr -d`.

## Risks And Edge Cases
Some backing filesystems may reject large xattrs or user xattrs, causing environment-specific failures. Internal xattr setup ignores failure, so that test becomes weaker if setting the lower internal xattr is unsupported. The `noxattrs` case assumes failure of `setfattr` is observable through the command exit status.

## Test Signals
Passing output ends with `All xattr tests passed!`. Strong signals include copy-up preservation of lower xattrs, upperdir materialization after setting xattrs on lower files, and filtering of internal `fuseoverlayfs` metadata.
<!-- END_FILE_RESEARCH: sources/cloud-native/fuse-overlayfs/tests/test-xattr.sh -->
