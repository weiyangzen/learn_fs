# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_7_4_sh_mask.h lines 29368-31801

## Scope

This chunk covers generated shift and mask macros for a portion of the AMD NBIO 7.4 register bitfield header. It starts in the middle of the `BIF_CFG_DEV0_EPF1_0_PCIE_VC1_RESOURCE_CNTL` field set and continues through:

- EPF1 PCIe extended capability fields: device serial number, Advanced Error Reporting, Resizable BAR, power budgeting, Dynamic Power Allocation, secondary PCIe, ACS, ATS, Page Request Interface, PASID, Multicast, LTR, ARI, SR-IOV, TPH requester, Data Link Feature, 16 GT/s PHY, margining, and VF Resizable BAR capabilities.
- A GPU IOV vendor-specific PCIe capability block for EPF1, including SR-IOV shadow state, interrupt enable/status bits, PF reset control, hypervisor/VF mailbox registers, VF framebuffer partition fields, P2P-over-XGMI enablement, and scheduler data windows for UVD, VCE, GFX, and UVD1 engines.
- The beginning of the `nbio_nbif0_bif_cfg_dev0_epf0_vf0_bifcfgdecp` address block, covering the standard PCI configuration header and PCIe/MSI/MSI-X/VSEC/AER fields for `BIF_CFG_DEV0_EPF0_VF0_0` through the start of its uncorrectable error severity fields.

The file is generated hardware metadata. This range defines preprocessor constants only: there are no C functions, structs, global variables, or executable branches in the chunk.

## Purpose

The purpose of this header section is to provide the bit-level ABI for NBIO 7.4 PCIe configuration-space and vendor-specific registers. Each field appears in the normal AMD register-header form:

- `<REGISTER>__<FIELD>__SHIFT`, the bit offset of the field.
- `<REGISTER>__<FIELD>_MASK`, the mask used to extract or compose the field.

Driver code pairs these definitions with register addresses from `nbio_7_4_offset.h` and with AMDGPU register helpers such as `REG_SET_FIELD`, `REG_GET_FIELD`, `RREG32_SOC15`, `WREG32_SOC15`, indirect PCI config access helpers, or SR-IOV-specific PF/VF register accessors. The macros let code refer to PCIe capability fields symbolically rather than hard-coding bit positions.

## Important Macro Families

### EPF1 PCIe Capability and Error Reporting Fields

The first part of the chunk completes EPF1 virtual-channel resource control/status fields, including traffic-class to virtual-channel mapping, port arbitration table load/status, VC ID, VC enable, and negotiation-pending state.

The AER block defines fields for uncorrectable error status, masks, and severity; correctable error status and masks; Advanced Error Capability/Control; header logs; and TLP prefix logs. The covered uncorrectable errors include DLP, surprise down, poisoned TLP, flow-control, completion timeout/abort, unexpected completion, receiver overflow, malformed TLP, ECRC, unsupported request, ACS violation, internal errors, MC blocked TLP, atomic operation egress blocked, and TLP prefix blocked. Correctable fields include receiver error, bad TLP/DLLP, replay rollover, replay timeout, advisory non-fatal, internal correctable error, and header-log overflow.

These macros are important for diagnostics, error masking, severity classification, and kernel AER integration. They describe which bits are status, mask, or severity bits, but the header does not encode clear semantics or ordering.

### BAR, Power, DPA, Link, and Lane Training Fields

The EPF1 extended capability portion includes:

- Device serial number high/low dwords and capability-list headers.
- Resizable BAR capability/control registers for BAR1 through BAR6, exposing supported sizes, BAR index, total BAR count, and selected BAR size.
- Power Budgeting fields for selected data, power budget values, scale, PM sub-state, type, power rail, and system allocation support.
- Dynamic Power Allocation fields for transition latency indicators, substate mask/status/control, and substate power allocations 0 through 7.
- Secondary PCIe capability fields for target link speed and link equalization request.
- Per-lane equalization control for lanes 0 through 15, with downstream/upstream TX presets and RX preset hints.

These fields back PCIe link training, power reporting, and BAR sizing behavior exposed to the OS or configured by firmware/driver policy.

### ACS, ATS, PRI, PASID, MC, LTR, ARI, and SR-IOV

The chunk describes several PCIe capabilities that matter for IOMMU, peer-to-peer routing, and virtualization:

- ACS capability/control fields cover source validation, translation blocking, P2P request/completion redirect, upstream forwarding, P2P egress control, direct translated P2P, and egress vector size.
- ATS fields expose invalidate queue depth, page-aligned/global invalidate support, smallest translation unit, and ATC enable.
- PRI fields expose PRI enable/reset, response failure, unexpected page-request group index, stopped state, PASID-required response state, outstanding page-request capacity, and allocation.
- PASID fields expose execute permission support, privileged-mode support, maximum PASID width, and enable bits.
- Multicast fields expose group count, window size requirement, ECRC regeneration support, receive/block bitmaps, and block-untranslated bitmaps.
- LTR fields expose snooped and non-snooped maximum latency values and scales.
- ARI fields expose function-group capabilities, next function number, enable bits, and function group selection.
- SR-IOV fields expose migration support, ARI hierarchy preservation, VF ten-bit tag support, VF enable, VF MSE, migration interrupt enable/status, initial/total/active VF counts, function dependency link, first VF offset, VF stride, VF device ID, supported/system page size, six VF BAR base registers, and migration state array offset/BIR.

These macros are consumed by PF-side setup, virtualization flows, and PCI core interactions. They are especially sensitive because they help define isolation boundaries, address translation behavior, and how VF configuration space is presented.

### TPH, Data Link Feature, 16 GT/s PHY, and Margining

The TPH requester capability fields include no-ST mode, interrupt/vector mode, device-specific mode support, extended TPH requester support, ST table location/size, ST mode selection, and requester enable.

The Data Link Feature capability/status fields expose local feature support bits and remote feature support/valid bits for scaled flow control and the data link feature exchange path.

The 16 GT/s PHY capability group includes equalization bypass, modified TS usage, retimer presence flags, 10-bit tag completeness, 16 GT/s data-rate signaling enablement, equalization complete/phase-success status, link-down reason, local and retimer parity mismatch status, and per-lane 16 GT/s downstream/upstream EQ control for lanes 0 through 15.

The margining block exposes port capability/status plus lane margining control/status for lanes 0 through 15. Each lane has receiver number, margin type, usage model, and payload fields, with matching status fields. These fields are integration points for PCIe signal-integrity diagnostics and link qualification rather than normal data-path programming.

### VF Resizable BAR and GPUIOV Vendor-Specific Capability

The VF Resizable BAR capability covers VF BAR1 through VF BAR6 supported sizes and selected sizes. This mirrors the PF BAR sizing concepts but applies to VF BAR windows.

The `BIF_CFG_DEV0_EPF1_0_PCIE_VENDOR_SPECIFIC_*_GPUIOV` block is AMD-specific virtualization surface:

- Capability-list and VSEC header fields expose capability ID, version, next pointer, VSEC ID, revision, and VSEC length.
- `SRIOV_SHADOW` exposes shadowed `VF_EN` and `VF_NUM`.
- Interrupt enable/status fields cover GFX, UVD, UVD1, and VCE command-complete, self-recovered hang, hang requiring FLR, and VM-busy transition events, plus hypervisor/VF mailbox transmit-ack and receive-valid events.
- `RESET_CONTROL` provides `SOFT_PF_FLR`.
- `HVVM_MBOX_DW0` through `DW2` define a PF/hypervisor and VF mailbox: VF index, transmit data/valid, receive data/ack, and per-VF transmit-ack/receive-valid bits for VF0 through VF31.
- `CONTEXT`, `TOTAL_FB`, `OFFSETS`, `P2P_OVER_XGMI_ENABLE`, and `VF0_FB` through `VF30_FB` describe VF context size/location, total framebuffer size, offset granularity, P2P-over-XGMI enablement, and per-VF framebuffer size/offset pairs.
- Scheduler dword windows for `UVDSCH`, `VCESCH`, `GFXSCH`, and `UVD1SCH` expose opaque 32-bit scheduler payload slots.

This block is one of the highest-risk areas in the chunk because it controls PF/VF coordination, partition metadata, mailbox signaling, engine scheduling metadata, and reset behavior for GPU virtualization.

### EPF0 VF0 PCI Configuration-Space Fields

Near line 31244 the chunk starts the `BIF_CFG_DEV0_EPF0_VF0_0` address block. It defines field masks for a VF's conventional PCI configuration header and the first capability structures:

- Vendor/device ID, command, status, revision/interface/class, cache line, latency, header type, BIST, BAR1 through BAR6, adapter ID, ROM base, capability pointer, interrupt line, and interrupt pin.
- PCIe capability list, PCIe capability register, device capability/control/status, link capability/control/status, device capability/control/status 2, link capability/control/status 2, and reserved slot capability/control/status 2 fields.
- MSI and MSI-X capability list/control/address/data/mask/pending/table/PBA fields.
- Vendor-specific capability header and scratch fields.
- The beginning of AER for VF0, including uncorrectable error status, mask, and the start of severity definitions.

This mirrors much of the EPF1 capability layout but is scoped to `EPF0_VF0_0`, the first virtual function under endpoint function 0.

## Control Flow and State Behavior

This header has no runtime control flow. It affects compiled driver behavior by defining how C code packs and unpacks 16-bit and 32-bit PCIe configuration register values.

The state represented by these macros lives in hardware configuration space or NBIO-side register windows. Some fields are persistent configuration bits, such as BAR sizes, ACS/ATS/PASID/SR-IOV enables, MSI/MSI-X enables, link controls, and interrupt masks. Others are status or diagnostic fields, such as AER status, link status, data link feature status, lane error status, equalization status, margining status, GPUIOV interrupt status, mailbox ack/valid state, and VF migration status. Some are command-like or reset-oriented fields, such as PRI reset, link equalization request, `SOFT_PF_FLR`, and mailbox valid/ack bits.

The macros do not describe sequencing. Users must follow the PCIe specification, AMDGPU PF/VF ownership rules, and the code paths that own the relevant capability. For example, enabling ATS/PASID/PRI is only useful when the IOMMU and driver memory-management paths are ready; SR-IOV VF enablement must be coordinated with BAR sizing and VF framebuffer partitioning; GPUIOV mailbox bits require valid/ack handshakes; and AER status handling requires the correct clear/mask semantics.

## Dependencies and Integration Points

This chunk depends on the generated AMD register-header set:

- `nbio_7_4_offset.h` supplies addresses such as `cfgBIF_CFG_DEV0_EPF1_0_PCIE_SRIOV_CONTROL`, `cfgBIF_CFG_DEV0_EPF1_0_PCIE_VENDOR_SPECIFIC_HDR_GPUIOV`, and the surrounding `cfgBIF_CFG_DEV0_EPF0_VF0_0_*` registers.
- `nbio_7_4_default.h`, where present, supplies reset/default values for corresponding NBIO registers.
- AMDGPU SOC15 and PCI config access helpers consume these `__SHIFT` and `_MASK` macros through `REG_SET_FIELD`, `REG_GET_FIELD`, and related helpers.

Important integration points include:

- AMDGPU NBIO initialization and reset code, which includes NBIO generation-specific offset/mask headers to program PCIe, doorbell, interrupt, and power-management-facing registers.
- AMDGPU SR-IOV and virtualization code, especially PF-controlled paths that expose VFs, size VF BARs, set VF memory apertures, process GPUIOV mailbox events, trigger FLR/reset flows, or route GFX/UVD/UVD1/VCE virtualization interrupts.
- Linux PCI and IOMMU-facing behavior for ACS, ATS, PRI, PASID, ARI, MSI, MSI-X, AER, LTR, Resizable BAR, and SR-IOV capabilities.
- Diagnostic and validation paths that inspect PCIe link equalization, 16 GT/s PHY status, lane margining, data link feature exchange, and AER logs.

Cross-generation similarity is high, but these definitions must stay paired with NBIO 7.4 offsets. Older NBIO headers expose similar capability names with different line positions or possibly different field availability, and newer headers may add or remove vendor-specific virtualization fields.

## Risks

- Bitfield drift can corrupt PCIe configuration behavior. A wrong shift or mask can silently program adjacent capability bits, misreport features, break enumeration, or alter link state.
- AER definitions are safety-critical for diagnostics. Incorrect status, mask, or severity fields can hide real PCIe faults, over-report errors, or misclassify fatal/non-fatal events.
- ACS/ATS/PRI/PASID mistakes can affect address translation and isolation. Enabling the wrong bits before IOMMU and driver setup is complete can lead to DMA faults or security-sensitive routing behavior.
- SR-IOV and GPUIOV fields are privilege-sensitive. Incorrect VF counts, strides, BAR sizes, framebuffer offsets, mailbox indexing, interrupt enables, or `SOFT_PF_FLR` handling can break PF/VF isolation, reset the wrong function, lose mailbox events, or expose invalid framebuffer ranges.
- Repeated lane and VF families are mechanically fragile. Lane equalization, lane margining, VF BAR, per-VF mailbox, and per-VF framebuffer macros are repetitive; copy-generation errors are easy to miss because names differ only by lane or VF number.
- Link training and margining fields require hardware-specific sequencing. Treating status fields as controls or issuing equalization/margining changes without the required polling can destabilize a PCIe link.
- The chunk starts and ends mid-family. `BIF_CFG_DEV0_EPF1_0_PCIE_VC1_RESOURCE_CNTL` begins before this chunk, and `BIF_CFG_DEV0_EPF0_VF0_0_PCIE_UNCORR_ERR_SEVERITY` continues after it. The final merged report must stitch those adjacent fields together.

## Test and Validation Signals

Useful validation signals are mostly integration and hardware bring-up tests:

- Build coverage for AMDGPU files that include `nbio/nbio_7_4_sh_mask.h`, paired with `nbio_7_4_offset.h`, catches missing or renamed generated macros.
- PCI enumeration tests should verify VF0 config header fields, BAR sizing, capability-list chaining, MSI/MSI-X capability decoding, and SR-IOV capability layout.
- AER tests should inject or observe correctable and uncorrectable PCIe errors and confirm status, mask, severity, header log, and TLP prefix log decoding.
- IOMMU and peer-to-peer tests should exercise ACS, ATS, PRI, PASID, ARI, and multicast-related behavior under real DMA workloads.
- SR-IOV validation should create/destroy VFs, verify VF counts/stride/device ID/page size/VF BARs, confirm per-VF framebuffer size/offset programming, and check FLR/reset behavior.
- GPUIOV tests should cover mailbox transmit/receive valid and ack transitions, per-VF mailbox bits for VF0 through VF31, virtualization interrupt enable/status bits for GFX/UVD/UVD1/VCE, and P2P-over-XGMI enablement where supported.
- PCIe link tests should validate equalization, 16 GT/s status, data link feature status, lane error status, and margining payload/status behavior across supported link widths.

## Unresolved Cross-Chunk References

The source range begins after the `BIF_CFG_DEV0_EPF1_0_PCIE_VC1_RESOURCE_CNTL` comment and first field definitions, so the previous chunk owns the start of that register. This range also ends while `BIF_CFG_DEV0_EPF0_VF0_0_PCIE_UNCORR_ERR_SEVERITY` is still being defined, so the next chunk owns the remaining severity fields and following VF0 AER capability definitions.
