# sources/distributed-fs/ceph-client/drivers/net/ethernet/brocade/bna/bfa_cs.h

Purpose: common-service helpers for the BFA/BNA driver stack, primarily finite-state-machine support and a small wait-counter utility.

Important APIs/types/functions: `BFA_SM_TABLE` generates state-machine table types and `*_sm_to_state` functions for IOC, IOCPF, message queues, and BNA Ethernet/TX/RX state machines. `BFA_SM`, `bfa_fsm_t`, `bfa_fsm_state_decl`, `bfa_fsm_set_state`, `bfa_fsm_send_event`, and `bfa_fsm_cmp_state` implement the local FSM style. `struct bfa_wc` plus `bfa_wc_init`, `bfa_wc_up`, `bfa_wc_down`, and `bfa_wc_wait` implement a callback-triggered wait counter.

Control flow: modules declare state handlers with `bfa_fsm_state_decl`, transition with `bfa_fsm_set_state`, and dispatch events with `bfa_fsm_send_event`. Entry functions run immediately on state change. State tables translate function pointers into stable status enums for external reporting. The wait counter starts at one, increments for outstanding sub-operations, and invokes `wc_resume` when the count reaches zero.

State and persistence behavior: FSM state is stored as a function pointer in each owning object; tables are static metadata. `struct bfa_wc` is in-memory coordination state only. No persistence.

Dependencies and integration points: includes `cna.h` for shared driver types and relies on `bfa_sm_fault` being provided elsewhere. The macros are used by `bfa_ioc.c`, `bfa_msgq.c`, and BNA Ethernet/TX/RX modules.

Risks: function-pointer FSMs are compact but make invalid-event handling rely on `bfa_sm_fault`, often fatal. `*_sm_to_state` assumes every active state appears in a null-terminated or sentinel-safe table; the visible tables in users must be complete. Wait-counter functions do not use atomics or locking, so they are suitable only under caller-provided serialization.

Test signals: state transition unit tests or trace logs should show entry functions firing once per transition and state-to-enum mapping matching exported attributes. Wait-counter tests should verify resume happens exactly when the last outstanding operation completes.
