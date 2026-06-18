# sources/distributed-fs/ceph-client/tools/testing/selftests/net/fin_ack_lat.c

## Purpose
`fin_ack_lat.c` is a small TCP loopback latency probe used to detect latency spikes caused by a FIN/ACK handling race. It starts a server on an ephemeral local TCP port, forks a client, and continuously performs short connect/send/read/close cycles. The client prints a line only when a round trip exceeds 100 ms; the shell wrapper treats any printed line as a failure.

## Important APIs, Functions, and Types
The program uses POSIX sockets and timing APIs: `socket`, `setsockopt`, `bind`, `listen`, `getsockname`, `fork`, `connect`, `send`, `read`, `accept`, `close`, `gettimeofday`, `signal`, and `kill`. `timediff()` converts `struct timeval` pairs to microseconds. `client()` owns the active loop and latency calculation. `server()` accepts a connection, reads one integer, and closes immediately, creating the FIN/ACK interaction under test. `sig_handler()` attempts to terminate the child when the parent receives `SIGTERM`.

## Control Flow
`main()` installs a `SIGTERM` handler, creates an IPv4 TCP socket, enables `SO_REUSEADDR | SO_REUSEPORT`, binds to `INADDR_ANY` with port zero, listens, discovers the chosen port, prints it to stderr, and forks. The child calls `client(port)`, repeatedly connecting to `127.0.0.1`, sending an integer, reading until the server close, timing the whole operation, and closing with `SO_LINGER` set to zero and `TCP_NODELAY` enabled. The parent calls `server()`, which loops accepting and closing connections after a read.

## State and Persistence
State is process-local: a global `child_pid`, socket descriptors, timing counters (`sum_lat`, `nr_lat`), and the ephemeral server port. No files are written by the C program. The parent and child run indefinitely until externally killed by the wrapper or signal handling.

## Dependencies and Integration Points
The file is compiled as a generated selftest binary and invoked by `fin_ack_lat.sh`. It assumes IPv4 loopback is available and that TCP sockets support linger and `TCP_NODELAY`. It integrates with the test by emitting spike lines to stdout and server port information to stderr.

## Risks
The signal handler calls `kill(SIGTERM, child_pid)`, which reverses the usual `kill(pid, signal)` argument order. In practice the shell wrapper kills processes by name, but this handler is suspicious and could fail to reap the child as intended. The client reads from a connection the server closes without sending data; the test relies on timing of close/error behavior rather than payload echo. There is no rate limiting in the loop, so the test can be CPU-intensive during the 30-second wrapper run.

## Test Signals
The key signal is absence of stdout lines over the wrapper runtime. Each printed line includes local port, latency in microseconds, average latency, and sample count, and represents a latency spike above 100 ms. Process exit is normally controlled by the shell wrapper rather than the program returning from `main()`.
