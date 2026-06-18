# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_7_7_0_offset.h lines 21934-24299

## Purpose

This chunk is an auto-generated AMD NBIO 7.7.0 register offset-header slice for PCIe bridge/root-port configuration decode windows. It contains only C preprocessor constants: register-address macros and matching `_BASE_IDX` macros. There are no executable functions, structs, enums, variables, locks, allocations, or algorithms in this range.

The assigned lines start in the tail of the `nbio_pcie0_bifplr0_cfgdecp` address block, cover complete `nbio_pcie0_bifplr1_cfgdecp` through `nbio_pcie0_bifplr4_cfgdecp` blocks, cover narrow partial `nbio_pcie1_bifplr0_cfgdecp` through `nbio_pcie1_bifplr4_cfgdecp` bridge-window/slot/subsystem blocks, cover a larger `nbio_pcie1_bifplr5_cfgdecp` block, and then enter `nbio_nbif0_bif_cfg_dev0_rc_bifcfgdecp` through `BIF_CFG_DEV0_RC1_PCIE_VENDOR_SPECIFIC_ENH_CAP_LIST`.

The offsets name NBIO-backed PCI/PCIe configuration-space registers for root-port/bridge-like functions. Driver code combines these constants with `nbio_7_7_0_sh_mask.h` field definitions and AMDGPU register helpers to read, write, or form SOC15 register offsets without embedding raw addresses.

## Public Surface

The public surface in this range is 2,322 macros: 1,161 register-address macros and 1,161 matching `_BASE_IDX` macros. Every `_BASE_IDX` macro in the chunk has value `5`, selecting the NBIO SOC15 base slot used by AMDGPU register-access helpers.

The key macro families are:

- `regBIFPLR0_2_*`: tail of PCIe controller 0 root-port 0, beginning at ACS/multicast/L1 PM/DPC/ESM/link-speed extended capabilities and ending at 32 GT/s link status.
- `regBIFPLR1_2_*` through `regBIFPLR4_2_*`: complete PCIe controller 0 root-port blocks from conventional PCI identity/header registers through 32 GT/s link registers.
- `regBIFPLR0_3_*` through `regBIFPLR4_3_*`: partial PCIe controller 1 root-port blocks containing bridge bus/window registers, slot capability/control/status, slot capability 2/control 2/status 2, and subsystem ID capability addresses.
- `regBIFPLR5_1_*`: a larger PCIe controller 1 root-port block from conventional PCI identity/header registers through Gen5/CCIX/ESM/32 GT/s link registers.
- `regBIF_CFG_DEV0_RC1_*`: start of the NBIF root-complex configuration block from vendor/device ID through MSI, subsystem/MSI-map, and the first vendor-specific enhanced capability address.

Address-block comments identify these bases inside the range: `nbio_pcie0_bifplr1_cfgdecp` at `0xfffe0000a000`, `bifplr2` at `0xfffe0000b000`, `bifplr3` at `0xfffe0000c000`, `bifplr4` at `0xfffe0000d000`, PCIe1 `bifplr0` through `bifplr5` at `0xfffe00011000` through `0xfffe00016000`, and `nbio_nbif0_bif_cfg_dev0_rc_bifcfgdecp` at `0xfffe00041000`. The initial `BIFPLR0_2` tail belongs to the earlier `nbio_pcie0_bifplr0_cfgdecp` block whose marker and base `0xfffe00009000` appear before this chunk.

## Register Coverage

The `BIFPLR0_2` tail covers PCIe extended capability address constants for access control services, multicast, L1 PM substates, downstream port containment, root-port PIO status/mask/severity/sys-error/exception and logs, ESM capability/status/control/capability registers, and 16 GT/s plus 32 GT/s link capability/control/status registers. This chunk does not include the conventional PCI/PCIe header for `BIFPLR0_2`; that context is in the previous chunk.

The full `BIFPLR1_2` through `BIFPLR4_2` blocks repeat a root-port style PCI configuration layout:

- Conventional PCI bridge fields: vendor/device ID, command/status, revision and class-code bytes, cache-line/latency/header/BIST, subordinate bus and latency register, I/O/memory/prefetchable bridge windows, capability pointer, interrupt line/pin, and bridge control.
- Power-management and PCIe capability fields: PM capability/status-control, PCIe capability header, device capability/control/status, link capability/control/status, slot capability/control/status, root control/capability/status, and PCIe capability 2 device/link/slot controls and statuses.
- Interrupt and identification fields: MSI capability list/control/address/data forms, SSID capability, and MSI-map capability.
- Extended capabilities: vendor-specific enhanced capability, virtual-channel capability/control/status/resource groups for VC0 and VC1, device serial number, Advanced Error Reporting, TLP header/prefix logs, secondary PCIe link control/lane error/equalization controls, ACS, multicast, L1 PM substates, DPC, RP PIO diagnostics, ESM, and 16 GT/s/32 GT/s link-speed capability groups.

The partial `BIFPLR0_3` through `BIFPLR4_3` ranges are intentionally narrow. For each of these five PCIe1 root-port instances, this chunk defines only `SUB_BUS_NUMBER_LATENCY`, I/O/memory/prefetchable window registers, `SLOT_CAP`, `SLOT_CNTL`, `SLOT_STATUS`, `SLOT_CAP2`, `SLOT_CNTL2`, `SLOT_STATUS2`, `SSID_CAP_LIST`, and `SSID_CAP`. The rest of each `_3` block is outside this range and must be reconciled with adjacent chunks.

The `BIFPLR5_1` block is the broadest block in this chunk. In addition to the standard bridge, PM, PCIe, MSI, SSID, MSI-map, VSEC, VC, serial-number, AER, secondary PCIe, ACS, multicast, L1 PM, DPC, RP PIO, ESM, and 16/32 GT/s groups, it includes address constants for data-link feature capability/status, PCIe PHY 16 GT/s parity mismatch status, Gen4 lane equalization controls, PCIe lane-margining control/status registers for lanes 0-15, CCIX capability/ESM registers, ESM lane equalization controls for 20 GT/s and 25 GT/s, and CCIX translation capability/control registers.

The final `BIF_CFG_DEV0_RC1` portion starts another address block for the NBIF root-complex configuration function. It covers identity/header fields, BARs, bridge windows, ROM BAR, interrupt/bridge controls, PM and PCIe capabilities, PCIe device/link/slot/root capability groups, MSI address/data forms including extended message data, SSID/MSI-map fields, and stops at the vendor-specific enhanced capability list. The vendor-specific header and later extended capabilities continue after this chunk.

## Control Flow And State

There is no runtime control flow in this header. The effective flow is compile-time substitution:

1. A translation unit includes `nbio/nbio_7_7_0_offset.h` and usually `nbio/nbio_7_7_0_sh_mask.h`.
2. Code selects a register address macro, for example a `regBIFPLR*_2_*`, `regBIFPLR*_3_*`, `regBIFPLR5_1_*`, or `regBIF_CFG_DEV0_RC1_*` name.
3. `SOC15_REG_OFFSET`, `RREG32_SOC15`, `WREG32_SOC15`, `RREG32_PCIE_PORT`, `WREG32_PCIE_PORT`, or related AMDGPU helpers combine the macro with NBIO instance/base information.
4. Field extraction or updates use sibling shift/mask macros from `nbio_7_7_0_sh_mask.h` or PCIe config-space conventions.

The header stores no software state and persists nothing. State lives in hardware PCIe/NBIO configuration registers and may be affected by reset, FLR, link retraining, power transitions, firmware policy, platform PCI enumeration, hotplug, or explicit driver writes. Some addressed registers are read-only identity/status, some are writable policy/control, and some are sticky error/log registers. The offset header does not encode access permissions, reset values, side effects, or write-one-to-clear behavior.

## Dependencies And Integration Points

The direct NBIO 7.7 include site in this tree is `drivers/gpu/drm/amd/amdgpu/nbio_v7_7.c`, which includes both `nbio_7_7_0_offset.h` and `nbio_7_7_0_sh_mask.h`. That implementation uses the same generated-header pattern for NBIO register access through `RREG32_SOC15`, `WREG32_SOC15`, `SOC15_REG_OFFSET`, `REG_SET_FIELD`, and `REG_GET_FIELD` style helpers. The exact root-port macros in this chunk are mostly a generated hardware map rather than frequently hand-referenced C symbols, but they remain part of the address namespace available to NBIO, PCIe, diagnostics, and generated access code.

The critical dependency is the sibling `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_7_7_0_sh_mask.h` header. Offset macros identify where a register lives; shift/mask macros identify how fields are packed. Mixing this NBIO 7.7.0 offset header with another ASIC generation's shift/mask header can compile while silently targeting the wrong register or field.

Semantic dependencies include the PCI and PCI Express configuration-space layouts, PCIe bridge/window semantics, MSI, subsystem ID, vendor-specific enhanced capabilities, Virtual Channel, Device Serial Number, Advanced Error Reporting, Secondary PCIe capability, ACS, Multicast, L1 PM Substates, Downstream Port Containment, RP PIO logging, ESM, Data Link Feature, PCIe 4.0/5.0 link equalization and lane margining, and CCIX-related extended capability conventions.

## Risks And Maintenance Notes

- The chunk boundaries split several address blocks. `BIFPLR0_2` starts mid-block, each `BIFPLR*_3` slice is partial, and `BIF_CFG_DEV0_RC1` stops just after the vendor-specific enhanced capability list. Whole-file research must merge adjacent chunks before claiming complete coverage of those blocks.
- The repeated `BIFPLR1_2` through `BIFPLR4_2` templates invite prefix mistakes. A register name with the wrong root-port prefix can compile cleanly while addressing a different port.
- Some different logical register names intentionally share the same dword address, such as command/status, device control/status, link control/status, capability/control pairs, and lane groups that pack multiple lanes per dword. Consumers must use the right field masks and access width rather than treating each macro as a unique physical word.
- All `_BASE_IDX` values are `5`; changing the base index or mixing helper paths would redirect accesses away from the intended NBIO aperture.
- AER, DPC, RP PIO, ESM, and TLP log registers are error-handling surfaces. Incorrect offsets can hide, misclassify, or clear PCIe faults.
- Bridge bus/window and slot-control offsets affect PCI topology visibility, hotplug state, and bridge aperture programming. These should normally be coordinated with PCI core and firmware policy rather than updated casually from device-driver code.
- Gen4/Gen5 link equalization, lane margining, DLF, and CCIX/ESM controls are hardware- and platform-sensitive. Writes using these offsets can affect link stability and interoperability.
- Generated headers provide no type safety, locking model, or ordering guarantees. Callers must supply the access sequencing, posting reads, reset handling, and firmware ownership checks where needed.

## Test Signals

Useful validation signals for this chunk are:

- Build coverage for AMDGPU NBIO 7.7 users, especially `drivers/gpu/drm/amd/amdgpu/nbio_v7_7.c`, with `nbio_7_7_0_offset.h` and `nbio_7_7_0_sh_mask.h` included together.
- Generated-header consistency checks that every address macro in this range has a matching `_BASE_IDX` macro with value `5`, and that each address macro has compatible field definitions in `nbio_7_7_0_sh_mask.h`.
- Address-block checks that repeated `BIFPLR1_2` through `BIFPLR4_2` layouts are structurally aligned, while documented exceptions for `BIFPLR0_2`, `BIFPLR*_3`, `BIFPLR5_1`, and `BIF_CFG_DEV0_RC1` are preserved.
- Hardware or simulator PCI config-space dumps for the corresponding root ports/root-complex function, compared against these offsets and standard `lspci -vvxxx` decoding for PCIe capabilities, MSI, VC, AER, ACS, DPC, L1 PM, link-speed, and lane-margining registers.
- Error-injection or fault-observation tests that verify AER/DPC/RP PIO/ESM status, masks, source IDs, header logs, and prefix logs decode at the expected addresses.
- Link training and margining tests on supported hardware that confirm 16 GT/s and 32 GT/s capability/control/status addresses line up with observed negotiated speed, lane width, equalization, and margining state.
- Static checks that no hand-written code pairs an offset from this NBIO 7.7.0 header with a field mask from another NBIO generation.
