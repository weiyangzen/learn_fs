# sources/distributed-fs/ceph-client/drivers/net/fddi/skfp/smtinit.c

## Purpose
`smtinit.c` sequences full SMT subsystem initialization after defaults and hardware resources are available. It connects MIB port pointers, applies OEM policy quirks, initializes the hardware driver, event/timer packages, SMT agent, and all FDDI state machines.

## Important APIs and Functions
The exported entry point is `init_smt(struct s_smc *smc, const u_char *mac_addr)`. It calls external or cross-module functions including `init_fddi_driver()`, `smt_set_mac_opvalues()`, `smt_fixup_mib()`, `ev_init()`, `smt_init_evc()`, `smt_timer_init()`, `smt_agent_init()`, `pcm_init()`, `ecm_init()`, `cfm_init()`, `rmt_init()`, `pcm()`, `ecm()`, `cfm()`, `rmt()`, `smt_agent_task()`, and `PNMI_INIT()`. `set_oem_spec_val()` is the local OEM customization helper.

## Control Flow
`init_smt()` first resets debug masks when built with global debug support. It then wires each `smc->y[p].mib` pointer to `smc->mib.p[p]`, because `smtdef.c` intentionally leaves those pointers unset during raw MIB initialization. `set_oem_spec_val()` applies an IBM OEM marker rule by restricting the connection policy to `POLICY_MM`. MAC operational timer values are recalculated before the hardware driver is initialized with the optional canonical MAC override.

After hardware setup, `smt_fixup_mib()` updates counts that depend on station attachment mode. The function then initializes event queues, SRF event-control blocks, timers, the SMT frame agent, PCM, ECM, CFM, and RMT. It explicitly kicks each state machine once so initial states are materialized, starts the SMT agent periodic NIF/timer flow, and initializes PNMI.

## State, Dependencies, and Integration
This file is the bridge from netdev open/reset paths into the SysKonnect SMT core. It depends on defaults from `smtdef.c`, EVC logic from `srf.c`, timer services from `smttimer.c`, the hardware driver, and the PCM/ECM/CFM/RMT modules. It mutates MIB pointers, OEM-dependent connection policy, state-machine internals, and timer/event queues.

## Risks and Test Signals
Initialization order is the central risk: hardware, MIB pointers, EVCs, timers, and state machines all assume earlier steps have completed. Tests should assert that every PHY MIB pointer is valid, IBM OEM policy overrides apply only when expected, state machines can be initialized from both open and reset paths, and repeated `init_smt()` calls after `smt_reset_defaults(level=1)` do not retain stale event/timer state.
