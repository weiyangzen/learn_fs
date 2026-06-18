# sources/distributed-fs/openafs/src/WINNT/afssvrmgr/svc_tab.h

Purpose: Declares the Services tab dialog procedure and service popup-menu helper.

Important APIs/types: `Services_DlgProc` plugs into tab UI; `Services_ShowParticularPopupMenu` starts async menu generation for selected/empty service context.

Control flow/state: The popup helper passes a `MENUTASK` to `taskSVC_MENU`.

Dependencies/integration: Used by services tab and other list contexts needing service menus.

Risks/test signals: Ensure returned `WM_ENDTASK` goes to a window that handles `taskSVC_MENU`.
