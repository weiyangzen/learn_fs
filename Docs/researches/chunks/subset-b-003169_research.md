# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_7_2_0_sh_mask.h lines 22072-24500

## Scope

This chunk is a generated AMDGPU NBIO 7.2.0 shift/mask header segment. It contains preprocessor constants for bitfield shifts and masks, not executable code. The range starts in the middle of the `BIFPLR2_LANE_9_MARGINING_LANE_CNTL` field list, completes the remaining BIFPLR2 lane-margining fields for lanes 9-15, covers BIFPLR2 CCIX/ESM capability and equalization metadata, then enters the `nbio_pcie0_bifplr3_cfgdecp` address block and maps a large portion of BIFPLR3 PCIe configuration and extended-capability fields through `BIFPLR3_LANE_2_MARGINING_LANE_STATUS`.

Although the repository path is under a `ceph-client` mirror, this file is AMD GPU hardware register metadata. It has no Ceph or distributed-filesystem behavior.

## Purpose

`nbio_7_2_0_sh_mask.h` provides symbolic bit positions and bit masks for NBIO 7.2.0 registers. Driver code combines these constants with sibling offset macros, register-access helpers, and hardware sequencing code to read, write, or decode specific PCIe/NBIO fields without embedding raw bit arithmetic at each call site.

This chunk specifically describes PCIe root-port-like BIFPLR2 and BIFPLR3 field layouts: lane margining, CCIX ESM capabilities, PCIe command/status and capability fields, MSI programming fields, virtual-channel/resource controls, advanced error reporting, secondary PCIe equalization, ACS and multicast, L1 PM substates, DPC/RP PIO error logging, ESM supported data-rate maps, data-link feature exchange, 16 GT/s PHY status, and the beginning of BIFPLR3 margining lane controls.

## Important Macro Families

The opening BIFPLR2 lane margining tail defines control/status fields for lanes 9-15. Each lane has `RECEIVER_NUMBER`, `MARGIN_TYPE`, `USAGE_MODEL`, and `MARGIN_PAYLOAD` fields in the control register and matching `*_STATUS` fields in the status register. The chunk starts after the first lane-9 shift definitions, so the prior chunk is required for the complete `BIFPLR2_LANE_9_MARGINING_LANE_CNTL` definition.

The BIFPLR2 CCIX group maps capability-list headers, CCIX vendor/capability headers, ESM capability bits, required/optional ESM support, ESM current data-rate and calibration-complete status, and ESM control fields for selecting data rates, requesting calibration, enabling ESM, choosing equalization timeouts, and describing link reach or retimer presence. It also maps per-lane 20 GT/s and 25 GT/s ESM equalization presets for lanes 0-15, with downstream and upstream transmit preset nibbles.

The BIFPLR3 block begins with PCI configuration-space fields: vendor/device IDs, command and status bits, class/revision/header/BIST fields, bridge bus-number and I/O/memory aperture fields, ROM base, interrupt line/pin, bridge control, vendor capability, adapter ID, power-management capability/status/control, PCIe capability, device capability/control/status, link capability/control/status, slot/root capability/control/status, device/link capability 2, and MSI capability/message address/data fields.

The BIFPLR3 extended PCIe capability groups cover vendor-specific capability headers, virtual-channel resources for VC0 and VC1, device serial number, AER uncorrectable/correctable status/mask/severity fields, AER capability/control, TLP header and prefix logs, root error command/status/source ID, secondary PCIe link control 3, lane error status, and per-lane equalization controls for lanes 0-15.

The later BIFPLR3 groups map ACS capability/control, multicast capability/control/address/receive/block/overlay BAR fields, L1 PM substate capability/control fields, DPC capability/control/status/source ID, RP PIO status/mask/severity/system-error/exception fields and header/prefix logs, ESM capability-list/header/status/control fields, seven dense ESM capability bitmaps covering supported rates from 2.5 GT/s through 28.0 GT/s, data-link feature exchange, 16 GT/s PHY enhanced capability fields, 16 GT/s equalization/parity status fields, 16 GT/s per-lane preset controls for lanes 0-15, and the start of BIFPLR3 PCIe margining lane controls through lane 2 status.

## APIs, Types, And Functions

There are no C functions, types, variables, inline helpers, callbacks, allocations, locks, or system calls in this chunk. The public surface is the generated macro namespace:

- `<REGISTER>__<FIELD>__SHIFT` constants give the bit position for a field.
- `<REGISTER>__<FIELD>_MASK` constants give the unshifted mask for that field inside the register value.
- Repeated lane macros encode per-lane field layouts for margining and equalization registers.
- Capability-list macros encode standard PCIe enhanced-capability header fields such as `CAP_ID`, `CAP_VER`, and `NEXT_PTR`.

Consumers are expected to use these with companion generated headers such as `nbio_7_2_0_offset.h` for register addresses and AMDGPU register helper macros for field extraction and insertion.

## Control Flow

This header has no local runtime control flow. The implied external flow is:

1. AMDGPU code selects NBIO 7.2.0 register offsets for the active ASIC/IP block.
2. Code reads a register, extracts a field with the matching `*_MASK` and `*_SHIFT`, and interprets it as PCIe/NBIO state.
3. For writable fields, code constructs a new field value using the same constants and writes or read-modify-writes the hardware register.
4. Hardware then performs protocol actions such as link training, equalization, margining, ESM calibration, DPC triggering, AER reporting, MSI delivery, L1 substate entry, ACS/multicast filtering, or virtual-channel negotiation.

The most sequencing-sensitive external flows represented here are PCIe link retraining/equalization, lane margining, ESM calibration and rate selection, DPC interrupt/completion handling, AER status clear/reporting, L1 PM substate programming, MSI enable/address/data programming, and bridge/resource-window configuration.

## State And Persistence Behavior

The file owns no software state and persists nothing. It describes hardware-visible fields whose lifetime is controlled by the NBIO/PCIe hardware, firmware initialization, PCI configuration writes, reset domains, power-management transitions, and driver restore paths.

State represented in this chunk includes PCI command enables, status/error bits, bridge apertures, link speed/width/training state, ASPM and L1 substate policy, MSI enable/address/data state, AER status/mask/severity and captured TLP logs, DPC/RP PIO status and logs, equalization presets and status, lane error/parity fields, margining control/status payloads, ESM calibration and supported-rate bitmaps, DLF negotiated support, ACS controls, and multicast filtering/overlay BAR state.

Many fields are status or log style fields (`*_STATUS`, `*_ERR_STATUS`, `*_HDR_LOG*`, `*_PREFIX_LOG*`, `*_PARITY_MISMATCH_STATUS*`, `*_LANE_ERROR_STATUS`). Their clear behavior, latch timing, read side effects, and reset persistence are not encoded in this generated mask header and must be derived from hardware documentation and the driver sequences that use these macros.

## Dependencies And Integration Points

This chunk depends on AMD's generated NBIO 7.2.0 register database and must remain synchronized with the same-version offset/default headers. Register names in this file need matching offsets in `nbio_7_2_0_offset.h`; otherwise a caller can correctly manipulate a bitfield in the wrong register address.

Primary integration points are AMDGPU NBIO/PCIe initialization, Linux PCI core configuration interactions, GPU reset and FLR recovery, interrupt/MSI setup, runtime power management, suspend/resume restore, link training and equalization handling, AER/RAS diagnostic paths, DPC containment/recovery, and any diagnostic or bring-up tooling that inspects lane margining, ESM, DLF, or 16 GT/s PHY state.

The BIFPLR3 fields align with standard PCIe configuration and extended-capability concepts, so they sit at the boundary between generic PCIe semantics and AMD ASIC-specific register access. Firmware, BIOS/UEFI, PSP/SMU, Linux PCI core, and AMDGPU driver code may all influence the final values observed in these registers.

## Risks And Edge Cases

- Generated field drift can compile cleanly but corrupt behavior at runtime: a wrong shift or mask can silently modify adjacent PCIe control bits, miss status bits, or clear unrelated error state.
- This chunk begins and ends mid-register-family. Complete analysis of `BIFPLR2_LANE_9_MARGINING_LANE_CNTL` requires the previous chunk, and complete BIFPLR3 lane-margining coverage requires the following chunk.
- PCIe command/status, device/link control, MSI, bridge window, AER, DPC, ACS, L1 PM, and multicast registers contain adjacent fields with different access semantics. Generic read-modify-write code can be unsafe when fields are write-one-to-clear, sticky, hardware-updated, or firmware-owned.
- Link training, equalization, ESM calibration, and lane margining fields are timing-sensitive. Writes may need polling, delays, retrain checks, or coordination with power/link state before follow-up access.
- AER and DPC status/log fields capture failure evidence. Overbroad masks or premature clears can lose the first-error pointer, TLP header/prefix logs, DPC trigger reason, or RP PIO error source.
- MSI fields affect interrupt routing and masking. Incorrect `MSI_EN`, address, data, 64-bit, or per-vector masking interpretation can result in lost or misrouted interrupts.
- ESM capability bitmaps are dense and mechanically generated. Off-by-one mapping between a named rate such as `ESM_20P0G` and its bit position could misadvertise a supported data rate or select an invalid equalization path.
- The BIFPLR3 block resembles a PCIe bridge/root-port capability layout. Consumer code must not assume endpoint-only semantics just because the broader AMDGPU device is a GPU.
- Reserved fields are represented by full-width `RESERVED` masks in some registers. These are documentation of layout, not permission to write arbitrary values.

## Test Signals

- Build coverage for AMDGPU code that includes NBIO 7.2.0 headers catches malformed or renamed macros used by consumers.
- Generated-header consistency checks should verify each `__SHIFT` has a matching `_MASK`, masks correspond to the expected shifted width, lane 0-15 repeated patterns are uniform where intended, and BIFPLR3 field names align with matching offset-header register names.
- PCIe enumeration tests should confirm vendor/device/class/header fields, bridge window sizing, capability-list traversal, PCIe capability decoding, and MSI programming behave as expected on NBIO 7.2.0 hardware.
- Link tests should exercise negotiated speed/width reporting, retraining, 8 GT/s and 16 GT/s equalization status, per-lane equalization presets, lane error status, and parity mismatch reporting.
- Error-handling tests should inject or observe AER/DPC/RP PIO conditions where possible and confirm status, mask, severity, source ID, first-error pointer, TLP header, and prefix logs are decoded and cleared without losing unrelated state.
- Power-management tests should cover ASPM/L1 PM substate programming, LTR-dependent thresholds, suspend/resume restore, and runtime power transitions around link status and MSI delivery.
- Margining and ESM validation should confirm lane margining control/status payloads, ESM calibration completion, selected data rates, supported-rate bitmaps, retimer/link-reach fields, and per-lane 20 GT/s/25 GT/s preset programming on supported platforms.
- Static comparison against the upstream/generated register source should flag any manual edits to masks, shifts, register names, or repeated lane-rate patterns.
