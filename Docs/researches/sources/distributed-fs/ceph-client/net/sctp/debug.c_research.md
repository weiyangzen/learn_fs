# sources/distributed-fs/ceph-client/net/sctp/debug.c

Purpose: provides string tables and lookup helpers for SCTP debug output covering chunks, states, event types, dispositions, primitives, miscellaneous events, and timers.

Important APIs/types/functions: `sctp_cname()` maps base and extension chunk ids. `sctp_state_tbl`, `sctp_evttype_tbl`, and `sctp_status_tbl` expose readable state-machine names. `sctp_pname()`, `sctp_oname()`, and `sctp_tname()` map primitive, other-event, and timer subtype values; `sctp_tname()` has a `BUILD_BUG_ON()` table-size guard.

Control flow: lookups check table bounds or switch on known extension ids, returning stable fallback strings for unknown values.

State and persistence: only static/const lookup data; no mutable runtime state.

Dependencies/integration: SCTP constants and subtype unions from SCTP headers; used by debug/state-machine logging.

Risks: tables must remain aligned with enum values. Only the timer table has an explicit build-time size guard. New chunk extensions need explicit names to avoid generic output.

Test signals: lookup base, extension, boundary, and unknown ids; build-time timer table drift; state/event/status array alignment with enum users.
