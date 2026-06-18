<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/psock_snd.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/net/psock_snd.c

## Purpose

`psock_snd.c` is a packet-socket send regression test. It hand-builds Ethernet, optional VLAN, IPv4, UDP, and optional virtio-net headers, sends them through AF_PACKET raw or datagram sockets, and verifies both packet-socket sniffing and UDP receive behavior.

## Important APIs, Types, and Functions

Global options are parsed into flags for bind mode, checksum offload, deliberately bad checksum offset, datagram mode, GSO, qdisc bypass, VLAN, virtio-net header, interface name, MTU, payload length, truncation length, and UDP port. Core helpers are `add_csum_hword`, `build_ip_csum`, `build_vnet_header`, `build_eth_header`, `build_ipv4_header`, `build_udp_header`, `build_packet`, `do_bind`, `do_send`, `do_tx`, `setup_rx`, `setup_sniffer`, `do_rx`, `parse_opts`, and `run_test`. It uses `PACKET_QDISC_BYPASS`, `PACKET_VNET_HDR`, `SO_RCVTIMEO`, and `psock_lib.h` filtering.

## Control Flow

Main parses options, configures loopback MTU, adds `172.17.0.1/24` to loopback, enables `accept_local`, then runs the test. `run_test` creates an INET UDP receiver and an AF_PACKET sniffer, sends the crafted packet through `do_tx`, optionally checks the sniffer frame when payload length and VLAN conditions match the shared BPF filter, and always verifies the UDP receiver got exactly the configured payload bytes. Error paths use `error(1, ...)` and therefore produce a failing process exit.

## State and Persistence Behavior

The program mutates the current network namespace by setting loopback MTU, adding an address, and enabling `net.ipv4.conf.lo.accept_local`. It creates only transient sockets and stack/static packet buffers. When invoked via `in_netns.sh`, those namespace mutations are disposable.

## Dependencies, Integration Points, Risks, and Test Signals

Dependencies include AF_PACKET send support, packet datagram/raw modes, loopback address configuration privileges, virtio-net header support for offload tests, UDP GSO/checksum behavior, and the companion shell driver for negative cases. Integration points are packet socket transmit validation, qdisc bypass, VLAN length accounting, checksum offload bounds, GSO maximums, and UDP delivery into the IP stack. Risks are persistent loopback mutation if not run in a namespace, exact MTU/GSO boundary expectations, hard-coded IPv4 addresses, and the intentionally bad checksum-offset mode needing to fail. Signals are matching `tx:` and `rx:` lengths, successful sniffer validation when enabled, and final `OK`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/psock_snd.c -->
