# sources/distributed-fs/openafs/src/WINNT/afssvrmgr/svr_install.h

Purpose: Declares server install task packet and UI entry point.

Important APIs/types: `SVR_INSTALL_PARAMS` carries server identity, local source path, and remote target directory. `Server_Install(LPIDENT)` opens the install dialog.

Control flow/state: The dialog fills this packet for `taskSVR_INSTALL`.

Dependencies/integration: Used by server maintenance commands.

Risks/test signals: Validate target path semantics in the task layer; UI only checks nonempty fields.
