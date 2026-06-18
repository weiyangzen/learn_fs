# sources/cloud-native/fuse-overlayfs/tests/test-rename.sh

## Purpose
`tests/test-rename.sh` validates rename behavior including lower-layer copy-up/whiteout, overwrite, cross-directory moves, recreate-after-rename, and Linux `renameat2` flags.

## Important APIs, Types, And Functions
The script compiles a helper C program that invokes `SYS_renameat2` with `RENAME_NOREPLACE` or `RENAME_EXCHANGE`. It also uses `mv`, `grep`, `stat`, and whiteout inspection.

## Control Flow
Ten scenarios cover upper-layer basic rename, renaming lower files with whiteout creation, renaming lower directories, overwrite of existing files, `RENAME_NOREPLACE` failure/success, `RENAME_EXCHANGE` for files and directories, renaming over lower-layer destination, cross-directory file moves, and recreating a lower name after it was moved.

## State And Persistence
Each scenario creates temporary lower/upper/workdir/merged state. Persistent upper effects include copied-up renamed files/directories, whiteouts at old names, replaced destination files, exchanged directory entries, and recreated names.

## Dependencies And Integration Points
Directly exercises `OverlayFs::rename`, `get_node_up`, `empty_upper_dir`, `whiteout::create_whiteout/delete_whiteout`, `renameat2` wrapper, inode table updates, parent cache invalidation, and directory reload behavior. Requires GCC and kernel/filesystem support for `renameat2` flags.

## Risks
If `renameat2` is unsupported, helper-driven tests fail as environmental failures. Directory lower-layer rename semantics are subtle; implementation currently rejects some lower/merged directory renames with `EXDEV`, so test expectations are important to keep aligned with actual supported behavior. Whiteout validation allows either char-device or `.wh.` format.

## Test Signals
Pass indicates rename paths maintain visible content, enforce no-replace, atomically exchange entries, generate whiteouts for lower source names, and keep directory/parent caches coherent after moves.
