# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_7_0_sh_mask.h lines 4970-7418

## Purpose

This chunk is part of AMDGPU's generated NBIO 7.0 register shift/mask header. It contains preprocessor constants only: each hardware register field is represented by a `<REGISTER>__<FIELD>__SHIFT` macro and a matching `<REGISTER>__<FIELD>_MASK` macro for packing or extracting bitfields from PCI configuration-space and NBIO register values. There are no functions, structs, variables, includes, allocation paths, locks, direct register accesses, or executable branches in this range.

The selected lines start in the middle of endpoint/function `BIF_CFG_DEV0_EPF1_0` PCIe capability definitions, covering the tail of `DEVICE_CAP` masks and then the rest of EPF1's PCIe device/link, MSI/MSI-X, VSEC, virtual-channel, AER, BAR sizing, power-budgeting, DPA, secondary PCIe, per-lane equalization, ACS/ATS/PASID/TPH/MC/LTR/ARI/SR-IOV, and AMD GPU-IOV vendor-specific capability fields. The range then switches at line 6509 to address block `nbio_nbif0_bif_cfg_dev0_epf2_bifcfgdecp` and defines the start of `BIF_CFG_DEV0_EPF2_0`, including conventional PCI config header fields, PM and PCIe capabilities, MSI/MSI-X, SATA capability fields, VSEC, AER, BAR sizing, power budgeting, DPA, ACS, and the beginning of ARI control.

Although the repository path is under a `ceph-client` source mirror, this source is AMDGPU DRM hardware metadata. It does not implement Ceph filesystem behavior, distributed filesystem state, networking, or storage persistence.

## Important APIs, Types, And Constants

There are no callable APIs or C types in this chunk. The exported interface is the generated macro namespace:

- `<REGISTER>__<FIELD>__SHIFT`: the field's low bit position.
- `<REGISTER>__<FIELD>_MASK`: the already-positioned field mask.

Major EPF1 register families in this chunk include:

- `BIF_CFG_DEV0_EPF1_0_DEVICE_*` and `LINK_*`: PCIe device capability/control/status and link capability/control/status fields, including payload size, read-request size, relaxed ordering, no-snoop, FLR initiation, completion timeout, LTR, OBFF, target link speed, link training, equalization, and de-emphasis/status bits.
- `BIF_CFG_DEV0_EPF1_0_MSI*` and `MSIX*`: MSI/MSI-X capability IDs, next pointers, enable and multiple-message controls, 32/64-bit message addresses/data, mask and pending bits, table size, function mask, table BIR/offset, and PBA BIR/offset.
- `BIF_CFG_DEV0_EPF1_0_PCIE_VENDOR_SPECIFIC*`, `PCIE_VC*`, and `PCIE_DEV_SERIAL_NUM*`: vendor-specific enhanced capability list/header fields, virtual-channel capability/control/status and VC0/VC1 resource maps, plus device serial number data words.
- `BIF_CFG_DEV0_EPF1_0_PCIE_ADV_ERR_*`: AER enhanced capability, uncorrectable error status/mask/severity, correctable error status/mask, advanced error capability/control, header logs, and TLP prefix logs. The uncorrectable sets include DLP, surprise down, poison, flow-control, completion timeout/abort, unexpected completion, receiver overflow, malformed TLP, ECRC, unsupported request, ACS violation, internal error, MC-blocked TLP, atomic egress block, and TLP prefix block fields.
- `BIF_CFG_DEV0_EPF1_0_PCIE_BAR*`: BAR enhanced capability plus BAR1 through BAR6 size-supported and control fields for BAR index, total count, and selected size.
- `BIF_CFG_DEV0_EPF1_0_PCIE_PWR_BUDGET*` and `PCIE_DPA*`: power budgeting data selection/data/capability fields and dynamic power allocation capability/status/control/substate power allocation fields.
- `BIF_CFG_DEV0_EPF1_0_PCIE_SECONDARY*` and `PCIE_LANE_*_EQUALIZATION_CNTL`: secondary PCIe capability/control fields and lane 0 through lane 15 equalization controls for downstream/upstream port transmit preset and preset hints.
- `BIF_CFG_DEV0_EPF1_0_PCIE_ACS*`, `ATS*`, `PAGE_REQ*`, `PASID*`, `TPH_REQR*`, `MC*`, `LTR*`, and `ARI*`: IOMMU/virtualization-related capabilities for ACS isolation, address translation service, page request, PASID width and enable, TPH requester controls, multicast address/receive/block maps, latency tolerance reporting, and alternative routing-ID interpretation.
- `BIF_CFG_DEV0_EPF1_0_PCIE_SRIOV*`: SR-IOV capability/control/status and VF enumeration/layout fields, including VF count, first VF offset, VF stride, VF device ID, supported/system page sizes, VF BARs, and migration state array offset.
- `BIF_CFG_DEV0_EPF1_0_PCIE_VENDOR_SPECIFIC_*_GPUIOV*`: AMD GPU-IOV VSEC fields for VSEC ID/revision/length, SR-IOV shadow VF enable/count, interrupt enable/status for GFX/UVD/VCE command complete, hang/self-recovery/FLR-needed, VM busy transition, and HVVM mailbox events, soft PF FLR, HVVM mailbox data and per-VF ack/valid bits, PF ack/valid bits, context and total framebuffer fields, per-VF framebuffer sizing for VF0 through VF15, and UVD/VCE/GFX scheduler dwords.

Major EPF2 register families in this chunk include:

- `BIF_CFG_DEV0_EPF2_0_VENDOR_ID`, `DEVICE_ID`, `COMMAND`, `STATUS`, revision/class/header/BIST/BAR/adapter/ROM/capability-pointer/interrupt/min-grant/max-latency fields. These mirror the conventional PCI configuration header for endpoint function 2.
- `BIF_CFG_DEV0_EPF2_0_PMI*`, `SBRN`, `FLADJ`, and `DBESL_DBESLD`: power-management capability/status/control and USB/SATA-style timing/control metadata.
- `BIF_CFG_DEV0_EPF2_0_PCIE_CAP*`, `DEVICE_*`, and `LINK_*`: PCIe capability list, device and link capability/control/status, device/link capability 2 and control/status 2, and slot capability/control/status 2 fields.
- `BIF_CFG_DEV0_EPF2_0_MSI*`, `MSIX*`, and `SATA_*`: MSI/MSI-X programming fields plus SATA capability/index/data fields.
- `BIF_CFG_DEV0_EPF2_0_PCIE_VENDOR_SPECIFIC*`, `PCIE_ADV_ERR_*`, `PCIE_BAR*`, `PCIE_PWR_BUDGET*`, `PCIE_DPA*`, `PCIE_ACS*`, and `PCIE_ARI*`: the EPF2 subset of vendor-specific, AER, BAR sizing, power-budgeting, DPA, ACS, and ARI field layouts. The chunk ends after the ARI control shift macros; matching ARI control masks continue in the next chunk.

## Control Flow

This header has no runtime control flow. It is compile-time hardware metadata consumed by C code that performs register read/modify/write operations.

Typical consumer flow is:

1. Driver code includes `nbio_7_0_offset.h` and `nbio_7_0_sh_mask.h`, and sometimes `nbio_7_0_default.h` or `nbio_7_0_smn.h`.
2. A consumer reads a 16-bit or 32-bit PCIe/NBIO register through AMDGPU helpers, or prepares a value to write to a configuration-space register.
3. Field values are inserted with generated shifts and masks, usually indirectly through helpers such as `REG_SET_FIELD` or extracted through `REG_GET_FIELD`-style logic.
4. The programmed value is written back through SOC15, PCIe, or SMN/MMIO access helpers. Ordering, polling, interrupt acknowledgement, and reset sequencing are implemented in the consuming driver code, not in this header.

Direct includes found in this source tree include `amdgpu/nbio_v7_0.c`, `amdgpu/soc15.c`, and `pm/powerplay/hwmgr/smu10_inc.h`. `nbio_v7_0.c` uses the generated masks with NBIO register access helpers for memory-controller access enablement, doorbell ranges, clock gating, light sleep, interrupt control, HDP flush registers, and other NBIO programming. This particular chunk's PCI configuration-space capability fields are more likely to be consumed by platform, virtualization, diagnostics, or generated-register paths than by the narrow NBIO core functions shown in `nbio_v7_0.c`.

## State And Persistence Behavior

The header stores no software state and persists nothing on disk. The constants describe state located in NBIO/PCIe hardware registers for AMD NBIO 7.0 endpoints.

Hardware state represented by this chunk includes:

- PCI command/status state such as IO, memory, bus mastering, parity/SERR, interrupt disable, target/master abort, parity error, and capability-list presence.
- PCIe device and link state such as payload size, read request size, FLR initiation, completion timeout behavior, LTR/OBFF, link speed/width, ASPM, retrain/link disable, common clock, link bandwidth interrupts/status, and lane equalization controls.
- Interrupt capability state for MSI and MSI-X, including enable bits, message address/data, function mask, per-vector mask/pending bits, table offsets, and pending bit array offsets.
- AER state for correctable and uncorrectable error status/masks/severity, ECRC generation/checking, header logs, and TLP prefix logs.
- Resource sizing and power state through BAR capability/control, power-budgeting fields, DPA substate controls, and PM capability/status/control fields.
- Isolation and address-translation state through ACS, ATS, PASID, page request, ARI, multicast, TPH, and LTR capabilities.
- SR-IOV and AMD GPU-IOV virtualization state through VF enumeration/page-size/VF BAR metadata, VF enable/count shadowing, per-VF mailbox ack/valid bits, PF mailbox status, per-VF framebuffer allocation fields, reset control, and engine scheduler dwords.

Persistence is register-specific. Configuration bits usually persist until PCI configuration rewrite, FLR, secondary bus reset, GPU reset, suspend/resume, power-gating transition, or firmware/hypervisor intervention. Status and interrupt bits are often transient or write-one-to-clear, and message/ack/valid bits can represent synchronization with firmware, PF/VF, or hypervisor logic. The generated masks do not encode access type, reset value, side effects, or ordering requirements; those must come from the hardware specification and consumer code.

## Dependencies And Integration Points

This chunk depends on AMD's generated ASIC register database and is meaningful only with matching NBIO 7.0 register address/default/SMN headers:

- `nbio_7_0_offset.h` supplies the symbolic register offsets corresponding to the register names used here.
- `nbio_7_0_default.h` supplies generated defaults for many NBIO registers.
- `nbio_7_0_smn.h` supplies SMN addresses for selected NBIO/PCIe registers.
- AMDGPU helper macros such as `RREG32_SOC15`, `WREG32_SOC15`, `RREG32_PCIE`, `WREG32_PCIE`, `REG_SET_FIELD`, and `REG_GET_FIELD` pair addresses and field constants to access hardware.

Important integration points include:

- AMDGPU SOC15 initialization and NBIO v7.0 programming paths, which include this header and rely on generated shifts/masks for NBIO field updates.
- PCIe configuration and capability handling for endpoint functions exposed by the GPU, especially device/link control, AER, MSI/MSI-X, BAR sizing, power management, and extended capability traversal.
- SR-IOV/MxGPU/GPU-IOV virtualization flows, where PF/VF layout, VF BAR sizing, mailbox status, per-VF framebuffer allocation, and engine scheduler dwords must match both hardware and hypervisor expectations.
- IOMMU and PCIe isolation features through ACS, ATS, PASID, page request, ARI, multicast, TPH, and LTR fields.
- Error handling and diagnostics, where AER status/mask/severity, header logs, TLP prefix logs, link status, and lane equalization/status fields provide post-error evidence and control bits.
- Power-management code, including SMU/PowerPlay include paths that need NBIO field definitions while coordinating PCIe, DPA, LTR, OBFF, and PM capability state.

Because this file is generated, hand edits are a maintenance hazard. Correctness depends on consistency across the offset, default, SMN, and shift/mask headers for the same ASIC generation.

## Risks And Edge Cases

The main risk is silent hardware or PCI configuration-space misprogramming. These macros are untyped integer constants; an incorrect shift or mask can compile cleanly while changing the wrong bit or corrupting neighboring fields.

High-risk areas include:

- PCIe control fields: wrong payload size, read-request size, completion timeout, relaxed ordering, no-snoop, FLR, link retrain, target speed, or ASPM-related masks can cause link instability, bad performance, device reset failures, or broken enumeration.
- Interrupt capability programming: confusing MSI and MSI-X enable, mask, pending, table offset, or PBA fields can lose interrupts, generate spurious interrupts, or point the OS at the wrong MSI-X table/PBA.
- AER handling: status, mask, and severity groups have nearly identical field names. Mixing them can hide fatal errors, over-report benign errors, clear evidence before it is sampled, or fail to unmask important link/device failures.
- Virtualization: SR-IOV and GPU-IOV fields carry PF/VF layout, mailbox handshakes, reset controls, per-VF framebuffer sizing, and scheduler data. A bad field definition can break VF enumeration, corrupt VF memory partitioning, deadlock PF/VF mailbox exchange, or trigger incorrect FLR behavior.
- Address translation and isolation: ACS, ATS, PASID, page request, ARI, multicast, and TPH fields affect DMA routing and isolation. Incorrect masks can weaken peer-to-peer isolation, break IOMMU translation, or make PASID/page-request state inconsistent with the OS.
- Power management: DPA, power-budget, LTR, OBFF, and PM state fields influence latency and power policy. Misprogramming can cause unexpected wake behavior, performance cliffs, or link/power-state transition failures.
- Repetitive generated blocks: EPF1 and EPF2 contain many similarly named register families with endpoint-specific prefixes. Copying an EPF1 macro into an EPF2 path, or vice versa, may compile but target the wrong function's field layout.
- Chunk boundary splits: this range starts after the first EPF1 `DEVICE_CAP` shift definitions and ends before EPF2 `PCIE_ARI_CNTL` masks. The merge lane must reconcile adjacent chunks before making complete per-register conclusions.

## Test Signals

Useful validation signals are compile-time, generated-header, and hardware-behavior oriented:

- Kernel build coverage for AMDGPU SOC15/NBIO v7.0/SMU10 code that includes this header; missing or renamed macros should fail compilation.
- Generated-register-database comparison for lines 4970-7418 against AMD's authoritative NBIO 7.0 register descriptions, including endpoint prefixes, field widths, shifts, and masks.
- PCI enumeration and configuration-space dump checks for EPF1 and EPF2, confirming vendor/device/class/header/capability pointers, PM, PCIe, MSI/MSI-X, AER, BAR, ACS, ARI, SR-IOV, and VSEC layouts decode correctly.
- Link training and PCIe performance tests that exercise target speed, negotiated width/speed, read request size, payload size, completion timeout, LTR/OBFF, ASPM, and lane equalization fields.
- Interrupt tests covering MSI/MSI-X enable/disable, vector table/PBA offsets, mask/pending behavior, GPU interrupt delivery, suspend/resume, and reset recovery.
- AER injection or fault-observation tests for correctable and uncorrectable PCIe errors, validating status capture, mask/severity behavior, header/TLP prefix logging, and driver diagnostics.
- SR-IOV/GPU-IOV tests that create/destroy VFs, validate VF counts/stride/device IDs/VF BARs/page sizes, exercise PF/VF mailbox ack/valid bits, reset PF/VF paths, and verify per-VF framebuffer allocation.
- IOMMU/virtualization isolation tests for ACS, ATS, PASID, page request, ARI, multicast, and TPH fields under DMA, peer-to-peer, and VF workloads.
- Power-management tests across D-states, runtime PM, suspend/resume, DPA substates, LTR/OBFF policy, and link power transitions.

Regression symptoms from bad constants include failed PCI enumeration, missing interrupts, AER storms or hidden AER reports, failed FLR, broken SR-IOV VF creation, VF mailbox hangs, incorrect framebuffer partitioning, link retraining failures, DMA/IOMMU faults, or unstable runtime power transitions.

## Cross-Chunk Notes

This is one chunk of the large generated `nbio_7_0_sh_mask.h` register map. The previous chunk contains the beginning of EPF1 and the start of the EPF1 `DEVICE_CAP` group whose masks appear at the top of this range. The next chunk completes EPF2 `PCIE_ARI_CNTL` and continues later EPF2 capability/register definitions. The final per-file document should treat this chunk as hardware ABI metadata and merge endpoint/function register families across chunk boundaries.
