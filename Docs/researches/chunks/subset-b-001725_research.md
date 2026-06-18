# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_0_1_sh_mask.h lines 7224-9864

## Scope And Purpose

This chunk is a generated AMD DCN 3.0.1 register shift/mask table. It contains C preprocessor constants that describe bit positions (`__SHIFT`) and bit masks (`_MASK`) for display-engine, audio, memory-hub, VM, HUBP, cursor, and performance-monitor registers. It does not define executable functions, structs, or runtime branches; its value is the compile-time register-field contract consumed by AMD display driver register helpers.

The requested range starts in the tail of the `DC_PERFMON4` block, covers the Azalia/HDA controller and codec-index windows, the main `DCHUBBUB` fabric and VM-request blocks, the `DC_PERFMON5` block, 16 DCN VM contexts, the first HUBP pipe's `HUBP0`/`HUBPREQ0`/`HUBPRET0` register fields, the first cursor block, and ends inside the `DC_PERFMON6` block. The companion offset header (`dcn_3_0_1_offset.h`) supplies register addresses; this file supplies how callers pack and extract the fields inside those 32-bit MMIO registers.

Within lines 7224-9864 there are 2,057 `#define` entries. The dominant prefixes are `DCHUBBUB`, `HUBPREQ0`, `DCN_VM_CONTEXT*`, `DC_PERFMON*`, `AZALIA`, `HUBP0`, `HUBPRET0`, and `CURSOR0_0`. The source is hardware-register metadata, so the practical research surface is the register grouping and the driver integration points that consume the generated names.

## Important APIs, Types, And Macros

The exported API is the naming convention:

- `<register>__<field>__SHIFT` gives the field's bit offset.
- `<register>__<field>_MASK` gives the already-shifted mask for that field.
- Address-block comments such as `// addressBlock: dce_dc_dcbubp0_dispdec_hubpreq_dispdec` identify replicated hardware blocks.
- Register comments such as `//HUBPREQ0_DCSURF_FLIP_CONTROL` delimit groups but are not consumed by C code.

These constants are used by AMD display macros such as `SF`, `HUBP_SF`, `HWS_SF`, `DMUB_SF`, `REG_SET`, `REG_UPDATE`, `REG_GET`, and `REG_READ`. For example, `display/dc/hubp/dcn10/dcn10_hubp.h` builds `HUBP_MASK_SH_LIST_*` entries from names such as `HUBP0_DCSURF_ADDR_CONFIG__NUM_PIPES_MASK`, `HUBPREQ0_DCSURF_FLIP_CONTROL__SURFACE_FLIP_PENDING_MASK`, and `HUBPRET0_HUBPRET_READ_LINE_STATUS__PIPE_READ_VBLANK_MASK`. `display/dc/dce/dce_audio.h` consumes the Azalia endpoint index/data field names, while `display/dc/dcn20/dcn20_vmid.h` consumes the `DCN_VM_CONTEXT0_*` field names as the canonical mask/shift shape for all VM context instances.

`display/dmub/src/dmub_dcn301.c` directly includes `dcn_3_0_1_offset.h` and this `dcn_3_0_1_sh_mask.h`, then materializes DMUB field masks and shifts through `FD_MASK` and `FD_SHIFT`. This makes the chunk relevant not only to kernel display core code but also to the display microcontroller service register abstraction for DCN 3.0.1.

## Register Blocks Covered

`DC_PERFMON4` is a partial tail at the start of the chunk. It includes fields for performance-monitor state, report count, count-off interrupt control/status/acknowledge, clock enable, run-enable start/stop selection, per-counter interrupt status and acknowledge bits, high/low counter value readback, and counter read selection.

`AZF0ENDPOINT0` through `AZF0ENDPOINT7` each expose an indexed Azalia codec endpoint register pair: `AZALIA_F0_CODEC_ENDPOINT_INDEX` selects a codec endpoint register index and `AZALIA_F0_CODEC_ENDPOINT_DATA` carries the data. Each instance has the same `AZALIA_ENDPOINT_REG_INDEX` and `AZALIA_ENDPOINT_REG_DATA` fields.

`AZALIA_CONTROLLER`, root, stream, and input endpoint blocks cover the display audio controller. The controller section includes clock gating, audio DTO phase/module, SOC clock/deep-sleep exit controls, DMA non-snoop and isochronous policy for data/BDL/RIRB/CORB paths, cyclic-buffer position/sync, global and stream payload capabilities, input/output stream arbiter controls, CRC controls/results, and memory power control/status. The root section exposes vendor/device/revision IDs, channel count, resync FIFO control, function parameter capabilities, power/reset controls, subsystem response fields, converter synchronization, audio port connectivity, GTC offsets, and registerized port connectivity. Stream windows `AZF0STREAM8` through `AZF0STREAM15` provide indexed stream register access; input endpoints `AZF0INPUTENDPOINT0` through `AZF0INPUTENDPOINT7` mirror the index/data access model for codec input endpoint registers.

`DCHUBBUB_SDPIF`, `DCHUBBUB_RET_PATH`, and main `DCHUBBUB` blocks describe the display hub fabric. The SDPIF and VM-address fields include physical request selection, forced IO status, framebuffer location, AGP bounds/base, local HBM address bounds and lock control, SDPIF memory power state, and SDPIF configuration. The return path section defines DCC configuration for surfaces 0 through 7, return-path memory power control/status, and CRC capture controls/results. The main hubbub section covers outstanding request limits, saturation/QoS force, DRAM state control, A/B/C/D watermarks for urgency, memory-trip, self-refresh enter/exit, DRAM clock-change behavior, watermark change control, timeout enable/detection/interrupt status, global timer control, surface-check addresses, VTG controls, soft reset, clock control, DCFCLK control, performance measurement, status, debug-index/data, fractional urgent bandwidth, host-VM controls, and FMON controls.

`DC_PERFMON5` is the DCHUBBUB perfmon instance. It has the standard DC perfmon shape: event select, counted-value select/type, increment and hardware-control mode, run-enable mode, count-off selection and start-disable, restart, interrupt enable/status/acknowledge, active status, per-counter state selection for counters 0 through 7, global monitor state/report count, clock enable, run-enable start/stop selectors, and low/high counter value readback.

`DCN_VM_CONTEXT0` through `DCN_VM_CONTEXT15` provide per-VMID display VM programming. Each context has page-table depth/block-size control, page-table base address high/low, logical start address high/low, and logical end address high/low. The chunk also includes default fault address high/low, VM fault control, fault status with context/client/read/write/walker/fault-type fields, and fault address high/low.

`HUBP0` covers the first hub pipe's surface format and request-size programming. It includes surface pixel format/alpha/rotation/h-mirror and DCC/tiling metadata, address configuration (`NUM_PIPES`, `NUM_BANKS`, `PIPE_INTERLEAVE`, `NUM_SE`, `NUM_RB_PER_SE`, `MAX_COMPRESSED_FRAGS`), tiling configuration (`SW_MODE`, `META_LINEAR`, `PIPE_ALIGNED`), primary/secondary viewport start/dimension for luma and chroma, request-size configuration for data/meta/DPTE chunks and swath heights, HUBP control/status bits such as blank enable, TTU disable, underflow status/clear, no-outstanding-requests, VTG select, disable, and in-blank, plus HUBP clock and measurement controls.

`HUBPREQ0` defines the first pipe's memory-request programming surface. It contains pitch and meta pitch for luma/chroma; VMID selection; primary/secondary data and metadata surface addresses for luma/chroma; TMZ and DCC enable/metadata fields in surface control; flip-control bits for flip type, stereo sync, pending state, update lock, earliest-in-use tracking, and flip interrupt status/clear/mask; expansion modes for DRQ/PRQ/MRQ/CRQ; TTU QoS watermarks and global/surface/cursor TTU controls; DMDATA VM control; VM aperture and L1 TLB controls; blank offsets; destination/scaler dimensions; prefetch, vblank, flip, nominal, and per-line delivery parameters; cursor delivery settings; reference-to-pixel frequency ratio; destination Y delta request limit; and HUBPREQ memory power state.

`HUBPRET0` describes the return/read side of the first hub pipe. It includes DET buffer base addresses, crossbar source selection for color components, stereo and first-line pairing fields, memory power control/status, read-line control/line registers, interrupt status/clear/mask/type fields for read line and read line compare events, and read-line value/status flags that distinguish vblank/inside/outside state for two programmable read lines.

`CURSOR0_0` describes cursor plane 0 for pipe 0. It includes cursor enable, magnification, mode, TMZ, pitch, rotation/mirroring bypass, lines per chunk, perfmon latency measurement controls, surface address high/low, size, position, hot spot, stereo offsets, destination X offset, cursor memory power control/status, and DMDATA address/control/QoS/status/software data fields. The DMDATA fields program auxiliary display metadata delivery, including update/repeat/mode/size, QoS level/deadline delta, done/underflow/clear status, and software-supplied data.

`DC_PERFMON6` begins at the end of the chunk. The requested range includes its counter control, counter-control2, per-counter state register, and the start of global perfmon control. The later `DC_PERFMON6` value and auxiliary registers continue after line 9864 and are owned by the next chunk.

## Control Flow And State Behavior

There is no direct control flow in this header. The effective flow is compile-time expansion: a driver-specific register list chooses an instance and register name, the offset header resolves its MMIO address, and this mask header resolves the fields used by helper macros to read, update, or write the register. At runtime the display driver writes memory-mapped registers in hardware-defined sequences for modesets, flips, cursor updates, audio setup, VM context setup, power management, and diagnostics.

The state described here persists in hardware registers until changed by the driver, DMUB firmware, reset logic, power-management logic, or the hardware block itself. Configuration state includes audio DTO values, DMA coherency/isochronous policy, hubbub watermarks, VM page-table bounds, surface addresses, tiling metadata, viewport geometry, TTU/prefetch parameters, cursor addresses, and memory-power force/disables. Live status includes flip pending/in-use addresses, underflow flags, no-outstanding-request state, memory power states, timeout status, fault status, read-line status, counter activity, CRC results, and perfmon values.

Some fields use event or acknowledge semantics rather than plain storage. Names containing `*_STATUS`, `*_INT_STATUS`, `*_INT_ACK`, `*_CLEAR`, `*_UNDERFLOW_CLEAR`, `*_FAULT_CLEAR`, and `*_EVENT_CLEAR` indicate fields that can be set by hardware and cleared or acknowledged by software. Confusing a status mask with a clear/ack mask can alter interrupt behavior or hide the evidence needed for diagnosing display faults.

Several groups are timing-sensitive. HUBPREQ prefetch, vblank, flip, nominal, TTU, and per-line-delivery registers are programmed relative to scanout timing and watermarks. HUBPRET read-line interrupts are line-position based. Cursor position/hotspot and DMDATA delivery must align with active planes and VM configuration. Audio DTO and cyclic-buffer fields affect stream rate and buffer-position reporting. VM fault and aperture state must be established before display memory requests are allowed to consume GPU virtual addresses.

## Dependencies And Integration Points

The chunk depends on the generated DCN 3.0.1 register database. It must stay aligned with `dcn_3_0_1_offset.h`; a mask with a stale offset can write a correct field layout into the wrong register, and a correct offset with a stale mask can corrupt neighboring fields. It also depends on the local display register-helper macros that concatenate register and field names exactly as generated here.

Audio integration is through `display/dc/dce/dce_audio.h` and `display/dc/dce/dce_audio.c`. The audio code uses `SRI(AZALIA_F0_CODEC_ENDPOINT_INDEX, AZF0ENDPOINT, id)` and the corresponding `AZALIA_ENDPOINT_REG_INDEX`/`AZALIA_ENDPOINT_REG_DATA` masks to implement indirect codec register access. Higher-level audio functions use the indexed Azalia register path for HBR, lipsync, hot-plug control, speaker/channel descriptors, sink info, power states, and stream format capability programming.

HUBP integration is through the hub pipe register lists in `display/dc/hubp/dcn10/dcn10_hubp.h` and later ASIC-specific variants. The mask list maps many fields from this chunk into `struct dcn_hubp*` shift/mask tables. Runtime hubp code then programs surface format, tiling, pitch, addresses, flip control, viewport, request sizes, DCC/TMZ state, VM/TLB settings, TTU/deadline parameters, blanking, underflow handling, cursor, and read-line behavior.

DCHUBBUB integration is through resource initialization, including `display/dc/resource/dcn30/dcn30_resource.c`, which builds `hubbub_reg`, `hubbub_shift`, and `hubbub_mask` from `HUBBUB_REG_LIST_DCN30` and `HUBBUB_MASK_SH_LIST_DCN30`. This connects the chunk to bandwidth/watermark programming, self-refresh and DRAM clock-change gating, timeout detection, hubbub CRC/debug state, soft reset, clock control, host-VM controls, and fabric monitoring.

VM integration is through `display/dc/dcn20/dcn20_vmid.h`, which uses the `DCN_VM_CONTEXT0_*` masks and shifts as the field-template for all VM contexts. The context instances in this chunk provide the per-VMID page table base/start/end state used by display memory requests, while default/fault registers expose fault recovery and debugging information.

DMUB integration is explicit in `display/dmub/src/dmub_dcn301.c`, which includes this header and emits DMUB service field arrays via `FD_MASK` and `FD_SHIFT`. Cursor state is also mirrored in DMUB command structures (`display/dmub/inc/dmub_cmd.h`) with fields matching names such as `CURSOR0_0_CURSOR_SURFACE_ADDRESS`, `CURSOR0_0_CURSOR_SIZE__CURSOR_WIDTH`, and `HUBPREQ0_CURSOR_SETTINGS__CURSOR0_DST_Y_OFFSET`.

## Risks And Edge Cases

The main risk is generated metadata drift. A wrong shift or mask can silently pack values into the wrong bit positions, which is especially dangerous for MMIO because failures may appear as display corruption, underflow, missed interrupts, lost audio, VM faults, or power-management instability rather than as compile errors.

Partial-block ownership is important for reconciliation. This chunk starts after the beginning of `DC_PERFMON4` and ends before the completion of `DC_PERFMON6`; any final per-file report should describe those perfmon blocks as spanning neighboring chunks. In contrast, most Azalia endpoint/index windows, `DC_PERFMON5`, the VM context array, and the pipe-0 HUBP/HUBPREQ/HUBPRET/cursor fields are materially represented here.

Instance replication is another source of mistakes. Azalia endpoint and input endpoint blocks repeat 0 through 7, streams repeat 8 through 15, VM contexts repeat 0 through 15, and HUBP-style fields are normally repeated for multiple pipes even though this chunk covers pipe 0. A generation error in one instance can be missed if only instance 0 is exercised; a driver assuming all instances are identical can also be wrong when later chunks or ASIC variants add or remove fields.

Status and clear fields are adjacent in several registers. Examples include HUBP underflow status/clear, HUBPREQ flip interrupt status/clear, HUBPRET read-line interrupt status/clear/mask/type, perfmon interrupt status/ack, DMDATA underflow/clear, timeout interrupt status/ack, and VM fault status/control. Incorrect use can either leave interrupts storming or clear diagnostic state before it is captured.

Address and VM fields are width-sensitive. Surface addresses are split into low/high fields, VM context start/end fields are split into high/low logical page-number pieces, and aperture or local-memory bounds are represented in multiple registers. Callers must preserve alignment, high-bit placement, and context selection; truncation or stale high halves can redirect scanout requests to the wrong memory.

Timing and bandwidth fields are mode-dependent. Hubbub watermarks, TTU controls, prefetch/vblank/flip/nominal parameters, per-line delivery, and DRAM/self-refresh clock-change controls must match the active mode set, memory clock behavior, DCC use, cursor use, and multi-plane composition. Bad values can cause underflow only under specific refresh rates, plane formats, scaling ratios, or power states.

Audio fields combine indexed codec access with DMA and DTO state. Incorrect endpoint indices, stream index/data handling, DTO phase/module, non-snoop/isochronous policy, cyclic-buffer sync, or HDA memory-power controls can manifest as silent audio, drift, buffer-position errors, or codec enumeration problems.

## Test Signals

Build-time signals are missing-symbol or initializer errors in AMD display modules that consume generated masks and shifts. High-signal failures would mention `SF`, `HUBP_SF`, `HWS_SF`, `DMUB_SF`, `FD_MASK`, `FD_SHIFT`, `REG_FIELD`, or a missing `*_MASK`/`__SHIFT` identifier from this chunk.

Runtime display validation should include modeset and page-flip tests on DCN 3.0.1-class hardware, with attention to HUBP0 scanout, DCC/TMZ surfaces, luma/chroma planes, scaling, viewport changes, cursor enable/move/resize, and flip interrupt delivery. Useful symptoms are absence of HUBP underflow, no stuck surface flip pending bit, correct in-use and earliest-in-use addresses, advancing frame/line state, and no unexpected timeout interrupts.

Memory/VM validation should exercise VMID setup across multiple contexts, GPU virtual-address scanout, fault injection or bad-address handling where available, and register dumps of fault context/client/read/write/walker fields. Correct behavior includes valid page-table bounds, no false VM faults during normal scanout, and clear fault status after expected recovery paths.

Bandwidth and power-management validation should cover memory clock changes, self-refresh entry/exit, low-power memory states, watermark set changes, and high-bandwidth multi-plane modes. Signals include stable display during pstate transitions, no DCHUBBUB timeout interrupt, expected memory power status, and no underflow when cursor/DMDATA and chroma planes are active.

Audio validation should cover HDMI/DP audio enumeration, supported sample rates and formats, HBR/lipsync/speaker allocation programming, stream start/stop, cyclic-buffer position reporting, and suspend/resume or display hotplug. Failures in the Azalia masks commonly show up as lost codec endpoint access, wrong stream descriptors, or unstable audio timing.

Perfmon and diagnostic validation should include reading `DC_PERFMON4/5/6` counters, checking counter interrupt/ack behavior, using DCHUBBUB CRC capture where supported, and verifying HUBPRET read-line interrupt/status behavior at programmed lines. Because these are generated register masks, the strongest regression signal is a combination of hardware register-database diffing, compile coverage for all generated field names, and smoke tests that touch the audio, hubbub, VM, HUBP, cursor, and perfmon paths represented by the chunk.
