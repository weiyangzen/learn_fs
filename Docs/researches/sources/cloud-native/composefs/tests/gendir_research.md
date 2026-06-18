# sources/cloud-native/composefs/tests/gendir

## Purpose
`gendir` is a Python randomized filesystem tree generator for composefs round-trip and FUSE tests. It creates directories, files, symlinks, FIFOs, optional devices, optional whiteouts, and user xattrs.

## Important APIs, Types, And Functions
Important helpers include `Chance`, `gen_filename`, `gen_filenames`, `gen_hierarchy`, `set_user_xattr`, `make_regular_file`, `make_symlink`, `make_node`, `make_whiteout`, `make_fifo`, `make_file`, and `make_dir`.

## Control Flow
The script seeds Python randomness from `--seed` or os randomness, builds a random directory hierarchy, creates the root, then creates each directory and its random children. File content sizes are mostly small with occasional large files; some data is reused.

## State And Persistence
It mutates the target filesystem path and records no separate manifest. It may create xattrs and special files when permissions allow.

## Dependencies And Integration Points
Used by `test-random-fuse.sh` and `integration.sh`. Depends on Python filesystem APIs and optional privilege for `mknod`.

## Risks
Randomness can make failures hard to reproduce unless the printed seed is captured. The `--unreadable` byte-name mode can stress encoding assumptions. Special files and xattrs depend on host permissions/filesystem support.

## Test Signals
The generator feeds randomized coverage for writer ingestion, xattr handling, digest store object emission, whiteout conversion, FUSE equivalence, and dump reproducibility.
