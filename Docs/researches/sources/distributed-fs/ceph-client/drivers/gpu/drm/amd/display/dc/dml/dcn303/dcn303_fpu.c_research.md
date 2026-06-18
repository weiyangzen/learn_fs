# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dml/dcn303/dcn303_fpu.c

## Purpose
This file is the DCN 3.03 counterpart to the DCN302 FPU bounding-box code. It defines DCN303 IP/SoC defaults, computes synthetic DCFCLK/UCLK states from clock-manager data, applies BIOS latency overrides, and reinitializes DML for DCN303 validation.

## Important APIs, Types, And Functions
- Global descriptors: `dcn3_03_ip` and `dcn3_03_soc`.
- Private helper: `dcn303_get_optimal_dcfclk_fclk_for_uclk()` estimates optimal DCFCLK/FCLK from memory bandwidth and SoC bus characteristics.
- Public functions: `dcn303_fpu_update_bw_bounding_box()` and `dcn303_fpu_init_soc_bounding_box()`.
- DCN303-specific constants differ from DCN302 in resource counts and capabilities: two DSC/DPP/OTG-oriented defaults and no ODM 4:1 support.

## Control Flow
`dcn303_fpu_update_bw_bounding_box()` mirrors the DCN302 sequence: update memory topology from BIOS, set VCO speed, scan clock-table maxima, adjust static DCFCLK target list, compute optimal DCFCLK per UCLK, compute optimal UCLK per DCFCLK target, merge the two sequences into final states, fill per-state clock limits, then reinitialize DML. DCN303 adds a fallback in target-to-UCLK mapping: when all optimal DCFCLK values are below a target, that target is assigned the max UCLK. It also adds a low-channel-count adjustment that forces DCFCLK/FCLK to 100 MHz for qualifying low memory-speed states.

`dcn303_fpu_init_soc_bounding_box()` applies BIOS latency overrides for DRAM clock change and stutter timing.

## State And Persistence
The global `dcn3_03_soc` is persistently changed by BIOS initialization and clock updates. `dcn3_03_ip` holds static IP capability data. The update function mutates the active `dc->dml` and optionally `dc->current_state->bw_ctx.dml` through `dml_init_instance()`.

## Dependencies And Integration Points
The file depends on common DC resource and clock-manager structures, DCN303 resource definitions, and DCN20 FPU/DML initialization helpers. It integrates BIOS VRAM topology, SMU clock tables, and clock-manager VCO into the DCN303 display-mode model using `DML_PROJECT_DCN30`.

## Risks And Edge Cases
- Like DCN302, the scan loops inspect up to `MAX_NUM_DPM_LVL` entries, so unused entries must be zero-initialized.
- State-count overflow triggers `ASSERT(0)` and returns without reinitializing DML.
- The low-channel-count 100 MHz override can intentionally reduce DCFCLK/FCLK for memory speeds between 1500 and 1700 MTS, which must match platform policy.
- Unit conversion uses `memclk_mhz * 16`; incorrect clock table units would distort bandwidth modeling.
- Mutable global SoC updates persist across calls and can be affected by call ordering.

## Test Signals
Use tests that compare DCN303 against DCN302 for the special max-UCLK fallback and low-channel-count override. Cover max DCFCLK target adjustment, state overflow, BIOS channel topology, missing memory clock, carry-forward of DTBCLK/SOCCLK, latency overrides, and DML reinitialization of current and active contexts.
