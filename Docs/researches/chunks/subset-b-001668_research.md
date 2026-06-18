# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_2_1_0_sh_mask.h lines 29927-32383

## Scope

This chunk is a generated AMDGPU DCN 2.1 shift/mask header slice. It contains preprocessor constants only: no functions, structs, enums, storage objects, or executable control flow. The exported surface is the usual AMD register-helper contract of `REGISTER__FIELD__SHIFT` and `REGISTER__FIELD_MASK` macros.

The range has 2,457 source lines. Inside the requested line window there are 2,144 `#define` entries: 1,074 shift macros and 1,070 mask macros. The count is intentionally uneven because the chunk ends in the middle of `OTG5_OTG_RANGE_TIMING_INT_STATUS`: line 32383 contains only the first mask for that register, while the remaining masks and subsequent `OTG5_OTG_DRR_CONTROL` fields start in the next chunk.

The covered hardware domain is the DCN output timing generator and display encoder controller register layout for later OTG instances:

- Tail of `OTG3`, beginning at `OTG3_OTG_H_SYNC_A_CNTL` and continuing through `OTG3_OTG_SPARE_REGISTER`.
- Complete generated `addressBlock: dce_dc_optc_otg4_dispdec`, from `OTG4_OTG_H_TOTAL` through `OTG4_OTG_SPARE_REGISTER`.
- Most of generated `addressBlock: dce_dc_optc_otg5_dispdec`, from `OTG5_OTG_H_TOTAL` through the first mask of `OTG5_OTG_RANGE_TIMING_INT_STATUS`.

## Purpose

The chunk provides exact bit positions and already-positioned bit masks for DCN 2.1 OTG timing-generator registers. The OTG block is responsible for display timing production and synchronization: horizontal and vertical totals, blanking, sync pulses, vblank/vupdate/vready events, update locks, dynamic refresh-rate programming, global-swap-lock coordination, CRC capture, stereo/3D timing state, and display pipeline update status.

Higher-level display code does not hand-code these bit positions. Instead, DCN21 resource setup includes this generated header and expands generic field-list macros into per-generation `shift` and `mask` tables. Runtime register helpers then use those tables to encode or decode fields during modesets, page flips, vblank/vline interrupt setup, CRC capture, DSC positioning, dynamic refresh-rate changes, and synchronized multi-display updates.

## Important APIs, Types, And Macros

There are no callable APIs in this chunk. The important interface is the generated macro namespace:

- `OTG3_*`, `OTG4_*`, and `OTG5_*` prefixes identify the hardware instance.
- `*_SHIFT` constants hold the low bit of a field.
- `*_MASK` constants hold the field mask already shifted into register position.
- Register-heading comments such as `//OTG4_OTG_GLOBAL_SYNC_STATUS` group related field macros.
- Address-block comments identify generated register windows, notably `dce_dc_optc_otg4_dispdec` and `dce_dc_optc_otg5_dispdec`.

Important register families in this range include:

- Timing geometry: `OTG_H_TOTAL`, `OTG_H_BLANK_START_END`, `OTG_H_SYNC_A`, `OTG_H_SYNC_A_CNTL`, `OTG_H_TIMING_CNTL`, `OTG_V_TOTAL`, `OTG_V_TOTAL_MIN`, `OTG_V_TOTAL_MAX`, `OTG_V_TOTAL_MID`, `OTG_V_BLANK_START_END`, `OTG_V_SYNC_A`, and `OTG_V_SYNC_A_CNTL`.
- Dynamic refresh rate and vtotal control: `OTG_V_TOTAL_CONTROL`, `OTG_V_TOTAL_INT_STATUS`, and `OTG_DRR_CONTROL` for OTG3 and OTG4. The OTG5 DRR fields are outside this chunk.
- Trigger and manual control: `OTG_TRIGA_CNTL`, `OTG_TRIGA_MANUAL_TRIG`, `OTG_TRIGB_CNTL`, `OTG_TRIGB_MANUAL_TRIG`, `OTG_FORCE_COUNT_NOW_CNTL`, `OTG_MANUAL_FORCE_VSYNC_NEXT_LINE`, `OTG_TRIG_MANUAL_CONTROL`, and `OTG_MANUAL_FLOW_CONTROL`.
- Output state and counters: `OTG_CONTROL`, `OTG_BLANK_CONTROL`, `OTG_PIPE_ABORT_CONTROL`, `OTG_INTERLACE_CONTROL`, `OTG_INTERLACE_STATUS`, `OTG_STATUS`, `OTG_STATUS_POSITION`, `OTG_NOM_VERT_POSITION`, `OTG_STATUS_FRAME_COUNT`, `OTG_STATUS_VF_COUNT`, `OTG_STATUS_HV_COUNT`, `OTG_COUNT_CONTROL`, and `OTG_COUNT_RESET`.
- Interrupts and event status: `OTG_GLOBAL_SYNC_STATUS`, `OTG_INTERRUPT_CONTROL`, `OTG_VERTICAL_INTERRUPT0_CONTROL`, `OTG_VERTICAL_INTERRUPT1_CONTROL`, `OTG_VERTICAL_INTERRUPT2_CONTROL`, `OTG_VSYNC_NOM_INT_STATUS`, and `OTG_RANGE_TIMING_INT_STATUS`.
- Double-buffer and update control: `OTG_UPDATE_LOCK`, `OTG_DOUBLE_BUFFER_CONTROL`, `OTG_MASTER_UPDATE_LOCK`, `OTG_GLOBAL_CONTROL0`, `OTG_GLOBAL_CONTROL1`, `OTG_GLOBAL_CONTROL2`, `OTG_GLOBAL_CONTROL3`, and `OTG_VUPDATE_KEEPOUT`.
- Color, CRC, and readback: `OTG_BLANK_DATA_COLOR`, `OTG_BLANK_DATA_COLOR_EXT`, `OTG_BLACK_COLOR`, `OTG_BLACK_COLOR_EXT`, `OTG_PIXEL_DATA_READBACK0`, `OTG_PIXEL_DATA_READBACK1`, `OTG_CRC_CNTL`, `OTG_CRC_CNTL2`, CRC window controls, CRC data registers, and CRC signal masks.
- Stereo, 3D, GSL, and DSC: `OTG_STEREO_FORCE_NEXT_EYE`, `OTG_STEREO_STATUS`, `OTG_STEREO_CONTROL`, `OTG_3D_STRUCTURE_CONTROL`, `OTG_GSL_VSYNC_GAP`, `OTG_GSL_CONTROL`, `OTG_GSL_WINDOW_X`, `OTG_GSL_WINDOW_Y`, and `OTG_DSC_START_POSITION`.
- Pipeline status: `OTG_PIPE_UPDATE_STATUS` for flip, DC register, cursor update, and vupdate keepout state. The complete OTG5 pipe-update block is outside this line range.

## Control Flow

This header has no local control flow. Runtime behavior is in consumers that include `dcn_2_1_0_offset.h` and this shift/mask header, then bind addresses and fields into register tables.

A typical control path is:

1. DCN21 resource code includes `dcn/dcn_2_1_0_offset.h` and `dcn/dcn_2_1_0_sh_mask.h`.
2. Resource setup expands `TG_COMMON_REG_LIST_DCN2_0(id)` to assign OTG register addresses and expands `TG_COMMON_MASK_SH_LIST_DCN2_0(__SHIFT)` and `TG_COMMON_MASK_SH_LIST_DCN2_0(_MASK)` into timing-generator shift/mask tables.
3. Common OPTC code calls helpers such as `REG_SET`, `REG_UPDATE`, `REG_UPDATE_N`, `REG_GET`, `REG_READ`, `REG_WRITE`, and `REG_WAIT`.
4. Those helpers use this generated field data to program timing, enable or disable CRTC output, lock or unlock double-buffered updates, configure vblank/vline/vupdate events, collect CRCs, and read status fields.

Representative flows represented by the fields in this chunk include:

- CRTC timing programming writes horizontal total, blanking, sync, vertical total, vblank, vsync, and divide-by-two timing fields.
- Dynamic refresh rate programming writes `OTG_V_TOTAL_MIN`, `OTG_V_TOTAL_MAX`, `OTG_V_TOTAL_MID`, and selection bits in `OTG_V_TOTAL_CONTROL`; later status can read `OTG_V_TOTAL_LAST_USED_BY_DRR` where present.
- Vblank and vupdate interrupt setup uses `OTG_GLOBAL_SYNC_STATUS` fields such as `VSTARTUP_INT_EN`, `VSTARTUP_EVENT_CLEAR`, `VUPDATE_NO_LOCK_INT_EN`, and `VUPDATE_NO_LOCK_EVENT_CLEAR`.
- Vline interrupt setup uses `OTG_VERTICAL_INTERRUPT0_POSITION` and `OTG_VERTICAL_INTERRUPT0_CONTROL` fields for line start/end, enable, status, clear, and interrupt type.
- Page flip, register update, cursor update, and keepout status are exposed through `OTG_PIPE_UPDATE_STATUS`.
- CRC capture setup uses `OTG_CRC_CNTL`, `OTG_CRC_CNTL2`, CRC window coordinates, CRC data readbacks, and signal masks.
- Multi-display synchronization and master-update-lock behavior use `OTG_GSL_CONTROL`, `OTG_GSL_VSYNC_GAP`, GSL windows, vupdate keepout, and global control/update-lock fields.
- DSC timing alignment uses `OTG_DSC_START_POSITION` X and line-number fields.

The macros do not express ordering rules, access permissions, volatile behavior, or write-one-to-clear semantics. Callers must know which fields are configuration latches, read-only status, sticky event bits, clear bits, interrupt masks, update-pending indicators, or self-clearing controls.

## State And Persistence Behavior

The file itself stores no state and has no persistence. It describes fields in MMIO registers whose values persist according to DCN hardware semantics until changed by software, hardware state machines, display reset, power management, or GPU reset.

Important hardware state represented here includes:

- Programmed scanout timing: horizontal/vertical totals, blanking windows, sync windows, sync polarity, timing divide mode, and nominal vertical counters.
- Dynamic refresh-rate state: min/max/mid vertical totals, selection bits, mid-frame replacement controls, event masks, last-used-vtotal status, and vtotal event interrupt state.
- Output enable and blanking state: master enable, blank-data enable, display read-request disable, current blank state, pipe abort, clock enable/gating/reset, and busy status.
- Counter and live-position state: current horizontal/vertical counters, frame counters, vertical-field counters, interlace current/next field, snapshot position/frame, and status readbacks for hblank, vblank, hsync, vsync, vupdate, and active display.
- Buffered update state: update locks, double-buffer pending bits, immediate-update control, blank-data double-buffer enable, timing update pending flags, DSC-position update pending, and master update-lock windows.
- Interrupt state: vstartup, vupdate, vupdate-no-lock, vready, vtotal-min, vsync-nominal, vertical interrupt 0/1/2, snapshot, force-count, force-vsync, trigger, GSL gap, and range-timing status/mask/type/clear fields.
- CRC and readback state: programmed CRC selection, one-shot pending flags, DSC/data-stream/data-format modes, CRC windows, CRC result registers, and pixel readback registers.
- Stereo, 3D, and synchronization state: stereo eye/field controls, stereo sync output, 3D structure enable/update/reset/status, GSL master and group enable, GSL delay/check windows, and GSL gap observation.

Incorrect state can survive until a full modeset, CRTC disable/enable, link reconfiguration, suspend/resume, or GPU reset rewrites the affected register block.

## Dependencies And Integration Points

The direct companion file is `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_2_1_0_offset.h`, which provides matching register addresses. This chunk provides bit layout within those registers.

Observed integration points in this tree include:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/resource/dcn21/dcn21_resource.c`, which includes the DCN 2.1 offset and shift/mask headers and expands timing-generator register, shift, and mask lists for DCN21 resources.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/optc/dcn20/dcn20_optc.h`, which defines `TG_COMMON_REG_LIST_DCN2_0` and `TG_COMMON_MASK_SH_LIST_DCN2_0`; those lists consume OTG fields from this generated namespace for DCN2-class timing generators.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/irq/dcn21/irq_service_dcn21.c`, which includes this header and uses generated masks for OTG vblank, vupdate-no-lock, and vertical-line interrupt register entries.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dmub/src/dmub_dcn21.c`, which includes the same generated header for DMUB common register-field definitions. This chunk is not primarily DMUB-specific, but it shares the generation header contract.
- Common OPTC implementation files such as `dcn10_optc.c` and `dcn20_optc.c`, which call register helpers against fields represented here for timing setup, DRR, CRC, DSC, GSL, double-buffer locks, and status collection.
- Display debug and state-reporting structures in `dc.h`, where comments explicitly map fields such as `OTG_H_TOTAL`, `OTG_V_TOTAL`, `OTG_V_TOTAL_CONTROL`, `OTG_GSL_CONTROL`, `OTG_DRR_CONTROL`, `OTG_DOUBLE_BUFFER_CONTROL`, and `OTG_PIPE_UPDATE_STATUS` to captured hardware state.

Although the repository path includes `sources/distributed-fs/ceph-client`, this file is AMDGPU display hardware metadata. It has no Ceph filesystem, distributed storage, network protocol, or persistent filesystem behavior.

## Risks And Edge Cases

The main risk is silent hardware misprogramming. These constants can be syntactically valid while pointing a register helper at the wrong bit. A bad shift or mask can corrupt adjacent fields, truncate values, miss read-only status, acknowledge the wrong event, or leave sticky bits uncleared.

Timing fields are display-critical. Errors in `OTG_H_TOTAL`, blanking, sync, `OTG_V_TOTAL`, or vtotal min/max/mid fields can produce unstable modes, blank displays, refresh-rate mismatch, VRR/DRR failures, broken interlace behavior, or timing that violates sink limits.

Interrupt fields mix enable, status, type, clear, and mask bits in the same registers. Mistakes in `OTG_GLOBAL_SYNC_STATUS`, `OTG_VERTICAL_INTERRUPT*_CONTROL`, `OTG_V_TOTAL_INT_STATUS`, `OTG_INTERRUPT_CONTROL`, or `OTG_RANGE_TIMING_INT_STATUS` can cause missing vblank/vline/vupdate notifications, interrupt storms, stale event state, or page-flip completion problems.

Double-buffer and update-lock fields are ordering-sensitive. Wrong masks in `OTG_UPDATE_LOCK`, `OTG_DOUBLE_BUFFER_CONTROL`, `OTG_MASTER_UPDATE_LOCK`, global controls, GSL controls, or vupdate keepout can cause register updates to latch in the wrong frame, never latch, latch during active scanout, or desynchronize multiple pipes.

CRC and readback fields are validation-sensitive. Incorrect `OTG_CRC_CNTL`, `OTG_CRC_CNTL2`, CRC window, data, or signal mask constants can invalidate automated display CRC tests, especially with DSC, split/combine modes, stereo, or interlace.

The repeated OTG3/OTG4/OTG5 layout creates copy-generation risk. The register families are mostly structurally identical across instances, so a one-off field-width or shift difference should be treated as suspicious unless confirmed by the ASIC register source. This chunk also has artificial boundaries: it starts after the beginning of the OTG3 block and ends before the full `OTG5_OTG_RANGE_TIMING_INT_STATUS` mask set, so per-file conclusions must be reconciled with neighboring chunks.

## Test Signals

Useful validation signals are mostly build coverage plus display hardware behavior:

- Compile coverage for DCN21 resource, IRQ, OPTC, DCCG, DMUB, and display-core code that includes `dcn_2_1_0_sh_mask.h`.
- Generated-header consistency checks that each `*_SHIFT`/`*_MASK` pair matches the field width, that every register has a matching address in `dcn_2_1_0_offset.h`, and that repeated OTG3/OTG4/OTG5 layouts stay aligned where the hardware spec expects them to.
- Modeset tests over multiple timing modes, including high-resolution, high-refresh, low-refresh, interlaced, DSC, ODM/combine, and blanking-sensitive modes.
- Vblank, vline, page-flip, and vupdate interrupt tests that verify events are enabled, delivered, acknowledged, and cleared on all applicable pipes, especially OTG4 and OTG5.
- Dynamic refresh-rate and VRR tests that exercise min/max/mid vtotal programming, vtotal event paths, and last-used-vtotal readback where the full register block is present.
- CRC validation through IGT-style display CRC tests, including one-shot and continuous CRC, windowed CRC, DSC mode, split/combine data streams, and blank-only or active-frame captures.
- Suspend/resume, display off/on, hotplug, and runtime power-management tests that confirm OTG timing, update locks, global sync, interrupt masks, and clock/reset state are restored correctly.
- Multi-display synchronization tests for GSL, master update locks, vupdate keepout windows, and synchronized flips across adjacent timing generators.

Regression symptoms from bad constants include black screen, unstable refresh, missed vblank or vline events, stuck page flips, cursor or plane updates that never latch, visible tearing during atomic updates, failed display CRC tests, broken DSC timing, incorrect VRR behavior, interrupt storms, or failures limited to later pipes corresponding to OTG3, OTG4, or OTG5.

## Cross-Chunk Notes

This is a generated constants-only chunk. It starts in the middle of the OTG3 register family; earlier OTG3 timing fields such as `OTG3_OTG_H_TOTAL`, `OTG3_OTG_H_BLANK_START_END`, and `OTG3_OTG_H_SYNC_A` are owned by the previous chunk. It ends at line 32383 in the middle of `OTG5_OTG_RANGE_TIMING_INT_STATUS`; the remaining masks for that register and the following OTG5 DRR/request/DSC/pipe-update/spare registers belong to the next chunk.

The final per-file document should merge this slice with adjacent chunks before making whole-file claims about DCN 2.1 OTG coverage.
