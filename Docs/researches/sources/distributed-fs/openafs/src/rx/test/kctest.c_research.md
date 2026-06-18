# sources/distributed-fs/openafs/src/rx/test/kctest.c

## Purpose
`kctest.c` is a simple RX client benchmark/regression tool. It connects to an RX test server, sends a single XDR-encoded long value, decodes the response, and measures average call latency.

## Important APIs, Types, and Functions
- `ParseCmd()` handles `-port`, `-host`, `-count`, `-security`, `-log`, and `-stats`.
- `SigInt()` prints RX stats, finalizes RX, and exits.
- `nowms()` provides coarse millisecond timing.
- `main()` initializes RX, creates an rxnull security object, creates a connection, loops over `count` calls, and uses `xdrrx_create()` plus `xdr_long()`.

## Control Flow
Defaults target localhost port 10000 with one unauthenticated call. After parsing, the client initializes RX with an ephemeral local port, creates an rxnull client security class, and constructs a connection to service id `1`. Each iteration creates a call, encodes `1988`, switches the same `XDR` object to decode mode, reads the returned value, expects `1989`, ends the call, and finally prints timing.

## State and Persistence
State is held in static globals for host, port, count, security level, and stats mode. Optional persistent output is `kctest.log` assigned to `rx_debugFile`.

## Dependencies and Integration Points
Depends on RX core, RX globals, rxnull, and XDR-over-RX (`xdrrx_create`). It pairs with `kstest.c`, whose server increments the decoded long value.

## Risks and Edge Cases
Only security level 0 is accepted. `count` is a `short`, so large counts truncate. The code calls `SigInt(0)` at normal completion, which exits with status 1 after finalization. Host and port are stored in network order after parsing; defaults are already network-ordered.

## Test Signals
Expected signal is `wrong value returned` never appearing and a printed average milliseconds-per-call line. RX debug/stat output on interrupt or completion provides transport diagnostics.
