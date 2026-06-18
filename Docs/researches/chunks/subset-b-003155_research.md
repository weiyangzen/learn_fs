# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_7_2_0_offset.h lines 21878-24223

## Scope

This chunk is a generated AMDGPU NBIO 7.2 offset-header segment for PCIe root-port/link register windows named `BIFPLR*_1`. It contains address constants and matching `_BASE_IDX` constants only. There are no functions, structs, enums, variables, locks, allocations, executable statements, or local algorithms in this range.

The range starts in the tail of the `BIFPLR1_1` block at lane-margining lane 1, covers the complete `nbio_pcie0_bifplr2_cfgdecp`, `nbio_pcie0_bifplr3_cfgdecp`, `nbio_pcie0_bifplr4_cfgdecp`, and `nbio_pcie0_bifplr5_cfgdecp` blocks, and then enters the `nbio_pcie0_bifplr6_cfgdecp` block through `BIFPLR6_1_STATUS`. The address-block comments identify base addresses `0xfffe0000b000`, `0xfffe0000c000`, `0xfffe0000d000`, `0xfffe0000e000`, and `0xfffe0000f000` for BIFPLR2 through BIFPLR6 respectively. All macros in this chunk use NBIO base index `5`.

Although this repository mirror is under `sources/distributed-fs/ceph-client`, this source file is AMD GPU hardware metadata. It does not implement Ceph or distributed-filesystem behavior.

## Purpose

`nbio_7_2_0_offset.h` is the address half of AMD's generated NBIO 7.2 register interface. The macros in this chunk map PCI/PCIe configuration-space style registers for NBIO PCIe root-port/link blocks to SOC15 register offsets. The generated convention is:

- `regBIFPLR<n>_1_<REGISTER>` gives the MMIO/config decode address used by AMDGPU register helpers.
- `regBIFPLR<n>_1_<REGISTER>_BASE_IDX` gives the SOC15 base-index selector, here always `5`.

The chunk's address values span roughly `0x3fff7bfc2913` through `0x3fff7bfc3c01`. Many logical PCI config fields share a dword address, such as vendor/device ID, command/status, class-code bytes, device/status controls, link/status controls, slot controls, root capability/status, MSI data fields, and CCIX headers. That aliasing is expected because the offset header names subregister fields that occupy portions of the same 32-bit config-space dword; the companion shift/mask header defines the actual bit positions.

## Important Macro Families

The `BIFPLR1_1` tail in this chunk covers the end of one root-port/link register block:

- Per-lane PCIe margining control and status for lanes 1 through 15, continuing from lane 0 in the prior chunk.
- The PCIe margining enhanced-capability tail is followed by CCIX capability registers: `PCIE_CCIX_CAP_LIST`, `PCIE_CCIX_HEADER_1`, `PCIE_CCIX_HEADER_2`, `PCIE_CCIX_CAP`, ESM required/optional capability, ESM status/control, 20 GT/s and 25 GT/s ESM lane equalization controls for lanes 0 through 15, and CCIX transport capability/control.

The `BIFPLR2_1`, `BIFPLR3_1`, `BIFPLR4_1`, and `BIFPLR5_1` blocks are complete and repeat the same generated register layout:

- Standard PCI bridge/header fields: `VENDOR_ID`, `DEVICE_ID`, `COMMAND`, `STATUS`, revision/class-code fields, cache-line/latency/header/BIST fields, subordinate bus and I/O/memory/prefetchable window limit registers, capability pointer, ROM base, interrupt line/pin, bridge control, vendor capability, and adapter ID write field.
- Power-management and PCIe capability registers: `PMI_CAP_LIST`, `PMI_CAP`, `PMI_STATUS_CNTL`, `PCIE_CAP_LIST`, `PCIE_CAP`, device capability/control/status, link capability/control/status, slot capability/control/status, root control/capability/status, and the PCIe 2.0 device/link/slot capability/control/status 2 registers.
- Interrupt and subsystem capability registers: MSI capability list/control/message address/data fields, subsystem ID capability, and MSI map capability.
- PCIe extended capabilities: vendor-specific enhanced capability, virtual channel capability/control/status/resource registers, device serial number, Advanced Error Reporting status/mask/severity/capability/header-log/root-error/source-ID/TLP-prefix-log registers, and secondary PCIe extended capability registers.
- Link-management and containment features: link control 3, lane error status, per-lane equalization controls for lanes 0 through 15, ACS capability/control, multicast capability/control/address/receive/block/overlay registers, L1 PM substate capability/control, DPC capability/control/status/error-source, and RP PIO status/mask/severity/system-error/exception/header-log/prefix-log registers.
- Extended-speed and protocol features: ESM capability/status/control/capability registers, data-link feature capability/status, 16 GT/s PHY capability/control/status/local and RTM parity mismatch registers, 16 GT/s per-lane equalization controls, PCIe margining enhanced capability with per-lane control/status, and CCIX/ESM/transport capability and control registers.

The `BIFPLR6_1` prefix begins the next block and includes only `VENDOR_ID`, `DEVICE_ID`, `COMMAND`, and `STATUS` in this chunk. Adjacent chunks are required before treating the BIFPLR6 register block as complete.

## APIs, Types, And Functions

There are no callable APIs or C types in this chunk. The public interface is the generated preprocessor macro namespace. Each address macro is an untyped integer literal, and each `_BASE_IDX` macro is the literal base index used by SOC15 register-offset construction.

Consumers combine these constants with AMDGPU register helpers and the sibling shift/mask header:

- `nbio_7_2_0_sh_mask.h` supplies field-level `__SHIFT` and `_MASK` definitions for the same `BIFPLR*_1_*` register names.
- `RREG32_SOC15`, `WREG32_SOC15`, `SOC15_REG_OFFSET`, `RREG32_PCIE_PORT`, `WREG32_PCIE_PORT`, `REG_GET_FIELD`, and `REG_SET_FIELD` are the normal AMDGPU helper layer used around generated NBIO register metadata.
- `drivers/gpu/drm/amd/amdgpu/nbio_v7_2.c` includes both this offset header and `nbio_7_2_0_sh_mask.h`; display resource files for DCN 3.0.1 and DCN 3.1 also include this offset header for NBIO address integration.

This specific `BIFPLR*_1` chunk is mostly metadata for PCIe root-port/link configuration windows. Direct hand-written C references to these exact macro names are not prominent in the mirrored tree, but the macros remain part of the generated ABI consumed by AMDGPU register-access code and by any generated or diagnostic code that addresses these NBIO config windows.

## Control Flow

This header has no runtime control flow. Its effect is compile-time substitution:

1. An AMDGPU translation unit includes `nbio_7_2_0_offset.h`.
2. Driver or generated code selects a `regBIFPLR*_1_*` address macro and its base index.
3. The SOC15/PCIe-port helper computes the actual MMIO address for the selected NBIO instance.
4. The caller reads, writes, or read-modify-writes the register, using `nbio_7_2_0_sh_mask.h` when it needs individual fields.
5. PCIe hardware interprets the resulting root-port, link, error-reporting, lane-training, margining, power-management, or CCIX/ESM state.

The register names imply hardware flows outside this file: PCI bridge-window programming, link training and equalization, MSI setup, root-port error reporting, AER/DPC logging and clearing, L1 substate power management, ACS isolation, multicast routing, PCIe margining, 16 GT/s parity monitoring, and CCIX/ESM transport negotiation. The header itself imposes no sequencing or validation.

## State And Persistence Behavior

The header owns no state and persists nothing. It describes hardware-visible state in NBIO 7.2 PCIe configuration/register windows. Persistence depends on GPU reset domains, PCI bus reset, function reset, firmware or BIOS initialization, suspend/resume save-restore, and explicit driver writes.

The represented hardware state includes:

- PCI bridge identity, command/status, class-code, bus numbering, I/O and memory aperture windows, prefetchable aperture windows, ROM base, interrupt routing, and bridge-control bits.
- Power-management status/control and PCIe device/link/slot/root capability/control/status registers.
- MSI routing metadata and subsystem/vendor capability data.
- Virtual channel resources, AER status/mask/severity/header logs/root-error state, secondary PCIe status, ACS control, multicast routing, L1 PM substates, DPC containment and RP PIO logs.
- Per-lane equalization, lane error status, 16 GT/s parity mismatch status, lane margining control/status, CCIX capability and ESM/transport state.

Some of those registers are read-only capabilities, some are status or sticky error logs, some are write-one-to-clear status registers, and some are writable controls. The offset macros do not encode access permissions, reset values, side effects, or whether read-modify-write is safe.

## Dependencies And Integration Points

The chunk depends on AMD's generated NBIO 7.2 register database and must remain synchronized with related generated files in `drivers/gpu/drm/amd/include/asic_reg/nbio/`:

- `nbio_7_2_0_sh_mask.h` provides field masks and shifts for these address names.
- Other NBIO 7.2 generated headers, where present, provide related default/reset or instance metadata.
- `amdgpu/nbio_v7_2.c` is the primary NBIO 7.2 driver integration point and includes this header for register access across NBIO initialization, revision detection, memory-controller access, doorbell aperture setup, interrupt handling, HDP flush, and related NBIO operations.
- `display/dc/resource/dcn301/dcn301_resource.c` and `display/dc/resource/dcn31/dcn31_resource.c` include this header to share NBIO offsets with DC resource setup on ASICs using NBIO 7.2-era register maps.

Semantic dependencies are the PCI and PCI Express specifications for bridge configuration headers, PCIe capability structures, MSI, AER, virtual channels, ACS, L1 PM substates, DPC, lane equalization, lane margining, data-link feature registers, and high-speed link training. CCIX/ESM register naming also depends on the corresponding AMD hardware register specification and protocol capability layout.

## Risks And Edge Cases

- The chunk starts and ends mid-block. BIFPLR1 and BIFPLR6 must be reconciled with adjacent chunks before whole-file reports claim full coverage of those blocks.
- Generated address drift can compile cleanly but route reads and writes to the wrong NBIO config dword. For bridge-style registers this can corrupt bus windows, interrupt state, link controls, AER/DPC logs, or lane-training controls.
- Multiple logical names intentionally share one dword offset. Treating aliases such as command/status, device/status control, link/status control, MSI message data, or CCIX header/capability as independent 32-bit registers can clobber neighboring fields unless callers use the matching masks and preserve unrelated bits.
- All entries use base index `5`. A wrong base index would be a systemic integration fault even if the literal register offsets look plausible.
- Status and error-reporting registers can have write-one-to-clear or sticky semantics. The address header cannot tell callers which fields are safe for blind writes or generic read-modify-write operations.
- AER, DPC, RP PIO, ACS, multicast, L1 PM, and lane-equalization registers affect reliability, isolation, power behavior, and link stability. Misprogramming can appear only on specific platforms, link widths, speeds, resets, or error conditions.
- Per-lane equalization and margining addresses are heavily repetitive. Copy or generation errors that affect only one lane or one `BIFPLR` instance are easy to miss in review and may surface only with particular board routing or degraded links.
- CCIX/ESM and 20/25 GT/s controls may be unused on many systems, so stale or incorrect offsets can evade normal boot testing.

## Test Signals

- Build AMDGPU with NBIO 7.2 support enabled so includes from `nbio_v7_2.c`, DCN 3.0.1, and DCN 3.1 resource code catch missing or renamed macros.
- Run generated-header consistency checks: each non-`_BASE_IDX` macro in this range should have a matching `_BASE_IDX`, every `_BASE_IDX` should be `5`, and repeated `BIFPLR2_1` through `BIFPLR5_1` register families should match except for the expected address stride.
- Cross-check this offset chunk against `nbio_7_2_0_sh_mask.h` so each covered register name has corresponding field definitions where field access is expected.
- On NBIO 7.2 hardware, compare decoded BIFPLR PCIe configuration space with PCI core dumps, `lspci -vvxxx`, AMDGPU debugfs/register dumps, or vendor diagnostics for vendor/device IDs, bridge windows, PM state, link capabilities/status, MSI state, AER/DPC logs, ACS state, L1 PM substate registers, lane equalization, lane margining, and CCIX/ESM capability registers.
- Exercise suspend/resume, GPU reset, PCI bus reset or retraining, MSI enable/disable, AER/DPC error paths, and link-speed changes to confirm callers preserve reserved bits and restore expected NBIO config state.
- For lane-specific changes, test multiple link widths and degraded-width scenarios because lane 0-only testing will not cover the repeated lane 1 through 15 address families in this chunk.
