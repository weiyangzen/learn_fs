# sources/distributed-fs/ceph-client/include/linux/qed/qed_ll2_if.h

Purpose: declares QED's Light L2 interface, a low-level packet path used by storage and RDMA clients for control, out-of-order, test, FCoE, TCP ULP, RoCE, and iWARP traffic outside the main Ethernet netdev queues.

Important APIs/types/functions: enums classify LL2 connection type, RX connection type, RoCE flavor, TX destination, and error handling. `qed_ll2_stats` reports invalid GSI headers, packet length/type/checksum errors, drops, and RX/TX byte/packet counters. Callback data and types include `qed_ll2_comp_rx_data`, RX/TX complete and release callbacks, slowpath callback, and `qed_ll2_cbs`. Connection setup uses `qed_ll2_acquire_data_inputs` and `qed_ll2_acquire_data`; TX uses `qed_ll2_tx_pkt_info`. Simpler netdev-style ops use `qed_ll2_cb_ops` and `qed_ll2_params`. `qed_ll2_ops` exposes `start`, `stop`, `start_xmit`, `register_cb_ops`, and `get_stats`. `qed_ll2_alloc_if`/`qed_ll2_dealloc_if` are real only under `CONFIG_QED_LL2`, otherwise stubs.

Control flow: a client registers packet callbacks, starts LL2 with MTU/drop/VLAN/MAC parameters, optionally acquires lower-level LL2 connections with descriptors and callbacks, posts RX buffers, prepares TX packets and fragments, receives completion/release callbacks, handles slowpath notifications, and stops/deallocates the interface. TX destination can send to network, loopback, or drop.

State and persistence: LL2 connection handles, descriptor rings, RX buffers, TX fragments, callbacks, and stats are runtime state owned by QED core and clients. Buffer cookies and DMA addresses must remain valid until release/completion callbacks return ownership.

Dependencies and integration points: includes Linux netdevice/skbuff/PCI/interrupt headers and `qed_if.h`. It integrates with FCoE FIP/control traffic, iSCSI out-of-order/TCP ULP traffic, RoCE/iWARP RDMA CM/control packets, and optional GSI handling.

Risks: callback lifetime and buffer ownership are central risks. Misconfigured MTU, descriptor counts, `tx_max_bds_per_packet`, or error handling can drop control traffic. Non-LL2 builds expose null ops except allocation stubs, so callers must respect config availability. Fragment mapping and `frags_mapped` semantics must match DMA ownership.

Test signals: build with and without `CONFIG_QED_LL2`, start/stop LL2, send SKBs with FIP discovery flag, acquire/establish/terminate/release low-level connections via RDMA ops, post RX buffers, verify RX/TX complete and release callbacks, exercise network/loopback/drop destinations, inject packet-too-big/no-buffer errors, and validate LL2 stats.
