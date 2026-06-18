
# `sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/lib/py/load.py`

## Purpose
Provides traffic generation helpers for driver tests, wrapping iperf3 server/client setup and a long-running packet generator.

## Important APIs, Types, And Functions
- `Iperf3Runner` builds server/client commands, starts one-shot servers, starts clients, and computes stable average bandwidth from JSON output.
- `GenerateTraffic` starts a one-shot server and a long-running 16-stream background client, waits for traffic ramp-up, and exposes `wait_pkts_and_stop()`.

## Control Flow
`Iperf3Runner` requires local and remote `iperf3`, picks or accepts a port, and uses the test environment's local address unless server/client bind IPs are provided. `GenerateTraffic` starts server then client, waits for at least 1000 pps, and raises if traffic does not ramp.

## State And Persistence
Maintains background process handles for iperf3 client and server. `stop()` terminates both, optionally logs stdout/stderr, and waits for the remote TCP connection to disappear from `/proc/net/tcp*`.

## Dependencies And Integration Points
Depends on `cmd`, `ip`, `wait_port_listen`, `rand_port`, remote command support, and interface RX packet stats. Used by page-pool failure, RSS, TSO, and other traffic-sensitive tests.

## Risks
`Iperf3Runner.start_server()` waits for the port locally because the server runs on the local host by default; client runs on `env.remote`. `GenerateTraffic._wait_pkts()` watches local RX packets, so it assumes reverse direction from remote client to local server.

## Test Signals
Traffic helpers raise if iperf3 fails, JSON is malformed, too few bandwidth samples are present, traffic does not ramp, or client shutdown does not complete within timeout.
