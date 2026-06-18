# sources/distributed-fs/ceph-client/drivers/s390/net/ctcm_fsms.h

## Purpose
`ctcm_fsms.h` declares the event and state contracts used by the CTCM channel, MPC channel, device, and MPC group finite state machines. It is the shared vocabulary between the ccw interrupt path, the netdev lifecycle path, the MPC negotiation implementation, and the FSM tables in `ctcm_fsms.c` and `ctcm_mpc.c`.

## Important APIs, Types, And Functions
- `enum ctc_ch_events` defines ccw result events, attention/busy events, unit-check events, machine-check events, normal IRQ/final-status events, start/stop commands, and MPC-only `CTC_EVENT_SEND_XID` and `CTC_EVENT_RSWEEP_TIMER`.
- `enum ctc_ch_states` defines classic states such as `CTC_STATE_STOPPED`, `CTC_STATE_SETUPWAIT`, `CTC_STATE_RXIDLE`, `CTC_STATE_TXIDLE`, error/termination states, and MPC-only XID states `CH_XID0_PENDING` through `CH_XID7_PENDING4`.
- `enum dev_states` and `enum dev_events` define the two-channel netdev FSM states and channel-up/channel-down events.
- `enum mpcg_events` and `enum mpcg_states` define MPC group negotiation and operational states from reset/inop through passive or active XID phases to flow-control and ready.
- Declares exported FSM tables, lengths, and helper actions: `ch_fsm`, `ctcmpc_ch_fsm`, `dev_fsm`, `ctcm_ccw_check_rc()`, `ctcm_purge_skb_queue()`, `ctcm_chx_txidle()`, and `ctcmpc_chx_rxidle()`.

## Control Flow
The header does not implement flow, but it constrains it. Interrupts in `ctcm_main.c` convert ccw status into `CTC_EVENT_*` values declared here. `ctcm_fsms.c` consumes those values in table-driven transitions. `ctcm_mpc.c` consumes the MPC group event/state definitions to coordinate XID2 negotiation, flow control, and discontact handling. The numbering deliberately extends the classic channel state/event ranges for MPC, so classic FSMs use `CTC_NR_STATES` and `CTC_NR_EVENTS` while MPC FSMs use `CTC_MPC_NR_STATES` and `CTC_MPC_NR_EVENTS`.

## State And Persistence Behavior
The header defines symbolic in-memory state only. Persistence is provided by `fsm_instance` objects embedded in runtime structures, not by this file. The order and final-count constants are persistent ABI-like contracts within the driver because FSM table dimensions and state/event name arrays rely on them.

## Dependencies And Integration Points
It includes kernel headers for interrupts, timers, skbs, ccw devices, and IDALs, then includes the local `fsm.h` and `ctcm_main.h`. Because `ctcm_main.h` also includes MPC definitions, this header sits in a tightly coupled local include graph. The declarations are consumed by `ctcm_main.c`, `ctcm_fsms.c`, and `ctcm_mpc.c`.

## Risks
- Enum ordering is semantically important. Moving values, inserting states before sentinel counts, or changing `CTC_NR_*` and `CTC_MPC_NR_*` boundaries can corrupt jump-matrix indexing.
- The header includes many heavyweight kernel headers, which increases coupling and makes circular include changes risky.
- MPC and classic CTC share state names and event names, so diagnostics and FSM dimensions must remain aligned when adding MPC-only states.

## Test Signals
- Compile-time coverage catches many enum/table dimension mismatches, but behavioral tests should assert all expected state/event pairs are represented in `ch_fsm`, `ctcmpc_ch_fsm`, and `dev_fsm`.
- Trace/debug output should display correct names for channel, device, and MPC group states during setup, teardown, and XID negotiation.
