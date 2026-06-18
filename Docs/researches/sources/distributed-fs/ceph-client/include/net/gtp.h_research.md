# sources/distributed-fs/ceph-client/include/net/gtp.h

Purpose: defines GPRS Tunneling Protocol constants and wire headers for GTPv0, GTPv1-U, extension headers, and PDU session metadata.

Important APIs/types: port constants are `GTP0_PORT` 3386 and `GTP1U_PORT` 2152. Message constants include echo request/response and TPDU. `gtp0_header`, `gtp1_header`, and `gtp1_header_long` are packed protocol headers. `gtp_ie`, `gtp0_packet`, and `gtp1u_packet` represent recovery information-element packets. `gtp_pdu_session_info` stores 5G PDU type and QFI. `netif_is_gtp()` detects rtnetlink devices with kind `"gtp"`. Extension-header flags and `gtp_ext_hdr` describe optional GTP1 fields.

Control flow and state: this header is layout-only. Runtime tunnel/session state lives in GTP netdevices, PDP/session tables, UDP sockets, and rtnetlink configuration.

Dependencies and integration: depends on netdevice, types, and rtnetlink. It integrates with mobile-core tunnel devices, UDP encapsulation, packet parsing, and traffic classification/offload matching.

Risks: packed headers require careful unaligned access and length validation. GTPv1 optional flags control presence of sequence, N-PDU, and extension headers. Tests should cover v0/v1 header parsing, extension-header chains, device-kind detection, PDU session info extraction, malformed/truncated packets, and endian correctness of TEID/length fields.
