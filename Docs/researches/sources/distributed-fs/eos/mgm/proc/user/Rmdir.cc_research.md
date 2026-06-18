# sources/distributed-fs/eos/mgm/proc/user/Rmdir.cc

Purpose: implements legacy empty-directory removal as `ProcCommand::Rmdir()`.

Important APIs and types: reads `mgm.path`, applies `NAMESPACEMAP`, `NAMESPACE_NO_TRAILING_SLASH`, illegal-name and permission bounces, token scope, and calls `gOFS->_remdir`.

Control flow: path is mapped and normalized without trailing slash, empty paths are rejected, and `_remdir` is invoked. Failures return a quoted path and `errno`.

State and persistence: mutates namespace metadata by removing a directory when lower-layer checks allow it.

Dependencies and integration: simple proc wrapper over MGM OFS directory removal.

Risks: behavior for non-empty directories and recycle policies is delegated entirely to `_remdir`; callers needing recursive or recycle-aware behavior should use rm. Tests should cover trailing slash normalization, empty path, token scope, illegal names, non-empty directory failure, missing path, and permission denial.
