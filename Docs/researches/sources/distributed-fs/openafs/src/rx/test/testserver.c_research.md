# sources/distributed-fs/openafs/src/rx/test/testserver.c

## Purpose
`testserver.c` is the companion RX throughput/file-transfer test server. It receives synthetic byte streams or writes incoming call data to a file, sends a fixed response string, and exposes many RX tuning/debug switches.

## Important APIs, Types, and Functions
- `main()` parses server options, initializes RX on port 2500, creates an rxnull service id `3`, configures process counts and reachability checks, and starts the server.
- `SimpleRequest()` drains a call into a static 2 MB buffer, optionally simulates compute/wait delay, and writes a fixed response.
- `FileRequest()` receives call data into `rcvFile`, sets RX local status `79`, writes a fixed response, and prints peer stats.
- `Abort()`, `Quit()`, and `OpenFD()` mirror the client-side helpers.

## Control Flow
Command-line parsing sets debug, packet/window, delay, file, drop, jumbo, and fd options. After RX initialization, the registered execute function is `FileRequest` when `-file` is present, otherwise `SimpleRequest`. RX then owns execution via `rx_StartServer(1)`.

## State and Persistence
Persistent effects include optional `rx_stest.db` logs, optional trace file configuration, and file output in `FileRequest()`. Global mutable state controls error return, print mode, debug logging, delays, and receive-file path.

## Dependencies and Integration Points
Uses RX core, rxnull, RX clocks, RX globals, OpenAFS abort helpers, and optional RXDEBUG trace/drop variables. It is designed for `testclient.c`.

## Risks and Edge Cases
`Abort()` has the same `printf`/`va_list` misuse as the client. `FileRequest()` allocates `buffer` but never frees it. `error` is parsed but not returned by `SimpleRequest()` or `FileRequest()`. Direct manipulation of RX globals makes the tool sensitive to RX build configuration.

## Test Signals
Startup prints packet-buffer count. Runtime signals include received-byte logs in verbose mode, fixed response text observed by the client, file creation in `-file` mode, and RX peer/stat output.
