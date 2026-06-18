# Research: sources/distributed-fs/ceph-client/net/llc/llc_core.c

## sources/distributed-fs/ceph-client/net/llc/llc_core.c

Purpose: Provides minimal LLC core registration and SAP lifetime management. It owns the global SAP list and registers the 802.2 packet handler with the network stack.

Important APIs/types/functions: Defines and exports `LIST_HEAD(llc_sap_list)`, `llc_sap_find()`, `llc_sap_open()`, and `llc_sap_close()`. Internal helpers allocate SAPs, initialize `sk_lock`, local-address nulls hash buckets, state, refcount, and look up by LSAP under `llc_sap_list_lock` or RCU.

Control flow: Module init registers a `packet_type` for `ETH_P_802_2` with `.func = llc_rcv`; exit removes it. Upper layers call `llc_sap_open()` to reserve a unique LSAP and attach an optional receive callback. `llc_sap_find()` is used on packet receive to take a safe reference. `llc_sap_close()` removes the SAP from the RCU list and frees it after grace period, warning if sockets remain attached.

State and persistence behavior: The persistent state is process-global: `llc_sap_list`, each `struct llc_sap`'s LSAP, receive callback, socket hashes, `sk_count`, and refcount. SAP entries are RCU-visible and require balanced holds/puts by users.

Dependencies and integration points: Depends on Linux module, packet socket dispatch, RCU list management, netdevice Ethernet protocol IDs, and `llc_rcv()` from `llc_input.c`. It is the shared registry used by both connection and datagram LLC paths.

Risks and test signals: Duplicate LSAP opens must fail, close with live sockets is dangerous, and callback publication must be compatible with RCU readers. Useful signals include module load/unload, SAP open/find/close races, repeated LSAP bind attempts, and receive delivery after close under RCU stress.
