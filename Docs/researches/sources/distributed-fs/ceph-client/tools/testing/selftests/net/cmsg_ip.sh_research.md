# sources/distributed-fs/ceph-client/tools/testing/selftests/net/cmsg_ip.sh

Purpose: this script verifies IP-related send-time control message behavior across IPv4, IPv6, UDP, UDP with `MSG_MORE`, ICMP, and raw sockets. It checks IPv6 `DONTFRAG`, IPv4 TOS / IPv6 traffic class, IPv4 TTL / IPv6 hop limit, and basic IPv6 extension-header cmsg handling.

Important APIs and commands: it sources `lib.sh`, creates one namespace with `setup_ns`, configures a dummy interface with IPv4 and IPv6 addresses, runs `./cmsg_sender`, captures packets with `tcpdump --immediate-mode`, and uses policy routing rules plus prohibit routes to detect TOS/TCLASS control. `check_result` records total and failed cases.

Control flow: after verifying tcpdump support, it creates namespace connectivity and allows unprivileged ping sockets. The `IPV6_DONTFRAG` matrix sends 2000-byte packets with option sources `setsock`, `cmsg`, `both`, and conflicting values, expecting return code equal to the don't-fragment value. `test_dscp` installs a prohibit rule for one DSCP/TOS value, sends packets with setsockopt/cmsg combinations, checks tcpdump output for the expected field, and checks rejection when the prohibited value is used. `test_ttl_hoplimit` captures packets and greps decoded TTL/hlim. The final extension-header loop sends hop-by-hop, destination, and routing-destination options and treats non-crash success as the signal.

State and persistence: state is namespace-local routes, rules, dummy link addresses, and a temporary pcap file removed in `cleanup`. No persistent repository files are modified.

Dependencies and integration points: depends on `cmsg_sender`, tcpdump with immediate mode, `ip`, namespace support, and packet decoding strings stable enough for grep. It integrates with `cmsg_sender.c` option names: `-f/-F`, `-c/-C`, `-l/-L`, `-H`, `-p`, `-4`, and `-6`.

Risks and test signals: tcpdump startup uses a fixed short sleep and packet-count loops, so slow systems can be flaky. Grep-based packet validation depends on tcpdump formatting. Strong signals are expected sender return codes, prohibited-route failures for controlled TOS/class values, and decoded packet fields matching the cmsg-selected values.
