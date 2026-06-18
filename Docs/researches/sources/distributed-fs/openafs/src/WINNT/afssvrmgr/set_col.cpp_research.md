# sources/distributed-fs/openafs/src/WINNT/afssvrmgr/set_col.cpp

## Purpose
`set_col.cpp` defines default fileset and replica views and formats column text for FastList callbacks.

## Important APIs, Types, And Functions
Public functions are `Filesets_SetDefaultView`, `Filesets_GetAlertCount`, `Filesets_GetColumnText`, `Replicas_SetDefaultView`, and `Replicas_GetColumnText`. Formatting covers fileset name, aggregate/server location, type, create/update/access/backup times, quota used/free/total/percent, status, numeric ID, file count, and replica server/aggregate/update date.

## Control Flow
Default-view functions copy resource IDs and widths from static column tables and set visible columns/sort. `Filesets_GetColumnText` rotates through static buffers, reads cached `FILESETSTATUS` from `FILESET_PREF`, formats the requested column, and uses alert descriptions before raw state flags for status. `Replicas_GetColumnText` similarly formats location and update date from cached fileset status.

## State And Persistence
The module uses static rotating text buffers sized by column count. It reads but does not write per-fileset preference cache state populated by display refreshes. `VIEWINFO` state is caller-owned and later persisted elsewhere.

## Dependencies And Integration Points
Dependencies include resource strings, alert helpers, `FormatTime`, `FormatString`, `LPIDENT` name accessors, fileset status flags/types, and global constants such as `ck1MB`. `display.cpp` calls these functions through `GetItemText`.

## Risks And Edge Cases
Static buffers are not thread-safe and returned pointers must be consumed immediately. `setcolQUOTA_FREE` subtracts used from quota without guarding underflow. Percent defaults to 100 when quota is zero. Type/status text depends on cached status; before a refresh columns may be blank or say no alerts.

## Test Signals
Test default column order/widths, all fileset types, quota formatting including zero and over-quota cases, alert versus state status precedence, date formatting failures, server-name inclusion, replica columns, and concurrent list rendering assumptions.
