# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_7_2_0_sh_mask.h lines 17219-19643

## Purpose

This chunk is part of AMDGPU's generated NBIO 7.2 register field header. It defines C preprocessor constants for bit shifts and masks used to access fields inside NBIO/PCIe configuration registers. The assigned span begins in the tail of the `BIFPLR0` CCIX/ESM lane-equalization definitions, then covers most of the `addressBlock: nbio_pcie0_bifplr1_cfgdecp` register field map.

The constants in this chunk are not standalone logic. They are a hardware ABI between the driver and the NBIO PCIe block: register address constants live in the sibling `nbio_7_2_0_offset.h`, while this file provides the bit positions and masks needed by `REG_GET_FIELD`, `REG_SET_FIELD`, `RREG32_*`, and `WREG32_*` users.

## Covered Register Areas

- `BIFPLR0_ESM_LANE_12..15_EQUALIZATION_CNTL_20GT` and `BIFPLR0_ESM_LANE_0..15_EQUALIZATION_CNTL_25GT`: per-lane downstream/upstream ESM transmit preset fields. Each lane has a low-nibble DSP preset at shift `0x0` with mask `0x0f`, and a high-nibble USP preset at shift `0x4` with mask `0xf0`.
- `BIFPLR0_PCIE_CCIX_TRANS_CAP` and `BIFPLR0_PCIE_CCIX_TRANS_CNTL`: single-bit support and enable fields for optimized CCIX TLP format.
- `BIFPLR1_VENDOR_ID` through bridge/base resource registers: standard PCI/PCIe bridge config-space fields including command/status, revision/class code, header/BIST, bus numbering, IO/memory/prefetchable windows, ROM base, interrupt line/pin, and bridge control.
- Power-management and PCIe capability registers: `PMI_*`, `PCIE_CAP_LIST`, `PCIE_CAP`, `DEVICE_CAP`, `DEVICE_CNTL`, `DEVICE_STATUS`, `LINK_CAP`, `LINK_CNTL`, `LINK_STATUS`, slot/root capability/control/status, and second-generation capability/control/status registers.
- MSI and subsystem/vendor structures: MSI message control/address/data fields, SSID capability, MSI map capability, and vendor-specific extended capability header/data words.
- PCIe extended capabilities: virtual channel, device serial number, advanced error reporting, secondary PCIe capability, access control services, multicast, L1 PM substates, downstream port containment, data link feature, 16GT PHY capability, margining, and the beginning of CCIX capability metadata.
- AER/DPC/RP PIO diagnostics: uncorrectable/correctable error status/mask/severity, header/TLP prefix logs, root error command/status/source IDs, DPC controls/status/source ID, and root-port PIO status/mask/severity/system-error/exception/log fields.
- Per-lane link training fields: `BIFPLR1_PCIE_LANE_0..15_EQUALIZATION_CNTL`, 16GT lane equalization controls, and `BIFPLR1_LANE_0..15_MARGINING_LANE_CNTL/STATUS`.
- ESM capability fields: `BIFPLR1_PCIE_ESM_CAP_1..7` expose supported data rates, lane counts, equalization modes, calibration timing, retimer/reach metadata, preset values, and related extended-speed-mode properties.

## Important APIs, Types, and Functions

This chunk defines no C functions, variables, enums, structs, or inline helpers. Its public surface is a large set of macros following the generated AMD register naming convention:

- `<REGISTER>__<FIELD>__SHIFT`: bit index used before masking or after extraction.
- `<REGISTER>__<FIELD>_MASK`: bit mask for the field in the register value.

The practical API is indirect. Callers include this header and combine these macros with AMDGPU register helpers such as `REG_SET_FIELD` and `REG_GET_FIELD`. The only direct C include found under the AMDGPU tree is `drivers/gpu/drm/amd/amdgpu/nbio_v7_2.c`, which includes both `nbio_7_2_0_offset.h` and `nbio_7_2_0_sh_mask.h`.

## Control Flow

There is no runtime control flow in this chunk. The effective flow is compile-time symbol substitution:

1. Driver code chooses a register address macro from `nbio_7_2_0_offset.h`.
2. It reads or prepares a register value through the SOC15/NBIO accessors.
3. It uses the matching shift/mask macros from this header to extract or update individual fields.
4. The resulting value is written back to hardware when the field is writable.

Because the constants describe PCIe configuration-space and extended-capability fields, any runtime behavior is determined by the code that reads or writes these registers and by NBIO hardware state.

## State and Persistence Behavior

The header itself has no persistent state. The fields it names correspond to hardware-backed state in the NBIO PCIe root-port/link block:

- Configuration-space identity and capability fields are generally hardware straps, firmware-populated values, or read-only capability reports.
- Command/control fields such as bus mastering, memory access, interrupt disable, link control, slot/root control, MSI control, ACS control, DPC control, L1 PM substate control, ESM control, CCIX transport control, and margining lane control are mutable hardware state.
- Status/log fields such as PCI status, link status, AER status, root error status, DPC status, RP PIO status, header logs, TLP prefix logs, lane error status, ESM status, and margining lane status report current or latched hardware events.
- Persistence is hardware/firmware-defined. Some fields survive only until reset or explicit clear, while error/status bits may be write-one-to-clear or otherwise side-effectful depending on the PCIe capability definition and ASIC register specification.

## Dependencies

- `nbio_7_2_0_offset.h`: supplies the paired register offsets and base indices for these fields. A field macro is meaningful only with the matching register address macro.
- AMDGPU SOC15 register access layer: `RREG32_SOC15`, `WREG32_SOC15`, `RREG32_PCIE_PORT`, `WREG32_PCIE_PORT`, `SOC15_REG_OFFSET`, `REG_SET_FIELD`, and `REG_GET_FIELD` are the normal consumers.
- PCI/PCIe architectural definitions: many field names mirror standard PCI bridge config space, PCIe capability, MSI, AER, ACS, DPC, L1 PM substate, data link feature, PHY 16GT, and margining capabilities.
- AMD NBIO 7.2 hardware generation: the macro values are ASIC-specific and must match the NBIO 7.2 register specification.

## Integration Points

- `drivers/gpu/drm/amd/amdgpu/nbio_v7_2.c` includes this file for NBIO 7.2-specific field operations. That source performs NBIO setup such as HDP remap, revision detection, memory controller access enable, doorbell aperture/range programming, and interrupt control through the same offset/mask convention.
- Register names in this chunk are mapped to `cfgBIFPLR1_*` or `regBIFPLR1_*` symbols in `nbio_7_2_0_offset.h`; code must select the correct config-space or MMIO access path for the register family being touched.
- PCIe capability fields integrate with system PCIe behavior: link speed/width negotiation, power-management policy, MSI delivery, AER reporting, containment, lane equalization, lane margining, and CCIX/ESM operation.
- The repeated per-lane definitions assume lane indices 0 through 15. Any caller iterating lanes has to map lane number to the correct register macro family; the preprocessor does not provide an array or computed field name.

## Risks and Edge Cases

- A wrong shift/mask silently corrupts register programming. This is high risk for link training, error reporting, DPC, ACS, MSI, and power-management fields because incorrect writes can break PCIe enumeration, DMA, interrupt delivery, or link stability.
- Read-modify-write operations must use the correct width and access path. Some config-space registers share dwords or words, and some status bits may have write-clear semantics.
- This chunk starts and ends mid-generated-file context. The first lines continue a `BIFPLR0` lane block that begins before line 17219, and the final lines stop at `BIFPLR1_PCIE_CCIX_CAP_LIST`; the following CCIX/ESM control and lane definitions continue after line 19643.
- The generated naming is repetitive and easy to mix across blocks (`BIFPLR0`, `BIFPLR1`, later suffixed instances, 16GT vs 20GT vs 25GT, normal equalization vs ESM equalization vs margining). Review should check the complete register prefix, not just the field suffix.
- Some masks are full-width (`0xffffffff`) or cover capability/vendor payloads; treating them as narrow status bits would lose information.
- Hardware capability fields may be read-only even though this header does not encode access permissions. Callers need the ASIC register spec or PCIe capability rules to know which fields are writable.

## Test Signals

- Build signal: any typo, duplicate misuse, or missing macro referenced by NBIO 7.2 code should surface as a compile failure when building AMDGPU with this header.
- Static review signal: compare each `<REGISTER>__<FIELD>__SHIFT` and `<REGISTER>__<FIELD>_MASK` pair against the generated `nbio_7_2_0_offset.h` register names and AMD NBIO 7.2 register specification.
- Runtime signal: successful GPU PCIe enumeration, stable link speed/width negotiation, working MSI/MSI-X interrupts, functional doorbells/DMA, and absence of AER/DPC errors under load indicate that the consumed fields are coherent.
- Diagnostics signal: `lspci -vv`, kernel PCIe/AER logs, DRM/amdgpu initialization logs, and link retraining or error counters can reveal mismatches in capability, link control, AER, DPC, or margining-related fields.
- Stress signal: suspend/resume, GPU reset, hot reset, high-throughput DMA, and link-speed transition tests are relevant because this chunk covers power-management, link training, status, error, and extended-speed/margining state.
