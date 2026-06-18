# Research: sources/distributed-fs/ceph-client/net/llc/llc_conn.c

## sources/distributed-fs/ceph-client/net/llc/llc_conn.c

Purpose: Implements the LLC type 2 connection driver: socket allocation/init/free, state-machine dispatch, established/listener lookup, received connection PDU handling, transmit queue handling, ACK removal/resend, timer defaults, and backlog processing.

Important APIs/types/functions: Exports `llc_conn_state_process()`, `llc_conn_send_pdu()`, `llc_conn_rtn_pdu()`, resend helpers, `llc_conn_remove_acked_pdus()`, `llc_lookup_established()`, `llc_data_accept_state()`, `llc_build_offset_table()`, SAP socket add/remove helpers, `llc_conn_handler()`, `llc_sk_alloc()`, `llc_sk_stop_all_timers()`, `llc_sk_free()`, and `llc_sk_reset()`. Global sysctls back timer defaults: `sysctl_llc2_ack_timeout`, `sysctl_llc2_p_timeout`, `sysctl_llc2_rej_timeout`, and `sysctl_llc2_busy_timeout`.

Control flow: `llc_conn_handler()` decodes source/destination LLC addresses, finds an established socket or listener, creates a child socket for passive opens, locks the socket, and either processes the PDU immediately or queues it to backlog. `llc_conn_state_process()` clears indication/confirmation fields, runs `llc_conn_service()`, then translates resulting primitives into socket receive queueing, stream state changes, write-space notification, or close/reset handling. `llc_conn_service()` locates the current state table, qualifies the event, executes actions, and commits `next_state`.

State and persistence behavior: Per-connection state is stored in `struct llc_sock`: state machine state, sequence variables, flags, timers, retry/window sizes, and `pdu_unack_q`. I-PDUs are cloned before transmit and the original is retained in `pdu_unack_q` for ACK tracking unless using loopback. Socket membership is persisted in SAP hash tables with RCU/nulls-list lookup and explicit SAP reference counts.

Dependencies and integration points: Uses `llc_conn_state_table` from `llc_c_st.c`, action/event definitions from LLC connection headers, PDU accessors from `llc_pdu.c`, SAP state from `llc_sap.c`, Linux socket state constants, network namespace checks, `dev_queue_xmit()`, backlog APIs, timers, and RCU/nulls socket hash traversal.

Risks and test signals: High-risk areas are skb ownership/refcount transitions, backlog lock ordering, SLAB_TYPESAFE_BY_RCU revalidation, child socket creation on listen sockets, sequence arithmetic in `llc_conn_remove_acked_pdus()`, and the transmit clone/unack queue path. Tests should cover connect/listen/accept, duplicate established lookup, timer expiry while user owns the socket, I-PDU retransmit, ACK advancement, loopback behavior, and stream state transitions from SYN_SENT/ESTABLISHED/CLOSING to close.
