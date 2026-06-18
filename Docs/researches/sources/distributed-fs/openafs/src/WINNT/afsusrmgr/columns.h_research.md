## sources/distributed-fs/openafs/src/WINNT/afsusrmgr/columns.h

Purpose: declares the column-selection dialog entry point used by the main command layer when the user chooses the Columns command. It is intentionally tiny and only exposes `ShowColumnsDialog(HWND hParent, LPVIEWINFO lpvi = NULL)`.

Important APIs/types/functions: the function accepts an optional `LPVIEWINFO`; passing `NULL` lets the implementation infer the active view, while passing a view structure lets callers edit a specific FastList layout. It depends on `HWND` and `LPVIEWINFO` coming from the broader `TaAfsUsrMgr.h` include graph.

Control flow: this header has no logic. Runtime flow is initiated from `command.cpp` via `OnContextCommand(M_COLUMNS)`, which calls `ShowColumnsDialog(g.hMain)`.

State and persistence behavior: column state is represented by `VIEWINFO` arrays for available/shown columns, sort order, and widths. Persistence happens elsewhere through `gr.viewUsr`, `gr.viewGrp`, `gr.viewMch`, `RestoreSettings`, and `StoreSettings`.

Dependencies and integration points: integrates with FastList view-management code (`FL_StoreView`, `FL_RestoreView`) and with `resource.h` column dialog control IDs. The dialog affects display behavior in `display.cpp`.

Risks: because the default argument hides whether the active view or an explicit view is edited, regressions can misapply column changes to the wrong tab. The header also requires C++ compilation because of its default parameter.

Test signals: exercise Columns from each tab, change column order/width/visibility, switch tabs, restart the app, and verify persisted `VIEWINFO` settings remain tab-specific.
