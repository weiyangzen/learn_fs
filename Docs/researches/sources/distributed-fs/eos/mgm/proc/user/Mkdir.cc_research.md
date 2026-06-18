# sources/distributed-fs/eos/mgm/proc/user/Mkdir.cc

Purpose: implements legacy directory creation as `ProcCommand::Mkdir()`.

Important APIs and types: reads `mgm.path` and `mgm.option`, applies `NAMESPACEMAP`, illegal-name and permission bounce macros, `PROC_TOKEN_SCOPE`, and calls `gOFS->_mkdir` with `SFS_O_MKPTH` for option `p`.

Control flow: map and validate the input path, reject an empty path, translate `-p` into the recursive create flag, call the OFS mkdir helper, and return `errno` plus a generic error string on failure.

State and persistence: mutates namespace metadata by creating a directory or a path of directories. It also participates in the usual access/token policy.

Dependencies and integration: simple wrapper around the MGM OFS namespace creation operation.

Risks: error text is generic and relies on `errno` for detail. Tests should cover empty path, illegal names, token-scoped create, `-p` parent creation, existing directory behavior, permission denial, and namespace mapping.
