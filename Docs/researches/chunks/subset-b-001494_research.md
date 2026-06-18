# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/bif/bif_5_1_sh_mask.h lines 21115-25046

## Purpose

This chunk is a generated AMD BIF 5.1 register field mask/shift section. It does not contain executable logic; it defines C preprocessor constants that describe bit positions inside PCI/PCIe/BIF registers for AMD GPU support code. The companion address header is `bif_5_1_d.h`; this file supplies the `*_MASK` and `*__SHIFT` values used with the register addresses from that header.

The covered range contains 3,932 `#define` lines. It starts in the middle of the `D3F4_STATUS` field list, completes the rest of the `D3F4` function-4 PCI/PCIe capability and extended capability masks, covers the much larger `D3F5` function-5 PCIe port/link-control block, then enters wrapper-level `PSX80_WRP_*` and `PSX81_WRP_*` strap/control definitions. The range ends in the middle of the `PSX81_WRP_BIF_STRAP_MISC_PORT_D` family, so the final per-file report must merge this with the next chunk before treating the `PSX81` wrapper family as complete.

## Important APIs, Types, And Macros

There are no functions, structs, enums, or runtime APIs in this chunk. The interface is the generated macro naming contract:

- `REGISTER__FIELD_MASK` gives the already-positioned bit mask for a field.
- `REGISTER__FIELD__SHIFT` gives the least significant bit index for extraction or insertion.
- Full-register fields use masks such as `0xffffffff` and shift `0`.
- Register prefixes must be paired with the matching address macros in `bif_5_1_d.h`; the mask header alone does not identify the access method.

Major macro groups in this chunk:

- `D3F4_*`: 1,040 macro definitions across 131 register names. These complete function 4 PCI config-space fields and capabilities, including status/class/header/BIST, bridge bus windows, interrupt and bridge control, PMI, PCIe capability registers, device/link/slot/root capability and status, MSI and MSI-map fields, subsystem ID, vendor-specific and virtual-channel extended capabilities, AER status/mask/severity/header-log/root-error fields, secondary PCIe capability, lane equalization controls for lanes 0-15, ACS, and multicast capability/control/address/block/overlay fields.
- `D3F5_*`: 1,938 macro definitions across 196 register names. This is the largest section and includes `D3F5_PCIE_PORT_INDEX/DATA`, `PCIEP_*` private port registers, transmit/receive datapath controls, flow-control credit advertisement/allocation/status, replay and requester ID fields, error controls and injection registers, link-controller controls (`PCIE_LC_CNTL*`, training, width, speed, CDR, lane, equalization coefficient, and state registers), hot-plug GPIO interrupt registers, function-5 PCI config-space and capability fields, AER/ACS/multicast/VC/vendor-specific extended capability fields, and lane equalization controls for lanes 0-15.
- `PSX80_WRP_*`: 626 macro definitions across 87 register names. These describe wrapper-level control, timing, strap, efuse, lane counter, delay-line, DTM, register-adaptation, and per-port link/ASPM/training strap fields for PSX80. Port strap definitions cover ports A-E in this range.
- `PSX81_WRP_*`: 324 macro definitions across 38 register names. These mirror a subset of the PSX80 wrapper strap/control set for PSX81, including feature-enable, PI, link-speed, LC miscellaneous, error-ignore, ACS, SSID, lane equalization, hold-training, port-is-sideband, and port A-D strap families. The port D `BIF_STRAP_MISC` family is incomplete at the chunk boundary.
- `C_PCIE_INDEX` and `C_PCIE_DATA`: full-width index/data masks for another PCIe indirect register aperture.

Important specific field families include:

- PCIe standard capability fields: max payload/read request size, relaxed ordering, no-snoop, FLR, link speed/width, ASPM and clock power management, link training, slot hotplug, root PME/error controls, completion timeout, ARI, atomic operations, ID-based ordering, LTR, OBFF, TLP prefix support, and Gen3 equalization status.
- Interrupt/MSI fields: MSI enable, multiple-message capability/enable, 64-bit capable, per-vector mask capability, MSI message address/data, MSI-map enable/fixed/64-bit/address values, bridge interrupt line/pin, and wrapper autonomous bandwidth interrupt bits.
- AER/error fields: uncorrectable and correctable error status/mask/severity bits, ECRC generation/checking, first error pointer, header logs, TLP prefix logs, root error command/status/source ID, RX ignore controls, generated LCRC/ECRC error bits, error injection controls, and completion/unsupported-request handling.
- Link and PHY tuning fields: LC target speed, link width, lane reversal, hardware/software/autonomous speed changes, equalization wait and coefficient controls, FS/LF presets, bypass equalization, CDR controls, N_FTS, lane power/downconfigure, TX/RX credit and sequence controls, and lane error/equalization status.
- Strap and wrapper fields: advertised capabilities for AER/ECN/ARI/ACS/LTR/OBFF/MSI, subsystem IDs, Gen2/Gen3 compliance/kill/force modes, target link speed, ASPM latencies, de-emphasis, single-path clock modes, enhanced hotplug, ECRC, BCH ECC, error-reporting disable, and debug/test/DFT options.

## Control Flow

This header has no runtime control flow. It is a collection of compile-time substitutions used by driver code that performs register reads, read-modify-writes, writes, and polling.

The operational pattern for consumers is:

1. Read a 32-bit register through the AMDGPU MMIO or indexed-register helper appropriate for the address macro.
2. Extract a field with `(value & REGISTER__FIELD_MASK) >> REGISTER__FIELD__SHIFT`, or clear and insert a new field value with the mask and shift pair.
3. Write the updated register back, or poll until a status bit or field reaches an expected value.

The order of definitions follows generated register-map order, not hand-written control flow. Function and wrapper boundaries are important: this range begins after earlier `D3F4_COMMAND` and initial `D3F4_STATUS` bits, transitions from `D3F4_PCIE_MC_OVERLAY_BAR1` into `D3F5_PCIE_PORT_INDEX`, then from `D3F5_PCIE_MC_OVERLAY_BAR1` into `C_PCIE_INDEX/DATA` and `PSX80_WRP_*`, and later from `PSX80_WRP_DELAYLINE_STATUS` into `PSX81_WRP_*`.

## State And Persistence Behavior

The header itself stores no mutable state and has no persistence behavior. State changes occur only in hardware registers when other driver code uses these constants.

The affected hardware state is persistent until overwritten or reset by GPU reset, PCIe reset, function-level reset, BACO/power transition, firmware action, or another driver path. In this chunk, that state includes:

- PCI config-space and PCIe capability exposure for functions 4 and 5.
- PCIe bridge windows, bus numbers, interrupt routing, MSI programming, and subsystem IDs.
- Link negotiation, speed, width, ASPM, common-clock, retrain, equalization, and lane-level tuning state.
- AER/error-reporting policy, error status latches, header logs, root error status, and error-injection controls.
- RX/TX sequence, replay, flow-control credit, completion-timeout, and unsupported-request behavior.
- Wrapper straps that may be latched or firmware-influenced, including advertised features, Gen2/Gen3 modes, ECRC/BCH/ACS/ARI/LTR/OBFF support, port link configuration, sideband-port marking, and hold-training bits.
- Delay-line, DTM, efuse, lane counter, and wrapper debug/test control fields.

Because these constants are raw bit definitions, they provide no locking, validation, sequencing, or side-effect protection. Any ordering constraints around link training, reset, strap latching, or error clearing are enforced by the calling driver/firmware code and hardware specification, not by this header.

## Dependencies And Integration Points

The direct dependency is the generated AMD ASIC register contract: macro names and numeric values must match the BIF 5.1 register database and the companion `bif_5_1_d.h` address definitions.

Likely consumers are low-level AMDGPU/PowerPlay/NBIO/BIF code paths that include generation-specific ASIC register headers and use helper macros or register accessors to program PCIe and BIF registers. Integration points include:

- PCIe config-space setup for GPU functions, including device/link/slot/root capability control and status.
- MSI and interrupt setup paths that need `D3F4_*` or `D3F5_*` MSI fields.
- PCIe link bring-up, retraining, speed changes, lane equalization, and ASPM/power-management flows.
- AER, ACS, virtual-channel, multicast, vendor-specific, and secondary PCIe extended capability programming.
- Error diagnostics and recovery code that reads status/masks, clears latched errors, captures header logs, or toggles error injection.
- Wrapper/strap initialization code that programs PSX80/PSX81 port behavior, feature exposure, DTM/delay-line behavior, efuse-derived controls, and hold-training states.

The `D3F4` and `D3F5` prefixes are function-specific. The `PSX80_WRP` and `PSX81_WRP` prefixes are wrapper-instance-specific. Mixing fields across functions or wrapper instances can compile successfully while targeting the wrong register layout.

## Risks And Edge Cases

The primary risk is silent hardware misprogramming. A wrong mask, shift, function prefix, wrapper prefix, or address/mask pairing compiles cleanly but can set the wrong bit, fail to clear an error, advertise unsupported PCIe capabilities, or destabilize link training.

This chunk has boundary splits. It starts after the first `D3F4_STATUS` fields (`INT_STATUS` and `CAP_LIST`) and ends before the rest of `PSX81_WRP_BIF_STRAP_MISC_PORT_D`; per-field completeness checks must reconcile adjacent chunks. The `D3F4_COMMAND` family is visible immediately before this range but is not part of the assigned chunk.

Generated lane and port families are repetitive and easy to misuse. Lane equalization fields are emitted for lanes 0-15, with alternating low-half/high-half masks in each 32-bit register. Wrapper port straps repeat across A-E for PSX80 and A-D for PSX81 in this range. Reviewers should watch for off-by-one lane numbers, lexicographic sorting surprises, and accidental use of a port A mask against another port's register.

Several fields are disruptive or security-sensitive:

- Link control, hold-training, speed override, bypass equalization, CDR, lane width, and Gen2/Gen3 force/kill fields can prevent PCIe link recovery or reduce negotiated capability.
- Error-ignore and error-reporting-disable fields can hide real protocol errors.
- ACS/ARI/atomic/LTR/OBFF/VC/multicast strap fields can change IOMMU isolation, routing, ordering, or capability exposure.
- ECRC/BCH/ECC and error-injection fields can affect reliability diagnostics or intentionally create malformed traffic.
- Full-width scratch/reserved/vendor fields should not be treated as safe arbitrary write targets merely because they have `0xffffffff` masks.

There is no type safety around signedness or width. Callers should use the driver's normal unsigned 32-bit register types and should mask shifted input values before writing multi-bit fields.

## Test Signals

Useful validation is mostly static, build, and hardware-behavior oriented:

- Build all AMDGPU translation units that include `bif_5_1_sh_mask.h`; renamed or missing macros should fail compile.
- Run static generation checks that every `*_MASK` has the expected matching `*__SHIFT`, allowing for known chunk-boundary splits during chunk review.
- Compare register prefixes in this mask header against address macros in `bif_5_1_d.h` to catch stale or cross-generation field names.
- PCIe enumeration tests should confirm function 4/function 5 class, bridge windows, MSI/MSI-map, subsystem ID, and capability-list behavior.
- Link bring-up, retrain, Gen1/Gen2/Gen3 speed transitions, width negotiation, ASPM, common-clock, and suspend/resume tests should exercise LC, lane equalization, PSX80/PSX81 strap, and hold-training fields.
- AER/error tests should validate uncorrectable/correctable status/mask/severity, ECRC generation/checking, root error status, header/TLP prefix logs, and RX/TX error handling.
- ACS/ARI/atomic/LTR/OBFF/VC/multicast tests should verify that advertised capabilities and control bits match platform policy and IOMMU expectations.
- Hardware diagnostics should inspect RX/TX flow-control credits, replay/sequence counters, error injection, BCH/ECC behavior, lane error status, DTM/delay-line status, and wrapper debug/test fields after controlled operations.

## Cross-Chunk Notes

The final per-file research should merge this with earlier and later chunks for `bif_5_1_sh_mask.h`. This chunk is not a complete file-level view: it begins mid-`D3F4_STATUS` and ends mid-`PSX81_WRP_BIF_STRAP_MISC_PORT_D`. Its main contribution is the dense function-4/function-5 PCIe capability and function-5 PCIe port-control coverage plus the beginning of PSX80/PSX81 wrapper strap and timing definitions.
