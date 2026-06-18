# sources/cloud-native/ostree/src/libostree/ostree-diff.c

## Purpose
This file implements directory diffing for OSTree trees and filesystem directories, producing modified, removed, and added arrays plus a simple printer.

## Important APIs, Types, And Functions
`get_file_checksum()` uses repo-file checksums directly for `OstreeRepoFile` inputs or computes xattr-aware file checksums from `GFileInfo`, optional xattrs, and regular-file streams. `OstreeDiffItem` is a boxed refcounted struct with source/target files, infos, and checksums. `diff_files()` compares file checksums. `diff_add_dir_recurse()` records all descendants of an added directory. `ostree_diff_dirs()` delegates to `ostree_diff_dirs_with_options()`. The options variant supports owner UID/GID overrides for target-side info. `ostree_diff_print()` prints `M`, `D`, and `A` lines relative to base paths.

## Control Flow, State, And Persistence
The main diff first adjusts flags if either repo disables xattrs or uses bare-user-only mode. If the source tree is `NULL`, the entire target tree is added. For repo-file directories, matching dirtree content checksums provide a fast path. Otherwise it enumerates source children to detect removals/modifications and recurses into matching directories, then enumerates target children to detect additions. State is in caller-owned `GPtrArray`s and boxed diff items.

## Dependencies And Integration Points
It depends on GLib/GIO, libglnx xattr helpers, repo-private `OstreeRepoFile` APIs, and core checksum functions. CLI/admin code can use the result arrays or printer.

## Risks And Test Signals
The algorithm performs two directory enumerations and checksum reads, so large trees and xattr-heavy filesystems are expensive. `devino_to_csum_cache` exists in the ABI-sized options struct but is unused here. Tests should cover repo fast-path equality, xattr-ignore behavior, type changes, owner remapping, added directory recursion, missing-file errors versus real I/O errors, symlinks, and stable ABI size of `OstreeDiffDirsOptions`.
