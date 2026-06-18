# sources/distributed-fs/openafs/src/WINNT/afssvrmgr/messages.h

## Purpose
`messages.h` centralizes custom window messages and timer IDs used by the Server Manager UI and worker dispatch paths.

## Important APIs, Types, And Functions
The file defines timer IDs `ID_DISPATCH_TIMER` and `ID_ACTION_TIMER`, plus `WM_USER`-based messages including `WM_NOTIFY_FROM_DISPATCH`, `WM_SERVER_CHANGED`, `WM_REFRESH_UPDATE`, `WM_OPEN_SERVERS`, `WM_COLUMNS_CHANGED`, `WM_OPEN_SERVER`, `WM_SHOW_CREATEREP_DIALOG`, `WM_SHOW_YOURSELF`, `WM_OPEN_ACTIONS`, and `WM_REFRESH_SETSECTION`. Comments document expected `wParam`/`lParam` payloads.

## Control Flow
No executable flow exists. Dialog procedures and main-window handlers switch on these values to receive AFSClass notifications, redraw server tabs, update refresh progress, reopen servers, react to column changes, and request cross-thread dialog creation.

## State And Persistence
No state is declared. The message values form an in-process ABI between UI components and worker/task code.

## Dependencies And Integration Points
The header depends on Win32 `WM_USER` conventions and is included by modules that post or handle these messages. It integrates the dispatch notification layer, refresh dialog, server windows, fileset drag/drop replica workflow, and action window.

## Risks And Test Signals
Risks include message ID collisions, wrong payload casting, and posting messages to windows after destruction. Test signals are compile coverage and functional tests for each message source/handler pair, especially cross-thread `WM_SHOW_CREATEREP_DIALOG` and notification cleanup.
