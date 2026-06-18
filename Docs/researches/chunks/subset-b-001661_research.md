# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_2_1_0_sh_mask.h lines 12313-14826

## Scope And Purpose

This chunk is part of the generated AMD DCN 2.1.0 register shift/mask header. It contains compile-time preprocessor constants only: 2,121 `#define` entries in this range, including 1,060 `__SHIFT` constants and 1,082 `_MASK` constants. There are no C functions, structs, enums, variables, or executable branches in the chunk.

The path is under a local `ceph-client` source mirror, but this file is AMDGPU display hardware metadata, not Ceph filesystem code. Its purpose is to publish exact bit positions for DCN 2.1 display hub, cursor, DPP, converter, scaler, color-management, and performance-monitor registers so AMD display code can use symbolic field names through register helper macros rather than open-coded constants.

The range starts at the final `HUBPREQ3_PER_LINE_DELIVERY` chroma mask, then covers:

- `HUBPREQ3` cursor delivery, ref-frequency conversion, destination-Y request limit, request-memory power control/status, and vblank/flip timing fields.
- `HUBPRET3` return-path detile-buffer control, return-memory power control/status, read-line windows, vblank/read-line interrupt control/status/clear bits, current read-line value, and read-line status bits.
- `CURSOR0_3` cursor fetch state, including control, surface address high/low, size, position, hotspot, stereo, destination offset, cursor memory power, DMDATA address/control/QoS/status/software-data registers.
- `DC_PERFMON10` and `DC_PERFMON11` performance counter and performance-monitor control/value fields for HUBP/DPP-adjacent instrumentation blocks.
- `DPP_TOP0`, `CNVC_CFG0`, `CNVC_CUR0`, `DSCL0`, and `CM0` fields for DPP top-level clock/reset/CRC/host-read, pixel format conversion, cursor color conversion, scaler programming, line-buffer/output-buffer state, color matrices, degamma/blending/shaper LUTs, 3D LUTs, memory power, and test/debug access.
- The beginning of repeated instance-1 DPP fields: `DPP_TOP1`, `CNVC_CFG1`, `CNVC_CUR1`, and the start of `DSCL1`.

The chunk boundaries are not semantic. Line 12313 is only the chroma mask for a register whose shifts and luma mask are in the previous chunk. Line 14826 is only the comment for `DSCL1_SCL_HORZ_FILTER_SCALE_RATIO`; that register's actual shift/mask definitions begin in the next chunk. The final per-file report must reconcile those boundaries.

## Important API Surface

The exported interface is the generated AMD register-field naming contract:

- `<REGISTER>__<FIELD>__SHIFT` gives the field's bit offset.
- `<REGISTER>__<FIELD>_MASK` gives the field's packed 32-bit mask.
- Consumers combine this header with the matching `dcn_2_1_0_offset.h` register-address header and AMD display helper macros such as `SF`, `SRI`, `TF_SF`, `IPP_SF`, `REG_SET`, `REG_UPDATE`, `REG_GET`, `set_reg_field_value`, and `get_reg_field_value`.

Important macro families in this chunk include:

- `HUBPREQ3_CURSOR_SETTINGS`, `HUBPREQ3_REF_FREQ_TO_PIX_FREQ`, `HUBPREQ3_DST_Y_DELTA_DRQ_LIMIT`, `HUBPREQ3_HUBPREQ_MEM_PWR_CTRL`, `HUBPREQ3_HUBPREQ_MEM_PWR_STATUS`, `HUBPREQ3_VBLANK_PARAMETERS_[5-6]`, and `HUBPREQ3_FLIP_PARAMETERS_[3-6]`. These describe cursor request offsets, chunk-handle adjustment, request scheduler timing, VM/PTE/meta fetch timing, and request-side memory power state for pipe instance 3.
- `HUBPRET3_HUBPRET_CONTROL`, `HUBPRET3_HUBPRET_MEM_PWR_CTRL`, `HUBPRET3_HUBPRET_MEM_PWR_STATUS`, `HUBPRET3_HUBPRET_READ_LINE_CTRL[0-1]`, `HUBPRET3_HUBPRET_READ_LINE[0-1]`, `HUBPRET3_HUBPRET_INTERRUPT`, `HUBPRET3_HUBPRET_READ_LINE_VALUE`, and `HUBPRET3_HUBPRET_READ_LINE_STATUS`. These fields define return-path detile-buffer layout, crossbar source selection, memory power, read-line comparators, vblank/read-line interrupt behavior, and live/snapshot line status.
- `CURSOR0_3_CURSOR_*` and `CURSOR0_3_DMDATA_*`. These cover cursor enable/mode/TMZ/snoop/system/pitch/chunk settings, surface addresses, dimensions, position, hotspot, stereo mode, destination offset, cursor memory power state, and display metadata address/QoS/status/software-write fields.
- `DC_PERFMON10_*` and `DC_PERFMON11_*`. These expose counter select fields, clear bits, counter state, performance-monitor mode, update/clear selection, window-control and static-screen/selectable-trigger fields, plus high/low/current-value registers.
- `DPP_TOP0_*` and `DPP_TOP1_*`. These include DPP clock enable/gating controls, soft reset, CRC value/control fields, and host-read rate control.
- `CNVC_CFG0_*` and `CNVC_CFG1_*`. These describe surface pixel format, format expansion, 16-bit conversion, alpha enable, converter bypass, MSB alignment, positive clamping, update-pending status, FP bias/scale for RGB channels, color-key ranges, and 2-bit alpha LUT entries.
- `CNVC_CUR0_*` and `CNVC_CUR1_*`. These describe DPP-side cursor color conversion: cursor enable, expansion, pixel inversion, ROM enable, mode, pixel-alpha modulation, update-pending state, two cursor colors, and FP scale/bias.
- `DSCL0_*` plus the first `DSCL1_*` fields. These cover scaler coefficient RAM selection/data, scaler mode and coefficient-bank selection, luma/chroma/alpha tap counts, 2-tap hardcoded/sharpness control, manual replicate factors, horizontal/vertical luma/chroma scale ratios and initial phases, external overscan, OTG blanking, RECOUT/MPC sizing, line-buffer format/counter/memory control, DSCL memory power/status, and output-buffer memory power/control.
- `CM0_*`. This is the largest family in the chunk: color-management control, input color-space conversion matrices for regular and B paths, gamut remap matrices, bias, degamma LUT index/data/write masks, degamma RAM A/B region descriptors, blending gamma LUT and RAM A/B region descriptors, HDR multiplier, memory power/status, dealpha, coefficient format, shaper control/offset/scale/LUT/region descriptors, 3D LUT mode/index/data/read-write control/output normalization/offsets, and test debug index/data.

## Control Flow

This chunk has no local runtime control flow. It is declarative hardware metadata. Runtime sequencing lives in AMD display code that binds register offsets, shifts, and masks into per-block tables, then performs MMIO reads and writes through helper macros.

Representative integration patterns in this source tree are:

- `display/dc/resource/dcn21/dcn21_resource.c` includes both `dcn_2_1_0_offset.h` and `dcn_2_1_0_sh_mask.h`, then constructs the DCN 2.1 resource pool. This is where generated constants become part of the DCN 2.1 block tables for HUBP, DPP, timing, GPIO, IRQ, audio/DMUB-related resources, and other display components.
- `display/dmub/src/dmub_dcn21.c`, `display/dc/irq/dcn21/irq_service_dcn21.c`, `display/dc/gpio/dcn21/hw_factory_dcn21.c`, and `display/dc/gpio/dcn21/hw_translate_dcn21.c` also include this header for DCN 2.1 register metadata.
- Shared DPP and IPP headers such as `display/dc/dpp/dcn10/dcn10_dpp.h`, `display/dc/dpp/dcn20/dcn20_dpp.h`, and `display/dc/dcn10/dcn10_ipp.h` show the symbol-pasting pattern for fields visible in this chunk: `TF_SF(DSCL0_SCL_MODE, DSCL_MODE, mask_sh)`, `TF_SF(CM0_CM_3DLUT_MODE, CM_3DLUT_MODE, mask_sh)`, `TF_SF(CNVC_CFG0_FORMAT_CONTROL, CNVC_BYPASS, mask_sh)`, and `IPP_SF(CURSOR0_0_CURSOR_CONTROL, CURSOR_ENABLE, mask_sh)`. Instance-specific resource code maps those base patterns to the actual register instances.
- Hardware sequencing code programs these fields during plane enable, scaling setup, format conversion, color pipeline setup, cursor updates, interrupt setup/acknowledgement, power gating, and diagnostic readback. This header does not encode the order; callers must apply DCN-specific ordering such as update locks, coefficient/LUT bank selection, memory-power polling, interrupt clear rules, and modeset/flip timing constraints.

## State And Persistence Behavior

The header itself stores no software state and has no persistence behavior. The represented fields describe persistent or live hardware state inside DCN display blocks while those blocks are powered.

State represented by this chunk includes:

- Request-side HUBPREQ3 timing and memory power state for VM/PTE/meta fetches, cursor request scheduling, flip/vblank parameters, and ref-clock-to-pixel-clock conversion.
- Return-side HUBPRET3 detile-buffer assignment, read-line comparator windows, vblank/read-line interrupt state, live read-line snapshots, and return-path memory power state.
- Cursor0 pipe-3 fetch configuration, addresses, dimensions, position, stereo presentation, memory power, and DMDATA payload/address/QoS/status state.
- DPP top-level clock/reset/CRC/host-read state and performance-monitor counter state.
- CNVC pixel format, color key, alpha, clamp, FP bias/scale, and cursor conversion state for DPP instances 0 and 1.
- DSCL scaler coefficient RAM contents/selectors, scale ratios, init phases, tap counts, overscan, output sizing, line-buffer state, output-buffer state, and DSCL memory power state.
- CM0 color pipeline state: input CSC, gamut remap, degamma and blending gamma LUT programming, shaper LUT and region descriptors, HDR multiplier, 3D LUT data/control, coefficient format, dealpha, memory power, and debug selector/data state.

Persistence is hardware-defined. Many programming fields remain active until the driver reprograms the plane, performs a modeset, disables the block, power-gates memory, resumes from suspend, or the GPU resets. Status, update-pending, interrupt, perfmon, read-line snapshot, LUT index/data, and debug fields may be transient, latched, sticky, self-clearing, write-one-to-clear, or banked; the access type is not captured by this generated header.

## Dependencies And Integration Points

This chunk depends on the generated DCN 2.1 register ecosystem:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_2_1_0_offset.h` supplies the matching MMIO register offsets and instance-indexed address macros.
- `dcn_2_1_0_sh_mask.h` supplies the shift/mask constants in this chunk plus adjacent chunks for complete register families.
- AMD display register access helpers in the DC codebase paste register and field names into the generated `__SHIFT` and `_MASK` symbols.
- DCN 2.1 resource construction, IRQ service, GPIO translation/factory, and DMUB code include this header directly.
- Common DPP/IPP/scaler/color-management code from DCN10/DCN20 generations consumes the same families of field names through generated per-generation tables.

Functional integration points include multi-pipe display plane programming, cursor updates, page flip/vblank/read-line interrupt behavior, DPP clock/reset management, CRC collection, scaler coefficient loading, line-buffer/output-buffer memory management, color-keying, degamma/blending/shaper/3D LUT programming, gamut remap, HDR multiplier setup, display metadata cursor/DMDATA handling, performance monitoring, and suspend/resume or power-gating restoration.

## Risks And Edge Cases

- These constants are a hardware ABI. A wrong bit shift or mask can compile cleanly while programming the wrong field in MMIO.
- The chunk starts and ends in the middle of logical register groups. The previous chunk is required for the complete `HUBPREQ3_PER_LINE_DELIVERY` definition, and the next chunk is required for the actual `DSCL1_SCL_HORZ_FILTER_SCALE_RATIO` fields.
- Repeated instance families create drift risk. `DPP_TOP0` and `DPP_TOP1`, `CNVC_CFG0` and `CNVC_CFG1`, `CNVC_CUR0` and `CNVC_CUR1`, plus the partial `DSCL0` and `DSCL1` families should remain consistent where hardware requires it, but each macro names a specific instance.
- Interrupt registers mix mask, type, clear, raw status, and interrupt-status bits. Incorrect masks in `HUBPRET3_HUBPRET_INTERRUPT` can lose vblank/read-line events or clear sticky state unexpectedly.
- Memory power fields for HUBPREQ, HUBPRET, cursor, DSCL, OBUF, and CM memories have side effects and status dependencies. Bad shifts can leave memory forced on, forced off, or incorrectly reported.
- Address-related cursor and DMDATA fields are split into high/low pieces. Treating all address fields as identical widths can truncate addresses or fetch from the wrong memory.
- Scaler ratio/init/tap/coefficient fields are narrow packed fields. Overflow, truncation, or bank-selection mistakes can produce visible image scaling artifacts, underflow, or mode validation failures only for specific formats and viewport sizes.
- Color-management LUT and region descriptors are dense and repetitive. A swapped channel, RAM bank, region offset, or write-enable mask can create hard-to-diagnose gamma, shaper, gamut, HDR, or 3D LUT errors that may not affect basic modes.
- Fields such as `*_UPDATE_PENDING`, CRC one-shot state, perfmon clear/update controls, read-line snapshots, and debug selectors may be volatile or side-effectful even though this header exposes only numeric masks.
- Cross-generation headers contain similar names with different field presence. For example later DCN generations add or remove fields around cursor control and format crossbars; copying values between `dcn_2_1_0_sh_mask.h` and `dcn_3_*`/`dcn_4_*` headers is unsafe without vendor-register validation.

## Test Signals

Useful validation for this chunk combines build checks, generated-header comparisons, and hardware behavior:

- Build AMDGPU display code with DCN 2.1 enabled. Missing or renamed fields should fail in `dcn21_resource.c`, `irq_service_dcn21.c`, DMUB, GPIO, or shared DPP/IPP field tables.
- Compare this generated range against the matching vendor register database and the companion `dcn_2_1_0_offset.h` offsets; every field should have the expected register address, shift, and mask.
- Static-diff repeated instance families (`DPP_TOP0` versus `DPP_TOP1`, `CNVC_CFG0` versus `CNVC_CFG1`, `CNVC_CUR0` versus `CNVC_CUR1`, `DSCL0` versus `DSCL1`) to catch unintended per-instance drift.
- Exercise multi-display and multi-plane modes that use pipe 3, including cursor movement, cursor format changes, vblank/read-line interrupt delivery, page flips, and DMDATA handling.
- Exercise scaling paths across luma/chroma formats, integer and fractional ratios, overscan, line-buffer programming, and coefficient-bank updates; watch for underflow, blanking, or visual artifacts.
- Validate color-management paths with degamma, blending gamma, shaper LUTs, gamut remap, HDR multiplier, and 3D LUT programming, using CRC/readback or visual test patterns where available.
- Test memory power and suspend/resume sequences; verify memory power status fields converge and that cursor, DPP, DSCL, OBUF, CM, and HUBPREQ/HUBPRET state is restored after power transitions.
- Use DPP CRC and perfmon readback as diagnostic signals for field-table correctness, but remember these paths themselves depend on the same generated masks.
