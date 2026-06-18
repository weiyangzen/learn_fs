# sources/distributed-fs/openafs/src/rxdebug/rxdebug.c

## Purpose
`rxdebug.c` implements the `rxdebug` command-line utility, which probes a remote RX server over UDP and prints server stats, RX stats, connection state, security stats, peer metrics, and server version.

## Important APIs, Types, and Functions
- `PortNumber()` parses numeric ports and returns network byte order.
- `PortName()` resolves service names with `getservbyname`.
- `MainCommand()` performs argument interpretation, socket setup, debug RPCs, filtering, and reporting.
- `main()` registers command syntax through the OpenAFS `cmd` package and dispatches.

## Control Flow
The command resolves the target host and port, opens/binds a UDP socket, optionally fetches server version and exits, then calls `rx_GetServerDebug()` to learn stats and supported feature flags. Depending on flags it fetches RX stats, iterates connections with `rx_GetServerConnections()`, filters by dally state, host, port, client/server type, and auth level, prints per-call state, and optionally iterates peers with `rx_GetServerPeers()`.

## State and Persistence
The utility persists no files. Runtime state is local to `MainCommand`: next-connection/peer cursors, supported-feature bitmasks, filters, and display options.

## Dependencies and Integration Points
Depends on RX user debug APIs, RX data structure constants, host utilities, command parser, RX statistics printer, and optional rxgk security stats. It is installed by `rxdebug/Makefile.in`.

## Risks and Edge Cases
Output depends heavily on server-supported debug flags; unsupported features downgrade with warnings. Auth filtering assumes rxkad and rxgk levels use matching numeric constants. The fixed 64-byte version buffer truncates longer version strings. Remote debug calls can fail with negative codes and terminate the utility.

## Test Signals
Probe a local fileserver/default port, `-version`, `-rxstats`, `-noconns`, filtered connection modes, and peer output. Backward-compatibility tests should cover servers lacking newer debug flags.
