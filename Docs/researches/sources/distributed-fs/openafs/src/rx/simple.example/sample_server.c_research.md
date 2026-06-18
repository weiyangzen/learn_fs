# sources/distributed-fs/openafs/src/rx/simple.example/sample_server.c

## Purpose
Demonstrates a minimal RX server that exports generated sample add/subtract RPC operations over null security.

## Important APIs, Types, And Functions
`main` initializes RX with `rx_Init(SAMPLE_SERVER_PORT)`, creates a null server security object, registers a service with `rx_NewService`, and donates the process to the server pool with `rx_StartServer(1)`. Server RPC handlers `STEST_Add` and `STEST_Sub` implement generated service operations. `Quit` prints an error and exits.

## Control Flow
Startup initializes RX on the fixed sample port, builds the one-entry security object array, creates the service using generated `TEST_ExecuteRequest`, and enters the RX server loop. Incoming RPCs dispatch through generated server stubs into `STEST_Add`/`STEST_Sub`, which compute results and return success.

## State And Persistence
State is in-memory RX service registration and security object state. No persistent storage is used.

## Dependencies And Integration Points
It depends on generated `sample.h`, RX service APIs, null security, and generated server stubs from `sample.xg`. It is paired with `sample_client.c`.

## Risks And Test Signals
Risks include null security, fixed port conflicts, minimal error reporting, and no graceful shutdown path. Test signals are service startup and correct client-visible add/subtract results.
