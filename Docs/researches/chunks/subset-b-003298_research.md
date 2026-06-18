# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_7_7_0_sh_mask.h lines 94603-97017

## Scope

This chunk is a generated AMD NBIO 7.7.0 register shift/mask header slice. It contains no executable functions or persistent software data structures; its purpose is to provide C preprocessor constants for extracting and programming PCIe/NBIO bitfields through the AMDGPU register helper macros. The covered range spans the tail of the `BIFPLR3_1` PCIe root-port/extended-capability block and the beginning of the `BIFPLR4_1` PCIe bridge configuration block (`addressBlock: nbio_pcie1_bifplr4_cfgdecp`).

## Purpose and Register Families

The `BIFPLR3_1` portion defines masks and shifts for PCIe error reporting and link-management capabilities:

- Advanced Error Reporting fields: uncorrectable error status/mask/severity, correctable error status/mask, ECRC capability/control, header logs, TLP prefix logs, root error command/status, and source IDs.
- Link equalization and secondary PCIe capability fields: link control 3, lane error status, per-lane equalization controls for lanes 0-15.
- ACS and multicast capability/control fields: ACS source validation, translation blocking, peer-to-peer redirect/completion redirect, upstream forwarding, egress control, direct translated P2P, enhanced capability, memory-target access controls, and multicast BAR/receive/block/overlay registers.
- L1 PM Substates fields: ASPM L1.1/L1.2 and PCI-PM L1.1/L1.2 support/enables, common-mode restore time, LTR L1.2 threshold, link activation, and power-on scale/value fields.
- Downstream Port Containment and RP PIO diagnostics: DPC capability/control/status, DPC error source ID, RP PIO status/mask/severity/system-error/exception, and RP PIO header/prefix logs.
- ESM, DLF, 16 GT/s, margining, CCIX, 20/25 GT/s ESM equalization, and 32 GT/s link capability fields. The ESM capability registers enumerate supported data rates from 8.0G through 28.0G in 0.1G increments; the per-lane ESM equalization controls cover lanes 0-15 for 20 GT/s and 25 GT/s presets.

The `BIFPLR4_1` portion begins a PCI-to-PCI bridge-style configuration-space view:

- Standard identity/class/header and command/status fields: vendor/device IDs, revision, class codes, cache line, latency, header type, BIST, command enables, SERR, interrupt disable, and status error bits.
- Bridge-window registers: primary/secondary/subordinate bus numbers, I/O base/limit, memory base/limit, prefetchable memory base/limit and upper 32-bit halves, ROM base, interrupt line/pin, and extended bridge control.
- Capability list entries and PCIe capability fields: vendor capability, adapter/subsystem ID, PM capability/status, PCIe capability, device capability/control/status, link capability/control/status, slot capability/control/status, root control/cap/status, device cap/control/status 2, link cap/control/status 2, and slot cap/control/status 2.

## Important APIs, Types, and Macros

This header exposes constants in the generated AMD register naming convention:

- `REGISTER__FIELD__SHIFT` gives the low bit for a field.
- `REGISTER__FIELD_MASK` gives the raw bit mask in the register value.
- All definitions are C preprocessor `#define`s, generally 16-bit or 32-bit masks with an `L` suffix.

The constants are not APIs by themselves. They are consumed by AMDGPU register helper APIs such as `REG_GET_FIELD`, `REG_SET_FIELD`, `WREG32_FIELD15`, `RREG32_SOC15`, `WREG32_SOC15`, and SOC15 register-offset macros from the surrounding AMDGPU code. For this ASIC generation, the companion `*_d.h` file supplies register addresses, while this `*_sh_mask.h` file supplies field layout.

There are no functions, structs, enums, locks, callbacks, or allocation paths in this chunk.

## Control Flow and Data Flow

No control flow is implemented here. Runtime behavior is indirect:

1. Driver code reads or writes a SOC15/NBIO register using the address definitions from the matching register-address header.
2. The driver passes a register family and field name to helper macros such as `REG_GET_FIELD` or `REG_SET_FIELD`.
3. Those helpers expand to the `__SHIFT` and `_MASK` constants from this header to isolate, test, or update the field.
4. Hardware consumes the resulting register value immediately; for status fields, hardware may set bits asynchronously and software may clear them by writing the documented clear/status fields.

Examples in nearby NBIO code use this pattern for doorbell/RAS interrupt status and clear bits, HDP flush masks, and register remapping. The `BIFPLR3_1` and `BIFPLR4_1` definitions in this chunk serve the same extraction/update role for PCIe capability, bridge configuration, link status, and error-reporting fields.

## State and Persistence

There is no software persistence in the header. The state represented by these macros lives in hardware registers:

- Error status/log registers preserve PCIe AER, DPC, RP PIO, lane-error, parity, and link-event observations until hardware or driver clear semantics are applied.
- Control registers persist in device hardware state across the relevant power/reset domain, not in kernel memory.
- Bridge aperture, command, PM, link, slot, and root-control fields reflect PCI configuration-space state that can be initialized by firmware, PCI core enumeration, or AMDGPU/NBIO setup.

Because these are fixed compile-time constants, any incorrect mask or shift is a build-time source error that becomes a runtime hardware programming error across all call sites using the field.

## Dependencies and Integration Points

This file is part of AMDGPU's generated ASIC register database under `drivers/gpu/drm/amd/include/asic_reg/nbio`. It depends on:

- The matching `nbio_7_7_0_d.h` register address definitions.
- AMDGPU SOC15 register access helpers and bitfield helpers.
- PCI/PCIe semantics for AER, DPC, ACS, L1 PM substates, DLF, 16/32 GT/s PHY capabilities, CCIX, PM capability, MSI capability linkage, bridge windows, and root/slot/link/device capability registers.
- Hardware/firmware initialization of NBIO and PCIe config-space defaults.

Integration is mostly compile-time. Driver code includes the ASIC-specific header selected for the device generation, then names fields through helper macros. The covered PCIe error and link masks are relevant to RAS/error reporting, PCIe link training diagnostics, hotplug/slot reporting, PM/LTR behavior, SR-IOV/ACS isolation, and low-level PCI bridge configuration.

## Risks and Edge Cases

- Mask/shift drift from hardware documentation would silently corrupt field extraction or writes. This is highest risk for control fields such as DPC enables, ACS controls, L1 PM substate controls, link target speed, command enables, and bridge aperture registers.
- Some registers are status or write-one-to-clear style in hardware. Treating status masks as ordinary writable configuration can lose error evidence or fail to clear interrupts.
- AER/DPC/RP PIO fields distinguish status, mask, severity, system-error, and exception registers with similar bit positions. Mixing those register families can report the wrong severity or suppress the wrong error.
- Per-lane equalization and margining fields are repeated for lanes 0-15. Copy/paste errors in generated constants would only show up on specific lane widths or degraded links.
- The `BIFPLR4_1` block maps PCI bridge configuration fields. Programming base/limit, command, interrupt, link, PM, or slot controls outside PCI core expectations can break enumeration, memory windows, power management, or error routing.
- Reserved fields and capability-present bits should be treated conservatively; software must not infer support from a mask definition alone. The actual register value and ASIC feature tables decide whether a field is meaningful.

## Test and Validation Signals

Useful signals for this chunk are indirect because it has no standalone unit-testable logic:

- Build coverage for AMDGPU configurations that include `nbio_7_7_0_sh_mask.h`; compile failures catch missing or renamed field macros.
- Runtime `REG_GET_FIELD`/`REG_SET_FIELD` behavior on NBIO 7.7.0 hardware for PCIe AER/DPC status, link speed/width/equalization status, L1 PM substate controls, ACS controls, and bridge command/window fields.
- PCIe enumeration and `lspci -vv` capability dumps matching expected vendor/device/class, bridge windows, PM, PCIe, slot/root, and extended capability values.
- RAS/AER/DPC injection or hardware error tests that verify correct status bits, source IDs, header logs, mask/severity behavior, and interrupt routing.
- Link training and margining diagnostics on x1/x4/x8/x16 configurations, checking lane-specific status and equalization fields rather than only aggregate link status.
- Suspend/resume, FLR, hot reset, and power-management tests to ensure hardware state programmed via these fields is restored or reinitialized as expected.
