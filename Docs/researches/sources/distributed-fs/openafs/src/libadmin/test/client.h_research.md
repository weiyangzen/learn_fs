<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/libadmin/test/client.h -->
# sources/distributed-fs/openafs/src/libadmin/test/client.h

## Purpose
Declares the client command registration function for the `afscp` test driver and includes the API surface needed by client command implementations.

## Important APIs, Types, And Functions
The header declares `SetupClientAdminCmd(void)` and includes OpenAFS standards, pthread, RX/rxstat, admin, client admin, util admin, cellconfig, cmd, and `common.h`.

## Control Flow
`afscp.c` calls `SetupClientAdminCmd` after installing common before/after hooks. `client.c` then registers all client and RX stats command syntaxes.

## State And Persistence
The header has no state. Through included declarations, client commands can use global `cellHandle`/`tokenHandle` from `common.h` and may mutate remote stats state or AFS namespace state.

## Dependencies And Integration Points
It is the module boundary between the generic `afscp` driver and the client command implementation.

## Risks And Test Signals
Risks are limited to declaration drift and over-broad includes. The relevant signal is a clean `afscp` build and visible client commands in the command parser.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/libadmin/test/client.h -->
