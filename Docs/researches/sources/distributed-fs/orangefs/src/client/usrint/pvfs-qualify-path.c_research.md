## sources/distributed-fs/orangefs/src/client/usrint/pvfs-qualify-path.c

Purpose: Implements `PVFS_qualify_path`, a symlink-blind canonicalizer that converts absolute or cwd-relative paths into a root-relative normalized path in a `PVFS_path_t` buffer.

Important APIs, types, and functions: The single exported function `PVFS_qualify_path(const char *path)` creates or reuses a `PVFS_path_t`, clears resolution/lookup flags, folds repeated slashes, removes `.` segments, handles `..` by backing up one component, and sets `PVFS_PATH_QUALIFIED`.

Control flow: Null input returns null. If the input is already the embedded buffer of a valid `PVFS_path_t`, that state object is reused; otherwise one is allocated. Already qualified or expanded paths return immediately. Relative paths start with `getcwd`; absolute paths seed the output with `/`. The scanner copies one component at a time and aborts on `PVFS_PATH_MAX` overflow.

State and persistence: Mutates only the `PVFS_path_t` flags and embedded buffer. No filesystem metadata is read except the process cwd for relative inputs.

Dependencies and integration points: Uses `pvfs2-internal.h` and `pvfs-path.h`. It exists separately from `pvfs-path.c` so code can qualify paths even when usrint is disabled at configure time.

Risks and test signals: On `getcwd` failure or path-too-long error, a newly allocated `PVFS_path_t` is leaked and `Ppath->rc` is not populated. The logic intentionally ignores symlinks, so later lookup/expand paths must recover. Test relative and absolute paths, root, trailing slash, repeated slash, `.` and `..`, cwd failure, long components, and repeated calls on the same expanded path.
