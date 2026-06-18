# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_4_1_0_sh_mask.h lines 25158-27730

## Purpose

This chunk is generated AMD DCN 4.1.0 register-field metadata. It contains no executable C logic; it publishes `#define` constants that describe bit shifts and masks for fields in DCN display MMIO registers. Driver code combines these constants with the matching offset header, register-list macros, and AMD display register helpers to encode, update, and decode individual hardware fields without disturbing neighboring bits.

The exact range contains 2,114 `#define` lines: 1,057 `__SHIFT` constants and 1,057 `_MASK` constants across 361 register names. The range starts inside the existing ABM2 adaptive-backlight block, covers a complete ABM3 block, covers output-pixel-processor and OPTC/ODM register families for display pipes 0-3, covers the full OTG0 timing-generator mask slice present in this part of the file, and ends in the middle of OTG1 trigger-control metadata.

Although this repository path is under a local `ceph-client` mirror, this header is AMDGPU display hardware metadata. It does not implement Ceph or distributed-filesystem behavior.

## Important APIs, Types, And Macros

There are no functions, structs, enums, variables, allocation paths, or locks in this chunk. The exported interface is the generated macro namespace:

- `<REGISTER>__<FIELD>__SHIFT`: bit position for packing or extracting a field.
- `<REGISTER>__<FIELD>_MASK`: bit mask for isolating, preserving, or clearing that field during MMIO operations.

Major register groups in this range:

- `ABM2_*` tail fields: luma statistics, min/max pixel thresholds, sample-rate counters, 64-bin histogram shift flags/indexes, histogram result index/data, and backlight master lock.
- `ABM3_*`: a full adaptive-backlight/PWM instance. It covers ambient/user/target/current/final/minimum backlight levels, ABM PWM control, backlight-update sampling, group-2 double-buffer lock/update controls, ABM enable/bypass, IPS CSC coefficient selectors, ACE PWL indexed slope/offset and threshold data, missed-frame status/clear bits, HGLS read progress, luma-statistics counters, histogram controls/results, and master lock.
- `DPG0`-`DPG3`: display pattern generator enable, ramp control, dimensions, RGB/YCbCr color words, output offset/segment width, and double-buffer pending status.
- `FMT0`-`FMT3`: output formatter clamp bounds, dynamic expansion, pixel encoding/subsampling, truncation, spatial/temporal dithering, random seeds, clamp format, side-by-side stereo width, 4:2:0 memory low-power controls, and 4:2:2 edge-pixel control.
- `OPPBUF0`-`OPPBUF3`, `OPP_PIPE0`-`OPP_PIPE3`, and `OPP_PIPE_CRC0`-`OPP_PIPE_CRC3`: output-buffer segmentation/3D parameters, OPP pipe clock/bypass controls, and OPP pipe CRC enable/mode/source/result fields.
- `DSCRM0`-`DSCRM3`: DSC-forward enable, source selection, double-buffer pending, and enable-status fields.
- `OPP_TOP_CLK_CONTROL` and `OPP_ABM_CONTROL`: OPP clock gating/test selection, ABM clock-on status for four ABM instances, and backlight PWM source selection.
- `ODM0`-`ODM3`: OPTC input global controls, underflow status/clear/interrupt bits, segment source routing, output/input segment counts, DSC format/bytes/slice width, input clock control, memory selection/status, and spare registers.
- `OTG0_*`: timing-generator horizontal/vertical totals, blanking/sync geometry, DRR/vtotal controls, trigger A/B controls, force-count controls, stereo/interlace/snapshot/status registers, update locks, double-buffer controls, vertical interrupts, CRC windows/data/readbacks, static-screen control, 3D structure control, global sync/update-lock/GSL/vupdate keepout controls, manual flow controls, DRR timing interrupts/ranges, DTO phase/modulo, request control, pipe-update status, pstate keepout, and spare registers.
- `OTG1_*` beginning: horizontal/vertical timing totals, blanking/sync geometry, vtotal/DRR control, vtotal/vsync status, and the start of trigger A/B control fields. The range ends before the full OTG1 block is complete.

## Control Flow

This header has no runtime control flow. Runtime sequencing is supplied by AMDGPU display code:

1. DCN401-specific files include `dcn_4_1_0_offset.h` and this shift/mask header.
2. Register-list macros token-paste symbolic register and field names into ASIC-specific register, shift, and mask tables.
3. Resource construction stores those tables in block structures such as ABM and timing-generator objects.
4. Runtime paths call helpers such as `REG_READ`, `REG_WRITE`, `REG_GET`, `REG_SET`, `REG_UPDATE`, and polling variants. Those helpers use the numeric offset, shift, and mask values to perform field-level MMIO operations.

Direct integration examples include `dcn401_resource.c`, where `ABM_MASK_SH_LIST_DCN401(__SHIFT)` and `ABM_MASK_SH_LIST_DCN401(_MASK)` initialize ABM field tables, and `dcn401_optc.h`, where `OPTC_COMMON_MASK_SH_LIST_DCN401` consumes many `OTG0_*` and `ODM0_*` fields from this range for timing-generator programming. `dmub_dcn401.c` also includes this header to build DMUB-visible DCN401 register/field tables.

The macros themselves do not encode sequencing. Consumers must still handle clock enable/status, soft reset, update locks, double-buffer pending bits, frame-start update timing, trigger clear semantics, CRC one-shot state, interrupt clear bits, power-gated memory controls, ABM master locks, and display pipe ownership correctly.

## State And Persistence Behavior

This chunk stores no software state and persists nothing to disk. It describes MMIO-backed hardware state for DCN 4.1.0 display blocks:

- ABM/PWM state for adaptive backlight levels, duty-cycle bounds, ambient-light input, ACE curve tables, luma/histogram statistics, sample rates, lock/update-pending state, and missed-frame indicators.
- OPP state for pattern generation, formatter clamp/dither/subsampling controls, output buffer segmentation, OPP pipe clock/bypass controls, pipe CRC capture, DSC forwarding, and ABM clock/source routing.
- ODM/OPTC input state for segment routing, DSC formatting, input clocks, underflow diagnostics, memory selection, and double-buffer pending status.
- OTG state for display timing, vertical/horizontal counters, dynamic refresh/vtotal selection, triggers, stereo/interlace operation, update locking, interrupts, CRC windows/results, GSL/global sync, DTO programming, pstate keepout, and pipe update status.

Persistence is hardware-defined. Configuration fields usually last until modeset, pipe reconfiguration, display-block power gating, suspend/resume, GPU reset, or driver reinitialization. Status, pending, missed-frame, clear, interrupt, CRC, snapshot, counter, and readback fields may be read-only, sticky, self-clearing, write-one-to-clear, or valid only while relevant clocks and power domains are active. The generated header does not express those access semantics.

## Dependencies And Integration Points

This chunk must stay synchronized with:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_4_1_0_offset.h`, which supplies matching MMIO register offsets and base-index selectors.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/resource/dcn401/dcn401_resource.c`, which initializes DCN401 ABM shift/mask tables from `ABM_MASK_SH_LIST_DCN401`.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dce/dce_abm.h`, whose DCN401 ABM field-list macro references ABM fields present in this range, including newer indexed ACE and extended histogram fields.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/optc/dcn401/dcn401_optc.h`, which references OTG0 and ODM0 fields in this range for timing, DRR, CRC, update-lock, GSL, ODM combine, pstate, and pipe-update programming.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dmub/src/dmub_dcn401.c`, which includes this generated header for DCN401 DMUB register/field table construction.
- Generic AMD display register-helper macros that combine offsets, shifts, and masks for MMIO read-modify-write operations.

Behaviorally, these fields integrate with panel backlight policy, display pipe enable/disable, modeset timing, variable refresh/DRR, ODM combine/split routing, DSC forwarding, output formatter color/bit-depth handling, CRC/debug capture, static-screen detection, interrupts, global sync, and power-state keepout logic.

## Risks And Edge Cases

- These are untyped preprocessor constants. A wrong shift or mask can compile successfully while writing the wrong MMIO bits, corrupting adjacent fields, or breaking only one pipe or display mode.
- The file is generated metadata. Manual edits risk divergence from AMD's authoritative register database, the offset header, firmware expectations, and ASIC documentation.
- The chunk begins inside ABM2 and ends inside OTG1. Adjacent chunks are required for complete per-register claims about ABM2 and OTG1.
- Repeated instances are copy-sensitive. `DPG`, `FMT`, `OPPBUF`, `OPP_PIPE`, `OPP_PIPE_CRC`, `DSCRM`, and `ODM` layouts repeat for instances 0-3; an instance-specific generator error may affect only one display pipe.
- ABM fields are sequencing-sensitive. Incorrect lock, pending, readback, missed-frame-clear, sample-rate, or ACE index masks can cause stale backlight curves, jumps in brightness, invalid luma statistics, or histogram readback races.
- Timing and DRR fields are high impact. Bad `OTG*_V_TOTAL*`, trigger, update-lock, or DRR masks can cause modeset failure, flicker, frame pacing errors, missed vblank events, or stuck update-pending state.
- Clock, reset, power, memory, and pstate fields may be ignored or unsafe when a block is gated, reset, firmware-owned, or unsupported on a given stepping.
- Clear/status fields share registers with enable/type/mask bits. Using the wrong mask can accidentally clear diagnostics or leave interrupts asserted.
- CRC and formatter fields are easy to validate but visually sensitive. Bad masks can produce color clipping, dithering artifacts, invalid 4:2:0/4:2:2 behavior, or misleading CRC signatures.

## Test Signals

Useful validation should combine generated-header consistency checks with DCN401 hardware behavior:

- Build AMDGPU display support with DCN401 enabled. Missing or renamed fields should fail in DMUB, ABM, resource, or OPTC register-table construction.
- Mechanically verify that every `__SHIFT` in this exact range has a matching `_MASK` in the range. This chunk has balanced counts, while full semantic completeness still depends on adjacent chunks for ABM2 and OTG1.
- Diff this slice against AMD's authoritative DCN 4.1.0 register database and the matching `dcn_4_1_0_offset.h`.
- Exercise ABM/PWM behavior: brightness transitions, ambient/user/target levels, duty-cycle limits, ACE indexed slope/threshold updates, histogram/luma readback, frame-start updates, locks, missed-frame clears, and suspend/resume.
- Exercise OPP/FMT/DPG/OPPBUF paths across normal modesets, color-depth changes, RGB/YUV formats, 4:2:0/4:2:2 modes, dithering/truncation, pattern generation, pipe bypass, and OPP pipe CRC capture.
- Exercise ODM/DSC-forward paths for single-pipe and combined-pipe configurations, including segment source selection, DSC byte/slice-width programming, input clock state, underflow clear/status, and double-buffer pending behavior.
- Exercise OTG timing and DRR paths: mode programming, vtotal min/max/mid changes, trigger A/B programming, vertical interrupts, update locks, GSL/global sync, vupdate keepout, CRC windows/readback, pstate keepout, pipe-update status, blank/unblank, and suspend/resume.
- Watch kernel logs, display diagnostics, CRC output, vblank/interrupt counters, underflow status, update-pending bits, missed-frame bits, brightness behavior, flicker, color corruption, and resume-only failures.

## Cross-Chunk Notes

The previous chunk owns the beginning of the ABM2 block, including earlier ABM2 control and read-progress fields. This chunk starts at `ABM2_DC_ABM1_LS_FILTERED_MIN_MAX_LUMA` and then moves into ABM3. The next chunk owns the rest of `OTG1`, because this range stops after the first part of `OTG1_OTG_TRIGB_CNTL`. The final per-file research document should merge adjacent chunks before making whole-file claims about all ABM instances, all OTG instances, or the complete DCN 4.1.0 shift/mask namespace.
