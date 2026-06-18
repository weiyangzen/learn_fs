# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_7_0_sh_mask.h lines 97678-100078

## Scope

This chunk is a generated AMDGPU NBIO 7.0 shift/mask header segment. It contains 2,181 `#define` macros and 216 register/address-block comments. There are no functions, structs, enums, globals, locks, allocations, or executable statements in this range.

The range starts at the tail of `BIFPLR4_2_PCIE_ESM_CAP_6`, covers `BIFPLR4_2_PCIE_ESM_CAP_7`, then the full `nbio_pcie0_bifplr5_cfgdecp` PCI/PCIe bridge configuration-decode block, and ends partway through the next `nbio_pcie0_bifplr6_cfgdecp` block at `BIFPLR6_2_DEVICE_CNTL2`. Adjacent chunks are needed for the beginning of `BIFPLR4_2_PCIE_ESM_CAP_6` and the remainder of `BIFPLR6_2`.

Although this source mirror lives under `sources/distributed-fs/ceph-client`, the file is AMDGPU hardware metadata and has no direct Ceph or distributed-filesystem behavior.

## Purpose

`nbio_7_0_sh_mask.h` is the bitfield-layout half of AMD's generated NBIO 7.0 register interface. For every hardware register field it exports:

- `<REGISTER>__<FIELD>__SHIFT`, the bit offset used to encode or decode the field.
- `<REGISTER>__<FIELD>_MASK`, the mask used to isolate, preserve, clear, or compose that field.

This chunk describes PCI Express bridge configuration-space fields for the NBIO `BIFPLR*_2` root-port instances. The covered registers include conventional PCI bridge header fields, PCI power-management capability fields, PCIe capability/device/link/slot/root fields, MSI and subsystem-ID fields, vendor-specific and virtual-channel enhanced capabilities, device serial number, Advanced Error Reporting, secondary PCIe link/equalization controls, Access Control Services, multicast, L1 PM substates, Downstream Port Containment, Root Port PIO logging, and the PCIe ESM capability bitmaps. These constants let AMDGPU code decode or compose register words without hard-coding bit positions at call sites.

## Important Macro Families

The opening `BIFPLR4_2_PCIE_ESM_CAP_7` section completes the previous port's ESM-speed capability bitmap. It maps one-bit ESM capability flags from `ESM_25P0G` through `ESM_28P0G`; the first five lines in the chunk are the closing masks for `BIFPLR4_2_PCIE_ESM_CAP_6`.

The `BIFPLR5_2` block is complete in this chunk and covers a full PCIe bridge/root-port configuration layout:

- Base PCI bridge identification and decode fields: vendor/device ID, command/status bits, revision/class codes, header/BIST, bus numbering, IO and memory windows, prefetchable base/limit upper words, capability pointer, interrupt line/pin, bridge control, and an AMD extension for port-80 IO decode.
- Power-management capability fields: capability-list IDs and next pointers, PM version, PME clock/support, D1/D2 support, power-state selection, PME enable/status, data select/scale, B2/B3 support, bus-power enable, and PM data.
- PCIe capability fields: device type, slot implemented, interrupt message number, maximum payload/read request sizing, extended tag, relaxed/no-snoop ordering, function-level reset capability, completion timeout, ARI forwarding, atomic operations, ID-based ordering, LTR, OBFF, end-to-end TLP prefix support, and link/slot/root controls and statuses.
- MSI and identification capabilities: MSI enable/multiple-message controls, 32/64-bit message address/data fields, subsystem/vendor IDs, and MSI map capability/address registers.
- Enhanced capabilities: vendor-specific headers/data words, virtual channel port/resource controls, device serial number, Advanced Error Reporting status/mask/severity/header logs/root error reporting/source IDs/TLP prefix logs, secondary PCIe link/equalization controls for lanes 0-15, ACS capability/control, multicast capability/control/address/receive/block/overlay registers, L1 PM substate capabilities and controls, DPC capability/control/status/error source, Root Port PIO status/mask/severity/system-error/exception/header-log/implementation-specific/prefix-log fields, and ESM capability/status/control/capability bitmap registers.

The `BIFPLR6_2` block begins the next root-port instance with the same generated pattern. This chunk includes its base PCI bridge fields, PM capability, first-generation PCIe capability, link/slot/root controls and statuses, and `DEVICE_CAP2`/the beginning of `DEVICE_CNTL2`. The remaining `BIFPLR6_2` fields are outside this chunk.

## APIs, Types, And Functions

There are no callable APIs or C types in this range. The public interface is the generated preprocessor namespace. The macro values are untyped integer literals, mostly with an `L` suffix, and encode only field geometry.

These definitions do not include register addresses, reset values, access size, read/write permissions, write-one-to-clear behavior, hardware sequencing rules, firmware ownership, or side effects. Consumers must combine them with the matching generated address/default metadata and AMDGPU register helpers such as `REG_GET_FIELD`, `REG_SET_FIELD`, `RREG32_SOC15`, `WREG32_SOC15`, or the NBIO/SMN/PCIe access path appropriate for the target register.

## Control Flow

This header has no local runtime control flow. Runtime behavior is external:

1. AMDGPU or platform code selects a `BIFPLR*_2_*` register address from sibling generated NBIO metadata.
2. Code reads a hardware register and decodes fields with the `__SHIFT` and `_MASK` constants, or composes an updated value while preserving unrelated and reserved bits.
3. The decoded or programmed values participate in PCIe root-port setup, link negotiation, power management, error reporting, interrupt delivery, link equalization, containment, or diagnostic reporting.

Several fields represent asynchronous hardware/protocol state rather than ordinary software state: link training and data-link-active bits, PME status/pending/requestor IDs, hotplug/slot status bits, AER/DPC/Root Port PIO error latches and logs, VC negotiation/pending flags, L1 substate controls, lane error and equalization state, and ESM status/control bits.

## State And Persistence Behavior

The header owns no state and persists nothing. It describes hardware-visible state in NBIO PCIe bridge/root-port configuration registers. Persistence depends on the GPU reset domain, PCIe conventional reset, link reset/retrain, power management, firmware/BIOS setup, suspend/resume restore, and explicit AMDGPU writes.

Represented state includes writable control bits, capability readbacks, bus/window decode values, MSI routing values, interrupt controls, power-management settings, link width/speed negotiation status, slot/hotplug state, error masks/severities/status latches, header/TLP-prefix logs, equalization settings, ACS/multicast policies, DPC containment state, Root Port PIO diagnostics, and ESM capability bitmaps. Some fields are likely read-only capability/status values, some are write-one-to-clear status bits, and some are writable policy controls; that access behavior is not encoded by the shift/mask macros alone.

## Dependencies And Integration Points

This chunk depends on AMD's generated NBIO 7.0 register database and must stay synchronized with sibling generated headers:

- `nbio_7_0_offset.h` and `nbio_7_0_smn.h` provide address metadata for the same NBIO register set.
- `nbio_7_0_default.h` provides reset/default values for many matching registers.
- AMDGPU SOC15/NBIO register access helpers and bitfield helper macros apply these shifts and masks at runtime.

Integration points include AMDGPU NBIO initialization, PCIe root-port configuration, GPU reset and resume restore, ASPM/L1 PM substate handling, MSI programming, AER/DPC error handling, hotplug/slot status reporting, virtualization/IOMMU-facing ACS policy, multicast/VC configuration, and low-level PCIe diagnostics. The `BIFPLR5_2` and `BIFPLR6_2` naming indicates repeated mechanically generated per-port instances, so consumers must select the instance that matches the active hardware port.

## Risks And Edge Cases

- Generated shift/mask drift can compile cleanly while causing code to write the wrong PCIe configuration bit, producing link, enumeration, interrupt, power-management, or error-reporting failures.
- The chunk starts and ends in the middle of register families. Whole-file research must reconcile the preceding `BIFPLR4_2_PCIE_ESM_CAP_6` fields and following `BIFPLR6_2` fields before treating either boundary register set as complete.
- Many status fields in PCIe/AER/DPC/slot/root-port registers have protocol-specific clearing semantics. The shift/mask header does not identify write-one-to-clear or read-only fields, so call sites must rely on hardware documentation and existing helpers.
- Link and power-management controls can trigger asynchronous state transitions. Writers must handle link-training timeouts, device removal, reset races, PME races, and non-converging equalization or DPC recovery.
- PCI bridge window, bus-number, ACS, multicast, and VC fields affect traffic routing and isolation. Incorrect programming can break enumeration, DMA reachability, peer-to-peer routing, or virtualization isolation.
- MSI address/data and MSI-map fields are interrupt-routing sensitive; stale restore values or wrong masks can misroute interrupts.
- AER/DPC and Root Port PIO logs can be lost or corrupted if status bits are cleared before software captures the associated header/source/prefix fields.
- The `BIFPLR5_2` and `BIFPLR6_2` definitions repeat the same layout for different ports. Copy/paste or generator mistakes can affect one port instance only, making failures topology-dependent.

## Test Signals

- Build AMDGPU with NBIO 7.0 support enabled. Compile-time coverage catches missing or renamed generated symbols referenced by consumers.
- Run generated-header consistency checks: every `__SHIFT` should have a compatible `_MASK`, masks should not overlap unexpectedly within a register, and repeated `BIFPLR*_2` port instances should match where hardware layout is intended to be identical.
- Cross-check this chunk against `nbio_7_0_offset.h`, `nbio_7_0_smn.h`, and `nbio_7_0_default.h` so each field layout maps to a known register address and expected default where one exists.
- On supported hardware, validate PCIe enumeration, bus/window decoding, negotiated link speed/width, link retraining, ASPM/L1 substate transitions, GPU reset, and suspend/resume.
- Exercise interrupt and error paths: MSI delivery, PME signaling, AER correctable/nonfatal/fatal reporting, DPC trigger/recovery, Root Port PIO status/log capture, hotplug/slot status changes, and lane error/equalization status readback.
- For any code that writes these fields, inspect register traces to ensure reserved bits are preserved, status/log fields are cleared only after capture, and per-port writes target the expected `BIFPLR5_2` or `BIFPLR6_2` instance.
