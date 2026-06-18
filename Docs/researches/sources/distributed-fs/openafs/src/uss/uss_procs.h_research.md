
# sources/distributed-fs/openafs/src/uss/uss_procs.h

Purpose: `uss_procs.h` declares the template action interface used by the generated `uss` grammar and by bulk `exec` handling.

Important APIs and definitions: `uss_procs_YOUNG` and `uss_procs_ANCIENT` classify preexisting mountpoints. Function declarations cover directory creation, file copying, file echoing, shell execution, link creation, directory-pool management, template lookup, error reporting, owner lookup, and `$AUTO` directory selection.

Control flow and integration: grammar actions call these functions as they parse template statements. `uss_vol.c` uses the mountpoint age constants and owner lookup. `uss.c` calls `uss_procs_FindAndOpen()` for the template and `uss_procs_Exec()` for bulk `exec`.

State and persistence: the API is stateless on paper, but the implementation is controlled by global dry-run, overwrite, parser line, syntax error, account creator, directory-pool, and cleanup-stack state.

Risks and test signals: callers pass all values as strings, so mode, owner, path, and command validation lives in the implementation. Tests should cover grammar-to-function argument mapping, especially path ordering for `SetLink()` and directory ACL arguments.
