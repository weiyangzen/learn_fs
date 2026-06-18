# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_5_0_sh_mask.h lines 19910-22126

## Purpose

This chunk is generated AMD DCN 3.5.0 register field metadata. It contains no executable C logic; it publishes `#define` constants for bit shifts and masks used by AMDGPU display code when packing, updating, and reading MMIO register fields. The companion offset header supplies register addresses, while this file supplies the field layout inside each register.

The assigned range starts in the middle of output-pixel-processor instance 0 metadata at `FMT0_FMT_BIT_DEPTH_CONTROL`, repeats FMT/DPG/OPPBUF/OPP_PIPE/OPP_PIPE_CRC field masks for output instances 0 through 3, covers top-level OPP and DSC forwarding controls, covers DC performance monitor 14, covers ODM/OPTC input controls for instances 0 through 3, then covers all of OTG0 timing-generator fields and the first half of OTG1 through `OTG1_OTG_CRC2_DATA_B`.

Although the repository path is under a local `ceph-client` mirror, this file is AMDGPU display-driver hardware metadata. It is unrelated to Ceph or distributed filesystem behavior.

## Important APIs, Types, And Macros

There are no functions, structs, enums, variables, includes, allocation sites, or locks in this chunk. The public interface is the generated macro namespace:

- `<REGISTER>__<FIELD>__SHIFT`: bit position of a field inside a 32-bit hardware register.
- `<REGISTER>__<FIELD>_MASK`: bit mask for that field.
- Instance prefixes such as `FMT0_`, `DPG1_`, `OPPBUF2_`, `ODM3_`, `OTG0_`, and `OTG1_` expose per-pipe/per-block copies of the same hardware layout.

Major macro families in this slice:

- `FMT0_` through `FMT3_`: output formatter controls for component clamps, dynamic expansion, stereo sync override, spatial/temporal dithering, truncation, random seeds, pixel encoding, 4:2:0 memory power, 4:2:2 edge behavior, and double-buffer update-pending state. The chunk starts after the earlier part of `FMT0_FMT_CONTROL`, so instance 0 is split across chunks.
- `DPG0_` through `DPG3_`: display pattern generator controls, ramp programming, active dimensions, two-color RGB/YCbCr values, segment offsets, and double-buffer pending status.
- `OPPBUF0_` through `OPPBUF3_`: OPP buffer active width, display segmentation, overlap pixels, pixel repetition, 3D dummy-data and vertical-space parameters, and segment-padding fields.
- `OPP_PIPE0_` through `OPP_PIPE3_`: OPP pipe clock enable/status and digital bypass controls.
- `OPP_PIPE_CRC0_` through `OPP_PIPE_CRC3_`: OPP pipe CRC enable/continuous mode, stereo/interlace mode, pixel/source selection, one-shot pending, masks, and CRC result fields.
- `OPP_TOP_CLK_CONTROL` and `OPP_ABM_CONTROL`: top-level OPP fine-grain clock-gating and ambient-backlight-management selection controls.
- `DSCRM0_` through `DSCRM3_`: DSC forwarding selectors that route DSC output toward an OPP pipe and expose enable/power-down related fields.
- `DC_PERFMON14_*`: performance counter control, selection, enable/clear, threshold, overflow/current-value, and state fields for a DC-local perfmon block.
- `ODM0_` through `ODM3_`: OPTC/ODM input global controls, segment source selection, data format and DSC mode, bytes-per-pixel, segment/slice width, input pixel clock enable, underflow controls, memory selection, and spare registers.
- `OTG0_*`: complete timing-generator field coverage for horizontal and vertical totals, blanking, syncs, trigger A/B, force-count interrupts, stereo/interlace, position/frame counters, snapshot, vertical interrupt 0/1/2, CRC windows/results/signature masks, static-screen detection, 3D structure, global sync lock, DRR, DTO, request control, DSC start position, pipe update status, and spare fields.
- `OTG1_*`: the same timing-generator layout begins for instance 1 and runs through CRC2 data in this chunk. Later OTG1 static-screen/global/DRR fields continue in the following chunk.

Within lines 19910-22126 there are 335 distinct register names represented by paired or grouped shift/mask macros. The largest family is OTG, followed by FMT, DPG, OPPBUF, OPP pipe CRC, ODM, DC perfmon, DSCRM, and top-level OPP fields.

## Control Flow

This header has no runtime control flow. Runtime use is indirect:

1. DCN35 resource and DMUB code include `dcn_3_5_0_offset.h` and `dcn_3_5_0_sh_mask.h`.
2. Register-table macros such as `SR`, `SRI`, `SF`, and block-specific wrappers paste register and field tokens into names from this file.
3. Constructors populate per-block register-offset, shift, and mask tables for OPP, OPTC/timing generator, DSC/ODM routing, performance monitoring, and DMUB-accessible DCN35 registers.
4. Operational code later calls helpers such as `REG_READ`, `REG_WRITE`, `REG_UPDATE`, `REG_UPDATE_N`, `REG_GET`, and wait/poll helpers. Those helpers use this chunk's shifts and masks to preserve unrelated hardware bits while programming output format, pattern generation, CRC capture, ODM/DSC routing, timing, vertical interrupts, global sync, and dynamic refresh behavior.

The macros do not encode sequencing. Modeset code still has to lock and unlock update domains, wait for double-buffer pending bits, sequence OPP/OPTC/DSC changes around blanking, and respect interrupt/status clear semantics supplied by hardware programming rules.

## State And Persistence Behavior

The chunk stores no software state and persists nothing by itself. It describes MMIO-backed GPU state:

- FMT and OPPBUF registers hold per-output-pipe format state: truncation, dither mode/depth, random seeds, clamp format, pixel encoding, subsampling, active width, segmentation, and 3D/pixel repetition parameters.
- DPG registers hold test-pattern state used for diagnostics, validation, and blank-pattern programming.
- OPP pipe and OPP CRC registers hold clock/bypass state, CRC capture configuration, CRC result registers, and one-shot pending status.
- DSCRM registers hold DSC-to-OPP forwarding state, including which OPP pipe receives DSC data.
- ODM/OPTC input registers hold source-segment mapping, segment count, DSC mode, bytes-per-pixel, slice/segment width, input clock enable, memory selection, and underflow status/clear fields.
- OTG registers hold timing-generator state: programmed horizontal/vertical timings, dynamic refresh totals, trigger/interrupt masks and statuses, frame/position counters, stereo/interlace state, CRC windows/results, static-screen detection, global sync lock state, DRR windows, DTO constants, and pipe-update pending status.
- DC perfmon 14 registers hold programmable counter selection, enable, clear, threshold, current-value, overflow, and state fields.

Persistence is hardware-defined. Configuration fields usually remain until modeset reprogramming, power gating, suspend/resume, or ASIC reset. Status, pending, interrupt, clear, snapshot, CRC one-shot, and counter fields can be read-only, sticky, self-clearing, write-one-to-clear, or timing-sensitive. This generated mask file does not identify access type.

## Dependencies And Integration Points

This chunk depends on AMD's generated DCN 3.5.0 register database and must remain synchronized with:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_5_0_offset.h`, which provides the matching register offsets and base indices.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/resource/dcn35/dcn35_resource.c`, which includes the generated DCN35 headers and constructs DCN35 display resources.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dmub/src/dmub_dcn35.c`, where `dmub_srv_dcn35_regs_init()` maps generated field masks and shifts into DMUB register tables.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/opp/dcn10/dcn10_opp.h` and `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/opp/dcn35/dcn35_opp.c`, which consume FMT, OPPBUF, OPP pipe, DPG, DSCRM, and OPP CRC field names for output-pixel-processor setup and state readback.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/optc/dcn35/dcn35_optc.h` and `dcn35_optc.c`, whose DCN35 timing-generator field lists consume the OTG/OPTC masks for CRC, update-pending, clock-gating, vertical interrupt, DRR, and timing behavior.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/link/link_dpms.c`, which reaches the OPTC DSC programming path when enabling or disabling DSC for a stream.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/core/dc_hw_sequencer.c`, which coordinates OPP/OPTC/ODM update sequencing, blanking waits, double-buffer waits, and pipe update state.

The main integration pattern is token pasting, so macro spelling is effectively a source-level ABI between generated headers and shared driver tables. Missing, renamed, or stale field names can break compilation; incorrect numeric masks can compile cleanly while corrupting runtime hardware programming.

## Risks And Edge Cases

- Generated masks are untyped constants. A wrong shift or mask can silently affect neighboring fields and show up only as display corruption, CRC mismatch, blanking failure, or timing instability.
- The chunk boundary is artificial. It begins after `FMT0_FMT_CONTROL` shifts/masks have already started in the previous chunk and ends before OTG1's later static-screen, global sync, DRR, DTO, request, DSC-start, and pipe-update fields. File-level analysis must reconcile adjacent chunks.
- FMT dither/truncation/pixel-encoding fields directly affect color depth and subsampling output. Bad masks can cause banding, incorrect RGB/YCbCr conversion behavior, or format-specific corruption.
- DPG and blank-pattern fields are used in diagnostic and transition paths. Incorrect pattern or dimension masks can make blanking/update waits misleading during ODM or pipe transitions.
- OPP pipe clock and bypass bits are power/clock-sensitive. Incorrect masks can leave an output path clock-gated, report false clock status, or bypass digital processing unexpectedly.
- OPP and OTG CRC fields are test/debug critical. Bad window, source-select, one-shot-pending, or result masks can invalidate CRC-based diagnostics and automated display validation.
- ODM/OPTC segment mapping and DSC mode fields are high-risk for wide/high-bandwidth modes. Wrong segment source, segment-count, bytes-per-pixel, slice-width, or DSC-mode masks can break ODM combine, DSC output routing, or multi-pipe timing.
- OTG timing, interrupt, global sync, DRR, and update-lock fields are sequencing-sensitive. Incorrect masks can cause missed vertical interrupts, stuck update-pending bits, invalid dynamic refresh timing, stereo/interlace regressions, or hangs in wait loops.
- Perfmon counter fields are diagnostic but side-effect-sensitive; wrong enable/clear/threshold masks can hide overflows or produce misleading performance telemetry.

## Test Signals

Useful validation is mostly generated-header consistency plus hardware behavior:

- Build AMDGPU/DC with DCN35 support enabled. Token-pasting consumers in resource, DMUB, OPP, OPTC, DSC, and timing-generator code should catch missing or renamed macros.
- Mechanically verify that every `__SHIFT` macro in this line range has the expected matching `_MASK` macro and that each mask aligns with its shift and expected field width.
- Diff the chunk against AMD's authoritative DCN 3.5.0 register database and nearby generated headers such as `dcn_3_5_1_sh_mask.h` or older DCN 3.x headers when hardware compatibility is expected.
- Exercise normal modesets across all active OPP/OTG instances, including pipe enable/disable, blank/unblank, suspend/resume, hotplug, and repeated timing changes.
- Exercise high-bandwidth and ODM/DSC paths: 2:1 or 4:1 ODM combine where supported, DSC enable/disable, native subsampled DSC formats, slice-width changes, and link DPMS transitions.
- Exercise color-output paths that depend on FMT fields: 6/8/10/12 bpc modes, temporal and spatial dithering, truncation, RGB/YCbCr, 4:2:0, and 4:2:2 output formats.
- Use CRC and debugfs-style validation where available: OPP CRC, OTG CRC windows, one-shot and continuous CRC modes, stereo/interlace CRC cases, and compare expected frame signatures.
- Monitor kernel logs, DC traces, hardware readback, and display output for underflow, stuck update-pending bits, missed vertical interrupts, CRC mismatches, black screens, link fallback, visible corruption, or timing-generator wait timeouts.

## Cross-Chunk Notes

Adjacent chunks are required for a complete file report. The previous chunk contains the beginning of `FMT0_FMT_CONTROL` and earlier output block fields. The next chunk continues OTG1 after `OTG1_OTG_CRC2_DATA_B`, including later CRC data, static-screen, global sync, DRR, DTO, DSC start, and pipe-update status fields. The merge lane should preserve that this is chunk 10 of 25 for `dcn_3_5_0_sh_mask.h`.
