# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_7_0_sh_mask.h lines 1-2466

## Purpose

This chunk is the opening section of AMDGPU's generated NBIO 7.0 shift/mask header. It defines bitfield offsets and masks for early NBIO/NBIF configuration spaces: northbridge configuration registers, the IOMMU L2 configuration capability block, root-complex PCIe configuration for BIF device 0, and the beginning of the matching BIF device 1 root-complex configuration block.

The header is hardware metadata, not executable logic. Its constants let AMDGPU register helpers encode field writes and decode register reads without hard-coding bit positions in driver C files. The companion NBIO 7.0 offset/default/SMN headers provide register addresses and reset/default values; this file supplies field geometry.

## Important APIs, Types, and Macros

There are no C functions, structs, typedefs, or enums in this chunk. The public interface is preprocessor constants named as:

- `<REGISTER>__<FIELD>__SHIFT`: bit offset for a field inside a register.
- `<REGISTER>__<FIELD>_MASK`: field mask at its encoded position.

Lines 1-2466 contain 2,145 `#define` rows: the include guard plus 1,073 shift definitions and 1,071 complete mask definitions. The shift/mask imbalance is expected because the artificial chunk boundary stops after two shift definitions for `BIF_CFG_DEV1_RC0_PCIE_VC0_RESOURCE_CAP`; the remaining two shifts and all four masks for that register are on lines 2467-2472 in the next chunk.

Important register families in this range include:

- `NB_NBCFG0_*`: northbridge PCI configuration identity, command/status, revision/class, cache/latency/header, adapter ID, capability pointer, PCI control, SMN index/data windows, scratch registers, PCI arbitration, DRAM slot base/top-of-DRAM, index/data mutexes, and global NB performance counter control fields.
- `IOMMU_L2_0_IOMMU_*`: IOMMU L2 PCI identity and command/status fields, capability header/base/range/miscellaneous descriptors, MSI and MSI mapping capability fields, writable capability mirrors, MMIO/SMMU feature ID registers, DSFX/DSSX/DSCX dummy/control fields, DMA/host-response stall controls, and ARM SMMU-style ID registers.
- `BIF_CFG_DEV0_RC0_*`: a complete root-complex configuration namespace for NBIF device 0. It covers standard PCI bridge identity, command/status, BAR and bus range fields, bridge controls, power-management capability, PCIe capability, device/link/slot/root controls and statuses, MSI and SSID/MSI-map capability fields, vendor-specific and VC enhanced capabilities, device serial number, AER status/mask/severity/header-log/root-error fields, secondary PCIe capability, lane error status, lane 0-15 equalization controls, and ACS capability/control.
- `BIF_CFG_DEV1_RC0_*`: the beginning of the corresponding device 1 root-complex namespace. The chunk repeats the same PCI bridge, PM, PCIe, MSI, vendor-specific, and VC capability patterns through the first two shifts of `PCIE_VC0_RESOURCE_CAP`.

These constants are normally consumed by helpers such as `REG_GET_FIELD`, `REG_SET_FIELD`, `RREG32_SOC15`, `WREG32_SOC15`, `RREG32_PCIE`, and `WREG32_PCIE`. The register address side comes from `nbio_7_0_offset.h` and `nbio_7_0_smn.h`.

## Control Flow and Runtime Behavior

This chunk has no runtime control flow. Including it gives the compiler symbols for mask-and-shift operations. Actual behavior is in AMDGPU NBIO, SOC15, PCIe, power-management, IOMMU, and error-handling code that reads or writes the registers.

The implied hardware flows are:

1. NB configuration fields expose device identity, command/status bits, SMN access windows, scratch registers, DRAM aperture metadata, index/data mutexes, and performance counter controls.
2. IOMMU L2 capability fields advertise and control translation unit capabilities, MSI delivery, SMMU MMIO exposure, feature IDs, stall behavior, DVM/DSFX support, and address-size/range metadata.
3. BIF device 0 root-complex fields describe bridge enumeration, memory and I/O forwarding windows, PME and link power controls, PCIe link speed/width negotiation, slot/hotplug controls, MSI routing, virtual channel allocation, PCIe advanced error reporting, lane equalization, and ACS policy.
4. BIF device 1 starts the same root-complex capability flow, but this chunk stops before its VC0 resource-capability definition is complete.

Because this is generated register metadata, control-flow risk is indirect: callers depend on these constants to preserve reserved bits, update only intended fields, and interpret hardware status correctly.

## State and Persistence

The header owns no runtime state, allocates no memory, performs no I/O, and persists nothing. The state represented here lives in NBIO 7.0 hardware registers.

State classes represented by the constants include:

- Enumerated PCI identity and capability metadata, such as vendor/device IDs, class/revision fields, capability pointers, PCIe capability versions, serial-number dwords, and feature capability bits.
- Writable configuration state, such as command enables, bridge windows, PME/MSI controls, link control, device control, VC arbitration controls, ACS controls, and IOMMU/SMMU enable or capability mirror fields.
- Hardware status/readback state, such as PCI status errors, link training/active status, slot status, root PME/error status, AER status/header logs, lane error status, and IOMMU/SMMU ID/status fields.
- Transient or side-effect-prone controls, including status clear fields, error masks/severity, link retrain/disable, function-level reset capability, IRQ/hotplug enables, VC table load controls, and index/data mutex unlock bits.

Reset values and retention across GPU reset, suspend/resume, PCI reset, or runtime power transitions are not defined here. Those semantics come from the NBIO hardware and companion default headers such as `nbio_7_0_default.h`.

## Dependencies and Integration Points

Primary companion generated headers are:

- `nbio_7_0_offset.h` for `cfg*` and `mm*` register offsets, including the registers named in this chunk.
- `nbio_7_0_default.h` for reset/default values.
- `nbio_7_0_smn.h` for SMN-addressed NBIO/PCIe registers outside ordinary config offsets.
- Adjacent chunks of `nbio_7_0_sh_mask.h`, especially the next chunk that completes `BIF_CFG_DEV1_RC0_PCIE_VC0_RESOURCE_CAP` and continues device 1 root-complex definitions.

In-tree include sites for this header include:

- `drivers/gpu/drm/amd/amdgpu/nbio_v7_0.c`, where NBIO 7.0 code combines offset, default, shift/mask, and SMN headers for doorbells, memory-controller access, register remapping, clock gating, and PCIe/NBIO register programming.
- `drivers/gpu/drm/amd/amdgpu/soc15.c`, where SOC15 common initialization includes NBIO 7.0 register metadata for Vega/Raven-era device setup.
- `drivers/gpu/drm/amd/pm/powerplay/hwmgr/smu10_inc.h`, which pulls NBIO 7.0 register metadata into SMU10/powerplay hardware-manager definitions.

Integration areas touched by these constants include PCI/PCIe enumeration, root-port bridge setup, NBIO index/SMN accesses, IOMMU discovery/configuration, MSI routing, link training and equalization, PCIe power management, hotplug/slot handling, AER/RAS reporting, ACS isolation, and NBIO clock/power-management paths.

## Risks

- Generated-header drift is the main risk. A wrong mask or shift silently makes `REG_SET_FIELD` or `REG_GET_FIELD` operate on the wrong hardware bits.
- The chunk boundary splits `BIF_CFG_DEV1_RC0_PCIE_VC0_RESOURCE_CAP`: only `PORT_ARB_CAP` and `REJECT_SNOOP_TRANS` shifts are inside this work item. Validators and merge logic must not treat the missing masks as source corruption.
- Many fields mirror PCI/PCIe architectural layouts. Small mistakes in bridge windows, link controls, AER masks, MSI addresses, VC mappings, or ACS controls can cause enumeration failures, interrupts routed incorrectly, hidden errors, peer-to-peer isolation gaps, or link instability.
- `BIF_CFG_DEV0_RC0_*` and `BIF_CFG_DEV1_RC0_*` are highly repetitive. Copy/paste or generator errors may only affect one root-complex instance and can be missed if tests exercise a single port.
- Several definitions include writable control bits adjacent to read-only status or reserved fields. Callers must use read-modify-write helpers carefully and preserve reserved bits.
- Error status, mask, and severity registers have very similar names. Confusing status fields with mask fields can leave PCIe errors uncleared, unreported, or misclassified.
- IOMMU and SMMU capability fields influence address translation, MSI delivery, and device range discovery. Bad masks here can break DMA isolation or produce misleading capability reporting.

## Test and Validation Signals

Useful validation is mostly generated-header consistency plus hardware integration:

- Kernel build coverage with AMDGPU NBIO 7.0 users enabled catches missing, renamed, or syntactically invalid macros.
- Mechanical checks should verify that each complete register in lines 1-2466 has paired `__SHIFT` and `_MASK` definitions, while allowing the include guard and the known split at `BIF_CFG_DEV1_RC0_PCIE_VC0_RESOURCE_CAP`.
- Cross-header checks should compare register names in this chunk against `nbio_7_0_offset.h`, `nbio_7_0_smn.h`, and `nbio_7_0_default.h` so addresses/defaults and bitfield metadata stay aligned.
- Symmetry checks should compare `BIF_CFG_DEV0_RC0_*` against the overlapping `BIF_CFG_DEV1_RC0_*` subset, ignoring only the device number and the artificial chunk ending.
- PCIe smoke tests on NBIO 7.0 ASICs should cover device enumeration, BAR and bridge-window programming, MSI delivery, link speed/width negotiation, link retrain/equalization, ASPM/power-management transitions, hotplug/slot status where applicable, ACS policy, and AER status/mask/reporting paths.
- IOMMU validation should exercise capability discovery, MSI mapping, MMIO/SMMU feature reporting, DMA translation/range setup, and error/status readback.
- Resume/reset tests should verify that driver reprogramming using these masks restores NBIO, BIF, IOMMU, PCIe link, interrupt, and error-reporting state after GPU reset or system suspend/resume.

## Chunk Boundary Notes

This chunk starts at the file header and includes complete address blocks for `nbio_iohub_nb_nbcfg_nb_cfgdec`, `nbio_iohub_iommu_l2_iommul2cfg`, and `nbio_nbif0_bif_cfg_dev0_rc_bifcfgdecp`. It then enters `nbio_nbif0_bif_cfg_dev1_rc_bifcfgdecp` and stops at line 2466 after the first two shifts for `BIF_CFG_DEV1_RC0_PCIE_VC0_RESOURCE_CAP`. The next chunk owns the remaining shifts and masks for that register plus the rest of the device 1 root-complex namespace.
