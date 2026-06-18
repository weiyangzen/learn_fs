# Research: sources/distributed-fs/ceph-client/include/net/llc_s_st.h

Purpose: `llc_s_st.h` defines the SAP state-machine schema for LLC Type 1 SAP handling. It connects SAP event predicates with next-state values and SAP action lists.

Important APIs/types/functions: `LLC_NR_SAP_STATES` declares two SAP states in the table. `struct llc_sap_state_trans` binds an event predicate, next state, and action-list pointer. `struct llc_sap_state` binds a current state to transition lists. `llc_sap_state_table[]` is the external state table used by SAP processing.

Control flow: SAP processing selects the table row for the current SAP state, scans transitions, evaluates `llc_sap_ev_t` predicates, changes to `next_state`, and executes `llc_sap_action_t` functions. The header supplies the structure and external table declaration; implementation files hold actual transition contents.

State and persistence behavior: persistent state is `struct llc_sap.state`; transition tables are static protocol policy. No runtime storage is allocated by this header.

Dependencies and integration points: it includes SAP action declarations from `llc_s_ac.h` and event declarations from `llc_s_ev.h`. It integrates with SAP open/close, SAP receive dispatch, and Type 1 PDU action code.

Risks: the state count must match the table implementation. Wrong transition ordering can select a broader predicate before a more specific one. Action-list pointers must be valid and terminated according to implementation expectations.

Test signals: SAP inactive/active transitions, activation/deactivation requests, all Type 1 event families in each state, table bounds checks, and fuzzing for unexpected SAP events.
