# sources/distributed-fs/openafs/src/WINNT/afsusrmgr/columns.cpp

Purpose: implements the Account Manager "Columns" dialog for choosing visible columns and column order for users, groups, and machines lists.

Important APIs/functions: `ShowColumnsDialog` clones current `gr.viewUsr`, `gr.viewGrp`, and `gr.viewMch` into static working entries and opens a modal property sheet. `Columns_DlgProc` routes selection and apply commands. `Columns_OnSelect` rebuilds available/shown lists from the selected `VIEWINFO`. `Columns_OnInsert`, `Columns_OnDelete`, `Columns_OnMoveUp`, and `Columns_OnMoveDown` mutate the working `VIEWINFO`. `Columns_OnApply` commits changed views to the active display via `Display_RefreshView` or copies them into `gr`.

Control flow: when no default view is supplied, active tab selection decides the initial category. The first shown column is protected from deletion and movement above index 0, preserving the primary name column. Apply only commits categories marked `fChanged`.

State and persistence: static `COLUMNS` holds modal working copies and change flags. Persistent state lives in `gr.viewUsr`, `gr.viewGrp`, and `gr.viewMch`; active tab commits are pushed through display refresh. Final registry storage happens through broader app settings persistence.

Dependencies/integration: uses `TaAfsUsrMgr.h`, `columns.h`, `display.h`, property sheets, combo/list helpers, and `VIEWINFO`.

Risks: `Columns_OnInsert` computes `iShown` but does not use it, so inserted columns are appended rather than inserted after the current selection. `Columns_OnMoveDown` writes `aColumns[ii+1]` without independently checking `ii < nColsShown - 1`; the button-state guard usually prevents this, but direct calls would overrun. Tests should cover add/delete/reorder edge cases, protected first column behavior, active versus inactive tab apply, and persistence after restart.
