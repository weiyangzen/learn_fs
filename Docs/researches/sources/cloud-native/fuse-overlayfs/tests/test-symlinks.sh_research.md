<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/fuse-overlayfs/tests/test-symlinks.sh -->
# sources/cloud-native/fuse-overlayfs/tests/test-symlinks.sh

## Purpose
Validates symlink behavior through `fuse-overlayfs`, including newly created symlinks, dangling links, links from lower layers, directory symlinks, symlink timestamp updates, upper symlinks overriding lower files, relative paths, chained symlink resolution, and replacing lower files with symlinks.

## Important APIs, Types, And Functions
- `cleanup` unmounts `$MERGED` and removes the temporary test directory on exit.
- Each test manually creates `lower`, `upper`, `workdir`, and `merged`, invokes `fuse-overlayfs -o lowerdir=...,upperdir=...,workdir=...`, performs shell assertions, unmounts, and removes layer directories.
- Uses `ln -s`, `readlink`, `test -L`, `test -d`, `touch -h -d`, `stat --format`, `grep`, and `rm`.

## Control Flow
The script executes ten independent cases under `set -xeuo pipefail`. It first verifies basic symlink creation and target traversal, then dangling link metadata without target access, lower-layer symlink visibility, directory symlink traversal, symlink timestamp mutation via `touch -h`, link removal without deleting the target, upper-layer symlink precedence over a lower regular file, relative link traversal in nested directories, chained link resolution, and lower-file deletion followed by upper symlink replacement.

## State And Persistence
All state lives under `/tmp/test-symlinks.*`. Each test tears down its layers after unmounting, so cases are isolated and do not rely on prior whiteouts or upperdir contents.

## Dependencies And Integration Points
Depends on `fuse-overlayfs`, mount permissions, GNU `stat`, and symlink-aware `touch -h`. It specifically exercises overlay path resolution and copy-up/whiteout interactions that regular file tests do not cover.

## Risks And Edge Cases
The timestamp test assumes the filesystem preserves symlink timestamps and formats `stat --format "%y"` with the expected second value. Absolute symlink behavior is mentioned in the header but the body only tests a relative nested symlink. Because each case is isolated, it does not test symlink persistence across remounts.

## Test Signals
Passing output ends with `All symlink tests passed!`. Failures indicate regressions in link metadata, overlay precedence, target traversal, or file-versus-symlink replacement behavior.
<!-- END_FILE_RESEARCH: sources/cloud-native/fuse-overlayfs/tests/test-symlinks.sh -->
