# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_7_2_0_sh_mask.h lines 51181-53621

## Scope

This chunk is a generated AMDGPU NBIO 7.2.0 shift/mask header segment. It contains 2,092 `#define` macros over 2,441 source lines, organized by 347 register-comment blocks. The macros describe bit positions (`__SHIFT`) and field masks (`_MASK`) for PCIe configuration and AMD GPU-IOV vendor-specific registers under the NBIO/BIF device-0 endpoint-function namespace.

The range starts inside the `BIF_CFG_DEV0_EPF0_0_PCIE_VC0_RESOURCE_CAP` field list, then covers the rest of the EPF0 PCIe extended-capability and GPU-IOV field definitions through many scheduling and framebuffer-allocation registers. It then begins the `addressBlock: nbio_nbif0_bif_cfg_dev0_epf1_bifcfgdecp` region and covers EPF1 standard PCI/PCIe configuration fields through the first fields of `BIF_CFG_DEV0_EPF1_0_PCIE_VC_ENH_CAP_LIST`. The EPF0 VC0 resource-capability opening is completed by the previous chunk, and the EPF1 VC enhanced-capability block continues in the next chunk.

Although this source mirror sits under `sources/distributed-fs/ceph-client`, this header is AMDGPU hardware register metadata and has no direct Ceph or distributed-filesystem behavior.

## Purpose

`nbio_7_2_0_sh_mask.h` gives driver code symbolic bit layouts for NBIO 7.2.0 registers. The companion offset header identifies the target register; this file identifies which bits inside that register carry each hardware field. Consumers use these macros with AMDGPU register access helpers, generated `REG_SET_FIELD`/`REG_GET_FIELD` style macros, or hand-written read/modify/write code to isolate fields without hard-coding numeric bit positions.

This chunk's purpose is to describe PCIe endpoint-function configuration for EPF0 and EPF1. It includes virtual channel negotiation, PCIe serial number and AER reporting, resizable BAR and VF resizable BAR metadata, dynamic power allocation, secondary PCIe/lane equalization, ACS/ATS/PASID/page-request/multicast/ARI/SR-IOV/LTR/TPH/data-link/16 GT/s PHY/margining capabilities, and AMD-specific GPU-IOV control, mailbox, interrupt, reset, framebuffer-partition, and engine-scheduler fields.

## Important Macro Families

The opening EPF0 virtual-channel section covers `PCIE_VC0_RESOURCE_CNTL`, `PCIE_VC0_RESOURCE_STATUS`, `PCIE_VC1_RESOURCE_CAP`, `PCIE_VC1_RESOURCE_CNTL`, and `PCIE_VC1_RESOURCE_STATUS`. Fields map traffic classes to virtual channels, select and load port arbitration tables, set VC IDs/enables, and expose VC negotiation or arbitration-table status.

The EPF0 serial-number and AER section defines enhanced capability list headers, serial-number low/high dwords, uncorrectable error status/mask/severity, correctable error status/mask, AER capability/control, header logs, and TLP prefix logs. Notable fields include DLP, surprise-down, poisoned/completion/timeout/unsupported-request, ACS violation, internal error, atomic-op egress blocked, TLP prefix blocked, receiver/bad-TLP/bad-DLLP/replay-timer/advisory errors, first-error pointer, ECRC generation/check capability/enables, multiple-header recording, and prefix log present bits.

The EPF0 BAR, power, and DPA groups cover PCIe BAR enhanced capability list fields, BAR1-BAR6 capability/control pairs, power-budget data select/data/capability fields, DPA capability/latency/status/control fields, and eight DPA substate power-allocation registers. These macros describe supported BAR sizes, BAR index/size selectors, power budget bases/data/scales/PM-state/type, transition latency fields, DPA enable/substate controls, and per-substate power allocation.

The EPF0 secondary PCIe and lane-equalization groups cover link control 3, lane error status, lane 0-15 equalization controls, 16 GT/s enhanced capability/list/control/status/parity fields, lane 0-15 16 GT/s presets, and lane 0-15 margining control/status pairs. These fields expose link equalization requests, preset and cursor values, per-lane error bits, 8 GT/s and 16 GT/s equalization phase results, parity mismatch status, margining readiness, lane receiver numbers, margin types, usage models, and margin payload/status data.

The EPF0 isolation, address-translation, and requestor-capability groups cover ACS, ATS, Page Request Interface, PASID, multicast, LTR, ARI, SR-IOV, TPH requestor, data-link feature, and VF resizable BAR fields. They include control/capability bits for source validation, translation blocking, P2P redirection/completion, upstream forwarding, direct translated P2P, address-translation invalidate queue depth, page-request enable/reset/status, outstanding page request capacity/allocation, PASID execution/privileged/no-privilege modes, multicast windows and block masks, max snoop/no-snoop latency values, ARI next function/grouping, SR-IOV VF enable/migration/MSE/ARI/capability/status/count/stride/device/page-size/VF BAR fields, TPH steering mode and ST table location/size, data-link feature exchange, and VF BAR size support/control.

The EPF0 AMD GPU-IOV vendor-specific section is the largest local block. It defines a GPUIOV enhanced capability header, VSEC header, SR-IOV shadow fields, interrupt enable/status bits for GFX/UVD/UVD1/VCE command completion, hang self-recovery, hang-needs-FLR, VM-busy transition, and HVVM mailbox events, a soft PF FLR reset-control bit, HVVM mailbox dwords, context and framebuffer accounting fields, scheduler offset fields, region fields, P2P-over-XGMI enable bits for VF/PF, and repeated `VF0_FB` through `VF30_FB` size/offset pairs.

The EPF0 scheduler windows define repeated dword fields for UVD, VCE, GFX, and UVD1 scheduling contexts. Their fields describe scheduler modes, command buffer base/size, queue write/read pointers, doorbell offsets, context-save area base/size, doorbell and engine-id assignments, VF counts, timing fields such as timeslice/period/reschedule rate, flags for force-reset or engine idle, and per-engine status/control payloads. These are mechanically repeated for `UVDSCH_DW0..DW8`, `VCESCH_DW0..DW8`, `GFXSCH_DW0..DW8`, and `UVD1SCH_DW0..DW8`.

The EPF1 standard PCI configuration section starts at `addressBlock: nbio_nbif0_bif_cfg_dev0_epf1_bifcfgdecp`. It covers vendor/device IDs, command/status, revision/class/interface, cache-line/latency/header/BIST, BAR1-BAR6, CardBus CIS pointer, subsystem adapter ID, ROM BAR, capability pointer, interrupt line/pin, min grant/max latency, vendor capability list, writable adapter ID, power-management capability/status/control, PCIe capability, device capability/control/status, link capability/control/status, PCIe capability 2 fields, MSI and MSI-X capability fields, vendor-specific capability scratch registers, and the beginning of the VC enhanced capability list.

## APIs, Types, And Functions

There are no callable APIs, C types, functions, variables, allocations, locks, or executable statements in this chunk. Its public interface is the preprocessor macro namespace:

- `<REGISTER>__<FIELD>__SHIFT` macros give the low-bit position for a field.
- `<REGISTER>__<FIELD>_MASK` macros give the raw register mask for that field.
- Register names are scoped mainly under `BIF_CFG_DEV0_EPF0_0_*` and `BIF_CFG_DEV0_EPF1_0_*`.

Consumers must pair these macros with `nbio_7_2_0_offset.h` register offsets and, where available, default/reset metadata. This file alone does not encode access size, read/write permissions, reset values, write-one-to-clear behavior, firmware ownership, or sequencing requirements.

## Control Flow

This header has no local runtime control flow. Runtime use is external and usually follows this pattern:

1. AMDGPU code chooses the NBIO 7.2.0 register for the active ASIC and endpoint function.
2. The offset header supplies the register address/base-index selection.
3. This shift/mask header supplies the field location for a read, write, or read/modify/write.
4. Hardware interprets the resulting register access as PCIe configuration, capability negotiation, error reporting, virtualization control, interrupt/messaging, reset, framebuffer partitioning, or scheduler configuration.

The implied hardware flows include PCIe capability walking, AER capture and masking, virtual-channel negotiation, BAR sizing, DPA and power-budget reporting, link equalization and margining, SR-IOV enablement and VF resource sizing, ATS/PASID/page-request setup, MSI/MSI-X programming, GPU-IOV host-to-VF mailbox handshakes, PF/VF reset signaling, virtual-function framebuffer assignment, and engine scheduler provisioning.

## State And Persistence Behavior

The header owns no software state and persists nothing. It describes fields in hardware-visible PCIe configuration space and AMD vendor-specific NBIO registers.

State represented by this chunk includes PCI command/status bits, power-management state, PCIe link/device capability and status, AER latched status and logs, VC negotiation state, BAR/VF BAR sizing, DPA substate selection, lane equalization and margining results, ACS/ATS/PASID/Page Request enablement, SR-IOV VF counts and offsets, MSI/MSI-X address/data/mask/pending state, GPUIOV interrupt status/enables, mailbox transmit/receive validity/ack bits, PF/VF framebuffer size/offset allocations, and per-engine scheduler register payloads.

Persistence depends on PCI reset type, function-level reset, hot reset, power gating, firmware/BIOS initialization, SR-IOV enable/disable transitions, PSP/SMU or hypervisor ownership, suspend/resume restore, and explicit driver writes. Field names such as `*_STATUS`, `*_ERR_STATUS`, `*_MASK`, `*_PENDING`, `*_TRN_ACK`, `*_RCV_VALID`, and `*_SOFT_PF_FLR` indicate latched, masking, handshake, or reset-related behavior, but the header does not define side effects or clear semantics.

## Dependencies And Integration Points

This generated file depends on AMD's NBIO 7.2.0 register database and must remain synchronized with sibling generated headers for offsets and defaults. It is integrated through AMDGPU ASIC register include paths under `drivers/gpu/drm/amd/include/asic_reg/nbio`.

Primary integration points are AMDGPU NBIO/PCIe initialization, Linux PCI enumeration and capability handling, BAR and VF BAR resource sizing, MSI/MSI-X setup, AER/RAS reporting, GPU reset and FLR paths, runtime power management, SR-IOV/GPU virtualization setup, ATS/PASID/page-request flows used by IOMMU-aware paths, link training and lane diagnostics, and debug/diagnostic code that samples PCIe or GPUIOV state.

The GPUIOV fields are also integration points with hypervisor-facing or virtualization-management logic. Mailbox, framebuffer allocation, scheduler, and interrupt/status fields must align with firmware and virtualization contracts outside this header. The EPF1 PCIe fields mirror EPF0 standard configuration concepts but target a different endpoint function, so call sites must keep function selection and field namespace consistent.

## Risks And Edge Cases

- Generated shift/mask drift can compile cleanly while causing field extraction or updates to hit the wrong bits, producing subtle PCIe, interrupt, reset, or virtualization failures.
- The chunk starts and ends mid-register-family. The previous chunk is needed for the beginning of `BIF_CFG_DEV0_EPF0_0_PCIE_VC0_RESOURCE_CAP`, and the next chunk is needed to complete `BIF_CFG_DEV0_EPF1_0_PCIE_VC_ENH_CAP_LIST`.
- Many PCIe registers pack multiple independent fields into one dword. Read/modify/write callers must preserve adjacent fields and avoid applying EPF0 masks to EPF1 registers or vice versa.
- Status and error fields may be write-one-to-clear, sticky, latched, or read-sensitive in hardware. The shift/mask header does not identify those semantics, so generic updates can lose diagnostic evidence.
- Link equalization, 16 GT/s, and margining fields are timing-sensitive and lane-indexed. Incorrect masks can make only some lanes fail, producing intermittent training or signal-integrity symptoms.
- ACS, ATS, PASID, PRI, SR-IOV, and multicast controls affect DMA isolation and address translation. Bad values can become security/isolation bugs, IOMMU faults, or peer-to-peer routing failures.
- GPUIOV mailbox and interrupt fields are handshake-heavy. Missing an ack/valid bit, using the wrong VF index, or clearing a shared interrupt bit can deadlock PF/VF communication or hide recovery events.
- GPUIOV framebuffer and scheduler fields are repeated across many VFs and engines. Mechanical copy/paste mistakes are hard to spot and may affect only a single VF, engine, or scheduler mode.
- MSI/MSI-X fields include address, data, masking, pending, table, and PBA fields. Bad masks can cause lost interrupts or interrupt storms while leaving normal MMIO paths apparently healthy.

## Test Signals

- Build AMDGPU code paths that include NBIO 7.2.0 headers; compile coverage catches missing or malformed macro names used by consumers.
- Run generated-header consistency checks against `nbio_7_2_0_offset.h`: every register field family in this chunk should map to a corresponding register offset, and repeated EPF0/EPF1 standard PCIe field layouts should stay aligned where the hardware model expects them to match.
- Cross-check shift/mask pairs mechanically: each field should have a plausible mask for its shift and width, repeated lane/VF/scheduler families should have consistent naming and bit layouts, and capability-list header fields should retain the common `CAP_ID`, `CAP_VER`, and `NEXT_PTR` pattern.
- On supported hardware, validate PCIe enumeration, BAR sizing, MSI/MSI-X delivery and masking, AER capture/masking, link speed/width negotiation, 8 GT/s and 16 GT/s equalization status, and lane margining diagnostics.
- Exercise reset and recovery paths: FLR initiation/status, soft PF FLR, hot reset, suspend/resume, and post-reset restoration should leave PCIe configuration and GPUIOV status coherent.
- For virtualization-enabled configurations, validate SR-IOV enable/disable, VF counts/strides/page sizes, VF BAR sizing, GPUIOV mailbox handshakes, GPUIOV interrupt status/enables, framebuffer partition reporting, P2P-over-XGMI enablement, and scheduler state for GFX/UVD/UVD1/VCE engines.
- For IOMMU-aware paths, validate ACS, ATS, PASID, and page-request behavior under DMA and page-fault traffic, including fault handling and teardown.
- For diagnostics, compare sampled AER, lane, mailbox, MSI pending, and scheduler status fields against hardware events to ensure no status is accidentally masked, misdecoded, or cleared too early.
