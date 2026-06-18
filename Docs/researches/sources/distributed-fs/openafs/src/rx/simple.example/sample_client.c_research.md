# sources/distributed-fs/openafs/src/rx/simple.example/sample_client.c

## Purpose
Demonstrates a minimal RX client that connects to the sample service and invokes generated add/subtract RPCs.

## Important APIs, Types, And Functions
The local helper `GetIpAddress` resolves a hostname with `gethostbyname`. `main` calls `rx_Init(0)`, creates a null client security object with `rxnull_NewClientSecurityObject`, opens a connection with `rx_NewConnection`, and repeatedly calls generated `TEST_Add` and `TEST_Sub`.

## Control Flow
The program expects the server hostname as `argv[1]`, resolves it, initializes RX on an ephemeral local port, creates a null-security connection to `SAMPLE_SERVER_PORT`/`SAMPLE_SERVICE_ID`, then loops from 1 to 9 printing each RPC input, result, and error code.

## State And Persistence
State is limited to the process RX runtime, one connection, and loop-local result variables. No persistence exists.

## Dependencies And Integration Points
It includes generated `sample.h`, RX runtime APIs, null security, and libc networking. It exercises the generated client stubs from `sample.xg` and the sample server.

## Risks And Test Signals
Risks include no argument validation before `argv[1]`, legacy IPv4-only `gethostbyname`, no connection destruction/finalization, and null security being unsuitable beyond a demo. Test signal is successful printed add/subtract responses against `sample_server`.
