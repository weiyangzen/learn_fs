# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_2_3_sh_mask.h lines 93607-96044

## Scope

This chunk covers a generated AMD NBIO 2.3 shift/mask header section for PCIe configuration-space bitfields. It starts in the tail of `BIF_CFG_DEV0_EPF0_1_PCIE_VENDOR_SPECIFIC_HDR_GPUIOV_UVD1SCH_DW0`, contains `DW1` through `DW8` for that EPF0 UVD1 GPUIOV scheduler block, then enters `addressBlock: nbio_nbif0_bif_cfg_dev0_epf1_bifcfgdecp` and defines most of endpoint function 1 instance 1 (`BIF_CFG_DEV0_EPF1_1_*`). The range ends at the comment for `BIF_CFG_DEV0_EPF1_1_PCIE_VENDOR_SPECIFIC_HDR_GPUIOV_VCESCH_DW7`; that register's field macros continue in the next chunk.

The file is data-only generated C preprocessor material. It defines no functions, structs, variables, locks, allocations, persistence code, or direct MMIO operations. Its public interface is the AMD register-header convention:

- `<REGISTER>__<FIELD>__SHIFT` for the field's bit offset.
- `<REGISTER>__<FIELD>_MASK` for the field's mask.

There are 2097 `#define` entries in this line range.

## Purpose

This header section is the bitfield side of the NBIO 2.3 PCIe configuration ABI used by AMDGPU. The companion `nbio_2_3_offset.h` file supplies matching config-space addresses or offsets, while `nbio_2_3_default.h` supplies reset/default values. Driver code can then compose and decode register values through helpers such as `REG_SET_FIELD`, `REG_GET_FIELD`, `RREG32_SOC15`, `WREG32_SOC15`, `RREG32_PCIE`, `WREG32_PCIE`, `SOC15_REG_OFFSET`, and `WREG32_FIELD15` without hard-coding bit numbers.

Most of the chunk describes how EPF1 exposes normal PCI/PCIe endpoint configuration: command/status, BARs, power management, PCIe link/device controls, MSI/MSI-X, vendor-specific capabilities, virtual channels, AER, resizable BAR, power budgeting, dynamic power allocation, secondary PCIe capability, ACS/ATS/PASID/page request/LTR/ARI/SR-IOV, multicast, TPH, data link features, 16 GT/s PHY controls, lane margining, VF resizable BAR, and AMD GPUIOV vendor-specific state.

## Important Macro Families

### EPF0 GPUIOV UVD1 Tail

Lines 93607-93631 complete the previous endpoint block by defining full-width `DW1` through `DW8` masks for `BIF_CFG_DEV0_EPF0_1_PCIE_VENDOR_SPECIFIC_HDR_GPUIOV_UVD1SCH_*`. Each covered register is a 32-bit scheduler dword with a `DWn` field at shift `0x0` and mask `0xFFFFFFFFL`. The comment for `DW0` and its shift live in the previous chunk, so this range is only a boundary tail for EPF0.

### EPF1 Standard PCI Header and Power Management

The `BIF_CFG_DEV0_EPF1_1_*` block begins with standard PCI header fields:

- `VENDOR_ID`, `DEVICE_ID`, revision/class/prog-interface fields, cache line, latency, BIST, six BAR registers, CardBus CIS pointer, subsystem IDs, ROM BAR, capability pointer, interrupt line/pin, and min/max grant fields.
- `COMMAND` exposes IO, memory, bus-master, special-cycle, memory-write-invalidate, snoop, parity response, SERR, fast back-to-back, and interrupt-disable bits.
- `STATUS` exposes readiness, interrupt status, capability-list presence, parity and abort status, SERR, and DEVSEL timing.
- `ADAPTER_ID` and `ADAPTER_ID_W` pack subsystem vendor and subsystem ID as 16-bit fields.

The power-management capability is represented by `PMI_CAP_LIST`, `PMI_CAP`, and `PMI_STATUS_CNTL`. These define capability-list linkage, PME support, D-state support, auxiliary current, current power state, PME enable/status, data select/scale, B2/B3 support, bus power enable, and PMI data.

### PCIe Capability, Link, Device, MSI, and MSI-X

The PCIe capability block defines:

- `PCIE_CAP_LIST` and `PCIE_CAP` for capability ID, next pointer, version, device type, slot implemented, and interrupt message number.
- `DEVICE_CAP`, `DEVICE_CNTL`, and `DEVICE_STATUS` for max payload/read-request policy, error reporting enables/status, relaxed ordering, no-snoop, extended tags, auxiliary power, pending transactions, emergency power reduction, and FLR initiation/capability.
- `LINK_CAP`, `LINK_CNTL`, and `LINK_STATUS` for supported/current link speed, link width, ASPM/PM support, exit latencies, retraining, common clock, extended sync, clock power management, link disable, link bandwidth notification, data link active reporting, and training/status bits.
- `DEVICE_CAP2`, `DEVICE_CNTL2`, `DEVICE_STATUS2`, `LINK_CAP2`, `LINK_CNTL2`, and `LINK_STATUS2` for completion timeout, ARI forwarding, atomic ops, ID-based ordering, LTR, TPH completer support, 10-bit tags, OBFF, end-to-end TLP prefixes, emergency power reduction, FRS, supported link speeds, compliance controls, de-emphasis, 8 GT/s equalization status, RTM presence, crosslink state, and DRS status.

Interrupt configuration is covered by MSI and MSI-X masks. MSI fields include enable, multi-message capability/enable, 64-bit address capability, per-vector masking, message address/data, mask, and pending bits. MSI-X fields include table size, function mask, enable, table BIR/offset, and PBA BIR/offset.

### Vendor-Specific Capability and Virtual Channels

`PCIE_VENDOR_SPECIFIC_ENH_CAP_LIST`, `PCIE_VENDOR_SPECIFIC_HDR`, `PCIE_VENDOR_SPECIFIC1`, and `PCIE_VENDOR_SPECIFIC2` describe a conventional VSEC header plus two full-width scratch dwords. These are separate from the later AMD GPUIOV VSEC.

The virtual-channel capability block defines capability-list linkage, port VC capability registers, VC arbitration table load/select/status fields, and resource capability/control/status for VC0 and VC1. Resource controls map traffic classes to VCs, load port arbitration tables, select arbitration policy, set VC ID, and enable a VC. Status bits indicate arbitration-table status and VC negotiation pending.

### Device Serial Number, AER, BAR Resize, Power Budget, and DPA

The device serial number capability exposes two full-width serial dwords.

The AER block defines uncorrectable error status/mask/severity, correctable error status/mask, advanced error capability/control, header logs, and TLP prefix logs. Covered fields include data link protocol error, poisoned TLP, flow-control protocol error, completion timeout, completer abort, unexpected completion, receiver overflow, malformed TLP, ECRC, unsupported request, ACS violation, uncorrectable internal error, MC blocked TLP, atomic egress blocked, TLP prefix blocked, correctable receiver/bad-TLP/bad-DLLP/replay/Advisory Non-Fatal/internal/header-log-overflow status, ECRC generation/check enables, and multiple-header recording.

Resizable BAR fields cover BAR1 through BAR6 capability/control pairs. Each capability has a supported-size bitmap and each control has BAR index, total BAR count, and selected size.

Power budgeting is represented by capability-list, data select, data payload, and capability registers. DPA fields describe substate maximum count, transition latency unit/value, DPA status, DPA enable, and eight substate power-allocation registers.

### Secondary PCIe Capability and Lane Controls

The secondary PCIe capability block defines `LINK_CNTL3`, lane error status, and per-lane equalization control for lanes 0 through 15. Equalization control fields repeat the same layout per lane: downstream TX preset, downstream RX preset hint, upstream TX preset, upstream RX preset hint, and a reserved bit. The 16 GT/s PHY block later mirrors this idea with link capability/control/status, parity mismatch status, and per-lane 16 GT/s equalization controls.

The PCIe margining capability defines port-level capability/status and per-lane margining control/status for lanes 0 through 15. Per-lane control/status fields carry receiver number, margin type, usage model, and margin payload. These are diagnostic and signal-integrity related rather than ordinary runtime policy fields.

### ACS, ATS, Page Request, PASID, Multicast, LTR, ARI, and SR-IOV

The chunk defines several PCIe extended capabilities that matter for virtualization and IOMMU integration:

- ACS capability/control fields cover source validation, translation blocking, P2P request/completion redirect, upstream forwarding, P2P egress control, direct translated P2P, and egress-control vector size.
- ATS fields expose invalidation queue depth and enable/stall controls.
- Page Request fields expose enable/reset and response-failure status.
- PASID fields expose execute permission, privileged mode support/enable, and PASID width.
- Multicast fields expose max group/window size, ECRC regeneration, enable, group count, base address, receive vectors, block-all vectors, and block-untranslated vectors.
- LTR exposes snoop and no-snoop max latency value/scale.
- ARI exposes function-group capabilities, next function number, enables, and function group.
- SR-IOV exposes VF migration capability/status, ARI hierarchy preservation, VF 10-bit tag requester support/enable, VF enable, VF memory-space enable, initial/total/current VF counts, function dependency link, first VF offset, VF stride, VF device ID, supported/system page sizes, six VF BARs, and migration state array offset.

These fields are closely tied to host PCI enumeration, IOMMU behavior, and PF/VF isolation.

### TPH, Data Link Feature, 16 GT/s PHY, and VF Resizable BAR

TPH requester capability/control fields describe supported steering tag modes, extended requester support, steering table location/size, selected steering mode, and TPH enable.

The data link feature capability exposes feature capability and status registers. The covered field names include data-link feature exchange enable/capability style fields and status bits that software may use during link-feature negotiation or diagnostics.

The 16 GT/s PHY capability block includes link capability/control/status, local and retimer parity mismatch status, and lane 0-15 16 GT/s equalization control fields. The 16 GT/s lane controls use downstream/upstream preset and coefficient fields that are more detailed than the older 8 GT/s equalization masks.

The VF resizable BAR capability mirrors the PF BAR resize block for VF BAR1 through VF BAR6, with supported-size bitmaps and controls for VF BAR index, total VF BAR count, and selected VF BAR size.

### GPUIOV Vendor-Specific Region

The AMD GPUIOV VSEC begins with `PCIE_VENDOR_SPECIFIC_ENH_CAP_LIST_GPUIOV` and `PCIE_VENDOR_SPECIFIC_HDR_GPUIOV`, then exposes virtualization control and communication fields:

- `SRIOV_SHADOW` carries a shadow VF enable bit and VF count.
- `INTR_ENABLE` and `INTR_STATUS` define GFX, UVD, UVD1, and VCE command-complete, self-recovered hang, need-FLR hang, and VM-busy-transition interrupt bits, plus HVVM mailbox transmit-ack and receive-valid interrupt bits.
- `RESET_CONTROL` defines GFX, UVD, UVD1, and VCE VF FLR controls and per-engine scheduler reset bits.
- `HVVM_MBOX_DW0` through `DW2` expose full-width mailbox dwords for hypervisor/VM communication.
- `CONTEXT`, `TOTAL_FB`, `OFFSETS`, `REGION`, and `P2P_OVER_XGMI_ENABLE` describe GPUIOV context count/size style metadata, total framebuffer partitioning, offsets, region selection, and XGMI peer-to-peer enablement.
- `VF0_FB` through `VF30_FB` each pack a 16-bit VF framebuffer size and a 16-bit VF framebuffer offset.
- `UVDSCH_DW0` through `DW8` and `VCESCH_DW0` through `DW6` are full-width scheduler dwords for video decode and encode scheduling. `VCESCH_DW7` starts at the chunk boundary and is completed by the next chunk.

## Control Flow and State Behavior

There is no executable control flow in this header. It changes behavior only at compile time by giving C code the correct bit positions and masks for hardware-backed PCIe configuration registers.

The state represented here is hardware state exposed through PCI configuration space or AMD vendor-specific configuration windows. Important persistent state includes PCI command enables, BAR and ROM BAR values, power-management state, PCIe link and device control, MSI/MSI-X message routing and masks, VC arbitration/resource state, AER masks/status/severity/logs, resizable BAR selections, DPA allocations, secondary PCIe equalization controls, ACS/ATS/PASID/page-request controls, multicast filters, ARI/SR-IOV configuration, VF BARs, GPUIOV interrupt enables/status, reset controls, mailbox dwords, per-VF framebuffer partitions, and video scheduler dwords.

Several fields are status, sticky status, or command-like rather than ordinary durable configuration. Examples include PCI/AER error status, PME status, link training/equalization status, MSI pending bits, VC negotiation pending, page request response failure, SR-IOV migration status, GPUIOV interrupt status, FLR/reset controls, mailbox handshake bits, and margining status. Correct users need the sequencing and clearing rules from PCIe, hardware documentation, and the owning AMDGPU virtualization paths; the masks alone do not define ordering, polling, or timeout behavior.

## Dependencies and Integration Points

This chunk depends on the generated NBIO 2.3 register header set:

- `nbio_2_3_offset.h` supplies matching register/config-space offsets and base indices.
- `nbio_2_3_default.h` supplies reset/default values for the same register names.
- AMDGPU register helper macros consume the `__SHIFT` and `_MASK` definitions to compose and decode fields.

Observed source-tree integration includes `drivers/gpu/drm/amd/amdgpu/nbio_v2_3.c`, which includes `nbio_2_3_default.h`, `nbio_2_3_offset.h`, and `nbio_2_3_sh_mask.h` and uses SOC15/PCIe helpers for NBIO programming. Related MXGPU/SR-IOV code paths depend on the same generated definitions for VF enablement, FLR handling, doorbell/interrupt setup, and virtualization-visible PCIe state. The PCI core and host firmware also interact indirectly with these fields through normal PCI configuration-space enumeration and capability negotiation.

Cross-generation similarity is high but not interchangeable. Other NBIO/NBIF headers contain similar EPF, SR-IOV, GPUIOV, AER, and lane-control names with different prefixes, offsets, capability ordering, or field layouts. Consumers must include the matching NBIO 2.3 offset/mask/default set for this ASIC generation.

## Risks

- Bitfield drift is high impact. A wrong shift or mask can write an unrelated PCIe field, causing failed enumeration, link instability, lost interrupts, broken BAR sizing, failed FLR, incorrect power policy, or GPU hangs.
- The EPF1 block is large and repetitive. PCIe capability lists, per-lane equalization/margining, BAR resize, VF BAR, VF framebuffer, and scheduler dword families are easy to damage mechanically.
- Virtualization fields are isolation-sensitive. Incorrect ACS, ATS, PASID, ARI, SR-IOV, GPUIOV shadow, VF BAR, VF framebuffer, P2P-over-XGMI, or reset-control masks can break PF/VF isolation or expose the wrong memory aperture.
- Error and interrupt fields include enable, status, mask, and severity variants with similar names. Mixing AER status/mask/severity or GPUIOV interrupt enable/status fields can mask real faults or create spurious interrupts.
- Link training, equalization, 16 GT/s PHY, and margining fields are hardware-timing sensitive. Treating diagnostic or training fields as generic runtime knobs can destabilize PCIe links.
- The chunk has partial boundaries at both ends: EPF0 UVD1 scheduler `DW0` is incomplete at the start, and EPF1 GPUIOV VCE scheduler `DW7` and later fields continue after the end. The merge lane must stitch adjacent chunks before making final file-level completeness claims.

## Test and Validation Signals

Useful validation is primarily compile and hardware integration coverage:

- Build AMDGPU paths that include `nbio_2_3_sh_mask.h`, especially NBIO 2.3, MXGPU/SR-IOV, and SMU/platform files, to catch missing or renamed macros.
- PCI enumeration should report stable vendor/device/class IDs, capability chains, BAR sizes, MSI/MSI-X capability state, PCIe link capabilities, and SR-IOV capability contents for NBIO 2.3 hardware.
- Link tests should validate negotiated speed/width, retraining, ASPM/power-management controls, 8 GT/s/16 GT/s equalization status, and lane margining diagnostics where supported.
- Error-handling tests should exercise PCIe/AER status and masks, FLR initiation/completion, GPUIOV need-FLR/self-recovery interrupts, and mailbox transmit/receive interrupt paths.
- SR-IOV tests should create and destroy VFs, verify VF enable/MSE/count/stride/device-ID fields, validate VF BAR and VF resizable BAR sizing, and check per-VF framebuffer size/offset partitioning.
- Virtualization and peer-to-peer tests should cover ACS/ATS/PASID/page-request/ARI/LTR behavior, multicast vectors if enabled, and `P2P_OVER_XGMI_ENABLE` policy.
- Suspend/resume and reset coverage should verify that persistent PCIe, MSI/MSI-X, SR-IOV, GPUIOV, and scheduler dword state is restored or reinitialized consistently.

## Unresolved Cross-Chunk References

The first line is only the mask for `BIF_CFG_DEV0_EPF0_1_PCIE_VENDOR_SPECIFIC_HDR_GPUIOV_UVD1SCH_DW0`; the register comment and shift are in the previous chunk. The final line is only the comment for `BIF_CFG_DEV0_EPF1_1_PCIE_VENDOR_SPECIFIC_HDR_GPUIOV_VCESCH_DW7`; its shift/mask and later GPUIOV scheduler fields are in the next chunk.
