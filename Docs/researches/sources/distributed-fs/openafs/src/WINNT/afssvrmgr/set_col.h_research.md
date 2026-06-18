# sources/distributed-fs/openafs/src/WINNT/afssvrmgr/set_col.h

## Purpose
`set_col.h` declares fileset and replica column metadata and formatter APIs.

## Important APIs, Types, And Functions
`FILESETCOLUMN` enumerates fileset columns, and `FILESETCOLUMNS` maps each to a resource string and width. `REPLICACOLUMN` and `REPLICACOLUMNS` do the same for replica views. Macros `nFILESETCOLUMNS` and `nREPLICACOLUMNS` expose counts. Functions declare default-view setup and text retrieval for filesets and replicas.

## Control Flow
No executable logic exists. Display code uses these enums as indexes in `VIEWINFO::aColumns` and callback dispatch.

## State And Persistence
The static column tables live in each translation unit that includes the header. View selections are stored in `VIEWINFO` instances elsewhere.

## Dependencies And Integration Points
The header depends on resource IDs, `LPVIEWINFO`, `LPFILESET`, `LPIDENT`, and column justification flags. It integrates display callbacks with fileset and replica tabs/dialogs.

## Risks And Test Signals
Because the static tables are in a header, every including source gets its own copy. Enum order must match table order and resource strings. Test default views and column chooser behavior after adding or reordering columns.
