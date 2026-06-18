# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_2_0_1_sh_mask.h lines 2552-5077

## Scope

This chunk is part of the generated AMD DCN 2.0.1 ASIC register mask/shift header. It covers lines 2552-5077 and exports preprocessor constants for display hub pipe, hub request/return, cursor, DPP top, converter, scaler, and color-management register fields. The slice contains 2,105 `#define` entries: 1,052 `__SHIFT` constants and 1,053 `_MASK` constants. It has no C functions, structs, enums, or executable control flow; its API is the generated macro namespace consumed by AMDGPU display register helper code.

The chunk starts in the tail of the `HUBP2_DCHUBP_REQ_SIZE_CONFIG_C` mask set and ends mid-register at `CM0_CM_BLNDGAM_RAMB_REGION_16_17`, so whole-file reconciliation must merge it with adjacent chunks for complete register-family coverage.

## Purpose

The purpose of this chunk is to map symbolic DCN 2.0.1 display register fields to exact bit positions and bit masks. Runtime AMDGPU display code can then use generated field names with register access macros instead of hand-coded shifts and constants.

Major hardware domains represented here are:

- `HUBP2` control, clock, debug, and measurement-window fields for hub pixel processor instance 2.
- `HUBPREQ2` and `HUBPREQ3` request-path fields for pitch, luma/chroma primary and secondary surface addresses, metadata surface addresses, DCC/TMZ control, flip control, flip interrupts, in-use/earliest-in-use tracking, expansion modes, TTU/QoS timing, blanking, prefetch, vblank, flip, nominal delivery timing, cursor request timing, ref-clock conversion, destination Y limits, and request memory power control/status.
- `HUBPRET2` and `HUBPRET3` return-path fields for detile-buffer control, memory power, read-line windows, vblank/read-line interrupt status/clear/mask bits, current read-line value, and read-line status.
- `CURSOR0_2` and `CURSOR0_3` fields for cursor enable/mode/pitch, surface address, size, position, hotspot, stereo, destination offset, cursor memory power, and DMDATA address/QoS/status/software-write handling.
- `DPP_TOP0`, `CNVC_CFG0`, `CNVC_CUR0`, and `DSCL0` fields for DPP control/reset/CRC/host-read, surface pixel format conversion, FP bias/scale, color keying, cursor color conversion, scaler coefficient RAM, scaler ratios/init/taps, RECOUT/MPC dimensions, line-buffer format, memory power, and output buffer control.
- `CM0` fields for input color-space conversion, gamut remap matrices, bias, degamma LUT programming, degamma RAM A/B region descriptors, blending gamma LUT programming, and blending gamma RAM A/B region descriptors.

## Important API Surface

The exported surface is the generated naming convention:

- `<REGISTER>__<FIELD>__SHIFT`
- `<REGISTER>__<FIELD>_MASK`

Important examples in this chunk include:

- `HUBP2_DCHUBP_CNTL__HUBP_DISABLE__SHIFT` / `_MASK`, `HUBP2_DCHUBP_CNTL__HUBP_UNDERFLOW_STATUS__SHIFT` / `_MASK`, and `HUBP2_HUBP_CLK_CNTL__HUBP_CLOCK_ENABLE__SHIFT` / `_MASK` for pipe enable, underflow, and clock state.
- `HUBPREQ2_DCSURF_PRIMARY_SURFACE_ADDRESS*`, `HUBPREQ2_DCSURF_SECONDARY_SURFACE_ADDRESS*`, and matching `_C` and metadata address macros for luma/chroma scanout and DCC metadata programming.
- `HUBPREQ2_DCSURF_SURFACE_CONTROL__PRIMARY_SURFACE_DCC_EN`, `*_TMZ`, and secondary/meta TMZ fields for compression/security-related fetch configuration.
- `HUBPREQ2_DCSURF_FLIP_CONTROL`, `HUBPREQ2_DCSURF_FLIP_CONTROL2`, and `HUBPREQ2_DCSURF_SURFACE_FLIP_INTERRUPT` for update locking, pending flip state, GSL/triple-buffer behavior, and flip interrupt status/clear/mask fields.
- `HUBPREQ2_DCN_*`, `HUBPREQ2_PREFETCH_SETTINGS*`, `HUBPREQ2_VBLANK_PARAMETERS_*`, `HUBPREQ2_FLIP_PARAMETERS_*`, `HUBPREQ2_NOM_PARAMETERS_*`, and per-line delivery fields for request scheduling and watermark-style timing.
- The same `HUBPREQ3`, `HUBPRET3`, and `CURSOR0_3` families repeated for pipe instance 3.
- `DPP_TOP0_DPP_CONTROL`, `CNVC_CFG0_CNVC_SURFACE_PIXEL_FORMAT`, `CNVC_CFG0_FORMAT_CONTROL`, `DSCL0_SCL_*`, and `DSCL0_LB_*` for DPP format/scaler programming.
- `CM0_CM_ICSC_*`, `CM0_CM_GAMUT_REMAP_*`, `CM0_CM_DGAM_*`, and `CM0_CM_BLNDGAM_*` for matrix color transforms and piecewise LUT region programming.

These constants are normally consumed through AMD display helper macros such as `REG_SET`, `REG_UPDATE`, `REG_GET`, register field-list macros, and symbol-pasting helpers like `SF`, `TF_SF`, or block-specific field table builders. For this exact header family, `drivers/gpu/drm/amd/display/dc/irq/dcn201/irq_service_dcn201.c` includes `dcn/dcn_2_0_1_sh_mask.h`; the DPP color-management fields visible here are also represented in DCN20 DPP field-list macros in `drivers/gpu/drm/amd/display/dc/dpp/dcn20/dcn20_dpp.h`.

## Control Flow

There is no local control flow in this header chunk. Runtime behavior is external and follows the display driver's register programming sequences:

- Resource and block constructors bind generated offset, mask, and shift tables to specific DCN 2.0.1 hardware blocks.
- HUBP/HUBPREQ programming code writes format, tiling, pitch, address, metadata, DCC, TMZ, VM/timing, and flip-related fields when enabling planes or performing page flips.
- IRQ service code uses generated interrupt masks/shifts to enable, query, and clear vblank, read-line, and flip interrupts.
- DPP scaler and color code writes CNVC, DSCL, and CM fields while applying plane format conversion, scaling, gamut remap, degamma, and blending gamma state.
- Power-management paths write force/disable/low-power-mode fields and poll corresponding status fields for HUBPREQ, HUBPRET, cursor, DSCL, and OBUF memories.

Ordering is an implicit contract enforced by callers, not by this file. For example, callers must apply update locks, program related surface address and metadata fields, handle flip timing, and clear sticky interrupt bits in the sequence required by hardware.

## State and Persistence

The file has no software state. Its macros describe memory-mapped hardware state that persists in the GPU display blocks while powered:

- Surface pitch, address, metadata address, DCC, TMZ, and format fields define the active scanout memory interpretation.
- Flip control, pending, in-use, earliest-in-use, and interrupt fields track frame-boundary update state.
- TTU, prefetch, vblank, flip, nominal, per-line delivery, cursor timing, and ref-frequency conversion fields persist as scheduler parameters used by HUBPREQ.
- Clock, blank, disable, timeout, underflow, read-line, and memory power fields expose live block state and sticky health/status bits.
- DPP, CNVC, DSCL, and CM fields persist as active image processing state for a plane, including scaler coefficients/ratios, color matrices, LUT indices/data, and gamma region descriptors.

Incorrect constants can therefore corrupt persistent hardware programming until a modeset, block reprogramming, GPU reset, or power transition restores correct register contents.

## Dependencies and Integration Points

This chunk depends on the matching DCN 2.0.1 register offset header and on AMD display register helper macros that paste register and field identifiers into `__SHIFT` and `_MASK` symbols. It is tightly coupled to the DCN 2.0.1 hardware register specification.

Key integration points include:

- DCN 2.0.1 IRQ service setup through `drivers/gpu/drm/amd/display/dc/irq/dcn201/irq_service_dcn201.c`, which includes this mask header for interrupt source field metadata.
- HUBP and HUBPREQ/HUBPRET display pipe code that programs scanout surfaces, flip sequencing, request timing, cursor fetch state, and memory power state by pipe instance.
- DPP code, especially DCN20-generation field-list macros in `drivers/gpu/drm/amd/display/dc/dpp/dcn20/dcn20_dpp.h`, which reference `CM0_CM_BLNDGAM_*`, `CM0_CM_DGAM_*`, scaler, converter, and color management fields.
- Register address constants in the corresponding `dcn_2_0_1_offset.h` family; mask/shift definitions are only meaningful when paired with the correct register offsets.
- Cross-generation generated headers such as `dcn_2_0_0_sh_mask.h`, `dcn_2_1_0_sh_mask.h`, and later `dcn_3_*`/`dcn_4_*` variants. The names are similar, but field presence and masks can diverge, so copying between generations is risky.

## Risks

- A wrong mask or shift silently writes the wrong hardware bits. Highest-risk fields in this chunk include surface addresses, metadata addresses, DCC/TMZ enables, flip locks/pending bits, interrupt clears, memory power controls, scaler ratios, and color LUT region descriptors.
- Pipe instance drift is likely because `HUBPREQ2`/`HUBPREQ3`, `HUBPRET2`/`HUBPRET3`, and `CURSOR0_2`/`CURSOR0_3` are near-duplicate families. A one-bit mismatch may only affect a specific pipe or multi-display layout.
- Address-high masks are narrower than address-low masks, typically 16-bit versus 32-bit. Treating the address pairs uniformly can truncate scanout, metadata, or DMDATA addresses.
- Status and clear bits share registers with mask/type/control bits in interrupt and underflow paths. Incorrect read-modify-write masks can lose interrupts, fail to acknowledge sticky status, or clear status unexpectedly.
- Timing fields are narrow and packed. Overflow or stale masks in prefetch, vblank, nominal, delivery, and scaler-ratio fields can produce underflow, tearing, or validation failures only under specific modes.
- Color-management region macros use repeated RAM A/RAM B and channel-specific start/slope/end/region patterns. A swapped region offset or channel mask can create hard-to-debug color/gamma errors rather than compile failures.
- Because this is a generated constants-only header, normal unit tests do not exercise the macros directly; many errors surface only through integration builds, static comparison, or hardware/display behavior.

## Test Signals

Useful validation signals for changes to this chunk are:

- AMDGPU display driver compilation for DCN 2.0.1 and nearby DCN20 paths, which catches missing or renamed macros in IRQ, HUBP, DPP, scaler, and color-management code.
- Static diff against the vendor register database or adjacent generated DCN 2.0.1 artifacts, especially verifying each `__SHIFT` has the intended `_MASK` and that repeated pipe 2/pipe 3 families remain consistent where hardware requires it.
- Multi-pipe runtime display tests with planes on pipe 2 and pipe 3, including primary/secondary plane flips, luma/chroma formats, DCC-enabled surfaces, TMZ-protected surfaces, cursor movement, stereo cursor fields, and metadata-address changes.
- Interrupt tests for flip, vblank, and read-line mask/status/clear behavior in `HUBPREQ*` and `HUBPRET*` registers.
- Suspend/resume, memory power-gating, and clock-gating tests that verify memory power status fields converge and no underflow/timeout bits remain stuck.
- Image-quality tests for DPP0 conversion, scaling, color keying, gamut remap, degamma, and blending gamma programming, including LUT load/readback or visual CRC-style checks where available.

## Chunk Notes

This chunk is generated register metadata, not functional logic. The main research value is identifying the hardware surfaces covered and the risk profile of the exported constants: display memory fetch, flip/interrupt sequencing, request timing, cursor fetch/DMDATA, DPP scaler/format conversion, and color-management LUT/matrix programming. The final merged file report should connect this slice with adjacent chunks to cover the complete `dcn_2_0_1_sh_mask.h` register map.
