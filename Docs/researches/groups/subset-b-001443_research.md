# Research group subset-b-001443

This grouped report covers AMD DC hw sequencer files for DCN32, DCN35, and DCN351. Each section is source-tree-aligned and bounded by the exact reconciliation markers for the source file it describes.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/hwss/dcn32/dcn32_hwseq.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/hwss/dcn32/dcn32_hwseq.c

## Purpose
`dcn32_hwseq.c` implements the DCN 3.2 display hardware sequencing overrides used by the AMD Display Core. It provides the generation-specific operations for DSC and HUBP power gating, MALL/CAB idle scanout, SubVP/phantom pipes, color LUT programming, DSC/ODM programming, pixel-rate divider selection, link-output shutdown, init-time hardware bring-up, and bandwidth preparation.

## Important APIs, types, and functions
- Public hwseq hooks include `dcn32_init_hw`, `dcn32_apply_idle_power_optimizations`, `dcn32_prepare_bandwidth`, `dcn32_program_outstanding_updates`, `dcn32_unblank_stream`, `dcn32_disable_link_output`, and `dcn32_interdependent_update_lock`.
- Private hwseq hooks include `dcn32_dsc_pg_control`, `dcn32_hubp_pg_control`, `dcn32_enable_power_gating_plane`, `dcn32_update_odm`, `dcn32_update_mall_sel`, `dcn32_update_force_pstate`, `dcn32_resync_fifo_dccg_dio`, and transfer-function helpers.
- MALL/CAB helpers `dcn32_check_no_memory_request_for_cab` and `dcn32_calculate_cab_allocation` derive DMUB CAB actions and cache ways from the current `dc_state`.
- Color functions program DPP degamma and MPC 1D LUT, shaper, 3D LUT, and output gamma through `dpp->funcs` and `mpc->funcs`.
- SubVP functions coordinate driver DMUB hardware locks, phantom viewport updates, phantom stream enable/disable, and topology transition checks.

## Control flow
Initialization starts with clock manager and DCCG setup, optional BIOS golden init/VGA disable, memory low-power defaults, reference-clock discovery, link encoder initialization, plane power-gating enablement, DP blanking, pipe shutdown or accelerated-mode preservation, self-refresh enablement, minimum clock programming, idle optimization reset/re-enable, audio/panel/ABM init, DIO memory power, clock gating, watermark and p-state controls, CRB/request-limit programming, and DMUB capability probing. Runtime programming is callback-driven through the DC hwseq vtables: commit paths call bandwidth preparation, power/clock controls, plane and stream programming, DSC/ODM setup, MALL configuration, and SubVP/phantom helpers depending on the new context.

## State and persistence behavior
The file mutates live hardware registers through `REG_*` macros and updates software-visible state such as `dc->caps.dmub_caps`, `dc->debug.force_disable_subvp`, `dc->debug.disable_fpo_optimizations`, stream/link active state, FEC state, PHY `symclk_state`, HUBP MALL selection, HUBP p-state force bits, DPP cached LUT parameters, and pipe update flags. Persistent hardware state across transitions includes DSC power-gate state, MALL/CAB allocation, DCCG pixel dividers, DSC/ODM topology, blank pattern generators, and phantom pipe topology. DMUB commands are used for CAB idle optimization, SubVP setup, p-state delegation, and hardware locks.

## Dependencies and integration points
This code integrates with common DC resources (`dc`, `dc_state`, `pipe_ctx`, `resource_pool`), DCCG, HUBP, Hubbub, DPP, OPP, MPC, DSC, timing generators, link services, DMUB services, DMCU, ABM, panel control, audio, BIOS tables, and DML-derived bandwidth results. It inherits substantial behavior from DCN10/20/30/31 helpers and is selected by `dcn32_init.c`.

## Risks and edge cases
Register access ordering is sensitive: DSC power gating temporarily enables `DC_IP_REQUEST_CNTL`, DSC programming avoids DTO clocks below the 48 MHz pixel-clock threshold, link disable keeps SYMCLK alive when OTG still references it, and SubVP locks must be paired correctly. CAB/MALL entry is blocked for PSR combinations, stereo 3D, TMZ surfaces, and oversized allocations. Firmware capability probing can disable FAMS2/SubVP/FPO paths for older DMUB firmware, so tests must cover firmware-version dependent behavior.

## Test signals
Useful signals include successful modesets on DCN32, DSC enable/disable with ODM and low pixel clocks, SubVP and phantom stream transitions, PSR/MALL idle entry and exit, eDP seamless boot, TMDS link disable while OTG uses SYMCLK, DP 128b/132b and legacy DP pixel-rate dividers, watermark/p-state changes, and absence of underflow or register-access hangs during bandwidth transitions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/hwss/dcn32/dcn32_hwseq.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/hwss/dcn32/dcn32_hwseq.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/hwss/dcn32/dcn32_hwseq.h

## Purpose
`dcn32_hwseq.h` declares the DCN32 generation-specific hw sequencer entry points implemented in `dcn32_hwseq.c` and consumed by `dcn32_init.c` and derivative generations.

## Important APIs, types, and functions
The header exports power-gating controls, idle optimization, SubVP and phantom helpers, MCM color functions, init and bandwidth hooks, ODM/DSC programming, DCCG pixel divider helpers, link-output disable, and update-lock helpers. Types are intentionally forward-referenced through `hw_sequencer_private.h`, including `struct dc`, `struct dc_state`, `struct pipe_ctx`, `struct dc_link`, `struct link_resource`, and `union block_sequence_params`.

## Control flow
This header has no runtime control flow. Its declarations define the compile-time contract used to populate public `hw_sequencer_funcs` and private `hwseq_private_funcs` tables.

## State and persistence behavior
The header owns no state. The declared functions mutate live DC hardware, DMUB state, pipe context fields, link PHY state, and DC capability/debug flags in the corresponding C implementation.

## Dependencies and integration points
It depends on `hw_sequencer_private.h` for callback table and core display types. It is included by DCN32 init code and by newer generations, such as DCN35/DCN351 init paths, that reuse DCN32 color, pixel-divider, link, or DSC status behavior.

## Risks and edge cases
The header declares `dcn32_cab_for_ss_control`, but the matching implementation is not present in the read source file, so any consumer would require a definition elsewhere or fail at link time. The broad declaration set also means signature drift affects multiple generations that reuse these helpers.

## Test signals
Build coverage is the primary test signal: DCN32 and derivative ASIC objects must compile and link. Runtime signals come indirectly from all vtable hooks that bind these declarations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/hwss/dcn32/dcn32_hwseq.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/hwss/dcn32/dcn32_init.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/hwss/dcn32/dcn32_init.c

## Purpose
`dcn32_init.c` constructs the public and private hw sequencer function tables for DCN32. It is the binding layer that makes the DCN32-specific implementation active inside `dc->hwss` and `dc->hwseq->funcs`.

## Important APIs, types, and functions
The file defines `dcn32_funcs`, `dcn32_private_funcs`, and `dcn32_hw_sequencer_init_functions`. Public hooks bind `dcn32_init_hw`, `dcn32_unblank_stream`, `dcn32_prepare_bandwidth`, `dcn32_apply_idle_power_optimizations`, `dcn32_commit_subvp_config`, phantom stream hooks, DSC PG update, topology transition checks, pixel-divider calculation, and outstanding-update programming. Private hooks bind DCN32 transfer functions, power-gating, ODM/DSC, MALL, p-state, FIFO resync, DP pixel-rate policy, init blank, and inherited DCN10/20/30 helpers.

## Control flow
Construction is simple assignment: `dcn32_hw_sequencer_init_functions` copies the static public table into `dc->hwss` and the private table into `dc->hwseq->funcs`. Runtime behavior is entirely through later indirect calls.

## State and persistence behavior
This file initializes the callback state stored on the `dc` object. Those function pointers persist for the lifetime of the DC instance and define which generation-specific operations will be used by modeset, bandwidth, plane, stream, idle, and teardown paths.

## Dependencies and integration points
The table composes helpers from DCE110 and DCN10/20/21/30/31/32 plus a DCN401 include. It integrates DCN32 code into the common Display Core dispatch layer without duplicating inherited behavior.

## Risks and edge cases
Misbinding a callback can route a DCN32 ASIC through incompatible register sequences. Several entries are intentionally `NULL`, such as `apply_ctx_for_surface` and `does_plane_fit_in_mall`; callers must handle those omissions. The table also relies on private functions matching hardware capabilities such as DSC count, DPP/HUBP domains, DMUB support, and SubVP support.

## Test signals
Compile/link coverage catches missing symbols. Runtime validation should include modeset, plane update, idle optimization, DSC/ODM, SubVP, phantom, and link-disable scenarios that exercise the table entries rather than only direct unit-style calls.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/hwss/dcn32/dcn32_init.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/hwss/dcn32/dcn32_init.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/hwss/dcn32/dcn32_init.h

## Purpose
`dcn32_init.h` exposes the DCN32 hw sequencer construction entry point.

## Important APIs, types, and functions
The only API is `dcn32_hw_sequencer_init_functions(struct dc *dc)`. The file forward-declares `struct dc` and uses a normal include guard.

## Control flow
The header has no runtime control flow. It allows resource construction code to call the DCN32 vtable initializer.

## State and persistence behavior
No state is owned here. The declared function persists callback assignments into the `dc` object when called.

## Dependencies and integration points
This header is included by DCN32 resource construction or generation selection code that needs to install the DCN32 hwseq table.

## Risks and edge cases
The interface is small, so the main risk is selecting the wrong generation constructor for an ASIC or failing to call it before DC paths invoke `dc->hwss`.

## Test signals
Build coverage and successful DCN32 probe/init are the relevant signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/hwss/dcn32/dcn32_init.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/hwss/dcn35/dcn35_hwseq.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/hwss/dcn35/dcn35_hwseq.c

## Purpose
`dcn35_hwseq.c` implements DCN 3.5 hardware sequencing on top of inherited DCN32/DCN31 behavior. Its main additions are DCN35 initialization, root-clock gating, block power-gate decisions and sequences, DCN35-specific idle optimization constraints, plane disable/enable handling, ODM/DSC programming differences, DRR/static-screen controls, cursor offload coordination with DMUB, and a TMDS/SYMCLK-aware link disable path.

## Important APIs, types, and functions
- Initialization and boot: `dcn35_init_hw`, `dcn35_power_down_on_boot`, `dcn35_z10_restore`, and `dcn35_init_pipes`.
- Power/clock management: `dcn35_calc_blocks_to_gate`, `dcn35_calc_blocks_to_ungate`, `dcn35_hw_block_power_down`, `dcn35_hw_block_power_up`, `dcn35_root_clock_control`, `dcn35_dpp_root_clock_control`, `dcn35_dpstream_root_clock_control`, `dcn35_physymclk_root_clock_control`, `dcn35_set_dmu_fgcg`, and `dcn35_setup_hpo_hw_control`.
- Plane and pipe operations: `dcn35_enable_plane`, `dcn35_plane_atomic_disable`, `dcn35_disable_plane`, `dcn35_update_odm`.
- Timing/panel features: `dcn35_set_drr`, `dcn35_set_static_screen_control`, `dcn35_set_long_vblank`, and `dcn35_is_dp_dig_pixel_rate_div_policy`.
- Cursor offload: `dcn35_abort_cursor_offload_update`, `dcn35_begin_cursor_offload_update`, `dcn35_commit_cursor_offload_update`, `dcn35_update_cursor_offload_pipe`, `dcn35_notify_cursor_offload_drr_update`, and `dcn35_program_cursor_offload_now`.

## Control flow
`dcn35_init_hw` initializes clocks, BIOS/DMUB golden state, DCCG, reference clocks, physical link encoders, DP/eDP blanking, Hubbub, pipe reset, self-refresh, audio/panel/ABM, DIO memory power, HPO hardware control, clock gating, watermarks, p-state controls, request limits, DMUB capabilities, and PG status. During bandwidth preparation, `dcn35_prepare_bandwidth` computes blocks to ungate, enables root clocks, powers up hardware blocks, then delegates to `dcn20_prepare_bandwidth`. During optimization, `dcn35_optimize_bandwidth` delegates to DCN20 optimization, computes unused blocks to gate, powers them down, and then disables root clocks. Plane disable waits for MPCC disconnect, clears GSL, gates HUBP/DPP clocks, resets blocks, clears pipe resources, and handles phantom OTG disable.

## State and persistence behavior
The file mutates `pg_block_update` masks, hardware PG domains through `pg_cntl`, DCCG root clock state, HUBP/DPP `power_gated` and cursor-offload flags, pipe resource pointers, stream/link active state, DMUB capability fields, ABM/panel state, DIO memory power, HPO control, static screen controls, DRR registers, and DMUB cursor offload shared memory write indices. Power-gating state is persistent across bandwidth optimizations and must be restored by prepare-bandwidth or hardware-release paths.

## Dependencies and integration points
Dependencies include DCE/DCN hwseq helpers, DCCG, Hubbub, HUBP, DPP, OPP, MPC, DSC, timing generator, link services, link encoder config, VPG, I2C, DMUB outbox/shared state, DMCU, panel control, ABM, and `pg_cntl`. `dcn35_init.c` installs these functions into public/private vtables and reuses many DCN32 functions for color and pixel-divider behavior.

## Risks and edge cases
Power sequencing is the highest-risk area. `calc_blocks_to_gate` and `calc_blocks_to_ungate` must match actual resource ownership, especially sequential ONO, DSC-to-HUBP/DPP coupling, phantom pipes, fused pipe counts, HPO, OPTC domain 24, and eDP presence. Cursor offload uses volatile DMUB shared memory and relies on correct write-index ordering. Idle optimization is limited to one active embedded panel using PSR or Replay on link index 0. `should_avoid_empty_tu` blocks DP tunneling pixel-rate division when average pixels per TU are too low. Link disable intentionally preserves SYMCLK for TMDS when OTG still references it.

## Test signals
Test with DCN35 cold boot, accelerated boot, headless boot, seamless eDP, ODM with DSC, fused-pipe variants, idle PSR/Replay entry, IPS/Z10 restore, DP tunneling rates, HPO DP, plane add/remove, phantom pipe disable, cursor offload updates during full pipe programming, hardware release, and repeated bandwidth prepare/optimize cycles while monitoring PG debug logs and underflow counters.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/hwss/dcn35/dcn35_hwseq.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/hwss/dcn35/dcn35_hwseq.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/hwss/dcn35/dcn35_hwseq.h

## Purpose
`dcn35_hwseq.h` declares the DCN35 hw sequencer functions that supplement inherited DCN32 behavior and are bound by `dcn35_init.c`.

## Important APIs, types, and functions
The declarations cover DCN35 init, boot power-down, idle optimization, Z10 restore, pipe init, plane enable/disable, ODM, root-clock controls, power-gate mask calculation, power up/down sequencing, DRR/static-screen/long-vblank controls, DP pixel-rate policy, hardware release, cursor offload, HPO control, and link-output disable.

## Control flow
The header has no runtime control flow. It defines callable contracts for public and private hwseq vtables.

## State and persistence behavior
No state is stored in this header. Its functions operate on persistent DC object state, pipe contexts, PG masks, root clock state, DMUB shared memory, and hardware registers in the implementation.

## Dependencies and integration points
It includes `hw_sequencer_private.h`, which supplies callback table structures and core display types. It is consumed by DCN35 init code and by DCN351, which reuses most DCN35 behavior while replacing a subset of power-gating functions.

## Risks and edge cases
The header contains duplicate declarations for `dcn35_dsc_pg_control` and `dcn35_disable_link_output`. It also declares functions such as `dcn35_dsc_pg_control` and `dcn35_enable_power_gating_plane` that are not implemented in the read `dcn35_hwseq.c`, indicating either stale declarations or definitions outside this subset. Build coverage determines whether those declarations are harmless.

## Test signals
Build/link tests should catch missing declarations or definitions. Runtime tests should focus on vtable-bound paths in `dcn35_init.c` and derivative reuse by DCN351.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/hwss/dcn35/dcn35_hwseq.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/hwss/dcn35/dcn35_init.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/hwss/dcn35/dcn35_init.c

## Purpose
`dcn35_init.c` constructs the DCN35 public and private hw sequencer callback tables. It binds DCN35-specific power, plane, idle, cursor offload, and timing behavior while retaining inherited DCE/DCN helpers for stable functionality.

## Important APIs, types, and functions
The file defines `dcn35_funcs`, `dcn35_private_funcs`, and `dcn35_hw_sequencer_construct`. Notable public bindings include `dcn35_init_hw`, `dcn35_power_down_on_boot`, `dcn35_disable_plane`, `dcn35_prepare_bandwidth`, `dcn35_optimize_bandwidth`, `dcn35_set_drr`, `dcn35_set_static_screen_control`, cursor offload callbacks, `dcn35_disable_link_output`, `dcn35_z10_restore`, `dcn35_apply_idle_power_optimizations`, block gate/ungate callbacks, root-clock control, long-vblank, hardware release, and pipe change detection. Private bindings include `dcn35_init_pipes`, `dcn35_plane_atomic_disable`, root-clock controls, `dcn35_update_odm`, DCN32 color helpers, DCN314 FIFO resync, DCN35 DP pixel-rate policy, and DCN35 plane enable.

## Control flow
`dcn35_hw_sequencer_construct` installs the two static tables onto `dc->hwss` and `dc->hwseq->funcs`. After construction, common DC code dispatches through those tables for init, modeset, plane updates, bandwidth transitions, idle power, cursor updates, and release.

## State and persistence behavior
This file sets long-lived function-pointer state on `dc`. Those assignments decide all later hardware sequencing behavior for the DCN35 device instance.

## Dependencies and integration points
The table composes functions from DCE110, DCN10/20/21/30/301/31/314/32/35. It integrates DCN35 into the common Display Core without duplicating common sequence code.

## Risks and edge cases
Callback selection is hardware-critical. For example, DCN35 uses `dcn10_lock_all_pipes` instead of DCN32's SubVP-specific interdependent lock, DCN35 bandwidth power gating instead of DCN20-only behavior, and DCN35 link disable instead of DCN32 for TMDS/SYMCLK handling. `enable_plane` in the public table points to `dcn20_enable_plane` while the private table has `dcn35_enable_plane`, so call-site choice matters.

## Test signals
Probe/init on DCN35 hardware, full modeset, plane disable/enable, bandwidth optimize/prepare, cursor offload, DRR/static screen control, link disable, and hardware release should all demonstrate that the installed callback table is coherent.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/hwss/dcn35/dcn35_init.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/hwss/dcn35/dcn35_init.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/hwss/dcn35/dcn35_init.h

## Purpose
`dcn35_init.h` exposes the DCN35 hw sequencer constructor.

## Important APIs, types, and functions
The only API is `dcn35_hw_sequencer_construct(struct dc *dc)`, with `struct dc` forward-declared.

## Control flow
There is no runtime control flow in the header. It supplies the construction prototype for generation selection code.

## State and persistence behavior
No state is stored here. The declared constructor persists callback assignments in the `dc` object.

## Dependencies and integration points
The header is included wherever DCN35 resource construction needs to install the DCN35 hwseq callbacks.

## Risks and edge cases
The main risk is selecting the wrong constructor or invoking DC paths before construction. The concise interface otherwise has little local complexity.

## Test signals
Build coverage and successful DCN35 display initialization validate this header's role.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/hwss/dcn35/dcn35_init.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/hwss/dcn351/Makefile -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/hwss/dcn351/Makefile

## Purpose
The DCN351 Makefile lists the DCN351 hw sequencer objects and adds them to the AMD Display build.

## Important APIs, types, and functions
It defines `DCN351 = dcn351_hwseq.o dcn351_init.o`, expands that into `AMD_DAL_DCN351` under `$(AMDDALPATH)/dc/dcn351/`, and appends the result to `AMD_DISPLAY_FILES`.

## Control flow
There is no runtime control flow. Build-system control flow is the object list expansion that ensures both DCN351 implementation files are compiled and linked.

## State and persistence behavior
No runtime state is owned. Build state is limited to make variables contributing object files to the display driver.

## Dependencies and integration points
The file integrates the DCN351 directory into the broader AMD Display build system. The path prefix assumes the tree layout used by the surrounding display Makefiles.

## Risks and edge cases
If the object list or path prefix drifts from source layout, DCN351 symbols such as `dcn351_hw_sequencer_construct` or power-gating overrides will be missing at link time. Adding new DCN351 source files requires updating this list.

## Test signals
A successful kernel/display-driver build with DCN351 enabled is the primary signal. Link failures or missing constructor symbols indicate Makefile coverage issues.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/hwss/dcn351/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/hwss/dcn351/dcn351_hwseq.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/hwss/dcn351/dcn351_hwseq.c

## Purpose
`dcn351_hwseq.c` implements the small DCN351 override layer for hardware block gating and ONO sequencing. It reuses DCN35 calculations as a base, then enforces DCN351-specific contiguous HUBP/DPP gate and ungate behavior and custom power up/down order.

## Important APIs, types, and functions
The file defines `dcn351_calc_blocks_to_gate`, `dcn351_calc_blocks_to_ungate`, `dcn351_hw_block_power_down`, and `dcn351_hw_block_power_up`. Each operates on `struct dc`, `struct dc_state`, and `struct pg_block_update`.

## Control flow
The gate/ungate functions first call the DCN35 equivalent, then scan from the highest pipe down. When they find the first active HUBP/DPP pair that must remain powered or be powered, they force all lower-numbered HUBP/DPP entries to the same state. The power-down sequence walks pipes from high to low, gating DSC before paired HUBP/DPP, then gates the shared plane/OTG domain. The power-up sequence enables plane/OTG first, then walks low to high and ungates paired HUBP/DPP before DSC.

## State and persistence behavior
The functions mutate `pg_block_update` masks and live hardware power-gate state through `dc->res_pool->pg_cntl`. They honor `dc->debug.ignore_pg` and leave domains 22, 23, and 25 effectively always on according to comments.

## Dependencies and integration points
The implementation includes DC core/resource types, its own header, and `dcn35_hwseq.h`. It depends on DCN35 calculation semantics and on `pg_cntl` callbacks `dsc_pg_control`, `hubp_dpp_pg_control`, and `plane_otg_pg_control`. `dcn351_init.c` binds these overrides into the DCN351 public hwseq table.

## Risks and edge cases
The contiguous lower-pipe rule can intentionally keep more HUBP/DPP blocks powered than the base DCN35 calculation. This avoids invalid ONO sequencing but can reduce power savings. The high-to-low and low-to-high order must match DCN351 hardware requirements; changing it risks display hangs or power-domain violations. Missing `pg_cntl` callbacks silently skip parts of the sequence.

## Test signals
Test bandwidth optimize/prepare across pipe counts, DSC allocation changes, plane add/remove, sequential display bring-up/teardown, and `ignore_pg` debug mode. PG debug logs should show the expected DCN351 order and no underflow or register timeouts.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/hwss/dcn351/dcn351_hwseq.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/hwss/dcn351/dcn351_hwseq.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/hwss/dcn351/dcn351_hwseq.h

## Purpose
`dcn351_hwseq.h` declares the DCN351-specific power-gating override functions.

## Important APIs, types, and functions
The header exports `dcn351_calc_blocks_to_gate`, `dcn351_calc_blocks_to_ungate`, `dcn351_hw_block_power_up`, and `dcn351_hw_block_power_down`, all using `struct dc`, `struct dc_state`, and `struct pg_block_update`.

## Control flow
There is no runtime control flow in the header. The declarations are bound in `dcn351_init.c`.

## State and persistence behavior
No state is owned here. The declared functions mutate power-gate masks and hardware PG domains in the implementation.

## Dependencies and integration points
It includes `hw_sequencer_private.h` for the relevant structures and callback context. It is consumed by `dcn351_init.c`.

## Risks and edge cases
Signature changes must stay synchronized with `dcn351_hwseq.c` and the hwseq callback table. Since these functions override only power sequencing, incorrect binding would make DCN351 fall back to incompatible DCN35 behavior.

## Test signals
Build/link coverage plus runtime power-gating tests on DCN351 validate this header.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/hwss/dcn351/dcn351_hwseq.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/hwss/dcn351/dcn351_init.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/hwss/dcn351/dcn351_init.c

## Purpose
`dcn351_init.c` constructs the DCN351 hw sequencer callback tables. It mostly reuses DCN35 behavior, but binds DCN351-specific block gate/ungate and power up/down sequencing.

## Important APIs, types, and functions
The file defines `dcn351_funcs`, `dcn351_private_funcs`, and `dcn351_hw_sequencer_construct`. Public table differences from DCN35 include `dcn351_calc_blocks_to_gate`, `dcn351_calc_blocks_to_ungate`, `dcn351_hw_block_power_up`, `dcn351_hw_block_power_down`, and `dcn32_disable_link_output`. It reuses DCN35 init, boot power-down, bandwidth prepare/optimize, idle optimization, Z10 restore, DRR/static-screen/long-vblank, root-clock control, and HPO setup. Private functions reuse DCN35 pipe init, plane disable/enable, root-clock controls, ODM, and DP pixel policy plus DCN32 color and pixel-divider helpers.

## Control flow
`dcn351_hw_sequencer_construct` assigns the static public and private tables into `dc->hwss` and `dc->hwseq->funcs`. Common DC code then dispatches through these entries for all display sequencing.

## State and persistence behavior
The file persists function-pointer state on the `dc` object. It does not directly program hardware; it decides which implementation will be used later.

## Dependencies and integration points
It includes DCE/DCN helper headers from DCE110 and DCN10/20/21/30/301/31/32/35 plus the local DCN351 header. It integrates DCN351 as a derivative generation while avoiding duplication of most DCN35 logic.

## Risks and edge cases
The deliberate use of `dcn32_disable_link_output` instead of `dcn35_disable_link_output` is a behavioral difference worth testing, especially for TMDS/SYMCLK cases. DCN35 cursor offload callbacks are not present in the DCN351 public table even though many other DCN35 hooks are reused. The private table omits DCN35's `resync_fifo_dccg_dio` binding, so callers must tolerate that or use inherited alternatives.

## Test signals
Build/link validation, DCN351 probe/init, bandwidth gating transitions, link disable on DP/eDP/TMDS, plane enable/disable, ODM/DSC, idle PSR/Replay, and hardware release should confirm the table is coherent for this derivative ASIC.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/hwss/dcn351/dcn351_init.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/hwss/dcn351/dcn351_init.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/hwss/dcn351/dcn351_init.h

## Purpose
`dcn351_init.h` exposes the DCN351 hw sequencer constructor.

## Important APIs, types, and functions
The only API is `dcn351_hw_sequencer_construct(struct dc *dc)`, with `struct dc` forward-declared.

## Control flow
There is no runtime control flow. The header supplies the prototype for generation construction code.

## State and persistence behavior
No state is owned. The declared function installs persistent public/private hwseq callback tables into `dc`.

## Dependencies and integration points
This header is included by code that selects the DCN351 hw sequencer during resource construction.

## Risks and edge cases
As with the other init headers, the main risk is failing to call the constructor or calling it for the wrong ASIC generation.

## Test signals
Successful DCN351 build, probe, and display init are the practical validation signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/hwss/dcn351/dcn351_init.h -->
