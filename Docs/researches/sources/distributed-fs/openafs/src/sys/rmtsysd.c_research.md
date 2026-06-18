# sources/distributed-fs/openafs/src/sys/rmtsysd.c

## Purpose
`rmtsysd.c` is the standalone daemon main for the RMTSYS service, which exposes remote `setpag` and `pioctl` over RX for AFS client hosts.

## Important APIs, types, and functions
The only routine is `main`. It uses `rx_Init`, `rxnull_NewServerSecurityObject`, `rx_NewService`, `rx_SetMaxProcs`, `rx_StartServer`, and generated `RMTSYS_ExecuteRequest`.

## Control flow
On AIX it enables full core dumps for abort/segv. It initializes RX on `AFSCONF_RMTSYSPORT`, creates a null-security RX service with `RMTSYS_SERVICEID` and `AFSCONF_RMTSYSSERVICE`, limits server procs to two, and donates the process to the RX server loop.

## State and persistence behavior
The daemon opens a listening RX endpoint and runs indefinitely. It does not persist data directly; server request handlers mutate local cache-manager/PAG state.

## Dependencies and integration points
It depends on RX, generated RMTSYS RPC code, `rmtsyss.c` request handlers, and afsd or service management that starts the daemon.

## Risks
Only null security is configured, so exposure must be controlled by deployment assumptions. Startup failure paths call `rmt_Quit` and exit. The fixed max-procs value may limit throughput or hide concurrency bugs.

## Test signals
Start the daemon on an isolated port/client, verify RX service registration, remote `pioctl` and `setpag` calls, startup failure when port is in use, and AIX signal setup in platform builds.
