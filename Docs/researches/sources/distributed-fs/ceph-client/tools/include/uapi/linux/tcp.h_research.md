<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/include/uapi/linux/tcp.h -->
# sources/distributed-fs/ceph-client/tools/include/uapi/linux/tcp.h

Purpose: this header defines the Linux TCP wire header layout, socket options, diagnostic structs, TCP_INFO telemetry, MD5 signature configuration, and zero-copy receive ABI.

Important APIs/types: `struct tcphdr` uses endian-specific bitfields for data offset and flags. `union tcp_word_hdr`, `tcp_flag_word`, and `TCP_FLAG_*` support flag-word inspection. Socket options range from `TCP_NODELAY`, `MAXSEG`, keepalive, `TCP_INFO`, congestion control, MD5, repair, Fast Open, ULP, zerocopy receive, INQ, and TX delay. `struct tcp_info` exposes state, congestion state, RTT, cwnd, pacing, segment/byte counters, delivery rate, busy/limited time, retransmission, reordering, and receive window. MD5 structs and `struct tcp_zerocopy_receive` define specialized options.

Control flow: applications use `setsockopt`/`getsockopt` with these constants and structs. Packet parsers inspect `tcphdr`. Diagnostics receive netlink attributes such as `TCP_NLA_*` for timestamping stats.

State and persistence: socket options mutate per-socket TCP state; `TCP_INFO` is a snapshot. Repair mode and MD5 keys are high-impact persistent socket state.

Dependencies/integration: depends on Linux types, byte order, and socket storage. Used by networking apps, route daemons, diagnostics, packet filters, and kernel selftests.

Risks and test signals: risks include endian bitfield assumptions, partial `tcp_info` support across kernels, privileged/unsafe repair and MD5 operations, and zerocopy buffer alignment/error reporting. Test get/set option round trips, TCP_INFO length-tolerant reads, TFO/MD5 behavior, and packet flag parsing on both endian configurations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/include/uapi/linux/tcp.h -->
