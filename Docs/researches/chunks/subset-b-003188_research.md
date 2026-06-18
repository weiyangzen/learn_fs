# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_7_2_0_sh_mask.h lines 68463-70923

## Scope

This chunk covers generated shift and mask macros from the AMD NBIO 7.2.0 register mask header. The line range contains 2,130 `#define` entries across 325 register-comment sections:

- The tail of `BIF_CFG_DEV2_EPF0_0`: lane 14/15 16 GT/s equalization presets, PCIe margining enhanced capability metadata, port capability/status fields, and lane 0-15 margining control/status fields.
- The full `nbio_nbif0_bif_cfg_dev2_epf1_bifcfgdecp` address block: standard PCI configuration space, PCIe capability, MSI/MSI-X, vendor-specific enhanced capability, AER, BAR enhanced capability, power budget, DPA, ACS, PASID, ARI, TPH requester, and TPH steering table fields for endpoint function 1.
- The beginning of `nbio_nbif0_bif_cfg_dev2_epf2_bifcfgdecp`: standard PCI configuration space, PCIe capability, MSI/MSI-X, vendor-specific enhanced capability, AER, BAR enhanced capability, and power budget fields for endpoint function 2.

The range ends in the middle of `BIF_CFG_DEV2_EPF2_0_PCIE_PWR_BUDGET_DATA`: it includes shifts and masks through `PM_STATE_MASK`, while the remaining `TYPE_MASK` and `POWER_RAIL_MASK` definitions continue in the next chunk. This file is generated hardware register metadata only; it defines no C functions, structs, variables, or executable control flow.

## Purpose

`nbio_7_2_0_sh_mask.h` provides the bitfield side of the NBIO 7.2.0 hardware ABI used by AMDGPU. Each field is expressed as a pair:

- `<REGISTER>__<FIELD>__SHIFT`, the low bit used when packing or unpacking a field.
- `<REGISTER>__<FIELD>_MASK`, the bit mask used to isolate or compose that field.

The companion `nbio_7_2_0_offset.h` supplies the register addresses, for example `regBIF_CFG_DEV2_EPF0_0_LANE_0_MARGINING_LANE_CNTL` at `0x14112`, `regBIF_CFG_DEV2_EPF1_0_VENDOR_ID` at `0x14400`, and `regBIF_CFG_DEV2_EPF2_0_VENDOR_ID` at `0x14800`. Driver code includes this header through `amdgpu/nbio_v7_2.c` and combines the masks with access helpers such as `REG_SET_FIELD`, `REG_GET_FIELD`, `RREG32_SOC15`, `WREG32_SOC15`, `RREG32_PCIE_PORT`, `WREG32_PCIE_PORT`, and `SOC15_REG_OFFSET`.

## Important Macro Families

### EPF0 PCIe Margining and Equalization

The first section finishes the endpoint-function-0 lane equalization and margining capability map. `BIF_CFG_DEV2_EPF0_0_LANE_14_EQUALIZATION_CNTL_16GT` and `LANE_15_EQUALIZATION_CNTL_16GT` expose four-bit downstream/upstream 16 GT/s TX preset fields. These are per-lane PCIe link-training values and must be used with the corresponding offset definitions rather than inferred from neighboring lanes.

`BIF_CFG_DEV2_EPF0_0_PCIE_MARGINING_ENH_CAP_LIST` contains the standard enhanced capability list fields: `CAP_ID`, `CAP_VER`, and `NEXT_PTR`. `MARGINING_PORT_CAP` and `MARGINING_PORT_STATUS` define software-managed margining capability and readiness bits.

`BIF_CFG_DEV2_EPF0_0_LANE_0_MARGINING_LANE_CNTL` through `LANE_15_MARGINING_LANE_STATUS` are a regular 16-lane register family. Each control register has `RECEIVER_NUMBER`, `MARGIN_TYPE`, `USAGE_MODEL`, and `MARGIN_PAYLOAD`; each status register mirrors those as `*_STATUS` fields. In the offset header, lane control and status names for a lane point at the same register address, so users must treat writes and reads as different interpretations of one hardware mailbox-style location.

### EPF1 Standard PCI Configuration Space

The EPF1 block starts at the `nbio_nbif0_bif_cfg_dev2_epf1_bifcfgdecp` address block and describes endpoint-function-1 PCI config-space fields. It includes identity and class registers (`VENDOR_ID`, `DEVICE_ID`, `REVISION_ID`, `PROG_INTERFACE`, `SUB_CLASS`, `BASE_CLASS`), command/status registers, cache-line/latency/header/BIST registers, six base address registers, CardBus CIS pointer, adapter ID, ROM base address, capability pointer, interrupt line/pin, and min/max latency fields.

The command/status fields are the normal PCI control and observation surface: IO and memory access enable, bus mastering, parity/SERR handling, interrupt disable, capability-list presence, interrupt status, abort/error reporting, and DEVSEL timing. These definitions are low-level ABI constants; policy about enabling bus mastering, memory decoding, or interrupts belongs to PCI core or AMDGPU code using the fields.

### Power Management and PCIe Capability Registers

EPF1 and EPF2 both include PMI capability list, power-management capability, and power-management status/control fields. These macros describe version, PME clock/support, D-state support, PME enable/status, data select/scale, and no-soft-reset behavior.

The PCIe capability families cover `PCIE_CAP`, `DEVICE_CAP`, `DEVICE_CNTL`, `DEVICE_STATUS`, `LINK_CAP`, `LINK_CNTL`, `LINK_STATUS`, `DEVICE_CAP2`, `DEVICE_CNTL2`, `DEVICE_STATUS2`, `LINK_CAP2`, `LINK_CNTL2`, and `LINK_STATUS2`. Important fields include payload and read-request sizing, phantom functions, extended tags, relaxed ordering, no-snoop, AUX/current reporting, link speed and width, ASPM/power-management controls, retrain/link-disable controls, link training and data-link-active status, completion timeout policy, ARI, atomic operations, ID-based ordering, LTR, OBFF, end-to-end TLP prefix handling, equalization status, crosslink resolution, and downstream component presence.

These are the fields most likely to be read during device capability discovery or changed during low-level link/power tuning. The macros do not encode reset defaults or access permissions; callers must preserve reserved bits and respect PCIe spec semantics.

### MSI, MSI-X, and Interrupt Data

The `MSI_*` and `MSIX_*` sections map capability headers, control registers, message addresses, message data, masks, pending bits, MSI-X table metadata, and MSI-X PBA metadata. EPF1 contains the full family; EPF2 contains the same family within the covered partial block.

The field names distinguish 32-bit and 64-bit MSI layouts (`MSI_MSG_DATA` versus `MSI_MSG_DATA_64`, `MSI_MASK` versus `MSI_MASK_64`, and pending variants). Code using these definitions must select the correct layout based on the capability-control bits rather than writing all possible aliases.

### Vendor-Specific and Advanced Error Reporting

The PCIe vendor-specific enhanced capability list and header fields expose enhanced capability ID/version/next pointer, VSEC ID/revision/length, and vendor-specific data words.

The AER section is extensive for both EPF1 and EPF2. It defines uncorrectable error status, mask, and severity fields for DLP, surprise down, poisoned TLP, flow control, completion timeout/abort, unexpected completion, receiver overflow, malformed TLP, ECRC, unsupported request, ACS violation, internal error, MC blocked TLP, atomic-op egress blocking, TLP prefix blocking, and poisoned-TLP egress blocking. Correctable error status/mask fields cover receiver errors, bad TLP/DLLP, replay rollover, replay timer timeout, advisory nonfatal errors, internal correctable errors, and header-log overflow. `PCIE_ADV_ERR_CAP_CNTL` adds first-error pointer, ECRC capability/enable, multi-header receive capability/enable, TLP prefix log present, and completion-timeout log capability.

Header log and TLP prefix log registers (`PCIE_HDR_LOG0-3`, `PCIE_TLP_PREFIX_LOG0-3`) are full-width 32-bit capture fields. Their contents are diagnostic state produced by hardware after errors, not persistent driver configuration.

### BAR, Power Budget, DPA, ACS, PASID, ARI, and TPH

The BAR enhanced capability families define capability list metadata plus `PCIE_BAR1_CAP` through `PCIE_BAR6_CAP` and matching `PCIE_BAR*_CNTL` fields. The capability registers expose supported BAR sizes; the control registers expose selected BAR index, total number, active size, and upper supported-size bits.

Power budget fields include enhanced capability list metadata, `DATA_SELECT`, and `PCIE_PWR_BUDGET_DATA` fields for base power, data scale, PM sub-state, PM state, type, and power rail. In this chunk, EPF1 has the complete data field map, while EPF2 stops before the last two masks.

EPF1 additionally covers Dynamic Power Allocation (`PCIE_DPA_*` capability, latency indicator, status, control, and eight substate power-allocation registers), ACS capability/control bits, PASID capability/control bits, ARI capability/control bits, and TPH requester capability/control. The TPH steering table is represented by `PCIE_TPH_ST_TABLE_0` through `PCIE_TPH_ST_TABLE_63`, each with `ST_LOWER` and `ST_UPPER` two-byte fields.

## Control Flow

There is no runtime control flow in this header chunk. The generated comments partition the macro stream by hardware register. At compile time, C preprocessor expansion feeds these masks into helper macros. At runtime, the actual flow is in callers such as `nbio_v7_2.c`: code reads a register by offset, uses field masks/shifts to update or inspect selected bits, and writes the composed value back when needed.

The important operational sequence for this chunk is therefore external:

1. Select the correct register offset from `nbio_7_2_0_offset.h` for EPF0, EPF1, or EPF2.
2. Read the register through the appropriate MMIO, SOC15, PCIE port, or PCI config accessor.
3. Apply the matching `BIF_CFG_DEV2_EPF*_0_*` shift/mask pair from this header.
4. Preserve unrelated bits unless the hardware register explicitly defines write-one-to-clear or command semantics.

## State and Persistence

The macros are compile-time constants and have no storage. The state they describe lives in NBIO/PCIe hardware registers. Some fields are durable configuration while the device remains powered, such as command enables, link controls, power-management enables, MSI/MSI-X control bits, AER masks/severity, ACS/PASID/ARI controls, BAR sizing controls, and TPH steering entries.

Other fields are hardware-observed or diagnostic state: PCI/PCIe status bits, link status, equalization status, DPA status, AER status bits, header logs, TLP prefix logs, and margining status. Those fields can change asynchronously due to link training, PCIe errors, firmware actions, power transitions, or host PCI core configuration.

The lane margining control/status aliases require extra care because control and status macros share register addresses in the offset header. Software should not assume normal independent read/write storage for these names.

## Dependencies and Integration Points

- `amdgpu/nbio_v7_2.c` includes this header with `nbio_7_2_0_offset.h` and provides the NBIO 7.2 function table for revision ID reads, memory-controller access, doorbell ranges, interrupt handling, clock-gating/light-sleep controls, register initialization, HDP flush register offsets, and PCIe index/data offsets.
- `amdgpu.h`, SOC15 register helpers, and PCIe port access helpers provide the actual read/write mechanism. This header only supplies bit positions.
- `nbio_7_2_0_offset.h` is mandatory for correct address selection. The same field layout appears under several endpoint functions and instances, but their register addresses differ (`EPF0_0` around `0x14000`, `EPF1_0` around `0x14400`, `EPF2_0` around `0x14800`).
- PCI core, firmware, SMU/power management, AER handling, and interrupt setup can all interact with the hardware state represented here. The header does not arbitrate ownership.

## Risks

- Off-by-one or family-copy mistakes are easy because EPF1 and EPF2 fields are nearly identical but address bases differ.
- The chunk boundary cuts through `BIF_CFG_DEV2_EPF2_0_PCIE_PWR_BUDGET_DATA`; merged research should combine the next chunk before treating that register as fully covered.
- Many status/AER fields have hardware-specific write-clear or sticky behavior. A generic read-modify-write using masks can accidentally clear diagnostics or change severity/mask policy if the caller does not understand the register access semantics.
- PCIe link-control, completion-timeout, atomic-operation, ACS, PASID, ARI, and TPH fields affect system interoperability and IOMMU/virtualization behavior. Changing them outside established PCI/AMDGPU flows can break enumeration, DMA routing, error handling, or peer-to-peer behavior.
- Margining and equalization fields are per-lane and link-speed-specific. Incorrect writes can destabilize PCIe training or make diagnostics misleading.

## Test Signals

Useful validation signals for changes touching this header or users of these macros include:

- Build coverage for AMDGPU with NBIO 7.2 enabled, catching missing or misspelled generated macro names.
- Boot and PCI enumeration logs on NBIO 7.2 hardware, confirming EPF1/EPF2 functions expose expected PCI capabilities and BARs.
- `lspci -vv` or kernel PCI capability dumps showing stable MSI/MSI-X, PCIe capability, AER, ACS, PASID, ARI, power-budget, and TPH capability decoding.
- Runtime checks for AER logs, link status, negotiated speed/width, and absence of unexpected link retraining after register changes.
- AMDGPU smoke tests around doorbells, interrupts, HDP flush, suspend/resume, reset, and memory access, because `nbio_v7_2.c` is the main in-tree consumer of the NBIO 7.2 mask/offset headers.
- Hardware margining/equalization diagnostics, where available, to confirm lane control/status aliases and per-lane payload fields are interpreted correctly.
