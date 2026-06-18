# sources/distributed-fs/ceph-client/tools/testing/selftests/net/tcp_ao/restore.c

## Purpose
`restore.c` verifies that an established TCP-AO connection can be checkpointed with TCP repair, killed, restored onto another socket, and continue exchanging authenticated traffic. It also deliberately corrupts restored TCP-AO repair fields to confirm mismatches break the connection and increment the expected AO counters.

## Important APIs, Types, And Functions
Core routines are `try_server_run()`, `test_get_sk_checkpoint()`, `test_sk_restore()`, `server_fn()`, and `client_fn()`. The test uses TCP repair helpers such as `test_enable_repair()`, `test_sock_checkpoint()`, `test_ao_checkpoint()`, `test_sock_restore()`, `test_add_repaired_key()`, `test_ao_restore()`, `test_disable_repair()`, `test_kill_sk()`, and `test_sock_state_free()`, plus AO counter and trace expectation helpers.

## Control Flow
The server iterates through five ports. For each port it listens, installs an AO key, accepts a client, performs a pre-migration echo, then attempts another echo after the client restores its socket. The client creates a matching AO socket, connects, verifies traffic, checkpoints TCP and AO state, kills the original socket, and restores a new socket. The first case uses valid state; subsequent cases increment send ISN, receive ISN, send SNE, or receive SNE before restore and register expected mismatch tracepoints.

## State, Persistence, And Dependencies
State is transient TCP repair image data in `struct tcp_sock_state`, `sockaddr_af`, and `struct tcp_ao_repair`. Network state lives in the two test namespaces created by `setup.c`. The test depends on TCP-AO, TCP repair support, ftrace event expectation helpers, netstat counters such as `TCPAOGood`/`TCPAOBad`, and the shared socket echo helpers.

## Integration Points
This test exercises the kernel TCP-AO repair ABI together with normal established TCP traffic. It integrates AO key installation, AO repair state restore, netstat deltas, per-socket counters, and tracepoint verification.

## Risks
The restore path is sensitive to barrier ordering between server and client. Fault cases rely on timeouts and counter changes to distinguish a broken authenticated connection from an unrelated scheduling delay. Incorrect cleanup of repaired sockets can leave peers in states where AO counters are unavailable. The test assumes tracepoint support when event expectations are registered.

## Test Signals
`main()` declares 21 planned checks. Passing signals include the valid restored connection staying alive, corrupted restore cases timing out or failing as expected, `TCPAOGood`/`TCPAOBad` increasing in the right direction, `test_assert_counters()` matching expected bitmasks, and AO mismatch tracepoints appearing for the corrupted fields.
