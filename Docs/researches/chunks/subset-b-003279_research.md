# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_7_7_0_sh_mask.h lines 48823-51288

## Scope

This chunk covers generated shift and mask macros from the NBIO 7.7.0 AMD GPU register mask header. The range starts in the tail of the `BIF_CFG_DEV0_EPF0_0_LANE_11_MARGINING_LANE_CNTL` field set and ends at the beginning of `BIF_CFG_DEV0_EPF2_0_FLADJ`, before that register's remaining field definitions continue in the next chunk.

The covered register families are:

- EPF0 PCIe margining status/control fields for lanes 11 through 15.
- EPF0 virtual-function resizable BAR enhanced capability fields for VF BARs 1 through 6.
- EPF0 AMD GPUIOV vendor-specific enhanced capability fields, including SR-IOV shadow state, PF reset control, hypervisor/VF mailbox fields, per-VF framebuffer partition fields for VF0 through VF15, and UVD/VCE/GFX scheduler data words.
- The start of address block `nbio_nbif0_bif_cfg_dev0_epf1_bifcfgdecp`, which maps a full PCI/PCIe configuration-space image for embedded physical function 1.
- EPF1 base PCI configuration header, PM capability, PCIe capability, MSI/MSI-X, AER, resizable BAR, power budget, DPA, secondary PCIe, lane equalization, ACS, ATS, PRI, PASID, multicast, LTR, ARI, SR-IOV, DLF, 16 GT/s PHY, lane margining, and VF resizable BAR fields.
- The start of address block `nbio_nbif0_bif_cfg_dev0_epf2_bifcfgdecp`, covering EPF2 base PCI configuration header and PM capability fields through `FLADJ`.

This file chunk is a generated hardware bitfield map. It defines C preprocessor constants only. There are no C functions, structs, variables, allocations, or executable control-flow constructs in the chunk.

## Purpose

The purpose of this header section is to provide the bit-level ABI between AMDGPU/NBIO driver code and the NBIO 7.7.0 PCIe configuration-space register image. Each field is represented with the usual generated pair:

- `<REGISTER>__<FIELD>__SHIFT`, the bit offset for a field.
- `<REGISTER>__<FIELD>_MASK`, the bit mask used to isolate or compose that field.

Consumers combine these definitions with the matching NBIO 7.7.0 offset/default headers and AMDGPU register helpers such as `REG_GET_FIELD`, `REG_SET_FIELD`, `RREG32_SOC15`, `WREG32_SOC15`, and `SOC15_REG_OFFSET`. The offset header supplies addresses such as `regBIF_CFG_DEV0_EPF1_0_PCIE_SRIOV_CONTROL`; this mask header supplies the field positions and masks for those register values.

## Important Macro Families

### EPF0 Lane Margining and VF Resizable BARs

The first part of the chunk finishes the EPF0 PCIe margining lane definitions. Lanes 12 through 15 have complete `*_MARGINING_LANE_CNTL` and `*_MARGINING_LANE_STATUS` definitions, while lane 11 starts with the final payload mask from its control register and then includes status fields. The lane control/status layout is regular:

- `RECEIVER_NUMBER` or `RECEIVER_NUMBER_STATUS` at bits 2:0.
- `MARGIN_TYPE` or `MARGIN_TYPE_STATUS` at bits 5:3.
- `USAGE_MODEL` or `USAGE_MODEL_STATUS` at bit 6.
- `MARGIN_PAYLOAD` or `MARGIN_PAYLOAD_STATUS` at bits 15:8.

These fields implement the PCIe margining extended capability interface for per-lane electrical margin tests. The paired status registers let software observe the result/status encoding returned by the hardware for each lane.

EPF0 then exposes a virtual-function resizable BAR enhanced capability. `PCIE_VF_RESIZE_BAR_ENH_CAP_LIST` defines `CAP_ID`, `CAP_VER`, and `NEXT_PTR`. For VF BAR1 through VF BAR6, each `*_CAP` register exposes `VF_BAR_SIZE_SUPPORTED`, and each `*_CNTL` register exposes `VF_BAR_INDEX`, `VF_BAR_TOTAL_NUM`, `VF_BAR_SIZE`, and `VF_BAR_SIZE_SUPPORTED_UPPER`. These fields describe and control advertised VF BAR sizing for SR-IOV-capable functions.

### EPF0 GPUIOV Vendor-Specific Capability

The GPUIOV block is an AMD vendor-specific PCIe extended capability. It starts with `PCIE_VENDOR_SPECIFIC_ENH_CAP_LIST_GPUIOV` and `PCIE_VENDOR_SPECIFIC_HDR_GPUIOV`, which describe the capability ID/version/next pointer and VSEC ID/revision/length. The block then maps virtualization-oriented state:

- `PCIE_VENDOR_SPECIFIC_HDR_GPUIOV_SRIOV_SHADOW` mirrors `VF_EN` and `VF_NUM`.
- `PCIE_VENDOR_SPECIFIC_HDR_GPUIOV_RESET_CONTROL` exposes `SOFT_PF_FLR`, a PF-level reset-control bit.
- `PCIE_VENDOR_SPECIFIC_HDR_GPUIOV_HVVM_MBOX_DW0` provides the selected `VF_INDEX`, transmit/receive message data fields, and valid/ack bits for PF/hypervisor to VF mailbox exchange.
- `PCIE_VENDOR_SPECIFIC_HDR_GPUIOV_HVVM_MBOX_DW1` provides per-VF transmit acknowledgement and receive-valid bits for VF0 through VF15.
- `PCIE_VENDOR_SPECIFIC_HDR_GPUIOV_CONTEXT` provides context size, location, and offset fields.
- `PCIE_VENDOR_SPECIFIC_HDR_GPUIOV_TOTAL_FB` exposes total framebuffer available and consumed.
- `PCIE_VENDOR_SPECIFIC_HDR_GPUIOV_VF0_FB` through `VF15_FB` define per-VF framebuffer size and offset fields.
- `PCIE_VENDOR_SPECIFIC_HDR_GPUIOV_UVDSCH_DW0..DW8`, `VCESCH_DW0..DW8`, and `GFXSCH_DW0..DW8` are full-width scheduler data words for UVD, VCE, and GFX virtualization scheduling metadata.

The GPUIOV fields are integration points for SR-IOV and mediated GPU partitioning. They describe resource advertisement, VF memory partitioning, per-VF mailbox state, and scheduler-visible state rather than ordinary display or graphics queue configuration.

### EPF1 Base PCI and PCIe Capabilities

The EPF1 address block begins with conventional PCI configuration header fields:

- Identity and class-code fields: `VENDOR_ID`, `DEVICE_ID`, `REVISION_ID`, `PROG_INTERFACE`, `SUB_CLASS`, and `BASE_CLASS`.
- Command/status fields: I/O enable, memory enable, bus master enable, SERR, interrupt disable, capability-list presence, parity/abort/system-error status, and DEVSEL timing.
- BAR and expansion registers: `BASE_ADDR_1` through `BASE_ADDR_6`, `ROM_BASE_ADDR`, `CARDBUS_CIS_PTR`, `ADAPTER_ID`, and writeable adapter ID aliases.
- Interrupt and legacy timing registers: `CAP_PTR`, `INTERRUPT_LINE`, `INTERRUPT_PIN`, `MIN_GRANT`, and `MAX_LATENCY`.
- Vendor and PM capability headers plus PM capability/control fields such as D-state support, PME support, current power state, PME enable/status, data select/scale, bus power enable, and PM data.

The PCIe capability portion exposes endpoint capability and link behavior:

- `PCIE_CAP_LIST` and `PCIE_CAP` identify the capability and endpoint device type.
- `DEVICE_CAP`, `DEVICE_CNTL`, and `DEVICE_STATUS` describe max payload support/size, error reporting enables/status, relaxed ordering, no-snoop, extended tags, FLR capability/initiation, transactions pending, and emergency power-reduction status.
- `LINK_CAP`, `LINK_CNTL`, and `LINK_STATUS` describe supported/current speed and width, ASPM/PM control, retraining/link-disable/common-clock bits, data-link active reporting, bandwidth interrupts, DRS signaling, and negotiated link state.
- `DEVICE_CAP2`, `DEVICE_CNTL2`, `DEVICE_STATUS2`, `LINK_CAP2`, `LINK_CNTL2`, and `LINK_STATUS2` describe completion-timeout controls, ARI, atomic operations, IDO, LTR, OBFF, 10-bit tags, TLP prefix support/blocking, link target speed, compliance controls, 8 GT/s equalization phases, RTM presence, crosslink status, and DRS message receipt.

These masks are consumed by code that reads or programs the PCIe capability image for NBIO physical functions. They must remain aligned with the PCIe specification layout and the ASIC-specific capability chain.

### EPF1 Interrupt, Error Reporting, and Resizable BAR Capabilities

The EPF1 interrupt capability region includes MSI and MSI-X:

- `MSI_MSG_CNTL` exposes MSI enable, multi-message capability/enables, 64-bit addressing, per-vector masking capability, and extended message-data support/enable.
- MSI address/data, mask, and pending registers cover both 32-bit and 64-bit forms.
- `MSIX_MSG_CNTL`, `MSIX_TABLE`, and `MSIX_PBA` expose MSI-X table size, function mask, enable bit, BIR fields, and table/PBA offsets.

The AER block includes the enhanced capability header, uncorrectable error status/mask/severity, correctable error status/mask, advanced error capability/control, header logs, and TLP prefix logs. These fields are the hardware encoding used for PCIe error diagnostics and error masking.

The ordinary PF resizable BAR capability for EPF1 has `PCIE_BAR_ENH_CAP_LIST`, BAR1 through BAR6 capability registers, and matching control registers with `BAR_INDEX`, `BAR_TOTAL_NUM`, `BAR_SIZE`, and upper supported-size fields. Later in the chunk, EPF1 also exposes VF resizable BAR controls using the same `VF_BAR_*` layout as EPF0.

### EPF1 Power, DPA, Secondary PCIe, and Per-Lane Link Training

EPF1 power-related extended capabilities include:

- Power budget capability fields: data select, data value, data scale, PM sub-state, type, power rail, system allocation, and capability flags.
- Dynamic power allocation fields: DPA capability, latency indicator, status, control, and substate power allocation registers 0 through 7.

Secondary PCIe and high-speed link-training support includes:

- `PCIE_SECONDARY_ENH_CAP_LIST`, `PCIE_LINK_CNTL3`, and `PCIE_LANE_ERROR_STATUS`.
- Per-lane equalization control for lanes 0 through 15, carrying downstream/upstream port transmit presets and coefficient fields for regular equalization.
- 16 GT/s PHY capability, link capability/control/status, local and RTM parity mismatch status, and per-lane 16 GT/s equalization presets for lanes 0 through 15.
- PCIe lane margining capability, port capability/status, and lane 0 through lane 15 margining control/status fields using the same receiver/type/usage/payload layout as EPF0.

These fields participate in PCIe link training, equalization, margining, and diagnostics. Their status bits are often polled by platform, firmware, or driver diagnostics rather than used in hot paths.

### EPF1 Isolation, Address Translation, and Virtualization Capabilities

EPF1 includes several capabilities that matter for IOMMU, peer-to-peer routing, and virtualization:

- ACS capability/control fields cover source validation, translation blocking, P2P request/completion redirect, upstream forwarding, egress control, direct translated P2P, and egress vector support.
- ATS capability/control fields cover invalidation queue depth, page-aligned requests, and STU/enable.
- PRI/page request fields expose enable/reset bits, response-failure status, unexpected-page-request group/index, PASID-required, stopped, PRG response PASID required, outstanding capacity, and outstanding allocation.
- PASID capability/control fields describe execute permission, privileged mode, max PASID width, and enable bits.
- Multicast capability/control/address/receive/blocking fields describe MC group count, ECRC regeneration, MC enable, and translated/untranslated address blocking.
- LTR fields describe max snoop/no-snoop latency values and scales.
- ARI capability/control fields expose function-group capability/enables and next-function number.
- SR-IOV fields expose VF migration capability/status, ARI hierarchy, VF enable, VF memory-space enable, initial/total/active VF counts, first VF offset, VF stride, VF device ID, supported/system page sizes, VF BAR base addresses, and migration state array location.
- DLF fields expose local/remote data-link feature support and exchange status.

These masks define the advertised and controllable isolation surface for EPF1. They are especially sensitive in SR-IOV or VFIO deployments because incorrect values can change function enumeration, VF BAR layout, address translation behavior, and peer-to-peer isolation guarantees.

### EPF2 Partial PCI Configuration Block

The final part of the chunk starts EPF2. It mirrors the early EPF1 PCI header and PM capability definitions:

- `VENDOR_ID`, `DEVICE_ID`, command/status, revision/class fields, cache-line/latency/header/BIST, BAR1 through BAR6, CIS pointer, adapter ID, ROM BAR, capability pointer, interrupt line/pin, min grant, max latency, vendor capability, adapter ID write alias, PM capability list, `PMI_CAP`, `PMI_STATUS_CNTL`, and `SBRN`.
- The chunk ends after the first `BIF_CFG_DEV0_EPF2_0_FLADJ__FLADJ__SHIFT` definition; `NFC` and the masks for `FLADJ` are in the next chunk.

EPF2 is therefore only partially described here. The merge/reconciliation lane should connect this document with the following chunk for the rest of EPF2's USB/PCIe capability and later PCIe capability fields.

## Control Flow and State Behavior

This header chunk has no runtime control flow. It influences compiled driver behavior by defining how C code composes and decodes 32-bit hardware register values.

The persistent state represented by the chunk is hardware state in NBIO/PCIe configuration space, not software state in the header. Important state includes PCI command/status bits, BAR advertisements and size controls, MSI/MSI-X programming, PM/PME state, PCIe link capability/control/status, AER error state and masks, lane equalization and margining status, ACS/ATS/PRI/PASID/LTR/ARI controls, SR-IOV VF counts and BARs, GPUIOV mailbox and framebuffer partitioning, and scheduler data words.

Some fields are configuration bits that remain programmed until reset or reconfiguration, such as BAR sizes, ACS controls, MSI/MSI-X enables, SR-IOV controls, and per-VF framebuffer size/offset. Other fields are status, sticky error, or command-like fields, such as AER error status, margining status payloads, link retrain/compliance bits, FLR initiation, PF reset control, mailbox valid/ack bits, PME status, and SR-IOV migration status. Consumers must use the sequencing, write-one-to-clear, polling, and timeout behavior defined by the owning driver and hardware specification; those semantics are not encoded in the mask names alone.

## Dependencies and Integration Points

This chunk depends on the generated AMD register-header convention:

- `nbio_7_7_0_offset.h` supplies the register addresses and base indices for the `BIF_CFG_DEV0_EPF*_0_*` names.
- `nbio_7_7_0_default.h`, where present for a register, supplies reset/default values.
- AMDGPU SOC15 register helpers and PCI/NBIO code consume the `__SHIFT` and `_MASK` macros to avoid hard-coded bit positions.

Likely integration points in the source tree include:

- NBIO initialization, reset, and virtualization code that programs SR-IOV, GPUIOV, PF/VF resources, and PCIe capability state for AMD GPU devices.
- PCIe link-management and diagnostics paths that read link capability/status, lane equalization, 16 GT/s status, lane margining, and AER fields.
- Interrupt setup paths that use MSI/MSI-X capability fields and masks.
- VFIO/SR-IOV and hypervisor-facing code that relies on VF counts, VF BAR sizes, migration state array, per-VF framebuffer offsets, GPUIOV mailbox fields, and VF scheduler metadata.
- IOMMU and peer-to-peer isolation flows that depend on ACS, ATS, PRI, PASID, multicast, LTR, and ARI capability encodings.

The names are generation-specific. Similar fields exist in other NBIO 7.x headers, but the capability order, presence of GPUIOV fields, register offsets, VF counts, and reserved bits can differ. Consumers should include the matching NBIO 7.7.0 offset/mask/default set together rather than mixing definitions from nearby ASIC generations.

## Risks

- Bitfield drift is high impact. A wrong shift or mask can advertise the wrong PCIe capability, corrupt BAR sizing, break MSI/MSI-X setup, mask or misreport AER errors, or write reserved hardware bits.
- SR-IOV and GPUIOV fields are privilege-sensitive. Incorrect VF enable/count, VF BAR, per-VF framebuffer, mailbox, scheduler, or reset-control masks can break PF/VF isolation, enumeration, reset handling, or resource accounting.
- Capability-chain fields such as `CAP_ID`, `CAP_VER`, `NEXT_PTR`, VSEC length, and capability-list pointers must match the actual configuration-space layout. Bad values can confuse the kernel PCI core or user-space enumeration tools.
- Lane equalization and margining fields are repetitive and easy to copy incorrectly. Per-lane bit layouts must remain consistent, but lane numbers and status/control suffixes must not be crossed.
- AER and status fields may be sticky or write-one-to-clear in hardware. Treating them as ordinary read/write state can lose diagnostic evidence or fail to clear real faults.
- PCIe power-management and DPA fields can affect device power state and latency reporting. Incorrect writes may cause PME behavior changes, bad power-budget advertisement, or link/power instability.
- ACS/ATS/PRI/PASID/ARI fields are security- and IOMMU-relevant. Advertising support or enabling controls incorrectly can alter DMA translation, peer-to-peer forwarding, and VF function routing.
- The chunk begins and ends mid-family. Lane 11 control and EPF2 `FLADJ` are incomplete in this document and must be reconciled with adjacent chunks for a complete per-file report.

## Test and Validation Signals

Useful validation is mostly build, enumeration, and hardware integration coverage:

- Build AMDGPU and any NBIO/SOC15 consumers that include `nbio/nbio_7_7_0_sh_mask.h`; this catches missing or renamed macros.
- PCI config-space enumeration should confirm EPF1/EPF2 vendor/device/class/header/BAR/capability-list fields and GPUIOV VSEC chain values match expected hardware layout.
- MSI/MSI-X tests should verify message-control, table/PBA, mask, pending, and 64-bit address/data fields on supported hardware.
- PCIe link diagnostics should verify link speed/width, retrain/status, 8 GT/s and 16 GT/s equalization, lane error, RTM parity, and lane margining status/control behavior.
- AER validation should inject or observe correctable/uncorrectable errors and confirm status, mask, severity, header log, and TLP prefix log fields decode correctly.
- SR-IOV validation should enable VFs, check VF counts/stride/device IDs/page sizes, resize VF BARs, validate VF BAR base addresses, and verify migration-state array fields when supported.
- GPUIOV validation should cover mailbox valid/ack sequencing, VF framebuffer size/offset accounting, total framebuffer consumed/available, soft PF FLR behavior, and UVD/VCE/GFX scheduler data-word visibility.
- IOMMU and isolation tests should exercise ACS, ATS, PRI, PASID, ARI, multicast, and LTR capability advertisement and enablement with VFIO/SR-IOV workloads.
