# Research: sources/distributed-fs/ceph-client/include/net/llc_c_st.h

Purpose: `llc_c_st.h` defines the LLC Type 2 connection state machine schema and state IDs. It is the central contract between event detectors, qualifier arrays, action arrays, and the exported `llc_conn_state_table`.

Important APIs/types/functions: state constants include `LLC_CONN_STATE_ADM`, `SETUP`, `NORMAL`, `BUSY`, `REJ`, `AWAIT`, `AWAIT_BUSY`, `AWAIT_REJ`, `D_CONN`, `RESET`, `ERROR`, and `TEMP`, with `LLC_CONN_OUT_OF_SVC` and `NO_STATE_CHANGE` sentinel values. `struct llc_conn_state_trans` binds an event predicate, next state, qualifier list, and action list. `struct llc_conn_state` binds a current state to its transition table. `llc_conn_state_table[]` is the external table consumed by connection processing.

Control flow: `llc_conn_state_process()` uses the socket's current state to select a `llc_conn_state`, scans transitions, runs the event function, checks qualifiers, executes action functions, and applies `next_state` unless it is `NO_STATE_CHANGE`. The header itself defines only the data model and constants, not the engine.

State and persistence behavior: state is the `llc_sock.state` value and associated timers/queues declared elsewhere. Table data is static read-only protocol policy. There is no persistence beyond the connection socket lifetime.

Dependencies and integration points: it includes `llc_c_ac.h` and `llc_c_ev.h` for action, event, and qualifier function types. It integrates with the connection processor in `llc_conn.h` implementations and the generated/static state transition tables in LLC source files.

Risks: state numbering and `NBR_CONN_STATES` must match table dimensions and callers' expectations. Missing transitions can silently drop events; wrong `NO_STATE_CHANGE` usage can leave sockets stuck. Action ordering inside transition table entries is critical but not visible in this schema.

Test signals: run protocol conformance scenarios for every state, especially setup, normal, busy, reject, await, disconnect, reset, and error paths. Add transition-table coverage, invalid event fuzzing, and assertions that state numbers remain within table bounds.
