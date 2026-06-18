# Research: sources/distributed-fs/ceph-client/net/llc/llc_if.c

## sources/distributed-fs/ceph-client/net/llc/llc_if.c

Purpose: Provides upper-layer APIs for connection-oriented LLC operations: send data, initiate a connection, and disconnect.

Important APIs/types/functions: Exports `llc_build_and_send_pkt()`, `llc_establish_connection()`, and `llc_send_disc()`. These functions construct `llc_conn_state_ev` primitives on skbs and enter the connection state machine through `llc_conn_state_process()`.

Control flow: Data send rejects ADM/out-of-data states and active poll cycles, marks failed data requests, stamps `LLC_DATA_PRIM` request metadata, assigns `skb->dev`, and lets the connection table build/transmit the I-PDU. Connection establishment builds local/remote LLC addresses, checks for an existing established socket, allocates a zero-length event skb, and posts a `LLC_CONN_PRIM` request. Disconnect validates stream/established state, sets TCP state to `TCP_CLOSING`, and posts a `LLC_DISC_PRIM` request.

State and persistence behavior: This file mostly creates transient event skbs, but it reads and affects persistent socket state via `llc->state`, `llc->p_flag`, `llc->failed_data_req`, `sk_state`, and `sk_socket->state` indirectly through the state machine.

Dependencies and integration points: Depends on `llc_conn.c` for state processing and established lookup, `llc_c_st.c` for data-accept state, SAP addressing from `llc_sock`, and Linux TCP-style socket state constants used by the LLC socket layer.

Risks and test signals: Risks include consuming skbs on failure, duplicate connection behavior when an established socket already exists, and returning Linux errno values consistently despite the underlying state machine returning LLC-style statuses. Test upper-layer send during ADM, busy, and P/F wait states; connect to an existing established peer; connect allocation failure; and disconnect from invalid and established states.
