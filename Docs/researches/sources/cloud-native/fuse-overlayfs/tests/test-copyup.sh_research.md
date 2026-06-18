# sources/cloud-native/fuse-overlayfs/tests/test-copyup.sh

## Purpose
`tests/test-copyup.sh` validates copy-up behavior for regular files, metadata, symlinks, xattrs, directories, open-for-write, truncate, nested paths, and repeated copy-ups.

## Important APIs, Types, And Functions
The script uses `fuse-overlayfs`, `dd`, `md5sum`, `chmod`, `touch`, symlink commands, `setfattr/getfattr`, Python file I/O, `truncate`, and shell loops. Cleanup unmounts and removes a temporary test directory.

## Control Flow
Each test creates fresh lower/upper/workdir/merged directories, mounts a writable overlay, triggers copy-up by write/chmod/create/truncate/open, validates merged and upper-layer effects, unmounts, and resets. Scenarios cover content preservation for a 400 KiB file, permission/timestamp copy-up, symlink target behavior, xattr preservation before and after copy-up, directory and nested directory copy-up, write-open copy-up, truncation, and twenty sequential copy-ups.

## State And Persistence
Persistent state is test-local lower, upper, workdir, merged content. The key persisted artifact under validation is the upper-layer copy created from lower-layer input.

## Dependencies And Integration Points
Exercises `OverlayInner::get_node_up`, `copyup::copyup`, `open`, `setattr`, `create`, `xattr` wrappers, directory creation, and path-safe upper-layer operations. Requires xattr tools and Python.

## Risks
Some metadata tests only assert existence rather than exact preserved mode/timestamp, so regressions could slip through. `md5sum` checks only the original prefix after append. Environment must support FUSE and user xattrs.

## Test Signals
Pass indicates copy-up preserves data and user xattrs, keeps symlinks usable, creates upper nested directory structure, supports open-for-write and truncate copy-up paths, and handles multiple files without cross-contamination.
