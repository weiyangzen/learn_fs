# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_7_11_0_sh_mask.h lines 4902-7362

## Purpose

This chunk is part of AMDGPU's generated NBIO 7.11.0 shift/mask header. It defines C preprocessor constants for bit positions and masks in NBIO/NBIF PCI configuration-space registers. The range starts in the tail of the `BIF_CFG_DEV2_RC` root-complex PCIe margining area, then covers most of the `nbio_nbif0_bif_cfg_dev0_epf0_bifcfgdecp` address block and the beginning of the matching `DEV0_EPF1` block.

The content is hardware metadata, not executable driver code. AMDGPU code pairs these `*_SHIFT` and `*_MASK` macros with register offsets from the companion NBIO 7.11.0 offset header and with common register-field helpers to encode and decode PCIe configuration fields without embedding literal bit positions.

## Important APIs, Types, and Macros

There are no functions, structs, typedefs, or enums in this line range. The exported interface is the generated macro convention:

- `<REGISTER>__<FIELD>__SHIFT`: the field's starting bit.
- `<REGISTER>__<FIELD>_MASK`: the field mask already shifted into register position.

Major register families in this chunk are:

- `BIF_CFG_DEV2_RC_LANE_11_MARGINING_LANE_*` through `LANE_15_MARGINING_LANE_*`: root-complex receiver margining control/status fields for PCIe lanes 11-15. Each lane repeats receiver number, margin type, usage model, and payload fields.
- `BIF_CFG_DEV2_RC_PCIE_RTR_ENH_CAP_LIST`, `BIF_CFG_DEV2_RC_RTR_DATA1`, and `BIF_CFG_DEV2_RC_RTR_DATA2`: Readiness Time Reporting enhanced capability metadata and timing fields for reset, data-link-up, FLR, D3hot-to-D0, plus a valid bit.
- `BIF_CFG_DEV0_EPF0_*` conventional PCI header fields: vendor/device ID, command/status, revision/class code, cache line, latency, header/BIST, six base address registers, subsystem IDs, ROM BAR, capability pointer, interrupt line/pin, and legacy min-grant/max-latency fields.
- `BIF_CFG_DEV0_EPF0_PMI_*`: power-management capability list, capability flags, power state, PME enable/status, data select/scale, bus power, and power-management data fields.
- `BIF_CFG_DEV0_EPF0_PCIE_*` core PCIe capability fields: PCIe capability list/header, device capability/control/status, link capability/control/status, PCIe 2.0 device/link capability/control/status fields, completion timeout, ARI/atomic operation support, IDO, LTR, OBFF, emergency power reduction, DRS, equalization, and target link speed controls.
- `BIF_CFG_DEV0_EPF0_MSI*` and `MSIX*`: MSI/MSI-X capability list, message-control bits, 32/64-bit message address/data registers, mask/pending registers, MSI-X table and PBA BAR/index fields.
- `BIF_CFG_DEV0_EPF0_PCIE_VENDOR_SPECIFIC*`, `PCIE_VC*`, and `PCIE_DEV_SERIAL_NUM*`: vendor-specific enhanced capability fields, virtual-channel capabilities/resources/status, and device serial number dwords.
- `BIF_CFG_DEV0_EPF0_PCIE_ADV_ERR_RPT*`: PCIe Advanced Error Reporting capability, including uncorrectable error status/mask/severity, correctable error status/mask, ECRC controls, first error pointer, TLP header logs, and TLP prefix logs.
- `BIF_CFG_DEV0_EPF0_PCIE_BAR*` and `PCIE_VF_RESIZE_BAR*`: resizable BAR capability/control fields for PF BARs and VF BARs, with repeated bar index, total count, current size, and supported-size upper fields.
- `BIF_CFG_DEV0_EPF0_PCIE_PWR_BUDGET*` and `PCIE_DPA*`: power-budgeting and dynamic power allocation capability fields, including data select, base power, scale, PM state/substate, power rail, DPA substate count/control/status, transition latency indicators, and per-substate power allocations 0-7.
- `BIF_CFG_DEV0_EPF0_PCIE_SECONDARY*`, lane equalization, and 16GT PHY capability fields: link control 3, lane error status, 8GT lane equalization controls for lanes 0-15, 16GT equalization status, parity mismatch status, and 16GT lane preset controls for lanes 0-15.
- `BIF_CFG_DEV0_EPF0_PCIE_ACS*`, `ATS*`, `PAGE_REQ*`, `PASID*`, `MC*`, `LTR*`, `ARI*`, and `SRIOV*`: access control services, address translation services, page request interface, PASID, multicast, latency tolerance reporting, ARI, and SR-IOV capability/control/status surfaces.
- `BIF_CFG_DEV0_EPF0_DATA_LINK_FEATURE_*` and `PCIE_MARGINING*`: data-link feature capability/status and PCIe lane margining port/lane control/status for lanes 0-15.
- `PCIE_VENDOR_SPECIFIC_ENH_CAP_LIST_GPUIOV`: GPU IOV vendor-specific enhanced capability list fields, with capability ID/version/next pointer.
- `BIF_CFG_DEV0_EPF1_*`: the start of endpoint function 1's PCI configuration-space mask set. This chunk covers the same conventional PCI header, power-management, PCIe device/link capability/control/status, PCIe 2.0 device/link fields, and stops after `BIF_CFG_DEV0_EPF1_LINK_STATUS2`.

These macros are intended for use through AMDGPU register helpers such as `REG_GET_FIELD`, `REG_SET_FIELD`, and SOC15/NBIO register read-write paths. Register address definitions are not in this file; this header only describes field geometry.

## Control Flow and Runtime Behavior

This chunk has no runtime control flow. It is included by C sources at compile time and contributes constants to hardware register read, write, and read-modify-write operations.

The implied hardware flows are:

1. PCI enumeration or driver initialization can read conventional header fields for identity, class code, BAR layout, ROM BAR state, interrupt routing, and capability list traversal for `DEV0_EPF0` and `DEV0_EPF1`.
2. PCI command/status and PCIe device-control fields gate I/O, memory access, bus mastering, interrupt disable, error reporting enables, relaxed ordering, no-snoop, maximum payload size, maximum read request size, and function-level reset initiation.
3. Link capability/control/status fields report and control negotiated speed/width, link training, retraining, common clock, ASPM/clock power management, link bandwidth interrupts, target link speed, compliance entry, de-emphasis, equalization, DRS, crosslink, and downstream component presence.
4. MSI/MSI-X masks define interrupt capability programming surfaces: message count/enable, 64-bit capability, per-vector masking, message address/data, MSI-X table location, and pending-bit-array location.
5. AER fields let driver or firmware code classify PCIe corrected and uncorrected errors, mask selected events, configure severity, enable/check ECRC, and read logged TLP headers/prefixes after errors.
6. Resizable BAR and SR-IOV fields describe how PF and VF address windows, VF counts, VF stride, VF device ID, page sizes, and VF memory-space enable are exposed to PCIe software.
7. ACS, ATS, page request, PASID, ARI, multicast, LTR, data-link feature, DPA, and power-budget fields expose advanced PCIe capabilities that interact with IOMMU, virtualization, power management, and traffic-routing code.
8. Lane equalization and lane margining fields provide per-lane diagnostics and tuning surfaces for 8GT, 16GT, and PCIe receiver margining flows. Software writes lane control fields and reads status/error/parity indicators, but the timing and state machine behavior are in hardware.

The header does not sequence these operations, clear status bits, or enforce PCIe ordering rules. Callers must follow PCIe and ASIC-specific programming requirements when using the generated masks.

## State and Persistence

The header owns no memory, stores no runtime state, performs no I/O, and persists nothing. The represented state lives in NBIO/NBIF hardware registers.

State categories represented here include:

- PCI configuration identity and layout state: IDs, class codes, BARs, ROM BAR, subsystem IDs, capability pointers, interrupt line/pin, MSI/MSI-X table/PBA pointers, and SR-IOV VF BARs.
- PCI command and control policy: memory/bus-master enables, interrupt disable, PME enable/status, power state, error reporting enables, FLR initiation, completion timeout policy, atomic operation controls, IDO, LTR, OBFF, ARI forwarding, VF enable, and VF memory-space enable.
- PCIe link state: supported/current speeds and widths, link training, DL active, target speed, retrain/link-disable controls, common clock, bandwidth notification, compliance controls, equalization completion and phase status, 16GT parity mismatch, and per-lane equalization presets.
- Error reporting state: conventional PCI status bits, PCIe device status, AER corrected/uncorrected status/mask/severity, ECRC and multi-header logging controls, TLP header logs, TLP prefix logs, and lane error status.
- Power and virtualization capability state: power-budget records, DPA controls/status/substate allocations, LTR latency limits, PASID/page request/ATS state, multicast registers, ACS controls, ARI controls, SR-IOV VF counts/offset/stride/page sizes, and data-link feature negotiation.
- Lane diagnostics state: PCIe margining port ready/software-ready bits and per-lane margining control/status payloads for DEV2 root-complex lanes 11-15 and DEV0 EPF0 lanes 0-15.

Retention across GPU reset, PCI reset, FLR, suspend/resume, runtime power transitions, BACO, or hot reset is not specified by this header. Those semantics are defined by NBIO 7.11.0 hardware and by any AMDGPU initialization paths that restore configuration after reset or resume.

## Dependencies and Integration Points

Primary dependencies are adjacent generated NBIO 7.11.0 headers:

- `nbio_7_11_0_offset.h` for the register offsets matching these register names.
- Other generated ASIC-family headers included by AMDGPU SOC15/NBIO code for register access conventions and related blocks.

Likely integration areas in the AMDGPU tree include:

- NBIO 7.11 setup and low-level register access paths that include generated NBIO masks.
- PCIe and NBIF initialization code that programs device/link capabilities, BAR sizing, power management, MSI/MSI-X, and link controls.
- AMDGPU virtualization/SR-IOV code that uses VF counts, VF stride, VF BARs, ARI, ATS, PASID, page-request, ACS, and VF enable/memory-space fields.
- Error-handling and RAS-adjacent PCIe code that reads PCI status, PCIe device status, AER status/mask/severity, TLP logs, lane error status, and parity/equalization diagnostics.
- Link training, speed-change, equalization, and hardware validation code that consumes 8GT/16GT equalization and margining controls.
- Power-management code that reads or programs PCI PM capability, LTR, DPA, power-budgeting, OBFF, clock power management, and emergency power reduction fields.

Integration is symbol-name based. A caller must pair a field macro from this file with the correct register address macro and with PCIe/NBIO documentation for field value meanings.

## Risks

- Incorrect shifts or masks can silently program the wrong PCIe control bit or misdecode status. In this range, that can affect bus mastering, memory decode, FLR, interrupt masking, link training, power management, AER classification, virtualization, or BAR sizing.
- The header is highly repetitive across lanes, BARs, VF BARs, and endpoint functions. Generator or copy/paste mistakes can be hard to detect if validation covers only lane 0, BAR1, or EPF0.
- Several fields can disrupt device operation when written incorrectly: `BUS_MASTER_EN`, `MEM_ACCESS_EN`, `INITIATE_FLR`, `LINK_DIS`, `RETRAIN_LINK`, `TARGET_LINK_SPEED`, `ENTER_COMPLIANCE`, SR-IOV VF enable/MSE, MSI/MSI-X enable/masks, and AER masks/severity.
- AER status, mask, and severity names are intentionally similar. Mixing them can hide real PCIe faults, over-report benign faults, or misclassify fatal/nonfatal/corrected errors.
- BAR and resizable-BAR masks are full-width or size-encoded. Wrong size/index handling can expose invalid MMIO apertures or break PF/VF address layout.
- SR-IOV, ATS, PASID, page request, ACS, and ARI controls intersect with IOMMU and virtualization security. Misprogramming can break isolation or device assignment.
- Lane equalization and margining fields are per-lane hardware diagnostics. Incorrect lane indexes or payload encoding can make link-quality data misleading or destabilize validation flows.
- This chunk starts mid-register-family: the first `BIF_CFG_DEV2_RC_LANE_11_MARGINING_LANE_CNTL` comment and some context are in the previous chunk. It also ends immediately before `BIF_CFG_DEV0_EPF1_MSI_CAP_LIST`, so EPF1 interrupt and later capability masks are owned by the next chunk.

## Test and Validation Signals

Useful validation signals are generated-header consistency checks plus PCIe hardware coverage:

- Build AMDGPU configurations that include NBIO 7.11.0 generated headers to catch missing or malformed macros.
- Mechanically verify that complete registers in lines 4902-7362 have paired `__SHIFT` and `_MASK` definitions, allowing the intentional chunk split at the first DEV2 lane 11 control register and after EPF1 `LINK_STATUS2`.
- Cross-check register names against `nbio_7_11_0_offset.h` so every mask set used by code has a matching address definition.
- Run symmetry checks across repeated families: lane margining lanes 0-15, 8GT and 16GT lane equalization lanes 0-15, BAR1-BAR6, VF resize BAR1-BAR6, and matching EPF0/EPF1 conventional PCIe fields.
- Validate PCIe enumeration and configuration on NBIO 7.11.0 ASICs by confirming vendor/device IDs, class code, BAR sizing, capability traversal, MSI/MSI-X setup, and PCIe link status decode.
- Exercise link speed changes, retraining, equalization status, and margining diagnostics on real hardware or bring-up benches and compare decoded values against PCIe analyzer or platform firmware observations.
- Exercise AER by injecting or observing controlled corrected/nonfatal/fatal events and checking status, masks, severity, ECRC controls, and TLP log decode.
- Validate SR-IOV and IOMMU-related paths by enabling VFs, checking VF counts/stride/BAR/page-size fields, and verifying ATS/PASID/PRI/ACS/ARI behavior under device assignment.
- Run suspend/resume, FLR, hot reset, and runtime power-management coverage to confirm driver initialization restores policy registers and decodes retained status according to hardware expectations.

## Chunk Boundary Notes

The range begins inside the DEV2 root-complex margining register family. The lane 11 control register starts in this chunk, but the prior lane 10 family and the comment for the chunk transition are in the previous work item.

The range ends after `BIF_CFG_DEV0_EPF1_LINK_STATUS2` masks and immediately before `BIF_CFG_DEV0_EPF1_MSI_CAP_LIST`. Merge/reconciliation should combine this with adjacent chunks to produce the final source-file report and avoid treating the boundary as a missing EPF1 MSI section.
