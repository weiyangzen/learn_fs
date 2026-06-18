# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_2_0_0_sh_mask.h lines 32472-34932

## Scope

This chunk is a generated register field shift/mask slice for AMD DCN 2.0 output timing generator (OTG) blocks. It covers the end of the `dce_dc_optc_otg2_dispdec` address block, full repeated field definitions for `OTG3` and `OTG4`, and the first timing fields for `OTG5`. The content is entirely preprocessor data: each hardware field has a `__SHIFT` value and a matching `_MASK` value used by the display core register-access macros.

## Purpose

The macros describe the bit layout of DCN 2.0 OTG registers. The OTG is the timing side of OPTC: it generates horizontal/vertical timing, blanking, sync, update, trigger, CRC, dynamic refresh, global sync lock, and status signals for each display pipe. Driver code does not manipulate these constants directly in this header; instead, resource setup expands `SF(...)` lists into `struct dcn_optc_shift` and `struct dcn_optc_mask` tables, and OPTC code uses `REG_SET`, `REG_UPDATE`, `REG_GET`, `REG_WAIT`, and related helpers to program/read the selected hardware instance.

## Register Families In This Chunk

- `OTG2` continuation from vertical total interrupt status through `OTG_SPARE_REGISTER`.
- Complete `OTG3` block: horizontal/vertical timing, trigger, force-count, flow control, stereo, enable/blanking, interlace, status/counters, snapshot, interrupts, double buffering, colors, vertical interrupts, CRC engines, static screen, 3D, GSL/global sync, master update lock, DRR, DSC start, pipe update, and spare register.
- Complete `OTG4` block with the same layout and fields as `OTG3`.
- Initial `OTG5` timing fields through the `OTG5_OTG_H_SYNC_A_CNTL` comment at the chunk boundary.

The chunk is highly repetitive by hardware instance. For example, `OTG3_OTG_STATUS_POSITION__OTG_VERT_COUNT_MASK` and `OTG4_OTG_STATUS_POSITION__OTG_VERT_COUNT_MASK` have identical bit positions but apply to different register addresses in the generated address header.

## Important APIs, Types, And Consumers

No C functions or types are defined here. The important integration contract is the macro naming shape:

- `OTGx_REGISTER__FIELD__SHIFT` gives the field lsb.
- `OTGx_REGISTER__FIELD_MASK` gives the field mask.
- `SF(OTG0_REGISTER, FIELD, __SHIFT)` and `SF(OTG0_REGISTER, FIELD, _MASK)` in OPTC headers select these generated constants into runtime tables.

Key consumers observed in the tree:

- `display/dc/inc/hw/optc.h` defines `struct optc`, which stores `tg_regs`, `tg_shift`, and `tg_mask` pointers plus timing limits and state used by the timing-generator functions.
- `display/dc/optc/dcn10/dcn10_optc.h` defines the base OTG register and field lists. It includes many fields in this chunk such as `OTG_V_TOTAL_CONTROL`, `OTG_TRIGA_CNTL`, `OTG_CRC_CNTL`, status, interrupt, blanking, stereo, and static-screen fields.
- `display/dc/optc/dcn20/dcn20_optc.h` extends the DCN1 list for DCN2 with fields in this chunk: `OTG_GLOBAL_CONTROL1`, `OTG_GLOBAL_CONTROL2`, `OTG_GSL_WINDOW_X/Y`, `OTG_VUPDATE_KEEPOUT`, `OTG_DSC_START_POSITION`, `OTG_CRC_CNTL2`, `OTG_MANUAL_FLOW_CONTROL`, `OTG_DRR_CONTROL`, and `OTG_PIPE_UPDATE_STATUS`.
- `display/dc/optc/dcn10/dcn10_optc.c` and `display/dc/optc/dcn20/dcn20_optc.c` use these fields through register helper macros for CRTC enable/disable, reset triggers, dynamic refresh rate, manual triggers, CRC, blanking, and status polling.

## Functional Areas

### Timing And Dynamic Refresh

The timing fields include:

- Horizontal totals and sync/blank windows: `OTG_H_TOTAL`, `OTG_H_BLANK_START_END`, `OTG_H_SYNC_A`, `OTG_H_SYNC_A_CNTL`, `OTG_H_TIMING_CNTL`.
- Vertical totals and sync/blank windows: `OTG_V_TOTAL`, `OTG_V_TOTAL_MIN`, `OTG_V_TOTAL_MAX`, `OTG_V_TOTAL_MID`, `OTG_V_TOTAL_CONTROL`, `OTG_V_BLANK_START_END`, `OTG_V_SYNC_A`, `OTG_V_SYNC_A_CNTL`.
- DRR status/control: `OTG_DRR_CONTROL` exposes `OTG_DRR_AVERAGE_FRAME` and `OTG_V_TOTAL_LAST_USED_BY_DRR`.

`optc1_set_drr()` programs `OTG_V_TOTAL_MIN/MAX/MID` and updates `OTG_V_TOTAL_CONTROL` selectors. `optc2_setup_manual_trigger()` also updates `OTG_V_TOTAL_CONTROL` so DMCUB/manual trigger flows can alter OTG timings. The relevant masks in this chunk are therefore timing-critical: a wrong bit position can corrupt vtotal selection, frame pacing, or variable refresh behavior.

### Trigger And Reset Control

The trigger family includes `OTG_TRIGA_CNTL`, `OTG_TRIGA_MANUAL_TRIG`, `OTG_TRIGB_CNTL`, `OTG_TRIGB_MANUAL_TRIG`, `OTG_FORCE_COUNT_NOW_CNTL`, `OTG_VERT_SYNC_CONTROL`, `OTG_TRIG_MANUAL_CONTROL`, and `OTG_MANUAL_FLOW_CONTROL`.

The driver uses trigger A heavily:

- `optc1_enable_reset_trigger()` selects a source pipe, chooses vsync edge detection based on polarity, and enables force-count behavior.
- `optc1_enable_crtc_reset()` configures trigger edge and either next-line vsync force or immediate count force.
- `optc1_disable_reset_trigger()` clears trigger and force-vsync state.
- `optc2_setup_manual_trigger()` programs trigger A source 21 with the current OTG instance and sets `OTG_SET_V_TOTAL_MIN_MASK` to use TRIGA.
- `optc2_program_manual_trigger()` writes `OTG_TRIGA_MANUAL_TRIG`.

The chunk includes both control bits and sticky/status bits such as `OTG_TRIGA_OCCURRED`, `OTG_TRIGA_CLEAR`, `OTG_FORCE_COUNT_NOW_OCCURRED`, and `OTG_FORCE_COUNT_NOW_CLEAR`. These fields affect synchronization between pipes and controlled timing changes.

### Enable, Blanking, Interlace, Stereo, And Status

The core state fields include:

- `OTG_CONTROL`: master enable, start/disable point control, current enable state, field polarity, read request disable, and AV sync bits.
- `OTG_BLANK_CONTROL`, `OTG_MASTER_EN`, `OTG_BLANK_DATA_COLOR(_EXT)`, and `OTG_BLACK_COLOR(_EXT)` for blanking and output color state.
- `OTG_INTERLACE_CONTROL` and `OTG_INTERLACE_STATUS`.
- `OTG_STEREO_FORCE_NEXT_EYE`, `OTG_STEREO_STATUS`, and `OTG_STEREO_CONTROL`.
- `OTG_STATUS`, `OTG_STATUS_POSITION`, `OTG_STATUS_FRAME_COUNT`, `OTG_STATUS_VF_COUNT`, and `OTG_STATUS_HV_COUNT`.

These are consumed by functions such as `optc1_is_tg_enabled()`, `optc1_wait_for_state()`, position readers, blanking helpers, stereo helpers, and timing reads. Several fields are read-only hardware state or sticky status rather than ordinary writable configuration.

### Snapshot, Interrupt, And Update Lock

The chunk defines snapshot fields (`OTG_SNAPSHOT_STATUS`, `OTG_SNAPSHOT_CONTROL`, `OTG_SNAPSHOT_POSITION`, `OTG_SNAPSHOT_FRAME`), interrupt controls (`OTG_INTERRUPT_CONTROL`, vertical interrupt position/control registers, `OTG_V_TOTAL_INT_STATUS`, `OTG_VSYNC_NOM_INT_STATUS`, `OTG_RANGE_TIMING_INT_STATUS`), and synchronization/update controls (`OTG_UPDATE_LOCK`, `OTG_DOUBLE_BUFFER_CONTROL`, `OTG_MASTER_UPDATE_LOCK`, `OTG_GLOBAL_CONTROL0/1/2/3`, `OTG_VUPDATE_KEEPOUT`, `OTG_PIPE_UPDATE_STATUS`).

DCN2-specific code uses:

- `OTG_GLOBAL_CONTROL1` and `OTG_GLOBAL_CONTROL2` in double-buffer lock/unlock helpers.
- `OTG_VUPDATE_KEEPOUT` to avoid unsafe update windows.
- `OTG_PIPE_UPDATE_STATUS` to report pending/taken flip, DC register, cursor, and vupdate keepout state.

Interrupt/status fields often pair an event bit, an interrupt status bit, a clear/ack bit, a mask bit, and sometimes type/position selectors. These must be handled as write-one-to-clear or hardware-sticky semantics in consuming code; this header only supplies bit locations.

### CRC And Test Signals

CRC fields include:

- `OTG_CRC_CNTL` and `OTG_CRC_CNTL2`.
- Window controls for CRC engines 0 and 1: `OTG_CRC0_WINDOWA/B_X/Y_CONTROL`, `OTG_CRC1_WINDOWA/B_X/Y_CONTROL`.
- Data readbacks for engines 0 through 3: `OTG_CRC{0..3}_DATA_RG` and `OTG_CRC{0..3}_DATA_B`.
- Signature masks: `OTG_CRC_SIG_RED_GREEN_MASK` and `OTG_CRC_SIG_BLUE_CONTROL_MASK`.

`optc1_configure_crc()` writes window controls and enables CRC0 or CRC1 selection through `OTG_CRC_CNTL`. `optc2_configure_crc()` first programs `OTG_CRC_CNTL2` with DSC/ODM mode information, then delegates to the base implementation. `optc1_get_crc()` reads the RGB/YCbCr component CRC fields. Incorrect masks here would break debugfs/validation CRC capture or cause mismatched CRC values under DSC/ODM modes.

### Global Sync Lock, GSL, DSC, And ODM-Adjacent Timing

The chunk includes global sync lock support:

- `OTG_GSL_VSYNC_GAP`, `OTG_GSL_CONTROL`, `OTG_GSL_WINDOW_X`, `OTG_GSL_WINDOW_Y`.
- `OTG_GLOBAL_SYNC_STATUS` for startup/update/ready events, no-lock status, interrupt enables/types, clear bits, stereo, and field number status.
- `OTG_MASTER_UPDATE_MODE`, `OTG_MASTER_UPDATE_LOCK`, and global controls for master update lock windows.

It also includes `OTG_DSC_START_POSITION`, which coordinates DSC start x/line position with the timing generator, and `OTG_REQUEST_CONTROL`, which affects request mode for horizontal duplicate behavior. DCN2 resource and OPTC code add these registers to the common OTG tables.

## Control Flow

This header has no executable control flow. Runtime control flow is indirect:

1. DCN resource initialization builds per-OTG register address arrays and per-field shift/mask tables from generated macros like those in this chunk.
2. `struct optc` instances receive pointers to those tables.
3. Timing-generator functions call register helper macros, which use the current OTG instance's register address plus the field shift/mask to modify only the selected field.
4. Hardware state changes asynchronously with scanout, vblank, vupdate, interrupts, CRC capture, DRR, and trigger events; driver code polls or clears status fields using the same masks.

The repeated `OTG2`, `OTG3`, `OTG4`, and `OTG5` prefixes are not loop logic. They are separate hardware-instance namespaces that the generated address/mask tables map into a uniform software interface.

## State And Persistence Behavior

The state represented by this chunk is MMIO hardware state. It persists in GPU registers while the display block is powered and is normally reprogrammed during modesets, DPMS transitions, resume, or pipe reconfiguration. Important state categories:

- Latched configuration: timing totals, sync/blank windows, trigger source selection, blank colors, CRC setup, global sync/update-lock configuration.
- Live counters/status: horizontal/vertical count, frame count, blank/active/sync status, interlace/stereo status, pipe update pending/taken status.
- Sticky events and clear bits: vtotal min events, vsync nominal events, trigger occurred bits, global sync events, range timing events, CRC one-shot pending bits.

The header itself has no persistence layer and no defaults. Hardware reset values and power-gating behavior come from the ASIC, firmware, and display driver init paths.

## Dependencies And Integration Points

- Depends on generated companion address headers, especially `dcn_2_0_0_offset.h`, for register addresses matching these field definitions.
- Depends on display core register-helper macros that combine register address, shift, and mask tables.
- Integrates with `dcn10_optc.h` base OTG mask lists and `dcn20_optc.h` DCN2 extensions.
- Integrates with `dcn20_resource.c` style resource construction that binds the generated masks into arrays for each timing generator.
- Integrates with DMCUB/firmware-managed timing changes through fields such as `OTG_V_TOTAL_CONTROL`, manual trigger fields, and DRR controls.
- Integrates with IRQ service code through global sync and vupdate/vstartup/vready event fields on later DCN families with the same register model.

## Risks And Edge Cases

- Generated-header drift: if this mask header and the matching offset/header tables are from different ASIC register database revisions, the driver can write valid field names to wrong bits or wrong addresses.
- Instance-copy mistakes: the `OTG2`, `OTG3`, `OTG4`, and `OTG5` blocks must remain consistent. A single copied mask error for one instance can affect only that pipe, making failures topology-dependent.
- Read/write semantic confusion: status, clear, ack, interrupt mask, and enable bits coexist in the same registers. Treating sticky clear bits as persistent config can lose interrupts or hide events.
- Timing-window hazards: update lock, vupdate keepout, double-buffer mode, global sync, and DRR fields interact with scanout timing. Incorrect masks may only fail under high refresh, VRR/DRR, multi-display, ODM, or DSC.
- CRC limitations: CRC window fields are 15-bit x/y style fields and result fields are 16-bit components. Out-of-range values are masked by hardware/register helpers rather than validated here.
- Boundary chunking: this slice starts mid-`OTG2` and ends at the beginning of `OTG5`; final file-level research must reconcile adjacent chunks to describe full `OTG2` and `OTG5` coverage.

## Test Signals

Useful validation signals for code that consumes this chunk:

- Build coverage: compile AMDGPU DCN2 display code with generated mask tables enabled; missing or renamed macros should fail at compile time in OPTC mask list expansion.
- Modeset smoke: enable displays on OTG2, OTG3, OTG4, and OTG5-capable hardware paths and verify timing, vblank, and scanout position are sane.
- DRR/VRR tests: exercise `optc1_set_drr()` and `optc2_get_last_used_drr_vtotal()` and confirm vtotal min/max/mid behavior and last-used vtotal readback.
- Trigger/reset synchronization: validate multi-pipe timing synchronization, manual trigger setup/programming, and triggered reset occurrence/clear behavior.
- CRC capture: enable CRC0/CRC1 with windowed capture and, on DCN2 DSC/ODM modes, verify `OTG_CRC_CNTL2` mode fields produce expected CRC stability.
- Interrupt/status tests: verify vstartup/vupdate/vready, vertical interrupt, vsync nominal, range timing, and pipe update status events can be observed and cleared without losing subsequent events.
- Suspend/resume and power-gating tests: confirm OTG state is reinitialized rather than relying on stale register contents after display block reset.
