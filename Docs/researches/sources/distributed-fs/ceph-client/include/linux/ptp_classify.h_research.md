# sources/distributed-fs/ceph-client/include/linux/ptp_classify.h

Purpose: defines PTP packet classification constants, PTP header layouts, and helpers for recognizing and modifying IEEE 1588 event messages in networking paths.

Important APIs and types: `PTP_CLASS_*` flags classify protocol version and transport: IPv4, IPv6, L2, VLAN, and none. Message constants cover Sync, Delay_Req, Pdelay_Req, and Pdelay_Resp. `struct clock_identity`, `struct port_identity`, and packed `struct ptp_header` model PTPv2 headers. With `CONFIG_NET_PTP_CLASSIFY`, APIs include `ptp_classify_raw()`, `ptp_parse_header()`, `ptp_get_msgtype()`, `ptp_header_update_correction()`, `ptp_msg_is_sync()`, and `ptp_classifier_init()`.

Control flow: network drivers or timestamping code classify an skb, parse the PTP header accounting for VLAN/UDP/IP headers, inspect message type, and for one-step P2P correction update the correction field and UDP checksum. Disabled builds return no classification and no-op helpers.

State and persistence: no persistent state. Classification operates on live skbs and may mutate the PTP correction field and UDP checksum in packet data.

Dependencies and integration points: depends on skb layout, MAC headers, IP/UDP headers, unaligned access, checksum helpers, BPF-based classifier implementation, and hardware timestamping drivers.

Risks and test signals: risks include parsing with uninitialized skb MAC headers, length checks missing encapsulation variants, checksum update errors, PTPv1/v2 message-type differences, and VLAN handling. Test raw classification for IPv4/IPv6/L2/VLAN PTP, malformed/truncated packets, UDP checksum zero/mangled-zero behavior, correction update, and disabled classifier builds.
