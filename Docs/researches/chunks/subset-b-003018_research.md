# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_6_1_sh_mask.h lines 31898-34344

## Purpose

This chunk is part of AMDGPU's generated NBIO 6.1 register shift/mask header. It contains C preprocessor constants for PCI configuration-space bitfields exposed through `BIF_CFG_DEV0_EPF0_*` virtual-function register names. The chunk starts at the tail of the VF7 PCIe extended-capability block, covers complete repeated blocks for VF8, VF9, and VF10, and ends in the first part of the VF11 block at `BIF_CFG_DEV0_EPF0_VF11_1_PCIE_ADV_ERR_RPT_ENH_CAP_LIST`.

The definitions describe how to extract or program fields in PCI/PCIe config registers: vendor/device ID, command/status, class/revision/header/BIST, BARs, subsystem adapter ID, ROM base, capability pointers, PCIe capability and link control/status registers, MSI/MSI-X capability registers, vendor-specific extended capability registers, advanced error reporting registers, ATS capability/control, and ARI capability/control. The file is data-like hardware metadata, not executable logic.

## Important APIs, Types, and Macros

There are no C functions, structs, enums, or typedefs in this chunk. The exported interface is a large set of `#define` constants named as:

- `<REGISTER>__<FIELD>__SHIFT`: bit offset for a field.
- `<REGISTER>__<FIELD>_MASK`: field mask at its encoded register position.

The chunk has 2,132 `#define` entries. The repeated VF blocks account for 572 definitions each for VF8, VF9, and VF10, 378 definitions for the partial VF11 block, and 38 definitions for the VF7 tail. The fully covered VF8/VF9/VF10 sections are introduced by address-block comments such as `nbio_nbif_bif_cfg_dev0_epf0_vf8_bifcfgdecp`, making them mirror the companion offset header's config-space register map.

Important register families visible here include:

- Basic PCI config header fields: `VENDOR_ID`, `DEVICE_ID`, `COMMAND`, `STATUS`, `REVISION_ID`, `PROG_INTERFACE`, `SUB_CLASS`, `BASE_CLASS`, `CACHE_LINE`, `LATENCY`, `HEADER`, `BIST`, `BASE_ADDR_1` through `BASE_ADDR_6`, `ADAPTER_ID`, `ROM_BASE_ADDR`, `CAP_PTR`, `INTERRUPT_LINE`, and `INTERRUPT_PIN`.
- PCIe capability fields: `PCIE_CAP_LIST`, `PCIE_CAP`, `DEVICE_CAP`, `DEVICE_CNTL`, `DEVICE_STATUS`, `LINK_CAP`, `LINK_CNTL`, `LINK_STATUS`, and the PCIe 2.0 variants `DEVICE_CAP2`, `DEVICE_CNTL2`, `DEVICE_STATUS2`, `LINK_CAP2`, `LINK_CNTL2`, `LINK_STATUS2`, plus reserved slot capability/control/status 2 registers.
- Interrupt capability fields: `MSI_CAP_LIST`, `MSI_MSG_CNTL`, `MSI_MSG_ADDR_LO`, `MSI_MSG_ADDR_HI`, `MSI_MSG_DATA`, `MSI_MASK`, `MSI_PENDING`, the 64-bit MSI aliases, `MSIX_CAP_LIST`, `MSIX_MSG_CNTL`, `MSIX_TABLE`, and `MSIX_PBA`.
- Extended capability fields: `PCIE_VENDOR_SPECIFIC_ENH_CAP_LIST`, `PCIE_VENDOR_SPECIFIC_HDR`, `PCIE_VENDOR_SPECIFIC1`, `PCIE_VENDOR_SPECIFIC2`, `PCIE_ADV_ERR_RPT_ENH_CAP_LIST`, `PCIE_UNCORR_ERR_STATUS`, `PCIE_UNCORR_ERR_MASK`, `PCIE_UNCORR_ERR_SEVERITY`, `PCIE_CORR_ERR_STATUS`, `PCIE_CORR_ERR_MASK`, `PCIE_ADV_ERR_CAP_CNTL`, `PCIE_HDR_LOG0` through `PCIE_HDR_LOG3`, and `PCIE_TLP_PREFIX_LOG0` through `PCIE_TLP_PREFIX_LOG3`.
- Address translation and routing fields: `PCIE_ATS_ENH_CAP_LIST`, `PCIE_ATS_CAP`, `PCIE_ATS_CNTL`, `PCIE_ARI_ENH_CAP_LIST`, `PCIE_ARI_CAP`, and `PCIE_ARI_CNTL`.

These constants are intended for the AMDGPU register helper macros used elsewhere in the driver, for example `REG_GET_FIELD`, `REG_SET_FIELD`, `RREG32_SOC15`, `WREG32_SOC15`, and related NBIO/SOC15 register-access wrappers. This chunk supplies only field geometry; the actual register addresses come from `nbio_6_1_offset.h`.

## Control Flow and Runtime Behavior

This chunk has no runtime control flow. Including the header only provides constants for compile-time expansion. Runtime behavior occurs when AMDGPU code reads or writes the corresponding NBIO PCIe config registers using the offset names plus these shift/mask definitions.

The repeated layout matters operationally: VF8, VF9, and VF10 expose the same PCIe configuration and capability field model, while the VF7 content here closes its ATS/ARI tail and the VF11 content continues into the next chunk for AER details. Driver code or generated tables can therefore address per-VF config registers by selecting the matching VF register symbol while using identical field names.

## State and Persistence

The header itself owns no state, performs no allocation, and persists nothing. The state described by these macros is hardware state in NBIO/PCIe configuration space. Some fields represent writable controls (`COMMAND`, `DEVICE_CNTL`, `LINK_CNTL`, `DEVICE_CNTL2`, `MSI_MSG_CNTL`, `MSIX_MSG_CNTL`, `PCIE_ATS_CNTL`, `PCIE_ARI_CNTL`), while others represent capabilities, status, error latches, address registers, or diagnostic logs.

Persistence and reset behavior are determined by the GPU's PCIe/NBIO hardware and by PCIe configuration-space semantics, not by this header. A driver bug in these constants would be persistent only in the sense that every compiled user of the header would encode or decode the affected field incorrectly.

## Dependencies and Integration Points

Primary dependencies are the companion generated NBIO headers:

- `nbio_6_1_offset.h` for register offsets and base-index constants.
- Other NBIO 6.1 generated headers for defaults and related register blocks.
- AMDGPU SOC15 register-access helpers that combine offset, mask, and shift constants.

In-tree AMDGPU files include this header for NBIO 6.1 behavior, notably `drivers/gpu/drm/amd/amdgpu/nbio_v6_1.c` and `drivers/gpu/drm/amd/amdgpu/mxgpu_ai.c`. The specific VF8-VF11 config-space symbols in this chunk are most relevant to virtualization/SR-IOV style paths, PCIe capability enumeration/configuration, error reporting, MSI/MSI-X setup, ATS, and ARI handling. Since the chunk describes per-VF PCIe config fields, it also aligns with adjacent NBIO/NBIF generated headers that repeat the same config-space capability layout for other ASIC revisions or other VFs.

## Risks

- Generated-header drift is the main risk. If a `_MASK` or `__SHIFT` value diverges from the hardware register specification, register helper macros will silently manipulate the wrong bits.
- The per-VF repetition is easy to mis-edit manually. A copy/paste error between VF8, VF9, VF10, and VF11 could affect only one virtual function and be hard to diagnose.
- Width-sensitive masks must match the PCIe field width exactly. Examples include full-width BAR/log fields (`0xFFFFFFFFL`), 16-bit MSI data fields, 11-bit MSI-X table size, and AER status/mask/severity fields.
- This chunk straddles chunk boundaries. VF7 starts in an earlier chunk, and VF11 continues in the next chunk, so whole-file analysis must reconcile capability blocks across chunk boundaries before drawing per-file conclusions.
- Because the constants use `L` suffixes and are consumed in bit operations, portability depends on the kernel's existing assumptions about integer widths and the AMDGPU helper macros.

## Test and Validation Signals

Useful validation is mostly compile-time and hardware/driver integration based:

- Kernel build coverage for AMDGPU with NBIO 6.1 enabled catches missing or renamed macros.
- Static checks can verify every `__SHIFT` has the expected paired `_MASK`, masks are contiguous where the hardware field requires it, and repeated VF8/VF9/VF10 definitions remain identical except for the VF number.
- Cross-header checks can compare register names in `nbio_6_1_sh_mask.h` against `nbio_6_1_offset.h` to catch missing offsets or orphan field definitions.
- Runtime smoke tests on affected ASICs should exercise PCIe link setup, MSI/MSI-X interrupt delivery, SR-IOV virtual functions, ATS/ARI enablement, and PCIe AER logging.
- Diagnostic validation can read PCIe config space for VF8-VF11 and confirm decoded command/status, link state, MSI/MSI-X state, ATS/ARI capability values, and AER status fields match expected hardware behavior.
