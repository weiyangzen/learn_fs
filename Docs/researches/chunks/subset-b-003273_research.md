# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_7_7_0_sh_mask.h lines 34403-36864

## Purpose

This chunk is part of AMDGPU's generated NBIO 7.7.0 shift/mask header. It contains C preprocessor constants for decoding and composing fields in NBIO/BIF PCIe configuration, BIF system, GFX MMIO remap CAM, and RCC strap registers. The companion offset header selects a register address; this header selects bit positions within that register value.

The assigned range has 2,462 source lines, 2,138 `#define` entries, and four visible address-block comments. It is not executable code and has no Ceph or distributed-filesystem behavior despite its mirrored source-tree location. Its value is as a hardware ABI contract between AMDGPU NBIO 7.7.0 code and generated AMD register metadata.

At a high level, the range covers:

- The tail of `BIF_CFG_DEV1_RC0`, beginning inside lane 4 8 GT/s equalization fields, then ACS, Data Link Feature, 16 GT/s PHY/link status, per-lane 16 GT/s equalization, and PCIe lane margining fields.
- A large `nbio_nbif0_bif_cfg_dev2_rc_bifcfgdecp` block for `BIF_CFG_DEV2_RC0`, including conventional PCI bridge header fields, bridge windows, PM/PCIe/MSI/SSID/vendor-specific/VC capabilities, AER and root-error reporting, secondary PCIe capability, lane equalization, ACS, DLF, 16 GT/s PHY, and lane margining.
- `nbio_nbif0_bif_bx_pf_SYSPFVFDEC` and `nbio_nbif0_bif_bx_SYSDEC` fields for PF1 indirect MMIO access, BIF_BX1 PCIe index/data windows, SBIOS/BIOS scratch registers, RLC/VCE/UVD interrupt controls, and GFX MMIO register remap CAM entries.
- The beginning of `nbio_nbif0_rcc_strap_BIFDEC1:1`, including `RCC_STRAP1_RCC_BIF_STRAP0` and the start of `RCC_STRAP1_RCC_BIF_STRAP1`.

## Important APIs, Types, and Macros

There are no functions, structs, typedefs, enums, or storage objects in this chunk. The public surface is only generated macros with the convention:

- `<REGISTER>__<FIELD>__SHIFT` gives the field's bit offset.
- `<REGISTER>__<FIELD>_MASK` gives the field's unshifted mask in the register value.

Important macro families in this chunk include:

- `BIF_CFG_DEV1_RC0_PCIE_LANE_4_EQUALIZATION_CNTL` through `...LANE_15_EQUALIZATION_CNTL`: 8 GT/s downstream/upstream TX preset and RX preset hint fields for lanes 4-15. The chunk starts at the first lane 4 shift definition; the lane 4 register comment is on the previous source line outside this chunk.
- `BIF_CFG_DEV1_RC0_PCIE_ACS_*`: Access Control Services capability/control fields for source validation, translation blocking, peer-to-peer request/completion redirects, upstream forwarding, egress control, direct translated P2P, and egress-control vector size.
- `BIF_CFG_DEV1_RC0_DATA_LINK_FEATURE_*`, `...PCIE_PHY_16GT_*`, `...LINK_STATUS_16GT`, `...LANE_*_EQUALIZATION_CNTL_16GT`, and `...LANE_*_MARGINING_*`: PCIe DLF negotiation, 16 GT/s equalization status, 16 GT/s per-lane preset fields, and lane margining control/status payloads.
- `BIF_CFG_DEV2_RC0_VENDOR_ID` through `BIF_CFG_DEV2_RC0_ROOT_STATUS`: conventional PCI-to-PCI bridge configuration fields, including command/status bits, class/revision/header/BIST, BARs, primary/secondary/subordinate bus numbers, I/O and memory windows, interrupt and bridge controls, PM capability, PCIe device/link/slot/root capability and control/status fields.
- `BIF_CFG_DEV2_RC0_DEVICE_CAP2`, `DEVICE_CNTL2`, `LINK_CAP2`, `LINK_CNTL2`, and `LINK_STATUS2`: PCIe capability 2 fields such as completion timeout ranges/control, atomic operations, OBFF, LTR, TPH completer support, emergency power reduction, 10-bit tags, link speed vector, target speed, hardware autonomous speed disable, equalization completion/phase status, and de-emphasis/current speed reporting.
- `BIF_CFG_DEV2_RC0_MSI_*`, `SSID_*`, `MSI_MAP_*`, `PCIE_VENDOR_SPECIFIC*`, and `PCIE_VC*`: MSI control/address/data fields, subsystem identity capability, MSI mapping capability, vendor-specific extended capability headers, and virtual-channel capability/resource control/status fields.
- `BIF_CFG_DEV2_RC0_PCIE_UNCORR_ERR_*`, `PCIE_CORR_ERR_*`, `PCIE_ADV_ERR_CAP_CNTL`, `PCIE_HDR_LOG*`, `PCIE_ROOT_ERR_*`, `PCIE_ERR_SRC_ID`, and `PCIE_TLP_PREFIX_LOG*`: Advanced Error Reporting fields for error status, masks, severity, ECRC controls, captured TLP headers/prefixes, root-error reporting, and error source IDs.
- `BIF_CFG_DEV2_RC0_PCIE_SECONDARY_*`, `PCIE_LINK_CNTL3`, `PCIE_LANE_ERROR_STATUS`, per-lane 8 GT/s equalization, ACS, DLF, 16 GT/s status/equalization, and lane margining: link training, diagnostics, isolation, and margining fields for the DEV2 root-complex port.
- `BIF_BX_PF1_MM_INDEX`, `BIF_BX_PF1_MM_DATA`, and `BIF_BX_PF1_MM_INDEX_HI`: PF1 indirect MMIO index/data register fields, with index auto-increment and high-address support.
- `BIF_BX1_PCIE_INDEX`, `BIF_BX1_PCIE_DATA`, `BIF_BX1_PCIE_INDEX2`, and `BIF_BX1_PCIE_DATA2`: BIF_BX1 PCIe indirect index/data windows used by NBIO access paths.
- `BIF_BX1_SBIOS_SCRATCH_*` and `BIF_BX1_BIOS_SCRATCH_*`: 32-bit scratch registers used for firmware/BIOS/driver handoff state.
- `BIF_BX1_BIF_RLC_INTR_CNTL`, `BIF_BX1_BIF_VCE_INTR_CNTL`, and `BIF_BX1_BIF_UVD_INTR_CNTL`: interrupt-control bits for command completion, self-recovered hang, FLR-needed hang, VM-busy transition, and UVD instance selection.
- `BIF_BX1_GFX_MMIOREG_CAM_ADDR*`, `...REMAP_ADDR*`, `...CAM_CNTL`, `...ZERO_CPL`, `...ONE_CPL`, and `...PROGRAMMABLE_CPL`: GFX MMIO register remap CAM address/remap/enable/completion fields.
- `RCC_STRAP1_RCC_BIF_STRAP0` and partial `RCC_STRAP1_RCC_BIF_STRAP1`: strap fields controlling PCIe generation disable/kill, VGA/BIOS ROM exposure, memory aperture sizing, error-ignore policy, PME compliance, link-down reset, fuses/ROM validity, write disable, ECRC behavior, margining support/ready state, SWUS aperture configuration, DLF/16 GT/s/margining enablement, slot power support, LTR mode, and AP enablement. The chunk ends before all `RCC_BIF_STRAP1` mask macros are present.

## Control Flow and Runtime Behavior

This header has no runtime control flow. Runtime behavior is implied by how AMDGPU includes and uses the generated constants:

1. NBIO 7.7.0 code includes `nbio_7_7_0_offset.h` and `nbio_7_7_0_sh_mask.h`.
2. A caller selects an offset macro from the offset header and a field name from this shift/mask header.
3. Register helper macros such as field get/set helpers combine a read value with `__SHIFT` and `_MASK` definitions.
4. The actual side effects happen in MMIO, PCIe config, SMN, or indirect BIF access paths outside this generated header.

The directly visible include site is `drivers/gpu/drm/amd/amdgpu/nbio_v7_7.c`, which uses the generated NBIO 7.7.0 offset and shift/mask headers to implement the NBIO backend selected for matching ASICs. This particular chunk mostly supplies field-level definitions for PCIe root-complex configuration, link diagnostics, AER, lane margining, scratch, interrupt, CAM, and strap surfaces rather than implementing the access sequence itself.

## State and Persistence

The file owns no mutable software state, allocates no memory, performs no I/O, and persists nothing. It describes bitfields in hardware state.

State addressed through these fields lives in PCI/PCIe configuration images, NBIO/BIF internal registers, firmware scratch registers, and strap registers. Some fields describe static or firmware-seeded identity/capability values, such as vendor/device IDs, class codes, capability IDs, supported PCIe speeds/features, ACS/DLF/16 GT/s capabilities, VC resources, and strap-derived feature enables. Other fields are live control or status state, such as command bits, bridge windows, PM state, PCIe link control/status, MSI controls, AER status/masks/severity/logs, root-error status/source IDs, lane error/equalization/margining status, scratch registers, interrupt control bits, CAM enable/address/remap values, and strap validity/write-disable fields.

Persistence is hardware-defined. Some values reset on conventional reset, FLR, link reset, BACO, D3hot/D0 transition, or GPU reset; others may be sticky status, firmware-initialized strap state, or BIOS/driver handoff state. This header does not encode access permissions, reset values, write-one-to-clear behavior, lock sequencing, or ownership rules.

## Dependencies and Integration Points

The direct dependency is synchronization with the generated NBIO 7.7.0 offset header and AMD's authoritative register database:

- `nbio_7_7_0_offset.h` supplies matching register offsets and `_BASE_IDX` values.
- AMDGPU register helpers and `REG_GET_FIELD`/`REG_SET_FIELD` style macros depend on exact `REGISTER__FIELD__SHIFT` and `REGISTER__FIELD_MASK` spellings.
- `amdgpu/nbio_v7_7.c` includes this header with the offset header and wires NBIO 7.7.0 register access into the AMDGPU driver.

Integration areas include PCIe root-complex enumeration/configuration for DEV1/DEV2 RC0, bridge aperture programming, PM capability handling, MSI setup, PCIe link training/equalization, 16 GT/s status diagnostics, lane margining, ACS isolation policy, DLF negotiation, virtual-channel management, AER/root-error handling, firmware scratch handoff, BIF client interrupt reporting for RLC/VCE/UVD, indirect PCIe/MMIO access, GFX MMIO remap CAM programming, and RCC strap interpretation.

This chunk is field-level metadata only. Consumers must combine these masks with the right register offset, use read-modify-write for packed registers, and respect ownership of PCIe config space, firmware-managed scratch registers, and strap-derived state.

## Risks

- The assigned range starts and ends mid-register-definition context. It starts after the `BIF_CFG_DEV1_RC0_PCIE_LANE_4_EQUALIZATION_CNTL` comment and ends in the middle of `RCC_STRAP1_RCC_BIF_STRAP1` masks. Merge/reconciliation must include adjacent chunks before judging register completeness.
- A wrong shift or mask silently corrupts field extraction or read-modify-write composition. Because many registers are control registers, the result can alter PCIe command bits, bridge windows, MSI state, AER masking/severity, ACS isolation, link training, or margining behavior.
- DEV1 and DEV2 RC0 fields are highly repetitive across lanes and capability blocks. Copy/paste or generated-name drift can compile cleanly while targeting the wrong port, lane, or field.
- Packed PCIe config dwords intentionally contain many aliases, such as command/status, device control/status, link control/status, MSI control/address/data aliases, AER status/mask/severity, and lane control/status pairs. Callers must preserve unrelated bits and use the correct field macro for the register view they are modifying.
- Status and log registers may be sticky, write-one-to-clear, or otherwise side-effectful. This header gives bit positions only and does not identify destructive reads, clear-on-write behavior, or firmware-owned bits.
- AER, ACS, DLF, 16 GT/s, and lane-margining controls affect link health, diagnostics, and isolation. Incorrect programming can hide errors, trigger unnecessary retraining, break peer-to-peer policy, or destabilize the PCIe link.
- BIOS/SBIOS scratch and RCC strap fields can be part of firmware contracts. Uncoordinated writes or incorrect interpretation can break SBIOS/driver handoff, feature gating, reset behavior, aperture sizing, or advertised PCIe capabilities.
- BIF_BX1 GFX MMIOREG CAM fields remap MMIO register addresses. Wrong CAM address/remap/enable values can make driver-visible MMIO accesses target the wrong hardware register or return unexpected completions.

## Test and Validation Signals

Useful validation for this generated chunk includes:

- Build AMDGPU configurations that include `amdgpu/nbio_v7_7.c`, `nbio_7_7_0_offset.h`, and `nbio_7_7_0_sh_mask.h` to catch malformed or missing macros.
- Cross-check every in-range field macro against the generated NBIO 7.7.0 register database and the sibling offset header, allowing for the known chunk-boundary incompleteness at line 34403 and line 36864.
- Verify that repeated lane fields for lanes 0-15 use consistent masks/shifts for 8 GT/s equalization, 16 GT/s equalization, and margining control/status.
- Compare PCIe config-space dumps on matching hardware with DEV1/DEV2 RC0 field decoding for command/status, bridge windows, PM/PCIe/MSI capabilities, ACS, DLF, AER, secondary PCIe, 16 GT/s, and margining capability structures.
- Exercise PCIe link bring-up, retraining, equalization, lane error reporting, and lane margining diagnostics; decoded status fields should move consistently with hardware events.
- Use AER or PCIe fault-injection paths where available to confirm correct decoding of uncorrectable/correctable status, masks, severity, header logs, root error status, source IDs, and TLP prefix logs.
- Validate MSI/root-error interrupt behavior after enabling or masking relevant fields, checking that message number and status fields decode as expected.
- Run suspend/resume, FLR, GPU reset, D3hot/D0, and link reset flows to observe whether scratch, strap-derived fields, AER/link status, and CAM configuration are restored or retained as expected by the NBIO backend.
- For firmware/BIOS handoff testing, inspect SBIOS/BIOS scratch and RCC strap fields before and after initialization to ensure the driver interprets platform-seeded state consistently.

## Chunk Boundary Notes

Lines 34403-34982 finish the DEV1 RC0 field definitions visible in this slice, from lane 4 equalization through lane 15 margining status. Lines 34984-36606 cover the DEV2 RC0 root-complex configuration-space field definitions. Lines 36608-36783 cover PF1 and BIF_BX1 indirect, scratch, interrupt, and GFX MMIOREG CAM fields. Lines 36786-36864 begin RCC strap field definitions for BIF strap block 1 and stop before the rest of `RCC_STRAP1_RCC_BIF_STRAP1` masks.
