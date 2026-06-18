# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_7_2_0_offset.h lines 9784-12207

## Purpose

This chunk is an auto-generated AMD NBIO 7.2 register-offset slice for NBIF PCI/PCIe configuration decode blocks. It exports preprocessor constants that map PCI configuration-space register names to NBIO register offsets and `BASE_IDX` selector values. The range starts inside `DEV0_EPF3`, covers complete `DEV0_EPF4` through `DEV0_EPF7` endpoint-function blocks, covers complete `DEV1_EPF0`, and begins `DEV1_EPF1`.

The header does not contain executable code, data structures, or register access helpers. Its role is to give AMDGPU and display code stable symbolic names for hardware offsets that are used with the companion NBIO 7.2 shift/mask header and the driver's register access macros.

## Public Surface In This Chunk

The public API is a dense set of `#define` macros:

- `regBIF_CFG_DEV*_EPF*_0_*` names provide word-oriented NBIO offsets for PCI config registers.
- `regBIF_CFG_DEV*_EPF*_0_*_BASE_IDX` names provide the associated register base index; every macro in this chunk uses base index `5`.

The selected range contains 2,400 `#define` lines. Its address-block boundaries are:

- Continuation of `nbio_nbif0_bif_cfg_dev0_epf3_bifcfgdecp`, whose base address is `0x10143000`; the chunk begins at `DEV0_EPF3` MSI-X, vendor-specific, AER, BAR, power-budget, DPA, ACS, PASID, ARI, TPH requester, and 64-entry TPH steering-table offsets.
- `nbio_nbif0_bif_cfg_dev0_epf4_bifcfgdecp`, base `0x10144000`.
- `nbio_nbif0_bif_cfg_dev0_epf5_bifcfgdecp`, base `0x10145000`.
- `nbio_nbif0_bif_cfg_dev0_epf6_bifcfgdecp`, base `0x10146000`.
- `nbio_nbif0_bif_cfg_dev0_epf7_bifcfgdecp`, base `0x10147000`.
- `nbio_nbif0_bif_cfg_dev1_epf0_bifcfgdecp`, base `0x10148000`.
- Start of `nbio_nbif0_bif_cfg_dev1_epf1_bifcfgdecp`, base `0x10149000`; this chunk ends after the early PM/SBRN/FLADJ offsets.

## Important Register Families

For `DEV0_EPF4` through `DEV0_EPF7`, the complete repeated endpoint-function layout includes standard PCI header offsets such as vendor/device ID, command/status, revision/class-code bytes, BAR1 through BAR6, CardBus CIS pointer, subsystem adapter ID, ROM BAR, capability pointer, interrupt line/pin, min grant, and max latency. Each function then exposes PM capability offsets, PCIe capability offsets, device/link capability and control/status registers, MSI and MSI mapping offsets, MSI-X table/PBA offsets, vendor-specific enhanced capability offsets, AER status/mask/severity/control/header-log/TLP-prefix-log offsets, enhanced BAR capability/control offsets, power-budget and Dynamic Power Allocation offsets, ACS, PASID, ARI, TPH requester capability/control, and TPH steering table entries 0 through 63.

The `DEV1_EPF0` block has the same endpoint-style base PCI, PM, PCIe, MSI/MSI-X, vendor-specific, AER, BAR, power-budget, DPA, ACS, PASID, ARI, and TPH requester coverage. It additionally continues into newer PCIe link feature groups: secondary PCIe capability/list offsets, link capability/control/status 2, lane equalization controls for lanes 0-15, LTR enhanced capability offsets, data-link feature capability/status, 16 GT PHY/link capability/control/status, 16 GT parity mismatch status registers, per-lane 16 GT equalization controls, PCIe lane margining capability/status, and per-lane margining control/status for lanes 0-15.

The `DEV1_EPF1` block begins with the same standard endpoint header sequence, but this chunk only reaches through `SBRN` and `FLADJ`. Its remaining capability families are outside the selected lines and must be described by adjacent chunk research.

Several logical fields intentionally share the same offset because PCI config registers pack multiple fields into one dword or word. Examples in this chunk include vendor/device ID at the same dword, command/status at the same dword, device control/status pairs, link control/status pairs, DPA status/control, ACS capability/control, PASID capability/control, ARI capability/control, paired TPH steering table entries, 16 GT lane equalization groups, and margining lane control/status pairs.

## Control Flow And State

There is no runtime control flow in this header slice. The effective flow is compile-time substitution:

1. AMDGPU or display code includes `nbio/nbio_7_2_0_offset.h`.
2. Code chooses a `regBIF_CFG_*` offset and matching `*_BASE_IDX`.
3. The selected constants are passed to AMD register access helpers or used with companion shift/mask macros from `nbio_7_2_0_sh_mask.h`.
4. Hardware state is read, written, or decoded outside this header.

The header itself stores no state and has no persistence behavior. Persistent and externally visible state lives in GPU NBIO PCI/PCIe configuration registers. Offsets in this range can address configuration state for BAR assignment, command/status bits, power management, MSI/MSI-X routing, PCIe link controls, AER status/masks, ACS isolation, PASID/ARI behavior, TPH requester configuration, power budget/DPA controls, LTR/data-link features, 16 GT link training state, and lane margining status.

## Dependencies And Integration Points

This chunk depends on the generated AMD register-header naming convention. The offset header supplies register addresses and base indices; `nbio_7_2_0_sh_mask.h` supplies field shifts and masks for the same NBIO generation. Consumers must combine these constants with the AMDGPU register access layer and the relevant PCI/PCIe semantic rules; the preprocessor definitions do not enforce valid bit combinations, access sizes, side effects, or sequencing.

Direct include users in this tree include `drivers/gpu/drm/amd/amdgpu/nbio_v7_2.c` and DCN resource files under `drivers/gpu/drm/amd/display/dc/resource/dcn301/` and `dcn31/`. The surrounding AMDGPU code is responsible for selecting the correct NBIO generation, base index, and register access path for the ASIC. The offset names also align with other generated NBIO generation headers, but the repeated shape should not be treated as proof that offsets or capabilities are interchangeable across generations.

The semantic dependencies are the PCI and PCI Express configuration-space layouts for endpoint functions, PM capability, MSI, MSI-X, PCIe capability, AER, enhanced BAR, power budget, Dynamic Power Allocation, ACS, PASID, ARI, TPH requester, LTR, data-link feature, 16 GT PHY/link/equalization, and lane margining capabilities.

## Risks And Maintenance Notes

- The selected lines start and end mid-address-block. `DEV0_EPF3` is incomplete at the start, and `DEV1_EPF1` is incomplete at the end, so adjacent chunks are required for full per-file reconciliation.
- These generated offsets must match the exact NBIO 7.2 hardware register map. A stale or transposed offset can make driver code read the wrong PCI config dword or program the wrong endpoint function.
- The large repeated `DEV0_EPF4`-`DEV0_EPF7` blocks are review-hostile: most lines differ only by function number and offset stride. Generator drift or a single missing capability can be easy to miss.
- Many registers addressed by these macros have hardware side effects or strict access rules. Status registers may be write-one-to-clear, link controls may retrain or disable links, MSI/MSI-X controls affect interrupt delivery, and ACS/PASID/ARI settings affect isolation and addressing behavior.
- Shared-offset aliases are expected for packed PCI config fields. Consumers must use the matching shift/mask constants and access width rather than assuming each macro names a distinct storage location.
- Base index `5` is part of the generated addressing contract. Using the offset with the wrong base index or SOC register aperture can target unrelated registers.
- `DEV1_EPF0` includes 16 GT and lane margining offsets that can affect high-speed link characterization and training. Debug or test code that writes these offsets without hardware-specific sequencing risks link instability.

## Test Signals

Useful validation signals for this chunk are:

- Compile coverage for `amdgpu/nbio_v7_2.c` and DCN resource translation units that include `nbio_7_2_0_offset.h`.
- Static generated-header checks that every `regBIF_CFG_*` macro in this range has a corresponding `*_BASE_IDX` macro and that all base indices remain `5`.
- Cross-header checks that offsets here have matching field definitions in `nbio_7_2_0_sh_mask.h` for registers whose bitfields are consumed by driver code.
- Register-map sanity checks that `DEV0_EPF4` through `DEV0_EPF7` advance in the expected `0x400` offset stride and that `DEV1_EPF0`/`DEV1_EPF1` begin at `0x12000`/`0x12400`.
- Hardware dump comparison on NBIO 7.2 ASICs using AMDGPU debug register reads and PCI config-space tools such as `lspci -vvxxx`, especially for vendor/device IDs, BAR layout, capability pointers, MSI/MSI-X state, AER capability, ACS/PASID/ARI capability presence, TPH tables, LTR/data-link features, 16 GT link status, and margining capability/status.
- Error and link-management tests that exercise AER reporting, MSI/MSI-X delivery, link speed negotiation, 16 GT equalization, lane margining reads, and power-management capability decoding without touching unrelated endpoint functions.
