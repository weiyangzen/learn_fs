## sources/distributed-fs/openafs/src/WINNT/afsusrmgr/grp_col.h

Purpose: declares group-list columns and their metadata.

Important APIs/types/functions: defines `GROUPCOLUMN` values `grpcolNAME`, `grpcolCMEMBERS`, `grpcolUID`, `grpcolOWNER`, and `grpcolCREATOR`. Static `GROUPCOLUMNS` maps columns to string resource IDs and default widths, with numeric columns right-justified. Declares `Group_SetDefaultView` and `Group_GetColumn`.

Control flow: `Group_SetDefaultView` consumes `GROUPCOLUMNS` to seed a `VIEWINFO`; FastList lazy text and sorting call `Group_GetColumn`.

State and persistence behavior: no direct state, but static metadata in a header means each including translation unit gets a copy.

Dependencies and integration points: includes `display.h` for `ICONVIEW`/`VIEWINFO` and relies on resource IDs in `resource.h`.

Risks: header-level non-const static table can diverge per translation unit if modified at runtime, although current code treats it as read-only. Column enum order must stay aligned with the table and persisted `VIEWINFO` column indexes.

Test signals: verify all `GROUPCOLUMN` enum values have table entries and resource strings; test compatibility of persisted column indexes after changes.
