# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_7_7_0_offset.h lines 29001-29660

## Purpose

This chunk is the final slice of AMDGPU's generated NBIO 7.7 offset header. It defines preprocessor constants for NBIF/BIF PCIe configuration-space register addresses in device 2 endpoint-function blocks. The macros are register-map data only: they do not implement Ceph, distributed filesystem behavior, or executable AMDGPU control logic.

The range starts mid-block with the tail of `BIF_CFG_DEV2_EPF0_1`, covers a complete `nbio_nbif0_bif_cfg_dev2_epf1_bifcfgdecp` address block, then covers `nbio_nbif0_bif_cfg_dev2_epf2_bifcfgdecp` through ARI control and the file's closing include guard. The EPF1 block base comment is `0xfffe12501000`; the EPF2 block base comment is `0xfffe12502000`. The visible encoded register values are `0x3fff8090....` SOC15-style register identifiers, and every visible `_BASE_IDX` macro in the chunk has value `5`.

## Important APIs, Types, and Macros

There are no functions, structs, typedefs, enums, or storage objects in this chunk. The public API is the exact generated macro names and numeric constants:

- `regBIF_CFG_DEV2_EPF0_1_*` tail macros for the end of EPF0's PCIe extended capabilities.
- `regBIF_CFG_DEV2_EPF1_1_*` address macros for a complete endpoint-function PCI configuration image.
- `regBIF_CFG_DEV2_EPF2_1_*` address macros for another endpoint-function PCI configuration image, ending at ARI control.
- Matching `*_BASE_IDX` macros, all `5`, which select the NBIO register-base table entry expected by AMDGPU's SOC15 register helpers.

The assigned range contains 660 source lines and 649 `#define` entries: 324 register-address macros plus 325 `_BASE_IDX` macros. The count is uneven because line 29001 is only the base-index companion for an EPF0 lane-7 equalization register whose address appears in the previous chunk.

Important macro groups include:

- EPF0 tail: lane 8-15 equalization control, ACS, PASID, LTR, ARI, data-link feature capability/status, 16 GT/s PHY/link controls, parity mismatch status, 16 GT/s lane equalization controls, and lane margining controls/status for lanes 0-15.
- EPF1 conventional PCI header: vendor/device ID, command/status, revision and class code bytes, cache-line/latency/header/BIST, BAR1-BAR6, CardBus CIS pointer, adapter ID, ROM BAR, capability pointer, interrupt line/pin, min grant, and max latency.
- EPF1 capabilities: vendor capability, PCI power management, PCIe capability, device/link capability-control-status sets, device/link capability 2, MSI, MSI-X, vendor-specific enhanced capability, Advanced Error Reporting, BAR enhanced capability, power budget, DPA, ACS, PASID, and ARI.
- EPF2 mirrors the EPF1 layout from vendor/device ID through ARI control, with the same register spacing shifted from the `0x3fff809004xx` range to `0x3fff809008xx`.

Several names intentionally share the same encoded register value because multiple PCI config fields occupy different bit slices of the same 32-bit dword. Examples include `VENDOR_ID` and `DEVICE_ID`, `COMMAND` and `STATUS`, class-code bytes, MSI 32-bit versus 64-bit forms, `DPA_STATUS` and `DPA_CNTL`, ACS cap/control, PASID cap/control, and ARI cap/control.

## Control Flow and Runtime Behavior

This header has no runtime control flow. Its effective flow is compile-time substitution:

1. `amdgpu/nbio_v7_7.c` includes `nbio/nbio_7_7_0_offset.h` and the matching `nbio/nbio_7_7_0_sh_mask.h`.
2. Driver code passes `reg...` constants into SOC15/NBIO register helpers such as `SOC15_REG_OFFSET`, `RREG32_SOC15`, `WREG32_SOC15`, or related PCIe-port accessors.
3. When a register value needs bitfield interpretation or modification, the caller uses the same register prefix in `nbio_7_7_0_sh_mask.h` for field shifts and masks.
4. Hardware performs the actual PCIe configuration, capability-chain, status, interrupt, link, and error-reporting behavior.

The specific EPF1/EPF2 macros in this chunk are not directly referenced by C files in the current tree beyond inclusion of the whole generated header. They remain part of the exported ASIC register surface for generated-code compatibility, diagnostics, platform bring-up, and future call sites.

## State and Persistence

The chunk stores no software state, allocates no memory, performs no I/O, and persists nothing by itself. It names hardware state in NBIO-backed PCIe configuration registers.

State represented by these offsets includes:

- Endpoint identity and enumeration-visible configuration: vendor/device IDs, class code, command/status, BARs, ROM BAR, capability pointer, and interrupt routing fields.
- PCIe link and device policy: device control/status, link control/status, target speeds, completion timeout behavior, atomic operation capabilities, LTR/OBFF-related policy where represented in paired masks, and 16 GT/s link/equalization state.
- Interrupt configuration: MSI and MSI-X message control, address/data, mask, pending, table, and PBA registers.
- Error and diagnostic state: AER uncorrectable/correctable status, masks, severity, capability/control, header logs, TLP prefix logs, data-link feature status, parity mismatch status, lane equalization, and lane margining.
- Virtualization and isolation-adjacent capability state: ACS controls, PASID capability/control, ARI capability/control, and DPA/power-budget fields.

Persistence rules are hardware-defined, not encoded here. Some registers are writable configuration state that may survive until reset, FLR, link reset, suspend/resume, BACO, or driver reinitialization. Others are hardware-updated status, sticky error, log, or write-one-to-clear fields whose clear and side-effect behavior must be derived from PCIe and AMD NBIO documentation.

## Dependencies and Integration Points

The direct companion is `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_7_7_0_sh_mask.h`, which supplies field-level `__SHIFT` and `_MASK` definitions for the same register names. These offset and mask headers must stay synchronized by ASIC generation; mixing NBIO 7.7 offsets with another generation's masks can compile cleanly while targeting the wrong address or field.

The main C integration point in this tree is `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/nbio_v7_7.c`, which includes this offset header and uses generated NBIO constants through AMDGPU SOC15 register access macros. That file demonstrates the intended access pattern for the generated constants, even though its active call sites mostly use other NBIO 7.7 registers outside this particular chunk.

Semantic dependencies include the PCI and PCI Express configuration-space layouts, MSI/MSI-X capability formats, AER, ACS, PASID, ARI, data-link feature capability, PCIe 4.0 16 GT/s PHY/equalization registers, lane margining, AMD's SOC15 register-indexing scheme, and AMD's generated NBIO 7.7 register database.

## Risks and Maintenance Notes

- The range starts at a chunk boundary with only `regBIF_CFG_DEV2_EPF0_1_PCIE_LANE_7_EQUALIZATION_CNTL_BASE_IDX`; the matching address macro is in the previous chunk.
- Repeated EPF layouts are easy to cross-wire. An EPF1 macro and EPF2 macro can differ only by prefix and address stride, so prefix mistakes may compile while reading or writing the wrong endpoint-function image.
- Overlapping dword aliases are intentional. Consumers must pair each offset with the correct field masks and access width rather than assuming each macro names a distinct 32-bit register.
- `_BASE_IDX` value `5` is part of the register-address contract. A wrong base index can route SOC15 accessors to the wrong NBIO aperture even if the encoded address literal looks correct.
- MSI/MSI-X, ACS, PASID, and ARI registers affect interrupts, DMA isolation, process address spaces, and function routing. Incorrect programming can create reliability or isolation failures.
- AER and TLP log offsets are diagnostic-sensitive. Misaddressing status/mask/severity/log registers can suppress errors, misclassify PCIe faults, or attribute logs to the wrong function.
- Link equalization, 16 GT/s status, and lane margining registers are lane-numbered and repetitive; off-by-one lane use can make bring-up or debug tooling tune the wrong lane.
- This is a generated header with no type safety, reset values, access permissions, ordering requirements, or firmware-ownership metadata.

## Test and Validation Signals

Useful validation signals for this chunk are:

- Compile AMDGPU code paths that include `nbio_7_7_0_offset.h`, especially `amdgpu/nbio_v7_7.c`, to catch syntax, guard, or duplicate-definition breakage.
- Cross-check every visible `regBIF_CFG_DEV2_EPF1_1_*` and `regBIF_CFG_DEV2_EPF2_1_*` address macro against a matching shift/mask register block in `nbio_7_7_0_sh_mask.h`.
- Run generated-header consistency checks that each address macro has a matching `_BASE_IDX` with value `5`, accounting for the first line's chunk-boundary exception.
- Compare EPF1 and EPF2 macro sets mechanically: the register names should mirror each other while the encoded addresses should advance by the expected `0x400` dword stride.
- Compare this NBIO 7.7 block against AMD's authoritative register database and against nearby NBIO generation headers only as a sanity signal, not as a substitute for ASIC-specific data.
- On supported hardware or simulation, read PCI config-space dumps for device 2 EPF1/EPF2 and verify identity, BAR, capability chain, PCIe, MSI/MSI-X, AER, ACS, PASID, and ARI offsets decode as expected.
- Exercise PCIe error observation where possible and confirm AER status/mask/severity/header-log/TLP-prefix-log offsets map to the intended endpoint function.
- Validate link training, 16 GT/s equalization, and lane margining tooling against the EPF0 tail offsets, checking that lane-numbered accesses target the expected physical/logical lanes.

## Chunk Boundary Notes

Lines 29001-29161 finish `BIF_CFG_DEV2_EPF0_1` from the lane-equalization tail through ACS, PASID, LTR, ARI, data-link feature, 16 GT/s PHY/link, parity mismatch, 16 GT/s lane equalization, and lane margining registers.

Lines 29164-29409 define the complete `nbio_nbif0_bif_cfg_dev2_epf1_bifcfgdecp` block from `VENDOR_ID` through `PCIE_ARI_CNTL`.

Lines 29412-29657 define `nbio_nbif0_bif_cfg_dev2_epf2_bifcfgdecp` from `VENDOR_ID` through `PCIE_ARI_CNTL`. Lines 29659-29660 close the file's include guard.
