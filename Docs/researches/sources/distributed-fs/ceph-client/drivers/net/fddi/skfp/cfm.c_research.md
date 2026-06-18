# sources/distributed-fs/ceph-client/drivers/net/fddi/skfp/cfm.c

## Purpose
`cfm.c` implements SMT Configuration Management for a single-MAC FDDI station. It decides whether the station is isolated, wrapped on A/B/S, or through-connected, updates MIB path state, programs the PHY mux through `config_mux()`, and tells Ring Management whether the MAC should join or loop.

## Important APIs, Types, And Functions
The public entry points are `cfm_init()`, `cfm()`, `all_selection_criteria()`, `cfm_get_mac_input()`, `cfm_get_mac_output()`, and `cem_build_path()`. The core implementation is `cfm_fsm()`, with action-state tagging via `AFLAG`, `GO_STATE()`, and `ACTIONS_DONE()`. `selection_criteria()` computes per-port withhold flags, and `cem_priv_state()` maintains private CEM port states (`DOWN`, `UP`, `HOLD`) for DAS dual-homing behavior.

## Control Flow
`cfm()` recomputes all port selection criteria, applies CEM private-port state transitions for join/loop events, then repeatedly calls `cfm_fsm()` until the MIB CFM state stabilizes. Action states perform hardware and MIB side effects: set `fddiPORTCurrentPath`, `fddiPORTMACPlacement`, `fddiSMTStationStatus`, mux mode, RMT join/loop flags, and queued RMT events. Stable states evaluate transitions from `cf_join`, `cf_loop`, `wc_flag`, `pc_mode`, `attach_s`, and station type. SAS stations enter `SC11_C_WRAP_S`; DAS stations use `SC9_C_WRAP_A`, `SC10_C_WRAP_B`, `SC4_THRU_A`, or `SC5_THRU_B`.

## State And Persistence
State is runtime-only in `smc->mib.fddiSMTCF_State`, per-port `smc->y[]` flags (`cf_join`, `cf_loop`, `wc_flag`, `scrub`, `cem_pst`), and RMT flags (`rm_join`, `rm_loop`). The file has no disk persistence. Its persistent hardware-visible effects are mux programming and updated SMT MIB values that other frame services expose.

## Dependencies And Integration Points
It depends on `smtstate.h`, `smc.h`, queue dispatch, RMT, PCM port flags, `config_mux()`, and optional SRF reporting through `smt_srf_event()`. RMT consumes the queued `RM_JOIN`/`RM_LOOP` events. ECM uses `cfm_get_mac_input()` and `cfm_get_mac_output()` for trace propagation. SMT path reporting uses `cem_build_path()`.

## Risks And Edge Cases
The state array indexing assumes CFM states fit the sparse SMT values in `smtstate.h`; new states can break `cfm_states[]` or `cf_to_ptype[]`. Withhold logic only gives A-port special handling and deliberately lets B take precedence. `cem_build_path()` ignores `path_index` and omits `SC5_THRU_B`, so through-B reports use the default isolated path unless callers map it elsewhere. CFM action state bits must not leak into MIB consumers.

## Test Signals
Exercise SAS and DAS attach modes, join/loop events on A and B, tree/peer PCM modes, `attach_s` toggles, peer-wrap SRF condition transitions, mux calls for isolate/wrap/through, `scrub` flag setting during wrap-to-through changes, RMT event generation, and path descriptor output from `cem_build_path()`.
