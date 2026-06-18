# Research: sources/distributed-fs/ceph-client/net/llc/llc_input.c

## sources/distributed-fs/ceph-client/net/llc/llc_input.c

Purpose: Implements the minimal 802.2 receive path and dispatches validated LLC frames to station, SAP, or connection handlers.

Important APIs/types/functions: Exports `llc_add_pack()`, `llc_remove_pack()`, and `llc_set_station_handler()`. Internal helpers include `llc_pdu_type()` for destination classification and `llc_fixup_skb()` for header length validation, pulling, transport-header setup, and length trimming.

Control flow: `llc_rcv()` drops promiscuous other-host traffic, ensures a private skb, validates/pulls the LLC header, dispatches NULL DSAP frames to the station handler, looks up the destination SAP, classifies U/I/S PDUs, and either calls an upper-layer SAP callback, clones to that callback plus LLC handler, or drops. Handler tables are indexed by `LLC_DEST_SAP` and `LLC_DEST_CONN`.

State and persistence behavior: Handler pointers are static global state. Publication uses memory barriers and `synchronize_net()` on removal to protect lockless receive-side reads. The receive function mutates skb data/headers and may clone when both protocol callback and LLC state-machine handler are present.

Dependencies and integration points: Registered from `llc_core.c` as the packet handler. Uses SAP lookup from `llc_core.c`, PDU macros from `llc_pdu.h`, station handler from `llc_station.c`, SAP handler from `llc_sap.c`, and connection handler from `llc_conn.c`.

Risks and test signals: Header length handling is security-sensitive: malformed short 802.2 frames, bogus length fields, and non-Ethernet mac lengths should be dropped. Handler installation/removal races, invalid U-PDU commands, and clone failure should be tested. Functional signals include UI delivery to datagram sockets, SABME/DISC delivery to connection sockets, and NULL DSAP XID/TEST station responses.
