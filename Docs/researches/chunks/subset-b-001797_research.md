# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_1_2_offset.h lines 2663-5185

## Scope

This chunk covers 2,523 lines from the generated AMD DCN 3.1.2 register-offset header. The slice contains only preprocessor constants and generated address-block comments; there are no C functions, structs, enums, variables, or executable statements.

The range begins in the tail of the `dce_dc_dcbubp0_dispdec_hubpreq_dispdec` block at `regHUBPREQ0_VBLANK_PARAMETERS_1` and ends in the early part of the `dce_dc_dpp2_dispdec_dscl_dispdec` block at `regDSCL2_SCL_BLACK_COLOR`. Adjacent chunks are required to complete both the start-side `HUBPREQ0` register group and the end-side `DSCL2`/following DPP2 color-management blocks.

Within this range there are 1,196 non-`BASE_IDX` register-offset macros plus paired `*_BASE_IDX` macros. The lowest offset in the chunk is `0x064b` for `regHUBPREQ0_VBLANK_PARAMETERS_1`; the highest is `0x0fe0` for `regDSCL2_SCL_BLACK_COLOR`. Every address in this chunk uses DCN base segment index `2` after the initial file-level `BASE(reg..._BASE_IDX)` expansion.

## Purpose

This header region provides the DCN 3.1.2 symbolic MMIO offset contract for display pipe front-end and pixel-processing hardware. AMD display code includes this file with the matching `dcn_3_1_2_sh_mask.h` field header so register-table macros can resolve hardware addresses by token concatenation rather than by raw numeric constants.

The chunk maps three broad areas:

- HUBP/HUBPREQ/HUBPRET/CURSOR registers for plane pipes 0 through 3, including viewport, request-size, VMID, surface address, flip timing, prefetch, vblank/nominal delivery, cursor, metadata, line-read, memory power, and perf counter registers.
- DPP pipe registers for DPP0 and DPP1, including converter/cursor (`CNVC_CFG`, `CNVC_CUR`), scaler (`DSCL`), color-management (`CM`), DPP top, CRC, and per-DPP perfmon registers.
- The beginning of DPP2, covering `CNVC_CFG2`, `CNVC_CUR2`, and the first part of `DSCL2`.

This is a hardware description input to the driver. Its value is exact macro names and numeric offsets, not local algorithmic behavior.

## Important APIs, Types, And Constants

There are no callable APIs or C types in this chunk. The exported interface is the generated macro naming convention:

- `reg<block><instance>_<REGISTER>` gives the register offset relative to the selected DCN base segment.
- `reg<block><instance>_<REGISTER>_BASE_IDX` gives the base-index selector used by `BASE(...)` or equivalent macros in AMD display code.
- Address-block comments identify the generated hardware block and the block-local base address used by the register generator.

The most important register families in this range are:

- `regHUBPREQ0_*`, starting at `VBLANK_PARAMETERS_1`, `FLIP_PARAMETERS_*`, `NOM_PARAMETERS_*`, `PER_LINE_DELIVERY*`, `CURSOR_SETTINGS`, `REF_FREQ_TO_PIX_FREQ`, `DST_Y_DELTA_DRQ_LIMIT`, and HUBPREQ memory power registers. The earlier part of `HUBPREQ0` is outside this chunk.
- Complete `HUBP1`, `HUBP2`, and `HUBP3` front-end blocks for surface config, address/tiling config, primary/secondary viewport starts and dimensions, request-size config, clock control, VMPG config, debug registers, and measurement-window controls.
- Complete `HUBPREQ1`, `HUBPREQ2`, and `HUBPREQ3` blocks for surface pitch, VMID, primary/secondary luma and chroma surface addresses, metadata addresses, surface-in-use/earliest-in-use tracking, flip control, DCC/TMZ surface control, QoS, TTU, prefetch, vblank, flip, nominal, delivery, cursor settings, VM aperture, TLB, and memory power registers.
- `HUBPRET0` through `HUBPRET3` line-buffer/control blocks, including control, memory power, read-line controls, read-line values/status, and interrupt registers.
- `CURSOR0_0` through `CURSOR0_3` cursor blocks, including cursor control, surface address high/low, size, position, hot spot, stereo control, destination offset, cursor memory power, and display metadata data/address/QoS/status/software-control registers.
- `DC_PERFMON7` through `DC_PERFMON10` associated with the HUBP side, plus `DC_PERFMON11` and `DC_PERFMON12` associated with DPP0 and DPP1. Each perfmon block exposes counter control, counter state, perfmon control, current-value, high, and low registers.
- `CNVC_CFG0`, `CNVC_CFG1`, and `CNVC_CFG2`, covering surface pixel format, format control, floating-point bias/scale channels, color-keyer control and values, alpha 2-bit LUT, pre-dealpha, pre-CSC mode and coefficients, coefficient format, pre-degamma, and pre-realpha.
- `CNVC_CUR0`, `CNVC_CUR1`, and `CNVC_CUR2`, covering cursor control, cursor colors, and cursor floating-point scale/bias.
- `DSCL0` and `DSCL1` complete scaler blocks, plus the first part of `DSCL2`, covering coefficient RAM access, scaler mode, tap control, DSCL control, 2-tap control, manual replicate control, horizontal/vertical luma/chroma scale ratios and initial phases, black color, update/autocal, overscan, OTG blanking, recout/MPC sizes, line-buffer format/memory, DSCL/OBUF memory power, and output-buffer control.
- `CM0` and `CM1` complete color-management blocks, including dealpha, memory power/status, bias, gamma correction control/LUT, gamut remap A/B matrices, post-CSC A/B matrices, degamma/blend-gamma/shaper RAM A/B start/slope/end/base/region registers, LUT index/data/control registers, HDR multiplier coefficient, 3D LUT control/data/offset registers, and debug index/data registers.
- `DPP_TOP0` and `DPP_TOP1`, covering DPP control, soft reset, CRC values/control, and host-read control.

## Control Flow

The chunk has no runtime control flow. Its effective flow is compile-time macro expansion:

1. DCN 3.1 display code includes `yellow_carp_offset.h`, `dcn/dcn_3_1_2_offset.h`, and `dcn/dcn_3_1_2_sh_mask.h`.
2. Consumer macros such as `SR`, `SRI`, `SRIR`, and `SRII` concatenate a block name, instance id, and register name to select one of the `reg...` macros from this header.
3. The same expression adds `BASE(reg..._BASE_IDX)` to the selected offset to produce an absolute register address stored in generated register tables.
4. Runtime paths use those tables through register helpers such as `REG_READ`, `REG_WRITE`, `REG_GET`, `REG_SET`, and `REG_UPDATE`.

Concrete consumers include `display/dc/resource/dcn31/dcn31_resource.c`, which builds the `hubp_regs[]`, DPP register lists, HWSEQ registers, shifts, and masks for Yellow Carp/DCN 3.1 resources; `display/dc/irq/dcn31/irq_service_dcn31.c`, which includes the same offset/mask headers for IRQ register-table expansion; and `display/dmub/src/dmub_dcn31.c`, which uses the same include pair for DMUB register and field tables. The HUBP-specific field lists in `display/dc/hubp/dcn31/dcn31_hubp.h` and DPP lists in `display/dc/dpp/dcn30/dcn30_dpp.h` show the token names that must match these generated offsets.

## State And Persistence Behavior

The header itself stores no state and performs no persistence. It describes MMIO registers whose state is owned by DCN 3.1.2 display hardware.

The mapped HUBP/HUBPREQ/HUBPRET registers control or report plane-fetch state: surface addresses, metadata addresses, VMID selection, memory aperture/TLB behavior, request chunking, swath/viewport dimensions, flip and vblank timing, TTU/QoS behavior, prefetch timing, DCC/TMZ control, cursor fetch state, line-read state, underflow/blanking behavior, and per-block memory power. These values are normally programmed by the DC resource and hardware-sequencer paths during plane enable, flip, cursor update, bandwidth/programming updates, power transitions, and reset/recovery.

The mapped DPP/CNVC/DSCL/CM registers control or report per-pipe pixel processing: input format conversion, cursor color conversion, scaler taps and filter coefficients, viewport/output sizing, overscan and blanking, line-buffer state, color-space matrices, degamma/gamma/blend/shaper LUT RAMs, HDR multiplier, 3D LUT state, CRC, top-level DPP reset/control, and DPP-side perf counters. Writable settings persist according to hardware reset and power-gating behavior, while status/perf/readback registers can change asynchronously as scanout and processing progress.

Because this file only provides offsets, it does not encode register access permissions, volatile behavior, write-one-to-clear semantics, update-lock sequencing, or safe programming order. Those rules live in the display driver logic and the hardware programming model.

## Dependencies And Integration Points

This chunk depends on the generated DCN 3.1.2 register family staying synchronized:

- `dcn_3_1_2_sh_mask.h` must define matching field shifts and masks for the register names used by `REG_GET`, `REG_SET`, `FD_MASK`, and `FD_SHIFT`.
- `yellow_carp_offset.h` supplies the base-segment macros such as `DCN_BASE__INST0_SEG2` that turn each `*_BASE_IDX` into an absolute MMIO base.
- `reg_helper.h` and local macros in `dcn31_resource.c`, `irq_service_dcn31.c`, and `dmub_dcn31.c` depend on the exact `reg...` and `reg..._BASE_IDX` token spellings.
- HUBP register setup in `dcn31_resource.c` uses `HUBP_REG_LIST_DCN30(id)` for instances 0-3. The slice provides most of the instance-specific `HUBP*`, `HUBPREQ*`, `HUBPRET*`, and `CURSOR0_*` offsets needed by those tables.
- DPP register setup uses `DPP_REG_LIST_DCN30(id)`, which expects `CNVC_CFG*`, `CNVC_CUR*`, `DSCL*`, `CM*`, and `DPP_TOP*` offsets. This chunk contains complete DPP0/DPP1 coverage for those prefixes and partial DPP2 coverage.
- Higher-level display subsystems integrate through hardware object constructors such as HUBP and DPP construction paths, plane programming, cursor programming, color pipeline programming, scaler programming, perf counter/debug paths, IRQ handling, DMUB setup, and HWSEQ CRC/readback logic.

The integration contract is primarily compile-time. Missing or renamed macros fail during compilation when token concatenation cannot resolve a register name. Incorrect numeric offsets are more dangerous because they can compile cleanly while programming or reading the wrong MMIO register.

## Risks And Edge Cases

- The range starts mid-`HUBPREQ0` and ends mid-`DSCL2`; whole-file analysis must merge adjacent chunks before claiming full coverage for those blocks.
- The file is generated and highly repetitive. A one-instance offset drift, especially among `HUBPREQ1/2/3`, `CURSOR0_1/2/3`, or `CM0/CM1`, can be hard to catch by visual review.
- `SRI`-style token concatenation is sensitive to prefix conventions such as `CURSOR0_` versus `CURSOR`, `CNVC_CFG`, `CNVC_CUR`, `DPP_TOP`, and `DC_PERFMON`. A local rename or generation change can break consumers even if the hardware address is unchanged.
- Many registers in this range drive live scanout timing and memory fetch behavior. Bad offsets for `VBLANK_PARAMETERS_*`, `FLIP_PARAMETERS_*`, `PREFETCH_SETTINGS*`, `NOM_PARAMETERS_*`, `PER_LINE_DELIVERY*`, request-size config, or TTU/QoS registers can produce underflow, missed flips, visible corruption, or hangs under bandwidth pressure.
- Surface, metadata, VM aperture, VMID, DCC, and TMZ registers have security and memory-isolation implications. An offset mismatch can direct a pipe to stale memory, an incorrect VMID, or incorrectly protected surfaces.
- Cursor and DMDATA registers combine visible cursor state with metadata fetch/control state. Wrong offsets can leave cursors invisible, corrupt, stale after flips, or can break metadata delivery.
- DSCL coefficient RAM and CM LUT/RAM accesses are index/data style programming surfaces. Incorrect offsets or missing update sequencing can corrupt color/scaler tables without obvious compile-time symptoms.
- Memory power control/status registers appear for HUBPREQ, HUBPRET, cursor, DSCL/OBUF, and CM. Power-gating interactions require correct polling and sequencing; this header does not identify status-vs-control behavior.
- DPP0/DPP1 have full color-management blocks in this chunk, but DPP2 is partial. Tests or audits focused only on this chunk should not infer that DPP2 color, memory power, and top/perfmon definitions are absent from the whole file.

## Test Signals

Useful validation signals are build-time, generated-header consistency, and hardware behavior oriented:

- Compile AMDGPU display code for the DCN 3.1/Yellow Carp configuration to catch unresolved `reg...` and `reg..._BASE_IDX` tokens in HUBP, DPP, DMUB, HWSEQ, and IRQ register tables.
- Preprocess `dcn31_resource.c`, `dmub_dcn31.c`, and `irq_service_dcn31.c` to confirm `SRI`/`SR` expansions resolve to expected `BASE(2) + offset` expressions for representative `HUBPREQ`, `HUBP`, `CURSOR0_`, `CNVC_CFG`, `DSCL`, `CM`, and `DPP_TOP` registers.
- Compare this header against the matching AMD register database or generated sibling headers to ensure every `reg...` in this range has a paired `*_BASE_IDX` and matching shift/mask definitions where the driver uses field helpers.
- Exercise plane enable/disable, page flip, vblank, cursor update, DCC/TMZ surfaces, VM fault/underflow recovery, and suspend/resume on DCN 3.1.2 hardware while watching HUBP underflow, flip-pending, no-outstanding-request, VM fault, and memory power status behavior.
- Validate scaler paths with no scaling, luma/chroma scaling, 4:2:0, fractional ratios, coefficient programming, overscan, and recout/MPC sizing to cover `DSCL*` offsets.
- Validate color-management paths including degamma, gamma correction, gamut remap, post-CSC, HDR multiplier, shaper/blend gamma, and 3D LUT programming to cover `CM0`/`CM1` and the DPP2 definitions completed in adjacent chunks.
- Use CRC and perfmon debug paths to confirm `DPP_TOP*_DPP_CRC_*` and `DC_PERFMON*` offsets read sensible values and do not alias unrelated blocks.
- Include multi-pipe tests that activate pipe instances 0 through 3, because many defects in this header would only appear when programming nonzero instances.

## Open Cross-Chunk Questions

- The merge lane should combine this with the previous chunk to describe the complete `HUBPREQ0` block, including the surface, VM, TTU, and first vblank parameter registers before line 2663.
- The merge lane should combine this with the next chunk to complete `DSCL2`, `CM2`, DPP2 top/perfmon, and any subsequent DPP instances present in the whole DCN 3.1.2 offset file.
- Whole-file reconciliation should verify the expected number of HUBP/DPP pipe instances for this ASIC and check whether later instances are present, intentionally omitted, or handled by other generated files.
