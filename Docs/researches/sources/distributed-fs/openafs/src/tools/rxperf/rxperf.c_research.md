# sources/distributed-fs/openafs/src/tools/rxperf/rxperf.c

## Purpose
Implements `rxperf`, a client/server benchmark for the OpenAFS Rx RPC transport. It measures one-way send, one-way receive, request/response RPC, and scripted alternating file-pattern transfers with tunable packet/window/MTU/thread options.

## Important APIs, Types, And Functions
The command modes are `RX_PERF_SEND`, `RX_PERF_RECV`, `RX_PERF_RPC`, and `RX_PERF_FILE`, all using `RX_SERVER_ID`, protocol version `RX_PERF_VERSION`, and `RXPERF_MAGIC_COOKIE`. Important functions include `rxperf_ExecuteRequest`, `do_server`, `do_client`, `client_thread`, `do_readbytes`, `do_sendbytes`, `readfile`, `rxperf_server`, `rxperf_client`, `str2addr`, `get_sec`, timer helpers, signal handlers, and `main`. Global knobs include `somebuf`, `rxwrite_size`, `rxread_size`, and `use_rx_readv`.

## Control Flow
`main` initializes process support, sets signal handlers, zeros the transfer buffer, and dispatches `server` or `client`. The server initializes Rx, applies transport options, creates a null-security Rx service, sets min/max procs, and blocks in `rx_StartServer`. The request handler reads version, command, negotiated read/write chunk sizes, and command-specific sizes or file pattern data, then drains or emits bytes and replies with the magic cookie when applicable. The client parses command options, initializes Rx, creates a connection, starts a timer, runs one or more client threads, waits for completion, prints elapsed time and throughput, optionally dumps Rx stats, and finalizes Rx.

## State And Persistence
Most state is process-local benchmark configuration. The server is network state on the selected UDP port; the client may open an output file for results and may read a pattern file for `file` mode. No durable OpenAFS database or token state is changed. Multi-threaded clients share one `client_data` instance until the code creates additional connections after `RX_MAXCALLS` thread groups.

## Dependencies And Integration Points
The tool integrates with Rx core APIs, rxnull security, Rx stats/debug globals, pthreads or LWP process support, roken `err`/`warn` helpers, sockets, resolver APIs, and platform winsock setup on Windows. It is a diagnostic tool rather than a production service.

## Risks And Test Signals
Risks include several unchecked allocations, shared `client_data` and global chunk-size variables across threads, integer overflow for very large byte counts, `readfile` leaking its read/write list in client threads, no validation that `-f` is present for file mode, and benchmark results depending on null security and local buffering. Tests should cover client/server protocol version mismatch, all four commands, `-V` readv mode, max chunk-size bounds, multi-thread limits, stats output, output-file handling, invalid option parsing, and a loopback smoke run.
