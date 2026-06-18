<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/um/drivers/vector_transports.c -->
# sources/distributed-fs/ceph-client/arch/um/drivers/vector_transports.c

Purpose: builds transport-specific header, verification, and offload behavior for UML vector network devices. It supports GRE, L2TPv3, raw, tap, tap/raw hybrid, and BESS transport modes.

Important APIs/types/functions: transport state structs are `gre_minimal_header`, `uml_gre_data`, and `uml_l2tpv3_data`. Header callbacks are `l2tpv3_form_header()`, `gre_form_header()`, `raw_form_header()`, `l2tpv3_verify_header()`, `gre_verify_header()`, and `raw_verify_header()`. Builders are `build_gre_transport_data()`, `build_l2tpv3_transport_data()`, `build_raw_transport_data()`, `build_hybrid_transport_data()`, `build_tap_transport_data()`, `build_bess_transport_data()`, and dispatcher `build_transport_data()`.

Control flow: vector open calls `build_transport_data()` after host FDs are opened. GRE/L2TP builders parse required and optional args, allocate transport data, set header sizes, offsets, expected keys/cookies/session IDs/counters, and assign form/verify callbacks. Raw/tap/hybrid builders try to enable virtio-net vnet headers on host FDs and, if successful, enable checksum/GSO/GRO/TSO netdev features and use virtio-net header conversion callbacks. BESS uses no extra headers.

State and persistence: per-device transport state is allocated into `vp->transport_data`; sequence/counter values advance during TX. No persistent state is stored.

Dependencies and integration points: depends on vector parsed-arg helpers, Linux Ethernet/skbuff/netdev feature APIs, GRE/L2TP constants from `vector_user.h`, virtio-net header conversion, and host FD capability helpers such as `uml_raw_enable_vnet_headers()` and `uml_tap_enable_vnet_headers()`.

Risks: encapsulation verification must account for IPv4 raw headers versus IPv6/UDP layouts. Required GRE key and L2TP session/cookie pairs must be supplied consistently; otherwise open fails. Raw vnet-header support changes advertised offloads and buffer sizing. Header offset arithmetic is security-sensitive because malformed packets are parsed from host input.

Test signals: GRE with/without keys and sequence, L2TPv3 with UDP/IP, cookies/counters, IPv4/IPv6 variants, raw/tap vnet-header negotiation, GRO/TSO checksum behavior, bad key/cookie/session packet drops, BESS no-header path, and feature toggling via ethtool.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/um/drivers/vector_transports.c -->
