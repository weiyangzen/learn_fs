# sources/distributed-fs/ceph-client/drivers/net/fddi/skfp/srf.c

## Purpose
`srf.c` implements FDDI SMT 7.2 Status Report Frame handling. It maps MIB conditions/events to event-control blocks, rate-limits report generation with the SR0/SR1/SR2 state machine, builds SRF announce frames, and clears report-required state after successful reporting.

## Important APIs and Functions
The public functions are `smt_init_evc()` and `smt_srf_event()`. Internal helpers are `smt_get_evc()`, `clear_all_rep()`, `clear_reported()`, and `smt_send_srf()`. Static `evc_inits[]` defines supported SMT/MAC/PORT conditions and events and maps them to SMT parameter IDs such as `SMT_P208C`, `SMT_P4050`, and `SMT_P4053`.

## Control Flow
`smt_init_evc()` clears `smc->evcs`, expands the initializer table by index count, assigns code/parameter/index fields, and then binds condition or multiple-event pointers to the relevant MIB fields. It initializes SRF timing (`TSR`) and puts the SRF state machine in `SR0_WAIT`.

`smt_srf_event()` is called with a code, index, and condition state. For conditions, unchanged state is ignored; asserted conditions set the MIB condition bit, mark the EVC report-required, and set `any_report`; deassertions clear the MIB bit. For events, repeated events set the corresponding "multiple" MIB flag while first events mark the EVC report-required. The function records transition timestamps, optionally reports to SNMP, then applies the SRF rate-limiting state machine: immediate report after the threshold window, holdoff inside the two-second window, exponential re-report threshold up to 32 seconds, and disabled state when `fddiSMTStatRptPolicy` is false.

`smt_send_srf()` builds an SMT SRF announce to the SRF multicast destination, adds timestamp/status parameters and all required event parameters, sends it through `smt_send_frame()`, and calls `clear_reported()`.

## State, Dependencies, and Integration
State is in `smc->evcs[]`, `smc->srf`, and MIB condition/multiple fields. The module depends on SMT frame building/sending, SMT parameter construction (`smt_add_para()`), ring-status macros, timestamps, and optional SNMP hooks. It is initialized by `init_smt()` and driven by `smt_event()` and other SMT/MAC/PORT modules.

## Risks and Test Signals
Risks include EVC table capacity assumptions, pointer binding correctness, threshold/holdoff timing, disabled-policy transitions, and parameter buffer length handling in `smt_send_srf()`. Tests should assert each supported code/index maps to the right MIB field, condition assert/deassert behavior, event multiple flags, policy disable/enable clearing, SRF exponential backoff, and generated SRF length/parameter contents.
