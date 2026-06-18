# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_7_7_0_sh_mask.h lines 135240-137666

## Purpose

This chunk is part of AMDGPU's generated NBIO 7.7.0 register shift/mask header. It defines C preprocessor constants for PCIe/NBIO bitfields, not executable logic. The macros encode the bit positions and masks for root-complex configuration-space registers so the NBIO 7.7 driver can read, update, and decode hardware fields through the common AMDGPU register helpers.

The range starts in the tail of `BIF_CFG_DEV1_RC1_DEVICE_CAP2` and covers the rest of the `BIF_CFG_DEV1_RC1` PCIe extended capability area, including MSI, SSID, MSI mapping, vendor-specific, virtual-channel, AER, secondary PCIe, ACS, data-link feature, 16 GT/s PHY, 16 GT/s equalization, and lane margining registers. It then begins a new address block, `nbio_nbif0_bif_cfg_dev2_rc_bifcfgdecp`, and defines the standard and extended PCIe configuration fields for `BIF_CFG_DEV2_RC1` through `BIF_CFG_DEV2_RC1_LANE_6_EQUALIZATION_CNTL_16GT`.

## Important APIs, Types, and Functions

There are no functions, structs, enums, or runtime variables in this chunk. Its public interface is the macro naming contract:

- `BIF_CFG_DEV*_RC1_<REG>__<FIELD>__SHIFT` gives the field's least-significant bit.
- `BIF_CFG_DEV*_RC1_<REG>__<FIELD>_MASK` gives the already-shifted mask for that field.
- Register-block comments such as `//BIF_CFG_DEV2_RC1_LINK_STATUS` delimit field groups but do not compile into symbols.

These names are consumed by `REG_FIELD_SHIFT(reg, field)`, `REG_FIELD_MASK(reg, field)`, `REG_SET_FIELD(orig_val, reg, field, field_val)`, and `REG_GET_FIELD(value, reg, field)` in `drivers/gpu/drm/amd/amdgpu/amdgpu.h`. For this ASIC generation, `drivers/gpu/drm/amd/amdgpu/nbio_v7_7.c` includes both `nbio/nbio_7_7_0_offset.h` and this `nbio_7_7_0_sh_mask.h`, pairing register addresses with these bitfield definitions.

## Register Areas Covered

`BIF_CFG_DEV1_RC1` continuation:

- PCIe capability 2 fields: completion timeout support/control, ARI forwarding, atomic operations, IDO, LTR, OBFF, 10-bit tags, end-to-end TLP prefixes, emergency power reduction, FRS, Gen2+ link capabilities/control/status, and reserved slot capability/control/status 2 registers.
- MSI and identity-related capabilities: MSI capability list/control/address/data fields, extended MSI data, SSID capability/list, and MSI map capability/list.
- PCIe vendor-specific and virtual-channel capability blocks: capability IDs, versions, next pointers, VC arbitration controls, resource caps/control/status for VC0 and VC1.
- Device serial number and Advanced Error Reporting: uncorrectable error status/mask/severity bits, correctable error status/mask bits, AER capability/control, header logs, root error command/status, error source IDs, and TLP prefix logs.
- Secondary PCIe and link training/equalization: link control 3, lane error status, per-lane 8 GT/s equalization controls for lanes 0-15, ACS capability/control, Data Link Feature capability/status, 16 GT/s PHY capability, 16 GT/s link status, parity mismatch status registers, and per-lane 16 GT/s equalization controls for lanes 0-15.
- PCIe lane margining for DEV1: margining enhanced capability/list, port cap/status, and lane control/status pairs for lanes 0-15. These encode receiver number, margin type, usage model, payload, error count limit, sample reporting method, ready/error status, margin value, lane number, and software-ready bits.

`BIF_CFG_DEV2_RC1` new address block:

- Standard PCI type-1/root-port configuration fields: vendor/device ID, command/status, revision/class code, cache line/latency/header/BIST, base address registers, subordinate bus and latency registers, I/O and memory base/limit windows, prefetchable base/limit upper registers, capability pointer, ROM base, interrupt line/pin, IRQ bridge control, and extended bridge control.
- Power management and base PCIe capability fields: PM capability/status/control, PCIe capability header/type/slot interrupt fields, device/link/slot/root capability-control-status groups, and PCIe capability 2/link capability 2/control 2/status 2/slot 2 groups.
- MSI, SSID, MSI map, vendor-specific, virtual-channel, device serial number, AER, secondary PCIe, ACS, DLF, and 16 GT/s PHY blocks that mirror the DEV1 organization.
- The chunk ends after defining DEV2 16 GT/s lane equalization controls through lane 6; the remaining DEV2 16 GT/s lanes and later capability fields continue outside this work item.

## Control Flow

This header has no control flow. It is compiled as constant definitions and affects execution only when another source file expands the macros in register read/modify/write code.

The effective runtime pattern is:

1. Driver code selects a register address from `nbio_7_7_0_offset.h` or a SOC15 register offset helper.
2. It reads a 32-bit value with helpers such as `RREG32_SOC15`, `RREG32_PCIE_PORT`, or related AMDGPU MMIO/PCIe accessors.
3. It extracts or updates fields using the `*_MASK` and `*_SHIFT` macros through `REG_GET_FIELD` or `REG_SET_FIELD`.
4. For control registers, it writes the modified value back with `WREG32_SOC15`, `WREG32_PCIE_PORT`, or a similar accessor.

Status and log registers in this chunk are often read for diagnostics or error handling, while control/mask registers can be used to enable, disable, or classify PCIe behavior.

## State and Persistence Behavior

The macros themselves are build-time constants and persist only in compiled code. The hardware fields they describe are MMIO/configuration-space state inside NBIO PCIe root-complex instances.

State categories in this chunk include:

- Capability state advertised by hardware or straps, such as supported link speeds, MSI capability, ACS support, DLF support, 16 GT/s equalization support, and lane margining capability.
- Mutable control state, such as PCI command bits, bridge windows, completion timeout controls, link controls, MSI enable/data/address fields, VC controls, AER masks/severity, root error command, ACS controls, DLF exchange enable, and margining lane controls.
- Sticky or sampled status/log state, such as PCI status bits, device/link/slot/root status, AER status registers, AER header/TLP prefix logs, lane error status, 16 GT/s equalization completion/phase status, parity mismatch status, and margining lane status.

Persistence is hardware-defined. Some values reset with device reset, some are configured during PCI enumeration or GPU driver initialization, and error/status bits may be sticky until cleared according to PCIe semantics. This header does not enforce those semantics; it only provides the bit layout used by code that touches the registers.

## Dependencies and Integration Points

- Direct integration point: `drivers/gpu/drm/amd/amdgpu/nbio_v7_7.c` includes this header and its matching offset header for NBIO 7.7.0.
- Register-address dependency: field macros must match `nbio_7_7_0_offset.h`; a correct mask applied to the wrong offset still corrupts or misreads hardware state.
- Helper dependency: `REG_SET_FIELD` and `REG_GET_FIELD` expect exactly the generated `reg__field_MASK` and `reg__field__SHIFT` spelling used here.
- PCIe/NBIO subsystem dependency: the fields map to PCI/PCIe root-complex concepts used by enumeration, link training, interrupt routing, AER/RAS reporting, ACS isolation, VC arbitration, and PCIe 4.0/5.0 link quality features.
- Source-generation dependency: the file appears generated from AMD register descriptions. Manual edits risk divergence from the hardware database and from adjacent ASIC headers.

## Risks and Edge Cases

- Bitfield drift is the primary risk. A wrong shift or mask can silently write adjacent control bits or decode the wrong status bit, which is especially dangerous in PCI command, bridge window, AER mask/severity, ACS control, and link training fields.
- Field-width mistakes matter for multi-bit values such as link speed, link width, OBFF mode, completion timeout, VC arbitration table offsets, MSI multi-message fields, bus numbers, memory/I/O base-limit fields, margin payloads, and 16 GT/s presets.
- Several registers are status, log, or write-one-to-clear style by PCIe convention. Generic read/modify/write against those fields can accidentally clear sticky error state if the caller treats them like ordinary controls.
- DEV1 and DEV2 blocks are highly repetitive. Copy/paste or generated-name mismatches can compile cleanly but operate on the wrong root-complex instance.
- The range begins mid-register (`BIF_CFG_DEV1_RC1_DEVICE_CAP2`) and ends mid-DEV2 PHY lane sequence. Any per-file reconciliation must merge this chunk with neighboring chunks before making whole-register or whole-device claims.
- Reserved fields are represented by full-width masks in some slot/status/capability registers. Driver code should not infer writable behavior from the existence of a reserved mask.

## Test Signals

Useful validation signals for this chunk are mostly compile-time and hardware smoke tests:

- Build coverage for AMDGPU NBIO 7.7 code with this header included; unresolved macro names or duplicate incompatible definitions would be caught at compile time.
- Static comparison against the AMD register database or a known-good upstream `nbio_7_7_0_sh_mask.h`, especially for DEV1/DEV2 repeated blocks and lane-indexed registers.
- Runtime PCIe enumeration on NBIO 7.7 hardware: vendor/device IDs, class codes, bridge bus windows, capability pointers, MSI capability, and PCIe capability chains should decode correctly.
- Link-training diagnostics: link status, Gen2+ equalization status, 16 GT/s equalization phase bits, lane error status, and per-lane preset fields should match expected hardware behavior under supported link speeds.
- AER/RAS testing: injected or naturally observed PCIe correctable/uncorrectable errors should set the expected status bits, respect mask/severity programming, and populate header/TLP prefix logs consistently.
- Security/isolation testing: ACS capability/control fields should reflect and enforce the expected source-validation, translation-blocking, peer-to-peer redirect, upstream-forwarding, and egress-control behavior.
- Lane margining test flows should observe ready/error/status transitions and margin values matching the fields defined for the DEV1 lane margining controls/status registers.
