# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_0_2_sh_mask.h lines 27448-29915

## Scope And Purpose

This chunk covers 2,468 lines from AMD's generated DCN 3.0.2 shift/mask header. It contains C preprocessor constants for Output Timing Generator (`OTG`) register fields: `__SHIFT` macros define field bit positions and `_MASK` macros define already-shifted 32-bit MMIO masks. There are no functions, structs, enums, local variables, storage objects, or runtime branches in this slice.

The range starts at the mask half of `OTG1_OTG_VERT_SYNC_CONTROL`, covers the rest of the `OTG1` register-field block, then covers complete `OTG2` and `OTG3` OTG blocks. It begins the `OTG4` block and ends at `OTG4_OTG_COUNT_CONTROL`, immediately before `OTG4_OTG_COUNT_RESET`. Macro counts in this exact line range are 507 `OTG1` defines, 716 `OTG2` defines, 716 `OTG3` defines, and 202 `OTG4` defines.

In driver terms, this is the field-layout half of the DCN 3.0.2 timing-generator register contract. The matching `dcn_3_0_2_offset.h` file supplies register addresses, while this file supplies bit placement. `dcn302_resource.c` includes both files and declares five timing generators for this ASIC family, so these replicated OTG masks are used to instantiate per-pipe display timing resources.

## Register Blocks Covered

The partial `OTG1` tail begins with force-vsync-next-line status/control masks and then covers stereo, snapshot, interrupt, update-lock, double-buffer, master-enable, blank-color, vertical interrupt, CRC, static-screen, 3D-structure, global-sync-lock, update-window, global-control, manual-trigger, dynamic-refresh-rate, DTO, request, DSC start-position, pipe update status, and spare-register fields.

`OTG2` and `OTG3` are complete repeated timing-generator blocks. Each includes:

- Core horizontal and vertical timing fields: `OTG_H_TOTAL`, `OTG_H_BLANK_START_END`, `OTG_H_SYNC_A`, `OTG_H_SYNC_A_CNTL`, `OTG_H_TIMING_CNTL`, `OTG_V_TOTAL`, `OTG_V_TOTAL_MIN`, `OTG_V_TOTAL_MAX`, `OTG_V_TOTAL_MID`, `OTG_V_TOTAL_CONTROL`, `OTG_V_TOTAL_INT_STATUS`, `OTG_VSYNC_NOM_INT_STATUS`, `OTG_V_BLANK_START_END`, `OTG_V_SYNC_A`, and `OTG_V_SYNC_A_CNTL`.
- Trigger and forced-sync fields: `OTG_TRIGA_CNTL`, `OTG_TRIGA_MANUAL_TRIG`, `OTG_TRIGB_CNTL`, `OTG_TRIGB_MANUAL_TRIG`, `OTG_FORCE_COUNT_NOW_CNTL`, `OTG_FLOW_CONTROL`, `OTG_MANUAL_FORCE_VSYNC_NEXT_LINE`, and `OTG_VERT_SYNC_CONTROL`.
- Master, interlace, status, and counter fields: `OTG_CONTROL`, `OTG_MASTER_EN`, `OTG_INTERLACE_CONTROL`, `OTG_INTERLACE_STATUS`, `OTG_STATUS`, `OTG_STATUS_POSITION`, `OTG_NOM_VERT_POSITION`, `OTG_STATUS_FRAME_COUNT`, `OTG_STATUS_VF_COUNT`, `OTG_STATUS_HV_COUNT`, `OTG_COUNT_CONTROL`, and `OTG_COUNT_RESET`.
- Frame-phase and update fields: `OTG_UPDATE_LOCK`, `OTG_DOUBLE_BUFFER_CONTROL`, `OTG_MASTER_UPDATE_MODE`, `OTG_MASTER_UPDATE_LOCK`, `OTG_VSTARTUP_PARAM`, `OTG_VUPDATE_PARAM`, `OTG_VREADY_PARAM`, `OTG_VUPDATE_KEEPOUT`, `OTG_PIPE_UPDATE_STATUS`, and `OTG_REQUEST_CONTROL`.
- Stereo/3D and pixel output fields: `OTG_STEREO_FORCE_NEXT_EYE`, `OTG_STEREO_STATUS`, `OTG_STEREO_CONTROL`, `OTG_3D_STRUCTURE_CONTROL`, `OTG_BLANK_DATA_COLOR`, `OTG_BLANK_DATA_COLOR_EXT`, `OTG_PIXEL_DATA_READBACK0`, and `OTG_PIXEL_DATA_READBACK1`.
- Interrupt and diagnostic fields: `OTG_INTERRUPT_CONTROL`, `OTG_VERTICAL_INTERRUPT0/1/2_*`, `OTG_SNAPSHOT_*`, `OTG_CRC_CNTL`, `OTG_CRC_CNTL2`, `OTG_CRC0/1_WINDOW*`, `OTG_CRC0/1/2/3_DATA_*`, `OTG_CRC_SIG_*`, and `OTG_STATIC_SCREEN_CONTROL`.
- Global sync and DRR fields: `OTG_GLOBAL_SYNC_STATUS`, `OTG_GSL_CONTROL`, `OTG_GSL_VSYNC_GAP`, `OTG_GSL_WINDOW_X/Y`, `OTG_GLOBAL_CONTROL0` through `OTG_GLOBAL_CONTROL4`, `OTG_DRR_TIMING_INT_STATUS`, `OTG_DRR_V_TOTAL_REACH_RANGE`, `OTG_DRR_V_TOTAL_CHANGE`, `OTG_DRR_TRIGGER_WINDOW`, and `OTG_DRR_CONTROL`.
- Miscellaneous per-pipe fields: `OTG_CLOCK_CONTROL`, `OTG_M_CONST_DTO0/1`, `OTG_DSC_START_POSITION`, and `OTG_SPARE_REGISTER`.

The `OTG4` portion covers the same block shape only through the early timing/counter status registers. It includes horizontal/vertical timing, DRR total controls, trigger A/B controls, force-count-now, flow control, stereo force-next-eye, master control, interlace, pixel readback, live status, position counters, frame/VF/HV counts, and count-control fields. The remaining `OTG4` fields continue after this chunk.

## Important APIs, Types, And Macros

This chunk exposes no callable API. Its interface is the generated macro naming convention consumed by AMD display register helpers:

- `OTG<n>_<REGISTER>__<FIELD>__SHIFT` gives the low bit of a field inside a 32-bit OTG MMIO register.
- `OTG<n>_<REGISTER>__<FIELD>_MASK` gives the field mask at its final bit position.
- Register comments such as `//OTG2_OTG_V_TOTAL_CONTROL` delimit logical hardware registers.
- Address-block comments such as `// addressBlock: dce_dc_optc_otg2_dispdec`, `otg3`, and `otg4` mark repeated OPTC/OTG hardware instances.

The constants are normally reached indirectly through AMDGPU display helper patterns such as `REG_GET`, `REG_SET`, `REG_UPDATE`, `REG_FIELD`, `FD_MASK`, `FD_SHIFT`, and instance register-list macros. Higher-level code deals with timing generators, OPTC resources, DRR, DSC, CRC, and interrupt controls; preprocessor expansion binds those logical field names to concrete `OTG1_`, `OTG2_`, `OTG3_`, or `OTG4_` masks and shifts.

No C type information is encoded here. The implicit data model is 32-bit register words with packed bit fields. Range validation, access direction, sequencing, and hardware reset behavior are the responsibility of the caller and the DCN hardware specification.

## Control Flow And Runtime Behavior

This header has no local control flow. Runtime behavior emerges when DCN 3.0.2 resource and timing-generator code includes this mask header with the companion offset header, constructs per-instance register tables, and performs MMIO read/modify/write operations.

A typical timing-programming path computes a `dc_crtc_timing`, selects a timing-generator instance, then uses register helpers to program horizontal total, blanking, sync, vertical total, vertical blanking, sync polarity, update timing, and master enable fields. Dynamic refresh paths program `OTG_V_TOTAL_MIN/MAX/MID`, `OTG_V_TOTAL_CONTROL`, `OTG_DRR_*`, and related double-buffer update fields. Display Stream Compression paths depend on `OTG_DSC_START_POSITION` and OPTC-side timing/segment state outside this exact chunk. Diagnostics and validation paths read status counters, CRC result registers, vertical interrupt status, static-screen status, and live blank/active/sync flags.

The repeated `OTG2` and `OTG3` blocks show that the same logical timing-generator implementation can be bound to different hardware pipes by changing the macro prefix. The chunk boundaries are meaningful: `OTG1` is partial because its earlier base timing fields appear in the previous chunk, and `OTG4` is partial because later update, CRC, global-sync, and DRR fields appear in the next chunk.

## State And Persistence Behavior

The header itself persists no state. It describes hardware state stored in the display engine's OTG registers:

- Timing state: horizontal total, blank start/end, sync start/end/polarity, vertical total/min/max/mid, vertical blank, vertical sync, interlace, counter reset, repetition/count-by-two, and live horizontal/vertical position.
- Enable and routing state: `OTG_MASTER_EN`, `OTG_CONTROL`, current master-enable state, output mux, flow-control source and polarity, trigger source/pipe/polarity/delay, and forced-count or forced-vsync controls.
- Update and synchronization state: update locks, master update lock, double-buffer pending bits, startup/update/ready parameters, keepout windows, global sync lock control/status, manual trigger, and global control registers.
- DRR state: v-total replacement controls, min/max/mid selection, last-used v-total, change limits, trigger windows, reach-range events, timing interrupt state, and DRR double-buffer mode.
- Interrupt and event state: vertical interrupt enable/status/clear/type fields, snapshot occurred/clear/manual trigger fields, vsync nominal interrupt status, force-count and force-vsync occurred/clear fields, trigger occurred/clear fields, and global-sync event clear/mask/enable fields.
- Diagnostic state: CRC enable/mode/window/result fields, static-screen frame count/events, pixel readback channels, status frame/VF/HV counters, pipe update status, and spare fields.
- Stereo/3D/output-color state: stereo enable/sync/eye/status, forced next eye, 3D structure enable/sync patterns, blank data color and extended color fields.

Writable configuration generally persists until the driver rewrites it or the display block is reset. Status, counter, pending, and interrupt fields are live hardware observations or write-to-clear/acknowledge fields; this header does not distinguish those access semantics beyond names such as `*_STATUS`, `*_INT`, `*_CLEAR`, `*_ACK`, `*_PENDING`, and `*_MSK`.

## Dependencies And Integration Points

This chunk depends on the generated DCN 3.0.2 register database remaining synchronized with the matching offset header. If an offset exists without the right field macros, helper expansions fail to compile; if a mask or shift has the wrong numeric value, the driver can compile but program the wrong hardware bits.

Important integration points include:

- `drivers/gpu/drm/amd/display/dc/resource/dcn302/dcn302_resource.c`, which includes `dcn_3_0_2_offset.h` and `dcn_3_0_2_sh_mask.h` and declares DCN302 timing-generator resources.
- `dcn30` timing-generator/OPTC code, which reuses common register-list structures for DCN 3.0-family hardware.
- Core DC hardware sequencing, which locks/unlocks OPTC programming, waits for double-buffer pending state, sets manual triggers, configures ODM/DSC relationships, and programs timing updates.
- DC/DMUB DRR and FAMS update paths, which pass OTG instance and v-total range values for firmware-assisted refresh changes.
- IRQ service code that maps OTG vertical update, vstartup, vsync, and global-sync status bits to display interrupt sources.
- Debug and test paths that capture OPTC register state, CRCs, underflow/update status, and live timing counters.

Although this file lives under `sources/distributed-fs/ceph-client`, it is imported Linux AMD GPU display-driver code. It is not Ceph filesystem logic.

## Risks And Edge Cases

The largest risk is generated-register drift. One wrong shift or mask can make a correct `REG_UPDATE` alter a neighboring field, miss a write-to-clear bit, or read an unrelated status bit. High-risk packed registers in this chunk include `OTG_V_TOTAL_CONTROL`, `OTG_TRIGA_CNTL`, `OTG_TRIGB_CNTL`, `OTG_INTERRUPT_CONTROL`, `OTG_DOUBLE_BUFFER_CONTROL`, `OTG_GLOBAL_SYNC_STATUS`, `OTG_GSL_CONTROL`, `OTG_DRR_TIMING_INT_STATUS`, and `OTG_CRC_CNTL`.

Chunk boundaries are partial. This slice starts after the `OTG1_OTG_VERT_SYNC_CONTROL` shift definitions and ends before the rest of `OTG4`; final file-level reconciliation must combine adjacent chunks before claiming complete coverage for either instance.

Instance replication can hide pipe-specific errors. `OTG2` and `OTG3` are structurally mirrored, and the `OTG4` prefix starts the same pattern. A single generated prefix, address-block transition, or field-name mismatch may show up only on one display pipe or only in a multi-display/ODM/DRR scenario.

Several fields encode frame-phase-sensitive behavior. Bad update-lock, double-buffer, vstartup/vupdate/vready, manual-trigger, force-vsync, or GSL window masks can produce timing changes on the wrong frame, stuck pending updates, global-sync lock failures, or visible display glitches.

DRR and v-total fields are tightly coupled. Incorrect `V_TOTAL_MIN/MAX/MID`, replacement-enable, reach-range, trigger-window, or change-limit masks can break variable refresh, cause missed events, or allow timing values outside the safe range for the active stream.

Interrupt/status fields use similar names to control fields. Confusing `*_INT_STATUS`, `*_STATUS`, `*_CLEAR`, `*_ACK`, `*_MSK`, and `*_INT_TYPE` can leave interrupts asserted, clear evidence before it is sampled, or mask real timing faults.

CRC and diagnostic fields are useful for validation but can perturb test state if enabled at the wrong time. Window coordinates, one-shot pending bits, stereo/interlace modes, and blank-only/new-pixel selection must match the active timing mode when comparing expected CRCs.

## Test Signals

Build-time validation should compile DCN302 display code that includes this header and exercises timing-generator register tables. Missing or renamed `OTG<n>_*` macros should be caught by preprocessor expansion in register helper structures.

Static validation should compare this generated mask header against `dcn_3_0_2_offset.h` and the authoritative AMD register database. High-signal checks include ensuring every `OTG2` and `OTG3` register in this chunk has both shift and mask definitions for each field, verifying repeated field layouts match across instances, and confirming the `OTG1`/`OTG4` partial boundaries are completed by adjacent chunks.

Runtime validation should exercise DCN302 hardware with multiple active pipes, especially pipes mapped to OTG2 and OTG3. Useful scenarios include mode set, blank/unblank, interlace if supported, stereo/3D paths if exposed, ODM/DSC modes, display reset, suspend/resume, and hot transitions between single and multi-display states.

Timing-specific signals include correct horizontal/vertical totals and sync positions on the link, stable live position counters, frame count increments, correct vblank/vactive/hblank/hactive status transitions, and no stuck double-buffer pending bits after programming.

DRR and refresh tests should vary `v_total_min`, `v_total_max`, and `v_total_mid`, observe v-total reach/change interrupts, verify trigger windows, and confirm firmware-assisted DRR updates target the intended OTG instance.

Interrupt and synchronization tests should enable vertical interrupts, vsync nominal interrupts, force-count-now events, force-vsync-next-line events, and GSL events, then verify status, clear, ack, mask, and interrupt-type behavior.

Diagnostic tests should collect OTG CRCs over known frames, validate static-screen events, check pixel readback channels, and ensure pipe update status reflects completed timing changes without underflow or stale pending state.

## Open Cross-Chunk Questions

- The merge lane should combine this with the previous chunk to describe the full `OTG1` block, including base timing and count-control fields that precede line 27448.
- The merge lane should combine this with the next chunk to describe the complete `OTG4` block and any later OTG instances in the DCN 3.0.2 file.
- Whole-file reconciliation should verify all five timing generators declared for DCN302 have complete offset and shift/mask coverage and that the repeated OTG layouts match the ASIC register source.
