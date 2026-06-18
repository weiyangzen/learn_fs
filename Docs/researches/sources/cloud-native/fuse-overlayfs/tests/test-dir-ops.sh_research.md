# sources/cloud-native/fuse-overlayfs/tests/test-dir-ops.sh

## Purpose
`tests/test-dir-ops.sh` validates directory merge semantics, opaque directories, whiteout filtering, nlink computation, removal/recreation, nested operations, readdir correctness, and lower-layer priority.

## Important APIs, Types, And Functions
The script repeatedly mounts `fuse-overlayfs` over fresh test trees and uses mkdir, rm/rmdir, mknod/touch whiteouts, setfattr opaque markers, stat, grep, and ls counts.

## Control Flow
Fifteen isolated scenarios cover two-layer and three-layer merges, upper-over-lower shadowing, xattr and sentinel opaque directories, computed nlink and `static_nlink`, rmdir of lower content producing whiteouts, mkdir over deleted lower dirs, nested mkdir/rm, readdir updates after delete/add, whiteout filtering, rejecting non-empty rmdir, and multi-lower priority where the first lowerdir wins.

## State And Persistence
Creates temporary lower/upper/workdir/merged directories and persists whiteouts, opaque xattrs/sentinels, created dirs/files, and upper changes until each scenario cleanup.

## Dependencies And Integration Points
Directly exercises `load_dir_impl`, `do_lookup_file`, `reload_dir`, `build_dir_entries`, `do_rm`, `mkdir`, whiteout helpers, and nlink logic in `rpl_stat_with_path`. Requires FUSE, xattr tools, and optionally mknod.

## Risks
Directory listing counts depend on `ls` behavior and locale minimally. Char-device whiteout paths are conditional. The test focuses on visible behavior and does not inspect internal inode-table state.

## Test Signals
Pass is a strong signal for overlay directory layering semantics, opaque stop conditions, deletion hiding lower entries, correct readdir contents, nlink updates, and correct lowerdir ordering.
