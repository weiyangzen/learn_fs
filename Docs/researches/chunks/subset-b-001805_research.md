# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_1_2_sh_mask.h lines 7218-9886

## Purpose

This chunk is generated AMD DCN 3.1.2 register field metadata. It contains no executable C logic; it publishes preprocessor constants that describe bit positions (`__SHIFT`) and bit masks (`_MASK`) for memory-mapped display-controller registers. Driver code pairs these constants with offsets from `dcn_3_1_2_offset.h` and uses register helpers to read, write, update, poll, and decode individual fields without hard-coding bit layouts at each call site.

The requested range starts inside the `D2VGA_CONTROL` field group, covers VGA status/interrupt/control fields, MCIF/VGA interface and MCIF writeback fields, MMHUBBUB and DCHUBBUB memory-hub/display-hub fields, Azalia display-audio controller/root/stream/endpoint fields, DCN VM and SDPIF fields, return-path/DCC/CRC/compression-buffer fields, VM context 0 through 15 page-table fields, VM fault reporting fields, and begins the `DC_PERFMON6` performance-monitor block. Although the path is under a local `ceph-client` mirror, this file is AMDGPU display-driver hardware metadata, not Ceph or distributed-filesystem logic.

Within lines 7218-9886 there are 2,062 `#define` lines: 1,032 shift macros and 1,030 mask macros. The imbalance is due to chunk boundaries: the first two visible lines are masks from a preceding `D2VGA_CONTROL` group, and the final line stops before the rest of `DC_PERFMON6_PERFMON_CNTL` and subsequent perfmon masks in the next chunk.

## Important APIs, Types, And Macros

There are no functions, structs, enums, variables, local includes, allocation paths, or locking primitives in this range. The public interface is the generated macro namespace:

- `<REGISTER>__<FIELD>__SHIFT`: bit index for a field inside the register value.
- `<REGISTER>__<FIELD>_MASK`: already-shifted mask for isolating or updating that field.
- Register families are grouped by comment headers such as `//VGA_STATUS` and generated address-block comments such as `// addressBlock: dce_dc_dchubbubl_hubbub_dispdec`.

Major field families in this chunk:

- VGA and legacy display routing: `D2VGA_CONTROL` tail, `VGA_STATUS`, `VGA_INTERRUPT_CONTROL`, `VGA_STATUS_CLEAR`, `VGA_INTERRUPT_STATUS`, `VGA_MAIN_CONTROL`, `VGA_TEST_CONTROL`, `VGA_QOS_CTRL`, `D3VGA_CONTROL` through `D6VGA_CONTROL`, and `VGA_SOURCE_SELECT`.
- MCIF and display writeback: `MCIF_CONTROL`, write-combine timeout, phase outstanding counters, `MCIF_WB_BUFMGR_SW_CONTROL`, buffer-manager status, buffer pitch, four buffer status/status2 groups, buffer Y/C low/high addresses, luma/chroma size, per-buffer resolution, arbitration, SCLK/NB p-state/self-refresh/clock-gater controls, VMID control, and minimum time-to-outstanding fields.
- DC perfmon blocks: complete `DC_PERFMON4` and `DC_PERFMON5` counter/control/state/value fields and the beginning of `DC_PERFMON6`.
- MMHUBBUB: writeback watermarks, warmup configuration/control/base/region, minimum TTO, memory power status/control, clock control, soft reset, DMU error status, client unit ID, and warmup VMID control.
- Azalia display audio: controller clock/DMA/RIRB/CORB/DTO/status/CRC/memory-power fields; codec root parameters and controls; global audio port connectivity; stream index/data pairs for streams 0 through 15; output endpoint index/data pairs 0 through 7; and input endpoint index/data pairs 0 through 7.
- DCHUBBUB arbitration and hub control: outstanding request limits, saturation/QoS force, DRAM self-refresh and p-state forcing, watermark sets A through D, host-VM pressure/credit/QoS fields, watermark-change handshakes, timeout controls/interrupts, global timer, surface-check addresses, VTG controls, soft reset, clock/DCFCLK controls, latency measurement, ROB overflow status, FMON, and debug index/data.
- DCHUBBUB SDPIF and VM location: SDPIF credit/status/error/snoop fields, physical request controls, forced-IO diagnostics, framebuffer/AGP/HBM address fields, local HBM lock, and SDPIF memory-power state.
- DCHUBBUB return path, DCC, CRC, DET, and compbuf: DCC constant fields for return-path slices, return-path memory-power fields, CRC control/value fields, DCC statistic fields, compbuf settings, DET controls, hub memory-power mode/status, compbuf memory-power controls, and reserved-space fields.
- DCN VM request interface: repeated `DCN_VM_CONTEXT0` through `DCN_VM_CONTEXT15` page-table depth/block-size, base address hi/lo, start logical page hi/lo, and end logical page hi/lo fields, plus default address and VM fault control/status/address fields.

## Control Flow

This header has no runtime control flow. Runtime sequencing is supplied by AMDGPU display code:

1. DCN 3.1 resource, interrupt, DMUB, hubbub, audio, writeback, and diagnostics code includes `dcn_3_1_2_offset.h` and `dcn_3_1_2_sh_mask.h`.
2. Register-list macros paste register names into offset and mask/shift symbols. Examples from the include sites include `SR(DCHUBBUB_GLOBAL_TIMER_CNTL)`, `SR(DCHUBBUB_ARB_HOSTVM_CNTL)`, `SR(DCHUBBUB_CRC_CTRL)`, `SR(AZALIA_AUDIO_DTO)`, and `MCIF_WB_COMMON_MASK_SH_LIST_DCN30`.
3. Field helper macros such as `REG_GET`, `REG_SET`, `REG_UPDATE`, `REG_UPDATE_2`, and generated `SF(...)`/`HWS_SF(...)` lists use the `__SHIFT` and `_MASK` constants to pack writes and decode reads.
4. Hardware sequencing occurs in consumers: modeset and plane programming update DCHUBBUB watermarks and clocks; DMUB reads DCN VM framebuffer base/offset fields; writeback code controls MCIF buffers; audio code programs Azalia/AFMT-facing state; IRQ paths handle status, clear, and interrupt-mask fields.

The macros do not encode ordering requirements. Consumers must still respect display clock and power domains, register access ordering, write-one-to-clear behavior, interrupt acknowledgement, watermarks and p-state handshakes, VM context programming order, and suspend/resume restore sequencing.

## State And Persistence Behavior

The chunk stores no software state and persists nothing by itself. It describes MMIO-backed GPU state. The represented hardware state includes:

- Sticky and current VGA access, display-switch, and auto-trigger status plus interrupt masks and clear bits.
- MCIF writeback buffer manager state: active/current/next buffer, software and VCE locks, overrun/overflow, buffer tags, line counters, pitch, dimensions, addresses, and address fencing.
- Memory-hub and display-hub performance state: outstanding request counters, QoS, saturation, watermark programming, self-refresh and p-state permission, clock gating, soft reset, timeout detection, ROB overflow, frame/vline snapshots, debug buses, and perf counters.
- Audio state in Azalia registers: DMA stream control, ring-buffer/CORB/RIRB behavior, cyclic-buffer position/synchronization, payload capabilities, endpoint index/data windows, codec power/reset/control fields, CRC controls/results, and memory-power state.
- DCN VM state: framebuffer aperture, AGP aperture, local HBM bounds/lock, per-VMID page-table roots and address ranges, default/fault address, VM fault status, faulting VMID/table-level/pipe, and interrupt enable/clear policy.
- DCHUBBUB return-path state: DCC configuration constants, CRC capture source and values, DCC statistics, DET/compbuf allocation and reserved-space controls, and related memory-power status.

Persistence is hardware-defined. Configuration registers typically retain values until modeset reprogramming, power gating, suspend/resume, or ASIC reset. Status, fault, debug, counter, clear, ack, and memory-power fields may be read-only, sticky, self-clearing, write-one-to-clear, or sequencing-sensitive. This generated header only states field locations; it does not identify access type or side effects.

## Dependencies And Integration Points

This chunk depends on AMD's generated DCN 3.1.2 register database and must match:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_1_2_offset.h`, which supplies the matching MMIO offsets and base indices.
- SOC15/DCN base-address definitions such as `DCN_BASE__INST0_SEG*`, used by `BASE(...)` and `REG_OFFSET(...)` helpers.
- Common DC register helper macros that consume shift/mask pairs, including `REG_GET`, `REG_SET`, `REG_UPDATE`, generated field-list macros, and DMUB register access wrappers.

Direct include sites found in this tree include:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/resource/dcn31/dcn31_resource.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/irq/dcn31/irq_service_dcn31.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dmub/src/dmub_dcn31.c`

Notable integration examples:

- `dmub_dcn31.c` includes this header and uses `REG_GET(DCN_VM_FB_LOCATION_BASE, FB_BASE, ...)` and `REG_GET(DCN_VM_FB_OFFSET, FB_OFFSET, ...)`, so the `DCN_VM_*` masks in this range directly affect DMUB framebuffer address discovery.
- `dcn31_resource.c` builds hubbub/hardware sequencer register tables around `DCHUBBUB_GLOBAL_TIMER_CNTL`, `DCHUBBUB_ARB_HOSTVM_CNTL`, `DCHUBBUB_CRC_CTRL`, `AZALIA_AUDIO_DTO`, and `AZALIA_CONTROLLER_CLOCK_GATING`, and pulls MCIF writeback shifts/masks via `MCIF_WB_COMMON_MASK_SH_LIST_DCN30`.
- `irq_service_dcn31.c` includes the same offset and mask headers so generated interrupt-source tables can bind symbolic status/enable/ack fields to the correct hardware bits.

## Risks And Edge Cases

- Field drift is the central risk. These are untyped constants; a wrong shift or mask compiles cleanly but updates or decodes the wrong bits in live hardware.
- Chunk boundaries split field groups. `D2VGA_CONTROL` is incomplete at the start, and `DC_PERFMON6_PERFMON_CNTL` continues after line 9886. File-level conclusions must be reconciled with adjacent chunks.
- Many registers contain mixed read/write and status/clear fields in the same word. Incorrect masks around `*_STATUS`, `*_CLEAR`, `*_ACK`, `*_INT_STATUS`, `ROB_OVERFLOW_CLEAR`, VM fault clear, or SDPIF error clear can lose diagnostics or leave interrupts stuck.
- Watermark, p-state, self-refresh, and host-VM fields are timing-sensitive. Bad DCHUBBUB/MMHUBBUB masks can produce underflow, stutter, p-state transition failures, self-refresh entry/exit bugs, or blanking under memory pressure.
- VM context fields are repeated for VMIDs 0 through 15 and split into high/low halves. A shifted high-page, base, start, or end field can cause display-page-table faults, wrong aperture interpretation, or failures only for specific VMIDs.
- MCIF writeback buffer fields combine ownership, lock, address, size, pitch, and interrupt state. Bad masks can corrupt captured frames, overrun buffers, wedge software/VCE ownership, or mis-handle high address bits.
- Azalia audio fields include DMA, ring-buffer, codec, endpoint index/data, CRC, and memory-power controls. Incorrect field positions can cause HDMI/DP audio loss, underrun, bad channel capability reporting, failed endpoint access, or resume-only audio failures.
- Perfmon, FMON, CRC, DCC statistic, and debug fields are diagnostic surfaces. Incorrect definitions may not break normal display output but can invalidate validation, performance tuning, or automated failure triage.

## Test Signals

Useful validation is mostly generated-header consistency plus hardware behavior:

- Build AMDGPU/DC with DCN 3.1 support enabled. Missing or renamed macros should fail in `dcn31_resource.c`, `irq_service_dcn31.c`, DMUB register code, MCIF writeback tables, hubbub tables, and audio-related tables.
- Mechanically verify shift/mask pairing for lines 7218-9886 while allowing the known boundary exceptions at the beginning and end of this chunk.
- Diff this generated range against AMD's authoritative DCN 3.1.2 register source and nearby generated headers such as later DCN 3.x variants where compatibility is expected.
- Exercise modesets across multiple pipes and display combinations while monitoring hubbub/DCHUBBUB underflow, ROB overflow, timeout, watermark-change, p-state, and self-refresh diagnostics.
- Validate writeback paths with MCIF enabled: buffer rotation, pitch/dimension programming, high/low addresses, lock ownership, interrupt acknowledgement, overrun handling, and captured-frame integrity.
- Validate HDMI/DP audio through Azalia: stream start/stop, DMA/RIRB/CORB behavior, codec power/reset, endpoint index/data access, payload capability reporting, CRC paths, suspend/resume, and underrun handling.
- Exercise VM and fault handling with display surfaces in local framebuffer, AGP/GART-style apertures, and high addresses; watch VM fault status, fault address, VMID, table-level, and pipe fields.
- Enable diagnostic captures where available: DCHUBBUB CRC, DCC statistics, FMON/perfmon counters, timeout interrupts, and debug index/data paths. The observed values should change consistently with workload and clear/ack sequences.
- Watch kernel logs and display diagnostics for stuck interrupts, underflow, audio dropouts, writeback overruns, VM faults, bad framebuffer base discovery by DMUB, resume failures, and validation mismatches in CRC/perf counters.

## Cross-Chunk Notes

Previous chunks own the beginning of the generated DCN 3.1.2 shift/mask file, including most of `D2VGA_CONTROL`. Later chunks continue `DC_PERFMON6` after `DC_PERFMON6_PERFMON_CNTL` and cover the remaining field namespace. The final per-file research document should merge adjacent chunks before making complete claims about all VGA fields, all perfmon fields, or the full `dcn_3_1_2_sh_mask.h` hardware map.
