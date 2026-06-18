<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afssvrmgr/agg_col.h -->
# sources/distributed-fs/openafs/src/WINNT/afssvrmgr/agg_col.h

## Purpose
Declares aggregate column IDs, metadata, and display helpers.

## Important APIs, Types, And Functions
`AGGREGATECOLUMN`, `AGGREGATECOLUMNS`, `nAGGREGATECOLUMNS`, and prototypes for default view, alert count, and column text.

## Control Flow
No runtime flow.

## State And Persistence
Defines a static metadata array per including translation unit.

## Dependencies And Integration Points
Requires resource IDs and server-manager view/identity types.

## Risks And Edge Cases
Enum, metadata array, and formatter switch must remain synchronized.

## Test Signals
Compilation plus UI checks for aggregate column labels, widths, and values.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afssvrmgr/agg_col.h -->
