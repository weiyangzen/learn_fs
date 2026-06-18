# sources/distributed-fs/moosefs/mfschunkserver/csserv.c

## Purpose
`csserv.c` implements the chunkserver client/administrative TCP service. It accepts client connections on `CSSERV_LISTEN_HOST`/`CSSERV_LISTEN_PORT`, parses MooseFS packet headers and bodies, dispatches read/write work to background jobs, answers administrative and monitoring requests, and exposes byte counters for charting.

## Important Types and APIs
`csserventry` is the per-connection state: connection state (`IDLE`, `READ`, `WRITE`, `CLOSE`), parse mode (`HEADER`, `DATA`), socket, poll descriptor position, last read/write timestamps, header buffer, current input packet, output packet queue, active read/write job id, and a list of idle metadata jobs. `packetstruct` represents queued output buffers. `idlejob` tracks asynchronous chunk-info requests with a flexible `buff[1]` payload.

Public APIs are `csserv_stats`, `csserv_getlistenip`, `csserv_getlistenport`, and `csserv_init`. Internal handlers include version/config replies, read/write initialization, chunk blocks/checksum/checksum-tab/info, HDD listing, chart PNG/data, monotonic data, module info, error clearing, connection close cleanup, packet dispatch, reload, read/write I/O, poll descriptor registration, and serving.

## Control Flow
`csserv_init` reads listen config, creates a nonblocking TCP socket, enables nodelay/reuseaddr, resolves and listens, optionally sets an accept filter, then registers exit, reload, destruct, and poll callbacks with the main loop. `csserv_desc` adds the listening socket and idle client sockets to the poll set. `csserv_serve` accepts new sockets, handles poll errors, reads packets, sends keepalive `ANTOAN_NOP` packets after idle write intervals, writes queued output, closes timed-out idle connections after `CSSERV_TIMEOUT`, and frees closed entries.

`csserv_read` is a two-phase parser: read 8-byte header, validate body length against `CSTOCS_MAXPACKETSIZE`, allocate body, read body, then dispatch through `csserv_gotpacket`. Dispatch only accepts most commands while the connection is `IDLE`; data operations set state to `READ` or `WRITE` and call `job_serv_read`/`job_serv_write`. If those jobs cannot queue, the service sends immediate `MFS_ERROR_NOTDONE` status when packet size validates. Completion callback `csserv_iothread_finished` returns the connection to `IDLE` or closes it, clears `jobid`, and frees the input packet.

Idle metadata operations allocate `idlejob` records, call `job_get_chunk_*`, and build protocol replies in `csserv_idlejob_finished`. Connection close disables outstanding jobs and removes callbacks to avoid callbacks touching freed connection state.

## State and Persistence
Service state is in-memory: connection list, output queues, active jobs, listen socket, listen address, and byte counters. No durable client-service state is stored here. It reads configuration through `cfg`, and reload can replace the listening socket and force master reconnect so the master learns the new address.

## Dependencies and Integration
The module depends on `MFSCommunication.h` packet types/statuses, `datapack` for endian-safe packing, common `sockets`, `main`, `cfg`, `clocks`, `charts`, and `mfslog`, `bgjobs` for offloaded work, `mainserv` for actual client read/write processing, `hddspacemgr` for disk info and error clearing, and `masterconn` for module identity and reconnects.

## Risks
Connection lifetime is coupled to background callbacks; `csserv_close` must disable jobs and null callbacks before freeing entries. `idlejob` cleanup intentionally leaves detached jobs to complete with `eptr == NULL`, so future changes must preserve that safety. Packet size checks protect allocations, but many handlers allocate based on request flags and assume `malloc` succeeds. `csserv_reload` logs the old address in some failure/success messages even while handling new address values, which can confuse diagnostics. The timeout is short (5 seconds), so slow clients or blocked write buffers may be dropped quickly.

## Test Signals
Strong tests include packet parser behavior for partial headers/bodies, maximum packet rejection, malformed-size closure for each command, queue-full read/write immediate status, callback completion returning state to idle, closing a connection with outstanding jobs, idle chunk-info replies for success and error statuses, chart/HDD/admin command responses, listen reload with `masterconn_forcereconnect`, and byte counters resetting through `csserv_stats`.
