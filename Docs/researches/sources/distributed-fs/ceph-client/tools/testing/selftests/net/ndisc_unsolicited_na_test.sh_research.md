## sources/distributed-fs/ceph-client/tools/testing/selftests/net/ndisc_unsolicited_na_test.sh

Purpose: validates IPv6 neighbor discovery behavior for RFC9131-style `accept_untracked_na`, specifically whether unsolicited Neighbor Advertisements create STALE neighbor cache entries only when `drop_unsolicited_na=0`, `accept_untracked_na=1`, and forwarding is enabled.

Important APIs and tools: sources `lib.sh` for namespace helpers and kselftest counters, uses `ip -6`, `ip netns exec`, interface sysctls under `net.ipv6.conf.<if>`, `tcpdump`, and neighbor table queries via `ip neigh show ... nud stale`.

Control flow: option parsing supports pause modes. For each matrix entry, `setup()` creates host/router namespaces connected by a veth, configures router sysctls and IPv6 address, and enables host `ndisc_notify`. `link_up()` brings both ends up so the host emits unsolicited NA. `start_tcpdump()` captures one NA packet, and `verify_ndisc()` checks whether the router neighbor table contains the expected STALE entry. `test_unsolicited_na_combinations()` runs the single expected-accept case and seven expected-drop/no-update cases, logging pass/fail counts via `log_test()`.

State and persistence: creates temporary namespaces, veths, sysctl mutations, and temporary tcpdump files; cleanup removes tcpdump files and namespaces. Dependencies include root, `ip`, `tcpdump`, and IPv6 sysctls. Risks include asynchronous NA timing, `tcpdump` timeout behavior, missing kernel support for the sysctls, and possible stale namespace variables if setup fails before assignment. Test signals are per-case `[ OK ]`/`[FAIL]`, total pass/fail counts, and final `ret`.
