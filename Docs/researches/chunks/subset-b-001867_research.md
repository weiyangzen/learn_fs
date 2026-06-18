# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_1_5_sh_mask.h lines 4863-7527

## Purpose

This chunk is generated AMD DCN 3.1.5 register field metadata. It contains no executable C logic; it publishes preprocessor constants for bit positions and masks inside display-engine MMIO registers. The companion `dcn_3_1_5_offset.h` header supplies register offsets, while this file supplies the field layouts consumed by AMDGPU display register helpers such as `FD_MASK`, `FD_SHIFT`, `REG_GET`, `REG_SET`, and `REG_UPDATE`.

Although the tree path is under a local `ceph-client` source mirror, this range is AMDGPU display-driver hardware metadata and has no Ceph or distributed filesystem behavior.

The requested range covers the tail of `DC_PERFMON3`, legacy VGA and VGAIF/MMHUBBUB-facing registers, MCIF writeback buffer-manager fields, `DC_PERFMON4`, MMHUBBUB control/power/warmup fields, HDA/Azalia controller/root/stream/endpoint fields, `DC_PERFMON5`, DCHUBBUB arbitration/watermark/VM/SDPIF/return-path/diagnostic fields, and the beginning of DCN VM context page-table fields. This slice has 2,665 source lines, including 2,079 `#define` lines: 1,040 `__SHIFT` definitions and 1,039 `_MASK` definitions across 45 generated address-block sections. The count imbalance and incomplete register groups are chunk-boundary artifacts.

## Important APIs, Types, And Macros

There are no functions, structs, enums, variables, allocations, locks, callbacks, or direct persistence APIs in this line range. Its public interface is the generated macro naming convention:

- `<REGISTER>__<FIELD>__SHIFT`: field bit offset.
- `<REGISTER>__<FIELD>_MASK`: field mask for the same field.

Important register families in this chunk:

- `DC_PERFMON3`, `DC_PERFMON4`, and `DC_PERFMON5`: performance-counter control, event select, increment/run controls, per-counter state, repeat count, count-off interrupt controls, high/low counter readback, and interrupt status/ack fields.
- Legacy VGA and VGAIF fields: page-selection addresses, render control, sequencer reset behavior, VGA mode/surface/base address fields, HDP/cache controls, per-pipe `D1VGA_CONTROL` through `D6VGA_CONTROL`, VGA status/clear, indexed CRTC/SEQ/GRPH/DAC/attribute ports, source selection, QoS, and VGA split controls.
- MCIF writeback instance 0: buffer-manager software control/status, buffer pitch, four Y/C buffer address pairs with high address halves, buffer status/status2 groups, per-buffer resolution, arbitration, clock/p-state/self-refresh controls, watermark/QoS fields, VCE handoff controls, VMID selection, and minimum time-to-output.
- MMHUBBUB fields: writeback p-state latency and watermark controls, warmup base/region/status, WBIF/SMU watermark-change handshake, WBIF0 misc/outstanding counters, memory power status/control, clock gating, soft reset, DMU interface error status, client unit ID, and warmup VMID control.
- HDA/Azalia fields: controller clock gating, DTO/SOCCLK, DMA/BDL/RIRB/CORB/cyclic-buffer controls, stream arbitration, CRC setup/results, memory power control/status, root codec vendor/revision/capability/power/reset/subsystem/synchronization fields, port connectivity fields, GTC group offsets, 16 stream index/data windows, 8 output endpoint index/data windows, and 8 input endpoint index/data windows.
- DCHUBBUB hub fields: outstanding request limits, saturation and QoS forcing, DRAM-state controls, A/B/C/D watermark sets for urgency, memory trip time, self-refresh entry/exit including Z8, DRAM clock change, fractional urgent bandwidth, host-VM controls, watermark-change request/status, timeout enable, global timer, surface-check addresses, VTG controls, soft reset, clock controls, DCFCLK gating delay, performance measurement, vline snapshot, overflow/underflow status, timeout detection, FMON controls, and test debug windows.
- DCHUBBUB SDPIF and VM aperture fields: SDPIF credit/status/error/limit/snoop controls, physical VM request selection, forced IO status and address reporting, framebuffer base/top/offset, AGP aperture, local HBM address range and lock control, pipe security levels, metadata security levels, and SDPIF memory power state.
- DCHUBBUB return path and compression state: DCC configuration for pipes 0 through 7, return-path memory power, CRC controls and result values, DCC statistic controls/counters, compression-buffer control, DET controls, memory power mode/status, compression-buffer memory power controls, and reserved compression-buffer space.
- DCN VM context fields: complete control/base/start/end page-table fields for contexts 0 through 7, plus the start of context 8 through `DCN_VM_CONTEXT8_PAGE_TABLE_BASE_ADDR_LO32`.

## Control Flow

This header has no runtime control flow. Runtime sequencing is supplied by AMDGPU display code that includes the generated DCN 3.1.5 offset and mask headers.

Typical flow:

1. DCN315 DMUB, IRQ, and resource code include `dcn/dcn_3_1_5_offset.h` and `dcn/dcn_3_1_5_sh_mask.h`.
2. Resource code builds ASIC-specific register tables by expanding `SR`, `SRI`, `SRII`, and field-list helper macros over these names.
3. `dmub_dcn315.c` builds `dmub_srv_dcn315_regs` by expanding DCN315 field lists through `FD_MASK` and `FD_SHIFT`; fields from this chunk include `MMHUBBUB_SOFT_RESET`, `DCN_VM_FB_LOCATION_BASE`, and `DCN_VM_FB_OFFSET`.
4. Runtime paths use the generated offsets, shifts, and masks to program display hub power, VM apertures, writeback, audio, VGA disable/control paths, watermarks, performance counters, CRC/statistics, and timeout/diagnostic blocks.

The masks do not encode access ordering or side effects. Consumers still have to follow hardware sequences around reset assertion/release, clock and memory power transitions, indexed register windows, DMA/ring enablement, write-one-to-clear status, self-clearing request bits, watermark commits, VM aperture setup, and suspend/resume restore.

## State And Persistence Behavior

This chunk stores no software state and persists nothing on disk. It describes MMIO-backed GPU state:

- Perfmon state includes selected events, counter run/increment controls, current counter values, high/low readback selection, interrupt status, and acknowledgement bits.
- VGA state includes legacy aperture/page mapping, render and sequencer behavior, per-pipe VGA enable/timing/polarity/rotation, indexed legacy register windows, status/clear bits, cache/HDP controls, and source selection.
- Writeback and MMHUBBUB state includes buffer ownership/status, Y/C addresses, resolutions, VMID, arbitration, p-state/watermark controls, self-refresh, outstanding request counters, warmup configuration, memory power state, clock gating, and soft reset.
- HDA/Azalia state includes controller DMA/ring/cyclic-buffer controls, stream and endpoint indexed-register access, DTO/SOCCLK generation, codec root parameters, audio power/reset state, CRC diagnostics, connectivity registers, GTC offsets, and memory power state.
- DCHUBBUB state includes memory-service arbitration, watermark sets A through D, host-VM policy, VM apertures and local HBM ranges, SDPIF credits/security/power state, CRC/DCC statistics, DET/compression-buffer allocation, timeout detection, vline snapshots, global timers, and debug windows.
- DCN VM context state includes page-table depth, block size, page-directory base, and logical page start/end ranges for contexts 0 through 7, with context 8 continuing in the next chunk.

Persistence is hardware-defined. Some fields remain configured until modeset, reset, power gating, suspend/resume, or ASIC reset. Others are read-only status, sticky error, interrupt status, write-one-to-clear acknowledgements, self-clearing requests, or indexed-window data fields. This generated header does not distinguish those access classes.

## Dependencies And Integration Points

This chunk must match the generated DCN 3.1.5 register database and companion offset header:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_1_5_offset.h`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_1_5_sh_mask.h`

Direct include sites found in this tree include:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dmub/src/dmub_dcn315.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/irq/dcn315/irq_service_dcn315.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/resource/dcn315/dcn315_resource.c`

Key integration points:

- `dmub_dcn315.c` expands `DMUB_DCN315_FIELDS()` into mask and shift tables. This chunk backs DMUB-facing fields for MMHUBBUB soft reset and DCN VM framebuffer base/offset programming.
- `dcn315_resource.c` uses this namespace to build HW sequencer, DWB/MCIF writeback, audio, hub, and power-management register tables. The local `HWSEQ_DCN31_REG_LIST()` and `HWSEQ_DCN31_MASK_SH_LIST()` reference fields from this chunk including `DCHUBBUB_GLOBAL_TIMER_CNTL`, `DCHUBBUB_ARB_HOSTVM_CNTL`, `MMHUBBUB_MEM_PWR_CNTL`, `DCHUBBUB_CRC_CTRL`, `D1VGA_CONTROL` through `D6VGA_CONTROL`, `AZALIA_AUDIO_DTO`, and `AZALIA_CONTROLLER_CLOCK_GATING`.
- `dcn315_resource.c` also builds `dcn30_mmhubbub`/MCIF writeback tables with `MCIF_WB_COMMON_REG_LIST_DCN30()` and `MCIF_WB_COMMON_MASK_SH_LIST_DCN30()`, which rely on the MCIF writeback field names in this chunk.
- `irq_service_dcn315.c` includes the header for DCN315 interrupt-source status and acknowledge metadata; nearby perfmon, DCHUBBUB timeout, audio, and hub status fields are part of the same generated field namespace.
- Older AMDGPU paths outside DCN315 show direct use of compatible VGA masks such as `VGA_RENDER_CONTROL__VGA_VSTATUS_CNTL_MASK`, confirming that these generated constants are consumed by generic register-field helpers and direct read/modify/write paths.

## Risks And Edge Cases

- Generated macro drift is the primary risk. A wrong shift or mask compiles cleanly but can program the wrong bit, corrupt adjacent fields, or misread status.
- This chunk starts inside the `DC_PERFMON3` register family. The preceding chunk owns earlier `DC_PERFMON3_PERFMON_CNTL` definitions; file-level reconciliation should merge the adjacent chunk before making full claims about perfmon instance 3.
- This chunk ends inside the DCN VM context 8 field group after the context 8 page-table base low word. The next chunk owns the remaining context 8 start/end fields and later contexts.
- VGA fields are legacy but still high impact during boot, handoff, and disable sequences. Incorrect VGA render, sequencer reset, cache/HDP, page, or per-pipe control fields can leave legacy decode active, blank display unexpectedly, or interfere with display ownership.
- MCIF writeback and MMHUBBUB fields influence memory traffic and power state. Bad buffer address, high-address, pitch, VMID, arbitration, watermark, self-refresh, clock-gating, or memory power masks can cause writeback corruption, underflow, failed p-state changes, or resume problems.
- HDA/Azalia indexed stream and endpoint windows are sequencing-sensitive. Incorrect index/data/write-enable fields can target the wrong stream or codec node and break HDMI/DP audio setup, DMA ring operation, or codec power reporting.
- DCHUBBUB watermark and arbitration fields govern display memory-service latency. Incorrect A/B/C/D watermarks, urgent bandwidth, host-VM policy, timeout, or surface-check fields can produce underflow, false timeout interrupts, excessive power use, or stalls that are hard to attribute.
- VM aperture and context fields must agree with GPU memory-manager state. Bad framebuffer/AGP/HBM apertures or page-table base/start/end fields can translate display requests to the wrong memory.
- Soft reset and memory power fields are live-hardware controls. Applying these masks outside the expected quiesce/reset/power sequence can drop active writeback, hub, audio, or VGA state.
- Perfmon fields are diagnostic but side-effectful. Wrong run-enable, event, state, or ack masks can produce misleading measurements or stuck performance-counter interrupts.

## Test Signals

Useful validation combines build checks, generated-header consistency checks, and hardware behavior:

- Build AMDGPU/DC with DCN315 enabled. Missing or renamed macros should fail in `dmub_dcn315.c`, `irq_service_dcn315.c`, or `dcn315_resource.c`.
- Mechanically verify paired `__SHIFT` and `_MASK` definitions for complete fields in this range, while allowing the known boundary split at `DC_PERFMON3` and the partial `DCN_VM_CONTEXT8` group.
- Compare field values against AMD's authoritative DCN 3.1.5 register database and adjacent generated DCN 3.1.x/DCN 3.2.x headers where fields are expected to remain compatible.
- Exercise DMUB/DCN315 boot and service setup: MMHUBBUB soft reset release, framebuffer base/top/offset programming, inbox/outbox traffic from neighboring chunks, GPINT acknowledgement, and suspend/resume restore.
- Exercise VGA handoff/disable paths, including `VGA_RENDER_CONTROL`, sequencer reset, `D1VGA_CONTROL` through `D6VGA_CONTROL`, VGA status clear, and legacy indexed register access.
- Exercise MCIF writeback with luma/chroma buffers, high address halves, pitch/resolution programming, VMID selection, buffer-status transitions, p-state changes, self-refresh, outstanding-counter readback, and memory power transitions.
- Exercise HDMI/DP audio: controller DTO/SOCCLK, stream index/data programming, RIRB/CORB/BDL/cyclic-buffer DMA, endpoint index/data windows, codec power/reset, connectivity registers, and CRC diagnostics.
- Exercise DCHUBBUB watermarks and VM paths under bandwidth stress, p-state changes, host-VM traffic, AGP/FB/HBM aperture changes, timeout detection, surface-check diagnostics, CRC/DCC statistic collection, and suspend/resume.
- Exercise perfmon instances 3 through 5 by selecting events, enabling counters, reading high/low values, causing and clearing counter interrupts, and verifying state transitions.

## Cross-Chunk Notes

The previous chunk owns the earlier `DC_PERFMON3_PERFMON_CNTL` fields immediately before this range. The next chunk owns the remainder of `DCN_VM_CONTEXT8` and later VM context fields. The final per-file research document should reconcile adjacent chunks before drawing complete conclusions about `DC_PERFMON3` or the full DCN VM context table.
