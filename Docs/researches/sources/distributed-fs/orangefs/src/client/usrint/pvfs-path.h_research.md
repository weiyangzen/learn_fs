## sources/distributed-fs/orangefs/src/client/usrint/pvfs-path.h

Purpose: Defines the internal `PVFS_path_t` carrier used by the usrint path layer to pass an apparently plain expanded pathname while retaining resolution state, original input, OrangeFS mount metadata, and lookup progress.

Important APIs, types, and functions: `PVFS_path_t` stores `orig_path`, `pvfs_path`, `fs_id`, last looked-up `handle`, remaining `filename`, an `rc`, state flags in `magic`, and an embedded `expanded_path[PVFS_PATH_MAX + 1]`. Macros validate and manipulate flags such as `PVFS_PATH_QUALIFIED`, `EXPANDED`, `RESOLVED`, `MNTPOINT`, `LOOKEDUP`, `FOLLOWSYM`, and `ERROR`. Inline helpers are `PVFS_new_path`, `PVFS_path_from_expanded`, `PVFS_free_path`, and `PVFS_free_expanded`; exported path APIs include `PVFS_qualify_path`, `PVFS_expand_path`, `is_pvfs_path`, and `split_pathname`.

Control flow: Callers can pass a raw path to qualification/expansion, which allocates a `PVFS_path_t`, fills `expanded_path`, and returns a pointer to that embedded buffer. Later layers recover the containing struct through pointer arithmetic in `PVFS_path_from_expanded` and check the high bits of `magic` before trusting the object.

State and persistence: All state is heap-local and process-local. No persistent storage exists; flags only describe the current path-processing lifecycle.

Dependencies and integration points: Depends on `<pvfs2.h>`, `PVFS_PATH_MAX`, and OrangeFS path resolution routines implemented elsewhere. It bridges POSIX-like path strings into usrint open/stat/unlink and mount-resolution code.

Risks and test signals: `PVFS_new_path` does not check `malloc` before `memset`. `PVFS_path_from_expanded` performs unchecked container recovery and only becomes safe after `VALID_PATH_MAGIC`. `orig_path` is a borrowed pointer, so caller lifetime matters. Test raw paths, already-expanded PVFS buffers, invalid pointers, long paths, free-on-expanded behavior, and repeated qualify/expand flag transitions.
