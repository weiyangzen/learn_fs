# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_5_1_sh_mask.h lines 11022-13240

## Scope

This chunk is a generated AMD DCN 3.5.1 register shift/mask slice. It contains preprocessor constants only: each register field has a `__SHIFT` definition and a matching `_MASK` definition used to pack, update, and extract MMIO bit fields. There are no C functions, structs, enums, loops, branches, or driver-owned storage objects in this range.

The requested range begins in the tail of the `DC_PERFMON4_PERFCOUNTER_CNTL` field set and ends mid-register at `HUBP1_DCSURF_TILING_CONFIG__META_LINEAR_MASK`. The major covered surfaces are:

- Display performance monitor blocks `DC_PERFMON4`, `DC_PERFMON5`, and `DC_PERFMON6`.
- Azalia/HDA display-audio endpoint, stream, codec, CRC, DMA, DTO, clock-gating, memory-power, and connectivity fields.
- DCHUBBUB SDPIF, VM aperture, local memory, memory-power, CRC, DCC stats, compbuf/DET allocation, arbitration, watermark, timer, clock, performance measurement, timeout, debug, and fault-monitor fields.
- DCN VM context 0-15 page-table control and address fields, default address fields, and fault control/status/address fields.
- HUBP/HUBPREQ/HUBPRET/CURSOR instance 0 field definitions for surface format, tiling, viewport, addresses, flip, QoS/timing, memory power, read-line, interrupts, cursor, and DMDATA.
- The start of HUBP instance 1 surface configuration, address configuration, and tiling fields.

## Purpose

The header supplies the bit-position half of the DCN 3.5.1 hardware ABI. Companion offset headers identify which register to access; this file identifies which bits inside that register belong to each named field. AMD display code consumes these constants through field helper macros such as `FD_MASK`, `FD_SHIFT`, `SF`, `HWS_SF`, and block-specific mask/shift list macros, which then feed `REG_GET`, `REG_SET`, `REG_UPDATE`, IRQ table construction, DMUB register initialization, and hardware block register tables.

Because this is generated register metadata, the most important property is exact numeric correspondence with AMD's DCN 3.5.1 register specification and with the matching `dcn_3_5_1_offset.h` names. The file itself does not enforce access order or hardware side effects; it only defines symbolic bit encodings.

## Important Definitions

The exported interface is the macro namespace:

- `REGISTER__FIELD__SHIFT` gives the field's least-significant bit position.
- `REGISTER__FIELD_MASK` gives the field mask already shifted into register position.
- Repeated block prefixes such as `HUBP0`, `HUBPREQ0`, `HUBPRET0`, `CURSOR0_0`, and `DC_PERFMON6` identify the hardware instance whose fields are being described.

Important macro families in this range:

- `DC_PERFMON4_*`, `DC_PERFMON5_*`, and `DC_PERFMON6_*`: performance counter event selection, current-value source selection, increment mode, hardware start/stop/count-off selection, restart, interrupt enable/status/ack, active state, per-counter state, perfmon run-start/run-stop selection, high/low counter values, and high-half read selection.
- `AZF0ENDPOINT[0-7]_AZALIA_F0_CODEC_ENDPOINT_INDEX/DATA`: indirect endpoint register index and data windows for display-audio codec endpoints.
- `AZALIA_*`: controller clock gating, audio DTO phase/module and force controls, SOCCLK deep-sleep exit, underflow filler sample, data/BDL/CORB/RIRB/DP DMA snoop/isochronous settings, output stream arbiter, input/output CRC engines, memory-power control/status, function/root codec identity, power/reset/channel/resync controls, subsystem ID response, converter synchronization, and port connectivity override fields.
- `AZF0STREAM[8-15]_AZALIA_STREAM_INDEX/DATA` and `AZF0INPUTENDPOINT[0-7]_AZALIA_F0_CODEC_INPUT_ENDPOINT_INDEX/DATA`: indirect stream and input-endpoint index/data windows.
- `DCHUBBUB_*`: SDPIF configuration and error/status controls, forced-I/O status capture, framebuffer/AGP/local-HBM aperture fields, SDPIF and return-path memory power, hubbub CRC source/result fields, DCC statistics, compbuf/DET size and allocation status, memory-power modes/status, debug depths, outstanding-request and QoS controls, DRAM self-refresh/pstate/DCFCLK-deep-sleep controls, watermark sets A-D including Z8 variants, host-VM arbitration, watermark change requests, timeout controls/status/clear/mask, global timer, VTG controls, soft reset, clock controls, DCFCLK counter/readback, performance measurement, vline snapshot, control status, FMON controls, and test debug index/data.
- `DCN_VM_CONTEXT[0-15]_*`: page-table depth/block-size, page-directory base high/low, logical page start high/low, and logical page end high/low fields for 16 contexts.
- `DCN_VM_DEFAULT_ADDR_*` and `DCN_VM_FAULT_*`: default physical page number/VMID, fault replay/write/access/page-table-block/protection controls, fault status/clear/client/write/read/VMID fields, and fault address low/high fields.
- `HUBP0_*`: surface pixel format, rotation, mirror, alpha plane, address configuration, tiling configuration, primary/secondary viewport start/dimension for luma and chroma, request-size configuration, HUBP blank/reset/VTG/TTU/timeout/underflow controls, clock gates/status, VMPG size, and DCFCLK/DPPCLK measurement-window controls.
- `HUBPREQ0_*`: surface pitch, VMID, primary/secondary and luma/chroma surface addresses, meta-surface addresses, TMZ/DCC surface controls, flip controls and flip interrupts, in-use and earliest-in-use readbacks, expansion modes, TTU/QoS controls for surfaces and cursors, DMDATA VM fault/late/underflow status, system aperture and L1 TLB control, blank/destination/prefetch/vblank/flip/nominal/delivery timing parameters, cursor settings, reference-to-pixel clock conversion, DRQ limits, and HUBPREQ memory-power control/status.
- `HUBPRET0_*`: return-path control, memory-power control/status, read-line control/value/status fields, and return-path interrupt enable/status/clear/mask fields.
- `CURSOR0_0_*`: cursor enable/mode/format/2x magnify/pitch/lines-per-chunk fields, cursor image address, size, position, hot spot, stereo, destination offset, cursor memory power, DMDATA address/control/QoS/status/software controls.
- `HUBP1_DCSURF_SURFACE_CONFIG`, `HUBP1_DCSURF_ADDR_CONFIG`, and the start of `HUBP1_DCSURF_TILING_CONFIG`: partial pipe-1 surface format, address layout, and tiling metadata.

## Control Flow

There is no runtime control flow in the header. The effective flow is macro expansion in the consuming driver code:

1. DCN 3.5.1 display code includes `dcn_3_5_1_offset.h` and `dcn_3_5_1_sh_mask.h`.
2. Resource code expands block register-list macros and block mask/shift-list macros into C structs, for example HUBP and HUBBUB tables in `dcn351_resource.c`.
3. DMUB setup includes this exact header in `dmub_dcn351.c`; `dmub_srv_dcn351_regs_init()` calls `FD_MASK(reg, field)` and `FD_SHIFT(reg, field)` while expanding `DMUB_DCN35_FIELDS()`.
4. Runtime code uses the populated offsets, masks, and shifts to perform MMIO read/modify/write operations or to build IRQ register entries.
5. Hardware interprets the fields as state-machine controls, status bits, counter values, addresses, or timing parameters.

The header cannot express synchronization rules. Callers still need to serialize indirect index/data accesses, stage flip updates at the right vblank/vupdate boundary, poll or clear status bits according to hardware semantics, and avoid programming powered-down blocks.

## State and Persistence Behavior

The macros are compile-time constants and persist no data. The hardware registers they describe hold several kinds of state:

- Persistent configuration state: audio DTO, DMA snoop/isochronous behavior, codec power/reset/channel settings, port connectivity overrides, VM page-table context ranges, framebuffer/AGP/HBM apertures, HUBP format/tiling/viewport/request sizing, surface and metadata addresses, TMZ/DCC enablement, prefetch/vblank/flip/nominal/delivery timing, cursor image and DMDATA settings, clock-gating controls, and memory-power modes.
- Latched or double-buffered state: HUBPREQ surface update locks, flip pending state, master update lock status, in-use and earliest-in-use surface addresses, and timing fields that are consumed around frame boundaries.
- Volatile status and diagnostic state: Azalia CRC completion/results, memory-power status, SDPIF forced-I/O status, DCHUBBUB CRC values, DCC stats, compbuf/DET current sizes, watermark-change status, timeout status, VM fault status and fault address, HUBP timeout/underflow status, DMDATA fault/underflow/late/done status, read-line values/status, cursor memory-power state, and perfmon counter states/current values.
- Side-effect-sensitive fields: interrupt ack/clear bits, fault clears, timeout clears, underflow clears, perfmon ack bits, memory-power force/disable controls, soft resets, indirect stream/endpoint indexes, and debug index/data windows.

The repeated instance naming is part of the state isolation contract. `HUBP0`, `HUBPREQ0`, `HUBPRET0`, and `CURSOR0_0` describe pipe 0 fields; the final lines start pipe 1 and must be reconciled with the next chunk before drawing conclusions about all pipe-1 fields.

## Dependencies and Integration Points

Direct dependencies are preprocessor-level: this header is guarded by `_dcn_3_5_1_SH_MASK_HEADER` and is paired with the generated offset header for the same ASIC generation.

Important source-tree integration points include:

- `drivers/gpu/drm/amd/display/dmub/src/dmub_dcn351.c`, which includes `dcn/dcn_3_5_1_sh_mask.h` and initializes DMUB DCN 3.5 register masks and shifts with `FD_MASK` and `FD_SHIFT`.
- `drivers/gpu/drm/amd/display/dc/resource/dcn351/dcn351_resource.c`, which builds HUBP/HUBBUB/HWSEQ and other block shift/mask tables with macros such as `HUBP_MASK_SH_LIST_DCN35`, `HUBBUB_MASK_SH_LIST_DCN35`, and `HWSEQ_DCN35_MASK_SH_LIST`.
- `drivers/gpu/drm/amd/display/dc/irq/dcn351/irq_service_dcn351.c`, where IRQ entries macro-paste names such as `HUBPREQn_DCSURF_SURFACE_FLIP_INTERRUPT__SURFACE_FLIP_INT_MASK_MASK` and `__SURFACE_FLIP_CLEAR_MASK` into enable and ack tables.
- HUBP implementation code under `drivers/gpu/drm/amd/display/dc/hubp/dcn35/`, which programs fields such as `DCSURF_SURFACE_CONFIG`, surface addresses, flip controls, viewport/timing fields, cursor settings, and status readbacks through register helpers.
- DCN DML and resource code that computes watermarks, DET/compbuf allocation, VM timing, prefetch, vblank, flip, and delivery values that eventually land in the DCHUBBUB/HUBPREQ fields defined here.
- Display audio paths that use Azalia endpoint/stream/function fields for DP/HDMI audio setup, audio DTO control, audio memory power, CRC diagnostics, and codec power/reset behavior.

## Risks and Edge Cases

- Numeric drift is high impact. A wrong `_SHIFT` or `_MASK` can corrupt unrelated bits while all C code still compiles.
- This chunk starts and ends mid-block. `DC_PERFMON4_PERFCOUNTER_CNTL` lacks its earlier fields here, and `HUBP1_DCSURF_TILING_CONFIG` is incomplete at the end. Adjacent chunks are required for complete block-level documentation.
- Repeated register families are copy-sensitive. Azalia endpoint/input-endpoint/stream instances, DCN VM contexts 0-15, watermark sets A-D, and HUBP/HUBPREQ/HUBPRET/CURSOR instances can compile with an instance prefix mistake but affect only one pipe, stream, endpoint, or VM context at runtime.
- Indirect index/data windows require serialization. Azalia endpoint, input-endpoint, stream, and DCHUBBUB debug index/data fields can read or write the wrong target if callers interleave index and data operations.
- Address fields are split across low/high, primary/secondary, luma/chroma, and meta-surface variants. Partial updates can cause display fetches from mismatched addresses, wrong VMIDs, or stale compression metadata.
- Flip and timing fields are frame-boundary-sensitive. Bad values for update locks, flip pending delay, prefetch, vblank, nominal, delivery, and TTU/QoS fields can manifest as stale frames, page-flip timeout, underflow, or intermittent corruption.
- Clear/ack/status fields have hardware side effects. Misusing `SURFACE_FLIP_CLEAR`, `DCHUBBUB_TIMEOUT_INT_CLEAR`, `DMDATA_VM_FAULT_STATUS_CLEAR`, `DMDATA_UNDERFLOW_CLEAR`, perfmon interrupt ack bits, or HUBP underflow/timeout clears can lose diagnostics or leave interrupts stuck.
- Memory-power controls appear in Azalia, DCHUBBUB, HUBPREQ, HUBPRET, and cursor blocks. Writes while memory is disabled or before status settles can be dropped or produce transient readbacks.
- VM context and fault fields are global enough to affect multiple display fetch clients. Wrong page-table depth/block size, base/start/end addresses, default address, or fault control can break several planes rather than one immediate caller.

## Test Signals

Useful validation is mostly compile-time, generated-header consistency, and hardware/display behavior:

- Build AMDGPU/DC with DCN 3.5.1 support and DMUB enabled. Missing or renamed field macros should fail in `dmub_dcn351.c`, `dcn351_resource.c`, HUBP/HUBBUB/HWSEQ tables, IRQ service code, and shared register helpers.
- Run generated-header consistency checks that each covered `REGISTER__FIELD__SHIFT` has a matching `REGISTER__FIELD_MASK`, that masks align with shifts and field widths, and that repeated instances preserve intended layouts across endpoint, stream, VM context, perfmon, and pipe blocks.
- Diff this slice against AMD's authoritative DCN 3.5.1 register database and nearby DCN 3.5/3.6 generated headers where layouts are expected to match.
- Exercise DP/HDMI audio modes, including stream setup, endpoint/input-endpoint indirect access, audio DTO changes, codec power/reset, memory-power transitions, and Azalia CRC diagnostics.
- Run modeset and multi-plane tests through HUBP/HUBPREQ pipe 0 with varied pixel formats, alpha plane, rotation, mirror, tiling modes, DCC/TMZ, luma/chroma surfaces, primary/secondary surfaces, meta surfaces, and VMID-backed addresses.
- Stress page flips, triple buffering, GSL, flip interrupts, surface in-use/earliest-in-use readback, cursor movement, cursor image changes, stereo cursor behavior, and DMDATA delivery while checking for underflow, late/fault status, and missed flip completion.
- Validate DCHUBBUB arbitration and watermark behavior under high bandwidth, high resolution, multi-plane, compressed-surface, memory-pressure, self-refresh, pstate, Z8, and DCFCLK deep-sleep scenarios.
- Use perfmon and debug tooling to program and read `DC_PERFMON4`, `DC_PERFMON5`, `DC_PERFMON6`, DCHUBBUB performance measurement counters, FMON state, DCC stats, CRC results, and DCFCLK/DPPCLK measurement windows.
- Run suspend/resume, display hotplug, blank/unblank, audio suspend, and display power-gating tests to exercise memory-power state transitions and restore sequencing across Azalia, DCHUBBUB, HUBPREQ, HUBPRET, cursor, and perfmon blocks.
- Inject or observe VM/display-fetch faults where supported and verify `DCN_VM_FAULT_STATUS`, fault address fields, DMDATA VM fault fields, and valid page-table context programming.

## Chunk-Specific Summary

Lines 11022-13240 define DCN 3.5.1 bit-field metadata rather than executable code. The slice is centered on display audio, DCHUBBUB memory/VM/arbitration diagnostics, DCN VM context/fault registers, pipe-0 HUBP/HUBPREQ/HUBPRET/cursor programming, and perfmon diagnostics, with only the beginning of pipe-1 HUBP fields included. Correctness depends on exact generated masks/shifts, matching offset-header names, instance-correct macro use, serialized indirect access, and hardware validation across audio, VM, plane fetch, flip, cursor, memory-power, watermark, fault, interrupt, and perfmon paths.
