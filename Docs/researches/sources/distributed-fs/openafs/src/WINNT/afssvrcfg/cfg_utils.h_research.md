<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afssvrcfg/cfg_utils.h -->
# sources/distributed-fs/openafs/src/WINNT/afssvrcfg/cfg_utils.h

Purpose: Declares the shared configuration-state and UI/error helper functions implemented by `cfg_utils.cpp`.

Important APIs/functions: Exposes state predicates/mutators, `RedrawGraphic`, `GetAppTitleID`, admin-error translation, logging, and standard error/warning dialogs.

Control flow: No runtime logic; the header is included after `CONFIG_STATE` is defined in `afscfg.h`, making include order part of the contract.

State and persistence: No local state. Functions declared here operate on passed state references and process globals.

Dependencies and integration points: Depends on `CONFIG_STATE`, `afs_status_t`, Win32 `HWND`, and resource-driven UI conventions in the server configuration app.

Risks: Header guard name `_WIZ_UTILS_H_` does not match the filename and could collide with older wizard utility code. Callers can still bypass helpers and compare raw flags inconsistently.

Test signals: Compile all wizard/config pages through `afscfg.h`; verify no direct include before `CONFIG_STATE` exists.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afssvrcfg/cfg_utils.h -->
