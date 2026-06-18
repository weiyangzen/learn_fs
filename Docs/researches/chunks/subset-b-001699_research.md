# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_0_0_sh_mask.h lines 29905-32369

## Purpose

This chunk is part of AMD's generated DCN 3.0 ASIC register field mask header. It does not implement executable driver logic; it defines `#define` constants that describe bit positions (`__SHIFT`) and bit masks (`_MASK`) for fields inside DCN output data merger/output timing generator registers.

The range starts at the tail of the `ODM5` OPTC field definitions and then covers the `dce_dc_optc_otg0_dispdec`, `dce_dc_optc_otg1_dispdec`, and beginning of `dce_dc_optc_otg2_dispdec` address blocks. In practical driver terms, these constants are the hardware contract used by AMD display code to program display timing, trigger events, frame counting, CRC capture, vertical interrupts, global swap-lock/update-lock behavior, DSC/ODM width controls, and dynamic refresh rate state for DCN 3.0 display pipes.

## Important Definitions

- `ODM5_OPTC_BYTES_PER_PIXEL__OPTC_DSC_BYTES_PER_PIXEL_MASK`, `ODM5_OPTC_WIDTH_CONTROL__*`, `ODM5_OPTC_INPUT_CLOCK_CONTROL__*`, `ODM5_OPTC_MEMORY_CONFIG__*`, and `ODM5_OPTC_INPUT_SPARE_REGISTER__*`: the tail of the sixth ODM/OPTC instance. These fields describe DSC bytes-per-pixel, segment and DSC slice width, OPTC input clock gate/enable/on status, memory selection, and a spare register.
- `OTG0_*` and `OTG1_*`: complete repeated field-layout blocks for timing generator instances 0 and 1. The two blocks expose the same register shapes with instance-specific macro prefixes.
- `OTG2_*`: the beginning of the timing generator instance 2 block. This chunk covers the OTG2 fields from basic horizontal/vertical timing through `OTG2_OTG_DRR_CONTROL__OTG_DRR_AVERAGE_FRAME__SHIFT`; the remainder of OTG2 continues in the next chunk.
- Horizontal timing registers: `OTG*_OTG_H_TOTAL`, `OTG*_OTG_H_BLANK_START_END`, `OTG*_OTG_H_SYNC_A`, `OTG*_OTG_H_SYNC_A_CNTL`, and `OTG*_OTG_H_TIMING_CNTL` define total pixels, blanking start/end, sync start/end, sync polarity, composite sync enable, cutoff, and horizontal timing divisor/update mode fields.
- Vertical timing and DRR registers: `OTG*_OTG_V_TOTAL`, `OTG*_OTG_V_TOTAL_MIN`, `OTG*_OTG_V_TOTAL_MAX`, `OTG*_OTG_V_TOTAL_MID`, `OTG*_OTG_V_TOTAL_CONTROL`, `OTG*_OTG_DRR_TIMING_INT_STATUS`, `OTG*_OTG_DRR_V_TOTAL_REACH_RANGE`, `OTG*_OTG_DRR_V_TOTAL_CHANGE`, `OTG*_OTG_DRR_TRIGGER_WINDOW`, and `OTG*_OTG_DRR_CONTROL` describe nominal/adaptive vertical totals, DRR event windows, update/reach interrupt state, and average-frame selection.
- Trigger and flow-control registers: `OTG*_OTG_TRIGA_CNTL`, `OTG*_OTG_TRIGB_CNTL`, their manual trigger registers, `OTG*_OTG_FORCE_COUNT_NOW_CNTL`, `OTG*_OTG_FLOW_CONTROL`, `OTG*_OTG_TRIG_MANUAL_CONTROL`, and `OTG*_OTG_MANUAL_FLOW_CONTROL` define source selection, pipe selection, polarity, edge detection, delay, clear bits, manual trigger, and flow-control status fields.
- Generator enable/status registers: `OTG*_OTG_CONTROL`, `OTG*_OTG_MASTER_EN`, `OTG*_OTG_STATUS`, `OTG*_OTG_STATUS_POSITION`, `OTG*_OTG_NOM_VERT_POSITION`, `OTG*_OTG_STATUS_FRAME_COUNT`, `OTG*_OTG_STATUS_VF_COUNT`, `OTG*_OTG_STATUS_HV_COUNT`, `OTG*_OTG_COUNT_CONTROL`, `OTG*_OTG_COUNT_RESET`, `OTG*_OTG_UPDATE_LOCK`, and `OTG*_OTG_DOUBLE_BUFFER_CONTROL` expose enable state, current raster position, frame counters, vertical-frequency counters, horizontal/vertical count snapshots, count reset control, update lock, and double-buffer update controls.
- Interlace, stereo, and vertical-sync controls: `OTG*_OTG_INTERLACE_CONTROL`, `OTG*_OTG_INTERLACE_STATUS`, `OTG*_OTG_MANUAL_FORCE_VSYNC_NEXT_LINE`, `OTG*_OTG_VERT_SYNC_CONTROL`, `OTG*_OTG_STEREO_FORCE_NEXT_EYE`, `OTG*_OTG_STEREO_STATUS`, and `OTG*_OTG_STEREO_CONTROL` define field polarity/counting, stereo eye state, stereo force commands, and vertical-sync force/lock behavior.
- Snapshot and interrupt registers: `OTG*_OTG_SNAPSHOT_STATUS`, `OTG*_OTG_SNAPSHOT_CONTROL`, `OTG*_OTG_SNAPSHOT_POSITION`, `OTG*_OTG_SNAPSHOT_FRAME`, `OTG*_OTG_INTERRUPT_CONTROL`, `OTG*_OTG_V_TOTAL_INT_STATUS`, `OTG*_OTG_VSYNC_NOM_INT_STATUS`, and `OTG*_OTG_GLOBAL_SYNC_STATUS` define capture control/status and interrupt enable/type/status/clear fields for vstartup, vupdate, vupdate-no-lock, vready, vtotal-min, nominal vsync, and stereo/field status.
- Blank data and CRC registers: `OTG*_OTG_BLANK_DATA_COLOR`, `OTG*_OTG_BLANK_DATA_COLOR_EXT`, `OTG*_OTG_CRC_CNTL`, `OTG*_OTG_CRC_CNTL2`, `OTG*_OTG_CRC0_WINDOW*`, `OTG*_OTG_CRC1_WINDOW*`, `OTG*_OTG_CRC*_DATA_*`, `OTG*_OTG_CRC_SIG_RED_GREEN_MASK`, and `OTG*_OTG_CRC_SIG_BLUE_CONTROL_MASK` define blanking color fields, CRC window positions, CRC data readout, CRC component masks, and CRC control.
- Global sync and update-lock registers: `OTG*_OTG_GSL_VSYNC_GAP`, `OTG*_OTG_MASTER_UPDATE_MODE`, `OTG*_OTG_CLOCK_CONTROL`, `OTG*_OTG_VSTARTUP_PARAM`, `OTG*_OTG_VUPDATE_PARAM`, `OTG*_OTG_VREADY_PARAM`, `OTG*_OTG_MASTER_UPDATE_LOCK`, `OTG*_OTG_GSL_CONTROL`, `OTG*_OTG_GSL_WINDOW_X`, `OTG*_OTG_GSL_WINDOW_Y`, `OTG*_OTG_VUPDATE_KEEPOUT`, and `OTG*_OTG_GLOBAL_CONTROL0..4` describe global swap-lock, vstartup/vupdate/vready placement, master update locks, update keepout windows, manual flow-control source selection, and digital update position/field/eye selection.
- Stream/request/DSC support registers in complete OTG0/OTG1 blocks: `OTG*_OTG_M_CONST_DTO0`, `OTG*_OTG_M_CONST_DTO1`, `OTG*_OTG_REQUEST_CONTROL`, `OTG*_OTG_DSC_START_POSITION`, `OTG*_OTG_PIPE_UPDATE_STATUS`, and `OTG*_OTG_SPARE_REGISTER` define DTO phase/modulo, requestor selection/incrementing, DSC start coordinates, pipe update flags, and spare state. OTG2 reaches only `OTG_DRR_CONTROL` in this chunk.

Each field appears as a paired shift and mask macro. Consumers generally combine a field value with the shift and mask through AMD register helper macros rather than writing these constants directly.

## Control Flow

There is no local control flow, branching, or function call behavior in this header chunk. The runtime flow is indirect and table-driven:

1. DCN 3.0 modules include `dcn_3_0_0_offset.h` and `dcn_3_0_0_sh_mask.h`.
2. OPTC/OTG register structs and macro lists bind symbolic register names to hardware offsets and bind field names to the generated masks and shifts.
3. Display code calls helper macros such as `REG_UPDATE`, `REG_GET`, `REG_READ`, `SRI`, `SRI_ARR`, and `SF`.
4. Those helpers use the macros from this header to isolate, update, or test specific MMIO fields for a selected ODM/OTG instance.

Concrete integration references in this tree include `display/dc/optc/dcn30/dcn30_optc.h`, which maps `OTG_DRR_CONTROL`, `OPTC_WIDTH_CONTROL`, `OTG_H_TOTAL`, and `OTG_V_TOTAL_LAST_USED_BY_DRR` fields into the OPTC register/mask tables; `display/dc/optc/dcn30/dcn30_optc.c`, which writes `OPTC_WIDTH_CONTROL`; `display/dc/irq/dcn30/irq_service_dcn30.c`, which wires `OTG_GLOBAL_SYNC_STATUS` fields into interrupt sources; and DCN 3.0 resource, clock, GPIO, DMUB, and IRQ files that include this generated header.

## State And Persistence Behavior

The header itself stores no state and has no persistence behavior. It names fields in hardware registers whose state is owned by the display engine:

- Timing state includes horizontal and vertical totals, blanking intervals, sync positions, vtotal min/max/mid values, DRR transition limits, and raster position counters.
- Control state includes OTG master enable, update lock, double-buffer updates, force-count-now controls, trigger controls, manual flow controls, clock control, global sync lock, and DSC/ODM width settings.
- Status state includes current master-enable status, interlace/stereo field status, trigger occurrence bits, count snapshots, CRC results, pipe update status, vstartup/vupdate/vready/vsync events, and DRR timing/reach events.
- Persistence across modesets or power transitions is not defined by this file. Driver code must program or reprogram the corresponding registers when constructing a display pipe, changing a mode, enabling DRR/VRR, entering/exiting stereo/interlace paths, or restoring hardware after reset/power-gating.

Because the macros describe MMIO bit layouts, an incorrect definition changes how driver code mutates live hardware state. There is no software guard in this file that validates field values or prevents writes to reserved/neighbor bits.

## Dependencies And Integration Points

- The matching offset header, `dcn_3_0_0_offset.h`, supplies register addresses. This `*_sh_mask.h` chunk supplies field positions and masks; both are required for meaningful register access.
- AMD display register helpers in `display/dc` consume these field definitions through generated register structs and macros. The common pattern is that a logical field name such as `OTG_H_TOTAL` maps to an instance-specific macro such as `OTG0_OTG_H_TOTAL__OTG_H_TOTAL_MASK`.
- OPTC implementation files consume the ODM/OPTC fields for DSC slice width, segment width, and input clock/memory control. Public state comments in `display/dc/dc.h` also reference `OPTC_WIDTH_CONTROL->OPTC_SEGMENT_WIDTH`, `OPTC_WIDTH_CONTROL->OPTC_DSC_SLICE_WIDTH`, and `OTG_DRR_CONTROL->OTG_V_TOTAL_LAST_USED_BY_DRR` as relevant hardware-derived values.
- IRQ service code uses `OTG_GLOBAL_SYNC_STATUS` fields such as `VSTARTUP_INT_EN`, `VSTARTUP_EVENT_CLEAR`, `VUPDATE_NO_LOCK_INT_EN`, and `VUPDATE_NO_LOCK_EVENT_CLEAR` to route DCN timing interrupts.
- CRC capture and timing validation paths depend on the `OTG_CRC*`, status-position, frame-count, and HV-count fields matching the hardware so debugfs, diagnostics, or automated display validation can read meaningful values.
- Global swap-lock/update-lock behavior depends on `OTG_GSL_*`, `OTG_MASTER_UPDATE_LOCK`, `OTG_GLOBAL_CONTROL*`, `OTG_VUPDATE_KEEPOUT`, and vstartup/vupdate/vready fields. These are integration points for synchronized multi-pipe updates and stereo/field-aware programming.
- The chunk is source-tree-aligned with AMD GPU display code under `drivers/gpu/drm/amd/display`; it is not Ceph-specific despite living under the repository's `sources/distributed-fs/ceph-client` import path.

## Risks

- This is generated hardware contract data. A one-bit error in a mask or shift can make otherwise correct register helper calls corrupt adjacent fields or fail to update the intended hardware field.
- The OTG0 and OTG1 blocks are large repeated layouts, and OTG2 begins the same pattern. Instance-copy errors are hard to spot by eye and could produce pipe-specific display failures.
- The range starts mid-ODM5 block and ends mid-OTG2 `OTG_DRR_CONTROL`, so whole-file reconciliation must use adjacent chunks to avoid claiming complete coverage for ODM5 or OTG2.
- Timing fields are mode-critical. Bad masks for totals, blanking, sync, or divisor fields can cause blank displays, unstable scanout, incorrect interlace/stereo behavior, or timing underflow symptoms.
- Interrupt status and clear masks are sensitive. Incorrect `*_EVENT_CLEAR`, `*_INT_EN`, or `*_INT_STATUS` fields can cause missed vupdate/vstartup/vready events or stuck interrupts.
- Update-lock and global-sync fields coordinate multi-register programming. Incorrect definitions can expose partially updated timing state, break multi-pipe synchronization, or disrupt variable refresh operation.
- CRC and readback fields are often used for validation and diagnostics. Incorrect masks may hide real display corruption or create false failures in test automation.

## Test Signals

- Build coverage: DCN 3.0 display, DMUB, IRQ, GPIO, clock-manager, resource, and OPTC objects should compile when including `dcn_3_0_0_sh_mask.h`. Missing or malformed macros surface as compile-time errors in register table construction or helper macro expansion.
- Static/register-generation validation: compare this generated header against AMD's authoritative register database and adjacent DCN generations for identical repeated OTG field layouts where the hardware contract is expected to match.
- Modeset/runtime validation: exercise display modes on OTG0, OTG1, and OTG2-backed pipes, including changes to horizontal/vertical timing, blanking, sync polarity, interlace, stereo fields, and enable/disable sequencing.
- DRR/VRR validation: verify vtotal min/max/mid programming, DRR timing-update/reach interrupts, trigger windows, and `OTG_V_TOTAL_LAST_USED_BY_DRR` readback.
- Interrupt validation: verify vstartup, vupdate, vupdate-no-lock, vready, nominal-vsync, and vtotal-min event enable/status/clear behavior through the DCN IRQ service.
- CRC/readback validation: check CRC window programming, CRC data readouts, blank data color fields, pixel data readback, and raster/frame counters against expected scanout behavior.
- Synchronization validation: test global swap-lock, master update lock, update keepout, manual flow control, and digital update position behavior across synchronized multi-pipe updates.
