# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_7_4_sh_mask.h lines 2435-4879

## Scope

This chunk is a generated AMDGPU NBIO 7.4 shift/mask header segment for PCIe configuration-space and AMD GPU-IOV vendor-specific fields. It contains 2,093 `#define` entries over 2,445 source lines, with 1,052 `__SHIFT` definitions and 1,073 `_MASK` definitions. The count is not a strict pair count because the chunk starts and ends inside register definitions, and because some generated hardware field names themselves contain `MASK`.

The range begins inside `BIF_CFG_DEV0_EPF0_0_DEVICE_CNTL2`, covering the remaining EPF0 PCIe Device Control 2 fields and masks. It then runs through a large EPF0 endpoint-function capability area, including MSI/MSI-X, vendor-specific and virtual-channel capabilities, AER, resizable BAR and VF BAR metadata, DPA, secondary PCIe, ACS/ATS/PASID/PRI/multicast/LTR/ARI/SR-IOV/TPH/data-link/16 GT/s PHY/lane-margining features, and AMD GPU-IOV mailbox/framebuffer/scheduler registers. The chunk then enters `addressBlock: nbio_nbif0_bif_cfg_dev0_epf1_bifcfgdecp` and covers EPF1 standard PCI/PCIe configuration fields from vendor ID through the first `BIF_CFG_DEV0_EPF1_0_DEVICE_CAP2` masks. The previous chunk is needed for the first fields of EPF0 `DEVICE_CNTL2`, and the next chunk is needed to complete EPF1 `DEVICE_CAP2` and the later EPF1 capability space.

Although this mirror lives under `sources/distributed-fs/ceph-client`, the file is AMDGPU hardware register metadata. It has no Ceph or distributed-filesystem behavior.

## Purpose

`nbio_7_4_sh_mask.h` publishes symbolic bit positions and masks for NBIO 7.4 registers. The companion `nbio_7_4_offset.h` header identifies register offsets such as `cfgBIF_CFG_DEV0_EPF0_0_DEVICE_CNTL2`, while this file identifies the individual fields inside those registers. Driver code uses these macros with AMDGPU register access helpers, `REG_SET_FIELD`/`REG_GET_FIELD` style helpers, or direct read/modify/write logic so it does not hard-code bit numbers.

This chunk's specific purpose is to describe the bit layouts for two endpoint-function regions:

- The tail of EPF0 PCIe capability and extended capability space, including virtualization and GPU-IOV fields used by PF/VF resource control.
- The beginning of EPF1 PCI configuration space and early PCIe capability fields, mirroring the standard endpoint-function configuration model for a second function.

## Important Macro Families

The EPF0 Device Control 2 and Link Capability 2 area covers completion timeout controls, ARI forwarding, atomic-op request/egress behavior, ID-based ordering, LTR enable, emergency power reduction, 10-bit tag request support, OBFF, end-to-end TLP prefix blocking, supported link speed vectors, crosslink/RTM presence support, target link speed, compliance controls, autonomous speed disable, de-emphasis, equalization status, and downstream component presence.

The MSI/MSI-X groups define capability list headers, MSI enable/multiple-message/64-bit/per-vector masking fields, MSI message address and data fields, mask and pending vectors, MSI-X table size/function mask/enable fields, table BIR/offset, and PBA BIR/offset. These fields are central to interrupt delivery and masking for the endpoint function.

The EPF0 vendor-specific, virtual-channel, serial-number, and AER groups cover VSEC headers and scratch registers, VC capability/control/status for port and VC0/VC1 resources, device serial number dwords, uncorrectable and correctable AER status/mask/severity fields, AER capability/control, header logs, and TLP prefix logs. Notable AER fields include data-link protocol, surprise down, poisoned TLP, flow-control protocol, completion timeout, completer abort, unexpected completion, unsupported request, ECRC, ACS violation, internal error, atomic-op egress blocked, and TLP prefix blocked indications.

The BAR, power, DPA, secondary PCIe, and lane-diagnostic groups include PCIe BAR enhanced capability headers, BAR1-BAR6 capability/control pairs, power budget selection/data/capability fields, DPA capability/latency/status/control and eight substate power-allocation registers, link control 3, lane error status, and lane 0-15 equalization controls. These fields describe BAR sizing, active BAR size selection, power budget encoding, dynamic power substate support, and per-lane equalization presets/cursors.

The isolation and address-translation groups cover ACS, ATS, Page Request Interface, PASID, multicast, LTR, ARI, SR-IOV, TPH requester, and Data Link Feature capabilities. These fields expose source validation, translation blocking, request/completion redirection, upstream forwarding, egress control, ATS invalidate queue depth, PRI enable/reset/status, PASID execution/privileged/no-privileged mode support, multicast receive/block masks, LTR snoop/no-snoop latencies, ARI next-function/grouping, SR-IOV VF enable/count/stride/device/page-size/VF BAR fields, TPH steering modes, and data-link feature exchange support.

The 16 GT/s PHY and lane-margining blocks define enhanced capability headers, 16 GT/s link capability/control/status, local and RTM parity mismatch status, lane 0-15 equalization controls, margining port capability/status, and lane 0-15 margining control/status pairs. These fields are highly repetitive and lane-indexed; they are used for high-speed link training diagnostics and margining request/result payloads.

The VF resizable BAR and AMD GPU-IOV vendor-specific section is the largest EPF0 vendor area in this chunk. It covers VF BAR1-BAR6 capability/control fields, a GPUIOV VSEC header, SR-IOV shadow state, interrupt enable/status bits, reset control, HVVM mailbox dwords, context/total-framebuffer/offset fields, P2P-over-XGMI enable bits, `VF0_FB` through `VF30_FB` size/offset pairs, and repeated scheduler dwords for UVD, VCE, GFX, and UVD1 engines. Scheduler fields include mode, command buffer address/size, queue pointers, doorbell offsets, context save area address/size, engine IDs, VF counts, timing windows, flags, and status/control payloads.

The EPF1 section starts at `addressBlock: nbio_nbif0_bif_cfg_dev0_epf1_bifcfgdecp`. It covers vendor/device ID, command/status, revision/interface/subclass/base-class bytes, cache-line/latency/header/BIST fields, BAR1-BAR6, adapter ID, ROM BAR, capability pointer, interrupt line/pin, min grant/max latency, vendor capability list, writable adapter ID, PM capability and PM status/control, PCIe capability header, device capability/control/status, link capability/control/status, and the beginning of Device Capability 2.

## APIs, Types, And Functions

There are no callable APIs, C types, functions, variables, locks, allocations, or executable statements in this range. The public interface is the generated preprocessor namespace:

- `BIF_CFG_DEV0_EPF0_0_<REGISTER>__<FIELD>__SHIFT` and `BIF_CFG_DEV0_EPF0_0_<REGISTER>__<FIELD>_MASK` describe EPF0 fields.
- `BIF_CFG_DEV0_EPF1_0_<REGISTER>__<FIELD>__SHIFT` and `BIF_CFG_DEV0_EPF1_0_<REGISTER>__<FIELD>_MASK` describe EPF1 fields.
- Hardware fields named `MASK` naturally produce generated macro names like `*_MASK_MASK`; these are valid names and should not be normalized by hand.

The macro values are only field geometry. They do not encode access width, reset value, read/write permissions, write-one-to-clear behavior, firmware ownership, or ordering requirements.

## Control Flow

This header has no local runtime control flow. The runtime pattern is external:

1. AMDGPU code selects an NBIO 7.4 register for the active ASIC and endpoint function.
2. `nbio_7_4_offset.h` supplies the register offset or config-space address, such as EPF0 `DEVICE_CNTL2` at `cfgBIF_CFG_DEV0_EPF0_0_DEVICE_CNTL2`.
3. This shift/mask header supplies the bit location for a field extraction, comparison, or read/modify/write update.
4. Access happens through AMDGPU MMIO, SMN, or PCIe config access helpers outside this header.

The direct NBIO 7.4 implementation file, `drivers/gpu/drm/amd/amdgpu/nbio_v7_4.c`, includes both `nbio/nbio_7_4_offset.h` and `nbio/nbio_7_4_sh_mask.h`. That implementation handles NBIO revision reads, memory-controller access gating, doorbell ranges, interrupt control, RAS paths, ASPM/LTR programming, and register remapping. For example, the NBIO 7.4 ASPM/LTR path uses the EPF0 Device Control 2 LTR enable bit through a local SMN alias and mask, which corresponds semantically to the `BIF_CFG_DEV0_EPF0_0_DEVICE_CNTL2__LTR_EN` field in this generated file.

## State And Persistence Behavior

The header itself stores no software state and persists nothing. It describes hardware-visible PCIe configuration and AMD vendor-specific NBIO state.

State represented by this chunk includes PCIe link and device control, MSI/MSI-X programming and pending/mask bits, VC negotiation state, AER status/mask/severity/logs, BAR and VF BAR sizing, DPA and power-budget data, lane equalization and margining results, ACS/ATS/PASID/PRI/SR-IOV enablement, LTR latency values, ARI function grouping, TPH requester configuration, Data Link Feature exchange status, GPUIOV interrupts, GPUIOV mailbox valid/ack payloads, PF/VF reset state, framebuffer allocation per VF, P2P-over-XGMI enables, and per-engine scheduler state.

Persistence depends on hardware and platform events: PCI conventional reset, hot reset, function-level reset, SR-IOV enable/disable, suspend/resume, power-gating, firmware or hypervisor ownership, and explicit driver writes. Fields named `STATUS`, `ERR_STATUS`, `PENDING`, `MASK`, `INTR_STATUS`, `TRN_ACK`, `RCV_VALID`, or `RESET_CONTROL` should be assumed to have side effects or latching semantics until the programming guide or caller code proves otherwise.

## Dependencies And Integration Points

This generated file depends on AMD's NBIO 7.4 register database and must stay synchronized with `nbio_7_4_offset.h`. The offset header supplies matching `cfgBIF_CFG_DEV0_EPF0_0_*` and `cfgBIF_CFG_DEV0_EPF1_0_*` offsets, including the EPF0 GPUIOV register window and the EPF1 block beginning at `cfgBIF_CFG_DEV0_EPF1_0_VENDOR_ID`.

Source-tree consumers include `amdgpu/nbio_v7_4.c`, power management code such as the Vega20 and SMU PPT paths, display code that includes NBIO 7.4 offsets, PSP code, and SOC discovery setup that installs `nbio_v7_4_funcs` and `nbio_v7_4_ras`. The protocol-level dependencies are the PCI and PCI Express specifications plus AMD-specific NBIO, GPU-IOV, SR-IOV, mailbox, scheduler, and XGMI virtualization contracts.

Major integration areas are PCIe enumeration and capability handling, BAR and VF BAR sizing, MSI/MSI-X interrupt delivery, AER/RAS reporting, ASPM and LTR power management, link training and lane diagnostics, ACS/ATS/PASID/PRI/IOMMU-aware DMA flows, SR-IOV and VF provisioning, GPUIOV PF/VF mailbox exchange, framebuffer partitioning, scheduler setup for virtualized engines, reset/recovery, and debug or register-dump tooling.

## Risks And Edge Cases

- The chunk starts inside EPF0 `DEVICE_CNTL2` and ends inside EPF1 `DEVICE_CAP2`; adjacent chunks are required for a complete per-register and per-file view.
- Generated header drift can compile cleanly while programming the wrong bit, especially in dense fields such as AER severity/masks, ACS controls, SR-IOV state, MSI/MSI-X masks, LTR/ASPM controls, and GPUIOV mailbox bits.
- EPF0 and EPF1 names are similar but target different endpoint functions. Applying an EPF0 mask to an EPF1 offset, or vice versa, can silently corrupt the wrong function's configuration.
- Repeated lane, VF, BAR, and scheduler blocks are susceptible to mechanical review errors. Lane number, VF index, engine family, and BAR index are often the only visible differences across many definitions.
- Full-width masks such as `0xFFFFFFFFL` describe field coverage, not permission to write all bits as one. Reserved or log fields may have hardware-defined clear or sticky behavior.
- AER, MSI pending, interrupt status, mailbox, and error-log fields can be sticky, write-one-to-clear, read-sensitive, or owned by firmware/hypervisor logic. Generic read/modify/write code can drop diagnostic evidence or break a handshake.
- ACS, ATS, PASID, PRI, multicast, and SR-IOV fields affect DMA isolation and address translation. Incorrect masks can become security, IOMMU fault, or peer-to-peer routing issues.
- Link equalization, 16 GT/s PHY, and margining fields are timing-sensitive. Incorrect lane masks can produce intermittent link training or signal integrity failures isolated to one lane.
- GPUIOV framebuffer and scheduler fields encode virtualization resource contracts. Wrong size/offset, doorbell, queue pointer, or engine assignment fields can affect only one VF or one media/graphics engine, making failures hard to correlate.

## Test Signals

Useful validation signals for this chunk are:

- Build coverage for AMDGPU translation units that include `nbio/nbio_7_4_sh_mask.h`, especially `amdgpu/nbio_v7_4.c`, Vega20/SMU power-management files, and display/PSP users that depend on NBIO 7.4 headers.
- Mechanical cross-checks that every `BIF_CFG_DEV0_EPF0_0_*` and `BIF_CFG_DEV0_EPF1_0_*` register family in this chunk has a matching `cfg...` definition in `nbio_7_4_offset.h`.
- Generated-header comparison against AMD's authoritative NBIO 7.4 register database, with extra focus on repeated lane 0-15, VF0-VF30, BAR1-BAR6, and scheduler DW0-DW8 patterns.
- Static validation that each field mask is plausible for its shift and width, that reserved/full-width fields remain intentional, and that generated `*_MASK_MASK` names are preserved.
- Hardware or simulator checks that PCIe capability decoding matches `lspci -vvxxx`-style observations for MSI/MSI-X, link capability/control/status, Device Capability 2, AER, ACS, ATS, PASID, PRI, LTR, ARI, SR-IOV, TPH, and Data Link Feature fields.
- Interrupt tests covering MSI/MSI-X address/data/mask/pending behavior and GPUIOV interrupt enable/status bits.
- Link-training diagnostics on NBIO 7.4 hardware for 8 GT/s and 16 GT/s equalization, parity mismatch reporting, lane error status, and lane margining request/status fields.
- Error injection or RAS observation that verifies AER status/mask/severity, header logs, TLP prefix logs, and source decoding are not mis-shifted.
- Virtualization tests that enable/disable SR-IOV, verify VF counts/strides/page sizes/VF BAR sizing, exercise GPUIOV mailbox valid/ack flows, validate framebuffer partition reporting for VF0-VF30, and confirm UVD/VCE/GFX/UVD1 scheduler state per VF.
- Power-management tests around ASPM, LTR, DPA, PM capability/status, suspend/resume, and reset/FLR paths to ensure field programming survives or is restored according to platform policy.

## Merge Notes

The final per-file report should merge this chunk with adjacent `nbio_7_4_sh_mask.h` chunks. This range should not be presented as owning the full EPF0 `DEVICE_CNTL2` register or the full EPF1 `DEVICE_CAP2` register because both cross chunk boundaries.
