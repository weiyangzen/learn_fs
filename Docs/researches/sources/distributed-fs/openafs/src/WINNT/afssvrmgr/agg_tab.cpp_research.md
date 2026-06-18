<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afssvrmgr/agg_tab.cpp -->
# sources/distributed-fs/openafs/src/WINNT/afssvrmgr/agg_tab.cpp

## Purpose
Implements the Aggregates tab in server/cell windows.

## Important APIs, Types, And Functions
`Aggregates_DlgProc`, `Aggregates_OnNotifyFromDispatch`, list subclassing, and popup-menu helpers.

## Control Flow
Init resizes to the tab area, restores FastList view, installs text callbacks, and subclasses the list. Server changes register dispatch notifications, update description text, and refresh aggregates. Double-click opens properties; context menu handles headers, selected rows, server rows, and empty space.

## State And Persistence
`gr.viewAgg` stores view layout. Dispatch registrations track target windows. Static `procAggregatesList` stores the original list proc.

## Dependencies And Integration Points
Uses resize/FastList/display helpers, dispatch, server-window helpers, menus, and `StartContextCommand`.

## Risks And Edge Cases
Static subclass proc state can be problematic with multiple lists. Destroy cleanup is required to avoid dead HWND notifications. Right-clicking an unselected item does not command that item.

## Test Signals
Initialization/resizing, notification refresh, description variants, double-click properties, context menus, and destroy/recreate cycles.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afssvrmgr/agg_tab.cpp -->
