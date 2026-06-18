# File Research: sources/block-storage/lvm2/lib/misc/sharedlib.c

This file resolves configured shared library/plugin paths.

API:
- `get_shared_library_path(struct cmd_context *cmd, const char *libname, char *path, size_t path_len)`.

Behavior:
- Empty or NULL `libname` yields empty path.
- Absolute `libname` is used as-is.
- Relative `libname` is first tried under `cmd->lib_dir`, initialized from `global_library_dir`.
- If the constructed path cannot be statted, falls back to copying `libname`.

Dependencies:
- Config lookup, command context, `stat()`.

Role:
- Used for monitor/plugin DSO path resolution.

Risk:
- A missing file under `global_library_dir` silently falls back to the original string, leaving final resolution to later loader code.
