# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_7_0_sh_mask.h lines 107382-109840

## Scope

This chunk is part of the generated AMD NBIO 7.0 register shift/mask header used by the amdgpu driver. It covers PCI/PCIe configuration-space bitfield definitions for `nbio_nbif0_bif_cfg_dev0_epf2_bifcfgdecp`, all of `nbio_nbif0_bif_cfg_dev0_epf3_bifcfgdecp`, and the beginning of `nbio_nbif0_bif_cfg_dev0_epf4_bifcfgdecp`. The range starts just after `BIF_CFG_DEV0_EPF2_2_MIN_GRANT` and ends at the comment for `BIF_CFG_DEV0_EPF4_2_PCIE_BAR4_CNTL`, so EPF4 is intentionally partial in this chunk.

The file is not executable logic. It exposes `#define` constants of the form:

- `REGISTER__FIELD__SHIFT`, the bit position for a field.
- `REGISTER__FIELD_MASK`, the mask for that field in the register value.

These constants are consumed by register helpers such as `REG_SET_FIELD`, `REG_GET_FIELD`, `WREG32_SOC15`, `RREG32_SOC15`, and `WREG32_FIELD15` in amdgpu code after including the companion `nbio_7_0_offset.h`, `nbio_7_0_default.h`, and `nbio_7_0_smn.h` headers.

## Purpose

The chunk describes the NBIO 7.0 PCIe endpoint-function configuration register layout for virtual or exposed functions `DEV0_EPF2`, `DEV0_EPF3`, and part of `DEV0_EPF4`. The layout mirrors PCI conventional configuration space and PCIe extended capabilities:

- Base PCI identity, command, status, BAR, ROM, interrupt, and class-code fields.
- PCI Power Management Interface registers.
- PCIe capability registers for device, link, slot, and Gen2/Gen3-style extensions.
- MSI and MSI-X capability registers.
- SATA capability placeholders exposed through this NBIO config decode block.
- PCIe vendor-specific, AER, BAR enhanced allocation, power budget, dynamic power allocation, access control services, and alternative routing ID interpretation capability registers.

The definitions let driver code read, update, or decode hardware state without hard-coding bit positions. The masks also act as a local hardware contract: if a field moves in a future ASIC revision, callers must use the revision-specific header rather than reusing this one.

## Important Definitions

The chunk is organized by repeated endpoint-function prefixes:

- `BIF_CFG_DEV0_EPF2_2_*`: completes EPF2 from `MAX_LATENCY` through `PCIE_ARI_CNTL`.
- `BIF_CFG_DEV0_EPF3_2_*`: full EPF3 config block from `VENDOR_ID` through `PCIE_ARI_CNTL`.
- `BIF_CFG_DEV0_EPF4_2_*`: partial EPF4 config block from `VENDOR_ID` through the beginning of BAR enhanced allocation (`PCIE_BAR4_CNTL` comment at the range end).

Key register groups in each complete EPF block:

- PCI command/status: `COMMAND` includes I/O, memory, bus master, special cycle, memory-write-invalidate, VGA palette snoop, parity/error-response, SERR, fast back-to-back, interrupt disable, and atomic-operation requester controls. `STATUS` covers interrupt status, capability-list presence, frequency, fast-back-to-back, parity, devsel timing, target/master aborts, signaled system error, parity error, and atomic-op egress-blocked status.
- Identification and BAR layout: `VENDOR_ID`, `DEVICE_ID`, `REVISION_ID`, `PROG_INTERFACE`, `SUB_CLASS`, `BASE_CLASS`, `HEADER`, `BIST`, `BASE_ADDR_1` through `BASE_ADDR_6`, `ADAPTER_ID`, `ROM_BASE_ADDR`, `CAP_PTR`, `INTERRUPT_LINE`, and `INTERRUPT_PIN`.
- Power management: `PMI_CAP_LIST`, `PMI_CAP`, and `PMI_STATUS_CNTL` expose capability chaining, PME support, power state, PME enable/status, data select/scale, bus-power enable, and PMI data fields.
- PCIe core capability: `PCIE_CAP_LIST`, `PCIE_CAP`, `DEVICE_CAP`, `DEVICE_CNTL`, `DEVICE_STATUS`, `LINK_CAP`, `LINK_CNTL`, and `LINK_STATUS`.
- PCIe second-generation capability: `DEVICE_CAP2`, `DEVICE_CNTL2`, `DEVICE_STATUS2`, `LINK_CAP2`, `LINK_CNTL2`, `LINK_STATUS2`, `SLOT_CAP2`, `SLOT_CNTL2`, and `SLOT_STATUS2`.
- Interrupt capability: `MSI_CAP_LIST`, `MSI_MSG_CNTL`, `MSI_MSG_ADDR_LO`, `MSI_MSG_ADDR_HI`, `MSI_MSG_DATA`, `MSI_MASK`, 64-bit MSI variants, pending bits, `MSIX_CAP_LIST`, `MSIX_MSG_CNTL`, `MSIX_TABLE`, and `MSIX_PBA`.
- PCIe AER: `PCIE_ADV_ERR_RPT_ENH_CAP_LIST`, `PCIE_UNCORR_ERR_STATUS`, `PCIE_UNCORR_ERR_MASK`, `PCIE_UNCORR_ERR_SEVERITY`, `PCIE_CORR_ERR_STATUS`, `PCIE_CORR_ERR_MASK`, `PCIE_ADV_ERR_CAP_CNTL`, `PCIE_HDR_LOG0..3`, and `PCIE_TLP_PREFIX_LOG0..3`.
- Resource and power extended capabilities: `PCIE_BAR_ENH_CAP_LIST`, `PCIE_BAR{1..6}_CAP`, `PCIE_BAR{1..6}_CNTL`, `PCIE_PWR_BUDGET_ENH_CAP_LIST`, `PCIE_PWR_BUDGET_DATA_SELECT`, `PCIE_PWR_BUDGET_DATA`, `PCIE_PWR_BUDGET_CAP`, `PCIE_DPA_ENH_CAP_LIST`, `PCIE_DPA_CAP`, `PCIE_DPA_LATENCY_INDICATOR`, `PCIE_DPA_STATUS`, `PCIE_DPA_CNTL`, and `PCIE_DPA_SUBSTATE_PWR_ALLOC_0..7`.
- Isolation and routing: `PCIE_ACS_ENH_CAP_LIST`, `PCIE_ACS_CAP`, `PCIE_ACS_CNTL`, `PCIE_ARI_ENH_CAP_LIST`, `PCIE_ARI_CAP`, and `PCIE_ARI_CNTL`.

The AER uncorrectable status/mask/severity groups are among the densest groups in the range. They include data-link protocol, surprise-down, poisoned TLP, flow-control protocol, completion timeout, completer abort, unexpected completion, receiver overflow, malformed TLP, ECRC, unsupported request, ACS violation, internal error, MC blocked TLP, atomic-op egress blocked, and TLP prefix blocked bits.

## Control Flow

There is no run-time control flow inside this header. Control flow exists only in code that includes it. For NBIO 7.0, direct users include `amdgpu/nbio_v7_0.c`, `amdgpu/soc15.c`, and `pm/powerplay/hwmgr/smu10_inc.h`. Those files combine this mask header with the NBIO offset/default/SMN headers and the amdgpu register access wrappers.

The typical call pattern is:

1. Select an NBIO register offset from `nbio_7_0_offset.h` or an SMN address from `nbio_7_0_smn.h`.
2. Read a 32-bit register with an amdgpu helper.
3. Extract or modify a field using this header's `REGISTER__FIELD__SHIFT` and `REGISTER__FIELD_MASK` constants, often through `REG_GET_FIELD` or `REG_SET_FIELD`.
4. Write the updated register value back when the field is writable.

Within this chunk, the PCIe endpoint configuration fields are more likely to be decoded, exposed, or preserved than frequently written by generic driver code. Some writable classes are still important: command enables, power-management state, link controls, MSI/MSI-X enables and masks, AER masks/severity controls, BAR enhanced allocation controls, ACS controls, ARI controls, and DPA controls.

## State and Persistence

The header itself has no state and persists nothing. The state represented by these masks lives in NBIO hardware registers and PCIe configuration-space shadows. Values are hardware/firmware initialized at boot and can be changed by firmware, PCI core enumeration, amdgpu initialization, runtime power management, error handling, virtualization setup, or reset paths.

The companion default header shows the intended reset/default values for the same register names. In the complete EPF2 and EPF3 blocks, defaults include enabled PCIe capability-list pointers, FLR-capable device capability (`DEVICE_CAP` default `0x10000000`), link capability/status defaults, MSI capability defaults, AER severity/mask defaults, BAR enhanced allocation list defaults, power budget capability chaining, DPA status defaults, and ACS/ARI extended-capability defaults. This mask header should therefore be treated as the field map for persistent hardware state across reset domains, not as a configuration policy source.

## Dependencies and Integration Points

Primary dependencies:

- `nbio_7_0_offset.h` supplies MMIO register offsets for NBIO 7.0 registers.
- `nbio_7_0_smn.h` supplies SMN addresses for indirect or fabric-visible NBIO registers.
- `nbio_7_0_default.h` supplies expected hardware defaults for the same register names.
- amdgpu register helpers in the driver use the shift/mask naming convention directly.

Integration points:

- `amdgpu/nbio_v7_0.c` includes this header for NBIO 7.0 operations such as memory-controller access enable, revision-id extraction, doorbell range setup, interrupt control, HDP flush/remap offsets, and clock-gating/light-sleep control. That file demonstrates the broader usage pattern even though it does not directly manipulate every endpoint-function PCIe field in this chunk.
- `amdgpu/soc15.c` includes this header as part of SOC15 device setup, where ASIC family routing determines which IP blocks and register maps are active.
- `pm/powerplay/hwmgr/smu10_inc.h` includes this NBIO map alongside MP and THM register maps for SMU10-era power-management code.
- The kernel PCI core and platform firmware define the semantic meaning of many fields here; this header provides AMD-specific bit locations within the NBIO register decode.

## Risks

- Register-family mismatch is the primary risk. These masks are only valid for NBIO 7.0. Reusing them with NBIO 7.2, 7.4, 7.9, or later hardware can silently read or write the wrong bits.
- The range contains repeated, near-identical EPF2/EPF3/EPF4 definitions. Manual edits or generated-header drift can introduce copy/paste skew where one endpoint function no longer matches the others.
- The slice ends mid-EPF4 BAR enhanced-allocation section. Any consumer research that treats this chunk as the full EPF4 block would miss later EPF4 BAR5/BAR6, power budget, DPA, ACS, and ARI fields outside the requested line range.
- Write masks for PCI command, link control, MSI/MSI-X, AER, ACS, ARI, and DPA fields are sensitive. Incorrect use can disable memory or bus-master access, break interrupt delivery, alter error reporting, weaken isolation, or create link/power-management instability.
- Some AER status fields are write-one-to-clear in PCIe-style designs. Code using these masks must respect hardware semantics and avoid read-modify-write patterns that accidentally clear latched errors.
- BAR enhanced allocation and ACS/ARI fields affect resource routing and function isolation. Misprogramming can cause peer-to-peer access or VF/function routing behavior that conflicts with IOMMU and PCI core expectations.

## Test Signals

Useful validation signals for this chunk are mostly compile-time and hardware-observation based:

- Kernel build coverage for amdgpu with NBIO 7.0/SOC15 support ensures all macro names used by driver code still resolve.
- Static comparison against generated register specifications or adjacent NBIO revision headers can catch prefix or mask drift across repeated EPF blocks.
- Runtime PCI enumeration should still show coherent capability lists for the affected functions: PM, PCIe, MSI/MSI-X, AER, enhanced allocation, power budget, DPA, ACS, and ARI where enabled by defaults.
- `lspci -vvv` on matching hardware can verify link capability/status, MSI/MSI-X capability, AER fields, ACS/ARI presence, BAR sizing, and power-management capability state.
- AER testing should confirm correct reporting and clearing of correctable/uncorrectable errors without spurious status loss.
- Reset and suspend/resume testing should confirm that command enables, interrupt state, link state, BAR-related fields, and power-management fields return to expected defaults or driver-restored values.
- SR-IOV or multi-function tests, when applicable to the endpoint functions represented by EPF2/EPF3/EPF4, should confirm function isolation, ARI routing, ACS behavior, and interrupt delivery remain consistent.
