# sources/distributed-fs/ceph-client/include/linux/netfilter/nf_conntrack_tcp.h

Purpose: Defines TCP conntrack per-direction window tracking and aggregate TCP connection state.

Important APIs, types, and functions: Important types are `struct ip_ct_tcp_state` for td_end/td_maxend/window/scale/flags and `struct ip_ct_tcp` for two directions, retransmission counters, last packet metadata, and last window. Detected source surface: 33 lines; includes `uapi/linux/netfilter/nf_conntrack_tcp.h`; macros `_NF_CONNTRACK_TCP_H`; structs `ip_ct_tcp`, `ip_ct_tcp_state`; enums none; typedefs none; function-like declarations/helpers none.

Control flow: The TCP conntrack implementation feeds parsed TCP headers into this state to validate sequence windows, infer connection state, detect retransmits, and apply liberal/strict tracking policy.

State and persistence behavior: State is per conntrack entry and persists across packets until timeout or destruction. It mirrors the TCP stream from a firewall perspective rather than owning socket state.

Dependencies and integration points: Pulls UAPI TCP conntrack enums and is consumed by net/netfilter TCP protocol tracking code.

Risks and test signals: Risks are sequence arithmetic overflow, incorrect window scaling, false invalid drops, and stale retransmission counters. Test handshake, FIN/RST, retransmits, out-of-window packets, and asymmetric routing.
