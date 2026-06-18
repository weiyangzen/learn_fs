# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_1_4_sh_mask.h lines 61483-61832

## Scope

This chunk is the final slice of the generated DCN 3.1.4 register-field shift/mask header `dcn_3_1_4_sh_mask.h`. It contains C preprocessor constants only: `_SHIFT` macros for field low-bit positions, `_MASK` macros for raw register bit masks, register-name comments, address-block comments, and the closing `#endif`. There are no functions, structs, enums, allocations, branches, loops, or driver-owned state objects in this range.

The slice starts in the tail of the `ABM3_DC_ABM1_ACE_OFFSET_SLOPE_3` definitions, completes the `ABM3` automatic backlight module/statistics field definitions, then defines small `DPIA_MU`, HDA `AZCONTROLLER1`, `AZENDPOINT1`, and `AZINPUTENDPOINT1` register field groups. It ends the whole generated header.

## Purpose And Hardware Surface

The purpose of this header range is to provide the bit-layout ABI between AMDGPU Display Core code and DCN 3.1.4 display hardware. Companion offset headers, especially `dcn_3_1_4_offset.h`, provide the MMIO register addresses and base indices; this file provides the masks and shifts used by register helper macros to pack writes and decode readbacks without hard-coded bit positions.

Major hardware areas represented here:

- `ABM3_DC_ABM1_*` fields describe the third ABM instance's `ABM1` control and result register layout. The visible fields cover adaptive contrast enhancement slopes, offsets, thresholds, histogram/luma/backlight statistics control, missed-frame status, sample rates, histogram-bin shift metadata, histogram results, and a backlight master lock bit.
- `dce_dpia_dpia_mu0_dpiadec` fields describe the DPIA micro-unit RBBM interface timeout and invalid-access status surface. These fields expose timeout delay/hold, timeout disable, invalid access flag/type/address, timeout readback, and status clear.
- `dce_dc_hda_azcontroller_azdec` fields describe the display HDA controller command/response DMA rings and immediate-command path: CORB, RIRB, immediate command output, immediate response input, busy/result status, and DMA position buffer base address fields.
- `dce_dc_hda_azendpoint_azdec` fields provide endpoint immediate-command output data/index fields.
- `dce_dc_hda_azinputendpoint_azdec` fields provide input-endpoint immediate-command input data/index fields.

The chunk is hardware-definition data rather than active logic. Its correctness matters because higher-level display, DMUB, ABM, audio, interrupt, and diagnostics code uses these symbols as the source of truth for MMIO field layout.

## Important Definitions

The exported API is the generated macro naming convention:

- `<REGISTER>__<FIELD>__SHIFT` gives the low bit position for a field.
- `<REGISTER>__<FIELD>_MASK` gives the unshifted bit mask within the register.
- `//<REGISTER>` comments group the field macros by hardware register.
- `// addressBlock: ...` comments mark the hardware aperture for following registers.

Important field families in this chunk:

- `ABM3_DC_ABM1_ACE_OFFSET_SLOPE_3` and `ABM3_DC_ABM1_ACE_OFFSET_SLOPE_4` provide 11-bit adaptive contrast enhancement slope fields, 11-bit offset fields starting at bit 16, and an `ABM1_ACE_LOCK` bit at bit 31. The range begins mid-register for slope/offset 3, so earlier fields for this register are in the previous chunk.
- `ABM3_DC_ABM1_ACE_THRES_12` and `ABM3_DC_ABM1_ACE_THRES_34` pack 10-bit ACE thresholds in the low and high halves of the register. `ACE_THRES_34` also exposes ignore-master-lock, double-buffer readback, update-pending, and lock bits in bits 28-31.
- `ABM3_DC_ABM1_ACE_CNTL_MISC` reports and clears ACE register writes that missed the target frame.
- `ABM3_DC_ABM1_HGLS_REG_READ_PROGRESS` exposes histogram (`HG`), luma statistics (`LS`), and backlight (`BL`) register-read-in-progress bits, missed-frame bits, and corresponding missed-frame clear bits.
- `ABM3_DC_ABM1_HG_MISC_CTRL` configures histogram/statistics behavior: number of bins, VMAX mode, fine mode, bin bit width, over-scan pixel processing, double-buffered readback, frame-start display selection, update-at-frame-start, master-lock bypass, update-pending readback, and HGLS register lock.
- `ABM3_DC_ABM1_LS_*` read back luma statistics: sum of luma, min/max luma, filtered min/max luma, pixel count plus sum MSBs, threshold programming for min/max pixel-value counters, and 24-bit min/max pixel-value counts.
- `ABM3_DC_ABM1_HG_SAMPLE_RATE` and `ABM3_DC_ABM1_LS_SAMPLE_RATE` enable sample-rate counters, reset their frame counters, program 8-bit frame-count values, program initial reset values, and share the HGLS register lock bit.
- `ABM3_DC_ABM1_HG_BIN_*` fields expose packed histogram-bin shift flags and shift index words for bins 1-32.
- `ABM3_DC_ABM1_HG_RESULT_1` through `ABM3_DC_ABM1_HG_RESULT_24` expose full 32-bit histogram result words.
- `ABM3_DC_ABM1_BL_MASTER_LOCK` exposes the backlight master lock bit at bit 31.
- `DPIA_MU_RBBMIF_TIMEOUT_CTRL`, `DPIA_MU_RBBMIF_TIMEOUT_CTRL2`, and `DPIA_MU_RBBMIF_STATUS` define timeout delay/hold, timeout disable, invalid access flag/type/address, timeout status readback, and invalid-access status clear.
- `AZCONTROLLER1_CORB_*` fields define the HDA CORB write pointer, read pointer/reset, control, status, and ring size/capability fields.
- `AZCONTROLLER1_RIRB_*` fields define lower/upper RIRB base address, write pointer/reset, response interrupt count, control, status, and ring size/capability fields.
- `AZCONTROLLER1_IMMEDIATE_*` fields define immediate command output payload/codec address, output data/index windows, response input readback, and busy/result-valid status bits.
- `AZCONTROLLER1_DMA_POSITION_*` fields define the DMA position buffer enable bit and the split lower/upper base-address fields. The lower address reserves bits 1-6 as unimplemented and stores the aligned base at bit 7.
- `AZENDPOINT1_AZENDPOINT_IMMEDIATE_COMMAND_OUTPUT_INTERFACE_*` and `AZINPUTENDPOINT1_AZENDPOINT_IMMEDIATE_COMMAND_INPUT_INTERFACE_*` define endpoint immediate-command data and 17-bit index fields.

## Control Flow And State Behavior

There is no executable control flow in this header. Runtime behavior appears when AMDGPU Display Core, DMUB, ABM, or HDA-related code combines these constants with matching `reg*` offsets and register helpers such as `REG_GET`, `REG_SET`, `REG_UPDATE`, `REG_WRITE`, generated `DMUB_SF` field tables, or equivalent MMIO accessor wrappers.

A typical use path is:

1. Select a DCN 3.1.4 register address and base index from `dcn_3_1_4_offset.h`.
2. Select the matching field mask and shift from this header.
3. Pack a value, extract a readback, or build a read/modify/write mask through the display register abstraction.
4. Let hardware store, latch, consume, report, or clear the represented field.

The state represented here is hardware state:

- Persistent configuration fields include ABM ACE slopes, offsets, thresholds, sample-rate controls, histogram mode controls, readback/double-buffer options, frame-start update controls, lock bits, DPIA timeout delay/hold/disable controls, HDA CORB/RIRB ring base/size/control registers, immediate command output fields, and DMA position buffer enable/base programming.
- Volatile readback fields include ABM luma sums, min/max luma, filtered min/max luma, pixel counts, min/max pixel-value counts, histogram-bin metadata, histogram result words, update-pending flags, read-in-progress flags, missed-frame flags, DPIA invalid-access and timeout status, HDA CORB/RIRB status, immediate command busy, and immediate result valid.
- Side-effecting write fields include missed-frame clear bits, sample-rate frame-counter resets, lock/master-lock bits when used to stage updates, `RBBMIF_INVALID_ACCESS_STATUS_CLEAR`, CORB/RIRB pointer reset bits, interrupt/status clear-style HDA fields, immediate command write windows, and DMA position buffer enable.
- Several ABM fields explicitly expose double-buffer and frame-start update behavior. Incorrect writes can land in the wrong frame, be missed by the hardware latch, or leave an update pending until a later vertical boundary.

The sequencing rules are not encoded in the macros. Callers must still respect display lock/update timing, ABM ownership, frame-start/vblank timing, display power state, register double-buffering, DPIA timeout/fault clearing semantics, and HDA ring/command protocols.

## Dependencies And Integration Points

This chunk depends on the matching DCN 3.1.4 register-address definitions in `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_1_4_offset.h`. For the visible fields, that header maps examples such as `regABM3_DC_ABM1_HG_MISC_CTRL`, `regABM3_DC_ABM1_HG_RESULT_24`, `regABM3_DC_ABM1_BL_MASTER_LOCK`, `regDPIA_MU_RBBMIF_TIMEOUT_CTRL`, `regAZCONTROLLER1_CORB_WRITE_POINTER`, `regAZCONTROLLER1_IMMEDIATE_COMMAND_STATUS`, `regAZCONTROLLER1_DMA_POSITION_LOWER_BASE_ADDRESS`, and endpoint immediate-command registers to concrete offsets and base indices.

Known source integration points include:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dmub/src/dmub_dcn314.c`, which includes `dcn_3_1_4_sh_mask.h` and the matching offset header to build the DCN 3.1.4 DMUB register interface.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/irq/dcn314/irq_service_dcn314.c`, which includes this header for DCN 3.1.4 interrupt/register field definitions.
- ABM/backlight and panel-control code paths that program automatic brightness management, adaptive contrast enhancement, histogram collection, luma statistics, and backlight locks through generated ABM register lists.
- DMUB/display diagnostics and hardware-sequencing code that may configure or decode DPIA RBBMIF timeout/invalid-access behavior.
- HDA/audio controller paths that use AZ controller register definitions to manage command output rings, response input rings, immediate codec commands, and DMA position buffer programming.
- Other generated ASIC revision headers in the same directory. The same field families appear across DCN 3.0, 3.2, 3.5.1, 3.6, and 4.1 headers, so maintenance often involves cross-revision comparison while preserving DCN 3.1.4-specific offsets and field availability.

Because the file is generated, most use is indirect through macros. A missing or misspelled field usually fails compilation where a `REG_FIELD`, `SF`, `DMUB_SF`, or register-list macro expands. A wrong numeric mask or shift can compile cleanly and cause runtime MMIO misprogramming.

## Risks And Maintenance Notes

- Numeric drift from the DCN 3.1.4 register specification is the primary risk. Incorrect masks or shifts can corrupt ABM thresholds, histogram readbacks, HDA ring pointers, immediate command fields, or timeout status decoding.
- This chunk begins in the middle of `ABM3_DC_ABM1_ACE_OFFSET_SLOPE_3`. The merge/reconciliation lane should preserve that neighboring chunks are needed for the full per-file story and should not infer that the register starts at line 61483.
- ABM field names are repetitive and instance-qualified. Confusing `ABM3` with another ABM instance, or confusing `HG`, `LS`, `BL`, and `ACE` fields, can target a valid but wrong hardware function.
- Lock bits and frame-start update bits are timing-sensitive. Using generic read/modify/write flows without observing ABM double-buffering and vblank/frame-start constraints can produce missed-frame flags or stale readbacks.
- Several status and clear fields share the same register family. `ABM1_ACE_REG_WR_MISSED_FRAME_CLEAR`, HGLS missed-frame clear bits, and `RBBMIF_INVALID_ACCESS_STATUS_CLEAR` should be treated as write-side effects, not persistent configuration values.
- Histogram and luma result fields are full-width or packed counters. Consumers must preserve the documented masks when combining `LS_SUM_OF_LUMA` with `LS_SUM_OF_LUMA_MSB`, interpreting 24-bit pixel counts, or reading `HG_RESULT_1..24`.
- HDA ring fields use small pointer and capability widths. Incorrect CORB/RIRB size, reset, DMA-enable, or base-address packing can break codec command transport or DMA position reporting.
- The AZ endpoint and input-endpoint data/index registers share similar offsets and names. Data versus index and output versus input confusion can still compile if a wrong macro exists.
- The closing `#endif` belongs to the whole generated header. Accidental edits near this chunk can break inclusion of the entire DCN 3.1.4 mask file.

## Test Signals

Useful validation signals for changes touching this chunk include:

- Compile coverage for AMDGPU Display Core with DCN 3.1.4 enabled. This catches missing macro names, malformed generated constants, and broken include guards.
- Static comparison against the authoritative DCN 3.1.4 register database or a regenerated `dcn_3_1_4_sh_mask.h`, especially for bit positions, masks, and register/field spelling.
- Cross-revision spot checks against adjacent generated headers where hardware is expected to be compatible, while confirming DCN 3.1.4-specific differences are intentional.
- ABM functional testing on DCN 3.1.4 hardware: backlight changes, adaptive brightness/contrast behavior, histogram/luma readback sanity, missed-frame counters remaining clear during normal updates, and no stuck HGLS update-pending/read-in-progress flags.
- Display diagnostics for DPIA RBBMIF timeout and invalid-access handling, including status decode and clear behavior after induced or logged invalid accesses.
- Audio-over-display testing for HDA codec command transport: CORB/RIRB ring operation, immediate command busy/result-valid behavior, response interrupts, and DMA position buffer updates during playback.
- Runtime register dumps before and after ABM, DPIA, or HDA operations. Packed values should affect only the intended masked bits and preserve unrelated fields.

## Open Questions For Merge

- The exact high-level consumers for the `ABM3_DC_ABM1_*` fields are likely generated register lists in ABM resource code outside this chunk. The final per-file report should connect this end-of-file chunk with earlier ABM chunks that define the same instance's control, coefficient, and backlight fields.
- This chunk documents field layout only. The final merged report should avoid claiming behavioral sequencing beyond what is visible in the macros unless corroborated by functional source files.
