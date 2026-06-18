# sources/distributed-fs/openafs/src/vol/salvsync.h

## Purpose
Defines the SALVSYNC protocol, wire payloads, scheduler node type, endpoint, and public client/server APIs for demand-attach online salvage coordination.

## Important APIs, Types, And Functions
The header declares protocol versions `SALVSYNC_PROTO_VERSION_V1` through `V3`, command codes (`SALVSYNC_OP_NOP`, `SALVSYNC_OP_SALVAGE`, `SALVSYNC_OP_CANCEL`, `SALVSYNC_OP_RAISEPRIO`, `SALVSYNC_OP_QUERY`, `SALVSYNC_OP_CANCELALL`, `SALVSYNC_OP_LINK`), reason codes, `SALVSYNC_FLAG_VOL_STATS_VALID`, command states, `SALVSYNC_command_hdr`, `SALVSYNC_response_hdr`, wrapper structs, `SALVSYNC_command_info`, `SalvageQueueNodeType_t`, and `struct SalvageQueueNode`. It declares client functions and server functions `SALVSYNC_salvInit`, `SALVSYNC_getWork`, and `SALVSYNC_doneWorkByPid`.

## Control Flow
Clients fill `SALVSYNC_command_hdr` and send it inside generic `SYNC_command` frames. The server validates the version and payload size, changes scheduler state, and returns `SALVSYNC_response_hdr` containing state, priority, and queue lengths. Salvage worker code consumes `SalvageQueueNode` objects and reports completion by pid.

## State And Persistence
The header defines in-memory command and scheduler state, not durable state. The wire-visible partition name is a 16-byte fixed field, so partition naming and truncation behavior are part of the protocol contract. `SALVSYNC_IN_PORT` and `SALVSYNC_UN_PATH` define the persistent endpoint identity used by clients and server.

## Dependencies And Integration Points
It is only active under `AFS_DEMAND_ATTACH_FS` and depends on `daemon_com.h` and `voldefs.h`. It is shared by `salvsync-client.c`, `salvsync-server.c`, `salvaged.c`, fileserver/volserver code that schedules salvages, and any caller that needs volume-group link scheduling.

## Risks And Test Signals
Risks include protocol version drift across binaries, fixed-size `partName`, enum compatibility, and scheduler-node layout assumptions shared only in-process. Tests should build mixed client/server modules together and exercise every command code, malformed strings, queue state responses, clone links, and version mismatch handling.
