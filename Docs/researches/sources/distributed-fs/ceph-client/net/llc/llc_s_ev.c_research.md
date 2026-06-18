# Research: sources/distributed-fs/ceph-client/net/llc/llc_s_ev.c

## sources/distributed-fs/ceph-client/net/llc/llc_s_ev.c

Purpose: Provides SAP state-machine event predicate functions. Each returns 0 for a match and 1 for non-match, matching the transition scanner convention in `llc_sap.c`.

Important APIs/types/functions: Predicates include activation/deactivation requests, received UI, UNITDATA request, XID request, received XID command/response, TEST request, and received TEST command/response. They inspect `struct llc_sap_state_ev` metadata and U-PDU command/response fields.

Control flow: For primitive events, predicates match event type, primitive, and primitive type. For received PDUs, they require PDU event type, U-PDU type, command or response direction, and the expected UI/XID/TEST opcode. The SAP state table calls these in ordered transition arrays.

State and persistence behavior: No persistent state and no mutation except reading skb control/header data. Event metadata must already be initialized by `llc_sap.c` or upper-layer builders.

Dependencies and integration points: Used by `llc_s_st.c`; depends on PDU macros from `llc_pdu.h` and event layout from `llc_s_ev.h`. Its classifications must stay aligned with `llc_input.c`'s decision to send U UI/XID/TEST frames to SAP handling.

Risks and test signals: Return polarity is easy to misuse. Command/response macro alignment matters because XID and TEST opcodes are shared in similar fields. Tests should feed crafted UI/XID/TEST command and response frames, wrong primitive types, and non-U PDUs to ensure only intended transitions match.
