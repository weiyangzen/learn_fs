# sources/distributed-fs/ceph-client/tools/testing/selftests/net/tcp_ao/self-connect.c

## Purpose
`self-connect.c` tests TCP-AO behavior for TCP self-connect on loopback, where a single socket binds and connects to its own local address and port. It covers same key IDs, different send/receive key IDs, and TCP repair restore of self-connected AO sockets.

## Important APIs, Types, And Functions
The main helpers are `__setup_lo_intf()`, `setup_lo_intf()`, `tcp_self_connect()`, and `client_fn()`. The test uses `test_add_key()`, `test_add_repaired_key()`, `__test_connect_socket()`, `test_client_verify()`, `test_get_tcp_counters()`, `test_assert_counters()`, `test_enable_repair()`, `test_sock_checkpoint()`, `test_ao_checkpoint()`, `__test_sock_restore()`, `test_ao_restore()`, and trace expectations for `TCP_AO_RNEXT_REQUEST`.

## Control Flow
The single client thread configures loopback with either `127.0.0.1/8` or `::1/128`, adds a route to itself, and runs four self-connect scenarios. Each scenario creates one socket, installs AO keys, binds to the target local address and port, connects back to itself through `lo`, exchanges echo traffic, and checks AO counters. Restore scenarios checkpoint TCP and AO state, kill the original socket, restore onto a new port, reinstall repaired keys, restore AO state, and verify traffic again.

## State, Persistence, And Dependencies
The test mutates only the isolated test namespace loopback device, route table, and transient sockets. `local_addr` stores the loopback address. It depends on loopback routing, TCP-AO, TCP repair, ftrace expectation support for key rotation events, and shared TCP-AO helpers.

## Integration Points
Self-connect stresses a corner case where local and remote AO endpoint addresses are identical and both directions share one socket. It integrates AO key lookup, rnext/current-key behavior, route setup on `lo`, and repair restore using the same local and peer sockaddr.

## Risks
Self-connect behavior is unusual and may be sensitive to route selection and local address setup. Different key ID tests assume a predictable RNext negotiation trace. Restore changes the port, so mistakes in sockaddr port rewriting can make the restored flow fail for reasons unrelated to AO.

## Test Signals
`main()` plans 5 checks. Passing signals include successful traffic verification, `TCPAOGood` increasing, no unexpected counter deltas, and expected RNext trace events for different-key-ID scenarios, including the intentionally reversed repair key installation order.
