# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_7_2_0_offset.h lines 28915-31260

## Scope

This chunk is a generated AMDGPU NBIO 7.2.0 register-offset header segment. It contains 2,326 `#define` constants for BIF PCI/PCIe configuration-space register offsets and companion `_BASE_IDX` values. There are no functions, structs, enums, variables, allocations, locks, persistence hooks, or executable control flow in this range.

The range starts inside the `DEV0_EPF6_1` endpoint-function block at `LINK_CAP2`/`LINK_CNTL2`, covers the tail of that function, covers complete blocks for `DEV0_EPF7_1`, `DEV1_EPF0_1`, `DEV1_EPF1_1`, and `DEV2_EPF0_1`, then enters `DEV2_EPF1_1` through `PCIE_HDR_LOG1`. The visible address blocks and base addresses are:

- `nbio_nbif0_bif_cfg_dev0_epf7_bifcfgdecp`, base `0xfffe12107000`.
- `nbio_nbif0_bif_cfg_dev1_epf0_bifcfgdecp`, base `0xfffe12300000`.
- `nbio_nbif0_bif_cfg_dev1_epf1_bifcfgdecp`, base `0xfffe12301000`.
- `nbio_nbif0_bif_cfg_dev2_epf0_bifcfgdecp`, base `0xfffe12500000`.
- `nbio_nbif0_bif_cfg_dev2_epf1_bifcfgdecp`, base `0xfffe12501000`.

Although the repository path is under a `ceph-client` mirror, this file is AMD GPU hardware metadata and has no direct distributed-filesystem behavior.

## Purpose

`nbio_7_2_0_offset.h` is the address half of AMD's generated NBIO 7.2 register interface. Each public macro named `regBIF_CFG_DEV*_EPF*_1_*` maps a PCI/PCIe configuration register name to the encoded NBIO register offset used by AMDGPU register access helpers. Each adjacent `reg..._BASE_IDX` macro identifies the NBIO base-index slot; every macro in this chunk uses base index `5`.

The chunk describes PCIe endpoint-function configuration spaces for devices 0, 1, and 2. The covered registers include standard PCI config header fields, power-management and PCIe capability registers, MSI/MSI-X state, vendor-specific and Advanced Error Reporting capabilities, BAR enhanced capability registers, power-budget and Dynamic Power Allocation registers, ACS/PASID/ARI/TPH metadata, and lane-margining control/status registers for EPF0 blocks.

The generated offsets do not encode field positions, reset defaults, access permissions, register width, write-one-to-clear behavior, or legal programming sequences. Field decoding and composition depend on the matching `nbio_7_2_0_sh_mask.h` header and AMDGPU register helpers.

## Important Macro Families

The `DEV0_EPF6_1` tail starts at PCIe capability version 2 and interrupt capability state: `DEVICE_CAP2`, `DEVICE_CNTL2`, `DEVICE_STATUS2`, `LINK_CAP2`, `LINK_CNTL2`, `LINK_STATUS2`, MSI/MSI-X registers, vendor-specific enhanced capability registers, AER status/mask/severity/log registers, BAR enhanced capability registers, power-budgeting, DPA, ACS, PASID, ARI, and the full `PCIE_TPH_ST_TABLE_0` through `PCIE_TPH_ST_TABLE_63` range. This block is partial because its standard PCI header and early PCIe capability registers are in the preceding chunk.

`DEV0_EPF7_1` and `DEV1_EPF1_1` are complete endpoint-function blocks in this range. They define standard type-0 PCI config registers such as vendor/device IDs, command/status, revision/class-code fields, cache-line/latency/header/BIST, BAR1-BAR6, adapter ID, ROM base, capability pointer, interrupt line/pin, min grant, and max latency. They then repeat the power-management, PCIe capability, MSI/MSI-X, vendor-specific, AER, BAR sizing, power-budget, DPA, ACS, PASID, ARI, and TPH requester table groups.

`DEV1_EPF0_1` and `DEV2_EPF0_1` are larger complete endpoint-function blocks. In addition to the endpoint families above, each includes lane margining support: `MARGINING_PORT_CAP`, `MARGINING_PORT_CNTL`, `MARGINING_PORT_STATUS`, and per-lane `LANE_0` through `LANE_15_MARGINING_LANE_CNTL`/`STATUS`. These registers support PCIe link margining observation/control for each lane and are absent from the smaller EPF1/EPF7 patterns in this slice.

The `DEV2_EPF1_1` block begins at the standard PCI config header and continues through early AER logging: vendor/device IDs, command/status, revision/class-code fields, BARs, capability pointer, PM capability, PCIe device/link capability/control/status registers, MSI/MSI-X, vendor-specific enhanced capability, AER uncorrectable/correctable status and masks, AER capability/control, and `PCIE_HDR_LOG0`/`PCIE_HDR_LOG1`. The block is partial because later AER logs, TLP prefix logs, BAR enhanced capability, power, DPA, ACS/PASID/ARI, and TPH registers continue in a following chunk.

Many register names intentionally share the same offset because they represent adjacent fields in the same PCI configuration dword. Examples include `VENDOR_ID`/`DEVICE_ID`, `COMMAND`/`STATUS`, class-code bytes, `DEVICE_CNTL`/`DEVICE_STATUS`, `LINK_CNTL`/`LINK_STATUS`, MSI address/data aliases, DPA status/control, and ACS/PASID/ARI capability/control pairs. Consumers must use the shift/mask header or PCI config-field helpers to isolate the intended bits.

## APIs, Types, And Functions

There are no callable APIs or C types in this chunk. The public surface is the generated preprocessor namespace:

- `regBIF_CFG_DEVx_EPFy_1_REGISTER` gives the encoded register offset.
- `regBIF_CFG_DEVx_EPFy_1_REGISTER_BASE_IDX` gives the base-index selector, always `5` in this range.

AMDGPU code combines these constants with helpers such as `SOC15_REG_OFFSET`, `RREG32_SOC15`, `WREG32_SOC15`, `RREG32_PCIE_PORT`, `WREG32_PCIE_PORT`, and field helpers driven by `nbio_7_2_0_sh_mask.h`. The direct NBIO 7.2 integration file, `drivers/gpu/drm/amd/amdgpu/nbio_v7_2.c`, includes both this offset header and the matching shift/mask header. DC resource files for DCN 3.0.1 and DCN 3.1 include this offset header for NBIO base/address integration.

## Control Flow

There is no local runtime control flow. Use of the macros follows the generated register-access pattern:

1. Driver code includes `nbio_7_2_0_offset.h` and selects a `reg...` macro for the target NBIO register.
2. It computes the MMIO or PCIe-port address using the base index and SOC15/NBIO access helpers.
3. It reads or writes a raw register value, normally using field positions from `nbio_7_2_0_sh_mask.h` to preserve unrelated bits.
4. Hardware interprets the resulting PCIe configuration, interrupt, error-reporting, link, BAR, power, DPA, isolation, or lane-margining state.

The implied hardware flows include PCI config enumeration, PCIe link training and equalization, MSI/MSI-X routing, AER status logging and masking, BAR sizing, DPA and power budgeting, ACS/PASID/ARI routing and isolation, TPH steering table configuration, and per-lane margining.

## State And Persistence Behavior

The header stores no software state and persists nothing. It names hardware-visible configuration and status registers. The persistence of those registers depends on NBIO reset domains, PCI bus reset, function-level reset, D3hot-to-D0 transitions, suspend/resume save-restore, firmware/BIOS initialization, and explicit AMDGPU or PCI core writes.

The represented state mixes read-only capability data, writable control bits, BAR and interrupt configuration, masks, latched status, diagnostic logs, and live link/lane status. The offset header cannot distinguish safe read-only fields from write-one-to-clear status or side-effectful controls. Code must rely on hardware documentation, PCIe semantics, and the matching shift/mask definitions before using read-modify-write sequences.

## Dependencies And Integration Points

This chunk depends on AMD's generated NBIO 7.2.0 register database. It must stay synchronized with `nbio_7_2_0_sh_mask.h`, which supplies field shifts and masks for these register names, and with any generated default/reset metadata available for this ASIC family.

The direct code integration points are AMDGPU NBIO and display resource code:

- `drivers/gpu/drm/amd/amdgpu/nbio_v7_2.c` includes this header and the matching shift/mask header for NBIO 7.2 access.
- `drivers/gpu/drm/amd/display/dc/resource/dcn301/dcn301_resource.c` includes this header and composes NBIO base-relative register names for display resources.
- `drivers/gpu/drm/amd/display/dc/resource/dcn31/dcn31_resource.c` includes this header for similar DCN 3.1 NBIO address integration.

Semantic dependencies include the PCI and PCI Express specifications for endpoint configuration headers, PM capability, PCIe capability, MSI/MSI-X, AER, ACS, PASID, ARI, TPH requester tables, BAR enhanced capability, power budgeting, Dynamic Power Allocation, and lane margining. The macros are hardware-version-specific; similar names in other NBIO generations should not be substituted without verifying offsets and base indices.

## Risks And Edge Cases

- The range starts and ends inside endpoint-function blocks. Adjacent chunks are required for complete `DEV0_EPF6_1` and `DEV2_EPF1_1` analysis.
- Generated offset drift can compile cleanly while addressing the wrong PCIe config register, especially because the DEV/EPF families are highly repetitive.
- Shared dword offsets are expected, but they are easy to misuse without the matching field masks. Writing one named register can unintentionally change neighboring fields in the same dword.
- All `_BASE_IDX` values in this range are `5`; a wrong base selector would redirect otherwise correct offsets into the wrong NBIO aperture.
- MSI/MSI-X, AER, ACS, PASID, ARI, BAR sizing, DPA, TPH, and lane-margining controls can affect interrupt delivery, error containment, DMA isolation, link stability, power behavior, and performance.
- AER status/log and MSI pending/mask registers may have side effects or clear-on-write semantics. The offset macro alone is not enough to prove a read-modify-write is safe.
- Per-lane margining registers are repeated for lanes 0-15 and share control/status offsets per lane. Off-by-one or copy/paste mistakes can silently test or tune the wrong lane.
- These macros are untyped preprocessor constants, including large encoded offsets. Callers should keep established AMDGPU helper types and avoid ad hoc truncating casts.

## Test Signals

- Build AMDGPU NBIO 7.2 users, especially `amdgpu/nbio_v7_2.c` and DCN 3.0.1/3.1 resource files, to catch missing or renamed generated symbols.
- Run generated-header consistency checks: each `reg...` should have an adjacent `_BASE_IDX`, all base indices in this range should remain `5`, and repeated endpoint-function families should match expected per-device/per-function offset spacing.
- Cross-check register names against `nbio_7_2_0_sh_mask.h` so each offseted register has corresponding field definitions where fields are expected.
- On NBIO 7.2 hardware, compare decoded PCIe config-space state with `lspci -vvxxx`, PCI core dumps, or AMDGPU debug register reads for vendor/device IDs, BARs, PM state, link capabilities/status, MSI/MSI-X, AER, ACS/PASID/ARI, TPH, DPA, power-budget, and lane-margining registers.
- Exercise suspend/resume, PCIe retraining, FLR or GPU reset, MSI/MSI-X enable/disable, AER reporting, BAR sizing, and lane-margining paths to confirm callers use the intended offsets and preserve unrelated fields.
