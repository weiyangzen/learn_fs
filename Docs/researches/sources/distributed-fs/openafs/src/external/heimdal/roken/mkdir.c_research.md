# sources/distributed-fs/openafs/src/external/heimdal/roken/mkdir.c

Purpose: portable wrapper for directory creation with Unix-style signature.

Important APIs/types/functions: `rk_mkdir(const char *pathname, mode_t mode)`.

Control flow: on non-Windows, calls `mkdir(pathname, mode)`. On Windows, ignores `mode` and calls `_mkdir(pathname)`.

State and persistence behavior: creates a filesystem directory or returns an error from the platform call.

Dependencies and integration points: roken portability wrapper, with `mkdir` macro undefined before defining the wrapper to avoid replacement loops.

Risks: Windows cannot honor Unix permission mode, so callers needing specific ACLs must handle that elsewhere. Behavior and errno values otherwise follow the platform call.

Test signals: directory creation success, existing directory errors, permission-denied paths, and Windows mode-ignored behavior.
