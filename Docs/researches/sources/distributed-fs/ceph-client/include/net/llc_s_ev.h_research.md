# Research: sources/distributed-fs/ceph-client/include/net/llc_s_ev.h

Purpose: `llc_s_ev.h` defines SAP-component event types and event metadata for the LLC SAP state machine. It covers SAP activation/deactivation, unitdata requests, received UI frames, XID requests/responses, and TEST requests/responses.

Important APIs/types/functions: event types distinguish simple, condition, primitive, PDU, ACK timer, and report-status classes. Event IDs include activation request, Rx UI, unitdata request, XID request, Rx XID command/response, TEST request, Rx TEST command/response, and deactivation request. `struct llc_sap_state_ev` stores primitive data, type, reason, indication/confirmation flag, and source/destination LLC addresses in `skb->cb`. `llc_sap_ev()` casts skb control storage. `llc_sap_ev_t` is the event predicate signature, with declarations for every SAP event recognizer.

Control flow: receive or socket request paths annotate an skb with `llc_sap_state_ev`, then the SAP state table runs event predicates to choose a transition. The selected transition executes actions from `llc_s_ac.h`.

State and persistence behavior: event metadata is per-skb transient state. Source and destination LLC addresses copied into the event structure drive later action behavior, but persistent SAP state lives in `struct llc_sap`.

Dependencies and integration points: it depends on `linux/skbuff.h` and `net/llc.h`. It integrates with SAP receive handling, Type 1 PDU parsing/building, SAP state tables, and socket primitive reporting.

Risks: `skb->cb` layout must be large enough and not conflict with other users on queued skbs. Event classification must distinguish XID/TEST command versus response and UI traffic accurately. Incorrect address capture can reply to the wrong peer or SAP.

Test signals: exercise activation/deactivation, UI Rx and unitdata Tx, XID/TEST command-response classification, event metadata address fields, `skb->cb` preservation through queues, and malformed Type 1 PDUs.
