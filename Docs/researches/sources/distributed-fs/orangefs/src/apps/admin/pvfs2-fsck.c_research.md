# sources/distributed-fs/orangefs/src/apps/admin/pvfs2-fsck.c

## Purpose
`pvfs2-fsck.c` is an OrangeFS filesystem checker and optional repair tool. It creates or locates `/lost+found`, enumerates all server handles, traverses reachable directories, removes invalid dirents, verifies required datafile/dirdata backing handles, finds orphaned subtrees/files, salvages recoverable objects into lost+found, and removes leftover unreferenced data/dirdata objects when destructive mode is enabled.

## Important APIs, Types, And Functions
Key functions are `main`, `build_handlelist`, `traverse_directory_tree`, `match_dirdata`, `descend`, `verify_datafiles`, `find_sub_trees`, `fill_lost_and_found`, `cull_leftovers`, `create_lost_and_found`, `create_dirent`, `remove_directory_entry`, `remove_object`, handle-list helpers, `parse_args`, `get_type_str`, and `get_user_action_to_continue`. Key state includes `struct options`, global `fsck_opts`, global `laf_ref`, and `global_removals`.

## Control Flow
`main` parses mount/destructive/safety options, initializes PVFS, resolves the filesystem, gets credentials and server addresses, creates `/lost+found` before admin mode, switches all IO/meta servers to admin mode, builds a handle list including removal of reserved handles, and runs four passes. The first pass traverses `/`, removes broken dirents, checks datafiles and dirdata, and deletes unrecoverable objects. The second pass scans remaining handles for orphaned subtrees and collects other leftovers into an alternate list. The tool then leaves admin mode. The third pass tries to salvage orphaned metafiles/directories into lost+found after verifying their backing handles. The fourth pass removes leftover unreferenced data/dirdata/internal objects. Destructive operations are logged as `not` performed unless `-a`, `-p`, or `-y` enabled destructive mode.

## State And Persistence
In non-destructive mode, the tool mostly reports intended actions while still creating/looking up lost+found only if destructive mode allows actual mkdir. In destructive mode it persists significant metadata changes: new lost+found entries, removed directory entries, removed objects, and possibly lost+found creation. It also temporarily changes server mode to admin during scanning. Runtime state is held in per-server handle-list arrays and global options/removal count.

## Dependencies And Integration Points
The checker depends on OrangeFS sysint, management APIs, cached config handle ownership mapping, server admin mode, reserved-handle iteration, and management-only create/remove dirent/object operations. `pvfs2-fsck.h` declares the internal function and handle-list interfaces used in this implementation.

## Risks And Test Signals
Risks are high because destructive mode mutates filesystem metadata. There are many `assert` calls on runtime conditions, limited rollback, O(n) handle searches, path/mode changes that may leave servers in admin mode after abnormal termination, and subtle list ownership issues when matching handles across main and alternate lists. Safety prompting counts removals globally but only prompts in destructive mode. Tests should start with non-destructive dry runs on clean and intentionally damaged test filesystems, verify no changes under `-n`, exercise safety prompts with `-s`, confirm salvage naming (`lostfile.<handle>`, `lostdir.<handle>`), verify server mode restoration, and run post-fsck tree/data integrity checks.
