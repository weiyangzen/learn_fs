<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afssvrmgr/agg_col.cpp -->
# sources/distributed-fs/openafs/src/WINNT/afssvrmgr/agg_col.cpp

## Purpose
Defines aggregate-list default view and formats aggregate column text.

## Important APIs, Types, And Functions
`Aggregates_SetDefaultView`, `Aggregates_GetAlertCount`, and `Aggregates_GetColumnText` cover default columns, alert count, and display text for name, ID, device, storage, percent used, and status.

## Control Flow
Formatter retrieves `AGGREGATE_PREF` from the identifier user param, switches by `AGGREGATECOLUMN`, formats storage/percent fields, and uses `Alert_GetQuickDescription` for status.

## State And Persistence
Uses a ring of static text buffers. Reads attached aggregate preference/status snapshots but writes nothing.

## Dependencies And Integration Points
Depends on `LPIDENT`, aggregate prefs/status, `Alert_*`, `FormatString`, and FastList display callbacks.

## Risks And Edge Cases
Static buffers are overwritten and not thread-safe. Missing user params leave blank fields. Percent is clamped to 0-100.

## Test Signals
Column text for all columns, missing prefs, zero total, server-qualified names, and alert/no-alert status.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afssvrmgr/agg_col.cpp -->
