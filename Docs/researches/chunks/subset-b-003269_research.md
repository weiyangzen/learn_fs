# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_7_7_0_sh_mask.h lines 24630-27070

## Purpose

This chunk is part of AMDGPU's generated NBIO 7.7.0 shift/mask header. It defines C preprocessor constants for bit positions and masks in PCIe root-port configuration registers. The range starts inside the `BIFPLR4_COMMAND` register, covers the rest of the `BIFPLR4` root-port/bridge configuration-space field map, and then begins the next address block, `nbio_pcie1_bifplr5_cfgdecp`, through the first `BIFPLR5_PREF_BASE_LIMIT` fields.

The header is not executable driver code. Its role is to provide the field-layout half of the NBIO 7.7.0 hardware ABI. The paired `nbio_7_7_0_offset.h` file supplies offsets such as `cfgBIFPLR4_STATUS`, `cfgBIFPLR4_PCIE_UNCORR_ERR_STATUS`, and `cfgBIFPLR5_COMMAND`; this file supplies the corresponding `__SHIFT` and `_MASK` constants needed to decode or update individual fields after a register has been read.

## Major Register Groups

The `BIFPLR4` portion is a near-complete PCIe root-port/PCI bridge configuration image:

- Conventional bridge header fields: command/status, revision/class-code bytes, cache line, latency, header type, BIST, bridge BAR placeholders, primary/secondary/subordinate bus numbers, IO/memory/prefetchable windows, capability pointer, interrupt line/pin, and extended bridge control.
- PCI power-management and PCIe capability fields: PM capability/status/control, PCIe capability metadata, Device Control/Status, Link Capability/Status, Slot Capability/Control/Status, Root Control/Capability/Status, Device Control 2, Link Status 2, and Slot Capability/Control/Status 2.
- Interrupt and identity capabilities: MSI capability/list, MSI message address, subsystem ID, MSI map, and AMD/vendor-specific enhanced capability headers plus two scratch registers.
- Virtual channel resources: VC enhanced capability header, port VC capability/control/status, and VC0/VC1 resource capability/control/status including traffic-class maps, arbitration selectors, VC IDs, and VC enable bits.
- Device serial number and Advanced Error Reporting: serial-number dwords, AER enhanced-capability header, uncorrectable error status/mask/severity, correctable error status/mask, AER capability/control, header logs, root error command/source ID, and TLP prefix logs.
- Secondary PCIe, isolation, and routing features: secondary PCIe capability, lane error status, per-lane 8 GT/s equalization controls for lanes 0-15, ACS capability header, multicast capability/control/address/block/overlay registers, LTR, and ARI capability/control fields.
- Downstream Port Containment and root-port PIO diagnostics: DPC capability/status/error-source fields, RP PIO status/mask/severity/system-error/exception classification, and RP PIO header/prefix logs.
- High-speed link features: PCIe ESM capability/header/status/control and dense `PCIE_ESM_CAP_1` through `PCIE_ESM_CAP_7` bitmaps, Data Link Feature capability/status, 16 GT/s link status and parity mismatch registers, 16 GT/s per-lane equalization controls, lane margining control/status for lanes 0-15, CCIX capability/header/ESM fields, 20 GT/s and 25 GT/s ESM lane equalization controls for lanes 0-15, and CCIX optimized TLP transport capability.

The final lines switch to `// addressBlock: nbio_pcie1_bifplr5_cfgdecp` and start the `BIFPLR5` root-port block. This partial section includes vendor ID, device ID, command, status, revision and class-code bytes, cache line, latency, header type, BIST, bridge BAR placeholders, bus numbering, IO limits, secondary status, memory limits, and the beginning of prefetchable memory limits. The remaining `BIFPLR5` fields are outside this chunk.

## Important APIs, Types, And Functions

There are no functions, structs, enums, or runtime data objects in this range. The public surface consists of 2,165 `#define` entries across 273 register-comment groups.

The macro naming convention is the contract:

- `BIFPLR4_<REGISTER>__<FIELD>__SHIFT` gives the zero-based bit offset of a field within the named register.
- `BIFPLR4_<REGISTER>__<FIELD>_MASK` gives the unshifted bit mask for that field in the containing register value.
- `BIFPLR5_*` follows the same scheme for the next PCIe root-port block, but this chunk contains only the opening bridge-header portion.

Consumers normally combine these constants with register access helpers and the matching offset macros from `nbio_7_7_0_offset.h`. The macros are meaningful only for the NBIO 7.7.0 register layout and the matching `BIFPLR4` or `BIFPLR5` address block.

## Control Flow

This header has no executable control flow. Runtime behavior comes from AMDGPU code that includes the generated NBIO headers, selects a register offset for the detected ASIC, reads or writes the hardware register, and applies these masks and shifts.

Typical use is:

1. Select the NBIO 7.7.0 root-port register offset, for example a `cfgBIFPLR4_*` or `cfgBIFPLR5_*` macro from the offset header.
2. Read the register through the appropriate AMDGPU PCIe/NBIO register access path.
3. Decode a field with `(value & FIELD_MASK) >> FIELD__SHIFT`.
4. For writable controls, perform a read-modify-write that preserves unrelated and reserved bits, inserts the shifted new field value, and writes through the same hardware access path.
5. Hardware performs the actual bridge decode, interrupt delivery, error reporting, link training, DPC containment, ESM/CCIX negotiation, lane margining, or other PCIe behavior.

The fields imply several hardware control flows outside this file: PCI bridge window programming, PM state changes, MSI setup, PCIe link capability/status reporting, virtual-channel mapping, AER and DPC reporting/clearing, root-port PIO diagnostics, ACS policy, ARI forwarding, multicast routing, LTR behavior, lane equalization, 16 GT/s parity checks, lane margining, ESM data-rate selection, and CCIX transport capability reporting.

## State And Persistence

The header itself is stateless and persists no data. It is a compile-time description of hardware register bit layouts.

The state described by the macros lives in NBIO/PCIe configuration registers. Some fields describe mostly static identity or capability information, such as vendor/device ID, class code, capability IDs and versions, supported PCIe link speeds and widths, slot/root capabilities, AER capability, DPC support, ARI support, ESM supported-rate bitmaps, and CCIX capability fields. Other fields describe writable control state, including PCI command enables, PM state, interrupt disable, Device Control, Root Control, MSI map enablement, VC/TC mapping, AER masks/severity, DPC policy, RP PIO masks/severity/sys-error/exception policy, ARI controls, ESM enable/data-rate selection, lane margining controls, and bridge IO/memory window registers.

Status and log fields are live hardware observations. Examples include PCI and secondary status error bits, Device Status, Link Status, Slot Status, Root Status, AER correctable/uncorrectable status, AER header and prefix logs, DPC status and error-source ID, RP PIO status and logs, ESM status, Data Link Feature status, 16 GT/s parity mismatch status, lane margining status, CCIX ESM status, and per-lane equalization presets. This generated header does not encode reset defaults, access widths, read-only/write-only behavior, write-one-to-clear semantics, polling requirements, or whether reads have side effects.

Persistence depends on hardware reset and power domains. Writable fields may be lost or restored across FLR, hot reset, GPU reset, suspend/resume, PCIe link reset, or NBIO power transitions according to higher-level driver and firmware logic; this file only names the bit positions.

## Dependencies And Integration Points

The direct dependency is the paired NBIO 7.7.0 offset header. For this chunk, entries around `cfgBIFPLR4_*` and `cfgBIFPLR5_*` in `nbio_7_7_0_offset.h` provide the register offsets while this chunk provides their field masks. Mixing these masks with offsets from another root-port number, another NBIO generation, or a different register family can silently decode or program the wrong bits.

Semantic dependencies are the PCI and PCI Express specifications for type-1 bridge headers, PM capability, MSI, PCIe capability, slot/root controls, VC, device serial number, AER, secondary PCIe capability, ACS, multicast, LTR, ARI, DPC, RP PIO, Data Link Feature, 16 GT/s PHY/equalization, lane margining, and high-speed link reporting. AMD-specific dependencies include the NBIO 7.7 generated register specification, ESM capability layout, CCIX capability/ESM fields, and the hardware access path used by AMDGPU for NBIO PCIe configuration registers.

Integration points include:

- AMDGPU NBIO 7.7 support that includes generated `asic_reg/nbio` headers for register addressing and bitfield decode.
- PCIe root-port setup and diagnostics for command/status, bridge windows, bus numbering, PM, link, slot, root, MSI, and subsystem identity fields.
- RAS/AER handling paths that decode correctable/uncorrectable status, masks, severity, root error information, header logs, and TLP prefix logs.
- DPC and RP PIO error-containment paths that inspect trigger state, source IDs, PIO completion exceptions, masks, severity, sys-error policy, and logs.
- Link-management and bring-up code for equalization, 16 GT/s parity, lane margining, ESM, Data Link Feature, CCIX ESM, and 20/25 GT/s per-lane presets.
- Isolation and routing policy for ACS, ARI, multicast, VC/TC mapping, LTR, and bridge resource windows.

## Risks

The main risk is silent hardware misprogramming. These macros are generated ABI constants; if a mask or shift is wrong, or if a caller pairs it with the wrong offset, compiler checks will not catch the error. A single bit error can alter command enablement, bridge apertures, MSI routing, AER severity policy, DPC behavior, ACS isolation, link equalization, lane margining, or CCIX/ESM state.

The chunk boundaries split logical registers. The range begins after the first `BIFPLR4_COMMAND` shifts and ends before `BIFPLR5_PREF_BASE_LIMIT` is complete, so adjacent chunks are required for full per-file documentation and for complete register-group audits.

Repeated root-port layouts invite copy/paste mistakes. `BIFPLR4` and `BIFPLR5` names differ only by the port number for many fields, and other `BIFPLR*` blocks in this generated file share similar structure. A consumer can compile while targeting the wrong root port.

Reserved and status fields require hardware-specific handling. Generated `RESERVED` masks do not imply safe writes. PCI status, AER status, DPC status, RP PIO logs, slot/root status, link status, and margining status may have latch, clear-on-write, or sequencing requirements not represented here.

High-speed link fields are platform sensitive. Lane equalization, 16 GT/s parity, margining, ESM, CCIX, retimer/reach-related fields, and 20/25 GT/s presets may depend on board wiring, link partner, firmware policy, and training state. Normal boot testing may not exercise these paths, so stale generated constants can remain hidden.

## Test Signals

Useful validation signals include:

- The AMDGPU tree builds with NBIO 7.7.0 generated headers included, proving referenced `BIFPLR4_*` and `BIFPLR5_*` macro names resolve.
- Static generator checks confirm that every complete `BIFPLR4` register group in this chunk has a matching `cfgBIFPLR4_*` offset and that the partial `BIFPLR5` groups align with `cfgBIFPLR5_*` offsets.
- Hardware register dumps on NBIO 7.7 systems decode plausible PCI bridge headers, bus/window registers, PM state, PCIe capability fields, MSI state, link status, slot/root status, and AER/DPC logs when compared with `lspci -vvxxx`, AMDGPU debugfs/register dumps, or vendor diagnostics.
- Error-path testing or field observation validates AER correctable/uncorrectable status, masks, severity, root error source, DPC trigger/source state, and RP PIO classification/log fields.
- PCIe link diagnostics cover negotiated speed/width, 8 GT/s and 16 GT/s equalization status, 16 GT/s parity mismatch registers, lane margining control/status, Data Link Feature status, ESM status/control/capability bitmaps, and 20/25 GT/s per-lane presets.
- Isolation and routing tests exercise ACS, ARI forwarding, VC/TC mapping, multicast controls, LTR controls, and bridge resource-window programming without cross-programming neighboring root-port blocks.
- Reset and power-management testing verifies that writable fields are restored by higher-level NBIO/PCIe code after FLR, hot reset, GPU reset, suspend/resume, or link reset rather than relying on this header for defaults or persistence.
