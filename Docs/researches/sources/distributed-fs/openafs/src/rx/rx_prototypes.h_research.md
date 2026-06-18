# sources/distributed-fs/openafs/src/rx/rx_prototypes.h

## Purpose
Centralizes RX internal and public prototypes across core RX, clock, connection cache, event, address, globals, kernel adapters, thread support, misc, multi-call, null security, packet, read/write, stats, user-space socket, and external OSI helper modules.

## Important APIs, Types, And Functions
The header declares lifecycle APIs (`rx_Init`, `rx_InitHost`, `rx_StartServer`, `rx_Finalize`, `shutdown_rx`), connection/call APIs, service creation, stats/debug APIs, RPC stats controls, event functions, address discovery, window configuration, kernel socket hooks, LWP/pthread primitives, packet functions from `rx_packet.c`, stream functions from `rx_rdwr.c`, stats allocation/free, user-space UDP helpers, MTU controls, and selected external AFS OSI functions. It also declares debug hooks `rx_justReceived` and `rx_almostSent`.

## Control Flow
This file has no runtime flow, but it documents module call boundaries. RX initialization sets up sockets, thread/event support, packet pools, services, and listeners; listeners feed packets to receive code; call processing uses the read/write APIs; packet APIs implement transport I/O; stats/debug APIs introspect those paths.

## State And Persistence
The header declares state surfaces but stores none. It exposes globals such as event counters, socket hooks, interface mutexes, and debug callback pointers, all of which are owned by implementation files.

## Dependencies And Integration Points
This is a high-fanout compatibility header for RX. It bridges user/kernel builds, platform variants, generated RX stubs, security classes, multi-call clients, and debug tools. Because many modules include it instead of narrower headers, declaration drift can have large build impact.

## Risks And Test Signals
Risks are stale prototypes, duplicate declarations under conditional compilation, mismatches between pthread/LWP/kernel signatures, and accidental exposure of private internals. Full matrix builds across pthread, LWP, Unix, Windows, and kernel configurations are the main test signal.
