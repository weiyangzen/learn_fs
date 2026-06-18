# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_4_2_0_sh_mask.h lines 57275-59767

## Purpose

This chunk is a generated AMD DCN 4.2.0 register shift/mask header slice. It contains no executable C code; it exposes preprocessor constants that describe bit positions and masks for display-controller MMIO register fields.

The requested range contains 2,493 lines. It starts in the middle of the `MPCC_OGAM2` output-gamma block, covers the full `MPCC_OGAM3` output-gamma block, covers `MPC_OUT0` through `MPC_OUT3` output mux, denorm, and output CSC fields, covers complete `MPC_RMCM0` and almost-complete `MPC_RMCM1` reusable/movable color-management fields, and ends at the beginning of `DC_PERFMON22` performance-counter state fields. The chunk boundaries are mechanical: earlier `MPCC_OGAM2` control/RAMA fields are in the previous chunk, and most `DC_PERFMON22` fields continue in the next chunk.

Although this file is under a local `ceph-client` source mirror, this range is AMDGPU display hardware metadata. It does not implement Ceph or distributed filesystem behavior.

## Important APIs, Types, And Macros

There are no functions, structs, enums, variables, includes, allocations, locks, or direct register accesses in this range. The API surface is the generated macro convention:

- `<REGISTER>__<FIELD>__SHIFT`: the least-significant bit position for a register field.
- `<REGISTER>__<FIELD>_MASK`: the bit mask for that field within its register.

The main register-field families in this chunk are:

- `MPCC_OGAM2`: tail of output gamma instance 2, including RAMA region descriptors 6-33, all RAMB start/end/offset/region descriptors, and MPCC gamut remap mode/format plus A/B coefficient banks.
- `MPCC_OGAM3`: complete output gamma instance 3, including mode/select/PWL disable/current status, LUT index/data/control, per-channel RAMA and RAMB segmented PWL programming, offsets, and gamut remap coefficient banks.
- `MPC_OUT0` through `MPC_OUT3`: output mux selection/status, output rate/flow-control fields, denormalization mode and clamp bounds, and per-output CSC mode plus 3x4 coefficient matrices for A/B banks.
- `MPC_OCSC_TEST_DEBUG_INDEX` and `MPC_OCSC_TEST_DEBUG_DATA`: debug index/data window for output CSC diagnostics.
- `MPC_RMCM0` and `MPC_RMCM1`: shaper LUT control, RGB offsets/scales, shaper LUT index/data/write enable, shaper RAMA/RAMB region descriptors, 3D LUT mode/index/data/read-write controls, 30-bit data path, output normalization/bias/scale, gamut remap mode/format/coefficient banks, memory power controls, fast-load select/status, and top-level RMCM control.
- `DC_PERFMON22`: beginning of a display performance monitor block, covering `PERFCOUNTER_CNTL`, `PERFCOUNTER_CNTL2`, and the first `PERFCOUNTER_STATE` field.

The field names map directly into DCN 4.2 register-table construction. In particular, `MPC_RMCM0_*` names are consumed by `MPC_COMMON_MASK_SH_LIST_DCN42()` in `display/dc/mpc/dcn42/dcn42_mpc.h` and replicated for both RMCM instances by `MPC_RMCM_REG_LIST_DCN42(0/1)` in `display/dc/resource/dcn42/dcn42_resource.c`.

## Control Flow

This header has no runtime control flow. Its constants participate in compile-time table initialization:

1. DCN 4.2 display code includes `dcn_4_2_0_offset.h` and this matching `dcn_4_2_0_sh_mask.h`.
2. Resource construction macros bind register offsets, shifts, and masks into typed tables such as `dcn42_mpc_registers`, `dcn42_mpc_shift`, and `dcn42_mpc_mask`.
3. Runtime MPC code accesses those tables through AMD display register helpers such as `REG_SET`, `REG_UPDATE`, `REG_UPDATE_2`, `REG_GET`, `REG_GET_2`, `REG_GET_3`, and `REG_GET_4`.
4. Higher-level color-management paths program output gamma, gamut remap, output CSC, RMCM shaper LUT, RMCM 3D LUT, fast-load selection, and memory power by field name, while this file supplies only bit layout.

Programming order is not encoded here. Sequencing for LUT bank selection, memory power, clock ungating, fast load, modeset synchronization, debug reads, and perfmon sampling is controlled by driver code and hardware rules outside this generated header.

## State And Persistence Behavior

The file stores no software state and persists nothing itself. It describes hardware state fields that generally remain in registers until explicitly reprogrammed or reset by modeset, plane detach/attach, color-management updates, suspend/resume, power gating, GPU reset, or ASIC reset.

The chunk names several persistent display-pipeline states:

- MPCC output gamma state: active/current gamma mode, selected LUT bank, PWL disable, LUT host/read/write selection, per-channel segmented RAMA/RAMB PWL parameters, offsets, and gamut remap matrix bank state.
- MPC output state: output mux routing/status, denormalization mode, clamp windows, output rate and flow-control fields, and output CSC matrix selection and coefficients.
- RMCM state: shaper LUT mode/current mode, shaper PWL tables in RAMA/RAMB, 3D LUT mode/current mode and size, 3D LUT data/index/read/write controls, fast-load source selection and completion/underflow status, output bias/scale/norm factor, gamut remap matrices, and memory power force/disable/low-power/state bits.
- Perfmon state at the end of the chunk: event selection, counted-value selection, increment mode, hardware control/start/stop selectors, restart/interrupt enables, active/off status, and selected counter state.

Side effects are hardware-defined. Some status/current fields are readback-only or latched. Some interrupt/status bits may require write-one-to-clear semantics in adjacent perfmon registers. Memory-power and fast-load fields are especially sequencing-sensitive because the driver must power and clock memories before programming their contents.

## Dependencies And Integration Points

This generated shift/mask header must stay synchronized with the companion offset header and AMD's DCN 4.2 register database:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_4_2_0_offset.h` provides matching register offsets and base indices.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/resource/dcn42/dcn42_resource.c` includes the generated DCN 4.2 headers, initializes `mpc_shift`/`mpc_mask`, and registers two RMCM instances with `MPC_RMCM_REG_LIST_DCN42(0)` and `(1)`.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/mpc/dcn42/dcn42_mpc.h` defines `MPC_COMMON_MASK_SH_LIST_DCN42()`, which consumes the MPCC OGAM, MPC output, and RMCM shift/mask names represented here.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/mpc/dcn42/dcn42_mpc.c` programs RMCM shaper LUTs, 3D LUT size/bank/bit-depth/output bias/scale, fast-load select, memory power, and RMCM readback state through these field tables.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/mpc/dcn32/dcn32_mpc.h` and older MPC headers show the predecessor macro patterns for MPCC OGAM and output CSC fields; DCN 4.2 extends this path with RMCM fields.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/soc24_enum.h` supplies related MPCC OGAM enum values such as LUT bank selection, LUT config mode, PWL disable, read color selection, and segment count values.

Behaviorally, this range is on the user-visible color pipeline: plane composition feeds MPCC/MPC, then output gamma, gamut remap, output CSC/denorm, and RMCM shaper/3D LUT transformations affect final pixels before scanout or writeback. The perfmon fields at the end are diagnostic instrumentation rather than image-processing state.

## Risks And Edge Cases

- The constants are untyped preprocessor macros. A bad mask or shift can compile cleanly while silently programming the wrong register bits.
- The file is generated. Manual edits risk divergence from the authoritative hardware register database, the offset header, firmware expectations, and silicon documentation.
- Chunk boundaries are not semantic. This range begins after `MPCC_OGAM2` control and early RAMA fields, and stops inside `DC_PERFMON22_PERFCOUNTER_STATE`; adjacent chunk reports must be merged before making whole-block claims.
- Repeated instances are copy-sensitive. `MPCC_OGAM2`, `MPCC_OGAM3`, `MPC_OUT0-3`, and `MPC_RMCM0-1` are structurally similar, so a generator or paste error can affect only one pipe, one output, or one RMCM instance.
- LUT programming is banked and mode/current-mode based. Wrong `*_MODE`, `*_SELECT`, `*_RAM_SEL`, or `*_MODE_CURRENT` fields can display stale LUT contents, switch to the wrong bank, or report the wrong active bank.
- PWL region masks encode offsets and segment counts. Bad RAMA/RAMB region masks can make gamma/shaper curves non-monotonic, truncate a region, overflow the intended LUT span, or produce visible banding.
- Per-channel fields are easy to alias. Swapping R/G/B offset, scale, start/end, or coefficient masks can create color casts that only appear under color-managed modes.
- Matrix coefficients use paired 16-bit fields and A/B banks. Incorrect masks can corrupt only half of a coefficient register or only the inactive/active bank being flipped during modeset.
- RMCM memory-power fields gate shaper and 3D LUT memories. Programming LUT RAM while power-disabled or clock-gated can lead to lost writes, underflow status, or inconsistent readback.
- RMCM fast-load fields depend on `hubp_index`, LUT size, bit-depth, bias/scale, and bank selection. Wrong masks can connect fast load to the wrong HUBP, leave it disconnected, or misreport soft/hard underflow.
- `MPC_RMCM_CNTL` appears to gate/select RMCM participation. A wrong mask can disable the color module for a pipe or route the wrong MPC/RMCM path.
- Perfmon fields include event selection, run enable, stop/count-off controls, restart, interrupt enable, active state, and counter selector bits. Incorrect masks can make performance diagnostics misleading or cause stuck perfmon interrupts when adjacent status/ack fields are used.

## Test Signals

Useful validation combines generated-header consistency checks with runtime display/color tests:

- Build DCN 4.2 AMDGPU display support. Missing or renamed macros should surface in `dcn42_resource.c`, `dcn42_mpc.h`, and `dcn42_mpc.c`.
- Mechanically compare this range with the authoritative DCN 4.2 register database and verify every `_MASK` has the expected paired `__SHIFT`.
- Cross-check each register family against `dcn_4_2_0_offset.h`, especially instance-specific offsets for `MPCC_OGAM2/3`, `MPC_OUT0-3`, `MPC_RMCM0/1`, and `DC_PERFMON22`.
- Run repeated-instance consistency checks for `MPCC_OGAM2` versus `MPCC_OGAM3`, all `MPC_OUT` instances, and `MPC_RMCM0` versus `MPC_RMCM1`, while allowing intentional instance prefixes and chunk-boundary omissions.
- Exercise color-managed modes that program MPCC output gamma, gamut remap, output CSC, and denorm/clamp. Expected signals are correct color transforms, no channel swaps, no visible banding, and expected register readbacks.
- Test both LUT banks and mode/current-mode readback for output gamma and RMCM shaper/3D LUT paths. Bank flips should not show stale or partially programmed tables.
- Exercise RMCM shaper and 3D LUT fast-load on both RMCM instances, including 17x17x17 and 33x33x33-equivalent size selections where supported, 10-bit and non-10-bit data paths, and different HUBP sources. Watch `*_FL_DONE`, `*_FL_SOFT_UNDERFLOW`, and `*_FL_HARD_UNDERFLOW`.
- Exercise suspend/resume, rapid modesets, plane disable/enable, and memory-low-power debug settings while RMCM and OGAM LUTs are enabled. Expected signals are stable color state after resume and no lost LUT programming.
- Use debugfs or driver state dumps that call `mpc42_read_mpcc_state()` to verify RMCM fields read back coherently for instances 0 and 1.
- If perfmon support is exposed for this block, configure `DC_PERFMON22` counters for known events and confirm active/state/readback behavior matches expected display activity without spurious interrupts.

## Cross-Chunk Notes

The previous chunk should cover the beginning of `MPCC_OGAM2`, including its control, LUT index/data/control, RAMA start/end/offset, and RAMA regions 0-5. This chunk covers the rest of `MPCC_OGAM2`, all `MPCC_OGAM3`, output CSC/denorm/mux, and RMCM0/1 up to `MPC_RMCM1_MPC_RMCM_CNTL`. The next chunk should continue `DC_PERFMON22_PERFCOUNTER_STATE` and the remaining perfmon control/value/readback fields before moving into later address blocks.
