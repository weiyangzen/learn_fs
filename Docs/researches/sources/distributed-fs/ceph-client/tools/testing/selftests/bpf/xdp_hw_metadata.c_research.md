# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/xdp_hw_metadata.c

## Purpose

`xdp_hw_metadata.c` is a functional hardware test for XDP RX metadata and AF_XDP TX metadata. It diverts UDP port 9091 packets into AF_XDP sockets, verifies RX timestamp/RSS/VLAN metadata, optionally sends a TX reply with checksum, timestamp, and launch-time metadata requests, and checks SKB timestamp delivery on a UDP socket.

## Important APIs, Types, and Functions

Important state includes `struct xsk`, global `bpf_obj`, `bind_flags`, `rx_xsk`, `ifname`, `ifindex`, `rxq`, `skip_tx`, timestamp tracking, and launch-time queue settings. Key functions are `open_xsk`, `close_xsk`, `refill_rx`, `kick_tx`, `kick_rx`, `gettime`, `print_tstamp_delta`, `print_vlan_tci`, `verify_xdp_metadata`, `verify_skb_metadata`, `complete_tx`, `ping_pong`, `verify_metadata`, `rxq_num`, `hwtstamp_ioctl`, `hwtstamp_enable`, `cleanup`, `timestamping_enable`, `read_args`, `clean_existing_configurations`, and `main`.

## Control Flow

`main` parses options, counts RX queues, removes existing qdisc/filter state, enables hardware timestamping, optionally configures mqprio/ETF and VLAN steering for launch time, creates one AF_XDP socket per RX queue, opens and loads the dev-bound XDP skeleton, starts a UDP SKB endpoint on port 9092, populates the XSK map, attaches the XDP program, and enters `verify_metadata`. The verification loop polls all XSK fds and the SKB server, kicks RX, validates metadata from the first packet segment, optionally mirrors the packet back through AF_XDP TX, waits for TX completion metadata, releases descriptors, and refills RX buffers.

## State and Persistence Behavior

The program mutates external NIC state: XDP attachment, hardware timestamp config, tc qdisc/filter state, ethtool filters, VLAN offload, and AF_XDP socket mappings. `atexit` restores the saved hwtstamp config, while explicit cleanup detaches XDP, closes sockets, destroys the skeleton, and removes qdisc/filter state at the end.

## Dependencies and Integration Points

It depends on real NIC hardware support for XDP driver mode, AF_XDP, metadata kfuncs exposed by the companion skeleton, hardware timestamping, ethtool channels/filters, tc mqprio/ETF/flower, UDP test traffic, and the shared metadata layout in `xdp_metadata.h`.

## Risks and Test Signals

Risks include privileged host configuration changes, stale qdisc/filter state, hardware-specific metadata availability, multi-buffer descriptor handling, timeout sensitivity, and incomplete cleanup after fatal `error()`. Signals are printed RX hash/timestamp/VLAN metadata, SKB hardware timestamps, successful TX completion timestamps, checksum request behavior, packet counters in BPF BSS, and clean XDP detach/restoration.
