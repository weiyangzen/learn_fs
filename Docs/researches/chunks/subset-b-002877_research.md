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
