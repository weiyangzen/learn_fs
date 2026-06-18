# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_7_7_0_offset.h lines 26646-29000

## Scope

This chunk is part of the generated AMDGPU NBIO 7.7.0 register offset header. It covers a PCIe configuration-space macro range from `regBIF_CFG_DEV0_EPF2_1_PCIE_VENDOR_SPECIFIC2` at line 26646 through `regBIF_CFG_DEV2_EPF0_1_PCIE_LANE_7_EQUALIZATION_CNTL` at line 29000. The chunk contains 2,323 `#define` entries: 1,162 register-name aliases and 1,161 matching `*_BASE_IDX` entries. The one-count difference is caused by the chunk ending on a register alias whose `*_BASE_IDX` line appears after the chunk boundary.

The chunk is source-tree-aligned with NBIO register descriptions, not with executable C logic. It is consumed by AMDGPU NBIO code through SOC15 register access macros after inclusion from `drivers/gpu/drm/amd/amdgpu/nbio_v7_7.c`.

## Purpose

The purpose of this header segment is to publish stable symbolic names for NBIO 7.7.0 PCIe BIF configuration registers. These symbols let driver code refer to GPU PCIe endpoint, root-complex, and function-specific configuration registers by semantic names instead of raw encoded offsets.

This chunk is dominated by endpoint-function config blocks:

- Tail of `DEV0_EPF2`, from PCIe vendor-specific enhanced capability through AER, BAR, power-budget, DPA, ACS, PASID, and ARI registers.
- Full `DEV0_EPF3` through `DEV0_EPF7` blocks, each with conventional PCI config header registers, power management, PCIe capability, MSI/MSI-X, SATA/vendor-specific capability registers, AER, BAR enhanced capability, power-budget, DPA, ACS, PASID, and ARI entries.
- Full `DEV1_EPF0`, a larger function block that includes the common endpoint register set plus VC/resource capabilities, secondary PCIe capability, lane equalization controls, 16 GT/s PHY capability/status, and lane margining controls.
- Full `DEV1_EPF1`, a shorter endpoint-function block similar to the DEV0 EPF3-EPF7 pattern.
- Start of `DEV2_EPF0`, including standard config header, power management, PCIe, MSI/MSI-X, vendor-specific and VC capabilities, AER, BAR, power-budget, DPA, secondary PCIe, and lane equalization registers through lane 7.

The address block comments in this chunk identify the hardware aperture regions:

- `nbio_nbif0_bif_cfg_dev0_epf3_bifcfgdecp`, base `0xfffe12103000`
- `nbio_nbif0_bif_cfg_dev0_epf4_bifcfgdecp`, base `0xfffe12104000`
- `nbio_nbif0_bif_cfg_dev0_epf5_bifcfgdecp`, base `0xfffe12105000`
- `nbio_nbif0_bif_cfg_dev0_epf6_bifcfgdecp`, base `0xfffe12106000`
- `nbio_nbif0_bif_cfg_dev0_epf7_bifcfgdecp`, base `0xfffe12107000`
- `nbio_nbif0_bif_cfg_dev1_epf0_bifcfgdecp`, base `0xfffe12300000`
- `nbio_nbif0_bif_cfg_dev1_epf1_bifcfgdecp`, base `0xfffe12301000`
- `nbio_nbif0_bif_cfg_dev2_epf0_bifcfgdecp`, base `0xfffe12500000`

## Important APIs, Types, and Macros

There are no functions, structs, enums, or runtime APIs declared in this chunk. The API surface is a generated C preprocessor namespace:

- `regBIF_CFG_DEVx_EPFy_1_<REGISTER>` constants provide encoded SOC15/NBIO register addresses for PCIe configuration registers.
- `regBIF_CFG_DEVx_EPFy_1_<REGISTER>_BASE_IDX` constants identify the register base index used by AMDGPU's register-access helpers. All complete pairs in this chunk use base index `5`.
- Standard PCI config aliases include `VENDOR_ID`, `DEVICE_ID`, `COMMAND`, `STATUS`, `REVISION_ID`, `PROG_INTERFACE`, `SUB_CLASS`, `BASE_CLASS`, BARs, `ROM_BASE_ADDR`, `CAP_PTR`, and interrupt-line/pin fields.
- PCIe capability aliases include `PCIE_CAP_LIST`, `PCIE_CAP`, `DEVICE_CAP`, `DEVICE_CNTL`, `DEVICE_STATUS`, `LINK_CAP`, `LINK_CNTL`, `LINK_STATUS`, `DEVICE_CAP2`, `DEVICE_CNTL2`, `DEVICE_STATUS2`, `LINK_CAP2`, `LINK_CNTL2`, and `LINK_STATUS2`.
- Interrupt capability aliases include MSI and MSI-X registers such as `MSI_CAP_LIST`, `MSI_MSG_CNTL`, `MSI_MSG_ADDR_LO`, `MSI_MSG_ADDR_HI`, `MSI_MSG_DATA`, `MSI_MASK`, `MSI_PENDING`, `MSIX_CAP_LIST`, `MSIX_MSG_CNTL`, `MSIX_TABLE`, and `MSIX_PBA`.
- Error and diagnostics aliases include AER registers such as `PCIE_UNCORR_ERR_STATUS`, `PCIE_UNCORR_ERR_MASK`, `PCIE_UNCORR_ERR_SEVERITY`, `PCIE_CORR_ERR_STATUS`, `PCIE_CORR_ERR_MASK`, `PCIE_ADV_ERR_CAP_CNTL`, `PCIE_HDR_LOG0..3`, and `PCIE_TLP_PREFIX_LOG0..3`.
- Resource and virtualization/security aliases include enhanced BAR capability registers, ACS, PASID, ARI, VC/resource controls, DPA, and power-budget capability registers.
- High-speed link aliases in the larger endpoint blocks include `PCIE_LINK_CNTL3`, `PCIE_LANE_*_EQUALIZATION_CNTL`, 16 GT/s capability/status entries, and lane margining controls/status fields.

Several symbolic names intentionally share the same encoded address because they name fields or logical views within the same PCI config dword. Examples repeated across blocks include `VENDOR_ID` and `DEVICE_ID`, `COMMAND` and `STATUS`, `DEVICE_CNTL` and `DEVICE_STATUS`, `LINK_CNTL` and `LINK_STATUS`, `PCIE_DPA_STATUS` and `PCIE_DPA_CNTL`, `PCIE_ACS_CAP` and `PCIE_ACS_CNTL`, `PCIE_PASID_CAP` and `PCIE_PASID_CNTL`, and `PCIE_ARI_CAP` and `PCIE_ARI_CNTL`.

## Control Flow

This chunk has no runtime control flow. It is preprocessor data used at compile time.

The effective flow is:

1. `nbio_v7_7.c` includes `nbio/nbio_7_7_0_offset.h` and the matching `nbio_7_7_0_sh_mask.h`.
2. AMDGPU NBIO code passes selected `reg...` constants to access helpers such as `RREG32_SOC15`, `WREG32_SOC15`, `SOC15_REG_OFFSET`, and PCIe-port accessors.
3. The helper layer combines the register offset and base index with device instance information to reach the correct MMIO/register aperture.

Most symbols in this chunk are not directly referenced by the nearby `nbio_v7_7.c` logic in the current tree; they are still part of the generated register map and may be used by diagnostics, future ASIC support, or code paths outside the searched direct references.

## State and Persistence Behavior

The header itself stores no mutable state and performs no persistence. Its constants describe hardware-backed PCIe configuration and capability registers. Any state effects occur only when consumers read or write those registers through AMDGPU accessors.

The registers described here correspond to hardware state such as:

- PCI config identity, command/status, class code, BAR, ROM, and interrupt configuration.
- PCIe link capability, control, status, equalization, and higher-speed PHY state.
- MSI/MSI-X message address/data/masking and pending bits.
- AER correctable/uncorrectable error status, masks, severity policy, header logs, and TLP-prefix logs.
- ACS/PASID/ARI capability and control fields that affect PCIe isolation, address-space tagging, and function routing semantics.
- Power-management, power-budget, and dynamic power allocation fields.

Persistence is hardware-defined. Some registers are strap-derived, reset to ASIC defaults, latched by firmware/platform enumeration, or controlled by PCI/PCIe configuration mechanisms. Driver writes to control/mask/status registers may alter live device behavior but are not persisted by this header.

## Dependencies

Primary dependencies are architectural rather than C-level:

- SOC15/NBIO register addressing conventions used by AMDGPU.
- Matching shift/mask definitions in `nbio_7_7_0_sh_mask.h` for fields within these offsets.
- AMDGPU register access macros and helpers declared through the common AMDGPU headers.
- PCI/PCIe configuration-space layout, including PCI PM, PCIe capability, MSI/MSI-X, AER, ACS, PASID, ARI, DPA, LTR/secondary capability, VC, and link equalization structures.
- The generated ASIC register database that produced this offset file. Manual edits would risk drifting from silicon documentation and the paired mask header.

The chunk is under `sources/distributed-fs/ceph-client/`, but its technical integration is the vendored Linux AMDGPU driver source tree, not Ceph filesystem logic.

## Integration Points

The direct integration point observed in this tree is:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/nbio_v7_7.c` includes this header and uses NBIO 7.7 register symbols for revision ID, memory size, doorbells, interrupt handling, HDP flushes, PCIe index/data ports, and NBIO initialization.

This specific chunk maps endpoint-function PCIe config spaces rather than the doorbell/HDP registers that `nbio_v7_7.c` most visibly touches. Its integration value is still important because the generated header must provide a complete ASIC register namespace for all NBIO subblocks. Downstream users can add reads/writes to these symbols without introducing raw offsets.

The base-index constants are part of the integration contract with AMDGPU's generated-register infrastructure. They must stay paired with the correct `reg...` constants so helpers resolve each register against the intended NBIO base segment.

## Risks and Edge Cases

- Raw offset correctness is critical. A wrong encoded address can read or write the wrong PCIe config register, potentially changing link state, interrupt routing, BAR decoding, AER policy, or isolation features.
- Shared-address aliases are expected for packed PCI config dwords. Reviewers should not deduplicate them casually; the different names preserve semantic intent for different bitfields in the paired mask header.
- The chunk boundary splits a macro pair: `regBIF_CFG_DEV2_EPF0_1_PCIE_LANE_7_EQUALIZATION_CNTL` appears inside this chunk, while its `*_BASE_IDX` is immediately after line 29000. Merge/reconciliation tooling should account for that boundary rather than treating the source as malformed.
- Many blocks are repetitive, but the larger `DEV1_EPF0` and `DEV2_EPF0` areas contain extended link and lane-control coverage not present in the shorter EPF blocks. Bulk generated changes should preserve these block-specific differences.
- Because these are generated ASIC definitions, manual formatting or renaming changes can break out-of-tree users or make future generated drops noisy.
- Capability registers such as ACS, PASID, ARI, AER, and DPA are security- and reliability-sensitive when written. Any future consumer code should use field masks from the matching `*_sh_mask.h` file and preserve reserved bits.

## Test Signals

Useful validation signals for this chunk are mostly static and integration-oriented:

- Compile AMDGPU code that includes `nbio_v7_7.c`; missing, renamed, or malformed macros fail at build time.
- Run a preprocessor or static check that every `reg...` define in the full header has the expected `reg..._BASE_IDX` pair. This chunk alone has one expected boundary exception at its final line.
- Compare the generated offsets against the authoritative NBIO 7.7.0 register database or a known-good generated header such as neighboring NBIO versions.
- Use `rg` for direct consumers before changing symbols; direct references in this tree include the header include from `amdgpu/nbio_v7_7.c`, while many individual endpoint config symbols may be latent API surface.
- On hardware, PCIe enumeration, link training, MSI/MSI-X interrupt delivery, AER logging, and GPU initialization are the practical smoke tests for regressions in these definitions.
- For runtime changes that start using these symbols, test suspend/resume, GPU reset, PCIe error handling, SR-IOV/virtualization paths if applicable, and link-speed/link-width negotiation.
