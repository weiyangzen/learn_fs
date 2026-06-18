# sources/distributed-fs/ceph-client/drivers/infiniband/hw/irdma/cm.h

Purpose: public/internal declarations for the irdma iWARP connection manager. It defines MPA protocol constants, TCP option constants, CM node/listener/event states, timer and address structures, node/listener/core state containers, and prototypes used by other irdma modules.

Important APIs/types: protocol types include `struct ietf_mpa_v1`, `struct ietf_mpa_v2`, `struct ietf_rtr_msg`, TCP option structs, and `union all_known_options`. State enums include `irdma_cm_node_state`, `mpa_frame_ver`, `send_rdma0`, `irdma_tcpip_pkt_type`, `irdma_cm_listener_state`, and `irdma_cm_event_type`. Core runtime types are `irdma_timer_entry`, `irdma_cm_tcp_context`, `irdma_apbvt_entry`, `irdma_cm_listener`, `irdma_cm_node`, `irdma_cm_info`, `irdma_cm_event`, and `irdma_cm_core`.

Control flow: `cm.c` and neighboring modules use this header to schedule retransmit/close timers, create/listen/connect/accept/reject/destroy iw_cm sessions, process interface notifications, perform ARP table lookups, send ACKs, manage CM node references, and add established qhashes. `irdma_cm_core` function pointers select generation-specific frame formation and AH handling during CM setup.

State and persistence: the header lays out all in-memory CM state: listener lists, CM hash tables, APBVT hash table, TCP timer, event workqueue, stats counters, node TCP/MPA metadata, private-data buffers, AH/qhash/APBVT ownership flags, and refcounts. These persist while the device and individual CM sessions/listeners exist.

Dependencies and integration: relies on RDMA iw_cm IDs, irdma device/QP/PUDA/AH types from surrounding headers, Linux networking address types, workqueues, timers, hashtables, RCU, refcounts, and VLAN/Ethernet constants.

Risks: structure layout is shared across multiple files, so field ownership and locking rules must remain clear. Several constants encode wire limits such as 512-byte private data and MPA header sizes. `DECLARE_HASHTABLE(..., 8)` gives 256 buckets despite `IRDMA_CM_HASHTABLE_SIZE` being 1024, so readers should not assume that macro controls the declared tables. Function prototypes include `irdma_cm_start()`/`irdma_cm_stop()` even though this file's visible implementation uses setup/cleanup names, implying definitions or legacy declarations elsewhere must be checked during refactors.

Test signals: compile coverage from all irdma objects, state transition coverage for every enum value used in `cm.c`, hash/list teardown under RCU, timer entry lifecycle, and ABI checks for MPA frame sizes/private data limits.
