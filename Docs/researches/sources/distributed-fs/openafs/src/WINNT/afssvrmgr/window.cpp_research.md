# sources/distributed-fs/openafs/src/WINNT/afssvrmgr/window.cpp

Purpose: implements the main AFS Server Manager window, including server list, optional preview pane, action-window toggling, notification handling, refresh animation, keyboard traversal, and context-menu routing.

Important APIs/functions: `Main_DialogProc` is the main dialog procedure. `Main_OnNotifyFromDispatch` translates AfsClass notifications into display/task actions. `Main_OnOpenServers_ThreadProc` reopens persisted server windows. `Main_Redraw_ThreadProc` refreshes cell/server data. `Main_OnPreviewPane`, `Main_OnServerView`, `Main_SetServerViewMenus`, `Main_CreateTabControl`, `Main_DeleteTabControl`, `Main_DisplayTab`, and `Main_RearrangeChildren` manage the UI layout. `Main_StartWorking`, `Main_StopWorking`, and `Main_AnimateIcon` manage the busy indicator.

Control flow: on init the main dialog stores `g.hMain`, restores geometry, subclasses the server list, creates preview UI if enabled, subscribes for cell notifications, starts a redraw thread, and starts a dispatch timer. Commands update preview layout, server view, columns, actions, credentials, or delegate to `StartContextCommand`. Server-list selection updates the preview pseudo-window; double-click either opens properties or a standalone server window based on preferences.

State and persistence: uses and mutates `gr.rMain`, `gr.rMainPreview`, `gr.diHorz/diVert`, `gr.fPreview`, `gr.fVert`, `gr.fActions`, `gr.tabLast`, icon views, and credentials in `g.hCreds`. Preferences are ultimately stored by `Quit`.

Dependencies/integration: integrates display, command, notification dispatch, server window, property dialogs, credentials, column customization, action window, and AfsClass refresh.

Risks: background threads call UI helpers and AfsClass with shared globals; thread/UI boundaries depend on legacy assumptions. `LOWORD/HIWORD` on screen coordinates can mishandle negative multi-monitor coordinates. `procServers` is global subclass state. Tests should cover preview layout toggles, persisted view restoration, notification-driven redraw, expired credentials checks, double-click behavior, column dialog routing, and active-action quit behavior.
