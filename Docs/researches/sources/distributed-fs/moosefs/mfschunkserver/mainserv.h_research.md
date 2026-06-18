# sources/distributed-fs/moosefs/mfschunkserver/mainserv.h

## Purpose
`mainserv.h` exposes the public surface of the chunkserver main data service: stats, packet-level read/write handlers, and initialization.

## APIs and integration
`mainserv_stats()` returns and resets byte and high-level operation counters. `mainserv_read()` and `mainserv_write()` handle already-accepted sockets plus decoded packet payloads and return success/failure as `uint8_t`. `mainserv_init()` starts module state such as NOP support and connection cache.

The header is used by startup and by the chunkserver acceptor/dispatcher. It intentionally hides write-chain internals, packet allocation, and socket keepalive machinery.

## Risks and test signals
Detailed errors are conveyed through protocol status packets rather than the boolean return. Tests should verify caller disconnect behavior, status packet emission, and counter reset semantics for chart consumers.
