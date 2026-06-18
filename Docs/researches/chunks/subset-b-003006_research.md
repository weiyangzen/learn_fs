# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_6_1_sh_mask.h lines 2432-4881

## Scope

This chunk is a generated AMD NBIO 6.1 register shift/mask header segment. It contains C preprocessor constants only; there are no functions, structs, variables, branches, loops, locks, allocations, or direct register accesses in this range.

The range starts in the `BIF_CFG_DEV0_EPF0_0` PCIe BAR enhanced-capability area at `PCIE_BAR5_CNTL`, continues through EPF0 power budget, dynamic power allocation, secondary PCIe, lane equalization, ACS, ATS, page request, PASID, TPH requester, multicast, LTR, ARI, SR-IOV, and AMD GPUIOV vendor-specific capability fields, then switches at the `addressBlock: nbio_nbif_bif_cfg_dev0_epf1_bifcfgdecp` marker to the `BIF_CFG_DEV0_EPF1_0` PCI configuration image. The EPF1 section covers standard PCI header fields, PM/PCIe/MSI/MSI-X/vendor/VC/serial/AER/BAR/power/DPA/secondary/lane/ACS/ATS/PRI/PASID/TPH/multicast/LTR/ARI/SR-IOV fields and ends inside the EPF1 GPUIOV `HVVM_MBOX_DW1` valid/ack mask block. Although this file sits under a local `ceph-client` source mirror, the content is AMDGPU hardware metadata and does not implement Ceph filesystem behavior.

## Purpose

The purpose of this header range is to publish bit positions and masks for NBIO 6.1 PCIe configuration-space registers. Each field is represented by a pair of macros:

- `<REGISTER>__<FIELD>__SHIFT`, the bit offset used when packing or extracting a hardware field.
- `<REGISTER>__<FIELD>_MASK`, the bit mask used to isolate, clear, preserve, or update that field.

Runtime AMDGPU code combines these constants with the matching register addresses from `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_6_1_offset.h`. Common consumers include register helpers such as `RREG32_PCIE`, `WREG32_PCIE`, `RREG32_SOC15`, `WREG32_SOC15`, `REG_GET_FIELD`, `REG_SET_FIELD`, and `SOC15_REG_OFFSET`.

## Important Macro Families

The EPF0 opening covers the tail of the BAR enhanced capability: `PCIE_BAR5_CNTL`, `PCIE_BAR6_CAP`, and `PCIE_BAR6_CNTL`. These fields describe BAR index, total BAR count, supported sizes, and selected BAR size.

EPF0 power-management and link-diagnostic extended capabilities include power budget data selection/data/capability fields, DPA substate capability/control/status and eight substate power allocation registers, secondary PCIe `LINK_CNTL3`, lane error status, and per-lane equalization controls for lanes 0 through 15. The lane equalization blocks expose downstream/upstream TX preset and RX preset hint fields.

EPF0 isolation, address-translation, and request capabilities include ACS capability/control, ATS capability/control, page request interface control/status plus outstanding request capacity/allocation, PASID capability/control, TPH requester capability/control, multicast capability/control/address/receive/blocking registers, LTR capability, and ARI capability/control. These fields describe peer-to-peer routing restrictions, address translation support, page request protocol, process address space IDs, latency tolerance, and alternative routing interpretation.

EPF0 SR-IOV and AMD GPUIOV fields define the SR-IOV enhanced-capability header, VF enable/migration/MSI memory-space enable/ARI hierarchy controls, VF counts and stride, VF device ID, supported/system page size, six VF BAR base-address registers, and migration-state array offset. The AMD vendor-specific GPUIOV block adds a capability header, VSEC header, SR-IOV shadow state, interrupt enable/status bits for GFX/UVD/VCE command completion and hang/FLR/VM-busy transitions, PF reset control, hypervisor/VM mailbox words, context location/offset/size fields, total framebuffer accounting, GPUIOV offsets, per-VF framebuffer size/offset entries for VF0 through VF15, and scheduler dwords for UVD, VCE, and GFX.

After the address-block transition, EPF1 begins with standard PCI configuration header fields: vendor/device ID, command/status, revision and class code, cache-line and latency settings, header/BIST, BARs 1-6, adapter ID, ROM base, capability pointer, interrupt line/pin, min grant, max latency, vendor capability, and writable adapter ID. The command/status masks include normal PCI enable/status semantics such as I/O space, memory space, bus master, parity, SERR, fast back-to-back, interrupt disable, capability list, and error status bits.

EPF1 PM and PCIe capability fields cover PM capability linkage, D-state and PME controls/status, PCIe capability version/device type/slot/interrupt message metadata, device capability/control/status, link capability/control/status, and Device/Link Capability 2 plus control/status fields. These masks include payload sizing, phantom functions, extended tags, endpoint L0s/L1 latency, role-based error reporting, FLR, relaxed ordering, no-snoop, max read request, error reporting enables, link speed/width, ASPM, retrain/link disable, common clock, bandwidth interrupt enables, completion timeout, ARI forwarding, atomic operations, ID-based ordering, LTR, OBFF, emergency power reduction, 10-bit tags, TLP prefix controls, and equalization status.

EPF1 interrupt and extended-capability fields include MSI capability list/message control/address/data/mask/pending registers, MSI-X capability/table/PBA registers, generic vendor-specific capability headers and payload dwords, virtual-channel capability/control/status and VC0/VC1 resource fields, device serial number, advanced error reporting uncorrectable/correctable status/mask/severity/log fields, BAR enhanced capability fields for BAR1 through BAR6, power budget and DPA fields, secondary PCIe link control/lane error/equalization controls, ACS, ATS, page request, PASID, TPH requester, multicast, LTR, ARI, SR-IOV, and the beginning of the EPF1 AMD GPUIOV block.

The EPF1 GPUIOV portion in this chunk mirrors the EPF0 capability header, VSEC header, SR-IOV shadow, interrupt enable/status, reset control, and mailbox `DW0` fields. The range then enters `HVVM_MBOX_DW1`, which assigns two bits per VF for VF0 through VF15 transmit-acknowledge and receive-valid state, but the assigned lines stop after the `VF1_RCV_VALID_MASK`; the remaining `DW1` masks and later GPUIOV context/framebuffer/scheduler fields are outside this work item.

## Control Flow

There is no executable control flow in this header. Runtime behavior occurs only in code that includes these generated constants:

1. AMDGPU code selects a register offset from `nbio_6_1_offset.h`.
2. It reads an NBIO, PCIe configuration, or SOC15 register through the AMD register access layer.
3. It extracts, composes, or updates a field using these `__SHIFT` and `_MASK` macros directly or through `REG_GET_FIELD` and `REG_SET_FIELD`.
4. It writes control state, decodes capability/status fields, polls hardware-owned status, clears sticky diagnostics, or reports PCIe/NBIO state to power-management, reset, virtualization, interrupt, display, or diagnostics code.

Direct in-tree includes of this NBIO 6.1 shift/mask header appear in `drivers/gpu/drm/amd/amdgpu/nbio_v6_1.c`, `drivers/gpu/drm/amd/amdgpu/mxgpu_ai.c`, and Vega powerplay include files such as `vega10_inc.h` and `vega12_inc.h`. Related files such as `psp_v3_1.c` and display resource code include the companion offset header for NBIO addressing.

## State And Persistence Behavior

This file stores no software state and persists nothing to disk. It describes hardware-backed PCIe configuration and extended-capability state owned by the GPU, host PCIe fabric, platform firmware, Linux PCI core policy, AMDGPU NBIO code, power-management code, and virtualization management paths.

The represented state includes BAR sizing, power budget reporting, DPA substates, secondary PCIe link control, per-lane equalization presets and lane errors, ACS routing controls, ATS/PRI/PASID translation protocol state, TPH and multicast controls, LTR and ARI capability/control state, SR-IOV VF provisioning, MSI/MSI-X interrupt programming, virtual-channel allocation, AER status/mask/severity/logs, GPUIOV interrupt status/enables, PF reset requests, hypervisor/VM mailbox handshakes, and VF framebuffer allocation metadata. Some fields are static capability descriptions, some are software-programmed controls, some are hardware-updated status, and some diagnostic fields may be sticky or write-one-to-clear in the underlying hardware. The generated masks do not encode reset defaults, access permissions, side effects, ordering constraints, or ownership boundaries.

## Dependencies And Integration Points

The primary dependency is consistency with the generated NBIO 6.1 register database:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_6_1_offset.h` supplies matching addresses such as `cfgBIF_CFG_DEV0_EPF0_0_PCIE_BAR5_CNTL`, `cfgBIF_CFG_DEV0_EPF1_0_VENDOR_ID`, and `cfgBIF_CFG_DEV0_EPF1_0_PCIE_VENDOR_SPECIFIC_HDR_GPUIOV_HVVM_MBOX_DW1`.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_6_1_default.h` supplies reset/default values for the same register generation where generated.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_6_1_smn.h` and SOC15/NBIO access helpers provide the surrounding addressing and read/write mechanics.

Integration points include NBIO v6.1 device setup, Vega10/Vega12 power-management policy, PCIe link-speed and lane-equalization management, ASPM/LTR/OBFF policy, MSI/MSI-X interrupt delivery, AER diagnostics, ACS and peer-to-peer isolation, ATS/PRI/PASID IOMMU integration, multicast routing, SR-IOV PF/VF provisioning, AMD MxGPU/GPUIOV mailbox handling, framebuffer partitioning for VFs, suspend/resume, runtime power transitions, reset/FLR paths, PSP-visible management flows, and platform PCI enumeration.

The fields overlap generic PCIe concepts that may also be managed by firmware and the Linux PCI core. Consumers must pair the correct EPF0 or EPF1 mask with the matching NBIO 6.1 offset and must respect whether firmware, the PCI core, AMDGPU, the hypervisor, or hardware owns a given field at the time it is accessed.

## Risks And Edge Cases

- The chunk boundaries are artificial. It starts after earlier EPF0 BAR and AER definitions and ends in the middle of the EPF1 `HVVM_MBOX_DW1` mask list, after `VF1_RCV_VALID_MASK`.
- These are untyped preprocessor constants. A stale shift or mask can compile cleanly while decoding or programming the wrong hardware field.
- The generated file is highly repetitive. Per-lane equalization, per-VF framebuffer, per-VF mailbox, and mirrored EPF0/EPF1 capability blocks are vulnerable to generation drift, lane-number mismatch, VF-number mismatch, or offset/mask pairing mistakes.
- PCIe control fields are interoperability-sensitive. Incorrect payload size, read request size, ASPM, retrain, target link speed, completion timeout, ARI, atomic operation, ID-based ordering, LTR, OBFF, TLP prefix, ACS, ATS, PRI, or PASID handling can cause enumeration failures, DMA ordering bugs, IOMMU faults, peer-to-peer routing failures, link instability, reset failures, or platform-specific hangs.
- MSI and MSI-X fields carry interrupt-delivery side effects. Address/data width, multiple-message enable, vector masks, pending bits, table offsets, or PBA offsets must not be modified with stale masks.
- AER status/mask/severity/log fields may be sticky or write-one-to-clear in hardware. Generic read/modify/write use can lose diagnostic evidence or leave important errors masked incorrectly.
- SR-IOV and GPUIOV registers are isolation-sensitive. VF enablement, VF memory-space enable, VF BAR base addresses, page size, migration state, mailbox handshakes, reset controls, and framebuffer partition fields affect PF/VF boundaries and hypervisor coordination.
- EPF0 and EPF1 names describe different endpoint-function configuration images. Applying a mask from one family to an offset from the other may still produce plausible bit operations while corrupting unrelated configuration state.
- GPUIOV mailbox fields are handshake state, not ordinary scratch bits. Incorrect ack/valid sequencing can stall PF/VF communication or lose virtualization events.

## Test Signals

Useful validation is mostly build-time and hardware-integration oriented:

- Build AMDGPU with NBIO 6.1/Vega support enabled; missing, renamed, or duplicate macros should surface in `nbio_v6_1.c`, `mxgpu_ai.c`, Vega powerplay includes, or generated-header include paths.
- Compare this field list against `nbio_6_1_offset.h` and `nbio_6_1_default.h` to confirm EPF0/EPF1 register names, ordering, defaults, and the address-block transition remain synchronized.
- Boot affected hardware and verify PCIe config-space exposure for EPF0 and EPF1: BAR capabilities, PM, PCIe, MSI/MSI-X, vendor-specific, VC, serial-number, AER, secondary PCIe, ACS, ATS/PRI/PASID, multicast, LTR, ARI, SR-IOV, and GPUIOV capabilities should decode consistently.
- Exercise PCIe link-speed changes, retraining, suspend/resume, runtime power, ASPM/LTR/OBFF policy, and reset/FLR paths while monitoring link width/speed, equalization completion, lane error status, and DPA/power-budget reporting.
- Use MSI/MSI-X-enabled workloads and interrupt-stress tests to catch address/data/mask, pending-bit, or multiple-message field drift.
- Use AER injection or platform diagnostics where available to verify uncorrectable/correctable status, masks, severities, first-error pointer, header logs, and TLP prefix logs.
- Validate ACS, ATS/PRI/PASID, multicast, peer-to-peer DMA, and IOMMU scenarios on systems that expose those features; isolation failures, blocked traffic, or unexpected upstream forwarding can indicate mask or ownership mistakes.
- On SR-IOV/MxGPU-capable systems, test PF and VF boot, VF BAR sizing, VF page size, VF migration state, GPUIOV interrupt status/enable bits, PF reset request, mailbox ack/valid transitions, and per-VF framebuffer partition reporting.

## Chunk Notes

- Lines 2432-3354 finish a large `BIF_CFG_DEV0_EPF0_0` capability map, starting at `PCIE_BAR5_CNTL` and ending with EPF0 GPUIOV GFX scheduler dwords.
- Line 3357 marks the transition to `addressBlock: nbio_nbif_bif_cfg_dev0_epf1_bifcfgdecp`.
- Lines 3358-4881 cover `BIF_CFG_DEV0_EPF1_0` from standard PCI identity/header fields through the first two EPF1 GPUIOV mailbox `DW1` masks.
- The assigned range ends before EPF1 `HVVM_MBOX_DW1` masks for VF2-VF15 and before later EPF1 GPUIOV context/framebuffer/scheduler definitions.
