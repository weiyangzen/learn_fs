# sources/distributed-fs/openafs/src/WINNT/afssvrmgr/svr_install.cpp

Purpose: Implements singleton dialog for installing/copying a local binary/file to a target directory on a selected server.

Important APIs/functions: `Server_Install` opens/focuses the dialog. `Server_Install_DlgProc` handles lifecycle. `Server_Install_OnInitDialog` enumerates servers and sets description. `Server_Install_EnableOK` validates selected server, source filename, and target directory. `Server_Install_OnBrowse` uses `GetOpenFileName`. `Server_Install_OnOK` dispatches `taskSVR_INSTALL`.

Control flow: Dialog is cached under `pcSVR_INSTALL`. Server combo is disabled until async enumeration completes. Browse preserves/restores current directory around file dialog. OK dispatches install task then destroys the dialog through fallthrough to cancel handling.

State and persistence: `SVR_INSTALL_PARAMS` stores target server, source path, and target directory. No local persistence.

Dependencies/integration: Uses prop cache, server enumeration, common file dialog APIs, resource filters, and task dispatch.

Risks: Target directory is free text with only nonempty validation. Source/target buffers use `MAX_PATH`; long paths are unsupported. OK closes immediately, so task failures must surface elsewhere.

Test signals: Empty-field validation, server enum failure, browse cancel/success, current-directory preservation, duplicate dialog focus, and task packet field contents.
