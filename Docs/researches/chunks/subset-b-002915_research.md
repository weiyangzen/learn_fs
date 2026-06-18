# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_2_3_sh_mask.h lines 26850-29340

## Purpose

This chunk is part of the generated AMD NBIO 2.3 shift/mask register header. It does not define executable control flow; it defines C preprocessor constants that describe bit positions and bit masks for PCI/PCIe configuration-space registers exposed by the Navi-era NBIO/NBIF block. The paired `nbio_2_3_offset.h` file supplies register addresses, while this file supplies the field layout used by `REG_SET_FIELD`, `REG_GET_FIELD`, direct mask operations, and `WREG32_FIELD15`/`RREG32_SOC15` style AMDGPU register accessors.

The selected lines cover the end of endpoint function 2 (`EPF2`) PCIe extended-capability fields, all of endpoint function 3 (`EPF3`) configuration and PCIe capability fields, and the beginning of virtual function 0 (`EPF0_VF0`) configuration and PCIe capability fields. The last few lines enter the `EPF0_VF1` block but only include its vendor/device ID fields before the chunk boundary.

## Register Families Covered

- `BIF_CFG_DEV0_EPF2_PCIE_DPA_*`: Dynamic Power Allocation latency, status, control, and eight substate power allocation masks. These fields expose DPA substate selection and power allocation values for the previous EPF2 extended-capability block.
- `BIF_CFG_DEV0_EPF2_PCIE_ACS_*`: Access Control Services capability/control masks for source validation, translation blocking, peer-to-peer request/completion redirect, upstream forwarding, peer egress control, direct translated peer-to-peer, and egress vector size.
- `BIF_CFG_DEV0_EPF2_PCIE_PASID_*`: PASID enhanced-capability, capability, and control fields. These describe PASID enablement, execute-permission support, privileged-mode support, and maximum PASID width.
- `BIF_CFG_DEV0_EPF2_PCIE_ARI_*`: Alternative Routing-ID Interpretation capability/control fields for function-group handling and next-function numbering.
- `BIF_CFG_DEV0_EPF2_PCIE_TPH_REQR_*` and `BIF_CFG_DEV0_EPF2_PCIE_TPH_ST_TABLE_0..63`: TPH requester capability/control fields and steering-tag table entries. Each table register has lower and upper 8-bit ST entries.
- `addressBlock: nbio_nbif0_bif_cfg_dev0_epf3_bifcfgdecp`: A complete PCI configuration-space-like view for endpoint function 3, from vendor/device IDs through base address registers, PCI PM capability, PCIe capability, MSI/MSI-X, SATA, vendor-specific extended capabilities, AER, BAR sizing, power budget, DPA, ACS, PASID, ARI, TPH, and TPH steering table entries.
- `addressBlock: nbio_nbif0_bif_cfg_dev0_epf0_vf0_bifcfgdecp`: The beginning and most of the PCIe extended capability view for virtual function 0. It includes standard config header fields, PCIe device/link capabilities, MSI/MSI-X, vendor-specific capability, AER status/mask/severity/logging, ATS capability/control, and ARI capability/control.
- `addressBlock: nbio_nbif0_bif_cfg_dev0_epf0_vf1_bifcfgdecp`: The chunk only reaches `VF1_VENDOR_ID` and `VF1_DEVICE_ID`; VF1 command/status and later fields continue in the following chunk.

## Important APIs, Types, and Constants

This header contributes constants, not callable APIs or C types. The important contract is naming and layout:

- Field shift constants follow `<REGISTER>__<FIELD>__SHIFT`.
- Field mask constants follow `<REGISTER>__<FIELD>_MASK`.
- Register scopes encode hardware function identity: `EPF2`, `EPF3`, `EPF0_VF0`, and `EPF0_VF1`.
- Extended-capability list registers consistently expose `CAP_ID`, `CAP_VER`, and `NEXT_PTR` fields at bit ranges 0-15, 16-19, and 20-31.
- Repeated PCI capability groups retain PCIe-defined field naming, making them compatible with generic helper macros and with code that mirrors PCI/PCIe spec terminology.

Consumers include:

- `drivers/gpu/drm/amd/amdgpu/nbio_v2_3.c`, which includes `nbio_2_3_offset.h` and `nbio_2_3_sh_mask.h` for NBIO initialization, doorbell aperture setup, interrupt handling, clock gating, ASPM/LTR programming, and link-width handling.
- `drivers/gpu/drm/amd/amdgpu/mxgpu_nv.c`, which includes this header for SR-IOV/MxGPU mailbox and virtualized Navi GPU support.
- `drivers/gpu/drm/amd/pm/swsmu/smu11/navi10_ppt.c` and `sienna_cichlid_ppt.c`, which include the same offset/mask pair for SMU power-management code that reads PCIe/NBIO strap and link-related state.

## Control Flow

There is no runtime control flow in this chunk. The effective control flow appears in call sites that:

1. Select a register address from `nbio_2_3_offset.h` or an SMN/mmio literal.
2. Read the register via accessors such as `RREG32_SOC15`, `RREG32_PCIE`, or `RREG32`.
3. Extract or update fields using this header's `__SHIFT` and `_MASK` constants, commonly through `REG_SET_FIELD`, direct `& mask`, and `>> shift`.
4. Write changed values back through `WREG32_SOC15`, `WREG32_PCIE`, `WREG32`, or field-specific helpers.

For this exact range, most names represent PCI configuration capability state rather than the core NBIO doorbell and clock-gating registers used heavily in `nbio_v2_3.c`. The pattern is still the same: the constants are compile-time field descriptions for hardware register transactions performed elsewhere.

## State and Persistence Behavior

The file itself has no state and persists nothing. The constants describe hardware-backed state in PCIe configuration and NBIO register space:

- Capability and identity registers, such as vendor/device/class/header/capability-list fields, generally reflect strap, firmware, or hardware configuration.
- Control registers, such as `COMMAND`, `DEVICE_CNTL`, `LINK_CNTL`, `MSI_MSG_CNTL`, `MSIX_MSG_CNTL`, ACS/PASID/ARI/TPH controls, ATS control, and DPA control, may be programmed by firmware, host PCI configuration logic, the kernel PCI core, or AMDGPU.
- Error-status and logging registers, especially AER uncorrectable/correctable status, masks, severity, header logs, and TLP prefix logs, reflect live PCIe error state and may be sticky until cleared according to hardware semantics.
- VF register blocks expose virtual function configuration-space state. In SR-IOV environments, reads or writes may be mediated by the PF/hypervisor; `nbio_v2_3_get_rev_id()` in nearby code explicitly treats some guest reads as unreliable and substitutes defaults.

Persistence is therefore hardware/firmware-defined across reset domains. Driver writes are not persistent across full device reset unless replayed during initialization or restored by PCI/firmware paths.

## Dependencies and Integration Points

- Depends on AMDGPU register-access infrastructure (`RREG32*`, `WREG32*`, `SOC15_REG_OFFSET`, `REG_SET_FIELD`, `REG_GET_FIELD`) to make these constants useful.
- Depends on `nbio_2_3_offset.h` for the address half of the register contract. Shift/mask constants without matching offsets are not enough to access hardware.
- Integrates with Linux PCI/PCIe concepts: PCI command/status, BARs, MSI/MSI-X, PM capability, PCIe device/link capability and control, AER, ACS, PASID, ARI, ATS, TPH, DPA, and power-budgeting.
- Integrates with SR-IOV through the `EPF0_VF*` register blocks and with MxGPU/Navi virtualization code in `mxgpu_nv.c`.
- Integrates with SMU power-management code through shared NBIO/PCIe strap and link state, even though the specific EPF3/VF0 extended capability fields in this chunk are not directly referenced by a narrow textual search outside generated headers.

## Risks and Maintenance Notes

- The header is generated and very large. Manual edits are high risk because a one-bit shift or mask typo silently changes hardware programming semantics.
- Naming collisions are avoided by long register prefixes. Any rename must be coordinated with generated offset headers and all macro consumers.
- Several repeated capability blocks are structurally similar across EPF2, EPF3, and VF blocks. Copy/paste or generator errors can be hard to spot because the values look plausible.
- AER masks and severity fields directly affect error visibility and classification. Incorrect values could hide PCIe faults, over-report nonfatal faults, or mis-handle fatal conditions.
- ACS/PASID/ATS/ARI fields affect isolation, address translation, and SR-IOV behavior. Bad masks here can create functional regressions in IOMMU, peer-to-peer, or virtualized-device paths.
- TPH steering table fields are repeated 64 times for EPF2 and EPF3. Off-by-one generation mistakes would not necessarily be caught by compilation because each macro remains syntactically valid.
- The chunk boundary splits register families: EPF2 power budget/DPA begins in the prior chunk, and EPF0_VF1 continues in the next chunk. File-level reconciliation should merge adjacent chunk context before drawing final conclusions.

## Test and Validation Signals

- Build coverage: any syntax break or missing macro used by C code should be caught by compiling AMDGPU with Navi/NBIO 2.3 support enabled.
- Include coverage: `nbio_v2_3.c`, `mxgpu_nv.c`, `navi10_ppt.c`, and `sienna_cichlid_ppt.c` should still compile with this header and its paired offset header.
- Runtime smoke signals: successful AMDGPU probe on affected Navi/NBIO 2.3 hardware, correct PCIe link reporting, working MSI/MSI-X interrupt delivery, and no unexpected AER storms in `dmesg`.
- SR-IOV validation: VF bring-up, mailbox communication, guest probe, and VF reset/recovery paths should remain stable because this chunk describes VF0 and starts VF1 config-space fields.
- PCIe capability validation: `lspci -vv` or kernel PCI capability dumps should show coherent ACS, PASID, ARI, ATS, AER, MSI/MSI-X, and link capability/control state when those capabilities are exposed.
- Power-management validation: ASPM/LTR, PCIe DPM, and SMU power-state transitions should not regress on Navi10/Sienna Cichlid paths that include this NBIO header.
