# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/hwss/dcn42/dcn42_hwseq.c

## Purpose
`dcn42_hwseq.c` implements the DCN 4.2 hardware sequencer deltas on top of DCN401. It provides DCN42-specific hardware initialization, MPCC blending, RMCM color programming, bandwidth wrappers with driver power gating, root-clock and block power control, stereo setup, DMUB hardware locking policy, and boot power-down handling.

## Important APIs and Functions
- `dcn42_init_hw()` is the DCN42 boot/resume hardware initializer. It closely follows DCN401 init but differs in clock-gating programming, request-limit channel source, missing `dcn401_initialize_min_clocks()` call in the accelerated-mode block, extra null checks on link encoders, and PG status initialization/debug logging.
- `dcn42_update_mpcc()` programs MPCC blending for DCN42, using 12-bit-looking alpha/gain defaults (`0xfff`) and direct MPC insert/remove/update operations.
- `dcn42_program_cm_hist()` forwards plane color histogram controls to DPP.
- `dcn42_set_mcm_luts()` calls `dcn401_set_mcm_luts()` for MCM and optionally adds RMCM fast-load programming through `dcn42_program_rmcm_luts()`.
- `dcn42_prepare_bandwidth()` and `dcn42_optimize_bandwidth()` wrap DCN401 bandwidth transitions with block ungate/gate and root-clock sequencing.
- `dcn42_calc_blocks_to_gate()` and `dcn42_calc_blocks_to_ungate()` compute `struct pg_block_update` masks for DIO, HPO, HUBP, DPP, MPCC, DSC, OPP, OPTC, DPSTREAM, PHYSYMCLK, DCCG/DCIO/DCHUBBUB/DCHVM/DCOH, based on current and target resource state.
- `dcn42_hw_block_power_up()`, `dcn42_hw_block_power_down()`, and `dcn42_root_clock_control()` execute PG controller and root-clock operations in DCN42-specific order.
- `dcn42_dmub_hw_control_lock()` extends lock requirements beyond FAMS2/cursor offload by consulting `dmub_hw_lock_mgr_does_context_require_lock()`.
- `dcn42_power_down_on_boot()` powers down BIOS-left-enabled display hardware and asks the clock manager for low-power state.

## Control Flow and State Behavior
DCN42 init mutates the same broad state as DCN401 init: clock capabilities, reference clocks, link active/FEC/symclk state, panel and ABM state, DMUB caps, FAMS2 enable compatibility, and bandwidth bounding boxes. It additionally initializes `pg_cntl` status and prints optional PG status debug logs.

The bandwidth path is the main DCN42 behavioral difference. Before DCN401 prepare-bandwidth work, DCN42 calculates blocks that must be powered/root-clocked on for the target context and powers them up. After DCN401 optimize-bandwidth work, it calculates unused blocks and powers/root-clocks them down. The gate/ungate calculations persist only in the local `pg_block_update` mask, but the called PG functions update hardware power state and PG controller state.

RMCM programming is conditional on a stream-level RMCM 3D LUT allocation. It requires MPC RMCM shaper/3DLUT functions and HUBP fast-load support. It programs shaper LUT data, configures fast-load 3DLUT parameters, programs HUBP DMA config/address, and power-cycles the RMCM shaper/3DLUT block around configuration.

## Dependencies and Integration Points
DCN42 reuses many DCN401 functions through `dcn42_init.c`, so this file is intentionally a delta layer. It depends on `pg_cntl` callbacks for driver power gating, `dccg` callbacks for DSC/root clocks, DCN35 root-clock helpers, DMUB hardware lock manager helpers, DC stream private helpers for RMCM LUT lookup, and resource/pipe topology state from `dc_state`.

## Risks and Edge Cases
- Power-gating mask correctness is critical. A missed ungate can cause programming a powered-down block; a missed gate wastes power or conflicts with IPS.
- `dcn42_calc_blocks_to_gate()` has a local `hpo_frl_stream_enc_acquired` initialized false and never set in this file, so HPO gating currently depends only on HPO DP acquisition.
- Gate/ungate arrays use resource instance indices from pipe resources; resource remapping bugs can target the wrong hardware block.
- RMCM LUT programming currently uses `lut_bank_a = true` with a TODO to read from hardware, so bank conflicts are a risk during dynamic updates.
- `dcn42_program_rmcm_luts()` does not propagate its return value through `dcn42_set_mcm_luts()`; the MCM result is returned even if RMCM fails.
- Header/footer comments indicate no sequential ONO order for DCN42, but hardware PG ordering still matters for DIO/HPO/DSC/HUBP/DPP/plane/OTG domains.

## Test Signals
- Boot/resume and headless boot with BIOS-enabled DIG, including `power_down_on_boot()` and low-power clock assertion.
- Driver PG tests while adding/removing streams, planes, HPO DP, DSC, DIO encoders, disconnected links, and active streams.
- RMCM and MCM color tests with shaper enabled, DMA 3D LUT enabled, unsupported HUBP/MPC callbacks, missing stream RMCM allocation, and repeated LUT updates.
- MPO blending/global alpha/per-pixel alpha format tests for `dcn42_update_mpcc()`.
- PSR/Replay/FAMS2/cursor-offload scenarios that require or skip DMUB hardware locks.
- Stereo programming on timing generator and OPP.
