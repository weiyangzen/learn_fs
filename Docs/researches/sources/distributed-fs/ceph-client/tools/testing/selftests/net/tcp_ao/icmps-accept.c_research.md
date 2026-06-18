# sources/distributed-fs/ceph-client/tools/testing/selftests/net/tcp_ao/icmps-accept.c

Purpose: this source implements the TCP-AO ICMP interference test body. When built as `icmps-accept`, the Makefile defines `TEST_ICMPS_ACCEPT`, so the listener enables AO `accept_icmps` and the test expects matching ICMP hard errors to be accepted rather than ignored.

Important APIs and functions: the test uses `test_set_ao_flags`, `test_add_key`, `test_server_run`, `test_client_verify`, raw IPv4/IPv6 sockets, `TCP_REPAIR` and `TCP_QUEUE_SEQ` to obtain `rcv_nxt`, netstat readers, and TCP-AO counter helpers. Packet builders include `set_ip4hdr`, `icmp_interfere4`, `set_ip6hdr`, `icmp6_checksum`, `icmp6_interfere`, and `icmp_interfere`.

Control flow: the server listens with AO, sets `accept_icmps` according to the compile flag, accepts a connection, enables `IP_RECVERR` or `IPV6_RECVERR`, and runs `serve_interfered`. The client connects with AO, repeatedly sends valid data, obtains receive sequence state, and injects forged ICMP destination-unreachable packets matching the connection. The server checks destination-unreachable counters, AO dropped-ICMP counters, and whether data service failed or survived according to the build mode.

State and persistence: transient state includes packet counters, generated raw ICMP packets, TCP repair mode toggles, and netstat snapshots. In accept mode the expected state is that ICMPs are delivered as errors rather than counted as AO-dropped ICMPs. No durable files are modified.

Dependencies and integration points: compiled twice for IPv4/IPv6 and specifically with `-DTEST_ICMPS_ACCEPT` for this target. Requires raw socket privileges, TCP-AO support, TCP repair support, and the shared TCP-AO library.

Risks: source content is identical to `icmps-discard.c`; semantics depend entirely on the Makefile target flag. The raw packet construction is sensitive to kernel ICMP validation, sequence numbers, and address family layout. The code increments `icmps_sent` both in lower helpers and again in the loop, but that variable is not used as an assertion source.

Test signals: in accept mode, server failure with a hard error is considered OK, `TCPAODroppedIcmps` should not be required to increase, and counter assertions expect good AO traffic only. Destination unreachable counters must increase.
