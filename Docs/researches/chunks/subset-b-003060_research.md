# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_7_0_default.h lines 1-2880

## Scope

This chunk covers the first 2,880 lines of the generated AMD NBIO 7.0 default-register header. The full source file is much larger; this chunk contains the license and include guard plus the initial NBIO/IOMMU/PCIe configuration-space default-value macros. It defines 2,793 preprocessor constants in the assigned range and no functions, structs, enums, or executable statements.

## Purpose

The header provides hardware reset/default values for NBIO 7.0 register and PCI configuration-space fields used by AMDGPU and related SMU/power-management code. In this chunk, the constants describe:

- Northbridge configuration defaults for `nbio_iohub_nb_nbcfg_nb_cfgdec`.
- IOMMU L2 configuration defaults for `nbio_iohub_iommu_l2_iommul2cfg`.
- NBIF root-complex PCIe config defaults for device 0 and device 1.
- Dummy PCIe function headers.
- Endpoint-function PCIe config defaults for several `DEV0_EPF*` and `DEV1_EPF*` functions.
- PCIe physical/root-port-like `BIFPLR0` through the start of `BIFPLR4`.

The values are intended to be consumed with companion generated headers such as `nbio_7_0_offset.h`, `nbio_7_0_sh_mask.h`, and `nbio_7_0_smn.h`, giving driver code symbolic names for reset values when initializing, comparing, restoring, or documenting register programming.

## Important APIs, Types, And Macros

There are no C APIs or types in this chunk. The public surface is entirely C preprocessor macros with names ending in `_DEFAULT`.

The top-level guard is `_nbio_7_0_DEFAULT_HEADER`. Its casing differs from typical all-caps guard style but matches generated AMD register headers.

Important macro groups include:

- `cfgNB_NBCFG0_*_DEFAULT`: northbridge PCI config defaults. Notable non-zero defaults include `cfgNB_NBCFG0_NB_HEADER_DEFAULT` and `_HEADER_W_DEFAULT` at `0x00000080`, adapter IDs at `0x15d01022`, `NB_PCI_ARB_DEFAULT` at `0x00000108`, and `NB_PERF_CNT_CTRL_DEFAULT` at `0x00808000`.
- `cfgIOMMU_L2_0_*_DEFAULT`: AMD IOMMU/SMMU defaults. Vendor/device IDs are `0x1022`/`0x15d1`, interrupt pin defaults to `1`, and several SMMU ID/control values are non-zero, including `IOMMU_CONTROL_W_DEFAULT`, `IOMMU_MMIO_CONTROL0_W_DEFAULT`, `IOMMU_MMIO_CONTROL1_W_DEFAULT`, `SMMU_MMIO_IDR0_W_DEFAULT`, `SMMU_MMIO_IDR1_W_DEFAULT`, and `SMMU_MMIO_IDR5_W_DEFAULT`.
- `cfgBIF_CFG_DEV{0,1}_RC0_*_DEFAULT`: root-complex config-space defaults. They model PCI/PCIe capability chains, MSI capability defaults, virtual channel defaults, AER defaults, link capability/status defaults, lane-equalization defaults, and ACS defaults for two root-complex devices.
- `cfgNB_PCIEDUMMY{0,1}_0_*_DEFAULT`: compact dummy PCIe config headers with non-zero header type defaults.
- Unprefixed `cfg*` macros for `nbio_nbif0_bif_cfg_dev0_epf0_bifcfgdecp`: endpoint function 0 has generic names such as `cfgVENDOR_ID_DEFAULT`, `cfgLINK_CAP_DEFAULT`, and `cfgPCIE_SRIOV_SYSTEM_PAGE_SIZE_DEFAULT`. These are more collision-prone than the later prefixed endpoint groups and depend on include ordering/namespace discipline across generated headers.
- `cfgBIF_CFG_DEV0_EPF{1..7}_0_*_DEFAULT` and `cfgBIF_CFG_DEV1_EPF{0..2}_0_*_DEFAULT`: repeated endpoint-function templates for PCIe capability, MSI/MSI-X, AER, BAR enhanced capability, power budget, DPA, ACS, ARI, and in some functions ATS/PASID/page request/TPH/multicast/LTR/SR-IOV or SATA/USB-like capability placeholders.
- `cfgBIFPLR{0..4}_0_*_DEFAULT`: physical/root-port configuration defaults. This chunk fully covers `BIFPLR0` through `BIFPLR3` and begins `BIFPLR4`.

## Address-Block Layout

The assigned range is organized by generated comments of the form `// addressBlock: ...`. The visible blocks are:

- Lines 25-74: `nbio_iohub_nb_nbcfg_nb_cfgdec`.
- Lines 75-122: `nbio_iohub_iommu_l2_iommul2cfg`.
- Lines 123-247: `nbio_nbif0_bif_cfg_dev0_rc_bifcfgdecp`.
- Lines 248-372: `nbio_nbif0_bif_cfg_dev1_rc_bifcfgdecp`.
- Lines 373-380: `nbio_iohub_nb_pciedummy0_pciedummy_cfgdec`.
- Lines 381-388: `nbio_iohub_nb_pciedummy1_pciedummy_cfgdec`.
- Lines 389-642: `nbio_nbif0_bif_cfg_dev0_epf0_bifcfgdecp`.
- Lines 643-896: `nbio_nbif0_bif_cfg_dev0_epf1_bifcfgdecp`.
- Lines 897-1022: `nbio_nbif0_bif_cfg_dev0_epf2_bifcfgdecp`.
- Lines 1023-1148: `nbio_nbif0_bif_cfg_dev0_epf3_bifcfgdecp`.
- Lines 1149-1274: `nbio_nbif0_bif_cfg_dev0_epf4_bifcfgdecp`.
- Lines 1275-1400: `nbio_nbif0_bif_cfg_dev0_epf5_bifcfgdecp`.
- Lines 1401-1526: `nbio_nbif0_bif_cfg_dev0_epf6_bifcfgdecp`.
- Lines 1527-1652: `nbio_nbif0_bif_cfg_dev0_epf7_bifcfgdecp`.
- Lines 1653-1807: `nbio_nbif0_bif_cfg_dev1_epf0_bifcfgdecp`.
- Lines 1808-1933: `nbio_nbif0_bif_cfg_dev1_epf1_bifcfgdecp`.
- Lines 1934-2059: `nbio_nbif0_bif_cfg_dev1_epf2_bifcfgdecp`.
- Lines 2060-2231: `nbio_pcie0_bifplr0_cfgdecp`.
- Lines 2232-2403: `nbio_pcie0_bifplr1_cfgdecp`.
- Lines 2404-2575: `nbio_pcie0_bifplr2_cfgdecp`.
- Lines 2576-2747: `nbio_pcie0_bifplr3_cfgdecp`.
- Lines 2748-2880: the beginning of `nbio_pcie0_bifplr4_cfgdecp`.

## Control Flow

This chunk has no runtime control flow. It influences control flow indirectly when included driver code uses these macros as literal values in register programming, reset comparison, or default initialization paths.

The main integration path is compile-time inclusion:

- `drivers/gpu/drm/amd/amdgpu/nbio_v7_0.c` includes this header with the matching offset, mask, and SMN headers. That source implements NBIO operations such as HDP remap, memory controller access enablement, doorbell aperture programming, interrupt doorbell ranges, and syshub indirect access.
- `drivers/gpu/drm/amd/amdgpu/soc15.c` includes this header alongside many SOC15 IP headers. That source selects and initializes SOC15-family AMDGPU IP blocks.
- `drivers/gpu/drm/amd/pm/powerplay/hwmgr/smu10_inc.h` includes this header as part of the SMU10 hardware manager register include bundle.

No direct uses of the specific chunk macros were found in the nearby include sites during this pass; many generated default headers are included as shared symbolic catalogs even when only a subset of constants is referenced by handwritten code.

## State And Persistence Behavior

The header stores no mutable state and has no persistence behavior of its own. The macro values represent hardware-visible default/reset state for NBIO-related PCI config and MMIO-visible register blocks. Persistence concerns are therefore external:

- If driver suspend/resume, reset, or firmware handoff code uses these defaults as canonical values, a wrong macro can cause incorrect restore or validation behavior.
- Constants such as PCIe link capability, device control, AER masks/severity, VC resource control/status, and MSI capability defaults describe observable PCI configuration state and may affect enumeration, diagnostics, or error handling if programmed from these values.
- The IOMMU/SMMU ID and control defaults are especially sensitive because they describe translation capability and MMIO behavior exposed to system-level IOMMU paths.

## Dependencies

This chunk depends only on the C preprocessor. It does not include other headers, but it is semantically coupled to generated AMD register metadata:

- `nbio_7_0_offset.h` supplies register offsets and index names.
- `nbio_7_0_sh_mask.h` supplies field masks and shifts.
- `nbio_7_0_smn.h` supplies SMN addressing constants.
- AMDGPU helper macros such as `RREG32_SOC15`, `WREG32_SOC15`, `REG_SET_FIELD`, and `SOC15_REG_OFFSET` in consumer code perform actual register access; this header only supplies literal defaults.

The file is part of an AMDGPU source tree under a larger `sources/distributed-fs/ceph-client` import. Nothing in this chunk is specific to Ceph; it is Linux DRM/AMDGPU hardware-description material.

## Integration Points

The visible hardware integration points are NBIO, PCIe/NBIF, IOMMU L2/SMMU, and SMU10 include aggregation.

Notable register families in this chunk:

- PCI identity/config header fields: vendor ID, device ID, command, status, revision, class code, BARs, ROM base, interrupt line/pin.
- PCIe capability fields: `PCIE_CAP_LIST`, `PCIE_CAP`, device/link capabilities and controls, link status, link capability 2/control 2/status 2.
- MSI/MSI-X capability defaults: capability list pointers, message control/address/data, masks, pending bits.
- PCIe enhanced capabilities: vendor-specific, VC, serial number, AER, TLP prefix logs, secondary PCIe, BAR, power budget, dynamic power allocation, ACS, ATS, page request, PASID, TPH requester, multicast, LTR, ARI, SR-IOV, DPC, RP PIO, and ESM.
- IOMMU/SMMU configuration and identification defaults.
- PCIe lane equalization defaults. Root-complex blocks use `0x00007f0f`; endpoint extended-capability blocks use `0x00007f00`; BIFPLR blocks use `0x00007f7f`.

## Risks And Edge Cases

- Generated-header drift is the dominant risk. These constants must match the silicon register database for NBIO 7.0. Manual edits are risky because a single hex literal can change PCIe/IOMMU capability exposure or reset behavior.
- The unprefixed `cfg*` endpoint-function-0 macro block can collide with other generated config headers if multiple similar headers are included into the same translation unit. The include guard prevents duplicate inclusion of this header, but not macro-name conflicts with other headers.
- Capability-chain values encode offsets and next-capability links. Values such as `0x11000000`, `0x14000000`, `0x20020000`, `0x2a010019`, `0x2b000000`, `0x32800000`, and `0x33000000` are opaque without the paired register layout; accidentally changing them can silently break PCIe enhanced capability traversal.
- Most macros default to `0x00000000`, so meaningful review should focus on non-zero defaults and on block-to-block differences rather than raw macro count.
- The chunk ends in the middle of the `BIFPLR4` address block. Whole-file analysis must merge later chunks to understand the complete `BIFPLR4` block and subsequent NBIO register families.
- Some fields represent writable defaults (`*_W_DEFAULT`) while others represent read-only identification-like values. Consumer code must respect hardware access semantics from the paired mask/offset docs and not infer writability from this file alone.

## Test Signals

Useful validation signals for this chunk are mostly build-time and hardware/driver integration signals:

- Compile AMDGPU/SOC15 code with this header included; macro-name collisions or malformed generated lines should fail compilation.
- Compare generated constants against the authoritative AMD register database or a known-good upstream import for the same ASIC generation.
- Boot/probe AMDGPU hardware using NBIO 7.0/SOC15-era devices and watch for PCIe enumeration, IOMMU, MSI/MSI-X, AER, link-training, and doorbell-related regressions.
- Exercise suspend/resume and GPU reset paths to catch incorrect assumptions about reset/default values.
- Inspect kernel logs for AMDGPU NBIO, PCIe AER, IOMMU/SMMU, and SMU initialization warnings.
- Because this chunk contains no executable code, unit-test coverage is not expected; compile coverage and hardware smoke tests are the relevant checks.

## Cross-Chunk Notes

This is an oversized-file chunk report, not the final per-file research document. Later reconciliation should merge this with reports for the remaining line ranges of `nbio_7_0_default.h`, preserving the complete source path and summarizing all address blocks in the full generated header.
