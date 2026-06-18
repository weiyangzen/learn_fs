## sources/distributed-fs/ceph-client/tools/testing/selftests/net/netfilter/ipvs.sh

Purpose: end-to-end IPVS validation for direct routing, NAT, and IPIP tunneling forwarding modes using a three-namespace topology and real TCP payload transfer.

Important APIs and tools: sources `lib.sh`, requires `ipvsadm`, `socat`, optional `modprobe ip_vs` and `ipip`, uses bridge/veth setup, `ipvsadm -A/-a`, loopback VIP assignment, ARP suppression sysctls, and file comparison.

Control flow: `setup()` creates ns0 client/bridge, ns1 director, and ns2 real server with veth links and random input payload. `server_listen()`, `client_connect()`, and `verify_data()` perform a TCP transfer to the VIP and compare bytes. `test_dr()` configures IPVS direct routing with VIP on director and real server loopback. `test_nat()` configures IPVS masquerading and changes real server default route. `test_tun()` configures IPVS IPIP tunnel mode with `tunl0` and VIP loopbacks. `run_tests()` resets topology between modes and sums errors.

State and persistence: temporary namespaces, bridge, IPVS services, temp input/output files; cleanup removes all. Dependencies include IPVS kernel modules/protocol, ipvsadm, socat, and IPIP for tunnel mode. Risks include hard-coded addresses, ARP behavior sensitivity, fixed TCP port 8080, and short timeout. Test signals are payload `cmp`, colored PASS/FAIL, and exit status.
