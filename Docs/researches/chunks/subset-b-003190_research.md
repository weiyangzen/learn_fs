# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_7_2_0_sh_mask.h lines 73371-75796

## Scope

This chunk is a generated AMDGPU NBIO 7.2.0 shift/mask header segment. It contains 2,164 `#define` field-layout macros and 260 register or address-block comments. There are no functions, structs, enums, variables, allocations, locks, or executable statements in this range.

The range starts inside the `BIFPLR0_0_LANE_2_EQUALIZATION_CNTL_16GT` register family, covers the remaining `BIFPLR0_0` PCIe lane/equalization, margining, CCIX, and enhanced speed mode definitions, then enters the `nbio_pcie0_bifplr1_cfgdecp` address block. It continues through `BIFPLR1_0` PCI/PCIe configuration-space and extended-capability field definitions and stops at the `BIFPLR1_0_PCIE_ESM_CAP_7` register comment before that register's field macros appear. Adjacent chunks are required to see the beginning of lane 2's 16 GT equalization register and the field layout for `PCIE_ESM_CAP_7`.

## Purpose

`nbio_7_2_0_sh_mask.h` is the bitfield half of AMD's generated NBIO 7.2.0 register interface. For each hardware register field it exports:

- `<REGISTER>__<FIELD>__SHIFT`, the bit position used to encode or decode the field.
- `<REGISTER>__<FIELD>_MASK`, the mask used to isolate, preserve, clear, or update the field.

This chunk describes PCIe root-port style configuration and extended-capability registers for two BIFPLR instances. The `BIFPLR0_0` portion covers Gen4/16 GT lane transmit presets, software-assisted PCIe lane margining, CCIX capability/control/status fields, and CCIX enhanced speed mode support at 20 GT and 25 GT. The `BIFPLR1_0` portion covers conventional PCI bridge config registers, PCI power management, PCIe capability registers, MSI/SSID/vendor-specific capabilities, VC resources, device serial number, advanced error reporting, secondary PCIe and per-lane equalization, ACS, multicast, L1 PM substates, downstream port containment, root-port PIO logging, and PCIe enhanced speed mode capability bitmaps.

Although this repository path is under a `ceph-client` source mirror, the file is AMDGPU hardware metadata. It has no direct Ceph or distributed-filesystem behavior.

## Important Macro Families

The `BIFPLR0_0` tail of the chunk covers high-speed lane and capability blocks:

- `LANE_3_EQUALIZATION_CNTL_16GT` through `LANE_15_EQUALIZATION_CNTL_16GT` provide downstream/upstream 16 GT TX preset fields per lane. The first lines also complete the lane 2 16 GT preset masks started in the previous chunk.
- `PCIE_MARGINING_ENH_CAP_LIST`, `MARGINING_PORT_CAP`, and `MARGINING_PORT_STATUS` describe the PCIe margining extended-capability header and port readiness/software-readiness bits.
- `LANE_0_MARGINING_LANE_CNTL/STATUS` through `LANE_15_MARGINING_LANE_CNTL/STATUS` repeat receiver number, margin type, usage model, and margin payload control/status fields for each lane.
- `PCIE_CCIX_*` defines CCIX capability-list, header, capability, required/optional enhanced speed mode, status, and control fields including optimized buffer flush/fill, no-fallback behavior, enable bits, and selected enhanced speed mode.
- `ESM_LANE_0_EQUALIZATION_CNTL_20GT` through `ESM_LANE_15_EQUALIZATION_CNTL_25GT` provide downstream/upstream TX preset and RX preset hint fields for CCIX/enhanced speed mode operation at 20 GT and 25 GT.
- `PCIE_CCIX_TRANS_CAP` and `PCIE_CCIX_TRANS_CNTL` describe translation capability and enable/control fields such as max/xlat translate speed, max execute state, and selected execute state.

The `BIFPLR1_0` config-space section starts at `// addressBlock: nbio_pcie0_bifplr1_cfgdecp` and maps a PCI/PCIe bridge/root-port configuration image:

- Conventional PCI fields include vendor/device ID, command/status, revision/class codes, cache line, latency, header/BIST, secondary/subordinate bus numbering, I/O and memory base/limit windows, prefetchable windows, ROM base, interrupt line/pin, bridge control, and vendor/adapter capability fields.
- PCI power-management fields include PME version/support, D-state controls, PME enable/status, data select/scale, and bus power/clock control bits.
- PCIe capability fields include device/link/slot/root capabilities, controls, and statuses, plus second-generation capability registers such as `DEVICE_CAP2`, `DEVICE_CNTL2`, `LINK_CAP2`, `LINK_CNTL2`, `LINK_STATUS2`, and slot capability/control/status 2.
- MSI and SSID fields define MSI enable/multiple-message controls, 32/64-bit message addresses, message data, and subsystem vendor/device IDs.
- Vendor-specific, virtual-channel, and VC0/VC1 resource fields expose capability-list headers, arbitration table offsets, TC/VC maps, load/select bits, resource statuses, and port VC control/status.
- Device serial number fields expose the two 32-bit serial-number dwords.
- Advanced error reporting fields cover uncorrectable and correctable error status/mask/severity bits, ECRC and multi-header controls, TLP header and prefix logs, root error command/status, and error source IDs.
- Secondary PCIe capability and per-lane equalization fields cover `LINK_CNTL3`, lane error status, and lane 0-15 downstream/upstream TX preset and RX preset hint fields for normal PCIe equalization.
- ACS fields expose source validation, translation blocking, peer-to-peer redirection, upstream forwarding, egress control, and direct translated peer-to-peer capability/control bits.
- Multicast fields expose group/window/ECRC capabilities, multicast enable/group count, base addresses, receive/block vectors, untranslated-block vectors, and overlay BAR fields.
- L1 PM substate fields expose L1.1/L1.2 support/enables, common-mode restore timing, power-on scale/value, and LTR threshold fields.
- Downstream Port Containment and Root Port PIO fields expose DPC trigger/completion/interrupt/error controls, DPC status, error source ID, PIO mask/severity/system-error/exception controls, and PIO header/prefix log fields.
- `PCIE_ESM_CAP_LIST`, `PCIE_ESM_HEADER_*`, `PCIE_ESM_STATUS`, `PCIE_ESM_CTRL`, and `PCIE_ESM_CAP_1` through `PCIE_ESM_CAP_6` describe PCIe enhanced speed mode capability metadata, lock/select bits, and dense bitmaps for supported link speeds from 8.0 GT/s through 24.9 GT/s. `PCIE_ESM_CAP_7` begins at the end of the chunk.

## APIs, Types, And Functions

There are no callable APIs or C types in this chunk. The public interface is the generated macro namespace. The constants are untyped preprocessor integer literals, mostly using an `L` suffix, and encode only bit positions and masks.

These definitions do not include register addresses, reset values, read/write permissions, write-one-to-clear behavior, firmware ownership, sequencing requirements, or hardware side effects. Consumers must combine these macros with companion generated address metadata from `nbio_7_2_0_offset.h` and AMDGPU register helpers such as `REG_GET_FIELD`, `REG_SET_FIELD`, `RREG32_SOC15`, `WREG32_SOC15`, or the PCIe/NBIO access path used for the relevant register aperture.

## Control Flow

This header has no local runtime control flow. Runtime flow is external:

1. AMDGPU code selects a `BIFPLR0_0_*` or `BIFPLR1_0_*` register address from the generated NBIO offset metadata.
2. The code reads a PCIe/NBIO register, extracts fields with the `__SHIFT` and `_MASK` constants, or composes a new value while preserving unrelated and reserved bits.
3. The decoded or written fields affect PCIe bridge configuration, link status reporting, link equalization, lane margining, CCIX/enhanced speed mode setup, error reporting, power-management state, access-control behavior, multicast routing, or root-port containment/logging.

Several implied hardware flows are asynchronous to software: PCIe link training and equalization, lane margining command/status handshakes, enhanced speed mode selection/lock, AER/DPC error latching and reporting, MSI delivery, L1 PM substate entry/exit timing, VC arbitration/resource state, and bridge window decoding.

## State And Persistence Behavior

The header owns no state and persists nothing. It describes hardware-visible state in NBIO PCIe configuration and extended-capability registers. Persistence is determined by GPU reset domains, PCIe fundamental/hot/warm reset, function-level reset where supported, firmware/BIOS setup, driver initialization, suspend/resume restore, and explicit AMDGPU writes.

Represented state includes static identifiers and capability bits, writable command/control bits, bridge decode windows, interrupt/MSI routing values, link capabilities and negotiated status, error status/mask/severity latches, log registers, power-management controls, lane equalization presets, lane margining controls/statuses, CCIX/enhanced speed selections, ACS policy bits, multicast tables, L1 PM timing controls, and DPC/RP PIO diagnostic state.

Call sites must not infer reset persistence or write semantics from the mask definitions alone. Status fields may be live, sticky, write-one-to-clear, or read-only depending on the hardware specification; this header only provides field geometry.

## Dependencies And Integration Points

This chunk depends on AMD's generated NBIO 7.2.0 register database and must remain synchronized with sibling generated metadata:

- `nbio_7_2_0_offset.h` provides address offsets such as `cfgBIFPLR1_0_*` and related NBIO register locations.
- Other generated ASIC register headers provide comparable layouts for neighboring NBIO revisions, which helps detect drift between hardware generations.
- AMDGPU consumers access these fields through generated include stacks and SOC15/NBIO/PCIe register access helpers rather than through functions in this header.

Integration points are PCIe and NBIO code paths: device enumeration and bridge setup, link capability/status reporting, link-speed and equalization management, lane margining diagnostics, CCIX/enhanced speed mode support, AER/DPC handling, MSI configuration, ASPM/L1 PM substate policy, ACS/IOMMU isolation policy, multicast/VC resource programming, and error/debug log collection. The definitions are also useful for register-dump decoders and hardware bring-up scripts that need stable field names.

## Risks And Edge Cases

- Generated shift/mask drift can compile cleanly while causing software to read or write the wrong PCIe bit, leading to broken link training, incorrect advertised capabilities, missed errors, invalid bridge windows, or unsafe access-control policy.
- The range starts and ends mid-register-family. Whole-file research must reconcile lane 2 16 GT equalization fields from the previous chunk and `PCIE_ESM_CAP_7` fields from the next chunk before treating those families as complete.
- Several register families are per-lane repetitions across lanes 0-15. A single generated or copy error can affect only one lane, showing up as width-dependent equalization, margining, or speed-mode failures.
- Error reporting, DPC, and RP PIO registers often contain sticky or clear-on-write status fields. Generic read-modify-write code must preserve/clear fields according to the hardware spec, not merely according to masks.
- Bridge base/limit and ACS fields affect memory/I/O routing and isolation. Incorrect writes can expose peer-to-peer traffic unexpectedly, block legitimate transactions, or cause enumeration/resource assignment failures.
- L1 PM substate timing fields and CCIX/enhanced speed mode selections are link-partner sensitive. Values that work on one platform may cause resume latency, training instability, or throughput regressions on another.
- Lane margining and equalization controls can be diagnostic or negotiated state. Polling code needs timeouts and must tolerate unsupported lanes, inactive link widths, and transient status while training is in progress.
- Some fields are capability/status mirrors rather than software-owned controls. Treating read-only capability bits as programmable policy can produce ineffective writes and misleading register traces.

## Test Signals

- Build AMDGPU with NBIO 7.2.0 support enabled. Compile-time coverage catches missing or renamed generated macros used by consumers.
- Run generated-header consistency checks: every field should have compatible `__SHIFT` and `_MASK` values, masks within a register should not overlap unexpectedly, and repeated lane 0-15 families should match except for lane number.
- Cross-check `BIFPLR0_0_*` and `BIFPLR1_0_*` field names against `nbio_7_2_0_offset.h` so every layout maps to a known register address.
- On supported hardware, validate PCIe enumeration, bridge window assignment, negotiated link width/speed, Gen3/Gen4 equalization status, lane error status, suspend/resume, GPU reset recovery, and link retraining.
- Exercise diagnostics where available: PCIe lane margining, AER correctable/uncorrectable error logging, DPC containment paths, RP PIO logs, MSI delivery, L1 PM substate transitions, ACS policy, VC/multicast configuration, and enhanced speed mode capability reporting.
- For any code that writes these fields, inspect register traces to ensure reserved bits are preserved, sticky error bits are cleared intentionally, per-lane writes are bounded by the active link width, and link-sensitive fields are not changed while training is active unless the hardware sequence requires it.
