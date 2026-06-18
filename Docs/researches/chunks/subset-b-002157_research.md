# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_4_1_0_sh_mask.h lines 15147-17706

## Purpose

This chunk is generated AMD DCN 4.1.0 register field metadata. It contains no executable C code; it publishes preprocessor constants for bit shifts and masks used to pack and unpack fields in display-controller MMIO registers. Consumers pair these definitions with the matching register-address macros in `dcn_4_1_0_offset.h`, then access hardware through AMD display `REG_SET`, `REG_UPDATE`, `REG_GET`, `REG_READ`, `REG_WRITE`, and wait helpers.

The requested range is an artificial middle slice of a very large generated header. It starts inside the `CM2_CM_GAMCOR_RAMA_REGION_16_17` gamma-correction field block, covers the rest of the DPP2 gamma RAM A/B region metadata, then spans the DPP3 converter, cursor, scaler, color-management, gamma, memory-power, and top-level DPP fields. It then covers MPCC0 through MPCC3 plane-composition fields, MPC global/config/status fields, HUBP 3D LUT fast-load fields, the DWB mux field, and stops inside the initial `MPCC_OGAM0` output-gamma RAM A metadata.

Although this path sits under a local `ceph-client` source mirror, this file is AMDGPU display-driver ASIC metadata. It does not implement Ceph or distributed filesystem behavior.

## Important APIs, Types, And Macros

There are no functions, structs, enums, variables, includes, locks, allocation paths, or direct I/O in this chunk. The public interface is the generated macro namespace:

- `<REGISTER>__<FIELD>__SHIFT`: bit position used when encoding or decoding a field.
- `<REGISTER>__<FIELD>_MASK`: bit mask used to isolate the field in its 32-bit register.

Major register families in this range:

- `CM2_CM_GAMCOR_*`: late DPP2 gamma-correction RAM metadata. The chunk includes RAM A region pairs `18_19` through `32_33`, RAM B start/end/base/slope/offset fields for B/G/R channels, RAM B region pairs `0_1` through `32_33`, `CM_HDR_MULT_COEF`, `CM_MEM_PWR_CTRL`, `CM_MEM_PWR_STATUS`, `CM_DEALPHA`, and `CM_COEF_FORMAT`.
- `DPP_TOP2_*`: DPP2 top-level enable/reset/CRC/host-read fields.
- `CNVC_CFG3_*`: DPP3 input conversion fields for pixel format, format expansion, FP bias/scale, color keyer thresholds, alpha LUT, pre-dealpha, pre-CSC matrices and B-set matrices, coefficient format, pre-degamma, and pre-realpha.
- `CM_CUR3_*`: DPP3 cursor color, FP scale/bias, cursor matrix mode, and cursor matrix coefficient fields.
- `DSCL3_*`: DPP3 scaler fields for coefficient RAM selection/data, scaler mode, tap counts, manual replication, horizontal/vertical/chroma ratios and initial phases, black color, DSCL update/autocal, overscan, OTG blanking windows, recout and MPC sizes, line-buffer format and memory control, memory-power status, output buffer control, EASF/scaler-color matrix controls, ring-estimator and bilateral-filter controls, image-sharpening controls, noise detection, and sharpen LUT memory power.
- `CM3_CM_*`: DPP3 color-management fields for post-CSC matrices, bias, gamma-correction LUT control/data/index, RAM A/B PWL region configuration, HDR multiplier, gamma memory power, dealpha, and coefficient format.
- `DPP_TOP3_*`: DPP3 top-level enable/reset/CRC/host-read fields.
- `MPCC0_*` through `MPCC3_*`: repeated MPCC plane-compositor fields for top/bottom selection, OPP routing, blending/alpha controls, state-machine control, update-lock selection, top and bottom gains, movable color-management location, background color, memory power, and status.
- `MPC_*`: global MPC clock/reset/CRC selection and results, bypass background color, host-read rate control, DPP and miscellaneous pending-status bits, per-pipe vupdate lock set bits, HUBP 3D LUT fast-load mode/format/bias/scale fields, and `MPC_DWB0_MUX`.
- `MPCC_OGAM0_*`: start of MPCC output gamma RAM metadata, including output-gamma mode/select/current fields, LUT index/data/control fields, and RAM A start control fields through the beginning of RAM A end setup in the next chunk.

The values are hardware ABI, not ordinary software constants. For example, the many gamma PWL region registers consistently expose 9-bit LUT offsets, 3-bit segment counts, 18-bit start/base/slope-style values, 16-bit end/slope fields, and per-channel B/G/R forms. MPCC and MPC control fields are mostly small selectors, enables, status bits, IDs, and packed color/gain fields.

## Control Flow

This header has no runtime control flow. The runtime flow is supplied by DCN resource construction and hardware programming code:

1. DCN 4.0.1 resource code includes `dcn_4_1_0_sh_mask.h` with the matching offset header.
2. Register-list macros paste symbolic register and field names into generated macro names. Examples in this tree include `DPP_REG_LIST_SH_MASK_DCN401_COMMON(mask_sh)`, `MPC_COMMON_MASK_SH_LIST_DCN4_01(mask_sh)`, and `HUBP_MASK_SH_LIST_DCN401(mask_sh)`.
3. The resource layer initializes typed shift/mask tables such as `dcn401_dpp_shift`, `dcn401_dpp_mask`, `dcn401_mpc_shift`, `dcn401_mpc_mask`, and HUBP shift/mask tables by expanding those lists with `__SHIFT` or `_MASK`.
4. Runtime display code uses those tables through `reg_helper.h`. DPP setup and scaler code programs converter, pre/post CSC, cursor, scaler, gamma, memory-power, and top-level DPP fields. MPC code programs MPCC routing/blending, output gamma, gamut remap, DWB muxing, movable color-management location, and 1D/3D LUT modes. HUBP code programs the 3D LUT fast-load config and bias/scale fields.

The chunk does not encode sequencing rules. Consumers must still perform the real ordering: clock and memory power enablement before RAM access, choosing inactive gamma/LUT banks before programming, selecting the active bank only after data is loaded, respecting update locks and double-buffered state, and polling status/idle fields where the hardware contract requires it.

## State And Persistence Behavior

The macros hold no software state and persist nothing. They describe fields inside MMIO-backed display hardware state:

- DPP color pipeline state: pixel format conversion, alpha/dealpha/realpha behavior, pre-CSC and post-CSC matrices, cursor matrixing, gamma-correction PWL tables, HDR multiplier, coefficient formats, and gamma memory power.
- DPP scaler state: tap counts, scaling ratios, filter coefficients, initial phases, line-buffer configuration, recout/MPC dimensions, overscan/blanking windows, EASF and image-sharpening configuration, and scaler memory-power state.
- MPCC/MPC composition state: MPCC plane routing, blending gains, background color, MPCC memory power, update-lock selection, CRC configuration/results, pending-update status, DWB mux routing/status, and per-pipe update-lock set bits.
- HUBP fast-load state: per-HUBP 3D LUT fast-load mode/format and bias/scale fields used by DCN401 HUBP logic.
- MPCC output gamma state: output-gamma mode, active RAM selection/current fields, host LUT access control, LUT data/index registers, and RAM A PWL region geometry.

Persistence is hardware-defined. Most configuration fields remain until a modeset, plane update, explicit reprogramming, power gating, suspend/resume, or ASIC reset. Status and pending fields can be read-only, sticky, self-clearing, or timing-sensitive. Memory-power fields can gate LUT RAM visibility, so code that programs gamma or 3D LUT data must coordinate power state with register writes.

## Dependencies And Integration Points

This chunk depends on the generated DCN 4.1.0 register database and must match:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_4_1_0_offset.h` for matching MMIO register offsets.
- DCN401 display code under `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/`, especially `dpp/dcn401`, `mpc/dcn401`, `hubp/dcn401`, and `resource/dcn401`.
- Common register helpers in `reg_helper.h`, which consume the generated shift/mask tables through the `FN(reg_name, field_name)` pattern.
- Common DCN3/DCN32 color and MPC helpers reused by DCN401, including gamma PWL programming, shaper/3D LUT programming, post-1D LUT programming, output CSC/gamut remap helpers, and DWB mux helpers.
- Enum headers such as `soc24_enum.h` and older SOC enum headers, which document legal values for selector fields such as MPC config, MPCC output gamma mode, LUT RAM selection, and 3D LUT fast-load mode/format.

Concrete consumers visible in this tree include:

- `display/dc/resource/dcn401/dcn401_resource.c`, which instantiates DPP/MPC/HUBP shift and mask tables.
- `display/dc/dpp/dcn401/dcn401_dpp.c`, `dcn401_dpp_cm.c`, and `dcn401_dpp_dscl.c`, which consume DPP3 converter, color-management, gamma, cursor, scaler, and memory-power fields.
- `display/dc/mpc/dcn401/dcn401_mpc.c`, which consumes MPCC/MPC fields for movable color-management location, LUT population, LUT mode, gamut remap, 3D LUT fast-load status/select, and DWB mux behavior through inherited DCN3/DCN32 helpers.
- `display/dc/hubp/dcn401/dcn401_hubp.c`, which uses the `HUBP*_3DLUT_FL_*` fields to configure fast-load mode, format, bias, and scale.

## Risks And Edge Cases

- A wrong shift or mask compiles cleanly but corrupts hardware programming. The `REG_UPDATE` helpers rely on these constants to preserve unrelated bits while changing one field.
- Chunk boundaries are partial. The first lines are the tail of `CM2_CM_GAMCOR_RAMA_REGION_16_17`, and the final lines stop in the middle of `MPCC_OGAM0` RAM A setup. Adjacent chunks are needed for complete per-file analysis.
- Repeated blocks are copy-sensitive. DPP2/DPP3, MPCC0-3, HUBP0-3, and RAM A/RAM B gamma tables are structurally similar but not interchangeable. A token-paste typo or instance mismatch may only fail on one pipe, one plane, or one color pipeline.
- Gamma/LUT RAM programming is banked and power-sensitive. Incorrect RAM select/current fields, host access fields, memory power fields, or PWL region geometry can cause incorrect color, banding, black output, or failures that appear only after low-power transitions.
- Pending-status and update-lock bits are synchronization-critical. Misinterpreting `MPC_DPP_PENDING_STATUS`, `MPC_PENDING_STATUS_MISC`, or `*_VUPDATE_LOCK_SET*` can lead to torn updates, stuck pending state, or register changes landing in the wrong frame.
- Scaler fields interact with fixed-point formats and coefficients. Bad masks on ratios, initial phases, tap counts, coefficient RAM data, EASF, or sharpening controls can produce corruption limited to specific scaling ratios or chroma formats.
- DWB mux status and MPCC routing fields affect capture/composition topology. Bad masks here can route the wrong MPCC to writeback or leave writeback idle/busy detection unreliable.
- Fast-load fields bridge HUBP and MPC color paths. Incorrect `HUBP*_3DLUT_FL_*` masks or MPC fast-load status/select fields can underflow fast LUT loads or report completion incorrectly.

## Test Signals

Useful validation signals are mostly integration and hardware-behavior tests rather than unit tests:

- Build coverage for DCN401 display code after regenerating or modifying this header; compile errors in `dcn401_resource.c`, `dcn401_dpp*`, `dcn401_mpc*`, or `dcn401_hubp*` catch missing or renamed fields.
- Display modeset smoke tests on all available pipes, including multi-plane composition through MPCC0-3 and DPP2/DPP3 paths.
- Color-management tests that program degamma/gamma, post-CSC, output-gamma, shaper, 1D LUT, 3D LUT, and gamut-remap paths, then compare CRCs or captured frames.
- Scaling tests across RGB and YUV formats, chroma scaling, fractional scaling ratios, overscan/recout changes, EASF/image-sharpening modes, and line-buffer configurations.
- Update-lock and page-flip stress tests that watch for stuck pending bits, missed vupdate, tearing, or frame timing regressions.
- DWB capture tests validating `MPC_DWB0_MUX` routing and status after changing MPCC sources.
- Suspend/resume and low-power tests covering gamma/scaler/MPCC memory power fields and LUT RAM reprogramming after power gating.
