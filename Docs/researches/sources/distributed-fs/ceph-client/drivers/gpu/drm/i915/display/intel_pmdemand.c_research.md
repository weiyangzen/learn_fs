# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_pmdemand.c

## Purpose
`intel_pmdemand.c` implements i915 display PM Demand programming for display version 14 and newer. PM Demand packages display bandwidth, DBUF, CDCLK, DDI clock, active PHY, PLL, pipe, voltage, and scaler requirements into Punit-facing request registers. The code models those requirements as an Intel global atomic state object so atomic commits can detect changes, serialize when needed, and program higher-safe values before plane updates and settled values after plane updates.

## Important APIs, Types, And Functions
`struct pmdemand_params` is the register payload model. It tracks QGV bandwidth/index, voltage index, active pipe count, active DBUF count on pre-Xe3 platforms, active non-Type-C PHY count, PLL count, CDCLK MHz, max DDI clock MHz, and scaler count on pre-Xe3.

`struct intel_pmdemand_state` embeds `struct intel_global_state`, preserving `ddi_clocks[]`, `active_combo_phys_mask`, and the current `params`. This state is registered by `intel_pmdemand_init()` with duplicate/destroy callbacks and initialized early by `intel_pmdemand_init_early()` for the mutex and waitqueue.

The atomic-facing API is `intel_pmdemand_atomic_check()`, which decides whether the global state must be pulled into the transaction, updates parameters from bandwidth/DBUF/CDCLK/connector state, and either serializes or locks the global state depending on `allow_modeset`. `intel_pmdemand_pre_plane_update()` and `intel_pmdemand_post_plane_update()` then program registers around plane updates.

Other exported helpers update persistent input state: `intel_pmdemand_update_port_clock()` records per-pipe DDI clocks; `intel_pmdemand_update_phys_mask()` updates the active non-TC PHY mask; `intel_pmdemand_init_pmdemand_params()` reads existing hardware request values into software state; and `intel_pmdemand_program_dbuf()` programs DBUF count during display init sequencing.

## Control Flow
`intel_pmdemand_atomic_check()` is gated by `DISPLAY_VER(display) >= 14` and by `intel_pmdemand_needs_update()`. The update decision considers bandwidth PM Demand changes, DBUF changes, CDCLK changes, CRTC port-clock changes, and connector modesets that switch between non-Type-C PHY encoders.

When an update is needed, the function acquires the PM Demand global state, reads related new global states, and fills `params`: QGV peak bandwidth from `intel_bw_qgv_point_peakbw()`, active pipe/DBUF counts from DBUF state, voltage and CDCLK from CDCLK state, max DDI clock from persistent per-pipe clocks plus current CRTC states, active PHY count from connector old/new states, PLL count as active PHYs plus the CDCLK PLL, and scaler count fixed at max on pre-Xe3 because fast paths cannot safely lock all required global state.

Register programming uses `intel_pmdemand_program_params()`. It locks `display->pmdemand.lock`, verifies no previous transaction is in flight, reads both request registers, calls `intel_pmdemand_update_params()`, writes changed registers, sets `XELPDP_PMDEMAND_REQ_ENABLE`, and waits for completion either via polling on display version 20 or via the waitqueue on other platforms.

The pre-plane update passes both new and old states so each field is programmed to the maximum of old/new values. The post-plane update passes no old state so the final new values can settle. If a commit is not serialized, current register values are also considered to avoid under-programming while parallel commits may be active.

## State And Persistence Behavior
The PM Demand object is a persistent global atomic object under `display->pmdemand.obj`. It carries historical DDI clocks and non-TC PHY mask across transactions because not every CRTC or connector participates in every commit. This persistence is required to compute max DDI clock and active combo PHY count from partial atomic state.

The mutex protects MMIO register transactions and wait sequencing. The waitqueue coordinates PM Demand completion interrupts or wakeups elsewhere in the display stack. Hardware state is also read at initialization so software does not assume zeroed request parameters after firmware or BIOS programming.

## Dependencies And Integration Points
This file depends on Intel atomic global-state helpers, bandwidth state, DBUF state, CDCLK state, display register access, display workarounds, connector/encoder helpers, and platform stepping/version predicates. It programs `XELPDP_INITIATE_PMDEMAND_REQUEST(0/1)`, `GEN12_DCPR_STATUS_1`, and workaround register `XELPD_CHICKEN_DCPR_3`.

It integrates with atomic modeset validation before commit, with pre/post plane update phases during commit, and with display initialization for early DBUF programming and initial register readout.

## Risks And Edge Cases
The most important correctness risk is under-programming PM Demand during a transition. That is why pre-plane programming uses max(old,new,current) when needed. Removing that behavior could cause transient performance or power-management failures while display hardware still consumes old resources.

Concurrency is another risk. Non-modeset commits cannot serialize global state, so the code must lock the global object and consider current register values. Bugs here could race concurrent fastsets or flips.

Version-specific field packing is split between pre-Xe3 and Xe3+ paths. Active DBUF/scaler fields are not present on newer platforms, while active pipe masks use a different field. Incorrect version gating would corrupt PM Demand payloads.

Timeouts from `intel_pmdemand_check_prev_transaction()` or wait completion indicate firmware/Punit handshake issues. The initialization path zeros params on failed previous-transaction checks to avoid trusting stale state.

## Test Signals
Relevant tests include atomic modesets and fastsets that change CDCLK, bandwidth, DBUF slices, active pipes, port clocks, and connector PHY assignments on display version 14+ hardware. Stress tests should include parallel non-modeset commits to exercise current-register maxing and lock-global-state behavior.

Runtime signals include PM Demand debug logs showing request register values and error logs for timed-out Punit PM Demand responses. Workaround coverage should verify `DMD_RSP_TIMEOUT_DISABLE` programming when Wa_14016740474 applies and polling behavior for display version 20.
