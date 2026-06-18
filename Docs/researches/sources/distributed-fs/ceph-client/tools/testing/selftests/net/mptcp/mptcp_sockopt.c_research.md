# sources/distributed-fs/ceph-client/tools/testing/selftests/net/mptcp/mptcp_sockopt.c

## Purpose
`mptcp_sockopt.c` is a C selftest helper for MPTCP socket option ABI behavior. It validates `SOL_MPTCP` options, per-subflow TCP info and addresses, `MPTCP_FULL_INFO`, packet/stat counters, forward/backward-compatible length handling, and normal inherited socket options such as `IP_TOS`.

## Important APIs, Types, And Functions
The file defines fallback UAPI structures for `mptcp_info`, `mptcp_subflow_data`, `mptcp_subflow_addrs`, `mptcp_subflow_info`, and `mptcp_full_info` if headers are older. `struct so_state` tracks previous MPTCP and TCP samples. Core functions are `do_getsockopt_bogus_sf_data()`, `do_getsockopt_mptcp_info()`, `do_getsockopt_tcp_info()`, `do_getsockopt_subflow_addrs()`, `do_getsockopt_mptcp_full_info()`, `do_getsockopts()`, `test_ip_tos_sockopt()`, `connect_one_server()`, `process_one_client()`, `server()`, `client()`, and `main()`.

## Control Flow
`main()` parses `-6`, seeds randomness, creates a pipe, forks a server, waits for listener readiness, then forks a client. The server listens on loopback MPTCP, accepts one connection, samples sockopts, echoes received data, waits for EOF, and checks post-transfer counters. The client connects over MPTCP, validates `IP_TOS` set/get corner cases, samples initial sockopts, writes a random buffer, reads the echo, and checks MPTCP and TCP byte counters. The option-specific functions verify sizes, kernel/user truncation, subflow count `1`, socket local/remote address equivalence, and `MPTCP_FULL_INFO` consistency with prior `MPTCP_INFO`, `TCP_INFO`, and address samples.

## State, Persistence, And Dependencies
State is transient process/socket state: one listener, one accepted socket, one client socket, a pipe for readiness, random transfer buffers, and sampled structs. No persistent output is written. The helper depends on MPTCP kernel support, `SOL_MPTCP` getsockopts, loopback networking, and packet-stat fields that may be absent on older kernels; the code tolerates shorter `MPTCP_INFO` by treating packet stats as unavailable.

## Integration Points
`mptcp_sockopt.sh` invokes this binary inside a sandbox namespace for IPv4 and IPv6. Its success contributes TAP subtests named `sockopt v4` and `sockopt v6`. The helper also indirectly tests kernel UAPI compatibility because it carries local structure definitions for builds against older headers.

## Risks
Many assertions assume exactly one subflow; if the environment or path manager creates additional subflows, the helper fails even if the API works. It uses fixed port `15432` and 15-second alarms. Some TCP byte counters may update asynchronously, so `do_getsockopt_tcp_info()` polls up to five times. `MPTCP_FULL_INFO` may legitimately return `EOPNOTSUPP`, which is treated as a skip-like message inside the helper, not a process skip.

## Test Signals
Pass signals are zero exit status, correct MPTCP/TCP byte deltas, expected subflow data layout behavior for good and bogus buffers, matching subflow addresses, and valid `IP_TOS` behavior. Failures identify getsockopt ABI regressions, incorrect length negotiation, wrong subflow counts, mismatched addresses, stale counters, or unexpected process exits.
