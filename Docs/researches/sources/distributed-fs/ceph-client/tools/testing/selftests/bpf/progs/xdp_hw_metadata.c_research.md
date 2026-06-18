<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/xdp_hw_metadata.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/xdp_hw_metadata.c

## Purpose
This XDP fragments program collects hardware/software RX metadata for UDP port 9091 packets, stores it in XDP metadata space, and redirects matching packets to AF_XDP.

## Important APIs, Types, and Functions
It declares an `XSKMAP` named `xsk`, BSS counters `pkts_skip`, `pkts_fail`, and `pkts_redir`, and kfuncs `bpf_xdp_metadata_rx_timestamp`, `bpf_xdp_metadata_rx_hash`, and `bpf_xdp_metadata_rx_vlan_tag`. It uses `struct xdp_meta` and field flags from `xdp_metadata.h`.

## Control Flow
The `rx` program parses Ethernet with up to two VLAN tags, then IPv4/IPv6 UDP. Non-UDP or non-9091 packets increment skip and pass. Matching packets reserve metadata with `bpf_xdp_adjust_meta`, validate the metadata area, initialize `hint_valid`, write a TAI timestamp, attempt each metadata kfunc, set error fields or validity bits, increment redirect counter, and redirect to `xsk[rx_queue_index]`.

## State and Persistence
Persistent BSS counters track skipped, failed, and redirected packets. The XSK map persists AF_XDP socket bindings. Packet metadata is written before packet data and consumed by userspace.

## Dependencies and Integration Points
It integrates with AF_XDP hardware metadata selftests and driver support for XDP metadata kfuncs. It depends on `vmlinux.h`, `xdp_metadata.h`, endian helpers, and XDP frags support.

## Risks
Metadata kfuncs can fail depending on driver support; the code records errors but still redirects matching packets when metadata reservation succeeds. VLAN parsing is bounded but simple. Incorrect metadata size validation would corrupt packet data, but the code checks `meta + 1 > data`.

## Test Signals
Counters distinguish skip/fail/redirect paths, and userspace can inspect `struct xdp_meta` for timestamp/hash/VLAN validity bits and error codes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/xdp_hw_metadata.c -->
