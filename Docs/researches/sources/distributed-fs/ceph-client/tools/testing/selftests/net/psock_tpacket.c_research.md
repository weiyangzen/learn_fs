<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/psock_tpacket.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/net/psock_tpacket.c

## Purpose

`psock_tpacket.c` validates AF_PACKET memory-mapped ring behavior for `TPACKET_V1`, `TPACKET_V2`, and `TPACKET_V3`. It covers RX rings for all versions and TX rings for all versions, checking packet payload layout, ring ownership bits, block sequence numbers, block length accounting, and send/receive datapaths.

## Important APIs, Types, and Functions

Important types are `struct ring`, `struct block_desc`, and `union frame_map`. Key helpers include `pfsocket`, `create_payload`, `test_payload`, V1/V2 RX ownership helpers, TX ownership helpers, `walk_v1_v2_rx`, `walk_tx`, V3 block helpers (`__v3_test_block_seq_num`, `__v3_test_block_len`, `__v3_walk_block`, `__v3_flush_block`, `walk_v3_rx`), ring setup helpers (`__v1_v2_fill`, `__v3_fill`, `setup_ring`, `mmap_ring`, `bind_ring`, `unmap_ring`), `test_kernel_bit_width`, `test_user_bit_width`, and `test_tpacket`. It uses `PACKET_VERSION`, `PACKET_RX_RING`, `PACKET_TX_RING`, `PACKET_LOSS`, `mmap`, `poll`, and `psock_lib.h`.

## Control Flow

Main calls `test_tpacket` for V1 RX/TX, V2 RX/TX, and V3 RX/TX. Each test opens a packet socket at the requested version, sets up a large ring, maps it, binds to loopback with the shared BPF filter, walks the ring-specific datapath, unmaps, and closes. RX paths generate UDP traffic with `pair_udp_send` and consume packets until the expected loopback count is reached. TX paths fill mapped frames with synthetic Ethernet/IP packets, mark frames ready, kick transmission with `sendto`, and receive them through a filtered packet socket.

## State and Persistence Behavior

State is transient: packet sockets, mapped packet rings, UDP socket pairs, counters `total_packets`/`total_bytes`, and V3 block sequence tracking. No persistent system configuration is changed. V1 tests are skipped when user-space and kernel pointer widths differ because the V1 header ABI is width-sensitive.

## Dependencies, Integration Points, Risks, and Test Signals

Dependencies include AF_PACKET ring support, loopback, `/proc/kallsyms` readability for bit-width detection, mapped memory availability, classic BPF filters, and raw socket privileges. Integration points are the TPACKET UAPI, ring ownership synchronization, block retirement, TX ring packet layout, and loopback packet observation. Risks are timing around `poll`, hard-coded packet counts, architecture width mismatch, and memory-lock/mmap constraints. Signals are correct packet counts, payload `ETH_P_IP` validation, V3 block sequence/length checks, per-test status output, and final `OK. All tests passed`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/psock_tpacket.c -->
