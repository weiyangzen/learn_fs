# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_7_0_sh_mask.h lines 90485-92893

## Scope

This chunk is a generated AMDGPU NBIO 7.0 shift/mask header segment. It contains 2,176 `#define` field-layout macros for PCI/PCIe bridge and PCIe extended capability registers in the `BIFPLR1_2` logical root-port block and the beginning of the next `BIFPLR2_2` block. There are no functions, structs, enums, variables, locks, allocations, or executable statements in this range.

The range starts in the tail of `BIFPLR1_2_SECONDARY_STATUS`, beginning with `PARITY_ERROR_DETECTED__SHIFT` and the status masks. It then covers the rest of the `BIFPLR1_2` PCI bridge configuration, PCI Power Management, PCIe capability, MSI, subsystem ID, MSI mapping, vendor-specific, virtual-channel, device-serial-number, advanced error reporting, secondary PCIe, ACS, multicast, L1 PM substate, DPC, RP PIO, and ESM field definitions. After the `addressBlock: nbio_pcie0_bifplr2_cfgdecp` marker, it begins the mechanically similar `BIFPLR2_2` block from vendor/device/class registers through `BIFPLR2_2_PCIE_VC0_RESOURCE_STATUS`, ending after only the first `BIFPLR2_2_PCIE_VC1_RESOURCE_CAP__PORT_ARB_CAP__SHIFT` field. Adjacent chunks are required for the complete `BIFPLR1_2_SECONDARY_STATUS` and `BIFPLR2_2_PCIE_VC1_RESOURCE_CAP` register layouts.

Although this source tree is under a `ceph-client` mirror path, this file is AMDGPU hardware register metadata and has no direct distributed-filesystem behavior.

## Purpose

`nbio_7_0_sh_mask.h` is the bitfield geometry half of AMD's generated NBIO 7.0 register interface. For each register field it exports:

- `<REGISTER>__<FIELD>__SHIFT`, the bit offset used to extract or place a field.
- `<REGISTER>__<FIELD>_MASK`, the encoded bit mask used to isolate, preserve, clear, or update that field.

This chunk maps the configuration-space view of NBIO PCIe logical root ports. The macros let AMDGPU code decode PCI bridge windows, capabilities, link state, error latches, virtual-channel arbitration, message-signaled interrupts, ACS/multicast controls, L1 PM substates, downstream port containment, root-port PIO error logs, and ESM metadata without embedding raw bit positions at call sites.

## Important Macro Families

The `BIFPLR1_2` PCI bridge and conventional capability fields cover:

- Bridge resource routing: memory base/limit, prefetchable memory base/limit including upper 32-bit registers, high I/O base/limit, capability pointer, interrupt line/pin, bridge control, and the extended bridge `IO_PORT_80_EN` bit.
- Secondary bus status and bridge control error state: capability-list presence, 66 MHz/fast back-to-back capability, master-data parity, DEVSEL timing, target/master aborts, system error, parity detected, parity response, SERR enable, ISA/VGA forwarding, master-abort mode, secondary-bus reset, and fast back-to-back enable.
- Power management capability: PM capability list linkage, PM version/features, D1/D2 and PME support, power state, no-soft-reset, PME enable/status, data select/scale, B2/B3 support, bus-power enable, and PM data.

The `BIFPLR1_2` PCIe capability fields cover:

- PCIe capability header and device identity: capability version, device type, slot implemented, interrupt message number, max payload support/size, extended tags, phantom functions, relaxed ordering, no-snoop, max read request size, FLR capability, bridge configuration retry, and device error enables/status.
- Link and slot state: supported/current link speed and width, ASPM/link PM support, L0s/L1 exit latencies, clock power management, surprise-down reporting, data-link-layer active reporting, bandwidth notification, ASPM/RCB/common-clock/extended-sync/clock-power bits, retraining, slot-clock config, link training, data-link-layer active, slot power/controller fields, attention/power indicators, hot-plug events, MRL sensor, command-completed, presence detect, and electromechanical interlock state.
- Root-port control/status: PME interrupt enables, CRS software visibility, PME requester ID/status/pending, and root error command/status/source identifiers for advanced error reporting.
- PCIe Capability 2 registers: completion timeout ranges and disables, ARI forwarding, atomic operation routing/completion/request enables, 32/64/128-bit CAS support, no-RO PR-PR passing, LTR/OBFF support, end-to-end TLP prefix support and blocking, target link speed, compliance controls, de-emphasis, equalization status, and lane error/equalization controls.

The `BIFPLR1_2` extended capability and diagnostics section includes:

- MSI and MSI mapping: capability linkage, enable/multiple-message fields, 64-bit/per-vector support, message address/data registers, MSI map enable/fixed/type, and map base address.
- Subsystem/vendor-specific capabilities: SSID, vendor-specific enhanced capability list/header, two scratch vendor-specific registers, and device serial number DW1/DW2.
- Virtual channels: VC enhanced capability, port VC capabilities, VC arbitration table controls/status, VC0/VC1 resource capabilities, traffic-class to VC maps, VC IDs, VC enable bits, and negotiation-pending/status fields.
- Advanced Error Reporting: uncorrectable error status/mask/severity fields for data link protocol, surprise down, poisoned TLP, flow control protocol, completion timeout, completer abort, unexpected completion, receiver overflow, malformed TLP, ECRC, unsupported request, ACS violation, uncorrectable internal error, MC blocked TLP, atomic egress blocked, TLP prefix blocked, and poisoned TLP egress blocked. Correctable status/mask fields include receiver error, bad TLP/DLLP, replay rollover, replay timeout, advisory non-fatal, corrected internal, header-log overflow, and the matching AER capability/control and header/TLP-prefix logs.
- Secondary PCIe extended capability: link control 3, lane error status, and lane 0 through lane 15 equalization controls for downstream/upstream port transmitter preset fields and preset hints.
- ACS and multicast: ACS capability/control bits for source validation, translation blocking, P2P request/completion redirect, upstream forwarding, P2P egress control, direct translated P2P, egress control vector size, and multicast overlay/receiver/blocking address fields.
- L1 PM substates: capability list, ASPM/PCI-PM L1.1/L1.2 support, common-mode restore time, T-power-on scale/value, L1.2 enable bits, PME-turnoff acknowledgement, timing values, and T-power-on programming.
- DPC and RP PIO error handling: DPC capability/list/control/status/source ID fields, trigger reason/extension/status/interrupt bits, RP PIO status/mask/severity/system-error/exception bitmaps, header and prefix logs, and implementation-specific log storage.
- ESM registers: ESM capability list, headers, status, control, and capability blocks `PCIE_ESM_CAP_1` through `PCIE_ESM_CAP_7`, including capability count, next pointers, supported event masks, interrupt/message controls, and capability-specific bitmaps.

The `BIFPLR2_2` section restarts the same register model for another NBIO PCIe root-port address block. In this chunk it covers conventional PCI identity/class/cache/latency/header/BIST/bus-number/resource/status registers, PM and PCIe capabilities, MSI, SSID, MSI mapping, vendor-specific registers, and virtual-channel definitions through VC0 status. It stops before the complete VC1 resource-capability masks appear.

## APIs, Types, And Functions

There are no callable APIs or C types in this chunk. The public interface is the generated macro namespace. The constants are untyped preprocessor integer literals, mostly with an `L` suffix, and encode only field geometry.

These macros do not define register addresses, reset values, access permissions, write-one-to-clear behavior, polling timeouts, ownership rules, or side effects. Consumers must combine them with sibling NBIO metadata such as `nbio_7_0_default.h` for defaults and generated address headers for the actual register offsets, then use AMDGPU register helpers such as `REG_GET_FIELD`, `REG_SET_FIELD`, `RREG32_SOC15`, `WREG32_SOC15`, or the PCIe/NBIO access path appropriate for the register.

## Control Flow

This header has no local runtime control flow. Runtime flow is external:

1. AMDGPU code selects a `BIFPLR1_2_*` or `BIFPLR2_2_*` register address from generated NBIO address metadata.
2. It reads a hardware register, extracts fields with the `__SHIFT` and `_MASK` constants, or composes a write while preserving unrelated and reserved bits.
3. The decoded or written values participate in PCIe bridge setup, link capability reporting, error detection, interrupt delivery, power management, virtualization/isolation controls, and diagnostic logging.

The field names imply several asynchronous hardware flows that software must handle outside this header: link training/retraining, equalization, hot-plug and slot events, PME generation, MSI delivery, AER/DPC error capture, RP PIO exception logging, L1 substate entry/exit, virtual-channel negotiation, and ESM event reporting.

## State And Persistence Behavior

The header owns no state and persists nothing. It describes state held in NBIO PCIe configuration and extended-capability registers. Persistence depends on the GPU reset domain, PCIe hot/warm reset, FLR, DPC containment/recovery, runtime power management, suspend/resume restore, firmware/BIOS programming, and explicit AMDGPU writes.

Represented state includes writable control bits, bridge window registers, capability list pointers, negotiated link state, error enables/masks/severity maps, sticky status latches, MSI address/data state, virtual-channel mappings, ACS and multicast policy, L1 PM substate timing values, DPC trigger/status/source identifiers, RP PIO logs, and ESM capability/status/control words. Some fields are read-only capability or live-status bits, some are writable controls, and some status/error fields may be sticky or write-one-to-clear; that behavior is not derivable from the shift/mask definitions alone.

## Dependencies And Integration Points

This chunk must remain synchronized with the rest of the generated NBIO 7.0 register set:

- `nbio_7_0_default.h` contains matching `smnBIFPLR1_2_*_DEFAULT` and `smnBIFPLR2_2_*_DEFAULT` values for many of these registers.
- Generated NBIO offset/SMN headers provide the actual register addresses used by AMDGPU register access helpers.
- AMDGPU PCIe/NBIO, error handling, virtualization/isolation, reset, power-management, and diagnostic code consumes these definitions indirectly through generated ASIC register include stacks.

The `BIFPLR*` names indicate bridge-interface logical root-port configuration windows. Integration points include kernel PCI enumeration and bridge resource assignment, AMDGPU device initialization, PCIe capability reporting, hot-plug/root-port event handling, AER and DPC recovery paths, MSI setup, ACS/IOMMU isolation policy, virtual-channel QoS setup, and low-power link-state management.

## Risks And Edge Cases

- Generated shift/mask drift can compile cleanly while causing software to decode or update the wrong PCIe configuration bit. Failures can surface as incorrect resource windows, broken MSI delivery, misreported PCIe capabilities, unstable link training, missed errors, or unsafe ACS/multicast policy.
- The chunk starts and ends mid-register-family. Whole-file research must reconcile the previous `BIFPLR1_2_SECONDARY_STATUS` shift fields and the following `BIFPLR2_2_PCIE_VC1_RESOURCE_CAP` masks before treating those registers as complete.
- Many status and error registers are likely sticky or write-one-to-clear in hardware. A helper that writes a full register value using only these masks can accidentally clear diagnostic evidence or acknowledge events.
- Error mask/severity/sys-error fields are security and reliability sensitive: a wrong bit can suppress fatal reporting, over-report benign conditions, or route errors to the wrong recovery path.
- ACS, multicast, ARI, atomic operation, and virtual-channel controls affect isolation and ordering semantics. Incorrect programming can break peer-to-peer routing, IOMMU assumptions, traffic-class mapping, or device interoperability.
- Link control, equalization, ASPM, L1 substate, DPC, and hot-plug fields interact with asynchronous PCIe state machines. Call sites need timeouts and recovery paths for link training, equalization failure, DPC trigger races, and suspend/resume transitions.
- Reserved fields appear throughout the generated layouts. Writers must preserve reserved bits unless hardware documentation explicitly permits a value.
- `BIFPLR1_2` and `BIFPLR2_2` are mechanically similar. Copy/generation errors may affect one root-port instance only, making failures topology-dependent.

## Test Signals

- Build AMDGPU with NBIO 7.0 support enabled. Compile-time coverage catches missing or renamed generated symbols used by consumers.
- Run generated-header consistency checks: every non-reserved field should have a compatible `__SHIFT`/`_MASK` pair, masks should align with shifts, and repeated `BIFPLR1_2`/`BIFPLR2_2` layouts should match where the hardware block is intended to be identical.
- Cross-check these register names against sibling default and address headers so every field layout maps to a known register and reset/default value.
- On supported hardware, validate PCIe enumeration, bridge resource assignment, MSI programming, link speed/width negotiation, ASPM/L1 substate behavior, suspend/resume, FLR, GPU reset, and DPC recovery.
- Exercise error paths where possible: AER correctable/uncorrectable logging, root error command/status, RP PIO status/header/prefix logs, DPC trigger/source reporting, and ESM event/status reporting.
- For any code writing these registers, review register traces to confirm reserved bits are preserved, write-one-to-clear status fields are acknowledged deliberately, and temporary diagnostics restore MSI, ACS, VC, ASPM, DPC, and error-mask state afterward.
