# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_0_1_sh_mask.h lines 17408-19930

## Purpose

This chunk is generated AMD DCN 3.0.1 display-controller register field metadata. It contains no executable C logic; it publishes preprocessor constants for bit shifts and masks used to pack and unpack fields in DCN 3.0.1 MMIO registers. Consumers include this header with `dcn_3_0_1_offset.h` so register-table code can combine an address macro with the matching `__SHIFT` and `_MASK` constants.

The requested range starts at the tail of the DPP2 converter config block, covers DPP2 cursor, scaler, color-management, and DC perfmon field definitions, then starts the corresponding DPP3 top, converter, cursor, scaler, and color-management field definitions. The range is intentionally a chunk of a much larger generated header; the final line stops inside the DPP3 `CM3_CM_POST_CSC_B_C11_C12` register definition.

Although this source tree is under a local `ceph-client` mirror, this file is AMDGPU display-driver hardware metadata. It does not implement Ceph or distributed filesystem behavior.

## Important APIs, Types, And Macros

There are no functions, structs, enums, variables, includes, allocation paths, or locks in this range. The interface is the generated macro namespace:

- `<REGISTER>__<FIELD>__SHIFT`: the least-significant bit position for a register field.
- `<REGISTER>__<FIELD>_MASK`: the 32-bit field mask before shifting or extraction.

Major field families in this chunk:

- `CNVC_CFG2_PRE_DEGAM` and `CNVC_CFG2_PRE_REALPHA`: the end of DPP2 converter pre-degamma and realpha controls.
- `CNVC_CUR2_CURSOR0_*`: DPP2 cursor enable/mode, expansion, pixel inversion, ROM enable, alpha modulation, update-pending status, palette colors, and floating-point cursor scale/bias.
- `DSCL2_*`: DPP2 scaler coefficient RAM selection/data, scaler mode, tap counts, 2-tap sharpness/hardcoded coefficient controls, manual replication, horizontal/vertical scale ratios and initial phases for luma and chroma, black color, update-pending status, autocalibration, overscan, OTG blanking snapshots, recout/MPC sizes, line-buffer format/partition/counters, scaler memory power, output-buffer control, and output-buffer memory power.
- `CM2_*`: DPP2 color management fields for bypass/update state, post-CSC matrices, gamut remap matrices, bias, gamma correction (`GAMCOR`), blending gamma (`BLNDGAM`), HDR multiplier, memory power/status, dealpha, coefficient format, shaper LUTs, 3D LUT controls/data/output normalization, and test/debug access.
- `DC_PERFMON12_*`: DPP2 perfmon counter control, counter state, run/stop selection, count-off interrupts, counter interrupt status/ack bits, and high/low count-value reads.
- `DPP_TOP3_*`: DPP3 DPP top-level clock enables/gates, soft reset controls for CNVC/DSCL/CM/OBUF, CRC value/control fields, and host-read rate control.
- `CNVC_CFG3_*` and `CNVC_CUR3_*`: DPP3 converter surface format, alpha-plane enable, format expansion/conversion/bypass/crossbar, float conversion bias/scale, color keyer, alpha LUT, pre-dealpha, pre-CSC matrices, pre-degamma, realpha, and cursor fields.
- `DSCL3_*`: DPP3 scaler and output-buffer fields mirroring the DPP2 DSCL structure.
- `CM3_CM_CONTROL`, `CM3_CM_POST_CSC_CONTROL`, and the visible `CM3_CM_POST_CSC_*` registers: the beginning of DPP3 color-management bypass/update and post-CSC field definitions.

The repeated `RAMA` and `RAMB` blocks under `CM2_CM_GAMCOR`, `CM2_CM_BLNDGAM`, and `CM2_CM_SHAPER` describe double-buffered LUT programming metadata. Each RAM bank has start, slope, base, end, offset, and region-pair fields. Region macros cover pairs `0_1` through `32_33`, with LUT offsets and segment-count fields packed into one register per pair.

## Control Flow

This header has no runtime control flow. Runtime sequencing is supplied by AMDGPU display code:

1. DCN 3.0.1 resource and DMUB code include `dcn/dcn_3_0_1_offset.h` and this `dcn/dcn_3_0_1_sh_mask.h`.
2. Register-table macros build per-block register, shift, and mask tables. In `dcn301_resource.c`, `DPP_REG_LIST_DCN30(id)` builds DPP register addresses while `DPP_REG_LIST_SH_MASK_DCN30(__SHIFT)` and `DPP_REG_LIST_SH_MASK_DCN30(_MASK)` initialize DPP field metadata.
3. DMUB support in `dmub_dcn301.c` uses `FD_MASK(reg, field)` and `FD_SHIFT(reg, field)` to populate firmware-facing register field tables.
4. Hardware code later uses these tables through register helpers such as field update/extract macros to program converter, cursor, scaler, color-management, LUT, perfmon, clock/reset, CRC, and debug registers.

The macros do not encode ordering requirements. Consumers still have to sequence DPP clock enable, soft reset, scaler coefficient loading, double-buffered LUT RAM selection, color-pipeline updates, perfmon start/stop/ack handling, and modeset or power-management transitions correctly.

## State And Persistence Behavior

This chunk stores no software state and persists nothing. It describes bit layouts for MMIO-backed hardware state.

The represented hardware state includes:

- DPP2 and DPP3 pixel-converter state for input format, alpha behavior, pre-CSC, pre-degamma, channel crossbar, color keying, and cursor composition.
- DPP2 and DPP3 scaler state for coefficient RAM contents, scaler modes, phase/ratio values, line-buffer sizing, overscan/recout geometry, memory power, and output-buffer behavior.
- DPP2 color-management state for post-CSC, gamut remap, gamma correction, blending gamma, shaper LUTs, 3D LUTs, coefficient formats, HDR multiplier, debug access, and RAM bank selection.
- DPP2 perfmon counter state, including event selection, counter modes, count-off interrupt status/ack bits, and high/low count reads.
- DPP3 top-level DPP clock-gating, reset, CRC, and host-read controls.

Persistence is hardware-defined. Configuration registers generally retain values until a modeset, pipe disable, power gating, suspend/resume, ASIC reset, or driver reprogramming. Status, update-pending, interrupt, ack, memory-power-state, debug, CRC, and counter fields may be read-only, sticky, self-clearing, or write-one-to-clear depending on the register semantics. This generated header only names bit positions and masks; it does not distinguish those behavior classes.

## Dependencies And Integration Points

This chunk depends on AMD's generated DCN 3.0.1 register database and must match the companion offset header:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_0_1_offset.h`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/resource/dcn301/dcn301_resource.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dmub/src/dmub_dcn301.c`

Important consumers are the DCN 3.0 display-pipe code paths reused by DCN 3.0.1:

- DPP/CNVC/CUR/DSCL/CM programming through `dcn30/dcn30_dpp.*` and transform/color-management helpers.
- Resource construction in `dcn301_resource.c`, which instantiates four DPP register tables (`dpp_regs(0)` through `dpp_regs(3)`) and their shared shift/mask tables from the generated macros.
- DMUB register service initialization in `dmub_dcn301.c`, where generated field masks and shifts are exported into firmware-service register descriptors.

The integration pattern is token-pasted field construction. Higher-level macros refer to logical `(reg, field)` pairs and expand to names such as `DSCL2_SCL_MODE__DSCL_MODE_MASK`, `CNVC_CFG3_FORMAT_CONTROL__CNVC_BYPASS__SHIFT`, or `CM2_CM_3DLUT_READ_WRITE_CONTROL__CM_3DLUT_RAM_SEL_MASK`. A typo in either the generated name or the table macro normally becomes a compile error, but a wrong numeric mask or shift can compile and corrupt runtime register programming.

## Risks And Edge Cases

- Numeric field drift is the central risk. These are untyped constants; a wrong shift or mask can compile cleanly while updating or reading the wrong bits in a live display register.
- The register namespaces are highly repetitive. DPP2 and DPP3 fields are structurally similar, and DPP2 color-management RAMA/RAMB bank definitions repeat across `GAMCOR`, `BLNDGAM`, and `SHAPER`. Copy-generation errors can affect only one pipe, one RAM bank, one color channel, or one LUT region pair.
- Chunk boundaries are artificial. The first visible macros are the tail of `CNVC_CFG2_PRE_DEGAM`, and the final visible register is incomplete for DPP3 color management. Adjacent chunks are required for whole-file claims.
- Double-buffered LUT fields are sequencing-sensitive. Wrong RAM select/current/read-select/write-enable fields can program an inactive bank, read the wrong bank, or expose partially updated gamma/shaper/3D-LUT state.
- Scaler ratio/init/tap and coefficient-RAM fields are precision-sensitive. Bad masks can cause underflow, cropped/shifted output, chroma misalignment, bad sharpness, or artifacts that only appear on scaled, interlaced, chroma-subsampled, or multi-plane formats.
- Power and reset fields are high risk. Incorrect DPP clock-gate, soft-reset, DSCL memory-power, OBUF memory-power, or CM memory-power fields can make later register writes ineffective or stall a pipe.
- Status and ack fields must be handled with the correct semantics by consumers. Perfmon interrupt ACK/status, update-pending, memory-power-state, CRC one-shot pending, and test/debug fields can be read-only, sticky, or write-one-to-clear.
- Generated headers are ASIC-specific. Values that match nearby DCN 3.x headers may still differ for DCN 3.0.1; broad refactors should not substitute a sibling header's field data without checking the authoritative register source.

## Test Signals

Useful validation is mostly generated-header consistency plus hardware/display behavior:

- Build AMDGPU display code with DCN 3.0.1 support enabled; missing or renamed field macros should fail in DPP, resource, and DMUB register-table construction.
- Mechanically compare this chunk with the authoritative DCN 3.0.1 register database and verify that each visible `__SHIFT` has the intended matching `_MASK` width and position.
- Validate DPP2 and DPP3 pipe bring-up on DCN 3.0.1 hardware: modeset, plane enable/disable, cursor enable/disable, format changes, alpha/color-keying, scaling, chroma formats, and suspend/resume.
- Exercise color-management paths: pre-CSC/post-CSC, gamut remap, gamma correction, blending gamma, shaper LUT, 3D LUT, HDR multiplier, coefficient-format selection, and banked LUT update/readback flows.
- Exercise scaler-specific cases: non-integer scaling, luma/chroma scaling, vertical bottom-field init, overscan, line-buffer partitioning, OBUF control, and memory-power transitions.
- Exercise DPP CRC and DC perfmon: CRC one-shot/continuous capture, perfmon event selection, counter start/stop, count-value reads, interrupt status, and interrupt ACK handling.
- Watch kernel logs and display diagnostics for blank or stuck pipes, underflow, cursor corruption, color/gamma errors, scaler artifacts, CRC mismatches, perfmon counters that do not advance, stuck update-pending bits, memory-power timeouts, and suspend/resume failures.

## Cross-Chunk Notes

Earlier chunks own the beginning of the DPP2 CNVC config register family and the rest of the DCN 3.0.1 shift/mask namespace before line 17408. Later chunks continue DPP3 color-management definitions after `CM3_CM_POST_CSC_B_C11_C12` and cover the remaining register field metadata. The final per-file research document should merge adjacent chunks before making complete claims about all DPP instances, all color-management LUT banks, or the full `dcn_3_0_1_sh_mask.h` generated header.
