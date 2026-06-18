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
