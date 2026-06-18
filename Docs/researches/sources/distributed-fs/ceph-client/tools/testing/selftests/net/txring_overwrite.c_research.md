# sources/distributed-fs/ceph-client/tools/testing/selftests/net/txring_overwrite.c

Purpose: Regression test for AF_PACKET `PACKET_TX_RING` to ensure consecutive sends from the same TX ring slot are mirrored with original content intact and not overwritten before loopback receive.

Important APIs/functions: uses raw packet sockets, `PACKET_TX_RING`, `mmap`, `struct tpacket_req`, `struct tpacket_hdr`, `TP_STATUS_AVAILABLE`, `TP_STATUS_SEND_REQUEST`, `if_nametoindex("lo")`, and `sendto()` as the TX kick. `build_packet()` creates a loopback IPv4/UDP Ethernet frame with a caller-selected payload byte. `read_verify_pkt()` reads 100 bytes from RX and checks byte 60 for the pattern.

Control flow: `main()` opens a raw RX packet socket for `ETH_P_IP`, configures one TX ring frame on a raw packet socket bound to loopback, sends two packets with payload patterns `a` and `b` through the same ring slot, then reads and verifies the two mirrored packets in order.

State and persistence: state is one mmap'd packet ring slot and two sockets. The test does not unmap explicitly but exits after closing sockets. No persistent files are touched.

Dependencies and integration: requires CAP_NET_RAW/CAP_NET_ADMIN enough to create AF_PACKET raw sockets, loopback interface, and packet mmap support. It is a standalone compiled selftest with process exit status as the signal.

Risks: assumes loopback delivery ordering and fixed offset `buf[60]` into the constructed frame. It builds deliberately minimal IP/UDP headers with zero checksums, acceptable for the loopback/raw packet path tested but not a generic packet generator.

Test signals: success prints `read: a` and `read: b` and exits 0. A wrong byte reports the mismatched pattern and exits nonzero; socket/ring setup failures abort through `error(1, ...)`.
