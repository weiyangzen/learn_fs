# sources/distributed-fs/ceph-client/include/trace/events/net_probe_common.h

Purpose: Provides shared macros used by networking trace headers to snapshot socket tuple fields. It centralizes IPv4/IPv6 address, port, and family extraction for socket-oriented tracepoints.

Important APIs/types/functions: `TP_STORE_ADDR_PORTS`, `TP_STORE_ADDRS_PORTS`, `TP_STORE_ADDR_PORTS_SKB`, and related address-copy helper macros select IPv4 or IPv6 fields and copy source/destination addresses plus ports into trace entries. The header is macro-only and is intended for inclusion inside trace event definitions.

Control flow: A tracepoint fast-assign block invokes these macros with a socket or skb. The macro branches on address family, pulls tuple data from inet/IPv6 socket state or packet headers, and stores normalized fields into the trace entry before `TP_printk`.

State and persistence: No state is owned. It only copies transient socket or skb address fields into a trace record.

Dependencies and integration points: Included by MPTCP and other net probe trace headers that need common tuple formatting. It depends on the including file to provide appropriate structs and trace entry fields.

Risks and test signals: Risks include field-name contract mismatches between macro and trace entry, IPv6-disabled build coverage, byte-order mistakes, and skb header availability assumptions. Test IPv4/IPv6 sockets, mapped addresses, unconnected sockets, skb-based probes, and compile matrices with IPv6 enabled and disabled.

Source-read signal: read `sources/distributed-fs/ceph-client/include/trace/events/net_probe_common.h` completely for this pass (115 lines, 3338 bytes). Final split target: `Docs/researches/sources/distributed-fs/ceph-client/include/trace/events/net_probe_common.h_research.md`.
