# sources/distributed-fs/lustre-release/include/uapi/linux/lnet/lnet-idl.h

Purpose: wire-format IDL for core LNet messages, NIDs, handles, protocol magic/version values, counters, NI status, metadata, and ping information.

Important APIs/types: `lnet_nid_t` is the legacy 64-bit NID. `struct lnet_nid` is the extended packed NID supporting up to 128-bit address and ANY wildcard. `lnet_process_id_packed`, `lnet_handle_wire`, message type enum, command structs (`lnet_ack`, `lnet_put`, `lnet_get`, `lnet_reply`, `lnet_hello`), `lnet_hdr`, and nid4 wrapper types define wire headers. Protocol magic constants cover IB, GNI, TCP, KFI, acceptor, ping, EFA, and placeholder unified protocol. Acceptor v1/v2 structs support legacy and large NIDs. Counter/status structs support LNet stats and ping replies. Ping feature bits advertise NI status, routing, multi-rail, discovery, large address, primary-large, and metadata support.

Control flow: LNDs exchange HELLO/acceptor messages, convert between network buffers and host-order `lnet_hdr`, and use ping info to discover peer NIs/features. `lnet_ping_info_size()` computes variable ping size based on large-address feature.

State and persistence: wire structs are transient network data, but ABI/wire layout is persistent protocol contract.

Dependencies/integration: included by UAPI type headers and internal conversion helpers in `lib-lnet.h`. Packed/fixed-width layout is central to interoperability.

Risks and test signals: changing field order, packing, endian expectations, or feature bits breaks wire compatibility. Large-NID size math and `pi_ni[0].ns_msg_size` validation are sensitive. Test signals are wire constant assertions, endian conversion tests, legacy nid4 interoperability, acceptor v1/v2 negotiation, ping feature validation, and malformed large-address ping buffers.
