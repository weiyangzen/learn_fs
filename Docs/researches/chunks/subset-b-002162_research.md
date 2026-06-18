# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_4_1_0_sh_mask.h lines 27731-30197

## Scope

This chunk is a generated DCN 4.1.0 register field shift/mask block for the display timing generator path. It contains `#define` constants for OTG/OPTC bitfields, mostly for OTG instances 1-3:

- The chunk starts in the middle of `OTG1_OTG_TRIGA_CNTL`, after the first trigger-A source-select field.
- It covers the remainder of the OTG1 field block from trigger control through spare/P-state/update status registers.
- It covers the full `addressBlock: dcn_dcec_optc_otg2_dispdec` OTG2 block.
- It covers most of `addressBlock: dcn_dcec_optc_otg3_dispdec`, ending at `OTG3_OTG_DRR_TRIGGER_WINDOW__OTG_DRR_TRIGGER_WINDOW_START_X__SHIFT`; the corresponding end-X/mask fields continue outside this chunk.

There are no C functions or storage objects here. The file supplies preprocessor data that other display code folds into register-address, shift, and mask tables.

## Purpose

The constants describe how software packs and extracts fields from 32-bit display timing generator registers. Each field is emitted as a pair:

- `...__FIELD__SHIFT`: bit offset used by register helper macros.
- `...__FIELD_MASK`: bit mask used to isolate or update the field.

These definitions are critical because DCN display code uses generic helper macros such as `REG_SET`, `REG_UPDATE`, `REG_GET`, and `REG_WAIT`. Those helpers only work correctly when the generated shift/mask values match the ASIC register layout.

## Important Macro Groups

The chunk is organized as repeated per-OTG blocks. The same register families appear for OTG2 and OTG3, with the OTG1 block partially included from trigger-A onward.

- Timing geometry: `OTG*_OTG_H_TOTAL`, `OTG*_OTG_H_BLANK_START_END`, `OTG*_OTG_H_SYNC_A`, `OTG*_OTG_V_TOTAL`, `OTG*_OTG_V_BLANK_START_END`, `OTG*_OTG_V_SYNC_A`, and related control registers define total, blanking, sync start/end, sync polarity, and horizontal timing divide mode.
- Variable refresh and DRR: `OTG*_OTG_V_TOTAL_MIN`, `MAX`, `MID`, `OTG_V_TOTAL_CONTROL`, `OTG_DRR_TIMING_INT_STATUS`, `OTG_DRR_V_TOTAL_REACH_RANGE`, `OTG_DRR_V_TOTAL_CHANGE`, `OTG_DRR_TRIGGER_WINDOW`, `OTG_DRR_CONTROL`, and `OTG_DRR_CONTOL2` provide the fields used for dynamic refresh-rate timing limits, event status, trigger windows, and last-used timing readback.
- Trigger and manual sync: `OTG*_OTG_TRIGA_CNTL`, `OTG*_OTG_TRIGB_CNTL`, `OTG*_OTG_TRIGA_MANUAL_TRIG`, `OTG*_OTG_TRIGB_MANUAL_TRIG`, `OTG*_OTG_TRIG_MANUAL_CONTROL`, `OTG*_OTG_MANUAL_FLOW_CONTROL`, `OTG*_OTG_FORCE_COUNT_NOW_CNTL`, and `OTG*_OTG_MANUAL_FORCE_VSYNC_NEXT_LINE` configure external/manual triggers, edge detection, force-count operations, and force-vsync behavior.
- Enable, clock, and state: `OTG*_OTG_CONTROL`, `OTG*_OTG_MASTER_EN`, `OTG*_OTG_CLOCK_CONTROL`, `OTG*_OTG_STATUS`, `OTG*_OTG_STATUS_POSITION`, `OTG*_OTG_STATUS_FRAME_COUNT`, `OTG*_OTG_STATUS_VF_COUNT`, and `OTG*_OTG_STATUS_HV_COUNT` expose master enable, output mux selection, clock gating/busy state, blank/sync active state, counters, and current master-enable state.
- Interlace, stereo, and 3D: `OTG*_OTG_INTERLACE_CONTROL`, `OTG*_OTG_INTERLACE_STATUS`, `OTG*_OTG_STEREO_CONTROL`, `OTG*_OTG_STEREO_STATUS`, `OTG*_OTG_STEREO_FORCE_NEXT_EYE`, and `OTG*_OTG_3D_STRUCTURE_CONTROL` define stereo eye selection, field state, sync output, and 3D structure selection.
- Interrupts and events: `OTG*_OTG_INTERRUPT_CONTROL`, `OTG*_OTG_VERTICAL_INTERRUPT{0,1,2}_POSITION`, `OTG*_OTG_VERTICAL_INTERRUPT{0,1,2}_CONTROL`, `OTG*_OTG_GLOBAL_SYNC_STATUS`, `OTG*_OTG_V_TOTAL_INT_STATUS`, and `OTG*_OTG_VSYNC_NOM_INT_STATUS` provide enable, status, clear, and type bits for vstartup, vupdate, vready, vertical-line, DRR, and set-vtotal-min events.
- Update locking and global sync: `OTG*_OTG_UPDATE_LOCK`, `OTG*_OTG_DOUBLE_BUFFER_CONTROL`, `OTG*_OTG_MASTER_UPDATE_LOCK`, `OTG*_OTG_MASTER_UPDATE_MODE`, `OTG*_OTG_GSL_CONTROL`, `OTG*_OTG_GSL_WINDOW_X/Y`, `OTG*_OTG_VUPDATE_KEEPOUT`, and `OTG*_OTG_GLOBAL_CONTROL0-4` define double-buffer/update-lock behavior, global swap lock, keepout windows, and update positions.
- CRC and readback: `OTG*_OTG_CRC_CNTL`, CRC window/data/readback registers, `OTG*_OTG_CRC_SIG_*_MASK`, and `OTG*_OTG_PIXEL_DATA_READBACK*` support pipe CRC capture and pixel data readback for debug, validation, and userspace CRC workflows.
- Power and update status: `OTG*_OTG_PSTATE_REGISTER`, `OTG*_OTG_STATIC_SCREEN_CONTROL`, `OTG*_OTG_PIPE_UPDATE_STATUS`, `OTG*_OTG_REQUEST_CONTROL`, `OTG*_OTG_M_CONST_DTO0/1`, and `OTG*_OTG_SPARE_REGISTER` provide p-state keepout/unblank controls, static-screen detection, pending update status, request mode for duplicate horizontal timing, M/N DTO constants, and spare fields.

## Integration Points

The generated field constants are consumed by DCN401 display code through table-construction macros:

- `display/dc/resource/dcn401/dcn401_resource.c` includes this header and initializes `optc_shift` and `optc_mask` with `OPTC_COMMON_MASK_SH_LIST_DCN401(__SHIFT)` and `OPTC_COMMON_MASK_SH_LIST_DCN401(_MASK)`. `dcn401_timing_generator_create()` assigns those tables to each `struct optc` instance.
- `display/dc/optc/dcn401/dcn401_optc.c` is the primary functional consumer. It updates fields represented by this chunk when enabling/disabling CRTC timing (`OTG_CONTROL`, `OTG_MASTER_EN`, `OTG_CLOCK_CONTROL`), configuring ODM combine/bypass (`OTG_H_TIMING_CNTL`), programming DRR (`OTG_V_TOTAL_*`, `OTG_V_TOTAL_CONTROL`), setting output mux (`OTG_OUT_MUX`), programming global sync (`OTG_VSTARTUP_PARAM`, `OTG_VUPDATE_PARAM`, `OTG_VREADY_PARAM`, `OTG_PSTATE_REGISTER`), programming vupdate keepout (`OTG_VUPDATE_KEEPOUT`), and waiting for update-lock status (`OTG_MASTER_UPDATE_LOCK`).
- `display/dc/irq/dcn401/irq_service_dcn401.c` includes this header and uses OTG interrupt field masks to construct IRQ source descriptors for vblank/vstartup, vupdate-no-lock, and vertical-line interrupts through `OTG_GLOBAL_SYNC_STATUS` and `OTG_VERTICAL_INTERRUPT{0,1,2}_CONTROL`.
- `display/dc/optc/dcn10/dcn10_optc.h` defines the `struct dcn_optc_shift` and `struct dcn_optc_mask` members that receive these generated values. DCN401 extends the common field list with `OTG_PSTATE_REGISTER` fields such as `OTG_PSTATE_KEEPOUT_START`, `OTG_PSTATE_EXTEND`, `OTG_UNBLANK`, and `OTG_PSTATE_ALLOW_WIDTH_MIN`.
- `display/dc/dc.h` contains debug/register-state fields matching several registers in this chunk, including DRR trigger window/change limit, vertical interrupt line/enables, global sync parameters, trigger control, static-screen/update-lock fields, and GSL fields.

## Control Flow and State Behavior

This header does not implement control flow, but it directly shapes hardware control flow in the callers:

- CRTC enable writes `OTG_CONTROL.OTG_MASTER_EN` and waits on `OTG_CURRENT_MASTER_EN_STATE`/`OTG_CLOCK_CONTROL.OTG_BUSY` during disable paths.
- DRR programming writes min/max/mid vertical totals and, when firmware-assisted modes are not used, programs trigger masks in `OTG_V_TOTAL_CONTROL`; those fields decide when hardware switches between vertical totals.
- Global sync programming writes vstartup/vupdate/vready offsets. Interrupt service then uses `OTG_GLOBAL_SYNC_STATUS` bits to enable and clear those timing events.
- Update locking writes `OTG_MASTER_UPDATE_LOCK` and polls `UPDATE_LOCK_STATUS`; keepout fields define regions where master-update-lock release is blocked.
- CRC/readback fields do not persist in software, but they expose hardware state used to validate scanout and detect data mismatches.

The persistent state is hardware register state. Software persistence is limited to the cached register table pointers in each `struct optc` and debug snapshots of selected register values. Reset, modeset, power-gating, or display reprogramming can invalidate the register contents, so consumers must reprogram the hardware path rather than assuming these values are retained.

## Dependencies

- Depends on the paired generated offset header `dcn_4_1_0_offset.h` for register addresses. This file supplies only field positions/masks.
- Depends on display register helper macros (`REG_SET`, `REG_UPDATE`, `REG_GET`, `REG_WAIT`, and `SF`-style table macros) to combine offsets, shifts, and masks.
- Depends on DCN401-specific resource construction to bind the generated values to `struct optc`.
- Depends on ASIC register naming consistency. The preprocessor concatenation style means a typo in a generated macro name or a missing field breaks builds at compile time.

## Risks and Edge Cases

- Off-by-one or wrong-width masks can corrupt adjacent timing fields. That is high impact for CRTC enable, vblank/vupdate interrupts, DRR, update locking, and CRC configuration.
- The chunk boundary splits logical registers: it begins inside `OTG1_OTG_TRIGA_CNTL` and ends inside `OTG3_OTG_DRR_TRIGGER_WINDOW`. Any per-chunk review must account for adjacent chunks before declaring the full OTG1/OTG3 register families complete.
- Several event registers contain clear/ack fields next to status and enable fields. Incorrect use of masks can clear pending interrupts or leave interrupts stuck.
- DRR and FAMS/FAMS2 paths can be firmware-assisted or direct-register programmed. The same field definitions must match both direct driver writes and any firmware expectations about OTG instance numbering and trigger bits.
- `OTG_DRR_CONTOL2` appears with the generated spelling `CONTOL2`; consumers must use the generated name exactly if they reference it.
- Per-instance repetition makes copy/paste or generation errors easy to miss. OTG1/OTG2/OTG3 values should remain structurally aligned unless the ASIC intentionally differs.

## Test Signals

Useful validation signals for this chunk are mostly build-time and hardware/display behavior checks:

- Compile coverage for DCN401 display code, especially `dcn401_resource.c`, `dcn401_optc.c`, and `irq_service_dcn401.c`, catches missing or renamed generated fields.
- Modeset tests should verify CRTC enable/disable, output mux selection, ODM combine/bypass, and timing programming across OTG instances 1-3.
- Vblank, vupdate, and vertical-line interrupt tests should confirm enable/clear/status behavior through `OTG_GLOBAL_SYNC_STATUS` and `OTG_VERTICAL_INTERRUPT*`.
- Variable refresh/DRR tests should exercise min/max/mid vtotal programming, manual trigger setup, trigger-window programming, and last-used-vtotal readback.
- CRC tests should verify `OTG_CRC_CNTL`, CRC windows, and CRC data readback against expected frame contents.
- Power-management and p-state transition tests should cover `OTG_PSTATE_REGISTER` and vupdate keepout behavior, looking for underflow, missed vblank, or update-lock timeout symptoms.
