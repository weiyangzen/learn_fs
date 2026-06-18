# Research: sources/distributed-fs/ceph-client/net/llc/llc_s_ac.c

## sources/distributed-fs/ceph-client/net/llc/llc_s_ac.c

Purpose: Implements SAP-component action callbacks used by the SAP state machine for UI, XID, TEST, and status operations.

Important APIs/types/functions: Defines `llc_sap_action_unitdata_ind()`, `llc_sap_action_send_ui()`, XID command/response actions, TEST command/response actions, `llc_sap_action_report_status()`, `llc_sap_action_xid_ind()`, and `llc_sap_action_test_ind()`. Internal `llc_prepare_and_xmit()` initializes MAC headers, clones the skb, preserves owner when present, and transmits the clone.

Control flow: Indication actions mark received PDUs for upper-layer return through `llc_sap_rtn_pdu()`. Send actions construct the appropriate U-PDU header and control bytes, then queue a clone. Response actions decode source/destination MAC/SAP from the received skb, allocate a new frame, initialize it as a response, build a MAC header, and transmit.

State and persistence behavior: No persistent state. It mutates event skbs or creates response skbs. The original request skb remains owned by the SAP state process and is later freed or delivered.

Dependencies and integration points: Consumed by `llc_s_st.c` transition arrays and called by `llc_sap.c`. Depends on PDU helpers, `llc_alloc_frame()`, `llc_mac_hdr_init()`, Ethernet length fields, and `dev_queue_xmit()`.

Risks and test signals: TEST response length derives from the Ethernet length minus the 3-byte U header and is guarded by `skb->mac_len`; malformed length fields can still stress allocation and trim assumptions. Clone allocation failures and MAC header failures must not leak skbs. Tests should cover UI request, XID request/response, TEST with payload echo, malformed short Ethernet frames, and owner propagation on cloned sends.
