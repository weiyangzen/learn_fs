# sources/distributed-fs/ceph-client/drivers/net/fddi/skfp/smt.c

## Purpose
`smt.c` implements the FDDI Station Management (SMT) frame manager. It builds, sends, receives, validates, byte-swaps, and reacts to SMT NIF, SIF, ECF, RDF, SRF, PMF, and related frames while maintaining neighbor discovery, duplicate-address state, counters, timestamps, token-count emulation, and state-machine actions.

## Important APIs and Functions
Initialization and periodic work are `smt_agent_init()`, `smt_agent_task()`, `smt_event()`, and optional `smt_emulate_token_ct()`. Frame ingress is `smt_received_pack()`, which dispatches by SMT class and type. Frame egress helpers include `smt_send_frame()`, `smt_build_frame()`, `smt_send_rdf()`, `smt_send_nif()`, `smt_send_ecf()`, `smt_send_sif_config()`, and `smt_send_sif_operation()`. Parameter helpers include many `smt_fill_*()` functions, `smt_check_para()`, `sm_to_para()`, `smt_swap_para()`, `smt_get_tid()`, and `smt_set_timestamp()`. Management action dispatch is `smt_action()`.

## Control Flow
`smt_agent_init()` derives the SMT address from hardware, builds the station ID from the burned-in address, resets pending transaction IDs, clears UNA/DNA state, and initializes duplicate-address flags. `smt_event()` is periodically driven by the timer package: it services reconnect countdowns, driver cleanup/watchdog hooks, SRF polling, LEM/error-ratio evaluation, periodic NIF announcements, UNA/DNA expiry, and token counter emulation before rescheduling its timer.

On receive, `smt_received_pack()` filters by frame-control value, destination address, NSA/A-indicator rules, SMT version, and length; it swaps parameters into host order on little-endian systems. NIF requests update upstream neighbor and duplicate-address indicators and may trigger NIF replies. NIF replies validate transaction IDs, update downstream neighbor and duplicate-address results, and queue RMT duplicate-address events. SIF requests generate configuration or operation responses. ECF requests echo back data, while ECF replies validate pending echo tests. Unsupported or invalid request classes get RDF responses.

## State, Dependencies, and Integration
The file mutates `smc->mib`, `smc->sm`, `smc->r`, and related state-machine fields. It depends on SMT parameter definitions in `h/smt_p.h`, FDDI address constants, the event queue, PCM/ECM/CFM/RMT state machines, SRF (`smt_srf_event()`), PMF (`smt_pmf_received_pack()`), optional ESS/SBA hooks, and the lower SMT buffer send path (`smt_send_mbuf()`). Transaction state is in `smc->sm.pend[]`; neighbor timestamps are `smt_tvu` and `smt_tvd`; duplicate-address conditions are represented in MIB flags and RMT events.

## Risks and Test Signals
Risks include untrusted frame length and parameter parsing, endian conversion table coverage, neighbor/duplicate-address state races, optional feature ifdefs, and frame construction length accounting. Test signals should include NIF announce/request/reply flows, duplicate-address A-indicator handling, SIF config/operation replies, ECF echo request/reply, malformed length/version RDF generation, PMF dispatch, little-endian swap round trips, and timeout-driven UNA/DNA expiry.
