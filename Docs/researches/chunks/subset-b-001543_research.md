# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dce/dce_12_0_sh_mask.h lines 14851-17344

## Purpose

This chunk is a generated AMD DCE 12.0 register shift/mask section. It has no executable C logic; it publishes preprocessor constants that describe bit positions and bit masks for display-controller registers. Consumers combine these macros with DCE 12.0 register address macros from `dce_12_0_offset.h` and AMDGPU Display Core register helpers to read, write, lock, poll, or acknowledge hardware state.

The range covers the end of the `LB0` block and then several display pipe blocks for pipe 0 plus the beginning and most of the DCP pipe 1 register field map. It defines 2,130 `#define` entries for 341 register names in this line range. The major address blocks are:

- `LB0`: line-buffer urgency, empty/full, no-outstanding-request, and MVP flip/swap-lock control fields.
- `dce_dc_dcfe0_dispdec`: DCFE0 clock gating, soft reset, memory power control/status, miscellaneous, and flush fields.
- `dce_dc_dc_perfmon3_dispdec`: display performance-monitor counter selection, trigger/mask/window state, high/low counter values, and compare-value interrupt fields.
- `dce_dc_dmif_pg0_dispdec`: DMIF pipe arbitration, watermark mask, urgency, stutter, low-power, repeater, pre-processing check, and DVMM forced-flip status fields.
- `dce_dc_scl0_dispdec`: scaler coefficient RAM, mode, tap counts, filter ratios/init values, viewport/overscan, update, sharpness, ALU, and mode-change detection fields.
- `dce_dc_blnd0_dispdec`: blender mode, stereo/alpha/feedthrough controls, update/underflow interrupt state, V-update locks, and per-client pending-update status.
- `dce_dc_crtc0_dispdec`: timing generator totals, blank/sync windows, trigger events, force/count/status controls, interrupts, test pattern, master update locks, colors, vertical interrupts, CRC, external timing sync, static-screen, 3D, global swap-lock, and DRR/range timing fields.
- `dce_dc_fmt0_dispdec`: formatter clamp, dynamic expansion, pixel encoding/subsampling, dither, CRC, side-by-side stereo, and 4:2:0 hblank fields.
- `dce_dc_dcp1_dispdec`: graphics plane enable/control/surface addresses, update/flip/interrupt/compression fields, color-prescale/CSC/gamut/regamma matrices, denorm/clamp/key/degamma/dither fields, cursor state, LUT state, CRC/DVMM/GSL/rotation/XDMA fields, and regamma LUT region fields.

Although this path lives under a `ceph-client` source mirror, the content is AMDGPU display hardware metadata. It does not implement Ceph filesystem behavior, networking, distributed storage state, or persistence.

## Important APIs, Types, And Constants

There are no functions, structs, typedefs, variables, or call sites in this chunk. Its public surface is the macro naming contract:

- `REGISTER__FIELD__SHIFT` gives the low bit position for a field.
- `REGISTER__FIELD_MASK` gives the field mask in its final register position.

This naming shape is consumed by AMD Display Core macros such as `REG_SET`, `REG_UPDATE`, `REG_GET`, `REG_UPDATE_N`, `set_reg_field_value`, and `get_reg_field_value`. Per-block header macros convert these generated constants into typed register, shift, and mask tables. Representative consumers elsewhere in this tree include `dce120_timing_generator.c`, which includes `dce/dce_12_0_sh_mask.h`, updates `CRTC0_CRTC_CRC_*` fields, and reads `CRTC0_CRTC_CRC*_DATA_*` fields; `dce_mem_input.h` and `dce_mem_input.c`, which map and program `DCP*_GRPH_UPDATE` and `DMIF_PG*_DPG_PIPE_URGENCY_CONTROL`; and `dce_ipp.h`/`dce_ipp.c`, which map cursor and `DCFE*_DCFE_MEM_PWR_CTRL` fields.

Important register families in this chunk include:

- Line-buffer and MVP fields: `LB0_LB_BUFFER_URGENCY_STATUS`, `LB0_LB_BUFFER_STATUS`, `LB0_MVP_AFR_FLIP_*`, `LB0_MVP_FLIP_LINE_NUM_INSERT`, and `LB0_DC_MVP_LB_CONTROL`.
- DCFE0 power/clock/reset fields: `DCFE0_DCFE_CLOCK_CONTROL`, `DCFE0_DCFE_SOFT_RESET`, `DCFE0_DCFE_MEM_PWR_CTRL`, `DCFE0_DCFE_MEM_PWR_CTRL2`, `DCFE0_DCFE_MEM_PWR_STATUS`, and `DCFE0_DCFE_FLUSH`.
- Performance-monitor fields: `DC_PERFMON3_PERFCOUNTER_CNTL`, `DC_PERFMON3_PERFCOUNTER_CNTL2`, `DC_PERFMON3_PERFCOUNTER_STATE`, `DC_PERFMON3_PERFMON_CNTL`, `DC_PERFMON3_PERFMON_CVALUE_INT_MISC`, `DC_PERFMON3_PERFMON_CVALUE_LOW`, `DC_PERFMON3_PERFMON_HI`, and `DC_PERFMON3_PERFMON_LOW`.
- DMIF/watermark fields: `DMIF_PG0_DPG_PIPE_ARBITRATION_CONTROL*`, `DMIF_PG0_DPG_WATERMARK_MASK_CONTROL`, `DMIF_PG0_DPG_PIPE_URGENCY_CONTROL`, `DMIF_PG0_DPG_PIPE_URGENT_LEVEL_CONTROL`, `DMIF_PG0_DPG_PIPE_STUTTER_CONTROL*`, `DMIF_PG0_DPG_PIPE_LOW_POWER_CONTROL`, and `DMIF_PG0_DPG_DVMM_STATUS`.
- Scaler fields: `SCL0_SCL_COEF_RAM_SELECT`, `SCL0_SCL_COEF_RAM_TAP_DATA`, `SCL0_SCL_MODE`, `SCL0_SCL_TAP_CONTROL`, horizontal/vertical filter ratio/init registers, `SCL0_SCL_UPDATE`, `SCL0_SCL_COEF_RAM_CONFLICT_STATUS`, viewport/overscan registers, and mode-change detectors.
- Blender fields: `BLND0_BLND_CONTROL`, `BLND0_BLND_SM_CONTROL2`, `BLND0_BLND_CONTROL2`, `BLND0_BLND_UPDATE`, `BLND0_BLND_UNDERFLOW_INTERRUPT`, `BLND0_BLND_V_UPDATE_LOCK`, and `BLND0_BLND_REG_UPDATE_STATUS`.
- CRTC0 fields: the largest group in this chunk, spanning mode timing, trigger A/B, counters, stereo, snapshots, update locks, test patterns, vertical interrupts, CRC, external sync, static-screen detection, 3D structure, GSL, and DRR/range timing.
- FMT0 fields: clamp ranges, formatter dynamic expansion/control, bit-depth/dither control, random seeds, CRC signatures/masks, stereo control, and 4:2:0 hblank early-start.
- DCP1 fields: graphics surface setup, flip/update handshakes, compression metadata, prescale/input CSC/output CSC/common matrices, denorm/clamp/keying, degamma/gamut remap, spatial dither/random seeds, cursor programming, LUT and regamma programming, DCP CRC, DVMM PTE controls, GSL control, rotation, and XDMA recovery.

## Control Flow

This header section has no runtime branches or sequencing. The runtime flow is imposed by AMDGPU/DC consumers that use the shift/mask constants.

A typical write path is:

1. Driver code computes desired display state from DRM atomic state, mode timing, plane state, cursor state, color-management state, watermark calculations, CRC settings, or power-management policy.
2. The code selects a register address from the matching DCE 12.0 offset header and one or more field names from this shift/mask header.
3. Register helper macros clear the field with `*_MASK`, shift the new value by `*_SHIFT`, merge it with the old register value if needed, and write through `dm_write_reg`, `dm_write_reg_soc15`, `REG_SET`, or `REG_UPDATE`.
4. Hardware latches the resulting state immediately, at a vertical-update boundary, behind a block-specific update lock, after a double-buffer update, or after an interrupt/status acknowledge depending on the register.

A typical read/poll path is:

1. Driver code reads a register with `dm_read_reg`, `dm_read_reg_soc15`, `REG_GET`, or a related helper.
2. The helper masks with `REGISTER__FIELD_MASK` and right-shifts by `REGISTER__FIELD__SHIFT`.
3. The extracted value is interpreted as pending/taken status, CRC data, current counter position, memory power state, line-buffer state, underflow, interrupt status, outstanding request status, or performance-counter value.

Important sequencing implied by this chunk but implemented elsewhere includes:

- Update-lock sequencing for DCP, SCL, BLND, CRTC master update, and graphics surface updates.
- CRTC timing programming before enabling scanout or master enable.
- Scaler coefficient RAM selection and tap-data writes before scaler update completion.
- Cursor address/size/hotspot/color programming before enabling the cursor.
- DCFE memory-power disable/enable around LUT, regamma, cursor, line-buffer, scaler, or blender memory use.
- Interrupt and status acknowledgement for underflow, vertical interrupts, CRTC set-v-total events, static-screen events, CRC, external timing sync, and line-buffer empty/full events.

## State And Persistence Behavior

The file itself stores no state. It defines constants for state held in DCE hardware registers and for software's view of those registers.

Hardware state represented here includes:

- Line-buffer fullness/emptiness, urgency level, no-outstanding-request status, and MVP flip/swap-lock status.
- DCFE clock gating, soft reset, memory power force/disable/mode selection, memory power status, and flush controls.
- Performance-monitor selection, enable, windowing, event state, compare thresholds, and high/low sampled counter values.
- DMIF request arbitration, urgent/low/high watermarks, watermark masks, stutter/self-refresh controls, low-power controls, and DVMM mapped/unmapped forced-flip status.
- Scaler coefficient RAM contents and conflict status, viewport/overscan rectangles, filter ratios, filter initial phases, tap counts, sharpness controls, ALU mode-change detection, and update-pending state.
- Blender composition mode, stereo mode, alpha mode, feedthrough, global gain/alpha, underflow interrupt state, V-update locks, and pending update status for DCP/SCL/BLND clients.
- CRTC timing, blanking, sync polarity/windows, vertical-total min/max/DRR controls, trigger state, counter/status snapshots, stereo/3D, static-screen detection, test patterns, CRC windows/data, external sync windows, vertical interrupts, GSL synchronization, and master update locks.
- Formatter clamp/dither/CRC/pixel-encoding/subsampling state.
- DCP1 graphics plane addresses, pitch, surface extents, pixel format/control, flip mode, DFQ state, compression base/pitch, color matrices, LUT/regamma tables, gamut remap, spatial dither, cursor state, PTE/DVMM state, CRC, GSL, rotation, and XDMA recovery state.

Persistence is register-specific. Some fields are durable until the next modeset, plane update, cursor update, color update, power transition, or GPU reset. Others are transient status bits, pending/taken bits, clear/ack bits, latched counters, or hardware-owned readback fields. The header does not encode reset defaults, access permissions, write-one-to-clear behavior, polling deadlines, or safe ordering; those rules live in hardware documentation and in the display driver code that uses these masks.

## Dependencies And Integration Points

This chunk depends on the generated DCE 12.0 register corpus. It is meaningful only with the matching register address/header set, especially:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dce/dce_12_0_offset.h`, which defines the `mm*` register addresses and base indices for the fields in this chunk.
- Nearby generated enum and shift/mask headers that define value encodings and adjacent field families.
- AMD Display Core helper macros that consume `*_SHIFT` and `*_MASK` names to create per-IP register tables and bitfield updates.

Observed integration points in the source tree include:

- `display/dc/dce120/dce120_timing_generator.c`: includes this header and programs CRTC timing, CRC, status, and max-total fields through `CRTC_REG_UPDATE_*`, `dm_read_reg_soc15`, and `get_reg_field_value`.
- `display/dc/dce/dce_mem_input.h` and `display/dc/dce/dce_mem_input.c`: map `GRPH_UPDATE`, `GRPH_UPDATE_LOCK`, `GRPH_SURFACE_UPDATE_PENDING`, and `DPG_PIPE_URGENCY_CONTROL` fields for plane update locking and watermark/urgency programming.
- `display/dc/dce/dce_ipp.h` and `display/dc/dce/dce_ipp.c`: map cursor fields and `DCFE*_DCFE_MEM_PWR_CTRL` fields used when enabling/disabling LUT-related memory power.
- DCE compressor and timing-generator offset calculations that use `mmDCP1_GRPH_CONTROL - mmDCP0_GRPH_CONTROL` to address repeated pipe instances.
- OPP/DPP/scaler code patterns that use equivalent scaler coefficient, formatter, dither, and regamma field concepts on later DCN ASICs; these are not the same registers, but they show the same generated shift/mask consumption model.

The integration boundary is low level. Higher layers such as DRM atomic modeset, CRC debugfs, cursor IOCTL handling, color management, power management, and HPD/modeset policy do not include this header for business logic; they call hardware abstraction methods that eventually program the registers described by these constants.

## Risks And Edge Cases

The main risk is silent hardware misprogramming. These macros are plain preprocessor constants, so an incorrect mask or shift can compile cleanly while causing the driver to write the wrong bits.

High-risk areas in this chunk are:

- Timing generator fields. Bad CRTC totals, blanking windows, sync windows, polarity, master enable, vertical-total min/max, or DRR fields can produce a blank display, unstable refresh, underrun/underflow symptoms, or a mode that a sink cannot lock to.
- Update-lock and double-buffer fields. Incorrect use of `*_UPDATE_LOCK`, `*_UPDATE_PENDING`, and `*_UPDATE_TAKEN` can cause tearing, stale plane state, missed flips, or deadlocked waits for pending updates to clear.
- Interrupt/status/ack fields. Many fields pair occurred/status bits with clear/ack/mask/type bits. Writing the wrong mask can lose vertical interrupt, underflow, static-screen, external sync, CRC, trigger, or line-buffer events, or generate interrupt storms.
- DMIF watermark and urgency fields. Bad low/high watermark, urgent level, stutter, or arbitration values can cause display underflow, poor memory power behavior, excessive latency, or failure to enter/exit stutter states correctly.
- DCFE memory power controls. Forcing or disabling LUT, regamma, scaler coefficient, cursor, line-buffer, or blender memories while the relevant block is active can corrupt visible output or hang a programming sequence that expects memory to be powered.
- Scaler coefficient RAM fields. Wrong tap-pair, phase, filter type, coefficient enable, ratio, init, or update bits can produce bad scaling quality, color/chroma alignment issues, or host conflicts while hardware is reading coefficients.
- Blender alpha/stereo/feedthrough fields. Wrong blend mode, global alpha/gain, stereo polarity, overlap-only, or multiplied-alpha settings can hide planes, compose them with incorrect opacity, or break stereo presentation.
- Formatter and color fields. Wrong dither, clamp, pixel-encoding, subsampling, CSC, gamut, degamma, regamma, LUT, denorm, or clamp masks can cause visible color errors, CRC mismatches, or HDMI/DP format mismatches.
- DCP1 address and compression fields. Wrong surface address, high address, pitch, in-use/readback, compression address/pitch, or pipe request limit fields can cause corrupted scanout, memory faults, wrong framebuffer fetches, or compression metadata misuse.
- Cursor fields. Incorrect cursor surface address, size, hotspot, mode, position, or color fields can cause missing cursors, cursor corruption, or out-of-bounds fetch behavior.
- Repeated-instance naming. This chunk mixes pipe 0 blocks (`SCL0`, `BLND0`, `CRTC0`, `FMT0`, `DCFE0`, `DMIF_PG0`, `LB0`) with `DCP1`. Consumers that rely on instance offsets must combine the correct address base with the matching shift/mask table.

Generated-header maintenance is also risky. Manual edits, line wrapping changes, or generator regressions can break downstream macros that assume exact `REGISTER__FIELD__SHIFT` and `REGISTER__FIELD_MASK` spellings.

## Test Signals

Useful validation signals are build-time, generated-data, and hardware-behavior oriented:

- Kernel build coverage for DCE 12.0 display paths that include `dce_12_0_sh_mask.h`; missing or renamed macros should fail compilation in timing generator, memory input, IPP/cursor, color/LUT, and register-table code.
- Generated-header diffing against AMD's authoritative DCE 12.0 register database, checking every register/field shift and mask in this line range.
- Register-table self-consistency checks verifying that each `*_MASK` aligns with its `*_SHIFT`, has the expected field width, and does not overlap unrelated fields within the same register.
- Modeset tests across common and edge timing modes, including interlace/stereo/3D where supported, DRR or vertical-total variation, external timing sync, and master update lock paths.
- Page-flip and plane-update tests that watch `GRPH_UPDATE`, CRTC/blender/scaler update-pending bits, and visible tear-free transitions.
- Display CRC tests through `amdgpu_dm_crc`, including enabling/disabling CRTC CRC, programming CRC windows, reading CRC0/CRC1 data, and checking stable CRC output with and without dither.
- Watermark/underflow tests under memory pressure and low-power transitions, watching DMIF urgency/stutter behavior and `BLND_UNDERFLOW_INTERRUPT`.
- Scaler tests covering coefficient programming, horizontal/vertical scaling ratios, viewport/overscan, nearest/2-tap modes, and coefficient RAM conflict status.
- Color-management tests for LUT, regamma, degamma, CSC, gamut remap, clamp, denorm, spatial dither, and formatter bit-depth/pixel-encoding fields.
- Cursor tests for enable/disable, modes, address high/low, size, hotspot, color, position, 2x magnify, and update locking.
- Suspend/resume, runtime power, and GPU reset tests verifying that DCFE memory power and block reset state is restored before display programming resumes.

Regression symptoms from incorrect constants include blank or unstable displays, wrong timing, corrupted scanout, underflows, stuck pending updates, missing vertical interrupts, bad CRC reads, bad scaling, wrong colors, cursor corruption, failed flips, inability to enter stutter/low power, and failure to recover display state after reset or resume.

## Cross-Chunk Notes

This is a middle chunk of the large generated `dce_12_0_sh_mask.h` file. Earlier chunks define preceding DCE 12.0 register fields, and later chunks continue after `DCP1_GRPH_XDMA_RECOVERY_SURFACE_ADDRESS`. The final per-file merge should present the whole file as one generated hardware bitfield map for DCE 12.0, paired with offset and enum headers, rather than as independent executable modules.

The chunk begins mid-context with the mask for `LB0_LB_BUFFER_URGENCY_CTRL__LB_BUFFER_URGENCY_MARK_OFF_MASK`, so the matching shift and other fields for that register are in the previous chunk. It ends at the start of `DCP1_GRPH_XDMA_RECOVERY_SURFACE_ADDRESS`, so the mask and any following DCP1 fields are in the next chunk. Merge reconciliation should preserve those boundary relationships.
