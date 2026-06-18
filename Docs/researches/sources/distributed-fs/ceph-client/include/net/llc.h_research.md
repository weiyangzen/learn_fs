# Research: sources/distributed-fs/ceph-client/include/net/llc.h

Purpose: `llc.h` is the main internal header for the IEEE 802.2 LLC core. It defines LLC addressing, SAP state, SAP socket hash tables, packet dispatch hooks, SAP lifetime helpers, station initialization, and optional proc/sysctl integration.

Important APIs/types/functions: `struct llc_addr` stores an LSAP and MAC address. `struct llc_sap` stores SAP state, P/F bits, refcount, receive callback, local address, global SAP-list node, socket hash tables keyed by device or local address, lock, socket count, and RCU cleanup node. Hash helpers are `llc_sk_dev_hash()`, `llc_sk_laddr_hashfn()`, and `llc_sk_laddr_hash()`. Core entry points include `llc_rcv()`, `llc_mac_hdr_init()`, `llc_add_pack()`, `llc_remove_pack()`, `llc_set_station_handler()`, `llc_sap_open()`, `llc_sap_find()`, `llc_build_and_send_ui_pkt()`, `llc_sap_handler()`, `llc_conn_handler()`, `llc_station_init()`, and `llc_station_exit()`.

Control flow: Ethernet packet reception enters `llc_rcv()`, which classifies the PDU destination as SAP, connection, or station handling. SAPs are registered in the global `llc_sap_list`; callers open a SAP with a receive callback, bind sockets into per-SAP hash tables, and route Type 1 traffic through SAP handlers or Type 2 traffic through connection handlers. SAP refcounts are acquired with `llc_sap_hold()` / `hold_safe()` and released with `llc_sap_put()`.

State and persistence behavior: SAP state persists for the SAP lifetime and is protected by spinlocks, RCU, and refcounts. Socket lookup state is held in device and local-address hash tables. Optional sysctl variables persist runtime LLC2 timer settings for ack, busy, P, and reject timers. There is no disk persistence.

Dependencies and integration points: it depends on Ethernet address sizes, packet types, skb/net_device types, list/hlist/nulls lists, hash/jhash helpers, refcounting, RCU, procfs, sysctl, and the UAPI LLC option header. It integrates with AF_LLC sockets, LLC station code, the Ethernet receive path, `/proc` diagnostics, and LLC2 connection machinery.

Risks: risks include SAP refcount/RCU lifetime errors, socket hash corruption under concurrent bind/unbind, incorrect LSAP masking, stale device-index hash entries, and sysctl timer values that destabilize connection retransmission. Packet dispatch bugs can send Type 1 UI/XID/TEST traffic to connection logic or vice versa.

Test signals: useful tests include SAP open/find/close refcounting, concurrent socket bind/unbind under RCU lookup, UI packet send/receive, station handler registration, LLC proc/sysctl initialization with config on/off, packet fuzzing over DSAP/SSAP/control fields, and lockdep/KASAN during SAP teardown.
