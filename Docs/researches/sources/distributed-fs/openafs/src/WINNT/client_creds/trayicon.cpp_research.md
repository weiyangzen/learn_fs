# sources/distributed-fs/openafs/src/WINNT/client_creds/trayicon.cpp

Purpose: manages the notification-area icon representing AFS credential status.

Important APIs/functions: `ChangeTrayIcon(int nim)` wraps `Shell_NotifyIcon` operations for add, modify, and delete. It chooses `IDI_CREDS_YES` or `IDI_CREDS_NO` based on whether credentials exist and whether any are near expiration.

Control flow: first `NIM_MODIFY` becomes `NIM_ADD`; modify after delete is ignored. For add/modify/delete while the main window is valid, it fills `NOTIFYICONDATA`, calls `Main_FindExpiredCreds`, locks `g.credsLock` while checking `g.cCreds`, sets tooltip text, and calls `Shell_NotifyIcon`.

State/persistence: file-static flags track whether the icon was added or deleted. Reads global credential state; no persistent writes.

Dependencies/integration: depends on `window.cpp` for `WM_TRAYICON` and expiration detection, `TaLocale` for icons/tooltip, and Shell API.

Risks: `Main_FindExpiredCreds` may trigger token-renewal logic from an icon update, making this more than a pure paint/status function. Static icon handles are never destroyed. Delete behavior depends on `g.hMain` validity.

Test signals: initial add, repeated modify, delete on quit, tooltip localization, icon state for valid/expired/no tokens, and Explorer taskbar restart scenarios.
