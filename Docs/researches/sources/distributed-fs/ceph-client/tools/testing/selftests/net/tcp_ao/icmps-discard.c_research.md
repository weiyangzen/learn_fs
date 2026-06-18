# sources/distributed-fs/ceph-client/tools/testing/selftests/net/tcp_ao/icmps-discard.c

Purpose: this source implements the default TCP-AO ICMP discard test body. Built as `icmps-discard`, it does not define `TEST_ICMPS_ACCEPT`, so the test verifies RFC5925 default behavior: matching ICMP hard errors for established AO connections are ignored and counted as dropped.

Important APIs and functions: the file uses the same helpers as `icmps-accept.c`: `test_set_ao_flags`, `test_add_key`, `test_server_run`, raw ICMP/ICMPv6 packet generation, `TCP_REPAIR` receive-sequence reads, `netstat_read`, and `test_assert_counters`. Compile-time macros invert `test_icmps_fail` and `test_icmps_ok` depending on `TEST_ICMPS_ACCEPT`.

Control flow: server and client establish a valid AO connection. The client continuously sends verified data and injects forged destination-unreachable packets with embedded TCP headers matching the connection. The server serves a quota while `IP_RECVERR` or `IPV6_RECVERR` is enabled, then validates that destination-unreachable counters increased but the application connection survived.

State and persistence: all state is socket and namespace local. The key persistent signal during the run is counter deltas for `TCPAODroppedIcmps`, `InDestUnreachs` or `Icmp6InDestUnreachs`, and AO per-socket/per-namespace counters. No files are written.

Dependencies and integration points: built for IPv4 and IPv6 without the accept flag. It requires raw socket capability, TCP-AO, TCP repair, and the shared aolib network harness.

Risks: because it shares source text with `icmps-accept.c`, a build-system regression can silently change expected semantics. Raw ICMP injection is sensitive to checksum correctness and sequence selection. Timing depends on the server quota being long enough for injected ICMPs to arrive.

Test signals: a correct discard run reports delivered destination-unreachable packets, server survival, incremented `TCPAODroppedIcmps`, and `TEST_CNT_GOOD | TEST_CNT_AO_DROPPED_ICMP` counter deltas. A server hard-error failure is a test failure in this build.
