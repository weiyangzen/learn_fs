# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_4_2_0_sh_mask.h lines 62226-64689

## Purpose

This chunk is a generated AMD DCN 4.2.0 register shift/mask header slice. It contains no executable C logic; its public surface is a large set of preprocessor constants that map hardware register fields to bit positions (`__SHIFT`) and bit masks (`_MASK`) for DCN display MMIO programming.

The requested range starts in the middle of the `MPCC_MCM2_MPCC_MCM_SHAPER_RAMA_REGION_26_27` field list, completes the rest of MPCC MCM2 shaper/1DLUT/3DLUT/gamut-remap/memory-power/fast-load fields, contains a complete `dce_dc_mpc_mpcc_mcm3_dispdec` block for MPCC MCM3, covers global MPC configuration/status/CRC/update-lock/HUBP fast-load/DWB mux fields, and ends in the middle of `HDMI_TB_ENC_GENERIC_PACKET_CONTROL1` for the first HPO HDMI timing-buffer encoder.

Although the repository path is under a local `ceph-client` source mirror, this file is AMDGPU display-controller metadata. It does not implement Ceph or distributed filesystem behavior.

## Important APIs, Types, And Macros

There are no functions, structs, enums, variables, allocations, locks, callbacks, or direct MMIO accesses in this range. The API-like contract is the generated macro naming scheme:

- `<REGISTER>__<FIELD>__SHIFT`: least-significant bit index for a field inside a 32-bit hardware register.
- `<REGISTER>__<FIELD>_MASK`: field mask for extracting or updating that register field.

Important register-field families in this chunk include:

- `MPCC_MCM2_MPCC_MCM_SHAPER_*`: tail of shaper RAM A region metadata and complete RAM B start/end/region fields. These describe programmable piecewise shaper LUT region starts, ends, bases, LUT offsets, and segment counts for blue, green, and red channels.
- `MPCC_MCM2_MPCC_MCM_3DLUT_*`: 3D LUT mode, size/current mode, index/data writes, 30-bit data path, RAM selection, write-enable mask, read selection, output norm factor, output offsets/scales, fast-load select, and fast-load status.
- `MPCC_MCM2_MPCC_MCM_1DLUT_*`: 1D LUT mode/select/current state, host RAM selection, write/read color selection, RAM A/RAM B start slopes/bases/regions/offsets, and LUT data/index controls.
- `MPCC_MCM2_MPC_MCM_FIRST_GAMUT_REMAP_*` and `MPCC_MCM2_MPC_MCM_SECOND_GAMUT_REMAP_*`: coefficient format, remap mode/current mode, and 3x4 matrix coefficients split across A/B registers.
- `MPCC_MCM2_MPCC_MCM_MEM_PWR_CTRL`: low-power disable, force, and state fields for shaper, 3DLUT, and 1DLUT memories.
- `MPCC_MCM3_*`: the same MCM color-management surface for MPCC instance 3, starting at shaper control/offset/scale fields and continuing through shaper RAMs, 3DLUT, 1DLUT, first/second gamut remaps, memory power, and fast-load status.
- `MPC_CLOCK_CONTROL` and `MPC_SOFT_RESET`: MPC clock gate/test selections, disable controls, and soft-reset bits for shared MPC sub-blocks including mux, MPCC instances, memory power controller, CRC, and DWB mux paths.
- `MPC_CRC_*`: CRC enable, mode, stereo/interlace behavior, source selection, and AR/GB/result readback fields used for display validation/debug.
- `MPC_DPP_PENDING_STATUS` and `MPC_PENDING_STATUS_MISC`: per-DPP and miscellaneous pending-current flags for DPP, OPP, DWB, HUBP, ODM, MPC output mux, cursor, and configuration updates.
- `ADR_CFG_CUR_VUPDATE_LOCK_SET[0-3]`, `ADR_CFG_VUPDATE_LOCK_SET[0-3]`, `ADR_VUPDATE_LOCK_SET[0-3]`, `CFG_VUPDATE_LOCK_SET[0-3]`, and `CUR_VUPDATE_LOCK_SET[0-3]`: update-lock selectors for synchronizing address, configuration, cursor, and combined update domains.
- `HUBP[0-3]_3DLUT_FL_CONFIG` and `HUBP[0-3]_3DLUT_FL_BIAS_SCALE`: HUBP-side 3DLUT fast-load address, mode, format, bank select, finish, 10-bit enable, bias, and scale fields.
- `MPC_DWB0_MUX`: display writeback mux select and mux status fields.
- `HDMI_STREAM_ENC_*`: HPO HDMI stream encoder clock control, source/mux selection, clock-ramp adjuster FIFO status/control, and audio source/APG clock enable fields.
- `HDMI_TB_ENC_*`: HDMI timing-buffer encoder enable/reset, pixel format/deep color/DSC mode, packet limits, ACR packet control, VBI packet controls, GC AVMUTE/default phase state, and generic packet send/continuous/lock/line-reference fields for packet slots 0 through the beginning of slot 14.

## Control Flow

This header has no runtime control flow. It participates in compile-time construction of register access tables:

1. DCN42 resource code includes `dcn_4_2_0_offset.h` and this matching `dcn_4_2_0_sh_mask.h`.
2. Hardware-block headers define register-list and field-list macros such as `MPC_REG_LIST_DCN42`, `MPC_COMMON_MASK_SH_LIST_DCN42`, `SE_COMMON_MASK_SH_LIST_DCN42`, and HPO encoder list macros.
3. `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/resource/dcn42/dcn42_resource.c` expands offset macros (`SR`, `SRI`, `SR_ARR`, etc.) into register-address structs and expands field macros (`SF`, `SE_SF`, etc.) into shift/mask structs.
4. Runtime objects such as `struct dcn42_mpc`, `struct dcn10_stream_encoder`, and HPO encoder objects receive those register and shift/mask tables during construction.
5. Driver functions then call `REG_READ`, `REG_WRITE`, `REG_SET`, `REG_UPDATE`, `REG_GET`, and `REG_WAIT`; those helper macros use the tables generated from this header to update MMIO bitfields.

The sequencing rules for powering LUT memories, programming shaper/3DLUT data, switching gamut-remap modes, waiting for update-pending bits, running CRC, enabling HDMI stream clocks, and sending HDMI packets live in C source files and hardware documentation, not in this generated header.

## State And Persistence Behavior

The header stores no software state and persists nothing itself. It names hardware-visible state fields that are programmed or sampled by the display driver:

- MPCC MCM color state: shaper LUT RAM selection and region tables, 3DLUT mode/size/bank/data, 1DLUT mode/bank/data, gamut-remap matrices, current-mode readbacks, and output bias/scale.
- MCM memory-power state: force/disable/low-power mode and state readback for shaper, 3DLUT, and 1DLUT SRAMs.
- MPC global state: clock gating, soft resets, host-read mode, DPP and miscellaneous update-pending status, DWB mux selection, update-lock routing, and CRC configuration/results.
- HUBP fast-load state: which HUBP feeds 3DLUT fast load, the address/mode/format/bank, completion indication, 10-bit enable, bias, and scale.
- HDMI stream/timing-buffer state: stream encoder clock/reset/active status, ramp-adjuster FIFO thresholds and error status, audio muxing and APG clocking, deep-color/pixel-encoding/DSC mode, ACR and VBI packet scheduling, AVMUTE/default phase, and generic packet slot controls.

Persistence and side effects are hardware-defined. Many configuration fields remain until modeset, plane update, color-management update, stream disable, suspend/resume, power-gating, or GPU reset rewrites them. Status fields may be latched, self-clearing, write-one-to-clear, or valid only while the relevant display clock/power domain is enabled. This chunk only supplies bit positions and masks; it does not encode those access semantics.

## Dependencies And Integration Points

This file must stay synchronized with AMD's DCN 4.2.0 register database and the companion offset header:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_4_2_0_offset.h` supplies the matching register offsets and base indices.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/resource/dcn42/dcn42_resource.c` includes this header and creates DCN42 resource objects. In this chunk's area it builds `mpc_regs`, `mpc_shift`, and `mpc_mask` from `MPC_REG_LIST_DCN42` and `MPC_COMMON_MASK_SH_LIST_DCN42`, and it builds stream-encoder shift/mask tables from `SE_COMMON_MASK_SH_LIST_DCN42`.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/mpc/dcn42/dcn42_mpc.h` lists the DCN42 MPC/MCM fields consumed from this generated header, including MPCC MCM shaper, 3DLUT, 1DLUT, gamut-remap, fast-load, memory-power, DWB mux, update-lock, and CRC fields.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/mpc/dcn42/dcn42_mpc.c` programs color-management and MPC fields through these masks. Examples include MCM shaper LUT setup, RAM A/B region programming, 3DLUT fast-load selection, bit-depth programming, bias/scale programming, memory power toggling with `REG_WAIT`, and DWB mux/color-path updates.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/amdgpu_dm/amdgpu_dm_color.c` and plane/stream update paths feed DRM color state into DC plane/stream color structures that eventually cause the MPC/MCM programming using these fields.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dio/dcn42/dcn42_dio_stream_encoder.h` and `.c` consume HDMI stream-encoder related masks for HDMI stream attributes, audio clock enable, info packets, generic packets, metadata packets, and DP/HDMI stream control. This chunk's `HDMI_STREAM_ENC_*` and `HDMI_TB_ENC_*` families are part of the newer HPO HDMI/FRL-facing register surface, while legacy DIG HDMI fields are also present elsewhere in the generated header.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/resource/dcn42/dcn42_resource.h` includes HPO FRL stream encoder register-list entries for `HDMI_STREAM_ENC_AUDIO_CONTROL`, `HDMI_TB_ENC_MEM_CTRL`, and `HDMI_FRL_ENC_MEM_CTRL`, tying nearby HPO HDMI register families into DCN42 resource initialization.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dmub/src/dmub_dcn42.c` also includes the DCN42 offset and shift/mask headers for DMUB/DCN42 register access, though this particular range is mainly display color, MPC, and HDMI encoder metadata.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/soc24_enum.h` provides enum values for many named fields in this range, including MPCC MCM 3DLUT modes, RAM selections, LUT segment counts, gamut-remap formats/modes, memory-power states, HUBP 3DLUT fast-load modes, MPC CRC modes/source selections, update-lock booleans, and HDMI stream/TB encoder field values.

## Risks And Edge Cases

- These are untyped preprocessor constants. A wrong mask or shift compiles cleanly and can corrupt one hardware bitfield at runtime.
- The file is generated. Manual edits risk divergence from AMD's register database, the matching offset header, firmware expectations, and silicon documentation.
- The source chunk boundaries are artificial. The first line is only the final mask from `MPCC_MCM2_MPCC_MCM_SHAPER_RAMA_REGION_26_27`, and the final line stops before all `HDMI_TB_ENC_GENERIC_PACKET_CONTROL1` masks are present. Adjacent chunk research must be reconciled before making full-register claims.
- MPCC MCM and LUT programming is ordering-sensitive. Incorrect RAM-select, write-enable, index, region, or current-mode masks can produce bad color, stuck LUT updates, partial bank swaps, visible flicker, or invalid HDR/CTM/gamma behavior.
- Shaper and 1DLUT region fields repeat across 34 regions and RGB channels. Copy/generator mistakes can affect only one color, region pair, RAM bank, or MPCC instance, making failures mode- and content-dependent.
- 3DLUT fast-load fields cross MPCC/MPC and HUBP surfaces. Wrong source selection, address, bank, completion, format, 10-bit, bias, or scale masks can load the wrong LUT data or mark an incomplete DMA-style fast load as usable.
- Memory-power fields interact with clock gating and register programming. Incorrect force/disable/state masks can program powered-down SRAM, fail `REG_WAIT` polling, leave memory powered unnecessarily, or trigger underflow/error states.
- MPC pending-status and update-lock fields affect atomic update sequencing. Incorrect masks can make the driver believe an update has landed when it has not, or can keep updates locked/pending indefinitely.
- CRC field errors are often diagnostic-only but high impact for validation. Bad CRC source/mode/result masks can break display test automation, self-tests, and hardware debug without affecting ordinary display output.
- `MPC_SOFT_RESET` and clock-control masks are broad. A wrong bit can reset or ungate/gate an unrelated MPC sub-block, producing blank display, DWB failures, stale color state, or power regressions.
- HDMI stream encoder and timing-buffer fields are packet- and timing-sensitive. Incorrect deep-color, pixel-encoding, DSC mode, ACR, GC, AVMUTE, VBI, generic packet, or FIFO threshold/status masks can cause bad HDMI timing, missing infoframes, audio clock drift, repeated packet errors, or sink compatibility failures.
- HPO HDMI/FRL register naming differs from older DIG HDMI paths. Code that accidentally mixes legacy `DIG0_HDMI_*` fields with `HDMI_STREAM_ENC_*` or `HDMI_TB_ENC_*` fields can compile if names exist elsewhere but target the wrong hardware block.

## Test Signals

Useful validation combines generated-header consistency checks with runtime display behavior:

- Build AMDGPU DCN42 display support. Missing or renamed macros should surface in `dcn42_resource.c`, `dcn42_mpc.h`, `dcn42_mpc.c`, `dcn42_dio_stream_encoder.h`, `dcn42_dio_stream_encoder.c`, and HPO/FRL resource initialization paths.
- Mechanically compare this range against the authoritative DCN 4.2.0 register-field database. Every `_MASK` should have the expected paired `__SHIFT` and every register in the chunk should have a matching offset/base-index entry in `dcn_4_2_0_offset.h`.
- Run repeated-instance checks across `MPCC_MCM2` and `MPCC_MCM3`, including shaper RAM A/B regions `0_1` through `32_33`, 1DLUT RAM A/B regions, 3DLUT controls, gamut-remap coefficient registers, memory-power fields, and fast-load fields. Allow the intentional partial boundary at `MPCC_MCM2_SHAPER_RAMA_REGION_26_27`.
- Exercise DRM color-management paths that program plane/stream CTM, shaper LUTs, 1D LUTs, 3D LUTs, HDR transfer functions, and gamut remap. Expected signals are correct visual output, successful modesets, no color banding/regression, and stable bank switching.
- Test 3DLUT fast-load with each HUBP/MPCC combination used by DCN42. Expected signals include fast-load completion, no soft/hard underflow status, correct bias/scale, and expected output after bank swap.
- Validate suspend/resume, GPU reset recovery, and power-management paths with color-management enabled. Expected signals are memory-power state readbacks that settle, no `REG_WAIT` timeouts, and no lost LUT state after reprogramming.
- Exercise MPC CRC setup/readback in one-shot and continuous modes over DPP/OPP/DWB-related sources where supported. Expected signals are stable, repeatable CRC results and correct enable/source/mode behavior.
- Exercise atomic plane updates, cursor movement, DWB capture, and multi-pipe modes while watching pending-status/update-lock behavior. Expected signals are no stuck pending bits, no stale cursor/address/config updates, and correct DWB mux output.
- Exercise HDMI 2.x/FRL-capable and non-FRL sink modes across deep color, RGB/YCbCr encodings, DSC on/off, audio enabled/disabled, HDR/AVI/vendor/SPD/infoframe updates, AVMUTE transitions, hotplug, and modesets. Expected signals are stable video, correct packet delivery, no ACR/audio drift, and no ramp-adjuster FIFO overflow/underflow statuses.

## Cross-Chunk Notes

The previous chunk owns most of `MPCC_MCM2_MPCC_MCM_SHAPER_RAMA_REGION_26_27`; this chunk begins with only the `REGION27_NUM_SEGMENTS_MASK` tail and then continues from `REGION_28_29`. The next chunk should continue `HDMI_TB_ENC_GENERIC_PACKET_CONTROL1` after the `HDMI_GENERIC10_CONT_MASK` line and likely cover the remaining HPO HDMI packet/encoder registers. The final per-file research document should merge these boundaries before summarizing full MPCC MCM2 or HDMI TB encoder register coverage.
