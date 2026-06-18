# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_7_2_0_offset.h lines 14625-17031

## Purpose

This chunk is a generated AMD NBIO 7.2.0 register-offset slice for PCIe root-port configuration decode blocks. It contains preprocessor constants only: each `reg...` macro gives the SOC15/NBIO register offset for a PCIe configuration register, and each paired `reg..._BASE_IDX` macro identifies the register base index used by AMDGPU register access helpers.

The chunk covers the tail of `BIFPLR1_0`, full `BIFPLR2_0`, `BIFPLR3_0`, and `BIFPLR4_0` blocks, and the beginning-to-middle of `BIFPLR5_0`. It is not executable logic, but it is part of the hardware ABI used by NBIO 7.2 driver code to address PCIe capability, error handling, link-training, power-management, and lane diagnostic registers.

## Public Surface In This Chunk

The exported surface is 2,391 `#define` macros in the standard generated offset-header pattern:

- `regBIFPLR*_0_<REGISTER>`: NBIO register offset for a root-port config-space register.
- `regBIFPLR*_0_<REGISTER>_BASE_IDX`: base-index selector, consistently `5` in this slice.

The chunk starts at `regBIFPLR1_0_PCIE_LANE_7_EQUALIZATION_CNTL_BASE_IDX`, so the first visible register family is partial. It then covers `BIFPLR1_0` secondary PCIe/equalization tail, ACS, multicast, L1 PM substate, DPC, RP PIO, ESM, Data Link Feature, 16 GT PHY, margining, CCIX, and ESM lane equalization offsets through `regBIFPLR1_0_PCIE_CCIX_TRANS_CNTL`.

The full generated address blocks begin at:

- `// addressBlock: nbio_pcie0_bifplr2_cfgdecp`, base address `0x11102000`, macros `regBIFPLR2_0_*`.
- `// addressBlock: nbio_pcie0_bifplr3_cfgdecp`, base address `0x11103000`, macros `regBIFPLR3_0_*`.
- `// addressBlock: nbio_pcie0_bifplr4_cfgdecp`, base address `0x11104000`, macros `regBIFPLR4_0_*`.
- `// addressBlock: nbio_pcie0_bifplr5_cfgdecp`, base address `0x11105000`, macros `regBIFPLR5_0_*`.

The `BIFPLR5_0` block is partial in this chunk: it starts at standard PCI configuration registers and ends at `regBIFPLR5_0_LANE_9_MARGINING_LANE_STATUS_BASE_IDX`; lanes 10-15 margining and later CCIX/ESM entries continue in the next source chunk.

## Important Register Families

The complete `BIFPLR2_0`, `BIFPLR3_0`, and `BIFPLR4_0` blocks each map a bridge/root-port style PCIe configuration space. Their standard PCI header coverage includes vendor/device IDs, command/status, revision/class codes, cache-line/latency/header/BIST fields, bus numbering, IO and memory bridge windows, prefetchable window upper/lower registers, capability pointers, ROM base address, interrupt line/pin, bridge control, and vendor/adapter ID capability registers.

The PCI power, PCIe, and MSI families include PM capability/status-control, PCIe capability, device/link/slot/root capability and control/status registers, PCIe 2.0 device/link/slot extensions, MSI capability/list/control/address/data registers, SSID, and MSI map capability/address registers. These offsets allow consumers to read or program endpoint/root-port identity, interrupt routing, bridge aperture, link state, slot state, root error state, and power-management capability registers.

The extended PCIe capability families include vendor-specific capability registers, virtual channel resource registers, device serial number registers, AER status/mask/severity/capability/header-log/root-error/source-ID registers, TLP prefix logs, secondary PCIe link-control/equalization registers, ACS capability/control, multicast capability/control/address/receive/block/overlay BAR registers, L1 PM substate capability/control registers, DPC capability/control/status/source ID, RP PIO status/mask/severity/system-error/exception/header-log/prefix-log registers, ESM capability/header/status/control/capability registers, Data Link Feature capability/status, 16 GT PHY link capability/control/status/parity and lane equalization, PCIe margining port/lane registers, CCIX capability/ESM registers, and ESM 20 GT/25 GT lane equalization controls.

Per-lane families are intentionally repetitive. The slice includes 16-lane secondary equalization offsets, 16 GT equalization offsets, margining lane control/status offsets, and ESM 20 GT/25 GT equalization offsets. Several adjacent lane macros share a single dword offset because the hardware packs multiple lane fields into one register; field-level shifts and masks live in the sibling `nbio_7_2_0_sh_mask.h` header.

## Control Flow And State

There is no runtime control flow in this file. The effective flow is compile-time substitution:

1. AMDGPU NBIO 7.2 code includes `nbio_7_2_0_offset.h` and `nbio_7_2_0_sh_mask.h`.
2. A call site passes a `reg...` macro to a register helper such as `SOC15_REG_OFFSET`, `RREG32_SOC15`, `WREG32_SOC15`, `RREG32_PCIE_PORT`, or `WREG32_PCIE_PORT`.
3. If individual fields are needed, the call site combines the address macro from this file with shift/mask macros from the companion mask header and helper macros such as `REG_SET_FIELD`.

The header stores no C state and has no persistence layer. State is the hardware state in the GPU's NBIO PCIe configuration and capability registers. Many addressed registers represent persistent or externally visible hardware state until reset or explicit driver/firmware/PCIe action: bridge windows, command bits, MSI routing, PM state, link control, link equalization, lane margining results, AER/DPC/RP PIO error status and logs, ACS isolation controls, multicast routing, L1 PM substate settings, and CCIX/ESM capability state.

## Dependencies And Integration Points

This chunk depends on the generated AMD register-header convention for SOC15/NBIO hardware. The offset header supplies addresses and base indices; `nbio_7_2_0_sh_mask.h` supplies field shifts and masks for the same register names. Callers must use both correctly: an offset macro alone says where a register lives, not which bits are safe or meaningful.

The direct driver include point found in this tree is `drivers/gpu/drm/amd/amdgpu/nbio_v7_2.c`, which includes both `nbio/nbio_7_2_0_offset.h` and `nbio/nbio_7_2_0_sh_mask.h`. That NBIO implementation uses the same register-access ecosystem to configure memory-controller access, doorbell apertures, interrupt handling, HDP remap registers, and PCIe/NBIO controls. This chunk's root-port constants are therefore available to NBIO 7.2 code paths even when only a subset is touched by current call sites.

Semantic dependencies are the PCI and PCI Express specifications plus AMD's NBIO 7.2 register map. Register names encode standard capabilities such as PM, MSI, PCIe capability, AER, VC, ACS, multicast, L1 PM substate, DPC, Data Link Feature, 16 GT PHY, margining, and vendor/CCIX/ESM extensions, but this header does not enforce legal ordering, access width, write-one-to-clear behavior, or hardware side effects.

## Risks And Maintenance Notes

- The chunk boundaries are not semantic boundaries. It starts in the middle of `BIFPLR1_0` lane equalization and ends in the middle of `BIFPLR5_0` margining, so adjacent chunk research is required for complete per-block coverage.
- Address and base-index macros must match the NBIO 7.2.0 hardware definition exactly. A stale or cross-generation offset can make otherwise correct field code read or write the wrong PCIe/NBIO register.
- Many names are repeated across `BIFPLR2_0`, `BIFPLR3_0`, `BIFPLR4_0`, and `BIFPLR5_0` with only address offsets changing. Generated drift or copy/paste edits are hard to review visually.
- Packed registers intentionally have multiple symbolic names at the same offset, such as vendor/device ID pairs, command/status pairs, MSI address/data aliases, DPC capability/control pairs, ESM header/status pairs, and per-lane equalization groups. Consumers must rely on the companion shift/mask header for field disambiguation.
- Error/status/log registers in AER, DPC, RP PIO, ESM, link parity, and margining families may have hardware side effects, including write-one-to-clear status or latched diagnostic state. Read-modify-write is not automatically safe just because an offset macro exists.
- Control registers for ACS, multicast, bridge apertures, MSI, L1 PM substates, link retraining/equalization, DPC, CCIX, and ESM can affect isolation, interrupt delivery, power behavior, error containment, and PCIe link stability.
- The consistent `_BASE_IDX 5` convention is part of the SOC15 address calculation contract. Mixing these offsets with helpers or base indices from another NBIO generation can silently address a different register window.

## Test Signals

Useful validation signals for this chunk are:

- Compile coverage of NBIO 7.2 translation units that include `nbio_7_2_0_offset.h`, especially `drivers/gpu/drm/amd/amdgpu/nbio_v7_2.c`.
- Static generated-header checks that every `regBIFPLR*_0_*` offset in this slice has a paired `_BASE_IDX`, that each base index remains `5`, and that complete `BIFPLR2_0` through `BIFPLR4_0` blocks retain the same register-name sequence with the expected address stride.
- Cross-header checks that register names in this offset slice have corresponding shift/mask definitions in `nbio_7_2_0_sh_mask.h` where fields are defined.
- Hardware register-dump comparison on NBIO 7.2 devices against PCI config-space views such as `lspci -vvxxx` and AMDGPU debug register reads for vendor/device IDs, class codes, bridge windows, PM/MSI/PCIe capabilities, AER/DPC state, link speed/width, ACS controls, L1 PM substate controls, and lane equalization/margining registers.
- Runtime link/error-path tests that exercise PCIe retraining, equalization, AER reporting/clearing, DPC containment, RP PIO logging, L1.1/L1.2 behavior, and margining diagnostics without modifying unrelated packed fields.
