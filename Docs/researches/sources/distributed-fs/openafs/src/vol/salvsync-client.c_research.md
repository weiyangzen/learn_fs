# sources/distributed-fs/openafs/src/vol/salvsync-client.c

## Purpose
Implements the client-side SALVSYNC protocol helpers used by the fileserver, volserver utilities, and `salvageserver -client` to communicate with the demand-attach salvage server.

## Important APIs, Types, And Functions
Public functions are `SALVSYNC_clientInit`, `SALVSYNC_clientFinis`, `SALVSYNC_clientReconnect`, `SALVSYNC_askSalv`, `SALVSYNC_SalvageVolume`, and `SALVSYNC_LinkVolume`. The static `salvsync_client_state` defines the endpoint, protocol version, retry limit, timeout, and protocol name. Requests use `SYNC_command`, `SYNC_response`, `SALVSYNC_command_hdr`, and `SALVSYNC_response_hdr`.

## Control Flow
Clients connect with `SYNC_connect`, build a `SALVSYNC_command_hdr`, set command/reason/length metadata, and call `SALVSYNC_askSalv`. `SALVSYNC_askSalv` stamps the current protocol version, serializes access with `VSALVSYNC_LOCK`, invokes `SYNC_ask`, logs unusual responses, and returns the protocol status. `SALVSYNC_SalvageVolume` schedules, queries, cancels, or reprioritizes a volume by using the same helper with different command/reason values. `SALVSYNC_LinkVolume` sends the clone/parent relationship command.

## State And Persistence
Runtime state is the connected SALVSYNC socket/channel in `salvsync_client_state`, protected by the volume salvsync mutex. No state persists locally; all scheduling state lives in the salvageserver process.

## Dependencies And Integration Points
The file is compiled only for `AFS_DEMAND_ATTACH_FS`. It depends on generic daemon sync transport, volume locks, partition/volume headers for types, and OpenAFS logging. It is used by salvage clients and volume code that needs to request online salvage or link clone scheduling to a parent.

## Risks And Test Signals
Risks include protocol version mismatch, stale or disconnected channel state, part-name truncation to the wire field size, and in-memory-only server state after reconnect. Tests should cover connect/reconnect/close, malformed or denied responses, schedule/query/cancel flows, link-volume requests, and concurrent callers contending on `VSALVSYNC_LOCK`.
