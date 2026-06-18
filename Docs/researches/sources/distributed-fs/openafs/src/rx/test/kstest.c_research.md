# sources/distributed-fs/openafs/src/rx/test/kstest.c

## Purpose
`kstest.c` is the matching simple RX server for `kctest.c`. It decodes one long value from each call, increments it, encodes it back, and runs as a donated-thread RX server.

## Important APIs, Types, and Functions
- `ParseCmd()` handles `-port`, `-log`, and `-stats`.
- `rxk_erproc()` is the request handler; it wraps the call in an `XDR` stream, decodes a long, increments it, and encodes the result.
- `main()` initializes RX, creates an rxnull server security object, registers service id `1`, and calls `rx_StartServer(1)`.

## Control Flow
The server defaults to UDP port 10000, parses options, initializes RX, installs a SIGINT handler, creates rxnull security, registers the service, and donates the main thread to the RX server loop.

## State and Persistence
The only mutable static state is the listening port and `stats` flag. Optional persistent output is `kstest.log` through `rx_debugFile`.

## Dependencies and Integration Points
Integrates with RX server APIs, rxnull, RX debug stats, and XDR-over-RX. It is a direct protocol counterpart to `kctest.c`.

## Risks and Edge Cases
The handler does not check `xdr_long()` return values, so malformed or truncated calls may be treated as zero/undefined local state. `SigInt()` exits without `rx_Finalize()`, unlike the client. The service security array is sized for three but only index 0 is used.

## Test Signals
Normal startup prints initialization and service creation messages. A `kctest` client should receive `1989` after sending `1988`; interrupt-time stats indicate transport behavior.
