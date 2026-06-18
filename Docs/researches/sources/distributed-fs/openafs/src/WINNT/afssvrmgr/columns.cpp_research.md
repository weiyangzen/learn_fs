<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afssvrmgr/columns.cpp -->
# sources/distributed-fs/openafs/src/WINNT/afssvrmgr/columns.cpp

## Purpose
Implements the column customization dialog for server-manager FastList views.

## Important APIs, Types, And Functions
`ShowColumnsDialog`, `Columns_DlgProc`, and handlers for init, selection, insert, delete, move up/down, and apply. Static `COLUMNS` stores working `VIEWINFO` copies for server, fileset, aggregate, service, replica, and aggregate-picker lists.

## Control Flow
Opening copies global views into working state and selects a default category. The UI computes available/shown lists from `VIEWINFO`. Mutations update `aColumns/nColsShown`, mark changed, and dirty the property sheet. Apply copies changed views back to globals, restores visible FastLists, redraws server windows, and may post `WM_COLUMNS_CHANGED`.

## State And Persistence
Working state is static during the dialog. Global view preferences in `gr` are updated on apply.

## Dependencies And Integration Points
Uses property sheets/cache, combo/list helpers, FastList view APIs, server-window iteration, display refresh, and global layout state.

## Risks And Edge Cases
First column is pinned. `Columns_OnInsert` computes an insertion index but appends the new column. Static working state assumes one dialog. Applying visible windows depends on `PropCache_Search` iteration.

## Test Signals
Each category, hidden categories, insert/delete/reorder, apply/cancel, visible redraw, and persisted view settings.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afssvrmgr/columns.cpp -->
