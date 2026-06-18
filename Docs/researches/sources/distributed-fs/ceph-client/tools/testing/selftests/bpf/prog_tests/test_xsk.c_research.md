# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/test_xsk.c

## Purpose
Implements the AF_XDP selftest traffic engine used by `test_xsk.h` test specifications. It creates UMEMs and XSK sockets, attaches XDP programs, generates deterministic packet streams, runs threaded TX/RX paths, and validates normal, poll, shared-UMEM, metadata, multibuffer, invalid-descriptor, ring-size, teardown, and `bpf_xdp_adjust_tail()` behavior.

## APIs, Types, and Functions
Public helpers include `test_init()`, `ifobject_create()`, `ifobject_delete()`, `init_iface()`, `xsk_configure_umem()`, `xsk_configure_socket()`, `kick_tx()`, `kick_rx()`, packet-stream helpers, worker thread entry points, and many `testapp_*()` cases referenced from the header tables. Core internal helpers manage UMEM allocation, socket busy-poll options, hardware ring sizing, XDP program reattachment, XSK map updates, packet generation, descriptor validation, statistics validation, and socket/UMEM cleanup.

## Control Flow, State, and Persistence
`test_init()` resets the two `ifobject` instances into TX/RX roles and chooses copy, driver, or zero-copy bind flags. `testapp_validate_traffic()` applies MTU/ring prerequisites, attaches the desired XDP programs, then `__testapp_validate_traffic()` starts RX and TX worker threads with a barrier. RX allocates UMEM, populates fill rings, installs sockets into XSK maps, receives descriptors, validates offsets, payload sequence words, metadata, fragments, and packet lengths, and returns buffers to the fill ring. TX reserves descriptors, writes Ethernet headers and payloads into UMEM, kicks TX, drains completions, and enforces an in-flight pacing counter. Persistent state is all in `test_spec`, `ifobject`, `xsk_socket_info`, `xsk_umem_info`, global packet-in-flight counters, and libbpf skeleton state; no on-disk state is persisted.

## Dependencies and Integration
Depends on libbpf AF_XDP APIs, Linux XDP flags/statistics, pthreads, `network_helpers`, `xsk.h`, `xsk_xdp_common.h`, and `xsk_xdp_progs.skel.h`. It integrates with ethtool ring helpers, `/proc` and `/sys` tunables reported by the header, and generated XDP programs that perform forwarding, dropping, metadata population, shared UMEM routing, and tail adjustment.

## Risks and Test Signals
Risks include timing-sensitive TX/RX loops, driver-specific zero-copy and multibuffer support, hugepage availability for unaligned mode, hardware ring resize flakiness, shared UMEM base-address assumptions, and complex invalid descriptor expectations that differ between aligned and unaligned modes. Strong signals are successful packet count/sequence validation, expected XDP statistics (`rx_dropped`, `rx_ring_full`, fill-empty, invalid TX descriptors), clean socket/UMEM teardown, correct skip behavior for unsupported features, and no timeout in threaded send/receive loops.
