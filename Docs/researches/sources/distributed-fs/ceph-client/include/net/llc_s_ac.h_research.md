# Research: sources/distributed-fs/ceph-client/include/net/llc_s_ac.h

Purpose: `llc_s_ac.h` declares SAP-component state-transition actions for LLC Type 1 service access point handling. These actions deliver unitdata, send UI/XID/TEST PDUs, report status, and notify upper layers about XID/TEST events.

Important APIs/types/functions: action IDs include `SAP_ACT_UNITDATA_IND`, `SEND_UI`, `SEND_XID_C`, `SEND_XID_R`, `SEND_TEST_C`, `SEND_TEST_R`, `REPORT_STATUS`, `XID_IND`, and `TEST_IND`. `llc_sap_action_t` is the common action signature over `struct llc_sap *` and `struct sk_buff *`. The header declares one function per action.

Control flow: the SAP state machine matches a SAP event, then executes an action list declared with these function pointers. Actions either pass indications upward, build and send Type 1 PDUs, or report status back to the requesting socket/SAP user.

State and persistence behavior: actions operate on SAP state and skb contents but this header stores no state. Implementations may enqueue skbs to sockets, consume request skbs, or update SAP P/F bits depending on the action.

Dependencies and integration points: it depends only on forward-declared `llc_sap` and `sk_buff`, and integrates with `llc_s_st.h` state tables, `llc_s_ev.h` events, `llc_pdu.h` builders, and `llc_sap.h` send helpers.

Risks: action IDs are state-table contracts. Incorrect skb ownership in indication/send actions can leak or double-free packets. XID/TEST response actions must preserve source/destination SAP and MAC semantics.

Test signals: cover unitdata indication, UI send, XID command/response, TEST command/response including payload echo, status reporting, inactive SAP behavior, and skb lifetime checks under failure injection.
