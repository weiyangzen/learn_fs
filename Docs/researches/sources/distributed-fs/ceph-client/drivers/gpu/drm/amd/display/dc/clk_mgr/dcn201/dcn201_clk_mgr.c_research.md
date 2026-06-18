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
