# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_2_0_sh_mask.h lines 10081-12635

## Purpose

This chunk is part of the generated AMD DCN 3.2.0 register shift/mask header. It contains no executable C logic; it publishes preprocessor constants that describe field bit positions (`__SHIFT`) and field masks (`_MASK`) for DCN display pipe hardware registers. Consumers combine these constants with the matching DCN 3.2.0 offset header and AMD display register helper macros to compose MMIO writes, extract MMIO read fields, and populate per-block register tables.

The range covers 2,555 source lines and 2,107 `#define` constants: 1,054 shift constants and 1,053 mask constants. The shift/mask count is intentionally uneven because this work item is a byte/line chunk of a much larger generated file. It starts after the `HUBPREQ3_PREFETCH_SETTINGS` shifts, retaining only that register's two masks at lines 10081-10082, and it ends in the middle of `CM1_CM_GAMCOR_RAMB_REGION_26_27`, before three remaining masks in the next chunk.

Although this repository path is under `ceph-client`, this file is AMDGPU display hardware metadata, not distributed-filesystem code.

## Covered Register Areas

The chunk spans these generated address blocks and repeated hardware units:

- Tail of `dcn_dc_dcbubp3_dispdec_hubpreq_dispdec`: HUBP request timing, status, cursor, memory-power, and p-state request fields for pipe/request instance 3.
- Complete `dcn_dc_dcbubp3_dispdec_hubpret_dispdec`: HUBP return/control fields for pipe 3, including DET buffer routing, memory power, read-line windows, vblank/read-line interrupts, and read-line status/value registers.
- Complete `dcn_dc_dcbubp3_dispdec_cursor0_dispdec`: cursor surface address, size, position, hot spot, stereo, memory-power, and display metadata fields for cursor0 on pipe 3.
- `dcn_dc_dpp0_dispdec_cnvc_cfg_dispdec` and `dcn_dc_dpp0_dispdec_cnvc_cur_dispdec`: DPP0 input converter pixel-format, color-key, pre-dealpha/pre-realpha, pre-CSC, pre-degamma, and cursor-converter fields.
- `dcn_dc_dpp0_dispdec_dscl_dispdec`: DPP0 scaler, line-buffer, output-buffer, timing-window, and DSCL/OBUF memory-power fields.
- `dcn_dc_dpp0_dispdec_cm_dispdec`: DPP0 color-management post-CSC, gamut remap, bias, gamma-correction LUT/RAM A/B, HDR multiplier, memory-power, dealpha, coefficient-format, and debug fields.
- `dcn_dc_dpp0_dispdec_dpp_top_dispdec`: DPP0 top-level clock gating, soft reset, CRC, and host-read-rate fields.
- Start of the matching DPP1 blocks: `CNVC_CFG1`, `CNVC_CUR1`, `DSCL1`, and the first part of `CM1`, ending inside gamma-correction RAMB region descriptors.

## Important APIs, Types, And Macros

There are no functions, structs, enums, global variables, locks, allocation paths, includes, or direct register accesses in this range. The public surface is the generated macro namespace:

- `<REGISTER>__<FIELD>__SHIFT`: low bit index for a hardware register field.
- `<REGISTER>__<FIELD>_MASK`: bit mask for isolating or updating that field.
- `// addressBlock: ...`: generated comments grouping register names by hardware block instance.

Important macro families in this chunk include:

- `HUBPREQ3_*`: prefetch ratios, vblank/flip/nominal page-table and metadata timing, per-line delivery timing, cursor request adjustment, reference-to-pixel frequency, DRQ limit, request-side memory power, UCLK p-state force, and status bits for self-refresh, p-state allowance, urgent QoS, vblank, enable, recovery/flush, and flip-active state.
- `HUBPRET3_*`: return-side DET buffer base, component crossbar source selection, 3-to-2 packing disable, DMROB/PIXCDC memory-power controls/status, read-line interval/window registers, vblank/read-line interrupt mask/type/clear/status bits, and read-line snapshot/status fields.
- `CURSOR0_3_*`: cursor enable/request mode/magnification/mode/TMZ/pitch/lines-per-chunk, 64-bit cursor surface address split into low/high registers, width/height, x/y position, hot spot, stereo chunk/enable/offset, destination offset, cursor memory power, DMData address/control/QoS/status/software-control/data fields.
- `CNVC_CFG0_*` and `CNVC_CFG1_*`: surface pixel format, alpha-plane enable, format expansion/conversion/bypass/crossbar, floating-point conversion bias/scale, color-key ranges, alpha 2-bit LUT entries, pre-dealpha, pre-CSC mode and coefficient matrices, coefficient format, pre-degamma mode/select, and pre-realpha.
- `CNVC_CUR0_*` and `CNVC_CUR1_*`: converter-side cursor enable, expansion, pixel inversion, ROM enable, mode, pixel alpha modulation, update pending, two cursor colors, and cursor FP scale/bias.
- `DSCL0_*` and `DSCL1_*`: scaler coefficient RAM tap select/data, scaler mode, tap counts, 2-tap hardcoded/sharp filters, manual replicate factors, horizontal/vertical luma and chroma scale ratios/init phases, black color, update pending, autocal, overscan, OTG blanking, recout/MPC size, line-buffer format/configuration/counters, DSCL line-buffer/LUT memory power, OBUF behavior, and OBUF memory power/status.
- `CM0_*` and `CM1_*`: color-management bypass/update pending, post-CSC mode/current state and matrices, gamut-remap mode/current state and matrices, bias fields, gamma-correction mode/select/PWL disable/current state, LUT index/data/control, RAM A/B region start/slope/base/end/offset/region tables, HDR multiplier, gamma RAM memory power/status, dealpha, coefficient format, and CM test debug controls.
- `DPP_TOP0_*`: DPP clock enable and gate-disable fields, top-level soft reset for CNVC/DSCL/CM/OBUF, DPP CRC values/control, and host-read rate control.

## Control Flow

This header chunk has no runtime control flow. It is consumed by generated/table-driven AMD display code, where control flow exists in the including modules:

1. DCN 3.2 code includes `dcn_3_2_0_offset.h` and `dcn_3_2_0_sh_mask.h`.
2. Local helper macros such as `FD_SHIFT`, `FD_MASK`, `REG_FIELD`, `SR`, `SRI`, and block-specific `*_MASK_SH_LIST_*` macros token-paste a register and field name into the generated shift/mask constant.
3. Resource construction, DMUB, IRQ, GPIO, clock, HUBP, DPP, scaler, color, cursor, CRC, and audio/display support code stores those constants in typed register tables.
4. Runtime display paths use those tables to read/modify/write MMIO registers during modeset, plane programming, cursor updates, scaler programming, color pipeline programming, watermark/prefetch programming, interrupts, power transitions, CRC capture, suspend/resume, and debug reads.

The generated constants do not encode sequencing, volatility, access type, write-one-to-clear behavior, shadow-register latch behavior, or hardware hazards. Callers must still sequence update-pending polling, line/vblank windows, power-gating transitions, LUT index/data writes, scaler coefficient RAM writes, CRC capture, and cursor address updates according to the DCN programming model.

## State And Persistence Behavior

This chunk stores no software state and persists nothing to disk, memory, firmware, or kernel objects. It describes MMIO-backed GPU display state.

The represented hardware state includes:

- HUBP request/return state for pipe 3, including timing calculations for page-table, metadata, VM, prefetch, vblank, flip, per-line delivery, cursor fetch, self-refresh, p-state permission, and QoS urgency.
- Cursor state for pipe 3, including address, geometry, hot spot, request mode, secure/TMZ marking, stereo adjustment, memory power, and DMData metadata.
- DPP0 and DPP1 front-end format-conversion state: pixel format, alpha handling, color keying, component crossbars, pre-CSC/pre-degamma, cursor conversion, and update-pending state.
- DPP0 and DPP1 scaler state: coefficient RAM selection/data, filter taps, ratios, init phases, black fill, overscan, timing windows, recout/MPC dimensions, line-buffer configuration, output-buffer behavior, and memory-power controls/status.
- DPP0 and partial DPP1 color-management state: post-CSC matrices, gamut-remap matrices, bias, gamma-correction LUT index/data/control, RAM A/B PWL region metadata, HDR multiplier for CM0, gamma RAM power state, dealpha, coefficient format, and debug data.
- DPP0 top state for clock gating, soft reset, CRC capture, and host-read throttling.

Persistence is hardware-defined. Programmed values generally persist until the next modeset, plane update, cursor update, color update, power-gating event, suspend/resume, GPU reset, or firmware/hardware reinitialization. Status and interrupt fields can be live, latched, sticky, self-clearing, or clear-on-write depending on the register definition outside this generated mask file.

## Dependencies And Integration Points

This chunk must remain synchronized with the DCN 3.2.0 generated register database:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_2_0_offset.h` supplies the matching register offsets and base/index definitions.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/resource/dcn32/dcn32_resource.c` includes this header and uses generated shift/mask macros to build DCN32 resource register tables. The file directly lists `DPP_TOP0_DPP_CRC_CTRL`, `DPP_TOP0_DPP_CRC_VAL_B_A`, and `DPP_TOP0_DPP_CRC_VAL_R_G`, and uses `DPP_REG_LIST_SH_MASK_DCN30_COMMON`, `HUBP_MASK_SH_LIST_DCN32`, and related mask-list macros that draw from this generated namespace.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dmub/src/dmub_dcn32.c` includes this header and maps DCN32 register offsets, masks, and shifts into DMUB-facing structures.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/irq/dcn32/irq_service_dcn32.c`, `display/dc/gpio/dcn32/hw_translate_dcn32.c`, `display/dc/gpio/dcn32/hw_factory_dcn32.c`, and `display/dc/clk_mgr/dcn32/dcn32_clk_mgr.c` also include the same offset and shift/mask headers for DCN32 interrupt, GPIO, and clock-management integration.
- Shared display block code consumes the generated tables indirectly: HUBP code uses request/return timing and status fields; IPP/DPP code uses CNVC and cursor-converter fields; DSCL code uses scaler and line-buffer fields; color-management paths use CM post-CSC/gamut/gamma/dealpha fields; resource/debug paths use DPP CRC and host-read fields.

The generated DPP0/DPP1 macro naming is instance-specific. Higher-level helpers often define per-instance register tables using `SRI`/`SF` token-pasting rather than spelling every generated macro at the call site.

## Risks And Edge Cases

- Field drift is the primary risk. These are untyped integer constants, so an incorrect shift or mask can compile cleanly while causing the driver to update the wrong hardware bits.
- The range begins mid-register. Complete analysis of `HUBPREQ3_PREFETCH_SETTINGS` requires the previous chunk, because this chunk only contains its `VRATIO_PREFETCH` and `DST_Y_PREFETCH` masks.
- The range ends mid-register. Complete analysis of `CM1_CM_GAMCOR_RAMB_REGION_26_27` requires the next chunk, because this chunk contains the shifts and only the region-26 LUT-offset mask; the region-26 segment mask and both region-27 masks are outside this work item.
- Repeated DPP0/DPP1 register layouts make copy-generation mistakes easy to miss. A single bad instance suffix or mask can affect only one display pipe, producing connector-, plane-, or pipe-dependent failures.
- HUBPREQ/HUBPRET timing masks are tied to watermark, VM/PTE/meta fetch, vblank, flip, cursor, and p-state behavior. Bad masks can cause underflow, stutter, excessive latency, missed flip timing, blocked p-state changes, or power-management regressions.
- Interrupt/status fields in `HUBPRET3_HUBPRET_INTERRUPT` are event-sensitive. Incorrect mask/type/clear bits can cause missed vblank/read-line events, interrupt storms, or status bits that appear stuck.
- Cursor address, pitch, line, stereo, DMData, and TMZ fields can create visible corruption, wrong hot spot, stale cursor metadata, secure-display mistakes, or faults if programmed with the wrong field geometry.
- CNVC and CM fields affect user-visible pixels. Errors in pixel format, alpha, color key, CSC, gamut remap, degamma, gamma LUT, HDR multiplier, or coefficient-format masks can cause color shifts, washed-out HDR/SDR conversion, wrong alpha blending, or incorrect cursor colors.
- DSCL fields govern coefficient RAM, scale ratios, phase init, taps, overscan, line-buffer partitioning, and memory power. Bad masks can produce scaling artifacts, blank output, underflow, or memory-power transition bugs.
- LUT and PWL gamma programming uses index/data/control plus many compact region descriptors. Off-by-one or incomplete mask pairs can corrupt only specific gamma regions, making failures content-, HDR-, or calibration-dependent.
- Power-control/status fields are not ordinary data fields. Forcing or disabling memories through the wrong bits can hide in simple boot tests but fail under clock gating, idle entry/exit, suspend/resume, or multi-display stress.

## Test Signals

Useful validation should combine generated-header checks with DCN32 display behavior:

- Build AMDGPU display code with DCN32 enabled. Token-paste mismatches should surface in `dcn32_resource.c`, `dmub_dcn32.c`, IRQ/GPIO/clock modules, or shared register-table initializers.
- Mechanically verify that every complete register in this chunk has expected `__SHIFT`/`_MASK` pairs and that split-boundary exceptions are limited to `HUBPREQ3_PREFETCH_SETTINGS` at the beginning and `CM1_CM_GAMCOR_RAMB_REGION_26_27` at the end.
- Diff DPP0 and DPP1 repeated blocks in this range against each other and against nearby DCN generations where layout compatibility is expected.
- Exercise display modes that use pipe 3 and DPP0/DPP1 paths: cursor enable/disable/move, stereo cursor if supported, secure/TMZ cursor surfaces, scaling up/down, chroma paths, alpha planes, color keying, degamma, CSC, gamut remap, gamma LUT programming, HDR multiplier paths, CRC capture, suspend/resume, and runtime power management.
- Watch for visual artifacts, wrong colors, cursor corruption, scaling shimmer, blanking underflow, missed vblank/read-line IRQs, CRC mismatches, stuck update-pending bits, p-state allowance regressions, and failures that appear only on one pipe or after power transitions.

## Cross-Chunk Notes

This is chunk 5 of 92 for `dcn_3_2_0_sh_mask.h`. The final per-file report should merge this with adjacent chunks before making complete claims about `HUBPREQ3_PREFETCH_SETTINGS` or `CM1_CM_GAMCOR_RAMB_REGION_26_27`, and with all remaining chunks before summarizing the whole DCN 3.2.0 shift/mask namespace.
