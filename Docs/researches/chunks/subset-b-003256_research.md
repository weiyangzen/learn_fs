# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_7_7_0_offset.h lines 24300-26645

## Purpose

This chunk is an auto-generated AMD NBIO 7.7.0 register-offset slice for PCI/PCIe configuration-space registers exposed through NBIO BIF configuration decode blocks. It contains no executable code. Its job is to publish preprocessor constants that map AMDGPU register names to NBIO register addresses and base-index selectors for root-complex ports and endpoint functions.

The selected range begins in the middle of the `DEV0_RC1` root-complex block at PCIe vendor-specific and virtual-channel registers, then covers complete `DEV1_RC1` and `DEV2_RC1` root-complex blocks. It also covers complete `DEV0_EPF0_1` and `DEV0_EPF1_1` endpoint-function blocks, and ends in the early portion of the `DEV0_EPF2_1` block at `PCIE_VENDOR_SPECIFIC1`. Adjacent chunks are required for the beginning of `DEV0_RC1` and the remainder of `DEV0_EPF2_1`.

## Public Surface In This Chunk

The public surface is 2,326 `#define` macros in the assigned range: 1,163 register-address macros and 1,163 matching `_BASE_IDX` macros. Every register address macro in this chunk has a companion base-index macro with value `5`, which tells the AMDGPU register helpers which SOC15/NBIO base aperture to use when resolving the generated address.

Macro prefixes identify the logical PCI function or port:

- `regBIF_CFG_DEV0_RC1_*` covers the tail of the first root-complex block in this range.
- `regBIF_CFG_DEV1_RC1_*` and `regBIF_CFG_DEV2_RC1_*` cover two complete root-complex PCI/PCIe configuration maps.
- `regBIF_CFG_DEV0_EPF0_1_*`, `regBIF_CFG_DEV0_EPF1_1_*`, and `regBIF_CFG_DEV0_EPF2_1_*` cover endpoint-function configuration maps under device 0.

There are no functions, structs, enums, storage objects, or inline helpers. The API contract is the exact macro spelling and numeric value. Consumers are expected to pair these offsets with field definitions from `nbio_7_7_0_sh_mask.h` and with AMDGPU's generated-register access helpers.

## Register Coverage

The chunk has five explicit address-block markers:

- `nbio_nbif0_bif_cfg_dev1_rc_bifcfgdecp`, base address `0xfffe00042000`, with 185 register offsets from `regBIF_CFG_DEV1_RC1_VENDOR_ID` through `regBIF_CFG_DEV1_RC1_LANE_15_MARGINING_LANE_STATUS`.
- `nbio_nbif0_bif_cfg_dev2_rc_bifcfgdecp`, base address `0xfffe00043000`, with 185 register offsets from `regBIF_CFG_DEV2_RC1_VENDOR_ID` through `regBIF_CFG_DEV2_RC1_LANE_15_MARGINING_LANE_STATUS`.
- `nbio_nbif0_bif_cfg_dev0_epf0_bifcfgdecp`, base address `0xfffe12100000`, with 348 register offsets from `regBIF_CFG_DEV0_EPF0_1_VENDOR_ID` through `regBIF_CFG_DEV0_EPF0_1_PCIE_VENDOR_SPECIFIC_HDR_GPUIOV_UVD1SCH_DW8`.
- `nbio_nbif0_bif_cfg_dev0_epf1_bifcfgdecp`, base address `0xfffe12101000`, with 256 register offsets from `regBIF_CFG_DEV0_EPF1_1_VENDOR_ID` through `regBIF_CFG_DEV0_EPF1_1_PCIE_VF_RESIZE_BAR6_CNTL`.
- `nbio_nbif0_bif_cfg_dev0_epf2_bifcfgdecp`, base address `0xfffe12102000`, beginning here with 71 register offsets from `regBIF_CFG_DEV0_EPF2_1_VENDOR_ID` through `regBIF_CFG_DEV0_EPF2_1_PCIE_VENDOR_SPECIFIC1`.

The chunk also includes 118 tail offsets for `DEV0_RC1`, starting at `regBIF_CFG_DEV0_RC1_PCIE_VENDOR_SPECIFIC_HDR` and ending at `regBIF_CFG_DEV0_RC1_LANE_15_MARGINING_LANE_STATUS`. That root-complex block begins before this chunk, so identity, bridge-window, MSI, SSID, and MSI-map definitions for `DEV0_RC1` are only visible in the previous range.

Root-complex coverage includes conventional PCI header fields, bridge-window registers, bridge interrupt/control registers, power-management capability registers, PCIe capability and link registers, MSI and SSID/MSI-map capability offsets, vendor-specific extended capability offsets, virtual-channel resources, device serial number, Advanced Error Reporting, secondary PCIe capability, lane equalization, Access Control Services, Data Link Feature capability, 16 GT/s PHY capability, and PCIe lane margining registers.

Endpoint-function coverage includes conventional PCI header fields, BAR registers, capability pointer and interrupt bytes, vendor/adapter capability offsets, power-management capability offsets, SBRN/FLADJ/DBESL, PCIe device/link capability and control/status registers, MSI/MSI-X capability offsets, SATA capability/index/data offsets, vendor-specific extended capability offsets, Advanced Error Reporting and TLP logs, BAR enhanced capability offsets, SR-IOV capability and VF BAR controls, Address Translation Service and Page Request Interface registers, Process Address Space ID capability/control, data-link and 16 GT/s PHY capability registers, lane margining controls/statuses, and resizable VF BAR capabilities. `EPF0` additionally exposes a large GPU I/O virtualization vendor-specific register area, including VF framebuffer base/limit, device ID, FLR, doorbell, MMIO, and scheduling dword registers.

## Important Macro Patterns

Many macro names intentionally alias the same register dword because PCI configuration space packs multiple fields into one address. Examples include `VENDOR_ID` and `DEVICE_ID` sharing offset `...0000`, `COMMAND` and `STATUS` sharing `...0001`, class-code bytes sharing `...0002`, and interrupt/min-grant/max-latency fields sharing `...000f` in endpoint blocks. Similar aliases appear for `DEVICE_CNTL`/`DEVICE_STATUS`, `LINK_CNTL`/`LINK_STATUS`, `MSI_CAP_LIST`/`MSI_MSG_CNTL`, MSI 32-bit versus 64-bit data/mask/pending forms, `MSIX_CAP_LIST`/`MSIX_MSG_CNTL`, and lane control/status pairs.

The root-complex blocks use address ranges beginning with `0x3fff7bfd...`, while endpoint-function blocks use `0x3fff8080...`. The `_BASE_IDX` value remains `5` across all macros, so the changing high address bits and generated names are the main distinction between ports/functions within this chunk.

## Control Flow And State

There is no runtime control flow in this header. The effective flow is compile-time substitution:

1. A translation unit includes `nbio/nbio_7_7_0_offset.h`, usually with `nbio/nbio_7_7_0_sh_mask.h`.
2. Driver code chooses an offset macro such as `regBIF_CFG_DEV0_EPF0_1_PCIE_VENDOR_SPECIFIC_HDR_GPUIOV_VF0_FB`.
3. AMDGPU register helpers combine the generated register offset, the `_BASE_IDX` selector, and any shift/mask constants from the companion header.
4. Actual reads, writes, polling, error handling, or capability programming happen in AMDGPU NBIO, PCIe, RAS, interrupt, virtualization, or power-management code outside this generated header.

The header stores no software state and persists nothing by itself. Persistent state lives in hardware registers, PCI/PCIe configuration space, firmware-managed NBIO state, or platform PCI enumeration state. Some registers are writable controls that persist until reset, FLR, link reset, power transition, or driver reinitialization. Others are hardware-updated status, sticky error, log, or write-one-to-clear registers whose side effects are defined by PCIe and AMD hardware documentation, not by this offset header.

## Dependencies And Integration Points

The primary direct integration point is `drivers/gpu/drm/amd/amdgpu/nbio_v7_7.c`, which includes both `nbio_7_7_0_offset.h` and `nbio_7_7_0_sh_mask.h` and provides the `nbio_v7_7_funcs` implementation. That implementation wires NBIO register access into AMDGPU through callbacks for HDP flush offsets, PCIe index/data offsets, PCIe port index/data offsets, revision ID, memory-controller access, doorbell apertures, interrupt-handler doorbell ranges, clock gating, light sleep, initialization, HDP register remapping, and register remap setup.

`drivers/gpu/drm/amd/amdgpu/nbio_v7_7.h` exports `nbio_v7_7_hdp_flush_reg`, `nbio_v7_7_funcs`, and `nbio_v7_7_ras_funcs`. `drivers/gpu/drm/amd/amdgpu/amdgpu_discovery.c` selects these NBIO 7.7 functions for matching discovered IP versions. The generated constants in this chunk are therefore part of the hardware contract used after ASIC discovery chooses the NBIO 7.7 backend.

Semantic dependencies include the PCI and PCI Express configuration-space specifications, MSI/MSI-X, AER, ACS, ATS, PRI, PASID, SR-IOV, resizable BAR, PCIe 16 GT/s equalization and lane margining, and AMD's NBIO 7.7.0 register database. The header does not encode reset values, access permissions, ownership rules, firmware arbitration, register-lock sequencing, or whether every register is valid on every NBIO 7.7 ASIC.

## Risks And Maintenance Notes

- This range is chunked across logical blocks. `DEV0_RC1` starts before this range, and `DEV0_EPF2_1` continues after it, so isolated analysis must not treat either as complete.
- Repetition across `DEV1_RC1`, `DEV2_RC1`, `EPF0`, `EPF1`, and `EPF2` makes prefix mistakes the main practical risk. A wrong `DEV*` or `EPF*` macro can compile cleanly while targeting a different PCI function or port.
- Overlapping address aliases are intentional. Consumers must use companion shift/mask definitions to access the intended field and must not assume each macro names a distinct dword.
- Root-complex AER, ACS, virtual-channel, link equalization, 16 GT/s, and lane-margining offsets are hardware-control and diagnostics surfaces. Incorrect writes can hide PCIe errors, alter link training behavior, or disrupt link health reporting.
- Endpoint MSI/MSI-X and SR-IOV offsets are virtualization-sensitive. Misprogramming can affect interrupt delivery, VF BAR layout, VF enumeration, FLR handling, doorbells, MMIO aperture exposure, and GPU I/O virtualization scheduling state.
- ATS, PRI, and PASID offsets interact with IOMMU and process-address-space policy. Enabling or decoding them incorrectly can affect translation, isolation, and page-request behavior.
- GPUIOV vendor-specific offsets in `EPF0` are AMD-specific and not self-describing. They should be modified only by code paths that understand firmware and virtualization ownership.
- Generated addresses and `_BASE_IDX` values must remain synchronized with `nbio_7_7_0_sh_mask.h` and the upstream register database; hand edits are high risk.

## Test Signals

Useful validation signals for this chunk are:

- Build coverage for NBIO 7.7 include sites, especially `amdgpu/nbio_v7_7.c` and discovery paths that select `nbio_v7_7_funcs`.
- Generated-header comparison against AMD's authoritative NBIO 7.7.0 register database, with special attention to the repeated `DEV1_RC1`/`DEV2_RC1` and `EPF0`/`EPF1`/`EPF2` blocks.
- Cross-header checks that every register in this chunk has a matching `_BASE_IDX` and compatible field definitions in `nbio_7_7_0_sh_mask.h`.
- Static checks that duplicated numeric offsets are expected PCI config aliases rather than accidental copy/paste errors.
- Hardware or simulator PCI config-space dumps compared against the generated offsets for root-complex ports and endpoint functions.
- PCIe link validation around AER, ACS, equalization, 16 GT/s capability, and lane margining registers.
- SR-IOV and GPU I/O virtualization tests that enumerate VFs, exercise FLR, verify VF BAR and resizable VF BAR state, validate GPUIOV framebuffer/doorbell/MMIO registers, and confirm MSI/MSI-X delivery remains stable.
- IOMMU-backed virtualization tests for ATS, PRI, and PASID enablement and teardown, including reset and power-transition coverage.
