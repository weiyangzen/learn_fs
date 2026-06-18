# subset-b-001385 research

Grouped research for AMD DC clock-manager sources covering Raven, Renoir, DCN20/DCN30/DCN301/DCN31 clock programming, SMU mailbox transports, watermark table ABIs, DENTIST/DPP DTO sequencing, p-state coordination, and low-power display integration. Each section preserves the source path and is delimited for deterministic source-tree-aligned splitting.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/clk_mgr/dcn10/rv1_clk_mgr.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/clk_mgr/dcn10/rv1_clk_mgr.c

## Purpose

`rv1_clk_mgr.c` implements the Raven1 DCN10 clock-manager policy. It wires DC clock manager callbacks into the display core, translates bandwidth-computed `dc_clocks` into SMU and DPP/DPPCLK programming, and handles Raven-specific DISPCLK/DPPCLK sequencing needed during plane commits.

## Important APIs, Types, And Functions

The public entry point is `rv1_clk_mgr_construct()`. Runtime callbacks are held in `rv1_clk_funcs`, with `init_clocks`, `get_dp_ref_clk_frequency`, `update_clocks`, and `enable_pme_wa`. Internal clock setters are `rv1_clk_internal_funcs`, using `rv1_vbios_smu_set_dispclk()` and `dce112_set_dprefclk()`. Important helpers are `rv1_determine_dppclk_threshold()`, `ramp_up_dispclk_with_dpp()`, `rv1_update_clocks()`, and `rv1_enable_pme_wa()`.

## Control Flow

Construction stores `ctx`, `pp_smu`, the callback tables, DPREF spread-spectrum defaults, a 600 MHz DPREFCLK default, and BIOS-derived `dentist_vco_freq_khz`. It also enables DFS bypass if BIOS integrated info advertises `DFS_BYPASS_ENABLE` and the debug option allows it.

Clock updates exit early on `skip_clock_update`, count active displays, notify PP/SMU of display count when the prepare/optimize phase matches display-off entry, and determine whether voltage/fabric/DCF requests must be raised before display clocks. `ramp_up_dispclk_with_dpp()` may program DISPCLK in two steps around a DPP divider threshold and toggles every active DPP's `dpp_dppclk_control()` so prepare-bandwidth never leaves old hubp programming under-clocked. Lowering clocks sends SMU hard-min updates after display/DPP programming.

## State And Persistence Behavior

Persistent state is in `clk_mgr_internal` and `clk_mgr->base.clks`: current DISPCLK/DPPCLK/FCLK/DCFCLK, DPREF spread-spectrum parameters, DFS bypass flags, and BIOS-derived dentist VCO. No disk state is written; hardware state persists in SMU clock requests, DPP divider controls, and DMCU PSR wait-loop programming until the next clock update.

## Dependencies And Integration Points

The file depends on `clk_mgr_internal`, DCE clock helpers, Raven VBIOS-SMU mailbox helpers, `pp_smu_funcs_rv`, DPP resource callbacks, `clk_mgr_helper_get_active_display_cnt()`, and BIOS integrated/FW info. It is called by DC bandwidth prepare/optimize paths, so the `safe_to_lower` phase is part of the correctness contract.

## Risks

The two-step DPP divider sequencing is fragile because DPP clocks take effect before locked hubp register changes. Wrong `safe_to_lower` use can cause underflow or p-state warnings. SMU callback pointers are optional, so missing firmware hooks silently reduce voltage/display-count coordination. The code mutates `new_clocks` through forced FCLK and assumes every active pipe with a plane has a DPP with `dpp_dppclk_control()`.

## Test Signals

Useful signals include display mode-set/plane-commit tests across prepare and optimize phases, pipe-split transitions where DPPCLK becomes half DISPCLK, suspend/resume with equal DISPCLK reprogramming, forced FCLK debug testing, display-off/on cycles, PSR wait-loop changes through DMCU, and Raven SMU hard-min request tracing.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/clk_mgr/dcn10/rv1_clk_mgr.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/clk_mgr/dcn10/rv1_clk_mgr.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/clk_mgr/dcn10/rv1_clk_mgr.h

## Purpose

`rv1_clk_mgr.h` is the public constructor header for the Raven1 DCN10 clock manager. It exposes only the function needed by resource construction code to initialize a `clk_mgr_internal` instance for RV1 hardware.

## Important APIs, Types, And Functions

The only declaration is `rv1_clk_mgr_construct(struct dc_context *ctx, struct clk_mgr_internal *clk_mgr, struct pp_smu_funcs *pp_smu)`. The header relies on the including translation unit having the relevant DC and SMU types available.

## Control Flow

There is no runtime control flow in the header. At build time it provides the prototype for code that selects the RV1 clock manager. Runtime dispatch happens through the `clk_mgr_funcs` and `clk_mgr_internal_funcs` tables installed by the implementation.

## State And Persistence Behavior

The header owns no state. It describes construction of state that lives in `struct clk_mgr_internal`, including current clock values, SMU hooks, DCCG/DPP integration, and BIOS-derived clock metadata.

## Dependencies And Integration Points

It integrates with DC resource initialization and PP/SMU plumbing. Keeping the header surface narrow prevents unrelated code from depending on RV1 private helpers such as threshold calculations or SMU message details.

## Risks

Prototype drift between this header and `rv1_clk_mgr.c` would break builds. The closing comment names DCN10 rather than RV1, which is harmless but can confuse maintenance. Adding private helper declarations here would increase coupling to sequencing logic that should remain local.

## Test Signals

Build coverage is the main signal. Runtime validation comes from successful RV1 clock manager construction, clock update callback invocation, and Raven display bring-up tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/clk_mgr/dcn10/rv1_clk_mgr.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/clk_mgr/dcn10/rv1_clk_mgr_clk.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/clk_mgr/dcn10/rv1_clk_mgr_clk.h

## Purpose

`rv1_clk_mgr_clk.h` is an effectively empty include-guard header for Raven1 clock-manager clock definitions. In this snapshot it carries no declarations or macros beyond the guard.

## Important APIs, Types, And Functions

There are no exported APIs, types, or constants. `rv1_clk_mgr.c` includes it, so it exists as a placeholder or compatibility include for earlier or downstream RV1 clock definitions.

## Control Flow

The file has no runtime control flow. Its only compile-time behavior is preventing duplicate inclusion.

## State And Persistence Behavior

No state is owned or described here. Runtime clock state is managed by `rv1_clk_mgr.c` and the common clock-manager structures.

## Dependencies And Integration Points

The integration point is purely source organization: it allows RV1-specific code to include a clock-definition header without conditionalizing the include. If future RV1 register or constant declarations are added, this is the natural location.

## Risks

Because it is empty, maintainers may assume it can be removed; doing so can break include compatibility with downstream patches. Conversely, adding broad definitions here would expose RV1 internals to any file that includes it.

## Test Signals

Successful builds with `rv1_clk_mgr.c` are sufficient. No runtime tests directly target this header.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/clk_mgr/dcn10/rv1_clk_mgr_clk.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/clk_mgr/dcn10/rv1_clk_mgr_vbios_smu.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/clk_mgr/dcn10/rv1_clk_mgr_vbios_smu.c

## Purpose

`rv1_clk_mgr_vbios_smu.c` implements the Raven1 VBIOS-SMU mailbox used by the RV1 clock manager to request DISPCLK changes. It provides a thin register-level transport over MP1 SMN C2PMSG registers and updates DMCU PSR timing after the SMU returns the actual clock.

## Important APIs, Types, And Functions

The exported API is `rv1_vbios_smu_set_dispclk()`. Internal helpers are `rv1_smu_wait_for_response()` and `rv1_vbios_smu_send_msg_with_param()`. The file defines local MP1 base/address structures, C2PMSG register constants, `REG`/`FN` helpers, and VBIOSSMC message/result IDs for DISPCLK/DPREFCLK and response status.

## Control Flow

`rv1_vbios_smu_set_dispclk()` converts the requested kHz to MHz, calls the generic send helper with `VBIOSSMC_MSG_SetDispclkFreq`, and treats C2PMSG_83 as the returned actual MHz. The send helper clears C2PMSG_91 to BUSY, writes the parameter to C2PMSG_83, writes the message ID to C2PMSG_67, then polls C2PMSG_91 until it is no longer BUSY. An assertion expects `VBIOSSMC_Result_OK`. After a successful request, DMCU PSR wait-loop count is adjusted to `actual_mhz / 7` when DMCU is initialized and the returned clock differs from DFS bypass state.

## State And Persistence Behavior

The transport persists state only in MP1 mailbox registers and the returned clock in caller-managed `clk_mgr` state. DMCU wait-loop programming persists in DMCU firmware state until changed. The file keeps no heap or static mutable state.

## Dependencies And Integration Points

It depends on `reg_helper` register access, Linux sleep/delay functions through the included environment, DC/DMCU objects, `khz_to_mhz_ceil()`, and `dmcu->funcs`. It is installed as RV1's internal `.set_dispclk` callback.

## Risks

The polling helper stops on any non-BUSY response but only asserts OK; non-OK responses can still lead to reading C2PMSG_83 as a clock in non-assert builds. Register constants and MP1 base offsets are hard-coded locally. Timeout behavior is bounded by 1000 retries at 10 us but has no explicit error return from `rv1_vbios_smu_set_dispclk()` except whatever value remains in the parameter register.

## Test Signals

Trace SMU mailbox writes during DISPCLK changes, verify actual clock return values, exercise display resume and PSR panels, inject or simulate non-OK responses, and run mode changes that force repeated DISPCLK updates through the RV1 path.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/clk_mgr/dcn10/rv1_clk_mgr_vbios_smu.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/clk_mgr/dcn10/rv1_clk_mgr_vbios_smu.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/clk_mgr/dcn10/rv1_clk_mgr_vbios_smu.h

## Purpose

`rv1_clk_mgr_vbios_smu.h` declares the Raven1 VBIOS-SMU DISPCLK setter used by the RV1 clock-manager implementation.

## Important APIs, Types, And Functions

It exports `int rv1_vbios_smu_set_dispclk(struct clk_mgr_internal *clk_mgr, int requested_dispclk_khz)`. The function returns the actual DISPCLK in kHz as reported by SMU.

## Control Flow

The header has no runtime flow. It enables `rv1_clk_mgr.c` to install `rv1_vbios_smu_set_dispclk()` in the internal clock-manager function table.

## State And Persistence Behavior

No state is owned by the header. The implementation changes MP1 mailbox registers and may update DMCU PSR wait-loop state.

## Dependencies And Integration Points

It depends on `struct clk_mgr_internal` being visible to includers. The integration point is the clock-manager internal `.set_dispclk` hook.

## Risks

The header exposes only DISPCLK, so adding other RV1 SMU message helpers requires synchronized declarations. Prototype mismatch with the C implementation would cause build or call ABI failures.

## Test Signals

Build coverage verifies declaration consistency. Runtime validation belongs to RV1 DISPCLK changes and SMU mailbox tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/clk_mgr/dcn10/rv1_clk_mgr_vbios_smu.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/clk_mgr/dcn10/rv2_clk_mgr.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/clk_mgr/dcn10/rv2_clk_mgr.c

## Purpose

`rv2_clk_mgr.c` specializes the Raven2 DCN10 clock manager by reusing RV1 construction but replacing the internal clock setters with DCE112 register-based setters.

## Important APIs, Types, And Functions

The exported entry point is `rv2_clk_mgr_construct()`. The local `rv2_clk_internal_funcs` table maps `.set_dispclk` and `.set_dprefclk` to `dce112_set_dispclk()` and `dce112_set_dprefclk()`.

## Control Flow

Construction first calls `rv1_clk_mgr_construct()` to initialize all shared Raven clock-manager state, public callbacks, DPREF defaults, BIOS-derived VCO, spread-spectrum info, PP/SMU pointer, and DFS-bypass flags. It then overwrites `clk_mgr->funcs` with the RV2 internal table so later `update_clocks()` calls still use RV1 policy but program clocks through DCE112 helpers instead of the RV1 VBIOS-SMU DISPCLK mailbox.

## State And Persistence Behavior

The persistent state is inherited from RV1 construction. This file changes only the internal function table pointer, which changes future hardware programming behavior for the lifetime of the clock-manager instance.

## Dependencies And Integration Points

It depends on RV1 construction and DCE112 clock setter helpers. It is selected by ASIC/resource code for Raven2 hardware while preserving common RV1 update sequencing.

## Risks

The approach assumes RV2 differs only in the internal DISPCLK/DPREF programming mechanism. Any RV2-specific policy differences in voltage, DPP divider sequencing, or BIOS defaults would be hidden by the reused RV1 path. Because the static function table is file-local, tests need runtime coverage to confirm the correct constructor was selected.

## Test Signals

Raven2 display bring-up, DISPCLK/DPREFCLK register programming traces, suspend/resume, DPP divider transitions, and checks that VBIOS-SMU DISPCLK messages are not used on RV2.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/clk_mgr/dcn10/rv2_clk_mgr.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/clk_mgr/dcn10/rv2_clk_mgr.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/clk_mgr/dcn10/rv2_clk_mgr.h

## Purpose

`rv2_clk_mgr.h` declares the Raven2 clock-manager constructor.

## Important APIs, Types, And Functions

It exports `rv2_clk_mgr_construct(struct dc_context *ctx, struct clk_mgr_internal *clk_mgr, struct pp_smu_funcs *pp_smu)`.

## Control Flow

There is no runtime flow in the header. Runtime construction is implemented in `rv2_clk_mgr.c`, which delegates to RV1 construction and then swaps internal clock setters.

## State And Persistence Behavior

The header owns no state. It describes initialization of a `clk_mgr_internal` instance selected for Raven2 hardware.

## Dependencies And Integration Points

It integrates with DC resource construction and the shared Raven clock-manager implementation. As with RV1, type definitions must be visible through surrounding includes.

## Risks

Declaration/definition drift breaks builds. The end-guard comment still names DCN10 generically, which is harmless but imprecise.

## Test Signals

Build coverage and Raven2 resource-construction tests verify this header's contract.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/clk_mgr/dcn10/rv2_clk_mgr.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/clk_mgr/dcn20/dcn20_clk_mgr.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/clk_mgr/dcn20/dcn20_clk_mgr.c

## Purpose

`dcn20_clk_mgr.c` is the shared Navi/DCN2 clock-manager implementation. It converts bandwidth results into SMU hard-min/voltage requests, DENTIST DISPCLK/DPPCLK divider programming, DPP DTO updates, p-state handshakes, PHYCLK link-rate requests, and clock-state query helpers.

## Important APIs, Types, And Functions

Public/shared functions include `dentist_get_did_from_divider()`, `dcn20_update_clocks_update_dpp_dto()`, `dcn20_update_clocks_update_dentist()`, `dcn2_update_clocks()`, `dcn2_update_clocks_fpga()`, `dcn2_init_clocks()`, `dcn2_read_clocks_from_hw_dentist()`, `dcn2_get_clock()`, and `dcn20_clk_mgr_construct()`. Local callbacks include `dcn2_enable_pme_wa()`, `dcn2_are_clock_states_equal()`, and `dcn2_notify_link_rate_change()`. Register metadata is provided by `clk_mgr_regs`, `clk_mgr_shift`, and `clk_mgr_mask`.

## Control Flow

Construction installs DCN2 callbacks, register tables, SMU/DCCG pointers, spread-spectrum defaults, computes dentist VCO from `CLK3_CLK_PLL_REQ`, derives DPREFCLK from DFS slice 2, disables DFS bypass for dGPU, and reads spread-spectrum info. `dcn2_update_clocks()` handles resume/forced reset by reading current DENTIST dividers, updates display count through NV SMU, applies forced minimum DCFCLK, sends hard-min requests for DCFCLK, deep-sleep DCFCLK, SOCCLK, UCLK, and display voltage, updates p-state handshake support, and sequences DPP DTO versus DENTIST changes based on whether DPPCLK is being lowered.

The DENTIST helper calculates weighted dividers from VCO/current clocks, works around transitions to/from divider 127 by adding or dropping OTG pixels, then writes DISPCLK and DPPCLK dividers and waits for change-done bits. DPP DTO updates use per-pipe bandwidth DPP clocks and avoid lowering DTOs unless safe.

## State And Persistence Behavior

Clock state persists in `clk_mgr_base->clks`, DCCG `ref_dppclk` and `pipe_dppclk_khz`, SMU hard-min/voltage state, DENTIST hardware dividers, display count, PSR wait-loop settings, and `cur_phyclk_req_table`. No disk state is used.

## Dependencies And Integration Points

The file integrates with `dccg`, DCE DPREF helpers, PP/SMU NV callbacks, stream encoder FIFO calibration, DMCU PSR, link-service PHY rate changes, DC debug/config flags, and resource pool bandwidth bounding. Later DCN versions reuse its DENTIST and DTO helpers.

## Risks

Clock lowering order is safety-critical. Incorrect DENTIST divider conversion or missing divider-127 workaround can corrupt output. p-state support updates depend on `safe_to_lower` and active plane count. Optional SMU callbacks mean some voltage/display-count requests may be skipped. FPGA and forced-clock modes intentionally bypass parts of normal programming and need separate coverage.

## Test Signals

Mode sets with DPPCLK raise/lower, divider-127 transitions, active-display count changes, p-state supported/unsupported transitions, link-rate PHYCLK changes, suspend/resume, forced clock modes, FPGA builds, PSR wait-loop updates, and SMU hard-min trace validation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/clk_mgr/dcn20/dcn20_clk_mgr.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/clk_mgr/dcn20/dcn20_clk_mgr.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/clk_mgr/dcn20/dcn20_clk_mgr.h

## Purpose

`dcn20_clk_mgr.h` exposes the DCN2 shared clock-manager helpers used by DCN20 and later derived managers.

## Important APIs, Types, And Functions

It declares `dcn2_update_clocks()`, `dcn2_update_clocks_fpga()`, `dcn20_update_clocks_update_dpp_dto()`, `dcn2_init_clocks()`, `dcn20_clk_mgr_construct()`, `dentist_get_did_from_divider()`, `dcn2_get_clock()`, `dcn20_update_clocks_update_dentist()`, and `dcn2_read_clocks_from_hw_dentist()`.

## Control Flow

There is no runtime flow in the header. It enables derived clock managers such as DCN201, Renoir, DCN30, Van Gogh, and DCN31 to reuse DCN20 DPP DTO and DENTIST helpers.

## State And Persistence Behavior

No state is owned. The declared functions operate on `clk_mgr`, `clk_mgr_internal`, `dc_state`, DCCG, and hardware registers.

## Dependencies And Integration Points

It sits at the boundary between generic DCN clock code and ASIC-specific managers. It must be included where derived managers need shared DENTIST/DTO behavior.

## Risks

Because many later files call these helpers, signature or semantic changes have broad impact. `dcn2_update_clocks()` is declared with parameter name `dccg` despite taking `struct clk_mgr *`, a readability issue but not functional.

## Test Signals

Build coverage across all DCN2/DCN3 managers and runtime tests in any derived manager that exercises DENTIST and DPP DTO sequencing.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/clk_mgr/dcn20/dcn20_clk_mgr.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/clk_mgr/dcn201/dcn201_clk_mgr.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/clk_mgr/dcn201/dcn201_clk_mgr.c

## Purpose

`dcn201_clk_mgr.c` implements the Cyan Skillfish/DCN2.0.1 clock manager. It reuses DCN20 DENTIST and DPP DTO logic but keeps clock updates mostly internal to DC state rather than issuing NV SMU voltage/hard-min requests.

## Important APIs, Types, And Functions

The public constructor is `dcn201_clk_mgr_construct()`. Local callbacks are `dcn201_init_clocks()` and `dcn201_update_clocks()`, installed in `dcn201_funcs` with `dce12_get_dp_ref_freq_khz()` and `dcn2_get_clock()`. It uses DCN201 register tables built from `CLK_COMMON_REG_LIST_DCN_201()` and mask/shift macros.

## Control Flow

Initialization clears clocks, assumes p-state change support, and sets 1.2 GHz maximum supported DPPCLK/DISPCLK defaults. Updates skip on `skip_clock_update`, read current DENTIST clocks on boot/resume or forced mode, update PHYCLK, forced-min DCFCLK, DCFCLK/deep-sleep, SOCCLK, DRAMCLK, p-state support, DPPCLK, and DISPCLK in `clk_mgr_base->clks`. If hardware programming is not forced off, it reuses the DCN20 order: when lowering DPPCLK, raise per-DPP DTOs before lowering DENTIST; when raising, update DENTIST before reducing DTOs.

Construction installs callbacks/register metadata, DCCG pointer, spread-spectrum defaults, reads DPREFCLK from `CLK4_CLK2_CURRENT_CNT`, reads VCO integer multiplier from `CLK4_CLK_PLL_REQ`, falls back to 600 MHz DPREFCLK and 3 GHz VCO, enables DFS bypass from integrated BIOS info when allowed, and reads spread-spectrum info.

## State And Persistence Behavior

State persists in `clk_mgr_base->clks`, DENTIST registers, DCCG DTO state, DFS bypass flags, and BIOS-derived VCO/DPREF fields. It does not allocate memory or persist to disk.

## Dependencies And Integration Points

It depends on DCN20 shared helpers, DCE DPREF helpers, Skillfish/DCN201 register headers, BIOS integrated info, DCCG, and DC debug/config flags. It is a platform-specific constructor selected by DC resource code.

## Risks

Unlike DCN20, this path does not notify PP/SMU for hard-min voltage, UCLK, display count, or p-state handshakes; that is correct only if the platform does not require those messages. The same DENTIST/DPP sequencing risks remain. Fallback VCO/DPREF defaults can hide register-read problems.

## Test Signals

Cyan Skillfish boot/resume, forced-clock mode, DPPCLK lowering transitions, DENTIST register readback, p-state-support state changes, DFS bypass behavior from BIOS flags, and display mode changes at max clock boundaries.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/clk_mgr/dcn201/dcn201_clk_mgr.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/clk_mgr/dcn201/dcn201_clk_mgr.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/clk_mgr/dcn201/dcn201_clk_mgr.h

## Purpose

`dcn201_clk_mgr.h` declares the DCN2.0.1/Cyan Skillfish clock-manager constructor.

## Important APIs, Types, And Functions

It exports `dcn201_clk_mgr_construct(struct dc_context *ctx, struct clk_mgr_internal *clk_mgr, struct pp_smu_funcs *pp_smu, struct dccg *dccg)`.

## Control Flow

The header has no runtime flow. The implementation installs DCN201 callback tables and register metadata during resource construction.

## State And Persistence Behavior

No state is owned by the header. The constructed manager stores clock state in `clk_mgr_internal`, DCCG state, and hardware registers.

## Dependencies And Integration Points

It integrates with DC resource construction and shared DCN20 helper code. The `pp_smu` parameter is part of the common constructor shape even though DCN201's implementation does not use it heavily.

## Risks

Constructor signature drift breaks platform bring-up. The minimal header gives no access to private update helpers, which is intentional.

## Test Signals

Build coverage and DCN201 resource construction/runtime clock update tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/clk_mgr/dcn201/dcn201_clk_mgr.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/clk_mgr/dcn21/rn_clk_mgr.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/clk_mgr/dcn21/rn_clk_mgr.c

## Purpose

`rn_clk_mgr.c` implements the Renoir/DCN2.1 clock manager. It handles VBIOS-SMU clock messages, display low-power entry/exit, DPP DTO updates using actual DPP clock returns, DPM-table-derived bandwidth parameters, memory watermark range notification, boot clock snapshots, and link-rate PHYCLK requests.

## Important APIs, Types, And Functions

The public constructor is `rn_clk_mgr_construct()`. Main callbacks are `rn_update_clocks()`, `rn_init_clocks()`, `rn_enable_pme_wa()`, `rn_notify_wm_ranges()`, `rn_notify_link_rate_change()`, `rn_set_low_power_state()`, and `rn_are_clock_states_equal()`. Important helpers include `rn_get_active_display_cnt_wa()`, `rn_update_clocks_update_dpp_dto()`, `get_vco_frequency_from_reg()`, clock register dump helpers, `build_watermark_ranges()`, `find_socclk_for_voltage()`, `find_dcfclk_for_voltage()`, and `rn_clk_mgr_helper_populate_bw_params()`.

## Control Flow

Construction installs `dcn21_funcs`, sets SMU/DCCG/DFS defaults, obtains SMU version and periodic retraining status, clears the minimum DISPCLK workaround for SMU 55.51.0 or newer, reads VCO from CLK PLL registers, chooses DDR4/LPDDR4 watermark tables by memory type, Green Sardine revision, single-rank/asymmetric config, and retraining state, snapshots boot clock registers, sets DPREFCLK, and optionally replaces hard-coded bandwidth params with SMU DPM table data.

Clock update first handles power state: when safe to lower and no active display is detected, it sends display count 0; otherwise it restores mission mode. It updates hard-min DCFCLK, deep-sleep DCFCLK, clamps DPPCLK to at least 100 MHz, avoids zero DISP/DPP clocks, programs DISPCLK through SMU, and sequences DPP DTO around SMU DPPCLK requests. It uses actual DPPCLK returned by SMU as the DCCG reference.

## State And Persistence Behavior

State persists in `clk_mgr_base->clks`, `pwr_state`, `smu_ver`, `periodic_retraining_disabled`, `rn_bw_params`, selected watermark table, boot clock snapshot, DCCG DTOs, current PHYCLK request table, and PMFW watermark range state. No disk state is written.

## Dependencies And Integration Points

It depends on Renoir MP/CLK registers, `rn_clk_mgr_vbios_smu`, DCE DPREF helpers, DCN20 DPP DTO patterns, DCN20 FPU watermark table generation, PP/SMU DPM table callbacks, integrated BIOS memory info, DMCU PSR, and link encoder state.

## Risks

Active display counting intentionally mixes stream signals and DIG enable state and contains an HDMI display-off workaround; miscounts can prevent low-power entry or cause wake problems. DPM table parsing assumes voltage-level correspondence across FCLK/DCFCLK/SOCCLK arrays. Watermark table selection depends on memory type, retraining support, and ASIC revision. SMU version gates can leave older firmware without hard-min DCFCLK messages.

## Test Signals

Renoir/Green Sardine boot, LPDDR4 and DDR4 systems, display-off/on with HDMI and DP, low-power state entry, SMU DPM table reads, watermark range programming, p-state/retraining workloads, DPPCLK clamp cases, PSR wait-loop updates, and PHYCLK changes on link-rate switches.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/clk_mgr/dcn21/rn_clk_mgr.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/clk_mgr/dcn21/rn_clk_mgr.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/clk_mgr/dcn21/rn_clk_mgr.h

## Purpose

`rn_clk_mgr.h` exposes Renoir clock-manager construction and watermark table symbols.

## Important APIs, Types, And Functions

It declares external watermark tables for DDR4, LPDDR4, Green Sardine, disabled periodic retraining, and single-rank variants. It defines a small `rn_clk_registers` snapshot struct and declares `rn_clk_mgr_construct()`.

## Control Flow

The header has no runtime control flow. It lets the Renoir resource constructor instantiate the DCN2.1 clock manager and lets other compilation units provide watermark tables.

## State And Persistence Behavior

The header owns no state. The declared constructor initializes persistent manager state, selected watermark tables, SMU version fields, and DCCG clock data.

## Dependencies And Integration Points

It includes `clk_mgr.h`, `dm_pp_smu.h`, and `clk_mgr_internal.h`, tying it to the DC clock-manager and PP/SMU interfaces.

## Risks

External watermark table declarations must match exactly one definition elsewhere. The `rn_clk_registers` struct contains only one register and is not the full internal dump shape used in the C file, so it should not be treated as a complete ABI.

## Test Signals

Build/link coverage for watermark table definitions and Renoir resource construction. Runtime signals are in `rn_clk_mgr.c`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/clk_mgr/dcn21/rn_clk_mgr.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/clk_mgr/dcn21/rn_clk_mgr_vbios_smu.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/clk_mgr/dcn21/rn_clk_mgr_vbios_smu.c

## Purpose

`rn_clk_mgr_vbios_smu.c` implements Renoir's VBIOS-SMU mailbox for display clock, DCFCLK, DPPCLK, PHYCLK, display-count/low-power, 48 MHz refclk power-down, PME workaround, SMU version, and periodic retraining queries.

## Important APIs, Types, And Functions

Exports include `rn_vbios_smu_get_smu_version()`, `rn_vbios_smu_set_dispclk()`, `rn_vbios_smu_set_hard_min_dcfclk()`, `rn_vbios_smu_set_min_deep_sleep_dcfclk()`, `rn_vbios_smu_set_phyclk()`, `rn_vbios_smu_set_dppclk()`, `rn_vbios_smu_set_dcn_low_power_state()`, `rn_vbios_smu_enable_48mhz_tmdp_refclk_pwrdwn()`, `rn_vbios_smu_enable_pme_wa()`, and `rn_vbios_smu_is_periodic_retraining_disabled()`. Internal transport helpers are `rn_smu_wait_for_response()` and `rn_vbios_smu_send_msg_with_param()`.

## Control Flow

The generic send helper waits for a non-BUSY response before sending, logs if the prior response was not OK, returns `-1` if still BUSY, clears the response register, writes the argument and message ID, waits again, reports SMU timeout through `dm_helpers_smu_timeout()`, and returns the argument register. Clock setters convert kHz to MHz and multiply returned MHz back to kHz. DCFCLK hard-min and deep-sleep setters are gated on SMU version `0x370c00`. Display low-power is encoded as display count 0 or 1.

## State And Persistence Behavior

State persists in MP1 C2PMSG registers and PMFW-controlled clock/power policy. DISPCLK updates also adjust DMCU PSR wait-loop state. The implementation holds no allocated or static mutable state.

## Dependencies And Integration Points

It depends on Renoir MP register headers, `reg_helper`, `dm_helpers_smu_timeout()`, DC logging, DMCU, `khz_to_mhz_ceil()`, and `enum dcn_pwr_state`. `rn_clk_mgr.c` calls these helpers for all runtime SMU interactions.

## Risks

The transport returns the argument register for all messages, even commands whose response semantics are not frequencies. Failed commands may propagate `-1` through kHz conversions. Assertions assume PMFW returns actual DISP/DPP clocks at least as high as requested. Periodic retraining query passes default parameter 1 so unsupported messages are treated conservatively as disabled.

## Test Signals

Mailbox timeout injection, SMU version-gated DCFCLK messages, display low-power display-count messages, DPP/DISP actual clock validation, 48 MHz power-down toggling, PME workaround calls, periodic retraining query behavior, and PSR wait-loop updates.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/clk_mgr/dcn21/rn_clk_mgr_vbios_smu.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/clk_mgr/dcn21/rn_clk_mgr_vbios_smu.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/clk_mgr/dcn21/rn_clk_mgr_vbios_smu.h

## Purpose

`rn_clk_mgr_vbios_smu.h` declares the Renoir VBIOS-SMU helper API consumed by `rn_clk_mgr.c`.

## Important APIs, Types, And Functions

It forward-declares `enum dcn_pwr_state` and declares SMU helpers for version query, DISPCLK, DCFCLK hard-min/deep-sleep, PHYCLK, DPPCLK, DCN power state, 48 MHz refclk power-down, PME workaround, and periodic retraining status.

## Control Flow

There is no runtime flow in the header. It defines the callable mailbox surface used by Renoir clock update and construction paths.

## State And Persistence Behavior

The header owns no state. Implementations persist effects in PMFW clock/power state, MP mailbox registers, and DMCU timing.

## Dependencies And Integration Points

It integrates the Renoir clock manager with PMFW without exposing register-level details to the policy file.

## Risks

All declarations depend on `struct clk_mgr_internal` visibility from includers. Adding new SMU messages requires updating both this header and the implementation.

## Test Signals

Build coverage for prototype consistency; runtime SMU-message tests through `rn_clk_mgr.c`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/clk_mgr/dcn21/rn_clk_mgr_vbios_smu.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/clk_mgr/dcn30/dalsmc.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/clk_mgr/dcn30/dalsmc.h

## Purpose

`dalsmc.h` defines the DCN30 DAL-to-SMU message ABI constants used by DCN30 clock-manager SMU mailbox code.

## Important APIs, Types, And Functions

It defines `DALSMC_VERSION`, SMU response codes, message IDs from `DALSMC_MSG_TestMessage` through `DALSMC_MSG_SmartAccess`, and `DALSMC_Message_Count`. There are no functions or structs.

## Control Flow

No runtime flow exists. The constants drive message selection and response interpretation in `dcn30_clk_mgr_smu_msg.c` and `dcn30m_clk_mgr_smu_msg.c`.

## State And Persistence Behavior

The header owns no state. It describes a firmware ABI whose effects are persisted by PMFW when messages are sent.

## Dependencies And Integration Points

It is included by DCN30 SMU message implementations. `DALSMC_MSG_SmartAccess` is used by the mobile SmartMux path; watermark, DPM, display-count, MALL, DF C-state, and PME messages are used by the main DCN30 clock manager.

## Risks

The comment says this is temporary until definitions exist in the proper location, so ABI drift against PMFW headers is a risk. Numeric message IDs are firmware contracts; accidental renumbering would send the wrong command.

## Test Signals

Compile-time inclusion plus runtime SMU version/header checks, test message response, watermark transfers, DPM frequency queries, hard-min/max requests, and SmartAccess/SmartMux commands.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/clk_mgr/dcn30/dalsmc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/clk_mgr/dcn30/dcn30_clk_mgr.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/clk_mgr/dcn30/dcn30_clk_mgr.c

## Purpose

`dcn30_clk_mgr.c` implements the DCN3.0 clock manager for Sienna Cichlid-style dGPU. It initializes clock DPM levels from SMU, manages DISPCLK/DPPCLK/DCEFCLK/UCLK hard-mins, uploads watermark tables to PMFW, updates memory clock limits, and exposes DCN3 clock-manager callbacks.

## Important APIs, Types, And Functions

Public functions are `dcn3_init_clocks()`, `dcn3_clk_mgr_construct()`, and `dcn3_clk_mgr_destroy()`. Key helpers are `dcn3_init_single_clock()`, `dcn3_build_wm_range_table()`, `dcn30_get_vco_frequency_from_reg()`, `dcn3_update_clocks()`, `dcn3_notify_wm_ranges()`, memory limit setters, `dcn3_get_memclk_states_from_smu()`, `dcn3_is_smu_present()`, `dcn3_are_clock_states_equal()`, `dcn3_enable_pme_wa()`, and `dcn30_notify_link_rate_change()`. Callback tables are `dcn3_funcs` and `dcn3_fpga_funcs`.

## Control Flow

Construction installs callbacks/register masks, sets DFS/DPREF defaults and VCO fallback, allocates `bw_params`, and allocates a GART watermark range table whose GPU address is later passed to PMFW. `dcn3_init_clocks()` clears clock state, detects SMU presence through version query unless forced off, checks PMFW interface/header versions, queries DPM levels for DCEFCLK, DTBCLK, SOCCLK, DISPCLK, PIXCLK, PHYCLK, refreshes UCLK states, and builds watermark ranges.

`dcn3_update_clocks()` returns if SMU is missing, handles boot/resume DENTIST reads, notifies display count, applies forced DCFCLK minimums, sends DCEFCLK and deep-sleep hard-mins, manages p-state support by pinning UCLK to max or DC-mode softmax when unsupported, updates UCLK when support returns, sends hard-mins for PIXCLK and DISPCLK, sequences DPP DTO versus DENTIST changes, and updates DMCU PSR wait loops.

## State And Persistence Behavior

Persistent state includes `smu_present`, `smu_ver`, `bw_params`, `wm_range_table` and GPU address, clock state, p-state support history, DCCG DTO state, SMU hard-min/max constraints, and PMFW watermark table contents. `dcn3_clk_mgr_destroy()` frees allocated bandwidth params and watermark GPU memory.

## Dependencies And Integration Points

It depends on DCN20 shared DENTIST/DTO helpers, DCN30 SMU message helpers, DCN30 FPU watermark builder, Sienna/NBIO/MMHUB/DPCS register headers, DMCU, DCCG, DC resource bounding-box update functions, and SmartMux mobile hook `dcn30m_set_smartmux_switch()`.

## Risks

SMU absence disables updates entirely, so fallback behavior must be intentional. UCLK p-state pinning and DC-mode softmax transitions are subtle and can overconstrain memory clocks. Watermark upload requires valid GPU memory and matching `WatermarksExternal_t` layout. Construction can return after allocation failures without freeing earlier allocations. `dcn3_build_wm_range_table()` is wrapped in FPU guards twice.

## Test Signals

SMU present/absent paths, DPM-level discovery, interface/header version checks, p-state unsupported modes, DC-mode softmax, UCLK min/max APIs, watermark table uploads, link-rate PHYCLK changes, MALL/DF C-state messages, suspend/resume DENTIST reads, and destroy-time memory cleanup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/clk_mgr/dcn30/dcn30_clk_mgr.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/clk_mgr/dcn30/dcn30_clk_mgr.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/clk_mgr/dcn30/dcn30_clk_mgr.h

## Purpose

`dcn30_clk_mgr.h` declares DCN3 clock-manager construction/destruction and carries temporary DCN30 CLK register field definitions missing from generated headers.

## Important APIs, Types, And Functions

It declares `dcn3_init_clocks()`, `dcn3_clk_mgr_construct()`, and `dcn3_clk_mgr_destroy()`. It also defines several CLK PLL/DFS masks, shifts, and MMIO offsets for CLK0/CLK1/CLK2/CLK3 instances and AMCLK-related registers when the generated mask is absent.

## Control Flow

There is no runtime flow. The macros are consumed at compile time by DCN30 clock-manager code that reads VCO/DFS state.

## State And Persistence Behavior

The header owns no mutable state. The declared constructor allocates runtime `bw_params` and watermark GPU memory; destroy frees them.

## Dependencies And Integration Points

It integrates DCN30 resource construction with clock-manager internals and provides stopgap register definitions needed by implementation code.

## Risks

Temporary duplicated register definitions can drift from generated hardware headers. If the include guard around the fallback macros is wrong, stale masks or offsets could be used silently. Constructor/destroy declarations must remain synchronized with `dcn30_clk_mgr.c`.

## Test Signals

Build coverage, VCO readback sanity, clock-manager construction/destruction tests, and comparing fallback register constants against generated headers when they become available.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/clk_mgr/dcn30/dcn30_clk_mgr.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/clk_mgr/dcn30/dcn30_clk_mgr_smu_msg.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/clk_mgr/dcn30/dcn30_clk_mgr_smu_msg.c

## Purpose

`dcn30_clk_mgr_smu_msg.c` implements the DCN30 DALSMC mailbox transport and typed wrappers for PMFW clock, DPM, watermark, display, MALL, DF C-state, and PME messages.

## Important APIs, Types, And Functions

Exports include `dcn30_smu_test_message()`, `dcn30_smu_get_smu_version()`, interface/header version checks, DRAM address setters, watermark table transfers, hard-min/max by frequency, DPM frequency queries, DC-mode max DPM query, minimum deep-sleep DCEFCLK, number-of-displays, display-refresh-from-MALL, external-client DF C-state allow, and PME workaround. Internal helpers are `dcn30_smu_wait_for_response()` and `dcn30_smu_send_msg_with_param()`.

## Control Flow

The send helper waits for a nonzero response register, clears it, writes DAL argument and message registers, traces the message, waits again, reports timeouts, and returns true only for `DALSMC_Result_OK`, optionally reading the argument register as output. Frequency messages pack clock ID in bits 23:16 and MHz or DPM level in the low bits. Watermark transfers first require the caller to set DRAM high/low address, then send table-transfer messages with `TABLE_WATERMARKS`.

## State And Persistence Behavior

The file holds no heap/static mutable state. It changes PMFW state through SMU messages and uses DAL response/argument/message registers as transient mailbox state. Trace macros record message latency.

## Dependencies And Integration Points

It depends on `dalsmc.h`, `dcn30_smu11_driver_if.h`, `reg_helper`, DC logging, SMU timeout helpers, and DCN30 clock-manager callers. `dcn30_clk_mgr.c` uses it for all PMFW interactions.

## Risks

`CmdRejectedBusy` is noted but not specially retried. Most void wrappers ignore failed sends. Interface/header version checks return booleans but current init does not fail hard on mismatch. Parameter packing assumes frequencies fit in 16 bits. The mailbox register offsets are hard-coded DAL register numbers.

## Test Signals

SMU test message, version/interface/header checks, timeout handling, DPM feature query with `0xFF`, hard-min/max readbacks, watermark upload/download, display-count changes, MALL refresh parameters, DF C-state toggles, and PME message tracing.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/clk_mgr/dcn30/dcn30_clk_mgr_smu_msg.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/clk_mgr/dcn30/dcn30_clk_mgr_smu_msg.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/clk_mgr/dcn30/dcn30_clk_mgr_smu_msg.h

## Purpose

`dcn30_clk_mgr_smu_msg.h` declares the DCN30 SMU mailbox wrapper API.

## Important APIs, Types, And Functions

It declares message wrappers for test/version checks, DRAM address setup, watermark transfers, hard min/max frequency, DPM frequency queries, DC-mode max DPM, deep-sleep DCEFCLK, display count, MALL refresh, external DF C-state allow, and PME workaround.

## Control Flow

The header has no runtime flow. It exposes the typed SMU command surface to `dcn30_clk_mgr.c`.

## State And Persistence Behavior

No state is owned. Implementations persist effects in PMFW and mailbox registers.

## Dependencies And Integration Points

It includes `core_types.h` and forward-declares `struct clk_mgr_internal`. It is the public boundary between DCN30 clock policy and DALSMC transport.

## Risks

Prototype mismatches can corrupt SMU parameter packing or return handling. Because many wrappers are void, callers cannot observe failure unless implementation or logs are checked.

## Test Signals

Build coverage and runtime SMU command tests via DCN30 clock-manager operations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/clk_mgr/dcn30/dcn30_clk_mgr_smu_msg.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/clk_mgr/dcn30/dcn30_smu11_driver_if.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/clk_mgr/dcn30/dcn30_smu11_driver_if.h

## Purpose

`dcn30_smu11_driver_if.h` defines the subset of the SMU11 driver interface used by DCN30 display clock management, especially PPCLK IDs and watermark table layouts.

## Important APIs, Types, And Functions

It defines `SMU11_DRIVER_IF_VERSION`, `PPCLK_e`, `WatermarkRowGeneric_t`, watermark constants/enums, `Watermarks_t`, `WatermarksExternal_t`, and table IDs such as `TABLE_WATERMARKS`.

## Control Flow

No runtime flow exists. The structures are filled by `dcn30_clk_mgr.c` and transferred to PMFW through `dcn30_clk_mgr_smu_msg.c`.

## State And Persistence Behavior

The header describes binary table state shared with PMFW. Runtime instances live in GPU memory allocated by the clock manager and are persisted in PMFW after table transfer.

## Dependencies And Integration Points

It integrates DC display clock code with PMFW's SMU11 table ABI. PPCLK IDs are used in hard-min/max and DPM query messages. `WatermarksExternal_t` is the memory layout passed by physical/GPU address to PMFW.

## Risks

Any layout, padding, enum, or version mismatch can make PMFW misinterpret watermark data or reject interface checks. The file lacks include guards in this snapshot, so duplicate inclusion safety depends on surrounding usage.

## Test Signals

SMU driver-interface version check, watermark table upload acceptance, DPM query correctness for each PPCLK ID, and ABI-size/layout checks against PMFW headers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/clk_mgr/dcn30/dcn30_smu11_driver_if.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/clk_mgr/dcn30/dcn30m_clk_mgr.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/clk_mgr/dcn30/dcn30m_clk_mgr.c

## Purpose

`dcn30m_clk_mgr.c` is the small mobile DCN30 SmartMux bridge. It exposes a clock-manager callback that sends SmartMux switch requests to SMU.

## Important APIs, Types, And Functions

The exported function is `dcn30m_set_smartmux_switch(struct clk_mgr *clk_mgr_base, uint32_t pins_to_set)`. It converts the public `clk_mgr` to `clk_mgr_internal` and calls `dcn30m_smu_set_smart_mux_switch()`.

## Control Flow

There is one straight-line call path from DC clock-manager function table `.set_smartmux_switch` to the DCN30M SMU message helper. The return value from SMU is passed back to the caller.

## State And Persistence Behavior

This file owns no state. SmartMux pin/switch state is maintained by PMFW/platform hardware after the SMU message.

## Dependencies And Integration Points

It depends on `clk_mgr_internal`, `dcn30m_clk_mgr.h`, and `dcn30m_clk_mgr_smu_msg.h`. DCN30's main function table points `.set_smartmux_switch` at this helper.

## Risks

There is no local validation of `pins_to_set`, so correctness depends on callers and PMFW. If the active platform does not support SmartMux, failures are only visible through the SMU response.

## Test Signals

SmartMux switch requests on mobile platforms, SMU response validation, and negative tests for unsupported pins or unsupported firmware.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/clk_mgr/dcn30/dcn30m_clk_mgr.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/clk_mgr/dcn30/dcn30m_clk_mgr.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/clk_mgr/dcn30/dcn30m_clk_mgr.h

## Purpose

`dcn30m_clk_mgr.h` declares the mobile DCN30 SmartMux clock-manager callback.

## Important APIs, Types, And Functions

It exports `uint32_t dcn30m_set_smartmux_switch(struct clk_mgr *clk_mgr_base, uint32_t pins_to_set)`.

## Control Flow

No runtime flow exists. The implementation sends a DALSMC SmartAccess message through the mobile SMU helper.

## State And Persistence Behavior

The header owns no state. Runtime state is PMFW/platform SmartMux state.

## Dependencies And Integration Points

It is included by DCN30 main clock-manager code to install the SmartMux callback.

## Risks

Signature drift or missing declaration breaks the callback table. No enum is provided for `pins_to_set`, so semantic validation is external.

## Test Signals

Build coverage and SmartMux runtime tests on DCN30 mobile systems.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/clk_mgr/dcn30/dcn30m_clk_mgr.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/clk_mgr/dcn30/dcn30m_clk_mgr_smu_msg.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/clk_mgr/dcn30/dcn30m_clk_mgr_smu_msg.c

## Purpose

`dcn30m_clk_mgr_smu_msg.c` implements the mobile DCN30 SMU mailbox command used for SmartMux switching.

## Important APIs, Types, And Functions

The exported function is `dcn30m_smu_set_smart_mux_switch()`. Internal helpers mirror the DCN30 DALSMC transport: `dcn30m_smu_wait_for_response()` and `dcn30m_smu_send_msg_with_param()`.

## Control Flow

The send helper waits for a response, clears response, writes argument and message ID, waits for completion, reports timeout through `dm_helpers_smu_timeout()`, and returns true only on `DALSMC_Result_OK`. The SmartMux wrapper sends `DALSMC_MSG_SmartAccess` with `pins_to_set` and returns the response argument.

## State And Persistence Behavior

Only mailbox registers are transiently modified. SmartMux routing state persists in PMFW/platform hardware. No local memory is allocated.

## Dependencies And Integration Points

It depends on `dalsmc.h`, DAL mailbox register offsets, `reg_helper`, DC logging, and timeout helpers. It is called by `dcn30m_clk_mgr.c`.

## Risks

The transport duplicates much of `dcn30_clk_mgr_smu_msg.c` but without message tracing and with the same unhandled busy-reject note. Unsupported firmware commands return false internally, but the wrapper returns a zero response without richer error detail.

## Test Signals

SmartAccess command response checks, timeout path testing, busy/rejected command behavior, and platform validation that the requested mux pins actually change routing.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/clk_mgr/dcn30/dcn30m_clk_mgr_smu_msg.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/clk_mgr/dcn30/dcn30m_clk_mgr_smu_msg.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/clk_mgr/dcn30/dcn30m_clk_mgr_smu_msg.h

## Purpose

`dcn30m_clk_mgr_smu_msg.h` declares the mobile DCN30 SmartMux SMU message helper.

## Important APIs, Types, And Functions

It forward-declares `struct clk_mgr_internal` and exports `dcn30m_smu_set_smart_mux_switch()`.

## Control Flow

There is no runtime flow. The declaration is used by `dcn30m_clk_mgr.c`.

## State And Persistence Behavior

No state is owned. The implementation modifies PMFW SmartMux state through DALSMC.

## Dependencies And Integration Points

It includes `core_types.h` for fixed-width types and connects the mobile clock-manager wrapper to the mailbox implementation.

## Risks

The API exposes raw pin bits rather than a typed enum. Declaration drift breaks SmartMux callback builds.

## Test Signals

Build coverage and SmartMux SMU command execution tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/clk_mgr/dcn30/dcn30m_clk_mgr_smu_msg.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/clk_mgr/dcn301/dcn301_smu.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/clk_mgr/dcn301/dcn301_smu.c

## Purpose

`dcn301_smu.c` implements the Van Gogh/DCN3.0.1 VBIOS-SMU mailbox. It wraps MP1 C2PMSG messages for clock setting, DCFCLK constraints, display idle optimization, PME, DRAM-address setup, and DPM/watermark table transfers.

## Important APIs, Types, And Functions

Exports include `dcn301_smu_get_smu_version()`, `dcn301_smu_set_dispclk()`, `dcn301_smu_set_dprefclk()`, `dcn301_smu_set_hard_min_dcfclk()`, `dcn301_smu_set_min_deep_sleep_dcfclk()`, `dcn301_smu_set_dppclk()`, `dcn301_smu_set_display_idle_optimization()`, `dcn301_smu_enable_phy_refclk_pwrdwn()`, `dcn301_smu_enable_pme_wa()`, DRAM address setters, and DPM/watermark table transfer helpers. Internal helpers are `dcn301_smu_wait_for_response()` and `dcn301_smu_send_msg_with_param()`.

## Control Flow

The send helper waits for the previous response, logs non-OK responses, returns `-1` if still busy, clears response to BUSY, writes the argument and message, waits for completion, reports timeout, and returns C2PMSG_83. Clock setters convert kHz to MHz and return actual MHz as kHz. Table transfer functions assume the caller already set a GPU/MC address high and low. Display idle optimization sends a packed bitfield for DF request disable, PHY refclk off, and related idle flags.

## State And Persistence Behavior

State persists in PMFW clock/power policy, display idle optimization state, DPM/watermark table memory shared with SMU, and MP mailbox registers. No local dynamic state is held.

## Dependencies And Integration Points

It depends on Van Gogh MP register headers, `reg_helper`, `dm_helpers_smu_timeout()`, DC logging, and definitions from `dcn301_smu.h`. `vg_clk_mgr.c` uses it for all PMFW communication.

## Risks

Failure returns can become negative clocks when multiplied by 1000. Several command IDs are commented out or reused, so firmware ABI alignment is critical. `dcn301_smu_set_dprefclk()` notes DP DTO programming is handled elsewhere. Void helpers ignore send failure.

## Test Signals

SMU version detection, DISP/DPP/DCFCLK set responses, idle optimization transitions, DPM table transfer into framebuffer memory, watermark upload, PME workaround, timeout injection, and validation on Van Gogh firmware revisions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/clk_mgr/dcn301/dcn301_smu.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/clk_mgr/dcn301/dcn301_smu.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/clk_mgr/dcn301/dcn301_smu.h

## Purpose

`dcn301_smu.h` defines Van Gogh/DCN3.0.1 PMFW table layouts, DPM clock structures, watermark structures, display idle bitfields, and SMU helper prototypes.

## Important APIs, Types, And Functions

It defines `SMU13_DRIVER_IF_VERSION`, `df_pstate_t`, `vcn_clk_t`, `DSPCLK_e`, `DisplayClockTable_t`, `WatermarkRowGeneric_t`, watermark enums, `Watermarks_t`, table IDs `TABLE_WATERMARKS` and `TABLE_DPMCLOCKS`, VG DPM level counts, `struct vg_dpm_clocks`, `struct smu_dpm_clks`, `struct watermarks`, `struct display_idle_optimization`, `union display_idle_optimization_u`, and all `dcn301_smu_*` prototypes.

## Control Flow

The header has no runtime control flow. Its structs are allocated by `vg_clk_mgr.c`, filled by SMU table transfers or watermark builders, then passed back to PMFW through mailbox commands.

## State And Persistence Behavior

It defines binary shared-memory state: DPM clocks copied from SMU, watermark rows copied to SMU, and display idle optimization bitfields sent as message parameters. Runtime ownership is in the clock manager and PMFW.

## Dependencies And Integration Points

It is the ABI boundary between Van Gogh display clock management and PMFW. `vg_clk_mgr.c` uses its types for framebuffer-backed SMU tables; `dcn301_smu.c` uses its prototypes and table IDs.

## Risks

The header comments say some definitions are copied from PMFW headers; layout drift is a firmware compatibility risk. Counts must match PMFW array sizes. The display idle bitfield is packed into a `uint32_t`, so bit ordering is ABI-sensitive.

## Test Signals

Static layout/version checks against PMFW headers, DPM table transfer validation, watermark upload acceptance, idle optimization behavior, and build coverage of all SMU helper prototypes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/clk_mgr/dcn301/dcn301_smu.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/clk_mgr/dcn301/vg_clk_mgr.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/clk_mgr/dcn301/vg_clk_mgr.c

## Purpose

`vg_clk_mgr.c` implements the Van Gogh/DCN3.0.1 clock manager. It manages SMU-backed display/DPP/DCF clocks, display idle low-power state, framebuffer-backed DPM and watermark tables, BIOS/SMU-derived bandwidth parameters, and Van Gogh-specific watermark selection.

## Important APIs, Types, And Functions

Public functions are `vg_clk_mgr_construct()` and `vg_clk_mgr_destroy()`. Main callbacks are `vg_update_clocks()`, `vg_init_clocks()`, `vg_enable_pme_wa()`, `vg_notify_wm_ranges()`, and `vg_are_clock_states_equal()`. Important helpers include `vg_get_active_display_cnt_wa()`, VCO and clock-register dump helpers, `vg_build_watermark_ranges()`, `find_max_clk_value()`, `find_dcfclk_for_voltage()`, `vg_clk_mgr_helper_populate_bw_params()`, and `vg_get_dpm_table_from_smu()`.

## Control Flow

Construction initializes nested `clk_mgr_vgh`/`clk_mgr_internal` state, allocates framebuffer memory for watermarks and DPM clocks with dummy fallbacks, queries SMU version, reads dentist VCO, chooses DDR4 or LPDDR5 watermark table from BIOS memory type, snapshots boot clocks, sets DPREFCLK/spread-spectrum state, transfers DPM clocks from SMU into GPU memory, and populates bandwidth params from BIOS plus SMU table. It frees the temporary DPM table before returning.

Clock updates handle low-power display idle by sending `display_idle_optimization` when safe to lower and no active display remains, update hard-min DCFCLK and deep-sleep DCFCLK unless disabled by debug, clamp DPPCLK to 100 MHz, set DISPCLK, and sequence DPP DTOs relative to SMU DPPCLK changes. Watermark notification builds `struct watermarks`, sets its MC address, and transfers it to SMU.

## State And Persistence Behavior

Persistent state includes `clk_mgr_vgh.smu_wm_set`, selected `vg_bw_params`, SMU version/presence, boot clock snapshot, power state, DCCG DTOs, PMFW clock constraints, and watermark table contents. `vg_clk_mgr_destroy()` frees allocated watermark framebuffer memory.

## Dependencies And Integration Points

It depends on DCN20 DTO helpers, DCN20 FPU watermark table adjustment, Van Gogh register headers, `dcn301_smu`, BIOS integrated info, framebuffer memory allocation helpers, DCCG, DC debug flags, and external DDR4/LPDDR5 watermark tables.

## Risks

Dummy fallback tables let construction continue when GPU memory allocation fails, but SMU transfers are then skipped because MC address is zero. DPM table parsing assumes nonzero reverse-filled DF pstates and voltage lookup consistency. The low-power active-display workaround can miscount. The DPPCLK clamp lacks the Renoir guard for zero, so a zero request becomes 100 MHz.

## Test Signals

Van Gogh boot with SMU present/absent, framebuffer allocation failure fallback, DPM table transfer, DDR4 versus LPDDR5 watermark selection, display idle entry/exit, DPPCLK lowering/raising, DCFCLK debug disable, watermark upload, and destroy-time framebuffer free checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/clk_mgr/dcn301/vg_clk_mgr.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/clk_mgr/dcn301/vg_clk_mgr.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/clk_mgr/dcn301/vg_clk_mgr.h

## Purpose

`vg_clk_mgr.h` declares the Van Gogh clock-manager wrapper type and constructor/destructor.

## Important APIs, Types, And Functions

It forward-declares `struct watermarks`, declares external `ddr4_wm_table` and `lpddr5_wm_table`, defines `struct smu_watermark_set` with a watermark pointer and MC address, defines `struct clk_mgr_vgh` embedding `clk_mgr_internal`, and declares `vg_clk_mgr_construct()` and `vg_clk_mgr_destroy()`.

## Control Flow

There is no runtime flow in the header. It defines the object layout that lets implementation code recover `clk_mgr_vgh` from the embedded base and manage SMU watermark memory.

## State And Persistence Behavior

The declared wrapper persists watermark table memory and its GPU/MC address alongside the base clock manager. The header itself owns no state.

## Dependencies And Integration Points

It includes `clk_mgr_internal.h` and integrates Van Gogh-specific watermark memory with generic DC clock-manager callbacks.

## Risks

The embedded-struct layout is relied on by `container_of()` in `vg_clk_mgr.c`; changing field order breaks that conversion. External watermark table declarations must be defined elsewhere.

## Test Signals

Build/link coverage, constructor/destructor memory lifecycle tests, and runtime watermark notification on Van Gogh systems.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/clk_mgr/dcn301/vg_clk_mgr.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/clk_mgr/dcn31/dcn31_clk_mgr.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/clk_mgr/dcn31/dcn31_clk_mgr.c

## Purpose

`dcn31_clk_mgr.c` implements the DCN3.1/Yellow Carp clock manager. It handles SMU-backed clock updates, Z-state and DTBCLK control, display idle optimization, DMCUB clock notification, DPM-table-derived bandwidth params, DDR5/LPDDR5 watermark programming, and SMU shared-memory allocation.

## Important APIs, Types, And Functions

Public functions are `dcn31_update_clocks()`, `dcn31_init_clocks()`, `dcn31_are_clock_states_equal()`, `dcn31_get_dtb_ref_freq_khz()`, `dcn31_clk_mgr_construct()`, and `dcn31_clk_mgr_destroy()`. Helpers include `dcn31_get_active_display_cnt_wa()`, `dcn31_disable_otg_wa()`, `get_vco_frequency_from_reg()`, `dcn31_build_watermark_ranges()`, `dcn31_notify_wm_ranges()`, `dcn31_get_dpm_table_from_smu()`, `find_clk_for_voltage()`, `dcn31_clk_mgr_helper_populate_bw_params()`, and `dcn31_set_low_power_state()`.

## Control Flow

Construction initializes nested manager state, allocates framebuffer watermark and DPM tables with dummy fallbacks, queries SMU version, reads dentist VCO, chooses DDR5/LPDDR5 watermark table by BIOS memory type, sets DPREF/ref DTB clock defaults, installs bandwidth params, and if debug `pstate_enabled` is true, transfers DPM clocks from SMU, logs them, and populates bandwidth params with FCLK/MemClk/voltage/WCK ratio/DCFCLK/SOCCLK/dispclk/dppclk data.

Clock update first manages Z-state support and periodic detection, DTBCLK enable/disable, and display idle optimization based on `safe_to_lower`. It sends DCFCLK and deep-sleep DCFCLK requests, clamps DPPCLK to 100 MHz, temporarily disables OTGs for DPMS-off or virtual streams around DISPCLK changes, sequences DPP DTOs and DPPCLK, then sends a `DMUB_CMD__CLK_MGR_NOTIFY_CLOCKS` command to DMCUB with the latest clock values.

## State And Persistence Behavior

Persistent state includes SMU watermark memory/address, selected watermark table, DPM-derived `dcn31_bw_params`, power state, Z-state support, DTBCLK enable/reference, SMU version/presence, clock values, DCCG DTOs, DMCUB-notified clock state, and PMFW constraints. Destroy frees allocated watermark memory.

## Dependencies And Integration Points

It depends on DCN20 DPP DTO helpers, DCN31 SMU helpers, DCE DPREF helper, DMCUB command service, link service, Yellow Carp/MP/CLK registers, BIOS integrated info, and framebuffer allocation helpers.

## Risks

Z-state and DTBCLK sequencing depends on `safe_to_lower`; wrong ordering can affect idle residency or timing. The OTG workaround touches active timing generators and sync context for DPMS-off/virtual streams, so incorrect pipe selection can blank the wrong output. DPM parsing relies on voltage fallback logic and WCK ratio mapping. If `pstate_enabled` is false, bandwidth params remain mostly static defaults.

## Test Signals

Yellow Carp boot with DDR5 and LPDDR5, pstate-enabled/disabled debug modes, Z8/Z10 transitions, DTBCLK users, display idle entry/exit, DPMS-off and virtual-stream DISPCLK changes, DMCUB clock notification verification, watermark upload, DPM table logging, WCK ratio handling, and destroy memory cleanup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/clk_mgr/dcn31/dcn31_clk_mgr.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/clk_mgr/dcn31/dcn31_clk_mgr.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/clk_mgr/dcn31/dcn31_clk_mgr.h

## Purpose

`dcn31_clk_mgr.h` declares the DCN31 clock-manager wrapper type, watermark-set container, public callbacks, constructor, DTB reference query, and destructor.

## Important APIs, Types, And Functions

It forward-declares `struct dcn31_watermarks`, defines `struct dcn31_smu_watermark_set`, defines `struct clk_mgr_dcn31` embedding `clk_mgr_internal`, and declares `dcn31_are_clock_states_equal()`, `dcn31_init_clocks()`, `dcn31_update_clocks()`, `dcn31_clk_mgr_construct()`, `dcn31_get_dtb_ref_freq_khz()`, and `dcn31_clk_mgr_destroy()`.

## Control Flow

The header has no runtime flow. It exposes functions used by resource construction and by related DCN31 variants while keeping helper internals private.

## State And Persistence Behavior

The wrapper state persists framebuffer-backed watermark memory and its MC address beside the base clock manager. The header itself owns no state.

## Dependencies And Integration Points

It includes `clk_mgr_internal.h` and integrates DCN31-specific SMU watermark storage with the generic clock-manager callback interface.

## Risks

The embedded layout is used with `container_of()`; changing it requires implementation updates. Public declarations for update/init/equality mean derived managers may depend on DCN31 semantics, increasing compatibility pressure.

## Test Signals

Build coverage, DCN31 construction/destruction, DTB reference query, and derived-manager callback reuse tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/clk_mgr/dcn31/dcn31_clk_mgr.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/clk_mgr/dcn31/dcn31_smu.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/clk_mgr/dcn31/dcn31_smu.c

## Purpose

`dcn31_smu.c` implements the DCN31/Yellow Carp VBIOS-SMU mailbox. It wraps clock, DCFCLK, DPPCLK, idle optimization, PME, table transfer, Z-state, and DTBCLK messages with SMU-presence and pstate-debug guards.

## Important APIs, Types, And Functions

Exports include `dcn31_smu_get_smu_version()`, `dcn31_smu_set_dispclk()`, `dcn31_smu_set_dprefclk()`, `dcn31_smu_set_hard_min_dcfclk()`, `dcn31_smu_set_min_deep_sleep_dcfclk()`, `dcn31_smu_set_dppclk()`, `dcn31_smu_set_display_idle_optimization()`, `dcn31_smu_enable_phy_refclk_pwrdwn()`, `dcn31_smu_enable_pme_wa()`, DRAM address setters, DPM/watermark table transfers, `dcn31_smu_set_zstate_support()`, and `dcn31_smu_set_dtbclk()`. Internal transport helpers are `dcn31_smu_wait_for_response()` and `dcn31_smu_send_msg_with_param()`.

## Control Flow

The send helper waits for prior response, logs non-OK status, returns `-1` if busy, clears response, writes argument and message, waits for completion, handles explicit failure specially for watermark table transfer by logging and resetting the response to OK, reports timeouts, and returns C2PMSG_83. Most setters return requested clocks if SMU is absent; DCFCLK/deep-sleep and idle optimization also honor debug `pstate_enabled`. Z-state support maps DC enum values to Allow/Disallow message IDs and a parameter indicating Z10-capable states, with a debug gate that can downgrade Z10-only support to disallow.

## State And Persistence Behavior

Effects persist in PMFW clock constraints, idle optimization, Z-state permission, DTBCLK state, shared DPM/watermark table transfers, and MP mailbox registers. No dynamic state is allocated here.

## Dependencies And Integration Points

It depends on Yellow Carp MP register headers, `reg_helper`, DC logging, `dm_helpers_smu_timeout()`, debug flags in `dc`, and types/table IDs from `dcn31_smu.h`. `dcn31_clk_mgr.c` calls it during construction and updates.

## Risks

Returning requested clocks when SMU is absent can hide missing firmware interaction from higher layers. Pstate-disabled debug mode makes DCFCLK/idle calls no-ops returning `-1`. Watermark transfer failure is intentionally non-fatal, which can leave stale PMFW watermarks. Z-state downgrade behavior depends on `enable_z9_disable_interface`.

## Test Signals

SMU present/absent paths, pstate-disabled paths, clock set responses, table-transfer failure logging, timeout handling, Z-state allow/disallow with debug gate, DTBCLK toggles, idle optimization messages, and PME workaround.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/clk_mgr/dcn31/dcn31_smu.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/clk_mgr/dcn31/dcn31_smu.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/clk_mgr/dcn31/dcn31_smu.h

## Purpose

`dcn31_smu.h` defines the DCN31 PMFW interface subset and declares SMU mailbox helpers. It provides binary layouts for display clocks, DPM clocks, watermarks, custom DPM settings, metrics, table IDs, idle optimization bits, and WCK ratio metadata.

## Important APIs, Types, And Functions

Key definitions include `PMFW_DRIVER_IF_VERSION`, `FloatInIntFormat_t`, `DSPCLK_e`, `DisplayClockTable_t`, `WatermarkRowGeneric_t`, watermark constants/enums, `CustomDpmSettings_t`, DPM level counts, `WCK_RATIO_e`, `DfPstateTable_t`, `DpmClocks_t`, throttler status bits, `SmuMetrics_t`, workload bits, table IDs, `struct dcn31_watermarks`, `struct dcn31_smu_dpm_clks`, display idle bitfield/union, and all `dcn31_smu_*` prototypes.

## Control Flow

There is no runtime flow. The structures are allocated and filled by `dcn31_clk_mgr.c`, transferred with `dcn31_smu.c`, and interpreted by PMFW.

## State And Persistence Behavior

The header describes shared ABI state: DPM tables copied from SMU, watermark tables copied to SMU, DTB/Z-state/idle parameters sent by messages, and metrics/custom DPM structures used by broader PMFW consumers. Runtime ownership is outside the header.

## Dependencies And Integration Points

It is the contract between DCN31 display clock code and PMFW. The clock manager uses `DpmClocks_t`, `dcn31_watermarks`, table IDs, WCK ratio enums, and idle bitfields directly.

## Risks

ABI layout drift is high risk because padding, counts, enum values, and table IDs must match PMFW. The `PMFW_DRIVER_IF_H` guard wraps many definitions, so include-order interactions with other PMFW headers can change what is visible. The idle optimization struct is marked as copied from Van Gogh and may not be fully correct.

## Test Signals

Static ABI layout/version checks, DPM table transfer and parse validation, watermark upload acceptance, WCK ratio handling, Z-state/DTBCLK message tests, and build coverage with other PMFW headers included in different orders.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/clk_mgr/dcn31/dcn31_smu.h -->
