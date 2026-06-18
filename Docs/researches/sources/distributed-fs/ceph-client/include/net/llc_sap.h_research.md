# Research: sources/distributed-fs/ceph-client/include/net/llc_sap.h

Purpose: `llc_sap.h` declares SAP-level utility functions for returning PDUs, saving primitives on sockets, allocating LLC frames, and building/sending TEST and XID packets.

Important APIs/types/functions: declarations are `llc_sap_rtn_pdu()`, `llc_save_primitive()`, `llc_alloc_frame()`, `llc_build_and_send_test_pkt()`, and `llc_build_and_send_xid_pkt()`. The header forward-declares SAP, device, skb, and socket types and includes basic integer types.

Control flow: SAP action implementations use these helpers to allocate an outbound frame, preserve primitive metadata on a socket/skb, send XID or TEST responses/commands, or return a PDU to its originator. It sits beneath the state-machine action layer and above PDU encoding helpers.

State and persistence behavior: the header owns no state. Implementations may allocate skbs, mutate skb control buffers, and enqueue or transmit packets. Primitive values saved on sockets/skbs persist until consumed by upper-layer reporting.

Dependencies and integration points: it integrates with SAP actions, `llc_pdu.h` Type 1 PDU builders, Ethernet device output, AF_LLC socket state, and skb allocation/transmit paths.

Risks: frame allocation must reserve correct headroom and use the right device. Primitive saving shares skb/socket metadata with event processing. TEST/XID send helpers must use correct destination MAC and DSAP from the triggering packet or request.

Test signals: allocation failure injection, TEST payload echo, XID command/response contents, primitive delivery to sockets, PDU return behavior, and device-down transmit error handling.
