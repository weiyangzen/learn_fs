# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_0_0_sh_mask.h lines 32370-34834

## Scope And Purpose

This chunk is a generated AMD DCN 3.0.0 register shift/mask table for display timing-generator hardware. It contains C preprocessor constants that describe bit positions (`__SHIFT`) and bit masks (`_MASK`) for Output Timing Generator (`OTG`) registers. The covered range starts in the tail of `OTG2`, contains the full `dce_dc_optc_otg3_dispdec` and `dce_dc_optc_otg4_dispdec` address blocks, and ends inside the `dce_dc_optc_otg5_dispdec` block after `OTG5_OTG_DRR_V_TOTAL_REACH_RANGE`.

There are no executable functions, structs, or runtime branches in this chunk. Its purpose is to provide compile-time field metadata consumed by AMD display driver register-access macros. The companion offset header supplies register addresses such as `mmOTG3_OTG_H_TOTAL`; this header supplies the matching field layout such as `OTG3_OTG_H_TOTAL__OTG_H_TOTAL__SHIFT` and `OTG3_OTG_H_TOTAL__OTG_H_TOTAL_MASK`.

The register groups in this slice program and observe display scanout timing, vertical/horizontal blank and sync intervals, dynamic refresh-rate timing, global sync lock windows, vertical interrupts, stereo/interlace state, CRC capture windows and result fields, blanking colors, update locks, clock gating/reset state, DSC start position, and pending pipe-update status.

## Register Blocks Covered

The first lines finish `OTG2` with fields for DRR control, M/N constant DTO programming, request control for horizontal duplicate handling, DSC start position, pipe update pending status, and a spare register. This is only a partial tail of the `OTG2` block; the preceding chunk owns the earlier `OTG2` timing fields.

`OTG3` is fully represented under `// addressBlock: dce_dc_optc_otg3_dispdec`. It has 716 `#define` entries in the requested line slice and covers the full per-OTG timing generator layout from `OTG3_OTG_H_TOTAL` through `OTG3_OTG_SPARE_REGISTER`.

`OTG4` mirrors the `OTG3` layout under `// addressBlock: dce_dc_optc_otg4_dispdec`. It also contributes 716 `#define` entries. The field names, bit widths, and masks are structurally the same with the instance prefix changed from `OTG3_` to `OTG4_`.

`OTG5` starts under `// addressBlock: dce_dc_optc_otg5_dispdec` and is covered through `OTG5_OTG_DRR_V_TOTAL_REACH_RANGE`. The chunk includes the same major groups as `OTG3` and `OTG4` through DRR timing interrupt status and the DRR v-total reach range fields, but the later `OTG5` DRR change/window/control, DTO, request-control, DSC, pipe-status, and spare-register fields continue after line 34834.

## Important APIs, Types, And Macros

The important exported surface is the macro naming contract:

- `<instance>_<register>__<field>__SHIFT` gives the bit offset used when packing or extracting a field.
- `<instance>_<register>__<field>_MASK` gives the masked field bits in the 32-bit hardware register value.
- Instance prefixes in this chunk are `OTG2`, `OTG3`, `OTG4`, and `OTG5`.
- Register comments such as `//OTG3_OTG_GLOBAL_SYNC_STATUS` delimit groups but are not consumed by C code.
- Address-block comments such as `// addressBlock: dce_dc_optc_otg4_dispdec` identify the replicated display-controller hardware block.

The header is consumed by generated-style AMD display macros including `SF(...)`, `SRI(...)`, `REG_FIELD`, `REG_GET`, `REG_SET`, and `REG_UPDATE` through higher-level register lists. For example, `display/dc/optc/dcn30/dcn30_optc.h` declares `OPTC_COMMON_REG_LIST_DCN3_0(inst)` with `SRI(OTG_H_TOTAL, OTG, inst)`, `SRI(OTG_GLOBAL_SYNC_STATUS, OTG, inst)`, `SRI(OTG_DRR_TRIGGER_WINDOW, OTG, inst)`, and `SRI(OTG_PIPE_UPDATE_STATUS, OTG, inst)`. Its mask list uses `SF(OTG0_OTG_H_TOTAL, OTG_H_TOTAL, mask_sh)` style entries, relying on the same field-layout definitions replicated across OTG instances.

The IRQ service for DCN 3.0 and DCN 3.0.2 includes this header and maps vupdate/vblank interrupts through fields in `OTG_GLOBAL_SYNC_STATUS`, including `VUPDATE_NO_LOCK_INT_EN`, `VUPDATE_NO_LOCK_EVENT_CLEAR`, `VSTARTUP_INT_EN`, and `VSTARTUP_EVENT_CLEAR`. Later OPTC diagnostic code reads registers represented here into state snapshots, including `OTG_DRR_TIMING_INT_STATUS`, `OTG_GLOBAL_SYNC_STATUS`, `OTG_GSL_CONTROL`, `OTG_H_TOTAL`, CRC fields, and related timing registers.

## Functional Field Groups

Horizontal and vertical timing fields define scanout geometry. `OTG_H_TOTAL`, `OTG_H_BLANK_START_END`, `OTG_H_SYNC_A`, `OTG_H_SYNC_A_CNTL`, and `OTG_H_TIMING_CNTL` describe horizontal total pixels, blanking window, sync start/end, sync polarity, composite sync enable/cutoff, and timing divider behavior. `OTG_V_TOTAL`, `OTG_V_TOTAL_MIN`, `OTG_V_TOTAL_MAX`, `OTG_V_TOTAL_MID`, `OTG_V_BLANK_START_END`, `OTG_V_SYNC_A`, and `OTG_V_SYNC_A_CNTL` define vertical totals, variable-refresh bounds, blanking, sync timing, polarity, and sync mode.

Dynamic refresh-rate fields are centered on `OTG_V_TOTAL_CONTROL`, `OTG_DRR_TIMING_INT_STATUS`, `OTG_DRR_V_TOTAL_REACH_RANGE`, `OTG_DRR_V_TOTAL_CHANGE`, `OTG_DRR_TRIGGER_WINDOW`, and `OTG_DRR_CONTROL`. They expose min/max/mid v-total selection, masked min-vtotal updates, frame counts, DRR timing-update interrupts, v-total-reach interrupts, clear/mask/type bits, v-total reach ranges, v-total change limits, trigger windows, and the last v-total used by DRR. These fields are timing-sensitive because the driver uses them to vary refresh while preserving scanout stability.

Trigger and forced-count fields include `OTG_TRIGA_CNTL`, `OTG_TRIGB_CNTL`, manual trigger registers, `OTG_FORCE_COUNT_NOW_CNTL`, `OTG_TRIG_MANUAL_CONTROL`, and `OTG_MANUAL_FLOW_CONTROL`. They select trigger sources and source pipes, polarity, rising/falling edge detection, frequency, delay, status, clear bits, and manual trigger paths. `OTG_FLOW_CONTROL` adds source selection, polarity, granularity, and input status for flow-control signaling.

Mastering, update, and global-sync fields include `OTG_CONTROL`, `OTG_MASTER_EN`, `OTG_UPDATE_LOCK`, `OTG_DOUBLE_BUFFER_CONTROL`, `OTG_MASTER_UPDATE_MODE`, `OTG_MASTER_UPDATE_LOCK`, `OTG_GLOBAL_SYNC_STATUS`, `OTG_GSL_CONTROL`, `OTG_GSL_WINDOW_X/Y`, `OTG_VUPDATE_KEEPOUT`, and `OTG_GLOBAL_CONTROL0` through `OTG_GLOBAL_CONTROL4`. They control OTG enable state, disable/start points, update locks and pending state, global swap lock participation, vstartup/vupdate/vready events, vupdate keepout regions, double-buffer regions, digital update positions, and master-update-lock selection.

Status, snapshot, stereo, and interlace fields include `OTG_STATUS`, `OTG_STATUS_POSITION`, `OTG_NOM_VERT_POSITION`, `OTG_STATUS_FRAME_COUNT`, `OTG_STATUS_VF_COUNT`, `OTG_STATUS_HV_COUNT`, `OTG_COUNT_CONTROL`, `OTG_COUNT_RESET`, `OTG_VERT_SYNC_CONTROL`, `OTG_STEREO_STATUS`, `OTG_STEREO_CONTROL`, `OTG_STEREO_FORCE_NEXT_EYE`, `OTG_3D_STRUCTURE_CONTROL`, `OTG_INTERLACE_CONTROL`, `OTG_INTERLACE_STATUS`, and the snapshot registers. These fields expose current vblank/active/sync state, horizontal and vertical counters, frame counters, stereo eye state, forced next field/eye controls, and snapshot triggers or captured positions.

Interrupt and CRC fields include vertical interrupt position/control registers for interrupt slots 0 through 2, `OTG_INTERRUPT_CONTROL`, `OTG_CRC_CNTL`, `OTG_CRC_CNTL2`, CRC window controls, CRC data readbacks, and CRC signature masks. These support vline/vblank-style interrupt routing and validation/debug capture of displayed pixel streams.

Output data, clock, and miscellaneous fields include blank data color and extended-color fields, pixel data readback registers, `OTG_CLOCK_CONTROL`, `OTG_VSTARTUP_PARAM`, `OTG_VUPDATE_PARAM`, `OTG_VREADY_PARAM`, DTO phase/modulo constants, request-control flags, DSC start position, pipe update status, and spare registers.

## Control Flow And State Behavior

This header has no direct control flow. The effective control flow is created at compile time by macro expansion in DCN display modules. Register-list macros select an OTG instance, bind the corresponding offset from `dcn_3_0_0_offset.h`, then bind the field masks and shifts from this file. Runtime code then performs memory-mapped register reads and writes through AMD display register helpers.

The hardware state described here is persistent in display controller registers until the driver, firmware, reset logic, power management, or hardware event logic changes it. Some fields are configuration state, such as timing totals, blanking windows, update-lock settings, CRC windows, DTO constants, and blank colors. Some fields are live status, such as current blank/sync state, counters, frame counts, busy/clock-on bits, input status bits, pending-update bits, and current stereo/interlace state. Some interrupt/event fields use write-to-clear or acknowledge-style semantics, reflected by field names such as `*_CLEAR`, `*_ACK`, and `*_EVENT_CLEAR`.

Several registers are double-buffered or synchronized to scanout phases. Fields involving update locks, global update lock, vupdate keepout, digital update position, GSL windows, and DRR trigger windows must be programmed with attention to vstartup/vupdate/vready timing. Incorrect sequencing can cause updates to miss the intended frame, block indefinitely behind update locks, or land during active scanout.

## Dependencies And Integration Points

This file depends on hardware register contracts for AMD DCN 3.0.0. It must stay aligned with `dcn_3_0_0_offset.h`, which provides the register addresses and base indices for the same `OTG3`, `OTG4`, and `OTG5` names. It also must stay compatible with generated register-list and mask-list macros in the display core, especially the DCN 3.0 OPTC path.

Direct include sites for this header include DCN 3.0 and DCN 3.0.2 display components such as `display/dc/resource/dcn30/dcn30_resource.c`, `display/dc/irq/dcn30/irq_service_dcn30.c`, `display/dc/irq/dcn302/irq_service_dcn302.c`, `display/dmub/src/dmub_dcn30.c`, `display/dmub/src/dmub_dcn302.c`, `display/dc/clk_mgr/dcn30/dcn30_clk_mgr.c`, and DCN 3.0 GPIO factory/translation code.

The most important integration point for this chunk is the OPTC/timing-generator stack. `display/dc/optc/dcn30/dcn30_optc.h` lists many of the registers covered here in `OPTC_COMMON_REG_LIST_DCN3_BASE` and `OPTC_COMMON_REG_LIST_DCN3_0`, including timing, vtotal, trigger, static-screen, status, blank color, clock, vertical interrupt, GSL, CRC, DRR, DSC, and pipe-update-status registers. IRQ setup uses `OTG_GLOBAL_SYNC_STATUS` fields for vblank and vupdate sources. Diagnostic register-state capture uses these same register names to snapshot OTG timing and CRC/debug state.

## Risks And Edge Cases

The primary risk is field drift between this mask header, the companion offset header, and the real hardware specification. A wrong shift or mask can silently write the wrong bitfield in a memory-mapped register, which may produce display timing failures, missed interrupts, stuck update locks, incorrect CRC/readback data, or unstable variable-refresh behavior.

Instance replication is another risk. `OTG3`, `OTG4`, and `OTG5` are largely identical, so generation errors that affect only one prefix are easy to miss in review. Conversely, assuming all instances are complete in this chunk would be wrong: `OTG5` continues after the requested range, while `OTG2` only appears as a tail from the previous block.

Interrupt/status fields require particular care. Fields named `*_EVENT_OCCURRED`, `*_INT_STATUS`, `*_CLEAR`, `*_ACK`, `*_MSK`, and `*_INT_TYPE` are adjacent in shared registers. If a clear mask is confused with a status mask, the driver can either fail to acknowledge interrupts or clear state unexpectedly.

Timing-window and update-lock fields have frame-phase dependencies. Values for vstartup/vupdate/vready, vupdate keepout, GSL windows, vertical interrupt positions, DRR trigger windows, and double-buffer regions must be valid relative to programmed totals and blanking ranges. Bad values can create race-like failures that only reproduce on particular modes, refresh ranges, or multi-display topologies.

Many fields are limited-width counters or positions, commonly 15-bit horizontal/vertical values and packed 16-bit low/high halves. Callers must clamp or validate mode-derived values before packing them through these masks. Overwide values would be truncated by the mask and can shift timing positions to unintended scanout coordinates.

## Test Signals

Build-time signals are straightforward: any stale or missing macro used by DCN 3.0 register lists should fail compilation in AMD display modules that include this header. Warnings or errors around `SF`, `SRI`, `REG_FIELD`, or missing `OTGx_*__*` identifiers are high-signal indicators of a register metadata mismatch.

Runtime validation comes from display mode-set and scanout tests on DCN 3.0-class hardware. Useful signals include successful modesets across displays attached to OTG instances 3, 4, and 5; stable vblank/vupdate IRQ delivery; no stuck update-lock or GSL state; correct dynamic-refresh behavior; and absence of underflow, blanking, or sync glitches during resolution and refresh-rate changes.

Debug and conformance signals include CRC capture tests over `OTG_CRC*` windows, register-state dumps that show expected `OTG_STATUS_POSITION` and frame counters advancing, vertical interrupt tests at programmed line positions, stereo/interlace mode tests where supported, DSC start-position validation, and pipe update status returning to idle after flips, cursor updates, and DC register updates.

Because this is generated register metadata rather than algorithmic code, the strongest regression tests are cross-checks against the hardware register database and smoke tests that exercise every OTG instance using the same driver paths.
