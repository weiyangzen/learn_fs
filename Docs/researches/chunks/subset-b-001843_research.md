# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_1_4_sh_mask.h lines 24584-27100

## Scope

This chunk covers lines 24584-27100 of the generated AMD DCN 3.1.4 shift/mask header. It contains only preprocessor constants and generated register grouping comments: 2,112 `#define` entries, made up of 1,057 `__SHIFT` constants and 1,055 `_MASK` constants, plus 6 `addressBlock` comments. There are no functions, structs, enums, variables, allocations, locks, or executable statements in this range.

The range starts in the middle of the DPP1 color-management `CM1_CM_BLNDGAM_RAMB` block, continues through the end of DPP1 color-management shaper and 3D LUT masks, then moves into DPP1 perfmon and DPP2 register blocks. The DPP2 portion covers top-level DPP control, CNVC conversion/pre-CSC masks, DSCL scaler/memory-power masks, and most of the DPP2 color-management pipeline through the beginning of `CM2_CM_SHAPER_RAMA_REGION_2_3`. The chunk ends mid-register-family; later lines continue the remaining CM2 shaper RAM region definitions.

Although the source tree path is under a local `ceph-client` mirror, this file is AMDGPU display-driver hardware metadata. It does not implement Ceph or distributed-filesystem behavior.

## Purpose

The purpose of this header slice is to publish symbolic bit positions and masks for DCN 3.1.4 display pipe processor registers. AMDGPU display code combines these macros with the matching `dcn_3_1_4_offset.h` register-address constants and register-helper macros to pack MMIO writes, update individual fields, and decode hardware status without hard-coding numeric field layouts.

This is a generated hardware contract rather than algorithmic code. Runtime behavior is produced by code that includes this header and expands token-pasted field names into these constants. The important behavior is therefore the exact macro name, the associated register/field grouping, and the numeric shift/mask value.

## Important APIs, Types, And Constants

There are no callable APIs or C types in this chunk. The exported interface is the generated macro convention:

- `<REGISTER>__<FIELD>__SHIFT` gives a field bit offset.
- `<REGISTER>__<FIELD>_MASK` gives the field mask within the register word.
- `//<REGISTER>` comments group all fields for one logical register.
- `// addressBlock: ...` comments mark generated hardware address blocks for DPP1 perfmon, DPP2 top, DPP2 CNVC, DPP2 DSCL, and DPP2 CM.

Major constant groups in this slice include:

- DPP1 `CM1_CM_BLNDGAM_RAMB_*` blend-gamma RAM B metadata: per-channel start, start segment, start slope, start base, end base, end slope, offsets, and 34 exponential-region descriptors packed as pairs `REGION_0_1` through `REGION_32_33`.
- DPP1 color-management controls after blend gamma: `CM1_CM_HDR_MULT_COEF`, `CM1_CM_MEM_PWR_CTRL`, `CM1_CM_MEM_PWR_STATUS`, `CM1_CM_DEALPHA`, `CM1_CM_COEF_FORMAT`, shaper control/offset/scale/LUT-index/LUT-data/write-enable masks, shaper RAM A and RAM B start/end/region descriptors, `CM1_CM_MEM_PWR_CTRL2`, `CM1_CM_MEM_PWR_STATUS2`, `CM1_CM_3DLUT_MODE`, `CM1_CM_3DLUT_INDEX`, `CM1_CM_3DLUT_DATA`, `CM1_CM_3DLUT_DATA_30BIT`, `CM1_CM_3DLUT_READ_WRITE_CONTROL`, 3D LUT normalization/output offsets, and CM test-debug index/data masks.
- `DC_PERFMON11_*` DPP1 perfmon field masks for performance-counter source selection, clear/reset/free-run behavior, slice and threshold configuration, start/stop/continue/clear control, counter status, counter value, high/low count words, interrupt status, interrupt type, mode, and auto-clear behavior.
- `DPP_TOP2_*` masks for DPP2 enablement, clock gating, dithering, CRC results/control, soft reset, and host read control.
- `CNVC_CFG2_*` masks for DPP2 surface pixel format, alpha/dealpha/realpha behavior, expansion mode, floating-point conversion bias/scale, color-key controls, 2-bit alpha LUT values, pre-degamma, pre-CSC mode, pre-CSC coefficient pairs for normal and B matrices, and coefficient-format selection.
- `DSCL2_*` masks for DPP2 scaler coefficient RAM tap selection/data, scaler mode and taps, DSCL control, 2-tap mode, manual replication, horizontal/vertical luma and chroma scale ratios and initial phases, black color, update/autocal, overscan, OTG blanking, recout/MPC sizes, line-buffer data format, memory power control/status, vertical counter, and output-buffer memory power control.
- DPP2 `CM2_CM_*` color-management masks: main control and post-CSC/gamut-remap matrices, bias fields, gamma-correction LUT control and RAM A/B region metadata, blend-gamma LUT control and RAM A/B metadata, HDR multiplier, memory power controls/status, dealpha, coefficient format, shaper control/offset/scale/LUT access, and the beginning of shaper RAM A region metadata.

The repeated gamma and shaper region registers use a common packed layout: two regions per register, each with a LUT offset field and a number-of-segments field. Start/end control registers split per-channel R/G/B fixed-point values across start, start-segment, base, end, and slope fields.

## Control Flow

This chunk has no runtime control flow. Its effective flow is compile-time token expansion:

1. DCN 3.1.4 display code includes `dcn_3_1_4_offset.h` and `dcn_3_1_4_sh_mask.h`.
2. Register helper macros such as `FD_MASK`, `FD_SHIFT`, `REG_GET`, `REG_SET`, `REG_SET_*`, and `REG_UPDATE` paste register and field names into generated tokens.
3. The C preprocessor resolves those tokens to the shift and mask constants from this file.
4. Runtime display code performs MMIO reads/writes against the register offsets from the matching offset header.

The declaration order follows the hardware register database rather than driver execution order. In this range the generated sequence finishes a DPP1 CM block, emits DPP1 perfmon masks, then describes DPP2 top/CNVC/DSCL/CM blocks.

## State And Persistence Behavior

The header itself stores no state and persists nothing. It describes fields within hardware registers whose state is owned by the display engine.

Configuration-like fields in this chunk can program DPP color transforms, degamma/gamma/blend-gamma/shaper/3D LUT state, pre-CSC and post-CSC matrices, gamut remap matrices, scaler ratios and phase initialization, color keying, alpha handling, memory power controls, CRC capture, and perfmon counting. These values generally persist until the display driver rewrites them, a modeset or pipe reprogramming path changes them, power gating resets the block, suspend/resume restores state, or the GPU/ASIC is reset.

Status and observation fields include current shaper mode, memory power state, 3D LUT configuration status, perfmon counter state/value/interrupt fields, DPP CRC results/status-style fields, scaler vertical counter, DSCL memory status, and CM memory-power status. These values are hardware-updated and may change independently of any software-visible state transition in this header.

The masks do not encode access type. Consumers must know from the hardware specification and surrounding driver logic which fields are read-only, write-only, sticky, self-clearing, write-one-to-clear, double-buffered, or sequencing-sensitive.

## Dependencies And Integration Points

This chunk depends on the matching generated DCN 3.1.4 offset header. For example, the corresponding offsets for this slice include `regCM1_CM_BLNDGAM_RAMB_*`, `regCM1_CM_3DLUT_*`, `regDC_PERFMON11_*`, `regDPP_TOP2_*`, `regCNVC_CFG2_*`, `regDSCL2_*`, and `regCM2_CM_*` definitions in `dcn_3_1_4_offset.h`; the masks in this file only describe field placement, not register addresses or base-index selection.

Direct include sites found in this tree are:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/resource/dcn314/dcn314_resource.c`, which includes the DCN 3.1.4 offset and mask headers while constructing the DCN314 display resource layer.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dmub/src/dmub_dcn314.c`, which includes the same headers and builds `dmub_srv_dcn314_regs` using `FD_MASK` and `FD_SHIFT` expansion through `DMUB_DCN31_FIELDS()`.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/irq/dcn314/irq_service_dcn314.c`, which includes the headers for DCN314 interrupt-service register definitions.

Broader integration is through AMD display DPP/CM/DSCL/perfmon helpers that use generated register tables and field macros. Color management code programs gamma correction, blend gamma, shaper LUTs, 3D LUTs, CSC matrices, gamut remap, HDR multiplier, and dealpha behavior. Scaler code programs DSCL tap coefficients, ratios, viewport/recout dimensions, line-buffer format, blanking, and memory controls. DMUB service code consumes masks/shifts to communicate register metadata to firmware-facing services.

The generated offset and mask headers must come from the same register database. Mixing DCN 3.1.4 offsets with masks from DCN 3.1.2, DCN 3.2.x, or DCN 4.x would be risky because many names repeat while block counts and field layouts can diverge.

## Risks And Edge Cases

- The chunk starts inside `CM1_CM_BLNDGAM_RAMB`; the preceding `START_CNTL_B` and earlier RAM B fields are owned by the previous chunk. A final per-file summary must merge adjacent chunks before describing DPP1 blend-gamma RAM B as a complete block.
- The chunk ends inside the `CM2_CM_SHAPER_RAMA_REGION_*` sequence. It includes the start/end controls and regions `0_1` and `2_3`, but later chunks own the remaining shaper RAM A and likely RAM B region definitions.
- Many register families are highly repetitive across CM1/CM2, RAM A/RAM B, and R/G/B channels. Generator drift can be subtle because lines differ only by instance number, RAM bank letter, channel suffix, or region index.
- These are untyped numeric constants. A wrong mask or shift can compile successfully while corrupting adjacent hardware fields or silently misreading status.
- Full-width and high-bit masks appear in perfmon counters, LUT data, CRC values, coefficient fields, and packed pair registers. Callers must avoid signed-width assumptions and should use the register helper types expected by AMD display code.
- LUT and region programming is sequencing-sensitive. `*_LUT_INDEX`, `*_LUT_DATA`, write-enable masks, RAM A/B selection, current-mode/status fields, 3D LUT 30-bit mode, and start/end/region metadata must be programmed in the order required by the display pipeline, not merely with the correct masks.
- Memory-power control fields can gate gamma, blend-gamma, shaper, 3D LUT, scaler line-buffer, and output-buffer memories. Incorrect force/disable values can produce blank output, stale LUT contents, or invalid reads after power transitions.
- Perfmon controls mix counter setup, clear/reset/start/stop behavior, counter value reporting, and interrupt state. Blind read-modify-write patterns can perturb measurement or interrupt behavior if the field access semantics are not followed.
- CNVC and DSCL fields affect visible pixel interpretation and scaling. Errors may manifest only for particular pixel formats, chroma formats, alpha modes, color-key paths, viewport sizes, scaler ratios, or overscan settings.

## Test Signals

Useful validation is mostly build-time consistency plus hardware display behavior:

- Build AMDGPU display code for a DCN314-enabled configuration to catch missing or renamed macros in `FD_MASK`, `FD_SHIFT`, `REG_GET`, `REG_SET`, and `REG_UPDATE` expansion.
- Mechanically verify that every complete field in this line range has a consistent shift/mask pair, while accounting for artificial chunk boundaries at the start of `CM1_CM_BLNDGAM_RAMB` and the end of `CM2_CM_SHAPER_RAMA`.
- Compare this slice against AMD's authoritative DCN 3.1.4 register database and the matching `dcn_3_1_4_offset.h` so every register comment here has a corresponding offset/base-index definition.
- Exercise DCN314 display modes that use DPP2 CNVC and DSCL: different surface pixel formats, alpha/dealpha/realpha paths, pre-CSC/pre-degamma, scaling ratios, chroma/luma filtering, overscan, recout sizing, and line-buffer formats.
- Exercise color-management programming on DPP1 and DPP2: degamma/gamma correction, blend-gamma LUTs, shaper LUTs, 3D LUT enable/disable, HDR multiplier, post-CSC, gamut remap, coefficient-format changes, and bank switching between RAM A and RAM B.
- Validate suspend/resume, display hotplug, modeset, and GPU reset paths for correct restoration of CM, DSCL, memory-power, and LUT state.
- Use CRC and perfmon diagnostics where available to confirm that DPP CRC values and `DC_PERFMON11` counters change as expected and do not stick after clear/reset/start/stop sequences.
- Watch kernel logs, display selftests, visual output, color-calibration tests, scaling tests, and hardware CRC/perfmon traces for failures limited to DPP1/DPP2 or to one RAM bank/channel/region.

## Cross-Chunk Notes

The previous chunk should cover the beginning of `CM1_CM_BLNDGAM_RAMB`, including the missing start-control fields immediately before line 24584. The next chunk should complete the `CM2_CM_SHAPER_RAMA_REGION_*` sequence and any following CM2 shaper RAM B or later DPP2 blocks. The final per-file research document should reconcile these boundaries before making whole-file claims about DCN 3.1.4 DPP color-management coverage.
