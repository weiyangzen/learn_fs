# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_6_1_sh_mask.h lines 12201-14624

## Scope

This chunk is a generated AMD NBIO 6.1 shift/mask header segment. It contains only C preprocessor constants; there are no functions, structs, variables, dynamic allocations, locks, loops, branches, or direct register accesses in the assigned range.

The slice contains 2,136 `#define` entries and 279 commented register markers. It starts inside `BIF_CFG_DEV0_EPF0_VF9_0_PCIE_CAP` at the mask definitions, continues through the remaining VF9 PCIe capability, MSI/MSI-X, vendor-specific, AER, ATS, and ARI fields, then covers complete repeated PCI configuration-space field layouts for `BIF_CFG_DEV0_EPF0_VF10_0` and `BIF_CFG_DEV0_EPF0_VF11_0`. It begins `BIF_CFG_DEV0_EPF0_VF12_0` and reaches through `PCIE_HDR_LOG0`; line 14624 is only the `VF12_0_PCIE_HDR_LOG1` marker, with that register's shift and mask definitions continuing in the next chunk.

Although the repository path is under a `ceph-client` mirror, this source is AMDGPU hardware metadata for GPU NBIO/BIF PCIe virtual-function configuration space. It does not implement Ceph or distributed filesystem behavior.

## Purpose

The purpose of this range is to publish bit positions and masks for NBIO 6.1 device 0, endpoint function 0 virtual-function PCIe configuration images. Each field is represented by the generated pair:

- `<REGISTER>__<FIELD>__SHIFT`, the bit offset used when packing or extracting a hardware field.
- `<REGISTER>__<FIELD>_MASK`, the bit mask used to isolate, clear, preserve, or update that field.

Runtime code combines these constants with matching offsets from `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_6_1_offset.h` and, where reset values matter, defaults from `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_6_1_default.h`. Representative offset companions include `cfgBIF_CFG_DEV0_EPF0_VF10_0_VENDOR_ID` at `0x0000`, `cfgBIF_CFG_DEV0_EPF0_VF10_0_PCIE_CAP_LIST` at `0x0064`, `cfgBIF_CFG_DEV0_EPF0_VF10_0_DEVICE_CNTL` at `0x006c`, `cfgBIF_CFG_DEV0_EPF0_VF10_0_MSIX_TABLE` at `0x00c4`, `cfgBIF_CFG_DEV0_EPF0_VF10_0_PCIE_ADV_ERR_RPT_ENH_CAP_LIST` at `0x0150`, `cfgBIF_CFG_DEV0_EPF0_VF10_0_PCIE_ATS_ENH_CAP_LIST` at `0x02b0`, and `cfgBIF_CFG_DEV0_EPF0_VF10_0_PCIE_ARI_ENH_CAP_LIST` at `0x0328`.

## Important Macro Families

The opening VF9 section begins at the masks for `PCIE_CAP` and then defines field layouts for PCIe device/link capability and control registers, capability 2 registers, slot placeholder registers, MSI and MSI-X capability state, vendor-specific enhanced capability dwords, Advanced Error Reporting registers, AER header and TLP prefix logs, ATS capability/control, and ARI capability/control.

`BIF_CFG_DEV0_EPF0_VF10_0` and `BIF_CFG_DEV0_EPF0_VF11_0` are complete in this chunk. Each block repeats the same virtual-function PCI configuration-space template:

- Standard PCI header fields: vendor/device ID, command/status, revision ID, programming interface, subclass/base class, cache line, latency, header, BIST, six BARs, adapter/subsystem ID, ROM base, capability pointer, interrupt line, and interrupt pin.
- PCIe capability fields: capability list header, PCIe capability descriptor, device capability/control/status, link capability/control/status, device/link capability 2 controls and status, and empty slot-capability placeholders.
- Interrupt capability fields: MSI list header, MSI message control, low/high message address, message data, mask, pending bits, 64-bit aliases, MSI-X list header, MSI-X table size/function mask/enable, table BIR/offset, and PBA BIR/offset.
- Vendor-specific enhanced capability fields: enhanced capability list header, VSEC header, and two scratch dwords.
- AER fields: enhanced capability header, uncorrectable error status/mask/severity, correctable error status/mask, advanced error capability/control, four header-log dwords, and four TLP-prefix-log dwords.
- Address translation and function-routing fields: ATS enhanced capability, ATS queue/page/global-invalidate capability, ATS control `STU` and `ATC_ENABLE`, ARI enhanced capability, ARI capability next-function/function-group fields, and ARI control function-group enable/select bits.

The VF12 section is partial. It covers identity/header/BAR fields through MSI/MSI-X, vendor-specific enhanced capability, AER uncorrectable/correctable status/mask/severity, AER capability/control, and `PCIE_HDR_LOG0`. The `PCIE_HDR_LOG1` marker is present at the chunk end, but its actual shift/mask definitions are outside this work item.

## APIs, Types, And Functions

There are no callable APIs, C types, or functions in this chunk. The exported interface is the macro namespace itself:

- `BIF_CFG_DEV0_EPF0_VF9_0_*__SHIFT` and `BIF_CFG_DEV0_EPF0_VF9_0_*_MASK` for the tail of VF9's PCIe capability and extended-capability layout.
- `BIF_CFG_DEV0_EPF0_VF10_0_*__SHIFT` and `BIF_CFG_DEV0_EPF0_VF10_0_*_MASK` for a complete VF10 PCIe configuration-space layout.
- `BIF_CFG_DEV0_EPF0_VF11_0_*__SHIFT` and `BIF_CFG_DEV0_EPF0_VF11_0_*_MASK` for a complete VF11 PCIe configuration-space layout.
- `BIF_CFG_DEV0_EPF0_VF12_0_*__SHIFT` and `BIF_CFG_DEV0_EPF0_VF12_0_*_MASK` for the beginning and middle of VF12 through `PCIE_HDR_LOG0`.

The constants are untyped preprocessor integer literals, mostly 16-bit or 32-bit masks with `L` suffixes. They do not carry access width, register offset, read-only/write-only ownership, reset value, or side-effect semantics; callers must get those from the register database, hardware manual, PCIe specification behavior, and surrounding AMDGPU access code.

## Control Flow

This header has no executable control flow. Runtime control flow appears only in code that includes it:

1. AMDGPU code chooses the correct virtual-function register offset from `nbio_6_1_offset.h`.
2. The driver reads, composes, or updates a PCIe configuration-space value through the AMDGPU register access layer.
3. The shift/mask constants from this file are applied directly or through helpers such as `REG_GET_FIELD`, `REG_SET_FIELD`, `RREG32_PCIE`, `WREG32_PCIE`, `RREG32_SOC15`, `WREG32_SOC15`, and `SOC15_REG_OFFSET`.
4. The resulting value is used to publish VF identity/resources, enable or decode PCIe controls, program interrupt delivery, inspect AER diagnostics, configure ATS/ARI behavior, or restore state across reset and power transitions.

Typical consuming flows include SR-IOV VF setup, guest-visible PCI configuration emulation or pass-through, PF-managed VF resource publication, MSI/MSI-X routing, PCIe device/link policy, AER/RAS diagnostics, ATS/IOMMU coordination, ARI enumeration, reset/FLR behavior, suspend/resume restore, and debug dumps of PCIe configuration space.

## State And Persistence Behavior

This file stores no software state and persists nothing to disk. It describes hardware-backed PCIe configuration-space state owned by the GPU, platform firmware, Linux PCI core policy, AMDGPU NBIO/SR-IOV code, and guest or virtualization management flows.

The represented hardware state spans static capabilities, software-programmed controls, hardware-updated status, interrupt routing state, and diagnostic logs. Identity, class, BAR, ROM, adapter/subsystem, and capability-list fields shape how virtual functions appear to the host or guest. Command/status, PCIe device/link controls, completion timeout, relaxed ordering, no-snoop, max payload/read request, FLR, link retrain/disable, target speed, and ASPM-related fields affect DMA, reset, link, and enumeration behavior. MSI/MSI-X fields affect interrupt delivery. AER status, mask, severity, header logs, and TLP prefix logs record or control PCIe error reporting. ATS and ARI fields affect address translation cache behavior, invalidation support, and function enumeration/routing.

The generated macros do not encode reset defaults, sticky status behavior, write-one-to-clear rules, firmware ownership, required ordering around reads/writes, or whether a field is meaningful for a specific ASIC fuse/platform/virtualization mode.

## Dependencies And Integration Points

The immediate dependencies are the sibling generated NBIO 6.1 files:

- `nbio_6_1_offset.h`, which supplies the `cfgBIF_CFG_DEV0_EPF0_VF*_0_*` offsets that must be paired with these masks.
- `nbio_6_1_default.h`, which supplies generated `cfgBIF_CFG_DEV0_EPF0_VF*_0_*_DEFAULT` reset/default values for many of the same virtual-function registers.

Direct in-tree include sites for this header include `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/nbio_v6_1.c`, `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/mxgpu_ai.c`, and Vega power-management include aggregators such as `drivers/gpu/drm/amd/pm/powerplay/hwmgr/vega10_inc.h` and `vega12_inc.h`. `psp_v3_1.c` and display resource code include the offset header for related NBIO 6.1 register access.

Important external integration surfaces are the Linux PCI core, IOMMU and ATS policy, SR-IOV PF/VF lifecycle management, guest drivers, interrupt remapping/MSI/MSI-X delivery, PCIe AER handling, platform firmware, runtime power management, GPU reset/FLR flows, and diagnostic tooling that decodes PCIe configuration space.

## Risks And Edge Cases

- The chunk boundaries are artificial. It starts after the VF9 `PCIE_CAP` shifts and ends at the VF12 `PCIE_HDR_LOG1` comment before that register's shift/mask pair.
- These are untyped preprocessor constants. A bad field name, copied suffix, shift, or mask compiles cleanly but can decode or program the wrong hardware bit.
- The VF9/VF10/VF11/VF12 blocks are highly repetitive. Suffix drift between virtual functions can silently target the wrong VF and affect guest-visible resources, interrupts, or diagnostics.
- Offset/header drift is dangerous. These masks must be paired with `nbio_6_1_offset.h` offsets for the same NBIO generation and same `VF*_0` namespace; similarly named masks in other NBIO versions or access domains may not be interchangeable.
- PCI command and PCIe device-control fields have direct DMA and ordering consequences. Incorrect memory/bus-master enable, relaxed ordering, no-snoop, max payload, max read request, completion timeout, extended tag, or FLR programming can cause enumeration failures, DMA faults, ordering bugs, or reset hangs.
- PCIe link-control fields are platform-sensitive. Link disable, retrain, common clock, target speed, hardware autonomous speed/width disable, bandwidth interrupt enables, and link-status decoding can cause link instability or misleading diagnostics if used without PCIe policy checks.
- MSI/MSI-X fields control interrupt delivery. Mistakes in enable bits, function mask, table/PBA BIR and offsets, message address/data, masks, pending bits, or 64-bit aliases can produce lost, misrouted, or unexpectedly unmasked interrupts.
- AER status registers may be sticky or write-one-to-clear depending on hardware semantics. Treating status/mask/severity/header-log fields as generic read/modify/write state can erase evidence or leave errors reported at the wrong severity.
- ATS and ARI fields affect virtualization and IOMMU behavior. Incorrect `ATC_ENABLE`, smallest translation unit, invalidation queue depth interpretation, ARI next-function, or function-group controls can break VF enumeration, guest address translation, or isolation expectations.
- Default values are not present in this header. Code that assumes masks imply reset state will miss nonzero capability-list/default values supplied separately by `nbio_6_1_default.h`.

## Test Signals

Useful validation is mostly build-time consistency plus hardware or virtualization integration:

- Build AMDGPU paths that include NBIO 6.1 support so missing, renamed, or malformed macros surface in `nbio_v6_1.c`, `mxgpu_ai.c`, and Vega power-management include chains.
- Run a static pairing check that every complete `BIF_CFG_DEV0_EPF0_VF10_0_*` and `BIF_CFG_DEV0_EPF0_VF11_0_*` register block in this chunk has a matching `cfgBIF_CFG_DEV0_EPF0_VF10_0_*` or `cfgBIF_CFG_DEV0_EPF0_VF11_0_*` offset in `nbio_6_1_offset.h`.
- Compare representative defaults in `nbio_6_1_default.h` against decoded masks for identity, capability-list, PCIe, MSI/MSI-X, AER, ATS, and ARI registers.
- On NBIO 6.1 hardware with supported virtualization, create and remove VFs, bind guest drivers, and verify VF10/VF11/VF12 PCI configuration-space dumps decode consistently for identity/header, BARs, PCIe capability, MSI/MSI-X, AER, ATS, and ARI fields.
- Exercise MSI/MSI-X interrupt delivery under graphics, compute, DMA, and reset activity; watch for lost vectors, stuck pending bits, incorrect table/PBA decoding, or unexpected masking.
- Exercise suspend/resume, runtime power transitions, PCIe link retraining, ASPM/LTR policy changes where applicable, and FLR/reset paths while checking command/status, link status, completion timeout, and transaction-pending behavior.
- Use PCIe AER/error-injection or platform diagnostics where available to verify uncorrectable/correctable status, mask, severity, first-error pointer, ECRC controls, header logs, and TLP prefix logs decode as expected without losing diagnostic state.
- In ATS/ARI-capable configurations, validate IOMMU address translation behavior, ATS enable/disable sequencing, invalidation handling, ARI function enumeration, and guest isolation before and after VF lifecycle and reset operations.

## Chunk Notes

- Lines 12201-12724 finish the `BIF_CFG_DEV0_EPF0_VF9_0` block from `PCIE_CAP` masks through `DEVICE_CAP`, `DEVICE_CNTL`, `DEVICE_STATUS`, link capability/control/status, MSI/MSI-X, vendor-specific capability, AER, ATS, and ARI.
- Lines 12725-13378 define the complete `addressBlock: nbio_nbif_bif_cfg_dev0_epf0_vf10_bifcfgdecp` macro set for `BIF_CFG_DEV0_EPF0_VF10_0`.
- Lines 13379-14032 define the complete `addressBlock: nbio_nbif_bif_cfg_dev0_epf0_vf11_bifcfgdecp` macro set for `BIF_CFG_DEV0_EPF0_VF11_0`.
- Lines 14033-14624 begin `addressBlock: nbio_nbif_bif_cfg_dev0_epf0_vf12_bifcfgdecp` and cover `BIF_CFG_DEV0_EPF0_VF12_0` through `PCIE_HDR_LOG0`; `PCIE_HDR_LOG1` starts after the assigned chunk boundary.
