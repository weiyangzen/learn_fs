# sources/distributed-fs/openafs/src/rx/test/testclient.c

## Purpose
`testclient.c` is a manual RX throughput and behavior test client. It sends either a byte stream of configured size or a file to a test server and reports throughput and RX peer stats.

## Important APIs, Types, and Functions
- `main()` parses many transport-tuning options, initializes RX, creates an rxnull connection to service id `3` on port 2500, and performs calls.
- `SendFile()` streams a file over a single RX call and reads the server reply.
- `Abort()`, `Quit()`, `intSignal()`, and `quitSignal()` print RX stats and exit.
- `OpenFD()` opens `/dev/null` descriptors until a target fd number is reached, for fd-number stress testing.

## Control Flow
The client parses packet/window/drop/log/timing/file options, resolves the target host, optionally opens filler descriptors, initializes RX, creates a connection, and either runs `SendFile()` or loops over `nCalls` synthetic payload calls. For synthetic calls it writes until `nBytes` are sent, reads all response bytes, ends the call, reports throughput, optionally sleeps for compute/wait timing, and prints peer stats.

## State and Persistence
Global knobs include `print`, `eventlog`, `rxlog`, `fillPackets`, `timeout`, `waitTime`, `computeTime`, and `timeReadvs`. Optional persistent debug output is `rx_ctest.db`; file mode reads the named file but does not persist new local data.

## Dependencies and Integration Points
Uses RX core, RX globals, rxnull, RX clocks, `hostutil_GetHostByName`, and OpenAFS utility allocation. It pairs with `testserver.c`, especially the file-transfer mode and remote status `79` check.

## Risks and Edge Cases
`Abort()` passes a `va_list` to `printf` instead of `vprintf`, so formatted abort messages are unreliable. In `SendFile()`, `rx_Read(call, buf, sizeof(buf))` uses the size of the pointer, not the allocated block size. Large `nBytes` use a 4 MB buffer without initialization, so payload contents are arbitrary. Many transport globals are changed directly and depend on RXDEBUG or platform guards.

## Test Signals
Expected signals are throughput lines, response byte counts, and printed RX peer stats. File mode additionally detects remote status `79`, prints server response text, and reports file-send throughput.
