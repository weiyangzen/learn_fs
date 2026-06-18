## sources/distributed-fs/ceph-client/tools/testing/selftests/net/msg_zerocopy.sh

Purpose: namespace harness for `msg_zerocopy`, exercising IPv4/IPv6 TCP and UDP by default and supporting manual runs for TCP, UDP, raw, raw header-included, packet, and packet datagram modes. It compares local tx-rx behavior, where zerocopy may be copied, with a tx-only path through a dummy device, where outgoing packets should remain zerocopy.

Important APIs and tools: uses `ip netns`, veth and dummy devices, namespace-local `sysctl net.core.optmem_max`, fixed MAC and IP addresses, route setup, and the compiled `./msg_zerocopy` binary. It relies on kernel namespace, veth, dummy, IPv4/IPv6 forwarding, and sufficient privileges.

Control flow: no arguments trigger four automated tests: IPv4/IPv6 TCP and UDP. With arguments, it validates IP version and mode, maps transmit mode to receive mode for packet/raw-hdrincl cases, creates two namespaces, configures a high-MTU veth and a dummy interface, assigns deterministic addresses and routes, enables forwarding in the receiver namespace, then calls `do_test()` twice: once without `-z`, once with `-z`. `do_test()` first starts a receiver in namespace 2 and a sender in namespace 1 against the veth destination, then for non-TCP modes performs a tx-only send to the dummy-routed destination.

State and persistence: namespace and link state are temporary and cleaned by `trap cleanup EXIT`; no files are persisted. Integration points are the C helper, network namespace support, route behavior, and zerocopy completion semantics. Risks include background receiver timing (`sleep 0.2`), optmem limits, missing binary, and root requirement. Test signal is final `OK` plus exit status accumulated in `ret`.
