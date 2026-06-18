# sources/distributed-fs/moosefs/mfschunkserver/csserv.h

## Purpose
`csserv.h` declares the public surface of the chunkserver client service module. It lets other modules initialize the service, query its listen address, and collect/reset byte counters.

## Important APIs
`void csserv_stats(uint64_t *bin, uint64_t *bout)` returns bytes read and written by the service since the last call and resets those counters. `uint32_t csserv_getlistenip(void)` returns the numeric listen IP selected during initialization or reload. `uint16_t csserv_getlistenport(void)` returns the numeric listen port. `int csserv_init(void)` starts listening and registers the module with the common main-loop framework.

## Control Flow and Integration
Startup code calls `csserv_init`; after that, service activity is driven by poll callbacks registered inside the implementation. `chartsdata.c` calls `csserv_stats` during periodic refresh. `masterconn` can use the listen IP/port accessors when reporting this chunkserver to the master.

## State and Persistence
The header exposes no state. The implementation maintains the listen socket, connection list, and counters in process memory. Listen host and port are configuration-derived and may change on reload.

## Dependencies
Only `<inttypes.h>` is required by the header. The implementation has broader dependencies on sockets, packet definitions, background jobs, disk management, charts, and master connection code.

## Risks
`csserv_stats` is destructive by design because it resets counters. Callers that sample too frequently or from multiple places will alter chart semantics. Listen address accessors depend on successful init/reload; callers should not assume meaningful values before `csserv_init` succeeds.

## Test Signals
Compile-time signals come from inclusion by startup, chart, and master modules. Runtime signals include successful service initialization, nonzero byte counters after traffic, counter reset after `csserv_stats`, and listen IP/port reflecting configuration and reload changes.
