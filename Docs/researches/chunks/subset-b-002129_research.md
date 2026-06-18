# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_6_0_sh_mask.h lines 27615-30081

## Purpose

This chunk is a generated AMD DCN 3.6 register shift/mask slice for the OPTC/OTG display timing-generator blocks. It contains no executable functions, structs, or inline logic. Its API surface is a large set of C preprocessor constants named as `<register>__<field>__SHIFT` and `<register>__<field>_MASK`; AMDGPU DC code combines these constants with the matching `dcn_3_6_0_offset.h` register addresses and register helper macros to program MMIO fields without hardcoding bit positions.

The assigned range starts inside `OTG0_OTG_TRIGA_CNTL`, then covers the remaining OTG0 field definitions, the full `dce_dc_optc_otg1_dispdec` address block, and almost all of `dce_dc_optc_otg2_dispdec` through `OTG2_OTG_PIPE_UPDATE_STATUS`. `OTG2_OTG_SPARE_REGISTER` and the next `OTG3` block begin immediately after this chunk. The range contains 2,135 `#define` lines, including 1,067 `__SHIFT` constants, 1,091 `_MASK` constants, and 328 comment/address-block markers.

## Important APIs and Register Groups

- Trigger and manual trigger fields: `OTG*_OTG_TRIGA_CNTL`, `OTG*_OTG_TRIGB_CNTL`, `OTG*_OTG_TRIGA_MANUAL_TRIG`, `OTG*_OTG_TRIGB_MANUAL_TRIG`, and `OTG*_OTG_TRIG_MANUAL_CONTROL` define source selection, source pipe selection, polarity, resync bypass, input/polarity status, occurred/clear bits, edge detection, frequency select, delay, and software manual trigger bits.
- Core timing and output control: `OTG*_OTG_CONTROL`, `OTG*_OTG_MASTER_EN`, `OTG*_OTG_DLPC_CONTROL`, `OTG*_OTG_COUNT_CONTROL`, `OTG*_OTG_COUNT_RESET`, `OTG*_OTG_STATUS`, `OTG*_OTG_STATUS_POSITION`, `OTG*_OTG_STATUS_FRAME_COUNT`, `OTG*_OTG_STATUS_VF_COUNT`, `OTG*_OTG_STATUS_HV_COUNT`, `OTG*_OTG_LONG_VBLANK_STATUS`, and `OTG*_OTG_NOM_VERT_POSITION` expose master enable state, disable/start points, output muxing, resync/snapshot location, horizontal/vertical active/blank/sync status, current counters, frame counters, repeated horizontal counting, and count reset.
- Vertical sync, interlace, stereo, and 3D fields: `OTG*_OTG_INTERLACE_CONTROL`, `OTG*_OTG_INTERLACE_STATUS`, `OTG*_OTG_MANUAL_FORCE_VSYNC_NEXT_LINE`, `OTG*_OTG_VERT_SYNC_CONTROL`, `OTG*_OTG_STEREO_FORCE_NEXT_EYE`, `OTG*_OTG_STEREO_STATUS`, `OTG*_OTG_STEREO_CONTROL`, and `OTG*_OTG_3D_STRUCTURE_CONTROL` describe interlace enable/field state, forced-vsync events, stereo eye selection/status, stereo sync output line/polarity, DP-specific stereo output disables, and 3D structure enable/update points.
- Snapshot and interrupt fields: `OTG*_OTG_SNAPSHOT_STATUS`, `OTG*_OTG_SNAPSHOT_CONTROL`, `OTG*_OTG_SNAPSHOT_POSITION`, `OTG*_OTG_SNAPSHOT_FRAME`, `OTG*_OTG_INTERRUPT_CONTROL`, `OTG*_OTG_VERTICAL_INTERRUPT0/1/2_POSITION`, `OTG*_OTG_VERTICAL_INTERRUPT0/1/2_CONTROL`, and `OTG*_OTG_GLOBAL_SYNC_STATUS` define snapshot trigger/clear/readback fields plus interrupt enable/type/status/clear fields for snapshot, force-count-now, forced-vsync, trigger A/B, nominal vsync, GSL gap, vertical interrupt lines, vstartup, vupdate, vupdate-no-lock, and vready.
- Double-buffer and update-lock fields: `OTG*_OTG_UPDATE_LOCK`, `OTG*_OTG_DOUBLE_BUFFER_CONTROL`, `OTG*_OTG_MASTER_UPDATE_MODE`, `OTG*_OTG_MASTER_UPDATE_LOCK`, `OTG*_OTG_VUPDATE_KEEPOUT`, `OTG*_OTG_GLOBAL_CONTROL0` through `OTG*_OTG_GLOBAL_CONTROL4`, and `OTG*_OTG_PIPE_UPDATE_STATUS` define update pending state, DRR/timing/3D/vstartup/DSC double-buffer pending bits, instant update mode, master update lock status, VUPDATE keepout windows, global update-lock enable/select, DIG update position/field/eye selection, and flip/DC-register/cursor pending status.
- CRC and pixel readback fields: `OTG*_OTG_PIXEL_DATA_READBACK0/1`, `OTG*_OTG_CRC_CNTL`, `OTG*_OTG_CRC0/1_WINDOW{A,B}_{X,Y}_CONTROL`, `OTG*_OTG_CRC{0,1,2,3}_DATA_{RG,B}`, `OTG*_OTG_CRC_SIG_RED_GREEN_MASK`, `OTG*_OTG_CRC_SIG_BLUE_CONTROL_MASK`, and the CRC window readback registers expose CRC source selection, continuous/enable state, window selection coordinates, CRC signature masks, data readback values, and window coordinate readbacks.
- Global-swap-lock and synchronization fields: `OTG*_OTG_GSL_VSYNC_GAP`, `OTG*_OTG_GSL_CONTROL`, `OTG*_OTG_GSL_WINDOW_X`, and `OTG*_OTG_GSL_WINDOW_Y` define allowed vsync-gap windows, GSL channel enables, master enable/mode, check/force delays, all-fields behavior, master-update-lock GSL coupling, and X/Y windows used for coordinated multi-pipe updates.
- Dynamic refresh and DSC/request fields: `OTG*_OTG_DRR_TIMING_INT_STATUS`, `OTG*_OTG_DRR_V_TOTAL_REACH_RANGE`, `OTG*_OTG_DRR_V_TOTAL_CHANGE`, `OTG*_OTG_DRR_TRIGGER_WINDOW`, `OTG*_OTG_DRR_CONTROL`, `OTG*_OTG_DRR_CONTOL2`, `OTG*_OTG_M_CONST_DTO0/1`, `OTG*_OTG_REQUEST_CONTROL`, and `OTG*_OTG_DSC_START_POSITION` define DRR timing-update and v-total-reach event/interrupt bits, DRR ranges and trigger windows, average-frame and last-vtotal readbacks, DTO phase/modulo values, duplicate horizontal request mode, and DSC start position.
- Static screen and clock fields: `OTG*_OTG_STATIC_SCREEN_CONTROL` and `OTG*_OTG_CLOCK_CONTROL` provide event-mask controls for static-screen detection and clock enable/gating status fields for the timing generator instance.

## Control Flow and Usage Model

There is no local control flow in this header. The constants become data for higher-level register tables:

1. DCN 3.6 code includes `dcn_3_6_0_offset.h` for register addresses and this header for bit encodings.
2. Resource setup expands register-list macros such as `OPTC_COMMON_REG_LIST_DCN3_5_RI(id)` and field-list macros such as `OPTC_COMMON_MASK_SH_LIST_DCN3_6(__SHIFT)` / `OPTC_COMMON_MASK_SH_LIST_DCN3_6(_MASK)` into `struct dcn_optc_registers`, `struct dcn_optc_shift`, and `struct dcn_optc_mask` instances.
3. Timing-generator and IRQ code then calls shared register helpers (`REG_SET`, `REG_UPDATE`, `REG_GET`, `FD_MASK`, `FD_SHIFT`, and related macros) through those tables.
4. Hardware side effects happen only when consumers read or write the corresponding MMIO registers; this generated header itself only supplies compile-time numeric constants.

`dcn36_resource.c` is the main DCN 3.6 construction point for these OPTC fields. It includes this header, initializes four `optc_regs` instances, and populates `optc_shift`/`optc_mask` from DCN 3.6 OPTC field-list macros. `irq_service_dcn36.c` includes the same header and uses per-instance OTG names in `IRQ_REG_ENTRY` expansions; for example vblank and vupdate-no-lock entries use `OTGx_OTG_GLOBAL_SYNC_STATUS` masks such as `VSTARTUP_INT_EN` and `VUPDATE_NO_LOCK_EVENT_CLEAR`. `dmub_dcn36.c` also includes the generated header to initialize DMUB register masks/shifts, though most fields in this specific chunk are consumed by DC timing-generator and IRQ paths rather than DMCUB internals.

## State and Persistence Behavior

The header has no mutable software state. The state described by the fields lives in DCN display MMIO registers and hardware latches. These values persist until changed by modeset programming, runtime display updates, suspend/resume restore, GPU/display IP reset, or firmware/driver reinitialization.

Several covered groups represent stateful or edge-triggered hardware behavior:

- Master enable, timing counters, blank/active/sync status, frame counters, and current master-enable state reflect live timing-generator state. They are tied to scanout timing and can change every line or frame.
- Trigger, force-count-now, forced-vsync, snapshot, vertical-interrupt, global-sync, and DRR interrupt fields include event-occurred and clear bits. Software must preserve the expected acknowledge semantics when writing these registers.
- Double-buffer pending, update lock, master update lock, VUPDATE keepout, and pipe update status fields coordinate when timing and plane/cursor updates become visible. Persistence across a modeset matters because stale locks or pending bits can block later updates.
- CRC windows, CRC masks, CRC data, and pixel readback fields are diagnostic state. Some fields are programmed controls, while data/readback fields are snapshots of hardware output.
- GSL and global control fields coordinate multi-pipe synchronization. Incorrect persistence can affect only synchronized displays, stereo/interlace modes, or multi-stream timing transitions.
- DRR and DTO fields encode variable-refresh behavior and timing adjustment state. The `*_LAST_USED_BY_DRR` fields are hardware readbacks rather than normal software-owned configuration.

## Dependencies and Integration Points

- The constants must stay paired with `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_6_0_offset.h`; masks/shifts alone are not enough to address hardware.
- The generated names are consumed by AMD display register helper infrastructure in `reg_helper.h` and by macro families such as `SR`, `SRI_ARR`, `SF`, `FD_MASK`, and `FD_SHIFT`.
- DCN 3.6 resource construction in `display/dc/resource/dcn36/dcn36_resource.c` maps these fields into OPTC timing-generator objects. That resource file reuses the DCN 3.5 OPTC register list and adds the DCN 3.6 mask/shift list for CRC polynomial and 32-bit CRC data fields.
- Shared OPTC headers under `display/dc/optc/`, especially `dcn35_optc.h` and `dcn10_optc.h`, define the field-list structures that receive values from this generated header.
- DCN 3.6 IRQ setup in `display/dc/irq/dcn36/irq_service_dcn36.c` depends on `OTG*_OTG_GLOBAL_SYNC_STATUS` and vertical interrupt control/position field masks to map hardware source IDs to DAL interrupt sources.
- Display validation and debugging integrate with these fields through CRC capture, vblank/vline/vupdate IRQs, dynamic refresh-rate programming, update-lock sequencing, GSL synchronization, and per-pipe pending-status queries.

## Risks and Edge Cases

- Generated-header drift is the main risk. If `dcn_3_6_0_sh_mask.h` and `dcn_3_6_0_offset.h` are regenerated or copied out of sync, valid-looking masks may be applied to wrong MMIO addresses.
- The chunk boundary starts after the first two `OTG0_OTG_TRIGA_CNTL` fields. A final merged per-file report should reconcile this with the previous chunk before describing the full TRIGA layout.
- The range ends just before `OTG2_OTG_SPARE_REGISTER` and the `OTG3` address block. Any whole-file analysis must include the next block to cover all timing-generator instances.
- Many registers mix control, status, event, and clear bits. Full-register writes can accidentally clear interrupts, acknowledge events, alter lock state, or overwrite hardware-owned readback fields.
- Repeated OTG0/OTG1/OTG2 layouts are similar but instance-specific. Using OTG0 masks with an OTG1/OTG2 offset, or vice versa, can compile but program the wrong timing generator if table macros are expanded incorrectly.
- Field widths vary sharply: 1-bit enable/status fields sit next to 2-bit mode fields, 5-bit delay fields, 10/11/15-bit coordinate and line fields, 16-bit offsets, 24-bit frame counts, 31-bit/32-bit counters, and full 32-bit DTO values. Callers need input clamping before shifting values into masks.
- Update-lock, VUPDATE keepout, DRR, and GSL fields are timing-sensitive. Incorrect sequencing can produce missed flips, cursor/plane update stalls, vupdate-no-lock interrupts, scanout glitches, or multi-display desynchronization.
- CRC and pixel readback fields are often used for validation. Misprogrammed windows or masks can produce false failures in automated display tests even when scanout is visually correct.
- The generated typo `OTG_DRR_CONTOL2` appears consistently in the register names and must not be “fixed” locally unless the generated offset and all consumers are changed together.

## Test Signals

- Build DCN 3.6 display code and ensure `dcn36_resource.c`, `irq_service_dcn36.c`, and `dmub_dcn36.c` compile against the same generated offset and mask headers.
- Static consistency checks should verify that `OTG0`, `OTG1`, and `OTG2` repeated field layouts are bit-identical where the hardware block is repeated, and that DCN 3.6-specific OPTC fields in `OPTC_COMMON_MASK_SH_LIST_DCN3_6` resolve to generated constants.
- IRQ tests should exercise vblank, vline0, vupdate-no-lock, trigger, force-vsync, and DRR event paths, validating enable masks, clear masks, and source-to-DAL mapping.
- Modeset and page-flip tests should inspect `OTG*_OTG_DOUBLE_BUFFER_CONTROL`, `OTG*_OTG_MASTER_UPDATE_LOCK`, `OTG*_OTG_VUPDATE_KEEPOUT`, and `OTG*_OTG_PIPE_UPDATE_STATUS` for stuck pending bits or stale update locks.
- Variable-refresh tests should cover DRR v-total range, v-total reach interrupts, trigger windows, average-frame modes, and the `OTG_V_TOTAL_LAST_USED_BY_DRR` / `OTG_VCOUNT2_LAST_USED_BY_DRR` readbacks.
- Multi-display synchronization tests should exercise GSL windows, global update lock, stereo/interlace field selection, and master update lock behavior across more than one OTG instance.
- CRC validation should program CRC0/CRC1 windows, masks, continuous enable, polynomial select, and 32-bit CRC data readbacks where supported, then compare expected output signatures across SDR/HDR and DSC/non-DSC timing paths.
- Suspend/resume, GPU reset, and display hotplug tests should verify that master enable, interrupt enables, update locks, GSL, DRR, and CRC diagnostic state are either restored intentionally or reset to safe defaults.
