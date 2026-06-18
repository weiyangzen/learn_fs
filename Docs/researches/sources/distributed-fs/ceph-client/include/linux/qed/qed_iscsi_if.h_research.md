# sources/distributed-fs/ceph-client/include/linux/qed/qed_iscsi_if.h

Purpose: declares the public QED iSCSI offload client interface for device discovery, firmware start/stop, connection acquire/offload/update/destroy, SQ clearing, MAC change, async events, LL2 access, and stats collection.

Important APIs/types/functions: `iscsi_event_cb_t` is the async event callback signature. `qed_iscsi_stats` exposes RX/TX packet, byte, R2T/data PDU, threshold, retransmit, and dropped-task counters. `qed_dev_iscsi_info` reports common info, BDQ request queue addresses, and CQ count. `qed_iscsi_id_params` describes MAC/IP/port endpoints. `qed_iscsi_params_offload` carries layer code, SQ PBL, initial TCP ACK, source/destination endpoints, VLAN, TCP/IP state variables, timers, window scaling, MSS, TTL/TOS, and retransmit/keepalive state. `qed_iscsi_params_update` carries negotiated digest and iSCSI sequence/PDU sizing flags. `qed_iscsi_tid` describes task memory blocks. `qed_iscsi_ops` exposes the lifecycle and connection operations; `qed_get_iscsi_ops()`/`qed_put_iscsi_ops()` manage ops access.

Control flow: a client starts iSCSI with task blocks plus async event context/callback, acquires a connection handle and firmware CID/doorbell, offloads TCP+iSCSI state, updates negotiated iSCSI parameters after login, posts SQ work through firmware-defined rings, handles async connection events, clears SQ or changes MAC when needed, destroys the connection, releases it, reads stats, and stops iSCSI.

State and persistence: active connection state is split between client-owned connection objects, firmware contexts, doorbell addresses, task blocks, and TCP/iSCSI sequence variables. Update flags persist in firmware until another update or teardown. Statistics are runtime counters. No session state is durable across reset without upper-layer recovery.

Dependencies and integration points: includes `qed_if.h` and exposes an LL2 ops pointer for supporting packet paths. It is backed by `iscsi_common.h` ramrods and integrates with Linux iSCSI offload transport, TCP offload state, LL2 out-of-order handling, and management firmware telemetry.

Risks: offload requires a coherent snapshot of TCP sequence/window/timer state; stale or partially initialized fields can break the connection. Digest and InitialR2T/ImmediateData update flags must match negotiated login settings. Async event callback lifetime must exceed firmware event delivery. `destroy_conn` and `clear_sq` ordering can race with completions.

Test signals: login/offload/update, reads/writes with and without header/data digest, immediate data/R2T negotiation, async abort/close/timeout events, SQ clear, MAC change, connection teardown with abort flag, stats reads, recovery during active I/O, and invalid endpoint/IP-version inputs.
