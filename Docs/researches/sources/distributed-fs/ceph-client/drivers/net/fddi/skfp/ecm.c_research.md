# sources/distributed-fs/ceph-client/drivers/net/fddi/skfp/ecm.c

## Purpose
`ecm.c` implements SMT Entity Coordination Management. It inserts or removes the station from the ring, coordinates PCM start/stop across PHYs, handles trace propagation and path-test sequencing, controls optical bypass insertion/deinsertion, and reports ring/status events.

## Important APIs, Types, And Functions
The public API is `ecm_init()` and `ecm()`. The internal engine is `ecm_fsm()` with action-state macros mirroring CFM. `prop_actions()` propagates trace events through MAC/PHY topology. `start_ecm_timer()` and `stop_ecm_timer()` wrap SMT timer operations using `EV_TOKEN(EVENT_ECM, event)`.

## Control Flow
`ecm()` loops `ecm_fsm()` until `fddiSMTECMState` stabilizes, then calls `ecm_state_change()`. `EC0_OUT` waits for `EC_CONNECT`; if bypass exists on a DAS, it enters `EC5_INSERT`, otherwise `EC1_IN`. `EC1_IN` clears trace state, sends `MA_TREQ`, and queues `PC_START` for present PHYs. Trace propagation moves to `EC2_TRACE`, starts the Trace_Max timer, and either propagates upstream or marks a path test pending. Disconnects enter `EC3_LEAVE`, stop PCM, wait `TD_Min`, then either go out, path-test, or deinsert bypass. Bypass check polls QLS/HLS line states in `EC6_CHECK`; stuck bypass is reported once through AIX/ring-status hooks.

## State And Persistence
The state machine uses `smc->mib.fddiSMTECMState`, `fddiSMTBypassPresent`, `fddiSMTRemoteDisconnectFlag`, and `smc->e` fields (`path_test`, `trace_prop`, `sb_flag`, `DisconnectFlag`, `ecm_line_state`, `ecm_timer`). There is no storage persistence. Hardware side effects are MAC control commands, PCM events, timer state, and bypass control requests.

## Dependencies And Integration Points
ECM depends on SMT timers, queue dispatch, PCM, CFM topology helpers, RMT/MAC control, bypass hardware functions from `drvfbi.c`, line-state reads from PM/PLC code, `ring_status_indication()` via `RS_SET`, and optional `AIX_EVENT` reporting.

## Risks And Edge Cases
The bypass check state polls through a timer event value of `0`; dispatcher behavior must keep invoking ECM without confusing it with a named timeout. `trace_prop` needs enough bits for all PHY entities and the MAC; `NUMPHYS` above 31 is invalid per `smc.h`. Disconnect during pending path test changes `path_test` to `PT_EXITING`; mishandling this can incorrectly reinsert. Concentrator and SAS/DAS trace logic diverge under `CONCENTRATOR`.

## Test Signals
Cover connect/disconnect with and without bypass, DAS-only bypass insertion and deinsertion, `EC6_CHECK` success and stuck-bypass paths, trace initiated by MAC and each PHY, Trace_Max expiry causing path test, path-test pass/fail routing, PCM start/stop event fanout, remote disconnect event reporting, and timer cancellation when returning to `EC0_OUT`.
