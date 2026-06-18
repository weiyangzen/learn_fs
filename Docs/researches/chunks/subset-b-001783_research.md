# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_0_3_sh_mask.h lines 4720-7368

## Purpose

This chunk is generated AMD DCN 3.0.3 register field metadata. It contains no executable C logic; it exposes C preprocessor constants naming bit positions (`__SHIFT`) and masks (`_MASK`) for 32-bit MMIO register fields used by the AMD display driver. Consumer code pairs these definitions with the matching `dcn_3_0_3_offset.h` register offsets and AMD register helpers such as `REG_SET`, `REG_UPDATE`, `REG_GET`, `SR`, `SRI`, and block-specific field-list macros.

The requested range starts in the middle of the DMCUB interrupt/status block, then covers DMCUB mailbox, scratch, security, timer, memory-power, and GPINT fields; MCIF writeback and MMHUBBUB fields; one DC perfmon instance; Azalia/HDA audio endpoint, controller, root, stream, and input endpoint fields; DCHUBBUB SDPIF, return-path, arbitration, watermark, CRC, timing, clock, reset, timeout, and FMON fields; another DC perfmon instance; DCN VM context/fault fields; and the first HUBP0 surface/viewport/request/control/clock/perf-measurement fields. The slice has 2,066 `#define` lines: 1,035 shift definitions and 1,031 mask definitions.

Although the source path is under a local `ceph-client` mirror, this file is AMDGPU display-controller hardware metadata. It does not implement Ceph or distributed filesystem behavior.

## Important APIs, Types, And Macros

There are no functions, structs, enums, global variables, includes, locks, allocations, or persistence APIs in this chunk. The public interface is the generated macro namespace:

- `<REGISTER>__<FIELD>__SHIFT`: least-significant bit position of a hardware register field.
- `<REGISTER>__<FIELD>_MASK`: mask used to isolate or update that field.
- Address-block comments such as `dce_dc_mmhubbub_mcif_wb0_dispdec` and `dce_dc_dcbubp0_dispdec_hubp_dispdec`: generator breadcrumbs that group registers by display hardware block.

Major macro families in this slice:

- `DMCUB_*`: interrupt status/type, external interrupt status/context/ack, instruction/data fault addresses, security reset and fault-clear controls, memory QoS/space controls, inbox/outbox base/size/read/write pointers, timer triggers/window/current value, scratch registers 0-15, DMCUB control bits, GPINT data registers, undefined-address fault address, light-sleep wake interrupt enable, memory power control, and processor ID.
- `MCIF_WB_*`: display writeback buffer-manager software control/status, buffer pitch, per-buffer Y/C address low/high registers, per-buffer status/status2 and resolution, arbitration, SCLK/NB pstate/self-refresh controls, VCE buffer manager controls, clock gating, luma/chroma sizes, VMID, memory-power, and minimum time-to-output controls.
- `MMHUBBUB_*`, `WBIF0_*`, `MCIF_*`, and `VGA_SRC_SPLIT_CNTL`: writeback/hubbub warmup controls and base addresses, watermark and pstate-latency values, memory-power and clock/soft-reset controls, WBIF misc/phase counters, VGA/MCIF write-combine controls, DMU interface error status, client unit IDs, and warmup VMID controls.
- `DC_PERFMON3_*` and `DC_PERFMON4_*`: counter selection, increment mode, run mode, threshold/interrupt policy, counter state, perfmon start/stop/reporting, high/low counter reads, and counter-value interrupt status/ack fields for MMHUBBUB and DCHUBBUB perfmon blocks.
- `AZF0ENDPOINT[0-7]_*`, `AZF0INPUTENDPOINT[0-7]_*`, `AZF0STREAM[8-15]_*`, and `AZALIA_*`: indexed codec endpoint/stream registers, controller clock gating, audio DTO/control, SOCCLK, DMA, RIRB/CORB/BDL controls, payload capability and stream arbitration, CRC controls/results, memory-power state, root codec vendor/revision/channel/power/reset/sync controls, GTC group offsets, and audio port connectivity fields.
- `DCHUBBUB_SDPIF_*`, `VM_REQUEST_PHYSICAL`, and `DCHUBBUB_FORCE_IO_STATUS_*`: VM physical request policy, framebuffer/AGP/HBM address ranges, local HBM lock control, per-pipe security levels, SDPIF memory-power and config bits, and forced I/O status.
- `DCHUBBUB_RET_PATH_*`: return-path DCC configuration registers for multiple pipes, return-path memory-power control/status, and DCHUBBUB CRC select/mask/window/source and CRC result fields.
- `DCHUBBUB_ARB_*`, `SURFACE_CHECK*`, `VTG*`, `DCHUBBUB_*`, `DCFCLK_CNTL`, and `FMON_*`: arbitration outstanding request caps, saturation and QoS force values, DRAM state policy, A/B/C/D urgency and self-refresh/DRAM-clock-change watermarks, watermark change policy, global timer, surface-check addresses, VTG selection, hubbub soft reset and clock status, performance measurement windows, timeout detection/interrupts, fractional urgency bandwidth, and frequency-monitor controls.
- `DCN_VM_CONTEXT[0-15]_*`, `DCN_VM_DEFAULT_ADDR_*`, and `DCN_VM_FAULT_*`: VM page table base/start/end addresses, page-table depth and block size, default address/control fields, fault interrupt enable/clear/mode/status, fault address, and fault attribution fields.
- `HUBP0_*`: surface pixel format/rotation/mirroring/alpha, address and tiling configuration, primary/secondary viewport start/dimension for luma and chroma, request-size configuration, HUBP blank/disable/VTG/timeout/underflow controls, clock gating/status, VM page size, and DCFCLK/DPPCLK measurement-window controls.

## Control Flow

This header has no runtime control flow. Runtime sequencing is in the display driver:

1. DCN303 resource, IRQ, and DMUB service code include `dcn_3_0_3_offset.h` and this matching `dcn_3_0_3_sh_mask.h`.
2. Resource construction token-pastes register and field names into typed register, shift, and mask tables. Examples in this tree include `dcn303_resource.c` building `hubbub_shift`, `audio_shift`, `hubp_shift`, `mcif_wb30_shift`, and corresponding mask tables from block macros.
3. Block implementations operate through those tables with register-helper calls. DMUB code reads and writes DMCUB mailbox, interrupt, and fault fields; DCE audio code uses Azalia endpoint fields; HUBP/HUBBUB/MMHUBBUB code programs surface fetch, VM, arbitration, watermark, writeback, memory-power, and clocking state.
4. Hardware observes those MMIO fields during boot/display resource initialization, DMUB command exchange, modesets, page flips, audio stream setup, display writeback capture, memory watermark programming, VM context setup, fault handling, perf/debug capture, suspend/resume, and ASIC reset flows.

The macros do not encode ordering. Consumers must still sequence clocks and resets before programming gated blocks, update writeback buffers only when buffer fences/state allow it, program VM page-table fields coherently, acknowledge sticky interrupt/status fields correctly, and respect double-buffer or pending-update hardware semantics where applicable.

## State And Persistence Behavior

The chunk stores no software state. It describes MMIO-backed GPU state:

- DMCUB fields represent firmware-facing mailbox rings, timers, scratch state, GPINT data, interrupt status/type/ack state, fault addresses, security reset state, and microcontroller memory-power policy.
- MCIF writeback fields represent capture buffer addresses and dimensions, buffer-manager state, luma/chroma pitch and allocation size, VCE/writeback flow-control policy, self-refresh and pstate-change policy, clock gating, and VMID selection for writeback memory traffic.
- MMHUBBUB and DCHUBBUB fields represent display fabric warmup, memory power, clocking, resets, arbitration, watermarks, self-refresh and DRAM clock-change thresholds, urgency bandwidth, timeout detection, surface-check addresses, CRC collection, and debug/frequency/performance measurement state.
- Azalia/HDA fields represent audio codec endpoint/index/data windows, stream DMA/ring controls, audio DTO clocking, CRC/debug paths, root codec power/reset/channel capabilities, and output/input port connectivity.
- VM context fields represent display VM page table base/start/end ranges and page-table format for contexts 0 through 15, plus default address and fault attribution/status state.
- HUBP0 fields represent plane surface format, tiling/addressing, viewport geometry, fetch request sizing, blank/disable/underflow/timeout status, clock status, VM page sizing, and local perf-measurement controls.

Persistence is hardware-defined. Configuration fields generally last until display reprogramming, power gating, block reset, suspend/resume restoration, or full ASIC reset. Status, fault, interrupt, ack, counter, timeout, underflow, and update-pending fields may be sticky, read-only, write-one-to-clear, self-clearing, or timing-sensitive. This generated header only provides bit encodings; safe access rules come from the hardware spec and consuming AMD display code.

## Dependencies And Integration Points

This chunk depends on AMD's generated DCN 3.0.3 register database and must stay synchronized with:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_0_3_offset.h`, which provides the corresponding register offsets.
- AMD display register-helper infrastructure that expands `REG_*`, `SR`, `SRI`, `SRII`, `FD_MASK`, `FD_SHIFT`, `HUBP_MASK_SH_LIST_DCN30`, `HUBBUB_MASK_SH_LIST_DCN30`, `MCIF_WB_COMMON_MASK_SH_LIST_DCN30`, `AUD_COMMON_MASK_SH_LIST_BASE`, and similar macros into offset plus shift/mask operations.
- Adjacent chunks of this same header, because the requested slice starts after the beginning of `DMCUB_INTERRUPT_STATUS` and ends inside `HUBP0_HUBP_MEASURE_WIN_CTRL_DPPCLK`.

Direct DCN 3.0.3 include sites in this tree include:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dmub/src/dmub_dcn303.c`, which builds `dmub_srv_dcn303_regs` from DMUB common and DMCUB register/field lists.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/resource/dcn303/dcn303_resource.c`, which builds resource-pool register, shift, and mask tables for HUBBUB, audio, HUBP, DWB/MCIF writeback, DSC, DIO, and related blocks.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/irq/dcn303/irq_service_dcn303.c`, which maps DCN303 interrupt sources to register fields.

Important shared consumers include:

- `display/dmub/src/dmub_reg.h` and DMUB service code for DMCUB mailbox, scratch, interrupt, and fault access.
- `display/dc/mmhubbub/dcn30`/`dcn32` style MMHUBBUB implementations for MCIF writeback buffer programming, warmup, watermarks, pstate latency, memory-power, and clock control.
- `display/dc/hubbub/dcn20`/`dcn30` style HUBBUB implementations for DCHUBBUB arbitration, watermarks, CRC, timeout, clock, and reset programming.
- `display/dc/hubp/dcn20`/`dcn30` style HUBP implementations for surface format, tiling, viewport, VM, request sizing, underflow, and clock state.
- `display/dc/dce/dce_audio.*` and stream-encoder audio paths for Azalia endpoint/root/controller state and audio stream setup.
- `display/dc/dcn20/dcn20_vmid.*` and related VM helper code for VM context page table programming.

## Risks And Edge Cases

- Shift/mask drift is the central risk. These macros are untyped integers, so an incorrect mask or bit position can compile cleanly while programming the wrong hardware bit.
- Chunk boundaries are artificial. The beginning lacks the earlier part of `DMCUB_INTERRUPT_STATUS`, and the end stops before the rest of `HUBP0_HUBP_MEASURE_WIN_CTRL_DPPCLK` and the following HUBPREQ0 block.
- DMCUB mailbox and interrupt fields are synchronization-sensitive. Wrong inbox/outbox pointer masks, ack/status handling, GPINT fields, or timer/fault bits can cause DMUB command hangs, missed firmware interrupts, or unrecoverable display-controller faults.
- MCIF writeback buffer address, high-address, pitch, size, and status fields are DMA-facing. Bad masks can target the wrong memory, corrupt capture output, violate VMID isolation, or leave buffer-manager state inconsistent.
- HDA/Azalia endpoint, stream, DMA, and power fields are index/data-window based. A wrong endpoint or stream field can affect only specific audio instances, making regressions appear as sink-specific or stream-number-specific audio failures.
- DCHUBBUB arbitration and watermark fields are timing-critical. Incorrect urgency, self-refresh, DRAM-clock-change, timeout, or fractional bandwidth masks can show up only under high-resolution, high-refresh, multi-plane, writeback, or memory-clock-transition workloads.
- VM context page-table fields are security- and correctness-sensitive. Incorrect base/start/end/depth/block-size masks can cause display VM faults, wrong physical address translation, or out-of-range memory access.
- Sticky status and write-one-to-clear fields in interrupt, fault, CRC, timeout, underflow, perfmon, and memory-power blocks can be mishandled by generic read-modify-write operations if the consumer does not follow hardware-specific access rules.
- HUBP surface, viewport, tiling, and request-size fields interact with DML calculations and plane state. Small mask errors can cause corruption, cropping, underflow, or only-mode-specific failures.
- Perfmon and FMON fields are debug/telemetry-facing but still mutable hardware state. Bad selection or ack fields can make diagnostics misleading and can hide real performance, clock, or timeout issues.

## Test Signals

Useful validation is a mix of generated-header consistency and hardware behavior:

- Build AMDGPU/DC with DCN303 support enabled; missing or renamed macros should fail in `dmub_dcn303.c`, `dcn303_resource.c`, `irq_service_dcn303.c`, HUBP/HUBBUB/MMHUBBUB/audio table construction, and DMUB register tables.
- Mechanically verify that every field in lines 4720-7368 has coherent `__SHIFT`/`_MASK` pairs, accounting for the intentionally partial start and end of the chunk.
- Diff this range against AMD's authoritative generated DCN 3.0.3 register database and nearby generated headers where fields are expected to match.
- Exercise DMUB firmware command paths: boot, inbox/outbox command submission, GPINT signaling, timer handling, interrupt ack/status behavior, scratch reads/writes, and fault reporting.
- Exercise display writeback: buffer allocation/address programming, luma/chroma pitch and size, buffer fences, buffer flip/status transitions, VMID use, pstate/self-refresh transitions, overflow/backpressure, and captured-frame correctness.
- Exercise HDA/HDMI/DP audio: endpoint enumeration, audio stream enable/disable, sample-rate/DTO behavior, DMA ring operation, suspend/resume, hotplug audio device appearance, and CRC/debug paths if available.
- Exercise HUBBUB/DCHUBBUB under stress: multi-plane and high-refresh modes, memory clock changes, self-refresh entry/exit, watermark changes, warmup paths, CRC capture, timeout interrupt handling, and forced I/O/debug status.
- Exercise VM setup and fault paths: valid page-table programming, invalid/fault injection where supported, default address behavior, context 0-15 table ranges, and fault address/status reporting.
- Exercise HUBP0 plane programming: varied pixel formats, rotation/mirroring/alpha plane paths, linear and tiled surfaces, chroma planes, viewport cropping, underflow detection, clock gating, and performance measurement windows.
- Monitor kernel logs, DC debug traces, perf counters, CRCs, captured frames, display corruption, audio dropouts, DMUB timeouts, VM faults, underflow/timeout interrupts, and suspend/resume failures.

## Cross-Chunk Notes

Earlier chunks own the start of the DMCUB interrupt/status definitions and prior DCN 3.0.3 register field families. Later chunks continue after `HUBP0_HUBP_MEASURE_WIN_CTRL_DPPCLK` into HUBPREQ0 and the remaining HUBP/display pipe register fields. The final per-file research document should merge adjacent chunks before making complete claims about all DMCUB, MCIF writeback, HDA audio, DCHUBBUB, VM, or HUBP coverage in `dcn_3_0_3_sh_mask.h`.
