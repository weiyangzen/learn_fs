# sources/distributed-fs/ceph-client/tools/testing/selftests/net/double_udp_encap.sh

Purpose: this script validates segmentation and coalescing behavior for TCP over nested UDP tunnels. It builds two namespaces connected by veth, creates nested VXLAN or Geneve tunnel devices over IPv4 and IPv6, sends large TCP payloads with `udpgso_bench_tx`, receives with `udpgso_bench_rx`, and counts outer tunnel packets to verify GSO/GRO behavior.

Important APIs and commands: it sources `lib.sh`, uses YNL `pyynl/cli.py` for Geneve link creation, `ip link add type vxlan`, `ethtool -K` feature toggles, `iptables`/`ip6tables` length and BPF matches, `nfbpf_compile`, `jq`, `wait_local_port_listen`, `udpgso_bench_rx`, and `udpgso_bench_tx`.

Control flow: `create_ns` builds the base topology, creates outer and nested tunnel endpoints, assigns underlay and overlay addresses, adjusts nested MTUs, disables selected veth offloads, and sets TCP write memory. `create_ns_gso` enables tunnel GSO features on the source tunnel. `create_ns_gso_gro` additionally enables GRO on the destination veth and disables source veth TX offload. `run_test` computes expected segment counts, compiles a packet-offset BPF filter that identifies the double-encapsulated TCP stream, installs counters on source OUTPUT and destination INPUT, runs receiver and sender, then compares iptables packet counters against expected wire and received tunnel packet counts. `run_tests` iterates IPv4/IPv6, VXLAN/Geneve, no-GSO, GSO, fixed-ID-disabled IPv4, and Geneve GRO hint/csum/inner-proto-inherit scenarios.

State and persistence: it creates and deletes network namespaces and tunnel devices through `cleanup_all_ns`. Persistent files are not written. Kernel state includes offload settings, iptables rules, tunnel endpoints, and sysctls.

Dependencies and integration points: requires root, namespace support, VXLAN/Geneve, ethtool offload controls, bench binaries, BPF match support, iptables, and the YNL CLI. It integrates with generated net selftest binaries in the same directory.

Risks and test signals: packet-offset BPF filters are tightly coupled to encapsulation header layouts and options such as `USE_HINT` and `INHERIT`. TCP retransmissions can break accounting; the script wraps `run_tests` in `xfail_on_slow`. Strong signals are sender/receiver zero exits and exact tunnel packet counters for no-GSO, GSO, GRO, checksum, and short-last-packet cases.
