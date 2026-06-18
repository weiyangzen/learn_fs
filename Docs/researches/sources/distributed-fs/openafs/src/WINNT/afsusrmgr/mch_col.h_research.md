## sources/distributed-fs/openafs/src/WINNT/afsusrmgr/mch_col.h

Purpose: declares machine-list column enum, metadata table, and column accessors.

Important APIs/types/functions: `MACHINECOLUMN` values are `mchcolNAME`, `mchcolCGROUPMAX`, `mchcolUID`, `mchcolOWNER`, and `mchcolCREATOR`. `MACHINECOLUMNS` maps each to localized column IDs and widths, with numeric columns right-justified. Declares `Machine_SetDefaultView` and `Machine_GetColumn`.

Control flow: startup uses metadata for default `VIEWINFO`; display/sort code uses `Machine_GetColumn`.

State and persistence behavior: static header metadata only; runtime view persistence is stored in `gr.viewMch`.

Dependencies and integration points: includes `display.h`; depends on `resource.h` IDs and the machine tab/display modules.

Risks: enum order must remain compatible with persisted column indexes. Header-level static table creates one copy per translation unit.

Test signals: resource/string coverage for every machine column and compatibility after adding/reordering columns.
