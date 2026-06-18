# Research: sources/distributed-fs/ceph-client/net/llc/llc_output.c

## sources/distributed-fs/ceph-client/net/llc/llc_output.c

Purpose: Provides the minimal LLC output path for MAC header construction and connectionless UI transmission.

Important APIs/types/functions: Exports `llc_mac_hdr_init()` and `llc_build_and_send_ui_pkt()`. The MAC helper supports Ethernet and loopback devices through `dev_hard_header()`. The UI helper initializes LLC U-PDU headers and queues the frame with `dev_queue_xmit()`.

Control flow: `llc_build_and_send_ui_pkt()` writes DSAP/SSAP/command fields via `llc_pdu_header_init()`, converts the frame to a UI command, calls `llc_mac_hdr_init()`, and either transmits or frees the skb on header failure.

State and persistence behavior: No persistent state is kept. The functions mutate the outgoing skb in place and consume it by successful queueing or freeing on error.

Dependencies and integration points: Used by datagram/connectionless upper layers and SAP action helpers. Relies on netdevice hardware header support, PDU initializer macros, and the device address in `skb->dev`.

Risks and test signals: Unsupported device types return `-EINVAL`; callers must not reuse consumed skbs. Tests should cover Ethernet, loopback, unsupported ARP types, invalid destination SAP/MAC combinations, and ensuring UI frames carry the expected DSAP/SSAP/control bytes before transmit.
