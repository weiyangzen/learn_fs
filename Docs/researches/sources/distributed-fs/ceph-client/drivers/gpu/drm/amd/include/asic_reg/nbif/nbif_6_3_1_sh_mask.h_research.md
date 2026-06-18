# Research: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbif/nbif_6_3_1_sh_mask.h

This per-file research report is synthesized from ordered chunk research reports.

## Chunk Map

- `subset-b-002877`: lines 1-2468, `Docs/researches/chunks/subset-b-002877_research.md`
- `subset-b-002878`: lines 2469-4902, `Docs/researches/chunks/subset-b-002878_research.md`
- `subset-b-002879`: lines 4903-7323, `Docs/researches/chunks/subset-b-002879_research.md`
- `subset-b-002880`: lines 7324-9850, `Docs/researches/chunks/subset-b-002880_research.md`
- `subset-b-002881`: lines 9851-12254, `Docs/researches/chunks/subset-b-002881_research.md`
- `subset-b-002882`: lines 12255-14840, `Docs/researches/chunks/subset-b-002882_research.md`
- `subset-b-002883`: lines 14841-17760, `Docs/researches/chunks/subset-b-002883_research.md`
- `subset-b-002884`: lines 17761-20123, `Docs/researches/chunks/subset-b-002884_research.md`
- `subset-b-002885`: lines 20124-22598, `Docs/researches/chunks/subset-b-002885_research.md`
- `subset-b-002886`: lines 22599-25014, `Docs/researches/chunks/subset-b-002886_research.md`
- `subset-b-002887`: lines 25015-27550, `Docs/researches/chunks/subset-b-002887_research.md`
- `subset-b-002888`: lines 27551-30056, `Docs/researches/chunks/subset-b-002888_research.md`
- `subset-b-002889`: lines 30057-32583, `Docs/researches/chunks/subset-b-002889_research.md`
- `subset-b-002890`: lines 32584-32806, `Docs/researches/chunks/subset-b-002890_research.md`

## Chunk Research

### subset-b-002877: lines 1-2468

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbif/nbif_6_3_1_sh_mask.h lines 1-2468

## Scope

This chunk covers the beginning of the generated NBIF 6.3.1 register shift/mask header. It starts with the license/header guard, defines the `IRQ_BRIDGE_CNTL` bridge-control bitfields, then maps a large part of the PCI configuration and PCIe extended capability space for `BIF_CFG_DEV0_EPF0`. Near the end it transitions into the virtual-function address block `nbif_bif_cfg_dev0_epf0_vf0_bifcfgdecp` and covers the VF0 PCI configuration space through the first masks for `BIF_CFG_DEV0_EPF0_VF0_PCIE_UNCORR_ERR_STATUS`.

The file is generated, data-only C preprocessor content. This chunk defines no functions, structs, variables, locks, allocations, persistence code, or direct MMIO operations. Its public surface is the generated pair convention:

- `<REGISTER>__<FIELD>__SHIFT`, the bit offset for a hardware field.
- `<REGISTER>__<FIELD>_MASK`, the mask used to isolate or compose that field.

The chunk ends mid-register after `BIF_CFG_DEV0_EPF0_VF0_PCIE_UNCORR_ERR_STATUS__CPL_ABORT_ERR_STATUS_MASK`; later VF0 AER masks and subsequent NBIF fields are in following chunks.

## Purpose

This header section provides the bit-level ABI between AMDGPU NBIF/NBIO code and NBIF 6.3.1 PCIe-facing hardware registers. The matching `nbif_6_3_1_offset.h` header supplies register addresses such as `regBIF_CFG_DEV0_EPF0_DEVICE_CNTL2` and the many `regBIF_CFG_DEV0_EPF0_*` configuration-space offsets; this file supplies the field positions and masks for those registers.

Consumers include this header together with AMDGPU register helpers such as `REG_SET_FIELD`, `REG_GET_FIELD`, `WREG32_FIELD15_PREREG`, `RREG32_SOC15`, `WREG32_SOC15`, `RREG32_PCIE`, and `WREG32_PCIE`. Direct inclusion is visible in `amdgpu/nbif_v6_3_1.c`, and sibling NBIO implementations show concrete use of shared fields such as `BIF_CFG_DEV0_EPF0_DEVICE_CNTL2__LTR_EN_MASK` when programming PCIe LTR and ASPM-related behavior.

## Important Macro Families

### Root/Bridge Control

`IRQ_BRIDGE_CNTL` maps legacy bridge-control bits such as parity response, SERR, ISA/VGA decode, master-abort mode, secondary bus reset, fast back-to-back enable, discard timers, and discard-timer SERR enable. These fields are low-level PCI bridge semantics. Incorrect values can affect error signaling, legacy decode, and reset behavior.

### PF0 Standard PCI Configuration Header

The `BIF_CFG_DEV0_EPF0_*` standard header fields cover:

- Identity and class: `VENDOR_ID`, `DEVICE_ID`, revision, programming interface, subclass, base class, header type, and BIST.
- PCI command/status: IO, memory, bus-master, parity-error response, SERR, interrupt disable, immediate readiness, capabilities-list presence, data parity, target/master abort, system-error, and parity-detected bits.
- BAR and ROM resources: `BASE_ADDR_1` through `BASE_ADDR_6`, `ROM_BASE_ADDR`, CardBus CIS pointer, subsystem/vendor IDs, interrupt line/pin, min grant, and max latency.
- Capability list entries: vendor capability, power-management capability, PCIe capability, MSI, MSI-X, vendor-specific capability, virtual channel, device serial number, AER, BAR enhancement, power budget, DPA, secondary PCIe, ACS, PASID, LTR, ARI, SR-IOV, data-link feature, 16 GT/s PHY, margining, VF resizable BAR, and 32 GT/s link capability blocks.

Most fields mirror PCI/PCIe configuration-space encodings. The generated names are long because they preserve the hardware address-block and function naming, but the underlying meaning follows PCIe capability structure layout.

### Power Management and Link Management

The PM capability group includes `PMI_CAP_LIST`, `PMI_CAP`, and `PMI_STATUS_CNTL`. These macros expose PM capability ID/next-pointer fields, PME clock/support, D1/D2 support, aux current, power state, PME enable/status, data select/scale, bus-power enable, and PMI data.

The PCIe capability and link groups include:

- `PCIE_CAP`, with version, device type, slot implemented, and interrupt message number.
- `DEVICE_CAP`, `DEVICE_CNTL`, and `DEVICE_STATUS`, with payload size support/control, error reporting enables/status, relaxed ordering, extended tags, no-snoop, max read request size, FLR, aux power, and pending transactions.
- `LINK_CAP`, `LINK_CNTL`, and `LINK_STATUS`, with supported/current speed, width, ASPM/PM support, exit latencies, link disable/retrain, common clock, clock power management, bandwidth interrupts/status, data-link active reporting, DRS signaling, and port number.
- `DEVICE_CAP2`, `DEVICE_CNTL2`, `DEVICE_STATUS2`, `LINK_CAP2`, `LINK_CNTL2`, and `LINK_STATUS2`, with completion timeout, ARI, atomic operations, ID-based ordering, LTR, emergency power reduction, ten-bit tags, OBFF, end-to-end TLP prefixes, supported link-speed vector, compliance controls, 8 GT/s equalization status, crosslink status, RTM presence, and DRS received status.

`DEVICE_CNTL2__LTR_EN_MASK` is an important active integration point. Sibling NBIO code toggles it depending on `adev->pdev->ltr_path` and clears it during some ASPM programming paths before writing `PCIE_LTR_CAP`.

### MSI and MSI-X

The PF0 interrupt capability groups include MSI and MSI-X list, control, address, data, mask, pending, table, and PBA fields. They cover 32-bit and 64-bit MSI message encodings, optional extended message data, per-vector masking, pending bits, MSI-X table size, function mask, enable bit, and BAR indicator/offset pairs for MSI-X table and PBA storage.

These fields back interrupt-delivery configuration. Wrong masks or shifts can corrupt interrupt-vector enablement, message address/data, or MSI-X table/PBA placement.

### Vendor, Virtual Channel, and Device Serial Number

`PCIE_VENDOR_SPECIFIC_*` defines the vendor-specific extended capability header and two scratch dwords. `PCIE_VC_*` defines port VC capability/control/status and VC0/VC1 resource capability/control/status fields including arbitration capability/table offset, TC/VC mapping, load-table/select bits, and negotiation-pending status. `PCIE_DEV_SERIAL_NUM_DW1/DW2` provide the lower and upper serial-number dwords.

Virtual channel fields are routing and traffic-class sensitive. The macros only describe layout; owning driver or firmware policy must decide whether and how VC resources are enabled.

### AER and Header Logging

The PF0 AER section covers:

- `PCIE_UNCORR_ERR_STATUS`, `PCIE_UNCORR_ERR_MASK`, and `PCIE_UNCORR_ERR_SEVERITY` for DLP, surprise down, poisoned TLP, flow control, completion timeout/abort, unexpected completion, receiver overflow, malformed TLP, ECRC, unsupported request, ACS violation, internal error, multicast blocked TLP, atomic-operation egress blocked, TLP-prefix blocked, and poisoned-TLP egress-blocked conditions.
- `PCIE_CORR_ERR_STATUS` and `PCIE_CORR_ERR_MASK` for receiver error, bad TLP/DLLP, replay rollover, replay timeout, advisory nonfatal, correctable internal error, and header-log overflow.
- `PCIE_ADV_ERR_CAP_CNTL`, with first-error pointer, ECRC generation/check capability and enable bits, multiple-header recording, TLP-prefix log presence, and completion-timeout log capability.
- Four TLP header log dwords and four TLP prefix log dwords.

These fields are status, mask, severity, and log surfaces for PCIe RAS/error-handling paths. Some status bits are sticky or clear-on-write according to PCIe rules; this header does not encode those sequencing rules.

### BAR Enhancement, Power Budget, DPA, and Secondary Link Capability

`PCIE_BAR*_CAP` and `PCIE_BAR*_CNTL` define supported BAR size, BAR index, total number, selected size, and upper supported-size fields for BAR1 through BAR6. `PCIE_PWR_BUDGET_*` exposes data selection, base power, scale, PM substate/state, type, rail, and system-allocated indicators. `PCIE_DPA_*` exposes dynamic power allocation substate count, transition latency, allocation scale, status/control, and eight per-substate power-allocation bytes.

`PCIE_SECONDARY_ENH_CAP_LIST`, `PCIE_LINK_CNTL3`, `PCIE_LANE_ERROR_STATUS`, and `PCIE_LANE_0_EQUALIZATION_CNTL` through `LANE_15_EQUALIZATION_CNTL` describe secondary PCIe capability data, link equalization control, per-lane error status, and 8 GT/s equalization preset fields for 16 lanes.

### ACS, PASID, LTR, ARI, and SR-IOV

The chunk defines access-control, process address space, latency tolerance, alternative routing, and virtualization capability fields:

- `PCIE_ACS_CAP` and `PCIE_ACS_CNTL` for source validation, translation blocking, P2P request/completion redirect, upstream forwarding, egress control, direct translated P2P, I/O request blocking, and egress vector count.
- `PCIE_PASID_CAP` and `PCIE_PASID_CNTL` for execute permission, privileged mode, max PASID width, and PASID enable.
- `PCIE_LTR_CAP` for snoop and no-snoop latency value/scale.
- `PCIE_ARI_CAP` and `PCIE_ARI_CNTL` for next-function number and function-group controls.
- `PCIE_SRIOV_*` for VF migration capability/status, VF enable, VF memory-space enable, ARI hierarchy, VF ten-bit tag support/enable, initial/total/active VF counts, function dependency link, first VF offset, VF stride, VF device ID, page-size bitmaps, VF BAR base addresses, and VF migration-state array location.

The SR-IOV fields are privilege- and isolation-sensitive. PF code must preserve correct VF counts, BAR windows, page size, ARI behavior, and memory-space enable state.

### Data Link Feature, 16 GT/s PHY, Margining, VF Resizable BAR, and 32 GT/s Link

The data-link feature capability maps local/remote supported feature bitmaps and exchange/valid bits. The 16 GT/s PHY group maps equalization completion and phase status, link-equalization request, local/RTM parity mismatch status, and 16 per-lane DSP/USP TX preset controls. The margining group maps capability/status and 16 per-lane control/status pairs for receiver number, margin type, usage model, and margin payload.

The VF resizable BAR group mirrors the BAR enhancement pattern for virtual-function BAR1 through BAR6, using `VF_BAR_SIZE_SUPPORTED`, `VF_BAR_INDEX`, `VF_BAR_TOTAL_NUM`, `VF_BAR_SIZE`, and upper supported-size fields. The PF0 32 GT/s group exposes equalization-bypass/no-EQ-needed capability and disable controls, modified TS usage-mode support/selection, and 32 GT/s equalization, enhanced behavior, precoding, and no-EQ-needed status.

These high-speed link and margining fields are diagnostics/tuning surfaces for PCIe Gen4/Gen5 style links. They should be programmed only by code that also owns the associated link-training protocol and polling/timeout behavior.

### VF0 PCI Configuration Space

The final part starts `nbif_bif_cfg_dev0_epf0_vf0_bifcfgdecp`, duplicating a VF0-specific subset of the PF0 PCI configuration layout. Covered VF0 families include:

- Vendor/device/class/revision/header/BAR/ROM/subsystem/interrupt fields.
- PCIe capability, device/link capability/control/status, and second-generation device/link capability/control/status.
- MSI and MSI-X capability fields.
- Vendor-specific capability fields.
- The AER capability list and the beginning of `VF0_PCIE_UNCORR_ERR_STATUS`.

Compared with the PF0 block, this VF0 section is a virtualized PCI function view. It must remain aligned with SR-IOV policy and with any VF config-space emulation or hardware exposure rules in the rest of the NBIF header.

## Control Flow and State Behavior

There is no executable control flow in this chunk. The generated macros affect behavior at compile time by determining how driver code composes and decodes 16-bit and 32-bit PCIe/NBIF register values.

The state represented by this chunk is hardware register state, mostly PCI/PCIe configuration-space state. Important state surfaces include bridge error/reset/decode bits, PF0 command/status, BAR/ROM/subsystem identity, power-management state and PME status, PCIe error-reporting enables/status, link speed/width/training/equalization state, MSI/MSI-X interrupt configuration, virtual channel mapping/status, AER masks/severity/logs, resizable BAR state, power budget/DPA fields, ACS/PASID/LTR/ARI controls, SR-IOV VF topology and VF BARs, data-link feature exchange status, 16 GT/s and 32 GT/s equalization state, lane margining controls/status, VF resizable BAR state, and the early VF0 configuration/AER state.

Several fields are status, sticky status, command-like, or capability descriptors rather than ordinary durable driver configuration. Examples include FLR initiation, link retrain, equalization request/status, AER status and header logs, MSI/MSI-X pending/mask bits, DPA substate control/status, SR-IOV VF enable and VF memory-space enable, data-link feature exchange enable/valid, lane margining controls/status, and VF0 uncorrectable error status. Correct users need PCIe ordering, read/modify/write, clear, polling, and timeout rules from the PCIe specification and owning AMDGPU code.

## Dependencies and Integration Points

This chunk depends on the generated AMD register-header convention:

- `nbif_6_3_1_offset.h` supplies the matching NBIF 6.3.1 register addresses and base indices.
- `nbif_6_3_1_default.h`, where present for a register family, supplies reset/default values.
- `soc15.h`, AMDGPU register helpers, and PCIe/NBIO accessors consume the `__SHIFT` and `_MASK` definitions to avoid hard-coded bit positions.

Observed and inferred integration points in this source tree include:

- `amdgpu/nbif_v6_3_1.c` directly includes this header while implementing NBIF 6.3.1 operations such as HDP remap, revision detection, memory-controller access enable, memory-size readout, and doorbell aperture/range programming. Those functions rely on the same generated NBIF register naming contract, although many of their active fields are outside this exact chunk.
- `amdgpu/nbio_v4_3.c`, `nbio_v2_3.c`, `nbio_v6_1.c`, and `nbio_v7_4.c` show the same `BIF_CFG_DEV0_EPF0_DEVICE_CNTL2__LTR_EN_MASK` integration pattern for LTR and ASPM programming. NBIF 6.3.1 consumers should use the matching NBIF 6.3.1 offsets with these masks rather than copying offsets from another generation.
- PCI core, platform firmware, and hardware also interact with the same configuration-space fields. Driver code must preserve externally owned PCI config bits unless it explicitly owns the capability being changed.
- SR-IOV and virtualization paths depend on PF0 SR-IOV fields and VF0 config-space layouts being accurate and mutually consistent.
- Error handling, RAS, diagnostics, and debug tools depend on the AER status/mask/severity/header-log fields and high-speed link equalization/margining fields being decoded exactly.

## Risks

- Bitfield drift is high impact. A wrong mask or shift can corrupt adjacent PCIe configuration fields, causing missing memory/bus-master enablement, lost interrupts, broken link policy, invalid BAR sizing, incorrect error reporting, or VF isolation problems.
- The PF0 and VF0 families are similar but not interchangeable. Accidentally using a PF0 macro on a VF0 register, or vice versa, can silently address the wrong hardware view.
- PCIe capability blocks contain many status and command bits with specification-defined write semantics. Treating status bits as normal read/write configuration can clear errors, trigger FLR/retrain/compliance behavior, or leave link state inconsistent.
- LTR, ASPM, DPA, power budget, and emergency power-reduction fields are coordinated with platform PCIe policy. Incorrect writes can increase latency, break power management, or prevent low-power entry/exit.
- MSI/MSI-X fields affect interrupt routing. Incorrect address, data, table, PBA, enable, mask, or pending handling can lose interrupts or route them to the wrong vector.
- AER masks and severity bits are RAS-sensitive. Bad encodings can hide fatal PCIe errors, over-report benign conditions, or mislead recovery logic.
- ACS, PASID, ARI, and SR-IOV fields are security/isolation sensitive. Incorrect control, VF count/stride, page-size, or VF BAR programming can break DMA isolation or expose invalid virtual-function resources.
- Link equalization, 16 GT/s/32 GT/s, and margining controls are protocol-sensitive. Driver-side experimentation without the required training/polling sequence can destabilize PCIe links.
- The chunk boundary is mid-family in `VF0_PCIE_UNCORR_ERR_STATUS`; the final per-file merge must combine later chunks before making complete claims about VF0 AER handling.

## Test and Validation Signals

Useful validation is mostly build, PCIe bring-up, and hardware integration coverage:

- Build AMDGPU with NBIF 6.3.1 enabled; this catches missing, renamed, or malformed generated macros included by `amdgpu/nbif_v6_3_1.c`.
- PCI enumeration and probe tests should verify vendor/device/class, command/status, BAR, ROM, subsystem, and capability-list fields remain decodable.
- LTR/ASPM tests should cover paths that toggle `BIF_CFG_DEV0_EPF0_DEVICE_CNTL2__LTR_EN_MASK` and program `PCIE_LTR_CAP`, then verify link-power behavior and wake/latency behavior.
- Interrupt tests should exercise MSI and MSI-X enablement, address/data programming, masking, pending bits, table/PBA offsets, and interrupt delivery under load.
- AER/RAS tests should inject or observe correctable and uncorrectable PCIe errors, verify status/mask/severity decoding, confirm header/TLP-prefix log capture, and validate clear behavior.
- SR-IOV validation should enable VFs, check initial/total/active VF counts, first-VF offset, VF stride, VF BAR windows, page-size fields, VF memory-space enable, and VF0 config-space visibility.
- Link-training diagnostics should verify 8 GT/s, 16 GT/s, and 32 GT/s equalization status fields, lane error status, parity mismatch status, data-link feature exchange, and margining status on capable hardware.
- Resizable BAR and VF resizable BAR tests should verify supported-size and selected-size encoding for BAR1 through BAR6 and ensure host-visible resource sizes match the programmed fields.

## Unresolved Cross-Chunk References

This is the first chunk of a much larger generated header. It does not include later NBIF 6.3.1 blocks for additional VF configuration spaces, doorbells, memory-controller aperture registers, remap/HDP fields, or other NBIF-specific control/status registers used by `nbif_v6_3_1.c`. It also ends in the middle of `BIF_CFG_DEV0_EPF0_VF0_PCIE_UNCORR_ERR_STATUS`; later chunks must supply the remaining VF0 AER masks and subsequent VF0 capability/register families before the final source-file report can describe the complete file.

### subset-b-002878: lines 2469-4902

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbif/nbif_6_3_1_sh_mask.h lines 2469-4902

## Scope

This chunk covers generated shift and mask macros for the NBIF 6.3.1 PCIe configuration-space view of SR-IOV virtual functions. It starts in the middle of the `BIF_CFG_DEV0_EPF0_VF0_PCIE_UNCORR_ERR_STATUS` mask list, then finishes VF0's PCIe advanced error reporting and ARI fields. It then covers complete repeated config-space field maps for `VF1`, `VF2`, and `VF3`, and ends after the first field of `VF4_PCIE_CAP`.

The covered address blocks are:

- Tail of `nbif_bif_cfg_dev0_epf0_vf0_bifcfgdecp`: AER uncorrectable/correctable error masks and status, AER header/TLP-prefix logs, and ARI enhanced capability fields.
- Full `nbif_bif_cfg_dev0_epf0_vf1_bifcfgdecp`, `vf2_bifcfgdecp`, and `vf3_bifcfgdecp`: conventional PCI header fields, PCIe capability fields, MSI/MSI-X capability fields, vendor-specific enhanced capability fields, AER fields, header/TLP-prefix logs, and ARI fields.
- Beginning of `nbif_bif_cfg_dev0_epf0_vf4_bifcfgdecp`: conventional PCI header fields through `VF4_PCIE_CAP__VERSION__SHIFT`.

The file is a generated hardware register bitfield map. This chunk defines preprocessor constants only. It has no C functions, structs, variables, executable logic, dynamic allocation, or local persistence.

## Purpose

The purpose of this header section is to give AMDGPU/NBIF code symbolic access to bit positions in PCI/PCIe configuration registers exposed for virtual functions behind device 0, endpoint function 0. Each field is represented by the standard AMD generated pair:

- `<REGISTER>__<FIELD>__SHIFT`, the field's bit offset.
- `<REGISTER>__<FIELD>_MASK`, the mask used to isolate or compose that field.

The sibling `nbif_6_3_1_offset.h` file supplies the matching `cfgBIF_CFG_DEV0_EPF0_VF*_*` and `regBIF_CFG_DEV0_EPF0_VF*_*` register addresses. Driver code includes this mask header from `amdgpu/nbif_v6_3_1.c` and uses the broader AMD register-helper convention (`REG_SET_FIELD`, `REG_GET_FIELD`, `RREG32_SOC15`, `WREG32_SOC15`, and related helpers) to build or decode register values without hard-coding bit numbers.

## Important Macro Families

### Conventional PCI Header Fields

The complete VF1/VF2/VF3 blocks and the partial VF4 block define the basic PCI configuration header:

- Identity and class fields: `VENDOR_ID`, `DEVICE_ID`, `REVISION_ID`, `PROG_INTERFACE`, `SUB_CLASS`, and `BASE_CLASS`.
- Command/status fields: `COMMAND` exposes IO, memory, bus-master, parity, SERR, fast back-to-back, and interrupt-disable bits; `STATUS` exposes interrupt status, capability-list presence, data parity, DEVSEL timing, abort, SERR, and parity status.
- Header and resource fields: `CACHE_LINE`, `LATENCY`, `HEADER`, `BIST`, `BASE_ADDR_1` through `BASE_ADDR_6`, `CARDBUS_CIS_PTR`, `ADAPTER_ID`, `ROM_BASE_ADDR`, and `CAP_PTR`.
- Legacy interrupt hints: `INTERRUPT_LINE`, `INTERRUPT_PIN`, `MIN_GRANT`, and `MAX_LATENCY`.

These macros mirror PCI config-space layout for each VF. The VF blocks use the same field layout while the offset header assigns each VF a distinct register window.

### PCIe Capability and Link Fields

For VF1 through VF3, and the start of VF4, the chunk defines PCIe capability-list and device/link capability fields:

- `PCIE_CAP_LIST` and `PCIE_CAP` encode capability ID, next pointer, version, device type, slot-implemented state, and interrupt message number.
- `DEVICE_CAP`, `DEVICE_CNTL`, and `DEVICE_STATUS` describe payload size support and programming, error-reporting enables/status, relaxed ordering, extended tags, no-snoop behavior, read request size, FLR capability/initiation, auxiliary power, pending transactions, and emergency power-reduction status.
- `LINK_CAP`, `LINK_CNTL`, and `LINK_STATUS` describe link speed, width, power-management support, L0s/L1 latencies, clock power management, surprise-down reporting, data-link active reporting, bandwidth notifications, ASPM optionality, port number, link disable/retrain controls, common clock, extended sync, autonomous width control, DRS signaling, current negotiated speed/width, training state, slot clock, and link bandwidth status.
- `DEVICE_CAP2`, `DEVICE_CNTL2`, `DEVICE_STATUS2`, `LINK_CAP2`, `LINK_CNTL2`, and `LINK_STATUS2` cover completion timeout ranges, ARI forwarding, AtomicOp capability and request controls, ID-based ordering, LTR, ten-bit tags, OBFF, TLP prefix support/blocking, emergency power-reduction fields, FRS support, supported link speeds, compliance controls, de-emphasis, equalization status, crosslink/RTM presence, downstream component presence, and DRS message receipt.

These are not policy code; they encode the bit ABI for PCIe capability state that the hardware exposes for each virtual function.

### MSI and MSI-X Fields

The VF1/VF2/VF3 blocks define both MSI and MSI-X capability registers:

- `MSI_CAP_LIST`, `MSI_MSG_CNTL`, `MSI_MSG_ADDR_LO`, `MSI_MSG_ADDR_HI`, `MSI_MSG_DATA`, `MSI_EXT_MSG_DATA`, `MSI_MASK`, `MSI_MSG_DATA_64`, `MSI_EXT_MSG_DATA_64`, `MSI_MASK_64`, `MSI_PENDING`, and `MSI_PENDING_64`.
- `MSIX_CAP_LIST`, `MSIX_MSG_CNTL`, `MSIX_TABLE`, and `MSIX_PBA`.

Important fields include MSI enable, multi-message capability/enable, 64-bit support, per-vector masking capability, extended message data capability/enable, message address/data masks, vector mask and pending bits, MSI-X table size, function mask, MSI-X enable, table BIR/offset, and pending-bit-array BIR/offset.

These definitions are integration points for interrupt routing and virtualization setup. Incorrect field definitions would misprogram message addresses/data, vector masking, or MSI-X table/PBA decoding.

### Vendor-Specific Enhanced Capability Fields

For VF1 through VF3, the chunk defines:

- `PCIE_VENDOR_SPECIFIC_ENH_CAP_LIST`, with capability ID, version, and next pointer.
- `PCIE_VENDOR_SPECIFIC_HDR`, with VSEC ID, revision, and length.
- `PCIE_VENDOR_SPECIFIC1` and `PCIE_VENDOR_SPECIFIC2`, each exposing a full 32-bit data field.

These provide generic bit access for AMD/vendor-specific PCIe extended capability payloads associated with the VF config space.

### Advanced Error Reporting and ARI Fields

The chunk is heavily weighted toward AER fields for VF0 through VF3:

- `PCIE_ADV_ERR_RPT_ENH_CAP_LIST` encodes AER capability ID, version, and next pointer.
- `PCIE_UNCORR_ERR_STATUS`, `PCIE_UNCORR_ERR_MASK`, and `PCIE_UNCORR_ERR_SEVERITY` cover DLP errors, surprise-down, poisoned TLP, flow-control errors, completion timeout/abort, unexpected completion, receiver overflow, malformed TLP, ECRC, unsupported request, ACS violation, internal errors, multicast-blocked TLP, AtomicOp egress blocking, TLP prefix blocking, and poisoned-TLP egress blocking.
- `PCIE_CORR_ERR_STATUS` and `PCIE_CORR_ERR_MASK` cover receiver errors, bad TLP/DLLP, replay rollover, replay timer timeout, advisory non-fatal errors, corrected internal errors, and header-log overflow.
- `PCIE_ADV_ERR_CAP_CNTL` exposes first-error pointer, ECRC generation/check capabilities and enables, multi-header-recording capability/enable, TLP prefix log presence, and completion-timeout log capability.
- `PCIE_HDR_LOG0` through `PCIE_HDR_LOG3` and `PCIE_TLP_PREFIX_LOG0` through `PCIE_TLP_PREFIX_LOG3` expose full 32-bit header or prefix log words.
- `PCIE_ARI_ENH_CAP_LIST`, `PCIE_ARI_CAP`, and `PCIE_ARI_CNTL` expose ARI capability ID/version/next pointer, MFVC/ACS function-group capability/enables, next function number, and function group selection.

The VF0 portion is partial because the chunk begins after the first uncorrectable-error status shifts and lower mask bits. The AER/ARI layout is complete for VF1 through VF3.

## Control Flow and State Behavior

This header has no runtime control flow. Its only behavior is compile-time substitution of bit positions and masks into code that reads or writes NBIF registers.

The state represented by these macros lives in hardware PCIe configuration space and NBIF register windows. Some fields are stable descriptors, such as vendor/device IDs, class codes, capability IDs, next capability pointers, capability versions, BAR masks, link capability flags, and MSI-X table/PBA layout. Other fields are mutable controls, such as `COMMAND` memory and bus-master enables, PCIe error-reporting enables, payload/read-request size controls, FLR initiation, link retrain/disable, MSI/MSI-X enables, MSI vector masks, AER error masks/severity, ECRC enables, ARI forwarding, AtomicOp request enable, LTR enable, OBFF enable, and TLP prefix blocking.

Several fields are status or log surfaces rather than persistent software-owned configuration. Examples include PCI `STATUS`, `DEVICE_STATUS`, `LINK_STATUS`, `LINK_STATUS2`, MSI pending bits, AER uncorrectable/correctable status registers, AER header logs, and TLP prefix logs. These may be hardware-updated, sticky, clear-on-write, or consumed according to PCIe/AER semantics; the generated macros do not encode ordering, clear rules, or polling policy.

## Dependencies and Integration Points

This chunk depends on the generated AMD register-header convention:

- `nbif_6_3_1_offset.h` supplies matching config-space offsets and MMIO register addresses. The offset header shows repeated VF windows, for example `VF1` at the `0x184xx` register range, `VF2` at `0x188xx`, `VF3` at `0x18cxx`, and `VF4` beginning at `0x190xx` for this family.
- `nbif_6_3_1_sh_mask.h` supplies the bit positions and masks described here.
- `amdgpu/nbif_v6_3_1.c` includes both headers and is the direct NBIF 6.3.1 integration point in this source tree. That implementation primarily programs NBIF memory, doorbell, interrupt, and PCIe-related state through AMD register helpers; the VF config-space symbols are available to the same compilation unit when PF/VF configuration fields need to be decoded or programmed.
- Broader AMDGPU and Linux PCI/SR-IOV paths rely on the hardware presenting correct PCIe capability, MSI/MSI-X, AER, and ARI state for virtual functions.

The repeated VF layout also lines up with nearby generated NBIO/NBIF generations, but consumers must include the exact NBIF 6.3.1 offset/mask pair. Similar names in `nbio_*_sh_mask.h` or other NBIF versions are not safe substitutes because register bases, presence, and field layouts can drift across IP versions.

## Risks

- Bitfield drift is high impact. A wrong shift or mask can write unrelated PCIe config-space bits, affecting VF enumeration, bus mastering, memory access, interrupts, link management, error reporting, or FLR.
- The repeated VF blocks are mechanically similar and easy to corrupt by copy/paste or generator mistakes. A single VF-specific typo can make only one virtual function misreport capabilities or mishandle interrupts/errors.
- The chunk boundaries are partial. It starts mid-register in VF0 and ends mid-register in VF4. A final merged report must stitch adjacent chunks to avoid presenting VF0 or VF4 as complete here.
- MSI/MSI-X fields are interrupt-sensitive. Misprogrammed message addresses/data, mask bits, MSI-X table offsets, or PBA offsets can cause lost interrupts, spurious interrupts, or interrupts delivered to the wrong vector.
- AER fields are diagnostic and recovery-sensitive. Incorrect uncorrectable/correctable status, mask, or severity bits can hide PCIe errors, classify recoverable events incorrectly, or leave sticky error state uncleared.
- FLR, bus-master, memory-space, ARI, AtomicOp, ACS, and TLP-prefix controls are virtualization-sensitive. Wrong values can break VF reset behavior, DMA authorization, function discovery, isolation, or PCIe transaction handling.
- Full-width log/data fields such as BARs, MSI addresses, vendor-specific payloads, AER header logs, and TLP prefix logs use `0xFFFFFFFFL` masks; callers must know whether a register is read-only, writeable, write-one-to-clear, or hardware-owned before writing.

## Test and Validation Signals

Useful validation is mostly build, enumeration, and hardware integration coverage:

- Build AMDGPU with NBIF 6.3.1 enabled so `amdgpu/nbif_v6_3_1.c` includes `nbif_6_3_1_offset.h` and `nbif_6_3_1_sh_mask.h` without missing or conflicting macros.
- SR-IOV enumeration should show VF1/VF2/VF3, and adjacent chunks' VF0/VF4, with expected vendor/device IDs, class codes, BAR layout, capability chains, PCIe capability values, and ARI capability state.
- PCIe link diagnostics should report expected link speed/width, training, DL active, bandwidth status, link-capability flags, and Gen3+ equalization fields where applicable.
- MSI/MSI-X tests should verify VF interrupt enable/disable, vector mask/pending behavior, MSI-X table and PBA decoding, and interrupt delivery under load.
- AER injection or error-path tests should validate uncorrectable/correctable status bits, masks, severity selection, first-error pointer, ECRC controls, header logs, and TLP-prefix logs.
- VF reset tests should cover `DEVICE_CNTL__INITIATE_FLR`, transaction-pending behavior, bus-master/memory enable transitions, and post-reset config-space restoration.
- Virtualization isolation tests should cover ARI forwarding/function-group fields, ACS violation reporting, AtomicOp egress/request behavior, and poisoned/TLP-prefix blocking status.

## Unresolved Cross-Chunk References

Line 2469 starts inside `BIF_CFG_DEV0_EPF0_VF0_PCIE_UNCORR_ERR_STATUS`; the lower masks and all shifts for that register are in the previous chunk. Line 4902 stops after `BIF_CFG_DEV0_EPF0_VF4_PCIE_CAP__VERSION__SHIFT`; the rest of `VF4_PCIE_CAP` and VF4's later PCIe/MSI/MSI-X/AER/ARI fields continue in the next chunk.

### subset-b-002879: lines 4903-7323

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbif/nbif_6_3_1_sh_mask.h lines 4903-7323

## Purpose

This chunk is part of AMDGPU's generated NBIF 6.3.1 register bitfield mask header. It provides C preprocessor constants for bit shifts and masks used to access PCI configuration-space and PCIe extended-capability fields exposed through NBIF BIF config decoder address blocks. The macros are data definitions only: they do not execute logic, allocate state, or declare functions. Driver code includes this header alongside matching register-offset headers and uses the `*_SHIFT` and `*_MASK` constants to pack, unpack, set, and test fields in MMIO/config-register values.

The visible range covers virtual-function-oriented register definitions under `BIF_CFG_DEV0_EPF0_VF*`:

- The start of the chunk continues `VF4` PCIe capability definitions from a previous chunk, beginning at `BIF_CFG_DEV0_EPF0_VF4_PCIE_CAP__DEVICE_TYPE__SHIFT`.
- It completes the rest of `VF4` PCIe capability, MSI/MSI-X, vendor-specific, advanced error reporting, header log, TLP prefix log, and ARI mask definitions through `BIF_CFG_DEV0_EPF0_VF4_PCIE_ARI_CNTL`.
- It fully covers `addressBlock: nbif_bif_cfg_dev0_epf0_vf5_bifcfgdecp`.
- It fully covers `addressBlock: nbif_bif_cfg_dev0_epf0_vf6_bifcfgdecp`.
- It begins `addressBlock: nbif_bif_cfg_dev0_epf0_vf7_bifcfgdecp` and runs through the first `BIF_CFG_DEV0_EPF0_VF7_MSIX_MSG_CNTL__MSIX_TABLE_SIZE__SHIFT` macro; later `VF7` MSI-X and extended capability masks continue in the next chunk.

## Important Definitions

The exported API surface in this chunk is entirely macro names. Each register field usually has two macros:

- `...__FIELD__SHIFT`: bit index to shift a raw field value into or out of the register word.
- `...__FIELD_MASK`: bit mask for the encoded field within the register word.

Major register families in this chunk are:

- Standard PCI config header fields for `VF5`, `VF6`, and partially `VF7`: vendor/device IDs, command/status, revision/class, cache line, latency, header type, BIST, BARs, CardBus pointer, subsystem adapter ID, ROM base address, capability pointer, interrupt line/pin, min grant, and max latency.
- PCI command/status fields: I/O, memory, bus mastering, special cycles, memory write invalidate, VGA palette snoop, parity/error enables, SERR, fast back-to-back, interrupt disable, and status bits such as capability list, interrupt status, devsel timing, target/master aborts, system error, parity error, and immediate read readiness.
- PCIe capability set for `VF4`-`VF7`: `PCIE_CAP_LIST`, `PCIE_CAP`, `DEVICE_CAP`, `DEVICE_CNTL`, `DEVICE_STATUS`, `LINK_CAP`, `LINK_CNTL`, `LINK_STATUS`, `DEVICE_CAP2`, `DEVICE_CNTL2`, `DEVICE_STATUS2`, `LINK_CAP2`, `LINK_CNTL2`, and `LINK_STATUS2`.
- MSI and MSI-X definitions: capability list headers, MSI enable and multi-message controls, 32/64-bit message address/data registers, per-vector masks and pending bits, MSI-X table/PBA BIR and offset fields, and function mask / enable bits.
- Vendor-specific PCIe enhanced capability headers and scratch registers.
- Advanced Error Reporting definitions for `VF4`-`VF6`: AER capability list headers, uncorrectable error status/mask/severity, correctable error status/mask, AER capability/control, header logs, and TLP prefix logs.
- ARI enhanced capability definitions for `VF4`-`VF6`: MFVC function groups, ACS function groups, next-function number, and ARI forwarding controls.

No structs, enums, typedefs, or functions are defined in this range.

## Control Flow

There is no runtime control flow in this chunk. The practical "flow" is compile-time selection by macro name:

1. A consumer reads a register using the corresponding NBIF register offset from sibling generated headers.
2. It extracts a field with `(value & FIELD_MASK) >> FIELD_SHIFT`, or prepares an update by clearing `FIELD_MASK` and ORing a shifted field value.
3. It writes the resulting register value back through AMDGPU register access helpers.

The repetition across `VF5`, `VF6`, and `VF7` implies table-like hardware layout, but the header itself does not encode loops or iteration. Any iteration over virtual functions is handled by driver code that chooses the proper register offset and mask macro family.

## State and Persistence Behavior

This header does not hold software state. The state described by the macros lives in GPU/NBIF hardware registers and PCI configuration space. Many fields represent persistent or semi-persistent hardware configuration until reset, function-level reset, power transition, or firmware/hardware update, including BAR base addresses, command enables, link controls, MSI/MSI-X configuration, and AER masks/severity selections.

Several status/log fields are hardware-owned observations rather than driver-owned state:

- `DEVICE_STATUS`, `LINK_STATUS`, and `LINK_STATUS2` expose current PCIe link and transaction state.
- AER status registers report correctable and uncorrectable error conditions.
- header log and TLP prefix log registers capture error context.
- MSI pending registers expose pending interrupt-vector state.

Some fields can be write-one-to-clear or otherwise have PCIe-defined side effects in the underlying hardware, but this header does not document those semantics. Consumers must rely on PCIe/NBIF programming rules and existing AMDGPU access wrappers.

## Dependencies and Integration Points

The chunk depends only on the C preprocessor. It is intended to be included by AMDGPU NBIF and PCIe code together with generated register-offset headers for the same ASIC generation, commonly named in the same `asic_reg/nbif` area. The mask names are tightly coupled to the register names in those offset headers; using a mask with the wrong offset family can silently target the wrong bits.

Integration points include:

- AMDGPU NBIF initialization and reset paths that configure PCIe device, link, and function-level behavior.
- SR-IOV / virtual function handling, because the covered register blocks are `VF4` through `VF7`.
- PCIe error reporting paths that inspect or mask AER status for DLP, surprise-down, completion timeout/abort, unexpected completion, receiver overflow, malformed TLP, ECRC, unsupported request, ACS violation, internal errors, atomic-op egress blocking, TLP prefix blocking, and poisoned TLP egress blocking.
- Interrupt setup paths for MSI/MSI-X message address/data, vector masks, pending bits, table location, PBA location, and enable/function-mask control.
- Link-management diagnostics and policy code that reads current speed/width/training state or adjusts target speed, compliance mode, autonomous speed/width disable, ASPM/power management, common clock, extended sync, DRS signaling, and equalization-related status.

Because this is generated ASIC data, the source of truth is likely an AMD register database rather than handwritten driver logic. Edits should be treated as hardware contract changes.

## Risks

- Boundary risk: this chunk starts after the `VF4_PCIE_CAP__VERSION__SHIFT` macro and ends before the rest of `VF7_MSIX_MSG_CNTL`; the final merged report must combine adjacent chunks to avoid presenting partial VF4/VF7 coverage as complete.
- Copy/paste or generation drift can be severe. `VF5` and `VF6` are structurally identical in this span, while `VF7` is partial here. A single wrong mask width, shift, or suffix can cause register writes to corrupt adjacent PCIe fields.
- Several mask names include repeated semantic words, such as `...PCIE_UNCORR_ERR_MASK__DLP_ERR_MASK_MASK`; this is expected from `register__field_MASK` naming and should not be "cleaned up" manually.
- Width differences matter. Some fields are 16-bit PCI config words (`0xFFFFL`-style masks), while others are 32-bit capability or log dwords (`0xFFFFFFFFL`). Consumers must use access widths matching the actual register definition.
- AER and status/log fields may have side effects on write or clear operations. The macros do not protect against unsafe read-modify-write behavior.
- MSI/MSI-X fields affect interrupt delivery. Incorrect enable, function mask, table BIR, table offset, PBA BIR, or message address/data masks can produce lost interrupts, spurious interrupts, or device isolation issues under virtualization.
- SR-IOV-specific register access must respect function isolation. Accidentally applying a `VF5` macro to a `VF6`/`VF7` offset, or vice versa, is syntactically valid C but semantically wrong.

## Test Signals

Useful validation signals for changes touching this chunk include:

- Build coverage for AMDGPU with this generated header included, especially configurations that enable SR-IOV, NBIF, PCIe AER, MSI, and MSI-X paths.
- Static checks that every `__SHIFT`/`_MASK` pair has consistent field width and no overlap within a register block unless overlapping is hardware-intended.
- Generated-header consistency checks against the ASIC register database or against sibling `nbif_6_3_1` offset/default headers.
- Runtime smoke tests that enumerate the GPU and its virtual functions, read PCI config capability lists, and verify expected PCIe/PCI capability traversal.
- MSI/MSI-X interrupt tests under physical and virtualized GPU configurations.
- PCIe link-state diagnostics confirming reported speed, width, training, equalization, and DRS bits match hardware/firmware expectations.
- AER injection or fault-observation tests, where available, confirming uncorrectable/correctable status, masks, severity, header logs, and TLP prefix logs decode to the expected bit names.

## Chunk-Specific Notes for Merge

This chunk should be merged with adjacent chunks for the same source file before producing the final source-tree-aligned per-file research document. The merge should preserve that the source file as a whole is a generated NBIF 6.3.1 shift/mask catalog, while this chunk specifically represents `VF4` tail coverage, full `VF5`/`VF6` coverage, and `VF7` early coverage through the start of MSI-X message control.

### subset-b-002880: lines 7324-9850

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbif/nbif_6_3_1_sh_mask.h lines 7324-9850

## Purpose

This chunk is part of the generated AMD NBIF 6.3.1 register field header. It defines C preprocessor constants for bit shifts and bit masks used to read, compose, and update PCIe/NBIO register fields for AMDGPU. The companion offset header supplies register addresses; this header supplies field layout. The chunk contains about 2,109 `#define`s across roughly 390 register names, mostly in one-to-one `__SHIFT` and `_MASK` pairs.

The slice starts in the tail of the `BIF_CFG_DEV0_EPF0_VF7` PCIe virtual-function capability space, covers the full `BIF_CFG_DEV0_EPF1` endpoint function configuration space, then moves through NBIF/BIF system, RCC downstream/upstream/endpoint, doorbell, RAS, BACO, HDP remap, framebuffer access, and BIF ring controls. It ends at the start of `nbif_rcc_dev0_BIFDEC1`.

## Important Definitions

There are no functions, structs, or runtime types in this chunk. The public API is the macro naming convention consumed by register helpers such as `REG_SET_FIELD()`, `REG_GET_FIELD()`, `RREG32_SOC15()`, `WREG32_SOC15()`, and display register table initializers.

Key macro families in this chunk:

- `BIF_CFG_DEV0_EPF0_VF7_*`: final PCIe capability fields for virtual function 7, including MSI-X table/PBA, vendor-specific capabilities, AER uncorrectable/correctable status/mask/severity, header/TLP-prefix logs, and ARI capability/control.
- `BIF_CFG_DEV0_EPF1_*`: endpoint function 1 PCI configuration and extended capability space. This includes standard PCI IDs and BARs, command/status, PM capability, PCIe capability, MSI/MSI-X, VSEC, device serial number, AER, resizable BAR, power budget, DPA, secondary PCIe capability, lane equalization, ACS, PASID, LTR, ARI, SR-IOV, and VF resizable BAR definitions.
- `BIF_BX_PF0_*`: PF0 MMIO/RSMU index/data access registers that act as indirect access windows.
- `BIF_BX0_*`: NBIF system registers for PCIe indirect access, S/BIOS/driver/firmware scratch registers, interrupt controls, GFX MMIO register CAM/remap controls, doorbell controls, framebuffer access enables, BACO power controls, HDP remap flush controls, BIF ring controls, mailbox index, MP1 interrupt state, and physical pad controls.
- `RCC_DWN_DEV0_0_*`, `RCC_DWNP_DEV0_0_*`, and `RCC_EP_DEV0_0_*`: RCC downstream, downstream-port, and endpoint-side PCIe control/status/strap fields, including link speed/control, LTR messaging, DPA power allocation, PME, requester ID, error, RX, and TX controls.

Representative high-impact fields include:

- `BIF_CFG_DEV0_EPF1_DEVICE_CNTL__INITIATE_FLR_MASK`, error reporting enables, max payload size, max read request size, relaxed ordering, no-snoop, and extended tag controls.
- `BIF_CFG_DEV0_EPF1_DEVICE_CNTL2__LTR_EN_MASK`, completion timeout, ARI forwarding, atomic operation, ID-based ordering, OBFF, and ten-bit tag controls.
- `BIF_CFG_DEV0_EPF1_PCIE_SRIOV_CONTROL__SRIOV_VF_ENABLE_MASK`, `SRIOV_VF_MSE`, migration enables, ARI hierarchy, and VF ten-bit tag requester enable.
- AER fields for DLP, surprise down, poisoned TLP, flow control, completion timeout/abort, unexpected completion, receiver overflow, malformed TLP, ECRC, unsupported request, ACS violation, internal error, multicast blocked TLP, atomic egress blocking, TLP-prefix blocking, and poisoned TLP egress blocking.
- `BIF_BX0_BIF_FB_EN__FB_READ_EN_MASK` and `__FB_WRITE_EN_MASK`, which gate NBIF access to framebuffer memory.
- `BIF_BX0_REMAP_HDP_MEM_FLUSH_CNTL__ADDRESS_MASK` and `BIF_BX0_REMAP_HDP_REG_FLUSH_CNTL__ADDRESS_MASK`, which encode remapped KFD HDP flush registers.
- `BIF_BX0_BIF_DOORBELL_INT_CNTL__RAS_*`, `DOORBELL_INTERRUPT_*`, and `TIMEOUT_ERR_EVENT_INTERRUPT_ENABLE_MASK`, which expose RAS and doorbell interrupt status/clear/disable bits.
- `BIF_BX0_BACO_CNTL__BACO_EN_MASK`, `BACO_DUMMY_EN`, `BACO_POWER_OFF`, `BACO_MODE`, `RCU_BIF_CONFIG_DONE`, `PWRGOOD_VDDSOC`, and `BACO_AUTO_EXIT`, plus the BACO exit timer fields.
- `BIF_BX0_BIF_RB_CNTL__RB_ENABLE_MASK`, `RB_SIZE`, writeback, overflow-clear, FLR-reset-disable, and BIF ring pointer/base address fields.

## Control Flow And Data Flow

This file has no executable control flow. Its effect is compile-time expansion into constants used by the AMDGPU NBIF implementation and related display code.

The normal data flow is:

1. A driver source includes `nbif_6_3_1_offset.h` for register addresses and `nbif_6_3_1_sh_mask.h` for field positions.
2. The driver reads a 32-bit register with an SOC15 access macro, or receives a value from PCI config/indirect access.
3. `REG_GET_FIELD()` extracts a field by applying `<register>__<field>_MASK` and `<register>__<field>__SHIFT`.
4. `REG_SET_FIELD()` clears and inserts a field value using the same macro pair.
5. The updated value is written back through `WREG32_SOC15()` or a related MMIO helper.

Observed integration in this source tree:

- `amdgpu/nbif_v6_3_1.c` includes this header directly. It programs `BIF_BX0_REMAP_HDP_MEM_FLUSH_CNTL` and `BIF_BX0_REMAP_HDP_REG_FLUSH_CNTL` from `adev->rmmio_remap.reg_offset`, toggles framebuffer access through `BIF_BX0_BIF_FB_EN`, configures interrupt handling through `BIF_BX0_INTERRUPT_CNTL`, and manipulates `BIF_BX0_BIF_DOORBELL_INT_CNTL` for RAS ATHUB error-event interrupt enable/clear handling.
- The same implementation programs endpoint LTR behavior through `RCC_EP_DEV0_0_EP_PCIE_TX_LTR_CNTL` and PCIe config-space `PCI_EXP_DEVCTL2` when `CONFIG_PCIEASPM` is enabled.
- Display resource code such as `display/dc/resource/dcn401/dcn401_resource.c` uses `regBIF_BX0_*` offset names through `NBIO_SR()`-style macros. This chunk provides field masks, while the offset header provides addresses for those display-facing NBIF register tables.
- Similar field names also appear in adjacent NBIO generations, making this generated header part of a versioned hardware-description contract. Drivers select the proper header by IP version rather than probing field layout dynamically.

## State And Persistence Behavior

The macros themselves are stateless. The state they describe is hardware state in PCIe config space, NBIF MMIO registers, scratch registers, and power/interrupt control registers.

Persistent or semi-persistent hardware state described here includes:

- PCIe config-visible state for endpoint function 1 and VF7, such as BAR values, MSI/MSI-X state, AER status/masks, SR-IOV configuration, DPA allocation, ACS/PASID/LTR/ARI controls, and resizable BAR controls. Some fields are OS/programmed policy; others are capability or status fields owned by hardware/firmware.
- Scratch registers for SBIOS, BIOS, driver, and firmware, which are explicitly intended as cross-component communication or diagnostic storage across parts of device initialization and runtime.
- Doorbell and BIF ring state: enable bits, aperture behavior, interrupt status/clear bits, ring base/pointers, writeback address, and overflow status.
- BACO state and timers, which affect device power transitions and low-power exit sequencing.
- HDP remap addresses, which persist until reprogrammed and influence how later KFD/HDP flush requests reach hardware.

Because these are register definitions, persistence depends on reset domain. FLR, BACO, full GPU reset, PCIe link reset, and firmware initialization can each clear or reinterpret parts of this state.

## Dependencies And Integration Points

Direct dependencies:

- `nbif_6_3_1_offset.h` supplies matching `reg*` and `cfg*` addresses/base indices.
- SOC15 register access macros in AMDGPU provide `RREG32_SOC15()`, `WREG32_SOC15()`, `SOC15_REG_OFFSET()`, and field helper macros.
- Linux PCI helpers and constants, such as `pcie_capability_read_word()`, `pcie_capability_set_word()`, `pcie_capability_clear_word()`, and `PCI_EXP_DEVCTL2`, interact with the PCIe capability fields represented here.
- KFD remap constants such as `KFD_MMIO_REMAP_HDP_MEM_FLUSH_CNTL` and `KFD_MMIO_REMAP_HDP_REG_FLUSH_CNTL` are programmed through the HDP remap fields in this chunk.
- RAS handling uses `BIF_BX0_BIF_DOORBELL_INT_CNTL` status/clear/disable fields before calling higher-level RAS interrupt flow.

Integration points:

- AMDGPU NBIF IP block setup, especially `nbif_v6_3_1.c`.
- GPU reset and power management paths that need BACO and FLR-related fields.
- Interrupt and RAS setup paths that use doorbell interrupt controls and AER status/mask/severity fields.
- SR-IOV/vGPU paths that rely on endpoint function, virtual function, ARI, ACS, PASID, and SR-IOV capability definitions.
- Display resource initialization that builds NBIO register tables from matching offset names.

## Risks

- Generated-header drift: a wrong shift or mask silently corrupts unrelated register bits. This is especially risky for packed PCIe fields such as command/status, device control, AER status, SR-IOV control, BACO control, and doorbell interrupt control.
- Name/address mismatch: these masks must match `nbif_6_3_1_offset.h`. Reusing a field macro with the wrong generation or wrong `reg*` address can produce valid C that programs the wrong hardware field.
- Read-modify-write hazards: status/clear registers such as AER and doorbell interrupt controls may have write-one-to-clear or mixed status/control semantics. Generic field updates must preserve reserved bits and avoid accidentally clearing latched status.
- Virtualization sensitivity: EPF1, VF7, SR-IOV, ARI, ACS, PASID, and VF BAR fields are security and isolation relevant. Incorrect masks could expose memory apertures, break VF enumeration, or interfere with function-level reset.
- Power sequencing sensitivity: BACO enable, dummy enable, auto-exit, timer, and power-good fields can hang resume, leave the device inaccessible, or cause spurious reset interrupts if misprogrammed.
- Interrupt routing risk: doorbell/RAS interrupt status, clear, disable, vector-select, and BIF ring bits influence whether faults reach the interrupt handler or remain latched.

## Test Signals

Useful validation signals for this chunk are hardware- and integration-oriented:

- Build coverage for `amdgpu/nbif_v6_3_1.c` and display resource code that includes the NBIF 6.3.1 headers; compile failures catch missing or renamed field macros.
- Boot and probe on NBIF 6.3.1 hardware with successful AMDGPU initialization, no MMIO timeout, and correct NBIF IP version selection.
- Framebuffer access smoke tests: enabling/disabling MC access through `BIF_BX0_BIF_FB_EN` should not break VRAM access, GPU memory tests, or display bring-up.
- KFD/HDP flush tests should confirm remapped HDP flush registers work after `nbif_v6_3_1_remap_hdp_registers()`.
- RAS interrupt tests should exercise `BIF_BX0_BIF_DOORBELL_INT_CNTL` enable/disable, status detection, and clear paths, including the no-BIF-ring ATHUB handling path.
- ASPM/LTR tests under `CONFIG_PCIEASPM` should verify LTR enablement and link power transitions without malformed PCIe errors.
- SR-IOV tests should validate PF/VF enumeration, VF BAR sizing, ARI/ACS/PASID exposure, FLR behavior, and VF memory-space enablement.
- BACO suspend/resume and runtime power-management tests should check entry/exit completion, `BACO_EXIT_*` timing, and `BACO_EXIT_DONE` interrupt behavior.
- PCIe AER injection or error-reporting tests should verify uncorrectable/correctable status, mask, severity, header-log, and TLP-prefix-log fields line up with hardware-visible error reports.

### subset-b-002881: lines 9851-12254

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbif/nbif_6_3_1_sh_mask.h lines 9851-12254

## Scope And Purpose

This chunk is a middle range of the generated NBIF 6.3.1 shift/mask header. It contains no executable C code, functions, structs, or storage. Its job is to publish C preprocessor constants for hardware register bit positions and masks. Consumers combine these constants with register offsets from `nbif_6_3_1_offset.h` and AMDGPU register helpers such as `REG_SET_FIELD`, `REG_GET_FIELD`, `RREG32_SOC15`, `WREG32_SOC15`, and `WREG32_FIELD15_PREREG`.

The range starts in the `nbif_rcc_dev0_BIFDEC1` register block with root-complex/device control fields, continues through the `nbif_rcc_dev0_epf0_BIFDEC2` MSI-X vector table, the large `nbif_rcc_strap_BIFDEC1` strap register block, the `nbif_bif_bx_pf_BIFPFVFDEC1` PF/VF-facing BIF control block, the `nbif_rcc_dev0_epf0_BIFPFVFDEC1` EPF0 runtime fields, GDC and GDC S2A doorbell control blocks, and ends partway through the `nbif_bif_cfg_dev0_epf2_bifcfgdecp` PCI configuration-space field map at `BIF_CFG_DEV0_EPF2_PCIE_UNCORR_ERR_MASK`.

The primary purpose of this chunk is to make NBIF PCIe/root-complex, strap, power-management, doorbell, HDP flush, mailbox, SR-IOV, and PCI config-space fields addressable by name in the AMDGPU driver. The directly relevant in-tree implementation is `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/nbif_v6_3_1.c`, which includes this header and uses several field families from this exact range for ASIC revision discovery, ASPM/LTR strap programming, doorbell routing, doorbell self-ring aperture setup, HDP flush masks, and memory-size reporting.

## Important APIs, Types, And Macro Families

The `RCC_DEV0_0_RCC_*` family describes NBIF root-complex/device behavior for device 0. It includes SR-IOV invalid-register interrupt enablement, BACO request disables, reset enablement, VDM support, PCIe margining parameter discovery, GPUIOV and GPU host-VM enablement, console IOV mode, VF offset/stride, peer register ranges, bus-control policy, configuration aperture sizing, XDMA aperture bounds, feature-control "misc" bits, bus-number and dev/function ID lists, host bus number capture, peer framebuffer offset registers, link-down entry/exit controls, LTR switch latency, and memory-hub arbitration controls.

The root-complex bus and feature fields are broad control surfaces. `RCC_DEV0_0_RCC_BUS_CNTL` covers PMI IO/memory/bus-master disable controls, root error logging, poisoned completion behavior, downstream completion-abort/unsupported-request signaling, and private max-payload/max-read-request sizing. `RCC_DEV0_0_RCC_FEATURES_CONTROL_MISC` covers CRS return, ATC/PASID unsupported-request behavior, ignoring specific translated request classes, MSI/MSI-X pending clearing behavior, BME checks, poison checks, and ECRC device-error reporting.

The `RCC_DEV0_EPF0_GFXMSIX_*` macros describe four EPF0 graphics MSI-X vectors plus the pending-bit array. For each vector the fields cover low/high message address, message data, and vector-mask control. These constants are not heavily used in `nbif_v6_3_1.c`, but they define the local register view for interrupt table programming and diagnostics.

The `RCC_STRAP0_RCC_BIF_STRAP*` family is a large fuse/ROM/software strap surface for BIF/NBIF behavior. It includes generation enables/disables, VGA and ROM strap bits, aperture sizing, GPUIOV, error-ignore policy, AP/SWUS/SUC/SUM access policy, margining readiness, DLF/PHY capabilities, LTR and ASPM strap policy, power-break debounce/timer settings, VLINK timers, register-protection behavior, emergency power reduction, and register-aperture remapping. In `nbif_v6_3_1_program_ltr()` and `nbif_v6_3_1_program_aspm()`, `RCC_STRAP0_RCC_BIF_STRAP2`, `STRAP3`, and `STRAP5` masks/shifts are used to clear and then program LTR/ASPM-related strap fields.

The `RCC_STRAP0_RCC_DEV0_PORT_STRAP*` family describes the port-level PCIe capability straps for device 0. It includes link capabilities, maximum link speed/width, ASPM support, L1 acceptable latency, port type/number, slot and surprise-down capability, DRS, completion-timeout ranges, LTR support, OBFF, TPH, L1 PM substates, DPC, lane margining, lane equalization behavior, DLF, emergency power reduction, and other port feature advertisement knobs. These straps feed the PCIe capability values exposed by the device and must match platform policy and silicon support.

The `RCC_STRAP0_RCC_DEV0_EPF0_STRAP*` and `RCC_STRAP0_RCC_DEV0_EPF1_STRAP*` families describe endpoint-function identity and capability straps. EPF0 fields include device/revision IDs, function enablement, legacy device type, D-state support, soft-reset behavior, resize BAR, PASID width/capabilities, MSI/MSI-X, AER/ACS/ATS/DPA/DSN, subsystem IDs, PME, FLR, atomic operation support, doorbell/ROM/IO/memory/register BAR aperture sizing, VF aperture sizing, VGA disable, SR-IOV VF mapping mode, GPUIOV VSEC revision, and related VF protection. EPF1 has a similar but smaller set for the second function. `nbif_v6_3_1_get_rev_id()` reads `RCC_STRAP0_RCC_DEV0_EPF0_STRAP0` and extracts `STRAP_ATI_REV_ID_DEV0_F0` through this header's mask/shift pair.

The `BIF_BX_PF0_*` family covers PF-facing BIF status and service registers. It includes BME-low DMA status, unsupported atomic error logging and clear bits, doorbell self-ring GPA aperture base high/low/control, HDP coherency flush control registers, GPU HDP flush request/done bitmaps for CP0-CP9 and SDMA0-SDMA1, BIF transaction-pending bits, four transmit and receive mailbox data words, mailbox valid/ack controls, mailbox interrupt enables, and a compact VM/HV mailbox. `nbif_v6_3_1_enable_doorbell_selfring_aperture()` programs the self-ring aperture base/control fields, and the exported `nbif_v6_3_1_hdp_flush_reg` structure uses `BIF_BX_PF0_GPU_HDP_FLUSH_DONE__CP*` and `__SDMA*` masks from this range.

The `RCC_DEV0_EPF0_RCC_*` family covers runtime EPF0 sideband fields. It includes invalid SR-IOV access and doorbell-read error status, the global doorbell aperture enable bit, configured memory size, a reserved config register, and the IOV function identifier plus IOV enable bit. `nbif_v6_3_1_get_memsize()` reads `RCC_DEV0_EPF0_RCC_CONFIG_MEMSIZE`; `nbif_v6_3_1_enable_doorbell_aperture()` writes `RCC_DEV0_EPF0_RCC_DOORBELL_APER_EN__BIF_DOORBELL_APER_EN`.

The `GDC0_*` family describes general GDC controls, including SHUB register request protection, A2S FIFO arbitration, medium-grain clock-gating controls, S2A arbitration/performance behavior, power-gating misc/master/slave controls, and ATDMA arbitration weights. The clock-gating hooks in `nbif_v6_3_1.c` are currently empty, but these fields are the register surface that future NBIF/GDC clock-gating or power-gating code would use.

The `GDC_S2A0_S2A_DOORBELL_ENTRY_0_CTRL` through `GDC_S2A0_S2A_DOORBELL_ENTRY_15_CTRL` macros are a repeated 16-port doorbell routing table. Each entry has an enable bit, AWID field, fence enable, range offset, range size, 64-bit support disable, range-offset deduction, drop enable, and high address nibble. `nbif_v6_3_1_sdma_doorbell_range()` uses entry 2 for SDMA, `nbif_v6_3_1_ih_doorbell_range()` uses entry 1 for IH, `nbif_v6_3_1_vcn_doorbell_range()` uses entries 4/5 for VCN instances, and `nbif_v6_3_1_gc_doorbell_init()` writes fixed values to entries 0 and 3 for graphics command processor routing. The chunk also defines common doorbell fence controls and a GFX doorbell status/all-clear register.

The `BIF_CFG_DEV0_EPF2_*` family is the EPF2 PCI configuration-space field map. It includes standard PCI header registers, command/status bits, revision/class/prog-interface, BARs, ROM BAR, interrupt line/pin, capability-list pointers, vendor-specific capability fields, power-management capability/control fields, PCIe capability/device/link controls and status, MSI/MSI-X capabilities, MSI address/data/mask/pending registers, VSEC headers/scratch registers, AER enhanced-capability headers, uncorrectable error status, and the start of uncorrectable error mask fields. This range stops before the matching severity and correctable-error/AER tail, which begins in the next chunk.

## Control Flow And Runtime Use

There is no runtime control flow in this header. Inclusion and macro expansion happen at compile time. Runtime behavior is in C files that use these names to preserve or update individual hardware register fields.

`nbif_v6_3_1_get_rev_id()` reads the EPF0 strap register, chooses an alternate offset for IP version `7.11.4`, then masks and shifts the `STRAP_ATI_REV_ID_DEV0_F0` field. That path depends on this chunk's EPF0 strap field layout while the actual register address comes either from `nbif_6_3_1_offset.h` or a locally defined NBIF 4.10 compatibility offset.

Doorbell configuration is the most active direct use of this chunk. SDMA instance 0 reads doorbell entry 2, sets enable/AWID/range offset/range size/address-high-nibble fields when doorbells are enabled, or clears the range size when disabled, and writes the register back. IH does the same with entry 1. VCN uses entry 4 or 5 depending on instance and programs AWID/address-high values differently for each instance. Graphics doorbell initialization writes fixed values to entries 0 and 3. The helper paths also switch to locally defined NBIF 4.10 offsets on IP version `7.11.4`, while still using this chunk's field masks.

Doorbell aperture control has two layers. `nbif_v6_3_1_enable_doorbell_aperture()` toggles the EPF0 `BIF_DOORBELL_APER_EN` bit. `nbif_v6_3_1_enable_doorbell_selfring_aperture()` builds a PF0 self-ring aperture control value from enable/mode/size fields and writes low/high base registers from `adev->doorbell.base`. The field masks in this chunk therefore gate both external doorbell BAR exposure and the internal self-ring GPA aperture.

HDP coherency integration uses this chunk in two ways. `nbif_v6_3_1_get_hdp_flush_req_offset()` and `nbif_v6_3_1_get_hdp_flush_done_offset()` return SOC15 offsets for the request/done registers defined alongside these masks. The exported `nbif_v6_3_1_hdp_flush_reg` maps CP and SDMA done masks to the common NBIO HDP flush machinery, so command processor and SDMA clients can wait on the correct hardware acknowledgement bits after cache/coherency flush requests.

ASPM and LTR setup uses several strap masks/shifts from this chunk. Under `CONFIG_PCIEASPM`, `nbif_v6_3_1_program_ltr()` clears `RCC_STRAP0_RCC_BIF_STRAP2__STRAP_LTR_IN_ASPML1_DIS` and then updates Linux PCIe capability state. `nbif_v6_3_1_program_aspm()` clears VLINK ASPM and LDN timer fields, coordinates with PCIE block registers from the separate `pcie_6_1_0_sh_mask.h` header, programs PCI config LTR values through Linux PCI helpers, then writes timed values back through `RCC_STRAP0_RCC_BIF_STRAP3` and `STRAP5` shifts.

PCI configuration-space macros in the EPF2 section are mostly register-interface surface in this driver slice. They mirror the layout of standard PCI/PCIe fields and can be used by lower-level debug, RAS, firmware, virtualization, or capability setup code. Their correctness is still important because the offset/default headers expose the matching register addresses and because the same naming convention is used across AMD generated register headers.

## State And Persistence Behavior

The header itself has no storage, allocation, locking, persistence, or side effects. It only contributes constants to compiled C objects.

The described registers are persistent hardware state until reset, power transition, firmware reinitialization, or explicit driver writes. Important persistent state includes BIF strap policy, device/function identity, PCIe capability advertisement, doorbell aperture enablement, doorbell routing ranges, self-ring doorbell GPA base/control, HDP flush request/done state, mailbox valid/ack/data state, BME and transaction-pending status, SR-IOV/IOV function identifiers, GDC clock/power gating controls, and PCI config capability/status/error registers.

Several fields are status or latch-and-clear by convention. Examples include BME-low status with a clear bit, unsupported atomic error status with separate clear bits, HDP flush done masks, BIF transaction-pending bits, mailbox valid/ack handshakes, invalid SR-IOV access status, doorbell-read access status, GFX doorbell status/all-clear state, PCI status error bits, MSI/MSI-X pending state, and AER uncorrectable error status. The masks do not encode access type, so callers must know whether a field is read-only, write-one-to-clear, sticky across reset domains, strap-derived, or ordinary read/write.

Strap registers deserve special care because they bridge persistent platform/fuse/ROM policy and runtime writes. Some strap bits are read as capabilities or identity; others are modified at runtime by ASPM/LTR setup. Incorrect writes can change advertised PCIe capabilities, power behavior, reset behavior, access protection, or SR-IOV aperture layout until the next hardware reset or reinitialization.

Doorbell routing state is persistent and directly affects command submission paths. If range offset/size or AWID values are stale or wrong, CPU writes to doorbell pages can be dropped, routed to the wrong engine, or accepted for an unintended function. Disabling a doorbell range is represented by setting the range-size field to zero in the current NBIF code, not by clearing every field in the entry.

HDP flush request/done registers are synchronization state between GPU engines and host-visible memory/coherency paths. The common AMDGPU HDP flush code relies on stable engine-specific mask values for CP0-CP9 and SDMA0-SDMA1; a wrong bit mapping would cause waits on the wrong engine's completion bit or premature completion.

## Dependencies And Integration Points

The closest sibling dependency is `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbif/nbif_6_3_1_offset.h`, which supplies register addresses and base indices. This shift/mask file only supplies field layouts. There is no `nbif_6_3_1_default.h` in the immediate direct include path observed for `nbif_v6_3_1.c`; defaults, where needed, are hard-coded, read from hardware, or controlled by firmware/platform straps.

The main C integration point is `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/nbif_v6_3_1.c`. It includes this header and `nbif_6_3_1_offset.h`, then exposes `nbif_v6_3_1_funcs` as the NBIO function table for this generation. The function table plugs into AMDGPU's broader NBIO abstraction for HDP flush offsets, PCIe indirect offsets, revision ID, memory-controller access, memory-size reporting, SDMA/VCN/IH/GC doorbell setup, doorbell aperture controls, clock-gating hooks, interrupt control, register remapping, ROM offset reporting, ASPM programming, and RAS interrupt setup.

The macros integrate with standard AMDGPU register helper conventions. `REG_SET_FIELD(value, REGISTER, FIELD, new_value)` expects `REGISTER__FIELD_MASK` and `REGISTER__FIELD__SHIFT`. `REG_GET_FIELD(value, REGISTER, FIELD)` expects the same pair. Any spelling or mask drift from the generated naming contract becomes either a compile-time error or, worse, a build-clean wrong bit manipulation.

PCIe integration crosses subsystem boundaries. `nbif_v6_3_1_program_aspm()` combines NBIF strap fields from this chunk, PCIE block fields from `pcie_6_1_0_sh_mask.h`, and Linux PCI helpers such as `pcie_capability_read_word`, `pcie_capability_set_word`, `pcie_capability_clear_word`, `pci_find_ext_capability`, and `pci_write_config_dword`. The NBIF strap fields must stay consistent with what Linux sees in PCI capability space.

Display integration is indirect. `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/resource/dcn401/dcn401_resource.c` includes `nbif_6_3_1_offset.h` but not this shift/mask header in the inspected include region. That means display code may need NBIF register offsets for resource setup, while field-level manipulation for this ASIC generation is concentrated in AMDGPU NBIF/NBIO code.

Firmware and virtualization integration is implied by several field families. BACO, GPUIOV, SR-IOV invalid-access status, VF aperture sizing, IOV function identifiers, VM/HV mailbox fields, doorbell protection controls, PASID/ATS/ACS straps, and VSEC/AER fields all describe interfaces that may be coordinated with PSP/firmware, hypervisor flows, PF/VF isolation, or platform policy even when only a subset is actively touched by the visible driver code.

## Risks And Edge Cases

Manual edits are high risk because this is generated register metadata. A single incorrect shift or mask can compile cleanly while programming a neighboring field in hardware.

Doorbell entry fields are dense and repeated. Entries 0-15 share the same layout but different port-numbered macro names. Reusing the wrong register name in `REG_SET_FIELD` can set the wrong bit positions if a future ASIC changes a single entry layout, and using the wrong offset can route doorbells to the wrong hardware port. Existing code also uses entry 4 field names while writing either entry 4 or entry 5 for VCN, relying on identical layouts.

Range values for doorbell entries are packed into limited-width fields. `S2A_DOORBELL_PORT*_RANGE_OFFSET` is masked by `0x0001FF80`, and range size by `0x01FE0000`. Oversized or unvalidated `doorbell_index` or `doorbell_size` values are truncated by `REG_SET_FIELD`, which can create a plausible but incorrect route. Tests should cover high doorbell indices and disabled ranges.

The IP version `7.11.4` special case uses local NBIF 4.10 offset constants while keeping NBIF 6.3.1 field masks. That works only if the relevant register bit layouts are identical across those register address variants. Any future change to layout compatibility needs explicit review rather than assuming the offset alias is enough.

Strap fields mix static identity/capability bits with runtime policy bits. Clearing or setting the wrong strap field can change PCIe capability advertisement, reset behavior, access protection, ASPM/LTR timing, emergency power behavior, or SR-IOV layout. Runtime writes should preserve unrelated strap fields through read-modify-write and should be guarded by hardware generation and platform policy.

ASPM/LTR programming crosses NBIF straps, PCIE link-control registers, and Linux PCI config space. A mismatch can lead to link instability, missing LTR enablement, higher idle power, resume failures, or latency regressions. The driver clears some fields first and then writes timed values; interrupted or partial programming could leave conservative or inconsistent link-policy state.

HDP flush bit mappings are synchronization-critical. If a CP or SDMA done mask is wrong, clients may wait forever, skip a required memory flush, or observe stale memory. Because the register exposes many reserved engine bits as well, accidental use of reserved masks could hide a real completion failure.

SR-IOV and GPUIOV fields are security-sensitive. Invalid register access status, VF aperture sizing, VF mapping mode, IOV function identifier, doorbell aperture enablement, and VM/HV mailbox fields all affect isolation or PF/VF communication. Wrong masks can expose doorbells or BAR apertures to the wrong function, fail to report invalid access, or corrupt mailbox handshakes.

PCI config-space fields must match standard PCI/PCIe semantics. Misdescribing `COMMAND`, `STATUS`, MSI/MSI-X, device/link capability, or AER fields can break enumeration, interrupt delivery, link diagnostics, or error containment. This chunk ends in the middle of the AER uncorrectable mask family, so reconciliation with the following chunk is necessary for a complete EPF2 error-reporting picture.

## Test Signals

Build coverage should compile the AMDGPU NBIF implementation that includes `nbif_6_3_1_sh_mask.h`, especially `amdgpu/nbif_v6_3_1.c`. Macro naming or missing field pairs generally show up as compile errors in `REG_SET_FIELD`, `REG_GET_FIELD`, or direct mask references.

Generated-header validation should compare this file against the authoritative ASIC register source and `nbif_6_3_1_offset.h`. Useful local checks include verifying every field has both `__SHIFT` and `_MASK`, masks align with shifts and expected widths, and repeated families such as `GDC_S2A0_S2A_DOORBELL_ENTRY_0_CTRL` through `_15_CTRL` remain layout-identical.

Doorbell runtime tests should exercise GC, IH, SDMA, and VCN doorbells on supported hardware. Confirm that enabled ranges accept doorbell writes, disabled ranges stop routing, high range offsets do not truncate unexpectedly, and the IP version `7.11.4` alternate offsets produce the same behavior as the normal offsets on their target hardware.

HDP flush tests should issue CP and SDMA work that requires host-data-path coherency, request flushes, and verify the matching done bits for CP0-CP9 and SDMA0-SDMA1 are observed through the common NBIO flush path. Timeouts or stale memory after a flush are strong signals of wrong offset or mask mapping.

ASPM/LTR tests should boot with `CONFIG_PCIEASPM`, inspect PCIe capability state before and after `program_aspm`, exercise suspend/resume and idle transitions, and confirm that `RCC_STRAP0_RCC_BIF_STRAP2`, `STRAP3`, and `STRAP5` fields match expected policy without disturbing unrelated strap bits. Link retraining errors, LTR disablement, or elevated idle power are useful failure signals.

Revision and identity tests should verify that `nbif_v6_3_1_get_rev_id()` returns the expected value from EPF0 strap fields on both standard NBIF 6.3.1 offsets and the `7.11.4` alternate-offset path. PCI enumeration should expose the expected vendor/device/class/subsystem/capability values for EPF2 if that function is present and enabled.

SR-IOV and isolation tests should cover PF and VF configurations. They should validate invalid-access status reporting, VF aperture sizing, VF mapping mode, doorbell aperture access, IOV function identifiers, and VM/HV mailbox handshakes. The expected signal is that VFs can access only their intended BAR/doorbell resources and that invalid access does not silently pass.

PCIe error-reporting tests should inject or observe AER conditions where possible and confirm `BIF_CFG_DEV0_EPF2_PCIE_UNCORR_ERR_STATUS` and mask fields decode DLP, surprise down, poison, flow-control, completion timeout/abort, unexpected completion, overflow, malformed TLP, ECRC, unsupported request, ACS violation, internal, blocked TLP, and related error bits consistently with the PCIe specification and the next chunk's continuation fields.

### subset-b-002882: lines 12255-14840

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbif/nbif_6_3_1_sh_mask.h lines 12255-14840

## Purpose

This chunk is generated AMDGPU NBIF 6.3.1 register bitfield metadata. It contains no executable C code, structs, enums, or callable APIs. Its exported interface is a dense set of C preprocessor `__SHIFT` and `_MASK` constants used by AMDGPU register helpers to pack and decode 32-bit PCIe/NBIO configuration and MMIO register values.

The range starts in the middle of `BIF_CFG_DEV0_EPF2_PCIE_UNCORR_ERR_MASK`, so the first complete content is the rest of EPF2 Advanced Error Reporting policy and capability fields. It then defines the tail of EPF2 PCIe extended capabilities, a full `BIF_CFG_DEV0_EPF3_*` PCI configuration-space function view, several RCC endpoint/downstream/PFC NBIF control blocks, and the beginning of the `nbif_pciemsix_0_usb_MSIXTDEC` MSI-X table through `PCIEMSIX_VECT54_ADDR_LO`.

Although the repository path is under `distributed-fs/ceph-client`, this is Linux AMD GPU driver hardware metadata, not Ceph filesystem logic. The constants are paired with `nbif_6_3_1_offset.h` register addresses and consumed by AMDGPU NBIO/NBIF code through helpers such as `REG_SET_FIELD`, `REG_GET_FIELD`, `RREG32_SOC15`, `WREG32_SOC15`, and PCI config-space accessors.

## Important APIs, Types, And Macro Families

There are no functions or runtime types in this chunk. The important API is the generated naming contract:

- `<REGISTER>__<FIELD>__SHIFT` gives the bit offset for a register field.
- `<REGISTER>__<FIELD>_MASK` gives the register mask for that field.

The `BIF_CFG_DEV0_EPF2_PCIE_*` tail covers PCIe AER and optional endpoint capabilities for endpoint function 2. It includes uncorrectable error mask and severity bits for malformed TLP, ECRC, unsupported request, ACS violation, internal error, MC-blocked TLP, AtomicOp egress blocking, TLP-prefix blocking, and poisoned-TLP egress blocking. It also defines correctable error status/mask bits, AER capability/control fields, four TLP header-log dwords, four TLP-prefix-log dwords, enhanced BAR capability/control registers for BAR1 through BAR6, power-budget capability data selection/value fields, Dynamic Power Allocation capability/status/control/substate power allocation fields, ACS capability/control bits, PASID capability/control bits, and ARI capability/control bits.

The `BIF_CFG_DEV0_EPF3_*` block is a full PCI configuration-space map for endpoint function 3. It starts with standard PCI identity/header fields: vendor/device IDs, command/status, revision/interface/subclass/base class, cache line, latency, header type, BIST, six BARs, CIS pointer, adapter ID, ROM BAR, capability pointer, interrupt line/pin, and min/max latency. It then exposes legacy and PCIe capability structures: vendor capability, power-management capability and status/control, USB-related SBRN/FLADJ/DBESL fields, PCIe capability/device/link registers, MSI and MSI-X capability fields, vendor-specific enhanced capability fields, AER status/mask/severity/header-log/prefix-log fields, enhanced BAR controls, power-budgeting fields, DPA fields, ACS fields, PASID fields, and ARI fields.

The `RCC_DEV0_1_*` block describes root-complex/common control fields for device 0 instance 1: VDM support, bus control, feature-control miscellaneous flags, device and common link controls, endpoint requester-ID restore, LTR light-switch control, multi-host arbitration control, and margining parameter controls. These fields are NBIF-specific rather than generic PCI config-space header fields.

The `RCC_EP_DEV0_1_*` block describes endpoint-side PCIe controls and status: scratch, endpoint control, interrupt control/status, RX control, bus/config control, TX LTR control, strap registers, function-0 DPA capability/control/substate allocation mirrors, PME control, reserved register, TX control, requester-ID, error control, RX control, and link speed control.

The `RCC_DWN_DEV0_1_*` and `RCC_DWNP_DEV0_1_*` blocks describe downstream-port controls: reserved/scratch/control/config/RX/bus/strap registers, downstream error/RX/link controls, PCIeP strap misc, and LTR message information received from the endpoint. These are used to tune or observe the internal PCIe path between NBIF root-complex/downstream pieces and endpoint-facing logic.

The `RCC_PFC_AMDGFX_*` and `RCC_PFC_AMDGFXAZ_*` blocks provide per-function controller state for graphics and audio/azalia-related functions. They include LTR control, PME restore fields, sticky restore registers 0 through 5, and auxiliary power control fields.

The `PCIEMSIX_VECT*` block begins the USB MSI-X table metadata. For each vector, the same four register families appear: `ADDR_LO` with message address low bits shifted by two and masked by `0xFFFFFFFC`, `ADDR_HI` with full 32-bit high address, `MSG_DATA` with full 32-bit data, and `CONTROL` with the per-vector mask bit. This chunk covers vector 0 through vector 53 completely and stops at the shift macro for `PCIEMSIX_VECT54_ADDR_LO`, so the next chunk owns the remaining mask and later vectors.

## Control Flow And Runtime Use

This header has no runtime control flow. Its behavior is pure preprocessing: included C files name a register and field, and macro expansion supplies constants used for bit masking and shifting.

The direct NBIF 6.3.1 implementation is `drivers/gpu/drm/amd/amdgpu/nbif_v6_3_1.c`, which includes this shift/mask header and the matching offset header. That file primarily uses other NBIF register families from the same generated header set for revision ID, memory-controller access enablement, doorbell range programming, interrupt handling, HDP flush masks, register remapping, LTR/ASPM programming, and RAS ATHUB interrupt setup. The PCIe config-space and MSI-X table macros in this chunk are part of the same generated register contract even if many are not touched by the narrow visible init path.

Typical consumer flow is:

1. Driver code selects a register offset from `nbif_6_3_1_offset.h` or a PCI configuration-space accessor.
2. It reads an existing 32-bit value when preserving unrelated fields is required.
3. It calls `REG_SET_FIELD` or manually uses the `__SHIFT`/`_MASK` pair to update one field.
4. It writes the result with SOC15 MMIO helpers, PCI config helpers, or another NBIO/NBIF access path.
5. For status paths, it reads a register and uses `REG_GET_FIELD` or equivalent masking to decode hardware-owned state.

The header does not encode sequencing rules. It does not say when AER status is write-one-to-clear, when MSI-X table entries are safe to rewrite, when DPA/ASPM/LTR fields are firmware-owned, or when SR-IOV/virtualization-sensitive fields should be restricted to PF-only paths. Those rules live in the PCIe spec, AMD hardware specs, firmware protocols, and driver call sites.

## State And Persistence Behavior

The header itself has no storage, persistence, allocations, I/O, locks, or side effects. It only contributes constants to compiled code.

The hardware state described by the macros is persistent device register state until reset, power transition, firmware reprogramming, PCI core action, or explicit driver writes. Configuration-like state includes PCI command bits, BAR sizing/control, MSI/MSI-X capability programming, AER masks and severity policy, DPA substate power allocation, ACS/PASID/ARI controls, RCC link and bus controls, LTR/PME restore values, and PFC sticky restore values.

Status-like state includes PCI status bits, PCIe device/link status, correctable and uncorrectable AER status, AER header/prefix logs, DPA status, RCC endpoint interrupt status, downstream link/status fields, LTR message information, and MSI-X per-vector mask state. Some fields in these status registers may be sticky or write-one-to-clear, while others are live read-only views.

MSI-X vector table entries are especially stateful. The message address and data fields determine where interrupts are delivered, and the control mask bit gates delivery for that vector. Incorrect updates can reroute interrupts, lose interrupts, or expose interrupt writes to the wrong address in virtualized configurations.

Because this generated file only names bit ranges, it cannot distinguish read-only, write-trigger, write-one-to-clear, reserved, firmware-owned, or PCI-core-owned fields. Callers must preserve reserved bits and use the right access mechanism for the register's address space.

## Dependencies And Integration Points

The core dependency is the matching offset header, `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbif/nbif_6_3_1_offset.h`. Offsets such as `cfgBIF_CFG_DEV0_EPF*_...`, RCC block offsets, and MSI-X table offsets identify where the fields live; this header only describes bit positions.

The primary in-tree C integration point is `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/nbif_v6_3_1.c`, registered through `nbif_v6_3_1_funcs` and `nbif_v6_3_1_ras`. Discovery code selects those function tables for compatible NBIO/NBIF IP versions, and other AMDGPU components call them for HDP flush offsets, PCIe index/data offsets, memory size, doorbell apertures, interrupt control, ROM offset, ASPM, and RAS interrupt setup.

This header also integrates with the broader Linux PCIe stack. Generic PCI code may own parts of standard PCI, PCIe, MSI, MSI-X, AER, ACS, PASID, ARI, LTR, and power-management capability behavior, while AMDGPU/NBIF code may use device-specific RCC and PFC registers around that PCIe state. Driver code must avoid racing the PCI core or firmware when programming these fields.

The `EPF2` and `EPF3` namespaces indicate per-function endpoint config-space views. The same field names are repeated across functions, but their offsets and ownership differ. SR-IOV, multi-function, graphics/audio/USB-function exposure, and PF/VF separation all depend on pairing the correct function's offset namespace with the correct field namespace.

Adjacent chunks are needed for a complete per-file report. This chunk starts after the earlier `EPF2_PCIE_UNCORR_ERR_MASK` shift and first mask fields, and ends before completing `PCIEMSIX_VECT54_ADDR_LO`. The merge lane should not treat either boundary register family as complete from this chunk alone.

## Risks And Edge Cases

Generated-register drift is the main risk. A wrong shift or mask can compile cleanly but program a different PCIe/NBIF bit than intended, affecting link behavior, interrupt routing, AER policy, endpoint function identity, BAR exposure, or virtualization isolation.

AER fields are policy-sensitive. Masking unsupported requests, ECRC, malformed TLP, ACS violations, poisoned TLP egress blocking, or internal errors can hide real faults; severity bits control fatal/nonfatal reporting behavior. Header-log and prefix-log fields are diagnostic evidence and can be lost if status clearing is mishandled.

Capability-list fields have pointer and version subfields. Wrong `NEXT_PTR`, `CAP_ID`, or capability version interpretation can break PCI capability traversal or confuse software that expects standard PCIe enhanced capability layout.

BAR enhancement and SR-IOV-adjacent fields are address-exposure sensitive. Incorrect BAR size/index/control values can map too much or too little MMIO space, conflict with PCI resource assignment, or expose resources to the wrong function.

DPA, LTR, ASPM, PME, and auxiliary-power controls interact with platform power management and firmware sequencing. Misprogramming can cause power-state entry/exit failures, link instability, lost PME signaling, or performance/latency regressions.

ACS, PASID, ARI, requester-ID restore, active requester-ID, and endpoint/downstream config controls are security- and routing-sensitive in virtualized or IOMMU-backed systems. Incorrect field packing can break isolation, route DMA or completions incorrectly, or make VFs appear with the wrong capabilities.

MSI-X table entries are repetitive and easy to index incorrectly. A loop or table stride bug can write vector N's message address/data/control into a neighboring vector, and the chunk boundary at vector 54 increases the chance of incomplete generated-table reasoning if adjacent chunks are not merged.

## Test Signals

Build coverage should compile AMDGPU paths that include `nbif_6_3_1_offset.h` and `nbif_6_3_1_sh_mask.h`, especially `amdgpu/nbif_v6_3_1.c`, `gfx_v12_0.c`, `gmc_v12_0.c`, RAS registration paths, and display code that includes the NBIF offset header. Missing or renamed field macros generally surface as compile failures in `REG_SET_FIELD`, `REG_GET_FIELD`, or SOC15 register references.

Static validation should compare this generated header against the source register database and the matching offset header. Useful checks include every field having both a `__SHIFT` and `_MASK`, masks aligning with shifts, repeated EPF2/EPF3 capability layouts staying consistent where hardware intends them to be consistent, and MSI-X vector entries using the expected four-register stride.

Runtime PCIe tests should verify enumeration and capability traversal for functions represented by EPF2 and EPF3, including PCI IDs, BAR assignment, PCIe device/link capabilities, MSI/MSI-X capability exposure, AER capability exposure, ACS/PASID/ARI capability reporting, and power-management capability behavior.

Interrupt tests should exercise MSI-X vector programming for the USB/NBIF MSI-X table region: set address/data, mask and unmask vectors, trigger interrupts, and confirm delivery to the expected CPU vector without disturbing neighboring entries.

RAS and AER tests should inject or observe correctable and uncorrectable PCIe errors where supported, validate status decode, verify mask/severity policy, confirm header/prefix logging, and ensure clearing status does not clear unrelated evidence.

Power-management tests should cover ASPM/LTR/DPA/PME transitions, suspend/resume, reset, and runtime power changes on supported hardware. Regression signals include link retraining loops, failed wake, unexpected latency, missing PME, or device disappearance after low-power entry.

Virtualization and multi-function tests should cover PF/VF or multi-function configurations where EPF2/EPF3, ACS, PASID, ARI, requester-ID, BAR, and MSI-X state matter. Key regressions are DMA isolation failures, wrong function capability exposure, lost interrupts in VF/PF paths, or BAR/resource assignment mismatches.

### subset-b-002883: lines 14841-17760

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbif/nbif_6_3_1_sh_mask.h - subset-b-002883

## Scope

- Chunk id: `subset-b-002883`
- Source lines: 14841-17760
- Source file: `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbif/nbif_6_3_1_sh_mask.h`
- Observed content: 2,920 source lines from a generated AMD NBIF 6.3.1 shift/mask header; 2,014 `#define` constants, including 1,014 `__SHIFT` entries and 1,203 `_MASK` entries.

This chunk contains register field metadata, not executable logic. It exports preprocessor constants named `REGISTER__FIELD__SHIFT` and `REGISTER__FIELD_MASK` for NBIF PCIe/MSI-X, root-complex power-function, shadow, indirect-index, and strap registers. Register addresses and base-index selectors are supplied by the companion `nbif_6_3_1_offset.h` header.

## Purpose

The largest part of the chunk completes the MSI-X vector table definitions for `PCIEMSIX_VECT54` through `PCIEMSIX_VECT255`. Each vector has the standard table fields:

- `ADDR_LO`, where `MSG_ADDR_LO` starts at bit 2 and masks off the low 2 naturally aligned address bits.
- `ADDR_HI`, with a full 32-bit high message address.
- `MSG_DATA`, with a full 32-bit MSI-X payload.
- `CONTROL`, with bit 0 as the per-vector mask bit.

The later regions define smaller NBIF blocks:

- `nbif_rcc_pfc_usb_RCCPFCDEC` and `nbif_rcc_pfc_pd_controller_RCCPFCDEC` power-function controls for USB and PD-controller endpoints, covering LTR snoop/non-snoop latency fields, PME restore bits, sticky error/TLP restore registers, and auxiliary power override fields.
- `nbif_pciemsix_0_usb_MSIXPDEC` MSI-X pending-bit-array registers `PCIEMSIX_PBA_0` through `PCIEMSIX_PBA_7`, each exposing 32 pending bits.
- `nbif_rcc_shadow_reg_shadowdec` shadowed upstream command, BAR, bridge-control, and SUC indirect index/data fields.
- `nbif_bif_swus_SUMDEC` SUM indirect index/data fields, including an 8-bit high index register.
- `nbif_rcc_strap_rcc_strap_internal` strap fields for downstream/root-port behavior on device 0 and the beginning of BIF global strap fields.

The strap macros describe PCIe identity, advertised capabilities, link behavior, power-management support, atomic/ACS/ARI/AER/LTR/OBFF features, MSI/MSI-X capability exposure, power-budget entries, Gen2/Gen3/Gen4/Gen5 capability and equalization settings, 10-bit tag support, requester/completer behavior, routing timers, alternate protocol details, and DOE/CTO/error subclass support.

## Important APIs, Types, and Macros

There are no functions, structs, enums, or mutable objects in this chunk. The public interface is the generated macro namespace.

Important macro families include:

- MSI-X vector table fields: `PCIEMSIX_VECT54_*` through `PCIEMSIX_VECT255_*`. The visible pattern is repeated for every vector: `ADDR_LO__MSG_ADDR_LO`, `ADDR_HI__MSG_ADDR_HI`, `MSG_DATA__MSG_DATA`, and `CONTROL__MASK_BIT`.
- MSI-X pending bit arrays: `PCIEMSIX_PBA_0__MSIX_PENDING_BITS` through `PCIEMSIX_PBA_7__MSIX_PENDING_BITS`.
- PFC LTR and restore fields: `RCC_PFC_USB_RCC_PFC_LTR_CNTL`, `RCC_PFC_USB_RCC_PFC_PME_RESTORE`, `RCC_PFC_USB_RCC_PFC_STICKY_RESTORE_0..5`, `RCC_PFC_USB_RCC_PFC_AUXPWR_CNTL`, and the equivalent `RCC_PFC_PD_CONTROLLER_*` registers.
- Shadow register fields: `SHADOW_COMMAND__IOEN_UP`, `SHADOW_COMMAND__MEMEN_UP`, `SHADOW_BASE_ADDR_1__BAR1_UP`, `SHADOW_BASE_ADDR_2__BAR2_UP`, and `SHADOW_IRQ_BRIDGE_CNTL` upstream ISA/VGA/reset controls.
- Indirect window fields: `SUC_INDEX`, `SUC_DATA`, `SUM_INDEX`, `SUM_DATA`, and `SUM_INDEX_HI`.
- Device-0 port strap fields: `RCC_STRAP1_RCC_DEV0_PORT_STRAP0` through `RCC_STRAP1_RCC_DEV0_PORT_STRAP14`, covering identity, PCIe capabilities, link/power/error behavior, ACS, atomics, virtual channels, 10-bit tags, equalization presets, modified TS data, routing timers, alternate protocol metadata, and DOE/CTO/error subclass capability flags.
- Placeholder comments for `RCC_DEV1_PORT_STRAP0..14` and `RCC_DEV2_PORT_STRAP0..14`; this range has no shift/mask constants for those placeholders.
- BIF strap start: `RCC_STRAP1_RCC_BIF_STRAP0__STRAP_*__SHIFT` begins at the end of the chunk. The matching masks continue after this chunk.

## Control Flow

The header has no local runtime control flow. Runtime behavior is implied by code that includes this generated register database and uses AMD register helper macros.

For MSI-X, the hardware flow is the PCIe-defined table/PBA model: software or hardware writes each vector message address, message data, and mask state; pending interrupt state is reflected through PBA bits; an unmasked pending vector can generate the programmed MSI-X memory write. This chunk covers the table tail, so any code walking all 256 vectors depends on the regular four-register stride remaining correct.

For PFC/PME restore, the flow is power-management oriented. LTR fields advertise snoop and non-snoop latency tolerance; PME restore fields retain/restore PME enable, PME status, and sent-flag state; sticky restore registers preserve error status and captured TLP header/prefix information across a relevant low-power or reset transition; auxiliary-power fields override current and power-detected inputs.

For shadow/SUC/SUM blocks, the implied flow is indirect access: write an index register, then read or write the corresponding data register. Shadow command/BAR/bridge-control fields mirror or stage upstream-visible PCI configuration state.

For straps, the flow is mostly reset-time or early-initialization configuration. Strap bits describe the hardware defaults and advertised PCIe capability surface that later enumeration, link training, and driver policy observe. Driver code should treat these definitions as hardware layout constants rather than ordinary configurable software policy.

## State and Persistence Behavior

The macros are compile-time constants and keep no state. They describe hardware register fields whose values persist according to their register domain:

- MSI-X table values are persistent programmed interrupt routing state until rewritten, reset, or masked by device/function reset semantics. `ADDR_LO`, `ADDR_HI`, and `MSG_DATA` determine interrupt target and payload; `CONTROL__MASK_BIT` suppresses delivery per vector.
- MSI-X PBA fields are transient/latched pending bits. Pending state can be set by hardware while a vector is masked or while delivery is otherwise blocked, and is cleared according to MSI-X hardware protocol rather than by generic register retention assumptions.
- PFC LTR and auxiliary-power fields are retained control/advertisement state. PME restore and sticky restore fields preserve wake/error context such as PME state, PCIe error status, TLP headers, and TLP prefix values.
- Shadow command, BAR, and bridge-control fields hold upstream-visible or staged configuration state. SUC/SUM index registers hold the currently selected indirect address, and data registers expose the selected target.
- Strap registers represent sampled hardware configuration. Some may be read-only from the driver's point of view or only meaningful during reset/bring-up; changing them after enumeration can desynchronize PCIe capability advertisement from OS state.

Several fields have write-one, clear, restore, or latched semantics in hardware even though this header only provides masks. Consumers must follow the hardware programming model and avoid treating every field as a normal read-modify-write bit.

## Dependencies

This chunk depends on:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbif/nbif_6_3_1_offset.h`, which provides matching register offsets and base indices. Examples in this range include `regPCIEMSIX_VECT54_ADDR_LO` at `0x1e0d8`, `regPCIEMSIX_VECT255_CONTROL` at `0x1e3ff`, PFC USB registers around `0xd140`, PFC PD-controller registers around `0xd1c0`, shadow registers around `0xc001`, SUM registers around `0xec38`, port straps around `0xc400`, and BIF straps beginning at `0xc600`.
- AMDGPU SOC15/NBIO register access helpers such as `RREG32_SOC15`, `WREG32_SOC15`, `REG_GET_FIELD`, `REG_SET_FIELD`, and field-table macros that expect generated `REGISTER__FIELD__SHIFT` and `REGISTER__FIELD_MASK` names.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/nbif_v6_3_1.c`, which includes both `nbif_6_3_1_offset.h` and `nbif_6_3_1_sh_mask.h` for NBIF 6.3.1 programming.
- AMD PCIe/NBIO infrastructure, MSI/MSI-X semantics, power-management/PME restore behavior, and PCIe capability advertisement controlled by strap values.

The file path is inside a Ceph client source corpus, but this source is Linux AMDGPU hardware register metadata and is not Ceph filesystem logic.

## Integration Points

The direct integration point is the NBIF 6.3.1 AMDGPU driver layer. `amdgpu/nbif_v6_3_1.c` includes this header and uses the same generated mask/shift naming convention for NBIF fields; exact fields in this chunk are not directly referenced by current C source searches, but they remain part of the exported generated register ABI for the ASIC.

MSI-X integration is with PCI interrupt setup, masking, and diagnostic paths. The vector table definitions must stay aligned with the PCIe MSI-X table and PBA offsets so any table walker, firmware path, debug path, or future endpoint-specific driver logic programs the correct vector.

PFC integration is with PCIe power management for USB and PD-controller functions. LTR, PME restore, sticky error restore, and auxiliary power override fields influence suspend/resume, wake, and error recovery behavior for those NBIF-exposed functions.

Shadow/SUC/SUM integration is with indirect register access and upstream-visible PCI configuration state. These registers can be used by firmware, bring-up tools, or low-level driver code to stage or inspect state that is not represented by a simple direct MMIO register.

Strap integration is with PCI enumeration, capability discovery, link training, error handling, power management, and virtualization/security features. Fields such as ACS, ARI, AER, atomics, LTR, OBFF, VC, 10-bit tags, MSI mapping, target link speed, link width, equalization presets, and device/vendor IDs define what Linux and the PCIe fabric believe the device/root port supports.

## Risks and Edge Cases

- The chunk begins at line 14841 with `PCIEMSIX_VECT54_ADDR_LO__MSG_ADDR_LO_MASK`; the corresponding shift for that field is in the previous chunk. The merge lane must combine adjacent chunks for complete `VECT54_ADDR_LO` coverage.
- The chunk ends in the middle of `RCC_STRAP1_RCC_BIF_STRAP0`; only shifts through `STRAP_RX_IGNORE_TC_ERR_DN__SHIFT` are visible here, with masks and later fields in the next chunk.
- MSI-X vector definitions are highly repetitive. A single off-by-one vector number, stride mismatch, or low-address mask error can route interrupts to the wrong address/data pair or leave the wrong vector masked.
- `MSG_ADDR_LO` masks bits 31:2. Callers must preserve PCIe/MSI address alignment semantics and not try to encode data in the low two address bits.
- PBA registers expose pending state, not durable configuration. Treating pending bits as ordinary writable state can lose interrupt evidence or fight hardware delivery semantics.
- PME and sticky restore registers mix enable/status/sent flags with captured PCIe error data. Misinterpreting restore fields can break wake recovery or obscure the original TLP that triggered an error.
- LTR value/scale fields are split into snoop and non-snoop halves. Wrong values can cause platform power-management latency assumptions to be too aggressive or too conservative.
- Shadow and indirect index/data windows are stateful. Concurrent access without serialization can read or write the wrong indexed target if another path changes the index between operations.
- Strap fields may be sampled or hardware-owned. Runtime writes, if allowed at all, can produce inconsistent PCIe capability exposure after the OS has already enumerated the device.
- Capability straps for ACS, atomics, ARI, AER, PASID-adjacent routing behavior, 10-bit tags, and MSI/MSI-X affect isolation, error handling, and interrupt routing. Incorrect masks can become security or reliability bugs rather than simple feature toggles.
- Placeholder comments for device 1 and device 2 port straps have no macros in this range. Consumers must not assume every commented register has generated fields.

## Test Signals

Useful validation signals for this chunk include:

- Build coverage for AMDGPU NBIF 6.3.1 code that includes `nbif_6_3_1_offset.h` and `nbif_6_3_1_sh_mask.h`.
- Generated consistency checks that every complete `PCIEMSIX_VECT55` through `PCIEMSIX_VECT255` instance has the same four field groups and the expected masks: low message address `0xFFFFFFFC`, high address `0xFFFFFFFF`, message data `0xFFFFFFFF`, and mask bit `0x00000001`.
- Boundary checks that `PCIEMSIX_VECT54_ADDR_LO` is completed by the previous chunk and `RCC_STRAP1_RCC_BIF_STRAP0` is completed by the next chunk.
- Offset/mask alignment checks against `nbif_6_3_1_offset.h`, especially the MSI-X vector table stride from `regPCIEMSIX_VECT54_ADDR_LO` through `regPCIEMSIX_VECT255_CONTROL`, PBA registers, PFC USB/PD-controller register blocks, shadow/SUM windows, and strap registers.
- Hardware or emulation smoke tests for MSI-X vector programming and masking, including delivery to the programmed message address/data and correct PBA pending behavior for masked vectors.
- Suspend/resume and wake tests that exercise PME restore, LTR programming, auxiliary power override behavior, and sticky error restore capture for USB and PD-controller NBIF functions.
- PCIe enumeration/link tests that verify advertised IDs, link width/speed, AER/ACS/ARI/atomics/LTR/OBFF/VC/10-bit-tag/MSI capability behavior, and equalization settings match expected board or ASIC strap values.
- Error-injection tests that confirm restored sticky fields report PCIe poisoned, completion-timeout, completion-abort, unexpected-completion, malformed-TLP, ECRC, unsupported-request, advisory-nonfatal, header, and prefix information accurately.

## Chunk Boundary Notes

This report covers only lines 14841-17760. The first visible line is a mask without its paired shift, and the final visible region starts `RCC_STRAP1_RCC_BIF_STRAP0` but does not include its masks. The final per-file research document should reconcile these boundaries with adjacent chunks before presenting complete register families.

### subset-b-002884: lines 17761-20123

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbif/nbif_6_3_1_sh_mask.h lines 17761-20123

## Scope And Purpose

This chunk is generated AMDGPU NBIF 6.3.1 register bitfield metadata. It contains C preprocessor `*_SHIFT` and `*_MASK` constants only; there are no functions, structs, enums, variables, locks, allocations, or executable control flow in the chunk.

The covered range starts in the middle of `RCC_STRAP1_RCC_BIF_STRAP0`, then defines the rest of the `RCC_STRAP1` and `RCC_DEV0_EPF*` strap fields for the BIF and endpoint functions. It then covers the `nbif_bif_rst_bif_rst_regblk` reset, FLR, D-state, and reset interrupt registers, followed by the `nbif_bif_misc_bif_misc_regblk` ROM, interrupt line, BIFC, PASID, power-gating, SMN, self-ring, INTx, pending, GMI arbitration, power-brake, atomic error, DMA error, and PASID error-log fields.

The purpose is to publish the bit layout for NBIF 6.3.1 registers so driver code can use AMDGPU field helpers such as `REG_SET_FIELD`, `REG_GET_FIELD`, and `WREG32_FIELD15_PREREG` with matching register offsets from `nbif_6_3_1_offset.h`. The in-tree C consumer is `drivers/gpu/drm/amd/amdgpu/nbif_v6_3_1.c`, which includes this header together with the matching offset header. This specific chunk is mostly register surface rather than heavily used C API; the visible direct use from this range is `REGS_ROM_OFFSET_CTRL__ROM_OFFSET` in `nbif_v6_3_1_get_rom_offset()`.

## Important APIs, Types, And Macro Families

There are no runtime APIs or C types declared here. The exported interface is the generated macro namespace:

- `<REGISTER>__<FIELD>__SHIFT` gives the field bit position.
- `<REGISTER>__<FIELD>_MASK` gives the unshifted field mask.
- These macros are paired with `reg<REGISTER>` offsets and `_BASE_IDX` values in `nbif_6_3_1_offset.h`.

The first major family is NBIF strap metadata. `RCC_STRAP1_RCC_BIF_STRAP0..6` describe hardware/fuse/ROM strap-derived capabilities and policy: PCIe generation disable/kill bits for Gen3/Gen4/Gen5, VGA and BIOS ROM behavior, memory aperture sizing, PX capability, GPUIOV enablement, error-ignore policy, AP/SWUS apertures, DLF/margining/PHY speed enablement, S5 register access, LTR behavior, SMN error response/data forcing, emergency power reduction, power-brake timers, register aperture remapping, DOE version selection, production mode, and register protection behavior.

The endpoint-function strap families define PCI configuration and virtualization-visible capabilities for device 0 functions:

- `RCC_STRAP1_RCC_DEV0_EPF0_STRAP*` is the fullest PF0 set. It includes device and revision ID, function enable, D1/D2 support, SR-IOV enable, 64-bit BAR and resize BAR capability, PASID width and PASID feature bits, ARI/AER/ACS/ATS/page-request capabilities, MSI/MSI-X and interrupt pin capability, PME support, FLR enable, atomic operation support, subsystem IDs, doorbell/ROM/IO/memory/register aperture sizing, VF aperture sizing, VGA disable, total VFs, GPUIOV VSEC revision, RTR timing fields, and VF reset timing fields.
- `RCC_STRAP1_RCC_DEV0_EPF1_STRAP*` mirrors the common function capability fields for function 1, including device ID, function enable, D-state support, resize BAR, PASID, AER/ACS/ATS, MSI/MSI-X, FLR, PME, subsystem vendor, and 64-bit aperture enablement.
- `RCC_DEV0_EPF2_STRAP*` and `RCC_DEV0_EPF3_STRAP*` repeat the device/revision/function, PASID, AER/ACS, MSI, FLR/PME, USB DBE select, class code, vendor ID, and auxiliary-current fields for functions 2 and 3.
- `RCC_DEV0_EPF4_STRAP*`, `RCC_DEV0_EPF5_STRAP*`, and `RCC_DEV0_EPF6_STRAP*` are reduced forms covering function enable, D-state support, PASID width/features, AER/ACS, completion-abort/DPA behavior, power/clock/reporting bits, PME/AUX power, and auxiliary-current fields.

The reset block starts at `HARD_RST_CTRL` and contains reset source/control field layouts for hard reset, RSMU soft reset, self soft reset, VPU driver reset, link-reset policy, FLR reset policy, D3hot-to-D0 reset policy, reset interrupts, and D-state values:

- `HARD_RST_CTRL`, `RSMU_SOFT_RST_CTRL`, and `SELF_SOFT_RST` expose DSPT, endpoint, SDP port, SION AON, strap reload, SWUS shadow, sticky/core reset, and self-reset bits.
- `BIF_GFX_DRV_VPU_RST` defines driver-mode PF/VF config/private reset enable bits.
- `BIF_RST_MISC_CTRL`, `BIF_RST_MISC_CTRL2`, and `BIF_RST_MISC_CTRL3` define driver reset mode, auto-clear behavior, link-reset IOV/grace/timer settings, reset protection and idle status, PME turnoff timing, strap reload delays, and RSMU soft reset cycle timing.
- `DEV0_PF0_FLR_RST_CTRL` through `DEV0_PF6_FLR_RST_CTRL` define per-PF FLR reset coverage. PF0 has the broadest set, including PF/VF config/private reset enables, soft PF reset fields, VF-on-VF reset fields, FLR-twice, grace timeout, DMA/HST dummy response status, and PF-copy private reset enable. PF1-PF6 use smaller but aligned field families.
- `BIF_INST_RESET_INTR_STS`, `BIF_PF_FLR_INTR_STS`, `BIF_D3HOTD0_INTR_STS`, `BIF_POWER_INTR_STS`, and `BIF_PF_DSTATE_INTR_STS` publish status bits for instance reset, per-PF FLR, per-PF D3hot-to-D0, PME turnoff/port D-state, and PF D-state interrupts. Matching `*_INTR_MASK` registers define the mask bits.
- `BIF_PF_FLR_RST` exposes write/request bits for PF0-PF6 FLR reset.
- `BIF_DEV0_PF0_DSTATE_VALUE` through `BIF_DEV0_PF6_DSTATE_VALUE` and `BIF_PORT0_DSTATE_VALUE` expose target, acknowledge, and reset-needed D-state fields.
- `BIF_USB_SHUB_RS_RESET_CNTL` links USB SHUB RS reset to FLR or link reset behavior.

The misc block contains lower-level NBIF control, observability, and diagnostics:

- `REGS_ROM_OFFSET_CTRL` contains the `ROM_OFFSET` field read by `nbif_v6_3_1_get_rom_offset()`.
- `NBIF_STRAP_BIOS_CNTL`, `NBIF_STRAP_WRITE_CTRL`, and `MISC_SCRATCH` define BIOS strap override enables, write-once strap control, and a 32-bit scratch field.
- `INTR_LINE_POLARITY` and `INTR_LINE_ENABLE` provide per-device INTx line polarity and enable bitmaps.
- `OUTSTANDING_VC_ALLOC` controls DMA/HST virtual-channel allocation and outstanding thresholds.
- `BIFC_MISC_CTRL0`, `BIFC_MISC_CTRL1`, and `BIFC_MISC_CTRL2` cover a dense set of BIFC behavior: virtual-wire unit-ID checks, active VLINK L0, DMA VC4 non-DVM status, arbitration chain locks, GSI split-stall policy, DMA atomic checks, DMA-as-PF behavior, address phase handling, reset blocking, PCIe capability protection, ATS message blocking, secondary request disable, port D-state/PME modes, BME-drop behavior, poison/ACS violation reporting, SMN worst-error and response-data forcing, GMI request-attribute masking, completion buffer policy, and MMIO decode/protection policy.
- `BIFC_BME_ERR_LOG_LB` and `BIFC_RCCBIH_BME_ERR_LOG0` latch bus-master-enable-low errors for device functions and provide matching clear bits.
- `BIFC_DMA_ATTR_OVERRIDE_DEV0_F0_F1` through `BIFC_DMA_ATTR_OVERRIDE_DEV0_F6_F7` and `BIFC_DMA_ATTR_CNTL2_DEV0` describe DMA attribute override and force-enable fields per function pair.
- `BME_DUMMY_CNTL_0`, `BIFC_THT_CNTL`, `BIFC_HSTARB_CNTL`, and `BIFC_GSI_CNTL` control dummy completion behavior, THT credit allocation and UR/ECRC overrides, host arbitration, GSI response/request arbitration, SMN parity/burst/split behavior, and HDP flush/read count options.
- `BIFC_PCIEFUNC_CNTL`, `BIFC_PASID_CHECK_DIS`, `BIFC_PASID_STS`, and `BIF_PASID_ERR_LOG` expose PCIe function routing and PASID check/status/error bits for functions 0-6.
- `BIFC_SDP_CNTL_0`, `BIFC_SDP_CNTL_1`, and `BIFC_SDP_CNTL_2` control SDP disconnect hysteresis, disconnect disable policy, non-L0-only behavior, atomic stall policy, and credit allocation override.
- `BIFC_ATHUB_ACT_CNTL` controls ATHUB active response status typing, request drop behavior, and GSI/GMI flush triggers.
- `BIFC_PERF_CNTL_0`, `BIFC_PERF_CNTL_1`, and the four `BIFC_PERF_CNT_*_L32BIT` registers define MMIO and DMA read/write performance-counter enable, reset, event select, and low 32-bit readback fields.
- `NBIF_PGMST_CTRL`, `NBIF_PGSLV_CTRL`, and `NBIF_PG_MISC_CTRL` define NBIF power-gating, idle hysteresis, firmware power-gating exit behavior, D3-only policy, clock permission bits, refclk timing, and exit override.
- `SMN_MST_EP_CNTL3`, `SMN_MST_EP_CNTL4`, `SMN_MST_CNTL1`, and `SMN_MST_EP_CNTL5` expose per-PF SMN zero-byte read/write enablement and SMN error-response data-all-ones controls.
- `BIF_SELFRING_BUFFER_VID` and `BIF_SELFRING_VECTOR_CNTL` define self-ring client/vector selection for doorbell monitor, RAS controller, ATHUB error event, and interrupt timestamp/source behavior.
- `NBIF_INTX_DSTATE_MISC_CNTL` controls INTx deassertion checks across endpoint/downstream/SWUS D-states and PMI interrupt disable bits.
- `NBIF_PENDING_MISC_CNTL` disables FLR master/slave pending checks.
- `BIF_GMI_WRR_WEIGHT`, `BIF_GMI_WRR_WEIGHT2`, and `BIF_GMI_WRR_WEIGHT3` define GMI weighted-round-robin large-request modes and per-entry weights.
- `NBIF_PWRBRK_REQUEST` exposes a single NBIF power-brake request bit.
- `BIF_ATOMIC_ERR_LOG_DEV0_F0` through `BIF_ATOMIC_ERR_LOG_DEV0_F6` latch unsupported-request atomic error classes per function, covering opcode, request-enable-low, length, and non-relaxed-ordering/NR style errors plus matching clear bits.
- `BIF_DMA_MP4_ERR_LOG` latches MP4 SDP VC4 non-DVM and atomic request-enable-low errors plus clear bits.

## Control Flow And Runtime Use

This header chunk has no local control flow. Runtime sequencing is in C files that include the generated NBIF 6.3.1 headers.

The direct C consumer, `amdgpu/nbif_v6_3_1.c`, uses the NBIF 6.3.1 generated headers for NBIO register access. Its visible use from this chunk is:

1. `nbif_v6_3_1_get_rom_offset()` reads `regREGS_ROM_OFFSET_CTRL` with `RREG32_SOC15(NBIO, 0, ...)`.
2. It decodes the value with `REG_GET_FIELD(data, REGS_ROM_OFFSET_CTRL, ROM_OFFSET)`.
3. `REG_GET_FIELD` expands through `REGS_ROM_OFFSET_CTRL__ROM_OFFSET__SHIFT` and `REGS_ROM_OFFSET_CTRL__ROM_OFFSET_MASK` from this chunk.

Other NBIF 6.3.1 runtime code in the same C file programs doorbell apertures, interrupt control, LTR, ASPM, HDP flush, register remap, and RAS error-event interrupts through adjacent generated register families. The reset, strap, BIFC, PASID, perf-counter, power-gating, and error-log fields in this chunk are available to driver, firmware-oriented, diagnostics, or future ASIC support code even where this file does not currently program them directly.

The generated macros also participate in compile-time contracts. `REG_SET_FIELD` and `REG_GET_FIELD` require exact symbol names shaped as `<REGISTER>__<FIELD>__SHIFT` and `<REGISTER>__<FIELD>_MASK`; missing or renamed fields produce compile failures, while wrong values can compile but program or decode the wrong hardware bits.

## State And Persistence Behavior

The chunk itself has no software state or persistence. It describes hardware register state.

Strap fields represent boot-time or fuse/ROM-derived hardware configuration, often mirrored into strap registers. They determine persistent device identity and capability exposure until reset, strap reload, BIOS override, or explicit hardware-supported strap-write path changes them. Fields such as function enablement, SR-IOV enablement, total VFs, BAR sizes, PASID/ATS/ACS/AER capabilities, FLR capability, and GPUIOV policy affect what the PCIe/NBIF device exposes to the OS and to virtual functions.

Reset and D-state fields are stateful hardware controls. Reset request, reset-enable, sticky reset, reload strap, FLR, D3hot-to-D0, link-reset, and interrupt status bits can change during boot, runtime power management, FLR, GPU reset, hot reset, link reset, or suspend/resume. Some fields are command-like or status-like rather than ordinary configuration, especially reset request bits, interrupt status bits, clear bits, and auto-clear controls.

BIFC, PASID, SMN, SDP, GMI, and power-gating fields describe persistent-until-reprogrammed control state plus live status. Examples include arbitration/credit policy, PASID checking, SDP disconnect policy, GMI weights, power-gating hysteresis, clock permissions, and SMN error response behavior. Error-log fields are latch-and-clear hardware state: they preserve diagnostic evidence such as BME-low, atomic UR, PASID, and DMA MP4 errors until cleared through the corresponding clear fields or reset by hardware.

Performance counter fields are measurement state. The enable, reset, event select, and counter readback fields can be updated by diagnostic code and by traffic. The masks do not encode ownership, access type, clear semantics, or read-only/write-one-to-clear behavior, so consumers need the ASIC register spec or established driver sequence before writing these fields.

## Dependencies

This chunk depends on the surrounding AMDGPU NBIF register infrastructure:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbif/nbif_6_3_1_offset.h` supplies matching `reg<REGISTER>` offsets and base indices. The offset file contains the matching register addresses for this range, including the `RCC_STRAP1_RCC_BIF_STRAP*` family and `BIF_ATOMIC_ERR_LOG_DEV0_F0`.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/nbif_v6_3_1.c` includes this header and uses the generated field macros with SOC15 register helpers. It is selected through `amdgpu_discovery.c` for the matching NBIO/NBIF IP version and exposes `nbif_v6_3_1_funcs` to the wider AMDGPU NBIO layer.
- AMDGPU register helper macros such as `REG_SET_FIELD`, `REG_GET_FIELD`, `RREG32_SOC15`, `WREG32_SOC15`, and `WREG32_FIELD15_PREREG` consume the shift/mask metadata to preserve and manipulate register fields.
- Adjacent chunks of the same header are required for complete per-file understanding. This chunk starts after the opening fields of `RCC_STRAP1_RCC_BIF_STRAP0` and ends before the final fields/masks of `BIF_PASID_ERR_LOG`.

Sibling ASIC headers such as `nbif_6_1_sh_mask.h` and `nbio_7_2_0_sh_mask.h` contain similarly named fields, but they are not interchangeable. Names can look stable across generations while bit positions, field widths, supported functions, or register ownership rules change.

## Integration Points

Primary integration points are:

- NBIF/NBIO bring-up through `nbif_v6_3_1_funcs`, which provides revision ID, memory-size, MC access, doorbell range, clock-gating, interrupt, LTR/ASPM, register-remap, and ROM-offset services to AMDGPU core code.
- PCIe device identity and capability exposure through strap fields: device/vendor/subsystem IDs, class code, function enable, BAR sizing, MSI/MSI-X, FLR, PME, AER/ACS/ATS/PASID/page request, SR-IOV, GPUIOV, and total VF controls.
- Reset and power-management flows through hard/soft/self reset controls, FLR reset controls, D3hot-to-D0 reset controls, link-reset protection, PME turnoff timing, D-state target/ack fields, and power-gating controls.
- Virtualization and isolation paths through SR-IOV strap fields, VF aperture sizing, VF register protection, PASID checking, ATS enablement, GPUIOV fields, per-function atomic/PASID error logging, and BME-low error logs.
- RAS and diagnostics through BIFC error reporting, ATHUB active controls, self-ring interrupt/vector selection, atomic/DMA/PASID error latches, performance counters, SMN error-response policy, and interrupt status/mask fields.
- Performance and liveness tuning through outstanding VC allocation, GSI/HST arbitration, THT credit allocation, SDP disconnect hysteresis, GMI WRR weights, DMA/MMIO counter selection, and reset-protection idle state.

## Risks And Edge Cases

Manual edits are high risk because this is generated hardware metadata. A one-bit error in a mask or shift can silently alter PCIe capability exposure, break FLR/reset sequencing, hide or spuriously report errors, disable PASID/ATS/SR-IOV isolation, or corrupt power-management policy.

The chunk boundaries are artificial. `RCC_STRAP1_RCC_BIF_STRAP0` begins before line 17761, and `BIF_PASID_ERR_LOG` continues after line 20123. The later merge lane must combine adjacent chunks before treating either register family as complete.

Strap fields should not be treated as normal writable configuration. Many strap values are boot/fuse/ROM-derived and may be write-once, BIOS-controlled, or only valid during specific reset/strap reload windows. `NBIF_STRAP_WRITE_CTRL__NBIF_STRAP_WRITE_ONCE_ENABLE` is a strong signal that write ordering and one-time behavior matter.

Reset and FLR fields mix enable, sticky, exception, status, auto-clear, timeout, and request semantics in adjacent bits. Blind read-modify-write can accidentally preserve or clear command/status bits. FLR and D3hot-to-D0 paths are especially sensitive because PF0 has a richer field set than PF1-PF6.

Repeated per-function layouts invite indexing mistakes. Device 0 functions 0-6 share many field names but not identical sets; PF0 includes SR-IOV/VF aperture/RTR fields that later functions lack or reduce. Loop-based code must use the correct register offsets and field names for each function.

Security-sensitive virtualization fields are dense. Wrong PASID, ATS, ACS, SR-IOV, VF register protection, GPUIOV, BME, or VF BAR/aperture masks can expose resources to the wrong function or make the host believe a capability is present when hardware policy does not actually allow it.

Error-log clear fields are destructive. Clearing BME-low, atomic, DMA, or PASID error bits before RAS/debug code samples them can destroy evidence. Conversely, failing to clear latches after handling can cause repeated or stale reports.

Performance, arbitration, SDP, and GMI weight fields can cause plausible but hard-to-debug regressions. Bad values can surface as bandwidth loss, stalled requests, unfair virtual-channel allocation, unexpected completion ordering, timeout symptoms, or reset-protection waits that never drain.

## Test Signals

Useful validation signals include:

- Build coverage for `amdgpu/nbif_v6_3_1.c` with `nbif_6_3_1_offset.h` and `nbif_6_3_1_sh_mask.h` included. Macro-name drift in this chunk should fail compilation at `REG_GET_FIELD`/`REG_SET_FIELD` call sites.
- Static generated-header checks that every field has both `__SHIFT` and `_MASK`, masks align with shifts and expected widths, and the shift/mask/default/offset headers are generated from the same ASIC register source.
- NBIF bring-up tests on hardware using NBIF 6.3.1, checking revision ID, memory-size readout, ROM offset readout, doorbell aperture setup, HDP flush register access, LTR/ASPM programming, and interrupt routing.
- PCIe capability validation with `lspci` or equivalent, comparing exposed IDs, class code, BAR sizes, MSI/MSI-X, AER/ACS/ATS/PASID, FLR, PME, SR-IOV, and VF counts against expected strap policy.
- Reset tests covering GPU reset, FLR for each exposed PF/VF path, D3hot-to-D0 transitions, link reset, suspend/resume, and strap reload behavior while checking reset interrupt status/mask behavior and D-state target/ack fields.
- SR-IOV and virtualization tests that create/destroy VFs, exercise VF BAR and doorbell access, validate PASID/ATS behavior, and confirm isolation after FLR, D3hot-to-D0, and VF enable/disable transitions.
- RAS and diagnostic tests that intentionally trigger or simulate BME-low, atomic unsupported request, PASID, DMA MP4, SMN, or ATHUB-related errors, verify the corresponding status bits decode correctly, and verify clear bits clear only handled evidence.
- Performance and liveness tests that stress MMIO, DMA read/write, GMI traffic, SDP disconnect/reconnect, and virtual-channel arbitration while checking BIFC performance counters, absence of unexpected error latches, and no reset-protection or pending-check hangs.

### subset-b-002885: lines 20124-22598

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbif/nbif_6_3_1_sh_mask.h lines 20124-22598

## Scope

This chunk is a generated AMD NBIF 6.3.1 register field shift/mask header slice. It contains C preprocessor constants only: no functions, structs, variables, dynamic state, allocation, locking, or executable control flow.

The range starts at the tail of `BIF_PASID_ERR_LOG`, covers `BIF_PASID_ERR_CLR`, then spans NBIF virtual-wire, LCLK clock/deepsleep, SMN master, SDP, timeout-detection, BIFC credit/performance, RAS, RCC/PCIe endpoint and root-complex, BIF BX system, BIFDEC, and PF/PF-VF register-field families. It ends inside `BIF_BX_PF1_GPU_HDP_FLUSH_REQ`, after the `CP7` shift definition; the remaining shift and mask definitions for that register are in the next chunk.

Although this repository path is under a local `ceph-client` source mirror, this file is AMDGPU hardware metadata. It does not implement Ceph or distributed filesystem behavior.

## Purpose

The purpose of this header section is to publish the bitfield ABI for NBIF 6.3.1 registers. Each field generally appears as a pair:

- `<REGISTER>__<FIELD>__SHIFT`, the bit offset for packing or extracting the field.
- `<REGISTER>__<FIELD>_MASK`, the 32-bit mask for isolating or preserving the field.

The matching register-address metadata lives in `nbif_6_3_1_offset.h`, which provides symbols such as `regBIF_PASID_ERR_CLR`, `regNBIF_MGCG_CTRL_LCLK`, `regBIF_BX1_BIF_RB_CNTL`, and `regBIF_BX_PF1_GPU_HDP_FLUSH_REQ`. AMDGPU NBIO/BIF code combines the offset and mask headers with helpers such as `RREG32_SOC15`, `WREG32_SOC15`, `RREG32_PCIE`, `WREG32_PCIE`, `REG_SET_FIELD`, `REG_GET_FIELD`, and `SOC15_REG_OFFSET`.

## Important Macro Families

The early NBIF control block includes PASID error clear bits for device 0 functions 0-6, virtual-wire controls for SMN and SDP paths, per-set virtual-wire change disable/reset/trigger fields, medium-grain clock gating, LCLK deep sleep, SMN master arbitration and posted/zero-byte behavior, SDP virtual-wire triggers, SHUB timeout-detection controls/status, BIFC SDP/GMI/SST pool-credit allocation, early wakeup, and simple performance counter selectors/count values.

`NBIF_MGCG_CTRL_LCLK` is a notable integration point. It defines `NBIF_MGCG_EN_LCLK`, mode, hysteresis, host/DMA/register/AER/debug disable bits, and SRAM fine-grain clock-gating enable. Existing NBIO code reads this register, toggles `NBIF_MGCG_EN_LCLK` according to `AMD_CG_SUPPORT_BIF_MGCG`, and writes it back through PCIe register helpers.

The `BIFL_RAS_*` block covers centralized NBIF RAS handling and four repeated leaf blocks. Central control/status fields gate error-event, interrupt, egress-stall, and link-disable propagation. Each leaf exposes parity, poison, receiver-error-event, timeout logging, MCA logging, propagation, generated egress-stall, and UCP enable/status bits. `BIFL_IOHUB_RAS_IH_CNTL` and `BIFL_RAS_VWR_FROM_IOHUB` bridge these RAS events into the IOHUB interrupt/virtual-wire path.

The RCC and PCIe families cover downstream, downstream-port, endpoint, and common root-complex controls. They define fields for hidden config decoding by PCIe generation, unsupported-request reporting, AER timer/status clear behavior, completion timeout and FLR handling, link speed straps through Gen5, link bandwidth/state notification suppression, endpoint interrupt enables/status, LTR messaging, dynamic power allocation substate power values, requester ID restore, bus and device/function number capture/listing, peer framebuffer offsets, XDMA aperture bounds, VDM support, link-down entry/exit, PME blocking, and max payload/read-request sizing.

The `nbif_bif_bx_SYSDEC` block exposes indirect PCIe index/data windows, BIOS/SBIOS/driver/firmware scratch registers, GFX MMIO register CAM remap entries, and scratch/status locations. Many of these are full-width fields, meaning the macros primarily name persistent scratch or address payload registers rather than subfields.

The `nbif_bif_bx_BIFDEC1` block covers BIF strap/status/control surfaces: bus control, reset enable/control, interrupt control, CLKREQ pad fields, feature control, HDP atomic behavior, doorbell control and interrupt control, framebuffer enable, master/slave pending status, BACO entry/exit timers, memory type, SR-IOV virtual-function enable/status bitmaps, HDP flush remap addresses, a BIF ring buffer, mailbox index, MP1 interrupt control, PCIe pad controls, save/restore scratch state, S5 memory power controls, and dummy registers.

The VF bitmaps are especially repetitive and hardware-facing. `BIF_BX1_VF_REGWR_EN`, `BIF_BX1_VF_DOORBELL_EN`, `BIF_BX1_VF_FB_EN`, and matching `*_STATUS` registers provide one-bit-per-VF enable/status fields for virtual functions 0-30 or 0-31 depending on the family. These macros are part of the SR-IOV boundary where PF code controls or observes VF register-write, doorbell, and framebuffer access.

The final PF/PF-VF block begins with BME-low status/clear fields, unsupported atomic operation error logs and clear bits, doorbell self-ring GPA aperture base/control, HDP coherency flush/invalidate-only controls, and the start of `BIF_BX_PF1_GPU_HDP_FLUSH_REQ`. In this assigned range, only `CP0` through `CP7` shift constants for the flush request register are present; the rest of that register continues after line 22598.

## Control Flow

There is no runtime control flow in this header. Runtime sequencing belongs to the AMDGPU NBIO/BIF code that includes it:

1. Driver code selects a register offset from the companion offset header.
2. It reads or prepares a 32-bit value with SOC15/PCIE MMIO helpers.
3. It uses these `__SHIFT` and `_MASK` constants, commonly through `REG_SET_FIELD` or `REG_GET_FIELD`, to update or decode individual fields.
4. It writes the value back or polls status/done bits according to the hardware programming sequence.

For example, NBIO clock-gating code reads `smnNBIF_MGCG_CTRL_LCLK`, toggles `NBIF_MGCG_CTRL_LCLK__NBIF_MGCG_EN_LCLK_MASK`, and writes the value only when it changed. Another NBIO path returns `SOC15_REG_OFFSET(NBIO, 0, regBIF_BX_PF1_GPU_HDP_FLUSH_REQ)` so higher-level HDP flush logic can request engine flushes through the BIF/PF flush-request register.

## State And Persistence Behavior

This file stores no software state and persists nothing to disk. It describes MMIO-backed hardware state whose lifetime is controlled by the GPU, firmware, power management, PCIe link state, reset, suspend/resume, BACO, FLR, and SR-IOV PF/VF policy.

The represented state includes sticky error logs and clear bits, clock-gating and deepsleep configuration, RAS routing/status, PCIe link and error behavior, virtual-wire trigger/disable state, scratch registers shared with BIOS/SBIOS/firmware/driver code, doorbell and framebuffer apertures, virtual-function enable/status maps, HDP flush controls, a BIF ring-buffer base/pointers/writeback address, pad controls, and S5 memory power state. Some fields are durable configuration until reset or reprogramming; others are status, command strobes, write-one-to-clear bits, sticky logs, or hardware-owned counters/pointers. The header names bit positions but does not encode read/write side effects.

## Dependencies And Integration Points

This chunk depends on the generated NBIF 6.3.1 register database and must stay synchronized with `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbif/nbif_6_3_1_offset.h`. The offset header supplies numeric register addresses and base-index selectors; this shift/mask header supplies field layouts for those addresses.

Direct integration is through AMDGPU NBIO/BIF code under `drivers/gpu/drm/amd/amdgpu`. Nearby versioned NBIO files show the same macro families consumed for LCLK clock gating, interrupt control, indirect PCIe access, and HDP flush offsets. This chunk's `BIF_BX1_*` and `BIF_BX_PF1_*` fields also align with SR-IOV, doorbell, HDP coherency, BACO/power, PCIe error handling, and RAS paths.

The macros are untyped constants, so their correctness is enforced mostly by generated-header consistency and by hardware behavior. A renamed macro will usually fail at compile time, but a wrong mask value can compile cleanly and program the wrong bit.

## Risks And Edge Cases

- The chunk boundaries are artificial. The first line is already inside `BIF_PASID_ERR_LOG`, and the final line stops before `BIF_BX_PF1_GPU_HDP_FLUSH_REQ` masks and later engine bits. File-level reconciliation must join adjacent chunks before making whole-register claims.
- Side-effect fields are not distinguishable from plain configuration fields by type. Clear bits such as PASID, atomic, BME, AER, and status-clear fields must be used according to hardware write-one-to-clear or command semantics, not treated as ordinary persistent bits.
- Clock-gating and deep-sleep masks can affect register accessibility, DMA paths, AER/debug logic, and low-power behavior. Incorrect `NBIF_MGCG_CTRL_LCLK` or `NBIF_DS_CTRL_LCLK` programming can cause hangs, missed wakeups, or power regressions.
- RAS masks affect error propagation, MCA logging, interrupts, and egress stalls. Incorrect settings can hide poison/parity/timeout errors, create interrupt storms, or stall links unexpectedly.
- PCIe/RCC fields are interoperability-sensitive. Changing FLR, LTR, AER, max payload, requester ID, link speed, hidden config decode, or completion timeout behavior can break specific root complexes, virtualization flows, or suspend/resume cases.
- SR-IOV VF enable/status bitmaps are dense and repetitive. Off-by-one shifts in VF register-write, doorbell, or framebuffer access maps can grant or deny the wrong VF.
- HDP flush request/done and coherency flush controls are ordering-sensitive. Wrong masks or offsets can leave CPU-visible GPU memory stale or cause hangs in code waiting for a flush acknowledgment.
- Full-width scratch and address fields are not self-validating. Using the wrong offset with a full-width mask can silently overwrite firmware/BIOS/driver coordination state.

## Test Signals

Useful validation is mostly integration and hardware oriented:

- Build AMDGPU with NBIF/NBIO support for ASICs using the NBIF 6.3.1 headers; missing or renamed macros should fail in versioned NBIO/BIF code.
- Exercise clock-gating enable/disable paths and confirm `NBIF_MGCG_CTRL_LCLK` changes do not produce register-access failures, hangs, or power-management regressions.
- Run PCIe and suspend/resume tests that cover FLR, link-state changes, LTR, AER/error reporting, BACO, and S5-related state.
- In SR-IOV configurations, validate PF-controlled VF register-write, doorbell, and framebuffer enable/status behavior for every VF represented by the bitmaps.
- Use RAS/error-injection or diagnostic paths, where available, to confirm leaf and central RAS status, logging, interrupt, and clear behavior.
- Exercise HDP flush paths through command processor and SDMA workloads; stale CPU-visible memory, timeout waiting for flush done, or incorrect flush request offsets are strong signals of mask/offset drift.

### subset-b-002886: lines 22599-25014

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbif/nbif_6_3_1_sh_mask.h lines 22599-25014

## Scope And Purpose

This chunk is a generated AMD NBIF 6.3.1 shift/mask header segment. It contains no executable C code, functions, structs, or persistent software objects. Its purpose is to publish preprocessor constants that name bit positions and bit masks for NBIF/NBIO hardware registers so driver code can read, write, and preserve individual register fields through helpers such as `REG_SET_FIELD`, `REG_GET_FIELD`, `WREG32_SOC15`, and `RREG32_SOC15`.

The selected range starts in the middle of the `BIF_BX_PF1_GPU_HDP_FLUSH_REQ` field list, with the corresponding register family beginning just above the requested line range. From there it covers the rest of the PF1 BIF/PFVF register field definitions, an extensive `RCC_STRAP2` strap block, GDC DMA/HST SION arbitration and credit controls, GDC core and power/clock controls, GDC RAS controls/status registers, GDC reset controls, GDC S2A doorbell routing controls, A2S arbitration and tag allocation controls, syshub direct reset/NIC400 overrides, and the start of the device/function VF0 BIF/PFVF register field definitions.

The chunk is source-tree-aligned with AMDGPU's NBIF/NBIO hardware support. Its constants are only meaningful together with sibling generated register offset definitions from `nbif_6_3_1_offset.h` and with the driver code that selects the matching register namespace for the ASIC instance/function being programmed.

## Important APIs, Types, And Macro Families

There are no C APIs or types defined here. The "interface" is the generated macro naming contract:

- `<REGISTER>__<FIELD>__SHIFT` gives the bit offset for a hardware field.
- `<REGISTER>__<FIELD>_MASK` gives the field mask in the register value.
- Register address symbols with matching `<REGISTER>` names live in `nbif_6_3_1_offset.h`.
- Consumers rely on the AMDGPU register helpers to combine these field constants with read-modify-write operations.

The PF1 BIF/PFVF families cover a second physical-function style register namespace. `BIF_BX_PF1_BIF_BME_STATUS` reports and clears DMA activity observed while bus mastering is low. `BIF_BX_PF1_BIF_ATOMIC_ERR_LOG` reports unsupported-request atomic error causes such as opcode, request-enable-low, length, and non-relaxed cases, with separate clear bits. `BIF_BX_PF1_DOORBELL_SELFRING_GPA_APER_*` defines the low/high base and enable/mode/size fields for the doorbell self-ring GPA aperture. `BIF_BX_PF1_HDP_*_COHERENCY_*` provides one-bit control fields for HDP register and memory coherency flush, flush-only, and invalidate-only controls.

The PF1 HDP flush request/done families are repeated 32-bit bitmaps. Bits 0-9 map command processor engines `CP0` through `CP9`, bits 10-11 map `SDMA0` and `SDMA1`, and bits 12-31 are reserved engine slots. `BIF_BX_PF1_GPU_HDP_FLUSH_REQ` is the request bitmap, while `BIF_BX_PF1_GPU_HDP_FLUSH_DONE` is the completion/status bitmap. The same layout appears later for `BIF_BX_DEV0_EPF0_VF0_GPU_HDP_FLUSH_REQ` and the beginning of `..._DONE` for VF0.

The PF1 mailbox families define 32-bit transmit and receive message buffers, a four-bit handshake in `BIF_BX_PF1_MAILBOX_CONTROL` (`TRN_MSG_VALID`, `TRN_MSG_ACK`, `RCV_MSG_VALID`, `RCV_MSG_ACK`), interrupt enables for valid/ack transitions, and a compact VM/HV mailbox register with 4-bit transmit/receive payload fields, valid/ack bits, and interrupt enable bits. These are low-level hardware communication registers, not software queues.

The `RCC_STRAP2` block describes strap-derived PCIe/NBIF configuration. The general BIF strap registers include link-generation disables and kills, VGA/ROM/memory aperture pins, GPUIOV enablement, local prefix/error ignore policy, link-down reset, fuse/ROM strap validity, write-disable, SWUS aperture settings, DLF/margining/PHY support, PCIe extended capability behavior, lane equalization, target link speed, and reset/link power policy. Device port straps describe downstream-port capabilities such as LTR, MSI, timeout, OBFF, power budget data, atomics, virtual channels, ACS controls, 10-bit tags, TPH, Gen5 compliance, port identity, bus/device/function numbers, and vendor ID. EPF0 and EPF1 straps describe function identity, SR-IOV, page-size/VF counts, class/vendor/subsystem IDs, reset-time-reporting timings, PASID/ATS/PRI-related capabilities, MSI/MSI-X, AER/ACS, FLR, PME, BAR/aperture sizing, VF BAR sizing, GPUIOV VSEC revision, and other capability exposure.

The `nbif_gdc_dma_sion_SIONDEC` and `nbif_gdc_hst_sion_SIONDEC` blocks define sideband/interconnect arbitration for DMA and host-facing SION client lanes. For DMA clients CL0-CL3 and host clients CL0-CL1, the macros cover read-response, write-response, and request burst target registers, time-slot registers, request/data/read-response/write-response pool credit allocation registers, and per-block control registers with clock-gating enable/mode/hysteresis and live-active fields. These fields tune traffic shaping and resource allocation rather than implementing a software algorithm.

The `nbif_gdc_GDCDEC` block defines GDC-level controls. `GDC1_SHUB_REGS_IF_CTL` controls non-PF MMREG request handling and VF protection. `GDC1_A2S_QUEUE_FIFO_ARB_CNTL`, `GDC1_S2A_MISC_CNTL`, and `GDC1_ATDMA_MISC_CNTL` expose arbitration priorities, arbitration modes, and weighted round-robin weights. `GDC1_NGDC_MGCG_CTRL`, `GDC1_NGDC_EARLY_WAKEUP_CTRL`, `GDC1_NGDC_PG_MISC_CTRL`, `GDC1_NGDC_PGMST_CTRL`, and `GDC1_NGDC_PGSLV_CTRL` define medium-grain clock gating, SRAM fine-grain clock gating, early wakeup, power-gating, idleness, firmware exit, and clock idle hysteresis controls.

The `nbif_gdc_ras_gdc_ras_regblk` block provides GDC RAS/error response control and observability. `GDCSOC_ERR_RSP_CNTL` can bypass, accumulate, or force read-response status/data-status behavior. `GDCSOC_RAS_CENTRAL_STATUS` summarizes L2C and C2L egress-stall and error-event detections. Leaf control registers 0-4 repeat enable bits for error-event detection, poison/parity/receiver-error event and stall handling, generation/propagation of error events and egress stalls, MCA logging, UCP, and for leaf2 a RAS interrupt enable. Leaf2 misc controls define RAS drop, interrupt mask disable, ATHUB request/response action, and dummy-chain controls. Leaf status registers report error event received, poison/parity detection, generated status, propagated status, and egress-stall status.

The `nbif_gdc_rst_GDCRST_DEC` block describes reset controls for PF FLR, graphics driver/VPU reset, link reset, hard reset, soft reset, SDP port reset, and reset-misc trailer settings. These fields distinguish reset enable, action, mask, completion, global assertion, link-reset selection, hard/soft reset modes, and per-port reset bits.

The `nbif_gdc_s2a_GDCS2A_DEC` block maps sixteen `GDC_S2A1_S2A_DOORBELL_ENTRY_N_CTRL` registers. Each entry has enable, AWID, range offset, range size, address-high nibble value, address-high compare enable, and BIF queue-select fields. The common control register defines BIF doorbell packet mode and the NBIF graphics doorbell status register exposes `DOORBELL_INTERRUPT_STATUS`. These fields gate which doorbell address ranges are routed to which clients.

The `nbif_gdc_a2s_GDCA2S_DEC` block defines A2S traffic controls: static/dynamic virtual-channel selection, SDP write-chain disable controls, write tag behavior for chained and non-chained writes, read/write WRR weights, message block level, response accumulation selection, read-response priority, and tag allocation counts for VC0, VC1, VC3, and VC7.

The syshub direct block contains small reset and fabric override controls: `HST_CLK0_SW0_CL0_CNTL`, `HST_CLK0_SW1_CL0_CNTL`, and `DMA_CLK0_SW0_CL0_CNTL` can enable FLR or link-reset behavior on reset sequencers; `NIC400_1_ASIB_0_FN_MOD` and `NIC400_1_IB_0_FN_MOD` expose read/write issuing override bits.

The VF0 BIF/PFVF block at the end mirrors the PF BME status, atomic error log, doorbell self-ring GPA aperture, HDP coherency flush, and GPU HDP flush request/done layout for `BIF_BX_DEV0_EPF0_VF0_*`. This is the virtual-function scoped register namespace for the same classes of behavior.

## Control Flow And Runtime Use

This header has no runtime control flow. It participates at preprocessing and compile time: a driver source file names a register and field, then macro expansion supplies the shift and mask used to construct or extract a hardware register value.

The main NBIF 6.3.1 integration point is `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/nbif_v6_3_1.c`, which includes `nbif_6_3_1_offset.h` and this header. That C file primarily uses the PF0 version of the same generated register families for this ASIC generation. For example, `nbif_v6_3_1_enable_doorbell_selfring_aperture()` sets the self-ring aperture enable, mode, and size fields, then writes low/high doorbell base registers. `nbif_v6_3_1_get_hdp_flush_req_offset()` and `nbif_v6_3_1_get_hdp_flush_done_offset()` return the HDP flush request/done offsets, and `nbif_v6_3_1_hdp_flush_reg` stores per-engine done masks for common HDP flush handling.

The PF1 names covered by this chunk are directly visible in related NBIO code, especially `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/nbio_v7_11.c`. There, `nbio_v7_11_enable_doorbell_selfring_aperture()` uses `BIF_BX_PF1_DOORBELL_SELFRING_GPA_APER_CNTL` fields to enable and size the self-ring aperture, writes the PF1 self-ring GPA base registers, and then writes the PF1 aperture control register. The same file returns PF1 HDP flush request/done offsets and fills `nbio_v7_11_hdp_flush_reg` with the PF1 `GPU_HDP_FLUSH_DONE` engine masks.

S2A doorbell entry fields are used by NBIF/NBIO doorbell range setup paths. In `nbif_v6_3_1.c`, the visible code uses S2A0 entry macros to program SDMA and IH doorbell windows by setting enable, AWID, range offset, range size, and address-high fields. This chunk's S2A1 entry macros provide the same style of register surface for the S2A1 block.

The strap, RAS, reset, GDC power/clock, SION arbitration, A2S, and syshub macros are mostly hardware register surface in this tree. They may be read by init, diagnostics, firmware, virtualization, RAS, or future power/traffic-management code, but the header itself does not dictate sequencing. Correct sequencing lives in the NBIF/NBIO driver, firmware interface, and ASIC programming guide.

## State And Persistence Behavior

No software state is allocated or persisted by this header. Including it only adds macro definitions to a compilation unit.

The hardware registers described by the macros do hold device state. Important state classes include PF/VF DMA and BME-low latches, atomic error logs and clear bits, HDP coherency flush request/done state, mailbox message payloads and valid/ack handshakes, PCIe strap-derived capability exposure, SR-IOV and GPUIOV capability/control exposure, doorbell self-ring base and aperture enablement, S2A doorbell routing windows, SION arbitration/credit allocations, GDC clock/power-gating policy, RAS detection/propagation/logging controls, RAS status latches, and reset controls.

Many fields in this range are persistent until the device is reset or the driver/firmware reprograms them. Strap fields may be read-only or effectively fixed after fuse/ROM strap sampling. Status fields such as RAS central/leaf status, BME-low status, atomic error status, transaction-pending bits, mailbox valid/ack bits, and HDP flush done bits are hardware-updated. Clear fields such as `CLEAR_DMA_ON_BME_LOW` and `CLEAR_UR_ATOMIC_*` are write-control fields. The masks do not encode access permissions, side effects, or write-one-to-clear semantics; call sites must know that behavior from the register specification.

State persistence is security-sensitive for virtualization fields. Incorrect GPUIOV/SR-IOV strap interpretation, VF aperture sizing, VF register protection, VF doorbell mapping mode, ATS/PASID/PRI exposure, or non-PF MMREG request handling can affect isolation between PFs, VFs, and guests.

## Dependencies And Integration Points

The immediate dependency is `nbif_6_3_1_offset.h`, which supplies the register addresses and base indices corresponding to these field layouts. Consumers must pair the correct offset symbol with the matching shift/mask register namespace; mixing PF0, PF1, BIF_BX0, BIF_BX1, S2A0, S2A1, or VF0 families can compile while programming the wrong register.

The generated field names depend on AMDGPU's register helper conventions. `REG_SET_FIELD(value, REGISTER, FIELD, new_value)` expects both `REGISTER__FIELD_MASK` and `REGISTER__FIELD__SHIFT` to exist. `REG_GET_FIELD` has the same naming dependency for extracting bitfields. `WREG32_SOC15`, `RREG32_SOC15`, and `SOC15_REG_OFFSET` supply the SOC15 register access path and base-index selection.

Direct include integration points include `amdgpu/nbif_v6_3_1.c` and display resource code that includes the NBIF 6.3.1 offsets. Related PF1 use appears in `amdgpu/nbio_v7_11.c`, where the same register family names are used to implement doorbell self-ring aperture setup and HDP flush offsets/masks. Broader AMDGPU subsystems that consume the resulting NBIO/NBIF hooks include KFD doorbell remapping, interrupt handling, SDMA/IH doorbell setup, HDP cache flush synchronization, PCIe/RSMU indexed access, reset handling, SR-IOV/GPUIOV support, RAS logging, and power management.

The mailbox and VM/HV mailbox definitions are integration points for low-level firmware or hypervisor communication flows. The RAS definitions integrate with any code that enables, injects, logs, or reports GDC error events. The SION/A2S/GDC arbitration definitions integrate with performance, traffic-shaping, and QoS tuning. The strap definitions integrate with capability discovery and emulated PCI configuration exposure.

## Risks And Edge Cases

This file is generated hardware metadata, so manual edits are high risk. A one-bit mask or shift error can silently change the hardware field being programmed while still compiling cleanly.

The requested chunk begins after the `BIF_BX_PF1_GPU_HDP_FLUSH_REQ` comment and initial field definitions. Any chunk-local research or automated parser must account for that boundary; the complete request family starts just above line 22599, while this chunk contains its tail plus all masks and the following done register.

PF, PF1, BIF_BX0/BIF_BX1, and VF0 register names are similar but not interchangeable. The visible NBIF 6.3.1 C path mainly uses PF0 field macros, while related NBIO 7.11 code uses PF1 macros directly. Using the wrong namespace can route doorbells or HDP flushes to the wrong function or instance.

HDP flush bits are per engine. Missing a CP or SDMA mask, using a request bit as a done bit, or polling the wrong done register can hang cache-flush waits or let GPU/CPU coherency proceed before HDP writes are visible.

Doorbell aperture programming splits a 64-bit base across low/high registers and uses a compact control register for enable, mode, and size. Wrong base splitting, stale enable state, or bad range size can make rings unreachable or expose doorbell pages outside the intended aperture.

Strap fields expose PCIe, SR-IOV, GPUIOV, ATS, PASID, ACS, BAR, MSI/MSI-X, reset, and power-management capabilities. Treating strap values as freely writable policy instead of sampled hardware configuration can break enumeration, hot reset, FLR, VF assignment, or IOMMU behavior. Fields such as `WRITE_DISABLE`, strap validity bits, reset-time-reporting values, and SR-IOV total VF counts need especially cautious interpretation.

RAS and reset fields have strong side effects. Enabling error propagation, MCA logging, RAS interrupts, egress stalls, dummy-chain behavior, PF FLR reset, hard reset, soft reset, link reset, or SDP port reset without the expected sequencing can cause device hangs, unexpected interrupts, or loss of in-flight transactions.

SION/A2S arbitration and credit fields can create performance regressions that are not obvious in functional tests. Bad weights, credits, time slots, or virtual-channel mappings may only show under DMA, host-response, or doorbell-heavy workloads.

Mailbox valid/ack bits are handshake state. A caller must preserve the expected ordering between writing message buffer dwords, asserting valid, observing ack, consuming receive buffers, and clearing/acking receive state; the masks alone do not provide synchronization or locking.

## Test Signals

Build coverage should compile all AMDGPU files that include `nbif_6_3_1_sh_mask.h`, especially `amdgpu/nbif_v6_3_1.c`. Related NBIO PF1 coverage should include `amdgpu/nbio_v7_11.c`, where PF1 doorbell self-ring and HDP flush masks are consumed.

Static generated-header validation should confirm that every field in this chunk has a matching `__SHIFT` and `_MASK`, that masks align with shifts and expected widths, and that register names match entries in `nbif_6_3_1_offset.h`. It should also flag duplicate-looking PF/PF1/VF0 names for manual namespace review rather than collapsing them.

Runtime HDP flush tests should exercise CP0-CP9 and SDMA0-SDMA1 flush request/done paths on supported hardware. A useful signal is that common AMDGPU HDP flush waits complete reliably and that CPU-visible memory reflects GPU writes after the flush.

Doorbell tests should enable and disable the self-ring aperture, program a high 64-bit doorbell base, submit work through command processor, SDMA, and interrupt-handler doorbell paths, and verify that incorrect ranges do not receive writes. SR-IOV or GPUIOV configurations should verify PF/VF doorbell isolation.

PCIe/strap validation should compare decoded strap fields against expected device enumeration: link speed capabilities, BAR sizes, MSI/MSI-X, AER/ACS/ATS/PASID/PRI capability exposure, SR-IOV VF count and page sizes, class/vendor/device IDs, FLR/PME support, and reset-time-reporting values.

RAS tests should enable GDC RAS detection/logging paths in a controlled environment, inject or provoke supported parity/poison/error-event cases, and verify central status, leaf status, interrupt/MCA reporting, and clear/recovery behavior. Negative tests should verify that disabled propagation or logging bits remain quiet.

Reset tests should cover PF FLR, link reset, soft reset, hard reset, and SDP port reset paths, checking that completion bits and post-reset register state match expectations and that in-flight DMA/doorbell paths recover.

Traffic and performance tests should stress DMA, host response, SION, A2S, and doorbell-heavy workloads while changing only validated arbitration/credit/clock-gating settings. Regressions may appear as latency spikes, timeouts, lower throughput, or RAS/error response events rather than immediate functional failure.

### subset-b-002887: lines 25015-27550

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbif/nbif_6_3_1_sh_mask.h lines 25015-27550

## Scope And Purpose

This chunk is generated AMD NBIF 6.3.1 register bitfield metadata. It contains no executable C code, functions, structs, allocation, locking, or direct MMIO operations. Its public interface is a large set of C preprocessor constants describing bit shifts and masks for PCIe/NBIO virtual-function register fields.

The line range starts in the middle of `BIF_BX_DEV0_EPF0_VF0_GPU_HDP_FLUSH_DONE`, covering the reserved-engine tail and all mask definitions for VF0's HDP flush-done register. It then defines VF0 transaction-pending, mailbox, system PF/VF decode, RCC error/configuration, and GFX MSI-X vector fields. The range fully covers the repeated VF1 through VF7 blocks and ends at the opening of VF8's `BIF_ATOMIC_ERR_LOG` definitions. Because the chunk boundaries are artificial, the beginning depends on the previous chunk for the first VF0 flush-done shift fields and the end depends on the next chunk for the rest of VF8.

The purpose of these macros is to let AMDGPU NBIF/NBIO code name hardware bitfields instead of hard-coding numeric masks. The macros are paired with register offsets from `nbif_6_3_1_offset.h` and consumed by field helpers such as `REG_SET_FIELD`, `REG_GET_FIELD`, `WREG32_FIELD15_PREREG`, `RREG32_SOC15`, `WREG32_SOC15`, and `SOC15_REG_OFFSET`.

Although this repository is rooted under `distributed-fs/ceph-client`, this file is Linux AMD GPU driver hardware metadata. It is not Ceph filesystem code and has no filesystem persistence behavior.

## Important Macro Families

The chunk uses the generated convention `<REGISTER>__<FIELD>__SHIFT` and `<REGISTER>__<FIELD>_MASK`. The covered range contains 2065 `#define` lines, including 1026 shift definitions and 1071 mask definitions.

The `BIF_BX_DEV0_EPF0_VF*_BIF_BME_STATUS` registers expose `DMA_ON_BME_LOW` status and `CLEAR_DMA_ON_BME_LOW`. These fields track and clear DMA activity observed while PCI bus-master enable was low, which is relevant to virtualization and PCIe error diagnosis.

The `BIF_BX_DEV0_EPF0_VF*_BIF_ATOMIC_ERR_LOG` registers log unsupported-request atomic conditions: opcode, request-enable-low, length, and non-relaxed ordering, plus matching clear bits in the upper half of the register. VF1 through VF7 are complete here; VF0 began in the previous chunk and VF8 begins at the chunk tail.

The `DOORBELL_SELFRING_GPA_APER_*` registers define per-VF self-ring doorbell GPA aperture base high/low values and aperture controls. The control fields include enable, mode, and size. These are security- and isolation-sensitive because doorbell apertures let GPU clients signal queues through mapped MMIO/GPA windows.

The HDP coherency control families include `HDP_REG_COHERENCY_FLUSH_CNTL`, `HDP_MEM_COHERENCY_FLUSH_CNTL`, `HDP_MEM_COHERENCY_FLUSH_ONLY_CNTL`, and `HDP_MEM_COHERENCY_INVALIDATE_ONLY_CNTL`. Each exposes a small address/control field used to trigger host data path register or memory coherency operations.

The `GPU_HDP_FLUSH_REQ` and `GPU_HDP_FLUSH_DONE` families publish a 32-bit engine bitmap. Fields cover command processor engines `CP0` through `CP9`, `SDMA0`, `SDMA1`, and reserved engine bits `RSVD_ENG0` through `RSVD_ENG19`. Request bits initiate HDP flushes for engines; done bits report completion. The VF0 done masks are at the start of this chunk; complete request/done pairs are present for VF1 through VF7.

The `BIF_TRANS_PENDING` registers expose `BIF_MST_TRANS_PENDING` and `BIF_SLV_TRANS_PENDING`, used to observe outstanding master/slave transactions before reset, power transitions, or virtualization state changes.

The mailbox block for each VF includes four transmit dwords, four receive dwords, `MAILBOX_CONTROL`, `MAILBOX_INT_CNTL`, and `BIF_VMHV_MAILBOX`. The basic mailbox control bits are transmit valid/ack and receive valid/ack. Interrupt control bits enable valid and ack interrupts. The VM/HV mailbox packs small transmit/receive data fields, valid/ack flags, and interrupt-enable bits for hypervisor/virtual-machine communication.

The `SYSPFVFDEC` block defines indirect MMIO access registers `MM_INDEX`, `MM_DATA`, and `MM_INDEX_HI`. `MM_INDEX` carries a 31-bit offset and an aperture bit, `MM_INDEX_HI` carries the high offset, and `MM_DATA` carries the 32-bit data payload.

The `RCC_DEV0_EPF0_VF*_RCC_*` families describe per-VF RCC error and configuration registers. They include SR-IOV invalid register access status, doorbell read access status, doorbell aperture enable, configured memory size, reserved configuration data, and `RCC_IOV_FUNC_IDENTIFIER` with a function identifier bit and an IOV enable bit.

The `RCC_DEV0_EPF0_VF*_GFXMSIX_*` block defines four MSI-X vector table entries per VF in this range. Each vector has low/high message address, message data, and a `MASK_BIT` control field. The `GFXMSIX_PBA` register exposes pending bits for vector 0 and vector 1.

## Control Flow And Runtime Use

There is no runtime control flow in this header. The only behavior is C preprocessing: driver code names a register field, and the compiler substitutes the generated shift and mask constants.

Runtime sequencing lives in the AMDGPU NBIF/NBIO implementation. `amdgpu/nbif_v6_3_1.c` includes both `nbif_6_3_1_offset.h` and this mask header. It uses the same generated register stack to read the NBIF revision ID, get memory size from `RCC_DEV0_EPF0_RCC_CONFIG_MEMSIZE`, configure doorbell aperture enable, program doorbell ranges, remap HDP registers for KFD, provide HDP flush request/done offsets, configure interrupt handling, set the MMIO remap window, and handle the RAS ATHUB interrupt path.

The direct NBIF 6.3.1 implementation mostly uses PF0, BIF_BX0, GDC, PCIE, and non-VF RCC register families rather than every VF-specific macro in this chunk. The VF macro families still form the same hardware interface for SR-IOV/virtualization flows, diagnostics, firmware/hypervisor programming, and future code that needs to address per-VF doorbell, mailbox, HDP flush, transaction, RCC, or MSI-X state.

Older and sibling NBIO implementations in the tree show the common VF0 HDP remap pattern: in SR-IOV or when the normal MMIO hole cannot be used, `rmmio_remap.reg_offset` may be based on a VF0 HDP memory coherency flush register offset. That pattern explains why the VF HDP fields are important even when most NBIF 6.3.1 code paths use PF0 register names.

## State And Persistence Behavior

The header itself stores no state and performs no I/O. Its constants become part of compiled driver code wherever included.

The described hardware registers are device state. Doorbell aperture base/control values, RCC memory size/configuration, IOV enable/function identifier, MSI-X vector address/data/mask fields, and mailbox interrupt enables persist in hardware until reset, power loss, function reset, firmware/hypervisor reprogramming, or driver reinitialization.

Several fields are live status or sticky error state. `DMA_ON_BME_LOW`, atomic unsupported-request flags, BIF master/slave transaction pending bits, mailbox valid/ack bits, VM/HV mailbox valid/ack bits, MSI-X pending bits, and HDP flush-done bits may change asynchronously as hardware, firmware, host, or guest activity proceeds.

Several fields are command-like or clear-on-write by naming. `CLEAR_DMA_ON_BME_LOW`, the atomic error clear fields, HDP flush request bits, mailbox ack bits, and interrupt clear/ack style bits must be handled with the access semantics expected by the hardware specification. The generated mask file does not distinguish read-only, write-one-to-clear, pulse, sticky, firmware-owned, or reserved behavior; callers must know that from the register spec and implementation context.

## Dependencies And Integration Points

The immediate dependency is `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbif/nbif_6_3_1_offset.h`, which supplies the matching `reg...` offsets and base indices. This shift/mask header supplies only field layout; it is not sufficient to address registers by itself.

The primary implementation integration point is `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/nbif_v6_3_1.c`. That file includes this header and uses AMDGPU SOC15 register helpers to program NBIF/NBIO hardware. It exposes the `amdgpu_nbio_funcs` table for higher-level AMDGPU code, including HDP flush offsets, PCIe indirect offsets, memory-controller access, memory-size query, doorbell range setup, interrupt handling, ASPM programming, register remap setup, and RAS interrupt registration.

The fields also integrate indirectly with GPUVM/KFD and queue signaling because HDP flush and doorbell aperture setup affect coherency and queue wakeup behavior. The KFD MMIO remap path uses HDP flush remap registers so user-mode compute paths can reach a controlled MMIO window.

SR-IOV and hypervisor integration is central to this chunk. Per-VF register families define isolation surfaces for doorbells, mailbox messaging, MSI-X vectors, transaction drain status, invalid register access logging, and IOV function identity. Mistakes in these masks can affect guest/host communication, interrupt routing, or memory aperture isolation.

Display code under `drivers/gpu/drm/amd/display/dc/resource/dcn401/dcn401_resource.c` includes `nbif_6_3_1_offset.h`, showing that NBIF 6.3.1 register addresses can be shared outside the core `amdgpu/nbif_v6_3_1.c` file. This chunk's field masks remain part of the same generated register contract even when a particular consumer only needs offsets.

## Risks And Edge Cases

The largest risk is treating generated metadata as ordinary editable code. A one-bit shift or mask error can make valid driver logic write the wrong hardware bit while still compiling cleanly.

Chunk boundaries are incomplete. VF0 `GPU_HDP_FLUSH_DONE` begins before this range, and VF8 `BIF_ATOMIC_ERR_LOG` continues after it. Any final per-file analysis must merge adjacent chunks before claiming complete coverage for those two registers.

The repeated VF blocks invite copy/paste and wrong-function mistakes. VF1 through VF7 have nearly identical field layouts and offsets in the matching offset header. Code must select the correct VF register namespace and address window for the function it is managing; using VF0 masks or offsets for a different VF can target the wrong virtual function.

Doorbell aperture and RCC IOV fields are isolation-sensitive. Wrong base, size, enable, or IOV identity masks can expose doorbell pages incorrectly, prevent a guest from signaling queues, or allow access patterns outside the intended function boundary.

Mailbox fields are handshake-oriented. Setting valid/ack bits out of order, failing to preserve unrelated bits during read-modify-write, or mishandling interrupt enables can wedge host/guest mailbox communication or lose messages.

HDP flush request/done fields are coherency-sensitive. Incorrect masks for CP or SDMA engines can make the driver believe a flush completed for the wrong engine, which can surface as stale CPU/GPU views of memory, compute queue corruption, or hard-to-reproduce synchronization failures.

MSI-X vector fields are interrupt-routing-sensitive. Address low fields start at bit 2 and mask off alignment bits; incorrect packing can program unaligned message addresses or mask/unmask the wrong vector. PBA fields in this chunk expose only two pending bits despite four vector entries, so consumers should not assume a one-to-one complete pending-bit layout without checking the full hardware spec.

Status and clear fields sit close together in several registers. Read-modify-write helpers must be used carefully where write-one-to-clear or pulse semantics exist, otherwise diagnostic evidence may be cleared or command bits may be retriggered.

## Test Signals

Build coverage should compile AMDGPU paths that include `nbif_6_3_1_sh_mask.h`, especially `amdgpu/nbif_v6_3_1.c`. Macro drift normally appears as compile failures in `REG_SET_FIELD`, `REG_GET_FIELD`, `WREG32_FIELD15_PREREG`, or register-offset references.

Static validation should compare this generated mask header against `nbif_6_3_1_offset.h` and the source register database used to generate both files. Useful checks include verifying every field has a matching `__SHIFT` and `_MASK`, masks align with their shifts and widths, and repeated VF1-VF7 blocks remain structurally identical where expected.

Runtime smoke tests on NBIF 6.3.1 hardware should cover NBIF initialization, memory-size readback, doorbell aperture enable/disable, SDMA/VCN/IH/GC doorbell range setup, HDP flush request/done polling, MMIO remap setup, and RAS ATHUB interrupt enable/clear paths.

SR-IOV tests should exercise PF and VF boot, guest doorbell signaling, mailbox transmit/receive valid/ack handshakes, per-VF MSI-X programming and masking, and invalid-register-access/error-log reporting. Tests should include VF1 through VF7 explicitly because this chunk fully defines those repeated blocks.

Coherency tests should trigger CP and SDMA HDP flushes and verify that the expected done bits are observed before CPU-visible memory is consumed. Failures may appear as queue timeouts, stale memory, or inconsistent KFD/user-mode queue behavior.

Error-path tests should trigger or simulate BME-low DMA status, unsupported atomic request logs, BIF transaction-pending observation, RCC invalid-access status, and MSI-X pending state, then verify that clear bits clear only the intended latched status.

Regression indicators include mailbox timeouts, missing or misrouted interrupts, VF doorbell failures, unexpected SR-IOV isolation faults, HDP flush hangs, stale-memory symptoms after flush, incorrect memory-size reporting, persistent BIF transaction-pending bits during reset, or RAS ATHUB interrupt clear failures.

### subset-b-002888: lines 27551-30056

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbif/nbif_6_3_1_sh_mask.h lines 27551-30056

## Scope

This chunk covers a generated AMD NBIF 6.3.1 register shift/mask header section for SR-IOV virtual-function register blocks. It starts in the middle of `BIF_BX_DEV0_EPF0_VF8_BIF_ATOMIC_ERR_LOG`, then covers the rest of the VF8 block, complete repeated blocks for VF9 through VF14, and the beginning of VF15 through `BIF_BX_DEV0_EPF0_VF15_MAILBOX_MSGBUF_TRN_DW2`.

The file is data-only C preprocessor material. It defines no functions, structs, variables, locks, allocations, or direct MMIO operations. Its public interface is the standard generated register-field convention:

- `<REGISTER>__<FIELD>__SHIFT` for bit positions.
- `<REGISTER>__<FIELD>_MASK` for the corresponding 32-bit field mask.

The matching register addresses live in `nbif_6_3_1_offset.h`. Active C users include `amdgpu/nbif_v6_3_1.c`, which includes both the offset and shift/mask headers and consumes the same field families through AMDGPU register helpers such as `REG_SET_FIELD`, `REG_GET_FIELD`, `RREG32_SOC15`, `WREG32_SOC15`, and `SOC15_REG_OFFSET`.

## Purpose

These macros describe the ABI between AMDGPU/NBIO code, firmware, and NBIF hardware for per-VF BIF and RCC register windows on NBIF 6.3.1 ASICs. The covered virtual functions are mostly VF8 through VF14, plus partial VF15. Each full VF block repeats the same semantic layout:

- BIF bus-master and PCIe atomic-operation error status.
- Doorbell self-ring guest-physical-address aperture base and control fields.
- HDP register/memory coherency flush command fields.
- GPU HDP flush request and done bits for CP, SDMA, and reserved engines.
- Transaction-pending status.
- PF/VF mailbox transmit and receive message buffers, control, interrupt enable, and VM/HV compact mailbox fields.
- VF indirect MMIO index/data/index-high window fields.
- RCC SR-IOV error, doorbell aperture, memory-size, reserved config, and IOV identity fields.
- RCC MSI-X vector table and pending-bit array fields.

The chunk is primarily a generated hardware register contract. It does not decide policy itself, but it allows policy code and firmware-facing paths to compose exact register values for SR-IOV virtual functions.

## Important Macro Families

### BIF Error and Bus-Master Status

For VF9 through VF15, and the tail of VF8 at the chunk start, `BIF_BME_STATUS` exposes `DMA_ON_BME_LOW` plus `CLEAR_DMA_ON_BME_LOW`. `BIF_ATOMIC_ERR_LOG` exposes unsupported-request atomic error causes: opcode, request enable low, length, and non-relaxed/NR state, along with clear bits for each latch.

These fields are status/clear style, not ordinary configuration. The `CLEAR_*` bits imply write-to-clear behavior and need read/modify/write care so software does not accidentally drop adjacent error state.

### Doorbell Self-Ring Aperture

Each covered VF has:

- `DOORBELL_SELFRING_GPA_APER_BASE_HIGH`
- `DOORBELL_SELFRING_GPA_APER_BASE_LOW`
- `DOORBELL_SELFRING_GPA_APER_CNTL`

The base registers are full-width 32-bit halves of a guest physical address. The control register has enable, mode, and size fields. The PF0 version of this family is actively used in `nbif_v6_3_1_enable_doorbell_selfring_aperture()`, where the driver writes `adev->doorbell.base` into the base-low/high registers, sets enable and mode, and programs size through `REG_SET_FIELD`. The VF variants in this chunk describe equivalent per-VF doorbell self-ring aperture state.

### HDP Coherency Flush Controls

The chunk defines one-bit address fields for:

- `HDP_REG_COHERENCY_FLUSH_CNTL`
- `HDP_MEM_COHERENCY_FLUSH_CNTL`
- `HDP_MEM_COHERENCY_FLUSH_ONLY_CNTL`
- `HDP_MEM_COHERENCY_INVALIDATE_ONLY_CNTL`

The PF0 equivalents are used by NBIF register remapping and rMMIO setup in `nbif_v6_3_1_remap_hdp_registers()` and `nbif_v6_3_1_set_reg_remap()`. For VFs, these masks describe the per-function flush/invalidate aperture used to keep host data path visibility coherent across guest, host, and GPU engines.

### GPU HDP Flush Request/Done Handshake

`GPU_HDP_FLUSH_REQ` and `GPU_HDP_FLUSH_DONE` are full 32-bit bitmaps. Bits 0-9 are `CP0` through `CP9`, bits 10-11 are `SDMA0` and `SDMA1`, and bits 12-31 are reserved engine bits. The layout is repeated for each full VF block and the partial VF15 block.

The PF0 form is wired into `nbif_v6_3_1_get_hdp_flush_req_offset()`, `nbif_v6_3_1_get_hdp_flush_done_offset()`, and `nbif_v6_3_1_hdp_flush_reg`. GFX, MES, and SDMA code later use the NBIO function table and `struct nbio_hdp_flush_reg` masks to submit flush requests and wait for done bits. The VF masks provide the same per-engine handshake layout for virtualized register spaces.

Reserved engine bits are exposed by the generated header, but comparable NBIO code comments in other versions note that reserved HDP bits may be firmware-owned. Consumers should not assign new engine semantics to `RSVD_ENG*` bits without hardware/firmware confirmation.

### PF/VF Mailboxes and VM/HV Mailbox

For VF8 through VF14, the chunk defines four transmit message buffer dwords, four receive message buffer dwords, mailbox control bits, interrupt enable bits, and a compact `BIF_VMHV_MAILBOX` register. VF15 includes only transmit dwords 0 through 2 before the chunk ends.

The message buffer dwords are full-width `MSGBUF_DATA` fields. `MAILBOX_CONTROL` exposes transmit valid/ack and receive valid/ack bits. `MAILBOX_INT_CNTL` enables valid and ack interrupts. `BIF_VMHV_MAILBOX` packs VM/HV transmit/receive data nibbles, valid bits, ack bits, and interrupt enables into one register.

These fields implement a small state machine: producer writes message data, asserts valid, waits for ack; receiver observes valid, consumes data, and asserts ack. The header only supplies bit positions; ordering, timeout, and interrupt-routing rules come from mailbox users and firmware contracts.

### VF Indirect MMIO Window

For VF8 through VF14, `MM_INDEX`, `MM_DATA`, and `MM_INDEX_HI` define an indirect MMIO access window. `MM_INDEX` packs a 31-bit offset plus `MM_APER` in bit 31, `MM_INDEX_HI` extends the offset, and `MM_DATA` carries the read/write payload.

This is a critical integration surface for virtualized MMIO access because it can let guest-visible function code address selected register apertures without direct physical register mapping. Incorrect masks here can redirect register access to the wrong aperture or truncate high address bits.

### RCC SR-IOV Configuration and Error State

For VF8 through VF14, `RCC_ERR_LOG` exposes invalid SR-IOV register access and doorbell-read access status. `RCC_DOORBELL_APER_EN` enables the BIF doorbell aperture. `RCC_CONFIG_MEMSIZE` and `RCC_CONFIG_RESERVED` are full-width configuration registers. `RCC_IOV_FUNC_IDENTIFIER` exposes function identity and a high-bit `IOV_ENABLE`.

The PF0 doorbell aperture equivalent is used by `nbif_v6_3_1_enable_doorbell_aperture()` through `WREG32_FIELD15_PREREG`. The VF variants map the same kind of state into per-VF RCC decode blocks.

### RCC MSI-X Vector State

For VF8 through VF14, each block defines MSI-X vector 0 through vector 3 address-low, address-high, message-data, and control registers, plus `GFXMSIX_PBA`. Address-low masks bits 31:2, matching the natural alignment of MSI/MSI-X message addresses. Control exposes a `MASK_BIT`. The PBA exposes two pending bits.

These macros describe guest interrupt delivery state. They integrate with PCIe/MSI-X programming and interrupt handling, even though the source chunk itself has no interrupt handler code.

## Control Flow and State Behavior

There is no executable control flow in this header. Its behavior is compile-time: C code includes it and uses the generated constants to build and decode NBIF MMIO values.

The state represented by the fields is persistent hardware state until overwritten, reset, or cleared by status-specific write semantics. Persistent configuration includes doorbell base/control registers, RCC memory-size and IOV identity state, indirect MMIO aperture selectors, and MSI-X table values. Transient or command/status state includes BME-low and atomic-error latches, HDP flush request/done bits, transaction-pending bits, mailbox valid/ack bits, mailbox interrupt enables, RCC error logs, and MSI-X pending bits.

The implied control-flow patterns are hardware handshakes rather than C branches:

- Doorbell aperture setup writes base low/high before enabling the control register.
- HDP flushing writes a request bit for the relevant engine and waits for the matching done bit.
- PF/VF mailbox exchange writes message data, toggles valid, observes ack, and may use interrupt-enable bits for valid/ack events.
- Error logs are read, decoded, and cleared with matching clear bits.
- Indirect MMIO access writes index/index-high state and transfers payload through data.

## Dependencies and Integration Points

This chunk depends on generated NBIF and AMDGPU infrastructure:

- `nbif_6_3_1_offset.h` supplies the matching `reg...` addresses and base indices.
- `nbif_6_3_1_sh_mask.h` supplies the field masks in this chunk and adjacent PF/VF chunks.
- `soc15.h`-style AMDGPU helpers consume the `__SHIFT` and `_MASK` naming convention.
- `amdgpu/nbif_v6_3_1.c` includes this header and registers `nbif_v6_3_1_funcs`, including doorbell aperture setup, HDP flush offsets, rMMIO HDP remap, indirect PCIe index/data offsets, ASPM programming, and RAS interrupt hooks.
- GFX, MES, and SDMA paths use NBIO HDP flush offsets/masks through the NBIO function table and `adev->nbio.hdp_flush_reg`.
- SR-IOV and virtualization paths are the natural owners of the per-VF BIF/RCC blocks, because all covered register names are scoped under `DEV0_EPF0_VF*`.
- PCIe/MSI-X interrupt delivery integrates with the `GFXMSIX_*` vector table and PBA fields.

## Risks

- Generated bitfield drift is high impact. A wrong shift or mask can target the wrong NBIF field, breaking doorbells, coherency flushes, mailbox handshakes, indirect MMIO, or interrupt delivery.
- The VF blocks are mechanically repetitive. Copy-generation errors between VF8, VF9, VF10, VF11, VF12, VF13, VF14, and VF15 could silently isolate one virtual function from doorbells, HDP flush completion, or MSI-X delivery.
- Status clear bits share registers with status bits. Careless writes to `CLEAR_*`, mailbox ack/valid bits, or error-clear fields can lose diagnostic state or acknowledge events prematurely.
- Doorbell aperture base/control fields are security-sensitive under SR-IOV. Misprogramming can expose wrong guest physical addresses, disable guest doorbells, or route writes across function boundaries.
- HDP flush masks must match engine ownership. Using reserved engine bits or mixing request/done masks can cause hangs, false completion, stale CPU/GPU memory visibility, or firmware conflicts.
- Indirect MMIO index/data fields are sensitive because wrong offset or aperture bits can redirect register access. In a virtualized environment, this can become both a stability and isolation issue.
- Mailbox valid/ack sequencing needs timeout and ordering discipline. The macros do not enforce producer/consumer ordering or interrupt masking rules.
- MSI-X vector fields affect interrupt routing. Corrupt address, data, mask, or pending-bit interpretation can drop interrupts, signal the wrong host vector, or leave a VF stuck with masked interrupts.
- The chunk boundaries are partial: the start omits the first VF8 atomic-error fields and the end cuts VF15 mailbox definitions mid-block. The merge lane must use neighboring chunks before making complete per-VF coverage claims.

## Test and Validation Signals

Useful validation is mostly compile-time coverage plus hardware or emulated SR-IOV bring-up:

- Build AMDGPU with `amdgpu/nbif_v6_3_1.c` including `nbif/nbif_6_3_1_offset.h` and `nbif/nbif_6_3_1_sh_mask.h`; this catches missing or renamed generated macros.
- Exercise NBIF 6.3.1 device initialization paths that call `nbif_v6_3_1_funcs`, especially doorbell aperture setup, doorbell self-ring setup, HDP register remapping, and rMMIO remap selection.
- Run GFX, MES, and SDMA ring tests that issue HDP flushes through `get_hdp_flush_req_offset()`, `get_hdp_flush_done_offset()`, and `nbif_v6_3_1_hdp_flush_reg`; failures can reveal incorrect CP/SDMA request/done masks.
- In SR-IOV mode, validate VF8 through VF14 and the completed VF15 block after merge: doorbell writes, HDP flush completion, mailbox valid/ack exchange, and indirect MMIO access should work per VF without cross-function leakage.
- Verify PCIe/MSI-X interrupt setup for virtual functions by programming vector address/data/control fields, toggling mask bits, and checking pending-bit behavior.
- Inject or observe BIF atomic unsupported-request and BME-low events where possible; confirm status bits set and clear through the documented clear masks.
- Stress suspend/resume, FLR, VF reset, and GPU reset paths. Persistent doorbell, mailbox, MSI-X, and indirect-MMIO state should be reinitialized or cleared consistently.
- Run virtualization isolation tests that attempt invalid SR-IOV register and doorbell-read accesses and confirm `RCC_ERR_LOG` status is reported without exposing unauthorized register state.

## Unresolved Cross-Chunk References

Line 27551 starts inside `BIF_BX_DEV0_EPF0_VF8_BIF_ATOMIC_ERR_LOG`; the register comment and first atomic-error fields are in the previous chunk. Line 30056 ends inside `BIF_BX_DEV0_EPF0_VF15_MAILBOX_MSGBUF_TRN_DW2`; the rest of VF15 mailbox, MMIO, RCC, and MSI-X definitions are in the following chunk. The final per-file reconciliation should stitch these boundaries before summarizing complete VF8 or VF15 behavior.

### subset-b-002889: lines 30057-32583

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbif/nbif_6_3_1_sh_mask.h lines 30057-32583

## Purpose

This chunk is generated AMDGPU NBIF 6.3.1 register bitfield metadata. It contains `#define` constants for register field shifts and masks, not executable code. The covered region describes per-SR-IOV-virtual-function fields for the device 0 endpoint function 0 VF aperture, spanning the end of VF15, complete VF16 through VF22 blocks, and the beginning of VF23.

The macros are paired with the sibling offset header, `nbif_6_3_1_offset.h`, where the same register names receive address and base-index definitions. Driver code includes `nbif/nbif_6_3_1_sh_mask.h` from `amdgpu/nbif_v6_3_1.c`; generic AMDGPU register helpers such as `REG_SET_FIELD()` and `REG_GET_FIELD()` consume the `REGISTER__FIELD__SHIFT` and `REGISTER__FIELD_MASK` naming convention throughout the driver tree.

## Register Groups Covered

The slice is organized by generated `addressBlock` comments:

- Tail of `nbif_bif_bx_dev0_epf0_vf15_BIFPFVFDEC1`: VF15 mailbox transmit/receive data words, mailbox control/interrupt enable, and compact VM/HV mailbox fields.
- `nbif_bif_bx_dev0_epf0_vf15_SYSPFVFDEC`: VF15 indirect MMIO index/data/index-high fields.
- `nbif_rcc_dev0_epf0_vf15_BIFPFVFDEC1`: VF15 RCC error, doorbell aperture enable, config memory size/reserved, and IOV function identity fields.
- `nbif_rcc_dev0_epf0_vf15_BIFDEC2`: VF15 GFX MSI-X vector table and pending-bit array fields.
- Repeated full `BIFPFVFDEC1`, `SYSPFVFDEC`, RCC `BIFPFVFDEC1`, and RCC `BIFDEC2` blocks for VF16, VF17, VF18, VF19, VF20, VF21, and VF22.
- Beginning of `nbif_bif_bx_dev0_epf0_vf23_BIFPFVFDEC1`: VF23 BME/atomic/doorbell/HDP coherency and GPU HDP flush request fields, ending inside the VF23 GPU HDP flush done field definitions.

The repeated full VF blocks define the same field layout per VF with only the `VF##` register-name component changing. This makes the region a generated map of isolated virtual-function register windows rather than a set of independent hand-written definitions.

## Important APIs, Types, and Macros

There are no C functions or types in this chunk. The important API surface is the macro naming contract:

- `REGISTER__FIELD__SHIFT`: bit position used by field extraction and insertion helpers.
- `REGISTER__FIELD_MASK`: bit mask for the same field.
- Register comments such as `//BIF_BX_DEV0_EPF0_VF16_GPU_HDP_FLUSH_REQ`: delimit one hardware register's fields.
- Address block comments such as `// addressBlock: nbif_bif_bx_dev0_epf0_vf16_BIFPFVFDEC1`: preserve the hardware address-space grouping from AMD register generation.

Notable field families:

- `BIF_BME_STATUS`: `DMA_ON_BME_LOW` status and `CLEAR_DMA_ON_BME_LOW` write/clear bit, used to observe and clear DMA activity while bus-master enable is low.
- `BIF_ATOMIC_ERR_LOG`: unsupported-request atomic error latches for opcode, request-enable-low, length, and non-relaxed/NR-style conditions, plus clear bits at positions 16-19.
- `DOORBELL_SELFRING_GPA_APER_*`: high/low base and control fields for VF doorbell self-ring guest physical aperture enable, mode, and size.
- `HDP_REG_COHERENCY_FLUSH_CNTL` and `HDP_MEM_COHERENCY_FLUSH_CNTL`: single-bit flush-address controls for register and memory coherency.
- `GPU_HDP_FLUSH_REQ` and `GPU_HDP_FLUSH_DONE`: 32-bit engine bitmaps for CP0-CP9, SDMA0-SDMA1, and reserved engines. Request and done masks must align bit-for-bit for polling or completion checks.
- `BIF_TRANS_PENDING`: a single `TRANS_PENDING` status bit.
- `MAILBOX_MSGBUF_TRN_DW*` and `MAILBOX_MSGBUF_RCV_DW*`: full 32-bit data words for VF mailbox transmit and receive payloads.
- `MAILBOX_CONTROL`: transmit/receive valid and acknowledge bits at positions 0, 1, 8, and 9.
- `MAILBOX_INT_CNTL`: valid and ack interrupt enables.
- `BIF_VMHV_MAILBOX`: compact VM/HV mailbox interrupt enables, 4-bit data fields, valid bits, and ack bits.
- `MM_INDEX`, `MM_DATA`, `MM_INDEX_HI`: indirect MMIO index/data window with low 31-bit offset, aperture selector at bit 31, and high offset extension.
- `RCC_ERR_LOG`, `RCC_DOORBELL_APER_EN`, `RCC_CONFIG_MEMSIZE`, `RCC_CONFIG_RESERVED`, and `RCC_IOV_FUNC_IDENTIFIER`: RCC-side SR-IOV status/configuration fields.
- `GFXMSIX_VECT[0-3]_*` and `GFXMSIX_PBA`: MSI-X message address, data, per-vector mask bit, and two pending bits.

## Control Flow and State Behavior

This header contributes no direct control flow. Runtime behavior emerges when AMDGPU code reads or writes the corresponding registers through the offset definitions and these masks.

State represented here is hardware-resident and mostly volatile:

- Error-status registers expose latched hardware conditions and paired clear bits. Using the wrong clear mask can either fail to clear a condition or clear the wrong latch.
- Doorbell aperture fields configure guest-visible doorbell routing for each VF. These values affect how VF software signals queues or rings.
- HDP flush request/done fields model a request/completion handshake. Software sets request bits for engines and polls matching done bits, so request/done field drift is a coherency and hang risk.
- Mailbox registers model persistent-in-register handshakes until the peer updates valid/ack bits. The transmit and receive data words are full 32-bit payload registers.
- MSI-X vector fields hold interrupt message address/data/mask state, with pending bits recording delivery state.
- Indirect MMIO index/data fields preserve the usual indexed-register access state: writes to index select an offset/aperture, and data accesses target that selection.

No disk persistence, memory allocation, locking, or driver-owned data structure is defined in this chunk.

## Dependencies and Integration Points

The chunk depends on the generated AMD register naming scheme and its companion headers:

- `nbif_6_3_1_offset.h` supplies addresses and base indices for these same register names, for example VF16 `GPU_HDP_FLUSH_REQ`, `MAILBOX_CONTROL`, and `RCC_DEV0_EPF0_VF16_GFXMSIX_VECT0_ADDR_LO`.
- Older or alternate generated headers such as `include/asic_reg/nbio/nbio_2_3_sh_mask.h`, `nbio_2_3_offset.h`, and `nbio_2_3_default.h` contain analogous NBIO register metadata and defaults for related ASIC blocks.
- `amdgpu/nbif_v6_3_1.c` includes this header, so any driver code in that compilation unit can use these bit masks directly.
- AMDGPU register helper macros rely on exact names and suffixes. A field named `X` for register `Y` is expected to define `Y__X__SHIFT` and `Y__X_MASK`.

The immediate integration surface is low-level GPU initialization, SR-IOV virtualization support, mailbox handling between PF/VF or VM/HV contexts, interrupt/MSI-X setup, doorbell aperture programming, and HDP coherency-flush handling.

## Risks

- Generated constants are easy to treat as inert, but a single incorrect shift or mask can corrupt hardware programming across all VFs sharing the repeated pattern.
- The repeated VF16-VF22 blocks should remain structurally identical except for VF number. Divergence may indicate a generation issue unless backed by hardware documentation.
- This chunk starts and ends mid-VF context: it begins after earlier VF15 definitions and stops inside VF23. File-level research must reconcile adjacent chunks before drawing conclusions about complete VF15 and VF23 coverage.
- `GPU_HDP_FLUSH_REQ` and `GPU_HDP_FLUSH_DONE` define 32 one-bit fields each. Any mismatch between engine bit names, masks, or offsets can break flush completion polling and cause stale CPU/GPU-visible memory state.
- Mailbox valid/ack bits are small single-bit handshakes. Swapping transmit and receive fields or using a data mask on control bits can deadlock PF/VF or VM/HV communication.
- MSI-X address-low fields start at shift 2 with mask `0xFFFFFFFC`, reflecting aligned message addresses. Treating the field as a raw 32-bit value can discard or mis-handle low address bits.
- Clear bits for BME and atomic error logs are separate high-half bits, not the same bits as the status latches. Read/modify/write helpers need to avoid accidentally writing stale status bits as commands.

## Test and Validation Signals

Useful validation for this chunk is mostly structural and hardware-facing:

- Build coverage: compile AMDGPU code paths that include `nbif/nbif_6_3_1_sh_mask.h`, especially `amdgpu/nbif_v6_3_1.c`, to catch missing or renamed generated macros.
- Header consistency checks: verify every `REGISTER__FIELD__SHIFT` in the slice has the matching `REGISTER__FIELD_MASK`, and that each register has a companion address/base index in `nbif_6_3_1_offset.h` where expected.
- Pattern checks: compare VF16 through VF22 field sets for exact shape equality after replacing `VF16`...`VF22` with a placeholder.
- Runtime SR-IOV tests: create VFs, exercise doorbells, mailbox send/receive, MSI-X delivery/masking, and reset/error-clear paths.
- Coherency tests: submit CP/SDMA work that requires HDP flushes and confirm request bits transition to matching done bits without timeout.
- Error-injection or negative tests: trigger invalid SR-IOV register access, doorbell read access, atomic unsupported-request logging, and BME-low DMA detection, then confirm the documented clear bits reset the latched status.

### subset-b-002890: lines 32584-32806

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbif/nbif_6_3_1_sh_mask.h lines 32584-32806

## Scope

This chunk is the final section of the generated AMD NBIF 6.3.1 shift/mask header. It contains C preprocessor constants for hardware register bit positions and masks; it defines no C functions, structs, enums, variables, locks, memory allocations, or executable logic.

The range starts at the tail of the `BIF_BX_DEV0_EPF0_VF23_GPU_HDP_FLUSH_REQ` mask family, covers the complete `BIF_BX_DEV0_EPF0_VF23_GPU_HDP_FLUSH_DONE` family, VF23 transaction-pending status, mailbox data/control/interrupt fields, the compact VM/hypervisor mailbox, VF23 indirect MM access windows, VF23 RCC error and SR-IOV identity/configuration fields, four VF23 graphics MSI-X vector entries, the graphics MSI-X pending-bit array, and the closing `#endif`.

The source file is under `sources/distributed-fs/ceph-client`, but this header is AMDGPU DRM hardware-description data. It is unrelated to Ceph client filesystem behavior.

## Purpose

`nbif_6_3_1_sh_mask.h` supplies the field side of the NBIF 6.3.1 hardware ABI. Driver code pairs these `REGISTER__FIELD__SHIFT` and `REGISTER__FIELD_MASK` macros with register offsets from `nbif_6_3_1_offset.h` and SOC15/register helper APIs. The specific slice describes per-virtual-function register layouts for EPF0 VF23 and a small RCC/MSI-X tail block.

The covered fields support:

- HDP coherency flush request/done synchronization for command processor and SDMA engines.
- VF23 transaction-idle detection through BIF master/slave pending flags.
- PF/VF mailbox transport and receive buffers, valid/ack handshakes, and interrupt enables.
- A compact VMHV mailbox with 4-bit transmit/receive payload nibbles plus valid/ack and interrupt-enable bits.
- Indirect MM register access through index/data/high-index registers.
- RCC-side SR-IOV diagnostics and VF identification/configuration registers.
- VF23 graphics MSI-X table programming for four vectors and pending-bit reporting.

Because this is a generated register header, its central purpose is exact bitfield naming and numeric accuracy rather than algorithmic behavior. A single bad mask can make higher-level driver code read, poll, or write the wrong hardware bit.

## Important Macro Families

### HDP Flush Request and Done

The first three lines are the end of `BIF_BX_DEV0_EPF0_VF23_GPU_HDP_FLUSH_REQ`, defining masks for reserved engines 17, 18, and 19 at bits 29, 30, and 31. The rest of the request register is in the previous chunk.

`BIF_BX_DEV0_EPF0_VF23_GPU_HDP_FLUSH_DONE` is complete in this chunk. It defines matching one-bit fields for:

- `CP0` through `CP9` at bits 0-9.
- `SDMA0` and `SDMA1` at bits 10-11.
- `RSVD_ENG0` through `RSVD_ENG19` at bits 12-31.

The masks are the direct powers-of-two equivalents from `0x00000001L` through `0x80000000L`. The layout mirrors other NBIF/NBIO HDP flush register families used by AMDGPU. In `amdgpu/nbif_v6_3_1.c`, the PF0 variants of this family are wired into `nbif_v6_3_1_hdp_flush_reg`, and `nbif_v6_3_1_get_hdp_flush_req_offset()` / `nbif_v6_3_1_get_hdp_flush_done_offset()` return the PF0 request/done offsets. VF23 uses the same conceptual request/done protocol, with VF-specific register names and offsets.

### Transaction Pending

`BIF_BX_DEV0_EPF0_VF23_BIF_TRANS_PENDING` exposes:

- `BIF_MST_TRANS_PENDING` at bit 0.
- `BIF_SLV_TRANS_PENDING` at bit 1.

These fields indicate outstanding master-side and slave-side NBIF transactions for the VF23 BIF window. They are natural polling/status inputs for reset, FLR, quiesce, suspend, or virtualization management flows.

### Full-Word Mailbox Buffers

The mailbox message buffers are full 32-bit fields:

- Transmit buffers: `BIF_BX_DEV0_EPF0_VF23_MAILBOX_MSGBUF_TRN_DW0` through `_DW3`.
- Receive buffers: `BIF_BX_DEV0_EPF0_VF23_MAILBOX_MSGBUF_RCV_DW0` through `_DW3`.

Each register exposes `MSGBUF_DATA` with shift `0x0` and mask `0xFFFFFFFFL`. Together, the transmit and receive sides provide four doublewords each for PF/VF mailbox payloads.

### Mailbox Control and Interrupt Control

`BIF_BX_DEV0_EPF0_VF23_MAILBOX_CONTROL` defines the mailbox handshake bits:

- `TRN_MSG_VALID` at bit 0.
- `TRN_MSG_ACK` at bit 1.
- `RCV_MSG_VALID` at bit 8.
- `RCV_MSG_ACK` at bit 9.

`BIF_BX_DEV0_EPF0_VF23_MAILBOX_INT_CNTL` defines:

- `VALID_INT_EN` at bit 0.
- `ACK_INT_EN` at bit 1.

The split between transmit valid/ack and receive valid/ack encodes a hardware handshake protocol. Software must treat these as synchronization bits, not as arbitrary persistent storage.

### VMHV Mailbox

`BIF_BX_DEV0_EPF0_VF23_BIF_VMHV_MAILBOX` is a compact VM/hypervisor mailbox register with both data and control in one 32-bit word:

- `VMHV_MAILBOX_TRN_ACK_INTR_EN` at bit 0.
- `VMHV_MAILBOX_RCV_VALID_INTR_EN` at bit 1.
- `VMHV_MAILBOX_TRN_MSG_DATA` in bits 8-11 (`0x00000F00L`).
- `VMHV_MAILBOX_TRN_MSG_VALID` at bit 15.
- `VMHV_MAILBOX_RCV_MSG_DATA` in bits 16-19 (`0x000F0000L`).
- `VMHV_MAILBOX_RCV_MSG_VALID` at bit 23.
- `VMHV_MAILBOX_TRN_MSG_ACK` at bit 24.
- `VMHV_MAILBOX_RCV_MSG_ACK` at bit 25.

This is a lower-bandwidth mailbox than the four-doubleword message-buffer interface. It is suitable for small command/status nibbles plus interrupt-assisted valid/ack signaling.

### Indirect MM Access

The `nbif_bif_bx_dev0_epf0_vf23_SYSPFVFDEC` address block defines:

- `BIF_BX_DEV0_EPF0_VF23_MM_INDEX`, with `MM_OFFSET` in bits 0-30 and `MM_APER` at bit 31.
- `BIF_BX_DEV0_EPF0_VF23_MM_DATA`, with full-width `MM_DATA`.
- `BIF_BX_DEV0_EPF0_VF23_MM_INDEX_HI`, with full-width `MM_OFFSET_HI`.

The matching offset header places these at base index 0 (`regBIF_BX_DEV0_EPF0_VF23_MM_INDEX`, `reg...MM_DATA`, and `reg...MM_INDEX_HI`). This is an indirect access aperture: software programs an index/offset, optionally high offset bits, then reads or writes the data window. Correct ordering is enforced by the caller and hardware semantics, not by this macro header.

### RCC VF23 Error and SR-IOV Configuration

The `nbif_rcc_dev0_epf0_vf23_BIFPFVFDEC1` block defines:

- `RCC_DEV0_EPF0_VF23_RCC_ERR_LOG`: `INVALID_REG_ACCESS_IN_SRIOV_STATUS` at bit 0 and `DOORBELL_READ_ACCESS_STATUS` at bit 1.
- `RCC_DEV0_EPF0_VF23_RCC_DOORBELL_APER_EN`: `BIF_DOORBELL_APER_EN` at bit 0.
- `RCC_DEV0_EPF0_VF23_RCC_CONFIG_MEMSIZE`: full-width `CONFIG_MEMSIZE`.
- `RCC_DEV0_EPF0_VF23_RCC_CONFIG_RESERVED`: full-width `CONFIG_RESERVED`.
- `RCC_DEV0_EPF0_VF23_RCC_IOV_FUNC_IDENTIFIER`: `FUNC_IDENTIFIER` at bit 0 and `IOV_ENABLE` at bit 31.

These fields are SR-IOV and register-protection sensitive. Error-log bits report invalid SR-IOV register access and doorbell-read access status. Doorbell aperture enable controls whether the VF can use the BIF doorbell aperture. The function identifier and `IOV_ENABLE` bit describe whether this virtual function participates in IOV mode.

### VF23 Graphics MSI-X Table

The `nbif_rcc_dev0_epf0_vf23_BIFDEC2` block defines four graphics MSI-X vector entries:

- `RCC_DEV0_EPF0_VF23_GFXMSIX_VECT0_*` through `VECT3_*`.
- Each vector has `ADDR_LO`, `ADDR_HI`, `MSG_DATA`, and `CONTROL`.
- `ADDR_LO.MSG_ADDR_LO` starts at bit 2 and uses mask `0xFFFFFFFCL`, reflecting the alignment of MSI-X message addresses.
- `ADDR_HI.MSG_ADDR_HI` and `MSG_DATA.MSG_DATA` are full-width fields.
- `CONTROL.MASK_BIT` is bit 0 for vector masking.

`RCC_DEV0_EPF0_VF23_GFXMSIX_PBA` exposes pending bits 0 and 1 only in this NBIF 6.3.1 VF23 chunk. The companion offset header confirms the vector registers use base index 3 and that the PBA is at offset `0x0800` in the same base-index domain.

## Control Flow and Runtime Use

This header has no executable control flow. Runtime behavior comes from driver code that includes the header and uses the macros with register offsets and MMIO helpers.

Known local integration around this generation:

1. `amdgpu/nbif_v6_3_1.c` includes `nbif/nbif_6_3_1_offset.h` and `nbif/nbif_6_3_1_sh_mask.h`.
2. The NBIF 6.3.1 implementation exposes HDP flush request/done offsets to ring code through `adev->nbio.funcs->get_hdp_flush_req_offset` and `get_hdp_flush_done_offset`.
3. It populates `struct nbio_hdp_flush_reg` with HDP flush done masks for PF0 CP and SDMA clients. Generic GFX and SDMA ring paths use those masks as reference/mask values when emitting HDP flush packets or polling commands.
4. VF23-specific HDP flush, mailbox, and MSI-X macros in this chunk are not directly referenced by the searched C implementation, but they follow the same generated ABI pattern and are available for virtualization, debug, register dump, firmware-interaction, or future VF-specific code paths.

The implied hardware flows are:

- A client writes or triggers a `GPU_HDP_FLUSH_REQ` bit for an engine, then waits until the corresponding `GPU_HDP_FLUSH_DONE` bit is observed.
- Reset or quiesce code can inspect `BIF_TRANS_PENDING` before assuming the VF's BIF path is idle.
- Mailbox senders write message data, assert valid, and wait for an ack; receivers observe valid, consume data, and assert ack. Interrupt enables decide whether valid/ack transitions raise interrupts.
- MSI-X setup programs message address/data fields and clears or sets vector mask bits; pending bits report interrupts that are pending while vectors are masked.

## State and Persistence Behavior

The header stores no software state. The represented state lives in hardware registers and persists according to GPU reset, FLR, power management, PF/VF assignment, firmware programming, and explicit driver writes.

Important state classes:

- HDP flush request/done bits are transient synchronization state. They gate cache/coherency visibility for engines such as CP and SDMA.
- Transaction-pending bits are status state owned by the BIF hardware.
- Mailbox data buffers and valid/ack bits are shared communication state between PF/VF or VM/hypervisor participants.
- Mailbox interrupt-enable bits are configuration state that controls whether mailbox handshakes generate interrupts.
- Indirect MM index/data registers are access-window state. A stale index can redirect a later data access to the wrong register.
- RCC error-log bits are diagnostic/latch-like status; clearing semantics are determined by the hardware contract outside this header.
- Doorbell aperture enable, config memsize/reserved, and IOV function identifier state are virtualization configuration inputs.
- MSI-X address/data/control and PBA bits are interrupt routing and delivery state. Vector masking persists until changed or reset.

## Dependencies and Integration Points

Direct generated dependencies:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbif/nbif_6_3_1_offset.h` supplies matching register addresses and base indices. For this chunk, the VF23 BIFPFVFDEC1 registers use base index 2, the indirect MM window uses base index 0, and the graphics MSI-X table uses base index 3.
- Other chunks of `nbif_6_3_1_sh_mask.h` define the beginning of the VF23 `GPU_HDP_FLUSH_REQ` family, PF0 equivalents used directly by `nbif_v6_3_1.c`, and the broader NBIF PCIe/RCC/SR-IOV register contract.

Driver integration:

- `amdgpu/nbif_v6_3_1.c` is the direct NBIF 6.3.1 consumer and includes this header.
- `amdgpu/amdgpu_nbio.h` defines `struct nbio_hdp_flush_reg` and the NBIO function hooks used by graphics and SDMA rings.
- `amdgpu/amdgpu_gfx.c` uses `adev->nbio.hdp_flush_reg` to derive CP HDP flush masks for graphics rings.
- SDMA implementations such as `sdma_v6_0.c`, `sdma_v5_2.c`, and `sdma_v4_4_2.c` use NBIO-provided HDP flush offsets and masks to emit ring-level HDP flush/poll operations.
- MSI-X, SR-IOV, mailbox, and doorbell fields are hardware integration points for PCIe interrupt setup, VF management, PF/VF communication, and hypervisor-facing device control even when this exact VF23 name set is not referenced by a local C file.

## Risks and Edge Cases

- The chunk begins mid-register-family. The first three macros are only the tail of `BIF_BX_DEV0_EPF0_VF23_GPU_HDP_FLUSH_REQ`; final per-file reconciliation must merge the previous chunk for CP, SDMA, and earlier reserved-engine request bits.
- Bitfield drift in generated masks is high impact. Incorrect HDP flush done masks can make ring code wait on the wrong bit, skip a needed coherency flush, or time out.
- Reserved-engine bits are not free scratch bits. Other NBIO generations explicitly warn that some reserved HDP flush bits can be firmware-owned; callers should only use engine mappings documented for the ASIC.
- Mailbox valid/ack fields require protocol sequencing. Setting valid before payload writes, clearing ack too early, or enabling interrupts without a handler can lose messages or create interrupt storms.
- The indirect MM index/data interface is order-sensitive. Concurrent users need external serialization, and stale `MM_INDEX` or `MM_INDEX_HI` state can make a later `MM_DATA` access hit the wrong register.
- SR-IOV error and doorbell fields are isolation-sensitive. Wrong use can expose doorbells, hide invalid register access, or misidentify IOV state for a VF.
- MSI-X vector fields are interrupt-critical. Bad address/data masks or stale `MASK_BIT` state can misroute interrupts, leave interrupts masked, or report misleading pending bits.
- The VF23 block repeats patterns present for other VFs. Mechanical generation errors are plausible around VF numbers, base indices, vector numbers, and pending-bit counts. Adjacent offset/mask chunks should be compared when validating a generator update.

## Test and Verification Signals

Useful validation is mostly build, register readback, and hardware integration:

- Build AMDGPU code that includes `nbif_6_3_1_sh_mask.h` and `nbif_6_3_1_offset.h`; this catches missing or malformed generated names.
- On NBIF 6.3.1 hardware, issue HDP flushes through graphics and SDMA rings and confirm the expected request/done bits transition before memory-visible operations proceed.
- Exercise reset, FLR, suspend/resume, or VF teardown paths and confirm `BIF_TRANS_PENDING` reaches idle before destructive actions.
- In SR-IOV or VF debug environments, verify VF23 mailbox traffic by writing transmit buffers, setting `TRN_MSG_VALID`, observing `TRN_MSG_ACK`, and checking receive valid/ack behavior with and without mailbox interrupts enabled.
- Validate VMHV mailbox nibble payloads and valid/ack interrupt enables using firmware or hypervisor diagnostics that can see both endpoints.
- Test indirect MM access by programming `MM_INDEX`/`MM_INDEX_HI`, reading/writing `MM_DATA`, and confirming the targeted register changes while unrelated registers remain untouched.
- Inject or provoke invalid SR-IOV register access and doorbell-read cases, then check `RCC_ERR_LOG` status bits.
- Program the VF23 graphics MSI-X vectors, toggle `CONTROL.MASK_BIT`, generate interrupts, and confirm delivery or PBA pending behavior matches mask state.
- Compare register dumps against `nbif_6_3_1_offset.h` base-index plus offset calculations for the VF23 BIFPFVFDEC1, SYSPFVFDEC, and BIFDEC2 blocks.

## Cross-Chunk Notes

This is the end of `nbif_6_3_1_sh_mask.h`. The previous chunk is required for the start of `BIF_BX_DEV0_EPF0_VF23_GPU_HDP_FLUSH_REQ` and for earlier VF23 BIF/RCC fields such as BME status, atomic error logging, doorbell self-ring GPA aperture, and HDP coherency flush control. The final per-file report should describe the repeated VF register pattern across all VFs and explain that this header is a generated bitfield contract, while behavior is implemented in AMDGPU NBIF/NBIO, ring, PCIe, SR-IOV, mailbox, and interrupt code.
