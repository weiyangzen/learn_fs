# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_5_1_sh_mask.h lines 19897-22113

## Purpose

This chunk is generated AMD DCN 3.5.1 register field metadata. It contains no executable C code; it publishes preprocessor constants that describe field bit positions and field masks inside DCN hardware registers. The matching offset header supplies register addresses, while this shift/mask header supplies the layout used by AMDGPU display code to pack and decode MMIO register values without clobbering unrelated bits.

The assigned range starts in the middle of `FMT0_FMT_BIT_DEPTH_CONTROL` masks, then covers output formatter, display pattern generator, OPP buffer, OPP pipe, OPP pipe CRC, DSCRM, DC perfmon, ODM/OPTC input, OTG0 timing-generator, and the first half of OTG1 timing-generator field definitions. It ends at `OTG1_OTG_CRC3_DATA_B__CRC3_B_CB_MASK`; the companion `CRC3_C` mask and later OTG1 CRC signature/static-screen/3D/global-sync/DRR fields continue in the next chunk.

Although this source lives under a local `ceph-client` mirror path, this file is AMDGPU display-driver hardware metadata and is not related to Ceph or distributed filesystem behavior.

## Important APIs, Types, And Macros

There are no functions, structs, enums, variables, includes, allocations, or locks in this chunk. The effective API is the generated macro namespace:

- `<REGISTER>__<FIELD>__SHIFT`: zero-based bit position for a field in a hardware register.
- `<REGISTER>__<FIELD>_MASK`: bit mask for the same field.
- Instance prefixes such as `FMT0_`, `DPG2_`, `OPPBUF3_`, `ODM1_`, `OTG0_`, and `OTG1_` identify repeated display-pipe or timing-generator register instances.

The range contains 2,217 macro lines covering 337 distinct register names. Major families are:

- `FMT0_` through `FMT3_`: output formatter fields for clamp bounds, dynamic expansion, stereo sync override, pixel encoding, subsampling, CbCr bit-reduction bypass, double-buffer update-pending state, truncation, spatial/temporal dithering, FRC selectors, random seeds, clamp color format, side-by-side stereo active width, 4:2:0 memory power controls, and 4:2:2 left-edge behavior. `FMT0` is partial because the line range starts after its early bit-depth shift definitions.
- `DPG0_` through `DPG3_`: display pattern generator enable/mode, dynamic range, bit depth, horizontal and vertical resolution selectors, ramp offsets/increments, active dimensions, two-color RGB/YCbCr pattern values, segment offsets, and double-buffer-pending status.
- `OPPBUF0_` through `OPPBUF3_`: OPP buffer active width, display segmentation, overlap pixels, pixel repetition, double-buffer-pending state, 3D vertical active-space sizes, dummy data, and padded segment pixel count.
- `OPP_PIPE0_` through `OPP_PIPE3_`: OPP pipe clock enable/status and digital bypass fields.
- `OPP_PIPE_CRC0_` through `OPP_PIPE_CRC3_`: OPP pipe CRC enable, continuous mode, stereo/interlace mode, pixel/source select, one-shot pending, CRC masks, and ARGB/C result fields.
- `OPP_TOP_CLK_CONTROL` and `OPP_ABM_CONTROL`: top-level OPP fine-grain clock-gating and ambient-backlight-management mux fields.
- `DSCRM0_` through `DSCRM3_`: DSC forwarding configuration, including forward enable, OPP pipe source, enable status, power-down force, and power-down state.
- `DC_PERFMON14_*`: DC performance monitor 14 fields for counter control, selection, enable/clear, counter state, threshold/current values, interrupt status/ack bits, and high/low counter readback.
- `ODM0_` through `ODM3_`: OPTC input soft reset, underflow interrupt/status/clear/current fields, data source segment count and source selection, DSC data format/mode, bytes-per-pixel, segment and slice width, input clock control, memory selection/status, spare register, and double-buffer-pending state.
- `OTG0_*`: a broad timing-generator surface for horizontal/vertical totals, blanking, syncs, triggers A/B, force-count-now, master enable, stereo/interlace, pixel readback, status/position/frame counters, snapshots, interrupt masks/types/status/clears, update locks, double-buffer state, vertical interrupt 0/1/2, CRC controls/windows/results/signature masks, static-screen detection, 3D structure, global sync lock, DRR timing/status, DTO constants, request controls, DSC start position, pipe update status, and spare registers.
- `OTG1_*`: the same timing-generator layout begins for instance 1 and runs through CRC data registers in this chunk.

## Control Flow

This header has no runtime control flow. Runtime use is indirect and macro-driven:

1. DCN 3.5.1 resource and DMUB code include `dcn_3_5_1_offset.h` and this `dcn_3_5_1_sh_mask.h` header.
2. Register-table macros such as `SR`, `SRI`, `SF`, and block-specific wrappers paste register and field tokens into names from this file.
3. Constructors populate per-block offset, shift, and mask tables for OPP, DSC/DSCRM, OPTC/ODM/timing-generator, IRQ, DMUB-accessible registers, and related display resources.
4. Operational code later uses helpers such as `REG_READ`, `REG_WRITE`, `REG_UPDATE`, `REG_UPDATE_N`, `REG_SET`, `REG_GET`, and `REG_WAIT`. Those helpers use the shifts and masks from this chunk to update hardware fields while preserving other register bits.

The macros do not encode programming order. Modeset and validation paths still need to apply hardware sequencing rules: lock and unlock updates, wait for double-buffer-pending bits to clear, program timing changes around blanking boundaries, clear sticky interrupt/status bits correctly, and sequence DSC/ODM/OPP/OTG changes with pipe ownership.

## State And Persistence Behavior

The file stores no software state and persists nothing by itself. It describes MMIO-backed GPU state:

- FMT registers hold per-output-pipe color/output formatting state: clamp ranges, pixel encoding, subsampling, truncation, dither mode/depth, temporal dither state, random seeds, 4:2:0 memory power state, 4:2:2 edge handling, and update-pending readback.
- DPG registers hold diagnostic/test-pattern state used for validation, blank pattern generation, and controlled output during transitions.
- OPPBUF and OPP pipe registers hold active-width, segmentation, pixel repetition, 3D dummy-data, clock, and bypass state for the output pixel processor path.
- OPP pipe CRC and OTG CRC registers hold capture configuration, CRC windows, source selections, masks, one-shot pending bits, and captured result data used by debug and automated validation paths.
- DSCRM registers hold DSC-to-OPP forwarding state and status, including enable, source pipe, and power-down fields.
- ODM/OPTC input registers hold segment routing, input/output segment counts, DSC mode, bytes-per-pixel, segment/slice widths, input clock enable/status, underflow flags, memory selection, and double-buffer state.
- OTG registers hold timing-generator state: programmed timings, dynamic refresh totals, triggers, interrupts, status counters, update locks, vertical interrupt positions, stereo/interlace control, global sync, DRR windows, DTO programming, DSC start position, pipe update status, static-screen detection, and spare registers.
- DC perfmon 14 registers hold programmable performance counter selection, thresholds, current values, interrupt bits, enable/clear fields, and readback state.

Persistence is hardware-defined. Many configuration bits remain until modeset reprogramming, power gating, suspend/resume, or ASIC reset. Status, pending, interrupt, snapshot, one-shot, clear, and perf-counter fields may be read-only, sticky, self-clearing, write-one-to-clear, or timing-sensitive. This generated header only gives bit layout; it does not describe access type or side effects.

## Dependencies And Integration Points

This chunk must stay synchronized with AMD's generated DCN 3.5.1 register database and with these local consumers:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_5_1_offset.h`, the matching register offset/base-index header.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dmub/src/dmub_dcn351.c`, which includes the DCN 3.5.1 offset and shift/mask headers and uses `FD_MASK`/`FD_SHIFT` through `DMUB_DCN35_FIELDS()` to initialize DMUB register tables.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/resource/dcn351/dcn351_resource.c`, which includes this header when constructing DCN 3.5.1 display resources and expanding register/field tables.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/opp/dcn10/dcn10_opp.h`, `dcn10_opp.c`, and `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/opp/dcn35/dcn35_opp.c`, which consume FMT, OPPBUF, OPP pipe, OPP CRC, and DSCRM field names for color depth, dithering, CRC readback, and OPP register-state capture.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dsc/dcn35/dcn35_dsc.c` and `dcn35_dsc.h`, which use `DSCRM_DSC_FORWARD_CONFIG` fields to query and program DSC forwarding.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/optc/dcn35/dcn35_optc.c` and `dcn35_optc.h`, which consume ODM/OPTC and OTG masks for ODM segment source selection, CRC configuration, timing-generator status, and update sequencing.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/irq/dcn351/irq_service_dcn351.c` and the shared DCN35 IRQ support, which rely on OTG interrupt mask/status/clear/type field definitions.
- Shared hardware sequencing code under `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/hwss/dcn35/` and `dc/hwss/dcn351/`, which coordinates the modeset, blanking, power, pipe, and update-lock paths that ultimately touch these registers.

The integration contract is token spelling plus numeric correctness. A missing or renamed macro usually fails compilation through token-pasted field tables. A stale or incorrect numeric shift/mask can compile cleanly but program the wrong hardware bits at runtime.

## Risks And Edge Cases

- The chunk boundary is artificial. It begins after the `FMT0_FMT_BIT_DEPTH_CONTROL` shift definitions and early masks, and ends one line before `OTG1_OTG_CRC3_DATA_B__CRC3_C_MASK`. File-level analysis must merge adjacent chunks to avoid treating split register definitions as absent.
- These are untyped integer constants. A wrong mask or shift can corrupt adjacent register fields with no compiler diagnostics.
- FMT bit-depth, dithering, clamp, pixel-encoding, subsampling, and 4:2:0/4:2:2 fields directly affect visible output. Errors can present as banding, wrong color format, corruption on subsampled modes, bad stereo formatting, or failed update-pending waits.
- DPG fields are often diagnostic or transition-path tools. Incorrect dimensions, segment offsets, colors, or pending-state masks can make pattern generation or blanking validation misleading.
- OPP clock/bypass and OPPBUF segmentation fields are clock/power and pipe-topology sensitive. Bad masks can leave the OPP path clock gated, report false clock state, bypass processing, or break multi-segment output.
- DSCRM forwarding and ODM/OPTC segment-selection fields are high-risk for DSC and ODM combine. Wrong source pipe, segment count, DSC mode, bytes-per-pixel, or slice/segment width can break high-bandwidth modes even when simple single-pipe modes still work.
- OTG timing, vertical interrupt, trigger, force-count, update-lock, and double-buffer fields are sequencing-sensitive. Incorrect fields can cause missed vblank/vupdate interrupts, stuck update-pending waits, bad dynamic-refresh behavior, global-sync failures, or display hangs during modeset.
- CRC fields are used as validation signals. Incorrect OTG/OPP CRC source, window, mask, or result fields can invalidate automated display tests and obscure real rendering regressions.
- Perfmon fields are diagnostic but side-effect-sensitive; wrong enable/clear/ack/threshold masks can hide overflows or produce misleading performance telemetry.

## Test Signals

Useful validation combines generated-header checks with hardware/display behavior:

- Build AMDGPU/DC with DCN 3.5.1 enabled. Token-pasted tables in resource, DMUB, OPP, DSC, OPTC, and IRQ code should catch missing or renamed macro definitions.
- Mechanically verify each `__SHIFT` in the range has the expected matching `_MASK`, and verify masks align with the shift and expected bit width. Split boundary definitions should be reconciled with neighboring chunks before flagging mismatches.
- Diff this range against AMD's authoritative DCN 3.5.1 register database and nearby generated headers when compatibility is expected.
- Exercise normal and repeated modesets on all available pipes: enable/disable, blank/unblank, suspend/resume, hotplug, resolution/refresh changes, and pipe reassignment.
- Exercise color-format coverage that depends on FMT fields: 6/8/10/12 bpc, truncation, spatial and temporal dithering, RGB/YCbCr, 4:2:0, 4:2:2, and stereo cases.
- Exercise DSC and ODM paths: DSC enable/disable, DSC forwarding to OPP, high-bandwidth modes, ODM combine/split, segment source changes, and DSC slice width or bytes-per-pixel changes.
- Exercise OPP and OTG CRC debug paths in one-shot and continuous modes, with windowed CRC, stereo/interlace modes, and expected frame signatures.
- Monitor kernel logs, DC traces, hardware readback, debugfs CRC output, and display output for underflow, stuck double-buffer/update-pending bits, missed interrupts, CRC mismatches, black screens, link fallback, corruption, or timing-generator wait timeouts.

## Cross-Chunk Notes

Adjacent chunks are required for a complete file-level report. The previous chunk contains the beginning of `FMT0_FMT_BIT_DEPTH_CONTROL` and earlier FMT0 fields. The next chunk continues `OTG1_OTG_CRC3_DATA_B` with `CRC3_C_MASK` and then covers OTG1 CRC signature masks, static-screen controls, 3D structure, global sync, DRR, DTO, request, DSC start, pipe update, and spare fields.
