<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/budb/globals.h -->
# sources/distributed-fs/openafs/src/budb/globals.h

## Purpose
Defines global budb server configuration and database-dump synchronization structures shared across server modules.

## Important APIs, Types, And Functions
Configuration includes `DEFAULT_DBPREFIX`, debug flags `DF_NOAUTH`, `DF_RECHECKNOAUTH`, `DF_SMALLHT`, and `DF_TRUNCATEDB`, and `buServerConfS` with database directory/name, host/server list, cell config path, Ubik database handle, and debug flags. Dump synchronization uses `dumpSyncS`, status flags `DS_WAITING`, `DS_DONE`, `DS_DONE_ERROR`, and timeout increment `DUMP_TTL_INC`.

## Control Flow
No executable flow is present, but `dumpSyncS` fields define the producer/consumer protocol between `dbs_dump.c` and `db_dump.c`: pipe fds, status flags, condition variables or LWP process handles, active Ubik transaction, buffered byte count, and TTL.

## State And Persistence
`globalConfPtr` is process-global configuration. `dumpSyncPtr` points to runtime state only. Persistent database location and Ubik membership are derived from configuration fields.

## Dependencies And Integration Points
Included by server initialization, RPC setup, database dump streaming, and authentication configuration code.

## Risks And Test Signals
Risks are global mutable state, noauth debug flags, and synchronization divergence between pthread and LWP builds. Signals are startup with configured server lists, noauth detection, dump streaming under both threading models, and timeout cleanup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/budb/globals.h -->
