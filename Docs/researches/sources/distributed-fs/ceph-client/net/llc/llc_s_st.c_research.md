# Research: sources/distributed-fs/ceph-client/net/llc/llc_s_st.c

## sources/distributed-fs/ceph-client/net/llc/llc_s_st.c

Purpose: Defines the SAP component's two-state transition table for LLC type 1 style operations.

Important APIs/types/functions: Exports `struct llc_sap_state llc_sap_state_table[LLC_NR_SAP_STATES]`. It defines transitions for `LLC_SAP_STATE_INACTIVE` and `LLC_SAP_STATE_ACTIVE`, with action arrays referencing SAP action callbacks from `llc_s_ac.c` and event predicates from `llc_s_ev.c`.

Control flow: INACTIVE accepts activation and moves to ACTIVE after reporting status. ACTIVE handles UNITDATA/UI delivery, UNITDATA requests, XID request/command/response, TEST request/command/response, and deactivation. Most active transitions remain ACTIVE; deactivation returns to INACTIVE.

State and persistence behavior: The table itself is static. Runtime state is `sap->state`, changed by `llc_sap_next_state()` after action success. The active transitions can request upper-layer indications by setting event fields via actions.

Dependencies and integration points: Consumed by `llc_sap.c`; depends on consistent event metadata from upper-layer send helpers and receive handling. It integrates with `llc_s_ac.c` for actual transmission and indication effects.

Risks and test signals: Transition ordering matters because the scanner returns the first matching event. Inactive behavior is minimal, so unexpected active-only PDUs should be rejected. Tests should cover activation, deactivation, UI receive and send, XID/TEST command-response pairs, and action failure preventing state changes.
