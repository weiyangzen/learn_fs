# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_1_4_sh_mask.h lines 14355-17019

## Purpose

This chunk is generated AMD DCN 3.1.4 register field metadata. It contains no executable C logic; it publishes preprocessor constants for field bit positions and masks inside DCN display-engine MMIO registers. The companion offset header gives register addresses, while this header gives the field layout used by register-helper macros such as `FD_MASK`, `FD_SHIFT`, `REG_GET`, `REG_SET`, and `REG_UPDATE`.

Although the path is under a local `ceph-client` source mirror, this file is AMDGPU display-driver hardware metadata and has no Ceph or distributed filesystem behavior.

The requested range covers the tail of the DMCUB interrupt-status block, the rest of the DMCUB service interface fields, MCIF writeback and MMHUBBUB fields, HDA/Azalia stream/controller/root/input endpoint fields, DCHUBBUB SDPIF/return-path/arbitration/diagnostic fields, `DC_PERFMON3` through `DC_PERFMON5` field sets, and the start of DCN VM context page-table fields. This slice has 2,072 `#define` lines: 1,026 `__SHIFT` definitions and 1,046 `_MASK` definitions across 459 register-name groups. The count imbalance is caused by chunk boundaries: it starts with `DMCUB_INTERRUPT_STATUS` masks whose shifts are in the previous chunk, and it ends inside `DCN_VM_CONTEXT10_CNTL` before the final block-size mask.

## Important APIs, Types, And Macros

There are no functions, structs, enums, variables, local includes, locks, allocations, or direct persistence APIs in this line range. Its public interface is the generated macro naming convention:

- `<REGISTER>__<FIELD>__SHIFT`: field bit offset.
- `<REGISTER>__<FIELD>_MASK`: field bit mask.

Important register families in this chunk:

- DMCUB interrupt and control fields: `DMCUB_INTERRUPT_STATUS`, `DMCUB_INTERRUPT_TYPE`, external interrupt status/context/ack, fault-address registers, `DMCUB_SEC_CNTL`, memory QoS control, inbox/outbox base/size/read/write pointers, timers, scratch registers 0 through 15, GPINT input/output registers, low-speed wake interrupt enable, DMCUB memory power control, processor ID, and `DMCUB_CNTL2`.
- MCIF writeback buffer manager fields for writeback instance 0: software control, status, pitch, four buffer status/status2 blocks, arbitration, SCLK change, debug index/data, Y/C addresses and high address halves, VCE control, NB p-state/watermark controls, clock/self-refresh controls, QoS, luma/chroma sizes, per-buffer resolution, VMID, and minimum time-to-output.
- MMHUBBUB fields: p-state/watermark/warmup registers, warmup base and region, writeback/SMU watermark-change handshake, WBIF0 write-combine and outstanding counters, VGA split, memory power status/control, clock gating, soft reset, DMU interface error status, client unit IDs, and warmup VMID control.
- VGAIF MCIF fields for latency counters, write-combine timeout, and outstanding request counters.
- Perfmon instances `DC_PERFMON3`, `DC_PERFMON4`, and `DC_PERFMON5`: event selection, counted value selection, increment/run/interrupt controls, per-counter states, repeat count, count-off interrupt controls, counter interrupt status/ack, and high/low counter readback.
- HDA/Azalia fields: stream index/data windows for streams 0 through 15, clock gating, codec endpoint index/data windows, controller DTO/SOCCLK/DMA/RIRB/CORB/cyclic-buffer/global-capability/arbitration fields, CRC controls/results, memory power controls/status, root codec vendor/revision/capability/power/reset/subsystem/synchronization fields, audio port connectivity, GTC group offsets, and input endpoint index/data windows 0 through 7.
- DCHUBBUB SDPIF and VM aperture fields: SDPIF credit/status/error/snoop controls, VM physical-request selection, force-IO status and address reporting, framebuffer base/top/offset, AGP aperture, local HBM start/end/lock, and SDPIF memory power state.
- DCHUBBUB return-path and hub fields: return-path memory power, CRC controls and values, DCC statistic controls/counters, compression-buffer and DET controls, memory power mode/status, reserved compression-buffer space, debug controls, outstanding request limits, saturation/QoS forcing, DRAM-state controls, A/B/C/D watermark sets for urgency, self-refresh, Z8 self-refresh, DRAM clock change, and fractional urgent bandwidth.
- DCHUBBUB runtime/diagnostic fields: host-VM controls, watermark-change request/status, timeout enable, global timer, surface check addresses, VTG0 through VTG3 controls, soft reset, clock controls, DCFCLK gating delay, latency/ROB measurement controls, vline snapshot, overflow status/clear, timeout detection and interrupt status, FMON controls, and debug index/data.
- DCN VM context fields: `DCN_VM_CONTEXT0` through `DCN_VM_CONTEXT9` complete control/base/start/end page-table fields, plus the start of `DCN_VM_CONTEXT10_CNTL`.

## Control Flow

This header has no runtime control flow. Runtime sequencing is supplied by AMDGPU display and DMUB code that includes the generated DCN 3.1.4 offset and mask headers.

Typical flow:

1. DCN314 resource, IRQ, and DMUB code include `dcn_3_1_4_offset.h` and `dcn_3_1_4_sh_mask.h`.
2. Resource and IRQ code builds block-specific register tables using `SR`, `SRI`, `SRII`, field-list, and token-paste helper macros.
3. DMUB code builds `struct dmub_srv_dcn31_regs` for DCN314 by expanding `DMUB_DCN31_REGS()` and `DMUB_DCN31_FIELDS()` through `FD_MASK` and `FD_SHIFT`.
4. Runtime paths use those generated offsets/shifts/masks to program DMCUB reset/release, firmware windows, inbox/outbox rings, GPINT, scratch/status registers, interrupt status/ack, writeback memory, audio stream windows, hub watermarks, power/clock gating, VM context address ranges, and performance counters.

The masks do not encode ordering or access side effects. Consumers must still follow the hardware programming sequences around reset assertion/release, power gating, clock enabling, watermark updates, mailbox pointer ordering, write-one-to-clear status bits, indexed register windows, DMA enablement, VM table programming, and suspend/resume restore.

## State And Persistence Behavior

The chunk stores no software state and persists nothing on disk. It describes fields for MMIO-backed GPU state. State represented by these definitions includes:

- DMCUB firmware service state: interrupt status/type/ack, fault addresses, security reset/fault clear, memory QoS, inbox/outbox ring base/size/read/write pointers, timers, scratch registers, GPINT payloads, wake interrupts, memory power, processor ID, soft reset, and boot/control bits.
- Writeback and MMHUBBUB state: buffer manager ownership/status, buffer addresses and resolutions, arbitration, p-state/watermark coordination, self-refresh, QoS, VMID selection, outstanding request counters, memory power state, clock gating, and soft reset.
- HDA/Azalia state: indexed stream and endpoint register accesses, controller DMA/ring/cyclic-buffer controls, DTO/SOCCLK controls, CRC setup/results, global capabilities, stream arbitration, codec root parameters, audio power state, reset, connectivity overrides, GTC offsets, and audio memory power.
- DCHUBBUB memory fabric state: SDPIF port/credit/error status, VM aperture and AGP/HBM address windows, CRC/DCC statistics, compression buffers, DET allocations, hub memory power state, arbitration watermarks for sets A through D, host-VM policy, timer/surface-check diagnostics, timeout detection, and latency/ROB measurement state.
- DCN VM context state: page-table depth and block size, page-directory base address, logical page start/end ranges, and framebuffer/AGP aperture translation inputs.

Persistence is hardware-defined. Some fields are configuration bits that remain until modeset, reset, power gating, suspend/resume, or ASIC reset. Other fields are read-only status, sticky error, write-one-to-clear, self-clearing request, or indexed-window data fields. This generated header does not express those access classes; driver code and hardware documentation must supply that context.

## Dependencies And Integration Points

This chunk must match the generated DCN 3.1.4 register database and the companion offset file:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_1_4_offset.h`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_1_4_sh_mask.h`

Direct include sites found in this tree include:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dmub/src/dmub_dcn314.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/irq/dcn314/irq_service_dcn314.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/resource/dcn314/dcn314_resource.c`

Key integration points:

- `dmub_dcn314.c` expands `DMUB_DCN31_FIELDS()` into DCN314 mask and shift tables. Fields from this chunk directly back DMUB control paths such as `DMCUB_CNTL`, `DMCUB_CNTL2`, `DMCUB_SEC_CNTL`, inbox/outbox pointers, interrupt enable/ack, scratch registers, `MMHUBBUB_SOFT_RESET`, `DCN_VM_FB_LOCATION_BASE`, and `DCN_VM_FB_OFFSET`.
- `dmub_srv.c` selects `dmub_srv_dcn314_regs` for `DMUB_ASIC_DCN314`, then shares common `dmub_dcn31_*` operations for reset, window setup, mailbox setup, GPINT, boot options, diagnostic data, and timer reads.
- `irq_service_dcn314.c` uses the same generated field namespace for interrupt-source status, acknowledgement, and routing tables, including display, hub, audio, hotplug, AUX/DDC, and perfmon events.
- `dcn314_resource.c` includes this header while constructing DCN314 display resources, register blocks, IRQ service, DIO/stream encoders, DSC instances, timing generators, hardware sequencer, and resource capability tables.
- Clock manager, DML, and HWSS DCN314 code do not necessarily include this header directly, but they depend on the register tables and hardware behavior configured through it when programming watermarks, clock/power state, VM apertures, and hub arbitration.

## Risks And Edge Cases

- Generated macro drift is the main risk. A wrong constant compiles cleanly but can program the wrong bit, corrupt adjacent fields, or misread status.
- This range has two artificial boundary splits. The `DMCUB_INTERRUPT_STATUS` shift definitions are in the prior chunk, while `DCN_VM_CONTEXT10_CNTL__VM_CONTEXT10_PAGE_TABLE_BLOCK_SIZE_MASK` is in the next line/chunk. File-level reconciliation must merge adjacent chunks before making complete claims about those registers.
- DMCUB fields are high impact. Incorrect reset, security, mailbox pointer, interrupt, GPINT, scratch, timer, or fault-address masks can prevent firmware boot, lose command ring traffic, create stuck interrupts, or hide useful fault diagnostics.
- Indexed HDA/Azalia stream and endpoint windows are sequencing-sensitive. Incorrect index/write-enable/data fields can target the wrong stream or codec node and break HDMI/DP audio setup, ring/DMA operation, or codec power-state reporting.
- MCIF writeback and MMHUBBUB fields influence memory traffic and power management. Bad buffer address, VMID, pitch, outstanding-counter, watermark, self-refresh, or clock-gating fields can cause writeback corruption, display underflow, failed p-state changes, or resume problems.
- DCHUBBUB watermark and arbitration fields govern display memory-service latency. Incorrect A/B/C/D watermark, urgent-bandwidth, host-VM, timeout, or surface-check fields can lead to underflow, excessive power use, false timeout interrupts, or hard-to-diagnose stalls.
- VM aperture and context fields must agree with GPU memory manager state. Bad page-table base/start/end, FB/AGP/HBM aperture, or lock fields can translate display requests to the wrong physical memory.
- Perfmon fields are diagnostic but side-effectful. Wrong event selects, run-enable controls, or ack masks can make performance data misleading or leave counter interrupts stuck.
- Memory power and soft-reset fields affect live hardware blocks. Applying these masks outside the expected disable/reset sequence can power down active audio, writeback, hub, or DMCUB state.

## Test Signals

Useful validation combines build checks, generated-header consistency checks, and hardware behavior:

- Build AMDGPU/DC with DCN314 enabled. Missing or renamed macros should fail in `dmub_dcn314.c`, `irq_service_dcn314.c`, and `dcn314_resource.c`.
- Mechanically verify that complete fields in this range have paired `__SHIFT` and `_MASK` definitions, while allowing the known boundary exceptions for `DMCUB_INTERRUPT_STATUS` and `DCN_VM_CONTEXT10_CNTL`.
- Compare the field values against AMD's authoritative DCN 3.1.4 register database and adjacent generated DCN 3.1.x headers where fields are expected to remain compatible.
- Exercise DMUB/DCN314 boot: reset/release, secure reset status, firmware window setup, inbox/outbox ring pointer traffic, GPINT acknowledgement/response, scratch/status readback, timer readback, and fault-address reporting.
- Exercise IRQ behavior: vblank/vline, hotplug/HPD RX, AUX/DDC, audio, DMCUB GPINT IH, DCHUBBUB timeout, watermark-change done, and perfmon interrupts. Watch for missing, stuck, or misrouted events.
- Exercise writeback and hub memory paths: MCIF writeback buffers, pitch/resolution/address programming, VMID selection, p-state/watermark changes, self-refresh, outstanding-counter readback, and memory power transitions.
- Exercise HDMI/DP audio: stream index/data programming, controller DMA/RIRB/CORB/cyclic-buffer paths, DTO/SOCCLK controls, codec power/reset, endpoint register access, and CRC diagnostics.
- Exercise DCHUBBUB watermarks and VM paths under bandwidth stress, p-state changes, host-VM traffic, AGP/FB aperture changes, timeout detection, surface-check diagnostics, and suspend/resume.
- Exercise perfmon instances 3 through 5 by selecting events, enabling counters, reading high/low values, causing/clearing counter interrupts, and verifying stable state transitions.

## Cross-Chunk Notes

The previous chunk owns the beginning of `DMCUB_INTERRUPT_STATUS`, including the shift definitions for the status masks present at this range's start. The next chunk owns the remainder of `DCN_VM_CONTEXT10_CNTL` and later VM context fields. The final per-file research document should merge adjacent chunks before drawing full-file conclusions about DMCUB interrupt status or the complete set of DCN VM contexts.
