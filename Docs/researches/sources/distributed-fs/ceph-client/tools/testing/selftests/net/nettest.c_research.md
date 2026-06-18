<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/nettest.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/net/nettest.c

## Purpose
`nettest` is a general-purpose networking selftest utility that can run as client, server, or combined forked client/server. It exercises TCP, UDP, raw sockets, multicast, device binding, address expectations, network namespace switching, TCP MD5 signatures, DS fields, freebind, control-message device selection, XFRM UDP encapsulation, and interactive or repeated message loops.

## Important APIs, Types, And Functions
The core type is `struct sock_args`, which carries addresses, ports, socket type/protocol, namespace names, device binding, expected addresses/devices, multicast group, MD5 credentials, XFRM flags, and mode bits. Major functions include logging helpers, `switch_ns()`, `tcp_md5sig()`, `tcp_md5_remote()`, device helpers, socket-option helpers, `convert_addr()`, `validate_addresses()`, `send_msg*()`, `socket_read_*()`, `msg_loop()`, multicast socket setup, listener/client socket setup, `config_xfrm_policy()`, `do_server()`, `do_client()`, IPC helpers, and `main()` option parsing.

## Control Flow
`main()` parses a broad CLI, validates required address/port/mode combinations, resolves protocols, and chooses server, client, or both mode. Both mode forks a server child, waits for readiness over a pipe, then runs the client. Server mode can bind/listen/read datagrams or accept streams; client mode creates and optionally connects a socket, validates local/remote addresses, sends messages, and reads replies. Message loops support fixed iterations, random payloads, stdin/stdout interactive mode, cmsg packet info, and expected interface/address checks.

## State, Persistence, And Dependencies
State is process-local plus optional namespace membership changed by `setns()`. It opens sockets, may fork, and may configure per-socket TCP MD5, freebind, reuse, DS field, multicast, pktinfo, recverr, SO_BINDTODEVICE, SO_DONTROUTE, and XFRM policy options. It depends on Linux networking headers/features and root privileges for namespace and some socket options.

## Integration Points
Many shell selftests use `nettest` as a flexible endpoint generator and verifier. It integrates socket API behavior with namespaces, device routing, multicast membership, TCP authentication, and IPsec/XFRM policy plumbing.

## Risks
The CLI surface is large, so invalid combinations can produce confusing outcomes. Some functions assume address family consistency after parse. `SO_BINDTODEVICE`, TCP MD5, raw sockets, and XFRM require capabilities. The combined mode kills the child after the client finishes, which is appropriate for tests but not graceful server shutdown.

## Test Signals
Signals are exit codes plus timestamped client/server logs showing binds, peers, expected address/device matches, send/receive success, timeouts, and socket-option failures. In quiet mode, only the exit status remains.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/nettest.c -->
