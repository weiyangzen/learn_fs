# sources/distributed-fs/openafs/src/WINNT/afsusrmgr/action.h

Purpose: declares the Account Manager action-window interface.

Important API/functions: `Actions_SetDefaultView` initializes a `VIEWINFO`; `Actions_OpenWindow`, `Actions_CloseWindow`, and `Actions_WindowToTop` manage the modeless progress window; `Actions_OnNotify` is the external notification hook for admin-server actions.

Control flow contract: startup/default initialization calls `Actions_SetDefaultView`; menus call open/close; the notification plumbing passes action start/finish data to `Actions_OnNotify`.

State and persistence: functions operate on static state in `action.cpp` and global `gr.viewAct`, `gr.rActions`, `gr.fShowActions`.

Dependencies/integration: depends on `LPVIEWINFO`, `WPARAM`, and `LPARAM` from the umbrella header.

Risks/test signals: callers must transfer ownership of `LPASACTION` notifications because `Actions_OnNotify` deletes them. Tests should verify ownership and menu state after close.
