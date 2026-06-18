
# sources/distributed-fs/openafs/src/uss/uss_procs.c

Purpose: `uss_procs.c` implements template actions for building a user filesystem: create directories, copy prototype files, echo content, run shell commands, create links, choose `$AUTO` directories, resolve owners, locate templates, and report parser errors.

Important APIs and functions: exported `uss_procs_BuildDir()`, `uss_procs_CpFile()`, `uss_procs_EchoToFile()`, `uss_procs_Exec()`, `uss_procs_SetLink()`, `uss_procs_GetOwner()`, `uss_procs_PickADir()`, `uss_procs_AddToDirPool()`, `uss_procs_FindAndOpen()`, and `uss_procs_PrintErr()`. Static `Copy()` and `Echo()` perform low-level file writes.

Control flow: all mutating template actions bail when `uss_syntax_err` is already set. Overwrite checks skip existing targets unless `uss_OverwriteThisOne` is true. Directory creation sets Unix mode/owner, grants temporary full ACL to `uss_AccountCreator`, and pushes final ACL onto `uss_currentDir`. File copy and echo create or overwrite files, set mode, and chown. `$AUTO` selection counts non-dot entries under configured candidate directories and picks the least populated.

State and persistence: uses global `temp[1000]`, parser `line`, common flags, directory pool, and cleanup stack. Persistent effects are filesystem directories/files/links, owners, modes, ACLs, and arbitrary shell-command side effects.

Dependencies and integration: called by generated grammar actions after `uss.c` opens a template. Depends on POSIX filesystem APIs, passwd APIs, `uss_acl_SetAccess()`, and common globals.

Risks: `uss_procs_Exec()` passes template content to `system()`. `Copy()` opens overwrite targets without `O_TRUNC`, so shorter copied files can retain stale trailing bytes. Several `strcpy()`/`strcat()` calls operate on fixed buffers or mutate caller-owned `a_proto`. `$AUTO` path logic is fragile and has a pointer comparison typo-like loop condition. Test signals should cover dry-run, overwrite/no-overwrite, copy truncation, owner lookup failures, template search paths, `$AUTO` selection, and ACL cleanup stack order.
