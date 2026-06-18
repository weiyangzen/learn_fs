# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_7_0_sh_mask.h lines 24434-26840

## Scope

This chunk is a generated AMDGPU NBIO 7.0 shift/mask header segment. It contains 2,176 `#define` field-layout macros and 229 register-family comments. It has no executable C statements, functions, structs, enums, variables, allocations, locks, or local storage.

The range starts with the final `BIFPLR5_0_IRQ_BRIDGE_CNTL__FAST_B2B_EN_MASK` macro from the previous register family, then covers the rest of the `BIFPLR5_0` PCIe bridge/root-port configuration-space field map from `EXT_BRIDGE_CNTL` through the PCIe Emergency Power Reduction/ESM capability registers. It then starts the `addressBlock: nbio_pcie0_bifplr6_cfgdecp` section and covers `BIFPLR6_0` PCI/PCIe bridge configuration fields from vendor/device ID through the shift definitions for `BIFPLR6_0_PCIE_UNCORR_ERR_STATUS`. The matching masks for that last `BIFPLR6_0_PCIE_UNCORR_ERR_STATUS` register begin after this chunk and belong to the next chunk.

Although the repository path is under a `ceph-client` source mirror, this file is AMDGPU hardware metadata and has no direct distributed-filesystem behavior.

## Purpose

`nbio_7_0_sh_mask.h` provides bit-level register-field constants for NBIO 7.0 hardware. For each field it exports the generated pair:

- `<REGISTER>__<FIELD>__SHIFT`, the bit offset used to place or extract the field.
- `<REGISTER>__<FIELD>_MASK`, the encoded bit mask used to isolate, preserve, clear, or update that field.

This chunk describes PCI/PCIe bridge configuration-space fields for two NBIO PCIe logical root-port/bridge instances, primarily complete `BIFPLR5_0` coverage and partial `BIFPLR6_0` coverage. Driver code combines these constants with matching generated address/default headers and AMDGPU register helpers such as `REG_SET_FIELD`, `REG_GET_FIELD`, `RREG32_SOC15`, `WREG32_SOC15`, `WREG32_FIELD15`, and PCIe/SMN accessors. The constants let code name PCIe capability bits, error bits, link-control bits, and status bits instead of embedding raw bit positions.

## Important Macro Families

The `BIFPLR5_0` conventional PCI bridge and PCI Express capability portion includes:

- Power-management capability fields: capability-list IDs/next pointers, PME clock/init/current/support bits, power state, PME enable/status, B2/B3 support, bus power enable, and PMI data fields.
- PCIe capability, device, link, slot, and root fields: device type, slot implemented, interrupt message number, max payload/read request, relaxed ordering, extended tag, no-snoop, link speed/width, ASPM and clock power management controls, retrain/link-disable bits, slot power/hotplug controls, root error enables, and root PME status.
- PCIe capability version 2 fields: completion timeout support/value/disable, atomic operation routing/completer bits, LTR/OBFF/TPH related controls, IDO, emergency power reduction flags, 10-bit tag requester/completer support, link target speed, enter-compliance bits, equalization status, link bandwidth status, and lane margining style status bits.
- MSI and subsystem identity fields: MSI capability list, MSI enable/multiple-message/64-bit/per-vector masking controls, message address/data words, subsystem vendor/device IDs, MSI map capability and map address fields.
- Vendor-specific, virtual-channel, and device-serial-number enhanced capabilities: VSEC header/list fields, scratch registers, VC capability/control/status, VC0/VC1 resource capability/control/status, and serial number dwords.

The `BIFPLR5_0` PCIe error-reporting and recovery portions include:

- Advanced Error Reporting fields: uncorrectable error status/mask/severity bits for DLP, surprise down, poisoned TLP, flow control, completion timeout/abort, unexpected completion, receiver overflow, malformed TLP, ECRC, unsupported request, ACS violation, internal error, multicast blocked TLP, AtomicOp egress blocked, TLP-prefix blocked, and poisoned-TLP egress blocked conditions.
- Correctable error status/mask bits for receiver error, bad TLP, bad DLLP, replay rollover, replay timeout, advisory non-fatal, corrected internal, header-log overflow, and virtual-channel non-fatal reporting.
- AER capability/control and root error command/status/source-ID fields, including first-error pointer, ECRC generation/check enable/capable bits, multiple header recording, TLP-prefix log presence, correctable/non-fatal/fatal error message enables, and received error message status bits.
- Header log and TLP prefix log registers, represented as full 32-bit log payload fields.
- Secondary PCIe capability, link control 3, lane error status, and per-lane 0 through 15 equalization controls for downstream/upstream transmit preset, coefficient, and preset-hint fields.

The access-control, multicast, low-power, and containment sections include:

- ACS capability/control bits for source validation, translation blocking, P2P request/completion redirect, upstream forwarding, egress control, direct translated P2P, and egress vector size.
- Multicast capability/control/address/receive/block/overlay BAR fields, including multicast group counts, enable bits, egress blocking, overlay size, BAR index, and window base addresses.
- L1 PM substate capability/control fields for PCI-PM and ASPM L1.1/L1.2 support, common-mode restore times, T_POWER_ON scale/value, enable bits, LTR L1.2 threshold scale/value, and a separate T_POWER_ON value register.
- Downstream Port Containment capability/control/status/source-ID fields for trigger enables, completion control, interrupt enable/status, software trigger, poisoned-TLP egress blocking, RP busy, trigger reason, trigger reason extension, and first-error pointer.
- RP PIO status, mask, severity, system-error, exception, header log, implementation-specific log, and prefix-log registers for root-port PIO error reporting.
- ESM/Emergency Power Reduction fields: ESM capability list/header/status/control plus `PCIE_ESM_CAP_1` through `PCIE_ESM_CAP_7`, which enumerate supported ESM data rates from 8.0 GT/s-style entries through 28.0 GT/s-style entries at 0.1 increments.

The `BIFPLR6_0` portion repeats the same PCI/PCIe bridge configuration layout for another NBIO PCIe bridge instance, but only through the beginning of AER uncorrectable error status in this chunk. It includes vendor/device ID, command/status, class/revision/header/BIST, subordinate bus and bridge windows, interrupt and bridge-control fields, PM capability, PCIe capability, device/link/slot/root fields, version 2 capability fields, MSI/subsystem/MSI-map fields, VSEC/VC/serial-number fields, and the shift macros for AER uncorrectable error statuses.

## APIs, Types, And Functions

There are no callable APIs or C types in this chunk. The public interface is the generated preprocessor namespace for `BIFPLR5_0_*` and `BIFPLR6_0_*` register fields. The constants are untyped integer literals, mostly with an `L` suffix on masks, and encode only field geometry.

These macros do not define register addresses, access widths, reset values, write-one-to-clear behavior, side effects, polling rules, ownership, or sequencing. The companion `nbio_7_0_offset.h`, `nbio_7_0_smn.h`, and `nbio_7_0_default.h` headers provide the related address and default-value metadata. Observed include users in this source tree include `amdgpu/nbio_v7_0.c`, `amdgpu/soc15.c`, and `pm/powerplay/hwmgr/smu10_inc.h`.

## Control Flow

This header has no local runtime control flow. Runtime flow is external:

1. AMDGPU code selects the matching NBIO register address or PCIe configuration-space register from generated offset/SMN metadata.
2. The code reads the register through the SOC15, NBIO, PCIe, or SMN access path appropriate for the register.
3. It uses these `__SHIFT` and `_MASK` constants, often through `REG_GET_FIELD` or `REG_SET_FIELD`, to decode status or compose a modified value while preserving unrelated bits.
4. The resulting values guide PCIe bridge setup, link management, MSI programming, error reporting, DPC recovery, low-power substate configuration, virtual-channel setup, or hardware diagnostics.

The macro names imply several hardware-managed flows outside the header: PCIe link training and retraining, payload/read-request negotiation, hotplug/slot status propagation, MSI delivery, AER status latching and clearing, DPC triggering and recovery, RP PIO logging, L1 substate entry/exit, VC negotiation, multicast/ACS filtering, lane equalization, and ESM power-reduction capability selection.

## State And Persistence Behavior

The header owns no software state and persists nothing. It describes hardware-visible state in NBIO PCI/PCIe bridge configuration registers. Persistence depends on PCI reset, GPU reset domain, link reset, firmware/BIOS initialization, suspend/resume restore, power management, and explicit AMDGPU writes.

Represented state includes PCI command/status enables, bridge memory/I/O windows, power-management state and PME status, PCIe device/link/slot/root control and status, MSI address/data programming, subsystem identity, virtual-channel mappings, AER masks/severity/status/header logs, DPC state, PIO logs, L1 PM substate controls, ACS/multicast controls, lane equalization controls, and ESM capability/control state. Some fields are static capabilities, some are writable controls, some are live status bits, and some are sticky error/reporting latches. The macro definitions alone do not identify which category a field belongs to.

## Dependencies And Integration Points

This chunk depends on AMD's generated NBIO 7.0 register database staying synchronized across sibling headers:

- `nbio_7_0_offset.h` supplies register offsets such as `mm...` names for SOC15-style accesses.
- `nbio_7_0_smn.h` supplies SMN address definitions for NBIO/PCIe paths.
- `nbio_7_0_default.h` supplies reset/default values for matching `cfgBIFPLR5_0_*` and `cfgBIFPLR6_0_*` registers.
- AMDGPU register helper macros consume the `__SHIFT` and `_MASK` definitions to avoid hard-coded bit positions.

The broader integration points are AMDGPU NBIO and SOC15 initialization, power-management code that includes NBIO 7.0 metadata, PCIe link and bridge configuration, interrupt/MSI setup, AER/DPC/RAS style error handling, virtualization or topology paths that care about ACS/multicast/VC state, and hardware debug tooling that decodes PCIe logs or ESM capabilities. Cross-generation NBIO headers contain very similar names, but consumers must include the exact NBIO 7.0 address/mask/default set because field positions and register availability can differ by ASIC generation.

## Risks And Edge Cases

- Generated shift/mask drift can compile cleanly while causing software to read or write the wrong PCIe bridge bit. Symptoms may look like link-training failures, wrong payload sizing, MSI delivery failures, broken DPC/AER handling, or incorrect low-power behavior.
- This chunk has boundary incompleteness: it starts with one leftover `BIFPLR5_0_IRQ_BRIDGE_CNTL` mask whose shift is in the previous chunk, and it ends after the `BIFPLR6_0_PCIE_UNCORR_ERR_STATUS` shift macros but before their mask macros. Whole-file reconciliation must join adjacent chunks before treating those register families as complete.
- PCIe status, AER, DPC, and RP PIO fields may include sticky, write-one-to-clear, or hardware-updated bits. Blind read-modify-write using only masks can lose errors or clear state unexpectedly if the access semantics are not respected.
- Error mask and severity fields affect whether hardware reports, suppresses, or escalates PCIe failures. Incorrect defaults can hide link problems or create noisy fatal/non-fatal reporting.
- Link-control, link-control-2, equalization, and ESM fields are signal-integrity and link-stability sensitive. Bad writes may cause retraining loops, degraded link speed/width, or resume failures.
- Bridge window and bus-number fields describe PCI hierarchy routing. Misprogramming them can break config, memory, or I/O transactions below the bridge.
- ACS, multicast, VC, and MSI-map fields affect routing, isolation, and interrupt address behavior. Changes can have security or virtualization impact beyond a single driver call site.
- Capabilities and controls are mechanically repeated between `BIFPLR5_0` and `BIFPLR6_0`. Copying code across instances must still use the matching register address block and preserve instance-specific defaults.

## Test Signals

- Build AMDGPU/SOC15/NBIO 7.0 code paths with this header included; compile-time failures catch missing or renamed generated symbols used by consumers.
- Run generated-header consistency checks: every field should have a compatible `__SHIFT` and `_MASK`, masks within a register should not overlap unexpectedly, and repeated `BIFPLR5_0`/`BIFPLR6_0` layouts should match where the hardware database says they are identical.
- Cross-check this chunk against `nbio_7_0_offset.h`, `nbio_7_0_smn.h`, and `nbio_7_0_default.h` so each named register maps to an address and expected default value.
- On supported NBIO 7.0 hardware, validate PCIe enumeration, bridge window setup, MSI operation, link speed/width negotiation, link retraining, suspend/resume, GPU reset recovery, and low-power L1 substate behavior.
- Exercise PCIe error paths where hardware or platform validation allows it: AER correctable/uncorrectable reporting, DPC trigger/recovery, root error status/source-ID decoding, header/TLP-prefix logs, and RP PIO logs.
- For code that writes any field from this chunk, inspect register traces to ensure reserved and unrelated bits are preserved and sticky status bits are handled with the documented clear semantics.
