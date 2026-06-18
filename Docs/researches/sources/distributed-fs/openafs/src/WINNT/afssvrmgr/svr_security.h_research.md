# sources/distributed-fs/openafs/src/WINNT/afssvrmgr/svr_security.h

Purpose: declares server-security data structures and entry points for the AFS Server Manager security UI.

Important API/types: `SERVERKEYCOLUMN` defines version, data, and checksum columns. `SERVERKEYCOLUMNS` provides resource IDs and default widths, including right justification for checksum. `KEY_CREATE_PARAMS` carries the target server, version, optional string, and raw `ENCRYPTIONKEY`; `KEY_DELETE_PARAMS` carries target server and version. Public functions are `Server_Key_SetDefaultView` and `Server_Security`.

Control flow contract: `Server_Security` owns UI creation and passes key structs to `taskSVR_KEY_CREATE` or `taskSVR_KEY_DELETE`. `Server_Key_SetDefaultView` is called during global preference default initialization in `svrmgr.cpp`.

State and persistence: this header defines only transient task structs and column defaults. Persistent state is stored in `GLOBALS_RESTORED.viewKey`.

Dependencies/integration: depends on `LPIDENT`, `ENCRYPTIONKEY`, `VIEWINFO`, `cchRESOURCE`, and resource IDs. Included by startup, security implementation, and task code.

Risks/test signals: `SERVERKEYCOLUMNS` is a non-`extern` static definition in a header, which intentionally creates a private copy per translation unit; adding mutable fields would be risky. Tests should verify view defaults stay in sync with resource columns and task packet fields are initialized before dispatch.
