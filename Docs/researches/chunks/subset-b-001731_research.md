# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_0_1_sh_mask.h lines 22461-24958

## Scope And Purpose

This chunk is a generated AMD DCN 3.0.1 register shift/mask table. It exports C preprocessor constants for bit positions (`__SHIFT`) and bit masks (`_MASK`) used by AMD display register helpers when accessing memory-mapped display controller registers. The matching `dcn_3_0_1_offset.h` header supplies register addresses; this file supplies field layout.

The requested range starts in the tail of the `dce_dc_opp_dpg3_dispdec` block, covers the OPP buffer/pipe CRC/top-control registers for OPP instance 3, covers DSC forward routing registers for `DSCRM0` through `DSCRM2`, covers the `DC_PERFMON14` performance monitor block, covers all four `ODM0` through `ODM3` OPTC input blocks, covers full OTG timing-generator layouts for `OTG0` and `OTG1`, and ends inside the beginning of the `OTG2` timing-generator block at `OTG2_OTG_INTERRUPT_CONTROL`.

There are no functions, structs, or runtime branches in this chunk. Its purpose is to keep generated field metadata available to macro-based driver code such as `REG_SET`, `REG_UPDATE`, `REG_GET`, `REG_WAIT`, `SRI`, `SF`, `FD_MASK`, and `FD_SHIFT`.

## Register Blocks Covered

The range begins with the final fields of `DPG3`, including test-pattern colors, segment offset/width, and `DPG_DOUBLE_BUFFER_PENDING` status. The preceding chunk owns most of the `DPG3` block.

`dce_dc_opp_oppbuf3_dispdec` contributes OPP buffer control fields for active width, display segmentation, overlap pixels, pixel repetition, double-buffer pending state, 3D active-space dummy data, and padded segment pixels.

`dce_dc_opp_opp_pipe3_dispdec` contributes `OPP_PIPE3_OPP_PIPE_CONTROL`, with clock enable/on status and digital bypass enable. `dce_dc_opp_opp_pipe_crc3_dispdec` contributes OPP pipe CRC enable/control, CRC mask, and A/R/G/B/C result fields. `dce_dc_opp_opp_top_dispdec` contributes top-level OPP clock gating/test clock status and ABM backlight PWM selection.

`DSCRM0`, `DSCRM1`, and `DSCRM2` each expose the same `DSCRM_DSC_FORWARD_CONFIG` field layout: forward enable, OPP pipe source, double-buffer update pending, and forward-enable status.

`DC_PERFMON14` defines fields for event selection, counter control, counted value type, counter state selection, perfmon state, count-off interrupt state/acknowledge, counter interrupt status/acknowledge, captured value high/low words, and read-select fields.

`ODM0` through `ODM3` each define OPTC input control fields for soft reset, underflow interrupt/status/clear, current underflow state, double-buffer pending, input and output segment counts, per-segment source select, data format, DSC mode, DSC bytes per pixel, segment and DSC slice widths, input clock gate/enable/on status, memory selection, and spare register storage.

`OTG0` and `OTG1` are fully represented. Each has 716 `#define` entries covering scanout timing, sync and blanking, variable refresh, trigger controls, flow control, stereo/interlace, status counters, snapshots, interrupts, update locks, blank colors, vertical interrupts, CRC windows/results, global sync lock, update-window programming, DRR controls, DTO constants, request controls, DSC start position, pipe update status, and spare registers.

`OTG2` begins in this chunk and is covered from `OTG2_OTG_H_TOTAL` through `OTG2_OTG_INTERRUPT_CONTROL`. Later `OTG2` update-lock, double-buffer, master, CRC/global-control, DRR, DTO, DSC, pipe-status, and spare fields continue in the next chunk.

## Important APIs, Types, And Macros

The exported API is the generated macro naming contract:

- `<register>__<field>__SHIFT` gives the field's low bit position.
- `<register>__<field>_MASK` gives the field's masked bit range in a 32-bit register value.
- Instance prefixes in this chunk include `DPG3`, `OPPBUF3`, `OPP_PIPE3`, `OPP_PIPE_CRC3`, `OPP_TOP`, `DSCRM0` through `DSCRM2`, `DC_PERFMON14`, `ODM0` through `ODM3`, and `OTG0` through the first part of `OTG2`.
- Address-block comments identify hardware register blocks but are not compiled.

The main consumers are generated-style AMD display register lists. `display/dc/resource/dcn30/dcn30_resource.c` includes DCN 3.0 register-list structures and populates `optc_regs`, `optc_shift`, `optc_mask`, `dsc_shift`, and `dsc_mask` using macros that expand into the shift/mask symbols from this header. `display/dc/optc/dcn30/dcn30_optc.h` maps the OTG and ODM fields in this chunk through `OPTC_COMMON_REG_LIST_DCN3_0(inst)` and `OPTC_COMMON_MASK_SH_LIST_DCN30(mask_sh)`. `display/dmub/src/dmub_dcn301.c` directly includes `dcn_3_0_1_offset.h` and this header to populate DMUB register masks and shifts via `FD_MASK` and `FD_SHIFT`.

DSC routing is tied to `display/dc/dsc/dcn20/dcn20_dsc.h` and `display/dc/dsc/dcn20/dcn20_dsc.c`. That code uses `DSC_REG_LIST_DCN20(id)` and `DSC_REG_LIST_SH_MASK_DCN20(...)` for `DSCRM_DSC_FORWARD_CONFIG`, then runtime operations such as `dsc2_disconnect()` and `dsc2_wait_disconnect_pending_clear()` update `DSCRM_DSC_FORWARD_EN` and wait on `DSCRM_DSC_DOUBLE_BUFFER_REG_UPDATE_PENDING`.

## Functional Field Groups

OPP and DPG fields in this range configure late-pipe output behavior. DPG fields describe display-pattern generator colors, segment geometry, and double-buffer status. OPPBUF fields describe segmented output-buffer width, overlap, pixel repetition, 3D dummy data, and pending state. OPP pipe and pipe CRC fields expose clock/bypass control plus CRC enable modes, stereo/interlace CRC selection, one-shot pending state, CRC mask, and channel result readback.

DSCRM fields control whether a DSC stream is forwarded and which OPP pipe receives it. Their pending/status bits are synchronization points between DSC programming and OPP/OPTC routing.

`DC_PERFMON14` fields implement a display performance monitor endpoint. Counter control selects events, counted-value types, increment modes, hardware start/stop/count-off sources, restart and interrupt behavior, and readback selectors. The perfmon control fields expose monitor state, report count, count-off interrupt enable/status/ack, clock enable, run-enable start/stop selectors, counter interrupt status/ack fields, and high/low counter data.

ODM fields configure how OPTC input data is split, combined, formatted, clocked, and monitored. Source-select fields encode the number of input/output segments and the source for up to four segments. Width and bytes-per-pixel fields carry DSC-related layout, while input global control exposes underflow and double-buffer status used during ODM combine/bypass transitions.

OTG timing fields describe scanout geometry and timing. `OTG_H_TOTAL`, `OTG_H_BLANK_START_END`, `OTG_H_SYNC_A`, `OTG_H_SYNC_A_CNTL`, `OTG_H_TIMING_CNTL`, `OTG_V_TOTAL`, `OTG_V_TOTAL_MIN/MAX/MID`, `OTG_V_BLANK_START_END`, `OTG_V_SYNC_A`, and `OTG_V_SYNC_A_CNTL` hold horizontal/vertical totals, blanking windows, sync windows, polarity, mode, and divider behavior.

OTG event, trigger, and flow-control fields include vtotal and nominal-vsync interrupt status, `OTG_TRIGA/B_CNTL`, manual trigger registers, force-count-now controls, and flow-control source/polarity/granularity fields. These allow hardware-triggered timing events, manual trigger injection, delayed edge detection, and scanout-aligned control points.

OTG state and scanout readback fields include master enable, stereo force/control/status, interlace control/status, pixel data readback, vblank/hblank/active/sync status, horizontal and vertical counters, frame/VF/HV counters, count reset, vertical-sync force controls, and snapshot status/control/position/frame registers.

OTG update, global sync, DRR, CRC, and diagnostic fields include update locks, double-buffer pending bits, master update mode/lock, global sync status, GSL control/window fields, vupdate keepout, global control windows, manual flow control, DRR timing status/reach/change/trigger/control, DTO phase/modulo constants, DSC start position, pipe update status, vertical interrupt slots, CRC control, CRC windows, CRC data results, and CRC signature masks.

## Control Flow And State Behavior

This header has no direct control flow. The effective control flow is compile-time macro expansion: a resource file selects a DCN generation, instantiates per-block register tables with `SRI(...)`, and initializes shift/mask tables with `SF(...)`. Runtime code then passes logical register and field names to register helpers, which use these constants to pack or extract values.

The hardware state represented here is persistent memory-mapped register state. Configuration fields such as timing totals, ODM source selection, DSC forwarding, blank colors, CRC windows, DRR trigger windows, GSL windows, DTO constants, and update-lock settings remain active until driver writes, hardware reset, power transitions, or firmware actions change them.

Many status fields are live hardware state rather than stored configuration: clock-on bits, underflow current/status, CRC results, frame and scanout counters, blank/sync status, input trigger status, pending update bits, current stereo/interlace state, and perfmon active/counter status. Fields named `*_CLEAR`, `*_ACK`, `*_EVENT_CLEAR`, or interrupt acknowledge fields imply write-to-clear or acknowledge-style semantics in the hardware programming model.

Several register groups are frame-phase sensitive. OTG timing, vertical interrupts, vstartup/vupdate/vready, global update lock, GSL windows, vupdate keepout, DRR trigger windows, and double-buffer pending state must be programmed relative to scanout boundaries. DSCRM disconnect waits and ODM underflow/double-buffer state are also synchronization points when reconfiguring DSC/ODM paths.

## Dependencies And Integration Points

This file depends on the DCN 3.0.1 hardware register database and must stay aligned with `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_0_1_offset.h`. Register names in this shift/mask file must match address macros in the offset file and generated register-list entries in display core code.

Important integration points include:

- `display/dmub/src/dmub_dcn301.c`, which includes this header directly for DMUB register field masks/shifts.
- `display/dc/resource/dcn30/dcn30_resource.c`, whose `optc_regs[]`, `optc_shift`, `optc_mask`, `dsc_shift`, and `dsc_mask` tables rely on the OTG, ODM, and DSCRM field definitions.
- `display/dc/optc/dcn30/dcn30_optc.h`, which declares DCN 3.0 OPTC register and mask lists for OTG/ODM timing, CRC, DRR, GSL, DSC start-position, pipe-update-status, and ODM programming.
- `display/dc/dsc/dcn20/dcn20_dsc.*`, which uses `DSCRM_DSC_FORWARD_CONFIG` fields to connect, disconnect, and wait for DSC forwarding state.
- IRQ and diagnostics paths that consume OTG status, interrupt, CRC, frame counter, and global sync fields through common register helpers rather than spelling every generated macro directly.

## Risks And Edge Cases

The primary risk is drift between this generated mask header, the companion offset header, and the hardware register specification. A wrong mask or shift silently packs values into the wrong bits, which can produce display timing corruption, missed interrupts, invalid CRC capture, incorrect DSC routing, ODM underflow handling failures, or stuck update locks.

Instance replication is high risk. `ODM0` through `ODM3` and `OTG0` through `OTG2` use repeated layouts, but this chunk only contains full layouts for `OTG0` and `OTG1`; `OTG2` is split across chunk boundaries. Review or merge tooling should not infer that the `OTG2` block is complete from this document alone.

Interrupt/status fields are densely packed next to clear and ack bits. Confusing `*_INT_STATUS` with `*_INT_ACK`, `*_CLEAR`, or `*_MSK` can either fail to acknowledge an interrupt or clear an event unexpectedly. This applies to OPP pipe CRC one-shot state, perfmon counter interrupts, ODM underflow status/clear, OTG vertical interrupts, snapshot/trigger interrupts, vtotal/nominal-vsync events, DRR timing events, and global sync events.

Timing fields are width-limited and often packed as low/high halves. Mode-derived horizontal and vertical totals, blanking intervals, sync windows, CRC windows, GSL windows, DRR windows, and DSC/ODM widths must be clamped before packing. Overwide values are truncated by masks and can move timing points to unintended coordinates.

Double-buffer and update-lock fields can create frame-dependent failures. Incorrect sequencing around `OPTC_DOUBLE_BUFFER_PENDING`, `OTG_UPDATE_PENDING`, `OTG_DRR_TIMING_DBUF_UPDATE_PENDING`, `DSCRM_DSC_DOUBLE_BUFFER_REG_UPDATE_PENDING`, global update locks, and vupdate keepout can make updates apply on the wrong frame or appear stuck.

## Test Signals

Build-time failures involving missing `*_SHIFT` or `*_MASK` symbols in `SF`, `SRI`, `FD_MASK`, `FD_SHIFT`, `REG_FIELD`, `REG_GET`, `REG_SET`, `REG_UPDATE`, or `REG_WAIT` expansions are strong signals that this generated metadata no longer matches its consumers.

Runtime validation should include DCN 3.0.1 hardware modesets on OTG instances 0, 1, and 2, including standard timing changes, vblank/vupdate interrupt delivery, frame counter advancement, CRC readback, and no stuck pipe-update or double-buffer pending state.

ODM and DSC coverage should exercise bypass and combine configurations, DSC forwarding connect/disconnect, high-bandwidth modes requiring ODM segmentation, and underflow clear/status handling. Useful signals are correct segment source selection, expected DSC slice/bytes-per-pixel programming, no unexpected ODM underflow interrupts, and `DSCRM_DSC_DOUBLE_BUFFER_REG_UPDATE_PENDING` clearing after disconnect.

DRR and synchronization coverage should exercise variable refresh, DRR trigger windows, vtotal min/max/mid changes, GSL participation, global update locks, and vupdate keepout. Perfmon coverage should verify event selection, counter start/stop, interrupt/ack behavior, and high/low readback consistency.

Because this chunk is generated register metadata rather than algorithmic code, the strongest regression tests are hardware-register-database diffs, successful AMDGPU display builds, and targeted modeset/CRC/ODM/DSC/DRR smoke tests on DCN 3.0.1-class hardware.
