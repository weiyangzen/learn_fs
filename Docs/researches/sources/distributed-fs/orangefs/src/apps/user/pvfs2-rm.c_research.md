<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/orangefs/src/apps/user/pvfs2-rm.c -->
# sources/distributed-fs/orangefs/src/apps/user/pvfs2-rm.c

## Purpose
Older OrangeFS-specific remove utility that uses PVFS-aware stat and recursive delete helpers rather than FTS.

## Important APIs, Types, And Functions
`options` stores force, recursive, count, and filenames. `main` loops over input paths, calls `pvfs_lstat_mask(..., PVFS_ATTR_SYS_TYPE)`, dispatches directories to `recursive_delete_dir` when `-r` is set, and unlinks non-directories. `parse_args` handles `-r`, `-f`, and help; `usage` prints syntax.

## Control Flow
Missing files are ignored under force and reported otherwise. Directories require recursive mode; non-directories are removed with `unlink`. The final exit code is failure if any path produced an error.

## State And Persistence
Destructively removes OrangeFS files and possibly directory trees. No local persistence.

## Dependencies And Integration Points
Depends on `orange.h`, `recursive-remove.h`, PVFS stat wrappers, and the VFS unlink path. It is a simpler predecessor/alternative to `ofs_rm.c`.

## Risks And Test Signals
Risks include no interactive/verbose support, reliance on PVFS-only `pvfs_lstat_mask` so non-PVFS paths may fail, recursive helper behavior hidden in another module, and no NULL terminator in `filenames` array because the code tracks count separately. Test signals are PVFS files, missing paths with/without force, directory removal with/without recursive mode, symlink behavior, and mixed argument exit status.
<!-- END_FILE_RESEARCH: sources/distributed-fs/orangefs/src/apps/user/pvfs2-rm.c -->
