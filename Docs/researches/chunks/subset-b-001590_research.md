# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_1_0_sh_mask.h lines 22603-25075

## Purpose

This chunk is part of AMDGPU's generated DCN 1.0 register field mask header. It contains no executable C code; it publishes preprocessor constants that describe bit positions and masks for display timing-generator registers.

The range covers the tail of `OTG1`, all visible `OTG2` and `OTG3`, and the beginning of `OTG4` inside the `dce_dc_optc_otg*_dispdec` address blocks:

- `OTG1` from count reset / force-vsync controls through stereo, snapshot, interrupt, update-lock, double-buffer, test-pattern, blank/black color, vertical interrupt, CRC, static-screen, 3D structure, global-sync, global-sync-lock, GSL, vupdate keepout, global-control, trigger/manual-flow, range timing, DRR, request, and spare-register fields.
- Complete `OTG2` and `OTG3` register-mask runs for horizontal and vertical timing, total/min/max/mid totals, trigger controls, flow control, stereo and AV sync, blanking, pipe abort, interlace, status/readback counters, snapshots, interrupts, update locking, test patterns, CRC windows/data, static-screen detection, global-swap-lock, GSL windows, DRR, request control, and spare registers.
- The start of `OTG4`, from horizontal timing through stereo control. The following chunk continues `OTG4` snapshot, interrupt, CRC, global-sync, and later timing-generator families.

Each hardware field is exposed as a pair of macros: `REGISTER__FIELD__SHIFT` gives the low bit index, and `REGISTER__FIELD_MASK` gives the already-positioned bit mask. Driver code combines these constants with matching register-address definitions from `dcn_1_0_offset.h` and the DC register helper macros that generate read/modify/write operations.

## Important APIs, Types, And Macros

There are no functions, structs, enums, or persistent objects in this chunk. The API surface is the generated macro namespace.

The `OTG*_OTG_H_*` and `OTG*_OTG_V_*` families describe timing geometry. They include horizontal total, horizontal blank start/end, horizontal sync start/end/polarity, horizontal timing division, vertical total, vertical total min/max/mid, vertical total control, vertical blank start/end, vertical sync start/end/polarity, vstartup/vupdate/vready parameters, and nominal/status counter positions.

The trigger and flow families include `OTG_TRIGA_CNTL`, `OTG_TRIGB_CNTL`, `OTG_TRIGA_MANUAL_TRIG`, `OTG_TRIGB_MANUAL_TRIG`, `OTG_FORCE_COUNT_NOW_CNTL`, and `OTG_FLOW_CONTROL`. These masks cover trigger source selection, source pipe selection, polarity, resync bypass, input and occurrence status, edge detection mode, frequency select, delay, clear bits, manual trigger bits, force-count-now modes/checks/trigger selection/clear, and flow-control source/polarity/granularity/status.

The mode and status families include `OTG_CONTROL`, `OTG_MASTER_EN`, `OTG_BLANK_CONTROL`, `OTG_PIPE_ABORT_CONTROL`, `OTG_INTERLACE_CONTROL`, `OTG_INTERLACE_STATUS`, `OTG_FIELD_INDICATION_CONTROL`, `OTG_STATUS`, `OTG_STATUS_POSITION`, `OTG_NOM_VERT_POSITION`, `OTG_STATUS_FRAME_COUNT`, `OTG_STATUS_VF_COUNT`, `OTG_STATUS_HV_COUNT`, `OTG_COUNT_CONTROL`, `OTG_COUNT_RESET`, `OTG_MANUAL_FORCE_VSYNC_NEXT_LINE`, and `OTG_VERT_SYNC_CONTROL`. These fields expose master enable state, disable/start points, field-number behavior, blanking state/data enable, pipe abort/done, interlace current/next fields, field indication, live vblank/hblank/active/sync state, frame and counter readback, horizontal count options, frame-count reset, and forced-vsync-next-line status/clear/mode.

The stereo and snapshot families include `OTG_STEREO_FORCE_NEXT_EYE`, `OTG_AVSYNC_COUNTER`, `OTG_STEREO_STATUS`, `OTG_STEREO_CONTROL`, `OTG_SNAPSHOT_STATUS`, `OTG_SNAPSHOT_CONTROL`, `OTG_SNAPSHOT_POSITION`, and `OTG_SNAPSHOT_FRAME`. They describe stereo eye forcing, AV sync frame/line counters, active stereo eye/sync/3D state, stereo output line and polarity controls, snapshot trigger selection, snapshot position, and snapshot frame counters.

The interrupt/update families include `OTG_INTERRUPT_CONTROL`, `OTG_UPDATE_LOCK`, `OTG_DOUBLE_BUFFER_CONTROL`, `OTG_VERTICAL_INTERRUPT0_*`, `OTG_VERTICAL_INTERRUPT1_*`, `OTG_VERTICAL_INTERRUPT2_*`, `OTG_GLOBAL_SYNC_STATUS`, `OTG_MASTER_UPDATE_LOCK`, `OTG_MASTER_UPDATE_MODE`, `OTG_GSL_CONTROL`, `OTG_GSL_VSYNC_GAP`, `OTG_GSL_WINDOW_X`, `OTG_GSL_WINDOW_Y`, `OTG_VUPDATE_KEEPOUT`, and `OTG_RANGE_TIMING_INT_STATUS`. These masks cover interrupt enables/types/status/clear bits, vertical interrupt line ranges, update-lock and pending status, double-buffer update modes, vstartup/vupdate/vready and no-lock events, global swap lock enables and lock/unlock controls, GSL windowing, keepout windows, and range timing interrupt occurrence/clear/status.

The color/test/CRC families include `OTG_TEST_PATTERN_CONTROL`, `OTG_TEST_PATTERN_PARAMETERS`, `OTG_TEST_PATTERN_COLOR`, `OTG_BLANK_DATA_COLOR`, `OTG_BLANK_DATA_COLOR_EXT`, `OTG_BLACK_COLOR`, `OTG_BLACK_COLOR_EXT`, `OTG_PIXEL_DATA_READBACK0`, `OTG_PIXEL_DATA_READBACK1`, `OTG_CRC_CNTL`, `OTG_CRC0_WINDOWA_*`, `OTG_CRC0_WINDOWB_*`, `OTG_CRC0_DATA_*`, `OTG_CRC1_*`, `OTG_CRC2_DATA_*`, `OTG_CRC3_DATA_*`, `OTG_CRC_SIG_RED_GREEN_MASK`, and `OTG_CRC_SIG_BLUE_CONTROL_MASK`. These fields configure internal test patterns, blank/black color components and extension bits, pixel readback, CRC enable/selection/windowing/masking, and CRC result readback.

`OTG_STATIC_SCREEN_CONTROL`, `OTG_3D_STRUCTURE_CONTROL`, `OTG_GLOBAL_CONTROL0` through `OTG_GLOBAL_CONTROL3`, `OTG_TRIG_MANUAL_CONTROL`, `OTG_MANUAL_FLOW_CONTROL`, `OTG_DRR_CONTROL`, `OTG_REQUEST_CONTROL`, and `OTG_SPARE_REGISTER` expose display-state edge controls: static-screen detection thresholds and frame counters, 3D structure enable/state selection, global update/swap-lock and flow-control buses, manual trigger/flow outputs, dynamic refresh-rate averaging/last-used totals, immediate/request-controlled updates, and spare bits.

## Control Flow

This chunk has no runtime control flow. It is preprocessor data consumed by the DCN display driver.

A typical runtime path in the display driver is:

1. A DCN 1.0 component table selects an OPTC/OTG register address from `dcn_1_0_offset.h`, often through `SRI(OTG_..., OTG, inst)` style register-table macros.
2. The component code selects fields with `SF(OTG0_OTG_..., FIELD, mask_sh)` or equivalent generated field metadata.
3. Register helpers such as `REG_GET`, `REG_SET`, `REG_UPDATE`, or multi-field variants use the mask/shift values from this header to pack, clear, extract, or update fields.
4. Hardware performs the actual timing, interrupt, lock, snapshot, CRC, trigger, or double-buffer action according to DCN sequencing rules.

The control-sensitive actions represented by this chunk include programming scan timing, enabling and observing master timing state, locking updates across double-buffered registers, forcing counts or vsyncs, generating vertical interrupts, setting vstartup/vupdate/vready windows, controlling global swap lock, configuring GSL timing, enabling dynamic refresh behavior, selecting test patterns, capturing CRCs, and reading live counters. The macros do not encode ordering, read-only/write-one-to-clear semantics, valid value ranges, or synchronization requirements.

## State And Persistence Behavior

The header stores no software state. It describes state held in DCN timing-generator registers.

The represented hardware state includes:

- Latched timing-programming state, such as totals, blanking windows, sync windows, vstartup/vupdate/vready lines, test-pattern parameters, blank/black colors, stereo output settings, GSL windows, and global control buses.
- Live status and counters, such as blank/active/sync flags, current stereo eye, interlace field status, status positions, frame counts, VF/HV counts, snapshot position/frame, pixel readback, AV sync counter, trigger input/polarity/occurrence, pipe abort done, and current master enable or blank state.
- Sticky or explicitly cleared event state, such as vertical interrupt status, snapshot occurred, force-count-now occurred, force-vsync-next-line occurred, vstartup/vupdate/vready events, no-lock events, range timing events, and CRC done/overflow-like status fields.
- Double-buffer and lock state, including update-lock bits, update-pending bits, global update lock behavior, master update lock, and update request modes.
- Diagnostic state, including CRC window selections and masks, CRC result registers, static-screen counters/events, and spare/debug-style fields.

Persistence is hardware-defined. Values may survive within an enabled display engine until modeset, power-gating, suspend/resume, ASIC reset, or driver reprogramming. Some bits are live read-only status, some are writable programming fields, some are sticky clear-on-write fields, and some may self-clear after a trigger. This generated header does not distinguish those classes.

## Dependencies And Integration Points

This chunk depends on the generated DCN 1.0 register-header set. `dcn_1_0_sh_mask.h` supplies bit layouts; `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_1_0_offset.h` supplies the matching register addresses.

Direct local include points for the DCN 1.0 offset and mask headers include:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/irq/dcn10/irq_service_dcn10.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/resource/dcn10/dcn10_resource.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/gpio/dcn10/hw_factory_dcn10.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/gpio/dcn10/hw_translate_dcn10.c`

The OTG field names also integrate with the OPTC implementation under `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/optc/`, especially the DCN timing-generator register and mask structures defined around `dcn10_optc.h`. Later DCN generations reuse many of the same logical field names, so the correctness of this generated DCN 1.0 mask header matters to common helper code that is parameterized by per-generation register tables.

Although the repository path is under a local `ceph-client` source tree, this file is AMDGPU display-controller hardware metadata. It has no Ceph protocol, filesystem, or distributed-storage behavior.

## Risks And Edge Cases

The primary risk is silent hardware misprogramming. A wrong shift or mask can compile and still update the wrong bits, fail to update intended bits, or corrupt adjacent fields during read/modify/write operations.

High-risk fields in this chunk include timing totals and blank/sync windows, vertical total min/max/mid/control fields used for variable refresh and dynamic refresh behavior, update-lock and double-buffer pending fields, master enable and pipe abort fields, global sync and GSL lock fields, vertical interrupt enables/status/clear bits, vstartup/vupdate/vready events, trigger source and clear bits, and CRC/test-pattern fields. Errors here can produce blank displays, flicker, wrong refresh timing, missed interrupts, stuck update locks, failed multi-pipe synchronization, bad VRR/DRR behavior, incorrect CRC diagnostics, or modeset hangs.

Repeated instance layouts create copy-generation risk. `OTG2` and `OTG3` are complete, nearly identical register-mask sequences; `OTG1` and `OTG4` are partial because of chunk boundaries. An instance suffix mismatch or one-off mask difference could affect only a specific timing generator and might not appear on systems using fewer pipes.

Several masks describe status, event-clear, or trigger fields, but the header does not indicate access type. Consumers must know which fields are read-only, write-one-to-clear, self-clearing, or latch-on-update from hardware documentation and DCN sequencing code. Treating status bits like writable state, or clearing an event while enabling an interrupt, can lose display timing events.

This chunk starts immediately after earlier `OTG1` status/readback definitions and ends in the middle of the `OTG4_STEREO_CONTROL` block boundary transition to later `OTG4` snapshot/interrupt definitions. The final merged per-file research should treat those as chunk boundaries, not as missing register definitions.

## Test Signals

Useful validation signals are compile-time generated-header checks plus display hardware behavior:

- Kernel or AMDGPU display builds should compile all DCN 1.0 IRQ, resource, GPIO, and OPTC users of the generated `OTG*_...` field names.
- Register-generation validation should compare every `*_MASK` and `*__SHIFT` pair in this chunk against AMD's source register database and the corresponding `dcn_1_0_offset.h` addresses.
- Modeset tests should exercise multiple DCN timing generators, especially OTG2 and OTG3, to catch instance-specific copy errors.
- Display timing tests should verify horizontal/vertical totals, blanking, sync polarity, interlace, frame counters, and live status transitions across common modes.
- VRR/DRR and vtotal-min/max tests should observe stable `OTG_DRR_CONTROL` and vertical total behavior without flicker or invalid refresh jumps.
- IRQ tests should validate vstartup, vupdate, vready, vertical interrupt, snapshot, force-count-now, force-vsync, GSL-vsync-gap, and range-timing interrupt enable/status/clear behavior.
- Multi-pipe and synchronized update tests should exercise update locks, double-buffer pending state, master update lock, global swap lock, GSL windows, and global control fields.
- CRC and test-pattern tests should verify CRC window selection, masks, result registers, static-screen detection, blank/black color programming, and test-pattern output.
- Suspend/resume, hotplug, runtime power-management, and repeated modeset stress should not leave update locks stuck, timing generators disabled unexpectedly, or event status bits uncleared.

Regression symptoms from bad constants include blank or unstable displays, wrong refresh rate, tearing during atomic updates, missed vblank/vupdate interrupts, VRR failures, display CRC mismatches, test-pattern errors, stuck global sync, pipe abort timeouts, stereo/interlace field errors, and problems isolated to one OTG instance.

## Cross-Chunk Notes

Earlier chunks define the beginning of the DCN 1.0 header and the preceding OTG0/OTG1 timing-generator fields. This chunk begins at the tail of `OTG1` and contains complete `OTG2` and `OTG3` runs. The next chunk continues from `OTG4_OTG_STEREO_CONTROL` into the rest of `OTG4` and later register families. The final per-file merge should describe the whole header as a generated hardware register layout contract, not as algorithmic code.
