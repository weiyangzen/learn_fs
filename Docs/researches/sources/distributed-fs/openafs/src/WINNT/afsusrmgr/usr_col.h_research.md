# sources/distributed-fs/openafs/src/WINNT/afsusrmgr/usr_col.h

Purpose: defines the user-list column model for the AFS User Manager.

Important APIs/types: `USERCOLUMN` enumerates name, flags, KAS booleans, dates, lifetimes, lockout counts, quota, UID, owner, and creator columns. The static `USERCOLUMNS` table maps each enum entry to resource-string IDs and default widths/justification flags. Exports are `User_SetDefaultView`, `User_GetColumn`, `User_GetDisplayName`, and `User_SplitDisplayName`.

State and dependencies: includes `display.h` for `VIEWINFO`, `ICONVIEW`, `COLUMNTYPE`, and column flags. The header itself has no persistence, but the static table in a header means every including translation unit gets a private copy.

Risks and test signals: enum/table order must stay synchronized because comments and `User_GetColumn` switch logic depend on it. Tests should catch mismatched column captions, widths, sorting types, and display-name split behavior.
