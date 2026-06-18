# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_7_7_0_sh_mask.h lines 63527-65943

## Scope

This chunk is a generated AMDGPU NBIO 7.7.0 shift/mask header segment. It contains 2,163 `#define` field-layout macros and 216 register-family comments. There are no functions, structs, enums, variables, allocations, locks, or executable statements in this range.

The range starts at the tail of `BIFPLR0_0_DEVICE_CNTL`, covers most of the PCIe capability and extended-capability field layouts for `BIFPLR0_0`, and ends after the first base PCI configuration fields for the next `addressBlock`, `nbio_pcie0_bifplr1_cfgdecp`, through the `BIFPLR1_0_HEADER` comment and its initial field macros. Adjacent chunks are required to capture the missing beginning of `BIFPLR0_0_DEVICE_CNTL` and the remainder of `BIFPLR1_0_HEADER` and following `BIFPLR1_0` registers.

Although the repository path is under a `ceph-client` source mirror, this file is AMDGPU hardware metadata and has no direct distributed-filesystem behavior.

## Purpose

`nbio_7_7_0_sh_mask.h` is the bitfield half of AMD's generated NBIO 7.7.0 register interface. Each field is represented by:

- `<REGISTER>__<FIELD>__SHIFT`, the least-significant bit position used to extract or encode the field.
- `<REGISTER>__<FIELD>_MASK`, the already-shifted mask used to isolate or preserve the field.

This chunk describes PCIe root-port or link-root configuration space for NBIO BIF PCIe block `BIFPLR0_0`, including PCIe device/link/slot/root capabilities, MSI and subsystem-ID capabilities, virtual-channel and serial-number capabilities, Advanced Error Reporting, Secondary PCIe capability, per-lane equalization, Access Control Services, multicast, L1 PM substates, Downstream Port Containment, Root Port PIO logging, an Elasticity/ESM capability block, Data Link Feature, 16 GT/s and 32 GT/s capability fields, lane margining, CCIX-related fields, and 20/25 GT/s ESM equalization controls. The final lines begin the repeated base PCI configuration layout for `BIFPLR1_0`.

## Important Macro Families

The standard PCIe capability portion covers:

- Device, link, slot, and root status/control/capability fields: error status bits, maximum read request, link speed/width, ASPM and power-management enables, retrain/link-disable controls, data-link-active status, hotplug/slot power fields, PME/root error controls, and PCIe Capability 2 fields such as completion timeout, atomic operations, OBFF, LTR, TPH, ten-bit tags, and emergency power reduction support.
- Link Capability/Control/Status 2 fields: target link speed, equalization completion and phase status, selectable de-emphasis, transmit margin, compliance preset, link speed vector, retimer presence, crosslink support, and downstream component presence.
- MSI, subsystem ID, and MSI mapping capabilities: capability IDs/next pointers, message control, address/data payload fields, multiple-message enable/capability bits, 64-bit and per-vector mask support, and fixed/mappable MSI mapping status.
- Vendor-specific, virtual-channel, and device serial-number extended capabilities: capability headers, VC arbitration/low-priority extended count fields, VC0/VC1 resource capability/control/status, traffic-class mapping, load-table controls, arbitration select bits, and serial-number payload dwords.

The reliability and error-reporting section covers:

- Advanced Error Reporting (`PCIE_ADV_ERR_RPT_ENH_CAP_LIST`, `PCIE_UNCORR_ERR_STATUS`, `PCIE_UNCORR_ERR_MASK`, `PCIE_UNCORR_ERR_SEVERITY`, `PCIE_CORR_ERR_STATUS`, `PCIE_CORR_ERR_MASK`, `PCIE_ADV_ERR_CAP_CNTL`, header logs, root error command/status, source IDs, and TLP prefix logs). These fields cover data-link protocol errors, poisoned TLPs, flow-control protocol errors, completion timeout/abort, ECRC, unsupported requests, ACS violations, uncorrectable internal errors, malformed TLPs, atomic-op egress blocked, TLP prefix blocked, advisory nonfatal errors, replay rollover, replay timer timeout, receiver errors, correctable internal errors, and logging controls.
- Secondary PCIe and Link Control 3 fields: equalization perform-link-equalization request, lane error status, and 16 lanes of per-lane transmit presets with downstream/upstream receive preset hints.
- Downstream Port Containment and Root Port PIO: DPC capability/control/status, trigger reason/extension fields, interrupt enables/status, containment active/completed bits, RP PIO status/mask/severity/system-error/exception selectors, and header/prefix logs for PIO errors.

The link-training and high-speed capability section covers:

- 16 GT/s capability, control, status, local/retimer parity mismatch status, and lane 0-15 equalization controls.
- PCIe lane margining: port capability/status and per-lane control/status fields for receiver number, margin type, usage model, margin payload, timing/voltage step counts, sample reporting method, max offset, independent timing/voltage support, and ready/error/valid status.
- ESM and CCIX-oriented fields: ESM status/control, seven large ESM capability registers with supported rates, retimer/equalization modes, preset vectors, TS/FEC/precision-time and lane support indicators, CCIX capability/control/status fields, required/optional ESM capability bits, and per-lane 20 GT/s and 25 GT/s downstream/upstream transmit preset fields.
- 32 GT/s fields: equalization bypass/no-equalization-needed support and disable bits, modified training-sequence mode support/selection, enhanced link behavior status, transmitter precoding status/request, and 32 GT/s equalization phase status.

The final `BIFPLR1_0` start repeats base PCI configuration-space fields for another BIF port/root instance: vendor ID, device ID, command enables, status/error bits, revision/class code bytes, cache-line size, latency timer, and the beginning of header type/device type.

## APIs, Types, And Functions

There are no callable APIs or C types in this chunk. The public interface is the generated macro namespace. The constants are untyped preprocessor integer literals, mostly with an `L` suffix, and describe only bit geometry.

These macros do not provide register addresses, reset/default values, access permissions, write-one-to-clear behavior, sequencing, ownership, or side-effect rules. Consumers must combine them with the matching generated address/default headers and AMDGPU register helpers such as `REG_GET_FIELD`, `REG_SET_FIELD`, `RREG32_SOC15`, `WREG32_SOC15`, or the PCIe/NBIO access path used by the surrounding driver code.

## Control Flow

This header has no local runtime control flow. Runtime flow is supplied by AMDGPU code that includes the generated NBIO headers:

1. Driver code selects a `BIFPLR0_0_*` or `BIFPLR1_0_*` register address from sibling generated metadata.
2. It reads the register and extracts fields with these `__SHIFT` and `_MASK` macros, or composes a write value while preserving unrelated and reserved bits.
3. Decoded values influence PCIe link bring-up, capability advertisement, error reporting, interrupt setup, power-management policy, DPC/AER recovery, link retraining/equalization, lane margining diagnostics, or debug logging.

The field names imply several asynchronous hardware/PCIe flows outside the header: link training and retraining, link bandwidth notifications, hotplug events, PME signaling, AER status latching, DPC containment and recovery, RP PIO error capture, retimer parity status, equalization phase completion, lane margining command execution, CCIX/ESM negotiation, and high-speed 16/20/25/32 GT/s preset handling.

## State And Persistence Behavior

The header owns no state and persists nothing. It documents hardware-visible state in NBIO PCIe configuration and extended-capability registers. Persistence is controlled by the GPU reset domain, PCIe fundamental or hot reset, link retraining, firmware or BIOS initialization, power-management transitions, suspend/resume restore, and explicit AMDGPU writes.

Represented state includes writable control bits, advertised capabilities, interrupt enables, error masks and severities, status latches, error header/prefix logs, virtual-channel resource settings, ACS policy bits, multicast and overlay BAR settings, L1 PM substate timings, DPC/RP PIO containment state, per-lane equalization presets, lane-margining command/status fields, ESM/CCIX capability and control state, and base PCI command/status/class/header fields. Many status fields are live or latched hardware state and may require clear-on-write or ordered recovery behavior not visible from this shift/mask file alone.

## Dependencies And Integration Points

This chunk depends on AMD's generated NBIO 7.7.0 register database and must stay synchronized with sibling generated headers:

- `nbio_7_7_0_offset.h` and/or `nbio_7_7_0_smn.h` provide register address metadata for the same `BIFPLR*` registers.
- `nbio_7_7_0_default.h` provides reset/default values where generated for these registers.
- AMDGPU SOC15/NBIO/PCIe helper code provides the actual read/modify/write paths and bitfield helper macros that consume these shifts and masks.

Integration points are PCIe root-port initialization, link-speed and link-width management, ASPM/L1 substate power management, MSI setup, AER/DPC error handling, virtualization/IOMMU-facing ACS policy, VC/traffic-class configuration, high-speed link equalization, lane margining diagnostics, CCIX/ESM negotiation, suspend/resume restore, GPU reset recovery, and hardware debug tooling. The `BIFPLR1_0` lines indicate that the same generated pattern repeats for additional PCIe BIF blocks.

## Risks And Edge Cases

- Generated shift/mask drift can compile cleanly while causing the driver to read or write the wrong PCIe capability bit, which can surface as link-training failures, incorrect capability advertisement, broken MSI setup, missed errors, or unsafe recovery behavior.
- The range starts and ends mid-register-family. Whole-file research must reconcile the preceding `BIFPLR0_0_DEVICE_CNTL` fields and following `BIFPLR1_0_HEADER` fields before treating those registers as complete.
- Error status, AER, DPC, RP PIO, and hotplug/slot status fields are commonly latched and may have write-one-to-clear semantics. This header only names masks; call sites must know the hardware clearing rules.
- Link control, equalization, margining, retimer, CCIX, ESM, and 32 GT/s fields are timing-sensitive. Setting controls without polling completion/error bits and timeouts can leave the link unstable or down.
- ACS, multicast, virtual-channel, and traffic-class fields affect ordering, routing, isolation, and peer-to-peer behavior. Incorrect writes can break DMA isolation or performance in ways not detected by compile-time checks.
- Per-lane definitions are mechanically repeated for lanes 0-15. Copy/generation mistakes may affect only one lane or a subset of rates, producing lane-width downgrade or marginal signal-integrity symptoms.
- Reserved fields appear throughout the wider generated register set even when not in this specific range. Writers should preserve unknown bits unless hardware documentation explicitly permits overwrites.

## Test Signals

- Build AMDGPU with NBIO 7.7.0 support enabled. Compile-time coverage catches missing or renamed generated symbols used by consumers.
- Run generated-header consistency checks: each `__SHIFT` should have a compatible `_MASK`, masks should fit the documented register width, repeated lane families should be identical except for lane number, and `BIFPLR0_0`/`BIFPLR1_0` repeated base fields should match where the hardware block is cloned.
- Cross-check every register name in this chunk against sibling address/default headers so each field layout maps to a known register and expected reset value.
- On supported hardware, validate PCIe enumeration, MSI delivery, negotiated link speed/width, retraining, ASPM/L1 substate behavior, suspend/resume, GPU reset recovery, and hotplug or surprise-down paths where applicable.
- Exercise AER/DPC/RP PIO handling with injected or observed correctable/uncorrectable errors, confirming status capture, severity/mask behavior, source IDs, header/prefix logs, interrupts, containment, and recovery sequencing.
- Validate high-speed link diagnostics by checking 16/20/25/32 GT/s equalization status, lane error status, lane-margining command/status fields, retimer parity status, and per-lane preset programming against firmware or board expectations.
- For any code that writes these fields, inspect register traces to confirm read/modify/write preservation of unrelated bits and correct clear/restore behavior for temporary debug, margining, or containment controls.
